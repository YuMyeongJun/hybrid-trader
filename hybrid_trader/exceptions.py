"""Custom exception classes for Hybrid Trader.

This module defines a hierarchy of custom exceptions for the Hybrid Trader library,
providing fine-grained error handling for various trading scenarios.

예외 클래스 계층:
- HybridTraderException (base)
  ├── InvalidTickerError
  ├── APIConnectionError
  ├── InsufficientBalanceError
  ├── OrderFailedError
  ├── ConfigurationError
  └── SessionNotInitializedError
"""


class HybridTraderException(Exception):
    """Base exception class for Hybrid Trader.

    All other Hybrid Trader exceptions inherit from this class.
    Provides a common error code and message structure.

    하이브리드 트레이더의 모든 예외의 베이스 클래스입니다.

    Attributes:
        error_code (str): Unique error code for categorization
        message (str): Descriptive error message

    Example:
        >>> try:
        ...     # Some trading operation
        ...     pass
        ... except HybridTraderException as e:
        ...     print(f"Trading error [{e.error_code}]: {e.message}")
    """

    def __init__(self, message: str, error_code: str = "HYBRID_TRADER_ERROR") -> None:
        """Initialize HybridTraderException.

        Args:
            message (str): Descriptive error message
            error_code (str): Unique error code. Defaults to "HYBRID_TRADER_ERROR".
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the exception."""
        return f"[{self.error_code}] {self.message}"

    def __repr__(self) -> str:
        """Return detailed representation of the exception."""
        return f"{self.__class__.__name__}(message={self.message!r}, error_code={self.error_code!r})"


class InvalidTickerError(HybridTraderException):
    """Exception raised when an invalid ticker is provided.

    잘못된 티커 형식이 제공되었을 때 발생합니다.

    Attributes:
        ticker (str): The invalid ticker that caused the error
        market (str): The market where the ticker is invalid (e.g., "stock", "crypto")

    Example:
        >>> try:
        ...     price = engine.get_stock_price("")  # Empty ticker
        ... except InvalidTickerError as e:
        ...     print(f"Invalid ticker: {e.ticker} in {e.market}")
        ...     # Output: Invalid ticker:  in stock
    """

    def __init__(
        self,
        ticker: str,
        market: str = "unknown",
        message: str = None
    ) -> None:
        """Initialize InvalidTickerError.

        Args:
            ticker (str): The invalid ticker
            market (str): Market type ("stock" or "crypto"). Defaults to "unknown".
            message (str): Custom error message. Defaults to generated message.
        """
        self.ticker = ticker
        self.market = market
        if message is None:
            message = f"Invalid ticker '{ticker}' for market '{market}'"
        super().__init__(message, error_code="INVALID_TICKER")


class APIConnectionError(HybridTraderException):
    """Exception raised when API connection fails.

    API 연결 실패시 발생합니다.

    Attributes:
        api_name (str): Name of the API that failed (e.g., "KIS", "Upbit")
        status_code (int): HTTP status code if available
        original_error (Exception): The underlying exception

    Example:
        >>> try:
        ...     price = engine.get_stock_price("005930")
        ... except APIConnectionError as e:
        ...     print(f"Failed to connect to {e.api_name}")
        ...     print(f"Status code: {e.status_code}")
        ...     print(f"Original error: {e.original_error}")
    """

    def __init__(
        self,
        api_name: str,
        status_code: int = None,
        original_error: Exception = None,
        message: str = None
    ) -> None:
        """Initialize APIConnectionError.

        Args:
            api_name (str): Name of the API (e.g., "KIS", "Upbit")
            status_code (int): HTTP status code if available. Defaults to None.
            original_error (Exception): The underlying exception. Defaults to None.
            message (str): Custom error message. Defaults to generated message.
        """
        self.api_name = api_name
        self.status_code = status_code
        self.original_error = original_error
        if message is None:
            error_detail = f" (HTTP {status_code})" if status_code else ""
            message = f"Failed to connect to {api_name} API{error_detail}"
            if original_error:
                message += f": {str(original_error)}"
        super().__init__(message, error_code="API_CONNECTION_ERROR")


class InsufficientBalanceError(HybridTraderException):
    """Exception raised when account balance is insufficient for an order.

    주문에 필요한 잔고가 부족할 때 발생합니다.

    Attributes:
        required_balance (float): Balance required for the order
        available_balance (float): Currently available balance
        currency (str): Currency unit (e.g., "KRW", "BTC")

    Example:
        >>> try:
        ...     engine.place_stock_order("005930", 10, 100000)
        ... except InsufficientBalanceError as e:
        ...     print(f"Insufficient balance!")
        ...     print(f"Required: {e.required_balance:,.0f} {e.currency}")
        ...     print(f"Available: {e.available_balance:,.0f} {e.currency}")
    """

    def __init__(
        self,
        required_balance: float,
        available_balance: float,
        currency: str = "KRW",
        message: str = None
    ) -> None:
        """Initialize InsufficientBalanceError.

        Args:
            required_balance (float): Balance required for the order
            available_balance (float): Currently available balance
            currency (str): Currency unit. Defaults to "KRW".
            message (str): Custom error message. Defaults to generated message.
        """
        self.required_balance = required_balance
        self.available_balance = available_balance
        self.currency = currency
        if message is None:
            shortage = required_balance - available_balance
            message = (
                f"Insufficient balance: {available_balance:,.2f} {currency} available, "
                f"but {required_balance:,.2f} {currency} required "
                f"(shortage: {shortage:,.2f} {currency})"
            )
        super().__init__(message, error_code="INSUFFICIENT_BALANCE")


