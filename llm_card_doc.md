좋아. 그러면 최종 목표는 이거야.

> **각 repo 안에 “LLM 작업 운영 지침서”를 넣어두고, Claude Code / Codex / opencode 같은 도구가 그 지침을 읽고 자동으로 이슈 카드·지식 카드·결정 카드를 관리하게 만드는 구조**

이건 꽤 현실적이고 좋다. 특히 너처럼 여러 프로젝트를 왔다 갔다 하고, 개발 환경·설계 판단·이슈 해결 과정이 반복되는 사람에게 잘 맞아.

---

## 추천 구조

repo마다 이렇게 두면 돼.

```text
my-project/
  README.md
  CLAUDE.md
  AGENTS.md
  .agent/
    project.md
    workflow.md
    card-rules.md
    coding-rules.md
    report-format.md
    templates/
      issue.md
      knowledge.md
      decision.md
      experiment.md

  dev-notes/
    issues/
    knowledge/
    decisions/
    experiments/
    archive/

  src/
  tests/
```

핵심 파일은 3개야.

```text
CLAUDE.md      Claude Code가 우선 읽을 프로젝트 지침
AGENTS.md     여러 LLM/Agent 공통 지침
.agent/       세부 운영 규칙
```

실제로는 **CLAUDE.md와 AGENTS.md 둘 다 넣는 것**을 추천해.
도구마다 읽는 파일명이 다를 수 있으니까, 공통 지침은 `AGENTS.md`에 두고 `CLAUDE.md`는 그걸 참조하게 만들면 좋아.

---

## 가장 중요한 운영 방식

repo 안에서 LLM은 이렇게 움직이게 해야 해.

```text
1. 작업 시작 전 AGENTS.md / CLAUDE.md를 읽는다.
2. 사용자 요청을 Issue Card로 만든다.
3. 코드와 문서를 조사한다.
4. 수정한다.
5. 재사용 가능한 지식은 Knowledge Card로 남긴다.
6. 중요한 판단은 Decision Card로 남긴다.
7. 실패한 시도는 Experiment Card로 남긴다.
8. 작업 완료 후 Issue Card를 업데이트한다.
9. 최종 보고에 변경 파일과 생성된 카드를 포함한다.
```

중요한 건 **LLM이 매번 처음부터 기억하는 게 아니라, repo 안의 문서를 통해 프로젝트 기억을 복구하게 만드는 것**이야.

---

# 1. `AGENTS.md` 예시

이 파일은 repo 루트에 둬.
Claude Code, Codex, opencode가 공통으로 참고할 수 있는 최상위 지침이라고 보면 돼.

# Agent Instructions

이 저장소는 LLM 기반 개발 에이전트와 함께 작업하기 위해 설계되어 있다.
에이전트는 단순히 코드를 수정하는 것에서 끝나지 않고, 작업 과정에서 발생한 이슈, 지식, 결정 사항을 저장소 안에 카드 형태로 남겨야 한다.

## 1. 작업 시작 규칙

작업을 시작하기 전에 다음 파일을 순서대로 확인한다.

1. `AGENTS.md`
2. `CLAUDE.md` 또는 사용 중인 에이전트별 지침 파일
3. `.agent/project.md`
4. `.agent/workflow.md`
5. `.agent/card-rules.md`
6. `.agent/coding-rules.md`

파일이 없으면 추측해서 만들지 말고, 현재 존재하는 지침만 따른다.

## 2. 기본 원칙

사용자의 요청은 가능한 한 하나의 Issue Card로 관리한다.

작업 중 발견한 재사용 가능한 기술 지식은 Knowledge Card로 남긴다.
중요한 구현 판단이나 설계 판단은 Decision Card로 남긴다.
실패했지만 의미 있는 실험은 Experiment Card로 남긴다.

카드는 작업 로그가 아니다.
나중에 다시 검색하고 재사용할 수 있는 지식 단위여야 한다.

