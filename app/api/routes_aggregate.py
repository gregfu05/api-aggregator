from fastapi import APIRouter, Query, HTTPException
from app.services.aggregator import aggregate as do_aggregate
from app.services.cache_service import make_cache_key, get_cached, set_cached

router = APIRouter()

@router.get("/aggregate")
def aggregate_endpoint(
    symbols: str = Query(..., description="CSV of symbols, e.g. bitcoin,AAPL"),
    window: int = Query(60, ge=5, le=3600, description="Cache TTL seconds"),
):
    try:
        key = make_cache_key(symbols, window)
        hit = get_cached(key)
        if hit:
            data = hit["data"]
            if "meta" in data:
                data["meta"]["cache"] = "hit"
            else:
                data["meta"] = {"cache": "hit"}
            return data

        data = do_aggregate(symbols)
        if "meta" in data:
            data["meta"]["cache"] = "miss"
        else:
            data["meta"] = {"cache": "miss"}

        set_cached(key, data, window)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
