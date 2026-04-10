"""daily signal generator — refreshes data, runs signals, writes to disk."""

import json
import time
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler

from aegis.backtests.core import (
    BASE, DATA_RAW, DATA_PROC, DATA_FEAT,
    AssetConfig, base_rule, fit_regime, orient_regime_labels,
    risk_engine_v2, build_cross_asset_features, kelly_fraction,
)
from aegis.pipelines.feature_engineering import engineer_features_for_instrument
from aegis.logging_config import get_logger

log = get_logger("aegis.daily_signals")

LIVE_SIGNALS_PATH = DATA_PROC / "live_signals.json"
LIVE_HISTORY_PATH = DATA_PROC / "live_signal_history.json"

# target allocation per asset, must sum to 1.0
PORTFOLIO_WEIGHTS = {
    "SPY": 0.30,
    "QQQ": 0.25,
    "IWM": 0.25,
    "BTC": 0.20,
}

# each asset gets its own regime model type and risk params
# crisis cap is half the normal weight (except btc which is more aggressive at 0.3x)
# ema halflife of 0 means no smoothing on exposure changes
ASSET_CONFIGS = {
    "SPY": AssetConfig(
        name="SPY", close_col="spy", regime_type="gmm", regime_k=2,
        use_base_rule=True, risk_target_vol=0.15,
        risk_max_exposure=PORTFOLIO_WEIGHTS["SPY"],
        risk_regime_crisis_cap=PORTFOLIO_WEIGHTS["SPY"] * 0.5,
        exposure_ema_halflife=5,
    ),
    "QQQ": AssetConfig(
        name="QQQ", close_col="qqq", regime_type="gmm", regime_k=2,
        use_base_rule=True, risk_target_vol=0.15,
        risk_max_exposure=PORTFOLIO_WEIGHTS["QQQ"],
        risk_regime_crisis_cap=PORTFOLIO_WEIGHTS["QQQ"] * 0.5,
        exposure_ema_halflife=5,
    ),
    "IWM": AssetConfig(
        name="IWM", close_col="iwm", regime_type="hmm", regime_k=2,
        use_base_rule=True, risk_target_vol=0.15,
        risk_max_exposure=PORTFOLIO_WEIGHTS["IWM"],
        risk_regime_crisis_cap=PORTFOLIO_WEIGHTS["IWM"] * 0.5,
        exposure_ema_halflife=0,
    ),
    "BTC": AssetConfig(
        name="BTC", close_col="btc_usd", regime_type="hmm", regime_k=2,
        use_base_rule=True, risk_target_vol=0.40,
        risk_max_exposure=PORTFOLIO_WEIGHTS["BTC"],
        risk_regime_crisis_cap=PORTFOLIO_WEIGHTS["BTC"] * 0.3,
        exposure_ema_halflife=0,
    ),
}

# maps our internal column names to yahoo finance ticker symbols
TICKERS = {
    "spy": "SPY", "qqq": "QQQ", "iwm": "IWM", "btc_usd": "BTC-USD",
    "vix": "^VIX", "gld": "GLD", "xlf": "XLF", "xlk": "XLK",
    "xle": "XLE", "xlv": "XLV",
}


