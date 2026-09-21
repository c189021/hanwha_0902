# ch09_04_csv_loader.ipynb — CSV 로더

## 개요
CSV는 표 형태의 정형 데이터를 담는 대표적인 포맷입니다. LangChain의 `CSVLoader`는 CSV 파일의 **각 행(row)을 하나의 `Document`로 변환**해 줍니다. 이 노트북에서는 타이타닉 승객 데이터(`titanic.csv`, 891행)를 로드해 행 단위 `Document`의 구조와 메타데이터를 확인합니다.

> 노트북 제목은 "CSV 로더와 데이터프레임 로더"이지만, 실제 실습 코드는 `CSVLoader` 부분만 포함되어 있습니다. (데이터프레임 로더는 아래 "알아두면 좋은 점"에 개념만 정리)

## 핵심 개념

### 1. `CSVLoader` — 행 단위 Document 변환
```python
from langchain_community.document_loaders.csv_loader import CSVLoader

loader = CSVLoader("./data/titanic.csv")
docs = loader.load()

print(len(docs))   # 891
```
- CSV의 **헤더(첫 줄)를 제외한 각 행이 하나의 `Document`** 가 됩니다. 타이타닉 데이터는 승객 891명 → `Document` 891개입니다.
- PDF 로더가 "페이지 = Document"였다면, CSV 로더는 "**행 = Document**"라는 점이 다릅니다.

### 2. `page_content` 구조 — "컬럼명: 값" 텍스트
```
PassengerId: 1
Survived: 0
Pclass: 3
Name: Braund, Mr. Owen Harris
Sex: male
Age: 22
...
Cabin:
Embarked: S
```
- 각 행이 **`컬럼명: 값`을 줄바꿈으로 이어 붙인 문자열**로 변환됩니다.
- 컬럼명이 값과 함께 텍스트에 포함되므로, LLM이 각 값이 무엇을 의미하는지 **문맥적으로 이해**할 수 있습니다. (임베딩/검색 시에도 "Sex: female" 같은 의미 단위가 살아 있음)
- 값이 비어 있는 컬럼(예: 결측치 `Cabin`)은 `Cabin: ` 처럼 **빈 값으로 표시**됩니다.

### 3. `metadata` 구조
```python
print(docs[0].metadata)
# {'source': './data/titanic.csv', 'row': 0}
```
| 키 | 의미 |
|---|---|
| `source` | 원본 CSV 파일 경로 |
| `row` | 행 번호 (**0부터 시작**, 헤더 제외) |

- `row` 값을 통해 검색 결과가 원본 CSV의 몇 번째 행에서 나왔는지 추적할 수 있습니다.

### 4. 타이타닉 데이터 컬럼 (참고)
| 컬럼 | 의미 |
|---|---|
| PassengerId | 승객 ID |
| Survived | 생존 여부 (0 = 사망, 1 = 생존) |
| Pclass | 객실 등급 (1, 2, 3등급) |
| Name / Sex / Age | 이름 / 성별 / 나이 |
| SibSp / Parch | 동승한 형제·배우자 수 / 부모·자녀 수 |
| Ticket / Fare | 티켓 번호 / 요금 |
| Cabin / Embarked | 객실 번호 / 탑승 항구 |

## 코드 흐름 요약
1. `CSVLoader(FILE_PATH)`로 로더 생성 후 `load()`로 CSV 로드
2. `len(docs)`로 행 개수(891)와 `docs[0].metadata`로 `source`, `row` 확인
3. `docs[0]`, `docs[1]`의 `page_content`를 출력해 "컬럼명: 값" 형태의 텍스트 구조 확인

## 알아두면 좋은 점
- **행 단위 Document의 장단점**
  - 장점: 각 행이 독립된 검색 단위가 되어 특정 레코드(예: 특정 승객)를 정확히 검색 가능
  - 단점: 행이 수만~수십만 개면 `Document` 수가 폭증하고, "생존자는 총 몇 명?" 같은 **집계/통계형 질문**은 벡터 검색만으로 답하기 어려움 → 이런 경우 Pandas 에이전트 등 **데이터프레임 기반 분석 도구**가 더 적합
- **데이터프레임 로더(`DataFrameLoader`)**: Pandas `DataFrame`을 이미 메모리에 가지고 있을 때, 특정 컬럼을 `page_content`로 지정하고 나머지 컬럼은 `metadata`로 넣어 `Document`로 변환하는 방식입니다. `CSVLoader`와 달리 **어떤 컬럼을 본문으로, 어떤 컬럼을 메타데이터로 쓸지 직접 제어**할 수 있습니다.
- `CSVLoader`는 `csv_args`(구분자, 따옴표 문자 등)나 `source_column`(각 문서의 `source` 메타데이터로 쓸 컬럼 지정) 옵션으로 세부 동작을 조정할 수 있습니다.
- `langchain-community`는 유지보수가 축소(sunset)되고 있다는 Deprecation 경고가 출력됩니다. 현재는 동작에 문제 없으나, 향후 별도 통합 패키지로 이전될 수 있습니다.
