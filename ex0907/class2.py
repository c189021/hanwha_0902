"""
클래스(Class) 예시 2 - 실전: 상속, 다형성, 캡슐화
실행: python class2.py
"""


# ----------------------------------------------------------------------
# 1) 상속과 메서드 오버라이딩 (다형성)
# ----------------------------------------------------------------------
def example_inheritance_and_polymorphism():
    print("\n[1] 상속과 메서드 오버라이딩 (다형성)")

    class Animal:
        def __init__(self, name):
            self.name = name

        def speak(self):
            return f"{self.name}은(는) 소리를 냅니다."

    class Dog(Animal):
        def speak(self):  # 부모의 메서드를 재정의(오버라이딩)
            return f"{self.name}: 멍멍!"

    class Cat(Animal):
        def speak(self):
            return f"{self.name}: 야옹!"

    animals = [Dog("바둑이"), Cat("나비"), Animal("이름없는동물")]

    # 다형성: 같은 speak() 호출이지만, 실제 객체 타입에 따라 다르게 동작
    for animal in animals:
        print(animal.speak())


# ----------------------------------------------------------------------
# 2) super()로 부모 초기화 재사용하기
# ----------------------------------------------------------------------
def example_super():
    print("\n[2] super()로 부모 초기화 재사용")

    class Employee:
        def __init__(self, name, salary):
            self.name = name
            self.salary = salary

    class Manager(Employee):
        def __init__(self, name, salary, team_size):
            super().__init__(name, salary)  # 부모 __init__을 그대로 재사용
            self.team_size = team_size

        def info(self):
            return f"{self.name} (연봉 {self.salary}, 팀원 {self.team_size}명)"

    m = Manager("Park", 6000, 5)
    print(m.info())


# ----------------------------------------------------------------------
# 3) 캡슐화: private 속성 + property로 유효성 검증
# ----------------------------------------------------------------------
def example_encapsulation_and_property():
    print("\n[3] 캡슐화 + property")

    class BankAccount:
        def __init__(self, owner, balance=0):
            self.owner = owner
            self.__balance = balance  # 이름 앞 __ -> 클래스 외부에서 직접 접근하기 어렵게 만듦(캡슐화)

        @property
        def balance(self):  # balance를 읽기 전용 속성처럼 노출
            return self.__balance

        def deposit(self, amount):
            if amount <= 0:
                raise ValueError("입금액은 0보다 커야 합니다.")
            self.__balance += amount

        def withdraw(self, amount):
            if amount > self.__balance:
                raise ValueError("잔액이 부족합니다.")
            self.__balance -= amount

    account = BankAccount("Kim", 1000)
    account.deposit(500)
    print("입금 후 잔액:", account.balance)

    try:
        account.withdraw(100_000)
    except ValueError as e:
        print("출금 실패:", e)

    try:
        account.balance = 999999  # property에 setter가 없으므로 직접 대입 시 에러 발생
    except AttributeError as e:
        print("직접 대입 불가:", e)


if __name__ == "__main__":
    example_inheritance_and_polymorphism()
    example_super()
    example_encapsulation_and_property()
