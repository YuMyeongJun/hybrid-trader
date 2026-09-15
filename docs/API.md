# API 문서 (API Documentation)

Hybrid Trader의 완벽한 API 참고서입니다.

## 목차

- [개요](#개요)
- [HybridTradingEngine](#hybridtradingengine)
- [TradingConfig](#tradingconfig)
- [KISConfig](#kisconfig)
- [UpbitConfig](#upbitconfig)
- [예외(Exceptions)](#예외exceptions)
- [Context Manager](#context-manager)
- [로깅](#로깅)

---

## 개요

### 모듈 구조

```python
from hybrid_trader import (
    HybridTradingEngine,    # 메인 거래 엔진
    TradingConfig,          # 설정 클래스
    KISConfig,              # 한국투자증권 설정
    UpbitConfig             # 업비트 설정
)
```

### 버전 정보

```python
import hybrid_trader

print(hybrid_trader.__version__)  # "0.1.0"
print(hybrid_trader.__author__)   # "Your Name"
```

---

## HybridTradingEngine

주식과 암호화폐 거래를 통합으로 관리하는 메인 엔진 클래스입니다.

### 클래스 정의

```python
class HybridTradingEngine:
    """한국투자증권(KIS)과 업비트(Upbit) API를 통합 관리하는 엔진"""
    
    def __init__(self, config: TradingConfig) -> None:
        """
        엔진 초기화
        
        Args:
            config: 거래 설정
            
        Raises:
            ValueError: 설정 검증 실패
        """
```

### 속성 (Properties)

#### `kis_session`

```python
@property
def kis_session(self) -> Any:
    """한국투자증권 세션 (Lazy Loading)
    
    Returns:
        KIS 클라이언트 객체
        
    Raises:
        ImportError: python-kis 라이브러리 미설치
    """
```

**설명**: 필요할 때만 KIS 세션을 생성합니다(Lazy Loading).

**예시**:
```python
engine = HybridTradingEngine(config)
kis = engine.kis_session  # 첫 접근 시 생성
```

#### `upbit_session`

```python
@property
def upbit_session(self) -> Any:
    """업비트 세션 (Lazy Loading)
    
    Returns:
        Upbit 클라이언트 객체
        
    Raises:
        ImportError: pyupbit 라이브러리 미설치
    """
```

**설명**: 필요할 때만 업비트 세션을 생성합니다.

---

### 메서드 (Methods)

#### `get_stock_price(ticker: str) -> Optional[float]`

한국투자증권 API를 통해 주식의 현재가를 조회합니다.

**매개변수**:

| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `ticker` | str | O | 주식 코드 (예: "005930" = 삼성전자) |

**반환값**:

- `float`: 현재 주식가 (KRW 단위)
- `None`: 조회 실패 시

**에러 처리**:

| 예외 | 원인 |
|------|------|
| `ValueError` | 빈 문자열 또는 유효하지 않은 ticker |
| `Exception` | API 호출 실패 (재시도 후에도) |

**예시**:

```python
engine = HybridTradingEngine(config)

# 기본 사용
samsung_price = engine.get_stock_price("005930")
print(f"삼성전자: {samsung_price:,.0f} KRW")

# 에러 처리
try:
    price = engine.get_stock_price("005930")
    if price:
        print(f"가격: {price:,.0f} KRW")
    else:
        print("가격 조회 실패")
except ValueError as e:
    print(f"입력 오류: {e}")
except Exception as e:
    print(f"API 오류: {e}")
```

**주요 주식 코드**:

| 회사 | 코드 |
|------|------|
| 삼성전자 | 005930 |
| SK하이닉스 | 000660 |
| 현대차 | 005380 |
| LG화학 | 051910 |
| NAVER | 035420 |
| 카카오 | 035720 |

---

#### `get_coin_price(ticker: str) -> Optional[float]`

업비트 API를 통해 암호화폐의 현재가를 조회합니다.

**매개변수**:

| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `ticker` | str | O | 암호화폐 코드 (예: "KRW-BTC" = 비트코인) |

**반환값**:

- `float`: 현재 암호화폐 가격 (KRW 단위)
- `None`: 조회 실패 시

**에러 처리**:

| 예외 | 원인 |
|------|------|
| `ValueError` | 빈 문자열 또는 유효하지 않은 ticker |
| `Exception` | API 호출 실패 (재시도 후에도) |

**예시**:

```python
engine = HybridTradingEngine(config)

# 기본 사용
bitcoin_price = engine.get_coin_price("KRW-BTC")
print(f"비트코인: {bitcoin_price:,.0f} KRW")

# 여러 암호화폐 조회
cryptocurrencies = {
    "KRW-BTC": "비트코인",
    "KRW-ETH": "이더리움",
    "KRW-XRP": "리플",
    "KRW-DOGE": "도지코인"
}

for ticker, name in cryptocurrencies.items():
    try:
        price = engine.get_coin_price(ticker)
        if price:
            print(f"{name}: {price:,.0f} KRW")
    except Exception as e:
        print(f"{name} 조회 실패: {e}")
```

**주요 암호화폐 코드**:

| 암호화폐 | 코드 |
|---------|------|
| 비트코인 | KRW-BTC |
| 이더리움 | KRW-ETH |
| 리플 | KRW-XRP |
| 도지코인 | KRW-DOGE |
| 라이트코인 | KRW-LTC |
| 비트캐시 | KRW-BCH |
| EOS | KRW-EOS |
| 스텔라루멘 | KRW-XLM |

---

#### `close() -> None`

모든 활성 세션을 종료합니다.

**매개변수**: 없음

**반환값**: None

**예외**: 없음 (내부 예외는 로깅됨)

**설명**: 엔진을 사용한 후 반드시 호출하거나, Context Manager를 사용하세요.

**예시**:

```python
# 수동 종료
engine = HybridTradingEngine(config)
try:
    price = engine.get_stock_price("005930")
finally:
    engine.close()

# Context Manager 사용 (권장)
with HybridTradingEngine(config) as engine:
    price = engine.get_stock_price("005930")
    # 블록 종료 시 자동으로 close() 호출됨
```

---

### Context Manager

HybridTradingEngine은 Context Manager를 지원하여 안전한 리소스 관리가 가능합니다.

#### `__enter__() -> HybridTradingEngine`

Context Manager 진입.

#### `__exit__(exc_type, exc_val, exc_tb) -> None`

Context Manager 종료. 자동으로 `close()`를 호출합니다.

**예시**:

```python
# Context Manager 사용
with HybridTradingEngine(config) as engine:
    # engine 사용
    stock_price = engine.get_stock_price("005930")
    crypto_price = engine.get_coin_price("KRW-BTC")
    
    print(f"삼성전자: {stock_price:,.0f} KRW")
    print(f"비트코인: {crypto_price:,.0f} KRW")
    
# 자동으로 close()가 호출됨

# 예외가 발생해도 자동으로 close()가 호출됨
try:
    with HybridTradingEngine(config) as engine:
        # 어떤 오류가 발생하든
        engine.get_stock_price("999999")  # 잘못된 코드
except Exception as e:
    print(f"오류: {e}")
finally:
    # close()는 이미 호출되었음
    pass
```

---

## TradingConfig

거래 엔진의 전체 설정을 관리하는 클래스입니다.

### 클래스 정의

```python
@dataclass
class TradingConfig:
    """거래 엔진의 전체 설정"""
    
    kis_config: KISConfig        # 한국투자증권 설정 (필수)
    upbit_config: UpbitConfig    # 업비트 설정 (필수)
    timeout: int = 10            # API 타임아웃 (초, 기본: 10)
    retry_count: int = 3         # 재시도 횟수 (기본: 3)
```

### 속성

| 속성 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `kis_config` | KISConfig | - | 한국투자증권 API 설정 |
| `upbit_config` | UpbitConfig | - | 업비트 API 설정 |
| `timeout` | int | 10 | API 요청 타임아웃 (초) |
| `retry_count` | int | 3 | API 실패 시 재시도 횟수 |

### 메서드

#### `validate() -> bool`

설정의 필수 항목이 모두 입력되었는지 검증합니다.

**반환값**:

- `True`: 모든 필수 항목이 입력됨
- (반환 없음): 필수 항목 누락 시 `ValueError` 발생

**발생하는 예외**:

```
ValueError: Missing required credentials: KIS app_key, KIS secret_key, ...
```

**예시**:

```python
# 올바른 설정
kis_cfg = KISConfig(
    app_key="key",
    secret_key="secret",
    account_number="1234-5678",
    hts_id="hts_id"
)
upbit_cfg = UpbitConfig(access_key="access", secret_key="secret")
config = TradingConfig(kis_config=kis_cfg, upbit_config=upbit_cfg)

try:
    config.validate()
    print("설정이 유효합니다!")
except ValueError as e:
    print(f"설정 오류: {e}")

# 불완전한 설정
incomplete_config = TradingConfig(
    kis_config=KISConfig(app_key="", secret_key="", account_number="", hts_id=""),
    upbit_config=UpbitConfig(access_key="", secret_key="")
)

try:
    incomplete_config.validate()
except ValueError as e:
    print(e)  # Missing required credentials: KIS app_key, KIS secret_key, ...
```

---

## KISConfig

한국투자증권 API 설정을 관리하는 클래스입니다.

### 클래스 정의

```python
@dataclass
class KISConfig:
    """한국투자증권 API 설정"""
    
    app_key: str              # App Key (필수)
    secret_key: str           # Secret Key (필수)
    account_number: str       # 계좌번호 (필수, 형식: "XXXX-XXXX")
    hts_id: str              # HTS ID (필수)
    is_demo: bool = True     # 데모 모드 (기본: True)
```

### 속성

| 속성 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `app_key` | str | O | 한국투자증권 Application Key |
| `secret_key` | str | O | 한국투자증권 Secret Key |
| `account_number` | str | O | 거래 계좌번호 (형식: "1234-5678") |
| `hts_id` | str | O | HTS ID |
| `is_demo` | bool | X | 데모/테스트 모드 (기본값: True) |

### 사용 예시

```python
# 기본 사용 (데모 모드)
kis_config = KISConfig(
    app_key="your_app_key",
    secret_key="your_secret_key",
    account_number="1234-5678",
    hts_id="your_hts_id",
    is_demo=True  # 테스트 모드
)

# 실거래 모드
kis_config_live = KISConfig(
    app_key="your_app_key",
    secret_key="your_secret_key",
    account_number="1234-5678",
    hts_id="your_hts_id",
    is_demo=False  # 실제 거래
)

# 환경변수 사용
import os
kis_config = KISConfig(
    app_key=os.getenv("KIS_APP_KEY"),
    secret_key=os.getenv("KIS_SECRET_KEY"),
    account_number=os.getenv("KIS_ACCOUNT"),
    hts_id=os.getenv("KIS_HTS_ID"),
    is_demo=os.getenv("KIS_DEMO", "true").lower() == "true"
)
```

---

## UpbitConfig

업비트 API 설정을 관리하는 클래스입니다.

### 클래스 정의

```python
@dataclass
class UpbitConfig:
    """업비트 API 설정"""
    
    access_key: str    # Access Key (필수)
    secret_key: str    # Secret Key (필수)
```

### 속성

| 속성 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `access_key` | str | O | 업비트 Access Key |
| `secret_key` | str | O | 업비트 Secret Key |

### 사용 예시

```python
# 기본 사용
upbit_config = UpbitConfig(
    access_key="your_access_key",
    secret_key="your_secret_key"
)

# 환경변수 사용
import os
upbit_config = UpbitConfig(
    access_key=os.getenv("UPBIT_ACCESS_KEY"),
    secret_key=os.getenv("UPBIT_SECRET_KEY")
)

# 설정 재사용
config = TradingConfig(
    kis_config=kis_config,
    upbit_config=upbit_config
)
```

---

## 예외(Exceptions)

### ValueError

필수 설정이 누락되었을 때 발생합니다.

```python
try:
    config = TradingConfig(
        kis_config=KISConfig(app_key="", secret_key="", account_number="", hts_id=""),
        upbit_config=UpbitConfig(access_key="", secret_key="")
    )
except ValueError as e:
    print(f"설정 오류: {e}")
```

### ImportError

필수 라이브러리가 설치되지 않았을 때 발생합니다.

```python
try:
    engine = HybridTradingEngine(config)
    price = engine.get_stock_price("005930")  # KIS 세션 초기화 시도
except ImportError as e:
    print(f"라이브러리 설치 필요: {e}")
    # pip install python-kis 실행 필요
```

### Exception (일반)

API 호출 실패 등 예상치 못한 에러가 발생합니다.

```python
try:
    price = engine.get_stock_price("999999")  # 존재하지 않는 코드
except Exception as e:
    print(f"API 오류: {e}")
```

---

## 로깅

### 기본 로깅 설정

```python
import logging

# 기본 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s'
)

# hybrid_trader 로깅 레벨 설정
logger = logging.getLogger('hybrid_trader')
logger.setLevel(logging.DEBUG)
```

### 로깅 레벨

| 레벨 | 설명 |
|------|------|
| DEBUG | 상세한 디버깅 정보 |
| INFO | 일반 정보성 메시지 |
| WARNING | 경고 메시지 |
| ERROR | 에러 메시지 |
| CRITICAL | 심각한 에러 |

### 예시

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

engine = HybridTradingEngine(config)

# 로그 출력:
# 2024-01-15 10:30:45,123 - hybrid_trader.engine - INFO - HybridTradingEngine initialized successfully
# 2024-01-15 10:30:45,456 - hybrid_trader.engine - INFO - KIS session initialized successfully
# 2024-01-15 10:30:45,789 - hybrid_trader.engine - INFO - Fetching stock price for ticker: 005930
```

### 파일로 로깅

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()  # 콘솔에도 출력
    ]
)

engine = HybridTradingEngine(config)
# trading.log 파일에 모든 로그가 저장됨
```

---

## 완전한 예제

```python
import logging
import os
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s'
)

def main():
    # 환경변수에서 API 키 로드
    kis_config = KISConfig(
        app_key=os.getenv("KIS_APP_KEY"),
        secret_key=os.getenv("KIS_SECRET_KEY"),
        account_number=os.getenv("KIS_ACCOUNT"),
        hts_id=os.getenv("KIS_HTS_ID"),
        is_demo=True  # 테스트 모드
    )
    
    upbit_config = UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY"),
        secret_key=os.getenv("UPBIT_SECRET_KEY")
    )
    
    # 설정 검증
    config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    try:
        config.validate()
        print("✓ 설정이 유효합니다")
    except ValueError as e:
        print(f"✗ 설정 오류: {e}")
        return
    
    # Context Manager로 엔진 사용
    with HybridTradingEngine(config) as engine:
        # 주식 조회
        try:
            stock_price = engine.get_stock_price("005930")
            print(f"삼성전자: {stock_price:,.0f} KRW")
        except Exception as e:
            print(f"주식 조회 실패: {e}")
        
        # 암호화폐 조회
        try:
            crypto_price = engine.get_coin_price("KRW-BTC")
            print(f"비트코인: {crypto_price:,.0f} KRW")
        except Exception as e:
            print(f"암호화폐 조회 실패: {e}")

if __name__ == "__main__":
    main()
```

---

**더 많은 예제는 [EXAMPLES.md](./EXAMPLES.md)를 참고하세요.**
