# Structured Output과 CommaSeparatedListOutputParser

09/16 실습. [`ch06_02_StructuredOutput_and_CommaSeparatedListParser.ipynb`](ch06_02_StructuredOutput_and_CommaSeparatedListParser.ipynb) — LLM 호출 시 Pydantic 스키마를 직접 바인딩하는 `with_structured_output()`과, 쉼표로 구분된 응답을 Python 리스트로 변환하는 `CommaSeparatedListOutputParser`를 다룹니다.

---

## 1. 실습 내용

이 노트북에서는 구조화된 결과를 얻는 두 가지 방법을 비교합니다.

1. `with_structured_output()`: 모델에 Pydantic 스키마를 직접 연결해 복잡한 구조체를 반환합니다.
2. `CommaSeparatedListOutputParser`: LLM의 쉼표 구분 응답을 `list` 객체로 변환합니다.

`with_structured_output()`은 모델이 지원하는 네이티브 구조화 출력 기능을 사용하므로 별도의 출력 파서를 체인 마지막에 연결하지 않아도 됩니다. 반면 쉼표 구분 리스트 파서는 간단한 목록을 빠르고 적은 토큰으로 처리하는 데 적합합니다.

## 2. 환경 설정과 import

노트북은 `.env` 파일에 저장한 API 키를 `load_dotenv()`로 읽습니다.

```python
from dotenv import load_dotenv

load_dotenv()
```

주요 라이브러리는 다음과 같습니다.

```python
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
```

쉼표 구분 리스트 파서 실습에서는 다음 모듈을 추가로 사용합니다.

```python
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate
```

## 3. `with_structured_output()`으로 스키마 바인딩

### 이메일 스키마 정의

먼저 이메일 요약 결과의 형태를 Pydantic 모델로 선언합니다.

```python
class EmailSummary(BaseModel):
    person: str = Field(description="메일을 보낸 사람")
    email: str = Field(description="메일을 보낸 사람의 이메일 주소")
    subject: str = Field(description="메일 제목")
    summary: str = Field(description="메일 본문을 요약한 텍스트")
    date: str = Field(description="메일 본문에 언급된 미팅 날짜와 시간")
```

이 모델은 결과에 포함되어야 할 필드와 각 필드의 타입, 의미를 정의합니다. 이전 실습의 `PydanticOutputParser`에서는 포맷 지시사항을 프롬프트에 넣고 응답을 다시 파싱했지만, 여기서는 모델 객체에 스키마를 직접 바인딩합니다.

### 모델에 스키마 연결

```python
llm_with_structured = ChatOpenAI(
    temperature=0, model="gpt-4.1-mini"
).with_structured_output(EmailSummary)
```

`with_structured_output(EmailSummary)`는 모델이 `EmailSummary` 형태의 결과를 반환하도록 설정한 새 Runnable을 만듭니다. 노트북에서는 변수 이름을 `llm_with_structered`로 사용하지만, 의미상 `structured`가 올바른 철자입니다.

### 구조화된 응답 받기

```python
answer = llm_with_structured.invoke(email_conversation)
answer
```

이 호출의 결과는 일반 문자열이 아니라 `EmailSummary`에 맞는 구조화된 객체입니다. 예를 들어 다음과 같이 필드에 접근할 수 있습니다.

```python
answer.person
answer.email
answer.subject
answer.summary
answer.date
```

예시 이메일에서는 다음과 같은 정보가 추출됩니다.

```text
person: 김철수
email: chulsoo.kim@bikecorporation.me
subject: "ZENESIS" 자전거 유통 협력 및 미팅 일정 제안
date: 1월 15일 오전 10시
```

### 장점과 활용 분야

- 프롬프트에 복잡한 JSON 형식 지시사항을 직접 작성할 필요가 적습니다.
- 모델이 스키마를 따르도록 강제하므로 일반적인 문자열 파싱보다 파싱 오류가 적습니다.
- 여러 속성을 가진 구조체를 다루는 데 적합합니다.
- 엔티티 추출, API 파라미터 매핑, RAG 결과의 구조화 등에 활용할 수 있습니다.

단, 실제 동작은 사용하는 모델과 LangChain 연동 방식이 구조화 출력을 지원하는지에 따라 달라질 수 있습니다.

## 4. `CommaSeparatedListOutputParser`

