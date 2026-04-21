"""
Module 03: API Mastery — Solutions
===================================

Complete solutions for all 12 exercises on API integration.
"""

from typing import Optional, Protocol, Any
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Exercise 1: Parse API Response Structure
# ---------------------------------------------------------------------------
def parse_api_response(response: dict) -> str:
    """
    Extract the assistant's text response from API response.
    """
    # Try Claude format first
    if 'content' in response and isinstance(response['content'], list):
        if len(response['content']) > 0:
            if isinstance(response['content'][0], dict):
                if 'text' in response['content'][0]:
                    return response['content'][0]['text']

    # Try OpenAI format
    if 'choices' in response and isinstance(response['choices'], list):
        if len(response['choices']) > 0:
            choice = response['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                return choice['message']['content']

    return ""


# ---------------------------------------------------------------------------
# Exercise 2: Build Messages Array
# ---------------------------------------------------------------------------
def build_messages(
    user_input: str,
    conversation_history: list[dict],
) -> list[dict]:
    """
    Build a messages array from conversation history and current input.
    """
    messages = conversation_history.copy()
    messages.append({
        "role": "user",
        "content": user_input
    })
    return messages


# ---------------------------------------------------------------------------
# Exercise 3: Extract Token Usage
# ---------------------------------------------------------------------------
def extract_token_usage(response: dict) -> dict[str, int]:
    """
    Extract input and output token counts from API response.
    """
    usage = response.get('usage', {})
    return {
        'input_tokens': usage.get('input_tokens', 0),
        'output_tokens': usage.get('output_tokens', 0),
    }


# ---------------------------------------------------------------------------
# Exercise 4: Estimate Token Count
# ---------------------------------------------------------------------------
def estimate_tokens(text: str) -> int:
    """
    Estimate token count using the rule: 1 token ≈ 4 characters.
    """
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Exercise 5: Calculate API Cost
# ---------------------------------------------------------------------------
def calculate_api_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Calculate API call cost based on model and token counts.
    """
    pricing = {
        'claude-3-5-sonnet': {'input': 3, 'output': 15},
        'claude-3-opus': {'input': 15, 'output': 75},
        'gpt-4o': {'input': 5, 'output': 15},
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
    }

    if model not in pricing:
        return 0.0

    rates = pricing[model]
    input_cost = (input_tokens / 1_000_000) * rates['input']
    output_cost = (output_tokens / 1_000_000) * rates['output']

    return input_cost + output_cost


# ---------------------------------------------------------------------------
# Exercise 6: Classify Error Type
# ---------------------------------------------------------------------------
def classify_api_error(error_code: int) -> str:
    """
    Classify API error by HTTP status code.
    """
    if error_code in (401, 403):
        return 'authentication'
    elif error_code in (400, 422):
        return 'validation'
    elif error_code == 429:
        return 'rate_limit'
    elif error_code in (500, 503):
        return 'server'
    elif error_code == 504:
        return 'timeout'
    else:
        return 'unknown'


# ---------------------------------------------------------------------------
# Exercise 7: Retry Decision
# ---------------------------------------------------------------------------
def should_retry(
    error_type: str,
    attempt_count: int,
    max_retries: int = 3,
) -> bool:
    """
    Decide whether to retry based on error type and attempt count.
    """
    # Never retry authentication or validation errors
    if error_type in ('authentication', 'validation'):
        return False

    # Check if we've exceeded max retries
    if attempt_count >= max_retries:
        return False

    # Retry other error types
    if error_type in ('rate_limit', 'server', 'timeout'):
        return True

    return False


# ---------------------------------------------------------------------------
# Exercise 8: Calculate Backoff Delay
# ---------------------------------------------------------------------------
def calculate_backoff_delay(
    attempt_count: int,
    base_delay: float = 1.0,
) -> float:
    """
    Calculate exponential backoff delay: delay = base_delay * (2 ^ (attempt - 1))
    """
    return base_delay * (2 ** (attempt_count - 1))


# ---------------------------------------------------------------------------
# Exercise 9: Convert Streaming Response
# ---------------------------------------------------------------------------
def process_stream_events(events: list[dict]) -> str:
    """
    Reconstruct complete response from streaming events.
    """
    text_parts = []

    for event in events:
        event_type = event.get('type')

        if event_type == 'content_block_delta':
            delta = event.get('delta', {})
            if delta.get('type') == 'text_delta':
                text = delta.get('text', '')
                text_parts.append(text)

    return ''.join(text_parts)


# ---------------------------------------------------------------------------
# Exercise 10: Validate Request Parameters
# ---------------------------------------------------------------------------
def validate_request_params(
    model: str,
    max_tokens: int,
    temperature: float,
) -> list[str]:
    """
    Validate API request parameters and return list of errors.
    """
    errors = []

    if not model or not isinstance(model, str):
        errors.append("model must be a non-empty string")

    if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 200000:
        errors.append("max_tokens must be between 1 and 200000")

    if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
        errors.append("temperature must be between 0 and 2")

    return errors


# ---------------------------------------------------------------------------
# Exercise 11: System Prompt Template
# ---------------------------------------------------------------------------
def format_system_prompt(
    role: str,
    context: dict[str, str],
) -> str:
    """
    Format a system prompt with role and context variables.
    """
    instructions = context.get('instructions', '')
    constraints = context.get('constraints', '')
    tone = context.get('tone', '')

    prompt = f"You are a {role}."

    if instructions:
        prompt += f" {instructions}"

    if constraints:
        prompt += f" Do not {constraints}."

    if tone:
        prompt += f" Be {tone}."

    return prompt


# ---------------------------------------------------------------------------
# Exercise 12: Model Capability Matcher
# ---------------------------------------------------------------------------
def match_model_to_task(
    task: str,
    require_vision: bool = False,
    require_speed: bool = False,
    require_power: bool = False,
) -> str:
    """
    Select the best Claude model for a task based on requirements.
    """
    # If vision is required, eliminate haiku
    if require_vision:
        if require_power:
            return 'claude-3-opus'
        else:
            return 'claude-3-5-sonnet'

    # If speed is required
    if require_speed:
        return 'claude-3-haiku'

    # If power is required
    if require_power:
        return 'claude-3-opus'

    # Default: balanced choice
    return 'claude-3-5-sonnet'


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    claude_resp = {
        'content': [{'type': 'text', 'text': 'Hello'}],
        'usage': {'input_tokens': 10}
    }
    text = parse_api_response(claude_resp)
    assert text == 'Hello'

    openai_resp = {
        'choices': [{'message': {'content': 'World'}}]
    }
    text = parse_api_response(openai_resp)
    assert text == 'World'

    # Test Exercise 2
    history = [{'role': 'user', 'content': 'Hi'}]
    msgs = build_messages('How are you?', history)
    assert len(msgs) == 2
    assert msgs[-1]['role'] == 'user'
    assert msgs[-1]['content'] == 'How are you?'

    # Test Exercise 3
    resp = {'usage': {'input_tokens': 100, 'output_tokens': 50}}
    usage = extract_token_usage(resp)
    assert usage['input_tokens'] == 100
    assert usage['output_tokens'] == 50

    # Test Exercise 4
    tokens = estimate_tokens('hello world')
    assert tokens == 3

    # Test Exercise 5
    cost = calculate_api_cost('claude-3-5-sonnet', 1000, 1000)
    expected = (1000 / 1_000_000) * 3 + (1000 / 1_000_000) * 15
    assert abs(cost - expected) < 0.000001

    # Test Exercise 6
    assert classify_api_error(401) == 'authentication'
    assert classify_api_error(400) == 'validation'
    assert classify_api_error(429) == 'rate_limit'
    assert classify_api_error(500) == 'server'
    assert classify_api_error(504) == 'timeout'

    # Test Exercise 7
    assert should_retry('rate_limit', 1) is True
    assert should_retry('authentication', 1) is False
    assert should_retry('rate_limit', 3) is False

    # Test Exercise 8
    assert calculate_backoff_delay(1) == 1.0
    assert calculate_backoff_delay(2) == 2.0
    assert calculate_backoff_delay(3) == 4.0

    # Test Exercise 9
    events = [
        {'type': 'content_block_delta', 'delta': {'type': 'text_delta', 'text': 'Hi'}},
        {'type': 'content_block_delta', 'delta': {'type': 'text_delta', 'text': '!'}},
    ]
    text = process_stream_events(events)
    assert text == 'Hi!'

    # Test Exercise 10
    errors = validate_request_params('claude', 1000, 1.0)
    assert len(errors) == 0

    errors = validate_request_params('', 1000, 1.0)
    assert len(errors) > 0

    # Test Exercise 11
    prompt = format_system_prompt('assistant', {
        'instructions': 'Be helpful',
        'constraints': 'No lies',
        'tone': 'friendly'
    })
    assert 'assistant' in prompt
    assert 'helpful' in prompt

    # Test Exercise 12
    model = match_model_to_task('simple task')
    assert model == 'claude-3-5-sonnet'

    model = match_model_to_task('image analysis', require_vision=True, require_power=True)
    assert model == 'claude-3-opus'

    print('All tests passed!')
