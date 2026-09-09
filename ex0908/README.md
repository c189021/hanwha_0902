# FastAPI 시작하기 (설치 · 서버 실행 · 핵심 개념)

09/08 실습. FastAPI 공식 문서(<https://fastapi.tiangolo.com/ko/>, <https://fastapi.tiangolo.com/ko/learn/>)를 따라
**설치 → 서버 실행 → 경로/쿼리 매개변수 → 요청 본문**까지 정리했습니다.

- 실습 코드: [`main.py`](main.py)
- `ex0908_2`는 이어지는 실습용 작업 폴더입니다. (현재 비어 있음)

---

## 1. FastAPI 개념

### FastAPI란?

Python의 **타입 힌트**를 기반으로 API 서버를 빠르게 만들 수 있는 웹 프레임워크입니다.
내부적으로 요청/응답 처리는 **Starlette**(ASGI 웹 툴킷)가, 데이터 검증/직렬화는 **Pydantic**이 담당합니다.
(즉 `ex0907`에서 배운 Pydantic이 FastAPI의 요청·응답 검증에 그대로 쓰입니다.)

### 왜 쓰는가?

- **빠른 개발 속도**: 함수에 타입만 선언하면 파싱·검증·문서화가 자동으로 됨
- **자동 대화형 문서**: 코드만 짜면 Swagger UI(`/docs`), ReDoc(`/redoc`)이 자동 생성됨
- **타입 기반 검증**: 잘못된 요청은 프레임워크가 자동으로 `422` 에러로 걸러줌 (Pydantic)
- **높은 성능**: ASGI + async 기반이라 동시 요청 처리에 유리함
- **에디터 자동완성**: 타입 힌트 덕분에 IDE 자동완성/타입 체크가 잘 됨

---

## 2. 설치 및 서버 실행

### 2-1. 가상환경 생성 & 활성화

폴더마다 가상환경을 따로 만듭니다. (이 폴더는 `.fastvenv` 사용)

```cmd
:: 1. 해당 폴더로 이동
cd ex0908

:: 2. 가상환경 생성
python -m venv .fastvenv

:: 3. 가상환경 활성화 (Windows cmd)
.fastvenv\Scripts\activate.bat
:: PowerShell 이면
.fastvenv\Scripts\Activate.ps1
```

> 가상환경이 켜지면 프롬프트 앞에 `(.fastvenv)` 가 붙습니다.
> 가상환경 폴더(`.fastvenv`, `.fast2venv`)와 `__pycache__`, `.vscode/` 는 `.gitignore`에 등록되어 커밋되지 않습니다.

### 2-2. 패키지 설치

```cmd
pip install "fastapi[standard]"
```

- `fastapi[standard]` 는 FastAPI 본체 + 실무에 필요한 표준 패키지 묶음을 함께 설치합니다.
  - `uvicorn` (ASGI 서버), `fastapi-cli`(`fastapi` 명령어), `python-multipart`(폼/파일 업로드),
    `email-validator`(`EmailStr`), `jinja2`, `httpx` 등
- 따옴표(`"..."`)는 셸이 `[standard]` 의 대괄호를 다르게 해석하지 않게 하려고 씁니다. (특히 zsh/PowerShell)

설치가 끝나면 아래처럼 **pip 업그레이드 안내**가 뜨는데, 같이 실행해 줍니다.

```cmd
python -m pip install --upgrade pip
```

설치 확인:

```cmd
python -c "import fastapi; print(fastapi.__version__)"
```

### 2-3. 서버 실행

`app = FastAPI()` 인스턴스가 있는 파일이 `main.py` 라고 가정합니다.

**실행 명령어 - one (권장)**

```cmd
fastapi dev main.py
```

**실행 명령어 - two**

```cmd
uvicorn main:app --reload
```

접속: <http://127.0.0.1:8000> (또는 <http://localhost:8000>)

### 2-4. 옵션 설명 (`uvicorn main:app` 기준)

| 항목 | 의미 |
|---|---|
| `main` | 파일명 (`main.py` 에서 `.py` 제외) |
| `app` | 코드 안의 FastAPI 인스턴스 변수명 (`app = FastAPI()`) |
| `--reload` | 코드가 수정될 때마다 서버를 자동 재시작 (개발용) |
| `--host 0.0.0.0` | 외부(다른 기기)에서 접속 허용 (기본값 `127.0.0.1` 은 내 PC만) |
| `--port 8000` | 포트 번호 변경 (기본값 `8000`) |

예) 외부 접속 + 포트 변경:

