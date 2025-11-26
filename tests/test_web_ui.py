"""Tests for web UI routes."""


def test_home_page(client):
    """Test home page renders."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check for expected content
    content = response.text
    assert "CryptoStock" in content or "Crypto" in content or "Mixed" in content


def test_ui_search_empty_symbols(client):
    """Test UI search with empty symbols."""
    response = client.get("/ui/search?symbols=")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    content = response.text
    assert "Please enter at least one symbol" in content or "symbol" in content.lower()


def test_ui_search_with_symbols(client):
    """Test UI search with valid symbols."""
    response = client.get("/ui/search?symbols=bitcoin,AAPL")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    content = response.text
    # Should have rendered results
    assert "bitcoin" in content or "AAPL" in content


def test_ui_search_with_window_param(client):
    """Test UI search with custom window parameter."""
    response = client.get("/ui/search?symbols=bitcoin&window=120")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_ui_search_with_whitespace_symbols(client):
    """Test UI search with whitespace-only symbols."""
    response = client.get("/ui/search?symbols=   ")
    assert response.status_code == 200
    content = response.text
    assert "Please enter" in content or "symbol" in content.lower()


def test_crypto_page_no_symbol(client):
    """Test crypto page without symbol."""
    response = client.get("/crypto")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    content = response.text
    assert "crypto" in content.lower()


def test_crypto_page_with_symbol(client):
    """Test crypto page with symbol."""
    response = client.get("/crypto?symbol=bitcoin")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    content = response.text
    assert "bitcoin" in content.lower()


def test_crypto_page_with_whitespace_symbol(client):
    """Test crypto page with whitespace symbol."""
    response = client.get("/crypto?symbol=   ")
    assert response.status_code == 200
    # Should render page without error


def test_stocks_page_no_symbol(client):
    """Test stocks page without symbol."""
    response = client.get("/stocks")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    content = response.text
    assert "stock" in content.lower()


def test_stocks_page_with_symbol(client):
    """Test stocks page with symbol."""
    response = client.get("/stocks?symbol=AAPL")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    content = response.text
    assert "AAPL" in content or "aapl" in content.lower()


def test_stocks_page_with_whitespace_symbol(client):
    """Test stocks page with whitespace symbol."""
    response = client.get("/stocks?symbol=   ")
    assert response.status_code == 200
    # Should render page without error
