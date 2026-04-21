# Module 10: LangGraph and Agents

## Introduction for Swift Developers

If LangChain chains are like Combine pipelines -- linear, data flows one direction --
then LangGraph is like a full state machine. Think of UIKit's
`UIViewController` lifecycle or a `GKStateMachine` from GameplayKit: you have defined
states, transitions between them, and conditions that determine which transition fires.

LangGraph lets you build LLM applications that loop, branch, wait for human input, and
maintain persistent state. This is essential for building agents -- AI systems that can
reason, plan, use tools, and iterate on their own work.

This module covers StateGraph construction, conditional routing, checkpointing for
persistence, human-in-the-loop patterns, and multi-agent architectures.

---

## 1. Why LangGraph?

### Limitations of Simple Chains

LangChain chains (Module 09) are powerful but inherently linear:

```
Input -> Step A -> Step B -> Step C -> Output
```

Real-world agents need:
- **Cycles**: Try something, check the result, try again if needed
- **Conditional branching**: Route to different logic based on LLM output
- **State persistence**: Remember what happened across multiple steps
- **Human oversight**: Pause for approval before taking actions
- **Error recovery**: Retry failed steps without restarting

### What LangGraph Adds

```
┌─────────────────────────────────────────────┐
│                  LangGraph                   │
│                                             │
│  ┌──────┐    ┌──────┐    ┌──────┐          │
│  │Node A├───>│Node B├───>│Node C│          │
│  └──────┘    └──┬───┘    └──────┘          │
│                 │   ▲                       │
│                 │   │  (cycle)              │
│                 ▼   │                       │
│              ┌──────┐                       │
│              │Node D├───────────────┐       │
│              └──────┘               │       │
│                                     ▼       │
│                              ┌──────────┐   │
│                              │   END     │   │
│                              └──────────┘   │
└─────────────────────────────────────────────┘
```

### Installation

```bash
pip install langgraph langchain-anthropic langchain-core
```

### Swift Analogy

| LangGraph Concept  | Swift Equivalent                              |
|--------------------|-----------------------------------------------|
| StateGraph         | GKStateMachine / custom state machine         |
| Node               | A state's action handler                      |
| Edge               | State transition                              |
| Conditional edge   | Switch statement on state                     |
| State (TypedDict)  | A struct that holds all context                |
| Checkpointer       | Core Data / UserDefaults persistence          |
| Interrupt          | Async/await suspension point                  |

---

## 2. State Definition

### Using TypedDict

State is the central data structure that flows through your graph. Every node reads
from and writes to this shared state.

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# Define state with TypedDict
class AgentState(TypedDict):
    # Messages use a special reducer that appends (not replaces)
    messages: Annotated[list[BaseMessage], add_messages]
    # Simple fields are replaced on each update
    current_step: str
    iteration_count: int
```

### Understanding Reducers

The `Annotated` type with `add_messages` is a **reducer** -- it defines how updates
to a field are merged with existing values:

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

class ChatState(TypedDict):
    # With add_messages reducer: new messages are APPENDED to existing list
    messages: Annotated[list, add_messages]
    # Without reducer: value is REPLACED
    summary: str

# If state has messages: [msg1, msg2]
# And a node returns {"messages": [msg3]}
# Result: messages = [msg1, msg2, msg3]  (appended, not replaced!)

# If state has summary: "Old summary"
# And a node returns {"summary": "New summary"}
# Result: summary = "New summary"  (replaced!)
```

### Using Pydantic for State

```python
from pydantic import BaseModel, Field
from typing import Annotated
from langgraph.graph.message import add_messages

class ResearchState(BaseModel):
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    query: str = ""
    sources: list[str] = Field(default_factory=list)
    draft: str = ""
    is_complete: bool = False
```

---

## 3. Building Your First Graph

### Simple Two-Node Graph

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

# Step 1: Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Step 2: Define node functions
# Each node takes the full state and returns a partial state update
def greet(state: State) -> dict:
    """First node: generate a greeting."""
    last_message = state["messages"][-1]
    return {
        "messages": [AIMessage(content=f"Hello! You said: {last_message.content}")]
    }

def farewell(state: State) -> dict:
    """Second node: say goodbye."""
    return {
        "messages": [AIMessage(content="Goodbye! Have a great day!")]
    }