```cmd
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### 2-5. `fastapi dev` vs `uvicorn main:app`

| | `fastapi dev main.py` | `uvicorn main:app` |
|---|---|---|
| `--reload` | **자동으로 켜짐** | `--reload` 를 직접 붙여야 함 |
| `app` 변수 지정 | 파일에서 자동 탐색 | `main:app` 처럼 명시 |
| 성격 | 개발용 (`fastapi run` 은 배포용, reload 없음) | 범용 ASGI 서버 실행기 |

### 2-6. "reload 는 스스로 안 함?"

- **`fastapi dev`** 는 개발용이라 **reload 가 기본으로 켜져 있습니다.** (그래서 아무것도 안 붙여도 저장하면 재시작됨)
- **`uvicorn main:app`** 는 범용 실행기라 **기본값이 reload OFF** 입니다. 개발 중이면 `--reload` 를 직접 붙여야 합니다.
- reload 를 항상 켜두지 않는 이유:
  - 파일 변경 감시(watch)에 CPU/메모리 오버헤드가 있음
  - 재시작 중 짧게 요청이 끊길 수 있음
  - **운영(production) 환경에서는 코드가 바뀔 일이 없고 안정성이 중요**하므로 reload 를 꺼야 함
- 정리: reload 는 "개발 편의 기능"이라 개발 모드에서만 기본 ON, 그 외에는 opt-in.

---

## 3. 자동 대화형 문서 (Swagger UI / ReDoc)

서버를 켜고 주소 뒤에 경로를 붙이면 문서가 나옵니다.

| URL | 설명 |
|---|---|
| <http://127.0.0.1:8000/docs> | **Swagger UI** — 대화형 API 문서. 브라우저에서 바로 "Try it out" 으로 요청을 보내볼 수 있음 |
| <http://127.0.0.1:8000/redoc> | **ReDoc** — 읽기 좋은 정적 문서 형태 |
| <http://127.0.0.1:8000/openapi.json> | 위 문서들의 원본이 되는 OpenAPI 스키마(JSON) |

이 문서들은 **내가 선언한 타입 힌트/Pydantic 모델을 그대로 읽어서 자동 생성**됩니다. 따로 문서를 쓸 필요가 없습니다.

---

## 4. 동시성과 async / await

### 개념

- FastAPI 는 **ASGI** 기반이라 요청을 **비동기(async)** 로 처리할 수 있습니다.
- DB 조회, 외부 API 호출, 파일 읽기처럼 **"기다리는 시간"이 있는 작업(I/O bound)** 에서, 기다리는 동안
  다른 요청을 처리할 수 있어 동시 처리량이 올라갑니다.
- `await` 는 "이 작업이 끝날 때까지 기다리되, 기다리는 동안 CPU 는 다른 일 하도록 양보한다"는 의미입니다.

### 경로 함수: `def` vs `async def`

| 정의 | 언제 쓰나 | FastAPI 동작 |
|---|---|---|
| `async def` | 함수 안에서 `await ...` 를 쓰는 비동기 라이브러리를 호출할 때 | 이벤트 루프에서 그대로 실행 |
| `def` (일반 함수) | `await` 없이 동기 코드만 쓸 때 (일반 DB 드라이버, `requests` 등) | **별도 스레드풀**에서 실행해 이벤트 루프가 막히지 않게 함 |

- 둘 다 사용 가능하며, FastAPI 가 알아서 적절히 처리합니다.
- 주의: `async def` 안에서 `time.sleep()` 같은 **동기 블로킹 코드**를 쓰면 서버 전체가 멈춥니다.
  그럴 땐 `def` 로 만들거나 비동기 버전(`await asyncio.sleep()`)을 써야 합니다.
- `main.py` 에서도 어떤 함수는 `def`, 어떤 함수는 `async def` 로 섞여 있는데, 지금 단계에서는 동작 차이가 없습니다.

---

## 5. 경로 매개변수 (Path Parameters)

URL 경로의 일부를 변수로 받습니다. `{}` 안 이름과 함수 매개변수 이름이 같아야 합니다.

```python
# GET http://localhost:8000/items/555
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

- `item_id: int` 로 타입을 선언하면:
  - `/items/555` → `555` (int 로 자동 변환)
  - `/items/abc` → **422 에러** (숫자가 아니라서 검증 실패)

### 5-1. 경로 순서가 중요하다

경로는 **위에서부터 순서대로 매칭**됩니다. 고정 경로를 변수 경로보다 위에 둬야 합니다.

```python
@app.get("/users/me")          # 먼저 선언 → /users/me 는 여기서 처리
async def read_user_me():
    return {"user_id": "나는 me 입니다"}

@app.get("/users/{user_id}")   # 그 아래 → /users/무엇이든 여기서 처리
async def read_user(user_id: str):
    return {"user_id": user_id}
```

만약 `/users/{user_id}` 를 위에 두면 `/users/me` 요청이 `user_id="me"` 로 잡혀버립니다.

### 5-2. 같은 경로를 두 번 선언하면?

```python
@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]   # 이게 사용됨

@app.get("/users")
async def read_users2():
    return ["Bean", "Elfo"]    # 무시됨 (먼저 등록된 것이 우선)
```

### 5-3. 미리 정해진 값만 받기 — Enum

