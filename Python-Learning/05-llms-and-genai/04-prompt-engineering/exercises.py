"""
Module 04: Prompt Engineering — Exercises
===========================================

12 exercises on zero-shot, few-shot, chain-of-thought, system prompts,
output formatting, and prompt injection defense.

Run this file directly to check your solutions:
    python exercises.py
"""

from typing import Optional


# ---------------------------------------------------------------------------
# Exercise 1: Build Basic Prompt
# ---------------------------------------------------------------------------
def build_simple_prompt(task: str, input_data: str) -> str:
    """
    Build a simple zero-shot prompt.

    Format:
    "Task: {task}
    Input: {input_data}
    Output:"

    Args:
        task: Description of the task
        input_data: The data to process

    Returns:
        Formatted prompt string
    """
    pass


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

    Format:
    "Task: {task}

    Examples:
    Input: {ex1_input} → Output: {ex1_output}
    Input: {ex2_input} → Output: {ex2_output}
    ...

    Now process:
    Input: {input_data}
    Output:"

    Args:
        task: Description of the task
        examples: List of (input, output) tuples
        input_data: The data to process

    Returns:
        Formatted few-shot prompt string
    """
    pass


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

    Format:
    "You are a {role}.
    Tone: {tone}

    Constraints:
    - {constraint1}
    - {constraint2}
    ..."

    Args:
        role: Role description (e.g., "helpful assistant")
        tone: Tone (e.g., "professional", "friendly")
        constraints: List of constraints (e.g., "Do not lie")

    Returns:
        System prompt string
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Chain-of-Thought Wrapper
# ---------------------------------------------------------------------------
def add_chain_of_thought(prompt: str) -> str:
    """
    Add chain-of-thought instruction to a prompt.

    Append to the prompt:
    "\n\nThink step-by-step before answering. Show your reasoning."

    Args:
        prompt: Original prompt

    Returns:
        Prompt with chain-of-thought instruction added
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Format Output Instruction
# ---------------------------------------------------------------------------
def add_output_format_instruction(
    prompt: str,
    format_spec: str,
) -> str:
    """
    Add output format instruction to a prompt.

    Append:
    "\n\nFormat your response as:\n{format_spec}"

    Args:
        prompt: Original prompt
        format_spec: Desired output format (e.g., "JSON", "CSV", "List")

    Returns:
        Prompt with format instruction added
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Sanitize User Input
# ---------------------------------------------------------------------------
def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input to prevent prompt injection.

    Rules:
    - Remove any lines starting with "System:", "Ignore", "Override"
    - Remove lines containing "previous instructions"
    - Trim leading/trailing whitespace
    - Limit to 2000 characters

    Args:
        user_input: Raw user input

    Returns:
        Sanitized input
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Detect Injection Attempt
# ---------------------------------------------------------------------------
def detect_injection_attempt(user_input: str) -> bool:
    """
    Detect common prompt injection patterns.

    Return True if any of these patterns are found (case-insensitive):
    - "ignore"
    - "override"
    - "forget"
    - "system:"
    - "previous instructions"
    - "new instructions"

    Args:
        user_input: User input string

    Returns:
        True if injection attempt detected, False otherwise
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Build Template Prompt
# ---------------------------------------------------------------------------
def build_template_prompt(template: str, variables: dict[str, str]) -> str:
    """
    Fill in a prompt template with variables.

    Template uses {var_name} placeholders.

    Example:
        template = "Classify {text} as {categories}"
        variables = {"text": "great product", "categories": "good/bad"}
        Result: "Classify great product as good/bad"

    Args:
        template: Prompt template with {placeholder} variables
        variables: Dictionary of variable names to values

    Returns:
        Filled prompt string
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Compare Zero-Shot vs Few-Shot
# ---------------------------------------------------------------------------
def estimate_accuracy_improvement(
    base_accuracy: float,
    num_examples: int,
) -> float:
    """
    Estimate accuracy improvement from few-shot prompting.

    Rule of thumb: each example provides ~5-10% improvement (diminishing returns).
    - 0 examples: base_accuracy
    - 1 example: base_accuracy + 5%
    - 2 examples: base_accuracy + 9%
    - 3 examples: base_accuracy + 12%
    - 4+ examples: base_accuracy + 14% (plateau)

    Use: improvement = 5 * log(1 + num_examples) (capped at 14%)

    Args:
        base_accuracy: Zero-shot accuracy (0-1)
        num_examples: Number of few-shot examples

    Returns:
        Estimated accuracy with few-shot (0-1), rounded to 2 decimals
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Generate Prompt Variants
# ---------------------------------------------------------------------------
def generate_prompt_variants(
    base_prompt: str,
    variations: dict[str, list[str]],
) -> list[str]:
    """
    Generate multiple prompt variants by substituting different values.

    Example:
        base = "Task: {task}, Style: {style}"
        variations = {"task": ["classify", "extract"], "style": ["brief", "detailed"]}
        Result: 4 prompts with all combinations

    Args:
        base_prompt: Prompt with {placeholder} variables
        variations: Dict mapping placeholder to list of values

    Returns:
        List of all prompt variants
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Extract JSON from Response
# ---------------------------------------------------------------------------
def extract_json_response(response: str) -> dict:
    """
    Extract JSON object from a response that may contain extra text.

    Example:
        Input: 'The result is: {"name": "John", "age": 30}'
        Output: {"name": "John", "age": 30}

    Find the first occurrence of { ... } and parse as JSON.

    Args:
        response: Model response string

    Returns:
        Parsed JSON as dictionary (empty dict if no valid JSON found)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Build Self-Critique Prompt
