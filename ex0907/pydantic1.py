"""
Pydantic 예시 1 - 기본: 데이터 검증과 타입 변환
실행: pip install pydantic  (설치 후) -> python pydantic1.py
"""

from pydantic import BaseModel, ValidationError


# ----------------------------------------------------------------------
# 1) 기본 모델 정의 및 자동 타입 변환
# ----------------------------------------------------------------------
def example_basic_type_conversion():
    print("\n[1] 기본 모델 정의 및 자동 타입 변환")

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
# 2) 유효성 검사 실패 처리 (ValidationError)
# ----------------------------------------------------------------------
def example_validation_error():
    print("\n[2] 유효성 검사 실패 처리")

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


if __name__ == "__main__":
    example_basic_type_conversion()
    example_validation_error()
