# DatetimeOutputParser와 EnumOutputParser

09/16 실습. [`ch06_05_Datetime_and_EnumOutputParser.ipynb`](ch06_05_Datetime_and_EnumOutputParser.ipynb) — LLM의 응답을 날짜/시간 객체로 변환하는 `DatetimeOutputParser`와, 미리 정의한 열거형 값 중 하나로 제한하는 `EnumOutputParser`를 다룹니다.

---

## 1. 실습 내용

이 노트북에서는 특정 형식의 응답만 허용해야 할 때 사용하는 두 가지 출력 파서를 살펴봅니다.

- `DatetimeOutputParser`: LLM의 날짜 응답을 Python `datetime` 객체로 변환
- `EnumOutputParser`: LLM의 응답을 정의된 Enum 항목 중 하나로 변환

두 파서 모두 `get_format_instructions()`로 출력 형식 지시사항을 생성하고, 이를 프롬프트에 삽입한 뒤 체인의 마지막에 연결합니다.

## 2. 환경 설정과 import

노트북은 실행에 필요한 패키지를 설치하고 `.env` 파일의 API 키를 읽습니다.

```python
%pip install -q python-dotenv openai langchain-core langchain-classic langchain-openai langchain-teddynote
```

날짜 파서에 필요한 import는 다음과 같습니다.

```python
from langchain_classic.output_parsers import DatetimeOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_teddynote import logging
from dotenv import load_dotenv
```

환경변수와 LangSmith 로깅을 설정합니다.

```python
load_dotenv()
logging.langsmith("CH03-OutputParser")
```

## 3. `DatetimeOutputParser`

### 날짜 파서 생성과 형식 지정

```python
output_parser = DatetimeOutputParser()
output_parser.format = "%Y-%m-%d"
```

`DatetimeOutputParser`는 날짜 응답을 파싱하는 파서입니다. 노트북에서는 `format`을 `%Y-%m-%d`로 지정해 연-월-일 형식만 사용하도록 합니다.

- `%Y`: 네 자리 연도
- `%m`: 두 자리 월
- `%d`: 두 자리 일

파서가 모델에 전달할 출력 형식 지시사항을 확인할 수 있습니다.

```python
print(output_parser.get_format_instructions())
```

### 프롬프트 구성

```python
template = """Answer the users question:

#Format Instructions:
{format_instructions}

#Question:
{question}

#Answer:"""

prompt = PromptTemplate.from_template(
    template,
    partial_variables={
        "format_instructions": output_parser.get_format_instructions()
    },
)
```

`format_instructions`는 `partial_variables`로 미리 채웁니다. 따라서 체인을 실행할 때는 질문만 전달하면 됩니다.

### 날짜 응답 생성 및 파싱

```python
chain = prompt | ChatOpenAI() | output_parser

output = chain.invoke({"question": "구글이 창업한 연도?"})
```

체인의 실행 결과는 일반 문자열이 아니라 Python `datetime` 객체입니다. 날짜만 문자열로 확인하려면 `strftime()`을 사용합니다.

```python
output.strftime("%Y-%m-%d")
```

이 질문의 결과는 모델의 지식과 응답에 따라 달라질 수 있지만, 파싱된 값은 지정한 `YYYY-MM-DD` 형식을 만족해야 합니다. 연도만 질문하더라도 날짜 파서는 날짜 전체를 요구하므로 모델이 월과 일을 함께 반환하도록 형식 지시사항이 적용됩니다.

### 처리 흐름

```text
질문 -> PromptTemplate -> ChatOpenAI -> DatetimeOutputParser -> datetime 객체
```

날짜를 Python 객체로 받으면 날짜 비교, 정렬, 날짜 차이 계산 등 후속 처리를 쉽게 할 수 있습니다.

## 4. `EnumOutputParser`

### Enum 클래스 정의

`Enum`은 허용 가능한 값을 미리 정해 두는 Python 표준 기능입니다.

```python
from enum import Enum

class Colors(Enum):
    RED = "빨간색"
    GREEN = "초록색"
    BLUE = "파란색"
```

