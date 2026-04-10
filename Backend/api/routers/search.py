"""Search endpoint — accepts natural language queries about assets and returns predictions."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from api.services.data_loader import (
    get_live_signals, get_latest_signals, get_metrics, ASSETS
)

router = APIRouter(tags=["search"])

# maps common query terms to their asset symbols
ALIAS_MAP = {
    "spy": "SPY", "s&p": "SPY", "s&p 500": "SPY", "sp500": "SPY",
    "qqq": "QQQ", "nasdaq": "QQQ", "nasdaq 100": "QQQ",
    "iwm": "IWM", "russell": "IWM", "russell 2000": "IWM", "small cap": "IWM",
    "btc": "BTC", "bitcoin": "BTC", "crypto": "BTC",
    "all": "ALL", "portfolio": "ALL", "everything": "ALL",
}


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200, examples=["What is SPY doing?"])


class AssetPrediction(BaseModel):
    asset: str
    signal: str
    exposure_pct: float
    regime: str
    regime_confidence: float
    risk_score: int
    risk_level: str
    entry_conditions: dict
    price: float
    daily_change_pct: float
    risk_flags: list[str]
    backtest_sharpe: float | None = None


class SearchResponse(BaseModel):
    query: str
    matched_assets: list[str]
    predictions: list[AssetPrediction]
    summary: str


def _resolve_assets(query: str) -> list[str]:
    """Match a user query string to asset symbols using the alias map."""
    q = query.lower().strip()

    for alias, symbol in ALIAS_MAP.items():
        if alias in q:
            if symbol == "ALL":
                return ["SPY", "QQQ", "IWM", "BTC"]
            return [symbol]

    # no match found, return all assets
    return ["SPY", "QQQ", "IWM", "BTC"]


def _risk_level(score: int) -> str:
    """Convert numeric risk score to a human-readable label."""
    if score <= 30:
        return "LOW"
    elif score <= 60:
        return "MODERATE"
    else:
        return "HIGH"


def _build_prediction(asset: str, sig: dict, metrics: dict | None) -> AssetPrediction:
    """Assemble a structured prediction response from raw signal data."""
    flags = sig.get("risk_flags", "")
    flag_list = [f.strip() for f in flags.split(",") if f.strip()] if isinstance(flags, str) else flags

    risk_score = sig.get("risk_score", 0)

    return AssetPrediction(
        asset=asset,
        signal=sig.get("signal", "UNKNOWN"),
        exposure_pct=sig.get("exposure_pct", 0.0),
        regime=sig.get("regime", "UNKNOWN"),
        regime_confidence=sig.get("regime_conf", 0.0),
        risk_score=risk_score,
        risk_level=_risk_level(risk_score),
        entry_conditions={
            "trend_sma50": sig.get("above_sma50", False),
            "rsi_above_40": sig.get("rsi_ok", False),
            "volatility_ok": sig.get("vol_filter_pass", False),
        },
        price=sig.get("price", 0.0),
        daily_change_pct=sig.get("daily_change_pct", 0.0),
        risk_flags=flag_list,
        backtest_sharpe=metrics.get("sized_sharpe") if metrics else None,
    )


def _generate_summary(predictions: list[AssetPrediction]) -> str:
    """Generate a one-line summary of the signal state across matched assets."""
    long = [p.asset for p in predictions if p.signal == "LONG"]
    flat = [p.asset for p in predictions if p.signal != "LONG"]

    if not long and flat:
        regimes = set(p.regime for p in predictions)
        return f"All queried assets are FLAT (stay cash). Market regime: {', '.join(regimes)}."
    elif long and not flat:
        return f"All queried assets signal LONG: {', '.join(long)}."
    elif long:
        return f"LONG on {', '.join(long)}; FLAT on {', '.join(flat)}."
    return "No signal data available."


@router.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    """Accept a query about any tracked asset and return the current prediction."""
    matched = _resolve_assets(req.query)

    # prefer live signals, fall back to backtest snapshot
    live = get_live_signals()
    source = live.get("signals", {}) if live else get_latest_signals()

    predictions = []
    for asset in matched:
        sig = source.get(asset)
        if not sig:
            continue
        try:
            metrics = get_metrics(asset.lower())
        except Exception:
            metrics = None
        predictions.append(_build_prediction(asset, sig, metrics))

    if not predictions:
        raise HTTPException(404, f"No predictions found for query: {req.query}")

    return SearchResponse(
        query=req.query,
        matched_assets=matched,
        predictions=predictions,
        summary=_generate_summary(predictions),
    )
