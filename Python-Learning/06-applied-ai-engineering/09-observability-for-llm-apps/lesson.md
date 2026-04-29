# Module 09: Observability for LLM Applications

## Why This Module Matters for Interviews

Observability is the first thing that separates a prototype from a production LLM system. In solutions engineer and applied AI engineer interviews, you will face questions like:

- "A customer reports that your LLM integration is giving worse answers than last week. How do you investigate?"
- "How would you design a monitoring system for an LLM-powered application serving 10,000 customers?"
- "Walk me through how you would debug a RAG pipeline that is returning irrelevant results."
- "How do you track and control LLM API costs across multiple teams?"

This module goes beyond the general observability concepts covered in Phase 7 (Prometheus, health checks, basic OpenTelemetry) and focuses specifically on the unique challenges of monitoring non-deterministic AI systems in production.

---

## 1. Why LLM Observability is Different

### The Non-Determinism Problem

Traditional software is deterministic: given the same input, you get the same output. A REST API that returns user data will always return the same JSON for the same user ID. This makes monitoring straightforward -- you track status codes, latency, and error rates.

LLM applications break this assumption fundamentally. The same prompt can produce different outputs across calls, even with `temperature=0` (due to floating-point non-determinism in GPU operations). This means traditional observability tools are necessary but insufficient.

```python
import anthropic
import hashlib

client = anthropic.Anthropic()

# Same prompt, potentially different outputs
results = []
for i in range(3):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        temperature=0,
        messages=[{"role": "user", "content": "Summarize the benefits of Python in one sentence."}]
    )
    text = response.content[0].text
    results.append(text)
    print(f"Run {i+1}: {text[:80]}...")
    print(f"  Hash: {hashlib.sha256(text.encode()).hexdigest()[:16]}")

# Even with temperature=0, outputs may differ slightly
unique_outputs = len(set(results))
print(f"\nUnique outputs: {unique_outputs} out of {len(results)}")
```

### Quality vs. Traditional Metrics

In traditional systems, "working" means returning a 200 status code with valid data. In LLM systems, you need to answer a harder question: **was the output good?**

| Dimension | Traditional API | LLM Application |
|-----------|----------------|-----------------|
| Correctness | Schema validation, status codes | Factual accuracy, relevance, coherence |
| Performance | Latency, throughput | Latency + output quality trade-offs |
| Errors | Exceptions, HTTP errors | Silent failures (plausible but wrong answers) |
| Cost | Compute time | Token consumption (variable per request) |
| Debugging | Stack traces, logs | Prompt analysis, context window inspection |
| Regression | Unit tests catch changes | Same test, different (valid) outputs |

### The Observability Stack for LLM Apps

A complete LLM observability stack requires layers beyond traditional monitoring:

```
┌─────────────────────────────────────────────┐
│          Business Metrics Dashboard          │
│   (cost per customer, ROI, usage trends)     │
├─────────────────────────────────────────────┤
│           Quality Monitoring Layer           │
│  (output scoring, drift detection, evals)    │
├─────────────────────────────────────────────┤
│          LLM-Specific Telemetry              │
│  (tokens, prompts, completions, model info)  │
├─────────────────────────────────────────────┤
│        Standard Observability (OTel)         │
│     (traces, metrics, logs, spans)           │
├─────────────────────────────────────────────┤
│            Infrastructure                    │
│    (CPU, memory, network, GPU utilization)   │
└─────────────────────────────────────────────┘
```

> **Swift Developer Note:** In iOS development, you have a clear hierarchy: `os.log` for logging, Instruments for profiling, MetricKit for aggregated device metrics, and Xcode Organizer for crash/energy reports. LLM observability is analogous but adds layers for prompt/completion logging, token economics, and output quality -- dimensions that have no parallel in mobile development.

---

## 2. LLM Request/Response Logging

### What to Capture

Every LLM API call should produce a structured log record containing enough information to reconstruct, analyze, and debug the interaction.

```python
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional
import json
import uuid


@dataclass
class LLMRequestLog:
    """Structured log record for a single LLM API call."""
    # Identification
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

    # Timing
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    duration_ms: Optional[float] = None

    # Request details
    model: str = ""
    provider: str = ""  # anthropic, openai, cohere, etc.
    temperature: float = 1.0
    max_tokens: int = 0
    top_p: Optional[float] = None
    system_prompt_hash: Optional[str] = None  # Hash for privacy

    # Messages (may be redacted)
    prompt_messages: Optional[list] = None
    prompt_token_count: int = 0

    # Response details
    completion_text: Optional[str] = None
    completion_token_count: int = 0
    total_tokens: int = 0
    finish_reason: Optional[str] = None  # end_turn, max_tokens, stop_sequence

    # Cost
    estimated_cost_usd: float = 0.0

    # Quality signals
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    use_case: Optional[str] = None  # e.g., "customer_support", "code_gen"

    # Error handling
    error: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0

    # Feature flags / metadata
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)
```

### Structured Logging with Logfire

Pydantic Logfire is a modern observability platform built on OpenTelemetry that integrates naturally with Python AI/ML applications. It provides structured logging, tracing, and metrics in a single tool.

```python
import logfire

# Configure logfire (typically done once at app startup)
logfire.configure(
    service_name="llm-application",
    service_version="1.2.0",
    environment="production",
)


def call_llm_with_logging(
    client,
    model: str,
    messages: list[dict],
    temperature: float = 1.0,
    max_tokens: int = 1024,
    user_id: str | None = None,
    use_case: str = "general",
) -> str:
    """Call an LLM and log the full interaction with logfire."""

    with logfire.span(
        "llm_call",
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        user_id=user_id,
        use_case=use_case,
        message_count=len(messages),
    ) as span:
        import time
        start = time.perf_counter()

        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            duration_ms = (time.perf_counter() - start) * 1000

            # Log structured data about the response
            span.set_attribute("duration_ms", duration_ms)
            span.set_attribute("input_tokens", response.usage.input_tokens)
            span.set_attribute("output_tokens", response.usage.output_tokens)
            span.set_attribute("total_tokens",
                               response.usage.input_tokens + response.usage.output_tokens)
            span.set_attribute("finish_reason", response.stop_reason)

            logfire.info(
                "LLM call completed",
                model=model,
                duration_ms=round(duration_ms, 2),
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                finish_reason=response.stop_reason,
                user_id=user_id,
                use_case=use_case,
            )

            return response.content[0].text

        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            span.set_attribute("error", True)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))

            logfire.error(
                "LLM call failed",
                model=model,
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=user_id,
            )
            raise
```

### Privacy-Aware Logging

Logging prompts and completions is essential for debugging but creates privacy risks. Implement a layered approach:

```python
import hashlib
import re
from enum import Enum


class LogLevel(Enum):
    """Controls how much prompt/completion data is logged."""
    FULL = "full"           # Log everything (dev/staging only)
    REDACTED = "redacted"   # Redact PII patterns
    HASHED = "hashed"       # Log hashes only (for deduplication)
    MINIMAL = "minimal"     # Log metadata only, no content


# Common PII patterns to redact
PII_PATTERNS = [
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
    (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]'),
    (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
    (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CREDIT_CARD]'),
    (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_ADDRESS]'),
]


def redact_pii(text: str) -> str:
    """Remove common PII patterns from text."""
    redacted = text
    for pattern, replacement in PII_PATTERNS:
        redacted = re.sub(pattern, replacement, redacted)
    return redacted


def prepare_log_content(
    text: str,
    log_level: LogLevel,
    max_length: int = 500,
) -> dict:
    """Prepare text content for logging based on privacy level."""
    if log_level == LogLevel.MINIMAL:
        return {
            "content_logged": False,
            "content_length": len(text),
        }

    if log_level == LogLevel.HASHED:
        return {
            "content_logged": False,
            "content_hash": hashlib.sha256(text.encode()).hexdigest(),
            "content_length": len(text),
        }

    if log_level == LogLevel.REDACTED:
        cleaned = redact_pii(text)
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + f"... [truncated, {len(text)} chars total]"
        return {
            "content_logged": True,
            "content_redacted": True,
            "content": cleaned,
            "content_length": len(text),
        }

    # FULL logging
    content = text
    if len(content) > max_length:
        content = content[:max_length] + f"... [truncated, {len(text)} chars total]"
    return {
        "content_logged": True,
        "content_redacted": False,
        "content": content,
        "content_length": len(text),
    }


# Usage in production
import logfire

LOG_LEVEL = LogLevel.REDACTED  # Set via environment variable

def log_llm_interaction(
    prompt: str,
    completion: str,
    metadata: dict,
):
    """Log an LLM interaction with privacy controls."""
    prompt_log = prepare_log_content(prompt, LOG_LEVEL)
    completion_log = prepare_log_content(completion, LOG_LEVEL)

    logfire.info(
        "llm_interaction",
        prompt=prompt_log,
        completion=completion_log,
        **metadata,
    )
```

> **Swift Developer Note:** This is analogous to how you handle `os.log` privacy in iOS using `%{public}@` and `%{private}@` format specifiers. In Swift, the OS enforces log redaction at the system level. In Python LLM applications, you must build this redaction layer yourself, making it both more flexible and more error-prone.

---

## 3. Token Usage Tracking

### Per-Request Token Tracking

Token usage directly translates to cost. Every request must be tracked at a granular level.

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import logfire


