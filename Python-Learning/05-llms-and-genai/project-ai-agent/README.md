# Project: AI Agent with Tool Use

## Overview

Build a working AI agent that can use tools to solve complex tasks. This project integrates:
- Claude API with tool_use
- Tool definitions and schemas
- Multi-step reasoning (ReAct pattern)
- Error handling and retries

## Project Structure

```
project-ai-agent/
├── config.py           # Configuration (models, tools, API settings)
├── tools.py            # Tool implementations
├── agent.py            # Main agent logic (you'll build this)
├── test_agent.py       # Tests
├── README.md           # This file
└── requirements.txt    # Dependencies (implied)
```

## Quick Start

### 1. Set Up Environment

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Define Tools

Tools are already defined in `tools.py`. Examples:
- `calculator`: Evaluate math expressions
- `search`: Search for information (mock)
- `get_current_time`: Return current date/time

### 3. Implement Agent

The core agent loop (in `agent.py`):

```python
def run_agent(query: str, max_iterations: int = 5) -> str:
    """Run agent to process query using tools."""
    messages = [{"role": "user", "content": query}]

    for iteration in range(max_iterations):
        # Call Claude with tools
        response = client.messages.create(
            model=CONFIG['model'],
            max_tokens=1024,
            tools=CONFIG['tools'],
            messages=messages
        )

        # Check if model wants to use a tool
        has_tool_use = any(
            block.type == "tool_use"
            for block in response.content
        )

        if not has_tool_use:
            # Model generated final answer
            return extract_text_response(response.content)

        # Execute tools and add results
        messages.append({"role": "assistant", "content": response.content})
        tool_results = execute_tools(response.content)
        messages.append({"role": "user", "content": tool_results})

    return "Max iterations reached"
```

### 4. Run Tests

```bash
python -m pytest test_agent.py -v
```

## Example Usage

```python
from agent import run_agent

# Simple calculation
result = run_agent("What is 123 * 456 + 789?")
print(result)  # "56268"

# Multi-step task
result = run_agent("What's the current time and what's 100 + 50?")
print(result)  # "The current time is... and 100 + 50 = 150"
```

## Tools Available

### calculator(expression: str)
Evaluate a math expression.
```python
calculator("2 + 3 * 4")  # Returns: 14
```

### search(query: str)
Search for information (mock implementation).
```python
search("Python tutorials")  # Returns: mock results
```

### get_current_time()
Get current date and time.
```python
get_current_time()  # Returns: "2024-04-20 15:30:45"
```

## Key Concepts

### ReAct Pattern (Reason + Act)

1. **Think**: Model reasons about the task
2. **Act**: Model decides which tool to use
3. **Observe**: System provides tool result
4. **Repeat**: Until task is complete

### Error Handling

- Invalid tool inputs: Return error message to model
- Tool execution failures: Catch exceptions, return error
- Rate limiting: Check before each API call
- Timeout: Set max_iterations to prevent infinite loops

### Tool Calling Format

Claude returns tool_use blocks:

```python
{
    "type": "tool_use",
    "id": "tool_call_123",
    "name": "calculator",
    "input": {"expression": "100 + 50"}
}
```

Your agent extracts the tool name and input, executes it, then returns the result for the model to process.

## Extending the Agent

### Add a New Tool

1. Implement function in `tools.py`:
```python
def my_new_tool(param: str) -> str:
    """Tool description."""
    return "Result"
```

2. Add to tools in `config.py`:
```python
{
    "name": "my_new_tool",
    "description": "What it does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "..."}
        },
        "required": ["param"]
    }
}
```

### Change the Model

Edit `config.py`:
```python
CONFIG = {
    "model": "claude-3-opus-20240229",  # Change model
    ...
}
```

## Testing

Run tests:
```bash
python test_agent.py
```

Tests cover:
- Tool execution
- Multi-step reasoning
- Error handling
- Edge cases

## Interview Tips

If asked about this project:

1. **"How does the agent decide when to use a tool?"**
   - The LLM decides. If it generates a tool_use block, we execute.

2. **"How do you handle errors?"**
   - Catch exceptions, return error message to model, model can retry or explain.

3. **"Why use ReAct pattern?"**
   - Makes reasoning transparent, allows iteration, handles complex tasks.

4. **"What if the agent gets stuck in a loop?"**
   - Max iterations limit prevents infinite loops.

5. **"How would you scale this?"**
   - Parallel tool execution, caching, monitoring, vector DB for knowledge.

## Further Reading

- [Claude API Documentation](https://docs.anthropic.com)
- [ReAct: Synergizing Reasoning and Acting](https://arxiv.org/abs/2210.03629)
- [Tool Use Patterns](https://docs.anthropic.com/en/docs/build-a-chatbot-with-claude)
