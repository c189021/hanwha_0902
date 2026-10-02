from typing import TypedDict

# 사용자 기획서: 아이디, 이름, 이메일
# 클래스의 상속: TypedDict
class User(TypedDict):
    id:int
    name:str
    email:str

user1:User = {
    "id": 1,
    "name": "돌쇠",
    "email": "ddd@gmail.com"
}
user2:User = {
    "id": 2,
    "name": "먹쇠",
    "email": "mmm@gmail.com"
}
user3:User = {
    "id": 3,
    "name": "개똥이",
    "email": "gggg@gmail.com"
}
# page97
user_data={
    "id": 4,
    "name": "언팩킹",
    "email": "eeee@gmail.com"
}

print(user1)
print(str(user1["id"]) + " " + user1["name"] + " " + user1["email"])
print(str(user2["id"]) + " " + user2["name"] + " " + user2["email"])
print(str(user3["id"]) + " " + user3["name"] + " " + user3["email"])
# page97 : 언팩킹***
user4 = User(**user_data)
print(user4)