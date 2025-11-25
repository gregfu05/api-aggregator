from datetime import datetime, timezone


def test_list_assets_empty():
    """Test list_assets returns empty list when no assets exist."""
    from app.db.mongo import get_db
    from app.services.assets_service import list_assets
    
    db = get_db()
    db.assets.delete_many({})
    
    result = list_assets()
    assert isinstance(result, list)
    assert len(result) == 0


def test_add_asset_crypto():
    """Test add_asset creates a crypto asset properly."""
    from app.db.mongo import get_db
    from app.services.assets_service import add_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    result = add_asset("BTC", "crypto", "Bitcoin")
    
    assert result["symbol"] == "BTC"
    assert result["type"] == "crypto"
    assert result["name"] == "Bitcoin"
    assert result["active"] is True
    assert "addedAt" in result
    assert "updatedAt" in result


def test_add_asset_stock():
    """Test add_asset creates a stock asset properly."""
    from app.db.mongo import get_db
    from app.services.assets_service import add_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    result = add_asset("AAPL", "stock", "Apple Inc.")
    
    assert result["symbol"] == "AAPL"
    assert result["type"] == "stock"
    assert result["name"] == "Apple Inc."
    assert result["active"] is True


def test_add_asset_strips_whitespace():
    """Test add_asset strips whitespace from symbol and type."""
    from app.db.mongo import get_db
    from app.services.assets_service import add_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    result = add_asset("  BTC  ", "  crypto  ", "Bitcoin")
    
    assert result["symbol"] == "BTC"
    assert result["type"] == "crypto"


def test_add_asset_lowercase_type():
    """Test add_asset converts type to lowercase."""
    from app.db.mongo import get_db
    from app.services.assets_service import add_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    result = add_asset("ETH", "CRYPTO", "Ethereum")
    
    assert result["type"] == "crypto"


def test_add_asset_without_name():
    """Test add_asset works without providing a name."""
    from app.db.mongo import get_db
    from app.services.assets_service import add_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    result = add_asset("XRP", "crypto")
    
    assert result["symbol"] == "XRP"
    assert result["type"] == "crypto"
    assert result["name"] is None


def test_add_asset_upsert_behavior():
    """Test add_asset doesn't overwrite existing asset (upsert behavior)."""
    from app.db.mongo import get_db
    from app.services.assets_service import add_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    # Add first time
    first = add_asset("BTC", "crypto", "Bitcoin")
    first_added_at = first["addedAt"]
    
    # Try to add again with different name
    second = add_asset("BTC", "crypto", "Bitcoin Updated")
    
    # Should return existing asset, not overwrite
    assert second["symbol"] == "BTC"
    assert second["addedAt"] == first_added_at  # Same timestamp


def test_update_asset_success():
    """Test update_asset modifies an existing asset."""
    from app.db.mongo import get_db
    from app.services.assets_service import add_asset, update_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    # Create asset
    add_asset("BTC", "crypto", "Bitcoin")
    
    # Update it
    result = update_asset("BTC", {"name": "Bitcoin Updated", "active": False})
    
    assert result["symbol"] == "BTC"
    assert result["name"] == "Bitcoin Updated"
    assert result["active"] is False
    assert "updatedAt" in result


def test_update_asset_adds_updated_at():
    """Test update_asset adds updatedAt timestamp."""
    from app.db.mongo import get_db
    from app.services.assets_service import add_asset, update_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    # Create asset
    original = add_asset("BTC", "crypto", "Bitcoin")
    original_updated = original["updatedAt"]
    
    # Wait a moment and update
    import time
    time.sleep(0.01)
    
    result = update_asset("BTC", {"name": "Updated"})
    
    # updatedAt should be newer
    assert result["updatedAt"] > original_updated


def test_update_asset_nonexistent():
    """Test update_asset on non-existent asset returns None."""
    from app.db.mongo import get_db
    from app.services.assets_service import update_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    result = update_asset("NONEXISTENT", {"name": "Test"})
    
    assert result is None


def test_delete_asset_success():
    """Test delete_asset removes an existing asset."""
    from app.db.mongo import get_db
    from app.services.assets_service import add_asset, delete_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    # Create asset
    add_asset("BTC", "crypto", "Bitcoin")
    
    # Delete it
    result = delete_asset("BTC")
    
    assert result == 1  # One document deleted


def test_delete_asset_nonexistent():
    """Test delete_asset on non-existent asset returns 0."""
    from app.db.mongo import get_db
    from app.services.assets_service import delete_asset
    
    db = get_db()
    db.assets.delete_many({})
    
    result = delete_asset("NONEXISTENT")
    
    assert result == 0  # No documents deleted


def test_list_assets_multiple():
    """Test list_assets returns multiple assets sorted by addedAt."""
    from app.db.mongo import get_db
    from app.services.assets_service import add_asset, list_assets
    import time
    
    db = get_db()
    db.assets.delete_many({})
    
    # Add multiple assets with slight delays
    add_asset("BTC", "crypto", "Bitcoin")
    time.sleep(0.01)
    add_asset("ETH", "crypto", "Ethereum")
    time.sleep(0.01)
    add_asset("AAPL", "stock", "Apple")
    
    result = list_assets()
    
    assert len(result) == 3
    # Should be sorted by addedAt descending (most recent first)
    assert result[0]["symbol"] == "AAPL"
    assert result[1]["symbol"] == "ETH"
    assert result[2]["symbol"] == "BTC"
