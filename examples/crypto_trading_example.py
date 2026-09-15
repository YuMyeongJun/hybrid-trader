#!/usr/bin/env python
"""
암호화폐 거래 예제 (Crypto Trading Example)

이 예제는 업비트 API를 통해 암호화폐 현재가를 조회하고,
여러 코인을 비교 분석하는 방법을 보여줍니다.

주요 기능:
- 암호화폐 현재가 조회
- 여러 코인 동시 조회
- 투자 규모 계산
- 코인별 통계 분석
- 에러 처리
"""

import os
import logging
import sys
from typing import Dict, Optional
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class CryptocurrencyAnalyzer:
    """암호화폐 현재가 분석 도구"""

    def __init__(self, engine: HybridTradingEngine):
        """
        분석기 초기화

        Args:
            engine: HybridTradingEngine 인스턴스
        """
        self.engine = engine
        self.crypto_prices: Dict[str, Optional[float]] = {}
        self.statistics = {
            'total': 0,
            'success': 0,
            'failed': 0
        }

    def get_crypto_price_safe(self, ticker: str, name: str = "") -> Optional[float]:
        """
        안전한 암호화폐 현재가 조회

        Args:
            ticker: 암호화폐 코드 (예: "KRW-BTC")
            name: 암호화폐 이름 (표시용)

        Returns:
            현재가 또는 None
        """
        try:
            # 입력 검증
            if not ticker or not isinstance(ticker, str):
                logger.warning(f"Invalid ticker format: {ticker}")
                self.statistics['failed'] += 1
                return None

            if not ticker.startswith("KRW-"):
                logger.warning(f"Ticker must start with 'KRW-': {ticker}")
                self.statistics['failed'] += 1
                return None

            logger.info(f"조회 중: {name} ({ticker})")

            # API 호출
            price = self.engine.get_coin_price(ticker)

            if price is not None:
                self.crypto_prices[ticker] = price
                self.statistics['success'] += 1
                logger.info(f"✓ {name} ({ticker}): {price:,.0f} KRW")
                return price
            else:
                logger.warning(f"✗ {name} ({ticker}): 가격 조회 실패")
                self.statistics['failed'] += 1
                return None

        except ValueError as e:
            logger.error(f"입력 오류 - {name} ({ticker}): {e}")
            self.statistics['failed'] += 1
            return None

        except Exception as e:
            logger.error(f"API 오류 - {name} ({ticker}): {e}")
            self.statistics['failed'] += 1
            return None
        finally:
            self.statistics['total'] += 1

    def get_multiple_cryptos(self, cryptos: Dict[str, str]) -> Dict[str, Optional[float]]:
        """
        여러 암호화폐의 현재가를 일괄 조회

        Args:
            cryptos: {"코드": "이름"} 형식의 딕셔너리

        Returns:
            {"코드": 현재가} 형식의 딕셔너리
        """
        print("\n" + "=" * 70)
        print("💰 암호화폐 현재가 조회")
        print("=" * 70)

        results = {}

        for ticker, name in cryptos.items():
            price = self.get_crypto_price_safe(ticker, name)
            if price is not None:
                results[ticker] = price

        return results

    def calculate_investment(self, investment_amount: float) -> Dict[str, Dict]:
        """
        투자 금액으로 구매 가능한 코인 수량 계산

        Args:
            investment_amount: 투자 금액 (KRW)

        Returns:
            구매 가능 수량 정보
        """
        investments = {}

        for ticker, price in self.crypto_prices.items():
            if price is not None and price > 0:
                quantity = investment_amount / price
                investments[ticker] = {
                    'price': price,
                    'quantity': quantity,
                    'investment': investment_amount
                }

        return investments

    def print_investment_plan(self, investment_amount: float):
        """
        투자 계획 출력

        Args:
            investment_amount: 투자 금액 (KRW)
        """
        print("\n" + "=" * 70)
        print(f"💵 투자 계획 ({investment_amount:,.0f} KRW)")
        print("=" * 70)

        investments = self.calculate_investment(investment_amount)

        if not investments:
            logger.warning("계산할 암호화폐가 없습니다")
            return

        print(f"\n{'암호화폐':<15} {'현재가':<15} {'구매량':<15} {'투자액':<15}")
        print("-" * 70)

        for ticker, info in investments.items():
            # 티커에서 이름 추출
            name = ticker.replace("KRW-", "")

            print(f"{name:<15} {info['price']:>12,.0f} KRW {info['quantity']:>12.8f}개 {info['investment']:>12,.0f} KRW")

    def print_statistics(self):
        """통계 정보 출력"""
        if not self.crypto_prices:
            logger.warning("조회된 암호화폐가 없습니다")
            return

        prices = list(self.crypto_prices.values())

        print("\n" + "=" * 70)
        print("📊 조회 결과 통계")
        print("=" * 70)
        print(f"조회된 종목 수: {self.statistics['success']}/{self.statistics['total']}")
        print(f"조회 성공: {self.statistics['success']}")
        print(f"조회 실패: {self.statistics['failed']}")
        print()
        print(f"최고가: {max(prices):,.0f} KRW")
        print(f"최저가: {min(prices):,.0f} KRW")
        print(f"평균가: {sum(prices) / len(prices):,.0f} KRW")
        print(f"합계: {sum(prices):,.0f} KRW")

    def get_market_cap_comparison(self, investment_amounts: Dict[str, float]):
        """
        여러 투자 금액에 따른 시장 시가총액 비교

        Args:
            investment_amounts: {"이름": 금액} 형식의 딕셔너리
        """
        print("\n" + "=" * 70)
        print("📈 다양한 투자 규모 비교")
        print("=" * 70)

        for scenario_name, amount in investment_amounts.items():
            print(f"\n시나리오: {scenario_name} ({amount:,.0f} KRW)")
            print("-" * 70)

            investments = self.calculate_investment(amount)

            for ticker, info in investments.items():
                name = ticker.replace("KRW-", "")
                print(f"  {name:<10}: {info['quantity']:>12.8f}개")


