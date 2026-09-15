#!/usr/bin/env python
"""
주식 거래 예제 (Stock Trading Example)

이 예제는 한국투자증권 API를 통해 주식 현재가를 조회하고,
여러 종목을 비교 분석하는 방법을 보여줍니다.

주요 기능:
- 단일 주식 현재가 조회
- 여러 주식 동시 조회
- 주식 현재가 통계 분석
- 에러 처리
"""

import os
import logging
import sys
from typing import Dict, Optional, List
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class StockPriceAnalyzer:
    """주식 현재가 분석 도구"""

    def __init__(self, engine: HybridTradingEngine):
        """
        분석기 초기화

        Args:
            engine: HybridTradingEngine 인스턴스
        """
        self.engine = engine
        self.stock_prices: Dict[str, Optional[float]] = {}
        self.statistics = {
            'total': 0,
            'success': 0,
            'failed': 0
        }

    def get_stock_price_safe(self, ticker: str, name: str = "") -> Optional[float]:
        """
        안전한 주식 현재가 조회

        Args:
            ticker: 주식 코드 (예: "005930")
            name: 주식 이름 (표시용)

        Returns:
            현재가 또는 None
        """
        try:
            # 입력 검증
            if not ticker or not isinstance(ticker, str):
                logger.warning(f"Invalid ticker format: {ticker}")
                self.statistics['failed'] += 1
                return None

            logger.info(f"조회 중: {name} ({ticker})")

            # API 호출
            price = self.engine.get_stock_price(ticker)

            if price is not None:
                self.stock_prices[ticker] = price
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

    def get_multiple_stocks(self, stocks: Dict[str, str]) -> Dict[str, Optional[float]]:
        """
        여러 주식의 현재가를 일괄 조회

        Args:
            stocks: {"코드": "이름"} 형식의 딕셔너리

        Returns:
            {"코드": 현재가} 형식의 딕셔너리
        """
        print("\n" + "=" * 70)
        print("📈 주식 현재가 조회")
        print("=" * 70)

        results = {}

        for ticker, name in stocks.items():
            price = self.get_stock_price_safe(ticker, name)
            if price is not None:
                results[ticker] = price

        return results

    def calculate_statistics(self) -> Dict[str, float]:
        """
        조회된 주식들의 통계 계산

        Returns:
            통계 정보 딕셔너리
        """
        if not self.stock_prices:
            logger.warning("조회된 주식이 없습니다")
            return {}

        prices = list(self.stock_prices.values())

        return {
            'count': len(prices),
            'max': max(prices),
            'min': min(prices),
            'avg': sum(prices) / len(prices),
            'total': sum(prices)
        }

    def print_statistics(self):
        """통계 정보 출력"""
        stats = self.calculate_statistics()

        if not stats:
            return

        print("\n" + "=" * 70)
        print("📊 조회 결과 통계")
        print("=" * 70)
        print(f"조회된 종목 수: {self.statistics['success']}/{self.statistics['total']}")
        print(f"조회 성공: {self.statistics['success']}")
        print(f"조회 실패: {self.statistics['failed']}")
        print()
        print(f"최고가: {stats['max']:,.0f} KRW")
        print(f"최저가: {stats['min']:,.0f} KRW")
        print(f"평균가: {stats['avg']:,.0f} KRW")
        print(f"합계: {stats['total']:,.0f} KRW")

    def get_price_comparison(self, base_ticker: str, compare_tickers: List[str]) -> Dict:
        """
        특정 주식과 다른 주식들의 가격 비교

        Args:
            base_ticker: 기준 주식 코드
            compare_tickers: 비교할 주식 코드 리스트

        Returns:
            비교 결과
        """
        base_price = self.stock_prices.get(base_ticker)

        if base_price is None:
            logger.warning(f"기준 주식 ({base_ticker})의 가격 정보 없음")
            return {}

        comparison = {}

        for ticker in compare_tickers:
            compare_price = self.stock_prices.get(ticker)
            if compare_price is not None:
                ratio = compare_price / base_price
                comparison[ticker] = {
                    'price': compare_price,
                    'ratio': ratio
                }

        return comparison


def setup_config() -> TradingConfig:
    """
    환경변수에서 거래 설정을 로드합니다

    Returns:
        TradingConfig 인스턴스

    Raises:
        SystemExit: 필수 환경변수가 설정되지 않았을 때
    """

    # 필수 환경변수 확인
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
        print("예: export KIS_APP_KEY='your_key'")
        sys.exit(1)

    # 설정 생성
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY"),
        secret_key=os.getenv("KIS_SECRET_KEY"),
        account_number=os.getenv("KIS_ACCOUNT"),
        hts_id=os.getenv("KIS_HTS_ID"),
        is_demo=True  # 항상 테스트 모드로 시작
    )

    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY"),
        secret_key=os.getenv("UPBIT_SECRET_KEY")
    )

    return TradingConfig(kis_config=kis_config, upbit_config=upbit_config)


def main():
    """메인 함수 - 주식 거래 예제"""

    print("=" * 70)
    print("🚀 Hybrid Trader - 주식 거래 예제")
    print("=" * 70)
    print()

    # 설정 로드
    try:
        config = setup_config()
        logger.info("✓ 설정을 성공적으로 로드했습니다")
    except SystemExit:
        return

    # 관심 주식
    stocks = {
        "005930": "삼성전자",
        "000660": "SK하이닉스",
        "005380": "현대차",
        "051910": "LG화학",
        "035420": "NAVER",
        "035720": "카카오",
        "068270": "셀트리온",
        "207940": "삼성바이오로직스"
    }

    try:
        # 엔진 초기화 및 사용
        with HybridTradingEngine(config) as engine:
            logger.info("✓ Hybrid Trading Engine이 초기화되었습니다")

            # 분석기 생성
            analyzer = StockPriceAnalyzer(engine)

            # 여러 주식 조회
            results = analyzer.get_multiple_stocks(stocks)

            # 통계 출력
            analyzer.print_statistics()

            # 가격 비교
            if "005930" in results and len(results) > 1:
                print("\n" + "=" * 70)
                print("📈 삼성전자와의 가격 비교 (상대 비율)")
                print("=" * 70)

                samsung_price = results["005930"]
                print(f"\n기준: 삼성전자 ({samsung_price:,.0f} KRW)")
                print("-" * 70)

                for ticker, price in results.items():
                    if ticker != "005930":
                        ratio = price / samsung_price
                        comparison_status = "높음" if ratio > 1 else "낮음"
                        name = stocks[ticker]
                        print(f"{name:15s}: {price:>12,.0f} KRW (기준의 {ratio:.2f}배, {comparison_status})")

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
