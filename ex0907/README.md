# Git/GitHub & Pydantic 정리

## 1. GitHub 레포 Push / Pull 사용법

### 기본 흐름
```bash
# 1. 레포 클론 (처음 한 번만)
git clone https://github.com/사용자명/레포이름.git
cd 레포이름

# 2. 변경사항 확인
git status

# 3. 변경 파일 스테이징
git add .              # 전체 추가
git add 파일명          # 특정 파일만 추가

# 4. 커밋
git commit -m "커밋 메시지"

# 5. 원격 저장소로 push
git push origin main    # 브랜치명은 main 또는 master

# 6. 원격 저장소 변경사항 받아오기
git pull origin main
```

### 자주 쓰는 명령어
| 명령어 | 설명 |
|---|---|
| `git init` | 현재 폴더를 git 레포로 초기화 |
| `git remote add origin <URL>` | 원격 저장소 연결 |
| `git remote -v` | 연결된 원격 저장소 확인 |
| `git log` | 커밋 히스토리 확인 |
| `git branch` | 브랜치 목록 확인 |
| `git checkout -b 브랜치명` | 새 브랜치 생성 및 이동 |

### 최초 연결 시 (로컬 폴더 → 새 GitHub 레포)
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/사용자명/레포이름.git
git push -u origin main
```

---

## 2. 레포 연결 끊기 (로컬 + GitHub 완전 삭제)

### 2-1. 로컬 폴더에서 git 연결 끊기
`.git` 폴더는 숨김 파일이라 탐색기/Finder에서 "숨김 항목 보기"를 켜야 보입니다.

**Windows (탐색기)**
- 보기 → 숨긴 항목 체크 → `.git` 폴더 삭제

**Mac (Finder)**
- `Cmd + Shift + .` 로 숨김 파일 표시 → `.git` 폴더 삭제

**터미널로 삭제 (더 간단)**
```bash
# 레포 폴더로 이동 후
rm -rf .git          # Mac / Linux
rmdir /s /q .git      # Windows (cmd)
Remove-Item -Recurse -Force .git   # Windows (PowerShell)
```
> `.git` 폴더만 지우면 폴더 자체는 남고, git 이력/원격 연결 정보만 사라집니다 (일반 폴더가 됨).

### 2-2. GitHub에서 원격 레포 삭제
1. GitHub 접속 → 삭제할 레포 페이지 이동
2. 상단 탭에서 **Settings** 클릭
3. 맨 아래로 스크롤 → **Danger Zone** 섹션
4. **Delete this repository** 클릭
5. 확인 문구(레포 전체 경로, 예: `사용자명/레포이름`)를 정확히 입력
6. **I understand the consequences, delete this repository** 클릭 → 완료

⚠️ 삭제는 되돌릴 수 없으니, 필요하면 미리 zip 백업이나 다른 계정으로 fork 해두는 것을 추천합니다.

---

## 3. Pydantic 개념 정리

### Pydantic이란?
Python 타입 힌트를 기반으로 **데이터 검증(validation)**과 **설정 관리**를 해주는 라이브러리입니다. 클실래스에 타입을 선언해두면, 제 데이터가 들어올 때 그 타입에 맞는지 자동으로 검사하고 변환해줍니다.

### 왜 쓰는가?
- **자동 타입 검증**: 잘못된 타입의 데이터가 들어오면 명확한 에러를 발생시켜 버그를 조기에 발견
- **자동 형변환**: `"3"` 같은 문자열도 `int` 필드면 자동으로 `3`으로 변환 시도
- **코드 가독성/문서화**: 데이터 구조가 클래스 형태로 명시되어 있어 스키마 파악이 쉬움
- **FastAPI 등과의 통합**: FastAPI의 요청/응답 스키마 검증에 기본으로 사용됨
- **JSON ↔ 객체 변환**: API 응답이나 설정 파일(JSON)을 파이썬 객체로 쉽게 변환
- **에러 메시지가 친절함**: 어떤 필드가 왜 잘못됐는지 상세히 알려줌

간단히 말하면, "이 데이터는 이런 모양이어야 한다"를 코드로 선언하고, Pydantic이 그 약속이 지켜지는지 자동으로 검사해주는 도구입니다.

---

## 4. 설치 및 실행

### 설치
```bash
pip install pydantic
```

설치 확인:
```bash
python -c "import pydantic; print(pydantic.VERSION)"
```

### 간단 실행 예시
```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

