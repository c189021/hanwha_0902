# 출력 파서(Output Parser) — `prompt | model | output_parser`

09/14 실습. [`ch04_6_outputparser.ipynb`](ch04_6_outputparser.ipynb) — [`ch04_5_lcel_README.md`](ch04_5_lcel_README.md)의
`prompt | model` 체인에 **출력 파서(Output Parser)**를 이어 붙여, 모델 응답을 원하는 형태로 가공하는 방법을 다룹니다.

---

## 1. 출력 파서가 왜 필요한가?

[`ch04_5_lcel_README.md`](ch04_5_lcel_README.md)에서 `chain = prompt | model`로 호출하면
결과는 `AIMessage` **객체**였고, 실제 텍스트만 쓰려면 매번 `.content`를 꺼내야 했습니다.

```python
chain = prompt | model
chain.invoke(input)  # -> AIMessage(content="...", ...)  (객체 전체)
```

**출력 파서**는 이 마지막 단계를 체인 안에 넣어서, "모델 응답에서 필요한 형태만 뽑아내는" 후처리 단계를
자동화해 줍니다. 즉 `model`이 반환한 결과를 다시 받아서 **원하는 형태로 변환**하는 컴포넌트입니다.

## 2. `StrOutputParser` — 문자열만 바로 받기

```python
from langchain_core.output_parsers import StrOutputParser

output_parser = StrOutputParser()

chain = prompt | model | output_parser

chain.invoke({"topic": "인공지능 모델의 학습 원리"})
# -> '인공지능 모델의 학습 원리는 데이터를 입력으로 받아서 패턴을 학습하는 과정입니다...'  (문자열 그대로!)
```

- `StrOutputParser()` : `AIMessage` 객체에서 `.content`(문자열)만 뽑아내는 가장 기본적인 파서입니다.
- 체인 끝에 `| output_parser`만 추가하면, `chain.invoke(...)`의 반환값이 객체가 아니라
  **바로 사용 가능한 문자열**이 됩니다. `.content`를 따로 꺼낼 필요가 없어집니다.
- `chain.stream(...)`에도 그대로 적용되어, 스트리밍 토큰도 파서를 거쳐 나옵니다.

## 3. 여러 줄 템플릿 + 출력 형식(FORMAT) 지정하기

프롬프트 템플릿은 한 줄일 필요가 없습니다. 아래처럼 **역할, 상황, 출력 형식**을 자세히 지정하면
모델이 정해진 포맷에 맞춰 답하도록 유도할 수 있습니다.

```python
template = """
당신은 영어를 가르치는 10년차 영어 선생님입니다. 주어진 상황에 맞는 영어 회화를 작성해 주세요.
양식은 [FORMAT]을 참고하여 작성해 주세요.

#상황:
{question}

#FORMAT:
- 영어 회화:
- 한글 해석:
"""

prompt = PromptTemplate.from_template(template)
model = ChatOpenAI(model_name="gpt-4o-mini")
output_parser = StrOutputParser()

chain = prompt | model | output_parser
```

- `{question}` 자리에 실제 상황("식당에서 음식 주문", "미국에서 피자 주문" 등)을 넣으면,
  모델이 `#FORMAT`에 명시된 "영어 회화 / 한글 해석" 두 섹션 구조를 그대로 따라 답합니다.
- 이렇게 **역할(페르소나) + 출력 형식**을 프롬프트에 명시하는 패턴은 응답의 일관성을 높이는 데 자주 쓰입니다.

```python
chain.invoke({"question": "저는 식당에 가서 음식을 주문하고 싶어요"})
# -> '- 영어 회화:\nA: Hello! Welcome to our restaurant. ...\n- 한글 해석:\nA: 안녕하세요! ...'
```

```python
from langchain_teddynote.messages import stream_response

answer = chain.stream({"question": "미국에서 피자 주문"})
stream_response(answer)
```

## 참고 — 실행 로그에 보이는 LangSmith 연결 오류

`Failed to get info from https://eu.api.langchain.com ...` 류의 경고는 LangSmith 트레이싱 전송
실패일 뿐, 체인 실행/모델 응답 자체와는 무관합니다. 자세한 내용은
[`ch04_2_langsmith_README.md`](ch04_2_langsmith_README.md)를 참고하세요.
