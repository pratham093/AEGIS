# AEGIS V3 — Full Project Context

Use this document to understand the entire AEGIS V3 codebase. It covers architecture, every file's purpose, data flow, deployment setup, and key design decisions.

## Overview

AEGIS V3 is a multi-asset trading signal system. It pulls daily market data, detects market regimes (normal vs crisis), generates GO LONG / STAY FLAT signals for 4 assets (SPY, QQQ, IWM, BTC), and sizes positions through a multi-layered risk engine. There's a FastAPI backend serving the data and a Next.js frontend dashboard.

**Live URLs:**
- Frontend: https://aegis-3nmu.vercel.app
- Backend API: https://aegis-sx4j.onrender.com
- API docs: https://aegis-sx4j.onrender.com/docs
- GitHub: https://github.com/pratham093/AEGIS

## Tech Stack

**Backend:** Python 3.11, FastAPI, uvicorn, pandas, numpy, scikit-learn, LightGBM, hmmlearn, yfinance, pandas-datareader, matplotlib, seaborn

**Frontend:** Next.js 16, React 19, TypeScript 5, Tailwind CSS 4, Recharts (charts), Three.js + Vanta (3D background)

**Deployment:** Vercel (frontend, free tier) + Render (backend, free tier, Docker)

**Data sources:** Yahoo Finance (OHLCV), FRED (macro indicators), Fama-French (factor returns)

## Repository Structure

