from hybrid_trader.exceptions import APIConnectionError
"""Edge case tests for Hybrid Trader.

This module tests edge cases and boundary conditions that might occur
during normal operation of the trading engine.

엣지 케이스 및 경계 조건 테스트를 수행합니다.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from hybrid_trader.engine import HybridTradingEngine
from hybrid_trader.exceptions import (
    InvalidTickerError,
    APIConnectionError,
    SessionNotInitializedError,
)


@pytest.mark.edge_case
class TestTickerEdgeCases:
    """Test edge cases with ticker symbols."""

    def test_empty_ticker_string(self, trading_engine):
        """Test handling of empty ticker string.

        빈 티커 문자열 처리 테스트
        """
        with pytest.raises(InvalidTickerError):
            trading_engine.get_stock_price("")

    def test_none_ticker(self, trading_engine):
        """Test handling of None ticker.

        None 티커 처리 테스트
        """
        with pytest.raises((InvalidTickerError, TypeError)):
            trading_engine.get_stock_price(None)

    def test_very_long_ticker(self, trading_engine):
        """Test handling of very long ticker string.

        매우 긴 티커 문자열 처리 테스트
        """
        long_ticker = "A" * 1000
        with pytest.raises(InvalidTickerError):
            trading_engine.get_stock_price(long_ticker)

    def test_special_characters_in_ticker(self, trading_engine):
        """Test handling of special characters in ticker.

        티커의 특수문자 처리 테스트
        """
        special_tickers = ["005930!", "@005930", "005930#", "005930$"]
        for ticker in special_tickers:
            with pytest.raises(InvalidTickerError):
                trading_engine.get_stock_price(ticker)

    def test_unicode_ticker(self, trading_engine):
        """Test handling of unicode characters in ticker.

        티커의 유니코드 문자 처리 테스트
        """
        with pytest.raises(InvalidTickerError):
            trading_engine.get_stock_price("삼성전자")

    def test_lowercase_ticker_code(self, trading_engine):
        """Test handling of lowercase ticker codes.

        소문자 티커 코드 처리 테스트
        """
        with pytest.raises(InvalidTickerError):
            trading_engine.get_stock_price("krw-btc")

    def test_ticker_with_spaces(self, trading_engine):
        """Test handling of ticker with spaces.

        공백이 있는 티커 처리 테스트
        """
        with pytest.raises(InvalidTickerError):
            trading_engine.get_stock_price("KRW BTC")

    def test_ticker_with_leading_trailing_spaces(self, trading_engine):
        """Test handling of ticker with leading/trailing spaces.

        선행/후행 공백이 있는 티커 처리 테스트
        """
        # Should either trim and work or raise error
        with pytest.raises(InvalidTickerError):
            trading_engine.get_stock_price("  005930  ")


@pytest.mark.edge_case
class TestPriceEdgeCases:
    """Test edge cases with price values."""

    def test_zero_price(self, trading_engine):
        with patch.object(trading_engine.kis_session, 'get_price', return_value=0), pytest.raises(APIConnectionError):
            trading_engine.get_stock_price('005930')


    def test_negative_price(self, trading_engine):
        with patch.object(trading_engine.kis_session, 'get_price', return_value=-1), pytest.raises(APIConnectionError):
            trading_engine.get_stock_price('005930')


    def test_extremely_large_price(self, trading_engine):
        """Test handling of extremely large price values.

        매우 큰 가격값 처리 테스트
        """
        huge_price = 999_999_999_999.99
        with patch.object(trading_engine.kis_session, 'get_price', return_value=huge_price):
            result = trading_engine.get_stock_price("005930")
            assert result == huge_price

    def test_fractional_price(self, trading_engine):
        """Test handling of fractional price values.

        소수 가격값 처리 테스트
        """
        fractional_price = 100.5555
        with patch.object(trading_engine.kis_session, 'get_price', return_value=fractional_price):
            result = trading_engine.get_stock_price("005930")
            assert result == fractional_price

    def test_decimal_precision(self, trading_engine):
        """Test decimal precision handling.

        소수점 정밀도 처리 테스트
        """
        decimal_price = Decimal("50000.123456789")
        with patch.object(trading_engine.kis_session, 'get_price', return_value=float(decimal_price)):
            result = trading_engine.get_stock_price("005930")
            assert result is not None


@pytest.mark.edge_case
class TestNullAndEmptyEdgeCases:
    """Test null and empty value edge cases."""

    def test_none_return_from_api(self, trading_engine):
        with patch.object(trading_engine.kis_session, 'get_price', return_value=None), pytest.raises(APIConnectionError):
            trading_engine.get_stock_price('005930')


    def test_empty_response_from_api(self, trading_engine):
        with patch.object(trading_engine.kis_session, 'get_price', return_value=""), pytest.raises(APIConnectionError):
            trading_engine.get_stock_price('005930')


    def test_empty_dict_response(self, trading_engine):
        with patch.object(trading_engine.kis_session, 'get_price', return_value={}), pytest.raises(APIConnectionError):
            trading_engine.get_stock_price('005930')


@pytest.mark.edge_case
class TestSessionEdgeCases:
    """Test edge cases related to session management."""

    def test_multiple_initializations(self, trading_config):
        """Test multiple engine initializations.

        여러 엔진 초기화 테스트
        """
        engines = [HybridTradingEngine(trading_config) for _ in range(5)]
        assert len(engines) == 5
        assert all(e.config == trading_config for e in engines)

    def test_reusing_closed_engine(self, trading_engine):
        trading_engine.close()
        with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
            assert trading_engine.get_stock_price('005930') == 50000


    def test_close_without_initialization(self, trading_config):
        """Test closing engine that was never fully initialized.

        초기화되지 않은 엔진 종료 테스트
        """
        engine = HybridTradingEngine(trading_config)
        # Should not raise
        engine.close()
        engine.close()  # Double close should be safe


@pytest.mark.edge_case
class TestBoundaryConditions:
    """Test boundary conditions."""

    def test_maximum_decimal_places(self, trading_engine):
        """Test handling of maximum decimal places.

        최대 소수점 자리 처리 테스트
        """
        price = 100.123456789123456789
        with patch.object(trading_engine.kis_session, 'get_price', return_value=price):
            result = trading_engine.get_stock_price("005930")
            assert result is not None

    def test_scientific_notation_price(self, trading_engine):
        """Test handling of scientific notation in prices.

        가격의 과학적 표기법 처리 테스트
        """
        scientific_price = 1e6  # 1,000,000
        with patch.object(trading_engine.kis_session, 'get_price', return_value=scientific_price):
            result = trading_engine.get_stock_price("005930")
            assert result == scientific_price

    def test_integer_overflow_values(self, trading_engine):
        value = 2 ** 63 - 1
        with patch.object(trading_engine.kis_session, 'get_price', return_value=value):
            assert trading_engine.get_stock_price('005930') == float(value)
        with patch.object(trading_engine.kis_session, 'get_price', return_value=10 ** 1000), pytest.raises(APIConnectionError):
            trading_engine.get_stock_price('005930')


@pytest.mark.edge_case
class TestConcurrencyEdgeCases:
    """Test concurrency edge cases."""

    def test_concurrent_access_to_shared_session(self, trading_engine):
        """Test concurrent access to shared session.

        공유 세션에 동시 접근 테스트
        """
        import threading
        results = []

        def worker():
            with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
                result = trading_engine.get_stock_price("005930")
                results.append(result)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 50000 for r in results)

    def test_race_condition_on_session_creation(self, trading_config):
        """Test for race conditions during session creation.

        세션 생성 중 레이스 조건 테스트
        """
        import threading
        engines = []

        def create_engine():
            engine = HybridTradingEngine(trading_config)
            engines.append(engine)

        threads = [threading.Thread(target=create_engine) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(engines) == 5


@pytest.mark.edge_case
class TestTypeCoercionEdgeCases:
    """Test type coercion edge cases."""

    def test_price_as_string(self, trading_engine):
        """Test handling of price returned as string.

        문자열로 반환된 가격 처리 테스트
        """
        with patch.object(trading_engine.kis_session, 'get_price', return_value="50000"):
            result = trading_engine.get_stock_price("005930")
            # Should handle or raise appropriate error
            assert result is not None

    def test_price_as_boolean(self, trading_engine):
        with patch.object(trading_engine.kis_session, 'get_price', return_value=True), pytest.raises(APIConnectionError):
            trading_engine.get_stock_price('005930')


    def test_price_as_list(self, trading_engine):
        with patch.object(trading_engine.kis_session, 'get_price', return_value=[50000]), pytest.raises(APIConnectionError):
            trading_engine.get_stock_price('005930')
