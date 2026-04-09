"""Backtest summary metrics endpoints."""

from fastapi import APIRouter, HTTPException
from api.services.data_loader import get_metrics, get_all_metrics, ASSETS

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def all_metrics():
    """Metrics for all assets."""
    return get_all_metrics()


@router.get("/metrics/{asset}")
def asset_metrics(asset: str):
    """Metrics for a single asset."""
    if asset.lower() not in ASSETS:
        raise HTTPException(404, f"Asset {asset} not found. Available: {ASSETS}")
    return get_metrics(asset)
