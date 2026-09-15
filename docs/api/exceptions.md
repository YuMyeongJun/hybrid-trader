# Exceptions (예외 처리)

Hybrid Trader의 커스텀 예외들입니다.

## 예외 계층 구조

```
Exception
└── HybridTraderException (기본)
    ├── InvalidTickerError
    ├── APIConnectionError
    ├── ConfigurationError
    ├── SessionNotInitializedError
    ├── InsufficientBalanceError
    └── OrderRejectedError
```

---

## HybridTraderException

모든 Hybrid Trader 예외의 기본 클래스입니다.

```python
class HybridTraderException(Exception):
    """Hybrid Trader의 기본 예외"""
    pass
```

**예시:**
```python
from hybrid_trader.exceptions import HybridTraderException

try:
    # Hybrid Trader 코드
    pass
except HybridTraderException as e:
    print(f"Hybrid Trader 오류: {e}")
```

---

## InvalidTickerError

유효하지 않은 티커일 때 발생합니다.

```python
class InvalidTickerError(HybridTraderException):
    """유효하지 않은 티커"""
    pass
```

**원인:**
- 존재하지 않는 종목 코드
- 잘못된 형식의 티커
- 지원하지 않는 종목

**예시:**
```python
from hybrid_trader.exceptions import InvalidTickerError

try:
    price = engine.get_stock_price("999999")  # 존재하지 않는 코드
except InvalidTickerError as e:
    print(f"유효하지 않은 티커: {e}")
    
    # 올바른 티커로 재시도
    price = engine.get_stock_price("005930")  # 삼성전자
```

**해결책:**
```python
# 1. 올바른 티커 확인
# 한국투자증권: https://developers.trueinvesting.com
# 업비트: https://docs.upbit.com/guide/orderbook-api

# 2. 형식 확인
# 주식: 6자리 숫자 (예: 005930)
# 암호화폐: KRW-CODE (예: KRW-BTC)

# 3. 유효성 검사
def is_valid_stock_ticker(ticker):
    return isinstance(ticker, str) and len(ticker) == 6 and ticker.isdigit()

def is_valid_crypto_ticker(ticker):
    return isinstance(ticker, str) and ticker.startswith("KRW-")
```

---

## APIConnectionError

API 연결 오류가 발생했을 때입니다.

```python
class APIConnectionError(HybridTraderException):
    """API 연결 오류"""
    pass
```

**원인:**
- 인터넷 연결 끊김
- API 서버 다운
- 잘못된 API 키
- 권한 부족
- API 호출 한도 초과
- IP 화이트리스트 제외

**예시:**
```python
from hybrid_trader.exceptions import APIConnectionError

try:
    price = engine.get_stock_price("005930")
except APIConnectionError as e:
    print(f"API 연결 오류: {e}")
    print("나중에 다시 시도하세요")
```

**해결책:**
```python
import time

def retry_with_backoff(func, max_retries=3):
    """재시도 로직"""
    for attempt in range(max_retries):
        try:
            return func()
        except APIConnectionError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1초, 2초, 4초
                print(f"{wait_time}초 후 재시도...")
                time.sleep(wait_time)
            else:
                raise

# 사용
try:
    price = retry_with_backoff(
        lambda: engine.get_stock_price("005930")
    )
except APIConnectionError:
    print("재시도 실패")
```

---

## ConfigurationError

설정이 유효하지 않을 때입니다.

```python
class ConfigurationError(HybridTraderException):
    """설정 오류"""
    pass
```

**원인:**
- API 키 누락
- API 키 형식 오류
- 계좌번호 형식 오류
- 필수 설정 항목 누락
- 설정 값이 유효하지 않음

**예시:**
```python
from hybrid_trader.exceptions import ConfigurationError

try:
    config = TradingConfig(
        kis_config=KISConfig(
            app_key="",  # 빈 값
            secret_key="your_key",
            account_number="invalid",  # 형식 오류
            hts_id="your_id"
        ),
        upbit_config=UpbitConfig(...)
    )
    engine = HybridTradingEngine(config)
except ConfigurationError as e:
    print(f"설정 오류: {e}")
```

**해결책:**
```python
import os
from dotenv import load_dotenv

# 1. 환경변수 로드
load_dotenv()

# 2. 환경변수 확인
required_vars = [
    "KIS_APP_KEY",
    "KIS_SECRET_KEY",
    "KIS_ACCOUNT",
    "KIS_HTS_ID",
    "UPBIT_ACCESS_KEY",
    "UPBIT_SECRET_KEY"
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"누락된 환경변수: {missing_vars}")
else:
    # 3. 설정 생성
    config = TradingConfig(
        kis_config=KISConfig(
            app_key=os.getenv("KIS_APP_KEY"),
            secret_key=os.getenv("KIS_SECRET_KEY"),
            account_number=os.getenv("KIS_ACCOUNT"),  # XXXX-XXXX 형식
            hts_id=os.getenv("KIS_HTS_ID")
        ),
        upbit_config=UpbitConfig(
            access_key=os.getenv("UPBIT_ACCESS_KEY"),
            secret_key=os.getenv("UPBIT_SECRET_KEY")
        )
    )
    engine = HybridTradingEngine(config)
```