Enum 멤버와 실제 값을 각각 확인할 수 있습니다.

```python
Colors.RED
Colors.RED.value
```

- `Colors.RED`: Enum 멤버
- `Colors.RED.value`: 문자열 값인 `"빨간색"`

### Enum 파서 생성

```python
from langchain_classic.output_parsers import EnumOutputParser

parser = EnumOutputParser(enum=Colors)
parser.get_format_instructions()
```

파서는 모델이 `빨간색`, `초록색`, `파란색` 중 하나를 반환하도록 형식 지시사항을 만듭니다. 목록에 없는 색상이 반환되면 파싱에 실패할 수 있습니다.

### 색상 질문 체인 구성

```python
prompt = PromptTemplate.from_template(
    """다음의 물체는 어떤 색깔인가요?

Object: {object}

Instructions: {instructions}"""
).partial(
    instructions=parser.get_format_instructions()
)

chain = prompt | ChatOpenAI() | parser
```

프롬프트의 `object`에 물체를 전달하고, 응답을 Enum 파서로 변환합니다.

```python
response = chain.invoke({"object": "하늘"})
print(response)
```

하늘에 대한 일반적인 답변은 `파란색`이므로, 결과는 `Colors.BLUE`에 해당하는 Enum 값이 될 수 있습니다. 반환 타입은 다음과 같이 확인합니다.

```python
type(response)
response.value
```

`response.value`를 사용하면 실제 문자열인 `"파란색"`을 얻을 수 있습니다.

### 처리 흐름

```text
물체 -> PromptTemplate -> ChatOpenAI -> EnumOutputParser -> Colors Enum 객체
```

Enum 객체로 반환된 결과는 조건문이나 분기 처리에서 안정적으로 사용할 수 있습니다.

```python
if response == Colors.BLUE:
    print("파란색으로 분류되었습니다.")
```

## 5. 두 파서 비교

| 파서 | 출력 형식 | 사용 목적 | 후속 처리 |
|---|---|---|---|
| `DatetimeOutputParser` | Python `datetime` 객체 | 날짜와 시간 형식 통일 | `strftime()`, 날짜 비교, 정렬, 기간 계산 |
| `EnumOutputParser` | Enum 멤버 | 허용된 선택지 중 하나로 제한 | 조건문, 상태 분기, 카테고리 처리 |

두 파서는 자유로운 자연어 응답을 그대로 사용하는 대신, 애플리케이션이 처리하기 쉬운 제한된 형식으로 변환한다는 공통점이 있습니다.

## 6. 주의할 점

- `DatetimeOutputParser.format`과 프롬프트의 포맷 지시사항이 서로 일치해야 합니다.
- 날짜 파서는 날짜로 해석할 수 없는 응답을 받으면 파싱 오류가 발생할 수 있습니다.
- 연도만 필요한 질문에도 `DatetimeOutputParser`는 설정된 전체 날짜 형식을 요구합니다.
- `EnumOutputParser`는 Enum에 정의되지 않은 값이나 표현이 반환되면 파싱하지 못할 수 있습니다.
- 모델 응답의 불필요한 설명을 줄이고, 파서가 요구한 값만 반환하도록 프롬프트에 명시하는 것이 좋습니다.
- 실제 서비스에서는 파싱 오류에 대비한 예외 처리와 재시도 로직을 함께 고려해야 합니다.

## 요약

- `DatetimeOutputParser`는 날짜 문자열을 Python `datetime` 객체로 변환합니다.
- `output_parser.format = "%Y-%m-%d"`로 날짜 출력 형식을 지정할 수 있습니다.
- `EnumOutputParser`는 응답을 미리 정의한 Enum 값 중 하나로 제한합니다.
- 파싱 결과는 `strftime()` 또는 Enum의 `.value`로 원하는 표현으로 변환할 수 있습니다.
- 두 파서는 `get_format_instructions()`와 `prompt | model | parser` 패턴을 사용합니다.
