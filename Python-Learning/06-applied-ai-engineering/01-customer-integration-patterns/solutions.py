"""
Module 01: Customer Integration Patterns - Solutions
======================================================
Phase 6: Applied AI Engineering

Complete solutions for all 15 exercises on customer integration patterns.
Each solution includes detailed comments explaining the approach.

Run this file to verify all solutions:
    python solutions.py
"""

from __future__ import annotations

import re
import time
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol


# =============================================================================
# SECTION 1: Unified LLM Client Interface
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 1: Build a Unified LLM Client Interface
# ---------------------------------------------------------------------------

class LLMMessage:
    """A single message in a conversation."""

    VALID_ROLES = {"system", "user", "assistant"}

    def __init__(self, role: str, content: str) -> None:
        # Validate role against the known set -- similar to a Swift enum
        # with a failable initializer.
        if role not in self.VALID_ROLES:
            raise ValueError(
                f"Invalid role '{role}'. Must be one of: {sorted(self.VALID_ROLES)}"
            )
        self.role = role
        self.content = content

    def to_dict(self) -> dict[str, str]:
        """Convert to the dict format expected by LLM APIs."""
        return {"role": self.role, "content": self.content}

    def __repr__(self) -> str:
        return f"LLMMessage(role='{self.role}', content='{self.content[:40]}...')"


@dataclass
class LLMConfig:
    """Configuration for an LLM completion request."""
    model: str = "claude-3-5-sonnet"
    temperature: float = 0.7
    max_tokens: int = 1024


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    provider: str
    raw_response: dict[str, Any] = field(default_factory=dict)


class BaseLLMClient(ABC):
    """Abstract base class for LLM provider clients.

    In Swift, this would be a protocol:
        protocol LLMClient {
            var providerName: String { get }
            func complete(messages: [LLMMessage], config: LLMConfig?) -> LLMResponse
        }
    Python uses ABC (Abstract Base Class) instead.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @abstractmethod
    def complete(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> LLMResponse:
        ...


# ---------------------------------------------------------------------------
# Exercise 2: Implement Anthropic-Specific Client
# ---------------------------------------------------------------------------

class AnthropicClient(BaseLLMClient):
    """Mock Anthropic API client.

    In a real implementation, this would wrap the `anthropic` Python SDK.
    Here we simulate the response format so exercises work without API keys.
    """

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def complete(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> LLMResponse:
        # Use provided config or sensible defaults
        cfg = config or LLMConfig(model="claude-3-5-sonnet")

        # Find the last user message for our mock response
        last_user_content = ""
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_content = msg.content
                break

        # Estimate tokens: roughly 1 token per 4 characters
        input_tokens = sum(max(1, len(m.content) // 4) for m in messages)
        output_tokens = 50  # Fixed mock value

        # Build the generated response text
        generated_text = (
            f"[Anthropic/{cfg.model}] Mock response to: {last_user_content}"
        )

        # Build the raw response in Anthropic's actual API format
        # This mirrors what you'd get from anthropic.Anthropic().messages.create()
        raw_response = {
            "id": "msg_mock_001",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": generated_text}],
            "model": cfg.model,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        }

        # Return our standardized LLMResponse -- the whole point of the
        # abstraction layer is that callers don't need to know about
        # Anthropic-specific response structure.
        return LLMResponse(
            content=generated_text,
            model=cfg.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider="anthropic",
            raw_response=raw_response,
        )


# ---------------------------------------------------------------------------
# Exercise 3: Implement OpenAI-Specific Client
# ---------------------------------------------------------------------------

class OpenAIClient(BaseLLMClient):
    """Mock OpenAI API client.

    Same interface as AnthropicClient, but simulates OpenAI's different
    response format. This demonstrates why the abstraction layer matters:
    both providers return LLMResponse, hiding their format differences.
    """

    @property
    def provider_name(self) -> str:
        return "openai"

    def complete(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> LLMResponse:
        cfg = config or LLMConfig(model="gpt-4o")

        # Find the last user message
        last_user_content = ""
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_content = msg.content
                break

        # Token estimation
        prompt_tokens = sum(max(1, len(m.content) // 4) for m in messages)
        completion_tokens = 50

        generated_text = (
            f"[OpenAI/{cfg.model}] Mock response to: {last_user_content}"
        )

        # OpenAI's response format is notably different from Anthropic's:
        # - Uses "choices" array instead of "content" array
        # - Nests content under choices[0].message.content
        # - Uses "prompt_tokens" / "completion_tokens" naming
        raw_response = {
            "id": "chatcmpl-mock001",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": generated_text,
                    },
                    "finish_reason": "stop",
                }
            ],
            "model": cfg.model,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }

        # Map OpenAI's naming to our standard naming
        return LLMResponse(
            content=generated_text,
            model=cfg.model,
            input_tokens=prompt_tokens,       # prompt_tokens -> input_tokens
            output_tokens=completion_tokens,  # completion_tokens -> output_tokens
            provider="openai",
            raw_response=raw_response,
        )


# ---------------------------------------------------------------------------
# Exercise 4: Build a Provider Factory / Registry
# ---------------------------------------------------------------------------

class ProviderRegistry:
    """Registry that maps provider names to client classes.

    This pattern is extremely common in enterprise integrations. In Swift
    you might use a dictionary of metatypes: [String: LLMClient.Type].
    In Python, classes are first-class objects, so we just store them directly.
    """

    def __init__(self) -> None:
        # Private dict mapping provider name -> client class (not instances)
        self._registry: dict[str, type[BaseLLMClient]] = {}

    def register(self, name: str, client_class: type[BaseLLMClient]) -> None:
        """Register a provider by name. Overwrites existing registrations."""
        self._registry[name] = client_class

    def create(self, name: str, **kwargs: Any) -> BaseLLMClient:
        """Instantiate a registered provider by name.

        Raises KeyError with a helpful message listing available providers
        if the requested name is not registered.
        """
        if name not in self._registry:
            available = ", ".join(sorted(self._registry.keys()))
            raise KeyError(
                f"Unknown provider '{name}'. Available: {available}"
            )
        # Instantiate the class, passing any extra kwargs to __init__
        return self._registry[name](**kwargs)

    def list_providers(self) -> list[str]:
        """Return a sorted list of registered provider names."""
        return sorted(self._registry.keys())


# =============================================================================
# SECTION 2: Resilience Patterns
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 5: Exponential Backoff Retry Decorator
# ---------------------------------------------------------------------------

class TransientError(Exception):
    """Simulates a transient API error (e.g., 529 overloaded)."""
    pass


class PermanentError(Exception):
    """Simulates a permanent API error (e.g., 401 unauthorized)."""
    pass


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple[str, ...] = ("TransientError",),
    sleep_func: Callable[[float], None] = time.sleep,
) -> Callable:
    """Decorator factory implementing exponential backoff retry.

    Key design decisions:
    - We match exception class NAMES (strings) rather than types so the
      decorator works across module boundaries and with dynamically defined
      exception classes.
    - sleep_func is injectable for testing -- this is a common pattern in
      Python for making time-dependent code testable. In Swift you might
      use a Clock protocol.
    - max_retries=3 means up to 4 total attempts (1 initial + 3 retries).
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    # Check if this exception type is retryable by name
                    exc_name = type(e).__name__
                    if exc_name not in retryable_exceptions:
                        # Not retryable -- propagate immediately
                        raise

                    if attempt < max_retries:
                        # Calculate exponential backoff delay:
                        # attempt 0 -> base_delay * 1
                        # attempt 1 -> base_delay * backoff_factor
                        # attempt 2 -> base_delay * backoff_factor^2
                        delay = base_delay * (backoff_factor ** attempt)
                        sleep_func(delay)
                    # else: last attempt, will fall through to raise

            # All retries exhausted -- raise the last exception
            raise last_exception  # type: ignore[misc]

        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Exercise 6: Circuit Breaker Pattern
