"""
Module 02: Cost & Performance Optimization - Exercises
========================================================

15 exercises covering cost tracking, performance profiling, and optimization
strategies for production LLM applications.

These exercises simulate real-world scenarios you will face as an applied AI
engineer: estimating costs before API calls, routing requests to the cheapest
capable model, enforcing budgets, detecting anomalies, and generating reports.

No real API keys are needed -- all exercises use mock data and local logic.

Run this file directly to check your solutions:
    python exercises.py
"""

from __future__ import annotations

import time
import hashlib
from typing import Any
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Shared data structures used across exercises
# ---------------------------------------------------------------------------

# Pricing per 1M tokens (USD) -- representative as of mid-2025
MODEL_PRICING: dict[str, dict[str, float]] = {
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-opus":     {"input": 15.00, "output": 75.00},
    "claude-3-haiku":    {"input": 0.25, "output": 1.25},
    "gpt-4o":            {"input": 5.00, "output": 15.00},
    "gpt-4o-mini":       {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo":     {"input": 0.50, "output": 1.50},
}

# Average tokens-per-character ratio by model family (simplified)
CHARS_PER_TOKEN: dict[str, float] = {
    "claude": 3.5,
    "gpt":    4.0,
}


@dataclass
class UsageRecord:
    """A single API call usage record."""
    request_id: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    timestamp: float          # epoch seconds
    cost_usd: float = 0.0


@dataclass
class BudgetConfig:
    """Budget configuration for a project or team."""
    daily_limit_usd: float
    monthly_limit_usd: float
    alert_threshold: float = 0.8   # fraction of budget that triggers alert


# ---------------------------------------------------------------------------
# Exercise 1: Token Counter
# ---------------------------------------------------------------------------
def count_tokens(text: str, model: str) -> int:
    """
    Estimate the number of tokens in *text* for the given *model*.

    Use CHARS_PER_TOKEN to look up the correct ratio.  Determine the model
    family by checking whether the model name starts with "claude" or "gpt".
    If the model family is not found, default to 4.0 chars per token.

    Always return at least 1 token for non-empty text, and 0 for empty text.

    Args:
        text: The input string to tokenize.
        model: A model identifier (e.g. "claude-3-haiku").

    Returns:
        Estimated token count (int).
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Cost Calculator
# ---------------------------------------------------------------------------
def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Calculate the cost in USD for a single API call.

    Formula:
        cost = (input_tokens / 1_000_000) * input_price
             + (output_tokens / 1_000_000) * output_price

    Use MODEL_PRICING.  Return 0.0 for unknown models.

    Args:
        model: Model identifier.
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.

    Returns:
        Cost in USD (float).
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Pre-Call Cost Estimator
# ---------------------------------------------------------------------------
def estimate_call_cost(
    prompt: str,
    model: str,
    expected_output_tokens: int = 500,
) -> dict[str, Any]:
    """
    Estimate the cost of an API call *before* making it.

    Steps:
    1. Use count_tokens() to estimate input tokens from the prompt.
    2. Use calculate_cost() with estimated input tokens and expected_output_tokens.
    3. Return a dict with keys:
       - "model": the model name
       - "estimated_input_tokens": int
       - "expected_output_tokens": int
       - "estimated_cost_usd": float

    Args:
        prompt: The full prompt string.
        model: Model identifier.
        expected_output_tokens: Expected output length in tokens.

    Returns:
        Dictionary with estimation details.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Model Selector Based on Task Complexity
# ---------------------------------------------------------------------------
def select_model(
    task_description: str,
    max_cost_usd: float = 0.10,
    require_vision: bool = False,
) -> str:
    """
    Select the cheapest model that satisfies the constraints.

    Complexity heuristic (based on task_description length):
      - len <= 100 chars   -> "simple"
      - len <= 500 chars   -> "moderate"
      - len >  500 chars   -> "complex"

    Model capabilities (simplified):
      - simple   : any model works
      - moderate : exclude gpt-3.5-turbo and gpt-4o-mini
      - complex  : only claude-3-opus, claude-3-5-sonnet, gpt-4o

    Vision-capable models: claude-3-5-sonnet, claude-3-opus, gpt-4o

    From the remaining candidates, pick the one with the lowest *output*
    price (as a proxy for overall cheapness).  If no model fits within
    max_cost_usd for a 1000-input / 1000-output token scenario, return
    "no_model_available".

    Args:
        task_description: Natural-language description of the task.
        max_cost_usd: Maximum acceptable cost for a 1k/1k token call.
        require_vision: Whether the task requires image input.

    Returns:
        Selected model identifier or "no_model_available".
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Cost-Aware Model Router
# ---------------------------------------------------------------------------
def route_request(
    messages: list[dict[str, str]],
    budget_remaining_usd: float,
    priority: str = "balanced",
) -> dict[str, Any]:
    """
    Route an API request to the best model given remaining budget.

    priority values:
      - "cost"    : always pick the cheapest model
      - "quality" : pick the most capable model that fits the budget
      - "balanced": pick the best value (capability per dollar)

    Steps:
    1. Estimate input tokens from all message 'content' fields combined.
    2. Assume 500 output tokens.
    3. For each model in MODEL_PRICING, compute estimated cost.
    4. Filter to models whose estimated cost <= budget_remaining_usd.
    5. Apply priority logic to select from remaining candidates.

    Model quality ranking (best to worst):
      claude-3-opus > gpt-4o > claude-3-5-sonnet > gpt-4o-mini >
      claude-3-haiku > gpt-3.5-turbo

    Return dict with: "model", "estimated_cost_usd", "reason" (short string).
    If no model fits the budget, return model="none", estimated_cost_usd=0,
    reason="budget_exhausted".

    Args:
        messages: Conversation messages list.
        budget_remaining_usd: Remaining budget in USD.
        priority: One of "cost", "quality", "balanced".

    Returns:
        Routing decision dictionary.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Prompt Optimizer
# ---------------------------------------------------------------------------
def optimize_prompt(prompt: str) -> dict[str, Any]:
    """
    Reduce token count of a prompt while preserving meaning.

    Apply these transformations in order:
    1. Strip leading/trailing whitespace.
    2. Collapse multiple consecutive whitespace characters into single spaces.
    3. Remove filler phrases: "please ", "kindly ", "I would like you to ",
       "Could you please ", "I need you to " (case-insensitive).
    4. Remove duplicate sentences (keep first occurrence, compare lowercased).

    Return dict with:
      - "original_tokens": estimated tokens of original prompt (use 4 chars/token)
      - "optimized_tokens": estimated tokens of optimized prompt
      - "savings_pct": percentage reduction (float, 0-100)
      - "optimized_prompt": the transformed string

    Args:
        prompt: The original prompt text.

    Returns:
        Optimization results dictionary.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Prompt Cache
# ---------------------------------------------------------------------------
class PromptCache:
    """
    A simple prompt cache that stores responses keyed by prompt hash.

    Implement:
      - get(prompt) -> cached response or None
      - put(prompt, response, input_tokens, output_tokens) -> None
      - stats() -> dict with "hits", "misses", "saved_tokens", "entries"

    Cache key: SHA-256 hex digest of the prompt string (UTF-8 encoded).
    Track hits and misses.  "saved_tokens" is the total input+output tokens
    avoided by cache hits.
    """

    def __init__(self, max_size: int = 100) -> None:
        self.max_size = max_size
        self._cache: dict[str, dict[str, Any]] = {}
        self._hits: int = 0
        self._misses: int = 0
        self._saved_tokens: int = 0

    def _hash_prompt(self, prompt: str) -> str:
        """Return SHA-256 hex digest of prompt."""
        raise NotImplementedError

    def get(self, prompt: str) -> str | None:
        """Return cached response or None.  Update hit/miss counters."""
        raise NotImplementedError

    def put(
        self,
        prompt: str,
        response: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """
        Store response in cache.  If cache is full, evict the oldest entry.
        Store input_tokens + output_tokens alongside the response so that
        saved_tokens can be computed on cache hits.
        """
        raise NotImplementedError

    def stats(self) -> dict[str, int]:
        """Return cache statistics."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 8: Latency Profiler
# ---------------------------------------------------------------------------
def profile_latencies(records: list[UsageRecord]) -> dict[str, Any]:
    """
    Compute latency statistics from a list of UsageRecord objects.

    Return dict with per-model stats and overall stats:
    {
        "per_model": {
            "<model>": {
                "count": int,
                "mean_ms": float,
                "p50_ms": float,    # median
                "p95_ms": float,
                "p99_ms": float,
                "min_ms": float,
                "max_ms": float,
            },
            ...
        },
        "overall": {
            "count": int,
            "mean_ms": float,
            "p50_ms": float,
            "p95_ms": float,
            "p99_ms": float,
        }
    }

    Use linear interpolation for percentiles:
      sorted values, index = (percentile/100) * (n - 1).
      If index is integer, take that value; otherwise interpolate between
      floor and ceil indices.

    Args:
        records: List of UsageRecord objects.

    Returns:
        Nested statistics dictionary.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Batch Request Processor
# ---------------------------------------------------------------------------
def plan_batch(
    prompts: list[str],
    model: str,
    max_batch_cost_usd: float,
    max_batch_size: int = 50,
) -> list[dict[str, Any]]:
    """
    Split a list of prompts into cost-efficient batches.

    For each prompt, estimate input tokens (use count_tokens) and assume
    200 output tokens.  Group prompts into batches such that:
      - No single batch exceeds max_batch_cost_usd.
      - No single batch exceeds max_batch_size prompts.

    Return a list of batch dicts, each containing:
      - "batch_index": int (0-based)
      - "prompt_indices": list[int] (indices into the original list)
      - "estimated_cost_usd": float
      - "num_prompts": int

    Prompts should be added to the current batch greedily (in order).
    When adding the next prompt would exceed either limit, start a new batch.

    Args:
        prompts: List of prompt strings.
        model: Model to use for estimation.
        max_batch_cost_usd: Maximum cost per batch.
        max_batch_size: Maximum prompts per batch.

    Returns:
        List of batch plan dictionaries.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Rate Limiter (Token Bucket)
# ---------------------------------------------------------------------------
class TokenBucketRateLimiter:
    """
    Token-bucket rate limiter for API requests.

    Implement:
      - try_acquire(tokens=1) -> bool: attempt to consume tokens, return
        True if allowed, False if denied.
      - wait_time() -> float: seconds until at least 1 token is available.
      - reset() -> None: refill bucket to capacity.

    The bucket refills at `refill_rate` tokens per second, up to `capacity`.
    """

    def __init__(self, capacity: int, refill_rate: float) -> None:
        """
        Args:
            capacity: Maximum tokens in the bucket.
            refill_rate: Tokens added per second.
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill_time = time.monotonic()

    def _refill(self) -> None:
        """Add tokens based on elapsed time since last refill."""
        raise NotImplementedError

    def try_acquire(self, tokens: int = 1) -> bool:
        """Try to consume *tokens*. Return True if successful."""
        raise NotImplementedError

    def wait_time(self) -> float:
        """Seconds until at least 1 token is available (0.0 if available now)."""
        raise NotImplementedError

    def reset(self) -> None:
        """Refill bucket to full capacity."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 11: Cost Dashboard Data Aggregator
# ---------------------------------------------------------------------------
def aggregate_dashboard_data(
    records: list[UsageRecord],
) -> dict[str, Any]:
    """
    Aggregate usage records into dashboard-ready data.

    Return dict with:
    {
        "total_cost_usd": float,
        "total_requests": int,
        "total_input_tokens": int,
        "total_output_tokens": int,
        "by_model": {
            "<model>": {
                "cost_usd": float,
                "requests": int,
                "avg_latency_ms": float,
                "input_tokens": int,
                "output_tokens": int,
            },
            ...
        },
        "cost_trend": [                    # one entry per unique day
            {"date": "YYYY-MM-DD", "cost_usd": float},
            ...
        ],
    }

    Dates should be derived from record.timestamp (epoch -> date string)
    and cost_trend should be sorted chronologically.

    Args:
        records: List of UsageRecord objects.

    Returns:
        Dashboard data dictionary.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Budget Enforcer
# ---------------------------------------------------------------------------
class BudgetEnforcer:
    """
    Enforce daily and monthly spending limits.

    Implement:
      - record_spend(amount_usd, timestamp) -> None
      - can_spend(amount_usd, timestamp) -> dict with:
          "allowed": bool
          "reason": str  ("ok", "daily_limit", or "monthly_limit")
          "daily_remaining_usd": float
          "monthly_remaining_usd": float
      - get_spend(timestamp) -> dict with "daily_usd" and "monthly_usd"

    Use timestamp (epoch float) to bucket spending by calendar day (UTC)
    and calendar month.
    """

    def __init__(self, config: BudgetConfig) -> None:
        self.config = config
        self._daily_spend: dict[str, float] = {}    # "YYYY-MM-DD" -> USD
        self._monthly_spend: dict[str, float] = {}  # "YYYY-MM" -> USD

    def record_spend(self, amount_usd: float, timestamp: float) -> None:
        """Record a spending event."""
        raise NotImplementedError

    def can_spend(self, amount_usd: float, timestamp: float) -> dict[str, Any]:
        """Check if spending amount_usd is within budget."""
        raise NotImplementedError

    def get_spend(self, timestamp: float) -> dict[str, float]:
        """Return current daily and monthly spend for the timestamp's day/month."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 13: A/B Test Cost Comparator
# ---------------------------------------------------------------------------
def compare_ab_costs(
    group_a: list[UsageRecord],
    group_b: list[UsageRecord],
) -> dict[str, Any]:
    """
    Compare costs and performance between two A/B test groups.

    Return dict with:
    {
        "group_a": {
            "total_cost_usd": float,
            "avg_cost_per_request": float,
            "avg_latency_ms": float,
            "total_requests": int,
            "models_used": list[str],       # unique, sorted
        },
        "group_b": { ... same keys ... },
        "cost_difference_pct": float,       # (B - A) / A * 100
        "latency_difference_pct": float,    # (B - A) / A * 100
        "recommendation": str,             # "group_a", "group_b", or "no_difference"
    }

    Recommendation logic:
      - If one group is cheaper AND faster -> recommend it.
      - If one group is >= 20% cheaper but not slower -> recommend it.
      - Otherwise -> "no_difference".

    Args:
        group_a: Usage records for group A.
        group_b: Usage records for group B.

    Returns:
        Comparison results dictionary.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 14: Usage Report Generator
# ---------------------------------------------------------------------------
def generate_usage_report(
    records: list[UsageRecord],
    report_title: str = "LLM Usage Report",
) -> str:
    """
    Generate a plain-text usage report from usage records.

    The report should include these sections (separated by blank lines):
    1. Title (the report_title)
    2. Summary: total requests, total cost, date range
    3. Per-model breakdown table:
       Model | Requests | Input Tokens | Output Tokens | Cost (USD)
    4. Top 5 most expensive requests (by cost_usd, descending)
    5. Average cost per request

    Use simple text formatting (dashes for separators, aligned columns
    are not required but nice to have).

    Args:
        records: List of UsageRecord objects.
        report_title: Title for the report.

    Returns:
        Multi-line report string.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 15: Cost Anomaly Detection
# ---------------------------------------------------------------------------
def detect_cost_anomalies(
    records: list[UsageRecord],
    z_threshold: float = 2.0,
) -> list[dict[str, Any]]:
    """
    Detect anomalous API calls based on cost using z-score method.

    Steps:
    1. Calculate the mean and standard deviation of cost_usd across all records.
    2. For each record, compute z_score = (cost - mean) / std_dev.
       (If std_dev is 0, no anomalies exist.)
    3. Flag records whose abs(z_score) > z_threshold as anomalies.

    Return a list of anomaly dicts, each with:
      - "request_id": str
      - "model": str
      - "cost_usd": float
      - "z_score": float (rounded to 2 decimals)
      - "severity": "warning" if abs(z) <= 3.0 else "critical"

    Sort by abs(z_score) descending.

    Args:
        records: List of UsageRecord objects.
        z_threshold: Z-score threshold for flagging (default 2.0).

    Returns:
        List of anomaly dictionaries.
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import datetime as _dt

    # -- Exercise 1: Token Counter --
    tokens = count_tokens("Hello, world!", "claude-3-haiku")
    assert isinstance(tokens, int) and tokens > 0
    assert count_tokens("", "gpt-4o") == 0

    # -- Exercise 2: Cost Calculator --
    cost = calculate_cost("claude-3-haiku", 1000, 1000)
    assert isinstance(cost, float) and cost > 0
    assert calculate_cost("unknown-model", 100, 100) == 0.0

    # -- Exercise 3: Pre-Call Cost Estimator --
    est = estimate_call_cost("Tell me about Python", "gpt-4o", 300)
    assert "estimated_input_tokens" in est
    assert "estimated_cost_usd" in est
    assert est["model"] == "gpt-4o"

    # -- Exercise 4: Model Selector --
    model = select_model("Summarize this short text")
    assert model in MODEL_PRICING or model == "no_model_available"
    model_v = select_model("Analyze this image in detail", require_vision=True)
    assert model_v in ("claude-3-5-sonnet", "claude-3-opus", "gpt-4o")

    # -- Exercise 5: Cost-Aware Router --
    msgs = [{"role": "user", "content": "Hello, how are you?"}]
    route = route_request(msgs, budget_remaining_usd=0.01, priority="cost")
    assert "model" in route and "estimated_cost_usd" in route
    route_q = route_request(msgs, budget_remaining_usd=10.0, priority="quality")
    assert route_q["model"] != "none"

    # -- Exercise 6: Prompt Optimizer --
    original = "  Please   kindly   summarize the text. Summarize the text.  "
    result = optimize_prompt(original)
    assert result["optimized_tokens"] <= result["original_tokens"]
    assert "savings_pct" in result

    # -- Exercise 7: Prompt Cache --
    cache = PromptCache(max_size=2)
    assert cache.get("test prompt") is None
    cache.put("test prompt", "test response", 10, 20)
    assert cache.get("test prompt") == "test response"
    s = cache.stats()
    assert s["hits"] == 1 and s["misses"] == 1 and s["saved_tokens"] == 30

    # -- Exercise 8: Latency Profiler --
    recs = [
        UsageRecord("r1", "gpt-4o", 100, 50, 120.0, time.time()),
        UsageRecord("r2", "gpt-4o", 200, 80, 250.0, time.time()),
        UsageRecord("r3", "claude-3-haiku", 50, 30, 60.0, time.time()),
    ]
    stats = profile_latencies(recs)
    assert "per_model" in stats and "overall" in stats
    assert stats["overall"]["count"] == 3

    # -- Exercise 9: Batch Processor --
    prompts = ["Short prompt"] * 10
    batches = plan_batch(prompts, "gpt-4o-mini", max_batch_cost_usd=0.01)
    assert isinstance(batches, list) and len(batches) >= 1
    assert all("batch_index" in b for b in batches)

    # -- Exercise 10: Rate Limiter --
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1.0)
    assert limiter.try_acquire(3) is True
    assert limiter.try_acquire(3) is False
    limiter.reset()
    assert limiter.try_acquire(5) is True

    # -- Exercise 11: Dashboard Aggregator --
    ts_base = _dt.datetime(2025, 6, 1, tzinfo=_dt.timezone.utc).timestamp()
    dash_recs = [
        UsageRecord("d1", "gpt-4o", 500, 200, 150.0, ts_base, 0.0040),
        UsageRecord("d2", "gpt-4o", 300, 100, 100.0, ts_base + 3600, 0.0020),
        UsageRecord("d3", "claude-3-haiku", 100, 50, 40.0, ts_base + 86400, 0.0001),
    ]
    dash = aggregate_dashboard_data(dash_recs)
    assert dash["total_requests"] == 3
    assert "by_model" in dash and "cost_trend" in dash

    # -- Exercise 12: Budget Enforcer --
    cfg = BudgetConfig(daily_limit_usd=1.0, monthly_limit_usd=10.0)
    enforcer = BudgetEnforcer(cfg)
    enforcer.record_spend(0.50, ts_base)
    result = enforcer.can_spend(0.40, ts_base)
    assert result["allowed"] is True
    result2 = enforcer.can_spend(0.60, ts_base)
    assert result2["allowed"] is False

    # -- Exercise 13: A/B Comparator --
    group_a = [
        UsageRecord("a1", "gpt-4o", 100, 50, 200.0, ts_base, 0.0013),
        UsageRecord("a2", "gpt-4o", 150, 80, 250.0, ts_base, 0.0020),
    ]
    group_b = [
        UsageRecord("b1", "claude-3-haiku", 100, 50, 80.0, ts_base, 0.0001),
        UsageRecord("b2", "claude-3-haiku", 150, 80, 90.0, ts_base, 0.0002),
    ]
    comp = compare_ab_costs(group_a, group_b)
    assert "cost_difference_pct" in comp
    assert "recommendation" in comp

    # -- Exercise 14: Usage Report --
    report = generate_usage_report(dash_recs, "Test Report")
    assert "Test Report" in report
    assert isinstance(report, str) and len(report) > 50

    # -- Exercise 15: Anomaly Detection --
    anomaly_recs = [
        UsageRecord(f"n{i}", "gpt-4o", 100, 50, 100.0, ts_base, 0.001)
        for i in range(20)
    ]
    # inject one outlier
    anomaly_recs.append(
        UsageRecord("outlier", "gpt-4o", 10000, 5000, 500.0, ts_base, 0.50)
    )
    anomalies = detect_cost_anomalies(anomaly_recs)
    assert isinstance(anomalies, list)
    assert any(a["request_id"] == "outlier" for a in anomalies)

    print("All exercises passed!")
