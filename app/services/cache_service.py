from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from app.db.mongo import get_db  # must return a synchronous pymongo.Database


def get_cache(key: str) -> Optional[Dict[str, Any]]:
    """
    Return the cached document for `key` (if present and not yet TTL-purged).
    Shape:
      { "key": str, "payload": {...}, "expiresAt": datetime }
    """
    db = get_db()
    doc = db.cache.find_one({"key": key})
    if not doc:
        return None
    doc.pop("_id", None)
    return doc


def set_cache(key: str, payload: Dict[str, Any], ttl_seconds: int = 60) -> None:
    """
    Upsert a cache entry with TTL. The TTL index on `expiresAt` should exist
    (created by scripts/init_db.py). We update/insert:
      - key
      - payload
      - expiresAt = now + ttl_seconds (UTC)
    """
    db = get_db()
    expires = datetime.now(timezone.utc) + timedelta(seconds=int(ttl_seconds))
    db.cache.update_one(
        {"key": key},
        {"$set": {"key": key, "payload": payload, "expiresAt": expires}},
        upsert=True,
    )