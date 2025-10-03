from fastapi import APIRouter, Query, HTTPException
from app.adapters.alphavantage import fetch_quote as fetch_global_quote, AlphaVantageError


router = APIRouter()

@router.get("/stocks/quote")
def stocks_quote(symbol: str = Query(..., min_length=1)):
    try:
        quote = fetch_global_quote(symbol.upper())
        return {"symbol": symbol.upper(), "data": quote}
    except AlphaVantageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
