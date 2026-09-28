# ex0922 - 임베딩(Embeddings) & 벡터스토어 실습

LangChain을 이용한 다양한 임베딩 모델 사용법과 벡터스토어(Pinecone) 연동을 다루는 실습 모음입니다.
각 노트북마다 동일한 이름의 `_README.md`에 핵심 개념과 실습 결과가 정리되어 있습니다.

## 노트북 목록

| 노트북 | 설명 | 정리 문서 |
|--------|------|-----------|
| `ch11_01_OpenAIEmbeddings.ipynb` | OpenAI 임베딩, 코사인 유사도, 임베딩 캐싱(CacheBackedEmbeddings) | `ch11_01_OpenAIEmbeddings_README.md` |
| `ch11_02_HuggingFace_UpstageEmbeddings.ipynb` | HuggingFace / Upstage 임베딩 모델 사용법 | `ch11_02_HuggingFace_UpstageEmbeddings_README.md` |
| `ch11_03_OllamaEmbeddings.ipynb` | 로컬 Ollama 임베딩 모델 사용법 | `ch11_03_OllamaEmbeddings_README.md` |
| `ch12_02_PineconeVectorStore.ipynb` | Pinecone 벡터스토어 생성 및 검색 | `ch12_02_PineconeVectorStore_README.md` |

## 폴더 구조

```
.
├── data/            # 실습용 텍스트/문서 데이터
├── src/ex0922/      # 패키지 소스
├── pyproject.toml   # uv 프로젝트 설정
└── ch11_*, ch12_*   # 실습 노트북 + 노트북별 README
```

## 실행 방법

```bash
uv sync
```

`.env` 파일에 필요한 API 키(OpenAI, Upstage, Pinecone 등)를 설정한 뒤 노트북을 순서대로 실행합니다.
