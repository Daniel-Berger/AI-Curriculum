"""Configuration for the RAG pipeline.

Uses Pydantic Settings to load configuration from environment variables
and provide sensible defaults. This pattern is common in production
Python applications -- similar to how iOS apps use Info.plist or
xcconfig files for build-time configuration.

Swift parallel:
    - Pydantic Settings  ~  @AppStorage / UserDefaults with validation
    - Environment loading ~  ProcessInfo.processInfo.environment
    - Field validators    ~  Property wrappers with didSet validation

Usage:
    # Load defaults:
    config = RAGConfig()

    # Override via environment:
    export CHUNK_SIZE=1000
    export TOP_K=5
    config = RAGConfig()  # picks up env vars automatically

    # Override directly:
    config = RAGConfig(chunk_size=1000, top_k=5)
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class RAGConfig(BaseSettings):
    """Configuration for the RAG pipeline.

    All fields can be overridden via environment variables.
    Pydantic Settings automatically reads from the environment,
    converting UPPER_CASE env vars to snake_case field names.
    """

    # -- Chunking settings --------------------------------------------------
    chunk_size: int = Field(
        default=500,
        ge=100,
        le=10_000,
        description="Maximum number of characters per chunk.",
    )
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=500,
        description="Number of overlapping characters between consecutive chunks.",
    )

    # -- Retrieval settings -------------------------------------------------
    top_k: int = Field(
        default=3,
        ge=1,
        le=50,
        description="Number of top-matching chunks to retrieve.",
    )

    # -- Embedding settings -------------------------------------------------
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Name of the sentence-transformers model for embeddings.",
    )
    embedding_dimension: int = Field(
        default=384,
        ge=1,
        description="Dimensionality of embedding vectors.",
    )

    # -- LLM settings -------------------------------------------------------
    llm_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Model identifier for the LLM provider.",
    )
    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for LLM generation.",
    )
    llm_max_tokens: int = Field(
        default=1024,
        ge=1,
        le=100_000,
        description="Maximum tokens in the LLM response.",
    )

    # -- Vector store settings ----------------------------------------------
    collection_name: str = Field(
        default="rag_documents",
        description="ChromaDB collection name.",
    )
    persist_directory: str = Field(
        default=".chromadb",
        description="Directory to persist ChromaDB data.",
    )

    model_config = {
        "env_prefix": "",
        "case_sensitive": False,
        "extra": "ignore",
    }


class LLMProviderConfig(BaseSettings):
    """API key configuration for LLM providers.

    API keys should NEVER be hardcoded. Load them from environment
    variables or a .env file.

    Swift parallel: Similar to using Keychain Services for secrets,
    except here we use environment variables (the standard approach
    in server-side Python).
    """

    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key for Claude models.",
    )
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key for GPT models.",
    )

    model_config = {
        "env_prefix": "",
        "case_sensitive": False,
        "extra": "ignore",
    }
