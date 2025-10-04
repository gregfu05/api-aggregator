
import os
import time
from datetime import datetime, timezone
from typing import List, Dict

import requests

BASE = "https://www.alphavantage.co/query"
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")


class AlphaVantageError(Exception):
    pass


# ---- Realtime quote (used by /aggregate and stocks UI) ----
def fetch_quote(symbol: str) -> Dict:
    """
    GLOBAL_QUOTE -> returns dict for the symbol, tolerant to slight schema changes.
    """
    if not API_KEY:
        raise AlphaVantageError("Missing ALPHAVANTAGE_API_KEY in environment.")

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    r = requests.get(BASE, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    # Alpha Vantage may return "Note" on rate-limit
    if data.get("Note"):
        raise AlphaVantageError("Alpha Vantage rate limit hit. Try again in a minute.")

    quote = data.get("Global Quote") or data.get("GlobalQuote") or {}
    if not quote:
        # Sometimes they send "Information" or "Error Message"
        info = data.get("Information") or data.get("Error Message")
        if info:
            raise AlphaVantageError(info)
    return quote


# ---- Daily history (last 30 points) for charts ----
_daily_cache: Dict[str, Dict] = {}  # {symbol: {"ts": epoch, "data": [{t,y}, ...]}}


def _pick_series_block(data: dict):
    """Return the first available daily series block from the payload."""
    return (
        data.get("Time Series (Daily) Adjusted")
        or data.get("Time Series (Daily)")
        or data.get("Time Series (Digital Currency Daily)")
        or None
    )


def fetch_daily_series(symbol: str, compact: bool = True):
    """
    Returns list of points: [{t: unix_ms, y: close}], ascending, last ~30 pts.
    Handles Adjusted/Daily, rate limits, and caches for 60s.
    """
    if not API_KEY:
        raise AlphaVantageError("Missing ALPHAVANTAGE_API_KEY in environment.")

    key = symbol.upper()
    now = time.time()
    cached = _daily_cache.get(key)
    if cached and now - cached["ts"] < 60:
        return cached["data"]

    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": key,
        "outputsize": "compact" if compact else "full",
        "apikey": API_KEY,
    }
    r = requests.get(BASE, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    # Rate-limit?
    if data.get("Note"):
        raise AlphaVantageError("Alpha Vantage rate limit hit. Try again in a minute.")

    # Fallback to non-adjusted if needed
    if not _pick_series_block(data) and (data.get("Information") or data.get("Error Message")):
        params["function"] = "TIME_SERIES_DAILY"
        r2 = requests.get(BASE, params=params, timeout=15)
        r2.raise_for_status()
        data = r2.json()
        if data.get("Note"):
            raise AlphaVantageError("Alpha Vantage rate limit hit. Try again in a minute.")

    series = _pick_series_block(data)
    if not series:
        raise AlphaVantageError(f"No daily series for {key}")

    points = []
    for date_str, row in series.items():
        price_str = (
            row.get("5. adjusted close")
            or row.get("4. close")
            or row.get("5. close")
        )
        if not price_str:
            continue
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        points.append({"t": int(dt.timestamp() * 1000), "y": float(price_str)})

    points.sort(key=lambda p: p["t"])
    points = points[-30:]  # last ~30 days

    _daily_cache[key] = {"ts": now, "data": points}
    return points


# ---- Symbol search (typeahead) ----
def symbol_search(q: str) -> List[Dict]:
    if not API_KEY:
        raise AlphaVantageError("Missing ALPHAVANTAGE_API_KEY in environment.")
    params = {"function": "SYMBOL_SEARCH", "keywords": q, "apikey": API_KEY}
    r = requests.get(BASE, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    best = data.get("bestMatches") or []
    # normalize a tiny bit
    out = []
    for m in best:
        out.append({
            "symbol": m.get("1. symbol") or "",
            "name": m.get("2. name") or "",
            "region": m.get("4. region") or "",
            "currency": m.get("8. currency") or "",
        })
    return out


