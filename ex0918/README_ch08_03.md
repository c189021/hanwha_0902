# ch08_03_SummaryVectorStoreMemory.ipynb — 대화 요약 메모리 & 벡터 스토어 검색 메모리

## 개요
ch08_02에서 다룬 엔티티/지식그래프 메모리는 정보를 구조화해 압축 저장하지만, 그 과정에서 세부 뉘앙스가 손실될 수 있습니다. 이 노트북에서는 **정보 손실을 최소화하면서 대화를 압축하는 요약 메모리**(`ConversationSummaryMemory`, `ConversationSummaryBufferMemory`)와, **의미 유사도 기반으로 과거 대화를 검색하는 벡터 스토어 메모리**(`VectorStoreRetrieverMemory`)를 다룹니다.

## 핵심 개념

### 1. 대화 요약 메모리 (`ConversationSummaryMemory`)
```python
from langchain_classic.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(
    llm=ChatOpenAI(model_name="gpt-4o", temperature=0),
    return_messages=True,
)
```
- 대화가 저장될 때마다 LLM을 이용해 **지금까지의 전체 대화를 하나의 요약문으로 압축**합니다.
- `save_context()`를 호출할 때마다 이전 요약 + 새 대화 내용을 다시 LLM에 넣어 **누적 요약을 갱신**하는 방식으로 동작합니다.
- 실습에서 7턴의 유럽 여행 패키지 상담 대화를 저장한 뒤 `load_memory_variables({})`로 확인하면, 전체 대화가 하나의 `SystemMessage` 요약 문단으로 반환됩니다.
- 장점: `ConversationBufferWindowMemory`처럼 오래된 정보를 통째로 버리지 않고, 요약 형태로나마 전체 맥락을 계속 유지
- 단점: 매 저장마다 요약을 위한 **추가 LLM 호출**이 발생 → 비용/지연 증가, 그리고 요약 과정에서 세부 디테일(정확한 숫자 등)이 다소 손실될 수 있음

### 2. 대화 요약 버퍼 메모리 (`ConversationSummaryBufferMemory`)
```python
from langchain_classic.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=200,   # 이 토큰 수를 넘으면 오래된 부분부터 요약
    return_messages=True,
)
```
- `ConversationSummaryMemory`와 `ConversationTokenBufferMemory`의 **하이브리드** 방식입니다.
- 최근 대화는 원문 그대로(`HumanMessage`/`AIMessage`) 유지하다가, 누적 토큰 수가 `max_token_limit`을 초과하면 **가장 오래된 대화부터 요약(SystemMessage)으로 압축**합니다.
- 실습 결과를 보면, 오래된 대화(가격, 관광지, 보험, 비즈니스 클래스 관련 문답)는 하나의 요약(`SystemMessage`)으로 합쳐지고, 가장 최근 턴(호텔 등급 질문)은 원문 그대로(`HumanMessage`, `AIMessage`) 유지됩니다.
- 장점: 최근 대화는 정확한 원문으로 유지하면서, 오래된 대화도 완전히 버리지 않고 요약으로 보존 — 두 방식의 장점을 절충

### 3. 벡터 스토어 검색 메모리 (`VectorStoreRetrieverMemory`)
```python
import faiss
from langchain_openai import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_classic.memory import VectorStoreRetrieverMemory

embeddings = OpenAIEmbeddings()
index = faiss.IndexFlatL2(1536)                       # 임베딩 차원(1536)에 맞춘 FAISS 인덱스
vectorstore = FAISS(embeddings, index, InMemoryDocstore({}), {})

retriever = vectorstore.as_retriever(search_kwargs={"k": 1})  # 상위 1개만 검색
memory = VectorStoreRetrieverMemory(retriever=retriever)
```
- 지금까지의 메모리들은 대화를 **시간 순서**(최신 k턴, 토큰 제한 등)로 다뤘지만, 벡터 스토어 메모리는 **의미적 유사도**를 기준으로 과거 대화 중 질의(query)와 가장 관련 있는 항목을 찾아옵니다.
- 동작 방식:
  1. 각 대화 턴을 임베딩(`OpenAIEmbeddings`)하여 FAISS 벡터 인덱스에 저장
  2. 새로운 질문이 들어오면 그 질문을 임베딩하고, 벡터 유사도(`IndexFlatL2` = L2 거리)가 가장 가까운 상위 `k`개의 과거 대화를 검색해 반환
