"""
Module 02: Cost & Performance Optimization - Solutions
=======================================================

Complete implementations for all 15 exercises with detailed comments.

Run this file directly to verify all solutions:
    python solutions.py
"""

from __future__ import annotations

import math
import time
import hashlib
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Shared data structures (same as exercises.py)
# ---------------------------------------------------------------------------

MODEL_PRICING: dict[str, dict[str, float]] = {
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-opus":     {"input": 15.00, "output": 75.00},
    "claude-3-haiku":    {"input": 0.25, "output": 1.25},
    "gpt-4o":            {"input": 5.00, "output": 15.00},
    "gpt-4o-mini":       {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo":     {"input": 0.50, "output": 1.50},
}

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
    timestamp: float
    cost_usd: float = 0.0


@dataclass
class BudgetConfig:
    """Budget configuration for a project or team."""
    daily_limit_usd: float
    monthly_limit_usd: float
    alert_threshold: float = 0.8


# ---------------------------------------------------------------------------
# Solution 1: Token Counter
# ---------------------------------------------------------------------------
def count_tokens(text: str, model: str) -> int:
    """
    Estimate token count using per-model-family character ratios.

    We determine the model family by checking the model name prefix, then
    look up the average characters-per-token ratio.  This mirrors the quick
    estimation approach that solutions engineers use before making real
    tokenizer calls (e.g., tiktoken or Anthropic's tokenizer).
    """
    if not text:
        return 0

    # Determine chars-per-token from model family
    ratio = 4.0  # default fallback
    for family, cpt in CHARS_PER_TOKEN.items():
        if model.startswith(family):
            ratio = cpt
            break

    # Estimate tokens -- always at least 1 for non-empty text
    estimated = len(text) / ratio
    return max(1, int(estimated))


# ---------------------------------------------------------------------------
# Solution 2: Cost Calculator
# ---------------------------------------------------------------------------
def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Calculate USD cost from token counts using MODEL_PRICING.

    Pricing is specified per 1 million tokens, so we divide by 1_000_000.
    Returns 0.0 for unknown models -- a defensive pattern that prevents
    crashes in routing logic.
    """
    if model not in MODEL_PRICING:
        return 0.0

    rates = MODEL_PRICING[model]
    input_cost = (input_tokens / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    return input_cost + output_cost


# ---------------------------------------------------------------------------
# Solution 3: Pre-Call Cost Estimator
# ---------------------------------------------------------------------------
def estimate_call_cost(
    prompt: str,
    model: str,
    expected_output_tokens: int = 500,
) -> dict[str, Any]:
    """
    Estimate cost before making an API call.

    This is a critical pattern for production systems: you want to know
    the approximate cost *before* committing to an API call, especially
    when operating under a budget.  Real implementations might also add
    system prompt tokens and message-framing overhead.
    """
    estimated_input = count_tokens(prompt, model)
    estimated_cost = calculate_cost(model, estimated_input, expected_output_tokens)

    return {
        "model": model,
        "estimated_input_tokens": estimated_input,
        "expected_output_tokens": expected_output_tokens,
        "estimated_cost_usd": estimated_cost,
    }


# ---------------------------------------------------------------------------
# Solution 4: Model Selector Based on Task Complexity
# ---------------------------------------------------------------------------
def select_model(
    task_description: str,
    max_cost_usd: float = 0.10,
    require_vision: bool = False,
) -> str:
    """
    Select the cheapest adequate model for a task.

    In practice, applied AI engineers build model routers that consider
    task complexity, cost constraints, latency SLAs, and capability
    requirements (vision, tool use, long context).  This simplified
    version uses description length as a complexity proxy.
    """
    # 1. Determine complexity from description length
    desc_len = len(task_description)
    if desc_len <= 100:
        complexity = "simple"
    elif desc_len <= 500:
        complexity = "moderate"
    else:
        complexity = "complex"

    # 2. Filter models by complexity requirements
    all_models = list(MODEL_PRICING.keys())

    if complexity == "complex":
        candidates = ["claude-3-opus", "claude-3-5-sonnet", "gpt-4o"]
    elif complexity == "moderate":
        candidates = [m for m in all_models if m not in ("gpt-3.5-turbo", "gpt-4o-mini")]
    else:
        candidates = all_models

    # 3. Filter by vision requirement
    vision_models = {"claude-3-5-sonnet", "claude-3-opus", "gpt-4o"}
    if require_vision:
        candidates = [m for m in candidates if m in vision_models]

    # 4. Filter by cost: compute cost for a 1k/1k scenario
    affordable = []
    for m in candidates:
        cost = calculate_cost(m, 1000, 1000)
        if cost <= max_cost_usd:
            affordable.append((m, cost))

    if not affordable:
        return "no_model_available"

    # 5. Pick cheapest by output price (proxy for overall cheapness)
    affordable.sort(key=lambda x: MODEL_PRICING[x[0]]["output"])
    return affordable[0][0]


# ---------------------------------------------------------------------------
# Solution 5: Cost-Aware Model Router
# ---------------------------------------------------------------------------
def route_request(
    messages: list[dict[str, str]],
    budget_remaining_usd: float,
    priority: str = "balanced",
) -> dict[str, Any]:
    """
    Route a request to the optimal model given budget and priority.

    This is one of the most impactful patterns in production AI systems.
    A smart router can reduce costs 30-60% by sending simple queries to
    cheap models and only using expensive models when needed.
    """
    # Quality ranking: index 0 = best quality
    quality_ranking = [
        "claude-3-opus",
        "gpt-4o",
        "claude-3-5-sonnet",
        "gpt-4o-mini",
        "claude-3-haiku",
        "gpt-3.5-turbo",
    ]

    # Estimate input tokens from all messages
    all_text = " ".join(m.get("content", "") for m in messages)
    # Use 4.0 as a generic ratio since we don't know the model yet
    input_tokens = max(1, len(all_text) // 4)
    output_tokens = 500  # assumption

    # Compute estimated cost for each model and filter by budget
    candidates: list[tuple[str, float]] = []
    for model in quality_ranking:
        cost = calculate_cost(model, input_tokens, output_tokens)
        if cost <= budget_remaining_usd:
            candidates.append((model, cost))

    if not candidates:
        return {
            "model": "none",
            "estimated_cost_usd": 0.0,
            "reason": "budget_exhausted",
        }

    # Apply priority selection
    if priority == "cost":
        # Pick cheapest
        candidates.sort(key=lambda x: x[1])
        chosen = candidates[0]
        reason = "cheapest_model"

    elif priority == "quality":
        # Pick highest quality (first in quality_ranking that appears in candidates)
        candidate_models = {m for m, _ in candidates}
        for model in quality_ranking:
            if model in candidate_models:
                cost = next(c for m, c in candidates if m == model)
                chosen = (model, cost)
                reason = "highest_quality_within_budget"
                break

    else:  # "balanced"
        # Best value: quality rank per dollar.  Lower quality index = better.
        # Score = quality_position / cost  (lower is better value)
        def value_score(item: tuple[str, float]) -> float:
            model, cost = item
            # quality position: 0 = best
            pos = quality_ranking.index(model)
            # Avoid division by zero
            return pos * max(cost, 1e-10)

        candidates.sort(key=value_score)
        chosen = candidates[0]
        reason = "best_value"

    return {
        "model": chosen[0],
        "estimated_cost_usd": chosen[1],
        "reason": reason,
    }


# ---------------------------------------------------------------------------
# Solution 6: Prompt Optimizer
# ---------------------------------------------------------------------------
def optimize_prompt(prompt: str) -> dict[str, Any]:
    """
    Reduce token count by removing filler phrases and redundancy.

    In practice, prompt optimization can yield 10-40% cost savings on
    high-volume applications.  More advanced techniques include:
    - Automatic summarization of context
    - Dynamic few-shot example selection
    - Semantic deduplication of instructions
    """
    import re

    original_tokens = max(1, len(prompt) // 4)

    # Step 1: Strip leading/trailing whitespace
    optimized = prompt.strip()

    # Step 2: Collapse multiple whitespace into single spaces
    optimized = re.sub(r"\s+", " ", optimized)

    # Step 3: Remove filler phrases (case-insensitive)
    filler_phrases = [
        "please ",
        "kindly ",
        "I would like you to ",
        "Could you please ",
        "I need you to ",
    ]
    for phrase in filler_phrases:
        # Case-insensitive removal
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        optimized = pattern.sub("", optimized)

    # Clean up any double spaces left after removal
    optimized = re.sub(r"\s+", " ", optimized).strip()

    # Step 4: Remove duplicate sentences (keep first occurrence)
    # Split on sentence-ending punctuation while keeping the delimiter
    sentences = re.split(r"(?<=[.!?])\s+", optimized)
    seen: set[str] = set()
    unique_sentences: list[str] = []
    for sentence in sentences:
        key = sentence.lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique_sentences.append(sentence.strip())
    optimized = " ".join(unique_sentences)

    optimized_tokens = max(1, len(optimized) // 4) if optimized else 0

    savings_pct = 0.0
    if original_tokens > 0:
        savings_pct = ((original_tokens - optimized_tokens) / original_tokens) * 100

    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "savings_pct": savings_pct,
        "optimized_prompt": optimized,
    }


# ---------------------------------------------------------------------------
# Solution 7: Prompt Cache
# ---------------------------------------------------------------------------
class PromptCache:
    """
    SHA-256 keyed prompt cache with hit/miss tracking.

    Caching identical prompts is one of the simplest and most effective
    cost-reduction strategies.  Anthropic and OpenAI both offer server-side
    prompt caching, but client-side caching catches exact duplicates before
    they ever reach the API.
    """

    def __init__(self, max_size: int = 100) -> None:
        self.max_size = max_size
        self._cache: dict[str, dict[str, Any]] = {}
        self._hits: int = 0
        self._misses: int = 0
        self._saved_tokens: int = 0
        # Track insertion order for eviction
        self._order: list[str] = []

    def _hash_prompt(self, prompt: str) -> str:
        """Return SHA-256 hex digest of prompt."""
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    def get(self, prompt: str) -> str | None:
        """Return cached response or None.  Update hit/miss counters."""
        key = self._hash_prompt(prompt)
        if key in self._cache:
            self._hits += 1
            entry = self._cache[key]
            # Accumulate saved tokens on each hit
            self._saved_tokens += entry["input_tokens"] + entry["output_tokens"]
            return entry["response"]
        else:
            self._misses += 1
            return None

    def put(
        self,
        prompt: str,
        response: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """
        Store response in cache.  Evict oldest entry if at capacity.
        """
        key = self._hash_prompt(prompt)

        # Evict oldest if full and this is a new key
        if key not in self._cache and len(self._cache) >= self.max_size:
            oldest_key = self._order.pop(0)
            del self._cache[oldest_key]

        self._cache[key] = {
            "response": response,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
        if key not in self._order:
            self._order.append(key)

    def stats(self) -> dict[str, int]:
        """Return cache statistics."""
        return {
            "hits": self._hits,
            "misses": self._misses,
            "saved_tokens": self._saved_tokens,
            "entries": len(self._cache),
        }


# ---------------------------------------------------------------------------
# Solution 8: Latency Profiler
# ---------------------------------------------------------------------------
def _percentile(sorted_values: list[float], pct: float) -> float:
    """
    Compute percentile using linear interpolation.

    This matches numpy's default 'linear' interpolation method.
    """
    n = len(sorted_values)
    if n == 0:
        return 0.0
    if n == 1:
        return sorted_values[0]

    idx = (pct / 100.0) * (n - 1)
    lower = int(idx)
    upper = min(lower + 1, n - 1)
    fraction = idx - lower

    return sorted_values[lower] + fraction * (sorted_values[upper] - sorted_values[lower])


def _compute_latency_stats(latencies: list[float]) -> dict[str, float]:
    """Compute mean and percentile stats for a list of latencies."""
    sorted_lat = sorted(latencies)
    mean_val = sum(sorted_lat) / len(sorted_lat)
    return {
        "count": len(sorted_lat),
        "mean_ms": round(mean_val, 2),
        "p50_ms": round(_percentile(sorted_lat, 50), 2),
        "p95_ms": round(_percentile(sorted_lat, 95), 2),
        "p99_ms": round(_percentile(sorted_lat, 99), 2),
        "min_ms": round(sorted_lat[0], 2),
        "max_ms": round(sorted_lat[-1], 2),
    }


def profile_latencies(records: list[UsageRecord]) -> dict[str, Any]:
    """
    Compute latency statistics grouped by model and overall.

    Latency profiling is essential for meeting SLAs.  In production,
    you would also track time-to-first-token (TTFT) and
    inter-token latency for streaming responses.
    """
    # Group latencies by model
    by_model: dict[str, list[float]] = {}
    all_latencies: list[float] = []

    for rec in records:
        by_model.setdefault(rec.model, []).append(rec.latency_ms)
        all_latencies.append(rec.latency_ms)

    per_model = {}
    for model, latencies in by_model.items():
        per_model[model] = _compute_latency_stats(latencies)

    overall = {}
    if all_latencies:
        overall_stats = _compute_latency_stats(all_latencies)
        # Overall doesn't include min/max to match the exercise spec
        overall = {
            "count": overall_stats["count"],
            "mean_ms": overall_stats["mean_ms"],
            "p50_ms": overall_stats["p50_ms"],
            "p95_ms": overall_stats["p95_ms"],
            "p99_ms": overall_stats["p99_ms"],
        }

    return {
        "per_model": per_model,
        "overall": overall,
    }


# ---------------------------------------------------------------------------
# Solution 9: Batch Request Processor
# ---------------------------------------------------------------------------
def plan_batch(
    prompts: list[str],
    model: str,
    max_batch_cost_usd: float,
    max_batch_size: int = 50,
) -> list[dict[str, Any]]:
    """
    Greedily pack prompts into cost-bounded batches.

    Batch processing is used with APIs that offer batch endpoints
    (e.g., OpenAI's Batch API at 50% discount).  Even without a
    discount, batching helps with rate-limit management and cost tracking.
    """
    batches: list[dict[str, Any]] = []
    current_indices: list[int] = []
    current_cost = 0.0
    output_tokens_per_prompt = 200  # assumption from exercise spec

    for i, prompt in enumerate(prompts):
        input_tokens = count_tokens(prompt, model)
        prompt_cost = calculate_cost(model, input_tokens, output_tokens_per_prompt)

        # Check if adding this prompt would exceed limits
        would_exceed_cost = (current_cost + prompt_cost) > max_batch_cost_usd
        would_exceed_size = len(current_indices) >= max_batch_size

        if current_indices and (would_exceed_cost or would_exceed_size):
            # Finalize current batch
            batches.append({
                "batch_index": len(batches),
                "prompt_indices": current_indices,
                "estimated_cost_usd": round(current_cost, 8),
                "num_prompts": len(current_indices),
            })
            current_indices = []
            current_cost = 0.0

        current_indices.append(i)
        current_cost += prompt_cost

    # Finalize last batch
    if current_indices:
        batches.append({
            "batch_index": len(batches),
            "prompt_indices": current_indices,
            "estimated_cost_usd": round(current_cost, 8),
            "num_prompts": len(current_indices),
        })

    return batches


# ---------------------------------------------------------------------------
# Solution 10: Rate Limiter (Token Bucket)
# ---------------------------------------------------------------------------
class TokenBucketRateLimiter:
    """
    Token-bucket rate limiter.

    The token bucket algorithm is the industry standard for API rate
    limiting.  Tokens refill continuously at refill_rate per second up
    to capacity.  Each request consumes one or more tokens.

    This is the same algorithm used by most cloud API gateways and is
    how providers like Anthropic and OpenAI enforce their rate limits.
    """

    def __init__(self, capacity: int, refill_rate: float) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill_time = time.monotonic()

    def _refill(self) -> None:
        """Add tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill_time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill_time = now

    def try_acquire(self, tokens: int = 1) -> bool:
        """Try to consume *tokens*. Return True if successful."""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def wait_time(self) -> float:
        """Seconds until at least 1 token is available (0.0 if available now)."""
        self._refill()
        if self.tokens >= 1.0:
            return 0.0
        tokens_needed = 1.0 - self.tokens
        return tokens_needed / self.refill_rate

    def reset(self) -> None:
        """Refill bucket to full capacity."""
        self.tokens = float(self.capacity)
        self.last_refill_time = time.monotonic()


# ---------------------------------------------------------------------------
# Solution 11: Cost Dashboard Data Aggregator
# ---------------------------------------------------------------------------
def aggregate_dashboard_data(
    records: list[UsageRecord],
) -> dict[str, Any]:
    """
    Aggregate usage records into dashboard-ready data.

    Dashboard aggregation is a common backend task for AI engineering
    teams.  The output feeds cost monitoring dashboards (Grafana, Datadog,
    or custom internal tools).
    """
    total_cost = 0.0
    total_input = 0
    total_output = 0
    by_model: dict[str, dict[str, Any]] = {}
    daily_costs: dict[str, float] = {}

    for rec in records:
        total_cost += rec.cost_usd
        total_input += rec.input_tokens
        total_output += rec.output_tokens

        # Per-model aggregation
        if rec.model not in by_model:
            by_model[rec.model] = {
                "cost_usd": 0.0,
                "requests": 0,
                "total_latency_ms": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
            }
        entry = by_model[rec.model]
        entry["cost_usd"] += rec.cost_usd
        entry["requests"] += 1
        entry["total_latency_ms"] += rec.latency_ms
        entry["input_tokens"] += rec.input_tokens
        entry["output_tokens"] += rec.output_tokens

        # Daily cost aggregation
        dt = datetime.fromtimestamp(rec.timestamp, tz=timezone.utc)
        day_key = dt.strftime("%Y-%m-%d")
        daily_costs[day_key] = daily_costs.get(day_key, 0.0) + rec.cost_usd

    # Compute average latencies
    for model, data in by_model.items():
        data["avg_latency_ms"] = round(
            data.pop("total_latency_ms") / data["requests"], 2
        )

    # Build sorted cost trend
    cost_trend = [
        {"date": date, "cost_usd": round(cost, 6)}
        for date, cost in sorted(daily_costs.items())
    ]

    return {
        "total_cost_usd": round(total_cost, 6),
        "total_requests": len(records),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "by_model": by_model,
        "cost_trend": cost_trend,
    }


# ---------------------------------------------------------------------------
# Solution 12: Budget Enforcer
# ---------------------------------------------------------------------------
class BudgetEnforcer:
    """
    Enforce daily and monthly spending limits.

    Budget enforcement is critical for enterprise AI deployments.
    Without it, a misconfigured prompt loop or sudden traffic spike
    can consume an entire monthly budget in minutes.
    """

    def __init__(self, config: BudgetConfig) -> None:
        self.config = config
        self._daily_spend: dict[str, float] = {}
        self._monthly_spend: dict[str, float] = {}

    def _day_key(self, timestamp: float) -> str:
        """Convert epoch to YYYY-MM-DD string (UTC)."""
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")

    def _month_key(self, timestamp: float) -> str:
        """Convert epoch to YYYY-MM string (UTC)."""
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m")

    def record_spend(self, amount_usd: float, timestamp: float) -> None:
        """Record a spending event."""
        day = self._day_key(timestamp)
        month = self._month_key(timestamp)
        self._daily_spend[day] = self._daily_spend.get(day, 0.0) + amount_usd
        self._monthly_spend[month] = self._monthly_spend.get(month, 0.0) + amount_usd

    def can_spend(self, amount_usd: float, timestamp: float) -> dict[str, Any]:
        """Check if spending amount_usd is within budget."""
        day = self._day_key(timestamp)
        month = self._month_key(timestamp)

        daily_spent = self._daily_spend.get(day, 0.0)
        monthly_spent = self._monthly_spend.get(month, 0.0)

        daily_remaining = self.config.daily_limit_usd - daily_spent
        monthly_remaining = self.config.monthly_limit_usd - monthly_spent

        if daily_spent + amount_usd > self.config.daily_limit_usd:
            return {
                "allowed": False,
                "reason": "daily_limit",
                "daily_remaining_usd": max(0.0, daily_remaining),
                "monthly_remaining_usd": max(0.0, monthly_remaining),
            }

        if monthly_spent + amount_usd > self.config.monthly_limit_usd:
            return {
                "allowed": False,
                "reason": "monthly_limit",
                "daily_remaining_usd": max(0.0, daily_remaining),
                "monthly_remaining_usd": max(0.0, monthly_remaining),
            }

        return {
            "allowed": True,
            "reason": "ok",
            "daily_remaining_usd": round(daily_remaining, 6),
            "monthly_remaining_usd": round(monthly_remaining, 6),
        }

    def get_spend(self, timestamp: float) -> dict[str, float]:
        """Return current daily and monthly spend."""
        day = self._day_key(timestamp)
        month = self._month_key(timestamp)
        return {
            "daily_usd": self._daily_spend.get(day, 0.0),
            "monthly_usd": self._monthly_spend.get(month, 0.0),
        }


# ---------------------------------------------------------------------------
# Solution 13: A/B Test Cost Comparator
# ---------------------------------------------------------------------------
def compare_ab_costs(
    group_a: list[UsageRecord],
    group_b: list[UsageRecord],
) -> dict[str, Any]:
    """
    Compare costs and performance between two A/B test groups.

    A/B testing different models or prompts is a core practice for
    optimizing cost and quality.  This comparator gives you the data
    needed to make informed switching decisions.
    """
    def _summarize(records: list[UsageRecord]) -> dict[str, Any]:
        total_cost = sum(r.cost_usd for r in records)
        total_latency = sum(r.latency_ms for r in records)
        count = len(records)
        models = sorted(set(r.model for r in records))
        return {
            "total_cost_usd": total_cost,
            "avg_cost_per_request": total_cost / count if count else 0.0,
            "avg_latency_ms": total_latency / count if count else 0.0,
            "total_requests": count,
            "models_used": models,
        }

    summary_a = _summarize(group_a)
    summary_b = _summarize(group_b)

    # Compute percentage differences: (B - A) / A * 100
    cost_diff_pct = 0.0
    if summary_a["avg_cost_per_request"] > 0:
        cost_diff_pct = (
            (summary_b["avg_cost_per_request"] - summary_a["avg_cost_per_request"])
            / summary_a["avg_cost_per_request"]
            * 100
        )

    latency_diff_pct = 0.0
    if summary_a["avg_latency_ms"] > 0:
        latency_diff_pct = (
            (summary_b["avg_latency_ms"] - summary_a["avg_latency_ms"])
            / summary_a["avg_latency_ms"]
            * 100
        )

    # Recommendation logic
    b_cheaper = cost_diff_pct < 0
    a_cheaper = cost_diff_pct > 0
    b_faster = latency_diff_pct < 0
    a_faster = latency_diff_pct > 0
    b_not_slower = latency_diff_pct <= 0
    a_not_slower = latency_diff_pct >= 0

    recommendation = "no_difference"
    if a_cheaper and a_faster:
        recommendation = "group_a"
    elif b_cheaper and b_faster:
        recommendation = "group_b"
    elif cost_diff_pct >= 20 and a_not_slower:
        # B is >=20% more expensive, A is not slower -> recommend A
        recommendation = "group_a"
    elif cost_diff_pct <= -20 and b_not_slower:
        # B is >=20% cheaper, B is not slower -> recommend B
        recommendation = "group_b"

    return {
        "group_a": summary_a,
        "group_b": summary_b,
        "cost_difference_pct": round(cost_diff_pct, 2),
        "latency_difference_pct": round(latency_diff_pct, 2),
        "recommendation": recommendation,
    }


# ---------------------------------------------------------------------------
# Solution 14: Usage Report Generator
# ---------------------------------------------------------------------------
def generate_usage_report(
    records: list[UsageRecord],
    report_title: str = "LLM Usage Report",
) -> str:
    """
    Generate a plain-text usage report.

    Reports like this are sent to engineering leads and finance teams
    to track AI spending.  In production, you would also include
    charts and trend analysis.
    """
    if not records:
        return f"{report_title}\n\nNo usage records."

    lines: list[str] = []

    # 1. Title
    lines.append(report_title)
    lines.append("=" * len(report_title))
    lines.append("")

    # 2. Summary
    total_cost = sum(r.cost_usd for r in records)
    total_requests = len(records)
    timestamps = [r.timestamp for r in records]
    min_dt = datetime.fromtimestamp(min(timestamps), tz=timezone.utc)
    max_dt = datetime.fromtimestamp(max(timestamps), tz=timezone.utc)

    lines.append("Summary")
    lines.append("-" * 40)
    lines.append(f"Total Requests: {total_requests}")
    lines.append(f"Total Cost:     ${total_cost:.6f}")
    lines.append(f"Date Range:     {min_dt:%Y-%m-%d} to {max_dt:%Y-%m-%d}")
    lines.append("")

    # 3. Per-model breakdown
    by_model: dict[str, dict[str, Any]] = {}
    for rec in records:
        if rec.model not in by_model:
            by_model[rec.model] = {
                "requests": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
            }
        m = by_model[rec.model]
        m["requests"] += 1
        m["input_tokens"] += rec.input_tokens
        m["output_tokens"] += rec.output_tokens
        m["cost"] += rec.cost_usd

    lines.append("Per-Model Breakdown")
    lines.append("-" * 40)
    header = f"{'Model':<25} {'Reqs':>5} {'InTok':>8} {'OutTok':>8} {'Cost':>12}"
    lines.append(header)
    for model, data in sorted(by_model.items()):
        row = (
            f"{model:<25} {data['requests']:>5} "
            f"{data['input_tokens']:>8} {data['output_tokens']:>8} "
            f"${data['cost']:>10.6f}"
        )
        lines.append(row)
    lines.append("")

    # 4. Top 5 most expensive requests
    sorted_recs = sorted(records, key=lambda r: r.cost_usd, reverse=True)
    top5 = sorted_recs[:5]
    lines.append("Top 5 Most Expensive Requests")
    lines.append("-" * 40)
    for i, rec in enumerate(top5, 1):
        lines.append(
            f"  {i}. {rec.request_id} ({rec.model}) - "
            f"${rec.cost_usd:.6f} "
            f"[{rec.input_tokens}in/{rec.output_tokens}out]"
        )
    lines.append("")

    # 5. Average cost per request
    avg_cost = total_cost / total_requests
    lines.append(f"Average Cost Per Request: ${avg_cost:.6f}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Solution 15: Cost Anomaly Detection
# ---------------------------------------------------------------------------
def detect_cost_anomalies(
    records: list[UsageRecord],
    z_threshold: float = 2.0,
) -> list[dict[str, Any]]:
    """
    Detect anomalous API calls using z-score analysis.

    Z-score anomaly detection is a simple but effective method for
    catching runaway costs: a prompt injection that generates excessive
    output, a bug that sends the same request in a loop, or an
    unexpected model upgrade that changes pricing.
    """
    if not records:
        return []

    costs = [r.cost_usd for r in records]
    n = len(costs)
    mean = sum(costs) / n

    # Calculate standard deviation
    variance = sum((c - mean) ** 2 for c in costs) / n
    std_dev = math.sqrt(variance)

    # If all costs are identical, no anomalies
    if std_dev == 0:
        return []

    anomalies: list[dict[str, Any]] = []
    for rec in records:
        z_score = (rec.cost_usd - mean) / std_dev
        if abs(z_score) > z_threshold:
            severity = "critical" if abs(z_score) > 3.0 else "warning"
            anomalies.append({
                "request_id": rec.request_id,
                "model": rec.model,
                "cost_usd": rec.cost_usd,
                "z_score": round(z_score, 2),
                "severity": severity,
            })

    # Sort by absolute z-score descending
    anomalies.sort(key=lambda a: abs(a["z_score"]), reverse=True)
    return anomalies


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import datetime as _dt

    # -- Solution 1: Token Counter --
    tokens = count_tokens("Hello, world!", "claude-3-haiku")
    assert isinstance(tokens, int) and tokens > 0
    # "Hello, world!" is 13 chars, Claude ratio 3.5 -> ~3 tokens
    assert tokens == 3
    assert count_tokens("", "gpt-4o") == 0
    # Single character should still be 1
    assert count_tokens("A", "gpt-4o") == 1
    print("  [OK] Solution 1: Token Counter")

    # -- Solution 2: Cost Calculator --
    cost = calculate_cost("claude-3-haiku", 1000, 1000)
    expected = (1000 / 1_000_000) * 0.25 + (1000 / 1_000_000) * 1.25
    assert abs(cost - expected) < 1e-9
    assert calculate_cost("unknown-model", 100, 100) == 0.0
    print("  [OK] Solution 2: Cost Calculator")

    # -- Solution 3: Pre-Call Cost Estimator --
    est = estimate_call_cost("Tell me about Python", "gpt-4o", 300)
    assert est["model"] == "gpt-4o"
    assert est["estimated_input_tokens"] > 0
    assert est["expected_output_tokens"] == 300
    assert est["estimated_cost_usd"] > 0
    print("  [OK] Solution 3: Pre-Call Cost Estimator")

    # -- Solution 4: Model Selector --
    model = select_model("Summarize this short text")
    assert model in MODEL_PRICING
    # Vision-required task
    model_v = select_model("Analyze this image in detail", require_vision=True)
    assert model_v in ("claude-3-5-sonnet", "claude-3-opus", "gpt-4o")
    # Very tight budget -> cheapest or no_model_available
    model_cheap = select_model("Hello", max_cost_usd=0.0000001)
    assert model_cheap == "no_model_available"
    print("  [OK] Solution 4: Model Selector")

    # -- Solution 5: Cost-Aware Router --
    msgs = [{"role": "user", "content": "Hello, how are you?"}]
    route = route_request(msgs, budget_remaining_usd=0.01, priority="cost")
    assert "model" in route and "estimated_cost_usd" in route
    assert route["model"] != "none"

    route_q = route_request(msgs, budget_remaining_usd=10.0, priority="quality")
    assert route_q["model"] == "claude-3-opus"  # highest quality

    route_broke = route_request(msgs, budget_remaining_usd=0.0, priority="cost")
    assert route_broke["model"] == "none"
    print("  [OK] Solution 5: Cost-Aware Router")

    # -- Solution 6: Prompt Optimizer --
    original = "  Please   kindly   summarize the text. Summarize the text.  "
    result = optimize_prompt(original)
    assert result["optimized_tokens"] <= result["original_tokens"]
    assert result["savings_pct"] >= 0
    assert "please" not in result["optimized_prompt"].lower()
    assert "kindly" not in result["optimized_prompt"].lower()
    print("  [OK] Solution 6: Prompt Optimizer")

    # -- Solution 7: Prompt Cache --
    cache = PromptCache(max_size=2)
    assert cache.get("test prompt") is None
    cache.put("test prompt", "test response", 10, 20)
    assert cache.get("test prompt") == "test response"
    s = cache.stats()
    assert s["hits"] == 1 and s["misses"] == 1 and s["saved_tokens"] == 30
    assert s["entries"] == 1

    # Test eviction
    cache.put("prompt2", "resp2", 5, 5)
    cache.put("prompt3", "resp3", 5, 5)  # should evict "test prompt"
    assert cache.get("test prompt") is None  # evicted
    assert cache.stats()["entries"] == 2
    print("  [OK] Solution 7: Prompt Cache")

    # -- Solution 8: Latency Profiler --
    recs = [
        UsageRecord("r1", "gpt-4o", 100, 50, 120.0, time.time()),
        UsageRecord("r2", "gpt-4o", 200, 80, 250.0, time.time()),
        UsageRecord("r3", "claude-3-haiku", 50, 30, 60.0, time.time()),
    ]
    stats = profile_latencies(recs)
    assert stats["overall"]["count"] == 3
    assert "gpt-4o" in stats["per_model"]
    assert "claude-3-haiku" in stats["per_model"]
    assert stats["per_model"]["gpt-4o"]["count"] == 2
    print("  [OK] Solution 8: Latency Profiler")

    # -- Solution 9: Batch Processor --
    prompts = ["Short prompt"] * 10
    batches = plan_batch(prompts, "gpt-4o-mini", max_batch_cost_usd=0.01)
    assert len(batches) >= 1
    # All prompts accounted for
    all_indices = []
    for b in batches:
        all_indices.extend(b["prompt_indices"])
    assert sorted(all_indices) == list(range(10))
    print("  [OK] Solution 9: Batch Processor")

    # -- Solution 10: Rate Limiter --
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1.0)
    assert limiter.try_acquire(3) is True
    assert limiter.try_acquire(3) is False
    # Still have 2 tokens, so wait_time for 1 token is 0
    assert limiter.try_acquire(2) is True
    # Now bucket is empty, wait_time should be > 0
    assert limiter.wait_time() > 0
    limiter.reset()
    assert limiter.try_acquire(5) is True
    assert limiter.try_acquire(1) is False
    print("  [OK] Solution 10: Rate Limiter")

    # -- Solution 11: Dashboard Aggregator --
    ts_base = _dt.datetime(2025, 6, 1, tzinfo=_dt.timezone.utc).timestamp()
    dash_recs = [
        UsageRecord("d1", "gpt-4o", 500, 200, 150.0, ts_base, 0.0040),
        UsageRecord("d2", "gpt-4o", 300, 100, 100.0, ts_base + 3600, 0.0020),
        UsageRecord("d3", "claude-3-haiku", 100, 50, 40.0, ts_base + 86400, 0.0001),
    ]
    dash = aggregate_dashboard_data(dash_recs)
    assert dash["total_requests"] == 3
    assert abs(dash["total_cost_usd"] - 0.0061) < 1e-6
    assert dash["total_input_tokens"] == 900
    assert dash["total_output_tokens"] == 350
    assert "gpt-4o" in dash["by_model"]
    assert len(dash["cost_trend"]) == 2  # 2 distinct days
    assert dash["cost_trend"][0]["date"] < dash["cost_trend"][1]["date"]
    print("  [OK] Solution 11: Dashboard Aggregator")

    # -- Solution 12: Budget Enforcer --
    cfg = BudgetConfig(daily_limit_usd=1.0, monthly_limit_usd=10.0)
    enforcer = BudgetEnforcer(cfg)
    enforcer.record_spend(0.50, ts_base)
    result = enforcer.can_spend(0.40, ts_base)
    assert result["allowed"] is True
    assert result["reason"] == "ok"

    result2 = enforcer.can_spend(0.60, ts_base)
    assert result2["allowed"] is False
    assert result2["reason"] == "daily_limit"

    spend = enforcer.get_spend(ts_base)
    assert spend["daily_usd"] == 0.50
    print("  [OK] Solution 12: Budget Enforcer")

    # -- Solution 13: A/B Comparator --
    group_a = [
        UsageRecord("a1", "gpt-4o", 100, 50, 200.0, ts_base, 0.0013),
        UsageRecord("a2", "gpt-4o", 150, 80, 250.0, ts_base, 0.0020),
    ]
    group_b = [
        UsageRecord("b1", "claude-3-haiku", 100, 50, 80.0, ts_base, 0.0001),
        UsageRecord("b2", "claude-3-haiku", 150, 80, 90.0, ts_base, 0.0002),
    ]
    comp = compare_ab_costs(group_a, group_b)
    assert comp["cost_difference_pct"] < 0  # B is cheaper
    assert comp["latency_difference_pct"] < 0  # B is faster
    assert comp["recommendation"] == "group_b"
    assert comp["group_a"]["total_requests"] == 2
    assert comp["group_b"]["models_used"] == ["claude-3-haiku"]
    print("  [OK] Solution 13: A/B Comparator")

    # -- Solution 14: Usage Report --
    report = generate_usage_report(dash_recs, "Test Report")
    assert "Test Report" in report
    assert "gpt-4o" in report
    assert "Summary" in report
    assert len(report) > 100
    print("  [OK] Solution 14: Usage Report")

    # -- Solution 15: Anomaly Detection --
    anomaly_recs = [
        UsageRecord(f"n{i}", "gpt-4o", 100, 50, 100.0, ts_base, 0.001)
        for i in range(20)
    ]
    # Inject one outlier with very high cost
    anomaly_recs.append(
        UsageRecord("outlier", "gpt-4o", 10000, 5000, 500.0, ts_base, 0.50)
    )
    anomalies = detect_cost_anomalies(anomaly_recs)
    assert len(anomalies) >= 1
    assert anomalies[0]["request_id"] == "outlier"
    assert anomalies[0]["severity"] == "critical"
    assert anomalies[0]["z_score"] > 2.0

    # No anomalies when all costs are identical
    uniform_recs = [
        UsageRecord(f"u{i}", "gpt-4o", 100, 50, 100.0, ts_base, 0.001)
        for i in range(10)
    ]
    assert detect_cost_anomalies(uniform_recs) == []
    print("  [OK] Solution 15: Anomaly Detection")

    print("\nAll solutions passed!")
