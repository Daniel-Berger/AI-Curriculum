"""
RAG Generator Module
====================

Handles LLM-based answer generation using retrieved context. Constructs
prompts with retrieved documents, manages conversation history, and
supports streaming output.

Features:
- Context-aware prompt construction
- Source citation in responses
- Streaming token generation
- Conversation history management
- Configurable system prompts and templates
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional

from .retriever import RetrievalResult


@dataclass
class GenerationConfig:
    """Configuration for the RAG generator.

    Attributes
    ----------
    model_name : str
        LLM model identifier (e.g., 'gpt-4o', 'claude-3-sonnet').
    temperature : float
        Sampling temperature (0.0 = deterministic, 1.0 = creative).
    max_tokens : int
        Maximum number of tokens to generate.
    system_prompt : str
        System message to guide the LLM's behavior.
    include_sources : bool
        Whether to append source citations to the response.
    """

    model_name: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 1024
    system_prompt: str = (
        "You are a helpful assistant. Answer the user's question based on "
        "the provided context. If the context does not contain enough "
        "information, say so. Always cite your sources."
    )
    include_sources: bool = True


@dataclass
class ChatMessage:
    """A single message in the conversation history.

    Attributes
    ----------
    role : str
        'system', 'user', or 'assistant'.
    content : str
        Message text.
    """

    role: str
    content: str


class RAGGenerator:
    """Generate answers using retrieved context and an LLM.

    Parameters
    ----------
    config : GenerationConfig, optional
        Generation configuration. Uses defaults if not provided.

    Examples
    --------
    >>> generator = RAGGenerator()
    >>> response = generator.generate(
    ...     query="What is RAG?",
    ...     retrieved_results=results,
    ... )
    """

    def __init__(
        self, config: Optional[GenerationConfig] = None
    ) -> None:
        self.config = config or GenerationConfig()
        self._conversation_history: List[ChatMessage] = []
        self._client: Optional[Any] = None

    def initialize(self) -> None:
        """Initialize the LLM client.

        Raises
        ------
        ValueError
            If required API keys are not set.
        """
        raise NotImplementedError

    def generate(
        self,
        query: str,
        retrieved_results: List[RetrievalResult],
        conversation_history: Optional[List[ChatMessage]] = None,
    ) -> str:
        """Generate an answer using the query and retrieved context.

        Parameters
        ----------
        query : str
            The user's question.
        retrieved_results : list of RetrievalResult
            Retrieved document chunks for context.
        conversation_history : list of ChatMessage, optional
            Prior conversation messages for multi-turn support.

        Returns
        -------
        str
            The generated answer with optional source citations.
        """
        raise NotImplementedError

    async def generate_stream(
        self,
        query: str,
        retrieved_results: List[RetrievalResult],
        conversation_history: Optional[List[ChatMessage]] = None,
    ) -> AsyncIterator[str]:
        """Stream generated tokens as they are produced.

        Parameters
        ----------
        query : str
            The user's question.
        retrieved_results : list of RetrievalResult
            Retrieved context.
        conversation_history : list of ChatMessage, optional
            Prior conversation messages.

        Yields
        ------
        str
            Individual tokens or token groups as they are generated.
        """
        raise NotImplementedError
        yield  # Required for async generator type hint

    def build_prompt(
        self,
        query: str,
        retrieved_results: List[RetrievalResult],
    ) -> List[ChatMessage]:
        """Construct the prompt messages from query and context.

        Parameters
        ----------
        query : str
            User's question.
        retrieved_results : list of RetrievalResult
            Retrieved context to include in the prompt.

        Returns
        -------
        list of ChatMessage
            The formatted message list for the LLM.
        """
        raise NotImplementedError

    def format_context(self, results: List[RetrievalResult]) -> str:
        """Format retrieved results into a context string for the prompt.

        Parameters
        ----------
        results : list of RetrievalResult
            Retrieved document chunks.

        Returns
        -------
        str
            Formatted context string with source markers.
        """
        raise NotImplementedError

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self._conversation_history.clear()
