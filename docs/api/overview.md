# API 레퍼런스 개요

Hybrid Trader의 완전한 API 문서입니다.

## 📚 API 구조

```
hybrid_trader/
├── HybridTradingEngine      - 메인 거래 엔진
├── TradingConfig            - 설정
├── Monitoring
│   ├── PriceMonitor        - 가격 모니터링
│   └── PortfolioMonitor    - 포트폴리오 모니터링
├── Analysis                 - 분석 도구
└── Exceptions              - 예외 처리
```

## 🎯 빠른 시작

### 기본 사용법

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 설정
config = TradingConfig(
    kis_config=KISConfig(...),
    upbit_config=UpbitConfig(...)
)

# 엔진 초기화
engine = HybridTradingEngine(config)

# 사용
price = engine.get_stock_price("005930")
```

## 📖 API 문서 섹션

### 1. [Core Engine](engine.md)

**HybridTradingEngine** - 메인 거래 엔진

**주요 메서드:**
- `get_stock_price(ticker)` - 주식 가격 조회
- `get_coin_price(ticker)` - 암호화폐 가격 조회
- `buy_stock(ticker, quantity, price)` - 주식 매수
- `sell_stock(ticker, quantity, price)` - 주식 매도
- `buy_coin(ticker, amount)` - 암호화폐 매수
- `sell_coin(ticker, amount)` - 암호화폐 매도

### 2. [Configuration](config.md)

**설정 클래스** - API 자격증명 및 옵션

**클래스:**
- `KISConfig` - 한국투자증권 설정
- `UpbitConfig` - 업비트 설정
- `TradingConfig` - 통합 설정

### 3. [Monitoring](monitoring.md)

**모니터링 도구** - 실시간 데이터 추적

**클래스:**
- `PriceMonitor` - 가격 모니터링
- `PortfolioMonitor` - 포트폴리오 모니터링
- `PriceAlert` - 가격 알림
- `PriceSnapshot` - 가격 스냅샷

### 4. [Exceptions](exceptions.md)

**예외 처리** - 에러 처리

**예외:**
- `HybridTraderException` - 기본 예외
- `InvalidTickerError` - 유효하지 않은 티커
- `APIConnectionError` - API 연결 오류
- `ConfigurationError` - 설정 오류
- `SessionNotInitializedError` - 세션 미초기화

## 🔄 API 메서드 분류

### 조회 메서드

| 메서드 | 설명 | 반환값 |
|--------|------|--------|
| `get_stock_price(ticker)` | 주식 현재가 | float |
| `get_coin_price(ticker)` | 암호화폐 현재가 | float |
| `get_position(ticker)` | 포지션 조회 | Position |
| `get_orderbook(ticker)` | 호가 조회 | Dict |

### 거래 메서드

| 메서드 | 설명 | 반환값 |
|--------|------|--------|
| `buy_stock(ticker, qty, price)` | 주식 매수 | OrderResult |
| `sell_stock(ticker, qty, price)` | 주식 매도 | OrderResult |
| `buy_coin(ticker, amount)` | 암호화폐 매수 | OrderResult |
| `sell_coin(ticker, amount)` | 암호화폐 매도 | OrderResult |

### 주문 관리 메서드

| 메서드 | 설명 | 반환값 |
|--------|------|--------|
| `cancel_order(order_id)` | 주문 취소 | bool |
| `get_order_status(order_id)` | 주문 상태 조회 | OrderStatus |
| `get_order_history()` | 주문 이력 조회 | List[Order] |

### 포트폴리오 메서드

| 메서드 | 설명 | 반환값 |
|--------|------|--------|
| `get_portfolio_snapshot()` | 포트폴리오 스냅샷 | PortfolioSnapshot |
| `get_positions()` | 모든 포지션 조회 | List[Position] |
| `get_balance()` | 잔고 조회 | Balance |

## 💾 데이터 모델

### Position (포지션)

```python
@dataclass
class Position:
    ticker: str          # 티커
    quantity: float      # 수량
    average_price: float # 평균 매입가
    current_price: float # 현재가
    valuation: float     # 평가액
    profit_loss: float   # 평가손익
    profit_loss_rate: float # 수익률 (%)
```

### OrderResult (주문 결과)

```python
@dataclass
class OrderResult:
    order_id: str        # 주문번호
    ticker: str          # 티커
    side: str            # 'buy' 또는 'sell'
    quantity: float      # 수량
    price: float         # 가격
    timestamp: datetime  # 주문시간
    status: str          # 'pending', 'filled', 'cancelled'
