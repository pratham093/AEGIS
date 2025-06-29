import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# === CONFIG ===
START_DATE = "2021-01-01"
END_DATE = "2025-06-15"
INTERVAL = "1d"

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# === ASSET LISTS ===
crypto_assets = [
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD',
    'DOGE-USD', 'ADA-USD', 'AVAX-USD', 'DOT-USD', 'MATIC-USD',
    'SHIB-USD', 'LTC-USD', 'UNI1-USD', 'LINK-USD', 'ETC-USD'
]

tech_stocks = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA',
    'NVDA', 'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE',
    'NFLX', 'PYPL', 'UBER', 'SQ', 'SHOP', 'ZM'
]

finance_stocks = [
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP',
    'SCHW', 'BLK', 'COIN'
]

diverse_stocks = [
    'BA', 'GE', 'XOM', 'CVX', 'CAT', 'UNP', 'F',
    'GM', 'LMT', 'MMM', 'DE', 'NOC'
]

consumer_stocks = [
    'WMT', 'TGT', 'PG', 'PEP', 'KO', 'JNJ', 'PFE',
    'MRK', 'COST', 'MCD', 'DIS', 'NKE', 'HD', 'SBUX'
]

etfs = [
    'SPY', 'QQQ', 'DIA', 'VTI', 'ARKK', 'XLK',
    'XLF', 'XLE', 'XLY', 'IWM'
]

ALL_ASSETS = crypto_assets + tech_stocks + finance_stocks + diverse_stocks + consumer_stocks + etfs

def download_data(ticker, interval="1d"):
    print(f"Fetching: {ticker}")
    try:
        df = yf.download(ticker, start=START_DATE, end=END_DATE, interval=interval, progress=False)

        if df.empty:
            print(f"[!] No data for {ticker}")
            return

        # Ensure 'Date' is a column, not index
        df.reset_index(inplace=True)

        # Keep only the essential OHLCV columns
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

        # Save with consistent formatting
        df.to_csv(f"{DATA_DIR}/{ticker}.csv", index=False)
        print(f"✔ Saved {ticker}.csv")

    except Exception as e:
        print(f"[X] Failed to fetch {ticker}: {e}")

def main():
    for ticker in ALL_ASSETS:
        interval = "1d" if "-USD" in ticker else "1d"
        download_data(ticker, interval)

if __name__ == "__main__":
    main()

