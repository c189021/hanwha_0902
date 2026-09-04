# ex_git_0904 (09/04) — 파이썬 문법 · NumPy · Streamlit(Altair) · Git/GitHub · GitHub Desktop

셋째날. 코드를 **버전 관리(Git)** 하고 **GitHub에 올리는** 방법, 그리고 인터랙티브 차트를 만드는 방법을 다룹니다.

> 이 폴더는 원래 Git 실습용으로 만든 별도 레포지토리(`https://github.com/c189021/ex_git_0904`)였습니다. 그래서 이름에 `git`이 붙어 있고, 실습 커밋 이력(`첫번째날`, `두번째테스트`, `gitignore수정` …)이 남아 있었습니다. 지금은 상위 레포로 통합했습니다.

## 다루는 내용
- Git 기본 개념과 명령어 흐름
- GitHub Desktop으로 레포 생성하기
- `.gitignore`로 가상환경/불필요 파일 제외하기
- NumPy 배열 기초
- Streamlit + Altair 인터랙티브 차트 (캐싱, hover 툴팁, 레이어)

## 파일
| 파일 | 설명 |
|---|---|
| [`streamlit_altair_chart.py`](streamlit_altair_chart.py) | 주식 가격 라인차트 + 마우스오버 툴팁 + 이모지 주석 레이어. `@st.cache_data` 캐싱, `vega_datasets` 사용 |
| [`text.txt`](text.txt) | Git add/commit/push 흐름을 연습하려고 만든 더미 텍스트 파일 |

---

## 1. Git 기본

### Git이란?
파일의 변경 이력을 저장(스냅샷)해두고, 원하는 시점으로 되돌리거나 여러 사람이 나눠 작업한 내용을 합칠 수 있게 해주는 **버전 관리 시스템**. GitHub는 이 Git 저장소를 온라인에 올려두고 협업하는 **호스팅 서비스**.

### 기본 용어
| 용어 | 뜻 |
|---|---|
| repository (레포) | 프로젝트 폴더 + 변경 이력 전체 |
| commit | 특정 시점의 스냅샷 (메시지와 함께 저장) |
| staging area | 다음 커밋에 포함할 변경분을 담아두는 곳 (`git add`) |
| branch | 독립적으로 작업하는 갈래 (`main`이 기본) |
| remote (origin) | 원격 저장소 (보통 GitHub) |
| push / pull | 로컬 커밋을 원격에 올리기 / 원격 변경을 로컬로 받기 |

### 명령어 흐름
```bash
git init                       # 현재 폴더를 Git 레포로 만들기 (최초 1회)
git status                     # 현재 변경 상태 확인 (자주 사용)

git add text.txt               # 특정 파일을 staging에 올리기
git add .                      # 변경된 모든 파일 staging

git commit -m "첫번째날"        # staging된 내용을 스냅샷으로 저장

git remote add origin https://github.com/사용자명/레포명.git   # 원격 연결 (최초 1회)
git push -u origin main        # 로컬 main을 원격 origin에 올리기 (처음엔 -u)
git push                       # 이후에는 이것만

git pull                       # 원격의 최신 변경 받아오기
git log --oneline              # 커밋 이력 한 줄로 보기
```

> 커밋 메시지는 "무엇을 왜 바꿨는지" 알 수 있게 씀. 실습에서는 `첫번째날`, `두번째테스트`처럼 간단히 남기기도 함.

---

## 2. GitHub Desktop으로 레포 생성

명령어 대신 GUI로 Git을 쓰는 도구. `File > New repository` 에서 아래 항목 설정:

| 항목 | 설명 |
|---|---|
| Name | 레포지토리 이름 (예: `ex_git_0904`) |
| Local path | 로컬에 저장될 경로 |
| Description | 레포 설명 (선택) |
| Initialize with README | `README.md` 자동 생성 체크 |
| Git ignore | `Python` 선택 (파이썬 프로젝트용 불필요 파일 자동 제외) |
| License | 필요 시 선택 (기본 None) |

→ `Create repository` 클릭하면 지정한 로컬 경로에 레포 생성됨.
→ 이후 `Publish repository` 를 누르면 GitHub 계정에 원격 레포가 만들어지고 push됨.

### GitHub Desktop 기본 사용 흐름
1. 파일을 수정하면 왼쪽 **Changes** 탭에 변경 목록이 뜸
2. 아래 **Summary** 칸에 커밋 메시지 입력 → **Commit to main**
3. 상단 **Push origin** 클릭 → GitHub에 반영
4. 다른 곳에서 바뀐 게 있으면 **Fetch origin / Pull origin**

