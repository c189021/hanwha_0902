# ex0929 — LangChain 튜토리얼 정리

각 노트북별 상세 설명은 아래 링크된 개별 `.md` 파일을 참고하세요.

## ch_03 — 요약 & SQL

- [ch_03_01_요약.ipynb](ch_03_01_요약.md) — Stuff / Map-Reduce / Map-Refine / Chain of Density / Clustering-Map-Refine 문서 요약 기법
- [ch_03_02_SQL.ipynb](ch_03_02_SQL.md) — `create_sql_query_chain`으로 SQL 생성·실행·답변, SQL Agent 비교

## ch_04 — LCEL Runnable 고급

- [ch_04_01_RunnablePassthrough.ipynb](ch_04_01_RunnablePassthrough.md) — 입력을 그대로 전달하는 RunnablePassthrough
- [ch_04_02_그래프검토.ipynb](ch_04_02_그래프검토.md) — 체인 구조를 그래프로 시각화
- [ch_04_03_RunnableLambda.ipynb](ch_04_03_RunnableLambda.md) — 사용자 정의 함수 실행, RunnableConfig 활용
- [ch_04_04_RunnableBranch.ipynb](ch_04_04_RunnableBranch.md) — 입력에 따른 동적 라우팅
- [ch_04_05_RunnableParallel.ipynb](ch_04_05_RunnableParallel.md) — 여러 Runnable 병렬 실행
- [ch_04_06_런타임체인구성.ipynb](ch_04_06_런타임체인구성.md) — configurable_fields / configurable_alternatives
- [ch_04_07_chain데코레이터.ipynb](ch_04_07_chain데코레이터.md) — `@chain` 데코레이터로 함수를 Runnable로 변환

## 개발 환경

이 프로젝트는 [uv](https://docs.astral.sh/uv/)로 패키지를 관리합니다.

```bash
uv add 패키지명                # 새 패키지 설치
uv remove 패키지명             # 패키지 제거
uv sync                        # uv.lock 기준으로 환경 동기화
uv export --no-hashes --format requirements-txt -o requirements.txt   # requirements.txt 갱신
```
