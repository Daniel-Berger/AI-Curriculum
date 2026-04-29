# Module 01: Customer Integration Patterns

## Introduction for Swift Developers

You have spent your career building polished client-side applications. In the world of Applied AI Engineering, you shift to a fundamentally different surface area: you are the person who ensures that *other* engineers can successfully build with AI APIs. Think of it as designing and supporting the SDK layer rather than the app layer. Every debugging instinct you developed chasing down `URLSession` failures and parsing API responses translates directly -- the protocols and patterns are different, but the systematic thinking is identical.

---

## 1. Introduction to Applied AI Engineering

### What Solutions Engineers Actually Do

Applied AI Engineers (also called Solutions Engineers, Developer Advocates, or Field Engineers at companies like Anthropic, OpenAI, and Google) sit at the intersection of engineering and customer success. The role is *not* training models. It is making sure customers can integrate, scale, and succeed with AI APIs in production.

**Day-to-day responsibilities:**

- **Technical onboarding**: Walk enterprise customers through first API calls, authentication, and architecture decisions
- **Debugging integration failures**: When a customer's integration breaks at 2 AM, you diagnose whether it is their code, their infrastructure, or the API itself
- **Building reference implementations**: Create sample apps, SDKs, and integration guides that thousands of developers will follow
- **Architecture reviews**: Evaluate customer system designs and recommend patterns for reliability, cost, and latency
- **Feedback loop to product**: Translate customer pain points into product requirements for the engineering team
- **Proof-of-concept builds**: Rapidly prototype solutions to demonstrate feasibility during sales cycles

### How This Differs from ML Engineering

| Dimension | ML Engineer | Applied AI / Solutions Engineer |
|-----------|-------------|-------------------------------|
| Primary output | Models, training pipelines | Integrations, reference code, customer success |
| Key metric | Model accuracy, training efficiency | Customer adoption, time-to-first-call, satisfaction |
| Debugging focus | Data quality, gradient issues | Auth errors, rate limits, SDK misuse |
| Codebase | Training scripts, experiment tracking | Client libraries, middleware, demo apps |
| Stakeholders | Research team, data team | Customers, sales, product |
| Languages | Python, C++ | Python, TypeScript, whatever the customer uses |

### The Skills That Transfer from iOS

Your iOS background gives you genuine advantages:

- **API design intuition**: You have used dozens of REST and SDK APIs. You know what makes a good developer experience.
- **Debugging network issues**: `URLSession`, Charles Proxy, network link conditioner -- you know how to trace a failing HTTP call.
- **Type safety mindset**: You instinctively think about request/response contracts, which is exactly the rigor customers need.
- **Client-side architecture**: Understanding MVC/MVVM helps you advise customers building AI-powered apps.

> **Swift Developer Note:** Think of this role as being the person who *designs* the Alamofire or URLSession API, then helps every app team in the company adopt it correctly. You are not building the model (that is like building UIKit itself) -- you are building the integration layer and supporting the developers who use it.

---

## 2. Diagnosing Customer Integration Failures

The single most valuable skill for an Applied AI Engineer is systematic debugging of integration failures. Customers will send you error messages, partial logs, and vague descriptions. You need a framework for rapid diagnosis.

### Common Failure Modes

#### 2.1 Authentication Errors

The most common first-call failure. Customers misconfigure API keys, use the wrong environment, or expose keys in client-side code.

```python
"""
Diagnostic tool for authentication failures across LLM providers.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AuthErrorType(Enum):
    MISSING_KEY = "missing_key"
    INVALID_KEY = "invalid_key"
    EXPIRED_KEY = "expired_key"
    WRONG_ENVIRONMENT = "wrong_environment"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    KEY_EXPOSED_CLIENT_SIDE = "key_exposed_client_side"


@dataclass
class AuthDiagnosis:
    error_type: AuthErrorType
    provider: str
    message: str
    recommended_fix: str
    severity: str  # "critical", "warning", "info"


def diagnose_auth_error(
    status_code: int,
    error_body: dict,
    provider: str,
    api_key_prefix: Optional[str] = None,
) -> AuthDiagnosis:
    """
    Diagnose authentication errors from LLM API responses.

    In a real SE role, you would build tools like this to rapidly
    triage customer issues instead of debugging each one manually.
    """
    # Check for missing key
    if status_code == 401 and not api_key_prefix:
        return AuthDiagnosis(
            error_type=AuthErrorType.MISSING_KEY,
            provider=provider,
            message="No API key provided in request",
            recommended_fix=(
                f"Set the API key via environment variable "
                f"({_env_var_for_provider(provider)}) or pass it "
                f"directly to the client constructor."
            ),
            severity="critical",
        )

    # Check for wrong provider key format
    key_prefixes = {
        "anthropic": "sk-ant-",
        "openai": "sk-",
        "google": "AI",
    }

    if api_key_prefix and provider in key_prefixes:
        expected_prefix = key_prefixes[provider]
        if not api_key_prefix.startswith(expected_prefix):
            return AuthDiagnosis(
                error_type=AuthErrorType.INVALID_KEY,
                provider=provider,
                message=(
                    f"Key prefix '{api_key_prefix[:8]}...' does not match "
                    f"expected prefix '{expected_prefix}' for {provider}"
                ),
                recommended_fix=(
                    f"You may be using an API key from a different provider. "
                    f"{provider.title()} keys start with '{expected_prefix}'."
                ),
                severity="critical",
            )

    # Check for permission errors (403)
    if status_code == 403:
        return AuthDiagnosis(
            error_type=AuthErrorType.INSUFFICIENT_PERMISSIONS,
            provider=provider,
            message="API key lacks required permissions",
            recommended_fix=(
                "Check your API key permissions in the provider dashboard. "
                "Ensure the key has access to the requested model and endpoint."
            ),
            severity="critical",
        )

    # Generic 401
    return AuthDiagnosis(
        error_type=AuthErrorType.INVALID_KEY,
        provider=provider,
        message=f"Authentication failed: {error_body.get('error', {}).get('message', 'Unknown')}",
        recommended_fix="Verify your API key is correct and has not been revoked.",
        severity="critical",
    )


def _env_var_for_provider(provider: str) -> str:
    env_vars = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
    }
    return env_vars.get(provider, f"{provider.upper()}_API_KEY")
```

#### 2.2 Rate Limiting

Rate limit errors are the second most common issue, especially during load testing or batch processing.

```python
"""
Rate limit diagnosis and adaptive throttling.
"""
import time
from dataclasses import dataclass, field
from collections import deque
from typing import Optional


@dataclass
class RateLimitInfo:
    """Parsed rate limit information from API response headers."""
    requests_limit: Optional[int] = None
    requests_remaining: Optional[int] = None
    tokens_limit: Optional[int] = None
    tokens_remaining: Optional[int] = None
    retry_after_seconds: Optional[float] = None
    reset_at: Optional[str] = None


def parse_rate_limit_headers(headers: dict, provider: str) -> RateLimitInfo:
    """
    Parse rate limit headers from different providers.
    Each provider uses slightly different header names.
    """
    info = RateLimitInfo()

    if provider == "anthropic":
        info.requests_limit = _safe_int(headers.get("anthropic-ratelimit-requests-limit"))
        info.requests_remaining = _safe_int(headers.get("anthropic-ratelimit-requests-remaining"))
        info.tokens_limit = _safe_int(headers.get("anthropic-ratelimit-tokens-limit"))
        info.tokens_remaining = _safe_int(headers.get("anthropic-ratelimit-tokens-remaining"))
        info.retry_after_seconds = _safe_float(headers.get("retry-after"))
    elif provider == "openai":
        info.requests_limit = _safe_int(headers.get("x-ratelimit-limit-requests"))
        info.requests_remaining = _safe_int(headers.get("x-ratelimit-remaining-requests"))
        info.tokens_limit = _safe_int(headers.get("x-ratelimit-limit-tokens"))
        info.tokens_remaining = _safe_int(headers.get("x-ratelimit-remaining-tokens"))
        info.retry_after_seconds = _safe_float(headers.get("retry-after"))

    return info


def _safe_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _safe_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


@dataclass
class AdaptiveRateLimiter:
    """
    Client-side rate limiter that adapts based on provider feedback.

    This prevents customers from hammering the API and getting blocked.
    Essential pattern for batch processing workloads.
    """
    max_requests_per_second: float = 10.0
    _request_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    _backoff_until: float = 0.0

    def wait_if_needed(self) -> None:
        """Block until it is safe to make another request."""
        now = time.monotonic()

        # Respect backoff from rate limit responses
        if now < self._backoff_until:
            sleep_time = self._backoff_until - now
            time.sleep(sleep_time)
            now = time.monotonic()

        # Enforce client-side rate limit using sliding window
        if self._request_times:
            window_start = now - 1.0  # 1-second window
            # Remove requests outside the window
            while self._request_times and self._request_times[0] < window_start:
                self._request_times.popleft()

            if len(self._request_times) >= self.max_requests_per_second:
                sleep_time = self._request_times[0] - window_start
                if sleep_time > 0:
                    time.sleep(sleep_time)

        self._request_times.append(time.monotonic())

    def apply_backoff(self, retry_after_seconds: float) -> None:
        """Apply server-requested backoff."""
        self._backoff_until = time.monotonic() + retry_after_seconds

    def adjust_rate(self, rate_limit_info: RateLimitInfo) -> None:
        """Dynamically adjust rate based on remaining quota."""
        if rate_limit_info.requests_remaining is not None and rate_limit_info.requests_limit:
            utilization = 1.0 - (
                rate_limit_info.requests_remaining / rate_limit_info.requests_limit
            )
            if utilization > 0.8:
                # Slow down when approaching limit
                self.max_requests_per_second *= 0.5
            elif utilization < 0.3:
                # Speed up when well under limit (up to original max)
                self.max_requests_per_second = min(
                    self.max_requests_per_second * 1.2, 10.0
                )
```

