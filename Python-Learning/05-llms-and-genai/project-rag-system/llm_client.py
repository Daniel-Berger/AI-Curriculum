"""Abstracted LLM client for the RAG pipeline.

Provides a base interface and multiple implementations for calling
LLMs to generate answers from retrieved context. Includes streaming
support and a mock client for testing without API keys.

Swift parallel:
    - BaseLLMClient ABC       ~  protocol LLMClient { }
    - ClaudeLLMClient         ~  struct ClaudeService: LLMClient { }
    - MockLLMClient           ~  struct MockService: LLMClient { } (for previews/tests)
    - Streaming via generator  ~  AsyncStream<String>

Usage:
    # With a real API key:
    client = ClaudeLLMClient(api_key="sk-...")
    answer = client.generate(context="...", question="...")

    # For testing:
    client = MockLLMClient()
    answer = client.generate(context="...", question="...")
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LLMResponse:
    """Structured response from an LLM call.

    Attributes:
        content: The generated text.
        model: The model that produced the response.
        usage: Token usage information (prompt + completion tokens).
        finish_reason: Why the model stopped generating (e.g., "stop", "max_tokens").
    """

    content: str
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

RAG_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on
the provided context. Follow these rules:
1. Only use information from the context to answer the question.
2. If the context does not contain enough information, say so clearly.
3. Cite which part of the context your answer comes from when possible.
4. Be concise but thorough."""

RAG_USER_TEMPLATE = """Context:
{context}

---

Question: {question}

Answer based only on the context above:"""


def format_rag_prompt(context: str, question: str) -> list[dict[str, str]]:
    """Format context and question into a chat message list.

    Returns a list of message dicts compatible with both the Anthropic
    and OpenAI chat APIs.

    Args:
        context: The retrieved document chunks, concatenated.
        question: The user's question.

    Returns:
        A list of {"role": ..., "content": ...} dicts.
    """
    return [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": RAG_USER_TEMPLATE.format(
                context=context, question=question
            ),
        },
    ]


# ---------------------------------------------------------------------------
# Base class (ABC)
# ---------------------------------------------------------------------------

class BaseLLMClient(ABC):
    """Abstract base class for LLM clients.

    All LLM integrations implement this interface so the RAG pipeline
    can swap providers without changing business logic. This is the
    Python equivalent of defining a Swift protocol:

        protocol LLMClient {
            func generate(context: String, question: String) -> String
            func stream(context: String, question: String) -> AsyncStream<String>
        }
    """

    @abstractmethod
    def generate(
        self,
        context: str,
        question: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate a response given context and a question.

        Args:
            context: Retrieved document chunks as a single string.
            question: The user's question.
            temperature: Sampling temperature.
            max_tokens: Maximum response length.

        Returns:
            An LLMResponse with the generated answer.
        """
        ...

    @abstractmethod
    def stream(
        self,
        context: str,
        question: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """Stream a response token-by-token.

        Yields:
            Individual tokens or text chunks as they are generated.
        """
        ...


# ---------------------------------------------------------------------------
# Claude (Anthropic) implementation
# ---------------------------------------------------------------------------

class ClaudeLLMClient(BaseLLMClient):
    """LLM client for Anthropic's Claude API.

    Requires the `anthropic` package and a valid API key.
    Set the ANTHROPIC_API_KEY environment variable or pass the key
    directly to the constructor.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
    ) -> None:
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = model

        if not self.api_key:
            raise ValueError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY "
                "environment variable or pass api_key to constructor."
            )

        try:
            import anthropic  # noqa: F401

            self._client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "The 'anthropic' package is required for ClaudeLLMClient. "
                "Install it with: pip install anthropic"
            )

    def generate(
        self,
        context: str,
        question: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate a response using Claude."""
        messages = format_rag_prompt(context, question)

        # Anthropic API uses system as a separate parameter
        system_msg = messages[0]["content"]
        user_msg = messages[1]["content"]

        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_msg,
            messages=[{"role": "user", "content": user_msg}],
        )

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason or "stop",
        )

    def stream(
        self,
        context: str,
        question: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """Stream a response from Claude token-by-token."""
        messages = format_rag_prompt(context, question)
        system_msg = messages[0]["content"]
        user_msg = messages[1]["content"]

        with self._client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_msg,
            messages=[{"role": "user", "content": user_msg}],
        ) as stream:
            for text in stream.text_stream:
                yield text


# ---------------------------------------------------------------------------
# OpenAI implementation
# ---------------------------------------------------------------------------

class OpenAILLMClient(BaseLLMClient):
    """LLM client for OpenAI's GPT API.

    Requires the `openai` package and a valid API key.
    Set the OPENAI_API_KEY environment variable or pass the key
    directly to the constructor.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o",
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model

        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY "
                "environment variable or pass api_key to constructor."
            )

        try:
            import openai  # noqa: F401

            self._client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "The 'openai' package is required for OpenAILLMClient. "
                "Install it with: pip install openai"
            )

    def generate(
        self,
        context: str,
        question: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate a response using GPT."""
        messages = format_rag_prompt(context, question)

        response = self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=messages,  # type: ignore[arg-type]
        )

        choice = response.choices[0]
        usage = response.usage

        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            usage={
                "input_tokens": usage.prompt_tokens if usage else 0,
                "output_tokens": usage.completion_tokens if usage else 0,
            },
            finish_reason=choice.finish_reason or "stop",
        )

    def stream(
        self,
        context: str,
        question: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """Stream a response from GPT token-by-token."""
        messages = format_rag_prompt(context, question)

        stream = self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=messages,  # type: ignore[arg-type]
            stream=True,
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# ---------------------------------------------------------------------------
# Mock implementation (for testing)
# ---------------------------------------------------------------------------

class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing without API keys.

    Returns deterministic responses based on the input, making it
    ideal for unit tests and development. In Swift terms, this is
    like creating a mock conforming to your protocol for SwiftUI
    previews or XCTest.

    Attributes:
        responses: A list of canned responses to return in order.
        call_history: Records all calls for assertion in tests.
    """

    def __init__(
        self,
        responses: list[str] | None = None,
        model: str = "mock-model",
    ) -> None:
        self.model = model
        self._responses = responses or []
        self._response_index = 0
        self.call_history: list[dict[str, str]] = []

    def generate(
        self,
        context: str,
        question: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Return a mock response.

        If canned responses were provided, returns them in order
        (cycling back to the first when exhausted). Otherwise,
        generates a simple echo response.
        """
        self.call_history.append({"context": context, "question": question})

        if self._responses:
            content = self._responses[self._response_index % len(self._responses)]
            self._response_index += 1
        else:
            content = (
                f"Based on the provided context, here is the answer to "
                f"'{question}': The context discusses relevant information "
                f"that addresses this query."
            )

        logger.debug("MockLLMClient returning: %s", content[:80])

        return LLMResponse(
            content=content,
            model=self.model,
            usage={"input_tokens": len(context.split()), "output_tokens": len(content.split())},
            finish_reason="stop",
        )

    def stream(
        self,
        context: str,
        question: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """Stream a mock response word-by-word."""
        response = self.generate(
            context, question, temperature=temperature, max_tokens=max_tokens
        )
        # Simulate streaming by yielding one word at a time.
        for word in response.content.split():
            yield word + " "
