# ch_04_01_RunnablePassthrough.ipynb — RunnablePassthrough

입력을 그대로 다음 단계로 전달하는 `RunnablePassthrough`를 다루는 튜토리얼입니다.

## 핵심 개념

- `RunnablePassthrough()` 단독 호출 → 입력을 변경 없이 그대로 반환
- `RunnablePassthrough.assign(...)` → 입력에 추가 키를 계산해서 붙여 반환
- 데이터 변환이 필요 없거나, 파이프라인 특정 단계를 건너뛰거나, 디버깅/모니터링 목적일 때 유용

## 예제

- `RunnableParallel`과 함께 써서 `passed`(원본 그대로), `extra`(assign으로 `mult` 키 추가), `modified`(람다로 값 가공) 세 갈래를 동시에 실행
- **검색기(retriever) 예제**: FAISS 벡터 저장소 + `RunnablePassthrough()`로 질문(`question`)은 그대로 통과시키고, `context`는 retriever 결과로 채워 RAG 체인 구성

## 주요 사용 API

- `langchain_core.runnables.RunnableParallel`, `RunnablePassthrough`
- `langchain_community.vectorstores.FAISS` (+ `faiss-cpu` 패키지 필요)
- `OpenAIEmbeddings`, `ChatOpenAI`