#### 2.3 Timeout and Latency Issues

```python
"""
Timeout diagnosis — one of the trickiest failure modes because
the cause can be client config, network, or model inference time.
"""
from dataclasses import dataclass
from enum import Enum


class TimeoutCause(Enum):
    CLIENT_TIMEOUT_TOO_LOW = "client_timeout_too_low"
    LARGE_CONTEXT_WINDOW = "large_context_window"
    COMPLEX_GENERATION = "complex_generation"
    NETWORK_LATENCY = "network_latency"
    PROVIDER_OVERLOADED = "provider_overloaded"


@dataclass
class TimeoutDiagnosis:
    likely_cause: TimeoutCause
    explanation: str
    recommended_fix: str


def diagnose_timeout(
    timeout_seconds: float,
    input_tokens: int,
    max_output_tokens: int,
    model: str,
    is_streaming: bool,
) -> TimeoutDiagnosis:
    """
    Diagnose why a request might be timing out.

    This encodes institutional knowledge about model performance
    characteristics that customers rarely have.
    """
    # Estimate expected latency based on model and token counts
    # These are rough heuristics — real values vary by load
    tokens_per_second = _estimated_throughput(model)
    estimated_time_to_first_token = _estimated_ttft(model, input_tokens)
    estimated_total_time = (
        estimated_time_to_first_token + max_output_tokens / tokens_per_second
    )

    if timeout_seconds < estimated_time_to_first_token:
        return TimeoutDiagnosis(
            likely_cause=TimeoutCause.CLIENT_TIMEOUT_TOO_LOW,
            explanation=(
                f"Your timeout ({timeout_seconds}s) is shorter than the "
                f"estimated time-to-first-token ({estimated_time_to_first_token:.1f}s) "
                f"for {model} with {input_tokens} input tokens."
            ),
            recommended_fix=(
                f"Increase your client timeout to at least "
                f"{estimated_total_time * 1.5:.0f}s, or switch to streaming "
                f"to get partial results sooner."
            ),
        )

    if input_tokens > 50_000:
        return TimeoutDiagnosis(
            likely_cause=TimeoutCause.LARGE_CONTEXT_WINDOW,
            explanation=(
                f"Large input ({input_tokens} tokens) increases processing time. "
                f"Context processing is roughly O(n) for attention computation."
            ),
            recommended_fix=(
                "Consider chunking your input, using RAG to reduce context size, "
                "or switching to a model optimized for long context."
            ),
        )

    if not is_streaming and timeout_seconds < estimated_total_time:
        return TimeoutDiagnosis(
            likely_cause=TimeoutCause.CLIENT_TIMEOUT_TOO_LOW,
            explanation=(
                f"Non-streaming request with {max_output_tokens} max output tokens "
                f"may take up to {estimated_total_time:.0f}s."
            ),
            recommended_fix=(
                "Enable streaming to receive tokens incrementally, or increase "
                f"your timeout to {estimated_total_time * 2:.0f}s."
            ),
        )

    return TimeoutDiagnosis(
        likely_cause=TimeoutCause.PROVIDER_OVERLOADED,
        explanation="Timeout is reasonable for the workload. Provider may be under heavy load.",
        recommended_fix=(
            "Implement retry with exponential backoff. Consider adding a "
            "fallback provider for high-availability requirements."
        ),
    )


def _estimated_throughput(model: str) -> float:
    """Estimated output tokens per second by model family."""
    throughput_map = {
        "claude-3-haiku": 120.0,
        "claude-3-5-haiku": 120.0,
        "claude-3-5-sonnet": 80.0,
        "claude-3-opus": 40.0,
        "gpt-4o-mini": 100.0,
        "gpt-4o": 70.0,
        "gpt-4-turbo": 40.0,
        "gemini-1.5-flash": 110.0,
        "gemini-1.5-pro": 60.0,
    }
    for key, value in throughput_map.items():
        if key in model:
            return value
    return 50.0  # conservative default


def _estimated_ttft(model: str, input_tokens: int) -> float:
    """Estimated time-to-first-token in seconds."""
    base_ttft = {
        "haiku": 0.3,
        "sonnet": 0.8,
        "opus": 2.0,
        "gpt-4o-mini": 0.3,
        "gpt-4o": 0.6,
        "flash": 0.3,
        "pro": 1.0,
    }
    base = 1.0
    for key, value in base_ttft.items():
        if key in model:
            base = value
            break
    # Add time for large contexts
    context_factor = 1.0 + (input_tokens / 100_000) * 0.5
    return base * context_factor
```

#### 2.4 Model Selection Mistakes

```python
"""
Customers frequently choose the wrong model for their use case.
This diagnostic helps identify mismatches.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelRecommendation:
    current_model: str
    recommended_model: str
    reason: str
    estimated_cost_change: str  # e.g., "-70%", "+50%"
    estimated_latency_change: str


def analyze_model_fit(
    model: str,
    avg_input_tokens: int,
    avg_output_tokens: int,
    requests_per_day: int,
    requires_complex_reasoning: bool,
    latency_sensitive: bool,
    budget_per_month_usd: Optional[float] = None,
) -> Optional[ModelRecommendation]:
    """
    Analyze whether a customer is using the right model for their workload.

    This is the kind of analysis you do during architecture reviews.
    Customers often default to the most powerful model without considering
    cost and latency tradeoffs.
    """
    # Estimate monthly cost for current model
    monthly_cost = _estimate_monthly_cost(
        model, avg_input_tokens, avg_output_tokens, requests_per_day
    )

    # Pattern: Using Opus/GPT-4 for simple classification tasks
    if (
        not requires_complex_reasoning
        and avg_output_tokens < 100
        and _is_premium_model(model)
    ):
        cheaper_model = _get_cheaper_alternative(model)
        cheaper_cost = _estimate_monthly_cost(
            cheaper_model, avg_input_tokens, avg_output_tokens, requests_per_day
        )
        savings_pct = (1 - cheaper_cost / monthly_cost) * 100 if monthly_cost > 0 else 0

        return ModelRecommendation(
            current_model=model,
            recommended_model=cheaper_model,
            reason=(
                f"Short outputs ({avg_output_tokens} tokens avg) without complex "
                f"reasoning suggest a simpler task. A smaller model can handle "
                f"classification, extraction, and formatting tasks at a fraction "
                f"of the cost."
            ),
            estimated_cost_change=f"-{savings_pct:.0f}%",
            estimated_latency_change="-60%",
        )

    # Pattern: Using cheap model but getting poor quality complaints
    if requires_complex_reasoning and _is_budget_model(model):
        better_model = _get_premium_alternative(model)
        return ModelRecommendation(
            current_model=model,
            recommended_model=better_model,
            reason=(
                "Complex reasoning tasks benefit significantly from larger models. "
                "The quality improvement often justifies the cost increase, especially "
                "if poor outputs require human review."
            ),
            estimated_cost_change="+200-400%",
            estimated_latency_change="+100%",
        )

    # Pattern: Latency-sensitive app using slow model
    if latency_sensitive and _is_slow_model(model):
        fast_model = _get_fast_alternative(model)
        return ModelRecommendation(
            current_model=model,
            recommended_model=fast_model,
            reason=(
                f"For latency-sensitive applications, {model} may introduce "
                f"unacceptable delays. Consider a faster model with streaming."
            ),
            estimated_cost_change="-50%",
            estimated_latency_change="-70%",
        )

    # Budget check
    if budget_per_month_usd and monthly_cost > budget_per_month_usd:
        cheaper = _get_cheaper_alternative(model)
        return ModelRecommendation(
            current_model=model,
            recommended_model=cheaper,
            reason=(
                f"Estimated monthly cost (${monthly_cost:,.0f}) exceeds budget "
                f"(${budget_per_month_usd:,.0f}). Consider a more cost-effective model "
                f"or reducing request volume."
            ),
            estimated_cost_change=f"-{((monthly_cost - budget_per_month_usd) / monthly_cost * 100):.0f}%",
            estimated_latency_change="-40%",
        )

    return None  # Current model seems appropriate


def _is_premium_model(model: str) -> bool:
    premium = ["opus", "gpt-4o", "gpt-4-turbo", "gemini-1.5-pro"]
    return any(p in model.lower() for p in premium)


def _is_budget_model(model: str) -> bool:
    budget = ["haiku", "gpt-4o-mini", "flash"]
    return any(b in model.lower() for b in budget)


def _is_slow_model(model: str) -> bool:
    slow = ["opus", "gpt-4-turbo"]
    return any(s in model.lower() for s in slow)


def _get_cheaper_alternative(model: str) -> str:
    alternatives = {
        "opus": "claude-3-5-sonnet-latest",
        "gpt-4o": "gpt-4o-mini",
        "gpt-4-turbo": "gpt-4o-mini",
        "gemini-1.5-pro": "gemini-1.5-flash",
    }
    for key, value in alternatives.items():
        if key in model.lower():
            return value
    return model


def _get_premium_alternative(model: str) -> str:
    alternatives = {
        "haiku": "claude-3-5-sonnet-latest",
        "gpt-4o-mini": "gpt-4o",
        "flash": "gemini-1.5-pro",
    }
    for key, value in alternatives.items():
        if key in model.lower():
            return value
    return model


def _get_fast_alternative(model: str) -> str:
    alternatives = {
        "opus": "claude-3-5-sonnet-latest",
        "gpt-4-turbo": "gpt-4o",
    }
    for key, value in alternatives.items():
        if key in model.lower():
            return value
    return model


def _estimate_monthly_cost(
    model: str, avg_input: int, avg_output: int, requests_per_day: int
) -> float:
    """Rough monthly cost estimate in USD."""
    # Prices per million tokens (input, output)
    pricing = {
        "claude-3-haiku": (0.25, 1.25),
        "claude-3-5-haiku": (1.00, 5.00),
        "claude-3-5-sonnet": (3.00, 15.00),
        "claude-3-opus": (15.00, 75.00),
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4o": (2.50, 10.00),
        "gpt-4-turbo": (10.00, 30.00),
        "gemini-1.5-flash": (0.075, 0.30),
        "gemini-1.5-pro": (3.50, 10.50),
    }
    input_price, output_price = 3.0, 15.0  # default
    for key, (ip, op) in pricing.items():
        if key in model.lower():
            input_price, output_price = ip, op
            break

    monthly_requests = requests_per_day * 30
    input_cost = (avg_input / 1_000_000) * input_price * monthly_requests
    output_cost = (avg_output / 1_000_000) * output_price * monthly_requests
    return input_cost + output_cost
```

