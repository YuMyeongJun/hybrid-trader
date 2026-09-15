# Monitoring API

실시간 모니터링 도구들입니다.

## 클래스: PriceMonitor

가격을 실시간으로 모니터링합니다.

```python
from hybrid_trader import PriceMonitor, HybridTradingEngine

monitor = PriceMonitor(engine: HybridTradingEngine)
```

### get_latest_price

최신 가격을 조회합니다.

```python
def get_latest_price(self, ticker: str) -> Optional[float]:
    """
    Args:
        ticker (str): 티커
    
    Returns:
        float: 최신 가격
        None: 조회 실패 시
    """
```

**예시:**
```python
with HybridTradingEngine(config) as engine:
    monitor = PriceMonitor(engine)
    
    # 최신 주식 가격
    stock_price = monitor.get_latest_price("005930")
    
    # 최신 암호화폐 가격
    crypto_price = monitor.get_latest_price("KRW-BTC")
```

### add_alert

가격 변동 알림을 추가합니다.

```python
def add_alert(self, alert: PriceAlert) -> bool:
    """
    Args:
        alert (PriceAlert): 알림 설정
    
    Returns:
        bool: 성공 여부
    """
```

**예시:**
```python
alert = PriceAlert(
    ticker="005930",
    alert_type="above",  # above, below, change
    threshold=80000      # 8만원 이상
)
monitor.add_alert(alert)
```

### check_alerts

모든 알림을 확인합니다.

```python
def check_alerts(self) -> List[PriceAlert]:
    """
    Returns:
        List[PriceAlert]: 트리거된 알림 목록
    """
```

**예시:**
```python
triggered = monitor.check_alerts()
for alert in triggered:
    print(f"알림: {alert.ticker} - {alert.alert_type}")
```

### get_price_history

가격 이력을 조회합니다.

```python
def get_price_history(
    self,
    ticker: str,
    period: int = 100
) -> Optional[List[PriceSnapshot]]:
    """
    Args:
        ticker (str): 티커
        period (int): 조회 기간 (기본값: 100)
    
    Returns:
        List[PriceSnapshot]: 가격 이력
        None: 조회 실패 시
    """
```

**예시:**
```python
history = monitor.get_price_history("005930", period=60)
for snapshot in history:
    print(f"{snapshot.timestamp}: {snapshot.price:,.0f} KRW")
```

---

## 클래스: PortfolioMonitor

포트폴리오를 모니터링합니다.

```python
from hybrid_trader import PortfolioMonitor, HybridTradingEngine

monitor = PortfolioMonitor(engine: HybridTradingEngine)
```

### get_portfolio_snapshot

현재 포트폴리오 상태를 조회합니다.

```python
def get_portfolio_snapshot(self) -> Optional[PortfolioSnapshot]:
    """
    Returns:
        PortfolioSnapshot: 포트폴리오 스냅샷
        None: 조회 실패 시
    """
```

**반환값:**
```python
@dataclass
class PortfolioSnapshot:
    total_valuation: float      # 총 자산가
    cash_balance: float         # 현금
    profit_loss: float          # 평가손익
    profit_loss_rate: float     # 수익률 (%)
    positions: List[Position]   # 보유 포지션
    timestamp: datetime         # 조회 시간
```

**예시:**
```python
snapshot = monitor.get_portfolio_snapshot()
print(f"총 자산: {snapshot.total_valuation:,.0f} KRW")
print(f"수익률: {snapshot.profit_loss_rate:.2f}%")

for position in snapshot.positions:
    print(f"{position.ticker}: {position.profit_loss_rate:+.2f}%")
```

### get_position_snapshot

특정 포지션의 상태를 조회합니다.

```python
def get_position_snapshot(self, ticker: str) -> Optional[PositionSnapshot]:
    """
    Args:
        ticker (str): 티커
    
    Returns:
        PositionSnapshot: 포지션 스냅샷
        None: 조회 실패 시
    """
```

**예시:**
```python
position = monitor.get_position_snapshot("005930")
if position:
    print(f"보유: {position.quantity}주")
    print(f"평가액: {position.valuation:,.0f} KRW")
    print(f"손익: {position.profit_loss:+,.0f} KRW")
```

### track_performance

성능을 추적합니다.

```python
def track_performance(self, interval: int = 60) -> None:
    """
    Args:
        interval (int): 추적 간격 (초)
    """
```

**예시:**
```python
# 1분마다 포트폴리오를 추적
monitor.track_performance(interval=60)
```

### get_performance_history

