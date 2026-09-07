intent.md와 spec.md를 읽고 Anthropic AI-Native SDLC 방식으로 plan.md를 작성해줘.

현재 단계는 Implementation Planning 단계다.

먼저 다음 순서로 진행해.

intent.md를 읽고 이 작업의 원래 목적과 범위를 이해해.
spec.md를 읽고 합의된 요구사항과 설계를 이해해.
현재 코드베이스를 충분히 탐색해.
관련 코드, 기존 패턴, 의존성, 테스트 구조를 확인해.
그 내용을 기반으로 실제 구현 가능한 plan.md를 작성해.

plan.md는 다른 개발자나 AI Agent가 이 문서만 보고도 구현을 진행할 수 있을 정도로 구체적이어야 한다.

다음 내용을 포함해줘.

Overview

이번 구현에서 무엇을 변경하는지 간단히 설명.

Current State

현재 코드베이스에서 관련 기능이 어떻게 구성되어 있는지 설명.

Implementation Approach

spec.md의 설계를 실제 코드에 어떻게 반영할지 설명.

Files to Change

각 파일별로 다음을 작성해.

파일 경로
새로 생성 / 수정 / 삭제 여부
현재 역할
이번 작업에서 변경할 내용
다른 파일과의 관계

예:

src/service/cleaner.py
- Modify
- 오래된 로그 파일을 탐색하는 기존 서비스
- retention policy 적용 로직 추가
- repository.py의 delete_log()를 호출
Implementation Tasks

구현 작업을 실행 가능한 단위로 나눠서 순서대로 작성해.

각 Task에는 다음 내용을 포함해.

Task N: <작업 이름>

Goal
이 작업에서 달성해야 하는 것.

Files
수정하거나 생성할 파일의 정확한 경로.

Changes
구체적으로 어떤 코드 또는 동작을 변경해야 하는지.

가능하면 함수, 클래스, API, 데이터 구조 수준까지 명확하게 작성해.

Dependencies
이 Task가 이전 Task 또는 기존 코드의 무엇에 의존하는지.

Verification
이 작업이 제대로 완료되었음을 어떻게 확인할지.

Testing Plan

다음을 구분해서 작성해.

Unit tests
Integration tests
Regression tests
필요한 경우 manual verification

각 테스트에서 무엇을 검증해야 하는지 구체적으로 작성해.

가능하면 관련 테스트 파일 경로도 명시해.

Edge Cases

구현 시 반드시 처리해야 하는 예외 상황이나 경계 조건.

Risks

구현 과정에서 기존 기능에 영향을 줄 가능성이 있는 부분.

각 위험에 대해 어떻게 검증하거나 완화할지도 작성해.

Implementation Order

Task 간 의존성을 고려해서 실제 구현 순서를 정리해.

가능하면 각 단계가 독립적으로 검증 가능한 상태가 되도록 나눠.

Definition of Done

이 작업이 완료되었다고 판단하기 위한 조건을 체크리스트로 작성해.

중요한 원칙:

intent.md의 목적과 범위를 변경하지 마.
spec.md에서 합의되지 않은 기능을 임의로 추가하지 마.
spec.md와 구현 계획이 충돌하면 임의로 결정하지 말고 알려줘.
현재 코드베이스의 기존 구조와 패턴을 우선적으로 따라.
불필요한 리팩터링을 계획에 넣지 마.
필요한 경우에만 새로운 abstraction이나 dependency를 제안해.
파일 이름이나 함수가 실제로 존재하는지 코드베이스를 확인한 뒤 작성해.
존재하지 않는 파일이나 API를 추측해서 작성하지 마.
구현 작업은 가능한 작고 검증 가능한 단위로 나눠.
각 Task가 끝날 때 어떻게 테스트할지 명확하게 작성해.
구현과 테스트를 분리하지 말고 가능한 한 각 Task에 필요한 테스트를 함께 포함해.
아직 실제 코드는 수정하지 마.
plan.md 작성까지만 수행해.

계획을 작성하기 전에 intent.md, spec.md, 현재 코드베이스 사이에 모순이나 구현을 막는 중요한 불확실성이 있다면 먼저 알려줘.

그렇지 않다면 바로 plan.md를 작성해줘.
