# YAMLPrompt — YAML 파일로 프롬프트 템플릿 관리하기

09/15 실습. [`ch05_03_YAMLPrompt.ipynb`](ch05_03_YAMLPrompt.ipynb) — [`ch05_01_PromptTemplate_README.md`](ch05_01_PromptTemplate_README.md)에서
파이썬 코드로 직접 만들던 `PromptTemplate`을, 별도의 **YAML 파일로 분리 저장**하고 `load_prompt()`로
불러오는 방법을 다룹니다.

---

## 1. 왜 프롬프트를 YAML로 분리할까

프롬프트 템플릿을 파이썬 코드 안에 문자열로 박아 두면, 프롬프트 내용을 조금 수정할 때마다 코드를
건드려야 하고, 여러 노트북/스크립트에서 같은 프롬프트를 재사용하기도 번거롭습니다. 템플릿을 `.yaml`
파일로 따로 관리하면

- 프롬프트만 따로 버전 관리(git diff)하기 쉽고,
- 코드 수정 없이 프롬프트 파일만 교체해서 실험할 수 있고,
- 프롬프트가 길어져도(특히 여러 줄 지시문) 코드 가독성이 떨어지지 않습니다.

## 2. 기본 예제 — `prompts/fruit_color.yaml`

```yaml
_type: "prompt"
template: "{fruit}의 색깔이 뭐야?"
input_variables: ["fruit"]
```

- `_type: "prompt"`는 이 YAML이 `PromptTemplate`으로 로드되어야 함을 나타내는 식별자입니다.
- `template`은 `ch05_01`에서 다룬 것과 동일한, `{fruit}` 같은 변수 자리표시자를 포함한 템플릿 문자열입니다.
- `input_variables`는 `PromptTemplate`을 생성자로 직접 만들 때 넘기던 것과 동일한 변수 목록입니다.

```python
from langchain_core.prompts import load_prompt

prompt = load_prompt("prompts/fruit_color.yaml", encoding="utf-8")
prompt
# -> PromptTemplate(input_variables=['fruit'], ..., template='{fruit}의 색깔이 뭐야?')

prompt.format(fruit="사과")
# -> '사과의 색깔이 뭐야?'
```

- `load_prompt(경로)`는 YAML 파일을 읽어 `PromptTemplate.from_template()`으로 만든 것과 동일한 객체를
  반환합니다. 이후 `.format()`, `prompt | llm` 체인 연결 등은 지금까지와 완전히 동일하게 사용합니다.
- 한글이 포함된 YAML 파일이므로 `encoding="utf-8"`을 명시해야 인코딩 오류 없이 로드됩니다.

## 3. 여러 줄(멀티라인) 템플릿 — `prompts/capital.yaml`

지시문이 길어지면 YAML의 블록 스칼라 문법(`|`)을 사용해 여러 줄로 작성할 수 있습니다.

```yaml
_type: "prompt"
template: |
    {country}의 수도에 대해서 알려주세요.
    수도의 특징을 다음의 양식에 맞게 정리해 주세요.
    300자 내외로 작성해 주세요.
    한글로 작성해 주세요.
    ----
    [양식]
    1. 면적
    2. 인구
    3. 역사적 장소
    4. 특산품
        #Answer:
input_variables: ["country"]
```

- `template: |` 뒤에 들여쓰기된 줄바꿈 포함 텍스트는 **줄바꿈이 그대로 유지된 하나의 문자열**로
  파싱됩니다. 파이썬 코드에서 `"""...."""` 삼중따옴표 문자열을 쓰는 것과 같은 효과를, 프롬프트를
  코드 밖(YAML 파일)에 둔 채로 얻을 수 있습니다.
- 답변의 형식(면적/인구/역사적 장소/특산품 4개 항목)을 프롬프트 안에 명시해 LLM 출력 구조를 유도하는
  전형적인 "출력 양식 지정" 패턴입니다.

```python
prompt2 = load_prompt("prompts/capital.yaml", encoding="utf-8")
print(prompt2.format(country="대한민국"))
```
```
대한민국의 수도에 대해서 알려주세요.
수도의 특징을 다음의 양식에 맞게 정리해 주세요.
...
```

## 4. 체인 연결 및 스트리밍 출력

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_teddynote.messages import stream_response

chain = prompt2 | ChatOpenAI(model_name="gpt-4o-mini", temperature=0) | StrOutputParser()

answer = chain.stream({"country": "대한민국"})
stream_response(answer)
```
```
1. 면적: 서울특별시는 약 605.21㎢의 면적을 가지고 있습니다.
2. 인구: 2023년 기준으로 서울의 인구는 약 9백만 명에 달합니다.
3. 역사적 장소: 경복궁, 창덕궁, 남산, 종묘 등 다양한 역사적 장소가 있어 한국의 전통과 문화를 체험할 수 있습니다.
4. 특산품: 서울의 특산품으로는 한방차, 전통주, 그리고 다양한 길거리 음식들이 유명합니다. ...
```

- YAML에서 불러온 `prompt2`도 일반 `PromptTemplate`과 동일하게 `prompt2 | llm | StrOutputParser()`
  형태로 체인을 구성할 수 있습니다. 체인 실행 방식(`stream`, `invoke`, `batch`)에 대한 설명은
  [`ch04_7_runmethods_README.md`](../ex0914/ch04_7_runmethods_README.md)를 참고하세요.
- `model_name="gpt-4o-mini", temperature=0`으로 모델과 창의성(temperature)을 지정해, 출력이
  매번 비슷한 형식을 유지하도록 했습니다. `temperature=0`은 같은 입력에 대해 가장 결정적(deterministic)인
  응답을 생성하도록 유도합니다.
- `stream_response()`는 `langchain_teddynote` 패키지에서 제공하는 헬퍼로, `chain.stream()`이 돌려주는
  토큰 스트림을 받아 화면에 실시간으로 이어 출력해 줍니다.

## 요약

| 구성 요소 | 역할 |
|---|---|
| `_type: "prompt"` | YAML이 프롬프트 템플릿임을 나타내는 식별자 |
| `template` | `{변수}` 자리표시자를 포함한 프롬프트 문자열 (`|`로 여러 줄 작성 가능) |
| `input_variables` | 템플릿에 필요한 변수 목록 |
| `load_prompt(path, encoding="utf-8")` | YAML 파일을 읽어 `PromptTemplate` 객체로 반환 |