# Step 3: Build the graph
graph = StateGraph(State)

# Add nodes
graph.add_node("greet", greet)
graph.add_node("farewell", farewell)

# Add edges (define the flow)
graph.add_edge(START, "greet")      # Start -> greet
graph.add_edge("greet", "farewell") # greet -> farewell
graph.add_edge("farewell", END)     # farewell -> End

# Step 4: Compile
app = graph.compile()

# Step 5: Run
result = app.invoke({
    "messages": [HumanMessage(content="Hi there!")]
})

for msg in result["messages"]:
    print(f"{msg.type}: {msg.content}")
# human: Hi there!
# ai: Hello! You said: Hi there!
# ai: Goodbye! Have a great day!
```

### Visualizing the Graph

```python
# Print the graph structure as ASCII
app.get_graph().print_ascii()

# Or get a Mermaid diagram
print(app.get_graph().draw_mermaid())
```

---

## 4. Conditional Edges

### Routing Based on State

Conditional edges are the key to building intelligent agents. They examine the
current state and decide which node to visit next.

```python
from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]
    sentiment: str

def analyze_sentiment(state: State) -> dict:
    """Analyze the sentiment of the last message."""
    text = state["messages"][-1].content.lower()
    if any(word in text for word in ["happy", "great", "love", "awesome"]):
        return {"sentiment": "positive"}
    elif any(word in text for word in ["sad", "bad", "hate", "terrible"]):
        return {"sentiment": "negative"}
    return {"sentiment": "neutral"}

def positive_response(state: State) -> dict:
    return {"messages": [AIMessage(content="That's wonderful to hear! 😊")]}

def negative_response(state: State) -> dict:
    return {"messages": [AIMessage(content="I'm sorry to hear that. How can I help?")]}

def neutral_response(state: State) -> dict:
    return {"messages": [AIMessage(content="I see. Tell me more about that.")]}

# Routing function -- returns the name of the next node
def route_by_sentiment(state: State) -> Literal["positive", "negative", "neutral"]:
    return state["sentiment"]

# Build graph
graph = StateGraph(State)
graph.add_node("analyze", analyze_sentiment)
graph.add_node("positive", positive_response)
graph.add_node("negative", negative_response)
graph.add_node("neutral", neutral_response)

graph.add_edge(START, "analyze")

# Conditional edge: after "analyze", route based on sentiment
graph.add_conditional_edges(
    "analyze",           # Source node
    route_by_sentiment,  # Routing function
    {                    # Mapping: return value -> target node
        "positive": "positive",
        "negative": "negative",
        "neutral": "neutral",
    }
)

# All response nodes lead to END
graph.add_edge("positive", END)
graph.add_edge("negative", END)
graph.add_edge("neutral", END)

app = graph.compile()
```

---

## 5. Building an Agent with Tool Use

### The ReAct Pattern

The most common agent pattern: **Reason** about the task, **Act** by calling a tool,
observe the result, and repeat until done.

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

# Define tools
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)  # In production, use a safe math parser
        return str(result)
    except Exception as e:
        return f"Error: {e}"

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Mock weather data
    weather_data = {
        "new york": "72°F, sunny",
        "london": "58°F, cloudy",
        "tokyo": "68°F, partly cloudy",
    }
    return weather_data.get(city.lower(), f"Weather data not available for {city}")

# Bind tools to model
tools = [calculator, get_weather]
model = ChatAnthropic(model="claude-sonnet-4-20250514").bind_tools(tools)

# Define state
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Node: call the LLM
def call_model(state: AgentState) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# Node: execute tool calls
def call_tools(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    tool_results = []

    # Create a lookup for our tools
    tool_map = {t.name: t for t in tools}

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        # Execute the tool
        result = tool_map[tool_name].invoke(tool_args)
        # Create a ToolMessage with the result
        tool_results.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )

    return {"messages": tool_results}

# Routing: should we call tools or are we done?
def should_continue(state: AgentState) -> Literal["tools", "end"]:
    last_message = state["messages"][-1]
    # If the LLM made tool calls, execute them
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # Otherwise, we're done
    return "end"

# Build the agent graph
graph = StateGraph(AgentState)

graph.add_node("agent", call_model)
graph.add_node("tools", call_tools)

graph.add_edge(START, "agent")

# After the agent node, conditionally go to tools or end
graph.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", "end": END}
)

# After tools, always go back to agent (the cycle!)
graph.add_edge("tools", "agent")

agent = graph.compile()

# Usage
result = agent.invoke({
    "messages": [HumanMessage(content="What's 25 * 4 + 10?")]
})
```

