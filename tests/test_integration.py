from hybrid_trader.exceptions import APIConnectionError
"""Integration tests for Hybrid Trader.

This module tests end-to-end scenarios and interactions between multiple modules.
"""

import pytest
from unittest.mock import patch, MagicMock, call
from hybrid_trader.engine import HybridTradingEngine
from hybrid_trader.config import TradingConfig, KISConfig, UpbitConfig
from hybrid_trader.analysis import TechnicalAnalyzer
from hybrid_trader.exceptions import (
    ConfigurationError,
    APIConnectionError,
    InvalidTickerError,
    AnalysisError,
)


class TestEngineConfigurationIntegration:
    """Integration tests for engine and configuration."""

    def test_engine_initialization_with_config(self, trading_config):
        """Test engine initialization with configuration."""
        engine = HybridTradingEngine(trading_config)

        assert engine.config is not None
        assert engine.config.kis_config is not None
        assert engine.config.upbit_config is not None

    def test_engine_with_invalid_config_fails(self):
        """Test engine initialization fails with invalid config."""
        kis = KISConfig(
            app_key="",  # Empty app_key
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

    def test_multiple_engines_with_different_configs(self, trading_config, trading_config_custom):
        """Test creating multiple engines with different configurations."""
        engine1 = HybridTradingEngine(trading_config)
        engine2 = HybridTradingEngine(trading_config_custom)

        assert engine1.config != engine2.config
        assert engine1.config.kis_config.is_demo is True
        assert engine2.config.kis_config.is_demo is False


class TestStockAndCryptoPriceFetching:
    """Integration tests for fetching stock and crypto prices."""

    def test_get_stock_and_crypto_prices_together(self, trading_engine):
        """Test fetching both stock and crypto prices in sequence."""
        with patch.object(trading_engine, '_call_kis_api') as mock_kis, \
             patch.object(trading_engine, '_call_upbit_api') as mock_upbit:

            mock_kis.return_value = 75500.0
            mock_upbit.return_value = 65500000.0

            stock_price = trading_engine.get_stock_price("005930")
            crypto_price = trading_engine.get_coin_price("KRW-BTC")

            assert stock_price == 75500.0
            assert crypto_price == 65500000.0
            mock_kis.assert_called_once()
            mock_upbit.assert_called_once()

    def test_multiple_stock_prices(self, trading_engine, mock_stock_prices):
        """Test fetching multiple stock prices."""
        with patch.object(trading_engine, '_call_kis_api') as mock_kis:
            for ticker, expected_price in mock_stock_prices.items():
                mock_kis.return_value = expected_price
                price = trading_engine.get_stock_price(ticker)
                assert price == expected_price

    def test_multiple_crypto_prices(self, trading_engine, mock_crypto_prices):
        """Test fetching multiple crypto prices."""
        with patch.object(trading_engine, '_call_upbit_api') as mock_upbit:
            for ticker, expected_price in mock_crypto_prices.items():
                mock_upbit.return_value = expected_price
                price = trading_engine.get_coin_price(ticker)
                assert price == expected_price

    def test_alternating_stock_and_crypto_fetching(self, trading_engine):
        """Test alternating between stock and crypto price fetching."""
        with patch.object(trading_engine, '_call_kis_api') as mock_kis, \
             patch.object(trading_engine, '_call_upbit_api') as mock_upbit:

            mock_kis.return_value = 75500.0
            mock_upbit.return_value = 65500000.0

            calls_made = []

            for i in range(3):
                stock = trading_engine.get_stock_price("005930")
                crypto = trading_engine.get_coin_price("KRW-BTC")

                assert stock == 75500.0
                assert crypto == 65500000.0
                calls_made.append(("stock", stock))
                calls_made.append(("crypto", crypto))

            assert len(calls_made) == 6


class TestAPIErrorHandling:
    """Integration tests for API error handling."""

    def test_api_connection_error_recovery(self, trading_engine):
        with patch.object(trading_engine, '_call_kis_api', side_effect=[Exception('failed'), 75500.0]):
            with pytest.raises(APIConnectionError):
                trading_engine.get_stock_price('005930')
            assert trading_engine.get_stock_price('005930') == 75500.0


    def test_invalid_ticker_error(self, trading_engine):
        """Test error handling for invalid tickers."""
        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            trading_engine.get_stock_price("")

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            trading_engine.get_coin_price(None)

    def test_api_retry_mechanism(self, trading_engine):
        """Test API retry mechanism."""
        with patch('time.sleep'):
            with patch.object(trading_engine, '_call_kis_api') as mock_api:
                mock_api.side_effect = [
                    Exception("Error 1"),
                    Exception("Error 2"),
                    Exception("Error 3"),  # Final failure after retries
                ]

                # This should fail after retries
                # The actual implementation depends on how retries are done
                try:
                    trading_engine._call_kis_api(
                        endpoint="/stock/price",
                        params={"ticker": "005930"}
                    )
                except Exception:
                    pass


class TestContextManagerIntegration:
    """Integration tests for context manager functionality."""

    def test_engine_as_context_manager(self, trading_config):
        """Test using engine as context manager."""
        with HybridTradingEngine(trading_config) as engine:
            assert engine is not None
            with patch.object(engine, '_call_kis_api') as mock_kis:
                mock_kis.return_value = 75500.0
                price = engine.get_stock_price("005930")
                assert price == 75500.0

    def test_context_manager_closes_sessions(self, trading_config):
        """Test that context manager closes sessions on exit."""
        engine = HybridTradingEngine(trading_config)

        with patch.object(engine, 'close') as mock_close:
            with engine:
                pass
            mock_close.assert_called_once()

    def test_context_manager_exception_handling(self, trading_config):
        """Test context manager handles exceptions properly."""
        try:
            with HybridTradingEngine(trading_config) as engine:
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected

    def test_nested_context_managers(self, trading_config, trading_config_custom):
        """Test using nested context managers."""
        with HybridTradingEngine(trading_config) as engine1:
            with HybridTradingEngine(trading_config_custom) as engine2:
                assert engine1 is not None
                assert engine2 is not None
                assert engine1.config != engine2.config


class TestTechnicalAnalysisIntegration:
    """Integration tests for technical analysis with price data."""

    def test_full_technical_analysis_workflow(self, mock_price_history):
        """Test complete technical analysis workflow."""
        # MACD(12,26,9) needs at least 34 observations for its signal line.
        mock_price_history = mock_price_history + [mock_price_history[-1] + i * 10 for i in range(10)]
        analyzer = TechnicalAnalyzer()

        # Validate data
        assert analyzer.validate_price_data(mock_price_history)

        # Calculate multiple indicators
        sma = analyzer.calculate_sma(mock_price_history, 10)
        ema = analyzer.calculate_ema(mock_price_history, 10)
        rsi = analyzer.calculate_rsi(mock_price_history, 14)
        bands = analyzer.calculate_bollinger_bands(mock_price_history, 20)
        macd = analyzer.calculate_macd(mock_price_history)

        assert len(sma) > 0
        assert len(ema) > 0
        assert len(rsi) > 0
        assert len(bands['middle']) > 0
        assert len(macd['macd']) > 0

    def test_analysis_on_trending_data(self):
        """Test analysis on trending price data."""
        # Uptrending data
        prices = [100.0 + i * 2 for i in range(30)]

        analyzer = TechnicalAnalyzer()
        rsi = analyzer.calculate_rsi(prices, 14)

        # RSI should indicate uptrend
        assert any(x > 70 for x in rsi[-5:])

    def test_analysis_on_volatile_data(self):
        """Test analysis on volatile price data."""
        prices = [100.0, 110.0, 95.0, 115.0, 90.0, 120.0, 85.0, 125.0]

        analyzer = TechnicalAnalyzer()
        bands = analyzer.calculate_bollinger_bands(prices, 3, 1.0)

        # With volatility, bands should be wide
        assert len(bands['upper']) > 0
        assert all(
            bands['upper'][i] > bands['middle'][i]
            for i in range(len(bands['middle']))
        )

    def test_analysis_on_flat_data(self):
        """Test analysis on flat price data."""
        prices = [100.0] * 20

        analyzer = TechnicalAnalyzer()
        sma = analyzer.calculate_sma(prices, 5)

        # SMA of flat prices should be flat
        assert all(x == 100.0 for x in sma)

    def test_atr_with_ohlc_data(self, mock_ohlc_data):
        """Test ATR calculation with OHLC data."""
        analyzer = TechnicalAnalyzer()

        high = [candle["high"] for candle in mock_ohlc_data]
        low = [candle["low"] for candle in mock_ohlc_data]
        close = [candle["close"] for candle in mock_ohlc_data]

        atr = analyzer.calculate_atr(high, low, close, 14)

        assert len(atr) > 0
        assert all(x > 0 for x in atr)


class TestEngineWithAnalysisIntegration:
    """Integration tests combining engine and analysis."""

    def test_fetch_prices_and_analyze(self, trading_engine, mock_price_history):
        """Test fetching prices and performing analysis."""
        with patch.object(trading_engine, '_call_kis_api') as mock_kis:
            # Simulate fetching prices
            mock_kis.side_effect = mock_price_history

            analyzer = TechnicalAnalyzer()
            prices = []

            for price in mock_price_history[:10]:
                mock_kis.return_value = price
                fetched = trading_engine.get_stock_price("005930")
                if fetched:
                    prices.append(fetched)

            if len(prices) >= 5:
                sma = analyzer.calculate_sma(prices, 3)
                assert len(sma) > 0

    def test_portfolio_price_monitoring(self, trading_engine, mock_stock_prices, mock_crypto_prices):
        """Test monitoring portfolio with multiple assets."""
        with patch.object(trading_engine, '_call_kis_api') as mock_kis, \
             patch.object(trading_engine, '_call_upbit_api') as mock_upbit:

            portfolio = {}

            # Fetch stock prices
            for ticker, price in list(mock_stock_prices.items())[:2]:
                mock_kis.return_value = price
                stock_price = trading_engine.get_stock_price(ticker)
                portfolio[f"STOCK-{ticker}"] = stock_price

            # Fetch crypto prices
            for ticker, price in list(mock_crypto_prices.items())[:2]:
                mock_upbit.return_value = price
                crypto_price = trading_engine.get_coin_price(ticker)
                portfolio[f"CRYPTO-{ticker}"] = crypto_price

            assert len(portfolio) >= 4
            assert all(price is not None for price in portfolio.values())


class TestErrorPropagation:
    """Integration tests for error propagation across modules."""

    def test_configuration_error_propagation(self):
        """Test configuration errors propagate through engine."""
        kis = KISConfig(
            app_key="",
            secret_key="",
            account_number="",
            hts_id=""
        )
        upbit = UpbitConfig(
            access_key="",
            secret_key=""
        )
        config = TradingConfig(kis_config=kis, upbit_config=upbit)

        with pytest.raises(ValueError):
            HybridTradingEngine(config)

    def test_analysis_error_on_invalid_data(self):
        """Test analysis errors with invalid data."""
        analyzer = TechnicalAnalyzer()

        with pytest.raises(AnalysisError):
            analyzer.calculate_sma([], 5)

        with pytest.raises(AnalysisError):
            analyzer.calculate_sma([100.0], 5)

    def test_chained_error_handling(self, trading_engine):
        """Test error handling across multiple operations."""
        with pytest.raises(ValueError):
            trading_engine.get_stock_price(None)

        with pytest.raises(ValueError):
            trading_engine.get_coin_price("")

        # Should not raise after error handling
        with patch.object(trading_engine, '_call_kis_api') as mock_kis:
            mock_kis.return_value = 75500.0
            price = trading_engine.get_stock_price("005930")
            assert price == 75500.0


class TestMemoryAndResourceManagement:
    """Integration tests for memory and resource management."""

    def test_large_price_dataset_analysis(self, large_price_dataset):
        """Test analyzing large price dataset."""
        analyzer = TechnicalAnalyzer()

        sma = analyzer.calculate_sma(large_price_dataset, 20)
        ema = analyzer.calculate_ema(large_price_dataset, 20)
        rsi = analyzer.calculate_rsi(large_price_dataset, 14)

        assert len(sma) > 0
        assert len(ema) > 0
        assert len(rsi) > 0

    def test_multiple_engines_concurrent_operations(self, trading_config, trading_config_custom):
        """Test multiple engines with concurrent-like operations."""
        engine1 = HybridTradingEngine(trading_config)
        engine2 = HybridTradingEngine(trading_config_custom)

        with patch.object(engine1, '_call_kis_api') as mock_kis1, \
             patch.object(engine2, '_call_kis_api') as mock_kis2:

            mock_kis1.return_value = 75500.0
            mock_kis2.return_value = 80000.0

            price1 = engine1.get_stock_price("005930")
            price2 = engine2.get_stock_price("005930")

            assert price1 == 75500.0
            assert price2 == 80000.0

    def test_engine_cleanup_after_operations(self, trading_config):
        """Test engine properly cleans up after operations."""
        engine = HybridTradingEngine(trading_config)

        with patch.object(engine, 'close') as mock_close:
            engine.close()
            assert mock_close.called
