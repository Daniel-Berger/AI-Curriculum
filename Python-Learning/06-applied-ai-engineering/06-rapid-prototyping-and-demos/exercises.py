"""
Module 06: Rapid Prototyping & Demos - Exercises
==================================================
Target audience: Swift/iOS developers transitioning to AI/ML engineering roles.

Context:
As a solutions engineer or applied AI engineer, you will constantly build
proof-of-concept demos, internal prototypes, and customer-facing showcases.
Speed matters -- but so does polish, reliability, and data quality. These
exercises teach you the patterns behind Streamlit apps, demo scaffolding,
session management, synthetic data, feature flags, and deployment configs
that you will use in every customer engagement.

Instructions:
- Fill in each function body (replace `pass` or `raise NotImplementedError`).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- No API keys or external services required -- everything is self-contained.

Difficulty levels:
  Easy   - Direct data-modeling / configuration tasks
  Medium - Requires combining multiple patterns or light logic
  Hard   - End-to-end workflows, generators, or multi-step validation
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Literal
from uuid import uuid4


# =============================================================================
# Exercise 1: Build a Streamlit App Configuration Model
# Difficulty: Easy
# =============================================================================
def build_app_config(
    app_name: str,
    page_title: str,
    page_icon: str = "🤖",
    layout: Literal["centered", "wide"] = "wide",
    sidebar_state: Literal["expanded", "collapsed", "auto"] = "expanded",
    theme_primary_color: str = "#FF4B4B",
    show_footer: bool = False,
    max_upload_mb: int = 200,
) -> dict[str, Any]:
    """Build a Streamlit-style app configuration dictionary.

    In a real Streamlit app you call `st.set_page_config(...)` at the top of
    your script.  This exercise models that configuration as a plain dict so
    you can validate and version it without a running Streamlit server.

    Returns a dict with EXACTLY these keys:
        - "app_name"            -> str
        - "page_title"          -> str
        - "page_icon"           -> str
        - "layout"              -> "centered" | "wide"
        - "sidebar_state"       -> "expanded" | "collapsed" | "auto"
        - "theme_primary_color" -> str  (must start with '#' and be 7 chars)
        - "show_footer"         -> bool
        - "max_upload_mb"       -> int  (must be > 0)
        - "config_version"      -> str  (always "1.0")

    Raises ValueError when:
        - theme_primary_color does not start with '#' or is not 7 characters
        - max_upload_mb <= 0
        - app_name is empty

    Swift parallel: think of this as building a struct conforming to Codable
    with validation in `init(from decoder:)`.
    """
    pass


# =============================================================================
# Exercise 2: Implement a Chat Message Component
# Difficulty: Easy
# =============================================================================
class MessageRole(str, Enum):
    """Roles in a chat conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ChatMessage:
    """Data model for a single chat message displayed in a demo UI.

    Attributes to set:
        role        - MessageRole
        content     - str (the text body)
        timestamp   - datetime (default to now via default_factory)
        message_id  - str (default to a new uuid4 hex string)
        metadata    - dict[str, Any] (default empty dict)

    Implement these methods:

    to_api_format() -> dict:
        Return {"role": <role.value>, "content": <content>}
        Only include role and content -- this is the minimal format for
        an LLM API call.

    to_display_format() -> dict:
        Return {"role": <role.value>, "content": <content>,
                "timestamp": <ISO-format string>, "id": <message_id>}

    Swift parallel: similar to a ChatMessage struct with CodingKeys for
    multiple serialization targets.
    """
    pass  # Define fields and methods


# =============================================================================
# Exercise 3: Build a Demo Scenario Loader
# Difficulty: Medium
# =============================================================================
def load_demo_scenarios(json_string: str) -> list[dict[str, Any]]:
    """Parse and validate demo scenarios from a JSON string.

    Each scenario in the JSON array MUST have:
        - "id"          (str, non-empty)
        - "title"       (str, non-empty)
        - "description" (str)
        - "messages"    (list of dicts, each with "role" and "content")

    Processing rules:
        1. Parse the JSON string into a list of dicts.
        2. For each scenario, validate that all required keys exist and the
           values satisfy the constraints above.
        3. Add a "message_count" key set to len(messages).
        4. Add a "loaded_at" key set to the current ISO-format datetime string.
        5. Skip (do not include) any scenario that fails validation -- do NOT
           raise an exception for individual bad scenarios.
        6. Return the list of valid, enriched scenario dicts.

    Raises:
        json.JSONDecodeError - if the json_string is not valid JSON at all.

    >>> data = '[{"id":"s1","title":"T","description":"D","messages":[{"role":"user","content":"Hi"}]}]'
    >>> result = load_demo_scenarios(data)
    >>> result[0]["message_count"]
    1
    """
    pass


