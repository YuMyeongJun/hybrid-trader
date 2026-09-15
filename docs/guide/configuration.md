# 고급 설정 가이드

Hybrid Trader의 고급 설정 방법을 소개합니다.

## 🎯 기본 설정

### 간단한 설정

```python
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig
import os

# 환경변수에서 읽기
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

config = TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
engine = HybridTradingEngine(config)
```

## 🔧 고급 설정

### 1. 다중 환경 설정

```python
import os
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "dev"
    TESTING = "test"
    PRODUCTION = "prod"

def get_config(env: Environment) -> TradingConfig:
    """환경에 따른 설정을 반환합니다."""
    
    if env == Environment.DEVELOPMENT:
        return TradingConfig(
            kis_config=KISConfig(
                app_key=os.getenv("DEV_KIS_APP_KEY"),
                secret_key=os.getenv("DEV_KIS_SECRET_KEY"),
                account_number=os.getenv("DEV_KIS_ACCOUNT"),
                hts_id=os.getenv("DEV_KIS_HTS_ID"),
                is_demo=True  # 테스트 모드
            ),
            upbit_config=UpbitConfig(
                access_key=os.getenv("DEV_UPBIT_ACCESS_KEY"),
                secret_key=os.getenv("DEV_UPBIT_SECRET_KEY")
            )
        )
    
    elif env == Environment.TESTING:
        return TradingConfig(
            kis_config=KISConfig(
                app_key=os.getenv("TEST_KIS_APP_KEY"),
                secret_key=os.getenv("TEST_KIS_SECRET_KEY"),
                account_number=os.getenv("TEST_KIS_ACCOUNT"),
                hts_id=os.getenv("TEST_KIS_HTS_ID"),
                is_demo=True  # 항상 테스트 모드
            ),
            upbit_config=UpbitConfig(
                access_key=os.getenv("TEST_UPBIT_ACCESS_KEY"),
                secret_key=os.getenv("TEST_UPBIT_SECRET_KEY")
            )
        )
    
    else:  # PRODUCTION
        return TradingConfig(
            kis_config=KISConfig(
                app_key=os.getenv("PROD_KIS_APP_KEY"),
                secret_key=os.getenv("PROD_KIS_SECRET_KEY"),
                account_number=os.getenv("PROD_KIS_ACCOUNT"),
                hts_id=os.getenv("PROD_KIS_HTS_ID"),
                is_demo=False  # 실거래 모드
            ),
            upbit_config=UpbitConfig(
                access_key=os.getenv("PROD_UPBIT_ACCESS_KEY"),
                secret_key=os.getenv("PROD_UPBIT_SECRET_KEY")
            )
        )

# 사용 예시
env = Environment.DEVELOPMENT
config = get_config(env)
engine = HybridTradingEngine(config)
```

### 2. JSON 설정 파일

```python
import json
from pathlib import Path

def load_config_from_json(config_file: str) -> TradingConfig:
    """JSON 파일에서 설정을 로드합니다."""
    
    with open(config_file, "r") as f:
        config_data = json.load(f)
    
    kis_config = KISConfig(
        app_key=config_data["kis"]["app_key"],
        secret_key=config_data["kis"]["secret_key"],
        account_number=config_data["kis"]["account_number"],
        hts_id=config_data["kis"]["hts_id"],
        is_demo=config_data["kis"].get("is_demo", False)
    )
    
    upbit_config = UpbitConfig(
        access_key=config_data["upbit"]["access_key"],
        secret_key=config_data["upbit"]["secret_key"]
    )
    
    return TradingConfig(kis_config=kis_config, upbit_config=upbit_config)

# config.json 예시
"""
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
"""

# 사용 예시
config = load_config_from_json("config.json")
engine = HybridTradingEngine(config)
```

### 3. YAML 설정 파일

```bash
# 먼저 PyYAML 설치
pip install pyyaml
```

```python
import yaml
from pathlib import Path

def load_config_from_yaml(config_file: str) -> TradingConfig:
    """YAML 파일에서 설정을 로드합니다."""
    
    with open(config_file, "r") as f:
        config_data = yaml.safe_load(f)
    
    kis_config = KISConfig(
        app_key=config_data["kis"]["app_key"],
        secret_key=config_data["kis"]["secret_key"],
        account_number=config_data["kis"]["account_number"],
        hts_id=config_data["kis"]["hts_id"],
        is_demo=config_data["kis"].get("is_demo", False)
    )
    
    upbit_config = UpbitConfig(
        access_key=config_data["upbit"]["access_key"],
        secret_key=config_data["upbit"]["secret_key"]
    )
    
    return TradingConfig(kis_config=kis_config, upbit_config=upbit_config)

# config.yaml 예시
"""
kis:
  app_key: your_app_key
  secret_key: your_secret_key
  account_number: "1234-5678"
  hts_id: your_hts_id
  is_demo: true

upbit:
  access_key: your_access_key
  secret_key: your_secret_key
"""

# 사용 예시
config = load_config_from_yaml("config.yaml")
engine = HybridTradingEngine(config)
```