### Graph Visualization

```
         ┌──────────┐
         │  START    │
         └────┬─────┘
              │
              ▼
         ┌──────────┐
    ┌───>│  agent   │
    │    └────┬─────┘
    │         │
    │    has tool calls?
    │    ┌────┴─────┐
    │    │ yes  │ no │
    │    ▼      ▼    │
    │ ┌──────┐ ┌───┐ │
    │ │tools │ │END│ │
    │ └──┬───┘ └───┘ │
    │    │            │
    └────┘            │
```

---

## 6. Checkpointing (State Persistence)

### In-Memory Checkpointing

Checkpointing saves the graph state at each step, enabling:
- Resuming interrupted conversations
- Time-travel debugging
- Human-in-the-loop workflows

```python
from langgraph.checkpoint.memory import MemorySaver

# Create a checkpointer
memory = MemorySaver()

# Compile with checkpointer
agent = graph.compile(checkpointer=memory)

# Each invocation needs a thread_id for state tracking
config = {"configurable": {"thread_id": "conversation_1"}}

# First message
result = agent.invoke(
    {"messages": [HumanMessage(content="What's the weather in Tokyo?")]},
    config=config,
)

# Second message -- agent remembers the conversation
result = agent.invoke(
    {"messages": [HumanMessage(content="And in London?")]},
    config=config,
)

# Use a different thread_id for a separate conversation
config2 = {"configurable": {"thread_id": "conversation_2"}}
result = agent.invoke(
    {"messages": [HumanMessage(content="Hi, I'm new here")]},
    config=config2,
)
```

### SQLite Checkpointing (Persistent)

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Persistent checkpointer -- survives process restarts
with SqliteSaver.from_conn_string("checkpoints.db") as memory:
    agent = graph.compile(checkpointer=memory)

    config = {"configurable": {"thread_id": "persistent_chat"}}
    result = agent.invoke(
        {"messages": [HumanMessage(content="Remember: my favorite color is blue")]},
        config=config,
    )
```

### Inspecting State History

```python
# Get the current state
state = agent.get_state(config)
print(state.values)   # Current state values
print(state.next)     # Next node(s) to execute

# Get state history (time travel)
for state in agent.get_state_history(config):
    print(f"Step: {state.metadata.get('step', '?')}")
    print(f"Next: {state.next}")
    print(f"Messages: {len(state.values.get('messages', []))}")
    print("---")
```

---

## 7. Human-in-the-Loop

### Interrupt Before / After

You can pause graph execution before or after specific nodes, giving a human the
chance to review, modify, or approve the action.

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]
    approved: bool

def draft_email(state: State) -> dict:
    """Draft an email based on the request."""
    request = state["messages"][-1].content
    draft = f"Dear Team,\n\nRe: {request}\n\nBest regards"
    return {"messages": [AIMessage(content=f"Draft email:\n{draft}")]}

def send_email(state: State) -> dict:
    """Send the email (simulated)."""
    return {"messages": [AIMessage(content="Email sent successfully!")]}

graph = StateGraph(State)
graph.add_node("draft", draft_email)
graph.add_node("send", send_email)

graph.add_edge(START, "draft")
graph.add_edge("draft", "send")
graph.add_edge("send", END)

memory = MemorySaver()

# Compile with interrupt BEFORE the "send" node
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["send"]  # Pause before sending
)

config = {"configurable": {"thread_id": "email_1"}}

# First invocation -- runs "draft" then pauses before "send"
result = app.invoke(
    {"messages": [HumanMessage(content="Schedule meeting for Monday")]},
    config=config,
)
print(result["messages"][-1].content)  # Shows the draft

# Human reviews the draft...
# If approved, resume execution:
result = app.invoke(None, config=config)  # None = continue where we left off
print(result["messages"][-1].content)  # "Email sent successfully!"
```

### Modifying State Before Resuming

