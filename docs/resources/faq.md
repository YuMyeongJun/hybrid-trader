# 자주 묻는 질문 (FAQ)

## 🚀 설치 및 시작

### Q: Hybrid Trader를 설치하려면 어떻게 해야 하나요?

**A:** pip를 사용하여 간단하게 설치할 수 있습니다:

```bash
pip install hybrid-trader
```

또는 GitHub에서 직접 설치:

```bash
git clone https://github.com/YuMyeongJun/hybrid-trader.git
cd hybrid-trader
pip install -r requirements.txt
```

[상세 설치 가이드](../getting-started/installation.md)를 참고하세요.

---

### Q: 설치 후 확인하려면?

**A:** Python에서 다음 코드를 실행하세요:

```python
import hybrid_trader
print(hybrid_trader.__version__)
```

또는 터미널에서:

```bash
python -c "import hybrid_trader; print(hybrid_trader.__version__)"
```

---

### Q: Python 버전이 맞는지 확인하려면?

**A:** Hybrid Trader는 Python 3.8 이상이 필요합니다:

```bash
python --version
```

Python 3.8 미만이면 업그레이드하세요.

---

## 🔑 API 키 및 설정

### Q: API 키를 어디서 발급받나요?

**A:**

**한국투자증권 (KIS):**
1. [한국투자증권 Developer Center](https://developers.trueinvesting.com) 방문
2. 회원가입 및 앱 등록
3. App Key, Secret Key 발급

**업비트 (Upbit):**
1. [업비트](https://upbit.com) 로그인
2. 계정 → [API 센터](https://upbit.com/api_center)
3. "새로운 API 키 생성" 클릭
4. Access Key, Secret Key 복사

---

### Q: API 키를 안전하게 보관하려면?

**A:** 환경변수를 사용하세요:

```bash
export KIS_APP_KEY="your_key"
export KIS_SECRET_KEY="your_secret"
export UPBIT_ACCESS_KEY="your_access_key"
export UPBIT_SECRET_KEY="your_secret_key"
```

또는 `.env` 파일 사용:

```python
from dotenv import load_dotenv
import os

load_dotenv()
app_key = os.getenv("KIS_APP_KEY")
```

**절대 코드에 하드코딩하지 마세요!**

---

### Q: 테스트 모드에서 시작하려면?

**A:** KISConfig의 `is_demo=True`로 설정하세요:

```python
kis_config = KISConfig(
    app_key="your_key",
    secret_key="your_secret",
    account_number="1234-5678",
    hts_id="your_hts_id",
    is_demo=True  # 테스트 모드
)
```

테스트 모드는 실제 거래 없이 API를 테스트할 수 있습니다.

---

## 💼 거래 및 기능

### Q: 주식과 암호화폐를 동시에 거래할 수 있나요?

**A:** 네, Hybrid Trader는 정확히 이 목적으로 설계되었습니다:

```python
with HybridTradingEngine(config) as engine:
    # 주식 거래
    stock_order = engine.buy_stock("005930", 10)
    
    # 암호화폐 거래
    crypto_order = engine.buy_coin("KRW-BTC", 1000000)
```

---

### Q: 포트폴리오를 조회하려면?

**A:** PortfolioMonitor를 사용하세요:

```python
from hybrid_trader import PortfolioMonitor

with HybridTradingEngine(config) as engine:
    monitor = PortfolioMonitor(engine)
    snapshot = monitor.get_portfolio_snapshot()
    
    print(f"총 자산: {snapshot.total_valuation:,.0f} KRW")
    print(f"수익률: {snapshot.profit_loss_rate:.2f}%")
```

---

### Q: 주문이 거부되었습니다. 왜요?

**A:** 일반적인 원인:

1. **잔고 부족**: 충분한 현금이 있는지 확인
2. **거래 시간 아님**: 주식은 평일 09:00~15:30만 거래 가능
3. **수량 부족**: 매도할 수량이 충분한지 확인
4. **권한 부족**: API 권한 설정 확인

[문제 해결 가이드](../guide/troubleshooting.md)를 참고하세요.

---

### Q: 시장가 주문과 지정가 주문의 차이는?

**A:**

**시장가 주문** (빠른 체결):
```python
order = engine.buy_stock("005930", 10)  # price 생략
```

**지정가 주문** (원하는 가격):
```python
order = engine.buy_stock("005930", 10, 70000)
```

---

## 📊 성능 및 최적화

### Q: API 호출 한도를 초과하면?

**A:** 거래소별 한도를 확인하세요:

- 한국투자증권: 초당 20회, 분당 500회
- 업비트: 초당 10회

한도 초과 시 대기 후 재시도하세요:

```python
import time

try:
    price = engine.get_stock_price("005930")
except APIConnectionError as e:
    if "rate limit" in str(e).lower():
        print("API 한도 초과. 60초 대기...")
        time.sleep(60)
        price = engine.get_stock_price("005930")
```

---

### Q: 프로그램이 느린 이유는?

**A:** 일반적인 원인과 해결책:

1. **수많은 순차 API 호출**
   ```python
   # ❌ 느림
   for ticker in tickers:
       price = engine.get_stock_price(ticker)
   
   # ✅ 빠름 (병렬)
   from concurrent.futures import ThreadPoolExecutor
   with ThreadPoolExecutor() as executor:
       prices = list(executor.map(engine.get_stock_price, tickers))
   ```

2. **캐싱 미사용**
   ```python
   # 같은 데이터를 여러 번 요청하지 마세요
   price1 = engine.get_stock_price("005930")
   price2 = engine.get_stock_price("005930")  # 중복
   ```

---

## 🐛 에러 및 문제

### Q: "ConfigurationError: Configuration validation failed" 에러가 나요.

**A:** API 키 설정을 확인하세요:

```python
# 확인 체크리스트
- KIS_APP_KEY: 설정됨? 비어있지 않음?
- KIS_SECRET_KEY: 설정됨? 비어있지 않음?
- KIS_ACCOUNT: 형식이 XXXX-XXXX인가?
- KIS_HTS_ID: 설정됨?
- UPBIT_ACCESS_KEY: 설정됨?
- UPBIT_SECRET_KEY: 설정됨?

# 환경변수 확인
import os
print(os.getenv("KIS_APP_KEY"))
```

---

### Q: "APIConnectionError: Connection timeout" 에러가 나요.

**A:** 네트워크 문제일 가능성이 높습니다:

1. **인터넷 연결 확인**
   ```python
   import requests
   requests.get('https://www.google.com', timeout=5)
   ```

2. **API 서버 상태 확인**
   - 한국투자증권: https://developers.trueinvesting.com
   - 업비트: https://upbit.com

3. **재시도 로직 추가**
   ```python
   import time
   for attempt in range(3):
       try:
           price = engine.get_stock_price("005930")
           break
       except APIConnectionError:
           time.sleep(2 ** attempt)
   ```

---

### Q: "InvalidTickerError" 에러가 나요.

**A:** 티커가 유효한지 확인하세요:

```python
# 주식: 6자리 숫자
engine.get_stock_price("005930")  # ✅ 맞음
engine.get_stock_price("KIS005930")  # ❌ 틀림

# 암호화폐: KRW-CODE
engine.get_coin_price("KRW-BTC")  # ✅ 맞음
engine.get_coin_price("BTC")  # ❌ 틀림
```

---

## 🌐 기술 질문

### Q: Hybrid Trader는 비동기 작업을 지원하나요?

**A:** 현재 버전은 동기식입니다. 비동기 작업이 필요하면:

```python
from concurrent.futures import ThreadPoolExecutor

def get_multiple_prices(tickers):
    with ThreadPoolExecutor(max_workers=5) as executor:
        return list(executor.map(engine.get_stock_price, tickers))
```

---

### Q: Context Manager를 반드시 사용해야 하나요?

**A:** 권장합니다. 더 안전합니다:

```python
# ✅ 권장
with HybridTradingEngine(config) as engine:
    price = engine.get_stock_price("005930")
# 자동 정리

# ❌ 수동 관리 (권장하지 않음)
engine = HybridTradingEngine(config)
price = engine.get_stock_price("005930")
engine.close()  # 잊기 쉬움
```

---

### Q: 여러 계좌를 관리할 수 있나요?

**A:** 각 계좌마다 별도의 엔진을 생성하세요:

```python
# 계좌 1
config1 = TradingConfig(
    kis_config=KISConfig(account_number="1111-1111", ...),
    upbit_config=UpbitConfig(...)
)
engine1 = HybridTradingEngine(config1)

# 계좌 2
config2 = TradingConfig(
    kis_config=KISConfig(account_number="2222-2222", ...),
    upbit_config=UpbitConfig(...)
)
engine2 = HybridTradingEngine(config2)
```

---

## 📚 학습 및 커뮤니티

### Q: 초보자입니다. 어디서 시작해야 하나요?

**A:** 다음 순서로 진행하세요:

1. [빠른 시작](../getting-started/quickstart.md) 읽기
2. [기본 예제](../guide/examples.md) 실행하기
3. [아키텍처](../guide/architecture.md) 이해하기
4. [API 레퍼런스](../api/overview.md) 확인하기

---

### Q: 더 많은 예제를 원합니다.

**A:** [실전 예제 모음](../guide/examples.md)을 확인하세요.

---

### Q: 문제를 해결할 수 없습니다.

**A:** 다음 순서로 시도하세요:

1. [문제 해결 가이드](../guide/troubleshooting.md) 확인
2. [GitHub Issues](https://github.com/YuMyeongJun/hybrid-trader/issues) 검색
3. 새 이슈 생성 (에러 메시지, Python 버전, 재현 코드 포함)
4. [GitHub Discussions](https://github.com/YuMyeongJun/hybrid-trader/discussions)에 질문

---

### Q: 기여하고 싶습니다.

**A:** [기여 가이드](contributing.md)를 참고하세요.

---

## ⚖️ 법적 및 위험 고지

### Q: Hybrid Trader를 사용해서 손실을 입으면 책임은?

**A:** Hybrid Trader는 MIT 라이선스 아래 "있는 그대로" 제공됩니다. **자동매매는 고위험 활동**입니다:

- 철저히 테스트하세요 (`is_demo=True`)
- 소량으로 시작하세요
- 손절/익절 설정을 하세요
- 자신의 책임 하에 사용하세요

---

### Q: 보안은 어떻게 보장하나요?

**A:** 개인적으로 확인해야 합니다:

- 코드는 오픈소스이므로 감시되고 있습니다
- API 키는 환경변수로 안전하게 관리하세요
- 정기적으로 API 키를 변경하세요
- IP 화이트리스트를 설정하세요

---

## 📞 추가 도움

문제가 해결되지 않으면:

- [문제 해결 가이드](../guide/troubleshooting.md)
- [GitHub Issues](https://github.com/YuMyeongJun/hybrid-trader/issues)
- [GitHub Discussions](https://github.com/YuMyeongJun/hybrid-trader/discussions)

---

**도움이 되었나요?** [이 문서 개선하기](https://github.com/YuMyeongJun/hybrid-trader)를 클릭하세요!
