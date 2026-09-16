# PromptTemplate — 프롬프트 템플릿 기초

09/15 실습. [`ch05_01_PromptTemplate.ipynb`](ch05_01_PromptTemplate.ipynb) — LangChain에서 프롬프트에 **변수를 삽입**하고
재사용 가능한 템플릿으로 관리하는 기본기인 `PromptTemplate`을 다룹니다.

---

## 1. 프롬프트 템플릿이란

프롬프트 템플릿은 `{변수명}` 형태의 자리표시자(placeholder)를 포함한 문자열입니다. 실행 시점에 이 자리표시자에
실제 값을 채워 넣어(format) 최종 프롬프트 문자열을 만듭니다. 예를 들어 RAG(검색 증강 생성) 시스템에서는
아래와 같은 형태의 템플릿을 자주 사용합니다.

```
당신은 질문-답변(Question-Answer) Task를 수행하는 AI 어시스턴트입니다.
검색된 문맥(context)을 사용하여 질문(question)에 답하세요.
만약, 문맥(context)으로부터 답을 찾을 수 없다면 '모른다'고 말하세요.
한국어로 대답하세요.

Question: {이곳에 사용자가 입력한 질문이 삽입됩니다}
Context: {이곳에 검색된 정보가 삽입됩니다}
```

`{question}`, `{context}`처럼 실행 시점에 바뀌는 부분을 변수로 빼 두면, 질문/문맥이 달라질 때마다
프롬프트 문자열을 직접 새로 작성하지 않고 값만 갈아 끼울 수 있습니다.

## 2. `from_template()` — 템플릿 문자열로 빠르게 생성

```python
from langchain_core.prompts import PromptTemplate

template = "{country}의 수도는 어디인가요?"
prompt = PromptTemplate.from_template(template)

prompt.format(country="대한민국")
# -> '대한민국의 수도는 어디인가요?'
```

- `from_template()`은 문자열 안의 `{country}`를 자동으로 인식해 `input_variables=['country']`를 채운
  `PromptTemplate` 객체를 만들어 주는 클래스 메서드입니다. 변수 목록을 따로 적어줄 필요가 없습니다.
- `.format(country="대한민국")`을 호출하면 실제로 값이 채워진 **완성된 프롬프트 문자열**을 돌려받습니다.

### 체인과 결합하기

```python
llm = ChatOpenAI()
chain = prompt | llm

chain.invoke("대한민국").content
# -> '대한민국의 수도는 서울입니다.'
```

- `prompt | llm`으로 체인을 구성하면, `chain.invoke()`에 넘긴 값이 템플릿의 유일한 변수(`country`)에
  자동으로 매핑되어 프롬프트가 완성된 뒤 LLM에 전달됩니다. 자세한 파이프(`|`) 체인 구성 방식은
  [`ch04_5_lcel_README.md`](../ex0914/ch04_5_lcel_README.md)를 참고하세요.

## 3. 생성자를 직접 사용하기 — `input_variables` 명시

```python
prompt = PromptTemplate(
    template="{country}의 수도는 어디인가요?",
    input_variables=["country"],
)
```

- `from_template()`이 변수를 자동으로 추론하는 것과 달리, 생성자를 직접 호출할 때는 `input_variables`를
  **명시적으로** 지정합니다. 결과적으로 동일한 `PromptTemplate` 객체가 만들어지지만, 어떤 변수가
  필요한지 코드 상에서 더 분명하게 드러납니다.

## 4. `partial_variables` — 일부 변수를 미리 고정하기

```python
prompt = PromptTemplate(
    template="{country1}과 {country2}의 수도는 각각 어디인가요?",
    input_variables=["country1"],
    partial_variables={
        "country2": "미국"  # dictionary 형태로 partial_variables 전달
    },
)

prompt.format(country1="대한민국")
# -> '대한민국과 미국의 수도는 각각 어디인가요?'
```

- 템플릿에는 `{country1}`, `{country2}` 두 변수가 있지만, `country2`는 `partial_variables`로
  **미리 "미국"이라는 고정값**을 채워 넣었습니다. 그 결과 `input_variables`에는 `country1`만 남고,
  `.format()` 호출 시 `country1`만 넘기면 됩니다.
- 여러 프롬프트에서 공통으로 재사용하는 값(예: 오늘 날짜, 고정된 언어 설정 등)을 미리 박아두고 싶을 때
  유용합니다.

### `.partial()` 메서드 — 기존 템플릿의 일부 값 다시 고정

```python
prompt_partial = prompt.partial(country2="캐나다")
prompt_partial.format(country1="대한민국")
# -> '대한민국과 캐나다의 수도는 각각 어디인가요?'
```

- `.partial(country2="캐나다")`는 기존 `prompt` 객체를 수정하는 게 아니라, `country2` 값이
  "미국" → "캐나다"로 바뀐 **새로운 `PromptTemplate` 객체**를 반환합니다.
- 체인에 연결한 뒤에도 이미 고정된 변수는 그대로 유지되고, 남은 변수(`country1`)만 입력받습니다.

```python
chain = prompt_partial | llm
chain.invoke("대한민국").content
# -> '대한민국의 수도는 서울이며, 캐나다의 수도는 오타와입니다.'

# 체인 호출 시 딕셔너리로 넘기면 partial로 고정된 값도 덮어쓸 수 있음
chain.invoke({"country1": "대한민국", "country2": "호주"}).content
# -> '대한민국의 수도는 서울이고, 호주의 수도는 캔버라입니다.'
```

- `chain.invoke("대한민국")`처럼 문자열 하나만 넘기면 남은 변수 `country1`에 자동으로 매핑됩니다.
- `chain.invoke({...})`처럼 딕셔너리로 여러 키를 넘기면, `partial_variables`로 미리 고정해 둔 값이라도
  **명시적으로 넘긴 값이 우선**하여 덮어써집니다(위 예시에서 `country2`가 "캐나다" 대신 "호주"로 적용됨).

## 요약

| 방법 | 변수 지정 방식 | 용도 |
|---|---|---|
| `PromptTemplate.from_template(template)` | 템플릿 문자열에서 자동 추론 | 빠르게 템플릿 생성 |
| `PromptTemplate(template=..., input_variables=[...])` | 명시적으로 지정 | 변수를 코드에서 명확히 드러내고 싶을 때 |
| `partial_variables={...}` (생성자 인자) | 생성 시점에 일부 값 고정 | 공통으로 재사용할 고정값이 있을 때 |
| `prompt.partial(key=value)` | 기존 템플릿에서 일부 값 재고정 | 동일 템플릿을 변형해 재사용할 때 |