# ---------------------------------------------------------------------------

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker pattern for API calls.

    This is a critical resilience pattern for production integrations.
    Without it, a downed provider causes cascading failures as your
    application piles up connections and threads waiting for timeouts.

    State machine:
        CLOSED --[failure_threshold reached]--> OPEN
        OPEN   --[recovery_timeout elapsed]---> HALF_OPEN
        HALF_OPEN --[success]-----------------> CLOSED
        HALF_OPEN --[failure]-----------------> OPEN
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        time_func: Callable[[], float] = time.time,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._time_func = time_func

        # Start in CLOSED (normal operation) state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: float = 0.0

    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute func through the circuit breaker."""
        now = self._time_func()

        # OPEN state: check if we should transition to HALF_OPEN
        if self.state == CircuitState.OPEN:
            elapsed = now - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                # Enough time has passed -- allow one test request
                self.state = CircuitState.HALF_OPEN
            else:
                raise RuntimeError("Circuit breaker is OPEN")

        # CLOSED or HALF_OPEN: attempt the call
        try:
            result = func(*args, **kwargs)
            # Success! Reset to healthy state.
            self.failure_count = 0
            self.state = CircuitState.CLOSED
            return result
        except Exception as e:
            # Record the failure
            self.failure_count += 1
            self.last_failure_time = self._time_func()

            # Check if we've hit the threshold
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            # Always re-raise -- the circuit breaker doesn't swallow errors
            raise

    def reset(self) -> None:
        """Manually reset the circuit breaker to initial state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0


# =============================================================================
# SECTION 3: Middleware Pipeline
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 7: Request Validation Middleware
# ---------------------------------------------------------------------------

def validate_request(
    messages: list[dict[str, str]],
    config: dict[str, Any],
) -> list[str]:
    """Validate an LLM request and return a list of error strings.

    This is the kind of pre-flight validation you'd build for customers
    to catch common mistakes before they hit the API and get cryptic errors.
    """
    errors: list[str] = []

    # Rule 1: messages must not be empty
    if not messages:
        errors.append("messages list is empty")
        return errors  # No point checking individual messages

    # Rules 2-4: validate each message
    valid_roles = {"system", "user", "assistant"}
    for i, msg in enumerate(messages):
        # Rule 2: required keys
        for key in ("role", "content"):
            if key not in msg:
                errors.append(f"message at index {i} missing key: {key}")

        # Rule 3: valid role (only check if role key exists)
        if "role" in msg and msg["role"] not in valid_roles:
            errors.append(f"message at index {i} has invalid role: {msg['role']}")

        # Rule 4: non-empty content (only check if content key exists)
        if "content" in msg and msg["content"] == "":
            errors.append(f"message at index {i} has empty content")

    # Rule 5: temperature range
    if "temperature" in config:
        temp = config["temperature"]
        if not (0.0 <= temp <= 2.0):
            errors.append("temperature must be between 0.0 and 2.0")

    # Rule 6: max_tokens range
    if "max_tokens" in config:
        mt = config["max_tokens"]
        if not (1 <= mt <= 100000):
            errors.append("max_tokens must be between 1 and 100000")

    return errors