# Pricing per 1M tokens (example rates, check current provider pricing)
PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


@dataclass
class TokenUsageRecord:
    """Records token usage for a single LLM call."""
    request_id: str
    timestamp: datetime
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    customer_id: Optional[str] = None
    use_case: Optional[str] = None
    cached_tokens: int = 0  # Anthropic prompt caching

    @classmethod
    def from_response(
        cls,
        request_id: str,
        model: str,
        provider: str,
        usage: dict,
        customer_id: str | None = None,
        use_case: str | None = None,
    ) -> "TokenUsageRecord":
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        cached_tokens = usage.get("cache_read_input_tokens", 0)

        # Calculate cost
        pricing = PRICING.get(model, {"input": 0, "output": 0})
        # Cached tokens are typically 90% cheaper
        regular_input = input_tokens - cached_tokens
        cost = (
            (regular_input / 1_000_000) * pricing["input"]
            + (cached_tokens / 1_000_000) * pricing["input"] * 0.1
            + (output_tokens / 1_000_000) * pricing["output"]
        )

        return cls(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc),
            model=model,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            estimated_cost_usd=round(cost, 6),
            customer_id=customer_id,
            use_case=use_case,
            cached_tokens=cached_tokens,
        )
```

### Per-Customer Aggregation and Budget Enforcement

In multi-tenant applications, you need to track and limit usage per customer.

```python
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional
import logfire


class CustomerUsageTracker:
    """Tracks and enforces token usage budgets per customer."""

    def __init__(self, default_monthly_budget_usd: float = 100.0):
        self.default_monthly_budget = default_monthly_budget_usd
        # In production, use Redis or a database instead of in-memory dicts
        self._usage: dict[str, list[TokenUsageRecord]] = defaultdict(list)
        self._budgets: dict[str, float] = {}
        self._alerts_sent: dict[str, set[int]] = defaultdict(set)

    def set_budget(self, customer_id: str, monthly_budget_usd: float):
        """Set a custom monthly budget for a customer."""
        self._budgets[customer_id] = monthly_budget_usd

    def get_budget(self, customer_id: str) -> float:
        """Get the monthly budget for a customer."""
        return self._budgets.get(customer_id, self.default_monthly_budget)

    def record_usage(self, record: TokenUsageRecord):
        """Record a token usage event and check budget."""
        if record.customer_id:
            self._usage[record.customer_id].append(record)

            logfire.info(
                "token_usage_recorded",
                customer_id=record.customer_id,
                model=record.model,
                input_tokens=record.input_tokens,
                output_tokens=record.output_tokens,
                cost_usd=record.estimated_cost_usd,
            )

            # Check budget thresholds
            self._check_budget_alerts(record.customer_id)

    def get_monthly_usage(
        self,
        customer_id: str,
        year: int | None = None,
        month: int | None = None,
    ) -> dict:
        """Get aggregated usage for a customer in a given month."""
        now = datetime.now(timezone.utc)
        target_year = year or now.year
        target_month = month or now.month

        records = [
            r for r in self._usage[customer_id]
            if r.timestamp.year == target_year and r.timestamp.month == target_month
        ]

        total_input = sum(r.input_tokens for r in records)
        total_output = sum(r.output_tokens for r in records)
        total_cost = sum(r.estimated_cost_usd for r in records)

        # Break down by model
        by_model: dict[str, dict] = defaultdict(
            lambda: {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "requests": 0}
        )
        for r in records:
            by_model[r.model]["input_tokens"] += r.input_tokens
            by_model[r.model]["output_tokens"] += r.output_tokens
            by_model[r.model]["cost_usd"] += r.estimated_cost_usd
            by_model[r.model]["requests"] += 1

        budget = self.get_budget(customer_id)

        return {
            "customer_id": customer_id,
            "period": f"{target_year}-{target_month:02d}",
            "total_requests": len(records),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cost_usd": round(total_cost, 4),
            "budget_usd": budget,
            "budget_used_pct": round((total_cost / budget) * 100, 1) if budget > 0 else 0,
            "by_model": dict(by_model),
        }

    def check_budget(self, customer_id: str) -> tuple[bool, float]:
        """Check if a customer is within budget. Returns (allowed, remaining_usd)."""
        usage = self.get_monthly_usage(customer_id)
        budget = self.get_budget(customer_id)
        remaining = budget - usage["total_cost_usd"]
        return remaining > 0, max(0, remaining)

    def _check_budget_alerts(self, customer_id: str):
        """Send alerts at budget thresholds."""
        usage = self.get_monthly_usage(customer_id)
        pct = usage["budget_used_pct"]
        month_key = usage["period"]

        alert_thresholds = [50, 75, 90, 100]

        for threshold in alert_thresholds:
            if pct >= threshold and threshold not in self._alerts_sent.get(
                f"{customer_id}:{month_key}", set()
            ):
                self._alerts_sent[f"{customer_id}:{month_key}"].add(threshold)

                level = "warn" if threshold < 100 else "error"
                log_fn = logfire.warn if threshold < 100 else logfire.error

                log_fn(
                    "budget_threshold_reached",
                    customer_id=customer_id,
                    threshold_pct=threshold,
                    current_pct=pct,
                    cost_usd=usage["total_cost_usd"],
                    budget_usd=usage["budget_usd"],
                )


# Usage
tracker = CustomerUsageTracker(default_monthly_budget_usd=50.0)
tracker.set_budget("enterprise_customer_1", 500.0)
tracker.set_budget("startup_customer_2", 25.0)
```

### Usage Anomaly Detection

Detect unusual token consumption patterns that might indicate prompt injection, runaway loops, or abuse.

```python
import statistics
from collections import deque


class UsageAnomalyDetector:
    """Detects anomalous token usage patterns using statistical methods."""

    def __init__(
        self,
        window_size: int = 100,
        z_score_threshold: float = 3.0,
    ):
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        # Rolling windows per customer
        self._windows: dict[str, deque[float]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )

    def check_and_record(
        self,
        customer_id: str,
        total_tokens: int,
        cost_usd: float,
    ) -> dict:
        """Record a data point and check for anomalies."""
        window = self._windows[customer_id]
        anomalies = []

        if len(window) >= 10:  # Need minimum samples
            mean = statistics.mean(window)
            stdev = statistics.stdev(window)

            if stdev > 0:
                z_score = (total_tokens - mean) / stdev

                if abs(z_score) > self.z_score_threshold:
                    anomaly = {
                        "type": "token_usage_spike" if z_score > 0 else "token_usage_drop",
                        "z_score": round(z_score, 2),
                        "value": total_tokens,
                        "mean": round(mean, 1),
                        "stdev": round(stdev, 1),
                        "threshold": self.z_score_threshold,
                    }
                    anomalies.append(anomaly)

                    logfire.warn(
                        "usage_anomaly_detected",
                        customer_id=customer_id,
                        **anomaly,
                    )

        window.append(total_tokens)

        return {
            "is_anomalous": len(anomalies) > 0,
            "anomalies": anomalies,
            "window_size": len(window),
        }
```

> **Swift Developer Note:** In iOS, you track resource usage through MetricKit's `MXAppRunTimeMetric` and `MXCellularConditionMetric`. The concept of per-customer budget enforcement has no iOS equivalent -- it is a server-side concern unique to multi-tenant SaaS. However, the statistical anomaly detection approach (rolling windows, z-scores) is conceptually similar to how Xcode Organizer flags performance regressions across app versions.

---

## 4. Quality Monitoring

### The Quality Challenge

An LLM endpoint can return HTTP 200 with perfectly structured JSON while giving a completely wrong answer. Quality monitoring bridges this gap.

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import logfire


class QualityDimension(Enum):
    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    COHERENCE = "coherence"
    HELPFULNESS = "helpfulness"
    SAFETY = "safety"
    GROUNDEDNESS = "groundedness"  # For RAG: is it grounded in sources?


@dataclass
class QualityScore:
    """A quality assessment for a single LLM response."""
    request_id: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    dimension: QualityDimension = QualityDimension.RELEVANCE
    score: float = 0.0  # 0.0 to 1.0
    source: str = ""  # "automated", "user_feedback", "llm_judge", "human_review"
    details: Optional[str] = None
    evaluator_model: Optional[str] = None  # If LLM-as-judge


class QualityMonitor:
    """Tracks output quality over time and detects degradation."""

    def __init__(self, min_samples_for_alert: int = 50):
        self.min_samples = min_samples_for_alert
        self._scores: dict[str, list[QualityScore]] = defaultdict(list)
        self._baselines: dict[str, float] = {}

    def record_score(self, score: QualityScore, use_case: str = "default"):
        """Record a quality score and check for degradation."""
        key = f"{use_case}:{score.dimension.value}"
        self._scores[key].append(score)

        logfire.info(
            "quality_score_recorded",
            request_id=score.request_id,
            dimension=score.dimension.value,
            score=score.score,
            source=score.source,
            use_case=use_case,
        )

        # Check for quality drift
        self._check_quality_drift(key)

    def set_baseline(self, use_case: str, dimension: QualityDimension, baseline: float):
        """Set an expected quality baseline for drift detection."""
        key = f"{use_case}:{dimension.value}"
        self._baselines[key] = baseline

    def _check_quality_drift(self, key: str):
        """Detect if quality has drifted from baseline."""
        scores = self._scores[key]
        if len(scores) < self.min_samples:
            return

        baseline = self._baselines.get(key)
        if baseline is None:
            return

        # Compare recent scores to baseline
        recent = scores[-self.min_samples:]
        recent_mean = statistics.mean([s.score for s in recent])
        drift = recent_mean - baseline

        if drift < -0.1:  # More than 10% degradation
            logfire.error(
                "quality_drift_detected",
                key=key,
                baseline=baseline,
                current_mean=round(recent_mean, 3),
                drift=round(drift, 3),
                sample_size=len(recent),
            )

    def get_quality_report(self, use_case: str = "default") -> dict:
        """Generate a quality report for a use case."""
        report = {}
        for dim in QualityDimension:
            key = f"{use_case}:{dim.value}"
            scores = self._scores.get(key, [])
            if not scores:
                continue

            values = [s.score for s in scores]
            recent_values = [s.score for s in scores[-50:]]

            report[dim.value] = {
                "total_samples": len(scores),
                "all_time_mean": round(statistics.mean(values), 3),
                "recent_mean": round(statistics.mean(recent_values), 3) if recent_values else None,
                "all_time_stdev": round(statistics.stdev(values), 3) if len(values) > 1 else 0,
                "min": round(min(values), 3),
                "max": round(max(values), 3),
                "baseline": self._baselines.get(key),
            }

        return report
```

