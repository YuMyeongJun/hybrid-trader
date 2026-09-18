"""KIS domestic cash equities and Upbit KRW REST APIs. No implicit order retries.

Raw responses, credentials and transport exception messages must never be logged.
All mutation requests share the same fail-closed gate, including cancellations.
"""
import hashlib
import os
import re
import time
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation, ROUND_FLOOR, ROUND_CEILING
from urllib.parse import urlencode, unquote
from threading import RLock

import jwt
import requests

KST = timezone(timedelta(hours=9))


class BrokerError(RuntimeError):
    """Sanitized failure; the message never contains an API response."""


class OrderRejected(BrokerError):
    pass


class SubmissionUnknown(BrokerError):
    pass


class TradingDisabled(BrokerError):
    pass


def enabled(config, broker=None):
    global_gate = (config.enable_real_trading is True and config.dry_run is False
            and os.getenv("ENABLE_REAL_TRADING", "false").strip().lower() == "true"
            and os.getenv("DRY_RUN", "true").strip().lower() == "false")
    if not global_gate:
        return False
    if broker == "kis":
        return bool(config.enable_kis_paper_trading if config.kis_config.is_demo
                    else config.enable_kis_real_trading)
    if broker == "upbit":
        return bool(config.enable_upbit_trading)
    # A broker-less check is used only for the global dry-run fast path in
    # the journal layer; it never authorizes a network mutation.
    return True


def number(value, positive=False):
    try:
        if isinstance(value, bool) or value is None:
            raise ValueError
        result = Decimal(str(value))
        if not result.is_finite() or result < 0 or (positive and result == 0):
            raise ValueError
        return result
    except (ValueError, InvalidOperation):
        raise BrokerError("Invalid numeric data") from None


def text_number(value):
    return format(number(value), "f")


def round_price(value, market, side="buy"):
    price = number(value, True)
    if market == "kis":
        bands = [(500000, 1000), (200000, 500), (50000, 100), (20000, 50),
                 (5000, 10), (2000, 5), (0, 1)]
    else:
        bands = [(1000000, 1000), (500000, 500), (100000, 100), (50000, 50),
                 (10000, 10), (5000, 5), (100, 1), (10, '.1'), (1, '.01'),
                 ('.1', '.001'), ('.01', '.0001'), ('.001', '.00001'),
                 ('.0001', '.000001'), ('.00001', '.0000001'), (0, '.00000001')]
    tick = next(Decimal(str(step)) for lower, step in bands if price >= Decimal(str(lower)))
    rounded = (price / tick).to_integral_value(rounding=ROUND_FLOOR if side == "buy" else ROUND_CEILING) * tick
    return number(rounded, True)


def symbol(value, broker):
    pattern = r"[0-9]{6}" if broker == "kis" else r"KRW-[A-Z0-9]+"
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise BrokerError("Unsupported symbol; only domestic cash equities and KRW crypto are enabled")
    return value


