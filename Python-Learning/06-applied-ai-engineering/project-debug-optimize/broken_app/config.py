"""
Application configuration.
Loaded once at import time and used throughout the service.
"""

import os
import logging

from pydantic_settings import BaseSettings

logger = logging.getLogger("chat_service.config")


class Settings(BaseSettings):
    """Central configuration object.

    Values are read from environment variables; defaults are provided for
    local development.
    """

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-dev-placeholder")
    MODEL_NAME: str = "gpt-4o"
    TEMPERATURE: float = 0.7
    SYSTEM_PROMPT: str = (
        "You are a helpful enterprise assistant. Answer concisely."
    )
    MAX_RETRIES: int = 3        # NOTE: defined here but never actually used
    REQUEST_TIMEOUT: int = 30   # NOTE: defined here but never actually used

    class Config:
        env_file = ".env"


settings = Settings()

# BUG (security): The API key is written to the log in plaintext every time
# the module is imported.  In production this ends up in log aggregators
# (Datadog, Splunk, CloudWatch) where many people can read it.
logger.info("Loaded configuration: API_KEY=%s MODEL=%s", settings.OPENAI_API_KEY, settings.MODEL_NAME)