## 3. 작업 흐름

새로운 요청을 받으면 다음 순서로 작업한다.

1. 요청을 이해한다.
2. 관련 파일과 기존 카드를 검색한다.
3. 필요한 경우 Issue Card를 생성한다.
4. 코드를 조사한다.
5. 수정 계획을 세운다.
6. 변경을 수행한다.
7. 가능한 경우 테스트 또는 검증을 수행한다.
8. Issue Card를 업데이트한다.
9. 필요한 Knowledge Card, Decision Card, Experiment Card를 생성하거나 업데이트한다.
10. 사용자에게 완료 요약을 보고한다.

## 4. 카드 저장 위치

카드는 다음 위치에 저장한다.

```text
dev-notes/
  issues/
  knowledge/
  decisions/
  experiments/
  archive/
```

## 5. 카드 생성 기준

무조건 카드를 많이 만들지 않는다.

다음 경우에는 카드를 만든다.

* 사용자의 요청이 하나의 작업 단위로 관리되어야 할 때
* 원인 분석이 필요한 버그가 있을 때
* 나중에 재사용 가능한 해결 패턴을 발견했을 때
* 구현 방향에 대한 명확한 판단을 했을 때
* 실패한 접근이 반복 방지 가치가 있을 때

다음 경우에는 별도 카드를 만들지 않는다.

* 단순 오타 수정
* 아주 작은 문구 변경
* 임시 확인만 한 경우
* 재사용 가치가 없는 작업 로그

## 6. 코드 변경 원칙

기존 구조와 스타일을 우선 존중한다.

불필요한 대규모 리팩토링을 하지 않는다.
요청받지 않은 기능을 임의로 추가하지 않는다.
테스트나 검증이 가능하면 수행한다.
검증하지 못한 경우에는 최종 보고에 명확히 적는다.

## 7. 불확실성 처리

확실하지 않은 내용은 확정된 사실처럼 쓰지 않는다.

다음 표현을 사용한다.

* 가설
* 확인 필요
* 재검토 필요
* 현재 코드 기준
* 현재 문서 기준

## 8. 최종 보고 형식

작업 완료 후 다음 형식으로 보고한다.

```text
완료 요약:
- 해결한 문제:
- 변경한 파일:
- 확인한 내용:
- 생성/수정한 카드:
- 남은 이슈:
```

검증을 하지 못한 경우에는 이유를 적는다.

---

# 2. `CLAUDE.md` 예시

이 파일은 Claude Code가 보기 쉽게 루트에 두면 돼.
내용은 길게 쓰지 말고, 공통 지침으로 연결하는 게 좋아.

# Claude Code Instructions

이 저장소에서는 repo-local card system을 사용한다.

작업을 시작하기 전에 반드시 `AGENTS.md`를 먼저 읽고, 그 다음 `.agent/` 아래의 지침 파일을 확인한다.

## 반드시 지킬 것

* 사용자의 요청을 가능한 경우 Issue Card로 관리한다.
* 작업 중 발견한 재사용 가능한 지식은 Knowledge Card로 남긴다.
* 중요한 구현 판단은 Decision Card로 남긴다.
* 실패했지만 의미 있는 시도는 Experiment Card로 남긴다.
* 작업 완료 후 Issue Card를 업데이트한다.
* 최종 응답에는 변경 파일과 생성/수정한 카드를 포함한다.

## 카드 위치

```text
dev-notes/issues/
dev-notes/knowledge/
dev-notes/decisions/
dev-notes/experiments/
```

## 세부 규칙

세부 규칙은 다음 파일을 따른다.

```text
.agent/project.md
.agent/workflow.md
.agent/card-rules.md
.agent/coding-rules.md
.agent/report-format.md
```

## 주의

카드는 많을수록 좋은 것이 아니다.
나중에 다시 검색하고 재사용할 수 있는 내용만 카드로 남긴다.

---

