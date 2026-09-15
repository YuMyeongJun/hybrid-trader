"""Shared pytest fixtures and configuration for Hybrid Trader tests.

This module provides common fixtures, mock data, and configuration for all tests.
"""

import sys
import pytest
from unittest.mock import Mock, MagicMock, patch

# Mock external optional dependencies that may not be installed
mock_kis = MagicMock()
mock_kis.KISClient = MagicMock
sys.modules['kis'] = mock_kis

from hybrid_trader.config import TradingConfig, KISConfig, UpbitConfig
from hybrid_trader.engine import HybridTradingEngine
from hybrid_trader.analysis import TechnicalAnalyzer


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def kis_config():
    """Fixture providing KIS configuration for testing.
    
    테스트용 한국투자증권 설정을 제공합니다.
    """
    return KISConfig(
        app_key="test_app_key_kis",
        secret_key="test_secret_key_kis",
        account_number="1234-5678",
        hts_id="test_hts_id",
        is_demo=True
    )


@pytest.fixture
def upbit_config():
    """Fixture providing Upbit configuration for testing.
    
    테스트용 업비트 설정을 제공합니다.
    """
    return UpbitConfig(
        access_key="test_access_key_upbit",
        secret_key="test_secret_key_upbit"
    )


@pytest.fixture
def trading_config(kis_config, upbit_config):
    """Fixture providing complete trading configuration.
    
    테스트용 전체 거래 설정을 제공합니다.
    """
    return TradingConfig(
        kis_config=kis_config,
        upbit_config=upbit_config,
        timeout=10,
        retry_count=3
    )


@pytest.fixture
def trading_config_custom():
    """Fixture providing custom trading configuration.
    
    사용자 정의 거래 설정을 제공합니다.
    """
    kis = KISConfig(
        app_key="custom_app_key",
        secret_key="custom_secret_key",
        account_number="9999-8888",
        hts_id="custom_hts_id",
        is_demo=False
    )
    upbit = UpbitConfig(
        access_key="custom_access_key",
        secret_key="custom_secret_key"
    )
    return TradingConfig(
        kis_config=kis,
        upbit_config=upbit,
        timeout=20,
        retry_count=5
    )


# ============================================================================
# Engine Fixtures
# ============================================================================


@pytest.fixture
def trading_engine(trading_config):
    """Fixture providing HybridTradingEngine instance.
    
    테스트용 하이브리드 트레이딩 엔진 인스턴스를 제공합니다.
    """
    return HybridTradingEngine(trading_config)


@pytest.fixture
def trading_engine_custom(trading_config_custom):
    """Fixture providing custom HybridTradingEngine instance.
    
    사용자 정의 하이브리드 트레이딩 엔진 인스턴스를 제공합니다.
    """
    return HybridTradingEngine(trading_config_custom)


# ============================================================================
# Mock Data Fixtures
# ============================================================================


@pytest.fixture
def mock_stock_prices():
    """Fixture providing mock stock price data.
    
    테스트용 주식 가격 데이터를 제공합니다.
    """
    return {
        "005930": 75500.0,  # Samsung Electronics
        "000660": 98500.0,  # SK Hynix
        "207940": 848000.0,  # Samsung Electronics (preferred)
        "003550": 430500.0,  # LG Corp
    }


@pytest.fixture
def mock_crypto_prices():
    """Fixture providing mock cryptocurrency price data.
    
    테스트용 암호화폐 가격 데이터를 제공합니다.
    """
    return {
        "KRW-BTC": 65500000.0,    # Bitcoin
        "KRW-ETH": 3200000.0,     # Ethereum
        "KRW-XRP": 1500.0,        # Ripple
        "KRW-DOGE": 250.0,        # Dogecoin
    }


@pytest.fixture
def mock_price_history():
    """Fixture providing mock price history for analysis.
    
    기술적 분석용 모의 가격 이력을 제공합니다.
    """
    # Simulated price movement: uptrend then downtrend
    prices = []
    for i in range(30):
        if i < 15:
            prices.append(100.0 + i * 2)  # Uptrend
        else:
            prices.append(130.0 - (i - 14) * 1.5)  # Downtrend
    return prices


@pytest.fixture
def mock_ohlc_data():
    """Fixture providing mock OHLC (Open, High, Low, Close) data.
    
    OHLC 데이터를 제공합니다.
    """
    import random

    random.seed(42)
    data = []
    current_price = 100.0

    for i in range(20):
        open_price = current_price
        high_price = open_price + random.uniform(0, 5)
        low_price = open_price - random.uniform(0, 5)
        close_price = low_price + random.uniform(0, high_price - low_price)

        data.append({
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": random.randint(1000000, 10000000),
            "timestamp": f"2024-01-{i+1:02d}",
        })

        current_price = close_price

    return data