### LLM-as-Judge for Automated Quality Scoring

Use a separate LLM call to evaluate the quality of your primary LLM's output. This is a common pattern in production systems.

```python
import json
from typing import Optional
import anthropic


JUDGE_SYSTEM_PROMPT = """You are a quality evaluator for AI-generated responses.
Given a user query and an AI response, evaluate the response on these dimensions:

1. relevance (0-1): Does the response address the user's question?
2. accuracy (0-1): Is the information factually correct?
3. coherence (0-1): Is the response well-structured and easy to understand?
4. helpfulness (0-1): Does the response actually help the user accomplish their goal?

Respond with ONLY a JSON object, no other text:
{
    "relevance": 0.0,
    "accuracy": 0.0,
    "coherence": 0.0,
    "helpfulness": 0.0,
    "explanation": "Brief explanation of scores"
}"""


async def evaluate_response_quality(
    client: anthropic.AsyncAnthropic,
    user_query: str,
    ai_response: str,
    context: Optional[str] = None,
) -> dict:
    """Use an LLM to judge the quality of another LLM's response."""

    eval_prompt = f"User Query: {user_query}\n\nAI Response: {ai_response}"
    if context:
        eval_prompt += f"\n\nContext provided to the AI: {context}"

    with logfire.span("llm_quality_evaluation") as span:
        response = await client.messages.create(
            model="claude-3-5-haiku-20241022",  # Use a fast, cheap model for evals
            max_tokens=300,
            temperature=0,
            system=JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": eval_prompt}],
        )

        try:
            scores = json.loads(response.content[0].text)
            span.set_attribute("evaluation_scores", scores)

            logfire.info(
                "quality_evaluation_complete",
                relevance=scores.get("relevance"),
                accuracy=scores.get("accuracy"),
                coherence=scores.get("coherence"),
                helpfulness=scores.get("helpfulness"),
            )

            return scores
        except json.JSONDecodeError:
            logfire.error(
                "quality_evaluation_parse_error",
                raw_response=response.content[0].text[:200],
            )
            return {}


# Integration into request pipeline
async def handle_request_with_quality_check(
    client: anthropic.AsyncAnthropic,
    user_query: str,
    quality_monitor: QualityMonitor,
    sample_rate: float = 0.1,  # Evaluate 10% of requests
):
    """Process a request and optionally evaluate quality."""
    import random
    import uuid

    request_id = str(uuid.uuid4())

    # Primary LLM call
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_query}],
    )
    completion = response.content[0].text

    # Sample-based quality evaluation (to control costs)
    if random.random() < sample_rate:
        scores = await evaluate_response_quality(client, user_query, completion)

        for dim_name, score_value in scores.items():
            if dim_name == "explanation":
                continue
            try:
                dim = QualityDimension(dim_name)
                quality_monitor.record_score(
                    QualityScore(
                        request_id=request_id,
                        dimension=dim,
                        score=score_value,
                        source="llm_judge",
                        evaluator_model="claude-3-5-haiku-20241022",
                    )
                )
            except ValueError:
                pass  # Unknown dimension

    return completion
```

### User Feedback Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class FeedbackRequest(BaseModel):
    request_id: str
    rating: int = Field(ge=1, le=5, description="1-5 star rating")
    feedback_text: str | None = None
    categories: list[str] = Field(
        default_factory=list,
        description="e.g., ['inaccurate', 'unhelpful', 'too_verbose']",
    )


