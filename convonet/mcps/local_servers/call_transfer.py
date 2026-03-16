"""
Call Transfer Tools for LangChain Agent
Provides tools for transferring voice calls to human agents
"""

from typing import List, Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import os


class TransferToAgentInput(BaseModel):
    """Input schema for transfer_to_agent tool"""
    department: str = Field(
        default="support",
        description="Department or team to transfer to (e.g., 'support', 'sales', 'technical')"
    )
    reason: str = Field(
        default="User requested transfer to human agent",
        description="Reason for the transfer request"
    )
    extension: Optional[str] = Field(
        default=None,
        description="Specific extension number to transfer to (optional, will use default if not provided)"
    )


class GetAvailableDepartmentsInput(BaseModel):
    """Input schema for get_available_departments tool"""
    pass


def _transfer_to_agent_impl(department: str = "support", reason: str = "User requested transfer to human agent", extension: Optional[str] = None) -> str:
    """Transfer the current voice call to a human agent or department. Returns TRANSFER_INITIATED marker."""
    target_extension = extension or os.getenv('VOICE_AGENT_FALLBACK_EXTENSION', '2001')
    default_department = os.getenv('VOICE_AGENT_FALLBACK_DEPARTMENT', 'support')
    target_department = department if department else default_department
    return f"TRANSFER_INITIATED:{target_extension}|{target_department}|{reason}"


def _get_available_departments_impl() -> str:
    """Get a list of available departments that users can be transferred to."""
    departments_env = os.getenv('VOICE_AGENT_DEPARTMENTS', 'support,sales,technical')
    departments = [d.strip() for d in departments_env.split(',')]
    default_extension = os.getenv('VOICE_AGENT_FALLBACK_EXTENSION', '2001')
    result = "Available departments for transfer:\n"
    for dept in departments:
        result += f"- {dept.title()} (extension {default_extension})\n"
    result += "\nYou can transfer the user by saying 'transfer to [department]' or use the transfer_to_agent tool."
    return result


def transfer_to_agent_tool() -> StructuredTool:
    """Tool to transfer a voice call to a human agent or department"""
    return StructuredTool.from_function(
        func=_transfer_to_agent_impl,
        name="transfer_to_agent",
        description="""Transfer the current voice call to a human agent or department. 
        Use this when the user requests to speak with a human, agent, representative, or specific department.
        Examples: 'transfer me', 'speak to agent', 'talk to human', 'transfer to sales', 'I need help from support'.
        This tool will initiate the transfer process immediately.""",
        args_schema=TransferToAgentInput,
    )


def get_available_departments_tool() -> StructuredTool:
    """Tool to get list of available departments for transfer"""
    return StructuredTool.from_function(
        func=_get_available_departments_impl,
        name="get_available_departments",
        description="""Get a list of available departments that users can be transferred to.
        Use this when the user asks 'what departments are available?', 'who can I talk to?', or 'what are my options?'.
        This helps users understand their transfer options.""",
        args_schema=GetAvailableDepartmentsInput,
    )


def get_transfer_tools() -> List[StructuredTool]:
    """
    Get all call transfer tools for the LangChain agent.
    
    Returns:
        List of StructuredTool instances for call transfer functionality
    """
    return [
        transfer_to_agent_tool(),
        get_available_departments_tool()
    ]

