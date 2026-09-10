# proj_streamlit — 프론트엔드(화면 + 요청)

09/10 실습. **Streamlit(프론트) ↔ FastAPI(백엔드)** 연동에서 이 폴더는 **프론트엔드** 담당입니다.

```
Streamlit(proj_streamlit, 이 폴더)  ──HTTP POST──▶  FastAPI(proj_fastapi)
                                    ◀──JSON 응답──
```

- 사용자에게 **입력 폼 / 채팅창**을 보여주고
- 입력값을 `requests` 로 FastAPI 서버에 보낸 뒤
- 돌아온 JSON 응답을 화면에 표시합니다.
- **계산/판단 로직은 여기 없습니다.** 전부 백엔드(`proj_fastapi`) 쪽에 있습니다.

---

## 파일 2개

| 파일 | 앱 | 짝이 되는 백엔드 | 호출 |
|---|---|---|---|
| [`app.py`](app.py) | 이름·나이 입력 폼 → 결과 표시 | `proj_fastapi/main.py` | `POST /predict` |
| [`chat_app.py`](chat_app.py) | 챗봇 대화창 | `proj_fastapi/chat.py` | `POST /chat` |

---

## 1. 핵심 개념

### 1-1. Streamlit은 "위에서 아래로 매번 다시 실행"

화면에서 뭔가 바뀔 때마다 스크립트를 **처음부터 끝까지 다시 실행**합니다.
그래서 유지해야 할 값(대화 기록 등)은 `st.session_state` 에 저장합니다.

```python
if "messages" not in st.session_state:
    st.session_state.messages = []      # 최초 1회만 초기화
```

### 1-2. 입력 위젯

| 코드 | 역할 |
|---|---|
| `st.title(...)` | 페이지 제목 |
| `st.text_input`, `st.number_input` | 텍스트 / 숫자 입력칸 |
| `with st.form(...)` + `st.form_submit_button` | 여러 입력을 묶어 **버튼 눌렀을 때 한 번에** 제출 |
| `st.chat_input(...)` | 하단 채팅 입력창 (엔터 시 값 반환) |
| `st.chat_message("user" / "assistant")` | 말풍선 |
| `st.success` / `st.error` / `st.write` | 결과·오류 출력 |

### 1-3. FastAPI 서버로 요청 보내기 — `requests`

```python
import requests
FASTAPI_URL = "http://127.0.0.1:8000"          # uvicorn 기본 주소와 일치해야 함

payload = {"name": name, "age": age}           # 파이썬 dict
response = requests.post(f"{FASTAPI_URL}/predict", json=payload)  # dict -> JSON 본문
```

- `json=payload` 로 넘기면 파이썬 `dict` 가 JSON 본문으로 변환되어 전송됩니다.
- **보내는 키 이름**(`name`, `age`)은 백엔드 Pydantic 모델(`UserInput`)의 필드명과 같아야 합니다.

### 1-4. 응답 처리

```python
if response.status_code == 200:          # 200 = 정상
    result = response.json()             # 응답 JSON -> dict
    st.write(result["result_message"])   # 백엔드가 넣어준 키를 꺼내 표시
else:
    st.error(f"오류 (상태 코드: {response.status_code})")   # 예: 422 검증 실패
```

### 1-5. 서버가 꺼져 있을 때

```python
try:
    response = requests.post(...)
except requests.exceptions.ConnectionError:
    st.error("FastAPI 서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인하세요.")
```

`chat_app.py` 도 같은 방식으로 챗봇 답변 대신 안내 문구를 띄웁니다.

---

## 2. 설치 및 실행

```cmd
:: 1. 폴더 이동
cd ex0910\proj_streamlit

:: 2. 가상환경 생성 & 활성화
python -m venv .venv
.venv\Scripts\activate.bat
:: PowerShell 이면  .venv\Scripts\Activate.ps1

:: 3. 패키지 설치
pip install streamlit requests

:: 4. 앱 실행 (짝이 되는 백엔드를 먼저 켠 뒤)
streamlit run app.py         :: 이름/나이 예제  (백엔드: uvicorn main:app --reload)
streamlit run chat_app.py    :: 챗봇 예제       (백엔드: uvicorn chat:app --reload)
```

- 기본 주소: <http://localhost:8501>

### 연동 순서 (중요)

| 순서 | 터미널 1 (`proj_fastapi`) | 터미널 2 (`proj_streamlit`) |
|---|---|---|
| 1 | `uvicorn main:app --reload` | — |
| 2 | (실행 중 유지) | `streamlit run app.py` |

> 두 서버가 **동시에** 떠 있어야 연동됩니다. 백엔드를 먼저 켜세요.
> 챗봇 예제는 `chat:app` + `chat_app.py` 로 짝을 맞춥니다.