간단한 목록이 필요할 때는 `CommaSeparatedListOutputParser`를 사용할 수 있습니다. 이 파서는 LLM이 쉼표로 구분해 반환한 텍스트를 Python 리스트로 변환합니다.

### 파서 초기화와 형식 지시사항 확인

```python
output_parser = CommaSeparatedListOutputParser()
format_instructions = output_parser.get_format_instructions()

print(format_instructions)
```

`get_format_instructions()`는 모델에게 결과를 쉼표로 구분된 목록으로 작성하도록 안내하는 문장을 제공합니다.

### 프롬프트 구성

영어 주제를 대상으로 하는 프롬프트는 다음과 같이 작성합니다.

```python
prompt = PromptTemplate(
    template="List five {subject}.\n{format_instructions}",
    input_variables=["subject"],
    partial_variables={"format_instructions": format_instructions},
)
```

한국어로 요청하는 별도의 프롬프트도 구성합니다.

```python
prompt2 = PromptTemplate(
    template="다섯가지 {subject}.\n{format_instructions}",
    input_variables=["subject"],
    partial_variables={"format_instructions": format_instructions},
)
```

`format_instructions`는 `partial_variables`로 미리 고정했기 때문에 체인을 호출할 때 `subject`만 전달하면 됩니다.

## 5. 리스트 출력 체인 실행

프롬프트, ChatOpenAI, 출력 파서를 순서대로 연결합니다.

```python
model = ChatOpenAI(temperature=0)
chain = prompt | model | output_parser
```

호주의 관광명소 다섯 가지를 요청하면 결과는 문자열이 아닌 리스트로 반환됩니다.

```python
chain.invoke({"subject": "호주 관광명소"})
```

반환 결과의 형태는 다음과 같습니다.

```python
["시드니 오페라 하우스", "그레이트 배리어 리프", "울루루", " ... "]
```

실제 항목과 순서는 모델 응답에 따라 달라질 수 있습니다.

한국어 프롬프트도 같은 방식으로 체인을 구성합니다.

```python
model = ChatOpenAI(temperature=0)
chain2 = prompt2 | model | output_parser

chain2.invoke({"subject": "인도 관광명소"})
```

이 방식은 연관 키워드, 태그, 카테고리 목록처럼 순서가 중요하지 않은 짧은 목록을 만들 때 유용합니다.

## 6. 스트리밍으로 리스트 결과 확인

노트북에서는 대한민국 관광명소 목록을 스트리밍 방식으로도 실행합니다.

```python
for s in chain.stream({"subject": "대한민국 관광명소"}):
    print(s)
```

체인 마지막에 출력 파서가 연결되어 있으므로 스트림에서 반환되는 각 결과는 파싱된 리스트 단위로 전달됩니다. 스트리밍은 결과가 생성되는 과정을 확인하거나 사용자 화면에 단계적으로 표시할 때 사용할 수 있습니다.

## 7. 두 방식 비교

| 방식 | 반환 형태 | 적합한 경우 | 특징 |
|---|---|---|---|
| `with_structured_output(Schema)` | Pydantic 기반 구조화 객체 | 여러 필드를 가진 복잡한 데이터 | 모델에 스키마를 직접 바인딩하고 파싱 작업을 줄임 |
| `CommaSeparatedListOutputParser()` | Python `list` | 키워드, 태그, 간단한 목록 | 토큰 소비가 적고 빠르지만 쉼표 형식에 의존 |

`with_structured_output()`은 이메일 요약처럼 필드별 의미와 타입이 필요한 경우에 적합합니다. `CommaSeparatedListOutputParser`는 관광명소 다섯 가지처럼 단순한 항목 목록을 얻는 경우에 더 간결합니다.

## 요약

- `with_structured_output()`은 Pydantic 모델을 LLM에 직접 연결해 구조화된 결과를 받습니다.
- 구조가 복잡하고 여러 속성을 검증해야 할 때 `with_structured_output()`이 적합합니다.
- `CommaSeparatedListOutputParser`는 쉼표로 구분된 LLM 응답을 Python `list`로 변환합니다.
- `partial_variables`로 공통 포맷 지시사항을 프롬프트에 미리 삽입할 수 있습니다.
- 두 방식 모두 `prompt | model | parser` 형태의 LangChain Runnable 체인으로 구성할 수 있지만, `with_structured_output()`은 모델 바인딩 단계에서 스키마가 적용됩니다.
