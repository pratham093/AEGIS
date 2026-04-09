"""Portfolio-level views from asset backtests."""

from fastapi import APIRouter
from api.services.data_loader import get_portfolio_summary

router = APIRouter(tags=["portfolio"])


@router.get("/portfolio/summary")
def portfolio_summary():
    """Equal-weight portfolio summary for the dashboard."""
    return get_portfolio_summary()
