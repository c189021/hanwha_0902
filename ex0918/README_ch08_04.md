# ch08_04_RunnableWithMessageHistory.ipynb — LCEL 체인에 메모리 추가하기

## 개요
ch08_01~03에서는 `Memory` 객체 자체(`save_context`, `load_memory_variables`)를 직접 다뤘습니다. 이 노트북에서는 이러한 메모리를 **LCEL(LangChain Expression Language) 체인**과 실제로 연결해, "이전 대화를 참고해서 답변하는 체인"을 만드는 두 가지 방식을 다룹니다.

1. `RunnablePassthrough.assign()`으로 메모리를 체인에 수동 연결
2. `RunnableWithMessageHistory`로 세션별 대화 기록을 자동 관리 (SQLite 영구 저장 / 휘발성 메모리 저장 모두 실습)

## 핵심 개념

### 1. `MessagesPlaceholder` — 프롬프트에 대화 기록 슬롯 만들기
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful chatbot."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])
```
- `MessagesPlaceholder`는 프롬프트 안에 **메시지 리스트를 그대로 삽입할 자리**를 표시합니다.
- 여기 들어갈 `chat_history` 변수는 `HumanMessage`/`AIMessage` 객체들의 리스트여야 하며, 이는 메모리의 `return_messages=True` 옵션과 짝을 이룹니다.

### 2. `RunnablePassthrough.assign()`으로 메모리를 체인에 수동 연결하기
```python
from operator import itemgetter
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

runnable = RunnablePassthrough.assign(
    chat_history=RunnableLambda(memory.load_memory_variables)
    | itemgetter("chat_history")
)
```
- `RunnablePassthrough.assign(key=...)`은 **입력 딕셔너리에 새로운 키를 추가**하는 역할을 합니다. 원래 입력(`{"input": "hi"}`)은 그대로 유지한 채, `chat_history`라는 키를 새로 채워 넣습니다.
- `RunnableLambda(memory.load_memory_variables)`는 `memory.load_memory_variables({})`를 호출한 결과(`{"chat_history": [...]}`)를 반환합니다.
- 여기서 `itemgetter("chat_history")`가 왜 필요한지가 핵심 포인트입니다.
  - `itemgetter` 없이 그대로 두면: `{"input": "hi", "chat_history": {"chat_history": []}}` 처럼 **딕셔너리 안에 딕셔너리**가 중첩되어 버립니다 (노트북의 `bb024e0c` 셀에서 실제로 이 문제를 보여줌).
  - `itemgetter("chat_history")`를 붙이면: 중첩된 딕셔너리에서 `chat_history` 키의 값(메시지 리스트)만 꺼내어, 최종적으로 `{"input": "hi", "chat_history": []}` 형태가 됩니다. 이것이 프롬프트의 `MessagesPlaceholder(variable_name="chat_history")`가 기대하는 형태입니다.
- 이렇게 구성한 `runnable`을 프롬프트, 모델과 연결합니다.
```python
chain = runnable | prompt | model
```
- **주의**: 이 방식은 `chain.invoke()`를 호출해도 메모리에 **자동으로 저장되지 않습니다.** 실습에서 보듯, 응답을 받은 뒤 반드시 `memory.save_context(...)`를 수동으로 호출해야 다음 질문에서 문맥이 유지됩니다. (이 수동 저장의 번거로움을 해결한 것이 다음의 `RunnableWithMessageHistory`)

### 3. `RunnableWithMessageHistory` — 세션 기반 자동 히스토리 관리
```python
from langchain_core.runnables.history import RunnableWithMessageHistory

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,           # 세션 ID → 히스토리 객체를 반환하는 함수
    input_messages_key="question", # 사용자 입력이 들어갈 프롬프트 변수명
    history_messages_key="chat_history",  # 대화 기록이 들어갈 프롬프트 변수명
)
```
- `RunnableWithMessageHistory`는 체인을 감싸서, `invoke()` 호출 시마다 **자동으로** (1) 해당 세션의 과거 기록을 불러와 프롬프트에 채우고, (2) 이번 질문/답변을 히스토리에 저장까지 처리합니다. 앞서 본 수동 `save_context()` 호출이 필요 없어집니다.
- `config={"configurable": {"session_id": "abc123"}}`처럼 **세션 ID를 config로 전달**하여, 세션별로 독립된 대화 기록을 유지합니다.
- **Deprecation 안내**: `RunnableWithMessageHistory` 역시 Deprecated 상태이며, LangChain은 대신 **LangGraph의 내장 영속성(persistence)** 사용을 권장합니다.

### 4. SQLite 기반 영구 저장 — `SQLChatMessageHistory`
```python
from langchain_community.chat_message_histories import SQLChatMessageHistory

