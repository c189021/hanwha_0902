"""
Pydantic 예시 코드 모음
실행: pip install pydantic  (설치 후) -> python pydantic.py
"""

from pydantic import BaseModel, ValidationError, field_validator


# ----------------------------------------------------------------------
# 예시 1. 기본 모델 정의 및 자동 타입 변환
# ----------------------------------------------------------------------
def example_1_basic_model():
    print("\n[예시 1] 기본 모델 정의 및 자동 타입 변환")

    class User(BaseModel):
        id: int
        name: str
        is_active: bool = True  # 기본값 설정

    # 문자열 "1"이 들어와도 int로 자동 변환됨
    user = User(id="1", name="Kim")
    print(user)                 # id=1 name='Kim' is_active=True
    print(type(user.id))        # <class 'int'>

    # 모델을 dict / JSON으로 변환
    print(user.model_dump())       # dict 형태
    print(user.model_dump_json())  # JSON 문자열 형태


# ----------------------------------------------------------------------
# 예시 2. 유효성 검사 실패 처리 (ValidationError)
# ----------------------------------------------------------------------
def example_2_validation_error():
    print("\n[예시 2] 유효성 검사 실패 처리")

    class Product(BaseModel):
        name: str
        price: float
        quantity: int

    try:
        # price에 문자를 넣어 일부러 검증 실패 유도
        product = Product(name="노트북", price="비쌈", quantity=2)
        print(product)
    except ValidationError as e:
        print("검증 실패!")
        print(e.errors())  # 어떤 필드가 왜 실패했는지 리스트로 확인 가능
        for err in e.errors():
            print(f" - 필드: {err['loc']}, 이유: {err['msg']}")


# ----------------------------------------------------------------------
# 예시 3. 커스텀 검증(field_validator) + 중첩 모델
# ----------------------------------------------------------------------
def example_3_custom_validator_and_nested_model():
    print("\n[예시 3] 커스텀 검증 + 중첩 모델")

    class Address(BaseModel):
        city: str
        zipcode: str

    class Member(BaseModel):
        username: str
        age: int
        address: Address  # 다른 모델을 필드 타입으로 중첩 사용

        @field_validator("age")
        @classmethod
        def check_age(cls, value):
            if value < 0:
                raise ValueError("나이는 음수가 될 수 없습니다.")
            if value > 120:
                raise ValueError("나이 값이 비정상적으로 큽니다.")
            return value

    # 중첩된 dict를 그대로 넣으면 Address 모델로 자동 변환됨
    member = Member(
        username="hong",
        age=25,
        address={"city": "Daejeon", "zipcode": "34000"},
    )
    print(member)
    print(member.address.city)

    # 커스텀 검증 실패 케이스
    try:
        Member(username="bad", age=-5, address={"city": "Seoul", "zipcode": "00000"})
    except ValidationError as e:
        print("커스텀 검증 실패!")
        print(e.errors())


if __name__ == "__main__":
    example_1_basic_model()
    example_2_validation_error()
    example_3_custom_validator_and_nested_model()