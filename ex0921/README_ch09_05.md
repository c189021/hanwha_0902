# ch09_05_web_loader.ipynb — WebBaseLoader (웹 페이지 로더)

## 개요
웹 페이지(뉴스 기사, 블로그, 문서 사이트 등)의 내용을 RAG의 지식 소스로 쓰려면 HTML을 가져와 **필요한 본문 텍스트만 추출**해야 합니다. LangChain의 `WebBaseLoader`는 `requests`로 URL의 HTML을 가져오고 `BeautifulSoup(bs4)`으로 파싱해 `Document`로 변환합니다. 이 노트북에서는 네이버 뉴스 기사 1건을 대상으로 다음을 실습합니다.

1. 기본 웹 로더 생성
2. `bs4.SoupStrainer`로 **기사 제목과 본문만** 골라 추출
3. 요청 헤더(User-Agent) 설정
4. SSL 검증, 요청 속도 제한, 프록시 등 네트워크 옵션

## 핵심 개념

### 1. `WebBaseLoader` 기본 사용
```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader(web_paths=("https://n.news.naver.com/article/437/0000378416",))
docs = loader.load()
```
- `web_paths`에 URL을 **튜플/리스트**로 전달합니다. 여러 URL을 넣으면 각각 `Document`가 하나씩 생성됩니다.
- **주의**: 파이썬에서 `("url")`은 튜플이 아니라 단순 문자열입니다. 원소가 1개인 튜플은 **끝에 쉼표**를 붙여 `("url",)`로 써야 합니다. 노트북 첫 번째 셀은 쉼표가 없고, 두 번째 셀은 쉼표를 포함하고 있습니다.
- 결과 `Document`의 `metadata`에는 `source`(URL)가 들어가고, `page_content`에는 페이지에서 추출된 텍스트가 담깁니다.

### 2. 필요한 부분만 추출 — `bs_kwargs` + `SoupStrainer`
```python
import bs4

loader = WebBaseLoader(
    web_paths=("https://n.news.naver.com/article/437/0000378416",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            "div",
            attrs={"class": ["newsct_article _article_body", "media_end_head_title"]},
        )
    ),
)
```
- 웹 페이지 전체를 그대로 가져오면 메뉴, 광고, 댓글, 푸터 등 **본문과 무관한 텍스트가 대량 포함**되어 RAG 품질이 떨어집니다.
- `bs4.SoupStrainer`는 BeautifulSoup이 **파싱할 HTML 요소를 미리 필터링**하는 도구입니다.
  - 첫 인자 `"div"`: 태그 이름
  - `attrs={"class": [...]}`: 해당 클래스를 가진 요소만 선택
- 여기서는 기사 **본문**(`newsct_article _article_body`)과 **제목**(`media_end_head_title`) 영역만 가져오도록 지정했습니다. 그 결과 `page_content`에 기사 제목과 본문만 깔끔하게 담깁니다.
- `bs_kwargs`는 BeautifulSoup 생성자에 전달되는 옵션이며, 사이트마다 HTML 구조가 다르므로 **브라우저 개발자 도구(F12)로 원하는 요소의 태그/클래스를 확인**해 지정해야 합니다.

### 3. 요청 헤더 설정 — `header_template`
```python
header_template={
    "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ... Chrome/102.0.0.0 Safari/537.36",
},
```
- 많은 웹사이트가 봇(스크립트) 요청을 차단하므로, **일반 브라우저처럼 보이는 `User-Agent` 헤더**를 함께 보내면 차단을 피하는 데 도움이 됩니다.
- (참고: HTTP 표준 헤더명은 하이픈을 쓰는 `User-Agent`입니다.)

### 4. 네트워크 관련 옵션
```python
loader.requests_kwargs = {"verify": True}   # SSL 인증서 검증 관련 옵션
```
- `requests_kwargs`는 내부 `requests.get()`에 전달할 추가 인자입니다. `verify`는 SSL 인증서 검증 여부를 지정합니다. (주석은 "SSL 인증 우회"라고 되어 있지만 `True`는 오히려 **검증을 수행**하는 설정이며, 검증을 끄려면 `False`를 지정합니다. 보안상 `False`는 꼭 필요할 때만 사용해야 합니다.)

```python
import nest_asyncio
nest_asyncio.apply()

loader.requests_per_second = 1   # 초당 요청 수 제한
docs = loader.load()
```
- `WebBaseLoader`는 여러 URL을 **비동기(asyncio)** 로 병렬 요청합니다. Jupyter 노트북은 이미 이벤트 루프가 실행 중이라 충돌이 나므로, **`nest_asyncio.apply()`로 중첩 이벤트 루프를 허용**해야 합니다. (일반 `.py` 스크립트에서는 불필요)
- `requests_per_second`로 **초당 요청 수를 제한**해 서버에 과도한 부하를 주지 않고 차단당할 가능성도 줄입니다.

### 5. 프록시 설정 (주석 처리된 예시)
```python
loader = WebBaseLoader(
    "https://www.google.com/search?q=parrots",
    proxies={
        "http": "http://{username}:{password}:@proxy.service.com:6666/",
        "https": "http://{username}:{password}:@proxy.service.com:6666/",
    },
)
```
- **프록시(Proxy)** 는 클라이언트와 서버 사이에서 요청을 중계하는 서버로, 보안·익명성·캐싱 등의 역할을 합니다.
- IP 차단을 우회하거나 사내망에서 외부 접속이 프록시를 통해서만 가능한 경우 `proxies` 인자로 지정합니다.

## 코드 흐름 요약
1. `WebBaseLoader`로 네이버 뉴스 URL을 지정해 기본 로더 생성
2. `bs4.SoupStrainer`로 기사 제목/본문 영역만 파싱하도록 `bs_kwargs` 설정, `header_template`으로 User-Agent 지정
3. `loader.load()`로 로드 → `Document` 1개(기사 1건), `metadata`에는 `source`(URL) 확인
4. `requests_kwargs`(SSL 검증), `nest_asyncio` + `requests_per_second`(요청 속도)로 네트워크 옵션 조정
5. 프록시 사용 예시 확인 (주석 처리)

## 알아두면 좋은 점
- **웹 크롤링 시 유의사항**: 대상 사이트의 **이용약관과 `robots.txt`** 를 확인하고, 저작권과 서비스 부하를 고려해 사용해야 합니다. 이 실습의 뉴스 본문도 저작물이므로 학습/개인 용도에 한정하는 것이 바람직합니다.
- `WebBaseLoader`는 **정적 HTML**만 가져옵니다. JavaScript로 동적으로 렌더링되는 페이지는 내용이 비어 보일 수 있으며, 이 경우 Selenium/Playwright 기반 로더(`SeleniumURLLoader`, `PlaywrightURLLoader`)를 사용해야 합니다.
- 사이트 HTML 구조가 바뀌면 지정한 클래스명이 사라져 **빈 문서**가 반환될 수 있으므로, 로드 후 `page_content` 길이를 확인하는 습관이 필요합니다.
- 여러 URL을 리스트로 전달하면 `load()` 한 번으로 여러 페이지를 수집할 수 있고, 이때 `requests_per_second` 설정이 특히 중요해집니다.