### Systematic Debugging Framework

When a customer reports an issue, follow this decision tree:

```
1. Can the customer make ANY successful API call?
   ├── NO → Authentication issue (Section 2.1)
   └── YES → Continue
       2. Is the error intermittent or consistent?
           ├── INTERMITTENT → Rate limiting (2.2) or provider instability
           └── CONSISTENT → Continue
               3. Does the request return an error or time out?
                   ├── TIMEOUT → Latency issue (2.3)
                   └── ERROR → Parse the error code
                       4. HTTP status?
                           ├── 400 → Malformed request (check payload)
                           ├── 401/403 → Auth (2.1)
                           ├── 404 → Wrong endpoint or model name
                           ├── 429 → Rate limit (2.2)
                           ├── 500 → Provider issue (retry)
                           └── 529 → Provider overloaded (backoff)
```

> **Swift Developer Note:** This systematic approach is exactly like debugging a failing `URLSession` request. You check reachability first, then auth, then request format, then response parsing. The mental model is the same; only the specific error codes and headers change.

---

## 3. Multi-Provider Abstraction Layer

Enterprise customers frequently require multi-provider support for redundancy, cost optimization, or compliance reasons. Building a clean abstraction layer is a core SE skill.

### 3.1 Provider-Agnostic Interface

```python
"""
Multi-provider LLM client with a unified interface.

This is the kind of internal tool you build as an SE to
demonstrate integration patterns and to power your own demos.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, AsyncIterator
import time


class Provider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"


@dataclass
class Message:
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class LLMRequest:
    """Provider-agnostic request format."""
    messages: list[Message]
    model: str
    max_tokens: int = 1024
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    stream: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class LLMResponse:
    """Provider-agnostic response format."""
    content: str
    model: str
    provider: Provider
    usage: TokenUsage
    latency_ms: float
    raw_response: Optional[dict] = None
    stop_reason: Optional[str] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Send a completion request and return a response."""
        ...

    @abstractmethod
    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Stream a completion response token by token."""
        ...

    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """Check if a model identifier is valid for this provider."""
        ...
```

### 3.2 Provider Implementations

```python
"""
Concrete provider implementations.
In production, these wrap the official SDK clients.
"""
import asyncio
from typing import AsyncIterator


class AnthropicProvider(LLMProvider):
    """Wraps the Anthropic Python SDK."""

    SUPPORTED_MODELS = {
        "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-latest",
        "claude-3-opus-latest",
        "claude-sonnet-4-20250514",
    }

    def __init__(self, api_key: str):
        # In production: self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.api_key = api_key
        self.provider = Provider.ANTHROPIC

    async def complete(self, request: LLMRequest) -> LLMResponse:
        start = time.monotonic()

        # Convert our generic format to Anthropic's format
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
            if msg.role != "system"
        ]

        # Anthropic uses a separate system parameter, not a system message
        kwargs = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": messages,
        }
        if request.system_prompt:
            kwargs["system"] = request.system_prompt

        # In production: response = await self.client.messages.create(**kwargs)
        # For demonstration, we show the structure:
        response = await self._call_api(kwargs)

        elapsed_ms = (time.monotonic() - start) * 1000

        return LLMResponse(
            content=response["content"][0]["text"],
            model=response["model"],
            provider=self.provider,
            usage=TokenUsage(
                input_tokens=response["usage"]["input_tokens"],
                output_tokens=response["usage"]["output_tokens"],
            ),
            latency_ms=elapsed_ms,
            raw_response=response,
            stop_reason=response.get("stop_reason"),
        )

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        # In production: async with self.client.messages.stream(...) as stream:
        #     async for text in stream.text_stream:
        #         yield text
        yield "streaming not shown in example"

    def validate_model(self, model: str) -> bool:
        return model in self.SUPPORTED_MODELS

    async def _call_api(self, kwargs: dict) -> dict:
        """Placeholder for actual API call."""
        raise NotImplementedError("Replace with real Anthropic SDK call")


class OpenAIProvider(LLMProvider):
    """Wraps the OpenAI Python SDK."""

    SUPPORTED_MODELS = {
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "o1",
        "o1-mini",
        "o3-mini",
    }

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.provider = Provider.OPENAI

    async def complete(self, request: LLMRequest) -> LLMResponse:
        start = time.monotonic()

        # OpenAI uses system messages inline
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.extend(
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        )

        kwargs = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": messages,
        }

        response = await self._call_api(kwargs)
        elapsed_ms = (time.monotonic() - start) * 1000

        choice = response["choices"][0]
        return LLMResponse(
            content=choice["message"]["content"],
            model=response["model"],
            provider=self.provider,
            usage=TokenUsage(
                input_tokens=response["usage"]["prompt_tokens"],
                output_tokens=response["usage"]["completion_tokens"],
            ),
            latency_ms=elapsed_ms,
            raw_response=response,
            stop_reason=choice.get("finish_reason"),
        )

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        yield "streaming not shown in example"

    def validate_model(self, model: str) -> bool:
        return model in self.SUPPORTED_MODELS

    async def _call_api(self, kwargs: dict) -> dict:
        raise NotImplementedError("Replace with real OpenAI SDK call")
```

### 3.3 Unified Client with Fallback

```python
"""
The unified client that customers actually interact with.
Handles provider selection, fallback, and routing.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class UnifiedLLMClient:
    """
    A multi-provider LLM client with automatic fallback.

    This is the pattern you demonstrate to customers who need
    high availability across providers.
    """

    def __init__(self):
        self._providers: dict[Provider, LLMProvider] = {}
        self._fallback_order: list[Provider] = []
        self._model_to_provider: dict[str, Provider] = {}

    def register_provider(
        self,
        provider: Provider,
        client: LLMProvider,
        fallback_priority: int = 0,
    ) -> None:
        """Register a provider with optional fallback priority."""
        self._providers[provider] = client
        self._fallback_order.append(provider)
        # Sort by priority (lower number = higher priority)
        self._fallback_order.sort(key=lambda p: fallback_priority)

    def register_model_mapping(self, model: str, provider: Provider) -> None:
        """Map a model identifier to its provider."""
        self._model_to_provider[model] = provider

    async def complete(
        self,
        request: LLMRequest,
        provider: Optional[Provider] = None,
        enable_fallback: bool = True,
    ) -> LLMResponse:
        """
        Send a completion request, optionally falling back to other providers.

        The fallback logic automatically maps to equivalent models across
        providers when the primary provider fails.
        """
        # Determine which provider to use
        if provider:
            providers_to_try = [provider]
        elif request.model in self._model_to_provider:
            primary = self._model_to_provider[request.model]
            providers_to_try = [primary]
        else:
            providers_to_try = []
            for p, client in self._providers.items():
                if client.validate_model(request.model):
                    providers_to_try.append(p)

        if enable_fallback:
            # Add fallback providers not already in the list
            for p in self._fallback_order:
                if p not in providers_to_try:
                    providers_to_try.append(p)

        last_error: Optional[Exception] = None

        for p in providers_to_try:
            if p not in self._providers:
                continue

            client = self._providers[p]
            current_request = request

            # If falling back to a different provider, map the model
            if not client.validate_model(request.model):
                mapped_model = self._map_model(request.model, p)
                if not mapped_model:
                    continue
                current_request = LLMRequest(
                    messages=request.messages,
                    model=mapped_model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    system_prompt=request.system_prompt,
                    stream=request.stream,
                    metadata={**request.metadata, "original_model": request.model},
                )

            try:
                response = await client.complete(current_request)
                if p != providers_to_try[0]:
                    logger.warning(
                        f"Used fallback provider {p.value} "
                        f"(original: {providers_to_try[0].value})"
                    )
                return response
            except Exception as e:
                last_error = e
                logger.error(f"Provider {p.value} failed: {e}")
                continue

        raise RuntimeError(
            f"All providers failed. Last error: {last_error}"
        )

    @staticmethod
    def _map_model(model: str, target_provider: Provider) -> Optional[str]:
        """Map a model from one provider to an equivalent in another."""
        model_equivalents = {
            # Anthropic → others
            "claude-3-5-sonnet-latest": {
                Provider.OPENAI: "gpt-4o",
                Provider.GOOGLE: "gemini-1.5-pro",
            },
            "claude-3-5-haiku-latest": {
                Provider.OPENAI: "gpt-4o-mini",
                Provider.GOOGLE: "gemini-1.5-flash",
            },
            # OpenAI → others
            "gpt-4o": {
                Provider.ANTHROPIC: "claude-3-5-sonnet-latest",
                Provider.GOOGLE: "gemini-1.5-pro",
            },
            "gpt-4o-mini": {
                Provider.ANTHROPIC: "claude-3-5-haiku-latest",
                Provider.GOOGLE: "gemini-1.5-flash",
            },
        }
        mapping = model_equivalents.get(model, {})
        return mapping.get(target_provider)
```

