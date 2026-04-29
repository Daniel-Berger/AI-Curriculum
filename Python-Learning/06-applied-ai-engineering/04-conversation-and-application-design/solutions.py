"""
Module 04: Conversation & Application Design -- Solutions
==========================================================

Complete solutions for all 15 exercises with detailed comments,
test assertions, and runnable main block.

Covers: conversation management, guardrails, graceful degradation,
human-in-the-loop patterns, and application-level design for
production AI systems.
"""

from __future__ import annotations

import json
import re
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

    Each message carries role, content, a timestamp, and metadata with
    an estimated token count.  This mirrors the structure you would
    persist in a database or pass to a model API.
    """
    # Define the conversation turns
    turns = [
        ("system", "You are a helpful travel assistant."),
        ("user", "I want to plan a trip to Tokyo."),
        ("assistant",
         "I'd love to help you plan a trip to Tokyo! When are you thinking of going?"),
        ("user", "What's the best time to visit?"),
        ("assistant",
         "The best time to visit Tokyo is during spring (March-April) "
         "for cherry blossoms or autumn (October-November) for fall foliage."),
    ]

    messages: list[dict[str, Any]] = []
    base_timestamp = 1000.0

    for i, (role, content) in enumerate(turns):
        # Estimate tokens as word count -- a common quick heuristic
        token_count = len(content.split())
        messages.append({
            "role": role,
            "content": content,
            "timestamp": base_timestamp + float(i),
            "metadata": {"token_count": token_count},
        })

    return messages


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

    This is the simplest context-management strategy: just keep the N
    most recent turns.  The system prompt is optionally preserved at the
    front because it sets the persona/instructions for the model.
    """
    if not messages:
        return []

    # Separate system message if present and preservation is requested
    system_msg: dict[str, str] | None = None
    non_system: list[dict[str, str]] = list(messages)  # copy

    if preserve_system and messages[0]["role"] == "system":
        system_msg = messages[0]
        non_system = messages[1:]

    # Keep only the last max_messages non-system messages
    if len(non_system) > max_messages:
        non_system = non_system[-max_messages:]

    # Reassemble
    result: list[dict[str, str]] = []
    if system_msg is not None:
        result.append(system_msg)
    result.extend(non_system)

    return result