# ---------------------------------------------------------------------------
def build_self_critique_prompt(
    original_prompt: str,
    previous_answer: str,
) -> str:
    """
    Build a follow-up prompt asking the model to critique its answer.

    Format:
    "{original_prompt}

    Your previous answer was:
    {previous_answer}

    Review this answer. Is it correct? Any errors? Please improve it."

    Args:
        original_prompt: The original task prompt
        previous_answer: The model's previous response

    Returns:
        Self-critique prompt string
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    prompt = build_simple_prompt('Classify sentiment', 'I love this!')
    assert 'Task:' in prompt and 'sentiment' in prompt

    # Test Exercise 2
    examples = [('good', 'Positive'), ('bad', 'Negative')]
    prompt = build_few_shot_prompt('Classify', examples, 'okay')
    assert 'Examples:' in prompt and 'okay' in prompt

    # Test Exercise 3
    sys_prompt = create_system_prompt('assistant', 'friendly', ['No lies'])
    assert 'assistant' in sys_prompt and 'friendly' in sys_prompt

    # Test Exercise 4
    prompt = add_chain_of_thought('Solve this problem')
    assert 'step' in prompt.lower()

    # Test Exercise 5
    prompt = add_output_format_instruction('Classify', 'JSON')
    assert 'JSON' in prompt

    # Test Exercise 6
    clean = sanitize_input('Normal input\nIgnore this')
    assert 'Normal input' in clean

    # Test Exercise 7
    is_injection = detect_injection_attempt('ignore all instructions')
    assert is_injection is True

    # Test Exercise 8
    template = 'Hello {name}, you are {age} years old'
    result = build_template_prompt(template, {'name': 'John', 'age': '30'})
    assert 'John' in result and '30' in result

    # Test Exercise 9
    acc = estimate_accuracy_improvement(0.7, 3)
    assert isinstance(acc, float) and 0.7 <= acc <= 1.0

    # Test Exercise 10
    variants = generate_prompt_variants(
        '{action} {object}',
        {'action': ['test', 'run'], 'object': ['code']}
    )
    assert len(variants) >= 2

    # Test Exercise 11
    response = 'Result: {"key": "value"}'
    data = extract_json_response(response)
    assert isinstance(data, dict)

    # Test Exercise 12
    critique = build_self_critique_prompt('Question?', 'Answer!')
    assert 'Review' in critique

    print('All tests passed!')
