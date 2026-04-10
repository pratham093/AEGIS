"""Shared helpers for the per-asset backtests."""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import warnings
import joblib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, average_precision_score,
    silhouette_score
)

# optional heavy deps, degrade gracefully if missing
try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    from hmmlearn.hmm import GaussianHMM
    HAS_HMM = True
except ImportError:
    HAS_HMM = False

warnings.filterwarnings("ignore")
np.random.seed(42)

# resolve project root so all paths work regardless of cwd
BASE = Path(__file__).resolve().parent.parent.parent  # aegis/backtests/ → Backend/
DATA_RAW = BASE / "data" / "raw"
DATA_PROC = BASE / "data" / "processed"
DATA_FEAT = BASE / "data" / "features"
REPORT_FIG = BASE / "reports" / "figures"
REPORT_MET = BASE / "reports" / "metrics"
MODEL_DIR = BASE / "models"

# ensure output dirs exist on import so callers don't have to
for d in [REPORT_FIG, REPORT_MET, MODEL_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class AssetConfig:
    """Per-asset knobs controlling regime detection, signal model, and risk."""
    name: str
    close_col: str
    regime_type: str            # "gmm" or "hmm"
    regime_k: int = 2
    signal_model: str = "lightgbm"
    horizons: List[int] = field(default_factory=lambda: [5, 10, 21])
    # vol-adjusted forward return must exceed this to count as a buy signal
    vol_thresh: float = 0.3
    consensus_mode: str = "unanimous"
    top_n_features: int = 20
    use_base_rule: bool = False
    regime_features: List[str] = field(default_factory=lambda: [
        "volatility_21d", "volatility_63d", "log_ret_21d", "rsi_14",
        "dist_sma_50", "dist_sma_200", "atr_norm", "volume_ratio_20d"
    ])
    # equities get vix as an extra regime input; crypto doesn't
    equity_regime_extras: List[str] = field(default_factory=lambda: ["vix"])
    # walk-forward params: ~2 years train minimum, ~6 month steps
    min_train_days: int = 504
    step_days: int = 126
    # risk engine params
    risk_target_vol: float = 0.15
    risk_max_exposure: float = 1.0
    risk_regime_crisis_cap: float = 0.5
    exposure_ema_halflife: int = 5


def load_universe() -> pd.DataFrame:
    """Load the multi-asset price universe from parquet."""
    universe = pd.read_parquet(DATA_PROC / "universe.parquet")
    print(f"Universe: {universe.shape}, {universe.index[0]} → {universe.index[-1]}")
    return universe


def load_features(close_col: str) -> pd.DataFrame:
    """Load precomputed features for a single asset."""
    path = DATA_FEAT / f"features_{close_col}.parquet"
    df = pd.read_parquet(path).drop(columns=["instrument"], errors="ignore")
    print(f"Features ({close_col}): {df.shape}")
    return df


def build_cross_asset_features(universe: pd.DataFrame) -> pd.DataFrame:
    """Derive cross-asset momentum, dispersion, correlation, and macro signals."""
    xf = pd.DataFrame(index=universe.index)

    def ratio_mom(a, b, periods=[5, 10]):
        """Compute log-ratio momentum between two price series."""
        lr = np.log(a / b)
        return {p: lr.diff(p) for p in periods}

    # relative strength pairs (e.g. risk-on vs risk-off)
    pairs = [
        ("spy_gld", "spy", "gld"), ("iwm_spy", "iwm", "spy"),
        ("qqq_spy", "qqq", "spy"), ("btc_spy", "btc_usd", "spy"),
    ]
    for pair, a, b in pairs:
        if a in universe.columns and b in universe.columns:
            for p, s in ratio_mom(universe[a], universe[b]).items():
                xf[f"{pair}_mom_{p}d"] = s

    # sector dispersion captures breadth of rally/selloff across sectors
    sec = [c for c in ["xlf", "xlk", "xle", "xlv"] if c in universe.columns]
    if len(sec) >= 3:
        sr = pd.DataFrame({s: np.log(universe[s] / universe[s].shift(1)) for s in sec})
        xf["sector_disp"] = sr.std(axis=1)
        xf["sector_disp_21d"] = xf["sector_disp"].rolling(21, min_periods=10).mean()
        xf["sector_disp_chg_5d"] = xf["sector_disp_21d"].diff(5)
        # fraction of sectors with positive daily returns
        xf["sector_breadth"] = (sr > 0).mean(axis=1)
        xf["sector_breadth_5d"] = xf["sector_breadth"].rolling(5, min_periods=3).mean()

    # rolling correlations detect regime shifts (e.g. btc decorrelating from equities)
    spy_ret = np.log(universe["spy"] / universe["spy"].shift(1))
    for tag, col in [("btc", "btc_usd"), ("gld", "gld")]:
        if col in universe.columns:
            ar = np.log(universe[col] / universe[col].shift(1))
            xf[f"spy_{tag}_corr_21d"] = spy_ret.rolling(21, min_periods=15).corr(ar)
            xf[f"spy_{tag}_corr_chg_5d"] = xf[f"spy_{tag}_corr_21d"].diff(5)

    # yield curve features: spread changes signal macro turning points
    if "yield_spread_10y_2y" in universe.columns:
        ys = universe["yield_spread_10y_2y"]
        xf["yield_mom_5d"] = ys.diff(5)
        xf["yield_mom_10d"] = ys.diff(10)
        xf["yield_zscore"] = (
            (ys - ys.rolling(63, min_periods=30).mean())
            / ys.rolling(63, min_periods=30).std()
        )

    # vix features: fear gauge relative to its own recent history
    if "vix" in universe.columns:
        v = universe["vix"]
        xf["vix_sma_ratio"] = v / v.rolling(21, min_periods=15).mean()
        xf["vix_zscore"] = (
            (v - v.rolling(63, min_periods=30).mean())
            / v.rolling(63, min_periods=30).std()
        )

    return xf


def fit_regime(X, regime_type, k=2, seed=42):
    """Fit a GMM or HMM regime model and return labels, probabilities, and the model."""
    if regime_type == "gmm":
        model = GaussianMixture(k, covariance_type="full", n_init=10, random_state=seed)
        labels = model.fit_predict(X)
        probs = model.predict_proba(X)
    elif regime_type == "hmm" and HAS_HMM:
        model = GaussianHMM(k, covariance_type="full", n_iter=200, random_state=seed)
        model.fit(X)
        labels = model.predict(X)
        probs = model.predict_proba(X)
    else:
        # fallback to gmm if hmm unavailable
        model = GaussianMixture(k, covariance_type="full", n_init=10, random_state=seed)
        labels = model.fit_predict(X)
        probs = model.predict_proba(X)
    return labels, probs, model


def orient_regime_labels(labels, probs, vol_values, k=2):
    """Ensure regime 0 = high-vol (crisis) and regime 1 = low-vol (calm)."""
    vol_by_regime = {}
    for r in range(k):
        mask = labels == r
        if mask.sum() > 0:
            vol_by_regime[r] = vol_values[mask].mean()
    # swap labels if the model assigned them backwards
    if len(vol_by_regime) == 2:
        high_vol_label = max(vol_by_regime, key=vol_by_regime.get)
        if high_vol_label != 0:
            labels = 1 - labels
            probs = probs[:, ::-1]
    return labels, probs


def add_regime_features(X_df, labels, probs, k):
    """Enrich feature dataframe with regime-derived columns for the signal model."""
    out = X_df.copy()
    out["regime_label"] = labels
    for i in range(k):
        out[f"regime_prob_{i}"] = probs[:, i]
    out["regime_conf"] = np.max(probs, axis=1)

    # track how long current regime has lasted (regime persistence is predictive)
    changes = (pd.Series(labels, index=out.index) != pd.Series(labels, index=out.index).shift(1))
    groups = changes.cumsum()
    out["regime_dur"] = (groups.groupby(groups).cumcount() + 1).values
    # flag if any regime switch happened in the last 5 days
    out["regime_switch_5d"] = changes.rolling(5, min_periods=1).max().values

    # vol surprise: current vol vs expanding mean within that regime
    # helps catch vol spikes that are unusual even for the current regime
    if "volatility_21d" in out.columns:
        vol = out["volatility_21d"].values
        vs = np.ones(len(vol))
        for r in range(k):
            mask = labels == r
            if mask.sum() > 10:
                rv = pd.Series(vol[mask])
                em = rv.expanding(5).mean().shift(1)
                vs[mask] = (rv / em.replace(0, np.nan)).fillna(1).clip(0.2, 3).values
        out["vol_surprise"] = vs
    return out


def make_signal_model(model_type):
    """Instantiate a classifier for directional signal prediction."""
    if model_type == "lightgbm" and HAS_LGB:
        return lgb.LGBMClassifier(
            n_estimators=150, max_depth=5, learning_rate=0.03,
            num_leaves=20, subsample=0.7, colsample_bytree=0.7,
            reg_alpha=1.0, reg_lambda=1.0, min_child_samples=40,
            random_state=42, verbose=-1,
        )
    elif model_type == "xgboost" and HAS_XGB:
        return xgb.XGBClassifier(
            n_estimators=150, max_depth=5, learning_rate=0.03,
            subsample=0.7, colsample_bytree=0.7, reg_alpha=1.0,
            reg_lambda=1.0, min_child_weight=40,
            random_state=42, eval_metric="logloss", verbosity=0,
        )
    elif model_type == "logistic":
        return LogisticRegression(max_iter=1000, C=0.3, random_state=42)
    else:
        # safe default when requested model isn't available
        return LogisticRegression(max_iter=1000, C=0.3, random_state=42)


def select_features(X_train, y_train, feature_names, top_n=20):
    """Pick the most informative features using tree importance or correlation fallback."""
    if HAS_LGB and len(feature_names) > top_n:
        # quick lgbm fit just to rank feature importances
        selector = lgb.LGBMClassifier(
            n_estimators=50, max_depth=4, learning_rate=0.05,
            random_state=42, verbose=-1,
        )
        selector.fit(X_train, y_train)
        top_idx = np.argsort(selector.feature_importances_)[-top_n:]
        return sorted(top_idx.tolist())
    elif len(feature_names) > top_n:
        # no lgbm available, fall back to univariate correlation ranking
        corrs = np.array([
            abs(np.corrcoef(X_train[:, i], y_train)[0, 1])
            if np.std(X_train[:, i]) > 1e-10 else 0
            for i in range(X_train.shape[1])
        ])
        return sorted(np.argsort(corrs)[-top_n:].tolist())
    else:
        return list(range(len(feature_names)))


def build_targets(close, realized_vol, horizons, vol_thresh):
    """Create binary labels: 1 if vol-adjusted fwd return exceeds threshold, 0 if below negative threshold."""
    targets = {}
    for h in horizons:
        fwd = np.log(close.shift(-h) / close)
        # scale forward return by annualized vol to normalize across regimes
        hvol = realized_vol / np.sqrt(252 / h)
        vs = fwd / hvol.replace(0, np.nan)
        target = pd.Series(np.nan, index=close.index)
        target[vs > vol_thresh] = 1
        target[vs < -vol_thresh] = 0
        targets[h] = target
    return targets


def base_rule(features, universe, asset_name="BTC"):
    """Simple trend + momentum + vol filter as a non-ML baseline signal."""
    signals = pd.Series(0.0, index=features.index)
    above_sma = features["dist_sma_50"] > 0 if "dist_sma_50" in features.columns else True
    rsi_ok = features["rsi_14"] > 40 if "rsi_14" in features.columns else True
    # only go long when vol is below its historical 75th percentile
    if "volatility_21d" in features.columns:
        vol = features["volatility_21d"]
        vol_threshold = vol.rolling(252, min_periods=63).quantile(0.75)
        vol_ok = vol < vol_threshold
    else:
        vol_ok = True
    signals[above_sma & rsi_ok & vol_ok] = 1.0
    return signals


def kelly_fraction(win_rate, avg_win, avg_loss):
    """Compute half-kelly sizing from historical win/loss stats."""
    if avg_loss == 0 or avg_win == 0:
        return 0.0
    b = avg_win / abs(avg_loss)
    kelly = (b * win_rate - (1 - win_rate)) / b
    # half-kelly is more robust to estimation error
    return max(0.0, min(kelly * 0.5, 1.0))


def risk_engine_v2(signal_prob, prob_rank_pct, regime_label, regime_conf,
                   realized_vol, returns_history, cfg):
    """Convert a raw signal probability into a risk-adjusted exposure recommendation."""
    flags = []

    # map signal rank to a 0-1 exposure (below median = sit out)
    if prob_rank_pct < 0.50:
        signal_exposure = 0.0
        if prob_rank_pct < 0.30:
            flags.append("LOW_CONFIDENCE")
    else:
        signal_exposure = (prob_rank_pct - 0.50) / 0.50
        signal_exposure = min(signal_exposure, 1.0)

    # vol targeting: scale up when vol is low, scale down when high
    target_vol = cfg.risk_target_vol
    vol_scalar = np.clip(target_vol / realized_vol, 0.1, 2.0) if realized_vol > 0 else 1.0
    if realized_vol > target_vol * 2:
        flags.append("HIGH_VOL")

    # cap exposure during crisis regimes or when regime confidence is shaky
    regime_cap = cfg.risk_max_exposure
    if regime_label == 0:
        regime_cap = cfg.risk_regime_crisis_cap
        flags.append("CRISIS_REGIME")
    if regime_conf < 0.6:
        regime_cap *= 0.8
        flags.append("REGIME_UNSTABLE")

    # compute tail risk metrics from realized returns
    hist = returns_history.dropna()
    if len(hist) > 60:
        var_95 = float(np.percentile(hist, 5))
        var_99 = float(np.percentile(hist, 1))
        es_95 = float(hist[hist <= var_95].mean()) if (hist <= var_95).sum() > 0 else var_95
    else:
        # not enough history, use conservative defaults
        var_95, var_99, es_95 = -0.02, -0.04, -0.03

    # drawdown guard: cut exposure if recent performance has been ugly
    dd_scalar = 1.0
    recent_dd = 0.0
    if len(hist) > 21:
        recent_cum = hist.tail(63).cumsum()
        recent_dd = float((recent_cum - recent_cum.cummax()).min())
        if recent_dd < -0.10:
            flags.append("DRAWDOWN_GUARD")
            dd_scalar = 0.5
        elif recent_dd < -0.05:
            dd_scalar = 0.75

    # kelly fraction from rolling win/loss stats
    kf = 0.5
    if len(hist) > 60:
        wins, losses = hist[hist > 0], hist[hist < 0]
        if len(wins) > 10 and len(losses) > 10:
            kf = kelly_fraction(len(wins) / len(hist), float(wins.mean()), float(losses.mean()))

    # combine all scalars and enforce caps
    raw_exposure = signal_exposure * vol_scalar * dd_scalar
    capped_exposure = min(raw_exposure, regime_cap, cfg.risk_max_exposure)
    final_exposure = max(0.0, round(capped_exposure, 4))

    # composite risk score (0-100) for dashboards and monitoring
    risk_score = int(min(100, max(0,
        (realized_vol / 0.30) * 30 + (1 - regime_conf) * 20
        + (1 - signal_exposure) * 30 + abs(min(0, recent_dd)) * 200
    )))

    return {
        "recommended_exposure": final_exposure, "risk_score": risk_score,
        "risk_flags": flags, "var_95_1d": round(var_95, 6),
        "var_99_1d": round(var_99, 6),
        "expected_shortfall_95": round(es_95, 6) if not np.isnan(es_95) else None,
        "kelly_fraction": round(kf, 4), "vol_scalar": round(vol_scalar, 4),
        "regime_cap": regime_cap, "signal_exposure": round(signal_exposure, 4),
        "prob_rank_pct": round(prob_rank_pct, 4),
    }


def generate_expanding_folds(n_rows, min_train, step):
    """Create expanding-window walk-forward fold indices to avoid lookahead bias."""
    folds = []
    train_end = min_train
    while train_end + step <= n_rows:
        test_end = min(train_end + step, n_rows)
        folds.append((0, train_end, test_end))
        train_end += step
    # catch any leftover rows that didn't fill a full step
    if train_end < n_rows and folds:
        folds.append((0, train_end, n_rows))
    return folds


def prepare_asset_data(cfg, features, universe, cross_features):
    """Align and merge asset features, cross-asset features, and universe into a clean dataframe."""
    # intersect indices so everything lines up
    common = features.index.intersection(cross_features.index).intersection(universe.index)
    feat = features.loc[common]
    xf = cross_features.loc[common]

    # these per-asset columns get merged into the cross-asset frame
    asset_state_cols = [
        "rsi_14", "dist_sma_50", "bollinger_pos", "volatility_21d",
        "volatility_10d", "log_ret_1d", "atr_norm", "volume_ratio_20d",
    ]

    df_sig = xf.copy()
    for c in asset_state_cols:
        if c in feat.columns:
            df_sig[c] = feat.loc[common, c]

    # realized vol used for position sizing and regime detection
    asset_ret = np.log(universe[cfg.close_col] / universe[cfg.close_col].shift(1))
    df_sig["realized_vol_21d"] = asset_ret.rolling(21, min_periods=15).std() * np.sqrt(252)

    # vix/rv ratio is useful for equities but meaningless for crypto
    if cfg.name != "BTC" and "vix" in universe.columns:
        df_sig["vix_rv_ratio"] = (
            universe.loc[common, "vix"]
            / (df_sig["realized_vol_21d"] * 100).replace(0, np.nan)
        )

    df_sig = df_sig.dropna()
    asset_close = universe.loc[df_sig.index, cfg.close_col]
    asset_returns = asset_ret.loc[df_sig.index]

    # pick which columns feed the regime model
    rcols = [c for c in cfg.regime_features if c in feat.columns]
    if cfg.name != "BTC":
        rcols += [c for c in cfg.equity_regime_extras if c in universe.columns]
    regime_in_sig = [c for c in rcols if c in df_sig.columns]

    return df_sig, asset_close, asset_returns, regime_in_sig


def compute_backtest_metrics(asset_name, cfg, risk_results, asset_returns,
                             fold_metrics=None, tx_cost_bps=5.0):
    """Aggregate walk-forward results into portfolio-level performance metrics."""
    rdf = pd.DataFrame(risk_results).set_index("date").sort_index()

    # smooth exposure changes to reduce whipsaw and turnover
    raw_exposure = rdf["recommended_exposure"].copy()
    rdf["raw_exposure"] = raw_exposure
    if cfg.exposure_ema_halflife > 0:
        rdf["recommended_exposure"] = raw_exposure.ewm(
            halflife=cfg.exposure_ema_halflife, min_periods=1
        ).mean()

    # estimate realistic transaction costs from exposure changes
    rdf["exposure_change"] = rdf["recommended_exposure"].diff().abs().fillna(0)
    rdf["tx_cost"] = rdf["exposure_change"] * (tx_cost_bps / 10000)
    rdf["sized_ret"] = rdf["recommended_exposure"] * rdf["asset_ret"] - rdf["tx_cost"]
    rdf["cum_sized"] = rdf["sized_ret"].cumsum()
    rdf["cum_bh"] = rdf["asset_ret"].cumsum()

    sr, bh = rdf["sized_ret"], rdf["asset_ret"]
    sized_sharpe = float(sr.mean() / sr.std() * np.sqrt(252)) if sr.std() > 0 else 0
    bh_sharpe = float(bh.mean() / bh.std() * np.sqrt(252)) if bh.std() > 0 else 0

    # win rate only counts days where we actually had meaningful exposure
    exposed = rdf[rdf["recommended_exposure"] > 0.01]
    win_rate = float((exposed["sized_ret"] > 0).mean()) * 100 if len(exposed) > 0 else 0

    # tally risk flags across all test days for diagnostics
    all_flags = []
    for flags in rdf["risk_flags"]:
        all_flags.extend(flags)
    flag_counts = dict(pd.Series(all_flags).value_counts()) if all_flags else {}

    metrics = {
        "asset": asset_name,
        "sized_sharpe": round(sized_sharpe, 3),
        "bh_sharpe": round(bh_sharpe, 3),
        "cum_return_sized_pct": round(float(rdf["cum_sized"].iloc[-1]) * 100, 2),
        "cum_return_bh_pct": round(float(rdf["cum_bh"].iloc[-1]) * 100, 2),
        "max_dd_sized_pct": round(float((rdf["cum_sized"] - rdf["cum_sized"].cummax()).min()) * 100, 2),
        "max_dd_bh_pct": round(float((rdf["cum_bh"] - rdf["cum_bh"].cummax()).min()) * 100, 2),
        "avg_exposure_pct": round(float(rdf["recommended_exposure"].mean()) * 100, 1),
        "annualized_vol_pct": round(float(sr.std() * np.sqrt(252)) * 100, 2),
        "turnover_annual": round(float(rdf["exposure_change"].mean()) * 252, 2),
        "win_rate_pct": round(win_rate, 1),
        "avg_var95_pct": round(float(rdf["var_95_1d"].mean()) * 100, 2),
        "flag_counts": flag_counts,
        "n_test_days": len(rdf),
        "test_period": f"{rdf.index[0]} → {rdf.index[-1]}",
    }

    # include ML model quality metrics if available from walk-forward folds
    if fold_metrics:
        fm = pd.DataFrame(fold_metrics)
        metrics["mean_auc"] = round(float(fm["auc"].mean()), 4)
        metrics["std_auc"] = round(float(fm["auc"].std()), 4)
        metrics["mean_f1"] = round(float(fm["f1"].mean()), 4)

    print(f"\n  ── {asset_name} RESULTS ──")
    print(f"  Sharpe:  {metrics['sized_sharpe']:+.3f}  (B&H: {metrics['bh_sharpe']:+.3f})")
    print(f"  Return:  {metrics['cum_return_sized_pct']:+.2f}%  (B&H: {metrics['cum_return_bh_pct']:+.2f}%)")
    print(f"  MaxDD:   {metrics['max_dd_sized_pct']:.2f}%  (B&H: {metrics['max_dd_bh_pct']:.2f}%)")
    print(f"  Exposure: {metrics['avg_exposure_pct']:.1f}%  |  Win rate: {metrics['win_rate_pct']:.1f}%")
    print(f"  Turnover: {metrics['turnover_annual']:.2f}x  |  Vol: {metrics['annualized_vol_pct']:.2f}%")

    return {"metrics": metrics, "rdf": rdf, "fold_metrics": fold_metrics}


def plot_single_asset(asset_name, res, color="#2ecc71"):
    """Generate and save the 4-panel chart set for one asset's backtest."""
    rdf = res["rdf"]
    m = res["metrics"]
    tag = asset_name.lower()

    # panel 1: equity curve comparison
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(rdf.index, rdf["cum_sized"] * 100, color=color, linewidth=1.8, label="AEGIS V3")
    ax.plot(rdf.index, rdf["cum_bh"] * 100, color="#bbb", linewidth=1, label="Buy & Hold", alpha=0.7)
    ax.fill_between(rdf.index, 0, rdf["cum_sized"] * 100, alpha=0.1, color=color)
    ax.set_title(f"{asset_name} — Equity Curve  |  Sharpe: {m['sized_sharpe']:+.3f} vs {m['bh_sharpe']:+.3f}",
                 fontsize=14, fontweight="bold")
    ax.set_ylabel("Cumulative Return (%)")
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORT_FIG / f"v21_{tag}_equity.png", dpi=150, bbox_inches="tight")
    plt.close()

    # panel 2: drawdown comparison (shows risk reduction vs buy-and-hold)
    fig, ax = plt.subplots(figsize=(14, 4))
    dd_sized = (rdf["cum_sized"] - rdf["cum_sized"].cummax()) * 100
    dd_bh = (rdf["cum_bh"] - rdf["cum_bh"].cummax()) * 100
    ax.fill_between(rdf.index, dd_sized, 0, alpha=0.5, color=color, label="AEGIS V3")
    ax.fill_between(rdf.index, dd_bh, 0, alpha=0.2, color="#bbb", label="Buy & Hold")
    ax.set_title(f"{asset_name} — Drawdown", fontsize=14, fontweight="bold")
    ax.set_ylabel("Drawdown (%)")
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORT_FIG / f"v21_{tag}_drawdown.png", dpi=150, bbox_inches="tight")
    plt.close()

    # panel 3: exposure over time with crisis regime shading
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.fill_between(rdf.index, 0, rdf["recommended_exposure"] * 100,
                    alpha=0.5, color=color, label="Exposure")
    if "regime_label" in rdf.columns:
        crisis_mask = rdf["regime_label"] == 0
        in_crisis = False
        start = None
        for i, (idx, val) in enumerate(crisis_mask.items()):
            if val and not in_crisis:
                start = idx
                in_crisis = True
            elif not val and in_crisis:
                ax.axvspan(start, idx, alpha=0.08, color="red")
                in_crisis = False
        if in_crisis and start:
            ax.axvspan(start, rdf.index[-1], alpha=0.08, color="red")
    ax.set_title(f"{asset_name} — Exposure & Regime Overlay", fontsize=14, fontweight="bold")
    ax.set_ylabel("Exposure (%)")
    ax.set_ylim(0, 105)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORT_FIG / f"v21_{tag}_exposure.png", dpi=150, bbox_inches="tight")
    plt.close()

    # panel 4: rolling 6-month sharpe to see consistency over time
    fig, ax = plt.subplots(figsize=(14, 4))
    rolling_sharpe = rdf["sized_ret"].rolling(126, min_periods=63).apply(
        lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
    )
    rolling_bh = rdf["asset_ret"].rolling(126, min_periods=63).apply(
        lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
    )
    ax.plot(rolling_sharpe.index, rolling_sharpe, color=color, linewidth=1.5, label="AEGIS V3")
    ax.plot(rolling_bh.index, rolling_bh, color="#bbb", linewidth=1, label="Buy & Hold", alpha=0.7)
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.set_title(f"{asset_name} — Rolling 6M Sharpe", fontsize=14, fontweight="bold")
    ax.set_ylabel("Sharpe Ratio")
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORT_FIG / f"v21_{tag}_rolling_sharpe.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"  Saved 4 figures for {asset_name} → {REPORT_FIG}/v21_{tag}_*.png")


def save_asset_outputs(asset_name, res):
    """Persist metrics json, backtest parquet, and fold-level csv for one asset."""
    tag = asset_name.lower()
    m = res["metrics"]

    with open(REPORT_MET / f"v21_{tag}_metrics.json", "w") as f:
        json.dump(m, f, indent=2, default=str)

    # flatten risk_flags list to csv-friendly string before saving
    rdf = res["rdf"].copy()
    rdf["risk_flags"] = rdf["risk_flags"].apply(lambda x: ",".join(x) if x else "")
    rdf.to_parquet(DATA_PROC / f"v21_backtest_{tag}.parquet")

    if res.get("fold_metrics"):
        pd.DataFrame(res["fold_metrics"]).to_csv(
            REPORT_MET / f"v21_{tag}_fold_metrics.csv", index=False
        )

    print(f"  Saved outputs for {asset_name}")
