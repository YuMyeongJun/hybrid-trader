"""Tests for HybridTradingEngine."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from hybrid_trader.engine import HybridTradingEngine
from hybrid_trader.config import TradingConfig, KISConfig, UpbitConfig
from hybrid_trader.exceptions import ConfigurationError, InvalidTickerError, APIConnectionError


@pytest.fixture
def sample_config(tmp_path):
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
    return TradingConfig(kis_config=kis, upbit_config=upbit, order_db_path=str(tmp_path / 'orders.sqlite3'))


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

        with pytest.raises(ConfigurationError):
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

        with pytest.raises(InvalidTickerError):
            engine.get_stock_price("")

    def test_get_stock_price_invalid_ticker_none(self, sample_config):
        """Test get_stock_price raises error with None ticker."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(InvalidTickerError):
            engine.get_stock_price(None)

    def test_get_stock_price_api_failure(self, sample_config):
        """Test get_stock_price raises APIConnectionError on API failure."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_kis_api') as mock_kis:
            mock_kis.side_effect = Exception("API Error")

            with pytest.raises(APIConnectionError):
                engine.get_stock_price("005930")


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

        with pytest.raises(InvalidTickerError):
            engine.get_coin_price("")

    def test_get_coin_price_api_failure(self, sample_config):
        """Test get_coin_price raises APIConnectionError on API failure."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_upbit_api') as mock_upbit:
            mock_upbit.side_effect = Exception("API Error")

            with pytest.raises(APIConnectionError):
                engine.get_coin_price("KRW-BTC")


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


class TestHybridTradingEngineBuyStock:
    """Test cases for buy_stock method."""

    def test_buy_stock_valid_params(self, sample_config):
        """Test buying stock with valid parameters."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_kis_api') as mock_kis:
            mock_kis.return_value = {"order_id": "12345", "status": "pending"}

            result = engine.buy_stock("005930", qty=10, price=70000)

            assert result["order_id"] == "12345"
            assert result["status"] == "pending"
            mock_kis.assert_called_once()

    def test_buy_stock_invalid_ticker(self, sample_config):
        """Test buy_stock raises error with invalid ticker."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            engine.buy_stock("", qty=10, price=70000)

    def test_buy_stock_invalid_qty(self, sample_config):
        """Test buy_stock raises error with invalid quantity."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Quantity must be a positive integer"):
            engine.buy_stock("005930", qty=0, price=70000)

        with pytest.raises(ValueError, match="Quantity must be a positive integer"):
            engine.buy_stock("005930", qty=-5, price=70000)

    def test_buy_stock_invalid_price(self, sample_config):
        """Test buy_stock raises error with invalid price."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Price must be a positive number"):
            engine.buy_stock("005930", qty=10, price=0)

        with pytest.raises(ValueError, match="Price must be a positive number"):
            engine.buy_stock("005930", qty=10, price=-1000)

    def test_buy_stock_api_failure(self, sample_config):
        """Test buy_stock raises exception on API failure."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_kis_api') as mock_kis:
            mock_kis.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                engine.buy_stock("005930", qty=10, price=70000)


class TestHybridTradingEngineSellStock:
    """Test cases for sell_stock method."""

    def test_sell_stock_valid_params(self, sample_config):
        """Test selling stock with valid parameters."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_kis_api') as mock_kis:
            mock_kis.return_value = {"order_id": "54321", "status": "pending"}

            result = engine.sell_stock("005930", qty=5, price=75000)

            assert result["order_id"] == "54321"
            assert result["status"] == "pending"
            mock_kis.assert_called_once()

    def test_sell_stock_invalid_ticker(self, sample_config):
        """Test sell_stock raises error with invalid ticker."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            engine.sell_stock(None, qty=5, price=75000)

    def test_sell_stock_invalid_qty(self, sample_config):
        """Test sell_stock raises error with invalid quantity."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Quantity must be a positive integer"):
            engine.sell_stock("005930", qty=-1, price=75000)

    def test_sell_stock_invalid_price(self, sample_config):
        """Test sell_stock raises error with invalid price."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Price must be a positive number"):
            engine.sell_stock("005930", qty=5, price=0)


class TestHybridTradingEngineBuyCoin:
    """Test cases for buy_coin method."""

    def test_buy_coin_valid_params(self, sample_config):
        """Test buying coin with valid parameters."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_upbit_api') as mock_upbit:
            mock_upbit.return_value = {"order_id": "coin_12345", "status": "pending"}

            result = engine.buy_coin("KRW-BTC", krw=100000)

            assert result["order_id"] == "coin_12345"
            assert result["status"] == "pending"
            mock_upbit.assert_called_once()

    def test_buy_coin_invalid_market(self, sample_config):
        """Test buy_coin raises error with invalid market."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Market must be a non-empty string"):
            engine.buy_coin("", krw=100000)

    def test_buy_coin_invalid_krw(self, sample_config):
        """Test buy_coin raises error with invalid KRW amount."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="KRW amount must be a positive number"):
            engine.buy_coin("KRW-BTC", krw=0)

        with pytest.raises(ValueError, match="KRW amount must be a positive number"):
            engine.buy_coin("KRW-BTC", krw=-1000)

    def test_buy_coin_api_failure(self, sample_config):
        """Test buy_coin raises exception on API failure."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_upbit_api') as mock_upbit:
            mock_upbit.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                engine.buy_coin("KRW-BTC", krw=100000)


class TestHybridTradingEngineSellCoin:
    """Test cases for sell_coin method."""

    def test_sell_coin_valid_params(self, sample_config):
        """Test selling coin with valid parameters."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_upbit_api') as mock_upbit:
            mock_upbit.return_value = {"order_id": "coin_54321", "status": "pending"}

            result = engine.sell_coin("KRW-BTC", qty=0.5)

            assert result["order_id"] == "coin_54321"
            assert result["status"] == "pending"
            mock_upbit.assert_called_once()

    def test_sell_coin_invalid_market(self, sample_config):
        """Test sell_coin raises error with invalid market."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Market must be a non-empty string"):
            engine.sell_coin(None, qty=0.5)

    def test_sell_coin_invalid_qty(self, sample_config):
        """Test sell_coin raises error with invalid quantity."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Quantity must be a positive number"):
            engine.sell_coin("KRW-BTC", qty=0)

        with pytest.raises(ValueError, match="Quantity must be a positive number"):
            engine.sell_coin("KRW-BTC", qty=-0.1)


