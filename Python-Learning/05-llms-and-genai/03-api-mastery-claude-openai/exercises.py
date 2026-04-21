"""
Module 03: API Mastery — Claude & OpenAI — Exercises
======================================================

12 exercises on API integration, error handling, streaming, and multi-provider patterns.

These exercises use mock patterns (no real API keys needed).

Run this file directly to check your solutions:
    python exercises.py
"""

from typing import Optional, Protocol, Any
from dataclasses import dataclass
from enum import Enum


# ---------------------------------------------------------------------------
# Exercise 1: Parse API Response Structure
# ---------------------------------------------------------------------------
def parse_api_response(response: dict) -> str:
    """
    Extract the assistant's text response from a Claude/OpenAI API response.

    The response format varies slightly:
    - Claude: response['content'][0]['text']
    - OpenAI: response['choices'][0]['message']['content']

    Detect which format and extract the text.

    Args:
        response: API response dictionary

    Returns:
        The assistant's text response (string)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Build Messages Array
# ---------------------------------------------------------------------------
def build_messages(
    user_input: str,
    conversation_history: list[dict],
) -> list[dict]:
    """
    Build a messages array from conversation history and current user input.

    Append the current user input to the history.

    Args:
        user_input: Current user message
        conversation_history: List of previous messages with 'role' and 'content'

    Returns:
        Complete messages list ready for API call
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Extract Token Usage
# ---------------------------------------------------------------------------
def extract_token_usage(response: dict) -> dict[str, int]:
    """
    Extract input and output token counts from API response.

    Format: response['usage']['input_tokens'] and ['output_tokens']

    Args:
        response: API response dictionary

    Returns:
        Dictionary with 'input_tokens' and 'output_tokens' keys
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Estimate Token Count
# ---------------------------------------------------------------------------
def estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count using the rule: 1 token ≈ 4 characters.

    Args:
        text: Input text

    Returns:
        Estimated number of tokens
    """
    pass


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

    Use these pricing tiers (per million tokens):
    - claude-3-5-sonnet: input $3, output $15
    - claude-3-opus: input $15, output $75
    - gpt-4o: input $5, output $15
    - gpt-3.5-turbo: input $0.50, output $1.50

    Args:
        model: Model identifier string
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in dollars (float)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Classify Error Type
# ---------------------------------------------------------------------------
def classify_api_error(error_code: int) -> str:
    """
    Classify API error by HTTP status code.

    - 401, 403: 'authentication'
    - 400, 422: 'validation'
    - 429: 'rate_limit'
    - 500, 503: 'server'
    - 504: 'timeout'
    - Other: 'unknown'

    Args:
        error_code: HTTP status code (int)

    Returns:
        Error classification string
    """
    pass


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

    Rules:
    - Never retry 'authentication' or 'validation' errors
    - Retry 'rate_limit', 'server', 'timeout' up to max_retries times
    - Return False if max_retries exceeded

    Args:
        error_type: Classification from classify_api_error
        attempt_count: Current attempt number (1-based)
        max_retries: Maximum number of retries

    Returns:
        True if should retry, False otherwise
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Calculate Backoff Delay
# ---------------------------------------------------------------------------
def calculate_backoff_delay(
    attempt_count: int,
    base_delay: float = 1.0,
) -> float:
    """
    Calculate exponential backoff delay for retry attempt.

    Formula: delay = base_delay * (2 ^ (attempt_count - 1))

    Args:
        attempt_count: Current attempt number (1-based)
        base_delay: Initial delay in seconds

    Returns:
        Delay in seconds (float)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Convert Streaming Response
# ---------------------------------------------------------------------------
def process_stream_events(events: list[dict]) -> str:
    """
    Reconstruct complete response from streaming events.

    Stream events format:
    [
        {"type": "message_start", "message": {...}},
        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Hello"}},
        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": " world"}},
        {"type": "message_stop"}
    ]

    Args:
        events: List of streaming event dictionaries

    Returns:
        Complete text response
    """
    pass


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

    Rules:
    - model: must be a non-empty string
    - max_tokens: must be between 1 and 200000
    - temperature: must be between 0 and 2 (if provided)

    Args:
        model: Model identifier
        max_tokens: Max tokens in response
        temperature: Sampling temperature

    Returns:
        List of error messages (empty if all valid)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: System Prompt Template
# ---------------------------------------------------------------------------
def format_system_prompt(
    role: str,
    context: dict[str, str],
) -> str:
    """
    Format a system prompt with role and context variables.

    Template:
    "You are a {role}. {instructions}"

    Where instructions are built from context dict:
    - context['instructions']: Additional instructions
    - context['constraints']: What the model should not do
    - context['tone']: How the model should sound

    Args:
        role: Role description (e.g., "helpful assistant")
        context: Dictionary with 'instructions', 'constraints', 'tone'

    Returns:
        Formatted system prompt string
    """
    pass


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

    Available models and properties:
    - claude-3-haiku: fast, cheap, no vision, good for simple tasks
    - claude-3-5-sonnet: balanced, has vision, good for most tasks
    - claude-3-opus: most powerful, has vision, slowest, most expensive

    Select based on:
    - If require_vision: must support vision
    - If require_speed: prefer haiku > sonnet > opus
    - If require_power: prefer opus > sonnet > haiku
    - Otherwise: use sonnet (best balance)

    Args:
        task: Description of task
        require_vision: Whether task needs image input
        require_speed: Whether latency is critical
        require_power: Whether reasoning power is critical

    Returns:
        Selected model identifier string
    """
    pass


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

    # Test Exercise 2
    history = [{'role': 'user', 'content': 'Hi'}]
    msgs = build_messages('How are you?', history)
    assert len(msgs) == 2
    assert msgs[-1]['role'] == 'user'

    # Test Exercise 3
    resp = {'usage': {'input_tokens': 100, 'output_tokens': 50}}
    usage = extract_token_usage(resp)
    assert usage['input_tokens'] == 100

    # Test Exercise 4
    tokens = estimate_tokens('hello world')
    assert isinstance(tokens, int) and tokens > 0

    # Test Exercise 5
    cost = calculate_api_cost('claude-3-5-sonnet', 1000, 1000)
    assert isinstance(cost, float) and cost > 0

    # Test Exercise 6
    error_type = classify_api_error(429)
    assert error_type == 'rate_limit'

    # Test Exercise 7
    should = should_retry('rate_limit', 1)
    assert should is True

    # Test Exercise 8
    delay = calculate_backoff_delay(1)
    assert delay == 1.0

    # Test Exercise 9
    events = [
        {'type': 'content_block_delta', 'delta': {'type': 'text_delta', 'text': 'Hi'}},
        {'type': 'content_block_delta', 'delta': {'type': 'text_delta', 'text': '!'}},
    ]
    text = process_stream_events(events)
    assert 'Hi' in text

    # Test Exercise 10
    errors = validate_request_params('claude', 1000, 1.0)
    assert isinstance(errors, list)

    # Test Exercise 11
    prompt = format_system_prompt('assistant', {
        'instructions': 'Be helpful',
        'constraints': 'No lies',
        'tone': 'friendly'
    })
    assert 'assistant' in prompt

    # Test Exercise 12
    model = match_model_to_task('simple classification', require_speed=True)
    assert model in ['claude-3-haiku', 'claude-3-5-sonnet', 'claude-3-opus']

    print('All tests passed!')
