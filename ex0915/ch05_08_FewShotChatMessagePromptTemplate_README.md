# FewShotChatMessagePromptTemplate — Chat 모델용 퓨샷 프롬프트

09/15 실습. [`ch05_08_FewShotChatMessagePromptTemplate.ipynb`](ch05_08_FewShotChatMessagePromptTemplate.ipynb) —
[`ch05_06_FewShotPrompt_README.md`](ch05_06_FewShotPrompt_README.md)의 `FewShotPromptTemplate`(단일 문자열 프롬프트용)과
[`ch05_07_ExampleSelector_README.md`](ch05_07_ExampleSelector_README.md)의 `ExampleSelector`(유사 예시 자동 선택)를,
[`ch05_04_ChatPromptTemplate_README.md`](ch05_04_ChatPromptTemplate_README.md)에서 다룬 **Chat 모델(메시지 목록) 프롬프트**에
그대로 적용한 버전이 `FewShotChatMessagePromptTemplate`입니다.

---

## 1. 예시(examples) 준비 — 지시문 기반 태스크 3종

```python
examples = [
    {
        "instruction": "당신은 회의록 작성 전문가 입니다...",
        "input": "2023년 12월 25일, XYZ 회사의 마케팅 전략 회의가 오후 3시에 시작되었다...",
        "answer": """...""",
    },
    {
        "instruction": "당신은 요약 전문가 입니다. 다음 주어진 정보를 바탕으로 내용을 요약해 주세요",
        "input": "이 문서는 '지속 가능한 도시 개발을 위한 전략'에 대한 20페이지 분량...",
        "answer": """문서 요약: 지속 가능한 도시 개발을 위한 전략 보고서...""",
    },
    {
        "instruction": "당신은 문장 교정 전문가 입니다. 다음 주어진 문장을 교정해 주세요",
        "input": "우리 회사는 새로운 마케팅 전략을 도입하려고 한다...",
        "answer": "본 회사는 새로운 마케팅 전략을 도입함으로써, ...",
    },
]
```

- 이번에는 `question`/`answer` 2개 필드 대신 `instruction`(무슨 작업을 하라는 지시), `input`(작업
  대상 텍스트), `answer`(그 작업의 결과물)로 구성된 3개 필드를 씁니다. "회의록 작성", "문서 요약",
  "문장 교정"처럼 **서로 다른 태스크의 예시**를 함께 등록해 두고, 실제 질문에 맞는 태스크의 예시를
  골라 쓰는 것이 목표입니다.
- 노트북 안에서 `answer` 값이 `"..."`처럼 축약되어 있는 것은 실습 편의를 위해 예시 본문을 길게
  풀어 쓰지 않고 요약해 둔 것입니다. 실제로는 회의록/요약문/교정문 전체가 들어갑니다.

## 2. 예시를 메시지 쌍으로 렌더링하는 `example_prompt`

```python
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

chroma = Chroma("fewshot_chat", OpenAIEmbeddings())

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{instruction}:\n{input}"),
        ("ai", "{answer}"),
    ]
)
```

- `ch05_06`의 `example_prompt`는 `PromptTemplate`(문자열 하나)이었지만, 여기서는 `ChatPromptTemplate`을
  씁니다. 예시 하나가 **"human: 지시+입력" → "ai: 정답"이라는 대화 한 쌍(turn)**으로 렌더링되어,
  실제 Chat 모델이 주고받는 형식 그대로 예시를 보여줄 수 있습니다.

## 3. `SemanticSimilarityExampleSelector`로 예시 자동 선택

```python
example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, OpenAIEmbeddings(), chroma, k=1,
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
)
```

- `ch05_07`과 동일한 방식으로, 3개 예시의 `instruction`+`input`을 임베딩해 벡터 스토어(`chroma`)에
  저장해 두고, 실제 질문이 들어오면 가장 유사한 예시를 `k=1`개 골라냅니다.
