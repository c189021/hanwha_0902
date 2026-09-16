# ExampleSelector — 질문과 유사한 예시만 골라서 넣기

09/15 실습. [`ch05_07_ExampleSelector.ipynb`](ch05_07_ExampleSelector.ipynb) — [`ch05_06_FewShotPrompt_README.md`](ch05_06_FewShotPrompt_README.md)에서는
`examples` 리스트에 있는 예시를 **전부 다** 프롬프트에 넣었습니다. 예시가 많아지면 프롬프트가
불필요하게 길어지고 비용도 늘어납니다. `ExampleSelector`는 매번 모든 예시를 넣는 대신, **실제 질문과
가장 관련 있는 예시만 골라서** 프롬프트에 넣어주는 도구입니다.

---

## 1. 예시(examples) 4개 준비

이번에는 서로 성격이 다른 4개의 질문-풀이 예시를 준비합니다.

1. 스티브잡스와 아인슈타인 중 누가 더 오래 살았나요? (인물 수명 비교)
2. 네이버의 창립자는 언제 태어났나요? (인물 출생 정보)
3. 율곡 이이의 어머니가 태어난 해에 조선을 통치하던 왕은 누구인가요? (역사/연도 추론)
4. 올드보이와 기생충의 감독이 같은 나라 출신인가요? (인물 비교)

각 항목은 `ch05_06`과 동일하게 `{"question": ..., "answer": "추가 질문 → 중간 답변 → 최종 답변"}`
형태입니다. 예시가 늘어날수록 `FewShotPromptTemplate`에 전부 넣기엔 프롬프트가 길어지는 문제가
뚜렷해집니다.

## 2. `SemanticSimilarityExampleSelector` — 임베딩 기반 유사도로 선택

```python
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

chroma = Chroma("example_selector", OpenAIEmbeddings())

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples,          # 선택 가능한 예시 목록
    OpenAIEmbeddings(), # 예시들을 벡터로 바꿀 임베딩 모델
    Chroma,             # 벡터를 저장/검색할 벡터 스토어
    k=1,                # 질문마다 상위 몇 개의 예시를 고를지
)
```

- `SemanticSimilarityExampleSelector.from_examples()`는 `examples`의 각 `question`을 임베딩(벡터화)해
  **벡터 스토어(Chroma)**에 저장해 둡니다. 이후 새로운 질문이 들어오면 그 질문도 임베딩한 뒤,
  저장된 예시들 중 **벡터 거리가 가장 가까운(=의미적으로 가장 비슷한) 예시**를 찾아냅니다.
- `k=1`은 질문 하나당 가장 유사한 예시를 **1개만** 골라 쓰겠다는 뜻입니다. `k`를 늘리면 여러 개를
  함께 선택할 수 있습니다.
- 임베딩과 벡터 스토어를 이용해 텍스트 간 유사도를 계산하는 방식은 RAG(검색 증강 생성) 파이프라인의
  검색(retrieval) 단계와 동일한 원리입니다.

## 3. 유사 예시 선택 결과 확인

```python
question = "Google이 창립된 연도에 Bill Gates의 나이는 몇 살인가요?"
selected_examples = example_selector.select_examples({"question": question})

for example in selected_examples:
    print(f'question:\n{example["question"]}')
    print(f'answer:\n{example["answer"]}')
```
```
question:
네이버의 창립자는 언제 태어났나요?
answer:
이 질문에 추가 질문이 필요한가요: 예.
추가 질문: 네이버의 창립자는 누구인가요?
...
최종 답변은: 1967년 6월 22일
```

- `example_selector.select_examples({"question": ...})`를 호출하면, 4개 예시 중 "네이버의 창립자는
  언제 태어났나요?" 예시가 선택되었습니다. "회사 창립 시점 + 인물의 나이/생년"을 함께 묻는다는 점에서
  임베딩 상 가장 의미적으로 가까운 예시로 판단된 것입니다.
- 이처럼 질문마다 **자동으로 가장 관련 있는 예시**가 골라지므로, 예시가 수십~수백 개로 늘어나도
  프롬프트에는 필요한 만큼만 포함시킬 수 있습니다.

## 4. `FewShotPromptTemplate`에 `example_selector` 연결

```python
from langchain_core.prompts.few_shot import FewShotPromptTemplate

example_prompt = PromptTemplate.from_template(
    "Question:\n{question}\nAnswer:\n{answer}"
)

prompt = FewShotPromptTemplate(
    example_selector=example_selector,  # examples= 대신 example_selector= 사용
    example_prompt=example_prompt,
    suffix="Question:\n{question}\nAnswer:",
    input_variables=["question"],
)

example_selector_prompt = prompt.format(
    question="Google이 창립된 연도에 Bill Gates의 나이는 몇 살인가요?"
)
print(example_selector_prompt)
```
```
Question:
네이버의 창립자는 언제 태어났나요?
Answer:
...
최종 답변은: 1967년 6월 22일

Question:
Google이 창립된 연도에 Bill Gates의 나이는 몇 살인가요?
Answer:
```

- `ch05_06`에서는 `FewShotPromptTemplate(examples=examples, ...)`처럼 **고정된 예시 리스트**를
  넘겼지만, 여기서는 `examples` 대신 `example_selector=example_selector`를 넘깁니다. `.format()`이
  호출될 때마다 내부적으로 `select_examples()`가 실행되어, **입력 질문에 맞는 예시만 동적으로 골라**
  프롬프트에 포함시킵니다.
- 나머지 구조(`example_prompt`, `suffix`, `input_variables`)는 `ch05_06`과 동일합니다.

## 5. 체인 실행

```python
chain = prompt | llm

answer = chain.stream(
    {"question": "Google이 창립된 연도에 Bill Gates의 나이는 몇 살인가요?"}
)
stream_response(answer)
```
```
Google이 창립된 연도는 1998년이며, Bill Gates는 1998년에 43살이었습니다.
```

- 4개 예시를 전부 넣지 않고 가장 관련 있는 예시(네이버 창립자 예시) 1개만 넣었는데도, 모델은
  "추가 질문 → 중간 답변" 스타일을 그대로 따라 하며 구글 창립 연도(1998년)를 기준으로 빌 게이츠의
  나이(43세)를 정확히 계산했습니다.

## 요약

| 방식 | 예시 선택 | 특징 |
|---|---|---|
| `ch05_06` — `examples=[...]` | 고정된 예시를 전부 사용 | 예시가 적을 때 간단 |
| `ch05_07` — `example_selector=...` | 질문과 임베딩 유사도가 높은 예시를 동적으로 선택 | 예시가 많아져도 프롬프트 길이를 절약하며 관련성 높은 예시만 사용 |

핵심 구성 요소: `OpenAIEmbeddings`(텍스트→벡터), `Chroma`(벡터 저장/검색), `SemanticSimilarityExampleSelector`
(유사도 기반 선택), `k`(선택할 예시 개수).
