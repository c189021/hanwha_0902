# StructuredOutputParser와 JsonOutputParser

09/16 실습. [`ch06_03_StructuredOutputParser_JsonDict.ipynb`](ch06_03_StructuredOutputParser_JsonDict.ipynb) — 응답 스키마를 정의해 LLM의 답변을 키-값 형태의 Python `dict` 또는 JSON 객체로 변환하는 방법을 다룹니다.

---

## 1. 구조화된 출력 파서란

LLM의 답변은 기본적으로 자연어 문자열이지만, 애플리케이션에서 사용하려면 일정한 필드와 형식이 필요할 때가 많습니다. `StructuredOutputParser`는 응답에 포함될 필드를 `ResponseSchema`로 정의하고, LLM이 해당 형식으로 답하도록 포맷 지시사항을 생성합니다.

이 노트북에서 사용하는 첫 번째 응답 구조는 다음과 같습니다.

- `answer`: 사용자의 질문에 대한 답변
- `source`: 답변에 사용한 출처 또는 웹사이트 주소

## 2. 환경 설정과 import

노트북은 `.env` 파일에 저장된 API 키를 읽습니다.

```python
from dotenv import load_dotenv

load_dotenv()
```

### `langchain_classic` import 경로

노트북에서는 처음에 다음과 같은 import가 `ModuleNotFoundError`를 일으킬 수 있음을 설명합니다.

```python
# 오류가 발생할 수 있는 경로
# from output_parsers.output_parsers import ResponseSchema, StructuredOutputParser
```

실습에서는 `langchain_classic`의 경로를 사용합니다.

```python
from langchain_classic.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
```

필요한 환경에서는 다음 패키지를 설치합니다.

```python
!pip install langchain_classic
```

## 3. `ResponseSchema`로 응답 필드 정의

```python
response_schemas = [
    ResponseSchema(name="answer", description="사용자의 질문에 대한 답변"),
    ResponseSchema(
        name="source",
        description="사용자의 질문에 답하기 위해 사용된 `출처`, `웹사이트주소` 이여야 합니다.",
    ),
]
```

`ResponseSchema`는 결과에 포함할 필드의 이름과 설명을 정의합니다. 여러 필드를 리스트로 전달할 수 있습니다.

이 스키마를 바탕으로 파서를 생성합니다.

```python
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
```

## 4. 포맷 지시사항을 프롬프트에 삽입하기

파서는 모델이 따라야 하는 출력 형식 안내문을 자동으로 생성합니다.

```python
format_instructions = output_parser.get_format_instructions()
print(format_instructions)
```

생성된 지시사항을 프롬프트의 부분 변수로 미리 넣습니다.

```python
prompt = PromptTemplate(
    template=(
        "answer the users question as best as possible.\n"
        "{format_instructions}\n{question}"
    ),
    input_variables=["question"],
    partial_variables={"format_instructions": format_instructions},
)
```

`partial_variables`에 포맷 지시사항을 지정했기 때문에 체인을 실행할 때는 `question`만 전달하면 됩니다.

## 5. 모델과 파서 연결

```python
model = ChatOpenAI(temperature=0)
chain = prompt | model | output_parser
```

이 체인은 다음 순서로 실행됩니다.

```text
PromptTemplate -> ChatOpenAI -> StructuredOutputParser
```

- `PromptTemplate`: 질문과 출력 형식 지시사항을 하나의 프롬프트로 구성합니다.
- `ChatOpenAI`: 질문에 대한 답변을 생성합니다.
- `StructuredOutputParser`: 모델 응답을 스키마에 맞는 Python `dict`로 변환합니다.

### 일반 호출

```python
chain.invoke({"question": "아르헨티나의 수도는 어디인가요?"})
```

결과는 다음과 같은 키-값 구조가 됩니다.

```python
{
    "answer": "아르헨티나의 수도는 부에노스아이레스입니다.",
    "source": "..."
}
```

실제 답변과 출처의 내용은 모델 응답에 따라 달라질 수 있습니다.

### 스트리밍 호출

```python
for s in chain.stream({"question": "세종대왕의 업적은 무엇인가요?"}):
    print(s)
```

`stream()`을 사용하면 응답을 스트리밍으로 받아 출력할 수 있습니다. 체인 마지막에 파서가 연결되어 있으므로 최종 결과는 정의된 구조에 맞춰 처리됩니다.

