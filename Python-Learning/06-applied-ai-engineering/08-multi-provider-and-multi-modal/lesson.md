# Module 08: Multi-Provider & Multi-Modal AI

## Overview

Production AI systems rarely depend on a single provider. Enterprise customers demand failover
guarantees, procurement teams negotiate across vendors, and different models excel at different
tasks. As a solutions engineer or applied AI engineer, you will be expected to design systems
that abstract away provider differences, route requests intelligently, and handle multimodal
inputs -- images, audio, documents -- across heterogeneous backends.

This module covers the full stack of multi-provider and multi-modal engineering: from unified
client abstractions with LiteLLM, to intelligent routing strategies, to vision and audio
processing pipelines. By the end, you will be able to architect resilient, cost-optimized
systems that treat LLM providers as interchangeable commodities while exploiting each
provider's unique strengths.

---

## 1. The Multi-Provider Landscape

### Why Customers Need Multi-Provider Support

In enterprise sales calls and technical evaluations, multi-provider support comes up
constantly. The reasons are both technical and organizational:

**Vendor Lock-In Avoidance**
- Legal and procurement teams want negotiating leverage
- Engineering teams want to avoid rewriting code if a provider changes pricing or terms
- CTO-level concern: "What happens if Provider X has a major outage?"

**Regulatory and Compliance Requirements**
- Data residency laws (GDPR, CCPA) may require routing to region-specific providers
- Some industries (healthcare, finance) mandate that data never leaves certain jurisdictions
- Government contracts may restrict which providers can be used

**Cost Optimization**
- Simple summarization does not need the most expensive model
- Token-heavy batch jobs benefit from cheaper providers
- Different providers offer different pricing tiers for the same quality tier

**Quality and Capability Gaps**
- No single provider leads on every task
- Provider A may excel at code generation while Provider B handles multilingual tasks better
- New models launch constantly -- you need to swap in improvements quickly

```python
# The problem: tightly coupled provider code
# Changing providers means rewriting everything

# --- Anthropic-specific code ---
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Summarize this contract."}]
)
result = response.content[0].text

# --- OpenAI-specific code (completely different API) ---
import openai

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Summarize this contract."}]
)
result = response.choices[0].message.content

# Two different APIs, two different response structures,
# two different error types, two different auth mechanisms.
# This does not scale.
```

> **Swift Developer Note:** This is analogous to the problem iOS developers face when
> supporting multiple backend services. You might use `URLSession` for one API and
> Alamofire for another, but ideally you define a protocol like `NetworkService` and
> swap implementations. The same pattern applies here -- we need a unified interface
> over heterogeneous LLM providers.

### The Provider Matrix

Understanding what each provider offers is essential for routing decisions:

| Feature | Anthropic (Claude) | OpenAI (GPT) | Google (Gemini) | Cohere | Mistral |
|---------|-------------------|---------------|-----------------|--------|---------|
| Max context | 200K | 128K | 2M | 128K | 128K |
| Vision | Yes | Yes | Yes | No | Yes |
| Tool use | Yes | Yes | Yes | Yes | Yes |
| Streaming | Yes | Yes | Yes | Yes | Yes |
| Structured output | JSON mode | JSON mode + schema | JSON mode | JSON mode | JSON mode |
| Embeddings | No (via Voyage) | Yes | Yes | Yes | Yes |
| Fine-tuning | No | Yes | Yes | Yes | Yes |
| Batch API | Yes | Yes | Yes | No | Yes |

---

## 2. Building Unified Clients with LiteLLM

### What is LiteLLM?

LiteLLM is a Python library that provides a unified interface to 100+ LLM providers.
It translates your calls into provider-specific API requests and normalizes responses
into a consistent format.

```bash
pip install litellm
```

### Basic Usage

```python
import litellm

# Call Claude
response = litellm.completion(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Hello from Claude!"}]
)
print(response.choices[0].message.content)

# Call OpenAI -- same interface, different model string
response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello from GPT!"}]
)
print(response.choices[0].message.content)

# Call Gemini -- still the same interface
response = litellm.completion(
    model="gemini/gemini-1.5-pro",
    messages=[{"role": "user", "content": "Hello from Gemini!"}]
)
print(response.choices[0].message.content)
```

The key insight: the response format is always OpenAI-compatible. LiteLLM normalizes
every provider's response into the `ChatCompletion` object format.

### Model Naming Conventions

LiteLLM uses prefixes to identify providers:

```python
# Provider prefixes in LiteLLM
MODEL_MAP = {
    # Anthropic -- no prefix needed (auto-detected)
    "claude-sonnet-4-20250514": "Anthropic Claude Sonnet",
    "claude-3-5-haiku-20241022": "Anthropic Claude Haiku",

    # OpenAI -- no prefix needed (auto-detected)
    "gpt-4o": "OpenAI GPT-4o",
    "gpt-4o-mini": "OpenAI GPT-4o Mini",

    # Google -- requires prefix
    "gemini/gemini-1.5-pro": "Google Gemini 1.5 Pro",
    "gemini/gemini-1.5-flash": "Google Gemini 1.5 Flash",

    # Mistral -- requires prefix
    "mistral/mistral-large-latest": "Mistral Large",

    # Cohere -- requires prefix
    "cohere_chat/command-r-plus": "Cohere Command R+",

    # Azure OpenAI -- requires prefix + deployment name
    "azure/my-gpt4-deployment": "Azure-hosted GPT-4",

    # AWS Bedrock -- requires prefix
    "bedrock/anthropic.claude-3-sonnet-20240229-v1:0": "Bedrock Claude",

    # Self-hosted / Ollama
    "ollama/llama3": "Local Llama 3",
}
```

### Configuration and Environment Variables

```python
import os

# LiteLLM reads standard environment variables
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
os.environ["OPENAI_API_KEY"] = "sk-..."
os.environ["GEMINI_API_KEY"] = "..."

# Or pass them explicitly
response = litellm.completion(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Hello"}],
    api_key="sk-ant-explicit-key",
)

# Azure requires additional config
os.environ["AZURE_API_KEY"] = "..."
os.environ["AZURE_API_BASE"] = "https://my-resource.openai.azure.com"
os.environ["AZURE_API_VERSION"] = "2024-02-01"
```

### Streaming with LiteLLM

```python
import litellm

# Streaming works identically across providers
response = litellm.completion(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Write a short story."}],
    stream=True,
)

collected_content = []
for chunk in response:
    delta = chunk.choices[0].delta.content
    if delta:
        collected_content.append(delta)
        print(delta, end="", flush=True)

full_response = "".join(collected_content)
```

### Building a Unified Client Class

While LiteLLM handles the API abstraction, you still need application-level logic:

```python
import litellm
from dataclasses import dataclass, field
from typing import Optional
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a single model."""
    provider: str
    model_id: str
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0
    supports_vision: bool = False
    supports_tools: bool = True
    max_context_tokens: int = 128000


@dataclass
class CompletionResult:
    """Normalized result from any provider."""
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    raw_response: object = field(repr=False, default=None)


class UnifiedLLMClient:
    """Production-ready unified client wrapping LiteLLM."""

    MODELS = {
        "claude-sonnet": ModelConfig(
            provider="anthropic",
            model_id="claude-sonnet-4-20250514",
            cost_per_input_token=3.0 / 1_000_000,
            cost_per_output_token=15.0 / 1_000_000,
            supports_vision=True,
            max_context_tokens=200_000,
        ),
        "claude-haiku": ModelConfig(
            provider="anthropic",
            model_id="claude-3-5-haiku-20241022",
            cost_per_input_token=0.80 / 1_000_000,
            cost_per_output_token=4.0 / 1_000_000,
            supports_vision=True,
            max_context_tokens=200_000,
        ),
        "gpt-4o": ModelConfig(
            provider="openai",
            model_id="gpt-4o",
            cost_per_input_token=2.50 / 1_000_000,
            cost_per_output_token=10.0 / 1_000_000,
            supports_vision=True,
        ),
        "gpt-4o-mini": ModelConfig(
            provider="openai",
            model_id="gpt-4o-mini",
            cost_per_input_token=0.15 / 1_000_000,
            cost_per_output_token=0.60 / 1_000_000,
            supports_vision=True,
        ),
        "gemini-pro": ModelConfig(
            provider="google",
            model_id="gemini/gemini-1.5-pro",
            cost_per_input_token=1.25 / 1_000_000,
            cost_per_output_token=5.0 / 1_000_000,
            supports_vision=True,
            max_context_tokens=2_000_000,
        ),
    }

    def __init__(self, default_model: str = "claude-sonnet"):
        self.default_model = default_model
        self._request_log: list[dict] = []

    def complete(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> CompletionResult:
        """Send a completion request to any provider."""
        model_key = model or self.default_model
        config = self.MODELS[model_key]

        start = time.perf_counter()

        response = litellm.completion(
            model=config.model_id,
            messages=messages,
            max_tokens=max_tokens or config.max_tokens,
            temperature=temperature or config.temperature,
            **kwargs,
        )

        latency_ms = (time.perf_counter() - start) * 1000

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = (
            input_tokens * config.cost_per_input_token
            + output_tokens * config.cost_per_output_token
        )

        result = CompletionResult(
            content=response.choices[0].message.content,
            model=config.model_id,
            provider=config.provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost_usd=cost,
            raw_response=response,
        )

        self._request_log.append({
            "model": model_key,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms,
            "cost_usd": cost,
            "timestamp": time.time(),
        })

        logger.info(
            f"Completion: model={model_key} tokens={input_tokens}+{output_tokens} "
            f"latency={latency_ms:.0f}ms cost=${cost:.6f}"
        )

        return result

    def get_total_cost(self) -> float:
        """Return total cost across all requests in this session."""
        return sum(r["cost_usd"] for r in self._request_log)

    def get_request_stats(self) -> dict:
        """Return aggregate statistics for this session."""
        if not self._request_log:
            return {"total_requests": 0}

        return {
            "total_requests": len(self._request_log),
            "total_cost_usd": self.get_total_cost(),
            "avg_latency_ms": (
                sum(r["latency_ms"] for r in self._request_log)
                / len(self._request_log)
            ),
            "total_input_tokens": sum(r["input_tokens"] for r in self._request_log),
            "total_output_tokens": sum(r["output_tokens"] for r in self._request_log),
            "models_used": list(set(r["model"] for r in self._request_log)),
        }


# Usage
client = UnifiedLLMClient(default_model="claude-sonnet")

# Same interface regardless of provider
result = client.complete(
    messages=[{"role": "user", "content": "Explain quantum computing briefly."}],
)
print(f"Response: {result.content[:100]}...")
print(f"Cost: ${result.cost_usd:.6f}")
print(f"Latency: {result.latency_ms:.0f}ms")

# Switch providers with one argument
result_gpt = client.complete(
    messages=[{"role": "user", "content": "Explain quantum computing briefly."}],
    model="gpt-4o",
)
```

