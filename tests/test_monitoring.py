"""Tests for monitoring module."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, call
from hybrid_trader.monitoring import (
    PriceMonitor,
    PortfolioMonitor,
    PriceAlert,
    PriceSnapshot,
    PortfolioSnapshot
)


class TestPriceAlertDataclass:
    """Test cases for PriceAlert dataclass."""

    def test_price_alert_creation(self):
        """Test creating a price alert."""
        alert = PriceAlert(
            alert_id="test_id",
            ticker="005930",
            target_price=75000.0,
            alert_type="below",
            created_at=datetime.now(),
            is_active=True
        )

        assert alert.alert_id == "test_id"
        assert alert.ticker == "005930"
        assert alert.target_price == 75000.0
        assert alert.alert_type == "below"
        assert alert.is_active is True

    def test_price_alert_default_is_active(self):
        """Test PriceAlert defaults is_active to True."""
        alert = PriceAlert(
            alert_id="test_id",
            ticker="005930",
            target_price=75000.0,
            alert_type="above",
            created_at=datetime.now()
        )

        assert alert.is_active is True


class TestPriceSnapshotDataclass:
    """Test cases for PriceSnapshot dataclass."""

    def test_price_snapshot_creation(self):
        """Test creating a price snapshot."""
        now = datetime.now()
        snapshot = PriceSnapshot(
            ticker="005930",
            price=75500.0,
            timestamp=now,
            market_type="stock"
        )

        assert snapshot.ticker == "005930"
        assert snapshot.price == 75500.0
        assert snapshot.timestamp == now
        assert snapshot.market_type == "stock"


class TestPriceMonitorInitialization:
    """Test cases for PriceMonitor initialization."""

    def test_price_monitor_initialization(self):
        """Test PriceMonitor initialization."""
        monitor = PriceMonitor()

        assert monitor.alerts == {}
        assert monitor.price_history == {}
        assert monitor.watchers == {}
        assert monitor._monitoring is False
        assert monitor._max_history_size == 1000

    def test_price_monitor_initialization_with_custom_history_size(self):
        """Test PriceMonitor initialization with custom history size."""
        monitor = PriceMonitor(max_history_size=500)

        assert monitor._max_history_size == 500


class TestPriceMonitorWatchPrice:
    """Test cases for watch_price method."""

    def test_watch_price_valid_callback(self):
        """Test registering a valid price watcher."""
        monitor = PriceMonitor()
        callback = Mock()

        monitor.watch_price("005930", callback)

        assert "005930" in monitor.watchers
        assert callback in monitor.watchers["005930"]

    def test_watch_price_invalid_ticker_empty_string(self):
        """Test watch_price raises error with empty ticker."""
        monitor = PriceMonitor()
        callback = Mock()

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            monitor.watch_price("", callback)

    def test_watch_price_invalid_ticker_none(self):
        """Test watch_price raises error with None ticker."""
        monitor = PriceMonitor()
        callback = Mock()

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            monitor.watch_price(None, callback)

    def test_watch_price_invalid_callback_none(self):
        """Test watch_price raises error with None callback."""
        monitor = PriceMonitor()

        with pytest.raises(TypeError, match="Callback must be callable"):
            monitor.watch_price("005930", None)

    def test_watch_price_invalid_callback_not_callable(self):
        """Test watch_price raises error with non-callable callback."""
        monitor = PriceMonitor()

        with pytest.raises(TypeError, match="Callback must be callable"):
            monitor.watch_price("005930", "not_callable")

    def test_watch_price_multiple_callbacks(self):
        """Test registering multiple callbacks for same ticker."""
        monitor = PriceMonitor()
        callback1 = Mock()
        callback2 = Mock()

        monitor.watch_price("005930", callback1)
        monitor.watch_price("005930", callback2)

        assert len(monitor.watchers["005930"]) == 2
        assert callback1 in monitor.watchers["005930"]
        assert callback2 in monitor.watchers["005930"]


class TestPriceMonitorSetAlert:
    """Test cases for set_alert method."""

    def test_set_alert_above(self):
        """Test setting an 'above' price alert."""
        monitor = PriceMonitor()

        alert_id = monitor.set_alert("005930", 80000.0, "above")

        assert alert_id in monitor.alerts
        alert = monitor.alerts[alert_id]
        assert alert.ticker == "005930"
        assert alert.target_price == 80000.0
        assert alert.alert_type == "above"
        assert alert.is_active is True

    def test_set_alert_below(self):
        """Test setting a 'below' price alert."""
        monitor = PriceMonitor()

        alert_id = monitor.set_alert("005930", 70000.0, "below")

        assert alert_id in monitor.alerts
        alert = monitor.alerts[alert_id]
        assert alert.ticker == "005930"
        assert alert.target_price == 70000.0
        assert alert.alert_type == "below"

    def test_set_alert_invalid_ticker(self):
        """Test set_alert raises error with invalid ticker."""
        monitor = PriceMonitor()

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            monitor.set_alert("", 75000.0, "above")

    def test_set_alert_invalid_price_negative(self):
        """Test set_alert raises error with negative price."""
        monitor = PriceMonitor()

        with pytest.raises(ValueError, match="Target price must be a positive number"):
            monitor.set_alert("005930", -1000.0, "above")

    def test_set_alert_invalid_price_zero(self):
        """Test set_alert raises error with zero price."""
        monitor = PriceMonitor()

        with pytest.raises(ValueError, match="Target price must be a positive number"):
            monitor.set_alert("005930", 0, "above")

    def test_set_alert_invalid_type(self):
        """Test set_alert raises error with invalid alert type."""
        monitor = PriceMonitor()

        with pytest.raises(TypeError, match="Alert type must be 'above' or 'below'"):
            monitor.set_alert("005930", 75000.0, "between")

    def test_set_alert_returns_unique_ids(self):
        """Test that set_alert returns unique IDs."""
        monitor = PriceMonitor()

        alert_id1 = monitor.set_alert("005930", 75000.0, "above")
        alert_id2 = monitor.set_alert("005930", 70000.0, "below")

        assert alert_id1 != alert_id2


class TestPriceMonitorGetAlerts:
    """Test cases for get_alerts method."""

    def test_get_alerts_empty(self):
        """Test get_alerts returns empty list when no alerts."""
        monitor = PriceMonitor()

        alerts = monitor.get_alerts()

        assert alerts == []

    def test_get_alerts_returns_active_only(self):
        """Test get_alerts returns only active alerts."""
        monitor = PriceMonitor()

        alert_id1 = monitor.set_alert("005930", 75000.0, "above")
        alert_id2 = monitor.set_alert("005930", 70000.0, "below")

        monitor.alerts[alert_id1].is_active = False

        alerts = monitor.get_alerts()

        assert len(alerts) == 1
        assert alerts[0].alert_id == alert_id2

    def test_get_alerts_multiple(self):
        """Test get_alerts returns multiple alerts."""
        monitor = PriceMonitor()

        alert_id1 = monitor.set_alert("005930", 75000.0, "above")
        alert_id2 = monitor.set_alert("KRW-BTC", 65000000.0, "below")

        alerts = monitor.get_alerts()

        assert len(alerts) == 2


class TestPriceMonitorRemoveAlert:
    """Test cases for remove_alert method."""

    def test_remove_alert_success(self):
        """Test removing an alert successfully."""
        monitor = PriceMonitor()

        alert_id = monitor.set_alert("005930", 75000.0, "above")
        result = monitor.remove_alert(alert_id)

        assert result is True
        assert monitor.alerts[alert_id].is_active is False

    def test_remove_alert_not_found(self):
        """Test removing a non-existent alert."""
        monitor = PriceMonitor()

        result = monitor.remove_alert("nonexistent_id")

        assert result is False

    def test_remove_alert_invalid_alert_id(self):
        """Test remove_alert raises error with invalid alert_id."""
        monitor = PriceMonitor()

        with pytest.raises(ValueError, match="Alert ID must be a non-empty string"):
            monitor.remove_alert("")

    def test_remove_alert_invalid_alert_id_none(self):
        """Test remove_alert raises error with None alert_id."""
        monitor = PriceMonitor()

        with pytest.raises(ValueError, match="Alert ID must be a non-empty string"):
            monitor.remove_alert(None)


class TestPriceMonitorUpdatePrice:
    """Test cases for update_price method."""

    def test_update_price_new_ticker(self):
        """Test updating price for new ticker."""
        monitor = PriceMonitor()

        monitor.update_price("005930", 75500.0, "stock")

        assert monitor._current_prices["005930"] == 75500.0
        assert "005930" in monitor.price_history

    def test_update_price_triggers_callback(self):
        """Test that updating price triggers callbacks."""
        monitor = PriceMonitor()
        callback = Mock()

        monitor.watch_price("005930", callback)
        monitor.update_price("005930", 75500.0, "stock")

        callback.assert_called_once_with("005930", None, 75500.0)

    def test_update_price_tracks_old_price(self):
        """Test that callbacks receive old price."""
        monitor = PriceMonitor()
        callback = Mock()

        monitor.watch_price("005930", callback)
        monitor.update_price("005930", 75000.0, "stock")
        monitor.update_price("005930", 75500.0, "stock")

        assert callback.call_count == 2
        assert callback.call_args_list[1] == call("005930", 75000.0, 75500.0)

    def test_update_price_invalid_price_negative(self):
        """Test update_price raises error with negative price."""
        monitor = PriceMonitor()

        with pytest.raises(ValueError, match="Price must be a non-negative number"):
            monitor.update_price("005930", -100.0, "stock")

    def test_update_price_maintains_history_size(self):
        """Test that price history respects max size."""
        monitor = PriceMonitor(max_history_size=5)

        for i in range(10):
            monitor.update_price("005930", 75000.0 + i, "stock")

        assert len(monitor.price_history["005930"]) == 5

    def test_update_price_crypto(self):
        """Test updating crypto price."""
        monitor = PriceMonitor()

        monitor.update_price("KRW-BTC", 65500000.0, "crypto")

        assert monitor._current_prices["KRW-BTC"] == 65500000.0
        snapshot = monitor.price_history["KRW-BTC"][0]
        assert snapshot.market_type == "crypto"


class TestPriceMonitorCheckAlerts:
    """Test cases for alert checking."""

    def test_alert_triggered_below(self):
        """Test alert is triggered when price goes below target."""
        monitor = PriceMonitor()

        alert_id = monitor.set_alert("005930", 75000.0, "below")
        monitor.update_price("005930", 74000.0, "stock")

        assert monitor.alerts[alert_id].is_active is False

    def test_alert_triggered_above(self):
        """Test alert is triggered when price goes above target."""
        monitor = PriceMonitor()

        alert_id = monitor.set_alert("005930", 75000.0, "above")
        monitor.update_price("005930", 76000.0, "stock")

        assert monitor.alerts[alert_id].is_active is False

    def test_alert_not_triggered_above_when_below_target(self):
        """Test alert is not triggered when above alert and price below target."""
        monitor = PriceMonitor()

        alert_id = monitor.set_alert("005930", 75000.0, "above")
        monitor.update_price("005930", 74000.0, "stock")

        assert monitor.alerts[alert_id].is_active is True

    def test_alert_not_triggered_below_when_above_target(self):
        """Test alert is not triggered when below alert and price above target."""
        monitor = PriceMonitor()

        alert_id = monitor.set_alert("005930", 75000.0, "below")
        monitor.update_price("005930", 76000.0, "stock")

        assert monitor.alerts[alert_id].is_active is True


class TestPriceMonitorGetPriceHistory:
    """Test cases for get_price_history method."""

    def test_get_price_history_empty(self):
        """Test get_price_history returns empty list for non-existent ticker."""
        monitor = PriceMonitor()

        history = monitor.get_price_history("005930")

        assert history == []

    def test_get_price_history_returns_snapshots(self):
        """Test get_price_history returns all snapshots."""
        monitor = PriceMonitor()

        monitor.update_price("005930", 75000.0, "stock")
        monitor.update_price("005930", 75500.0, "stock")

        history = monitor.get_price_history("005930")

        assert len(history) == 2
        assert history[0].price == 75000.0
        assert history[1].price == 75500.0

    def test_get_price_history_with_limit(self):
        """Test get_price_history respects limit."""
        monitor = PriceMonitor()

        for i in range(10):
            monitor.update_price("005930", 75000.0 + i, "stock")

        history = monitor.get_price_history("005930", limit=5)

        assert len(history) == 5


class TestPortfolioMonitorInitialization:
    """Test cases for PortfolioMonitor initialization."""

    def test_portfolio_monitor_initialization(self):
        """Test PortfolioMonitor initialization."""
        portfolio = PortfolioMonitor(initial_value=10000000.0)

        assert portfolio.initial_value == 10000000.0
        assert portfolio.positions == {}
        assert portfolio.portfolio_history == []

    def test_portfolio_monitor_initialization_default_value(self):
        """Test PortfolioMonitor initialization with default value."""
        portfolio = PortfolioMonitor()

        assert portfolio.initial_value == 0.0

    def test_portfolio_monitor_initialization_negative_value(self):
        """Test PortfolioMonitor raises error with negative initial value."""
        with pytest.raises(ValueError, match="Initial value cannot be negative"):
            PortfolioMonitor(initial_value=-1000.0)


class TestPortfolioMonitorAddPosition:
    """Test cases for add_position method."""

    def test_add_position_with_entry_price(self):
        """Test adding a position with entry price."""
        portfolio = PortfolioMonitor()

        portfolio.add_position("005930", 100, entry_price=75000.0)

        assert "005930" in portfolio.positions
        position = portfolio.positions["005930"]
        assert position["quantity"] == 100.0
        assert position["entry_price"] == 75000.0

    def test_add_position_without_entry_price(self):
        """Test adding a position without entry price."""
        portfolio = PortfolioMonitor()

        portfolio.add_position("KRW-BTC", 0.5)

        assert portfolio.positions["KRW-BTC"]["quantity"] == 0.5
        assert portfolio.positions["KRW-BTC"]["entry_price"] is None

    def test_add_position_invalid_ticker(self):
        """Test add_position raises error with invalid ticker."""
        portfolio = PortfolioMonitor()

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            portfolio.add_position("", 100)

    def test_add_position_invalid_quantity_negative(self):
        """Test add_position raises error with negative quantity."""
        portfolio = PortfolioMonitor()

        with pytest.raises(ValueError, match="Quantity must be a non-negative number"):
            portfolio.add_position("005930", -100)

    def test_add_position_updates_existing(self):
        """Test add_position updates existing position."""
        portfolio = PortfolioMonitor()

        portfolio.add_position("005930", 100, entry_price=75000.0)
        portfolio.add_position("005930", 50, entry_price=76000.0)

        position = portfolio.positions["005930"]
        assert position["quantity"] == 50.0
        assert position["entry_price"] == 76000.0


class TestPortfolioMonitorUpdatePositionValue:
    """Test cases for update_position_value method."""

    def test_update_position_value(self):
        """Test updating position value."""
        portfolio = PortfolioMonitor()
        portfolio.add_position("005930", 100)

        portfolio.update_position_value("005930", 75500.0)

        position = portfolio.positions["005930"]
        assert position["current_value"] == 7550000.0
        assert position["current_price"] == 75500.0

    def test_update_position_value_invalid_ticker(self):
        """Test update_position_value raises error with non-existent ticker."""
        portfolio = PortfolioMonitor()

        with pytest.raises(ValueError, match="Position not found"):
            portfolio.update_position_value("005930", 75500.0)

    def test_update_position_value_invalid_price_negative(self):
        """Test update_position_value raises error with negative price."""
        portfolio = PortfolioMonitor()
        portfolio.add_position("005930", 100)

        with pytest.raises(ValueError, match="Current price must be a non-negative number"):
            portfolio.update_position_value("005930", -1000.0)


class TestPortfolioMonitorTrackPortfolio:
    """Test cases for track_portfolio method."""

    def test_track_portfolio(self):
        """Test creating portfolio snapshot."""
        portfolio = PortfolioMonitor(initial_value=10000000.0)
        portfolio.add_position("005930", 100)
        portfolio.update_position_value("005930", 75500.0)

        snapshot = portfolio.track_portfolio()

        assert snapshot.total_value == 7550000.0
        assert snapshot.daily_pnl == -2450000.0
        assert "005930" in snapshot.positions

    def test_track_portfolio_multiple_positions(self):
        """Test portfolio snapshot with multiple positions."""
        portfolio = PortfolioMonitor(initial_value=10000000.0)
        portfolio.add_position("005930", 100)
        portfolio.add_position("KRW-BTC", 1.0)

        portfolio.update_position_value("005930", 75500.0)
        portfolio.update_position_value("KRW-BTC", 65000000.0)

        snapshot = portfolio.track_portfolio()

        assert snapshot.total_value == 72550000.0


class TestPortfolioMonitorGetHistory:
    """Test cases for get_portfolio_history method."""

    def test_get_portfolio_history_empty(self):
        """Test get_portfolio_history returns empty list initially."""
        portfolio = PortfolioMonitor()

        history = portfolio.get_portfolio_history()

        assert history == []

    def test_get_portfolio_history_returns_snapshots(self):
        """Test get_portfolio_history returns snapshots."""
        portfolio = PortfolioMonitor(initial_value=10000000.0)
        portfolio.add_position("005930", 100)

        portfolio.update_position_value("005930", 75000.0)
        portfolio.track_portfolio()

        portfolio.update_position_value("005930", 75500.0)
        portfolio.track_portfolio()

        history = portfolio.get_portfolio_history()

        assert len(history) == 2

    def test_get_portfolio_history_with_limit(self):
        """Test get_portfolio_history respects limit."""
        portfolio = PortfolioMonitor(initial_value=10000000.0)
        portfolio.add_position("005930", 100)

        for i in range(10):
            portfolio.update_position_value("005930", 75000.0 + i)
            portfolio.track_portfolio()

        history = portfolio.get_portfolio_history(limit=5)

        assert len(history) == 5


class TestPortfolioMonitorCalculatePerformance:
    """Test cases for calculate_performance method."""

    def test_calculate_performance_no_positions(self):
        """Test calculate_performance with no positions."""
        portfolio = PortfolioMonitor(initial_value=10000000.0)

        performance = portfolio.calculate_performance()

        assert performance["total_value"] == 0.0
        assert performance["total_gain"] == -10000000.0
        assert performance["position_count"] == 0

    def test_calculate_performance_with_positions(self):
        """Test calculate_performance with positions."""
        portfolio = PortfolioMonitor(initial_value=10000000.0)
        portfolio.add_position("005930", 100)
        portfolio.update_position_value("005930", 75500.0)

        performance = portfolio.calculate_performance()

        assert performance["total_value"] == 7550000.0
        assert performance["total_gain"] == -2450000.0
        assert performance["total_return"] == pytest.approx(-24.5)
        assert performance["position_count"] == 1

    def test_calculate_performance_positive_return(self):
        """Test calculate_performance with positive return."""
        portfolio = PortfolioMonitor(initial_value=10000000.0)
        portfolio.add_position("005930", 100)
        portfolio.update_position_value("005930", 150000.0)

        performance = portfolio.calculate_performance()

        assert performance["total_value"] == 15000000.0
        assert performance["total_gain"] == 5000000.0
        assert performance["total_return"] == pytest.approx(50.0)


class TestPortfolioMonitorGetDailyPnL:
    """Test cases for get_daily_pnl method."""

    def test_get_daily_pnl_no_history(self):
        """Test get_daily_pnl returns 0 when no history."""
        portfolio = PortfolioMonitor()

        pnl = portfolio.get_daily_pnl()

        assert pnl == 0.0

    def test_get_daily_pnl_with_history(self):
        """Test get_daily_pnl returns latest snapshot's daily_pnl."""
        portfolio = PortfolioMonitor(initial_value=10000000.0)
        portfolio.add_position("005930", 100)
        portfolio.update_position_value("005930", 75500.0)
        portfolio.track_portfolio()

        pnl = portfolio.get_daily_pnl()

        assert pnl == -2450000.0