성능 이력을 조회합니다.

```python
def get_performance_history(self) -> List[PortfolioSnapshot]:
    """
    Returns:
        List[PortfolioSnapshot]: 성능 이력
    """
```

**예시:**
```python
history = monitor.get_performance_history()
for snapshot in history:
    print(f"{snapshot.timestamp}: 수익률 {snapshot.profit_loss_rate:.2f}%")
```

---

## 클래스: PriceAlert

가격 변동 알림 설정입니다.

```python
@dataclass
class PriceAlert:
    ticker: str        # 티커
    alert_type: str    # 'above', 'below', 'change'
    threshold: float   # 임계값
    name: str = ""     # 알림 이름
    enabled: bool = True  # 활성화 여부
```

### 알림 타입

| 타입 | 설명 | 예시 |
|------|------|------|
| `above` | 지정가 이상 | threshold=80000 (8만원 이상) |
| `below` | 지정가 이하 | threshold=60000 (6만원 이하) |
| `change` | 변화율 | threshold=3.0 (3% 변화) |

### 예시

```python
from hybrid_trader import PriceAlert

# 가격이 8만원 이상일 때
alert1 = PriceAlert(
    ticker="005930",
    alert_type="above",
    threshold=80000,
    name="삼성 고가 알림"
)

# 가격이 6만원 이하일 때
alert2 = PriceAlert(
    ticker="005930",
    alert_type="below",
    threshold=60000,
    name="삼성 저가 알림"
)

# 가격이 3% 이상 변했을 때
alert3 = PriceAlert(
    ticker="KRW-BTC",
    alert_type="change",
    threshold=3.0,
    name="비트코인 변동 알림"
)

monitor.add_alert(alert1)
monitor.add_alert(alert2)
monitor.add_alert(alert3)
```

---

## 클래스: PriceSnapshot

가격 스냅샷입니다.

```python
@dataclass
class PriceSnapshot:
    timestamp: datetime  # 시간
    ticker: str         # 티커
    price: float        # 가격
    volume: float       # 거래량
    change: float       # 가격 변화율
    high: float         # 고가
    low: float          # 저가
```

---

## 📊 모니터링 예제

### 예제 1: 실시간 가격 모니터링

```python
from hybrid_trader import PriceMonitor, HybridTradingEngine
import time

with HybridTradingEngine(config) as engine:
    monitor = PriceMonitor(engine)
    
    print("가격 모니터링 시작 (1분)")
    
    for _ in range(60):
        stock_price = monitor.get_latest_price("005930")
        crypto_price = monitor.get_latest_price("KRW-BTC")
        
        print(f"삼성전자: {stock_price:,.0f} KRW, 비트코인: {crypto_price:,.0f} KRW")
        time.sleep(1)
```

### 예제 2: 포트폴리오 모니터링

```python
from hybrid_trader import PortfolioMonitor, HybridTradingEngine
import time

with HybridTradingEngine(config) as engine:
    monitor = PortfolioMonitor(engine)
    
    print("포트폴리오 모니터링 시작 (10분간 1분 간격)")
    
    for i in range(10):
        snapshot = monitor.get_portfolio_snapshot()
        
        print(f"\n[{i+1}분]")
        print(f"총 자산: {snapshot.total_valuation:,.0f} KRW")
        print(f"평가손익: {snapshot.profit_loss:+,.0f} KRW")
        print(f"수익률: {snapshot.profit_loss_rate:+.2f}%")
        
        if i < 9:
            time.sleep(60)  # 1분 대기
```

### 예제 3: 가격 알림

```python
from hybrid_trader import PriceMonitor, PriceAlert, HybridTradingEngine
import time

with HybridTradingEngine(config) as engine:
    monitor = PriceMonitor(engine)
    
    # 알림 설정
    monitor.add_alert(PriceAlert(
        ticker="005930",
        alert_type="above",
        threshold=80000
    ))
    
    monitor.add_alert(PriceAlert(
        ticker="005930",
        alert_type="below",
        threshold=60000
    ))
    
    print("가격 알림 모니터링 시작")
    
    while True:
        triggered = monitor.check_alerts()
        
        for alert in triggered:
            price = monitor.get_latest_price(alert.ticker)
            print(f"🔔 알림: {alert.ticker} - {alert.alert_type} {alert.threshold} (현재가: {price:,.0f})")
        
        time.sleep(5)
```

---

## 📚 더 알아보기

- [Engine API](engine.md)
- [예제 모음](../guide/examples.md)
- [문제 해결](../guide/troubleshooting.md)
