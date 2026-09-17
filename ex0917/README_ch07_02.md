# ch07_02_체인직렬화와역직렬화.ipynb — 직렬화와 역직렬화로 모델 저장 및 로드하기

## 개요
LangChain으로 만든 체인(Runnable)은 파이썬 객체이기 때문에, 특정 파일 확장자로 곧바로 저장하기 어렵습니다. 이 노트북에서는 체인을 **직렬화(serialize)** 하여 딕셔너리/JSON 문자열 형태로 변환한 뒤, 이를 파일(Pickle, JSON)로 저장하고 다시 **역직렬화(deserialize)** 하여 체인 객체로 복원하는 방법을 다룹니다.

## 핵심 개념

### 1. 직렬화(Serialization)란?
객체(체인, 프롬프트, LLM 설정 등)를 다른 시스템에 저장하거나 전송할 수 있는 형태(딕셔너리, JSON, 바이트 등)로 변환하는 과정입니다. 역직렬화는 그 반대로, 저장된 형태를 다시 원래의 객체로 복원하는 과정입니다.

**왜 필요한가?**
- 체인을 코드로 다시 작성하지 않고 파일에서 불러와 재사용
- 설정(모델명, temperature, 프롬프트 템플릿 등)을 버전 관리하거나 배포
- 서버 간에 체인 구성을 전달

### 2. 직렬화 가능 여부 확인 — `is_lc_serializable()`
```python
ChatOpenAI.is_lc_serializable()   # 클래스 자체가 직렬화를 지원하는지
llm.is_lc_serializable()          # 인스턴스도 동일하게 지원
chain.is_lc_serializable()        # 체인(RunnableSequence) 전체도 직렬화 가능
```
LangChain의 컴포넌트(프롬프트, LLM, 체인 등)는 각자 직렬화 지원 여부를 표시하며, `True`인 경우에만 아래의 `dumpd`/`dumps`로 안전하게 변환할 수 있습니다.

### 3. `dumpd()` vs `dumps()`
| 함수 | 반환 타입 | 용도 |
|---|---|---|
| `dumpd(chain)` | `dict` | 체인을 딕셔너리로 변환 (Python 객체로 다루기 편함, Pickle 저장에 적합) |
| `dumps(chain)` | `str` (JSON) | 체인을 JSON 문자열로 변환 (파일 저장, 네트워크 전송에 적합) |

직렬화된 결과에는 다음 정보가 포함됩니다.
```python
{
  "lc": 1,
  "type": "constructor",
  "id": ["langchain", "schema", "runnable", "RunnableSequence"],
  "kwargs": {
    "first": {...PromptTemplate 설정...},
    "last": {...ChatOpenAI 설정...}
  }
}
```
- `id`: 원래 클래스의 모듈 경로 (역직렬화 시 이 경로로 클래스를 다시 찾음)
- `kwargs`: 객체를 생성할 때 필요한 생성자 인자들 (예: `model_name`, `temperature`, `template`)

### 4. API 키(Secret) 처리 방식
```python
"openai_api_key": {"lc": 1, "type": "secret", "id": ["OPENAI_API_KEY"]}
```
API 키처럼 민감한 값은 실제 값이 아니라 **환경 변수 이름에 대한 참조**만 저장됩니다. 즉, 직렬화된 JSON/Pickle 파일 안에는 실제 키 값이 노출되지 않습니다. 역직렬화 시 `secrets_map` 인자로 실제 값을 다시 주입해야 합니다.

### 5. 파일로 저장하기 — Pickle과 JSON
```python
import pickle
with open("fruit_chain.pkl", "wb") as f:
    pickle.dump(dumpd_chain, f)   # 딕셔너리를 바이너리(Pickle)로 저장

import json
with open("fruit_chain.json", "w") as fp:
    json.dump(dumpd_chain, fp)    # 딕셔너리를 JSON 텍스트로 저장
```
- **Pickle**: 파이썬 전용 바이너리 포맷. 파이썬 환경 밖에서는 호환되지 않음
- **JSON**: 언어 독립적 텍스트 포맷. 사람이 읽을 수 있고 다른 시스템과도 호환 가능

### 6. 파일에서 불러와 체인 복원하기 — `load()`
```python
from langchain_core.load import load

with open("fruit_chain.pkl", "rb") as f:
    loaded_chain = pickle.load(f)          # 1) 파일 → 딕셔너리

chain_from_file = load(loaded_chain, allowed_objects="all")  # 2) 딕셔너리 → 체인 객체
chain_from_file.invoke({"fruit": "사과"})
```
- `load()`는 딕셔너리 형태의 직렬화 데이터를 실제 LangChain 객체(Runnable)로 복원합니다.
- **`allowed_objects="all"`**: 보안상 기본적으로 LangChain은 신뢰할 수 없는 데이터를 역직렬화할 때 제한을 둡니다. 이 옵션으로 모든 객체 타입의 역직렬화를 허용합니다. (신뢰할 수 없는 외부 파일을 로드할 때는 주의 필요)
- **`secrets_map`**: API 키처럼 참조로만 저장된 값을 실제로 채워 넣을 때 사용합니다.
```python
load_chain = load(
    loaded_chain,
    secrets_map={"OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY")},
    allowed_objects="all",
)
```

### 7. JSON 파일에서 복원하는 흐름
```python
with open("fruit_chain.json", "r") as fp:
    loaded_chain_json = json.load(fp)              # JSON 텍스트 → 딕셔너리
    loads_chain = load(loaded_chain_json, allowed_objects="all")  # 딕셔너리 → 체인

loads_chain.invoke({"fruit": "사과"})
```
Pickle이든 JSON이든, 최종적으로 `load()` 함수에 **딕셔너리**를 넘겨 체인 객체로 복원한다는 점은 동일합니다.

## 코드 흐름 요약
1. 프롬프트(`PromptTemplate`) + LLM(`ChatOpenAI`)으로 체인 생성
2. 각 구성요소의 직렬화 가능 여부(`is_lc_serializable`) 확인
3. `dumpd()`로 체인을 딕셔너리로, `dumps()`로 JSON 문자열로 직렬화
4. 직렬화된 결과를 `fruit_chain.pkl`(Pickle)과 `fruit_chain.json`(JSON) 파일로 저장
5. 저장된 파일을 다시 읽어 `load()`로 체인 객체 복원
6. 복원된 체인을 `invoke()`로 실행하여 정상 동작 확인 (API 키를 `secrets_map`으로 주입)

## 알아두면 좋은 점
- 직렬화된 파일에는 **API 키 원본 값이 포함되지 않으므로**, 이 파일을 안전하게 형상관리(Git 등)에 올릴 수 있습니다. 단, 역직렬화할 때는 반드시 환경 변수 등을 통해 실제 키를 다시 공급해야 합니다.
- `allowed_objects="all"`은 편의를 위한 옵션이지만, 출처가 불분명한 직렬화 파일을 로드할 때는 임의 코드 실행과 유사한 보안 위험이 있을 수 있으므로 신뢰할 수 있는 파일에만 사용해야 합니다.
- 커스텀 클래스(사용자가 직접 만든 Runnable 등)는 기본적으로 직렬화가 지원되지 않을 수 있으며, 이 경우 `is_lc_serializable()`이 `False`를 반환합니다.