# =============================================================================
# Exercise 4: Implement a Session State Manager
# Difficulty: Medium
# =============================================================================
class SessionStateManager:
    """Manages session state for a demo app (like Streamlit's st.session_state).

    This is a simplified in-memory key-value store with history tracking.

    Implement:
        __init__():
            Initialize internal storage (_state: dict) and _history: list.

        get(key, default=None):
            Return the value for key, or default if missing.

        set(key, value):
            Store key=value and append a history entry:
            {"action": "set", "key": key, "value": value,
             "timestamp": <ISO datetime>}

        delete(key):
            Remove the key if it exists (no error if missing) and append a
            history entry with action="delete".

        get_history() -> list[dict]:
            Return a copy of the history list.

        reset():
            Clear all state and history.  Append a single history entry:
            {"action": "reset", "timestamp": <ISO datetime>}

        snapshot() -> dict:
            Return a shallow copy of the current state dict.

    Swift parallel: this mirrors a simple ObservableObject with @Published
    properties and a change log.
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def get(self, key: str, default: Any = None) -> Any:
        raise NotImplementedError

    def set(self, key: str, value: Any) -> None:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError

    def get_history(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError

    def snapshot(self) -> dict[str, Any]:
        raise NotImplementedError


# =============================================================================
# Exercise 5: Build a File Upload Processor
# Difficulty: Medium
# =============================================================================
def process_upload(
    filename: str,
    content_bytes: bytes,
    allowed_extensions: list[str] | None = None,
    max_size_bytes: int = 10 * 1024 * 1024,
) -> dict[str, Any]:
    """Validate and process a simulated file upload for a demo app.

    Steps:
        1. Extract the file extension (lowercase, without the dot).
           If the file has no extension, set extension to "".
        2. If allowed_extensions is provided and the extension is not in that
           list, raise ValueError("Unsupported file type: <ext>").
        3. If len(content_bytes) > max_size_bytes, raise
           ValueError("File too large: <size> bytes (max <max_size_bytes>)").
        4. Compute an MD5 hex digest of content_bytes for deduplication.
        5. Return a dict with:
            - "filename"     -> original filename
            - "extension"    -> extracted extension (lowercase, no dot)
            - "size_bytes"   -> int, length of content_bytes
            - "size_display" -> human-readable size string:
                  - < 1024        -> "<n> B"
                  - < 1024*1024   -> "<n.1f> KB"  (one decimal)
                  - else          -> "<n.2f> MB"  (two decimals)
            - "md5"          -> hex digest string
            - "content_type" -> guessed MIME type from this map:
                  {"txt": "text/plain", "csv": "text/csv",
                   "json": "application/json", "pdf": "application/pdf",
                   "png": "image/png", "jpg": "image/jpeg"}
                  Default to "application/octet-stream" if unknown.
            - "processed_at" -> ISO datetime string

    Swift parallel: similar to processing a Data payload from a
    UIDocumentPickerViewController with UTType validation.
    """
    pass


# =============================================================================
# Exercise 6: Implement a Demo Recording System
# Difficulty: Medium
# =============================================================================
class DemoRecorder:
    """Capture demo interactions (inputs + outputs) for replay / analysis.

    Implement:
        __init__(demo_name: str):
            Store the demo_name, start_time (datetime.now()),
            an empty list of _events, and _is_recording = True.

        record_event(event_type: str, data: dict) -> dict:
            If not recording, raise RuntimeError("Recording stopped").
            Create an event dict:
                {"event_id": <incremental int starting at 1>,
                 "event_type": event_type,
                 "data": data,
                 "timestamp": <ISO datetime>}
            Append it and return it.

        stop() -> None:
            Set _is_recording to False.  Record the stop time.

        get_events(event_type: str | None = None) -> list[dict]:
            If event_type is None, return all events.
            Otherwise, return only events matching that type.

        get_summary() -> dict:
            Return {"demo_name": ..., "total_events": ...,
                    "event_types": <dict of type -> count>,
                    "duration_seconds": <float, 0.0 if still recording>,
                    "is_recording": bool}

    Swift parallel: think of this like an analytics event logger with
    filtering and summary capabilities.
    """

    def __init__(self, demo_name: str) -> None:
        raise NotImplementedError

    def record_event(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

    def get_events(self, event_type: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    def get_summary(self) -> dict[str, Any]:
        raise NotImplementedError


# =============================================================================
# Exercise 7: Build a POC Requirements Checklist Validator
# Difficulty: Medium
# =============================================================================
def validate_poc_requirements(
    requirements: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate a list of POC requirement items and produce a status report.

    Each requirement dict should contain:
        - "id"       (str, required)
        - "title"    (str, required)
        - "status"   (str, one of: "not_started", "in_progress", "completed", "blocked")
        - "priority" (str, one of: "critical", "high", "medium", "low")
        - "owner"    (str, optional -- default "unassigned")

    Processing:
        1. Validate each requirement.  If any required key is missing or a
           status/priority value is invalid, add it to an "invalid" list with
           the id (or "unknown" if id is missing) and an error message.
        2. Group valid requirements by status.
        3. Compute readiness:
           - all_critical_done: bool -- every requirement with priority
             "critical" has status "completed".
           - completion_pct: float -- (completed / total_valid) * 100,
             rounded to 1 decimal.  0.0 if no valid requirements.
           - blockers: list of ids for requirements with status "blocked".

    Return:
        {"total": int (all input items),
         "valid": int,
         "invalid": list[{"id": str, "error": str}],
         "by_status": {"not_started": int, "in_progress": int,
                       "completed": int, "blocked": int},
         "all_critical_done": bool,
         "completion_pct": float,
         "blockers": list[str]}
    """
    pass


