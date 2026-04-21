"""
Module 11: Tool Use & Function Calling — Solutions
====================================================

Complete solutions for all 12 exercises.
"""

import json
import time
from collections import defaultdict


# Exercise 1
def create_tool_definition(name: str, description: str, parameters: dict) -> dict:
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": parameters.get("properties", {}),
            "required": parameters.get("required", [])
        }
    }


# Exercise 2
def create_schema_property(
    name: str,
    prop_type: str,
    description: str,
    required: bool = False,
    enum_values: list = None,
) -> tuple[str, dict]:
    prop = {
        "type": prop_type,
        "description": description
    }
    if enum_values:
        prop["enum"] = enum_values
    return (name, prop)


# Exercise 3
def parse_tool_use_response(response_content: list) -> list[dict]:
    tools = []
    for block in response_content:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            tools.append({
                "name": block.get("name"),
                "input": block.get("input", {}),
                "id": block.get("id")
            })
    return tools


# Exercise 4
def create_tool_result_message(tool_use_id: str, result: str, is_error: bool = False) -> dict:
    return {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": result,
                "is_error": is_error
            }
        ]
    }


# Exercise 5
def create_openai_function_tool(name: str, description: str, parameters: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": parameters.get("properties", {}),
                "required": parameters.get("required", [])
            }
        }
    }


# Exercise 6
def parse_openai_tool_call(tool_call_object: dict) -> dict:
    function = tool_call_object.get("function", {})
    name = function.get("name")
    args_str = function.get("arguments", "{}")
    try:
        arguments = json.loads(args_str)
    except:
        arguments = {}
    return {
        "function_name": name,
        "arguments": arguments
    }


# Exercise 7
def validate_tool_input(tool_name: str, tool_input: dict, schema: dict) -> tuple[bool, str]:
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for req_field in required:
        if req_field not in tool_input:
            return (False, f"Missing required field: {req_field}")

    for key, value in tool_input.items():
        if key in properties:
            prop = properties[key]
            expected_type = prop.get("type")
            if expected_type == "string" and not isinstance(value, str):
                return (False, f"Field {key} must be string")
            if expected_type == "number" and not isinstance(value, (int, float)):
                return (False, f"Field {key} must be number")

    return (True, "")


# Exercise 8
def handle_multiple_tool_calls(tool_calls: list[dict], tool_registry: dict[str, callable]) -> list[dict]:
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.get("name")
        tool_input = tool_call.get("input", {})

        if tool_name in tool_registry:
            try:
                result = tool_registry[tool_name](**tool_input)
                results.append({
                    "tool_name": tool_name,
                    "result": str(result),
                    "error": None
                })
            except Exception as e:
                results.append({
                    "tool_name": tool_name,
                    "result": None,
                    "error": str(e)
                })
        else:
            results.append({
                "tool_name": tool_name,
                "result": None,
                "error": f"Tool not found: {tool_name}"
            })

    return results


# Exercise 9
def execute_tool_with_retry(tool_name: str, tool_input: dict, tool_registry: dict, max_retries: int = 2) -> dict:
    for attempt in range(max_retries):
        try:
            if tool_name in tool_registry:
                result = tool_registry[tool_name](**tool_input)
                return {
                    "success": True,
                    "result": str(result),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "result": None,
                    "error": f"Tool not found: {tool_name}"
                }
        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    "success": False,
                    "result": None,
                    "error": str(e)
                }
            time.sleep(1)

    return {"success": False, "result": None, "error": "Max retries exceeded"}


# Exercise 10
def check_rate_limit(tool_name: str, call_history: list[tuple], max_calls_per_minute: int = 10) -> bool:
    current_time = time.time()
    one_minute_ago = current_time - 60

    recent_calls = [call for call in call_history if call[1] > one_minute_ago and call[0] == tool_name]

    return len(recent_calls) < max_calls_per_minute


# Exercise 11
def build_tool_chain_context(first_tool_result: str, next_tool_name: str) -> dict:
    return {
        "previous_result": first_tool_result,
        "next_tool": next_tool_name
    }


# Exercise 12
def create_mcp_tool_adapter(mcp_tool: dict) -> dict:
    return {
        "name": mcp_tool.get("name"),
        "description": mcp_tool.get("description", ""),
        "input_schema": mcp_tool.get("inputSchema", {})
    }


# Test Suite
if __name__ == '__main__':
    tool = create_tool_definition("search", "Search", {})
    assert tool["name"] == "search"

    name, schema = create_schema_property("q", "string", "Query")
    assert name == "q"
    assert schema["type"] == "string"

    response = [{"type": "tool_use", "id": "123", "name": "search", "input": {"q": "test"}}]
    parsed = parse_tool_use_response(response)
    assert parsed[0]["name"] == "search"

    msg = create_tool_result_message("123", "result")
    assert msg["role"] == "user"

    fn_tool = create_openai_function_tool("search", "Search", {})
    assert fn_tool["type"] == "function"

    tool_call = {"function": {"name": "search", "arguments": '{"q": "test"}'}}
    parsed = parse_openai_tool_call(tool_call)
    assert parsed["function_name"] == "search"

    valid, msg = validate_tool_input("search", {"q": "test"}, {"required": ["q"]})
    assert valid is True

    mcp = {"name": "test", "inputSchema": {}}
    adapted = create_mcp_tool_adapter(mcp)
    assert adapted["name"] == "test"

    print('All tests passed!')
