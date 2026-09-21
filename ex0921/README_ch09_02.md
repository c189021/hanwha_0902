# ch09_02_pdf_loader.ipynb — PDF 로더

## 개요
PDF는 보고서, 논문, 매뉴얼 등 RAG에서 가장 흔하게 다루는 문서 형식입니다. 이 노트북에서는 `PyPDFLoader`로 PDF를 불러와 **페이지별 텍스트 내용**과 **메타데이터**를 확인하고, 메타데이터를 보기 좋게 출력하는 헬퍼 함수를 만들어 봅니다. (ch09_01에서 다룬 `Document` 구조를 실제 PDF에 적용해보는 단계입니다.)

## 핵심 개념

### 1. `PyPDFLoader` — pypdf 기반 PDF 로더
```python
from langchain_community.document_loaders import PyPDFLoader

FILE_PATH = "./data/SPRI_AI_Brief_2023년12월호_F.pdf"
loader = PyPDFLoader(FILE_PATH)
docs = loader.load()
```
- 내부적으로 **`pypdf`** 라이브러리를 사용하므로 사전에 설치가 필요합니다. (`uv add pypdf` 또는 `pip install pypdf`)
- `load()`를 호출하면 **PDF의 각 페이지가 하나의 `Document`** 가 되어 리스트로 반환됩니다. 23페이지 PDF라면 `len(docs) == 23`입니다.
- `docs[10].page_content`는 11번째 페이지의 텍스트(본문)이고, `[:300]`처럼 슬라이싱하면 앞부분만 미리보기할 수 있습니다.

### 2. 페이지 내용(`page_content`) 확인
```python
print(docs[10].page_content[:300])
```
- 결과에서 보듯 PDF의 텍스트가 **줄바꿈과 특수문자(`n`, `£` 등)** 까지 그대로 추출됩니다. PDF의 글머리 기호(●, ▹ 등)가 폰트/인코딩 문제로 다른 문자로 바뀌어 나올 수 있으며, 이는 PDF 자체의 특성이므로 필요 시 전처리 단계에서 정리합니다.
- PDF는 원래 "인쇄용 레이아웃"을 위한 포맷이라, 표/다단 레이아웃/이미지 속 글자는 텍스트 추출 품질이 떨어질 수 있습니다.

### 3. 메타데이터 확인 — `show_metadata()` 헬퍼 함수
```python
def show_metadata(docs):
    if docs:
        print("[metadata]")
        print(list(docs[0].metadata.keys()))

        print("\n[examples]")
        max_key_length = max(len(key) for key in docs[0].metadata)
        for key, value in docs[0].metadata.items():
            print(f"{key:<{max_key_length}} : {value}")
```
- 첫 번째 문서의 `metadata` 키 목록과 값을 **정렬된 형태로 출력**해주는 유틸 함수입니다.
- `f"{key:<{max_key_length}}"`는 f-string 포맷팅으로, 가장 긴 키 길이에 맞춰 **왼쪽 정렬(`<`)** 하여 콜론(`:`) 위치를 맞추는 기법입니다.
- 이후 다른 로더(HWP, CSV, 웹 등)를 다룰 때도 재사용할 수 있는 범용 함수입니다.

### 4. PyPDFLoader가 채워주는 메타데이터

| 키 | 예시 값 | 의미 |
|---|---|---|
| `producer` | Hancom PDF 1.3.0.542 | PDF를 생성한 프로그램(엔진) |
| `creator` | Hwp 2018 10.0.0.13462 | 원본 문서를 만든 응용 프로그램 |
| `creationdate` | 2023-12-08T13:28:38+09:00 | 문서 생성 일시 |
| `moddate` | 2023-12-08T13:28:38+09:00 | 문서 수정 일시 |
| `author` | dj | 작성자 |
| `pdfversion` | 1.4 | PDF 버전 |
| `source` | ./data/SPRI_AI_Brief_2023년12월호_F.pdf | 파일 경로 |
| `total_pages` | 23 | 전체 페이지 수 |
| `page` | 0 | 현재 페이지 번호 (**0부터 시작**) |
| `page_label` | 1 | PDF에 표기된 페이지 번호 (**1부터 시작**) |

- `page`와 `page_label`의 차이에 주의해야 합니다. `page`는 리스트 인덱스 개념(0-based), `page_label`은 사람이 보는 페이지 번호입니다.
- 이 메타데이터는 RAG 결과에서 **"출처: 파일명, N페이지"** 를 표시하거나 특정 페이지 범위만 필터링할 때 유용하게 쓰입니다.

## 코드 흐름 요약
1. `.env` 로드 및 `pypdf` 패키지 확인
2. `PyPDFLoader(FILE_PATH).load()`로 PDF를 페이지 단위 `Document` 리스트로 로드
3. `docs[10].page_content[:300]`로 특정 페이지 본문의 일부를 확인
4. `show_metadata()` 헬퍼 함수를 정의해 메타데이터 키/값을 정렬 출력
5. 실제 PDF에서 어떤 메타데이터가 자동으로 채워지는지 확인

## 알아두면 좋은 점
- PDF 로더는 종류가 여러 가지입니다(`PyPDFLoader`, `PyMuPDFLoader`, `PDFPlumberLoader`, `UnstructuredPDFLoader` 등). 표 추출, 이미지 OCR, 레이아웃 보존 등 **목적에 따라 성능 차이**가 있으므로, 추출 결과가 좋지 않으면 다른 로더로 교체해 보는 것이 좋습니다.
- 이 실습의 PDF는 한글(HWP)로 만든 문서를 변환한 것이라 일부 기호가 깨져 보일 수 있습니다. 본문 추출 품질을 반드시 눈으로 확인한 뒤 다음 단계(분할·임베딩)로 넘어가야 합니다.
- 로드된 페이지 문서가 아직 길기 때문에, 실제 RAG에서는 [ch09_01](README_ch09_01.md)에서 본 `RecursiveCharacterTextSplitter` 등으로 **청크 분할**을 거치는 것이 일반적입니다.
