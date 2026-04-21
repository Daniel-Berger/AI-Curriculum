"""
Pydantic models for request/response validation.

Type-safe API contract.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================================================
# Chat Models
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request from user."""

    message: str = Field(
        ...,
        description="User message or question",
        min_length=1,
        max_length=10000
    )
    chat_id: str = Field(
        ...,
        description="Unique conversation identifier",
        min_length=1,
        max_length=100
    )
    temperature: float = Field(
        default=0.7,
        description="Sampling temperature (0.0=deterministic, 1.0=creative)",
        ge=0.0,
        le=1.0
    )

    @validator('message')
    def message_not_empty(cls, v):
        """Ensure message is not just whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatResponse(BaseModel):
    """Chat response to user."""

    message: str = Field(
        description="LLM-generated response"
    )
    sources: List[Dict[str, str]] = Field(
        default=[],
        description="Source documents used for retrieval"
    )
    tokens_used: int = Field(
        default=0,
        description="Number of tokens consumed"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


# ============================================================================
# Document Models
# ============================================================================

class DocumentUpload(BaseModel):
    """Document upload request."""

    name: str = Field(
        ...,
        description="Document name or title",
        min_length=1,
        max_length=200
    )
    content: str = Field(
        ...,
        description="Document content (text)",
        min_length=1,
        max_length=1000000  # ~1MB text
    )


class Document(BaseModel):
    """Document metadata."""

    id: str = Field(
        description="Unique document identifier"
    )
    name: str = Field(
        description="Document name"
    )
    chunks: int = Field(
        description="Number of text chunks"
    )
    indexed_at: datetime = Field(
        description="When document was indexed"
    )


# ============================================================================
# Health & Monitoring Models
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(
        description="Overall status: healthy, degraded, unhealthy"
    )
    services: Dict[str, str] = Field(
        default={},
        description="Status of individual services"
    )


class MetricsResponse(BaseModel):
    """System metrics response."""

    total_requests: int = Field(
        description="Total chat requests processed"
    )
    total_tokens_used: int = Field(
        description="Total tokens consumed across all requests"
    )
    avg_response_time_ms: float = Field(
        description="Average response time in milliseconds"
    )
    errors: int = Field(
        description="Total errors encountered"
    )
    documents_indexed: int = Field(
        description="Total documents successfully indexed"
    )


# ============================================================================
# Internal Models (not exposed via API)
# ============================================================================

class ChunkMetadata(BaseModel):
    """Metadata for a text chunk."""

    document_id: str
    chunk_index: int
    start_char: int
    end_char: int
    content: str


class RetrievalResult(BaseModel):
    """Result from vector retrieval."""

    content: str
    document_id: str
    score: float  # Similarity score (0-1)
    chunk_index: int


class AgentToolCall(BaseModel):
    """Tool call decision by agent."""

    tool_name: str
    tool_input: Dict[str, Any]
    thought: str  # Agent reasoning