> **Swift Developer Note:** The `UnifiedLLMClient` follows the same pattern as defining a
> `protocol LLMProvider` in Swift with concrete implementations for each backend. The
> difference is that LiteLLM handles the protocol conformance dynamically at runtime,
> while in Swift you would define explicit structs conforming to your protocol. Think of
> `ModelConfig` as analogous to a Swift `struct` with `Codable` conformance for
> configuration.

---

## 3. Model Routing Strategies

### Why Routing Matters

Not every request deserves the most expensive model. A production system should
intelligently route requests based on complexity, cost constraints, latency requirements,
and provider availability.

### Cost-Based Routing

```python
from enum import Enum
from typing import Optional


class TaskComplexity(Enum):
    TRIVIAL = "trivial"       # Classification, extraction, simple Q&A
    STANDARD = "standard"     # Summarization, translation, moderate reasoning
    COMPLEX = "complex"       # Multi-step reasoning, code generation, analysis
    CRITICAL = "critical"     # High-stakes decisions, legal/medical content


class CostBasedRouter:
    """Route requests to the cheapest model that meets quality requirements."""

    # Ordered by cost (cheapest first)
    TIER_MAP = {
        TaskComplexity.TRIVIAL: ["gpt-4o-mini", "claude-haiku"],
        TaskComplexity.STANDARD: ["claude-haiku", "gpt-4o-mini", "gemini-pro"],
        TaskComplexity.COMPLEX: ["claude-sonnet", "gpt-4o", "gemini-pro"],
        TaskComplexity.CRITICAL: ["claude-sonnet", "gpt-4o"],
    }

    def __init__(self, client: UnifiedLLMClient):
        self.client = client

    def classify_complexity(self, messages: list[dict]) -> TaskComplexity:
        """Heuristic complexity classification."""
        user_content = " ".join(
            m["content"] for m in messages
            if m["role"] == "user" and isinstance(m["content"], str)
        )

        word_count = len(user_content.split())

        # Simple heuristics -- in production, use a classifier model
        if word_count < 20 and any(
            kw in user_content.lower()
            for kw in ["classify", "extract", "yes or no", "true or false"]
        ):
            return TaskComplexity.TRIVIAL

        if any(
            kw in user_content.lower()
            for kw in ["analyze", "compare", "debug", "write code", "implement"]
        ):
            return TaskComplexity.COMPLEX

        if any(
            kw in user_content.lower()
            for kw in ["legal", "medical", "compliance", "audit", "contract"]
        ):
            return TaskComplexity.CRITICAL

        return TaskComplexity.STANDARD

    def route(
        self,
        messages: list[dict],
        complexity: Optional[TaskComplexity] = None,
        max_cost_usd: Optional[float] = None,
    ) -> CompletionResult:
        """Route to the best model based on complexity and cost constraints."""
        if complexity is None:
            complexity = self.classify_complexity(messages)

        candidates = self.TIER_MAP[complexity]

        if max_cost_usd is not None:
            # Filter to models within budget (estimate based on input size)
            candidates = [
                m for m in candidates
                if self._estimate_cost(m, messages) <= max_cost_usd
            ]

        if not candidates:
            raise ValueError(
                f"No models available within budget ${max_cost_usd} "
                f"for complexity {complexity.value}"
            )

        # Try each candidate, falling back on failure
        last_error = None
        for model_key in candidates:
            try:
                return self.client.complete(messages=messages, model=model_key)
            except Exception as e:
                last_error = e
                logger.warning(f"Model {model_key} failed: {e}")
                continue

        raise RuntimeError(f"All models failed. Last error: {last_error}")

    def _estimate_cost(self, model_key: str, messages: list[dict]) -> float:
        """Rough cost estimate based on input length."""
        config = self.client.MODELS[model_key]
        # Rough estimate: 1 token ~= 4 characters
        total_chars = sum(
            len(m["content"]) for m in messages
            if isinstance(m["content"], str)
        )
        estimated_input_tokens = total_chars / 4
        estimated_output_tokens = 500  # Assume moderate response
        return (
            estimated_input_tokens * config.cost_per_input_token
            + estimated_output_tokens * config.cost_per_output_token
        )


# Usage
router = CostBasedRouter(client)

# Automatically routes to cheapest appropriate model
result = router.route(
    messages=[{"role": "user", "content": "Classify this sentiment: 'I love this!'"}]
)
print(f"Routed to: {result.model} (cost: ${result.cost_usd:.6f})")

# Force complex routing
result = router.route(
    messages=[{"role": "user", "content": "Analyze this codebase for security issues."}],
    complexity=TaskComplexity.COMPLEX,
)
```

### Latency-Based Routing

```python
import asyncio
import time
from collections import defaultdict


class LatencyTracker:
    """Track and predict model latency using exponential moving average."""

    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha  # EMA smoothing factor
        self._ema: dict[str, float] = {}
        self._samples: dict[str, list[float]] = defaultdict(list)

    def record(self, model: str, latency_ms: float) -> None:
        """Record a latency observation."""
        self._samples[model].append(latency_ms)
        if model not in self._ema:
            self._ema[model] = latency_ms
        else:
            self._ema[model] = (
                self.alpha * latency_ms + (1 - self.alpha) * self._ema[model]
            )

    def predict(self, model: str) -> float:
        """Predict expected latency for a model."""
        return self._ema.get(model, float("inf"))

    def get_p99(self, model: str) -> float:
        """Get p99 latency for a model."""
        samples = self._samples.get(model, [])
        if not samples:
            return float("inf")
        sorted_samples = sorted(samples)
        idx = int(len(sorted_samples) * 0.99)
        return sorted_samples[min(idx, len(sorted_samples) - 1)]


class LatencyBasedRouter:
    """Route to the fastest available model."""

    def __init__(
        self,
        client: UnifiedLLMClient,
        models: list[str],
        max_latency_ms: float = 5000,
    ):
        self.client = client
        self.models = models
        self.max_latency_ms = max_latency_ms
        self.tracker = LatencyTracker()

    def route(self, messages: list[dict]) -> CompletionResult:
        """Route to the model with lowest predicted latency."""
        # Sort models by predicted latency
        ranked = sorted(self.models, key=lambda m: self.tracker.predict(m))

        last_error = None
        for model_key in ranked:
            predicted = self.tracker.predict(model_key)
            if predicted > self.max_latency_ms and last_error is None:
                logger.warning(
                    f"Model {model_key} predicted latency {predicted:.0f}ms "
                    f"exceeds threshold {self.max_latency_ms}ms"
                )

            try:
                result = self.client.complete(messages=messages, model=model_key)
                self.tracker.record(model_key, result.latency_ms)
                return result
            except Exception as e:
                # Record a penalty latency for failed requests
                self.tracker.record(model_key, self.max_latency_ms * 2)
                last_error = e
                continue

        raise RuntimeError(f"All models failed. Last error: {last_error}")


# Usage
latency_router = LatencyBasedRouter(
    client=client,
    models=["claude-haiku", "gpt-4o-mini", "gemini-pro"],
    max_latency_ms=3000,
)

result = latency_router.route(
    messages=[{"role": "user", "content": "Quick question: what is 2+2?"}]
)
print(f"Fastest route: {result.model} ({result.latency_ms:.0f}ms)")
```

