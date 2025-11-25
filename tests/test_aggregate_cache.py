def test_aggregate_crypto_and_stock_cache_hit_miss(client):
    # Clear any existing cache for this test
    from app.db.mongo import get_db
    db = get_db()
    db.cache.delete_many({})  # Clear cache collection
    
    url = "/aggregate?symbols=bitcoin,AAPL&window=120"

    # First call -> miss
    r1 = client.get(url)
    assert r1.status_code == 200
    body1 = r1.json()
    assert body1["meta"]["cache"] == "miss"
    # sanity checks
    syms = {a["symbol"] for a in body1["assets"]}
    assert "bitcoin" in syms and "AAPL" in syms

    # Second call (same params) -> hit
    r2 = client.get(url)
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["meta"]["cache"] == "hit"
    # assets should still be there
    syms2 = {a["symbol"] for a in body2["assets"]}
    assert syms2 == syms


def test_aggregate_missing_symbols_param(client):
    """Test /aggregate endpoint without required symbols parameter."""
    r = client.get("/aggregate")
    assert r.status_code == 422  # FastAPI validation error
