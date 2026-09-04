# ex0902 (09/02) — 파이썬 기본 문법 · 가상환경 세팅 · VSCode 익스텐션

첫날. 파이썬 개발을 시작하기 위한 **환경 세팅**과 **기본 문법**을 다룹니다.

## 다루는 내용
- 파이썬 가상환경(venv)을 왜 쓰고 어떻게 만드는지
- VSCode + 파이썬 익스텐션 세팅
- 파이썬 기본 문법: 변수, 자료형, 리스트, 반복문, 문자열 출력

## 파일
| 파일 | 설명 |
|---|---|
| [`python_basics.py`](python_basics.py) | 변수 선언, 리스트, `range` 반복문, `print` 서식(`f-string`, `sep`, `end`) 연습 |

---

## 1. 파이썬 가상환경(venv) 세팅

### 가상환경을 왜 만들어서 쓰는가?

- **프로젝트별 패키지 버전 충돌 방지**: 프로젝트마다 필요한 라이브러리 버전이 다를 수 있는데, 가상환경 없이 전역(global)에 설치하면 한 프로젝트에서 특정 패키지를 업데이트했을 때 다른 프로젝트가 깨질 수 있음
- **의존성 관리가 쉬워짐**: 프로젝트마다 독립된 패키지 환경을 가지므로, 필요한 패키지 목록(`requirements.txt` 등)을 깔끔하게 관리 가능
- **시스템 파이썬 환경 보호**: 전역 파이썬 환경을 건드리지 않아 OS나 다른 프로그램에 영향을 주지 않음
- **협업 시 동일한 환경 재현 가능**: 다른 사람이 동일한 가상환경을 그대로 만들어서 똑같은 버전으로 실행 가능

### 가상환경 생성 및 사용 방법

**1) 가상환경 생성**
```cmd
E:\agent26_DayByDay\day1> python -m venv .firstvenv
```
→ 위 명령어로 가상환경 구축 (`.firstvenv` 폴더가 생성됨)

**2) 가상환경 활성화**
```cmd
E:\agent26_DayByDay\day1> .firstvenv\Scripts\activate.bat
```
→ `Scripts` 폴더 안의 `activate.bat` 파일을 상대경로로 복사+붙여넣기 해서 실행

활성화되면 프롬프트 앞에 가상환경 이름이 표시됨:
```
(.firstvenv) E:\agent26_DayByDay\day1>
```

**3) 코드 실행 (테스트)**
```cmd
(.firstvenv) E:\agent26_DayByDay\day1> python test.py
```

**4) 가상환경 비활성화**
```cmd
deactivate.bat
```
→ 상대경로로 복사+붙여넣기 해서 실행하면 가상환경에서 빠져나옴

> 💡 PowerShell에서는 `.firstvenv\Scripts\Activate.ps1`, Git Bash/Mac/Linux에서는 `source .firstvenv/bin/activate` 를 사용합니다.
> 실행 정책 오류가 나면 PowerShell에서 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 한 번 설정.

---

## 2. VSCode 익스텐션 가이드

익스텐션 설치: 왼쪽 사이드바의 **Extensions** 아이콘(`Ctrl+Shift+X`) → 이름 검색 → **Install**.

| 익스텐션 | 게시자 | 용도 | 필수 여부 |
|---|---|---|---|
| **Python** | Microsoft | 파이썬 실행/디버그, 인터프리터 선택, 가상환경 인식 | 필수 |
| **Pylance** | Microsoft | 빠른 자동완성, 타입 힌트, 오류 표시 (Python 설치 시 함께 설치됨) | 필수 |
| **Jupyter** | Microsoft | `.ipynb` 노트북 실행, 셀 단위 실행 | 권장 |
| **Black Formatter** 또는 **autopep8** | Microsoft | 저장 시 코드 자동 정렬(PEP 8) | 권장 |
| **Korean Language Pack** | Microsoft | VSCode 메뉴 한글화 | 선택 |
| **Material Icon Theme** | Philipp Kief | 파일/폴더 아이콘 구분 | 선택 |

### 설치 후 필수 설정 — 인터프리터 선택
1. `Ctrl+Shift+P` → **Python: Select Interpreter** 입력
2. 목록에서 이 프로젝트의 가상환경(`.firstvenv\Scripts\python.exe`) 선택
3. 우측 하단 상태바에 선택한 파이썬 버전/가상환경이 표시되는지 확인

이 설정을 해야 VSCode 터미널을 열 때 가상환경이 자동 활성화되고, 실행(▶) 버튼이 올바른 환경에서 코드를 돌립니다.

### 저장 시 자동 포맷 (선택)
`settings.json`에 추가:
```json
{
  "editor.formatOnSave": true,
  "[python]": { "editor.defaultFormatter": "ms-python.black-formatter" }
}
```

---

## 3. 파이썬 기본 문법 정리

`python_basics.py`에서 다룬 내용:

### 변수와 자료형
```python
title = "AI 서비스 백엔드 프로그래밍 실무"   # 문자열(str)
hours = 8                                    # 정수(int)
topics = ["파이썬 기본 문법", "클래스", "데코레이터", "예외 처리", "로깅"]  # 리스트(list)
```
- 파이썬은 변수 선언 시 타입을 명시하지 않음(동적 타이핑)
- 주요 자료형: `int`, `float`, `str`, `bool`, `list`, `tuple`, `dict`, `set`

### 리스트(list)
- 순서가 있고 수정 가능한 자료 묶음. `[]`로 생성
- 인덱싱 `topics[0]`, 슬라이싱 `topics[1:3]`, 추가 `topics.append(...)`

### 반복문 — for + range
```python
for x in range(32):
    print("=", end="")   # end="" → 줄바꿈 대신 이어서 출력
print("")                # 마지막에 줄바꿈

for topic in topics:     # 리스트를 직접 순회
    print(topic)
```
- `range(32)` → 0부터 31까지 32번 반복
- `range(start, stop, step)` 형태도 가능

### 문자열 출력 — print 서식
```python
print(f"{topic}, 시간:{hours}")          # f-string: 중괄호 안에 변수/식
print(topic, hours, sep=", 시간:")        # sep: 값 사이 구분자
print("=", end="")                       # end: 출력 끝 문자(기본값 "\n")
```

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `sep` | `" "` (공백) | 여러 값을 출력할 때 값 사이에 넣을 문자 |
| `end` | `"\n"` (줄바꿈) | 출력이 끝난 뒤 붙일 문자 |

---

## 실행

```cmd
cd ex0902
python -m venv .firstvenv
.firstvenv\Scripts\activate.bat
python python_basics.py
```
