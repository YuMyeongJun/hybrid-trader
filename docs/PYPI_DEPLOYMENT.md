# PyPI Deployment Guide

이 문서는 `hybrid-trader` 패키지를 PyPI에 배포하는 방법을 설명합니다.

## 필수 조건

### 1. PyPI 계정 설정

#### PyPI 계정 생성
1. [PyPI 공식 웹사이트](https://pypi.org/) 방문
2. "Register" 클릭하여 계정 생성
3. 이메일 인증 완료

#### TestPyPI 계정 생성 (테스트용)
1. [TestPyPI 공식 웹사이트](https://test.pypi.org/) 방문
2. "Register" 클릭하여 계정 생성
3. 이메일 인증 완료

### 2. API Token 생성

#### PyPI API Token
1. PyPI 계정에 로그인
2. "Account settings" → "API tokens" 이동
3. "Add API token" 클릭
4. Token 생성 및 복사 (나중에 다시 볼 수 없음!)

#### TestPyPI API Token
1. TestPyPI 계정에 로그인
2. "Account settings" → "API tokens" 이동
3. "Add API token" 클릭
4. Token 생성 및 복사

### 3. 로컬 개발 환경 설정

```bash
# 필수 도구 설치
pip install --upgrade build twine wheel setuptools

# tokens을 환경변수로 설정 (선택사항)
export TEST_PYPI_API_TOKEN="pypi-..."  # TestPyPI token
export PYPI_API_TOKEN="pypi-..."       # PyPI token
```

## 로컬 배포 테스트

### 1단계: 패키지 빌드

```bash
# 프로젝트 디렉토리로 이동
cd /path/to/hybrid-trader

# 배포 패키지 빌드
python -m build

# 또는 setup.py 사용
python setup.py sdist bdist_wheel
```

빌드 결과:
- `dist/hybrid_trader-0.1.0-py3-none-any.whl` (Wheel)
- `dist/hybrid_trader-0.1.0.tar.gz` (Source Distribution)

### 2단계: 패키지 검증

```bash
# Twine을 사용한 검증
twine check dist/* --strict

# 또는 더 상세한 검증
twine check dist/hybrid_trader-0.1.0-py3-none-any.whl
twine check dist/hybrid_trader-0.1.0.tar.gz
```

### 3단계: TestPyPI에 업로드

```bash
# 방법 1: 환경변수 사용
twine upload dist/* \
    --repository testpypi \
    --username __token__ \
    --password $TEST_PYPI_API_TOKEN

# 방법 2: 대화형 입력
twine upload dist/* --repository testpypi

# 방법 3: 자동 스크립트 사용
bash scripts/test_pypi_deploy.sh
```

### 4단계: TestPyPI에서 설치 테스트

```bash
# TestPyPI에서 설치
pip install --index-url https://test.pypi.org/simple/ hybrid-trader

# 설치 확인
python -c "import hybrid_trader; print('Success!')"

# 패키지 정보 확인
pip show hybrid-trader
```

### 5단계: 버전 확인

TestPyPI에서: https://test.pypi.org/project/hybrid-trader/

## PyPI 배포 (프로덕션)

### 방법 1: GitHub Releases (권장)

이 방법이 가장 안전하고 자동화되어 있습니다.

```bash
# 1. 버전 업데이트 (setup.py, pyproject.toml에서)
# 예: 0.1.0 → 0.2.0

# 2. CHANGELOG.md 업데이트
# 변경 사항 기록

# 3. 커밋 및 푸시
git add .
git commit -m "Release version 0.2.0"
git push origin main

# 4. GitHub Release 생성
# https://github.com/mjyu-louis/hybrid-trader/releases/new
# Tag: v0.2.0 (또는 0.2.0)
# Release Notes: CHANGELOG.md 내용 참조

# 5. "Publish release" 클릭
# → CI/CD 자동 실행 (GitHub Actions)
# → TestPyPI 테스트
# → PyPI 자동 배포
```

### 방법 2: 로컬에서 수동 배포

```bash
# 1. 패키지 빌드
python -m build

# 2. PyPI에 업로드
twine upload dist/* -u __token__ -p $PYPI_API_TOKEN

# 또는 대화형 입력
twine upload dist/*
# 사용자명: __token__
# 비밀번호: (PyPI API token 붙여넣기)
```

### 방법 3: 환경변수 사용

```bash
# .env 파일에 저장 (절대 커밋하지 마세요!)
export PYPI_API_TOKEN="pypi-AgEIcHlwaS5vcmc..."

# 또는 sh 스크립트로
twine upload dist/* --username __token__ --password $PYPI_API_TOKEN
```

## 배포 후 검증

### PyPI 페이지 확인

https://pypi.org/project/hybrid-trader/

### 설치 테스트

```bash
# 새로운 가상환경에서 테스트
python -m venv /tmp/test_env
source /tmp/test_env/bin/activate

# 최신 버전 설치
pip install --upgrade hybrid-trader

# 설치 확인
python -c "from hybrid_trader import HybridTradingEngine; print('Success!')"

# 패키지 정보
pip show hybrid-trader

# 정리
deactivate
rm -rf /tmp/test_env
```

### 버전 확인

```bash
python -c "import hybrid_trader; print(hybrid_trader.__version__)"
```

## GitHub Actions CI/CD 설정

### 필수 Secrets 설정

GitHub Repository Settings → Secrets and variables → Actions

#### 1. PYPI_API_TOKEN
- **내용**: PyPI에서 발급받은 API token
- **예**: `pypi-AgEIcHlwaS5vcmc...`
- **참고**: 절대 공개하지 마세요!

#### 2. TEST_PYPI_API_TOKEN
- **내용**: TestPyPI에서 발급받은 API token
- **선택사항**: 테스트 배포에만 필요

#### 3. GITHUB_TOKEN
- **자동**: GitHub에서 자동으로 제공됨
- **추가 설정 불필요**

### Environments 설정 (선택사항)

GitHub Repository Settings → Environments에서:

#### release 환경
- **Protection rules**: 검토자 지정 가능
- **Secrets**: PYPI_API_TOKEN

#### release-test 환경
- **Secrets**: TEST_PYPI_API_TOKEN

## 버전 관리 및 배포 워크플로우

### 버전 체계
이 프로젝트는 [Semantic Versioning](https://semver.org/)을 따릅니다.

```
MAJOR.MINOR.PATCH
  0  .  1  .  0

- MAJOR: 호환성이 깨지는 변경
- MINOR: 역호환 기능 추가
- PATCH: 버그 수정
```

### 배포 체크리스트

- [ ] 모든 테스트 통과 (`pytest`)
- [ ] 코드 품질 검사 통과 (`flake8`, `black`, `mypy`)
- [ ] CHANGELOG.md 업데이트
- [ ] setup.py, pyproject.toml, setup.cfg에서 버전 일치 확인
- [ ] 최신 코드 커밋 및 푸시
- [ ] GitHub Release 생성
- [ ] CI/CD 완료 대기
- [ ] PyPI 페이지 확인
- [ ] 설치 테스트 완료

## 문제 해결

### 1. "version mismatch" 에러

**문제**: Tag와 setup.py 버전이 다름

```bash
# 해결책
# setup.py의 version 확인
grep 'version=' setup.py

# pyproject.toml의 version 확인  
grep 'version =' pyproject.toml

# setup.cfg의 version 확인
grep 'version =' setup.cfg
```

### 2. "twine check" 실패

**문제**: 패키지 메타데이터 형식 오류

```bash
# 상세 검증
twine check dist/* --strict -v

# 일반적인 원인:
# - README.md가 마크다운으로 인식되지 않음
# - 메타데이터가 UTF-8이 아님
# - Classifiers 형식 오류
```

### 3. 업로드 실패 (401 에러)

**문제**: API token 문제

```bash
# 확인사항
# 1. Token 복사 시 공백 확인
# 2. Token 권한 확인 (write 권한 필요)
# 3. Token 만료 여부 확인

# 테스트
twine upload dist/example.whl -u __token__ -p $PYPI_API_TOKEN --dry-run
```

### 4. 중복 버전 배포

**문제**: 같은 버전을 두 번 배포할 수 없음

```bash
# 해결책
# 1. 버전 업데이트
# 2. CHANGELOG 추가
# 3. 다시 커밋 및 릴리스 생성

# --skip-existing 옵션으로 무시 가능
twine upload dist/* --skip-existing
```

## 참고 링크

- [PyPI Official](https://pypi.org/)
- [TestPyPI](https://test.pypi.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Setuptools Documentation](https://setuptools.pypa.io/)
- [Python Packaging Guide](https://packaging.python.org/)
- [PEP 517 - Build System Interface](https://www.python.org/dev/peps/pep-0517/)
- [PEP 518 - Build Requirements](https://www.python.org/dev/peps/pep-0518/)
- [Semantic Versioning](https://semver.org/)

## 빠른 참고

### 자주 사용되는 명령어

```bash
# 전체 배포 테스트
bash scripts/test_pypi_deploy.sh

# 로컬 빌드
python -m build

# 패키지 검증
twine check dist/*

# TestPyPI 업로드
twine upload dist/* --repository testpypi -u __token__ -p $TEST_PYPI_API_TOKEN

# PyPI 업로드
twine upload dist/* -u __token__ -p $PYPI_API_TOKEN

# 설치 테스트
pip install hybrid-trader --upgrade

# 버전 확인
python -c "import hybrid_trader; print(getattr(hybrid_trader, '__version__', 'unknown'))"
```

## 지원

문제가 발생하면:
1. [GitHub Issues](https://github.com/mjyu-louis/hybrid-trader/issues) 확인
2. 자세한 에러 메시지와 함께 이슈 생성
3. 또는 풀 리퀘스트로 개선 제안
