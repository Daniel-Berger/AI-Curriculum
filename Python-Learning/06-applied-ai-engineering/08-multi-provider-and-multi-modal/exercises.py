"""
Module 08: Multi-Provider & Multi-Modal AI -- Exercises
========================================================
Target audience: Swift/iOS developers transitioning to AI/ML engineering roles
(solutions engineer / applied AI engineer at companies like OpenAI, Anthropic,
Google, Cohere).

15 exercises covering provider abstraction layers, intelligent routing,
failover strategies, multimodal request building, and provider migration.

No API keys or external services required -- all exercises use mock data
and simulated provider interfaces.

Instructions:
- Fill in each function/class body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.

Difficulty levels:
  Easy   - Direct data modeling or single-concept implementation
  Medium - Requires combining concepts or implementing algorithms
  Hard   - Complex multi-step logic with error handling and edge cases
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Protocol


# =============================================================================
# SECTION 1: Provider Abstraction & Configuration
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 1: Build a Provider Configuration Model
# Difficulty: Easy
# ---------------------------------------------------------------------------
class ProviderTier(Enum):
    """Tier classification for model quality/cost tradeoffs."""
    PREMIUM = "premium"
    STANDARD = "standard"
    BUDGET = "budget"


@dataclass
class ProviderConfig:
    """Configuration for a single AI provider.

    Build a dataclass that stores all the configuration needed to interact
    with an AI provider (like OpenAI, Anthropic, Google, Cohere).

    Think of this like a Swift struct with Codable conformance:
        struct ProviderConfig: Codable {
            let name: String
            let apiBase: URL
            let defaultModel: String
            ...
        }

    Fields:
        - name: str -- provider identifier (e.g., "openai", "anthropic")
        - api_base: str -- base URL for the API
        - default_model: str -- default model to use
        - tier: ProviderTier -- quality/cost tier
        - max_tokens_limit: int -- maximum tokens the provider supports
        - supports_vision: bool -- whether provider supports image inputs
        - supports_streaming: bool -- whether provider supports streaming
        - cost_per_1k_input_tokens: float -- cost in USD per 1K input tokens
        - cost_per_1k_output_tokens: float -- cost in USD per 1K output tokens
        - rate_limit_rpm: int -- requests per minute limit
        - regions: list[str] -- supported geographic regions (default empty list)
        - is_enabled: bool -- whether the provider is currently active (default True)

    Methods:
        - estimate_cost(input_tokens: int, output_tokens: int) -> float:
            Calculate estimated cost in USD for a given token count.
        - supports_feature(feature: str) -> bool:
            Check if provider supports a feature. Supported feature strings
            are "vision" and "streaming". Return False for unknown features.
    """
    pass


def build_provider_configs() -> dict[str, ProviderConfig]:
    """Create a registry of at least 3 provider configurations.

    Return a dict mapping provider name to its ProviderConfig.
    Must include configs for: "openai", "anthropic", "google".

    Requirements:
        - OpenAI: premium tier, supports vision & streaming,
          api_base="https://api.openai.com/v1"
        - Anthropic: premium tier, supports vision & streaming,
          api_base="https://api.anthropic.com/v1"
        - Google: standard tier, supports vision & streaming,
          api_base="https://generativelanguage.googleapis.com/v1"

    Returns:
        Dict mapping provider name -> ProviderConfig
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Implement a Unified Completion Interface (ABC)
# Difficulty: Medium
# ---------------------------------------------------------------------------
@dataclass
class CompletionRequest:
    """A provider-agnostic completion request.

    Fields:
        - model: str -- model identifier
        - messages: list[dict] -- list of message dicts with "role" and "content"
        - max_tokens: int -- maximum tokens to generate (default 1024)
        - temperature: float -- sampling temperature (default 0.7)
        - stop_sequences: list[str] -- stop sequences (default empty list)
    """
    pass


@dataclass
class CompletionResponse:
    """A provider-agnostic completion response.

    Fields:
        - content: str -- the generated text
        - model: str -- model that was used
        - provider: str -- provider name
        - input_tokens: int -- tokens in the prompt
        - output_tokens: int -- tokens in the completion
        - latency_ms: float -- time taken in milliseconds
        - cost_usd: float -- estimated cost in USD
    """
    pass


