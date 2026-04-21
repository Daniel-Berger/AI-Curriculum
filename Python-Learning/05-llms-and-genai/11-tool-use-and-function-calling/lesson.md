# Module 11: Tool Use & Function Calling

## Overview

Tool use (Claude) and function calling (OpenAI) allow models to request tool execution. Instead of generating text, the model says "I want to use this tool with these parameters."

```
User: "What's the weather in NYC?"

Model: {
  "type": "tool_use",
  "id": "tool_call_123",
  "name": "get_weather",
  "input": {"location": "New York City"}
}

System: Executes tool, returns result

Model: "The weather in NYC is 72°F and sunny."
```

---

## Claude Tool Use API

### Defining Tools

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
]
```

### API Call with Tools

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather in NYC?"}
    ]
)

# Response contains tool_use block
for block in response.content:
    if block.type == "tool_use":
        tool_name = block.name
        tool_input = block.input
```

### Tool Result Interaction

```python
# After executing tool
messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": "72°F, sunny"
        }
    ]
})

# Model continues with result
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=messages
)
```

---

## OpenAI Function Calling

### Defining Functions

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

### API Call

```python
response = client.chat.completions.create(
    model="gpt-4o",
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather in NYC?"}
    ]
)

# Check for tool call
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
```

---

## Common Patterns

### Multi-Turn Tool Use

```
1. User asks question
2. Model calls tool
3. System returns result
4. Model may call another tool
5. Model generates final answer
```

### Tool Chaining

```python
def execute_tool_chain(user_query, tools):
    messages = [{"role": "user", "content": user_query}]

    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            tools=tools,
            messages=messages
        )

        # Check if model wants to use a tool
        has_tool_use = any(block.type == "tool_use" for block in response.content)

        if not has_tool_use:
            # Final response
            return response.content[0].text

        # Execute tools
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        messages.append({"role": "user", "content": tool_results})
```

---

## JSON Schema for Tool Definitions

### Core Fields

```json
{
  "type": "object",
  "properties": {
    "param_name": {
      "type": "string|number|boolean|array|object",
      "description": "Human-readable parameter description",
      "enum": ["option1", "option2"],
      "default": "default_value"
    }
  },
  "required": ["param_name"]
}
```

### Type Validation

- **string**: Text
- **number**: Float or int
- **boolean**: True/false
- **array**: List of items
- **object**: Nested object

---

## MCP (Model Context Protocol)

MCP enables secure, standardized tool integration.

```python
# MCP servers implement tools
# Clients connect and call tools
# Example: Calendar server, Email server, etc.

client = MCPClient("sse", {
    "command": "python",
    "args": ["-m", "mcp_calendar_server"]
})

# List available tools
tools = client.get_tools()

# Call tool
result = client.use_tool("get_calendar_events", {
    "start_date": "2024-04-20",
    "end_date": "2024-04-27"
})
```

---

## Best Practices

1. **Descriptive naming**: Tool names should be clear (`get_current_weather` not `gw`)
2. **Clear descriptions**: Explain what tool does, when to use it
3. **Strict schemas**: Validate inputs with JSON schema
4. **Error handling**: Tell model what went wrong
5. **Timeout handling**: Long-running tools should timeout gracefully
6. **Rate limiting**: Monitor API calls to prevent abuse
7. **Logging**: Log all tool calls for debugging

---

## Summary

- **Claude**: Uses `tool_use` blocks with `tool_use_id`
- **OpenAI**: Uses `function` type with tool_calls
- **Schema**: Define input schema as JSON Schema
- **Multi-turn**: Model can call multiple tools before answering
- **Results**: Return tool results in messages for model to process
