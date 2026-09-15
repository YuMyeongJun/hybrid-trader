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
class AlpacaConfig:
    """Alpaca API configuration for US stocks.

    미국 주식 거래를 위한 Alpaca API 설정입니다.

    Attributes:
        api_key (str): Alpaca API Key
        secret_key (str): Alpaca Secret Key
        base_url (str): Alpaca API base URL
        is_paper (bool): Whether to use paper trading mode. Defaults to True.
    """
    api_key: str
    secret_key: str
    base_url: str = "https://paper-api.alpaca.markets"
    is_paper: bool = True


@dataclass
class InteractiveBrokersConfig:
    """Interactive Brokers API configuration for global markets.

    글로벌 시장(유럽, 아시아 등) 거래를 위한 IB 설정입니다.

    Attributes:
        account_id (str): Interactive Brokers account ID
        host (str): IB Gateway host
        port (int): IB Gateway port
        client_id (int): Client ID for connection
        is_demo (bool): Whether to use demo mode. Defaults to True.
    """
    account_id: str
    host: str = "127.0.0.1"
    port: int = 7497
    client_id: int = 1
    is_demo: bool = True


@dataclass
class TradingConfig:
    """Main configuration class for Hybrid Trading Engine.

    하이브리드 트레이딩 엔진의 전체 설정을 관리합니다.
    한국, 미국, 유럽 등 글로벌 시장을 지원합니다.

    Attributes:
        kis_config (KISConfig): Korea Investment & Securities configuration
        upbit_config (UpbitConfig): Upbit configuration (Crypto)
        alpaca_config (Optional[AlpacaConfig]): Alpaca configuration for US stocks
        ib_config (Optional[InteractiveBrokersConfig]): Interactive Brokers config for global markets
        timeout (int): API request timeout in seconds. Defaults to 10.
        retry_count (int): Number of retries for failed requests. Defaults to 3.

    Example:
        >>> kis = KISConfig(...)
        >>> upbit = UpbitConfig(...)
        >>> alpaca = AlpacaConfig(...)
        >>> ib = InteractiveBrokersConfig(...)
        >>> config = TradingConfig(
        ...     kis_config=kis,
        ...     upbit_config=upbit,
        ...     alpaca_config=alpaca,
        ...     ib_config=ib
        ... )
    """
    kis_config: KISConfig
    upbit_config: UpbitConfig
    alpaca_config: Optional[AlpacaConfig] = None
    ib_config: Optional[InteractiveBrokersConfig] = None
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