class CompletionProvider(ABC):
    """Abstract base class for AI completion providers.

    Subclasses must implement:
        - complete(request: CompletionRequest) -> CompletionResponse
        - provider_name property -> str
        - format_messages(messages: list[dict]) -> Any:
            Convert generic messages to provider-specific format.

    Provided concrete method:
        - is_available() -> bool: Returns True (override to add health checks).
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
        """Check if the provider is currently available."""
        return True


class MockAnthropicProvider(CompletionProvider):
    """A mock Anthropic provider for testing.

    Implement all abstract methods:
        - provider_name: return "anthropic"
        - format_messages: Anthropic expects messages as-is but extracts
          any "system" role message separately. Return a dict with keys
          "system" (str or None) and "messages" (list without system messages).
        - complete: Return a CompletionResponse with content="Mock Anthropic response",
          model=request.model, provider="anthropic", input_tokens=10,
          output_tokens=5, latency_ms=100.0, cost_usd=0.001
    """
    pass


class MockOpenAIProvider(CompletionProvider):
    """A mock OpenAI provider for testing.

    Implement all abstract methods:
        - provider_name: return "openai"
        - format_messages: OpenAI accepts messages as-is (pass through).
          Return the messages list unchanged.
        - complete: Return a CompletionResponse with content="Mock OpenAI response",
          model=request.model, provider="openai", input_tokens=10,
          output_tokens=5, latency_ms=120.0, cost_usd=0.0015
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Build a Model Mapping Registry
# Difficulty: Easy
# ---------------------------------------------------------------------------
def build_model_registry() -> dict[str, dict[str, str]]:
    """Create a mapping from provider-agnostic model names to provider-specific ones.

    Map these canonical names to each provider's actual model identifier:
        - "best"     -> openai: "gpt-4o", anthropic: "claude-sonnet-4-20250514",
                        google: "gemini-1.5-pro"
        - "good"     -> openai: "gpt-4o-mini", anthropic: "claude-haiku-35-20241022",
                        google: "gemini-1.5-flash"
        - "fast"     -> openai: "gpt-4o-mini", anthropic: "claude-haiku-35-20241022",
                        google: "gemini-1.5-flash"
        - "vision"   -> openai: "gpt-4o", anthropic: "claude-sonnet-4-20250514",
                        google: "gemini-1.5-pro"

    Returns:
        Nested dict: {canonical_name: {provider_name: model_id}}
    """
    pass


def resolve_model(
    registry: dict[str, dict[str, str]],
    canonical_name: str,
    provider: str,
) -> str:
    """Resolve a canonical model name to a provider-specific model ID.

    Args:
        registry: The model registry from build_model_registry()
        canonical_name: Provider-agnostic name (e.g., "best")
        provider: Provider name (e.g., "openai")

    Returns:
        Provider-specific model ID string.

    Raises:
        KeyError: If canonical_name or provider not found in registry.
    """
    pass


