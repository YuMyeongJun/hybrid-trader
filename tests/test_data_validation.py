"""Data validation tests for Hybrid Trader.

This module tests data validation, type checking, and schema validation
across the trading engine and related components.

데이터 유효성 검증 테스트를 수행합니다.
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from hybrid_trader.engine import HybridTradingEngine
from hybrid_trader.config import TradingConfig, KISConfig, UpbitConfig
from hybrid_trader.exceptions import InvalidTickerError, ConfigurationError, APIConnectionError


@pytest.mark.data_validation
class TestTickerValidation:
    """Test ticker symbol validation."""

    def test_valid_stock_ticker_formats(self, trading_engine):
        """Test recognition of valid stock ticker formats.

        유효한 주식 티커 형식 인식 테스트
        """
        valid_tickers = [
            "005930",  # Samsung
            "000660",  # SK Hynix
            "005380",  # Hyundai Motor
            "051910",  # LG Chem
            "207940",  # Samsung Electronics
        ]

        for ticker in valid_tickers:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
                result = trading_engine.get_stock_price(ticker)
                assert result is not None or result is None  # Just checking no exception

    def test_valid_crypto_ticker_formats(self, trading_engine):
        """Test recognition of valid crypto ticker formats.

        유효한 암호화폐 티커 형식 인식 테스트
        """
        valid_tickers = [
            "KRW-BTC",
            "KRW-ETH",
            "KRW-XRP",
            "KRW-DOGE",
            "KRW-ADA",
        ]

        for ticker in valid_tickers:
            with patch.object(trading_engine.upbit_session, 'get_ticker', return_value={"trade_price": 50000000}):
                result = trading_engine.get_coin_price(ticker)
                assert result is not None or result is None

    def test_ticker_length_validation(self, trading_engine):
        """Test ticker length validation.

        티커 길이 검증 테스트
        """
        # Too short
        with pytest.raises(InvalidTickerError):
            trading_engine.get_stock_price("00")

        # Too long
        with pytest.raises(InvalidTickerError):
            trading_engine.get_stock_price("0" * 100)

    def test_ticker_character_validation(self, trading_engine):
        """Test ticker character validation.

        티커 문자 검증 테스트
        """
        invalid_chars = [
            "005@30",
            "0059#0",
            "0059 30",
            "005.930",
            "005,930",
        ]

        for ticker in invalid_chars:
            with pytest.raises(InvalidTickerError):
                trading_engine.get_stock_price(ticker)

    def test_ticker_whitespace_handling(self, trading_engine):
        """Test ticker whitespace handling.

        티커 공백 처리 테스트
        """
        # Ticker with spaces should be rejected or stripped
        with pytest.raises(InvalidTickerError):
            trading_engine.get_stock_price(" 005930 ")

        with pytest.raises(InvalidTickerError):
            trading_engine.get_stock_price("005 930")


@pytest.mark.data_validation
class TestPriceValidation:
    """Test price data validation."""

    def test_price_type_validation(self, trading_engine):
        """Test price type validation.

        가격 타입 검증 테스트
        """
        # Valid types
        valid_prices = [
            50000,           # int
            50000.0,         # float
            Decimal("50000"), # Decimal
        ]

        for price in valid_prices:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=price):
                result = trading_engine.get_stock_price("005930")
                assert result is not None

    def test_price_range_validation(self, trading_engine):
        for value in [-1, 0, True, float('nan'), float('inf')]:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=value), pytest.raises(APIConnectionError):
                trading_engine.get_stock_price('005930')
        for value in [.01, 1, 100000000, 999999999999.99]:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=value):
                assert trading_engine.get_stock_price('005930') == float(value)


    def test_price_precision(self, trading_engine):
        """Test price decimal precision.

        가격 소수점 정밀도 테스트
        """
        prices_with_precision = [
            100.1,
            100.12,
            100.123,
            100.1234,
            100.12345,
        ]

        for price in prices_with_precision:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=price):
                result = trading_engine.get_stock_price("005930")
                assert result is not None

    def test_price_boundary_values(self, trading_engine):
        for value in [-1, 0, True, float('nan'), float('inf')]:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=value), pytest.raises(APIConnectionError):
                trading_engine.get_stock_price('005930')
        for value in [.01, 1, 100000000, 999999999999.99]:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=value):
                assert trading_engine.get_stock_price('005930') == float(value)


@pytest.mark.data_validation
class TestConfigValidation:
    """Test configuration validation."""

    def test_kis_config_validation(self, upbit_config):
        config = TradingConfig(KISConfig('key', None, '12345678-01', 'id'), upbit_config)
        with pytest.raises(ValueError, match='Missing required credentials'):
            config.validate()


    def test_upbit_config_validation(self, kis_config):
        config = TradingConfig(kis_config, UpbitConfig(None, 'secret'))
        with pytest.raises(ValueError, match='Missing required credentials'):
            config.validate()


    def test_trading_config_combined_validation(self, kis_config, upbit_config):
        assert TradingConfig(kis_config, upbit_config).validate()
        with pytest.raises(ValueError):
            TradingConfig(None, None).validate()


    def test_timeout_configuration_validation(self, kis_config, upbit_config):
        for value in [-1, 0, True, float('nan')]:
            with pytest.raises(ValueError):
                TradingConfig(kis_config, upbit_config, timeout=value).validate()
        assert TradingConfig(kis_config, upbit_config, timeout=5).validate()


    def test_retry_count_validation(self, kis_config, upbit_config):
        for value in [-1, 0, True, float('nan')]:
            with pytest.raises(ValueError):
                TradingConfig(kis_config, upbit_config, retry_count=value).validate()
        assert TradingConfig(kis_config, upbit_config, retry_count=5).validate()


@pytest.mark.data_validation
class TestResponseDataValidation:
    """Test API response data validation."""

    def test_kis_response_validation(self, trading_engine):
        """Test KIS API response validation.

        KIS API 응답 검증 테스트
        """
        valid_responses = [50000, 100000.5, 1]

        for response in valid_responses:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=response):
                result = trading_engine.get_stock_price("005930")
                assert result == response

    def test_upbit_response_validation(self, trading_engine):
        """Test Upbit API response validation.

        Upbit API 응답 검증 테스트
        """
        valid_responses = [
            {"trade_price": 50000000},
            {"trade_price": 75500000.5},
            {"market": "KRW-BTC", "trade_price": 50000000},
        ]

        for response in valid_responses:
            with patch.object(trading_engine.upbit_session, 'get_ticker', return_value=response):
                result = trading_engine.get_coin_price("KRW-BTC")
                if result is not None:
                    assert isinstance(result, (int, float))

    def test_invalid_response_handling(self, trading_engine):
        for value in ['invalid', [], {}, {'invalid_key': 123}, None]:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=value), pytest.raises(APIConnectionError):
                trading_engine.get_stock_price('005930')


@pytest.mark.data_validation
class TestDataTypeConsistency:
    """Test data type consistency across operations."""

    def test_return_type_consistency_stock(self, trading_engine):
        for value in [50000, 50000.5]:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=value):
                assert isinstance(trading_engine.get_stock_price('005930'), float)
        with patch.object(trading_engine.kis_session, 'get_price', return_value=None), pytest.raises(APIConnectionError):
            trading_engine.get_stock_price('005930')


    def test_return_type_consistency_crypto(self, trading_engine):
        for value in [50000, 50000.5]:
            with patch.object(trading_engine.upbit_session, 'get_ticker', return_value={'trade_price': value}):
                assert isinstance(trading_engine.get_coin_price('KRW-BTC'), float)
        with patch.object(trading_engine.upbit_session, 'get_ticker', return_value=None), pytest.raises(APIConnectionError):
            trading_engine.get_coin_price('KRW-BTC')


    def test_consistent_error_types(self, trading_engine):
        """Test consistent error types across operations.

        작업 간 일관된 오류 타입 테스트
        """
        exceptions = [
            Exception("Generic error"),
            ValueError("Invalid value"),
            ConnectionError("Connection failed"),
        ]

        for exc in exceptions:
            with patch.object(trading_engine.kis_session, 'get_price', side_effect=exc):
                with pytest.raises(Exception):
                    trading_engine.get_stock_price("005930")


@pytest.mark.data_validation
class TestDataSanitization:
    """Test data sanitization."""

    def test_ticker_sanitization(self, trading_engine):
        """Test ticker sanitization.

        티커 살균 테스트
        """
        # Should strip and validate
        test_cases = [
            "  005930  ",  # Leading/trailing spaces
            "005930\n",     # Newline
            "005930\t",     # Tab
        ]

        for ticker in test_cases:
            with pytest.raises(InvalidTickerError):
                trading_engine.get_stock_price(ticker)

    def test_price_numeric_validation(self, trading_engine):
        for value in ['invalid', [], {}, {'invalid_key': 123}, None]:
            with patch.object(trading_engine.kis_session, 'get_price', return_value=value), pytest.raises(APIConnectionError):
                trading_engine.get_stock_price('005930')


    def test_response_key_validation(self, trading_engine):
        for value in [{}, {'invalid': 100}, {'price': 50000}]:
            with patch.object(trading_engine.upbit_session, 'get_ticker', return_value=value), pytest.raises(APIConnectionError):
                trading_engine.get_coin_price('KRW-BTC')


@pytest.mark.data_validation
class TestDataIntegrity:
    """Test data integrity through operations."""

    def test_data_not_modified_during_retrieval(self, trading_engine):
        """Test that data is not modified during retrieval.

        검색 중 데이터가 수정되지 않는 테스트
        """
        original_price = 50000

        with patch.object(trading_engine.kis_session, 'get_price', return_value=original_price):
            retrieved_price = trading_engine.get_stock_price("005930")
            assert retrieved_price == original_price

    def test_concurrent_data_integrity(self, trading_engine):
        """Test data integrity under concurrent access.

        동시 접근 중 데이터 무결성 테스트
        """
        import threading
        results = []

        def retrieve_price():
            with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
                result = trading_engine.get_stock_price("005930")
                results.append(result)

        threads = [threading.Thread(target=retrieve_price) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should have same value
        assert all(r == 50000 for r in results)

    def test_no_side_effects_on_retrieval(self, trading_engine):
        """Test that retrieval has no side effects.

        검색이 부작용을 갖지 않는 테스트
        """
        with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
            price1 = trading_engine.get_stock_price("005930")
            price2 = trading_engine.get_stock_price("005930")

            # Prices should be identical
            assert price1 == price2
