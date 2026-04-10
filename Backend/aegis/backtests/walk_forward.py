"""Walk-forward research harness — expanding-window backtest with per-asset regime + signal models."""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import warnings
import joblib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, average_precision_score,
    silhouette_score
)

# optional boosting libraries, gracefully degrade to logistic if missing
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

# hmm gives us sequential regime detection; gmm is the fallback
try:
    from hmmlearn.hmm import GaussianHMM
    HAS_HMM = True
except ImportError:
    HAS_HMM = False

warnings.filterwarnings("ignore")
np.random.seed(42)

# resolve paths relative to the Backend/ root so this works from anywhere
BASE = Path(__file__).resolve().parent.parent.parent  # aegis/backtests/ → Backend/
DATA_RAW = BASE / "data" / "raw"
DATA_PROC = BASE / "data" / "processed"
DATA_FEAT = BASE / "data" / "features"
REPORT_FIG = BASE / "reports" / "figures"
REPORT_MET = BASE / "reports" / "metrics"
MODEL_DIR = BASE / "models"

for d in [REPORT_FIG, REPORT_MET, MODEL_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# per-asset config lets each instrument carry its own regime type,
# signal model, risk parameters, and feature set
@dataclass
class AssetConfig:
    """holds all tunable knobs for a single asset's backtest pipeline."""
    name: str
    close_col: str
    regime_type: str            # "gmm" or "hmm"
    regime_k: int = 2
    signal_model: str = "lightgbm"  # "lightgbm", "xgboost", "logistic"
    horizons: List[int] = field(default_factory=lambda: [5, 10, 21])
    vol_thresh: float = 0.3
    consensus_mode: str = "unanimous"  # "majority" or "unanimous"
    top_n_features: int = 20
    use_base_rule: bool = False  # BTC uses base rule, no ML
    regime_features: List[str] = field(default_factory=lambda: [
        "volatility_21d", "volatility_63d", "log_ret_21d", "rsi_14",
        "dist_sma_50", "dist_sma_200", "atr_norm", "volume_ratio_20d"
    ])
    equity_regime_extras: List[str] = field(default_factory=lambda: ["vix"])
    min_train_days: int = 504    # ~2 years
    step_days: int = 126         # ~6 months
    risk_target_vol: float = 0.15
    risk_max_exposure: float = 1.0
    risk_regime_crisis_cap: float = 0.5
    exposure_ema_halflife: int = 5


# each asset gets its own architecture choices tuned to its behavior
ASSET_CONFIGS = {
    "SPY": AssetConfig(
        name="SPY", close_col="spy", regime_type="gmm",
        signal_model="logistic", top_n_features=20,
    ),
    "QQQ": AssetConfig(
        name="QQQ", close_col="qqq", regime_type="gmm",
        signal_model="lightgbm", top_n_features=20,
    ),
    "IWM": AssetConfig(
        name="IWM", close_col="iwm", regime_type="hmm",
        use_base_rule=True, top_n_features=15,
        exposure_ema_halflife=0,  # base rule needs sharp exits
        # IWM ML: AUC 0.60 but Fold 4 (COVID) AUC=0.19 → model inverts
        # during crashes, producing -0.91 Sharpe. Base rule is safer.
    ),
    "BTC": AssetConfig(
        name="BTC", close_col="btc_usd", regime_type="hmm",
        signal_model="lightgbm", use_base_rule=True,
        top_n_features=15, risk_target_vol=0.40,
        risk_regime_crisis_cap=0.3,
        exposure_ema_halflife=0,  # NO smoothing — base rule needs sharp exits
    ),
}


# data loading

def load_data() -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """load universe prices and per-asset feature parquets."""
    universe = pd.read_parquet(DATA_PROC / "universe.parquet")
    print(f"Universe: {universe.shape}, {universe.index[0]} → {universe.index[-1]}")

    features = {}
    for name, cfg in ASSET_CONFIGS.items():
        path = DATA_FEAT / f"features_{cfg.close_col}.parquet"
        if path.exists():
            df = pd.read_parquet(path).drop(columns=["instrument"], errors="ignore")
            features[name] = df
            print(f"  {name}: {df.shape}")
        else:
            print(f"  {name}: NOT FOUND at {path}")
    return universe, features


# cross-asset feature engineering
# these capture relative momentum, sector dispersion, and macro signals
# that no single-asset feature set can provide on its own

def build_cross_asset_features(universe: pd.DataFrame) -> pd.DataFrame:
    """build inter-asset ratio momentum, dispersion, and macro features."""
    xf = pd.DataFrame(index=universe.index)

    def ratio_mom(a, b, periods=[5, 10]):
        lr = np.log(a / b)
        return {p: lr.diff(p) for p in periods}

    # relative momentum between key pairs
    pairs = [
        ("spy_gld", "spy", "gld"), ("iwm_spy", "iwm", "spy"),
        ("qqq_spy", "qqq", "spy"), ("btc_spy", "btc_usd", "spy"),
    ]
    for pair, a, b in pairs:
        if a in universe.columns and b in universe.columns:
            for p, s in ratio_mom(universe[a], universe[b]).items():
                xf[f"{pair}_mom_{p}d"] = s

    # sector dispersion flags broadening risk-off moves
    sec = [c for c in ["xlf", "xlk", "xle", "xlv"] if c in universe.columns]
    if len(sec) >= 3:
        sr = pd.DataFrame({s: np.log(universe[s] / universe[s].shift(1)) for s in sec})
        xf["sector_disp"] = sr.std(axis=1)
        xf["sector_disp_21d"] = xf["sector_disp"].rolling(21, min_periods=10).mean()
        xf["sector_disp_chg_5d"] = xf["sector_disp_21d"].diff(5)
        xf["sector_breadth"] = (sr > 0).mean(axis=1)
        xf["sector_breadth_5d"] = xf["sector_breadth"].rolling(5, min_periods=3).mean()

    # rolling cross-asset correlations detect regime shifts
    spy_ret = np.log(universe["spy"] / universe["spy"].shift(1))
    for tag, col in [("btc", "btc_usd"), ("gld", "gld")]:
        if col in universe.columns:
            ar = np.log(universe[col] / universe[col].shift(1))
            xf[f"spy_{tag}_corr_21d"] = spy_ret.rolling(21, min_periods=15).corr(ar)
            xf[f"spy_{tag}_corr_chg_5d"] = xf[f"spy_{tag}_corr_21d"].diff(5)

    # yield curve momentum as a macro leading indicator
    if "yield_spread_10y_2y" in universe.columns:
        ys = universe["yield_spread_10y_2y"]
        xf["yield_mom_5d"] = ys.diff(5)
        xf["yield_mom_10d"] = ys.diff(10)
        xf["yield_zscore"] = (
            (ys - ys.rolling(63, min_periods=30).mean())
            / ys.rolling(63, min_periods=30).std()
        )

    # vix mean-reversion signals
    if "vix" in universe.columns:
        v = universe["vix"]
        xf["vix_sma_ratio"] = v / v.rolling(21, min_periods=15).mean()
        xf["vix_zscore"] = (
            (v - v.rolling(63, min_periods=30).mean())
            / v.rolling(63, min_periods=30).std()
        )

    return xf


# regime detection
# gmm clusters market states by volatility and trend features;
# hmm adds temporal transition structure which helps for iwm and btc

def fit_regime(X: np.ndarray, regime_type: str, k: int = 2, seed: int = 42):
    """fit a gmm or hmm regime model and return labels, probabilities, and the fitted model."""
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
        print(f"    [WARN] hmmlearn not installed, falling back to GMM")
        model = GaussianMixture(k, covariance_type="full", n_init=10, random_state=seed)
        labels = model.fit_predict(X)
        probs = model.predict_proba(X)
    return labels, probs, model


def add_regime_features(X_df: pd.DataFrame, labels: np.ndarray,
                        probs: np.ndarray, k: int) -> pd.DataFrame:
    """augment the feature frame with regime labels, confidence, duration, and vol surprise."""
    out = X_df.copy()
    out["regime_label"] = labels
    for i in range(k):
        out[f"regime_prob_{i}"] = probs[:, i]
    out["regime_conf"] = np.max(probs, axis=1)

    # how many consecutive days we've been in the current regime
    changes = (pd.Series(labels, index=out.index) != pd.Series(labels, index=out.index).shift(1))
    groups = changes.cumsum()
    out["regime_dur"] = (groups.groupby(groups).cumcount() + 1).values

    # did a regime switch happen in the last 5 days
    out["regime_switch_5d"] = changes.rolling(5, min_periods=1).max().values

    # vol surprise: current vol relative to the expanding mean for this regime
    # helps detect unusual vol even within a known regime
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


# signal model factory
# each asset can pick its own classifier; logistic for spy (simpler signal),
# lightgbm for qqq (captures nonlinear interactions)

def make_signal_model(model_type: str):
    """return a fresh classifier instance for the given model type."""
    if model_type == "lightgbm" and HAS_LGB:
        return lgb.LGBMClassifier(
            n_estimators=150, max_depth=5, learning_rate=0.03,
            num_leaves=20, subsample=0.7, colsample_bytree=0.7,
            reg_alpha=1.0, reg_lambda=1.0,
            min_child_samples=40, random_state=42, verbose=-1,
        )
    elif model_type == "xgboost" and HAS_XGB:
        return xgb.XGBClassifier(
            n_estimators=150, max_depth=5, learning_rate=0.03,
            subsample=0.7, colsample_bytree=0.7,
            reg_alpha=1.0, reg_lambda=1.0, min_child_weight=40,
            random_state=42, eval_metric="logloss", verbosity=0,
        )
    elif model_type == "logistic":
        return LogisticRegression(max_iter=1000, C=0.3, random_state=42)
    else:
        print(f"    [WARN] {model_type} not available, falling back to logistic")
        return LogisticRegression(max_iter=1000, C=0.3, random_state=42)


# feature selection
# prune noisy features to reduce overfitting; lgbm importance if available,
# otherwise fall back to univariate correlation ranking

def select_features(X_train: np.ndarray, y_train: np.ndarray,
                    feature_names: List[str], top_n: int = 20) -> List[int]:
    """pick the top_n most informative features using lgbm importance or correlation."""
    if HAS_LGB and len(feature_names) > top_n:
        selector = lgb.LGBMClassifier(
            n_estimators=50, max_depth=4, learning_rate=0.05,
            random_state=42, verbose=-1,
        )
        selector.fit(X_train, y_train)
        importances = selector.feature_importances_
        top_idx = np.argsort(importances)[-top_n:]
        return sorted(top_idx.tolist())
    elif len(feature_names) > top_n:
        corrs = np.array([
            abs(np.corrcoef(X_train[:, i], y_train)[0, 1])
            if np.std(X_train[:, i]) > 1e-10 else 0
            for i in range(X_train.shape[1])
        ])
        top_idx = np.argsort(corrs)[-top_n:]
        return sorted(top_idx.tolist())
    else:
        return list(range(len(feature_names)))


# target construction
# forward returns are vol-scaled so the threshold means the same thing
# across different vol regimes

def build_targets(close: pd.Series, realized_vol: pd.Series,
                  horizons: List[int], vol_thresh: float
                  ) -> Dict[int, pd.Series]:
    """create binary targets for each horizon based on vol-adjusted forward returns."""
    targets = {}
    for h in horizons:
        fwd = np.log(close.shift(-h) / close)
        hvol = realized_vol / np.sqrt(252 / h)
        vs = fwd / hvol.replace(0, np.nan)
        target = pd.Series(np.nan, index=close.index)
        target[vs > vol_thresh] = 1
        target[vs < -vol_thresh] = 0
        targets[h] = target
    return targets


# base rule fallback
# simple trend + momentum + vol filter for assets where ml struggles
# (btc and iwm both use this because their ml models invert during crashes)

def base_rule(features: pd.DataFrame, universe: pd.DataFrame,
              asset_name: str = "BTC") -> pd.Series:
    """long when above sma50, rsi > 40, and vol is below its 75th percentile."""
    signals = pd.Series(0.0, index=features.index)

    above_sma = features["dist_sma_50"] > 0 if "dist_sma_50" in features.columns else True
    rsi_ok = features["rsi_14"] > 40 if "rsi_14" in features.columns else True

    if "volatility_21d" in features.columns:
        vol = features["volatility_21d"]
        vol_threshold = vol.rolling(252, min_periods=63).quantile(0.75)
        vol_ok = vol < vol_threshold
    else:
        vol_ok = True

    signals[above_sma & rsi_ok & vol_ok] = 1.0
    return signals


# risk engine
# converts raw signal probabilities into position sizes using vol targeting,
# regime awareness, drawdown guards, and half-kelly sizing

def kelly_fraction(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """half-kelly fraction clamped to [0, 1] for conservative sizing."""
    if avg_loss == 0 or avg_win == 0:
        return 0.0
    b = avg_win / abs(avg_loss)
    kelly = (b * win_rate - (1 - win_rate)) / b
    return max(0.0, min(kelly * 0.5, 1.0))


def risk_engine_v2(
    signal_prob: float,
    prob_rank_pct: float,       # percentile rank of this prob in recent window
    regime_label: int,
    regime_conf: float,
    realized_vol: float,
    returns_history: pd.Series,
    cfg: AssetConfig,
) -> dict:
    """combine signal strength, vol targeting, regime, and drawdown into a final exposure."""
    flags = []

    # ranking-based sizing: only go long when the signal is above median
    # this adapts to model calibration drift across folds
    if prob_rank_pct < 0.50:
        signal_exposure = 0.0
        if prob_rank_pct < 0.30:
            flags.append("LOW_CONFIDENCE")
    else:
        signal_exposure = (prob_rank_pct - 0.50) / 0.50
        signal_exposure = min(signal_exposure, 1.0)

    # vol targeting: scale exposure inversely with realized vol
    target_vol = cfg.risk_target_vol
    if realized_vol > 0:
        vol_scalar = target_vol / realized_vol
        vol_scalar = np.clip(vol_scalar, 0.1, 2.0)
    else:
        vol_scalar = 1.0

    if realized_vol > target_vol * 2:
        flags.append("HIGH_VOL")

    # regime-based cap: crisis regime (label 0) tightens max exposure
    regime_cap = cfg.risk_max_exposure
    if regime_label == 0:
        regime_cap = cfg.risk_regime_crisis_cap
        flags.append("CRISIS_REGIME")

    # shaky regime confidence means the model isn't sure which state we're in
    if regime_conf < 0.6:
        regime_cap *= 0.8
        flags.append("REGIME_UNSTABLE")

    # tail risk metrics from the trailing return distribution
    hist = returns_history.dropna()
    if len(hist) > 60:
        var_95 = float(np.percentile(hist, 5))
        var_99 = float(np.percentile(hist, 1))
        es_95 = float(hist[hist <= var_95].mean()) if (hist <= var_95).sum() > 0 else var_95
    else:
        var_95, var_99, es_95 = -0.02, -0.04, -0.03

    # drawdown guard: cut exposure when recent losses are steep
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

    # kelly sizing: half-kelly from recent win/loss stats
    if len(hist) > 60:
        wins = hist[hist > 0]
        losses = hist[hist < 0]
        if len(wins) > 10 and len(losses) > 10:
            kf = kelly_fraction(len(wins) / len(hist), float(wins.mean()), float(losses.mean()))
        else:
            kf = 0.5
    else:
        kf = 0.5

    # combine all scalars, then cap by regime and max exposure
    raw_exposure = signal_exposure * vol_scalar * dd_scalar
    capped_exposure = min(raw_exposure, regime_cap, cfg.risk_max_exposure)
    final_exposure = max(0.0, round(capped_exposure, 4))

    # composite risk score (0-100) for monitoring dashboards
    risk_score = int(min(100, max(0,
        (realized_vol / 0.30) * 30
        + (1 - regime_conf) * 20
        + (1 - signal_exposure) * 30
        + abs(min(0, recent_dd)) * 200
    )))

    return {
        "recommended_exposure": final_exposure,
        "risk_score": risk_score,
        "risk_flags": flags,
        "var_95_1d": round(var_95, 6),
        "var_99_1d": round(var_99, 6),
        "expected_shortfall_95": round(es_95, 6) if not np.isnan(es_95) else None,
        "kelly_fraction": round(kf, 4),
        "vol_scalar": round(vol_scalar, 4),
        "regime_cap": regime_cap,
        "signal_exposure": round(signal_exposure, 4),
        "prob_rank_pct": round(prob_rank_pct, 4),
    }


# walk-forward fold generation
# expanding window: every fold sees all history up to that point,
# so later folds benefit from more training data

def generate_expanding_folds(n_rows: int, min_train: int, step: int) -> List[Tuple[int, int, int]]:
    """generate (start, train_end, test_end) tuples for expanding-window walk-forward."""
    folds = []
    train_end = min_train
    while train_end + step <= n_rows:
        test_end = min(train_end + step, n_rows)
        folds.append((0, train_end, test_end))
        train_end += step
    # catch any leftover rows that don't fill a full step
    if train_end < n_rows and folds:
        folds.append((0, train_end, n_rows))
    return folds


# main backtest orchestrator for a single asset

def run_asset_backtest(
    asset_name: str,
    cfg: AssetConfig,
    features: pd.DataFrame,
    universe: pd.DataFrame,
    cross_features: pd.DataFrame,
) -> dict:
    """run full walk-forward backtest for a single asset."""

    print(f"\n{'='*70}")
    print(f"  BACKTEST: {asset_name} ({'base rule' if cfg.use_base_rule else cfg.signal_model})")
    print(f"{'='*70}")

    close_col = cfg.close_col

    # align all dataframes to their shared date range
    common = features.index.intersection(cross_features.index).intersection(universe.index)
    feat = features.loc[common]
    xf = cross_features.loc[common]

    # pull asset-specific state features into the signal frame
    asset_state_cols = [
        "rsi_14", "dist_sma_50", "bollinger_pos", "volatility_21d",
        "volatility_10d", "log_ret_1d", "atr_norm", "volume_ratio_20d",
    ]

    df_sig = xf.copy()
    for c in asset_state_cols:
        if c in feat.columns:
            df_sig[c] = feat.loc[common, c]

    # realized vol from log returns, annualized
    asset_ret = np.log(universe[close_col] / universe[close_col].shift(1))
    df_sig["realized_vol_21d"] = asset_ret.rolling(21, min_periods=15).std() * np.sqrt(252)

    # vix/rv ratio only makes sense for equities, not crypto
    if asset_name != "BTC" and "vix" in universe.columns:
        df_sig["vix_rv_ratio"] = (
            universe.loc[common, "vix"]
            / (df_sig["realized_vol_21d"] * 100).replace(0, np.nan)
        )

    df_sig = df_sig.dropna()
    asset_close = universe.loc[df_sig.index, close_col]
    asset_returns = asset_ret.loc[df_sig.index]

    print(f"  Data: {df_sig.shape[0]} rows, {df_sig.shape[1]} features")
    print(f"  Period: {df_sig.index[0]} → {df_sig.index[-1]}")

    # figure out which regime features are actually available
    rcols = [c for c in cfg.regime_features if c in feat.columns]
    if asset_name != "BTC":
        rcols += [c for c in cfg.equity_regime_extras if c in universe.columns]
    regime_in_sig = [c for c in rcols if c in df_sig.columns]

    # route to the appropriate backtest path
    if cfg.use_base_rule:
        return _run_base_rule_backtest(
            asset_name, cfg, df_sig, feat, universe, asset_close,
            asset_returns, regime_in_sig,
        )

    return _run_ml_signal_backtest(
        asset_name, cfg, df_sig, feat, universe, asset_close,
        asset_returns, regime_in_sig,
    )


# base rule backtest path (no ml)
# still uses regime detection for the risk engine, just skips the signal model

def _run_base_rule_backtest(
    asset_name, cfg, df_sig, feat, universe, asset_close,
    asset_returns, regime_in_sig,
):
    """base rule backtest (no ml) for assets where ml underperforms."""
    print(f"  → Using BASE RULE (no ML signal)")

    signals = base_rule(df_sig, universe, asset_name)
    long_pct = signals.mean() * 100
    print(f"  Base rule: LONG {long_pct:.1f}% of days ({int(signals.sum())} / {len(signals)})")

    # fit regime on entire history (no train/test split needed for base rule)
    rdata = df_sig[regime_in_sig].dropna()
    sc = StandardScaler()
    X_regime = sc.fit_transform(rdata)
    labels, probs, _ = fit_regime(X_regime, cfg.regime_type, cfg.regime_k)

    # orient labels so 0 = high-vol crisis, 1 = calm
    # risk engine keys off regime_label == 0 meaning danger
    for k in range(cfg.regime_k):
        mask = labels == k
        if mask.sum() > 0:
            vol_in_k = df_sig.loc[rdata.index, "volatility_21d"].values[mask].mean()
            if k == 0 and vol_in_k < df_sig["volatility_21d"].mean():
                labels = 1 - labels  # flip
                probs = probs[:, ::-1]
                break

    # run each day through the risk engine
    regime_series = pd.Series(labels, index=rdata.index)
    conf_series = pd.Series(np.max(probs, axis=1), index=rdata.index)

    results = []
    for date in df_sig.index:
        sig = float(signals.get(date, 0))
        rl = int(regime_series.get(date, 1))
        rc = float(conf_series.get(date, 0.5))
        rv = float(df_sig.loc[date, "realized_vol_21d"])
        ret_hist = asset_returns.loc[:date].tail(252)

        risk = risk_engine_v2(
            signal_prob=sig,
            prob_rank_pct=sig,  # base rule: 1.0 when long, 0.0 when flat
            regime_label=rl,
            regime_conf=rc,
            realized_vol=rv,
            returns_history=ret_hist,
            cfg=cfg,
        )
        risk["date"] = date
        risk["signal_prob"] = sig
        risk["asset_ret"] = float(asset_returns.get(date, 0))
        risk["regime_label"] = rl
        results.append(risk)

    return _compute_backtest_metrics(asset_name, cfg, results, asset_returns, df_sig.index)


# ml signal backtest path
# trains a classifier on multi-horizon consensus targets,
# walks forward with expanding windows so no future data leaks

def _run_ml_signal_backtest(
    asset_name, cfg, df_sig, feat, universe, asset_close,
    asset_returns, regime_in_sig,
):
    """ml signal backtest with multi-horizon ensemble."""

    # build vol-scaled targets for each horizon, then combine
    rv = df_sig["realized_vol_21d"]
    targets = build_targets(asset_close, rv, cfg.horizons, cfg.vol_thresh)

    # consensus across horizons reduces noise from any single lookahead
    target_df = pd.DataFrame(targets)
    valid_mask = target_df.notna().all(axis=1)
    consensus = target_df[valid_mask].mean(axis=1)

    if cfg.consensus_mode == "unanimous":
        # all horizons must agree, much stricter but better balanced
        y_consensus = (consensus == 1.0).astype(int)
    else:
        # majority: > 0.5 means most horizons say favorable
        y_consensus = (consensus > 0.5).astype(int)

    # align features and targets to the same index
    common_idx = df_sig.index.intersection(y_consensus.index)
    df_sig = df_sig.loc[common_idx]
    y_all = y_consensus.loc[common_idx].values

    feat_cols = [c for c in df_sig.columns if c not in ["target"]]
    N = len(df_sig)

    print(f"  After target alignment: {N} rows, {len(feat_cols)} features")
    print(f"  Class balance: {y_all.mean()*100:.1f}% favorable")

    # expanding-window folds: each fold trains on all prior data
    folds = generate_expanding_folds(N, cfg.min_train_days, cfg.step_days)
    print(f"  Walk-forward folds: {len(folds)}")

    # walk-forward loop
    all_fold_metrics = []
    all_test_rows = []

    for fi, (ts, te, te_end) in enumerate(folds):
        fold_dates = df_sig.index[te:te_end]
        print(f"    Fold {fi+1}: train={df_sig.index[ts]}→{df_sig.index[te-1]} "
              f"({te} rows), test={df_sig.index[te]}→{df_sig.index[te_end-1]} "
              f"({te_end-te} rows)")

        # regime detection: fit on train, predict on test with the same scaler
        r_input = [c for c in regime_in_sig if c in df_sig.columns]
        if len(r_input) > 0:
            rd_tr = df_sig.iloc[ts:te][r_input].values
            rd_te = df_sig.iloc[te:te_end][r_input].values
            sr = StandardScaler()
            rtr = sr.fit_transform(rd_tr)
            rte = sr.transform(rd_te)

            # fit regime model on train, apply to both train and test
            if cfg.regime_type == "gmm":
                rm = GaussianMixture(cfg.regime_k, covariance_type="full",
                                     n_init=10, random_state=42)
                trl = rm.fit_predict(rtr)
                trp = rm.predict_proba(rtr)
                tel = rm.predict(rte)
                tep = rm.predict_proba(rte)
            elif cfg.regime_type == "hmm" and HAS_HMM:
                rm = GaussianHMM(cfg.regime_k, covariance_type="full",
                                 n_iter=200, random_state=42)
                rm.fit(rtr)
                trl = rm.predict(rtr)
                trp = rm.predict_proba(rtr)
                tel = rm.predict(rte)
                tep = rm.predict_proba(rte)
            else:
                rm = GaussianMixture(cfg.regime_k, covariance_type="full",
                                     n_init=10, random_state=42)
                trl = rm.fit_predict(rtr)
                trp = rm.predict_proba(rtr)
                tel = rm.predict(rte)
                tep = rm.predict_proba(rte)

            # orient labels so high-vol = 0 (crisis) consistently across folds
            # without this, the risk engine's crisis logic would flip randomly
            if "volatility_21d" in df_sig.columns:
                train_vol = df_sig.iloc[ts:te]["volatility_21d"].values
                vol_by_regime = {}
                for k in range(cfg.regime_k):
                    mask = trl == k
                    if mask.sum() > 0:
                        vol_by_regime[k] = train_vol[mask].mean()
                if len(vol_by_regime) == 2:
                    high_vol_label = max(vol_by_regime, key=vol_by_regime.get)
                    if high_vol_label != 0:
                        trl = 1 - trl
                        trp = trp[:, ::-1]
                        tel = 1 - tel
                        tep = tep[:, ::-1]

            try:
                sil = silhouette_score(rtr, trl)
            except Exception:
                sil = 0.0
        else:
            trl = np.zeros(te)
            trp = np.ones((te, 1))
            tel = np.zeros(te_end - te)
            tep = np.ones((te_end - te, 1))
            sil = 0.0

        # enrich features with regime state before training the signal model
        Xtr = add_regime_features(df_sig.iloc[ts:te].copy(), trl, trp, cfg.regime_k)
        Xte = add_regime_features(df_sig.iloc[te:te_end].copy(), tel, tep, cfg.regime_k)
        all_fc = list(Xtr.columns)

        # feature selection on train only to avoid leakage
        ss = StandardScaler()
        Xtr_s = ss.fit_transform(Xtr)
        Xte_s = ss.transform(Xte)
        ytr = y_all[ts:te]
        yte = y_all[te:te_end]

        selected_idx = select_features(Xtr_s, ytr, all_fc, cfg.top_n_features)
        Xtr_sel = Xtr_s[:, selected_idx]
        Xte_sel = Xte_s[:, selected_idx]

        # train signal model and predict on test
        model = make_signal_model(cfg.signal_model)
        model.fit(Xtr_sel, ytr)
        yp = model.predict(Xte_sel)
        ypr = model.predict_proba(Xte_sel)[:, 1]

        # fold-level evaluation
        acc = accuracy_score(yte, yp)
        f1 = f1_score(yte, yp, zero_division=0)
        try:
            auc = roc_auc_score(yte, ypr)
        except Exception:
            auc = 0.5
        try:
            prauc = average_precision_score(yte, ypr)
        except Exception:
            prauc = 0.5

        all_fold_metrics.append({
            "fold": fi + 1, "acc": acc, "f1": f1, "auc": auc,
            "prauc": prauc, "sil": sil,
            "train_size": te, "test_size": te_end - te,
            "selected_features": [all_fc[i] for i in selected_idx],
        })

        print(f"      AUC={auc:.4f}  F1={f1:.4f}  Sil={sil:.4f}")

        # collect test predictions for post-loop risk engine pass
        for i, date in enumerate(fold_dates):
            all_test_rows.append({
                "date": date,
                "actual": int(yte[i]),
                "prob": float(ypr[i]),
                "regime_label": int(tel[i]),
                "regime_conf": float(np.max(tep[i])),
            })

    # aggregate metrics across all folds
    fm = pd.DataFrame(all_fold_metrics)
    print(f"\n  AGGREGATE: AUC={fm['auc'].mean():.4f}±{fm['auc'].std():.4f}  "
          f"F1={fm['f1'].mean():.4f}  PR-AUC={fm['prauc'].mean():.4f}")

    # apply risk engine to the stitched test predictions
    test_df = pd.DataFrame(all_test_rows).set_index("date").sort_index()
    # overlapping folds can produce duplicate dates, keep the latest
    test_df = test_df[~test_df.index.duplicated(keep="last")]

    # rolling percentile rank adapts to calibration drift across folds
    test_df["prob_rank_pct"] = test_df["prob"].rolling(
        63, min_periods=20
    ).apply(lambda x: (x.iloc[-1] >= x).mean(), raw=False)
    # bootstrap early rows with global rank since rolling window isn't full yet
    early_mask = test_df["prob_rank_pct"].isna()
    if early_mask.any():
        early_probs = test_df.loc[early_mask, "prob"]
        test_df.loc[early_mask, "prob_rank_pct"] = early_probs.rank(pct=True)

    test_df["asset_ret"] = asset_returns.loc[test_df.index]

    # run risk engine on every test day
    risk_results = []
    for date, row in test_df.iterrows():
        rv = float(df_sig.loc[date, "realized_vol_21d"]) if date in df_sig.index else 0.15
        ret_hist = asset_returns.loc[:date].tail(252)

        risk = risk_engine_v2(
            signal_prob=float(row["prob"]),
            prob_rank_pct=float(row["prob_rank_pct"]),
            regime_label=int(row["regime_label"]),
            regime_conf=float(row["regime_conf"]),
            realized_vol=rv,
            returns_history=ret_hist,
            cfg=cfg,
        )
        risk["date"] = date
        risk["signal_prob"] = row["prob"]
        risk["actual"] = row["actual"]
        risk["asset_ret"] = row["asset_ret"]
        risk["regime_label"] = row["regime_label"]
        risk_results.append(risk)

    # diagnostic output for debugging exposure behavior
    diag_df = pd.DataFrame(risk_results)
    print(f"\n  RISK ENGINE DIAGNOSTICS:")
    print(f"    prob range:       [{test_df['prob'].min():.4f}, {test_df['prob'].max():.4f}]")
    print(f"    prob_rank_pct:    [{test_df['prob_rank_pct'].min():.4f}, {test_df['prob_rank_pct'].max():.4f}]")
    print(f"    signal_exposure:  [{diag_df['signal_exposure'].min():.4f}, {diag_df['signal_exposure'].max():.4f}], "
          f"mean={diag_df['signal_exposure'].mean():.4f}")
    print(f"    vol_scalar:       [{diag_df['vol_scalar'].min():.4f}, {diag_df['vol_scalar'].max():.4f}]")
    print(f"    regime_cap:       [{diag_df['regime_cap'].min():.4f}, {diag_df['regime_cap'].max():.4f}]")
    print(f"    kelly:            [{diag_df['kelly_fraction'].min():.4f}, {diag_df['kelly_fraction'].max():.4f}]")
    print(f"    exposure:         [{diag_df['recommended_exposure'].min():.4f}, {diag_df['recommended_exposure'].max():.4f}], "
          f"mean={diag_df['recommended_exposure'].mean():.4f}")
    print(f"    regime_label dist: {diag_df['regime_label'].value_counts().to_dict()}"
          if 'regime_label' in diag_df.columns else "")
    print(f"    days with exp>0:  {(diag_df['recommended_exposure'] > 0).sum()} / {len(diag_df)}")

    return _compute_backtest_metrics(
        asset_name, cfg, risk_results, asset_returns, df_sig.index,
        fold_metrics=all_fold_metrics,
    )


# backtest metrics computation

def _compute_backtest_metrics(
    asset_name: str, cfg: AssetConfig, risk_results: list,
    asset_returns: pd.Series, full_index: pd.DatetimeIndex,
    fold_metrics: list = None, tx_cost_bps: float = 5.0,
) -> dict:
    """compute sharpe, drawdown, turnover, and other strategy metrics from risk engine output."""

    rdf = pd.DataFrame(risk_results).set_index("date").sort_index()

    # ema smoothing on exposure reduces turnover from daily probability jitter
    # disabled (halflife=0) for base-rule assets that need sharp regime exits
    raw_exposure = rdf["recommended_exposure"].copy()
    rdf["raw_exposure"] = raw_exposure
    if cfg.exposure_ema_halflife > 0:
        rdf["recommended_exposure"] = raw_exposure.ewm(
            halflife=cfg.exposure_ema_halflife, min_periods=1
        ).mean()

    # strategy returns net of round-trip transaction costs
    rdf["exposure_change"] = rdf["recommended_exposure"].diff().abs().fillna(0)
    rdf["tx_cost"] = rdf["exposure_change"] * (tx_cost_bps / 10000)
    rdf["sized_ret"] = rdf["recommended_exposure"] * rdf["asset_ret"] - rdf["tx_cost"]

    # cumulative return series for charting
    rdf["cum_sized"] = rdf["sized_ret"].cumsum()
    rdf["cum_bh"] = rdf["asset_ret"].cumsum()

    # strategy vs buy-and-hold comparison metrics
    sr = rdf["sized_ret"]
    bh = rdf["asset_ret"]

    sized_sharpe = float(sr.mean() / sr.std() * np.sqrt(252)) if sr.std() > 0 else 0
    bh_sharpe = float(bh.mean() / bh.std() * np.sqrt(252)) if bh.std() > 0 else 0

    cum_ret_sized = float(rdf["cum_sized"].iloc[-1]) * 100
    cum_ret_bh = float(rdf["cum_bh"].iloc[-1]) * 100

    sized_dd = float((rdf["cum_sized"] - rdf["cum_sized"].cummax()).min()) * 100
    bh_dd = float((rdf["cum_bh"] - rdf["cum_bh"].cummax()).min()) * 100

    avg_exposure = float(rdf["recommended_exposure"].mean()) * 100
    avg_risk = float(rdf["risk_score"].mean())

    sized_vol = float(sr.std() * np.sqrt(252)) * 100
    turnover = float(rdf["exposure_change"].mean()) * 252  # annualized

    # win rate only counts days where we actually had exposure
    exposed = rdf[rdf["recommended_exposure"] > 0.01]
    win_rate = float((exposed["sized_ret"] > 0).mean()) * 100 if len(exposed) > 0 else 0

    # tally risk flags for the summary report
    all_flags = []
    for flags in rdf["risk_flags"]:
        all_flags.extend(flags)
    flag_counts = dict(pd.Series(all_flags).value_counts()) if all_flags else {}

    avg_var95 = float(rdf["var_95_1d"].mean()) * 100

    metrics = {
        "asset": asset_name,
        "architecture": f"{'base_rule' if cfg.use_base_rule else cfg.signal_model} + {cfg.regime_type}",
        "sized_sharpe": round(sized_sharpe, 3),
        "bh_sharpe": round(bh_sharpe, 3),
        "cum_return_sized_pct": round(cum_ret_sized, 2),
        "cum_return_bh_pct": round(cum_ret_bh, 2),
        "max_dd_sized_pct": round(sized_dd, 2),
        "max_dd_bh_pct": round(bh_dd, 2),
        "avg_exposure_pct": round(avg_exposure, 1),
        "avg_risk_score": round(avg_risk, 1),
        "annualized_vol_pct": round(sized_vol, 2),
        "turnover_annual": round(turnover, 2),
        "win_rate_pct": round(win_rate, 1),
        "avg_var95_pct": round(avg_var95, 2),
        "flag_counts": flag_counts,
        "n_test_days": len(rdf),
        "test_period": f"{rdf.index[0]} → {rdf.index[-1]}",
        "tx_cost_bps": tx_cost_bps,
    }

    if fold_metrics:
        fm = pd.DataFrame(fold_metrics)
        metrics["mean_auc"] = round(float(fm["auc"].mean()), 4)
        metrics["std_auc"] = round(float(fm["auc"].std()), 4)
        metrics["mean_f1"] = round(float(fm["f1"].mean()), 4)
        metrics["fold_details"] = fold_metrics

    print(f"\n  ── {asset_name} RESULTS ──")
    print(f"  Sharpe:  {metrics['sized_sharpe']:+.3f}  (B&H: {metrics['bh_sharpe']:+.3f})")
    print(f"  Return:  {metrics['cum_return_sized_pct']:+.2f}%  (B&H: {metrics['cum_return_bh_pct']:+.2f}%)")
    print(f"  MaxDD:   {metrics['max_dd_sized_pct']:.2f}%  (B&H: {metrics['max_dd_bh_pct']:.2f}%)")
    print(f"  Exposure: {metrics['avg_exposure_pct']:.1f}%  |  Win rate: {metrics['win_rate_pct']:.1f}%")
    print(f"  Turnover: {metrics['turnover_annual']:.2f}x  |  Vol: {metrics['annualized_vol_pct']:.2f}%")
    print(f"  Flags: {flag_counts}")
    if fold_metrics:
        print(f"  AUC: {metrics['mean_auc']:.4f}±{metrics['std_auc']:.4f}")

    return {
        "metrics": metrics,
        "rdf": rdf,
        "fold_metrics": fold_metrics,
    }


# plotting

def plot_backtest_results(all_results: Dict[str, dict]):
    """generate equity curve, exposure, drawdown, and summary bar charts."""

    n_assets = len(all_results)
    colors = {"SPY": "#2ecc71", "QQQ": "#3498db", "IWM": "#9b59b6", "BTC": "#f39c12"}

    # equity curves: strategy vs buy-and-hold for each asset
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, (asset, res) in enumerate(all_results.items()):
        ax = axes[idx]
        rdf = res["rdf"]
        color = colors.get(asset, "#333")

        ax.plot(rdf.index, rdf["cum_sized"] * 100, color=color, linewidth=1.5, label="AEGIS V2.1")
        ax.plot(rdf.index, rdf["cum_bh"] * 100, color="#bbb", linewidth=1, label="Buy & Hold", alpha=0.7)
        ax.fill_between(rdf.index, 0, rdf["cum_sized"] * 100, alpha=0.1, color=color)

        m = res["metrics"]
        ax.set_title(f"{asset}  |  Sharpe: {m['sized_sharpe']:+.3f} vs {m['bh_sharpe']:+.3f}",
                     fontsize=12, fontweight="bold")
        ax.set_ylabel("Cumulative Return (%)")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.suptitle("AEGIS V2.1 — Walk-Forward Equity Curves", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(REPORT_FIG / "v21_equity_curves.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved: {REPORT_FIG / 'v21_equity_curves.png'}")

    # exposure and regime overlay: shows when the strategy scales in/out
    fig, axes = plt.subplots(n_assets, 1, figsize=(16, 4 * n_assets))
    if n_assets == 1:
        axes = [axes]

    for idx, (asset, res) in enumerate(all_results.items()):
        ax = axes[idx]
        rdf = res["rdf"]
        color = colors.get(asset, "#333")

        ax.fill_between(rdf.index, 0, rdf["recommended_exposure"] * 100,
                        alpha=0.4, color=color, label="Exposure")

        # red shading for crisis regime periods
        if "regime_label" in rdf.columns:
            crisis_mask = rdf["regime_label"] == 0
            for start, end in _contiguous_ranges(crisis_mask):
                ax.axvspan(rdf.index[start], rdf.index[end],
                          alpha=0.1, color="red", label="Crisis" if start == 0 else None)

        ax.set_title(f"{asset} — Exposure & Regime", fontsize=12, fontweight="bold")
        ax.set_ylabel("Exposure (%)")
        ax.set_ylim(0, 105)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(REPORT_FIG / "v21_exposure_regime.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {REPORT_FIG / 'v21_exposure_regime.png'}")

    # drawdown comparison: strategy should have shallower drawdowns than buy-and-hold
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, (asset, res) in enumerate(all_results.items()):
        ax = axes[idx]
        rdf = res["rdf"]
        color = colors.get(asset, "#333")

        dd_sized = (rdf["cum_sized"] - rdf["cum_sized"].cummax()) * 100
        dd_bh = (rdf["cum_bh"] - rdf["cum_bh"].cummax()) * 100

        ax.fill_between(rdf.index, dd_sized, 0, alpha=0.4, color=color, label="AEGIS V2.1")
        ax.fill_between(rdf.index, dd_bh, 0, alpha=0.2, color="#bbb", label="Buy & Hold")
        ax.set_title(f"{asset} Drawdown", fontsize=12, fontweight="bold")
        ax.set_ylabel("Drawdown (%)")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(REPORT_FIG / "v21_drawdowns.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {REPORT_FIG / 'v21_drawdowns.png'}")

    # summary bar charts: quick cross-asset comparison
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    assets = list(all_results.keys())
    x = range(len(assets))
    c = [colors.get(a, "#333") for a in assets]

    # sharpe comparison
    aegis_sharpe = [all_results[a]["metrics"]["sized_sharpe"] for a in assets]
    bh_sharpe = [all_results[a]["metrics"]["bh_sharpe"] for a in assets]
    axes[0].bar([i - 0.15 for i in x], aegis_sharpe, 0.3, color=c, label="AEGIS V2.1")
    axes[0].bar([i + 0.15 for i in x], bh_sharpe, 0.3, color="#bbb", label="B&H")
    axes[0].set_xticks(list(x))
    axes[0].set_xticklabels(assets)
    axes[0].set_title("Sharpe Ratio", fontweight="bold")
    axes[0].legend()
    axes[0].axhline(y=0, color="black", linewidth=0.5)
    axes[0].grid(True, alpha=0.3)

    # max drawdown comparison
    aegis_dd = [all_results[a]["metrics"]["max_dd_sized_pct"] for a in assets]
    bh_dd = [all_results[a]["metrics"]["max_dd_bh_pct"] for a in assets]
    axes[1].bar([i - 0.15 for i in x], aegis_dd, 0.3, color=c, label="AEGIS V2.1")
    axes[1].bar([i + 0.15 for i in x], bh_dd, 0.3, color="#bbb", label="B&H")
    axes[1].set_xticks(list(x))
    axes[1].set_xticklabels(assets)
    axes[1].set_title("Max Drawdown (%)", fontweight="bold")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # average exposure per asset
    exp = [all_results[a]["metrics"]["avg_exposure_pct"] for a in assets]
    axes[2].bar(x, exp, color=c)
    axes[2].set_xticks(list(x))
    axes[2].set_xticklabels(assets)
    axes[2].set_title("Avg Exposure (%)", fontweight="bold")
    axes[2].grid(True, alpha=0.3)

    plt.suptitle("AEGIS V2.1 — Cross-Asset Summary", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(REPORT_FIG / "v21_summary_bars.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {REPORT_FIG / 'v21_summary_bars.png'}")


def _contiguous_ranges(mask: pd.Series) -> list:
    """find contiguous True ranges in a boolean series for shading."""
    ranges = []
    start = None
    for i, val in enumerate(mask):
        if val and start is None:
            start = i
        elif not val and start is not None:
            ranges.append((start, i - 1))
            start = None
    if start is not None:
        ranges.append((start, len(mask) - 1))
    return ranges


# output persistence

def save_outputs(all_results: Dict[str, dict]):
    """save summary csv, full metrics json, per-asset parquets, and fold metrics."""

    # summary csv for quick comparison across assets
    summary_rows = []
    for asset, res in all_results.items():
        m = res["metrics"]
        row = {k: v for k, v in m.items() if k not in ["fold_details", "flag_counts"]}
        row["flag_summary"] = str(m.get("flag_counts", {}))
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(REPORT_MET / "v21_backtest_summary.csv", index=False)
    print(f"\n  Saved: {REPORT_MET / 'v21_backtest_summary.csv'}")

    # full json for downstream consumption by the api/dashboard
    metrics_json = {}
    for asset, res in all_results.items():
        m = res["metrics"].copy()
        if "fold_details" in m:
            for fd in m["fold_details"]:
                fd.pop("selected_features", None)  # too verbose for json
        metrics_json[asset] = m

    with open(REPORT_MET / "v21_backtest_metrics.json", "w") as f:
        json.dump(metrics_json, f, indent=2, default=str)
    print(f"  Saved: {REPORT_MET / 'v21_backtest_metrics.json'}")

    # per-asset daily timeseries for detailed analysis
    for asset, res in all_results.items():
        rdf = res["rdf"].copy()
        rdf["risk_flags"] = rdf["risk_flags"].apply(lambda x: ",".join(x) if x else "")
        rdf.to_parquet(DATA_PROC / f"v21_backtest_{asset.lower()}.parquet")
    print(f"  Saved: per-asset backtest parquets to {DATA_PROC}")

    # fold-level metrics for diagnosing per-period model quality
    for asset, res in all_results.items():
        if res.get("fold_metrics"):
            fm = pd.DataFrame(res["fold_metrics"])
            fm.to_csv(REPORT_MET / f"v21_fold_metrics_{asset.lower()}.csv", index=False)
    print(f"  Saved: per-asset fold metrics to {REPORT_MET}")


# entry point

def main():
    """run the full walk-forward backtest across all configured assets."""
    print("=" * 70)
    print("  AEGIS V2.1 — Walk-Forward Backtest")
    print("  Per-asset architecture | Multi-horizon ensemble | Risk v2")
    print("=" * 70)

    # load universe prices and per-asset feature sets
    universe, features = load_data()

    # cross-asset features capture macro context no single asset can see alone
    print("\nBuilding cross-asset features...")
    cross_features = build_cross_asset_features(universe)
    print(f"  Cross-asset features: {cross_features.shape}")

    # run each asset independently with its own config
    all_results = {}
    for asset_name, cfg in ASSET_CONFIGS.items():
        if asset_name not in features:
            print(f"\n  SKIP {asset_name}: features not found")
            continue

        result = run_asset_backtest(
            asset_name, cfg, features[asset_name],
            universe, cross_features,
        )
        all_results[asset_name] = result

    # charts and persistence
    print("\n\nGenerating figures...")
    plot_backtest_results(all_results)

    print("\nSaving outputs...")
    save_outputs(all_results)

    # final cross-asset summary
    print("\n" + "=" * 70)
    print("  AEGIS V2.1 BACKTEST COMPLETE")
    print("=" * 70)
    for asset, res in all_results.items():
        m = res["metrics"]
        print(f"  {asset:4s}: Sharpe={m['sized_sharpe']:+.3f} "
              f"(B&H={m['bh_sharpe']:+.3f})  "
              f"DD={m['max_dd_sized_pct']:.1f}% "
              f"(B&H={m['max_dd_bh_pct']:.1f}%)  "
              f"Exp={m['avg_exposure_pct']:.0f}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