### Geographic Routing

```python
from dataclasses import dataclass


@dataclass
class GeoConfig:
    region: str
    allowed_providers: list[str]
    preferred_provider: str
    data_residency: str  # Where data must stay


class GeoRouter:
    """Route based on user geography and data residency requirements."""

    GEO_CONFIGS = {
        "eu": GeoConfig(
            region="eu",
            allowed_providers=["anthropic", "google"],
            preferred_provider="anthropic",
            data_residency="EU",
        ),
        "us": GeoConfig(
            region="us",
            allowed_providers=["anthropic", "openai", "google"],
            preferred_provider="openai",
            data_residency="US",
        ),
        "apac": GeoConfig(
            region="apac",
            allowed_providers=["google", "anthropic"],
            preferred_provider="google",
            data_residency="APAC",
        ),
    }

    # Map providers to available models
    PROVIDER_MODELS = {
        "anthropic": ["claude-sonnet", "claude-haiku"],
        "openai": ["gpt-4o", "gpt-4o-mini"],
        "google": ["gemini-pro"],
    }

    def __init__(self, client: UnifiedLLMClient):
        self.client = client

    def route(
        self,
        messages: list[dict],
        user_region: str,
        quality_tier: str = "standard",
    ) -> CompletionResult:
        """Route based on geographic constraints."""
        geo = self.GEO_CONFIGS.get(user_region)
        if geo is None:
            raise ValueError(f"Unknown region: {user_region}")

        # Build candidate list respecting geo constraints
        candidates = []
        # Preferred provider first
        candidates.extend(self.PROVIDER_MODELS.get(geo.preferred_provider, []))
        # Then other allowed providers
        for provider in geo.allowed_providers:
            if provider != geo.preferred_provider:
                candidates.extend(self.PROVIDER_MODELS.get(provider, []))

        logger.info(
            f"Geo routing: region={user_region} "
            f"residency={geo.data_residency} "
            f"candidates={candidates}"
        )

        last_error = None
        for model_key in candidates:
            try:
                return self.client.complete(messages=messages, model=model_key)
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"No available models for region {user_region}: {last_error}")
```

### Composite Router with Fallback Chains

```python
from abc import ABC, abstractmethod


class Router(ABC):
    """Base router interface."""

    @abstractmethod
    def route(self, messages: list[dict], **kwargs) -> CompletionResult:
        ...


class FallbackChainRouter(Router):
    """Try a primary model, then fall back through alternatives."""

    def __init__(
        self,
        client: UnifiedLLMClient,
        primary: str,
        fallbacks: list[str],
        max_retries: int = 1,
    ):
        self.client = client
        self.chain = [primary] + fallbacks
        self.max_retries = max_retries

    def route(self, messages: list[dict], **kwargs) -> CompletionResult:
        errors = []
        for model_key in self.chain:
            for attempt in range(self.max_retries + 1):
                try:
                    result = self.client.complete(
                        messages=messages, model=model_key, **kwargs
                    )
                    if model_key != self.chain[0]:
                        logger.warning(
                            f"Used fallback model {model_key} "
                            f"(primary: {self.chain[0]})"
                        )
                    return result
                except Exception as e:
                    errors.append((model_key, attempt, str(e)))
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {model_key}: {e}"
                    )
                    if attempt < self.max_retries:
                        time.sleep(2 ** attempt)  # Exponential backoff

        error_summary = "\n".join(
            f"  {m} (attempt {a+1}): {e}" for m, a, e in errors
        )
        raise RuntimeError(f"All models in fallback chain failed:\n{error_summary}")


# Usage: Claude primary, GPT fallback, Gemini last resort
router = FallbackChainRouter(
    client=client,
    primary="claude-sonnet",
    fallbacks=["gpt-4o", "gemini-pro"],
    max_retries=2,
)

result = router.route(
    messages=[{"role": "user", "content": "Analyze this data set."}]
)
```

> **Swift Developer Note:** The `Router` ABC (Abstract Base Class) is equivalent to a Swift
> `protocol`. The `FallbackChainRouter` pattern mirrors how iOS apps handle network failures:
> try the primary endpoint, then fall back to a CDN, then to a cached response. The key
> difference is that in Python, ABC enforcement is a runtime check, while Swift protocols
> are enforced at compile time.

---

## 4. Vision + Text (Multimodal)

### Sending Images to LLMs

Vision-capable models can process images alongside text. This is critical for document
understanding, UI analysis, accessibility, and content moderation.

```python
import base64
from pathlib import Path


def encode_image(image_path: str) -> str:
    """Read an image file and return base64-encoded string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_media_type(image_path: str) -> str:
    """Determine media type from file extension."""
    suffix = Path(image_path).suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return media_types.get(suffix, "image/jpeg")
```

### Vision API Differences Across Providers

Each provider has a slightly different format for image inputs. LiteLLM normalizes this,
but understanding the native formats is important for debugging:

```python
# --- Native Claude Vision API ---
import anthropic

claude_client = anthropic.Anthropic()

image_data = encode_image("screenshot.png")

response = claude_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data,
                },
            },
            {
                "type": "text",
                "text": "Describe what you see in this image.",
            },
        ],
    }],
)


# --- Native OpenAI Vision API ---
import openai

openai_client = openai.OpenAI()

response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_data}",
                    # OpenAI supports detail level
                    "detail": "high",  # "low", "high", or "auto"
                },
            },
            {
                "type": "text",
                "text": "Describe what you see in this image.",
            },
        ],
    }],
)


# --- Unified via LiteLLM ---
# LiteLLM normalizes to OpenAI format for all providers
import litellm

response = litellm.completion(
    model="claude-sonnet-4-20250514",  # Works with any vision model
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_data}",
                },
            },
            {
                "type": "text",
                "text": "Describe what you see in this image.",
            },
        ],
    }],
)
```

### Image Preprocessing for Optimal Results

```python
from PIL import Image
import io
import base64


class ImagePreprocessor:
    """Prepare images for LLM vision APIs."""

    # Most providers have size and token cost considerations
    MAX_DIMENSION = 2048
    MAX_FILE_SIZE_MB = 20
    QUALITY_FOR_JPEG = 85

    @staticmethod
    def resize_if_needed(img: Image.Image) -> Image.Image:
        """Resize image if it exceeds maximum dimensions."""
        width, height = img.size
        if width <= ImagePreprocessor.MAX_DIMENSION and \
           height <= ImagePreprocessor.MAX_DIMENSION:
            return img

        ratio = min(
            ImagePreprocessor.MAX_DIMENSION / width,
            ImagePreprocessor.MAX_DIMENSION / height,
        )
        new_size = (int(width * ratio), int(height * ratio))
        return img.resize(new_size, Image.Resampling.LANCZOS)

    @staticmethod
    def to_base64(
        img: Image.Image,
        format: str = "PNG",
    ) -> tuple[str, str]:
        """Convert PIL Image to base64 string. Returns (data, media_type)."""
        buffer = io.BytesIO()

        if format.upper() == "JPEG":
            # Convert RGBA to RGB for JPEG
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(buffer, format="JPEG", quality=ImagePreprocessor.QUALITY_FOR_JPEG)
            media_type = "image/jpeg"
        else:
            img.save(buffer, format="PNG")
            media_type = "image/png"

        data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return data, media_type

    @classmethod
    def prepare(cls, image_path: str) -> tuple[str, str]:
        """Full preprocessing pipeline: load, resize, encode."""
        img = Image.open(image_path)
        img = cls.resize_if_needed(img)

        # Use JPEG for photos (smaller), PNG for screenshots/diagrams (sharper)
        if img.mode == "RGBA" or Path(image_path).suffix.lower() == ".png":
            return cls.to_base64(img, "PNG")
        else:
            return cls.to_base64(img, "JPEG")


# Usage
image_data, media_type = ImagePreprocessor.prepare("document.png")

response = litellm.completion(
    model="claude-sonnet-4-20250514",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{media_type};base64,{image_data}"},
            },
            {"type": "text", "text": "Extract all text from this document."},
        ],
    }],
)
```

### Document Understanding Pipeline