class OrderFailedError(HybridTraderException):
    """Exception raised when an order execution fails.

    주문 실행 실패시 발생합니다.

    Attributes:
        order_id (str): Order ID if available
        order_type (str): Type of order (e.g., "buy", "sell")
        ticker (str): The security ticker
        reason (str): Reason for the failure

    Example:
        >>> try:
        ...     order = engine.place_stock_order("005930", 10, 100000)
        ... except OrderFailedError as e:
        ...     print(f"Order {e.order_id} ({e.order_type}) failed!")
        ...     print(f"Reason: {e.reason}")
    """

    def __init__(
        self,
        order_type: str,
        ticker: str,
        reason: str,
        order_id: str = None,
        message: str = None
    ) -> None:
        """Initialize OrderFailedError.

        Args:
            order_type (str): Type of order (e.g., "buy", "sell")
            ticker (str): The security ticker
            reason (str): Reason for the failure
            order_id (str): Order ID if available. Defaults to None.
            message (str): Custom error message. Defaults to generated message.
        """
        self.order_id = order_id
        self.order_type = order_type
        self.ticker = ticker
        self.reason = reason
        if message is None:
            order_info = f" ({order_id})" if order_id else ""
            message = (
                f"Failed to {order_type} {ticker}{order_info}: {reason}"
            )
        super().__init__(message, error_code="ORDER_FAILED")


class ConfigurationError(HybridTraderException):
    """Exception raised when configuration is invalid or incomplete.

    설정이 잘못되었거나 불완전할 때 발생합니다.

    Attributes:
        config_key (str): Configuration key that failed validation
        expected_type (str): Expected type or format
        provided_value (str): The value that was provided

    Example:
        >>> try:
        ...     config = TradingConfig(kis_config=None)
        ... except ConfigurationError as e:
        ...     print(f"Configuration error: {e.config_key}")
        ...     print(f"Expected: {e.expected_type}")
        ...     print(f"Provided: {e.provided_value}")
    """

    def __init__(
        self,
        config_key: str,
        expected_type: str = None,
        provided_value: str = None,
        message: str = None
    ) -> None:
        """Initialize ConfigurationError.

        Args:
            config_key (str): Configuration key that failed validation
            expected_type (str): Expected type or format. Defaults to None.
            provided_value (str): The value that was provided. Defaults to None.
            message (str): Custom error message. Defaults to generated message.
        """
        self.config_key = config_key
        self.expected_type = expected_type
        self.provided_value = provided_value
        if message is None:
            message = f"Configuration error: '{config_key}'"
            if expected_type:
                message += f" (expected {expected_type}"
            if provided_value:
                message += f", got {provided_value}"
            if expected_type:
                message += ")"
        super().__init__(message, error_code="CONFIGURATION_ERROR")


class SessionNotInitializedError(HybridTraderException):
    """Exception raised when a session is not properly initialized before use.

    세션이 초기화되지 않았을 때 발생합니다.

    Attributes:
        session_name (str): Name of the session that was not initialized (e.g., "KIS", "Upbit")
        required_config (str): Configuration required to initialize the session

    Example:
        >>> try:
        ...     engine = HybridTradingEngine(config)
        ...     # Session accessed without proper initialization
        ...     price = engine.kis_session.fetch_price("005930")
        ... except SessionNotInitializedError as e:
        ...     print(f"Session {e.session_name} not initialized!")
        ...     print(f"Please configure: {e.required_config}")
    """

    def __init__(
        self,
        session_name: str,
        required_config: str = None,
        message: str = None
    ) -> None:
        """Initialize SessionNotInitializedError.

        Args:
            session_name (str): Name of the session
            required_config (str): Configuration required to initialize the session. Defaults to None.
            message (str): Custom error message. Defaults to generated message.
        """
        self.session_name = session_name
        self.required_config = required_config
        if message is None:
            message = f"{session_name} session is not initialized"
            if required_config:
                message += f". Please configure: {required_config}"
        super().__init__(message, error_code="SESSION_NOT_INITIALIZED")


class AnalysisError(HybridTraderException):
    """Exception raised when technical analysis fails.

    기술적 분석 실패시 발생합니다.

    Attributes:
        analysis_type (str): Type of analysis that failed (e.g., "moving_average", "rsi")
        data_info (str): Information about the data that caused the failure

    Example:
        >>> try:
        ...     analyzer = TechnicalAnalyzer()
        ...     result = analyzer.calculate_moving_average(invalid_data)
        ... except AnalysisError as e:
        ...     print(f"Analysis failed: {e.analysis_type}")
        ...     print(f"Data issue: {e.data_info}")
    """

    def __init__(
        self,
        analysis_type: str,
        data_info: str = None,
        message: str = None
    ) -> None:
        """Initialize AnalysisError.

        Args:
            analysis_type (str): Type of analysis that failed
            data_info (str): Information about the data. Defaults to None.
            message (str): Custom error message. Defaults to generated message.
        """
        self.analysis_type = analysis_type
        self.data_info = data_info
        if message is None:
            message = f"Technical analysis failed for {analysis_type}"
            if data_info:
                message += f": {data_info}"
        super().__init__(message, error_code="ANALYSIS_ERROR")
