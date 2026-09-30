# ch_03_02_SQL.ipynb — SQL 체인 & Agent

`create_sql_query_chain`을 활용해 자연어 질문을 SQL 쿼리로 변환·실행·답변까지 이어가는 방법과, SQL Agent와의 동작 차이를 다루는 튜토리얼입니다.

## 흐름

1. `SQLDatabase.from_uri("sqlite:///data/finance.db")`로 SQLite DB 연결 (`accounts`, `customers`, `transactions` 테이블)
2. `create_sql_query_chain(llm, db)`로 질문 → SQL 쿼리 생성 체인 생성 (커스텀 프롬프트로 테이블 컬럼 설명 추가 가능)
3. `QuerySQLDataBaseTool`로 생성된 쿼리를 실제 DB에 실행
4. `write_query | execute_query` 체인으로 "쿼리 생성 → 실행"을 한 번에 연결
5. **답변 증강**: 단답형 결과를 자연스러운 문장으로 바꾸기 위해 `RunnablePassthrough.assign(...)`으로 query/result를 모으고 LLM으로 최종 답변 생성
6. **SQL Agent**: `create_sql_agent(llm, db=db, agent_type="openai-tools")`로 쿼리 생성·실행·답변을 에이전트가 자동으로 처리 (도구 호출 로그를 통해 동작 과정을 확인 가능)

## 주요 사용 API

- `langchain_classic.chains.create_sql_query_chain`
- `langchain_community.utilities.SQLDatabase`
- `langchain_community.tools.sql_database.tool.QuerySQLDataBaseTool`
- `langchain_community.agent_toolkits.create_sql_agent`

## 데이터

- `data/finance.db` — SQLite DB (직접 준비 필요, 저장소에는 포함되어 있지 않음)