# 3. `.agent/project.md`

이 파일에는 이 repo가 무슨 프로젝트인지 적어.
LLM이 매번 프로젝트 맥락을 빠르게 이해하게 해주는 파일이야.

# Project Context

## 프로젝트 이름

{{project_name}}

## 프로젝트 목적

{{이 프로젝트가 해결하려는 문제를 적는다.}}

## 주요 사용자

{{이 프로젝트를 사용하는 사람 또는 시스템을 적는다.}}

## 핵심 기능

* {{feature_1}}
* {{feature_2}}
* {{feature_3}}

## 기술 스택

* Language: {{Python / Java / JavaScript / TypeScript 등}}
* Backend: {{FastAPI / Spring / Express 등}}
* Frontend: {{React / Next.js 등}}
* Database: {{Oracle / PostgreSQL / MongoDB 등}}
* Infra: {{Docker / Kubernetes / Prefect / Airflow 등}}

## 실행 방법

```bash
{{run_command}}
```

## 테스트 방법

```bash
{{test_command}}
```

## 중요한 제약

* {{사내망 / 프록시 / 인증서 / 특정 DB / 특정 런타임 등}}
* {{운영 환경 제약}}
* {{권한 제약}}
* {{성능 제약}}

## 개발 시 주의할 점

* 기존 구조를 우선 존중한다.
* 운영 환경에서 깨질 수 있는 경로, 인증서, 환경변수 처리를 주의한다.
* 사용자가 요청하지 않은 대규모 리팩토링은 하지 않는다.

---

# 4. `.agent/workflow.md`

이 파일은 LLM이 작업할 때의 절차야.

# Agent Workflow

## 1. 요청 접수

사용자의 요청을 받으면 먼저 다음을 판단한다.

* 버그 수정인가?
* 기능 추가인가?
* 리팩토링인가?
* 조사 작업인가?
* 문서 작업인가?

작업 단위가 명확하면 Issue Card를 생성한다.
이미 관련 Issue Card가 있으면 새로 만들지 않고 기존 카드를 업데이트한다.

## 2. 기존 정보 확인

작업 전에 다음을 검색한다.

* 관련 소스 파일
* 관련 테스트
* 관련 설정 파일
* `dev-notes/issues/`
* `dev-notes/knowledge/`
* `dev-notes/decisions/`

기존 카드에 관련 내용이 있으면 새 카드에서 링크한다.

## 3. 작업 계획

코드를 수정하기 전에 간단한 계획을 세운다.

계획에는 다음을 포함한다.

* 수정 대상 파일
* 예상 원인 또는 구현 방향
* 검증 방법
* 리스크

단순 작업이면 계획을 길게 작성하지 않는다.

## 4. 구현

요청 범위 안에서만 수정한다.

기존 코드 스타일을 따른다.
불필요한 리팩토링을 하지 않는다.
환경변수, 파일 경로, 외부 시스템 연동은 특히 주의한다.

## 5. 검증

가능한 경우 테스트를 실행한다.

테스트가 없으면 다음 중 가능한 방법으로 확인한다.

* 타입 체크
* 린트
* 단위 실행
* 주요 함수 수동 확인
* 설정 파일 검토

검증하지 못한 경우에는 최종 보고에 이유를 적는다.

## 6. 카드 업데이트

작업 중 다음을 수행한다.

* Issue Card에 조사 내용과 수행 작업을 업데이트한다.
* 재사용 가능한 지식이 있으면 Knowledge Card를 만든다.
* 구현 판단이 있으면 Decision Card를 만든다.
* 실패한 실험이 의미 있으면 Experiment Card를 만든다.

## 7. 완료 보고

작업 완료 후 사용자에게 다음을 보고한다.

* 해결한 문제
* 변경한 파일
* 확인한 내용
* 생성 또는 수정한 카드
* 남은 이슈

---

# 5. `.agent/card-rules.md`

