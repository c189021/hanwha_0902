# FastAPI CRUD API 만들기 (REST · Pydantic 검증)

09/09 실습. `ex0908`에서 배운 FastAPI 기초(경로/쿼리 매개변수, 요청 본문)를 이어서,
**하나의 리소스(`items`)에 대한 CRUD REST API**를 처음부터 끝까지 만들어 봅니다.

- 실습 코드: [`main.py`](main.py)
- 메모리(파이썬 `dict`)를 임시 DB로 사용합니다. 서버를 끄면 데이터는 사라집니다.

---

## 1. 이번 실습에서 다루는 개념

### 1-1. REST / CRUD

**REST**는 "자원(리소스)을 URL로 표현하고, 그 자원에 대한 행위는 HTTP 메서드로 표현한다"는 API 설계 방식입니다.

**CRUD**는 데이터가 살아있는 동안 하는 4가지 기본 동작이고, 각각 HTTP 메서드와 짝이 맞습니다.

| 동작 | 뜻 | HTTP 메서드 | 이번 코드의 경로 |
|---|---|---|---|
| **C**reate | 생성 | `POST` | `POST /items/` |
| **R**ead | 조회 | `GET` | `GET /items/` (전체), `GET /items/{item_id}` (단일) |
| **U**pdate | 수정 | `PUT` | `PUT /items/{item_id}` |
| **D**elete | 삭제 | `DELETE` | `DELETE /items/{item_id}` |

> 같은 `/items/` 경로라도 메서드에 따라 다른 함수가 실행됩니다. 이게 REST의 핵심입니다.

### 1-2. 경로 매개변수 (Path Parameter)

`GET /items/{item_id}` 처럼 URL 경로에 들어가는 값입니다.
함수 인자에 `item_id: int` 로 타입을 선언하면 FastAPI가 문자열을 `int`로 변환·검증해 줍니다.
(`/items/abc` 처럼 숫자가 아니면 자동으로 `422` 에러)

### 1-3. 요청 본문 (Request Body) + Pydantic

`POST`, `PUT` 처럼 **데이터를 보내는** 요청은 JSON 본문을 함께 보냅니다.
이 JSON을 그대로 받지 않고 **Pydantic 모델(`BaseModel`)로 받아서 검증**합니다.

```python
class ItemSchema(BaseModel):
    name: str
    price: float
    description: str | None = None
```

- `name` 은 반드시 있어야 하고 문자열이어야 함
- `price` 는 반드시 있어야 하고 숫자(float)여야 함 → `"price": "비싸요"` 같이 보내면 `422`
- `description` 은 없어도 되고(`None` 허용), 있으면 문자열
- 검증을 통과한 데이터는 `item.model_dump()` 로 `dict`로 바꿔서 저장

### 1-4. 상태 코드 & 예외 처리 (`HTTPException`)

- `POST` 성공 시 `status_code=201` (Created) 을 명시
- 없는 `item_id` 를 조회/수정/삭제하면 `raise HTTPException(status_code=404, detail="...")`
- `422` 는 Pydantic 검증 실패 시 FastAPI가 **자동으로** 내려주는 코드 (우리가 안 짜도 됨)

### 1-5. 메모리 DB 패턴

```python
items_db: dict[int, dict] = {}   # {id: item}
id_counter = 1                    # 다음에 부여할 id
```

실제 DB 대신 `dict`를 씁니다. `global id_counter` 로 생성 때마다 1씩 증가시켜 id를 부여합니다.

---

## 2. PUT 요청은 반드시 Pydantic으로 검증

이번 실습의 핵심 규칙입니다.

> **`PUT /items/{item_id}` 로 들어오는 수정 데이터도 `POST`와 똑같이 `ItemSchema`(Pydantic 모델)로 받아서 검증한다.**

이유:

- 수정이라고 검증을 건너뛰면, 잘못된 타입/누락된 필드가 그대로 DB에 덮어씌워짐
- `PUT`은 "그 자원을 통째로 교체"하는 의미라서, 생성과 동일하게 **모든 필드가 갖춰졌는지** 확인해야 함
- 같은 `ItemSchema` 를 재사용하면 검증 규칙이 한 곳에 모여 유지보수가 쉬움

```python
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: ItemSchema):   # ← item: ItemSchema 로 검증
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")

    updated_data = item.model_dump()
    updated_data["id"] = item_id       # 경로의 id로 고정 (본문의 id는 신뢰하지 않음)
    items_db[item_id] = updated_data
    return {"message": "수정 완료", "data": updated_data}
```

- 본문에 `price` 를 빼먹거나 문자열로 보내면 → FastAPI가 `422` 로 거부 (함수 안 들어옴)
- `id` 는 본문 값이 아니라 **경로 매개변수 `item_id`** 로 강제 지정

---

## 3. 설치 및 실행

### 3-1. 가상환경 생성 & 활성화

```cmd
:: 1. 폴더 이동
cd ex0909

:: 2. 가상환경 생성
python -m venv .crudvenv

:: 3. 활성화 (Windows cmd)
.crudvenv\Scripts\activate.bat
:: PowerShell 이면
.crudvenv\Scripts\Activate.ps1
```

### 3-2. 패키지 설치

```cmd
pip install "fastapi[standard]"
pip install pydantic
```

- `fastapi[standard]` 를 설치하면 Pydantic도 함께 깔리지만,
  **요청 검증에 Pydantic을 직접 쓰므로 명시적으로 `pip install pydantic` 도 실행**합니다.
- 버전 확인: `pip show pydantic` (FastAPI는 Pydantic v2 기준)

### 3-3. 서버 실행

```cmd
fastapi dev main.py
:: 또는
uvicorn main:app --reload
```

브라우저에서 <http://127.0.0.1:8000/docs> (Swagger UI) 를 열어 직접 호출해 봅니다.

---

## 4. 엔드포인트 요약

| 메서드 · 경로 | 함수 | 하는 일 | 실패 케이스 |
|---|---|---|---|
| `POST /items/` | `create_item` | 새 아이템 생성, id 자동 부여, `201` 반환 | 본문 검증 실패 시 `422` |
| `GET /items/` | `get_all_items` | 전체 목록 조회 | - |
| `GET /items/{item_id}` | `get_item` | 단일 조회 | 없는 id → `404` |
| `PUT /items/{item_id}` | `update_item` | **Pydantic 검증 후** 통째로 수정 | 없는 id → `404`, 본문 검증 실패 → `422` |
| `DELETE /items/{item_id}` | `delete_item` | 삭제하고 삭제된 데이터 반환 | 없는 id → `404` |

---

## 5. 테스트 예시 (Swagger UI 또는 curl)

```bash
# 생성
curl -X POST http://127.0.0.1:8000/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "커피", "price": 4500, "description": "아메리카노"}'

# 전체 조회
curl http://127.0.0.1:8000/items/

# 단일 조회
curl http://127.0.0.1:8000/items/1

# 수정 (PUT — 모든 필드 필요, Pydantic 검증)
curl -X PUT http://127.0.0.1:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "라떼", "price": 5000}'

# 검증 실패 예시 (price 누락) → 422
curl -X PUT http://127.0.0.1:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "라떼"}'

# 삭제
curl -X DELETE http://127.0.0.1:8000/items/1
```
