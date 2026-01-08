from langgraph.graph import add_messages
from pydantic import BaseModel
from typing import Annotated, List, Optional


class AgentState(BaseModel):
    messages: Annotated[List, add_messages] = []
    customer_id: str = ""
    authenticated_user_id: Optional[str] = None  # User ID after PIN verification
    authenticated_user_name: Optional[str] = None  # User name for personalization
    is_authenticated: bool = False  # Whether user has been authenticated
    request_id: Optional[str] = None  # Request ID for tool execution tracking
