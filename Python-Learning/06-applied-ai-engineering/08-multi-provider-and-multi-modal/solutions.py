"""
Module 08: Multi-Provider & Multi-Modal AI -- Solutions
========================================================
Complete solutions for all 15 exercises with detailed comments
and test assertions.

Target audience: Swift/iOS developers transitioning to AI/ML engineering roles.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Protocol


# =============================================================================
# SECTION 1: Provider Abstraction & Configuration
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 1: Build a Provider Configuration Model
# ---------------------------------------------------------------------------
class ProviderTier(Enum):
    """Tier classification for model quality/cost tradeoffs."""
    PREMIUM = "premium"
    STANDARD = "standard"
    BUDGET = "budget"


@dataclass
class ProviderConfig:
    """Configuration for a single AI provider.

    This is analogous to a Swift struct encapsulating all provider settings.
    The dataclass decorator auto-generates __init__, __repr__, and __eq__,
    much like Swift's automatic Codable synthesis.
    """
    name: str
    api_base: str
    default_model: str
    tier: ProviderTier
    max_tokens_limit: int
    supports_vision: bool
    supports_streaming: bool
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    rate_limit_rpm: int
    regions: list[str] = field(default_factory=list)
    is_enabled: bool = True

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost in USD for given token counts.

        Cost formula: (input_tokens / 1000 * input_rate) +
                      (output_tokens / 1000 * output_rate)
        """
        input_cost = (input_tokens / 1000) * self.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * self.cost_per_1k_output_tokens
        return input_cost + output_cost

    def supports_feature(self, feature: str) -> bool:
        """Check if this provider supports a given feature string."""
        feature_map = {
            "vision": self.supports_vision,
            "streaming": self.supports_streaming,
        }
        return feature_map.get(feature, False)


def build_provider_configs() -> dict[str, ProviderConfig]:
    """Create a registry of provider configurations.

    Returns configs for OpenAI, Anthropic, and Google with realistic
    pricing and capability information.
    """
    return {
        "openai": ProviderConfig(
            name="openai",
            api_base="https://api.openai.com/v1",
            default_model="gpt-4o",
            tier=ProviderTier.PREMIUM,
            max_tokens_limit=4096,
            supports_vision=True,
            supports_streaming=True,
            # GPT-4o pricing (approximate)
            cost_per_1k_input_tokens=0.005,
            cost_per_1k_output_tokens=0.015,
            rate_limit_rpm=500,
            regions=["us", "eu"],
        ),
        "anthropic": ProviderConfig(
            name="anthropic",
            api_base="https://api.anthropic.com/v1",
            default_model="claude-sonnet-4-20250514",
            tier=ProviderTier.PREMIUM,
            max_tokens_limit=8192,
            supports_vision=True,
            supports_streaming=True,
            # Claude Sonnet pricing (approximate)
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015,
            rate_limit_rpm=1000,
            regions=["us"],
        ),
        "google": ProviderConfig(
            name="google",
            api_base="https://generativelanguage.googleapis.com/v1",
            default_model="gemini-1.5-pro",
            tier=ProviderTier.STANDARD,
            max_tokens_limit=8192,
            supports_vision=True,
            supports_streaming=True,
            # Gemini 1.5 Pro pricing (approximate)
            cost_per_1k_input_tokens=0.00125,
            cost_per_1k_output_tokens=0.005,
            rate_limit_rpm=360,
            regions=["us", "eu", "asia"],
        ),
    }


# ---------------------------------------------------------------------------
# Exercise 2: Implement a Unified Completion Interface (ABC)
# ---------------------------------------------------------------------------
@dataclass
class CompletionRequest:
    """A provider-agnostic completion request.

    Similar to how you might define a protocol in Swift with associated types,
    this dataclass provides a common request format that each provider adapter
    translates into its native format.
    """
    model: str
    messages: list[dict]
    max_tokens: int = 1024
    temperature: float = 0.7
    stop_sequences: list[str] = field(default_factory=list)


@dataclass
class CompletionResponse:
    """A provider-agnostic completion response.

    Normalizes the diverse response formats from different providers
    into a single, consistent structure.
    """
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float


class CompletionProvider(ABC):
    """Abstract base class for AI completion providers.

    In Swift, this would be a protocol with required methods.
    Python's ABC serves the same purpose: any subclass MUST implement
    all @abstractmethod-decorated methods or it cannot be instantiated.
    """

    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Send a completion request and return a response."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name string."""
        pass

    @abstractmethod
    def format_messages(self, messages: list[dict]) -> Any:
        """Convert generic messages to provider-specific format."""
        pass

    def is_available(self) -> bool:
        """Check if the provider is currently available.

        Concrete method -- subclasses can override to add real health checks.
        """
        return True


class MockAnthropicProvider(CompletionProvider):
    """Mock Anthropic provider for testing the abstraction layer.

    Key Anthropic API difference: system messages are extracted from
    the messages array and sent as a top-level 'system' parameter.
    """

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def format_messages(self, messages: list[dict]) -> dict:
        """Anthropic extracts system messages to a separate parameter.

        This is a real difference between providers: OpenAI keeps system
        messages inline, while Anthropic requires them as a separate field.
        """
        system_msg = None
        filtered = []
        for msg in messages:
            if msg.get("role") == "system":
                # Anthropic takes only one system message (the last one wins)
                system_msg = msg.get("content", "")
            else:
                filtered.append(msg)
        return {"system": system_msg, "messages": filtered}

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Return a mock response simulating Anthropic's API."""
        return CompletionResponse(
            content="Mock Anthropic response",
            model=request.model,
            provider="anthropic",
            input_tokens=10,
            output_tokens=5,
            latency_ms=100.0,
            cost_usd=0.001,
        )


class MockOpenAIProvider(CompletionProvider):
    """Mock OpenAI provider for testing the abstraction layer.

    OpenAI accepts messages as-is, including system messages inline.
    """

    @property
    def provider_name(self) -> str:
        return "openai"

    def format_messages(self, messages: list[dict]) -> list[dict]:
        """OpenAI accepts the standard message format directly."""
        return messages

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Return a mock response simulating OpenAI's API."""
        return CompletionResponse(
            content="Mock OpenAI response",
            model=request.model,
            provider="openai",
            input_tokens=10,
            output_tokens=5,
            latency_ms=120.0,
            cost_usd=0.0015,
        )


