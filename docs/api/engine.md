# HybridTradingEngine API

Hybrid Trader의 메인 거래 엔진입니다.

## 클래스: HybridTradingEngine

주식(KIS)과 암호화폐(Upbit) 거래를 통합으로 관리하는 메인 엔진입니다.

### 초기화

```python
from hybrid_trader import HybridTradingEngine, TradingConfig

engine = HybridTradingEngine(config: TradingConfig) -> None
```

**매개변수:**
- `config` (TradingConfig): 거래 설정

**예시:**
```python
config = TradingConfig(kis_config=kis_cfg, upbit_config=upbit_cfg)
engine = HybridTradingEngine(config)
```

### Context Manager

```python
with HybridTradingEngine(config) as engine:
    price = engine.get_stock_price("005930")
    # 블록 종료 시 자동으로 세션 정리
```

## 📊 조회 메서드

### get_stock_price

주식의 현재가를 조회합니다.

```python
def get_stock_price(self, ticker: str) -> Optional[float]:
    """
    Args:
        ticker (str): 주식 코드 (예: "005930")
    
    Returns:
        float: 현재가 (KRW 단위)
        None: 조회 실패 시
    
    Raises:
        InvalidTickerError: 유효하지 않은 티커
        APIConnectionError: API 연결 오류
    """
```

**예시:**
```python
price = engine.get_stock_price("005930")  # 삼성전자
print(f"삼성전자: {price:,.0f} KRW")
```

### get_coin_price

암호화폐의 현재가를 조회합니다.

```python
def get_coin_price(self, ticker: str) -> Optional[float]:
    """
    Args:
        ticker (str): 암호화폐 코드 (예: "KRW-BTC")
    
    Returns:
        float: 현재가 (KRW 단위)
        None: 조회 실패 시
    
    Raises:
        InvalidTickerError: 유효하지 않은 티커
        APIConnectionError: API 연결 오류
    """
```

**예시:**
```python
btc_price = engine.get_coin_price("KRW-BTC")  # 비트코인
eth_price = engine.get_coin_price("KRW-ETH")  # 이더리움
print(f"비트코인: {btc_price:,.0f} KRW")
```

### get_position

특정 종목의 포지션을 조회합니다.

```python
def get_position(self, ticker: str) -> Optional[Position]:
    """
    Args:
        ticker (str): 티커
    
    Returns:
        Position: 포지션 정보
        None: 포지션이 없는 경우
    """
```

**반환값:**
```python
@dataclass
class Position:
    ticker: str
    quantity: float
    average_price: float
    current_price: float
    valuation: float
    profit_loss: float
    profit_loss_rate: float
```

**예시:**
```python
position = engine.get_position("005930")
if position:
    print(f"보유: {position.quantity}주")
    print(f"평가액: {position.valuation:,.0f} KRW")
    print(f"손익: {position.profit_loss:+,.0f} KRW ({position.profit_loss_rate:+.2f}%)")
```

### get_orderbook

특정 종목의 호가를 조회합니다.

```python
def get_orderbook(self, ticker: str) -> Optional[Dict[str, Any]]:
    """
    Args:
        ticker (str): 티커
    
    Returns:
        Dict: 호가 정보
        None: 조회 실패 시
    """
```

**반환값 예시:**
```python
{
    'asks': [  # 매도호가 (낮은 가격 순)
        {'price': 70100, 'volume': 100},
        {'price': 70200, 'volume': 50}
    ],
    'bids': [  # 매수호가 (높은 가격 순)
        {'price': 70000, 'volume': 200},
        {'price': 69900, 'volume': 150}
    ]
}
```

### get_balance

계좌의 현금 잔고를 조회합니다.

```python
def get_balance(self) -> Optional[float]:
    """
    Returns:
        float: 현금 잔고 (KRW 단위)
        None: 조회 실패 시
    """
```

**예시:**
```python
balance = engine.get_balance()
print(f"현금 잔고: {balance:,.0f} KRW")
```

## 💳 거래 메서드

### buy_stock

주식을 매수합니다.

```python
def buy_stock(
    self,
    ticker: str,
    quantity: int,
    price: Optional[float] = None
) -> Optional[OrderResult]:
    """
    Args:
        ticker (str): 주식 코드
        quantity (int): 수량 (주)
        price (float, optional): 지정가. None이면 시장가
    
    Returns:
        OrderResult: 주문 결과
        None: 주문 실패 시
    
    Raises:
        InvalidTickerError: 유효하지 않은 티커
        APIConnectionError: API 연결 오류
    """
```

**예시:**
```python
# 시장가 주문
order = engine.buy_stock("005930", 10)

# 지정가 주문
order = engine.buy_stock("005930", 10, 70000)

if order:
    print(f"주문번호: {order.order_id}")
    print(f"상태: {order.status}")
```

### sell_stock

주식을 매도합니다.

```python
def sell_stock(
    self,
    ticker: str,
    quantity: int,
    price: Optional[float] = None
) -> Optional[OrderResult]:
    """
    Args:
        ticker (str): 주식 코드
        quantity (int): 수량 (주)
        price (float, optional): 지정가. None이면 시장가
    
    Returns:
        OrderResult: 주문 결과
        None: 주문 실패 시
    """
```

