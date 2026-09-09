from fastapi import FastAPI
from enum import Enum

class ModelName(str, Enum):
    aaa = "alexnet"
    r = "resnet"
    l = "lenet"
    기타 = "기타"

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

app = FastAPI()

# http://localhost:8000/
@app.get("/")
def read_root():
    return {"Hello": "World"}

# http://localhost:8000/items/{555}
@app.get("/items/{item_id}")
def read_item(item_id:int, q:str | None=None):
    return {"item_id":item_id, "q":q}

# http://localhost:8000/users/me
@app.get("/users/me")
async def read_user_me():
    return{"user_id":"나를 me입니다"}

# http://localhost:8000/users/사용자
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return{"사용자아이디user_id": user_id}

# http://localhost:8000/users
@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]

# http://localhost:8000/users 위에것이 우선순위 이니 이놈은 무시된다
@app.get("/users")
async def read_users2():
    return ["Bean", "Elfo"]

# http://localhost:8000/models/{aaa}
# http://localhost:8000/models/{resnet}
# http://localhost:8000/models/{lenet}
# http://localhost:8000/models/{기타}
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):

    # 키를 요청하면, 값을 return
    if model_name is ModelName.aaa:
        return {"model_name": model_name, "message": "키요청: Deep Learning FTW!"}

    # 값을 요청하면, 키를 return
    if model_name.value == "resnet":
        return {"model_name": model_name, "message": "값요청: LeCNN all the images"}

    # 그 외에 상황
    return {"model_name": model_name, "message": "그 외에, Have some residuals"}

# http://localhost:8000/items/

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
    # return fake_items_db[0 : 10]
    # 범위연산자
    # return fake_items_db[0 : 1]

# http://localhost:8000/items2/test
# http://localhost:8000/items2/test?q=None
# http://localhost:8000/items2/test?q=qqqq
@app.get("/items2/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}