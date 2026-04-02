# jira-delay-sync 개발 설계 문서 v1.0

> Jira 지연 사유 수집 및 DB 적재 자동화 파이프라인

---

## 1. 프로젝트 개요

Jira에서 지연된 이슈를 주기적으로 수집하고, 각 이슈의 커멘트에서 지연 사유 키워드를 탐지하여 Oracle DB에 적재하는 자동화 파이프라인입니다. Apache Airflow DAG으로 실행되며 uv 기반으로 환경을 관리합니다.

---

## 2. 처리 흐름

```
Jira JQL (지연 조건)
  → 이슈 목록 조회
  → 각 이슈 커멘트 조회
  → 키워드 필터링
  → DB 중복 체크 (TASK_ID + COMMENT_ID)
  → 신규만 INSERT
```

| 단계 | 설명 |
|------|------|
| 1. Jira 이슈 조회 | JQL 조건으로 지연 이슈 목록 조회 (조건 config에서 관리) |
| 2. 커멘트 조회 | 각 이슈의 커멘트 목록 조회 |
| 3. 키워드 필터링 | 커멘트 본문에서 지연 사유 키워드 탐지 |
| 4. 중복 체크 | TASK_ID + COMMENT_ID 기준으로 기존 DB 조회 |
| 5. DB INSERT | 신규 지연 사유만 Oracle DB에 INSERT (history 보존) |

---

## 3. 프로젝트 구조

```
jira-delay-sync/
├── dags/
│   └── delay_sync_dag.py           # Airflow DAG 정의
├── src/
│   └── jira_delay_sync/
│       ├── config.py               # JQL 조건, 키워드, 접속 설정
│       ├── jira_client.py          # Jira REST API 연동
│       ├── db_client.py            # Oracle DB 접근 (중복 체크, INSERT)
│       └── sync.py                 # 메인 오케스트레이션 로직
├── pyproject.toml
└── .env
```

---

## 4. DB 테이블 설계

### 4.1 DELAY_REASON 테이블

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| ID | NUMBER | PK, Sequence 자동 생성 |
| TASK_ID | NUMBER | FK → 기존 Jira 이슈 테이블 |
| ISSUE_KEY | VARCHAR2(50) | Jira 이슈 키 (예: PROJ-123) |
| COMMENT_ID | VARCHAR2(50) | Jira 커멘트 고유 ID |
| COMMENT_BODY | CLOB | 커멘트 전문 |
| COMMENT_CREATED_AT | TIMESTAMP | Jira 커멘트 작성 시각 |
| CREATED_AT | TIMESTAMP | DB 적재 시각 (DEFAULT SYSDATE) |

### 4.2 중복 체크 기준

`TASK_ID + COMMENT_ID` 조합으로 중복 여부를 판단합니다. Jira 커멘트 ID는 전역 고유값이므로 이 조합으로 동일 지연 사유의 재적재를 방지합니다.

UPDATE 없이 INSERT만 수행하여 지연 사유 변경 이력을 모두 보존합니다.

---

## 5. 핵심 설정 (config.py)

### 5.1 JQL 조건

지연 이슈 탐지 조건은 config에서 문자열로 관리하여 코드 수정 없이 조건 변경이 가능합니다.

```python
JQL = "project = PROJ AND duedate < now() AND status != Done"
```

### 5.2 지연 사유 키워드

커멘트 필터링에 사용할 키워드 목록도 config에서 리스트로 관리합니다.

```python
DELAY_KEYWORDS = ["지연 사유", "딜레이 원인", "delay reason"]
```

---

## 6. 실행 환경

### 6.1 환경 구성 (uv)

| 환경 | 명령어 | 비고 |
|------|--------|------|
| 개발서버 | `uv sync` | dev 의존성 포함 |
| 배포서버 | `uv sync --no-dev` | 프로덕션 의존성만 |
| DAG 실행 | `uv run python -m jira_delay_sync` | .venv 재사용 |

배포 시 `uv sync` 1회 실행 후, DAG은 매 실행마다 `uv run`으로 기존 `.venv`를 재사용합니다.

### 6.2 Airflow DAG

BashOperator로 uv run 실행. Airflow 환경과 스크립트 환경을 분리하여 의존성 충돌을 방지합니다.

```python
BashOperator(
    task_id="delay_sync",
    bash_command="cd /path/to/jira-delay-sync && uv run python -m jira_delay_sync"
)
```

### 6.3 환경 변수 (.env)

| 변수명 | 설명 |
|--------|------|
| JIRA_URL | Jira 서버 주소 |
| JIRA_USER | Jira 계정 이메일 |
| JIRA_API_TOKEN | Jira API Token |
| ORACLE_DSN | Oracle DB 접속 DSN |
| ORACLE_USER | Oracle 계정 |
| ORACLE_PASSWORD | Oracle 비밀번호 |

---

## 7. 확인 필요 사항

- [ ] 커멘트 조회 범위: 전체 vs 최근 N일 (성능 고려)
- [ ] Jira 인증 방식: API Token vs Basic Auth
- [ ] 기존 이슈 테이블명 및 TASK_ID 매핑 방식
- [ ] Airflow DAG 실행 주기 (cron 설정)
- [ ] Oracle thick mode 여부 (환경에 따라 Oracle Client 필요)
