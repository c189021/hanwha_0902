# OpenAI API 키 연결 + LangChain 맛보기

09/11 실습. **OpenAI API 키를 발급받아 코드에서 안전하게 읽어오는 3가지 방법**을 비교하고,
**LangChain**으로 OpenAI 모델을 호출하는 기본 예제를 다룹니다.

- 원본 API로 호출: [`keytest.py`](keytest.py), [`test.ipynb`](test.ipynb)
- LangChain으로 호출: [`page90.ipynb`](page90.ipynb)
- 패키지 목록: [`requirements.txt`](requirements.txt)

---

## ⚠️ API 키 보안 — 가장 먼저 읽으세요

OpenAI API 키는 **비밀번호와 같습니다.** 유출되면 다른 사람이 내 계정으로 과금을 발생시킬 수 있습니다.

- 이 폴더의 `.env` 파일에는 **실제 키**가 들어 있습니다. `.gitignore`에 `.env`가 등록되어 있어 **커밋되지 않습니다.** (직접 확인: `git status`에 `.env`가 안 보이면 정상)
- 키를 공유해야 할 땐 실제 키 대신 [`.env.example`](.env.example) 처럼 **형식만 보여주는 파일**을 커밋합니다.
- 키가 실수로 깃허브에 올라갔다면 **즉시 OpenAI 대시보드에서 키를 폐기(revoke)하고 재발급**해야 합니다. (지운다고 히스토리에서 완전히 사라지지 않기 때문)

---

## 1. (코랩) GPT API 키 발급받아서 연결하기

1. <https://platform.openai.com/api-keys> 접속 → 로그인 → **Create new secret key** → 키 복사
   (키는 생성 시 **한 번만** 전체가 보이므로 안전한 곳에 복사해 둡니다.)
2. 결제 수단 등록 필요 (OpenAI는 사용량만큼 과금되는 유료 API)
3. **Google Colab**에서 쓰는 경우 — 코랩은 `.env` 파일 대신 **Secrets(비밀키) 기능**을 씁니다.
   - 코랩 왼쪽 사이드바 🔑(열쇠) 아이콘 → **Add new secret**
   - 이름: `OPENAI_API_KEY`, 값: 발급받은 키 → 저장 + 노트북 접근 허용(토글 ON)
   - 코드에서 꺼내 쓰기:
     ```python
     from google.colab import userdata
     import os

     os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")

     from openai import OpenAI
     client = OpenAI()   # 환경변수(OPENAI_API_KEY)를 자동으로 읽음
     ```
   - Colab Secrets는 노트북 파일 자체에는 저장되지 않고 계정에 저장되므로, `.ipynb`를 공유/커밋해도 키가 노출되지 않습니다. (로컬의 `.env`와 같은 역할)

---

## 2. API 키를 코드에서 읽는 3가지 방법

`OpenAI()` 클라이언트는 인자를 안 주면 기본적으로 **환경변수 `OPENAI_API_KEY`** 를 찾습니다.
"환경변수에 값을 넣는 방법"이 곧 아래 3가지입니다. **① 은 실무 금지, ② 를 기본으로 사용, ③ 은 대안**입니다.

### ① 하드코딩 — 코드 파일에 키를 직접 문자열로 작성 (❌ 하지 말 것)

```python
from openai import OpenAI

client = OpenAI(api_key="sk-proj-xxxxxxxxxxxxxxxx")   # 절대 금지
```

- 코드를 Git에 커밋하거나 남에게 보여주는 순간 **키가 그대로 노출**됩니다.
- `.gitignore`로도 못 막습니다. (소스 코드 자체가 커밋 대상이라서)
- **이 실습에서 다루는 이유는 "왜 하면 안 되는지" 보여주기 위함**이며, 실제로 이렇게 짠 파일은 없습니다.

### ② `.env` 파일 + `python-dotenv` (기본 권장) — [`keytest.py`](keytest.py)

키를 코드가 아닌 **별도 파일(`.env`)에 두고**, 실행할 때만 환경변수로 불러옵니다.

```env
# .env  (이 폴더에 이미 있음. 커밋 대상 아님)
OPENAI_API_KEY=sk-proj-...
```

