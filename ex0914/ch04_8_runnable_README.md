# LangChain Runnable 3종 — `RunnableParallel` / `RunnablePassthrough` / `RunnableLambda`

09/14 실습. [`ch04_8_runnable.ipynb`](ch04_8_runnable.ipynb) — 여러 체인을 **병렬로 실행**하거나,
체인 중간에 **원본 입력을 그대로 흘려보내거나**, **일반 파이썬 함수를 체인 안에 끼워 넣는** 방법을 다룹니다.
`prompt | model | output_parser` 처럼 일직선으로 이어붙이는 것만으로는 부족한, 더 복잡한 데이터 흐름을
구성할 때 쓰는 LCEL의 핵심 도구 3가지입니다.

---

## 1. `RunnableParallel` — 여러 체인을 동시에 실행해서 딕셔너리로 합치기

```python
from langchain_core.runnables import RunnableParallel

# {country} 의 수도를 물어보는 체인
chain1 = PromptTemplate.from_template("{country} 의 수도는 어디야?") | model | StrOutputParser()

# {country} 의 면적을 물어보는 체인
chain2 = PromptTemplate.from_template("{country} 의 면적은 얼마야?") | model | StrOutputParser()

combined = RunnableParallel(capital=chain1, area=chain2)

combined.invoke({"country": "대한민국"})
# -> {'capital': '대한민국의 수도는 서울이야.', 'area': '대한민국의 총 면적은 약 100,363.49 km² 입니다.'}
```

- `RunnableParallel(키1=체인1, 키2=체인2, ...)` : 같은 입력을 여러 체인에 **동시에** 전달해서 호출하고,
  각 체인의 결과를 지정한 키로 묶은 **딕셔너리**로 돌려줍니다.
- 순서대로 `chain1.invoke(...)`, `chain2.invoke(...)`를 따로 호출하는 것과 최종 결과는 같지만,
  `RunnableParallel`은 내부적으로 두 체인을 **병렬로** 실행하기 때문에 더 빠릅니다.
- `combined.batch([...])`처럼 [`ch04_7_runmethods_README.md`](ch04_7_runmethods_README.md)에서 다룬
  `invoke`/`batch` 등 모든 실행 메서드를 `RunnableParallel` 결과에도 동일하게 쓸 수 있습니다.

## 2. `RunnablePassthrough` — 입력을 그대로(또는 살짝 더해서) 다음 단계로 넘기기

```python
from langchain_core.runnables import RunnablePassthrough

RunnablePassthrough().invoke({"num": 10})
# -> {'num': 10}   (받은 입력을 그대로 반환)
```

- 가장 단순한 형태는 **입력을 아무 가공 없이 그대로 다음 단계로 전달**하는 역할입니다.
- 왜 필요할까? 체인의 첫 단계가 `{"country": RunnablePassthrough()}` 처럼 감싸져 있으면,
  `chain.invoke("대한민국")` 처럼 **딕셔너리가 아닌 값**을 넣어도 자동으로
  `{"country": "대한민국"}` 형태로 변환되어 이후 `PromptTemplate`에 그대로 전달됩니다.

```python
runnable_chain = {"num": RunnablePassthrough()} | prompt | ChatOpenAI()

runnable_chain.invoke(10)   # 딕셔너리가 아니라 숫자 10만 넘겨도 동작함
# -> "10의 10배는 100입니다."
```

### `RunnablePassthrough.assign(...)` — 원본은 유지하면서 새 키를 추가

```python
RunnablePassthrough.assign(new_num=lambda x: x["num"] * 3).invoke({"num": 1})
# -> {'num': 1, 'new_num': 3}
```

- 입력 딕셔너리를 그대로 유지하면서, `new_num` 처럼 **계산된 값을 추가한 새 딕셔너리**를 만듭니다.
- `lambda x: ...`의 `x`는 이 단계로 들어온 입력 딕셔너리 전체입니다.

## 3. `RunnableParallel` + `RunnablePassthrough` 조합

```python
runnable = RunnableParallel(
    passed=RunnablePassthrough(),                              # 입력을 그대로 통과
    extra=RunnablePassthrough.assign(mult=lambda x: x["num"] * 3),  # 입력 + 계산값 추가
    modified=lambda x: x["num"] + 1,                            # 일반 함수도 그대로 넣을 수 있음
)

runnable.invoke({"num": 1})
# -> {'passed': {'num': 1}, 'extra': {'num': 1, 'mult': 3}, 'modified': 2}
```

