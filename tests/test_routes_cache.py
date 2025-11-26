"""Tests for cache management routes."""


def test_cache_status_empty(client):
    """Test cache status when cache is empty."""
    response = client.get("/cache/status")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["keysSample"] == []
    assert "ttlDefaultNote" in data


def test_cache_status_with_entries(client):
    """Test cache status with some cached entries."""
    # Add entries directly to db.cache (not via cache_service)
    from app.db.mongo import get_db
    from datetime import datetime, timezone, timedelta
    db = get_db()
    db.cache.insert_one({"key": "key1", "payload": {"data": "value1"}, "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=60)})
    db.cache.insert_one({"key": "key2", "payload": {"data": "value2"}, "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=60)})
    db.cache.insert_one({"key": "key3", "payload": {"data": "value3"}, "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=60)})
    
    response = client.get("/cache/status")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    assert len(data["keysSample"]) == 3
    assert "key1" in data["keysSample"]


def test_cache_status_with_sample_limit(client):
    """Test cache status with sample limit."""
    # Add entries directly to db.cache
    from app.db.mongo import get_db
    from datetime import datetime, timezone, timedelta
    db = get_db()
    for i in range(10):
        db.cache.insert_one({"key": f"key{i}", "payload": {"data": f"value{i}"}, "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=60)})
    
    response = client.get("/cache/status?sample=3")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 10
    assert len(data["keysSample"]) == 3


def test_cache_clear_all(client):
    """Test clearing all cache entries."""
    # Add entries directly to db.cache
    from app.db.mongo import get_db
    from datetime import datetime, timezone, timedelta
    db = get_db()
    db.cache.insert_one({"key": "key1", "payload": {"data": "value1"}, "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=60)})
    db.cache.insert_one({"key": "key2", "payload": {"data": "value2"}, "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=60)})
    
    response = client.post("/cache/clear", json={"all": True})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "all"
    assert data["cleared"] == 2
    
    # Verify cache is empty
    status = client.get("/cache/status")
    assert status.json()["count"] == 0


def test_cache_clear_specific_keys(client):
    """Test clearing specific cache keys."""
    # Add entries directly to db.cache
    from app.db.mongo import get_db
    from datetime import datetime, timezone, timedelta
    db = get_db()
    db.cache.insert_one({"key": "key1", "payload": {"data": "value1"}, "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=60)})
    db.cache.insert_one({"key": "key2", "payload": {"data": "value2"}, "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=60)})
    db.cache.insert_one({"key": "key3", "payload": {"data": "value3"}, "expiresAt": datetime.now(timezone.utc) + timedelta(seconds=60)})
    
    response = client.post("/cache/clear", json={"keys": ["key1", "key3"]})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "keys"
    assert data["cleared"] == 2
    assert data["keys"] == ["key1", "key3"]
    
    # Verify only key2 remains
    status = client.get("/cache/status")
    assert status.json()["count"] == 1


def test_cache_clear_no_params(client):
    """Test cache clear with no parameters returns error."""
    response = client.post("/cache/clear", json={})
    assert response.status_code == 400
    assert "Provide" in response.json()["detail"]


def test_cache_clear_empty_keys_list(client):
    """Test cache clear with empty keys list returns error (empty list is falsy)."""
    response = client.post("/cache/clear", json={"keys": []})
    assert response.status_code == 400
    assert "Provide" in response.json()["detail"]
