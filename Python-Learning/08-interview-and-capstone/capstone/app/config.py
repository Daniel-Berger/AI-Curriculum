"""
Configuration management using Pydantic Settings.

Reads from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # API Keys
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None

    # ChromaDB Configuration
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION_NAME: str = "documents"

    # Embedding Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Small, fast, open-source

    # RAG Configuration
    CHUNK_SIZE: int = 500  # Characters per chunk
    CHUNK_OVERLAP: int = 100  # Overlap between chunks
    TOP_K_RETRIEVAL: int = 3  # Number of chunks to retrieve

    # LLM Configuration
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1024
    LLM_MODEL: str = "claude-3-sonnet-20240229"

    # Agent Configuration
    AGENT_MAX_ITERATIONS: int = 10
    AGENT_TIMEOUT_SECONDS: int = 60

    # Application Configuration
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