def setup_config() -> TradingConfig:
    """
    환경변수에서 거래 설정을 로드합니다

    Returns:
        TradingConfig 인스턴스

    Raises:
        SystemExit: 필수 환경변수가 설정되지 않았을 때
    """

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
        print("\n환경변수를 설정한 후 다시 실행하세요.")
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
    """메인 함수 - 암호화폐 거래 예제"""

    print("=" * 70)
    print("🚀 Hybrid Trader - 암호화폐 거래 예제")
    print("=" * 70)
    print()

    # 설정 로드
    try:
        config = setup_config()
        logger.info("✓ 설정을 성공적으로 로드했습니다")
    except SystemExit:
        return

    # 관심 암호화폐
    cryptos = {
        "KRW-BTC": "비트코인",
        "KRW-ETH": "이더리움",
        "KRW-XRP": "리플",
        "KRW-DOGE": "도지코인",
        "KRW-LTC": "라이트코인",
        "KRW-BCH": "비트캐시",
        "KRW-EOS": "이오스",
        "KRW-TRX": "트론",
        "KRW-ADA": "에이다",
        "KRW-LINK": "체인링크"
    }

    try:
        # 엔진 초기화 및 사용
        with HybridTradingEngine(config) as engine:
            logger.info("✓ Hybrid Trading Engine이 초기화되었습니다")

            # 분석기 생성
            analyzer = CryptocurrencyAnalyzer(engine)

            # 여러 암호화폐 조회
            results = analyzer.get_multiple_cryptos(cryptos)

            # 통계 출력
            analyzer.print_statistics()

            # 투자 계획 출력
            investment_amounts = {
                "소액 투자": 1_000_000,       # 100만원
                "중액 투자": 5_000_000,       # 500만원
                "대액 투자": 10_000_000       # 1000만원
            }

            for scenario, amount in investment_amounts.items():
                analyzer.print_investment_plan(amount)

            # 시장 시가총액 비교
            print("\n" + "=" * 70)
            print("💰 투자 규모별 구매 수량 비교")
            print("=" * 70)

            analyzer.get_market_cap_comparison(investment_amounts)

            print("\n" + "=" * 70)
            print("예제 완료!")
            print("=" * 70)

    except ValueError as e:
        logger.error(f"설정 오류: {e}")
        print("\n설정을 다시 확인하세요.")
        sys.exit(1)

    except Exception as e:
        logger.error(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
