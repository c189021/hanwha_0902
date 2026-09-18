# ch08_02_ConversationMemoryTypes.ipynb — 다양한 대화 메모리 유형

## 개요
ch08_01에서 다룬 `ConversationBufferMemory`는 대화를 무제한으로 누적 저장하기 때문에, 대화가 길어질수록 토큰 사용량이 계속 증가하는 문제가 있습니다. 이 노트북에서는 이 문제를 다양한 방식으로 완화하는 **4가지 메모리 유형**을 비교합니다.

1. **ConversationBufferWindowMemory** — 최근 N개의 대화만 유지 (윈도우)
2. **ConversationTokenBufferMemory** — 토큰 수 기준으로 오래된 대화 제거
3. **ConversationEntityMemory** — 대화에 등장한 "개체(entity)"의 정보만 요약 추출
4. **ConversationKGMemory** — 대화 내용을 지식 그래프(주어-관계-목적어) 형태로 추출/저장

## 핵심 개념

### 1. 대화 버퍼 윈도우 메모리 (`ConversationBufferWindowMemory`)
```python
from langchain_classic.memory import ConversationBufferWindowMemory
memory = ConversationBufferWindowMemory(k=2, return_messages=True)
```
- `k` 파라미터로 **최근 몇 개의 대화 턴(Human+AI 쌍)** 만 유지할지 지정합니다. `k=2`면 최신 2턴(=메시지 4개)만 남고 그 이전 대화는 버려집니다.
- 실습에서 6턴을 저장했지만 `load_memory_variables()`로 확인하면 **가장 최근 2턴(다음 주, 다음 달 질문)** 만 남아 있는 것을 확인할 수 있습니다.
- 장점: 항상 일정한 대화 길이를 유지해 토큰 사용량이 예측 가능함
- 단점: `k`턴보다 오래된 대화 내용은 완전히 사라져, 초반에 언급된 중요한 정보를 잊어버릴 수 있음

### 2. 대화 토큰 버퍼 메모리 (`ConversationTokenBufferMemory`)
```python
from langchain_classic.memory import ConversationTokenBufferMemory
memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=200,   # 토큰 수 기준 제한
    return_messages=True,
)
```
- 메시지 "개수"가 아니라 **토큰 수**를 기준으로 오래된 대화를 잘라냅니다. `llm`을 넘겨주는 이유는 해당 모델의 토크나이저 기준으로 토큰 수를 계산하기 위함입니다.
- `max_token_limit`이 작을수록 유지되는 대화 분량이 줄어듭니다(예: 200 토큰 제한이면 초반 대화 일부가 잘려나감).
- 윈도우 메모리(턴 개수 고정)와 달리, **메시지 길이에 따라 유지되는 턴의 개수가 달라진다**는 점이 특징입니다. 실습 결과 6턴 중 앞의 일부(가장 오래된 Human 메시지 등)가 잘려나간 것을 확인할 수 있습니다.

### 3. 대화 엔티티 메모리 (`ConversationEntityMemory`)
```python
from langchain_classic.memory import ConversationEntityMemory
from langchain_classic.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_classic.chains import ConversationChain

conversation = ConversationChain(
    llm=llm,
    prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
    memory=ConversationEntityMemory(llm=llm),
)
```
- 대화 전체를 그대로 저장하는 대신, LLM을 이용해 대화 속에 등장하는 **개체(entity, 예: 사람 이름)** 를 자동으로 인식하고 각 개체에 대한 요약 정보를 별도로 관리합니다.
- `ENTITY_MEMORY_CONVERSATION_TEMPLATE`을 보면 프롬프트에 `{entities}`(개체별 요약 정보)와 `{history}`(최근 대화)가 함께 들어가는 구조임을 알 수 있습니다.
- 실습 결과, "테디"와 "셜리"라는 두 인물에 대한 정보가 자동으로 추출되어 저장됩니다.
```python
conversation.memory.entity_store.store
# {'테디': '테디는 개발자이며, 셜리와 함께 자신들의 회사를 차릴 계획을 세우고 있습니다.',
#  '셜리': '셜리는 디자이너로, 테디와 함께 자신들의 회사를 차릴 계획을 세우고 있습니다.'}
```
- 장점: 대화가 길어져도 특정 인물/사물에 대한 핵심 정보만 압축되어 유지되므로 토큰 효율적
- 단점: 개체 추출을 위해 내부적으로 추가 LLM 호출이 발생 (비용/지연 증가)

