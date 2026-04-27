from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import operator

load_dotenv()


class SupportState(TypedDict):
    """State for the support agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    should_escalate: bool
    issue_type: str
    user_tier: str  # "vip" or "standard"
    order_status: str
    tracking_id: Annotated[int, operator.add]
    sentiment: str
    discount_code: str
    message_to_user: str