# AEGIS V3

Multi-asset trading signal system that combines regime detection, trend/momentum rules, and risk management to generate daily long/flat signals for SPY, QQQ, IWM, and BTC.

Built this to answer one question every day: should I be in or out?

![Next.js](https://img.shields.io/badge/Next.js-16-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)

## What it does

- Pulls daily OHLCV from Yahoo Finance + macro data from FRED
- Engineers 49 features per asset (volatility, momentum, trend, cross-asset correlations)
- Classifies market regime as NORMAL or CRISIS using GMM/HMM models
- Generates GO LONG or STAY FLAT signals with position sizing
- Risk engine applies vol targeting, regime caps, VaR limits, and drawdown guards
- Dashboard shows live signals, backtest results, and market news

## Backtest results (2015-2026, walk-forward)

| Metric | Portfolio |
|--------|-----------|
| Sharpe | 2.63 |
| Total Return | +232% |
| Max Drawdown | -5.6% |
| Avg Exposure | ~45% |

## Architecture

```
Backend (FastAPI + Python)
├── aegis/pipelines/     # data fetching, feature engineering, EDA
├── aegis/backtests/     # per-asset backtest runners (SPY, QQQ, IWM, BTC)
├── aegis/risk/          # position sizing engine
├── aegis/scripts/       # daily signal generator, cron job
├── api/                 # REST endpoints for the dashboard
└── data/                # raw, processed, features (parquet files)

Frontend (Next.js + TypeScript)
├── src/app/             # pages: landing, signals, backtest, learn
├── src/components/      # charts, cards, interactive flowchart
└── src/lib/api.ts       # typed API client
```

## How the signals work

Three conditions must all pass to go long:

1. Price above 50-day moving average (trend is up)
2. RSI above 40 (momentum isn't collapsing)
3. Volatility below 75th percentile of past year (not too choppy)

If any fails, the signal is FLAT. The risk engine then sizes the position based on vol targeting (15% annual target), regime caps (50% max in crisis), and drawdown guards.

## Setup

### Backend

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# build the dataset (fetches from Yahoo + FRED)
python -m aegis.pipelines.build_dataset
python -m aegis.pipelines.feature_engineering

# run backtests
python -m aegis.backtests.run_all

# generate today's signals
python -m aegis.scripts.daily_signals

# start the API
uvicorn api.main:app --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard at `localhost:3000`, API docs at `localhost:8000/docs`.

Or just run `./start.sh` from the root to start both.

### Docker

```bash
cd Backend
docker build -t aegis-api .
docker run -p 8000:8000 aegis-api
```

## Assets tracked

- **SPY** — S&P 500 (GMM regime, base rule, EMA smoothed)
- **QQQ** — Nasdaq 100 (GMM regime, base rule, EMA smoothed)
- **IWM** — Russell 2000 (HMM regime, base rule, no smoothing)
- **BTC** — Bitcoin (HMM regime, base rule, no smoothing, tighter crisis caps)

## Tech stack

- **Backend:** Python 3.11, FastAPI, scikit-learn, LightGBM, hmmlearn, pandas, yfinance
- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS, Recharts, Three.js/Vanta
- **Data:** Yahoo Finance (OHLCV), FRED (macro), Fama-French (factors)

## Daily cron

The signal generator is meant to run after market close (5:30 PM ET). See `aegis/scripts/cron_refresh.sh` for the crontab setup.

---

Not financial advice. Past performance doesn't guarantee future results.
