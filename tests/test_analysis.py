"""Tests for technical analysis module.

This module tests all technical analysis methods and data validation.
"""

import pytest
import math
from hybrid_trader.analysis import TechnicalAnalyzer
from hybrid_trader.exceptions import AnalysisError


class TestTechnicalAnalyzerValidation:
    """Test cases for price data validation."""

    def test_validate_price_data_valid(self):
        """Test validate_price_data accepts valid data."""
        prices = [100.0, 101.0, 102.0, 103.0, 104.0]
        assert TechnicalAnalyzer.validate_price_data(prices) is True

    def test_validate_price_data_empty(self):
        """Test validate_price_data rejects empty list."""
        with pytest.raises(AnalysisError, match="cannot be empty"):
            TechnicalAnalyzer.validate_price_data([])

    def test_validate_price_data_not_list(self):
        """Test validate_price_data rejects non-list input."""
        with pytest.raises(AnalysisError, match="must be a list"):
            TechnicalAnalyzer.validate_price_data("100,101,102")

    def test_validate_price_data_single_element(self):
        """Test validate_price_data rejects single element."""
        with pytest.raises(AnalysisError, match="at least 2"):
            TechnicalAnalyzer.validate_price_data([100.0])

    def test_validate_price_data_non_numeric(self):
        """Test validate_price_data rejects non-numeric values."""
        with pytest.raises(AnalysisError, match="not a number"):
            TechnicalAnalyzer.validate_price_data([100.0, "101", 102.0])

    def test_validate_price_data_zero_price(self):
        """Test validate_price_data rejects zero price."""
        with pytest.raises(AnalysisError, match="must be positive"):
            TechnicalAnalyzer.validate_price_data([100.0, 0.0, 102.0])

    def test_validate_price_data_negative_price(self):
        """Test validate_price_data rejects negative price."""
        with pytest.raises(AnalysisError, match="must be positive"):
            TechnicalAnalyzer.validate_price_data([100.0, -50.0, 102.0])

    def test_validate_price_data_mixed_int_float(self):
        """Test validate_price_data accepts mixed int and float."""
        prices = [100, 101.5, 102, 103.2, 104]
        assert TechnicalAnalyzer.validate_price_data(prices) is True


