def test_get_assets_empty(client):
    """Test GET /assets returns empty list initially."""
    # Clear the assets collection
    from app.db.mongo import get_db
    db = get_db()
    db.assets.delete_many({})
    
    r = client.get("/assets")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_post_asset_crypto(client):
    """Test POST /assets to create a crypto asset."""
    from app.db.mongo import get_db
    db = get_db()
    db.assets.delete_many({})
    
    payload = {"symbol": "BTC", "type": "crypto", "name": "Bitcoin"}
    r = client.post("/assets", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "BTC"
    assert data["type"] == "crypto"
    assert data["name"] == "Bitcoin"
    assert data["active"] is True
    assert "addedAt" in data
    assert "updatedAt" in data


def test_post_asset_stock(client):
    """Test POST /assets to create a stock asset."""
    from app.db.mongo import get_db
    db = get_db()
    db.assets.delete_many({})
    
    payload = {"symbol": "AAPL", "type": "stock", "name": "Apple Inc."}
    r = client.post("/assets", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "AAPL"
    assert data["type"] == "stock"
    assert data["name"] == "Apple Inc."


def test_post_asset_invalid_type(client):
    """Test POST /assets with invalid type."""
    payload = {"symbol": "XYZ", "type": "invalid"}
    r = client.post("/assets", json=payload)
    assert r.status_code == 400
    assert "must be 'crypto' or 'stock'" in r.json()["detail"]


def test_post_asset_uppercase_type(client):
    """Test POST /assets normalizes type to lowercase."""
    from app.db.mongo import get_db
    db = get_db()
    db.assets.delete_many({})
    
    payload = {"symbol": "ETH", "type": "CRYPTO"}
    r = client.post("/assets", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "crypto"  # Should be lowercased


def test_put_asset_success(client):
    """Test PUT /assets to update an existing asset."""
    from app.db.mongo import get_db
    db = get_db()
    db.assets.delete_many({})
    
    # First create an asset
    payload = {"symbol": "BTC", "type": "crypto", "name": "Bitcoin"}
    client.post("/assets", json=payload)
    
    # Now update it
    update_payload = {"symbol": "BTC", "updates": {"name": "Bitcoin Updated", "active": False}}
    r = client.put("/assets", json=update_payload)
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "BTC"
    assert data["name"] == "Bitcoin Updated"
    assert data["active"] is False


def test_put_asset_not_found(client):
    """Test PUT /assets for non-existent asset."""
    from app.db.mongo import get_db
    db = get_db()
    db.assets.delete_many({})
    
    update_payload = {"symbol": "NONEXISTENT", "updates": {"name": "Test"}}
    r = client.put("/assets", json=update_payload)
    assert r.status_code == 404
    assert "asset not found" in r.json()["detail"]


def test_put_asset_empty_updates(client):
    """Test PUT /assets with no updates provided."""
    update_payload = {"symbol": "BTC", "updates": {}}
    r = client.put("/assets", json=update_payload)
    assert r.status_code == 400
    assert "no updates provided" in r.json()["detail"]


def test_delete_asset_success(client):
    """Test DELETE /assets to remove an asset."""
    from app.db.mongo import get_db
    db = get_db()
    db.assets.delete_many({})
    
    # First create an asset
    payload = {"symbol": "BTC", "type": "crypto", "name": "Bitcoin"}
    client.post("/assets", json=payload)
    
    # Now delete it
    r = client.delete("/assets", params={"symbol": "BTC"})
    assert r.status_code == 200
    data = r.json()
    assert data["deleted"] == 1


def test_delete_asset_not_found(client):
    """Test DELETE /assets for non-existent asset."""
    from app.db.mongo import get_db
    db = get_db()
    db.assets.delete_many({})
    
    r = client.delete("/assets", params={"symbol": "NONEXISTENT"})
    assert r.status_code == 404
    assert "asset not found" in r.json()["detail"]


def test_get_assets_after_creating(client):
    """Test GET /assets returns created assets."""
    from app.db.mongo import get_db
    db = get_db()
    db.assets.delete_many({})
    
    # Create multiple assets
    client.post("/assets", json={"symbol": "BTC", "type": "crypto", "name": "Bitcoin"})
    client.post("/assets", json={"symbol": "ETH", "type": "crypto", "name": "Ethereum"})
    client.post("/assets", json={"symbol": "AAPL", "type": "stock", "name": "Apple"})
    
    r = client.get("/assets")
    assert r.status_code == 200
    assets = r.json()
    assert len(assets) == 3
    symbols = {a["symbol"] for a in assets}
    assert "BTC" in symbols
    assert "ETH" in symbols
    assert "AAPL" in symbols
