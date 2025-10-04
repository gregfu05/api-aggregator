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

@pytest.fixture
def client(monkeypatch):
    """FastAPI TestClient with external calls + cache replaced by fakes."""

    # ---- Fake adapters ----
    def fake_fetch_simple_price(ids, vs):
        data = {}
        for i in ids:
            if i == "bitcoin":
                data[i] = {"usd": 30000.0}
            elif i == "ethereum":
                data[i] = {"usd": 2000.0}
            else:
                data[i] = {"usd": 1.23}
        return data

    def fake_fetch_quote(symbol):
        up = symbol.upper()
        if up == "AAPL":
            return {"05. price": "190.50", "07. latest trading day": "2025-09-30"}
        if up == "MSFT":
            return {"05. price": "410.00", "07. latest trading day": "2025-09-30"}
        return {"05. price": "10.00", "07. latest trading day": "2025-09-30"}

    # History: 30 daily points ending today
    def _series_30(base=100.0):
        out = []
        today = datetime.now(timezone.utc).date()
        for d in range(30, 0, -1):
            dt = datetime.combine(today - timedelta(days=d), datetime.min.time(), tzinfo=timezone.utc)
            out.append({"t": int(dt.timestamp() * 1000), "y": base + (30 - d)})
        return out

    def fake_fetch_market_chart(coin_id, days=30, vs="usd"):
        base = 30000.0 if coin_id == "bitcoin" else 2000.0
        return _series_30(base=base)

    def fake_fetch_daily_series(symbol, compact=True):
        base = 190.0 if symbol.upper() == "AAPL" else 410.0
        return _series_30(base=base)

    # ---- In-memory cache to simulate Mongo cache ----
    _mem = {}

    def fake_get_cache(key: str):
        entry = _mem.get(key)
        if not entry:
            return None
        if entry["expiresAt"] <= datetime.now(timezone.utc):
            return None
        return entry

    def fake_set_cache(key: str, payload, ttl_seconds: int = 60):
        _mem[key] = {
            "key": key,
            "payload": payload,
            "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
        }

    # Apply monkeypatches (import modules directly)
    import app.adapters.coingecko as cg
    import app.adapters.alphavantage as av
    monkeypatch.setattr(cg, "fetch_simple_price", fake_fetch_simple_price, raising=True)
    monkeypatch.setattr(cg, "fetch_market_chart", fake_fetch_market_chart, raising=True)
    monkeypatch.setattr(av, "fetch_quote", fake_fetch_quote, raising=True)
    monkeypatch.setattr(av, "fetch_daily_series", fake_fetch_daily_series, raising=True)

    from app.services import cache_service
    monkeypatch.setattr(cache_service, "get_cache", fake_get_cache, raising=True)
    monkeypatch.setattr(cache_service, "set_cache", fake_set_cache, raising=True)

    # Import app AFTER patches so routes use the fakes
    from app.main import app
    return TestClient(app)
