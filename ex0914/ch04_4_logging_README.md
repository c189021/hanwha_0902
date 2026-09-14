# Python `logging`으로 LLM 호출 과정 기록하기

09/14 실습. [`ch04_4_logging.ipynb`](ch04_4_logging.ipynb) — 멀티모달 LLM 호출 과정을
`print` 대신 Python 표준 라이브러리 **`logging`** 모듈로 파일에 기록하고, 예외(에러) 발생 시에도
원인을 추적할 수 있도록 로그를 남기는 방법을 다룹니다.

---

## 1. 왜 `print` 대신 `logging`을 쓰나요?

- `print`는 화면에만 출력되고, 프로그램이 끝나면 내용이 사라집니다.
- `logging`은 **파일로 저장**되므로, 나중에 "언제, 어떤 요청을 보냈고, 어떤 에러가 났는지"를
  다시 열어 확인할 수 있습니다. 실무에서 문제가 생겼을 때 원인을 추적(디버깅)하는 표준적인 방법입니다.

## 2. 로깅 설정

```python
import logging

logging.basicConfig(
    filename="app.log",             # 저장될 로그 파일 이름
    level=logging.INFO,             # 이 레벨 이상만 기록 (INFO, DEBUG, ERROR 등)
    format="%(asctime)s - %(levelname)s - %(message)s",  # 로그 포맷 (시간 - 레벨 - 메시지)
    encoding="utf-8",               # 한글 깨짐 방지
)

logger = logging.getLogger("MyMultimodalApp")
```

- `filename="app.log"` : 실행한 폴더에 `app.log` 파일이 생기고, 이후 모든 로그가 이 파일에 **추가(append)**됩니다.
- `level=logging.INFO` : 로그 심각도 등급입니다. 낮은 것부터 `DEBUG < INFO < WARNING < ERROR < CRITICAL` 순이며,
  `INFO`로 설정하면 `INFO` 이상(즉 `INFO`, `WARNING`, `ERROR`, `CRITICAL`)만 파일에 기록됩니다.
- `encoding="utf-8"` : 로그에 한글을 쓸 것이므로 인코딩을 명시하지 않으면 깨질 수 있습니다.
- `logging.getLogger("이름")` : 로거(logger)에 이름을 붙여, 어떤 모듈/앱에서 남긴 로그인지 구분할 수 있게 합니다.

## 3. 정상 흐름 기록 — `logger.info(...)`

```python
logger.info("LangSmith 연동 및 애플리케이션 시작2")

multimodal_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = "이미지의 내용을 한국어로 상세히 설명해 주세요."

logger.info(f"요청 전송 - Prompt: {prompt} / Image: {IMAGE_URL}")

answer = multimodal_llm.stream([message])
logger.info("답변 수신 및 스트리밍 시작")
stream_response(answer)
logger.info("답변 처리 완료")
```

주요 단계(시작 → 요청 전송 → 스트리밍 시작 → 처리 완료)마다 `logger.info()`를 남겨서,
`app.log`만 열어봐도 "이 실행이 어디까지 진행됐는지" 순서대로 파악할 수 있습니다.

## 4. 예외 발생 시 기록 — `try / except` + `logger.error(..., exc_info=True)`

```python
try:
    # ... LLM 호출 로직 ...
    ...
except Exception as e:
    logger.error(f"실행 중 에러 발생: {str(e)}", exc_info=True)
```

- 전체 호출 로직을 `try` 블록으로 감싸서, 중간에 어떤 예외(네트워크 오류, API 키 오류 등)가 나더라도
  프로그램이 그냥 죽지 않고 **에러 내용을 로그에 남긴 뒤** 처리를 이어갈 수 있게 합니다.
- `logger.error(메시지, exc_info=True)` : `exc_info=True`를 주면 에러 메시지뿐 아니라
  **전체 스택 트레이스(traceback)**까지 로그 파일에 함께 기록되어, 정확히 어느 줄에서 문제가
  발생했는지 나중에 파일만 보고도 알 수 있습니다.
- 이렇게 "여러 번 실행하면서 로그를 하나씩 확인하고 오류를 고쳐나가는" 방식은 실제 개발에서
  디버깅할 때 자주 쓰는 흐름입니다.

## 참고

- `.env`에서 `OPENAI_API_KEY` 등을 로드하는 방식은 [`ch03_README.md`](ch03_README.md),
  이미지+텍스트 멀티모달 호출 자체는 [`ch04_3_multimodal_README.md`](ch04_3_multimodal_README.md)를 참고하세요.
- 실행할 때마다 `app.log` 파일에 로그가 계속 **누적**되므로, 너무 오래된 로그는 주기적으로 정리하는 것이 좋습니다.
