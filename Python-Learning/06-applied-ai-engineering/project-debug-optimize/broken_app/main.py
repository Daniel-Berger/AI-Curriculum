"""
AI Chat Service - Production Application
=========================================
FastAPI wrapper around an LLM API that provides multi-turn chat for
enterprise customers.  Each customer has a user_id and maintains a
running conversation history.

NOTE: This file contains DELIBERATE bugs for the Debug & Optimize
challenge.  Do not deploy this code.
"""

import time
import logging
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI

from config import settings
from models import ChatRequest, ChatResponse, UsageRecord

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------
app = FastAPI(title="AI Chat Service", version="1.2.0")
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger("chat_service")
logging.basicConfig(level=logging.DEBUG)

# ---------------------------------------------------------------------------
# In-memory stores (shared across all requests)
# ---------------------------------------------------------------------------

# BUG 4 (race condition): A single mutable dict is shared across all async
# requests with no locking.  Under concurrency two requests that arrive
# close together can read/write the same list, causing users to see each
# other's messages.
conversation_store: Dict[str, List[dict]] = {}

# BUG 5 (cost tracking): token-to-dollar multiplier is wrong — it uses the
# per-token price instead of the per-1K-token price, inflating costs by 1000x
# in the dashboard but UNDER-counting when the billing report divides back.
COST_PER_INPUT_TOKEN = 0.01    # BUG: should be 0.01 / 1000
COST_PER_OUTPUT_TOKEN = 0.03   # BUG: should be 0.03 / 1000

usage_log: List[UsageRecord] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_messages(user_id: str, new_message: str) -> List[dict]:
    """Return the full message list for the OpenAI call."""
    # BUG 3 (memory leak / quality drop): conversation history is NEVER
    # truncated.  Over days of use the list grows without bound, eventually
    # exceeding the context window and causing the model to lose track of
    # the recent conversation — quality degrades.
    if user_id not in conversation_store:
        conversation_store[user_id] = [
            {"role": "system", "content": settings.SYSTEM_PROMPT}
        ]
    conversation_store[user_id].append(
        {"role": "user", "content": new_message}
    )
    return conversation_store[user_id]


def record_usage(user_id: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost and append to the usage log."""
    # BUG 5 continued: the multiplication is done with the wrong constants
    cost = (input_tokens * COST_PER_INPUT_TOKEN) + (
        output_tokens * COST_PER_OUTPUT_TOKEN
    )
    usage_log.append(
        UsageRecord(
            user_id=user_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            timestamp=time.time(),
        )
    )
    return cost


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle a chat turn.

    Accepts a user message, appends it to the conversation, calls the LLM,
    and returns the assistant reply.
    """

    # BUG 1 (PII leak): The raw user message — which may contain SSNs,
    # credit card numbers, or other PII — is logged at DEBUG level and
    # sent directly to the LLM with no redaction.
    logger.debug(
        "Incoming request from user=%s message=%s", request.user_id, request.message
    )

    messages = build_messages(request.user_id, request.message)

    # BUG 2 (no retry / timeout): A single API call with no retry logic,
    # no timeout, and no streaming.  If the upstream LLM is slow or
    # throws a transient 500/429 the request simply crashes.
    try:
        response = await client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            temperature=settings.TEMPERATURE,
        )
    except Exception as exc:
        # BUG 2 continued: generic catch that surfaces raw error to caller
        raise HTTPException(status_code=500, detail=str(exc))

    assistant_msg = response.choices[0].message.content

    # Store assistant reply back into shared history (race condition window)
    conversation_store[request.user_id].append(
        {"role": "assistant", "content": assistant_msg}
    )

    # Log the full response including any PII that was echoed back
    logger.debug("Response to user=%s: %s", request.user_id, assistant_msg)

    cost = record_usage(
        request.user_id,
        response.usage.prompt_tokens,
        response.usage.completion_tokens,
    )

    return ChatResponse(
        message=assistant_msg,
        tokens_used=response.usage.total_tokens,
        cost_usd=cost,
    )


@app.get("/usage/{user_id}")
async def get_usage(user_id: str):
    """Return usage records for a given user."""
    records = [r for r in usage_log if r.user_id == user_id]
    total_cost = sum(r.cost_usd for r in records)
    return {
        "user_id": user_id,
        "total_records": len(records),
        "total_cost_usd": total_cost,
        "records": records,
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "active_conversations": len(conversation_store),
        "total_usage_records": len(usage_log),
    }
