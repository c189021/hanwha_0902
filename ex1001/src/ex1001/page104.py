from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1. 상태(State) 정의
class State(TypedDict):
    text: str
    response: str

# 2. 노드(Node) 함수 정의
def check_input(state: State):
    print(f"--- 입력 확인: {state['text']} ---")
    return state

def answer_question(state: State):
    print("--- 질문 처리 중 ---")
    return {"response": "질문에 대한 답변입니다."}

# 3. 조건부 에지 라우팅 함수 정의
def decide_next_node(state: State):
    # 입력 텍스트에 '질문'이라는 단어가 있으면 answer 노드로, 없으면 종료
    if "질문" in state["text"]:
        return "answer"
    else:
        return "end"

# 4. 그래프 생성 및 노드 추가
workflow = StateGraph(State)

workflow.add_node("check", check_input)
workflow.add_node("answer", answer_question)

# 시작점 설정
workflow.set_entry_point("check")

# 5. 조건부 에지 추가 (*** 핵심! ***)
workflow.add_conditional_edges(
    "check",             # 시작 노드
    decide_next_node,    # 다음 노드를 결정할 라우팅 함수
    {
        "answer": "answer", # 라우팅 함수 반환값 : 이동할 노드 이름
        "end": END
    }
)

# answer 노드 다음은 항상 종료
workflow.add_edge("answer", END)

# ------------------ 그래프 -----------------
# graph TD;
#         __start__([<p>__start__</p>]):::first
#         chatbot(chatbot)
#         __end__([<p>__end__</p>]):::last
#         __start__ --> chatbot;
#         chatbot --> __end__;
#         classDef default fill:#f2f0ff,line-height:1.2
#         classDef first fill-opacity:0
#         classDef last fill:#bfb6fc
# -------------------------------------------

# 6. 그래프 컴파일
app = workflow.compile()
print("^^^page104 챗봇서비스를 시작합니다 ^^^")


# ----- 실행1 : 조건에 맞아(질문을 포함) ------
result1 = app.invoke({"text": "안녕하세요, 질문이 있습니다."})
# --- 입력 확인: 안녕하세요, 질문이 있습니다. ---
# --- 질문 처리 중 ---

# ----- 실행2 : 조건에 맞아(질문 없음) ------
result2 = app.invoke({"text": "안녕하세요, 반갑습니다."})
# --- 입력 확인: 안녕하세요, 반갑습니다. ---

print(result1)
print(result2)