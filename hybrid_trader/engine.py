"""Core trading engine module for Hybrid Trader.

This module provides the HybridTradingEngine class that unifies Korea Investment &
Securities (KIS) and Upbit APIs into a single, easy-to-use interface.
"""

from typing import Optional, Dict, Any, List
import logging
import time
import math

from .config import TradingConfig
from .exceptions import (
    HybridTraderException,
    UnsupportedOperationError,
    InvalidTickerError,
    APIConnectionError,
    ConfigurationError,
    SessionNotInitializedError,
)

logger = logging.getLogger(__name__)


class HybridTradingEngine:
    """Unified trading engine for global stock trading and cryptocurrencies.

    This engine provides a simplified, wrapper interface to simultaneously
    manage Korean stock trading via Korea Investment & Securities, US stock trading
    via Alpaca, crypto trading via Upbit, and global market trading via Interactive Brokers,
    eliminating the complexity of dealing with multiple APIs.

    한국 주식(한국투자증권), 미국 주식(알파카), 암호화폐(업비트), 글로벌 시장(Interactive Brokers) 거래를 통합으로 관리하는 엔진입니다.

    Attributes:
        config (TradingConfig): Trading configuration containing API credentials
        kis_session: Korea Investment & Securities session (lazy-loaded)
        upbit_session: Upbit session (lazy-loaded)
        alpaca_session: Alpaca session for US stocks (lazy-loaded)
        ib_session: Interactive Brokers session for global markets (lazy-loaded)

    Example:
        >>> from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig, AlpacaConfig, InteractiveBrokersConfig
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
        >>> alpaca_cfg = AlpacaConfig(
        ...     api_key="YOUR_ALPACA_API_KEY",
        ...     secret_key="YOUR_ALPACA_SECRET_KEY",
        ...     base_url="https://paper-api.alpaca.markets",
        ...     is_paper=True
        ... )
        >>> ib_cfg = InteractiveBrokersConfig(
        ...     account_id="YOUR_IB_ACCOUNT_ID",
        ...     host="127.0.0.1",
        ...     port=7497
        ... )
        >>> config = TradingConfig(kis_config=kis_cfg, upbit_config=upbit_cfg, alpaca_config=alpaca_cfg, ib_config=ib_cfg)
        >>> engine = HybridTradingEngine(config)
        >>>
        >>> # Get current prices with a single line
        >>> stock_price = engine.get_stock_price("005930")  # Samsung Electronics
        >>> crypto_price = engine.get_coin_price("KRW-BTC")  # Bitcoin
        >>> us_stock_price = engine.get_us_stock_price("AAPL")  # Apple (US stock)
        >>> eu_stock_price = engine.get_eu_stock_price("BMW")  # BMW (European stock)
    """

    def __init__(self, config: TradingConfig) -> None:
        """Initialize the Hybrid Trading Engine.

        하이브리드 트레이딩 엔진을 초기화합니다.

        Args:
            config (TradingConfig): Trading configuration with API credentials.

        Raises:
            ConfigurationError: If configuration validation fails.
        """
        self.config = config
        try:
            self.config.validate()
        except Exception as e:
            raise ConfigurationError(
                config_key="TradingConfig",
                message=f"Configuration validation failed: {str(e)}"
            ) from e

        self._kis_session = None
        self._upbit_session = None
        self._alpaca_session = None
        self._ib_session = None

        logger.info("HybridTradingEngine initialized successfully")

    @property
    def kis_session(self) -> Any:
        """Lazy-load Korea Investment & Securities session.

        한국투자증권 세션을 필요할 때만 생성합니다(Lazy Loading).

        Returns:
            KIS session object

        Raises:
            SessionNotInitializedError: If KIS session initialization fails.
            APIConnectionError: If API connection fails.
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
            except ImportError as e:
                logger.error("python-kis library is not installed. Run: pip install python-kis")
                raise SessionNotInitializedError(
                    session_name="KIS",
                    required_config="python-kis library",
                    message="python-kis library is not installed. Install with: pip install python-kis"
                ) from e
            except Exception as e:
                logger.error(f"Failed to initialize KIS session: {e}")
                raise APIConnectionError(
                    api_name="KIS",
                    original_error=e,
                    message=f"Failed to connect to KIS API during session initialization"
                ) from e

        return self._kis_session

    @property
    def upbit_session(self) -> Any:
        """Lazy-load Upbit session.

        업비트 세션을 필요할 때만 생성합니다(Lazy Loading).

        Returns:
            Upbit session object

        Raises:
            SessionNotInitializedError: If Upbit session initialization fails.
            APIConnectionError: If API connection fails.
        """
        if self._upbit_session is None:
            try:
                import pyupbit

                self._upbit_session = pyupbit.Upbit(
                    access=self.config.upbit_config.access_key,
                    secret=self.config.upbit_config.secret_key
                )
                logger.info("Upbit session initialized successfully")
            except ImportError as e:
                logger.error("pyupbit library is not installed. Run: pip install pyupbit")
                raise SessionNotInitializedError(
                    session_name="Upbit",
                    required_config="pyupbit library",
                    message="pyupbit library is not installed. Install with: pip install pyupbit"
                ) from e
            except Exception as e:
                logger.error(f"Failed to initialize Upbit session: {e}")
                raise APIConnectionError(
                    api_name="Upbit",
                    original_error=e,
                    message=f"Failed to connect to Upbit API during session initialization"
                ) from e

        return self._upbit_session

    @property
    def alpaca_session(self) -> Any:
        """Lazy-load Alpaca session for US stocks.

        알파카 세션을 필요할 때만 생성합니다(Lazy Loading).

        Returns:
            Alpaca session object

        Raises:
            SessionNotInitializedError: If Alpaca session initialization fails.
            APIConnectionError: If API connection fails.
        """
        if self._alpaca_session is None:
            # Alpaca config은 선택사항이므로 None일 수 있습니다
            if self.config.alpaca_config is None:
                raise SessionNotInitializedError(
                    session_name="Alpaca",
                    required_config="alpaca_config",
                    message="Alpaca configuration is not set. Set alpaca_config in TradingConfig to use US stock trading."
                )

            try:
                from alpaca_trade_api import REST

                # 알파카 REST API 세션 생성
                self._alpaca_session = REST(
                    key_id=self.config.alpaca_config.api_key,
                    secret_key=self.config.alpaca_config.secret_key,
                    base_url=self.config.alpaca_config.base_url,
                    api_version='v2'
                )
                logger.info("Alpaca session initialized successfully")
            except ImportError as e:
                logger.error("alpaca-trade-api library is not installed. Run: pip install alpaca-trade-api")
                raise SessionNotInitializedError(
                    session_name="Alpaca",
                    required_config="alpaca-trade-api library",
                    message="alpaca-trade-api library is not installed. Install with: pip install alpaca-trade-api"
                ) from e
            except Exception as e:
                logger.error(f"Failed to initialize Alpaca session: {e}")
                raise APIConnectionError(
                    api_name="Alpaca",
                    original_error=e,
                    message=f"Failed to connect to Alpaca API during session initialization"
                ) from e

        return self._alpaca_session

    @property
    def ib_session(self) -> Any:
        """Lazy-load Interactive Brokers session for global markets.

        Interactive Brokers 세션을 필요할 때만 생성합니다(Lazy Loading).
        유럽/글로벌 주식 거래에 사용됩니다.

        Returns:
            Interactive Brokers session object

        Raises:
            SessionNotInitializedError: If IB session initialization fails.
            APIConnectionError: If API connection fails.
        """
        if self._ib_session is None:
            # Interactive Brokers config은 선택사항이므로 None일 수 있습니다
            if self.config.ib_config is None:
                raise SessionNotInitializedError(
                    session_name="InteractiveBrokers",
                    required_config="ib_config",
                    message="Interactive Brokers configuration is not set. Set ib_config in TradingConfig to use global stock trading."
                )

            try:
                from ib_insync import IB

                # Interactive Brokers 세션 생성
                ib = IB()

                # IB Gateway 또는 Trader Workstation에 연결
                ib.connect(
                    host=self.config.ib_config.host,
                    port=self.config.ib_config.port,
                    clientId=self.config.ib_config.client_id
                )

                self._ib_session = ib
                logger.info(f"Interactive Brokers session initialized successfully (host={self.config.ib_config.host}, port={self.config.ib_config.port})")
            except ImportError as e:
                logger.error("ib-insync library is not installed. Run: pip install ib-insync")
                raise SessionNotInitializedError(
                    session_name="InteractiveBrokers",
                    required_config="ib-insync library",
                    message="ib-insync library is not installed. Install with: pip install ib-insync"
                ) from e
            except Exception as e:
                logger.error(f"Failed to initialize Interactive Brokers session: {e}")
                raise APIConnectionError(
                    api_name="InteractiveBrokers",
                    original_error=e,
                    message=f"Failed to connect to Interactive Brokers API during session initialization. Make sure IB Gateway or TWS is running on {self.config.ib_config.host}:{self.config.ib_config.port}"
                ) from e

        return self._ib_session

    def get_stock_price(self, ticker: str) -> Optional[float]:
        """Get current stock price from Korea Investment & Securities.

        한국투자증권 API를 통해 주식의 현재가를 조회합니다.

        Args:
            ticker (str): Stock ticker code (e.g., "005930" for Samsung Electronics)

        Returns:
            Optional[float]: Current stock price in KRW, or None if unavailable.

        Raises:
            InvalidTickerError: If ticker format is invalid.
            APIConnectionError: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> price = engine.get_stock_price("005930")
            >>> print(f"Samsung Electronics: {price:,.0f} KRW")
        """
        if not ticker or not isinstance(ticker, str):
            raise InvalidTickerError(
                ticker=ticker,
                market="stock",
                message="Ticker must be a non-empty string"
            )

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

        except InvalidTickerError:
            raise
        except HybridTraderException:
            raise
        except Exception as e:
            logger.error(f"Failed to get stock price for {ticker}: {e}")
            raise APIConnectionError(
                api_name="KIS",
                original_error=e,
                message=f"Failed to fetch stock price for {ticker}"
            ) from e

    def get_coin_price(self, ticker: str) -> Optional[float]:
        """Get current cryptocurrency price from Upbit.

        업비트 API를 통해 암호화폐의 현재가를 조회합니다.

        Args:
            ticker (str): Cryptocurrency ticker code (e.g., "KRW-BTC" for Bitcoin)

        Returns:
            Optional[float]: Current crypto price in KRW, or None if unavailable.

        Raises:
            InvalidTickerError: If ticker format is invalid.
            APIConnectionError: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> price = engine.get_coin_price("KRW-BTC")
            >>> print(f"Bitcoin: {price:,.0f} KRW")
        """
        if not ticker or not isinstance(ticker, str):
            raise InvalidTickerError(
                ticker=ticker,
                market="crypto",
                message="Ticker must be a non-empty string"
            )

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

        except InvalidTickerError:
            raise
        except HybridTraderException:
            raise
        except Exception as e:
            logger.error(f"Failed to get crypto price for {ticker}: {e}")
            raise APIConnectionError(
                api_name="Upbit",
                original_error=e,
                message=f"Failed to fetch crypto price for {ticker}"
            ) from e

    def get_us_stock_price(self, ticker: str) -> Optional[float]:
        """Get current US stock price from Alpaca.

        알파카 API를 통해 미국 주식의 현재가를 조회합니다.

        Args:
            ticker (str): US stock ticker code (e.g., "AAPL" for Apple)

        Returns:
            Optional[float]: Current stock price in USD, or None if unavailable.

        Raises:
            InvalidTickerError: If ticker format is invalid.
            APIConnectionError: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> price = engine.get_us_stock_price("AAPL")
            >>> print(f"Apple: ${price:,.2f}")
        """
        if not ticker or not isinstance(ticker, str):
            raise InvalidTickerError(
                ticker=ticker,
                market="us_stock",
                message="Ticker must be a non-empty string"
            )

        try:
            logger.info(f"Fetching US stock price for ticker: {ticker}")

            price = self._call_alpaca_api(
                endpoint="/quotes/latest",
                params={"symbols": ticker}
            )

            if price is not None:
                logger.info(f"US stock price for {ticker}: ${price:,.2f}")
            else:
                logger.warning(f"US stock price not found for {ticker}")

            return price

        except InvalidTickerError:
            raise
        except HybridTraderException:
            raise
        except Exception as e:
            logger.error(f"Failed to get US stock price for {ticker}: {e}")
            raise APIConnectionError(
                api_name="Alpaca",
                original_error=e,
                message=f"Failed to fetch US stock price for {ticker}"
            ) from e

    def _call_kis_api(self, endpoint: str, params=None, method: str = 'GET') -> Any:
        params = params or {}
        if method != 'GET' or endpoint != '/stock/price' or 'ticker' not in params:
            raise UnsupportedOperationError('KIS', endpoint)
        try:
            result = self.kis_session.fetch_price(params['ticker'])
            return self._validated_price(result['stck_prpr'])
        except Exception as exc:
            raise APIConnectionError(api_name='KIS', original_error=exc) from exc

    def _call_upbit_api(self, endpoint: str, params=None, method: str = 'GET') -> Any:
        params = params or {}
        if method != 'GET' or endpoint != '/ticker' or 'markets' not in params:
            raise UnsupportedOperationError('Upbit', endpoint)
        try:
            import pyupbit
            return self._validated_price(pyupbit.get_current_price(params['markets']))
        except Exception as exc:
            raise APIConnectionError(api_name='Upbit', original_error=exc) from exc

    def _call_alpaca_api(self, endpoint: str, params=None, method: str = 'GET') -> Any:
        params = params or {}
        if method != 'GET' or endpoint != '/quotes/latest' or 'symbols' not in params:
            raise UnsupportedOperationError('Alpaca', endpoint)
        try:
            symbol = params['symbols']
            quotes = self.alpaca_session.get_latest_quotes(symbol, feed='sip')
            quote = quotes[symbol]
            price = getattr(quote, 'ap', None)
            if price is None:
                price = quote.ask_price
            return self._validated_price(price)
        except Exception as exc:
            raise APIConnectionError(api_name='Alpaca', original_error=exc) from exc

    @staticmethod
    def _validated_price(value: Any) -> float:
        if isinstance(value, bool) or value is None:
            raise ValueError('Market price must be a finite positive number')
        price = float(value)
        if not math.isfinite(price) or price <= 0:
            raise ValueError('Market price must be a finite positive number')
        return price

    def buy_stock(self, ticker: str, qty: int, price: float) -> Dict[str, Any]:
        """Buy stocks through Korea Investment & Securities.

        한국투자증권을 통해 주식을 매수합니다.

        Args:
            ticker (str): Stock ticker code (e.g., "005930" for Samsung Electronics)
            qty (int): Quantity to buy
            price (float): Purchase price per share in KRW

        Returns:
            Dict[str, Any]: Order information containing order_id, status, etc.

        Raises:
            ValueError: If parameters are invalid.
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> result = engine.buy_stock("005930", qty=10, price=70000)
            >>> print(result['order_id'])
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
            raise ValueError("Price must be a positive number")

        try:
            logger.info(f"Buying stock: ticker={ticker}, qty={qty}, price={price}")

            order_result = self._call_kis_api(
                endpoint="/stock/buy",
                params={
                    "ticker": ticker,
                    "qty": qty,
                    "price": price,
                    "account": self.config.kis_config.account_number
                },
                method="POST"
            )

            logger.info(f"Stock buy order placed successfully: {order_result}")
            return order_result

        except Exception as e:
            logger.error(f"Failed to buy stock {ticker}: {e}")
            raise

    def sell_stock(self, ticker: str, qty: int, price: float) -> Dict[str, Any]:
        """Sell stocks through Korea Investment & Securities.

        한국투자증권을 통해 주식을 매도합니다.

        Args:
            ticker (str): Stock ticker code (e.g., "005930" for Samsung Electronics)
            qty (int): Quantity to sell
            price (float): Selling price per share in KRW

        Returns:
            Dict[str, Any]: Order information containing order_id, status, etc.

        Raises:
            ValueError: If parameters are invalid.
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> result = engine.sell_stock("005930", qty=5, price=75000)
            >>> print(result['order_id'])
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
            raise ValueError("Price must be a positive number")

        try:
            logger.info(f"Selling stock: ticker={ticker}, qty={qty}, price={price}")

            order_result = self._call_kis_api(
                endpoint="/stock/sell",
                params={
                    "ticker": ticker,
                    "qty": qty,
                    "price": price,
                    "account": self.config.kis_config.account_number
                },
                method="POST"
            )

            logger.info(f"Stock sell order placed successfully: {order_result}")
            return order_result

        except Exception as e:
            logger.error(f"Failed to sell stock {ticker}: {e}")
            raise

    def buy_coin(self, market: str, krw: float) -> Dict[str, Any]:
        """Buy cryptocurrency through Upbit.

        업비트를 통해 암호화폐를 매수합니다.

        Args:
            market (str): Cryptocurrency market code (e.g., "KRW-BTC" for Bitcoin)
            krw (float): Amount in KRW to spend

        Returns:
            Dict[str, Any]: Order information containing order_id, status, etc.

        Raises:
            ValueError: If parameters are invalid.
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> result = engine.buy_coin("KRW-BTC", krw=100000)
            >>> print(result['order_id'])
        """
        if not market or not isinstance(market, str):
            raise ValueError("Market must be a non-empty string")
        if isinstance(krw, bool) or not isinstance(krw, (int, float)) or not math.isfinite(krw) or krw <= 0:
            raise ValueError("KRW amount must be a positive number")

        try:
            logger.info(f"Buying coin: market={market}, krw={krw}")

            order_result = self._call_upbit_api(
                endpoint="/orders",
                params={
                    "market": market,
                    "side": "bid",
                    "price": krw,
                    "ord_type": "price"
                },
                method="POST"
            )

            logger.info(f"Coin buy order placed successfully: {order_result}")
            return order_result

        except Exception as e:
            logger.error(f"Failed to buy coin {market}: {e}")
            raise

    def sell_coin(self, market: str, qty: float) -> Dict[str, Any]:
        """Sell cryptocurrency through Upbit.

        업비트를 통해 암호화폐를 매도합니다.

        Args:
            market (str): Cryptocurrency market code (e.g., "KRW-BTC" for Bitcoin)
            qty (float): Quantity of cryptocurrency to sell

        Returns:
            Dict[str, Any]: Order information containing order_id, status, etc.

        Raises:
            ValueError: If parameters are invalid.
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> result = engine.sell_coin("KRW-BTC", qty=0.5)
            >>> print(result['order_id'])
        """
        if not market or not isinstance(market, str):
            raise ValueError("Market must be a non-empty string")
        if isinstance(qty, bool) or not isinstance(qty, (int, float)) or not math.isfinite(qty) or qty <= 0:
            raise ValueError("Quantity must be a positive number")

        try:
            logger.info(f"Selling coin: market={market}, qty={qty}")

            order_result = self._call_upbit_api(
                endpoint="/orders",
                params={
                    "market": market,
                    "side": "ask",
                    "volume": qty,
                    "ord_type": "market"
                },
                method="POST"
            )

            logger.info(f"Coin sell order placed successfully: {order_result}")
            return order_result

        except Exception as e:
            logger.error(f"Failed to sell coin {market}: {e}")
            raise

    def buy_us_stock(self, ticker: str, qty: int, price: float) -> Dict[str, Any]:
        """Buy US stocks through Alpaca.

        알파카를 통해 미국 주식을 매수합니다.

        Args:
            ticker (str): US stock ticker code (e.g., "AAPL" for Apple)
            qty (int): Quantity to buy
            price (float): Purchase price per share in USD

        Returns:
            Dict[str, Any]: Order information containing order_id, status, etc.

        Raises:
            ValueError: If parameters are invalid.
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> result = engine.buy_us_stock("AAPL", qty=10, price=150.00)
            >>> print(result['order_id'])
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
            raise ValueError("Price must be a positive number")

        try:
            logger.info(f"Buying US stock: ticker={ticker}, qty={qty}, price=${price:.2f}")

            order_result = self._call_alpaca_api(
                endpoint="/orders",
                params={
                    "symbol": ticker,
                    "qty": qty,
                    "side": "buy",
                    "type": "limit",
                    "time_in_force": "day",
                    "limit_price": price
                },
                method="POST"
            )

            logger.info(f"US stock buy order placed successfully: {order_result}")
            return order_result

        except Exception as e:
            logger.error(f"Failed to buy US stock {ticker}: {e}")
            raise

    def sell_us_stock(self, ticker: str, qty: int, price: float) -> Dict[str, Any]:
        """Sell US stocks through Alpaca.

        알파카를 통해 미국 주식을 매도합니다.

        Args:
            ticker (str): US stock ticker code (e.g., "AAPL" for Apple)
            qty (int): Quantity to sell
            price (float): Selling price per share in USD

        Returns:
            Dict[str, Any]: Order information containing order_id, status, etc.

        Raises:
            ValueError: If parameters are invalid.
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> result = engine.sell_us_stock("AAPL", qty=5, price=155.00)
            >>> print(result['order_id'])
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
            raise ValueError("Price must be a positive number")

        try:
            logger.info(f"Selling US stock: ticker={ticker}, qty={qty}, price=${price:.2f}")

            order_result = self._call_alpaca_api(
                endpoint="/orders",
                params={
                    "symbol": ticker,
                    "qty": qty,
                    "side": "sell",
                    "type": "limit",
                    "time_in_force": "day",
                    "limit_price": price
                },
                method="POST"
            )

            logger.info(f"US stock sell order placed successfully: {order_result}")
            return order_result

        except Exception as e:
            logger.error(f"Failed to sell US stock {ticker}: {e}")
            raise

    def get_stock_balance(self) -> Dict[str, Any]:
        """Get stock portfolio balance from Korea Investment & Securities.

        한국투자증권에서 주식 잔고를 조회합니다.

        Returns:
            Dict[str, Any]: Stock balance information including holdings, valuations, etc.

        Raises:
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> balance = engine.get_stock_balance()
            >>> print(f"Total valuation: {balance['total_valuation']:,.0f} KRW")
        """
        try:
            logger.info("Fetching stock balance from KIS")

            balance = self._call_kis_api(
                endpoint="/accounts/balance",
                params={"account": self.config.kis_config.account_number},
                method="GET"
            )

            logger.info(f"Stock balance retrieved successfully")
            return balance or {}

        except Exception as e:
            logger.error(f"Failed to get stock balance: {e}")
            raise

    def get_coin_balance(self) -> Dict[str, Any]:
        """Get cryptocurrency portfolio balance from Upbit.

        업비트에서 암호화폐 잔고를 조회합니다.

        Returns:
            Dict[str, Any]: Crypto balance information including holdings, valuations, etc.

        Raises:
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> balance = engine.get_coin_balance()
            >>> print(f"Bitcoin holdings: {balance.get('KRW-BTC', {}).get('balance', 0)}")
        """
        try:
            logger.info("Fetching coin balance from Upbit")

            balance = self._call_upbit_api(
                endpoint="/accounts",
                params={},
                method="GET"
            )

            logger.info(f"Coin balance retrieved successfully")
            return balance or {}

        except Exception as e:
            logger.error(f"Failed to get coin balance: {e}")
            raise

    def get_total_balance(self) -> Dict[str, Any]:
        """Get total balance combining stocks and cryptocurrencies.

        주식과 암호화폐 잔고를 합산한 전체 자산을 조회합니다.

        Returns:
            Dict[str, Any]: Combined balance with stocks, coins, total valuation, and cash.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> total = engine.get_total_balance()
            >>> print(f"Total assets: {total['total_valuation']:,.0f} KRW")
        """
        try:
            logger.info("Fetching total balance (stocks + coins)")

            stock_balance = self.get_stock_balance()
            coin_balance = self.get_coin_balance()

            total_valuation = 0
            if stock_balance:
                total_valuation += stock_balance.get("total_valuation", 0)
            if coin_balance:
                total_valuation += coin_balance.get("total_valuation", 0)

            result = {
                "stocks": stock_balance,
                "coins": coin_balance,
                "total_valuation": total_valuation,
                "timestamp": time.time()
            }

            logger.info(f"Total balance: {total_valuation:,.0f} KRW")
            return result

        except Exception as e:
            logger.error(f"Failed to get total balance: {e}")
            raise

    def get_order_history(self, ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get order history for a specific stock or crypto.

        특정 종목의 주문 히스토리를 조회합니다.

        Args:
            ticker (str): Stock/Crypto ticker code (e.g., "005930" for stock or "KRW-BTC" for crypto)
            limit (int): Maximum number of orders to retrieve. Defaults to 10.

        Returns:
            List[Dict[str, Any]]: List of order information including order_id, price, quantity, status, etc.

        Raises:
            ValueError: If parameters are invalid.
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> history = engine.get_order_history("005930", limit=20)
            >>> for order in history:
            ...     print(f"{order['ticker']}: {order['qty']} @ {order['price']}")
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")

        try:
            logger.info(f"Fetching order history for {ticker} (limit={limit})")

            # Determine if it's stock or crypto based on ticker format
            is_crypto = ticker.startswith("KRW-")

            if is_crypto:
                endpoint = "/orders"
                params = {"market": ticker, "limit": limit}
            else:
                endpoint = "/orders/history"
                params = {"ticker": ticker, "account": self.config.kis_config.account_number, "limit": limit}

            history = self._call_kis_api(
                endpoint=endpoint,
                params=params,
                method="GET"
            ) if not is_crypto else self._call_upbit_api(
                endpoint=endpoint,
                params=params,
                method="GET"
            )

            logger.info(f"Order history retrieved: {len(history or []) if isinstance(history, list) else 0} orders")
            return history if isinstance(history, list) else []

        except Exception as e:
            logger.error(f"Failed to get order history for {ticker}: {e}")
            raise

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order.

        미체결 주문을 취소합니다.

        Args:
            order_id (str): Order ID to cancel

        Returns:
            bool: True if cancellation was successful, False otherwise.

        Raises:
            ValueError: If order_id is invalid.
            Exception: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> success = engine.cancel_order("order_123456")
            >>> print(f"Cancellation: {'Success' if success else 'Failed'}")
        """
        if not order_id or not isinstance(order_id, str):
            raise ValueError("Order ID must be a non-empty string")

        try:
            logger.info(f"Cancelling order: {order_id}")

            # Try both KIS and Upbit APIs to cancel the order
            result = None

            try:
                result = self._call_kis_api(
                    endpoint="/orders/cancel",
                    params={"order_id": order_id},
                    method="DELETE"
                )
            except:
                logger.debug(f"KIS order cancellation failed for {order_id}, trying Upbit")
                result = self._call_upbit_api(
                    endpoint=f"/orders/{order_id}",
                    params={},
                    method="DELETE"
                )

            if result:
                logger.info(f"Order {order_id} cancelled successfully")
                return True
            else:
                logger.warning(f"Order cancellation result unclear for {order_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            raise

    def get_eu_stock_price(self, ticker: str) -> Optional[float]:
        """Get current European stock price from Interactive Brokers.

        Interactive Brokers를 통해 유럽 주식의 현재가를 조회합니다.

        Args:
            ticker (str): Stock ticker code (e.g., "BMW" for BMW, "SAP" for SAP SE)

        Returns:
            Optional[float]: Current stock price in EUR, or None if unavailable.

        Raises:
            InvalidTickerError: If ticker format is invalid.
            SessionNotInitializedError: If IB session not configured.
            APIConnectionError: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> price = engine.get_eu_stock_price("BMW")
            >>> print(f"BMW: {price:,.2f} EUR")
        """
        if not ticker or not isinstance(ticker, str):
            raise InvalidTickerError(
                ticker=ticker,
                market="eu_stock",
                message="Ticker must be a non-empty string"
            )

        try:
            logger.info(f"Fetching EU stock price for ticker: {ticker}")

            price = self._call_ib_api(
                endpoint="/ticker/price",
                params={"ticker": ticker, "market": "EUREX"}
            )

            if price is not None:
                logger.info(f"EU stock price for {ticker}: {price:,.2f} EUR")
            else:
                logger.warning(f"EU stock price not found for {ticker}")

            return price

        except InvalidTickerError:
            raise
        except HybridTraderException:
            raise
        except Exception as e:
            logger.error(f"Failed to get EU stock price for {ticker}: {e}")
            raise APIConnectionError(
                api_name="InteractiveBrokers",
                original_error=e,
                message=f"Failed to fetch EU stock price for {ticker}"
            ) from e

    def buy_eu_stock(self, ticker: str, qty: int, price: float) -> Dict[str, Any]:
        """Buy European stocks through Interactive Brokers.

        Interactive Brokers를 통해 유럽 주식을 매수합니다.

        Args:
            ticker (str): Stock ticker code (e.g., "BMW" for BMW)
            qty (int): Quantity to buy
            price (float): Purchase price per share in EUR

        Returns:
            Dict[str, Any]: Order information containing order_id, status, etc.

        Raises:
            ValueError: If parameters are invalid.
            SessionNotInitializedError: If IB session not configured.
            APIConnectionError: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> result = engine.buy_eu_stock("BMW", qty=10, price=92.50)
            >>> print(result['order_id'])
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
            raise ValueError("Price must be a positive number")

        try:
            logger.info(f"Buying EU stock: ticker={ticker}, qty={qty}, price={price} EUR")

            order_result = self._call_ib_api(
                endpoint="/orders/buy",
                params={
                    "ticker": ticker,
                    "qty": qty,
                    "price": price,
                    "account": self.config.ib_config.account_id,
                    "market": "EUREX"
                },
                method="POST"
            )

            logger.info(f"EU stock buy order placed successfully: {order_result}")
            return order_result

        except Exception as e:
            logger.error(f"Failed to buy EU stock {ticker}: {e}")
            raise

    def sell_eu_stock(self, ticker: str, qty: int, price: float) -> Dict[str, Any]:
        """Sell European stocks through Interactive Brokers.

        Interactive Brokers를 통해 유럽 주식을 매도합니다.

        Args:
            ticker (str): Stock ticker code (e.g., "BMW" for BMW)
            qty (int): Quantity to sell
            price (float): Selling price per share in EUR

        Returns:
            Dict[str, Any]: Order information containing order_id, status, etc.

        Raises:
            ValueError: If parameters are invalid.
            SessionNotInitializedError: If IB session not configured.
            APIConnectionError: If API request fails after retry attempts.

        Example:
            >>> engine = HybridTradingEngine(config)
            >>> result = engine.sell_eu_stock("BMW", qty=5, price=95.00)
            >>> print(result['order_id'])
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
            raise ValueError("Price must be a positive number")

        try:
            logger.info(f"Selling EU stock: ticker={ticker}, qty={qty}, price={price} EUR")

            order_result = self._call_ib_api(
                endpoint="/orders/sell",
                params={
                    "ticker": ticker,
                    "qty": qty,
                    "price": price,
                    "account": self.config.ib_config.account_id,
                    "market": "EUREX"
                },
                method="POST"
            )

            logger.info(f"EU stock sell order placed successfully: {order_result}")
            return order_result

        except Exception as e:
            logger.error(f"Failed to sell EU stock {ticker}: {e}")
            raise

    def _call_ib_api(self, endpoint: str, params=None, method: str = 'GET') -> Any:
        if self.config.ib_config is None:
            raise SessionNotInitializedError(
                session_name='InteractiveBrokers', required_config='ib_config')
        raise UnsupportedOperationError('InteractiveBrokers', endpoint)

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

        if self._alpaca_session is not None:
            try:
                if hasattr(self._alpaca_session, 'close'):
                    self._alpaca_session.close()
                logger.info("Alpaca session closed")
            except Exception as e:
                logger.error(f"Error closing Alpaca session: {e}")

        if self._ib_session is not None:
            try:
                if hasattr(self._ib_session, 'disconnect'):
                    self._ib_session.disconnect()
                logger.info("Interactive Brokers session closed")
            except Exception as e:
                logger.error(f"Error closing Interactive Brokers session: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
