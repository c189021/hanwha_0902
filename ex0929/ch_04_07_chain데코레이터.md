# ch_04_07_chain데코레이터.ipynb — @chain 데코레이터

`@chain` 데코레이터를 사용해 임의의 함수를 `Runnable` 객체로 변환하는 방법을 다루는 튜토리얼입니다.

## 핵심 개념

- 일반 함수에 `@chain` 데코레이터를 붙이면 해당 함수가 `Runnable` 객체로 변환됨
- 변환된 함수(`custom_chain`)는 더 이상 일반 함수가 아니라 실행 가능한 객체이므로, 직접 호출하지 않고 `invoke()`로 실행해야 함
- LCEL 파이프라인(`|`)에 그대로 연결하거나 LangSmith 추적도 자동 적용됨

## 주요 사용 API

- `langchain_core.runnables.chain` (`@chain` 데코레이터)
