"""
Module 06: Rapid Prototyping & Demos - Solutions
==================================================
Complete solutions for all 15 exercises with detailed comments.

Target audience: Swift/iOS developers transitioning to AI/ML engineering roles.

Run this file to verify all solutions pass: `python solutions.py`
"""

from __future__ import annotations

import json
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Literal
from uuid import uuid4


# =============================================================================
# Exercise 1: Build a Streamlit App Configuration Model
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
    """Build a Streamlit-style app configuration dictionary."""
    # Validate inputs -- similar to a Swift init that throws
    if not app_name:
        raise ValueError("app_name must be non-empty")
    if not theme_primary_color.startswith("#") or len(theme_primary_color) != 7:
        raise ValueError(
            f"theme_primary_color must be '#' followed by 6 hex chars, "
            f"got: {theme_primary_color!r}"
        )
    if max_upload_mb <= 0:
        raise ValueError(f"max_upload_mb must be > 0, got {max_upload_mb}")

    # Build and return the config dict.
    # In a production Streamlit app, this would be passed to
    # st.set_page_config() and stored in st.session_state.
    return {
        "app_name": app_name,
        "page_title": page_title,
        "page_icon": page_icon,
        "layout": layout,
        "sidebar_state": sidebar_state,
        "theme_primary_color": theme_primary_color,
        "show_footer": show_footer,
        "max_upload_mb": max_upload_mb,
        "config_version": "1.0",
    }


