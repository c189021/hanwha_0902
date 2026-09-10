# 09/10 실습 — 파이썬 문법 + FastAPI ↔ Streamlit 연동

오늘 수업은 크게 두 파트입니다.

| 폴더 | 내용 | 문서 |
|---|---|---|
| [`python_basics`](python_basics) | 딕셔너리 타입 적용 · 제어문 `if` · `lambda` · `match/case`(`case _`, 타입이 달라도 처리) · 반복문 `while` | [python_basics/README.md](python_basics/README.md) |
| [`proj_fastapi`](proj_fastapi) | **백엔드**: FastAPI 서버 (`POST /predict`, `POST /chat`) | [proj_fastapi/README.md](proj_fastapi/README.md) |
| [`proj_streamlit`](proj_streamlit) | **프론트엔드**: Streamlit 화면 → `requests` 로 FastAPI 호출 | [proj_streamlit/README.md](proj_streamlit/README.md) |

---

## 1. 파이썬 문법 (`python_basics`)

예제 파일을 순서대로 실행:

```cmd
cd ex0910\python_basics
python 01_dict_typing.py   :: dict 기본 + dict[str,int] / TypedDict 로 타입 붙이기
python 02_if.py            :: if/elif/else, falsy 값, 삼항 연산자
python 03_lambda.py        :: 한 줄 함수, sorted(key=...) / map / filter
python 04_match_case.py    :: match/case, case _ (그 외), 타입별(int/str/list/dict) 분기
python 05_while.py         :: while, break / continue / while~else
```

## 2. FastAPI ↔ Streamlit 연동 (`proj_fastapi` + `proj_streamlit`)

**서버 2개를 각각 띄워서** HTTP(JSON)로 주고받습니다. 역할을 분리하는 게 핵심입니다.

```
proj_streamlit (화면·입력, 포트 8501)  ──HTTP POST(json)──▶  proj_fastapi (로직·처리, 포트 8000)
                                       ◀──JSON 응답────────
```

- **프론트(Streamlit)**: 입력만 받고, 결과만 그린다. 판단 로직 없음.
- **백엔드(FastAPI)**: Pydantic으로 요청 검증 → 처리 → `dict` 반환(자동 JSON).

예제가 두 쌍입니다.

| 주제 | 백엔드 | 프론트 | 실행 |
|---|---|---|---|
| 이름·나이 → 성인 판별 | `proj_fastapi/main.py` (`/predict`) | `proj_streamlit/app.py` | `uvicorn main:app --reload` + `streamlit run app.py` |
| 규칙 기반 챗봇 | `proj_fastapi/chat.py` (`/chat`) | `proj_streamlit/chat_app.py` | `uvicorn chat:app --reload` + `streamlit run chat_app.py` |

### 실행 순서

1. **백엔드 먼저**: `cd ex0910\proj_fastapi` → 가상환경 활성화 → `uvicorn main:app --reload`
2. **그다음 프론트**: 새 터미널에서 `cd ex0910\proj_streamlit` → 가상환경 활성화 → `streamlit run app.py`
3. 백엔드가 꺼져 있으면 프론트에 `ConnectionError` 안내 문구가 뜬다.

> 폴더별 가상환경/패키지 설치 방법은 각 폴더의 `README.md`에 있습니다.
