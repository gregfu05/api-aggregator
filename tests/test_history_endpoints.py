def test_history_crypto(client):
    r = client.get("/history/crypto", params={"id": "bitcoin", "days": 30})
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "bitcoin"
    assert isinstance(data["series"], list)
    assert len(data["series"]) == 30

def test_history_stock(client):
    r = client.get("/history/stock", params={"symbol": "AAPL"})
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "AAPL"
    assert isinstance(data["series"], list)
    assert len(data["series"]) == 30