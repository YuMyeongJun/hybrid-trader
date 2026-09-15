"""Tests for custom exceptions module.

This module tests all custom exceptions and their inheritance hierarchy.
"""

import pytest
from hybrid_trader.exceptions import (
    HybridTraderException,
    ConfigurationError,
    APIConnectionError,
    InvalidTickerError,
    InsufficientBalanceError,
    OrderFailedError,
    SessionNotInitializedError,
    AnalysisError,
)


class TestExceptionHierarchy:
    """Test cases for exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_hybrid_trader_exception(self):
        """Test all custom exceptions inherit from HybridTraderException."""
        exception_classes = [
            ConfigurationError,
            APIConnectionError,
            InvalidTickerError,
            InsufficientBalanceError,
            OrderFailedError,
            SessionNotInitializedError,
            AnalysisError,
        ]

        for exc_class in exception_classes:
            assert issubclass(exc_class, HybridTraderException)

    def test_hybrid_trader_exception_inherits_from_exception(self):
        """Test HybridTraderException inherits from Exception."""
        assert issubclass(HybridTraderException, Exception)


class TestExceptionInstantiation:
    """Test cases for exception instantiation and error messages."""

    def test_hybrid_trader_exception_with_message(self):
        """Test HybridTraderException can be raised with message."""
        message = "Test error message"
        with pytest.raises(HybridTraderException, match=message):
            raise HybridTraderException(message)

    def test_configuration_error_initialization(self):
        """Test ConfigurationError initialization."""
        exc = ConfigurationError("api_key", "string", "invalid_value")
        assert exc.config_key == "api_key"
        assert exc.expected_type == "string"
        assert exc.provided_value == "invalid_value"
        assert "CONFIGURATION_ERROR" in str(exc)

    def test_api_connection_error_initialization(self):
        """Test APIConnectionError initialization."""
        exc = APIConnectionError("KIS", status_code=500)
        assert exc.api_name == "KIS"
        assert exc.status_code == 500
        assert "API_CONNECTION_ERROR" in str(exc)

    def test_invalid_ticker_error_initialization(self):
        """Test InvalidTickerError initialization."""
        exc = InvalidTickerError("", "stock")
        assert exc.ticker == ""
        assert exc.market == "stock"
        assert "INVALID_TICKER" in str(exc)

    def test_insufficient_balance_error_initialization(self):
        """Test InsufficientBalanceError initialization."""
        exc = InsufficientBalanceError(1000000.0, 500000.0, "KRW")
        assert exc.required_balance == 1000000.0
        assert exc.available_balance == 500000.0
        assert exc.currency == "KRW"
        assert "INSUFFICIENT_BALANCE" in str(exc)

    def test_order_failed_error_initialization(self):
        """Test OrderFailedError initialization."""
        exc = OrderFailedError("buy", "005930", "Insufficient balance", "ORD-123")
        assert exc.order_type == "buy"
        assert exc.ticker == "005930"
        assert exc.reason == "Insufficient balance"
        assert exc.order_id == "ORD-123"
        assert "ORDER_FAILED" in str(exc)

    def test_session_not_initialized_error_initialization(self):
        """Test SessionNotInitializedError initialization."""
        exc = SessionNotInitializedError("KIS", "app_key")
        assert exc.session_name == "KIS"
        assert exc.required_config == "app_key"
        assert "SESSION_NOT_INITIALIZED" in str(exc)

    def test_analysis_error_initialization(self):
        """Test AnalysisError initialization."""
        exc = AnalysisError("moving_average", "Insufficient data points")
        assert exc.analysis_type == "moving_average"
        assert exc.data_info == "Insufficient data points"
        assert "ANALYSIS_ERROR" in str(exc)


class TestExceptionCatching:
    """Test cases for catching exceptions with inheritance."""

    def test_catch_configuration_error_as_hybrid_trader_exception(self):
        """Test ConfigurationError can be caught as HybridTraderException."""
        with pytest.raises(HybridTraderException):
            raise ConfigurationError("key", "type", "value")

    def test_catch_api_connection_error_as_hybrid_trader_exception(self):
        """Test APIConnectionError can be caught as HybridTraderException."""
        with pytest.raises(HybridTraderException):
            raise APIConnectionError("KIS")

    def test_catch_all_custom_errors_as_hybrid_trader_exception(self):
        """Test all custom errors can be caught as HybridTraderException."""
        exceptions = [
            ConfigurationError("key", "type", "value"),
            APIConnectionError("KIS"),
            InvalidTickerError("", "stock"),
            InsufficientBalanceError(1000000.0, 500000.0),
            OrderFailedError("buy", "005930", "Failed"),
            SessionNotInitializedError("KIS"),
            AnalysisError("rsi"),
        ]

        for exc in exceptions:
            with pytest.raises(HybridTraderException):
                raise exc


class TestExceptionMessages:
    """Test cases for exception messages and string representation."""

    def test_exception_message_preserved(self):
        """Test exception message is preserved when raised and caught."""
        message = "Specific error message"
        try:
            raise HybridTraderException(message)
        except HybridTraderException as e:
            assert message in str(e)

    def test_exception_error_code_included(self):
        """Test exception error code is included in string representation."""
        exc = ConfigurationError("key")
        assert "CONFIGURATION_ERROR" in str(exc)

    def test_exception_repr(self):
        """Test exception repr includes class name."""
        exc = InvalidTickerError("", "stock")
        assert "InvalidTickerError" in repr(exc)

    def test_exception_with_custom_message(self):
        """Test exception with custom message."""
        custom_msg = "Custom error message"
        exc = ConfigurationError("key", message=custom_msg)
        assert custom_msg in str(exc)


class TestExceptionUseCases:
    """Test real-world usage scenarios for exceptions."""

    def test_configuration_validation_error(self):
        """Test ConfigurationError in configuration validation scenario."""
        def validate_config(config_dict):
            if 'api_key' not in config_dict:
                raise ConfigurationError('api_key', 'string', 'missing')
            return True

        with pytest.raises(ConfigurationError):
            validate_config({})

    def test_api_call_error_handling(self):
        """Test APIConnectionError in API call scenario."""
        def call_api(endpoint):
            if not endpoint:
                raise APIConnectionError("KIS")
            return {"status": "success"}

        with pytest.raises(APIConnectionError):
            call_api(None)

    def test_ticker_validation_error(self):
        """Test InvalidTickerError in ticker validation scenario."""
        def validate_ticker(ticker):
            if not isinstance(ticker, str) or len(ticker) == 0:
                raise InvalidTickerError(ticker, "stock")
            return True

        with pytest.raises(InvalidTickerError):
            validate_ticker("")

    def test_balance_check_error(self):
        """Test InsufficientBalanceError in balance check scenario."""
        def execute_trade(balance, amount):
            if balance < amount:
                raise InsufficientBalanceError(amount, balance)
            return True

        with pytest.raises(InsufficientBalanceError):
            execute_trade(1000, 2000)

    def test_order_execution_error(self):
        """Test OrderFailedError in order execution scenario."""
        def place_order(ticker, amount):
            if amount <= 0:
                raise OrderFailedError("buy", ticker, "Invalid amount")
            return True

        with pytest.raises(OrderFailedError):
            place_order("005930", -100)

    def test_session_initialization_error(self):
        """Test SessionNotInitializedError in session access scenario."""
        def access_session(session):
            if session is None:
                raise SessionNotInitializedError("KIS", "app_key")
            return session

        with pytest.raises(SessionNotInitializedError):
            access_session(None)

    def test_analysis_data_validation_error(self):
        """Test AnalysisError in data validation scenario."""
        def analyze_prices(prices):
            if not prices or len(prices) < 2:
                raise AnalysisError("moving_average", "Insufficient data")
            return True

        with pytest.raises(AnalysisError):
            analyze_prices([])


class TestExceptionDetails:
    """Test exception detail attributes."""

    def test_insufficient_balance_error_shortage_calculation(self):
        """Test InsufficientBalanceError calculates shortage correctly."""
        required = 1000000.0
        available = 600000.0
        shortage = required - available

        exc = InsufficientBalanceError(required, available)
        assert "shortage" in str(exc).lower()
        assert "400,000.00" in str(exc)

    def test_order_failed_error_with_order_id(self):
        """Test OrderFailedError includes order ID."""
        exc = OrderFailedError("sell", "005930", "Server error", "ORD-789")
        assert "ORD-789" in str(exc)

    def test_order_failed_error_without_order_id(self):
        """Test OrderFailedError works without order ID."""
        exc = OrderFailedError("buy", "000660", "Network error")
        assert "Network error" in str(exc)

    def test_api_connection_error_with_original_error(self):
        """Test APIConnectionError includes original error."""
        original = Exception("Network timeout")
        exc = APIConnectionError("Upbit", original_error=original)
        assert "Network timeout" in str(exc)
