"""
Test suite for the Debug & Optimize Challenge.
==============================================
Each test class covers one ticket's fix.  Tests are designed to run
WITHOUT a live OpenAI API key — they mock external calls and focus on
verifying the logic of each fix.

Run:
    cd project-debug-optimize
    python -m pytest tests/test_fixes.py -v
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Ticket #001 — Retry / timeout logic
# ---------------------------------------------------------------------------

class TestTicket001Retry:
    """Verify that the retry wrapper retries transient errors and respects
    the maximum attempt count."""

    @pytest.mark.asyncio
    async def test_retry_on_transient_error(self):
        from solutions.ticket_001_solution import chat_with_retry
        from openai import APITimeoutError

        mock_client = AsyncMock()

        # First call raises timeout, second call succeeds
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock(delta=MagicMock(content="hello"))]

        mock_stream = AsyncMock()
        mock_stream.__aiter__ = MagicMock(return_value=iter([mock_chunk]))

        mock_client.chat.completions.create = AsyncMock(
            side_effect=[
                APITimeoutError(request=MagicMock()),
                mock_stream,
            ]
        )

        tokens = []
        async for token in chat_with_retry(
            mock_client, [{"role": "user", "content": "hi"}], "gpt-4o", 0.7
        ):
            tokens.append(token)

        assert mock_client.chat.completions.create.call_count == 2

    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self):
        from solutions.ticket_001_solution import chat_with_retry
        from openai import APITimeoutError
        from fastapi import HTTPException

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=APITimeoutError(request=MagicMock())
        )

        with pytest.raises(HTTPException) as exc_info:
            async for _ in chat_with_retry(
                mock_client, [{"role": "user", "content": "hi"}], "gpt-4o", 0.7
            ):
                pass

        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# Ticket #002 — PII redaction
# ---------------------------------------------------------------------------

class TestTicket002PIIRedaction:
    """Verify that PII patterns are correctly redacted."""

    def test_ssn_redacted(self):
        from solutions.ticket_002_solution import redact_pii
        text = "Patient SSN: 123-45-6789 and more text"
        result = redact_pii(text)
        assert "123-45-6789" not in result
        assert "[REDACTED_SSN]" in result

    def test_email_redacted(self):
        from solutions.ticket_002_solution import redact_pii
        text = "Contact me at jane.doe@example.com please"
        result = redact_pii(text)
        assert "jane.doe@example.com" not in result
        assert "[REDACTED_EMAIL]" in result

    def test_non_pii_preserved(self):
        from solutions.ticket_002_solution import redact_pii
        text = "The weather today is sunny and 72 degrees."
        result = redact_pii(text)
        assert result == text

    def test_mask_secret(self):
        from solutions.ticket_002_solution import mask_secret
        key = "sk-abc123xyz789"
        masked = mask_secret(key)
        assert masked.endswith("z789")
        assert "sk-abc" not in masked

    def test_multiple_pii_types(self):
        from solutions.ticket_002_solution import redact_pii
        text = "SSN: 111-22-3333, email: a@b.com, phone: (555) 123-4567"
        result = redact_pii(text)
        assert "111-22-3333" not in result
        assert "a@b.com" not in result


# ---------------------------------------------------------------------------
# Ticket #003 — Cost calculation
# ---------------------------------------------------------------------------

class TestTicket003CostCalculation:
    """Verify that token costs are calculated correctly."""

    def test_cost_uses_per_1k_pricing(self):
        from solutions.ticket_003_solution import record_usage, usage_log
        usage_log.clear()

        cost = record_usage("test_user", input_tokens=1000, output_tokens=500)

        # Expected: (1000 * 0.01/1000) + (500 * 0.03/1000) = 0.01 + 0.015 = 0.025
        assert abs(cost - 0.025) < 1e-9

    def test_small_request_cost(self):
        from solutions.ticket_003_solution import record_usage, usage_log
        usage_log.clear()

        cost = record_usage("test_user", input_tokens=350, output_tokens=150)

        # Expected: (350 * 0.00001) + (150 * 0.00003) = 0.0035 + 0.0045 = 0.008
        assert abs(cost - 0.008) < 1e-9

    def test_cost_not_inflated_1000x(self):
        from solutions.ticket_003_solution import record_usage, usage_log
        usage_log.clear()

        cost = record_usage("test_user", input_tokens=500, output_tokens=200)

        # With the bug, this would be (500*0.01)+(200*0.03) = 5+6 = 11.0
        # With the fix, it should be 0.011
        assert cost < 1.0, f"Cost {cost} is suspiciously high — bug still present?"

    def test_usage_record_appended(self):
        from solutions.ticket_003_solution import record_usage, usage_log
        usage_log.clear()

        record_usage("user_a", 100, 50)
        record_usage("user_b", 200, 100)

        assert len(usage_log) == 2
        assert usage_log[0].user_id == "user_a"
        assert usage_log[1].user_id == "user_b"


# ---------------------------------------------------------------------------
# Ticket #004 — Race condition / conversation isolation
# ---------------------------------------------------------------------------

class TestTicket004ConversationIsolation:
    """Verify that concurrent requests for different users do not
    cross-contaminate conversation histories."""

    @pytest.mark.asyncio
    async def test_parallel_users_isolated(self):
        from solutions.ticket_004_solution import ConversationStore

        store = ConversationStore(system_prompt="You are helpful.")

        # Simulate two users hitting the endpoint concurrently
        msgs_a = await store.get_messages_and_append("user_a", "Hello from A")
        msgs_b = await store.get_messages_and_append("user_b", "Hello from B")

        # Each should only see their own message
        a_contents = [m["content"] for m in msgs_a]
        b_contents = [m["content"] for m in msgs_b]

        assert "Hello from A" in a_contents
        assert "Hello from B" not in a_contents
        assert "Hello from B" in b_contents
        assert "Hello from A" not in b_contents

    @pytest.mark.asyncio
    async def test_deep_copy_prevents_mutation(self):
        from solutions.ticket_004_solution import ConversationStore

        store = ConversationStore(system_prompt="System")

        msgs = await store.get_messages_and_append("user_x", "original")
        # Mutate the returned list — this should NOT affect the store
        msgs.append({"role": "user", "content": "injected"})

        msgs2 = await store.get_messages_and_append("user_x", "second")
        contents = [m["content"] for m in msgs2]

        assert "injected" not in contents

    @pytest.mark.asyncio
    async def test_assistant_message_appended(self):
        from solutions.ticket_004_solution import ConversationStore

        store = ConversationStore(system_prompt="System")
        await store.get_messages_and_append("user_z", "Hi")
        await store.append_assistant_message("user_z", "Hello!")

        msgs = await store.get_messages_and_append("user_z", "Follow up")
        roles = [m["role"] for m in msgs]
        assert "assistant" in roles


# ---------------------------------------------------------------------------
# Ticket #005 — Context window management
# ---------------------------------------------------------------------------

class TestTicket005ContextManagement:
    """Verify that long conversations are summarized to stay within the
    context budget."""

    def test_count_message_tokens(self):
        from solutions.ticket_005_solution import count_message_tokens

        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello, how are you?"},
        ]
        token_count = count_message_tokens(messages)
        # Should be a small positive number
        assert 10 < token_count < 50

    @pytest.mark.asyncio
    async def test_short_conversation_not_trimmed(self):
        from solutions.ticket_005_solution import manage_context_window

        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]

        mock_client = AsyncMock()
        result = await manage_context_window(mock_client, messages)

        # Short conversation should be returned unchanged
        assert result == messages
        mock_client.chat.completions.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_long_conversation_triggers_summarization(self):
        from solutions.ticket_005_solution import (
            manage_context_window,
            MAX_CONTEXT_TOKENS,
        )

        # Build a conversation that exceeds the token budget
        messages = [{"role": "system", "content": "You are helpful."}]
        for i in range(40):
            messages.append({"role": "user", "content": f"Question {i}: " + "word " * 100})
            messages.append({"role": "assistant", "content": f"Answer {i}: " + "word " * 100})

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Summary of earlier conversation."))]

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await manage_context_window(mock_client, messages)

        # Result should be shorter than the input
        assert len(result) < len(messages)
        # System prompt should still be first
        assert result[0]["role"] == "system"
        assert result[0]["content"] == "You are helpful."