```python
from dataclasses import dataclass


@dataclass
class DocumentAnalysis:
    """Result of analyzing a document image."""
    extracted_text: str
    document_type: str
    key_fields: dict[str, str]
    confidence: str  # "high", "medium", "low"
    summary: str


class DocumentAnalyzer:
    """Analyze documents using vision models."""

    ANALYSIS_PROMPT = """Analyze this document image. Return a JSON object with:
{
    "extracted_text": "full text content extracted from the document",
    "document_type": "invoice|contract|receipt|letter|form|other",
    "key_fields": {
        "field_name": "field_value"
    },
    "confidence": "high|medium|low",
    "summary": "one-sentence summary of the document"
}

Extract ALL visible text. Identify the document type and key structured fields
(dates, amounts, names, addresses, reference numbers, etc.)."""

    def __init__(self, client: UnifiedLLMClient):
        self.client = client

    def analyze(
        self,
        image_path: str,
        model: str = "claude-sonnet",
    ) -> DocumentAnalysis:
        """Analyze a document image."""
        image_data, media_type = ImagePreprocessor.prepare(image_path)

        result = self.client.complete(
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_data}",
                        },
                    },
                    {"type": "text", "text": self.ANALYSIS_PROMPT},
                ],
            }],
            model=model,
        )

        import json
        # Parse the JSON response (in production, use structured output)
        parsed = json.loads(result.content)

        return DocumentAnalysis(
            extracted_text=parsed["extracted_text"],
            document_type=parsed["document_type"],
            key_fields=parsed["key_fields"],
            confidence=parsed["confidence"],
            summary=parsed["summary"],
        )


    def compare_documents(
        self,
        image_paths: list[str],
        comparison_prompt: str = "Compare these documents and identify differences.",
    ) -> str:
        """Compare multiple document images."""
        content = []
        for path in image_paths:
            image_data, media_type = ImagePreprocessor.prepare(path)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{media_type};base64,{image_data}"},
            })
        content.append({"type": "text", "text": comparison_prompt})

        result = self.client.complete(
            messages=[{"role": "user", "content": content}],
            model="claude-sonnet",  # Use a strong vision model for comparison
        )
        return result.content


# Usage
analyzer = DocumentAnalyzer(client)
analysis = analyzer.analyze("invoice.png")
print(f"Document type: {analysis.document_type}")
print(f"Key fields: {analysis.key_fields}")
print(f"Summary: {analysis.summary}")
```

> **Swift Developer Note:** In iOS, you might use `VNRecognizeTextRequest` (Vision
> framework) for on-device OCR or `VNClassifyImageRequest` for image classification.
> The LLM vision approach is more flexible -- it can understand context, layout, and
> relationships between elements -- but it requires a network call and costs money per
> request. In production, you often combine both: fast on-device Vision framework
> for initial filtering, then LLM vision for deep understanding.

---

## 5. Audio Processing

### Speech-to-Text with Whisper

OpenAI's Whisper API (and its open-source model) is the most common speech-to-text
integration in LLM applications:

```python
import openai


def transcribe_audio(
    audio_path: str,
    language: str | None = None,
    prompt: str | None = None,
) -> dict:
    """Transcribe audio using OpenAI's Whisper API."""
    client = openai.OpenAI()

    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,      # ISO 639-1 code, e.g., "en", "es"
            prompt=prompt,          # Optional context to guide transcription
            response_format="verbose_json",  # Get timestamps and segments
            timestamp_granularities=["segment", "word"],
        )

    return {
        "text": transcript.text,
        "language": transcript.language,
        "duration": transcript.duration,
        "segments": [
            {
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
            }
            for seg in (transcript.segments or [])
        ],
    }


# Usage
result = transcribe_audio("meeting_recording.mp3")
print(f"Transcription: {result['text'][:200]}...")
print(f"Duration: {result['duration']:.1f} seconds")
print(f"Segments: {len(result['segments'])}")
```

### Text-to-Speech

```python
from pathlib import Path


def text_to_speech(
    text: str,
    output_path: str = "output.mp3",
    voice: str = "alloy",
    model: str = "tts-1",
    speed: float = 1.0,
) -> str:
    """Convert text to speech using OpenAI's TTS API."""
    client = openai.OpenAI()

    # Available voices: alloy, echo, fable, onyx, nova, shimmer
    # Models: tts-1 (faster), tts-1-hd (higher quality)
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        speed=speed,  # 0.25 to 4.0
    )

    response.stream_to_file(output_path)
    return output_path


# Usage
audio_file = text_to_speech(
    text="Hello! This is a demonstration of text-to-speech integration.",
    voice="nova",
    model="tts-1-hd",
)
print(f"Audio saved to: {audio_file}")
```

### Audio Analysis Pipeline

Combine speech-to-text with LLM analysis for powerful audio understanding:

```python
@dataclass
class AudioAnalysis:
    """Result of analyzing an audio file."""
    transcript: str
    summary: str
    key_points: list[str]
    sentiment: str
    action_items: list[str]
    duration_seconds: float


class AudioAnalyzer:
    """Full pipeline: transcribe audio, then analyze with LLM."""

    ANALYSIS_PROMPT = """Analyze the following transcript from an audio recording.

Transcript:
{transcript}

Provide a JSON response with:
{{
    "summary": "2-3 sentence summary",
    "key_points": ["point 1", "point 2", ...],
    "sentiment": "positive|negative|neutral|mixed",
    "action_items": ["action 1", "action 2", ...]
}}"""

    def __init__(self, llm_client: UnifiedLLMClient):
        self.llm_client = llm_client
        self.openai_client = openai.OpenAI()

    def transcribe(self, audio_path: str) -> dict:
        """Transcribe audio to text."""
        with open(audio_path, "rb") as f:
            transcript = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
            )

        return {
            "text": transcript.text,
            "duration": transcript.duration,
            "segments": transcript.segments,
        }

    def analyze(self, audio_path: str, model: str = "claude-haiku") -> AudioAnalysis:
        """Full pipeline: transcribe then analyze."""
        # Step 1: Transcribe
        transcription = self.transcribe(audio_path)

        # Step 2: Analyze with LLM
        prompt = self.ANALYSIS_PROMPT.format(transcript=transcription["text"])
        result = self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model=model,
        )

        import json
        analysis = json.loads(result.content)

        return AudioAnalysis(
            transcript=transcription["text"],
            summary=analysis["summary"],
            key_points=analysis["key_points"],
            sentiment=analysis["sentiment"],
            action_items=analysis["action_items"],
            duration_seconds=transcription["duration"],
        )


# Usage
audio_analyzer = AudioAnalyzer(llm_client=client)
analysis = audio_analyzer.analyze("standup_meeting.mp3")
print(f"Summary: {analysis.summary}")
print(f"Action items: {analysis.action_items}")
```

### Chunked Transcription for Long Audio

The Whisper API has a 25 MB file size limit. For longer recordings, you need to split:

```python
from pydub import AudioSegment
import tempfile
import os


class ChunkedTranscriber:
    """Handle audio files that exceed API size limits."""

    MAX_CHUNK_SIZE_MB = 24  # Leave margin below 25 MB limit
    CHUNK_DURATION_MS = 10 * 60 * 1000  # 10-minute chunks
    OVERLAP_MS = 5000  # 5-second overlap to avoid cutting mid-sentence

    def __init__(self):
        self.openai_client = openai.OpenAI()

    def transcribe_long_audio(self, audio_path: str) -> str:
        """Transcribe audio of any length by chunking."""
        audio = AudioSegment.from_file(audio_path)
        duration_ms = len(audio)

        if duration_ms <= self.CHUNK_DURATION_MS:
            # Short enough for a single call
            return transcribe_audio(audio_path)["text"]

        # Split into overlapping chunks
        chunks = []
        start = 0
        while start < duration_ms:
            end = min(start + self.CHUNK_DURATION_MS, duration_ms)
            chunk = audio[start:end]
            chunks.append(chunk)
            start = end - self.OVERLAP_MS  # Overlap for continuity

        # Transcribe each chunk
        transcripts = []
        for i, chunk in enumerate(chunks):
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                chunk.export(tmp.name, format="mp3")
                result = transcribe_audio(tmp.name)
                transcripts.append(result["text"])
                os.unlink(tmp.name)

            logger.info(f"Transcribed chunk {i + 1}/{len(chunks)}")

        # Merge transcripts (simple concatenation; production systems
        # would deduplicate overlap regions)
        return " ".join(transcripts)
```

> **Swift Developer Note:** iOS has excellent built-in speech recognition via
> `SFSpeechRecognizer` that works on-device. The Whisper API approach is different --
> it runs server-side and supports 99 languages with higher accuracy for many of them.
> In a production iOS app, you might use `SFSpeechRecognizer` for real-time UI feedback
> and then send the recording to Whisper for the authoritative transcript.

---

## 6. Failover and Redundancy

### Automatic Failover Between Providers

Production systems must handle provider outages gracefully. This goes beyond simple
retry logic -- it requires health tracking, circuit breaking, and graceful degradation.

