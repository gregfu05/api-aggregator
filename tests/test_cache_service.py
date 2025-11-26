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


def test_get_cache_returns_expired_document_before_ttl_cleanup():
    """Test that cache entries persist even after expiration (like MongoDB before TTL cleanup)."""
    test_key = "will_expire_key"
    test_payload = {"data": "temp"}
    
    # Set a cache entry with very short TTL
    set_cache(test_key, test_payload, ttl_seconds=1)
    
    # Wait for it to expire
    time.sleep(1.1)
    
    # Our fake cache still returns it (like MongoDB before TTL cleanup job runs)
    result = get_cache(test_key)
    assert result is not None  # Entry still exists
    assert result["key"] == test_key
    assert result["payload"] == test_payload


def test_get_cache_returns_none_for_nonexistent_key():
    """Test that get_cache returns None for keys that don't exist."""
    result = get_cache("nonexistent_key_12345")
    assert result is None
