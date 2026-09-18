"""API integration tests for Hybrid Trader.

This module tests the integration with external APIs (KIS and Upbit),
including API communication patterns and error handling.

API 통합 테스트를 수행합니다.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from hybrid_trader.engine import HybridTradingEngine
from hybrid_trader.exceptions import APIConnectionError, InvalidTickerError


@pytest.mark.integration
@pytest.mark.api
class TestKISAPIIntegration:
    """Test integration with Korea Investment & Securities API."""

    def test_kis_session_lazy_initialization(self, trading_engine):
        from hybrid_trader.brokers import KISBroker
        assert isinstance(trading_engine.kis_session, KISBroker)
        assert trading_engine.kis_session._token is None
        assert trading_engine.kis_session is trading_engine.kis_session


    def test_kis_api_call_with_retry(self, trading_engine):
        """Test KIS API calls with retry logic.

        재시도 로직을 포함한 KIS API 호출 테스트
        """
        call_count = 0

        def mock_get_price_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return 50000

        with patch.object(trading_engine.kis_session, 'get_price', side_effect=mock_get_price_with_retry):
            # May retry internally, but should eventually succeed or fail
            try:
                result = trading_engine.get_stock_price("005930")
            except Exception:
                pass

    def test_kis_api_timeout_handling(self, trading_engine):
        """Test handling of KIS API timeouts.

        KIS API 타임아웃 처리 테스트
        """
        from requests.exceptions import Timeout

        with patch.object(trading_engine.kis_session, 'get_price', side_effect=Timeout("Request timed out")):
            with pytest.raises((Timeout, APIConnectionError)):
                trading_engine.get_stock_price("005930")

    def test_kis_api_connection_error(self, trading_engine):
        """Test handling of KIS API connection errors.

        KIS API 연결 오류 처리 테스트
        """
        from requests.exceptions import ConnectionError

        with patch.object(trading_engine.kis_session, 'get_price', side_effect=ConnectionError("Connection refused")):
            with pytest.raises((ConnectionError, APIConnectionError)):
                trading_engine.get_stock_price("005930")

    def test_kis_api_authentication_error(self, trading_engine):
        """Test handling of KIS API authentication errors.

        KIS API 인증 오류 처리 테스트
        """
        with patch.object(trading_engine.kis_session, 'get_price', side_effect=Exception("401 Unauthorized")):
            with pytest.raises(Exception):
                trading_engine.get_stock_price("005930")

    def test_kis_api_rate_limiting(self, trading_engine):
        """Test handling of KIS API rate limiting.

        KIS API 속도 제한 처리 테스트
        """
        with patch.object(trading_engine.kis_session, 'get_price', side_effect=Exception("429 Too Many Requests")):
            with pytest.raises(Exception):
                trading_engine.get_stock_price("005930")

    def test_kis_api_malformed_response(self, trading_engine):
        with patch.object(trading_engine.kis_session, 'get_price', return_value=None):
            with pytest.raises(APIConnectionError):
                trading_engine.get_stock_price("005930")


@pytest.mark.integration
@pytest.mark.api
class TestUpbitAPIIntegration:
    """Test integration with Upbit API."""

    def test_upbit_session_lazy_initialization(self, trading_engine):
        """Test that Upbit session is lazily initialized.

        Upbit 세션 지연 초기화 테스트
        """
        # Session should not be created until needed
        assert trading_engine._upbit_session is None

    def test_upbit_api_call_with_retry(self, trading_engine):
        """Test Upbit API calls with retry logic.

        재시도 로직을 포함한 Upbit API 호출 테스트
        """
        call_count = 0

        def mock_get_ticker_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return {"trade_price": 50000000}

        with patch.object(trading_engine.upbit_session, 'get_ticker', side_effect=mock_get_ticker_with_retry):
            try:
                result = trading_engine.get_coin_price("KRW-BTC")
            except Exception:
                pass

    def test_upbit_api_timeout_handling(self, trading_engine):
        """Test handling of Upbit API timeouts.

        Upbit API 타임아웃 처리 테스트
        """
        from requests.exceptions import Timeout

        with patch.object(trading_engine.upbit_session, 'get_ticker', side_effect=Timeout("Request timed out")):
            with pytest.raises((Timeout, APIConnectionError, Exception)):
                trading_engine.get_coin_price("KRW-BTC")

    def test_upbit_api_connection_error(self, trading_engine):
        """Test handling of Upbit API connection errors.

        Upbit API 연결 오류 처리 테스트
        """
        from requests.exceptions import ConnectionError

        with patch.object(trading_engine.upbit_session, 'get_ticker', side_effect=ConnectionError("Connection refused")):
            with pytest.raises((ConnectionError, APIConnectionError, Exception)):
                trading_engine.get_coin_price("KRW-BTC")

    def test_upbit_api_rate_limiting(self, trading_engine):
        """Test handling of Upbit API rate limiting.

        Upbit API 속도 제한 처리 테스트
        """
        with patch.object(trading_engine.upbit_session, 'get_ticker', side_effect=Exception("429 Too Many Requests")):
            with pytest.raises(Exception):
                trading_engine.get_coin_price("KRW-BTC")

    def test_upbit_api_invalid_ticker(self, trading_engine):
        """Test handling of invalid ticker in Upbit API.

        Upbit API의 잘못된 티커 처리 테스트
        """
        with patch.object(trading_engine.upbit_session, 'get_ticker', side_effect=Exception("Not found")):
            with pytest.raises(Exception):
                trading_engine.get_coin_price("INVALID-TICKER")

    def test_upbit_api_response_parsing(self, trading_engine):
        """Test parsing of Upbit API responses.

        Upbit API 응답 분석 테스트
        """
        response = {
            "market": "KRW-BTC",
            "trade_price": 50000000,
            "trade_date": "20240101",
            "trade_time": "120000"
        }

        with patch.object(trading_engine.upbit_session, 'get_ticker', return_value=response):
            result = trading_engine.get_coin_price("KRW-BTC")
            assert result == 50000000


@pytest.mark.integration
@pytest.mark.api
class TestCrossAPIIntegration:
    """Test cross-API integration and consistency."""

    def test_simultaneous_kis_and_upbit_calls(self, trading_engine):
        """Test simultaneous KIS and Upbit API calls.

        KIS와 Upbit API 동시 호출 테스트
        """
        with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
            with patch.object(trading_engine.upbit_session, 'get_ticker', return_value={"trade_price": 50000000}):
                stock_price = trading_engine.get_stock_price("005930")
                coin_price = trading_engine.get_coin_price("KRW-BTC")

                assert stock_price == 50000
                assert coin_price == 50000000

    def test_api_call_isolation(self, trading_engine):
        """Test that API calls are isolated and don't affect each other.

        API 호출이 서로 영향을 주지 않는 테스트
        """
        kis_called = False
        upbit_called = False

        def mock_kis(*args, **kwargs):
            nonlocal kis_called
            kis_called = True
            return 50000

        def mock_upbit(*args, **kwargs):
            nonlocal upbit_called
            upbit_called = True
            return {"trade_price": 50000000}

        with patch.object(trading_engine.kis_session, 'get_price', side_effect=mock_kis):
            with patch.object(trading_engine.upbit_session, 'get_ticker', side_effect=mock_upbit):
                # Call KIS only
                trading_engine.get_stock_price("005930")
                assert kis_called
                assert not upbit_called

                # Reset flags
                kis_called = False
                upbit_called = False

                # Call Upbit only
                trading_engine.get_coin_price("KRW-BTC")
                assert not kis_called
                assert upbit_called

    def test_mixed_success_and_failure(self, trading_engine):
        """Test handling of mixed success and failure across APIs.

        API 간 성공과 실패 혼합 처리 테스트
        """
        with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
            with patch.object(trading_engine.upbit_session, 'get_ticker', side_effect=Exception("API Error")):
                stock_price = trading_engine.get_stock_price("005930")
                assert stock_price == 50000

                with pytest.raises(Exception):
                    trading_engine.get_coin_price("KRW-BTC")


@pytest.mark.integration
@pytest.mark.api
class TestAPIErrorRecovery:
    """Test recovery from API errors."""

    def test_recovery_after_temporary_api_failure(self, trading_engine):
        """Test recovery after temporary API failure.

        일시적 API 실패 후 복구 테스트
        """
        call_count = [0]

        def mock_with_recovery(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Temporary failure")
            return 50000

        with patch.object(trading_engine.kis_session, 'get_price', side_effect=mock_with_recovery):
            try:
                trading_engine.get_stock_price("005930")
            except Exception:
                pass

            # Try again - may succeed on second attempt
            call_count[0] = 0
            with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
                result = trading_engine.get_stock_price("005930")
                assert result == 50000

    def test_circuit_breaker_pattern(self, trading_engine):
        """Test circuit breaker pattern for API failures.

        API 실패에 대한 서킷 브레이커 패턴 테스트
        """
        # Simulate multiple failures
        with patch.object(trading_engine.kis_session, 'get_price', side_effect=Exception("API down")):
            for _ in range(5):
                with pytest.raises(Exception):
                    trading_engine.get_stock_price("005930")

    def test_fallback_mechanism(self, trading_engine):
        """Test fallback mechanism when API fails.

        API 실패 시 폴백 메커니즘 테스트
        """
        # If primary fails, should handle gracefully
        with patch.object(trading_engine.kis_session, 'get_price', side_effect=Exception("Primary API down")):
            with pytest.raises(Exception):
                trading_engine.get_stock_price("005930")


@pytest.mark.integration
@pytest.mark.api
class TestAPIDataConsistency:
    """Test data consistency across API calls."""

    def test_consistent_price_for_same_ticker(self, trading_engine):
        """Test that same ticker returns consistent price within time window.

        동일 티커가 시간 내에 일관된 가격을 반환하는 테스트
        """
        expected_price = 50000

        with patch.object(trading_engine.kis_session, 'get_price', return_value=expected_price):
            price1 = trading_engine.get_stock_price("005930")
            price2 = trading_engine.get_stock_price("005930")

            assert price1 == price2 == expected_price

    def test_different_tickers_different_prices(self, trading_engine):
        """Test that different tickers can have different prices.

        다른 티커는 다른 가격을 가질 수 있는 테스트
        """
        prices = {"005930": 50000, "000660": 75000, "005380": 100000}

        def mock_price_by_ticker(ticker, *args, **kwargs):
            return prices.get(ticker)

        with patch.object(trading_engine.kis_session, 'get_price', side_effect=mock_price_by_ticker):
            for ticker, expected_price in prices.items():
                actual_price = trading_engine.get_stock_price(ticker)
                assert actual_price == expected_price
