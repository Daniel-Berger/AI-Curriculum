"""
Solution for Ticket #005 — Significant Response Quality Degradation
====================================================================
Root cause:  Conversation history is never truncated.  As conversations
grow beyond 8-10 turns, the accumulated tokens approach (and eventually
exceed) the model's context window.  The API silently truncates from
the beginning, which drops the system prompt and early conversation
context.  The model then produces generic, ungrounded responses.

Fix:
  1. Track the token count of the conversation and enforce a budget.
  2. When the conversation exceeds the budget, summarize the oldest
     messages and replace them with a compact summary, preserving the
     system prompt and most recent turns.
  3. This keeps total tokens under the context limit while retaining
     the information the model needs to give high-quality answers.
"""

import logging
from typing import List

import tiktoken

logger = logging.getLogger("chat_service")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MAX_CONTEXT_TOKENS = 6000       # leave headroom below the model's limit
RECENT_TURNS_TO_KEEP = 6        # always keep the last N messages verbatim
SUMMARY_MODEL = "gpt-4o"


def count_message_tokens(messages: List[dict], model: str = "gpt-4o") -> int:
    """Estimate the token count of a message list using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    token_count = 0
    for msg in messages:
        # Every message has role + content + overhead (~4 tokens)
        token_count += 4
        token_count += len(encoding.encode(msg.get("content", "")))
    token_count += 2  # reply priming
    return token_count


async def summarize_messages(
    client, messages: List[dict], model: str = SUMMARY_MODEL
) -> str:
    """Ask the LLM to produce a concise summary of a message sequence."""
    combined = "\n".join(
        f"{m['role']}: {m['content']}" for m in messages
    )
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Summarize the following conversation excerpt in 2-3 "
                    "sentences.  Preserve all key facts, decisions, and "
                    "context that would be needed to continue the conversation."
                ),
            },
            {"role": "user", "content": combined},
        ],
        temperature=0.3,
        max_tokens=300,
    )
    return response.choices[0].message.content


async def manage_context_window(
    client, messages: List[dict], model: str = "gpt-4o"
) -> List[dict]:
    """Trim and summarize messages to fit within the context budget.

    Returns a new message list that:
      - Starts with the original system prompt.
      - Includes a summary of older turns (if any were trimmed).
      - Ends with the most recent RECENT_TURNS_TO_KEEP messages.
    """
    token_count = count_message_tokens(messages, model)

    if token_count <= MAX_CONTEXT_TOKENS:
        return messages  # no trimming needed

    logger.info(
        "Context window at %d tokens (limit %d). Summarizing older turns.",
        token_count, MAX_CONTEXT_TOKENS,
    )

    # Separate system prompt from conversation turns
    system_msg = messages[0] if messages[0]["role"] == "system" else None
    conversation = messages[1:] if system_msg else messages

    # Keep the most recent turns verbatim
    recent = conversation[-RECENT_TURNS_TO_KEEP:]
    older = conversation[:-RECENT_TURNS_TO_KEEP]

    if not older:
        return messages  # nothing to summarize

    summary_text = await summarize_messages(client, older)

    # Rebuild the message list
    trimmed: List[dict] = []
    if system_msg:
        trimmed.append(system_msg)
    trimmed.append({
        "role": "system",
        "content": f"[Summary of earlier conversation]\n{summary_text}",
    })
    trimmed.extend(recent)

    new_count = count_message_tokens(trimmed, model)
    logger.info("Trimmed context from %d to %d tokens.", token_count, new_count)

    return trimmed
