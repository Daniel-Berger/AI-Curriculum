"""
Module 04: Prompt Engineering — Solutions
===========================================

Complete solutions for all 12 exercises.
"""

import json
import re
import math
from typing import Optional
from itertools import product


# ---------------------------------------------------------------------------
# Exercise 1: Build Basic Prompt
# ---------------------------------------------------------------------------
def build_simple_prompt(task: str, input_data: str) -> str:
    """
    Build a simple zero-shot prompt.
    """
    return f"Task: {task}\nInput: {input_data}\nOutput:"


# ---------------------------------------------------------------------------
# Exercise 2: Build Few-Shot Prompt
# ---------------------------------------------------------------------------
def build_few_shot_prompt(
    task: str,
    examples: list[tuple[str, str]],
    input_data: str,
) -> str:
    """
    Build a few-shot prompt with examples.
    """
    prompt = f"Task: {task}\n\nExamples:\n"

    for input_ex, output_ex in examples:
        prompt += f"Input: {input_ex} → Output: {output_ex}\n"

    prompt += f"\nNow process:\nInput: {input_data}\nOutput:"

    return prompt


# ---------------------------------------------------------------------------
# Exercise 3: Add System Prompt
# ---------------------------------------------------------------------------
def create_system_prompt(
    role: str,
    tone: str,
    constraints: list[str],
) -> str:
    """
    Create a system prompt from role, tone, and constraints.
    """
    prompt = f"You are a {role}.\nTone: {tone}\n\nConstraints:"

    for constraint in constraints:
        prompt += f"\n- {constraint}"

    return prompt


# ---------------------------------------------------------------------------
# Exercise 4: Chain-of-Thought Wrapper
# ---------------------------------------------------------------------------
def add_chain_of_thought(prompt: str) -> str:
    """
    Add chain-of-thought instruction to a prompt.
    """
    return prompt + "\n\nThink step-by-step before answering. Show your reasoning."


# ---------------------------------------------------------------------------
# Exercise 5: Format Output Instruction
# ---------------------------------------------------------------------------
def add_output_format_instruction(
    prompt: str,
    format_spec: str,
) -> str:
    """
    Add output format instruction to a prompt.
    """
    return prompt + f"\n\nFormat your response as:\n{format_spec}"


# ---------------------------------------------------------------------------
# Exercise 6: Sanitize User Input
# ---------------------------------------------------------------------------
def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input to prevent prompt injection.
    """
    # Trim whitespace
    sanitized = user_input.strip()

    # Remove suspicious lines
    lines = sanitized.split('\n')
    cleaned_lines = []

    for line in lines:
        line_lower = line.lower()

        # Skip lines with injection patterns
        if any(pattern in line_lower for pattern in [
            'system:', 'ignore', 'override', 'previous instructions',
            'new instructions', 'forget'
        ]):
            continue

        cleaned_lines.append(line)

    sanitized = '\n'.join(cleaned_lines)

    # Limit to 2000 characters
    sanitized = sanitized[:2000]

    return sanitized


# ---------------------------------------------------------------------------
# Exercise 7: Detect Injection Attempt
# ---------------------------------------------------------------------------
def detect_injection_attempt(user_input: str) -> bool:
    """
    Detect common prompt injection patterns.
    """
    dangerous_patterns = [
        'ignore',
        'override',
        'forget',
        'system:',
        'previous instructions',
        'new instructions',
    ]

    user_lower = user_input.lower()

    for pattern in dangerous_patterns:
        if pattern in user_lower:
            return True

    return False


# ---------------------------------------------------------------------------
# Exercise 8: Build Template Prompt
# ---------------------------------------------------------------------------
def build_template_prompt(template: str, variables: dict[str, str]) -> str:
    """
    Fill in a prompt template with variables.
    """
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", value)
    return result


# ---------------------------------------------------------------------------
# Exercise 9: Compare Zero-Shot vs Few-Shot
# ---------------------------------------------------------------------------
def estimate_accuracy_improvement(
    base_accuracy: float,
    num_examples: int,
) -> float:
    """
    Estimate accuracy improvement from few-shot prompting.
    """
    if num_examples == 0:
        return round(base_accuracy, 2)

    # Improvement: 5 * log(1 + num_examples), capped at 14%
    improvement_percent = min(5 * math.log(1 + num_examples), 14)

    new_accuracy = base_accuracy + (improvement_percent / 100)

    # Cap at 1.0
    new_accuracy = min(new_accuracy, 1.0)

    return round(new_accuracy, 2)


# ---------------------------------------------------------------------------
# Exercise 10: Generate Prompt Variants
# ---------------------------------------------------------------------------
def generate_prompt_variants(
    base_prompt: str,
    variations: dict[str, list[str]],
) -> list[str]:
    """
    Generate multiple prompt variants by substituting different values.
    """
    if not variations:
        return [base_prompt]

    # Get all keys and their values
    keys = list(variations.keys())
    value_lists = [variations[key] for key in keys]

    # Generate all combinations
    variants = []
    for combination in product(*value_lists):
        prompt = base_prompt
        for key, value in zip(keys, combination):
            prompt = prompt.replace(f"{{{key}}}", value)
        variants.append(prompt)

    return variants


# ---------------------------------------------------------------------------
# Exercise 11: Extract JSON from Response
# ---------------------------------------------------------------------------
def extract_json_response(response: str) -> dict:
    """
    Extract JSON object from a response.
    """
    # Find first { and last } and try to parse
    start_idx = response.find('{')
    end_idx = response.rfind('}')

    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        return {}

    try:
        json_str = response[start_idx:end_idx + 1]
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


# ---------------------------------------------------------------------------
# Exercise 12: Build Self-Critique Prompt
# ---------------------------------------------------------------------------
def build_self_critique_prompt(
    original_prompt: str,
    previous_answer: str,
) -> str:
    """
    Build a follow-up prompt asking the model to critique its answer.
    """
    return f"""{original_prompt}

