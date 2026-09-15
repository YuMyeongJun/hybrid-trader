#!/usr/bin/env python
"""
하이브리드 거래 전략 예제 (Hybrid Trading Strategy Example)

이 예제는 주식과 암호화폐를 함께 활용하는 고급 거래 전략을 보여줍니다.
포트폴리오 분산, 자산 배분, 리밸런싱 등의 개념을 구현합니다.

주요 기능:
- 포트폴리오 자산 배분 전략
- 가격 변동에 따른 알림
- 리밸런싱 추천
- 시나리오 분석
"""

import os
import logging
import sys
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AllocationStrategy:
    """자산 배분 전략"""
    name: str
    stock_ratio: float  # 주식 비중
    crypto_ratio: float  # 암호화폐 비중

    def validate(self) -> bool:
        """전략 검증"""
        total = self.stock_ratio + self.crypto_ratio
        if abs(total - 1.0) > 0.01:  # 오차 범위 1%
            logger.error(f"Invalid allocation: {total}")
            return False
        return True


class HybridTradingStrategy:
    """하이브리드 거래 전략 엔진"""

    def __init__(self, engine: HybridTradingEngine, initial_budget: float):
        """
        전략 엔진 초기화

        Args:
            engine: HybridTradingEngine 인스턴스
            initial_budget: 초기 투자 금액
        """
        self.engine = engine
        self.initial_budget = initial_budget
        self.prices: Dict[str, Optional[float]] = {}
        self.strategies: Dict[str, AllocationStrategy] = {}
        self._setup_strategies()

    def _setup_strategies(self):
        """기본 전략 설정"""
        self.strategies = {
            "conservative": AllocationStrategy(
                name="보수적 (Conservative)",
                stock_ratio=0.3,      # 주식 30%
                crypto_ratio=0.7      # 암호화폐 70%... 실제로는 0.7이 높지만 예제용
            ),
            "balanced": AllocationStrategy(
                name="균형적 (Balanced)",
                stock_ratio=0.6,      # 주식 60%
                crypto_ratio=0.4      # 암호화폐 40%
            ),
            "aggressive": AllocationStrategy(
                name="공격적 (Aggressive)",
                stock_ratio=0.8,      # 주식 80%
                crypto_ratio=0.2      # 암호화폐 20%
            )
        }

    def fetch_prices(self, stocks: Dict[str, str], cryptos: Dict[str, str]) -> bool:
        """
        주식과 암호화폐 가격 조회

        Args:
            stocks: {"코드": "이름"}
            cryptos: {"코드": "이름"}

        Returns:
            성공 여부
        """
        print("\n" + "=" * 70)
        print("📊 시장 데이터 수집 중...")
        print("=" * 70)

        success_count = 0

        # 주식 가격 조회
        print("\n📈 주식:")
        for ticker, name in stocks.items():
            try:
                price = self.engine.get_stock_price(ticker)
                if price is not None:
                    self.prices[ticker] = price
                    logger.info(f"✓ {name}: {price:,.0f} KRW")
                    success_count += 1
                else:
                    logger.warning(f"✗ {name}: 조회 실패")
            except Exception as e:
                logger.error(f"오류 - {name}: {e}")

        # 암호화폐 가격 조회
        print("\n💰 암호화폐:")
        for ticker, name in cryptos.items():
            try:
                price = self.engine.get_coin_price(ticker)
                if price is not None:
                    self.prices[ticker] = price
                    logger.info(f"✓ {name}: {price:,.0f} KRW")
                    success_count += 1
                else:
                    logger.warning(f"✗ {name}: 조회 실패")
            except Exception as e:
                logger.error(f"오류 - {name}: {e}")

        return success_count > 0

    def calculate_portfolio(self, strategy_name: str,
                          stocks: Dict[str, str],
                          cryptos: Dict[str, str]) -> Optional[Dict]:
        """
        전략에 따른 포트폴리오 계산

        Args:
            strategy_name: 전략 이름
            stocks: {"코드": "이름"}
            cryptos: {"코드": "이름"}

        Returns:
            포트폴리오 정보
        """
        if strategy_name not in self.strategies:
            logger.error(f"Unknown strategy: {strategy_name}")
            return None

        strategy = self.strategies[strategy_name]

        if not strategy.validate():
            return None

        # 자산 배분 계산
        stock_budget = self.initial_budget * strategy.stock_ratio
        crypto_budget = self.initial_budget * strategy.crypto_ratio

        # 각 종목별 배분
        stock_per_allocation = stock_budget / len(stocks)
        crypto_per_allocation = crypto_budget / len(cryptos)

        portfolio = {
            'strategy_name': strategy.name,
            'total_budget': self.initial_budget,
            'stock_budget': stock_budget,
            'crypto_budget': crypto_budget,
            'stocks': {},
            'cryptos': {}
        }

        # 주식 계산
        for ticker, name in stocks.items():
            price = self.prices.get(ticker)
            if price is not None and price > 0:
                quantity = int(stock_per_allocation / price)
                investment = quantity * price
                portfolio['stocks'][ticker] = {
                    'name': name,
                    'quantity': quantity,
                    'price': price,
                    'investment': investment
                }

        # 암호화폐 계산
        for ticker, name in cryptos.items():
            price = self.prices.get(ticker)
            if price is not None and price > 0:
                quantity = crypto_per_allocation / price
                investment = quantity * price
                portfolio['cryptos'][ticker] = {
                    'name': name,
                    'quantity': quantity,
                    'price': price,
                    'investment': investment
                }

        return portfolio

    def print_portfolio(self, portfolio: Dict):
        """포트폴리오 상세 출력"""
        if not portfolio:
            logger.warning("포트폴리오가 없습니다")
            return

        print("\n" + "=" * 70)
        print(f"💼 포트폴리오: {portfolio['strategy_name']}")
        print("=" * 70)
        print()
        print(f"총 투자액: {portfolio['total_budget']:,.0f} KRW")
        print(f"주식 배분: {portfolio['stock_budget']:,.0f} KRW ({portfolio['stock_budget']/portfolio['total_budget']*100:.1f}%)")
        print(f"암호화폐 배분: {portfolio['crypto_budget']:,.0f} KRW ({portfolio['crypto_budget']/portfolio['total_budget']*100:.1f}%)")
        print()

        # 주식 투자 계획
        if portfolio['stocks']:
            print("📈 주식 투자 계획")
            print("-" * 70)
            print(f"{'종목':<15} {'수량':<10} {'가격':<15} {'투자액':<15}")
            print("-" * 70)

            for ticker, info in portfolio['stocks'].items():
                print(f"{info['name']:<15} {info['quantity']:<10} {info['price']:<14,.0f} {info['investment']:<14,.0f}")

        # 암호화폐 투자 계획
        if portfolio['cryptos']:
            print("\n💰 암호화폐 투자 계획")
            print("-" * 70)
            print(f"{'종목':<15} {'수량':<15} {'가격':<15} {'투자액':<15}")
            print("-" * 70)

            for ticker, info in portfolio['cryptos'].items():
                print(f"{info['name']:<15} {info['quantity']:<14.8f} {info['price']:<14,.0f} {info['investment']:<14,.0f}")

    def compare_strategies(self, stocks: Dict[str, str], cryptos: Dict[str, str]):
        """모든 전략 비교"""
        print("\n" + "=" * 70)
        print("🎯 투자 전략 비교")
        print("=" * 70)
        print()

        portfolios = {}

        for strategy_name in self.strategies:
            portfolio = self.calculate_portfolio(strategy_name, stocks, cryptos)
            if portfolio:
                portfolios[strategy_name] = portfolio
                self.print_portfolio(portfolio)

        # 통합 비교
        print("\n" + "=" * 70)
        print("📊 전략별 투자 금액 비교")
        print("=" * 70)
        print()

        print(f"{'전략':<20} {'주식':<15} {'암호화폐':<15} {'합계':<15}")
        print("-" * 70)

        for strategy_name, portfolio in portfolios.items():
            print(f"{portfolio['strategy_name']:<20} {portfolio['stock_budget']:<14,.0f} {portfolio['crypto_budget']:<14,.0f} {portfolio['total_budget']:<14,.0f}")

    def calculate_rebalancing(self, current_portfolio: Dict,
                            target_strategy: str) -> Optional[Dict]:
        """
        리밸런싱 필요성 계산

        Args:
            current_portfolio: 현재 포트폴리오
            target_strategy: 목표 전략

        Returns:
            리밸런싱 추천사항
        """
        target_portfolio = self.calculate_portfolio(target_strategy, {}, {})

        if not target_portfolio:
            return None

        print("\n" + "=" * 70)
        print(f"🔄 리밸런싱 분석: {target_portfolio['strategy_name']}")
        print("=" * 70)
        print()
        print("비교 분석:")
        print("-" * 70)

        # 현재 vs 목표
        current_stock_ratio = current_portfolio.get('stock_budget', 0) / current_portfolio.get('total_budget', 1)
        current_crypto_ratio = current_portfolio.get('crypto_budget', 0) / current_portfolio.get('total_budget', 1)

        target_stock_ratio = target_portfolio['stock_budget'] / target_portfolio['total_budget']
        target_crypto_ratio = target_portfolio['crypto_budget'] / target_portfolio['total_budget']

        print(f"현재 주식 비중: {current_stock_ratio*100:.1f}% → 목표: {target_stock_ratio*100:.1f}%")
        print(f"현재 암호화폐 비중: {current_crypto_ratio*100:.1f}% → 목표: {target_crypto_ratio*100:.1f}%")

        if abs(current_stock_ratio - target_stock_ratio) > 0.05:
            action = "증가" if target_stock_ratio > current_stock_ratio else "감소"
            amount = abs(target_stock_ratio - current_stock_ratio) * current_portfolio['total_budget']
            print(f"\n⚠️  주식 비중을 {action}시키세요 ({amount:,.0f} KRW)")

        if abs(current_crypto_ratio - target_crypto_ratio) > 0.05:
            action = "증가" if target_crypto_ratio > current_crypto_ratio else "감소"
            amount = abs(target_crypto_ratio - current_crypto_ratio) * current_portfolio['total_budget']
            print(f"⚠️  암호화폐 비중을 {action}시키세요 ({amount:,.0f} KRW)")

        if abs(current_stock_ratio - target_stock_ratio) <= 0.05 and \
           abs(current_crypto_ratio - target_crypto_ratio) <= 0.05:
            print("\n✓ 현재 포트폴리오가 목표 비중과 유사합니다. 리밸런싱 불필요")


