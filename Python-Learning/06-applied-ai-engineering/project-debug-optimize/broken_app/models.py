"""
Pydantic models for request / response validation.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request from a client."""

    user_id: str = Field(..., description="Unique identifier for the user")
    message: str = Field(..., description="The user's message text")

    # BUG (overly permissive): No length constraints on `message`.
    # A caller can send a 500 KB prompt and blow through rate limits /
    # context windows.  There is also no validation on user_id format —
    # empty strings or extremely long IDs are accepted.

    class Config:
        # Allows arbitrary extra fields — anything the caller sends is
        # silently accepted and forwarded, which can cause confusion.
        extra = "allow"


class ChatResponse(BaseModel):
    """Response returned to the client after a chat turn."""

    message: str
    tokens_used: int
    cost_usd: float


class UsageRecord(BaseModel):
    """Single usage entry stored in memory."""

    user_id: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float


class ConversationSummary(BaseModel):
    """Optional summary of a conversation (currently unused)."""

    user_id: str
    turn_count: int
    total_tokens: int
    summary_text: Optional[str] = None
