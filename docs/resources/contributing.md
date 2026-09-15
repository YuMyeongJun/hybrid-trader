# 기여 가이드

Hybrid Trader 프로젝트에 기여하는 방법을 소개합니다.

## 🙌 기여의 종류

### 1. 코드 기여

- 버그 수정
- 새로운 기능 추가
- 코드 최적화
- 테스트 추가

### 2. 문서 기여

- 문서 작성/수정
- 예제 추가
- 오타 수정
- 번역

### 3. 이슈 보고

- 버그 보고
- 기능 요청
- 개선 제안
- 질문

## 🚀 시작하기

### 1단계: Fork & Clone

```bash
# GitHub에서 Fork하기
# https://github.com/YuMyeongJun/hybrid-trader

# 로컬에 Clone
git clone https://github.com/YOUR_USERNAME/hybrid-trader.git
cd hybrid-trader
git remote add upstream https://github.com/YuMyeongJun/hybrid-trader.git
```

### 2단계: 개발 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 활성화 (macOS/Linux)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 3단계: Branch 생성

```bash
# 항상 main 또는 develop에서 시작
git checkout main
git pull upstream main

# 새로운 branch 생성
git checkout -b feature/your-feature-name
# 또는
git checkout -b fix/your-bug-fix
```

## 📝 코드 스타일 가이드

### PEP 8 준수

```python
# ✅ 올바른 스타일
def get_stock_price(ticker: str) -> Optional[float]:
    """주식 가격을 조회합니다."""
    if not ticker:
        raise ValueError("Ticker cannot be empty")
    
    return self._fetch_price(ticker)

# ❌ 나쁜 스타일
def getStockPrice(ticker):
    if(not ticker):
        raise ValueError("Ticker cannot be empty")
    return self._fetch_price(ticker)
```

### 타입 힌트 사용

```python
# ✅ 타입 힌트 포함
from typing import Optional, List

def buy_stock(
    self,
    ticker: str,
    quantity: int,
    price: Optional[float] = None
) -> Optional[OrderResult]:
    """주식을 매수합니다."""
    pass

# ❌ 타입 힌트 없음
def buy_stock(self, ticker, quantity, price=None):
    pass
```

### Docstring

```python
# ✅ 완벽한 Docstring
def get_coin_price(self, ticker: str) -> Optional[float]:
    """
    암호화폐의 현재가를 조회합니다.
    
    Args:
        ticker (str): 암호화폐 코드 (예: "KRW-BTC")
    
    Returns:
        float: 현재가 (KRW 단위)
        None: 조회 실패 시
    
    Raises:
        InvalidTickerError: 유효하지 않은 티커
        APIConnectionError: API 연결 오류
    
    Example:
        >>> price = engine.get_coin_price("KRW-BTC")
        >>> print(f"비트코인: {price:,.0f} KRW")
    """
    pass
```

### 코드 포맷팅

```bash
# Black으로 포맷팅
black hybrid_trader/

# isort로 import 정렬
isort hybrid_trader/

# Flake8로 스타일 확인
flake8 hybrid_trader/

# mypy로 타입 확인
mypy hybrid_trader/
```

## 🧪 테스트

### 테스트 작성

```bash
# 테스트 실행
pytest

# 특정 테스트 실행
pytest tests/test_engine.py

# 커버리지 확인
pytest --cov=hybrid_trader tests/
```

### 테스트 예제

```python
# tests/test_engine.py
import pytest
from hybrid_trader import HybridTradingEngine, TradingConfig, KISConfig, UpbitConfig
from hybrid_trader.exceptions import InvalidTickerError

@pytest.fixture
def engine():
    config = TradingConfig(
        kis_config=KISConfig(..., is_demo=True),
        upbit_config=UpbitConfig(...)
    )
    return HybridTradingEngine(config)

def test_get_stock_price(engine):
    """주식 가격 조회 테스트"""
    price = engine.get_stock_price("005930")
    assert isinstance(price, (int, float))
    assert price > 0

def test_invalid_ticker_raises_error(engine):
    """유효하지 않은 티커 테스트"""
    with pytest.raises(InvalidTickerError):
        engine.get_stock_price("999999")
```

## 📋 PR (Pull Request) 체크리스트

### PR 생성 전 확인

- [ ] Fork된 repository에서 작업했나요?
- [ ] 최신 main/develop에서 branch를 만들었나요?
- [ ] 새로운 기능/버그 수정에 대한 테스트를 작성했나요?
- [ ] 기존 테스트가 모두 통과하나요? (`pytest`)
- [ ] 코드 스타일을 확인했나요? (`black`, `flake8`)
- [ ] 타입 체크를 통과했나요? (`mypy`)
- [ ] 문서를 업데이트했나요?
- [ ] Commit 메시지가 명확한가요?

