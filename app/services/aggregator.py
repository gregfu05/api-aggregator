
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, List

from app.adapters.coingecko import fetch_simple_price
from app.adapters.alphavantage import fetch_quote
from app.services.cache_service import get_cache, set_cache


def _classify(symbol: str) -> str:
    """
    Very simple heuristic:
    - if it's ALL UPPERCASE -> treat as stock ticker
    - else -> treat as crypto (CoinGecko id)
    """
    return "stock" if symbol and symbol.upper() == symbol else "crypto"


def _normalize_symbols(csv: str) -> List[str]:
    return [s.strip() for s in csv.split(",") if s.strip()]


def aggregate_with_cache(symbols_csv: str, window: int = 60) -> Dict:
    """
    Unified aggregator used by BOTH the API and the UI.
    - Checks Mongo cache first (TTL).
    - On miss, fetches live data, writes cache, returns payload.
    - Adds meta.cache = "hit" | "miss".
    """
    now = datetime.now(timezone.utc)
    symbols = _normalize_symbols(symbols_csv)
    cache_key = f"agg::{','.join(symbols)}"

    # 1) Try cache
    cached_doc = get_cache(cache_key)
    if cached_doc:
        payload = cached_doc.get("payload") or cached_doc  # tolerate either shape
        # Ensure meta.cache is visible to the UI
        payload.setdefault("meta", {})
        payload["meta"]["cache"] = "hit"
        return payload

    # 2) Miss -> fetch live
    assets: List[Dict] = []

    # crypto chunk (CoinGecko expects ids lowercased by design)
    crypto_ids = [s for s in symbols if _classify(s) == "crypto"]
    if crypto_ids:
        price_map = fetch_simple_price(crypto_ids, ["usd"])  # { "bitcoin": {"usd": 12345.0}, ... }
        for cid in crypto_ids:
            usd = price_map.get(cid, {}).get("usd")
            if usd is None:
                continue
            assets.append({
                "symbol": cid,
                "type": "crypto",
                "price": float(usd),
                "source": "coingecko",
                "asOf": now.isoformat(),
            })

    # stock chunk (Alpha Vantage)
    stock_syms = [s for s in symbols if _classify(s) == "stock"]
    for sym in stock_syms:
        q = fetch_quote(sym)  # returns the "Global Quote" dict fields
        price = (
            q.get("05. price")
            or q.get("05. Price")
            or q.get("price")
            or q.get("05_price")
            or 0
        )
        try:
            price = float(price)
        except Exception:
            price = 0.0
        as_of = q.get("07. latest trading day") or q.get("07_latest_trading_day")
        assets.append({
            "symbol": sym,
            "type": "stock",
            "price": price,
            "source": "alphavantage",
            "asOf": as_of or now.date().isoformat(),
        })

    payload = {
        "timestamp": now.isoformat(),
        "assets": assets,
        "meta": {
            "cache": "miss",
            "sources": [{"name": "coingecko"}, {"name": "alphavantage"}],
            "warnings": [],
        },
    }

    # 3) Write to cache with TTL window (seconds)
    ttl_seconds = max(15, int(window))  # small safety floor
    set_cache(cache_key, payload, ttl_seconds)

    return payload
