"""
Module 04: Conversation & Application Design -- Exercises
==========================================================

15 exercises covering conversation management, guardrails, graceful
degradation, human-in-the-loop patterns, and application-level design
for production AI systems.

Target audience: experienced Swift/iOS engineers transitioning to
applied AI engineering roles (solutions engineer / applied AI engineer).

Run this file directly to check your solutions:
    python exercises.py
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


# ---------------------------------------------------------------------------
# Exercise 1: Conversation Message Data Model
# ---------------------------------------------------------------------------
def build_conversation_model() -> list[dict[str, Any]]:
    """
    Build a list of conversation messages following the OpenAI/Anthropic
    message format.

    Create a conversation with the following turns:
      1. system  -- "You are a helpful travel assistant."
      2. user    -- "I want to plan a trip to Tokyo."
      3. assistant -- "I'd love to help you plan a trip to Tokyo! ..."
      4. user    -- "What's the best time to visit?"
      5. assistant -- "The best time to visit Tokyo is ..."

    Each message is a dict with keys:
      - "role": one of "system", "user", "assistant"
      - "content": the message text (use the exact strings above; assistant
        messages can be any reasonable text that starts with the prefix shown)
      - "timestamp": a float (use sequential values starting from 1000.0,
        incrementing by 1.0 for each message)
      - "metadata": a dict that must include the key "token_count" (int).
        Estimate token count as ``len(content.split())``.

    Returns:
        List of 5 message dicts in chronological order.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Sliding Window Context Manager
# ---------------------------------------------------------------------------
def sliding_window_context(
    messages: list[dict[str, str]],
    max_messages: int,
    preserve_system: bool = True,
) -> list[dict[str, str]]:
    """
    Return the most recent messages that fit within *max_messages*.

    Rules:
      - If *preserve_system* is True and the first message has
        role == "system", always keep it as the first element of the
        returned list (it does NOT count toward *max_messages*).
      - From the remaining (non-system) messages, keep only the last
        *max_messages* items.
      - If *max_messages* >= number of non-system messages, return all.

    Args:
        messages: Full conversation history (list of dicts with "role"
                  and "content" keys).
        max_messages: Maximum number of non-system messages to keep.
        preserve_system: Whether to always keep the system message.

    Returns:
        Trimmed list of messages.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Conversation Summarizer
# ---------------------------------------------------------------------------
def summarize_and_truncate(
    messages: list[dict[str, str]],
    max_messages: int,
) -> list[dict[str, str]]:
    """
    When a conversation exceeds *max_messages* (non-system), compress the
    older messages into a single summary message.

    Steps:
      1. Separate out the system message (first msg if role == "system").
      2. If the number of remaining messages <= *max_messages*, return
         the original list unchanged.
      3. Otherwise split the non-system messages into:
         - *old*: messages to summarize (everything except the last
           *max_messages* items)
         - *recent*: the last *max_messages* items
      4. Create a summary message:
         {"role": "system",
          "content": "Summary of earlier conversation:\n" +
                     one-line-per-old-message in the format
                     "{role}: {content}"}
      5. Return: [original_system_msg (if any), summary_msg] + recent

    Args:
        messages: Full conversation history.
        max_messages: How many recent non-system messages to keep verbatim.

    Returns:
        Compressed message list.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Token Budget Allocator
# ---------------------------------------------------------------------------
def allocate_token_budget(
    total_budget: int,
    system_tokens: int,
    history_messages: list[dict[str, str]],
    reserved_for_response: int = 1024,
) -> dict[str, Any]:
    """
    Given a total context-window budget, allocate tokens to each component.

    Token estimation: ``len(content.split())`` for each message's "content".

    Compute:
      - system_used   = system_tokens (given)
      - response_reserved = reserved_for_response (given)
      - available_for_history = total_budget - system_used - response_reserved
      - Walk *history_messages* from most recent to oldest, accumulating
        tokens.  Stop adding messages when the next message would exceed
        available_for_history.

    Return a dict:
      {
        "total_budget": <int>,
        "system_tokens": <int>,
        "response_reserved": <int>,
        "available_for_history": <int>,
        "history_tokens_used": <int>,       # tokens actually used
        "messages_included": <int>,          # how many history msgs fit
        "messages_dropped": <int>,           # how many were dropped
      }
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: System Prompt Template Engine
# ---------------------------------------------------------------------------
def render_system_prompt(
    template: str,
    variables: dict[str, str],
    strict: bool = True,
) -> str:
    """
    Render a system prompt template by replacing ``{{var_name}}``
    placeholders with values from *variables*.

    Rules:
      - Placeholders use double-brace syntax: ``{{var_name}}``.
      - If *strict* is True and a placeholder has no matching key in
        *variables*, raise a ``KeyError`` with the missing variable name.
      - If *strict* is False, leave unmatched placeholders as-is.
      - Extra keys in *variables* that don't appear in the template are
        silently ignored.
      - Whitespace inside braces is stripped: ``{{ var_name }}`` is
        equivalent to ``{{var_name}}``.

    Args:
        template: Template string with ``{{placeholder}}`` markers.
        variables: Mapping of variable names to replacement values.
        strict: Whether to raise on missing variables.

    Returns:
        Rendered prompt string.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Input Guardrails (Content Validation)
