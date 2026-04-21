# Module 03: API Mastery — Claude & OpenAI

## Why This Module Matters for Interviews

API integration is the practical skill most LLM engineers need immediately. You'll be asked:
- "How do you call Claude's API in production?"
- "How do you handle rate limits and errors?"
- "What's the difference between streaming and non-streaming?"
- "How do you architect multi-provider support?"

This module bridges from LLM concepts to real-world code patterns. You will NOT need real API keys for exercises (we use mocks), but you must understand the actual patterns used in production.

---

## The Anthropic Claude API

### API Overview

Anthropic's Claude API uses a **messages-based architecture**:

```
POST /v1/messages

{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 1024,
  "system": "You are a helpful assistant.",
  "messages": [
    {"role": "user", "content": "Hello, Claude"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "Tell me a joke"}
  ]
}
```

**Key concepts:**
- **Model**: Specifies which Claude version (Haiku, Sonnet, Opus)
- **Messages**: List of message objects with roles (user, assistant, system)
- **Max tokens**: Maximum length of response (not total conversation)
- **System prompt**: Special first message that sets behavior

### Basic Usage

```python
import anthropic

client = anthropic.Anthropic(api_key="sk-ant-...")

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": "What is 2+2?"}
    ]
)

print(response.content[0].text)
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model identifier (claude-3-5-sonnet, claude-3-opus, claude-3-haiku) |
| `messages` | array | Yes | List of message dicts with role and content |
| `max_tokens` | int | Yes | Max tokens in response (1-200000) |
| `system` | string | No | System prompt to set context/behavior |
| `temperature` | float | No | Randomness (0-1, default 1.0) |
| `top_p` | float | No | Nucleus sampling (0-1) |
| `top_k` | int | No | Top-K sampling |
| `tools` | array | No | Tool/function definitions for tool_use |
| `tool_choice` | object | No | Force tool use or allow auto |

### Response Structure

```python
{
    "id": "msg_1234567890",
    "type": "message",
    "role": "assistant",
    "content": [
        {
            "type": "text",
            "text": "The answer is 4."
        }
    ],
    "model": "claude-3-5-sonnet-20241022",
    "stop_reason": "end_turn",
    "stop_sequence": null,
    "usage": {
        "input_tokens": 10,
        "output_tokens": 5
    }
}
```

### Model Options

| Model | Context | Strengths | Cost |
|-------|---------|-----------|------|
| claude-3-haiku | 200K | Fast, cheap | Lowest |
| claude-3-5-sonnet | 200K | Best balance | Medium |
| claude-3-opus | 200K | Most powerful | Highest |

---

## Streaming API

Streaming returns tokens as they're generated, improving perceived latency.

### Non-Streaming (Default)

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a poem"}]
)
# Waits for entire response before returning
print(response.content[0].text)
```

### Streaming

```python
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a poem"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

**Stream event types:**
- `message_start`: Metadata (model, role, ID)
- `content_block_start`: Signifies start of text block
- `content_block_delta`: Contains incremental `type: "text_delta"` with `text` field
- `message_stop`: End of message
- `message_delta`: Final usage stats

---

## Vision API (Image Input)

Claude can process images (JPEG, PNG, GIF, WebP).

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_encoded_image,
                    },
                },
                {
                    "type": "text",
                    "text": "What's in this image?"
                }
            ],
        }
    ],
)
```

---

## The OpenAI API

### API Overview

OpenAI's API is similar in structure but uses different parameter names:

```python
import openai

client = openai.OpenAI(api_key="sk-...")

response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.7,
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "What is 2+2?"}
    ]
)

print(response.choices[0].message.content)
```

### Key Differences from Claude

| Feature | Claude | OpenAI |
|---------|--------|--------|
| Max tokens param | `max_tokens` (required) | `max_tokens` (optional) |
| System prompt | In messages array or `system` param | In messages with role='system' |
| Streaming | `messages.stream()` context | `stream=True` parameter |
| Stop tokens | `stop_sequences` | `stop` (list) |
| Function calling | `tools` + `tool_use` | `tools` + `function` |

### Models

| Model | Context | Strengths |
|-------|---------|-----------|
| gpt-4o | 128K | Multimodal, strong reasoning |
| gpt-4-turbo | 128K | Previous flagship |
| gpt-3.5-turbo | 16K | Fast, cheap |

---

## Multi-Provider Pattern

Production systems often support multiple providers for redundancy and cost optimization.

### Provider Abstraction

```python
from typing import Protocol

class LLMProvider(Protocol):
    def call(
        self,
        messages: list[dict],
        system: str,
        max_tokens: int,
        model: str,
    ) -> str:
        """Generate response from any provider."""
        ...

class AnthropicProvider:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def call(self, messages, system, max_tokens, model):
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages
        )
        return response.content[0].text

class OpenAIProvider:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    def call(self, messages, system, max_tokens, model):
        # Transform system message format
        all_messages = [{"role": "system", "content": system}] + messages
        response = self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=all_messages
        )
        return response.choices[0].message.content
```

### Failover Logic

