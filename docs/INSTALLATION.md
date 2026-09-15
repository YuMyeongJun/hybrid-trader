# 설치 가이드 (Installation Guide)

Hybrid Trader의 상세한 설치 방법을 안내합니다.

## 목차

- [요구사항](#요구사항)
- [기본 설치](#기본-설치)
- [API 키 발급](#api-키-발급)
- [환경 설정](#환경-설정)
- [설치 확인](#설치-확인)
- [트러블슈팅](#트러블슈팅)

---

## 요구사항

### 시스템 요구사항

- **Python**: 3.8 이상 (3.8, 3.9, 3.10, 3.11 권장)
- **OS**: Windows, macOS, Linux
- **인터넷**: 안정적인 인터넷 연결 필수

### 필수 라이브러리

다음 라이브러리들이 자동으로 설치됩니다:

```
python-kis>=0.3.0      # 한국투자증권 API
pyupbit>=0.2.35        # 업비트 API
requests>=2.28.0       # HTTP 요청
pandas>=1.5.0          # 데이터 분석
```

---

## 기본 설치

### 1단계: 프로젝트 클론 또는 다운로드

```bash
# GitHub에서 클론
git clone https://github.com/yourusername/hybrid-trader.git
cd hybrid-trader

# 또는 ZIP 다운로드 후 압축 해제
```

### 2단계: 가상 환경 생성 (권장)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**가상 환경을 사용하는 이유:**
- 프로젝트별 독립적인 패키지 관리
- 버전 충돌 방지
- 시스템 Python 보호

### 3단계: 의존성 설치

#### 방법 1: requirements.txt 사용 (권장)

```bash
pip install -r requirements.txt
```

#### 방법 2: 수동 설치

```bash
pip install python-kis>=0.3.0
pip install pyupbit>=0.2.35
pip install requests>=2.28.0
pip install pandas>=1.5.0
```

#### 방법 3: 개발 환경 설치

개발이나 테스트를 계획 중이면:

```bash
pip install -r requirements.txt
pip install pytest>=7.0
pip install pytest-cov>=3.0
pip install black>=22.0
pip install flake8>=4.0
```

### 4단계: 패키지 설치 (선택사항)

프로젝트를 패키지로 설치하려면:

```bash
pip install -e .
```

`-e` 플래그는 개발 모드 설치로, 파일 수정 시 재설치 없이 변경사항이 반영됩니다.

---

## API 키 발급

### 한국투자증권 (KIS) API 키 발급

#### 1단계: 계정 생성 및 로그인

1. [한국투자증권 공식 웹사이트](https://www.trueinvesting.com) 방문
2. 계정 생성 (이미 계좌가 있으면 로그인)
3. HTS 다운로드 및 설치 (실시간 데이터 필요 시)

#### 2단계: Developer Center 접속

1. [한국투자증권 Developer Center](https://developers.trueinvesting.com) 접속
2. 로그인 (계좌 로그인과 동일)
3. "Open API" 또는 "API 신청" 메뉴 선택

#### 3단계: API 신청

1. **App Key, Secret Key 발급 신청**
   - API 신청 페이지에서 "신청" 클릭
   - 앱 이름 입력 (예: "MyTradingBot")
   - 사용 목적 입력 (예: "자동매매 테스트")
   - "신청" 완료

2. **승인 대기**
   - 일반적으로 1-2시간 내 자동 승인
   - 이메일로 App Key, Secret Key 수신

#### 4단계: 필수 정보 확인

필요한 정보들을 안전한 장소에 기록하세요:

- **App Key**: API 신청 결과에서 확인
- **Secret Key**: API 신청 결과에서 확인  
- **Account Number**: 거래 계좌번호 (형식: "1234-5678")
  - HTS > 상단 메뉴 > 계좌정보에서 확인
- **HTS ID**: HTS 로그인 ID

### 업비트 (Upbit) API 키 발급

#### 1단계: 계정 생성 및 로그인

1. [업비트 공식 웹사이트](https://upbit.com) 방문
2. 계정 생성 (이미 계정이 있으면 로그인)
3. 2차 인증 설정 필수 (OTP 또는 보안문자)

#### 2단계: API 센터 접속

1. 로그인 후 [업비트 API 센터](https://upbit.com/api_center) 접속
2. 마이페이지 > 개발자 센터 선택

#### 3단계: API Key 생성

1. "API Key 관리" 클릭
2. "새 API Key 생성" 버튼 클릭
3. 필요한 권한 선택:
   - 필수: "조회" (시세 조회)
   - 거래 기능 필요 시: "주문", "출금"
4. IP 화이트리스트 설정 (선택, 보안상 권장)
5. "생성" 클릭

#### 4단계: 키 저장

- **Access Key**: 환경변수 또는 안전한 파일에 저장
- **Secret Key**: 절대 공유하지 말기

**주의**: Secret Key는 재발급할 수 없으므로 안전하게 보관하세요!

---

## 환경 설정

### 환경변수 설정 (권장)

API 키를 환경변수로 관리하면 보안이 높아집니다.

#### Windows (CMD)

```batch
setx KIS_APP_KEY "your_kis_app_key"
setx KIS_SECRET_KEY "your_kis_secret_key"
setx KIS_ACCOUNT "1234-5678"
setx KIS_HTS_ID "your_hts_id"
setx UPBIT_ACCESS_KEY "your_upbit_access_key"
setx UPBIT_SECRET_KEY "your_upbit_secret_key"
```

설정 후 CMD 재시작 필요.

#### Windows (PowerShell)

```powershell
[System.Environment]::SetEnvironmentVariable("KIS_APP_KEY", "your_kis_app_key", "User")
[System.Environment]::SetEnvironmentVariable("KIS_SECRET_KEY", "your_kis_secret_key", "User")
# ... 나머지 환경변수도 동일하게 설정
```

#### macOS / Linux

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export KIS_APP_KEY="your_kis_app_key"
export KIS_SECRET_KEY="your_kis_secret_key"
export KIS_ACCOUNT="1234-5678"
export KIS_HTS_ID="your_hts_id"
export UPBIT_ACCESS_KEY="your_upbit_access_key"
export UPBIT_SECRET_KEY="your_upbit_secret_key"

# 변경사항 적용
source ~/.bashrc  # 또는 source ~/.zshrc
```

### .env 파일 사용 (개발 환경용)

`.env` 파일을 프로젝트 루트에 생성:

```bash
# .env
KIS_APP_KEY=your_kis_app_key
KIS_SECRET_KEY=your_kis_secret_key
KIS_ACCOUNT=1234-5678
KIS_HTS_ID=your_hts_id
UPBIT_ACCESS_KEY=your_upbit_access_key
UPBIT_SECRET_KEY=your_upbit_secret_key
```

Python에서 사용:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드 (python-dotenv 필요: pip install python-dotenv)

kis_app_key = os.getenv("KIS_APP_KEY")
kis_secret_key = os.getenv("KIS_SECRET_KEY")
# ...
```

**.env를 .gitignore에 추가 (중요!):**

```bash
# .gitignore에 다음 추가
.env
.env.local
```

---

## 설치 확인

### 1단계: Python 버전 확인

```bash
python --version
# Python 3.8 이상이어야 함
```

### 2단계: 필수 라이브러리 확인

```bash
pip list | grep -E "python-kis|pyupbit|requests|pandas"
```

### 3단계: 간단한 테스트 스크립트 실행

`test_installation.py` 생성:

```python
#!/usr/bin/env python
"""설치 확인 테스트 스크립트"""

def check_installation():
    """필요한 라이브러리가 제대로 설치되었는지 확인"""
    
    print("=" * 50)
    print("Hybrid Trader 설치 확인")
    print("=" * 50)
    
    # Python 버전 확인
    import sys
    print(f"\n✓ Python 버전: {sys.version}")
    
    # 라이브러리 확인
    libraries = {
        "requests": "HTTP 요청",
        "pandas": "데이터 분석",
        "kis": "한국투자증권 API (설치되면 확인)",
        "pyupbit": "업비트 API (설치되면 확인)"
    }
    
    print("\n필수 라이브러리 확인:")
    for lib, description in libraries.items():
        try:
            __import__(lib)
            print(f"  ✓ {lib}: 설치됨")
        except ImportError:
            print(f"  ✗ {lib}: 미설치 ({description})")
    
    # Hybrid Trader 패키지 확인
    print("\nHybrid Trader 패키지:")
    try:
        from hybrid_trader import HybridTradingEngine, TradingConfig
        print(f"  ✓ hybrid_trader: 설치됨")
    except ImportError as e:
        print(f"  ✗ hybrid_trader: 미설치 - {e}")
    
    print("\n" + "=" * 50)
    print("설치 확인 완료!")
    print("=" * 50)

if __name__ == "__main__":
    check_installation()
```

실행:

```bash
python test_installation.py
```

### 4단계: 간단한 연결 테스트

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig
import os

# 환경변수에서 API 키 로드
kis_config = KISConfig(
    app_key=os.getenv("KIS_APP_KEY", "demo"),
    secret_key=os.getenv("KIS_SECRET_KEY", "demo"),
    account_number=os.getenv("KIS_ACCOUNT", "1234-5678"),
    hts_id=os.getenv("KIS_HTS_ID", "demo")
)

upbit_config = UpbitConfig(
    access_key=os.getenv("UPBIT_ACCESS_KEY", "demo"),
    secret_key=os.getenv("UPBIT_SECRET_KEY", "demo")
)

config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)

try:
    engine = HybridTradingEngine(config)
    print("✓ Hybrid Trader 엔진 초기화 성공!")
    engine.close()
except Exception as e:
    print(f"✗ 에러: {e}")
```

---

## 트러블슈팅

### 설치 문제

#### 1. "No module named 'hybrid_trader'"

**원인**: 패키지가 설치되지 않았거나 가상 환경이 활성화되지 않음

**해결책**:
```bash
# 가상 환경 활성화 확인
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 패키지 재설치
pip install -e .
```

#### 2. "python-kis not installed"

**원인**: KIS 라이브러리가 설치되지 않음

**해결책**:
```bash
pip install python-kis>=0.3.0
```

#### 3. "No module named 'pyupbit'"

**원인**: pyupbit 라이브러리가 설치되지 않음

**해결책**:
```bash
pip install pyupbit>=0.2.35
```

### API 연결 문제

#### 1. "Missing required credentials"

**원인**: API 키가 없거나 잘못됨

**해결책**:
- API 키 발급 절차를 다시 확인
- 환경변수가 제대로 설정되었는지 확인
- 특수문자 처리 확인

```bash
# 환경변수 확인 (macOS/Linux)
echo $KIS_APP_KEY
echo $UPBIT_ACCESS_KEY
```

#### 2. "Connection timeout"

**원인**: 네트워크 문제 또는 API 서버 다운

**해결책**:
- 인터넷 연결 확인
- 각 플랫폼 상태 페이지 확인:
  - [한국투자증권 상태](https://developers.trueinvesting.com)
  - [업비트 상태](https://upbit.com)
- 방화벽/프록시 설정 확인

#### 3. "API key is not valid"

**원인**: API 키 오류 또는 만료

**해결책**:
- 한국투자증권: Developer Center에서 키 재확인
- 업비트: API 센터에서 키 재확인
- 키 복사 시 공백이 없는지 확인

### 성능 최적화

#### 1. 패키지 업그레이드

```bash
pip install --upgrade -r requirements.txt
```

#### 2. 불필요한 라이브러리 제거

```bash
pip install --no-deps hybrid_trader
```

#### 3. 로깅 레벨 조정

```python
import logging

# DEBUG 모드 (자세한 정보)
logging.basicConfig(level=logging.DEBUG)

# INFO 모드 (기본)
logging.basicConfig(level=logging.INFO)

# WARNING 모드 (경고만)
logging.basicConfig(level=logging.WARNING)
```

---

## 다음 단계

설치가 완료되었습니다! 다음을 진행하세요:

1. [빠른 시작](../README.md#-빠른-시작) - 기본 사용법 학습
2. [API 문서](./API.md) - 전체 API 참고
3. [예제 코드](./EXAMPLES.md) - 실제 사용 사례
4. [아키텍처](./ARCHITECTURE.md) - 시스템 구조 이해

---

**문제가 있으신가요?**
- [Troubleshooting Guide](./TROUBLESHOOTING.md)를 참고하세요
- [Issues](https://github.com/yourusername/hybrid-trader/issues)에서 질문하세요