# ---------------------------------------------------------------------------
# Exercise 3: Build a Model Mapping Registry
# ---------------------------------------------------------------------------
def build_model_registry() -> dict[str, dict[str, str]]:
    """Create a mapping from canonical model names to provider-specific IDs.

    This pattern is essential in multi-provider systems: callers use
    intent-based names like "best" or "fast" rather than knowing every
    provider's model naming conventions.
    """
    return {
        "best": {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
            "google": "gemini-1.5-pro",
        },
        "good": {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-haiku-35-20241022",
            "google": "gemini-1.5-flash",
        },
        "fast": {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-haiku-35-20241022",
            "google": "gemini-1.5-flash",
        },
        "vision": {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
            "google": "gemini-1.5-pro",
        },
    }


def resolve_model(
    registry: dict[str, dict[str, str]],
    canonical_name: str,
    provider: str,
) -> str:
    """Resolve a canonical model name to a provider-specific model ID.

    Raises KeyError if either the canonical name or provider is not found,
    giving callers a clear error rather than a silent fallback.
    """
    if canonical_name not in registry:
        raise KeyError(f"Unknown canonical model name: {canonical_name}")
    provider_map = registry[canonical_name]
    if provider not in provider_map:
        raise KeyError(f"Provider '{provider}' not found for model '{canonical_name}'")
    return provider_map[provider]


# =============================================================================
# SECTION 2: Intelligent Routing
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 4: Implement Cost-Based Model Routing
# ---------------------------------------------------------------------------
def route_by_cost(
    providers: dict[str, ProviderConfig],
    estimated_input_tokens: int,
    estimated_output_tokens: int,
    max_budget_usd: float | None = None,
    require_vision: bool = False,
) -> list[str]:
    """Route to the cheapest provider(s) that meet requirements.

    This is a common pattern in production AI systems: route simple
    queries to cheaper models and reserve expensive ones for complex tasks.
    """
    candidates = []

    for name, config in providers.items():
        # Filter: must be enabled
        if not config.is_enabled:
            continue

        # Filter: vision requirement
        if require_vision and not config.supports_vision:
            continue

        # Calculate estimated cost
        cost = config.estimate_cost(estimated_input_tokens, estimated_output_tokens)

        # Filter: budget constraint
        if max_budget_usd is not None and cost > max_budget_usd:
            continue

        candidates.append((name, cost))

    # Sort by cost ascending
    candidates.sort(key=lambda x: x[1])

    return [name for name, _ in candidates]


# ---------------------------------------------------------------------------
# Exercise 5: Implement Quality-Based Model Routing
# ---------------------------------------------------------------------------
@dataclass
class QualityScore:
    """Quality scores for a provider on various dimensions.

    In a real system, these scores would be computed from evaluation
    benchmarks (e.g., MMLU, HumanEval, MT-Bench) run periodically.
    """
    provider_name: str
    accuracy: float       # 0.0 to 1.0
    coherence: float      # 0.0 to 1.0
    instruction_following: float  # 0.0 to 1.0
    reasoning: float      # 0.0 to 1.0


def route_by_quality(
    scores: list[QualityScore],
    task_type: str,
    min_score: float = 0.0,
) -> list[str]:
    """Route to the highest-quality provider for a given task type.

    Maps task types to the most relevant quality dimension, then
    ranks providers by that dimension. This enables task-aware routing:
    use the best reasoning model for analysis, the best coherence model
    for writing, etc.
    """

    def _get_relevant_score(qs: QualityScore) -> float:
        """Extract the score relevant to the task type."""
        if task_type == "analysis":
            return qs.reasoning
        elif task_type == "writing":
            return qs.coherence
        elif task_type == "coding":
            return qs.accuracy
        elif task_type == "general":
            return (qs.accuracy + qs.coherence +
                    qs.instruction_following + qs.reasoning) / 4.0
        else:
            return qs.instruction_following

    # Filter by minimum score threshold, then sort descending
    filtered = [
        (qs.provider_name, _get_relevant_score(qs))
        for qs in scores
        if _get_relevant_score(qs) >= min_score
    ]

    # Sort by score descending (highest quality first)
    filtered.sort(key=lambda x: x[1], reverse=True)

    return [name for name, _ in filtered]


# ---------------------------------------------------------------------------
# Exercise 6: Build a Latency-Based Router with Historical Data
# ---------------------------------------------------------------------------
@dataclass
class LatencyRecord:
    """A single latency measurement for time-series analysis."""
    provider_name: str
    latency_ms: float
    timestamp: float
    was_successful: bool


def route_by_latency(
    records: list[LatencyRecord],
    window_seconds: float = 300.0,
    current_time: float | None = None,
    p_value: int = 95,
) -> list[str]:
    """Route to the fastest provider based on recent p-percentile latency.

    Uses the nearest-rank method for percentile calculation, which is
    the simplest and most commonly used approach. This helps avoid
    routing based on best-case latency (which is misleading) and instead
    uses tail latency for more realistic performance expectations.
    """
    if current_time is None:
        current_time = time.time()

    cutoff = current_time - window_seconds

    # Group successful records by provider within the time window
    provider_latencies: dict[str, list[float]] = defaultdict(list)
    for record in records:
        if (record.was_successful
                and record.timestamp >= cutoff):
            provider_latencies[record.provider_name].append(record.latency_ms)

    # Compute p-th percentile for each provider using nearest-rank method
    provider_percentiles: list[tuple[str, float]] = []
    for provider, latencies in provider_latencies.items():
        if not latencies:
            continue
        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)
        # Nearest-rank: rank = ceil(p/100 * n), 1-indexed
        rank = math.ceil(p_value / 100.0 * n)
        # Clamp rank to valid range
        rank = max(1, min(rank, n))
        percentile_val = sorted_latencies[rank - 1]  # convert to 0-indexed
        provider_percentiles.append((provider, percentile_val))

    # Sort by percentile latency ascending (fastest first)
    provider_percentiles.sort(key=lambda x: x[1])

    return [name for name, _ in provider_percentiles]


