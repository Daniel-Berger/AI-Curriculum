"""
AI Agent Module
===============

Core agent implementation using LangGraph for structured state management
and multi-step reasoning. The agent follows a plan-execute-observe loop
with support for parallel tool calls, human-in-the-loop approvals, and
graceful error recovery.

Architecture:
- LangGraph StateGraph defines the execution flow
- Nodes: plan, execute_tools, observe, respond, human_approval
- Conditional edges route based on tool requirements and HITL policies
- Checkpointing enables pause/resume and conversation persistence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .memory import AgentMemory
from .state import AgentState
from .tools import ToolRegistry


class AgentStatus(Enum):
    """Current status of the agent."""

    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    RESPONDING = "responding"
    ERROR = "error"


@dataclass
class AgentConfig:
    """Configuration for the AI agent.

    Attributes
    ----------
    model_name : str
        LLM model to use for reasoning.
    temperature : float
        Sampling temperature.
    max_iterations : int
        Maximum plan-execute-observe loops before forcing a response.
    enable_hitl : bool
        Whether to enable human-in-the-loop approvals.
    hitl_tools : list of str
        Tool names that require human approval before execution.
    enable_memory : bool
        Whether to enable persistent memory.
    max_tokens : int
        Maximum tokens per LLM call.
    """

    model_name: str = "gpt-4o"
    temperature: float = 0.1
    max_iterations: int = 10
    enable_hitl: bool = True
    hitl_tools: List[str] = field(default_factory=lambda: ["code_executor"])
    enable_memory: bool = True
    max_tokens: int = 4096


class AIAgent:
    """Production AI agent with LangGraph state management.

    Parameters
    ----------
    config : AgentConfig, optional
        Agent configuration. Uses defaults if not provided.
    tool_registry : ToolRegistry, optional
        Registry of available tools.
    memory : AgentMemory, optional
        Memory system for the agent.

    Examples
    --------
    >>> agent = AIAgent()
    >>> response = agent.invoke("What is the weather in San Francisco?")
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        tool_registry: Optional[ToolRegistry] = None,
        memory: Optional[AgentMemory] = None,
    ) -> None:
        self.config = config or AgentConfig()
        self.tool_registry = tool_registry or ToolRegistry()
        self.memory = memory or AgentMemory()
        self.status = AgentStatus.IDLE
        self._graph: Optional[Any] = None  # LangGraph StateGraph
        self._checkpointer: Optional[Any] = None

    def build_graph(self) -> Any:
        """Build the LangGraph state graph for agent execution.

        Creates nodes for planning, tool execution, observation,
        human approval, and response generation. Connects them
        with conditional edges.

        Returns
        -------
        Any
            Compiled LangGraph StateGraph.
        """
        raise NotImplementedError

    def invoke(
        self,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> str:
        """Process a user message and return the agent's response.

        Parameters
        ----------
        message : str
            The user's input message.
        conversation_id : str, optional
            ID for conversation continuity. Creates new if not provided.

        Returns
        -------
        str
            The agent's response.
        """
        raise NotImplementedError

    async def ainvoke(
        self,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> str:
        """Async version of invoke.

        Parameters
        ----------
        message : str
            The user's input message.
        conversation_id : str, optional
            Conversation ID for continuity.

        Returns
        -------
        str
            The agent's response.
        """
        raise NotImplementedError

    def plan(self, state: AgentState) -> AgentState:
        """Planning node: decide which tools to call and in what order.

        Parameters
        ----------
        state : AgentState
            Current agent state.

        Returns
        -------
        AgentState
            Updated state with the execution plan.
        """
        raise NotImplementedError

    def execute_tools(self, state: AgentState) -> AgentState:
        """Execution node: run the planned tool calls.

        Parameters
        ----------
        state : AgentState
            Current state with pending tool calls.

        Returns
        -------
        AgentState
            Updated state with tool results.
        """
        raise NotImplementedError

    def observe(self, state: AgentState) -> AgentState:
        """Observation node: analyze tool results and decide next steps.

        Parameters
        ----------
        state : AgentState
            Current state with tool results.

        Returns
        -------
        AgentState
            Updated state with observations and routing decision.
        """
        raise NotImplementedError

    def respond(self, state: AgentState) -> AgentState:
        """Response node: generate the final answer to the user.

        Parameters
        ----------
        state : AgentState
            Final state with all gathered information.

        Returns
        -------
        AgentState
            State with the final response.
        """
        raise NotImplementedError

    def request_human_approval(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> bool:
        """Request human approval for a sensitive tool call.

        Parameters
        ----------
        tool_name : str
            Name of the tool requesting approval.
        tool_input : dict
            The input that would be passed to the tool.

        Returns
        -------
        bool
            True if approved, False if rejected.
        """
        raise NotImplementedError

    def handle_error(
        self, state: AgentState, error: Exception
    ) -> AgentState:
        """Handle errors during agent execution with recovery strategies.

        Parameters
        ----------
        state : AgentState
            Current state when error occurred.
        error : Exception
            The exception that was raised.

        Returns
        -------
        AgentState
            Recovered state (may include fallback response).
        """
        raise NotImplementedError

    def get_execution_trace(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve the execution trace for a conversation.

        Parameters
        ----------
        conversation_id : str
            The conversation to trace.

        Returns
        -------
        list of dict
            Ordered list of execution steps with timing and results.
        """
        raise NotImplementedError
