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

> `ex_git_0904`는 원래 Git 실습을 위해 별도 레포지토리로 만들었던 폴더라 이름에 `git`이 붙어 있습니다. 지금은 이 레포로 합쳐서 관리합니다.

---

## 공통 환경

- **Python 3.12**
- **에디터**: VSCode
- 폴더마다 **가상환경을 따로** 생성해서 사용합니다. (`.firstvenv`, `.secondvenv`, `.thirdenv` …)
- 가상환경 폴더와 `__pycache__`, `*.pyc` 등은 `.gitignore`에 등록되어 **커밋되지 않습니다.** 코드를 받은 뒤 각자 로컬에서 가상환경을 새로 만들어 패키지를 설치하세요.

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
