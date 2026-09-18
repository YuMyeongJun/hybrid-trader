"""Offline regressions for fabricated prices, orders and trading profits."""

import asyncio
import importlib.util
import logging
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from hybrid_trader import (
    HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig,
    InteractiveBrokersConfig,
)
from hybrid_trader.exceptions import APIConnectionError, UnsupportedOperationError
from hybrid_trader.orders import submission_receipt


def engine():
    return HybridTradingEngine(TradingConfig(
        KISConfig('test', 'test', 'test', 'test'), UpbitConfig('test', 'test'),
        ib_config=InteractiveBrokersConfig('test', is_demo=False), retry_count=1))


class ExecutionSafetyTests(unittest.TestCase):
    def test_unimplemented_orders_never_initialize_broker_sessions(self):
        e = engine()
        calls = [
            lambda: e.buy_stock('005930', 1, 100),
            lambda: e.sell_stock('005930', 1, 100),
            lambda: e.buy_coin('KRW-BTC', 10000),
            lambda: e.sell_coin('KRW-BTC', 0.1),
            lambda: e.buy_us_stock('AAPL', 1, 100),
            lambda: e.sell_us_stock('AAPL', 1, 100),
            lambda: e.buy_eu_stock('BMW', 1, 100),
            lambda: e.sell_eu_stock('BMW', 1, 100),
        ]
        for call in calls[:4]:
            with self.subTest(call=call):
                self.assertEqual(call()['status'], 'DRY_RUN')
        for call in calls[4:]:
            with self.subTest(call=call), self.assertRaises(UnsupportedOperationError):
                call()
        self.assertTrue(all(getattr(e, name) is None for name in (
            '_kis_session', '_upbit_session', '_alpaca_session', '_ib_session')))

    def test_live_ib_does_not_fabricate_price(self):
        with self.assertRaises(UnsupportedOperationError):
            engine()._call_ib_api('/ticker/price', {'ticker': 'BMW'})

    def test_kis_missing_sdk_method_does_not_fabricate_price(self):
        e = engine()
        e._kis_session = object()
        with self.assertRaises(APIConnectionError):
            e._call_kis_api('/stock/price', {'ticker': '005930'})

    def test_upbit_uses_guarded_adapter(self):
        e = engine()
        with patch.object(e.upbit_session, 'get_ticker', return_value={'trade_price': 123.45}) as quote:
            self.assertEqual(e._call_upbit_api('/ticker', {'markets': 'KRW-ETH'}), 123.45)
        quote.assert_called_once_with('KRW-ETH')

    def test_bad_quotes_are_not_usable_prices(self):
        for value in (None, True, 0, -1, float('nan'), float('inf'), {}, 'invalid'):
            with self.subTest(value=value):
                e = engine()
                with patch.object(e.upbit_session, 'get_ticker', return_value={'trade_price': value}), self.assertRaises(APIConnectionError):
                    e._call_upbit_api('/ticker', {'markets': 'KRW-BTC'})

    def test_invalid_order_numbers_fail_before_submission(self):
        for value in (True, float('nan'), float('inf'), -1, 0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                engine().buy_coin('KRW-BTC', value)

    def test_missing_or_generic_success_is_unknown(self):
        for response in (None, {}, {'status': 'success'}, {'id': '1', 'status': 'success'}):
            self.assertEqual(submission_receipt(response).status, 'UNKNOWN')

    def test_even_filled_ack_needs_execution_reconciliation(self):
        for state in ('pending', 'filled', 'done', 'cancel', 'partially_filled'):
            receipt = submission_receipt({'uuid': 'test-order', 'state': state})
            self.assertEqual(receipt.status, 'UNRECONCILED')
            self.assertEqual(receipt.broker_status, state)

    def test_explicit_rejection(self):
        self.assertEqual(submission_receipt({'error': {'name': 'insufficient_funds'}}).status, 'REJECTED')


class ConsumerSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[2] / 'trading-bot' / 'main.py'
        if not path.exists():
            raise unittest.SkipTest('Sibling trading-bot checkout is not available')
        sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_file_location('consumer_safety_main', path)
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def setUp(self):
        m = self.module
        self.bot = m.TradingBot.__new__(m.TradingBot)
        self.bot.bot_config = m.BotConfig(enable_real_trading=True, dry_run=False)
        self.bot.logger = logging.getLogger('execution-safety')
        self.bot.engine = Mock()
        self.bot.trade_history = []
        self.bot.daily_stats = {'profit_loss': None, 'buy_count': 0, 'sell_count': 0}

    def test_crypto_buy_uses_budget_without_integer_rounding(self):
        self.bot.engine.submit_order.return_value = {'uuid': 'test', 'state': 'wait'}
        r = asyncio.run(self.bot.handle_buy_signal(self.module.MarketType.CRYPTO, 'KRW-BTC', 100000000))
        self.bot.engine.submit_order.assert_called_once_with('KRW-BTC', 'buy', quantity=0.001, price=100000000, budget=100000)
        self.assertEqual(r.quantity, 0.001)
        self.assertEqual(r.status, 'UNRECONCILED')
        self.assertEqual(r.amount, 0)
        self.assertIsNone(self.bot.daily_stats['profit_loss'])

    def test_no_response_does_not_become_success(self):
        self.bot.engine.submit_order.return_value = None
        r = asyncio.run(self.bot.handle_buy_signal(self.module.MarketType.STOCK, '005930', 10000))
        self.assertEqual(r.status, 'UNKNOWN')
        self.assertEqual(self.bot.daily_stats['buy_count'], 0)

    def test_sell_without_local_quantity_delegates_to_broker_balance(self):
        self.bot.engine.submit_order.return_value = {'status': 'DRY_RUN'}
        r = asyncio.run(self.bot.handle_sell_signal(self.module.MarketType.CRYPTO, 'KRW-BTC', 100000000))
        self.assertEqual(r.status, 'DRY_RUN')
        self.bot.engine.submit_order.assert_called_once_with('KRW-BTC', 'sell', quantity=None, price=100000000, budget=None)

    def test_sell_does_not_generate_target_profit(self):
        self.bot.engine.submit_order.return_value = {'uuid': 'test', 'state': 'done'}
        r = asyncio.run(self.bot.handle_sell_signal(self.module.MarketType.CRYPTO, 'KRW-BTC', 100000000, 0.001))
        self.assertEqual(r.status, 'UNRECONCILED')
        self.assertEqual(r.amount, 0)
        self.assertIsNone(self.bot.daily_stats['profit_loss'])

    def test_transport_failure_is_unknown_not_rejection(self):
        self.bot.engine.submit_order.side_effect = TimeoutError('response lost')
        r = asyncio.run(self.bot.handle_buy_signal(self.module.MarketType.CRYPTO, 'KRW-BTC', 100000000))
        self.assertEqual(r.status, 'UNKNOWN')

    def test_unimplemented_adapter_is_not_sent(self):
        self.bot.engine.submit_order.side_effect = UnsupportedOperationError('Upbit', '/orders')
        r = asyncio.run(self.bot.handle_buy_signal(self.module.MarketType.CRYPTO, 'KRW-BTC', 100000000))
        self.assertEqual(r.status, 'NOT_SENT')


if __name__ == '__main__':
    unittest.main()
