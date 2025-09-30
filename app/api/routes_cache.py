from fastapi import APIRouter, Body, HTTPException
from typing import List, Optional
from app.db.mongo import get_db

router = APIRouter()

@router.get("/cache/status")
def cache_status(sample: int = 5):
    db = get_db()
    count = db.cache.count_documents({})
    keys = []
    for doc in db.cache.find({}, {"_id": 0, "key": 1}).limit(max(sample, 0)):
        keys.append(doc["key"])
    return {
        "count": count,
        "keysSample": keys,
        "ttlDefaultNote": "TTL is set on expiresAt via index; entries auto-expire."
    }

@router.post("/cache/clear")
def cache_clear(
    all: Optional[bool] = Body(default=False),
    keys: Optional[List[str]] = Body(default=None),
):
    db = get_db()

    if all:
        res = db.cache.delete_many({})
        return {"cleared": res.deleted_count, "mode": "all"}

    if keys:
        res = db.cache.delete_many({"key": {"$in": keys}})
        return {"cleared": res.deleted_count, "mode": "keys", "keys": keys}

    raise HTTPException(status_code=400, detail="Provide 'all': true or a 'keys' list.")