### 3.4 Using LiteLLM for Quick Multi-Provider Support

For rapid prototyping (especially in POC scenarios), `litellm` provides a drop-in multi-provider abstraction:

```python
"""
LiteLLM provides a unified interface to 100+ LLM providers
with a single function call. Great for rapid prototyping.

pip install litellm
"""
import litellm
from litellm import completion, acompletion


# All providers use the same function signature
def call_any_provider(provider: str, prompt: str) -> str:
    """
    LiteLLM normalizes the interface so switching providers
    is just a model string change.
    """
    model_map = {
        "anthropic": "claude-3-5-sonnet-latest",
        "openai": "gpt-4o",
        "google": "gemini/gemini-1.5-pro",
        "mistral": "mistral/mistral-large-latest",
    }

    model = model_map.get(provider, provider)

    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )

    return response.choices[0].message.content


# LiteLLM also supports fallbacks natively
def call_with_fallback(prompt: str) -> str:
    """Use LiteLLM's built-in fallback mechanism."""
    response = completion(
        model="claude-3-5-sonnet-latest",
        messages=[{"role": "user", "content": prompt}],
        fallbacks=["gpt-4o", "gemini/gemini-1.5-pro"],
        max_tokens=1024,
    )
    return response.choices[0].message.content


# Async version for production use
async def call_async(prompt: str) -> str:
    """Async call — essential for web servers and batch processing."""
    response = await acompletion(
        model="claude-3-5-sonnet-latest",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    return response.choices[0].message.content
```

> **Swift Developer Note:** LiteLLM is analogous to how Moya wraps Alamofire to provide a protocol-oriented networking abstraction in Swift. Just as Moya lets you define your API as an enum conforming to `TargetType` and handles the underlying URLSession details, LiteLLM lets you swap between Anthropic, OpenAI, and Google by changing a single model string.

---

## 4. Retry and Circuit Breaker Patterns

API calls fail. Networks drop. Providers have outages. Robust retry logic is not optional -- it is the difference between a production system and a demo.

### 4.1 Exponential Backoff with Tenacity

```python
"""
Retry patterns using the tenacity library.
pip install tenacity

Tenacity is the standard Python library for retry logic,
similar to how you might use Combine's .retry() operator in Swift.
"""
import asyncio
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
    wait_random_exponential,
    retry_if_exception_type,
    retry_if_result,
    before_sleep_log,
    RetryError,
)

logger = logging.getLogger(__name__)


# ---- Basic retry with exponential backoff ----

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def call_llm_with_retry(client, request: dict) -> dict:
    """
    Basic retry: exponential backoff (1s, 2s, 4s, 8s, 16s)
    with a maximum of 5 attempts.
    """
    return client.messages.create(**request)


# ---- Retry only on transient errors ----

class TransientAPIError(Exception):
    """Errors that may succeed on retry."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")


class PermanentAPIError(Exception):
    """Errors that will NOT succeed on retry."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")


def classify_api_error(status_code: int, message: str) -> Exception:
    """
    Classify API errors as transient or permanent.

    This classification is crucial: retrying a 400 Bad Request
    wastes time and quota. Retrying a 429 or 500 is correct.
    """
    transient_codes = {429, 500, 502, 503, 529}
    permanent_codes = {400, 401, 403, 404, 405}

    if status_code in transient_codes:
        return TransientAPIError(status_code, message)
    elif status_code in permanent_codes:
        return PermanentAPIError(status_code, message)
    else:
        # Unknown status codes: treat as transient to be safe
        return TransientAPIError(status_code, message)


@retry(
    retry=retry_if_exception_type(TransientAPIError),
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5) | stop_after_delay(120),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_with_smart_retry(client, request: dict) -> dict:
    """
    Only retries transient errors. Permanent errors (400, 401, 403)
    are raised immediately without wasting retry attempts.
    """
    try:
        return client.messages.create(**request)
    except Exception as e:
        # Parse the HTTP status code from the SDK exception
        status_code = getattr(e, "status_code", 500)
        raise classify_api_error(status_code, str(e))


# ---- Async retry pattern ----

@retry(
    retry=retry_if_exception_type(TransientAPIError),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def call_with_async_retry(client, request: dict) -> dict:
    """
    Tenacity works seamlessly with async functions.
    Just add the decorator to an async def.
    """
    try:
        return await client.messages.create(**request)
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        raise classify_api_error(status_code, str(e))
```

### 4.2 Circuit Breaker Pattern

When a provider is having a prolonged outage, continuing to send requests wastes time and may worsen the situation. The circuit breaker pattern stops calling a failing service until it recovers.

```python
"""
Circuit breaker implementation for LLM API calls.

States:
  CLOSED  → Normal operation. Requests pass through.
  OPEN    → Provider is failing. Requests are immediately rejected.
  HALF_OPEN → Testing if provider has recovered.
"""
import time
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any


class CircuitState(Enum):
    CLOSED = "closed"        # Normal: requests flow through
    OPEN = "open"            # Tripped: requests rejected immediately
    HALF_OPEN = "half_open"  # Testing: limited requests allowed


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for API calls.

    This pattern is essential for multi-provider architectures:
    when one provider goes down, the circuit opens and traffic
    automatically routes to fallback providers.
    """
    failure_threshold: int = 5        # Failures before opening
    recovery_timeout: float = 30.0    # Seconds before trying again
    half_open_max_calls: int = 1      # Test calls in half-open state

    # Internal state
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _half_open_calls: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _total_calls: int = field(default=0, init=False)

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
        return self._state

    def record_success(self) -> None:
        """Record a successful call."""
        self._success_count += 1
        self._total_calls += 1

        if self._state == CircuitState.HALF_OPEN:
            # Recovery confirmed — close the circuit
            self._state = CircuitState.CLOSED
            self._failure_count = 0

        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0  # Reset consecutive failures

    def record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._total_calls += 1
        self._last_failure_time = time.monotonic()

        if self._state == CircuitState.HALF_OPEN:
            # Recovery failed — reopen the circuit
            self._state = CircuitState.OPEN

        elif (
            self._state == CircuitState.CLOSED
            and self._failure_count >= self.failure_threshold
        ):
            # Too many failures — open the circuit
            self._state = CircuitState.OPEN

    def allow_request(self) -> bool:
        """Check if a request should be allowed through."""
        current_state = self.state  # Triggers timeout check

        if current_state == CircuitState.CLOSED:
            return True
        elif current_state == CircuitState.OPEN:
            return False
        elif current_state == CircuitState.HALF_OPEN:
            if self._half_open_calls < self.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False
        return False

    def get_stats(self) -> dict:
        """Return circuit breaker statistics for monitoring."""
        return {
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "total_calls": self._total_calls,
            "failure_rate": (
                self._failure_count / self._total_calls
                if self._total_calls > 0
                else 0.0
            ),
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejecting requests."""
    pass


class ResilientLLMClient:
    """
    LLM client with per-provider circuit breakers.

    When a provider fails repeatedly, its circuit opens and
    requests automatically route to healthy providers.
    """

    def __init__(self):
        self._providers: dict[str, LLMProvider] = {}
        self._breakers: dict[str, CircuitBreaker] = {}

    def register(
        self,
        name: str,
        provider: LLMProvider,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ) -> None:
        self._providers[name] = provider
        self._breakers[name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )

    async def complete(
        self,
        request: LLMRequest,
        preferred_provider: Optional[str] = None,
    ) -> LLMResponse:
        """
        Complete a request, routing around failed providers.
        """
        # Build ordered list of providers to try
        providers = []
        if preferred_provider and preferred_provider in self._providers:
            providers.append(preferred_provider)
        providers.extend(
            name for name in self._providers if name not in providers
        )

        errors = []
        for name in providers:
            breaker = self._breakers[name]

            if not breaker.allow_request():
                errors.append(
                    f"{name}: circuit open (will retry in "
                    f"{breaker.recovery_timeout}s)"
                )
                continue

            try:
                response = await self._providers[name].complete(request)
                breaker.record_success()
                return response
            except Exception as e:
                breaker.record_failure()
                errors.append(f"{name}: {e}")

        raise CircuitBreakerOpenError(
            f"All providers unavailable: {'; '.join(errors)}"
        )

    def health_status(self) -> dict[str, dict]:
        """Return health status of all providers."""
        return {
            name: breaker.get_stats()
            for name, breaker in self._breakers.items()
        }
```

> **Swift Developer Note:** The circuit breaker pattern maps directly to what you might build around `URLSession`. In iOS, you might track consecutive failures to a backend and show a "server unavailable" UI rather than spinning on retries. The `NWPathMonitor` in Network.framework serves a similar purpose for connectivity. In Python, since we are on the server side, the circuit breaker routes traffic to healthy providers automatically.

---

## 5. Middleware and Request Pipeline

Production AI integrations need more than just sending a request and getting a response. You need logging, validation, cost tracking, PII detection, and more. The middleware pattern lets you compose these concerns cleanly.

### 5.1 Middleware Architecture

