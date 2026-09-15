#!/usr/bin/env python
"""
하이브리드 트레이더 메인 - 글로벌 거래 통합 버전 (Hybrid Trader Main - Global Trading Integration)

이 모듈은 HybridTradingEngine을 기반으로 자동 거래 봇을 제공합니다.
한국 주식(KIS), 암호화폐(Upbit), 미국 주식(Alpaca), 유럽 주식(Interactive Brokers) 거래를
자동으로 관리하고 모니터링합니다.

주요 기능:
- 글로벌 시장 자동 모니터링
- 미국 주식 자동 거래 (Alpaca)
- 유럽 주식 자동 거래 (Interactive Brokers)
- 한국 주식 & 암호화폐 거래
- 실시간 거래 알림
- 텔레그램 알림 지원
"""

import os
import sys
import logging
import time
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import threading

from hybrid_trader import (
    HybridTradingEngine,
    TradingConfig,
    KISConfig,
    UpbitConfig,
    AlpacaConfig,
    InteractiveBrokersConfig,
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class MarketRegion(Enum):
    """시장 지역 정의"""
    KOREA = "korea"           # 한국 (KIS + Upbit)
    US = "us"                 # 미국 (Alpaca)
    EU = "eu"                 # 유럽 (Interactive Brokers)
    GLOBAL = "global"         # 글로벌 (모든 시장)


@dataclass
class GlobalTradingConfig:
    """글로벌 거래 설정

    글로벌 거래 기능을 제어하는 설정입니다.
    """
    ENABLE_GLOBAL_TRADING: bool = True        # 글로벌 거래 활성화 여부
    ENABLE_US_STOCK_TRADING: bool = True      # 미국 주식 거래 활성화
    ENABLE_EU_STOCK_TRADING: bool = True      # 유럽 주식 거래 활성화
    ENABLE_GLOBAL_MONITORING: bool = True     # 글로벌 시장 모니터링 활성화
    ENABLE_TELEGRAM_NOTIFICATION: bool = False  # 텔레그램 알림 활성화

    MONITORING_INTERVAL: int = 60             # 모니터링 간격 (초)
    TRADING_INTERVAL: int = 300               # 거래 실행 간격 (초)

    US_STOCK_SYMBOLS: List[str] = None        # 미국 주식 심볼 목록
    EU_STOCK_SYMBOLS: List[str] = None        # 유럽 주식 심볼 목록

    TELEGRAM_BOT_TOKEN: str = ""              # 텔레그램 봇 토큰
    TELEGRAM_CHAT_ID: str = ""                # 텔레그램 채팅 ID

    def __post_init__(self):
        """기본값 설정"""
        if self.US_STOCK_SYMBOLS is None:
            self.US_STOCK_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        if self.EU_STOCK_SYMBOLS is None:
            self.EU_STOCK_SYMBOLS = ["BMW", "SAP", "SIEMENS", "ASML", "LVMH"]


class TradingBot:
    """글로벌 자동 거래 봇

    HybridTradingEngine을 기반으로 한 자동 거래 봇입니다.
    한국, 미국, 유럽의 여러 시장에서 자동으로 거래합니다.
    """

    def __init__(
        self,
        config: TradingConfig,
        global_config: Optional[GlobalTradingConfig] = None,
        telegram_notifier=None
    ):
        """TradingBot 초기화

        Args:
            config (TradingConfig): 거래 설정
            global_config (Optional[GlobalTradingConfig]): 글로벌 거래 설정
            telegram_notifier: 텔레그램 알림 객체 (선택사항)
        """
        self.config = config
        self.global_config = global_config or GlobalTradingConfig()
        self.telegram_notifier = telegram_notifier

        # HybridTradingEngine 초기화
        try:
            self.engine = HybridTradingEngine(config)
            logger.info("✓ HybridTradingEngine 초기화 완료")
        except Exception as e:
            logger.error(f"✗ HybridTradingEngine 초기화 실패: {e}")
            raise

        # 글로벌 거래 설정 검증
        self._validate_global_config()

        # 거래 상태 추적
        self.is_running = False
        self.trading_thread = None
        self.monitoring_thread = None

        # 거래 통계
        self.trade_history: List[Dict[str, Any]] = []
        self.market_data: Dict[str, Any] = {}

        logger.info(f"✓ TradingBot 초기화 완료 (글로벌 거래: {self.global_config.ENABLE_GLOBAL_TRADING})")

    def _validate_global_config(self):
        """글로벌 거래 설정 검증"""
        if not self.global_config.ENABLE_GLOBAL_TRADING:
            logger.warning("⚠️  글로벌 거래가 비활성화되어 있습니다")
            return

    @staticmethod
    def _market_open(region: MarketRegion) -> bool:
        """Return whether the region is in its weekday regular session."""
        zones = {
            MarketRegion.US: ("America/New_York", dt_time(9, 30), dt_time(16, 0)),
            MarketRegion.EU: ("Europe/Berlin", dt_time(9, 0), dt_time(17, 30)),
            MarketRegion.KOREA: ("Asia/Seoul", dt_time(9, 0), dt_time(15, 30)),
        }
        zone, opening, closing = zones[region]
        now = datetime.now(ZoneInfo(zone))
        return now.weekday() < 5 and opening <= now.time() <= closing
        # 미국 주식 거래 설정 확인
        if self.global_config.ENABLE_US_STOCK_TRADING:
            if self.config.alpaca_config is None:
                logger.warning("⚠️  미국 주식 거래가 설정되었지만 Alpaca 설정이 없습니다")
            else:
                logger.info(f"✓ 미국 주식 거래 설정: Alpaca (Paper: {self.config.alpaca_config.is_paper})")

        # 유럽 주식 거래 설정 확인
        if self.global_config.ENABLE_EU_STOCK_TRADING:
            if self.config.ib_config is None:
                logger.warning("⚠️  유럽 주식 거래가 설정되었지만 Interactive Brokers 설정이 없습니다")
            else:
                logger.info(f"✓ 유럽 주식 거래 설정: Interactive Brokers (Demo: {self.config.ib_config.is_demo})")

    def send_notification(self, title: str, message: str, region: MarketRegion = MarketRegion.GLOBAL):
        """알림 전송 (텔레그램)

        Args:
            title (str): 제목
            message (str): 메시지
            region (MarketRegion): 시장 지역
        """
        # 로그에 항상 기록
        logger.info(f"[{region.value.upper()}] {title}: {message}")

        # 텔레그램 알림 전송
        if self.global_config.ENABLE_TELEGRAM_NOTIFICATION and self.telegram_notifier:
            try:
                full_message = f"🤖 *{title}*\n\n{message}\n\n시간: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                self.telegram_notifier.send_message(full_message)
            except Exception as e:
                logger.error(f"텔레그램 알림 전송 실패: {e}")

    def trade_us_stocks(self) -> Dict[str, Any]:
        """미국 주식 자동 거래 (Alpaca 사용)

        Returns:
            Dict[str, Any]: 거래 결과

        Raises:
            Exception: API 호출 실패 시
        """
        if not self.global_config.ENABLE_GLOBAL_TRADING or not self.global_config.ENABLE_US_STOCK_TRADING:
            logger.debug("미국 주식 거래가 비활성화되어 있습니다")
            return {"status": "disabled", "region": "US"}
        if not self._market_open(MarketRegion.US):
            return {"status": "closed", "region": "US", "trades": [], "errors": []}

        result = {
            "status": "pending",
            "region": "US",
            "trades": [],
            "errors": []
        }

        try:
            logger.info("🇺🇸 미국 주식 모니터링 및 거래 시작")

            # 미국 주식 가격 조회
            for symbol in self.global_config.US_STOCK_SYMBOLS:
                try:
                    price = self.engine.get_us_stock_price(symbol)

                    if price is not None:
                        logger.info(f"  {symbol}: ${price:,.2f}")

                        # 간단한 거래 로직 예시: 가격 변동에 따른 거래
                        # 실제 구현에서는 더 복잡한 거래 신호를 사용하세요
                        trade_signal = self._analyze_us_stock_signal(symbol, price)

                        if trade_signal:
                            trade_result = self._execute_us_stock_trade(symbol, trade_signal)
                            result["trades"].append(trade_result)
                            if trade_result["status"] != "unreconciled":
                                result["errors"].append(f"{symbol}: {trade_result['status']}")
                            self.send_notification(
                                f"미국 주식 거래 - {symbol}",
                                f"신호: {trade_signal['action']}\n가격: ${price:,.2f}",
                                MarketRegion.US
                            )
                    else:
                        logger.warning(f"  {symbol}: 가격 조회 실패")

                except Exception as e:
                    error_msg = f"{symbol} 거래 중 오류: {e}"
                    logger.error(f"  ✗ {error_msg}")
                    result["errors"].append(error_msg)

            result["status"] = "unreconciled" if result["trades"] and not result["errors"] else ("no_orders" if not result["errors"] else "partial")

        except Exception as e:
            logger.error(f"미국 주식 거래 중 오류: {e}")
            result["status"] = "failed"
            result["errors"].append(str(e))
            self.send_notification(
                "미국 주식 거래 오류",
                f"오류 메시지: {e}",
                MarketRegion.US
            )

        return result

    def trade_eu_stocks(self) -> Dict[str, Any]:
        """유럽 주식 자동 거래 (Interactive Brokers 사용)

        Returns:
            Dict[str, Any]: 거래 결과

        Raises:
            Exception: API 호출 실패 시
        """
        if not self.global_config.ENABLE_GLOBAL_TRADING or not self.global_config.ENABLE_EU_STOCK_TRADING:
            logger.debug("유럽 주식 거래가 비활성화되어 있습니다")
            return {"status": "disabled", "region": "EU"}
        if not self._market_open(MarketRegion.EU):
            return {"status": "closed", "region": "EU", "trades": [], "errors": []}

        result = {
            "status": "pending",
            "region": "EU",
            "trades": [],
            "errors": []
        }

        try:
            logger.info("🇪🇺 유럽 주식 모니터링 및 거래 시작")

            # 유럽 주식 가격 조회
            for symbol in self.global_config.EU_STOCK_SYMBOLS:
                try:
                    price = self.engine.get_eu_stock_price(symbol)

                    if price is not None:
                        logger.info(f"  {symbol}: {price:,.2f} EUR")

                        # 간단한 거래 로직 예시
                        trade_signal = self._analyze_eu_stock_signal(symbol, price)

                        if trade_signal:
                            trade_result = self._execute_eu_stock_trade(symbol, trade_signal)
                            result["trades"].append(trade_result)
                            if trade_result["status"] != "unreconciled":
                                result["errors"].append(f"{symbol}: {trade_result['status']}")
                            self.send_notification(
                                f"유럽 주식 거래 - {symbol}",
                                f"신호: {trade_signal['action']}\n가격: {price:,.2f} EUR",
                                MarketRegion.EU
                            )
                    else:
                        logger.warning(f"  {symbol}: 가격 조회 실패")

                except Exception as e:
                    error_msg = f"{symbol} 거래 중 오류: {e}"
                    logger.error(f"  ✗ {error_msg}")
                    result["errors"].append(error_msg)

            result["status"] = "unreconciled" if result["trades"] and not result["errors"] else ("no_orders" if not result["errors"] else "partial")

        except Exception as e:
            logger.error(f"유럽 주식 거래 중 오류: {e}")
            result["status"] = "failed"
            result["errors"].append(str(e))
            self.send_notification(
                "유럽 주식 거래 오류",
                f"오류 메시지: {e}",
                MarketRegion.EU
            )

        return result

    def monitor_global_markets(self) -> Dict[str, Any]:
        """글로벌 시장 모니터링

        한국, 미국, 유럽의 시장 데이터를 수집하고 분석합니다.

        Returns:
            Dict[str, Any]: 모니터링 결과
        """
        if not self.global_config.ENABLE_GLOBAL_MONITORING:
            logger.debug("글로벌 시장 모니터링이 비활성화되어 있습니다")
            return {}

        monitoring_result = {
            "timestamp": time.time(),
            "regions": {}
        }

        try:
            logger.info("🌍 글로벌 시장 모니터링")

            # 미국 시장 모니터링
            if self.global_config.ENABLE_US_STOCK_TRADING:
                us_market = self._monitor_us_market()
                monitoring_result["regions"]["US"] = us_market
                logger.info(f"  🇺🇸 미국: {len(us_market.get('prices', {}))} 종목 모니터링")

            # 유럽 시장 모니터링
            if self.global_config.ENABLE_EU_STOCK_TRADING:
                eu_market = self._monitor_eu_market()
                monitoring_result["regions"]["EU"] = eu_market
                logger.info(f"  🇪🇺 유럽: {len(eu_market.get('prices', {}))} 종목 모니터링")

            # 한국 시장 모니터링
            kr_market = self._monitor_korea_market()
            monitoring_result["regions"]["KR"] = kr_market
            logger.info(f"  🇰🇷 한국: {len(kr_market.get('prices', {}))} 종목 모니터링")

            # 모니터링 결과 저장
            self.market_data = monitoring_result

        except Exception as e:
            logger.error(f"글로벌 시장 모니터링 중 오류: {e}")
            self.send_notification(
                "시장 모니터링 오류",
                f"오류 메시지: {e}",
                MarketRegion.GLOBAL
            )

        return monitoring_result

    def _analyze_us_stock_signal(self, symbol: str, price: float) -> Optional[Dict[str, Any]]:
        """미국 주식 거래 신호 분석

        Args:
            symbol (str): 종목 심볼
            price (float): 현재 가격

        Returns:
            Optional[Dict[str, Any]]: 거래 신호 (매수/매도) 또는 None
        """
        # 간단한 예시: 가격이 특정 범위에 있으면 거래
        # 실제로는 더 복잡한 기술적 분석을 수행하세요

        if symbol == "AAPL" and 150 < price < 160:
            return {"action": "buy", "qty": 10, "price": price}

        return None

    def _analyze_eu_stock_signal(self, symbol: str, price: float) -> Optional[Dict[str, Any]]:
        """유럽 주식 거래 신호 분석

        Args:
            symbol (str): 종목 심볼
            price (float): 현재 가격

        Returns:
            Optional[Dict[str, Any]]: 거래 신호 (매수/매도) 또는 None
        """
        # 간단한 예시: 가격이 특정 범위에 있으면 거래
        # 실제로는 더 복잡한 기술적 분석을 수행하세요

        if symbol == "BMW" and 90 < price < 95:
            return {"action": "buy", "qty": 5, "price": price}

        return None

    def _execute_us_stock_trade(self, symbol: str, signal: Dict[str, Any]) -> Dict[str, Any]:
        """미국 주식 거래 실행

        Args:
            symbol (str): 종목 심볼
            signal (Dict[str, Any]): 거래 신호

        Returns:
            Dict[str, Any]: 거래 결과
        """
        trade_result = {
            "symbol": symbol,
            "action": signal["action"],
            "qty": signal["qty"],
            "price": signal["price"],
            "status": "pending"
        }

        try:
            if signal["action"] == "buy":
                order = self.engine.buy_us_stock(symbol, signal["qty"], signal["price"])
                receipt = submission_receipt(order)
                trade_result["order_id"] = receipt.order_id
                trade_result["status"] = receipt.status.lower()
                trade_result["broker_status"] = receipt.broker_status
                logger.info(f"  ✓ {symbol} 매수 주문 실행")

            elif signal["action"] == "sell":
                order = self.engine.sell_us_stock(symbol, signal["qty"], signal["price"])
                receipt = submission_receipt(order)
                trade_result["order_id"] = receipt.order_id
                trade_result["status"] = receipt.status.lower()
                trade_result["broker_status"] = receipt.broker_status
                logger.info(f"  ✓ {symbol} 매도 주문 실행")

            # 거래 히스토리에 기록
            trade_result["timestamp"] = time.time()
            self.trade_history.append(trade_result)

        except Exception as e:
            logger.error(f"  ✗ {symbol} 거래 실행 실패: {e}")
            trade_result["status"] = "not_sent" if isinstance(e, UnsupportedOperationError) else "unknown"
            trade_result["error"] = str(e)

        return trade_result

    def _execute_eu_stock_trade(self, symbol: str, signal: Dict[str, Any]) -> Dict[str, Any]:
        """유럽 주식 거래 실행

        Args:
            symbol (str): 종목 심볼
            signal (Dict[str, Any]): 거래 신호

        Returns:
            Dict[str, Any]: 거래 결과
        """
        trade_result = {
            "symbol": symbol,
            "action": signal["action"],
            "qty": signal["qty"],
            "price": signal["price"],
            "status": "pending"
        }

        try:
            if signal["action"] == "buy":
                order = self.engine.buy_eu_stock(symbol, signal["qty"], signal["price"])
                receipt = submission_receipt(order)
                trade_result["order_id"] = receipt.order_id
                trade_result["status"] = receipt.status.lower()
                trade_result["broker_status"] = receipt.broker_status
                logger.info(f"  ✓ {symbol} 매수 주문 실행")

            elif signal["action"] == "sell":
                order = self.engine.sell_eu_stock(symbol, signal["qty"], signal["price"])
                receipt = submission_receipt(order)
                trade_result["order_id"] = receipt.order_id
                trade_result["status"] = receipt.status.lower()
                trade_result["broker_status"] = receipt.broker_status
                logger.info(f"  ✓ {symbol} 매도 주문 실행")

            # 거래 히스토리에 기록
            trade_result["timestamp"] = time.time()
            self.trade_history.append(trade_result)

        except Exception as e:
            logger.error(f"  ✗ {symbol} 거래 실행 실패: {e}")
            trade_result["status"] = "not_sent" if isinstance(e, UnsupportedOperationError) else "unknown"
            trade_result["error"] = str(e)

        return trade_result

    def _monitor_us_market(self) -> Dict[str, Any]:
        """미국 시장 데이터 수집

        Returns:
            Dict[str, Any]: 미국 시장 데이터
        """
        market_data = {
            "region": "US",
            "timestamp": time.time(),
            "prices": {},
            "errors": []
        }

        for symbol in self.global_config.US_STOCK_SYMBOLS:
            try:
                price = self.engine.get_us_stock_price(symbol)
                if price is not None:
                    market_data["prices"][symbol] = price
            except Exception as e:
                logger.debug(f"미국 {symbol} 가격 조회 실패: {e}")
                market_data["errors"].append(f"{symbol}: {e}")

        return market_data

    def _monitor_eu_market(self) -> Dict[str, Any]:
        """유럽 시장 데이터 수집

        Returns:
            Dict[str, Any]: 유럽 시장 데이터
        """
        market_data = {
            "region": "EU",
            "timestamp": time.time(),
            "prices": {},
            "errors": []
        }

        for symbol in self.global_config.EU_STOCK_SYMBOLS:
            try:
                price = self.engine.get_eu_stock_price(symbol)
                if price is not None:
                    market_data["prices"][symbol] = price
            except Exception as e:
                logger.debug(f"유럽 {symbol} 가격 조회 실패: {e}")
                market_data["errors"].append(f"{symbol}: {e}")

        return market_data

    def _monitor_korea_market(self) -> Dict[str, Any]:
        """한국 시장 데이터 수집

        Returns:
            Dict[str, Any]: 한국 시장 데이터
        """
        market_data = {
            "region": "KR",
            "timestamp": time.time(),
            "prices": {},
            "errors": []
        }

        # 한국 주식 샘플
        kr_stocks = ["005930", "000660"]  # 삼성전자, SK하이닉스

        for ticker in kr_stocks:
            try:
                price = self.engine.get_stock_price(ticker)
                if price is not None:
                    market_data["prices"][ticker] = price
            except Exception as e:
                logger.debug(f"한국 {ticker} 가격 조회 실패: {e}")
                market_data["errors"].append(f"{ticker}: {e}")

        return market_data

    def _trading_loop(self):
        """자동 거래 루프 (스레드에서 실행)

        일정 간격으로 글로벌 시장을 모니터링하고 자동 거래를 실행합니다.
        """
        logger.info("자동 거래 루프 시작")

        while self.is_running:
            try:
                # 미국 주식 거래
                if self.global_config.ENABLE_US_STOCK_TRADING:
                    us_result = self.trade_us_stocks()
                    if us_result.get("status") == "failed":
                        self.send_notification(
                            "미국 주식 거래 실패",
                            f"오류: {us_result.get('errors', [])}",
                            MarketRegion.US
                        )

                # 유럽 주식 거래
                if self.global_config.ENABLE_EU_STOCK_TRADING:
                    eu_result = self.trade_eu_stocks()
                    if eu_result.get("status") == "failed":
                        self.send_notification(
                            "유럽 주식 거래 실패",
                            f"오류: {eu_result.get('errors', [])}",
                            MarketRegion.EU
                        )

                # 다음 거래 주기까지 대기
                time.sleep(self.global_config.TRADING_INTERVAL)

            except Exception as e:
                logger.error(f"거래 루프 오류: {e}")
                self.send_notification(
                    "거래 루프 오류",
                    f"오류 메시지: {e}",
                    MarketRegion.GLOBAL
                )
                time.sleep(10)

        logger.info("자동 거래 루프 종료")

    def _monitoring_loop(self):
        """시장 모니터링 루프 (스레드에서 실행)

        지속적으로 글로벌 시장 데이터를 수집합니다.
        """
        logger.info("시장 모니터링 루프 시작")

        while self.is_running:
            try:
                # 글로벌 시장 모니터링
                monitoring_result = self.monitor_global_markets()

                # 모니터링 간격만큼 대기
                time.sleep(self.global_config.MONITORING_INTERVAL)

            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(10)

        logger.info("시장 모니터링 루프 종료")

    def start(self):
        """거래 봇 시작

        자동 거래 루프 및 모니터링 루프를 시작합니다.
        """
        if self.is_running:
            logger.warning("거래 봇이 이미 실행 중입니다")
            return

        self.is_running = True
        logger.info("=" * 70)
        logger.info("🤖 거래 봇 시작")
        logger.info("=" * 70)

        # 글로벌 거래 여부 확인
        if self.global_config.ENABLE_GLOBAL_TRADING:
            logger.info("✓ 글로벌 거래 활성화")
            if self.global_config.ENABLE_US_STOCK_TRADING:
                logger.info(f"  ✓ 미국 주식: {', '.join(self.global_config.US_STOCK_SYMBOLS)}")
            if self.global_config.ENABLE_EU_STOCK_TRADING:
                logger.info(f"  ✓ 유럽 주식: {', '.join(self.global_config.EU_STOCK_SYMBOLS)}")

        # 거래 루프 시작
        self.trading_thread = threading.Thread(
            target=self._trading_loop,
            daemon=True,
            name="TradingLoop"
        )
        self.trading_thread.start()

        # 모니터링 루프 시작 (선택사항)
        if self.global_config.ENABLE_GLOBAL_MONITORING:
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="MonitoringLoop"
            )
            self.monitoring_thread.start()

        self.send_notification(
            "거래 봇 시작",
            f"글로벌 거래 활성화: {self.global_config.ENABLE_GLOBAL_TRADING}",
            MarketRegion.GLOBAL
        )

    def stop(self):
        """거래 봇 종료

        자동 거래 루프 및 모니터링 루프를 종료합니다.
        """
        if not self.is_running:
            logger.warning("거래 봇이 실행 중이지 않습니다")
            return

        self.is_running = False
        logger.info("=" * 70)
        logger.info("🛑 거래 봇 종료 대기 중...")
        logger.info("=" * 70)

        # 스레드 종료 대기
        if self.trading_thread:
            self.trading_thread.join(timeout=5)
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        # 엔진 종료
        try:
            self.engine.close()
            logger.info("✓ HybridTradingEngine 종료")
        except Exception as e:
            logger.error(f"엔진 종료 중 오류: {e}")

        logger.info("✓ 거래 봇 종료 완료")
        self.send_notification(
            "거래 봇 종료",
            "거래 봇이 정상적으로 종료되었습니다",
            MarketRegion.GLOBAL
        )

    def get_status(self) -> Dict[str, Any]:
        """거래 봇 상태 조회

        Returns:
            Dict[str, Any]: 거래 봇 상태 정보
        """
        return {
            "is_running": self.is_running,
            "global_trading_enabled": self.global_config.ENABLE_GLOBAL_TRADING,
            "us_stock_trading_enabled": self.global_config.ENABLE_US_STOCK_TRADING,
            "eu_stock_trading_enabled": self.global_config.ENABLE_EU_STOCK_TRADING,
            "trade_count": len(self.trade_history),
            "market_data": self.market_data,
            "recent_trades": self.trade_history[-5:] if self.trade_history else []
        }