# =============================================================================
# SECTION 2: Intelligent Routing
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 4: Implement Cost-Based Model Routing
# Difficulty: Medium
# ---------------------------------------------------------------------------
def route_by_cost(
    providers: dict[str, ProviderConfig],
    estimated_input_tokens: int,
    estimated_output_tokens: int,
    max_budget_usd: float | None = None,
    require_vision: bool = False,
) -> list[str]:
    """Route to the cheapest provider(s) that meet the requirements.

    Filter and rank providers by estimated cost (ascending).
    Only include enabled providers. If require_vision is True, only
    include providers that support vision. If max_budget_usd is set,
    exclude providers whose estimated cost exceeds the budget.

    Args:
        providers: Dict of provider name -> ProviderConfig
        estimated_input_tokens: Expected input token count
        estimated_output_tokens: Expected output token count
        max_budget_usd: Maximum acceptable cost (None = no limit)
        require_vision: Whether vision support is required

    Returns:
        List of provider names sorted by cost (cheapest first).
        Empty list if no providers meet the criteria.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Implement Quality-Based Model Routing
# Difficulty: Medium
# ---------------------------------------------------------------------------
@dataclass
class QualityScore:
    """Quality scores for a provider on various dimensions.

    Fields:
        - provider_name: str
        - accuracy: float -- 0.0 to 1.0
        - coherence: float -- 0.0 to 1.0
        - instruction_following: float -- 0.0 to 1.0
        - reasoning: float -- 0.0 to 1.0
    """
    pass


def route_by_quality(
    scores: list[QualityScore],
    task_type: str,
    min_score: float = 0.0,
) -> list[str]:
    """Route to the highest-quality provider for a given task type.

    Task type determines which quality dimension to prioritize:
        - "analysis"  -> sort by reasoning (descending)
        - "writing"   -> sort by coherence (descending)
        - "coding"    -> sort by accuracy (descending)
        - "general"   -> sort by average of all scores (descending)
        - any other   -> sort by instruction_following (descending)

    Only include providers whose relevant score >= min_score.

    Args:
        scores: List of QualityScore objects
        task_type: Type of task to route for
        min_score: Minimum acceptable score threshold

    Returns:
        List of provider names, best quality first.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Build a Latency-Based Router with Historical Data
# Difficulty: Medium
# ---------------------------------------------------------------------------
@dataclass
class LatencyRecord:
    """A single latency measurement.

    Fields:
        - provider_name: str
        - latency_ms: float
        - timestamp: float -- Unix timestamp
        - was_successful: bool
    """
    pass


