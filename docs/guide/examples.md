# 실전 예제 모음

다양한 실전 코드 예제들을 소개합니다.

## 🎯 기본 예제

### 1. 간단한 가격 조회

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig
import os

# 설정
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

# 엔진 초기화
config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)

with HybridTradingEngine(config) as engine:
    # 주식 가격
    samsung_price = engine.get_stock_price("005930")
    print(f"삼성전자: {samsung_price:,.0f} KRW")
    
    # 암호화폐 가격
    bitcoin_price = engine.get_coin_price("KRW-BTC")
    print(f"비트코인: {bitcoin_price:,.0f} KRW")
```

## 📈 주식 거래 예제

### 2. 주식 가격 모니터링

```python
import time
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 설정
config = TradingConfig(
    kis_config=KISConfig(...),
    upbit_config=UpbitConfig(...)
)

# 가격 모니터링
with HybridTradingEngine(config) as engine:
    print("삼성전자 가격 모니터링 (5초 간격, 1분 동안)")
    
    start_time = time.time()
    while time.time() - start_time < 60:
        price = engine.get_stock_price("005930")
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] 삼성전자: {price:,.0f} KRW")
        time.sleep(5)
```

### 3. 지정가 매수/매도 봇

```python
import time
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

config = TradingConfig(
    kis_config=KISConfig(...),
    upbit_config=UpbitConfig(...)
)

BUY_PRICE = 70000      # 매수 가격
SELL_PRICE = 75000     # 매도 가격
QUANTITY = 10          # 거래량

with HybridTradingEngine(config) as engine:
    print("삼성전자 자동 거래 시작")
    print(f"매수: {BUY_PRICE:,.0f} KRW")
    print(f"매도: {SELL_PRICE:,.0f} KRW")
    
    position = False  # 포지션 보유 여부
    
    while True:
        price = engine.get_stock_price("005930")
        
        if not position and price <= BUY_PRICE:
            # 매수 주문
            order = engine.buy_stock("005930", QUANTITY, BUY_PRICE)
            if order:
                print(f"✓ 매수 완료: {QUANTITY}주 @ {BUY_PRICE:,.0f} KRW")
                position = True
        
        elif position and price >= SELL_PRICE:
            # 매도 주문
            order = engine.sell_stock("005930", QUANTITY, SELL_PRICE)
            if order:
                print(f"✓ 매도 완료: {QUANTITY}주 @ {SELL_PRICE:,.0f} KRW")
                position = False
        
        time.sleep(1)
```

## 🪙 암호화폐 거래 예제

### 4. 여러 암호화폐 모니터링

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig
import time

config = TradingConfig(
    kis_config=KISConfig(...),
    upbit_config=UpbitConfig(...)
)

CRYPTOCURRENCIES = [
    ("KRW-BTC", "비트코인"),
    ("KRW-ETH", "이더리움"),
    ("KRW-XRP", "리플"),
    ("KRW-ADA", "카르다노"),
]

with HybridTradingEngine(config) as engine:
    print("암호화폐 가격 조회 (1초 간격)")
    
    while True:
        print("\n" + "="*50)
        for ticker, name in CRYPTOCURRENCIES:
            price = engine.get_coin_price(ticker)
            if price:
                print(f"{name:10s}: {price:>15,.0f} KRW")
        
        time.sleep(1)
```

### 5. 암호화폐 자동 거래

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

config = TradingConfig(
    kis_config=KISConfig(...),
    upbit_config=UpbitConfig(...)
)

# 거래 설정
TARGET_TICKER = "KRW-BTC"
BUY_THRESHOLD = -2.0   # -2% 하락 시 매수
SELL_THRESHOLD = 2.0   # +2% 상승 시 매도
BUY_AMOUNT = 1000000   # 1백만원

prev_price = None

with HybridTradingEngine(config) as engine:
    while True:
        current_price = engine.get_coin_price(TARGET_TICKER)
        
        if prev_price is not None:
            price_change_rate = ((current_price - prev_price) / prev_price) * 100
            
            print(f"비트코인: {current_price:,.0f} KRW ({price_change_rate:+.2f}%)")
            
            if price_change_rate <= BUY_THRESHOLD:
                # 매수
                order = engine.buy_coin(TARGET_TICKER, BUY_AMOUNT)
                print(f"✓ 매수: {BUY_AMOUNT:,.0f} KRW")
            
            elif price_change_rate >= SELL_THRESHOLD:
                # 매도
                order = engine.sell_coin(TARGET_TICKER, BUY_AMOUNT)
                print(f"✓ 매도: {BUY_AMOUNT:,.0f} KRW")
        
        prev_price = current_price
        time.sleep(5)
```

## 📊 포트폴리오 분석

### 6. 포트폴리오 조회

```python
from hybrid_trader import HybridTradingEngine, PortfolioMonitor, TradingConfig, KISConfig, UpbitConfig

config = TradingConfig(
    kis_config=KISConfig(...),
    upbit_config=UpbitConfig(...)
)

