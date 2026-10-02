from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

load_dotenv()

class State(TypedDict):
    messages:Annotated[list[AnyMessage], add_messages]