```python
def call_with_fallback(
    primary_provider: LLMProvider,
    fallback_provider: LLMProvider,
    messages: list[dict],
    system: str,
    max_tokens: int,
    primary_model: str,
    fallback_model: str,
) -> str:
    """Try primary provider, fall back to secondary."""
    try:
        return primary_provider.call(
            messages=messages,
            system=system,
            max_tokens=max_tokens,
            model=primary_model
        )
    except (RateLimitError, APIError, Timeout):
        return fallback_provider.call(
            messages=messages,
            system=system,
            max_tokens=max_tokens,
            model=fallback_model
        )
```

---

## Error Handling

### Common Error Types

```python
class RateLimitError(Exception):
    """API rate limit exceeded."""
    pass

class APIError(Exception):
    """Generic API error (500, 503, etc.)."""
    pass

class AuthenticationError(Exception):
    """Invalid API key or permissions."""
    pass

class ValidationError(Exception):
    """Invalid request (bad parameter)."""
    pass

class TimeoutError(Exception):
    """Request timed out."""
    pass
```

### Retry with Exponential Backoff

```python
import time
from functools import wraps

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for automatic retry with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (RateLimitError, APIError) as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
                except (AuthenticationError, ValidationError):
                    raise  # Don't retry on client errors
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def call_api(client, messages):
    return client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=messages
    )
```

---

## Async / Concurrent Calls

For calling multiple APIs in parallel:

```python
import asyncio
from typing import Coroutine

async def call_claude_async(messages: list[dict], system: str) -> str:
    """Async call to Claude (requires async client)."""
    client = anthropic.AsyncAnthropic(api_key="sk-ant-...")
    response = await client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=system,
        messages=messages
    )
    return response.content[0].text

async def call_multiple_providers(providers_and_params: list[tuple]) -> list[str]:
    """Call multiple providers in parallel."""
    tasks = [
        call_claude_async(params['messages'], params['system'])
        for params in providers_and_params
    ]
    results = await asyncio.gather(*tasks)
    return results

# Usage
async def main():
    providers = [
        {"messages": [{"role": "user", "content": "Q1"}], "system": "Help"},
        {"messages": [{"role": "user", "content": "Q2"}], "system": "Help"},
    ]
    results = await call_multiple_providers(providers)
    print(results)

asyncio.run(main())
```

---

## Token Counting and Cost Estimation

### Counting Tokens

```python
# Anthropic doesn't provide a public token counter yet
# but you can estimate: 1 token ≈ 4 characters

def estimate_tokens(text: str) -> int:
    return len(text) // 4

# For accurate counts, call the API with max_tokens=1 and read usage
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1,
    messages=[{"role": "user", "content": "Hello"}]
)
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
```

### Cost Calculation

```python
PRICING = {
    "claude-3-5-sonnet": {
        "input": 3 / 1_000_000,      # $3 per million input tokens
        "output": 15 / 1_000_000,    # $15 per million output tokens
    },
    "gpt-4o": {
        "input": 5 / 1_000_000,      # $5 per million input tokens
        "output": 15 / 1_000_000,    # $15 per million output tokens
    },
}

def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Estimate API call cost in dollars."""
    pricing = PRICING[model]
    input_cost = input_tokens * pricing["input"]
    output_cost = output_tokens * pricing["output"]
    return input_cost + output_cost
```

---

## Best Practices

1. **Always include system prompt**: Guides model behavior and improves consistency
2. **Use appropriate temperature**: 0 for deterministic tasks, 0.7-1.0 for creative
3. **Implement retry logic**: API calls can fail transiently
4. **Stream for better UX**: Return tokens as they arrive rather than waiting
5. **Monitor costs**: Track token usage to catch runaway costs early
6. **Cache system prompts**: If using the same system prompt repeatedly
7. **Use specific models**: Claude Haiku for speed, Sonnet for balance, Opus for quality
8. **Handle timeouts**: Set explicit timeout values for all requests
9. **Log all API calls**: For debugging and audit trails
10. **Test with mock responses**: Use recorded responses in tests, not real API calls

---

## Interview Questions You Should Answer

1. "What are the main differences between Claude and OpenAI APIs?"
   - Messages format, parameter names, streaming mechanism

2. "How would you implement retry logic for API calls?"
   - Exponential backoff, distinguishing retryable vs non-retryable errors

3. "How do you stream responses?"
   - Context managers for Claude, stream parameter for OpenAI

4. "How would you support multiple LLM providers?"
   - Abstract interface, provider implementations, failover logic

5. "What's the impact of system prompts on model behavior?"
   - Affects consistency, safety, task performance

---

## Summary

- **Claude API**: Messages-based, requires max_tokens, system prompt optional
- **OpenAI API**: Similar structure, system in messages, max_tokens optional
- **Streaming**: Improved UX by returning tokens incrementally
- **Vision**: Both support image inputs (different formats)
- **Error Handling**: Retry with exponential backoff for transient errors
- **Multi-provider**: Abstract interface for flexibility and failover
- **Cost**: Estimate based on token counts and pricing tiers
