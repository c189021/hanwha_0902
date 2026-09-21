# ch09_03_hwp_loader.ipynb — HWP 로더 (커스텀 Document Loader 만들기)

## 개요
HWP(한글 문서)는 국내 공공기관·기업에서 매우 널리 쓰이지만, PDF처럼 널리 지원되는 표준 로더가 LangChain에 내장되어 있지 않습니다. 이 노트북에서는 `BaseLoader`를 상속해 **HWP 5.x 파일에서 본문 텍스트를 추출하는 커스텀 로더(`HWPLoader`)를 직접 구현**하고, 실제 HWP 파일(`디지털정부혁신 추진계획.hwp`)을 로드해 봅니다.

이를 통해 "지원하지 않는 문서 형식은 **직접 로더를 만들어 `Document`로 변환**하면 된다"는 LangChain 로더의 확장 구조를 이해할 수 있습니다.

## 핵심 개념

### 1. 커스텀 로더의 뼈대 — `BaseLoader` 상속
```python
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

class HWPLoader(BaseLoader):
    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)

    def lazy_load(self) -> Iterator[Document]:
        ...
        yield Document(page_content=..., metadata=...)
```
- `BaseLoader`를 상속하고 **`lazy_load()` 메서드만 구현**하면, `load()`, `load_and_split()`, `aload()` 등은 부모 클래스가 자동으로 제공합니다.
- `lazy_load()`는 `yield`로 `Document`를 하나씩 반환하는 **제너레이터**입니다. (ch09_01에서 다룬 지연 로딩과 같은 원리)
- 즉, 어떤 문서 형식이든 "**파일을 읽어 → `Document(page_content, metadata)`로 만들어 yield**"만 구현하면 LangChain 생태계에 바로 연결됩니다.

### 2. HWP 파일의 구조 — OLE 복합 문서
- HWP 5.x 파일은 내부적으로 **OLE(Object Linking and Embedding) 복합 문서 포맷**이며, 하나의 파일 안에 여러 "스트림(stream)"이 폴더처럼 들어 있습니다.
- 이를 읽기 위해 **`olefile`** 라이브러리를 사용합니다. (`uv add olefile`)

| 스트림 | 역할 |
|---|---|
| `FileHeader` | 파일 시그니처와 속성(압축 여부 등)이 담긴 헤더 |
| `\x05HwpSummaryInformation` | 문서 요약 정보 |
| `BodyText/Section0`, `Section1` … | 실제 본문이 담긴 **섹션 스트림들** |

### 3. `HWPLoader`의 동작 단계

**(1) 유효한 HWP 파일인지 검증 — `_is_valid_hwp()`**
```python
streams = {"/".join(item) for item in ole.listdir()}
return self.FILE_HEADER in streams and self.HWP_SUMMARY in streams
```
- 파일 안에 `FileHeader`와 `HwpSummaryInformation` 스트림이 모두 있는지 확인해 HWP 파일이 맞는지 검증하고, 아니면 `ValueError`를 발생시킵니다.

**(2) 압축 여부 확인 — `_is_compressed()`**
```python
header = ole.openstream("FileHeader").read()
return bool(header[36] & 1)
```
- `FileHeader`의 36번째 바이트의 최하위 비트가 **본문 압축 여부 플래그**입니다.

**(3) 섹션 스트림 정렬**
```python
sections = sorted(
    (item for item in ole.listdir() if item[0] == "BodyText"),
    key=lambda item: int(item[1][len("Section"):]),
)
```
- `BodyText` 하위의 `Section0`, `Section1`, ... 스트림을 **숫자 순서대로** 정렬합니다. (문자열 정렬 시 `Section10`이 `Section2`보다 앞서는 문제를 막기 위해 숫자로 변환)

**(4) 압축 해제 — `zlib.decompress(data, -15)`**
- 압축된 섹션 데이터는 **raw deflate 방식**이므로, `wbits=-15` 옵션(헤더 없는 raw deflate)으로 압축을 해제해야 합니다.

