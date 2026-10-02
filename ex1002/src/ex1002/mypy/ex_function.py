def my_function(num1):
    result = num1 + 100
    return result

sum = my_function(77)
print(sum)

# 매개변수의 인수를 똑같이
def my_function2(fname, lname):
    print(fname + " " + lname)

my_function2("길동", "홍")

def my_function3(country = "천안"):
    print("나의 고향은", country)

my_function3("서울")
my_function3("익산")
my_function3()

def my_function4(animal, name):
    print("나의 애완동물", animal)
    print("나의 이름", name)

my_function4(animal="개", name="철수")