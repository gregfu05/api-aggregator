import pytest
from unittest.mock import patch
from app.services.aggregator import aggregate_with_cache


def test_aggregate_one_crypto():
    """Test aggregating a single crypto symbol."""
    with patch('app.services.aggregator.fetch_simple_price') as mock_crypto, \
         patch('app.services.aggregator.get_cache') as mock_get_cache, \
         patch('app.services.aggregator.set_cache') as mock_set_cache:
        
        # Mock cache miss
        mock_get_cache.return_value = None
        
        # Mock CoinGecko response
        mock_crypto.return_value = {"bitcoin": {"usd": 45000.0}}
        
        result = aggregate_with_cache("bitcoin")
        
        assert "assets" in result
        assert len(result["assets"]) == 1
        
        asset = result["assets"][0]
        assert asset["symbol"] == "bitcoin"
        assert asset["type"] == "crypto"
        assert asset["price"] == 45000.0
        assert asset["source"] == "coingecko"
        assert "asOf" in asset
        
        # Verify cache was called
        mock_crypto.assert_called_once_with(["bitcoin"], ["usd"])
        mock_set_cache.assert_called_once()


def test_aggregate_one_stock():
    """Test aggregating a single stock symbol."""
    with patch('app.services.aggregator.fetch_quote') as mock_stock, \
         patch('app.services.aggregator.get_cache') as mock_get_cache, \
         patch('app.services.aggregator.set_cache') as mock_set_cache:
        
        # Mock cache miss
        mock_get_cache.return_value = None
        
        # Mock Alpha Vantage response
        mock_stock.return_value = {
            "05. price": "150.25",
            "07. latest trading day": "2025-11-25"
        }
        
        result = aggregate_with_cache("AAPL")
        
        assert "assets" in result
        assert len(result["assets"]) == 1
        
        asset = result["assets"][0]
        assert asset["symbol"] == "AAPL"
        assert asset["type"] == "stock"
        assert asset["price"] == 150.25
        assert asset["source"] == "alphavantage"
        assert asset["asOf"] == "2025-11-25"
        
        # Verify cache was called
        mock_stock.assert_called_once_with("AAPL")
        mock_set_cache.assert_called_once()


def test_aggregate_mixed_inputs():
    """Test aggregating both crypto and stock symbols."""
    with patch('app.services.aggregator.fetch_simple_price') as mock_crypto, \
         patch('app.services.aggregator.fetch_quote') as mock_stock, \
         patch('app.services.aggregator.get_cache') as mock_get_cache, \
         patch('app.services.aggregator.set_cache') as mock_set_cache:
        
        # Mock cache miss
        mock_get_cache.return_value = None
        
        # Mock responses
        mock_crypto.return_value = {"bitcoin": {"usd": 45000.0}}
        mock_stock.return_value = {
            "05. price": "150.25",
            "07. latest trading day": "2025-11-25"
        }
        
        result = aggregate_with_cache("bitcoin,AAPL")
        
        assert "assets" in result
        assert len(result["assets"]) == 2
        
        # Find crypto and stock assets
        crypto_asset = next(a for a in result["assets"] if a["type"] == "crypto")
        stock_asset = next(a for a in result["assets"] if a["type"] == "stock")
        
        assert crypto_asset["symbol"] == "bitcoin"
        assert crypto_asset["price"] == 45000.0
        
        assert stock_asset["symbol"] == "AAPL"
        assert stock_asset["price"] == 150.25
        
        # Verify both adapters were called
        mock_crypto.assert_called_once_with(["bitcoin"], ["usd"])
        mock_stock.assert_called_once_with("AAPL")


def test_invalid_symbol_handling():
    """Test handling of invalid symbols that return no data."""
    with patch('app.services.aggregator.fetch_simple_price') as mock_crypto, \
         patch('app.services.aggregator.fetch_quote') as mock_stock, \
         patch('app.services.aggregator.get_cache') as mock_get_cache, \
         patch('app.services.aggregator.set_cache') as mock_set_cache:
        
        # Mock cache miss
        mock_get_cache.return_value = None
        
        # Mock CoinGecko returning empty data for invalid crypto symbol
        mock_crypto.return_value = {}  # No data for invalid symbol
        
        # Mock Alpha Vantage returning empty quote for invalid stock symbol
        mock_stock.return_value = {}  # No price field
        
        # Test with a lowercase crypto-like invalid symbol
        result = aggregate_with_cache("invalidcrypto")
        
        assert "assets" in result
        assert len(result["assets"]) == 0  # No valid assets returned
        assert result["meta"]["cache"] == "miss"
        
        # Verify the crypto adapter was called (but returned no data)
        mock_crypto.assert_called_once_with(["invalidcrypto"], ["usd"])


def test_stock_price_conversion_error():
    """Test handling when stock price cannot be converted to float."""
    with patch('app.services.aggregator.fetch_quote') as mock_stock, \
         patch('app.services.aggregator.get_cache') as mock_get_cache, \
         patch('app.services.aggregator.set_cache') as mock_set_cache:
        
        # Mock cache miss
        mock_get_cache.return_value = None
        
        # Mock Alpha Vantage returning non-numeric price
        mock_stock.return_value = {
            "05. price": "N/A",  # Invalid price format
            "07. latest trading day": "2025-11-25"
        }
        
        result = aggregate_with_cache("INVALID")
        
        assert "assets" in result
        assert len(result["assets"]) == 1
        asset = result["assets"][0]
        assert asset["symbol"] == "INVALID"
        assert asset["price"] == 0.0  # Falls back to 0.0 when conversion fails
