# =============================================================================
# proj_streamlit/chat_app.py  -  챗봇 화면(프론트엔드)
# =============================================================================
# [전체 구조]
#   Streamlit(chat_app.py, 이 파일)  ──HTTP POST──▶  FastAPI(chat.py)
#                                    ◀──JSON 응답──
#
#   - 이 파일은 채팅창을 보여주고, 내가 친 메시지를 서버로 보낸 뒤
#     서버가 준 답변을 화면에 띄운다. (답을 고르는 일은 서버가 함)
#
# [실행 순서 - 중요]
#   1) 먼저 백엔드 실행:  cd proj_fastapi && uvicorn chat:app --reload
#   2) 그다음 이 파일 실행: cd proj_streamlit && streamlit run chat_app.py
# =============================================================================

import streamlit as st
import requests

# FastAPI 서버 주소 (uvicorn 기본 주소와 같아야 함)
FASTAPI_URL = "http://127.0.0.1:8000"

st.title("아주 간단한 챗봇")


# -----------------------------------------------------------------------------
# 1) 대화 기록을 담아둘 공간 만들기
# -----------------------------------------------------------------------------
# Streamlit은 화면이 새로 그려질 때마다 코드를 처음부터 다시 실행한다.
# 그래서 대화 내용을 st.session_state 에 저장해 둬야 사라지지 않는다.
if "messages" not in st.session_state:
    st.session_state.messages = []   # 예: [{"role": "user", "content": "안녕"}]


# -----------------------------------------------------------------------------
# 2) 지금까지의 대화를 화면에 다시 그리기
# -----------------------------------------------------------------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):   # "user" 또는 "assistant"
        st.write(m["content"])


# -----------------------------------------------------------------------------
# 3) 아래쪽 입력창 (엔터를 치면 user_input 에 글자가 들어옴)
# -----------------------------------------------------------------------------
user_input = st.chat_input("메시지를 입력하세요")

if user_input:
    # (1) 내가 보낸 메시지 저장 + 화면에 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # (2) FastAPI 서버로 메시지를 보내고 답변을 받아옴
    try:
        response = requests.post(f"{FASTAPI_URL}/chat", json={"text": user_input})
        bot_reply = response.json()["reply"]
    except requests.exceptions.ConnectionError:
        bot_reply = "서버에 연결할 수 없어요. FastAPI 서버가 켜져 있는지 확인해 주세요."

    # (3) 챗봇 답변 저장 + 화면에 표시
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.write(bot_reply)
