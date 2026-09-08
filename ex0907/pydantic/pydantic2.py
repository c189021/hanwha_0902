"""
Pydantic 예시 2 - 실전: 기본값, Optional, 중첩 모델
실행: pip install pydantic  (설치 후) -> ex0907 폴더에서 python pydantic/pydantic2.py
"""

from typing import Optional

from pydantic import BaseModel, ValidationError, field_validator


# ----------------------------------------------------------------------
# 1) 기본값(default)과 Optional 필드
# ----------------------------------------------------------------------
def example_default_and_optional():
    print("\n[1] 기본값과 Optional 필드")

    class Member(BaseModel):
        username: str
        age: int = 20               # 값이 없으면 기본값 20 사용
        nickname: Optional[str] = None  # 없어도 되고, None이 들어와도 되는 필드

    # age, nickname을 생략해도 에러 없이 기본값이 채워짐
    m1 = Member(username="kim")
    print(m1)  # username='kim' age=20 nickname=None

    # 값을 직접 지정하면 그 값이 사용됨
    m2 = Member(username="lee", age=30, nickname="리")
    print(m2)


# ----------------------------------------------------------------------
# 2) 중첩 모델(nested model) + 커스텀 검증
# ----------------------------------------------------------------------
def example_nested_model():
    print("\n[2] 중첩 모델 + 커스텀 검증")

    class Address(BaseModel):
        city: str
        zipcode: str

    class User(BaseModel):
        username: str
        age: int
        address: Address  # 다른 모델을 필드 타입으로 중첩 사용
        sub_address: Optional[Address] = None  # 중첩 모델도 Optional 가능

        @field_validator("age")
        @classmethod
        def check_age(cls, value):
            if value < 0:
                raise ValueError("나이는 음수가 될 수 없습니다.")
            if value > 120:
                raise ValueError("나이 값이 비정상적으로 큽니다.")
            return value

    # 중첩된 dict를 그대로 넣으면 Address 모델로 자동 변환됨
    user = User(
        username="hong",
        age=25,
        address={"city": "Daejeon", "zipcode": "34000"},
    )
    print(user)
    print(user.address.city)
    print(user.sub_address)  # 값을 안 줬으므로 None

    # 커스텀 검증 실패 케이스
    try:
        User(username="bad", age=-5, address={"city": "Seoul", "zipcode": "00000"})
    except ValidationError as e:
        print("커스텀 검증 실패!")
        print(e.errors())


if __name__ == "__main__":
    example_default_and_optional()
    example_nested_model()
