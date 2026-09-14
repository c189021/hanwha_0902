# .env로 OpenAI API 키 불러오기

09/14 실습. [`ch03.ipynb`](ch03.ipynb) — `python-dotenv`로 `.env` 파일의 `OPENAI_API_KEY`를
환경변수로 읽어와서 제대로 로드됐는지 확인하는 가장 기본적인 예제입니다.
(같은 방식을 더 자세히 다룬 문서: [`../ex0911/README.md`](../ex0911/README.md))

---

## 코드 흐름

```python
from dotenv import load_dotenv

# .env파일에 설정된 보안정보를 읽기.
load_dotenv()   # -> True (성공 시)
```

```python
import os

print(f"키 값은: {os.environ["OPENAI_API_KEY"][:8]}")
# -> 키 값은: sk-proj-
```

- `load_dotenv()` : 현재 폴더의 [`.env`](.env) 파일을 읽어 `KEY=VALUE` 형태의 값들을 `os.environ`에 등록합니다.
  성공하면 `True`를 반환합니다.
- `os.environ["OPENAI_API_KEY"]` : 등록된 환경변수를 직접 꺼내 씁니다. 키 전체를 출력하면 유출 위험이 있으므로
  `[:8]`로 앞 8자리(`sk-proj-`)만 잘라서 "정상적으로 로드됐는지"만 확인합니다.

## 주의

- `.env`에는 실제 API 키가 들어 있고, 레포 루트의 `.gitignore`에 `.env`가 등록되어 있어 **커밋되지 않습니다.**
- 키를 화면에 출력할 땐 항상 일부만 잘라서 확인하고, 전체 키를 print/커밋하지 않습니다.