# =============================================================================
# Exercise 8: Implement a Demo Data Generator
# Difficulty: Hard
# =============================================================================
def generate_demo_conversations(
    num_conversations: int,
    turns_per_conversation: int = 3,
    topics: list[str] | None = None,
    include_system: bool = True,
) -> list[dict[str, Any]]:
    """Generate synthetic demo conversations for showcasing an AI assistant.

    This is useful when you need realistic-looking data for a live demo but
    cannot use real customer data.

    Rules:
        - Default topics: ["product inquiry", "technical support", "billing"]
        - Each conversation is a dict with:
            "conversation_id": "conv_<i>" where i is 1-indexed
            "topic": cycle through topics list (use modulo)
            "messages": list of message dicts
            "created_at": ISO datetime string
        - Messages in each conversation:
            * If include_system is True, start with a system message:
              {"role": "system", "content": "You are a helpful assistant
               specializing in <topic>."}
            * Then alternate user/assistant for `turns_per_conversation` turns
              (one turn = one user message + one assistant message).
              - User message content:
                "User question {turn} about {topic}"   (turn is 1-indexed)
              - Assistant message content:
                "Here's helpful information about {topic} for question {turn}."
        - Raise ValueError if num_conversations < 1 or
          turns_per_conversation < 1.

    Returns: list of conversation dicts.
    """
    pass