## 6. JSON 형식 출력

노트북 후반부에서는 JSON 객체의 기본 구조도 확인합니다.

```json
{
    "name": "John Doe",
    "age": 30,
    "is_student": false,
    "skills": ["Java", "Python", "JavaScript"],
    "address": {
        "street": "123 Main St",
        "city": "Anytown"
    }
}
```

JSON은 문자열 키와 값을 쌍으로 가지며, 문자열·숫자·불리언·배열·중첩 객체를 표현할 수 있습니다. 구조화된 응답을 다른 프로그램이나 API로 전달할 때 유용합니다.

## 7. `JsonOutputParser`와 Pydantic 결합

### 모델 스키마 정의

```python
from pydantic import BaseModel, Field

class Topic(BaseModel):
    description: str = Field(description="주제에 대한 간결한 설명")
    hashtags: str = Field(description="해시태그 형식의 키워드(2개 이상)")
```

이 실습에서는 지구 온난화 질문에 대해 간결한 설명과 두 개 이상의 해시태그를 반환하도록 합니다.

```python
question = "지구 온난화의 심각성에 대해 알려주세요."
```

### JSON 파서 생성

```python
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser(pydantic_object=Topic)
print(parser.get_format_instructions())
```

`JsonOutputParser`는 Pydantic 모델을 참고해 JSON 형식 지시사항을 생성합니다. `StructuredOutputParser`와 마찬가지로 이 지시사항을 프롬프트에 넣어 모델의 출력 형식을 안내합니다.

### `ChatPromptTemplate`으로 체인 구성

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 친절한 AI 어시스턴트 입니다. 질문에 간결하게 답변하세요."),
        ("user", "#Format: {format_instructions}\n\n#Question: {question}"),
    ]
)

prompt = prompt.partial(
    format_instructions=parser.get_format_instructions()
)
```

시스템 메시지에는 답변 역할과 길이를 지정하고, 사용자 메시지에는 포맷 지시사항과 질문을 배치합니다.

### JSON 응답 받기

```python
model = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
chain = prompt | model | parser

answer = chain.invoke({"question": question})
```

결과는 JSON 형태로 파싱된 Python `dict`입니다. 따라서 키를 사용해 원하는 값에 접근할 수 있습니다.

```python
answer["description"]
answer["hashtags"]
```

## 8. 두 파서 비교

| 파서 | 스키마 정의 방식 | 반환 형태 | 적합한 경우 |
|---|---|---|---|
| `StructuredOutputParser` | `ResponseSchema` 리스트 | Python `dict` | 여러 응답 필드와 설명을 간단히 정의할 때 |
| `JsonOutputParser` | JSON 형식 또는 Pydantic 모델 | JSON 형태의 Python `dict` | JSON 응답이나 Pydantic 기반 구조가 필요할 때 |

두 파서 모두 `get_format_instructions()`로 모델에 출력 형식을 안내하고, 프롬프트에 해당 지시사항을 삽입한 뒤 체인의 마지막에 연결합니다.

## 9. 주의할 점

- 출력 형식 지시사항이 프롬프트에 포함되어야 원하는 구조가 나올 가능성이 높습니다.
- 모델이 JSON 괄호, 쉼표, 따옴표 등을 잘못 생성하면 파싱 오류가 발생할 수 있습니다.
- `source`처럼 모델이 실제로 확인할 수 없는 출처를 요구하면 부정확한 값이 생성될 수 있으므로, 검색 도구나 문서 검색 결과와 함께 사용하는 것이 좋습니다.
- `with_structured_output()`은 모델이 네이티브 구조화 출력을 지원하는지 확인해야 하지만, `StructuredOutputParser`와 `JsonOutputParser`는 프롬프트 지시와 응답 파싱에 의존합니다.

## 요약

- `ResponseSchema`로 응답 필드의 이름과 설명을 정의합니다.
- `StructuredOutputParser`는 모델 응답을 키-값 형태의 Python `dict`로 파싱합니다.
- `get_format_instructions()`로 출력 형식 지시사항을 만들고 `partial_variables`로 프롬프트에 삽입합니다.
- `JsonOutputParser`는 JSON 형식 응답을 파싱하며 Pydantic 모델을 스키마로 사용할 수 있습니다.
- 두 파서는 `prompt | model | parser` 형태의 Runnable 체인으로 연결할 수 있습니다.