```python
"""
Middleware pipeline for LLM API calls.

Each middleware is a function that can inspect/modify the request,
call the next middleware in the chain, and inspect/modify the response.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Awaitable, Optional
import asyncio
import time
import logging
import re
import json

logger = logging.getLogger(__name__)


# Type alias for the handler function
Handler = Callable[[LLMRequest], Awaitable[LLMResponse]]


class Middleware(ABC):
    """Base class for middleware components."""

    @abstractmethod
    async def __call__(
        self,
        request: LLMRequest,
        next_handler: Handler,
    ) -> LLMResponse:
        """
        Process the request, optionally modifying it,
        call next_handler to continue the chain,
        and optionally modify the response.
        """
        ...


class MiddlewarePipeline:
    """
    Composes middleware into an ordered processing pipeline.

    Middleware executes in order for requests (top to bottom)
    and in reverse order for responses (bottom to top).

    Request  → [Logging] → [Validation] → [PII] → [API Call]
    Response ← [Logging] ← [Validation] ← [PII] ← [API Call]
    """

    def __init__(self, handler: Handler):
        self._handler = handler
        self._middleware: list[Middleware] = []

    def use(self, middleware: Middleware) -> "MiddlewarePipeline":
        """Add middleware to the pipeline. Returns self for chaining."""
        self._middleware.append(middleware)
        return self

    async def execute(self, request: LLMRequest) -> LLMResponse:
        """Execute the full middleware chain."""
        # Build the chain from inside out
        handler = self._handler
        for mw in reversed(self._middleware):
            handler = self._wrap(mw, handler)
        return await handler(request)

    @staticmethod
    def _wrap(middleware: Middleware, next_handler: Handler) -> Handler:
        async def wrapped(request: LLMRequest) -> LLMResponse:
            return await middleware(request, next_handler)
        return wrapped
```

### 5.2 Logging Middleware

```python
class LoggingMiddleware(Middleware):
    """
    Logs request/response details for debugging and auditing.

    In production, this feeds into your observability stack
    (Datadog, Grafana, CloudWatch).
    """

    def __init__(self, log_level: int = logging.INFO):
        self.log_level = log_level

    async def __call__(
        self,
        request: LLMRequest,
        next_handler: Handler,
    ) -> LLMResponse:
        request_id = request.metadata.get("request_id", "unknown")
        logger.log(
            self.log_level,
            f"[{request_id}] LLM Request: model={request.model}, "
            f"messages={len(request.messages)}, "
            f"max_tokens={request.max_tokens}",
        )

        start = time.monotonic()
        try:
            response = await next_handler(request)
            elapsed = (time.monotonic() - start) * 1000

            logger.log(
                self.log_level,
                f"[{request_id}] LLM Response: "
                f"tokens={response.usage.total_tokens}, "
                f"latency={elapsed:.0f}ms, "
                f"provider={response.provider.value}",
            )
            return response

        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            logger.error(
                f"[{request_id}] LLM Error after {elapsed:.0f}ms: {e}"
            )
            raise
```

### 5.3 Validation Middleware

```python
class ValidationMiddleware(Middleware):
    """
    Validates requests before sending to the API.

    Catches common customer mistakes early, before they hit
    rate limits or incur costs.
    """

    MAX_MESSAGES = 100
    MAX_TOTAL_CHARS = 500_000  # Rough proxy for token limit

    async def __call__(
        self,
        request: LLMRequest,
        next_handler: Handler,
    ) -> LLMResponse:
        errors = self._validate(request)
        if errors:
            raise ValueError(
                f"Request validation failed: {'; '.join(errors)}"
            )
        return await next_handler(request)

    def _validate(self, request: LLMRequest) -> list[str]:
        errors = []

        # Check message list is not empty
        if not request.messages:
            errors.append("Messages list is empty")

        # Check message count
        if len(request.messages) > self.MAX_MESSAGES:
            errors.append(
                f"Too many messages ({len(request.messages)}). "
                f"Max is {self.MAX_MESSAGES}"
            )

        # Check total content size
        total_chars = sum(len(m.content) for m in request.messages)
        if total_chars > self.MAX_TOTAL_CHARS:
            errors.append(
                f"Total content too large ({total_chars} chars). "
                f"Consider chunking or summarizing."
            )

        # Check for empty messages
        for i, msg in enumerate(request.messages):
            if not msg.content.strip():
                errors.append(f"Message {i} has empty content")

        # Check temperature range
        if not 0.0 <= request.temperature <= 2.0:
            errors.append(
                f"Temperature {request.temperature} out of range [0.0, 2.0]"
            )

        # Check max_tokens
        if request.max_tokens <= 0:
            errors.append(f"max_tokens must be positive, got {request.max_tokens}")

        # Check alternating roles (Anthropic requirement)
        for i in range(1, len(request.messages)):
            if request.messages[i].role == request.messages[i - 1].role:
                errors.append(
                    f"Messages {i-1} and {i} have the same role "
                    f"('{request.messages[i].role}'). Some providers require "
                    f"alternating user/assistant messages."
                )

        return errors
```

### 5.4 Token Counting and Cost Tracking

```python
"""
Token counting and cost tracking middleware.

Customers need visibility into their API spend.
This middleware tracks costs per request and provides
aggregated reporting.
"""
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, timezone


@dataclass
class CostRecord:
    timestamp: datetime
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    request_id: str


class CostTracker:
    """Tracks cumulative costs across requests."""

    # Pricing per million tokens (input, output) — as of early 2025
    PRICING: dict[str, tuple[float, float]] = {
        "claude-3-5-sonnet": (3.00, 15.00),
        "claude-3-5-haiku": (0.80, 4.00),
        "claude-3-opus": (15.00, 75.00),
        "claude-sonnet-4": (3.00, 15.00),
        "gpt-4o": (2.50, 10.00),
        "gpt-4o-mini": (0.15, 0.60),
        "gemini-1.5-pro": (3.50, 10.50),
        "gemini-1.5-flash": (0.075, 0.30),
    }

    def __init__(self):
        self._records: list[CostRecord] = []
        self._total_cost: float = 0.0
        self._cost_by_model: dict[str, float] = defaultdict(float)

    def record(self, response: LLMResponse, request_id: str) -> CostRecord:
        input_price, output_price = self._get_pricing(response.model)

        input_cost = (response.usage.input_tokens / 1_000_000) * input_price
        output_cost = (response.usage.output_tokens / 1_000_000) * output_price
        total_cost = input_cost + output_cost

        record = CostRecord(
            timestamp=datetime.now(timezone.utc),
            model=response.model,
            provider=response.provider.value,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            input_cost_usd=input_cost,
            output_cost_usd=output_cost,
            total_cost_usd=total_cost,
            request_id=request_id,
        )

        self._records.append(record)
        self._total_cost += total_cost
        self._cost_by_model[response.model] += total_cost

        return record

    def _get_pricing(self, model: str) -> tuple[float, float]:
        for key, pricing in self.PRICING.items():
            if key in model.lower():
                return pricing
        return (3.0, 15.0)  # Default pricing

    def get_summary(self) -> dict:
        return {
            "total_cost_usd": round(self._total_cost, 6),
            "total_requests": len(self._records),
            "cost_by_model": dict(self._cost_by_model),
            "avg_cost_per_request": (
                round(self._total_cost / len(self._records), 6)
                if self._records else 0
            ),
        }


class CostTrackingMiddleware(Middleware):
    """Middleware that tracks cost for every API call."""

    def __init__(self, tracker: Optional[CostTracker] = None):
        self.tracker = tracker or CostTracker()

    async def __call__(
        self,
        request: LLMRequest,
        next_handler: Handler,
    ) -> LLMResponse:
        response = await next_handler(request)

        request_id = request.metadata.get("request_id", "unknown")
        record = self.tracker.record(response, request_id)

        logger.info(
            f"Cost: ${record.total_cost_usd:.6f} "
            f"({record.input_tokens} in, {record.output_tokens} out) "
            f"[Total: ${self.tracker._total_cost:.4f}]"
        )

        return response
```

### 5.5 PII Detection Middleware

