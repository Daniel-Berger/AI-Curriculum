"""Tool implementations for the AI agent.

Provides a set of tools the agent can invoke to answer questions:
calculator, date/time, and mock web search. Uses a registry pattern
so tools are discoverable and callable by name.

Swift parallel:
    - Tool protocol      ~  protocol AgentTool { func execute(input:) -> String }
    - Tool registry       ~  [String: any AgentTool] dictionary
    - Safe math eval      ~  NSExpression(format:).expressionValue(with:)
    - DateFormatter       ~  DateFormatter / ISO8601DateFormatter

Usage:
    from tools import ToolRegistry

    registry = ToolRegistry()
    result = registry.execute("calculator", "2 + 3 * 4")
    print(result)  # "14"
"""

from __future__ import annotations

import ast
import logging
import math
import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ToolResult:
    """Result from a tool execution.

    Attributes:
        tool_name: Name of the tool that produced this result.
        input_text: The input that was passed to the tool.
        output: The tool's output as a string.
        success: Whether the execution succeeded.
        error: Error message if the execution failed.
    """

    tool_name: str
    input_text: str
    output: str
    success: bool = True
    error: str = ""

    def __str__(self) -> str:
        if self.success:
            return f"[{self.tool_name}] {self.output}"
        return f"[{self.tool_name}] ERROR: {self.error}"


@dataclass(frozen=True)
class ToolDefinition:
    """Schema definition for a tool, used to describe it to the LLM.

    This mirrors the function/tool calling format used by Claude and
    OpenAI APIs.

    Attributes:
        name: Unique tool identifier.
        description: Human-readable description for the LLM.
        parameters: JSON Schema describing the input parameters.
    """

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Base tool class
# ---------------------------------------------------------------------------