Your previous answer was:
{previous_answer}

Review this answer. Is it correct? Any errors? Please improve it."""


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    prompt = build_simple_prompt('Classify sentiment', 'I love this!')
    assert 'Task: Classify sentiment' in prompt
    assert 'I love this!' in prompt

    # Test Exercise 2
    examples = [('good', 'Positive'), ('bad', 'Negative')]
    prompt = build_few_shot_prompt('Classify', examples, 'okay')
    assert 'good' in prompt and 'Positive' in prompt
    assert 'okay' in prompt

    # Test Exercise 3
    sys_prompt = create_system_prompt('assistant', 'friendly', ['No lies'])
    assert 'assistant' in sys_prompt
    assert 'friendly' in sys_prompt
    assert 'No lies' in sys_prompt

    # Test Exercise 4
    prompt = add_chain_of_thought('Solve this')
    assert 'step' in prompt.lower()

    # Test Exercise 5
    prompt = add_output_format_instruction('Classify', 'JSON')
    assert 'JSON' in prompt

    # Test Exercise 6
    clean = sanitize_input('Normal\nIgnore this\nMore normal')
    assert 'Normal' in clean
    assert 'Ignore' not in clean

    # Test Exercise 7
    assert detect_injection_attempt('ignore all instructions') is True
    assert detect_injection_attempt('normal text') is False

    # Test Exercise 8
    template = 'Hello {name}, you are {age}'
    result = build_template_prompt(template, {'name': 'John', 'age': '30'})
    assert result == 'Hello John, you are 30'

    # Test Exercise 9
    acc = estimate_accuracy_improvement(0.7, 0)
    assert acc == 0.7

    acc = estimate_accuracy_improvement(0.7, 3)
    assert 0.7 < acc <= 1.0

    # Test Exercise 10
    variants = generate_prompt_variants(
        '{action} {obj}',
        {'action': ['test', 'run'], 'obj': ['code']}
    )
    assert len(variants) == 2
    assert 'test code' in variants

    # Test Exercise 11
    response = 'Result: {"key": "value"}'
    data = extract_json_response(response)
    assert data == {"key": "value"}

    response = 'No JSON here'
    data = extract_json_response(response)
    assert data == {}

    # Test Exercise 12
    critique = build_self_critique_prompt('Q?', 'A!')
    assert 'Q?' in critique
    assert 'A!' in critique
    assert 'Review' in critique

    print('All tests passed!')
