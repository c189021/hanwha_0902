# proj_fastapi — 백엔드(API 서버)

09/10 실습. **Streamlit(프론트) ↔ FastAPI(백엔드)** 를 각각 다른 서버로 띄우고 HTTP로 연동합니다.
이 폴더는 그중 **백엔드** 담당입니다.

```
Streamlit(proj_streamlit)  ──HTTP 요청──▶  FastAPI(proj_fastapi, 이 폴더)
                           ◀──JSON 응답──
```

- **Streamlit**: 화면(입력 폼/채팅창)을 그리고, 입력값을 이 서버로 전송
- **FastAPI**: 전달받은 데이터를 처리(로직/AI 추론)하고 결과를 JSON으로 반환
- 계산·판단 로직은 전부 이쪽에 있습니다. (역할 분리)

---

## 파일 2개 — 예제가 둘입니다

| 파일 | 앱 | 짝이 되는 프론트 | 엔드포인트 |
|---|---|---|---|
| [`main.py`](main.py) | 이름·나이 입력 → 성인 판별 | `proj_streamlit/app.py` | `POST /predict` |
| [`chat.py`](chat.py) | 메시지 → 규칙 기반 챗봇 답변 | `proj_streamlit/chat_app.py` | `POST /chat` |

둘 다 포트 `8000` 을 쓰므로 **한 번에 하나만** 실행합니다.

---

## 1. 핵심 개념

### 1-1. `FastAPI()` 앱 객체

```python
from fastapi import FastAPI
app = FastAPI()
```

`uvicorn main:app` 은 "`main.py` 안의 `app` 객체를 실행하라"는 뜻입니다.

### 1-2. 요청 본문 검증 — Pydantic `BaseModel`

클라이언트(Streamlit)가 보내는 JSON의 **모양을 클래스로 선언**합니다.

```python
from pydantic import BaseModel

class UserInput(BaseModel):
    name: str   # 문자열 필수
    age: int    # 정수 필수
```

- 타입이 안 맞거나 필드가 빠지면 FastAPI가 **자동으로 `422` 에러** 응답 (함수 안 들어옴)
- `chat.py` 는 `Message(text: str)` 하나만 받습니다.

### 1-3. 엔드포인트 = 데코레이터 + 함수

```python
@app.get("/")            # GET  http://127.0.0.1:8000/
def read_root():
    return {"message": "정상 동작 중"}

@app.post("/predict")    # POST http://127.0.0.1:8000/predict
def process_data(data: UserInput):   # ← 본문이 UserInput 으로 자동 파싱·검증
    ...
    return {"status": "success", "result_message": message, "is_adult": is_adult}
```

- `GET /` : 서버가 살아있는지 확인용(헬스 체크)
- `POST /predict`, `POST /chat` : 실제 데이터를 처리하는 곳
- `dict` 를 `return` 하면 FastAPI가 **JSON으로 직렬화**해서 응답

### 1-4. 처리 로직 (지금은 예시)

`main.py` — 삼항 연산자로 성인 여부 판별:
```python
is_adult = data.age >= 19
message = f"안녕하세요 {data.name}님! " + ("성인입니다." if is_adult else "미성년자입니다.")
```

`chat.py` — `if / elif / else` + `in` 으로 규칙 기반 답변:
```python
if "안녕" in user_text:
    reply = "안녕하세요! 반가워요."
elif "날씨" in user_text:
    reply = "날씨는 저도 잘 몰라요."
else:
    reply = f'"{user_text}" 라고 하셨네요. 아직 잘 이해하지 못했어요.'
```
> 나중에 이 자리에 진짜 AI 모델을 넣으면 됩니다.

---

## 2. 설치 및 실행

```cmd
:: 1. 폴더 이동
cd ex0910\proj_fastapi

:: 2. 가상환경 생성 & 활성화
python -m venv .venv
.venv\Scripts\activate.bat
:: PowerShell 이면  .venv\Scripts\Activate.ps1

:: 3. 패키지 설치
pip install "fastapi[standard]" uvicorn pydantic

:: 4. 서버 실행 (둘 중 하나만)
uvicorn main:app --reload      :: 이름/나이 예제
uvicorn chat:app --reload      :: 챗봇 예제
```

- 기본 주소: <http://127.0.0.1:8000>
- 자동 생성 API 문서(Swagger UI): <http://127.0.0.1:8000/docs> — 여기서 직접 호출해 볼 수 있습니다.
- `--reload` : 코드를 저장하면 서버가 자동 재시작

### 연동 순서 (중요)

1. **먼저** 이 폴더에서 FastAPI 서버를 켠다.
2. **그다음** `proj_streamlit` 에서 Streamlit 앱을 켠다.
3. 백엔드가 꺼져 있으면 프론트에서 `ConnectionError` 메시지가 뜬다.

---

## 3. 직접 호출해 보기 (curl)

```bash
# 헬스 체크
curl http://127.0.0.1:8000/

# main.py — 성인 판별
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"name": "홍길동", "age": 20}'
# -> {"status":"success","result_message":"안녕하세요 홍길동님! 성인입니다.","is_adult":true}

# 검증 실패 (age 를 문자열로) -> 422
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"name": "홍길동", "age": "스무살"}'

# chat.py — 챗봇 (chat:app 으로 실행했을 때)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "안녕"}'
# -> {"reply":"안녕하세요! 반가워요."}
```
