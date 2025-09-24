from fastapi import APIRouter, Query, HTTPException
from app.services.aggregator import aggregate

router = APIRouter()

@router.get("/aggregate")
def aggregate_endpoint(symbols: str = Query(..., description="CSV of symbols, e.g. bitcoin,AAPL")):
    try:
        return aggregate(symbols)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