# ---------------------------------------------------------------------------
# Exercise 7: Implement a Failover Chain with Health Checks
# ---------------------------------------------------------------------------
@dataclass
class ProviderHealth:
    """Health status tracking for failover decisions.

    In production, this would be updated by a background health checker
    that periodically pings each provider's API.
    """
    provider_name: str
    is_healthy: bool
    consecutive_failures: int
    last_check_time: float
    error_rate_1h: float


def build_failover_chain(
    providers: list[str],
    health_statuses: dict[str, ProviderHealth],
    max_error_rate: float = 0.1,
    max_consecutive_failures: int = 3,
) -> list[str]:
    """Build an ordered failover chain of healthy providers.

    The failover chain preserves the original priority ordering from the
    providers list but removes any provider that fails health checks.
    This is a common pattern: primary -> secondary -> tertiary providers,
    where unhealthy ones are temporarily removed from rotation.
    """
    chain = []

    for provider_name in providers:
        # Skip providers without health data (unknown = unsafe)
        if provider_name not in health_statuses:
            continue

        health = health_statuses[provider_name]

        # All three conditions must pass for the provider to be included
        if (health.is_healthy
                and health.error_rate_1h <= max_error_rate
                and health.consecutive_failures < max_consecutive_failures):
            chain.append(provider_name)

    return chain


# =============================================================================
# SECTION 3: Multimodal Capabilities
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 8: Build an Image Preprocessing Pipeline for Vision APIs
# ---------------------------------------------------------------------------
@dataclass
class ImageMetadata:
    """Metadata about a processed image, useful for logging and debugging."""
    original_size_bytes: int
    processed_size_bytes: int
    width: int
    height: int
    format: str
    was_resized: bool
    was_converted: bool


def preprocess_image_for_api(
    image_bytes: bytes,
    image_format: str,
    max_dimension: int = 2048,
    max_size_bytes: int = 5_000_000,
    target_format: str = "png",
    original_width: int = 1000,
    original_height: int = 800,
) -> tuple[str, ImageMetadata]:
    """Preprocess an image for sending to a vision API.

    In a real system, you would use PIL/Pillow for actual image
    manipulation. Here we simulate the logic to focus on the
    preprocessing decision-making pipeline.
    """
    original_size = len(image_bytes)
    was_resized = False
    was_converted = False
    width = original_width
    height = original_height

    # Step 1: Check if resizing is needed
    if original_width > max_dimension or original_height > max_dimension:
        was_resized = True
        # Scale down maintaining aspect ratio: the larger side becomes max_dimension
        if original_width >= original_height:
            scale = max_dimension / original_width
            width = max_dimension
            height = int(original_height * scale)
        else:
            scale = max_dimension / original_height
            height = max_dimension
            width = int(original_width * scale)

    # Step 2: Check if format conversion is needed
    if image_format != target_format:
        was_converted = True

    # Step 3: Simulate size reduction
    processed_size = min(original_size, max_size_bytes)

    # Step 4: Base64-encode the image bytes for API transport
    b64_encoded = base64.b64encode(image_bytes).decode("utf-8")

    metadata = ImageMetadata(
        original_size_bytes=original_size,
        processed_size_bytes=processed_size,
        width=width,
        height=height,
        format=target_format if was_converted else image_format,
        was_resized=was_resized,
        was_converted=was_converted,
    )

    return b64_encoded, metadata


# ---------------------------------------------------------------------------
# Exercise 9: Implement a Multimodal Request Builder
# ---------------------------------------------------------------------------
def build_multimodal_request_anthropic(
    text_prompt: str,
    image_data_list: list[dict],
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 1024,
) -> dict:
    """Build a multimodal request for the Anthropic API.

    Anthropic uses structured content blocks where images are represented
    with a "source" object containing type, media_type, and data fields.
    Images are placed before text in the content array so the model
    "sees" them before reading the instruction.
    """
    content_blocks = []

    # Add image blocks first
    for img in image_data_list:
        content_blocks.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": img["media_type"],
                "data": img["base64_data"],
            },
        })

    # Add text block last
    content_blocks.append({
        "type": "text",
        "text": text_prompt,
    })

    return {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": content_blocks,
            }
        ],
    }


def build_multimodal_request_openai(
    text_prompt: str,
    image_data_list: list[dict],
    model: str = "gpt-4o",
    max_tokens: int = 1024,
) -> dict:
    """Build a multimodal request for the OpenAI API.

    OpenAI uses a different format: images are encoded as data URIs
    within an "image_url" object. The data URI format is:
    data:{media_type};base64,{base64_data}
    """
    content_blocks = []

    # Add image blocks first
    for img in image_data_list:
        data_uri = f"data:{img['media_type']};base64,{img['base64_data']}"
        content_blocks.append({
            "type": "image_url",
            "image_url": {
                "url": data_uri,
            },
        })

    # Add text block last
    content_blocks.append({
        "type": "text",
        "text": text_prompt,
    })

    return {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": content_blocks,
            }
        ],
    }


# =============================================================================
# SECTION 4: Provider Management & Operations
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 10: Build a Provider Feature Parity Matrix Checker
# ---------------------------------------------------------------------------
@dataclass
class ProviderCapabilities:
    """Feature capabilities of a provider.

    This dataclass captures the full feature surface of a provider,
    making it easy to compare what each provider supports.
    """
    provider_name: str
    supports_chat: bool
    supports_completion: bool
    supports_embedding: bool
    supports_vision: bool
    supports_audio: bool
    supports_function_calling: bool
    supports_streaming: bool
    supports_json_mode: bool
    max_context_window: int


