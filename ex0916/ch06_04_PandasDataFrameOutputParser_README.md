# PandasDataFrameOutputParser — DataFrame 질의와 결과 파싱

09/16 실습. [`ch06_04_PandasDataFrameOutputParser.ipynb`](ch06_04_PandasDataFrameOutputParser.ipynb) — LangChain의 `PandasDataFrameOutputParser`를 사용해 자연어 질문을 Pandas DataFrame 연산 형식으로 변환하고, 결과를 Python 객체로 받는 방법을 다룹니다.

---

## 1. Pandas DataFrame 출력 파서란

`PandasDataFrameOutputParser`는 LLM에게 DataFrame의 구조와 사용할 수 있는 연산 형식을 알려준 뒤, 사용자의 질문을 DataFrame 질의로 변환합니다. 파서는 모델이 다음과 같은 형식으로 응답하도록 유도합니다.

- `max:열이름`: 특정 열의 최댓값
- `mean:열이름`: 특정 열의 평균
- `mean:열이름[시작..끝]`: 지정한 행 범위의 평균
- 열 조회 또는 행 조회: DataFrame의 해당 데이터 반환

LLM이 직접 숫자를 계산하도록 맡기는 것이 아니라, DataFrame에 정의된 연산을 사용해 결과를 얻는 것이 핵심입니다.

## 2. 환경 설정과 import

노트북은 필요한 패키지를 설치한 뒤 `.env` 파일의 API 키를 읽습니다.

```python
%pip install -q pandas numpy python-dotenv openai langchain-core langchain-classic langchain-openai langchain-teddynote
```

주요 import는 다음과 같습니다.

```python
import pprint
from typing import Any, Dict

import pandas as pd
from dotenv import load_dotenv
from langchain_classic.output_parsers import PandasDataFrameOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_teddynote import logging
```

환경변수와 LangSmith 로깅을 설정하고 모델을 생성합니다.

```python
load_dotenv()
logging.langsmith("CH03-OutputParser")

model = ChatOpenAI(temperature=0, model="gpt-4.1-mini")
```

`temperature=0`은 같은 질문에 대해 비교적 일정한 형식의 응답을 얻기 위한 설정입니다.

## 3. 간단한 DataFrame으로 최댓값 구하기

먼저 도시별 인구 DataFrame을 생성합니다.

```python
df = pd.DataFrame(
    {
        "도시": ["서울", "부산", "인천", "대구", "대전"],
        "인구": [9500000, 3400000, 3000000, 2500000, 1500000],
    }
)
```

DataFrame을 파서에 전달합니다.

```python
parser = PandasDataFrameOutputParser(dataframe=df)
```

파서가 요구하는 형식을 프롬프트에 포함합니다.

```python
prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    },
)
```

`get_format_instructions()`는 현재 DataFrame의 열과 사용할 수 있는 질의 형식을 안내합니다. 포맷 지시사항은 `partial_variables`로 고정했기 때문에 실행할 때 `query`만 전달하면 됩니다.

### 체인 실행

```python
chain = prompt | model | parser

question = (
    "인구 열의 최댓값을 구하세요. "
    "반드시 정확히 max:인구 형식으로만 답하세요."
)
answer = chain.invoke({"query": question})
pprint.pprint(answer)
```

이 요청은 `인구` 열의 최댓값을 계산하며, 결과는 서울의 인구인 `9500000`에 해당합니다.

## 4. Titanic DataFrame 불러오기

다음으로 노트북에 포함된 Titanic CSV 파일을 읽습니다.

```python
df = pd.read_csv("./data/titanic.csv")
df.head()
```

DataFrame이 바뀌었으므로 새 DataFrame을 파서에 전달합니다.

```python
parser = PandasDataFrameOutputParser(dataframe=df)
print(parser.get_format_instructions())
```

파서는 전달받은 DataFrame의 열 정보를 기준으로 포맷 지시사항을 생성합니다. 따라서 DataFrame을 교체한 뒤에는 파서와 프롬프트의 지시사항도 새 DataFrame에 맞춰 다시 구성해야 합니다.

## 5. Titanic 데이터 질의

### 열 조회

```python
df_query = "Age column을 조회해 주세요."

prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    },
)

chain = prompt | model | parser
parser_output = chain.invoke({"query": df_query})
```

`Age` 열을 요청하면 해당 열의 값이 파싱된 결과로 반환됩니다.

### 첫 번째 행 조회

```python
df_query = "Retrieve the first row."
parser_output = chain.invoke({"query": df_query})
```