이게 네가 말한 **제텔카스텔 방식의 핵심**이야.

# Card Rules

이 프로젝트는 개발 이슈와 지식을 카드 단위로 관리한다.

## 1. 카드 종류

### Issue Card

현재 해결해야 하는 작업 단위다.

대상:

* 버그
* 기능 추가
* 리팩토링
* 조사
* 문서 작업
* 운영 이슈

저장 위치:

```text
dev-notes/issues/
```

### Knowledge Card

작업 중 발견한 재사용 가능한 지식이다.

대상:

* 에러 원인과 해결 패턴
* 라이브러리 동작 방식
* 프레임워크 주의점
* 프로젝트 내부 구조
* 환경 설정 지식
* 비슷한 문제에 재사용 가능한 설명

저장 위치:

```text
dev-notes/knowledge/
```

### Decision Card

구현 또는 설계 과정에서 내린 중요한 결정이다.

대상:

* 여러 대안 중 하나를 선택한 경우
* 임시 해결책을 선택한 경우
* 성능과 유지보수성 사이에서 타협한 경우
* 운영 환경 제약 때문에 특정 방식을 선택한 경우

저장 위치:

```text
dev-notes/decisions/
```

### Experiment Card

시도했지만 실패했거나 보류한 실험이다.

대상:

* 실패한 접근
* 성능 실험
* 임시 테스트
* 확인했지만 채택하지 않은 방법

저장 위치:

```text
dev-notes/experiments/
```

## 2. 파일명 규칙

```text
ISSUE-YYYYMMDD-001-short-title.md
K-YYYYMMDD-001-short-title.md
D-YYYYMMDD-001-short-title.md
EXP-YYYYMMDD-001-short-title.md
```

예시:

```text
ISSUE-20260707-001-session-reset-after-refresh.md
K-20260707-001-cookie-samesite-affects-session.md
D-20260707-001-store-session-in-http-only-cookie.md
EXP-20260707-001-local-storage-session-token.md
```

파일명은 영어 소문자와 하이픈을 사용한다.
본문은 한국어로 작성한다.

## 3. 카드 작성 원칙

하나의 카드는 하나의 목적만 가진다.

Knowledge Card는 하나의 핵심 지식만 담는다.
Decision Card는 하나의 결정만 담는다.
Issue Card는 하나의 작업 단위만 담는다.

## 4. 링크 규칙

카드끼리는 Markdown 링크로 연결한다.

예시:

```text
관련 이슈:
- [[ISSUE-20260707-001-session-reset-after-refresh]]

관련 지식:
- [[K-20260707-001-cookie-samesite-affects-session]]

관련 결정:
- [[D-20260707-001-store-session-in-http-only-cookie]]
```

Issue Card에는 관련 Knowledge Card와 Decision Card를 연결한다.
Knowledge Card와 Decision Card에는 원인이 된 Issue Card를 연결한다.

## 5. 카드 생성 기준

카드는 많을수록 좋은 것이 아니다.

다음 조건 중 하나 이상을 만족할 때만 카드를 만든다.

* 나중에 비슷한 문제를 해결할 때 다시 쓸 수 있다.
* 프로젝트 구조 이해에 도움이 된다.
* 중요한 구현 판단이 담겨 있다.
* 실패한 접근을 반복하지 않게 해준다.
* 사용자나 미래의 에이전트가 검색할 가능성이 높다.

## 6. 카드 생성 금지 기준

다음 경우에는 별도 카드를 만들지 않는다.

* 단순 오타 수정
* 포맷팅 변경
* 작은 변수명 변경
* 일회성 작업 로그
* 재사용 가치가 없는 명령 실행 기록

## 7. 불확실성 표시

확실하지 않은 내용은 다음 표현으로 표시한다.

* 가설
* 확인 필요
* 재검토 필요
* 현재 코드 기준
* 현재 실행 결과 기준

---

## 6. 템플릿 파일들