---

## SessionNotInitializedError

세션이 초기화되지 않았을 때입니다.

```python
class SessionNotInitializedError(HybridTraderException):
    """세션 미초기화"""
    pass
```

**원인:**
- 엔진이 생성되지 않음
- 엔진이 종료됨
- 중복 호출

**예시:**
```python
from hybrid_trader.exceptions import SessionNotInitializedError

try:
    engine.close()
    price = engine.get_stock_price("005930")  # 에러!
except SessionNotInitializedError as e:
    print(f"세션 오류: {e}")
    print("새 엔진을 생성해야 합니다")
```

**해결책:**
```python
# ✅ 올바른 방법: with 문 사용
with HybridTradingEngine(config) as engine:
    price = engine.get_stock_price("005930")
    # 블록 종료 시 자동으로 세션 정리

# ❌ 잘못된 방법: 수동 관리
engine = HybridTradingEngine(config)
price = engine.get_stock_price("005930")
engine.close()
price = engine.get_stock_price("005930")  # 에러!
```

---

## InsufficientBalanceError

잔고가 부족할 때입니다.

```python
class InsufficientBalanceError(HybridTraderException):
    """잔고 부족"""
    pass
```

**원인:**
- 매수 금액이 잔고보다 많음
- 매도 수량이 보유량보다 많음
- 거래비 계산 오류

**예시:**
```python
from hybrid_trader.exceptions import InsufficientBalanceError

try:
    # 1000만원짜리 주식을 500만원으로는 구매 불가
    order = engine.buy_stock("005930", 100, 100000)
except InsufficientBalanceError as e:
    print(f"잔고 부족: {e}")
    
    # 잔고 확인 후 재시도
    balance = engine.get_balance()
    print(f"현금 잔고: {balance:,.0f} KRW")
```

**해결책:**
```python
# 1. 잔고 확인
balance = engine.get_balance()
print(f"현금 잔고: {balance:,.0f} KRW")

# 2. 보유 포지션 확인
position = engine.get_position("005930")
if position:
    print(f"보유 수량: {position.quantity}주")

# 3. 주문 가능 금액/수량 확인
orderable = engine.get_orderable_amount("005930")
print(f"주문 가능 금액: {orderable:,.0f} KRW")

# 4. 금액 조정하여 주문
qty = int(balance * 0.95 / 100000)  # 잔고의 95%로 주식 구매
order = engine.buy_stock("005930", qty)
```

---

## OrderRejectedError

주문이 거부되었을 때입니다.

```python
class OrderRejectedError(HybridTraderException):
    """주문 거부"""
    pass
```

**원인:**
- 거래 가능 시간이 아님
- 매도 주문 시 해당 수량 미보유
- 거래소 점검 중
- 규정 위반 주문
- 기술적 문제

**예시:**
```python
from hybrid_trader.exceptions import OrderRejectedError

try:
    order = engine.buy_stock("005930", 10, 70000)
except OrderRejectedError as e:
    print(f"주문 거부: {e}")
    
    # 거래 가능 시간 확인
    # 주식: 09:00 ~ 15:30 (평일)
    # 암호화폐: 24/7
```

---

## 🛡️ 예외 처리 모범 사례

### 1. 기본 예외 처리

```python
from hybrid_trader import HybridTradingEngine
from hybrid_trader.exceptions import HybridTraderException

try:
    with HybridTradingEngine(config) as engine:
        price = engine.get_stock_price("005930")
except HybridTraderException as e:
    print(f"오류 발생: {e}")
except Exception as e:
    print(f"예상치 못한 오류: {e}")
```

### 2. 구체적인 예외 처리

```python
from hybrid_trader.exceptions import (
    InvalidTickerError,
    APIConnectionError,
    ConfigurationError,
    InsufficientBalanceError
)

try:
    price = engine.get_stock_price("005930")
except InvalidTickerError as e:
    print(f"유효하지 않은 티커: {e}")
except APIConnectionError as e:
    print(f"API 연결 오류: {e}")
    # 재시도 로직
except ConfigurationError as e:
    print(f"설정 오류: {e}")
except InsufficientBalanceError as e:
    print(f"잔고 부족: {e}")
```

### 3. 로깅과 함께 사용

```python
import logging
from hybrid_trader.exceptions import HybridTraderException

logger = logging.getLogger(__name__)

try:
    price = engine.get_stock_price("005930")
except HybridTraderException as e:
    logger.error(f"Hybrid Trader 오류: {e}", exc_info=True)
    raise
```

### 4. 재시도 데코레이터

```python
import functools
import time
from hybrid_trader.exceptions import APIConnectionError

def retry_on_api_error(max_retries=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except APIConnectionError:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                    else:
                        raise
        return wrapper
    return decorator

@retry_on_api_error(max_retries=3)
def get_price(ticker):
    return engine.get_stock_price(ticker)
```

---

## 📚 더 알아보기

- [문제 해결](../guide/troubleshooting.md)
- [예제 모음](../guide/examples.md)
- [Engine API](engine.md)
