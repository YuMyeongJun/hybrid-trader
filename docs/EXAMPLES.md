# 사용 예제 (Examples)

Hybrid Trader의 실제 사용 사례 10개 이상을 포함합니다.

## 목차

- [기본 예제](#기본-예제)
- [예제 1: 단일 주식 현재가 조회](#예제-1-단일-주식-현재가-조회)
- [예제 2: 여러 주식 동시 조회](#예제-2-여러-주식-동시-조회)
- [예제 3: 암호화폐 가격 조회](#예제-3-암호화폐-가격-조회)
- [예제 4: 주식과 암호화폐 비교](#예제-4-주식과-암호화폐-비교)
- [예제 5: 환경변수를 사용한 안전한 API 키 관리](#예제-5-환경변수를-사용한-안전한-api-키-관리)
- [예제 6: 에러 처리가 포함된 데이터 조회](#예제-6-에러-처리가-포함된-데이터-조회)
- [예제 7: 정기적인 가격 모니터링](#예제-7-정기적인-가격-모니터링)
- [예제 8: 가격 변동 알림](#예제-8-가격-변동-알림)
- [예제 9: 포트폴리오 분석](#예제-9-포트폴리오-분석)
- [예제 10: 하이브리드 거래 전략](#예제-10-하이브리드-거래-전략)
- [예제 11: 리스트에서 CSV로 내보내기](#예제-11-리스트에서-csv로-내보내기)
- [예제 12: 실시간 대시보드 구현](#예제-12-실시간-대시보드-구현)

---

## 기본 예제

가장 간단한 사용법:

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 1. API 설정
kis_config = KISConfig(
    app_key="YOUR_KIS_APP_KEY",
    secret_key="YOUR_KIS_SECRET_KEY",
    account_number="1234-5678",
    hts_id="YOUR_HTS_ID",
    is_demo=True
)

upbit_config = UpbitConfig(
    access_key="YOUR_UPBIT_ACCESS_KEY",
    secret_key="YOUR_UPBIT_SECRET_KEY"
)

# 2. 엔진 초기화
config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)

# 3. Context Manager로 사용 (권장)
with HybridTradingEngine(config) as engine:
    # 주식 조회
    samsung_price = engine.get_stock_price("005930")
    print(f"삼성전자: {samsung_price:,.0f} KRW")
    
    # 암호화폐 조회
    bitcoin_price = engine.get_coin_price("KRW-BTC")
    print(f"비트코인: {bitcoin_price:,.0f} KRW")
```

---

## 예제 1: 단일 주식 현재가 조회

특정 주식의 현재가를 조회하는 가장 기본적인 예제입니다.

```python
#!/usr/bin/env python
"""예제 1: 단일 주식 현재가 조회"""

import logging
import os
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s'
)

def main():
    """주식 한 종목의 현재가 조회"""
    
    # 환경변수에서 API 키 로드
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True  # 테스트 모드
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    # 엔진 사용
    with HybridTradingEngine(config) as engine:
        print("=" * 50)
        print("예제 1: 단일 주식 현재가 조회")
        print("=" * 50)
        
        # 삼성전자 현재가 조회
        ticker = "005930"
        try:
            price = engine.get_stock_price(ticker)
            if price:
                print(f"\n✓ 삼성전자 ({ticker})")
                print(f"  현재가: {price:,.0f} KRW")
            else:
                print(f"\n✗ 삼성전자 ({ticker})")
                print(f"  가격 조회 실패")
        except Exception as e:
            print(f"\n✗ 오류 발생: {e}")

if __name__ == "__main__":
    main()
```

---

## 예제 2: 여러 주식 동시 조회

여러 주식의 현재가를 한 번에 조회합니다.

```python
#!/usr/bin/env python
"""예제 2: 여러 주식 동시 조회"""

import os
import logging
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

logging.basicConfig(level=logging.INFO)

def main():
    """여러 주식 종목의 현재가를 한 번에 조회"""
    
    # 설정
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    # 주식 종목 정보
    stocks = {
        "005930": "삼성전자",
        "000660": "SK하이닉스",
        "005380": "현대차",
        "051910": "LG화학",
        "035420": "NAVER",
        "035720": "카카오"
    }
    
    with HybridTradingEngine(config) as engine:
        print("=" * 60)
        print("예제 2: 여러 주식 동시 조회")
        print("=" * 60)
        print()
        
        # 현재가 조회 및 저장
        stock_prices = {}
        
        for ticker, name in stocks.items():
            try:
                price = engine.get_stock_price(ticker)
                if price:
                    stock_prices[ticker] = price
                    print(f"✓ {name:10s} ({ticker}): {price:>12,.0f} KRW")
                else:
                    print(f"✗ {name:10s} ({ticker}): 조회 실패")
            except Exception as e:
                print(f"✗ {name:10s} ({ticker}): 오류 - {e}")
        
        # 통계
        print()
        print("=" * 60)
        print("조회 결과 통계")
        print("=" * 60)
        print(f"조회된 종목 수: {len(stock_prices)}/{len(stocks)}")
        
        if stock_prices:
            prices = list(stock_prices.values())
            print(f"최고가: {max(prices):,.0f} KRW")
            print(f"최저가: {min(prices):,.0f} KRW")
            print(f"평균가: {sum(prices) / len(prices):,.0f} KRW")

if __name__ == "__main__":
    main()
```

---

## 예제 3: 암호화폐 가격 조회

비트코인, 이더리움 등 암호화폐 가격을 조회합니다.

```python
#!/usr/bin/env python
"""예제 3: 암호화폐 가격 조회"""

import os
import logging
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

logging.basicConfig(level=logging.INFO)

def main():
    """암호화폐의 현재가를 조회"""
    
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    # 암호화폐 목록
    cryptos = {
        "KRW-BTC": "비트코인",
        "KRW-ETH": "이더리움",
        "KRW-XRP": "리플",
        "KRW-DOGE": "도지코인",
        "KRW-LTC": "라이트코인",
        "KRW-BCH": "비트캐시",
        "KRW-EOS": "이오스",
        "KRW-TRX": "트론"
    }
    
    with HybridTradingEngine(config) as engine:
        print("=" * 60)
        print("예제 3: 암호화폐 가격 조회")
        print("=" * 60)
        print()
        
        # 암호화폐 가격 조회
        crypto_prices = {}
        
        for ticker, name in cryptos.items():
            try:
                price = engine.get_coin_price(ticker)
                if price:
                    crypto_prices[ticker] = price
                    print(f"✓ {name:12s} ({ticker}): {price:>15,.0f} KRW")
                else:
                    print(f"✗ {name:12s} ({ticker}): 조회 실패")
            except Exception as e:
                print(f"✗ {name:12s} ({ticker}): 오류 - {e}")
        
        # 가치 비교 (1000만원 기준)
        print()
        print("=" * 60)
        print("1000만원 투자 시 각 암호화폐 개수")
        print("=" * 60)
        
        investment = 10_000_000  # 1000만원
        
        for ticker, name in cryptos.items():
            if ticker in crypto_prices:
                price = crypto_prices[ticker]
                amount = investment / price
                print(f"{name:12s}: {amount:>10,.4f} 개")

if __name__ == "__main__":
    main()
```

---

## 예제 4: 주식과 암호화폐 비교

주식과 암호화폐 가격을 함께 표시하고 비교합니다.

```python
#!/usr/bin/env python
"""예제 4: 주식과 암호화폐 비교"""

import os
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

def main():
    """주식과 암호화폐의 가격을 함께 조회하고 비교"""
    
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    # 관심 자산
    assets = {
        "stocks": {
            "005930": "삼성전자",
            "000660": "SK하이닉스"
        },
        "cryptos": {
            "KRW-BTC": "비트코인",
            "KRW-ETH": "이더리움"
        }
    }
    
    with HybridTradingEngine(config) as engine:
        print("=" * 70)
        print("예제 4: 주식과 암호화폐 비교")
        print("=" * 70)
        
        # 주식 조회
        print("\n📈 주식 (주식 시장)")
        print("-" * 70)
        
        stock_total = 0
        stock_count = 0
        
        for ticker, name in assets["stocks"].items():
            try:
                price = engine.get_stock_price(ticker)
                if price:
                    print(f"  {name:15s} ({ticker}): {price:>12,.0f} KRW")
                    stock_total += price
                    stock_count += 1
                else:
                    print(f"  {name:15s} ({ticker}): 조회 실패")
            except Exception as e:
                print(f"  {name:15s} ({ticker}): 오류 - {e}")
        
        if stock_count > 0:
            print(f"\n  평균 주식가: {stock_total / stock_count:,.0f} KRW")
        
        # 암호화폐 조회
        print("\n💰 암호화폐 (암호화폐 시장)")
        print("-" * 70)
        
        crypto_total = 0
        crypto_count = 0
        
        for ticker, name in assets["cryptos"].items():
            try:
                price = engine.get_coin_price(ticker)
                if price:
                    print(f"  {name:15s} ({ticker}): {price:>12,.0f} KRW")
                    crypto_total += price
                    crypto_count += 1
                else:
                    print(f"  {name:15s} ({ticker}): 조회 실패")
            except Exception as e:
                print(f"  {name:15s} ({ticker}): 오류 - {e}")
        
        if crypto_count > 0:
            print(f"\n  평균 암호화폐 가격: {crypto_total / crypto_count:,.0f} KRW")
        
        # 비교
        print("\n" + "=" * 70)
        print("비교 분석")
        print("=" * 70)
        
        if stock_count > 0 and crypto_count > 0:
            avg_stock = stock_total / stock_count
            avg_crypto = crypto_total / crypto_count
            
            print(f"평균 주식가: {avg_stock:>12,.0f} KRW")
            print(f"평균 암호화폐: {avg_crypto:>12,.0f} KRW")
            
            if avg_crypto > avg_stock:
                ratio = avg_crypto / avg_stock
                print(f"\n암호화폐가 주식보다 {ratio:.2f}배 비쌉니다")
            else:
                ratio = avg_stock / avg_crypto
                print(f"\n주식이 암호화폐보다 {ratio:.2f}배 비쌉니다")

if __name__ == "__main__":
    main()
```

---

## 예제 5: 환경변수를 사용한 안전한 API 키 관리

절대 코드에 API 키를 하드코딩하지 마세요. 환경변수를 사용하세요.

```python
#!/usr/bin/env python
"""예제 5: 환경변수를 사용한 안전한 API 키 관리"""

import os
import sys
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

def get_api_config():
    """환경변수에서 API 설정 로드
    
    필수 환경변수:
    - KIS_APP_KEY: 한국투자증권 App Key
    - KIS_SECRET_KEY: 한국투자증권 Secret Key
    - KIS_ACCOUNT: 한국투자증권 계좌번호
    - KIS_HTS_ID: 한국투자증권 HTS ID
    - UPBIT_ACCESS_KEY: 업비트 Access Key
    - UPBIT_SECRET_KEY: 업비트 Secret Key
    """
    
    required_keys = {
        "KIS_APP_KEY": "한국투자증권 App Key",
        "KIS_SECRET_KEY": "한국투자증권 Secret Key",
        "KIS_ACCOUNT": "한국투자증권 계좌번호",
        "KIS_HTS_ID": "한국투자증권 HTS ID",
        "UPBIT_ACCESS_KEY": "업비트 Access Key",
        "UPBIT_SECRET_KEY": "업비트 Secret Key"
    }
    
    # 환경변수 확인
    missing_keys = []
    for key, description in required_keys.items():
        if not os.getenv(key):
            missing_keys.append(f"{key} ({description})")
    
    if missing_keys:
        print("❌ 필수 환경변수가 설정되지 않았습니다:")
        for key in missing_keys:
            print(f"  - {key}")
        print("\n환경변수를 설정한 후 다시 실행하세요:")
        print("  export KIS_APP_KEY='your_key'")
        print("  export KIS_SECRET_KEY='your_secret'")
        print("  export KIS_ACCOUNT='1234-5678'")
        print("  export KIS_HTS_ID='your_hts_id'")
        print("  export UPBIT_ACCESS_KEY='your_access_key'")
        print("  export UPBIT_SECRET_KEY='your_secret_key'")
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
    """안전한 API 키 관리"""
    
    print("=" * 60)
    print("예제 5: 환경변수를 사용한 안전한 API 키 관리")
    print("=" * 60)
    print()
    
    # API 설정 로드
    config = get_api_config()
    
    print("✓ 환경변수에서 API 설정을 성공적으로 로드했습니다")
    print()
    
    # 엔진 사용
    with HybridTradingEngine(config) as engine:
        print("엔진이 초기화되었습니다")
        
        # 주식 조회
        try:
            stock_price = engine.get_stock_price("005930")
            print(f"삼성전자 현재가: {stock_price:,.0f} KRW" if stock_price else "조회 실패")
        except Exception as e:
            print(f"주식 조회 실패: {e}")
        
        # 암호화폐 조회
        try:
            crypto_price = engine.get_coin_price("KRW-BTC")
            print(f"비트코인 현재가: {crypto_price:,.0f} KRW" if crypto_price else "조회 실패")
        except Exception as e:
            print(f"암호화폐 조회 실패: {e}")

if __name__ == "__main__":
    main()
```

---

## 예제 6: 에러 처리가 포함된 데이터 조회

실무에서 필요한 상세한 에러 처리를 포함합니다.

```python
#!/usr/bin/env python
"""예제 6: 에러 처리가 포함된 데이터 조회"""

import os
import logging
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

class PriceChecker:
    """에러 처리가 포함된 가격 조회 도우미"""
    
    def __init__(self, config):
        self.engine = HybridTradingEngine(config)
        self.results = {
            "success": 0,
            "failed": 0,
            "errors": []
        }
    
    def get_stock_price_safe(self, ticker, name=""):
        """에러 처리가 포함된 주식 가격 조회"""
        
        try:
            # 입력 검증
            if not ticker or not isinstance(ticker, str):
                raise ValueError(f"Invalid ticker: {ticker}")
            
            # API 호출
            price = self.engine.get_stock_price(ticker)
            
            if price is None:
                self.results["failed"] += 1
                error_msg = f"{name} ({ticker}): 가격 정보를 찾을 수 없습니다"
                self.results["errors"].append(error_msg)
                return None
            
            self.results["success"] += 1
            return price
        
        except ValueError as e:
            self.results["failed"] += 1
            error_msg = f"{name} ({ticker}): 입력 오류 - {e}"
            self.results["errors"].append(error_msg)
            return None
        
        except Exception as e:
            self.results["failed"] += 1
            error_msg = f"{name} ({ticker}): API 오류 - {e}"
            self.results["errors"].append(error_msg)
            return None
    
    def get_coin_price_safe(self, ticker, name=""):
        """에러 처리가 포함된 암호화폐 가격 조회"""
        
        try:
            if not ticker or not isinstance(ticker, str):
                raise ValueError(f"Invalid ticker: {ticker}")
            
            price = self.engine.get_coin_price(ticker)
            
            if price is None:
                self.results["failed"] += 1
                error_msg = f"{name} ({ticker}): 가격 정보를 찾을 수 없습니다"
                self.results["errors"].append(error_msg)
                return None
            
            self.results["success"] += 1
            return price
        
        except ValueError as e:
            self.results["failed"] += 1
            error_msg = f"{name} ({ticker}): 입력 오류 - {e}"
            self.results["errors"].append(error_msg)
            return None
        
        except Exception as e:
            self.results["failed"] += 1
            error_msg = f"{name} ({ticker}): API 오류 - {e}"
            self.results["errors"].append(error_msg)
            return None
    
    def print_results(self):
        """결과 출력"""
        print("\n" + "=" * 60)
        print("결과 요약")
        print("=" * 60)
        print(f"성공: {self.results['success']}")
        print(f"실패: {self.results['failed']}")
        
        if self.results["errors"]:
            print("\n오류 목록:")
            for error in self.results["errors"]:
                print(f"  ✗ {error}")
    
    def close(self):
        """세션 정리"""
        self.engine.close()

def main():
    """에러 처리가 포함된 데이터 조회"""
    
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    print("=" * 60)
    print("예제 6: 에러 처리가 포함된 데이터 조회")
    print("=" * 60)
    print()
    
    checker = PriceChecker(config)
    
    try:
        # 주식 조회
        print("📈 주식 조회")
        print("-" * 60)
        
        stocks = {
            "005930": "삼성전자",
            "000660": "SK하이닉스",
            "999999": "존재하지않음",  # 오류 테스트
            "": "빈코드"  # 오류 테스트
        }
        
        for ticker, name in stocks.items():
            price = checker.get_stock_price_safe(ticker, name)
            if price:
                print(f"✓ {name}: {price:,.0f} KRW")
            else:
                print(f"✗ {name}: 조회 실패")
        
        # 암호화폐 조회
        print("\n💰 암호화폐 조회")
        print("-" * 60)
        
        cryptos = {
            "KRW-BTC": "비트코인",
            "KRW-ETH": "이더리움",
            "KRW-INVALID": "잘못된코드"  # 오류 테스트
        }
        
        for ticker, name in cryptos.items():
            price = checker.get_coin_price_safe(ticker, name)
            if price:
                print(f"✓ {name}: {price:,.0f} KRW")
            else:
                print(f"✗ {name}: 조회 실패")
        
        # 결과 출력
        checker.print_results()
    
    finally:
        checker.close()

if __name__ == "__main__":
    main()
```

---

## 예제 7: 정기적인 가격 모니터링

주식과 암호화폐 가격을 정기적으로 모니터링합니다.

```python
#!/usr/bin/env python
"""예제 7: 정기적인 가격 모니터링"""

import os
import time
from datetime import datetime
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

def format_time():
    """현재 시간을 포맷팅합니다"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """10초 간격으로 5회 가격을 모니터링"""
    
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    # 모니터링할 자산
    assets = {
        "stocks": {"005930": "삼성전자"},
        "cryptos": {"KRW-BTC": "비트코인"}
    }
    
    print("=" * 60)
    print("예제 7: 정기적인 가격 모니터링")
    print("=" * 60)
    print()
    
    with HybridTradingEngine(config) as engine:
        # 5회 반복
        for iteration in range(1, 6):
            print(f"[반복 {iteration}/5] {format_time()}")
            print("-" * 60)
            
            # 주식 조회
            for ticker, name in assets["stocks"].items():
                try:
                    price = engine.get_stock_price(ticker)
                    if price:
                        print(f"  {name}: {price:>12,.0f} KRW")
                except Exception as e:
                    print(f"  {name}: 오류 - {e}")
            
            # 암호화폐 조회
            for ticker, name in assets["cryptos"].items():
                try:
                    price = engine.get_coin_price(ticker)
                    if price:
                        print(f"  {name}: {price:>12,.0f} KRW")
                except Exception as e:
                    print(f"  {name}: 오류 - {e}")
            
            # 마지막이 아니면 대기
            if iteration < 5:
                print("\n10초 대기 중...")
                time.sleep(10)
                print()
    
    print("=" * 60)
    print("모니터링 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

---

## 예제 8: 가격 변동 알림

특정 가격 이상/이하가 되면 알림을 표시합니다.

```python
#!/usr/bin/env python
"""예제 8: 가격 변동 알림"""

import os
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

class PriceAlert:
    """가격 알림 시스템"""
    
    def __init__(self, engine):
        self.engine = engine
        self.alerts = []
    
    def check_stock_alert(self, ticker, name, target_price, condition="above"):
        """주식 가격 알림 확인
        
        condition:
            "above": target_price 이상
            "below": target_price 이하
        """
        try:
            price = self.engine.get_stock_price(ticker)
            if price is None:
                return
            
            triggered = False
            if condition == "above" and price >= target_price:
                triggered = True
            elif condition == "below" and price <= target_price:
                triggered = True
            
            if triggered:
                alert_msg = f"🔔 [{name}] 가격이 {condition} {target_price:,.0f} KRW에 도달했습니다!"
                alert_msg += f"\n   현재가: {price:,.0f} KRW"
                self.alerts.append(alert_msg)
                return True
            
            return False
        
        except Exception as e:
            print(f"오류: {e}")
            return False
    
    def check_crypto_alert(self, ticker, name, target_price, condition="above"):
        """암호화폐 가격 알림 확인"""
        try:
            price = self.engine.get_coin_price(ticker)
            if price is None:
                return
            
            triggered = False
            if condition == "above" and price >= target_price:
                triggered = True
            elif condition == "below" and price <= target_price:
                triggered = True
            
            if triggered:
                alert_msg = f"🔔 [{name}] 가격이 {condition} {target_price:,.0f} KRW에 도달했습니다!"
                alert_msg += f"\n   현재가: {price:,.0f} KRW"
                self.alerts.append(alert_msg)
                return True
            
            return False
        
        except Exception as e:
            print(f"오류: {e}")
            return False
    
    def print_alerts(self):
        """수집된 알림 출력"""
        if self.alerts:
            print("\n" + "=" * 60)
            print("발생한 알림")
            print("=" * 60)
            for alert in self.alerts:
                print(alert)
                print()
        else:
            print("\n발생한 알림이 없습니다")

def main():
    """가격 변동 알림"""
    
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    print("=" * 60)
    print("예제 8: 가격 변동 알림")
    print("=" * 60)
    print()
    
    with HybridTradingEngine(config) as engine:
        alert_system = PriceAlert(engine)
        
        # 주식 가격 알림 설정
        print("📈 주식 가격 알림 설정")
        print("-" * 60)
        
        # 삼성전자가 70000 이상이면 알림
        alert_system.check_stock_alert("005930", "삼성전자", 70000, "above")
        
        # SK하이닉스가 100000 이하면 알림
        alert_system.check_stock_alert("000660", "SK하이닉스", 100000, "below")
        
        print("✓ 주식 알림 설정 완료")
        
        # 암호화폐 가격 알림 설정
        print("\n💰 암호화폐 가격 알림 설정")
        print("-" * 60)
        
        # 비트코인이 50000000 이상이면 알림
        alert_system.check_crypto_alert("KRW-BTC", "비트코인", 50000000, "above")
        
        # 이더리움이 2000000 이하면 알림
        alert_system.check_crypto_alert("KRW-ETH", "이더리움", 2000000, "below")
        
        print("✓ 암호화폐 알림 설정 완료")
        
        # 알림 출력
        alert_system.print_alerts()

if __name__ == "__main__":
    main()
```

---

## 예제 9: 포트폴리오 분석

보유 자산의 포트폴리오를 분석합니다.

```python
#!/usr/bin/env python
"""예제 9: 포트폴리오 분석"""

import os
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

class Portfolio:
    """포트폴리오 관리 및 분석"""
    
    def __init__(self, engine):
        self.engine = engine
        self.holdings = {}  # 보유 자산
        self.total_value = 0
    
    def add_stock(self, ticker, name, quantity, purchase_price):
        """주식 보유 추가"""
        self.holdings[ticker] = {
            "type": "stock",
            "name": name,
            "quantity": quantity,
            "purchase_price": purchase_price
        }
    
    def add_crypto(self, ticker, name, quantity, purchase_price):
        """암호화폐 보유 추가"""
        self.holdings[ticker] = {
            "type": "crypto",
            "name": name,
            "quantity": quantity,
            "purchase_price": purchase_price
        }
    
    def analyze(self):
        """포트폴리오 분석"""
        print("\n" + "=" * 70)
        print("포트폴리오 분석")
        print("=" * 70)
        print()
        
        print(f"{'자산':<15} {'수량':<8} {'매입가':<12} {'현재가':<12} {'평가액':<12} {'수익률':<8}")
        print("-" * 70)
        
        total_purchase = 0
        total_value = 0
        
        for ticker, holding in self.holdings.items():
            name = holding["name"]
            quantity = holding["quantity"]
            purchase_price = holding["purchase_price"]
            
            # 현재 가격 조회
            if holding["type"] == "stock":
                current_price = self.engine.get_stock_price(ticker)
            else:
                current_price = self.engine.get_coin_price(ticker)
            
            if current_price is None:
                print(f"{name:<15} {quantity:<8} {purchase_price:<12,.0f} {'N/A':<12} {'N/A':<12} {'N/A':<8}")
                continue
            
            # 계산
            purchase_value = purchase_price * quantity
            current_value = current_price * quantity
            profit = current_value - purchase_value
            profit_rate = (profit / purchase_value * 100) if purchase_value > 0 else 0
            
            total_purchase += purchase_value
            total_value += current_value
            
            # 출력
            profit_str = f"{profit_rate:+.2f}%"
            print(f"{name:<15} {quantity:<8.2f} {purchase_price:<12,.0f} {current_price:<12,.0f} {current_value:<12,.0f} {profit_str:<8}")
        
        # 요약
        print("-" * 70)
        total_profit = total_value - total_purchase
        total_profit_rate = (total_profit / total_purchase * 100) if total_purchase > 0 else 0
        
        print(f"\n총 매입액: {total_purchase:,.0f} KRW")
        print(f"현재 평가액: {total_value:,.0f} KRW")
        print(f"총 수익/손실: {total_profit:+,.0f} KRW ({total_profit_rate:+.2f}%)")

def main():
    """포트폴리오 분석"""
    
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    print("=" * 70)
    print("예제 9: 포트폴리오 분석")
    print("=" * 70)
    
    with HybridTradingEngine(config) as engine:
        portfolio = Portfolio(engine)
        
        # 주식 보유
        portfolio.add_stock("005930", "삼성전자", 10, 70000)      # 10주, 매입가 70000
        portfolio.add_stock("000660", "SK하이닉스", 5, 85000)     # 5주, 매입가 85000
        
        # 암호화폐 보유
        portfolio.add_crypto("KRW-BTC", "비트코인", 0.1, 50000000)        # 0.1BTC, 매입가 50000000
        portfolio.add_crypto("KRW-ETH", "이더리움", 1, 2000000)          # 1ETH, 매입가 2000000
        
        # 분석
        portfolio.analyze()

if __name__ == "__main__":
    main()
```

---

## 예제 10: 하이브리드 거래 전략

주식과 암호화폐를 함께 활용하는 거래 전략을 구현합니다.

```python
#!/usr/bin/env python
"""예제 10: 하이브리드 거래 전략 - 자산 분산 투자"""

import os
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

class HybridTradingStrategy:
    """주식과 암호화폐를 함께 활용하는 거래 전략"""
    
    def __init__(self, engine, budget):
        self.engine = engine
        self.budget = budget
        self.allocation_ratio = {
            "stock": 0.6,      # 60% 주식
            "crypto": 0.4      # 40% 암호화폐
        }
    
    def get_recommended_stocks(self):
        """추천 주식 목록"""
        return {
            "005930": "삼성전자",
            "000660": "SK하이닉스",
            "005380": "현대차"
        }
    
    def get_recommended_cryptos(self):
        """추천 암호화폐 목록"""
        return {
            "KRW-BTC": "비트코인",
            "KRW-ETH": "이더리움",
            "KRW-XRP": "리플"
        }
    
    def analyze_investment_plan(self):
        """투자 계획 분석"""
        print("=" * 70)
        print("하이브리드 거래 전략 - 자산 분산 투자")
        print("=" * 70)
        print()
        
        # 자산 배분
        stock_budget = self.budget * self.allocation_ratio["stock"]
        crypto_budget = self.budget * self.allocation_ratio["crypto"]
        
        print(f"전체 투자 예산: {self.budget:,.0f} KRW")
        print(f"주식 투자액: {stock_budget:,.0f} KRW ({self.allocation_ratio['stock']*100:.0f}%)")
        print(f"암호화폐 투자액: {crypto_budget:,.0f} KRW ({self.allocation_ratio['crypto']*100:.0f}%)")
        print()
        
        # 주식 분석
        print("=" * 70)
        print("📈 주식 투자 분석")
        print("=" * 70)
        print()
        
        stocks = self.get_recommended_stocks()
        stock_per_allocation = stock_budget / len(stocks)
        
        print(f"투자 종목 수: {len(stocks)}")
        print(f"종목당 투자액: {stock_per_allocation:,.0f} KRW")
        print()
        print("투자 계획:")
        print("-" * 70)
        
        for ticker, name in stocks.items():
            try:
                price = self.engine.get_stock_price(ticker)
                if price:
                    quantity = int(stock_per_allocation / price)
                    investment = quantity * price
                    print(f"  {name:15s}: {quantity:>3}주 @ {price:>10,.0f} KRW = {investment:>12,.0f} KRW")
                else:
                    print(f"  {name:15s}: 가격 조회 실패")
            except Exception as e:
                print(f"  {name:15s}: 오류 - {e}")
        
        # 암호화폐 분석
        print()
        print("=" * 70)
        print("💰 암호화폐 투자 분석")
        print("=" * 70)
        print()
        
        cryptos = self.get_recommended_cryptos()
        crypto_per_allocation = crypto_budget / len(cryptos)
        
        print(f"투자 종목 수: {len(cryptos)}")
        print(f"종목당 투자액: {crypto_per_allocation:,.0f} KRW")
        print()
        print("투자 계획:")
        print("-" * 70)
        
        for ticker, name in cryptos.items():
            try:
                price = self.engine.get_coin_price(ticker)
                if price:
                    quantity = crypto_per_allocation / price
                    investment = quantity * price
                    print(f"  {name:15s}: {quantity:>10.6f}개 @ {price:>10,.0f} KRW = {investment:>12,.0f} KRW")
                else:
                    print(f"  {name:15s}: 가격 조회 실패")
            except Exception as e:
                print(f"  {name:15s}: 오류 - {e}")

def main():
    """하이브리드 거래 전략"""
    
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    with HybridTradingEngine(config) as engine:
        # 1000만원 투자 계획
        strategy = HybridTradingStrategy(engine, budget=10_000_000)
        strategy.analyze_investment_plan()

if __name__ == "__main__":
    main()
```

---

## 예제 11: 리스트에서 CSV로 내보내기

조회한 가격을 CSV 파일로 내보냅니다.

```python
#!/usr/bin/env python
"""예제 11: 리스트에서 CSV로 내보내기"""

import os
import csv
from datetime import datetime
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

def export_prices_to_csv(stocks, cryptos, engine, filename=None):
    """가격 정보를 CSV로 내보내기"""
    
    if filename is None:
        filename = f"prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # 헤더
        writer.writerow(['자산 유형', '종목명', '티커', '현재가', '조회 시간'])
        
        # 주식 데이터
        for ticker, name in stocks.items():
            try:
                price = engine.get_stock_price(ticker)
                if price:
                    writer.writerow(['주식', name, ticker, f"{price:,.0f}", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            except Exception as e:
                writer.writerow(['주식', name, ticker, 'ERROR', str(e)])
        
        # 암호화폐 데이터
        for ticker, name in cryptos.items():
            try:
                price = engine.get_coin_price(ticker)
                if price:
                    writer.writerow(['암호화폐', name, ticker, f"{price:,.0f}", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            except Exception as e:
                writer.writerow(['암호화폐', name, ticker, 'ERROR', str(e)])
    
    return filename

def main():
    """CSV 내보내기"""
    
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    stocks = {
        "005930": "삼성전자",
        "000660": "SK하이닉스"
    }
    
    cryptos = {
        "KRW-BTC": "비트코인",
        "KRW-ETH": "이더리움"
    }
    
    print("=" * 60)
    print("예제 11: CSV로 내보내기")
    print("=" * 60)
    print()
    
    with HybridTradingEngine(config) as engine:
        filename = export_prices_to_csv(stocks, cryptos, engine)
        print(f"✓ {filename}로 내보냈습니다")

if __name__ == "__main__":
    main()
```

---

## 예제 12: 실시간 대시보드 구현

간단한 텍스트 기반 실시간 대시보드를 구현합니다.

```python
#!/usr/bin/env python
"""예제 12: 실시간 대시보드 구현"""

import os
import time
import os
from datetime import datetime
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

class SimpleDashboard:
    """간단한 텍스트 기반 대시보드"""
    
    def __init__(self, engine):
        self.engine = engine
        self.refresh_count = 0
    
    def clear_screen(self):
        """화면 지우기"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display(self, stocks, cryptos):
        """대시보드 표시"""
        self.refresh_count += 1
        self.clear_screen()
        
        print("╔" + "═" * 78 + "╗")
        print("║" + " Hybrid Trader 실시간 대시보드".center(78) + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        
        # 현재 시간 및 새로고침 정보
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 새로고침: {self.refresh_count}회")
        print()
        
        # 주식 섹션
        print("╔" + "─" * 78 + "╗")
        print("║ 📈 주식 시장".ljust(79) + "║")
        print("╠" + "─" * 78 + "╣")
        
        for ticker, name in stocks.items():
            try:
                price = self.engine.get_stock_price(ticker)
                if price:
                    print(f"║ {name:15s} ({ticker}): {price:>12,.0f} KRW".ljust(79) + "║")
                else:
                    print(f"║ {name:15s} ({ticker}): {'조회 중...':>12}".ljust(79) + "║")
            except Exception as e:
                print(f"║ {name:15s} ({ticker}): {'오류':>12}".ljust(79) + "║")
        
        print("╚" + "─" * 78 + "╝")
        print()
        
        # 암호화폐 섹션
        print("╔" + "─" * 78 + "╗")
        print("║ 💰 암호화폐 시장".ljust(79) + "║")
        print("╠" + "─" * 78 + "╣")
        
        for ticker, name in cryptos.items():
            try:
                price = self.engine.get_coin_price(ticker)
                if price:
                    print(f"║ {name:15s} ({ticker}): {price:>12,.0f} KRW".ljust(79) + "║")
                else:
                    print(f"║ {name:15s} ({ticker}): {'조회 중...':>12}".ljust(79) + "║")
            except Exception as e:
                print(f"║ {name:15s} ({ticker}): {'오류':>12}".ljust(79) + "║")
        
        print("╚" + "─" * 78 + "╝")
        print()
        print("Ctrl+C를 눌러 종료하세요...")

def main():
    """실시간 대시보드"""
    
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY", "demo"),
        secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
        account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
        hts_id=os.getenv("KIS_HTS_ID", "demo"),
        is_demo=True
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
        secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
    )
    
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    stocks = {
        "005930": "삼성전자",
        "000660": "SK하이닉스"
    }
    
    cryptos = {
        "KRW-BTC": "비트코인",
        "KRW-ETH": "이더리움"
    }
    
    with HybridTradingEngine(config) as engine:
        dashboard = SimpleDashboard(engine)
        
        try:
            while True:
                dashboard.display(stocks, cryptos)
                time.sleep(5)  # 5초마다 새로고침
        except KeyboardInterrupt:
            print("\n대시보드를 종료합니다.")

if __name__ == "__main__":
    main()
```

---

## 예제 실행 방법

### 필수 환경변수 설정

```bash
# macOS / Linux
export KIS_APP_KEY="your_key"
export KIS_SECRET_KEY="your_secret"
export KIS_ACCOUNT="1234-5678"
export KIS_HTS_ID="your_hts_id"
export UPBIT_ACCESS_KEY="your_access_key"
export UPBIT_SECRET_KEY="your_secret_key"

# Windows (CMD)
setx KIS_APP_KEY "your_key"
setx KIS_SECRET_KEY "your_secret"
setx KIS_ACCOUNT "1234-5678"
setx KIS_HTS_ID "your_hts_id"
setx UPBIT_ACCESS_KEY "your_access_key"
setx UPBIT_SECRET_KEY "your_secret_key"
```

### 예제 실행

```bash
# 각 예제는 examples/ 폴더에 저장
python examples/stock_trading_example.py
python examples/crypto_trading_example.py
python examples/portfolio_analyzer_example.py
python examples/hybrid_strategy_example.py
```

---

## 더 많은 정보

- [API 문서](./API.md) - 전체 API 참고
- [설치 가이드](./INSTALLATION.md) - 설치 방법
- [아키텍처](./ARCHITECTURE.md) - 시스템 구조
- [문제 해결](./TROUBLESHOOTING.md) - 문제 해결 가이드
