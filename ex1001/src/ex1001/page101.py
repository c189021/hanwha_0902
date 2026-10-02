from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import END, START, StateGraph

from .page100 import State

class State(TypedDict):
    messages: Annotated[list[str], add]

graph = StateGraph(State)

def chatbot(state:State):
    question = state["messages"]
    answer = f"사용자 입력을 그대로 반환하는 챗봇입니다. {question}라는 질문을 받았음."
    return {"messages": [answer]}

graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

# graph.add_edge("node_a", "node_b")

# 그래프 구조를 Mermaid 문법으로 터미널에 출력.
print("------------------")
app = graph.compile()
print(app.get_graph().draw_mermaid())
print("------------------")

# Mermaid 그래프의 동작 순서
# __start__ → chatbot → __end__

# ----- 그래프 실행 해보기