"""Configuration module for Hybrid Trading Engine.

This module manages API credentials and trading configurations for both
Korea Investment & Securities (KIS) and Upbit platforms.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class KISConfig:
    """Korea Investment & Securities API configuration.

    한국투자증권 API 설정을 관리하는 클래스입니다.

    Attributes:
        app_key (str): KIS Application Key
        secret_key (str): KIS Secret Key
        account_number (str): Trading account number (format: "XXXX-XXXX")
        hts_id (str): HTS ID for real-time data subscription
        is_demo (bool): Whether to use demo/paper trading mode. Defaults to True.
    """
    app_key: str
    secret_key: str
    account_number: str
    hts_id: str
    is_demo: bool = True


@dataclass
class UpbitConfig:
    """Upbit API configuration.

    업비트 API 설정을 관리하는 클래스입니다.

    Attributes:
        access_key (str): Upbit Access Key
        secret_key (str): Upbit Secret Key
    """
    access_key: str
    secret_key: str


@dataclass
class TradingConfig:
    """Main configuration class for Hybrid Trading Engine.

    하이브리드 트레이딩 엔진의 전체 설정을 관리합니다.

    Attributes:
        kis_config (KISConfig): Korea Investment & Securities configuration
        upbit_config (UpbitConfig): Upbit configuration
        timeout (int): API request timeout in seconds. Defaults to 10.
        retry_count (int): Number of retries for failed requests. Defaults to 3.

    Example:
        >>> kis = KISConfig(
        ...     app_key="your_app_key",
        ...     secret_key="your_secret_key",
        ...     account_number="1234-5678",
        ...     hts_id="your_hts_id"
        ... )
        >>> upbit = UpbitConfig(
        ...     access_key="your_access_key",
        ...     secret_key="your_secret_key"
        ... )
        >>> config = TradingConfig(kis_config=kis, upbit_config=upbit)
    """
    kis_config: KISConfig
    upbit_config: UpbitConfig
    timeout: int = 10
    retry_count: int = 3

    def validate(self) -> bool:
        """Validate configuration credentials.

        설정의 필수 항목이 모두 입력되었는지 검증합니다.

        Returns:
            bool: True if all required fields are present, False otherwise.

        Raises:
            ValueError: If required credentials are missing or empty.
        """
        missing_fields = []

        if not self.kis_config.app_key:
            missing_fields.append("KIS app_key")
        if not self.kis_config.secret_key:
            missing_fields.append("KIS secret_key")
        if not self.kis_config.account_number:
            missing_fields.append("KIS account_number")
        if not self.kis_config.hts_id:
            missing_fields.append("KIS hts_id")
        if not self.upbit_config.access_key:
            missing_fields.append("Upbit access_key")
        if not self.upbit_config.secret_key:
            missing_fields.append("Upbit secret_key")

        if missing_fields:
            raise ValueError(f"Missing required credentials: {', '.join(missing_fields)}")

        return True
