def test_history_crypto(client):
    r = client.get("/history/crypto", params={"id": "bitcoin", "days": 30})
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "bitcoin"
    assert isinstance(data["series"], list)
    assert len(data["series"]) == 30

def test_history_crypto_default_days(client):
    """Test history/crypto with default days parameter."""
    r = client.get("/history/crypto", params={"id": "ethereum"})
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "ethereum"
    assert isinstance(data["series"], list)

def test_history_stock(client):
    r = client.get("/history/stock", params={"symbol": "AAPL"})
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "AAPL"
    assert isinstance(data["series"], list)
    assert len(data["series"]) == 30

def test_history_stock_different_symbol(client):
    """Test history/stock with different stock symbol."""
    r = client.get("/history/stock", params={"symbol": "MSFT"})
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "MSFT"
    assert isinstance(data["series"], list)