@pytest.fixture
def mock_kis_response():
    """Fixture providing mock KIS API response.
    
    한국투자증권 API 응답 데이터를 제공합니다.
    """
    return {
        "rt_cd": "0",  # Return code: 0 = success
        "msg_cd": "00000000",
        "msg1": "정상",
        "output": {
            "stck_prpr": "75500",  # Stock price
            "stck_mxpr": "76000",  # Max price
            "stck_llam": "75000",  # Min price
            "stck_vol": "1234567",  # Volume
        }
    }


@pytest.fixture
def mock_upbit_response():
    """Fixture providing mock Upbit API response.
    
    업비트 API 응답 데이터를 제공합니다.
    """
    return {
        "market": "KRW-BTC",
        "candle_date_time_utc": "2024-01-01T12:00:00Z",
        "candle_date_time_kst": "2024-01-01T21:00:00+09:00",
        "opening_price": 65000000.0,
        "high_price": 65500000.0,
        "low_price": 64800000.0,
        "trade_price": 65500000.0,
        "timestamp": 1704110400000,
        "candle_acc_trade_price": 1234567890.0,
        "candle_acc_trade_volume": 0.05,
        "unit": 1,
    }


@pytest.fixture
def mock_kis_session():
    """Fixture providing mock KIS session.
    
    모의 한국투자증권 세션을 제공합니다.
    """
    session = MagicMock()
    session.fetch_price = MagicMock(return_value={"stck_prpr": "75500"})
    session.close = MagicMock()
    return session


@pytest.fixture
def mock_upbit_session():
    """Fixture providing mock Upbit session.
    
    모의 업비트 세션을 제공합니다.
    """
    session = MagicMock()
    session.get_current_price = MagicMock(return_value=65500000.0)
    session.close = MagicMock()
    return session


# ============================================================================
# Analyzer Fixtures
# ============================================================================


@pytest.fixture
def technical_analyzer():
    """Fixture providing TechnicalAnalyzer instance.
    
    기술적 분석기 인스턴스를 제공합니다.
    """
    return TechnicalAnalyzer()


@pytest.fixture
def sample_price_data():
    """Fixture providing sample price data for analysis.
    
    분석용 샘플 가격 데이터를 제공합니다.
    """
    return [100.0, 101.5, 102.3, 101.8, 103.2, 104.1, 103.5, 105.0, 104.5, 106.2]


@pytest.fixture
def large_price_dataset():
    """Fixture providing large price dataset for analysis.
    
    대규모 가격 데이터셋을 제공합니다.
    """
    prices = []
    current = 100.0
    for i in range(500):
        change = (i % 20 - 10) * 0.5  # Wave pattern
        current += change
        prices.append(max(current, 1.0))  # Ensure positive
    return prices


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_api_client():
    """Fixture providing mock API client.
    
    모의 API 클라이언트를 제공합니다.
    """
    client = MagicMock()
    client.connect = MagicMock(return_value=True)
    client.disconnect = MagicMock(return_value=True)
    client.is_connected = MagicMock(return_value=True)
    return client


@pytest.fixture
def mock_order_response():
    """Fixture providing mock order response.
    
    모의 주문 응답을 제공합니다.
    """
    return {
        "order_id": "ORD-2024-001-12345",
        "status": "accepted",
        "quantity": 100,
        "price": 75500.0,
        "total": 7550000.0,
        "timestamp": "2024-01-01T12:00:00Z",
        "type": "buy",
    }


@pytest.fixture
def mock_balance_response():
    """Fixture providing mock account balance response.
    
    모의 계좌 잔액 응답을 제공합니다.
    """
    return {
        "account_id": "1234-5678",
        "total_balance": 10000000.0,
        "available_balance": 5000000.0,
        "holdings": [
            {
                "ticker": "005930",
                "quantity": 10,
                "average_price": 75000.0,
                "current_price": 75500.0,
            }
        ],
        "timestamp": "2024-01-01T12:00:00Z",
    }


# ============================================================================
# Utility Functions
# ============================================================================


def generate_mock_prices(
    base_price: float = 100.0,
    count: int = 100,
    volatility: float = 0.02,
    trend: float = 0.0
) -> list:
    """Generate mock price data with trend and volatility.
    
    추세와 변동성이 있는 모의 가격 데이터를 생성합니다.
    
    Args:
        base_price: Starting price
        count: Number of prices to generate
        volatility: Price volatility (0.02 = 2%)
        trend: Daily trend percentage
        
    Returns:
        List of generated prices
    """
    import random
    random.seed(42)

    prices = []
    current = base_price

    for _ in range(count):
        change = random.gauss(trend, volatility)
        current *= (1 + change)
        prices.append(current)

    return prices


# ============================================================================
# Pytest Hooks
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
    config.addinivalue_line(
        "markers", "network: mark test that requires network"
    )