```python
# Get current state
state = app.get_state(config)

# Modify the state (e.g., edit the draft)
app.update_state(
    config,
    {"messages": [AIMessage(content="Updated draft: ...")]}
)

# Resume with modified state
result = app.invoke(None, config=config)
```

---

## 8. Streaming

### Stream Graph Events

```python
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

# Stream individual events as the graph executes
config = {"configurable": {"thread_id": "stream_1"}}

for event in agent.stream(
    {"messages": [HumanMessage(content="What's the weather?")]},
    config=config,
):
    # Each event is a dict with the node name as key
    for node_name, node_output in event.items():
        print(f"--- Node: {node_name} ---")
        if "messages" in node_output:
            for msg in node_output["messages"]:
                print(f"  {msg.type}: {msg.content[:100]}")
```

### Stream LLM Tokens

```python
# Stream individual tokens from the LLM within the graph
async for event in agent.astream_events(
    {"messages": [HumanMessage(content="Write a poem")]},
    config=config,
    version="v2",
):
    if event["event"] == "on_chat_model_stream":
        chunk = event["data"]["chunk"]
        print(chunk.content, end="", flush=True)
```

---

## 9. Error Handling and Retries

### Retry Logic in Nodes

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
import time

class State(TypedDict):
    messages: Annotated[list, add_messages]
    retry_count: int
    max_retries: int

def risky_operation(state: State) -> dict:
    """A node that might fail and needs retry logic."""
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)

    try:
        # Simulate an operation that might fail
        result = perform_api_call()
        return {
            "messages": [AIMessage(content=f"Success: {result}")],
            "retry_count": 0,
        }
    except Exception as e:
        if retry_count < max_retries:
            time.sleep(2 ** retry_count)  # Exponential backoff
            return {
                "messages": [AIMessage(content=f"Retry {retry_count + 1}: {e}")],
                "retry_count": retry_count + 1,
            }
        else:
            return {
                "messages": [AIMessage(content=f"Failed after {max_retries} retries: {e}")],
                "retry_count": retry_count,
            }

def should_retry(state: State) -> str:
    """Check if we should retry or give up."""
    if state["retry_count"] > 0 and state["retry_count"] <= state["max_retries"]:
        return "retry"
    return "done"
```

### Error Boundaries with Try/Except Nodes

```python
def safe_node(state: State) -> dict:
    """Wrap node logic in error handling."""
    try:
        # Main logic
        result = process_data(state)
        return {"messages": [AIMessage(content=result)], "error": None}
    except ValueError as e:
        return {"messages": [AIMessage(content=f"Validation error: {e}")], "error": str(e)}
    except Exception as e:
        return {"messages": [AIMessage(content=f"Unexpected error: {e}")], "error": str(e)}
```

---

## 10. Subgraphs

### Composing Graphs

Subgraphs let you build modular, reusable graph components -- similar to how you
compose SwiftUI views from smaller subviews.

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage

# --- Subgraph: Research ---
class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    findings: str

def search(state: ResearchState) -> dict:
    return {"findings": f"Found info about: {state['query']}"}

def summarize_findings(state: ResearchState) -> dict:
    return {
        "messages": [AIMessage(content=f"Summary: {state['findings']}")],
    }

research_graph = StateGraph(ResearchState)
research_graph.add_node("search", search)
research_graph.add_node("summarize", summarize_findings)
research_graph.add_edge(START, "search")
research_graph.add_edge("search", "summarize")
research_graph.add_edge("summarize", END)

research_subgraph = research_graph.compile()

# --- Main Graph ---
class MainState(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    findings: str

def route_request(state: MainState) -> dict:
    return {"query": state["messages"][-1].content}

main_graph = StateGraph(MainState)
main_graph.add_node("route", route_request)
main_graph.add_node("research", research_subgraph)  # Use subgraph as a node!

main_graph.add_edge(START, "route")
main_graph.add_edge("route", "research")
main_graph.add_edge("research", END)

app = main_graph.compile()
```

---

## 11. Multi-Agent Patterns

### Supervisor Pattern

One agent (supervisor) delegates tasks to specialized worker agents.

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic

class MultiAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str

model = ChatAnthropic(model="claude-sonnet-4-20250514")

