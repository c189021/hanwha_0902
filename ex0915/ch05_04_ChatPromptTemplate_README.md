# ChatPromptTemplate — 대화형(멀티 메시지) 프롬프트 템플릿

09/15 실습. [`ch05_04_ChatPromptTemplate.ipynb`](ch05_04_ChatPromptTemplate.ipynb) — 지금까지 쓴 `PromptTemplate`은
**하나의 문자열 프롬프트**를 만드는 도구였다면, `ChatPromptTemplate`은 `system`/`human`/`ai` 역할이 있는
**여러 개의 메시지로 구성된 대화**를 템플릿화하는 도구입니다.

---

## 1. `PromptTemplate`과의 차이 — `from_template()`

```python
from langchain_core.prompts import ChatPromptTemplate

chat_prompt = ChatPromptTemplate.from_template("{country}의 수도는 어디인가요?")
chat_prompt.format(country="대한민국")
# -> 'Human: 대한민국의 수도는 어디인가요?'
```

- `ChatPromptTemplate.from_template()`도 `ch05_01`의 `PromptTemplate.from_template()`처럼 템플릿
  문자열에서 변수를 자동 추론합니다. 다만 내부적으로는 이 문자열을 **`HumanMessagePromptTemplate`
  하나로 감싼 메시지 리스트**로 관리합니다.
- 그래서 `.format()` 결과도 단순 문자열이 아니라 `'Human: ...'`처럼 **누가 말한 메시지인지 역할이
  표시된 문자열**로 나옵니다. Chat 모델(`ChatOpenAI` 등)은 문자열 하나가 아니라 "누가 무슨 말을 했는가"의
  목록(대화 기록)을 입력으로 받기 때문입니다.

## 2. `from_messages()` — 여러 역할의 메시지를 한 번에 정의

```python
chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 친절한 AI 어시스턴트입니다. 당신의 이름은 {name}입니다."),
        ("human", "반가워요!"),
        ("ai", "안녕하세요! 무엇을 도와드릴까요?"),
        ("human", "{user_input}"),
    ]
)
```

- `(역할, 템플릿문자열)` 튜플의 리스트로 대화 전체를 구성합니다. 역할은 세 가지입니다.
  - `"system"`: AI의 역할/성격/규칙을 지정하는 시스템 메시지 (사용자에게는 보이지 않고 모델 동작을 설정)
  - `"human"`: 사용자가 보낸 말
  - `"ai"`: 이전에 AI가 답변했던 말 (few-shot처럼 대화 예시를 미리 넣어 흐름을 잡아줄 때 사용)
- 각 메시지 템플릿 안에도 `{name}`, `{user_input}`처럼 변수를 자유롭게 넣을 수 있습니다. 변수는
  메시지 전체에서 모아져 `chat_template.input_variables`로 관리됩니다.
- 이 예시는 "이름이 {name}인 AI와 인사를 나눈 뒤, 사용자가 `{user_input}`을 물어보는" 대화 흐름을
  미리 짜 놓은 것입니다.

## 3. `format_messages()` — 메시지 객체 리스트로 완성하기

```python
messages = chat_template.format_messages(
    name="테디", user_input="당신의 이름은 무엇입니까?"
)
messages
```
```
[SystemMessage(content='당신은 친절한 AI 어시스턴트입니다. 당신의 이름은 테디입니다.', ...),
 HumanMessage(content='반가워요!', ...),
 AIMessage(content='안녕하세요! 무엇을 도와드릴까요?', ...),
 HumanMessage(content='당신의 이름은 무엇입니까?', ...)]
```

- `PromptTemplate.format()`이 문자열 하나를 반환했다면, `ChatPromptTemplate.format_messages()`는
  `SystemMessage`, `HumanMessage`, `AIMessage` 객체로 이루어진 **리스트**를 반환합니다. 각 변수(`{name}`,
  `{user_input}`)는 해당하는 메시지 안에서 값으로 치환됩니다.
- 이 메시지 리스트가 바로 Chat 모델이 실제로 받는 입력 형식입니다.

```python
llm = ChatOpenAI()
llm.invoke(messages).content
# -> '제 이름은 테디입니다. 부르실 때는 편하게 부르세요!'
```

- 완성된 메시지 리스트를 `llm.invoke()`에 그대로 넘기면, 모델은 system 메시지의 설정("이름은 테디")과
  이전 human/ai 주고받음을 대화 맥락으로 참고하여 답변합니다. 그 결과 "이름이 뭐냐"는 질문에
  system 메시지에서 지정한 "테디"로 정확히 답합니다.

## 4. 체인으로 연결하기

```python
chain = chat_template | llm
chain.invoke({"name": "Teddy", "user_input": "당신의 이름은 무엇입니까?"}).content
# -> '제 이름은 Teddy입니다. 어떻게 도와드릴까요?'
```

- `chat_template | llm`으로 체인을 구성하면 `format_messages()`를 직접 호출하지 않아도, `chain.invoke()`에
  넘긴 딕셔너리 값이 자동으로 각 메시지에 채워진 뒤 모델에 전달됩니다. `ch05_01`에서 본
  `prompt | llm` 패턴과 동일한 방식이며, 프롬프트가 단일 문자열이냐 메시지 리스트냐만 다릅니다.
- `name="Teddy"`로 바꾸자 모델 답변도 "테디" 대신 "Teddy"로 나온 것을 통해, system 메시지의 `{name}`
  값이 실제로 모델의 자기소개에 반영되었음을 확인할 수 있습니다.

## 요약

| 비교 | `PromptTemplate` (`ch05_01`) | `ChatPromptTemplate` |
|---|---|---|
| 표현하는 것 | 단일 문자열 프롬프트 | system/human/ai로 구성된 대화(메시지 목록) |
| 생성 | `from_template(문자열)` | `from_template(문자열)` 또는 `from_messages([(역할, 문자열), ...])` |
| 완성 결과 | `.format()` → 문자열 | `.format_messages()` → 메시지 객체 리스트 |
| 체인 결합 | `prompt \| llm` | `chat_template \| llm` (동일한 방식) |