```python
"""
PII detection middleware — prevents sensitive data from being
sent to LLM providers.

This is a critical compliance requirement for enterprise customers,
especially in healthcare (HIPAA) and finance (PCI-DSS).
"""
import re
from dataclasses import dataclass


@dataclass
class PIIDetectionResult:
    has_pii: bool
    pii_types: list[str]
    locations: list[dict]  # {"type": str, "start": int, "end": int, "sample": str}


class PIIDetector:
    """
    Regex-based PII detector for pre-flight request scanning.

    Note: In production, you would use a more sophisticated approach
    (Presidio, custom NER models, or provider-side PII filtering).
    This is a first line of defense.
    """

    PATTERNS: dict[str, re.Pattern] = {
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "phone_us": re.compile(r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
        "api_key_generic": re.compile(r"\b(?:sk-|api[_-]?key[=:]\s*)[A-Za-z0-9_-]{20,}\b", re.IGNORECASE),
    }

    def scan(self, text: str) -> PIIDetectionResult:
        pii_types = []
        locations = []

        for pii_type, pattern in self.PATTERNS.items():
            for match in pattern.finditer(text):
                pii_types.append(pii_type)
                # Only store a redacted sample for logging
                matched = match.group()
                sample = matched[:4] + "..." + matched[-2:]
                locations.append({
                    "type": pii_type,
                    "start": match.start(),
                    "end": match.end(),
                    "sample": sample,
                })

        return PIIDetectionResult(
            has_pii=len(pii_types) > 0,
            pii_types=list(set(pii_types)),
            locations=locations,
        )

    def redact(self, text: str) -> str:
        """Replace detected PII with redaction markers."""
        for pii_type, pattern in self.PATTERNS.items():
            text = pattern.sub(f"[REDACTED_{pii_type.upper()}]", text)
        return text


class PIIDetectionMiddleware(Middleware):
    """
    Scans outgoing requests for PII and either blocks or redacts.

    mode="block" → Raise an error if PII is detected
    mode="redact" → Automatically redact PII before sending
    mode="warn" → Log a warning but allow the request through
    """

    def __init__(self, mode: str = "warn"):
        assert mode in ("block", "redact", "warn")
        self.mode = mode
        self.detector = PIIDetector()

    async def __call__(
        self,
        request: LLMRequest,
        next_handler: Handler,
    ) -> LLMResponse:
        # Scan all message content
        all_content = " ".join(msg.content for msg in request.messages)
        if request.system_prompt:
            all_content += " " + request.system_prompt

        result = self.detector.scan(all_content)

        if result.has_pii:
            pii_summary = ", ".join(result.pii_types)

            if self.mode == "block":
                raise ValueError(
                    f"PII detected in request: {pii_summary}. "
                    f"Request blocked. Remove sensitive data before sending."
                )

            elif self.mode == "redact":
                logger.warning(f"PII detected ({pii_summary}). Auto-redacting.")
                # Create new request with redacted content
                redacted_messages = [
                    Message(
                        role=msg.role,
                        content=self.detector.redact(msg.content),
                    )
                    for msg in request.messages
                ]
                redacted_system = (
                    self.detector.redact(request.system_prompt)
                    if request.system_prompt
                    else None
                )
                request = LLMRequest(
                    messages=redacted_messages,
                    model=request.model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    system_prompt=redacted_system,
                    stream=request.stream,
                    metadata=request.metadata,
                )

            elif self.mode == "warn":
                logger.warning(
                    f"PII detected in request ({pii_summary}). "
                    f"Proceeding per policy."
                )

        return await next_handler(request)
```

### 5.6 Assembling the Pipeline

```python
"""
Putting it all together: a production-ready middleware pipeline.
"""


async def create_production_pipeline(
    llm_handler: Handler,
    cost_tracker: CostTracker,
) -> MiddlewarePipeline:
    """
    Build a standard production pipeline.

    Order matters:
    1. Logging (outermost — captures everything including errors)
    2. Validation (reject bad requests early)
    3. PII Detection (compliance gate)
    4. Cost Tracking (business metrics)

    The LLM API call is the innermost handler.
    """
    pipeline = MiddlewarePipeline(llm_handler)
    pipeline.use(LoggingMiddleware(log_level=logging.INFO))
    pipeline.use(ValidationMiddleware())
    pipeline.use(PIIDetectionMiddleware(mode="redact"))
    pipeline.use(CostTrackingMiddleware(tracker=cost_tracker))

    return pipeline


# Usage example
async def example_usage():
    """
    Demonstrates how the middleware pipeline is used in practice.
    """
    cost_tracker = CostTracker()

    # The innermost handler calls the actual LLM provider
    async def llm_handler(request: LLMRequest) -> LLMResponse:
        # In production, this calls the UnifiedLLMClient
        return LLMResponse(
            content="Hello! How can I help?",
            model="claude-3-5-sonnet-latest",
            provider=Provider.ANTHROPIC,
            usage=TokenUsage(input_tokens=50, output_tokens=10),
            latency_ms=450.0,
        )

    pipeline = await create_production_pipeline(llm_handler, cost_tracker)

    # Every request goes through the full middleware chain
    request = LLMRequest(
        messages=[Message(role="user", content="Summarize this document.")],
        model="claude-3-5-sonnet-latest",
        metadata={"request_id": "req-abc-123", "customer_id": "cust-456"},
    )

    response = await pipeline.execute(request)
    print(f"Response: {response.content}")
    print(f"Cost so far: {cost_tracker.get_summary()}")
```

> **Swift Developer Note:** This middleware pipeline is conceptually identical to the `URLProtocol` interception pattern in iOS, or Alamofire's `RequestInterceptor` and `EventMonitor` protocols. In Swift, you might write a `RequestAdapter` that adds auth headers, a `RequestRetrier` that handles 401s, and an `EventMonitor` that logs requests. The Python version uses the same chain-of-responsibility pattern, just with `async`/`await` instead of completion handlers.

---

## 6. Customer Onboarding Patterns

Smooth onboarding reduces time-to-first-successful-call and is the strongest predictor of customer retention. As an SE, you will build and maintain onboarding tooling.

### 6.1 API Key Management

```python
"""
Secure API key management patterns for customer onboarding.

The #1 onboarding failure is key misconfiguration.
These utilities make it harder to get wrong.
"""
import os
import hashlib
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class KeySource(Enum):
    ENVIRONMENT = "environment"
    FILE = "file"
    VAULT = "vault"  # HashiCorp Vault, AWS Secrets Manager, etc.
    DIRECT = "direct"


@dataclass
class APIKeyConfig:
    """Validated API key configuration."""
    provider: str
    key_source: KeySource
    key_hash: str  # For logging without exposing the key
    is_valid_format: bool
    warnings: list[str]


class APIKeyManager:
    """
    Manages API keys with validation and security best practices.

    Customers frequently:
    - Hardcode keys in source code
    - Use test keys in production
    - Mix up keys between providers
    - Commit keys to version control
    """

    KEY_FORMATS = {
        "anthropic": {
            "prefix": "sk-ant-",
            "env_var": "ANTHROPIC_API_KEY",
            "min_length": 40,
        },
        "openai": {
            "prefix": "sk-",
            "env_var": "OPENAI_API_KEY",
            "min_length": 40,
        },
        "google": {
            "prefix": "AI",
            "env_var": "GOOGLE_API_KEY",
            "min_length": 30,
        },
    }

    @classmethod
    def load_key(cls, provider: str) -> APIKeyConfig:
        """
        Load and validate an API key for a provider.
        Returns configuration with validation results and warnings.
        """
        format_info = cls.KEY_FORMATS.get(provider, {})
        env_var = format_info.get("env_var", f"{provider.upper()}_API_KEY")

        # Try to load from environment
        key = os.environ.get(env_var)
        key_source = KeySource.ENVIRONMENT

        if not key:
            return APIKeyConfig(
                provider=provider,
                key_source=KeySource.ENVIRONMENT,
                key_hash="",
                is_valid_format=False,
                warnings=[
                    f"API key not found. Set the {env_var} environment variable.",
                    f"Example: export {env_var}='your-key-here'",
                ],
            )

        # Validate format
        warnings = []
        is_valid = True

        expected_prefix = format_info.get("prefix", "")
        if expected_prefix and not key.startswith(expected_prefix):
            warnings.append(
                f"Key does not start with expected prefix '{expected_prefix}'. "
                f"You may be using a key from a different provider."
            )
            is_valid = False

        min_length = format_info.get("min_length", 20)
        if len(key) < min_length:
            warnings.append(
                f"Key seems too short ({len(key)} chars, expected >= {min_length}). "
                f"It may be truncated."
            )
            is_valid = False

        # Security warnings
        if key in ("test", "demo", "placeholder", "your-key-here"):
            warnings.append("Key appears to be a placeholder, not a real key.")
            is_valid = False

        # Hash the key for safe logging
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:12]

        return APIKeyConfig(
            provider=provider,
            key_source=key_source,
            key_hash=key_hash,
            is_valid_format=is_valid,
            warnings=warnings,
        )

    @classmethod
    def validate_all_providers(cls) -> dict[str, APIKeyConfig]:
        """Validate keys for all known providers. Useful in health checks."""
        return {
            provider: cls.load_key(provider)
            for provider in cls.KEY_FORMATS
        }
```

### 6.2 Health Check Implementation

```python
"""
Health check endpoint for LLM integrations.

Every production integration needs a health check that verifies
connectivity, authentication, and basic functionality.
"""
import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ProviderHealth:
    provider: str
    status: HealthStatus
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    last_checked: Optional[str] = None


@dataclass
class SystemHealth:
    overall_status: HealthStatus
    providers: list[ProviderHealth]
    api_keys_valid: dict[str, bool]
    timestamp: str


class HealthChecker:
    """
    Comprehensive health check for LLM integrations.

    Deploy this as a /health endpoint. Monitoring systems
    (Datadog, PagerDuty) poll it to detect outages.
    """

    def __init__(self, providers: dict[str, LLMProvider]):
        self._providers = providers

    async def check_provider(self, name: str, provider: LLMProvider) -> ProviderHealth:
        """
        Send a minimal test request to verify provider connectivity.
        Uses the cheapest possible request (short prompt, low max_tokens).
        """
        start = time.monotonic()
        try:
            test_request = LLMRequest(
                messages=[Message(role="user", content="Hi")],
                model=self._get_cheapest_model(name),
                max_tokens=5,  # Minimize cost
                temperature=0.0,
            )
            await provider.complete(test_request)
            elapsed = (time.monotonic() - start) * 1000

            status = (
                HealthStatus.HEALTHY if elapsed < 5000
                else HealthStatus.DEGRADED
            )

            return ProviderHealth(
                provider=name,
                status=status,
                latency_ms=round(elapsed, 1),
            )

        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return ProviderHealth(
                provider=name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=round(elapsed, 1),
                error=str(e),
            )

    async def full_check(self) -> SystemHealth:
        """Run health checks against all providers concurrently."""
        from datetime import datetime, timezone

        # Check all providers in parallel
        tasks = [
            self.check_provider(name, provider)
            for name, provider in self._providers.items()
        ]
        provider_results = await asyncio.gather(*tasks)

        # Check API key validity
        key_configs = APIKeyManager.validate_all_providers()
        keys_valid = {
            provider: config.is_valid_format
            for provider, config in key_configs.items()
        }

        # Determine overall status
        statuses = [p.status for p in provider_results]
        if all(s == HealthStatus.HEALTHY for s in statuses):
            overall = HealthStatus.HEALTHY
        elif any(s == HealthStatus.HEALTHY for s in statuses):
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.UNHEALTHY

        return SystemHealth(
            overall_status=overall,
            providers=list(provider_results),
            api_keys_valid=keys_valid,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _get_cheapest_model(provider: str) -> str:
        cheapest = {
            "anthropic": "claude-3-5-haiku-latest",
            "openai": "gpt-4o-mini",
            "google": "gemini-1.5-flash",
        }
        return cheapest.get(provider, "claude-3-5-haiku-latest")
```