def supervisor(state: MultiAgentState) -> dict:
    """Supervisor decides which worker to delegate to."""
    last_message = state["messages"][-1].content.lower()

    # Simple routing logic (in practice, use LLM for this)
    if "code" in last_message or "bug" in last_message:
        return {"next_agent": "coder"}
    elif "write" in last_message or "draft" in last_message:
        return {"next_agent": "writer"}
    else:
        return {"next_agent": "researcher"}

def coder_agent(state: MultiAgentState) -> dict:
    """Specialized coding agent."""
    response = model.invoke([
        {"role": "system", "content": "You are an expert programmer."},
        *state["messages"]
    ])
    return {"messages": [response]}

def writer_agent(state: MultiAgentState) -> dict:
    """Specialized writing agent."""
    response = model.invoke([
        {"role": "system", "content": "You are an expert writer."},
        *state["messages"]
    ])
    return {"messages": [response]}

def researcher_agent(state: MultiAgentState) -> dict:
    """Specialized research agent."""
    response = model.invoke([
        {"role": "system", "content": "You are an expert researcher."},
        *state["messages"]
    ])
    return {"messages": [response]}

def route_to_agent(state: MultiAgentState) -> str:
    return state["next_agent"]

# Build multi-agent graph
graph = StateGraph(MultiAgentState)

graph.add_node("supervisor", supervisor)
graph.add_node("coder", coder_agent)
graph.add_node("writer", writer_agent)
graph.add_node("researcher", researcher_agent)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges(
    "supervisor",
    route_to_agent,
    {
        "coder": "coder",
        "writer": "writer",
        "researcher": "researcher",
    }
)

# All workers return to END
graph.add_edge("coder", END)
graph.add_edge("writer", END)
graph.add_edge("researcher", END)

multi_agent = graph.compile()
```

### Swarm Pattern

Agents can hand off to each other dynamically, without a central supervisor.

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage

class SwarmState(TypedDict):
    messages: Annotated[list, add_messages]
    current_agent: str
    task_complete: bool

def agent_a(state: SwarmState) -> dict:
    """Agent A handles initial analysis, may hand off to Agent B."""
    # Do some work...
    if needs_specialist_help(state):
        return {
            "messages": [AIMessage(content="Handing off to specialist...")],
            "current_agent": "agent_b",
        }
    return {
        "messages": [AIMessage(content="Task complete!")],
        "task_complete": True,
    }

def agent_b(state: SwarmState) -> dict:
    """Agent B is a specialist, may hand back to Agent A."""
    # Do specialized work...
    return {
        "messages": [AIMessage(content="Specialist work done.")],
        "current_agent": "agent_a",
        "task_complete": True,
    }

def route_swarm(state: SwarmState) -> str:
    if state.get("task_complete"):
        return "end"
    return state.get("current_agent", "agent_a")
```

---

## 12. Practical Agent Architecture: Research Assistant

### Complete Working Example

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    research_topic: str
    sources: list[str]
    draft: str
    revision_count: int
    max_revisions: int
    is_approved: bool

model = ChatAnthropic(model="claude-sonnet-4-20250514")

def plan_research(state: ResearchState) -> dict:
    """Plan the research approach."""
    topic = state["messages"][-1].content
    response = model.invoke([
        SystemMessage(content="You are a research planner. Outline 3 key areas to research."),
        HumanMessage(content=f"Plan research on: {topic}")
    ])
    return {
        "messages": [response],
        "research_topic": topic,
    }

def gather_sources(state: ResearchState) -> dict:
    """Simulate gathering research sources."""
    topic = state["research_topic"]
    # In a real app, this would search the web, databases, etc.
    sources = [
        f"Source 1: Academic paper on {topic}",
        f"Source 2: Industry report on {topic}",
        f"Source 3: Expert blog post on {topic}",
    ]
    return {
        "messages": [AIMessage(content=f"Found {len(sources)} sources")],
        "sources": sources,
    }

def write_draft(state: ResearchState) -> dict:
    """Write or revise the research draft."""
    sources_text = "\n".join(state["sources"])
    revision = state.get("revision_count", 0)

    if revision == 0:
        prompt = f"Write a research summary on '{state['research_topic']}' using these sources:\n{sources_text}"
    else:
        prompt = f"Revise this draft (revision {revision}):\n{state['draft']}\n\nImprove clarity and depth."

    response = model.invoke([
        SystemMessage(content="You are a research writer. Write clear, well-structured summaries."),
        HumanMessage(content=prompt)
    ])

    return {
        "messages": [response],
        "draft": response.content,
        "revision_count": revision + 1,
    }

