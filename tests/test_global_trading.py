"""Tests for global trading configuration and API integration.

글로벌 거래 설정 및 API 통합을 위한 테스트 모듈입니다.
Alpaca(미국), Interactive Brokers(유럽/아시아) 등 글로벌 시장 거래 지원을 테스트합니다.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from hybrid_trader.config import (
    AlpacaConfig,
    InteractiveBrokersConfig,
    TradingConfig,
    KISConfig,
    UpbitConfig,
)


class TestAlpacaConfig:
    """Test cases for Alpaca API configuration.

    미국 주식 거래를 위한 Alpaca API 설정을 테스트합니다.
    """

    def test_alpaca_config_initialization(self):
        """Test AlpacaConfig initialization with valid parameters."""
        config = AlpacaConfig(
            api_key="test_alpaca_api_key",
            secret_key="test_alpaca_secret_key",
        )

        assert config.api_key == "test_alpaca_api_key"
        assert config.secret_key == "test_alpaca_secret_key"
        assert config.base_url == "https://paper-api.alpaca.markets"
        assert config.is_paper is True

    def test_alpaca_config_custom_base_url(self):
        """Test AlpacaConfig with custom base URL."""
        custom_url = "https://api.alpaca.markets"
        config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
            base_url=custom_url,
        )

        assert config.base_url == custom_url

    def test_alpaca_config_live_trading_mode(self):
        """Test AlpacaConfig in live trading mode (is_paper=False)."""
        config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
            is_paper=False,
        )

        assert config.is_paper is False

    def test_alpaca_config_paper_trading_mode(self):
        """Test AlpacaConfig in paper trading mode (default)."""
        config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
            is_paper=True,
        )

        assert config.is_paper is True

    def test_alpaca_config_defaults(self):
        """Test AlpacaConfig default values."""
        config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
        )

        # Check defaults
        assert config.base_url == "https://paper-api.alpaca.markets"
        assert config.is_paper is True

    def test_alpaca_config_with_all_parameters(self):
        """Test AlpacaConfig with all parameters specified."""
        config = AlpacaConfig(
            api_key="test_key",
            secret_key="test_secret",
            base_url="https://api.alpaca.markets",
            is_paper=False,
        )

        assert config.api_key == "test_key"
        assert config.secret_key == "test_secret"
        assert config.base_url == "https://api.alpaca.markets"
        assert config.is_paper is False


class TestInteractiveBrokersConfig:
    """Test cases for Interactive Brokers API configuration.

    글로벌 시장(유럽, 아시아) 거래를 위한 Interactive Brokers 설정을 테스트합니다.
    """

    def test_ib_config_initialization(self):
        """Test InteractiveBrokersConfig initialization with required parameters."""
        config = InteractiveBrokersConfig(
            account_id="test_account_id",
        )

        assert config.account_id == "test_account_id"
        assert config.host == "127.0.0.1"
        assert config.port == 7497
        assert config.client_id == 1
        assert config.is_demo is True

    def test_ib_config_custom_host_and_port(self):
        """Test InteractiveBrokersConfig with custom host and port."""
        config = InteractiveBrokersConfig(
            account_id="account",
            host="192.168.1.100",
            port=7498,
        )

        assert config.host == "192.168.1.100"
        assert config.port == 7498

    def test_ib_config_custom_client_id(self):
        """Test InteractiveBrokersConfig with custom client ID."""
        config = InteractiveBrokersConfig(
            account_id="account",
            client_id=2,
        )

        assert config.client_id == 2

    def test_ib_config_demo_mode(self):
        """Test InteractiveBrokersConfig in demo mode."""
        config = InteractiveBrokersConfig(
            account_id="account",
            is_demo=True,
        )

        assert config.is_demo is True

    def test_ib_config_live_mode(self):
        """Test InteractiveBrokersConfig in live mode."""
        config = InteractiveBrokersConfig(
            account_id="account",
            is_demo=False,
        )

        assert config.is_demo is False

    def test_ib_config_defaults(self):
        """Test InteractiveBrokersConfig default values."""
        config = InteractiveBrokersConfig(
            account_id="test_account",
        )

        # Check defaults
        assert config.host == "127.0.0.1"
        assert config.port == 7497
        assert config.client_id == 1
        assert config.is_demo is True

    def test_ib_config_with_all_parameters(self):
        """Test InteractiveBrokersConfig with all parameters specified."""
        config = InteractiveBrokersConfig(
            account_id="DU12345",
            host="gateway.ibcloud.com",
            port=4002,
            client_id=5,
            is_demo=False,
        )

        assert config.account_id == "DU12345"
        assert config.host == "gateway.ibcloud.com"
        assert config.port == 4002
        assert config.client_id == 5
        assert config.is_demo is False


class TestGlobalTradingConfig:
    """Test cases for global trading configuration with multiple brokers.

    글로벌 거래 설정을 테스트합니다.
    여러 거래소(Alpaca, Interactive Brokers, KIS, Upbit)를 지원합니다.
    """

    @pytest.fixture
    def kis_config(self):
        """Fixture for KIS configuration."""
        return KISConfig(
            app_key="kis_key",
            secret_key="kis_secret",
            account_number="1234-5678",
            hts_id="hts_id",
        )

    @pytest.fixture
    def upbit_config(self):
        """Fixture for Upbit configuration."""
        return UpbitConfig(
            access_key="upbit_key",
            secret_key="upbit_secret",
        )

    def test_trading_config_with_alpaca(self, kis_config, upbit_config):
        """Test TradingConfig with Alpaca enabled."""
        alpaca = AlpacaConfig(
            api_key="alpaca_key",
            secret_key="alpaca_secret",
        )

        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            alpaca_config=alpaca,
        )

        assert config.alpaca_config is not None
        assert config.alpaca_config.api_key == "alpaca_key"
        assert config.alpaca_config.is_paper is True

    def test_trading_config_with_interactive_brokers(self, kis_config, upbit_config):
        """Test TradingConfig with Interactive Brokers enabled."""
        ib_config = InteractiveBrokersConfig(
            account_id="DU12345",
            host="127.0.0.1",
            port=7497,
        )

        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            ib_config=ib_config,
        )

        assert config.ib_config is not None
        assert config.ib_config.account_id == "DU12345"
        assert config.ib_config.is_demo is True

    def test_trading_config_with_all_global_brokers(self, kis_config, upbit_config):
        """Test TradingConfig with all global brokers enabled."""
        alpaca = AlpacaConfig(
            api_key="alpaca_key",
            secret_key="alpaca_secret",
            is_paper=True,
        )

        ib_config = InteractiveBrokersConfig(
            account_id="DU12345",
            is_demo=True,
        )

        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            alpaca_config=alpaca,
            ib_config=ib_config,
        )

        assert config.alpaca_config is not None
        assert config.ib_config is not None
        assert config.alpaca_config.is_paper is True
        assert config.ib_config.is_demo is True

    def test_trading_config_global_brokers_optional(self, kis_config, upbit_config):
        """Test that global brokers (Alpaca, IB) are optional."""
        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            alpaca_config=None,
            ib_config=None,
        )

        assert config.alpaca_config is None
        assert config.ib_config is None

    def test_global_trading_enabled_with_alpaca(self, kis_config, upbit_config):
        """Test if global trading is enabled with Alpaca configuration."""
        alpaca = AlpacaConfig(
            api_key="key",
            secret_key="secret",
        )

        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            alpaca_config=alpaca,
        )

        # Global trading is enabled if either Alpaca or IB is configured
        global_trading_enabled = config.alpaca_config is not None or config.ib_config is not None
        assert global_trading_enabled is True

    def test_global_trading_enabled_with_ib(self, kis_config, upbit_config):
        """Test if global trading is enabled with Interactive Brokers configuration."""
        ib_config = InteractiveBrokersConfig(
            account_id="DU12345",
        )

        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            ib_config=ib_config,
        )

        # Global trading is enabled if either Alpaca or IB is configured
        global_trading_enabled = config.alpaca_config is not None or config.ib_config is not None
        assert global_trading_enabled is True

    def test_global_trading_disabled(self, kis_config, upbit_config):
        """Test if global trading is disabled when no global brokers configured."""
        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
        )

        # Global trading is disabled when both are None
        global_trading_enabled = config.alpaca_config is not None or config.ib_config is not None
        assert global_trading_enabled is False


class TestGlobalTradingEnvironmentVariables:
    """Test cases for loading global trading configuration from environment variables.

    환경 변수에서 글로벌 거래 설정을 로드하는 테스트입니다.
    """

    @patch.dict(os.environ, {
        "ALPACA_API_KEY": "env_alpaca_key",
        "ALPACA_SECRET_KEY": "env_alpaca_secret",
    })
    def test_load_alpaca_from_environment(self):
        """Test loading Alpaca configuration from environment variables."""
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")

        config = AlpacaConfig(
            api_key=api_key,
            secret_key=secret_key,
        )

        assert config.api_key == "env_alpaca_key"
        assert config.secret_key == "env_alpaca_secret"

    @patch.dict(os.environ, {
        "IB_ACCOUNT_ID": "env_ib_account",
        "IB_HOST": "gateway.ibcloud.com",
        "IB_PORT": "4002",
    })
    def test_load_ib_from_environment(self):
        """Test loading Interactive Brokers configuration from environment variables."""
        account_id = os.getenv("IB_ACCOUNT_ID")
        host = os.getenv("IB_HOST")
        port = int(os.getenv("IB_PORT", "7497"))

        config = InteractiveBrokersConfig(
            account_id=account_id,
            host=host,
            port=port,
        )

        assert config.account_id == "env_ib_account"
        assert config.host == "gateway.ibcloud.com"
        assert config.port == 4002

    @patch.dict(os.environ, {
        "ALPACA_API_KEY": "env_key",
        "ALPACA_SECRET_KEY": "env_secret",
        "ALPACA_PAPER_TRADING": "false",
    }, clear=False)
    def test_load_alpaca_live_mode_from_environment(self):
        """Test loading Alpaca in live mode from environment variables."""
        is_paper = os.getenv("ALPACA_PAPER_TRADING", "true").lower() != "false"

        config = AlpacaConfig(
            api_key=os.getenv("ALPACA_API_KEY"),
            secret_key=os.getenv("ALPACA_SECRET_KEY"),
            is_paper=is_paper,
        )

        assert config.is_paper is False

    @patch.dict(os.environ, {
        "IB_ACCOUNT_ID": "env_account",
        "IB_DEMO_MODE": "false",
    }, clear=False)
    def test_load_ib_live_mode_from_environment(self):
        """Test loading Interactive Brokers in live mode from environment variables."""
        is_demo = os.getenv("IB_DEMO_MODE", "true").lower() != "false"

        config = InteractiveBrokersConfig(
            account_id=os.getenv("IB_ACCOUNT_ID"),
            is_demo=is_demo,
        )

        assert config.is_demo is False


class TestGlobalTradingDemoMode:
    """Test cases for demo/paper trading modes in global brokers.

    글로벌 거래소의 데모/종이 거래 모드를 테스트합니다.
    """

    def test_alpaca_paper_trading_default(self):
        """Test Alpaca defaults to paper trading."""
        config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
        )

        assert config.is_paper is True
        assert config.base_url == "https://paper-api.alpaca.markets"

    def test_alpaca_live_trading_url_change(self):
        """Test Alpaca uses different URL for live trading."""
        config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
            base_url="https://api.alpaca.markets",
            is_paper=False,
        )

        assert config.is_paper is False
        assert config.base_url == "https://api.alpaca.markets"

    def test_ib_demo_mode_default(self):
        """Test Interactive Brokers defaults to demo mode."""
        config = InteractiveBrokersConfig(
            account_id="account",
        )

        assert config.is_demo is True

    def test_ib_demo_mode_enabled(self):
        """Test Interactive Brokers demo mode can be enabled explicitly."""
        config = InteractiveBrokersConfig(
            account_id="account",
            is_demo=True,
        )

        assert config.is_demo is True

    def test_ib_demo_mode_disabled_for_live_trading(self):
        """Test Interactive Brokers demo mode can be disabled for live trading."""
        config = InteractiveBrokersConfig(
            account_id="live_account",
            is_demo=False,
        )

        assert config.is_demo is False

    def test_global_config_mixed_demo_modes(self):
        """Test TradingConfig with mixed demo/live modes for different brokers."""
        kis_config = KISConfig(
            app_key="key",
            secret_key="secret",
            account_number="1234-5678",
            hts_id="hts",
            is_demo=False,  # Live mode
        )
        upbit_config = UpbitConfig(
            access_key="key",
            secret_key="secret",
        )
        alpaca_config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
            is_paper=True,  # Paper mode
        )
        ib_config = InteractiveBrokersConfig(
            account_id="account",
            is_demo=False,  # Live mode
        )

        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            alpaca_config=alpaca_config,
            ib_config=ib_config,
        )

        # Each broker can have its own demo/live setting
        assert config.kis_config.is_demo is False
        assert config.alpaca_config.is_paper is True
        assert config.ib_config.is_demo is False


class TestGlobalTradingIntegration:
    """Test cases for global trading integration scenarios.

    글로벌 거래 통합 시나리오를 테스트합니다.
    """

    def test_us_and_european_trading_setup(self):
        """Test setup for US (Alpaca) and European (IB) trading."""
        kis_config = KISConfig(
            app_key="key",
            secret_key="secret",
            account_number="1234-5678",
            hts_id="hts",
        )
        upbit_config = UpbitConfig(
            access_key="key",
            secret_key="secret",
        )

        # US stocks via Alpaca
        alpaca_config = AlpacaConfig(
            api_key="alpaca_key",
            secret_key="alpaca_secret",
            is_paper=True,
        )

        # European stocks via Interactive Brokers
        ib_config = InteractiveBrokersConfig(
            account_id="EU_ACCOUNT",
            host="127.0.0.1",
            port=7497,
            is_demo=True,
        )

        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            alpaca_config=alpaca_config,
            ib_config=ib_config,
        )

        # Verify all brokers are configured
        assert config.kis_config.app_key == "key"
        assert config.upbit_config.access_key == "key"
        assert config.alpaca_config.api_key == "alpaca_key"
        assert config.ib_config.account_id == "EU_ACCOUNT"

    def test_multi_market_trading_with_different_modes(self):
        """Test multi-market trading with different modes for each market."""
        kis_config = KISConfig(
            app_key="key",
            secret_key="secret",
            account_number="1234-5678",
            hts_id="hts",
            is_demo=False,  # Korea: Live mode
        )
        upbit_config = UpbitConfig(
            access_key="key",
            secret_key="secret",
        )
        alpaca_config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
            is_paper=True,  # US: Paper mode
        )
        ib_config = InteractiveBrokersConfig(
            account_id="account",
            is_demo=False,  # Europe: Live mode
        )

        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            alpaca_config=alpaca_config,
            ib_config=ib_config,
            timeout=15,
            retry_count=5,
        )

        # Verify config is complete and correct
        assert config.timeout == 15
        assert config.retry_count == 5
        assert config.kis_config.is_demo is False
        assert config.alpaca_config.is_paper is True
        assert config.ib_config.is_demo is False

    def test_config_validation_with_global_brokers(self):
        """Test configuration validation with global brokers."""
        kis_config = KISConfig(
            app_key="key",
            secret_key="secret",
            account_number="1234-5678",
            hts_id="hts",
        )
        upbit_config = UpbitConfig(
            access_key="key",
            secret_key="secret",
        )
        alpaca_config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
        )

        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            alpaca_config=alpaca_config,
        )

        # Basic validation should pass with KIS and Upbit configs
        assert config.validate() is True

    def test_global_brokers_do_not_require_validation(self):
        """Test that global brokers (Alpaca, IB) don't require validation.

        글로벌 거래소 설정은 기본 검증(KIS, Upbit)에 영향을 주지 않습니다.
        """
        kis_config = KISConfig(
            app_key="key",
            secret_key="secret",
            account_number="1234-5678",
            hts_id="hts",
        )
        upbit_config = UpbitConfig(
            access_key="key",
            secret_key="secret",
        )

        # Even without Alpaca and IB, config should validate
        config = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            alpaca_config=None,
            ib_config=None,
        )

        assert config.validate() is True


class TestGlobalTradingBrokerComparison:
    """Test cases comparing different global trading brokers.

    글로벌 거래 거래소 비교 테스트입니다.
    """

    def test_alpaca_vs_ib_configuration_structure(self):
        """Test configuration structure differences between Alpaca and IB."""
        alpaca = AlpacaConfig(
            api_key="alpaca_key",
            secret_key="alpaca_secret",
            base_url="https://paper-api.alpaca.markets",
            is_paper=True,
        )

        ib = InteractiveBrokersConfig(
            account_id="DU12345",
            host="127.0.0.1",
            port=7497,
            client_id=1,
            is_demo=True,
        )

        # Alpaca uses API-based authentication
        assert hasattr(alpaca, "api_key")
        assert hasattr(alpaca, "secret_key")
        assert hasattr(alpaca, "base_url")

        # IB uses socket connection
        assert hasattr(ib, "account_id")
        assert hasattr(ib, "host")
        assert hasattr(ib, "port")
        assert hasattr(ib, "client_id")

    def test_alpaca_base_url_variations(self):
        """Test Alpaca base URL for different trading modes."""
        paper_config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
            is_paper=True,
        )

        live_config = AlpacaConfig(
            api_key="key",
            secret_key="secret",
            is_paper=False,
            base_url="https://api.alpaca.markets",
        )

        # Different endpoints for paper and live trading
        assert "paper" in paper_config.base_url
        assert "paper" not in live_config.base_url

    def test_ib_connection_parameters(self):
        """Test Interactive Brokers connection parameters."""
        gateway_config = InteractiveBrokersConfig(
            account_id="account",
            host="gateway.ibcloud.com",
            port=4002,
        )

        local_config = InteractiveBrokersConfig(
            account_id="account",
            host="127.0.0.1",
            port=7497,
        )

        # Different hosts and ports for IB Gateway vs Local
        assert gateway_config.host != local_config.host
        assert gateway_config.port != local_config.port
