import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


import os
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

# Ensure env is set for imports that expect a key
os.environ.setdefault("ALPHAVANTAGE_API_KEY", "DUMMY_FOR_TESTS")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB", "aggregator_test")

# Module-level fake database storage (reset per fixture)
_FAKE_DB_STORAGE = {
    "cache": [],
    "req_logs": [],
    "assets": []
}

# In-memory cache (reset per test via client fixture)
_MEM_CACHE = {}

# Define fake adapter functions at module level
def _fake_fetch_simple_price(ids, vs):
    data = {}
    for i in ids:
        if i == "bitcoin":
            data[i] = {"usd": 30000.0}
        elif i == "ethereum":
            data[i] = {"usd": 2000.0}
        else:
            data[i] = {"usd": 1.23}
    return data

def _fake_fetch_quote(symbol):
    up = symbol.upper()
    if up == "AAPL":
        return {"05. price": "190.50", "07. latest trading day": "2025-09-30"}
    if up == "MSFT":
        return {"05. price": "410.00", "07. latest trading day": "2025-09-30"}
    return {"05. price": "10.00", "07. latest trading day": "2025-09-30"}

def _series_30(base=100.0):
    out = []
    today = datetime.now(timezone.utc).date()
    for d in range(30, 0, -1):
        dt = datetime.combine(today - timedelta(days=d), datetime.min.time(), tzinfo=timezone.utc)
        out.append({"t": int(dt.timestamp() * 1000), "y": base + (30 - d)})
    return out

def _fake_fetch_market_chart(coin_id, days=30, vs="usd"):
    base = 30000.0 if coin_id == "bitcoin" else 2000.0
    return _series_30(base=base)

def _fake_fetch_daily_series(symbol, compact=True):
    base = 190.0 if symbol.upper() == "AAPL" else 410.0
    return _series_30(base=base)

def _fake_get_cache(key: str):
    """Fake cache using in-memory dict. Returns entry even if expired (like real MongoDB)."""
    return _MEM_CACHE.get(key)

def _fake_set_cache(key: str, payload, ttl_seconds: int = 60):
    """Fake cache using in-memory dict."""
    _MEM_CACHE[key] = {
        "key": key,
        "payload": payload,
        "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
    }

def pytest_configure(config):
    """Patch adapters and cache BEFORE test collection/imports."""
    import app.adapters.coingecko as cg
    import app.adapters.alphavantage as av
    import app.services.cache_service as cache_svc
    
    # Patch adapters
    cg.fetch_simple_price = _fake_fetch_simple_price
    cg.fetch_market_chart = _fake_fetch_market_chart
    av.fetch_quote = _fake_fetch_quote
    av.fetch_daily_series = _fake_fetch_daily_series
    
    # Patch cache service
    cache_svc.get_cache = _fake_get_cache
    cache_svc.set_cache = _fake_set_cache

@pytest.fixture(autouse=True, scope="function")
def reset_fakes():
    """Reset cache and database storage before each test."""
    # Reset cache
    global _MEM_CACHE
    _MEM_CACHE.clear()
    
    # Reset database storage
    global _FAKE_DB_STORAGE
    _FAKE_DB_STORAGE = {
        "cache": [],
        "req_logs": [],
        "assets": []
    }

@pytest.fixture(autouse=True)
def mock_database(monkeypatch):
    """Auto-patch get_db for ALL tests, whether they use client or not."""
    # Note: Database storage is already reset by reset_fakes fixture
    
    class FakeCollection:
        def __init__(self, name):
            self.name = name

        @property
        def _data(self):
            return _FAKE_DB_STORAGE[self.name]

        def count_documents(self, query=None):
            """Count documents matching the query."""
            if not query:
                return len(self._data)
            count = 0
            for doc in self._data:
                if self._matches(doc, query):
                    count += 1
            return count

        def find_one(self, query, projection=None):
            for doc in self._data:
                if self._matches(doc, query):
                    return self._apply_projection(doc.copy(), projection)
            return None

        def find(self, query=None, projection=None):
            query = query or {}
            results = [self._apply_projection(doc.copy(), projection) 
                      for doc in self._data if self._matches(doc, query)]
            return FakeCursor(results)

        def insert_one(self, doc):
            doc_copy = doc.copy()
            doc_copy["_id"] = f"fake_id_{len(self._data)}"
            self._data.append(doc_copy)
            return type('Result', (), {'inserted_id': doc_copy["_id"]})()

        def update_one(self, query, update, upsert=False):
            for doc in self._data:
                if self._matches(doc, query):
                    if "$set" in update:
                        doc.update(update["$set"])
                    if "$setOnInsert" in update and upsert:
                        pass
                    return type('Result', (), {'matched_count': 1, 'modified_count': 1})()
            
            if upsert:
                new_doc = {}
                if "$setOnInsert" in update:
                    new_doc.update(update["$setOnInsert"])
                if "$set" in update:
                    new_doc.update(update["$set"])
                new_doc["_id"] = f"fake_id_{len(self._data)}"
                self._data.append(new_doc)
                return type('Result', (), {'matched_count': 0, 'modified_count': 0, 'upserted_id': new_doc["_id"]})()
            
            return type('Result', (), {'matched_count': 0, 'modified_count': 0})()

        def delete_one(self, query):
            for i, doc in enumerate(self._data):
                if self._matches(doc, query):
                    self._data.pop(i)
                    return type('Result', (), {'deleted_count': 1})()
            return type('Result', (), {'deleted_count': 0})()

        def delete_many(self, query):
            to_remove = [i for i, doc in enumerate(self._data) if self._matches(doc, query)]
            for i in reversed(to_remove):
                self._data.pop(i)
            return type('Result', (), {'deleted_count': len(to_remove)})()

        def _matches(self, doc, query):
            if not query:
                return True
            for key, value in query.items():
                # Handle $in operator
                if isinstance(value, dict) and "$in" in value:
                    if key not in doc or doc[key] not in value["$in"]:
                        return False
                elif key not in doc or doc[key] != value:
                    return False
            return True

        def _apply_projection(self, doc, projection):
            if not projection:
                return doc
            if projection.get("_id") == 0:
                doc.pop("_id", None)
            return doc

    class FakeCursor:
        def __init__(self, data):
            self._data = list(data)
            self._sort_key = None
            self._sort_direction = -1

        def sort(self, key, direction=-1):
            self._sort_key = key
            self._sort_direction = direction
            return self

        def limit(self, count):
            results = self._get_results()
            self._data = results[:count]
            self._sort_key = None
            return self

        def _get_results(self):
            if self._sort_key:
                reverse = (self._sort_direction == -1)
                def sort_fn(x):
                    val = x.get(self._sort_key)
                    if val is None:
                        return datetime.min if isinstance(val, datetime) else ""
                    return val
                return sorted(self._data, key=sort_fn, reverse=reverse)
            return self._data

        def __iter__(self):
            return iter(self._get_results())

    class FakeDB:
        def __init__(self):
            self.cache = FakeCollection("cache")
            self.req_logs = FakeCollection("req_logs")
            self.assets = FakeCollection("assets")

    def fake_get_db():
        return FakeDB()

    import app.db.mongo as mongo_module
    monkeypatch.setattr(mongo_module, "get_db", fake_get_db, raising=True)


@pytest.fixture
def client():
    """FastAPI TestClient with mocked external dependencies."""
    # Note: All patches are applied at pytest_configure time
    from app.main import app
    return TestClient(app)
