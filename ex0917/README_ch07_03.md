# ch07_03_HuggingFace엔드포인트.ipynb — Hugging Face Endpoint 사용하기

## 개요
지금까지는 OpenAI(`ChatOpenAI`)를 사용했지만, 이 노트북에서는 **Hugging Face Hub**에 호스팅된 오픈소스/서드파티 LLM을 LangChain에서 호출하는 방법을 다룹니다. `HuggingFaceEndpoint`와 `ChatHuggingFace`를 조합해 Hugging Face의 Inference 엔드포인트를 Chat 모델처럼 사용합니다.

## 핵심 개념

### 1. Hugging Face Hub 로그인
```python
from huggingface_hub import login
login(os.environ.get("HUGGINGFACEHUB_API_TOKEN"))
```
- Hugging Face Hub의 모델/추론 API를 사용하려면 계정의 **Access Token**이 필요합니다.
- `.env` 파일에 `HUGGINGFACEHUB_API_TOKEN`을 저장해두고 `load_dotenv()`로 불러와 사용합니다.
- `login()`을 호출하면 이후 Hugging Face 관련 라이브러리 호출 시 별도로 토큰을 넘기지 않아도 인증된 세션을 사용할 수 있습니다.

### 2. 채팅 템플릿 형식의 프롬프트
```python
template = """<|system|>
Your are a helpful assistant.s<|end|>
<|user|>
{question}<|end|>
<|assistant|>"""
```
- OpenAI Chat API는 `system`/`user`/`assistant` 역할을 별도 파라미터로 구분하지만, 많은 오픈소스 LLM(특히 Phi, Llama 계열)은 **특수 토큰이 포함된 텍스트 템플릿**으로 대화 역할을 표현합니다.
- `<|system|>`, `<|user|>`, `<|assistant|>`, `<|end|>` 같은 토큰은 모델이 학습될 때 사용한 채팅 포맷(chat template)에 맞춰 작성해야 모델이 역할을 올바르게 구분합니다. 모델마다 요구하는 특수 토큰 형식이 다르므로, 사용하려는 모델의 문서를 확인해야 합니다.
- (참고: 노트북에는 오타로 보이는 `assistant.s`가 있는데, 실제 사용 시에는 `You are a helpful assistant.` 형태로 수정하는 것이 바람직합니다.)

### 3. `HuggingFaceEndpoint` — 텍스트 생성 엔드포인트 래퍼
```python
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    provider="auto",
    repo_id="openai/gpt-oss-120b",
    max_new_tokens=256,
    temperature=0.1,
    huggingfacehub_api_token=os.environ.get("HUGGINGFACEHUB_API_TOKEN"),
)
```
| 파라미터 | 의미 |
|---|---|
| `provider="auto"` | Hugging Face Inference Providers 중 사용 가능한 곳을 자동으로 선택 (여러 회사가 동일 모델을 서빙할 수 있음) |
| `repo_id` | Hugging Face Hub 상의 모델 저장소 ID (예: `openai/gpt-oss-120b`) |
| `max_new_tokens` | 응답으로 생성할 최대 토큰 수 (입력 토큰 제외, 새로 생성되는 부분만 카운트) |
| `temperature` | 생성 다양성 조절 (0에 가까울수록 결정적/일관된 답변) |
| `huggingfacehub_api_token` | 인증용 API 토큰 |

`HuggingFaceEndpoint`는 원시 텍스트 생성(completion) 인터페이스에 가깝습니다.

### 4. `ChatHuggingFace` — Chat 모델 인터페이스로 감싸기
```python
chat_llm = ChatHuggingFace(llm=llm)
```
- `HuggingFaceEndpoint`를 `ChatHuggingFace`로 한 번 더 감싸면, `ChatOpenAI`와 유사하게 **Chat 모델 인터페이스**(메시지 기반 입출력, 채팅 템플릿 자동 적용 등)로 사용할 수 있습니다.
- 즉, 앞선 노트북들에서 `ChatOpenAI`를 사용하던 자리에 그대로 `chat_llm`을 넣어도 동일한 LCEL 체인 문법(`prompt | llm | parser`)을 사용할 수 있습니다.

### 5. 체인 구성과 출력 파싱
```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | chat_llm | StrOutputParser()
response = chain.invoke({"question": "What is the capital of South korea?"})
print(response)
```
- `StrOutputParser`는 LLM의 응답 객체(AIMessage 등)에서 순수 문자열(`content`)만 추출해주는 출력 파서입니다.
- 이전 노트북들에서는 `response.content`로 직접 접근했지만, 여기서는 체인 끝에 파서를 붙여 곧바로 문자열 결과를 얻습니다.
- 결과: `"The capital of South Korea is **Seoul**."`

## 코드 흐름 요약
1. `.env`에서 Hugging Face API 토큰을 로드하고 `login()`으로 인증
2. 특수 토큰 기반 채팅 템플릿(`<|system|>`, `<|user|>`, `<|assistant|>`)으로 `PromptTemplate` 생성
3. `HuggingFaceEndpoint`로 원격 모델(`openai/gpt-oss-120b`) 연결 설정
4. `ChatHuggingFace`로 감싸 Chat 인터페이스화
5. `prompt | chat_llm | StrOutputParser()` LCEL 체인 구성 후 질의 실행

## 알아두면 좋은 점
- **OpenAI vs Hugging Face 사용법 차이**: `ChatOpenAI`는 역할(system/user)을 메시지 객체로 자동 처리하지만, `HuggingFaceEndpoint` 기반 모델은 모델별 채팅 템플릿 문자열을 직접(혹은 토크나이저의 `apply_chat_template`을 통해) 맞춰줘야 하는 경우가 많습니다. `ChatHuggingFace`가 이 변환을 도와주지만, 프롬프트 템플릿 자체는 사용자가 모델에 맞게 작성해야 할 수 있습니다.
- `provider="auto"`처럼 Hugging Face Inference Providers를 활용하면 특정 회사의 인프라에 종속되지 않고 여러 제공자 중 가용한 곳으로 라우팅할 수 있습니다.
- 오픈소스 모델은 모델마다 지원하는 파라미터, 컨텍스트 길이, 채팅 포맷이 다르므로, 새로운 `repo_id`로 교체할 때는 반드시 해당 모델 카드(model card) 문서를 확인해야 합니다.
