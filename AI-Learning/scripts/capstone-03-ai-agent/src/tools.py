"""
Tool Definitions Module
=======================

Defines the tools available to the AI agent. Each tool is a callable with
a clear schema (name, description, input parameters, output type) that the
agent can invoke during execution.

Built-in tools:
- **Web Search**: Search the web via Tavily or SerpAPI
- **Calculator**: Safe mathematical expression evaluation
- **Code Executor**: Sandboxed Python code execution

The ToolRegistry manages tool discovery, registration, and invocation,
including support for MCP (Model Context Protocol) dynamic tools.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type


@dataclass
class ToolSchema:
    """Schema definition for a tool.

    Attributes
    ----------
    name : str
        Unique tool identifier.
    description : str
        Human-readable description of what the tool does.
    parameters : dict
        JSON Schema describing the tool's input parameters.
    returns : str
        Description of the tool's return value.
    requires_approval : bool
        Whether this tool requires HITL approval.
    """

    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    returns: str = "str"
    requires_approval: bool = False


@dataclass
class ToolResult:
    """Result from a tool execution.

    Attributes
    ----------
    tool_name : str
        Name of the tool that produced this result.
    output : Any
        The tool's output.
    success : bool
        Whether the tool executed successfully.
    error : str or None
        Error message if execution failed.
    execution_time_ms : float
        Time taken to execute the tool.
    """

    tool_name: str
    output: Any = None
    success: bool = True
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class BaseTool(ABC):
    """Abstract base class for agent tools."""

    @property
    @abstractmethod
    def schema(self) -> ToolSchema:
        """Return the tool's schema definition."""
        ...

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with the given parameters.

        Parameters
        ----------
        **kwargs
            Tool-specific input parameters.

        Returns
        -------
        ToolResult
            The execution result.
        """
        ...


class WebSearchTool(BaseTool):
    """Search the web using Tavily or SerpAPI.

    Parameters
    ----------
    api_key : str, optional
        API key for the search provider.
    provider : str
        Search provider ('tavily' or 'serpapi').
    max_results : int
        Maximum number of search results to return.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = "tavily",
        max_results: int = 5,
    ) -> None:
        self.api_key = api_key
        self.provider = provider
        self.max_results = max_results

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="web_search",
            description="Search the web for current information on a topic.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query.",
                    }
                },
                "required": ["query"],
            },
            returns="List of search results with titles, URLs, and snippets.",
            requires_approval=False,
        )

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute a web search.

        Parameters
        ----------
        query : str
            The search query.

        Returns
        -------
        ToolResult
            Search results.
        """
        raise NotImplementedError


class CalculatorTool(BaseTool):
    """Safely evaluate mathematical expressions.

    Uses a restricted evaluator (no builtins, no imports) to prevent
    code injection while supporting standard math operations.
    """

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="calculator",
            description="Evaluate a mathematical expression safely.",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4').",
                    }
                },
                "required": ["expression"],
            },
            returns="The numerical result of the expression.",
            requires_approval=False,
        )

    def execute(self, **kwargs: Any) -> ToolResult:
        """Evaluate a mathematical expression.

        Parameters
        ----------
        expression : str
            The math expression to evaluate.

        Returns
        -------
        ToolResult
            Evaluation result.
        """
        raise NotImplementedError


class CodeExecutorTool(BaseTool):
    """Execute Python code in a sandboxed environment.

    Runs code in a restricted subprocess with timeouts, memory limits,
    and no network access. Requires human approval by default.

    Parameters
    ----------
    timeout_seconds : int
        Maximum execution time before killing the process.
    max_memory_mb : int
        Maximum memory allocation.
    """

    def __init__(
        self, timeout_seconds: int = 30, max_memory_mb: int = 256
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="code_executor",
            description="Execute Python code in a sandboxed environment.",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute.",
                    }
                },
                "required": ["code"],
            },
            returns="stdout output and return value from code execution.",
            requires_approval=True,
        )

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute Python code in a sandbox.

        Parameters
        ----------
        code : str
            Python code to execute.

        Returns
        -------
        ToolResult
            Execution output including stdout and return value.
        """
        raise NotImplementedError


class ToolRegistry:
    """Registry for managing available tools.

    Supports static tool registration and dynamic MCP tool discovery.

    Examples
    --------
    >>> registry = ToolRegistry()
    >>> registry.register(WebSearchTool())
    >>> result = registry.execute("web_search", query="AI news")
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool in the registry.

        Parameters
        ----------
        tool : BaseTool
            Tool instance to register.
        """
        self._tools[tool.schema.name] = tool

    def register_defaults(self) -> None:
        """Register all built-in tools."""
        self.register(WebSearchTool())
        self.register(CalculatorTool())
        self.register(CodeExecutorTool())

    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name.

        Parameters
        ----------
        name : str
            Tool name.

        Returns
        -------
        BaseTool
            The requested tool.

        Raises
        ------
        KeyError
            If the tool is not registered.
        """
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    def execute(self, tool_name: str, **kwargs: Any) -> ToolResult:
        """Execute a registered tool by name.

        Parameters
        ----------
        tool_name : str
            Name of the tool to execute.
        **kwargs
            Tool input parameters.

        Returns
        -------
        ToolResult
            Tool execution result.
        """
        tool = self.get_tool(tool_name)
        return tool.execute(**kwargs)

    def list_tools(self) -> List[ToolSchema]:
        """List all registered tool schemas.

        Returns
        -------
        list of ToolSchema
            Schemas for all registered tools.
        """
        return [tool.schema for tool in self._tools.values()]

    def discover_mcp_tools(self, mcp_server_url: str) -> int:
        """Discover and register tools from an MCP server.

        Parameters
        ----------
        mcp_server_url : str
            URL of the MCP server to connect to.

        Returns
        -------
        int
            Number of new tools discovered and registered.
        """
        raise NotImplementedError
