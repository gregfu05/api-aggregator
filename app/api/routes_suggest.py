from fastapi import APIRouter, Query, HTTPException
from app.adapters.coingecko import suggest_crypto
import os, requests

router = APIRouter()

@router.get("/suggest/crypto")
def suggest_crypto_route(q: str = Query(..., min_length=1), limit: int = 10):
    return suggest_crypto(q, limit=limit)

@router.get("/suggest/stocks")
def suggest_stocks_route(q: str = Query(..., min_length=1), limit: int = 10):
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Alpha Vantage API key missing")
    url = "https://www.alphavantage.co/query"
    params = {"function": "SYMBOL_SEARCH", "keywords": q, "apikey": api_key}
    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        data = r.json().get("bestMatches", [])
        out = []
        for m in data:
            out.append({
                "symbol": m.get("1. symbol"),
                "name": m.get("2. name"),
                "type": m.get("3. type"),
                "region": m.get("4. region")
            })
            if len(out) >= limit:
                break
        return out
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
