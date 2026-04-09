"""Data access layer — reads backtest artifacts and shapes them for the API."""

import json
import pandas as pd
import numpy as np
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent.parent  # api/services/ → Backend/
DATA_PROC = BASE / "data" / "processed"
REPORT_MET = BASE / "reports" / "metrics"

ASSETS = ["spy", "qqq", "iwm", "btc"]
LIVE_SIGNALS_PATH = DATA_PROC / "live_signals.json"
LIVE_HISTORY_PATH = DATA_PROC / "live_signal_history.json"

_backtest_cache: dict[str, pd.DataFrame] = {}
_metrics_cache: dict[str, dict] = {}


def _load_backtest(asset: str) -> pd.DataFrame:
    if asset not in _backtest_cache:
        path = DATA_PROC / f"v21_backtest_{asset}.parquet"
        df = pd.read_parquet(path)
        df.index = pd.to_datetime(df.index)
        _backtest_cache[asset] = df
    return _backtest_cache[asset]


def _load_metrics(asset: str) -> dict:
    if asset not in _metrics_cache:
        path = REPORT_MET / f"v21_{asset}_metrics.json"
        with open(path) as f:
            _metrics_cache[asset] = json.load(f)
    return _metrics_cache[asset]


def get_backtest_df(asset: str) -> pd.DataFrame:
    return _load_backtest(asset.lower())


def get_metrics(asset: str) -> dict:
    return _load_metrics(asset.lower())


def get_all_metrics() -> dict:
    return {a.upper(): get_metrics(a) for a in ASSETS}


def get_latest_signals() -> dict:
    signals = {}
    for asset in ASSETS:
        df = _load_backtest(asset)
        last = df.iloc[-1]
        signals[asset.upper()] = {
            "date": df.index[-1].isoformat(),
            "signal": "LONG" if last["signal_prob"] > 0 else "FLAT",
            "signal_prob": round(float(last["signal_prob"]), 4),
            "exposure": round(float(last["recommended_exposure"]) * 100, 1),
            "risk_score": int(last["risk_score"]),
            "regime": "CRISIS" if int(last["regime_label"]) == 0 else "NORMAL",
            "risk_flags": last["risk_flags"] if isinstance(last["risk_flags"], str) else "",
            "asset_ret": round(float(last["asset_ret"]) * 100, 3),
        }
    return signals


def get_equity_curve(asset: str) -> list[dict]:
    df = _load_backtest(asset.lower())
    records = []
    for date, row in df.iterrows():
        records.append({
            "date": date.isoformat(),
            "strategy": round(float(row["cum_sized"]) * 100, 2),
            "buyhold": round(float(row["cum_bh"]) * 100, 2),
        })
    return records


def get_drawdown_series(asset: str) -> list[dict]:
    df = _load_backtest(asset.lower())
    dd_sized = (df["cum_sized"] - df["cum_sized"].cummax()) * 100
    dd_bh = (df["cum_bh"] - df["cum_bh"].cummax()) * 100
    records = []
    for date in df.index:
        records.append({
            "date": date.isoformat(),
            "strategy": round(float(dd_sized[date]), 2),
            "buyhold": round(float(dd_bh[date]), 2),
        })
    return records


def get_regime_series(asset: str) -> list[dict]:
    df = _load_backtest(asset.lower())
    records = []
    for date, row in df.iterrows():
        records.append({
            "date": date.isoformat(),
            "regime": int(row["regime_label"]),
            "exposure": round(float(row["recommended_exposure"]) * 100, 1),
        })
    return records


def get_signal_history(asset: str, days: int = 30) -> list[dict]:
    df = _load_backtest(asset.lower()).tail(days)
    records = []
    for date, row in df.iterrows():
        records.append({
            "date": date.isoformat(),
            "signal": "LONG" if row["signal_prob"] > 0 else "FLAT",
            "exposure": round(float(row["recommended_exposure"]) * 100, 1),
            "risk_score": int(row["risk_score"]),
            "regime": "CRISIS" if int(row["regime_label"]) == 0 else "NORMAL",
            "daily_return": round(float(row["sized_ret"]) * 100, 3),
        })
    return records


def get_portfolio_summary() -> dict:
    dfs = {}
    for asset in ASSETS:
        df = _load_backtest(asset)
        dfs[asset] = df["sized_ret"]

    combined = pd.DataFrame(dfs)
    # only dates where all assets have data
    common_idx = combined.dropna().index
    combined = combined.loc[common_idx]
    port_ret = combined.mean(axis=1)

    cum_ret = port_ret.cumsum()
    dd = cum_ret - cum_ret.cummax()

    sharpe = float(port_ret.mean() / port_ret.std() * np.sqrt(252)) if port_ret.std() > 0 else 0
    total_return = float(cum_ret.iloc[-1]) * 100
    max_dd = float(dd.min()) * 100
    vol = float(port_ret.std() * np.sqrt(252)) * 100

    allocation = {}
    for asset in ASSETS:
        df = _load_backtest(asset)
        allocation[asset.upper()] = round(float(df.iloc[-1]["recommended_exposure"]) * 100, 1)

    equity = []
    for date in common_idx:
        equity.append({
            "date": date.isoformat(),
            "portfolio": round(float(cum_ret[date]) * 100, 2),
        })

    return {
        "sharpe": round(sharpe, 3),
        "total_return": round(total_return, 2),
        "max_drawdown": round(max_dd, 2),
        "annualized_vol": round(vol, 2),
        "allocation": allocation,
        "equity_curve": equity,
        "n_days": len(common_idx),
        "start_date": common_idx[0].isoformat(),
        "end_date": common_idx[-1].isoformat(),
    }


def get_live_signals() -> dict | None:
    if not LIVE_SIGNALS_PATH.exists():
        return None
    with open(LIVE_SIGNALS_PATH) as f:
        return json.load(f)


def get_live_history() -> list | None:
    if not LIVE_HISTORY_PATH.exists():
        return None
    with open(LIVE_HISTORY_PATH) as f:
        return json.load(f)
