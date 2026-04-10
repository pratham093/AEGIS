"""Backfill DXY, HYG, IEF into the universe dataset."""
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

PROCESSED = Path(__file__).resolve().parent.parent.parent / 'data' / 'processed'
universe = pd.read_parquet(PROCESSED / 'universe.parquet')
print(f'Current universe: {universe.shape}')
print(f'Date range: {universe.index.min().date()} → {universe.index.max().date()}')

# map yahoo ticker symbols to short column names used in the universe
new_tickers = {
    'DX-Y.NYB': 'dxy',
    'HYG': 'hyg',
    'IEF': 'ief',
}

# match the existing date range so everything lines up
start = str(universe.index.min().date())
end = str(universe.index.max().date())

for ticker, col_name in new_tickers.items():
    if col_name in universe.columns:
        print(f'  {col_name} already in universe — skipping')
        continue
    try:
        print(f'  Fetching {ticker} as {col_name}...')
        data = yf.download(ticker, start=start, end=end, progress=False)
        if len(data) > 0:
            close = data['Close'].squeeze()
            # strip timezone so the index matches the tz-naive universe index
            close.index = close.index.tz_localize(None)
            universe[col_name] = close
            print(f'    ✅ {col_name}: {close.notna().sum()} values')
        else:
            print(f'    ❌ No data for {ticker}')
    except Exception as e:
        print(f'    ❌ Error fetching {ticker}: {e}')

# forward fill small gaps (weekends, holidays) but cap at 5 to avoid hiding real holes
for col in new_tickers.values():
    if col in universe.columns:
        universe[col] = universe[col].ffill(limit=5)

universe.to_parquet(PROCESSED / 'universe.parquet')
print(f'\nUpdated universe: {universe.shape}')
print(f'New columns: {[c for c in new_tickers.values() if c in universe.columns]}')
print(f'Missing values in new columns:')
for col in new_tickers.values():
    if col in universe.columns:
        print(f'  {col}: {universe[col].isna().sum()} ({universe[col].isna().mean()*100:.1f}%)')
