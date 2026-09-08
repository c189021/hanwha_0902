"""
NumPy 예시 3 - 응용: 데이터 전처리 파이프라인 (원본 데이터 -> 정제 -> 정규화 -> 요약)
실행: pip install numpy  (설치 후) -> ex0907 폴더에서 python numpy/numpy3.py
"""

import numpy as np


# ----------------------------------------------------------------------
# 원본 데이터: 5명의 시험 점수 (결측치 포함, 실제 데이터처럼 일부러 NaN 섞음)
# ----------------------------------------------------------------------
RAW_SCORES = np.array([85.0, 92.0, np.nan, 78.0, np.nan, 88.0, 95.0])


# ----------------------------------------------------------------------
# 1) 원본 데이터 확인 + 결측치 정제
# ----------------------------------------------------------------------
def clean_scores(raw: np.ndarray) -> np.ndarray:
    """결측치(NaN)가 있는지 확인하고, NaN을 제외한 배열을 반환"""
    print("원본 데이터:", raw)

    nan_mask = np.isnan(raw)
    print("NaN 여부:", nan_mask)
    print("NaN 개수:", np.sum(nan_mask))

    cleaned = raw[~nan_mask]  # NaN이 아닌 값만 남김
    print("정제된 데이터:", cleaned)
    return cleaned


# ----------------------------------------------------------------------
# 2) 정규화(표준화): (x - 평균) / 표준편차
# ----------------------------------------------------------------------
def normalize_scores(cleaned: np.ndarray) -> np.ndarray:
    """평균 0, 표준편차 1이 되도록 데이터를 표준화(z-score)"""
    mean = cleaned.mean()
    std = cleaned.std()
    normalized = (cleaned - mean) / std
    print(f"평균: {mean:.2f}, 표준편차: {std:.2f}")
    print("정규화된 데이터 (z-score):", np.round(normalized, 2))
    return normalized


# ----------------------------------------------------------------------
# 3) 통계 요약 결과 만들기
# ----------------------------------------------------------------------
def summarize(cleaned: np.ndarray) -> dict:
    """최종적으로 서비스/리포트에서 쓸 수 있는 요약 통계 dict를 생성"""
    summary = {
        "count": int(cleaned.size),
        "mean": round(float(cleaned.mean()), 2),
        "std": round(float(cleaned.std()), 2),
        "min": float(cleaned.min()),
        "max": float(cleaned.max()),
        "median": float(np.median(cleaned)),
    }
    return summary


# ----------------------------------------------------------------------
# 전체 흐름: 원본 데이터 -> 정제 -> 정규화 -> 요약
# ----------------------------------------------------------------------
def example_pipeline():
    print("\n[1] 원본 -> 정제")
    cleaned = clean_scores(RAW_SCORES)

    print("\n[2] 정제 -> 정규화")
    normalize_scores(cleaned)

    print("\n[3] 정제된 데이터 -> 요약 통계")
    summary = summarize(cleaned)
    print("요약 통계 결과:", summary)


if __name__ == "__main__":
    example_pipeline()
