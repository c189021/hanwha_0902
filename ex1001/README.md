# ex1001

LangChain / LangGraph 학습용 예제 프로젝트입니다. 교재 페이지 번호(86, 95, 99, 100, 101)별로 파일을 나누어 실습 코드를 정리했습니다.

## 요구 사항

- Python 3.12 이상
- [uv](https://docs.astral.sh/uv/) 패키지 매니저 (권장)
- 주요 의존성: `langchain-openai`, `langgraph`, `pandas`, `python-dotenv`

## 설치 및 실행

```bash
# uv 사용 (권장)
uv sync
uv run ex1001

# 또는 pip 사용
pip install -r requirements.txt
python -c "from ex1001 import main; main()"   # src 경로가 설치되어 있어야 함
```

### 환경 변수

프로젝트 루트에 `.env` 파일을 만들고 API 키를 넣습니다. `.env`는 `.gitignore`에 포함되어 있어 커밋되지 않습니다.

```env
OPENAI_API_KEY=...
LANGSMITH_TRACING=...
LANGSMITH_ENDPOINT=...
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=...
HUGGINGFACEHUB_API_TOKEN=...
UPSTAGE_API_KEY=...
PINECONE_API_KEY=...
```

## 프로젝트 구조

```
ex1001/
├── pyproject.toml          # 프로젝트 설정 및 의존성, 실행 스크립트(ex1001)
├── requirements.txt        # pip 용 고정 버전 의존성 목록
├── pre-requirements.txt    # 핵심 패키지 이름만 적은 목록
├── test.py                 # 단순 출력 테스트
└── src/ex1001/
    ├── __init__.py         # 패키지 진입점, main 노출
    ├── app.py              # main(): 각 페이지 예제를 순서대로 실행
    ├── page86.py           # ChatOpenAI 번역 예제 (현재 더미 데이터)
    ├── page95.py           # TypedDict 와 딕셔너리 언패킹
    ├── page99.py           # 리듀서와 add_messages
    ├── page100.py          # add_messages 를 사용하는 State 정의
    └── page101.py          # StateGraph 로 챗봇 그래프 구성
```

## 파일별 설명

### `__init__.py`
`app.main`을 가져와 `__all__`로 노출합니다. 패키지가 import 될 때 `"프로젝트 초기화 init"`을 출력합니다.

### `app.py`
`main()` 함수가 각 페이지 예제를 순서대로 실행합니다.

1. `page86_ai_msg()` 함수를 호출합니다.
2. `page95`, `page99`, `page101`은 내부에 함수가 없는 스크립트형 모듈이라, `import` 하는 순간 파일 전체가 실행됩니다.

`sub()`는 메인에서 호출하는 서브 함수 예시이며 현재는 호출되지 않습니다.

### `page86.py`
`ChatOpenAI`(gpt-4o)로 한국어를 영어로 번역하는 예제입니다. 실제 호출 코드는 주석 처리되어 있고, 현재는 `"더미 데이터"` 문자열을 출력해 API 호출 없이 동작합니다.

### `page95.py`
- `TypedDict`를 상속한 `User` 클래스(`id`, `name`, `email`)를 정의합니다.
- `user1`~`user3`을 만들어 필드를 출력합니다.
- 97쪽 내용으로, 딕셔너리 `user_data`를 `User(**user_data)`로 언패킹해 `user4`를 만듭니다.

### `page99.py`
LangGraph 상태 관리의 핵심인 **리듀서(reducer)** 를 다룹니다.

- 직접 만든 `add(left, right)` 리듀서를 `Annotated[list[str], add]`로 `State`에 지정합니다.
- `add_messages`로 `HumanMessage`와 `AIMessage` 리스트를 병합합니다.
- **메시지 `id`가 같으면 기존 메시지를 덮어씁니다.** (`id=3`인 메시지 두 개를 병합하면 뒤의 것만 남음)

### `page100.py`
`messages: Annotated[list[AnyMessage], add_messages]` 형태의 `State`를 정의합니다. 에이전트가 주고받는 메시지를 저장하는 표준 상태 형태입니다.

### `page101.py`
`StateGraph`로 가장 단순한 챗봇 그래프를 만듭니다.

- `chatbot` 노드는 입력 메시지를 받아 `"사용자 입력을 그대로 반환하는 챗봇입니다. ..."` 형태의 문자열을 `messages`에 추가합니다.
- 그래프 흐름은 `START → chatbot → END` 입니다.
- `graph.compile()` 후 `draw_mermaid()`로 구조를 Mermaid 문법으로 출력합니다.
- 그래프 실행(`invoke`) 부분은 아직 작성되지 않았습니다.

> 참고: `page100`에서 `State`를 import 하지만 같은 파일에서 `State`를 다시 정의하므로 import 한 것은 사용되지 않습니다.

### `test.py`
`"test"`를 출력하는 단순 테스트 파일입니다.