chat_message_history = SQLChatMessageHistory(
    session_id="sql_history",
    connection="sqlite:///sqlite.db",
)
chat_message_history.add_user_message("...")
chat_message_history.add_ai_message("...")
```
- 인메모리 방식(`ConversationBufferMemory` 등)은 **프로세스가 종료되면 대화 내용이 사라집니다.** 이어서 대화를 계속하려면 DB 같은 영구 저장소가 필요합니다.
- `SQLChatMessageHistory`는 대화 메시지를 SQLite 파일(`sqlite.db`)에 저장해, 프로세스를 재시작해도 이전 대화를 그대로 불러올 수 있게 합니다.

### 5. 다중 사용자 지원 — `ConfigurableFieldSpec`
```python
def get_chat_history(user_id, conversation_id):
    return SQLChatMessageHistory(
        table_name=user_id,
        session_id=conversation_id,
        connection="sqlite:///sqlite.db",
    )

from langchain_core.runnables.utils import ConfigurableFieldSpec

config_fields = [
    ConfigurableFieldSpec(id="user_id", annotation=str, name="User ID", ...),
    ConfigurableFieldSpec(id="conversation_id", annotation=str, name="Conversation ID", ...),
]

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_chat_history,
    input_messages_key="question",
    history_messages_key="chat_history",
    history_factory_config=config_fields,
)
```
- 세션 ID 하나만으로는 "어떤 사용자의 어떤 대화방인지"를 구분하기 부족할 때, `user_id` + `conversation_id` **두 개의 축**으로 대화 기록을 분리 관리할 수 있습니다.
- `ConfigurableFieldSpec`은 `RunnableWithMessageHistory`가 config로부터 받을 파라미터(이름, 타입, 설명 등)를 정의하는 스펙입니다.
- 실습 결과, 같은 `user1`이라도 `conversation1`에서는 "테디"라는 이름을 기억하지만, `conversation2`에서는 대화 기록이 분리되어 있어 이름을 기억하지 못하는 것을 확인할 수 있습니다.

### 6. 휘발성 메모리 — `ChatMessageHistory` + 딕셔너리 세션 스토어
```python
from langchain_community.chat_message_histories import ChatMessageHistory

store = {}  # 세션 기록을 저장할 딕셔너리 (프로세스 종료 시 소멸)

def get_session_history(session_ids):
    if session_ids not in store:
        store[session_ids] = ChatMessageHistory()
    return store[session_ids]
```
- DB 없이 파이썬 딕셔너리(`store`)에 세션별 `ChatMessageHistory` 객체를 담아두는 방식입니다.
- SQLite 방식과 달리 **프로세스가 종료되면 모든 대화가 사라지는 휘발성(in-memory)** 저장소입니다. 빠른 프로토타이핑이나 테스트에 적합합니다.
- 실습에서 `session_id="abc123"`에는 "테디"라는 이름을 저장했지만, 다른 세션 `"abc1234"`에서 이름을 물으면 해당 세션 기록이 비어 있으므로 "이름을 알 수 없다"고 답하는 것을 확인할 수 있습니다.

## 코드 흐름 요약
1. `MessagesPlaceholder`가 포함된 프롬프트 + `ConversationBufferMemory`를 `RunnablePassthrough.assign()`으로 수동 연결 → `itemgetter`의 필요성 확인
2. 체인 실행 후 `memory.save_context()`를 수동 호출해야 다음 질문에서 문맥이 유지됨을 실습으로 확인
3. `SQLChatMessageHistory`로 대화를 SQLite 파일에 영구 저장하는 방법 실습
4. `RunnableWithMessageHistory` + `get_chat_history(user_id, conversation_id)` + `ConfigurableFieldSpec`로 다중 사용자/다중 대화방을 지원하는 체인 구성
5. `ChatMessageHistory` + 딕셔너리 기반 `store`로 세션 ID만으로 구분되는 휘발성 메모리 체인 구성

## 알아두면 좋은 점
- `RunnablePassthrough.assign()` 방식은 메모리 연결 원리를 이해하는 데 유용하지만, 실무에서는 저장을 자동화해주는 `RunnableWithMessageHistory`(또는 최신 LangGraph 방식)를 쓰는 것이 훨씬 편리합니다.
- **세션 식별 전략**이 중요합니다. 단순 챗봇이면 `session_id` 하나로 충분하지만, 여러 사용자가 여러 대화방을 오가는 서비스라면 `user_id` + `conversation_id`처럼 복수 축으로 설계해야 합니다.
- 인메모리(`ChatMessageHistory` + dict)는 재시작 시 소실되므로 프로토타입/테스트용으로, 운영 서비스에서는 `SQLChatMessageHistory`나 Redis 등 영구 저장소를 사용해야 합니다.
- 이 노트북 전반에 사용된 `RunnableWithMessageHistory`, `ConversationBufferMemory`는 Deprecated 상태이며, LangChain 공식 문서는 **LangGraph 기반 checkpointer**로의 전환을 권장하고 있습니다 (관련 배경은 [[ch08_02]] 참고).