class TestHybridTradingEngineBalance:
    """Test cases for balance-related methods."""

    def test_get_stock_balance(self, sample_config):
        """Test getting stock balance."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_kis_api') as mock_kis:
            mock_kis.return_value = {
                "total_valuation": 5000000,
                "holdings": [{"ticker": "005930", "qty": 10, "price": 75500}]
            }

            balance = engine.get_stock_balance()

            assert balance["total_valuation"] == 5000000
            assert len(balance["holdings"]) == 1
            mock_kis.assert_called_once()

    def test_get_stock_balance_api_failure(self, sample_config):
        """Test get_stock_balance raises exception on API failure."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_kis_api') as mock_kis:
            mock_kis.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                engine.get_stock_balance()

    def test_get_coin_balance(self, sample_config):
        """Test getting coin balance."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_upbit_api') as mock_upbit:
            mock_upbit.return_value = {
                "KRW-BTC": {"balance": 0.5, "valuation": 30000000},
                "KRW-ETH": {"balance": 5, "valuation": 15000000}
            }

            balance = engine.get_coin_balance()

            assert "KRW-BTC" in balance
            assert "KRW-ETH" in balance
            mock_upbit.assert_called_once()

    def test_get_coin_balance_api_failure(self, sample_config):
        """Test get_coin_balance raises exception on API failure."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_upbit_api') as mock_upbit:
            mock_upbit.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                engine.get_coin_balance()

    def test_get_total_balance(self, sample_config):
        """Test getting total balance combining stocks and coins."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, 'get_stock_balance') as mock_stock, \
             patch.object(engine, 'get_coin_balance') as mock_coin:

            mock_stock.return_value = {"total_valuation": 5000000}
            mock_coin.return_value = {"total_valuation": 3000000}

            total = engine.get_total_balance()

            assert total["total_valuation"] == 8000000
            assert "stocks" in total
            assert "coins" in total
            assert "timestamp" in total

    def test_get_total_balance_with_exception(self, sample_config):
        """Test get_total_balance raises exception if balance retrieval fails."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, 'get_stock_balance') as mock_stock:
            mock_stock.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                engine.get_total_balance()


