"""AEGIS V3 API — serves live signals, backtest data, and search."""

import os
import time
import platform
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.routers import metrics, backtest, signals, portfolio, news, search
from aegis.logging_config import get_logger

log = get_logger("aegis.api")

VERSION = "3.1.0"
BASE = Path(__file__).resolve().parent.parent
DATA_PROC = BASE / "data" / "processed"

app = FastAPI(
    title="AEGIS V3 API",
    description="Multi-asset algorithmic trading signals with regime-aware risk management",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
extra = os.getenv("CORS_ORIGINS", "")
if extra:
    ALLOWED_ORIGINS += [o.strip() for o in extra.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router, prefix="/api")
app.include_router(backtest.router, prefix="/api")
app.include_router(signals.router, prefix="/api")
app.include_router(portfolio.router, prefix="/api")
app.include_router(news.router, prefix="/api")
app.include_router(search.router, prefix="/api")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # skip health check noise
    if request.url.path == "/api/health":
        return await call_next(request)

    t0 = time.time()
    response = await call_next(request)
    duration = round(time.time() - t0, 3)

    log.info(
        f"{request.method} {request.url.path} → {response.status_code}",
        extra={"endpoint": request.url.path, "duration_s": duration},
    )
    return response


@app.get("/api/health")
def health():
    live_ok = (DATA_PROC / "live_signals.json").exists()
    return {
        "status": "healthy",
        "version": VERSION,
        "live_signals_available": live_ok,
    }


@app.get("/api/info")
def info():
    live_signals = DATA_PROC / "live_signals.json"
    last_signal_time = None
    market_date = None
    if live_signals.exists():
        import json
        with open(live_signals) as f:
            data = json.load(f)
        last_signal_time = data.get("generated_at")
        market_date = data.get("market_date")

    backtest_files = list(DATA_PROC.glob("v21_backtest_*.parquet"))
    assets_with_backtest = [f.stem.replace("v21_backtest_", "").upper() for f in backtest_files]

    return {
        "app": "AEGIS V3",
        "version": VERSION,
        "python": platform.python_version(),
        "environment": os.getenv("AEGIS_ENV", "development"),
        "models": {
            "regime": ["GaussianMixture (GMM)", "GaussianHMM (HMM)"],
            "signal": ["base_rule (trend + momentum + volatility)"],
            "risk_engine": "risk_engine_v2 (vol-targeting + regime caps + drawdown guard)",
        },
        "assets_tracked": ["SPY", "QQQ", "IWM", "BTC"],
        "assets_with_backtest": sorted(assets_with_backtest),
        "data": {
            "market_date": market_date,
            "last_signal_generated": last_signal_time,
            "universe_rows": _universe_row_count(),
        },
        "server_time": datetime.now().isoformat(),
    }


def _universe_row_count() -> int | None:
    path = DATA_PROC / "universe.parquet"
    if not path.exists():
        return None
    try:
        import pyarrow.parquet as pq
        return pq.read_metadata(path).num_rows
    except Exception:
        return None