class BaseTool(ABC):
    """Abstract base class for agent tools.

    All tools implement this interface so the agent can discover
    and invoke them uniformly. This is the Python equivalent of
    a Swift protocol:

        protocol AgentTool {
            var name: String { get }
            var definition: ToolDefinition { get }
            func execute(input: String) throws -> String
        }
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for the tool."""
        ...

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Tool definition for LLM function calling."""
        ...

    @abstractmethod
    def execute(self, input_text: str) -> ToolResult:
        """Execute the tool with the given input.

        Args:
            input_text: The input string to process.

        Returns:
            A ToolResult with the output or error.
        """
        ...


# ---------------------------------------------------------------------------
# Calculator tool
# ---------------------------------------------------------------------------

class CalculatorTool(BaseTool):
    """Safely evaluates mathematical expressions.

    Uses Python's AST module to parse and evaluate math expressions
    without using eval() -- which would be a security risk. Only
    allows numeric literals, basic operators, and common math functions.

    Supported operations:
        - Arithmetic: +, -, *, /, //, %, **
        - Functions: sqrt, abs, round, sin, cos, tan, log, pi, e
        - Parentheses for grouping

    Examples:
        "2 + 3 * 4"       -> "14"
        "sqrt(144)"        -> "12.0"
        "round(3.14159, 2)" -> "3.14"
    """

    # Allowed binary operators.
    _OPERATORS: dict[type, Any] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    # Allowed function names mapped to implementations.
    _FUNCTIONS: dict[str, Any] = {
        "sqrt": math.sqrt,
        "abs": abs,
        "round": round,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "ceil": math.ceil,
        "floor": math.floor,
    }

    # Allowed constants.
    _CONSTANTS: dict[str, float] = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="calculator",
            description=(
                "Evaluates mathematical expressions. Supports basic arithmetic "
                "(+, -, *, /, **), functions (sqrt, sin, cos, log, round), "
                "and constants (pi, e). Input should be a math expression as a string."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate.",
                    }
                },
                "required": ["expression"],
            },
        )

    def execute(self, input_text: str) -> ToolResult:
        """Safely evaluate a mathematical expression."""
        expression = input_text.strip()
        if not expression:
            return ToolResult(
                tool_name=self.name,
                input_text=input_text,
                output="",
                success=False,
                error="Empty expression",
            )

        try:
            result = self._safe_eval(expression)
            output = str(result)
            # Clean up float formatting.
            if isinstance(result, float) and result == int(result):
                output = str(int(result))

            logger.info("Calculator: %s = %s", expression, output)
            return ToolResult(
                tool_name=self.name,
                input_text=input_text,
                output=output,
            )
        except (ValueError, TypeError, ZeroDivisionError, OverflowError) as e:
            return ToolResult(
                tool_name=self.name,
                input_text=input_text,
                output="",
                success=False,
                error=f"Math error: {e}",
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                input_text=input_text,
                output="",
                success=False,
                error=f"Invalid expression: {e}",
            )

    def _safe_eval(self, expression: str) -> float | int:
        """Parse and evaluate a math expression using AST.

        This is significantly safer than eval() because it only
        allows a whitelist of operations.
        """
        tree = ast.parse(expression, mode="eval")
        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.expr) -> float | int:
        """Recursively evaluate an AST node."""
        # Numeric literals: 42, 3.14
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        # Unary operators: -x
        if isinstance(node, ast.UnaryOp):
            op_func = self._OPERATORS.get(type(node.op))
            if op_func is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op_func(self._eval_node(node.operand))

        # Binary operators: x + y, x * y
        if isinstance(node, ast.BinOp):
            op_func = self._OPERATORS.get(type(node.op))
            if op_func is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return op_func(left, right)

        # Function calls: sqrt(x), round(x, 2)
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls are allowed")
            func_name = node.func.id
            if func_name not in self._FUNCTIONS:
                raise ValueError(f"Unknown function: {func_name}")
            args = [self._eval_node(arg) for arg in node.args]
            return self._FUNCTIONS[func_name](*args)

        # Named constants: pi, e
        if isinstance(node, ast.Name):
            if node.id in self._CONSTANTS:
                return self._CONSTANTS[node.id]
            raise ValueError(f"Unknown variable: {node.id}")

        raise ValueError(f"Unsupported expression type: {type(node).__name__}")


# ---------------------------------------------------------------------------
# DateTime tool
# ---------------------------------------------------------------------------

class DateTimeTool(BaseTool):
    """Provides current date and time information.

    Supports multiple output formats and timezone-aware results.

    Swift parallel: Similar to DateFormatter with format strings,
    or Date() / Calendar.current for components.
    """

    _FORMATS: dict[str, str] = {
        "iso": "%Y-%m-%dT%H:%M:%S%z",
        "date": "%Y-%m-%d",
        "time": "%H:%M:%S",
        "full": "%A, %B %d, %Y at %I:%M %p",
        "short": "%m/%d/%Y %H:%M",
        "timestamp": "",  # Uses .timestamp() instead.
    }

    @property
    def name(self) -> str:
        return "datetime"

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="datetime",
            description=(
                "Returns the current date and time. Accepts an optional format "
                "parameter: 'iso' (default), 'date', 'time', 'full', 'short', "
                "or 'timestamp'. Can also accept a custom strftime format string."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "Output format: iso, date, time, full, short, timestamp, or a custom strftime pattern.",
                        "default": "iso",
                    }
                },
                "required": [],
            },
        )

    def execute(self, input_text: str) -> ToolResult:
        """Return the current date/time in the requested format."""
        fmt = input_text.strip().lower() if input_text.strip() else "iso"
        now = datetime.now(timezone.utc)

        try:
            if fmt == "timestamp":
                output = str(int(now.timestamp()))
            elif fmt in self._FORMATS:
                output = now.strftime(self._FORMATS[fmt])
            else:
                # Treat as custom strftime format.
                output = now.strftime(fmt)

            return ToolResult(
                tool_name=self.name,
                input_text=input_text,
                output=output,
            )
        except ValueError as e:
            return ToolResult(
                tool_name=self.name,
                input_text=input_text,
                output="",
                success=False,
                error=f"Invalid format: {e}",
            )


# ---------------------------------------------------------------------------
# MockSearch tool
# ---------------------------------------------------------------------------

class MockSearchTool(BaseTool):
    """Mock web search tool that returns predefined results.

    In production, this would call a real search API (e.g., Brave,
    Google, Tavily). For learning and testing, it returns canned
    results based on keyword matching.

    The mock approach is standard practice in agent development --
    you build and test the agent logic with mocks, then swap in
    real APIs when ready.
    """

    # Predefined search results keyed by topic keywords.
    _MOCK_RESULTS: dict[str, list[dict[str, str]]] = {
        "python": [
            {
                "title": "Python (programming language) - Wikipedia",
                "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
                "snippet": "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.",
            },
            {
                "title": "Python.org",
                "url": "https://www.python.org",
                "snippet": "Python is a programming language that lets you work quickly and integrate systems more effectively.",
            },
        ],
        "machine learning": [
            {
                "title": "Machine learning - Wikipedia",
                "url": "https://en.wikipedia.org/wiki/Machine_learning",
                "snippet": "Machine learning is a subset of artificial intelligence that provides systems the ability to automatically learn and improve from experience.",
            },
        ],
        "transformer": [
            {
                "title": "Attention Is All You Need",
                "url": "https://arxiv.org/abs/1706.03762",
                "snippet": "The Transformer model architecture eschews recurrence and instead relies entirely on an attention mechanism to draw global dependencies between input and output.",
            },
        ],
        "rag": [
            {
                "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
                "url": "https://arxiv.org/abs/2005.11401",
                "snippet": "RAG models combine pre-trained parametric and non-parametric memory for language generation, accessing external knowledge during generation.",
            },
        ],
    }

    _DEFAULT_RESULT: list[dict[str, str]] = [
        {
            "title": "No specific results found",
            "url": "https://example.com",
            "snippet": "The search did not return specific results for this query. Try rephrasing your search terms.",
        },
    ]

    @property
    def name(self) -> str:
        return "search"

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search",
            description=(
                "Searches the web for information. Returns a list of relevant "
                "results with titles, URLs, and snippets. Input should be a "
                "search query string."
            ),
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
        )

    def execute(self, input_text: str) -> ToolResult:
        """Return mock search results based on keyword matching."""
        query = input_text.strip().lower()

        if not query:
            return ToolResult(
                tool_name=self.name,
                input_text=input_text,
                output="",
                success=False,
                error="Empty search query",
            )

        # Find the best matching topic.
        results = self._DEFAULT_RESULT
        for keyword, keyword_results in self._MOCK_RESULTS.items():
            if keyword in query:
                results = keyword_results
                break

        # Format results as a readable string.
        output_parts: list[str] = []
        for i, r in enumerate(results, start=1):
            output_parts.append(
                f"{i}. {r['title']}\n"
                f"   URL: {r['url']}\n"
                f"   {r['snippet']}"
            )

        output = "\n\n".join(output_parts)
        logger.info("MockSearch for '%s': %d results", query, len(results))

        return ToolResult(
            tool_name=self.name,
            input_text=input_text,
            output=output,
        )


# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Registry for discovering and executing tools by name.

    Implements the Registry pattern -- tools register themselves
    and the agent looks them up by name at runtime.

    Swift parallel: Similar to a dependency injection container
    or a [String: any AgentTool] dictionary with type-erased values.

    Usage:
        registry = ToolRegistry()
        # Tools are auto-registered by default.

        # Or register custom tools:
        registry.register(MyCustomTool())

        # Execute by name:
        result = registry.execute("calculator", "2 + 2")

        # List available tools:
        for defn in registry.definitions:
            print(defn.name, defn.description)
    """

    def __init__(self, auto_register: bool = True) -> None:
        self._tools: dict[str, BaseTool] = {}

        if auto_register:
            self.register(CalculatorTool())
            self.register(DateTimeTool())
            self.register(MockSearchTool())

    def register(self, tool: BaseTool) -> None:
        """Register a tool in the registry.

        Args:
            tool: The tool instance to register.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered. "
                f"Use a different name or unregister first."
            )
        self._tools[tool.name] = tool
        logger.info("Registered tool: %s", tool.name)

    def unregister(self, name: str) -> None:
        """Remove a tool from the registry.

        Args:
            name: The name of the tool to remove.

        Raises:
            KeyError: If the tool is not registered.
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        del self._tools[name]

    def execute(self, tool_name: str, input_text: str) -> ToolResult:
        """Execute a tool by name.

        Args:
            tool_name: The name of the tool to execute.
            input_text: The input to pass to the tool.

        Returns:
            A ToolResult with the output or error.
        """
        if tool_name not in self._tools:
            return ToolResult(
                tool_name=tool_name,
                input_text=input_text,
                output="",
                success=False,
                error=f"Tool '{tool_name}' not found. Available: {list(self._tools.keys())}",
            )

        tool = self._tools[tool_name]
        logger.info("Executing tool '%s' with input: %s", tool_name, input_text[:80])
        return tool.execute(input_text)

    def get_tool(self, name: str) -> BaseTool | None:
        """Get a tool by name, or None if not found."""
        return self._tools.get(name)

    @property
    def tool_names(self) -> list[str]:
        """List of registered tool names."""
        return list(self._tools.keys())

    @property
    def definitions(self) -> list[ToolDefinition]:
        """List of tool definitions for all registered tools."""
        return [tool.definition for tool in self._tools.values()]

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools
