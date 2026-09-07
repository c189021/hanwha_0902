"""
NumPy 예시 2 - 실전: 배열 조작과 통계/집계 함수
실행: pip install numpy  (설치 후) -> python numpy2.py
"""

import numpy as np


# ----------------------------------------------------------------------
# 1) 배열 형태 변경 (reshape, transpose)
# ----------------------------------------------------------------------
def example_reshape_and_transpose():
    print("\n[1] 배열 형태 변경 (reshape, transpose)")

    arr = np.arange(1, 13)  # 1~12, 1차원 배열
    print("원본 1차원 배열:", arr)

    # 형태를 (3, 4)로 변경 -> 3행 4열 행렬
    matrix = arr.reshape(3, 4)
    print("reshape(3, 4):\n", matrix)

    # 행과 열을 뒤바꾸기
    print("transpose (행/열 전환):\n", matrix.T)

    # 여러 배열 이어 붙이기
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    print("세로로 이어 붙이기 (axis=0):\n", np.concatenate([a, b], axis=0))
    print("가로로 이어 붙이기 (axis=1):\n", np.concatenate([a, b], axis=1))


# ----------------------------------------------------------------------
# 2) axis 개념과 통계 함수
# ----------------------------------------------------------------------
def example_axis_and_statistics():
    print("\n[2] axis 개념과 통계 함수")

    # 3명의 학생 x 4과목 점수
    scores = np.array([
        [80, 90, 70, 60],
        [70, 60, 80, 90],
        [90, 80, 60, 70],
    ])
    print("점수표 (행=학생, 열=과목):\n", scores)

    # axis=0 -> 세로 방향(행끼리) 연산 -> 과목별 결과
    print("과목별 평균 (axis=0):", scores.mean(axis=0))
    # axis=1 -> 가로 방향(열끼리) 연산 -> 학생별 결과
    print("학생별 평균 (axis=1):", scores.mean(axis=1))

    print("전체 최댓값:", scores.max())
    print("과목별 최댓값 (axis=0):", scores.max(axis=0))
    print("학생별 총점 (axis=1):", scores.sum(axis=1))
    print("표준편차 (axis=1):", scores.std(axis=1))


# ----------------------------------------------------------------------
# 3) 정렬과 조건 필터링 (불리언 인덱싱 / where)
# ----------------------------------------------------------------------
def example_sorting_and_filtering():
    print("\n[3] 정렬과 조건 필터링")

    arr = np.array([50, 10, 40, 20, 30])
    print("원본 배열:", arr)
    print("오름차순 정렬:", np.sort(arr))
    print("정렬했을 때의 원래 인덱스 (argsort):", np.argsort(arr))

    # 조건에 맞는 값만 뽑아내는 불리언 인덱싱
    mask = arr > 25
    print("25보다 큰 값인지 여부:", mask)
    print("25보다 큰 값만 필터링:", arr[mask])

    # np.where: 조건에 따라 다른 값으로 치환
    labels = np.where(arr >= 30, "합격", "불합격")
    print("30 이상이면 합격, 아니면 불합격:", labels)


if __name__ == "__main__":
    example_reshape_and_transpose()
    example_axis_and_statistics()
    example_sorting_and_filtering()
