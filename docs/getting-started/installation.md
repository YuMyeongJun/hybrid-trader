# 설치 가이드

Hybrid Trader를 설치하고 시작하는 방법입니다.

## 📋 사전 요구사항

- **Python**: 3.8 이상
- **pip**: 21.0 이상
- **인터넷 연결**: API 통신을 위해 필요

## 🚀 설치 방법

### 1. PyPI에서 설치 (권장)

```bash
pip install hybrid-trader
```

### 2. GitHub에서 직접 설치

```bash
git clone https://github.com/YuMyeongJun/hybrid-trader.git
cd hybrid-trader
pip install -r requirements.txt
pip install -e .
```

### 3. 개발 환경 설정

```bash
git clone https://github.com/YuMyeongJun/hybrid-trader.git
cd hybrid-trader
pip install -r requirements.txt
pip install -e ".[dev]"
```

## 🔑 API 키 발급

### 한국투자증권 (KIS) API 설정

1. **개발자 센터 접속**
   - [한국투자증권 Developer Center](https://developers.trueinvesting.com) 방문
   
2. **계정 생성 및 앱 등록**
   - 회원가입 후 새 앱 등록
   
3. **인증 정보 수집**
   - **App Key**: 앱의 고유 키
   - **Secret Key**: 앱의 비밀 키
   - **Account Number**: 거래 계좌 번호 (형식: `XXXX-XXXX`)
   - **HTS ID**: HTS 로그인 ID

4. **테스트 모드 활성화** (선택)
   - `is_demo=True`로 설정하면 모의거래 환경에서 테스트 가능

### 업비트 (Upbit) API 설정

1. **업비트 로그인**
   - [업비트](https://upbit.com) 접속
   
2. **API 센터 접속**
   - 계정 → [API 센터](https://upbit.com/api_center) 이동
   
3. **API 키 발급**
   - "새로운 API 키 생성" 클릭
   - 권한 설정 (캔들, 주문가능 등)
   - **Access Key** 복사
   - **Secret Key** 복사 (한 번만 표시됨)

4. **IP 화이트리스트 설정** (선택)
   - 보안을 위해 특정 IP만 허용 가능

## 🔒 보안 가이드

### ⚠️ 절대하지 말아야 할 것

```python
# ❌ 절대 이렇게 하지 마세요!
kis_config = KISConfig(
    app_key="ak1234567890",  # 절대 하드코딩 금지!
    secret_key="sk9876543210"
)
```

### ✅ 올바른 방법: 환경변수 사용

#### 방법 1: `.env` 파일 사용

```bash
# .env 파일 생성
echo "KIS_APP_KEY=your_app_key" > .env
echo "KIS_SECRET_KEY=your_secret_key" >> .env
echo "KIS_ACCOUNT=1234-5678" >> .env
echo "KIS_HTS_ID=your_hts_id" >> .env
echo "UPBIT_ACCESS_KEY=your_access_key" >> .env
echo "UPBIT_SECRET_KEY=your_secret_key" >> .env
```

```python
import os
from dotenv import load_dotenv
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# .env 파일 로드
load_dotenv()

kis_config = KISConfig(
    app_key=os.getenv("KIS_APP_KEY"),
    secret_key=os.getenv("KIS_SECRET_KEY"),
    account_number=os.getenv("KIS_ACCOUNT"),
    hts_id=os.getenv("KIS_HTS_ID")
)

upbit_config = UpbitConfig(
    access_key=os.getenv("UPBIT_ACCESS_KEY"),
    secret_key=os.getenv("UPBIT_SECRET_KEY")
)

config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
engine = HybridTradingEngine(config)
```

#### 방법 2: 시스템 환경변수 사용

```bash
# 터미널에서 설정 (일시적)
export KIS_APP_KEY="your_app_key"
export KIS_SECRET_KEY="your_secret_key"
export KIS_ACCOUNT="1234-5678"
export KIS_HTS_ID="your_hts_id"
export UPBIT_ACCESS_KEY="your_access_key"
export UPBIT_SECRET_KEY="your_secret_key"

# 영구 설정 (macOS/Linux)
echo 'export KIS_APP_KEY="your_app_key"' >> ~/.zshrc
source ~/.zshrc
```

#### 방법 3: 설정 파일 사용

```python
# config.json
{
    "kis": {
        "app_key": "your_app_key",
        "secret_key": "your_secret_key",
        "account_number": "1234-5678",
        "hts_id": "your_hts_id"
    },
    "upbit": {
        "access_key": "your_access_key",
        "secret_key": "your_secret_key"
    }
}
```

```python
import json
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 설정 파일 로드
with open("config.json", "r") as f:
    config_data = json.load(f)

kis_config = KISConfig(**config_data["kis"])
upbit_config = UpbitConfig(**config_data["upbit"])

config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
engine = HybridTradingEngine(config)
```

### 🛡️ 보안 체크리스트

- [ ] API 키를 코드에 하드코딩하지 않음
- [ ] `.env` 파일을 `.gitignore`에 추가함
- [ ] 배포 환경에서 환경변수 설정함
- [ ] 불필요한 API 권한은 비활성화함
- [ ] 정기적으로 API 키를 재발급함
- [ ] 로그 파일에서 민감한 정보 제거함

## ✅ 설치 확인

### Python 인터프리터에서 확인

```python
>>> import hybrid_trader
>>> print(hybrid_trader.__version__)
0.1.0
>>> from hybrid_trader import HybridTradingEngine
>>> print("설치 완료!")
```

### 커맨드 라인에서 확인

```bash
python -c "import hybrid_trader; print(f'Version: {hybrid_trader.__version__}')"
```

## 🐛 설치 문제 해결

### 문제 1: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'hybrid_trader'
```

**해결책:**
```bash
pip install hybrid-trader
# 또는
pip install -e .  # 로컬에서 개발 중인 경우
```

### 문제 2: 의존성 충돌

```bash
# 의존성 업데이트
pip install --upgrade hybrid-trader

# 또는 깨끗하게 재설치
pip uninstall hybrid-trader
pip install hybrid-trader
```

### 문제 3: Python 버전 오류

```
ERROR: hybrid-trader requires Python >=3.8
```

**해결책:**
```bash
# Python 버전 확인
python --version

# Python 3.8+ 로 업그레이드
# macOS: brew install python@3.11
# Ubuntu: sudo apt-get install python3.11
# Windows: https://www.python.org/downloads/
```

## 📦 의존성

Hybrid Trader는 다음 라이브러리에 의존합니다:

| 라이브러리 | 용도 | 버전 |
|-----------|------|------|
| `python-kis` | 한국투자증권 API | >=0.3.0 |
| `pyupbit` | 업비트 API | >=0.2.35 |
| `requests` | HTTP 통신 | >=2.28.0 |
| `pandas` | 데이터 분석 | >=1.5.0 |

## 🎯 다음 단계

설치가 완료되었습니다! 다음 단계를 따라 진행하세요:

1. **[빠른 시작](quickstart.md)** - 5분 안에 첫 거래 시작
2. **[기본 예제](../guide/examples.md)** - 실제 코드 예제 보기
3. **[API 레퍼런스](../api/overview.md)** - 전체 API 문서 확인

---

**문제가 발생했나요?** [이슈 제보](https://github.com/YuMyeongJun/hybrid-trader/issues)하거나 [FAQ](../resources/faq.md)를 확인해보세요.
