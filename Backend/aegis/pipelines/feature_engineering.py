"""Feature engineering — builds causal features per asset from the universe dataset."""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # aegis/pipelines/ → Backend/
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FEATURES_DIR = BASE_DIR / "data" / "features"
FEATURES_DIR.mkdir(parents=True, exist_ok=True)

TARGET_INSTRUMENTS = ["spy", "qqq", "iwm", "btc_usd"]


def compute_log_returns(series: pd.Series, periods: list[int] = [1, 5, 10, 21]) -> pd.DataFrame:
    results = {}
    for p in periods:
        results[f"log_ret_{p}d"] = np.log(series / series.shift(p))
    return pd.DataFrame(results, index=series.index)


def compute_rolling_volatility(returns_1d: pd.Series, windows: list[int] = [5, 10, 21, 63]) -> pd.DataFrame:
    results = {}
    for w in windows:
        results[f"volatility_{w}d"] = returns_1d.rolling(window=w, min_periods=w).std() * np.sqrt(252)
    return pd.DataFrame(results, index=returns_1d.index)


def compute_sma(series: pd.Series, windows: list[int] = [10, 21, 50, 200]) -> pd.DataFrame:
    results = {}
    for w in windows:
        sma = series.rolling(window=w, min_periods=w).mean()
        results[f"sma_{w}"] = sma
        results[f"dist_sma_{w}"] = (series - sma) / sma
    return pd.DataFrame(results, index=series.index)


def compute_ma_crossover(series: pd.Series, fast: int = 10, slow: int = 50) -> pd.Series:
    fast_ma = series.rolling(window=fast, min_periods=fast).mean()
    slow_ma = series.rolling(window=slow, min_periods=slow).mean()
    return (fast_ma > slow_ma).astype(float)


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(window=period, min_periods=period).mean()


def compute_volume_features(volume: pd.Series) -> pd.DataFrame:
    results = {}
    vol_ma_20 = volume.rolling(window=20, min_periods=20).mean()
    results["volume_ratio_20d"] = volume / vol_ma_20.replace(0, np.nan)
    results["volume_change"] = volume.pct_change()
    results["volume_ma_20"] = vol_ma_20
    return pd.DataFrame(results, index=volume.index)


def compute_parkinson_volatility(high: pd.Series, low: pd.Series, window: int = 21) -> pd.Series:
    log_hl = np.log(high / low) ** 2
    factor = 1 / (4 * np.log(2))
    return np.sqrt(factor * log_hl.rolling(window=window, min_periods=window).mean()) * np.sqrt(252)


def compute_rate_of_change(series: pd.Series, period: int = 10) -> pd.Series:
    return (series - series.shift(period)) / series.shift(period)


