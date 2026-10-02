from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langgraph.graph.message import add_messages

load_dotenv()

# ==== 메세지를 병합하는 리듀서 함수 ===
def add(left, right):
    return left + right

# 상태값 리듀서 ----- start ------
class State(TypedDict):
    # 리듀서가 지정된 필드(add 리듀서를 사용)
    messages:Annotated[list[str], add]
# -------------------  end  -------

# 기존state : HumanMessage
msgs1 = [HumanMessage(content="Hello", id=1)]

# 노드반환값 : AIMessage
msgs2 = [AIMessage(content="Hi there", id=2)]


# 에이전트에 들어온 메세지 저장용: add_messages
result = add_messages(msgs1, msgs2)
print(type(result))
# <class 'list'>
print(result)
# [HumanMessage(content='Hello', additional_kwargs={}, response_metadata={}, id='1'), 
# AIMessage(content='Hi there', additional_kwargs={}, response_metadata={}, id='2', 
# tool_calls=[], invalid_tool_calls=[])]



# ----- id가 같으면, 덮어씀 -----
msg3 = [HumanMessage(content="안녕", id=3)]
msg5 = [HumanMessage(content="안녕-아이디 같아서 덮어씀", id=3)]
result2 = add_messages(msg3, msg5)
print(result2)
# [HumanMessage(content='안녕-아이디 같아서 덮어씀', 
# additional_kwargs={}, response_metadata={}, id='3')]