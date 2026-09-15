# 문제 해결 가이드 (Troubleshooting Guide)

Hybrid Trader 사용 중 발생하는 일반적인 문제와 해결 방법을 설명합니다.

## 목차

- [설치 관련](#설치-관련)
- [API 연결 문제](#api-연결-문제)
- [인증 오류](#인증-오류)
- [데이터 조회 문제](#데이터-조회-문제)
- [성능 문제](#성능-문제)
- [환경 변수 문제](#환경-변수-문제)
- [테스트 실패](#테스트-실패)
- [자주 묻는 질문 (FAQ)](#자주-묻는-질문-faq)

---

## 설치 관련

### 문제: "No module named 'hybrid_trader'"

**증상**: 
```
ModuleNotFoundError: No module named 'hybrid_trader'
```

**원인**:
- 패키지가 설치되지 않았음
- 가상 환경이 활성화되지 않음
- 잘못된 Python 환경

**해결책**:

1. 가상 환경 활성화 확인:
```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 확인: 프롬프트에 (venv) 표시 여부
```

2. 패키지 재설치:
```bash
pip install -e .

# 또는
pip install -r requirements.txt
```

3. 설치 확인:
```bash
python -c "import hybrid_trader; print(hybrid_trader.__version__)"
```

---

### 문제: "No module named 'python-kis'"

**증상**:
```
ImportError: No module named 'kis'
또는
ImportError: python-kis is required. Install with: pip install python-kis
```

**원인**:
- python-kis 라이브러리가 설치되지 않음
- 가상 환경에 설치되지 않음

**해결책**:

```bash
# 라이브러리 설치
pip install python-kis>=0.3.0

# 버전 확인
pip show python-kis
```

---

### 문제: "No module named 'pyupbit'"

**증상**:
```
ImportError: No module named 'pyupbit'
또는
ImportError: pyupbit is required. Install with: pip install pyupbit
```

**원인**:
- pyupbit 라이브러리가 설치되지 않음

**해결책**:

```bash
# 라이브러리 설치
pip install pyupbit>=0.2.35

# 또는 전체 의존성 재설치
pip install -r requirements.txt
```

---

### 문제: Python 버전이 맞지 않음

**증상**:
```
ERROR: hybrid-trader requires Python >=3.8
```

**원인**:
- Python 3.8 미만의 버전 사용

**해결책**:

1. Python 버전 확인:
```bash
python --version
```

2. Python 3.8 이상 설치:
   - Windows: [python.org](https://www.python.org/downloads/)에서 다운로드
   - macOS: `brew install python@3.11`
   - Linux: `sudo apt-get install python3.10`

3. 올바른 Python으로 다시 설치:
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## API 연결 문제

### 문제: "Connection refused"

**증상**:
```
ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**원인**:
- 인터넷 연결 불안정
- API 서버 다운
- 방화벽이 연결 차단

**해결책**:

1. 인터넷 연결 확인:
```bash
# Windows
ping google.com

# macOS / Linux
ping google.com
```

2. 각 플랫폼 상태 확인:
   - 한국투자증권: https://developers.trueinvesting.com
   - 업비트: https://upbit.com

3. 방화벽 설정 확인:
   - Windows: 방화벽 설정 > 앱 허용
   - macOS: 시스템 설정 > 보안 및 개인정보 보호
   - Linux: `sudo ufw status`

---

### 문제: "Connection timeout"

**증상**:
```
TimeoutError: ('Connection aborted.', socket.timeout('timed out'))
```

**원인**:
- 네트워크 지연
- API 응답 시간이 너무 김
- 타임아웃 설정이 너무 짧음

**해결책**:

1. 네트워크 상태 확인:
```bash
# 인터넷 속도 테스트
# 또는 다른 API 서비스 접근 시도
curl https://api.upbit.com/api/v1/ticker
```

2. 타임아웃 설정 증가:
```python
from hybrid_trader import TradingConfig, HybridTradingEngine

config = TradingConfig(
    kis_config=kis_cfg,
    upbit_config=upbit_cfg,
    timeout=30  # 기본값: 10초, 30초로 증가
)

engine = HybridTradingEngine(config)
```

3. 재시도 횟수 증가:
```python
config = TradingConfig(
    kis_config=kis_cfg,
    upbit_config=upbit_cfg,
    retry_count=5  # 기본값: 3, 5회로 증가
)
```

---

### 문제: "ERR_NETWORK_CHANGED"

**증상**:
```
requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**원인**:
- 네트워크 변경 (WiFi → 모바일 등)
- VPN 연결 해제
- DNS 문제

**해결책**:

1. 안정적인 네트워크로 전환
2. VPN 사용 중이면 끄고 다시 시도
3. DNS 확인:
```bash
# Windows
ipconfig /all

# macOS / Linux
cat /etc/resolv.conf
```

---

## 인증 오류

### 문제: "Missing required credentials"

**증상**:
```
ValueError: Missing required credentials: KIS app_key, KIS secret_key, ...
```

**원인**:
- API 키가 설정되지 않음
- 환경변수가 제대로 설정되지 않음
- 설정값이 빈 문자열

**해결책**:

1. 모든 필수 키 확인:
```python
import os

required_keys = [
    "KIS_APP_KEY",
    "KIS_SECRET_KEY",
    "KIS_ACCOUNT",
    "KIS_HTS_ID",
    "UPBIT_ACCESS_KEY",
    "UPBIT_SECRET_KEY"
]

for key in required_keys:
    value = os.getenv(key)
    print(f"{key}: {'OK' if value else 'MISSING'}")
```

2. 환경변수 재설정:
```bash
# macOS / Linux
export KIS_APP_KEY="your_key"
export KIS_SECRET_KEY="your_secret"
export KIS_ACCOUNT="1234-5678"
export KIS_HTS_ID="your_hts_id"
export UPBIT_ACCESS_KEY="your_access_key"
export UPBIT_SECRET_KEY="your_secret_key"

# 확인
echo $KIS_APP_KEY
```

3. 코드에서 직접 확인:
```python
from hybrid_trader import TradingConfig, KISConfig, UpbitConfig

kis_config = KISConfig(
    app_key="test_key",
    secret_key="test_secret",
    account_number="1234-5678",
    hts_id="test_hts"
)

print(f"app_key: {kis_config.app_key}")
print(f"secret_key: {kis_config.secret_key}")
```

---

### 문제: "Invalid API key"

**증상**:
```
APIError: 401 Unauthorized
또는
403 Forbidden
```

**원인**:
- API 키가 잘못됨
- API 키 형식이 잘못됨
- API 키가 만료됨
- API 키의 권한 부족

**해결책**:

1. API 키 재확인:
   - 한국투자증권: [Developer Center](https://developers.trueinvesting.com)
   - 업비트: [API 센터](https://upbit.com/api_center)

2. 키 복사 시 공백 제거:
```python
# 잘못된 경우
app_key = "your_app_key " # 뒤에 공백

# 올바른 경우
app_key = "your_app_key".strip()
```

3. 환경변수에서 로드할 때 확인:
```python
import os

app_key = os.getenv("KIS_APP_KEY", "").strip()
if not app_key:
    raise ValueError("KIS_APP_KEY 환경변수가 설정되지 않았습니다")
```

---

### 문제: "Permission denied"

**증상**:
```
PermissionError
또는
403 Forbidden
```

**원인**:
- API 권한 부족
- 거래 권한 없음
- IP 화이트리스트 설정 문제

**해결책**:

1. 업비트 권한 확인:
   - 마이페이지 > 개발자 센터 > API Key 관리
   - "조회" 권한은 필수
   - "주문" 권한은 거래 기능 필요 시 필수

2. 한국투자증권 권한 확인:
   - Developer Center에서 API 키 권한 확인

3. IP 화이트리스트 확인:
```python
# 현재 공인 IP 확인
import requests
ip = requests.get('https://api.ipify.org').text
print(f"Your IP: {ip}")
```

---

## 데이터 조회 문제

### 문제: "Price not found" 또는 None 반환

**증상**:
```python
engine = HybridTradingEngine(config)
price = engine.get_stock_price("005930")
print(price)  # None 출력
```

**원인**:
- 존재하지 않는 티커
- 잘못된 티커 형식
- API 서버에서 데이터를 못 찾음

**해결책**:

1. 티커 형식 확인:
```python
# 올바른 티커 (6자리 숫자)
price = engine.get_stock_price("005930")  # OK

# 잘못된 티커
price = engine.get_stock_price("005930.KS")  # 잘못됨
price = engine.get_stock_price("삼성전자")  # 잘못됨
```

2. 유효한 티커 목록 확인:
```python
# 주식 티커 (한국투자증권)
valid_stocks = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "005380": "현대차",
    "051910": "LG화학"
}

# 암호화폐 티커 (업비트)
valid_cryptos = {
    "KRW-BTC": "비트코인",
    "KRW-ETH": "이더리움",
    "KRW-XRP": "리플"
}
```

3. 에러 처리:
```python
try:
    price = engine.get_stock_price("005930")
    if price is None:
        print("티커를 찾을 수 없습니다")
    else:
        print(f"가격: {price:,.0f} KRW")
except ValueError as e:
    print(f"입력 오류: {e}")
except Exception as e:
    print(f"API 오류: {e}")
```

---

### 문제: "Invalid ticker"

**증상**:
```
ValueError: Ticker must be a non-empty string
```

**원인**:
- 빈 문자열 전달
- None 전달
- 숫자 전달

**해결책**:

```python
# 잘못된 경우
engine.get_stock_price("")  # ValueError
engine.get_stock_price(None)  # ValueError
engine.get_stock_price(5930)  # ValueError

# 올바른 경우
engine.get_stock_price("005930")  # OK
ticker = "005930"
engine.get_stock_price(ticker)  # OK
```

---

## 성능 문제

### 문제: API 호출이 느림

**증상**:
```python
# 너무 오래 걸림
start = time.time()
price = engine.get_stock_price("005930")
print(f"소요 시간: {time.time() - start}초")  # 10초 이상
```

**원인**:
- 네트워크 지연
- 타임아웃 설정이 높음
- API 서버 부하

**해결책**:

1. 네트워크 속도 확인:
```bash
# 인터넷 속도 테스트
speedtest-cli

# 또는 핑 테스트
ping api.upbit.com
```

2. 타임아웃 최적화:
```python
config = TradingConfig(
    kis_config=kis_cfg,
    upbit_config=upbit_cfg,
    timeout=5  # 5초로 감소
)
```

3. 배치 처리로 효율화:
```python
# 비효율적: 10번의 API 호출
tickers = ["005930", "000660", "035420"]
for ticker in tickers:
    price = engine.get_stock_price(ticker)  # 각각 호출

# 효율적: 리스트 컴프리헨션
prices = [engine.get_stock_price(t) for t in tickers]
```

---

### 문제: 메모리 누수

**증상**:
```python
# 장시간 실행 시 메모리 계속 증가
import psutil
process = psutil.Process()

while True:
    price = engine.get_stock_price("005930")
    memory = process.memory_info().rss / 1024 / 1024
    print(f"Memory: {memory:.2f} MB")
```

**원인**:
- 세션이 정리되지 않음
- 로그 누적

**해결책**:

1. Context Manager 사용:
```python
# 좋은 방법
with HybridTradingEngine(config) as engine:
    for i in range(100):
        price = engine.get_stock_price("005930")
# 자동으로 정리됨
```

2. 명시적 정리:
```python
engine = HybridTradingEngine(config)
try:
    for i in range(100):
        price = engine.get_stock_price("005930")
finally:
    engine.close()  # 반드시 호출
```

3. 로깅 레벨 감소:
```python
import logging
logging.basicConfig(level=logging.WARNING)  # DEBUG 대신 WARNING
```

---

## 환경 변수 문제

### 문제: "환경변수가 읽어지지 않음"

**증상**:
```python
import os
print(os.getenv("KIS_APP_KEY"))  # None 출력
```

**원인**:
- 환경변수가 설정되지 않음
- 터미널을 재시작하지 않음
- 잘못된 환경변수명

**해결책**:

1. 환경변수 재설정:
```bash
# macOS / Linux
export KIS_APP_KEY="your_key"
echo $KIS_APP_KEY  # 확인

# Windows (CMD)
setx KIS_APP_KEY "your_key"
# CMD 재시작 후 확인
echo %KIS_APP_KEY%

# Windows (PowerShell)
[System.Environment]::SetEnvironmentVariable("KIS_APP_KEY", "your_key", "User")
```

2. 파이썬에서 확인:
```python
import os

# 수동으로 설정
os.environ["KIS_APP_KEY"] = "your_key"

# 또는 .env 파일 사용
from dotenv import load_dotenv
load_dotenv()
```

3. .env 파일 사용:
```bash
# .env 파일 생성
cat > .env << EOF
KIS_APP_KEY=your_key
KIS_SECRET_KEY=your_secret
KIS_ACCOUNT=1234-5678
KIS_HTS_ID=your_hts_id
UPBIT_ACCESS_KEY=your_access_key
UPBIT_SECRET_KEY=your_secret_key
EOF

# Python에서 로드
from dotenv import load_dotenv
load_dotenv()
```

---

## 테스트 실패

### 문제: pytest 실행 실패

**증상**:
```
ModuleNotFoundError: No module named 'pytest'
또는
tests/test_engine.py: ERROR collecting test module
```

**해결책**:

1. pytest 설치:
```bash
pip install pytest pytest-cov
```

2. 테스트 실행:
```bash
# 모든 테스트 실행
pytest

# 자세한 출력
pytest -v

# 코드 커버리지
pytest --cov=hybrid_trader
```

---

### 문제: "Mock 객체 사용 오류"

**증상**:
```
ImportError: No module named 'unittest.mock'
```

**해결책**:

```python
# Python 3.3 이상 (표준 라이브러리)
from unittest.mock import Mock, patch, MagicMock

# 테스트 예제
@patch('hybrid_trader.engine.HybridTradingEngine.kis_session')
def test_get_stock_price(mock_kis):
    mock_kis.get_current_price.return_value = 75500.0
    # 테스트
```

---

## 자주 묻는 질문 (FAQ)

### Q1: 실거래 전에 테스트는 어떻게 하나요?

**A**: 다음 방법을 추천합니다:

1. 데모 모드 사용:
```python
kis_config = KISConfig(
    app_key=os.getenv("KIS_APP_KEY"),
    secret_key=os.getenv("KIS_SECRET_KEY"),
    account_number=os.getenv("KIS_ACCOUNT"),
    hts_id=os.getenv("KIS_HTS_ID"),
    is_demo=True  # 데모 모드
)
```

2. 적은 금액으로 테스트
3. 로그 기록하고 검토

---

### Q2: 여러 계좌를 관리할 수 있나요?

**A**: 각 계좌별로 별도의 엔진 인스턴스를 생성하세요:

```python
# 계좌 1
config1 = TradingConfig(
    kis_config=KISConfig(..., account_number="1111-1111"),
    upbit_config=UpbitConfig(...)
)
engine1 = HybridTradingEngine(config1)

# 계좌 2
config2 = TradingConfig(
    kis_config=KISConfig(..., account_number="2222-2222"),
    upbit_config=UpbitConfig(...)
)
engine2 = HybridTradingEngine(config2)
```

---

### Q3: API 호출 한도는?

**A**: 각 플랫폼의 제한:

- **한국투자증권**: 시간당 API 호출 제한 있음 (정확한 한도는 개발자 센터 확인)
- **업비트**: 분당 600회 요청 제한

대책:
```python
import time

# API 호출 간격 설정
for ticker in tickers:
    price = engine.get_stock_price(ticker)
    time.sleep(1)  # 1초 대기
```

---

### Q4: 로그는 어디에 저장되나요?

**A**: 기본적으로 콘솔에만 출력됩니다. 파일로 저장하려면:

```python
import logging

# 파일로 로깅
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
```

---

### Q5: 한 PC에서 여러 스크립트를 동시에 실행할 수 있나요?

**A**: 가능하지만 주의하세요:

```python
# 각 스크립트가 독립적인 엔진을 사용하면 됨
# 하지만 같은 계좌를 동시에 거래하면 충돌 가능

# 권장: 하나의 매니저 스크립트에서 관리
import threading

def strategy1():
    with HybridTradingEngine(config) as engine:
        # 전략 1
        pass

def strategy2():
    with HybridTradingEngine(config) as engine:
        # 전략 2
        pass

# 스레드로 동시 실행
t1 = threading.Thread(target=strategy1)
t2 = threading.Thread(target=strategy2)
t1.start()
t2.start()
```

---

### Q6: 인터넷 연결이 끊기면?

**A**: 재시도 로직으로 자동 처리됩니다:

```python
config = TradingConfig(
    kis_config=kis_cfg,
    upbit_config=upbit_cfg,
    retry_count=5  # 5회 재시도
)

# 3회 실패 후 자동으로 4번째 시도
price = engine.get_stock_price("005930")
```

---

## 추가 도움말

### 디버깅 팁

1. 로깅 레벨을 DEBUG로 설정:
```python
logging.basicConfig(level=logging.DEBUG)
```

2. 각 단계를 프린트:
```python
print("1. 엔진 초기화")
engine = HybridTradingEngine(config)

print("2. KIS 세션 확인")
print(engine.kis_session)

print("3. 가격 조회")
price = engine.get_stock_price("005930")
print(f"가격: {price}")
```

3. 예외 정보 출력:
```python
import traceback

try:
    price = engine.get_stock_price("005930")
except Exception as e:
    print(f"오류: {e}")
    traceback.print_exc()
```

---

## 문제 해결 체크리스트

- [ ] 가상 환경이 활성화되어 있는가?
- [ ] 모든 의존성이 설치되어 있는가?
- [ ] API 키가 올바른가?
- [ ] 환경변수가 제대로 설정되어 있는가?
- [ ] 인터넷 연결이 안정적인가?
- [ ] Python 버전이 3.8 이상인가?
- [ ] 로그 파일을 확인했는가?

---

**문제가 해결되지 않으면 [Issues](https://github.com/YuMyeongJun/hybrid-trader/issues)에서 문의해주세요.**
