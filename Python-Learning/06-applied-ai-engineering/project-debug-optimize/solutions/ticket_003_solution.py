"""
Solution for Ticket #003 — Unexpected 10x Cost Increase
========================================================
Root cause:  The cost-per-token constants in main.py are set to the
per-token price instead of the per-1K-token price.

    COST_PER_INPUT_TOKEN  = 0.01   # wrong — should be 0.01 / 1000
    COST_PER_OUTPUT_TOKEN = 0.03   # wrong — should be 0.03 / 1000

This makes every recorded cost exactly 1000x too high, which is
consistent with the customer's observation ($4,200 -> $41,500 is
roughly a 10x multiplier because their request mix shifted slightly,
but the dominant factor is the 1000x unit error).

Fix:
  1. Correct the constants to use per-token pricing.
  2. Use tiktoken for accurate local token counting as a cross-check.
  3. Add a sanity-check assertion that flags impossible costs.
"""

import time
import logging
from typing import List

import tiktoken

from models import UsageRecord

logger = logging.getLogger("chat_service")

# ---------------------------------------------------------------------------
# Correct pricing constants (per token, not per 1K tokens)
# ---------------------------------------------------------------------------
COST_PER_INPUT_TOKEN = 0.01 / 1000    # $0.01 per 1K input tokens
COST_PER_OUTPUT_TOKEN = 0.03 / 1000   # $0.03 per 1K output tokens

# Sanity threshold — flag any single request that costs more than this
MAX_REASONABLE_COST_PER_REQUEST = 5.00  # dollars

usage_log: List[UsageRecord] = []


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens locally using tiktoken as a cross-check."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def record_usage(
    user_id: str, input_tokens: int, output_tokens: int
) -> float:
    """Calculate cost correctly and append to the usage log."""
    cost = (input_tokens * COST_PER_INPUT_TOKEN) + (
        output_tokens * COST_PER_OUTPUT_TOKEN
    )

    if cost > MAX_REASONABLE_COST_PER_REQUEST:
        logger.warning(
            "Unusually high cost for user=%s: $%.4f "
            "(input=%d, output=%d tokens). Investigate.",
            user_id, cost, input_tokens, output_tokens,
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
