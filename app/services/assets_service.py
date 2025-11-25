from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from app.db.mongo import get_db

def list_assets() -> List[Dict[str, Any]]:
    db = get_db()
    return list(db.assets.find({}, {"_id": 0}).sort("addedAt", -1))

def add_asset(symbol: str, type_: str, name: Optional[str] = None) -> Dict[str, Any]:
    db = get_db()
    doc = {
        "symbol": symbol.strip(),
        "type": type_.strip().lower(),  # "crypto" or "stock"
        "name": name,
        "active": True,
        "addedAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    db.assets.update_one({"symbol": doc["symbol"]}, {"$setOnInsert": doc}, upsert=True)
    return db.assets.find_one({"symbol": doc["symbol"]}, {"_id": 0})

def update_asset(symbol: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db()
    updates["updatedAt"] = datetime.now(timezone.utc)
    db.assets.update_one({"symbol": symbol}, {"$set": updates})
    return db.assets.find_one({"symbol": symbol}, {"_id": 0})

def delete_asset(symbol: str) -> int:
    db = get_db()
    res = db.assets.delete_one({"symbol": symbol})
    return res.deleted_count

