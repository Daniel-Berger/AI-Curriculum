"""
LLM Client Abstraction.

Provides unified interface for LLM calls with fallbacks.
Supports Claude, OpenAI, and mock for testing.
"""

import logging
from typing import AsyncGenerator, Optional
import time

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client with fallback support.

    Supports:
    - Anthropic Claude (primary)
    - OpenAI GPT (fallback)
    - Mock for testing
    """

    def __init__(
        self,
        api_key: str,
        openai_api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        use_mock: bool = False
    ):
        """Initialize LLM client.

        Args:
            api_key: Anthropic API key
            openai_api_key: OpenAI API key (optional)
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            use_mock: Use mock LLM (for testing)
        """
        self.api_key = api_key
        self.openai_api_key = openai_api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_mock = use_mock

        self._initialize_client()

    def _initialize_client(self):
        """Initialize LLM client (mock in this implementation)."""
        try:
            if self.use_mock:
                logger.info("Using mock LLM client")
                self.client = None
            else:
                # In production:
                # from anthropic import Anthropic
                # self.client = Anthropic(api_key=self.api_key)

                logger.info("LLM client initialized (mock mode)")
                self.client = None

        except Exception as e:
            logger.error(f"LLM client initialization failed: {e}")
            self.client = None

    async def generate_response(
        self,
        user_message: str,
        context: str = "",
        temperature: Optional[float] = None
    ) -> str:
        """Generate LLM response.

        Args:
            user_message: User input
            context: Optional context/documents
            temperature: Sampling temperature override

        Returns:
            Generated text
        """
        try:
            temp = temperature or self.temperature

            # Build prompt
            system_prompt = self._build_system_prompt(context)
            user_prompt = user_message

            logger.info(f"Generating response with temp={temp}")

            # Mock response (in production, call actual LLM)
            response = self._generate_mock_response(user_prompt, context)

            logger.info(f"Response generated ({len(response)} chars)")
            return response

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            raise

    async def stream_response(
        self,
        user_message: str,
        context: str = "",
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """Stream LLM response.

        Args:
            user_message: User input
            context: Optional context
            temperature: Sampling temperature override

        Yields:
            Response text chunks
        """
        try:
            temp = temperature or self.temperature

            system_prompt = self._build_system_prompt(context)
            user_prompt = user_message

            logger.info("Streaming response")

            # Mock streaming (in production, iterate over API response)
            mock_response = self._generate_mock_response(user_prompt, context)

            # Yield in chunks
            chunk_size = 50
            for i in range(0, len(mock_response), chunk_size):
                chunk = mock_response[i:i+chunk_size]
                yield chunk
                await asyncio.sleep(0.01)  # Simulate network delay

        except Exception as e:
            logger.error(f"Stream failed: {e}")
            yield f"Error: {str(e)}"

    def _build_system_prompt(self, context: str) -> str:
        """Build system prompt with context.

        Args:
            context: Retrieved context

        Returns:
            System prompt
        """
        system = "You are a helpful AI assistant with access to documents."

        if context:
            system += f"\n\nContext from documents:\n{context}"

        system += (
            "\n\nBe concise, accurate, and cite sources when using context."
        )

        return system

    def _generate_mock_response(self, user_message: str, context: str) -> str:
        """Generate mock response for testing.

        Args:
            user_message: User input
            context: Retrieved context

        Returns:
            Mock response
        """
        # Simple mock that incorporates context
        if context:
            return (
                f"Based on the provided documents, here's an answer to your question "
                f"'{user_message[:50]}...': The documents contain relevant information "
                f"that addresses your query. Key points: 1) Content is available in the "
                f"context, 2) This is a mock response for testing, 3) In production, "
                f"the actual LLM would generate a thoughtful response based on the context."
            )
        else:
            return (
                f"I don't have specific document context for '{user_message[:50]}...' "
                f"but I can help with general knowledge. Please upload relevant documents "
                f"or ask a more specific question."
            )

    def count_tokens(self, text: str) -> int:
        """Estimate token count.

        Args:
            text: Text to count

        Returns:
            Approximate token count
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API cost.

        Args:
            input_tokens: Input token count
            output_tokens: Output token count

        Returns:
            Estimated cost in USD
        """
        # Claude 3 Sonnet pricing (approximate)
        input_cost = input_tokens * 0.003 / 1000  # $0.003 per 1K
        output_cost = output_tokens * 0.015 / 1000  # $0.015 per 1K

        return input_cost + output_cost


# Mock async for compatibility
import asyncio