**예시:**
```python
# 시장가 매도
order = engine.sell_stock("005930", 5)

# 지정가 매도
order = engine.sell_stock("005930", 5, 75000)
```

### buy_coin

암호화폐를 매수합니다.

```python
def buy_coin(
    self,
    ticker: str,
    amount: float
) -> Optional[OrderResult]:
    """
    Args:
        ticker (str): 암호화폐 코드 (예: "KRW-BTC")
        amount (float): 매수 금액 (KRW)
    
    Returns:
        OrderResult: 주문 결과
        None: 주문 실패 시
    """
```

**예시:**
```python
# 100만원어치 비트코인 매수
order = engine.buy_coin("KRW-BTC", 1000000)

if order:
    print(f"주문번호: {order.order_id}")
    print(f"상태: {order.status}")
```

### sell_coin

암호화폐를 매도합니다.

```python
def sell_coin(
    self,
    ticker: str,
    amount: float
) -> Optional[OrderResult]:
    """
    Args:
        ticker (str): 암호화폐 코드
        amount (float): 매도 금액 (KRW)
    
    Returns:
        OrderResult: 주문 결과
        None: 주문 실패 시
    """
```

**예시:**
```python
# 모든 비트코인 매도 (금액 기준)
order = engine.sell_coin("KRW-BTC", 1000000)
```

## 📋 주문 관리 메서드

### cancel_order

주문을 취소합니다.

```python
def cancel_order(self, order_id: str) -> bool:
    """
    Args:
        order_id (str): 주문번호
    
    Returns:
        bool: 취소 성공 여부
    """
```

**예시:**
```python
order = engine.buy_stock("005930", 10, 70000)
if order:
    success = engine.cancel_order(order.order_id)
    if success:
        print("주문 취소됨")
```

### get_order_status

주문의 상태를 조회합니다.

```python
def get_order_status(self, order_id: str) -> Optional[str]:
    """
    Args:
        order_id (str): 주문번호
    
    Returns:
        str: 주문 상태 ('pending', 'filled', 'cancelled' 등)
        None: 조회 실패 시
    """
```

**예시:**
```python
status = engine.get_order_status("order123")
print(f"주문 상태: {status}")
```

### get_order_history

주문 이력을 조회합니다.

```python
def get_order_history(
    self,
    limit: int = 100,
    exchange: Optional[str] = None
) -> Optional[List[Order]]:
    """
    Args:
        limit (int): 조회 건수 (최대 1000)
        exchange (str, optional): 거래소 ('KIS', 'Upbit' 또는 None)
    
    Returns:
        List[Order]: 주문 이력
        None: 조회 실패 시
    """
```

**예시:**
```python
# 최근 50개 주문 조회
orders = engine.get_order_history(limit=50)

# KIS 주식 주문만 조회
orders = engine.get_order_history(exchange="KIS")

for order in orders:
    print(f"{order.timestamp}: {order.ticker} - {order.quantity}주 @ {order.price:,.0f}")
```

## 🏦 포트폴리오 메서드

### get_positions

모든 포지션을 조회합니다.

```python
def get_positions(self) -> Optional[List[Position]]:
    """
    Returns:
        List[Position]: 모든 포지션
        None: 조회 실패 시
    """
```

**예시:**
```python
positions = engine.get_positions()
if positions:
    for position in positions:
        print(f"{position.ticker}: {position.quantity} @ {position.current_price:,.0f}")
```

### get_portfolio_value

포트폴리오의 총액을 조회합니다.

```python
def get_portfolio_value(self) -> Optional[float]:
    """
    Returns:
        float: 포트폴리오 총액 (KRW)
        None: 조회 실패 시
    """
```

**예시:**
```python
total_value = engine.get_portfolio_value()
print(f"포트폴리오 총액: {total_value:,.0f} KRW")
```

## ⚙️ 세션 관리

### close

세션을 종료합니다. (with 문 사용 시 자동 호출)

```python
def close(self) -> None:
    """세션을 종료하고 리소스를 정리합니다."""
```

**예시:**
```python
engine = HybridTradingEngine(config)
try:
    price = engine.get_stock_price("005930")
finally:
    engine.close()  # 항상 정리
```

### 데이터 모델

#### OrderResult

```python
@dataclass
class OrderResult:
    order_id: str           # 주문번호
    ticker: str             # 티커
    side: str               # 'buy' 또는 'sell'
    quantity: float         # 수량
    price: float            # 가격
    timestamp: datetime     # 주문시간
    status: str             # 주문 상태
    message: Optional[str]  # 메시지
```

#### Order

```python
@dataclass
class Order:
    order_id: str
    ticker: str
    side: str
    quantity: float
    price: float
    timestamp: datetime
    status: str
    filled_quantity: float  # 체결수량
    remaining_quantity: float  # 미체결수량
```

---

## 📚 더 알아보기

- [Configuration API](config.md)
- [Monitoring API](monitoring.md)
- [Exceptions](exceptions.md)
- [예제 모음](../guide/examples.md)
