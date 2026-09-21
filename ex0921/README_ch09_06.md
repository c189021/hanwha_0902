# ch09_06_text_splitter.ipynb — 텍스트 분할(Text Splitter)

## 개요
로더로 불러온 문서는 보통 길이가 길어 그대로 LLM에 넣거나 임베딩하기 어렵습니다. **텍스트 스플리터(Text Splitter)** 는 긴 문서를 검색·임베딩에 적합한 **청크(chunk)** 단위로 나누는 도구입니다. 청크를 어떻게 나누느냐가 RAG 검색 품질을 크게 좌우합니다.

이 노트북에서는 `appendix-keywords.txt`(NLP 용어 사전 텍스트)를 대상으로 **4가지 분할 방식**을 비교합니다.

1. 문자 단위 분할 — `CharacterTextSplitter`, `RecursiveCharacterTextSplitter`
2. 토큰 단위 분할 — `KonlpyTextSplitter`(한국어 형태소), `from_huggingface_tokenizer`(HF 토크나이저)
3. 의미 단위 분할 — `SemanticChunker`(임베딩 유사도 기반)

## 핵심 개념

### 1. 왜 분할이 필요한가?
- LLM/임베딩 모델의 **입력 길이(컨텍스트) 제한**을 넘지 않기 위해
- 검색 시 **작고 의미가 집중된 단위**로 찾아야 관련성이 높고, LLM에 전달되는 토큰(비용)도 줄기 때문에
- 핵심 파라미터: `chunk_size`(청크 최대 크기), `chunk_overlap`(청크 간 겹침, 경계 문맥 보존용 — [ch09_01](README_ch09_01.md) 참고), `length_function`(크기를 재는 함수, 기본 `len`)

### 2. `CharacterTextSplitter` — 단일 구분자 기반 분할
```python
from langchain_text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=210,
    chunk_overlap=0,
    length_function=len,
)
texts = text_splitter.create_documents([file])
```
- 지정한 **하나의 구분자(`separator`)** 로 텍스트를 먼저 나눈 뒤, `chunk_size`를 넘지 않는 범위에서 조각들을 합칩니다. 여기서는 빈 줄(`\n\n`, 문단 경계)이 구분자입니다.
- **`split_text(text)`**: 문자열 리스트(`list[str]`) 반환 / **`create_documents([text, ...])`**: `Document` 리스트 반환 (`metadata` 포함 가능)
- 주의: 구분자로 나눈 한 조각 자체가 `chunk_size`보다 크면 **더 쪼개지 못하고 그대로 초과**한 채 반환될 수 있습니다. (실제로 아래 토큰 분할 예제에서 "Created a chunk of size 358, which is longer than the specified 300" 경고가 다수 발생)

### 3. `create_documents()`와 `metadatas` — 문서별 메타데이터 부여
```python
metadatas = [{"document": 1}, {"document": 2}]
documents = text_splitter.create_documents([file, file], metadatas=metadatas)

len(documents)          # 64  (32개 청크 x 2문서)
documents[0].metadata   # {'document': 1}
documents[32].metadata  # {'document': 2}
```
- 원문 리스트와 **같은 길이의 `metadatas` 리스트**를 넘기면, 각 원문에서 나온 모든 청크에 해당 메타데이터가 붙습니다.
- 동일한 원문 2개를 넣어 "원문 1 → 32청크, 원문 2 → 32청크 = 총 64개"이고, 청크 0~31은 `document: 1`, 32~63은 `document: 2`임을 확인하는 실습입니다. 여러 문서를 한꺼번에 분할할 때 **출처를 구분**하는 데 유용합니다.

### 4. `RecursiveCharacterTextSplitter` — 재귀적 분할 (가장 권장되는 기본 스플리터)
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=250,
    chunk_overlap=50,
    length_function=len,
    is_separator_regex=False,
)
```
- 여러 구분자를 **우선순위대로**(기본: `"\n\n"` → `"\n"` → `" "` → `""`) 시도하며, 큰 단위(문단)로 나누다가 청크가 너무 크면 더 작은 단위(줄 → 단어 → 글자)로 **재귀적으로** 다시 나눕니다.
- 그래서 가능한 한 **문단/문장 경계를 유지**하면서도 `chunk_size`를 넘지 않도록 보장해 줍니다. (`CharacterTextSplitter`의 크기 초과 문제 해결)
- `chunk_overlap=50` 덕분에 결과에서 청크 0의 끝 `"Embedding"`이 청크 1의 시작에 다시 등장하는 **겹침**을 볼 수 있습니다.
- `is_separator_regex`: 구분자를 정규식으로 해석할지 여부

### 5. 토큰 단위 분할 — 글자 수 대신 "토큰" 기준으로 나누기
LLM은 글자가 아니라 **토큰** 단위로 입력 제한/과금을 하므로, 토큰 기준으로 분할하면 실제 모델 제한에 더 정확히 맞출 수 있습니다.

**(1) `KonlpyTextSplitter` — 한국어 문장/형태소 기반**
```python
from langchain_text_splitters import KonlpyTextSplitter
text_splitter = KonlpyTextSplitter(chunk_size=200, chunk_overlap=50)
texts = text_splitter.split_text(file)
```
- 한국어 형태소 분석기(KoNLPy, 내부적으로 Kkma)로 **한국어 문장 경계**를 인식해 나눕니다. `konlpy` 설치가 필요합니다(Java 필요).
- 결과에서 `" 태양계 행성"`처럼 따옴표 뒤에 공백이 붙는 등 형태소 분석 과정의 흔적이 남을 수 있습니다.

**(2) Hugging Face 토크나이저 기반 `CharacterTextSplitter`**
```python
from transformers import GPT2TokenizerFast
hf_tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

