# MessagesPlaceholder — 메시지 목록 통째로 끼워 넣기

09/15 실습. [`ch05_05_MessagesPlaceholder.ipynb`](ch05_05_MessagesPlaceholder.ipynb) — [`ch05_04_ChatPromptTemplate_README.md`](ch05_04_ChatPromptTemplate_README.md)에서
만든 `ChatPromptTemplate`의 메시지 목록은 `("human", "...")`처럼 **개수와 내용이 고정**되어 있었습니다.
`MessagesPlaceholder`는 실행 시점에 **길이가 정해지지 않은 메시지 리스트**(대화 기록 등)를 통째로
끼워 넣을 수 있게 해주는 특수 자리표시자입니다.

---

## 1. 왜 필요한가 — 대화 기록처럼 개수가 변하는 입력

`ch05_04`의 `from_messages()`는 `("human", "반가워요!")`처럼 메시지 하나하나를 미리 고정된 개수만큼
템플릿에 박아 두는 방식이었습니다. 하지만 실제 챗봇에서는 "지금까지 주고받은 대화 전체"처럼 **턴 수가
매번 달라지는 메시지 묶음**을 프롬프트에 넣어야 하는 경우가 많습니다. 이런 가변 길이 메시지 목록을
위한 자리표시자가 `MessagesPlaceholder`입니다.

## 2. `MessagesPlaceholder`를 포함한 템플릿 구성

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "당신은 요약 전문 AI 어시스턴트입니다. 당신의 임무는 주요 키워드로 대화를 요약하는 것입니다.",
        ),
        MessagesPlaceholder(variable_name="conversation"),
        ("human", "지금까지의 대화를 {word_count} 단어로 요약합니다."),
    ]
)
```

- `("system", ...)`, `("human", ...)`은 `ch05_04`와 동일하게 역할과 내용이 고정된 메시지입니다.
- `MessagesPlaceholder(variable_name="conversation")`은 그 자체로 메시지 내용을 갖고 있지 않고,
  실행 시 `conversation`이라는 변수에 **메시지 리스트**가 통째로 전달되면 그 위치에 펼쳐서 삽입됩니다.
- 이 템플릿은 "시스템 지시 → (지금까지의 대화 기록이 여기 끼워짐) → 마지막으로 몇 단어로 요약해달라는
  요청"이라는 순서로 구성되어 있어, 대화 요약 챗봇의 전형적인 구조를 보여줍니다.
- `chat_prompt.input_variables`를 확인하면 `['conversation', 'word_count']`로, 일반 문자열 변수
  (`word_count`)와 메시지 목록 변수(`conversation`)가 함께 관리되는 것을 알 수 있습니다.

## 3. `.format()`으로 실제 메시지 채우기

```python
formatted_chat_prompt = chat_prompt.format(
    word_count=5,
    conversation=[
        ("human", "안녕하세요! 저는 오늘 새로 입사한 테디입니다. 만나서 반갑습니다."),
        ("ai", "반가워요! 앞으로 잘 부탁드립니다."),
    ],
)

print(formatted_chat_prompt)
```
```
System: 당신은 요약 전문 AI 어시스턴트입니다. 당신의 임무는 주요 키워드로 대화를 요약하는 것입니다.
Human: 안녕하세요! 저는 오늘 새로 입사한 테디입니다. 만나서 반갑습니다.
AI: 반가워요! 앞으로 잘 부탁드립니다.
Human: 지금까지의 대화를 5 단어로 요약합니다.
```

- `conversation`에 `("human", ...)`, `("ai", ...)` 튜플의 **리스트**를 넘기면, `MessagesPlaceholder`
  위치에 해당 메시지들이 순서대로 펼쳐져 들어갑니다. 리스트 길이가 2턴이든 10턴이든 템플릿 구조를
  바꿀 필요가 없습니다.
- 최종적으로 system 메시지 1개 + conversation의 human/ai 메시지 2개 + 마지막 human 메시지(요약 요청)
  1개, 총 4개의 메시지로 구성된 대화가 만들어집니다.

## 4. 체인 실행

```python
llm = ChatOpenAI()
chain = chat_prompt | llm | StrOutputParser()

chain.invoke(
    {
        "word_count": 5,
        "conversation": [
            ("human", "안녕하세요! 저는 오늘 새로 입사한 테디입니다. 만나서 반갑습니다."),
            ("ai", "반가워요! 앞으로 잘 부탁드립니다."),
        ],
    }
)
# -> '테디 새 입사, 반갑습니다!'
```

- `chat_prompt | llm | StrOutputParser()`로 체인을 구성한 뒤 `conversation`, `word_count` 두 변수를
  딕셔너리로 넘기면, system 메시지의 지시("주요 키워드로 요약")에 따라 방금 나눈 대화를 5단어 내외로
  요약한 결과를 받습니다. `StrOutputParser()`가 모델 응답 메시지 객체에서 텍스트만 뽑아내는 역할은
  [`ch04_6_outputparser_README.md`](../ex0914/ch04_6_outputparser_README.md)에서 다룬 내용과 동일합니다.

## 요약

| 구성 요소 | 역할 |
|---|---|
| `("system"/"human"/"ai", 문자열)` | 내용과 개수가 고정된 메시지 |
| `MessagesPlaceholder(variable_name="conversation")` | 실행 시 메시지 리스트를 통째로 끼워 넣는 가변 길이 자리표시자 |
| `.format(conversation=[("human", ...), ("ai", ...)])` | 실제 대화 기록으로 자리표시자를 채움 |

대화 기록처럼 매 턴 개수가 달라지는 메시지를 프롬프트에 넣어야 할 때는 메시지를 일일이
`from_messages()`에 나열하는 대신 `MessagesPlaceholder`를 사용하는 것이 핵심 패턴입니다.
