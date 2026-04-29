"""
Solution for Ticket #001 — Integration Timeouts on Large Prompts
================================================================
Root cause: The /chat endpoint makes a single blocking (non-streaming)
call to the LLM API with no timeout and no retry logic.  When the
upstream API is slow or returns a transient error (429, 500, 503),
the request hangs until the customer's HTTP client gives up.

Fix:
  1. Enable streaming so partial tokens arrive immediately and the
     customer's HTTP client stays alive.
  2. Set an explicit timeout on the OpenAI client call.
  3. Add exponential-backoff retry for transient failures.
"""

import asyncio
import logging
from typing import AsyncGenerator

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI, APITimeoutError, RateLimitError, APIStatusError

logger = logging.getLogger("chat_service")

# Retry configuration — these match the values already defined (but
# previously unused) in config.py.
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30  # seconds
RETRY_BASE_DELAY = 1.0  # seconds


async def chat_with_retry(
    client: AsyncOpenAI,
    messages: list,
    model: str,
    temperature: float,
) -> AsyncGenerator[str, None]:
    """Stream a chat completion with timeout and exponential-backoff retry."""

    retryable_errors = (APITimeoutError, RateLimitError)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            stream = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True,
                timeout=REQUEST_TIMEOUT,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
            return  # success — exit the retry loop

        except retryable_errors as exc:
            if attempt == MAX_RETRIES:
                logger.error("All %d retry attempts exhausted: %s", MAX_RETRIES, exc)
                raise HTTPException(
                    status_code=503,
                    detail="The upstream model is temporarily unavailable. Please retry.",
                )
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            logger.warning(
                "Attempt %d/%d failed (%s). Retrying in %.1fs...",
                attempt, MAX_RETRIES, type(exc).__name__, delay,
            )
            await asyncio.sleep(delay)

        except APIStatusError as exc:
            # Non-retryable API error — surface a sanitized message
            logger.error("Non-retryable API error: %s", exc)
            raise HTTPException(status_code=502, detail="Upstream API error.")


# ---- Example endpoint using the fix ----

async def fixed_chat_endpoint(request, client, settings, build_messages_fn):
    """Drop-in replacement for the /chat route."""
    messages = build_messages_fn(request.user_id, request.message)

    async def generate():
        async for token in chat_with_retry(
            client, messages, settings.MODEL_NAME, settings.TEMPERATURE,
        ):
            yield token

    return StreamingResponse(generate(), media_type="text/plain")