- 실습에서 면접 대화 4턴을 저장한 후:
  - `"면접자 전공은 무엇인가요?"` → 자기소개 관련 턴이 검색됨
  - `"면접자가 프로젝트에서 맡은 역할은 무엇인가요?"` → 역할 관련 턴이 검색됨
  - 즉, **저장 순서와 무관하게 질문 의미에 맞는 대화만 뽑아온다**는 것이 핵심 특징입니다.
- 장점: 대화가 아주 길어져도 관련 있는 부분만 정확히 찾아 낼 수 있어 확장성이 좋음 (RAG와 유사한 원리)
- 단점: 임베딩 계산 및 벡터 검색에 따른 비용/인프라(FAISS 등 벡터DB)가 추가로 필요, 시간적 흐름(최근 대화 우선순위)은 고려하지 않음

### 4. FAISS 관련 구성요소
| 구성요소 | 역할 |
|---|---|
| `OpenAIEmbeddings()` | 텍스트를 1536차원 벡터로 변환하는 임베딩 모델 |
| `faiss.IndexFlatL2(embedding_size)` | 벡터 간 L2(유클리드) 거리 기반 최근접 이웃 검색 인덱스 |
| `InMemoryDocstore({})` | 벡터에 대응하는 원본 문서(텍스트)를 메모리에 저장하는 저장소 |
| `FAISS(embeddings, index, docstore, {})` | 위 요소들을 결합한 벡터 스토어 객체 |
| `vectorstore.as_retriever(search_kwargs={"k": 1})` | 벡터 스토어를 "질의 시 상위 k개 반환"하는 Retriever 인터페이스로 변환 |

## 메모리 유형 비교 (ch08_02 + ch08_03 종합)

| 메모리 유형 | 압축/검색 방식 | 세부 정보 보존도 |
|---|---|---|
| SummaryMemory | 전체를 하나의 요약으로 압축 | 중간 (요약 과정에서 손실 가능) |
| SummaryBufferMemory | 오래된 부분만 요약 + 최근은 원문 유지 | 높음 (하이브리드) |
| VectorStoreRetrieverMemory | 의미 유사도 기반 검색(시간순 무시) | 검색된 항목은 원문 그대로 |

## 코드 흐름 요약
1. `ConversationSummaryMemory`로 유럽 여행 패키지 상담 7턴을 저장 → 하나의 요약문으로 압축되는 것 확인
2. `ConversationSummaryBufferMemory(max_token_limit=200)`로 동일 시나리오 진행 → 오래된 대화는 요약, 최근 대화는 원문 유지되는 것 비교
3. FAISS + `OpenAIEmbeddings`로 벡터 스토어 구성
4. `VectorStoreRetrieverMemory(retriever, k=1)`로 면접 대화 4턴 저장
5. 서로 다른 질의로 `load_memory_variables()`를 호출해, 질의 의미와 가장 유사한 과거 대화가 검색되는 것을 확인

## 알아두면 좋은 점
- `ConversationSummaryBufferMemory`, `VectorStoreRetrieverMemory` 역시 [[ch08_02]]에서 언급한 다른 legacy 메모리들과 마찬가지로 LangChain 0.3.1부터 Deprecated 상태이며, 최신 프로젝트에서는 `create_agent` + 체크포인터/`Store` API 기반 구현을 검토해야 합니다.
- 벡터 스토어 메모리는 사실상 **RAG(Retrieval-Augmented Generation)** 의 축소판입니다. 대화 이력을 문서처럼 취급해 검색한다는 점에서, 문서 기반 RAG 시스템 설계 시 사고방식을 그대로 적용할 수 있습니다.
- 실무에서는 목적에 따라 조합해서 사용하기도 합니다. 예: 최근 대화는 버퍼로 유지 + 오래된 대화는 요약 + 특정 키워드 검색이 필요하면 벡터 스토어 병행.
