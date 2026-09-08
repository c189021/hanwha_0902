"""
클래스(Class) 예시 1 - 기본: 클래스 정의와 인스턴스
실행: ex0907 폴더에서 python class/class1.py
"""


# ----------------------------------------------------------------------
# 1) 클래스 정의와 인스턴스 생성
# ----------------------------------------------------------------------
def example_basic_class():
    print("\n[1] 클래스 정의와 인스턴스 생성")

    class Dog:
        def __init__(self, name, age):
            self.name = name  # 인스턴스 속성
            self.age = age

        def bark(self):
            return f"{self.name}: 멍멍!"

    # 같은 클래스로 여러 인스턴스를 만들어도 서로 독립적인 속성을 가짐
    d1 = Dog("바둑이", 3)
    d2 = Dog("나비", 1)

    print(d1.bark())
    print(d2.name, d2.age)
    print("d1과 d2는 서로 다른 객체:", d1 is not d2)


# ----------------------------------------------------------------------
# 2) 클래스 변수 vs 인스턴스 변수
# ----------------------------------------------------------------------
def example_class_vs_instance_variable():
    print("\n[2] 클래스 변수 vs 인스턴스 변수")

    class Counter:
        total_count = 0  # 클래스 변수: 모든 인스턴스가 공유하는 값

        def __init__(self, name):
            self.name = name  # 인스턴스 변수: 각 인스턴스마다 따로 가지는 값
            Counter.total_count += 1  # 클래스 변수는 클래스 이름으로 접근/수정

    c1 = Counter("a")
    c2 = Counter("b")
    c3 = Counter("c")

    print("생성된 인스턴스 개수 (클래스 변수):", Counter.total_count)
    print("각 인스턴스의 이름 (인스턴스 변수):", c1.name, c2.name, c3.name)


# ----------------------------------------------------------------------
# 3) 인스턴스 메서드 vs classmethod vs staticmethod
# ----------------------------------------------------------------------
def example_method_types():
    print("\n[3] 인스턴스 메서드 vs classmethod vs staticmethod")

    class Person:
        count = 0

        def __init__(self, name):
            self.name = name
            Person.count += 1

        def introduce(self):  # 인스턴스 메서드: self(인스턴스)를 통해 동작
            return f"저는 {self.name}입니다."

        @classmethod
        def from_full_name(cls, full_name):  # classmethod: cls(클래스)를 통해 동작, 대체 생성자로 자주 사용
            first, last = full_name.split()
            return cls(f"{first} {last}")

        @staticmethod
        def is_valid_name(name):  # staticmethod: self/cls 없이, 클래스와 관련된 유틸 함수로 사용
            return len(name.strip()) > 0

    p1 = Person("Kim")
    print(p1.introduce())

    # classmethod를 통해 다른 방식으로 인스턴스 생성
    p2 = Person.from_full_name("Hong Gildong")
    print(p2.introduce())

    print("총 인원 수:", Person.count)
    print("빈 이름은 유효한가?", Person.is_valid_name(""))
    print("'Lee'는 유효한가?", Person.is_valid_name("Lee"))


if __name__ == "__main__":
    example_basic_class()
    example_class_vs_instance_variable()
    example_method_types()
