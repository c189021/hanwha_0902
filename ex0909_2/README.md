# ex0909_2 - FastAPI CRUD 실습

FastAPI와 Pydantic을 사용한 기본 CRUD(Create/Read/Update/Delete) API 실습 프로젝트입니다.
데이터베이스 없이 메모리 딕셔너리(`items_db`)에 아이템을 저장합니다.

## 구성

- `main.py`: FastAPI 앱 및 라우터 정의

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | `/items/` | 아이템 생성 |
| GET | `/items/` | 전체 아이템 조회 |
| GET | `/items/{item_id}` | 단일 아이템 조회 |
| PUT | `/items/{item_id}` | 아이템 수정 |
| DELETE | `/items/{item_id}` | 아이템 삭제 |

### 아이템 스키마

```python
class ItemSchema(BaseModel):
    name: str
    price: float
    description: str | None = None
```

## 실행 방법

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

실행 후 `http://127.0.0.1:8000/docs`에서 Swagger UI로 API를 테스트할 수 있습니다.