```
AEGIS_V3/
├── README.md
├── CONTEXT.md              ← this file
├── .gitignore
├── start.sh                # starts both backend + frontend locally
│
├── Backend/
│   ├── Dockerfile          # multi-stage build, python:3.11-slim
│   ├── docker-compose.yml  # local docker setup
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── scripts/
│   │   └── docker-push.sh  # build + push to Docker Hub
│   │
│   ├── api/                    # FastAPI REST layer
│   │   ├── main.py             # app setup, CORS, health/info endpoints
│   │   ├── routers/
│   │   │   ├── signals.py      # /signals/current, /signals/live, /signals/refresh
│   │   │   ├── backtest.py     # /backtest/{asset}/equity, /drawdown, /regime
│   │   │   ├── metrics.py      # /metrics, /metrics/{asset}
│   │   │   ├── portfolio.py    # /portfolio/summary
│   │   │   ├── news.py         # /news (Yahoo Finance RSS, cached 30min)
│   │   │   └── search.py       # /search (query assets, get predictions)
│   │   └── services/
│   │       └── data_loader.py  # reads parquet/json artifacts, caches in memory
│   │
│   ├── aegis/                      # core logic
│   │   ├── logging_config.py       # console + rotating JSON file logger
│   │   │
│   │   ├── pipelines/
│   │   │   ├── build_dataset.py    # fetches Yahoo + FRED + Fama-French → universe.parquet
│   │   │   ├── feature_engineering.py  # 49 features per asset from universe
│   │   │   └── eda.py             # generates 16 EDA plots + stats
│   │   │
│   │   ├── backtests/
│   │   │   ├── core.py            # shared functions: regime fitting, risk engine, plotting
│   │   │   ├── walk_forward.py    # research harness with expanding-window ML backtests
│   │   │   ├── spy.py             # SPY: GMM regime + base rule + EMA smoothing
│   │   │   ├── qqq.py             # QQQ: GMM regime + base rule + EMA smoothing
│   │   │   ├── iwm.py             # IWM: HMM regime + base rule + no smoothing
│   │   │   ├── btc.py             # BTC: HMM regime + base rule + no smoothing + tight caps
│   │   │   └── run_all.py         # runs all 4 backtests + saves combined outputs
│   │   │
│   │   ├── risk/
│   │   │   └── sizing.py          # standalone position sizing: conviction → caps → smoothing
│   │   │
│   │   └── scripts/
│   │       ├── daily_signals.py   # daily signal generator (meant for cron)
│   │       ├── update_data.py     # one-off: backfill DXY, HYG, IEF into universe
│   │       ├── run_eda_pipeline.py # runs build_dataset → feature_engineering → eda
│   │       └── cron_refresh.sh    # crontab wrapper for daily_signals.py
│   │
│   ├── data/
│   │   ├── raw/                # Yahoo/FRED downloads (gitignored)
│   │   ├── processed/          # universe.parquet, backtest parquets, live_signals.json
│   │   └── features/           # per-asset feature parquets
│   │
│   └── reports/
│       ├── figures/            # all generated plots (EDA, backtest, comparison)
│       └── metrics/            # JSON/CSV metrics from backtests
│
└── frontend/
    ├── package.json
    ├── next.config.ts          # API rewrite proxy: /api/* → backend
    ├── tsconfig.json
    ├── postcss.config.mjs
    ├── eslint.config.mjs
    ├── public/
    │   ├── dark.png            # logo (dark mode)
    │   ├── light.png           # logo (light mode)
    │   └── Flowchart.png
    │
    └── src/
        ├── app/
        │   ├── layout.tsx      # root layout with ThemeProvider
        │   ├── globals.css     # Tailwind + CSS variables for theming
        │   ├── page.tsx        # landing page (hero + stats)
        │   ├── signals/
        │   │   └── page.tsx    # live signals dashboard (server component)
        │   ├── learn/
        │   │   └── page.tsx    # educational page explaining all metrics
        │   └── backtest/
        │       ├── layout.tsx  # sidebar nav for backtest section
        │       ├── page.tsx    # dashboard overview with portfolio stats
        │       └── asset/[slug]/
        │           └── page.tsx # per-asset detail: equity curve, regime, history table
        │
        ├── components/
        │   ├── Navbar.tsx          # top nav with cursor glow effect on links
        │   ├── HeroSection.tsx     # landing hero with interactive text glow
        │   ├── VantaBackground.tsx # Three.js animated net background
        │   ├── CursorGlow.tsx      # green radial glow following cursor
        │   ├── DotGrid.tsx         # canvas dot grid with push-away interaction
        │   ├── Flowchart.tsx       # interactive system architecture flowchart
        │   ├── AssetCard.tsx       # compact asset card (signal, sharpe, exposure)
        │   ├── StatCard.tsx        # single stat display card
        │   ├── MetricsPanel.tsx    # 6-stat grid for per-asset detail page
        │   ├── EquityCurve.tsx     # Recharts line chart: strategy vs buy & hold
        │   ├── RegimeChart.tsx     # Recharts area chart: exposure colored by regime
        │   ├── PortfolioChart.tsx  # portfolio equity curve chart
        │   ├── PositionsTable.tsx  # current positions table
        │   ├── MarketNews.tsx      # Yahoo Finance news cards with shuffle
        │   ├── RefreshButton.tsx   # triggers /signals/refresh, shows spinner
        │   ├── ThemeProvider.tsx   # dark/light theme context
        │   └── ThemeToggle.tsx     # sun/moon toggle button
        │
        └── lib/
            └── api.ts          # typed fetch wrappers for all API endpoints


## Signal Generation Logic

### Entry Rule (base_rule in core.py)
All three must pass to signal LONG:
1. Price > 50-day SMA (trend is up)
2. RSI(14) > 40 (momentum not collapsing)
3. 21-day volatility < 75th percentile of past year

If any fails → FLAT (0% exposure).

This simple rule was chosen over ML classifiers (LightGBM, Logistic) because the ML models inverted during crisis periods in walk-forward testing. The base rule can't invert — it just goes flat.

### Regime Detection
- SPY, QQQ: Gaussian Mixture Model (GMM), k=2
- IWM, BTC: Hidden Markov Model (HMM), k=2
- Input features: volatility_21d, volatility_63d, log_ret_21d, rsi_14, dist_sma_50, dist_sma_200, atr_norm, volume_ratio_20d
- SPY/QQQ also include VIX
- Labels are oriented so regime 0 = high-vol (crisis), regime 1 = low-vol (normal)

### Risk Engine (risk_engine_v2 in core.py)
Takes signal + regime and produces a sized exposure:

1. **Signal sizing:** Uses prob_rank_pct. Below 50th percentile → 0 exposure. Above → linear scale to 1.0
2. **Vol targeting:** Scale exposure so portfolio hits 15% annual vol target (BTC: 40%)
3. **Regime caps:** Crisis regime → max 50% exposure (BTC: 30%). Low confidence → additional 20% haircut
4. **VaR:** Computed from trailing returns (95th and 99th percentile)
5. **Drawdown guard:** Recent drawdown > 5% → scale to 75%. > 10% → scale to 50%
6. **Kelly fraction:** Computed but only used as a diagnostic metric, not for sizing
7. **Final:** min(signal * vol_scalar * dd_scalar, regime_cap, max_exposure)

Risk score (0-100) combines vol level, regime confidence, signal strength, and recent drawdown.

### Position Smoothing
- SPY, QQQ: EMA smoothing with halflife=5 days (reduces turnover)
- IWM, BTC: No smoothing (sharp exits during crashes)

## Data Pipeline

### build_dataset.py
1. Downloads OHLCV from Yahoo Finance for: SPY, QQQ, IWM, BTC-USD, VIX, XLF, XLK, XLE, XLV, GLD, USO
2. Downloads macro from FRED: fed funds rate, 10Y/2Y treasury, CPI, unemployment, industrial production
3. Downloads Fama-French 3-factor daily data
4. Merges into universe.parquet with cleaning log (dedup, ffill limit=5, drop incomplete rows, outlier flagging)
5. Date range: 2005-01-01 to present

### feature_engineering.py
Builds 49 features per asset from the universe:
- Log returns (1d, 5d, 10d, 21d)
- Rolling volatility (5d, 10d, 21d, 63d) + Parkinson estimator
- SMA distances (10, 21, 50, 200)
- MA crossover, RSI(14), ROC, ATR, Bollinger position
- Volume ratio, volume change
- VIX level + change, gold/equity ratio, sector ratios
- Macro columns (yield spread, fed funds, CPI, etc.)
- Fama-French factors
- Credit spread features (HYG/IEF), DXY momentum

All features are causal (no future data leakage).

### daily_signals.py
Runs after market close (designed for 5:30 PM ET cron):
1. Loads existing universe, appends latest Yahoo prices
2. Rebuilds features for each asset
3. Fits regime model on latest data
4. Runs base rule + risk engine
5. Writes live_signals.json + appends to live_signal_history.json (rolling 365-day archive)

Portfolio weights: SPY 30%, QQQ 25%, IWM 25%, BTC 20%

## Backtest Results (walk-forward, 2015-2026)

| Asset | Sharpe | Return | Max DD | B&H Sharpe | B&H DD | Avg Exposure |
|-------|--------|--------|--------|------------|--------|--------------|
| SPY   | +1.07  | +117%  | -8.2%  | +0.73      | -33.7% | 55%          |
| QQQ   | +1.18  | +162%  | -9.1%  | +0.82      | -41.2% | 52%          |
| IWM   | +0.89  | +67%   | -7.8%  | +0.31      | -36.4% | 38%          |
| BTC   | +1.45  | +890%  | -18%   | +1.12      | -83%   | 41%          |
| Portfolio (EW) | 2.63 | +232% | -5.6% | — | — | ~45% |

## API Endpoints

All endpoints are prefixed with `/api`.

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Liveness check |
| GET | /info | Build metadata, model inventory |
| GET | /signals/current | Latest backtest-based signals |
| GET | /signals/live | Live signals from daily pipeline |
| POST | /signals/refresh | Re-run daily signal generator |
| GET | /signals/live/history | Rolling daily signal archive |
| GET | /signals/{asset}/history?days=30 | Backtest signal history |
| GET | /backtest/{asset}/equity | Cumulative return series |
| GET | /backtest/{asset}/drawdown | Drawdown series |
| GET | /backtest/{asset}/regime | Regime + exposure time series |
| GET | /metrics | All assets metrics |
| GET | /metrics/{asset} | Single asset metrics |
| GET | /portfolio/summary | Equal-weight portfolio stats + equity curve |
| GET | /news?shuffle=false | Market news from Yahoo Finance |
| POST | /search | Query assets by name, get predictions |

## Key Data Files

| File | Location | Contents |
|------|----------|----------|
| universe.parquet | data/processed/ | All instruments + macro, daily, ~5000 rows x 40 cols |
| features_{asset}.parquet | data/features/ | 49 engineered features per asset |
| v21_backtest_{asset}.parquet | data/processed/ | Full backtest time series with exposures, returns, flags |
| v21_{asset}_metrics.json | reports/metrics/ | Sharpe, return, drawdown, exposure, win rate, VaR |
| live_signals.json | data/processed/ | Current day's signal snapshot |
| live_signal_history.json | data/processed/ | Rolling 365-day archive of daily signals |

## Frontend Architecture

- Server components (pages) fetch data at request time with `cache: "no-store"`
- Client components handle interactivity (charts, theme toggle, refresh button)
- API calls from server components go direct to backend URL (env var)
- API calls from client components go through Next.js rewrite proxy (`/api/*` → backend)
- Theme: dark/light mode via CSS variables + React context
- Charts: Recharts (LineChart, AreaChart)
- Landing page effects: Vanta.js (Three.js net), cursor glow, dot grid canvas

## Environment Variables

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL` — backend URL (e.g., `https://aegis-sx4j.onrender.com`)

### Backend (Render)
- `CORS_ORIGINS` — comma-separated allowed origins (e.g., `https://aegis-3nmu.vercel.app`)
- `AEGIS_ENV` — `production` or `development`

## Deployment Notes

- Render free tier spins down after 15min idle. First request takes 30-50s cold start.
- Backend runs 2 uvicorn workers in Docker.
- Data files (parquet, json) are committed to git and baked into the Docker image.
- To update signals in production: hit the Refresh button on the signals page, or POST to /api/signals/refresh. This runs daily_signals.py which fetches latest prices from Yahoo.
- Raw data (data/raw/) is gitignored — regenerate with `python -m aegis.pipelines.build_dataset`.

## Local Development

```bash
# start both services
./start.sh

# stop both
./start.sh stop

# or manually:
cd Backend && source .venv/bin/activate && uvicorn api.main:app --port 8000
cd frontend && npm run dev
```

Dashboard: http://localhost:3000
API docs: http://localhost:8000/docs

## Design Decisions

1. **Base rule over ML:** Walk-forward testing showed LightGBM/Logistic models inverted during crisis periods (AUC dropped to 0.19 in COVID fold for IWM). The base rule is simpler but can't invert — it just goes flat.

2. **GMM for equities, HMM for IWM/BTC:** HMM captures regime persistence better for assets with longer crisis periods. GMM is simpler and sufficient for SPY/QQQ.

3. **No smoothing for IWM/BTC:** These assets can gap violently. EMA smoothing would delay exits during crashes. SPY/QQQ are smoother so EMA reduces unnecessary turnover.

4. **Ranking-based sizing:** Instead of requiring model probability > threshold (which fails when AUCs are ~0.52), the risk engine uses the probability's percentile rank in a recent window. Top 50% → scale exposure, bottom 50% → zero.

5. **Kelly as diagnostic only:** Kelly fraction computed on daily returns produces near-zero or negative values (win rate ~53%, win/loss ~0.9). Using it as a hard cap would zero out all positions. It's reported but doesn't size.

6. **49 features, 4 used for entry:** The full feature set feeds the regime model and the walk-forward research harness. Production signals only check 3 conditions (SMA, RSI, vol) because they proved more robust than the ML models.
