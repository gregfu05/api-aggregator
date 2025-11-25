def test_crypto_price_single(client):
    r = client.get("/crypto/price", params={"ids": "bitcoin", "vs": "usd"})
    assert r.status_code == 200
    data = r.json()
    assert data["ids"] == "bitcoin"
    assert data["vs"] == "usd"
    assert "data" in data
    assert "bitcoin" in data["data"]
    assert "usd" in data["data"]["bitcoin"]
    assert isinstance(data["data"]["bitcoin"]["usd"], float)

def test_crypto_price_multiple(client):
    """Test with multiple cryptocurrencies."""
    r = client.get("/crypto/price", params={"ids": "bitcoin,ethereum", "vs": "usd"})
    assert r.status_code == 200
    data = r.json()
    assert data["ids"] == "bitcoin,ethereum"
    assert "bitcoin" in data["data"]
    assert "ethereum" in data["data"]

def test_crypto_price_invalid_input(client):
    # Test missing required parameter
    r = client.get("/crypto/price")
    assert r.status_code == 422  # FastAPI validation error
