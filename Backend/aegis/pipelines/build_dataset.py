"""fetch market + macro data and build the unified universe dataset."""

import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader.data as web
from pathlib import Path
from datetime import datetime
import warnings
import time

warnings.filterwarnings("ignore")

# resolve paths relative to the Backend/ root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "2005-01-01"
END_DATE = datetime.today().strftime("%Y-%m-%d")

# instruments we actually predict on vs ones used only as context signals
TARGET_INSTRUMENTS = ["SPY", "QQQ", "IWM", "BTC-USD"]
CONTEXT_INSTRUMENTS = ["^VIX", "XLF", "XLK", "XLE", "XLV", "GLD", "USO"]

ALL_TICKERS = TARGET_INSTRUMENTS + CONTEXT_INSTRUMENTS

# fred series ids mapped to readable column names
FRED_SERIES = {
    "DFF":      "fed_funds_rate",
    "DGS10":    "treasury_10y",
    "DGS2":     "treasury_2y",
    "CPIAUCSL": "cpi",
    "UNRATE":   "unemployment",
    "INDPRO":   "industrial_production",
}


def fetch_ohlcv() -> dict[str, pd.DataFrame]:
    """download daily ohlcv bars for all tickers from yahoo finance."""
    print("\n  Fetching OHLCV from Yahoo Finance...")

    data = {}
    for ticker in ALL_TICKERS:
        print(f"  Fetching {ticker}...", end=" ")
        try:
            df = yf.download(
                ticker,
                start=START_DATE,
                end=END_DATE,
                auto_adjust=True,
                progress=False,
            )

            if df.empty:
                print("EMPTY — skipped")
                continue

            # yfinance sometimes returns multiindex columns for single tickers
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.columns = [c.lower().replace(" ", "_") for c in df.columns]
            df.index.name = "date"

            # sanitize ticker for safe filenames (^VIX -> vix, BTC-USD -> btc_usd)
            safe_name = ticker.replace("^", "").replace("-", "_").lower()
            path = RAW_DIR / f"ohlcv_{safe_name}.parquet"
            df.to_parquet(path, engine="pyarrow")

            data[ticker] = df
            print(f"OK — {len(df)} rows, {df.index.min().date()} to {df.index.max().date()}")
        except Exception as e:
            print(f"FAILED — {e}")

    return data


def fetch_fred() -> pd.DataFrame:
    """pull macro indicators from fred and join them into one dataframe."""
    print("\n  Fetching macro data from FRED...")

    frames = []
    for series_id, friendly_name in FRED_SERIES.items():
        print(f"  Fetching {series_id} ({friendly_name})...", end=" ")
        try:
            df = web.DataReader(series_id, "fred", START_DATE, END_DATE)
            df.columns = [friendly_name]
            frames.append(df)
            print(f"OK — {len(df)} rows")
        except Exception as e:
            print(f"FAILED — {e}")
        # be polite to the fred api
        time.sleep(0.3)

    if not frames:
        print("  WARNING: No FRED data fetched!")
        return pd.DataFrame()

    # iteratively join so we keep the full date range from all series
    macro = frames[0]
    for f in frames[1:]:
        macro = macro.join(f, how="outer")

    macro.index.name = "date"

    # forward fill gaps since macro data publishes at different frequencies
    macro = macro.sort_index().ffill()

    # yield curve inversion is a classic recession signal
    if "treasury_10y" in macro.columns and "treasury_2y" in macro.columns:
        macro["yield_spread_10y_2y"] = macro["treasury_10y"] - macro["treasury_2y"]
        print(f"  Derived: yield_spread_10y_2y")

    path = RAW_DIR / "fred_macro.parquet"
    macro.to_parquet(path, engine="pyarrow")
    print(f"  Saved → {path} ({len(macro)} rows)")

    return macro