### 6.3 Usage Monitoring and Alerting

```python
"""
Usage monitoring for customer onboarding.

Track request volume, error rates, and costs to proactively
identify issues before the customer reports them.
"""
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Optional
import statistics


@dataclass
class UsageWindow:
    """Sliding window of usage metrics."""
    window_size_minutes: int = 60
    _requests: deque = field(default_factory=deque)
    _errors: deque = field(default_factory=deque)
    _latencies: deque = field(default_factory=deque)
    _costs: deque = field(default_factory=deque)

    def record_request(
        self,
        success: bool,
        latency_ms: float,
        cost_usd: float,
    ) -> None:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=self.window_size_minutes)

        # Add new data point
        self._requests.append(now)
        self._latencies.append((now, latency_ms))
        self._costs.append((now, cost_usd))
        if not success:
            self._errors.append(now)

        # Prune old data
        while self._requests and self._requests[0] < cutoff:
            self._requests.popleft()
        while self._errors and self._errors[0] < cutoff:
            self._errors.popleft()
        while self._latencies and self._latencies[0][0] < cutoff:
            self._latencies.popleft()
        while self._costs and self._costs[0][0] < cutoff:
            self._costs.popleft()

    @property
    def request_count(self) -> int:
        return len(self._requests)

    @property
    def error_rate(self) -> float:
        if not self._requests:
            return 0.0
        return len(self._errors) / len(self._requests)

    @property
    def avg_latency_ms(self) -> float:
        if not self._latencies:
            return 0.0
        return statistics.mean(lat for _, lat in self._latencies)

    @property
    def p95_latency_ms(self) -> float:
        if len(self._latencies) < 2:
            return self.avg_latency_ms
        latencies = sorted(lat for _, lat in self._latencies)
        idx = int(len(latencies) * 0.95)
        return latencies[min(idx, len(latencies) - 1)]

    @property
    def total_cost_usd(self) -> float:
        return sum(cost for _, cost in self._costs)


@dataclass
class AlertThresholds:
    max_error_rate: float = 0.10          # 10% error rate
    max_p95_latency_ms: float = 10_000.0  # 10 seconds
    max_cost_per_hour_usd: float = 100.0  # $100/hour
    min_requests_for_alert: int = 10       # Minimum requests before alerting


@dataclass
class Alert:
    severity: str  # "warning", "critical"
    metric: str
    message: str
    current_value: float
    threshold: float


class UsageMonitor:
    """
    Monitor customer usage and generate alerts.

    As an SE, you set this up during onboarding so customers
    get proactive notifications instead of surprise outages.
    """

    def __init__(
        self,
        customer_id: str,
        thresholds: Optional[AlertThresholds] = None,
    ):
        self.customer_id = customer_id
        self.thresholds = thresholds or AlertThresholds()
        self.window = UsageWindow()

    def record(
        self, success: bool, latency_ms: float, cost_usd: float
    ) -> list[Alert]:
        """Record a request and return any triggered alerts."""
        self.window.record_request(success, latency_ms, cost_usd)
        return self._check_alerts()

    def _check_alerts(self) -> list[Alert]:
        alerts = []
        t = self.thresholds

        if self.window.request_count < t.min_requests_for_alert:
            return alerts

        # Error rate alert
        if self.window.error_rate > t.max_error_rate:
            severity = (
                "critical" if self.window.error_rate > t.max_error_rate * 2
                else "warning"
            )
            alerts.append(Alert(
                severity=severity,
                metric="error_rate",
                message=(
                    f"Customer {self.customer_id}: error rate "
                    f"{self.window.error_rate:.1%} exceeds threshold "
                    f"{t.max_error_rate:.1%}"
                ),
                current_value=self.window.error_rate,
                threshold=t.max_error_rate,
            ))

        # Latency alert
        p95 = self.window.p95_latency_ms
        if p95 > t.max_p95_latency_ms:
            alerts.append(Alert(
                severity="warning",
                metric="p95_latency",
                message=(
                    f"Customer {self.customer_id}: P95 latency "
                    f"{p95:.0f}ms exceeds threshold {t.max_p95_latency_ms:.0f}ms"
                ),
                current_value=p95,
                threshold=t.max_p95_latency_ms,
            ))

        # Cost alert
        cost = self.window.total_cost_usd
        if cost > t.max_cost_per_hour_usd:
            alerts.append(Alert(
                severity="critical",
                metric="hourly_cost",
                message=(
                    f"Customer {self.customer_id}: hourly cost "
                    f"${cost:.2f} exceeds threshold ${t.max_cost_per_hour_usd:.2f}"
                ),
                current_value=cost,
                threshold=t.max_cost_per_hour_usd,
            ))

        return alerts

    def get_dashboard_data(self) -> dict:
        """Data for a customer usage dashboard."""
        return {
            "customer_id": self.customer_id,
            "window_minutes": self.window.window_size_minutes,
            "request_count": self.window.request_count,
            "error_rate": round(self.window.error_rate, 4),
            "avg_latency_ms": round(self.window.avg_latency_ms, 1),
            "p95_latency_ms": round(self.window.p95_latency_ms, 1),
            "total_cost_usd": round(self.window.total_cost_usd, 4),
        }
```

### 6.4 Customer Onboarding Checklist (Programmatic)

```python
"""
Automated onboarding validation.

Run this as a script or integrate into a CLI tool that
customers execute to verify their setup is correct.
"""
from dataclasses import dataclass
from typing import Optional
import asyncio


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    fix_suggestion: Optional[str] = None


async def run_onboarding_checks(
    provider: str = "anthropic",
) -> list[CheckResult]:
    """
    Run a comprehensive set of onboarding checks.

    Customers run this to verify their integration is set up correctly
    before going to production.
    """
    results = []

    # 1. Check API key
    key_config = APIKeyManager.load_key(provider)
    results.append(CheckResult(
        name="API Key Format",
        passed=key_config.is_valid_format,
        message=(
            f"Key loaded from {key_config.key_source.value} "
            f"(hash: {key_config.key_hash})"
            if key_config.is_valid_format
            else f"Invalid key: {'; '.join(key_config.warnings)}"
        ),
        fix_suggestion=(
            None if key_config.is_valid_format
            else key_config.warnings[0] if key_config.warnings else None
        ),
    ))

    # 2. Check Python version
    import sys
    py_version = sys.version_info
    is_modern_python = py_version >= (3, 10)
    results.append(CheckResult(
        name="Python Version",
        passed=is_modern_python,
        message=f"Python {py_version.major}.{py_version.minor}.{py_version.micro}",
        fix_suggestion=(
            None if is_modern_python
            else "Python 3.10+ is recommended for modern type hints and performance."
        ),
    ))

    # 3. Check required packages
    required_packages = {
        "anthropic": "anthropic",
        "openai": "openai",
        "google": "google-generativeai",
    }
    pkg = required_packages.get(provider, provider)
    try:
        __import__(pkg.replace("-", "_"))
        results.append(CheckResult(
            name=f"SDK Package ({pkg})",
            passed=True,
            message=f"{pkg} is installed",
        ))
    except ImportError:
        results.append(CheckResult(
            name=f"SDK Package ({pkg})",
            passed=False,
            message=f"{pkg} is not installed",
            fix_suggestion=f"pip install {pkg}",
        ))

    # 4. Check network connectivity (basic)
    import socket
    hosts = {
        "anthropic": "api.anthropic.com",
        "openai": "api.openai.com",
        "google": "generativelanguage.googleapis.com",
    }
    host = hosts.get(provider, "api.anthropic.com")
    try:
        socket.create_connection((host, 443), timeout=5)
        results.append(CheckResult(
            name="Network Connectivity",
            passed=True,
            message=f"Can reach {host}:443",
        ))
    except (socket.timeout, socket.error) as e:
        results.append(CheckResult(
            name="Network Connectivity",
            passed=False,
            message=f"Cannot reach {host}: {e}",
            fix_suggestion="Check firewall rules and proxy settings.",
        ))

    return results


def print_onboarding_report(results: list[CheckResult]) -> None:
    """Pretty-print the onboarding check results."""
    print("\n" + "=" * 60)
    print("  LLM Integration Onboarding Check")
    print("=" * 60 + "\n")

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        icon = "[+]" if r.passed else "[-]"
        print(f"  {icon} {r.name}: {status}")
        print(f"      {r.message}")
        if r.fix_suggestion:
            print(f"      Fix: {r.fix_suggestion}")
        print()

    print(f"  Results: {passed}/{total} checks passed")
    if passed == total:
        print("  Status: Ready for integration!\n")
    else:
        print("  Status: Please fix the issues above before proceeding.\n")
```

---

## 7. Swift Comparison Sidebar

This section maps the Python patterns you have learned to their Swift/iOS equivalents. The goal is not to write Swift code in this course, but to leverage your existing mental models.