```

### PortfolioSnapshot (포트폴리오 스냅샷)

```python
@dataclass
class PortfolioSnapshot:
    total_valuation: float      # 총 자산가
    cash_balance: float         # 현금
    profit_loss: float          # 평가손익
    profit_loss_rate: float     # 수익률 (%)
    positions: List[Position]   # 보유 포지션
    timestamp: datetime         # 조회시간
```

## 🔐 보안 가이드

### API 키 관리

```python
# ❌ 하지 말 것
engine = HybridTradingEngine(
    config=TradingConfig(
        kis_config=KISConfig(app_key="ak1234567890")  # 절대 금지!
    )
)

# ✅ 올바른 방법
import os
engine = HybridTradingEngine(
    config=TradingConfig(
        kis_config=KISConfig(app_key=os.getenv("KIS_APP_KEY"))
    )
)
```

### Context Manager 사용

```python
# ✅ 권장: with 문으로 자동 정리
with HybridTradingEngine(config) as engine:
    price = engine.get_stock_price("005930")
# 블록 종료 시 자동으로 세션 정리

# ❌ 권장하지 않음
engine = HybridTradingEngine(config)
price = engine.get_stock_price("005930")
# 수동으로 정리 필요: engine.close()
```

## 🚀 성능 팁

### 1. 배치 요청

```python
# 여러 주식 가격을 한번에 조회
tickers = ["005930", "000660", "005380"]
prices = engine.get_batch_stock_prices(tickers)
```

### 2. 캐싱

```python
# 캐시를 사용하여 불필요한 API 호출 줄이기
price = engine.get_cached_stock_price("005930", cache_timeout=60)
```

### 3. 비동기 처리

```python
# 여러 작업을 동시에 처리
import asyncio

async def get_prices():
    price1 = await engine.get_stock_price_async("005930")
    price2 = await engine.get_coin_price_async("KRW-BTC")
    return price1, price2
```

## ⚡ 에러 처리

### 기본 에러 처리

```python
from hybrid_trader.exceptions import (
    HybridTraderException,
    InvalidTickerError,
    APIConnectionError
)

try:
    price = engine.get_stock_price("999999")
except InvalidTickerError as e:
    print(f"유효하지 않은 티커: {e}")
except APIConnectionError as e:
    print(f"API 연결 오류: {e}")
except HybridTraderException as e:
    print(f"기타 오류: {e}")
```

### 재시도 로직

```python
import time

def get_price_with_retry(ticker, max_retries=3):
    for attempt in range(max_retries):
        try:
            return engine.get_stock_price(ticker)
        except APIConnectionError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"{wait_time}초 후 재시도...")
                time.sleep(wait_time)
            else:
                raise
```

## 📊 사용 예제

### 예제 1: 기본 거래

```python
with HybridTradingEngine(config) as engine:
    # 가격 조회
    stock_price = engine.get_stock_price("005930")
    crypto_price = engine.get_coin_price("KRW-BTC")
    
    # 주문
    stock_order = engine.buy_stock("005930", 10, stock_price * 0.99)
    crypto_order = engine.buy_coin("KRW-BTC", 1000000)
```

### 예제 2: 포트폴리오 분석

```python
from hybrid_trader import PortfolioMonitor

with HybridTradingEngine(config) as engine:
    monitor = PortfolioMonitor(engine)
    
    # 포트폴리오 조회
    snapshot = monitor.get_portfolio_snapshot()
    print(f"총 자산: {snapshot.total_valuation:,.0f} KRW")
    print(f"수익률: {snapshot.profit_loss_rate:.2f}%")
    
    # 각 포지션 분석
    for position in snapshot.positions:
        print(f"{position.ticker}: {position.profit_loss_rate:+.2f}%")
```

### 예제 3: 실시간 모니터링

```python
from hybrid_trader import PriceMonitor
import time

with HybridTradingEngine(config) as engine:
    monitor = PriceMonitor(engine)
    
    for _ in range(10):
        price = monitor.get_latest_price("005930")
        print(f"삼성전자: {price:,.0f} KRW")
        time.sleep(1)
```

## 🔗 API 버전

**현재 버전**: 0.1.0

**호환성**: Python 3.8+

## 📚 추가 자료

- [상세 API 문서](engine.md)
- [설정 가이드](../guide/configuration.md)
- [예제 모음](../guide/examples.md)
- [문제 해결](../guide/troubleshooting.md)

---

**더 많은 도움이 필요하신가요?**

- 📝 [FAQ](../resources/faq.md)
- 🐛 [이슈 제보](https://github.com/YuMyeongJun/hybrid-trader/issues)
- 💬 [토론](https://github.com/YuMyeongJun/hybrid-trader/discussions)
