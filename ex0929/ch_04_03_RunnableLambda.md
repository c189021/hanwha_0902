# ch_04_03_RunnableLambda.ipynb — RunnableLambda

사용자 정의 함수를 체인에서 실행할 수 있게 해주는 `RunnableLambda`를 다루는 튜토리얼입니다.

## 핵심 개념

- 사용자 정의 함수를 `RunnableLambda`로 감싸 체인에 연결 가능
- **주의**: 함수는 인자를 1개만 받을 수 있음 → 여러 인자가 필요하면 단일 딕셔너리를 받아 내부에서 풀어내는 wrapper 함수를 작성
- `RunnableLambda`는 선택적으로 `RunnableConfig`를 인자로 받아, 콜백/태그 등 구성 정보를 하위 실행에 전달 가능

## 예제

- `length_function`, `multiple_length_function` — 텍스트 길이 계산 함수를 체인에 연결해 `{a}+{b}` 형태 프롬프트에 활용
- `parse_or_fix(text, config)` — JSON 파싱 실패 시 LLM으로 텍스트를 수정하는 재시도 로직을 최대 3회 반복, `RunnableConfig`로 태그/콜백 전달
- `get_openai_callback()`으로 실행 중 토큰 사용량/비용 추적

## 주요 사용 API

- `langchain_core.runnables.RunnableLambda`, `RunnableConfig`
- `langchain_community.callbacks.get_openai_callback`
