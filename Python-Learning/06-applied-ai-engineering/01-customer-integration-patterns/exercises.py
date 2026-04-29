"""
Module 01: Customer Integration Patterns - Exercises
======================================================
Phase 6: Applied AI Engineering

Target audience: Experienced Swift/iOS developers transitioning to
AI/ML engineering roles (solutions engineer, applied AI engineer).

These exercises teach the patterns you will use daily when helping
customers integrate LLM APIs into their applications. You will build:
  - Unified multi-provider client interfaces
  - Resilience patterns (retries, circuit breakers)
  - Middleware pipelines (validation, cost tracking, PII detection)
  - Operational tooling (health checks, rate limiting, onboarding)

Instructions:
  - Fill in each function/class body (replace `pass` or
    `raise NotImplementedError` with your solution).
  - Run this file to check your work: `python exercises.py`
  - All exercises use assert statements for self-checking.
  - No real API keys are needed -- everything uses mocks.

Difficulty levels:
  Easy   - Direct translation from Swift/Vapor concepts
  Medium - Requires understanding Python-specific patterns
  Hard   - Combines multiple concepts or requires creative design

Swift parallels noted where relevant.
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
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: Your team supports customers integrating with multiple LLM
# providers. Rather than writing provider-specific code everywhere, you need
# a common interface that lets customers swap providers without rewriting
# their application logic.
#
# Swift parallel: This is like defining a protocol in Swift:
#     protocol LLMClient {
#         func complete(messages: [Message], config: Config) -> Response
#     }

class LLMMessage:
    """A single message in a conversation.

    Attributes:
        role: One of "system", "user", or "assistant".
        content: The text content of the message.
    """

    def __init__(self, role: str, content: str) -> None:
        # TODO: Store role and content. Validate that role is one of
        # "system", "user", or "assistant"; raise ValueError otherwise.
        raise NotImplementedError

    def to_dict(self) -> dict[str, str]:
        """Return {"role": ..., "content": ...}."""
        raise NotImplementedError


@dataclass
class LLMConfig:
    """Configuration for an LLM completion request.

    Fields:
        model: Model identifier (e.g. "claude-3-5-sonnet", "gpt-4o").
        temperature: Sampling temperature, 0.0-2.0, default 0.7.
        max_tokens: Maximum tokens in the response, default 1024.
    """
    model: str = "claude-3-5-sonnet"
    temperature: float = 0.7
    max_tokens: int = 1024


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider.

    Fields:
        content: The generated text.
        model: Which model produced the response.
        input_tokens: Number of input tokens consumed.
        output_tokens: Number of output tokens produced.
        provider: Provider name (e.g. "anthropic", "openai").
        raw_response: The original provider-specific response dict.
    """
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    provider: str
    raw_response: dict[str, Any] = field(default_factory=dict)


