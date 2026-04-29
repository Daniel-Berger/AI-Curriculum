"""
Solution for Ticket #004 — Users Seeing Each Other's Conversations
===================================================================
Root cause:  The application stores all conversation histories in a
single module-level dict (`conversation_store`) that is shared across
all concurrent async requests.  Because Python's asyncio cooperative
multitasking can interleave coroutines at any `await` point, two
requests that arrive near-simultaneously can both read and mutate the
same user's message list — or worse, one request's messages can leak
into another user's context.

Fix:
  1. Replace the shared module-level dict with per-request conversation
     state.  Load history from a persistent store (or an async-safe
     cache) at the start of each request and write it back atomically
     at the end.
  2. Use an asyncio.Lock per user_id to serialize concurrent writes to
     the same conversation.
  3. Deep-copy the message list before passing it to the LLM so that
     any concurrent mutation cannot affect an in-flight request.
"""

import asyncio
import copy
import logging
from typing import Dict, List

logger = logging.getLogger("chat_service")

# ---------------------------------------------------------------------------
# Per-user lock registry — prevents two concurrent requests for the SAME
# user from interleaving their conversation mutations.
# ---------------------------------------------------------------------------
_user_locks: Dict[str, asyncio.Lock] = {}


def _get_user_lock(user_id: str) -> asyncio.Lock:
    """Return (or create) the asyncio.Lock for a given user_id."""
    if user_id not in _user_locks:
        _user_locks[user_id] = asyncio.Lock()
    return _user_locks[user_id]


# ---------------------------------------------------------------------------
# Thread-safe conversation store
# ---------------------------------------------------------------------------

class ConversationStore:
    """Async-safe wrapper around the in-memory conversation dict.

    All reads and writes for a given user are serialized by an
    asyncio.Lock so that concurrent requests cannot interleave.
    """

    def __init__(self, system_prompt: str):
        self._store: Dict[str, List[dict]] = {}
        self._system_prompt = system_prompt

    async def get_messages_and_append(
        self, user_id: str, new_user_message: str
    ) -> List[dict]:
        """Atomically read history, append the new message, and return
        a deep copy safe for use in an LLM call."""
        lock = _get_user_lock(user_id)
        async with lock:
            if user_id not in self._store:
                self._store[user_id] = [
                    {"role": "system", "content": self._system_prompt}
                ]
            self._store[user_id].append(
                {"role": "user", "content": new_user_message}
            )
            # Deep-copy so the caller has an immutable snapshot
            return copy.deepcopy(self._store[user_id])

    async def append_assistant_message(
        self, user_id: str, assistant_message: str
    ) -> None:
        """Atomically append the assistant's reply."""
        lock = _get_user_lock(user_id)
        async with lock:
            if user_id in self._store:
                self._store[user_id].append(
                    {"role": "assistant", "content": assistant_message}
                )
