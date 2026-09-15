"""Monitoring module for Hybrid Trading Engine.

This module provides real-time price monitoring, alert management, and portfolio
tracking capabilities for both stock (KIS) and cryptocurrency (Upbit) markets.

가격 모니터링, 알림 관리, 포트폴리오 추적 기능을 제공합니다.
"""

from typing import Optional, Dict, Any, List, Callable, Literal
from dataclasses import dataclass, field
from datetime import datetime
from threading import Thread, Event, Lock
import logging
import uuid
import time

logger = logging.getLogger(__name__)


@dataclass
class PriceAlert:
    """Price alert configuration.

    가격 알림 설정을 관리하는 클래스입니다.

    Attributes:
        alert_id (str): Unique alert identifier
        ticker (str): Asset ticker code (stock or crypto)
        target_price (float): Target price level for alert
        alert_type (Literal["above", "below"]): Alert type
            - "above": Alert when price goes above target
            - "below": Alert when price goes below target
        created_at (datetime): Timestamp when alert was created
        is_active (bool): Whether the alert is currently active
    """
    alert_id: str
    ticker: str
    target_price: float
    alert_type: Literal["above", "below"]
    created_at: datetime
    is_active: bool = True


@dataclass
class PriceSnapshot:
    """Price data snapshot.

    가격 데이터 스냅샷을 관리합니다.

    Attributes:
        ticker (str): Asset ticker code
        price (float): Current price
        timestamp (datetime): Timestamp of the price
        market_type (Literal["stock", "crypto"]): Market type
    """
    ticker: str
    price: float
    timestamp: datetime
    market_type: Literal["stock", "crypto"]


@dataclass
class PortfolioSnapshot:
    """Portfolio state snapshot.

    포트폴리오 상태 스냅샷을 관리합니다.

    Attributes:
        timestamp (datetime): Timestamp of the snapshot
        total_value (float): Total portfolio value in KRW
        stock_value (float): Stock portfolio value
        crypto_value (float): Cryptocurrency portfolio value
        daily_pnl (float): Daily profit/loss
        total_pnl (float): Total profit/loss
        positions (Dict): Current positions
    """
    timestamp: datetime
    total_value: float
    stock_value: float
    crypto_value: float
    daily_pnl: float
    total_pnl: float
    positions: Dict[str, float] = field(default_factory=dict)


