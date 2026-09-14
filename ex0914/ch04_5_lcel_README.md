# LCEL(LangChain Expression Language) — `prompt | model` 체인 기초

09/14 실습. [`ch04_5_lcel.ipynb`](ch04_5_lcel.ipynb) — LangChain에서 프롬프트와 모델을
파이프(`|`) 연산자로 이어 붙이는 **LCEL(LangChain Expression Language)**의 기본 사용법을 다룹니다.

---

## 1. LCEL이란?

```text
chain = prompt | model | output_parser
```

LCEL은 "프롬프트를 만들고 → 모델에 넣고 → 결과를 파싱한다"는 흐름을, 유닉스 파이프(`|`)처럼
**구성 요소를 연결해서 하나의 실행 가능한 체인(chain)**으로 표현하는 LangChain의 문법입니다.
각 단계를 함수 호출로 따로따로 작성하지 않고, `|`로 이어 붙이기만 하면 "입력 → 프롬프트 완성 →
모델 호출"이 자동으로 순서대로 실행됩니다.

## 2. `PromptTemplate` — 변할 값을 `{}`로 비워둔 프롬프트

```python
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template("{topic} 에 대해 쉽게 설명해주세요.")
```

- `{topic}` 처럼 중괄호로 감싼 부분이 **입력값으로 채워질 자리(변수)**입니다.
- `PromptTemplate.from_template(문자열)` : 문자열 템플릿으로부터 프롬프트 템플릿 객체를 만듭니다.
  나중에 `{"topic": "..."}` 형태의 딕셔너리를 넘기면 그 값이 `{topic}` 자리에 채워집니다.

## 3. 체인 만들기 — `prompt | model`

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

chain = prompt | model
```

- `prompt | model` : "프롬프트 템플릿의 출력(완성된 문자열)을 모델의 입력으로 그대로 넘긴다"는 뜻입니다.
  `chain` 하나로 "템플릿 채우기 + 모델 호출"이 합쳐진 새로운 실행 단위가 만들어집니다.
- `chain`을 그대로 출력해보면 `PromptTemplate(...) | ChatOpenAI(...)` 형태로, 두 컴포넌트가
  파이프로 연결된 구조임을 그대로 보여줍니다.

## 4. 체인 실행하기 — `invoke()` / `stream()`

```python
# 한 번에 전체 응답 받기
input = {"topic": "인공지능 모델의 학습 원리"}
chain.invoke(input)   # -> AIMessage(content="인공지능 모델의 학습 원리를 쉽게 설명하자면 ...")
```

```python
from langchain_teddynote.messages import stream_response

# 토큰 단위로 실시간 받기
answer = chain.stream(input)
stream_response(answer)
```

- `chain.invoke({"topic": "..."})` : 딕셔너리의 키(`topic`)가 프롬프트 템플릿의 `{topic}` 자리에
  채워진 뒤, 완성된 프롬프트가 모델로 전달되어 호출됩니다. 개별 `PromptTemplate.format()` +
  `llm.invoke()`를 따로 호출하지 않아도 됩니다.
- `chain.stream(input)` : 위와 동일하지만 결과를 토큰 단위 스트리밍으로 받습니다.
  ([`ch04_README.md`](ch04_README.md#3-스트리밍streaming--실시간-토큰-출력)의 `llm.stream()`과 같은 개념이
  체인 전체에도 그대로 적용됩니다.)

## 5. 변수 여러 개 쓰기

```python
prompt = PromptTemplate.from_template("{topic} 에 대해 쉽게 {how} 설명해주세요.")
model = ChatOpenAI()  # model 이름을 안 주면 langchain-openai 기본값(gpt-3.5-turbo) 사용

chain = prompt | model

input = {"topic": "인공지능 모델의 학습 원리", "how": "5살짜리도 이해하기 쉽게 설명해주세요."}
chain.invoke(input)
```

- 템플릿 안에 `{topic}`, `{how}` 처럼 **여러 개의 변수**를 넣을 수 있고, `invoke()`에 넘기는
  딕셔너리도 그만큼 키를 늘려주면 됩니다.
- `ChatOpenAI()`처럼 `model` 인자를 생략하면 `langchain-openai` 패키지의 **기본 모델**
  (이 실습 환경에서는 `gpt-3.5-turbo`)이 사용됩니다. 명시적으로 모델을 고정하고 싶다면
  [`ch04_README.md`](ch04_README.md)처럼 `model_name="gpt-4o-mini"`를 항상 지정하는 것이 안전합니다.

## 참고 — 실행 로그에 보이는 LangSmith 연결 오류

`Failed to get info from https://eu.api.langchain.com ...` 류의 경고는 LangSmith 트레이싱 전송
실패일 뿐, 체인 실행/모델 응답 자체와는 무관합니다. 자세한 내용은
[`ch04_2_langsmith_README.md`](ch04_2_langsmith_README.md)를 참고하세요.