# ---------------------------------------------------------------------------
# Exercise 3: Conversation Summarizer
# ---------------------------------------------------------------------------
def summarize_and_truncate(
    messages: list[dict[str, str]],
    max_messages: int,
) -> list[dict[str, str]]:
    """
    Compress older messages into a summary, keeping *max_messages* recent
    turns verbatim.

    In production you would call an LLM to create the summary.  Here we
    create a deterministic textual summary by concatenating the older
    messages.  This pattern lets you maintain arbitrarily long conversations
    without exceeding the context window.
    """
    if not messages:
        return []

    # Separate optional system message
    system_msg: dict[str, str] | None = None
    non_system = list(messages)

    if messages[0]["role"] == "system":
        system_msg = messages[0]
        non_system = messages[1:]

    # If we're under budget, return as-is
    if len(non_system) <= max_messages:
        return list(messages)

    # Split into old (to summarize) and recent (to keep)
    old = non_system[:-max_messages]
    recent = non_system[-max_messages:]

    # Build a textual summary of old messages
    summary_lines = [f"{m['role']}: {m['content']}" for m in old]
    summary_content = "Summary of earlier conversation:\n" + "\n".join(summary_lines)
    summary_msg = {"role": "system", "content": summary_content}

    # Reassemble: [original system (if any), summary, recent...]
    result: list[dict[str, str]] = []
    if system_msg is not None:
        result.append(system_msg)
    result.append(summary_msg)
    result.extend(recent)

    return result


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
    Allocate tokens across system prompt, conversation history, and
    reserved response space.

    This is a critical production pattern: models have a fixed context
    window, so you must decide how to split it.  We walk backwards
    through history (most recent first) to keep the freshest context.
    """
    available_for_history = total_budget - system_tokens - reserved_for_response

    # Walk from most recent to oldest, accumulating token estimates
    history_tokens_used = 0
    messages_included = 0

    # Iterate in reverse (most recent first)
    for msg in reversed(history_messages):
        msg_tokens = len(msg["content"].split())
        if history_tokens_used + msg_tokens > available_for_history:
            break  # adding this message would exceed budget
        history_tokens_used += msg_tokens
        messages_included += 1

    messages_dropped = len(history_messages) - messages_included

    return {
        "total_budget": total_budget,
        "system_tokens": system_tokens,
        "response_reserved": reserved_for_response,
        "available_for_history": available_for_history,
        "history_tokens_used": history_tokens_used,
        "messages_included": messages_included,
        "messages_dropped": messages_dropped,
    }


# ---------------------------------------------------------------------------
# Exercise 5: System Prompt Template Engine
# ---------------------------------------------------------------------------
def render_system_prompt(
    template: str,
    variables: dict[str, str],
    strict: bool = True,
) -> str:
    """
    Render a system prompt template with {{placeholder}} syntax.

    In production, system prompts are often parameterized -- e.g.
    injecting user name, product context, or tool descriptions.
    This engine supports strict mode (fail on missing vars) and
    lax mode (leave placeholders in place).
    """
    # Find all placeholders with optional internal whitespace
    # Pattern: {{ optional_space var_name optional_space }}
    pattern = r"\{\{\s*(\w+)\s*\}\}"

    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        if var_name in variables:
            return variables[var_name]
        if strict:
            raise KeyError(var_name)
        # Lax mode: leave the original placeholder intact
        return match.group(0)

    return re.sub(pattern, replacer, template)


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

    Input guardrails are a first line of defense in production AI apps.
    They run *before* the model sees the input, catching obvious policy
    violations quickly and cheaply.
    """
    if blocked_patterns is None:
        blocked_patterns = []

    original_length = len(user_input)

    # Check 1: length
    if original_length > max_length:
        return {
            "valid": False,
            "sanitized_input": None,
            "reason": "exceeds_max_length",
            "original_length": original_length,
        }

    # Check 2: empty / whitespace-only
    stripped = user_input.strip()
    if not stripped:
        return {
            "valid": False,
            "sanitized_input": None,
            "reason": "empty_input",
            "original_length": original_length,
        }

    # Check 3: blocked patterns (case-insensitive)
    lower_input = stripped.lower()
    for pat in blocked_patterns:
        if pat.lower() in lower_input:
            return {
                "valid": False,
                "sanitized_input": None,
                "reason": f"blocked_pattern: {pat}",
                "original_length": original_length,
            }

    # Check 4: URLs
    if not allow_urls and ("http://" in stripped or "https://" in stripped):
        return {
            "valid": False,
            "sanitized_input": None,
            "reason": "urls_not_allowed",
            "original_length": original_length,
        }

    # All checks passed
    return {
        "valid": True,
        "sanitized_input": stripped,
        "reason": None,
        "original_length": original_length,
    }


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

    Output guardrails are the second line of defense: even if the model
    generates content that shouldn't be shared (PII, internal data),
    we catch it before it reaches the user.
    """
    if pii_patterns is None:
        pii_patterns = []

    original_length = len(response)
    filtered = response
    redactions_applied = 0

    # Step 1: Redact PII patterns (case-insensitive)
    for pattern in pii_patterns:
        # Count occurrences before replacing
        count = len(re.findall(re.escape(pattern), filtered, flags=re.IGNORECASE))
        redactions_applied += count
        filtered = re.sub(
            re.escape(pattern), redaction_token, filtered, flags=re.IGNORECASE,
        )

    # Step 2: Truncate if necessary
    was_truncated = False
    if len(filtered) > max_length:
        filtered = filtered[:max_length] + "... [truncated]"
        was_truncated = True

    return {
        "filtered_response": filtered,
        "redactions_applied": redactions_applied,
        "was_truncated": was_truncated,
        "original_length": original_length,
        "final_length": len(filtered),
    }


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
    Try the primary function, then each fallback in order, then a static
    default message.

    This is the "chain of responsibility" pattern for LLM apps:
    primary model -> cheaper/smaller fallback model -> cached response
    -> static default.  Every production system needs this.
    """
    # Try primary
    try:
        result = primary_fn()
        return FallbackResponse(message=result, source="primary", is_fallback=False)
    except Exception:
        pass  # fall through to fallbacks

    # Try each fallback in order
    for i, fallback_fn in enumerate(fallback_fns, start=1):
        try:
            result = fallback_fn()
            return FallbackResponse(
                message=result, source=f"fallback_{i}", is_fallback=True,
            )
        except Exception:
            continue  # try next fallback

    # All failed -- return the static default
    return FallbackResponse(
        message=default_message, source="default", is_fallback=True,
    )


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
    or escalated to a human.

    This is a key pattern for enterprise deployments: not every query
    should be auto-answered.  Sensitive topics, low confidence, and
    explicit user requests all trigger human involvement.
    """
    # Rule 1: user explicitly asked for a human
    if user_requested_human:
        return {
            "level": EscalationLevel.ESCALATE,
            "reason": "User requested human assistance",
            "confidence": confidence,
            "requires_human": True,
        }

    # Rule 2: sensitive topic -> at least REVIEW
    if contains_sensitive_topic:
        return {
            "level": EscalationLevel.REVIEW,
            "reason": "Sensitive topic detected, requires human review",
            "confidence": confidence,
            "requires_human": True,
        }

    # Rule 3: high confidence -> auto
    if confidence >= auto_threshold:
        return {
            "level": EscalationLevel.AUTO,
            "reason": "High confidence, auto-responding",
            "confidence": confidence,
            "requires_human": False,
        }

    # Rule 4: medium confidence -> review
    if confidence >= review_threshold:
        return {
            "level": EscalationLevel.REVIEW,
            "reason": "Medium confidence, queued for review",
            "confidence": confidence,
            "requires_human": True,
        }

    # Rule 5: low confidence -> escalate
    return {
        "level": EscalationLevel.ESCALATE,
        "reason": "Low confidence, escalating to human",
        "confidence": confidence,
        "requires_human": True,
    }


# ---------------------------------------------------------------------------
# Exercise 10: Confidence Threshold Classifier
# ---------------------------------------------------------------------------
def classify_with_confidence(
    scores: dict[str, float],
    threshold: float = 0.7,
    ambiguity_gap: float = 0.1,
) -> dict[str, Any]:
    """
    Classify based on confidence scores with ambiguity detection.

    Production classifiers should not blindly return the top label.
    We check whether the model is confident enough AND whether the
    gap between the top two labels is wide enough to be meaningful.
    """
    if not scores:
        raise ValueError("scores dict must not be empty")

    # Sort labels by score descending
    sorted_labels = sorted(scores.items(), key=lambda x: (-x[1], x[0]))

    top_label, top_score = sorted_labels[0]

    # Runner-up
    if len(sorted_labels) >= 2:
        runner_up_label, runner_up_score = sorted_labels[1]
    else:
        runner_up_label = None
        runner_up_score = 0.0

    gap = top_score - runner_up_score

    # Determine result
    if top_score < threshold:
        result = "low_confidence"
    elif gap < ambiguity_gap:
        result = "ambiguous"
    else:
        result = "confident"

    return {
        "label": top_label,
        "score": top_score,
        "result": result,
        "runner_up_label": runner_up_label,
        "runner_up_score": runner_up_score,
        "gap": gap,
    }


# ---------------------------------------------------------------------------
# Exercise 11: Conversation State Persistence
# ---------------------------------------------------------------------------
def serialize_conversation(
    messages: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> str:
    """
    Serialize a conversation to JSON for persistence.

    In production you'd store this in a database (Postgres, DynamoDB, etc).
    The version field allows you to evolve the schema over time --
    critical when you're iterating quickly on conversation formats.
    """
    payload = {
        "version": "1.0",
        "exported_at": metadata["exported_at"],
        "conversation_id": metadata["conversation_id"],
        "message_count": len(messages),
        "messages": messages,
    }
    return json.dumps(payload, indent=2)


def deserialize_conversation(json_str: str) -> dict[str, Any]:
    """
    Deserialize a conversation JSON string back to a dict, validating
    required keys are present.
    """
    data = json.loads(json_str)

    required_keys = {"version", "messages", "conversation_id"}
    missing = required_keys - set(data.keys())
    if missing:
        raise ValueError(f"Missing required keys: {missing}")

    return data


# ---------------------------------------------------------------------------
# Exercise 12: Multi-Turn Conversation Router
# ---------------------------------------------------------------------------
def route_conversation(
    message: str,
    intent_keywords: dict[str, list[str]],
    default_route: str = "general",
) -> dict[str, Any]:
    """
    Route a user message to a handler based on keyword matching.

    This is a lightweight, deterministic routing layer.  In production
    you might combine this with an LLM-based intent classifier, but
    keyword routing is fast, interpretable, and a good first pass.
    """
    message_lower = message.lower()

    # Score each route by counting keyword matches
    best_route = default_route
    best_count = 0
    best_keywords: list[str] = []
    best_total = 1  # avoid division by zero for default

    route_scores: list[tuple[str, int, list[str], int]] = []

    for route, keywords in intent_keywords.items():
        matched = [kw for kw in keywords if kw.lower() in message_lower]
        route_scores.append((route, len(matched), matched, len(keywords)))

    # Sort by match count descending, then alphabetically for ties
    route_scores.sort(key=lambda x: (-x[1], x[0]))

    if route_scores and route_scores[0][1] > 0:
        best_route = route_scores[0][0]
        best_count = route_scores[0][1]
        best_keywords = route_scores[0][2]
        best_total = route_scores[0][3]
        is_default = False
    else:
        is_default = True

    confidence = best_count / best_total if best_total > 0 else 0.0

    return {
        "route": best_route,
        "matched_keywords": best_keywords,
        "confidence": confidence,
        "is_default": is_default,
    }


# ---------------------------------------------------------------------------
# Exercise 13: Conversation Analytics Collector
# ---------------------------------------------------------------------------
def compute_conversation_analytics(
    messages: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Compute analytics for a conversation.

    These metrics are what you'd track in a dashboard for a production
    AI chatbot: response times, message lengths, turn counts.  They
    help you understand user engagement and model performance.
    """
    total_messages = len(messages)

    user_msgs = [m for m in messages if m["role"] == "user"]
    assistant_msgs = [m for m in messages if m["role"] == "assistant"]

    user_messages = len(user_msgs)
    assistant_messages = len(assistant_msgs)

    # Average message lengths (character count)
    avg_user_msg_length = (
        sum(len(m["content"]) for m in user_msgs) / user_messages
        if user_messages > 0 else 0.0
    )
    avg_assistant_msg_length = (
        sum(len(m["content"]) for m in assistant_msgs) / assistant_messages
        if assistant_messages > 0 else 0.0
    )

    # Total duration
    if total_messages >= 2:
        total_duration = messages[-1]["timestamp"] - messages[0]["timestamp"]
    else:
        total_duration = 0.0

    # Average response time: time between user msg and immediately
    # following assistant msg
    response_times: list[float] = []
    turn_count = 0
    for i in range(len(messages) - 1):
        if messages[i]["role"] == "user" and messages[i + 1]["role"] == "assistant":
            response_times.append(
                messages[i + 1]["timestamp"] - messages[i]["timestamp"]
            )
            turn_count += 1

    avg_response_time = (
        sum(response_times) / len(response_times)
        if response_times else 0.0
    )

    return {
        "total_messages": total_messages,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "avg_user_msg_length": avg_user_msg_length,
        "avg_assistant_msg_length": avg_assistant_msg_length,
        "total_duration": total_duration,
        "avg_response_time": avg_response_time,
        "turn_count": turn_count,
    }


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

    Satisfaction score is a simple net-promoter-style metric:
    (positive_count - negative_count) / total.  In production you'd
    also segment by conversation topic, time period, model version, etc.
    """
    total = len(feedbacks)

    # Count each rating category
    counts = {
        FeedbackRating.POSITIVE.value: 0,
        FeedbackRating.NEUTRAL.value: 0,
        FeedbackRating.NEGATIVE.value: 0,
    }
    for fb in feedbacks:
        rating = fb["rating"]
        if rating in counts:
            counts[rating] += 1

    # Satisfaction score
    if total > 0:
        satisfaction_score = round(
            (counts["positive"] - counts["negative"]) / total, 2,
        )
    else:
        satisfaction_score = 0.0

    # Collect non-empty comments
    comments = [fb["comment"] for fb in feedbacks if fb.get("comment", "").strip()]

    # Most recent feedback
    most_recent = max(feedbacks, key=lambda f: f["timestamp"]) if feedbacks else None

    return {
        "total": total,
        "counts": counts,
        "satisfaction_score": satisfaction_score,
        "comments": comments,
        "most_recent": most_recent,
    }


# ---------------------------------------------------------------------------
# Exercise 15: Conversation Export Formatter
# ---------------------------------------------------------------------------
def export_conversation(
    messages: list[dict[str, str]],
    format: str = "markdown",
) -> str:
    """
    Export a conversation to markdown, plain text, or HTML.

    Multiple export formats are needed in practice: markdown for docs,
    plain text for logs, HTML for web UIs or email reports.
    """
    if format == "markdown":
        lines = ["# Conversation", ""]
        for msg in messages:
            lines.append(f"**{msg['role']}**: {msg['content']}")
            lines.append("")  # blank line between messages
        return "\n".join(lines)

    elif format == "text":
        lines = []
        for msg in messages:
            lines.append(f"[{msg['role']}]: {msg['content']}")
        return "\n".join(lines)

    elif format == "html":
        inner_lines = []
        for msg in messages:
            inner_lines.append(
                f'<div class="message {msg["role"]}">'
                f'<strong>{msg["role"]}</strong>: {msg["content"]}</div>'
            )
        inner = "\n".join(inner_lines)
        return f'<div class="conversation">\n{inner}\n</div>'

    else:
        raise ValueError(f"Unsupported format: {format!r}. Use 'markdown', 'text', or 'html'.")


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # ---- Exercise 1: Conversation Message Data Model ----
    convo = build_conversation_model()
    assert isinstance(convo, list) and len(convo) == 5
    assert convo[0]["role"] == "system"
    assert convo[1]["role"] == "user"
    assert convo[2]["role"] == "assistant"
    assert all("timestamp" in m and "metadata" in m for m in convo)
    assert all(isinstance(m["metadata"]["token_count"], int) for m in convo)
    # Timestamps should be sequential
    for i in range(1, len(convo)):
        assert convo[i]["timestamp"] > convo[i - 1]["timestamp"]
    print("Exercise  1 passed")

    # ---- Exercise 2: Sliding Window Context Manager ----
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
    assert trimmed[1]["content"] == "Bye"
    assert trimmed[2]["content"] == "Goodbye!"

    # Without preserving system
    trimmed2 = sliding_window_context(msgs, max_messages=2, preserve_system=False)
    assert len(trimmed2) == 2
    assert trimmed2[0]["content"] == "Bye"

    # All fit
    trimmed3 = sliding_window_context(msgs, max_messages=10, preserve_system=True)
    assert len(trimmed3) == 5
    print("Exercise  2 passed")

    # ---- Exercise 3: Conversation Summarizer ----
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
    assert compressed[0]["content"] == "System msg"
    assert "Summary" in compressed[1]["content"]
    assert "msg1" in compressed[1]["content"]  # old msgs are summarized
    assert len(compressed) == 4  # system + summary + 2 recent
    assert compressed[-1]["content"] == "resp3"

    # Under budget -- return unchanged
    short_convo = [{"role": "user", "content": "hi"}]
    assert summarize_and_truncate(short_convo, max_messages=5) == short_convo
    print("Exercise  3 passed")

    # ---- Exercise 4: Token Budget Allocator ----
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
    assert budget["system_tokens"] == 100
    assert budget["response_reserved"] == 1024
    assert budget["available_for_history"] == 4096 - 100 - 1024
    assert budget["messages_included"] + budget["messages_dropped"] == 3
    assert budget["history_tokens_used"] <= budget["available_for_history"]

    # Tiny budget -- should drop messages
    tiny = allocate_token_budget(
        total_budget=130, system_tokens=100,
        history_messages=history, reserved_for_response=20,
    )
    assert tiny["messages_dropped"] >= 1
    print("Exercise  4 passed")

    # ---- Exercise 5: System Prompt Template Engine ----
    tpl = "You are a {{role}} specializing in {{domain}}."
    rendered = render_system_prompt(tpl, {"role": "tutor", "domain": "math"})
    assert rendered == "You are a tutor specializing in math."

    # Whitespace inside braces
    tpl2 = "Hello {{ name }}!"
    assert render_system_prompt(tpl2, {"name": "World"}) == "Hello World!"

    # Strict mode: missing variable
    try:
        render_system_prompt("Hello {{name}}", {}, strict=True)
        assert False, "Should have raised KeyError"
    except KeyError as e:
        assert "name" in str(e)

    # Lax mode: leave placeholder
    lax = render_system_prompt("Hello {{name}}", {}, strict=False)
    assert "{{name}}" in lax

    # Extra keys silently ignored
    rendered3 = render_system_prompt("Hi {{x}}", {"x": "A", "y": "B"})
    assert rendered3 == "Hi A"
    print("Exercise  5 passed")

    # ---- Exercise 6: Input Guardrails ----
    result = validate_user_input("Hello there!", max_length=5000)
    assert result["valid"] is True
    assert result["sanitized_input"] == "Hello there!"

    result = validate_user_input("", max_length=5000)
    assert result["valid"] is False and result["reason"] == "empty_input"

    result = validate_user_input("   ", max_length=5000)
    assert result["valid"] is False and result["reason"] == "empty_input"

    result = validate_user_input("a" * 6000, max_length=5000)
    assert result["valid"] is False and result["reason"] == "exceeds_max_length"

    result = validate_user_input("visit http://evil.com", allow_urls=False)
    assert result["valid"] is False and result["reason"] == "urls_not_allowed"

    result = validate_user_input("visit http://good.com", allow_urls=True)
    assert result["valid"] is True

    result = validate_user_input("I will HACK you", blocked_patterns=["hack"])
    assert result["valid"] is False and "blocked_pattern" in result["reason"]
    print("Exercise  6 passed")

    # ---- Exercise 7: Output Guardrails ----
    resp = filter_model_response(
        "Contact john@example.com or call 555-1234.",
        pii_patterns=["john@example.com", "555-1234"],
    )
    assert resp["redactions_applied"] == 2
    assert "[REDACTED]" in resp["filtered_response"]
    assert "john@example.com" not in resp["filtered_response"]

    # Truncation
    short = filter_model_response("Hello world", max_length=5)
    assert short["was_truncated"] is True
    assert short["filtered_response"].endswith("... [truncated]")

    # No redactions needed
    clean = filter_model_response("All good here", pii_patterns=[])
    assert clean["redactions_applied"] == 0
    assert clean["was_truncated"] is False
    print("Exercise  7 passed")

    # ---- Exercise 8: Graceful Degradation Handler ----
    def ok():
        return "Primary response"

    fb = graceful_degradation_handler(ok, [])
    assert fb.message == "Primary response"
    assert fb.source == "primary"
    assert fb.is_fallback is False

    def fail():
        raise RuntimeError("Service down")

    def backup():
        return "Backup response"

    fb = graceful_degradation_handler(fail, [backup])
    assert fb.message == "Backup response"
    assert fb.source == "fallback_1"
    assert fb.is_fallback is True

    def also_fail():
        raise RuntimeError("Also down")

    fb = graceful_degradation_handler(fail, [also_fail, backup])
    assert fb.source == "fallback_2"

    fb = graceful_degradation_handler(fail, [also_fail, also_fail])
    assert fb.source == "default"
    assert "unable to process" in fb.message.lower()
    print("Exercise  8 passed")

    # ---- Exercise 9: Escalation System ----
    result = evaluate_escalation(0.95, False, False)
    assert result["level"] == EscalationLevel.AUTO
    assert result["requires_human"] is False

    result = evaluate_escalation(0.95, True, False)
    assert result["level"] == EscalationLevel.REVIEW  # sensitive overrides high confidence

    result = evaluate_escalation(0.3, False, True)
    assert result["level"] == EscalationLevel.ESCALATE  # user request always wins

    result = evaluate_escalation(0.6, False, False)
    assert result["level"] == EscalationLevel.REVIEW  # medium confidence

    result = evaluate_escalation(0.4, False, False)
    assert result["level"] == EscalationLevel.ESCALATE  # below review threshold
    print("Exercise  9 passed")

    # ---- Exercise 10: Confidence Classifier ----
    scores = {"positive": 0.85, "negative": 0.10, "neutral": 0.05}
    cls = classify_with_confidence(scores)
    assert cls["label"] == "positive"
    assert cls["result"] == "confident"
    assert cls["gap"] == 0.75

    scores2 = {"a": 0.51, "b": 0.49}
    cls2 = classify_with_confidence(scores2, threshold=0.5, ambiguity_gap=0.1)
    assert cls2["result"] == "ambiguous"

    scores3 = {"x": 0.3}
    cls3 = classify_with_confidence(scores3, threshold=0.7)
    assert cls3["result"] == "low_confidence"
    assert cls3["runner_up_label"] is None
    assert cls3["runner_up_score"] == 0.0
    print("Exercise 10 passed")

    # ---- Exercise 11: Conversation Persistence ----
    sample_msgs = [{"role": "user", "content": "hi"}]
    meta = {"exported_at": "2025-01-01T00:00:00Z", "conversation_id": "abc-123"}
    json_str = serialize_conversation(sample_msgs, meta)
    parsed = json.loads(json_str)
    assert parsed["version"] == "1.0"
    assert parsed["message_count"] == 1
    assert parsed["conversation_id"] == "abc-123"

    restored = deserialize_conversation(json_str)
    assert restored["conversation_id"] == "abc-123"
    assert len(restored["messages"]) == 1

    # Missing key should raise ValueError
    try:
        deserialize_conversation('{"messages": []}')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Missing" in str(e)
    print("Exercise 11 passed")

    # ---- Exercise 12: Conversation Router ----
    intents = {
        "billing": ["invoice", "payment", "charge", "refund"],
        "technical": ["error", "bug", "crash", "not working"],
        "sales": ["pricing", "plan", "upgrade", "demo"],
    }
    r = route_conversation("I have a payment error", intents)
    assert r["route"] in ("billing", "technical")
    assert len(r["matched_keywords"]) >= 1
    assert r["is_default"] is False

    # Multiple matches in one route
    r2 = route_conversation("I need a refund for the payment charge", intents)
    assert r2["route"] == "billing"
    assert len(r2["matched_keywords"]) >= 2

    # No match -> default
    r3 = route_conversation("hello there", intents)
    assert r3["is_default"] is True
    assert r3["route"] == "general"
    print("Exercise 12 passed")

    # ---- Exercise 13: Conversation Analytics ----
    analytics_msgs = [
        {"role": "user", "content": "Hello", "timestamp": 100.0},
        {"role": "assistant", "content": "Hi there!", "timestamp": 101.5},
        {"role": "user", "content": "How are you?", "timestamp": 105.0},
        {"role": "assistant", "content": "I'm doing well, thank you!", "timestamp": 106.0},
    ]
    stats = compute_conversation_analytics(analytics_msgs)
    assert stats["total_messages"] == 4
    assert stats["user_messages"] == 2
    assert stats["assistant_messages"] == 2
    assert stats["total_duration"] == 6.0
    assert stats["turn_count"] == 2
    assert stats["avg_response_time"] == (1.5 + 1.0) / 2
    assert stats["avg_user_msg_length"] == (5 + 12) / 2  # "Hello", "How are you?"
    print("Exercise 13 passed")

    # ---- Exercise 14: Feedback Processor ----
    fb_list = [
        {"rating": "positive", "comment": "Great!", "conversation_id": "c1", "timestamp": 1.0},
        {"rating": "negative", "comment": "", "conversation_id": "c2", "timestamp": 2.0},
        {"rating": "positive", "comment": "Helpful", "conversation_id": "c3", "timestamp": 3.0},
    ]
    fb_result = process_feedback(fb_list)
    assert fb_result["total"] == 3
    assert fb_result["counts"]["positive"] == 2
    assert fb_result["counts"]["negative"] == 1
    assert fb_result["satisfaction_score"] == round((2 - 1) / 3, 2)
    assert len(fb_result["comments"]) == 2  # empty comment excluded
    assert fb_result["most_recent"]["timestamp"] == 3.0

    # Empty list
    empty_result = process_feedback([])
    assert empty_result["total"] == 0
    assert empty_result["satisfaction_score"] == 0.0
    assert empty_result["most_recent"] is None
    print("Exercise 14 passed")

    # ---- Exercise 15: Conversation Export ----
    export_msgs = [
        {"role": "system", "content": "Be helpful."},
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ]

    # Markdown
    md = export_conversation(export_msgs, format="markdown")
    assert "# Conversation" in md
    assert "**user**: Hi" in md
    assert "**assistant**: Hello!" in md

    # Text
    txt = export_conversation(export_msgs, format="text")
    assert "[user]: Hi" in txt
    assert "[system]: Be helpful." in txt

    # HTML
    html = export_conversation(export_msgs, format="html")
    assert '<div class="conversation">' in html
    assert '<div class="message user">' in html
    assert "<strong>assistant</strong>: Hello!</div>" in html

    # Invalid format
    try:
        export_conversation(export_msgs, format="xml")
        assert False, "Should raise ValueError"
    except ValueError:
        pass

    print("Exercise 15 passed")

    print("\nAll solutions passed!")
