# PartialVariables — 함수로 부분 변수 채우기

09/15 실습. [`ch05_02_PartialVariables.ipynb`](ch05_02_PartialVariables.ipynb) — [`ch05_01_PromptTemplate_README.md`](ch05_01_PromptTemplate_README.md)에서
다룬 `partial_variables`를 한 단계 더 활용해, **고정값이 아니라 호출할 때마다 값이 바뀌는 함수**를
부분 변수로 넘기는 방법을 다룹니다.

---

## 1. 문제 상황 — 매번 바뀌는 값을 어떻게 채울까

`ch05_01`에서는 `partial_variables={"country2": "미국"}`처럼 **고정된 문자열**을 미리 채워 넣었습니다.
하지만 "오늘 날짜"처럼 프롬프트를 만드는 시점마다 값이 달라져야 하는 경우도 있습니다.

```python
from datetime import datetime

def get_today():  # 날짜를 반환하는 함수 정의
    return datetime.now().strftime("%B %d")

get_today()
# -> 'September 15'
```

이런 값을 `partial_variables`에 문자열로 직접 넣으면 노트북을 실행한 그 순간의 날짜로 **고정**되어 버립니다.
매번 최신 날짜가 반영되게 하려면 값이 아니라 **값을 만들어내는 함수 자체**를 넘겨야 합니다.

## 2. `partial_variables`에 함수 전달하기

```python
prompt = PromptTemplate(
    template="오늘의 날짜는 {today}입니다. 오늘이 생일인 유명인 {n}명을 나열해 주세요. 생년월일을 표기해주세요.",
    input_variables=["n"],
    partial_variables={
        "today": get_today  # 함수 자체를 전달 (호출 결과가 아님에 주의)
    },
)

prompt.format(n=3)
# -> '오늘의 날짜는 September 15입니다. 오늘이 생일인 유명인 3명을 나열해 주세요. 생년월일을 표기해주세요.'
```

- `"today": get_today`처럼 **함수 객체 자체**를 전달하면, `PromptTemplate`이 `.format()`을 호출할 때마다
  내부적으로 `get_today()`를 실행해 그 반환값을 `{today}` 자리에 채워 넣습니다.
- `"today": get_today()`처럼 **괄호를 붙여 호출한 결과(문자열)**를 넘기면 `ch05_01`의 `"country2": "미국"`
  예시와 똑같이 그 시점의 값으로 고정되어 버립니다. 함수 vs. 함수 호출 결과의 차이를 구분하는 것이 핵심입니다.
- `input_variables=["n"]`에는 `today`가 빠져 있으므로, 실제로 값을 매번 입력해야 하는 변수는 `n` 하나뿐입니다.

## 3. 체인 실행

```python
chain = prompt | llm
print(chain.invoke(3).content)
```
```
1. Prince Harry (1984년 9월 15일)
2. Tommy Lee Jones (1946년 9월 15일)
3. Agatha Christie (1890년 9월 15일)
```

- `chain.invoke(3)`처럼 값 하나만 넘기면 남은 변수 `n`에 자동으로 매핑되고, `today`는 호출 시점마다
  `get_today()`가 실행되어 오늘 날짜(9월 15일)로 채워집니다.

### partial로 고정된 값도 명시적으로 덮어쓰기 가능

```python
print(chain.invoke({"today": "Jan 02", "n": 3}).content)
```
```
1. Kate Bosworth - 1983년 1월 2일
2. Tia Carrere - 1967년 1월 2일
3. Renée Elise Goldsberry - 1971년 1월 2일
```

- `ch05_01`에서 확인한 것과 마찬가지로, 체인 호출 시 딕셔너리에 `today` 키를 명시적으로 넘기면
  `partial_variables`에 등록된 함수(`get_today`) 대신 **넘긴 값이 우선 적용**됩니다.
- 덕분에 "평소에는 오늘 날짜를 자동으로 쓰되, 필요할 때만 다른 날짜로 테스트"하는 것이 가능합니다.

## 요약

| 상황 | `partial_variables`에 넘길 값 | 결과 |
|---|---|---|
| 항상 같은 고정값 | 문자열/값 그 자체 (예: `"미국"`) | 매번 동일한 값 사용 |
| 호출 시점마다 달라지는 값 | 함수 객체 (예: `get_today`) | `.format()`/`.invoke()` 호출마다 함수가 재실행되어 최신 값 반영 |
| 특정 호출에서만 다른 값을 쓰고 싶을 때 | 체인 `invoke({"today": "Jan 02", ...})` | 부분 변수를 일시적으로 덮어씀 |
