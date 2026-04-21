"""
Module 11: Tool Use & Function Calling — Exercises
====================================================

12 exercises on Claude tool_use, OpenAI functions, schemas, and MCP.

Run this file directly to check your solutions:
    python exercises.py
"""

import json


# ---------------------------------------------------------------------------
# Exercise 1: Simple Tool Definition
# ---------------------------------------------------------------------------
def create_tool_definition(
    name: str,
    description: str,
    parameters: dict,
) -> dict:
    """
    Create a Claude tool definition.

    Args:
        name: Tool name
        description: What the tool does
        parameters: JSON schema for parameters

    Returns:
        Tool definition dict
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: JSON Schema Property
# ---------------------------------------------------------------------------
def create_schema_property(
    name: str,
    prop_type: str,
    description: str,
    required: bool = False,
    enum_values: list = None,
) -> tuple[str, dict]:
    """
    Create a single JSON schema property.

    Args:
        name: Property name
        prop_type: 'string', 'number', 'boolean', 'array', 'object'
        description: Property description
        required: If required
        enum_values: If enum, list of allowed values

    Returns:
        Tuple of (property_name, property_schema_dict)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Parse Tool Use Response
# ---------------------------------------------------------------------------
def parse_tool_use_response(response_content: list) -> list[dict]:
    """
    Parse Claude tool_use blocks from response.

    Each block has: type, id, name, input

    Args:
        response_content: Response content list from API

    Returns:
        List of tool_use dicts with 'name', 'input', 'id'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Tool Result Message
# ---------------------------------------------------------------------------
def create_tool_result_message(
    tool_use_id: str,
    result: str,
    is_error: bool = False,
) -> dict:
    """
    Create a tool result message for Claude.

    Args:
        tool_use_id: ID from tool_use block
        result: Result string
        is_error: Whether this is an error result

    Returns:
        Message dict for conversation
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Function Definition for OpenAI
# ---------------------------------------------------------------------------
def create_openai_function_tool(
    name: str,
    description: str,
    parameters: dict,
) -> dict:
    """
    Create an OpenAI-style function tool definition.

    Format: {"type": "function", "function": {...}}

    Args:
        name: Function name
        description: Description
        parameters: JSON schema for parameters

    Returns:
        OpenAI function tool dict
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Parse OpenAI Tool Call
# ---------------------------------------------------------------------------
def parse_openai_tool_call(tool_call_object: dict) -> dict:
    """
    Parse an OpenAI tool_call object.

    Extract function name and parse JSON arguments.

    Args:
        tool_call_object: Tool call from OpenAI response

    Returns:
        Dict with 'function_name' and 'arguments'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Tool Execution Safety Check
# ---------------------------------------------------------------------------
def validate_tool_input(
    tool_name: str,
    tool_input: dict,
    schema: dict,
) -> tuple[bool, str]:
    """
    Validate tool input against schema.

    Check:
    - Required fields present
    - Types correct
    - Enum values valid

    Args:
        tool_name: Name of tool
        tool_input: Input dict to validate
        schema: JSON schema for validation

    Returns:
        Tuple of (is_valid, error_message)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Multi-Tool Response
# ---------------------------------------------------------------------------
def handle_multiple_tool_calls(
    tool_calls: list[dict],
    tool_registry: dict[str, callable],
) -> list[dict]:
    """
    Execute multiple tool calls and gather results.

    Args:
        tool_calls: List of tool calls from model
        tool_registry: Dict mapping tool name to function

    Returns:
        List of result dicts with 'tool_name', 'result', 'error'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Tool Retry Logic
# ---------------------------------------------------------------------------
def execute_tool_with_retry(
    tool_name: str,
    tool_input: dict,
    tool_registry: dict,
    max_retries: int = 2,
) -> dict:
    """
    Execute tool with retry on failure.

    Args:
        tool_name: Tool to execute
        tool_input: Parameters
        tool_registry: Available tools
        max_retries: Number of retries

    Returns:
        Dict with 'success', 'result', 'error'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Tool Rate Limiting
# ---------------------------------------------------------------------------
def check_rate_limit(
    tool_name: str,
    call_history: list[tuple],
    max_calls_per_minute: int = 10,
) -> bool:
    """
    Check if tool call exceeds rate limit.

    Args:
        tool_name: Tool being called
        call_history: List of (tool_name, timestamp) tuples
        max_calls_per_minute: Rate limit

    Returns:
        True if call is allowed, False if rate limited
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Tool Chaining Context
# ---------------------------------------------------------------------------
def build_tool_chain_context(
    first_tool_result: str,
    next_tool_name: str,
) -> dict:
    """
    Build context for next tool based on previous result.

    Args:
        first_tool_result: Result from previous tool
        next_tool_name: Name of next tool to call

    Returns:
        Context dict with 'previous_result', 'next_tool'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: MCP Tool Adapter
# ---------------------------------------------------------------------------
def create_mcp_tool_adapter(
    mcp_tool: dict,
) -> dict:
    """
    Convert MCP tool format to Claude/OpenAI format.

    MCP format: {"name": ..., "inputSchema": {...}}
    Claude format: {"name": ..., "input_schema": {...}}

    Args:
        mcp_tool: MCP tool definition

    Returns:
        Adapted tool for Claude API
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    tool = create_tool_definition('test', 'A test tool', {})
    assert 'name' in tool

    # Test Exercise 2
    name, schema = create_schema_property('q', 'string', 'Query')
    assert name == 'q'

    # Test Exercise 3
    response = [{'type': 'tool_use', 'id': '123', 'name': 'search', 'input': {'q': 'test'}}]
    parsed = parse_tool_use_response(response)
    assert len(parsed) > 0

    # Test Exercise 4
    msg = create_tool_result_message('123', 'result')
    assert 'tool_use_id' in msg

    # Test Exercise 5
    fn_tool = create_openai_function_tool('test', 'A test', {})
    assert fn_tool['type'] == 'function'

    # Test Exercise 6
    tool_call = {
        'function': {'name': 'search', 'arguments': '{"q": "test"}'}
    }
    parsed = parse_openai_tool_call(tool_call)
    assert 'function_name' in parsed

    # Test Exercise 7
    valid, msg = validate_tool_input('search', {}, {})
    assert isinstance(valid, bool)

    # Test Exercise 8
    calls = [{'name': 'test', 'input': {}}]
    results = handle_multiple_tool_calls(calls, {})
    assert isinstance(results, list)

    # Test Exercise 9
    result = execute_tool_with_retry('search', {}, {})
    assert 'success' in result

    # Test Exercise 10
    allowed = check_rate_limit('test', [])
    assert isinstance(allowed, bool)

    # Test Exercise 11
    context = build_tool_chain_context('result1', 'next_tool')
    assert 'previous_result' in context

    # Test Exercise 12
    mcp = {'name': 'test', 'inputSchema': {}}
    adapted = create_mcp_tool_adapter(mcp)
    assert 'name' in adapted

    print('All tests passed!')
