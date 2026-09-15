"""
Basic example of using Hybrid Trader

하이브리드 트레이더 기본 사용 예제
"""

from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig


def main():
    # ============================================
    # 1. API 설정 구성
    # ============================================

    kis_config = KISConfig(
        app_key="YOUR_KIS_APP_KEY",           # 한국투자증권 App Key
        secret_key="YOUR_KIS_SECRET_KEY",     # 한국투자증권 Secret Key
        account_number="1234-5678",           # 한국투자증권 계좌번호
        hts_id="YOUR_HTS_ID",                # 한국투자증권 HTS ID
        is_demo=True                          # 데모/테스트 모드 활성화
    )

    upbit_config = UpbitConfig(
        access_key="YOUR_UPBIT_ACCESS_KEY",  # 업비트 Access Key
        secret_key="YOUR_UPBIT_SECRET_KEY"   # 업비트 Secret Key
    )

    # ============================================
    # 2. 트레이딩 엔진 초기화
    # ============================================

    config = TradingConfig(
        kis_config=kis_config,
        upbit_config=upbit_config,
        timeout=10,          # API 타임아웃 (초)
        retry_count=3        # 재시도 횟수
    )

    # ============================================
    # 3. Context Manager를 사용한 안전한 사용
    # (권장: 자동으로 세션이 정리됨)
    # ============================================

    with HybridTradingEngine(config) as engine:
        print("=" * 50)
        print("Hybrid Trader - 기본 예제")
        print("=" * 50)

        # 주식 현재가 조회
        print("\n📈 주식 시세 조회")
        print("-" * 50)

        stock_tickers = {
            "005930": "삼성전자",
            "000660": "SK하이닉스",
            "035420": "NAVER",
        }

        for ticker, name in stock_tickers.items():
            try:
                price = engine.get_stock_price(ticker)
                if price:
                    print(f"  {name} ({ticker}): {price:,.0f} KRW")
                else:
                    print(f"  {name} ({ticker}): 조회 실패")
            except Exception as e:
                print(f"  {name} ({ticker}): 오류 - {e}")

        # 암호화폐 현재가 조회
        print("\n💰 암호화폐 시세 조회")
        print("-" * 50)

        crypto_tickers = {
            "KRW-BTC": "비트코인",
            "KRW-ETH": "이더리움",
            "KRW-XRP": "리플",
        }

        for ticker, name in crypto_tickers.items():
            try:
                price = engine.get_coin_price(ticker)
                if price:
                    print(f"  {name} ({ticker}): {price:,.0f} KRW")
                else:
                    print(f"  {name} ({ticker}): 조회 실패")
            except Exception as e:
                print(f"  {name} ({ticker}): 오류 - {e}")

        print("\n" + "=" * 50)
        print("예제 완료!")
        print("=" * 50)


def advanced_example():
    """
    고급 사용 예제: 환경변수로 API 키 관리
    """
    import os

    # 환경변수에서 API 키를 읽어옵니다
    # 보안을 위해 코드에 키를 직접 하드코딩하지 마세요!

    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", ""),
        secret_key=os.getenv("KIS_SECRET_KEY", ""),
        account_number=os.getenv("KIS_ACCOUNT", ""),
        hts_id=os.getenv("KIS_HTS_ID", "")
    )

    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", ""),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "")
    )

    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    engine = HybridTradingEngine(config)

    # 엔진 사용
    # ...

    engine.close()


if __name__ == "__main__":
    import sys
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(name)s: %(message)s'
    )

    print("\n" + "=" * 60)
    print("Hybrid Trader - Basic Example")
    print("=" * 60 + "\n")

    print("Select an example to run:")
    print("  1. Basic example (basic)")
    print("  2. Advanced example with env vars")
    print("  3. Exit")

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice == "1":
        print("\n[!] API key required. Set these values before running:")
        print("    kis_config.app_key = 'YOUR_KIS_APP_KEY'")
        print("    kis_config.secret_key = 'YOUR_KIS_SECRET_KEY'")
        print("    kis_config.account_number = 'YOUR_ACCOUNT'")
        print("    kis_config.hts_id = 'YOUR_HTS_ID'")
        print("    upbit_config.access_key = 'YOUR_UPBIT_ACCESS_KEY'")
        print("    upbit_config.secret_key = 'YOUR_UPBIT_SECRET_KEY'\n")

        try:
            main()
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print("\nPlease check your API keys and try again.")

    elif choice == "2":
        print("\n[!] Environment variable example")
        print("    export KIS_APP_KEY='your_key_here'")
        print("    export KIS_SECRET_KEY='your_secret_here'")
        print("    export KIS_ACCOUNT='your_account'")
        print("    export KIS_HTS_ID='your_hts_id'")
        print("    export UPBIT_ACCESS_KEY='your_key_here'")
        print("    export UPBIT_SECRET_KEY='your_secret_here'\n")

        try:
            advanced_example()
            print("\n[SUCCESS] Advanced example completed!")
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print("\nPlease check your environment variables and try again.")

    elif choice == "3":
        print("\n[INFO] Exiting...")
        sys.exit(0)

    else:
        print("\n[ERROR] Invalid choice.")
        sys.exit(1)