# ---------------------------------------------------------------------------
class ContentViolation(Exception):
    """Raised when user input violates content policy."""
    pass


def validate_user_input(
    user_input: str,
    blocked_patterns: list[str] | None = None,
    max_length: int = 5000,
    allow_urls: bool = False,
) -> dict[str, Any]:
    """
    Validate user input against content-policy rules.

    Checks (in order):
      1. Length: if ``len(user_input) > max_length``, return a failure
         result with reason "exceeds_max_length".
      2. Empty: if input is empty or whitespace-only, return failure
         with reason "empty_input".
      3. Blocked patterns: for each pattern in *blocked_patterns*
         (case-insensitive substring match), if found return failure
         with reason "blocked_pattern: <pattern>".
      4. URLs: if *allow_urls* is False and input contains "http://" or
         "https://", return failure with reason "urls_not_allowed".

    Return dict:
      {
        "valid": bool,
        "sanitized_input": str (stripped whitespace) or None if invalid,
        "reason": str or None,       # reason if invalid
        "original_length": int,
      }
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Output Guardrails (Response Filtering)
# ---------------------------------------------------------------------------
def filter_model_response(
    response: str,
    pii_patterns: list[str] | None = None,
    max_length: int = 10000,
    redaction_token: str = "[REDACTED]",
) -> dict[str, Any]:
    """
    Post-process a model response to redact PII and enforce length limits.

    Steps:
      1. For each pattern in *pii_patterns* (case-insensitive), replace
         every occurrence in the response with *redaction_token*.
      2. If the resulting string exceeds *max_length*, truncate it to
         *max_length* characters and append "... [truncated]".
      3. Track how many redactions were made (total across all patterns).

    Return dict:
      {
        "filtered_response": str,
        "redactions_applied": int,
        "was_truncated": bool,
        "original_length": int,
        "final_length": int,
      }
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Graceful Degradation Handler
# ---------------------------------------------------------------------------
class FallbackResponse:
    """Represents a fallback response when the primary model fails."""

    def __init__(self, message: str, source: str, is_fallback: bool = True):
        self.message = message
        self.source = source
        self.is_fallback = is_fallback