```python
# keytest.py
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()                # .env 파일을 읽어서 os.environ 에 등록
client = OpenAI()            # OPENAI_API_KEY 를 환경변수에서 자동으로 읽음

response = client.responses.create(
    model="gpt-5-mini",
    input="API 키 연결 테스트입니다. '정상 연결' 이라고만 답해주세요.",
)
print(response.output_text)  # -> 정상 연결
```

- `load_dotenv()` 가 `.env` 파일의 `KEY=VALUE` 줄들을 읽어 `os.environ` 에 넣어줍니다.
- **`.env` 는 반드시 `.gitignore`에 등록** (이 레포는 이미 되어 있음). 대신 값이 빈 `.env.example` 을 커밋해서 "이런 키가 필요하다"는 걸 알려줍니다.
- 프로젝트/폴더마다 다른 키를 쓸 수 있어 실습 환경에 적합합니다.

### ③ 데스크탑(OS) 전역 환경변수에 등록해서 읽기 — [`test.ipynb`](test.ipynb)

`.env` 파일도 없이 `client = OpenAI()` 만 호출해도 동작한다면, **운영체제(윈도우) 시스템 환경변수**에
`OPENAI_API_KEY` 가 이미 등록되어 있기 때문입니다. `test.ipynb` 가 이 방식입니다. (`load_dotenv()` 호출이 없음)

```python
from openai import OpenAI

client = OpenAI()            # .env 없이도, OS 환경변수에 키가 있으면 그대로 읽힘
response = client.responses.create(model="gpt-5-mini", input="...")
```

**Windows에 등록하는 방법 (한 번만 설정하면 모든 프로젝트에서 재사용됨):**

1. 시작 메뉴 → "환경 변수" 검색 → **시스템 환경 변수 편집**
2. **환경 변수(N)...** 버튼 → 사용자 변수(또는 시스템 변수)에서 **새로 만들기**
3. 변수 이름: `OPENAI_API_KEY`, 변수 값: 발급받은 키 → 확인
4. **터미널/VSCode를 완전히 재시작**해야 새 환경변수가 적용됩니다.

또는 PowerShell에서 한 번만:

```powershell
setx OPENAI_API_KEY "sk-proj-..."
```

| 방법 | 장점 | 단점 |
|---|---|---|
| ① 하드코딩 | 없음 | **키 유출 위험, 절대 금지** |
| ② `.env` + `python-dotenv` | 프로젝트별로 키를 다르게 관리, 협업 시 `.env.example`로 형식 공유 가능 | 매 프로젝트마다 `.env` 파일을 만들어야 함 |
| ③ OS 전역 환경변수 | 한 번 설정하면 모든 프로젝트에서 재사용, `.env` 파일 자체가 없어도 됨 | PC를 바꾸면 다시 설정해야 함, 여러 키를 프로젝트별로 구분해 쓰기 불편 |

---

## 3. `requirements.txt` 명령어로 만들기

가상환경에 설치한 패키지 목록을 파일로 저장해두면, 다른 사람(또는 미래의 나)이 같은 환경을 그대로 복원할 수 있습니다.

```cmd
:: 1) 현재 활성화된 가상환경에 설치된 패키지 전부를 requirements.txt 로 저장
pip freeze > requirements.txt

:: 2) 나중에 새 가상환경에서 그대로 설치(복원)할 때
pip install -r requirements.txt
```

- `pip freeze` 는 `패키지명==버전` 형식으로 **현재 설치된 모든 패키지**를 출력합니다.
- 이 폴더의 [`requirements.txt`](requirements.txt) 에는 `openai`, `python-dotenv`, `langchain-openai`, `langchain-core` 등이 포함되어 있습니다.
- 팀원에게 코드를 넘길 때 가상환경 폴더(`.venv`)는 절대 같이 안 넘기고(용량 큼, OS마다 다름), **`requirements.txt` 파일만** 넘깁니다.

---

## 4. LangChain 이란?

**LangChain**은 OpenAI 같은 LLM(거대 언어 모델)을 **애플리케이션에 쉽게 연결·조합**하도록 도와주는 파이썬 프레임워크입니다.

