# 🚀 Hybrid Trader

**하이브리드 자동매매 시스템을 위한 통합 파이썬 라이브러리**

[![Tests](https://github.com/mjyu-louis/hybrid-trader/actions/workflows/tests.yml/badge.svg)](https://github.com/mjyu-louis/hybrid-trader/actions/workflows/tests.yml)
[![Advanced Tests](https://github.com/mjyu-louis/hybrid-trader/actions/workflows/tests-advanced.yml/badge.svg)](https://github.com/mjyu-louis/hybrid-trader/actions/workflows/tests-advanced.yml)
[![codecov](https://codecov.io/gh/mjyu-louis/hybrid-trader/branch/main/graph/badge.svg)](https://codecov.io/gh/mjyu-louis/hybrid-trader)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

한국투자증권(KIS) API와 업비트(Upbit) API를 하나로 통합하여, 주식과 암호화폐를 동시에 거래할 수 있는 자동매매 시스템을 **단 몇 줄의 코드**로 구축할 수 있습니다.

---

## ✨ 주요 기능

- **통합 인터페이스**: 한투 API와 업비트 API를 하나의 엔진으로 관리
- **타입 힌트**: 완벽한 타입 힌트로 IDE 자동완성 지원
- **클린 코드**: 복잡한 API 호출을 감싸서 깔끔한 사용 경험 제공
- **재시도 로직**: 자동 재시도 기능으로 안정적인 거래 지원
- **로깅**: 상세한 로깅으로 디버깅 및 모니터링 용이
- **Context Manager**: `with` 문법으로 안전한 세션 관리

---

## 📦 설치

### 1단계: 필수 라이브러리 설치

```bash
# Hybrid Trader 설치
pip install -r requirements.txt

# 또는 수동으로 설치
pip install python-kis>=0.3.0
pip install pyupbit>=0.2.35
pip install requests>=2.28.0
pip install pandas>=1.5.0
```

### 2단계: API 키 발급

#### 한국투자증권 (KIS)
1. [한국투자증권 Developer Center](https://developers.trueinvesting.com) 방문
2. App Key, Secret Key 발급
3. Account Number와 HTS ID 확인

#### 업비트 (Upbit)
1. [업비트 API 센터](https://upbit.com/api_center) 방문
2. Access Key, Secret Key 발급

---

## 🎯 빠른 시작

### 기본 사용법

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

# 1. API 설정 구성
kis_config = KISConfig(
    app_key="YOUR_KIS_APP_KEY",
    secret_key="YOUR_KIS_SECRET_KEY",
    account_number="1234-5678",
    hts_id="YOUR_HTS_ID",
    is_demo=True  # 테스트 모드
)

upbit_config = UpbitConfig(
    access_key="YOUR_UPBIT_ACCESS_KEY",
    secret_key="YOUR_UPBIT_SECRET_KEY"
)

# 2. 트레이딩 엔진 초기화
config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
engine = HybridTradingEngine(config)

# 3. 현재가 조회 (주식)
samsung_price = engine.get_stock_price("005930")  # 삼성전자
print(f"삼성전자: {samsung_price:,.0f} KRW")

# 4. 현재가 조회 (암호화폐)
bitcoin_price = engine.get_coin_price("KRW-BTC")  # 비트코인
print(f"비트코인: {bitcoin_price:,.0f} KRW")

# 5. 세션 정리
engine.close()
```

### Context Manager 사용 (권장)

```python
with HybridTradingEngine(config) as engine:
    stock_price = engine.get_stock_price("005930")
    coin_price = engine.get_coin_price("KRW-BTC")
    print(f"삼성전자: {stock_price}, 비트코인: {coin_price}")
    # 자동으로 세션이 정리됩니다
```

---

## 📚 문서 및 API

**전체 문서는 [Hybrid Trader 공식 문서](https://YuMyeongJun.github.io/hybrid-trader)를 참고하세요.**

### 빠른 링크

- [설치 가이드](https://YuMyeongJun.github.io/hybrid-trader/getting-started/installation/)
- [빠른 시작](https://YuMyeongJun.github.io/hybrid-trader/getting-started/quickstart/)
- [API 레퍼런스](https://YuMyeongJun.github.io/hybrid-trader/api/overview/)
- [실전 예제](https://YuMyeongJun.github.io/hybrid-trader/guide/examples/)
- [FAQ](https://YuMyeongJun.github.io/hybrid-trader/resources/faq/)

### HybridTradingEngine

#### `get_stock_price(ticker: str) -> Optional[float]`

한국투자증권 API를 통해 주식의 현재가를 조회합니다.

**매개변수:**
- `ticker` (str): 주식 코드 (예: "005930" = 삼성전자)

**반환값:**
- `float`: 현재가 (KRW 단위)
- `None`: 조회 실패 시

**예시:**
```python
samsung_price = engine.get_stock_price("005930")
```

---

#### `get_coin_price(ticker: str) -> Optional[float]`

업비트 API를 통해 암호화폐의 현재가를 조회합니다.

**매개변수:**
- `ticker` (str): 암호화폐 코드 (예: "KRW-BTC" = 비트코인)

**반환값:**
- `float`: 현재가 (KRW 단위)
- `None`: 조회 실패 시

**예시:**
```python
bitcoin_price = engine.get_coin_price("KRW-BTC")
ethereum_price = engine.get_coin_price("KRW-ETH")
```

---

### TradingConfig

#### `KISConfig`

한국투자증권 API 설정

```python
KISConfig(
    app_key="YOUR_APP_KEY",           # 필수: KIS App Key
    secret_key="YOUR_SECRET_KEY",     # 필수: KIS Secret Key
    account_number="1234-5678",       # 필수: 거래 계좌 번호
    hts_id="YOUR_HTS_ID",            # 필수: HTS ID
    is_demo=True                      # 선택: 테스트 모드 여부
)
```

#### `UpbitConfig`

업비트 API 설정

```python
UpbitConfig(
    access_key="YOUR_ACCESS_KEY",    # 필수: Upbit Access Key
    secret_key="YOUR_SECRET_KEY"     # 필수: Upbit Secret Key
)
```

---

## 🛠️ 구조

```
hybrid-trader/
├── README.md                 # 프로젝트 문서
├── requirements.txt          # 의존성 목록
├── setup.py                  # 패키지 설정
└── hybrid_trader/
    ├── __init__.py          # 패키지 초기화
    ├── config.py            # API 설정 클래스
    ├── engine.py            # 메인 거래 엔진
    └── exceptions.py        # 커스텀 예외 (선택)
```

---

## 🔒 보안 가이드

**중요**: API 키를 절대 코드에 하드코딩하지 마세요!

### 환경변수 사용 (권장)

```bash
# .env 파일
export KIS_APP_KEY="your_key_here"
export KIS_SECRET_KEY="your_secret_here"
export UPBIT_ACCESS_KEY="your_key_here"
export UPBIT_SECRET_KEY="your_secret_here"
```

```python
import os
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig

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

engine = HybridTradingEngine(TradingConfig(kis_config, upbit_config))
```

---

## 📝 로깅

기본 로깅 설정:

```python
import logging

logging.basicConfig(level=logging.INFO)
# DEBUG, INFO, WARNING, ERROR, CRITICAL

# 특정 모듈만 로깅
logger = logging.getLogger('hybrid_trader.engine')
logger.setLevel(logging.DEBUG)
```

---

## 🧪 테스트

이 프로젝트는 포괄적인 테스트 스위트를 제공합니다:

### 로컬 테스트 실행

```bash
# 전체 테스트 실행
pytest tests/ -v

# 커버리지 리포트와 함께 실행
pytest tests/ -v --cov=hybrid_trader --cov-report=html

# 특정 테스트 카테고리만 실행
pytest tests/ -v -m "unit"              # 단위 테스트
pytest tests/ -v -m "integration"       # 통합 테스트
pytest tests/ -v -m "performance"       # 성능 테스트
pytest tests/ -v -m "security"          # 보안 테스트
pytest tests/ -v -m "edge_case"         # 엣지 케이스 테스트
```

### 테스트 스위트 구성

- **test_engine.py**: 메인 트레이딩 엔진 테스트
- **test_config.py**: 설정 검증 테스트
- **test_analysis.py**: 기술적 분석 테스트
- **test_monitoring.py**: 모니터링 기능 테스트
- **test_performance.py**: 성능 및 속도 테스트
- **test_edge_cases.py**: 엣지 케이스 및 경계 조건 테스트
- **test_security.py**: 보안 및 자격증명 처리 테스트
- **test_api_integration.py**: KIS 및 Upbit API 통합 테스트
- **test_data_validation.py**: 데이터 유효성 검증 테스트

### 커버리지 목표

- **목표 커버리지**: 90% 이상
- **현재 상태**: [![codecov](https://codecov.io/gh/mjyu-louis/hybrid-trader/branch/main/graph/badge.svg)](https://codecov.io/gh/mjyu-louis/hybrid-trader)

### CI/CD 파이프라인

- **tests.yml**: 기본 테스트 및 코드 품질 검사
- **tests-advanced.yml**: 고급 테스트 (성능, 보안, 엣지 케이스)
  - Python 3.8 ~ 3.12 (여러 OS 지원)
  - 성능 벤치마크
  - 보안 스캔 (Bandit, Safety)
  - 종합 커버리지 분석

---

## 🤝 기여하기

이 프로젝트는 오픈소스입니다! 다음과 같은 방식으로 기여할 수 있습니다:

1. **이슈 제보**: 버그나 기능 요청은 [Issues](https://github.com/yourusername/hybrid-trader/issues) 탭에서
2. **풀 리퀘스트**: 개선 사항은 PR로 제출해주세요
3. **문서 개선**: 문서 오류나 부족한 부분을 알려주세요

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

## ⚠️ 주의사항

- **테스트 환경**: 본거래 전에 `is_demo=True`로 충분히 테스트하세요
- **API 한도**: 각 플랫폼의 API 호출 한도를 확인하세요
- **네트워크**: 안정적인 인터넷 연결을 유지하세요
- **보안**: API 키를 안전하게 관리하세요

---

## 📞 문의

문제가 있거나 질문이 있으신가요? 
- GitHub Issues에서 이슈를 생성해주세요
- 또는 PR을 통해 개선 제안을 해주세요

---

**Made with ❤️ for traders and developers**

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!