user = User(id=1, name="Kim")
print(user)
```
```bash
python 파일명.py
```

---

## 5. 공식 문서 기반 예시 코드

아래 예시들은 Pydantic 공식 문서(https://docs.pydantic.dev)에서 다루는 대표 패턴을 참고해 작성했습니다. 주제별로 파일을 나눠서 정리했습니다.

### `pydantic1.py` — 기본: 데이터 검증과 타입 변환
- 기본 모델 정의 및 자동 타입 변환 — `BaseModel`로 필드 타입을 선언하고, 문자열 숫자가 자동으로 int로 변환되는 예시
- 유효성 검사 실패 처리 — `ValidationError`를 잡아서 어떤 필드가 왜 실패했는지 확인하는 예시

### `pydantic2.py` — 실전: 기본값, Optional, 중첩 모델
- 기본값(default)과 Optional 필드 — 값을 생략해도 기본값이 채워지고, `Optional[str] = None`처럼 없어도 되는 필드를 다루는 예시
- 중첩 모델(nested model) + 커스텀 검증 — 모델 안에 다른 모델(`Address`)을 필드로 중첩하고, `field_validator`로 커스텀 검증 규칙(나이 범위 등)을 추가하는 예시

> **개념: 기본값 vs Optional은 다르다**
> - `age: int = 20` → 필드를 **생략**할 수 있고, 생략하면 20이 들어감 (필드는 필수가 아님, 타입은 여전히 `int`만 허용)
> - `nickname: Optional[str] = None` → 값으로 **`None`이 들어와도** 허용한다는 의미 (`str` 또는 `None`)
> - 즉 "생략 가능"과 "None 허용"은 별개 개념이라, 실전에서는 상황에 맞게 `기본값만`, `Optional만`, 또는 `Optional + 기본값`(`Optional[str] = None`) 조합을 골라 써야 함
>
> **개념: 중첩 모델을 쓰는 이유**
> 실무 데이터는 대부분 계층 구조(회원 안에 주소, 주문 안에 상품 목록 등)를 가짐. 하나의 모델에 모든 필드를 평평하게 넣는 대신 `Address`처럼 의미 단위로 모델을 쪼개 중첩하면 ① 재사용이 쉽고 ② dict를 그대로 넘겨도 Pydantic이 알아서 하위 모델로 변환/검증해줘 코드가 간결해짐.

### `pydantic3.py` — 실전: API 요청 → 검증 → 데이터 변환
- 요청 모델(`SignupRequest`)로 들어온 데이터를 검증(이메일 형식, 커스텀 username 규칙 포함)
- 검증에 성공하면 내부용 모델(`UserRecord`)로 변환(이메일 소문자 정규화, 생년 → 나이 계산 등)해 응답/DB 저장에 사용하는 흐름 예시
- 검증 실패 시 `ValidationError`의 오류 목록을 클라이언트 응답 형태로 가공하는 예시
- `EmailStr` 타입을 쓰므로 `pip install pydantic email-validator` 필요

> **개념: 요청(Request) 모델과 내부(Internal) 모델을 왜 분리하는가**
> 실제 API 서버(FastAPI 등)에서는 보통 아래 3단계 흐름을 따름:
> 1. **요청 모델**로 클라이언트가 보낸 원본 데이터의 형태/타입을 검증 (예: `SignupRequest`)
> 2. 검증을 통과한 데이터를 서비스 로직에서 쓰기 좋은 **내부 모델**로 가공/변환 (예: `UserRecord` — 이메일 정규화, 생년→나이 계산처럼 원본에는 없던 값을 파생)
> 3. 내부 모델을 다시 **응답/저장용 형태**(JSON, DB row 등)로 내보냄
>
> 이렇게 나누면 "클라이언트가 보내는 값"과 "서버 내부/DB에서 쓰는 값"이 달라져도(필드명, 단위, 파생값 등) 서로 영향을 주지 않고, 검증 실패는 요청 단계에서 조기에 걸러낼 수 있음.

각 파일은 `python 파일명.py`로 바로 실행할 수 있습니다.