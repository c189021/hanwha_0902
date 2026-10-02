from .page86 import page86_ai_msg

def sub():
    print("메인에서 실행하는 서브함수")
    

def main() -> None:
    # print("메인화면 : app.py")
    # sub()

    # page86.py
    page86_ai_msg()

    # page95.py
    # 내부에 함수가 없을때, 문서 전체를 실행
    from . import page95

    # page99.py
    from . import page99

    # page101.py 랭그래프
    from . import page101


    
    
    




    
    