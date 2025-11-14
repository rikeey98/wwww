# TDD 개발 규칙 (Python + uv)

## 🔧 프로젝트 초기화 체크

### 첫 작업 전 확인
```bash
# pyproject.toml 없으면 실행 필요
uv init
```

**확인 항목:**
- [ ] `pyproject.toml` 존재
- [ ] `uv.lock` 존재
- [ ] 가상환경 활성화 상태

## 🚫 절대 금지 사항
1. 테스트 없이 프로덕션 코드 작성 금지
2. 한 번에 여러 테스트 작성 금지
3. 내가 요청하지 않은 리팩토링 금지
4. 전체 아키텍처/구조 제안 금지
5. pip/poetry 명령어 사용 금지 (uv만 사용)

## ✅ 필수 프로세스

### RED: 실패하는 테스트 작성
- 단일 케이스만
- 가장 간단한 것부터
- 테스트 실행: `uv run pytest [파일명]`
- 결과 확인 후 대기

### GREEN: 테스트 통과
- 최소한의 코드만 작성
- "작동하게만" 만들기
- 리팩토링 하지 말 것

### REFACTOR: 명시적 요청 시에만
- 내가 "리팩토링해"라고 명령할 때만
- 테스트는 그대로 유지
- 실행: `uv run pytest` 로 검증

## 🧪 테스트 설정

### 테스트 프레임워크
```bash
# pytest 설치 (필요시)
uv add --dev pytest pytest-cov
```

### 파일 구조
```
project/
├── pyproject.toml
├── uv.lock
├── src/
│   └── module/
│       └── __init__.py
└── tests/
    └── test_module.py
```

### 테스트 파일명
- `test_*.py` 또는 `*_test.py`
- 함수명: `test_*`

## 📝 응답 형식

**테스트 작성 시:**
```
[RED] 테스트 추가:
- 케이스: [설명]
- 예상 결과: [결과]

# tests/test_validator.py
def test_empty_string_returns_false():
    assert validate("") == False

실행: uv run pytest tests/test_validator.py -v
```

**구현 시:**
```
[GREEN] 최소 구현:

# src/validator.py
def validate(value: str) -> bool:
    return value != ""

테스트 실행: uv run pytest
결과: ✅ 1 passed
```

## 🎯 작업 범위

- 함수 하나 = 작업 하나
- 10줄 이내 구현 선호
- 복잡하면 더 작게 쪼개기 제안

## 🔄 의존성 관리

### 패키지 추가
```bash
# 프로덕션 의존성
uv add [package]

# 개발 의존성
uv add --dev [package]
```

### 실행
```bash
# 테스트
uv run pytest

# 커버리지
uv run pytest --cov=src

# 특정 파일
uv run pytest tests/test_file.py -v
```

## 💬 커뮤니케이션

**잘못된 요청 시:**
"이 작업은 [X]개 테스트가 필요합니다. 첫 번째 테스트부터 시작할까요?"

**uv init 안 된 경우:**
"pyproject.toml이 없습니다. 먼저 `uv init` 실행이 필요합니다."

## 📋 예시 대화 흐름

**시작:**
```
User: "이메일 검증 함수 만들자"
Roo: "pyproject.toml 확인... OK
      첫 번째 테스트: 빈 문자열 검증부터 시작할까요?"

User: "응"
Roo: [RED] 
     def test_empty_email_returns_false():
         assert is_valid_email("") == False
     
     실행: uv run pytest tests/test_email.py
     결과: ❌ FAILED (함수 없음)

User: "통과시켜"
Roo: [GREEN]
     def is_valid_email(email: str) -> bool:
         return email != ""
     
     실행: uv run pytest
     결과: ✅ 1 passed

User: "다음 테스트"
Roo: [RED] 두 번째 테스트 제안
     - @ 기호 없으면 False?
```

## 🛠 Git 커밋 형식
```bash
# RED 단계
git commit -m "🔴 test: add empty email validation test"

# GREEN 단계  
git commit -m "🟢 feat: implement basic email validation"

# REFACTOR 단계
git commit -m "🔵 refactor: extract email pattern validation"
```

## ⚠️ 트러블슈팅

**"ModuleNotFoundError"**
→ `uv add [패키지명]`

**"uv: command not found"**
→ uv 설치: `curl -LsSf https://astral.sh/uv/install.sh | sh`

**테스트 실행 안 됨**
→ `uv run pytest -v` (경로 확인)

**Roo가 큰 코드 작성**
→ "STOP. RED 단계만. 테스트 1개만"

---

## 🚀 프로젝트 시작 체크리스트
```bash
# 1. 프로젝트 초기화 (없으면)
uv init

# 2. pytest 설치
uv add --dev pytest pytest-cov

# 3. 디렉터리 생성
mkdir -p src tests

# 4. 첫 대화 시작
"rules.md에 따라 작업하자. TDD로 [기능명] 만들자"
```

---

이제 이 파일을 프로젝트 루트에 `rules.md`로 저장하고,
Roo에게 "rules.md 읽고 시작" 하면 됩니다.

추가하고 싶은 규칙 있나요?
