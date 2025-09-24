from datetime import datetime, timedelta, timezone
import hashlib
from typing import Optional, Dict, Any

from app.db.mongo import get_db

def _now_utc():
    return datetime.now(timezone.utc)

def make_cache_key(symbols_csv: str, ttl_seconds: int) -> str:
    # normalize symbols (sorted, lowercase for crypto, keep case for stocks)
    parts = [s.strip() for s in symbols_csv.split(",") if s.strip()]
    # keep original tokens but sort for idempotence
    key_norm = ",".join(sorted(parts))
    raw = f"AGG:v1|symbols={key_norm}|ttl={ttl_seconds}"
    # hash to keep key length safe
    key_hash = hashlib.sha256(raw.encode()).hexdigest()[:24]
    return f"{raw}|h={key_hash}"

def get_cached(key: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    doc = db.cache.find_one({"key": key})
    if not doc:
        return None
    # if document exists but expired (just in case TTL hasn’t cleaned it yet)
    if doc.get("expiresAt") and doc["expiresAt"] <= _now_utc():
        return None
    return doc

def set_cached(key: str, data: Dict[str, Any], ttl_seconds: int) -> None:
    db = get_db()
    created = _now_utc()
    expires = created + timedelta(seconds=ttl_seconds)
    db.cache.update_one(
        {"key": key},
        {
            "$set": {
                "key": key,
                "data": data,
                "createdAt": created,
                "expiresAt": expires,
            }
        },
        upsert=True,
    )