# =============================================================================
# Exercise 9: Build a Feature Flag System for Demos
# Difficulty: Medium
# =============================================================================
class FeatureFlagManager:
    """Manage feature flags for controlling demo behavior.

    This lets you toggle features on/off during a live demo without
    redeploying -- essential for progressive disclosure to customers.

    Implement:
        __init__():
            Initialize an internal dict of flags.  Each flag is stored as:
            {"enabled": bool, "description": str, "created_at": str}

        register(name: str, enabled: bool = False, description: str = ""):
            Add a flag.  Raise ValueError if the name already exists.

        is_enabled(name: str) -> bool:
            Return True/False.  Raise KeyError if the flag does not exist.

        toggle(name: str) -> bool:
            Flip the flag and return the NEW value.
            Raise KeyError if the flag does not exist.

        enable(name: str) / disable(name: str):
            Explicitly set the flag.  Raise KeyError if missing.

        list_flags(only_enabled: bool = False) -> dict[str, dict]:
            Return a dict of flag_name -> flag_data.
            If only_enabled is True, include only enabled flags.

        bulk_update(updates: dict[str, bool]) -> dict[str, bool]:
            Set multiple flags at once.  Skip names that do not exist.
            Return a dict of name -> new_value for flags that WERE updated.

    Swift parallel: similar to a FeatureGate / LaunchDarkly wrapper with
    @AppStorage-backed booleans.
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def register(self, name: str, enabled: bool = False, description: str = "") -> None:
        raise NotImplementedError

    def is_enabled(self, name: str) -> bool:
        raise NotImplementedError

    def toggle(self, name: str) -> bool:
        raise NotImplementedError

    def enable(self, name: str) -> None:
        raise NotImplementedError

    def disable(self, name: str) -> None:
        raise NotImplementedError

    def list_flags(self, only_enabled: bool = False) -> dict[str, dict[str, Any]]:
        raise NotImplementedError

    def bulk_update(self, updates: dict[str, bool]) -> dict[str, bool]:
        raise NotImplementedError


# =============================================================================
# Exercise 10: Implement a Demo Metrics Collector
# Difficulty: Medium
# =============================================================================
class DemoMetricsCollector:
    """Collect and aggregate metrics during a demo run.

    Useful for showing customers latency percentiles, token counts, etc.

    Implement:
        __init__():
            Initialize an empty dict of metric names -> list of float values.

        record(metric_name: str, value: float) -> None:
            Append the value to the metric's list (create list if first time).

        get_stats(metric_name: str) -> dict:
            Return {"count": int, "sum": float, "mean": float,
                    "min": float, "max": float}
            Raise KeyError if the metric has never been recorded.
            Round mean to 4 decimal places.

        get_all_metric_names() -> list[str]:
            Return sorted list of all metric names.

        reset(metric_name: str | None = None) -> None:
            If metric_name is given, clear that metric (raise KeyError if
            missing).  If None, clear everything.

        export() -> dict[str, dict]:
            Return {metric_name: get_stats(metric_name)} for all metrics.
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def record(self, metric_name: str, value: float) -> None:
        raise NotImplementedError

    def get_stats(self, metric_name: str) -> dict[str, Any]:
        raise NotImplementedError

    def get_all_metric_names(self) -> list[str]:
        raise NotImplementedError

    def reset(self, metric_name: str | None = None) -> None:
        raise NotImplementedError

    def export(self) -> dict[str, dict[str, Any]]:
        raise NotImplementedError


# =============================================================================
# Exercise 11: Build a Customer Handoff Document Generator
# Difficulty: Hard
# =============================================================================
def generate_handoff_document(
    customer_name: str,
    poc_title: str,
    features_demonstrated: list[dict[str, str]],
    metrics: dict[str, float],
    next_steps: list[str],
    technical_notes: list[str] | None = None,
) -> dict[str, Any]:
    """Generate a structured handoff document after a successful POC demo.

    This document is what you hand to the customer's engineering team so they
    can move from POC to production.

    Args:
        customer_name: Company name.
        poc_title: Title of the proof of concept.
        features_demonstrated: List of dicts with "name" and "status" keys.
            Valid statuses: "working", "partial", "not_demonstrated".
        metrics: Dict of metric_name -> value (e.g. {"avg_latency_ms": 120}).
        next_steps: Non-empty list of action items.
        technical_notes: Optional list of engineering notes.

    Validation:
        - customer_name and poc_title must be non-empty strings.
        - features_demonstrated must be non-empty.
        - Each feature must have "name" and "status" keys, and status must
          be one of the three valid values.
        - next_steps must be non-empty.
        Raise ValueError with a descriptive message for any violation.

    Return dict:
        {
            "document_type": "poc_handoff",
            "version": "1.0",
            "generated_at": <ISO datetime>,
            "customer": customer_name,
            "poc_title": poc_title,
            "features": features_demonstrated,       (pass through as-is)
            "feature_summary": {
                "total": int,
                "working": int,     (count of "working")
                "partial": int,
                "not_demonstrated": int,
            },
            "metrics": metrics,
            "next_steps": next_steps,
            "technical_notes": technical_notes or [],
            "ready_for_production": bool
                -> True only if ALL features have status "working"
        }
    """
    pass