**(5) 레코드 파싱 및 텍스트 추출 — `_extract_text()`**
```python
header = struct.unpack_from("<I", section, position)[0]
record_type   = header & 0x3FF          # 하위 10비트: 태그(레코드 종류) ID
record_length = (header >> 20) & 0xFFF  # 상위 12비트: 데이터 길이
```
- HWP 본문은 **레코드(record)의 연속**으로 저장되어 있고, 각 레코드는 4바이트 헤더 + 데이터로 구성됩니다.
  - 헤더 하위 10비트 = 레코드 타입, 상위 12비트 = 데이터 길이
  - 길이가 `0xFFF`이면 실제 길이는 **뒤따르는 추가 4바이트**에 저장됩니다(확장 길이).
- 여러 레코드 중 **`HWPTAG_PARA_TEXT`(태그 ID = 67)** 레코드만 문단 텍스트를 담고 있으므로, 이것만 골라 **UTF-16 Little Endian**으로 디코딩합니다.
```python
text = payload.decode("utf-16-le", errors="ignore")
text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)   # 제어 문자 제거
```
- 정규식으로 화면에 출력되지 않는 제어 문자를 제거하고, 문단들을 `"\n"`으로 이어 붙입니다.

**(6) `Document`로 반환**
```python
yield Document(
    page_content=self._extract_text(data),
    metadata={"source": str(self.file_path), "section": section_number},
)
```
- **섹션 하나당 `Document` 하나**가 만들어지며, `metadata`에는 파일 경로와 섹션 번호를 담습니다. (PDF 로더처럼 "페이지" 단위가 아니라 "섹션" 단위)

### 4. 실행 결과 해석
```python
loader = HWPLoader("./data/디지털정부혁신 추진계획.hwp")
documents = loader.load()
print(f"섹션 수: {len(documents)}")   # 1
```
- 이 문서는 섹션이 1개뿐이라 `Document`가 **1개**만 생성됩니다. (문서 전체가 하나의 `Document`)
- 출력 앞부분에 `捤獥汤捯湰灧桤灧`, `氠瑢桤灧` 같은 **깨진 한자 형태의 문자열**이 보이는데, 이는 HWP 내부의 **컨트롤 문자(표, 구역 정의 등 확장 제어 코드)** 가 텍스트 레코드에 섞여 있기 때문입니다. 정규식으로 일부 제어 문자를 제거했지만 완벽히 걸러지지는 않은 부분이며, 본문 텍스트(예: "디지털 정부혁신 추진계획", "Ⅰ. 개 요" 등)는 정상 추출됩니다.
- 이 문서는 하나의 `Document`가 매우 길기 때문에, 실제 RAG에서는 반드시 **텍스트 스플리터로 청크 분할**한 후 사용해야 합니다.

## 코드 흐름 요약
1. `olefile` 설치 및 필요한 모듈(`struct`, `zlib`, `re`, `olefile`, `BaseLoader`, `Document`) import
2. `BaseLoader`를 상속한 `HWPLoader` 클래스 정의 (검증 → 압축 확인 → 섹션 정렬 → 압축 해제 → 레코드 파싱 → `Document` 생성)
3. `HWPLoader("./data/디지털정부혁신 추진계획.hwp").load()`로 실제 HWP 파일 로드
4. 섹션 수와 추출된 본문 텍스트 일부를 출력해 확인

## 알아두면 좋은 점
- **커스텀 로더 작성의 핵심**은 (a) `BaseLoader` 상속, (b) `lazy_load()` 구현, (c) `Document(page_content, metadata)`로 `yield` 이 세 가지입니다. 어떤 포맷이든 이 패턴으로 확장할 수 있습니다.
- 위 구현은 **HWP 5.x(바이너리) 형식**만 지원합니다. 최신 한글의 **HWPX**(XML 기반 zip 포맷)는 구조가 달라 별도 처리가 필요합니다.
- 직접 만든 파서는 표, 이미지, 각주 같은 복잡한 요소를 완벽히 처리하지 못할 수 있으므로, 실무에서는 커뮤니티 라이브러리(`langchain-teddynote`, `pyhwp` 기반 로더 등)나 HWP → PDF/텍스트 변환 후 로드하는 방식도 함께 고려할 수 있습니다.
- 추출 결과에 섞인 깨진 문자는 RAG 품질을 떨어뜨릴 수 있으므로, 로드 후 **후처리(불필요 문자 제거 정규식 등)** 를 추가하면 좋습니다.