def build_feature_parity_matrix(
    capabilities: list[ProviderCapabilities],
) -> dict[str, dict[str, Any]]:
    """Build a feature parity matrix across providers.

    Transforms the per-provider view into a per-feature view, making
    it easy to see which providers support each feature at a glance.
    This is exactly the kind of comparison table you would present
    to a customer evaluating multi-provider strategies.
    """
    # Define the mapping from feature name to attribute name
    bool_features = {
        "chat": "supports_chat",
        "completion": "supports_completion",
        "embedding": "supports_embedding",
        "vision": "supports_vision",
        "audio": "supports_audio",
        "function_calling": "supports_function_calling",
        "streaming": "supports_streaming",
        "json_mode": "supports_json_mode",
    }

    matrix: dict[str, dict[str, Any]] = {}

    # Boolean features
    for feature_name, attr_name in bool_features.items():
        matrix[feature_name] = {}
        for cap in capabilities:
            matrix[feature_name][cap.provider_name] = getattr(cap, attr_name)

    # Numeric features
    matrix["max_context_window"] = {}
    for cap in capabilities:
        matrix["max_context_window"][cap.provider_name] = cap.max_context_window

    return matrix


def find_feature_gaps(
    matrix: dict[str, dict[str, Any]],
    reference_provider: str,
) -> dict[str, list[str]]:
    """Find features that other providers lack compared to a reference.

    This is critical for migration planning: if a customer is moving
    from OpenAI to Anthropic, they need to know which features they
    might lose.
    """
    gaps: dict[str, list[str]] = {}

    for feature_name, provider_values in matrix.items():
        # Get the reference provider's value
        ref_value = provider_values.get(reference_provider)
        if ref_value is None:
            continue

        lacking_providers = []
        for provider, value in provider_values.items():
            if provider == reference_provider:
                continue

            if isinstance(ref_value, bool):
                # For boolean features: gap if reference has True but other has False
                if ref_value is True and value is False:
                    lacking_providers.append(provider)
            elif isinstance(ref_value, (int, float)):
                # For numeric features: gap if other has a smaller value
                if value < ref_value:
                    lacking_providers.append(provider)

        if lacking_providers:
            gaps[feature_name] = sorted(lacking_providers)

    return gaps


# ---------------------------------------------------------------------------
# Exercise 11: Implement a Provider Benchmark Runner
# ---------------------------------------------------------------------------
@dataclass
class BenchmarkResult:
    """Result from a single benchmark run.

    Captures all the data needed to compare providers: performance,
    cost, and reliability metrics.
    """
    provider_name: str
    prompt: str
    response: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    success: bool
    error: str | None


def run_mock_benchmark(
    providers: dict[str, CompletionProvider],
    provider_configs: dict[str, ProviderConfig],
    prompts: list[str],
) -> list[BenchmarkResult]:
    """Run benchmark prompts against all providers and collect results.

    In a real system, this would make actual API calls with timing.
    Here we use the mock providers to demonstrate the benchmarking
    framework structure.
    """
    results: list[BenchmarkResult] = []

    for prompt_text in prompts:
        for provider_name, provider in providers.items():
            request = CompletionRequest(
                model="benchmark-model",
                messages=[{"role": "user", "content": prompt_text}],
            )

            try:
                response = provider.complete(request)

                # Calculate cost using the provider config if available
                cost = 0.0
                if provider_name in provider_configs:
                    cost = provider_configs[provider_name].estimate_cost(
                        response.input_tokens, response.output_tokens
                    )

                results.append(BenchmarkResult(
                    provider_name=provider_name,
                    prompt=prompt_text,
                    response=response.content,
                    latency_ms=response.latency_ms,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    cost_usd=cost,
                    success=True,
                    error=None,
                ))
            except Exception as e:
                results.append(BenchmarkResult(
                    provider_name=provider_name,
                    prompt=prompt_text,
                    response="",
                    latency_ms=0.0,
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    success=False,
                    error=str(e),
                ))

    return results


def summarize_benchmark(
    results: list[BenchmarkResult],
) -> dict[str, dict[str, float]]:
    """Summarize benchmark results per provider.

    Aggregates individual run metrics into per-provider summaries,
    which is the format you would present in a benchmark report
    or customer-facing comparison document.
    """
    # Group results by provider
    by_provider: dict[str, list[BenchmarkResult]] = defaultdict(list)
    for r in results:
        by_provider[r.provider_name].append(r)

    summary: dict[str, dict[str, float]] = {}

    for provider_name, provider_results in by_provider.items():
        successful = [r for r in provider_results if r.success]
        total = len(provider_results)

        if successful:
            avg_latency = sum(r.latency_ms for r in successful) / len(successful)
            avg_output_tokens = sum(r.output_tokens for r in successful) / len(successful)
        else:
            avg_latency = 0.0
            avg_output_tokens = 0.0

        total_cost = sum(r.cost_usd for r in provider_results)
        success_rate = len(successful) / total if total > 0 else 0.0

        summary[provider_name] = {
            "avg_latency_ms": avg_latency,
            "total_cost_usd": total_cost,
            "success_rate": success_rate,
            "avg_output_tokens": avg_output_tokens,
        }

    return summary


# ---------------------------------------------------------------------------
# Exercise 12: Build a Load Balancer Across Providers
# ---------------------------------------------------------------------------
class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_LOADED = "least_loaded"


@dataclass
class LoadBalancerState:
    """State for the load balancer.

    Uses dataclass with field(default_factory=...) for mutable defaults,
    similar to how you would handle mutable state in a Swift class.
    """
    providers: list[str]
    weights: dict[str, float]
    current_index: int = 0
    active_requests: dict[str, int] = field(default_factory=dict)