@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Endpoint for users to submit quality feedback on LLM responses."""
    # Normalize rating to 0-1 scale
    normalized_score = (feedback.rating - 1) / 4.0

    logfire.info(
        "user_feedback_received",
        request_id=feedback.request_id,
        rating=feedback.rating,
        normalized_score=normalized_score,
        categories=feedback.categories,
        has_text=feedback.feedback_text is not None,
    )

    # Record as quality score
    quality_monitor.record_score(
        QualityScore(
            request_id=feedback.request_id,
            dimension=QualityDimension.HELPFULNESS,
            score=normalized_score,
            source="user_feedback",
            details=feedback.feedback_text,
        )
    )

    # Flag very negative feedback for human review
    if feedback.rating <= 2:
        logfire.warn(
            "negative_feedback_flagged",
            request_id=feedback.request_id,
            rating=feedback.rating,
            categories=feedback.categories,
        )

    return {"status": "recorded", "request_id": feedback.request_id}
```

---

## 5. Debugging LLM Applications

### Tracing Multi-Step Chains

LLM applications often involve multiple steps: retrieval, prompt construction, LLM call, post-processing. Tracing each step is critical for debugging.

```python
import logfire
import time
from typing import Any


class TracedLLMPipeline:
    """A multi-step LLM pipeline with full observability."""

    def __init__(self, client, retriever, model: str = "claude-sonnet-4-20250514"):
        self.client = client
        self.retriever = retriever
        self.model = model

    async def run(self, query: str, user_id: str | None = None) -> dict:
        """Execute the full RAG pipeline with tracing."""

        with logfire.span(
            "rag_pipeline",
            query=query[:200],
            user_id=user_id,
        ) as pipeline_span:

            # Step 1: Query understanding
            with logfire.span("query_understanding") as span:
                processed_query = await self._process_query(query)
                span.set_attribute("original_query", query[:200])
                span.set_attribute("processed_query", processed_query[:200])

            # Step 2: Retrieval
            with logfire.span("document_retrieval") as span:
                start = time.perf_counter()
                documents = await self._retrieve_documents(processed_query)
                retrieval_ms = (time.perf_counter() - start) * 1000

                span.set_attribute("num_documents", len(documents))
                span.set_attribute("retrieval_ms", round(retrieval_ms, 2))
                span.set_attribute(
                    "top_scores",
                    [round(d.get("score", 0), 3) for d in documents[:5]],
                )

                logfire.info(
                    "retrieval_complete",
                    num_documents=len(documents),
                    retrieval_ms=round(retrieval_ms, 2),
                    top_score=documents[0].get("score", 0) if documents else 0,
                )

            # Step 3: Context assembly
            with logfire.span("context_assembly") as span:
                context = self._build_context(documents)
                span.set_attribute("context_length_chars", len(context))
                span.set_attribute("context_num_sources", len(documents))

            # Step 4: Prompt construction
            with logfire.span("prompt_construction") as span:
                messages = self._build_messages(query, context)
                # Estimate token count (rough: 1 token ~ 4 chars for English)
                estimated_tokens = sum(len(m["content"]) for m in messages) // 4
                span.set_attribute("estimated_input_tokens", estimated_tokens)
                span.set_attribute("num_messages", len(messages))

            # Step 5: LLM call
            with logfire.span("llm_generation") as span:
                start = time.perf_counter()
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=messages,
                )
                generation_ms = (time.perf_counter() - start) * 1000

                span.set_attribute("model", self.model)
                span.set_attribute("generation_ms", round(generation_ms, 2))
                span.set_attribute("input_tokens", response.usage.input_tokens)
                span.set_attribute("output_tokens", response.usage.output_tokens)
                span.set_attribute("finish_reason", response.stop_reason)

            # Step 6: Post-processing
            with logfire.span("post_processing") as span:
                result = self._post_process(response.content[0].text, documents)
                span.set_attribute("has_citations", result.get("has_citations", False))

            # Summary attributes on the parent span
            pipeline_span.set_attribute("total_documents", len(documents))
            pipeline_span.set_attribute("generation_ms", round(generation_ms, 2))
            pipeline_span.set_attribute("input_tokens", response.usage.input_tokens)
            pipeline_span.set_attribute("output_tokens", response.usage.output_tokens)

            return result

    async def _process_query(self, query: str) -> str:
        """Expand or rephrase query for better retrieval."""
        return query  # Simplified -- real implementation might use LLM

    async def _retrieve_documents(self, query: str) -> list[dict]:
        """Retrieve relevant documents from vector store."""
        return await self.retriever.search(query, top_k=5)

    def _build_context(self, documents: list[dict]) -> str:
        """Assemble retrieved documents into context string."""
        parts = []
        for i, doc in enumerate(documents):
            parts.append(f"[Source {i+1}] {doc.get('content', '')}")
        return "\n\n".join(parts)

    def _build_messages(self, query: str, context: str) -> list[dict]:
        """Construct the prompt messages."""
        system = (
            "Answer the user's question based on the provided context. "
            "Cite sources using [Source N] format."
        )
        user_msg = f"Context:\n{context}\n\nQuestion: {query}"
        return [
            {"role": "user", "content": f"{system}\n\n{user_msg}"},
        ]

    def _post_process(self, text: str, documents: list[dict]) -> dict:
        """Post-process the LLM output."""
        return {
            "answer": text,
            "sources": [d.get("metadata", {}) for d in documents],
            "has_citations": "[Source" in text,
        }
```

### Debugging RAG Pipelines

RAG failures are notoriously hard to debug. Here is a diagnostic tool that identifies where in the pipeline things went wrong.

```python
import logfire
from dataclasses import dataclass
from enum import Enum


class RAGFailureMode(Enum):
    RETRIEVAL_MISS = "retrieval_miss"        # Relevant docs not retrieved
    RETRIEVAL_NOISE = "retrieval_noise"      # Too many irrelevant docs
    CONTEXT_OVERFLOW = "context_overflow"    # Too much context, key info buried
    GENERATION_HALLUCINATION = "hallucination"  # Answer not grounded in context
    GENERATION_REFUSAL = "refusal"           # Model refused to answer
    PROMPT_AMBIGUITY = "prompt_ambiguity"    # Query was ambiguous


@dataclass
class RAGDiagnostics:
    """Diagnostic data for a RAG pipeline execution."""
    query: str
    retrieved_docs: list[dict]
    context: str
    generated_answer: str
    expected_answer: str | None = None

    def analyze(self) -> dict:
        """Run diagnostic checks and identify potential failure modes."""
        issues = []

        # Check 1: Were any documents retrieved?
        if not self.retrieved_docs:
            issues.append({
                "mode": RAGFailureMode.RETRIEVAL_MISS.value,
                "severity": "critical",
                "detail": "No documents retrieved for query.",
            })

        # Check 2: Are retrieval scores too low?
        if self.retrieved_docs:
            scores = [d.get("score", 0) for d in self.retrieved_docs]
            avg_score = sum(scores) / len(scores)
            if avg_score < 0.5:
                issues.append({
                    "mode": RAGFailureMode.RETRIEVAL_NOISE.value,
                    "severity": "warning",
                    "detail": f"Low average retrieval score: {avg_score:.3f}",
                    "scores": [round(s, 3) for s in scores],
                })

        # Check 3: Context length
        context_chars = len(self.context)
        if context_chars > 50_000:
            issues.append({
                "mode": RAGFailureMode.CONTEXT_OVERFLOW.value,
                "severity": "warning",
                "detail": f"Context very long ({context_chars} chars). Key info may be buried.",
            })

        # Check 4: Did the model refuse to answer?
        refusal_phrases = [
            "I don't have enough information",
            "I cannot answer",
            "not mentioned in the context",
            "the provided context does not",
        ]
        if any(phrase.lower() in self.generated_answer.lower() for phrase in refusal_phrases):
            issues.append({
                "mode": RAGFailureMode.GENERATION_REFUSAL.value,
                "severity": "info",
                "detail": "Model indicated insufficient context.",
            })

        # Check 5: Basic groundedness check (citation presence)
        if self.retrieved_docs and "[Source" not in self.generated_answer:
            issues.append({
                "mode": RAGFailureMode.GENERATION_HALLUCINATION.value,
                "severity": "warning",
                "detail": "Response does not cite any sources.",
            })

        logfire.info(
            "rag_diagnostics_complete",
            query=self.query[:200],
            num_docs=len(self.retrieved_docs),
            context_length=context_chars,
            num_issues=len(issues),
            issue_modes=[i["mode"] for i in issues],
        )

        return {
            "query": self.query,
            "num_documents_retrieved": len(self.retrieved_docs),
            "context_length_chars": context_chars,
            "answer_length_chars": len(self.generated_answer),
            "issues": issues,
            "has_critical_issues": any(i["severity"] == "critical" for i in issues),
        }
```

### Prompt Debugging with Snapshot Comparison

When prompt changes cause regressions, you need to compare outputs across prompt versions.

```python
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


class PromptVersionTracker:
    """Track prompt versions and compare outputs across versions."""

    def __init__(self, storage_dir: str = "./prompt_versions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def register_prompt(
        self,
        prompt_name: str,
        system_prompt: str,
        user_template: str,
        metadata: dict | None = None,
    ) -> str:
        """Register a prompt version and return its hash."""
        content = f"{system_prompt}|||{user_template}"
        version_hash = hashlib.sha256(content.encode()).hexdigest()[:12]

        version_data = {
            "prompt_name": prompt_name,
            "version_hash": version_hash,
            "system_prompt": system_prompt,
            "user_template": user_template,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

        filepath = self.storage_dir / f"{prompt_name}_{version_hash}.json"
        filepath.write_text(json.dumps(version_data, indent=2))

        logfire.info(
            "prompt_version_registered",
            prompt_name=prompt_name,
            version_hash=version_hash,
        )

        return version_hash

    def compare_outputs(
        self,
        prompt_name: str,
        version_a: str,
        version_b: str,
        test_inputs: list[str],
        outputs_a: list[str],
        outputs_b: list[str],
    ) -> dict:
        """Compare outputs from two prompt versions on the same inputs."""
        comparisons = []
        for inp, out_a, out_b in zip(test_inputs, outputs_a, outputs_b):
            # Simple length and overlap comparison
            len_diff = len(out_b) - len(out_a)
            words_a = set(out_a.lower().split())
            words_b = set(out_b.lower().split())
            overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)

            comparisons.append({
                "input": inp[:100],
                "output_a_length": len(out_a),
                "output_b_length": len(out_b),
                "length_diff": len_diff,
                "word_overlap": round(overlap, 3),
            })

        avg_overlap = statistics.mean([c["word_overlap"] for c in comparisons])

        logfire.info(
            "prompt_version_comparison",
            prompt_name=prompt_name,
            version_a=version_a,
            version_b=version_b,
            num_test_cases=len(test_inputs),
            avg_word_overlap=round(avg_overlap, 3),
        )

        return {
            "prompt_name": prompt_name,
            "version_a": version_a,
            "version_b": version_b,
            "num_comparisons": len(comparisons),
            "avg_word_overlap": round(avg_overlap, 3),
            "comparisons": comparisons,
        }
```

> **Swift Developer Note:** Debugging in Xcode gives you breakpoints, LLDB, view hierarchy debugging, and Instruments time profiling. Debugging LLM apps is more like debugging a colleague's thought process than debugging code. The traces and spans above serve a role similar to `signpost` intervals in Instruments -- they let you see exactly how long each step took and what data flowed through it. The key difference is that the "output correctness" of an LLM step cannot be validated by a type system.

---

## 6. Performance Monitoring

### Latency Tracking with Percentiles

For LLM applications, latency is highly variable -- a short prompt might return in 500ms, while a complex reasoning task might take 30 seconds. Percentile tracking is essential.

```python
import time
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logfire


@dataclass
class LatencyRecord:
    timestamp: datetime
    duration_ms: float
    model: str
    input_tokens: int
    output_tokens: int
    use_case: str


class PerformanceMonitor:
    """Track LLM performance metrics with percentile analysis."""

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self._latencies: dict[str, deque[LatencyRecord]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        self._rate_limits: list[dict] = []

    def record_latency(self, record: LatencyRecord):
        """Record a latency measurement."""
        key = f"{record.model}:{record.use_case}"
        self._latencies[key].append(record)

        logfire.info(
            "llm_latency_recorded",
            model=record.model,
            use_case=record.use_case,
            duration_ms=round(record.duration_ms, 2),
            input_tokens=record.input_tokens,
            output_tokens=record.output_tokens,
            # Derived: tokens per second throughput
            tokens_per_second=round(
                record.output_tokens / (record.duration_ms / 1000), 1
            ) if record.duration_ms > 0 else 0,
        )

    def get_latency_percentiles(
        self,
        model: str,
        use_case: str = "default",
    ) -> dict:
        """Calculate latency percentiles for a model/use_case combination."""
        key = f"{model}:{use_case}"
        records = list(self._latencies[key])

        if not records:
            return {"error": "No data available"}

        durations = sorted([r.duration_ms for r in records])
        n = len(durations)

        def percentile(data: list[float], pct: float) -> float:
            idx = int(pct / 100 * (len(data) - 1))
            return round(data[idx], 2)

        result = {
            "model": model,
            "use_case": use_case,
            "sample_count": n,
            "p50": percentile(durations, 50),
            "p75": percentile(durations, 75),
            "p90": percentile(durations, 90),
            "p95": percentile(durations, 95),
            "p99": percentile(durations, 99),
            "min": round(min(durations), 2),
            "max": round(max(durations), 2),
            "mean": round(statistics.mean(durations), 2),
            "stdev": round(statistics.stdev(durations), 2) if n > 1 else 0,
        }

        logfire.info("latency_percentiles_calculated", **result)
        return result

    def get_throughput_stats(
        self,
        model: str,
        use_case: str = "default",
        window_minutes: int = 5,
    ) -> dict:
        """Calculate throughput (tokens/sec and requests/min) over a time window."""
        key = f"{model}:{use_case}"
        records = list(self._latencies[key])
        now = datetime.now(timezone.utc)

        from datetime import timedelta
        cutoff = now - timedelta(minutes=window_minutes)
        recent = [r for r in records if r.timestamp >= cutoff]

        if not recent:
            return {"error": "No data in time window"}

        total_output_tokens = sum(r.output_tokens for r in recent)
        total_input_tokens = sum(r.input_tokens for r in recent)
        total_duration_sec = sum(r.duration_ms for r in recent) / 1000

        return {
            "model": model,
            "use_case": use_case,
            "window_minutes": window_minutes,
            "request_count": len(recent),
            "requests_per_minute": round(len(recent) / window_minutes, 1),
            "avg_output_tokens_per_sec": round(
                total_output_tokens / total_duration_sec, 1
            ) if total_duration_sec > 0 else 0,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
        }


# Context manager for easy latency tracking
class track_llm_latency:
    """Context manager for tracking LLM call latency."""

    def __init__(
        self,
        monitor: PerformanceMonitor,
        model: str,
        use_case: str = "default",
    ):
        self.monitor = monitor
        self.model = model
        self.use_case = use_case
        self.start_time = 0.0
        self.response = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start_time) * 1000

        input_tokens = 0
        output_tokens = 0
        if self.response and hasattr(self.response, "usage"):
            input_tokens = self.response.usage.input_tokens
            output_tokens = self.response.usage.output_tokens

        self.monitor.record_latency(LatencyRecord(
            timestamp=datetime.now(timezone.utc),
            duration_ms=duration_ms,
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            use_case=self.use_case,
        ))


# Usage
perf_monitor = PerformanceMonitor()

async def monitored_llm_call(client, messages, model="claude-sonnet-4-20250514"):
    with track_llm_latency(perf_monitor, model, "customer_support") as tracker:
        response = await client.messages.create(
            model=model,
            max_tokens=1024,
            messages=messages,
        )
        tracker.response = response

    return response
```

### Rate Limit Monitoring

Track rate limit events to optimize your request patterns and plan capacity.

```python
from datetime import datetime, timezone
import logfire


class RateLimitTracker:
    """Track and analyze rate limit events from LLM providers."""

    def __init__(self):
        self._events: list[dict] = []

    def record_rate_limit(
        self,
        provider: str,
        model: str,
        retry_after_seconds: float | None = None,
        headers: dict | None = None,
    ):
        """Record a rate limit event."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "model": model,
            "retry_after": retry_after_seconds,
        }

        # Extract rate limit headers (Anthropic format)
        if headers:
            event.update({
                "requests_limit": headers.get("anthropic-ratelimit-requests-limit"),
                "requests_remaining": headers.get("anthropic-ratelimit-requests-remaining"),
                "tokens_limit": headers.get("anthropic-ratelimit-tokens-limit"),
                "tokens_remaining": headers.get("anthropic-ratelimit-tokens-remaining"),
                "reset_at": headers.get("anthropic-ratelimit-requests-reset"),
            })

        self._events.append(event)

        logfire.warn(
            "rate_limit_hit",
            **event,
        )

    def get_rate_limit_summary(self, minutes: int = 60) -> dict:
        """Summarize rate limit events over a time window."""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        recent = [
            e for e in self._events
            if datetime.fromisoformat(e["timestamp"]) >= cutoff
        ]

        by_provider = defaultdict(int)
        by_model = defaultdict(int)
        for e in recent:
            by_provider[e["provider"]] += 1
            by_model[e["model"]] += 1

        return {
            "window_minutes": minutes,
            "total_rate_limits": len(recent),
            "by_provider": dict(by_provider),
            "by_model": dict(by_model),
            "avg_retry_after": round(
                statistics.mean(
                    [e["retry_after"] for e in recent if e.get("retry_after")]
                ), 2
            ) if any(e.get("retry_after") for e in recent) else None,
        }
