# 빠른 시작 (5분)

이 가이드는 Hybrid Trader를 5분 안에 시작하도록 도와줍니다.

## 1️⃣ 설치

```bash
pip install hybrid-trader
```

!!! note
    [상세 설치 가이드](installation.md)는 별도 문서를 참고하세요.

## 2️⃣ API 키 준비

다음 정보를 준비하세요:

**한국투자증권 (KIS)**
- `KIS_APP_KEY` - App Key
- `KIS_SECRET_KEY` - Secret Key
- `KIS_ACCOUNT` - 계좌번호 (예: 1234-5678)
- `KIS_HTS_ID` - HTS ID

**업비트 (Upbit)**
- `UPBIT_ACCESS_KEY` - Access Key
- `UPBIT_SECRET_KEY` - Secret Key

!!! warning
    API 키를 안전하게 보관하세요. [보안 가이드](installation.md#-보안-가이드)를 읽어보세요.

## 3️⃣ 첫 번째 코드 작성

### 기본 예제

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig
import os

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

# 트레이딩 엔진 초기화
config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
engine = HybridTradingEngine(config)

# 주식 가격 조회
samsung_price = engine.get_stock_price("005930")  # 삼성전자
print(f"삼성전자: {samsung_price:,.0f} KRW")

# 암호화폐 가격 조회
bitcoin_price = engine.get_coin_price("KRW-BTC")  # 비트코인
print(f"비트코인: {bitcoin_price:,.0f} KRW")

# 세션 정리
engine.close()
```

### Context Manager 사용 (권장)

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig
import os

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

config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)

# with 문으로 자동 세션 관리
with HybridTradingEngine(config) as engine:
    samsung_price = engine.get_stock_price("005930")
    bitcoin_price = engine.get_coin_price("KRW-BTC")
    print(f"삼성전자: {samsung_price:,.0f} KRW")
    print(f"비트코인: {bitcoin_price:,.0f} KRW")
    # 블록 종료 시 자동으로 세션이 정리됩니다
```

## 4️⃣ 코드 실행

### 방법 1: 직접 실행

```bash
python quickstart.py
```

### 방법 2: Python 대화형 모드

```bash
python

>>> from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig
>>> import os
>>> 
>>> kis_config = KISConfig(
...     app_key=os.getenv("KIS_APP_KEY"),
...     secret_key=os.getenv("KIS_SECRET_KEY"),
...     account_number=os.getenv("KIS_ACCOUNT"),
...     hts_id=os.getenv("KIS_HTS_ID"),
...     is_demo=True
... )
>>>
>>> upbit_config = UpbitConfig(
...     access_key=os.getenv("UPBIT_ACCESS_KEY"),
...     secret_key=os.getenv("UPBIT_SECRET_KEY")
... )
>>>
>>> config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
>>> engine = HybridTradingEngine(config)
>>> samsung_price = engine.get_stock_price("005930")
>>> print(samsung_price)
```

## 💡 다음 단계

축하합니다! 기본 설정을 완료했습니다.

### 추천 학습 경로

=== "실전 예제 배우기"

    [고급 예제](../guide/examples.md)를 통해:
    - 📈 주식 거래
    - 🪙 암호화폐 거래
    - 📊 포트폴리오 분석
    - 🎯 자동 거래 봇

=== "아키텍처 이해하기"

    [아키텍처 문서](../guide/architecture.md)를 읽고:
    - 📐 시스템 구조 이해
    - 🔄 데이터 흐름 파악
    - 🛠️ 확장 방법 학습

=== "완전한 API 문서"

    [API 레퍼런스](../api/overview.md)에서:
    - 📖 모든 메서드 확인
    - ⚙️ 고급 설정 학습
    - 🔧 커스터마이징

## 🎯 일반적인 작업

### 주식 가격 모니터링

```python
# 계속해서 가격 확인
import time

with HybridTradingEngine(config) as engine:
    for _ in range(5):
        price = engine.get_stock_price("005930")
        print(f"삼성전자: {price:,.0f} KRW")
        time.sleep(1)
```

### 암호화폐 다중 조회

```python
# 여러 암호화폐 한번에 조회
with HybridTradingEngine(config) as engine:
    cryptocurrencies = [
        ("KRW-BTC", "비트코인"),
        ("KRW-ETH", "이더리움"),
        ("KRW-XRP", "리플"),
    ]
    
    for ticker, name in cryptocurrencies:
        price = engine.get_coin_price(ticker)
        print(f"{name}: {price:,.0f} KRW")
```

### 포트폴리오 조회

```python
from hybrid_trader import PortfolioMonitor

with HybridTradingEngine(config) as engine:
    monitor = PortfolioMonitor(engine)
    
    # 포트폴리오 스냅샷 조회
    snapshot = monitor.get_portfolio_snapshot()
    print(f"총 자산: {snapshot.total_valuation:,.0f} KRW")
    print(f"평가손익: {snapshot.profit_loss:,.0f} KRW")
```

## ⚠️ 주의사항

- **테스트 모드**: 처음에는 `is_demo=True`로 테스트하세요
- **API 한도**: 각 플랫폼의 API 호출 한도를 확인하세요
- **네트워크**: 안정적인 인터넷 연결을 유지하세요
- **에러 처리**: 실제 거래 시 예외 처리를 꼭 추가하세요

## 🐛 문제 해결

### API 연결 오류

```
APIConnectionError: Failed to connect to API
```

**확인 사항:**
- API 키가 올바른지 확인
- 네트워크 연결 확인
- 테스트 모드(`is_demo=True`)로 시작

### 잘못된 환경변수

```
KeyError: 'KIS_APP_KEY'
```

**확인 사항:**
- 환경변수가 설정되었는지 확인: `echo $KIS_APP_KEY`
- `.env` 파일이 있는지 확인
- 파일명이 정확한지 확인

### 권한 부족

```
ConfigurationError: Missing required permissions
```

**확인 사항:**
- API 키에 필요한 권한이 있는지 확인
- 업비트 API 권한 설정 재확인

[더 많은 도움말은 FAQ를 참고하세요](../resources/faq.md)

## 📚 더 알아보기

- **[상세 설치 가이드](installation.md)** - 더 자세한 설치 과정
- **[고급 예제](../guide/examples.md)** - 실전 예제 모음
- **[API 레퍼런스](../api/overview.md)** - 전체 API 문서
- **[아키텍처](../guide/architecture.md)** - 시스템 구조

---

**도움이 필요하신가요?**

- 📝 [FAQ](../resources/faq.md) 읽기
- 🐛 [이슈 제보](https://github.com/YuMyeongJun/hybrid-trader/issues)
- 💬 [토론](https://github.com/YuMyeongJun/hybrid-trader/discussions)
