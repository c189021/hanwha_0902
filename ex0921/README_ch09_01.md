# ch09_01_document_loader.ipynb — 문서 로더의 구조 이해하기

## 개요
RAG(Retrieval-Augmented Generation)의 첫 단계는 **다양한 형태의 원본 문서(PDF, HWP, CSV, 웹 등)를 LLM이 다룰 수 있는 표준 객체로 불러오는 것**입니다. LangChain은 이를 위해 `Document` 객체와 다양한 **Document Loader**를 제공합니다.

이 노트북에서는 문서 로더의 가장 기본 구조를 이해하기 위해 다음을 다룹니다.
1. `Document` 객체의 구조 (`page_content` + `metadata`)
2. `PyPDFLoader`로 PDF 로드하기 (`load()`)
3. 로드와 동시에 청크로 분할하기 (`load_and_split()`)
4. `chunk_overlap`의 개념
5. 지연 로딩(`lazy_load()`)과 비동기 로딩(`aload()`)

## 핵심 개념

### 1. `Document` 객체 — LangChain의 기본 문서 단위
```python
from langchain_core.documents import Document

doc = Document(page_content="안녕하세요? 랭체인의 도큐먼트입니다.")
doc.metadata["source"] = "skc소스"
doc.metadata["page"] = 1
doc.metadata["author"] = "어쩌구~저자"
```
| 속성 | 의미 |
|---|---|
| `page_content` | 문서의 실제 텍스트 본문 (문자열) |
| `metadata` | 문서에 대한 부가 정보 딕셔너리 (출처, 페이지, 저자 등 자유롭게 추가 가능) |
| `id` | 문서 식별자 (선택, 기본값 `None`) |

- 모든 Document Loader는 결과를 `Document` 객체(또는 그 리스트)로 반환하므로, 이후 단계(분할, 임베딩, 벡터스토어 저장)를 **문서 형식과 무관하게 동일한 방식**으로 처리할 수 있습니다.
- `metadata`는 나중에 검색 결과의 **출처 표시**, **필터링**(예: 특정 페이지만 검색)에 활용됩니다.

### 2. `PyPDFLoader` — PDF 로드하기
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("./data/SPRI_AI_Brief_2023년12월호_F.pdf")
docs = loader.load()
```
- 내부적으로 `pypdf` 라이브러리를 사용하며, **PDF의 각 페이지가 하나의 `Document`** 로 변환됩니다. (실습 문서는 23페이지 → `len(docs) == 23`)
- 자동으로 채워지는 `metadata` 예시:

| 키 | 의미 |
|---|---|
| `source` | 파일 경로 |
| `page` | 페이지 번호 (0부터 시작) |
| `page_label` | 실제 표기 페이지 번호 (1부터 시작) |
| `total_pages` | 전체 페이지 수 |
| `producer`, `creator`, `author`, `creationdate` 등 | PDF 파일 자체의 속성 정보 |

- `docs[1]`은 **두 번째 페이지**(인덱스 1)이며, `metadata['page'] == 1`, `page_label == '2'`로 0-based/1-based 차이를 확인할 수 있습니다.

### 3. `load_and_split()` — 로드 + 청크 분할
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)
split_docs = loader.load_and_split(text_splitter=text_splitter)
```
- 페이지 단위 문서를 **지정한 크기(청크)로 더 잘게 분할**합니다. 23페이지 문서가 `chunk_size=200`으로 **173개 청크**로 나뉩니다.
- 분할된 각 청크도 원본 페이지의 `metadata`를 그대로 물려받으므로, 어느 페이지에서 나온 조각인지 추적할 수 있습니다.
- 분할을 하는 이유: LLM 컨텍스트 길이 제한, 그리고 임베딩/검색 시 **작고 의미가 집중된 단위**로 검색해야 정확도가 높아지기 때문입니다. (자세한 내용은 ch09_06 텍스트 스플리터에서 다룸)

### 4. `chunk_size`와 `chunk_overlap`
- **`chunk_size`**: 한 청크의 최대 글자 수
- **`chunk_overlap`**: 인접한 청크끼리 **겹치게 할 글자 수**