- `FewShotChatMessagePromptTemplate(example_selector=..., example_prompt=...)`는 `FewShotPromptTemplate`의
  Chat 버전으로, `.format()`/체인 실행 시점에 선택된 예시를 `example_prompt`로 렌더링해 **메시지
  리스트** 형태로 만들어 줍니다. (`suffix`가 없는 이유는, 실제 질문 메시지를 아래 4단계에서 별도로
  붙이기 때문입니다.)

```python
question = {
    "instruction": "회의록을 작성해 주세요",
    "input": "2023년 12월 26일, ABC 기술 회사의 제품 개발 팀은 새로운 모바일 애플리케이션 프로젝트에 대한 주간 진행 상황 회의를 가졌다. ...",
}

example_selector.select_examples(question)
```
```
[{'input': '2023년 12월 25일, XYZ 회사의 마케팅 전략 회의가 오후 3시에 시작되었다...',
  'instruction': '당신은 회의록 작성 전문가 입니다...',
  'answer': '...'}]
```

- "회의록을 작성해 주세요"라는 질문에 대해, 3개 예시 중 **회의록 작성 예시**가 정확히 선택되었습니다.
  태스크 종류가 다른 예시들(요약, 교정) 속에서도 의미적으로 가장 가까운 예시를 골라낸 것입니다.

## 4. `MessagesPlaceholder`처럼 다른 메시지들과 함께 조립하기

```python
final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        few_shot_prompt,
        ("human", "{instruction}\n{input}"),
    ]
)
```

- `ch05_05`에서 `MessagesPlaceholder`를 `ChatPromptTemplate.from_messages()` 목록 중간에 끼워 넣었던
  것과 같은 방식으로, 여기서는 `few_shot_prompt`(선택된 예시로 만들어진 메시지들) 자체를 목록의
  한 항목으로 그대로 끼워 넣습니다.
- 최종 구조: `system 메시지(역할 설정)` → `few_shot_prompt가 만든 예시 메시지들(선택된 예시 1개의
  human/ai 쌍)` → `human 메시지(실제 지시+입력)`. 모델은 예시를 참고 자료 삼아 마지막 질문에 답합니다.

## 5. 체인 실행

```python
chain = final_prompt | llm
answer = chain.stream(question)
stream_response(answer)
```
```
### ABC 기술 회사 제품 개발 팀 회의록
- 날짜: 2023년 12월 26일
- 참석자: 최현수 (프로젝트 매니저), 황지연 (주요 개발자), 김태영 (UI/UX 디자이너)

#### 회의 주요 내용:
1. 프로젝트의 현재 진행 상황 검토
2. 다가오는 마일스톤에 대한 계획 수립
...
```

- `question` 딕셔너리(`instruction`, `input`)를 그대로 `chain.stream()`에 넘기면, 선택된 회의록
  예시의 형식(날짜/참석자/주요 내용/요약/다음 일정 등 구조화된 항목)을 그대로 따라 한 **회의록**이
  생성됩니다. 예시로 준 태스크(회의록 작성)와 실제 요청이 일치했기 때문에, 모델이 예시의 출력
  구조를 자연스럽게 재사용했습니다.

## 요약

| 비교 | `ch05_06`/`07` (`FewShotPromptTemplate`) | `ch05_08` (`FewShotChatMessagePromptTemplate`) |
|---|---|---|
| 대상 | 단일 문자열 프롬프트 | Chat 메시지 목록 프롬프트 |
| 예시 렌더링 | `PromptTemplate` (문자열) | `ChatPromptTemplate` (human/ai 메시지 쌍) |
| 실제 질문 결합 방식 | `suffix`로 문자열 뒤에 이어 붙임 | `ChatPromptTemplate.from_messages()` 목록에 `few_shot_prompt`를 항목으로 삽입 |
| 예시 선택 | (동일) `example_selector`로 유사 예시 자동 선택 가능 | (동일) `example_selector`로 유사 예시 자동 선택 가능 |

태스크 종류가 여러 개 섞여 있는 예시 풀에서, 질문에 맞는 예시(형식)를 자동으로 골라 Chat 모델에게
"이런 형식으로 답하라"고 보여주는 것이 핵심입니다.
