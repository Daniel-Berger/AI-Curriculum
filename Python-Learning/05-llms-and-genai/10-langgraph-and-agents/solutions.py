"""
Module 10: LangGraph and Agents — Solutions
=============================================

Complete solutions for all 12 exercises.
"""

import re
from typing import Optional


# Exercise 1
def define_agent_state() -> dict:
    return {
        'messages': [],
        'current_task': '',
        'iteration': 0,
        'tools_used': [],
    }


# Exercise 2
def create_node_function(node_name: str) -> callable:
    def node_fn(state: dict) -> dict:
        state['iteration'] = state.get('iteration', 0) + 1
        return state
    return node_fn


# Exercise 3
def create_router_function() -> callable:
    def router(state: dict) -> str:
        messages = state.get('messages', '')
        if isinstance(messages, list):
            messages = ' '.join(str(m) for m in messages)
        else:
            messages = str(messages)

        if 'continue' in messages.lower():
            return 'process_node'
        elif 'stop' in messages.lower():
            return 'end_node'
        else:
            return 'default_node'
    return router


# Exercise 4
def parse_agent_action(agent_output: str) -> dict:
    action_match = re.search(r'Action:\s*(\w+)', agent_output)
    input_match = re.search(r'Input:\s*({.*})', agent_output, re.DOTALL)

    action = action_match.group(1) if action_match else 'unknown'
    input_str = input_match.group(1) if input_match else '{}'

    try:
        import ast
        input_dict = ast.literal_eval(input_str)
    except:
        input_dict = {}

    return {'action': action, 'input': input_dict}


# Exercise 5
def create_tool_registry(tools: list[dict]) -> dict[str, callable]:
    registry = {}
    for tool in tools:
        registry[tool['name']] = tool['function']
    return registry


# Exercise 6
def execute_action(action: str, action_input: dict, tool_registry: dict) -> str:
    if action not in tool_registry:
        return f"Error: Unknown tool '{action}'"
    try:
        result = tool_registry[action](**action_input)
        return str(result)
    except Exception as e:
        return f"Error executing {action}: {str(e)}"


# Exercise 7
def format_messages_for_llm(state: dict) -> list[dict]:
    formatted = []
    messages = state.get('messages', [])
    for msg in messages:
        if isinstance(msg, tuple):
            role, content = msg
            formatted.append({'role': role, 'content': content})
        elif isinstance(msg, dict):
            formatted.append(msg)
    return formatted


# Exercise 8
def execute_graph_cycle(state: dict, nodes: dict[str, callable], start_node: str, max_iterations: int = 10) -> dict:
    current_node = start_node
    iterations = 0

    while iterations < max_iterations and current_node != 'end_node':
        if current_node in nodes:
            state = nodes[current_node](state)
        iterations += 1

    return state


# Exercise 9
def apply_react_pattern(state: dict, llm_call: callable, tool_registry: dict) -> dict:
    thought = llm_call(state)
    action_dict = parse_agent_action(thought)
    result = execute_action(action_dict['action'], action_dict['input'], tool_registry)

    state = integrate_tool_result(state, action_dict['action'], result)
    return state


# Exercise 10
def should_continue_loop(state: dict, max_iterations: int = 10) -> bool:
    iteration = state.get('iteration', 0)
    done = state.get('done', False)
    return iteration < max_iterations and not done


# Exercise 11
def integrate_tool_result(state: dict, tool_name: str, tool_result: str) -> dict:
    if 'tools_used' not in state:
        state['tools_used'] = []
    state['tools_used'].append(tool_name)

    if 'messages' not in state:
        state['messages'] = []

    if isinstance(state['messages'], list):
        state['messages'].append(('system', f'Tool {tool_name} result: {tool_result}'))

    return state


# Exercise 12
def create_agent_config(
    model: str = 'claude-3-5-sonnet-20241022',
    tools: list[dict] = None,
    max_iterations: int = 10,
    temperature: float = 0.7,
) -> dict:
    return {
        'model': model,
        'tools': tools or [],
        'max_iterations': max_iterations,
        'temperature': temperature,
    }


# Test Suite
if __name__ == '__main__':
    state = define_agent_state()
    assert 'messages' in state

    node_fn = create_node_function('test')
    updated = node_fn({'iteration': 0})
    assert updated['iteration'] == 1

    router = create_router_function()
    result = router({'messages': 'continue'})
    assert result == 'process_node'

    action = parse_agent_action("Action: search\nInput: {q: test}")
    assert action['action'] == 'search'

    tools = [{'name': 'search', 'description': 'Search', 'function': lambda **x: 'result'}]
    registry = create_tool_registry(tools)
    assert 'search' in registry

    result = execute_action('search', {'q': 'test'}, registry)
    assert isinstance(result, str)

    formatted = format_messages_for_llm({'messages': [('user', 'hello')]})
    assert len(formatted) > 0

    config = create_agent_config()
    assert config['model'] == 'claude-3-5-sonnet-20241022'

    print('All tests passed!')
