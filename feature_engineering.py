import pandas as pd
import numpy as np
import os
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, ROCIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

# === Directory Setup ===
RAW_DIR = "data"
STRUCTURED_DIR = "STRUCTURED"
os.makedirs(STRUCTURED_DIR, exist_ok=True)

# === Step 1: Load and Clean ===
def load_clean(file_path):
    df = pd.read_csv(file_path)

    # Convert columns to datetime + numeric
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Sort and clean
    df = df.sort_values('Date').dropna()
    df.set_index('Date', inplace=True)
    return df


# === Step 2: Price Features ===
def add_price_features(df):
    df['daily_return'] = df['Close'].pct_change()
    df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))
    df['close_lag_1'] = df['Close'].shift(1)
    df['close_lag_3'] = df['Close'].shift(3)
    df['close_lag_7'] = df['Close'].shift(7)
    return df

# === Step 3: Trend Indicators ===
def add_trend_features(df):
    df['sma_10'] = SMAIndicator(df['Close'], window=10).sma_indicator()
    df['ema_10'] = EMAIndicator(df['Close'], window=10).ema_indicator()
    df['macd'] = MACD(df['Close']).macd_diff()
    return df

# === Step 4: Momentum Indicators ===
def add_momentum_features(df):
    df['rsi_14'] = RSIIndicator(df['Close'], window=14).rsi()
    df['roc_5'] = ROCIndicator(df['Close'], window=5).roc()
    return df

# === Step 5: Volatility Indicators ===
def add_volatility_features(df):
    bb = BollingerBands(df['Close'], window=20, window_dev=2)
    df['bb_mavg'] = bb.bollinger_mavg()
    df['bb_high'] = bb.bollinger_hband()
    df['bb_low'] = bb.bollinger_lband()
    df['atr'] = AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()
    return df

# === Step 6: Volume Indicators ===
def add_volume_features(df):
    df['obv'] = OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
    df['volume_change'] = df['Volume'].pct_change()
    return df

# === Step 7: Generate Label for ML ===
def generate_label(df, forward_days=5):
    df['future_return'] = df['Close'].shift(-forward_days) / df['Close'] - 1
    df['target'] = (df['future_return'] > 0).astype(int)
    return df

# === Step 8: Full Pipeline ===
def process_file(file_path, output_path):
    df = load_clean(file_path)
    df = add_price_features(df)
    df = add_trend_features(df)
    df = add_momentum_features(df)
    df = add_volatility_features(df)
    df = add_volume_features(df)
    df = generate_label(df)
    df.dropna(inplace=True)
    df.to_csv(output_path)
    print(f"[✓] Saved structured file: {os.path.basename(output_path)}")

# === Main ===
def main():
    for file in os.listdir(RAW_DIR):
        if file.endswith('.csv'):
            file_path = os.path.join(RAW_DIR, file)
            output_path = os.path.join(STRUCTURED_DIR, file)
            process_file(file_path, output_path)

if __name__ == "__main__":
    main()