def select_provider(
    state: LoadBalancerState,
    strategy: LoadBalancingStrategy,
) -> tuple[str, LoadBalancerState]:
    """Select the next provider using the given load balancing strategy.

    Three strategies cover the most common production needs:
    - Round robin: even distribution, simplest to understand
    - Weighted: distribute based on provider capacity/preference
    - Least loaded: dynamic balancing based on current load
    """
    # Ensure all providers have an active_requests entry
    for p in state.providers:
        if p not in state.active_requests:
            state.active_requests[p] = 0

    if strategy == LoadBalancingStrategy.ROUND_ROBIN:
        selected = state.providers[state.current_index]
        # Advance index, wrapping around
        new_index = (state.current_index + 1) % len(state.providers)
        state.current_index = new_index
        state.active_requests[selected] = state.active_requests.get(selected, 0) + 1
        return selected, state

    elif strategy == LoadBalancingStrategy.WEIGHTED:
        # Sort by fewest active requests first, then highest weight
        candidates = sorted(
            state.providers,
            key=lambda p: (state.active_requests.get(p, 0), -state.weights.get(p, 0.0)),
        )
        selected = candidates[0]
        state.active_requests[selected] = state.active_requests.get(selected, 0) + 1
        return selected, state

    elif strategy == LoadBalancingStrategy.LEAST_LOADED:
        # Pick provider with fewest active requests (ties broken by list order)
        selected = min(
            state.providers,
            key=lambda p: state.active_requests.get(p, 0),
        )
        state.active_requests[selected] = state.active_requests.get(selected, 0) + 1
        return selected, state

    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def release_provider(
    state: LoadBalancerState,
    provider_name: str,
) -> LoadBalancerState:
    """Release a provider after a request completes.

    Decrements the active request count, flooring at 0 to prevent
    negative counts from mismatched release calls.
    """
    current = state.active_requests.get(provider_name, 0)
    state.active_requests[provider_name] = max(0, current - 1)
    return state


# ---------------------------------------------------------------------------
# Exercise 13: Implement Geographic Routing Based on Data Residency
# ---------------------------------------------------------------------------
@dataclass
class DataResidencyRule:
    """A data residency constraint for compliance.

    In enterprise AI deployments, data sovereignty is critical:
    certain data (especially PII) may only be processed in specific
    geographic regions due to regulations like GDPR, CCPA, etc.
    """
    rule_name: str
    allowed_regions: list[str]
    data_classification: str


def route_by_geography(
    providers: dict[str, ProviderConfig],
    residency_rule: DataResidencyRule,
) -> list[str]:
    """Route to providers that comply with data residency requirements.

    Checks the intersection between each provider's available regions
    and the residency rule's allowed regions. Only providers with at
    least one overlapping region are included.
    """
    compliant = []

    for name, config in providers.items():
        if not config.is_enabled:
            continue

        # Check if the provider has at least one allowed region
        provider_regions = set(config.regions)
        allowed_regions = set(residency_rule.allowed_regions)

        if provider_regions & allowed_regions:  # set intersection
            compliant.append(name)

    # Sort alphabetically for deterministic ordering
    return sorted(compliant)


# ---------------------------------------------------------------------------
# Exercise 14: Build a Provider Health Dashboard Data Collector
# ---------------------------------------------------------------------------
@dataclass
class HealthSnapshot:
    """A point-in-time health snapshot for monitoring.

    In production, these would be collected by a background health
    check service running every 30-60 seconds.
    """
    provider_name: str
    timestamp: float
    is_up: bool
    response_time_ms: float
    error_count: int
    request_count: int


def compute_health_dashboard(
    snapshots: list[HealthSnapshot],
    window_seconds: float = 3600.0,
    current_time: float | None = None,
) -> dict[str, dict[str, Any]]:
    """Compute health dashboard metrics from snapshots.

    Aggregates raw health snapshots into actionable dashboard metrics
    with a traffic-light status system (healthy/degraded/unhealthy).
    """
    if current_time is None:
        current_time = time.time()

    cutoff = current_time - window_seconds

    # Group snapshots by provider within the time window
    by_provider: dict[str, list[HealthSnapshot]] = defaultdict(list)
    for snap in snapshots:
        if snap.timestamp >= cutoff:
            by_provider[snap.provider_name].append(snap)

    dashboard: dict[str, dict[str, Any]] = {}

    for provider_name, provider_snapshots in by_provider.items():
        total_snapshots = len(provider_snapshots)
        up_count = sum(1 for s in provider_snapshots if s.is_up)

        uptime_pct = (up_count / total_snapshots * 100.0) if total_snapshots > 0 else 0.0
        avg_response = (
            sum(s.response_time_ms for s in provider_snapshots) / total_snapshots
            if total_snapshots > 0 else 0.0
        )
        total_errors = sum(s.error_count for s in provider_snapshots)
        total_requests = sum(s.request_count for s in provider_snapshots)
        error_rate = total_errors / total_requests if total_requests > 0 else 0.0

        # Determine status using traffic-light thresholds
        if uptime_pct >= 99.0 and error_rate < 0.05:
            status = "healthy"
        elif uptime_pct >= 95.0 and error_rate < 0.10:
            status = "degraded"
        else:
            status = "unhealthy"

        dashboard[provider_name] = {
            "uptime_pct": uptime_pct,
            "avg_response_time_ms": avg_response,
            "total_errors": total_errors,
            "total_requests": total_requests,
            "error_rate": error_rate,
            "status": status,
        }

    return dashboard


# ---------------------------------------------------------------------------
# Exercise 15: Implement a Provider Migration Helper
# ---------------------------------------------------------------------------
@dataclass
class MigrationMapping:
    """A single find-and-replace rule for prompt migration.

    Each rule documents WHY the change is needed, which is essential
    for maintaining an audit trail during provider migrations.
    """
    pattern: str
    replacement: str
    description: str


def build_migration_rules(
    source_provider: str,
    target_provider: str,
) -> list[MigrationMapping]:
    """Build migration rules for moving from one provider to another.

    These rules encode the practical differences between providers
    that affect prompt text. In a real system, this would also include
    API parameter name changes, token limit adjustments, etc.
    """
    if source_provider == "openai" and target_provider == "anthropic":
        return [
            MigrationMapping(
                pattern="You are a helpful assistant.",
                replacement="You are a helpful, harmless, and honest assistant.",
                description="Adapt system prompt for Anthropic style",
            ),
            MigrationMapping(
                pattern="```json",
                replacement="```json",
                description="JSON format marker -- no change needed",
            ),
            MigrationMapping(
                pattern="function_call",
                replacement="tool_use",
                description="Rename function calling to tool use",
            ),
        ]
    elif source_provider == "anthropic" and target_provider == "openai":
        return [
            MigrationMapping(
                pattern="tool_use",
                replacement="function_call",
                description="Rename tool use to function calling",
            ),
            MigrationMapping(
                pattern="You are a helpful, harmless, and honest assistant.",
                replacement="You are a helpful assistant.",
                description="Adapt system prompt for OpenAI style",
            ),
        ]
    else:
        return []


