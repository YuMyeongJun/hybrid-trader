#!/usr/bin/env python
"""
포트폴리오 분석 예제 (Portfolio Analyzer Example)

이 예제는 보유한 주식과 암호화폐의 포트폴리오를 분석하고,
수익률, 평가액 등을 계산하는 방법을 보여줍니다.

주요 기능:
- 포트폴리오 구성
- 현재 평가액 계산
- 수익/손실 계산
- 수익률 분석
- 자산 배분 분석
"""

import os
import logging
import sys
from typing import Dict, Optional, List
from dataclasses import dataclass
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Holding:
    """보유 자산 정보"""
    ticker: str
    name: str
    asset_type: str  # "stock" 또는 "crypto"
    quantity: float
    purchase_price: float

    @property
    def purchase_value(self) -> float:
        """매입액"""
        return self.quantity * self.purchase_price

    def get_current_value(self, current_price: Optional[float]) -> Optional[float]:
        """현재 평가액"""
        if current_price is None:
            return None
        return self.quantity * current_price

    def get_profit(self, current_price: Optional[float]) -> Optional[float]:
        """수익/손실"""
        if current_price is None:
            return None
        return self.get_current_value(current_price) - self.purchase_value

    def get_profit_rate(self, current_price: Optional[float]) -> Optional[float]:
        """수익률 (%)"""
        if current_price is None or self.purchase_value == 0:
            return None
        return (self.get_profit(current_price) / self.purchase_value) * 100


class PortfolioAnalyzer:
    """포트폴리오 분석 도구"""

    def __init__(self, engine: HybridTradingEngine):
        """
        분석기 초기화

        Args:
            engine: HybridTradingEngine 인스턴스
        """
        self.engine = engine
        self.holdings: Dict[str, Holding] = {}
        self.current_prices: Dict[str, Optional[float]] = {}

    def add_holding(self, ticker: str, name: str, asset_type: str,
                   quantity: float, purchase_price: float):
        """
        포트폴리오에 자산 추가

        Args:
            ticker: 자산 코드
            name: 자산 이름
            asset_type: 자산 유형 ("stock" 또는 "crypto")
            quantity: 수량
            purchase_price: 매입가
        """
        if asset_type not in ["stock", "crypto"]:
            raise ValueError(f"Invalid asset type: {asset_type}")

        self.holdings[ticker] = Holding(
            ticker=ticker,
            name=name,
            asset_type=asset_type,
            quantity=quantity,
            purchase_price=purchase_price
        )

        logger.info(f"✓ {name}을(를) 포트폴리오에 추가했습니다")

    def fetch_current_prices(self) -> bool:
        """
        현재 가격을 조회합니다

        Returns:
            성공 여부
        """
        print("\n" + "=" * 70)
        print("📊 현재 가격 조회 중...")
        print("=" * 70)

        success_count = 0

        for ticker, holding in self.holdings.items():
            try:
                if holding.asset_type == "stock":
                    price = self.engine.get_stock_price(ticker)
                else:  # crypto
                    price = self.engine.get_coin_price(ticker)

                self.current_prices[ticker] = price

                if price is not None:
                    logger.info(f"✓ {holding.name}: {price:,.0f} KRW")
                    success_count += 1
                else:
                    logger.warning(f"✗ {holding.name}: 가격 조회 실패")

            except Exception as e:
                logger.error(f"오류 - {holding.name}: {e}")

        return success_count > 0

    def print_portfolio_summary(self):
        """포트폴리오 요약 출력"""
        if not self.current_prices or not self.holdings:
            logger.warning("포트폴리오 데이터가 없습니다")
            return

        print("\n" + "=" * 100)
        print("💼 포트폴리오 상세 분석")
        print("=" * 100)
        print()

        # 헤더
        header = f"{'자산':<15} {'수량':<12} {'매입가':<15} {'현재가':<15} {'평가액':<15} {'수익/손실':<15} {'수익률':<10}"
        print(header)
        print("-" * 100)

        total_purchase = 0
        total_current = 0
        total_profit = 0

        for ticker, holding in self.holdings.items():
            current_price = self.current_prices.get(ticker)
            current_value = holding.get_current_value(current_price)
            profit = holding.get_profit(current_price)
            profit_rate = holding.get_profit_rate(current_price)

            if current_value is None:
                print(f"{holding.name:<15} {holding.quantity:<12.4f} {holding.purchase_price:<15,.0f} {'N/A':<15} {'N/A':<15} {'N/A':<15} {'N/A':<10}")
                continue

            # 데이터 계산
            total_purchase += holding.purchase_value
            total_current += current_value
            if profit is not None:
                total_profit += profit

            # 포맷팅
            profit_str = f"{profit:,.0f}" if profit else "N/A"
            profit_rate_str = f"{profit_rate:+.2f}%" if profit_rate else "N/A"

            print(f"{holding.name:<15} {holding.quantity:<12.4f} {holding.purchase_price:<15,.0f} {current_price:<15,.0f} {current_value:<15,.0f} {profit_str:>14} {profit_rate_str:>9}")

        # 요약
        print("-" * 100)
        total_profit_rate = (total_profit / total_purchase * 100) if total_purchase > 0 else 0

        print(f"\n{'합계':<15} {'':<12} {'':<15} {'':<15} {total_current:<15,.0f} {total_profit:>14,.0f} {total_profit_rate:>9.2f}%")

        print()
        print("=" * 100)
        print("📈 포트폴리오 요약")
        print("=" * 100)
        print(f"총 매입액: {total_purchase:,.0f} KRW")
        print(f"현재 평가액: {total_current:,.0f} KRW")
        print(f"총 수익/손실: {total_profit:+,.0f} KRW")
        print(f"총 수익률: {total_profit_rate:+.2f}%")

    def print_asset_allocation(self):
        """자산 배분 분석"""
        if not self.current_prices or not self.holdings:
            return

        print("\n" + "=" * 70)
        print("📊 자산 배분 분석")
        print("=" * 70)
        print()

        # 자산 유형별 계산
        stock_value = 0
        crypto_value = 0

        for ticker, holding in self.holdings.items():
            current_price = self.current_prices.get(ticker)
            current_value = holding.get_current_value(current_price)

            if current_value is None:
                continue

            if holding.asset_type == "stock":
                stock_value += current_value
            else:
                crypto_value += current_value

        total_value = stock_value + crypto_value

        if total_value == 0:
            logger.warning("평가액이 0입니다")
            return

        stock_ratio = (stock_value / total_value) * 100
        crypto_ratio = (crypto_value / total_value) * 100

        print(f"주식 투자액: {stock_value:>15,.0f} KRW ({stock_ratio:>6.2f}%)")
        print(f"암호화폐 투자액: {crypto_value:>10,.0f} KRW ({crypto_ratio:>6.2f}%)")
        print(f"{'─' * 40}")
        print(f"총 투자액: {total_value:>15,.0f} KRW (100.00%)")

        # 시각화 (간단한 바 차트)
        print()
        bar_length = 50
        stock_bar = int(stock_ratio / 2)
        crypto_bar = int(crypto_ratio / 2)

        print("시각화:")
        print(f"주식    [{('█' * stock_bar):50s}] {stock_ratio:.2f}%")
        print(f"암호화폐 [{('█' * crypto_bar):50s}] {crypto_ratio:.2f}%")

    def print_top_holdings(self, limit: int = 5):
        """상위 자산 출력"""
        if not self.current_prices or not self.holdings:
            return

        print("\n" + "=" * 70)
        print(f"🏆 상위 {limit}대 자산")
        print("=" * 70)
        print()

        # 평가액 기준으로 정렬
        sorted_holdings = []

        for ticker, holding in self.holdings.items():
            current_price = self.current_prices.get(ticker)
            current_value = holding.get_current_value(current_price)

            if current_value is not None:
                sorted_holdings.append((holding.name, current_value, current_price))

        sorted_holdings.sort(key=lambda x: x[1], reverse=True)

        total_value = sum(h[1] for h in sorted_holdings)

        for i, (name, value, price) in enumerate(sorted_holdings[:limit], 1):
            ratio = (value / total_value * 100) if total_value > 0 else 0
            print(f"{i}. {name:<20} {value:>15,.0f} KRW ({ratio:>6.2f}%)")


