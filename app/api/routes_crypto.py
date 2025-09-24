from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.adapters.coingecko import fetch_simple_price

router = APIRouter()

@router.get("/crypto/price")
def crypto_price(ids: str = Query(...), vs: str = Query("usd")):
    try:
        data = fetch_simple_price(ids.split(","), vs.split(","))
        return {"ids": ids, "vs": vs, "data": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