### Commit 메시지 가이드

```bash
# ✅ 좋은 커밋 메시지 형식
feat: Add price alert functionality
fix: Fix API connection timeout issue
docs: Update installation guide
test: Add unit tests for engine

# ❌ 나쁜 커밋 메시지
Update stuff
Fixed bug
WIP
asdf

# 자세한 설명이 필요한 경우
feat: Add price alert functionality

- Implement PriceAlert class
- Add alert triggering logic
- Add unit tests
- Update documentation
```

### PR 설명 템플릿

```markdown
## 📝 설명
이 PR은 [기능 설명 또는 버그 수정]을 합니다.

## 🎯 변경 사항
- [ ] 새로운 기능 추가
- [ ] 버그 수정
- [ ] 문서 업데이트
- [ ] 코드 리팩토링

## 📋 변경 내용
- 변경 사항 1
- 변경 사항 2
- 변경 사항 3

## 🧪 테스트 방법
```bash
pytest tests/test_new_feature.py
```

## 📸 스크린샷 (해당하는 경우)
[스크린샷 추가]

## ✅ 체크리스트
- [x] 코드 스타일 확인 (black, flake8)
- [x] 테스트 작성 및 통과
- [x] 문서 업데이트
- [x] 타입 체크 통과 (mypy)
```

## 🐛 이슈 보고

### 좋은 이슈 보고 예제

**제목**: 주식 가격 조회가 "timeout" 오류로 실패

**설명**:
```
## 현상
주식 가격 조회 시 다음 오류가 발생합니다:
APIConnectionError: Connection timeout

## 재현 방법
```python
engine = HybridTradingEngine(config)
price = engine.get_stock_price("005930")
```

## 예상되는 결과
가격이 정상적으로 반환되어야 함

## 실제 결과
APIConnectionError 발생

## 환경
- Python: 3.10.5
- hybrid-trader: 0.1.0
- OS: macOS 13.0

## 로그
```
Traceback (most recent call last):
  File "test.py", line 5, in <module>
    price = engine.get_stock_price("005930")
  ...
APIConnectionError: Connection timeout
```

## 추가 정보
인터넷 연결은 정상입니다.
```

## 📚 문서 작성 가이드

### 문서 추가 시

1. 적절한 위치에 `.md` 파일 생성
2. mkdocs.yml에 등록
3. 명확한 제목과 목차 포함
4. 코드 예제 포함
5. 관련 페이지로 링크

### 예제 코드 작성

```markdown
### 기본 사용법

```python
from hybrid_trader import HybridTradingEngine

with HybridTradingEngine(config) as engine:
    price = engine.get_stock_price("005930")
    print(f"가격: {price:,.0f} KRW")
```
```

## 🔄 PR 리뷰 프로세스

1. **자동 테스트**: 모든 테스트 통과 확인
2. **코드 리뷰**: 유지관리자가 코드 검토
3. **Feedback**: 필요한 수정사항 제시
4. **수정 & Rebase**: 변경사항 적용
5. **Approval**: 승인 후 merge

## 🏆 기여자 인정

모든 기여자는:

- Contributors 페이지에 나열됩니다
- Commit에서 인정됩니다
- 주요 기여는 README에 표시됩니다

## ⚠️ 커뮤니티 가이드

### 행동 강령

- 존중하는 태도 유지
- 건설적인 피드백 제공
- 다양성 존중
- 괴롭힘 및 학대 금지

### 어떻게 도움이 될 수 있나요?

- 질문에 답변하기
- 새 사용자 도와주기
- 문서 개선하기
- 예제 공유하기
- 버그 테스트하기

## 📞 도움 받기

- **GitHub Issues**: 기술적 문제
- **GitHub Discussions**: 질문 및 아이디어
- **Email**: dev.claude@blumn.ai

## 🎓 첫 기여 팁

1. **작은 것부터 시작**: typo 수정, 문서 개선 등
2. **커뮤니케이션**: PR 전에 이슈에서 의도 공유
3. **코드 스타일 학습**: 기존 코드를 참고
4. **테스트 작성**: 새 기능에는 테스트 필수
5. **피드백 수용**: 리뷰 코멘트를 학습 기회로

## 📖 참고 자료

- [Git 가이드](https://git-scm.com/book/ko/v2)
- [Python 스타일 가이드 (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Google Python 스타일 가이드](https://google.github.io/styleguide/pyguide.html)

---

## ✨ 감사합니다!

Hybrid Trader를 더 좋게 만들어주세요. 모든 기여는 소중합니다!

**❤️ Happy Contributing!**