class TestSimpleMovingAverage:
    """Test cases for SMA calculation."""

    def test_calculate_sma_valid(self):
        """Test calculate_sma with valid data."""
        prices = [100.0, 101.0, 102.0, 103.0, 104.0]
        sma = TechnicalAnalyzer.calculate_sma(prices, 3)

        assert len(sma) == 3
        assert sma[0] == pytest.approx(101.0)  # (100+101+102)/3
        assert sma[1] == pytest.approx(102.0)  # (101+102+103)/3
        assert sma[2] == pytest.approx(103.0)  # (102+103+104)/3

    def test_calculate_sma_period_one(self):
        """Test calculate_sma with period 1."""
        prices = [100.0, 101.0, 102.0]
        sma = TechnicalAnalyzer.calculate_sma(prices, 1)

        assert len(sma) == 3
        assert sma == prices

    def test_calculate_sma_period_equals_length(self):
        """Test calculate_sma when period equals list length."""
        prices = [100.0, 101.0, 102.0]
        sma = TechnicalAnalyzer.calculate_sma(prices, 3)

        assert len(sma) == 1
        assert sma[0] == pytest.approx(101.0)

    def test_calculate_sma_invalid_period_zero(self):
        """Test calculate_sma rejects zero period."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="must be positive"):
            TechnicalAnalyzer.calculate_sma(prices, 0)

    def test_calculate_sma_invalid_period_negative(self):
        """Test calculate_sma rejects negative period."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="must be positive"):
            TechnicalAnalyzer.calculate_sma(prices, -1)

    def test_calculate_sma_period_exceeds_length(self):
        """Test calculate_sma rejects period > length."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="cannot exceed"):
            TechnicalAnalyzer.calculate_sma(prices, 5)


class TestExponentialMovingAverage:
    """Test cases for EMA calculation."""

    def test_calculate_ema_valid(self):
        """Test calculate_ema with valid data."""
        prices = [100.0, 101.0, 102.0, 103.0, 104.0]
        ema = TechnicalAnalyzer.calculate_ema(prices, 3)

        assert len(ema) > 0
        assert all(isinstance(x, float) for x in ema)

    def test_calculate_ema_period_one(self):
        """Test calculate_ema with period 1."""
        prices = [100.0, 101.0, 102.0]
        ema = TechnicalAnalyzer.calculate_ema(prices, 1)

        assert len(ema) > 0
        assert all(isinstance(x, float) for x in ema)

    def test_calculate_ema_invalid_period_zero(self):
        """Test calculate_ema rejects zero period."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="must be positive"):
            TechnicalAnalyzer.calculate_ema(prices, 0)

    def test_calculate_ema_period_exceeds_length(self):
        """Test calculate_ema rejects period > length."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="cannot exceed"):
            TechnicalAnalyzer.calculate_ema(prices, 5)


class TestRelativeStrengthIndex:
    """Test cases for RSI calculation."""

    def test_calculate_rsi_valid(self):
        """Test calculate_rsi with valid data."""
        prices = [100.0 + i for i in range(30)]
        rsi = TechnicalAnalyzer.calculate_rsi(prices, 14)

        assert len(rsi) > 0
        assert all(0 <= x <= 100 for x in rsi)

    def test_calculate_rsi_default_period(self):
        """Test calculate_rsi with default period."""
        prices = [100.0 + i for i in range(30)]
        rsi = TechnicalAnalyzer.calculate_rsi(prices)

        assert len(rsi) > 0
        assert all(0 <= x <= 100 for x in rsi)

    def test_calculate_rsi_invalid_period_zero(self):
        """Test calculate_rsi rejects zero period."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="must be positive"):
            TechnicalAnalyzer.calculate_rsi(prices, 0)

    def test_calculate_rsi_period_exceeds_length(self):
        """Test calculate_rsi rejects period >= length."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="must be less than"):
            TechnicalAnalyzer.calculate_rsi(prices, 5)

    def test_calculate_rsi_increasing_prices(self):
        """Test calculate_rsi with increasing prices (high RSI)."""
        prices = [float(100 + i) for i in range(30)]
        rsi = TechnicalAnalyzer.calculate_rsi(prices, 14)

        # RSI should be high for consistently increasing prices
        assert all(x > 50 for x in rsi[-5:])

    def test_calculate_rsi_decreasing_prices(self):
        """Test calculate_rsi with decreasing prices (low RSI)."""
        prices = [float(130 - i) for i in range(30)]
        rsi = TechnicalAnalyzer.calculate_rsi(prices, 14)

        # RSI should be low for consistently decreasing prices
        assert all(x < 50 for x in rsi[-5:])


class TestBollingerBands:
    """Test cases for Bollinger Bands calculation."""

    def test_calculate_bollinger_bands_valid(self):
        """Test calculate_bollinger_bands with valid data."""
        prices = [100.0 + i * 0.5 for i in range(30)]
        bands = TechnicalAnalyzer.calculate_bollinger_bands(prices, 20, 2.0)

        assert 'upper' in bands
        assert 'middle' in bands
        assert 'lower' in bands
        assert len(bands['upper']) == len(bands['middle']) == len(bands['lower'])

    def test_calculate_bollinger_bands_band_order(self):
        """Test that upper band > middle band > lower band."""
        prices = [100.0 + i * 0.5 for i in range(30)]
        bands = TechnicalAnalyzer.calculate_bollinger_bands(prices, 20, 2.0)

        for i in range(len(bands['middle'])):
            assert bands['upper'][i] >= bands['middle'][i] >= bands['lower'][i]

    def test_calculate_bollinger_bands_default_params(self):
        """Test calculate_bollinger_bands with default parameters."""
        prices = [100.0 + i * 0.5 for i in range(30)]
        bands = TechnicalAnalyzer.calculate_bollinger_bands(prices)

        assert len(bands['middle']) > 0

    def test_calculate_bollinger_bands_invalid_period_zero(self):
        """Test calculate_bollinger_bands rejects zero period."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="must be positive"):
            TechnicalAnalyzer.calculate_bollinger_bands(prices, 0, 2.0)

    def test_calculate_bollinger_bands_invalid_std_dev_zero(self):
        """Test calculate_bollinger_bands rejects zero std_dev."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="must be positive"):
            TechnicalAnalyzer.calculate_bollinger_bands(prices, 2, 0)

    def test_calculate_bollinger_bands_period_exceeds_length(self):
        """Test calculate_bollinger_bands rejects period > length."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="cannot exceed"):
            TechnicalAnalyzer.calculate_bollinger_bands(prices, 5, 2.0)


