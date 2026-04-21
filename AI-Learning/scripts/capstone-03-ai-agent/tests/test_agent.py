"""
Agent Tests
===========

Unit tests for the AI agent components. Tests cover the agent core,
tool registry, memory system, and state management. Uses mocked LLM
calls and tool executions.
"""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent import AgentConfig, AgentStatus, AIAgent
from src.memory import AgentMemory, ConversationTurn, MemoryEntry
from src.state import (
    AgentState,
    RoutingDecision,
    ToolCall,
    create_initial_state,
)
from src.tools import (
    BaseTool,
    CalculatorTool,
    CodeExecutorTool,
    ToolRegistry,
    ToolResult,
    WebSearchTool,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def agent_config() -> AgentConfig:
    """Create a test agent configuration."""
    return AgentConfig(
        model_name="gpt-4o",
        max_iterations=5,
        enable_hitl=False,
        enable_memory=False,
    )


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Create a tool registry with default tools."""
    registry = ToolRegistry()
    registry.register_defaults()
    return registry


@pytest.fixture
def memory() -> AgentMemory:
    """Create an agent memory instance."""
    return AgentMemory(
        max_conversation_turns=10,
        enable_long_term=False,
    )


@pytest.fixture
def agent(
    agent_config: AgentConfig,
    tool_registry: ToolRegistry,
    memory: AgentMemory,
) -> AIAgent:
    """Create a fully configured agent for testing."""
    return AIAgent(
        config=agent_config,
        tool_registry=tool_registry,
        memory=memory,
    )


# ---------------------------------------------------------------------------
# Tool Registry Tests
# ---------------------------------------------------------------------------


class TestToolRegistry:
    """Tests for the ToolRegistry."""

    def test_register_defaults(self, tool_registry: ToolRegistry) -> None:
        """Default tools should be registered."""
        tools = tool_registry.list_tools()
        tool_names = [t.name for t in tools]
        assert "web_search" in tool_names
        assert "calculator" in tool_names
        assert "code_executor" in tool_names

    def test_get_existing_tool(self, tool_registry: ToolRegistry) -> None:
        """Should return a registered tool by name."""
        tool = tool_registry.get_tool("calculator")
        assert isinstance(tool, CalculatorTool)

    def test_get_nonexistent_tool_raises(
        self, tool_registry: ToolRegistry
    ) -> None:
        """Should raise KeyError for unregistered tools."""
        with pytest.raises(KeyError, match="Tool not found"):
            tool_registry.get_tool("nonexistent_tool")

    def test_execute_tool_raises_not_implemented(
        self, tool_registry: ToolRegistry
    ) -> None:
        """Tool execution should raise NotImplementedError until implemented."""
        with pytest.raises(NotImplementedError):
            tool_registry.execute("calculator", expression="2 + 2")


# ---------------------------------------------------------------------------
# Memory Tests
# ---------------------------------------------------------------------------


class TestAgentMemory:
    """Tests for the AgentMemory system."""

    def test_init_defaults(self, memory: AgentMemory) -> None:
        """Memory should initialize with configured settings."""
        assert memory.max_conversation_turns == 10
        assert memory.enable_long_term is False

    def test_clear_conversation(self, memory: AgentMemory) -> None:
        """clear_conversation should remove the conversation buffer."""
        memory._conversation_buffer["test"] = [
            ConversationTurn(role="user", content="hi")
        ]
        memory.clear_conversation("test")
        assert "test" not in memory._conversation_buffer

    def test_add_turn_raises_not_implemented(
        self, memory: AgentMemory
    ) -> None:
        """add_turn should raise NotImplementedError until implemented."""
        turn = ConversationTurn(role="user", content="hello")
        with pytest.raises(NotImplementedError):
            memory.add_turn(turn)


# ---------------------------------------------------------------------------
# State Tests
# ---------------------------------------------------------------------------


class TestAgentState:
    """Tests for the agent state management."""

    def test_create_initial_state(self) -> None:
        """create_initial_state should produce a valid initial state."""
        state = create_initial_state("What is AI?")
        assert state.current_query == "What is AI?"
        assert len(state.messages) == 1
        assert state.messages[0]["role"] == "user"
        assert state.iteration == 0
        assert state.routing_decision == RoutingDecision.CONTINUE

    def test_create_initial_state_with_history(self) -> None:
        """Should include conversation history in the state."""
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]
        state = create_initial_state("What is AI?", conversation_history=history)
        assert len(state.messages) == 3
        assert state.messages[-1]["content"] == "What is AI?"

    def test_tool_call_dataclass(self) -> None:
        """ToolCall should store tool invocation details."""
        tc = ToolCall(
            tool_name="web_search",
            tool_input={"query": "AI news"},
        )
        assert tc.tool_name == "web_search"
        assert tc.success is False
        assert tc.result is None
        assert tc.approved is None


# ---------------------------------------------------------------------------
# Agent Core Tests
# ---------------------------------------------------------------------------


class TestAIAgent:
    """Tests for the AIAgent core."""

    def test_init_with_config(self, agent: AIAgent) -> None:
        """Agent should store configuration."""
        assert agent.config.max_iterations == 5
        assert agent.status == AgentStatus.IDLE

    def test_build_graph_raises_not_implemented(
        self, agent: AIAgent
    ) -> None:
        """build_graph should raise NotImplementedError until implemented."""
        with pytest.raises(NotImplementedError):
            agent.build_graph()

    def test_invoke_raises_not_implemented(self, agent: AIAgent) -> None:
        """invoke should raise NotImplementedError until implemented."""
        with pytest.raises(NotImplementedError):
            agent.invoke("test query")

    def test_plan_raises_not_implemented(self, agent: AIAgent) -> None:
        """plan should raise NotImplementedError until implemented."""
        state = create_initial_state("test")
        with pytest.raises(NotImplementedError):
            agent.plan(state)

    def test_handle_error_raises_not_implemented(
        self, agent: AIAgent
    ) -> None:
        """handle_error should raise NotImplementedError until implemented."""
        state = create_initial_state("test")
        with pytest.raises(NotImplementedError):
            agent.handle_error(state, RuntimeError("test error"))
