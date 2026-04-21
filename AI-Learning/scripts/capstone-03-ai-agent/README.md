# Capstone 3: Production AI Agent

## Overview

A production-grade AI agent built with LangGraph for state management, featuring
multiple tools, human-in-the-loop (HITL) approval workflows, persistent memory
(conversation and long-term), MCP integration for extensibility, robust error
recovery, and a FastAPI serving layer.

## Architecture

```
User Request
     |
  FastAPI API
     |
  AIAgent (LangGraph)
     |
  +--+--+--+--+--+
  |  |  |  |  |  |
  Tools:
  - Web Search
  - Calculator
  - Code Executor
  - MCP Tools (dynamic)
     |
  AgentMemory
  (short-term + long-term)
     |
  HITL Gate (if needed)
     |
  Response
```

## Components

| Module | Description |
|---|---|
| `src/agent.py` | Core agent with LangGraph orchestration |
| `src/tools.py` | Tool definitions (web search, calculator, code executor) |
| `src/memory.py` | Conversation memory and long-term knowledge store |
| `src/state.py` | LangGraph state schema and transition definitions |
| `src/api.py` | FastAPI endpoints for agent interaction |

## Features

- **LangGraph State Management**: Typed state graph with conditional edges, parallel tool execution, and cycle detection
- **Multiple Tools**: Web search (Tavily/SerpAPI), safe calculator, sandboxed code execution
- **Human-in-the-Loop**: Configurable approval gates for sensitive operations
- **Persistent Memory**: Short-term conversation buffer + long-term vector-based memory
- **MCP Integration**: Model Context Protocol for dynamic tool discovery and use
- **Error Recovery**: Graceful degradation, retry logic, and fallback strategies
- **FastAPI Serving**: REST API with WebSocket support for real-time interaction
- **Observability**: Structured logging, trace IDs, and execution timeline

## Usage

```bash
# Run the agent API
uvicorn src.api:app --host 0.0.0.0 --port 8000

# Docker
docker build -t ai-agent .
docker run -p 8000:8000 ai-agent

# Interactive query
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Search the web for the latest AI news and summarize it."}'
```

## Project Structure

```
capstone-03-ai-agent/
  README.md
  Dockerfile
  src/
    __init__.py
    agent.py
    tools.py
    memory.py
    state.py
    api.py
  tests/
    __init__.py
    test_agent.py
```

## Dependencies

- langgraph
- langchain / langchain-community
- openai
- fastapi / uvicorn
- tavily-python (or serpapi)
- chromadb (for long-term memory)
- pytest
