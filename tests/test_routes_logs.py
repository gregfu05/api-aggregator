"""Tests for request logging routes."""


def test_logs_status_empty(client):
    """Test logs status when no logs exist."""
    response = client.get("/logs/status")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["latest"] == []


def test_logs_status_with_entries(client):
    """Test logs status with request logs."""
    from app.db.mongo import get_db
    from datetime import datetime, timezone
    
    db = get_db()
    # Add some log entries
    db.req_logs.insert_one({
        "path": "/test1",
        "method": "GET",
        "statusCode": 200,
        "createdAt": datetime.now(timezone.utc)
    })
    db.req_logs.insert_one({
        "path": "/test2",
        "method": "POST",
        "statusCode": 201,
        "createdAt": datetime.now(timezone.utc)
    })
    
    response = client.get("/logs/status")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["latest"]) == 2
    assert any(log["path"] == "/test1" for log in data["latest"])


def test_logs_status_limits_to_three(client):
    """Test logs status returns only latest 3 entries."""
    from app.db.mongo import get_db
    from datetime import datetime, timezone, timedelta
    
    db = get_db()
    # Add 5 log entries with different timestamps
    base_time = datetime.now(timezone.utc)
    for i in range(5):
        db.req_logs.insert_one({
            "path": f"/test{i}",
            "method": "GET",
            "statusCode": 200,
            "createdAt": base_time + timedelta(seconds=i)
        })
    
    response = client.get("/logs/status")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5
    assert len(data["latest"]) == 3
    # Should return newest entries (test3, test4)
    paths = [log["path"] for log in data["latest"]]
    assert "/test4" in paths  # Most recent