```

### Provider Health Dashboard Data

```python
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ProviderHealthSnapshot:
    """Point-in-time health assessment of an LLM provider."""
    provider: str
    timestamp: datetime
    is_healthy: bool
    latency_p50_ms: float
    latency_p95_ms: float
    error_rate_pct: float
    rate_limit_events_last_hour: int
    active_model: str


class ProviderHealthDashboard:
    """Aggregates health data across LLM providers for dashboard display."""

    def __init__(
        self,
        perf_monitor: PerformanceMonitor,
        rate_limit_tracker: RateLimitTracker,
    ):
        self.perf = perf_monitor
        self.rate_limits = rate_limit_tracker

    def get_health_snapshot(
        self,
        provider: str,
        model: str,
        use_case: str = "default",
    ) -> dict:
        """Generate a health snapshot for a provider/model combination."""
        latency = self.perf.get_latency_percentiles(model, use_case)
        throughput = self.perf.get_throughput_stats(model, use_case)
        rate_limit_summary = self.rate_limits.get_rate_limit_summary(minutes=60)

        # Determine health status
        is_healthy = True
        issues = []

        if isinstance(latency, dict) and "p95" in latency:
            if latency["p95"] > 10_000:  # p95 > 10s
                is_healthy = False
                issues.append(f"High p95 latency: {latency['p95']}ms")

        rate_limit_count = rate_limit_summary.get("by_provider", {}).get(provider, 0)
        if rate_limit_count > 10:
            is_healthy = False
            issues.append(f"Frequent rate limits: {rate_limit_count} in last hour")

        snapshot = {
            "provider": provider,
            "model": model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_healthy": is_healthy,
            "issues": issues,
            "latency": latency if isinstance(latency, dict) and "p50" in latency else {},
            "throughput": throughput if isinstance(throughput, dict) and "request_count" in throughput else {},
            "rate_limits_last_hour": rate_limit_count,
        }

        logfire.info("provider_health_snapshot", **snapshot)
        return snapshot
```

> **Swift Developer Note:** Performance monitoring for LLM apps is conceptually similar to using Instruments with Time Profiler and Network profiling in Xcode. The percentile approach (p50, p95, p99) mirrors how MetricKit reports `MXSignpostMetric` histograms in iOS. The key difference is that LLM latency is dominated by model inference on the provider side, not local computation, making it more like monitoring a third-party service dependency than profiling your own code.

---

## 7. Anomaly Detection

### Detecting Unusual Patterns

Production LLM applications need automated detection of cost spikes, quality drops, and latency regressions. The following implements a multi-signal anomaly detector.

```python
import statistics
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Callable
import logfire


class AnomalyType(Enum):
    COST_SPIKE = "cost_spike"
    LATENCY_INCREASE = "latency_increase"
    QUALITY_DROP = "quality_drop"
    ERROR_RATE_SPIKE = "error_rate_spike"
    TOKEN_USAGE_ANOMALY = "token_usage_anomaly"
    THROUGHPUT_DROP = "throughput_drop"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AnomalyAlert:
    anomaly_type: AnomalyType
    severity: AlertSeverity
    timestamp: datetime
    description: str
    current_value: float
    expected_value: float
    deviation_pct: float
    metadata: dict = field(default_factory=dict)


