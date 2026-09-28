# ex0923 - Retriever 실습

LangChain의 다양한 Retriever 전략을 다루는 실습 모음입니다.
각 노트북마다 동일한 이름의 `_README.md`에 핵심 개념과 실습 결과가 정리되어 있습니다.

## 노트북 목록

| 노트북 | 설명 | 정리 문서 |
|--------|------|-----------|
| `ch13_01_retriever.ipynb` | 기본 Retriever 사용법 | `ch13_01_retriever_README.md` |
| `ch13_02_ensemble_retriever.ipynb` | 여러 Retriever를 결합하는 EnsembleRetriever | `ch13_02_ensemble_retriever_README.md` |
| `ch13_03_long_context_reorder.ipynb` | 긴 컨텍스트에서 검색 결과 재정렬(Long Context Reorder) | `ch13_03_long_context_reorder_README.md` |
| `ch13_04_parent_document_retriever.ipynb` | 부모-자식 문서 단위로 검색하는 ParentDocumentRetriever | `ch13_04_parent_document_retriever_README.md` |

## 폴더 구조

```
.
├── data/            # 실습용 텍스트/문서 데이터
├── src/ex0923/      # 패키지 소스
├── pyproject.toml   # uv 프로젝트 설정
└── ch13_*           # 실습 노트북 + 노트북별 README
```

## 실행 방법

```bash
uv sync
```

`.env` 파일에 필요한 API 키를 설정한 뒤 노트북을 순서대로 실행합니다.
