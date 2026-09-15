"""Technical analysis module for Hybrid Trader.

This module provides technical analysis tools for trading strategies.
"""

from typing import List, Dict, Any, Optional
import logging

from .exceptions import AnalysisError

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Technical analysis tool for price data analysis.
    
    가격 데이터에 대한 기술적 분석을 수행하는 도구입니다.
    """

    def __init__(self):
        """Initialize the TechnicalAnalyzer."""
        pass

    @staticmethod
    def validate_price_data(prices: List[float]) -> bool:
        """Validate price data format and values.
        
        가격 데이터의 형식과 값을 검증합니다.
        
        Args:
            prices: List of price values
            
        Returns:
            True if data is valid
            
        Raises:
            AnalysisError: If data is invalid
        """
        if not prices:
            raise AnalysisError("Price data cannot be empty")
        
        if not isinstance(prices, list):
            raise AnalysisError("Price data must be a list")
        
        if len(prices) < 2:
            raise AnalysisError("At least 2 price points are required")
        
        for i, price in enumerate(prices):
            if not isinstance(price, (int, float)):
                raise AnalysisError(f"Price at index {i} is not a number: {price}")
            
            if price <= 0:
                raise AnalysisError(f"Price at index {i} must be positive: {price}")
        
        return True

    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average.
        
        단순 이동 평균을 계산합니다.
        
        Args:
            prices: List of price values
            period: SMA period
            
        Returns:
            List of SMA values
            
        Raises:
            AnalysisError: If data is invalid
        """
        TechnicalAnalyzer.validate_price_data(prices)
        
        if period <= 0:
            raise AnalysisError("Period must be positive")
        
        if period > len(prices):
            raise AnalysisError(f"Period ({period}) cannot exceed number of prices ({len(prices)})")
        
        sma = []
        for i in range(len(prices) - period + 1):
            avg = sum(prices[i:i+period]) / period
            sma.append(avg)
        
        return sma

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average.
        
        지수 이동 평균을 계산합니다.
        
        Args:
            prices: List of price values
            period: EMA period
            
        Returns:
            List of EMA values
            
        Raises:
            AnalysisError: If data is invalid
        """
        TechnicalAnalyzer.validate_price_data(prices)
        
        if period <= 0:
            raise AnalysisError("Period must be positive")
        
        if period > len(prices):
            raise AnalysisError(f"Period ({period}) cannot exceed number of prices ({len(prices)})")
        
        k = 2 / (period + 1)
        ema = []
        
        # Calculate first SMA as initial EMA
        initial_sma = sum(prices[:period]) / period
        ema.append(initial_sma)
        
        # Calculate EMA for remaining prices
        for i in range(period, len(prices)):
            ema_value = prices[i] * k + ema[-1] * (1 - k)
            ema.append(ema_value)
        
        return ema

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index.
        
        상대 강도 지수를 계산합니다.
        
        Args:
            prices: List of price values
            period: RSI period (default: 14)
            
        Returns:
            List of RSI values
            
        Raises:
            AnalysisError: If data is invalid
        """
        TechnicalAnalyzer.validate_price_data(prices)
        
        if period <= 0:
            raise AnalysisError("Period must be positive")
        
        if period >= len(prices):
            raise AnalysisError(f"Period ({period}) must be less than number of prices ({len(prices)})")
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [max(d, 0) for d in deltas]
        losses = [abs(min(d, 0)) for d in deltas]
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi_values = []
        
        for i in range(period):
            if avg_loss == 0:
                rsi_values.append(100.0 if avg_gain > 0 else 50.0)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)
            
            if i < len(gains) - period:
                avg_gain = (avg_gain * (period - 1) + gains[period + i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[period + i]) / period
        
        return rsi_values[-len(prices) + period:]

    @staticmethod
    def calculate_bollinger_bands(
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, List[float]]:
        """Calculate Bollinger Bands.
        
        볼린저 밴드를 계산합니다.
        
        Args:
            prices: List of price values
            period: Period for moving average (default: 20)
            std_dev: Standard deviation multiplier (default: 2.0)
            
        Returns:
            Dictionary with 'upper', 'middle', 'lower' bands
            
        Raises:
            AnalysisError: If data is invalid
        """
        TechnicalAnalyzer.validate_price_data(prices)
        
        if period <= 0:
            raise AnalysisError("Period must be positive")
        
        if std_dev <= 0:
            raise AnalysisError("Standard deviation must be positive")
        
        if period > len(prices):
            raise AnalysisError(f"Period ({period}) cannot exceed number of prices ({len(prices)})")
        
        middle = []
        upper = []
        lower = []
        
        for i in range(len(prices) - period + 1):
            window = prices[i:i+period]
            mean = sum(window) / period
            variance = sum((x - mean) ** 2 for x in window) / period
            std = variance ** 0.5
            
            middle.append(mean)
            upper.append(mean + std_dev * std)
            lower.append(mean - std_dev * std)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }

    @staticmethod
    def calculate_macd(
        prices: List[float],
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict[str, List[float]]:
        """Calculate MACD (Moving Average Convergence Divergence).
        
        MACD를 계산합니다.
        
        Args:
            prices: List of price values
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line period (default: 9)
            
        Returns:
            Dictionary with 'macd', 'signal', 'histogram' lines
            
        Raises:
            AnalysisError: If data is invalid
        """
        TechnicalAnalyzer.validate_price_data(prices)
        
        if fast <= 0 or slow <= 0 or signal <= 0:
            raise AnalysisError("All periods must be positive")
        
        if slow >= len(prices):
            raise AnalysisError(f"Slow period ({slow}) must be less than number of prices")
        
        ema_fast = TechnicalAnalyzer.calculate_ema(prices, fast)
        ema_slow = TechnicalAnalyzer.calculate_ema(prices, slow)
        
        # Align EMA arrays
        macd_line = [ema_fast[i - (fast - 1) + (slow - 1)] - ema_slow[i] for i in range(len(ema_slow))]
        
        signal_line = TechnicalAnalyzer.calculate_sma(macd_line, signal)
        histogram = [macd_line[i + len(macd_line) - len(signal_line)] - signal_line[i] for i in range(len(signal_line))]
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_atr(
        high: List[float],
        low: List[float],
        close: List[float],
        period: int = 14
    ) -> List[float]:
        """Calculate Average True Range.
        
        평균 진정 범위(ATR)를 계산합니다.
        
        Args:
            high: List of high prices
            low: List of low prices
            close: List of close prices
            period: ATR period (default: 14)
            
        Returns:
            List of ATR values
            
        Raises:
            AnalysisError: If data is invalid
        """
        if not (len(high) == len(low) == len(close)):
            raise AnalysisError("High, low, and close price lists must have the same length")
        
        if len(high) < period + 1:
            raise AnalysisError(f"Need at least {period + 1} price points")
        
        tr_values = []
        for i in range(1, len(high)):
            tr = max(
                high[i] - low[i],
                abs(high[i] - close[i-1]),
                abs(low[i] - close[i-1])
            )
            tr_values.append(tr)
        
        atr = []
        atr.append(sum(tr_values[:period]) / period)
        
        for i in range(period, len(tr_values)):
            atr_value = (atr[-1] * (period - 1) + tr_values[i]) / period
            atr.append(atr_value)
        
        return atr
