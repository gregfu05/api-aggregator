import os
from datetime import timezone
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "aggregator")

_client = None
_db = None

def get_client() -> MongoClient:
    global _client
    if _client is None:
        # Make datetimes timezone-aware when read from Mongo
        _client = MongoClient(MONGODB_URI, tz_aware=True, tzinfo=timezone.utc)
    return _client

def get_db():
    global _db
    if _db is None:
        _db = get_client()[MONGODB_DB]
    return _db
