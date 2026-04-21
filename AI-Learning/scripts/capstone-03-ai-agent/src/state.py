"""
LangGraph State Definition
==========================

Defines the typed state schema for the AI agent's LangGraph execution graph.
The state flows through graph nodes and edges, accumulating information at
each step of the agent's reasoning process.

The state tracks:
- Input messages and conversation context
- Planned tool calls and their results
- Intermediate reasoning steps
- HITL approval status
- Error state and recovery information
- Final response
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeType(Enum):
    """Types of nodes in the agent graph."""

    PLAN = "plan"
    EXECUTE = "execute"
    OBSERVE = "observe"
    RESPOND = "respond"
    HUMAN_APPROVAL = "human_approval"
    ERROR_HANDLER = "error_handler"


class RoutingDecision(Enum):
    """Decisions for conditional routing between nodes."""

    CONTINUE = "continue"       # Continue to next tool call
    NEED_APPROVAL = "need_approval"  # Route to HITL gate
    RESPOND = "respond"         # Route to response generation
    RETRY = "retry"             # Retry failed tool call
    ERROR = "error"             # Route to error handler


@dataclass
class ToolCall:
    """A planned or executed tool call.

    Attributes
    ----------
    tool_name : str
        Name of the tool to call.
    tool_input : dict
        Input parameters for the tool.
    result : Any, optional
        Tool execution result (populated after execution).
    success : bool
        Whether the tool call succeeded.
    error : str, optional
        Error message if the call failed.
    approved : bool or None
        HITL approval status (None if not applicable).
    """

    tool_name: str
    tool_input: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    success: bool = False
    error: Optional[str] = None
    approved: Optional[bool] = None


@dataclass
class AgentState:
    """Full state for the LangGraph agent execution.

    This dataclass serves as the typed state that flows through the
    LangGraph execution graph. Each node reads and updates relevant
    fields.

    Attributes
    ----------
    messages : list of dict
        Conversation messages in OpenAI format ({'role': ..., 'content': ...}).
    current_query : str
        The current user query being processed.
    plan : list of ToolCall
        Planned tool calls for this turn.
    tool_results : list of ToolCall
        Completed tool calls with results.
    observations : list of str
        Intermediate reasoning observations.
    routing_decision : RoutingDecision
        Decision for the next node to route to.
    response : str
        The final response to return to the user.
    iteration : int
        Current plan-execute-observe loop iteration.
    max_iterations : int
        Maximum iterations before forced response.
    error : str or None
        Current error state.
    metadata : dict
        Execution metadata (timing, trace IDs, etc.).
    """

    messages: List[Dict[str, str]] = field(default_factory=list)
    current_query: str = ""
    plan: List[ToolCall] = field(default_factory=list)
    tool_results: List[ToolCall] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    routing_decision: RoutingDecision = RoutingDecision.CONTINUE
    response: str = ""
    iteration: int = 0
    max_iterations: int = 10
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def should_continue(state: AgentState) -> str:
    """Conditional edge function: decide next node based on state.

    Used by LangGraph to determine routing after the observe node.

    Parameters
    ----------
    state : AgentState
        Current agent state.

    Returns
    -------
    str
        Name of the next node to route to.
    """
    raise NotImplementedError


def should_request_approval(state: AgentState) -> str:
    """Conditional edge function: check if HITL approval is needed.

    Used by LangGraph before tool execution to determine if
    human approval is required for any planned tool calls.

    Parameters
    ----------
    state : AgentState
        Current agent state.

    Returns
    -------
    str
        'human_approval' if approval needed, 'execute' otherwise.
    """
    raise NotImplementedError


def create_initial_state(
    query: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    max_iterations: int = 10,
) -> AgentState:
    """Create the initial agent state for a new query.

    Parameters
    ----------
    query : str
        The user's query.
    conversation_history : list of dict, optional
        Prior conversation messages.
    max_iterations : int
        Maximum reasoning iterations.

    Returns
    -------
    AgentState
        Initial state ready for graph execution.
    """
    messages = list(conversation_history) if conversation_history else []
    messages.append({"role": "user", "content": query})

    return AgentState(
        messages=messages,
        current_query=query,
        max_iterations=max_iterations,
    )