class BaseLLMClient(ABC):
    """Abstract base class for LLM provider clients.

    Subclasses must implement `complete()` and `provider_name`.
    Think of this as a Swift protocol with associated types.

    Requirements:
        - `provider_name` property returning a string
        - `complete(messages, config)` returning an LLMResponse
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name, e.g. 'anthropic' or 'openai'."""
        ...

    @abstractmethod
    def complete(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> LLMResponse:
        """Send a completion request and return a standardized response."""
        ...


# ---------------------------------------------------------------------------
# Exercise 2: Implement Anthropic-Specific Client
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: A customer wants to integrate with the Anthropic (Claude) API.
# Implement a mock client that simulates Anthropic's response format.

class AnthropicClient(BaseLLMClient):
    """Mock Anthropic API client.

    The `complete` method should:
    1. Use config or defaults (model="claude-3-5-sonnet").
    2. Build a simulated raw response in Anthropic's format:
       {
           "id": "msg_mock_001",
           "type": "message",
           "role": "assistant",
           "content": [{"type": "text", "text": "<generated>"}],
           "model": "<model>",
           "usage": {"input_tokens": <estimated>, "output_tokens": <estimated>}
       }
    3. Estimate tokens: input_tokens = sum of len(m.content) // 4 for each
       message; output_tokens = 50 (fixed mock value).
    4. The generated text should be:
       f"[Anthropic/{model}] Mock response to: {last_user_message_content}"
    5. Return an LLMResponse with provider="anthropic".
    """

    @property
    def provider_name(self) -> str:
        raise NotImplementedError

    def complete(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> LLMResponse:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 3: Implement OpenAI-Specific Client
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: Another customer uses OpenAI. Same interface, different
# underlying format.

class OpenAIClient(BaseLLMClient):
    """Mock OpenAI API client.

    The `complete` method should:
    1. Use config or defaults (model="gpt-4o").
    2. Build a simulated raw response in OpenAI's format:
       {
           "id": "chatcmpl-mock001",
           "object": "chat.completion",
           "choices": [
               {
                   "index": 0,
                   "message": {"role": "assistant", "content": "<generated>"},
                   "finish_reason": "stop"
               }
           ],
           "model": "<model>",
           "usage": {
               "prompt_tokens": <estimated>,
               "completion_tokens": <estimated>,
               "total_tokens": <total>
           }
       }
    3. Estimate tokens: prompt_tokens = sum of len(m.content) // 4 for
       each message; completion_tokens = 50 (fixed mock value).
    4. The generated text should be:
       f"[OpenAI/{model}] Mock response to: {last_user_message_content}"
    5. Return an LLMResponse with provider="openai".
       Map prompt_tokens -> input_tokens, completion_tokens -> output_tokens.
    """

    @property
    def provider_name(self) -> str:
        raise NotImplementedError

    def complete(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> LLMResponse:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 4: Build a Provider Factory / Registry
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: Customers should be able to request a client by provider name.
# Build a registry that maps names to client classes and instantiates them.
#
# Swift parallel: This is similar to a factory pattern using a dictionary
# of types, like [String: LLMClient.Type].

class ProviderRegistry:
    """Registry that maps provider names to client classes.

    Usage:
        registry = ProviderRegistry()
        registry.register("anthropic", AnthropicClient)
        client = registry.create("anthropic")

    Methods:
        register(name, client_class) - Add a provider.
        create(name, **kwargs) -> BaseLLMClient - Instantiate a provider.
            Raise KeyError with helpful message if name not found.
        list_providers() -> list[str] - Return sorted list of registered names.
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def register(self, name: str, client_class: type[BaseLLMClient]) -> None:
        raise NotImplementedError

    def create(self, name: str, **kwargs: Any) -> BaseLLMClient:
        raise NotImplementedError

    def list_providers(self) -> list[str]:
        raise NotImplementedError


# =============================================================================
# SECTION 2: Resilience Patterns
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 5: Exponential Backoff Retry Decorator
# Difficulty: Hard
# ---------------------------------------------------------------------------
# Scenario: A customer reports intermittent 529 "overloaded" errors from
# the API. You need a retry decorator with exponential backoff.
#
# Requirements:
# - Decorator factory: retry(max_retries=3, base_delay=1.0, backoff_factor=2.0)
# - Only retry on exceptions whose type name is in `retryable_exceptions`
#   (default: ("TransientError",)).
# - Delay = base_delay * (backoff_factor ** attempt), where attempt starts at 0.
# - For testability, accept an optional `sleep_func` parameter (default time.sleep).
# - Return the successful result if any attempt succeeds.
# - If all retries are exhausted, raise the last exception.
#
# Swift parallel: Think of this like a property wrapper that adds retry
# behavior to an async function.

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
    """Decorator factory that adds exponential backoff retry logic.

    Args:
        max_retries: Maximum number of retry attempts (not counting the
            initial call). So max_retries=3 means up to 4 total calls.
        base_delay: Base delay in seconds before the first retry.
        backoff_factor: Multiplier for each subsequent delay.
        retryable_exceptions: Tuple of exception class *names* (strings)
            that should trigger a retry.
        sleep_func: Function to call for sleeping (injectable for testing).

    Returns:
        A decorator that wraps a function with retry logic.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 6: Circuit Breaker Pattern
# Difficulty: Hard
# ---------------------------------------------------------------------------
# Scenario: A downstream provider is experiencing an outage. Instead of
# hammering their API and making things worse, you want to "trip" a circuit
# breaker after N consecutive failures and fast-fail subsequent requests.
#
# States: CLOSED (normal), OPEN (failing fast), HALF_OPEN (testing recovery).

class CircuitState(Enum):
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing fast, not sending requests
    HALF_OPEN = "half_open"  # Allowing one test request through


class CircuitBreaker:
    """Implements the circuit breaker pattern for API calls.

    Constructor args:
        failure_threshold: Number of consecutive failures before opening.
            Default 5.
        recovery_timeout: Seconds to wait before transitioning from
            OPEN -> HALF_OPEN. Default 30.0.
        time_func: Callable returning current time (injectable for testing).

    Attributes to track:
        state: Current CircuitState (start CLOSED).
        failure_count: Consecutive failure count.
        last_failure_time: Timestamp of most recent failure (or 0.0).

    Methods:
        call(func, *args, **kwargs):
            - If OPEN: check if recovery_timeout has elapsed.
              If yes, transition to HALF_OPEN. If no, raise RuntimeError
              with message "Circuit breaker is OPEN".
            - If CLOSED or HALF_OPEN: call func(*args, **kwargs).
              On success: reset failure_count to 0, set state to CLOSED,
              return result.
              On exception: increment failure_count, record time. If
              failure_count >= failure_threshold, set state to OPEN. Re-raise.
        reset(): Reset to initial CLOSED state.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        time_func: Callable[[], float] = time.time,
    ) -> None:
        raise NotImplementedError

    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError


# =============================================================================
# SECTION 3: Middleware Pipeline
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 7: Request Validation Middleware
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: Before sending a request to the LLM, validate that the input
# meets basic requirements. This prevents wasted API calls and gives
# customers clear error messages.

def validate_request(
    messages: list[dict[str, str]],
    config: dict[str, Any],
) -> list[str]:
    """Validate an LLM request and return a list of error strings.

    Validation rules:
    1. messages must not be empty -> "messages list is empty"
    2. Each message must have "role" and "content" keys ->
       "message at index {i} missing key: {key}"
    3. Each role must be one of ("system", "user", "assistant") ->
       "message at index {i} has invalid role: {role}"
    4. No message content may be empty string ->
       "message at index {i} has empty content"
    5. config["temperature"] (if present) must be between 0.0 and 2.0 ->
       "temperature must be between 0.0 and 2.0"
    6. config["max_tokens"] (if present) must be between 1 and 100000 ->
       "max_tokens must be between 1 and 100000"

    Returns:
        List of error strings. Empty list means the request is valid.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 8: Token Counting Middleware
# Difficulty: Easy
# ---------------------------------------------------------------------------
# Scenario: Customers frequently ask "how many tokens will this cost?"
# before making an API call. Build a pre-flight token estimator.

@dataclass
class TokenEstimate:
    """Estimated token counts for a request.

    Fields:
        input_tokens: Estimated input/prompt tokens.
        estimated_output_tokens: Estimated output tokens (from max_tokens).
        total_tokens: Sum of input and estimated output.
        estimated_cost_usd: Rough cost estimate in USD.
    """
    input_tokens: int
    estimated_output_tokens: int
    total_tokens: int
    estimated_cost_usd: float


def estimate_request_tokens(
    messages: list[dict[str, str]],
    model: str = "claude-3-5-sonnet",
    max_tokens: int = 1024,
) -> TokenEstimate:
    """Estimate token usage and cost for a request before sending it.

    Token estimation rules:
    - Input tokens: sum of (len(msg["content"]) // 4) for all messages,
      plus 4 tokens overhead per message (for role formatting), minimum 1
      total.
    - Estimated output tokens: use max_tokens as the upper bound.
    - Cost: use this pricing table (per 1M tokens):
        "claude-3-5-sonnet": input=$3.00,  output=$15.00
        "claude-3-opus":     input=$15.00, output=$75.00
        "gpt-4o":            input=$5.00,  output=$15.00
        "gpt-4o-mini":       input=$0.15,  output=$0.60
      For unknown models, use input=$10.00, output=$30.00.

    Returns:
        A TokenEstimate dataclass.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 9: Cost Tracking Middleware
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: An enterprise customer wants to track API spend across teams,
# with configurable per-team budgets and alerts.

@dataclass
class UsageRecord:
    """A single API usage record.

    Fields:
        team: Team identifier string.
        model: Model used.
        input_tokens: Actual input tokens used.
        output_tokens: Actual output tokens used.
        cost_usd: Calculated cost in USD.
        timestamp: Unix timestamp of the request.
    """
    team: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float


class CostTracker:
    """Tracks API costs across teams with budget enforcement.

    Constructor args:
        budgets: dict mapping team name -> monthly budget in USD.
            Teams not in this dict have unlimited budget.

    Methods:
        record_usage(team, model, input_tokens, output_tokens, timestamp):
            - Calculate cost using the same pricing table as Exercise 8.
            - Create a UsageRecord and store it.
            - Return the UsageRecord.

        get_team_spend(team) -> float:
            Return total spend for a team across all records.

        check_budget(team) -> dict:
            Return {
                "team": team,
                "budget": budget or float("inf"),
                "spent": total_spend,
                "remaining": budget - total_spend,
                "over_budget": bool
            }

        get_top_teams(n=5) -> list[tuple[str, float]]:
            Return the top N teams by spend as (team, total_spend) tuples,
            sorted descending by spend.
    """

    def __init__(self, budgets: dict[str, float] | None = None) -> None:
        raise NotImplementedError

    def record_usage(
        self,
        team: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        timestamp: float | None = None,
    ) -> UsageRecord:
        raise NotImplementedError

    def get_team_spend(self, team: str) -> float:
        raise NotImplementedError

    def check_budget(self, team: str) -> dict[str, Any]:
        raise NotImplementedError

    def get_top_teams(self, n: int = 5) -> list[tuple[str, float]]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 10: PII Detection Middleware
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: Before sending prompts to an LLM, you need to scan for PII
# (personally identifiable information) that should not be sent to
# third-party APIs. This is a simple regex-based approach -- production
# systems use more sophisticated NER models.

@dataclass
class PIIMatch:
    """A detected PII occurrence.

    Fields:
        pii_type: Category of PII found (e.g. "email", "phone", "ssn").
        value: The matched text.
        start: Start index in the original text.
        end: End index in the original text.
    """
    pii_type: str
    value: str
    start: int
    end: int


def detect_pii(text: str) -> list[PIIMatch]:
    """Scan text for common PII patterns using regex.

    Patterns to detect:
    1. "email" - standard email pattern: word chars, dots, hyphens @
       domain. Use: r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}'
    2. "phone" - US phone numbers with optional country code.
       Use: r'\\+?1?[-.\\s]?\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}'
    3. "ssn" - Social Security Numbers (XXX-XX-XXXX).
       Use: r'\\b\\d{3}-\\d{2}-\\d{4}\\b'
    4. "credit_card" - 13-19 digit card numbers with optional separators.
       Use: r'\\b(?:\\d[- ]?){13,19}\\b'

    Returns:
        List of PIIMatch objects, sorted by start position.
    """
    raise NotImplementedError


def redact_pii(text: str, matches: list[PIIMatch]) -> str:
    """Replace detected PII in text with redaction markers.

    Each PII match should be replaced with [REDACTED_{pii_type_upper}].
    For example, an email becomes [REDACTED_EMAIL].

    Process matches in reverse order (by start position) to preserve
    indices. Return the redacted text.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 11: Middleware Chain / Pipeline
# Difficulty: Hard
# ---------------------------------------------------------------------------
# Scenario: Combine multiple middleware functions into a pipeline that
# processes a request through each stage before sending it to the LLM.
#
# Swift parallel: This is like composing middleware in Vapor:
#     app.middleware.use(LoggingMiddleware())
#     app.middleware.use(AuthMiddleware())

@dataclass
class PipelineContext:
    """Context object passed through the middleware pipeline.

    Fields:
        messages: The list of message dicts.
        config: Request configuration dict.
        metadata: Dict for middleware to attach data (token estimates,
            PII scan results, etc.).
        errors: List of error strings from validation.
        blocked: Whether the request should be blocked (default False).
    """
    messages: list[dict[str, str]]
    config: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    blocked: bool = False


# A Middleware is a callable: (PipelineContext) -> PipelineContext
MiddlewareFunc = Callable[[PipelineContext], PipelineContext]


class MiddlewarePipeline:
    """A composable pipeline of middleware functions.

    Methods:
        add(middleware_func): Append a middleware function to the pipeline.
        process(context) -> PipelineContext: Run context through each
            middleware in order. If any middleware sets context.blocked = True,
            stop processing and return immediately.
        __len__(): Return number of middleware in the pipeline.
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def add(self, middleware: MiddlewareFunc) -> "MiddlewarePipeline":
        """Add a middleware and return self for chaining."""
        raise NotImplementedError

    def process(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


# =============================================================================
# SECTION 4: Operational Tooling
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 12: API Health Checker
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: You need a dashboard that shows the health of each LLM provider.
# Build a health checker that pings each provider and reports status.

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass
class HealthCheckResult:
    """Result of a health check for one provider.

    Fields:
        provider: Provider name.
        status: HealthStatus enum value.
        latency_ms: Response time in milliseconds (0.0 if down).
        message: Human-readable status message.
    """
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

    Args:
        provider: Provider name to check.
        ping_func: Callable that takes a provider name and returns
            (success: bool, latency_ms: float). If it raises an exception,
            the provider is DOWN.
        latency_threshold_ms: Latency above this -> DEGRADED status.

    Returns:
        HealthCheckResult with:
        - HEALTHY if ping succeeds and latency < threshold
        - DEGRADED if ping succeeds but latency >= threshold
        - DOWN if ping returns success=False or raises an exception
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 13: Rate Limit Tracking
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: A customer is hitting rate limits. Build a sliding-window
# rate limiter that tracks requests per time window.

class RateLimiter:
    """Sliding-window rate limiter.

    Constructor args:
        max_requests: Maximum requests allowed in the window.
        window_seconds: Size of the sliding window in seconds.
        time_func: Callable returning current time (injectable for testing).

    Methods:
        allow() -> bool:
            Record current time. Remove timestamps older than the window.
            Return True if the number of requests in the window (including
            this one) is <= max_requests. Return False otherwise.
            Always record the timestamp regardless of allow/deny.

        remaining() -> int:
            Return how many more requests are allowed in the current window.
            (Clean up old timestamps first.) Minimum 0.

        reset_time() -> float | None:
            If currently rate-limited (remaining == 0), return the timestamp
            when the oldest request in the window will expire (i.e., oldest
            timestamp + window_seconds). Return None if not rate-limited.
    """

    def __init__(
        self,
        max_requests: int = 60,
        window_seconds: float = 60.0,
        time_func: Callable[[], float] = time.time,
    ) -> None:
        raise NotImplementedError

    def allow(self) -> bool:
        raise NotImplementedError

    def remaining(self) -> int:
        raise NotImplementedError

    def reset_time(self) -> float | None:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 14: Customer Onboarding Validator
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: When a new customer onboards, validate that their integration
# configuration is correct before they go live.

@dataclass
class OnboardingConfig:
    """Customer onboarding configuration to validate.

    Fields:
        api_key: Their API key (must start with "sk-" and be 20+ chars).
        provider: Provider name (must be one of known providers).
        webhook_url: Optional webhook URL (must start with "https://" if set).
        rate_limit: Requests per minute (must be 1-10000).
        allowed_models: List of model names they want access to.
        team_name: Team identifier (must be non-empty alphanumeric + hyphens).
    """
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

    Args:
        config: The OnboardingConfig to validate.
        known_providers: List of supported provider names.
            Default: ["anthropic", "openai", "google", "cohere"]

    Validation rules:
    1. api_key must start with "sk-" and be at least 20 characters.
    2. provider must be in known_providers (case-insensitive).
    3. If webhook_url is set, it must start with "https://".
    4. rate_limit must be between 1 and 10000 inclusive.
    5. allowed_models must not be empty.
    6. team_name must be non-empty and match r'^[a-zA-Z0-9-]+$'.

    Returns:
        {
            "valid": bool,
            "errors": list[str],     # list of validation error messages
            "warnings": list[str]    # list of non-blocking warnings
        }
        Warnings to include:
        - If rate_limit > 1000: "High rate limit ({rate_limit} rpm) --
          consider starting lower"
        - If len(allowed_models) > 10: "Large number of models
          ({count}) -- consider restricting access"
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 15: Error Classification
# Difficulty: Medium
# ---------------------------------------------------------------------------
# Scenario: A customer reports various errors and you need to classify them
# to determine the right remediation: retry, fix config, contact support, etc.

class ErrorCategory(Enum):
    TRANSIENT = "transient"           # Retry will likely fix it
    RATE_LIMIT = "rate_limit"         # Slow down, then retry
    AUTH = "authentication"           # Fix API key / permissions
    INVALID_REQUEST = "invalid_request"  # Fix the request
    MODEL_ERROR = "model_error"       # Try a different model or params
    UNKNOWN = "unknown"               # Escalate to support


@dataclass
class ClassifiedError:
    """An error with its classification and recommended action.

    Fields:
        category: ErrorCategory enum value.
        original_message: The original error message.
        is_retryable: Whether automatic retry makes sense.
        recommended_action: Human-readable guidance for the customer.
    """
    category: ErrorCategory
    original_message: str
    is_retryable: bool
    recommended_action: str


def classify_error(status_code: int, error_message: str) -> ClassifiedError:
    """Classify an API error and recommend an action.

    Classification rules by status code:
    - 401, 403 -> AUTH, not retryable,
        action: "Check your API key and permissions."
    - 429 -> RATE_LIMIT, retryable,
        action: "Reduce request rate. Implement backoff."
    - 400 -> INVALID_REQUEST, not retryable,
        action: "Review request format: {error_message}"
    - 404 -> INVALID_REQUEST, not retryable,
        action: "Check the model name or endpoint URL."
    - 500 -> TRANSIENT, retryable,
        action: "Server error -- retry with exponential backoff."
    - 529, 503 -> TRANSIENT, retryable,
        action: "Service temporarily overloaded -- retry shortly."
    - 422 -> MODEL_ERROR, not retryable,
        action: "Check model parameters (temperature, max_tokens, etc.)."
    - Any other code -> UNKNOWN, not retryable,
        action: "Unrecognized error ({status_code}). Contact support."

    Returns:
        ClassifiedError with the appropriate classification.
    """
    raise NotImplementedError


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Module 01: Customer Integration Patterns - Exercise Validation")
    print("=" * 70)

    passed = 0
    failed = 0

    def check(name: str, test_func: Callable[[], bool]) -> None:
        global passed, failed
        try:
            result = test_func()
            if result:
                print(f"  PASS  {name}")
                passed += 1
            else:
                print(f"  FAIL  {name} (returned False)")
                failed += 1
        except NotImplementedError:
            print(f"  SKIP  {name} (not implemented)")
        except Exception as e:
            print(f"  FAIL  {name} ({type(e).__name__}: {e})")
            failed += 1

    # --- Exercise 1 ---
    print("\nExercise 1: LLM Message & Base Interface")
    check("LLMMessage creation", lambda: (
        LLMMessage("user", "Hello").role == "user"
    ))
    check("LLMMessage to_dict", lambda: (
        LLMMessage("assistant", "Hi").to_dict() == {"role": "assistant", "content": "Hi"}
    ))
    check("LLMMessage invalid role raises ValueError", lambda: (
        _raises(ValueError, lambda: LLMMessage("invalid", "text"))
    ))

    # --- Exercise 2 ---
    print("\nExercise 2: Anthropic Client")
    check("AnthropicClient provider_name", lambda: (
        AnthropicClient().provider_name == "anthropic"
    ))
    check("AnthropicClient complete returns LLMResponse", lambda: (
        isinstance(
            AnthropicClient().complete([LLMMessage("user", "test")]),
            LLMResponse,
        )
    ))

    # --- Exercise 3 ---
    print("\nExercise 3: OpenAI Client")
    check("OpenAIClient provider_name", lambda: (
        OpenAIClient().provider_name == "openai"
    ))
    check("OpenAIClient complete returns LLMResponse", lambda: (
        isinstance(
            OpenAIClient().complete([LLMMessage("user", "test")]),
            LLMResponse,
        )
    ))

    # --- Exercise 4 ---
    print("\nExercise 4: Provider Registry")
    check("ProviderRegistry register and create", lambda: (
        _test_registry()
    ))

    # --- Exercise 5 ---
    print("\nExercise 5: Retry Decorator")
    check("retry succeeds after transient failures", lambda: (
        _test_retry()
    ))

    # --- Exercise 6 ---
    print("\nExercise 6: Circuit Breaker")
    check("CircuitBreaker opens after threshold", lambda: (
        _test_circuit_breaker()
    ))

    # --- Exercise 7 ---
    print("\nExercise 7: Request Validation")
    check("validate_request catches empty messages", lambda: (
        "messages list is empty" in validate_request([], {})
    ))

    # --- Exercise 8 ---
    print("\nExercise 8: Token Estimation")
    check("estimate_request_tokens returns TokenEstimate", lambda: (
        isinstance(
            estimate_request_tokens([{"role": "user", "content": "hello"}]),
            TokenEstimate,
        )
    ))

    # --- Exercise 9 ---
    print("\nExercise 9: Cost Tracker")
    check("CostTracker records and tracks", lambda: (
        _test_cost_tracker()
    ))

    # --- Exercise 10 ---
    print("\nExercise 10: PII Detection")
    check("detect_pii finds email", lambda: (
        any(m.pii_type == "email" for m in detect_pii("email: test@example.com"))
    ))
    check("redact_pii replaces email", lambda: (
        "[REDACTED_EMAIL]" in redact_pii(
            "email: test@example.com",
            detect_pii("email: test@example.com"),
        )
    ))

    # --- Exercise 11 ---
    print("\nExercise 11: Middleware Pipeline")
    check("MiddlewarePipeline processes context", lambda: (
        _test_pipeline()
    ))

    # --- Exercise 12 ---
    print("\nExercise 12: Health Checker")
    check("check_provider_health healthy", lambda: (
        check_provider_health("test", lambda p: (True, 100.0)).status
        == HealthStatus.HEALTHY
    ))

    # --- Exercise 13 ---
    print("\nExercise 13: Rate Limiter")
    check("RateLimiter allows within limit", lambda: (
        _test_rate_limiter()
    ))

    # --- Exercise 14 ---
    print("\nExercise 14: Onboarding Validator")
    check("validate_onboarding catches bad api_key", lambda: (
        not validate_onboarding(OnboardingConfig(api_key="bad"))["valid"]
    ))

    # --- Exercise 15 ---
    print("\nExercise 15: Error Classification")
    check("classify_error 429 -> RATE_LIMIT", lambda: (
        classify_error(429, "rate limited").category == ErrorCategory.RATE_LIMIT
    ))

    print(f"\n{'=' * 70}")
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)


# -- Helper functions for self-check --

def _raises(exc_type: type, func: Callable) -> bool:
    try:
        func()
        return False
    except exc_type:
        return True
    except Exception:
        return False


def _test_registry() -> bool:
    r = ProviderRegistry()
    r.register("anthropic", AnthropicClient)
    r.register("openai", OpenAIClient)
    client = r.create("anthropic")
    return (
        isinstance(client, AnthropicClient)
        and r.list_providers() == ["anthropic", "openai"]
    )


def _test_retry() -> bool:
    call_count = 0

    @retry(
        max_retries=3,
        base_delay=0.0,
        retryable_exceptions=("TransientError",),
        sleep_func=lambda _: None,
    )
    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise TransientError("overloaded")
        return "success"

    result = flaky()
    return result == "success" and call_count == 3


def _test_circuit_breaker() -> bool:
    current_time = [0.0]
    cb = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=10.0,
        time_func=lambda: current_time[0],
    )
    for _ in range(3):
        try:
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        except RuntimeError:
            pass
    return cb.state == CircuitState.OPEN


def _test_cost_tracker() -> bool:
    ct = CostTracker(budgets={"team-a": 100.0})
    ct.record_usage("team-a", "claude-3-5-sonnet", 1000, 500, 1000.0)
    return ct.get_team_spend("team-a") > 0


def _test_pipeline() -> bool:
    pipeline = MiddlewarePipeline()

    def add_marker(ctx: PipelineContext) -> PipelineContext:
        ctx.metadata["marked"] = True
        return ctx

    pipeline.add(add_marker)
    ctx = PipelineContext(
        messages=[{"role": "user", "content": "hi"}],
        config={},
    )
    result = pipeline.process(ctx)
    return result.metadata.get("marked") is True


def _test_rate_limiter() -> bool:
    current_time = [0.0]
    rl = RateLimiter(
        max_requests=3,
        window_seconds=10.0,
        time_func=lambda: current_time[0],
    )
    results = [rl.allow() for _ in range(4)]
    # First 3 should be True, 4th False
    return results == [True, True, True, False]
