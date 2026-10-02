# from 같은경로의 app파일
# import app파일 안에 있는 main()
from .app import main

__all__ = ["main"]


# --- 프로젝트 초기화 --- 
print("프로젝트 초기화 init")