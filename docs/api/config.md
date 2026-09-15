# Configuration API

API 자격증명 및 설정 클래스들입니다.

## 클래스: KISConfig

한국투자증권 API 설정을 저장합니다.

```python
@dataclass
class KISConfig:
    app_key: str          # KIS App Key
    secret_key: str       # KIS Secret Key
    account_number: str   # 계좌번호 (형식: XXXX-XXXX)
    hts_id: str          # HTS 로그인 ID
    is_demo: bool = False # 테스트 모드 여부
```

### 초기화

```python
from hybrid_trader import KISConfig

kis_config = KISConfig(
    app_key="your_app_key",
    secret_key="your_secret_key",
    account_number="1234-5678",
    hts_id="your_hts_id",
    is_demo=True  # 테스트 모드
)
```

### 유효성 검사

```python
def validate(self) -> None:
    """설정이 유효한지 검사합니다."""
```

**예시:**
```python
try:
    kis_config.validate()
    print("설정이 유효합니다")
except ConfigurationError as e:
    print(f"설정 오류: {e}")
```

### 속성

| 속성 | 타입 | 설명 |
|------|------|------|
| `app_key` | str | KIS App Key (필수) |
| `secret_key` | str | KIS Secret Key (필수) |
| `account_number` | str | 계좌번호, 형식: XXXX-XXXX (필수) |
| `hts_id` | str | HTS 로그인 ID (필수) |
| `is_demo` | bool | 테스트 모드 (기본값: False) |

---

## 클래스: UpbitConfig

업비트 API 설정을 저장합니다.

```python
@dataclass
class UpbitConfig:
    access_key: str   # Upbit Access Key
    secret_key: str   # Upbit Secret Key
```

### 초기화

```python
from hybrid_trader import UpbitConfig

upbit_config = UpbitConfig(
    access_key="your_access_key",
    secret_key="your_secret_key"
)
```

### 유효성 검사

```python
def validate(self) -> None:
    """설정이 유효한지 검사합니다."""
```

**예시:**
```python
try:
    upbit_config.validate()
    print("설정이 유효합니다")
except ConfigurationError as e:
    print(f"설정 오류: {e}")
```

### 속성

| 속성 | 타입 | 설명 |
|------|------|------|
| `access_key` | str | Upbit Access Key (필수) |
| `secret_key` | str | Upbit Secret Key (필수) |

---

## 클래스: TradingConfig

전체 거래 설정을 통합합니다.

```python
@dataclass
class TradingConfig:
    kis_config: KISConfig      # KIS 설정
    upbit_config: UpbitConfig  # Upbit 설정
```

### 초기화

```python
from hybrid_trader import TradingConfig, KISConfig, UpbitConfig

kis_cfg = KISConfig(...)
upbit_cfg = UpbitConfig(...)

config = TradingConfig(
    kis_config=kis_cfg,
    upbit_config=upbit_cfg
)
```

### 유효성 검사

```python
def validate(self) -> None:
    """설정이 유효한지 검사합니다."""
```

**예시:**
```python
try:
    config.validate()
    print("모든 설정이 유효합니다")
except ConfigurationError as e:
    print(f"설정 오류: {e}")
```

### 속성

| 속성 | 타입 | 설명 |
|------|------|------|
| `kis_config` | KISConfig | 한국투자증권 설정 (필수) |
| `upbit_config` | UpbitConfig | 업비트 설정 (필수) |

---

## 🔧 설정 예제

### 환경변수 사용

```python
import os
from hybrid_trader import TradingConfig, KISConfig, UpbitConfig

# 환경변수에서 읽기
config = TradingConfig(
    kis_config=KISConfig(
        app_key=os.getenv("KIS_APP_KEY"),
        secret_key=os.getenv("KIS_SECRET_KEY"),
        account_number=os.getenv("KIS_ACCOUNT"),
        hts_id=os.getenv("KIS_HTS_ID"),
        is_demo=True
    ),
    upbit_config=UpbitConfig(
        access_key=os.getenv("UPBIT_ACCESS_KEY"),
        secret_key=os.getenv("UPBIT_SECRET_KEY")
    )
)
```

### JSON 설정 파일

```python
import json
from hybrid_trader import TradingConfig, KISConfig, UpbitConfig

# JSON 파일에서 읽기
with open("config.json", "r") as f:
    data = json.load(f)

config = TradingConfig(
    kis_config=KISConfig(**data["kis"]),
    upbit_config=UpbitConfig(**data["upbit"])
)
```

### 설정 파일 (config.json)

```json
{
    "kis": {
        "app_key": "your_app_key",
        "secret_key": "your_secret_key",
        "account_number": "1234-5678",
        "hts_id": "your_hts_id",
        "is_demo": true
    },
    "upbit": {
        "access_key": "your_access_key",
        "secret_key": "your_secret_key"
    }
}
```

### 검증 함수

```python
def create_validated_config(kis_cfg: KISConfig, upbit_cfg: UpbitConfig) -> TradingConfig:
    """설정을 검증한 후 생성합니다."""
    
    # 개별 검증
    kis_cfg.validate()
    upbit_cfg.validate()
    
    # 통합 검증
    config = TradingConfig(kis_config=kis_cfg, upbit_config=upbit_cfg)
    config.validate()
    
    return config
```

---

## ⚙️ 테스트 모드

### 테스트 모드 활성화

```python
# is_demo=True로 설정하면 실제 거래 없이 테스트 가능
kis_config = KISConfig(
    ...,
    is_demo=True  # 테스트 모드
)
```

### 테스트 모드의 장점

- 실제 돈을 사용하지 않음
- API 호출 한도를 덜 소모
- 신속한 테스트 가능
- 프로덕션 배포 전 검증

---

## 🔒 보안 모범 사례

### ✅ 올바른 방법

```python
# 1. 환경변수 사용
import os
app_key = os.getenv("KIS_APP_KEY")

# 2. 설정 파일 + .gitignore
# .gitignore에 config.json 추가

# 3. AWS Secrets Manager, HashiCorp Vault 등 사용
```

### ❌ 피해야 할 방법

```python
# 절대 하지 마세요!
kis_config = KISConfig(
    app_key="ak1234567890",     # 절대 금지!
    secret_key="sk9876543210"   # 절대 금지!
)
```

---

## 🆘 설정 오류 해결

### ConfigurationError

설정이 유효하지 않을 때 발생합니다.

```python
from hybrid_trader.exceptions import ConfigurationError

try:
    config.validate()
except ConfigurationError as e:
    print(f"설정 오류: {e}")
    # 설정을 수정하고 다시 시도
```

### 일반적인 오류

| 오류 | 원인 | 해결책 |
|------|------|--------|
| `app_key is required` | KIS App Key 누락 | 환경변수 설정 확인 |
| `Invalid account number format` | 계좌번호 형식 오류 | XXXX-XXXX 형식 확인 |
| `access_key is required` | Upbit Access Key 누락 | 환경변수 설정 확인 |

---

## 📚 더 알아보기

- [Engine API](engine.md)
- [Monitoring API](monitoring.md)
- [설정 가이드](../guide/configuration.md)