`RunnableParallel`의 각 값 자리에는 체인뿐 아니라 `RunnablePassthrough`나 **평범한 람다 함수**도
넣을 수 있다는 걸 보여줍니다. 즉 "여러 갈래의 가공 결과를 한 딕셔너리로 모으기"에 자유롭게 활용됩니다.

## 4. `RunnableLambda` — 일반 파이썬 함수를 체인 부품으로 사용하기

```python
from langchain_core.runnables import RunnableLambda
from datetime import datetime

def get_today(a):
    return datetime.today().strftime("%b-%d")   # 오늘 날짜, 예: 'Sep-14'

prompt = PromptTemplate.from_template(
    "{today} 가 생일인 유명인이나 가수 {n} 명을 나열하세요. 생년월일을 표기해 주세요."
)
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

chain = (
    {"today": RunnableLambda(get_today), "n": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

chain.invoke(3)
# -> "9월 14일에 생일인 유명인이나 가수는 다음과 같습니다: 1. 안젤리나 졸리 ..."
```

- `RunnableLambda(함수)` : 일반 파이썬 함수를 체인 안에서 호출 가능한 부품(Runnable)으로 감싸줍니다.
  여기서는 `get_today`가 오늘 날짜 문자열을 계산해서 프롬프트의 `{today}` 자리를 채우는 데 쓰입니다.
- 체인 첫 단계의 딕셔너리 `{"today": ..., "n": ...}`는 `chain.invoke(3)`으로 넘긴 값(`3`)이
  `n`에는 `RunnablePassthrough()`를 통해 그대로 들어가고, `today`에는 `get_today` 함수의 실행 결과가
  들어가도록 **입력 하나를 여러 갈래로 나눠 가공**하는 패턴입니다.

### `itemgetter`로 딕셔너리 특정 키만 꺼내서 함수에 넘기기

```python
from operator import itemgetter

def length_function(text):
    return len(text)

def multiple_length_function(_dict):
    return len(_dict["text1"]) * len(_dict["text2"])

chain = (
    {
        "a": itemgetter("word1") | RunnableLambda(length_function),
        "b": {"text1": itemgetter("word1"), "text2": itemgetter("word2")}
        | RunnableLambda(multiple_length_function),
    }
    | prompt   # "{a} + {b} 는 무엇인가요?"
    | model
)

chain.invoke({"word1": "hello", "word2": "world"})
# -> AIMessage(content='5 + 25 = 30')
```

- `itemgetter("word1")` : 입력 딕셔너리에서 `"word1"` 키의 값만 꺼내는 함수입니다. 이것도
  `RunnableLambda`처럼 체인에 `|`로 연결할 수 있는 Runnable로 취급됩니다.
- `itemgetter("word1") | RunnableLambda(length_function)` : `word1` 값을 꺼낸 뒤 그 문자열의
  길이(`len("hello")` → `5`)를 계산해 `a`에 넣습니다.
- `{"text1": ..., "text2": ...} | RunnableLambda(multiple_length_function)` : `word1`, `word2` 두 값을
  각각 `text1`, `text2`로 매핑한 딕셔너리를 만든 뒤, 두 문자열 길이를 곱한 값(`5 × 5` → `25`)을 `b`에 넣습니다.
- 최종적으로 `{a} + {b} 는 무엇인가요?` 프롬프트에 `5 + 25`가 채워져 모델이 `30`이라고 답합니다.
  이는 **체인 입력의 일부만 골라서 서로 다른 가공을 거친 뒤 다시 하나의 프롬프트로 합치는** 전형적인 LCEL 패턴입니다.

## 참고 — 실행 로그에 보이는 LangSmith 연결 오류

`Failed to get info from https://eu.api.langchain.com ...` / `Failed to multipart ingest runs ...` 류의
경고는 LangSmith 트레이싱 전송 실패일 뿐, 체인 실행 결과 자체와는 무관합니다. 자세한 내용은
[`ch04_2_langsmith_README.md`](ch04_2_langsmith_README.md)를 참고하세요.
