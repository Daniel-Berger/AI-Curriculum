"""Multi-provider LLM client with a unified interface.

Provides an abstract base class and concrete implementations for Anthropic,
OpenAI, and a demo/mock provider.  A factory function selects the correct
provider at runtime based on available API keys and user selection.
"""

from __future__ import annotations

import time
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generator, List, Optional

from config import AppSettings, ModelConfig, PROVIDER_MODELS


@dataclass
class Message:
    """A single chat message."""

    role: str  # "user", "assistant", or "system"
    content: str


@dataclass
class CompletionResult:
    """Result returned by a provider completion call."""

    content: str
    input_tokens: int
    output_tokens: int
    model: str
    provider: str
    latency_ms: float
    finish_reason: str = "stop"


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class BaseProvider(ABC):
    """Interface that every LLM provider must implement."""

    provider_name: str

    @abstractmethod
    def complete(
        self,
        messages: List[Message],
        model: ModelConfig,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> CompletionResult:
        """Send a list of messages and return a CompletionResult."""

    @abstractmethod
    def stream(
        self,
        messages: List[Message],
        model: ModelConfig,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """Yield response tokens one chunk at a time."""


# ---------------------------------------------------------------------------
# Demo / mock provider -- always available
# ---------------------------------------------------------------------------

_MOCK_RESPONSES: List[str] = [
    "Based on the information provided, I recommend reviewing the integration "
    "documentation for the most up-to-date guidance on this topic.",
    "That's a great question! Here is a step-by-step approach:\n\n"
    "1. First, verify your environment configuration.\n"
    "2. Next, check the API endpoint availability.\n"
    "3. Finally, run the test suite to confirm everything works.",
    "I can help with that. The key consideration here is ensuring your data "
    "pipeline handles edge cases such as empty inputs and rate-limit errors.",
    "Let me look into that. The recommended pattern for this use case is to "
    "use an asynchronous queue combined with a retry strategy.",
    "Great question! The most common approach involves three components: "
    "an ingestion layer, a processing engine, and a response cache.",
]


class DemoProvider(BaseProvider):
    """Mock provider that returns synthetic responses without an API key."""

    provider_name: str = "demo"

    def complete(
        self,
        messages: List[Message],
        model: ModelConfig,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> CompletionResult:
        start = time.perf_counter()
        response_text = random.choice(_MOCK_RESPONSES)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Approximate token counts for cost tracking demonstration.
        input_tokens = sum(len(m.content.split()) for m in messages) + len(system_prompt.split())
        output_tokens = len(response_text.split())

        return CompletionResult(
            content=response_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model.name,
            provider=self.provider_name,
            latency_ms=round(elapsed_ms, 2),
        )

    def stream(
        self,
        messages: List[Message],
        model: ModelConfig,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        response_text = random.choice(_MOCK_RESPONSES)
        words = response_text.split()
        for word in words:
            time.sleep(0.03)
            yield word + " "


# ---------------------------------------------------------------------------
# Anthropic provider stub (uses real SDK when available, else falls back)
# ---------------------------------------------------------------------------

class AnthropicProvider(BaseProvider):
    """Provider for the Anthropic Claude API."""

    provider_name: str = "anthropic"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def complete(
        self,
        messages: List[Message],
        model: ModelConfig,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> CompletionResult:
        try:
            import anthropic  # type: ignore

            client = anthropic.Anthropic(api_key=self.api_key)
            formatted = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]
            start = time.perf_counter()
            response = client.messages.create(
                model=model.name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=formatted,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            return CompletionResult(
                content=response.content[0].text,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                model=model.name,
                provider=self.provider_name,
                latency_ms=round(elapsed_ms, 2),
            )
        except ImportError:
            return DemoProvider().complete(messages, model, system_prompt, temperature, max_tokens)

    def stream(self, messages, model, system_prompt="", temperature=0.7, max_tokens=1024):
        yield from DemoProvider().stream(messages, model, system_prompt, temperature, max_tokens)


# ---------------------------------------------------------------------------
# OpenAI provider stub
# ---------------------------------------------------------------------------

class OpenAIProvider(BaseProvider):
    """Provider for the OpenAI API."""

    provider_name: str = "openai"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def complete(
        self,
        messages: List[Message],
        model: ModelConfig,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> CompletionResult:
        try:
            import openai  # type: ignore

            client = openai.OpenAI(api_key=self.api_key)
            oai_messages: list[dict] = []
            if system_prompt:
                oai_messages.append({"role": "system", "content": system_prompt})
            oai_messages.extend({"role": m.role, "content": m.content} for m in messages if m.role != "system")

            start = time.perf_counter()
            response = client.chat.completions.create(
                model=model.name,
                messages=oai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            choice = response.choices[0]
            usage = response.usage
            return CompletionResult(
                content=choice.message.content or "",
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                model=model.name,
                provider=self.provider_name,
                latency_ms=round(elapsed_ms, 2),
            )
        except ImportError:
            return DemoProvider().complete(messages, model, system_prompt, temperature, max_tokens)

    def stream(self, messages, model, system_prompt="", temperature=0.7, max_tokens=1024):
        yield from DemoProvider().stream(messages, model, system_prompt, temperature, max_tokens)


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------

def get_provider(provider_name: str, settings: AppSettings) -> BaseProvider:
    """Return the appropriate provider instance, falling back to demo mode."""

    if provider_name == "anthropic" and settings.anthropic_api_key:
        return AnthropicProvider(api_key=settings.anthropic_api_key)
    if provider_name == "openai" and settings.openai_api_key:
        return OpenAIProvider(api_key=settings.openai_api_key)
    # Google and any unknown provider fall back to demo.
    return DemoProvider()


def available_providers(settings: AppSettings) -> List[str]:
    """Return a list of provider names that are available given current keys."""
    providers = ["demo"]
    if settings.anthropic_api_key:
        providers.append("anthropic")
    if settings.openai_api_key:
        providers.append("openai")
    if settings.google_api_key:
        providers.append("google")
    return providers