| 설정 | 동작 | 장점 | 단점 |
|---|---|---|---|
| `chunk_size=200, chunk_overlap=50` | 0~200, 150~350, 300~500 … 처럼 겹쳐서 자름 | 경계에 걸친 문장의 문맥 보존 | 청크 수/저장공간/토큰 증가 |
| `chunk_size=200, chunk_overlap=0` | 겹침 없이 최대 200자 단위로 자름 | 토큰·저장공간 절약, 처리 속도 빠름 | **경계선에서 문맥 단절** |

- 예시: `"이 제품의 보증 기간은 구매일로부터"` / `"2년입니다."`처럼 핵심 문장이 두 청크로 갈라지면, 검색 정확도(Precision/Recall)가 떨어지고 **RAG 답변 품질이 크게 저하**될 수 있습니다. 이를 막기 위해 보통 소량의 overlap을 둡니다.

### 5. 지연 로딩 — `lazy_load()`
```python
for doc in loader.lazy_load():
    print(doc.metadata)
```
- `load()`는 모든 페이지를 **한꺼번에 메모리에 올리지만**, `lazy_load()`는 **제너레이터**로 동작해 필요할 때 **하나씩** 읽어옵니다.
- 대용량 문서/수많은 파일을 처리할 때 **메모리 사용량을 크게 줄일 수 있습니다.**

### 6. 비동기 로딩 — `aload()`
```python
adocs = loader.aload()   # 코루틴(coroutine) 객체만 반환, 아직 실행 X
await adocs              # 실행 및 완료까지 대기
```
- `aload()`는 비동기 로딩 메서드로, 호출만 하면 **실제 로딩이 아니라 코루틴 객체**가 반환됩니다.
- `await`를 붙여야 실제로 실행되고 결과(`Document` 리스트)를 얻습니다. (Jupyter 노트북에서는 셀 최상단에서 바로 `await` 사용 가능)
- 다수의 파일/URL을 동시에 처리해야 할 때 I/O 대기 시간을 줄일 수 있어 유용합니다.

## 로딩 메서드 비교

| 메서드 | 반환 | 특징 |
|---|---|---|
| `load()` | `list[Document]` | 전체를 한 번에 메모리에 로드 (가장 단순) |
| `load_and_split(splitter)` | `list[Document]` | 로드 후 스플리터로 청크 분할까지 수행 |
| `lazy_load()` | `Iterator[Document]` | 하나씩 읽어 메모리 절약 |
| `aload()` | coroutine → `list[Document]` | 비동기 실행 (`await` 필요) |

## 코드 흐름 요약
1. `.env` 로드 및 필요 패키지(`langchain-core`, `langchain-community`, `pypdf`) 확인
2. `Document` 객체를 직접 생성하고 `metadata`를 자유롭게 추가해 구조 확인
3. `PyPDFLoader.load()`로 PDF 23페이지 → `Document` 23개 로드, 특정 페이지의 내용과 메타데이터 확인
4. `RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)`와 `load_and_split()`으로 173개 청크 생성
5. `chunk_overlap`의 개념과 트레이드오프 정리
6. `lazy_load()`로 페이지를 순차 처리, `aload()` + `await`로 비동기 로딩 실습

## 알아두면 좋은 점
- Document Loader의 종류(PDF, CSV, HWP, 웹 등)가 달라도 **결과물은 모두 `Document` 객체**이므로, 이후 RAG 파이프라인 코드는 재사용할 수 있습니다. (이후 ch09_02~05에서 각 로더를 다룸)
- PDF 로더가 페이지 단위로만 분할하기 때문에, 한 페이지가 너무 길거나 페이지를 가로지르는 문맥이 있으면 별도의 텍스트 스플리터로 재분할하는 것이 일반적입니다.
- `metadata`를 잘 관리하면 RAG 답변에 **출처/페이지 번호를 함께 제시**하는 등 신뢰도 높은 서비스를 만들 수 있습니다.
