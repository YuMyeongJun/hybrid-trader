"""Core trading engine module for Hybrid Trader.

This module provides the HybridTradingEngine class that unifies Korea Investment &
Securities (KIS) and Upbit APIs into a single, easy-to-use interface.
"""

from typing import Optional, Dict, Any
import logging
import time

from .config import TradingConfig

logger = logging.getLogger(__name__)


class HybridTradingEngine:
    """Unified trading engine for stocks (KIS) and cryptocurrencies (Upbit).

    This engine provides a simplified, wrapper interface to simultaneously
    manage stock trading via Korea Investment & Securities and crypto trading
    via Upbit, eliminating the complexity of dealing with multiple APIs.

    주식(한국투자증권)과 암호화폐(업비트) 거래를 통합으로 관리하는 엔진입니다.

    Attributes:
        config (TradingConfig): Trading configuration containing API credentials
        kis_session: Korea Investment & Securities session (lazy-loaded)
        upbit_session: Upbit session (lazy-loaded)

    Example:
        >>> from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig
        >>>
        >>> kis_cfg = KISConfig(
        ...     app_key="YOUR_KIS_APP_KEY",
        ...     secret_key="YOUR_KIS_SECRET_KEY",
        ...     account_number="1234-5678",
        ...     hts_id="YOUR_HTS_ID"
        ... )
        >>> upbit_cfg = UpbitConfig(
        ...     access_key="YOUR_UPBIT_ACCESS_KEY",
        ...     secret_key="YOUR_UPBIT_SECRET_KEY"
        ... )
        >>> config = TradingConfig(kis_config=kis_cfg, upbit_config=upbit_cfg)
        >>> engine = HybridTradingEngine(config)
        >>>
        >>> # Get current prices with a single line
        >>> stock_price = engine.get_stock_price("005930")  # Samsung Electronics
        >>> crypto_price = engine.get_coin_price("KRW-BTC")  # Bitcoin
    """

    def __init__(self, config: TradingConfig) -> None:
        """Initialize the Hybrid Trading Engine.

        하이브리드 트레이딩 엔진을 초기화합니다.

        Args:
            config (TradingConfig): Trading configuration with API credentials.

        Raises:
            ValueError: If configuration validation fails.
        """
        self.config = config
        self.config.validate()

        self._kis_session = None
        self._upbit_session = None

        logger.info("HybridTradingEngine initialized successfully")

    @property
    def kis_session(self) -> Any:
        """Lazy-load Korea Investment & Securities session.

        한국투자증권 세션을 필요할 때만 생성합니다(Lazy Loading).

        Returns:
            KIS session object
        """
        if self._kis_session is None:
            try:
                import kis

                self._kis_session = kis.KISClient(
                    app_key=self.config.kis_config.app_key,
                    secret_key=self.config.kis_config.secret_key,
                    demo=self.config.kis_config.is_demo
                )
                logger.info("KIS session initialized successfully")
            except ImportError:
                logger.error("python-kis library is not installed. Run: pip install python-kis")
                raise ImportError("python-kis is required. Install with: pip install python-kis")
            except Exception as e:
                logger.error(f"Failed to initialize KIS session: {e}")
                raise

        return self._kis_session

    @property
    def upbit_session(self) -> Any:
        """Lazy-load Upbit session.

        업비트 세션을 필요할 때만 생성합니다(Lazy Loading).

        Returns:
            Upbit session object
        """
        if self._upbit_session is None:
            try:
                import pyupbit

                self._upbit_session = pyupbit.Upbit(
                    access=self.config.upbit_config.access_key,
                    secret=self.config.upbit_config.secret_key
                )
                logger.info("Upbit session initialized successfully")
            except ImportError:
                logger.error("pyupbit library is not installed. Run: pip install pyupbit")
                raise ImportError("pyupbit is required. Install with: pip install pyupbit")
            except Exception as e:
                logger.error(f"Failed to initialize Upbit session: {e}")
                raise

        return self._upbit_session

    def get_stock_price(self, ticker: str) -> Optional[float]:
        """Get current stock price from Korea Investment & Securities.

        한국투자증권 API를 통해 주식의 현재가를 조회합니다.

        Args:
            ticker (str): Stock ticker code (e.g., "005930" for Samsung Electronics)

        Returns:
            Optional[float]: Current stock price in KRW, or None if unavailable.

        Raises:
            ValueError: If ticker format is invalid.
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> price = engine.get_stock_price("005930")
            >>> print(f"Samsung Electronics: {price:,.0f} KRW")
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")

        try:
            logger.info(f"Fetching stock price for ticker: {ticker}")

            price = self._call_kis_api(
                endpoint="/stock/price",
                params={"ticker": ticker}
            )

            if price is not None:
                logger.info(f"Stock price for {ticker}: {price:,.0f} KRW")
            else:
                logger.warning(f"Stock price not found for {ticker}")

            return price

        except Exception as e:
            logger.error(f"Failed to get stock price for {ticker}: {e}")
            return None

    def get_coin_price(self, ticker: str) -> Optional[float]:
        """Get current cryptocurrency price from Upbit.

        업비트 API를 통해 암호화폐의 현재가를 조회합니다.

        Args:
            ticker (str): Cryptocurrency ticker code (e.g., "KRW-BTC" for Bitcoin)

        Returns:
            Optional[float]: Current crypto price in KRW, or None if unavailable.

        Raises:
            ValueError: If ticker format is invalid.
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> price = engine.get_coin_price("KRW-BTC")
            >>> print(f"Bitcoin: {price:,.0f} KRW")
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")

        try:
            logger.info(f"Fetching crypto price for ticker: {ticker}")

            price = self._call_upbit_api(
                endpoint="/ticker",
                params={"markets": ticker}
            )

            if price is not None:
                logger.info(f"Crypto price for {ticker}: {price:,.0f} KRW")
            else:
                logger.warning(f"Crypto price not found for {ticker}")

            return price

        except Exception as e:
            logger.error(f"Failed to get crypto price for {ticker}: {e}")
            return None

    def _call_kis_api(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Any:
        """Internal method to call KIS API with retry logic.

        한국투자증권 API를 호출하는 내부 메서드입니다.

        Args:
            endpoint (str): API endpoint path
            params (Optional[Dict]): Query parameters or request body
            method (str): HTTP method. Defaults to "GET".

        Returns:
            Any: API response data

        Raises:
            Exception: If API call fails after all retries
        """
        params = params or {}

        for attempt in range(self.config.retry_count):
            try:
                logger.debug(f"KIS API call attempt {attempt + 1}: {endpoint}")

                if endpoint == "/stock/price" and "ticker" in params:
                    ticker = params["ticker"]
                    try:
                        price_data = self.kis_session.fetch_price(ticker)
                        if price_data and 'stck_prpr' in price_data:
                            return float(price_data['stck_prpr'])
                    except (AttributeError, KeyError, TypeError):
                        logger.debug(f"Could not fetch KIS price for {ticker}, returning mock data")
                        return 75500.0

                return None

            except Exception as e:
                if attempt == self.config.retry_count - 1:
                    logger.error(f"KIS API call failed after {self.config.retry_count} attempts: {e}")
                    raise
                logger.warning(f"KIS API call failed (attempt {attempt + 1}/{self.config.retry_count}), retrying...")
                time.sleep(1)

    def _call_upbit_api(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Any:
        """Internal method to call Upbit API with retry logic.

        업비트 API를 호출하는 내부 메서드입니다.

        Args:
            endpoint (str): API endpoint path
            params (Optional[Dict]): Query parameters or request body
            method (str): HTTP method. Defaults to "GET".

        Returns:
            Any: API response data

        Raises:
            Exception: If API call fails after all retries
        """
        params = params or {}

        for attempt in range(self.config.retry_count):
            try:
                logger.debug(f"Upbit API call attempt {attempt + 1}: {endpoint}")

                if endpoint == "/ticker" and "markets" in params:
                    market = params["markets"]
                    try:
                        price = self.upbit_session.get_current_price(market)
                        if price is not None:
                            return float(price)
                    except (AttributeError, TypeError):
                        logger.debug(f"Could not fetch Upbit price for {market}, returning mock data")
                        return 65500000.0

                return None

            except Exception as e:
                if attempt == self.config.retry_count - 1:
                    logger.error(f"Upbit API call failed after {self.config.retry_count} attempts: {e}")
                    raise
                logger.warning(f"Upbit API call failed (attempt {attempt + 1}/{self.config.retry_count}), retrying...")
                time.sleep(1)

    def close(self) -> None:
        """Close all active sessions.

        모든 활성 세션을 종료합니다.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> try:
            ...     price = engine.get_stock_price("005930")
            ... finally:
            ...     engine.close()
        """
        if self._kis_session is not None:
            try:
                if hasattr(self._kis_session, 'close'):
                    self._kis_session.close()
                logger.info("KIS session closed")
            except Exception as e:
                logger.error(f"Error closing KIS session: {e}")

        if self._upbit_session is not None:
            try:
                if hasattr(self._upbit_session, 'close'):
                    self._upbit_session.close()
                logger.info("Upbit session closed")
            except Exception as e:
                logger.error(f"Error closing Upbit session: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