### 4. 데이터클래스 검증

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class EnhancedTradingConfig:
    """향상된 거래 설정"""
    
    kis_config: KISConfig
    upbit_config: UpbitConfig
    
    # 선택적 설정
    log_level: str = "INFO"
    retry_attempts: int = 3
    timeout_seconds: int = 30
    enable_monitoring: bool = True
    
    def __post_init__(self):
        """초기화 후 검증"""
        self.kis_config.validate()
        self.upbit_config.validate()
        
        # 로그 레벨 검증
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            raise ValueError(f"Invalid log level: {self.log_level}")
        
        # 재시도 횟수 검증
        if not 1 <= self.retry_attempts <= 5:
            raise ValueError("retry_attempts must be between 1 and 5")

# 사용 예시
config = EnhancedTradingConfig(
    kis_config=kis_config,
    upbit_config=upbit_config,
    log_level="DEBUG",
    retry_attempts=3
)
```

## 📝 로깅 설정

### 기본 로깅 설정

```python
import logging

# 기본 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Hybrid Trader 로깅
logger = logging.getLogger('hybrid_trader')
logger.setLevel(logging.DEBUG)
```

### 파일로 로깅

```python
import logging
from logging.handlers import RotatingFileHandler

# 로깅 설정
logger = logging.getLogger('hybrid_trader')
logger.setLevel(logging.DEBUG)

# 파일 핸들러 (최대 5MB, 5개 백업 파일)
handler = RotatingFileHandler(
    'hybrid_trader.log',
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5
)

# 포맷 설정
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

logger.addHandler(handler)
```

### 모듈별 로깅 설정

```python
import logging

# 각 모듈별로 로깅 설정
logging.getLogger('hybrid_trader.engine').setLevel(logging.DEBUG)
logging.getLogger('hybrid_trader.monitoring').setLevel(logging.INFO)
logging.getLogger('hybrid_trader.config').setLevel(logging.WARNING)
```

## 🔐 비밀번호 관리

### python-dotenv 사용

```bash
# 설치
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경변수 사용
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
```

### AWS Secrets Manager 사용

```bash
pip install boto3
```

```python
import boto3
import json

def get_config_from_aws() -> TradingConfig:
    """AWS Secrets Manager에서 설정을 가져옵니다."""
    
    client = boto3.client('secretsmanager', region_name='ap-northeast-2')
    
    try:
        response = client.get_secret_value(SecretId='hybrid-trader-config')
        secret = json.loads(response['SecretString'])
        
        kis_config = KISConfig(
            app_key=secret['kis']['app_key'],
            secret_key=secret['kis']['secret_key'],
            account_number=secret['kis']['account_number'],
            hts_id=secret['kis']['hts_id']
        )
        
        upbit_config = UpbitConfig(
            access_key=secret['upbit']['access_key'],
            secret_key=secret['upbit']['secret_key']
        )
        
        return TradingConfig(kis_config=kis_config, upbit_config=upbit_config)
    
    except Exception as e:
        raise ConfigurationError("Failed to load config from AWS", str(e))
```

## ⚙️ 프로덕션 설정 체크리스트

- [ ] 모든 API 키를 환경변수로 설정
- [ ] 테스트 모드(`is_demo=False`)로 설정
- [ ] 로깅을 파일로 저장
- [ ] 에러 처리 추가
- [ ] 모니터링 활성화
- [ ] 백업 계획 수립
- [ ] 네트워크 모니터링 설정
- [ ] 정기적인 감사 로그 검토

## 🧪 설정 검증

```python
def validate_config(config: TradingConfig) -> bool:
    """설정이 유효한지 검증합니다."""
    
    try:
        # TradingConfig 검증
        config.validate()
        
        # 각 설정 검증
        kis_config = config.kis_config
        upbit_config = config.upbit_config
        
        # API 키 형식 검증
        if not isinstance(kis_config.app_key, str) or len(kis_config.app_key) == 0:
            raise ValueError("Invalid KIS app_key")
        
        if not isinstance(kis_config.secret_key, str) or len(kis_config.secret_key) == 0:
            raise ValueError("Invalid KIS secret_key")
        
        if not isinstance(upbit_config.access_key, str) or len(upbit_config.access_key) == 0:
            raise ValueError("Invalid Upbit access_key")
        
        if not isinstance(upbit_config.secret_key, str) or len(upbit_config.secret_key) == 0:
            raise ValueError("Invalid Upbit secret_key")
        
        return True
    
    except Exception as e:
        print(f"설정 검증 실패: {str(e)}")
        return False

# 사용 예시
if validate_config(config):
    engine = HybridTradingEngine(config)
else:
    print("설정이 유효하지 않습니다")
```

---

## 📚 다음 단계

- [예제](examples.md) - 실전 코드 예제
- [아키텍처](architecture.md) - 시스템 구조
- [API 레퍼런스](../api/overview.md) - 전체 API 문서
