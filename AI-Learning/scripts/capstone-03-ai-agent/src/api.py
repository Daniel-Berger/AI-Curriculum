"""
FastAPI Application for the AI Agent
=====================================

REST API for interacting with the AI agent. Provides endpoints for
chat interaction, conversation management, tool listing, and execution
trace retrieval.

Endpoints:
- POST /agent/chat           -- Send a message and get a response
- POST /agent/chat/stream    -- Send a message with streaming response
- GET  /agent/conversations  -- List active conversations
- GET  /agent/conversations/{id}/trace -- Get execution trace
- POST /agent/approve        -- Approve/reject HITL requests
- GET  /agent/tools          -- List available tools
- GET  /health               -- Health check
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    """Request body for the /agent/chat endpoint."""

    message: str = Field(..., description="The user's message to the agent")
    conversation_id: Optional[str] = Field(
        default=None, description="Conversation ID for continuity"
    )


class ChatResponse(BaseModel):
    """Response body for the /agent/chat endpoint."""

    response: str
    conversation_id: str
    tools_used: List[str] = []
    iterations: int = 0
    execution_time_ms: float = 0.0


class ApprovalRequest(BaseModel):
    """Request to approve or reject a HITL tool call."""

    conversation_id: str
    tool_name: str
    approved: bool
    reason: Optional[str] = None


class ToolInfo(BaseModel):
    """Information about an available tool."""

    name: str
    description: str
    parameters: Dict[str, Any] = {}
    requires_approval: bool = False


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    active_conversations: int = 0


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Agent API",
    description="Production AI agent with LangGraph, tools, and HITL support.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check agent system health."""
    raise NotImplementedError


@app.post("/agent/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message to the agent and receive a response.

    The agent will plan, execute tools as needed, and generate
    a response. Supports multi-turn conversations via conversation_id.
    """
    raise NotImplementedError


@app.post("/agent/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Send a message and receive a streaming response via SSE."""
    raise NotImplementedError


@app.websocket("/agent/ws/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket, conversation_id: str
) -> None:
    """WebSocket endpoint for real-time agent interaction.

    Supports bidirectional communication including HITL approval
    prompts sent to the client.
    """
    raise NotImplementedError


@app.get("/agent/tools", response_model=List[ToolInfo])
async def list_tools() -> List[ToolInfo]:
    """List all tools available to the agent."""
    raise NotImplementedError


@app.post("/agent/approve")
async def approve_tool_call(request: ApprovalRequest) -> Dict[str, str]:
    """Approve or reject a pending HITL tool call."""
    raise NotImplementedError


@app.get("/agent/conversations")
async def list_conversations() -> List[Dict[str, Any]]:
    """List all active conversations."""
    raise NotImplementedError


@app.get("/agent/conversations/{conversation_id}/trace")
async def get_execution_trace(
    conversation_id: str,
) -> List[Dict[str, Any]]:
    """Retrieve the execution trace for a conversation.

    Returns the step-by-step execution history including planning,
    tool calls, observations, and timing information.
    """
    raise NotImplementedError