def graceful_degradation_handler(
    primary_fn: Callable[[], str],
    fallback_fns: list[Callable[[], str]],
    default_message: str = "I'm sorry, I'm unable to process your request right now.",
) -> FallbackResponse:
    """
    Try *primary_fn* first.  If it raises any exception, try each function
    in *fallback_fns* in order.  If all fail, return *default_message*.

    Return a ``FallbackResponse`` with:
      - message: the string returned by the first successful callable
      - source: "primary" | "fallback_1" | "fallback_2" | ... | "default"
      - is_fallback: False only when the primary succeeded

    Args:
        primary_fn: Primary response generator.
        fallback_fns: Ordered list of fallback generators.
        default_message: Last-resort static message.

    Returns:
        FallbackResponse instance.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Human-in-the-Loop Escalation System
# ---------------------------------------------------------------------------
class EscalationLevel(Enum):
    AUTO = "auto"
    REVIEW = "review"
    ESCALATE = "escalate"


def evaluate_escalation(
    confidence: float,
    contains_sensitive_topic: bool,
    user_requested_human: bool,
    auto_threshold: float = 0.85,
    review_threshold: float = 0.5,
) -> dict[str, Any]:
    """
    Decide whether a response should be auto-sent, queued for review,
    or escalated to a human operator.

    Rules (evaluated in priority order):
      1. If *user_requested_human* is True -> ESCALATE
      2. If *contains_sensitive_topic* is True -> REVIEW (at minimum)
      3. If *confidence* >= *auto_threshold* -> AUTO
      4. If *confidence* >= *review_threshold* -> REVIEW
      5. Otherwise -> ESCALATE

    When rule 2 applies AND confidence >= auto_threshold, the result
    is still REVIEW (sensitive topics always require at least review).

    Return dict:
      {
        "level": EscalationLevel value (the enum member),
        "reason": str (brief explanation),
        "confidence": float,
        "requires_human": bool (True for REVIEW and ESCALATE),
      }
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Confidence Threshold Classifier
# ---------------------------------------------------------------------------
def classify_with_confidence(
    scores: dict[str, float],
    threshold: float = 0.7,
    ambiguity_gap: float = 0.1,
) -> dict[str, Any]:
    """
    Given a dict mapping class labels to confidence scores (0-1),
    classify the input and assess confidence.

    Rules:
      1. Find the label with the highest score (*top_label*, *top_score*).
      2. Find the second-highest score (*runner_up_score*). If only one
         label, runner_up_score = 0.0.
      3. Determine classification result:
         - If *top_score* < *threshold* -> "low_confidence"
         - Else if (top_score - runner_up_score) < *ambiguity_gap*
           -> "ambiguous"
         - Else -> "confident"
      4. Return:
         {
           "label": top_label (str),
           "score": top_score (float),
           "result": "confident" | "ambiguous" | "low_confidence",
           "runner_up_label": str or None,
           "runner_up_score": float,
           "gap": float (top_score - runner_up_score),
         }
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Conversation State Persistence
# ---------------------------------------------------------------------------
def serialize_conversation(
    messages: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> str:
    """
    Serialize a conversation to a JSON string for persistence.

    The output JSON object must have the keys:
      - "version": "1.0"
      - "exported_at": metadata["exported_at"] (pass-through)
      - "conversation_id": metadata["conversation_id"]
      - "message_count": int (len of messages)
      - "messages": the messages list as-is

    Args:
        messages: List of message dicts.
        metadata: Must contain "exported_at" and "conversation_id".

    Returns:
        Pretty-printed JSON string (indent=2).
    """
    pass


def deserialize_conversation(json_str: str) -> dict[str, Any]:
    """
    Deserialize a conversation JSON string back to a dict.

    Validate that the required keys ("version", "messages",
    "conversation_id") are present.  Raise ``ValueError`` if any
    required key is missing.

    Args:
        json_str: JSON string produced by serialize_conversation.

    Returns:
        Parsed dict with all conversation data.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Multi-Turn Conversation Router
