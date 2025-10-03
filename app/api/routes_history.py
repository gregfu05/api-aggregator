from fastapi import APIRouter, Query, HTTPException
from app.adapters.coingecko import fetch_market_chart
from app.adapters.alphavantage import fetch_daily_series, AlphaVantageError

router = APIRouter()

@router.get("/history/crypto")
def crypto_history(id: str = Query(..., description="coingecko id, e.g. bitcoin"), days: int = 30):
    try:
        series = fetch_market_chart(id, days=days, vs="usd")
        return {"symbol": id, "series": series, "currency": "usd"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/history/stock")
def stock_history(symbol: str = Query(..., description="ticker, e.g. AAPL")):
    try:
        series = fetch_daily_series(symbol)
        return {"symbol": symbol.upper(), "series": series, "currency": "usd"}
    except AlphaVantageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