- OpenAI SDK를 직접 쓰면(`client.responses.create(...)`) 모델 호출마다 API 형식이 다를 수 있고, 프롬프트 템플릿·대화 기록·문서 검색(RAG)·에이전트 같은 기능을 전부 직접 만들어야 합니다.
- LangChain은 **모델을 하나의 공통 인터페이스(`invoke()`)로 감싸서**, OpenAI/Anthropic/Google 등 **어떤 LLM 제공사든 코드를 거의 안 바꾸고 교체**할 수 있게 해주고, 프롬프트·체인·메모리·도구 연결 같은 부품들을 표준화해 제공합니다.

### 기본 예제 — [`page90.ipynb`](page90.ipynb)

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    temperature=0.1,     # 0에 가까울수록 항상 비슷한(결정적) 답변, 높을수록 다양/창의적인 답변
    model="gpt-4o-mini",
)

question = "대한민국의 수도는 어디인가요?"
print(f"[답변]: {llm.invoke(question)}")
```

```text
[답변]: content='대한민국의 수도는 서울입니다.' additional_kwargs={...} response_metadata={...} ...
```

- `ChatOpenAI(...)` : OpenAI 채팅 모델을 LangChain 방식으로 감싼 객체. **키는 여기서도 환경변수(`OPENAI_API_KEY`)를 자동으로 읽습니다** — `.env`(② 방식)나 시스템 환경변수(③ 방식)가 미리 준비되어 있어야 합니다.
- `llm.invoke(질문)` : 모델을 호출하는 **공통 메서드**. 어떤 LLM으로 바꿔도(`ChatAnthropic`, `ChatGoogleGenerativeAI` 등) 이 메서드 이름은 그대로입니다.
- 반환값은 문자열이 아니라 **`AIMessage` 객체**입니다. 실제 답변 텍스트만 쓰려면 `.content` 를 꺼냅니다.
  ```python
  result = llm.invoke(question)
  print(result.content)   # -> 대한민국의 수도는 서울입니다.
  ```
- `response_metadata` 안에 토큰 사용량(`token_usage`), 실제 사용된 모델명 등 부가 정보가 함께 담겨 옵니다.

> 순수 OpenAI SDK(`client.responses.create`, `keytest.py`/`test.ipynb`)와 LangChain(`llm.invoke`, `page90.ipynb`)은
> **같은 OpenAI 모델을 호출**하지만, LangChain 쪽이 "다른 모델로 갈아끼우기 쉬운 공통 형태"라는 점이 핵심 차이입니다.

---

## 5. 설치 및 실행

```cmd
:: 1. 폴더 이동
cd ex0911

:: 2. 가상환경 생성 & 활성화
python -m venv .venv
.venv\Scripts\activate.bat
:: PowerShell 이면  .venv\Scripts\Activate.ps1

:: 3. 패키지 설치 (이미 만들어둔 목록으로 그대로 복원)
pip install -r requirements.txt

:: 4. .env 파일 준비 (① 방식 사용 시)
copy .env.example .env
:: .env 파일을 열어 OPENAI_API_KEY 값을 실제 발급받은 키로 교체

:: 5. 실행
python keytest.py
:: 또는 test.ipynb / page90.ipynb 를 VSCode/Jupyter 에서 셀 단위로 실행
```

### 파일 요약

| 파일 | 방식 | 내용 |
|---|---|---|
| [`keytest.py`](keytest.py) | `.env` + `load_dotenv()` | OpenAI SDK로 연결 테스트 (`responses.create`) |
| [`test.ipynb`](test.ipynb) | OS 전역 환경변수 (`load_dotenv()` 없음) | 동일한 연결 테스트, 응답 객체(`Response`) 전체 구조 확인 |
| [`page90.ipynb`](page90.ipynb) | 환경변수 자동 인식 | LangChain `ChatOpenAI` 로 질의응답 |
| [`requirements.txt`](requirements.txt) | - | `pip freeze` 로 생성한 패키지 목록 |
| [`.env.example`](.env.example) | - | 실제 키가 없는 템플릿 (커밋 대상) |
| `.env` | - | 실제 키 (커밋 **안 됨**, `.gitignore`) |