# ---------------------------------------------------------------------------
def route_conversation(
    message: str,
    intent_keywords: dict[str, list[str]],
    default_route: str = "general",
) -> dict[str, Any]:
    """
    Route a user message to the appropriate handler based on keyword
    matching.

    For each route in *intent_keywords*, check if ANY of its keywords
    appear in the message (case-insensitive).  Count the number of
    keyword matches per route.

    Rules:
      - The route with the most keyword matches wins.
      - Ties are broken alphabetically (first route name wins).
      - If no keywords match any route, use *default_route*.

    Return dict:
      {
        "route": str,
        "matched_keywords": list[str],   # the keywords that matched
        "confidence": float,             # matches / total_keywords for that route
        "is_default": bool,
      }
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 13: Conversation Analytics Collector
# ---------------------------------------------------------------------------
def compute_conversation_analytics(
    messages: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Compute analytics for a conversation.

    Each message dict has keys: "role", "content", "timestamp" (float).

    Compute:
      - total_messages: int
      - user_messages: int
      - assistant_messages: int
      - avg_user_msg_length: float (average character count, 0.0 if none)
      - avg_assistant_msg_length: float (average character count, 0.0 if none)
      - total_duration: float (last timestamp - first timestamp, 0.0 if < 2 msgs)
      - avg_response_time: float -- average time between each user message
        and the immediately following assistant message.  0.0 if no such
        pairs exist.
      - turn_count: int -- number of (user, assistant) adjacent pairs

    Returns:
        Dict with the analytics described above.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 14: User Feedback Collector and Processor
# ---------------------------------------------------------------------------
class FeedbackRating(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


def process_feedback(
    feedbacks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Process a batch of user feedback entries.

    Each feedback dict has:
      - "rating": str ("positive", "neutral", or "negative")
      - "comment": str (may be empty)
      - "conversation_id": str
      - "timestamp": float

    Compute:
      - total: int
      - counts: dict mapping each FeedbackRating value string to its count
      - satisfaction_score: float = (positive - negative) / total,
        rounded to 2 decimals.  0.0 if total == 0.
      - comments: list of non-empty comment strings
      - most_recent: the feedback dict with the highest timestamp, or None.

    Returns:
        Dict with all computed fields.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 15: Conversation Export Formatter
# ---------------------------------------------------------------------------
def export_conversation(
    messages: list[dict[str, str]],
    format: str = "markdown",
) -> str:
    """
    Export a conversation to a formatted string.

    Supported formats:

    "markdown":
        # Conversation

        **system**: <content>

        **user**: <content>

        **assistant**: <content>

        (blank line between each message)

    "text":
        [system]: <content>
        [user]: <content>
        [assistant]: <content>
        (single newline between messages, no blank lines)

    "html":
        <div class="conversation">
        <div class="message system"><strong>system</strong>: <content></div>
        <div class="message user"><strong>user</strong>: <content></div>
        <div class="message assistant"><strong>assistant</strong>: <content></div>
        </div>

    If *format* is not one of the three above, raise ``ValueError``.

    Args:
        messages: List of message dicts with "role" and "content".
        format: One of "markdown", "text", "html".

    Returns:
        Formatted conversation string.
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # -- Exercise 1 --
    convo = build_conversation_model()
    assert isinstance(convo, list) and len(convo) == 5
    assert convo[0]["role"] == "system"
    assert all("timestamp" in m and "metadata" in m for m in convo)
    assert all(isinstance(m["metadata"]["token_count"], int) for m in convo)
    print("Exercise  1 passed")

    # -- Exercise 2 --
    msgs = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "Bye"},
        {"role": "assistant", "content": "Goodbye!"},
    ]
    trimmed = sliding_window_context(msgs, max_messages=2, preserve_system=True)
    assert trimmed[0]["role"] == "system"
    assert len(trimmed) == 3  # system + 2 recent
    assert trimmed[-1]["content"] == "Goodbye!"
    print("Exercise  2 passed")

    # -- Exercise 3 --
    long_convo = [
        {"role": "system", "content": "System msg"},
        {"role": "user", "content": "msg1"},
        {"role": "assistant", "content": "resp1"},
        {"role": "user", "content": "msg2"},
        {"role": "assistant", "content": "resp2"},
        {"role": "user", "content": "msg3"},
        {"role": "assistant", "content": "resp3"},
    ]
    compressed = summarize_and_truncate(long_convo, max_messages=2)
    assert compressed[0]["role"] == "system"  # original system
    assert "Summary" in compressed[1]["content"]
    assert len(compressed) == 4  # system + summary + 2 recent
    print("Exercise  3 passed")

    # -- Exercise 4 --
    history = [
        {"role": "user", "content": "Tell me about machine learning"},
        {"role": "assistant", "content": "Machine learning is a field of AI"},
        {"role": "user", "content": "What about deep learning specifically"},
    ]
    budget = allocate_token_budget(
        total_budget=4096, system_tokens=100,
        history_messages=history, reserved_for_response=1024,
    )
    assert budget["total_budget"] == 4096
    assert budget["messages_included"] + budget["messages_dropped"] == 3
    assert budget["history_tokens_used"] <= budget["available_for_history"]
    print("Exercise  4 passed")

    # -- Exercise 5 --
    tpl = "You are a {{role}} specializing in {{domain}}."
    rendered = render_system_prompt(tpl, {"role": "tutor", "domain": "math"})
    assert rendered == "You are a tutor specializing in math."
    try:
        render_system_prompt("Hello {{name}}", {}, strict=True)
        assert False, "Should have raised KeyError"
    except KeyError:
        pass
    lax = render_system_prompt("Hello {{name}}", {}, strict=False)
    assert "{{name}}" in lax
    print("Exercise  5 passed")

    # -- Exercise 6 --
    result = validate_user_input("Hello there!", max_length=5000)
    assert result["valid"] is True
    result = validate_user_input("", max_length=5000)
    assert result["valid"] is False and result["reason"] == "empty_input"
    result = validate_user_input("visit http://evil.com", allow_urls=False)
    assert result["valid"] is False and result["reason"] == "urls_not_allowed"
    result = validate_user_input(
        "I will hack you", blocked_patterns=["hack"],
    )
    assert result["valid"] is False and "blocked_pattern" in result["reason"]
    print("Exercise  6 passed")

    # -- Exercise 7 --
    resp = filter_model_response(
        "Contact john@example.com or call 555-1234.",
        pii_patterns=["john@example.com", "555-1234"],
    )
    assert resp["redactions_applied"] == 2
    assert "[REDACTED]" in resp["filtered_response"]
    short = filter_model_response("Hello world", max_length=5)
    assert short["was_truncated"] is True
    print("Exercise  7 passed")

    # -- Exercise 8 --
    def ok():
        return "Primary response"
    fb = graceful_degradation_handler(ok, [])
    assert fb.message == "Primary response" and fb.source == "primary"

    def fail():
        raise RuntimeError("down")
    def backup():
        return "Backup response"
    fb = graceful_degradation_handler(fail, [backup])
    assert fb.source == "fallback_1" and fb.is_fallback is True

    fb = graceful_degradation_handler(fail, [fail])
    assert fb.source == "default"
    print("Exercise  8 passed")

    # -- Exercise 9 --
    result = evaluate_escalation(0.95, False, False)
    assert result["level"] == EscalationLevel.AUTO
    result = evaluate_escalation(0.95, True, False)
    assert result["level"] == EscalationLevel.REVIEW
    result = evaluate_escalation(0.3, False, True)
    assert result["level"] == EscalationLevel.ESCALATE
    result = evaluate_escalation(0.4, False, False)
    assert result["level"] == EscalationLevel.ESCALATE
    print("Exercise  9 passed")

    # -- Exercise 10 --
    scores = {"positive": 0.85, "negative": 0.10, "neutral": 0.05}
    cls = classify_with_confidence(scores)
    assert cls["label"] == "positive" and cls["result"] == "confident"
    scores2 = {"a": 0.51, "b": 0.49}
    cls2 = classify_with_confidence(scores2, threshold=0.5, ambiguity_gap=0.1)
    assert cls2["result"] == "ambiguous"
    scores3 = {"x": 0.3}
    cls3 = classify_with_confidence(scores3, threshold=0.7)
    assert cls3["result"] == "low_confidence"
    print("Exercise 10 passed")

    # -- Exercise 11 --
    sample_msgs = [{"role": "user", "content": "hi"}]
    meta = {"exported_at": "2025-01-01T00:00:00Z", "conversation_id": "abc-123"}
    json_str = serialize_conversation(sample_msgs, meta)
    parsed = json.loads(json_str)
    assert parsed["version"] == "1.0"
    assert parsed["message_count"] == 1

    restored = deserialize_conversation(json_str)
    assert restored["conversation_id"] == "abc-123"
    try:
        deserialize_conversation('{"messages": []}')
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("Exercise 11 passed")

    # -- Exercise 12 --
    intents = {
        "billing": ["invoice", "payment", "charge", "refund"],
        "technical": ["error", "bug", "crash", "not working"],
        "sales": ["pricing", "plan", "upgrade", "demo"],
    }
    r = route_conversation("I have a payment error", intents)
    assert r["route"] in ("billing", "technical")
    assert len(r["matched_keywords"]) >= 1
    r2 = route_conversation("hello there", intents)
    assert r2["is_default"] is True
    print("Exercise 12 passed")

    # -- Exercise 13 --
    analytics_msgs = [
        {"role": "user", "content": "Hello", "timestamp": 100.0},
        {"role": "assistant", "content": "Hi there!", "timestamp": 101.5},
        {"role": "user", "content": "How are you?", "timestamp": 105.0},
        {"role": "assistant", "content": "I'm doing well, thank you!", "timestamp": 106.0},
    ]
    stats = compute_conversation_analytics(analytics_msgs)
    assert stats["total_messages"] == 4
    assert stats["user_messages"] == 2
    assert stats["turn_count"] == 2
    assert stats["total_duration"] == 6.0
    print("Exercise 13 passed")

    # -- Exercise 14 --
    fb_list = [
        {"rating": "positive", "comment": "Great!", "conversation_id": "c1", "timestamp": 1.0},
        {"rating": "negative", "comment": "", "conversation_id": "c2", "timestamp": 2.0},
        {"rating": "positive", "comment": "Helpful", "conversation_id": "c3", "timestamp": 3.0},
    ]
    fb_result = process_feedback(fb_list)
    assert fb_result["total"] == 3
    assert fb_result["satisfaction_score"] == round((2 - 1) / 3, 2)
    assert len(fb_result["comments"]) == 2
    assert fb_result["most_recent"]["timestamp"] == 3.0
    print("Exercise 14 passed")

    # -- Exercise 15 --
    export_msgs = [
        {"role": "system", "content": "Be helpful."},
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ]
    md = export_conversation(export_msgs, format="markdown")
    assert "# Conversation" in md and "**user**" in md
    txt = export_conversation(export_msgs, format="text")
    assert "[user]" in txt
    html = export_conversation(export_msgs, format="html")
    assert '<div class="conversation">' in html
    try:
        export_conversation(export_msgs, format="xml")
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    print("Exercise 15 passed")

    print("\nAll exercises passed!")
