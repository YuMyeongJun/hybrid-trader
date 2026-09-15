# 문제 해결 가이드

일반적인 문제와 해결 방법을 소개합니다.

## 🔧 설치 및 설정 문제

### 문제 1: ModuleNotFoundError: No module named 'hybrid_trader'

**증상:**
```
ModuleNotFoundError: No module named 'hybrid_trader'
```

**원인:**
- Hybrid Trader가 설치되지 않음
- 잘못된 Python 환경 사용

**해결책:**

```bash
# 1. 설치 확인
python -c "import hybrid_trader; print(hybrid_trader.__version__)"

# 2. 새로 설치
pip install hybrid-trader

# 3. 또는 로컬 개발 환경
git clone https://github.com/YuMyeongJun/hybrid-trader.git
cd hybrid-trader
pip install -e .
```

### 문제 2: Python 버전 오류

**증상:**
```
ERROR: hybrid-trader requires Python >=3.8
```

**해결책:**

```bash
# Python 버전 확인
python --version

# Python 3.8 이상으로 업그레이드
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt-get install python3.11

# Windows
# https://www.python.org/downloads/에서 다운로드
```

### 문제 3: API 키 누락

**증상:**
```
ConfigurationError: Configuration validation failed: 'KIS_APP_KEY'
```

**해결책:**

```bash
# 환경변수 확인
echo $KIS_APP_KEY

# 환경변수 설정 (임시)
export KIS_APP_KEY="your_key"

# 환경변수 설정 (영구)
# macOS/Linux
echo 'export KIS_APP_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc

# Windows (PowerShell)
[Environment]::SetEnvironmentVariable("KIS_APP_KEY", "your_key", "User")
$env:KIS_APP_KEY="your_key"
```

### 문제 4: 의존성 충돌

**증상:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**해결책:**

```bash
# 의존성 업그레이드
pip install --upgrade pip setuptools wheel

# 패키지 재설치
pip uninstall hybrid-trader -y
pip install hybrid-trader

# 또는 가상환경 재생성
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
pip install hybrid-trader
```

## 🔑 API 및 인증 문제

### 문제 5: 유효하지 않은 API 키

**증상:**
```
APIConnectionError: Invalid API key or secret
```

**해결책:**

```python
# 1. API 키 확인
import os
print(f"KIS_APP_KEY: {os.getenv('KIS_APP_KEY')}")
print(f"KIS_SECRET_KEY: {os.getenv('KIS_SECRET_KEY')}")

# 2. API 센터에서 새 키 발급
# - 한국투자증권: https://developers.trueinvesting.com
# - 업비트: https://upbit.com/api_center

# 3. 테스트 모드로 확인
kis_config = KISConfig(
    app_key="your_key",
    secret_key="your_secret",
    account_number="account",
    hts_id="hts_id",
    is_demo=True  # 테스트 모드
)
```

### 문제 6: 권한 부족

**증상:**
```
ConfigurationError: Missing required permissions
```

**해결책:**

```
1. API 센터 접속
2. API 키 권한 설정 확인
3. 필요한 권한 활성화:
   - 캔들 (조회)
   - 주문 (매수/매도)
   - 계좌 (포지션, 잔고 조회)
4. 변경사항 저장
5. 변경 후 잠시 대기 (보통 5-10분)
```

### 문제 7: IP 화이트리스트 오류

**증상:**
```
APIConnectionError: IP address not whitelisted
```

**해결책:**

```
업비트의 경우:
1. 업비트 로그인
2. API 센터 → API 키 관리
3. IP 화이트리스트 설정
4. 현재 IP 주소 확인: https://www.myip.com
5. 화이트리스트에 추가
6. 또는 화이트리스트 비활성화 (보안 주의)
```

## 🌐 네트워크 및 연결 문제

### 문제 8: 인터넷 연결 끊김

**증상:**
```
APIConnectionError: Connection timeout
```

**해결책:**

```python
# 1. 인터넷 연결 확인
import requests
try:
    requests.get('https://www.google.com', timeout=5)
    print("인터넷 연결됨")
except:
    print("인터넷 연결 안됨")

# 2. 타임아웃 시간 설정
# (라이브러리에서 지원하는 경우)

# 3. 재시도 로직 추가
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        price = engine.get_stock_price("005930")
        break
    except APIConnectionError:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"{wait_time}초 후 재시도...")
            time.sleep(wait_time)
        else:
            raise
```

### 문제 9: API 응답 시간 초과

**증상:**
```
APIConnectionError: Request timeout
```

**해결책:**

```python
# 1. 네트워크 속도 확인
# https://www.speedtest.net

# 2. VPN 사용 (ISP 제한인 경우)
# 일부 ISP가 암호화폐 거래소 트래픽을 차단할 수 있음

# 3. DNS 변경
# 8.8.8.8 (Google) 또는 1.1.1.1 (Cloudflare)

# 4. 요청 간격 조정
import time
time.sleep(1)  # 1초 대기 후 다시 시도
```

### 문제 10: API 호출 한도 초과

**증상:**
```
APIConnectionError: Rate limit exceeded
```

**해결책:**

```python
# 1. 요청 빈도 줄이기
import time

requests_made = 0
requests_per_minute = 100

while True:
    price = engine.get_stock_price("005930")
    requests_made += 1
    
    if requests_made >= requests_per_minute:
        print("API 한도에 도달했습니다. 60초 대기...")
        time.sleep(60)
        requests_made = 0
    else:
        time.sleep(0.6)  # 최소 대기 시간

# 2. 각 거래소의 한도 확인
# 한국투자증권: https://developers.trueinvesting.com/api-docs
# 업비트: https://docs.upbit.com/guide/quotation-apikey
```

