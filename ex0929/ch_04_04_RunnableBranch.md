# ch_04_04_RunnableBranch.ipynb — RunnableBranch

입력 내용에 따라 동적으로 처리 경로를 분기하는 방법을 다루는 튜토리얼입니다.

## 핵심 개념

- 입력 데이터 특성에 따라 다른 처리 경로를 유연하게 정의 → 복잡한 의사 결정 트리를 간단하게 구현
- 라우팅을 수행하는 두 가지 방법
  1. `RunnableLambda`에서 조건부로 실행 가능한 객체를 반환 (LangChain 권장 방식)
  2. `RunnableBranch` 사용

## 예제

- 질문을 `수학` / `과학` / `기타` 중 하나로 분류하는 분류 체인을 먼저 만든 뒤, 분류 결과에 따라 각기 다른 프롬프트 체인으로 라우팅하는 2단계 시퀀스 구성
- 두 라우팅 방식(RunnableLambda 조건부 반환 vs RunnableBranch)을 같은 예제로 비교

## 주요 사용 API

- `langchain_core.prompts.PromptTemplate`
- `langchain_core.runnables.RunnableBranch`, `RunnableLambda`
- `langchain_core.output_parsers.StrOutputParser`
