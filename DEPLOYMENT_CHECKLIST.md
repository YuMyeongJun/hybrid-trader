# PyPI 배포 준비 완료 체크리스트

## 완료된 설정

### 1. 패키징 설정 파일 ✅

- [x] **setup.py** - 완벽한 메타데이터 포함
  - author: "MJ YU"
  - author_email: "dev.claude@blumn.ai"
  - maintainer 정보 포함
  - keywords 포함
  - 완벽한 classifiers (Python 3.8-3.12 지원)
  - python_requires=">=3.8"
  - extras_require (dev, test, lint)
  - project_urls 포함

- [x] **pyproject.toml** - PEP 517/518 준수
  - [build-system] 섹션
  - [project] 메타데이터
  - [project.optional-dependencies]
  - [tool.*] 설정 (black, isort, mypy, pytest)

- [x] **setup.cfg** - 보조 설정
  - [metadata] 완전 구성
  - [options] 의존성
  - [bdist_wheel] 설정

- [x] **MANIFEST.in** - 배포 파일 포함 지정
  - README.md, LICENSE, CHANGELOG.md
  - docs/ 모든 .md 파일
  - examples/ 모든 .py 파일
  - tests/ 모든 .py 파일
  - 불필요한 파일 제외

### 2. 문서 파일 ✅

