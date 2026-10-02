# ex1002 — 파이썬 함수 & 객체지향(OOP) 기초 예제

## 개요
`ex1002`는 LangChain/LangGraph 실습에 들어가기 전, **파이썬 함수와 클래스(OOP) 기본 문법**을 연습하는 예제 모음입니다. `uv` 프로젝트 구조(`pyproject.toml`, `src/` 레이아웃)로 구성되어 있으며, `app.py`를 진입점으로 각 예제 모듈을 불러와 실행합니다.

## 디렉터리 구조
```
ex1002/
├── pyproject.toml
├── requirements.txt
├── uv.lock
└── src/
    └── ex1002/
        ├── __init__.py       # 패키지 초기화, app.main() 노출
        ├── app.py            # 진입점
        └── mypy/
            ├── ex_function.py  # 함수 문법 예제
            └── ex_oop.py       # 클래스/OOP 문법 예제
```

## 파일별 내용 및 개념 정리

### 1. `src/ex1002/__init__.py` — 패키지 초기화
```python
from .app import main

__all__ = ["main"]

print("프로젝트 초기화 init")
```
- 패키지가 처음 import될 때 **`__init__.py`가 가장 먼저 실행**되며, 여기서 `app.py`의 `main` 함수를 끌어와 패키지 바깥에서 `from ex1002 import main`처럼 바로 쓸 수 있게 노출합니다.
- `__all__`은 `from ex1002 import *`를 했을 때 **공개할 이름 목록**을 명시하는 관례입니다.
- `print("프로젝트 초기화 init")`을 통해 패키지가 import되는 시점을 확인할 수 있습니다.

### 2. `src/ex1002/app.py` — 진입점
```python
def main() -> None:
    print("앱")
    from .mypy import ex_oop
```
- `main()` 함수 안에서 `from .mypy import ex_oop`를 실행하면, **`ex_oop.py` 모듈 전체가 그 시점에 로드되면서 모듈 최상단의 모든 코드가 즉시 실행**됩니다. (`ex_oop.py` 안에 별도 함수로 감싸인 코드가 없기 때문)
- 주석 처리된 `# from .mypy import ex_function`은 같은 방식으로 함수 예제 쪽을 실행하고 싶을 때 바꿔 쓸 수 있다는 것을 보여줍니다.
- `def main() -> None:`의 `-> None`은 **타입 힌트(type hint)** 로, 이 함수가 반환값이 없음을 명시합니다. (패키지 이름이 `mypy`인 것도 타입 체크 학습을 염두에 둔 것으로 보입니다.)

### 3. `src/ex1002/mypy/ex_function.py` — 함수(Function) 문법 정리

| 예제 | 핵심 개념 |
|---|---|
| `my_function(num1)` | 가장 기본적인 **위치 인자(positional argument)** 함수, `return`으로 값 반환 |
| `my_function2(fname, lname)` | 인자를 **순서대로** 전달받아 조합해서 출력 (반환값 없이 `print`만 수행) |
| `my_function3(country="천안")` | **기본값(default argument)** — 인자를 생략하면 `"천안"`이 사용됨 (`my_function3()` 호출 결과로 확인) |
| `my_function4(animal="개", name="철수")` | **키워드 인자(keyword argument)** — 호출 시 `animal=`, `name=`처럼 이름을 지정해 순서와 무관하게 전달 |

- 함수 정의 순서와 무관하게, **먼저 정의된 함수를 바로 아래에서 호출**하는 절차적 스크립트 스타일로 작성되어 있습니다.
- `sum = my_function(77)`처럼 파이썬 내장 함수 `sum`과 같은 이름의 변수를 쓰는 것은 실제 프로젝트에서는 **내장 함수를 가리는(shadowing) 안티패턴**이므로 피하는 것이 좋습니다. (이 예제에서는 간단한 학습 목적상 그대로 사용됨)

### 4. `src/ex1002/mypy/ex_oop.py` — 객체지향(OOP) 문법 정리

**(1) 클래스와 클래스 변수**
```python
class MyClass:
    name = "홍길동"
    age = 5
```
- 클래스는 객체를 만들기 위한 **설계도/틀**입니다. `MyClass.age`처럼 **클래스 자체**에서 바로 접근 가능한 변수를 **클래스 변수**라고 합니다.

**(2) 객체(인스턴스) 생성과 독립성**
```python
p1 = MyClass()
p2 = MyClass()
p2.name = "test"   # p2만 변경됨, p1은 영향 없음
```
- `p1`, `p2`는 같은 클래스에서 만들어진 **서로 다른 인스턴스(객체)** 이며, 한 인스턴스의 속성을 바꿔도 다른 인스턴스에는 영향이 없습니다. (인스턴스 변수의 독립성)

