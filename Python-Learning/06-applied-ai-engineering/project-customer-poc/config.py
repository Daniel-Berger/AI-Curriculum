"""Application configuration using Pydantic Settings.

Loads API keys from environment variables, defines per-provider model
configurations, token-cost tables, PII regex patterns, and general app
settings.
"""

from __future__ import annotations

import re
from typing import Dict, List

from pydantic import Field
from pydantic_settings import BaseSettings


class ModelConfig:
    """Per-model metadata used by providers and cost tracking."""

    def __init__(self, name: str, display_name: str, cost_per_input_token: float, cost_per_output_token: float) -> None:
        self.name = name
        self.display_name = display_name
        self.cost_per_input_token = cost_per_input_token
        self.cost_per_output_token = cost_per_output_token


# -- Provider model catalogues ------------------------------------------------

PROVIDER_MODELS: Dict[str, List[ModelConfig]] = {
    "anthropic": [
        ModelConfig("claude-sonnet-4-20250514", "Claude Sonnet 4", 3.0e-6, 15.0e-6),
        ModelConfig("claude-haiku-4-20250414", "Claude Haiku 4", 0.80e-6, 4.0e-6),
    ],
    "openai": [
        ModelConfig("gpt-4o", "GPT-4o", 2.5e-6, 10.0e-6),
        ModelConfig("gpt-4o-mini", "GPT-4o Mini", 0.15e-6, 0.60e-6),
    ],
    "google": [
        ModelConfig("gemini-2.0-flash", "Gemini 2.0 Flash", 0.10e-6, 0.40e-6),
    ],
    "demo": [
        ModelConfig("mock-model", "Demo Model (no API key)", 0.0, 0.0),
    ],
}

# -- PII detection patterns ----------------------------------------------------

PII_PATTERNS: Dict[str, re.Pattern[str]] = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
}


class AppSettings(BaseSettings):
    """Top-level application settings, populated from environment variables."""

    # API keys -- optional; app falls back to demo mode when absent.
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")

    # App display
    app_title: str = "Customer POC Builder"
    app_icon: str = "🔧"

    # Budget
    session_budget_usd: float = 1.00

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