def route_by_latency(
    records: list[LatencyRecord],
    window_seconds: float = 300.0,
    current_time: float | None = None,
    p_value: int = 95,
) -> list[str]:
    """Route to the fastest provider based on recent latency data.

    Compute the p-th percentile latency for each provider using only
    successful records within the time window. Sort by percentile
    latency ascending (fastest first).

    Percentile calculation: use the nearest-rank method.
        rank = ceil(p / 100 * n), then pick the value at that rank
        in the sorted latencies.

    Exclude providers with no successful records in the window.

    Args:
        records: Historical latency records
        window_seconds: How far back to look (seconds)
        current_time: Reference time (defaults to time.time())
        p_value: Percentile to use (e.g., 95 for p95)

    Returns:
        List of provider names sorted by percentile latency (fastest first).
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Implement a Failover Chain with Health Checks
# Difficulty: Hard
# ---------------------------------------------------------------------------
@dataclass
class ProviderHealth:
    """Health status for a provider.

    Fields:
        - provider_name: str
        - is_healthy: bool
        - consecutive_failures: int -- number of consecutive failures
        - last_check_time: float -- Unix timestamp of last health check
        - error_rate_1h: float -- error rate in the last hour (0.0 to 1.0)
    """
    pass


def build_failover_chain(
    providers: list[str],
    health_statuses: dict[str, ProviderHealth],
    max_error_rate: float = 0.1,
    max_consecutive_failures: int = 3,
) -> list[str]:
    """Build an ordered failover chain of healthy providers.

    A provider is considered "healthy enough" if:
        1. is_healthy is True, AND
        2. error_rate_1h <= max_error_rate, AND
        3. consecutive_failures < max_consecutive_failures

    Return providers that pass all checks, maintaining the original
    ordering from the `providers` list. Providers not found in
    health_statuses should be excluded (unknown health = excluded).

    Args:
        providers: Ordered list of preferred providers
        health_statuses: Dict of provider name -> ProviderHealth
        max_error_rate: Maximum acceptable error rate
        max_consecutive_failures: Maximum consecutive failures allowed

    Returns:
        Filtered list of healthy provider names in priority order.
    """
    pass


# =============================================================================
# SECTION 3: Multimodal Capabilities
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 8: Build an Image Preprocessing Pipeline for Vision APIs
# Difficulty: Medium
# ---------------------------------------------------------------------------
@dataclass
class ImageMetadata:
    """Metadata about a processed image.

    Fields:
        - original_size_bytes: int
        - processed_size_bytes: int
        - width: int
        - height: int
        - format: str -- e.g., "png", "jpeg", "webp"
        - was_resized: bool
        - was_converted: bool
    """
    pass


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

    Since we cannot use PIL in this exercise, simulate the preprocessing:

    1. Check if image needs resizing: if original_width or original_height
       exceeds max_dimension, calculate the new dimensions maintaining
       aspect ratio (scale down so the larger side equals max_dimension).
       Otherwise keep original dimensions.

    2. Check if format conversion is needed: if image_format != target_format,
       mark was_converted = True.

    3. Simulate size reduction: if the image_bytes length exceeds
       max_size_bytes, set processed_size_bytes = max_size_bytes.
       Otherwise processed_size_bytes = len(image_bytes).

    4. Base64-encode the (original) image_bytes for API transport.

    Args:
        image_bytes: Raw image data
        image_format: Current format ("png", "jpeg", etc.)
        max_dimension: Maximum width or height
        max_size_bytes: Maximum file size
        target_format: Desired output format
        original_width: Image width in pixels
        original_height: Image height in pixels

    Returns:
        Tuple of (base64_encoded_string, ImageMetadata)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Implement a Multimodal Request Builder
# Difficulty: Medium
# ---------------------------------------------------------------------------
def build_multimodal_request_anthropic(
    text_prompt: str,
    image_data_list: list[dict],
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 1024,
) -> dict:
    """Build a multimodal (text + images) request for the Anthropic API.

    Anthropic's format for vision requests uses content blocks:
        {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_data,
                            }
                        },
                        ...more images...,
                        {
                            "type": "text",
                            "text": text_prompt
                        }
                    ]
                }
            ]
        }

    Each item in image_data_list is a dict with:
        - "base64_data": str (base64-encoded image)
        - "media_type": str (e.g., "image/png")

    Images come first in the content list, then the text prompt last.

    Args:
        text_prompt: Text instruction/question about the images
        image_data_list: List of image data dicts
        model: Model identifier
        max_tokens: Max tokens to generate

    Returns:
        Complete API request dict in Anthropic's format.
    """
    pass


def build_multimodal_request_openai(
    text_prompt: str,
    image_data_list: list[dict],
    model: str = "gpt-4o",
    max_tokens: int = 1024,
) -> dict:
    """Build a multimodal (text + images) request for the OpenAI API.

    OpenAI's format for vision requests:
        {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_data}"
                            }
                        },
                        ...more images...,
                        {
                            "type": "text",
                            "text": text_prompt
                        }
                    ]
                }
            ]
        }

    Args:
        text_prompt: Text instruction/question about the images
        image_data_list: List of image data dicts with "base64_data" and "media_type"
        model: Model identifier
        max_tokens: Max tokens to generate

    Returns:
        Complete API request dict in OpenAI's format.
    """
    pass


# =============================================================================
# SECTION 4: Provider Management & Operations
# =============================================================================

# ---------------------------------------------------------------------------
# Exercise 10: Build a Provider Feature Parity Matrix Checker
# Difficulty: Easy
# ---------------------------------------------------------------------------
@dataclass
class ProviderCapabilities:
    """Feature capabilities of a provider.

    Fields:
        - provider_name: str
        - supports_chat: bool
        - supports_completion: bool
        - supports_embedding: bool
        - supports_vision: bool
        - supports_audio: bool
        - supports_function_calling: bool
        - supports_streaming: bool
        - supports_json_mode: bool
        - max_context_window: int -- max tokens in context
    """
    pass


def build_feature_parity_matrix(
    capabilities: list[ProviderCapabilities],
) -> dict[str, dict[str, Any]]:
    """Build a feature parity matrix across providers.

    Returns a dict where keys are feature names and values are dicts
    mapping provider_name -> feature_value (bool or int).

    Feature names to include (matching the ProviderCapabilities field names
    but without the "supports_" prefix for boolean fields):
        "chat", "completion", "embedding", "vision", "audio",
        "function_calling", "streaming", "json_mode", "max_context_window"

    Example output:
        {
            "chat": {"openai": True, "anthropic": True, "google": True},
            "vision": {"openai": True, "anthropic": True, "google": False},
            "max_context_window": {"openai": 128000, "anthropic": 200000, ...},
            ...
        }

    Args:
        capabilities: List of ProviderCapabilities objects

    Returns:
        Feature parity matrix dict.
    """
    pass


def find_feature_gaps(
    matrix: dict[str, dict[str, Any]],
    reference_provider: str,
) -> dict[str, list[str]]:
    """Find features that other providers lack compared to a reference.

    For each boolean feature where the reference_provider has True,
    list providers that have False. For max_context_window, list
    providers with a smaller value.

    Args:
        matrix: Feature parity matrix from build_feature_parity_matrix()
        reference_provider: Provider to compare others against

    Returns:
        Dict mapping feature_name -> list of provider names that lack it.
        Only include features where at least one provider has a gap.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Implement a Provider Benchmark Runner