# =============================================================================
# Exercise 12: Implement a Demo Fallback System
# Difficulty: Hard
# =============================================================================
class DemoFallbackSystem:
    """Provide pre-cached responses when a live API is unavailable.

    During live demos, network issues or rate limits can derail the
    presentation.  A fallback system ensures you always have a response.

    Implement:
        __init__():
            Initialize a dict of cached responses, keyed by a string key.
            Each entry: {"response": Any, "used_count": int, "added_at": str}

        add_fallback(key: str, response: Any) -> None:
            Store a cached response.  Overwrite if key already exists
            (reset used_count to 0 when overwriting).

        get_response(key: str, live_fn: callable | None = None) -> dict:
            1. If live_fn is provided, try calling it.
               - If it succeeds, return {"source": "live", "response": <result>}
               - If it raises any exception, fall through to step 2.
            2. If the key exists in cache, increment used_count and return
               {"source": "fallback", "response": <cached>, "used_count": int}
            3. Otherwise return {"source": "error",
                                 "response": "No fallback available for: <key>"}

        list_fallbacks() -> dict[str, dict]:
            Return a copy of the internal cache dict.

        get_stats() -> dict:
            Return {"total_fallbacks": int,
                    "total_used": int (sum of all used_counts),
                    "most_used": str | None (key with highest used_count,
                        None if all are 0 or cache is empty)}
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def add_fallback(self, key: str, response: Any) -> None:
        raise NotImplementedError

    def get_response(self, key: str, live_fn: Any = None) -> dict[str, Any]:
        raise NotImplementedError

    def list_fallbacks(self) -> dict[str, dict[str, Any]]:
        raise NotImplementedError

    def get_stats(self) -> dict[str, Any]:
        raise NotImplementedError


# =============================================================================
# Exercise 13: Build a Progressive Complexity Demo Flow
# Difficulty: Hard
# =============================================================================
def build_progressive_demo(
    stages: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a progressive-disclosure demo flow with multiple stages.

    In customer demos, you start simple and layer on complexity.  Each stage
    builds on the previous one.

    Each stage dict must have:
        - "name"        (str, required)
        - "description" (str, required)
        - "complexity"  (int, 1-5, required)
        - "features"    (list[str], required, non-empty)
        - "demo_script" (str, required -- talking points for the presenter)

    Validation:
        - stages must be non-empty.
        - All required keys must be present with correct types/ranges.
        - complexity values must be non-decreasing across the list (each
          stage's complexity >= previous stage's complexity).
          Raise ValueError if they decrease.

    Return:
        {
            "total_stages": int,
            "stages": <validated stages list with an added "stage_number" key
                       (1-indexed) in each stage dict>,
            "complexity_range": {"min": int, "max": int},
            "all_features": <sorted list of ALL unique features across stages>,
            "estimated_duration_minutes": int
                -> 3 minutes per stage (simple heuristic)
        }
    """
    pass


