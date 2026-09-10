# 파이썬 문법 정리 — dict 타입 · if · lambda · match/case · while

09/10 실습 중 **파이썬 문법** 파트. 예제 파일을 순서대로 실행하며 읽으면 됩니다.

```cmd
cd ex0910\python_basics
python 01_dict_typing.py
python 02_if.py
python 03_lambda.py
python 04_match_case.py
python 05_while.py
```

> 별도 패키지가 필요 없습니다. Python 3.10 이상이면 됩니다. (`match/case` 는 3.10+)

---

## 1. 딕셔너리에 타입 적용하기 — [`01_dict_typing.py`](01_dict_typing.py)

딕셔너리(`dict`)는 **`키: 값` 쌍**을 모아둔 자료형입니다.

```python
user = {"name": "홍길동", "age": 20}
user["name"]                 # 값 꺼내기
user.get("email", "없음")    # 없는 키도 에러 없이 기본값
user["email"] = "a@b.com"    # 추가
del user["email"]            # 삭제
for k, v in user.items():    # 키-값 순회
    ...
```

### 타입 힌트 붙이기

파이썬은 타입을 강제하지 않지만, 힌트를 달면 편집기 자동완성·오타 경고를 받고, "이 dict의 모양"을 문서처럼 남길 수 있습니다.

| 방식 | 예시 | 의미 |
|---|---|---|
| `dict[키타입, 값타입]` | `scores: dict[str, int]` | 문자열 키 → 정수 값 |
| 중첩 | `dict[str, dict[str, int]]` | 값이 다시 `dict[str, int]` |
| `TypedDict` | `class Product(TypedDict): ...` | 키 이름·타입을 미리 못박음 (Pydantic 모델과 비슷) |

```python
from typing import TypedDict

class Product(TypedDict):
    name: str
    price: int
    in_stock: bool

item: Product = {"name": "커피", "price": 4500, "in_stock": True}
# item["price"] = "비싸요"  ← 편집기가 타입 경고
```

---

## 2. 제어문 if — [`02_if.py`](02_if.py)

조건의 **참/거짓**에 따라 실행 흐름을 나눕니다. 들여쓰기(공백 4칸)로 블록을 구분합니다.

```python
if score >= 90:
    grade = "A"
elif score >= 80:      # 위가 False일 때만 검사
    grade = "B"
else:
    grade = "F"
```

### falsy 값 (if에서 False로 취급)

`0` · `0.0` · `""` · `[]` · `{}` · `None`

```python
if name:            # 빈 문자열이면 False
    ...
if items:           # 리스트에 원소가 있으면 True
    ...
```

### 자주 쓰는 조건 표현

- `and` / `or` / `not`
- `"날씨" in user_text` — 포함 여부
- 삼항 연산자: `값A if 조건 else 값B`
  ```python
  label = "성인" if age >= 19 else "미성년자"
  ```
  → `proj_fastapi/main.py`, `proj_fastapi/chat.py` 에서 실제로 이 형태를 씁니다.

---

## 3. 람다 lambda — [`03_lambda.py`](03_lambda.py)

**이름 없는 한 줄 함수**. `lambda 인자: 반환식`

```python
square = lambda x: x * x        # def square(x): return x * x 와 같음
```

혼자 변수에 담아 쓰기보다는, **다른 함수의 인자로 넘길 때** 주로 씁니다.

```python
users = [{"name": "홍길동", "age": 20}, {"name": "김철수", "age": 17}]

sorted(users, key=lambda u: u["age"])                 # 나이 오름차순
sorted(users, key=lambda u: u["age"], reverse=True)   # 내림차순
max(users, key=lambda u: u["age"])                    # 가장 나이 많은 사람

list(map(lambda n: n * 2, nums))         # 각 원소 변환
list(filter(lambda n: n % 2 == 0, nums)) # 조건 통과한 원소만
```

> `map`/`filter` 는 리스트 컴프리헨션(`[n*2 for n in nums]`)으로 쓰면 보통 더 읽기 쉽습니다.
> 로직이 여러 줄이면 람다 대신 `def` 로 함수를 만드세요.

---

## 4. match / case — [`04_match_case.py`](04_match_case.py)

하나의 값을 여러 **패턴**과 위에서부터 대조해, 처음 맞는 `case` 를 실행합니다. (Python 3.10+)

```python
match status:
    case 200:
        ...
    case 400 | 401 | 404:      # | 로 여러 값 OR
        ...
    case _:                    # _ = "그 외 전부" (default 역할)
        ...
```

### `case _` — 데이터 타입이 달라도 처리

`case` 에 **타입**을 쓰면, 들어오는 값이 `int`든 `str`든 `list`든 `dict`든 타입별로 갈라서 처리하고,
어디에도 안 맞으면 `case _` 가 받아 줍니다.

```python
def describe(value):
    match value:
        case bool():                 # bool 은 int 하위라 먼저 검사
            return f"불리언: {value}"
        case int() | float():
            return f"숫자: {value}"
        case str():
            return f"문자열: '{value}'"
        case [first, *rest]:         # 시퀀스 구조 분해
            return f"리스트: 첫 항목={first}"
        case {"name": name}:         # dict 에 'name' 키가 있으면
            return f"딕셔너리: name={name}"
        case None:
            return "None"
        case _:                      # 처리 규칙이 없는 나머지
            return f"미지원 타입: {type(value).__name__}"
```

| 입력 | 결과 |
|---|---|
| `describe(10)` | 숫자: 10 |
| `describe("안녕")` | 문자열: '안녕' |
| `describe([1,2,3])` | 리스트: 첫 항목=1 |
| `describe({"name":"홍길동"})` | 딕셔너리: name=홍길동 |
| `describe(3+4j)` | 미지원 타입: complex ← **`case _` 가 처리** |

### 가드 (case + if)

```python
match score:
    case n if n >= 90:
        return "A"
    case n if n >= 80:
        return "B"
    case _:
        return "F"
```

---

## 5. 반복문 while — [`05_while.py`](05_while.py)

**조건이 참인 동안** 블록을 반복합니다. 반복 횟수가 정해졌으면 `for`, 조건으로 끝내야 하면 `while`.

```python
i = 1
while i <= 5:
    print(i)
    i += 1          # ← 조건을 언젠가 False로 만들 코드 필수 (없으면 무한 루프)
```

| 키워드 | 동작 |
|---|---|
| `break` | 조건과 상관없이 루프 **즉시 탈출** |
| `continue` | 이번 회차만 건너뛰고 **다음 반복으로** |
| `while ~ else` | `break` 없이 조건이 False가 되어 정상 종료하면 `else` 실행 |

```python
while True:                 # 무한 루프 + 내부 break 로 제어
    total += n
    if total > 30:
        break
    n += 1
```

> "올바른 입력이 들어올 때까지 되묻는" `while True` 패턴은
> `proj_streamlit/chat_app.py` 의 "메시지를 계속 받는" 챗봇 흐름과 같은 아이디어입니다.