# Difficulty: Hard
# ---------------------------------------------------------------------------
@dataclass
class BenchmarkResult:
    """Result from a single benchmark run.

    Fields:
        - provider_name: str
        - prompt: str
        - response: str
        - latency_ms: float
        - input_tokens: int
        - output_tokens: int
        - cost_usd: float
        - success: bool
        - error: str | None
    """
    pass


def run_mock_benchmark(
    providers: dict[str, CompletionProvider],
    provider_configs: dict[str, ProviderConfig],
    prompts: list[str],
) -> list[BenchmarkResult]:
    """Run benchmark prompts against all providers and collect results.

    For each prompt, call each provider's complete() method and record
    the results. If a provider raises an exception, record it as a
    failed result with the exception message as the error.

    Use the provider_configs to calculate cost_usd via estimate_cost().
    Use the CompletionResponse fields for latency_ms, input_tokens,
    output_tokens.

    Args:
        providers: Dict of provider name -> CompletionProvider instance
        provider_configs: Dict of provider name -> ProviderConfig
        prompts: List of test prompts to benchmark

    Returns:
        List of BenchmarkResult for every (provider, prompt) combination.
    """
    pass


def summarize_benchmark(
    results: list[BenchmarkResult],
) -> dict[str, dict[str, float]]:
    """Summarize benchmark results per provider.

    For each provider compute:
        - "avg_latency_ms": average latency across successful runs
        - "total_cost_usd": sum of all costs
        - "success_rate": fraction of successful runs (0.0 to 1.0)
        - "avg_output_tokens": average output tokens for successful runs

    Only include results where success is True when computing averages.
    If a provider has no successful runs, set avg_latency_ms and
    avg_output_tokens to 0.0.

    Args:
        results: List of BenchmarkResult objects

    Returns:
        Dict mapping provider_name -> summary stats dict.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Build a Load Balancer Across Providers
# Difficulty: Hard
# ---------------------------------------------------------------------------
class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_LOADED = "least_loaded"


@dataclass
class LoadBalancerState:
    """State for the load balancer.

    Fields:
        - providers: list[str] -- available provider names
        - weights: dict[str, float] -- weight per provider (for weighted strategy)
        - current_index: int -- current position for round robin (default 0)
        - active_requests: dict[str, int] -- count of in-flight requests per provider
            (default empty dict via field(default_factory=dict))
    """
    pass


def select_provider(
    state: LoadBalancerState,
    strategy: LoadBalancingStrategy,
) -> tuple[str, LoadBalancerState]:
    """Select the next provider using the given strategy.

    Strategies:
        - ROUND_ROBIN: Pick the provider at current_index, then increment
          current_index (wrapping around). Update active_requests += 1.
        - WEIGHTED: Pick the provider with the highest weight that also has
          the fewest active_requests (break ties by weight descending, then
          by list order). Update active_requests += 1.
        - LEAST_LOADED: Pick the provider with the fewest active_requests.
          Break ties by list order. Update active_requests += 1.

    Args:
        state: Current load balancer state
        strategy: Which strategy to use

    Returns:
        Tuple of (selected_provider_name, updated_state).
        Return a new LoadBalancerState (or mutated copy) with updated
        current_index and active_requests.
    """
    pass


def release_provider(
    state: LoadBalancerState,
    provider_name: str,
) -> LoadBalancerState:
    """Release a provider after a request completes.

    Decrement active_requests for the provider (minimum 0).

    Args:
        state: Current load balancer state
        provider_name: Provider to release

    Returns:
        Updated LoadBalancerState.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 13: Implement Geographic Routing Based on Data Residency
