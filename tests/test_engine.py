"""Tests for HybridTradingEngine."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from hybrid_trader.engine import HybridTradingEngine
from hybrid_trader.config import TradingConfig, KISConfig, UpbitConfig


@pytest.fixture
def sample_config():
    """Fixture providing sample trading configuration."""
    kis = KISConfig(
        app_key="test_app_key",
        secret_key="test_secret_key",
        account_number="1234-5678",
        hts_id="test_hts_id"
    )
    upbit = UpbitConfig(
        access_key="test_access_key",
        secret_key="test_secret_key"
    )
    return TradingConfig(kis_config=kis, upbit_config=upbit)


class TestHybridTradingEngineInitialization:
    """Test cases for HybridTradingEngine initialization."""

    def test_engine_initialization(self, sample_config):
        """Test engine initialization with valid config."""
        engine = HybridTradingEngine(sample_config)

        assert engine.config == sample_config
        assert engine._kis_session is None
        assert engine._upbit_session is None

    def test_engine_initialization_with_invalid_config(self):
        """Test engine initialization fails with invalid config."""
        kis = KISConfig(
            app_key="",
            secret_key="secret",
            account_number="1234-5678",
            hts_id="hts"
        )
        upbit = UpbitConfig(
            access_key="key",
            secret_key="secret"
        )
        config = TradingConfig(kis_config=kis, upbit_config=upbit)

        with pytest.raises(ValueError):
            HybridTradingEngine(config)


class TestHybridTradingEngineStockPrice:
    """Test cases for get_stock_price method."""

    def test_get_stock_price_valid_ticker(self, sample_config):
        """Test getting stock price with valid ticker."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_kis_api') as mock_kis:
            mock_kis.return_value = 75500.0

            price = engine.get_stock_price("005930")

            assert price == 75500.0
            mock_kis.assert_called_once()

    def test_get_stock_price_invalid_ticker_empty_string(self, sample_config):
        """Test get_stock_price raises error with empty ticker."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            engine.get_stock_price("")

    def test_get_stock_price_invalid_ticker_none(self, sample_config):
        """Test get_stock_price raises error with None ticker."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            engine.get_stock_price(None)

    def test_get_stock_price_api_failure(self, sample_config):
        """Test get_stock_price returns None on API failure."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_kis_api') as mock_kis:
            mock_kis.side_effect = Exception("API Error")

            price = engine.get_stock_price("005930")

            assert price is None


class TestHybridTradingEngineCoinPrice:
    """Test cases for get_coin_price method."""

    def test_get_coin_price_valid_ticker(self, sample_config):
        """Test getting crypto price with valid ticker."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_upbit_api') as mock_upbit:
            mock_upbit.return_value = 65500000.0

            price = engine.get_coin_price("KRW-BTC")

            assert price == 65500000.0
            mock_upbit.assert_called_once()

    def test_get_coin_price_invalid_ticker_empty_string(self, sample_config):
        """Test get_coin_price raises error with empty ticker."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            engine.get_coin_price("")

    def test_get_coin_price_api_failure(self, sample_config):
        """Test get_coin_price returns None on API failure."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_upbit_api') as mock_upbit:
            mock_upbit.side_effect = Exception("API Error")

            price = engine.get_coin_price("KRW-BTC")

            assert price is None


class TestHybridTradingEngineContextManager:
    """Test cases for context manager functionality."""

    def test_context_manager_enter_exit(self, sample_config):
        """Test engine works as context manager."""
        with HybridTradingEngine(sample_config) as engine:
            assert engine is not None
            assert engine.config == sample_config

    def test_context_manager_closes_sessions(self, sample_config):
        """Test context manager properly closes sessions."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, 'close') as mock_close:
            with engine:
                pass

            mock_close.assert_called_once()


class TestHybridTradingEngineAPIRetry:
    """Test cases for API retry logic."""

    def test_kis_api_retry_on_failure(self, sample_config):
        """Test KIS API retries on failure."""
        engine = HybridTradingEngine(sample_config)

        with patch('time.sleep'):
            with pytest.raises(Exception):
                engine._call_kis_api(
                    endpoint="/stock/price",
                    params={"ticker": "005930"}
                )

    def test_upbit_api_retry_on_failure(self, sample_config):
        """Test Upbit API retries on failure."""
        engine = HybridTradingEngine(sample_config)

        with patch('time.sleep'):
            with pytest.raises(Exception):
                engine._call_upbit_api(
                    endpoint="/ticker",
                    params={"markets": "KRW-BTC"}
                )


class TestHybridTradingEngineIntegration:
    """Integration tests for HybridTradingEngine."""

    def test_fetch_multiple_prices(self, sample_config):
        """Test fetching multiple prices in sequence."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_kis_api') as mock_kis, \
             patch.object(engine, '_call_upbit_api') as mock_upbit:

            mock_kis.return_value = 75500.0
            mock_upbit.return_value = 65500000.0

            stock_price = engine.get_stock_price("005930")
            crypto_price = engine.get_coin_price("KRW-BTC")

            assert stock_price == 75500.0
            assert crypto_price == 65500000.0