def setup_config() -> TradingConfig:
    """환경변수에서 거래 설정을 로드합니다"""
    required_env_vars = [
        'KIS_APP_KEY',
        'KIS_SECRET_KEY',
        'KIS_ACCOUNT',
        'KIS_HTS_ID',
        'UPBIT_ACCESS_KEY',
        'UPBIT_SECRET_KEY'
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ 필수 환경변수가 설정되지 않았습니다:")
        for var in missing_vars:
            print(f"  - {var}")
        sys.exit(1)

    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY"),
        secret_key=os.getenv("KIS_SECRET_KEY"),
        account_number=os.getenv("KIS_ACCOUNT"),
        hts_id=os.getenv("KIS_HTS_ID"),
        is_demo=True
    )

    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY"),
        secret_key=os.getenv("UPBIT_SECRET_KEY")
    )

    return TradingConfig(kis_config=kis_config, upbit_config=upbit_config)


def main():
    """메인 함수 - 포트폴리오 분석 예제"""

    print("=" * 70)
    print("🚀 Hybrid Trader - 포트폴리오 분석 예제")
    print("=" * 70)
    print()

    try:
        config = setup_config()
        logger.info("✓ 설정을 성공적으로 로드했습니다")
    except SystemExit:
        return

    try:
        with HybridTradingEngine(config) as engine:
            logger.info("✓ Hybrid Trading Engine이 초기화되었습니다")

            # 분석기 생성
            analyzer = PortfolioAnalyzer(engine)

            # 포트폴리오 구성
            print("\n" + "=" * 70)
            print("📝 포트폴리오 구성")
            print("=" * 70)
            print()

            # 주식 추가
            analyzer.add_holding("005930", "삼성전자", "stock", 10, 70000)
            analyzer.add_holding("000660", "SK하이닉스", "stock", 5, 85000)
            analyzer.add_holding("005380", "현대차", "stock", 20, 50000)

            # 암호화폐 추가
            analyzer.add_holding("KRW-BTC", "비트코인", "crypto", 0.1, 50000000)
            analyzer.add_holding("KRW-ETH", "이더리움", "crypto", 1, 2000000)

            # 현재 가격 조회
            if analyzer.fetch_current_prices():
                # 분석 결과 출력
                analyzer.print_portfolio_summary()
                analyzer.print_asset_allocation()
                analyzer.print_top_holdings(3)
            else:
                logger.error("가격 조회 실패")

            print("\n" + "=" * 70)
            print("예제 완료!")
            print("=" * 70)

    except Exception as e:
        logger.error(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
