
from fastapi import APIRouter, Query, HTTPException
from app.services.aggregator import aggregate_with_cache

router = APIRouter()

@router.get("/aggregate")
def aggregate_endpoint(
    symbols: str = Query(..., description="CSV of symbols, e.g. bitcoin,AAPL"),
    window: int = Query(60, description="Cache TTL seconds"),
):
    try:
        return aggregate_with_cache(symbols, window=window)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