repo에 `.agent/templates/` 아래로 넣으면 돼.

### `.agent/templates/issue.md`

```markdown
# {{title}}

ID: {{issue_id}}  
상태: Inbox  
유형: {{bug | feature | refactor | research | chore}}  
생성일: {{date}}  
관련 프로젝트: {{project_name}}

## 문제 / 요청

{{user_request}}

## 배경

{{context}}

## 현재 상태

{{current_state}}

## 관련 파일

- {{file_path}}

## 조사 내용

- {{finding_1}}
- {{finding_2}}

## 수행한 작업

- {{action_1}}
- {{action_2}}

## 결과

{{result}}

## 확인 방법

- {{test_or_check}}

## 연결된 Knowledge Cards

- [[{{knowledge_card_id}}]]

## 연결된 Decision Cards

- [[{{decision_card_id}}]]

## 남은 작업

- {{todo}}

## 메모

{{notes}}
```

### `.agent/templates/knowledge.md`

````markdown
# {{title}}

ID: {{knowledge_id}}  
유형: Knowledge  
생성일: {{date}}  
관련 프로젝트: {{project_name}}

## 핵심

{{one_sentence_summary}}

## 설명

{{explanation}}

## 언제 다시 쓰는가

- {{case_1}}
- {{case_2}}

## 예시

```text
{{example}}
````

## 주의점

{{caution}}

## 연결된 Issue Cards

* [[{{issue_card_id}}]]

## 연결된 Decision Cards

* [[{{decision_card_id}}]]

## 관련 키워드

#{{tag_1}} #{{tag_2}}

````

### `.agent/templates/decision.md`

```markdown
# {{title}}

ID: {{decision_id}}  
유형: Decision  
생성일: {{date}}  
관련 프로젝트: {{project_name}}

## 결정

{{decision}}

## 이유

{{reason}}

## 고려한 대안

1. {{alternative_1}}
2. {{alternative_2}}
3. {{alternative_3}}

## 장점

- {{pros_1}}
- {{pros_2}}

## 단점 / 리스크

- {{risk_1}}
- {{risk_2}}

## 재검토 조건

- {{condition_1}}
- {{condition_2}}

## 연결된 Issue Cards

- [[{{issue_card_id}}]]

## 연결된 Knowledge Cards

- [[{{knowledge_card_id}}]]

## 관련 키워드

#{{tag_1}} #{{tag_2}}
````

### `.agent/templates/experiment.md`

```markdown
# {{title}}

ID: {{experiment_id}}  
유형: Experiment  
생성일: {{date}}  
관련 프로젝트: {{project_name}}

## 실험 목적

{{purpose}}

## 가설

{{hypothesis}}

## 시도한 방법

{{method}}

## 결과

{{result}}

## 실패 또는 보류 이유

{{reason}}

## 배운 점

{{lesson}}

## 다음에 시도할 방법

{{next_try}}

## 연결된 Issue Cards

- [[{{issue_card_id}}]]

## 관련 키워드

#{{tag_1}} #{{tag_2}}
```

---

## 너한테 맞는 실제 운영 방식

너는 repo마다 이렇게 넣으면 돼.

```text
project-a/
  AGENTS.md
  CLAUDE.md
  .agent/
  dev-notes/

project-b/
  AGENTS.md
  CLAUDE.md
  .agent/
  dev-notes/

project-c/
  AGENTS.md
  CLAUDE.md
  .agent/
  dev-notes/
```

그리고 Claude Code에 이렇게 말하면 된다.

```text
이 repo의 AGENTS.md와 CLAUDE.md를 읽고 작업해줘.
내가 말하는 문제를 Issue Card로 만들고,
해결 과정에서 재사용 가능한 지식은 Knowledge Card,
중요한 구현 판단은 Decision Card로 남겨줘.
```

예를 들면:

```text
환경변수 입력 UI에서 벌크 입력 후 중복 값 처리가 이상해.
AGENTS.md 규칙에 따라 이슈 카드 만들고 조사해서 수정해줘.
```

그러면 이상적인 결과는 이거야.

```text
dev-notes/issues/
  ISSUE-20260707-001-bulk-env-duplicate-handling.md

dev-notes/knowledge/
  K-20260707-001-env-key-normalization-before-duplicate-check.md

dev-notes/decisions/
  D-20260707-001-keep-first-env-value-on-duplicate.md
```

---

## 처음부터 너무 거창하게 하지 않는 버전

처음에는 이 정도만 있어도 충분해.

```text
my-project/
  AGENTS.md
  CLAUDE.md
  dev-notes/
    issues/
    knowledge/
    decisions/
```

그리고 `AGENTS.md`에 최소 규칙만 넣어.

```text
1. 모든 작업은 Issue Card로 시작한다.
2. 재사용 가능한 지식은 Knowledge Card로 남긴다.
3. 중요한 판단은 Decision Card로 남긴다.
4. 작업 완료 후 Issue Card를 업데이트한다.
5. 카드는 dev-notes/ 아래에 저장한다.
```

처음부터 `.agent/`를 너무 세분화하면 LLM도 읽을 게 많아지고, 너도 관리가 귀찮아질 수 있어.
그래서 나는 **처음에는 3파일 구조**를 추천해.

```text
AGENTS.md
CLAUDE.md
dev-notes/
```

익숙해지면 그때 `.agent/templates/`, `.agent/card-rules.md`를 분리하면 돼.

---

## 더 좋은 구조: 공통 지침 repo 하나 만들기

너는 여러 프로젝트를 관리할 가능성이 높으니까, 공통 템플릿 repo를 하나 만드는 것도 좋아.

```text
agent-repo-template/
  AGENTS.md
  CLAUDE.md
  .agent/
    project.md
    workflow.md
    card-rules.md
    coding-rules.md
    report-format.md
    templates/
```

새 프로젝트 만들 때마다 복사해서 쓰는 거야.

```bash
cp -r agent-repo-template/.agent ./my-project/
cp agent-repo-template/AGENTS.md ./my-project/
cp agent-repo-template/CLAUDE.md ./my-project/
mkdir -p ./my-project/dev-notes/{issues,knowledge,decisions,experiments,archive}
```

나중에는 이걸 스크립트로 만들어도 돼.

```bash
init-agent-notes my-project
```

---

## 이 방식의 핵심 가치

네가 원하는 건 단순히 “노트를 잘 쓰자”가 아니야.

정확히는 이거야.

> **Repo 자체가 LLM에게 프로젝트 기억을 제공하는 구조**

LLM은 매번 새로 들어와도 repo 안의 문서를 읽고 이렇게 이해할 수 있어.

```text
이 프로젝트는 무엇인가?
어떤 규칙으로 개발해야 하는가?
과거에 어떤 문제가 있었는가?
어떤 결정을 왜 했는가?
비슷한 버그는 어떻게 해결했는가?
```

그러면 프로젝트가 오래될수록 LLM이 더 똑똑하게 작동해.

---

## 내가 추천하는 최종 MVP

처음 버전은 딱 이렇게 가자.

```text
repo/
  AGENTS.md
  CLAUDE.md
  dev-notes/
    issues/
    knowledge/
    decisions/
```

그리고 규칙은 단순하게.

```text
Issue Card = 지금 해결할 작업
Knowledge Card = 다음에도 쓸 수 있는 지식
Decision Card = 왜 이렇게 구현했는지
```

나중에 필요해지면 추가.

```text
.agent/templates/
dev-notes/experiments/
dev-notes/archive/
```

이게 가장 현실적이야.
처음부터 완벽한 제텔카스텔을 만들기보다, **LLM이 부담 없이 계속 쌓을 수 있는 repo-local 기억 시스템**으로 시작하는 게 좋아.