class PriceMonitor:
    """Real-time price monitor with alert capabilities.

    주식과 암호화폐의 가격을 실시간으로 모니터링하고 알림을 관리합니다.

    Attributes:
        alerts (Dict[str, PriceAlert]): Dictionary of active alerts by alert_id
        price_history (Dict[str, List]): Historical price data by ticker
        watchers (Dict[str, List[Callable]]): Callbacks for price changes by ticker
        _monitoring (bool): Flag to control monitoring thread
        _monitor_thread (Optional[Thread]): Background monitoring thread
        _lock (Lock): Thread lock for thread-safe operations

    Example:
        >>> monitor = PriceMonitor()
        >>>
        >>> def on_price_change(ticker, old_price, new_price):
        ...     print(f"{ticker}: {old_price} -> {new_price}")
        >>>
        >>> monitor.watch_price("005930", on_price_change)
        >>> alert_id = monitor.set_alert("005930", 75000, "below")
        >>> alerts = monitor.get_alerts()
    """

    def __init__(self, max_history_size: int = 1000) -> None:
        """Initialize the Price Monitor.

        가격 모니터를 초기화합니다.

        Args:
            max_history_size (int): Maximum number of price records to keep per ticker.
                Defaults to 1000.
        """
        self.alerts: Dict[str, PriceAlert] = {}
        self.price_history: Dict[str, List[PriceSnapshot]] = {}
        self.watchers: Dict[str, List[Callable]] = {}
        self._monitoring = False
        self._monitor_thread: Optional[Thread] = None
        self._lock = Lock()
        self._max_history_size = max_history_size
        self._current_prices: Dict[str, float] = {}

        logger.info("PriceMonitor initialized")

    def watch_price(
        self,
        ticker: str,
        callback: Callable[[str, Optional[float], float], None]
    ) -> None:
        """Register a callback for price changes.

        가격 변동 시 호출될 콜백을 등록합니다.

        Args:
            ticker (str): Asset ticker code to monitor
            callback (Callable): Function to call on price change.
                Signature: callback(ticker: str, old_price: Optional[float], new_price: float)

        Raises:
            TypeError: If callback is not callable
            ValueError: If ticker is empty or callback is None

        Example:
            >>> def on_price(ticker, old_price, new_price):
            ...     print(f"{ticker}: {old_price} -> {new_price}")
            >>>
            >>> monitor.watch_price("KRW-BTC", on_price)
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if callback is None or not callable(callback):
            raise TypeError("Callback must be callable")

        try:
            with self._lock:
                if ticker not in self.watchers:
                    self.watchers[ticker] = []
                    self.price_history[ticker] = []

                self.watchers[ticker].append(callback)
                logger.info(f"Price watcher registered for {ticker}")

        except Exception as e:
            logger.error(f"Failed to register price watcher for {ticker}: {e}")
            raise

    def set_alert(
        self,
        ticker: str,
        target_price: float,
        alert_type: Literal["above", "below"]
    ) -> str:
        """Set a price alert for an asset.

        특정 가격 수준에서 알림을 설정합니다.

        Args:
            ticker (str): Asset ticker code
            target_price (float): Price level to trigger alert
            alert_type (Literal["above", "below"]): Alert condition
                - "above": Alert when price exceeds target
                - "below": Alert when price falls below target

        Returns:
            str: Alert ID for future reference

        Raises:
            ValueError: If parameters are invalid
            TypeError: If alert_type is not valid

        Example:
            >>> alert_id = monitor.set_alert("005930", 75000, "below")
            >>> print(f"Alert set with ID: {alert_id}")
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if not isinstance(target_price, (int, float)) or target_price <= 0:
            raise ValueError("Target price must be a positive number")
        if alert_type not in ("above", "below"):
            raise TypeError(f"Alert type must be 'above' or 'below', got '{alert_type}'")

        try:
            alert_id = str(uuid.uuid4())
            alert = PriceAlert(
                alert_id=alert_id,
                ticker=ticker,
                target_price=target_price,
                alert_type=alert_type,
                created_at=datetime.now(),
                is_active=True
            )

            with self._lock:
                self.alerts[alert_id] = alert
                if ticker not in self.watchers:
                    self.watchers[ticker] = []
                    self.price_history[ticker] = []

            logger.info(
                f"Alert set: {ticker} {alert_type} {target_price} KRW "
                f"(ID: {alert_id})"
            )
            return alert_id

        except Exception as e:
            logger.error(f"Failed to set alert for {ticker}: {e}")
            raise

    def get_alerts(self) -> List[PriceAlert]:
        """Get all active alerts.

        모든 활성 알림을 조회합니다.

        Returns:
            List[PriceAlert]: List of active price alerts

        Example:
            >>> alerts = monitor.get_alerts()
            >>> for alert in alerts:
            ...     print(f"{alert.ticker}: {alert.alert_type} {alert.target_price}")
        """
        try:
            with self._lock:
                return [alert for alert in self.alerts.values() if alert.is_active]

        except Exception as e:
            logger.error(f"Failed to retrieve alerts: {e}")
            return []

    def remove_alert(self, alert_id: str) -> bool:
        """Remove an alert by ID.

        알림을 제거합니다.

        Args:
            alert_id (str): Alert ID to remove

        Returns:
            bool: True if alert was removed, False if not found

        Raises:
            ValueError: If alert_id is empty or invalid

        Example:
            >>> alert_id = monitor.set_alert("005930", 75000, "below")
            >>> monitor.remove_alert(alert_id)
            True
        """
        if not alert_id or not isinstance(alert_id, str):
            raise ValueError("Alert ID must be a non-empty string")

        try:
            with self._lock:
                if alert_id in self.alerts:
                    self.alerts[alert_id].is_active = False
                    logger.info(f"Alert removed: {alert_id}")
                    return True
                else:
                    logger.warning(f"Alert not found: {alert_id}")
                    return False

        except Exception as e:
            logger.error(f"Failed to remove alert {alert_id}: {e}")
            return False

    def update_price(
        self,
        ticker: str,
        price: float,
        market_type: Literal["stock", "crypto"] = "stock"
    ) -> None:
        """Update price and trigger callbacks and alerts.

        가격을 업데이트하고 콜백과 알림을 트리거합니다.

        Args:
            ticker (str): Asset ticker code
            price (float): Current price
            market_type (Literal["stock", "crypto"]): Market type. Defaults to "stock".

        Raises:
            ValueError: If price is invalid or negative

        Example:
            >>> monitor.update_price("005930", 75500.0, "stock")
            >>> monitor.update_price("KRW-BTC", 65500000.0, "crypto")
        """
        if price < 0 or not isinstance(price, (int, float)):
            raise ValueError("Price must be a non-negative number")

        try:
            with self._lock:
                old_price = self._current_prices.get(ticker)
                self._current_prices[ticker] = price

                snapshot = PriceSnapshot(
                    ticker=ticker,
                    price=price,
                    timestamp=datetime.now(),
                    market_type=market_type
                )

                if ticker not in self.price_history:
                    self.price_history[ticker] = []

                self.price_history[ticker].append(snapshot)
                if len(self.price_history[ticker]) > self._max_history_size:
                    self.price_history[ticker].pop(0)

            self._trigger_callbacks(ticker, old_price, price)
            self._check_alerts(ticker, price)

            logger.debug(f"Price updated: {ticker} = {price}")

        except Exception as e:
            logger.error(f"Failed to update price for {ticker}: {e}")

    def _trigger_callbacks(
        self,
        ticker: str,
        old_price: Optional[float],
        new_price: float
    ) -> None:
        """Trigger registered callbacks for price change.

        등록된 콜백을 실행합니다.

        Args:
            ticker (str): Asset ticker code
            old_price (Optional[float]): Previous price or None if new
            new_price (float): New price
        """
        try:
            if ticker in self.watchers:
                for callback in self.watchers[ticker]:
                    try:
                        callback(ticker, old_price, new_price)
                    except Exception as e:
                        logger.error(f"Error in callback for {ticker}: {e}")

        except Exception as e:
            logger.error(f"Failed to trigger callbacks for {ticker}: {e}")

    def _check_alerts(self, ticker: str, current_price: float) -> None:
        """Check if any alerts should be triggered.

        알림 조건을 확인하고 트리거합니다.

        Args:
            ticker (str): Asset ticker code
            current_price (float): Current price
        """
        try:
            with self._lock:
                for alert in self.alerts.values():
                    if not alert.is_active or alert.ticker != ticker:
                        continue

                    should_trigger = False
                    if alert.alert_type == "above" and current_price >= alert.target_price:
                        should_trigger = True
                    elif alert.alert_type == "below" and current_price <= alert.target_price:
                        should_trigger = True

                    if should_trigger:
                        self._trigger_alert(alert, current_price)
                        alert.is_active = False

        except Exception as e:
            logger.error(f"Failed to check alerts for {ticker}: {e}")

    def _trigger_alert(self, alert: PriceAlert, current_price: float) -> None:
        """Log alert trigger event.

        알림을 트리거합니다.

        Args:
            alert (PriceAlert): Alert to trigger
            current_price (float): Current price
        """
        try:
            logger.warning(
                f"Alert triggered: {alert.ticker} {alert.alert_type} "
                f"{alert.target_price} (Current: {current_price}) "
                f"[ID: {alert.alert_id}]"
            )

        except Exception as e:
            logger.error(f"Failed to trigger alert {alert.alert_id}: {e}")

    def get_price_history(
        self,
        ticker: str,
        limit: int = 100
    ) -> List[PriceSnapshot]:
        """Get price history for a ticker.

        특정 자산의 가격 히스토리를 조회합니다.

        Args:
            ticker (str): Asset ticker code
            limit (int): Maximum number of records to return. Defaults to 100.

        Returns:
            List[PriceSnapshot]: Price history records

        Example:
            >>> history = monitor.get_price_history("005930", limit=50)
            >>> for snapshot in history[-5:]:
            ...     print(f"{snapshot.timestamp}: {snapshot.price}")
        """
        try:
            with self._lock:
                if ticker not in self.price_history:
                    return []
                return self.price_history[ticker][-limit:]

        except Exception as e:
            logger.error(f"Failed to retrieve price history for {ticker}: {e}")
            return []