def setup_config() -> tuple:
    """환경변수에서 거래 설정을 로드합니다

    Returns:
        tuple: (TradingConfig, GlobalTradingConfig)
    """
    # 기본 거래 설정 (필수)
    required_env_vars = [
        'KIS_APP_KEY', 'KIS_SECRET_KEY', 'KIS_ACCOUNT', 'KIS_HTS_ID',
        'UPBIT_ACCESS_KEY', 'UPBIT_SECRET_KEY'
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        logger.error("❌ 필수 환경변수가 설정되지 않았습니다:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        sys.exit(1)

    # KIS 설정
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY"),
        secret_key=os.getenv("KIS_SECRET_KEY"),
        account_number=os.getenv("KIS_ACCOUNT"),
        hts_id=os.getenv("KIS_HTS_ID"),
        is_demo=os.getenv("KIS_DEMO", "true").lower() == "true"
    )

    # Upbit 설정
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY"),
        secret_key=os.getenv("UPBIT_SECRET_KEY")
    )

    # Alpaca 설정 (선택사항)
    alpaca_config = None
    if os.getenv("ALPACA_API_KEY") and os.getenv("ALPACA_SECRET_KEY"):
        alpaca_config = AlpacaConfig(
            api_key=os.getenv("ALPACA_API_KEY"),
            secret_key=os.getenv("ALPACA_SECRET_KEY"),
            base_url=os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
            is_paper=os.getenv("ALPACA_PAPER", "true").lower() == "true"
        )
        logger.info("✓ Alpaca 설정 로드됨")

    # Interactive Brokers 설정 (선택사항)
    ib_config = None
    if os.getenv("IB_ACCOUNT_ID"):
        ib_config = InteractiveBrokersConfig(
            account_id=os.getenv("IB_ACCOUNT_ID"),
            host=os.getenv("IB_HOST", "127.0.0.1"),
            port=int(os.getenv("IB_PORT", "7497")),
            client_id=int(os.getenv("IB_CLIENT_ID", "1")),
            is_demo=os.getenv("IB_DEMO", "true").lower() == "true"
        )
        logger.info("✓ Interactive Brokers 설정 로드됨")

    # TradingConfig 생성
    trading_config = TradingConfig(
        kis_config=kis_config,
        upbit_config=upbit_config,
        alpaca_config=alpaca_config,
        ib_config=ib_config,
        timeout=int(os.getenv("API_TIMEOUT", "10")),
        retry_count=int(os.getenv("API_RETRY_COUNT", "3"))
    )

    # GlobalTradingConfig 생성
    global_config = GlobalTradingConfig(
        ENABLE_GLOBAL_TRADING=os.getenv("ENABLE_GLOBAL_TRADING", "true").lower() == "true",
        ENABLE_US_STOCK_TRADING=os.getenv("ENABLE_US_STOCK_TRADING", "true").lower() == "true",
        ENABLE_EU_STOCK_TRADING=os.getenv("ENABLE_EU_STOCK_TRADING", "true").lower() == "true",
        ENABLE_GLOBAL_MONITORING=os.getenv("ENABLE_GLOBAL_MONITORING", "true").lower() == "true",
        ENABLE_TELEGRAM_NOTIFICATION=os.getenv("ENABLE_TELEGRAM_NOTIFICATION", "false").lower() == "true",
        MONITORING_INTERVAL=int(os.getenv("MONITORING_INTERVAL", "60")),
        TRADING_INTERVAL=int(os.getenv("TRADING_INTERVAL", "300")),
        US_STOCK_SYMBOLS=os.getenv("US_STOCK_SYMBOLS", "AAPL,MSFT,GOOGL").split(","),
        EU_STOCK_SYMBOLS=os.getenv("EU_STOCK_SYMBOLS", "BMW,SAP,SIEMENS").split(","),
        TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID", "")
    )

    return trading_config, global_config


def main():
    """메인 함수 - 거래 봇 실행"""

    print("=" * 70)
    print("🤖 Hybrid Trader - Global Trading Integration")
    print("=" * 70)
    print()

    try:
        # 설정 로드
        trading_config, global_config = setup_config()
        logger.info("✓ 설정을 성공적으로 로드했습니다")

        # 거래 봇 생성
        bot = TradingBot(trading_config, global_config)

        # 거래 봇 시작
        bot.start()

        # 봇이 실행 중이므로 메인 스레드에서 대기
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n종료 신호 수신...")
            bot.stop()

        print()
        print("=" * 70)
        print("✓ 거래 봇 정상 종료")
        print("=" * 70)

    except Exception as e:
        logger.error(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