`str` + `Enum` 을 상속한 클래스를 타입으로 쓰면, **정해진 값만** 허용되고 `/docs` 에 선택지로 표시됩니다.

```python
from enum import Enum

class ModelName(str, Enum):
    aaa = "alexnet"
    r = "resnet"
    l = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.aaa:          # 멤버끼리 비교
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "resnet":         # 실제 문자열 값과 비교
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}
```

- `/models/alexnet`, `/models/resnet`, `/models/lenet` → OK
- `/models/xxx` → 422 에러
- `model_name` (멤버) 와 `model_name.value` (`"alexnet"` 같은 실제 값) 를 구분해서 씁니다.

---

## 6. 쿼리 매개변수 (Query Parameters)

경로에 없는 함수 매개변수는 자동으로 **쿼리 문자열**(`?key=value&...`)로 인식됩니다.

```python
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# GET http://localhost:8000/items/?skip=0&limit=10
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
```

- `skip: int = 0` 처럼 **기본값이 있으면 선택(optional)**, 없으면 필수 쿼리 파라미터가 됩니다.
- `/items/` → `skip=0, limit=10` (기본값 사용)
- `/items/?skip=1&limit=1` → `[{"item_name": "Bar"}]`
- 값은 URL 상 문자열이지만 `int` 로 선언했으므로 자동 변환됩니다.

### 선택적 파라미터 — `str | None = None`

```python
# GET http://localhost:8000/items2/test
# GET http://localhost:8000/items2/test?q=hello
@app.get("/items2/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

- `q: str | None = None` → 쿼리에 `q` 가 없어도 되고, 있으면 문자열로 받음
- `item_id` 는 경로에 있으므로 경로 매개변수, `q` 는 쿼리 매개변수로 자동 구분됨

> 참고: `main.py` 에는 `read_item` 이라는 이름의 함수가 여러 번 나오는데,
> FastAPI 는 **함수 이름이 아니라 `@app.get("경로")` 데코레이터로 라우팅**하므로 경로만 다르면 문제없이 동작합니다.

---

## 7. 요청 본문 (Request Body) — Pydantic `BaseModel`

`GET` 은 보통 쿼리로 값을 받지만, `POST`/`PUT` 등에서 **JSON 본문**으로 데이터를 받을 때는
Pydantic 모델을 타입으로 선언합니다. (`ex0907` 의 Pydantic 내용이 그대로 이어집니다.)

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None   # 선택 필드
    price: float
    tax: float | None = None

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        item_dict["price_with_tax"] = item.price + item.tax
    return item_dict
```

동작:

1. 요청 본문(JSON)을 읽어 `Item` 으로 파싱
2. 타입/필수값 검증 → 실패 시 자동 `422` 에러 (어느 필드가 왜 틀렸는지 응답에 포함)
3. 함수 안에서는 검증된 `item` 객체(`item.price` 등)로 바로 사용
4. `/docs` 에 요청 본문 스키마와 예시가 자동 표시됨

**경로 + 쿼리 + 본문 같이 받기**도 됩니다. FastAPI 가 매개변수를 보고 알아서 구분합니다.

- 경로에 이름이 있으면 → 경로 매개변수
- 타입이 Pydantic 모델이면 → 요청 본문
- 그 외 단순 타입(`int`, `str` 등)이면 → 쿼리 매개변수

```python
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result["q"] = q
    return result
```

---

## 8. `main.py` 엔드포인트 요약

| 메서드 · 경로 | 함수 | 다루는 개념 |
|---|---|---|
| `GET /` | `read_root` | 가장 기본적인 라우트, dict 반환(JSON) |
| `GET /items/{item_id}` | `read_item` | 경로 매개변수(`int` 변환) + 선택 쿼리 `q` |
| `GET /users/me` | `read_user_me` | 고정 경로를 변수 경로보다 먼저 선언 |
| `GET /users/{user_id}` | `read_user` | 문자열 경로 매개변수 |
| `GET /users` (2번) | `read_users`, `read_users2` | 같은 경로 중복 시 먼저 등록된 것이 우선 |
| `GET /models/{model_name}` | `get_model` | `str`+`Enum` 으로 허용 값 제한, 멤버 vs `.value` |
| `GET /items/` | `read_item` | 쿼리 매개변수 `skip`/`limit` + 기본값 + 리스트 슬라이싱 |
| `GET /items2/{item_id}` | `read_item` | 경로 매개변수 + 선택 쿼리 `q` 유무 분기 |

### 실행

```cmd
cd ex0908
python -m venv .fastvenv
.fastvenv\Scripts\activate.bat
pip install "fastapi[standard]"
python -m pip install --upgrade pip

fastapi dev main.py
:: 또는
uvicorn main:app --reload
```

브라우저에서 <http://127.0.0.1:8000/docs> 를 열어 각 엔드포인트를 직접 호출해 봅니다.