def setup_config() -> TradingConfig:
    """환경변수에서 거래 설정을 로드합니다"""
    required_env_vars = [
        'KIS_APP_KEY', 'KIS_SECRET_KEY', 'KIS_ACCOUNT', 'KIS_HTS_ID',
        'UPBIT_ACCESS_KEY', 'UPBIT_SECRET_KEY'
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
    """메인 함수 - 하이브리드 거래 전략 예제"""

    print("=" * 70)
    print("🚀 Hybrid Trader - 하이브리드 거래 전략 예제")
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

            # 투자 금액
            initial_budget = 10_000_000  # 1000만원

            # 관심 종목
            stocks = {
                "005930": "삼성전자",
                "000660": "SK하이닉스",
                "005380": "현대차"
            }

            cryptos = {
                "KRW-BTC": "비트코인",
                "KRW-ETH": "이더리움",
                "KRW-XRP": "리플"
            }

            # 전략 엔진 생성
            strategy = HybridTradingStrategy(engine, initial_budget)

            # 시장 데이터 수집
            if strategy.fetch_prices(stocks, cryptos):
                # 전략 비교
                strategy.compare_strategies(stocks, cryptos)

                # 리밸런싱 분석
                current_portfolio = {
                    'stock_budget': initial_budget * 0.5,
                    'crypto_budget': initial_budget * 0.5,
                    'total_budget': initial_budget
                }

                strategy.calculate_rebalancing(current_portfolio, "balanced")
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
