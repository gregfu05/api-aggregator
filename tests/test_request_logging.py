def test_request_logging_middleware(client):
    """Test that requests are logged to the database."""
    # Make a request to any endpoint
    r = client.get("/health")
    assert r.status_code == 200
    
    # The middleware should log the request to MongoDB
    # We can verify by checking the database
    from app.db.mongo import get_db
    db = get_db()
    
    # Find the most recent log entry
    logs = list(db.req_logs.find().sort("createdAt", -1).limit(1))
    assert len(logs) > 0
    
    log = logs[0]
    assert log["method"] == "GET"
    assert log["path"] == "/health"
    assert log["status"] == 200
    assert "durationMs" in log
    assert isinstance(log["durationMs"], int)


def test_request_logging_handles_db_failure(client, monkeypatch):
    """Test that the app doesn't crash if logging fails."""
    from app.db import mongo
    
    def mock_get_db_error():
        class MockCollection:
            def insert_one(self, doc):
                raise Exception("Database connection failed")
        
        class MockDB:
            req_logs = MockCollection()
        
        return MockDB()
    
    # Mock get_db to raise an error
    monkeypatch.setattr(mongo, "get_db", mock_get_db_error)
    
    # The request should still succeed even if logging fails
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