### 4. 대화 지식 그래프 메모리 (`ConversationKGMemory`)
```python
from langchain_classic.memory import ConversationKGMemory
memory = ConversationKGMemory(llm=llm, return_messages=True)
```
- 대화 내용을 **지식 그래프(Knowledge Graph)** 형태, 즉 "주어-관계-목적어" 트리플로 추출해 저장합니다.
- 예시 결과:
```
On 김셜리씨: 김셜리씨 거주중인 Pangyo. 김셜리씨 is a 신입 디자이너. 김셜리씨 works at 우리 회사.
```
- 특정 주제(예: "김셜리씨")에 대해 질문(`load_memory_variables({"input": "김셜리씨는 누구입니까?"})`)하면, 관련된 그래프 정보만 추려서 반환합니다. 즉, **질의 기반으로 관련 지식만 선택적으로 불러올 수 있다**는 점이 엔티티 메모리와의 차이입니다.
- `ConversationChain` + 커스텀 프롬프트와 결합하면, LLM이 "Relevant Information" 섹션에 담긴 그래프 정보만 참고해 답하도록 유도할 수 있습니다.

### 5. 공통 주의사항 — Deprecation 경고
이 노트북에 등장하는 `ConversationBufferWindowMemory`, `ConversationTokenBufferMemory`, `ConversationEntityMemory`, `ConversationKGMemory`, `ConversationChain`은 모두 **LangChain 0.2~0.3대에서 Deprecated** 처리되었고, 2.0.0에서 제거될 예정입니다. 최신 LangChain에서는 이 역할을 `langchain.agents.create_agent` + 체크포인터(checkpointing) 또는 `Store` API로 대체하도록 안내하고 있습니다. 이 노트북은 메모리의 **개념**을 이해하기 위한 학습 자료로 보고, 실무에서는 최신 API를 확인해야 합니다.

## 메모리 유형 비교

| 메모리 유형 | 유지 기준 | 특징 |
|---|---|---|
| BufferMemory (ch08_01) | 전체 다 저장 | 가장 단순하지만 토큰이 무한 증가 |
| BufferWindowMemory | 최근 k개 턴 | 턴 개수 기준, 구현 간단 |
| TokenBufferMemory | 최대 토큰 수 | 토큰 기준, 메시지 길이에 유연하게 대응 |
| EntityMemory | 등장 개체(사람 등) | 개체별 핵심 정보만 압축 저장 |
| KGMemory | 지식 그래프(트리플) | 주어-관계-목적어 형태로 구조화, 질의 기반 조회 가능 |

## 코드 흐름 요약
1. `ConversationBufferWindowMemory(k=2)`로 최근 2턴만 유지되는 것을 6턴 저장 후 확인
2. `ConversationTokenBufferMemory(max_token_limit=200)`로 토큰 기준 컷오프 확인
3. `ENTITY_MEMORY_CONVERSATION_TEMPLATE` 프롬프트 구조 확인 후, `ConversationEntityMemory` + `ConversationChain`으로 "테디/셜리" 대화에서 개체 정보 자동 추출
4. `ConversationKGMemory`로 "김셜리씨" 정보를 트리플 형태로 저장하고 질의 기반 조회
5. 커스텀 프롬프트 + `ConversationKGMemory`로 영어 대화("Teddy", "Shirley") 예제 반복 실습

## 알아두면 좋은 점
- 어떤 메모리를 선택할지는 **애플리케이션 특성**에 따라 달라집니다. 단순 챗봇이면 윈도우/토큰 버퍼로 충분하지만, 특정 인물·사물에 대한 정보를 지속적으로 참조해야 하는 CRM성 챗봇이라면 엔티티/KG 메모리가 유리합니다.
- 엔티티 메모리와 KG 메모리는 내부적으로 **LLM을 추가로 호출**해 정보를 추출하므로, 응답 지연과 비용이 늘어날 수 있다는 점을 감안해야 합니다.
- 최신 프로젝트에서는 이 노트북의 legacy 메모리 클래스 대신 `create_agent`의 체크포인터/Store 기반 메모리 사용을 검토하는 것이 좋습니다.