# Difficulty: Medium
# ---------------------------------------------------------------------------
@dataclass
class DataResidencyRule:
    """A data residency constraint.

    Fields:
        - rule_name: str -- descriptive name
        - allowed_regions: list[str] -- regions where data can be processed
        - data_classification: str -- e.g., "pii", "public", "confidential"
    """
    pass


def route_by_geography(
    providers: dict[str, ProviderConfig],
    residency_rule: DataResidencyRule,
) -> list[str]:
    """Route to providers that comply with data residency requirements.

    A provider complies if it has at least one region in its `regions`
    list that is also in the residency_rule's `allowed_regions`.
    Only include enabled providers.

    Return compliant provider names sorted alphabetically.

    Args:
        providers: Dict of provider name -> ProviderConfig
        residency_rule: The data residency constraint to apply

    Returns:
        List of compliant provider names (sorted alphabetically).
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 14: Build a Provider Health Dashboard Data Collector
# Difficulty: Medium
# ---------------------------------------------------------------------------
@dataclass
class HealthSnapshot:
    """A point-in-time health snapshot for a provider.

    Fields:
        - provider_name: str
        - timestamp: float
        - is_up: bool
        - response_time_ms: float
        - error_count: int
        - request_count: int
    """
    pass


def compute_health_dashboard(
    snapshots: list[HealthSnapshot],
    window_seconds: float = 3600.0,
    current_time: float | None = None,
) -> dict[str, dict[str, Any]]:
    """Compute health dashboard metrics from snapshots.

    For each provider, using only snapshots within the time window, compute:
        - "uptime_pct": percentage of snapshots where is_up is True (0-100)
        - "avg_response_time_ms": average response_time_ms
        - "total_errors": sum of error_count
        - "total_requests": sum of request_count
        - "error_rate": total_errors / total_requests (0.0 if no requests)
        - "status": "healthy" if uptime_pct >= 99.0 and error_rate < 0.05,
                    "degraded" if uptime_pct >= 95.0 and error_rate < 0.10,
                    "unhealthy" otherwise

    Providers with no snapshots in the window should not appear in results.

    Args:
        snapshots: Historical health snapshots
        window_seconds: How far back to look
        current_time: Reference time (defaults to time.time())

    Returns:
        Dict mapping provider_name -> metrics dict.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 15: Implement a Provider Migration Helper
# Difficulty: Hard
# ---------------------------------------------------------------------------
@dataclass
class MigrationMapping:
    """A mapping rule for migrating prompts between providers.

    Fields:
        - pattern: str -- substring to find in the prompt
        - replacement: str -- replacement string
        - description: str -- why this migration is needed
    """
    pass


def build_migration_rules(
    source_provider: str,
    target_provider: str,
) -> list[MigrationMapping]:
    """Build migration rules for moving from one provider to another.

    Define rules for these migration paths:

    "openai" -> "anthropic":
        1. Replace "You are a helpful assistant." with
           "You are a helpful, harmless, and honest assistant."
           (description: "Adapt system prompt for Anthropic style")
        2. Replace "```json" with "```json"
           (description: "JSON format marker -- no change needed")
        3. Replace "function_call" with "tool_use"
           (description: "Rename function calling to tool use")

    "anthropic" -> "openai":
        1. Replace "tool_use" with "function_call"
           (description: "Rename tool use to function calling")
        2. Replace "You are a helpful, harmless, and honest assistant." with
           "You are a helpful assistant."
           (description: "Adapt system prompt for OpenAI style")

    For any other migration path, return an empty list.

    Args:
        source_provider: Provider migrating from
        target_provider: Provider migrating to

    Returns:
        List of MigrationMapping rules.
    """
    pass