# =============================================================================
# Exercise 14: Implement a Demo Feedback Collector
# Difficulty: Medium
# =============================================================================
class DemoFeedbackCollector:
    """Collect and analyze audience feedback during or after a demo.

    Implement:
        __init__(demo_name: str):
            Store demo_name, initialize empty list of feedback entries.

        add_feedback(rating: int, comment: str = "",
                     category: str = "general") -> dict:
            Validate: rating must be 1-5, category must be one of
            ["general", "ui", "performance", "accuracy", "feature_request"].
            Raise ValueError for invalid inputs.
            Create and store a feedback entry:
            {"id": <incremental 1-indexed>,
             "rating": int, "comment": str, "category": str,
             "timestamp": <ISO datetime>}
            Return the entry.

        get_average_rating() -> float:
            Return average rating rounded to 2 decimal places.
            Return 0.0 if no feedback.

        get_feedback_by_category(category: str) -> list[dict]:
            Return list of entries matching the category.

        get_summary() -> dict:
            Return {"demo_name": str,
                    "total_responses": int,
                    "average_rating": float,
                    "rating_distribution": {1: int, 2: int, 3: int, 4: int, 5: int},
                    "categories": {category: count},
                    "latest_comments": list of up to 5 most recent non-empty
                        comment strings (most recent first)}
    """

    def __init__(self, demo_name: str) -> None:
        raise NotImplementedError

    def add_feedback(
        self, rating: int, comment: str = "", category: str = "general"
    ) -> dict[str, Any]:
        raise NotImplementedError

    def get_average_rating(self) -> float:
        raise NotImplementedError

    def get_feedback_by_category(self, category: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    def get_summary(self) -> dict[str, Any]:
        raise NotImplementedError


# =============================================================================
# Exercise 15: Build a Demo Deployment Configuration Generator
# Difficulty: Hard
# =============================================================================
def generate_deployment_config(
    app_name: str,
    environment: Literal["development", "staging", "production"],
    provider: Literal["aws", "gcp", "azure"],
    features: list[str],
    scaling: dict[str, int] | None = None,
    env_vars: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Generate a deployment configuration for a demo application.

    This is what you hand to DevOps / the customer to deploy the POC.

    Args:
        app_name: Application name (non-empty, alphanumeric + hyphens only).
        environment: Target deployment environment.
        provider: Cloud provider.
        features: Non-empty list of feature names to enable.
        scaling: Optional dict with "min_instances" and "max_instances".
            Defaults: {"min_instances": 1, "max_instances": 3}
            Validate: min >= 1, max >= min.
        env_vars: Optional extra environment variables (key-value pairs).

    Validation:
        - app_name must match pattern: only lowercase letters, digits, hyphens;
          must start with a letter; length 3-63.
        - Raise ValueError for any validation failure.

    Return:
        {
            "config_version": "2.0",
            "app_name": str,
            "environment": str,
            "provider": str,
            "container": {
                "image": f"{app_name}:{environment}",
                "port": 8501,           (Streamlit default)
                "health_check": "/healthz"
            },
            "scaling": {
                "min_instances": int,
                "max_instances": int,
                "auto_scaling": True if environment != "development" else False,
            },
            "features": sorted(features),
            "environment_variables": {
                "APP_NAME": app_name,
                "ENVIRONMENT": environment,
                "LOG_LEVEL": "DEBUG" if environment == "development"
                             else "INFO" if environment == "staging"
                             else "WARNING",
                **<env_vars or {}>
            },
            "provider_config": {
                "aws":   {"region": "us-east-1", "service": "ECS"},
                "gcp":   {"region": "us-central1", "service": "Cloud Run"},
                "azure": {"region": "eastus", "service": "Container Apps"},
            }[provider],
            "generated_at": <ISO datetime>
        }
    """
    pass


# =============================================================================
# Main -- run all exercises
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Module 06: Rapid Prototyping & Demos - Exercise Tests")
    print("=" * 70)

    # --- Exercise 1 ---
    print("\n--- Exercise 1: Streamlit App Configuration ---")
    cfg = build_app_config("My Demo", "AI Assistant Demo")
    assert cfg["app_name"] == "My Demo"
    assert cfg["layout"] == "wide"
    assert cfg["config_version"] == "1.0"
    assert cfg["max_upload_mb"] == 200
    try:
        build_app_config("", "title")
        assert False, "Should have raised ValueError for empty app_name"
    except ValueError:
        pass
    try:
        build_app_config("app", "title", theme_primary_color="red")
        assert False, "Should have raised ValueError for bad color"
    except ValueError:
        pass
    print("  PASSED")

    # --- Exercise 2 ---
    print("\n--- Exercise 2: Chat Message Component ---")
    msg = ChatMessage(role=MessageRole.USER, content="Hello!")
    api_fmt = msg.to_api_format()
    assert api_fmt == {"role": "user", "content": "Hello!"}
    disp_fmt = msg.to_display_format()
    assert "timestamp" in disp_fmt
    assert "id" in disp_fmt
    print("  PASSED")

    # --- Exercise 3 ---
    print("\n--- Exercise 3: Demo Scenario Loader ---")
    sample_json = json.dumps([
        {"id": "s1", "title": "Greeting", "description": "Basic hello",
         "messages": [{"role": "user", "content": "Hi"}]},
        {"id": "", "title": "Bad", "description": "Empty id",
         "messages": []},
    ])
    scenarios = load_demo_scenarios(sample_json)
    assert len(scenarios) == 1
    assert scenarios[0]["message_count"] == 1
    assert "loaded_at" in scenarios[0]
    print("  PASSED")

    # --- Exercise 4 ---
    print("\n--- Exercise 4: Session State Manager ---")
    ssm = SessionStateManager()
    ssm.set("user", "Alice")
    assert ssm.get("user") == "Alice"
    assert ssm.get("missing", "default") == "default"
    ssm.delete("user")
    assert ssm.get("user") is None
    history = ssm.get_history()
    assert len(history) == 2  # set + delete
    ssm.reset()
    assert ssm.snapshot() == {}
    print("  PASSED")

    # --- Exercise 5 ---
    print("\n--- Exercise 5: File Upload Processor ---")
    result = process_upload("test.txt", b"Hello world", ["txt", "csv"])
    assert result["extension"] == "txt"
    assert result["size_bytes"] == 11
    assert result["content_type"] == "text/plain"
    assert "md5" in result
    try:
        process_upload("image.exe", b"data", ["txt"])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("  PASSED")

    # --- Exercise 6 ---
    print("\n--- Exercise 6: Demo Recording System ---")
    rec = DemoRecorder("test_demo")
    e1 = rec.record_event("user_input", {"text": "Hello"})
    assert e1["event_id"] == 1
    e2 = rec.record_event("api_response", {"text": "Hi there"})
    assert e2["event_id"] == 2
    assert len(rec.get_events("user_input")) == 1
    rec.stop()
    summary = rec.get_summary()
    assert summary["total_events"] == 2
    assert summary["is_recording"] is False
    try:
        rec.record_event("late", {})
        assert False, "Should have raised RuntimeError"
    except RuntimeError:
        pass
    print("  PASSED")

    # --- Exercise 7 ---
    print("\n--- Exercise 7: POC Requirements Checklist ---")
    reqs = [
        {"id": "R1", "title": "Auth", "status": "completed", "priority": "critical"},
        {"id": "R2", "title": "UI", "status": "in_progress", "priority": "high"},
        {"id": "R3", "title": "Bad", "status": "invalid_status", "priority": "low"},
    ]
    report = validate_poc_requirements(reqs)
    assert report["valid"] == 2
    assert len(report["invalid"]) == 1
    assert report["all_critical_done"] is True
    assert report["completion_pct"] == 50.0
    print("  PASSED")

    # --- Exercise 8 ---
    print("\n--- Exercise 8: Demo Data Generator ---")
    convos = generate_demo_conversations(2, turns_per_conversation=2)
    assert len(convos) == 2
    assert convos[0]["conversation_id"] == "conv_1"
    # system + 2*(user+assistant) = 5 messages
    assert len(convos[0]["messages"]) == 5
    convos_no_sys = generate_demo_conversations(1, turns_per_conversation=1,
                                                 include_system=False)
    assert len(convos_no_sys[0]["messages"]) == 2
    print("  PASSED")

    # --- Exercise 9 ---
    print("\n--- Exercise 9: Feature Flag System ---")
    ff = FeatureFlagManager()
    ff.register("streaming", enabled=True, description="Enable streaming")
    ff.register("dark_mode", enabled=False)
    assert ff.is_enabled("streaming") is True
    assert ff.toggle("dark_mode") is True
    assert ff.is_enabled("dark_mode") is True
    ff.disable("dark_mode")
    assert ff.is_enabled("dark_mode") is False
    enabled = ff.list_flags(only_enabled=True)
    assert "streaming" in enabled
    assert "dark_mode" not in enabled
    updated = ff.bulk_update({"streaming": False, "nonexistent": True})
    assert updated == {"streaming": False}
    print("  PASSED")

    # --- Exercise 10 ---
    print("\n--- Exercise 10: Demo Metrics Collector ---")
    mc = DemoMetricsCollector()
    for v in [100, 150, 200]:
        mc.record("latency_ms", v)
    stats = mc.get_stats("latency_ms")
    assert stats["count"] == 3
    assert stats["mean"] == 150.0
    assert stats["min"] == 100
    assert stats["max"] == 200
    assert mc.get_all_metric_names() == ["latency_ms"]
    mc.reset("latency_ms")
    try:
        mc.get_stats("latency_ms")
        assert False, "Should raise KeyError"
    except KeyError:
        pass
    print("  PASSED")

    # --- Exercise 11 ---
    print("\n--- Exercise 11: Customer Handoff Document ---")
    doc = generate_handoff_document(
        customer_name="Acme Corp",
        poc_title="AI Chatbot POC",
        features_demonstrated=[
            {"name": "Chat", "status": "working"},
            {"name": "RAG", "status": "working"},
        ],
        metrics={"avg_latency_ms": 120, "accuracy_pct": 95.5},
        next_steps=["Scale to production", "Add auth"],
    )
    assert doc["document_type"] == "poc_handoff"
    assert doc["ready_for_production"] is True
    assert doc["feature_summary"]["working"] == 2
    print("  PASSED")

    # --- Exercise 12 ---
    print("\n--- Exercise 12: Demo Fallback System ---")
    fb = DemoFallbackSystem()
    fb.add_fallback("greeting", "Hello! How can I help?")
    # Test live success
    result = fb.get_response("greeting", live_fn=lambda: "Live response!")
    assert result["source"] == "live"
    # Test live failure -> fallback
    def _failing_api():
        raise ConnectionError("API down")
    result = fb.get_response("greeting", live_fn=_failing_api)
    assert result["source"] == "fallback"
    assert result["used_count"] == 1
    # Test no fallback
    result = fb.get_response("unknown_key")
    assert result["source"] == "error"
    stats = fb.get_stats()
    assert stats["total_fallbacks"] == 1
    print("  PASSED")

    # --- Exercise 13 ---
    print("\n--- Exercise 13: Progressive Complexity Demo ---")
    stages = [
        {"name": "Basic", "description": "Simple chat", "complexity": 1,
         "features": ["chat"], "demo_script": "Show basic chat."},
        {"name": "Advanced", "description": "With RAG", "complexity": 3,
         "features": ["chat", "rag"], "demo_script": "Add retrieval."},
    ]
    demo = build_progressive_demo(stages)
    assert demo["total_stages"] == 2
    assert demo["stages"][0]["stage_number"] == 1
    assert demo["complexity_range"] == {"min": 1, "max": 3}
    assert demo["all_features"] == ["chat", "rag"]
    assert demo["estimated_duration_minutes"] == 6
    print("  PASSED")

    # --- Exercise 14 ---
    print("\n--- Exercise 14: Demo Feedback Collector ---")
    fc = DemoFeedbackCollector("AI Demo")
    fc.add_feedback(5, "Great demo!", "ui")
    fc.add_feedback(4, "Good accuracy", "accuracy")
    fc.add_feedback(3)
    summary = fc.get_summary()
    assert summary["total_responses"] == 3
    assert summary["average_rating"] == 4.0
    assert summary["rating_distribution"][5] == 1
    assert len(fc.get_feedback_by_category("ui")) == 1
    print("  PASSED")

    # --- Exercise 15 ---
    print("\n--- Exercise 15: Deployment Configuration ---")
    config = generate_deployment_config(
        app_name="my-demo-app",
        environment="staging",
        provider="aws",
        features=["chat", "rag"],
        env_vars={"API_KEY": "sk-test"},
    )
    assert config["config_version"] == "2.0"
    assert config["container"]["image"] == "my-demo-app:staging"
    assert config["scaling"]["auto_scaling"] is True
    assert config["environment_variables"]["LOG_LEVEL"] == "INFO"
    assert config["environment_variables"]["API_KEY"] == "sk-test"
    assert config["provider_config"]["region"] == "us-east-1"
    try:
        generate_deployment_config("BAD APP!", "staging", "aws", ["f"])
        assert False, "Should raise ValueError for invalid app_name"
    except ValueError:
        pass
    print("  PASSED")

    print("\n" + "=" * 70)
    print("ALL EXERCISES PASSED!")
    print("=" * 70)
