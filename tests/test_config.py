"""Tests for configuration module."""

import pytest
from hybrid_trader.config import KISConfig, UpbitConfig, TradingConfig


class TestKISConfig:
    """Test cases for KISConfig."""

    def test_kis_config_initialization(self):
        """Test KISConfig initialization with valid parameters."""
        config = KISConfig(
            app_key="test_app_key",
            secret_key="test_secret_key",
            account_number="1234-5678",
            hts_id="test_hts_id"
        )

        assert config.app_key == "test_app_key"
        assert config.secret_key == "test_secret_key"
        assert config.account_number == "1234-5678"
        assert config.hts_id == "test_hts_id"
        assert config.is_demo is True

    def test_kis_config_demo_mode(self):
        """Test KISConfig demo mode setting."""
        config = KISConfig(
            app_key="key",
            secret_key="secret",
            account_number="1234-5678",
            hts_id="hts",
            is_demo=False
        )

        assert config.is_demo is False


class TestUpbitConfig:
    """Test cases for UpbitConfig."""

    def test_upbit_config_initialization(self):
        """Test UpbitConfig initialization with valid parameters."""
        config = UpbitConfig(
            access_key="test_access_key",
            secret_key="test_secret_key"
        )

        assert config.access_key == "test_access_key"
        assert config.secret_key == "test_secret_key"


class TestTradingConfig:
    """Test cases for TradingConfig."""

    def test_trading_config_initialization(self):
        """Test TradingConfig initialization."""
        kis = KISConfig(
            app_key="kis_key",
            secret_key="kis_secret",
            account_number="1234-5678",
            hts_id="hts_id"
        )
        upbit = UpbitConfig(
            access_key="upbit_key",
            secret_key="upbit_secret"
        )

        config = TradingConfig(kis_config=kis, upbit_config=upbit)

        assert config.kis_config == kis
        assert config.upbit_config == upbit
        assert config.timeout == 10
        assert config.retry_count == 3

    def test_trading_config_custom_timeout(self):
        """Test TradingConfig with custom timeout."""
        kis = KISConfig(
            app_key="key",
            secret_key="secret",
            account_number="1234-5678",
            hts_id="hts"
        )
        upbit = UpbitConfig(
            access_key="key",
            secret_key="secret"
        )

        config = TradingConfig(
            kis_config=kis,
            upbit_config=upbit,
            timeout=20,
            retry_count=5
        )

        assert config.timeout == 20
        assert config.retry_count == 5

    def test_trading_config_validation_missing_kis_app_key(self):
        """Test TradingConfig validation fails with missing KIS app_key."""
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

        with pytest.raises(ValueError, match="Missing required credentials"):
            config.validate()

    def test_trading_config_validation_missing_upbit_key(self):
        """Test TradingConfig validation fails with missing Upbit credentials."""
        kis = KISConfig(
            app_key="key",
            secret_key="secret",
            account_number="1234-5678",
            hts_id="hts"
        )
        upbit = UpbitConfig(
            access_key="",
            secret_key="secret"
        )

        config = TradingConfig(kis_config=kis, upbit_config=upbit)

        with pytest.raises(ValueError, match="Missing required credentials"):
            config.validate()

    def test_trading_config_validation_success(self):
        """Test TradingConfig validation succeeds with all credentials."""
        kis = KISConfig(
            app_key="key",
            secret_key="secret",
            account_number="1234-5678",
            hts_id="hts"
        )
        upbit = UpbitConfig(
            access_key="key",
            secret_key="secret"
        )

        config = TradingConfig(kis_config=kis, upbit_config=upbit)

        assert config.validate() is True
