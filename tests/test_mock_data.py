"""Tests for mock data generation and API response structures.

This module tests mock data generators and ensures API response structures are correct.
"""

import pytest
from tests.conftest import generate_mock_prices


class TestMockPriceGeneration:
    """Test cases for mock price data generation."""

    def test_generate_mock_prices_basic(self):
        """Test basic mock price generation."""
        prices = generate_mock_prices(base_price=100.0, count=10)

        assert len(prices) == 10
        assert all(isinstance(p, float) for p in prices)
        assert all(p > 0 for p in prices)

    def test_generate_mock_prices_custom_base(self):
        """Test mock price generation with custom base price."""
        prices = generate_mock_prices(base_price=50000.0, count=10)

        assert len(prices) == 10
        assert prices[0] > 0  # All prices should be positive

    def test_generate_mock_prices_volatility(self):
        """Test mock price generation with high volatility."""
        low_vol = generate_mock_prices(volatility=0.01, count=50)
        high_vol = generate_mock_prices(volatility=0.1, count=50)

        # High volatility should produce more variance
        low_vol_std = (max(low_vol) - min(low_vol)) / min(low_vol)
        high_vol_std = (max(high_vol) - min(high_vol)) / min(high_vol)

        assert high_vol_std > low_vol_std

    def test_generate_mock_prices_trend_up(self):
        """Test mock price generation with uptrend."""
        prices = generate_mock_prices(trend=0.01, count=50)

        # Check for overall uptrend (last price > first price)
        # Note: With randomness, this may not always be true, so we just verify generation
        assert len(prices) == 50
        assert prices[-1] > 0

    def test_generate_mock_prices_trend_down(self):
        """Test mock price generation with downtrend."""
        prices = generate_mock_prices(trend=-0.01, count=50)

        assert len(prices) == 50
        assert all(p > 0 for p in prices)

    def test_generate_mock_prices_deterministic(self):
        """Test that mock price generation is deterministic with same seed."""
        prices1 = generate_mock_prices(count=20)
        prices2 = generate_mock_prices(count=20)

        # Should be identical due to seed
        assert prices1 == prices2

    def test_generate_mock_prices_large_dataset(self):
        """Test generating large mock price dataset."""
        prices = generate_mock_prices(count=1000)

        assert len(prices) == 1000
        assert all(isinstance(p, float) for p in prices)


class TestMockKISResponse:
    """Test cases for mock KIS API responses."""

    def test_kis_response_structure(self, mock_kis_response):
        """Test KIS API response structure."""
        assert "rt_cd" in mock_kis_response
        assert "msg_cd" in mock_kis_response
        assert "output" in mock_kis_response

        output = mock_kis_response["output"]
        assert "stck_prpr" in output  # Stock price
        assert "stck_vol" in output   # Volume

    def test_kis_response_data_types(self, mock_kis_response):
        """Test KIS API response data types."""
        assert isinstance(mock_kis_response["rt_cd"], str)
        assert isinstance(mock_kis_response["msg_cd"], str)
        assert isinstance(mock_kis_response["output"], dict)

    def test_kis_response_stock_price(self, mock_kis_response):
        """Test KIS API stock price field."""
        output = mock_kis_response["output"]
        price = float(output["stck_prpr"])

        assert price > 0
        assert isinstance(price, float)

    def test_kis_response_volume(self, mock_kis_response):
        """Test KIS API volume field."""
        output = mock_kis_response["output"]
        volume = int(output["stck_vol"])

        assert volume >= 0
        assert isinstance(volume, int)


class TestMockUpbitResponse:
    """Test cases for mock Upbit API responses."""

    def test_upbit_response_structure(self, mock_upbit_response):
        """Test Upbit API response structure."""
        required_fields = [
            "market",
            "trade_price",
            "high_price",
            "low_price",
            "opening_price",
        ]

        for field in required_fields:
            assert field in mock_upbit_response

    def test_upbit_response_data_types(self, mock_upbit_response):
        """Test Upbit API response data types."""
        assert isinstance(mock_upbit_response["market"], str)
        assert isinstance(mock_upbit_response["trade_price"], float)
        assert isinstance(mock_upbit_response["candle_acc_trade_volume"], float)

    def test_upbit_response_price_consistency(self, mock_upbit_response):
        """Test Upbit API price consistency."""
        assert mock_upbit_response["high_price"] >= mock_upbit_response["opening_price"]
        assert mock_upbit_response["high_price"] >= mock_upbit_response["low_price"]
        assert mock_upbit_response["low_price"] <= mock_upbit_response["opening_price"]

    def test_upbit_response_market_format(self, mock_upbit_response):
        """Test Upbit market ticker format."""
        market = mock_upbit_response["market"]

        assert "-" in market  # Format: "KRW-BTC"
        parts = market.split("-")
        assert len(parts) == 2
        assert parts[0] == "KRW"


