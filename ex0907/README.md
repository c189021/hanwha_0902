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

아래 예시들은 Pydantic 공식 문서(https://docs.pydantic.dev)에서 다루는 대표 패턴을 참고해 작성했습니다. 실제 실행 가능한 전체 코드는 `pydantic_examples.py` 파일에 정리했습니다.

1. **기본 모델 정의 및 자동 타입 변환** — `BaseModel`로 필드 타입을 선언하고, 문자열 숫자가 자동으로 int로 변환되는 예시
2. **유효성 검사 실패 처리** — `ValidationError`를 잡아서 어떤 필드가 왜 실패했는지 확인하는 예시
3. **커스텀 검증 로직 (`field_validator`) + 중첩 모델** — 필드에 커스텀 검증 규칙을 추가하고, 모델 안에 다른 모델을 중첩하는 예시

자세한 내용은 pydantic_examples.py 참고.