class MultiSignalAnomalyDetector:
    """Monitors multiple signals and detects anomalies using configurable rules."""

    def __init__(self):
        self._signals: dict[str, deque[tuple[datetime, float]]] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self._alert_handlers: list[Callable[[AnomalyAlert], None]] = []
        self._cooldowns: dict[str, datetime] = {}
        self.cooldown_minutes = 30  # Minimum time between repeated alerts

    def add_alert_handler(self, handler: Callable[[AnomalyAlert], None]):
        """Register a function to be called when an anomaly is detected."""
        self._alert_handlers.append(handler)

    def record_signal(self, signal_name: str, value: float):
        """Record a data point for a signal."""
        self._signals[signal_name].append(
            (datetime.now(timezone.utc), value)
        )

    def check_for_anomalies(self) -> list[AnomalyAlert]:
        """Run anomaly detection across all signals."""
        alerts = []

        for signal_name, data_points in self._signals.items():
            if len(data_points) < 20:
                continue

            values = [v for _, v in data_points]
            recent_values = values[-10:]
            historical_values = values[:-10]

            if not historical_values:
                continue

            hist_mean = statistics.mean(historical_values)
            hist_stdev = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
            recent_mean = statistics.mean(recent_values)

            # Skip if no variance in historical data
            if hist_stdev == 0:
                continue

            z_score = (recent_mean - hist_mean) / hist_stdev
            deviation_pct = ((recent_mean - hist_mean) / hist_mean) * 100 if hist_mean != 0 else 0

            # Determine anomaly type and severity
            anomaly_type = self._classify_signal(signal_name)
            severity = self._determine_severity(z_score, deviation_pct, signal_name)

            if severity is not None:
                alert = AnomalyAlert(
                    anomaly_type=anomaly_type,
                    severity=severity,
                    timestamp=datetime.now(timezone.utc),
                    description=(
                        f"{signal_name}: recent mean {recent_mean:.2f} vs "
                        f"historical mean {hist_mean:.2f} "
                        f"(z-score: {z_score:.2f}, deviation: {deviation_pct:+.1f}%)"
                    ),
                    current_value=recent_mean,
                    expected_value=hist_mean,
                    deviation_pct=deviation_pct,
                    metadata={
                        "signal_name": signal_name,
                        "z_score": round(z_score, 2),
                        "sample_size": len(data_points),
                    },
                )

                # Check cooldown to avoid alert fatigue
                cooldown_key = f"{signal_name}:{severity.value}"
                now = datetime.now(timezone.utc)
                last_alert = self._cooldowns.get(cooldown_key)

                if last_alert is None or (now - last_alert) > timedelta(
                    minutes=self.cooldown_minutes
                ):
                    alerts.append(alert)
                    self._cooldowns[cooldown_key] = now
                    self._fire_alert(alert)

        return alerts

    def _classify_signal(self, signal_name: str) -> AnomalyType:
        """Map signal name to anomaly type."""
        mapping = {
            "cost": AnomalyType.COST_SPIKE,
            "latency": AnomalyType.LATENCY_INCREASE,
            "quality": AnomalyType.QUALITY_DROP,
            "error": AnomalyType.ERROR_RATE_SPIKE,
            "token": AnomalyType.TOKEN_USAGE_ANOMALY,
            "throughput": AnomalyType.THROUGHPUT_DROP,
        }
        for keyword, anomaly_type in mapping.items():
            if keyword in signal_name.lower():
                return anomaly_type
        return AnomalyType.TOKEN_USAGE_ANOMALY

    def _determine_severity(
        self, z_score: float, deviation_pct: float, signal_name: str
    ) -> AlertSeverity | None:
        """Determine alert severity based on statistical deviation."""
        abs_z = abs(z_score)
        if abs_z < 2.0:
            return None  # Within normal range
        elif abs_z < 3.0:
            return AlertSeverity.INFO
        elif abs_z < 4.0:
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.CRITICAL

    def _fire_alert(self, alert: AnomalyAlert):
        """Send alert to all registered handlers."""
        logfire_fn = {
            AlertSeverity.INFO: logfire.info,
            AlertSeverity.WARNING: logfire.warn,
            AlertSeverity.CRITICAL: logfire.error,
        }[alert.severity]

        logfire_fn(
            "anomaly_detected",
            anomaly_type=alert.anomaly_type.value,
            severity=alert.severity.value,
            description=alert.description,
            current_value=alert.current_value,
            expected_value=alert.expected_value,
            deviation_pct=round(alert.deviation_pct, 1),
        )

        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logfire.error(
                    "alert_handler_failed",
                    handler=handler.__name__,
                    error=str(e),
                )
```

### Alerting Strategies

```python
import httpx


# Alert handler: Slack webhook
async def slack_alert_handler(alert: AnomalyAlert):
    """Send anomaly alerts to Slack."""
    color_map = {
        AlertSeverity.INFO: "#36a64f",
        AlertSeverity.WARNING: "#ff9900",
        AlertSeverity.CRITICAL: "#ff0000",
    }

    payload = {
        "attachments": [{
            "color": color_map[alert.severity],
            "title": f"LLM Anomaly: {alert.anomaly_type.value}",
            "text": alert.description,
            "fields": [
                {"title": "Severity", "value": alert.severity.value, "short": True},
                {"title": "Current", "value": f"{alert.current_value:.2f}", "short": True},
                {"title": "Expected", "value": f"{alert.expected_value:.2f}", "short": True},
                {"title": "Deviation", "value": f"{alert.deviation_pct:+.1f}%", "short": True},
            ],
            "ts": int(alert.timestamp.timestamp()),
        }]
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            json=payload,
        )


# Alert handler: PagerDuty for critical alerts
async def pagerduty_alert_handler(alert: AnomalyAlert):
    """Escalate critical anomalies to PagerDuty."""
    if alert.severity != AlertSeverity.CRITICAL:
        return

    payload = {
        "routing_key": "YOUR_PAGERDUTY_ROUTING_KEY",
        "event_action": "trigger",
        "payload": {
            "summary": f"LLM {alert.anomaly_type.value}: {alert.description}",
            "severity": "critical",
            "source": "llm-observability",
            "custom_details": {
                "current_value": alert.current_value,
                "expected_value": alert.expected_value,
                "deviation_pct": alert.deviation_pct,
                **alert.metadata,
            },
        },
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            "https://events.pagerduty.com/v2/enqueue",
            json=payload,
        )
```

### Root Cause Analysis Helper

```python
class RootCauseAnalyzer:
    """Correlate anomalies across signals to identify root causes."""

    def __init__(self, detector: MultiSignalAnomalyDetector):
        self.detector = detector

    def analyze(self, alerts: list[AnomalyAlert]) -> dict:
        """Given a set of concurrent anomalies, suggest root causes."""
        alert_types = {a.anomaly_type for a in alerts}

        hypotheses = []

        # Correlation patterns
        if AnomalyType.LATENCY_INCREASE in alert_types and AnomalyType.ERROR_RATE_SPIKE in alert_types:
            hypotheses.append({
                "hypothesis": "Provider degradation or outage",
                "confidence": "high",
                "action": "Check provider status page. Consider failover to backup provider.",
                "signals": ["latency", "error_rate"],
            })

        if AnomalyType.COST_SPIKE in alert_types and AnomalyType.TOKEN_USAGE_ANOMALY in alert_types:
            hypotheses.append({
                "hypothesis": "Unusual input pattern (possible prompt injection or runaway loop)",
                "confidence": "medium",
                "action": "Inspect recent requests for abnormal prompt lengths or repeated calls.",
                "signals": ["cost", "token_usage"],
            })

        if AnomalyType.QUALITY_DROP in alert_types and AnomalyType.LATENCY_INCREASE not in alert_types:
            hypotheses.append({
                "hypothesis": "Model behavior change (possible provider model update)",
                "confidence": "medium",
                "action": "Check provider changelog. Run eval suite against current model version.",
                "signals": ["quality"],
            })

        if AnomalyType.THROUGHPUT_DROP in alert_types:
            hypotheses.append({
                "hypothesis": "Rate limiting or upstream capacity issue",
                "confidence": "medium",
                "action": "Check rate limit headers. Review request queuing.",
                "signals": ["throughput"],
            })

        if not hypotheses:
            hypotheses.append({
                "hypothesis": "Unknown pattern -- manual investigation required",
                "confidence": "low",
                "action": "Review dashboards and recent deployment changes.",
                "signals": [a.anomaly_type.value for a in alerts],
            })

        logfire.info(
            "root_cause_analysis",
            num_alerts=len(alerts),
            num_hypotheses=len(hypotheses),
            alert_types=[a.value for a in alert_types],
        )

        return {
            "alerts": [
                {
                    "type": a.anomaly_type.value,
                    "severity": a.severity.value,
                    "description": a.description,
                }
                for a in alerts
            ],
            "hypotheses": hypotheses,
            "recommendation": hypotheses[0]["action"] if hypotheses else "Investigate manually.",
        }
```

---

## 8. Observability Infrastructure

### OpenTelemetry for LLM Applications

OpenTelemetry (OTel) is the industry standard for observability. Here is how to set it up with LLM-specific instrumentation.

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME


def setup_otel(
    service_name: str = "llm-service",
    otlp_endpoint: str = "http://localhost:4317",
):
    """Configure OpenTelemetry with OTLP export for an LLM application."""

    resource = Resource.create({
        SERVICE_NAME: service_name,
        "service.version": "1.0.0",
        "deployment.environment": "production",
    })

    # Traces
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=otlp_endpoint)
        )
    )
    trace.set_tracer_provider(trace_provider)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=otlp_endpoint),
        export_interval_millis=30_000,  # Export every 30 seconds
    )
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )
    metrics.set_meter_provider(meter_provider)

    return trace.get_tracer(service_name), metrics.get_meter(service_name)


# Initialize
tracer, meter = setup_otel("my-llm-app")
```

### Custom Spans and Attributes for LLM Calls

```python
from opentelemetry import trace
from opentelemetry.trace import StatusCode
import time


# Define semantic conventions for LLM operations
# (Based on emerging OpenTelemetry GenAI semantic conventions)
LLM_SYSTEM = "gen_ai.system"
LLM_REQUEST_MODEL = "gen_ai.request.model"
LLM_REQUEST_MAX_TOKENS = "gen_ai.request.max_tokens"
LLM_REQUEST_TEMPERATURE = "gen_ai.request.temperature"
LLM_RESPONSE_MODEL = "gen_ai.response.model"
LLM_RESPONSE_FINISH_REASONS = "gen_ai.response.finish_reasons"
LLM_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
LLM_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"


def traced_llm_call(
    client,
    model: str,
    messages: list[dict],
    temperature: float = 1.0,
    max_tokens: int = 1024,
    **kwargs,
):
    """Make an LLM call with full OpenTelemetry instrumentation."""
    tracer = trace.get_tracer("llm-client")

    with tracer.start_as_current_span(
        "llm.chat",
        kind=trace.SpanKind.CLIENT,
        attributes={
            LLM_SYSTEM: "anthropic",
            LLM_REQUEST_MODEL: model,
            LLM_REQUEST_MAX_TOKENS: max_tokens,
            LLM_REQUEST_TEMPERATURE: temperature,
            "llm.request.message_count": len(messages),
        },
    ) as span:
        start = time.perf_counter()

        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                **kwargs,
            )

            duration_ms = (time.perf_counter() - start) * 1000

            # Set response attributes
            span.set_attribute(LLM_RESPONSE_MODEL, response.model)
            span.set_attribute(LLM_RESPONSE_FINISH_REASONS, [response.stop_reason])
            span.set_attribute(LLM_USAGE_INPUT_TOKENS, response.usage.input_tokens)
            span.set_attribute(LLM_USAGE_OUTPUT_TOKENS, response.usage.output_tokens)
            span.set_attribute("llm.duration_ms", round(duration_ms, 2))
            span.set_attribute(
                "llm.tokens_per_second",
                round(response.usage.output_tokens / (duration_ms / 1000), 1)
                if duration_ms > 0 else 0,
            )

            span.set_status(StatusCode.OK)
            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            span.set_status(StatusCode.ERROR, str(e))
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            span.set_attribute("llm.duration_ms", round(duration_ms, 2))
            span.record_exception(e)
            raise
```