def migrate_prompt(
    prompt: str,
    rules: list[MigrationMapping],
) -> tuple[str, list[str]]:
    """Apply migration rules to transform a prompt.

    Apply each rule in order: if the rule's pattern is found as a
    substring in the prompt, replace ALL occurrences with the replacement.
    Track which rules were applied (by description).

    Args:
        prompt: Original prompt text
        rules: Migration rules to apply

    Returns:
        Tuple of (migrated_prompt, list_of_applied_rule_descriptions).
        Only include descriptions of rules that actually matched.
    """
    pass


# =============================================================================
# Test Suite
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Module 08: Multi-Provider & Multi-Modal AI -- Tests")
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
    assert configs["openai"].supports_feature("vision") is True
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

    anthropic_provider = MockAnthropicProvider()
    assert anthropic_provider.provider_name == "anthropic"
    response = anthropic_provider.complete(request)
    assert response.provider == "anthropic"
    assert response.content == "Mock Anthropic response"

    openai_provider = MockOpenAIProvider()
    assert openai_provider.provider_name == "openai"
    response = openai_provider.complete(request)
    assert response.provider == "openai"

    formatted = anthropic_provider.format_messages([
        {"role": "system", "content": "Be helpful"},
        {"role": "user", "content": "Hi"},
    ])
    assert formatted["system"] == "Be helpful"
    assert len(formatted["messages"]) == 1
    print("  PASSED")

    # --- Exercise 3: Model Mapping Registry ---
    print("\n--- Exercise 3: Model Mapping Registry ---")
    registry = build_model_registry()
    assert "best" in registry
    assert "good" in registry
    assert resolve_model(registry, "best", "openai") == "gpt-4o"
    assert resolve_model(registry, "best", "anthropic") == "claude-sonnet-4-20250514"
    try:
        resolve_model(registry, "nonexistent", "openai")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass
    print("  PASSED")

    # --- Exercise 4: Cost-Based Routing ---
    print("\n--- Exercise 4: Cost-Based Routing ---")
    configs = build_provider_configs()
    ranked = route_by_cost(configs, 1000, 500)
    assert isinstance(ranked, list)
    assert len(ranked) > 0
    # Cheapest should be first
    costs = [configs[p].estimate_cost(1000, 500) for p in ranked]
    assert costs == sorted(costs), "Should be sorted by cost ascending"
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
    assert analysis_ranked[0] == "anthropic", "Anthropic has highest reasoning"
    writing_ranked = route_by_quality(scores, "writing")
    assert writing_ranked[0] == "anthropic", "Anthropic has highest coherence"
    coding_ranked = route_by_quality(scores, "coding")
    assert coding_ranked[0] == "openai", "OpenAI has highest accuracy"
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
        LatencyRecord("google", 95.0, now - 20, False),  # failed, excluded
    ]
    latency_ranked = route_by_latency(records, window_seconds=300, current_time=now)
    assert len(latency_ranked) >= 2
    assert latency_ranked[0] == "anthropic", "Anthropic should be fastest"
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
    assert "openai" in chain
    assert "anthropic" in chain
    assert "google" not in chain, "Google is not healthy"
    assert "cohere" in chain
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
    assert metadata.format == "png"
    assert metadata.width == 1000

    _, meta2 = preprocess_image_for_api(
        fake_image, "jpeg", max_dimension=512,
        original_width=1024, original_height=768,
        target_format="png",
    )
    assert meta2.was_resized is True
    assert meta2.was_converted is True
    assert meta2.width == 512
    assert meta2.height <= 512
    print("  PASSED")

    # --- Exercise 9: Multimodal Request Builder ---
    print("\n--- Exercise 9: Multimodal Request Builder ---")
    images = [
        {"base64_data": "abc123", "media_type": "image/png"},
        {"base64_data": "def456", "media_type": "image/jpeg"},
    ]
    anthropic_req = build_multimodal_request_anthropic("Describe these images", images)
    assert anthropic_req["model"] == "claude-sonnet-4-20250514"
    content = anthropic_req["messages"][0]["content"]
    assert content[-1]["type"] == "text"
    assert content[0]["type"] == "image"
    assert content[0]["source"]["type"] == "base64"

    openai_req = build_multimodal_request_openai("Describe these images", images)
    assert openai_req["model"] == "gpt-4o"
    content = openai_req["messages"][0]["content"]
    assert content[-1]["type"] == "text"
    assert content[0]["type"] == "image_url"
    assert "data:image/png;base64,abc123" in content[0]["image_url"]["url"]
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
    assert matrix["chat"]["openai"] is True
    assert matrix["max_context_window"]["anthropic"] == 200000

    gaps = find_feature_gaps(matrix, "openai")
    assert "audio" in gaps
    assert "anthropic" in gaps["audio"]
    assert "google" in gaps["audio"]
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

    summary = summarize_benchmark(results)
    assert "anthropic" in summary
    assert "openai" in summary
    assert summary["anthropic"]["success_rate"] == 1.0
    print("  PASSED")

    # --- Exercise 12: Load Balancer ---
    print("\n--- Exercise 12: Load Balancer ---")
    lb_state = LoadBalancerState(
        providers=["openai", "anthropic", "google"],
        weights={"openai": 0.5, "anthropic": 0.3, "google": 0.2},
        current_index=0,
        active_requests={"openai": 0, "anthropic": 0, "google": 0},
    )

    # Round robin
    selected, lb_state = select_provider(lb_state, LoadBalancingStrategy.ROUND_ROBIN)
    assert selected == "openai"
    assert lb_state.current_index == 1
    assert lb_state.active_requests[selected] == 1

    selected2, lb_state = select_provider(lb_state, LoadBalancingStrategy.ROUND_ROBIN)
    assert selected2 == "anthropic"

    lb_state = release_provider(lb_state, "openai")
    assert lb_state.active_requests["openai"] == 0

    # Least loaded
    lb_state3 = LoadBalancerState(
        providers=["a", "b", "c"],
        weights={},
        current_index=0,
        active_requests={"a": 5, "b": 2, "c": 3},
    )
    selected, _ = select_provider(lb_state3, LoadBalancingStrategy.LEAST_LOADED)
    assert selected == "b"
    print("  PASSED")

    # --- Exercise 13: Geographic Routing ---
    print("\n--- Exercise 13: Geographic Routing ---")
    configs = build_provider_configs()
    # Add regions to configs for this test
    configs["openai"].regions = ["us", "eu"]
    configs["anthropic"].regions = ["us"]
    configs["google"].regions = ["us", "eu", "asia"]

    eu_rule = DataResidencyRule("EU Data", ["eu"], "pii")
    eu_providers = route_by_geography(configs, eu_rule)
    assert "openai" in eu_providers
    assert "google" in eu_providers
    assert "anthropic" not in eu_providers
    assert eu_providers == sorted(eu_providers)
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
    assert dashboard["openai"]["uptime_pct"] == 100.0
    assert dashboard["openai"]["status"] == "healthy"
    # Anthropic: 2/3 up = 66.7%, so unhealthy
    assert dashboard["anthropic"]["status"] == "unhealthy"
    print("  PASSED")

    # --- Exercise 15: Provider Migration ---
    print("\n--- Exercise 15: Provider Migration ---")
    rules = build_migration_rules("openai", "anthropic")
    assert len(rules) >= 2

    prompt = "You are a helpful assistant. Use function_call to get data."
    migrated, applied = migrate_prompt(prompt, rules)
    assert "helpful, harmless, and honest" in migrated
    assert "tool_use" in migrated
    assert len(applied) >= 2

    # Reverse migration
    rules_back = build_migration_rules("anthropic", "openai")
    migrated_back, applied_back = migrate_prompt(migrated, rules_back)
    assert "function_call" in migrated_back
    print("  PASSED")

    print("\n" + "=" * 60)
    print("All 15 exercises passed!")
    print("=" * 60)
