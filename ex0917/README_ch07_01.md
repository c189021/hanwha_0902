# ch07_01_LLM응답캐싱.ipynb — LLM 답변 캐싱하기

## 개요
동일하거나 반복되는 질문에 대해 LLM을 매번 새로 호출하면 **비용**과 **응답 시간**이 계속 발생합니다. LangChain은 LLM의 응답을 캐싱(caching)하는 기능을 제공하여, 이미 한 번 요청했던 질문(프롬프트)에 대한 답변을 저장해두었다가 동일한 요청이 다시 들어오면 캐시된 결과를 즉시 반환합니다.

이 노트북에서는 두 가지 캐싱 방식을 다룹니다.
1. **인메모리 캐시 (InMemoryCache)** — 메모리(RAM)에 저장, 프로세스가 종료되면 사라짐
2. **SQLite 캐시 (SQLiteCache)** — 파일(DB)에 저장, 프로세스를 재시작해도 캐시가 유지됨

## 핵심 개념

### 1. 캐싱이 필요한 이유
- **비용 절감**: 동일 질문에 대해 API를 재호출하지 않아 토큰 비용 절약
- **속도 향상**: 캐시 히트 시 네트워크 호출 없이 즉시 응답 (아래 실습 결과 참고)
- **재현성**: 같은 입력에 대해 항상 같은 출력을 재사용 (테스트/개발 시 유용)

### 2. `set_llm_cache()`
LangChain 전역 설정 함수로, 이후 실행되는 모든 LLM 호출에 지정한 캐시 정책을 적용합니다.
```python
from langchain_core.globals import set_llm_cache
set_llm_cache(InMemoryCache())  # 이 시점 이후의 모든 체인 호출에 캐시 적용
```

### 3. 인메모리 캐시 (`InMemoryCache`)
```python
from langchain_core.caches import InMemoryCache
set_llm_cache(InMemoryCache())
```
- 파이썬 프로세스 내부의 메모리(딕셔너리 형태)에 프롬프트-응답 쌍을 저장
- 노트북/스크립트를 껐다 켜면 캐시가 초기화됨
- 실습 결과: 첫 호출은 `Wall time: 1.79 s`이지만, 동일 질문 재호출 시 `Wall time: 10.3 ms`로 약 **170배** 빨라짐 (캐시 히트)

### 4. SQLite 캐시 (`SQLiteCache`)
```python
from langchain_community.cache import SQLiteCache
set_llm_cache(SQLiteCache(database_path="cache/llm_cache.db"))
```
- 캐시를 로컬 SQLite 파일(`cache/llm_cache.db`)에 영구 저장
- 프로세스를 재시작해도 이전에 캐싱된 응답을 그대로 재사용 가능
- `os.makedirs("cache")`로 캐시 저장 폴더를 미리 생성해야 함
- `langchain_community`는 유지보수가 축소(sunset)되고 있다는 Deprecation 경고가 발생 — 향후에는 별도 통합 패키지로 이전될 예정이라는 안내이므로 참고만 하면 됨

### 5. 캐시 키(Key)의 기준
LangChain 캐시는 기본적으로 **프롬프트 문자열 + 모델 파라미터(모델명, temperature 등)** 조합을 키로 사용합니다. 즉, `chain.invoke({"country": "한국"})`처럼 프롬프트 내용이 완전히 동일해야 캐시가 히트됩니다. `"대한민국"`과 `"한국"`은 다른 입력이므로 별도로 캐싱됩니다.

### 6. 사용된 주요 컴포넌트
| 컴포넌트 | 역할 |
|---|---|
| `ChatOpenAI` | OpenAI Chat 모델(GPT-4o-mini) 래퍼 |
| `PromptTemplate.from_template` | `{country}` 같은 변수를 담은 프롬프트 템플릿 생성 |
| `prompt \| llm` (LCEL) | 프롬프트와 모델을 파이프(`\|`)로 연결한 체인(Runnable) |
| `stream_response` | 스트리밍 응답을 실시간으로 출력해주는 teddynote 헬퍼 함수 |
| `%%time` | 셀 실행 시간을 측정하는 Jupyter 매직 커맨드 |
| `logging.langsmith(...)` | LangSmith 추적(트레이싱) 프로젝트를 설정 |

## 코드 흐름 요약
1. `.env` 로드 후 LangSmith 추적 설정
2. `ChatOpenAI`로 스트리밍 답변 테스트 (`stream_response`)
3. `PromptTemplate + LLM`으로 LCEL 체인 구성
4. 캐시 없이 체인 실행 → 시간 측정
5. `InMemoryCache` 적용 후 첫 실행(캐시 저장) vs 재실행(캐시 히트) 시간 비교
6. `SQLiteCache`로 전환하여 파일 기반 영구 캐시 실습

## 알아두면 좋은 점
- 캐시는 **전역 설정**이므로, 한 번 `set_llm_cache()`를 호출하면 이후의 모든 LLM 호출(다른 체인 포함)에도 적용됩니다.
- 운영 환경에서는 SQLite보다 Redis 등 외부 캐시 스토어를 사용하는 것이 여러 프로세스/서버 간 캐시 공유에 유리합니다.
- 캐싱은 프롬프트가 완전히 동일할 때만 동작하므로, 사용자 입력이 조금이라도 다르면(오타, 띄어쓰기 등) 캐시가 적중하지 않는다는 한계가 있습니다.
