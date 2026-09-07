"""
클래스(Class) 예시 3 - 응용: 특수 메서드(dunder)를 활용한 실전 객체 설계
(원본 데이터 -> 객체 변환 -> 정렬/필터링 -> 요약)
실행: python class3.py
"""


class Product:
    """상품 하나를 표현하는 클래스"""

    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

    def __repr__(self):
        # print()나 리스트 출력 시 사람이 읽기 좋은 형태로 보여줌
        return f"Product(name={self.name!r}, price={self.price}, stock={self.stock})"

    def __eq__(self, other):
        # 이름과 가격이 같으면 같은 상품으로 취급
        if not isinstance(other, Product):
            return NotImplemented
        return self.name == other.name and self.price == other.price

    def __lt__(self, other):
        # 가격 기준으로 크기 비교 -> sorted()에서 자동으로 사용됨
        return self.price < other.price

    def total_value(self):
        return self.price * self.stock


# ----------------------------------------------------------------------
# 1) 특수 메서드(dunder) 동작 확인
# ----------------------------------------------------------------------
def example_dunder_methods():
    print("\n[1] 특수 메서드(__repr__, __eq__, __lt__) 동작 확인")

    p1 = Product("keyboard", 30000, 10)
    p2 = Product("keyboard", 30000, 5)
    p3 = Product("mouse", 15000, 20)

    print("p1:", p1)  # __repr__ 덕분에 보기 좋게 출력됨
    print("p1 == p2 (이름/가격 같음):", p1 == p2)
    print("p1 == p3:", p1 == p3)
    print("p3 < p1 (가격 비교):", p3 < p1)


# ----------------------------------------------------------------------
# 2) 실전 파이프라인: 원본 데이터 -> 객체 변환 -> 정렬/필터링 -> 요약
# ----------------------------------------------------------------------
def example_inventory_pipeline():
    print("\n[2] 재고 데이터 파이프라인 (원본 -> 객체 변환 -> 처리 -> 요약)")

    # 원본 데이터 (예: DB나 API에서 받아온 raw dict 목록이라고 가정)
    raw_items = [
        {"name": "keyboard", "price": 30000, "stock": 10},
        {"name": "mouse", "price": 15000, "stock": 20},
        {"name": "monitor", "price": 250000, "stock": 3},
        {"name": "webcam", "price": 45000, "stock": 0},
    ]

    # 1. raw dict -> Product 객체로 변환
    products = [Product(**item) for item in raw_items]
    print("전체 상품:", products)

    # 2. 가격 기준 정렬 (__lt__ 덕분에 sorted()가 바로 동작함)
    cheapest_first = sorted(products)
    print("가격 오름차순 정렬:", cheapest_first)

    # 3. 조건 필터링: 재고가 있는 상품만
    in_stock = [p for p in products if p.stock > 0]
    print("재고 있는 상품만:", in_stock)

    # 4. 요약 통계 생성
    summary = {
        "총 상품 수": len(products),
        "품절 상품 수": len(products) - len(in_stock),
        "총 재고 가치": sum(p.total_value() for p in products),
        "가장 비싼 상품": max(products).name,
        "가장 저렴한 상품": min(products).name,
    }
    print("재고 요약:", summary)


if __name__ == "__main__":
    example_dunder_methods()
    example_inventory_pipeline()
