"""
Pydantic 예시 3 - API 요청 -> 검증 -> 데이터 변환
실행: pip install pydantic email-validator  (설치 후) -> ex0907 폴더에서 python pydantic/pydantic3.py
(EmailStr 타입을 쓰려면 email-validator 패키지가 추가로 필요합니다)
"""

from datetime import date

from pydantic import BaseModel, EmailStr, ValidationError, field_validator


# ----------------------------------------------------------------------
# 요청으로 들어오는 데이터 형태 (예: JSON body)
# ----------------------------------------------------------------------
class SignupRequest(BaseModel):
    username: str
    email: EmailStr          # 이메일 형식이 아니면 자동으로 검증 실패
    birth_year: int

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, value):
        if len(value) < 3:
            raise ValueError("username은 3자 이상이어야 합니다.")
        return value


# ----------------------------------------------------------------------
# 검증을 통과한 데이터를 서비스/DB에서 쓰기 좋은 형태로 변환한 모델
# ----------------------------------------------------------------------
class UserRecord(BaseModel):
    username: str
    email: str
    age: int


def to_user_record(request: SignupRequest) -> UserRecord:
    """요청 모델 -> 내부에서 사용할 데이터로 변환"""
    current_year = date.today().year
    return UserRecord(
        username=request.username.lower(),   # 소문자로 정규화
        email=request.email,
        age=current_year - request.birth_year,  # 생년 -> 나이로 변환
    )


# ----------------------------------------------------------------------
# 1) 정상적인 요청: 검증 성공 -> 데이터 변환까지 이어지는 흐름
# ----------------------------------------------------------------------
def example_api_request_success():
    print("\n[1] 정상 요청 처리 흐름 (검증 -> 변환)")

    raw_request = {
        "username": "HONG",
        "email": "hong@example.com",
        "birth_year": 2000,
    }

    # 1. 요청 데이터 검증
    request = SignupRequest(**raw_request)
    print("검증된 요청:", request)

    # 2. 검증된 데이터를 내부 형태로 변환
    record = to_user_record(request)
    print("변환된 내부 데이터:", record)
    print("응답으로 내려줄 JSON:", record.model_dump_json())


# ----------------------------------------------------------------------
# 2) 잘못된 요청: 검증 단계에서 실패
# ----------------------------------------------------------------------
def example_api_request_failure():
    print("\n[2] 잘못된 요청 처리 흐름 (검증 실패)")

    raw_request = {
        "username": "ab",              # 3자 미만 -> 커스텀 검증 실패
        "email": "not-an-email",       # 이메일 형식 아님 -> 검증 실패
        "birth_year": "이천년",          # 정수 변환 불가 -> 검증 실패
    }

    try:
        SignupRequest(**raw_request)
    except ValidationError as e:
        print("요청 검증 실패! 아래 오류들을 클라이언트에 응답으로 내려줄 수 있음")
        for err in e.errors():
            print(f" - 필드: {err['loc']}, 이유: {err['msg']}")


if __name__ == "__main__":
    example_api_request_success()
    example_api_request_failure()
