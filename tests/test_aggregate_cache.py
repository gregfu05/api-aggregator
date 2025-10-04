def test_aggregate_crypto_and_stock_cache_hit_miss(client):
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