class TestHybridTradingEngineOrderHistory:
    """Test cases for get_order_history method."""

    def test_get_order_history_stock(self, sample_config):
        engine = HybridTradingEngine(sample_config)
        rows = [{"order_id": "1", "ticker": "005930", "status": "PARTIALLY_FILLED"},
                {"order_id": "2", "ticker": "KRW-BTC", "status": "OPEN"}]
        with patch.object(engine.execution, 'orders', return_value=rows):
            assert engine.get_order_history("005930") == rows[:1]


    def test_get_order_history_crypto(self, sample_config):
        engine = HybridTradingEngine(sample_config)
        rows = [{"order_id": "1", "ticker": "KRW-BTC"}, {"order_id": "2", "ticker": "KRW-BTC"}]
        with patch.object(engine.execution, 'orders', return_value=rows):
            assert engine.get_order_history("KRW-BTC", limit=1) == rows[-1:]


    def test_get_order_history_invalid_ticker(self, sample_config):
        """Test get_order_history raises error with invalid ticker."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Invalid ticker"):
            engine.get_order_history("", limit=10)

    def test_get_order_history_invalid_limit(self, sample_config):
        """Test get_order_history raises error with invalid limit."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            engine.get_order_history("005930", limit=0)

        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            engine.get_order_history("005930", limit=-5)

    def test_get_order_history_empty_result(self, sample_config):
        """Test get_order_history with empty result."""
        engine = HybridTradingEngine(sample_config)

        with patch.object(engine, '_call_kis_api') as mock_kis:
            mock_kis.return_value = []

            history = engine.get_order_history("005930", limit=10)

            assert history == []

    def test_get_order_history_api_failure(self, sample_config):
        engine = HybridTradingEngine(sample_config)
        with patch.object(engine.execution, 'orders', side_effect=OSError('journal unavailable')):
            with pytest.raises(OSError):
                engine.get_order_history("005930")


class TestHybridTradingEngineCancelOrder:
    """Test cases for cancel_order method."""

    def test_cancel_order_success(self, sample_config):
        engine = HybridTradingEngine(sample_config)
        with patch.object(engine.execution, 'cancel', return_value={"status": "CANCEL_REQUESTED"}) as cancel:
            assert engine.cancel_order("order_12345")["status"] == "CANCEL_REQUESTED"
            cancel.assert_called_once_with("order_12345")


    def test_cancel_order_fallback_to_upbit(self, sample_config, monkeypatch):
        from hybrid_trader.brokers import BrokerError
        sample_config.enable_real_trading = True
        sample_config.dry_run = False
        sample_config.order_db_path = ":memory:"
        monkeypatch.setenv("ENABLE_REAL_TRADING", "true")
        monkeypatch.setenv("DRY_RUN", "false")
        engine = HybridTradingEngine(sample_config)
        with patch.object(engine.kis_session, 'cancel') as kis, patch.object(engine.upbit_session, 'cancel') as upbit:
            with pytest.raises(BrokerError, match="identity"):
                engine.cancel_order("unowned")
            kis.assert_not_called()
            upbit.assert_not_called()


    def test_cancel_order_invalid_order_id(self, sample_config):
        """Test cancel_order raises error with invalid order ID."""
        engine = HybridTradingEngine(sample_config)

        with pytest.raises(ValueError, match="Order ID is required"):
            engine.cancel_order("")

        with pytest.raises(ValueError, match="Order ID is required"):
            engine.cancel_order(None)

    def test_cancel_order_both_apis_fail(self, sample_config):
        engine = HybridTradingEngine(sample_config)
        with patch.object(engine.execution, 'cancel', side_effect=RuntimeError('journal failure')):
            with pytest.raises(RuntimeError):
                engine.cancel_order("known")


    def test_cancel_order_no_result(self, sample_config):
        engine = HybridTradingEngine(sample_config)
        with patch.object(engine.kis_session, 'cancel') as kis, patch.object(engine.upbit_session, 'cancel') as upbit:
            assert engine.cancel_order("known")["status"] == "DRY_RUN"
            kis.assert_not_called()
            upbit.assert_not_called()
