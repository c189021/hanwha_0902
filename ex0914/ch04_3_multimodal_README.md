# 멀티모달(Multimodal) — 이미지 + 텍스트로 GPT-4o-mini 질의하기

09/14 실습. [`ch04_3_multimodal.ipynb`](ch04_3_multimodal.ipynb) — 텍스트뿐 아니라 **이미지**를
함께 넣어 모델에게 질의하는 멀티모달(multimodal) 호출을 다룹니다. `langchain_teddynote`가 제공하는
`MultiModal` 헬퍼와, 직접 구현한 이미지 질의 함수 두 가지 방식을 비교합니다.

---

## 1. 멀티모달이란?

지금까지는 텍스트만 모델에 넣었지만, `gpt-4o-mini`처럼 **비전(vision)을 지원하는 모델**은
이미지를 함께 입력받아 "이 이미지를 설명해줘", "이 표를 분석해줘" 같은 질의에 답할 수 있습니다.
이미지와 텍스트를 함께 다루기 때문에 **멀티모달(multimodal, 다중 형식)** 모델이라고 부릅니다.

## 2. 방법 ① — `langchain_teddynote`의 `MultiModal` 헬퍼

```python
from langchain_teddynote.models import MultiModal
from langchain_teddynote.messages import stream_response
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0.1, model_name="gpt-4o-mini")
multimodal_llm = MultiModal(llm)   # 기존 llm 객체를 멀티모달 질의용으로 감싸줌

IMAGE_URL = "https://.../table_image.jpg"

answer = multimodal_llm.stream(IMAGE_URL)   # 이미지 URL만 넘기면 기본 프롬프트로 질의
stream_response(answer)                     # 스트리밍 결과를 화면에 출력
```

- `MultiModal(llm)` : 일반 `ChatOpenAI` 객체를 멀티모달 질의가 가능한 형태로 감싸는 래퍼(wrapper)입니다.
- `multimodal_llm.stream(이미지주소)` : 이미지 URL(또는 로컬 경로)만 넘기면 내부적으로 기본 시스템/사용자
  프롬프트를 구성해서 질의합니다. 가장 간단하게 "이 이미지 설명해줘" 류의 질의를 할 때 편리합니다.
- `stream_response(answer)` : 스트리밍 제너레이터를 받아 토큰을 이어붙여 화면에 출력해주는 유틸 함수입니다.

## 3. 방법 ② — 직접 만든 이미지 질의 함수 (프롬프트를 세밀하게 제어)

`MultiModal`은 편리하지만 시스템/사용자 프롬프트를 세밀하게 바꾸기 어려울 수 있어서,
`HumanMessage`/`SystemMessage`를 직접 구성하는 함수도 함께 구현합니다.

```python
import base64
from pathlib import Path
from langchain_core.messages import HumanMessage, SystemMessage

def image_url(image_source):
    """로컬 이미지 경로는 base64 data URL로 변환하고, http(s) URL은 그대로 반환."""
    if str(image_source).startswith(("http://", "https://")):
        return str(image_source)
    image_path = Path(image_source)
    mime_type = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
    encoded_image = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_image}"

def stream_image_response(image_source, user_prompt, system_prompt=None):
    content = [
        {"type": "text", "text": user_prompt},
        {"type": "image_url", "image_url": {"url": image_url(image_source)}},
    ]
    messages = [HumanMessage(content=content)]
    if system_prompt:
        messages.insert(0, SystemMessage(content=system_prompt))

    for token in llm.stream(messages):
        print(token.content, end="", flush=True)
```

- **이미지를 모델에 넘기는 두 가지 방법**
  1. **웹 URL 그대로 전달** — `https://...jpg` 형태면 모델이 직접 그 주소에서 이미지를 가져옵니다.
  2. **로컬 파일 → base64 data URL 변환** — 내 PC에 있는 이미지는 인터넷 주소가 없으므로,
     파일을 읽어(`read_bytes()`) `base64`로 인코딩한 뒤 `data:image/png;base64,...` 형식의
     "데이터 URL"로 바꿔서 전달해야 합니다. 이 함수는 두 경우를 자동으로 구분해서 처리합니다.
- **메시지 구조** : `HumanMessage(content=[...])`의 `content`는 문자열이 아니라
  `[{"type": "text", ...}, {"type": "image_url", ...}]` 형태의 **리스트**로 구성합니다.
  하나의 메시지 안에 텍스트 블록과 이미지 블록을 함께 담을 수 있다는 뜻입니다.
- **시스템 프롬프트로 역할 부여** : 아래처럼 `system_prompt`를 지정하면 모델에게 "어떤 역할로,
  어떤 관점에서 답할지"를 미리 지시할 수 있습니다.

```python
system_prompt = """당신은 표(재무제표) 를 해석하는 금융 AI 어시스턴트 입니다.
당신의 임무는 주어진 테이블 형식의 재무제표를 바탕으로 흥미로운 사실을 정리하여 친절하게 답변하는 것입니다."""

user_prompt = """당신에게 주어진 표는 회사의 재무제표 입니다. 흥미로운 사실을 정리하여 답변하세요."""

stream_image_response(IMAGE_PATH_FROM_FILE, user_prompt, system_prompt)
```

위 예제는 재무제표 이미지를 넣고 "금융 AI 어시스턴트" 역할을 부여해, 유동자산·현금성자산 증감 같은
수치를 비교·분석한 답변을 스트리밍으로 받는 과정을 보여줍니다.

## 참고 — 실행 로그에 보이는 LangSmith 연결 오류

노트북 출력에 `Failed to get info from https://eu.api.langchain.com ...` 같은 에러 메시지가 보이는데,
이는 **LangSmith 트레이싱 전송이 실패했다는 경고**일 뿐이며 모델 응답 자체와는 무관합니다.
`.env`의 `LANGSMITH_ENDPOINT`가 실제 접속 가능한 주소와 다르게 설정되어 있거나 네트워크가 막혀 있을 때
나타나며, 무시해도 GPT 응답은 정상적으로 출력됩니다. ([`ch04_2_langsmith_README.md`](ch04_2_langsmith_README.md) 참고)
