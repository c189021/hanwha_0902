# 설계도, 틀, 개념.
class MyClass:
    # 이름, 나이
    name = "홍길동"
    age = 5

print(MyClass)
print(MyClass.age)

#오브젝트
p1 = MyClass()
print(p1.name)
p2 = MyClass() # 이렇게 오브젝트로 값 을 바꿀 수 있음
p2.name = "test"
print(p2.name)
p3 = MyClass()
print(p3.name)
p4 = MyClass()
print(p4.name)

#############################
#오브젝트를 생성할 때 클래스 초기화 사용.
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

p1 = Person("에밀리", 30)
print(p1.name)
print(p1.age)

############################
# 클래스의 메서드(액션)
class Person2:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    # 메서드 : 클래스 안에 정의된 함수(액션용)
    def greet(self):
        print("반가워요, 내 이름은 "+ self.name)

p2 = Person2("에밀리", 30)
# 오브젝트를 통해서 호출함.
p2.greet()

############################
# 클래스
class Person3:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.name} ---({self.age})"

p3 = Person3("장영실", 37)
print(p3)

########################
# class Student(Person):
#     pass

# s1 = Student("홍길동", 20)
# print(s1.name)
#########
class MyPerson:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Student(MyPerson):
    def __init__(self, name, age, school, grade):
        super().__init__(name, age)
        self.school = school
        self.grade = grade

st01 = Student("홍길동", 20, "호서대학교", 4 )
print(st01.school)
print(st01.grade)
print(st01.name)
print(st01.age)
########## 상속예시2
class Shape:
    def __init__(self, name):
        self.name = name

class Square(Shape):
    def __init__(self, name, width):
        super().__init__(name)
        self.width = width

class Triangle(Shape):
    def __init__(self, name, height):
        super().__init__(name)
        self.height = height

sq1 = Square("정사각형", 10)
print(sq1.name)
print(sq1.width)
tr1 = Triangle("삼각형", 20)
print(tr1.name)
print(tr1.height)