# ---------------------------------------------------------------------------
# Exercise 8: Token Counting Middleware
# ---------------------------------------------------------------------------

@dataclass
class TokenEstimate:
    """Estimated token counts for a request."""
    input_tokens: int
    estimated_output_tokens: int
    total_tokens: int
    estimated_cost_usd: float


# Shared pricing table used by Exercises 8 and 9
# Prices are per 1 million tokens in USD
PRICING_TABLE: dict[str, dict[str, float]] = {
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}
DEFAULT_PRICING: dict[str, float] = {"input": 10.00, "output": 30.00}


def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Helper to calculate cost using the pricing table."""
    pricing = PRICING_TABLE.get(model, DEFAULT_PRICING)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def estimate_request_tokens(
    messages: list[dict[str, str]],
    model: str = "claude-3-5-sonnet",
    max_tokens: int = 1024,
) -> TokenEstimate:
    """Estimate token usage and cost for a request before sending it.

    The 4-characters-per-token heuristic is a widely used approximation.
    Real tokenizers (tiktoken for OpenAI, Anthropic's tokenizer) are more
    accurate but require additional dependencies.
    """
    # Estimate input tokens: content tokens + per-message overhead
    input_tokens = 0
    for msg in messages:
        content = msg.get("content", "")
        # ~4 chars per token for the content
        content_tokens = len(content) // 4
        # Add 4 tokens overhead per message for role formatting / delimiters
        input_tokens += content_tokens + 4

    # Ensure at least 1 token
    input_tokens = max(1, input_tokens)

    # Output estimation uses max_tokens as the upper bound
    estimated_output_tokens = max_tokens
    total_tokens = input_tokens + estimated_output_tokens

    # Calculate cost
    cost = _calculate_cost(model, input_tokens, estimated_output_tokens)

    return TokenEstimate(
        input_tokens=input_tokens,
        estimated_output_tokens=estimated_output_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=cost,
    )


# ---------------------------------------------------------------------------
# Exercise 9: Cost Tracking Middleware
# ---------------------------------------------------------------------------

@dataclass
class UsageRecord:
    """A single API usage record."""
    team: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float


class CostTracker:
    """Tracks API costs across teams with budget enforcement.

    This is a critical feature for enterprise customers. Without cost
    tracking, teams can accidentally run up massive bills with tight
    loops or inefficient prompts.
    """

    def __init__(self, budgets: dict[str, float] | None = None) -> None:
        self._budgets: dict[str, float] = budgets or {}
        self._records: list[UsageRecord] = []

    def record_usage(
        self,
        team: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        timestamp: float | None = None,
    ) -> UsageRecord:
        """Record a usage event and return the UsageRecord."""
        cost = _calculate_cost(model, input_tokens, output_tokens)
        record = UsageRecord(
            team=team,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            timestamp=timestamp if timestamp is not None else time.time(),
        )
        self._records.append(record)
        return record

    def get_team_spend(self, team: str) -> float:
        """Return total spend for a team across all records."""
        return sum(r.cost_usd for r in self._records if r.team == team)

    def check_budget(self, team: str) -> dict[str, Any]:
        """Check a team's budget status."""
        budget = self._budgets.get(team, float("inf"))
        spent = self.get_team_spend(team)
        return {
            "team": team,
            "budget": budget,
            "spent": spent,
            "remaining": budget - spent,
            "over_budget": spent > budget,
        }

    def get_top_teams(self, n: int = 5) -> list[tuple[str, float]]:
        """Return the top N teams by spend, sorted descending."""
        # Aggregate spend per team
        team_spend: dict[str, float] = {}
        for record in self._records:
            team_spend[record.team] = (
                team_spend.get(record.team, 0.0) + record.cost_usd
            )
        # Sort descending by spend and return top N
        sorted_teams = sorted(
            team_spend.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_teams[:n]


# ---------------------------------------------------------------------------
# Exercise 10: PII Detection Middleware
# ---------------------------------------------------------------------------

@dataclass
class PIIMatch:
    """A detected PII occurrence."""
    pii_type: str
    value: str
    start: int
    end: int


def detect_pii(text: str) -> list[PIIMatch]:
    """Scan text for common PII patterns using regex.

    IMPORTANT: This is a basic regex approach suitable for a first line of
    defense. Production systems should use NER models (like spaCy, Presidio,
    or cloud-based PII detection services) for higher accuracy.

    The patterns are ordered so that more specific patterns (SSN, credit card)
    are checked alongside more general ones (email, phone).
    """
    # Define our PII patterns. Each tuple is (pii_type, compiled_regex).
    patterns: list[tuple[str, re.Pattern[str]]] = [
        ("email", re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')),
        ("phone", re.compile(r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')),
        ("ssn", re.compile(r'\b\d{3}-\d{2}-\d{4}\b')),
        ("credit_card", re.compile(r'\b(?:\d[- ]?){13,19}\b')),
    ]

    matches: list[PIIMatch] = []
    for pii_type, pattern in patterns:
        for match in pattern.finditer(text):
            matches.append(PIIMatch(
                pii_type=pii_type,
                value=match.group(),
                start=match.start(),
                end=match.end(),
            ))

    # Sort by start position for consistent ordering
    matches.sort(key=lambda m: m.start)
    return matches


def redact_pii(text: str, matches: list[PIIMatch]) -> str:
    """Replace detected PII with redaction markers.

    We process matches in REVERSE order so that replacing text doesn't
    shift the indices of earlier matches. This is a classic string
    manipulation technique -- similar to how you'd process ranges in
    reverse when editing an NSAttributedString in Swift.
    """
    result = text
    # Process in reverse order by start position
    for match in sorted(matches, key=lambda m: m.start, reverse=True):
        redaction = f"[REDACTED_{match.pii_type.upper()}]"
        result = result[:match.start] + redaction + result[match.end:]
    return result


# ---------------------------------------------------------------------------
# Exercise 11: Middleware Chain / Pipeline
# ---------------------------------------------------------------------------

@dataclass
class PipelineContext:
    """Context object passed through the middleware pipeline."""
    messages: list[dict[str, str]]
    config: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    blocked: bool = False


MiddlewareFunc = Callable[[PipelineContext], PipelineContext]


class MiddlewarePipeline:
    """A composable pipeline of middleware functions.

    This is the Chain of Responsibility pattern. Each middleware receives
    the context, can modify it, and passes it along. If any middleware
    sets blocked=True, the pipeline short-circuits.

    In Swift/Vapor, middleware works similarly:
        app.middleware.use(LoggingMiddleware())
        app.middleware.use(AuthMiddleware())
        app.middleware.use(CORSMiddleware())

    The key insight is that middleware should be independently composable --
    each middleware function should work regardless of what other middleware
    is in the pipeline.
    """

    def __init__(self) -> None:
        self._middleware: list[MiddlewareFunc] = []

    def add(self, middleware: MiddlewareFunc) -> "MiddlewarePipeline":
        """Add a middleware function. Returns self for method chaining."""
        self._middleware.append(middleware)
        return self

    def process(self, context: PipelineContext) -> PipelineContext:
        """Run context through each middleware in order.

        If any middleware sets context.blocked = True, stop immediately
        and return the context as-is. This allows validation middleware
        to prevent requests from proceeding.
        """
        for mw in self._middleware:
            context = mw(context)
            if context.blocked:
                break
        return context

    def __len__(self) -> int:
        return len(self._middleware)


# =============================================================================
# SECTION 4: Operational Tooling
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 12: API Health Checker
# ---------------------------------------------------------------------------

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass
class HealthCheckResult:
    """Result of a health check for one provider."""
    provider: str
    status: HealthStatus
    latency_ms: float
    message: str


def check_provider_health(
    provider: str,
    ping_func: Callable[[str], tuple[bool, float]],
    latency_threshold_ms: float = 2000.0,
) -> HealthCheckResult:
    """Check health of an LLM provider.

    The ping_func abstraction lets us test without real network calls.
    In production, the ping function would make a lightweight API call
    (e.g., a models/list endpoint) and measure response time.
    """
    try:
        success, latency_ms = ping_func(provider)

        if not success:
            return HealthCheckResult(
                provider=provider,
                status=HealthStatus.DOWN,
                latency_ms=0.0,
                message=f"{provider} ping failed",
            )

        if latency_ms >= latency_threshold_ms:
            return HealthCheckResult(
                provider=provider,
                status=HealthStatus.DEGRADED,
                latency_ms=latency_ms,
                message=f"{provider} responding slowly ({latency_ms:.0f}ms)",
            )

        return HealthCheckResult(
            provider=provider,
            status=HealthStatus.HEALTHY,
            latency_ms=latency_ms,
            message=f"{provider} is healthy ({latency_ms:.0f}ms)",
        )

    except Exception as e:
        # If the ping function itself raises, the provider is down
        return HealthCheckResult(
            provider=provider,
            status=HealthStatus.DOWN,
            latency_ms=0.0,
            message=f"{provider} unreachable: {e}",
        )


# ---------------------------------------------------------------------------
# Exercise 13: Rate Limit Tracking
# ---------------------------------------------------------------------------

class RateLimiter:
    """Sliding-window rate limiter.

    This uses a simple list of timestamps. For high-throughput production
    systems, you'd use a more efficient data structure (sorted set, Redis
    sorted set with ZRANGEBYSCORE, or a token bucket algorithm).

    The sliding window approach is more fair than fixed windows because
    it doesn't have the "boundary burst" problem where a client sends
    max_requests at 11:59:59 and again at 12:00:00.
    """

    def __init__(
        self,
        max_requests: int = 60,
        window_seconds: float = 60.0,
        time_func: Callable[[], float] = time.time,
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._time_func = time_func
        self._timestamps: list[float] = []

    def _cleanup(self) -> None:
        """Remove timestamps outside the current window."""
        now = self._time_func()
        cutoff = now - self.window_seconds
        # Keep only timestamps within the window
        self._timestamps = [t for t in self._timestamps if t > cutoff]

    def allow(self) -> bool:
        """Record a request and return whether it's allowed."""
        now = self._time_func()
        # Always record the timestamp (even if denied)
        self._timestamps.append(now)
        # Clean up old entries
        self._cleanup()
        # Check if we're within the limit
        return len(self._timestamps) <= self.max_requests

    def remaining(self) -> int:
        """Return how many more requests are allowed right now."""
        self._cleanup()
        return max(0, self.max_requests - len(self._timestamps))

    def reset_time(self) -> float | None:
        """Return when the rate limit will reset, or None if not limited."""
        self._cleanup()
        if self.remaining() == 0 and self._timestamps:
            # The oldest timestamp in our window -- when it expires,
            # we'll have room for one more request
            return self._timestamps[0] + self.window_seconds
        return None


# ---------------------------------------------------------------------------
# Exercise 14: Customer Onboarding Validator
# ---------------------------------------------------------------------------

@dataclass
class OnboardingConfig:
    """Customer onboarding configuration to validate."""
    api_key: str
    provider: str
    webhook_url: str | None = None
    rate_limit: int = 60
    allowed_models: list[str] = field(default_factory=list)
    team_name: str = ""


def validate_onboarding(
    config: OnboardingConfig,
    known_providers: list[str] | None = None,
) -> dict[str, Any]:
    """Validate a customer's onboarding configuration.

    This is the kind of function you'd run when a customer submits their
    integration setup form. Clear, specific error messages save enormous
    amounts of support time.
    """
    if known_providers is None:
        known_providers = ["anthropic", "openai", "google", "cohere"]

    errors: list[str] = []
    warnings: list[str] = []

    # Rule 1: API key format
    if not config.api_key.startswith("sk-") or len(config.api_key) < 20:
        errors.append(
            "api_key must start with 'sk-' and be at least 20 characters"
        )

    # Rule 2: Known provider (case-insensitive comparison)
    normalized_providers = [p.lower() for p in known_providers]
    if config.provider.lower() not in normalized_providers:
        errors.append(
            f"Unknown provider '{config.provider}'. "
            f"Supported: {', '.join(known_providers)}"
        )

    # Rule 3: Webhook URL must use HTTPS
    if config.webhook_url is not None:
        if not config.webhook_url.startswith("https://"):
            errors.append("webhook_url must start with 'https://'")

    # Rule 4: Rate limit range
    if not (1 <= config.rate_limit <= 10000):
        errors.append("rate_limit must be between 1 and 10000")

    # Rule 5: At least one allowed model
    if not config.allowed_models:
        errors.append("allowed_models must not be empty")

    # Rule 6: Team name format
    if not config.team_name or not re.match(r'^[a-zA-Z0-9-]+$', config.team_name):
        errors.append(
            "team_name must be non-empty and contain only "
            "alphanumeric characters and hyphens"
        )

    # Warnings (non-blocking)
    if config.rate_limit > 1000:
        warnings.append(
            f"High rate limit ({config.rate_limit} rpm) -- "
            "consider starting lower"
        )

    if len(config.allowed_models) > 10:
        warnings.append(
            f"Large number of models ({len(config.allowed_models)}) -- "
            "consider restricting access"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Exercise 15: Error Classification
# ---------------------------------------------------------------------------

class ErrorCategory(Enum):
    TRANSIENT = "transient"
    RATE_LIMIT = "rate_limit"
    AUTH = "authentication"
    INVALID_REQUEST = "invalid_request"
    MODEL_ERROR = "model_error"
    UNKNOWN = "unknown"


@dataclass
class ClassifiedError:
    """An error with its classification and recommended action."""
    category: ErrorCategory
    original_message: str
    is_retryable: bool
    recommended_action: str


def classify_error(status_code: int, error_message: str) -> ClassifiedError:
    """Classify an API error and recommend an action.

    This classification drives automated remediation (retry? alert? block?)
    and also generates customer-facing guidance. Getting this right saves
    enormous amounts of support ticket volume.
    """
    # Build a lookup of status codes to classifications.
    # Using a dict for clean dispatch rather than a long if/elif chain.
    classifications: dict[int, tuple[ErrorCategory, bool, str]] = {
        401: (
            ErrorCategory.AUTH,
            False,
            "Check your API key and permissions.",
        ),
        403: (
            ErrorCategory.AUTH,
            False,
            "Check your API key and permissions.",
        ),
        429: (
            ErrorCategory.RATE_LIMIT,
            True,
            "Reduce request rate. Implement backoff.",
        ),
        400: (
            ErrorCategory.INVALID_REQUEST,
            False,
            f"Review request format: {error_message}",
        ),
        404: (
            ErrorCategory.INVALID_REQUEST,
            False,
            "Check the model name or endpoint URL.",
        ),
        500: (
            ErrorCategory.TRANSIENT,
            True,
            "Server error -- retry with exponential backoff.",
        ),
        529: (
            ErrorCategory.TRANSIENT,
            True,
            "Service temporarily overloaded -- retry shortly.",
        ),
        503: (
            ErrorCategory.TRANSIENT,
            True,
            "Service temporarily overloaded -- retry shortly.",
        ),
        422: (
            ErrorCategory.MODEL_ERROR,
            False,
            "Check model parameters (temperature, max_tokens, etc.).",
        ),
    }

    if status_code in classifications:
        category, retryable, action = classifications[status_code]
    else:
        category = ErrorCategory.UNKNOWN
        retryable = False
        action = f"Unrecognized error ({status_code}). Contact support."

    return ClassifiedError(
        category=category,
        original_message=error_message,
        is_retryable=retryable,
        recommended_action=action,
    )


# =============================================================================
# TEST SUITE
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Module 01: Customer Integration Patterns - Solution Tests")
    print("=" * 70)

    # ---- Exercise 1: LLMMessage & Base Interface ----
    print("\n--- Exercise 1: LLMMessage & Base Interface ---")
    msg = LLMMessage("user", "Hello, Claude!")
    assert msg.role == "user"
    assert msg.content == "Hello, Claude!"
    assert msg.to_dict() == {"role": "user", "content": "Hello, Claude!"}

    # Invalid role should raise ValueError
    try:
        LLMMessage("invalid", "text")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("  PASS: LLMMessage creation and validation")

    # ---- Exercise 2: Anthropic Client ----
    print("\n--- Exercise 2: Anthropic Client ---")
    anthropic = AnthropicClient()
    assert anthropic.provider_name == "anthropic"

    response = anthropic.complete([LLMMessage("user", "What is Python?")])
    assert isinstance(response, LLMResponse)
    assert response.provider == "anthropic"
    assert "Anthropic" in response.content
    assert "What is Python?" in response.content
    assert response.input_tokens > 0
    assert response.output_tokens == 50
    assert "content" in response.raw_response  # Anthropic format
    print("  PASS: AnthropicClient complete()")

    # ---- Exercise 3: OpenAI Client ----
    print("\n--- Exercise 3: OpenAI Client ---")
    openai_client = OpenAIClient()
    assert openai_client.provider_name == "openai"

    response = openai_client.complete([LLMMessage("user", "What is Python?")])
    assert isinstance(response, LLMResponse)
    assert response.provider == "openai"
    assert "OpenAI" in response.content
    assert response.input_tokens > 0
    assert "choices" in response.raw_response  # OpenAI format
    print("  PASS: OpenAIClient complete()")

    # ---- Exercise 4: Provider Registry ----
    print("\n--- Exercise 4: Provider Registry ---")
    registry = ProviderRegistry()
    registry.register("anthropic", AnthropicClient)
    registry.register("openai", OpenAIClient)

    client = registry.create("anthropic")
    assert isinstance(client, AnthropicClient)
    assert registry.list_providers() == ["anthropic", "openai"]

    try:
        registry.create("nonexistent")
        assert False, "Should have raised KeyError"
    except KeyError as e:
        assert "nonexistent" in str(e)

    print("  PASS: ProviderRegistry register/create/list")

    # ---- Exercise 5: Retry Decorator ----
    print("\n--- Exercise 5: Retry Decorator ---")
    sleep_calls: list[float] = []

    def mock_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    # Test: succeeds after 2 transient failures
    call_counter = [0]  # Use list to allow mutation in nested function

    @retry(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        retryable_exceptions=("TransientError",),
        sleep_func=mock_sleep,
    )
    def flaky_function():
        call_counter[0] += 1
        if call_counter[0] < 3:
            raise TransientError("overloaded")
        return "success"

    result = flaky_function()
    assert result == "success"
    assert call_counter[0] == 3
    assert len(sleep_calls) == 2  # Two retries before success
    assert sleep_calls[0] == 1.0   # base_delay * 2^0
    assert sleep_calls[1] == 2.0   # base_delay * 2^1
    print("  PASS: retry succeeds after transient failures")

    # Test: permanent error is not retried
    perm_counter = [0]

    @retry(
        max_retries=3,
        retryable_exceptions=("TransientError",),
        sleep_func=mock_sleep,
    )
    def permanent_failure():
        perm_counter[0] += 1
        raise PermanentError("unauthorized")

    try:
        permanent_failure()
        assert False, "Should have raised PermanentError"
    except PermanentError:
        assert perm_counter[0] == 1  # No retries for permanent errors

    print("  PASS: permanent errors are not retried")

    # ---- Exercise 6: Circuit Breaker ----
    print("\n--- Exercise 6: Circuit Breaker ---")
    current_time = [0.0]
    cb = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=10.0,
        time_func=lambda: current_time[0],
    )
    assert cb.state == CircuitState.CLOSED

    # Trigger 3 failures to open the circuit
    for i in range(3):
        try:
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        except RuntimeError:
            pass
    assert cb.state == CircuitState.OPEN
    assert cb.failure_count == 3

    # While open, calls should be rejected immediately
    try:
        cb.call(lambda: "should not execute")
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "OPEN" in str(e)

    print("  PASS: circuit opens after threshold failures")

    # Advance time past recovery timeout -> HALF_OPEN
    current_time[0] = 15.0
    result = cb.call(lambda: "recovered!")
    assert result == "recovered!"
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0
    print("  PASS: circuit recovers after timeout")

    # ---- Exercise 7: Request Validation ----
    print("\n--- Exercise 7: Request Validation ---")
    # Empty messages
    errors = validate_request([], {})
    assert "messages list is empty" in errors

    # Missing keys
    errors = validate_request([{"role": "user"}], {})
    assert any("missing key: content" in e for e in errors)

    # Invalid role
    errors = validate_request([{"role": "villain", "content": "ha"}], {})
    assert any("invalid role" in e for e in errors)

    # Empty content
    errors = validate_request([{"role": "user", "content": ""}], {})
    assert any("empty content" in e for e in errors)

    # Bad temperature
    errors = validate_request(
        [{"role": "user", "content": "hi"}],
        {"temperature": 3.0},
    )
    assert any("temperature" in e for e in errors)

    # Valid request
    errors = validate_request(
        [{"role": "user", "content": "Hello"}],
        {"temperature": 0.7, "max_tokens": 1024},
    )
    assert errors == []
    print("  PASS: request validation rules")

    # ---- Exercise 8: Token Estimation ----
    print("\n--- Exercise 8: Token Estimation ---")
    estimate = estimate_request_tokens(
        [{"role": "user", "content": "Hello, how are you?"}],
        model="claude-3-5-sonnet",
        max_tokens=1024,
    )
    assert isinstance(estimate, TokenEstimate)
    assert estimate.input_tokens > 0
    assert estimate.estimated_output_tokens == 1024
    assert estimate.total_tokens == estimate.input_tokens + 1024
    assert estimate.estimated_cost_usd > 0
    print(f"  PASS: estimated {estimate.input_tokens} input tokens, "
          f"${estimate.estimated_cost_usd:.6f}")

    # Unknown model should use default pricing
    est_unknown = estimate_request_tokens(
        [{"role": "user", "content": "test"}],
        model="unknown-model",
    )
    assert est_unknown.estimated_cost_usd > 0
    print("  PASS: unknown model uses default pricing")

    # ---- Exercise 9: Cost Tracker ----
    print("\n--- Exercise 9: Cost Tracker ---")
    tracker = CostTracker(budgets={"team-alpha": 100.0, "team-beta": 50.0})

    tracker.record_usage("team-alpha", "claude-3-5-sonnet", 100000, 50000, 1000.0)
    tracker.record_usage("team-alpha", "gpt-4o", 200000, 100000, 1001.0)
    tracker.record_usage("team-beta", "gpt-4o-mini", 500000, 200000, 1002.0)

    alpha_spend = tracker.get_team_spend("team-alpha")
    assert alpha_spend > 0

    budget_check = tracker.check_budget("team-alpha")
    assert budget_check["team"] == "team-alpha"
    assert budget_check["budget"] == 100.0
    assert budget_check["spent"] == alpha_spend
    assert isinstance(budget_check["over_budget"], bool)

    top = tracker.get_top_teams(2)
    assert len(top) == 2
    assert top[0][1] >= top[1][1]  # Sorted descending
    print(f"  PASS: team-alpha spent ${alpha_spend:.4f}")

    # Unlimited budget team
    tracker.record_usage("team-gamma", "claude-3-5-sonnet", 1000, 500, 1003.0)
    gamma_budget = tracker.check_budget("team-gamma")
    assert gamma_budget["budget"] == float("inf")
    assert gamma_budget["over_budget"] is False
    print("  PASS: unlimited budget teams work correctly")

    # ---- Exercise 10: PII Detection ----
    print("\n--- Exercise 10: PII Detection ---")
    test_text = (
        "Contact john@example.com or call 555-123-4567. "
        "SSN: 123-45-6789. Card: 4111 1111 1111 1111."
    )
    pii_matches = detect_pii(test_text)
    pii_types = {m.pii_type for m in pii_matches}
    assert "email" in pii_types
    assert "phone" in pii_types
    assert "ssn" in pii_types

    # Verify ordering by start position
    for i in range(len(pii_matches) - 1):
        assert pii_matches[i].start <= pii_matches[i + 1].start

    # Test redaction
    redacted = redact_pii(test_text, pii_matches)
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "[REDACTED_SSN]" in redacted
    assert "john@example.com" not in redacted
    assert "555-123-4567" not in redacted
    assert "123-45-6789" not in redacted
    print(f"  PASS: detected {len(pii_matches)} PII matches")
    print(f"  Redacted: {redacted[:70]}...")

    # ---- Exercise 11: Middleware Pipeline ----
    print("\n--- Exercise 11: Middleware Pipeline ---")

    def validation_middleware(ctx: PipelineContext) -> PipelineContext:
        errs = validate_request(ctx.messages, ctx.config)
        ctx.errors.extend(errs)
        if errs:
            ctx.blocked = True
        return ctx

    def token_estimate_middleware(ctx: PipelineContext) -> PipelineContext:
        est = estimate_request_tokens(ctx.messages)
        ctx.metadata["token_estimate"] = est
        return ctx

    def pii_middleware(ctx: PipelineContext) -> PipelineContext:
        for msg in ctx.messages:
            matches = detect_pii(msg.get("content", ""))
            if matches:
                ctx.metadata["pii_detected"] = True
                msg["content"] = redact_pii(msg["content"], matches)
        return ctx

    pipeline = MiddlewarePipeline()
    pipeline.add(validation_middleware).add(pii_middleware).add(token_estimate_middleware)
    assert len(pipeline) == 3

    # Test: valid request with PII goes through all middleware
    ctx = PipelineContext(
        messages=[{"role": "user", "content": "My email is foo@bar.com"}],
        config={"temperature": 0.5},
    )
    result = pipeline.process(ctx)
    assert not result.blocked
    assert "[REDACTED_EMAIL]" in result.messages[0]["content"]
    assert "token_estimate" in result.metadata
    print("  PASS: pipeline processes valid request with PII redaction")

    # Test: invalid request is blocked early
    ctx2 = PipelineContext(messages=[], config={})
    result2 = pipeline.process(ctx2)
    assert result2.blocked
    assert len(result2.errors) > 0
    # Token estimation should NOT have run (blocked by validation)
    assert "token_estimate" not in result2.metadata
    print("  PASS: pipeline blocks invalid request early")

    # ---- Exercise 12: Health Checker ----
    print("\n--- Exercise 12: Health Checker ---")
    healthy = check_provider_health("anthropic", lambda p: (True, 150.0))
    assert healthy.status == HealthStatus.HEALTHY
    assert healthy.latency_ms == 150.0

    degraded = check_provider_health("openai", lambda p: (True, 3000.0))
    assert degraded.status == HealthStatus.DEGRADED

    def failing_ping(p: str) -> tuple[bool, float]:
        raise ConnectionError("timeout")

    down = check_provider_health("cohere", failing_ping)
    assert down.status == HealthStatus.DOWN

    down2 = check_provider_health("test", lambda p: (False, 0.0))
    assert down2.status == HealthStatus.DOWN

    print("  PASS: health check for healthy/degraded/down providers")

    # ---- Exercise 13: Rate Limiter ----
    print("\n--- Exercise 13: Rate Limiter ---")
    current_rl_time = [0.0]
    rl = RateLimiter(
        max_requests=3,
        window_seconds=10.0,
        time_func=lambda: current_rl_time[0],
    )

    # First 3 requests should be allowed
    assert rl.allow() is True   # request 1
    assert rl.allow() is True   # request 2
    assert rl.allow() is True   # request 3
    assert rl.remaining() == 0
    assert rl.allow() is False  # request 4: denied

    # Check reset time
    reset = rl.reset_time()
    assert reset is not None
    assert reset == 10.0  # oldest timestamp (0.0) + window (10.0)

    # Advance time so oldest request expires
    current_rl_time[0] = 11.0
    assert rl.remaining() > 0
    assert rl.allow() is True

    print("  PASS: sliding window rate limiter")

    # ---- Exercise 14: Onboarding Validator ----
    print("\n--- Exercise 14: Onboarding Validator ---")

    # Valid config
    valid_config = OnboardingConfig(
        api_key="sk-1234567890abcdefghij",
        provider="anthropic",
        webhook_url="https://hooks.example.com/notify",
        rate_limit=60,
        allowed_models=["claude-3-5-sonnet"],
        team_name="engineering-team",
    )
    result = validate_onboarding(valid_config)
    assert result["valid"] is True
    assert result["errors"] == []
    print("  PASS: valid config passes")

    # Invalid config: multiple errors
    bad_config = OnboardingConfig(
        api_key="bad-key",
        provider="unknown-provider",
        webhook_url="http://insecure.com",
        rate_limit=0,
        allowed_models=[],
        team_name="",
    )
    result = validate_onboarding(bad_config)
    assert result["valid"] is False
    assert len(result["errors"]) >= 5  # Should catch all issues
    print(f"  PASS: invalid config catches {len(result['errors'])} errors")

    # Warnings
    warn_config = OnboardingConfig(
        api_key="sk-1234567890abcdefghij",
        provider="openai",
        rate_limit=5000,
        allowed_models=[f"model-{i}" for i in range(15)],
        team_name="big-team",
    )
    result = validate_onboarding(warn_config)
    assert result["valid"] is True
    assert len(result["warnings"]) == 2
    print(f"  PASS: warnings generated for high rate limit and many models")

    # ---- Exercise 15: Error Classification ----
    print("\n--- Exercise 15: Error Classification ---")
    # Auth errors
    err = classify_error(401, "invalid api key")
    assert err.category == ErrorCategory.AUTH
    assert err.is_retryable is False

    err = classify_error(403, "forbidden")
    assert err.category == ErrorCategory.AUTH

    # Rate limit
    err = classify_error(429, "rate limited")
    assert err.category == ErrorCategory.RATE_LIMIT
    assert err.is_retryable is True

    # Invalid request
    err = classify_error(400, "missing 'messages' field")
    assert err.category == ErrorCategory.INVALID_REQUEST
    assert "missing 'messages' field" in err.recommended_action

    err = classify_error(404, "model not found")
    assert err.category == ErrorCategory.INVALID_REQUEST

    # Transient
    err = classify_error(500, "internal server error")
    assert err.category == ErrorCategory.TRANSIENT
    assert err.is_retryable is True

    err = classify_error(529, "overloaded")
    assert err.category == ErrorCategory.TRANSIENT

    err = classify_error(503, "service unavailable")
    assert err.category == ErrorCategory.TRANSIENT

    # Model error
    err = classify_error(422, "invalid temperature value")
    assert err.category == ErrorCategory.MODEL_ERROR
    assert err.is_retryable is False

    # Unknown
    err = classify_error(418, "I'm a teapot")
    assert err.category == ErrorCategory.UNKNOWN
    assert "418" in err.recommended_action

    print("  PASS: error classification for all status codes")

    # ---- Summary ----
    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)