class Transport:
    def __init__(self, config, session=None, sleep=time.sleep):
        self.config = config
        self.session = session or requests.Session()
        self.sleep = sleep
        self._next = 0.0
        self._lock = RLock()

    def request(self, method, base, path, params=None, headers=None, mutation=False, broker=None):
        if mutation and not enabled(self.config, broker):
            raise TradingDisabled("Order transmission disabled")
        attempts = 1 if mutation or method != "GET" else self.config.retry_count
        with self._lock:
            for attempt in range(attempts):
                wait = self._next - time.monotonic()
                if wait > self.config.timeout:
                    raise BrokerError('Broker rate-limit cooldown active')
                if wait > 0:
                    self.sleep(wait)
                # Conservative pacing also covers KIS paper's low request limit.
                self._next = time.monotonic() + (1.05 if "koreainvestment" in base else 0.14)
                try:
                    hdr = headers() if callable(headers) else (headers or {})
                    if mutation and not enabled(self.config, broker):
                        raise TradingDisabled("Order transmission disabled")
                    response = self.session.request(
                        method, base + path, headers=hdr,
                        **({"json": params} if method == "POST" else {"params": params}),
                        timeout=self.config.timeout, allow_redirects=False)
                except requests.RequestException:
                    if mutation:
                        raise SubmissionUnknown("Order response lost; reconciliation required") from None
                    if attempt + 1 == attempts:
                        raise BrokerError("Broker transport failed") from None
                    self.sleep(min(2 ** attempt, 8))
                    continue
                status = response.status_code
                remaining = response.headers.get("Remaining-Req", "")
                if re.search(r"sec=0(?:;|$)", remaining):
                    self._next = max(self._next, time.monotonic() + 1.05)
                if status in (418, 429) or status >= 500:
                    try:
                        delay = max(1.0, float(response.headers.get("Retry-After", 2 ** attempt)))
                        if not delay < 3600:
                            delay = 60
                    except (ValueError, TypeError):
                        delay = 60
                    self._next = max(self._next, time.monotonic() + delay)
                    if mutation:
                        raise SubmissionUnknown("Order outcome uncertain; no retry")
                    if status != 418 and attempt + 1 < attempts:
                        continue
                    raise BrokerError("Broker unavailable or rate limited")
                if not 200 <= status < 300:
                    if mutation and 400 <= status < 500:
                        raise OrderRejected("Broker rejected request")
                    if mutation:
                        raise SubmissionUnknown("Unexpected order response")
                    raise BrokerError("Broker request failed")
                try:
                    data = response.json()
                except (ValueError, TypeError):
                    error = SubmissionUnknown if mutation else BrokerError
                    raise error("Malformed broker response") from None
                return data, response.headers
        raise BrokerError("Broker request failed")

    def close(self):
        self.session.close()


