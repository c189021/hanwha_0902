# -*- coding: utf-8 -*-
"""한화ex0907.py

Colab에서 내보낸 코드를 실행 순서에 맞게 정리한 버전입니다.
(user 객체를 만든 뒤에 사용하도록 순서를 바꿨습니다.)
"""

# 모듈 import
from datetime import datetime
from pydantic import BaseModel, PositiveInt, ValidationError
from typing import Annotated, Literal
from annotated_types import Gt


# ---------------------------------------------------------------
# 1. User 모델
# ---------------------------------------------------------------
class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: datetime | None = None   # = None 을 줘야 생략 가능한 필드가 됩니다
    tastes: dict[str, PositiveInt]


# 데이터
external_data = {
    'id': 123,
    'signup_ts': '2019-06-01 12:22',
    'tastes': {
        'wine': 9,
        b'cheese': 7,
        'cabbage': '1',
    },
}

# user 오브젝트 생성 (사용하기 전에 반드시 먼저 생성)
user = User(**external_data)

print(user.id)
#> 123

print(user.model_dump())
#> {
#>   'id': 123,
#>   'name': 'John Doe',
#>   'signup_ts': datetime.datetime(2019, 6, 1, 12, 22),
#>   'tastes': {'wine': 9, 'cheese': 7, 'cabbage': 1},
#> }

print(user.signup_ts)
print(user.tastes)


# ---------------------------------------------------------------
# 2. 검증 실패(ValidationError) 확인
# ---------------------------------------------------------------
external_data2 = {
    'id': 'not an int',
    'tastes': {},
}

try:
    User(**external_data2)
except ValidationError as e:
    print(e.errors())


# ---------------------------------------------------------------
# 3. Fruit 모델 - Literal, Annotated 사용
# ---------------------------------------------------------------
class Fruit(BaseModel):
    name: str
    color: Literal['red', 'green']
    weight: Annotated[float, Gt(0)]
    bazam: dict[str, list[tuple[int, bool, float]]]


print(
    Fruit(
        name='Apple',
        color='red',
        weight=4.2,
        bazam={'foobar': [(1, True, 0.1)]},
    )
)


# ---------------------------------------------------------------
# 4. Meeting 모델 - model_dump 옵션들
# ---------------------------------------------------------------
class Meeting(BaseModel):
    when: datetime
    where: bytes
    why: str = 'No idea'


m = Meeting(when='2020-01-01T12:00', where='home')

print(m.model_dump(exclude_unset=True))
#> {'when': datetime.datetime(2020, 1, 1, 12, 0), 'where': b'home'}

print(m.model_dump(exclude={'where'}, mode='json'))
#> {'when': '2020-01-01T12:00:00', 'why': 'No idea'}

print(m.model_dump_json(exclude_defaults=True))
#> {"when":"2020-01-01T12:00:00","where":"home"}