```python
import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict


class ProviderHealth(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class HealthState:
    """Track health of a single provider/model."""
    status: ProviderHealth = ProviderHealth.HEALTHY
    consecutive_failures: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    total_requests: int = 0
    total_failures: int = 0
    circuit_open_until: float = 0.0
    avg_latency_ms: float = 0.0


class CircuitBreaker:
    """Circuit breaker pattern for LLM providers.

    States:
    - CLOSED (healthy): Requests flow normally
    - OPEN (unhealthy): Requests are rejected immediately
    - HALF-OPEN: Allow one test request to check recovery
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 60.0,
        degraded_threshold: int = 2,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_seconds
        self.degraded_threshold = degraded_threshold
        self._states: dict[str, HealthState] = defaultdict(HealthState)
        self._lock = threading.Lock()

    def can_request(self, model: str) -> bool:
        """Check if requests are allowed for this model."""
        with self._lock:
            state = self._states[model]

            if state.status == ProviderHealth.CIRCUIT_OPEN:
                # Check if recovery timeout has elapsed
                if time.time() >= state.circuit_open_until:
                    state.status = ProviderHealth.DEGRADED  # Half-open
                    return True
                return False

            return True

    def record_success(self, model: str, latency_ms: float) -> None:
        """Record a successful request."""
        with self._lock:
            state = self._states[model]
            state.consecutive_failures = 0
            state.last_success_time = time.time()
            state.total_requests += 1
            state.status = ProviderHealth.HEALTHY
            # Update rolling average
            alpha = 0.2
            state.avg_latency_ms = (
                alpha * latency_ms + (1 - alpha) * state.avg_latency_ms
                if state.avg_latency_ms > 0
                else latency_ms
            )

    def record_failure(self, model: str) -> None:
        """Record a failed request."""
        with self._lock:
            state = self._states[model]
            state.consecutive_failures += 1
            state.last_failure_time = time.time()
            state.total_requests += 1
            state.total_failures += 1

            if state.consecutive_failures >= self.failure_threshold:
                state.status = ProviderHealth.CIRCUIT_OPEN
                state.circuit_open_until = time.time() + self.recovery_timeout
                logger.error(
                    f"Circuit OPEN for {model}: "
                    f"{state.consecutive_failures} consecutive failures"
                )
            elif state.consecutive_failures >= self.degraded_threshold:
                state.status = ProviderHealth.DEGRADED
                logger.warning(f"Model {model} degraded: {state.consecutive_failures} failures")

    def get_health(self, model: str) -> HealthState:
        """Get current health state for a model."""
        return self._states[model]

    def get_all_health(self) -> dict[str, HealthState]:
        """Get health states for all tracked models."""
        return dict(self._states)


class ResilientRouter:
    """Production router with circuit breaker, failover, and health monitoring."""

    def __init__(
        self,
        client: UnifiedLLMClient,
        primary: str,
        fallbacks: list[str],
    ):
        self.client = client
        self.primary = primary
        self.fallbacks = fallbacks
        self.all_models = [primary] + fallbacks
        self.breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout_seconds=60,
        )

    def route(self, messages: list[dict], **kwargs) -> CompletionResult:
        """Route with automatic failover and circuit breaking."""
        # Try models in priority order, skipping those with open circuits
        for model_key in self.all_models:
            if not self.breaker.can_request(model_key):
                logger.info(f"Skipping {model_key}: circuit open")
                continue

            try:
                result = self.client.complete(
                    messages=messages, model=model_key, **kwargs
                )
                self.breaker.record_success(model_key, result.latency_ms)

                if model_key != self.primary:
                    logger.warning(
                        f"Serving from fallback {model_key} "
                        f"(primary {self.primary} unavailable)"
                    )

                return result

            except Exception as e:
                self.breaker.record_failure(model_key)
                logger.error(f"Request to {model_key} failed: {e}")

        # All models failed or circuits open
        raise RuntimeError(
            "All providers unavailable. Health states:\n"
            + "\n".join(
                f"  {m}: {self.breaker.get_health(m).status.value}"
                for m in self.all_models
            )
        )

    def health_report(self) -> dict:
        """Generate a health report for monitoring dashboards."""
        report = {}
        for model in self.all_models:
            state = self.breaker.get_health(model)
            report[model] = {
                "status": state.status.value,
                "consecutive_failures": state.consecutive_failures,
                "total_requests": state.total_requests,
                "failure_rate": (
                    state.total_failures / state.total_requests
                    if state.total_requests > 0
                    else 0.0
                ),
                "avg_latency_ms": state.avg_latency_ms,
            }
        return report


# Usage
resilient = ResilientRouter(
    client=client,
    primary="claude-sonnet",
    fallbacks=["gpt-4o", "gemini-pro", "claude-haiku"],
)

# Normal operation -- uses Claude Sonnet
result = resilient.route(
    messages=[{"role": "user", "content": "Analyze this data."}]
)

# Check health
health = resilient.health_report()
for model, status in health.items():
    print(f"  {model}: {status['status']} (failure rate: {status['failure_rate']:.1%})")
```

### Health Check Endpoint

```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

# Global resilient router
resilient_router = ResilientRouter(
    client=UnifiedLLMClient(),
    primary="claude-sonnet",
    fallbacks=["gpt-4o", "gemini-pro"],
)


@app.get("/health")
async def health_check():
    """Health endpoint for load balancers and monitoring."""
    report = resilient_router.health_report()

    # Overall health: healthy if primary or at least one fallback is healthy
    any_healthy = any(
        v["status"] == "healthy" for v in report.values()
    )

    return {
        "status": "healthy" if any_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "providers": report,
    }


@app.get("/health/detailed")
async def detailed_health():
    """Detailed health with latency probe (for internal monitoring)."""
    results = {}

    for model_key in resilient_router.all_models:
        try:
            start = time.perf_counter()
            result = resilient_router.client.complete(
                messages=[{"role": "user", "content": "ping"}],
                model=model_key,
                max_tokens=5,
            )
            latency = (time.perf_counter() - start) * 1000
            results[model_key] = {
                "status": "reachable",
                "latency_ms": round(latency, 1),
            }
        except Exception as e:
            results[model_key] = {
                "status": "unreachable",
                "error": str(e),
            }

    return {"probes": results, "timestamp": datetime.utcnow().isoformat()}
```

> **Swift Developer Note:** The circuit breaker pattern here is the same concept used in
> iOS networking libraries like Alamofire's `RetryPolicy`. The `ProviderHealth` enum maps
> directly to how you might model network reachability states with `NWPathMonitor` in
> Network.framework. The key difference is that server-side circuit breakers must be
> thread-safe (hence the `threading.Lock`), while iOS typically uses the main actor or
> `@MainActor` for state synchronization.

---

## 7. Provider Benchmarking

### Why Benchmark?

Provider performance changes over time. Models get updated, infrastructure scales,
pricing shifts. You need automated benchmarking to make data-driven routing decisions.

### Building a Benchmark Suite

