# FewShotPromptTemplate — 예시를 보여주고 형식을 따라 하게 만들기

09/15 실습. [`ch05_06_FewShotPrompt.ipynb`](ch05_06_FewShotPrompt.ipynb) — 지금까지는 지시문만 담긴 프롬프트를 다뤘다면,
이번에는 **"이렇게 풀어라"는 예시(example)를 프롬프트 안에 미리 보여준 뒤** 실제 질문을 묻는
퓨샷(Few-Shot) 프롬프팅을 `FewShotPromptTemplate`으로 구현합니다.

---

## 1. 퓨샷 프롬프팅이란

퓨샷 프롬프팅은 모델에게 "질문 → 풀이 과정 → 답"의 **예시를 몇 개 먼저 보여준 뒤**, 마지막에 진짜
질문을 던져서 같은 형식(예: 단계별로 나눠 생각하기)으로 답하도록 유도하는 기법입니다. 이 노트북은
"복잡한 질문을 여러 개의 하위 질문으로 쪼개 단계적으로 답을 찾아가는" 방식(중간 질문 → 중간 답변 →
최종 답변)을 예시로 보여줍니다.

## 2. 예시(example) 데이터 정의

```python
examples = [
    {
        "question": "스티브잡스와 아인슈타인 중 누가 더 오래 살았나요?",
        "answer": """이 질문에 추가 질문이 필요한가요: 예.
                추가 질문 : 스티브 잡스는 몇 살에 사망했나요?
                중간 답변 : 스티브 잡스는 56세에 사망했습니다.
                추가 질문: 아인슈타인은 몇 살에 사망했나요?
                중간 답변 아인슈타인은 76세에 사망했습니다.
                최종 답변은 : 아인슈타인
                """,
    },
]
```

- `examples`는 `{"question": ..., "answer": ...}` 형태의 딕셔너리 리스트입니다. 각 `answer`는 최종
  답만 던지지 않고, "추가 질문 → 중간 답변"을 반복하며 논리적으로 답에 도달하는 **풀이 과정 전체**를
  담고 있습니다. 모델이 이 형식을 그대로 따라 하도록 유도하는 것이 목표입니다.

## 3. `example_prompt` — 예시 하나를 문자열로 렌더링하는 템플릿

```python
example_prompt = PromptTemplate.from_template(
    "Question:\n{question}\nAnswer:\n{answer}"
)

print(example_prompt.format(**examples[0]))
```
```
Question:
스티브잡스와 아인슈타인 중 누가 더 오래 살았나요?
Answer:
이 질문에 추가 질문이 필요한가요: 예.
                추가 질문 : 스티브 잡스는 몇 살에 사망했나요?
                ...
                최종 답변은 : 아인슈타인
```

- `example_prompt`는 `ch05_01`에서 배운 평범한 `PromptTemplate`입니다. 다만 여기서는 예시 하나를
  "Question: ... / Answer: ..." 형식의 문자열로 바꾸는 데 사용됩니다.
- `example_prompt.format(**examples[0])`처럼 `**`로 딕셔너리를 풀어서 넘기면 `question`, `answer`
  키가 각각 템플릿의 `{question}`, `{answer}`에 매핑됩니다.

## 4. `FewShotPromptTemplate` — 예시들 + 실제 질문을 하나로 합치기

```python
prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Question:\n{question}\nAnswer:",
    input_variables=["question"],
)

question = "Google이 창립된 연도에 Bill Gates의 나이는 몇 살인가요?"
final_prompt = prompt.format(question=question)
print(final_prompt)
```
```
Question:
스티브잡스와 아인슈타인 중 누가 더 오래 살았나요?
Answer:
이 질문에 추가 질문이 필요한가요: 예.
                ...
                최종 답변은 : 아인슈타인

Question:
Google이 창립된 연도에 Bill Gates의 나이는 몇 살인가요?
Answer:
```