class KISBroker:
    REAL_BASE = "https://openapi.koreainvestment.com:9443"
    DEMO_BASE = "https://openapivts.koreainvestment.com:29443"

    def __init__(self, config, transport=None):
        self.broker = "kis"
        self.config = config
        self.credentials = config.kis_config
        self.base = self.DEMO_BASE if self.credentials.is_demo else self.REAL_BASE
        self.http = transport or Transport(config)
        self._token = None
        self._expires = 0

    def _account(self):
        value = self.credentials.account_number.replace("-", "")
        if not re.fullmatch(r"\d{10}", value):
            raise BrokerError("KIS_ACCOUNT_NUMBER must contain 8 account digits and 2 product digits")
        return {"CANO": value[:8], "ACNT_PRDT_CD": value[8:]}

    def _headers(self, tr_id, continuation=""):
        if not self._token or time.time() >= self._expires - 60:
            data, _ = self.http.request("POST", self.base, "/oauth2/tokenP", {
                "grant_type": "client_credentials", "appkey": self.credentials.app_key,
                "appsecret": self.credentials.secret_key})
            if not isinstance(data, dict) or not isinstance(data.get("access_token"), str):
                raise BrokerError("KIS authentication failed")
            lifetime = number(data.get("expires_in"), True)
            self._token = data["access_token"]
            self._expires = time.time() + float(lifetime)
        return {"authorization": "Bearer " + self._token, "appkey": self.credentials.app_key,
                "appsecret": self.credentials.secret_key, "tr_id": tr_id,
                "custtype": "P", "tr_cont": continuation, "content-type": "application/json"}

    def _tr(self, value):
        return ("V" + value[1:]) if self.credentials.is_demo else value

    def _api(self, path, tr_id, params, method="GET", continuation=""):
        mutation = method != "GET"
        if mutation and not enabled(self.config, self.broker):
            raise TradingDisabled("Order transmission disabled")
        data, headers = self.http.request(method, self.base, "/uapi/domestic-stock/v1/" + path,
            params, lambda: self._headers(tr_id, continuation), mutation=mutation, broker=self.broker)
        if not isinstance(data, dict) or "rt_cd" not in data:
            raise (SubmissionUnknown if mutation else BrokerError)("Malformed KIS response")
        if data["rt_cd"] != "0":
            raise (OrderRejected if mutation else BrokerError)("KIS request rejected")
        return data, headers

    def _pages(self, path, tr_id, params, field="output1"):
        rows, seen, continuation = [], set(), ""
        for _ in range(100):
            data, headers = self._api(path, tr_id, params, continuation=continuation)
            page = data.get(field)
            if not isinstance(page, list) or not all(isinstance(row, dict) for row in page):
                raise BrokerError("Malformed KIS page")
            rows.extend(page)
            if headers.get("tr_cont", "") not in ("M", "F"):
                return rows, data
            cursor = (data.get("ctx_area_fk100", ""), data.get("ctx_area_nk100", ""))
            if cursor in seen or not any(cursor):
                raise BrokerError("Incomplete KIS pagination")
            seen.add(cursor)
            params = dict(params, CTX_AREA_FK100=cursor[0], CTX_AREA_NK100=cursor[1])
            continuation = "N"
        raise BrokerError("KIS pagination limit reached")

    def quote(self, ticker):
        symbol(ticker, "kis")
        data, _ = self._api("quotations/inquire-price", "FHKST01010100",
                           {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": ticker})
        try:
            row = data["output"]
            return {"price": float(number(row["stck_prpr"], True)),
                    "volume": float(number(row["acml_vol"])), "volume_key": datetime.now(KST).date().isoformat(),
                    "change": float(Decimal(row["prdy_ctrt"]))}
        except (KeyError, TypeError, InvalidOperation):
            raise BrokerError("Malformed KIS quote") from None

    def market_change(self):
        data, _ = self._api("quotations/inquire-index-price", "FHPUP02100000",
                           {"FID_COND_MRKT_DIV_CODE": "U", "FID_INPUT_ISCD": "0001"})
        try:
            value = Decimal(data["output"]["bstp_nmix_prdy_ctrt"])
            if not value.is_finite():
                raise ValueError
            return float(value)
        except (KeyError, TypeError, ValueError, InvalidOperation):
            raise BrokerError("Malformed KOSPI quote") from None

    def get_price(self, ticker):
        """Read-only scalar compatibility interface."""
        return self.quote(ticker)['price']

    def has_open_orders(self):
        today = datetime.now(KST).strftime('%Y%m%d')
        rows, _ = self._pages('trading/inquire-daily-ccld', self._tr('TTTC0081R'),
            dict(self._account(), INQR_STRT_DT=today, INQR_END_DT=today, SLL_BUY_DVSN_CD='00',
                 PDNO='', CCLD_DVSN='02', INQR_DVSN='00', INQR_DVSN_3='00', ORD_GNO_BRNO='',
                 ODNO='', INQR_DVSN_1='', CTX_AREA_FK100='', CTX_AREA_NK100='', EXCG_ID_DVSN_CD='KRX'))
        return any(number(row.get('rmn_qty')) > 0 for row in rows)

    def balance(self):
        params = dict(self._account(), AFHR_FLPR_YN="N", OFL_YN="", INQR_DVSN="02",
            UNPR_DVSN="01", FUND_STTL_ICLD_YN="N", FNCG_AMT_AUTO_RDPT_YN="N", PRCS_DVSN="00",
            CTX_AREA_FK100="", CTX_AREA_NK100="")
        rows, data = self._pages("trading/inquire-balance", self._tr("TTTC8434R"), params)
        try:
            totals = data["output2"][0]
            holdings = {}
            for row in rows:
                qty = number(row["hldg_qty"])
                if qty:
                    available = number(row["ord_psbl_qty"])
                    if available > qty:
                        raise BrokerError("Invalid available balance")
                    holdings[symbol(row["pdno"], "kis")] = {
                        "quantity": float(qty), "available": float(available),
                        "average_price": float(number(row["pchs_avg_pric"])),
                        "value": float(number(row["evlu_amt"]))}
            return {"holdings": holdings, "cash": float(number(totals["dnca_tot_amt"])),
                    "total_valuation": float(number(totals["tot_evlu_amt"]))}
        except (KeyError, IndexError, TypeError):
            raise BrokerError("Malformed KIS balance") from None

    def buying_power(self, ticker, price):
        data, _ = self._api("trading/inquire-psbl-order", self._tr("TTTC8908R"),
            dict(self._account(), PDNO=ticker, ORD_UNPR=text_number(price), ORD_DVSN="00",
                 CMA_EVLU_AMT_ICLD_YN="N", OVRS_ICLD_YN="N"))
        try:
            row = data["output"]
            return number(row["ord_psbl_cash"]), number(row["nrcvb_buy_qty"])
        except (KeyError, TypeError):
            raise BrokerError("Malformed KIS buying power") from None

    def settlement(self, date):
        """Actual account-day fees/taxes; never allocate aggregates to an order.

        KIS exposes this report only for live accounts. Reports may lag trades.
        They include manual account activity, so they are not bot-only P&L.
        """
        if self.credentials.is_demo:
            return {'status': 'UNAVAILABLE_IN_PAPER', 'fee': None, 'tax': None}
        _, data = self._pages('trading/inquire-period-trade-profit', 'TTTC8715R',
            dict(self._account(), SORT_DVSN='02', INQR_STRT_DT=date, INQR_END_DT=date,
                 CBLC_DVSN='00', PDNO='', CTX_AREA_FK100='', CTX_AREA_NK100=''))
        try:
            totals = data['output2']
            return {'status': 'ACCOUNT_AGGREGATE', 'date': date,
                'fee': float(number(totals['tot_fee'])), 'tax': float(number(totals['tot_tltx'])),
                'buy_amount': float(number(totals['buy_tr_amt_smtl'])),
                'sell_amount': float(number(totals['sll_tr_amt_smtl']))}
        except (KeyError, TypeError):
            raise BrokerError('Malformed KIS settlement report') from None

    def submit(self, ticker, side, quantity, price, identifier):
        if not enabled(self.config, self.broker):
            raise TradingDisabled("Order transmission disabled")
        symbol(ticker, "kis")
        qty = number(quantity, True)
        if qty != qty.to_integral_value() or side not in ("buy", "sell"):
            raise BrokerError("Invalid equity order")
        params = dict(self._account(), PDNO=ticker, ORD_DVSN="00", ORD_QTY=text_number(qty),
            ORD_UNPR=text_number(round_price(price, "kis", side)), EXCG_ID_DVSN_CD="KRX",
            SLL_TYPE="01" if side == "sell" else "", CNDT_PRIC="")
        data, _ = self._api("trading/order-cash", self._tr("TTTC0012U" if side == "buy" else "TTTC0011U"), params, "POST")
        try:
            output = data["output"]
            oid, branch = output["ODNO"], output["KRX_FWDG_ORD_ORGNO"]
            if not isinstance(oid, str) or not oid or not isinstance(branch, str) or not branch:
                raise ValueError
            return {"order_id": oid, "branch": branch, "state": "accepted"}
        except (KeyError, TypeError, ValueError):
            raise SubmissionUnknown("KIS acknowledgement missing order identity") from None

    def order(self, order_id, date, branch="", identifier=None):
        params = dict(self._account(), INQR_STRT_DT=date, INQR_END_DT=date, SLL_BUY_DVSN_CD="00",
            PDNO="", CCLD_DVSN="00", INQR_DVSN="00", INQR_DVSN_3="00", ORD_GNO_BRNO=branch,
            ODNO=order_id, INQR_DVSN_1="", CTX_AREA_FK100="", CTX_AREA_NK100="", EXCG_ID_DVSN_CD="KRX")
        rows, _ = self._pages("trading/inquire-daily-ccld", self._tr("TTTC0081R"), params)
        rows = [row for row in rows if row.get("odno") == order_id]
        if len(rows) != 1:
            raise BrokerError("KIS order not uniquely reconciled")
        try:
            row = rows[0]
            qty, filled = number(row["ord_qty"], True), number(row["tot_ccld_qty"])
            remaining, rejected = number(row["rmn_qty"]), number(row["rjct_qty"])
            amount = number(row["tot_ccld_amt"])
            if filled + remaining + rejected > qty or (filled > 0 and amount <= 0):
                raise BrokerError("Inconsistent KIS fill")
            state = "FILLED" if filled == qty else "PARTIALLY_FILLED" if filled else "OPEN"
            if row.get("cncl_yn") == "Y" and remaining == 0:
                state = "CANCELED"
            elif rejected == qty:
                state = "REJECTED"
            # This endpoint does NOT report per-order commission/tax. Never invent it.
            return {"order_id": order_id, "status": state, "filled_quantity": float(filled),
                    "filled_amount": float(amount), "average_price": float(amount / filled) if filled else 0,
                    "fee": None, "fee_status": "UNAVAILABLE", "remaining_quantity": float(remaining)}
        except (KeyError, TypeError):
            raise BrokerError("Malformed KIS execution") from None

    def cancel(self, order_id, date, branch=""):
        if not enabled(self.config, self.broker):
            raise TradingDisabled("Order transmission disabled")
        # Official cancel-availability endpoint is live-only. In paper mode use
        # the paper daily-order query to validate the outstanding remainder.
        if self.credentials.is_demo:
            if self.order(order_id, date, branch)["remaining_quantity"] <= 0:
                raise OrderRejected("No cancellable quantity")
        else:
            rows, _ = self._pages("trading/inquire-psbl-rvsecncl", "TTTC0084R",
                dict(self._account(), CTX_AREA_FK100="", CTX_AREA_NK100="", INQR_DVSN_1="0", INQR_DVSN_2="0"), "output")
            matches = [r for r in rows if r.get("odno") == order_id]
            if len(matches) != 1 or number(matches[0].get("psbl_qty")) <= 0:
                raise OrderRejected("No cancellable quantity")
            branch = matches[0]["krx_fwdg_ord_orgno"]
        if not branch:
            raise BrokerError("Missing KIS order branch")
        self._api("trading/order-rvsecncl", self._tr("TTTC0013U"),
            dict(self._account(), KRX_FWDG_ORD_ORGNO=branch, ORGN_ODNO=order_id, ORD_DVSN="00",
                 RVSE_CNCL_DVSN_CD="02", ORD_QTY="0", ORD_UNPR="0", QTY_ALL_ORD_YN="Y", EXCG_ID_DVSN_CD="KRX"), "POST")
        return {"order_id": order_id, "status": "CANCEL_REQUESTED"}

    def close(self):
        self.http.close()


class UpbitBroker:
    base = "https://api.upbit.com"

    def __init__(self, config, transport=None):
        self.broker = "upbit"
        self.config = config
        self.http = transport or Transport(config)

    def _headers(self, params):
        creds = self.config.upbit_config
        payload = {"access_key": creds.access_key, "nonce": str(uuid.uuid4())}
        if params:
            payload.update(query_hash=hashlib.sha512(unquote(urlencode(params, doseq=True)).encode()).hexdigest(), query_hash_alg="SHA512")
        return {"Authorization": "Bearer " + jwt.encode(payload, creds.secret_key, algorithm="HS512")}

    def _api(self, path, params=None, method="GET", private=True):
        data, _ = self.http.request(method, self.base, "/v1/" + path, params,
            (lambda: self._headers(params)) if private else {}, mutation=method != "GET",
            broker=self.broker)
        if isinstance(data, dict) and "error" in data:
            raise (OrderRejected if method != "GET" else BrokerError)("Upbit request rejected")
        return data

    def quote(self, ticker):
        symbol(ticker, "upbit")
        rows = self._api("ticker", {"markets": ticker}, private=False)
        try:
            row = rows[0]
            if len(rows) != 1 or row["market"] != ticker:
                raise ValueError
            return {"price": float(number(row["trade_price"], True)),
                    "volume": float(number(row["acc_trade_volume"])),
                    "volume_key": row["trade_date"],
                    "change": float(Decimal(str(row["signed_change_rate"])) * 100)}
        except (KeyError, TypeError, IndexError, ValueError, InvalidOperation):
            raise BrokerError("Malformed Upbit quote") from None

    def balance(self):
        rows = self._api("accounts")
        if not isinstance(rows, list):
            raise BrokerError("Malformed Upbit balances")
        cash, equity, holdings = Decimal(0), Decimal(0), {}
        try:
            for row in rows:
                available, locked = number(row["balance"]), number(row["locked"])
                if row["currency"] == "KRW":
                    cash = available
                    equity += available + locked
                elif available + locked:
                    ticker = symbol("KRW-" + row["currency"], "upbit")
                    value = (available + locked) * number(self.quote(ticker)["price"], True)
                    holdings[ticker] = {"quantity": float(available + locked), "available": float(available),
                        "average_price": float(number(row["avg_buy_price"])), "value": float(value)}
                    equity += value
            return {"holdings": holdings, "cash": float(cash), "total_valuation": float(equity)}
        except (KeyError, TypeError):
            raise BrokerError("Malformed Upbit balance") from None

    def get_ticker(self, ticker):
        """Read-only ticker compatibility interface."""
        return {'trade_price': self.quote(ticker)['price']}

    def has_open_orders(self):
        rows = self._api('orders/open', {'states[]': ['wait', 'watch'], 'limit': 1})
        if not isinstance(rows, list):
            raise BrokerError('Malformed Upbit open orders')
        return bool(rows)

    def chance(self, ticker):
        data = self._api("orders/chance", {"market": symbol(ticker, "upbit")})
        try:
            market = data["market"]
            if market["id"] != ticker or market["state"] != "active":
                raise BrokerError("Upbit market unavailable")
            return {"buy_fee": number(data["bid_fee"]), "sell_fee": number(data["ask_fee"]),
                "min_buy": number(market["bid"]["min_total"]), "min_sell": number(market["ask"]["min_total"]),
                "max_total": number(market["max_total"])}
        except (KeyError, TypeError):
            raise BrokerError("Malformed Upbit order constraints") from None

    def submit(self, ticker, side, quantity, price, identifier):
        symbol(ticker, "upbit")
        if side not in ("buy", "sell"):
            raise BrokerError("Invalid order side")
        qty = number(quantity, True).quantize(Decimal("0.00000001"), rounding=ROUND_FLOOR)
        number(qty, True)
        # Limit orders bound slippage; unfilled remainders are reconciled/canceled,
        # never silently converted into market orders.
        data = self._api("orders", {"market": ticker, "side": "bid" if side == "buy" else "ask",
            "volume": text_number(qty), "price": text_number(round_price(price, "upbit", side)),
            "ord_type": "limit", "identifier": identifier}, "POST")
        if not isinstance(data, dict) or not isinstance(data.get("uuid"), str) or not data["uuid"]:
            raise SubmissionUnknown("Upbit acknowledgement missing order identity")
        return {"order_id": data["uuid"], "state": "accepted"}

    def order(self, order_id, date=None, branch="", identifier=None):
        data = self._api("order", {"uuid": order_id} if order_id else {"identifier": identifier})
        try:
            if not data["uuid"] or (order_id and data["uuid"] != order_id):
                raise ValueError
            if not order_id and data.get('identifier') != identifier:
                raise ValueError
            qty, filled = number(data["volume"], True), number(data["executed_volume"])
            remaining, fee = number(data["remaining_volume"]), number(data["paid_fee"])
            trades = data["trades"]
            trade_qty = sum((number(t["volume"], True) for t in trades), Decimal(0))
            amount = sum((number(t["funds"], True) for t in trades), Decimal(0))
            if filled != trade_qty or filled + remaining > qty or data["state"] not in ("wait", "watch", "done", "cancel"):
                raise ValueError
            state = {"wait": "PARTIALLY_FILLED" if filled else "OPEN", "watch": "OPEN", "done": "FILLED", "cancel": "CANCELED"}[data["state"]]
            if state == "FILLED" and filled != qty:
                raise ValueError
            return {"order_id": data["uuid"], "status": state, "filled_quantity": float(filled),
                "filled_amount": float(amount), "average_price": float(amount / filled) if filled else 0,
                "fee": float(fee), "fee_status": "REPORTED", "remaining_quantity": float(remaining)}
        except (KeyError, TypeError, ValueError):
            raise BrokerError("Malformed Upbit execution") from None

    def cancel(self, order_id, date=None, branch=""):
        data = self._api("order", {"uuid": order_id}, "DELETE")
        if not isinstance(data, dict) or data.get("uuid") != order_id:
            raise SubmissionUnknown("Malformed cancellation acknowledgement")
        return {"order_id": order_id, "status": "CANCEL_REQUESTED"}

    def close(self):
        self.http.close()