class TestMACD:
    """Test cases for MACD calculation."""

    def test_calculate_macd_valid(self):
        """Test calculate_macd with valid data."""
        prices = [100.0 + i * 0.5 for i in range(50)]
        macd = TechnicalAnalyzer.calculate_macd(prices)

        assert 'macd' in macd
        assert 'signal' in macd
        assert 'histogram' in macd
        assert len(macd['macd']) > 0

    def test_calculate_macd_default_params(self):
        """Test calculate_macd with default parameters."""
        prices = [100.0 + i * 0.5 for i in range(50)]
        macd = TechnicalAnalyzer.calculate_macd(prices)

        # Verify structure
        assert isinstance(macd, dict)
        assert all(key in macd for key in ['macd', 'signal', 'histogram'])

    def test_calculate_macd_custom_params(self):
        """Test calculate_macd with custom parameters."""
        prices = [100.0 + i * 0.5 for i in range(50)]
        macd = TechnicalAnalyzer.calculate_macd(prices, fast=5, slow=10, signal=5)

        assert len(macd['macd']) > 0

    def test_calculate_macd_invalid_periods_zero(self):
        """Test calculate_macd rejects zero periods."""
        prices = [100.0 + i * 0.5 for i in range(50)]
        with pytest.raises(AnalysisError, match="must be positive"):
            TechnicalAnalyzer.calculate_macd(prices, 0, 26, 9)

    def test_calculate_macd_slow_exceeds_length(self):
        """Test calculate_macd rejects slow period > length."""
        prices = [100.0, 101.0, 102.0]
        with pytest.raises(AnalysisError, match="must be less than"):
            TechnicalAnalyzer.calculate_macd(prices, 12, 50, 9)


class TestAverageTrueRange:
    """Test cases for ATR calculation."""

    def test_calculate_atr_valid(self):
        """Test calculate_atr with valid data."""
        high = [101.0 + i for i in range(20)]
        low = [100.0 + i for i in range(20)]
        close = [100.5 + i for i in range(20)]

        atr = TechnicalAnalyzer.calculate_atr(high, low, close, 14)

        assert len(atr) > 0
        assert all(x > 0 for x in atr)

    def test_calculate_atr_default_period(self):
        """Test calculate_atr with default period."""
        high = [101.0 + i for i in range(20)]
        low = [100.0 + i for i in range(20)]
        close = [100.5 + i for i in range(20)]

        atr = TechnicalAnalyzer.calculate_atr(high, low, close)

        assert len(atr) > 0

    def test_calculate_atr_mismatched_lengths(self):
        """Test calculate_atr rejects mismatched list lengths."""
        high = [101.0, 102.0, 103.0]
        low = [100.0, 101.0]
        close = [100.5, 101.5, 102.5]

        with pytest.raises(AnalysisError, match="same length"):
            TechnicalAnalyzer.calculate_atr(high, low, close)

    def test_calculate_atr_insufficient_data(self):
        """Test calculate_atr rejects insufficient data."""
        high = [101.0, 102.0]
        low = [100.0, 101.0]
        close = [100.5, 101.5]

        with pytest.raises(AnalysisError, match="at least"):
            TechnicalAnalyzer.calculate_atr(high, low, close, 14)

    def test_calculate_atr_high_low_close_relationship(self):
        """Test calculate_atr with valid high > low relationship."""
        high = [105.0 + i for i in range(20)]
        low = [100.0 + i for i in range(20)]
        close = [102.5 + i for i in range(20)]

        atr = TechnicalAnalyzer.calculate_atr(high, low, close)

        # ATR should be positive and reasonable
        assert all(0 <= x <= 10 for x in atr)


class TestAnalyzerIntegration:
    """Integration tests for TechnicalAnalyzer."""

    def test_multiple_indicators_on_same_data(self):
        """Test calculating multiple indicators on same data."""
        prices = [100.0 + i * 0.5 for i in range(50)]

        sma = TechnicalAnalyzer.calculate_sma(prices, 10)
        ema = TechnicalAnalyzer.calculate_ema(prices, 10)
        rsi = TechnicalAnalyzer.calculate_rsi(prices, 14)

        assert len(sma) > 0
        assert len(ema) > 0
        assert len(rsi) > 0

    def test_analyzer_with_volatile_data(self):
        """Test analyzer with volatile price data."""
        prices = [100.0, 110.0, 95.0, 115.0, 90.0, 120.0]

        sma = TechnicalAnalyzer.calculate_sma(prices, 2)
        assert len(sma) == len(prices) - 1

    def test_analyzer_with_trending_data(self):
        """Test analyzer with strongly trending data."""
        prices = [float(100 + i) for i in range(30)]

        sma = TechnicalAnalyzer.calculate_sma(prices, 5)
        rsi = TechnicalAnalyzer.calculate_rsi(prices, 14)

        # For uptrending data
        assert all(x > 50 for x in rsi[-5:])

    def test_analyzer_edge_case_flat_prices(self):
        """Test analyzer with flat price data."""
        prices = [100.0] * 20

        sma = TechnicalAnalyzer.calculate_sma(prices, 5)
        assert all(x == pytest.approx(100.0) for x in sma)

        bands = TechnicalAnalyzer.calculate_bollinger_bands(prices, 10, 2.0)
        # With flat prices, upper and lower bands should converge
        assert all(
            bands['upper'][i] == pytest.approx(bands['lower'][i])
            for i in range(len(bands['upper']))
        )