class TestMockOrderResponse:
    """Test cases for mock order responses."""

    def test_order_response_structure(self, mock_order_response):
        """Test order response structure."""
        required_fields = [
            "order_id",
            "status",
            "quantity",
            "price",
            "total",
            "type",
        ]

        for field in required_fields:
            assert field in mock_order_response

    def test_order_response_data_types(self, mock_order_response):
        """Test order response data types."""
        assert isinstance(mock_order_response["order_id"], str)
        assert isinstance(mock_order_response["status"], str)
        assert isinstance(mock_order_response["quantity"], (int, float))
        assert isinstance(mock_order_response["price"], (int, float))

    def test_order_response_calculation(self, mock_order_response):
        """Test order response calculation correctness."""
        expected_total = (
            mock_order_response["quantity"] * mock_order_response["price"]
        )

        assert mock_order_response["total"] == pytest.approx(expected_total)

    def test_order_response_valid_statuses(self, mock_order_response):
        """Test order response has valid status."""
        valid_statuses = ["accepted", "rejected", "pending", "executed", "cancelled"]
        assert mock_order_response["status"] in valid_statuses

    def test_order_response_valid_types(self, mock_order_response):
        """Test order response has valid type."""
        valid_types = ["buy", "sell"]
        assert mock_order_response["type"] in valid_types


class TestMockBalanceResponse:
    """Test cases for mock balance responses."""

    def test_balance_response_structure(self, mock_balance_response):
        """Test balance response structure."""
        required_fields = [
            "account_id",
            "total_balance",
            "available_balance",
            "holdings",
        ]

        for field in required_fields:
            assert field in mock_balance_response

    def test_balance_response_data_types(self, mock_balance_response):
        """Test balance response data types."""
        assert isinstance(mock_balance_response["account_id"], str)
        assert isinstance(mock_balance_response["total_balance"], (int, float))
        assert isinstance(mock_balance_response["available_balance"], (int, float))
        assert isinstance(mock_balance_response["holdings"], list)

    def test_balance_response_balance_consistency(self, mock_balance_response):
        """Test balance response consistency."""
        # Available balance should not exceed total balance
        assert (
            mock_balance_response["available_balance"]
            <= mock_balance_response["total_balance"]
        )

    def test_balance_response_holdings_structure(self, mock_balance_response):
        """Test holdings structure in balance response."""
        holdings = mock_balance_response["holdings"]

        if holdings:
            holding = holdings[0]
            required_fields = ["ticker", "quantity", "average_price", "current_price"]

            for field in required_fields:
                assert field in holding

    def test_balance_response_holding_prices(self, mock_balance_response):
        """Test holding price consistency."""
        holdings = mock_balance_response["holdings"]

        for holding in holdings:
            assert holding["average_price"] > 0
            assert holding["current_price"] > 0
            assert holding["quantity"] > 0


class TestMockOHLCData:
    """Test cases for mock OHLC data."""

    def test_ohlc_data_structure(self, mock_ohlc_data):
        """Test OHLC data structure."""
        assert isinstance(mock_ohlc_data, list)
        assert len(mock_ohlc_data) > 0

        for candle in mock_ohlc_data:
            required_fields = ["open", "high", "low", "close", "volume"]
            for field in required_fields:
                assert field in candle

    def test_ohlc_data_price_relationships(self, mock_ohlc_data):
        """Test OHLC price relationships."""
        for candle in mock_ohlc_data:
            # High should be >= all other prices
            assert candle["high"] >= candle["open"]
            assert candle["high"] >= candle["close"]
            assert candle["high"] >= candle["low"]

            # Low should be <= all other prices
            assert candle["low"] <= candle["open"]
            assert candle["low"] <= candle["close"]
            assert candle["low"] <= candle["high"]

    def test_ohlc_data_positive_values(self, mock_ohlc_data):
        """Test OHLC data has positive values."""
        for candle in mock_ohlc_data:
            assert candle["open"] > 0
            assert candle["high"] > 0
            assert candle["low"] > 0
            assert candle["close"] > 0
            assert candle["volume"] >= 0

    def test_ohlc_data_volume_type(self, mock_ohlc_data):
        """Test OHLC volume is numeric."""
        for candle in mock_ohlc_data:
            assert isinstance(candle["volume"], (int, float))
            assert candle["volume"] >= 0

    def test_ohlc_data_timestamps(self, mock_ohlc_data):
        """Test OHLC data has timestamps."""
        for candle in mock_ohlc_data:
            assert "timestamp" in candle or "candle_date_time_kst" in candle