# =============================================================================
# Exercise 2: Implement a Chat Message Component
# =============================================================================
class MessageRole(str, Enum):
    """Roles in a chat conversation.

    Using str as a mixin so that MessageRole.USER == "user" and
    .value gives us a plain string -- handy for JSON serialization.
    In Swift you'd use `enum MessageRole: String, Codable`.
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ChatMessage:
    """Data model for a single chat message displayed in a demo UI.

    We use a dataclass rather than a Pydantic model here because this is
    a lightweight, in-memory UI component -- no request validation needed.
    In Swift this would be a plain struct.
    """
    role: MessageRole
    content: str
    # default_factory ensures every instance gets its own datetime / uuid
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: uuid4().hex)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_api_format(self) -> dict[str, str]:
        """Minimal format for sending to an LLM API (role + content only).

        Similar to conforming to a simpler Encodable protocol in Swift
        that only encodes a subset of properties.
        """
        return {"role": self.role.value, "content": self.content}

    def to_display_format(self) -> dict[str, str]:
        """Richer format for rendering in a chat UI.

        Includes the timestamp and message id for display / debugging.
        """
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "id": self.message_id,
        }


# =============================================================================
# Exercise 3: Build a Demo Scenario Loader
# =============================================================================
def load_demo_scenarios(json_string: str) -> list[dict[str, Any]]:
    """Parse and validate demo scenarios from a JSON string.

    Gracefully skips invalid scenarios so a single bad entry doesn't
    break the entire demo.  This is a common pattern when loading
    user-contributed or customer-provided data.
    """
    # Step 1: Parse -- let JSONDecodeError propagate
    raw: list[dict[str, Any]] = json.loads(json_string)

    valid_scenarios: list[dict[str, Any]] = []

    for scenario in raw:
        # Step 2: Validate required keys and types
        if not isinstance(scenario, dict):
            continue

        sid = scenario.get("id", "")
        title = scenario.get("title", "")
        description = scenario.get("description")
        messages = scenario.get("messages")

        # id and title must be non-empty strings
        if not isinstance(sid, str) or not sid:
            continue
        if not isinstance(title, str) or not title:
            continue
        if description is None:
            continue
        if not isinstance(messages, list):
            continue

        # Each message must have role and content
        messages_valid = True
        for msg in messages:
            if not isinstance(msg, dict):
                messages_valid = False
                break
            if "role" not in msg or "content" not in msg:
                messages_valid = False
                break
        if not messages_valid:
            continue

        # Step 3-4: Enrich the scenario
        scenario["message_count"] = len(messages)
        scenario["loaded_at"] = datetime.now().isoformat()

        valid_scenarios.append(scenario)

    return valid_scenarios


# =============================================================================
# Exercise 4: Implement a Session State Manager
# =============================================================================
class SessionStateManager:
    """Manages session state for a demo app.

    This mirrors Streamlit's st.session_state with the addition of a
    full change history -- useful for debugging during demos.
    """

    def __init__(self) -> None:
        self._state: dict[str, Any] = {}
        self._history: list[dict[str, Any]] = []

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value by key, returning default if not found."""
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Store a key-value pair and log the change."""
        self._state[key] = value
        self._history.append({
            "action": "set",
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat(),
        })

    def delete(self, key: str) -> None:
        """Remove a key (no error if missing) and log the deletion."""
        self._state.pop(key, None)  # pop with default avoids KeyError
        self._history.append({
            "action": "delete",
            "key": key,
            "timestamp": datetime.now().isoformat(),
        })

    def get_history(self) -> list[dict[str, Any]]:
        """Return a copy of the full change history."""
        return list(self._history)  # shallow copy prevents external mutation

    def reset(self) -> None:
        """Clear all state and history, logging the reset itself."""
        self._state.clear()
        self._history.clear()
        self._history.append({
            "action": "reset",
            "timestamp": datetime.now().isoformat(),
        })

    def snapshot(self) -> dict[str, Any]:
        """Return a shallow copy of the current state dictionary."""
        return dict(self._state)


# =============================================================================
# Exercise 5: Build a File Upload Processor
# =============================================================================
def process_upload(
    filename: str,
    content_bytes: bytes,
    allowed_extensions: list[str] | None = None,
    max_size_bytes: int = 10 * 1024 * 1024,
) -> dict[str, Any]:
    """Validate and process a simulated file upload.

    This is the kind of utility you build early in any demo that accepts
    user documents (PDFs, CSVs, images, etc.).
    """
    # 1. Extract extension
    if "." in filename:
        extension = filename.rsplit(".", 1)[-1].lower()
    else:
        extension = ""

    # 2. Check allowed extensions
    if allowed_extensions is not None and extension not in allowed_extensions:
        raise ValueError(f"Unsupported file type: {extension}")

    # 3. Check size
    size = len(content_bytes)
    if size > max_size_bytes:
        raise ValueError(f"File too large: {size} bytes (max {max_size_bytes})")

    # 4. Compute MD5 hash for deduplication
    md5 = hashlib.md5(content_bytes).hexdigest()

    # 5. Human-readable size
    if size < 1024:
        size_display = f"{size} B"
    elif size < 1024 * 1024:
        size_display = f"{size / 1024:.1f} KB"
    else:
        size_display = f"{size / (1024 * 1024):.2f} MB"

    # 6. Guess MIME type from extension
    mime_map = {
        "txt": "text/plain",
        "csv": "text/csv",
        "json": "application/json",
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
    }
    content_type = mime_map.get(extension, "application/octet-stream")

    return {
        "filename": filename,
        "extension": extension,
        "size_bytes": size,
        "size_display": size_display,
        "md5": md5,
        "content_type": content_type,
        "processed_at": datetime.now().isoformat(),
    }


# =============================================================================
# Exercise 6: Implement a Demo Recording System
# =============================================================================
class DemoRecorder:
    """Capture demo interactions for replay and analysis.

    Think of this as a specialized event logger.  During a customer demo,
    you record every user input and API response so you can:
      - Replay the demo later for stakeholders who missed it
      - Analyze which parts of the demo were most engaging
      - Debug issues that occurred during the demo

    Similar to how you might use OSLog + signposts in iOS for tracing.
    """

    def __init__(self, demo_name: str) -> None:
        self.demo_name = demo_name
        self.start_time = datetime.now()
        self._stop_time: datetime | None = None
        self._events: list[dict[str, Any]] = []
        self._is_recording = True

    def record_event(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Record a single event.  Raises RuntimeError if recording stopped."""
        if not self._is_recording:
            raise RuntimeError("Recording stopped")

        event = {
            "event_id": len(self._events) + 1,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        self._events.append(event)
        return event

    def stop(self) -> None:
        """Stop the recording and capture the stop time."""
        self._is_recording = False
        self._stop_time = datetime.now()

    def get_events(self, event_type: str | None = None) -> list[dict[str, Any]]:
        """Return events, optionally filtered by type."""
        if event_type is None:
            return list(self._events)
        return [e for e in self._events if e["event_type"] == event_type]

    def get_summary(self) -> dict[str, Any]:
        """Return a summary of the recording session."""
        # Count events by type
        type_counts: dict[str, int] = {}
        for event in self._events:
            et = event["event_type"]
            type_counts[et] = type_counts.get(et, 0) + 1

        # Duration is 0.0 if still recording
        if self._stop_time is not None:
            duration = (self._stop_time - self.start_time).total_seconds()
        else:
            duration = 0.0

        return {
            "demo_name": self.demo_name,
            "total_events": len(self._events),
            "event_types": type_counts,
            "duration_seconds": duration,
            "is_recording": self._is_recording,
        }


# =============================================================================
# Exercise 7: Build a POC Requirements Checklist Validator
# =============================================================================
def validate_poc_requirements(
    requirements: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate POC requirements and produce a readiness report.

    In a customer engagement, you track requirements as they move from
    "not_started" -> "in_progress" -> "completed" (or "blocked").
    This function validates the data and produces a summary the account
    team can share with the customer.
    """
    valid_statuses = {"not_started", "in_progress", "completed", "blocked"}
    valid_priorities = {"critical", "high", "medium", "low"}

    valid_reqs: list[dict[str, Any]] = []
    invalid_entries: list[dict[str, str]] = []

    for req in requirements:
        req_id = req.get("id", "unknown")

        # Check required keys
        if not req.get("id"):
            invalid_entries.append({"id": "unknown", "error": "Missing or empty id"})
            continue
        if not req.get("title"):
            invalid_entries.append({"id": req_id, "error": "Missing or empty title"})
            continue

        status = req.get("status")
        if status not in valid_statuses:
            invalid_entries.append({
                "id": req_id,
                "error": f"Invalid status: {status}",
            })
            continue

        priority = req.get("priority")
        if priority not in valid_priorities:
            invalid_entries.append({
                "id": req_id,
                "error": f"Invalid priority: {priority}",
            })
            continue

        # Apply default owner
        req.setdefault("owner", "unassigned")
        valid_reqs.append(req)

    # Group by status
    by_status = {"not_started": 0, "in_progress": 0, "completed": 0, "blocked": 0}
    for req in valid_reqs:
        by_status[req["status"]] += 1

    # Readiness checks
    critical_reqs = [r for r in valid_reqs if r["priority"] == "critical"]
    all_critical_done = all(r["status"] == "completed" for r in critical_reqs)

    total_valid = len(valid_reqs)
    if total_valid > 0:
        completion_pct = round((by_status["completed"] / total_valid) * 100, 1)
    else:
        completion_pct = 0.0

    blockers = [r["id"] for r in valid_reqs if r["status"] == "blocked"]

    return {
        "total": len(requirements),
        "valid": total_valid,
        "invalid": invalid_entries,
        "by_status": by_status,
        "all_critical_done": all_critical_done,
        "completion_pct": completion_pct,
        "blockers": blockers,
    }


# =============================================================================
# Exercise 8: Implement a Demo Data Generator
# =============================================================================
def generate_demo_conversations(
    num_conversations: int,
    turns_per_conversation: int = 3,
    topics: list[str] | None = None,
    include_system: bool = True,
) -> list[dict[str, Any]]:
    """Generate synthetic demo conversations.

    When demoing an AI assistant you often need realistic-looking data.
    Using real customer data is a privacy concern, so we generate synthetic
    conversations that are topically relevant.

    This is analogous to generating mock data in XCTest / SwiftUI previews.
    """
    if num_conversations < 1:
        raise ValueError(f"num_conversations must be >= 1, got {num_conversations}")
    if turns_per_conversation < 1:
        raise ValueError(
            f"turns_per_conversation must be >= 1, got {turns_per_conversation}"
        )

    # Default topics if none provided
    if topics is None:
        topics = ["product inquiry", "technical support", "billing"]

    conversations: list[dict[str, Any]] = []

    for i in range(num_conversations):
        # Cycle through topics using modulo
        topic = topics[i % len(topics)]
        messages: list[dict[str, str]] = []

        # Optional system message
        if include_system:
            messages.append({
                "role": "system",
                "content": f"You are a helpful assistant specializing in {topic}.",
            })

        # Generate user/assistant turn pairs
        for turn in range(1, turns_per_conversation + 1):
            messages.append({
                "role": "user",
                "content": f"User question {turn} about {topic}",
            })
            messages.append({
                "role": "assistant",
                "content": (
                    f"Here's helpful information about {topic} "
                    f"for question {turn}."
                ),
            })

        conversations.append({
            "conversation_id": f"conv_{i + 1}",
            "topic": topic,
            "messages": messages,
            "created_at": datetime.now().isoformat(),
        })

    return conversations


# =============================================================================
# Exercise 9: Build a Feature Flag System for Demos
# =============================================================================
class FeatureFlagManager:
    """Manage feature flags for controlling demo behavior at runtime.

    Feature flags let you progressively reveal capabilities during a demo
    without restarting or redeploying.  For example, you might start with
    basic chat, then toggle on "streaming", then "tool_use".

    This is analogous to using UserDefaults-backed feature flags in an
    iOS app, or LaunchDarkly in a server-side context.
    """

    def __init__(self) -> None:
        self._flags: dict[str, dict[str, Any]] = {}

    def register(self, name: str, enabled: bool = False, description: str = "") -> None:
        """Register a new feature flag.  Raises ValueError if duplicate."""
        if name in self._flags:
            raise ValueError(f"Flag already exists: {name}")
        self._flags[name] = {
            "enabled": enabled,
            "description": description,
            "created_at": datetime.now().isoformat(),
        }

    def is_enabled(self, name: str) -> bool:
        """Check if a flag is enabled.  Raises KeyError if missing."""
        if name not in self._flags:
            raise KeyError(f"Unknown flag: {name}")
        return self._flags[name]["enabled"]

    def toggle(self, name: str) -> bool:
        """Flip the flag and return the new value."""
        if name not in self._flags:
            raise KeyError(f"Unknown flag: {name}")
        self._flags[name]["enabled"] = not self._flags[name]["enabled"]
        return self._flags[name]["enabled"]

    def enable(self, name: str) -> None:
        """Explicitly enable a flag."""
        if name not in self._flags:
            raise KeyError(f"Unknown flag: {name}")
        self._flags[name]["enabled"] = True

    def disable(self, name: str) -> None:
        """Explicitly disable a flag."""
        if name not in self._flags:
            raise KeyError(f"Unknown flag: {name}")
        self._flags[name]["enabled"] = False

    def list_flags(self, only_enabled: bool = False) -> dict[str, dict[str, Any]]:
        """Return all flags, optionally filtering to enabled-only."""
        if only_enabled:
            return {
                name: dict(data)
                for name, data in self._flags.items()
                if data["enabled"]
            }
        return {name: dict(data) for name, data in self._flags.items()}

    def bulk_update(self, updates: dict[str, bool]) -> dict[str, bool]:
        """Update multiple flags.  Skip names that do not exist.

        Returns a dict of name -> new_value for flags that were updated.
        """
        result: dict[str, bool] = {}
        for name, enabled in updates.items():
            if name in self._flags:
                self._flags[name]["enabled"] = enabled
                result[name] = enabled
        return result


# =============================================================================
# Exercise 10: Implement a Demo Metrics Collector
# =============================================================================
class DemoMetricsCollector:
    """Collect and aggregate metrics during a demo run.

    During a live demo you might show customers:
      - Average latency per request
      - Token counts (input vs output)
      - Cost estimates

    This collector stores raw values and computes stats on demand.
    Similar to using MetricKit or custom analytics in an iOS app.
    """

    def __init__(self) -> None:
        self._metrics: dict[str, list[float]] = {}

    def record(self, metric_name: str, value: float) -> None:
        """Append a value to the named metric, creating it if needed."""
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        self._metrics[metric_name].append(value)

    def get_stats(self, metric_name: str) -> dict[str, Any]:
        """Compute summary statistics for a metric.  Raises KeyError if missing."""
        if metric_name not in self._metrics:
            raise KeyError(f"Unknown metric: {metric_name}")
        values = self._metrics[metric_name]
        return {
            "count": len(values),
            "sum": sum(values),
            "mean": round(sum(values) / len(values), 4),
            "min": min(values),
            "max": max(values),
        }

    def get_all_metric_names(self) -> list[str]:
        """Return a sorted list of all recorded metric names."""
        return sorted(self._metrics.keys())

    def reset(self, metric_name: str | None = None) -> None:
        """Clear a specific metric or all metrics."""
        if metric_name is not None:
            if metric_name not in self._metrics:
                raise KeyError(f"Unknown metric: {metric_name}")
            del self._metrics[metric_name]
        else:
            self._metrics.clear()

    def export(self) -> dict[str, dict[str, Any]]:
        """Export stats for all metrics as a nested dict."""
        return {name: self.get_stats(name) for name in self._metrics}


# =============================================================================
# Exercise 11: Build a Customer Handoff Document Generator
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

    This is the deliverable you produce at the end of a customer engagement.
    It summarises what was demonstrated, what metrics were achieved, and
    what comes next.  The customer's engineering team uses it to plan
    the production implementation.
    """
    # --- Validation ---
    if not customer_name or not isinstance(customer_name, str):
        raise ValueError("customer_name must be a non-empty string")
    if not poc_title or not isinstance(poc_title, str):
        raise ValueError("poc_title must be a non-empty string")
    if not features_demonstrated:
        raise ValueError("features_demonstrated must be non-empty")
    if not next_steps:
        raise ValueError("next_steps must be non-empty")

    valid_feature_statuses = {"working", "partial", "not_demonstrated"}
    for feat in features_demonstrated:
        if "name" not in feat or "status" not in feat:
            raise ValueError(
                f"Each feature must have 'name' and 'status' keys, got: {feat}"
            )
        if feat["status"] not in valid_feature_statuses:
            raise ValueError(
                f"Invalid feature status: {feat['status']}. "
                f"Must be one of {valid_feature_statuses}"
            )

    # --- Build feature summary ---
    feature_summary = {
        "total": len(features_demonstrated),
        "working": sum(1 for f in features_demonstrated if f["status"] == "working"),
        "partial": sum(1 for f in features_demonstrated if f["status"] == "partial"),
        "not_demonstrated": sum(
            1 for f in features_demonstrated if f["status"] == "not_demonstrated"
        ),
    }

    # Ready for production only if every feature is working
    ready = all(f["status"] == "working" for f in features_demonstrated)

    return {
        "document_type": "poc_handoff",
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "customer": customer_name,
        "poc_title": poc_title,
        "features": features_demonstrated,
        "feature_summary": feature_summary,
        "metrics": metrics,
        "next_steps": next_steps,
        "technical_notes": technical_notes or [],
        "ready_for_production": ready,
    }


# =============================================================================
# Exercise 12: Implement a Demo Fallback System
# =============================================================================
class DemoFallbackSystem:
    """Provide pre-cached responses when a live API is unavailable.

    This is a critical pattern for live demos.  Network failures,
    rate limits, and API outages can all derail a demo.  By pre-caching
    responses for your key scenarios, you ensure the demo always works.

    The pattern: try live first, fall back to cache, report an error
    only if both fail.

    Similar to a caching layer in an iOS app (NSCache / URLCache).
    """

    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}

    def add_fallback(self, key: str, response: Any) -> None:
        """Store a cached response.  Overwrites existing entries."""
        self._cache[key] = {
            "response": response,
            "used_count": 0,
            "added_at": datetime.now().isoformat(),
        }

    def get_response(self, key: str, live_fn: Any = None) -> dict[str, Any]:
        """Try live_fn first, fall back to cache, then report error.

        The three-tier approach:
          1. Live (if live_fn provided and succeeds)
          2. Cached fallback (if key exists in cache)
          3. Error (no fallback available)
        """
        # Tier 1: Try the live function
        if live_fn is not None:
            try:
                result = live_fn()
                return {"source": "live", "response": result}
            except Exception:
                pass  # Fall through to cache

        # Tier 2: Use the cached fallback
        if key in self._cache:
            self._cache[key]["used_count"] += 1
            return {
                "source": "fallback",
                "response": self._cache[key]["response"],
                "used_count": self._cache[key]["used_count"],
            }

        # Tier 3: No fallback available
        return {
            "source": "error",
            "response": f"No fallback available for: {key}",
        }

    def list_fallbacks(self) -> dict[str, dict[str, Any]]:
        """Return a copy of the cache for inspection."""
        return {key: dict(val) for key, val in self._cache.items()}

    def get_stats(self) -> dict[str, Any]:
        """Return aggregate stats about the fallback cache."""
        total = len(self._cache)
        total_used = sum(entry["used_count"] for entry in self._cache.values())

        # Find the most-used fallback
        most_used: str | None = None
        if self._cache:
            max_count = max(entry["used_count"] for entry in self._cache.values())
            if max_count > 0:
                # Find the first key with the max count
                for key, entry in self._cache.items():
                    if entry["used_count"] == max_count:
                        most_used = key
                        break

        return {
            "total_fallbacks": total,
            "total_used": total_used,
            "most_used": most_used,
        }


# =============================================================================
# Exercise 13: Build a Progressive Complexity Demo Flow
# =============================================================================
def build_progressive_demo(
    stages: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a progressive-disclosure demo flow.

    The progressive demo pattern is essential for customer-facing
    presentations.  You start with the simplest possible example,
    then add complexity one layer at a time.  This lets the audience
    build intuition before you show advanced features.

    Think of it like an onboarding flow in an iOS app -- each screen
    introduces one new concept.
    """
    if not stages:
        raise ValueError("stages must be non-empty")

    validated_stages: list[dict[str, Any]] = []
    all_features: set[str] = set()
    prev_complexity: int | None = None

    for idx, stage in enumerate(stages):
        # Validate required keys
        for key in ("name", "description", "complexity", "features", "demo_script"):
            if key not in stage:
                raise ValueError(f"Stage {idx + 1} missing required key: {key}")

        # Validate types and ranges
        if not isinstance(stage["name"], str):
            raise ValueError(f"Stage {idx + 1}: 'name' must be a string")
        if not isinstance(stage["description"], str):
            raise ValueError(f"Stage {idx + 1}: 'description' must be a string")
        if not isinstance(stage["complexity"], int) or not (1 <= stage["complexity"] <= 5):
            raise ValueError(
                f"Stage {idx + 1}: 'complexity' must be an int between 1 and 5"
            )
        if not isinstance(stage["features"], list) or len(stage["features"]) == 0:
            raise ValueError(
                f"Stage {idx + 1}: 'features' must be a non-empty list"
            )
        if not isinstance(stage["demo_script"], str):
            raise ValueError(f"Stage {idx + 1}: 'demo_script' must be a string")

        # Complexity must be non-decreasing
        if prev_complexity is not None and stage["complexity"] < prev_complexity:
            raise ValueError(
                f"Stage {idx + 1}: complexity ({stage['complexity']}) is less "
                f"than previous stage ({prev_complexity}). "
                f"Stages must have non-decreasing complexity."
            )
        prev_complexity = stage["complexity"]

        # Add stage_number and collect features
        enriched = dict(stage)
        enriched["stage_number"] = idx + 1
        validated_stages.append(enriched)
        all_features.update(stage["features"])

    complexities = [s["complexity"] for s in validated_stages]

    return {
        "total_stages": len(validated_stages),
        "stages": validated_stages,
        "complexity_range": {"min": min(complexities), "max": max(complexities)},
        "all_features": sorted(all_features),
        "estimated_duration_minutes": len(validated_stages) * 3,
    }


# =============================================================================
# Exercise 14: Implement a Demo Feedback Collector
# =============================================================================
class DemoFeedbackCollector:
    """Collect and analyze audience feedback during or after a demo.

    After showing a customer demo, you typically ask for structured feedback.
    This helps you prioritize which features to build out and identify
    areas where the demo fell short.

    Similar to an in-app rating prompt (SKStoreReviewController) but
    with richer data collection.
    """

    VALID_CATEGORIES = {"general", "ui", "performance", "accuracy", "feature_request"}

    def __init__(self, demo_name: str) -> None:
        self.demo_name = demo_name
        self._feedback: list[dict[str, Any]] = []

    def add_feedback(
        self, rating: int, comment: str = "", category: str = "general"
    ) -> dict[str, Any]:
        """Add a feedback entry after validation."""
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValueError(f"Rating must be 1-5, got: {rating}")
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category: {category}. "
                f"Must be one of {self.VALID_CATEGORIES}"
            )

        entry = {
            "id": len(self._feedback) + 1,
            "rating": rating,
            "comment": comment,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }
        self._feedback.append(entry)
        return entry

    def get_average_rating(self) -> float:
        """Return the average rating, or 0.0 if no feedback."""
        if not self._feedback:
            return 0.0
        total = sum(f["rating"] for f in self._feedback)
        return round(total / len(self._feedback), 2)

    def get_feedback_by_category(self, category: str) -> list[dict[str, Any]]:
        """Return all feedback entries matching the given category."""
        return [f for f in self._feedback if f["category"] == category]

    def get_summary(self) -> dict[str, Any]:
        """Return a comprehensive summary of all collected feedback."""
        # Rating distribution (1-5)
        distribution = {i: 0 for i in range(1, 6)}
        for f in self._feedback:
            distribution[f["rating"]] += 1

        # Category counts
        categories: dict[str, int] = {}
        for f in self._feedback:
            cat = f["category"]
            categories[cat] = categories.get(cat, 0) + 1

        # Latest non-empty comments (up to 5, most recent first)
        comments_with_text = [
            f["comment"] for f in reversed(self._feedback) if f["comment"]
        ]
        latest_comments = comments_with_text[:5]

        return {
            "demo_name": self.demo_name,
            "total_responses": len(self._feedback),
            "average_rating": self.get_average_rating(),
            "rating_distribution": distribution,
            "categories": categories,
            "latest_comments": latest_comments,
        }


# =============================================================================
# Exercise 15: Build a Demo Deployment Configuration Generator
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

    After a successful POC, you need to deploy it somewhere.  This function
    generates a configuration dict that can be serialised to YAML/JSON
    and fed to a CI/CD pipeline (Terraform, Docker Compose, Cloud Run, etc.).

    This is the deployment equivalent of generating an Xcode build
    configuration programmatically.
    """
    # --- Validate app_name ---
    # Must be lowercase letters, digits, hyphens; start with letter; 3-63 chars
    pattern = r"^[a-z][a-z0-9\-]{2,62}$"
    if not re.match(pattern, app_name):
        raise ValueError(
            f"Invalid app_name: '{app_name}'. Must be 3-63 characters, "
            f"lowercase letters/digits/hyphens, starting with a letter."
        )

    # --- Validate features ---
    if not features:
        raise ValueError("features must be non-empty")

    # --- Resolve scaling ---
    if scaling is None:
        scaling = {"min_instances": 1, "max_instances": 3}
    min_inst = scaling.get("min_instances", 1)
    max_inst = scaling.get("max_instances", 3)
    if min_inst < 1:
        raise ValueError(f"min_instances must be >= 1, got {min_inst}")
    if max_inst < min_inst:
        raise ValueError(
            f"max_instances ({max_inst}) must be >= min_instances ({min_inst})"
        )

    # --- Determine log level by environment ---
    log_levels = {
        "development": "DEBUG",
        "staging": "INFO",
        "production": "WARNING",
    }

    # --- Provider-specific configuration ---
    provider_configs = {
        "aws": {"region": "us-east-1", "service": "ECS"},
        "gcp": {"region": "us-central1", "service": "Cloud Run"},
        "azure": {"region": "eastus", "service": "Container Apps"},
    }

    # --- Build environment variables ---
    environment_variables = {
        "APP_NAME": app_name,
        "ENVIRONMENT": environment,
        "LOG_LEVEL": log_levels[environment],
    }
    if env_vars:
        environment_variables.update(env_vars)

    return {
        "config_version": "2.0",
        "app_name": app_name,
        "environment": environment,
        "provider": provider,
        "container": {
            "image": f"{app_name}:{environment}",
            "port": 8501,
            "health_check": "/healthz",
        },
        "scaling": {
            "min_instances": min_inst,
            "max_instances": max_inst,
            "auto_scaling": environment != "development",
        },
        "features": sorted(features),
        "environment_variables": environment_variables,
        "provider_config": provider_configs[provider],
        "generated_at": datetime.now().isoformat(),
    }


# =============================================================================
# Main -- run all solution tests
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Module 06: Rapid Prototyping & Demos - Solution Tests")
    print("=" * 70)

    # --- Exercise 1 ---
    print("\n--- Exercise 1: Streamlit App Configuration ---")
    cfg = build_app_config("My Demo", "AI Assistant Demo")
    assert cfg["app_name"] == "My Demo"
    assert cfg["page_title"] == "AI Assistant Demo"
    assert cfg["layout"] == "wide"
    assert cfg["sidebar_state"] == "expanded"
    assert cfg["config_version"] == "1.0"
    assert cfg["max_upload_mb"] == 200
    assert cfg["show_footer"] is False

    # Custom settings
    cfg2 = build_app_config(
        "Custom", "Custom App", layout="centered",
        theme_primary_color="#00FF00", max_upload_mb=50,
    )
    assert cfg2["layout"] == "centered"
    assert cfg2["theme_primary_color"] == "#00FF00"
    assert cfg2["max_upload_mb"] == 50

    # Validation tests
    try:
        build_app_config("", "title")
        assert False, "Should raise ValueError for empty app_name"
    except ValueError as e:
        assert "non-empty" in str(e)

    try:
        build_app_config("app", "title", theme_primary_color="red")
        assert False, "Should raise ValueError for bad color"
    except ValueError as e:
        assert "#" in str(e)

    try:
        build_app_config("app", "title", max_upload_mb=0)
        assert False, "Should raise ValueError for max_upload_mb=0"
    except ValueError:
        pass

    print("  PASSED")

    # --- Exercise 2 ---
    print("\n--- Exercise 2: Chat Message Component ---")
    msg = ChatMessage(role=MessageRole.USER, content="Hello!")
    api_fmt = msg.to_api_format()
    assert api_fmt == {"role": "user", "content": "Hello!"}
    assert "timestamp" not in api_fmt  # API format is minimal

    disp_fmt = msg.to_display_format()
    assert disp_fmt["role"] == "user"
    assert "timestamp" in disp_fmt
    assert "id" in disp_fmt
    assert len(disp_fmt["id"]) == 32  # uuid4 hex is 32 chars

    # System message
    sys_msg = ChatMessage(role=MessageRole.SYSTEM, content="Be helpful.")
    assert sys_msg.to_api_format()["role"] == "system"

    # Two messages should have different IDs
    msg2 = ChatMessage(role=MessageRole.USER, content="World!")
    assert msg.message_id != msg2.message_id
    print("  PASSED")

    # --- Exercise 3 ---
    print("\n--- Exercise 3: Demo Scenario Loader ---")
    sample_json = json.dumps([
        {
            "id": "s1", "title": "Greeting", "description": "Basic hello",
            "messages": [{"role": "user", "content": "Hi"}],
        },
        {"id": "", "title": "Bad", "description": "Empty id", "messages": []},
        {"id": "s2", "title": "No messages", "description": "Test"},
        {"id": "s3", "title": "Bad msg", "description": "D",
         "messages": [{"role": "user"}]},  # missing "content"
    ])
    scenarios = load_demo_scenarios(sample_json)
    assert len(scenarios) == 1, f"Expected 1 valid scenario, got {len(scenarios)}"
    assert scenarios[0]["id"] == "s1"
    assert scenarios[0]["message_count"] == 1
    assert "loaded_at" in scenarios[0]

    # Invalid JSON should raise
    try:
        load_demo_scenarios("not json")
        assert False, "Should raise JSONDecodeError"
    except json.JSONDecodeError:
        pass

    print("  PASSED")

    # --- Exercise 4 ---
    print("\n--- Exercise 4: Session State Manager ---")
    ssm = SessionStateManager()

    # Set and get
    ssm.set("user", "Alice")
    assert ssm.get("user") == "Alice"
    assert ssm.get("missing") is None
    assert ssm.get("missing", "default") == "default"

    # Overwrite
    ssm.set("user", "Bob")
    assert ssm.get("user") == "Bob"

    # Delete
    ssm.delete("user")
    assert ssm.get("user") is None

    # Delete non-existent (no error)
    ssm.delete("nonexistent")

    # History
    history = ssm.get_history()
    assert len(history) == 4  # set, set, delete, delete
    assert history[0]["action"] == "set"
    assert history[2]["action"] == "delete"

    # Snapshot
    ssm.set("key1", "val1")
    ssm.set("key2", "val2")
    snap = ssm.snapshot()
    assert snap == {"key1": "val1", "key2": "val2"}
    snap["key1"] = "modified"
    assert ssm.get("key1") == "val1"  # Original unchanged

    # Reset
    ssm.reset()
    assert ssm.snapshot() == {}
    reset_history = ssm.get_history()
    assert len(reset_history) == 1
    assert reset_history[0]["action"] == "reset"
    print("  PASSED")

    # --- Exercise 5 ---
    print("\n--- Exercise 5: File Upload Processor ---")
    result = process_upload("test.txt", b"Hello world", ["txt", "csv"])
    assert result["filename"] == "test.txt"
    assert result["extension"] == "txt"
    assert result["size_bytes"] == 11
    assert result["size_display"] == "11 B"
    assert result["content_type"] == "text/plain"
    assert "md5" in result
    assert "processed_at" in result

    # Larger file size display
    result_kb = process_upload("data.csv", b"x" * 2048)
    assert "KB" in result_kb["size_display"]

    result_mb = process_upload("big.pdf", b"x" * (2 * 1024 * 1024))
    assert "MB" in result_mb["size_display"]

    # No extension
    result_noext = process_upload("README", b"content")
    assert result_noext["extension"] == ""
    assert result_noext["content_type"] == "application/octet-stream"

    # Unsupported type
    try:
        process_upload("image.exe", b"data", ["txt"])
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Unsupported" in str(e)

    # Too large
    try:
        process_upload("big.txt", b"x" * 100, max_size_bytes=50)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "too large" in str(e).lower()

    print("  PASSED")

    # --- Exercise 6 ---
    print("\n--- Exercise 6: Demo Recording System ---")
    rec = DemoRecorder("test_demo")
    e1 = rec.record_event("user_input", {"text": "Hello"})
    assert e1["event_id"] == 1
    assert e1["event_type"] == "user_input"

    e2 = rec.record_event("api_response", {"text": "Hi there"})
    assert e2["event_id"] == 2

    e3 = rec.record_event("user_input", {"text": "Tell me more"})
    assert e3["event_id"] == 3

    # Filter by type
    user_events = rec.get_events("user_input")
    assert len(user_events) == 2
    all_events = rec.get_events()
    assert len(all_events) == 3

    # Stop and check summary
    rec.stop()
    summary = rec.get_summary()
    assert summary["demo_name"] == "test_demo"
    assert summary["total_events"] == 3
    assert summary["event_types"] == {"user_input": 2, "api_response": 1}
    assert summary["is_recording"] is False
    assert summary["duration_seconds"] > 0

    # Cannot record after stopping
    try:
        rec.record_event("late_event", {})
        assert False, "Should raise RuntimeError"
    except RuntimeError as e:
        assert "stopped" in str(e).lower()

    print("  PASSED")

    # --- Exercise 7 ---
    print("\n--- Exercise 7: POC Requirements Checklist ---")
    reqs = [
        {"id": "R1", "title": "Auth", "status": "completed", "priority": "critical"},
        {"id": "R2", "title": "UI", "status": "in_progress", "priority": "high"},
        {"id": "R3", "title": "API", "status": "blocked", "priority": "medium"},
        {"id": "R4", "title": "Bad", "status": "invalid_status", "priority": "low"},
        {"title": "No ID", "status": "completed", "priority": "low"},
    ]
    report = validate_poc_requirements(reqs)
    assert report["total"] == 5
    assert report["valid"] == 3
    assert len(report["invalid"]) == 2
    assert report["by_status"]["completed"] == 1
    assert report["by_status"]["blocked"] == 1
    assert report["all_critical_done"] is True
    assert report["completion_pct"] == 33.3
    assert report["blockers"] == ["R3"]

    # No critical requirements means all_critical_done is True (vacuously)
    report2 = validate_poc_requirements([
        {"id": "R1", "title": "X", "status": "in_progress", "priority": "low"},
    ])
    assert report2["all_critical_done"] is True
    print("  PASSED")

    # --- Exercise 8 ---
    print("\n--- Exercise 8: Demo Data Generator ---")
    convos = generate_demo_conversations(3, turns_per_conversation=2)
    assert len(convos) == 3
    assert convos[0]["conversation_id"] == "conv_1"
    assert convos[0]["topic"] == "product inquiry"
    assert convos[1]["topic"] == "technical support"
    assert convos[2]["topic"] == "billing"

    # With system: system + 2*(user+assistant) = 5
    assert len(convos[0]["messages"]) == 5
    assert convos[0]["messages"][0]["role"] == "system"
    assert convos[0]["messages"][1]["role"] == "user"
    assert convos[0]["messages"][2]["role"] == "assistant"

    # Without system: 2*(user+assistant) = 4
    convos_no_sys = generate_demo_conversations(
        1, turns_per_conversation=2, include_system=False,
    )
    assert len(convos_no_sys[0]["messages"]) == 4
    assert convos_no_sys[0]["messages"][0]["role"] == "user"

    # Custom topics
    convos_custom = generate_demo_conversations(
        2, topics=["AI safety", "embeddings"],
    )
    assert convos_custom[0]["topic"] == "AI safety"
    assert convos_custom[1]["topic"] == "embeddings"

    # Validation
    try:
        generate_demo_conversations(0)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

    try:
        generate_demo_conversations(1, turns_per_conversation=0)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

    print("  PASSED")

    # --- Exercise 9 ---
    print("\n--- Exercise 9: Feature Flag System ---")
    ff = FeatureFlagManager()
    ff.register("streaming", enabled=True, description="Enable streaming responses")
    ff.register("dark_mode", enabled=False, description="Dark theme")
    ff.register("tool_use", enabled=False, description="Tool/function calling")

    # Check enabled state
    assert ff.is_enabled("streaming") is True
    assert ff.is_enabled("dark_mode") is False

    # Toggle
    assert ff.toggle("dark_mode") is True
    assert ff.is_enabled("dark_mode") is True
    assert ff.toggle("dark_mode") is False

    # Enable / disable
    ff.enable("tool_use")
    assert ff.is_enabled("tool_use") is True
    ff.disable("tool_use")
    assert ff.is_enabled("tool_use") is False

    # List flags
    all_flags = ff.list_flags()
    assert len(all_flags) == 3
    enabled_only = ff.list_flags(only_enabled=True)
    assert "streaming" in enabled_only
    assert "dark_mode" not in enabled_only

    # Bulk update
    updated = ff.bulk_update({"streaming": False, "dark_mode": True, "nonexistent": True})
    assert updated == {"streaming": False, "dark_mode": True}
    assert ff.is_enabled("streaming") is False
    assert ff.is_enabled("dark_mode") is True

    # Duplicate registration
    try:
        ff.register("streaming")
        assert False, "Should raise ValueError"
    except ValueError:
        pass

    # Unknown flag
    try:
        ff.is_enabled("unknown")
        assert False, "Should raise KeyError"
    except KeyError:
        pass

    print("  PASSED")

    # --- Exercise 10 ---
    print("\n--- Exercise 10: Demo Metrics Collector ---")
    mc = DemoMetricsCollector()

    # Record latency values
    for v in [100, 150, 200, 250]:
        mc.record("latency_ms", v)
    mc.record("tokens", 500)
    mc.record("tokens", 300)

    # Stats
    lat_stats = mc.get_stats("latency_ms")
    assert lat_stats["count"] == 4
    assert lat_stats["sum"] == 700
    assert lat_stats["mean"] == 175.0
    assert lat_stats["min"] == 100
    assert lat_stats["max"] == 250

    tok_stats = mc.get_stats("tokens")
    assert tok_stats["count"] == 2
    assert tok_stats["mean"] == 400.0

    # Metric names
    assert mc.get_all_metric_names() == ["latency_ms", "tokens"]

    # Export
    exported = mc.export()
    assert "latency_ms" in exported
    assert "tokens" in exported

    # Reset specific metric
    mc.reset("tokens")
    assert mc.get_all_metric_names() == ["latency_ms"]
    try:
        mc.get_stats("tokens")
        assert False, "Should raise KeyError"
    except KeyError:
        pass

    # Reset all
    mc.reset()
    assert mc.get_all_metric_names() == []

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
        metrics={"avg_latency_ms": 120.0, "accuracy_pct": 95.5},
        next_steps=["Scale to production", "Add authentication"],
    )
    assert doc["document_type"] == "poc_handoff"
    assert doc["version"] == "1.0"
    assert doc["customer"] == "Acme Corp"
    assert doc["ready_for_production"] is True
    assert doc["feature_summary"]["working"] == 2
    assert doc["feature_summary"]["total"] == 2

    # Not ready if any feature is partial
    doc2 = generate_handoff_document(
        customer_name="Beta Inc",
        poc_title="POC 2",
        features_demonstrated=[
            {"name": "Chat", "status": "working"},
            {"name": "RAG", "status": "partial"},
        ],
        metrics={},
        next_steps=["Fix RAG"],
    )
    assert doc2["ready_for_production"] is False
    assert doc2["feature_summary"]["partial"] == 1

    # Technical notes
    doc3 = generate_handoff_document(
        customer_name="Gamma LLC",
        poc_title="POC 3",
        features_demonstrated=[{"name": "Chat", "status": "working"}],
        metrics={},
        next_steps=["Deploy"],
        technical_notes=["Needs GPU instance", "Use Redis for caching"],
    )
    assert len(doc3["technical_notes"]) == 2

    # Validation
    try:
        generate_handoff_document("", "POC", [{"name": "X", "status": "working"}], {}, ["go"])
        assert False, "Should raise ValueError for empty customer_name"
    except ValueError:
        pass

    try:
        generate_handoff_document("C", "POC", [{"name": "X", "status": "bad"}], {}, ["go"])
        assert False, "Should raise ValueError for invalid status"
    except ValueError:
        pass

    try:
        generate_handoff_document("C", "POC", [], {}, ["go"])
        assert False, "Should raise ValueError for empty features"
    except ValueError:
        pass

    print("  PASSED")

    # --- Exercise 12 ---
    print("\n--- Exercise 12: Demo Fallback System ---")
    fb = DemoFallbackSystem()
    fb.add_fallback("greeting", "Hello! How can I help you today?")
    fb.add_fallback("product_info", {"name": "Widget", "price": 9.99})

    # Live success -> use live
    result = fb.get_response("greeting", live_fn=lambda: "Live greeting!")
    assert result["source"] == "live"
    assert result["response"] == "Live greeting!"

    # Live failure -> fallback
    def failing_fn():
        raise ConnectionError("API is down")

    result = fb.get_response("greeting", live_fn=failing_fn)
    assert result["source"] == "fallback"
    assert result["response"] == "Hello! How can I help you today?"
    assert result["used_count"] == 1

    # Second fallback use
    result = fb.get_response("greeting", live_fn=failing_fn)
    assert result["used_count"] == 2

    # No live_fn, key exists -> fallback
    result = fb.get_response("product_info")
    assert result["source"] == "fallback"
    assert result["response"]["name"] == "Widget"

    # No live_fn, key missing -> error
    result = fb.get_response("unknown")
    assert result["source"] == "error"
    assert "No fallback available" in result["response"]

    # Stats
    stats = fb.get_stats()
    assert stats["total_fallbacks"] == 2
    assert stats["total_used"] == 3  # greeting:2 + product_info:1
    assert stats["most_used"] == "greeting"

    # Overwrite resets used_count
    fb.add_fallback("greeting", "New greeting")
    assert fb.list_fallbacks()["greeting"]["used_count"] == 0

    print("  PASSED")

    # --- Exercise 13 ---
    print("\n--- Exercise 13: Progressive Complexity Demo ---")
    stages = [
        {
            "name": "Basic Chat",
            "description": "Simple Q&A",
            "complexity": 1,
            "features": ["chat"],
            "demo_script": "Start with a simple question and answer.",
        },
        {
            "name": "Chat + Memory",
            "description": "Multi-turn with context",
            "complexity": 2,
            "features": ["chat", "memory"],
            "demo_script": "Show how the assistant remembers context.",
        },
        {
            "name": "RAG Pipeline",
            "description": "Retrieval-augmented generation",
            "complexity": 3,
            "features": ["chat", "memory", "rag"],
            "demo_script": "Upload a document and ask questions about it.",
        },
        {
            "name": "Full Agent",
            "description": "Agent with tool use",
            "complexity": 5,
            "features": ["chat", "memory", "rag", "tools"],
            "demo_script": "Demonstrate autonomous tool usage.",
        },
    ]
    demo = build_progressive_demo(stages)
    assert demo["total_stages"] == 4
    assert demo["stages"][0]["stage_number"] == 1
    assert demo["stages"][3]["stage_number"] == 4
    assert demo["complexity_range"] == {"min": 1, "max": 5}
    assert demo["all_features"] == ["chat", "memory", "rag", "tools"]
    assert demo["estimated_duration_minutes"] == 12

    # Non-decreasing complexity violation
    bad_stages = [
        {"name": "A", "description": "D", "complexity": 3,
         "features": ["x"], "demo_script": "s"},
        {"name": "B", "description": "D", "complexity": 1,
         "features": ["y"], "demo_script": "s"},
    ]
    try:
        build_progressive_demo(bad_stages)
        assert False, "Should raise ValueError for decreasing complexity"
    except ValueError as e:
        assert "non-decreasing" in str(e).lower() or "less" in str(e).lower()

    # Empty stages
    try:
        build_progressive_demo([])
        assert False, "Should raise ValueError for empty stages"
    except ValueError:
        pass

    print("  PASSED")

    # --- Exercise 14 ---
    print("\n--- Exercise 14: Demo Feedback Collector ---")
    fc = DemoFeedbackCollector("AI Assistant Demo")

    fb1 = fc.add_feedback(5, "Amazing demo!", "ui")
    assert fb1["id"] == 1
    assert fb1["rating"] == 5
    assert fb1["category"] == "ui"

    fc.add_feedback(4, "Good accuracy on financial docs", "accuracy")
    fc.add_feedback(3, "", "general")  # No comment
    fc.add_feedback(5, "Love the streaming", "performance")
    fc.add_feedback(2, "Needs dark mode", "feature_request")

    # Average rating: (5+4+3+5+2) / 5 = 3.8
    assert fc.get_average_rating() == 3.8

    # Filter by category
    ui_feedback = fc.get_feedback_by_category("ui")
    assert len(ui_feedback) == 1
    assert ui_feedback[0]["comment"] == "Amazing demo!"

    # Summary
    summary = fc.get_summary()
    assert summary["demo_name"] == "AI Assistant Demo"
    assert summary["total_responses"] == 5
    assert summary["average_rating"] == 3.8
    assert summary["rating_distribution"][5] == 2
    assert summary["rating_distribution"][3] == 1
    assert summary["categories"]["ui"] == 1
    assert summary["categories"]["accuracy"] == 1

    # Latest comments (non-empty, most recent first, max 5)
    assert len(summary["latest_comments"]) == 4  # One had empty comment
    assert summary["latest_comments"][0] == "Needs dark mode"

    # Invalid rating
    try:
        fc.add_feedback(0)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

    try:
        fc.add_feedback(6)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

    # Invalid category
    try:
        fc.add_feedback(3, category="invalid_cat")
        assert False, "Should raise ValueError"
    except ValueError:
        pass

    # Empty collector
    empty_fc = DemoFeedbackCollector("Empty")
    assert empty_fc.get_average_rating() == 0.0
    empty_summary = empty_fc.get_summary()
    assert empty_summary["total_responses"] == 0

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
    assert config["app_name"] == "my-demo-app"
    assert config["environment"] == "staging"
    assert config["provider"] == "aws"
    assert config["container"]["image"] == "my-demo-app:staging"
    assert config["container"]["port"] == 8501
    assert config["container"]["health_check"] == "/healthz"
    assert config["scaling"]["min_instances"] == 1
    assert config["scaling"]["max_instances"] == 3
    assert config["scaling"]["auto_scaling"] is True
    assert config["features"] == ["chat", "rag"]
    assert config["environment_variables"]["APP_NAME"] == "my-demo-app"
    assert config["environment_variables"]["ENVIRONMENT"] == "staging"
    assert config["environment_variables"]["LOG_LEVEL"] == "INFO"
    assert config["environment_variables"]["API_KEY"] == "sk-test"
    assert config["provider_config"]["region"] == "us-east-1"
    assert config["provider_config"]["service"] == "ECS"

    # Development config
    dev_config = generate_deployment_config(
        app_name="dev-app",
        environment="development",
        provider="gcp",
        features=["chat"],
    )
    assert dev_config["scaling"]["auto_scaling"] is False
    assert dev_config["environment_variables"]["LOG_LEVEL"] == "DEBUG"
    assert dev_config["provider_config"]["service"] == "Cloud Run"

    # Production config
    prod_config = generate_deployment_config(
        app_name="prod-app",
        environment="production",
        provider="azure",
        features=["chat", "rag", "tools"],
        scaling={"min_instances": 2, "max_instances": 10},
    )
    assert prod_config["scaling"]["min_instances"] == 2
    assert prod_config["scaling"]["max_instances"] == 10
    assert prod_config["scaling"]["auto_scaling"] is True
    assert prod_config["environment_variables"]["LOG_LEVEL"] == "WARNING"
    assert prod_config["provider_config"]["service"] == "Container Apps"

    # Invalid app_name
    for bad_name in ["BAD APP!", "ab", "1starts-with-digit", "has spaces", ""]:
        try:
            generate_deployment_config(bad_name, "staging", "aws", ["f"])
            assert False, f"Should raise ValueError for app_name={bad_name!r}"
        except ValueError:
            pass

    # Empty features
    try:
        generate_deployment_config("my-app", "staging", "aws", [])
        assert False, "Should raise ValueError for empty features"
    except ValueError:
        pass

    # Invalid scaling
    try:
        generate_deployment_config(
            "my-app", "staging", "aws", ["f"],
            scaling={"min_instances": 0, "max_instances": 3},
        )
        assert False, "Should raise ValueError for min_instances=0"
    except ValueError:
        pass

    try:
        generate_deployment_config(
            "my-app", "staging", "aws", ["f"],
            scaling={"min_instances": 5, "max_instances": 2},
        )
        assert False, "Should raise ValueError for max < min"
    except ValueError:
        pass

    print("  PASSED")

    print("\n" + "=" * 70)
    print("ALL SOLUTION TESTS PASSED!")
    print("=" * 70)