with HybridTradingEngine(config) as engine:
    monitor = PortfolioMonitor(engine)
    
    # 포트폴리오 스냅샷
    snapshot = monitor.get_portfolio_snapshot()
    
    print(f"총 자산: {snapshot.total_valuation:,.0f} KRW")
    print(f"평가손익: {snapshot.profit_loss:,.0f} KRW")
    print(f"수익률: {snapshot.profit_loss_rate:.2f}%")
    
    # 보유 포지션 목록
    for position in snapshot.positions:
        print(f"\n{position.name}:")
        print(f"  수량: {position.quantity}")
        print(f"  평가액: {position.valuation:,.0f} KRW")
        print(f"  손익: {position.profit_loss:+,.0f} KRW ({position.profit_loss_rate:+.2f}%)")
```

### 7. 포트폴리오 성능 분석

```python
from hybrid_trader import HybridTradingEngine, PortfolioMonitor, TradingConfig, KISConfig, UpbitConfig
import time
from datetime import datetime

config = TradingConfig(
    kis_config=KISConfig(...),
    upbit_config=UpbitConfig(...)
)

# 성능 기록
performance_log = []

with HybridTradingEngine(config) as engine:
    monitor = PortfolioMonitor(engine)
    
    print("포트폴리오 성능 추적 (1시간 동안 10분마다)")
    
    for i in range(6):  # 6회 (10분마다)
        snapshot = monitor.get_portfolio_snapshot()
        
        log_entry = {
            'timestamp': datetime.now(),
            'total_valuation': snapshot.total_valuation,
            'profit_loss': snapshot.profit_loss,
            'profit_loss_rate': snapshot.profit_loss_rate,
        }
        performance_log.append(log_entry)
        
        print(f"\n[{log_entry['timestamp'].strftime('%H:%M:%S')}]")
        print(f"  총 자산: {snapshot.total_valuation:,.0f} KRW")
        print(f"  수익률: {snapshot.profit_loss_rate:.2f}%")
        
        if i < 5:
            time.sleep(600)  # 10분 대기
    
    # 변화 분석
    first = performance_log[0]
    last = performance_log[-1]
    
    print(f"\n=== 1시간 성능 요약 ===")
    print(f"시작 시점: {first['total_valuation']:,.0f} KRW")
    print(f"종료 시점: {last['total_valuation']:,.0f} KRW")
    print(f"변화: {last['profit_loss_rate'] - first['profit_loss_rate']:+.2f}%")
```

## 🔔 실시간 모니터링

### 8. 가격 변동 알림

```python
from hybrid_trader import HybridTradingEngine, PriceMonitor, PriceAlert, TradingConfig, KISConfig, UpbitConfig
import time

config = TradingConfig(
    kis_config=KISConfig(...),
    upbit_config=UpbitConfig(...)
)

with HybridTradingEngine(config) as engine:
    monitor = PriceMonitor(engine)
    
    # 알림 설정
    alerts = [
        PriceAlert(ticker="005930", alert_type="above", threshold=80000),  # 8만원 이상
        PriceAlert(ticker="005930", alert_type="below", threshold=60000),  # 6만원 이하
        PriceAlert(ticker="KRW-BTC", alert_type="change", threshold=3.0),  # 3% 변화
    ]
    
    print("가격 변동 모니터링 시작")
    
    for _ in range(60):  # 1분간 모니터링
        time.sleep(1)
        
        for alert in alerts:
            triggered = monitor.check_alert(alert)
            if triggered:
                print(f"🔔 알림: {alert.ticker} - {alert.alert_type} {alert.threshold}")
```

## 🛡️ 에러 처리

### 9. 안전한 거래

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig
from hybrid_trader.exceptions import (
    HybridTraderException,
    InvalidTickerError,
    APIConnectionError,
    ConfigurationError
)

config = TradingConfig(
    kis_config=KISConfig(...),
    upbit_config=UpbitConfig(...)
)

try:
    with HybridTradingEngine(config) as engine:
        try:
            price = engine.get_stock_price("999999")  # 존재하지 않는 티커
        except InvalidTickerError as e:
            print(f"유효하지 않은 티커: {e}")
        
        try:
            price = engine.get_coin_price("KRW-INVALID")
        except APIConnectionError as e:
            print(f"API 연결 오류: {e}")
        
        # 안전한 거래
        try:
            order = engine.buy_stock("005930", 10)
            print("거래 성공")
        except Exception as e:
            print(f"거래 실패: {e}")

except ConfigurationError as e:
    print(f"설정 오류: {e}")
except HybridTraderException as e:
    print(f"Hybrid Trader 오류: {e}")
```

## 📝 로깅과 디버깅

### 10. 상세 로깅

```python
import logging
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 특정 모듈 로깅
logger = logging.getLogger('hybrid_trader.engine')
logger.setLevel(logging.DEBUG)

config = TradingConfig(
    kis_config=KISConfig(...),
    upbit_config=UpbitConfig(...)
)

with HybridTradingEngine(config) as engine:
    # 디버그 정보와 함께 실행
    price = engine.get_stock_price("005930")
    print(f"삼성전자: {price:,.0f} KRW")
```

---

## 📚 더 알아보기

- [아키텍처](architecture.md) - 시스템 구조 이해
- [설정 가이드](configuration.md) - 고급 설정
- [문제 해결](troubleshooting.md) - 일반적인 문제 해결
- [API 레퍼런스](../api/overview.md) - 전체 API 문서

---

**더 많은 예제가 필요하신가요?** [GitHub Discussions](https://github.com/YuMyeongJun/hybrid-trader/discussions)에서 질문하세요!