```python
import json
import time
import statistics
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BenchmarkCase:
    """A single benchmark test case."""
    name: str
    category: str  # "reasoning", "coding", "summarization", "extraction"
    messages: list[dict]
    expected_contains: list[str] = field(default_factory=list)
    max_acceptable_latency_ms: float = 10000
    max_acceptable_cost_usd: float = 0.10


@dataclass
class BenchmarkResult:
    """Result from running a benchmark case against a model."""
    case_name: str
    model: str
    provider: str
    latency_ms: float
    cost_usd: float
    input_tokens: int
    output_tokens: int
    passed_quality: bool
    response_preview: str
    error: str | None = None


class ProviderBenchmark:
    """Benchmark suite for comparing LLM providers."""

    STANDARD_CASES = [
        BenchmarkCase(
            name="simple_math",
            category="reasoning",
            messages=[{"role": "user", "content": "What is 15% of 240? Reply with just the number."}],
            expected_contains=["36"],
        ),
        BenchmarkCase(
            name="json_extraction",
            category="extraction",
            messages=[{
                "role": "user",
                "content": (
                    'Extract name and email from: "Contact John Smith at '
                    'john@example.com for details." '
                    'Return as JSON: {"name": "...", "email": "..."}'
                ),
            }],
            expected_contains=["John Smith", "john@example.com"],
        ),
        BenchmarkCase(
            name="code_generation",
            category="coding",
            messages=[{
                "role": "user",
                "content": "Write a Python function that checks if a string is a palindrome. Just the function, no explanation.",
            }],
            expected_contains=["def", "palindrome"],
        ),
        BenchmarkCase(
            name="summarization",
            category="summarization",
            messages=[{
                "role": "user",
                "content": (
                    "Summarize in one sentence: The transformer architecture, "
                    "introduced in 2017 by Vaswani et al., revolutionized natural "
                    "language processing by replacing recurrent neural networks with "
                    "self-attention mechanisms. This allowed for much better "
                    "parallelization during training and captured long-range "
                    "dependencies more effectively than LSTMs."
                ),
            }],
            expected_contains=["transformer"],
        ),
        BenchmarkCase(
            name="instruction_following",
            category="reasoning",
            messages=[{
                "role": "user",
                "content": "List exactly 3 primary colors. Use a numbered list. No other text.",
            }],
            expected_contains=["1.", "2.", "3."],
        ),
    ]

    def __init__(self, client: UnifiedLLMClient):
        self.client = client
        self.results: list[BenchmarkResult] = []

    def run_case(
        self,
        case: BenchmarkCase,
        model: str,
    ) -> BenchmarkResult:
        """Run a single benchmark case against a model."""
        try:
            result = self.client.complete(
                messages=case.messages,
                model=model,
                temperature=0.0,  # Deterministic for benchmarks
            )

            # Quality check: does response contain expected strings?
            content_lower = result.content.lower()
            passed = all(
                exp.lower() in content_lower
                for exp in case.expected_contains
            )

            return BenchmarkResult(
                case_name=case.name,
                model=result.model,
                provider=result.provider,
                latency_ms=result.latency_ms,
                cost_usd=result.cost_usd,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                passed_quality=passed,
                response_preview=result.content[:200],
            )

        except Exception as e:
            return BenchmarkResult(
                case_name=case.name,
                model=model,
                provider="unknown",
                latency_ms=0,
                cost_usd=0,
                input_tokens=0,
                output_tokens=0,
                passed_quality=False,
                response_preview="",
                error=str(e),
            )

    def run_suite(
        self,
        models: list[str],
        cases: list[BenchmarkCase] | None = None,
        runs_per_case: int = 3,
    ) -> list[BenchmarkResult]:
        """Run full benchmark suite across models."""
        cases = cases or self.STANDARD_CASES
        all_results = []

        for model in models:
            print(f"\nBenchmarking {model}...")
            for case in cases:
                case_results = []
                for run in range(runs_per_case):
                    result = self.run_case(case, model)
                    case_results.append(result)
                    all_results.append(result)
                    print(
                        f"  {case.name} (run {run + 1}): "
                        f"{'PASS' if result.passed_quality else 'FAIL'} "
                        f"latency={result.latency_ms:.0f}ms "
                        f"cost=${result.cost_usd:.6f}"
                    )

        self.results = all_results
        return all_results

    def generate_report(self) -> dict:
        """Generate a comparison report from benchmark results."""
        # Group results by model
        by_model: dict[str, list[BenchmarkResult]] = defaultdict(list)
        for r in self.results:
            by_model[r.model].append(r)

        report = {}
        for model, results in by_model.items():
            successful = [r for r in results if r.error is None]
            report[model] = {
                "total_cases": len(results),
                "passed": sum(1 for r in results if r.passed_quality),
                "failed": sum(1 for r in results if not r.passed_quality),
                "errors": sum(1 for r in results if r.error),
                "pass_rate": (
                    sum(1 for r in results if r.passed_quality) / len(results)
                    if results
                    else 0
                ),
                "avg_latency_ms": (
                    statistics.mean(r.latency_ms for r in successful)
                    if successful
                    else 0
                ),
                "p50_latency_ms": (
                    statistics.median(r.latency_ms for r in successful)
                    if successful
                    else 0
                ),
                "p95_latency_ms": (
                    sorted(r.latency_ms for r in successful)[
                        int(len(successful) * 0.95)
                    ]
                    if successful
                    else 0
                ),
                "total_cost_usd": sum(r.cost_usd for r in results),
                "avg_cost_per_request": (
                    statistics.mean(r.cost_usd for r in results)
                    if results
                    else 0
                ),
            }

        return report

    def print_comparison_table(self) -> None:
        """Print a formatted comparison table."""
        report = self.generate_report()

        header = f"{'Model':<35} {'Pass Rate':>10} {'Avg Latency':>12} {'P95 Latency':>12} {'Avg Cost':>10}"
        print("\n" + "=" * len(header))
        print(header)
        print("=" * len(header))

        for model, stats in sorted(report.items()):
            print(
                f"{model:<35} "
                f"{stats['pass_rate']:>9.1%} "
                f"{stats['avg_latency_ms']:>10.0f}ms "
                f"{stats['p95_latency_ms']:>10.0f}ms "
                f"${stats['avg_cost_per_request']:>8.6f}"
            )

        print("=" * len(header))


# Usage
benchmark = ProviderBenchmark(client)
results = benchmark.run_suite(
    models=["claude-sonnet", "claude-haiku", "gpt-4o", "gpt-4o-mini"],
    runs_per_case=3,
)
benchmark.print_comparison_table()
```

### Tracking Performance Over Time

```python
import sqlite3
from datetime import datetime


class BenchmarkTracker:
    """Persist benchmark results to track trends over time."""

    def __init__(self, db_path: str = "benchmarks.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    case_name TEXT NOT NULL,
                    model TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    latency_ms REAL,
                    cost_usd REAL,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    passed_quality BOOLEAN,
                    error TEXT
                )
            """)

    def save_results(self, results: list[BenchmarkResult]) -> None:
        """Save benchmark results to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT INTO benchmark_results
                (timestamp, case_name, model, provider, latency_ms, cost_usd,
                 input_tokens, output_tokens, passed_quality, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        datetime.utcnow().isoformat(),
                        r.case_name,
                        r.model,
                        r.provider,
                        r.latency_ms,
                        r.cost_usd,
                        r.input_tokens,
                        r.output_tokens,
                        r.passed_quality,
                        r.error,
                    )
                    for r in results
                ],
            )

    def get_trend(self, model: str, days: int = 30) -> dict:
        """Get performance trend for a model over time."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT
                    DATE(timestamp) as date,
                    AVG(latency_ms) as avg_latency,
                    AVG(CASE WHEN passed_quality THEN 1.0 ELSE 0.0 END) as pass_rate,
                    AVG(cost_usd) as avg_cost,
                    COUNT(*) as num_requests
                FROM benchmark_results
                WHERE model = ?
                  AND timestamp >= datetime('now', ?)
                GROUP BY DATE(timestamp)
                ORDER BY date
                """,
                (model, f"-{days} days"),
            ).fetchall()

        return {
            "model": model,
            "daily_stats": [
                {
                    "date": row[0],
                    "avg_latency_ms": row[1],
                    "pass_rate": row[2],
                    "avg_cost_usd": row[3],
                    "requests": row[4],
                }
                for row in rows
            ],
        }
```

---

## 8. Handling Provider-Specific Features

### Tool Use Differences

Each provider implements tool use differently. LiteLLM abstracts much of this, but
you need to understand the differences when debugging or when using provider-specific
features.

```python
# --- Unified tool definition (LiteLLM-compatible, OpenAI format) ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g., 'San Francisco, CA'",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                    },
                },
                "required": ["location"],
            },
        },
    }
]

# LiteLLM translates this to each provider's native format
response = litellm.completion(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
)

# Access tool calls (normalized to OpenAI format)
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"Tool: {tool_call.function.name}")
        print(f"Args: {tool_call.function.arguments}")
```

### Provider-Specific Feature Matrix

```python
@dataclass
class ProviderCapabilities:
    """Track what each provider supports."""
    supports_vision: bool = False
    supports_tools: bool = False
    supports_streaming: bool = False
    supports_json_mode: bool = False
    supports_structured_output: bool = False  # Schema-enforced JSON
    supports_system_prompt: bool = True
    supports_logprobs: bool = False
    supports_seed: bool = False  # Reproducibility
    max_images_per_request: int = 0
    max_tools: int = 0
    supports_parallel_tool_calls: bool = False
    supports_forced_tool_use: bool = False


PROVIDER_CAPABILITIES = {
    "anthropic": ProviderCapabilities(
        supports_vision=True,
        supports_tools=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_structured_output=False,
        supports_system_prompt=True,
        supports_logprobs=False,
        supports_seed=False,
        max_images_per_request=20,
        max_tools=128,
        supports_parallel_tool_calls=True,
        supports_forced_tool_use=True,
    ),
    "openai": ProviderCapabilities(
        supports_vision=True,
        supports_tools=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_structured_output=True,
        supports_system_prompt=True,
        supports_logprobs=True,
        supports_seed=True,
        max_images_per_request=10,
        max_tools=128,
        supports_parallel_tool_calls=True,
        supports_forced_tool_use=True,
    ),
    "google": ProviderCapabilities(
        supports_vision=True,
        supports_tools=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_structured_output=True,
        supports_system_prompt=True,
        supports_logprobs=False,
        supports_seed=False,
        max_images_per_request=16,
        max_tools=64,
        supports_parallel_tool_calls=True,
        supports_forced_tool_use=True,
    ),
}


class FeatureAwareRouter:
    """Route based on required features."""

    def __init__(self, client: UnifiedLLMClient):
        self.client = client

    def find_compatible_models(
        self,
        requires_vision: bool = False,
        requires_tools: bool = False,
        requires_structured_output: bool = False,
        requires_logprobs: bool = False,
        min_images: int = 0,
    ) -> list[str]:
        """Find models that support all required features."""
        compatible = []

        for model_key, config in self.client.MODELS.items():
            caps = PROVIDER_CAPABILITIES.get(config.provider)
            if caps is None:
                continue

            if requires_vision and not caps.supports_vision:
                continue
            if requires_tools and not caps.supports_tools:
                continue
            if requires_structured_output and not caps.supports_structured_output:
                continue
            if requires_logprobs and not caps.supports_logprobs:
                continue
            if min_images > 0 and caps.max_images_per_request < min_images:
                continue

            compatible.append(model_key)

        return compatible

    def route_with_features(
        self,
        messages: list[dict],
        requires_vision: bool = False,
        requires_tools: bool = False,
        requires_structured_output: bool = False,
        preferred_models: list[str] | None = None,
    ) -> CompletionResult:
        """Route to a model that supports all required features."""
        compatible = self.find_compatible_models(
            requires_vision=requires_vision,
            requires_tools=requires_tools,
            requires_structured_output=requires_structured_output,
        )

        if not compatible:
            raise ValueError("No models support all required features")

        # Prefer models in the preferred list, then fall back
        if preferred_models:
            ordered = [m for m in preferred_models if m in compatible]
            ordered += [m for m in compatible if m not in ordered]
        else:
            ordered = compatible

        for model_key in ordered:
            try:
                return self.client.complete(messages=messages, model=model_key)
            except Exception as e:
                logger.warning(f"Model {model_key} failed: {e}")
                continue

        raise RuntimeError("All compatible models failed")


# Usage
feature_router = FeatureAwareRouter(client)

# Find models that support both vision and structured output
compatible = feature_router.find_compatible_models(
    requires_vision=True,
    requires_structured_output=True,
)
print(f"Vision + structured output models: {compatible}")
```

