"""Market news endpoint — fetches articles from Yahoo Finance for tracked tickers."""

from fastapi import APIRouter, Query
import yfinance as yf
from datetime import datetime
import random

router = APIRouter(tags=["news"])

# tickers we pull news for, mapped to display names
TICKERS = {
    "SPY": "S&P 500",
    "QQQ": "Nasdaq 100",
    "IWM": "Russell 2000",
    "BTC-USD": "Bitcoin",
}

# simple in-memory cache to avoid hitting Yahoo on every page load
_cache: dict = {"data": None, "ts": 0}
CACHE_TTL = 1800  # 30 min


def _fetch_all_articles() -> list[dict]:
    """Fetch and deduplicate articles from Yahoo across all tracked tickers."""
    now = datetime.now().timestamp()

    # return cached data if still fresh
    if _cache["data"] and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["data"]

    by_ticker: dict[str, list[dict]] = {}
    seen_ids: set[str] = set()  # track IDs to avoid duplicate articles

    for ticker, label in TICKERS.items():
        tag = ticker.replace("-USD", "")
        by_ticker[tag] = []
        try:
            t = yf.Ticker(ticker)
            news = t.news or []
            for item in news[:8]:
                content = item.get("content", {})
                article_id = content.get("id", "")

                # skip duplicates (same article often appears under multiple tickers)
                if article_id in seen_ids:
                    continue
                seen_ids.add(article_id)

                # extract thumbnail URL from nested resolution list
                thumb = content.get("thumbnail", {})
                thumb_url = ""
                resolutions = thumb.get("resolutions", [])
                if resolutions:
                    thumb_url = resolutions[0].get("url", "")

                canonical = content.get("canonicalUrl", {})
                url = canonical.get("url", "")

                article = {
                    "id": article_id,
                    "title": content.get("title", ""),
                    "summary": (content.get("summary", "") or "")[:200],
                    "publisher": content.get("provider", {}).get("displayName", ""),
                    "date": content.get("pubDate", ""),
                    "url": url,
                    "thumbnail": thumb_url,
                    "ticker": tag,
                    "asset_label": label,
                }
                by_ticker[tag].append(article)
        except Exception:
            continue

    _cache["data"] = by_ticker
    _cache["ts"] = now
    return by_ticker


@router.get("/news")
def get_news(shuffle: bool = Query(False)):
    """Returns a balanced mix of news across all tickers (max 12 articles)."""
    by_ticker = _fetch_all_articles()

    # round-robin pick so each ticker gets equal representation
    balanced: list[dict] = []
    max_per_ticker = 3
    for tag in TICKERS:
        tag_clean = tag.replace("-USD", "")
        pool = by_ticker.get(tag_clean, [])
        if shuffle:
            pool = list(pool)
            random.shuffle(pool)
        balanced.extend(pool[:max_per_ticker])

    # sort by date unless shuffle was requested
    if shuffle:
        random.shuffle(balanced)
    else:
        balanced.sort(key=lambda x: x.get("date", ""), reverse=True)

    return {"articles": balanced[:12], "fetched_at": datetime.now().isoformat()}
