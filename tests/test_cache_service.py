import time
from datetime import datetime, timedelta, timezone
from app.services.cache_service import get_cache, set_cache


def test_set_cache_stores_properly():
    """Test that set_cache stores data with correct structure."""
    test_key = "test_key_1"
    test_payload = {"symbol": "BTC", "price": 50000.0}
    
    # Set cache with 60 second TTL
    set_cache(test_key, test_payload, ttl_seconds=60)
    
    # Retrieve the cached entry
    result = get_cache(test_key)
    
    assert result is not None
    assert result["key"] == test_key
    assert result["payload"] == test_payload
    assert "expiresAt" in result
    assert isinstance(result["expiresAt"], datetime)
    
    # Check that expiresAt is approximately 60 seconds from now
    expected_expiry = datetime.now(timezone.utc) + timedelta(seconds=60)
    time_diff = abs((result["expiresAt"] - expected_expiry).total_seconds())
    assert time_diff < 2  # Allow 2 seconds tolerance


def test_get_cache_returns_expired_document_before_ttl_cleanup(monkeypatch):
    """Expired documents still appear until MongoDB TTL cleanup deletes them."""
    # Mock the database to return an expired cache entry
    def mock_get_db():
        class MockCollection:
            def find_one(self, query):
                if query.get("key") == "expired_key":
                    # Return an entry that expired 10 seconds ago
                    expired_time = datetime.now(timezone.utc) - timedelta(seconds=10)
                    return {
                        "_id": "mock_id",
                        "key": "expired_key", 
                        "payload": {"data": "old"},
                        "expiresAt": expired_time
                    }
                return None
        
        class MockDB:
            def __init__(self):
                self.cache = MockCollection()
        
        return MockDB()
    
    # Apply the monkeypatch
    import app.services.cache_service
    monkeypatch.setattr(app.services.cache_service, "get_db", mock_get_db)
    
    # Test that expired cache returns the document (MongoDB TTL handles actual deletion)
    result = get_cache("expired_key")
    assert result is not None  # The function returns the doc, MongoDB handles TTL cleanup
    assert result["key"] == "expired_key"
    assert "expiresAt" in result


def test_get_cache_returns_none_for_nonexistent_key():
    """Test that get_cache returns None for keys that don't exist."""
    result = get_cache("nonexistent_key_12345")
    assert result is None