class PortfolioMonitor:
    """Portfolio tracking and performance monitoring.

    포트폴리오를 추적하고 성과를 분석합니다.

    Attributes:
        positions (Dict): Current portfolio positions by ticker
        portfolio_history (List): Historical portfolio snapshots
        initial_value (float): Initial portfolio value
        _lock (Lock): Thread lock for thread-safe operations

    Example:
        >>> portfolio = PortfolioMonitor(initial_value=10000000)
        >>> portfolio.add_position("005930", 100)
        >>> portfolio.update_position_value("005930", 75500)
        >>> history = portfolio.get_portfolio_history()
    """

    def __init__(self, initial_value: float = 0.0) -> None:
        """Initialize the Portfolio Monitor.

        포트폴리오 모니터를 초기화합니다.

        Args:
            initial_value (float): Initial portfolio value in KRW.
                Defaults to 0.0.

        Raises:
            ValueError: If initial_value is negative
        """
        if initial_value < 0:
            raise ValueError("Initial value cannot be negative")

        self.positions: Dict[str, Dict[str, Any]] = {}
        self.portfolio_history: List[PortfolioSnapshot] = []
        self.initial_value = initial_value
        self._base_date_pnl = 0.0
        self._lock = Lock()

        logger.info(f"PortfolioMonitor initialized with initial value: {initial_value:,.0f} KRW")

    def add_position(
        self,
        ticker: str,
        quantity: float,
        entry_price: Optional[float] = None
    ) -> None:
        """Add or update a position in the portfolio.

        포트폴리오에 포지션을 추가하거나 수정합니다.

        Args:
            ticker (str): Asset ticker code
            quantity (float): Quantity of the asset
            entry_price (Optional[float]): Entry price. Defaults to None.

        Raises:
            ValueError: If ticker is empty or quantity is invalid

        Example:
            >>> portfolio.add_position("005930", 100, 75000)
            >>> portfolio.add_position("KRW-BTC", 0.5)
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if not isinstance(quantity, (int, float)) or quantity < 0:
            raise ValueError("Quantity must be a non-negative number")

        try:
            with self._lock:
                self.positions[ticker] = {
                    "quantity": float(quantity),
                    "entry_price": float(entry_price) if entry_price else None,
                    "current_value": 0.0,
                    "added_at": datetime.now()
                }
                logger.info(f"Position added: {ticker} x {quantity}")

        except Exception as e:
            logger.error(f"Failed to add position {ticker}: {e}")
            raise

    def update_position_value(self, ticker: str, current_price: float) -> None:
        """Update current value of a position.

        포지션의 현재 가치를 업데이트합니다.

        Args:
            ticker (str): Asset ticker code
            current_price (float): Current price of the asset

        Raises:
            ValueError: If current_price is invalid or position doesn't exist

        Example:
            >>> portfolio.update_position_value("005930", 75500)
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if not isinstance(current_price, (int, float)) or current_price < 0:
            raise ValueError("Current price must be a non-negative number")

        try:
            with self._lock:
                if ticker not in self.positions:
                    raise ValueError(f"Position not found for {ticker}")

                quantity = self.positions[ticker]["quantity"]
                current_value = quantity * current_price
                self.positions[ticker]["current_value"] = current_value
                self.positions[ticker]["current_price"] = current_price

                logger.debug(f"Position updated: {ticker} = {current_value:,.0f} KRW")

        except Exception as e:
            logger.error(f"Failed to update position value for {ticker}: {e}")
            raise

    def track_portfolio(self) -> PortfolioSnapshot:
        """Create a snapshot of the current portfolio state.

        현재 포트폴리오 상태를 스냅샷으로 저장합니다.

        Returns:
            PortfolioSnapshot: Current portfolio state

        Example:
            >>> snapshot = portfolio.track_portfolio()
            >>> print(f"Total value: {snapshot.total_value:,.0f} KRW")
            >>> print(f"Daily P&L: {snapshot.daily_pnl:,.0f} KRW")
        """
        try:
            with self._lock:
                total_value = sum(
                    pos["current_value"] for pos in self.positions.values()
                )
                stock_value = sum(
                    pos["current_value"] for pos in self.positions.values()
                    if pos.get("market_type") == "stock"
                )
                crypto_value = sum(
                    pos["current_value"] for pos in self.positions.values()
                    if pos.get("market_type") == "crypto"
                )

                daily_pnl = total_value - self.initial_value
                total_pnl = daily_pnl

                snapshot = PortfolioSnapshot(
                    timestamp=datetime.now(),
                    total_value=total_value,
                    stock_value=stock_value,
                    crypto_value=crypto_value,
                    daily_pnl=daily_pnl,
                    total_pnl=total_pnl,
                    positions={k: v["current_value"] for k, v in self.positions.items()}
                )

                self.portfolio_history.append(snapshot)
                logger.info(
                    f"Portfolio snapshot created: "
                    f"Total={total_value:,.0f} KRW, "
                    f"Daily PnL={daily_pnl:,.0f} KRW"
                )
                return snapshot

        except Exception as e:
            logger.error(f"Failed to track portfolio: {e}")
            raise

    def get_portfolio_history(self, limit: int = 100) -> List[PortfolioSnapshot]:
        """Get portfolio history snapshots.

        포트폴리오 히스토리를 조회합니다.

        Args:
            limit (int): Maximum number of snapshots to return. Defaults to 100.

        Returns:
            List[PortfolioSnapshot]: Portfolio history records

        Example:
            >>> history = portfolio.get_portfolio_history(limit=20)
            >>> for snapshot in history:
            ...     print(f"{snapshot.timestamp}: {snapshot.total_value:,.0f} KRW")
        """
        try:
            with self._lock:
                return self.portfolio_history[-limit:]

        except Exception as e:
            logger.error(f"Failed to retrieve portfolio history: {e}")
            return []

    def calculate_performance(self) -> Dict[str, float]:
        """Calculate portfolio performance metrics.

        포트폴리오의 성과 지표를 계산합니다.

        Returns:
            Dict[str, float]: Performance metrics including:
                - total_value: Total portfolio value
                - total_gain: Total profit/loss amount
                - total_return: Total return percentage
                - daily_gain: Daily profit/loss
                - daily_return: Daily return percentage

        Example:
            >>> performance = portfolio.calculate_performance()
            >>> print(f"Total Return: {performance['total_return']:.2f}%")
            >>> print(f"Daily Gain: {performance['daily_gain']:,.0f} KRW")
        """
        try:
            with self._lock:
                total_value = sum(
                    pos["current_value"] for pos in self.positions.values()
                )
                total_gain = total_value - self.initial_value
                total_return = (total_gain / self.initial_value * 100) if self.initial_value > 0 else 0.0

                daily_gain = total_gain
                daily_return = total_return

                return {
                    "total_value": total_value,
                    "total_gain": total_gain,
                    "total_return": total_return,
                    "daily_gain": daily_gain,
                    "daily_return": daily_return,
                    "position_count": len(self.positions)
                }

        except Exception as e:
            logger.error(f"Failed to calculate performance: {e}")
            return {
                "total_value": 0.0,
                "total_gain": 0.0,
                "total_return": 0.0,
                "daily_gain": 0.0,
                "daily_return": 0.0,
                "position_count": 0
            }

    def get_daily_pnl(self) -> float:
        """Get daily profit/loss.

        일일 손익을 계산합니다.

        Returns:
            float: Daily profit/loss amount in KRW

        Example:
            >>> pnl = portfolio.get_daily_pnl()
            >>> print(f"Daily P&L: {pnl:,.0f} KRW")
        """
        try:
            with self._lock:
                if not self.portfolio_history:
                    return 0.0

                latest = self.portfolio_history[-1]
                return latest.daily_pnl

        except Exception as e:
            logger.error(f"Failed to get daily PnL: {e}")
            return 0.0

    def remove_position(self, ticker: str) -> bool:
        """Remove a position from the portfolio.

        포지션을 제거합니다.

        Args:
            ticker (str): Asset ticker code

        Returns:
            bool: True if position was removed, False if not found

        Example:
            >>> portfolio.remove_position("005930")
            True
        """
        try:
            with self._lock:
                if ticker in self.positions:
                    del self.positions[ticker]
                    logger.info(f"Position removed: {ticker}")
                    return True
                else:
                    logger.warning(f"Position not found for removal: {ticker}")
                    return False

        except Exception as e:
            logger.error(f"Failed to remove position {ticker}: {e}")
            return False

    def get_position(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific position.

        특정 포지션의 상세 정보를 조회합니다.

        Args:
            ticker (str): Asset ticker code

        Returns:
            Optional[Dict]: Position details or None if not found

        Example:
            >>> pos = portfolio.get_position("005930")
            >>> print(f"Quantity: {pos['quantity']}")
            >>> print(f"Current Value: {pos['current_value']:,.0f} KRW")
        """
        try:
            with self._lock:
                return self.positions.get(ticker)

        except Exception as e:
            logger.error(f"Failed to get position {ticker}: {e}")
            return None
