def test_suggest_crypto_success(client):
    """Test GET /suggest/crypto returns crypto suggestions."""
    r = client.get("/suggest/crypto", params={"q": "bit"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Should return at least one result
    # Check structure of results
    if len(data) > 0:
        assert "id" in data[0] or "symbol" in data[0]


def test_suggest_crypto_with_limit(client):
    """Test GET /suggest/crypto respects limit parameter."""
    r = client.get("/suggest/crypto", params={"q": "bit", "limit": 2})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 2  # Should respect limit


def test_suggest_crypto_empty_query(client):
    """Test GET /suggest/crypto with missing query parameter."""
    r = client.get("/suggest/crypto")
    assert r.status_code == 422  # FastAPI validation error


def test_suggest_stocks_success(client, monkeypatch):
    """Test GET /suggest/stocks returns stock suggestions."""
    import requests
    from unittest.mock import Mock
    
    # Mock the requests.get call
    mock_response = Mock()
    mock_response.json.return_value = {
        "bestMatches": [
            {
                "1. symbol": "AAPL",
                "2. name": "Apple Inc.",
                "3. type": "Equity",
                "4. region": "United States"
            },
            {
                "1. symbol": "AAPA",
                "2. name": "Another Apple",
                "3. type": "Equity",
                "4. region": "United States"
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    
    def mock_get(url, params=None, timeout=None):
        return mock_response
    
    monkeypatch.setattr(requests, "get", mock_get)
    
    r = client.get("/suggest/stocks", params={"q": "aap"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["symbol"] == "AAPL"
    assert data[0]["name"] == "Apple Inc."


def test_suggest_stocks_with_limit(client, monkeypatch):
    """Test GET /suggest/stocks respects limit parameter."""
    import requests
    from unittest.mock import Mock
    
    mock_response = Mock()
    mock_response.json.return_value = {
        "bestMatches": [
            {"1. symbol": "AAPL", "2. name": "Apple Inc.", "3. type": "Equity", "4. region": "US"},
            {"1. symbol": "AAPA", "2. name": "Another", "3. type": "Equity", "4. region": "US"},
            {"1. symbol": "AAP", "2. name": "Third", "3. type": "Equity", "4. region": "US"}
        ]
    }
    mock_response.raise_for_status = Mock()
    
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: mock_response)
    
    r = client.get("/suggest/stocks", params={"q": "aa", "limit": 2})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2


def test_suggest_stocks_api_error(client, monkeypatch):
    """Test GET /suggest/stocks handles API errors."""
    import requests
    
    def mock_get_error(*args, **kwargs):
        raise Exception("Network error")
    
    monkeypatch.setattr(requests, "get", mock_get_error)
    
    r = client.get("/suggest/stocks", params={"q": "aap"})
    assert r.status_code == 502
    assert "Network error" in r.json()["detail"]


def test_suggest_stocks_empty_query(client):
    """Test GET /suggest/stocks with missing query parameter."""
    r = client.get("/suggest/stocks")
    assert r.status_code == 422  # FastAPI validation error