첫 번째 행을 요청하면 DataFrame의 인덱스 0에 해당하는 레코드를 반환합니다.

### 특정 행 범위의 평균

먼저 Pandas로 직접 계산하면 다음과 같습니다.

```python
df["age"].head().mean()
```

같은 연산을 파서 체인에 요청할 수 있습니다.

```python
df_query = (
    "Retrieve the average of the age column from row 0 to 4. "
    "반드시 정확히 mean:age[0..4] 형식으로만 답하세요."
)
parser_output = chain.invoke({"query": df_query})
print(parser_output)
```

`mean:age[0..4]`는 `age` 열의 0번부터 4번 행까지 평균을 계산하라는 의미입니다.

### 전체 열의 평균

```python
df_query = (
    "Calculate average 'fare' rate. "
    "반드시 정확히 mean:fare 형식으로만 답하세요."
)
parser_output = chain.invoke({"query": df_query})
print(parser_output)
```

Pandas로 직접 계산하면 다음과 같은 의미입니다.

```python
df["fare"].mean()
```

## 6. 파싱 결과 보기 좋게 출력하기

파서 결과에는 Series나 DataFrame 객체가 포함될 수 있습니다. 노트북에서는 이를 dictionary 형태로 변환해 출력하는 함수를 정의합니다.

```python
def format_parser_output(parser_output: Dict[str, Any]) -> None:
    for key in parser_output.keys():
        parser_output[key] = parser_output[key].to_dict()
    return pprint.PrettyPrinter(width=4, compact=True).pprint(parser_output)
```

사용 예시는 다음과 같습니다.

```python
format_parser_output(parser_output)
```

각 결과 객체의 `.to_dict()`를 호출해 사람이 확인하기 쉬운 형태로 출력합니다. 이 함수는 결과 dictionary를 직접 수정하므로, 원래 파서 결과를 보존해야 한다면 복사본을 전달하는 것이 좋습니다.

## 7. 체인 처리 흐름

```text
사용자 질문
    -> PromptTemplate
    -> ChatOpenAI
    -> PandasDataFrameOutputParser
    -> DataFrame 연산 결과
```

- `PromptTemplate`: DataFrame 정보와 질의 형식을 모델에 안내합니다.
- `ChatOpenAI`: 자연어 질문을 파서가 이해할 수 있는 연산 표현으로 변환합니다.
- `PandasDataFrameOutputParser`: 모델의 결과를 실제 DataFrame 조회·계산 결과로 파싱합니다.

## 8. 사용 가능한 질의 예시

| 질의 형식 | 의미 |
|---|---|
| `max:인구` | `인구` 열의 최댓값 |
| `mean:fare` | `fare` 열 전체의 평균 |
| `mean:age[0..4]` | `age` 열의 0번부터 4번 행까지 평균 |
| `Age column 조회` | `Age` 열 조회 |
| `Retrieve the first row` | 첫 번째 행 조회 |

정확한 질의 형식은 `parser.get_format_instructions()`의 안내를 우선 따라야 합니다. 열 이름의 대소문자와 DataFrame에 실제로 존재하는지 여부도 중요합니다.

## 9. 주의할 점

- 파서에는 반드시 대상 DataFrame을 전달해야 합니다.
- DataFrame을 변경하면 파서와 프롬프트의 포맷 지시사항을 새로 만들어야 합니다.
- 질의에 사용한 열 이름은 실제 DataFrame의 열 이름과 일치해야 합니다.
- LLM이 정해진 형식을 지키지 않으면 파싱 오류가 발생할 수 있으므로, 질의에 `max:열이름`이나 `mean:열이름`처럼 정확한 형식을 명시하는 것이 도움이 됩니다.
- CSV 경로 `./data/titanic.csv`는 노트북의 현재 작업 디렉터리에 따라 달라질 수 있습니다.

## 요약

- `PandasDataFrameOutputParser`는 DataFrame을 기반으로 자연어 질의를 구조화된 연산으로 처리합니다.
- `max:열이름`, `mean:열이름`, `mean:열이름[시작..끝]` 형식으로 최댓값과 평균을 요청할 수 있습니다.
- DataFrame을 교체할 때는 파서와 포맷 지시사항도 함께 갱신해야 합니다.
- Series나 DataFrame 결과는 `.to_dict()`로 변환해 읽기 쉽게 출력할 수 있습니다.
- 데이터 분석용 질의응답 시스템이나 LLM 기반 DataFrame 탐색 기능의 기본 패턴으로 활용할 수 있습니다.
