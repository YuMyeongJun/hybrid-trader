"""Durable intent journal, broker reconciliation and shared execution limits."""
import hashlib
import json
from pathlib import Path
import sqlite3
import time
import uuid
from datetime import datetime
from decimal import Decimal, ROUND_FLOOR
from threading import RLock

from .brokers import (KISBroker, UpbitBroker, BrokerError, OrderRejected,
                      SubmissionUnknown, TradingDisabled, KST, enabled, number,
                      round_price, symbol)

TERMINAL = {"FILLED", "CANCELED", "REJECTED", "NOT_SENT"}


class Execution:
    def __init__(self, config):
        self.config = config
        self.brokers = {"kis": KISBroker(config), "upbit": UpbitBroker(config)}
        self._db = None
        self._lock = RLock()
        # Separate broker identities: toggling KIS paper mode must not reset
        # Upbit's pending orders or daily loss latch.
        identities = {'kis': 'kis|' + config.kis_config.account_number.replace('-', '') + '|' + str(config.kis_config.is_demo),
                      'upbit': 'upbit|' + config.upbit_config.access_key}
        self.scopes = {broker: hashlib.sha256(value.encode()).hexdigest() for broker, value in identities.items()}

    @property
    def db(self):
        if self._db is None:
            path = self.config.order_db_path
            if path != ":memory:":
                Path(path).resolve().parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(path, timeout=10, isolation_level=None)
            self._db.execute("PRAGMA synchronous=FULL")
            self._db.execute("CREATE TABLE IF NOT EXISTS orders (scope TEXT, id TEXT PRIMARY KEY, broker TEXT, ticker TEXT, status TEXT, payload TEXT)")
            self._db.execute('CREATE TABLE IF NOT EXISTS costs (scope TEXT, day TEXT, payload TEXT, PRIMARY KEY(scope,day))')
            self._db.execute("CREATE TABLE IF NOT EXISTS daily (scope TEXT, broker TEXT, day TEXT, equity REAL, halted INTEGER, current_equity REAL, PRIMARY KEY(scope,broker,day))")
            if 'current_equity' not in {r[1] for r in self._db.execute('PRAGMA table_info(daily)')}:
                self._db.execute('ALTER TABLE daily ADD COLUMN current_equity REAL')
        return self._db

    def _save(self, row):
        self.db.execute("INSERT OR REPLACE INTO orders VALUES (?,?,?,?,?,?)",
            (self.scopes[row['broker']], row["identifier"], row["broker"], row["ticker"], row["status"], json.dumps(row, allow_nan=False)))

    def orders(self):
        return [json.loads(r[0]) for r in self.db.execute("SELECT payload FROM orders WHERE scope IN (?,?) ORDER BY rowid", tuple(self.scopes.values()))]

    def balance(self, broker):
        balance = self.brokers[broker].balance()
        self._daily(broker, balance, 'sell')
        return balance

    def _risk(self, broker, ticker, side, quantity, price, balance, cost_rate):
        c = self.config
        amount = quantity * price
        if amount > number(c.max_order_amount):
            raise BrokerError("Per-order amount limit exceeded")
        holding = balance["holdings"].get(ticker, {})
        if side == "sell":
            if quantity > number(holding.get("available", 0)):
                raise BrokerError("Insufficient broker sellable balance")
            return
        if amount * (1 + cost_rate) > number(balance["cash"]):
            raise BrokerError("Insufficient cash including fees")
        if number(holding.get("value", 0)) + amount > number(c.max_symbol_amount):
            raise BrokerError("Per-symbol exposure limit exceeded")
        if len(balance["holdings"]) >= c.max_positions and not holding:
            raise BrokerError("Maximum position count reached")
        entries = sum(1 for row in self.orders() if row["ticker"] == ticker and row["side"] == "buy"
                      and row.get("filled_quantity", 0) > 0)
        # Existing broker holdings count as an entry even if acquired outside bot.
        if holding and max(1, entries) >= c.max_positions_per_symbol:
            raise BrokerError("Per-symbol entry count reached")

    def _daily(self, broker, balance, side):
        day = datetime.now(KST).date().isoformat()
        equity = float(number(balance["total_valuation"]))
        scope = self.scopes[broker]
        self.db.execute("INSERT OR IGNORE INTO daily VALUES (?,?,?,?,0,?)", (scope, broker, day, equity, equity))
        self.db.execute("UPDATE daily SET current_equity=? WHERE scope=? AND broker=? AND day=?", (equity, scope, broker, day))
        initial, halted = self.db.execute("SELECT equity,halted FROM daily WHERE scope=? AND broker=? AND day=?", (scope, broker, day)).fetchone()
        scope_day = (*self.scopes.values(), day)
        loss = self.db.execute("SELECT SUM(MAX(0,equity-current_equity)),MAX(halted) FROM daily WHERE scope IN (?,?) AND day=?", scope_day).fetchone()
        if (loss[0] or 0) >= self.config.daily_loss_limit or loss[1]:
            self.db.execute("UPDATE daily SET halted=1 WHERE scope IN (?,?) AND day=?", scope_day)
            halted = 1
        if halted and side == "buy":
            raise BrokerError("Daily equity loss limit reached; buys halted")

    def submit(self, broker, ticker, side, quantity=None, price=None, budget=None):
        symbol(ticker, broker)
        if side not in ("buy", "sell"):
            raise BrokerError("Invalid order side")
        if not enabled(self.config, broker):
            return {"status": "DRY_RUN", "state": "dry_run", "order_id": None}
        with self._lock:
            # BEGIN IMMEDIATE serializes risk checks + intent creation across
            # processes sharing this journal. Commit BEFORE the external write.
            self.db.execute("BEGIN IMMEDIATE")
            try:
                active = [r for r in self.orders() if r["status"] not in TERMINAL]
                # One unresolved intent account-wide: conservative reservation.
                if active:
                    raise BrokerError("Unresolved order blocks new submissions")
                adapter = self.brokers[broker]
                if adapter.has_open_orders():
                    raise BrokerError('Broker has untracked open orders')
                balance = adapter.balance()
                self._daily(broker, balance, side)
                if side == 'buy':
                    other = 'upbit' if broker == 'kis' else 'kis'
                    if self.brokers[other].has_open_orders():
                        raise BrokerError('Other account has untracked open orders')
                    other_balance = self.brokers[other].balance()
                    self._daily(other, other_balance, side)
                    combined_count = len(balance['holdings']) + len(other_balance['holdings'])
                    if combined_count >= self.config.max_positions and ticker not in balance['holdings']:
                        raise BrokerError('Maximum combined position count reached')
                quote = number(adapter.quote(ticker)["price"], True)
                reference = number(price, True) if price is not None else quote
                if abs(reference / quote - 1) > number(self.config.max_slippage):
                    raise BrokerError("Stale price exceeds slippage limit")
                limit = round_price(reference, broker, side)
                fees = number(self.config.fee_reserve)
                chance = None
                if broker == "upbit":
                    chance = adapter.chance(ticker)
                    fees = max(fees, chance["buy_fee"] if side == "buy" else chance["sell_fee"])
                if side == "sell":
                    available = number(balance["holdings"].get(ticker, {}).get("available", 0))
                    qty = min(number(quantity, True), available) if quantity is not None else available
                    qty = min(qty, number(self.config.max_order_amount) / limit)
                elif budget is not None:
                    spend = min(number(budget, True), number(self.config.max_order_amount))
                    qty = spend / (limit * (1 + fees))
                else:
                    qty = number(quantity, True)
                step = Decimal(1) if broker == "kis" else Decimal("0.00000001")
                qty = number(qty.quantize(step, rounding=ROUND_FLOOR), True)
                self._risk(broker, ticker, side, qty, limit, balance, fees)
                if broker == "kis" and side == "buy":
                    cash, max_qty = adapter.buying_power(ticker, limit)
                    if qty > max_qty or qty * limit * (1 + fees) > cash:
                        raise BrokerError("Insufficient KIS cash-only buying power")
                if chance and not chance["min_buy" if side == "buy" else "min_sell"] <= qty * limit <= chance["max_total"]:
                    raise BrokerError("Upbit order amount outside exchange limits")
                row = {"identifier": str(uuid.uuid4()), "broker": broker, "ticker": ticker, "side": side,
                    "date": datetime.now(KST).strftime("%Y%m%d"), "created_at": time.time(),
                    "quantity": float(qty), "limit_price": float(limit), "reference_price": float(quote),
                    "order_id": None, "status": "SUBMITTING", "filled_quantity": 0,
                    "initial_quantity": balance['holdings'].get(ticker, {}).get('quantity', 0),
                    "filled_amount": 0, "fee": None, "fee_status": "UNRECONCILED"}
                self._save(row)
                self.db.execute("COMMIT")
            except Exception:
                # Keep a triggered daily halt durable even if buy was blocked.
                self.db.execute("COMMIT")
                raise
            try:
                receipt = adapter.submit(ticker, side, qty, limit, row["identifier"])
                row.update(order_id=receipt["order_id"], branch=receipt.get("branch", ""), status="UNRECONCILED")
            except TradingDisabled:
                row["status"] = "NOT_SENT"
            except OrderRejected:
                row["status"] = "REJECTED"
            except Exception:
                # Includes validation errors after an external call: no retry.
                row["status"] = "UNKNOWN"
            self._save(row)
            return dict(row, state="accepted" if row["status"] == "UNRECONCILED" else row["status"].lower())

    def reconcile(self):
        with self._lock:
            for row in self.orders():
                if row["status"] in TERMINAL:
                    continue
                if not row["order_id"] and row["broker"] == "kis":
                    # KIS provides no client idempotency identifier. An ambiguous
                    # submission must be matched manually; do not guess by price.
                    continue
                try:
                    result = self.brokers[row["broker"]].order(row["order_id"], row["date"],
                        row.get("branch", ""), identifier=row["identifier"])
                    if result["filled_quantity"] < row.get("filled_quantity", 0):
                        raise BrokerError("Regressing execution snapshot")
                    if result["filled_quantity"] > row["quantity"]:
                        raise BrokerError("Execution exceeds requested quantity")
                    row.update(result)
                    if result['status'] in TERMINAL and result['filled_quantity']:
                        row['execution_status'] = result['status']
                        row['status'] = 'BALANCE_PENDING'
                        try:
                            balance = self.brokers[row['broker']].balance()
                            actual = number(balance['holdings'].get(row['ticker'], {}).get('quantity', 0))
                            expected = number(row['initial_quantity']) + number(result['filled_quantity']) * (1 if row['side'] == 'buy' else -1)
                            if abs(actual - expected) <= Decimal('0.000000005'):
                                row['status'] = result['status']
                        except BrokerError:
                            pass  # Persist the known fill while awaiting balance.
                    row["slippage"] = ((row["average_price"] / row["reference_price"] - 1)
                        * (1 if row["side"] == "buy" else -1)) if row["filled_quantity"] else 0
                    self._save(row)
                except BrokerError:
                    # Failed reads never erase an existing fill or release intent.
                    continue
            rows = self.orders()
            dates = {r['date'] for r in rows if r['broker'] == 'kis' and r.get('filled_quantity', 0)}
            for date in sorted(dates)[-5:]:
                try:
                    report = self.brokers['kis'].settlement(date)
                    self.db.execute('INSERT OR REPLACE INTO costs VALUES (?,?,?)', (self.scopes['kis'], date, json.dumps(report, allow_nan=False)))
                except BrokerError:
                    pass
            return rows

    def cost_reports(self):
        return [json.loads(r[0]) for r in self.db.execute('SELECT payload FROM costs WHERE scope=?', (self.scopes['kis'],))]

    def cancel(self, order_id):
        if not enabled(self.config):
            return {"order_id": order_id, "status": "DRY_RUN"}
        with self._lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                rows = [r for r in self.orders() if r["order_id"] == order_id]
                if len(rows) != 1:
                    raise BrokerError("Order identity ambiguous or absent from journal")
                row = rows[0]
                if not enabled(self.config, row["broker"]):
                    self.db.execute('COMMIT')
                    return {"order_id": order_id, "status": "DRY_RUN"}
                if row["status"] in TERMINAL or row["status"] in ("CANCEL_REQUESTED", "CANCEL_UNKNOWN"):
                    raise BrokerError("Order cannot be canceled again without reconciliation")
                row["status"] = "CANCEL_UNKNOWN"
                self._save(row)
                self.db.execute('COMMIT')
            except Exception:
                self.db.execute('ROLLBACK')
                raise
            try:
                self.brokers[row["broker"]].cancel(order_id, row["date"], row.get("branch", ""))
                row["status"] = "CANCEL_REQUESTED"
            except OrderRejected:
                row["status"] = "UNRECONCILED"
            except BrokerError:
                pass
            self._save(row)
            return row

    def close(self):
        for broker in self.brokers.values():
            broker.close()
        if self._db is not None:
            self._db.close()
            self._db = None