def fetch_latest_prices() -> pd.DataFrame:
    """pull new price data from yahoo and append to the existing universe parquet."""
    existing = pd.read_parquet(DATA_PROC / "universe.parquet")
    last_date = existing.index[-1]
    log.info("Universe loaded", extra={"rows": existing.shape[0]})
    print(f"  Existing universe: {existing.shape[0]} rows, ends {last_date.date()}")

    log.info("Fetching latest prices from Yahoo Finance")
    print("  Fetching latest prices from Yahoo Finance...")
    start = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
    # +1 day on end because yfinance uses exclusive end dates
    end = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    new_data = {}
    for col_name, ticker in TICKERS.items():
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)
            if len(df) > 0:
                close = df["Close"]
                # yfinance sometimes returns multi-level columns for single tickers
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]
                close.index = close.index.tz_localize(None)
                new_data[col_name] = close
                # only grab ohlcv extras for assets we actually trade
                if col_name in ["spy", "qqq", "iwm", "btc_usd"]:
                    for field, label in [("High", "high"), ("Low", "low"), ("Volume", "volume")]:
                        s = df[field]
                        if isinstance(s, pd.DataFrame):
                            s = s.iloc[:, 0]
                        s.index = s.index.tz_localize(None)
                        new_data[f"{col_name}_{label}"] = s

                print(f"    {col_name}: {len(close)} new days")
            else:
                print(f"    {col_name}: up to date")
        except Exception as e:
            print(f"    {col_name}: FAILED ({e})")

    if new_data:
        new_df = pd.DataFrame(new_data)
        new_rows = new_df[~new_df.index.isin(existing.index)]
        if len(new_rows) > 0:
            # carry forward columns that weren't in the new fetch (e.g. fama french factors)
            for col in existing.columns:
                if col not in new_rows.columns:
                    last_val = existing[col].iloc[-1]
                    new_rows[col] = last_val
            universe = pd.concat([existing, new_rows]).sort_index()
            # limit ffill to 5 days so stale data doesn't propagate forever
            universe = universe.ffill(limit=5)
            print(f"  Added {len(new_rows)} new rows")
        else:
            universe = existing
            print(f"  No new rows to add")
    else:
        universe = existing
        print(f"  No new data fetched")

    # weekends/holidays sometimes sneak in as duplicate rows from ffill
    spy_dup = (universe["spy"] == universe["spy"].shift(1))
    if "spy_volume" in universe.columns:
        spy_dup = spy_dup & (universe["spy_volume"] == universe["spy_volume"].shift(1))
    non_trading = spy_dup.fillna(False)
    if non_trading.any():
        print(f"  Dropping {non_trading.sum()} non-trading days")
        universe = universe[~non_trading]

    # fama french factors update monthly so they need aggressive forward fill
    lag_cols = [c for c in universe.columns if c.startswith("ff_")]
    for c in lag_cols:
        universe[c] = universe[c].ffill()

    universe.to_parquet(DATA_PROC / "universe.parquet")

    print(f"  Universe: {universe.shape[0]} rows, {universe.shape[1]} columns")
    print(f"  Date range: {universe.index[0].date()} to {universe.index[-1].date()}")
    return universe


def generate_signal_for_asset(asset_name: str, cfg: AssetConfig,
                               universe: pd.DataFrame) -> dict:
    """run the full signal pipeline for one asset and return a summary dict."""
    col = cfg.close_col

    features = engineer_features_for_instrument(universe, col)
    xf = build_cross_asset_features(universe)

    # align all dataframes to the same date index
    common = features.index.intersection(xf.index).intersection(universe.index)
    df_sig = xf.loc[common].copy()

    # pull in per-asset technical indicators for the signal model
    asset_state_cols = [
        "rsi_14", "dist_sma_50", "bollinger_pos", "volatility_21d",
        "volatility_10d", "log_ret_1d", "atr_norm", "volume_ratio_20d",
    ]
    for c in asset_state_cols:
        if c in features.columns:
            df_sig[c] = features.loc[common, c]

    # annualized realized vol for risk sizing
    asset_ret = np.log(universe[col] / universe[col].shift(1))
    df_sig["realized_vol_21d"] = asset_ret.rolling(21, min_periods=15).std() * np.sqrt(252)
    df_sig = df_sig.dropna()

    asset_returns = asset_ret.loc[df_sig.index]

    signals = base_rule(df_sig, universe, asset_name)
    today_signal = float(signals.iloc[-1])

    # pick regime features, equities get extra macro columns btc doesn't
    regime_cols = [c for c in cfg.regime_features if c in df_sig.columns]
    if cfg.name != "BTC":
        regime_cols += [c for c in cfg.equity_regime_extras if c in universe.columns and c in df_sig.columns]

    # fit regime model (gmm or hmm) on standardized features
    rdata = df_sig[regime_cols].dropna()
    sc = StandardScaler()
    X_regime = sc.fit_transform(rdata)
    labels, probs, _ = fit_regime(X_regime, cfg.regime_type, cfg.regime_k)
    # make sure label 0 = crisis (high vol) and 1 = normal (low vol)
    labels, probs = orient_regime_labels(
        labels, probs, df_sig.loc[rdata.index, "volatility_21d"].values, cfg.regime_k
    )

    today_regime = int(labels[-1])
    today_regime_conf = float(np.max(probs[-1]))

    today_date = df_sig.index[-1]
    rv = float(df_sig.iloc[-1]["realized_vol_21d"])
    # use last year of returns for var/kelly calculations
    ret_hist = asset_returns.tail(252)

    risk = risk_engine_v2(
        today_signal, today_signal,
        today_regime, today_regime_conf,
        rv, ret_hist, cfg,
    )

    current_price = float(universe[col].iloc[-1])
    prev_price = float(universe[col].iloc[-2])
    daily_change = (current_price / prev_price - 1) * 100

    max_weight = PORTFOLIO_WEIGHTS.get(asset_name, 0.25)

    return {
        "asset": asset_name,
        "date": today_date.strftime("%Y-%m-%d"),
        "price": round(current_price, 2),
        "daily_change_pct": round(daily_change, 2),
        "signal": "LONG" if today_signal > 0 else "FLAT",
        "portfolio_weight_pct": round(max_weight * 100, 0),
        "exposure_pct": round(risk["recommended_exposure"] * 100, 1),
        "risk_score": risk["risk_score"],
        "regime": "CRISIS" if today_regime == 0 else "NORMAL",
        "regime_confidence": round(today_regime_conf * 100, 1),
        "realized_vol_pct": round(rv * 100, 1),
        "risk_flags": risk["risk_flags"],
        "var_95_pct": round(risk["var_95_1d"] * 100, 3),
        "kelly_fraction": risk["kelly_fraction"],
        "above_sma50": bool(df_sig.iloc[-1].get("dist_sma_50", 0) > 0),
        "rsi_14": round(float(df_sig.iloc[-1].get("rsi_14", 50)), 1),
        "vol_filter_pass": bool(today_signal > 0),
    }