def evaluate_draft(state: ResearchState) -> dict:
    """Evaluate the quality of the draft."""
    response = model.invoke([
        SystemMessage(content="You are a writing critic. Evaluate this draft. "
                      "Respond with APPROVED if it's good enough, or NEEDS_REVISION with feedback."),
        HumanMessage(content=state["draft"])
    ])
    is_approved = "APPROVED" in response.content.upper()
    return {
        "messages": [response],
        "is_approved": is_approved,
    }

def should_revise(state: ResearchState) -> Literal["revise", "finalize"]:
    """Decide whether to revise or finalize."""
    if state.get("is_approved") or state.get("revision_count", 0) >= state.get("max_revisions", 3):
        return "finalize"
    return "revise"

def finalize(state: ResearchState) -> dict:
    """Finalize the research output."""
    return {
        "messages": [AIMessage(
            content=f"Research complete! Final draft ({state['revision_count']} revisions):\n\n{state['draft']}"
        )]
    }

# Build the graph
graph = StateGraph(ResearchState)

graph.add_node("plan", plan_research)
graph.add_node("gather", gather_sources)
graph.add_node("write", write_draft)
graph.add_node("evaluate", evaluate_draft)
graph.add_node("finalize", finalize)

graph.add_edge(START, "plan")
graph.add_edge("plan", "gather")
graph.add_edge("gather", "write")
graph.add_edge("write", "evaluate")

# Conditional: revise or finalize
graph.add_conditional_edges(
    "evaluate",
    should_revise,
    {"revise": "write", "finalize": "finalize"}
)

graph.add_edge("finalize", END)

# Compile with memory
memory = MemorySaver()
research_agent = graph.compile(checkpointer=memory)

# Usage
config = {"configurable": {"thread_id": "research_1"}}
result = research_agent.invoke(
    {
        "messages": [HumanMessage(content="The impact of LLMs on software development")],
        "revision_count": 0,
        "max_revisions": 2,
        "sources": [],
        "draft": "",
        "research_topic": "",
        "is_approved": False,
    },
    config=config,
)
```

---

## 13. Best Practices

### Graph Design Principles

1. **Keep nodes focused** -- each node should do one thing well
2. **Use typed state** -- TypedDict or Pydantic catches errors early
3. **Plan your edges** -- sketch the graph on paper before coding
4. **Use conditional edges sparingly** -- too many branches become hard to debug
5. **Always add checkpointing** -- even for development, it helps with debugging
6. **Test nodes independently** -- invoke each node function directly before assembling

### Common Pitfalls

```python
# BAD: Node that does too much
def do_everything(state):
    # Searches, writes, evaluates, and sends email in one node
    pass

# GOOD: Separate concerns into focused nodes
def search(state): ...
def write(state): ...
def evaluate(state): ...
def send(state): ...
```

### Debugging Tips

```python
# 1. Print state at each step
def debug_node(state: State) -> dict:
    print(f"Current state: {state}")
    return {}  # Pass-through

# 2. Use graph visualization
app.get_graph().print_ascii()

# 3. Stream events to see execution flow
for event in app.stream(input_data, config):
    print(event)

# 4. Inspect checkpoint history
for state in app.get_state_history(config):
    print(state)
```

---

## 14. Key Takeaways

| Concept           | What It Does                                      |
|--------------------|-------------------------------------------------|
| StateGraph         | Defines the graph structure (nodes + edges)      |
| TypedDict State    | Shared data that flows through all nodes         |
| add_messages       | Reducer that appends messages instead of replacing|
| Conditional edges  | Route to different nodes based on state          |
| Checkpointer       | Persists state for resumption and debugging      |
| interrupt_before   | Pauses execution for human review                |
| Subgraph           | Reusable graph component, composed like a node   |
| Supervisor pattern | Central agent delegates to specialized workers   |
| Swarm pattern      | Agents hand off to each other dynamically        |

---

## Next Module

In Module 11, we will explore **Tool Use and Function Calling** -- the mechanics of how
LLMs invoke external tools, including Claude's tool_use API, OpenAI function calling,
and the Model Context Protocol (MCP) for standardized tool integration.