## 🐛 거래 관련 문제

### 문제 11: 주문이 거부됨

**증상:**
```
Order rejected: Insufficient balance
```

**해결책:**

```python
# 1. 잔고 확인
portfolio = monitor.get_portfolio_snapshot()
print(f"현금 잔고: {portfolio.cash_balance:,.0f} KRW")

# 2. 주문 가능 금액 확인
order_amount = engine.get_orderable_amount("005930")
print(f"주문 가능 금액: {order_amount:,.0f} KRW")

# 3. 테스트 모드에서 테스트
kis_config = KISConfig(..., is_demo=True)
```

### 문제 12: 매도 주문 실패

**증상:**
```
Order rejected: Not enough quantity to sell
```

**해결책:**

```python
# 1. 보유 수량 확인
position = engine.get_position("005930")
if position:
    print(f"보유 수량: {position.quantity}주")
else:
    print("해당 종목을 보유하지 않음")

# 2. 매도 가능 수량 확인
sellable_qty = engine.get_sellable_quantity("005930")
print(f"매도 가능 수량: {sellable_qty}주")

# 3. 정정/취소 후 재주문
engine.cancel_order(order_id)
time.sleep(1)
engine.sell_stock("005930", qty)
```

### 문제 13: 지정가 주문이 체결되지 않음

**증상:**
```
Order placed but not filled
```

**해결책:**

```python
# 1. 호가 정보 확인
orderbook = engine.get_orderbook("005930")
print(f"매도호가: {orderbook['asks'][0]}")
print(f"매수호가: {orderbook['bids'][0]}")

# 2. 주문 상태 확인
order_status = engine.get_order_status(order_id)
print(f"상태: {order_status['status']}")  # pending, filled, cancelled

# 3. 지정가 조정
# 더 유리한 가격으로 수정
current_price = engine.get_stock_price("005930")
buy_price = current_price * 0.99  # 현재가 1% 할인
order = engine.buy_stock("005930", qty, buy_price)

# 4. 시간가 주문 사용
# (거래소에서 지원하는 경우)
order = engine.buy_stock("005930", qty)  # 시장가 주문
```

## 📊 모니터링 및 분석 문제

### 문제 14: 데이터 조회가 느림

**증상:**
```
Program hangs or responds slowly
```

**해결책:**

```python
# 1. 병렬 요청 사용
from concurrent.futures import ThreadPoolExecutor

tickers = ["005930", "000660", "005380"]

with ThreadPoolExecutor(max_workers=3) as executor:
    prices = list(executor.map(engine.get_stock_price, tickers))

# 2. 캐싱 추가
cache = {}

def get_cached_price(ticker, cache_timeout=5):
    if ticker in cache:
        cached_time, price = cache[ticker]
        if time.time() - cached_time < cache_timeout:
            return price
    
    price = engine.get_stock_price(ticker)
    cache[ticker] = (time.time(), price)
    return price

# 3. 배치 조회 (지원하는 경우)
prices = engine.get_batch_stock_prices(["005930", "000660", "005380"])
```

### 문제 15: 포트폴리오 계산이 부정확함

**증상:**
```
Portfolio valuation does not match expected value
```

**해결책:**

```python
# 1. 환율 확인 (필요한 경우)
krw_usd_rate = engine.get_exchange_rate("KRW/USD")

# 2. 거래비 포함 여부 확인
# 거래비가 계산에 포함되는지 확인

# 3. 정산 기준일 확인
# 주식과 암호화폐의 정산 기준이 다를 수 있음

# 4. 수동 계산으로 검증
total = 0
for position in portfolio.positions:
    position_value = position.current_price * position.quantity
    total += position_value
print(f"계산된 총액: {total:,.0f} KRW")
print(f"API 반환값: {portfolio.total_valuation:,.0f} KRW")
```

## 📝 로깅과 디버깅

### 문제 16: 에러 메시지가 불명확함

**해결책:**

```python
# 1. 로깅 활성화
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 2. 커스텀 로깅
logger = logging.getLogger(__name__)

try:
    price = engine.get_stock_price("005930")
except Exception as e:
    logger.exception("주식 가격 조회 실패")
    logger.debug(f"요청한 티커: 005930")
    raise

# 3. 스택 트레이스 출력
import traceback

try:
    price = engine.get_stock_price("999999")
except Exception as e:
    traceback.print_exc()
```

## 🆘 추가 지원

### 문제가 해결되지 않으면:

1. **[FAQ](../resources/faq.md)** 확인
2. **[GitHub Issues](https://github.com/YuMyeongJun/hybrid-trader/issues)** 검색
3. **새 이슈 생성**: 다음 정보 포함
   - 에러 메시지 및 스택 트레이스
   - Python 버전
   - 설치 방법
   - 최소 재현 코드
4. **[GitHub Discussions](https://github.com/YuMyeongJun/hybrid-trader/discussions)** 질문

---

## 🎓 일반적인 조언

- **테스트 모드부터 시작**: `is_demo=True`로 충분히 테스트하세요
- **로그를 기록하세요**: 문제 해결에 도움이 됩니다
- **API 문서 확인**: 각 거래소의 공식 문서를 참고하세요
- **커뮤니티에 참여**: 다른 사용자의 경험을 배우세요

---

**도움이 되었나요?** [더 알아보기](../resources/faq.md)
