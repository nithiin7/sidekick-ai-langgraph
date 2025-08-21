"""
State management for the Sidekick AI application.
Defines the state structure and validation for the LangGraph workflow.
"""

from typing import Annotated, List, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class State(TypedDict):
    """State structure for the LangGraph workflow."""
    messages: Annotated[List[Any], add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool


class EvaluatorOutput(BaseModel):
    """Output model for the evaluator node."""
    feedback: str = Field(
        description="Feedback on the assistant's response"
    )
    success_criteria_met: bool = Field(
        description="Whether the success criteria have been met"
    )
    user_input_needed: bool = Field(
        description="True if more input is needed from the user, or clarifications, or the assistant is stuck"
    )


def create_initial_state(message: str, success_criteria: str) -> State:
    """Create initial state for a new conversation."""
    return {
        "messages": message,
        "success_criteria": success_criteria or "The answer should be clear and accurate",
        "feedback_on_work": None,
        "success_criteria_met": False,
        "user_input_needed": False,
    }