def main():
    """entry point for the daily signal job."""
    t0 = time.time()
    log.info("Daily signal generation started")
    print(f"\n  Daily signals — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    universe = fetch_latest_prices()

    signals = {}
    for asset_name, cfg in ASSET_CONFIGS.items():
        print(f"\n  Processing {asset_name}...")
        try:
            sig = generate_signal_for_asset(asset_name, cfg, universe)
            signals[asset_name] = sig
            log.info("Signal generated", extra={
                "asset": asset_name, "signal": sig["signal"],
                "exposure": sig["exposure_pct"], "regime": sig["regime"],
                "risk_score": sig["risk_score"], "price": sig["price"],
            })
            print(f"    {sig['signal']} @ {sig['exposure_pct']}% | "
                  f"Regime: {sig['regime']} | Risk: {sig['risk_score']}/100")
        except Exception as e:
            log.error("Signal generation failed", extra={"asset": asset_name, "error": str(e)})
            print(f"    ERROR: {e}")
            signals[asset_name] = {"asset": asset_name, "error": str(e)}

    output = {
        "generated_at": datetime.now().isoformat(),
        "market_date": signals.get("SPY", {}).get("date", "unknown"),
        "signals": signals,
    }

    with open(LIVE_SIGNALS_PATH, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  Saved → {LIVE_SIGNALS_PATH}")

    # keep a rolling year of signal history for drift monitoring
    history = []
    if LIVE_HISTORY_PATH.exists():
        with open(LIVE_HISTORY_PATH) as f:
            history = json.load(f)

    history.append(output)
    history = history[-365:]
    with open(LIVE_HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2, default=str)
    print(f"  History: {len(history)} entries → {LIVE_HISTORY_PATH}")

    print("\n  Today's signals:")
    for asset, sig in signals.items():
        if "error" in sig:
            print(f"  {asset:4s}: ERROR — {sig['error']}")
        else:
            print(f"  {asset:4s}: {sig['signal']:5s} @ {sig['exposure_pct']:5.1f}%  "
                  f"| ${sig['price']:>10,.2f} ({sig['daily_change_pct']:+.2f}%)  "
                  f"| {sig['regime']:6s}  | Risk {sig['risk_score']:3d}/100")

    duration = round(time.time() - t0, 1)
    log.info("Daily signal generation complete", extra={"duration_s": duration})


if __name__ == "__main__":
    main()
