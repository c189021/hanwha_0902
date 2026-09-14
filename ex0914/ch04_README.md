# LangChain ChatOpenAI — 응답 구조 / logprobs / 스트리밍

09/14 실습. [`ch04.ipynb`](ch04.ipynb) — LangChain의 `ChatOpenAI`로 모델을 호출했을 때
**응답 객체의 구조**, **토큰 확신도(logprobs)**, **스트리밍(streaming) 출력**을 다룹니다.
(기본 호출 자체는 [`../ex0911/README.md`](../ex0911/README.md#4-langchain-이란) 참고)

---

## 1. 기본 호출과 응답 객체

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    temperature=0.1,
    model_name="gpt-4o-mini",
)

question = "대한민국의 수도는 어디인가요?"
response = llm.invoke(question)
```

`response`는 문자열이 아니라 **`AIMessage` 객체**이며, 아래 정보를 함께 담고 있습니다.

- `response.content` → `'대한민국의 수도는 서울입니다.'` (실제 답변 텍스트)
- `response.response_metadata` → 모델명, 토큰 사용량 등 부가 정보를 담은 딕셔너리
  - `response.response_metadata["token_usage"]["total_tokens"]` → `24` (이번 호출에 사용된 전체 토큰 수)

## 2. logprobs — 모델의 답변 확신도 확인하기

> 모델이 단어(토큰)를 하나씩 생성할 때 "이 토큰을 얼마나 확신을 가지고 선택했는지"에 대한
> 확률값(log probability)을 함께 받을 수 있습니다. **0에 가까울수록 확신이 강한 답변**입니다.

```python
llm_with_logprob = ChatOpenAI(
    temperature=0.1,
    max_tokens=2048,
    model_name="gpt-4o-mini",
).bind(logprobs=True)   # logprobs 옵션을 켠 모델 바인딩

response = llm_with_logprob.invoke("대한민국의 수도는 어디인가요?")
response.response_metadata["logprobs"]
```

- `.bind(옵션=값)` : 모델 객체에 추가 옵션(`logprobs=True`)을 결합해 새 호출 가능 객체를 만듭니다.
- 응답의 `response_metadata["logprobs"]["content"]`에 토큰별 `token`, `logprob` 값이 배열로 들어옵니다.
  예: `"서울"` 토큰의 `logprob`이 `-0.000135` → 0에 매우 가까움 → 모델이 확신을 가지고 답했다는 의미.

## 3. 스트리밍(streaming) — 실시간 토큰 출력

```python
answer = llm.stream("대한민국의 아름다운 관광지 10곳과 주소를 알려주세요!")

for token in answer:
    print(token.content, end="", flush=True)
```

- `llm.invoke()`는 답변이 전부 완성된 뒤 한 번에 반환하지만, `llm.stream()`은 토큰(글자/단어 조각)이
  생성되는 대로 하나씩 순차적으로 반환하는 **제너레이터**를 돌려줍니다. ChatGPT 화면처럼 답변이
  실시간으로 타이핑되는 효과를 내고 싶을 때 사용합니다.
- `flush=True` : 출력 버퍼에 모아뒀다가 한 번에 찍지 않고, 생성되는 즉시 화면에 바로바로 출력합니다.
- 스트리밍 결과를 변수에 모아서 최종 문자열로 쓰고 싶다면 아래처럼 이어붙입니다.

```python
answer = llm.stream("대한민국의 아름다운 관광지 10곳과 주소를 알려주세요!")

final_answer = ""
for token in answer:
    final_answer += token.content
```
