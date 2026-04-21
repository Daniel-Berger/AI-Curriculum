"""
Business logic and service layer for ML operations.
"""

import logging
import os
from typing import Optional
from abc import ABC, abstractmethod
from functools import lru_cache

from app.models import PredictionResponse

logger = logging.getLogger(__name__)


class ModelInterface(ABC):
    """Abstract base class for model implementations."""

    @abstractmethod
    async def predict(self, prompt: str, max_tokens: int) -> dict:
        """Generate prediction from prompt."""
        pass

    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        pass


class MockModel(ModelInterface):
    """Mock model for testing without external dependencies."""

    def __init__(self):
        self.loaded = True
        self.name = "mock-model"

    async def predict(self, prompt: str, max_tokens: int) -> dict:
        """Generate mock prediction."""
        # Simulate token counting
        prompt_tokens = len(prompt.split())
        completion_tokens = min(max_tokens, 50)
        total_tokens = prompt_tokens + completion_tokens

        # Generate mock response
        response = f"This is a mock response to: '{prompt[:50]}...'. " * 3

        return {
            "text": response[:completion_tokens * 4],
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }

    def is_loaded(self) -> bool:
        return self.loaded


class OpenAIModel(ModelInterface):
    """OpenAI API model implementation."""

    def __init__(self, api_key: str, model_name: str = "gpt-4"):
        self.api_key = api_key
        self.model_name = model_name
        self.loaded = True

        # In production, initialize OpenAI client here
        # import openai
        # openai.api_key = api_key

    async def predict(self, prompt: str, max_tokens: int) -> dict:
        """Generate prediction using OpenAI API."""
        # In production, call OpenAI API
        # response = openai.ChatCompletion.create(
        #     model=self.model_name,
        #     messages=[{"role": "user", "content": prompt}],
        #     max_tokens=max_tokens,
        #     temperature=0.7
        # )

        # Mock response for demo
        logger.info(f"Would call OpenAI with prompt: {prompt[:50]}...")

        return {
            "text": "OpenAI response would go here",
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": min(max_tokens, 100),
            "total_tokens": len(prompt.split()) + min(max_tokens, 100)
        }

    def is_loaded(self) -> bool:
        return self.loaded


class MLService:
    """Main service for ML operations."""

    def __init__(self, model: ModelInterface):
        self.model = model
        self.model_name = getattr(model, 'name', 'unknown')
        self.request_count = 0
        self.error_count = 0
        self.total_tokens = 0

    async def predict(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> PredictionResponse:
        """
        Generate prediction from prompt.

        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter

        Returns:
            PredictionResponse with generated text

        Raises:
            ValueError: If input is invalid
            RuntimeError: If model inference fails
        """
        # Validate input
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if len(prompt) > 5000:
            raise ValueError("Prompt exceeds maximum length")

        try:
            self.request_count += 1

            logger.info(f"Processing prediction request #{self.request_count}")

            # Get model prediction
            result = await self.model.predict(
                prompt=prompt,
                max_tokens=max_tokens
            )

            # Track tokens
            total_tokens = result.get("total_tokens", 0)
            self.total_tokens += total_tokens

            # Create response
            response = PredictionResponse(
                prediction=result["text"],
                tokens_used=total_tokens,
                model=self.model_name
            )

            logger.info(
                f"Prediction successful: {total_tokens} tokens used"
            )

            return response

        except ValueError as e:
            self.error_count += 1
            logger.warning(f"Validation error: {str(e)}")
            raise

        except Exception as e:
            self.error_count += 1
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            raise RuntimeError(f"Model inference failed: {str(e)}")

    def is_loaded(self) -> bool:
        """Check if model is loaded and ready."""
        return self.model.is_loaded()

    def get_stats(self) -> dict:
        """Get service statistics."""
        return {
            "requests": self.request_count,
            "errors": self.error_count,
            "total_tokens": self.total_tokens,
            "error_rate": (
                self.error_count / self.request_count
                if self.request_count > 0
                else 0
            )
        }


# Global service instance
_ml_service: Optional[MLService] = None


def initialize_service() -> MLService:
    """Initialize ML service with configured model."""
    global _ml_service

    # Get model configuration from environment
    model_type = os.getenv("MODEL_TYPE", "mock").lower()
    api_key = os.getenv("API_KEY", "")
    model_name = os.getenv("MODEL_NAME", "gpt-4")

    logger.info(f"Initializing ML service with model: {model_type}")

    # Create appropriate model
    if model_type == "openai":
        if not api_key:
            raise ValueError("API_KEY not set for OpenAI model")
        model = OpenAIModel(api_key=api_key, model_name=model_name)
    else:
        # Default to mock model
        model = MockModel()

    # Create service
    _ml_service = MLService(model=model)
    logger.info("ML service initialized successfully")

    return _ml_service


async def get_ml_service() -> MLService:
    """Dependency injection for ML service."""
    global _ml_service

    if _ml_service is None:
        _ml_service = initialize_service()

    return _ml_service


@lru_cache(maxsize=1000)
def should_cache_prediction(prompt_hash: int) -> bool:
    """Determine if prediction should be cached."""
    # Simple heuristic: cache if prompt hash is even
    return prompt_hash % 2 == 0