### Retry Patterns

| Python (tenacity) | Swift Equivalent |
|-------------------|------------------|
| `@retry(wait=wait_exponential(...))` | `Combine: .retry(3).delay(for: ...)` |
| `stop_after_attempt(5)` | Manual counter in `URLSessionDelegate` |
| `retry_if_exception_type(TransientError)` | Check `URLError.code` in retry logic |
| `wait_random_exponential(max=60)` | `DispatchQueue.asyncAfter` with jitter |

```python
# Python: tenacity retry
@retry(
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(TransientAPIError),
)
async def call_api(request):
    return await client.complete(request)
```

The Swift equivalent using Combine would be:

```swift
// Swift equivalent (for reference — not part of this course)
func callAPI(request: APIRequest) -> AnyPublisher<APIResponse, Error> {
    URLSession.shared.dataTaskPublisher(for: request.urlRequest)
        .retry(3)
        .delay(for: .seconds(1), scheduler: DispatchQueue.main)
        .tryMap { data, response in
            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                throw APIError.serverError
            }
            return try JSONDecoder().decode(APIResponse.self, from: data)
        }
        .eraseToAnyPublisher()
}
```

### Middleware Patterns

| Python Middleware | Swift/iOS Equivalent |
|-------------------|----------------------|
| `MiddlewarePipeline` | `URLProtocol` subclass chain |
| `LoggingMiddleware` | Alamofire `EventMonitor` |
| `ValidationMiddleware` | Alamofire `RequestInterceptor.adapt()` |
| `PIIDetectionMiddleware` | Custom `URLProtocol` that inspects request body |
| `CostTrackingMiddleware` | `URLSessionTaskDelegate` metrics |

```python
# Python: Middleware pipeline
pipeline = MiddlewarePipeline(handler)
pipeline.use(LoggingMiddleware())
pipeline.use(ValidationMiddleware())
pipeline.use(PIIDetectionMiddleware(mode="redact"))
```

In iOS, the closest analog is Alamofire's interceptor and event monitor system:

```swift
// Swift equivalent (for reference)
let session = Session(
    interceptor: CompositeInterceptor([
        AuthInterceptor(),
        ValidationInterceptor(),
        LoggingInterceptor()
    ]),
    eventMonitors: [
        CostTrackingMonitor(),
        PerformanceMonitor()
    ]
)
```

### Circuit Breaker

There is no standard circuit breaker library in the iOS ecosystem because client apps typically talk to *one* backend, and connectivity is handled by `NWPathMonitor`. On the server side (Python), circuit breakers are essential because you are orchestrating calls to multiple external services that can independently fail.

The closest Swift pattern is checking `NWPath.status` before making a request:

```swift
// Swift: Simple connectivity gate (not a full circuit breaker)
let monitor = NWPathMonitor()
monitor.pathUpdateHandler = { path in
    if path.status == .satisfied {
        // Circuit "closed" — proceed with request
    } else {
        // Circuit "open" — skip request, use cached data
    }
}
```

> **Swift Developer Note:** The key insight is that server-side Python needs these patterns because it manages connections to *multiple* external services (Anthropic, OpenAI, databases, caches). An iOS app typically talks to one or two backends. But if you have ever built an app that aggregates data from multiple APIs (like a travel app hitting flight, hotel, and car rental APIs), you have encountered the same need for fallbacks and circuit breakers. The Python patterns are more mature because the server-side ecosystem has been dealing with this for decades.

---

## 8. Interview Focus

### What Interviewers Are Looking For

Solutions Engineer and Applied AI Engineer interviews test a specific blend of skills. Here is what matters most for the integration patterns covered in this module:

**Technical depth:**
- Can you explain *why* you would use exponential backoff instead of fixed delays?
- Do you understand the difference between transient and permanent errors?
- Can you design a multi-provider abstraction from scratch on a whiteboard?

**Customer empathy:**
- When a customer reports "the API is slow," how do you diagnose the root cause?
- How do you explain rate limiting to a non-technical stakeholder?
- What would you include in an onboarding guide?

**System design:**
- How would you build a cost monitoring dashboard for enterprise customers?
- Design a middleware pipeline for a multi-tenant LLM proxy.
- What trade-offs exist between building your own abstraction layer vs. using LiteLLM?

### Common Interview Questions

**Q1: "A customer says your API is returning 500 errors intermittently. Walk me through how you would debug this."**

Strong answer structure:
1. Gather information: frequency, timing, specific endpoints, request patterns
2. Check provider status page for known incidents
3. Ask for request IDs to trace in server logs
4. Look at the customer's retry logic -- are they amplifying the problem?
5. Check if the errors correlate with load (rate limiting presenting as 500s)
6. Reproduce with a minimal request to isolate the issue
7. If provider-side: escalate with evidence. If customer-side: provide specific fix.

**Q2: "How would you design a system that uses multiple LLM providers for redundancy?"**

Strong answer covers:
- Unified request/response interface (as shown in Section 3)
- Model mapping across providers (Sonnet <-> GPT-4o <-> Gemini Pro)
- Per-provider circuit breakers with automatic failover
- Cost tracking to understand the financial impact of fallbacks
- Latency monitoring to detect degradation before total failure
- Customer-configurable preferences (some customers cannot use certain providers for compliance reasons)

**Q3: "A customer is spending 10x more than expected on API calls. How do you help them?"**

Walk through this systematically:
1. Pull their usage data: which models, how many tokens, how many requests
2. Check for the "over-powered model" antipattern (using Opus for simple tasks)
3. Look for inefficient prompting (huge system prompts repeated every request)
4. Check for retry storms (failed requests being retried aggressively)
5. Evaluate whether caching could help (semantic cache for repeated queries)
6. Recommend model routing: use Haiku for classification, Sonnet for generation
7. Quantify the savings of each optimization

**Q4: "How do you handle PII in LLM API requests?"**

Address multiple layers:
- Client-side detection and redaction (as shown in Section 5.5)
- Provider-side data handling policies (zero retention options)
- Architectural alternatives (on-premise models for sensitive data)
- Compliance frameworks (HIPAA, GDPR, SOC 2) and how they affect integration patterns
- The limitations of regex-based detection and when to use ML-based NER

**Q5: "Tell me about a time you helped a customer solve a difficult integration problem."**

For this behavioral question, structure your answer using the STAR framework (Situation, Task, Action, Result). Even if your experience is from iOS development, the problem-solving pattern is the same:
- Situation: Customer had a complex requirement
- Task: You needed to diagnose the issue and provide a working solution
- Action: Describe your systematic debugging approach
- Result: Quantify the impact (time saved, reliability improved, cost reduced)

### Key Concepts to Memorize

1. **Exponential backoff formula**: `delay = min(base * 2^attempt + random_jitter, max_delay)`
2. **Circuit breaker states**: Closed (normal) -> Open (failing) -> Half-Open (testing)
3. **HTTP status code classification**: 4xx = client error (usually permanent), 5xx = server error (usually transient), 429 = rate limit (transient with specific backoff)
4. **Middleware ordering matters**: Logging first (outermost), then validation, then business logic, then the actual API call (innermost)
5. **Cost estimation**: `(tokens / 1,000,000) * price_per_million_tokens` -- always estimate before deploying

### What Sets Great Candidates Apart

The best candidates in SE interviews do not just describe the patterns -- they explain the *trade-offs*:

- "I would use LiteLLM for a POC because it saves days of integration work, but for production I would build a custom abstraction because we need fine-grained control over retry behavior and provider-specific optimizations."
- "Regex-based PII detection catches common formats but misses names, addresses, and contextual PII. For a healthcare customer, I would layer in Microsoft Presidio or a dedicated NER model."
- "Circuit breakers protect against cascading failures, but they add complexity. For a single-provider integration, simple retry logic is usually sufficient. The circuit breaker becomes essential when you have fallback providers to route to."

---

## Summary

This module covered the core patterns that Applied AI Engineers use daily:

| Pattern | Purpose | Key Library |
|---------|---------|-------------|
| Auth diagnosis | Rapid triage of key issues | Custom tooling |
| Rate limit handling | Adaptive throttling | tenacity, custom |
| Multi-provider abstraction | Redundancy and flexibility | litellm, custom |
| Retry with backoff | Transient failure recovery | tenacity |
| Circuit breaker | Cascading failure prevention | Custom (or pybreaker) |
| Middleware pipeline | Request/response processing | Custom |
| PII detection | Compliance gate | regex, Presidio |
| Health checks | Proactive monitoring | Custom |
| Usage monitoring | Cost and performance tracking | Custom |

**Next module**: We will cover Cost and Performance Optimization -- how to reduce API spend by 5-10x through caching, model routing, prompt optimization, and batch processing strategies.

---

## Practice Exercises

1. **Build a diagnostic CLI**: Create a command-line tool that takes a provider name, API key, and model, then runs the onboarding checks and prints a formatted report.

2. **Extend the middleware pipeline**: Add a `CachingMiddleware` that stores responses keyed by a hash of the request messages. Use an LRU cache with a configurable TTL.

3. **Implement a token budget middleware**: Write middleware that tracks cumulative token usage across requests and rejects new requests when a daily budget is exceeded.

4. **Multi-provider load test**: Write a script that sends 100 concurrent requests to the `UnifiedLLMClient` with artificial failures injected into one provider. Verify that the circuit breaker opens and traffic routes to the healthy provider.

5. **PII detection edge cases**: Extend the `PIIDetector` to handle international phone numbers, UK National Insurance numbers, and Canadian Social Insurance Numbers. Write tests for each pattern.
