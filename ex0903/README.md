# ex0903 (09/03) — 파이썬 문법 · Streamlit 가이드 · Matplotlib

둘째날. 파이썬으로 **데이터를 다루고(Numpy/Pandas)**, **웹 앱/그래프로 보여주는** 방법을 다룹니다.

## 다루는 내용
- Streamlit이 무엇이고 언제 쓰는지, 설치/실행 방법
- Streamlit 주요 위젯: 데이터 표시, 레이아웃(컬럼), 이미지, 차트, 수식
- NumPy / Pandas로 데이터 만들기
- Matplotlib으로 기본 그래프 그리기

## 파일
| 파일 | 설명 |
|---|---|
| [`streamlit_basics.py`](streamlit_basics.py) | `st.write`/`st.dataframe`, `st.columns` 레이아웃, `st.image`, Altair 차트, `st.latex` 종합 연습 |
| [`matplotlib_plot.py`](matplotlib_plot.py) | `matplotlib`으로 선 그래프 그리기 (`plt.plot`, 포맷 문자열, `plt.show`) |

---

## 1. 스트림릿(Streamlit)

### 스트림릿이란?
파이썬으로 에이전트/데이터 앱을 개발할 때 **빠르게 웹 앱·대시보드**를 만들기 위해 사용하는 도구. HTML/CSS/JS 없이 순수 파이썬 코드만으로 UI를 구성한다.

### 주요 사용 상황

**1. 데이터 분석 결과를 빠르게 공유할 때**
- 주피터 노트북에서 분석한 내용을 다른 사람(팀원, 상사, 고객)이 직접 조작하며 볼 수 있는 웹 앱으로 만들고 싶을 때
- "이 그래프에서 필터를 바꿔가며 보고 싶다" 같은 요구가 있을 때

**2. 머신러닝/AI 모델 데모**
- 학습시킨 모델을 프론트엔드 없이 빠르게 시연용 앱으로 보여주고 싶을 때
- 이미지 업로드 → 분류 결과 출력, 텍스트 입력 → LLM 응답 같은 간단한 인터페이스

**3. 내부용 도구(Internal Tool) 제작**
- 회사 내부에서만 쓰는 간단한 대시보드, 데이터 입력 폼, 모니터링 도구
- 정식 프론트엔드 개발자 없이 데이터 팀이 직접 UI를 뚝딱 만들 때

**4. 프로토타입/MVP**
- "일단 아이디어가 작동하는지 빠르게 확인하고 싶다" 할 때
- React/Vue 같은 프론트엔드 프레임워크 배울 필요 없이 순수 파이썬 코드만으로 UI 구성 가능

### 설치 및 실행 방법

**1) 설치**
```cmd
:: 가상환경 활성화 후
pip install streamlit numpy pandas altair
```

**2) 실행**
```cmd
streamlit run streamlit_basics.py
```
→ 터미널에서 실행하면 기본 브라우저에 `http://localhost:8501` 로 열림
→ `python streamlit_basics.py`로 실행하면 안 되고, 반드시 `streamlit run`을 써야 함

**3) 수정 사항 반영**
파일을 수정하고 저장하면, 브라우저 우측 상단에 **"Rerun"** 버튼이 뜸. 클릭하거나 **"Always rerun"**을 켜면 저장할 때마다 자동 반영됨. (새로고침만 해도 반영)

**4) 종료**
터미널에서 `Ctrl + C`

### 자주 쓰는 API — `streamlit_basics.py`에서 사용한 것

| API | 설명 |
|---|---|
| `st.write(obj)` | 뭐든 알아서 렌더링 (문자열, 표, 차트, 딕셔너리 등) — "만능 출력" |
| `st.dataframe(df)` | 스크롤·정렬 가능한 인터랙티브 표 |
| `st.columns(n)` | 화면을 n개의 열로 분할 → `with col1:` 블록 안에 위젯 배치 |
| `st.header(text)` | 소제목 |
| `st.image(url)` | 이미지 표시 (URL 또는 로컬 경로) |
| `st.latex(r"...")` | LaTeX 수식 렌더링 |
| `st.altair_chart(chart)` | Altair 차트 표시 (`use_container_width=True`로 폭 맞춤) |

```python
col1, col2, col3 = st.columns(3)
with col1:
    st.header("A cat")
    st.image("https://static.streamlit.io/examples/cat.jpg")
```

---

## 2. NumPy / Pandas 기초

`streamlit_basics.py`에서 데이터를 만들 때 사용:

```python
import numpy as np
import pandas as pd

# Pandas DataFrame — 표 형태 데이터(엑셀 시트 같은 것)
df = pd.DataFrame({
    "first column": [1, 2, 3, 4],
    "second column": [10, 20, 30, 40],
})

# NumPy — 수치 배열 / 난수 생성
dataframe = np.random.randn(10, 20)   # 표준정규분포 난수 10x20 배열
```

- `pd.DataFrame(dict)` → 키가 컬럼명, 값이 열 데이터
- `np.random.randn(행, 열)` → 평균 0, 표준편차 1 난수 배열
- Altair 예제에서는 `rng(0).standard_normal((200, 3))`으로 재현 가능한 난수(시드 고정) 사용

---

## 3. Matplotlib 기초 — `matplotlib_plot.py`

```python
import matplotlib.pyplot as plt
import numpy as np

ypoints = np.array([3, 8, 1, 10])
plt.plot(ypoints, "*:y")   # 포맷 문자열: 마커 '*', 선 스타일 ':', 색 'y'(노랑)
plt.show()                 # 별도 창으로 그래프 출력
```

### 포맷 문자열 `"*:y"` 읽는 법
| 위치 | 값 | 의미 |
|---|---|---|
| 마커 | `*` | 별표 (`o` 원, `.` 점, `s` 사각형 …) |
| 선 스타일 | `:` | 점선 (`-` 실선, `--` 파선, `-.` 일점쇄선) |
| 색 | `y` | 노랑 (`r` 빨강, `g` 초록, `b` 파랑, `k` 검정) |

- x값을 안 주면 인덱스(0, 1, 2, 3)가 x축이 됨
- `plt.show()`는 로컬에서 창을 띄움. Streamlit 안에서 보여주려면 `st.pyplot(fig)` 사용

---

## 실행

```cmd
cd ex0903
python -m venv .secondvenv
.secondvenv\Scripts\activate.bat
pip install streamlit numpy pandas altair matplotlib

streamlit run streamlit_basics.py   :: Streamlit 앱
python matplotlib_plot.py           :: Matplotlib 그래프
```
