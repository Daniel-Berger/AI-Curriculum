# Module 02: Cost & Performance Optimization

## Why This Module Matters for Interviews

At companies like Anthropic, OpenAI, and Google, solutions engineers are directly responsible for helping enterprise customers control AI spend while maintaining quality. You will be asked:

- "A customer is spending $50K/month on API calls. How do you reduce that by 40%?"
- "How do you decide between Haiku and Sonnet for a given use case?"
- "Walk me through how you would profile and optimize an LLM-powered pipeline."
- "How do you build cost guardrails so a customer never gets a surprise bill?"

This module teaches you to think about LLM usage as an engineering optimization problem -- balancing cost, latency, and quality. Every technique here maps directly to real customer conversations and production system design.

---

## 1. The Economics of LLM APIs

### Token Pricing Models

LLM APIs charge per token, with separate rates for input and output tokens. Output tokens are always more expensive because they require autoregressive generation (each token depends on the previous one).

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Provider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    COHERE = "cohere"


@dataclass(frozen=True)
class ModelPricing:
    """Pricing per 1M tokens (as of early 2025)."""
    provider: Provider
    model_name: str
    input_price_per_mtok: float   # USD per 1M input tokens
    output_price_per_mtok: float  # USD per 1M output tokens
    context_window: int
    cached_input_price_per_mtok: Optional[float] = None  # Discounted cached rate

    @property
    def input_price_per_token(self) -> float:
        return self.input_price_per_mtok / 1_000_000

    @property
    def output_price_per_token(self) -> float:
        return self.output_price_per_mtok / 1_000_000

    def estimate_cost(
        self, input_tokens: int, output_tokens: int, cached_tokens: int = 0
    ) -> float:
        """Estimate cost for a single API call."""
        uncached_input = input_tokens - cached_tokens
        cost = uncached_input * self.input_price_per_token
        cost += output_tokens * self.output_price_per_token
        if cached_tokens > 0 and self.cached_input_price_per_mtok:
            cost += cached_tokens * (self.cached_input_price_per_mtok / 1_000_000)
        return cost


# Current pricing catalog (approximate, verify against provider docs)
PRICING_CATALOG: dict[str, ModelPricing] = {
    # Anthropic
    "claude-3-5-haiku": ModelPricing(
        Provider.ANTHROPIC, "claude-3-5-haiku-20241022",
        input_price_per_mtok=0.80, output_price_per_mtok=4.00,
        context_window=200_000, cached_input_price_per_mtok=0.08,
    ),
    "claude-3-5-sonnet": ModelPricing(
        Provider.ANTHROPIC, "claude-3-5-sonnet-20241022",
        input_price_per_mtok=3.00, output_price_per_mtok=15.00,
        context_window=200_000, cached_input_price_per_mtok=0.30,
    ),
    "claude-3-opus": ModelPricing(
        Provider.ANTHROPIC, "claude-3-opus-20240229",
        input_price_per_mtok=15.00, output_price_per_mtok=75.00,
        context_window=200_000, cached_input_price_per_mtok=1.50,
    ),
    # OpenAI
    "gpt-4o-mini": ModelPricing(
        Provider.OPENAI, "gpt-4o-mini",
        input_price_per_mtok=0.15, output_price_per_mtok=0.60,
        context_window=128_000,
    ),
    "gpt-4o": ModelPricing(
        Provider.OPENAI, "gpt-4o",
        input_price_per_mtok=2.50, output_price_per_mtok=10.00,
        context_window=128_000,
    ),
    # Google
    "gemini-1.5-flash": ModelPricing(
        Provider.GOOGLE, "gemini-1.5-flash",
        input_price_per_mtok=0.075, output_price_per_mtok=0.30,
        context_window=1_000_000,
    ),
    "gemini-1.5-pro": ModelPricing(
        Provider.GOOGLE, "gemini-1.5-pro",
        input_price_per_mtok=1.25, output_price_per_mtok=5.00,
        context_window=2_000_000,
    ),
}
```

### Total Cost of Ownership

API token costs are only part of the picture. A full cost model includes infrastructure, engineering time, and quality costs.

```python
from dataclasses import dataclass, field


@dataclass
class TotalCostModel:
    """Model the true cost of an AI feature, not just API spend."""
    # Direct API costs (monthly)
    api_calls_per_month: int = 0
    avg_input_tokens: int = 0
    avg_output_tokens: int = 0
    model_pricing: ModelPricing | None = None

    # Infrastructure costs (monthly)
    vector_db_cost: float = 0.0       # Pinecone, Weaviate, etc.
    compute_cost: float = 0.0         # Servers running the app
    storage_cost: float = 0.0         # Logs, embeddings, caches

    # People costs (monthly, amortized)
    engineering_hours: float = 0.0
    hourly_rate: float = 150.0

    # Quality costs
    error_rate: float = 0.0           # Fraction of calls needing retry
    retry_multiplier: float = 1.5     # Cost multiplier for retried calls

    def monthly_api_cost(self) -> float:
        if not self.model_pricing:
            return 0.0
        base_cost = self.model_pricing.estimate_cost(
            self.avg_input_tokens, self.avg_output_tokens
        )
        effective_calls = self.api_calls_per_month * (
            1 + self.error_rate * self.retry_multiplier
        )
        return base_cost * effective_calls

    def monthly_infrastructure_cost(self) -> float:
        return self.vector_db_cost + self.compute_cost + self.storage_cost

    def monthly_people_cost(self) -> float:
        return self.engineering_hours * self.hourly_rate

    def monthly_total(self) -> float:
        return (
            self.monthly_api_cost()
            + self.monthly_infrastructure_cost()
            + self.monthly_people_cost()
        )

    def cost_per_request(self) -> float:
        if self.api_calls_per_month == 0:
            return 0.0
        return self.monthly_total() / self.api_calls_per_month


# Example: a RAG-powered customer support bot
support_bot = TotalCostModel(
    api_calls_per_month=500_000,
    avg_input_tokens=2000,
    avg_output_tokens=500,
    model_pricing=PRICING_CATALOG["claude-3-5-sonnet"],
    vector_db_cost=200.0,
    compute_cost=500.0,
    storage_cost=50.0,
    engineering_hours=40,
    error_rate=0.03,
)

print(f"Monthly API cost:     ${support_bot.monthly_api_cost():,.2f}")
print(f"Monthly infra cost:   ${support_bot.monthly_infrastructure_cost():,.2f}")
print(f"Monthly people cost:  ${support_bot.monthly_people_cost():,.2f}")
print(f"Monthly total:        ${support_bot.monthly_total():,.2f}")
print(f"Cost per request:     ${support_bot.cost_per_request():.4f}")
```

> **Swift Developer Note:** In iOS development, you think about costs in terms of battery, bandwidth, and App Store fees. LLM API costs are more like CloudKit or Firebase usage-based pricing -- they scale linearly with usage and can surprise you if unmonitored. The `TotalCostModel` above is analogous to building a cost model for a feature that uses CloudKit extensively, where you would also factor in compute, storage, and transfer costs alongside the direct API charges.

---

## 2. Token Counting and Cost Modeling

### Counting Tokens with tiktoken (OpenAI)

OpenAI provides the `tiktoken` library for exact token counting. This lets you estimate costs before making API calls.

```python
import tiktoken


def count_openai_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens for an OpenAI model."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def count_chat_tokens(
    messages: list[dict[str, str]], model: str = "gpt-4o"
) -> int:
    """
    Count tokens for a chat completion request.

    Chat messages have overhead tokens for message formatting.
    See: https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
    """
    encoding = tiktoken.encoding_for_model(model)

    # Every message has overhead for role and formatting
    tokens_per_message = 3  # <|start|>role<|end|>
    tokens_per_name = 1

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name

    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


# Usage
prompt = "Explain the theory of relativity in simple terms."
tokens = count_openai_tokens(prompt)
print(f"Prompt tokens: {tokens}")

messages = [
    {"role": "system", "content": "You are a physics tutor."},
    {"role": "user", "content": "Explain the theory of relativity in simple terms."},
]
chat_tokens = count_chat_tokens(messages)
print(f"Chat message tokens: {chat_tokens}")
```

### Counting Tokens with Anthropic

Anthropic's SDK provides a token counting endpoint. Since Anthropic uses a different tokenizer than OpenAI, you must use the Anthropic-specific method.

```python
import anthropic


def count_anthropic_tokens(
    messages: list[dict[str, str]],
    model: str = "claude-3-5-sonnet-20241022",
    system: str = "",
) -> int:
    """
    Count tokens using Anthropic's token counting API.

    This is an API call (not local), but it does not consume usage.
    """
    client = anthropic.Anthropic()
    response = client.messages.count_tokens(
        model=model,
        messages=messages,
        system=system,
    )
    return response.input_tokens