- `examples`와 `example_prompt`를 지정하면, `FewShotPromptTemplate`이 `examples` 리스트의 각 항목을
  `example_prompt`로 포맷해 순서대로 이어 붙입니다(예시가 여러 개면 모두 나열됨).
- `suffix="Question:\n{question}\nAnswer:"`는 예시들 **뒤에 덧붙는, 실제로 답을 구해야 하는 질문
  부분**입니다. `{question}`이 바로 이 템플릿의 유일한 입력 변수(`input_variables=["question"]`)입니다.
- 결과적으로 `final_prompt`는 "예시 1개(풀이 과정 포함) + 진짜 질문(아직 답은 비어있음)"이 하나로
  합쳐진 긴 프롬프트 문자열이 됩니다. 모델은 이 전체를 읽고, 앞의 예시와 같은 스타일로 답을 이어 씁니다.

## 5. 퓨샷 프롬프트 없이 직접 호출 vs. 있을 때 비교

```python
llm = ChatOpenAI()
answer = llm.stream(final_prompt)
stream_response(answer)
```
```
이 질문에 추가 정보가 필요합니다. 구글이 창립된 연도와 Bill Gates의 출생 연도를 알아야 합니다.
```

- `final_prompt`(예시 포함)를 `llm.stream()`에 바로 문자열로 넘긴 경우입니다. 이 호출은 프롬프트
  템플릿 체인을 거치지 않고 완성된 문자열을 모델에 곧바로 전달한 것으로, 앞선 셀들에서 `final_prompt`가
  이미 예시+질문을 포함한 완성 문자열임을 확인하기 위한 예시입니다.

## 6. 체인으로 구성해 실행하기

```python
prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Question:\n{question}\nAnswer:",
    input_variables=["question"],
)

chain = prompt | llm | StrOutputParser()

answer = chain.stream(
    {"question": "Google이 창립된 연도에 Bill Gates의 나이는 몇 살인가요?"}
)
stream_response(answer)
```
```
이 질문에 추가 질문이 필요한가요? 예
        추가 질문: 구글이 창립된 연도는 언제인가요?
        중간 답변: 구글이 창립된 연도는 1998년입니다.
        추가 질문: 빌 게이츠는 1998년에 몇 살이었나요?
        중간 답변: 빌 게이츠는 43세였습니다.
        최종 답변: 빌 게이츠는 1998년에 43세이었습니다.
```

- `prompt | llm | StrOutputParser()`로 체인을 구성하면, `ch05_01`~`ch05_05`에서 본 것과 동일하게
  `chain.stream({"question": ...})` 한 번 호출로 "예시 포맷팅 → 모델 호출 → 텍스트 추출"이 전부 처리됩니다.
- 예시에서 보여준 "추가 질문 → 중간 답변 → 최종 답변" 패턴을 모델이 그대로 따라 하여, 구글 창립 연도
  (1998년)와 그 해 빌 게이츠의 나이(43세)를 단계적으로 구한 뒤 최종 답을 냈습니다. **예시 하나만
  보여줬을 뿐인데도 모델이 같은 풀이 형식을 재현**한 것이 퓨샷 프롬프팅의 핵심 효과입니다.

## 요약

| 구성 요소 | 역할 |
|---|---|
| `examples` | `{"question": ..., "answer": ...}` 형태의 예시(질문+풀이과정) 목록 |
| `example_prompt` | 예시 하나를 문자열로 렌더링하는 `PromptTemplate` |
| `suffix` | 예시들 뒤에 붙는, 실제로 답해야 할 질문 템플릿 |
| `FewShotPromptTemplate(examples, example_prompt, suffix, input_variables)` | 예시 + 실제 질문을 하나의 프롬프트로 결합 |

예시가 많아지거나 상황에 따라 예시를 동적으로 골라야 한다면 `ch05_07`의 `ExampleSelector`를 함께
사용합니다.