### Custom OTel Metrics for LLM Applications

```python
from opentelemetry import metrics


def create_llm_metrics(meter: metrics.Meter) -> dict:
    """Create a set of OpenTelemetry metrics for LLM monitoring."""

    return {
        # Token counters
        "input_tokens": meter.create_counter(
            name="llm.tokens.input",
            description="Total input tokens consumed",
            unit="tokens",
        ),
        "output_tokens": meter.create_counter(
            name="llm.tokens.output",
            description="Total output tokens generated",
            unit="tokens",
        ),

        # Cost tracking
        "cost": meter.create_counter(
            name="llm.cost",
            description="Estimated LLM API cost",
            unit="usd",
        ),

        # Latency histogram
        "latency": meter.create_histogram(
            name="llm.request.duration",
            description="LLM request duration",
            unit="ms",
        ),

        # Quality gauge
        "quality_score": meter.create_histogram(
            name="llm.quality.score",
            description="LLM output quality score",
            unit="score",
        ),

        # Error counter
        "errors": meter.create_counter(
            name="llm.errors",
            description="LLM API errors",
            unit="errors",
        ),

        # Rate limit counter
        "rate_limits": meter.create_counter(
            name="llm.rate_limits",
            description="Rate limit events",
            unit="events",
        ),

        # Active requests gauge
        "active_requests": meter.create_up_down_counter(
            name="llm.requests.active",
            description="Currently active LLM requests",
            unit="requests",
        ),
    }


# Usage with metrics
llm_metrics = create_llm_metrics(meter)

def record_llm_metrics(
    response,
    duration_ms: float,
    model: str,
    cost_usd: float,
    use_case: str = "default",
):
    """Record all metrics for a completed LLM call."""
    attributes = {"model": model, "use_case": use_case}

    llm_metrics["input_tokens"].add(
        response.usage.input_tokens, attributes
    )
    llm_metrics["output_tokens"].add(
        response.usage.output_tokens, attributes
    )
    llm_metrics["cost"].add(cost_usd, attributes)
    llm_metrics["latency"].record(duration_ms, attributes)
```

### Dashboard Design: What to Display

A well-designed LLM observability dashboard should be organized around operational questions.

```python
# Dashboard panel definitions (for Grafana or similar)
# These define the queries and visualizations you would build.

DASHBOARD_PANELS = {
    "row_1_overview": {
        "title": "System Overview",
        "panels": [
            {
                "title": "Request Rate (RPM)",
                "type": "graph",
                "query": 'rate(llm_requests_total[5m]) * 60',
                "description": "How many LLM calls per minute across all models",
            },
            {
                "title": "Error Rate (%)",
                "type": "gauge",
                "query": 'rate(llm_errors_total[5m]) / rate(llm_requests_total[5m]) * 100',
                "thresholds": {"green": 0, "yellow": 1, "red": 5},
            },
            {
                "title": "Hourly Cost ($)",
                "type": "stat",
                "query": 'increase(llm_cost_usd_total[1h])',
                "description": "Total LLM spend in the last hour",
            },
        ],
    },
    "row_2_latency": {
        "title": "Latency",
        "panels": [
            {
                "title": "Latency Percentiles by Model",
                "type": "graph",
                "queries": {
                    "p50": 'histogram_quantile(0.50, rate(llm_request_duration_ms_bucket[5m]))',
                    "p95": 'histogram_quantile(0.95, rate(llm_request_duration_ms_bucket[5m]))',
                    "p99": 'histogram_quantile(0.99, rate(llm_request_duration_ms_bucket[5m]))',
                },
            },
            {
                "title": "Tokens per Second",
                "type": "graph",
                "query": 'rate(llm_tokens_output_total[5m]) / rate(llm_request_duration_seconds_sum[5m])',
            },
        ],
    },
    "row_3_tokens_cost": {
        "title": "Token Usage & Cost",
        "panels": [
            {
                "title": "Token Usage by Model",
                "type": "stacked_bar",
                "queries": {
                    "input": 'increase(llm_tokens_input_total[1h])',
                    "output": 'increase(llm_tokens_output_total[1h])',
                },
            },
            {
                "title": "Cost by Customer (Top 10)",
                "type": "table",
                "query": 'topk(10, increase(llm_cost_usd_total[24h]))',
            },
            {
                "title": "Cost Trend (7-day)",
                "type": "graph",
                "query": 'increase(llm_cost_usd_total[1d])',
                "range": "7d",
            },
        ],
    },
    "row_4_quality": {
        "title": "Quality Metrics",
        "panels": [
            {
                "title": "Quality Score Distribution",
                "type": "histogram",
                "query": 'llm_quality_score_bucket',
            },
            {
                "title": "Quality Trend (7-day Moving Average)",
                "type": "graph",
                "query": 'avg_over_time(llm_quality_score_mean[1d])',
                "range": "7d",
            },
            {
                "title": "User Feedback Ratings",
                "type": "pie_chart",
                "query": 'increase(llm_user_feedback_total[24h])',
            },
        ],
    },
    "row_5_alerts": {
        "title": "Anomalies & Alerts",
        "panels": [
            {
                "title": "Active Alerts",
                "type": "alert_list",
                "description": "Currently firing anomaly alerts",
            },
            {
                "title": "Rate Limit Events",
                "type": "graph",
                "query": 'increase(llm_rate_limits_total[5m])',
            },
        ],
    },
}
```

### Alert Configuration

```yaml
# prometheus_alerts.yml - LLM-specific alert rules
groups:
  - name: llm_observability
    interval: 30s
    rules:
      # Cost alerts
      - alert: LLMHourlyCostSpike
        expr: increase(llm_cost_usd_total[1h]) > 200
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "LLM hourly cost exceeding $200"
          description: >
            Current hourly spend is ${{ $value }}.
            Check for runaway requests or unexpected usage patterns.

      - alert: LLMDailyCostBudget
        expr: increase(llm_cost_usd_total[24h]) > 2000
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Daily LLM cost approaching budget limit"

      # Latency alerts
      - alert: LLMHighLatencyP95
        expr: >
          histogram_quantile(0.95,
            rate(llm_request_duration_ms_bucket[10m])
          ) > 15000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "LLM p95 latency exceeds 15 seconds"

      # Quality alerts
      - alert: LLMQualityDegradation
        expr: >
          avg_over_time(llm_quality_score_mean[1h])
          < 0.7
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Average LLM quality score dropped below 0.7"

      # Error rate alerts
      - alert: LLMHighErrorRate
        expr: >
          rate(llm_errors_total[5m])
          / rate(llm_requests_total[5m])
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "LLM error rate exceeds 5%"

      # Rate limiting
      - alert: LLMFrequentRateLimits
        expr: increase(llm_rate_limits_total[15m]) > 20
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Frequent rate limit hits from LLM provider"
```

### Putting It All Together: FastAPI Integration

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import logfire
import time


# Configure logfire with OpenTelemetry export
logfire.configure(
    service_name="llm-api",
    send_to_logfire=True,
)