---

## 3. `.gitignore`에 가상환경 폴더 추가하기

가상환경 폴더(`venv`, `.venv`, `.thirdenv` 등)는 용량이 크고 사람마다 환경이 달라서 **Git에 올리면 안 됨**. 대신 `requirements.txt`만 공유하고, 각자 로컬에서 가상환경을 새로 만들어 패키지를 설치하는 방식이 일반적.

`.gitignore` 파일에 만든 가상환경 폴더명을 추가:
```gitignore
# Environments
.env
.venv
.thirdenv
```

- `.env`: 환경변수(API 키 등 민감 정보) 저장 파일 → **절대 커밋되면 안 됨**
- `.venv`, `.thirdenv` 등: 직접 만든 가상환경 폴더명 → 프로젝트마다 실제 만든 폴더 이름을 그대로 추가

> 💡 GitHub Desktop에서 레포 생성 시 "Git ignore: Python" 옵션을 선택하면 기본적인 파이썬 제외 파일(`__pycache__`, `*.pyc` 등)은 자동으로 들어가지만, **직접 만든 가상환경 폴더명은 자동으로 안 들어가는 경우가 많으니** `.gitignore`를 열어서 직접 추가해야 함.

> ⚠️ 이미 가상환경 폴더를 한 번이라도 커밋한 적이 있다면, `.gitignore`에 추가해도 이미 추적 중인 파일은 자동으로 안 빠짐. 그럴 땐 캐시에서 제거한 뒤 다시 커밋:
> ```bash
> git rm -r --cached .thirdenv
> git commit -m "gitignore수정: 가상환경 폴더 추적 해제"
> ```

> ⚠️ 폴더 안에 또 다른 `.git` 폴더가 있으면(레포 안의 레포), 상위 Git이 그 폴더 내용을 추적하지 못하고 빈 폴더처럼 처리됨. 하위 폴더를 상위 레포로 합칠 때는 하위 `.git` 폴더를 먼저 삭제해야 함.

---

## 4. NumPy 기초

```python
import numpy as np

a = np.array([3, 8, 1, 10])       # 1차원 배열
m = np.random.randn(10, 20)       # 표준정규분포 난수 10x20
z = np.zeros((2, 3))              # 0으로 채운 2x3
r = np.arange(0, 10, 2)           # [0 2 4 6 8]

a.shape      # (4,)   배열 모양
a.mean()     # 평균
a * 2        # 원소별 연산 (반복문 없이 한 번에)
a[a > 5]     # 조건 필터링 → [8 10]
```

- 파이썬 리스트보다 **빠르고 메모리 효율적**, 벡터/행렬 연산에 최적화
- Pandas / Matplotlib / scikit-learn 등 데이터 라이브러리의 기반

---

## 5. Streamlit + Altair 인터랙티브 차트 — `streamlit_altair_chart.py`

`vega_datasets`의 주식 가격 데이터로 **마우스를 올리면 값이 표시되는** 라인차트를 만든다.

```python
@st.cache_data          # 함수 결과를 캐싱 → 앱이 리런돼도 데이터를 다시 안 불러옴
def get_data():
    source = data.stocks()
    return source[source.date.gt("2004-01-01")]
```

핵심 개념:
| 요소 | 설명 |
|---|---|
| `@st.cache_data` | 느린 데이터 로딩/연산을 캐시. 인자가 같으면 재실행 안 함 |
| `alt.selection_single(on="mouseover")` | 마우스오버 인터랙션 정의 (hover) |
| `mark_line()` / `mark_circle()` / `mark_rule()` | 선 / 점 / 세로 기준선 |
| `transform_filter(hover)` | hover된 지점만 강조 표시 |
| 레이어 합성 `lines + points + tooltips` | 여러 차트를 겹쳐서 하나로 |
| 주석(annotation) 레이어 | 특정 날짜/가격에 이모지·설명 텍스트 표시 |
| `st.altair_chart(chart, use_container_width=True)` | 컨테이너 폭에 맞춰 렌더링 |

설치:
```cmd
pip install streamlit altair pandas vega_datasets
```

> 참고: 최신 Altair(5.x)에서는 `selection_single` → `selection_point`, `add_selection` → `add_params`, `empty="none"` → `empty=False` 로 API가 바뀌었음. 예제가 안 돌면 버전 확인.

---

## 실행

```cmd
cd ex_git_0904
python -m venv .thirdenv
.thirdenv\Scripts\activate.bat
pip install streamlit altair pandas vega_datasets numpy

streamlit run streamlit_altair_chart.py
```