# For local estimation without an API call, use a rough heuristic:
def estimate_tokens_heuristic(text: str) -> int:
    """
    Rough estimate: ~1 token per 4 characters for English text.
    This is an approximation -- use the API for precise counts.
    """
    return max(1, len(text) // 4)
```

### Building a Pre-Call Cost Estimator

Before making expensive API calls, estimate the cost and enforce budgets.

```python
from dataclasses import dataclass
from typing import Protocol


class TokenCounter(Protocol):
    """Protocol for token counting implementations."""
    def count(self, text: str) -> int: ...


@dataclass
class CostEstimate:
    """Pre-call cost estimate with budget check."""
    input_tokens: int
    estimated_output_tokens: int
    estimated_cost: float
    model: str
    within_budget: bool
    budget_remaining: float


class CostEstimator:
    """Estimates cost before making API calls."""

    def __init__(
        self,
        pricing_catalog: dict[str, ModelPricing],
        monthly_budget: float = 1000.0,
    ) -> None:
        self.pricing = pricing_catalog
        self.monthly_budget = monthly_budget
        self._spent_this_month: float = 0.0

    def estimate(
        self,
        model_key: str,
        input_text: str,
        expected_output_ratio: float = 0.5,
        max_output_tokens: int = 4096,
    ) -> CostEstimate:
        """
        Estimate cost for a planned API call.

        Args:
            model_key: Key into pricing catalog
            input_text: The full prompt text
            expected_output_ratio: Expected output tokens as fraction of input
            max_output_tokens: Cap on output tokens
        """
        pricing = self.pricing[model_key]
        input_tokens = estimate_tokens_heuristic(input_text)
        estimated_output = min(
            int(input_tokens * expected_output_ratio),
            max_output_tokens,
        )

        cost = pricing.estimate_cost(input_tokens, estimated_output)
        remaining = self.monthly_budget - self._spent_this_month

        return CostEstimate(
            input_tokens=input_tokens,
            estimated_output_tokens=estimated_output,
            estimated_cost=cost,
            model=pricing.model_name,
            within_budget=cost <= remaining,
            budget_remaining=remaining,
        )

    def record_actual_cost(self, cost: float) -> None:
        """Record actual cost after an API call completes."""
        self._spent_this_month += cost

    def budget_utilization(self) -> float:
        """Return fraction of monthly budget consumed."""
        return self._spent_this_month / self.monthly_budget


# Usage
estimator = CostEstimator(PRICING_CATALOG, monthly_budget=500.0)

long_prompt = "Analyze the following document... " * 500  # Simulate a long prompt
estimate = estimator.estimate("claude-3-5-sonnet", long_prompt)

print(f"Input tokens:  {estimate.input_tokens:,}")
print(f"Output tokens: {estimate.estimated_output_tokens:,}")
print(f"Est. cost:     ${estimate.estimated_cost:.4f}")
print(f"Within budget: {estimate.within_budget}")
print(f"Budget left:   ${estimate.budget_remaining:.2f}")
```

### Budget Alert System

```python
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class BudgetAlert:
    level: AlertLevel
    message: str
    current_spend: float
    budget: float
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class BudgetMonitor:
    """Monitor spending and trigger alerts at configurable thresholds."""

    def __init__(
        self,
        monthly_budget: float,
        warning_threshold: float = 0.75,
        critical_threshold: float = 0.90,
    ) -> None:
        self.monthly_budget = monthly_budget
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self._total_spend: float = 0.0
        self._alerts: list[BudgetAlert] = []

    def record_spend(self, amount: float) -> BudgetAlert | None:
        """Record spending and return an alert if a threshold is crossed."""
        previous_utilization = self._total_spend / self.monthly_budget
        self._total_spend += amount
        current_utilization = self._total_spend / self.monthly_budget

        alert = None
        if (
            current_utilization >= self.critical_threshold
            and previous_utilization < self.critical_threshold
        ):
            alert = BudgetAlert(
                level=AlertLevel.CRITICAL,
                message=f"Budget {current_utilization:.0%} consumed! "
                        f"${self.monthly_budget - self._total_spend:.2f} remaining.",
                current_spend=self._total_spend,
                budget=self.monthly_budget,
            )
            logger.critical(alert.message)
        elif (
            current_utilization >= self.warning_threshold
            and previous_utilization < self.warning_threshold
        ):
            alert = BudgetAlert(
                level=AlertLevel.WARNING,
                message=f"Budget {current_utilization:.0%} consumed. "
                        f"Consider reviewing usage patterns.",
                current_spend=self._total_spend,
                budget=self.monthly_budget,
            )
            logger.warning(alert.message)

        if alert:
            self._alerts.append(alert)
        return alert

    @property
    def alerts(self) -> list[BudgetAlert]:
        return list(self._alerts)
```

> **Swift Developer Note:** This pattern is similar to how you might monitor CloudKit operation quotas or in-app purchase transaction volumes in an iOS app. The `BudgetMonitor` follows the same observer-style pattern you would use with `NotificationCenter` in Swift -- crossing a threshold triggers a notification. In production, these alerts would fire webhooks to Slack or PagerDuty.

---

## 3. Prompt Caching and Optimization

### How Prompt Caching Works

Prompt caching allows providers to reuse the KV-cache from previously processed prompt prefixes. When the beginning of your prompt matches a cached prefix, you pay a reduced rate for those tokens and skip the computation.

**Key rules:**
- The cached portion must be an exact prefix match (same tokens, same order)
- There is a minimum token threshold for caching to activate (Anthropic: 1024 tokens)
- Cached tokens have a TTL (Anthropic: 5 minutes of inactivity)

### Anthropic Prompt Caching

Anthropic's caching uses explicit `cache_control` markers in the request:

```python
import anthropic


def call_with_caching(
    client: anthropic.Anthropic,
    system_prompt: str,
    reference_document: str,
    user_question: str,
) -> anthropic.types.Message:
    """
    Make an API call with prompt caching enabled.

    The system prompt and reference document are marked for caching
    because they remain constant across many user questions.
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Reference document:\n\n{reference_document}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": user_question,
                    },
                ],
            }
        ],
    )
    return response


def analyze_cache_performance(response: anthropic.types.Message) -> dict:
    """Extract caching metrics from a response."""
    usage = response.usage
    return {
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "cache_creation_input_tokens": getattr(
            usage, "cache_creation_input_tokens", 0
        ),
        "cache_read_input_tokens": getattr(
            usage, "cache_read_input_tokens", 0
        ),
        "cache_hit": getattr(usage, "cache_read_input_tokens", 0) > 0,
    }
```

### Cache-Aware Prompt Design

Structure your prompts so the stable parts come first (and are long enough to cache), and the variable parts come last.

```python
from dataclasses import dataclass


@dataclass
class CacheOptimizedPrompt:
    """
    Structure prompts for maximum cache efficiency.

    Principle: static content first, dynamic content last.
    The cache prefix match works left-to-right, so anything
    that changes between requests should be at the end.
    """
    # Layer 1: System prompt (most stable, changes rarely)
    system_prompt: str

    # Layer 2: Reference material (stable per session/customer)
    reference_docs: str

    # Layer 3: Few-shot examples (stable per task type)
    examples: str

    # Layer 4: User input (changes every request)
    user_input: str

    def build_messages(self) -> tuple[list[dict], list[dict]]:
        """Build system and messages arrays with cache markers."""
        system = [
            {
                "type": "text",
                "text": self.system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

        user_content = []

        # Add reference docs with caching (if substantial)
        if len(self.reference_docs) > 500:
            user_content.append({
                "type": "text",
                "text": f"<reference>\n{self.reference_docs}\n</reference>",
                "cache_control": {"type": "ephemeral"},
            })

        # Add examples (cached as part of prefix)
        if self.examples:
            user_content.append({
                "type": "text",
                "text": f"<examples>\n{self.examples}\n</examples>",
                "cache_control": {"type": "ephemeral"},
            })

        # User input is always last (never cached because it varies)
        user_content.append({
            "type": "text",
            "text": self.user_input,
        })

        messages = [{"role": "user", "content": user_content}]
        return system, messages


# Example: A customer support bot with a large knowledge base
prompt = CacheOptimizedPrompt(
    system_prompt=(
        "You are a technical support agent for Acme Corp. "
        "Answer questions using only the provided reference material. "
        "If the answer is not in the reference, say so clearly."
    ),
    reference_docs="..." * 2000,  # Large product documentation
    examples=(
        "Q: How do I reset my password?\n"
        "A: Go to Settings > Account > Reset Password.\n\n"
        "Q: What are the system requirements?\n"
        "A: Windows 10+, macOS 12+, 8GB RAM minimum."
    ),
    user_input="How do I configure SSO for my organization?",
)

system, messages = prompt.build_messages()
```

### Measuring Cache Hit Rates

```python
from dataclasses import dataclass, field


@dataclass
class CacheMetrics:
    """Track prompt caching efficiency over time."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_input_tokens: int = 0
    cached_tokens: int = 0
    cache_creation_tokens: int = 0
    estimated_savings: float = 0.0

    def record(
        self,
        input_tokens: int,
        cache_read_tokens: int,
        cache_creation_tokens: int,
        model_pricing: ModelPricing,
    ) -> None:
        self.total_requests += 1
        self.total_input_tokens += input_tokens
        self.cached_tokens += cache_read_tokens
        self.cache_creation_tokens += cache_creation_tokens

        if cache_read_tokens > 0:
            self.cache_hits += 1
            # Savings = tokens that were read from cache *
            #           (full price - cached price)
            if model_pricing.cached_input_price_per_mtok is not None:
                price_diff = (
                    model_pricing.input_price_per_mtok
                    - model_pricing.cached_input_price_per_mtok
                ) / 1_000_000
                self.estimated_savings += cache_read_tokens * price_diff
        else:
            self.cache_misses += 1

    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests

    @property
    def token_cache_rate(self) -> float:
        if self.total_input_tokens == 0:
            return 0.0
        return self.cached_tokens / self.total_input_tokens

    def summary(self) -> str:
        return (
            f"Cache Performance:\n"
            f"  Requests:     {self.total_requests:,}\n"
            f"  Hit rate:     {self.hit_rate:.1%}\n"
            f"  Token cache:  {self.token_cache_rate:.1%}\n"
            f"  Savings:      ${self.estimated_savings:,.2f}\n"
        )
```

> **Swift Developer Note:** Prompt caching is conceptually similar to `NSURLCache` or the HTTP caching layer in `URLSession`. The difference is that with LLM caching, you are caching the *computation* of processing tokens (the KV-cache), not the response itself. The design principle is the same: put the most stable, reusable content first so the cache prefix is maximally reused. Think of it like how you would structure a `URLRequest` to maximize CDN cache hits by keeping query parameters consistent.

---

## 4. Model Selection Strategy

### When to Use Which Model Tier

Model selection is the single biggest cost lever. Choosing the right model for each task can cut costs by 10-50x without meaningful quality loss.

```python
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class TaskComplexity(Enum):
    SIMPLE = "simple"          # Classification, extraction, formatting
    MODERATE = "moderate"      # Summarization, Q&A, standard generation
    COMPLEX = "complex"        # Reasoning, analysis, creative writing
    EXPERT = "expert"          # Multi-step reasoning, code gen, research


class QualityRequirement(Enum):
    BEST_EFFORT = "best_effort"    # Minor errors acceptable
    PRODUCTION = "production"      # High quality, occasional errors ok
    CRITICAL = "critical"          # Must be correct, customer-facing


@dataclass
class ModelRecommendation:
    model_key: str
    reasoning: str
    estimated_cost_per_1k_calls: float
    expected_quality_score: float  # 0-1


def recommend_model(
    complexity: TaskComplexity,
    quality: QualityRequirement,
    avg_input_tokens: int = 500,
    avg_output_tokens: int = 200,
) -> ModelRecommendation:
    """
    Recommend a model based on task requirements.

    This is the kind of logic you would build for an enterprise
    customer to route requests to the appropriate model tier.
    """
    # Decision matrix
    model_map: dict[tuple[TaskComplexity, QualityRequirement], str] = {
        # Simple tasks: use the cheapest model that works
        (TaskComplexity.SIMPLE, QualityRequirement.BEST_EFFORT): "gpt-4o-mini",
        (TaskComplexity.SIMPLE, QualityRequirement.PRODUCTION): "claude-3-5-haiku",
        (TaskComplexity.SIMPLE, QualityRequirement.CRITICAL): "claude-3-5-haiku",

        # Moderate tasks: mid-tier models
        (TaskComplexity.MODERATE, QualityRequirement.BEST_EFFORT): "claude-3-5-haiku",
        (TaskComplexity.MODERATE, QualityRequirement.PRODUCTION): "claude-3-5-sonnet",
        (TaskComplexity.MODERATE, QualityRequirement.CRITICAL): "claude-3-5-sonnet",

        # Complex tasks: top-tier models
        (TaskComplexity.COMPLEX, QualityRequirement.BEST_EFFORT): "claude-3-5-sonnet",
        (TaskComplexity.COMPLEX, QualityRequirement.PRODUCTION): "claude-3-5-sonnet",
        (TaskComplexity.COMPLEX, QualityRequirement.CRITICAL): "gpt-4o",

        # Expert tasks: best available
        (TaskComplexity.EXPERT, QualityRequirement.BEST_EFFORT): "claude-3-5-sonnet",
        (TaskComplexity.EXPERT, QualityRequirement.PRODUCTION): "gpt-4o",
        (TaskComplexity.EXPERT, QualityRequirement.CRITICAL): "claude-3-opus",
    }

    model_key = model_map[(complexity, quality)]
    pricing = PRICING_CATALOG[model_key]
    cost_per_call = pricing.estimate_cost(avg_input_tokens, avg_output_tokens)

    # Quality heuristic (simplified)
    quality_scores = {
        "gpt-4o-mini": 0.70,
        "claude-3-5-haiku": 0.78,
        "gemini-1.5-flash": 0.72,
        "claude-3-5-sonnet": 0.90,
        "gpt-4o": 0.90,
        "gemini-1.5-pro": 0.87,
        "claude-3-opus": 0.95,
    }

    return ModelRecommendation(
        model_key=model_key,
        reasoning=f"{complexity.value} task with {quality.value} quality "
                  f"requirement -> {model_key}",
        estimated_cost_per_1k_calls=cost_per_call * 1000,
        expected_quality_score=quality_scores.get(model_key, 0.80),
    )


# Example usage
rec = recommend_model(
    TaskComplexity.MODERATE,
    QualityRequirement.PRODUCTION,
    avg_input_tokens=1000,
    avg_output_tokens=300,
)
print(f"Model: {rec.model_key}")
print(f"Reason: {rec.reasoning}")
print(f"Cost per 1K calls: ${rec.estimated_cost_per_1k_calls:.2f}")
print(f"Expected quality: {rec.expected_quality_score:.0%}")
```

### Dynamic Model Routing

In production, you can route requests to different models based on runtime conditions.

```python
from dataclasses import dataclass
from typing import Any


@dataclass
class RoutingContext:
    """Context used to make model routing decisions."""
    task_type: str
    input_length: int
    customer_tier: str            # "free", "pro", "enterprise"
    latency_budget_ms: int        # Maximum acceptable latency
    is_customer_facing: bool      # Whether the output goes directly to users
    current_budget_utilization: float  # 0.0 - 1.0


class ModelRouter:
    """Route requests to the optimal model based on context."""

    def __init__(self, pricing: dict[str, ModelPricing]) -> None:
        self.pricing = pricing

    def route(self, ctx: RoutingContext) -> str:
        """Select the best model for the given context."""

        # Budget pressure: downgrade when nearing budget limits
        if ctx.current_budget_utilization > 0.90:
            return "claude-3-5-haiku"

        # Latency-sensitive: use fastest model
        if ctx.latency_budget_ms < 500:
            return "claude-3-5-haiku"

        # Customer tier routing
        if ctx.customer_tier == "free":
            return "gpt-4o-mini"

        if ctx.customer_tier == "enterprise" and ctx.is_customer_facing:
            return "claude-3-5-sonnet"

        # Task-specific routing
        task_models: dict[str, str] = {
            "classification": "claude-3-5-haiku",
            "summarization": "claude-3-5-sonnet",
            "code_generation": "claude-3-5-sonnet",
            "creative_writing": "claude-3-5-sonnet",
            "complex_reasoning": "claude-3-opus",
            "data_extraction": "claude-3-5-haiku",
        }

        return task_models.get(ctx.task_type, "claude-3-5-sonnet")


# Usage
router = ModelRouter(PRICING_CATALOG)

context = RoutingContext(
    task_type="summarization",
    input_length=5000,
    customer_tier="enterprise",
    latency_budget_ms=3000,
    is_customer_facing=True,
    current_budget_utilization=0.45,
)

selected_model = router.route(context)
print(f"Routed to: {selected_model}")
```

### A/B Testing Model Quality vs Cost

```python
import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ABTestResult:
    model: str
    response: str
    latency_ms: float
    cost: float
    quality_score: float | None = None  # Filled in by evaluation


@dataclass
class ABTestConfig:
    model_a: str
    model_b: str
    traffic_split: float = 0.5  # Fraction going to model_a
    min_samples: int = 100


class ModelABTest:
    """Run A/B tests comparing two models on the same task."""

    def __init__(self, config: ABTestConfig) -> None:
        self.config = config
        self.results_a: list[ABTestResult] = []
        self.results_b: list[ABTestResult] = []

    def assign_model(self) -> str:
        """Randomly assign a request to model A or B."""
        if random.random() < self.config.traffic_split:
            return self.config.model_a
        return self.config.model_b

    def record_result(self, result: ABTestResult) -> None:
        if result.model == self.config.model_a:
            self.results_a.append(result)
        else:
            self.results_b.append(result)

    def summary(self) -> dict[str, Any]:
        """Compute summary statistics for both models."""
        def stats(results: list[ABTestResult]) -> dict[str, float]:
            if not results:
                return {"count": 0}
            costs = [r.cost for r in results]
            latencies = [r.latency_ms for r in results]
            qualities = [
                r.quality_score for r in results if r.quality_score is not None
            ]
            return {
                "count": len(results),
                "avg_cost": sum(costs) / len(costs),
                "avg_latency_ms": sum(latencies) / len(latencies),
                "avg_quality": (
                    sum(qualities) / len(qualities) if qualities else None
                ),
                "total_cost": sum(costs),
            }

        return {
            self.config.model_a: stats(self.results_a),
            self.config.model_b: stats(self.results_b),
            "has_enough_samples": (
                len(self.results_a) >= self.config.min_samples
                and len(self.results_b) >= self.config.min_samples
            ),
        }
```

> **Swift Developer Note:** Model routing is directly analogous to how you might implement feature flags or A/B testing in iOS using tools like LaunchDarkly or Firebase Remote Config. The `ModelRouter` follows the same strategy pattern you would use to switch between, say, on-device Core ML inference and a server-side model based on device capabilities, network conditions, or user tier. The key difference is that LLM model selection has a direct, per-request cost impact that device-side ML does not.

---

## 5. Latency Profiling and Optimization

### Measuring LLM Latency Components

LLM latency has distinct phases that you need to measure separately.

```python
import time
from dataclasses import dataclass, field


@dataclass
class LatencyBreakdown:
    """Detailed latency metrics for an LLM API call."""
    # Time to First Byte: how long before any response arrives
    ttfb_ms: float = 0.0

    # Token generation rate (for streaming)
    tokens_per_second: float = 0.0

    # Total wall-clock time for the entire call
    total_ms: float = 0.0

    # Network overhead (estimated)
    network_overhead_ms: float = 0.0

    # Number of output tokens generated
    output_tokens: int = 0

    # Computed metrics
    @property
    def generation_time_ms(self) -> float:
        """Time spent generating tokens (excludes TTFB)."""
        return self.total_ms - self.ttfb_ms

    @property
    def ms_per_token(self) -> float:
        if self.output_tokens == 0:
            return 0.0
        return self.generation_time_ms / self.output_tokens


class LatencyProfiler:
    """Profile LLM API call latency with detailed breakdown."""

    def __init__(self) -> None:
        self._measurements: list[LatencyBreakdown] = []

    def measure_streaming_call(
        self,
        stream_iterator,
        count_tokens_fn=None,
    ) -> tuple[str, LatencyBreakdown]:
        """
        Measure latency for a streaming API call.

        Args:
            stream_iterator: An iterable that yields text chunks
            count_tokens_fn: Optional function to count tokens in text
        """
        full_text = ""
        first_chunk_received = False
        start_time = time.perf_counter()
        ttfb_time = 0.0
        chunk_count = 0

        for chunk in stream_iterator:
            if not first_chunk_received:
                ttfb_time = time.perf_counter()
                first_chunk_received = True
            full_text += chunk
            chunk_count += 1

        end_time = time.perf_counter()

        total_ms = (end_time - start_time) * 1000
        ttfb_ms = (ttfb_time - start_time) * 1000 if first_chunk_received else total_ms

        # Estimate output tokens (roughly 1 token per 4 chars)
        output_tokens = len(full_text) // 4 if count_tokens_fn is None else count_tokens_fn(full_text)

        generation_ms = total_ms - ttfb_ms
        tps = (output_tokens / (generation_ms / 1000)) if generation_ms > 0 else 0

        breakdown = LatencyBreakdown(
            ttfb_ms=ttfb_ms,
            tokens_per_second=tps,
            total_ms=total_ms,
            output_tokens=output_tokens,
        )

        self._measurements.append(breakdown)
        return full_text, breakdown

    def measure_non_streaming_call(
        self,
        api_call_fn,
    ) -> tuple[object, LatencyBreakdown]:
        """Measure latency for a non-streaming API call."""
        start_time = time.perf_counter()
        response = api_call_fn()
        end_time = time.perf_counter()

        total_ms = (end_time - start_time) * 1000

        # For non-streaming, TTFB == total time (all-or-nothing)
        breakdown = LatencyBreakdown(
            ttfb_ms=total_ms,
            total_ms=total_ms,
            output_tokens=getattr(
                getattr(response, "usage", None), "output_tokens", 0
            ),
        )

        self._measurements.append(breakdown)
        return response, breakdown

    def percentile(self, metric: str, p: float) -> float:
        """Compute a percentile for a given metric across all measurements."""
        values = sorted(getattr(m, metric) for m in self._measurements)
        if not values:
            return 0.0
        idx = int(len(values) * p / 100)
        idx = min(idx, len(values) - 1)
        return values[idx]

    def summary(self) -> dict[str, float]:
        """Return summary statistics across all measurements."""
        if not self._measurements:
            return {}
        return {
            "count": len(self._measurements),
            "avg_total_ms": sum(m.total_ms for m in self._measurements) / len(self._measurements),
            "avg_ttfb_ms": sum(m.ttfb_ms for m in self._measurements) / len(self._measurements),
            "p50_total_ms": self.percentile("total_ms", 50),
            "p95_total_ms": self.percentile("total_ms", 95),
            "p99_total_ms": self.percentile("total_ms", 99),
            "avg_tokens_per_sec": sum(m.tokens_per_second for m in self._measurements) / len(self._measurements),
        }
```

### Streaming vs Non-Streaming Tradeoffs

```python
"""
Streaming vs Non-Streaming Decision Guide
==========================================

Use STREAMING when:
- User is waiting for a response (chat UI)
- Response will be long (>500 tokens)
- You want to display progressive results
- TTFB matters more than throughput

Use NON-STREAMING when:
- Response feeds into another system (pipeline)
- You need to validate/parse the full response before using it
- Response is short (<100 tokens)
- You are doing batch processing
- You need structured output (JSON) that must be complete to parse

Performance characteristics:
- Streaming TTFB: ~200-500ms (first token arrives quickly)
- Non-streaming TTFB: ~500-5000ms (waits for full generation)
- Streaming throughput: same total tokens/sec
- Non-streaming overhead: slightly less (no SSE framing)
"""

from enum import Enum


class ResponseMode(Enum):
    STREAMING = "streaming"
    NON_STREAMING = "non_streaming"


def choose_response_mode(
    is_user_facing: bool,
    expected_output_tokens: int,
    needs_full_parse: bool,
    latency_budget_ms: int,
) -> ResponseMode:
    """Decide whether to use streaming or non-streaming."""
    # If we need to parse the complete response (e.g., JSON), skip streaming
    if needs_full_parse:
        return ResponseMode.NON_STREAMING

    # Short responses: streaming overhead is not worth it
    if expected_output_tokens < 100:
        return ResponseMode.NON_STREAMING

    # User-facing with reasonable latency budget: stream for UX
    if is_user_facing and latency_budget_ms > 200:
        return ResponseMode.STREAMING

    # Tight latency budget: streaming gives faster TTFB
    if latency_budget_ms < 1000 and expected_output_tokens > 200:
        return ResponseMode.STREAMING

    return ResponseMode.NON_STREAMING
```

### Concurrent Request Patterns

```python
import asyncio
import time
from dataclasses import dataclass


@dataclass
class ConcurrencyResult:
    """Results from a concurrent batch of API calls."""
    total_requests: int
    successful: int
    failed: int
    total_time_ms: float
    avg_latency_ms: float
    throughput_rps: float  # requests per second


async def run_concurrent_requests(
    tasks: list,
    max_concurrency: int = 10,
) -> ConcurrencyResult:
    """
    Run multiple API calls concurrently with a semaphore.

    This pattern prevents overwhelming the API with too many
    simultaneous requests while maximizing throughput.
    """
    semaphore = asyncio.Semaphore(max_concurrency)
    results: list[dict] = []
    start_time = time.perf_counter()

    async def bounded_task(task_fn, index: int) -> dict:
        async with semaphore:
            task_start = time.perf_counter()
            try:
                result = await task_fn()
                return {
                    "index": index,
                    "success": True,
                    "latency_ms": (time.perf_counter() - task_start) * 1000,
                    "result": result,
                }
            except Exception as e:
                return {
                    "index": index,
                    "success": False,
                    "latency_ms": (time.perf_counter() - task_start) * 1000,
                    "error": str(e),
                }

    results = await asyncio.gather(
        *(bounded_task(task, i) for i, task in enumerate(tasks))
    )

    total_time = (time.perf_counter() - start_time) * 1000
    successful = sum(1 for r in results if r["success"])
    latencies = [r["latency_ms"] for r in results if r["success"]]

    return ConcurrencyResult(
        total_requests=len(tasks),
        successful=successful,
        failed=len(tasks) - successful,
        total_time_ms=total_time,
        avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
        throughput_rps=(successful / (total_time / 1000)) if total_time > 0 else 0,
    )
```

> **Swift Developer Note:** If you have profiled iOS apps with Instruments, this latency breakdown will feel natural. TTFB is analogous to measuring the time until `URLSessionDataDelegate.didReceive` fires for the first time. The streaming pattern maps directly to `URLSession` streaming with `AsyncBytes`. The concurrency pattern using `asyncio.Semaphore` is equivalent to using a `OperationQueue` with `maxConcurrentOperationCount` or Swift's `TaskGroup` with a manual concurrency limit. In both ecosystems, the goal is the same: maximize throughput without triggering rate limits.

---

## 6. Prompt Optimization for Cost

### Reducing Input Token Count

Every token in your prompt costs money. Shorter prompts that maintain quality directly reduce costs.

```python
from dataclasses import dataclass


@dataclass
class PromptOptimization:
    """Track the effect of prompt optimization."""
    original_tokens: int
    optimized_tokens: int
    quality_retained: float  # 0-1, measured by evaluation

    @property
    def token_reduction(self) -> float:
        return 1 - (self.optimized_tokens / self.original_tokens)

    @property
    def cost_reduction(self) -> float:
        """Cost reduction from input tokens (output stays the same)."""
        return self.token_reduction


# Technique 1: Remove verbose instructions
VERBOSE_PROMPT = """
I would like you to please analyze the following text and provide
a comprehensive summary. The summary should capture the main points,
key arguments, and important details. Please make sure to include
all relevant information while keeping the summary concise and
well-organized. The summary should be written in a professional tone
and should be easy to understand for a general audience.

Text to summarize:
{text}

Please provide your summary below:
"""

OPTIMIZED_PROMPT = """Summarize this text, covering main points and key arguments.

{text}"""


# Technique 2: Use structured output to reduce output tokens
VERBOSE_OUTPUT_PROMPT = """
Classify the sentiment of each review below. For each review, explain
your reasoning and then provide the final classification.
"""

STRUCTURED_OUTPUT_PROMPT = """
Classify sentiment as positive/negative/neutral. Return JSON array.
Format: [{"id": 1, "sentiment": "positive"}, ...]
"""


# Technique 3: System prompt compression
def compress_system_prompt(prompt: str) -> str:
    """
    Apply common compression techniques to system prompts.

    These techniques typically reduce token count by 20-40%
    with minimal quality impact.
    """
    import re

    # Remove filler phrases
    fillers = [
        r"I would like you to ",
        r"Please make sure to ",
        r"It is important that you ",
        r"You should always ",
        r"Please note that ",
        r"Keep in mind that ",
    ]
    result = prompt
    for filler in fillers:
        result = re.sub(filler, "", result, flags=re.IGNORECASE)

    # Collapse multiple spaces and newlines
    result = re.sub(r"\n{3,}", "\n\n", result)
    result = re.sub(r" {2,}", " ", result)

    return result.strip()
```

### Few-Shot vs Zero-Shot Cost Analysis

```python
from dataclasses import dataclass


@dataclass
class ShotStrategyAnalysis:
    """Compare zero-shot vs few-shot cost and quality."""
    strategy: str
    prompt_tokens: int
    avg_output_tokens: int
    quality_score: float
    cost_per_call: float

    @property
    def cost_per_quality_point(self) -> float:
        """Cost efficiency: how much does each quality point cost?"""
        if self.quality_score == 0:
            return float("inf")
        return self.cost_per_call / self.quality_score


def analyze_shot_strategies(
    base_prompt_tokens: int,
    tokens_per_example: int,
    output_tokens: int,
    model_pricing: ModelPricing,
    quality_scores: dict[int, float],
) -> list[ShotStrategyAnalysis]:
    """
    Analyze cost vs quality tradeoff for different numbers of examples.

    Args:
        base_prompt_tokens: Tokens in the base prompt (no examples)
        tokens_per_example: Average tokens per few-shot example
        output_tokens: Expected output tokens
        model_pricing: Pricing for the model being used
        quality_scores: Dict mapping num_examples -> quality score
    """
    results = []
    for num_examples, quality in quality_scores.items():
        total_input = base_prompt_tokens + (num_examples * tokens_per_example)
        cost = model_pricing.estimate_cost(total_input, output_tokens)

        results.append(ShotStrategyAnalysis(
            strategy=f"{num_examples}-shot",
            prompt_tokens=total_input,
            avg_output_tokens=output_tokens,
            quality_score=quality,
            cost_per_call=cost,
        ))

    return results


# Example: Sentiment classification task
strategies = analyze_shot_strategies(
    base_prompt_tokens=50,
    tokens_per_example=80,
    output_tokens=10,
    model_pricing=PRICING_CATALOG["claude-3-5-sonnet"],
    quality_scores={
        0: 0.82,   # Zero-shot
        2: 0.89,   # 2-shot
        5: 0.93,   # 5-shot
        10: 0.94,  # 10-shot (diminishing returns)
    },
)

print(f"{'Strategy':<12} {'Tokens':<10} {'Cost':<12} {'Quality':<10} {'Cost/Quality'}")
print("-" * 60)
for s in strategies:
    print(
        f"{s.strategy:<12} {s.prompt_tokens:<10} "
        f"${s.cost_per_call:<11.6f} {s.quality_score:<10.2f} "
        f"${s.cost_per_quality_point:.6f}"
    )
```

### System Prompt Optimization Patterns

```python
# Pattern 1: Role-based compression
# Instead of long behavioral descriptions, use a concise role

LONG_SYSTEM = """
You are an AI assistant that specializes in analyzing financial data.
You should always provide accurate and well-researched responses.
When analyzing data, you should consider multiple perspectives and
provide balanced viewpoints. You should cite sources when possible
and acknowledge uncertainty when appropriate. Your responses should
be professional in tone and suitable for a business audience.
"""

SHORT_SYSTEM = """You are a financial data analyst. Be accurate, balanced,
cite sources, flag uncertainty. Professional tone."""


# Pattern 2: Use XML tags for structure instead of prose
PROSE_INSTRUCTIONS = """
When the user gives you a customer support ticket, you should first
identify the category of the issue (billing, technical, account, other).
Then determine the priority (low, medium, high, urgent). Then draft
a response to the customer. Finally, note any internal actions needed.
"""

STRUCTURED_INSTRUCTIONS = """Process support tickets with this output format:
<category>billing|technical|account|other</category>
<priority>low|medium|high|urgent</priority>
<response>Customer-facing reply</response>
<internal_actions>Internal team notes</internal_actions>"""


# Pattern 3: Conditional instructions (only include when relevant)
def build_system_prompt(
    task: str,
    include_safety: bool = True,
    include_formatting: bool = False,
    custom_rules: list[str] | None = None,
) -> str:
    """Build a minimal system prompt with only relevant instructions."""
    parts = [f"Task: {task}"]

    if include_safety:
        parts.append("Decline harmful or illegal requests.")

    if include_formatting:
        parts.append("Use markdown formatting with headers and bullet points.")

    if custom_rules:
        rules_text = "; ".join(custom_rules)
        parts.append(f"Rules: {rules_text}")

    return " ".join(parts)
```

> **Swift Developer Note:** Prompt optimization has a direct parallel in iOS development: reducing payload sizes for network requests. Just as you would minimize JSON payloads, use `Codable` with custom keys, or compress data before sending to a REST API, prompt optimization is about sending fewer tokens to achieve the same result. The key insight from both domains: measure first. Do not optimize prompts based on intuition alone -- run evaluations (like A/B tests or eval suites) to confirm that shorter prompts maintain quality, just as you would profile network performance in Instruments before and after optimization.

---

## 7. Batch Processing and Throughput

### Anthropic Batch API

The Batch API allows you to send large volumes of requests at 50% reduced cost, with results returned within 24 hours.

```python
import anthropic
import json
from dataclasses import dataclass


@dataclass
class BatchRequest:
    """A single request within a batch."""
    custom_id: str
    prompt: str
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 1024
    system: str = ""


def create_anthropic_batch(
    client: anthropic.Anthropic,
    requests: list[BatchRequest],
) -> str:
    """
    Submit a batch of requests to Anthropic's Batch API.

    Returns the batch ID for polling results.
    Batch processing costs 50% less than real-time API calls.
    """
    batch_requests = []
    for req in requests:
        params: dict = {
            "model": req.model,
            "max_tokens": req.max_tokens,
            "messages": [{"role": "user", "content": req.prompt}],
        }
        if req.system:
            params["system"] = req.system

        batch_requests.append({
            "custom_id": req.custom_id,
            "params": params,
        })

    batch = client.messages.batches.create(requests=batch_requests)
    return batch.id


def poll_batch_results(
    client: anthropic.Anthropic,
    batch_id: str,
) -> list[dict]:
    """Poll for batch results (simplified -- production code would use webhooks)."""
    import time

    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            break
        time.sleep(60)  # Check every minute

    results = []
    for result in client.messages.batches.results(batch_id):
        results.append({
            "custom_id": result.custom_id,
            "result": result.result,
        })
    return results


# Example: Batch-classify 1000 support tickets
def batch_classify_tickets(
    client: anthropic.Anthropic,
    tickets: list[dict[str, str]],
) -> str:
    """Classify support tickets using the batch API for 50% cost savings."""
    batch_requests = [
        BatchRequest(
            custom_id=f"ticket-{ticket['id']}",
            prompt=f"Classify this support ticket into exactly one category "
                   f"(billing/technical/account/other): {ticket['text']}",
            model="claude-3-5-haiku-20241022",  # Cheap model for classification
            max_tokens=50,
            system="Return only the category name, nothing else.",
        )
        for ticket in tickets
    ]

    return create_anthropic_batch(client, batch_requests)
```

### Async Concurrent Requests with Rate Limiting

```python
import asyncio
import time
from collections import deque
from dataclasses import dataclass, field


class RateLimiter:
    """
    Token bucket rate limiter for API calls.

    Enforces both requests-per-minute and tokens-per-minute limits
    as required by most LLM API providers.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        tokens_per_minute: int = 100_000,
    ) -> None:
        self.rpm_limit = requests_per_minute
        self.tpm_limit = tokens_per_minute
        self._request_timestamps: deque[float] = deque()
        self._token_counts: deque[tuple[float, int]] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self, estimated_tokens: int = 1000) -> None:
        """Wait until we can make a request within rate limits."""
        while True:
            async with self._lock:
                now = time.monotonic()
                window_start = now - 60.0

                # Prune old entries
                while (
                    self._request_timestamps
                    and self._request_timestamps[0] < window_start
                ):
                    self._request_timestamps.popleft()

                while (
                    self._token_counts
                    and self._token_counts[0][0] < window_start
                ):
                    self._token_counts.popleft()

                # Check limits
                current_rpm = len(self._request_timestamps)
                current_tpm = sum(t[1] for t in self._token_counts)

                if (
                    current_rpm < self.rpm_limit
                    and current_tpm + estimated_tokens <= self.tpm_limit
                ):
                    self._request_timestamps.append(now)
                    self._token_counts.append((now, estimated_tokens))
                    return

            # Back off and retry
            await asyncio.sleep(0.5)


class ConcurrentProcessor:
    """Process multiple LLM requests concurrently with rate limiting."""

    def __init__(
        self,
        rate_limiter: RateLimiter,
        max_concurrency: int = 10,
        max_retries: int = 3,
    ) -> None:
        self.rate_limiter = rate_limiter
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.max_retries = max_retries

    async def process_single(
        self,
        task_fn,
        task_id: str,
        estimated_tokens: int = 1000,
    ) -> dict:
        """Process a single task with rate limiting and retries."""
        async with self.semaphore:
            for attempt in range(self.max_retries):
                await self.rate_limiter.acquire(estimated_tokens)
                try:
                    result = await task_fn()
                    return {"id": task_id, "success": True, "result": result}
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        return {"id": task_id, "success": False, "error": str(e)}
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)

        return {"id": task_id, "success": False, "error": "Max retries exceeded"}

    async def process_batch(
        self,
        tasks: list[tuple[str, callable, int]],
    ) -> list[dict]:
        """
        Process a batch of tasks concurrently.

        Args:
            tasks: List of (task_id, async_callable, estimated_tokens) tuples
        """
        coros = [
            self.process_single(fn, task_id, tokens)
            for task_id, fn, tokens in tasks
        ]
        return await asyncio.gather(*coros)
```

### Queue-Based Architecture

```python
import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LLMJob:
    """A job in the LLM processing queue."""
    job_id: str
    prompt: str
    model: str
    priority: int = 0          # Higher = more urgent
    max_tokens: int = 1024
    status: JobStatus = JobStatus.PENDING
    result: str | None = None
    error: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime | None = None
    cost: float = 0.0

    def __lt__(self, other: "LLMJob") -> bool:
        """Higher priority jobs come first."""
        return self.priority > other.priority


class LLMJobQueue:
    """
    Priority queue for LLM processing jobs.

    In production, this would be backed by Redis, RabbitMQ, or SQS.
    This in-memory implementation demonstrates the pattern.
    """

    def __init__(self, max_queue_size: int = 10_000) -> None:
        self._queue: asyncio.PriorityQueue[LLMJob] = asyncio.PriorityQueue(
            maxsize=max_queue_size
        )
        self._jobs: dict[str, LLMJob] = {}
        self._completed_count: int = 0
        self._failed_count: int = 0

    async def submit(self, job: LLMJob) -> str:
        """Submit a job to the queue."""
        self._jobs[job.job_id] = job
        await self._queue.put(job)
        logger.info(f"Job {job.job_id} submitted (priority={job.priority})")
        return job.job_id

    async def get_next(self) -> LLMJob:
        """Get the next highest-priority job."""
        job = await self._queue.get()
        job.status = JobStatus.PROCESSING
        return job

    def complete(self, job: LLMJob, result: str, cost: float) -> None:
        """Mark a job as completed."""
        job.status = JobStatus.COMPLETED
        job.result = result
        job.cost = cost
        job.completed_at = datetime.now(timezone.utc)
        self._completed_count += 1

    def fail(self, job: LLMJob, error: str) -> None:
        """Mark a job as failed."""
        job.status = JobStatus.FAILED
        job.error = error
        job.completed_at = datetime.now(timezone.utc)
        self._failed_count += 1

    def get_status(self, job_id: str) -> dict[str, Any]:
        """Get the status of a specific job."""
        job = self._jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "result": job.result,
            "error": job.error,
            "cost": job.cost,
        }

    @property
    def queue_depth(self) -> int:
        return self._queue.qsize()

    @property
    def stats(self) -> dict[str, int]:
        return {
            "queue_depth": self.queue_depth,
            "completed": self._completed_count,
            "failed": self._failed_count,
            "total_submitted": len(self._jobs),
        }
```

> **Swift Developer Note:** The queue pattern here is directly analogous to `OperationQueue` in Foundation or structured concurrency with `TaskGroup` in Swift. The `LLMJobQueue` plays the same role as `NSOperationQueue` with `maxConcurrentOperationCount` -- it controls concurrency, enforces ordering via priorities, and provides status tracking. In an iOS app making many network requests, you would use a similar pattern to avoid overwhelming the network stack. The key difference is that LLM API rate limits are much stricter than typical REST APIs, making the rate limiter component essential.

---

## 8. Building a Cost Dashboard

### Real-Time Cost Tracking

```python
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any


@dataclass
class UsageRecord:
    """A single API usage event."""
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    cost: float
    customer_id: str
    feature: str            # Which product feature triggered this call
    latency_ms: float
    request_id: str


class CostDashboard:
    """
    Real-time cost tracking and analytics dashboard.

    In production, this data would live in a time-series database
    (InfluxDB, TimescaleDB) or a data warehouse (BigQuery, Snowflake).
    """

    def __init__(self, pricing: dict[str, ModelPricing]) -> None:
        self.pricing = pricing
        self._records: list[UsageRecord] = []
        self._customer_budgets: dict[str, float] = {}

    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        customer_id: str,
        feature: str,
        latency_ms: float,
        request_id: str,
    ) -> UsageRecord:
        """Record a single API usage event."""
        model_key = self._find_model_key(model)
        pricing = self.pricing.get(model_key)

        cost = 0.0
        if pricing:
            cost = pricing.estimate_cost(input_tokens, output_tokens, cached_tokens)

        record = UsageRecord(
            timestamp=datetime.now(timezone.utc),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            cost=cost,
            customer_id=customer_id,
            feature=feature,
            latency_ms=latency_ms,
            request_id=request_id,
        )
        self._records.append(record)
        return record

    def _find_model_key(self, model_name: str) -> str:
        """Map a full model name to a pricing catalog key."""
        for key, pricing in self.pricing.items():
            if key in model_name or pricing.model_name in model_name:
                return key
        return model_name

    def total_cost(
        self,
        since: datetime | None = None,
        customer_id: str | None = None,
    ) -> float:
        """Get total cost, optionally filtered by time and customer."""
        records = self._filter_records(since=since, customer_id=customer_id)
        return sum(r.cost for r in records)

    def cost_by_model(
        self, since: datetime | None = None
    ) -> dict[str, float]:
        """Break down costs by model."""
        records = self._filter_records(since=since)
        costs: dict[str, float] = defaultdict(float)
        for r in records:
            costs[r.model] += r.cost
        return dict(costs)

    def cost_by_customer(
        self, since: datetime | None = None
    ) -> dict[str, float]:
        """Break down costs by customer."""
        records = self._filter_records(since=since)
        costs: dict[str, float] = defaultdict(float)
        for r in records:
            costs[r.customer_id] += r.cost
        return dict(sorted(costs.items(), key=lambda x: x[1], reverse=True))

    def cost_by_feature(
        self, since: datetime | None = None
    ) -> dict[str, float]:
        """Break down costs by product feature."""
        records = self._filter_records(since=since)
        costs: dict[str, float] = defaultdict(float)
        for r in records:
            costs[r.feature] += r.cost
        return dict(sorted(costs.items(), key=lambda x: x[1], reverse=True))

    def hourly_cost_trend(
        self, hours: int = 24
    ) -> list[dict[str, Any]]:
        """Get hourly cost trend for the last N hours."""
        now = datetime.now(timezone.utc)
        trends = []
        for h in range(hours):
            hour_start = now - timedelta(hours=hours - h)
            hour_end = hour_start + timedelta(hours=1)
            records = [
                r for r in self._records
                if hour_start <= r.timestamp < hour_end
            ]
            trends.append({
                "hour": hour_start.isoformat(),
                "cost": sum(r.cost for r in records),
                "requests": len(records),
                "avg_latency_ms": (
                    sum(r.latency_ms for r in records) / len(records)
                    if records else 0
                ),
            })
        return trends

    def _filter_records(
        self,
        since: datetime | None = None,
        customer_id: str | None = None,
    ) -> list[UsageRecord]:
        records = self._records
        if since:
            records = [r for r in records if r.timestamp >= since]
        if customer_id:
            records = [r for r in records if r.customer_id == customer_id]
        return records
```

### Per-Customer Usage and Budget Enforcement

```python
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class CustomerBudget:
    customer_id: str
    monthly_budget: float
    alert_threshold: float = 0.80  # Alert at 80% utilization
    hard_limit: bool = False       # If True, reject requests over budget


class CustomerBudgetEnforcer:
    """Enforce per-customer spending limits."""

    def __init__(self, dashboard: CostDashboard) -> None:
        self.dashboard = dashboard
        self._budgets: dict[str, CustomerBudget] = {}

    def set_budget(self, budget: CustomerBudget) -> None:
        self._budgets[budget.customer_id] = budget

    def check_budget(self, customer_id: str) -> dict:
        """
        Check if a customer is within budget.

        Returns a dict with budget status and whether to proceed.
        """
        budget = self._budgets.get(customer_id)
        if not budget:
            return {"allowed": True, "reason": "No budget configured"}

        # Get spending for current month
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        spent = self.dashboard.total_cost(
            since=month_start,
            customer_id=customer_id,
        )

        utilization = spent / budget.monthly_budget if budget.monthly_budget > 0 else 0
        remaining = budget.monthly_budget - spent

        result = {
            "customer_id": customer_id,
            "budget": budget.monthly_budget,
            "spent": spent,
            "remaining": remaining,
            "utilization": utilization,
            "allowed": True,
            "alert": False,
        }

        if utilization >= 1.0 and budget.hard_limit:
            result["allowed"] = False
            result["reason"] = "Monthly budget exceeded"
            result["alert"] = True
        elif utilization >= budget.alert_threshold:
            result["alert"] = True
            result["reason"] = f"Budget {utilization:.0%} utilized"

        return result

    def enforce(self, customer_id: str, estimated_cost: float) -> bool:
        """
        Check if a request should proceed based on budget.

        Call this before every API call for budget-enforced customers.
        Returns True if the request should proceed.
        """
        status = self.check_budget(customer_id)
        if not status["allowed"]:
            return False
        if status["remaining"] < estimated_cost:
            budget = self._budgets.get(customer_id)
            if budget and budget.hard_limit:
                return False
        return True
```

### Cost Anomaly Detection

```python
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta


@dataclass
class CostAnomaly:
    """A detected cost anomaly."""
    timestamp: datetime
    metric: str
    expected_value: float
    actual_value: float
    deviation_sigma: float
    description: str


class CostAnomalyDetector:
    """
    Detect unusual spending patterns using statistical analysis.

    Uses a simple z-score approach: if the current period's cost
    is more than N standard deviations from the rolling mean,
    flag it as an anomaly.
    """

    def __init__(
        self,
        dashboard: CostDashboard,
        lookback_hours: int = 168,  # 1 week
        sigma_threshold: float = 2.5,
    ) -> None:
        self.dashboard = dashboard
        self.lookback_hours = lookback_hours
        self.sigma_threshold = sigma_threshold

    def check_hourly_anomalies(self) -> list[CostAnomaly]:
        """Check for cost anomalies in the most recent hour."""
        trends = self.dashboard.hourly_cost_trend(hours=self.lookback_hours)
        if len(trends) < 24:
            return []  # Not enough data

        # Use all but the last hour as baseline
        baseline_costs = [t["cost"] for t in trends[:-1] if t["cost"] > 0]
        if len(baseline_costs) < 10:
            return []

        current = trends[-1]
        mean_cost = statistics.mean(baseline_costs)
        std_cost = statistics.stdev(baseline_costs) if len(baseline_costs) > 1 else 0

        anomalies = []

        if std_cost > 0:
            z_score = (current["cost"] - mean_cost) / std_cost
            if abs(z_score) > self.sigma_threshold:
                anomalies.append(CostAnomaly(
                    timestamp=datetime.now(timezone.utc),
                    metric="hourly_cost",
                    expected_value=mean_cost,
                    actual_value=current["cost"],
                    deviation_sigma=z_score,
                    description=(
                        f"Hourly cost ${current['cost']:.2f} is "
                        f"{z_score:.1f} sigma from mean ${mean_cost:.2f}"
                    ),
                ))

        # Also check request volume
        baseline_requests = [
            t["requests"] for t in trends[:-1] if t["requests"] > 0
        ]
        if baseline_requests and len(baseline_requests) > 1:
            mean_req = statistics.mean(baseline_requests)
            std_req = statistics.stdev(baseline_requests)
            if std_req > 0:
                z_score_req = (current["requests"] - mean_req) / std_req
                if abs(z_score_req) > self.sigma_threshold:
                    anomalies.append(CostAnomaly(
                        timestamp=datetime.now(timezone.utc),
                        metric="hourly_requests",
                        expected_value=mean_req,
                        actual_value=current["requests"],
                        deviation_sigma=z_score_req,
                        description=(
                            f"Hourly requests {current['requests']} is "
                            f"{z_score_req:.1f} sigma from mean {mean_req:.0f}"
                        ),
                    ))

        return anomalies

    def check_customer_anomalies(
        self,
        customer_id: str,
    ) -> list[CostAnomaly]:
        """Check for anomalous spending by a specific customer."""
        now = datetime.now(timezone.utc)
        anomalies = []

        # Compare today's spend to the daily average over the past week
        daily_costs = []
        for day_offset in range(1, 8):
            day_start = (now - timedelta(days=day_offset)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            day_end = day_start + timedelta(days=1)
            cost = sum(
                r.cost for r in self.dashboard._filter_records(since=day_start)
                if r.timestamp < day_end and r.customer_id == customer_id
            )
            daily_costs.append(cost)

        if len(daily_costs) < 3:
            return anomalies

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_cost = self.dashboard.total_cost(
            since=today_start, customer_id=customer_id
        )

        mean = statistics.mean(daily_costs)
        std = statistics.stdev(daily_costs) if len(daily_costs) > 1 else 0

        if std > 0:
            z = (today_cost - mean) / std
            if abs(z) > self.sigma_threshold:
                anomalies.append(CostAnomaly(
                    timestamp=now,
                    metric=f"daily_cost_{customer_id}",
                    expected_value=mean,
                    actual_value=today_cost,
                    deviation_sigma=z,
                    description=(
                        f"Customer {customer_id}: today's spend "
                        f"${today_cost:.2f} vs avg ${mean:.2f} "
                        f"({z:.1f} sigma)"
                    ),
                ))

        return anomalies
```

### Putting It All Together: Dashboard API

```python
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any


@dataclass
class DashboardSnapshot:
    """A point-in-time snapshot of cost metrics."""
    timestamp: datetime
    total_cost_today: float
    total_cost_this_month: float
    cost_by_model: dict[str, float]
    cost_by_customer: dict[str, float]
    cost_by_feature: dict[str, float]
    hourly_trend: list[dict[str, Any]]
    anomalies: list[CostAnomaly]
    budget_alerts: list[dict[str, Any]]


def generate_dashboard_snapshot(
    dashboard: CostDashboard,
    anomaly_detector: CostAnomalyDetector,
    budget_enforcer: CustomerBudgetEnforcer,
) -> DashboardSnapshot:
    """Generate a complete dashboard snapshot."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Check budgets for all known customers
    budget_alerts = []
    for customer_id in budget_enforcer._budgets:
        status = budget_enforcer.check_budget(customer_id)
        if status.get("alert"):
            budget_alerts.append(status)

    return DashboardSnapshot(
        timestamp=now,
        total_cost_today=dashboard.total_cost(since=today_start),
        total_cost_this_month=dashboard.total_cost(since=month_start),
        cost_by_model=dashboard.cost_by_model(since=month_start),
        cost_by_customer=dashboard.cost_by_customer(since=month_start),
        cost_by_feature=dashboard.cost_by_feature(since=month_start),
        hourly_trend=dashboard.hourly_cost_trend(hours=24),
        anomalies=anomaly_detector.check_hourly_anomalies(),
        budget_alerts=budget_alerts,
    )


# Example: Wire up the full system
def create_cost_monitoring_stack() -> tuple[
    CostDashboard, CostAnomalyDetector, CustomerBudgetEnforcer
]:
    """Create a complete cost monitoring stack."""
    dashboard = CostDashboard(PRICING_CATALOG)

    anomaly_detector = CostAnomalyDetector(
        dashboard=dashboard,
        lookback_hours=168,
        sigma_threshold=2.5,
    )

    budget_enforcer = CustomerBudgetEnforcer(dashboard=dashboard)

    # Set up customer budgets
    budget_enforcer.set_budget(CustomerBudget(
        customer_id="acme-corp",
        monthly_budget=5000.0,
        alert_threshold=0.80,
        hard_limit=True,
    ))
    budget_enforcer.set_budget(CustomerBudget(
        customer_id="startup-xyz",
        monthly_budget=500.0,
        alert_threshold=0.75,
        hard_limit=False,
    ))

    return dashboard, anomaly_detector, budget_enforcer
```

> **Swift Developer Note:** This dashboard pattern is analogous to building analytics dashboards in iOS using tools like Firebase Analytics or custom Instruments traces. The `CostDashboard` collects events just like you would log events with `os_signpost` or Firebase. The anomaly detection is similar to how Xcode Organizer flags performance regressions across app versions. The big difference: in LLM applications, cost anomalies can translate directly to unexpected bills in real dollars, making this monitoring much more operationally critical than most iOS performance metrics.

---

## 9. Comprehensive Optimization Workflow

### End-to-End Optimization Pipeline

Here is a complete workflow that ties together all the concepts from this module: model routing, cost estimation, caching, budget enforcement, and metrics collection.

```python
import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class OptimizedRequest:
    """A fully optimized LLM request with all cost controls."""
    request_id: str
    customer_id: str
    feature: str
    prompt: str
    system_prompt: str = ""
    max_tokens: int = 1024
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizedResponse:
    """Response from the optimized pipeline."""
    request_id: str
    text: str
    model_used: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    cost: float
    latency_ms: float
    cache_hit: bool
    budget_remaining: float


class OptimizedLLMPipeline:
    """
    Production-grade LLM pipeline with all cost optimizations.

    This is the kind of class you would build for an enterprise
    customer as a solutions engineer. It combines:
    - Model routing based on task and budget
    - Pre-call cost estimation
    - Budget enforcement
    - Cache-optimized prompt structure
    - Latency tracking
    - Cost recording and anomaly detection
    """

    def __init__(
        self,
        router: ModelRouter,
        estimator: CostEstimator,
        dashboard: CostDashboard,
        budget_enforcer: CustomerBudgetEnforcer,
        cache_metrics: CacheMetrics,
    ) -> None:
        self.router = router
        self.estimator = estimator
        self.dashboard = dashboard
        self.budget_enforcer = budget_enforcer
        self.cache_metrics = cache_metrics

    async def process(
        self,
        request: OptimizedRequest,
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        quality: QualityRequirement = QualityRequirement.PRODUCTION,
    ) -> OptimizedResponse:
        """Process a request through the full optimization pipeline."""
        start_time = time.perf_counter()
        request_id = request.request_id or str(uuid.uuid4())

        # Step 1: Check budget
        budget_status = self.budget_enforcer.check_budget(request.customer_id)
        if not budget_status["allowed"]:
            raise BudgetExceededError(
                f"Customer {request.customer_id} has exceeded their budget. "
                f"Spent: ${budget_status['spent']:.2f} / "
                f"${budget_status['budget']:.2f}"
            )

        # Step 2: Route to optimal model
        routing_ctx = RoutingContext(
            task_type=request.feature,
            input_length=len(request.prompt),
            customer_tier=request.metadata.get("customer_tier", "pro"),
            latency_budget_ms=request.metadata.get("latency_budget_ms", 5000),
            is_customer_facing=request.metadata.get("is_customer_facing", True),
            current_budget_utilization=budget_status.get("utilization", 0),
        )
        selected_model = self.router.route(routing_ctx)

        # Step 3: Estimate cost
        estimate = self.estimator.estimate(selected_model, request.prompt)
        if not estimate.within_budget:
            # Downgrade model if estimate exceeds remaining budget
            selected_model = "claude-3-5-haiku"
            estimate = self.estimator.estimate(selected_model, request.prompt)

        # Step 4: Make the API call (simulated here)
        # In production, this would call the actual API
        response_text = f"[Simulated response from {selected_model}]"
        input_tokens = estimate.input_tokens
        output_tokens = estimate.estimated_output_tokens
        cached_tokens = int(input_tokens * 0.6)  # Simulated cache hit

        latency_ms = (time.perf_counter() - start_time) * 1000

        # Step 5: Calculate actual cost
        pricing = PRICING_CATALOG[selected_model]
        actual_cost = pricing.estimate_cost(
            input_tokens, output_tokens, cached_tokens
        )

        # Step 6: Record everything
        self.estimator.record_actual_cost(actual_cost)
        self.dashboard.record_usage(
            model=selected_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            customer_id=request.customer_id,
            feature=request.feature,
            latency_ms=latency_ms,
            request_id=request_id,
        )
        self.cache_metrics.record(
            input_tokens=input_tokens,
            cache_read_tokens=cached_tokens,
            cache_creation_tokens=0,
            model_pricing=pricing,
        )

        # Step 7: Return optimized response
        updated_budget = self.budget_enforcer.check_budget(request.customer_id)
        return OptimizedResponse(
            request_id=request_id,
            text=response_text,
            model_used=selected_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            cost=actual_cost,
            latency_ms=latency_ms,
            cache_hit=cached_tokens > 0,
            budget_remaining=updated_budget.get("remaining", 0),
        )


class BudgetExceededError(Exception):
    """Raised when a customer exceeds their spending budget."""
    pass
```

---

## 10. Swift Comparison

### Mapping LLM Optimization to iOS Performance Engineering

The skills you built profiling iOS apps translate directly to LLM cost optimization. Here is how concepts map across.

| iOS / Swift Concept | LLM Cost Optimization Equivalent |
|---|---|
| Instruments (Time Profiler) | `LatencyProfiler` -- measure TTFB, tokens/sec |
| Network Link Conditioner | Rate limiting simulation, latency budgets |
| Energy Impact gauge (Xcode) | Cost per request tracking |
| `URLSession` background tasks | Batch API (50% discount for async processing) |
| `NSURLCache` / HTTP caching | Prompt caching (KV-cache reuse) |
| Core ML on-device inference | Choosing small models (Haiku) for simple tasks |
| `OperationQueue.maxConcurrentOperationCount` | `asyncio.Semaphore` for concurrent requests |
| App Store Connect analytics | `CostDashboard` for usage tracking |
| MetricKit crash/performance reports | `CostAnomalyDetector` for spending anomalies |
| `Codable` payload size optimization | Prompt compression, structured output |
| Feature flags (LaunchDarkly) | `ModelRouter` for dynamic model selection |
| CloudKit quota management | `CustomerBudgetEnforcer` for per-customer limits |

### Code Pattern Comparison

```python
# Python: Concurrent API calls with rate limiting
import asyncio

async def process_batch_python(items: list[str], max_concurrent: int = 5):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_one(item: str) -> str:
        async with semaphore:
            return await call_llm_api(item)

    return await asyncio.gather(*(process_one(i) for i in items))
```

```swift
// Swift equivalent: Concurrent network calls with TaskGroup
func processBatch(items: [String], maxConcurrent: Int = 5) async throws -> [String] {
    try await withThrowingTaskGroup(of: String.self) { group in
        var results: [String] = []
        var inFlight = 0

        for item in items {
            if inFlight >= maxConcurrent {
                if let result = try await group.next() {
                    results.append(result)
                    inFlight -= 1
                }
            }
            group.addTask { try await self.callLLMAPI(item) }
            inFlight += 1
        }

        for try await result in group {
            results.append(result)
        }
        return results
    }
}
```

```python
# Python: Budget enforcement middleware
class BudgetMiddleware:
    def __init__(self, enforcer: CustomerBudgetEnforcer):
        self.enforcer = enforcer

    async def __call__(self, request: OptimizedRequest) -> OptimizedResponse:
        if not self.enforcer.enforce(request.customer_id, estimated_cost=0.01):
            raise BudgetExceededError("Budget exceeded")
        return await self.next(request)
```

```swift
// Swift equivalent: URLSession delegate for request gating
class BudgetURLProtocol: URLProtocol {
    override class func canInit(with request: URLRequest) -> Bool {
        // Check budget before allowing the request
        guard let customerId = request.value(forHTTPHeaderField: "X-Customer-ID") else {
            return false
        }
        return BudgetEnforcer.shared.isWithinBudget(customerId: customerId)
    }
}
```

> **Swift Developer Note:** The fundamental mental model is the same across both platforms: measure, analyze, optimize, monitor. In iOS, you reach for Instruments and Xcode Organizer. In LLM engineering, you build the same instrumentation in code because there is no built-in IDE tooling. The biggest adjustment for Swift developers is that LLM optimization has a direct financial cost dimension that iOS development typically lacks. Every inefficiency in your prompt, every unnecessary use of Opus when Haiku would suffice, translates to real dollars on a monthly invoice. This makes the optimization work feel more like infrastructure cost management (AWS bill optimization) than traditional app performance tuning.

---

## 11. Interview Focus

### Common Interview Questions and How to Answer Them

**Q1: "A customer is spending $80K/month on Claude API calls. Walk me through how you would reduce their costs by 50%."**

Framework for answering:

```python
"""
Cost Reduction Playbook (use this structure in interviews)
=========================================================

1. MEASURE: Understand current spending
   - Break down costs by model, feature, and customer segment
   - Identify the top 3-5 cost drivers (usually 80/20 rule applies)
   - Measure cache hit rates and token distributions

2. QUICK WINS (Week 1-2):
   a) Model downgrade: Identify tasks using Sonnet/Opus that work
      fine with Haiku (classification, extraction, simple Q&A)
      -> Typical savings: 10-20x per call on those tasks
   b) Prompt caching: Structure prompts for cache reuse
      -> Typical savings: 90% on cached input tokens
   c) Prompt compression: Remove verbose instructions
      -> Typical savings: 20-40% token reduction

3. MEDIUM-TERM (Week 3-6):
   a) Model routing: Build intelligent routing based on task
      complexity and quality requirements
   b) Batch API: Move non-real-time workloads to batch (50% off)
   c) Output optimization: Use structured output (JSON) to
      reduce output tokens
   d) Few-shot reduction: Test if fewer examples maintain quality

4. LONG-TERM (Month 2+):
   a) Fine-tuning: For high-volume, narrow tasks, a fine-tuned
      smaller model can match larger model quality at fraction
      of cost
   b) Evaluation pipeline: Automated quality checks to safely
      downgrade models
   c) Caching layer: Cache frequent identical queries at the
      application level (not just prompt caching)

5. MONITORING:
   - Set up per-feature cost tracking
   - Budget alerts at 75%, 90%, 100%
   - Anomaly detection for spending spikes
   - Weekly cost review meetings with customer
"""
```

**Q2: "How do you decide between using Claude Haiku vs Sonnet vs Opus for a given feature?"**

```python
"""
Model Selection Framework
=========================

Step 1: Define the task taxonomy
- SIMPLE: Classification, extraction, formatting, routing
  -> Haiku (10-20x cheaper than Sonnet)
- MODERATE: Summarization, Q&A, standard generation
  -> Sonnet (best price/performance)
- COMPLEX: Multi-step reasoning, code generation, analysis
  -> Sonnet or Opus (depends on quality requirements)
- EXPERT: Research, creative writing, complex code review
  -> Opus (when quality is paramount)

Step 2: Run an evaluation
- Create a test set of 50-100 representative inputs
- Run all candidate models on the test set
- Score outputs on task-specific metrics
- Calculate cost per quality point

Step 3: Set quality thresholds
- If Haiku scores >= 90% of Sonnet quality -> use Haiku
- If Sonnet scores >= 95% of Opus quality -> use Sonnet
- Only use Opus when the quality gap is meaningful

Step 4: Implement routing
- Start with static routing (task type -> model)
- Graduate to dynamic routing (based on input complexity)
- Add fallback logic (if Haiku fails, retry with Sonnet)
"""
```

**Q3: "Design a system that handles 10,000 LLM API calls per minute with cost controls."**

```python
"""
High-Throughput System Design
=============================

Architecture:
[Load Balancer]
      |
[API Gateway] -- Budget check, rate limiting, model routing
      |
[Request Queue] -- Priority queue (Redis/SQS)
      |
[Worker Pool] -- N async workers with semaphore
      |
[LLM APIs] -- Multi-provider with failover
      |
[Results Cache] -- Application-level response cache
      |
[Metrics Pipeline] -- Async cost/latency recording

Key components:

1. API Gateway:
   - Authenticate customer
   - Check budget (in-memory cache of budgets, async refresh)
   - Route to model based on request metadata
   - Reject if over budget (hard limit) or queue if over soft limit

2. Request Queue:
   - Priority queue (enterprise > pro > free tier)
   - Dead letter queue for failed requests
   - Configurable TTL per priority level

3. Worker Pool:
   - Async workers with configurable concurrency
   - Per-provider rate limiters (separate RPM/TPM buckets)
   - Circuit breaker pattern for provider outages
   - Automatic failover (Anthropic -> OpenAI -> Google)

4. Caching Layer:
   - Exact-match response cache (hash of prompt -> response)
   - Prompt prefix caching via provider APIs
   - Semantic cache (embed query, find similar past queries)

5. Observability:
   - Real-time cost dashboard
   - Per-customer usage tracking
   - Anomaly detection on spending patterns
   - Alerting pipeline (Slack, PagerDuty)

Capacity math:
- 10K RPM = ~167 requests/second
- At 5 concurrent per worker: need ~34 workers
- At avg 1000 input + 300 output tokens per request:
  - Sonnet: ~$0.0075/request -> $4,500/hour -> $108K/month
  - Haiku:  ~$0.002/request  -> $1,200/hour -> $28.8K/month
  - Mixed (70% Haiku, 30% Sonnet): ~$52K/month
"""
```

**Q4: "How would you implement prompt caching to reduce costs for a RAG application?"**

```python
"""
RAG Prompt Caching Strategy
============================

RAG prompts have a natural caching structure:

[System prompt]        <- Stable (cache this)
[Retrieved documents]  <- Semi-stable per topic (cache when possible)
[Conversation history] <- Changes every turn (hard to cache)
[Current question]     <- Changes every request (never cached)

Optimization approach:

1. Structure the prompt with cache breakpoints:
   system=[
       {"text": system_prompt, "cache_control": {"type": "ephemeral"}},
   ]
   messages=[
       {"role": "user", "content": [
           {"text": docs, "cache_control": {"type": "ephemeral"}},
           {"text": question},  # No cache control
       ]}
   ]

2. Group queries by topic to maximize cache hits:
   - Cluster incoming questions by retrieved document set
   - Process questions about the same documents together
   - This ensures the document prefix is cached across questions

3. Application-level caching for identical queries:
   - Hash the full prompt
   - Check a response cache (Redis) before calling the API
   - TTL based on content freshness requirements

4. Measure cache performance:
   - Track cache_creation_input_tokens vs cache_read_input_tokens
   - Target: >60% cache hit rate for production RAG
   - If hit rate is low, investigate prompt instability
"""
```

**Q5: "What metrics would you track to monitor the cost-effectiveness of an LLM-powered feature?"**

```python
@dataclass
class CostEffectivenessMetrics:
    """The key metrics to track for any LLM-powered feature."""

    # Cost metrics
    cost_per_request: float           # Direct API cost per call
    cost_per_successful_outcome: float  # Cost per task that achieves its goal
    monthly_total_cost: float         # Total spend

    # Efficiency metrics
    cache_hit_rate: float             # Fraction of tokens served from cache
    model_downgrade_rate: float       # Fraction routed to cheaper models
    retry_rate: float                 # Fraction of calls requiring retry
    token_efficiency: float           # Useful output tokens / total tokens

    # Quality metrics
    task_success_rate: float          # Fraction of calls producing good output
    user_satisfaction: float          # User rating or thumbs up/down
    latency_p50_ms: float             # Median latency
    latency_p99_ms: float             # Tail latency

    # Business metrics
    cost_per_user_per_month: float    # Unit economics
    revenue_per_api_dollar: float     # ROI on API spend
    budget_utilization: float         # Fraction of budget consumed

    def summary_report(self) -> str:
        return (
            f"Cost Effectiveness Report\n"
            f"{'='*40}\n"
            f"Cost/request:        ${self.cost_per_request:.4f}\n"
            f"Cost/success:        ${self.cost_per_successful_outcome:.4f}\n"
            f"Monthly total:       ${self.monthly_total_cost:,.2f}\n"
            f"Cache hit rate:      {self.cache_hit_rate:.1%}\n"
            f"Task success:        {self.task_success_rate:.1%}\n"
            f"Latency P50:         {self.latency_p50_ms:.0f}ms\n"
            f"Latency P99:         {self.latency_p99_ms:.0f}ms\n"
            f"Budget utilization:  {self.budget_utilization:.1%}\n"
            f"Revenue/API dollar:  ${self.revenue_per_api_dollar:.2f}\n"
        )
```

### Practice Exercise: Optimization Audit

```python
"""
EXERCISE: Cost Optimization Audit
==================================

You are a solutions engineer at Anthropic. A customer provides you with
the following usage data for their AI-powered customer support system:

Usage Profile:
- 200,000 API calls/month
- All calls use claude-3-opus (most expensive model)
- Average input: 3,000 tokens (includes 2,500-token system prompt)
- Average output: 800 tokens
- No prompt caching enabled
- No batch processing
- 15% of calls are simple FAQ lookups
- 45% are standard support questions
- 30% are complex technical issues
- 10% are escalations requiring human review

Tasks:
1. Calculate their current monthly cost
2. Design a model routing strategy
3. Estimate savings from prompt caching
4. Estimate savings from batch processing eligible requests
5. Calculate the optimized monthly cost
6. Present a phased optimization plan

Use the PRICING_CATALOG and classes from this lesson to build
your analysis. Write a function that takes these parameters
and produces a complete optimization report.
"""


def run_optimization_audit() -> dict:
    """Run the optimization audit exercise."""
    opus_pricing = PRICING_CATALOG["claude-3-opus"]
    sonnet_pricing = PRICING_CATALOG["claude-3-5-sonnet"]
    haiku_pricing = PRICING_CATALOG["claude-3-5-haiku"]

    total_calls = 200_000
    avg_input = 3_000
    avg_output = 800
    system_prompt_tokens = 2_500

    # Current cost (all Opus, no caching)
    current_cost_per_call = opus_pricing.estimate_cost(avg_input, avg_output)
    current_monthly = current_cost_per_call * total_calls

    # Optimized routing
    faq_calls = int(total_calls * 0.15)       # -> Haiku
    standard_calls = int(total_calls * 0.45)  # -> Sonnet
    complex_calls = int(total_calls * 0.30)   # -> Sonnet
    escalation_calls = int(total_calls * 0.10)  # -> Opus (need quality)

    # With prompt caching (system prompt is cacheable)
    # Assume 80% cache hit rate after warmup
    cache_rate = 0.80
    cached_tokens = int(system_prompt_tokens * cache_rate)

    faq_cost = haiku_pricing.estimate_cost(
        avg_input, 200, cached_tokens  # FAQs have shorter output
    ) * faq_calls

    standard_cost = sonnet_pricing.estimate_cost(
        avg_input, avg_output, cached_tokens
    ) * standard_calls

    complex_cost = sonnet_pricing.estimate_cost(
        avg_input, avg_output * 1.5, cached_tokens  # Longer output
    ) * complex_calls

    escalation_cost = opus_pricing.estimate_cost(
        avg_input, avg_output, cached_tokens
    ) * escalation_calls

    optimized_monthly = faq_cost + standard_cost + complex_cost + escalation_cost

    # Batch processing savings (FAQ lookups can be batched)
    # Batch API is 50% off
    batch_eligible = faq_calls * 0.5  # 50% of FAQ calls are non-urgent
    batch_savings = (
        haiku_pricing.estimate_cost(avg_input, 200, cached_tokens)
        * batch_eligible
        * 0.5  # 50% discount
    )
    optimized_monthly -= batch_savings

    return {
        "current_monthly_cost": current_monthly,
        "optimized_monthly_cost": optimized_monthly,
        "monthly_savings": current_monthly - optimized_monthly,
        "savings_percentage": (
            (current_monthly - optimized_monthly) / current_monthly * 100
        ),
        "breakdown": {
            "faq_cost": faq_cost,
            "standard_cost": standard_cost,
            "complex_cost": complex_cost,
            "escalation_cost": escalation_cost,
            "batch_savings": batch_savings,
        },
    }


# Run the audit
audit = run_optimization_audit()
print(f"Current monthly cost:   ${audit['current_monthly_cost']:,.2f}")
print(f"Optimized monthly cost: ${audit['optimized_monthly_cost']:,.2f}")
print(f"Monthly savings:        ${audit['monthly_savings']:,.2f}")
print(f"Savings percentage:     {audit['savings_percentage']:.1f}%")
```

---

## Key Takeaways

1. **Measure before optimizing.** Build cost tracking from day one. You cannot optimize what you cannot measure.

2. **Model routing is the biggest lever.** Switching from Opus to Haiku for simple tasks can reduce costs by 10-20x with negligible quality impact.

3. **Prompt caching pays for itself immediately.** Structure prompts with stable prefixes, and monitor cache hit rates. Target 60%+ hit rate.

4. **Batch when you can, stream when you must.** The Batch API offers 50% savings for any workload that does not need real-time responses.

5. **Budget enforcement prevents surprises.** Per-customer budgets with alerts at 75%, 90%, and 100% utilization are table stakes for enterprise deployments.

6. **Optimize prompts like you optimize payloads.** Every token costs money. Remove filler words, use structured output, and test whether fewer examples maintain quality.

7. **Think in cost-per-successful-outcome, not cost-per-call.** A cheaper model that fails 20% of the time may cost more than a reliable one.

8. **Anomaly detection catches runaway costs.** Simple z-score monitoring on hourly spend can catch bugs and abuse before they become expensive problems.

---

## Further Reading

- [Anthropic API Pricing](https://www.anthropic.com/pricing)
- [Anthropic Prompt Caching Documentation](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Anthropic Batch API Documentation](https://docs.anthropic.com/en/docs/build-with-claude/message-batches)
- [OpenAI Pricing](https://openai.com/pricing)
- [tiktoken: OpenAI Token Counter](https://github.com/openai/tiktoken)
- [Google Gemini Pricing](https://ai.google.dev/pricing)
