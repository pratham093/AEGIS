"""Backtest time series endpoints."""

from fastapi import APIRouter, HTTPException
from api.services.data_loader import (
    get_equity_curve, get_drawdown_series, get_regime_series, ASSETS
)

router = APIRouter(tags=["backtest"])


@router.get("/backtest/{asset}/equity")
def equity_curve(asset: str):
    """Cumulative strategy vs buy-and-hold for one asset."""
    if asset.lower() not in ASSETS:
        raise HTTPException(404, f"Asset {asset} not found")
    return get_equity_curve(asset)


@router.get("/backtest/{asset}/drawdown")
def drawdown(asset: str):
    """Drawdown series from backtest data."""
    if asset.lower() not in ASSETS:
        raise HTTPException(404, f"Asset {asset} not found")
    return get_drawdown_series(asset)


@router.get("/backtest/{asset}/regime")
def regime(asset: str):
    """Regime labels and exposure history."""
    if asset.lower() not in ASSETS:
        raise HTTPException(404, f"Asset {asset} not found")
    return get_regime_series(asset)
