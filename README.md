# hanwha_0902

한화 부트캠프 **AI 서비스 백엔드 프로그래밍 실무** 과정의 실습 모음 레포지토리입니다.

날짜별로 폴더를 나눠, 그날 배운 **파이썬 문법 · 라이브러리 · 개발 환경/도구 사용법**을 실습 코드와 함께 정리합니다. 각 폴더 안의 `README.md`에 그 날의 내용이 상세하게 들어 있습니다.

---

## 폴더 구성

| 폴더 | 날짜 | 주제 | 문서 |
|---|---|---|---|
| [`ex0902`](ex0902) | 09/02 | 파이썬 기본 문법 · 가상환경(venv) 세팅 · VSCode 익스텐션 가이드 | [ex0902/README.md](ex0902/README.md) |
| [`ex0903`](ex0903) | 09/03 | 파이썬 문법 · Streamlit 가이드 · Matplotlib | [ex0903/README.md](ex0903/README.md) |
| [`ex_git_0904`](ex_git_0904) | 09/04 | 파이썬 문법 · NumPy · Streamlit(Altair) · Git/GitHub 가이드 · GitHub Desktop 가이드 | [ex_git_0904/README.md](ex_git_0904/README.md) |
| [`ex0907`](ex0907) | 09/07 | Git/GitHub 가이드 · Pydantic (데이터 검증/타입 변환, 기본값·Optional·중첩 모델, API 요청 검증·변환) · NumPy (배열/연산 기초, 통계·집계, 데이터 전처리 파이프라인) · 클래스(OOP) (클래스/인스턴스 기초, 상속·다형성·캡슐화, 특수 메서드 활용) | [ex0907/README.md](ex0907/README.md) |
| [`ex0908`](ex0908) | 09/08 | FastAPI (설치·서버 실행(`fastapi dev` / `uvicorn --reload`)·Swagger UI, 동시성과 async/await, 경로 매개변수(타입·순서·Enum), 쿼리 매개변수(기본값·Optional), 요청 본문(Pydantic `BaseModel`)) | [ex0908/README.md](ex0908/README.md) |
| [`ex0909`](ex0909) | 09/09 | FastAPI CRUD REST API (REST/CRUD ↔ HTTP 메서드, 경로 매개변수, 요청 본문 Pydantic 검증(특히 `PUT`), `HTTPException`·상태 코드(201/404/422), 메모리 `dict` DB 패턴) | [ex0909/README.md](ex0909/README.md) |
| [`ex0910`](ex0910) | 09/10 | 파이썬 문법 (딕셔너리 타입 적용 `dict[str, int]`·`TypedDict`, 제어문 `if`·삼항 연산자, `lambda`, `match`/`case`(`case _`·타입별 분기), 반복문 `while`·`break`/`continue`) · **FastAPI ↔ Streamlit 연동** (백엔드/프론트 서버를 각각 띄워 HTTP(JSON)로 통신, `requests` 로 호출, `ConnectionError` 처리) | [ex0910/README.md](ex0910/README.md) |

> `ex_git_0904`는 원래 Git 실습을 위해 별도 레포지토리로 만들었던 폴더라 이름에 `git`이 붙어 있습니다. 지금은 이 레포로 합쳐서 관리합니다.

---

## 공통 환경

- **Python 3.12**
- **에디터**: VSCode
- 폴더마다 **가상환경을 따로** 생성해서 사용합니다. (`.firstvenv`, `.secondvenv`, `.thirdenv`, `.fastvenv` …)
- 가상환경 폴더와 `__pycache__`, `*.pyc`, `.vscode/` 등은 `.gitignore`에 등록되어 **커밋되지 않습니다.** 코드를 받은 뒤 각자 로컬에서 가상환경을 새로 만들어 패키지를 설치하세요.

## 실행 방법 (공통)

```cmd
:: 1. 해당 폴더로 이동
cd ex0903

:: 2. 가상환경 생성
python -m venv .secondvenv

:: 3. 가상환경 활성화
.secondvenv\Scripts\activate.bat

:: 4. 패키지 설치 (폴더별 README 참고)
pip install streamlit numpy pandas matplotlib

:: 5. 실행
python streamlit_basics.py
:: 또는 Streamlit 앱인 경우
streamlit run streamlit_basics.py
```

자세한 내용은 각 폴더의 `README.md`를 참고하세요.
