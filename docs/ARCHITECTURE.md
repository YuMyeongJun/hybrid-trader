# 시스템 아키텍처 (System Architecture)

Hybrid Trader의 전체 아키텍처를 설명합니다.

## 목차

- [개요](#개요)
- [전체 아키텍처](#전체-아키텍처)
- [모듈 구조](#모듈-구조)
- [데이터 흐름](#데이터-흐름)
- [클래스 다이어그램](#클래스-다이어그램)
- [라이프사이클](#라이프사이클)
- [재시도 로직](#재시도-로직)
- [세션 관리](#세션-관리)
- [확장 포인트](#확장-포인트)

---

## 개요

### 프로젝트의 목표

Hybrid Trader는 다음을 목표로 합니다:

1. **API 통합**: 한국투자증권(KIS)과 업비트(Upbit) API를 단일 인터페이스로 제공
2. **간편성**: 복잡한 API 호출을 감싸서 사용하기 쉽게 만들기
3. **안정성**: 자동 재시도, 에러 처리, 로깅으로 안정적인 거래 지원
4. **확장성**: 향후 추가 거래소나 기능을 쉽게 확장할 수 있는 구조

### 핵심 가치

- **Simplicity**: 단순한 API
- **Reliability**: 안정적인 거래 처리
- **Flexibility**: 유연한 구조
- **Maintainability**: 유지보수하기 쉬운 코드

---

## 전체 아키텍처

### 계층 구조

```
┌─────────────────────────────────────┐
│         사용자 애플리케이션         │
│   (User Application/Examples)       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Hybrid Trader 라이브러리       │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  HybridTradingEngine        │   │
│  │  (통합 거래 엔진)           │   │
│  └──────┬──────────────┬───────┘   │
│         │              │            │
│    ┌────▼────┐    ┌────▼────┐     │
│    │ KIS API │    │Upbit API│     │
│    │ Wrapper │    │ Wrapper │     │
│    └────┬────┘    └────┬────┘     │
│         │              │            │
│  ┌──────▼──────────────▼───────┐   │
│  │    TradingConfig            │   │
│  │    (KISConfig, UpbitConfig) │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
         │              │
         │              │
    ┌────▼─┐        ┌───▼────┐
    │ KIS  │        │ Upbit  │
    │ API  │        │  API   │
    └──────┘        └────────┘
         │              │
    ┌────▼──────────────▼──┐
    │   한국투자증권 서버   │
    │   업비트 서버        │
    └─────────────────────┘
```

---

## 모듈 구조

### 패키지 레이아웃

```
hybrid-trader/
│
├── hybrid_trader/           # 메인 패키지
│   ├── __init__.py         # 패키지 초기화 (public API)
│   ├── config.py           # 설정 클래스 (KISConfig, UpbitConfig, TradingConfig)
│   ├── engine.py           # 메인 엔진 (HybridTradingEngine)
│   └── exceptions.py       # 커스텀 예외 (향후 추가)
│
├── examples/               # 예제 코드
│   ├── basic_example.py
│   ├── stock_trading_example.py
│   ├── crypto_trading_example.py
│   ├── portfolio_analyzer_example.py
│   └── hybrid_strategy_example.py
│
├── tests/                  # 테스트 코드
│   ├── __init__.py
│   ├── test_config.py
│   └── test_engine.py
│
├── docs/                   # 문서
│   ├── INSTALLATION.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── EXAMPLES.md
│   ├── CONTRIBUTING.md
│   └── TROUBLESHOOTING.md
│
├── README.md              # 프로젝트 README
├── setup.py              # 패키지 설정
├── requirements.txt      # 의존성
└── LICENSE              # 라이선스
```

### 모듈 설명

#### `__init__.py`

**목적**: 패키지 초기화 및 public API 정의

**내용**:
```python
from .engine import HybridTradingEngine
from .config import TradingConfig, KISConfig, UpbitConfig

__version__ = "0.1.0"
__author__ = "Your Name"
__all__ = ["HybridTradingEngine", "TradingConfig", "KISConfig", "UpbitConfig"]
```

**역할**: 외부 사용자가 접근해야 할 클래스만 노출

#### `config.py`

**목적**: 설정 클래스 관리

**클래스**:
- `KISConfig`: 한국투자증권 설정
- `UpbitConfig`: 업비트 설정
- `TradingConfig`: 전체 설정 및 검증

#### `engine.py`

**목적**: 메인 거래 엔진

**클래스**:
- `HybridTradingEngine`: 주식과 암호화폐 거래를 통합 관리

**주요 메서드**:
- `get_stock_price()`: 주식 현재가 조회
- `get_coin_price()`: 암호화폐 현재가 조회
- `close()`: 세션 종료
- `_call_kis_api()`: 내부 KIS API 호출
- `_call_upbit_api()`: 내부 업비트 API 호출

---

## 데이터 흐름

### 주식 가격 조회 흐름

```
┌─────────────────────────┐
│  get_stock_price("005930")
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Validation                      │
│ - ticker 빈 문자열 확인         │
│ - ticker 타입 확인              │
└──────────┬──────────────────────┘
           │ (Valid)
           ▼
┌─────────────────────────────────┐
│ _call_kis_api()                 │
│ endpoint: "/stock/price"        │
│ params: {"ticker": "005930"}    │
└──────────┬──────────────────────┘
           │
      ┌────┴──────────────────┐
      │                       │
  ┌───▼────┐              ┌───▼──────┐
  │ API    │              │ Retry   │
  │ Success│              │ (3회)   │
  └───┬────┘              └───┬─────┘
      │                       │
      │                   ┌───▼────┐
      │                   │ Failed │
      │                   └───┬────┘
      │                       │
      └───────┬───────────────┘
              │
      ┌───────▼────────────┐
      │ Parse Response     │
      │ Extract 'stck_prpr'│
      └───────┬────────────┘
              │
      ┌───────▼────────────────┐
      │ Return float price     │
      │ 또는 None (실패)        │
      └────────────────────────┘
```

### 암호화폐 가격 조회 흐름

```
┌─────────────────────────┐
│  get_coin_price("KRW-BTC")
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Validation                      │
│ - ticker 빈 문자열 확인         │
│ - ticker 타입 확인              │
└──────────┬──────────────────────┘
           │ (Valid)
           ▼
┌──────────────────────────────────┐
│ _call_upbit_api()                │
│ endpoint: "/ticker"              │
│ params: {"markets": "KRW-BTC"}   │
└──────────┬───────────────────────┘
           │
      ┌────┴──────────────────┐
      │                       │
  ┌───▼────┐              ┌───▼──────┐
  │ API    │              │ Retry   │
  │ Success│              │ (3회)   │
  └───┬────┘              └───┬─────┘
      │                       │
      │                   ┌───▼────┐
      │                   │ Failed │
      │                   └───┬────┘
      │                       │
      └───────┬───────────────┘
              │
      ┌───────▼──────────────┐
      │ Parse Response       │
      │ Extract current_price│
      └───────┬──────────────┘
              │
      ┌───────▼────────────────┐
      │ Return float price     │
      │ 또는 None (실패)        │
      └────────────────────────┘
```

---

## 클래스 다이어그램

### 클래스 관계도

```
┌─────────────────────────────────────┐
│      TradingConfig (설정)           │
│─────────────────────────────────────│
│ + kis_config: KISConfig             │
│ + upbit_config: UpbitConfig         │
│ + timeout: int                      │
│ + retry_count: int                  │
│─────────────────────────────────────│
│ + validate() -> bool                │
└────────┬──────────────────┬─────────┘
         │                  │
   ┌─────▼──────┐   ┌──────▼────────┐
   │  KISConfig │   │ UpbitConfig   │
   │────────────│   │───────────────│
   │+ app_key   │   │+ access_key   │
   │+ secret_key│   │+ secret_key   │
   │+ account_# │   └────────────────┘
   │+ hts_id    │
   │+ is_demo   │
   └────────────┘
         ▲
         │ uses
         │
┌────────┴─────────────────────────────┐
│  HybridTradingEngine (엔진)          │
│──────────────────────────────────────│
│ - config: TradingConfig              │
│ - _kis_session: Any                  │
│ - _upbit_session: Any                │
│──────────────────────────────────────│
│ + kis_session: Any (property)        │
│ + upbit_session: Any (property)      │
│ + get_stock_price(ticker) -> float   │
│ + get_coin_price(ticker) -> float    │
│ + close()                            │
│ + __enter__() -> self                │
│ + __exit__()                         │
│ - _call_kis_api(endpoint, params)    │
│ - _call_upbit_api(endpoint, params)  │
└──────────────────────────────────────┘
```

---

## 라이프사이클

### 엔진의 생명주기

```
1. 인스턴스 생성
   ↓
   engine = HybridTradingEngine(config)
   ├─ config 저장
   ├─ _kis_session = None
   └─ _upbit_session = None

2. 첫 호출 (Lazy Loading)
   ↓
   engine.get_stock_price("005930")
   ├─ kis_session 속성 접근
   ├─ KIS 세션 초기화
   └─ API 호출

3. 세션 재사용
   ↓
   engine.get_stock_price("000660")
   ├─ kis_session 이미 초기화됨
   └─ 기존 세션 사용

4. 종료
   ↓
   engine.close()
   ├─ KIS 세션 정리
   └─ 업비트 세션 정리
```

### Context Manager 사용 시

```
with HybridTradingEngine(config) as engine:  # __enter__() 호출
    # engine 사용
    price = engine.get_stock_price("005930")
# __exit__() 호출 → engine.close() 자동 실행
```

---

## 재시도 로직

### 재시도 메커니즘

```python
for attempt in range(retry_count):  # 기본값: 3
    try:
        # API 호출
        response = api.call()
        return response
    except Exception as e:
        if attempt == retry_count - 1:
            # 마지막 시도 → 예외 발생
            raise
        # 대기 후 재시도
        time.sleep(1)  # 1초 대기
```

### 동작 흐름

```
첫 번째 시도
    ├─ 성공 → 반환
    └─ 실패 → 1초 대기

두 번째 시도
    ├─ 성공 → 반환
    └─ 실패 → 1초 대기

세 번째 시도 (마지막)
    ├─ 성공 → 반환
    └─ 실패 → 예외 발생
```

### 설정

```python
config = TradingConfig(
    kis_config=kis_cfg,
    upbit_config=upbit_cfg,
    retry_count=3,  # 재시도 횟수
    timeout=10      # 타임아웃 (초)
)
```

---

## 세션 관리

### Lazy Loading

세션은 필요할 때만 초기화됩니다:

```python
engine = HybridTradingEngine(config)
# 아직 세션 없음

price = engine.get_stock_price("005930")
# kis_session 속성 접근 → KIS 세션 초기화

crypto = engine.get_coin_price("KRW-BTC")
# upbit_session 속성 접근 → Upbit 세션 초기화
```

### 장점

1. **성능**: 필요하지 않은 세션은 초기화하지 않음
2. **유연성**: 한쪽 API만 사용 가능
3. **리소스 절약**: 메모리와 네트워크 리소스 절약

---

## 확장 포인트

### 1. 새로운 API 추가

```python
# engine.py에 새로운 메서드 추가
def get_forex_rate(self, pair: str) -> Optional[float]:
    """외환 환율 조회"""
    # 구현
    pass
```

### 2. API 래퍼 확장

```python
# config.py에 새로운 Config 클래스 추가
@dataclass
class ForexConfig:
    """외환 API 설정"""
    api_key: str
    api_secret: str
```

### 3. 커스텀 예외 추가

```python
# exceptions.py 생성
class APIError(Exception):
    """API 호출 실패"""
    pass

class ValidationError(Exception):
    """설정 검증 실패"""
    pass
```

### 4. 로깅 확장

```python
# 세션별 로거
kis_logger = logging.getLogger('hybrid_trader.kis')
upbit_logger = logging.getLogger('hybrid_trader.upbit')
```

---

## 보안 고려사항

### API 키 관리

```python
# 권장: 환경변수 사용
import os
app_key = os.getenv("KIS_APP_KEY")

# 비권장: 하드코딩
app_key = "your_key_here"  # 절대 금지!
```

### 세션 정리

```python
# 반드시 사용
with HybridTradingEngine(config) as engine:
    # 사용
    pass
# 자동으로 정리됨
```

---

## 성능 최적화

### 1. 세션 재사용

같은 엔진 인스턴스로 여러 API 호출:

```python
engine = HybridTradingEngine(config)

# 같은 세션 사용
for ticker in ["005930", "000660", "035420"]:
    price = engine.get_stock_price(ticker)
```

### 2. 배치 처리

여러 ticker를 한 번에 처리:

```python
tickers = ["005930", "000660", "035420"]
prices = [engine.get_stock_price(t) for t in tickers]
```

### 3. 에러 처리 최적화

```python
# 효율적인 에러 처리
try:
    prices = [engine.get_stock_price(t) for t in tickers]
except Exception as e:
    # 개별 처리로 변경
    for ticker in tickers:
        try:
            price = engine.get_stock_price(ticker)
        except Exception:
            continue
```

---

## 테스트 전략

### 단위 테스트

```python
# test_engine.py
def test_get_stock_price_validation():
    """invalid ticker는 ValueError 발생"""
    engine = HybridTradingEngine(config)
    with pytest.raises(ValueError):
        engine.get_stock_price("")
```

### 통합 테스트

```python
def test_hybrid_workflow():
    """주식과 암호화폐를 동시에 조회"""
    with HybridTradingEngine(config) as engine:
        stock = engine.get_stock_price("005930")
        crypto = engine.get_coin_price("KRW-BTC")
        
        assert stock is not None
        assert crypto is not None
```

---

## 버전 관리

### Semantic Versioning

```
0.1.0
│ │ │
│ │ └─ 패치 (버그 수정)
│ └─── 마이너 (기능 추가)
└───── 메이저 (호환성 변경)
```

### 향후 계획

- **0.2.0**: 매도/매수 기능 추가
- **0.3.0**: 실시간 데이터 스트리밍
- **1.0.0**: 안정화 버전

---

## 다음 단계

- [API 문서](./API.md)를 읽고 메서드 사용법 학습
- [예제](./EXAMPLES.md)로 실제 사용 사례 확인
- [기여 가이드](./CONTRIBUTING.md)로 프로젝트 개선에 참여
