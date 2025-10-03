from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

from app.adapters.coingecko import fetch_simple_price
from app.adapters.alphavantage import fetch_global_quote, AlphaVantageError

def classify_symbols(symbols: List[str]) -> Tuple[List[str], List[str]]:
    """
    Naive split:
    - STOCK if it looks like AAPL, MSFT (all caps, letters/dots, len <= 6)
    - otherwise CRYPTO (e.g., bitcoin, ethereum)
    """
    stocks, cryptos = [], []
    for s in symbols:
        s_clean = s.strip()
        if s_clean.isupper() and 1 <= len(s_clean) <= 6 and s_clean.replace(".", "").isalpha():
            stocks.append(s_clean)
        else:
            cryptos.append(s_clean.lower())
    return stocks, cryptos

def aggregate(symbols_csv: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    symbols = [s for s in symbols_csv.split(",") if s.strip()]
    if not symbols:
        return {"timestamp": now, "assets": [], "meta": {"warnings": ["no symbols provided"]}}

    stocks, cryptos = classify_symbols(symbols)

    assets: List[Dict[str, Any]] = []
    warnings: List[str] = []
    sources_meta: List[Dict[str, Any]] = []

    # ---- Crypto batch via CoinGecko ----
    if cryptos:
        try:
            cg = fetch_simple_price(cryptos, ["usd"])
            for cid in cryptos:
                price = cg.get(cid, {}).get("usd")
                if price is None:
                    warnings.append(f"no crypto price for '{cid}'")
                    continue
                assets.append({
                    "symbol": cid,
                    "type": "crypto",
                    "price": float(price),
                    "source": "coingecko",
                    "asOf": now
                })
            sources_meta.append({"name": "coingecko", "count": len(cryptos)})
        except Exception as e:
            warnings.append(f"coingecko error: {e}")

    # ---- Stocks from Alpha Vantage one-by-one ----
    for sym in stocks:
        try:
            gq = fetch_global_quote(sym)
            price_str = gq.get("05. price")
            day = gq.get("07. latest trading day")
            if price_str is None:
                warnings.append(f"no stock price for '{sym}'")
                continue
            assets.append({
                "symbol": sym,
                "type": "stock",
                "price": float(price_str),
                "source": "alphavantage",
                "asOf": f"{day}T00:00:00Z" if day else now
            })
        except AlphaVantageError as e:
            warnings.append(f"{sym}: {e}")
        except Exception as e:
            warnings.append(f"{sym}: upstream error: {e}")

    return {
        "timestamp": now,
        "assets": assets,
        "meta": {
            "cache": "n/a",
            "sources": sources_meta,
            "warnings": warnings
        }
    }
