"""
Module 10: LangGraph and Agents — Exercises
=============================================

12 exercises on StateGraph, conditional routing, agent patterns, and tool use.

Run this file directly to check your solutions:
    python exercises.py
"""


# ---------------------------------------------------------------------------
# Exercise 1: State Dictionary Definition
# ---------------------------------------------------------------------------
def define_agent_state() -> dict:
    """
    Define the state structure for an agent.

    Return a dict with keys representing different state fields:
    - 'messages': list of (role, content) tuples
    - 'current_task': str
    - 'iteration': int
    - 'tools_used': list[str]

    Returns:
        Example state dict with all fields initialized
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Graph Node as Function
# ---------------------------------------------------------------------------
def create_node_function(node_name: str) -> callable:
    """
    Create a simple node function for a state graph.

    The function should:
    - Accept a state dict
    - Process/modify the state
    - Return updated state

    For exercise: create a counter node that increments 'iteration'

    Args:
        node_name: Name of the node

    Returns:
        Callable that takes state dict and returns updated state
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Conditional Router
# ---------------------------------------------------------------------------
def create_router_function() -> callable:
    """
    Create a conditional routing function.

    Route based on current state:
    - If 'continue' in messages: return 'process_node'
    - If 'stop' in messages: return 'end_node'
    - Otherwise: return 'default_node'

    Returns:
        Callable that takes state dict and returns node name string
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Agent Action Parsing
# ---------------------------------------------------------------------------
def parse_agent_action(
    agent_output: str,
) -> dict:
    """
    Parse LLM agent output into action and input.

    Format: "Action: tool_name\nInput: {param1: value1, ...}"

    Args:
        agent_output: Raw LLM output

    Returns:
        Dict with 'action' and 'input' keys
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Tool Registry
# ---------------------------------------------------------------------------
def create_tool_registry(
    tools: list[dict],
) -> dict[str, callable]:
    """
    Create a registry mapping tool names to callable functions.

    Each tool dict has: 'name', 'description', 'function'

    Args:
        tools: List of tool definitions

    Returns:
        Dict mapping tool name to function
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Execute Agent Action
# ---------------------------------------------------------------------------
def execute_action(
    action: str,
    action_input: dict,
    tool_registry: dict,
) -> str:
    """
    Execute an agent action using available tools.

    Look up action in tool_registry and call with action_input.
    Handle errors gracefully.

    Args:
        action: Tool name
        action_input: Parameters for tool
        tool_registry: Available tools

    Returns:
        Result as string
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Message Formatting
# ---------------------------------------------------------------------------
def format_messages_for_llm(
    state: dict,
) -> list[dict]:
    """
    Format agent state messages for LLM API call.

    Convert from state format to API format:
    Each message should have 'role' and 'content'

    Args:
        state: Agent state dict with 'messages' key

    Returns:
        List of message dicts in API format
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Graph Execution Cycle
# ---------------------------------------------------------------------------
def execute_graph_cycle(
    state: dict,
    nodes: dict[str, callable],
    start_node: str,
    max_iterations: int = 10,
) -> dict:
    """
    Execute one full cycle through a state graph.

    Start at start_node, execute, follow routing to next node.
    Stop when reaching 'end_node' or max_iterations.

    Args:
        state: Initial state
        nodes: Dict of node_name -> node_function
        start_node: Name of starting node
        max_iterations: Max cycles to allow

    Returns:
        Final state after execution
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: ReAct Pattern (Reason + Act)
# ---------------------------------------------------------------------------
def apply_react_pattern(
    state: dict,
    llm_call: callable,
    tool_registry: dict,
) -> dict:
    """
    Execute one step of ReAct (Reasoning + Acting).

    1. LLM thinks about the task
    2. LLM decides on action
    3. Execute action
    4. Add observation to state

    Args:
        state: Current state
        llm_call: Function to call LLM
        tool_registry: Available tools

    Returns:
        Updated state with thought, action, and observation
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Branching Decision
# ---------------------------------------------------------------------------
def should_continue_loop(
    state: dict,
    max_iterations: int = 10,
) -> bool:
    """
    Determine if agent loop should continue.

    Continue if:
    - iteration < max_iterations
    - not 'done' in state
    - not error condition

    Args:
        state: Current state
        max_iterations: Max iterations allowed

    Returns:
        True if should continue, False to stop
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Tool Result Integration
# ---------------------------------------------------------------------------
def integrate_tool_result(
    state: dict,
    tool_name: str,
    tool_result: str,
) -> dict:
    """
    Integrate tool execution result back into state.

    Add to state:
    - tool_name to 'tools_used' list
    - result to 'messages' as observation

    Args:
        state: Current state
        tool_name: Name of tool executed
        tool_result: Result from tool

    Returns:
        Updated state
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Agent Configuration
# ---------------------------------------------------------------------------
def create_agent_config(
    model: str = 'claude-3-5-sonnet-20241022',
    tools: list[dict] = None,
    max_iterations: int = 10,
    temperature: float = 0.7,
) -> dict:
    """
    Create configuration for agent graph.

    Args:
        model: LLM model to use
        tools: List of available tools
        max_iterations: Max reasoning steps
        temperature: LLM temperature

    Returns:
        Config dict with all parameters
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    state = define_agent_state()
    assert 'messages' in state

    # Test Exercise 2
    node_fn = create_node_function('counter')
    assert callable(node_fn)
    updated = node_fn({'iteration': 0})
    assert updated['iteration'] == 1

    # Test Exercise 3
    router = create_router_function()
    assert callable(router)

    # Test Exercise 4
    action = parse_agent_action("Action: search\nInput: {q: test}")
    assert 'action' in action

    # Test Exercise 5
    tools = [{'name': 'search', 'description': 'Search', 'function': lambda x: 'result'}]
    registry = create_tool_registry(tools)
    assert 'search' in registry

    # Test Exercise 6
    result = execute_action('search', {'q': 'test'}, registry)
    assert isinstance(result, str)

    # Test Exercise 7
    state = {'messages': [('user', 'hello')]}
    formatted = format_messages_for_llm(state)
    assert isinstance(formatted, list)

    # Test Exercise 8
    nodes = {'start': lambda s: s, 'end': lambda s: s}
    final = execute_graph_cycle(state, nodes, 'start')
    assert isinstance(final, dict)

    # Test Exercise 9
    result = apply_react_pattern(state, lambda x: 'action', registry)
    assert isinstance(result, dict)

    # Test Exercise 10
    should_cont = should_continue_loop({'iteration': 5}, max_iterations=10)
    assert should_cont is True

    # Test Exercise 11
    updated = integrate_tool_result(state, 'search', 'found results')
    assert 'search' in updated.get('tools_used', [])

    # Test Exercise 12
    config = create_agent_config()
    assert 'model' in config

    print('All tests passed!')
