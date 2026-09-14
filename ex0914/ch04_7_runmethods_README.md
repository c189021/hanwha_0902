# 체인 실행 방법 4가지 — `invoke` / `stream` / `batch` / `async`

09/14 실습. [`ch04_7_runmethods.ipynb`](ch04_7_runmethods.ipynb) — [`ch04_5_lcel_README.md`](ch04_5_lcel_README.md),
[`ch04_6_outputparser_README.md`](ch04_6_outputparser_README.md)에서 만든 `prompt | model | output_parser` 체인을
**어떤 방식으로 호출할 수 있는지** 정리합니다. LangChain의 모든 체인(Runnable)은 아래 4가지 실행 메서드를 공통으로 지원합니다.

---

## 1. 실행 메서드 한눈에 보기

| 메서드 | 동기/비동기 | 입력 → 출력 | 설명 |
|---|---|---|---|
| `invoke()` | 동기 | 단일 입력 → 단일 출력 | 체인을 한 번 호출해 완성된 결과를 받음 |
| `stream()` | 동기 | 단일 입력 → 데이터 스트림 | 응답을 토큰(청크) 단위로 순차 수신 |
| `batch()` | 동기 | 입력 목록 → 출력 목록 | 여러 입력을 한 번에 처리해 리스트로 받음 |
| `ainvoke()` / `astream()` | 비동기 | `invoke`/`stream`과 동일 | `async/await`로 논블로킹 호출 |

`invoke`, `stream`은 이미 [`ch04_README.md`](ch04_README.md), [`ch04_5_lcel_README.md`](ch04_5_lcel_README.md)에서
다뤘으므로, 이 문서는 **`batch`와 비동기(`async`) 호출**을 중심으로 설명합니다.

```python
model = ChatOpenAI()
prompt = PromptTemplate.from_template("{topic} 에 대하여 3문장으로 설명해줘.")
chain = prompt | model | StrOutputParser()
```

## 2. `batch()` — 여러 입력을 한 번에 처리하기

```python
chain.batch([{"topic": "ChatGPT"}, {"topic": "Instagram"}])
# -> ['ChatGPT는 인공지능 챗봇으로 ...', '인스타그램은 소셜 미디어 플랫폼으로 ...']
```

- 입력을 **딕셔너리의 리스트**로 넘기면, 각 딕셔너리마다 `invoke()`를 한 번씩 호출한 것과 같은 결과를
  **리스트**로 한 번에 돌려받습니다. "ChatGPT는 어떤 서비스인지", "Instagram은 어떤 서비스인지"를
  각각 따로 반복문으로 호출하지 않아도 됩니다.
- 결과 리스트의 순서는 입력 리스트의 순서와 동일하게 대응됩니다 (`answer[0]` → 첫 번째 입력의 답변).

### `max_concurrency` — 동시 처리 개수 제한

```python
chain.batch(
    [
        {"topic": "ChatGPT"},
        {"topic": "Instagram"},
        {"topic": "멀티모달"},
        {"topic": "프로그래밍"},
        {"topic": "머신러닝"},
    ],
    config={"max_concurrency": 3},
)
```

- 입력이 5개라고 해서 5개 요청을 전부 동시에 보내는 게 아니라, `max_concurrency=3`을 주면
  **최대 3개씩만 동시에** OpenAI API를 호출하고 나머지는 순서를 기다립니다.
- API 요청 속도 제한(rate limit)에 걸리지 않도록 동시 호출 개수를 조절할 때 사용합니다.

## 3. 비동기(`async`) 호출 — `astream()` / `ainvoke()`

지금까지 쓴 `invoke`/`stream`/`batch`는 모두 **동기(synchronous)** 방식이라, 호출이 끝날 때까지
다음 코드가 실행되지 않고 기다립니다. 비동기 버전은 이름 앞에 `a`가 붙으며, `await`와 함께 사용해
"기다리는 동안 다른 작업도 할 수 있게" 만들 수 있습니다. (주피터 노트북 셀은 기본적으로 `async` 코드를
바로 실행할 수 있는 환경을 제공합니다.)

```python
# astream() : 비동기 스트리밍
async for token in chain.astream({"topic": "YouTube"}):
    print(token, end="", flush=True)
```

```python
# ainvoke() : 비동기 단일 호출
my_process = chain.ainvoke({"topic": "NVDA"})   # 호출 즉시 코루틴(작업)만 생성, 아직 실행 완료 안 됨
result = await my_process                        # 실제로 완료될 때까지 기다렸다가 결과를 받음
```

- `chain.ainvoke(...)`을 호출하는 순간 결과가 바로 나오는 게 아니라, **아직 끝나지 않은 비동기 작업
  객체(코루틴)**가 반환됩니다. 실제 값을 얻으려면 `await`로 완료될 때까지 기다려야 합니다.
- `async for`는 `astream()`이 돌려주는 비동기 스트림에서 토큰을 하나씩 받아오는 문법입니다.
  동기 버전의 `for token in chain.stream(...)`과 동일한 역할을 비동기 방식으로 수행합니다.
- 여러 개의 비동기 호출을 동시에 실행하고 싶다면(예: 5개 질문을 동시에 요청), `asyncio.gather()` 같은
  도구와 함께 쓰지만 이 노트북에서는 단일 호출 예제만 다룹니다.

## 참고 — 실행 로그에 보이는 LangSmith 연결 오류

`Failed to get info from https://eu.api.langchain.com ...` / `Failed to multipart ingest runs ...` 류의
경고는 LangSmith 트레이싱 전송 실패일 뿐, 체인 실행 결과 자체와는 무관합니다. 자세한 내용은
[`ch04_2_langsmith_README.md`](ch04_2_langsmith_README.md)를 참고하세요.
