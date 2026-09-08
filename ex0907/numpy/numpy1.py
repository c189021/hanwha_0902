"""
NumPy 예시 1 - 기본: 배열 생성과 기본 연산
실행: pip install numpy  (설치 후) -> ex0907 폴더에서 python numpy/numpy1.py
"""

import numpy as np


# ----------------------------------------------------------------------
# 1) 배열 생성과 속성 확인
# ----------------------------------------------------------------------
def example_array_creation():
    print("\n[1] 배열 생성과 속성 확인")

    # 리스트로부터 1차원 배열 생성
    arr1 = np.array([1, 2, 3, 4, 5])
    print("1차원 배열:", arr1)

    # 중첩 리스트로부터 2차원 배열 생성
    arr2 = np.array([[1, 2, 3], [4, 5, 6]])
    print("2차원 배열:\n", arr2)

    # 배열의 주요 속성
    print("shape (행, 열):", arr2.shape)
    print("ndim (차원 수):", arr2.ndim)
    print("size (전체 원소 개수):", arr2.size)
    print("dtype (원소 타입):", arr2.dtype)

    # 자주 쓰는 생성 함수들
    print("0으로 채운 배열:\n", np.zeros((2, 3)))
    print("1로 채운 배열:\n", np.ones((2, 3)))
    print("연속된 값 (arange):", np.arange(0, 10, 2))
    print("구간을 등분 (linspace):", np.linspace(0, 1, 5))


# ----------------------------------------------------------------------
# 2) 벡터화 연산과 브로드캐스팅
# ----------------------------------------------------------------------
def example_vectorized_operations():
    print("\n[2] 벡터화 연산과 브로드캐스팅")

    a = np.array([1, 2, 3])
    b = np.array([10, 20, 30])

    # 파이썬 반복문 없이 원소별로 자동 연산됨 (벡터화 연산)
    print("a + b =", a + b)
    print("a * b =", a * b)
    print("a ** 2 =", a ** 2)

    # 배열과 스칼라 값 사이의 연산 -> 브로드캐스팅 (스칼라가 배열 크기에 맞춰 확장됨)
    print("a + 10 =", a + 10)

    # 크기가 다른 배열끼리도 규칙에 맞으면 자동으로 broadcasting 됨
    matrix = np.array([[1, 2, 3], [4, 5, 6]])
    row = np.array([10, 20, 30])
    print("행렬 + 1행 벡터 (브로드캐스팅):\n", matrix + row)


# ----------------------------------------------------------------------
# 3) 인덱싱과 슬라이싱
# ----------------------------------------------------------------------
def example_indexing_and_slicing():
    print("\n[3] 인덱싱과 슬라이싱")

    arr = np.array([10, 20, 30, 40, 50])
    print("전체 배열:", arr)
    print("arr[1] =", arr[1])
    print("arr[1:4] (슬라이싱) =", arr[1:4])
    print("arr[-1] (마지막 원소) =", arr[-1])

    matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print("2차원 배열:\n", matrix)
    print("matrix[0, 2] (0행 2열) =", matrix[0, 2])
    print("matrix[1] (1행 전체) =", matrix[1])
    print("matrix[:, 1] (모든 행의 1열) =", matrix[:, 1])
    print("matrix[0:2, 0:2] (부분 행렬) =\n", matrix[0:2, 0:2])


if __name__ == "__main__":
    example_array_creation()
    example_vectorized_operations()
    example_indexing_and_slicing()