### Streaming Differences

```python
import litellm
import asyncio


async def stream_with_provider_awareness(
    model: str,
    messages: list[dict],
) -> str:
    """Stream a response, handling provider-specific streaming behavior."""

    collected = []
    tool_calls_buffer = []

    response = litellm.completion(
        model=model,
        messages=messages,
        stream=True,
    )

    for chunk in response:
        choice = chunk.choices[0]

        # Text content
        if choice.delta.content:
            collected.append(choice.delta.content)
            print(choice.delta.content, end="", flush=True)

        # Tool calls in stream (providers handle this differently)
        if choice.delta.tool_calls:
            for tc in choice.delta.tool_calls:
                # Accumulate tool call deltas
                if tc.index is not None:
                    while len(tool_calls_buffer) <= tc.index:
                        tool_calls_buffer.append({"name": "", "arguments": ""})
                    if tc.function.name:
                        tool_calls_buffer[tc.index]["name"] = tc.function.name
                    if tc.function.arguments:
                        tool_calls_buffer[tc.index]["arguments"] += tc.function.arguments

        # Check for stop reason
        if choice.finish_reason:
            print(f"\n[Finished: {choice.finish_reason}]")

    full_response = "".join(collected)

    if tool_calls_buffer:
        print(f"\nTool calls received: {tool_calls_buffer}")

    return full_response
```

### Handling JSON Mode Across Providers

```python
def request_json_output(
    client: UnifiedLLMClient,
    messages: list[dict],
    model: str = "claude-sonnet",
) -> dict:
    """Request JSON output, handling provider differences.

    - Anthropic: Use system prompt instruction (no native JSON mode for all models)
    - OpenAI: Use response_format={"type": "json_object"}
    - Google: Use response_format={"type": "json_object"}
    """
    config = client.MODELS[model]

    # Build provider-appropriate kwargs
    kwargs = {}
    if config.provider in ("openai", "google"):
        kwargs["response_format"] = {"type": "json_object"}

    # Always include JSON instruction in messages for reliability
    enhanced_messages = messages.copy()
    if enhanced_messages and isinstance(enhanced_messages[-1]["content"], str):
        enhanced_messages[-1] = {
            **enhanced_messages[-1],
            "content": (
                enhanced_messages[-1]["content"]
                + "\n\nRespond with valid JSON only. No other text."
            ),
        }

    result = client.complete(
        messages=enhanced_messages,
        model=model,
        **kwargs,
    )

    return json.loads(result.content)
```

> **Swift Developer Note:** The feature matrix concept maps well to Swift protocol
> conformance. In Swift, you would define protocols like `VisionCapable`, `ToolCapable`,
> and `StreamCapable`, then have each provider struct conform only to the protocols it
> supports. You could use `where` clauses on generic functions to constrain which providers
> are eligible for a given operation. Python's duck typing means you check capabilities
> at runtime via the matrix instead of at compile time via protocols.

---

## 9. Swift Comparison

### Multi-Backend Patterns in iOS

iOS developers frequently work with multiple backend services. The patterns translate
directly to multi-provider LLM architecture:

```swift
// Swift: Protocol-based backend abstraction
protocol LLMProvider {
    var name: String { get }
    var supportsVision: Bool { get }
    func complete(messages: [Message], maxTokens: Int) async throws -> CompletionResult
}

struct AnthropicProvider: LLMProvider {
    let name = "Anthropic"
    let supportsVision = true

    func complete(messages: [Message], maxTokens: Int) async throws -> CompletionResult {
        // URLSession call to Claude API
        var request = URLRequest(url: URL(string: "https://api.anthropic.com/v1/messages")!)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "content-type")
        request.addValue(apiKey, forHTTPHeaderField: "x-api-key")
        // ... build body, send request, parse response
    }
}

struct OpenAIProvider: LLMProvider {
    let name = "OpenAI"
    let supportsVision = true

    func complete(messages: [Message], maxTokens: Int) async throws -> CompletionResult {
        // URLSession call to OpenAI API
        // ... different URL, different headers, different body format
    }
}

// Router using Swift generics
class LLMRouter {
    private let providers: [LLMProvider]
    private var healthStates: [String: ProviderHealth] = [:]

    func route(messages: [Message]) async throws -> CompletionResult {
        for provider in providers {
            guard healthStates[provider.name] != .circuitOpen else { continue }
            do {
                let result = try await provider.complete(messages: messages, maxTokens: 1024)
                healthStates[provider.name] = .healthy
                return result
            } catch {
                recordFailure(for: provider.name)
            }
        }
        throw LLMError.allProvidersFailed
    }
}
```

```python
# Python equivalent using ABC and LiteLLM
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Equivalent to Swift's LLMProvider protocol."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def supports_vision(self) -> bool: ...

    @abstractmethod
    def complete(self, messages: list[dict], max_tokens: int) -> CompletionResult: ...


class AnthropicProvider(LLMProvider):
    name = "Anthropic"
    supports_vision = True

    def complete(self, messages, max_tokens=1024):
        return litellm.completion(
            model="claude-sonnet-4-20250514",
            messages=messages,
            max_tokens=max_tokens,
        )
```

### URLSession Adapter Pattern vs. LiteLLM

| Concept | Swift / iOS | Python / LiteLLM |
|---------|-------------|-------------------|
| HTTP client | `URLSession` | `httpx` / `requests` |
| Provider abstraction | Protocol + concrete types | LiteLLM unified interface |
| Type safety | Compile-time via generics | Runtime via duck typing |
| Error handling | `Result<T, Error>`, `throws` | `try/except`, `Optional` |
| Async model | `async/await` (structured) | `asyncio` or sync |
| Streaming | `URLSession.AsyncBytes` | Generator / `async for` |
| Config | `struct` with `Codable` | `dataclass` or `dict` |
| Dependency injection | Protocol-based init | Constructor injection or `litellm.completion` |

### Core ML vs. Server-Side ML

| Aspect | Core ML (on-device) | Server-side LLM |
|--------|---------------------|-----------------|
| Latency | Sub-millisecond inference | 500ms - 5s network + inference |
| Privacy | Data stays on device | Data sent to provider |
| Model size | Limited by device memory | Unlimited (provider-managed) |
| Quality | Smaller models, lower quality | State-of-the-art models |
| Cost | Free after integration | Per-token pricing |
| Offline | Works offline | Requires network |
| Updates | App update required | Provider updates transparently |

```python
# Hybrid pattern: local triage, server-side processing
class HybridRouter:
    """Mimics the iOS pattern of on-device + server-side processing."""

    def __init__(self, client: UnifiedLLMClient):
        self.client = client

    def route(self, text: str) -> CompletionResult:
        complexity = self._local_complexity_check(text)

        if complexity == "trivial":
            # Use cheapest/fastest model (like Core ML for simple tasks)
            return self.client.complete(
                messages=[{"role": "user", "content": text}],
                model="gpt-4o-mini",
            )
        else:
            # Use powerful model (like sending to server for heavy processing)
            return self.client.complete(
                messages=[{"role": "user", "content": text}],
                model="claude-sonnet",
            )

    def _local_complexity_check(self, text: str) -> str:
        """Simple heuristic (would be Core ML model in iOS)."""
        if len(text.split()) < 20:
            return "trivial"
        return "complex"
```

> **Swift Developer Note:** The hybrid pattern is exactly what you would build in a
> production iOS app: use Core ML or `NaturalLanguage` framework for fast local
> classification, then route to the appropriate server-side model. The key insight
> for interviews is that you understand when on-device processing is appropriate
> (latency-sensitive, privacy-critical, offline) versus when server-side processing
> is needed (quality-critical, complex reasoning, large context windows).

