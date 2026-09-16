# CustomExampleSelector — 나만의 예제 선택 로직 만들기

09/15 실습. [`ch05_09_CustomExampleSelector.ipynb`](ch05_09_CustomExampleSelector.ipynb) — [`ch05_07`](ch05_07_ExampleSelector_README.md)/
[`ch05_08`](ch05_08_FewShotChatMessagePromptTemplate_README.md)에서는 LangChain이 기본 제공하는
`SemanticSimilarityExampleSelector`를 사용했습니다. 이번에는 `langchain_teddynote` 패키지가 제공하는
**직접 구현된 예제 선택기(`CustomExampleSelector`)**를 사용해, "어떤 기준으로 예시를 고를지"를
직접 정의할 수 있다는 점을 확인합니다.

---

## 1. 예시(examples) — `ch05_08`과 동일한 3개 태스크

```python
examples = [
    {"instruction": "당신은 회의록 작성 전문가 입니다...", "input": "...", "answer": "..."},
    {"instruction": "당신은 요약 전문가 입니다. ...", "input": "...", "answer": "..."},
    {"instruction": "당신은 문장 교정 전문가 입니다. ...", "input": "...", "answer": "..."},
]
```

- `ch05_08`에서 썼던 "회의록 작성 / 요약 / 문장 교정" 3개 태스크 예시를 그대로 재사용합니다. 선택기
  구현체만 바뀌었을 뿐, 예시 데이터와 이후 프롬프트 조립 방식은 동일합니다.

## 2. `CustomExampleSelector` 생성 및 선택 결과 확인

```python
from langchain_openai import OpenAIEmbeddings
from langchain_teddynote.prompts import CustomExampleSelector

custom_selector = CustomExampleSelector(examples, OpenAIEmbeddings())

custom_selector.select_examples({"instruction": "다음 문장으로 회의록을 작성해 주세요"})
```
```
[{'instruction': '당신은 문장 교정 전문가 입니다. 다음 주어진 문장을 교정해 주세요',
  'input': '우리 회사는 새로운 마케팅 전략을 도입하려고 한다...',
  'answer': '본 회사는 새로운 마케팅 전략을 도입함으로써, ...'}]
```

- `CustomExampleSelector`는 LangChain의 예제 선택기 인터페이스(`BaseExampleSelector`)를 구현한
  **직접 만든(또는 강의용으로 커스터마이즈된) 선택기**로, `example_selector`가 갖춰야 할 최소 요건인
  `add_example()` / `select_examples()` 메서드를 자체 로직으로 정의한 것입니다. `ch05_07`/`ch05_08`의
  `SemanticSimilarityExampleSelector`처럼 내부적으로 임베딩(`OpenAIEmbeddings`)을 사용하지만,
  유사도를 계산하는 구체적인 방식(비교에 사용하는 필드, 거리 계산 방법 등)은 선택기를 만든 사람이
  자유롭게 정할 수 있습니다.
- 주목할 점은 선택 결과입니다. "**회의록**을 작성해 주세요"라는 요청에 대해 `ch05_08`의
  `SemanticSimilarityExampleSelector`라면 회의록 작성 예시를 골랐을 법하지만, 여기서는 **문장 교정**
  예시가 선택되었습니다. 이는 커스텀 선택기가 `ch05_07`/`08`의 기본 선택기와 **다른 비교 기준**(예:
  `instruction`만 비교하는지, 어떤 임베딩/거리 함수를 쓰는지)으로 동작하기 때문입니다. 즉,
  선택기 구현에 따라 "가장 관련 있는 예시"의 결과가 달라질 수 있다는 점을 직접 보여주는 예제입니다.

## 3. `FewShotChatMessagePromptTemplate`에 커스텀 선택기 연결

```python
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{instruction}:\n{input}"),
        ("ai", "{answer}"),
    ]
)

custom_fewshot_prompt = FewShotChatMessagePromptTemplate(
    example_selector=custom_selector,  # 커스텀 예제 선택기 사용
    example_prompt=example_prompt,
)

custom_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        custom_fewshot_prompt,
        ("human", "{instruction}\n{input}"),
    ]
)
```

- `ch05_08`과 완전히 동일한 조립 패턴입니다. `FewShotChatMessagePromptTemplate`의 `example_selector`
  인자에 `SemanticSimilarityExampleSelector` 대신 `custom_selector`를 꽂아 넣었을 뿐, 나머지
  (`example_prompt`, `system` 메시지 + `few_shot_prompt` + 실제 질문 메시지로 조립하는 구조)는
  바뀌지 않았습니다. 이는 `example_selector`가 `BaseExampleSelector` 인터페이스만 만족하면
  어떤 구현체든 `FewShotChatMessagePromptTemplate`에 자유롭게 끼워 넣을 수 있음을 보여줍니다.

## 4. 체인 실행

```python
from langchain_teddynote.messages import stream_response

chain = custom_prompt | llm

question = {
    "instruction": "회의록을 작성해 주세요",
    "input": "2023년 12월 26일, ABC 기술 회사의 제품 개발 팀은 새로운 모바일 애플리케이션 프로젝트에 대한 주간 진행 상황 회의를 가졌다...",
}

stream_response(chain.stream(question))
```

- `ch05_08`과 동일하게 `question`(`instruction` + `input`)을 체인에 넘기면, `custom_selector`가
  골라준 예시(위에서 확인한 문장 교정 예시)를 참고 자료로 삼아 모델이 회의록을 작성합니다.
  (이 셀의 실행 결과는 노트북에 저장되어 있지 않아 별도로 기록하지 않았습니다.)
- 2번 단계에서 확인했듯, 커스텀 선택기가 "회의록" 예시가 아닌 "문장 교정" 예시를 골랐기 때문에,
  `ch05_08`에서처럼 정확히 일치하는 형식의 예시가 주어지지 않고도 모델이 얼마나 잘 대응하는지를
  관찰할 수 있는 지점이기도 합니다.

## 요약

| 비교 | `ch05_07`/`08` — `SemanticSimilarityExampleSelector` | `ch05_09` — `CustomExampleSelector` |
|---|---|---|
| 출처 | LangChain 기본 제공 | `langchain_teddynote`가 제공하는 커스텀 구현체 |
| 선택 기준 | 예시 전체(질문/지시+입력)를 임베딩해 벡터 거리로 비교 | 구현체가 정의한 자체 기준(이 예제에서는 `SemanticSimilarityExampleSelector`와 다른 예시를 선택) |
| 연결 방법 | `FewShotPromptTemplate`/`FewShotChatMessagePromptTemplate`의 `example_selector=` | 동일하게 `example_selector=`에 연결 (인터페이스만 맞으면 교체 가능) |

핵심은 `example_selector`가 **교체 가능한 부품**이라는 점입니다. 기본 제공 선택기가 우리 데이터/요구에
맞지 않는다면, 같은 인터페이스(`select_examples()` 등)를 구현한 나만의 선택기를 만들어 그대로
갈아 끼울 수 있습니다.