text_splitter = CharacterTextSplitter.from_huggingface_tokenizer(
    hf_tokenizer, chunk_size=300, chunk_overlap=50
)
```
- `length_function`을 **토크나이저의 토큰 수 계산**으로 바꿔서, `chunk_size=300`이 "300글자"가 아니라 "**300토큰**"을 의미하게 합니다.
- 여기서도 구분자 단위(기본 `\n\n`)로 먼저 나눈 조각이 300토큰을 넘으면 그대로 남아 **"Created a chunk of size 358, which is longer than the specified 300"** 경고가 뜹니다. 엄격한 크기 제한이 필요하면 `RecursiveCharacterTextSplitter.from_huggingface_tokenizer(...)`나 `TokenTextSplitter` 사용을 고려합니다.
- 참고: GPT-2 토크나이저는 영어 중심이라 **한국어는 글자 대비 토큰 수가 훨씬 많게** 계산됩니다. OpenAI 모델 기준이라면 `tiktoken` 기반 분할이 더 정확합니다.

### 6. `SemanticChunker` — 의미 단위 분할 (임베딩 기반)
```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

text_splitter = SemanticChunker(OpenAIEmbeddings())
chunks = text_splitter.split_text(file)
```
- 글자 수가 아니라 **문장 간 의미 유사도**로 분할 지점을 정합니다.
  1. 텍스트를 문장 단위로 나누고 각 문장을 **임베딩**
  2. **인접한 문장 임베딩 간 거리**(의미 차이)를 계산
  3. 그 거리가 **임계값을 넘는 지점**(주제가 바뀌는 곳)을 분할 경계로 삼음
- 주제별로 자연스럽게 묶이는 장점이 있지만, 임베딩 API 호출이 필요해 **비용/시간이 추가**되고 청크 크기가 일정하지 않을 수 있습니다.
- 기본 설정에서는 청크 하나가 매우 크게 나와, 결과 `chunks[0]`이 `Semantic Search`부터 `Word2Vec`까지 사실상 **문서 전체**에 가깝게 반환되었습니다. (임계값이 높아 분할점이 거의 안 잡힌 경우)

**임계값 방식 조정 — `breakpoint_threshold_type`**

| 방식 | 설정 예시 | 의미 |
|---|---|---|
| `percentile` (기본) | `breakpoint_threshold_amount=70` | 문장 간 거리 분포의 **상위 (100-70)% 지점**을 경계로 삼음 → 값이 **낮을수록** 더 잘게 분할 |
| `standard_deviation` | `breakpoint_threshold_amount=1.25` | 거리의 **평균 + 1.25 x 표준편차**를 넘으면 경계 → 값이 **낮을수록** 더 잘게 분할 |

- 실습 결과: `percentile=70` → **27개** 청크, `standard_deviation=1.25` → **14개** 청크. 같은 문서도 기준에 따라 청크 개수와 크기가 크게 달라집니다.
- `interquartile`, `gradient` 같은 다른 방식도 지원합니다.
- `langchain_experimental` 패키지에 포함된 **실험적(experimental) 기능**입니다.

## 분할 방식 비교

| 스플리터 | 분할 기준 | 특징 |
|---|---|---|
| `CharacterTextSplitter` | 단일 구분자 + 글자 수 | 단순·빠름, 청크가 `chunk_size`를 초과할 수 있음 |
| `RecursiveCharacterTextSplitter` | 여러 구분자를 재귀적으로 | 문단/문장 경계 유지, **일반적으로 가장 권장** |
| `KonlpyTextSplitter` | 한국어 형태소/문장 | 한국어 문장 경계 인식, KoNLPy(Java) 필요 |
| `from_huggingface_tokenizer` | 토크나이저 토큰 수 | 실제 모델 토큰 기준 크기 제어 |
| `SemanticChunker` | 문장 임베딩 유사도 | 주제 단위 분할, 임베딩 비용 발생 |

## 코드 흐름 요약
1. `appendix-keywords.txt` 로드 후 내용 확인
2. `CharacterTextSplitter`(`\n\n`, size=210, overlap=0)로 분할, `create_documents` + `metadatas`로 문서별 메타데이터 부여 (2개 문서 → 64청크)
3. `RecursiveCharacterTextSplitter`(size=250, overlap=50)로 분할하고 겹침 확인
4. `KonlpyTextSplitter`로 한국어 문장 단위 분할
5. GPT-2 토크나이저 기반 분할 — 토큰 수 기준이며 크기 초과 경고 확인
6. `SemanticChunker`로 의미 단위 분할, 기본값 / `percentile=70`(27개) / `standard_deviation=1.25`(14개) 비교

## 알아두면 좋은 점
- **어떤 스플리터를 쓸지**: 특별한 이유가 없으면 `RecursiveCharacterTextSplitter`부터 시작하는 것이 안전합니다. 주제 경계가 중요한 문서(논문, 사전 등)나 품질이 최우선이면 `SemanticChunker`를 검토합니다.
- **청크 크기 선택은 트레이드오프**: 너무 작으면 문맥이 끊겨 검색 정확도가 떨어지고, 너무 크면 관련 없는 내용이 섞여 검색 정밀도와 토큰 비용이 나빠집니다. 문서 특성에 맞춰 `chunk_size`/`chunk_overlap`을 실험적으로 조정해야 합니다.
- 분할 결과는 항상 **눈으로 확인**하고, 이후 단계(임베딩 → 벡터스토어 저장 → 검색)로 이어집니다.
- `KonlpyTextSplitter` 셀의 `import chunk`는 실제로 쓰이지 않는 불필요한 import이며, Python 3.13에서 제거 예정이라는 경고가 뜹니다. 삭제해도 무방합니다.
