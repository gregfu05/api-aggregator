def test_stock_quote_success(client):
    r = client.get("/stocks/quote", params={"symbol": "AAPL"})
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "AAPL"
    assert "data" in data
    assert "05. price" in data["data"]
    assert "07. latest trading day" in data["data"]
    assert data["data"]["05. price"] == "190.50"
    assert data["data"]["07. latest trading day"] == "2025-09-30"

def test_stock_quote_different_symbol(client):
    """Test with a different stock symbol."""
    r = client.get("/stocks/quote", params={"symbol": "MSFT"})
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "MSFT"
    assert "data" in data
    assert "05. price" in data["data"]

def test_stock_quote_lowercase_symbol(client):
    """Test that lowercase symbols are converted to uppercase."""
    r = client.get("/stocks/quote", params={"symbol": "aapl"})
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "AAPL"  # Should be uppercased

def test_stock_quote_missing_symbol(client):
    # Test missing required parameter
    r = client.get("/stocks/quote")
    assert r.status_code == 422  # FastAPI validation error
