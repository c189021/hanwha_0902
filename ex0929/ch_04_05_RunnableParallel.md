# ch_04_05_RunnableParallel.ipynb — RunnableParallel

여러 `Runnable`을 동시에(병렬로) 실행해 결과를 하나의 맵으로 합치는 `RunnableParallel`을 다루는 튜토리얼입니다.

## 핵심 개념

- 여러 개의 Runnable을 하나의 `RunnableParallel`로 묶어 병렬 실행
- **입력/출력 조작**: 다른 Runnable과 함께 사용될 때 입력/출력 형태 변환이 자동으로 처리되므로, 파이프라인 중간에서 데이터 형태를 맞추는 데 활용
- **단계별 병렬 처리 이해**: 여러 Runnable이 순차가 아닌 병렬로 실행되며 결과가 어떻게 합쳐지는지 단계별로 확인

## 주요 사용 API

- `langchain_core.runnables.RunnableParallel`
