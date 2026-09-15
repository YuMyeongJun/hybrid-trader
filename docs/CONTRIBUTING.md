# 기여 가이드 (Contributing Guide)

Hybrid Trader 프로젝트에 기여하고 싶으신가요? 이 가이드를 따라주세요!

## 목차

- [기여 방법](#기여-방법)
- [개발 환경 설정](#개발-환경-설정)
- [코드 스타일](#코드-스타일)
- [테스트 작성](#테스트-작성)
- [PR 작성 가이드](#pr-작성-가이드)
- [이슈 보고](#이슈-보고)
- [문서 작성](#문서-작성)
- [행동 강령](#행동-강령)

---

## 기여 방법

### 1. 버그 보고

버그를 발견했다면 [Issues](https://github.com/yourusername/hybrid-trader/issues)에서 보고해주세요.

**버그 보고 템플릿**:

```markdown
## 버그 설명
간단하고 명확한 설명을 해주세요.

## 재현 방법
재현 단계:
1. '...' 로 이동
2. '...' 클릭
3. '...' 입력
4. 오류 발생

## 기대되는 행동
정상적으로 작동되어야 할 방식을 설명하세요.

## 스크린샷
해당되면 스크린샷을 추가하세요.

## 환경
- OS: Windows 10
- Python 버전: 3.9
- Hybrid Trader 버전: 0.1.0

## 추가 정보
기타 추가 정보가 있으면 입력하세요.
```

### 2. 기능 제안

새로운 기능을 제안하려면 [Issues](https://github.com/yourusername/hybrid-trader/issues)에서 "Feature Request"로 작성해주세요.

**기능 제안 템플릿**:

```markdown
## 기능 설명
추가되었으면 하는 기능을 설명하세요.

## 이 기능이 해결하는 문제
어떤 문제를 해결하는지 설명하세요.

## 가능한 구현 방법
기능을 어떻게 구현할 수 있을지 제안하세요.

## 추가 정보
기타 추가 정보가 있으면 입력하세요.
```

### 3. 코드 기여

#### 단계별 과정

**1단계: Fork & Clone**

```bash
# GitHub에서 이 저장소를 Fork
git clone https://github.com/your-username/hybrid-trader.git
cd hybrid-trader
```

**2단계: 브랜치 생성**

```bash
# main 브랜치에서 새 브랜치 생성
git checkout -b feature/amazing-feature

# 또는 버그 수정인 경우
git checkout -b fix/bug-description
```

**브랜치 이름 규칙**:
- 기능 추가: `feature/description`
- 버그 수정: `fix/description`
- 문서 수정: `docs/description`
- 스타일 정리: `style/description`

**3단계: 개발 환경 설정**

[개발 환경 설정](#개발-환경-설정) 섹션을 참고하세요.

**4단계: 코드 작성**

[코드 스타일](#코드-스타일)을 따라주세요.

**5단계: 테스트 작성**

[테스트 작성](#테스트-작성) 섹션을 참고하세요.

**6단계: Commit**

```bash
git add .
git commit -m "feat: Add amazing feature"
```

**Commit 메시지 규칙**:
- `feat:` - 새로운 기능
- `fix:` - 버그 수정
- `docs:` - 문서 변경
- `style:` - 코드 스타일 변경
- `refactor:` - 코드 리팩토링
- `test:` - 테스트 추가
- `chore:` - 기타 변경

**7단계: Push & PR 작성**

```bash
git push origin feature/amazing-feature
```

그 후 GitHub에서 Pull Request를 작성하세요. [PR 작성 가이드](#pr-작성-가이드)를 참고하세요.

---

## 개발 환경 설정

### 1단계: 가상 환경 생성

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2단계: 의존성 설치

```bash
# 기본 의존성
pip install -r requirements.txt

# 개발 의존성 추가
pip install pytest pytest-cov black flake8 isort mypy
```

### 3단계: 개발 모드 설치

```bash
pip install -e .
```

### 4단계: Pre-commit Hooks 설정 (선택)

```bash
pip install pre-commit
pre-commit install
```

이제 commit 전에 자동으로 코드 스타일 검사가 실행됩니다.

---

## 코드 스타일

### Python 스타일 가이드

Hybrid Trader는 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 스타일 가이드를 따릅니다.

### 1. Black으로 포매팅

```bash
# 모든 파일 포매팅
black hybrid_trader/ examples/ tests/

# 특정 파일 포매팅
black hybrid_trader/engine.py
```

### 2. isort로 import 정렬

```bash
# import 자동 정렬
isort hybrid_trader/ examples/ tests/
```

### 3. Flake8로 코드 검사

```bash
# 코드 스타일 검사
flake8 hybrid_trader/ examples/ tests/

# 특정 오류만 무시
flake8 --ignore=E203,W503 hybrid_trader/
```

### 4. mypy로 타입 검사

```bash
# 타입 검사
mypy hybrid_trader/

# 특정 파일 검사
mypy hybrid_trader/engine.py
```

### 코드 작성 규칙

#### 1. 타입 힌트 사용

```python
# 권장
def get_stock_price(self, ticker: str) -> Optional[float]:
    """한국투자증권 API를 통해 주식의 현재가를 조회합니다."""
    ...

# 비권장
def get_stock_price(self, ticker):
    ...
```

#### 2. Docstring 작성

```python
def get_stock_price(self, ticker: str) -> Optional[float]:
    """Get current stock price from Korea Investment & Securities.

    한국투자증권 API를 통해 주식의 현재가를 조회합니다.

    Args:
        ticker (str): Stock ticker code (e.g., "005930" for Samsung Electronics)

    Returns:
        Optional[float]: Current stock price in KRW, or None if unavailable.

    Raises:
        ValueError: If ticker format is invalid.
        Exception: If API request fails after retry attempts.

    Example:
        >>> engine = HybridTradingEngine(config)
        >>> price = engine.get_stock_price("005930")
        >>> print(f"Samsung Electronics: {price:,.0f} KRW")
    """
```

#### 3. 한글 주석과 영문 docstring

```python
# 한글 주석: 코드 설명
# 단계별 처리를 위한 재시도 로직

# 영문 docstring: 공식 문서
def method(self):
    """English description for official documentation."""
```

#### 4. 의미 있는 변수명

```python
# 권장
retry_count = 3
api_timeout_seconds = 10

# 비권장
rc = 3
t = 10
```

#### 5. 길이 제한

- 한 줄 최대 88자 (Black 기본값)
- 함수: 한 함수는 20줄 이하로 (가능한 한)

---

## 테스트 작성

### 테스트 구조

```
tests/
├── __init__.py
├── test_config.py       # config.py 테스트
└── test_engine.py       # engine.py 테스트
```

### 테스트 작성 방법

```python
# tests/test_engine.py
import pytest
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig


class TestHybridTradingEngine:
    """HybridTradingEngine 테스트"""

    @pytest.fixture
    def config(self):
        """테스트용 설정"""
        kis_cfg = KISConfig(
            app_key="test_key",
            secret_key="test_secret",
            account_number="1234-5678",
            hts_id="test_hts"
        )
        upbit_cfg = UpbitConfig(
            access_key="test_access",
            secret_key="test_secret"
        )
        return TradingConfig(kis_config=kis_cfg, upbit_config=upbit_cfg)

    def test_initialization(self, config):
        """엔진 초기화 테스트"""
        engine = HybridTradingEngine(config)
        assert engine.config == config

    def test_get_stock_price_invalid_ticker(self, config):
        """invalid ticker로 ValueError 발생"""
        engine = HybridTradingEngine(config)
        
        with pytest.raises(ValueError):
            engine.get_stock_price("")

    def test_context_manager(self, config):
        """Context Manager 사용"""
        with HybridTradingEngine(config) as engine:
            assert engine is not None
```

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 파일만 실행
pytest tests/test_engine.py

# 자세한 출력
pytest -v

# 코드 커버리지 확인
pytest --cov=hybrid_trader

# 특정 테스트만 실행
pytest tests/test_engine.py::TestHybridTradingEngine::test_initialization
```

### 테스트 작성 체크리스트

- [ ] 모든 public 메서드를 테스트했는가?
- [ ] 정상 케이스만 테스트했는가? (예외 케이스도 필요!)
- [ ] 경계값 테스트를 했는가?
- [ ] Mock 객체를 사용했는가? (외부 API 호출 피하기)
- [ ] 테스트 이름이 명확한가?

---

## PR 작성 가이드

### PR 템플릿

```markdown
## 변경 내용
이 PR이 무엇을 변경하는지 명확하게 설명하세요.

## 이슈와의 연관성
Fixes #(issue number)
또는
Related to #(issue number)

## 변경 유형
- [ ] 버그 수정 (Bug fix)
- [ ] 새로운 기능 (New feature)
- [ ] 기존 기능 개선 (Enhancement)
- [ ] 문서 업데이트 (Documentation)
- [ ] 코드 스타일 정리 (Style)
- [ ] 테스트 추가 (Test)

## 테스트
- [ ] 새 테스트를 추가했는가?
- [ ] 기존 테스트가 모두 통과하는가?
- [ ] 코드 커버리지가 감소하지 않았는가?

## 체크리스트
- [ ] 코드 스타일을 따랐는가? (Black, isort, flake8)
- [ ] Docstring을 작성했는가?
- [ ] 한글 설명을 추가했는가?
- [ ] 타입 힌트를 사용했는가?
- [ ] 기존 테스트가 모두 통과하는가?
- [ ] 새 기능에 대한 테스트를 작성했는가?

## 스크린샷 (필요시)
변경사항을 시각적으로 보여주세요.
```

### PR 리뷰 과정

1. **Automated Checks**: 자동 테스트와 코드 스타일 검사
2. **Code Review**: 유지보수자의 코드 리뷰
3. **Approval**: 최소 1명의 승인
4. **Merge**: main 브랜치에 병합

---

## 이슈 보고

### 버그 보고 예시

```markdown
## 버그 설명
get_stock_price()를 호출하면 항상 None을 반환합니다.

## 재현 방법
1. 다음 코드 실행:
```python
from hybrid_trader import HybridTradingEngine, TradingConfig
config = TradingConfig(...)
engine = HybridTradingEngine(config)
price = engine.get_stock_price("005930")
print(price)  # None 출력
```

## 기대되는 행동
현재가(예: 75500.0)가 출력되어야 합니다.

## 환경
- OS: macOS 12.0
- Python: 3.10
- Hybrid Trader: 0.1.0
- python-kis: 0.3.0
- pyupbit: 0.2.35

## 로그
```
[ERROR] hybrid_trader.engine: Failed to get stock price for 005930: ...
```
```

---

## 문서 작성

### 문서 추가/수정

문서는 다음 위치에서 관리합니다:

```
docs/
├── INSTALLATION.md     # 설치 가이드
├── API.md             # API 문서
├── ARCHITECTURE.md    # 아키텍처 설명
├── EXAMPLES.md        # 사용 예제
├── CONTRIBUTING.md    # 기여 가이드 (이 파일)
└── TROUBLESHOOTING.md # 문제 해결 가이드
```

### 마크다운 작성 규칙

```markdown
# 주제 (h1)

## 소제목 (h2)

### 작은 주제 (h3)

- 목록 항목 1
- 목록 항목 2

1. 순서 있는 항목 1
2. 순서 있는 항목 2

**굵게** (강조)
_기울기_ (강조)
`코드` (인라인 코드)

```python
# 코드 블록
def example():
    pass
```

| 테이블 | 헤더 |
|--------|------|
| 셀 1   | 셀 2 |

> 인용

[링크](https://example.com)
```

---

## 행동 강령

### 우리의 약속

Hybrid Trader 커뮤니티는 모든 사람을 존중하고 환영합니다.

### 우리의 기준

- 다양성과 포함성을 존중합니다
- 건설적인 피드백을 제공합니다
- 성별, 성적 지향, 장애, 국적, 종교 등을 이유로 차별하지 않습니다

### 용인되지 않는 행동

- 괴롭힘, 폭력, 협박
- 욕설, 명예 훼손
- 차별적 언어나 행동
- 원치 않는 성적 관심
- 기타 비전문적인 행동

### 위반 보고

행동 강령 위반을 목격했다면, 프로젝트 유지보수자에게 비공개로 보고해주세요.

---

## 추가 리소스

- [GitHub Guides](https://guides.github.com/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Pytest Documentation](https://docs.pytest.org/)

---

## 다음 단계

기여를 고려해주셔서 감사합니다! 질문이 있으시면 Issues에서 문의해주세요.

**Happy Contributing! 🚀**
