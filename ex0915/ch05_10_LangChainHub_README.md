# LangChain Hub — 프롬프트를 내려받고 공유하기

09/15 실습. [`ch05_10_LangChainHub.ipynb`](ch05_10_LangChainHub.ipynb) — 지금까지는 `ch05_01`~`09`에서 프롬프트를
**직접 코드/YAML로 작성**했습니다. 이번에는 다른 사람이 이미 만들어 검증해 둔 프롬프트를 **LangChain
Hub(LangSmith 프롬프트 저장소)**에서 가져오고, 반대로 내가 만든 프롬프트를 업로드해 공유하는 방법을
다룹니다.

---

## 1. LangChain Hub란

LangChain Hub는 LangSmith가 제공하는 **프롬프트 저장/공유 플랫폼**입니다. `owner/repo` 형식의
이름으로 프롬프트를 등록해 두면, 누구나(공개 프롬프트의 경우) `pull_prompt()`로 해당 프롬프트를
코드에 바로 가져다 쓸 수 있습니다. 매번 프롬프트를 처음부터 작성하는 대신, RAG용 프롬프트처럼
이미 검증된 프롬프트를 재사용할 수 있다는 점이 장점입니다.

## 2. `pull_prompt()` — 공개 프롬프트 가져오기

```python
from langsmith import Client

client = Client()

# 가장 최신 버전의 프롬프트를 가져옵니다.
# 공개(public) 프롬프트를 가져올 때는 신뢰할 수 있는 프롬프트인지 명시적으로 동의해야 합니다.
prompt = client.pull_prompt("rlm/rag-prompt", dangerously_pull_public_prompt=True)
print(prompt)
```
```
input_variables=['context', 'question'] ... messages=[HumanMessagePromptTemplate(prompt=PromptTemplate(
    input_variables=['context', 'question'],
    template="You are an assistant for question-answering tasks. Use the following pieces of retrieved context
    to answer the question. If you don't know the answer, just say that you don't know. Use three sentences
    maximum and keep the answer concise.\nQuestion: {question} \nContext: {context} \nAnswer:"
))]
```

- `client.pull_prompt("owner/repo")`처럼 **"소유자/저장소" 이름**으로 프롬프트를 조회합니다.
  `"rlm/rag-prompt"`는 RAG(검색 증강 생성)용으로 널리 쓰이는 공개 프롬프트로, `context`와 `question`
  두 변수를 받아 "문맥을 참고해 세 문장 이내로 간결하게 답하라"는 지시를 담고 있습니다.
- 불러온 결과는 지금까지 다뤄온 `ChatPromptTemplate`과 동일한 객체이므로, `ch05_04`~`09`에서 배운
  방식 그대로 `prompt | llm` 체인 구성이나 `.format()` 호출에 바로 사용할 수 있습니다.
- `dangerously_pull_public_prompt=True`는 **다른 사람이 올린 공개 프롬프트**를 그대로 내 코드에서
  실행하게 된다는 것을 인지하고 동의한다는 표시입니다. 이름에 "dangerously"가 붙은 이유는, 출처가
  검증되지 않은 프롬프트를 무심코 가져다 쓰면 의도하지 않은 지시(프롬프트 인젝션 등)가 섞여 있을
  위험이 있기 때문입니다. 신뢰할 수 있는 프롬프트인지 확인한 뒤 사용해야 합니다.

## 3. 특정 버전(commit hash) 지정해서 가져오기

```python
prompt = client.pull_prompt("rlm/rag-prompt:50442af1", dangerously_pull_public_prompt=True)
prompt
```
```
ChatPromptTemplate(..., metadata={'lc_hub_owner': 'rlm', 'lc_hub_repo': 'rag-prompt',
'lc_hub_commit_hash': '50442af133e61576e74536c6556cefe1fac147cad032f4377b60c436e6cdcb6e'}, ...)
```

- `"rlm/rag-prompt"` 뒤에 `:50442af1`처럼 **커밋 해시(버전 식별자)**를 붙이면, 저장소의 최신 버전이
  아니라 **그 시점에 고정된 특정 버전**을 가져옵니다. 게시자가 프롬프트를 나중에 수정하더라도, 내
  코드는 처음 검증했던 그 버전 그대로 동작하도록 고정할 수 있습니다.
- 반환된 객체의 `metadata`에 `lc_hub_owner`, `lc_hub_repo`, `lc_hub_commit_hash`가 함께 담겨 있어,
  이 프롬프트가 어디서(누가 만든 어떤 저장소의 어떤 버전) 왔는지 추적할 수 있습니다.

## 4. 내 프롬프트를 만들어 업로드하기 — `push_prompt()`

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
    "주어진 내용을 바탕으로 다음 문장을 요약하세요. 답변은 반드시 한글로 작성하세요\n\nCONTEXT: {context}\n\nSUMMARY:"
)
```

- `ch05_04`에서 배운 것과 동일하게 `ChatPromptTemplate.from_template()`으로 평범한 프롬프트를 만듭니다.
  `{context}`를 받아 한글로 요약하도록 지시하는 프롬프트입니다.

```python
client.push_prompt("simple-summary-korean", object=prompt)  # 내 워크스페이스에 프롬프트 업로드
# -> 'https://smith.langchain.com/prompts/simple-summary-korean/de93adb6?organizationId=...'
```

- `client.push_prompt(이름, object=prompt)`는 로컬에서 만든 `ChatPromptTemplate` 객체를 내 LangSmith
  워크스페이스에 `"simple-summary-korean"`이라는 이름으로 업로드합니다.
- 반환값은 업로드된 프롬프트를 확인할 수 있는 **LangSmith 웹 UI 링크**입니다. 이후 다른 프로젝트나
  팀원이 `client.pull_prompt("내계정/simple-summary-korean")`처럼 같은 방식으로 이 프롬프트를 가져다
  쓸 수 있습니다.
- `pull_prompt`가 "완성된 공개 프롬프트를 가져다 쓰는 것"이라면, `push_prompt`는 그 반대로
  **내가 만든 프롬프트를 남들도 재사용할 수 있게 등록하는 것**입니다.

## 요약

| 함수 | 방향 | 역할 |
|---|---|---|
| `client.pull_prompt("owner/repo")` | 다운로드 | 최신 버전의 공개/내 프롬프트를 `ChatPromptTemplate`으로 가져옴 |
| `client.pull_prompt("owner/repo:commit_hash")` | 다운로드 | 특정 버전으로 고정해서 가져옴 |
| `dangerously_pull_public_prompt=True` | - | 검증되지 않은 공개 프롬프트를 가져온다는 것에 대한 명시적 동의 |
| `client.push_prompt(name, object=prompt)` | 업로드 | 내가 만든 프롬프트를 내 워크스페이스에 등록/공유 |

`pull_prompt`로 받아온 프롬프트든 `push_prompt`로 올리기 전 직접 만든 프롬프트든, 결과 객체는
`ch05_01`~`09`에서 다룬 `PromptTemplate`/`ChatPromptTemplate`과 동일하게 체인(`prompt | llm`)에
그대로 연결해 사용할 수 있습니다.