def fetch_fama_french() -> pd.DataFrame:
    """grab daily fama french 3 factor data for risk decomposition."""
    print("\n  Fetching Fama-French factors...")

    try:
        ff_data = web.DataReader(
            "F-F_Research_Data_Factors_daily", "famafrench", START_DATE, END_DATE
        )
        df = ff_data[0]
        df.columns = [c.strip().lower().replace("-", "_") for c in df.columns]
        df.index = pd.to_datetime(df.index)
        df.index.name = "date"

        # source data is in percentage points, convert to decimals
        df = df / 100.0

        path = RAW_DIR / "fama_french.parquet"
        df.to_parquet(path, engine="pyarrow")
        print(f"  OK — {len(df)} rows, columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"  FAILED — {e}")
        return pd.DataFrame()


def build_close_matrix(ohlcv_data: dict) -> pd.DataFrame:
    """extract just the close prices from each ticker into a wide dataframe."""
    closes = {}
    for ticker, df in ohlcv_data.items():
        safe_name = ticker.replace("^", "").replace("-", "_").lower()
        if "close" in df.columns:
            closes[safe_name] = df["close"]

    close_matrix = pd.DataFrame(closes)
    close_matrix.index.name = "date"
    return close_matrix


def build_universe(
    ohlcv_data: dict,
    macro: pd.DataFrame,
    ff: pd.DataFrame,
) -> pd.DataFrame:
    """merge all sources into one daily dataset with a cleaning log."""
    print("\n  Building universe dataset...")

    cleaning_log = []

    universe = build_close_matrix(ohlcv_data)

    # add ohlv columns (not just close) for target instruments since models need them
    for ticker in TARGET_INSTRUMENTS:
        if ticker not in ohlcv_data:
            continue
        df = ohlcv_data[ticker]
        safe = ticker.replace("^", "").replace("-", "_").lower()
        for col in ["open", "high", "low", "volume"]:
            if col in df.columns:
                universe[f"{safe}_{col}"] = df[col]

    # left join keeps the market calendar as the spine
    if not macro.empty:
        universe = universe.join(macro, how="left")
    if not ff.empty:
        ff_renamed = ff.add_prefix("ff_")
        universe = universe.join(ff_renamed, how="left")

    universe = universe.sort_index()

    # snapshot raw state before any cleaning for the audit trail
    raw_shape = universe.shape
    raw_missing = universe.isnull().sum().to_dict()
    raw_total_missing = universe.isnull().sum().sum()
    raw_missing_pct = (raw_total_missing / universe.size * 100)

    raw_snapshot_path = PROCESSED_DIR / "universe_raw_snapshot.parquet"
    universe.to_parquet(raw_snapshot_path, engine="pyarrow")

    cleaning_log.append({
        "step": 0,
        "action": "Raw merge of all data sources",
        "rows_before": raw_shape[0],
        "rows_after": raw_shape[0],
        "cols": raw_shape[1],
        "total_missing": int(raw_total_missing),
        "missing_pct": round(raw_missing_pct, 4),
        "detail": f"Merged {len(ohlcv_data)} OHLCV sources + FRED + Fama-French",
    })
    print(f"\n  Step 0 — Raw merge: {raw_shape}, {raw_total_missing} missing values ({raw_missing_pct:.2f}%)")

    # step 1: dedup dates, keeping the latest value if yahoo gives us duplicates
    before_rows = len(universe)
    universe = universe[~universe.index.duplicated(keep="last")]
    after_rows = len(universe)
    dupes_removed = before_rows - after_rows

    cleaning_log.append({
        "step": 1,
        "action": "Remove duplicate timestamps",
        "rows_before": before_rows,
        "rows_after": after_rows,
        "removed": dupes_removed,
        "detail": f"Kept last value for {dupes_removed} duplicate dates",
    })
    print(f"  Step 1 — Duplicates: {dupes_removed} removed ({before_rows} → {after_rows})")

    # step 2: btc trades 24/7 but equities don't, so calendars don't fully overlap
    if "btc_usd" in universe.columns and "spy" in universe.columns:
        btc_only_dates = universe["btc_usd"].notna() & universe["spy"].isna()
        spy_only_dates = universe["spy"].notna() & universe["btc_usd"].isna()
        n_btc_only = btc_only_dates.sum()
        n_spy_only = spy_only_dates.sum()
    else:
        n_btc_only, n_spy_only = 0, 0

    cleaning_log.append({
        "step": 2,
        "action": "Calendar alignment analysis",
        "rows_before": len(universe),
        "rows_after": len(universe),
        "detail": (
            f"BTC-only dates (weekends): {n_btc_only}, "
            f"SPY-only dates: {n_spy_only}. "
            "Kept all dates; NaN indicates market closed."
        ),
    })
    print(f"  Step 2 — Calendar mismatch: {n_btc_only} BTC-only dates, {n_spy_only} SPY-only dates")

    # step 3: fill short gaps causally (no backfill to avoid future leakage)
    missing_before_ffill = universe.isnull().sum().sum()

    # limit=5 prevents filling across long structural gaps like btc pre-2014
    universe = universe.ffill(limit=5)

    missing_after_ffill = universe.isnull().sum().sum()
    filled_count = missing_before_ffill - missing_after_ffill

    cleaning_log.append({
        "step": 3,
        "action": "Forward-fill (limit=5 days, causal only — no backfill)",
        "missing_before": int(missing_before_ffill),
        "missing_after": int(missing_after_ffill),
        "values_filled": int(filled_count),
        "detail": (
            "Forward-fill propagates the last known value forward. "
            "Limit of 5 prevents filling across long data gaps (e.g., BTC not available before 2014). "
            "No backward fill is ever used — that would leak future data."
        ),
    })
    print(f"  Step 3 — Forward-fill: {filled_count} values filled ({missing_before_ffill} → {missing_after_ffill} missing)")

    # step 4: drop rows where any target is still missing after ffill
    # this effectively trims the dataset to the overlapping period
    before_rows = len(universe)
    target_cols = [t.replace("^", "").replace("-", "_").lower() for t in TARGET_INSTRUMENTS]
    available_targets = [c for c in target_cols if c in universe.columns]

    if available_targets:
        universe = universe.dropna(subset=available_targets, how="any")

    after_rows = len(universe)
    dropped = before_rows - after_rows

    cleaning_log.append({
        "step": 4,
        "action": "Drop rows where any target instrument has NaN",
        "rows_before": before_rows,
        "rows_after": after_rows,
        "rows_dropped": dropped,
        "detail": (
            f"Dropped {dropped} rows where at least one of {available_targets} was NaN. "
            "This aligns the dataset to the period where all instruments have data."
        ),
    })
    print(f"  Step 4 — Drop incomplete rows: {dropped} dropped ({before_rows} → {after_rows})")

    # step 5: flag extreme moves but keep them, real crashes matter for regime detection
    outlier_flags = pd.DataFrame(index=universe.index)
    outlier_counts = {}

    for col in available_targets:
        if col in universe.columns:
            returns = np.log(universe[col] / universe[col].shift(1))
            mean_ret = returns.mean()
            std_ret = returns.std()
            z_scores = ((returns - mean_ret) / std_ret).abs()
            is_outlier = z_scores > 4
            outlier_flags[f"{col}_outlier"] = is_outlier.astype(int)
            outlier_counts[col] = int(is_outlier.sum())

    outlier_flags.to_parquet(PROCESSED_DIR / "outlier_flags.parquet", engine="pyarrow")

    cleaning_log.append({
        "step": 5,
        "action": "Outlier detection (flagged, NOT removed)",
        "method": "Z-score > 4 on daily log returns",
        "outliers_per_instrument": outlier_counts,
        "detail": (
            "Extreme return outliers are FLAGGED but kept in the dataset. "
            "Removing them would erase real market events (crashes, squeezes). "
            "The regime model is expected to learn these as distinct market states."
        ),
    })
    print(f"  Step 5 — Outliers flagged (z>4): {outlier_counts}")

    final_missing = universe.isnull().sum().sum()
    final_missing_pct = final_missing / universe.size * 100

    cleaning_log.append({
        "step": 6,
        "action": "Final dataset state",
        "rows": len(universe),
        "cols": len(universe.columns),
        "total_missing": int(final_missing),
        "missing_pct": round(final_missing_pct, 4),
        "date_range": f"{universe.index.min().date()} → {universe.index.max().date()}",
        "detail": "Cleaned dataset ready for feature engineering.",
    })

    path = PROCESSED_DIR / "universe.parquet"
    universe.to_parquet(path, engine="pyarrow")

    # persist the full cleaning audit trail as json
    import json
    log_path = PROCESSED_DIR / "cleaning_log.json"
    with open(log_path, "w") as f:
        json.dump(cleaning_log, f, indent=2, default=str)

    # per column missing value report so we can spot problematic series
    missing_report = pd.DataFrame({
        "column": universe.columns,
        "missing_before_cleaning": [raw_missing.get(c, 0) for c in universe.columns],
        "missing_after_cleaning": [universe[c].isnull().sum() for c in universe.columns],
    })
    missing_report["values_filled"] = missing_report["missing_before_cleaning"] - missing_report["missing_after_cleaning"]
    missing_report.to_csv(PROCESSED_DIR / "missing_value_report.csv", index=False)

    print(f"\n  Raw: {raw_shape[0]} rows, {raw_total_missing} missing ({raw_missing_pct:.2f}%)")
    print(f"  Cleaned: {len(universe)} rows, {final_missing} missing ({final_missing_pct:.2f}%)")
    print(f"  Saved: {path}")

    return universe


def main():
    """run the full data pipeline end to end."""
    print(f"\n  Data pipeline: {START_DATE} to {END_DATE}")

    ohlcv_data = fetch_ohlcv()

    macro = fetch_fred()

    ff = fetch_fama_french()

    universe = build_universe(ohlcv_data, macro, ff)

    print(f"\n  Done: {len(universe)} rows, {len(universe.columns)} cols")

    return universe


if __name__ == "__main__":
    main()