---

## 10. Interview Focus

### Common Multi-Provider Architecture Questions

These questions come up frequently in solutions engineer and applied AI engineer
interviews at companies like OpenAI, Anthropic, Google, and Cohere.

### Question 1: "Design a Multi-Provider LLM Gateway"

**What they are testing:** System design, provider abstraction, resilience patterns.

```
Interviewer: "A customer wants to use multiple LLM providers with automatic
failover and cost optimization. Design the architecture."

Your answer framework:

1. UNIFIED INTERFACE
   - Single API endpoint for all consumers
   - Provider-agnostic request/response format
   - Model aliasing (customer says "fast" or "smart", we map to providers)

2. ROUTING LAYER
   - Cost-based routing for budget-sensitive workloads
   - Quality-based routing using benchmark scores
   - Latency-based routing for real-time applications
   - Feature-based routing (vision, tools, etc.)
   - Geographic routing for compliance

3. RESILIENCE
   - Circuit breaker per provider
   - Automatic failover with fallback chains
   - Health checking (synthetic probes)
   - Rate limit awareness and queuing

4. OBSERVABILITY
   - Per-provider latency, error rate, cost tracking
   - Request tracing across provider switches
   - Alerting on quality degradation

5. COST MANAGEMENT
   - Per-customer budget enforcement
   - Token counting and cost attribution
   - Batch processing for non-urgent requests
```

### Question 2: "How Do You Handle Provider-Specific Features?"

```
Interviewer: "Provider A supports structured output but Provider B doesn't.
How do you handle this in a multi-provider system?"

Key points to cover:

1. CAPABILITY REGISTRY
   - Maintain a feature matrix for all providers
   - Update dynamically as providers add features
   - Expose capability queries to consumers

2. GRACEFUL DEGRADATION
   - If structured output isn't available, fall back to:
     a. Prompt-based JSON instruction + post-parse validation
     b. Retry with schema correction on parse failure
     c. Route to a provider that does support it

3. ABSTRACTION BOUNDARIES
   - Core features: available everywhere (text completion, streaming)
   - Extended features: best-effort with fallbacks (vision, tools)
   - Provider-exclusive features: explicit opt-in with provider lock
```

### Question 3: "Compare Providers for a Specific Use Case"

```python
# Framework for answering "which provider for X?" questions

def recommend_provider(use_case: str) -> dict:
    """Framework for provider recommendations."""

    recommendations = {
        "customer_support_chatbot": {
            "primary": "claude-haiku",
            "reasoning": [
                "High throughput, low latency for interactive chat",
                "Strong instruction following for staying on-topic",
                "Cost-effective for high-volume conversational workloads",
            ],
            "fallback": "gpt-4o-mini",
            "when_to_escalate": "Route to claude-sonnet for complex complaints",
        },
        "code_generation": {
            "primary": "claude-sonnet",
            "reasoning": [
                "Strong code generation benchmarks",
                "200K context for large codebases",
                "Good at following complex coding instructions",
            ],
            "fallback": "gpt-4o",
            "when_to_escalate": "Use for all code tasks; no need to tier",
        },
        "document_analysis": {
            "primary": "gemini-pro",
            "reasoning": [
                "2M token context window for entire documents",
                "Native PDF understanding",
                "Cost-effective for large input contexts",
            ],
            "fallback": "claude-sonnet",
            "when_to_escalate": "Use Claude for nuanced legal/compliance analysis",
        },
        "real_time_classification": {
            "primary": "gpt-4o-mini",
            "reasoning": [
                "Lowest latency for simple tasks",
                "Cheapest per-token cost",
                "JSON mode for structured classification output",
            ],
            "fallback": "claude-haiku",
            "when_to_escalate": "Never -- keep classification at this tier",
        },
    }

    return recommendations.get(use_case, {"error": f"No recommendation for {use_case}"})
```

### Question 4: "How Do You Test Multi-Provider Systems?"

```python
class MultiProviderTestStrategy:
    """Testing framework for multi-provider systems."""

    def test_provider_abstraction(self):
        """Verify all providers produce compatible responses."""
        messages = [{"role": "user", "content": "Say 'hello' and nothing else."}]
        models = ["claude-sonnet", "gpt-4o", "gemini-pro"]

        for model in models:
            result = client.complete(messages=messages, model=model)

            # All results should have the same structure
            assert isinstance(result.content, str)
            assert result.input_tokens > 0
            assert result.output_tokens > 0
            assert result.latency_ms > 0
            assert result.cost_usd >= 0
            assert result.provider in ("anthropic", "openai", "google")

    def test_failover(self):
        """Verify failover works when primary provider is down."""
        router = FallbackChainRouter(
            client=client,
            primary="claude-sonnet",
            fallbacks=["gpt-4o", "gemini-pro"],
        )

        # Simulate primary failure by using a bad model name
        # (In production tests, use mocks or chaos engineering)
        result = router.route(
            messages=[{"role": "user", "content": "Hello"}]
        )
        assert result is not None
        assert isinstance(result.content, str)

    def test_cost_routing(self):
        """Verify cost routing sends simple tasks to cheap models."""
        router = CostBasedRouter(client)

        # Simple classification should route to cheap model
        result = router.route(
            messages=[{"role": "user", "content": "Classify: 'I love it' - positive or negative?"}]
        )
        assert result.provider in ("openai", "anthropic")  # Should use mini/haiku

    def test_circuit_breaker(self):
        """Verify circuit breaker opens after consecutive failures."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=5)

        # Simulate 3 failures
        for _ in range(3):
            breaker.record_failure("test-model")

        assert not breaker.can_request("test-model")  # Circuit should be open
        assert breaker.get_health("test-model").status == ProviderHealth.CIRCUIT_OPEN

        # After timeout, circuit should be half-open
        import time
        time.sleep(6)
        assert breaker.can_request("test-model")  # Should allow test request

    def test_multimodal_routing(self):
        """Verify vision requests only route to vision-capable models."""
        feature_router = FeatureAwareRouter(client)
        compatible = feature_router.find_compatible_models(requires_vision=True)

        # All compatible models should support vision
        for model_key in compatible:
            config = client.MODELS[model_key]
            assert config.supports_vision
```

### Behavioral Interview Angles

When discussing multi-provider architecture in behavioral interviews:

**"Tell me about a time you dealt with a system outage"**
- Describe implementing fallover logic between providers
- Emphasize monitoring and alerting that enabled fast detection
- Discuss the customer communication during degraded operation

**"How do you make technical decisions with incomplete information?"**
- Provider benchmarks give you data, but real workloads differ
- Start with reasonable defaults, instrument everything, iterate
- A/B testing across providers with production traffic

**"How would you help a customer choose between providers?"**
- Run benchmarks on their specific use cases, not generic benchmarks
- Factor in their existing cloud relationships (Azure = easy OpenAI, GCP = easy Gemini)
- Consider total cost of ownership, not just per-token pricing
- Think about support, SLAs, and enterprise agreements

---

## Summary

### Key Takeaways

1. **Provider abstraction is essential** -- LiteLLM (or a custom unified client) decouples
   your application logic from any single provider's API.

2. **Routing is a spectrum** -- from simple fallback chains to sophisticated cost/quality/
   latency-aware routers, the right approach depends on your workload characteristics.

3. **Multimodal is multi-step** -- vision and audio processing require preprocessing
   pipelines, provider-specific format handling, and thoughtful cost management.

4. **Resilience requires active engineering** -- circuit breakers, health checks, and
   fallback chains do not happen by accident. Design them from the start.

5. **Benchmark continuously** -- provider performance changes over time. Automated
   benchmark suites and trend tracking are infrastructure investments that pay off.

6. **Features are not universal** -- maintain a capability matrix and route based on
   what each request actually needs.

### What to Study Next

- **Module 09 (Observability for LLM Apps)**: Deep dive into monitoring the multi-provider
  systems built in this module
- **Module 10 (Customer Scenario Simulation)**: Apply multi-provider patterns to realistic
  customer situations
- **Phase 7 Production Engineering**: Deploy these patterns in production with Docker,
  CI/CD, and cloud infrastructure

### Practice Exercises

1. **Build a Unified Client**: Extend the `UnifiedLLMClient` to support at least 4
   providers. Add async support using `litellm.acompletion()`.

2. **Implement Smart Routing**: Build a router that combines cost, latency, and quality
   signals. Use the benchmark suite to calibrate your routing weights.

3. **Document Analysis Pipeline**: Build an end-to-end pipeline that accepts images of
   invoices, extracts structured data, and routes to the cheapest vision model that meets
   a quality threshold.

4. **Chaos Engineering**: Simulate provider outages by wrapping LiteLLM calls with
   random failure injection. Verify your circuit breaker and failover logic handles
   all edge cases.

5. **Provider Comparison Report**: Run the benchmark suite against 3+ providers and
   generate a written recommendation for a hypothetical customer. Include cost
   projections at 1M, 10M, and 100M tokens/month.