# Instrument FastAPI
logfire.instrument_fastapi(app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logfire.info("application_starting")
    # Initialize monitors
    app.state.perf_monitor = PerformanceMonitor()
    app.state.quality_monitor = QualityMonitor()
    app.state.usage_tracker = CustomerUsageTracker()
    app.state.anomaly_detector = MultiSignalAnomalyDetector()
    yield
    logfire.info("application_shutting_down")


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Add observability to every request."""
    start = time.perf_counter()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    with logfire.span(
        "http_request",
        method=request.method,
        path=request.url.path,
        request_id=request_id,
    ):
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logfire.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            request_id=request_id,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Duration-Ms"] = str(round(duration_ms, 2))
        return response


@app.get("/observability/health")
async def observability_health(request: Request):
    """Dashboard endpoint for observability health data."""
    perf = request.app.state.perf_monitor
    usage = request.app.state.usage_tracker

    return {
        "status": "healthy",
        "monitors": {
            "performance": "active",
            "quality": "active",
            "usage": "active",
            "anomaly_detection": "active",
        },
    }
```

> **Swift Developer Note:** OpenTelemetry in Python serves a similar role to Apple's unified logging system (`os.log` with `OSLogStore`) combined with `MetricKit` for aggregated performance data. The key architectural difference is that Apple's system is push-based (the OS collects and delivers metrics to you), while OTel is pull/push-flexible (you instrument your code and export to any backend). If you have used `os_signpost` for custom Instruments, OTel spans will feel familiar -- they mark the beginning and end of operations and carry custom attributes, just like signpost intervals.

---

## 9. Swift Comparison

This section maps LLM observability concepts to their closest iOS/Swift equivalents to accelerate your learning.

### Logging

| Python / LLM Observability | Swift / iOS Equivalent |
|----------------------------|----------------------|
| `logfire.info("event", key=value)` | `os.log(.info, "event: \(value)")` |
| `structlog` / `python-json-logger` | `os.Logger` with `OSLogStore` |
| Log levels: DEBUG, INFO, WARN, ERROR | `OSLogType`: `.debug`, `.info`, `.default`, `.error`, `.fault` |
| Privacy redaction via custom code | `%{private}@` / `%{public}@` format specifiers |
| Centralized log aggregation (ELK, Datadog) | Console.app, `log collect`, Xcode Organizer |

### Tracing and Profiling

| Python / LLM Observability | Swift / iOS Equivalent |
|----------------------------|----------------------|
| OpenTelemetry spans | `os_signpost` intervals in Instruments |
| Distributed traces across services | Instruments Time Profiler (single process) |
| Span attributes (model, tokens, etc.) | Signpost metadata and categories |
| Trace context propagation (HTTP headers) | No direct equivalent (single-device) |
| Jaeger / Zipkin trace visualization | Instruments trace viewer |

### Metrics

| Python / LLM Observability | Swift / iOS Equivalent |
|----------------------------|----------------------|
| Prometheus counters/gauges/histograms | `MetricKit` (`MXMetricPayload`) |
| Custom business metrics | `MXSignpostMetric` for custom intervals |
| Real-time dashboards (Grafana) | Xcode Organizer (aggregated, delayed) |
| Alerting (PagerDuty, Slack) | `MXCrashDiagnostic`, `MXDiskWriteException` |

### Key Conceptual Differences

```python
# In Swift/iOS, you profile a deterministic, single-user application:
#
#   let logger = Logger(subsystem: "com.app", category: "network")
#   logger.info("Request completed in \(duration)s")
#
#   // Instruments signpost for profiling
#   let signpostID = OSSignpostID(log: log)
#   os_signpost(.begin, log: log, name: "Network Request", signpostID: signpostID)
#   // ... do work ...
#   os_signpost(.end, log: log, name: "Network Request", signpostID: signpostID)

# In Python LLM apps, you observe a non-deterministic, multi-tenant system:
#
#   - You CANNOT reproduce issues by "running it again" (non-determinism)
#   - You MUST log full request/response data (prompts + completions)
#   - You MUST track per-customer costs (multi-tenancy)
#   - You MUST monitor output QUALITY, not just uptime
#   - You MUST handle third-party provider variability (not just your own code)
#
# This makes observability MORE important and MORE complex than in mobile apps.
```

### What Transfers and What Does Not

**Transfers well:**
- The habit of instrumenting code (signposts -> spans)
- Thinking in percentiles (MetricKit histograms -> Prometheus histograms)
- Structured logging practices (OSLog -> structlog/logfire)
- Privacy awareness in logs (OSLog privacy -> PII redaction)

**New concepts to learn:**
- Distributed tracing across microservices (iOS is single-process)
- Per-customer cost tracking and budget enforcement (no iOS equivalent)
- Output quality monitoring and LLM-as-judge evaluation
- Provider failover and multi-provider health monitoring
- Token economics and cost optimization observability

---

## 10. Interview Focus

### Common Observability Questions for SE/AI Engineer Roles

#### Question 1: "A customer says your AI feature got worse. How do you investigate?"

**Strong answer structure:**

```
1. Check quality metrics dashboard
   - Look for quality score trends (LLM-as-judge, user feedback)
   - Compare recent scores to baseline by use_case
   - Check if the issue is global or customer-specific

2. Check for infrastructure changes
   - Model version changes (provider may have updated)
   - Prompt template changes (recent deployments)
   - Data pipeline changes (RAG index updates)

3. Reproduce and trace
   - Pull the customer's recent request logs (with privacy controls)
   - Trace individual requests through the RAG pipeline
   - Compare retrieval quality, prompt construction, generation

4. Compare prompt versions
   - If prompts changed: run eval suite on old vs new
   - If model changed: run eval suite on old vs new model
   - If data changed: check retrieval recall on test queries

5. Communicate findings
   - Share specific data points with the customer
   - Provide timeline of when degradation started
   - Propose remediation (rollback, prompt fix, etc.)
```

#### Question 2: "How would you design a cost monitoring system for an LLM API serving 1000 customers?"

**Key points to cover:**

```python
# 1. Per-request cost tracking (as shown in TokenUsageRecord)
# 2. Per-customer aggregation with budget enforcement
# 3. Tiered alerting (50%, 75%, 90%, 100% of budget)
# 4. Anomaly detection on usage patterns
# 5. Dashboard with top spenders, cost trends, model breakdown

# Architecture sketch:
#
# Request -> LLM API -> Response
#    |                      |
#    v                      v
# [Token Counter] --> [Usage Aggregator] --> [Budget Checker]
#                          |                       |
#                          v                       v
#                    [Time-series DB]        [Alert System]
#                          |
#                          v
#                    [Dashboard/API]
```

#### Question 3: "How do you monitor the quality of an LLM application in production?"

**Framework for answering:**

1. **Automated metrics**: LLM-as-judge scoring on sampled requests (relevance, accuracy, coherence)
2. **User feedback**: Thumbs up/down, star ratings, explicit corrections
3. **Proxy metrics**: Response length distribution, refusal rate, citation rate
4. **Regression detection**: Compare rolling quality averages to established baselines
5. **Human review**: Periodic review of flagged or sampled outputs
6. **Eval suites**: Regular runs of golden-set evaluations against fixed test cases

#### Question 4: "Walk through how you would debug a RAG system returning wrong answers."

```
Step 1: Identify the failure mode
  - Is it retrieving wrong documents? (retrieval problem)
  - Is it retrieving right documents but generating wrong answers? (generation problem)
  - Is it not finding any documents? (indexing problem)

Step 2: Inspect the trace
  - Query understanding: Was the query transformed correctly?
  - Retrieval: What scores did the retrieved documents have?
  - Context: Was the relevant information in the context window?
  - Generation: Did the model ignore or misinterpret the context?

Step 3: Isolate the component
  - Test retrieval independently with known queries
  - Test generation independently with known contexts
  - Check for context window overflow (key info buried)

Step 4: Fix and verify
  - Adjust retrieval (chunking strategy, embedding model, k value)
  - Adjust prompt (more explicit instructions, better formatting)
  - Adjust post-processing (citation validation, answer verification)
```

#### Question 5: "What metrics would you put on your LLM observability dashboard?"

**Tier 1 - Always visible (top of dashboard):**
- Request rate (RPM)
- Error rate (%)
- p95 latency (ms)
- Hourly cost ($)

**Tier 2 - Operational health:**
- Token usage by model (stacked area chart)
- Latency percentiles over time (p50, p95, p99)
- Rate limit events
- Active alerts

**Tier 3 - Quality and business:**
- Quality score trend (7-day rolling average)
- User feedback distribution
- Cost per customer (top 10 table)
- Cache hit rate (for prompt caching)

**Tier 4 - Debugging (drill-down):**
- Individual request traces
- Prompt version comparison
- Retrieval score distributions
- Error type breakdown

### Practice Exercise: Design an Observability System

Design a complete observability solution for the following scenario:

> You are building an AI-powered customer support bot that uses RAG over a company's help documentation. It serves 500 customers, handles 10,000 queries per day, and uses Claude Sonnet as the primary model with Haiku as a fallback. The company has a $5,000/month LLM budget.

Your design should address:
1. What do you log for each request?
2. How do you track costs and enforce the budget?
3. How do you monitor quality?
4. What alerts do you set up?
5. What does your dashboard look like?
6. How do you handle a quality regression?

Think through this exercise before looking at production systems -- it is a common interview format for solutions engineer roles.

---

## Summary

LLM observability builds on traditional monitoring foundations but adds critical new dimensions:

| Traditional Observability | LLM Observability Addition |
|--------------------------|---------------------------|
| Status codes and errors | Output quality scoring |
| Latency tracking | Token usage and cost tracking |
| Throughput monitoring | Per-customer budget enforcement |
| Error alerting | Quality drift detection |
| Stack trace debugging | Prompt and context debugging |
| Structured logging | Privacy-aware prompt/completion logging |
| Health checks | Provider health monitoring |

**Key takeaways:**

1. **Log everything, but carefully.** Capture prompts, completions, tokens, latency, and model parameters. Apply privacy controls appropriate to your environment.

2. **Track costs as a first-class metric.** Token usage translates directly to dollars. Per-customer tracking and budget enforcement are essential for multi-tenant systems.

3. **Quality is the hardest metric.** Use a combination of automated scoring (LLM-as-judge), user feedback, and regular human review to monitor output quality over time.

4. **Trace the full pipeline.** LLM applications involve multiple steps (retrieval, prompt construction, generation, post-processing). Each step needs its own span with relevant attributes.

5. **Detect anomalies proactively.** Cost spikes, quality drops, and latency increases should trigger alerts before customers notice problems.

6. **Design dashboards around questions.** Organize dashboards by the questions operators need to answer: "Is the system healthy?", "Are we within budget?", "Is quality stable?", "What went wrong?"

The observability infrastructure you build determines how quickly you can diagnose issues, how confidently you can ship changes, and how effectively you can demonstrate system health to customers -- all critical skills for a solutions engineer or applied AI engineer role.
