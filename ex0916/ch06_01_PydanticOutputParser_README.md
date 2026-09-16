# PydanticOutputParser — Pydantic 기반 구조화된 출력

09/16 실습. [`ch06_01_PydanticOutputParser.ipynb`](ch06_01_PydanticOutputParser.ipynb) — LangChain의 `PydanticOutputParser`를 사용해 LLM의 자유로운 답변을 미리 정의한 Pydantic 모델 객체로 변환하는 방법을 다룹니다.

---

## 1. 출력 파서란

LLM은 기본적으로 자연어 형태의 문자열을 반환합니다. 사람이 읽기에는 편하지만, 프로그램에서 발신자·이메일 주소·제목처럼 필요한 항목을 안정적으로 사용하려면 일정한 구조가 필요합니다.

출력 파서(Output Parser)는 LLM의 응답을 원하는 형식으로 변환합니다. 이 실습에서는 이메일 내용을 다음과 같은 `EmailSummary` 객체로 구조화합니다.

- `person`: 메일을 보낸 사람
- `email`: 메일을 보낸 사람의 이메일 주소
- `subject`: 메일 제목
- `summary`: 메일 본문 요약
- `date`: 본문에 언급된 미팅 날짜와 시간

## 2. 환경 설정과 import

노트북은 `.env` 파일에 저장한 API 키를 `load_dotenv()`로 읽습니다. 실행하기 전에 프로젝트 환경에 OpenAI API 키가 설정되어 있어야 합니다.

```python
from dotenv import load_dotenv

load_dotenv()
```

주요 라이브러리는 다음과 같습니다.

```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
```

LLM은 결정적인 결과를 얻기 위해 `temperature=0`으로 설정합니다.

```python
llm = ChatOpenAI(temperature=0, model="gpt-4.1-mini")
```

## 3. 파서 없이 이메일 요약하기

먼저 출력 파서를 사용하지 않고 이메일의 주요 내용을 추출합니다.

```python
prompt = PromptTemplate.from_template(
    "다음의 이메일 내용중 중요한 내용을 추출해 주세요.\n\n{email_conversation}"
)

chain = prompt | llm
answer = chain.stream({"email_conversation": email_conversation})
output = stream_response(answer, return_output=True)
```

이 방식은 자연어 답변을 얻기에는 간단하지만, 응답의 항목명이나 형식이 매번 달라질 수 있습니다. 따라서 이후 코드에서 `output.person`처럼 특정 필드에 직접 접근하기 어렵습니다.

## 4. Pydantic 모델로 출력 스키마 정의

`BaseModel`과 `Field`를 사용해 LLM 응답이 가져야 할 필드를 선언합니다.

```python
class EmailSummary(BaseModel):
    person: str = Field(description="메일을 보낸 사람")
    email: str = Field(description="메일을 보낸 사람의 이메일 주소")
    subject: str = Field(description="메일 제목")
    summary: str = Field(description="메일 본문을 요약한 텍스트")
    date: str = Field(description="메일 본문에 언급된 미팅 날짜와 시간")
```

각 필드의 타입과 설명은 출력 형식을 안내하는 데 사용됩니다. 이 모델을 기준으로 파서를 생성합니다.

```python
parser = PydanticOutputParser(pydantic_object=EmailSummary)
```

## 5. 포맷 지시사항을 프롬프트에 추가하기

`get_format_instructions()`는 모델이 `EmailSummary`에 맞는 형식으로 답하도록 안내하는 지시사항을 만들어 줍니다.

```python
print(parser.get_format_instructions())
```

이 지시사항을 프롬프트의 `{format}` 변수에 삽입합니다.

```python
prompt = PromptTemplate.from_template(
    """
You are a helpful assistant. Please answer the following questions in KOREAN.

QUESTION:
{question}

EMAIL CONVERSATION:
{email_conversation}

FORMAT:
{format}
"""
)

prompt = prompt.partial(format=parser.get_format_instructions())
```

`partial()`을 사용하면 실행할 때마다 포맷 지시사항을 입력하지 않아도 됩니다. 이후 체인을 호출할 때는 이메일과 질문만 전달하면 됩니다.

## 6. 응답을 Pydantic 객체로 파싱하기

먼저 LLM을 호출해 구조화된 형식의 문자열을 생성합니다.

```python
chain = prompt | llm

response = chain.stream(
    {
        "email_conversation": email_conversation,
        "question": "이메일 내용중 주요 내용을 추출해 주세요.",
    }
)

output = stream_response(response, return_output=True)
```

생성된 문자열을 `parser.parse()`에 전달하면 `EmailSummary` 객체가 반환됩니다.

```python
structured_output = parser.parse(output)
print(structured_output)
```

이제 응답 전체를 문자열로 다루지 않고 필드별로 접근할 수 있습니다.

```python
structured_output.person
structured_output.email
structured_output.subject
```

예시 이메일을 기준으로 하면 다음과 같은 정보가 추출됩니다.

```text
person: 김철수
email: chulsoo.kim@bikecorporation.me
subject: "ZENESIS" 자전거 유통 협력 및 미팅 일정 제안
date: 1월 15일 오전 10시
```

`summary`에는 ZENESIS 자전거의 브로슈어와 기술 사양·배터리 성능·디자인 정보 요청, 유통 협력 논의 및 미팅 제안 내용이 요약됩니다.

## 7. 체인에 파서를 직접 연결하기

응답 생성과 파싱을 별도의 단계로 나누지 않고, 파서를 체인의 마지막에 연결할 수도 있습니다.

```python
chain = prompt | llm | parser

response = chain.invoke(
    {
        "email_conversation": email_conversation,
        "question": "이메일 내용중 주요 내용을 추출해 주세요.",
    }
)

response
```

이 경우 `chain.invoke()`의 반환값이 이미 `EmailSummary` 객체입니다.

```text
PromptTemplate -> ChatOpenAI -> PydanticOutputParser
```

- `PromptTemplate`: 질문, 이메일 본문, 출력 형식을 하나의 프롬프트로 구성합니다.
- `ChatOpenAI`: 프롬프트를 바탕으로 응답을 생성합니다.
- `PydanticOutputParser`: 응답을 `EmailSummary` 객체로 변환합니다.

## 8. `parser.parse()`와 체인 연결 비교

| 방식 | 결과 | 특징 |
|---|---|---|
| `parser.parse(output)` | 문자열을 파싱한 `EmailSummary` | LLM 응답을 확인한 뒤 원하는 시점에 파싱 |
| `prompt \| llm \| parser` | 체인 실행 결과인 `EmailSummary` | 생성과 파싱을 하나의 체인으로 연결 |

## 요약

- `BaseModel`과 `Field`로 원하는 출력 스키마를 정의합니다.
- `PydanticOutputParser`가 Pydantic 모델에 맞는 출력 형식 지시사항을 생성합니다.
- `prompt.partial(format=...)`으로 포맷 지시사항을 프롬프트에 고정할 수 있습니다.
- `parser.parse()` 또는 체인 마지막의 `| parser`를 사용해 자연어 응답을 구조화된 객체로 변환합니다.
- 구조화된 결과는 `structured_output.person`처럼 필드 단위로 후속 처리할 수 있습니다.