**(3) 생성자 — `__init__`**
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```
- `__init__`은 `Person(...)`으로 객체를 만드는 순간 **자동으로 호출되는 초기화 메서드(생성자)** 입니다.
- `self`는 **생성되는 객체 자기 자신**을 가리키며, `self.name = name`처럼 전달받은 인자를 **인스턴스 변수**로 저장합니다.

**(4) 메서드 — 클래스 안에 정의된 함수**
```python
class Person2:
    def __init__(self, name, age):
        ...
    def greet(self):
        print("반가워요, 내 이름은 " + self.name)

p2 = Person2("에밀리", 30)
p2.greet()
```
- 클래스 안에 정의된 함수를 **메서드(method)** 라고 하며, 객체가 할 수 있는 "행동"을 표현합니다. `p2.greet()`처럼 **객체를 통해서 호출**합니다.

**(5) `__str__` — 객체를 문자열로 표현하기**
```python
class Person3:
    def __str__(self):
        return f"{self.name} ---({self.age})"

p3 = Person3("장영실", 37)
print(p3)   # 장영실 ---(37)
```
- `print(객체)`를 실행하면 파이썬이 내부적으로 **`__str__` 메서드의 반환값**을 출력합니다. 이를 정의하지 않으면 `<__main__.Person3 object at 0x...>`처럼 메모리 주소가 출력됩니다.

**(6) 상속 — `super().__init__()`**
```python
class MyPerson:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Student(MyPerson):
    def __init__(self, name, age, school, grade):
        super().__init__(name, age)   # 부모 클래스의 생성자 호출
        self.school = school
        self.grade = grade
```
- `class Student(MyPerson)`처럼 괄호 안에 부모 클래스를 적으면 **상속(inheritance)** 이 이루어지고, 부모의 속성/메서드를 그대로 물려받습니다.
- `super().__init__(name, age)`는 **부모 클래스의 생성자를 호출**해 공통 속성(`name`, `age`) 초기화를 재사용하고, 자식 클래스에서는 **추가된 속성(`school`, `grade`)만** 따로 처리합니다. 코드 중복을 줄이는 핵심 기법입니다.

**(7) 상속 예시 2 — 공통 속성 + 서로 다른 특화 속성**
```python
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
```
- `Shape`라는 공통 부모를 두고, `Square`는 `width`, `Triangle`은 `height`라는 **서로 다른 특화된 속성**을 추가하는 전형적인 상속 패턴입니다. 도형이라는 공통 개념(`name`)은 부모가, 도형별 고유 속성은 자식이 책임집니다.
- 주석 처리된 `class Student(Person): pass`는 **아무 내용도 추가하지 않고 부모 기능을 그대로 물려받는 가장 단순한 상속 형태**를 보여주려던 예시입니다. (`Person` 클래스가 이 파일에는 정의되어 있어 실행 가능하지만, 뒤에 재정의된 `Person2`, `Person3`과 헷갈리지 않도록 유의가 필요합니다.)

## 핵심 개념 요약

| 개념 | 설명 |
|---|---|
| 위치 인자 / 기본값 / 키워드 인자 | 함수에 값을 전달하는 세 가지 방식 |
| 클래스 vs 인스턴스 | 클래스는 설계도, 인스턴스(객체)는 그 설계도로 만든 실체 |
| `__init__` (생성자) | 객체 생성 시 자동 호출되어 초기 상태를 설정 |
| 메서드 | 클래스 안에 정의되어 객체가 수행하는 동작 |
| `__str__` | `print(객체)` 시 출력될 문자열을 정의 |
| 상속 (`class 자식(부모)`) | 공통 속성/동작을 재사용하고, 자식에서 고유 기능만 추가 |
| `super().__init__()` | 부모 클래스의 생성자를 호출해 초기화 로직 재사용 |

## 알아두면 좋은 점
- 이 예제들은 이후 LangChain/LangGraph에서 다루는 **커스텀 클래스(예: 커스텀 `Document Loader`, 커스텀 `Runnable`, 상태(State) 클래스 등)** 를 이해하기 위한 기초 체력 훈련에 해당합니다. 예를 들어 `ch09_03`의 `HWPLoader(BaseLoader)`도 결국 "부모 클래스를 상속해 필요한 메서드만 구현하는" 동일한 패턴입니다.
- `app.py`에서 실행할 예제 모듈을 바꾸려면 `from .mypy import ex_oop` 줄의 주석을 풀거나(`ex_function`) 바꿔주면 됩니다. 모듈 최상단에 있는 코드가 import 시점에 바로 실행되는 구조이므로, 실습 코드를 추가할 때도 이 패턴을 참고하면 됩니다.
- `my_function4(animal="개", name="철수")`처럼 키워드 인자를 쓰면 인자 순서를 몰라도 호출할 수 있어, 매개변수가 많은 함수(예: LangChain의 `ChatOpenAI(model_name=..., temperature=...)`)를 호출할 때 실무에서도 자주 쓰이는 방식입니다.
