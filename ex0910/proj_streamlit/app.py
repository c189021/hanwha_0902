# =============================================================================
# proj_streamlit/app.py  -  프론트엔드(화면 + 요청) 역할
# =============================================================================
# [전체 구조]
#   Streamlit(app.py, 이 파일)  ──HTTP POST──▶  FastAPI(main.py, 백엔드)
#                               ◀──JSON 응답──
#
#   - 이 파일은 사용자에게 입력 폼을 보여주고,
#     입력값을 FastAPI 서버(/predict)로 보낸 뒤 응답을 화면에 표시한다.
#   - 계산/판단 로직은 여기 없고 전부 FastAPI 쪽에 있다. (역할 분리)
#
# [실행 순서 - 중요]
#   1) 먼저 백엔드 실행:  cd proj_fastapi && uvicorn main:app --reload
#   2) 그다음 이 파일 실행: cd proj_streamlit && streamlit run app.py
#   (백엔드가 꺼져 있으면 아래 ConnectionError 처리 구문이 동작한다.)
# =============================================================================

import streamlit as st   # 화면 UI를 만드는 라이브러리
import requests          # FastAPI 서버로 HTTP 요청을 보내는 라이브러리

# FastAPI 백엔드 URL (uvicorn 기본 주소와 일치해야 함)
FASTAPI_URL = "http://127.0.0.1:8000"

# 페이지 제목
st.title("Streamlit & FastAPI 연결 예제")


# -----------------------------------------------------------------------------
# 1) 입력 폼 구성
# -----------------------------------------------------------------------------
# st.form 으로 묶으면, 값을 여러 개 바꿔도 '전송' 버튼을 눌러야 한 번에 제출된다.
with st.form("user_form"):
    name = st.text_input("이름", value="홍길동")
    age = st.number_input("나이", min_value=1, max_value=120, value=20)
    submit_button = st.form_submit_button("백엔드로 전송")   # 제출 버튼


# -----------------------------------------------------------------------------
# 2) 버튼이 눌렸을 때만 실행되는 블록
# -----------------------------------------------------------------------------
if submit_button:
    # FastAPI로 보낼 데이터 (main.py의 UserInput 스키마와 필드명이 같아야 함)
    payload = {
        "name": name,
        "age": age
    }

    try:
        # 3) FastAPI의 POST /predict 엔드포인트로 요청 전송
        #    json=payload -> 파이썬 dict가 JSON 본문으로 변환되어 전송됨
        response = requests.post(f"{FASTAPI_URL}/predict", json=payload)

        # 4) 응답 처리
        if response.status_code == 200:                 # 200 = 정상 응답
            result = response.json()                    # 응답 JSON -> dict
            st.success("FastAPI 응답 성공!")
            # main.py가 돌려준 "result_message" 키를 꺼내 화면에 출력
            st.write(f"**결과:** {result['result_message']}")
        else:
            # 서버가 응답은 했지만 에러 상태 코드인 경우 (예: 422 검증 실패)
            st.error(f"오류 발생 (상태 코드: {response.status_code})")

    except requests.exceptions.ConnectionError:
        # 백엔드 서버 자체에 연결이 안 되는 경우 (uvicorn 미실행 등)
        st.error("FastAPI 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요.")