- [x] **README.md** - 완벽한 프로젝트 설명
- [x] **CHANGELOG.md** - 버전 이력
- [x] **LICENSE** - MIT 라이선스
- [x] **docs/PYPI_DEPLOYMENT.md** - 배포 가이드
- [x] **docs/** - 완벽한 문서
  - API.md
  - ARCHITECTURE.md
  - CONTRIBUTING.md
  - EXAMPLES.md
  - INSTALLATION.md
  - TROUBLESHOOTING.md

### 3. 배포 도구 ✅

- [x] **scripts/test_pypi_deploy.sh** - 배포 테스트 스크립트
- [x] **.github/workflows/deploy.yml** - CI/CD 자동 배포
  - 5단계 자동화 파이프라인
  - TestPyPI 검증
  - 여러 Python 버전 테스트 (3.8-3.12)

### 4. 빌드 및 검증 ✅

- [x] 로컬 빌드 성공
  - hybrid_trader-0.1.0-py3-none-any.whl
  - hybrid_trader-0.1.0.tar.gz

- [x] Twine 검증 완료
  ```
  Checking dist/hybrid_trader-0.1.0-py3-none-any.whl: PASSED
  Checking dist/hybrid_trader-0.1.0.tar.gz: PASSED
  ```

---

## 첫 번째 배포를 위한 단계별 가이드

### Step 1: 로컬 환경 준비

```bash
# 필수 도구 설치
pip install --upgrade build twine wheel setuptools

# 테스트 배포 (권장)
bash scripts/test_pypi_deploy.sh
```

### Step 2: PyPI 계정 설정

1. [PyPI](https://pypi.org/) 계정 생성
2. [TestPyPI](https://test.pypi.org/) 계정 생성
3. 각각 API token 생성
   - PyPI API token 저장
   - TestPyPI API token 저장

### Step 3: GitHub Secrets 설정

Repository Settings → Secrets and variables → Actions

#### 필수 Secrets

| 이름 | 값 | 용도 |
|------|-----|------|
| `PYPI_API_TOKEN` | PyPI token | 프로덕션 배포 |
| `TEST_PYPI_API_TOKEN` | TestPyPI token | 테스트 배포 (선택) |

**보안 주의**: 절대 코드에 token을 포함하지 마세요!

### Step 4: 환경 설정 (GitHub Actions)

Settings → Environments → Add environment

#### release 환경 (권장)
- 배포 전 승인 보호
- PYPI_API_TOKEN secret 추가

#### release-test 환경
- TEST_PYPI_API_TOKEN secret 추가

### Step 5: 첫 배포 실행

```bash
# 옵션 1: GitHub Releases (자동화, 권장)
1. https://github.com/mjyu-louis/hybrid-trader/releases/new
2. Tag version: v0.1.0
3. Release name: Release 0.1.0
4. Description: CHANGELOG 내용 참조
5. "Publish release" 클릭
6. CI/CD 자동 실행 → PyPI 배포

# 옵션 2: 로컬 수동 배포
python -m build
twine upload dist/* --username __token__ --password $PYPI_API_TOKEN
```

### Step 6: 배포 검증

```bash
# PyPI에서 확인
# https://pypi.org/project/hybrid-trader/

# 설치 테스트
pip install hybrid-trader

# 동작 확인
python -c "from hybrid_trader import HybridTradingEngine; print('Success!')"
```

---

## 계속된 유지보수

### 새 버전 배포 절차

1. **코드 변경 및 테스트**
   ```bash
   git checkout -b feature/new-feature
   # 코드 수정...
   pytest  # 모든 테스트 통과 확인
   ```

2. **버전 업데이트**
   - setup.py에서 version 업데이트
   - pyproject.toml에서 version 업데이트
   - setup.cfg에서 version 업데이트
   - CHANGELOG.md 업데이트

3. **코드 푸시**
   ```bash
   git add .
   git commit -m "Release version X.Y.Z"
   git push origin main
   ```

4. **GitHub Release 생성**
   - Tag: vX.Y.Z
   - Release notes: CHANGELOG.md 내용

5. **CI/CD 자동 실행**
   - TestPyPI에 자동 배포
   - 검증 후 PyPI 배포

6. **배포 후 검증**
   ```bash
   pip install --upgrade hybrid-trader
   ```

---

## 배포 실패 대응

### 빌드 실패
```bash
# 원인 분석
python -m build -v

# 의존성 확인
pip install -r requirements.txt

# setup.py 재확인
python setup.py check
```

### Twine 검증 실패
```bash
twine check dist/* --strict -v
# 메타데이터 형식 확인
```

### API Token 문제
- Token 복사 시 공백 제거
- Token 권한 확인 (write 권한 필요)
- Token 만료 여부 확인
- 새로운 token 발급

---

## 유용한 명령어

```bash
# 전체 배포 테스트
bash scripts/test_pypi_deploy.sh

# 로컬 빌드
python -m build

# 검증
twine check dist/*

# TestPyPI 업로드
twine upload dist/* --repository testpypi -u __token__ -p $TEST_PYPI_API_TOKEN

# PyPI 업로드
twine upload dist/* -u __token__ -p $PYPI_API_TOKEN

# 설치
pip install hybrid-trader

# 버전 확인
pip show hybrid-trader

# 언인스톨
pip uninstall hybrid-trader -y
```

---

## 참고 링크

| 링크 | 설명 |
|------|------|
| [PyPI Package](https://pypi.org/project/hybrid-trader/) | 공개 패키지 페이지 |
| [GitHub Repository](https://github.com/mjyu-louis/hybrid-trader) | 소스 코드 |
| [GitHub Releases](https://github.com/mjyu-louis/hybrid-trader/releases) | 배포 이력 |
| [TestPyPI Package](https://test.pypi.org/project/hybrid-trader/) | 테스트 페이지 |
| [Twine Docs](https://twine.readthedocs.io/) | 배포 도구 문서 |
| [Setuptools Docs](https://setuptools.pypa.io/) | 패키징 도구 문서 |
| [Python Packaging](https://packaging.python.org/) | 공식 가이드 |

---

## 상태 요약

**현재 상태**: ✅ PyPI 배포 준비 완료

### 완료된 항목
- ✅ setup.py, pyproject.toml, setup.cfg 완벽 설정
- ✅ MANIFEST.in 배포 파일 구성
- ✅ CHANGELOG.md 버전 이력
- ✅ 배포 가이드 문서 (PYPI_DEPLOYMENT.md)
- ✅ 배포 스크립트 (test_pypi_deploy.sh)
- ✅ GitHub Actions CI/CD 자동화
- ✅ 로컬 빌드 및 검증 완료
- ✅ Twine 메타데이터 검증 완료

### 다음 단계
1. GitHub Secrets 설정 (PYPI_API_TOKEN, TEST_PYPI_API_TOKEN)
2. 로컬 테스트 배포 실행 (bash scripts/test_pypi_deploy.sh)
3. GitHub Release 생성 → 자동 배포 실행

### 설치 명령어 (향후)
```bash
pip install hybrid-trader
```

---

**Created**: 2026-09-15
**Status**: Ready for production deployment
**Next Release**: Follow the "New Version Deployment Procedure" above