class TestPortfolioMonitorRemovePosition:
    """Test cases for remove_position method."""

    def test_remove_position_success(self):
        """Test removing a position successfully."""
        portfolio = PortfolioMonitor()
        portfolio.add_position("005930", 100)

        result = portfolio.remove_position("005930")

        assert result is True
        assert "005930" not in portfolio.positions

    def test_remove_position_not_found(self):
        """Test removing a non-existent position."""
        portfolio = PortfolioMonitor()

        result = portfolio.remove_position("005930")

        assert result is False


class TestPortfolioMonitorGetPosition:
    """Test cases for get_position method."""

    def test_get_position_exists(self):
        """Test getting an existing position."""
        portfolio = PortfolioMonitor()
        portfolio.add_position("005930", 100, entry_price=75000.0)

        position = portfolio.get_position("005930")

        assert position is not None
        assert position["quantity"] == 100.0
        assert position["entry_price"] == 75000.0

    def test_get_position_not_found(self):
        """Test getting a non-existent position."""
        portfolio = PortfolioMonitor()

        position = portfolio.get_position("005930")

        assert position is None


class TestPortfolioMonitorIntegration:
    """Integration tests for PortfolioMonitor."""

    def test_full_portfolio_workflow(self):
        """Test complete portfolio monitoring workflow."""
        portfolio = PortfolioMonitor(initial_value=10000000.0)

        portfolio.add_position("005930", 100, entry_price=75000.0)
        portfolio.update_position_value("005930", 75500.0)

        portfolio.add_position("KRW-BTC", 1.0, entry_price=60000000.0)
        portfolio.update_position_value("KRW-BTC", 65000000.0)

        snapshot1 = portfolio.track_portfolio()
        assert snapshot1.total_value == 72550000.0

        performance = portfolio.calculate_performance()
        assert performance["total_value"] == 72550000.0
        assert performance["total_gain"] == 62550000.0

        history = portfolio.get_portfolio_history()
        assert len(history) == 1

        pnl = portfolio.get_daily_pnl()
        assert pnl == 62550000.0
