"""교사용 패키지의 Streamlit 페이지 인증 기능.

교육생용 챗봇 코드와 교사용 기능을 분리하기 위해 인증 처리는 이 파일에서만
담당한다. 요청된 실습용 비밀번호는 ``4365``이며, 인증 결과만 세션에 저장한다.
"""

from __future__ import annotations

import hmac

import streamlit as st

# 교육생에게 배포되는 실습 프로젝트에서 사용할 교사용 고정 비밀번호.
# 운영 환경에서는 환경 변수나 별도의 비밀 저장소를 사용하는 것이 안전하다.
TEACHER_PASSWORD = "4365"
AUTH_SESSION_KEY = "teacher_authenticated"


def verify_teacher_password(password: str) -> bool:
    """입력값이 교사용 비밀번호와 일치하는지 안전하게 비교한다."""
    return hmac.compare_digest(password, TEACHER_PASSWORD)


def require_teacher_login() -> bool:
    """교사용 로그인 화면을 표시하고 현재 인증 여부를 반환한다."""
    if st.session_state.get(AUTH_SESSION_KEY, False):
        with st.sidebar:
            st.success("교사용 인증 완료")
            if st.button("교사용 로그아웃", use_container_width=True):
                st.session_state[AUTH_SESSION_KEY] = False
                st.rerun()
        return True

    st.title("🔐 교사용 페이지")
    st.caption("합성 테스트 데이터셋 생성 기능은 교사용 비밀번호가 필요합니다.")

    with st.form("teacher_login_form"):
        password = st.text_input(
            "교사용 비밀번호",
            type="password",
            placeholder="비밀번호 입력",
        )
        submitted = st.form_submit_button(
            "로그인", type="primary", use_container_width=True
        )

    if submitted:
        if verify_teacher_password(password):
            st.session_state[AUTH_SESSION_KEY] = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    return False