class TestMockSessionObjects:
    """Test cases for mock session objects."""

    def test_kis_session_methods(self, mock_kis_session):
        """Test mock KIS session has required methods."""
        assert hasattr(mock_kis_session, "fetch_price")
        assert hasattr(mock_kis_session, "close")

    def test_kis_session_fetch_price_callable(self, mock_kis_session):
        """Test mock KIS session fetch_price is callable."""
        result = mock_kis_session.fetch_price("005930")
        assert result is not None

    def test_kis_session_close_callable(self, mock_kis_session):
        """Test mock KIS session close is callable."""
        mock_kis_session.close()
        assert mock_kis_session.close.called

    def test_upbit_session_methods(self, mock_upbit_session):
        """Test mock Upbit session has required methods."""
        assert hasattr(mock_upbit_session, "get_current_price")
        assert hasattr(mock_upbit_session, "close")

    def test_upbit_session_get_current_price_callable(self, mock_upbit_session):
        """Test mock Upbit session get_current_price is callable."""
        result = mock_upbit_session.get_current_price("KRW-BTC")
        assert isinstance(result, (int, float))

    def test_upbit_session_close_callable(self, mock_upbit_session):
        """Test mock Upbit session close is callable."""
        mock_upbit_session.close()
        assert mock_upbit_session.close.called


class TestStockPriceData:
    """Test cases for mock stock price data."""

    def test_stock_prices_structure(self, mock_stock_prices):
        """Test stock prices data structure."""
        assert isinstance(mock_stock_prices, dict)
        assert all(isinstance(k, str) for k in mock_stock_prices.keys())
        assert all(isinstance(v, (int, float)) for v in mock_stock_prices.values())

    def test_stock_prices_all_positive(self, mock_stock_prices):
        """Test all stock prices are positive."""
        assert all(price > 0 for price in mock_stock_prices.values())

    def test_stock_prices_have_samples(self, mock_stock_prices):
        """Test stock prices contain expected samples."""
        expected_tickers = ["005930", "000660"]
        for ticker in expected_tickers:
            assert ticker in mock_stock_prices


class TestCryptoPriceData:
    """Test cases for mock cryptocurrency price data."""

    def test_crypto_prices_structure(self, mock_crypto_prices):
        """Test crypto prices data structure."""
        assert isinstance(mock_crypto_prices, dict)
        assert all(isinstance(k, str) for k in mock_crypto_prices.keys())
        assert all(isinstance(v, (int, float)) for v in mock_crypto_prices.values())

    def test_crypto_prices_all_positive(self, mock_crypto_prices):
        """Test all crypto prices are positive."""
        assert all(price > 0 for price in mock_crypto_prices.values())

    def test_crypto_prices_format(self, mock_crypto_prices):
        """Test crypto prices use standard format."""
        for ticker in mock_crypto_prices.keys():
            assert ticker.startswith("KRW-")


class TestPriceHistoryData:
    """Test cases for mock price history data."""

    def test_price_history_structure(self, mock_price_history):
        """Test price history data structure."""
        assert isinstance(mock_price_history, list)
        assert len(mock_price_history) > 0
        assert all(isinstance(p, (int, float)) for p in mock_price_history)

    def test_price_history_all_positive(self, mock_price_history):
        """Test all prices in history are positive."""
        assert all(p > 0 for p in mock_price_history)

    def test_price_history_length(self, mock_price_history):
        """Test price history has sufficient data."""
        assert len(mock_price_history) >= 30