def compute_bollinger_position(close: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.Series:
    sma = close.rolling(window=window, min_periods=window).mean()
    std = close.rolling(window=window, min_periods=window).std()
    upper = sma + num_std * std
    lower = sma - num_std * std
    width = upper - lower
    return ((close - lower) / width.replace(0, np.nan)).clip(0, 1)


def engineer_features_for_instrument(
    universe: pd.DataFrame,
    symbol: str,
) -> pd.DataFrame:
    print(f"\n  Engineering features for {symbol.upper()}...")

    features = pd.DataFrame(index=universe.index)
    features["date"] = universe.index

    close = universe[symbol]
    high = universe.get(f"{symbol}_high")
    low = universe.get(f"{symbol}_low")
    volume = universe.get(f"{symbol}_volume")

    log_rets = compute_log_returns(close, periods=[1, 5, 10, 21])
    for col in log_rets.columns:
        features[col] = log_rets[col]
    print(f"    Returns: {list(log_rets.columns)}")

    if "log_ret_1d" in features.columns:
        vol = compute_rolling_volatility(features["log_ret_1d"], windows=[5, 10, 21, 63])
        for col in vol.columns:
            features[col] = vol[col]
        print(f"    Volatility: {list(vol.columns)}")

    if high is not None and low is not None:
        features["parkinson_vol_21d"] = compute_parkinson_volatility(high, low, window=21)
        print(f"    Parkinson vol: parkinson_vol_21d")

    sma_feats = compute_sma(close, windows=[10, 21, 50, 200])
    dist_cols = [c for c in sma_feats.columns if c.startswith("dist_")]
    for col in dist_cols:
        features[col] = sma_feats[col]
    print(f"    MA distance: {dist_cols}")

    features["ma_cross_10_50"] = compute_ma_crossover(close, fast=10, slow=50)
    print(f"    MA crossover: ma_cross_10_50")

    features["rsi_14"] = compute_rsi(close, period=14)
    print(f"    RSI: rsi_14")

    features["roc_10"] = compute_rate_of_change(close, period=10)
    features["roc_21"] = compute_rate_of_change(close, period=21)
    print(f"    ROC: roc_10, roc_21")

    if high is not None and low is not None:
        features["atr_14"] = compute_atr(high, low, close, period=14)
        features["atr_norm"] = features["atr_14"] / close
        print(f"    ATR: atr_14, atr_norm")

    features["bollinger_pos"] = compute_bollinger_position(close, window=20)
    print(f"    Bollinger: bollinger_pos")

    if volume is not None:
        vol_feats = compute_volume_features(volume)
        for col in vol_feats.columns:
            features[col] = vol_feats[col]
        print(f"    Volume: {list(vol_feats.columns)}")

    if "vix" in universe.columns:
        features["vix"] = universe["vix"]
        features["vix_change_1d"] = universe["vix"].pct_change()
        print(f"    VIX: vix, vix_change_1d")

    if "gld" in universe.columns:
        features["gold_equity_ratio"] = universe["gld"] / close
        print(f"    Gold: gold_equity_ratio")

    if symbol != "spy" and "spy" in universe.columns:
        features[f"{symbol}_spy_ratio"] = close / universe["spy"]
        print(f"    Relative: {symbol}_spy_ratio")

    if "xlk" in universe.columns and "spy" in universe.columns:
        features["xlk_spy_ratio"] = universe["xlk"] / universe["spy"]
    if "xlf" in universe.columns and "spy" in universe.columns:
        features["xlf_spy_ratio"] = universe["xlf"] / universe["spy"]

    macro_cols = [
        "fed_funds_rate", "treasury_10y", "treasury_2y",
        "yield_spread_10y_2y", "cpi", "unemployment",
        "industrial_production",
    ]
    for col in macro_cols:
        if col in universe.columns:
            features[col] = universe[col]
    present_macro = [c for c in macro_cols if c in universe.columns]
    if present_macro:
        print(f"    Macro: {present_macro}")

    ff_cols = [c for c in universe.columns if c.startswith("ff_")]
    for col in ff_cols:
        features[col] = universe[col]
    if ff_cols:
        print(f"    Fama-French: {ff_cols}")

    if "log_ret_1d" in features.columns:
        features["mean_ret_21d"] = features["log_ret_1d"].rolling(21, min_periods=21).mean()
        features["mean_ret_63d"] = features["log_ret_1d"].rolling(63, min_periods=63).mean()
        print(f"    Mean returns: mean_ret_21d, mean_ret_63d")

    if "hyg" in universe.columns and "ief" in universe.columns:
        hyg_ief = np.log(universe["hyg"] / universe["ief"])
        features["credit_spread"] = hyg_ief
        features["credit_spread_mom_5d"] = hyg_ief.diff(5)
        features["credit_spread_mom_21d"] = hyg_ief.diff(21)
        features["credit_spread_zscore"] = (
            (hyg_ief - hyg_ief.rolling(63, min_periods=30).mean())
            / hyg_ief.rolling(63, min_periods=30).std()
        )
        features["credit_spread_vol_21d"] = hyg_ief.diff().rolling(21, min_periods=15).std()
        print(f"    Credit: credit_spread, mom_5d/21d, zscore, vol_21d")

    if "dxy" in universe.columns:
        dxy = universe["dxy"]
        features["dxy_mom_5d"] = np.log(dxy / dxy.shift(5))
        features["dxy_mom_21d"] = np.log(dxy / dxy.shift(21))
        features["dxy_zscore"] = (
            (dxy - dxy.rolling(63, min_periods=30).mean())
            / dxy.rolling(63, min_periods=30).std()
        )
        print(f"    Dollar: dxy_mom_5d/21d, dxy_zscore")

    features = features.drop(columns=["date"], errors="ignore")

    # ffill lagged columns (FF factors, macro) so recent rows aren't dropped
    lagged_cols = [c for c in features.columns if c.startswith("ff_")]
    lagged_cols += [c for c in ["fed_funds_rate", "treasury_10y", "treasury_2y",
                                "yield_spread_10y_2y", "cpi", "unemployment",
                                "industrial_production"] if c in features.columns]
    for c in lagged_cols:
        features[c] = features[c].ffill()

    initial_len = len(features)
    features = features.dropna()
    dropped = initial_len - len(features)

    feature_cols = [c for c in features.columns]
    print(f"\n    TOTAL: {len(feature_cols)} features, {len(features)} rows")
    print(f"    Dropped {dropped} rows (rolling window warmup)")

    return features


def main():
    print("\n  Feature engineering pipeline")

    universe_path = PROCESSED_DIR / "universe.parquet"
    if not universe_path.exists():
        print(f"ERROR: {universe_path} not found. Run build_dataset.py first.")
        return

    universe = pd.read_parquet(universe_path)
    print(f"Loaded universe: {universe.shape}")

    all_features = {}
    for symbol in TARGET_INSTRUMENTS:
        if symbol not in universe.columns:
            print(f"\n  SKIP {symbol} — not in universe")
            continue

        features = engineer_features_for_instrument(universe, symbol)

        features["instrument"] = symbol

        path = FEATURES_DIR / f"features_{symbol}.parquet"
        features.to_parquet(path, engine="pyarrow")
        print(f"    Saved → {path}")

        all_features[symbol] = features

    if all_features:
        combined = pd.concat(all_features.values(), keys=all_features.keys(), names=["symbol", "date"])
        combined_path = FEATURES_DIR / "features_all.parquet"
        combined.to_parquet(combined_path, engine="pyarrow")
        print(f"\n  Combined features saved → {combined_path}")

    print("\n  Feature engineering complete:")

    for symbol, df in all_features.items():
        n_features = len([c for c in df.columns if c != "instrument"])
        print(f"  {symbol:10s}: {n_features} features × {len(df)} rows")


if __name__ == "__main__":
    main()
