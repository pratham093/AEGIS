"""Signal endpoints for backtest snapshots and live daily outputs."""

import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from api.services.data_loader import (
    get_latest_signals, get_signal_history, get_live_signals, get_live_history, ASSETS
)

router = APIRouter(tags=["signals"])

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # → Backend/


@router.get("/signals/current")
def current_signals():
    """Latest signals from backtest data."""
    return get_latest_signals()


@router.get("/signals/live")
def live_signals():
    """Live signals from the daily pipeline."""
    data = get_live_signals()
    if data is None:
        raise HTTPException(404, "No live signals found. Run: python -m aegis.scripts.daily_signals")
    return data


@router.post("/signals/refresh")
def refresh_signals():
    """Re-run daily signals and return fresh data."""
    result = subprocess.run(
        [sys.executable, "-m", "aegis.scripts.daily_signals"],
        cwd=str(BACKEND_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise HTTPException(500, f"Signal generation failed: {result.stderr[-500:]}")
    data = get_live_signals()
    if data is None:
        raise HTTPException(500, "Signals generated but file not found")
    return data


@router.get("/signals/live/history")
def live_history():
    """Rolling history of daily live signals."""
    data = get_live_history()
    if data is None:
        raise HTTPException(404, "No live signal history found.")
    return data


@router.get("/signals/{asset}/history")
def signal_history(asset: str, days: int = Query(default=30, ge=1, le=365)):
    """Recent backtest signal history for one asset."""
    if asset.lower() not in ASSETS:
        raise HTTPException(404, f"Asset {asset} not found")
    return get_signal_history(asset, days)
