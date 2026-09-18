# ch08_01_ConversationBufferMemory.ipynb — 대화 버퍼 메모리

## 개요
LLM 자체는 상태(state)를 갖지 않는 **stateless** 존재입니다. 즉, `invoke()`를 여러 번 호출해도 이전 대화 내용을 스스로 기억하지 못합니다. 챗봇처럼 문맥을 이어가려면 이전 대화 기록을 매번 프롬프트에 함께 넣어줘야 하는데, 이를 도와주는 것이 LangChain의 **메모리(Memory)** 모듈입니다.

이 노트북에서는 가장 단순한 형태의 메모리인 `ConversationBufferMemory`를 사용해, 대화 내용을 있는 그대로 모두 누적 저장하고 불러오는 방법을 다룹니다.

## 핵심 개념

### 1. 메모리(Memory)가 필요한 이유
- LLM 호출은 기본적으로 독립적(stateless)이라, 이전 턴에서 나눈 대화를 다음 호출에서 참조하려면 개발자가 직접 이전 대화를 프롬프트에 포함시켜야 합니다.
- 메모리 모듈은 이 "대화 이력 저장 + 불러오기" 작업을 표준화된 인터페이스로 제공합니다.

### 2. `ConversationBufferMemory` — 가장 단순한 메모리
```python
from langchain_classic.memory import ConversationBufferMemory
memory = ConversationBufferMemory()
```
- 대화에서 오간 모든 Human/AI 메시지를 **가공 없이 그대로(버퍼)** 누적 저장합니다.
- 내부적으로 `InMemoryChatMessageHistory`에 `HumanMessage`, `AIMessage` 객체 리스트로 보관됩니다.
- **주의(Deprecation)**: `ConversationBufferMemory`는 LangChain 0.3.1부터 지원 중단(deprecated) 예정이며, 최신 버전에서는 `langchain.agents.create_agent`의 체크포인팅(checkpointing)이나 `Store` API를 사용해 단기/장기 기억을 구현하도록 권장하고 있습니다. 학습/개념 이해 목적으로는 여전히 유효하지만, 실무 신규 프로젝트에서는 새 API 사용을 고려해야 합니다.

### 3. 대화 저장 — `save_context()`
```python
memory.save_context(
    inputs={"human": "사용자 발화"},
    outputs={"ai": "AI 응답"},
)
```
- `inputs`와 `outputs` 딕셔너리를 한 쌍씩 넘기면, 내부적으로 `HumanMessage`/`AIMessage`로 변환되어 메모리에 순서대로 쌓입니다.
- 호출할 때마다 대화 한 턴(사용자 질문 + AI 답변)이 누적됩니다.

### 4. 대화 불러오기 — `load_memory_variables()`
```python
memory.load_memory_variables({})
# {'history': 'Human: ...\nAI: ...\nHuman: ...\nAI: ...'}
```
- 기본 설정에서는 저장된 전체 대화가 `"Human: ...\nAI: ..."` 형태의 **하나의 문자열**로 반환됩니다. 이 문자열을 프롬프트의 `{history}` 같은 변수에 그대로 삽입해 LLM에게 이전 문맥을 전달할 수 있습니다.
- 인자로 넘기는 빈 딕셔너리 `{}`는 다른 메모리 유형(예: 특정 키를 기준으로 검색하는 메모리)을 위한 자리로, `ConversationBufferMemory`에서는 특별히 사용되지 않습니다.

### 5. 메시지 객체 형태로 불러오기 — `return_messages=True`
```python
memory = ConversationBufferMemory(return_messages=True)
memory.load_memory_variables({})["history"]
# [HumanMessage(...), AIMessage(...), HumanMessage(...), AIMessage(...), ...]
```
- `return_messages=True`로 설정하면, 문자열이 아니라 `HumanMessage`/`AIMessage` **객체의 리스트**로 반환됩니다.
- Chat 모델(`ChatOpenAI` 등)에 메시지 리스트를 직접 넘겨야 하는 경우(`MessagesPlaceholder` 등과 함께 사용) 이 옵션이 유용합니다. 반면 단순 텍스트 프롬프트에 문맥을 삽입하는 경우엔 기본값(문자열 반환)이 더 편리합니다.

## 코드 흐름 요약
1. `.env` 로드 및 LangSmith 로깅 설정, `ChatOpenAI` 객체 생성
2. `ConversationBufferMemory()` 생성 (기본값: 문자열 반환)
3. `save_context()`로 은행 계좌 개설 상담 시나리오의 대화를 턴 단위로 저장
4. `load_memory_variables({})["history"]`로 누적된 전체 대화 문자열 확인
5. 여러 턴을 추가로 저장하며 히스토리가 계속 누적되는 것을 확인
6. `return_messages=True` 옵션으로 새 메모리를 만들어, 문자열이 아닌 메시지 객체 리스트로 히스토리를 받는 방식 비교

## 알아두면 좋은 점
- `ConversationBufferMemory`는 대화가 길어질수록 저장되는 내용도 계속 늘어나며, 이를 그대로 프롬프트에 넣으면 **토큰 수가 무한정 증가**해 비용 증가·컨텍스트 길이 초과 문제가 생길 수 있습니다. 이런 한계를 보완하기 위해 등장한 것이 다음 노트북(ch08_02)에서 다룰 요약형/윈도우형 메모리들입니다.
- 실무에서는 이 노트북의 개념(대화 이력을 어떻게 저장·구성하는지)을 이해한 뒤, 최신 LangChain 권장 방식인 `create_agent` + 체크포인터 기반 메모리로 옮겨가는 것이 좋습니다.
- `inputs`/`outputs`에 사용하는 키 이름(`"human"`, `"ai"`)은 관례적으로 붙인 것이며, 메모리 내부적으로는 어떤 입력이 사람 발화이고 어떤 출력이 AI 응답인지만 구분하면 됩니다.