def migrate_prompt(
    prompt: str,
    rules: list[MigrationMapping],
) -> tuple[str, list[str]]:
    """Apply migration rules to transform a prompt.

    Rules are applied sequentially (order matters), and only rules
    that actually match are recorded. This produces an audit log of
    what changed and why.
    """
    applied_descriptions: list[str] = []

    for rule in rules:
        if rule.pattern in prompt:
            prompt = prompt.replace(rule.pattern, rule.replacement)
            applied_descriptions.append(rule.description)

    return prompt, applied_descriptions


# =============================================================================
# Test Suite
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Module 08: Multi-Provider & Multi-Modal AI -- Solution Tests")
    print("=" * 60)

    # --- Exercise 1: Provider Configuration ---
    print("\n--- Exercise 1: Provider Configuration ---")
    configs = build_provider_configs()
    assert "openai" in configs
    assert "anthropic" in configs
    assert "google" in configs
    assert configs["openai"].tier == ProviderTier.PREMIUM
    assert configs["openai"].supports_vision is True
    cost = configs["openai"].estimate_cost(1000, 500)
    assert cost > 0, "Cost should be positive"
    # Verify cost calculation: (1000/1000 * 0.005) + (500/1000 * 0.015) = 0.0125
    assert abs(cost - 0.0125) < 0.001, f"Expected ~0.0125, got {cost}"
    assert configs["openai"].supports_feature("vision") is True
    assert configs["openai"].supports_feature("streaming") is True
    assert configs["openai"].supports_feature("teleportation") is False
    print("  PASSED")

    # --- Exercise 2: Unified Completion Interface ---
    print("\n--- Exercise 2: Unified Completion Interface ---")
    request = CompletionRequest(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": "Hello"}],
    )
    assert request.max_tokens == 1024
    assert request.temperature == 0.7
    assert request.stop_sequences == []

    anthropic_provider = MockAnthropicProvider()
    assert anthropic_provider.provider_name == "anthropic"
    assert anthropic_provider.is_available() is True
    response = anthropic_provider.complete(request)
    assert response.provider == "anthropic"
    assert response.content == "Mock Anthropic response"
    assert response.latency_ms == 100.0

    openai_provider = MockOpenAIProvider()
    assert openai_provider.provider_name == "openai"
    response = openai_provider.complete(request)
    assert response.provider == "openai"
    assert response.content == "Mock OpenAI response"

    # Test format_messages for Anthropic (system extraction)
    formatted = anthropic_provider.format_messages([
        {"role": "system", "content": "Be helpful"},
        {"role": "user", "content": "Hi"},
    ])
    assert formatted["system"] == "Be helpful"
    assert len(formatted["messages"]) == 1
    assert formatted["messages"][0]["role"] == "user"

    # Test format_messages for OpenAI (pass-through)
    msgs = [{"role": "user", "content": "Hi"}]
    assert openai_provider.format_messages(msgs) == msgs
    print("  PASSED")

    # --- Exercise 3: Model Mapping Registry ---
    print("\n--- Exercise 3: Model Mapping Registry ---")
    registry = build_model_registry()
    assert "best" in registry
    assert "good" in registry
    assert "fast" in registry
    assert "vision" in registry
    assert resolve_model(registry, "best", "openai") == "gpt-4o"
    assert resolve_model(registry, "best", "anthropic") == "claude-sonnet-4-20250514"
    assert resolve_model(registry, "good", "google") == "gemini-1.5-flash"
    try:
        resolve_model(registry, "nonexistent", "openai")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass
    try:
        resolve_model(registry, "best", "nonexistent_provider")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass
    print("  PASSED")

    # --- Exercise 4: Cost-Based Routing ---
    print("\n--- Exercise 4: Cost-Based Routing ---")
    configs = build_provider_configs()
    ranked = route_by_cost(configs, 1000, 500)
    assert isinstance(ranked, list)
    assert len(ranked) == 3
    costs = [configs[p].estimate_cost(1000, 500) for p in ranked]
    assert costs == sorted(costs), "Should be sorted by cost ascending"
    # Google should be cheapest with lowest rates
    assert ranked[0] == "google"

    # Test with budget constraint
    tiny_budget = 0.002
    budget_ranked = route_by_cost(configs, 1000, 500, max_budget_usd=tiny_budget)
    # Only Google should fit under this budget
    for p in budget_ranked:
        assert configs[p].estimate_cost(1000, 500) <= tiny_budget
    print("  PASSED")

    # --- Exercise 5: Quality-Based Routing ---
    print("\n--- Exercise 5: Quality-Based Routing ---")
    scores = [
        QualityScore(provider_name="openai", accuracy=0.9, coherence=0.85,
                     instruction_following=0.88, reasoning=0.87),
        QualityScore(provider_name="anthropic", accuracy=0.88, coherence=0.92,
                     instruction_following=0.91, reasoning=0.93),
        QualityScore(provider_name="google", accuracy=0.82, coherence=0.80,
                     instruction_following=0.83, reasoning=0.79),
    ]
    analysis_ranked = route_by_quality(scores, "analysis")
    assert analysis_ranked[0] == "anthropic", "Anthropic has highest reasoning (0.93)"
    writing_ranked = route_by_quality(scores, "writing")
    assert writing_ranked[0] == "anthropic", "Anthropic has highest coherence (0.92)"
    coding_ranked = route_by_quality(scores, "coding")
    assert coding_ranked[0] == "openai", "OpenAI has highest accuracy (0.9)"

    # Test min_score filter
    high_bar = route_by_quality(scores, "coding", min_score=0.89)
    assert "google" not in high_bar, "Google accuracy 0.82 < 0.89"
    print("  PASSED")

    # --- Exercise 6: Latency-Based Routing ---
    print("\n--- Exercise 6: Latency-Based Routing ---")
    now = time.time()
    records = [
        LatencyRecord("openai", 120.0, now - 10, True),
        LatencyRecord("openai", 150.0, now - 20, True),
        LatencyRecord("openai", 200.0, now - 30, True),
        LatencyRecord("anthropic", 100.0, now - 10, True),
        LatencyRecord("anthropic", 110.0, now - 20, True),
        LatencyRecord("anthropic", 105.0, now - 30, True),
        LatencyRecord("google", 180.0, now - 10, True),
        LatencyRecord("google", 95.0, now - 20, False),  # excluded: not successful
    ]
    latency_ranked = route_by_latency(records, window_seconds=300, current_time=now)
    assert latency_ranked[0] == "anthropic", "Anthropic has lowest p95 latency"
    # Google only has 1 successful record (180ms), so it should rank last
    assert "google" in latency_ranked

    # Test with expired window (no records in range)
    old_ranked = route_by_latency(records, window_seconds=1, current_time=now + 1000)
    assert len(old_ranked) == 0, "No records in window"
    print("  PASSED")

    # --- Exercise 7: Failover Chain ---
    print("\n--- Exercise 7: Failover Chain ---")
    health = {
        "openai": ProviderHealth("openai", True, 0, now, 0.02),
        "anthropic": ProviderHealth("anthropic", True, 1, now, 0.05),
        "google": ProviderHealth("google", False, 5, now, 0.20),
        "cohere": ProviderHealth("cohere", True, 2, now, 0.09),
    }
    chain = build_failover_chain(
        ["openai", "anthropic", "google", "cohere"],
        health,
        max_error_rate=0.1,
        max_consecutive_failures=3,
    )
    assert chain == ["openai", "anthropic", "cohere"]
    assert "google" not in chain, "Google: is_healthy=False, too many failures"

    # Test with unknown provider (not in health_statuses)
    chain2 = build_failover_chain(
        ["openai", "unknown_provider"], health
    )
    assert "unknown_provider" not in chain2
    print("  PASSED")

    # --- Exercise 8: Image Preprocessing ---
    print("\n--- Exercise 8: Image Preprocessing ---")
    fake_image = b"\x89PNG" + b"\x00" * 100
    b64_str, metadata = preprocess_image_for_api(
        fake_image, "png", max_dimension=2048,
        original_width=1000, original_height=800,
    )
    assert isinstance(b64_str, str)
    assert metadata.was_resized is False
    assert metadata.was_converted is False
    assert metadata.format == "png"
    assert metadata.width == 1000
    assert metadata.height == 800
    # Verify base64 round-trip
    assert base64.b64decode(b64_str) == fake_image

    # Test resizing scenario
    _, meta2 = preprocess_image_for_api(
        fake_image, "jpeg", max_dimension=512,
        original_width=1024, original_height=768,
        target_format="png",
    )
    assert meta2.was_resized is True
    assert meta2.was_converted is True
    assert meta2.width == 512
    assert meta2.height == 384  # 768 * (512/1024) = 384
    assert meta2.format == "png"
    print("  PASSED")

    # --- Exercise 9: Multimodal Request Builder ---
    print("\n--- Exercise 9: Multimodal Request Builder ---")
    images = [
        {"base64_data": "abc123", "media_type": "image/png"},
        {"base64_data": "def456", "media_type": "image/jpeg"},
    ]

    # Test Anthropic format
    anthropic_req = build_multimodal_request_anthropic("Describe these images", images)
    assert anthropic_req["model"] == "claude-sonnet-4-20250514"
    assert anthropic_req["max_tokens"] == 1024
    content = anthropic_req["messages"][0]["content"]
    assert len(content) == 3  # 2 images + 1 text
    assert content[0]["type"] == "image"
    assert content[0]["source"]["type"] == "base64"
    assert content[0]["source"]["data"] == "abc123"
    assert content[1]["type"] == "image"
    assert content[2]["type"] == "text"
    assert content[2]["text"] == "Describe these images"

    # Test OpenAI format
    openai_req = build_multimodal_request_openai("Describe these images", images)
    assert openai_req["model"] == "gpt-4o"
    content = openai_req["messages"][0]["content"]
    assert len(content) == 3
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"] == "data:image/png;base64,abc123"
    assert content[1]["image_url"]["url"] == "data:image/jpeg;base64,def456"
    assert content[2]["type"] == "text"
    print("  PASSED")

    # --- Exercise 10: Feature Parity Matrix ---
    print("\n--- Exercise 10: Feature Parity Matrix ---")
    caps = [
        ProviderCapabilities("openai", True, True, True, True, True, True, True, True, 128000),
        ProviderCapabilities("anthropic", True, False, False, True, False, True, True, False, 200000),
        ProviderCapabilities("google", True, True, True, True, False, True, True, True, 1000000),
    ]
    matrix = build_feature_parity_matrix(caps)
    assert "chat" in matrix
    assert "vision" in matrix
    assert "max_context_window" in matrix
    assert matrix["chat"]["openai"] is True
    assert matrix["completion"]["anthropic"] is False
    assert matrix["max_context_window"]["anthropic"] == 200000
    assert matrix["max_context_window"]["google"] == 1000000

    gaps = find_feature_gaps(matrix, "openai")
    assert "audio" in gaps
    assert "anthropic" in gaps["audio"]
    assert "google" in gaps["audio"]
    assert "completion" in gaps
    assert "anthropic" in gaps["completion"]
    # max_context_window: openai=128000, others are larger, so no gap
    assert "max_context_window" not in gaps
    print("  PASSED")

    # --- Exercise 11: Benchmark Runner ---
    print("\n--- Exercise 11: Benchmark Runner ---")
    mock_providers = {
        "anthropic": MockAnthropicProvider(),
        "openai": MockOpenAIProvider(),
    }
    mock_configs = build_provider_configs()
    prompts = ["Hello, world!", "What is AI?"]
    results = run_mock_benchmark(mock_providers, mock_configs, prompts)
    assert len(results) == 4  # 2 providers * 2 prompts
    assert all(isinstance(r, BenchmarkResult) for r in results)
    assert all(r.success for r in results)

    summary = summarize_benchmark(results)
    assert "anthropic" in summary
    assert "openai" in summary
    assert summary["anthropic"]["success_rate"] == 1.0
    assert summary["openai"]["success_rate"] == 1.0
    assert summary["anthropic"]["avg_latency_ms"] == 100.0
    assert summary["openai"]["avg_latency_ms"] == 120.0
    assert summary["anthropic"]["avg_output_tokens"] == 5.0
    print("  PASSED")

    # --- Exercise 12: Load Balancer ---
    print("\n--- Exercise 12: Load Balancer ---")
    lb_state = LoadBalancerState(
        providers=["openai", "anthropic", "google"],
        weights={"openai": 0.5, "anthropic": 0.3, "google": 0.2},
        current_index=0,
        active_requests={"openai": 0, "anthropic": 0, "google": 0},
    )

    # Round robin: should pick providers in order
    selected, lb_state = select_provider(lb_state, LoadBalancingStrategy.ROUND_ROBIN)
    assert selected == "openai"
    assert lb_state.current_index == 1
    assert lb_state.active_requests["openai"] == 1

    selected2, lb_state = select_provider(lb_state, LoadBalancingStrategy.ROUND_ROBIN)
    assert selected2 == "anthropic"
    assert lb_state.current_index == 2
    assert lb_state.active_requests["anthropic"] == 1

    # Release openai
    lb_state = release_provider(lb_state, "openai")
    assert lb_state.active_requests["openai"] == 0

    # Release a provider that is already at 0 (should stay at 0)
    lb_state = release_provider(lb_state, "google")
    assert lb_state.active_requests["google"] == 0

    # Least loaded: picks the one with fewest active requests
    lb_state3 = LoadBalancerState(
        providers=["a", "b", "c"],
        weights={},
        current_index=0,
        active_requests={"a": 5, "b": 2, "c": 3},
    )
    selected, lb_state3 = select_provider(lb_state3, LoadBalancingStrategy.LEAST_LOADED)
    assert selected == "b", f"Expected 'b' (2 active), got '{selected}'"
    assert lb_state3.active_requests["b"] == 3

    # Weighted: should prefer highest weight with fewest requests
    lb_state4 = LoadBalancerState(
        providers=["a", "b", "c"],
        weights={"a": 0.5, "b": 0.3, "c": 0.2},
        current_index=0,
        active_requests={"a": 0, "b": 0, "c": 0},
    )
    selected, _ = select_provider(lb_state4, LoadBalancingStrategy.WEIGHTED)
    assert selected == "a", "With equal load, highest weight wins"
    print("  PASSED")

    # --- Exercise 13: Geographic Routing ---
    print("\n--- Exercise 13: Geographic Routing ---")
    configs = build_provider_configs()
    configs["openai"].regions = ["us", "eu"]
    configs["anthropic"].regions = ["us"]
    configs["google"].regions = ["us", "eu", "asia"]

    eu_rule = DataResidencyRule("EU Data", ["eu"], "pii")
    eu_providers = route_by_geography(configs, eu_rule)
    assert "openai" in eu_providers
    assert "google" in eu_providers
    assert "anthropic" not in eu_providers, "Anthropic only has 'us' region"
    assert eu_providers == sorted(eu_providers), "Should be alphabetically sorted"

    # Test with region no one supports
    mars_rule = DataResidencyRule("Mars Data", ["mars"], "public")
    mars_providers = route_by_geography(configs, mars_rule)
    assert len(mars_providers) == 0
    print("  PASSED")

    # --- Exercise 14: Health Dashboard ---
    print("\n--- Exercise 14: Health Dashboard ---")
    now = time.time()
    snapshots = [
        HealthSnapshot("openai", now - 60, True, 100.0, 0, 100),
        HealthSnapshot("openai", now - 120, True, 110.0, 1, 100),
        HealthSnapshot("openai", now - 180, True, 105.0, 2, 100),
        HealthSnapshot("anthropic", now - 60, True, 90.0, 0, 80),
        HealthSnapshot("anthropic", now - 120, False, 500.0, 10, 80),
        HealthSnapshot("anthropic", now - 180, True, 95.0, 1, 80),
    ]
    dashboard = compute_health_dashboard(snapshots, window_seconds=3600, current_time=now)

    assert "openai" in dashboard
    assert "anthropic" in dashboard

    # OpenAI: 3/3 up = 100%, errors=3, requests=300, error_rate=0.01
    assert dashboard["openai"]["uptime_pct"] == 100.0
    assert dashboard["openai"]["total_errors"] == 3
    assert dashboard["openai"]["total_requests"] == 300
    assert dashboard["openai"]["status"] == "healthy"

    # Anthropic: 2/3 up = 66.7%, errors=11, requests=240, error_rate~0.046
    assert abs(dashboard["anthropic"]["uptime_pct"] - 66.67) < 1.0
    assert dashboard["anthropic"]["status"] == "unhealthy"  # uptime < 95%

    # Test with snapshots outside the window
    old_dashboard = compute_health_dashboard(
        snapshots, window_seconds=10, current_time=now + 5000
    )
    assert len(old_dashboard) == 0, "All snapshots outside window"
    print("  PASSED")

    # --- Exercise 15: Provider Migration ---
    print("\n--- Exercise 15: Provider Migration ---")
    rules = build_migration_rules("openai", "anthropic")
    assert len(rules) >= 2

    prompt = "You are a helpful assistant. Use function_call to get data."
    migrated, applied = migrate_prompt(prompt, rules)
    assert "helpful, harmless, and honest" in migrated
    assert "tool_use" in migrated
    assert "function_call" not in migrated
    assert len(applied) >= 2
    assert "Adapt system prompt for Anthropic style" in applied
    assert "Rename function calling to tool use" in applied

    # Reverse migration
    rules_back = build_migration_rules("anthropic", "openai")
    migrated_back, applied_back = migrate_prompt(migrated, rules_back)
    assert "function_call" in migrated_back
    assert "tool_use" not in migrated_back
    assert "You are a helpful assistant." in migrated_back

    # Unknown migration path returns empty rules
    empty_rules = build_migration_rules("google", "cohere")
    assert len(empty_rules) == 0
    no_change, no_applied = migrate_prompt("Hello", empty_rules)
    assert no_change == "Hello"
    assert len(no_applied) == 0
    print("  PASSED")

    print("\n" + "=" * 60)
    print("All 15 solution tests passed!")
    print("=" * 60)
