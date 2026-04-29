"""
Module 09: Observability for LLM Apps -- Exercises
=====================================================

15 exercises covering production observability for LLM-powered applications:
- Structured logging for LLM calls
- Token and cost tracking
- Quality and latency metrics
- Anomaly detection and alerting
- Multi-step chain tracing
- RAG pipeline debugging
- Dashboard data aggregation
- Privacy-aware log sanitization
- Observability health checks

These exercises simulate real-world observability scenarios without requiring
external services. All data structures use stdlib + dataclasses.

Run this file directly to check your solutions:
    python exercises.py
"""

from __future__ import annotations

import hashlib
import math
import statistics
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


# ============================================================================
# Shared Data Models
# ============================================================================

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# Exercise 1: Build an LLM Request Log Entry Model
# ============================================================================

def exercise_1_llm_log_entry(
    request_id: str,
    model: str,
    provider: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: float,
    status_code: int,
    customer_id: str,
    timestamp: datetime,
    error_message: Optional[str] = None,
) -> dict[str, Any]:
    """
    Build a structured log entry dictionary for an LLM API request.

    Every LLM call in production must be logged with consistent structure so
    downstream tools (dashboards, alerting, billing) can parse them reliably.

    Requirements:
    - Return a dict with ALL of the following keys:
        request_id, model, provider, prompt_tokens, completion_tokens,
        total_tokens (computed), latency_ms, status_code, customer_id,
        timestamp (ISO-8601 string), success (bool derived from status_code),
        cost_usd (computed), error_message (None when successful)
    - success is True when 200 <= status_code < 300
    - total_tokens = prompt_tokens + completion_tokens
    - cost_usd is computed using these rates (per 1M tokens):
        "claude-3-5-sonnet": input $3, output $15
        "claude-3-opus":     input $15, output $75
        "gpt-4o":            input $5, output $15
        "gpt-4o-mini":       input $0.15, output $0.60
      For unknown models default to input $10, output $30 per 1M tokens.
    - timestamp must be an ISO-8601 formatted string

    Returns:
        Structured log entry dictionary.
    """
    pass


# ============================================================================
# Exercise 2: Implement a Structured Logger for LLM Calls
# ============================================================================

def exercise_2_structured_logger(
    log_entries: list[dict[str, Any]],
    min_level: LogLevel = LogLevel.INFO,
) -> list[dict[str, Any]]:
    """
    Filter and enrich a batch of raw log entries for structured output.

    In production you have a firehose of log entries at different severity
    levels. This function filters by minimum level and enriches each entry.

    Each entry in log_entries has at minimum:
        {"level": "INFO", "message": "...", "timestamp": "...", **extras}

    Requirements:
    - Filter out entries whose level is below min_level.
      Level ordering: DEBUG < INFO < WARNING < ERROR < CRITICAL
    - Add a "log_id" field (use uuid4 hex) to each surviving entry
    - Add a "service" field with value "llm-gateway"
    - Add an "environment" field with value "production"
    - Return the filtered + enriched list, preserving original order

    Returns:
        List of filtered and enriched log entry dicts.
    """
    pass


# ============================================================================
# Exercise 3: Build a Token Usage Tracker
# ============================================================================

def exercise_3_token_usage_tracker(
    requests: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Aggregate token usage statistics per request and per customer.

    Given a list of completed LLM requests, produce a summary report.

    Each request dict contains:
        customer_id (str), model (str), prompt_tokens (int),
        completion_tokens (int)

    Requirements:
    - "total_requests": total number of requests
    - "total_prompt_tokens": sum of all prompt tokens
    - "total_completion_tokens": sum of all completion tokens
    - "total_tokens": prompt + completion combined
    - "per_customer": dict mapping customer_id -> {
          "requests": int,
          "prompt_tokens": int,
          "completion_tokens": int,
          "total_tokens": int
      }
    - "per_model": dict mapping model -> {
          "requests": int,
          "total_tokens": int
      }

    Returns:
        Aggregated usage report dictionary.
    """
    pass


# ============================================================================
# Exercise 4: Implement a Usage Aggregator (Daily/Weekly/Monthly)
# ============================================================================

def exercise_4_usage_aggregator(
    daily_records: list[dict[str, Any]],
    period: str = "weekly",
) -> list[dict[str, Any]]:
    """
    Roll up daily usage records into weekly or monthly summaries.

    Each daily_record contains:
        date (str YYYY-MM-DD), customer_id (str), total_tokens (int),
        total_cost_usd (float), request_count (int)

    Requirements:
    - If period == "weekly": group by ISO week (use isocalendar). The period
      key should be formatted as "YYYY-WNN" (e.g., "2025-W03").
    - If period == "monthly": group by month. The period key should be
      formatted as "YYYY-MM" (e.g., "2025-01").
    - Each output dict: {
          "period": str,
          "customer_id": str,
          "total_tokens": int,
          "total_cost_usd": float (rounded to 4 decimals),
          "request_count": int
      }
    - Sort output by (period, customer_id)

    Returns:
        List of aggregated period summaries.
    """
    pass


# ============================================================================
# Exercise 5: Build a Quality Score Calculator from User Feedback
# ============================================================================

def exercise_5_quality_score_calculator(
    feedbacks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate quality scores from user feedback on LLM responses.

    Each feedback dict contains:
        request_id (str), model (str), thumbs_up (bool),
        rating (int 1-5, optional), comment (str, optional)

    Requirements:
    - "overall_satisfaction": percentage of thumbs_up (0.0 - 1.0)
    - "average_rating": mean of all ratings that are not None, or None
      if no ratings exist
    - "total_feedback_count": total feedbacks
    - "per_model": dict mapping model -> {
          "satisfaction": float (0.0-1.0),
          "average_rating": float or None,
          "count": int
      }
    - "negative_feedback_ids": list of request_ids where thumbs_up is False,
      sorted alphabetically

    Returns:
        Quality score report dictionary.
    """
    pass


# ============================================================================
# Exercise 6: Implement a Latency Percentile Calculator
# ============================================================================

def exercise_6_latency_percentiles(
    latencies_ms: list[float],
) -> dict[str, float | None]:
    """
    Compute latency percentile statistics from raw latency measurements.

    Requirements:
    - Return a dict with keys: "p50", "p90", "p95", "p99", "mean", "min", "max"
    - Use linear interpolation for percentiles (statistics module or manual)
    - If the input list is empty, return all values as None
    - Round all float values to 2 decimal places

    Returns:
        Dictionary of latency statistics.
    """
    pass


# ============================================================================
# Exercise 7: Build an Anomaly Detector for Cost Spikes
# ============================================================================

def exercise_7_cost_anomaly_detector(
    daily_costs: list[dict[str, Any]],
    z_threshold: float = 2.0,
) -> list[dict[str, Any]]:
    """
    Detect anomalous cost spikes using a z-score approach.

    Each daily_cost dict contains:
        date (str YYYY-MM-DD), cost_usd (float)

    Requirements:
    - Compute mean and standard deviation of all cost_usd values
    - A day is anomalous if |cost - mean| > z_threshold * std_dev
    - If std_dev is 0 (all same values), no anomalies
    - Return a list of anomaly dicts: {
          "date": str,
          "cost_usd": float,
          "mean_cost": float (rounded to 2 decimals),
          "std_dev": float (rounded to 2 decimals),
          "z_score": float (rounded to 2 decimals),
          "direction": "spike" if above mean else "drop"
      }
    - Sort by date ascending

    Returns:
        List of detected anomaly records.
    """
    pass


# ============================================================================
# Exercise 8: Implement a Rate Limit Monitor
# ============================================================================

def exercise_8_rate_limit_monitor(
    request_log: list[dict[str, Any]],
    window_seconds: int = 60,
    max_requests_per_window: int = 100,
) -> dict[str, Any]:
    """
    Analyze a request log for rate-limit violations and near-misses.

    Each request_log entry:
        timestamp (datetime), customer_id (str), endpoint (str)

    Requirements:
    - For each customer, slide a window of window_seconds over their requests
      (sorted by timestamp). Count requests in each window starting from each
      request timestamp.
    - "violations": list of {
          "customer_id": str,
          "window_start": datetime,
          "request_count": int
      } where request_count > max_requests_per_window
    - "near_misses": list with same structure where request_count is between
      80% and 100% of max_requests_per_window (inclusive of 80%, exclusive
      of the limit itself)
    - "summary": {
          "total_violations": int,
          "total_near_misses": int,
          "customers_with_violations": list[str] (sorted)
      }

    Returns:
        Rate limit analysis report.
    """
    pass


# ============================================================================
# Exercise 9: Build a Multi-Step Chain Tracer
# ============================================================================

@dataclass
class SpanRecord:
    """Represents a single span in a trace."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation: str
    start_time: datetime
    end_time: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"  # "ok" or "error"


def exercise_9_chain_tracer(
    spans: list[SpanRecord],
) -> dict[str, Any]:
    """
    Analyze multi-step LLM chain traces for debugging and performance.

    Given a flat list of SpanRecord objects (potentially from multiple traces),
    reconstruct and analyze the trace trees.

    Requirements:
    - Group spans by trace_id
    - For each trace, compute:
        - "total_duration_ms": end_time of latest span minus start_time
          of earliest span, in milliseconds
        - "span_count": number of spans in the trace
        - "has_error": True if any span has status == "error"
        - "root_operation": the operation name of the root span
          (parent_span_id is None)
        - "critical_path_ms": sum of durations of spans on the longest
          sequential path from root to leaf (spans that are children
          execute after their parent starts, use span's own duration)
    - Return {
          "traces": dict mapping trace_id -> trace analysis dict above,
          "total_traces": int,
          "error_traces": int,
          "avg_duration_ms": float (rounded to 2 decimals)
      }

    Returns:
        Trace analysis report.
    """
    pass


# ============================================================================
# Exercise 10: Implement a RAG Pipeline Debugger
# ============================================================================

@dataclass
class RAGStep:
    """Represents one step in a RAG pipeline execution."""
    step_name: str          # e.g., "query_embedding", "retrieval", "reranking", "generation"
    duration_ms: float
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


def exercise_10_rag_pipeline_debugger(
    pipeline_runs: list[list[RAGStep]],
) -> dict[str, Any]:
    """
    Analyze multiple RAG pipeline runs to identify bottlenecks and failures.

    Each pipeline_run is a list of RAGStep objects executed in sequence.

    Requirements:
    - "total_runs": number of pipeline runs
    - "avg_total_duration_ms": average total duration across all runs
      (rounded to 2 decimals)
    - "step_analysis": dict mapping step_name -> {
          "avg_duration_ms": float (rounded to 2),
          "max_duration_ms": float,
          "min_duration_ms": float,
          "pct_of_total": float (avg step duration / avg total duration * 100,
                                 rounded to 1 decimal)
      }
    - "bottleneck_step": the step_name with the highest avg_duration_ms
    - "retrieval_analysis" (only if "retrieval" step exists): {
          "avg_docs_retrieved": float (from output_data["num_docs"]),
          "avg_relevance_score": float (from output_data["avg_score"])
      }
      Round both to 2 decimals.

    Returns:
        RAG pipeline analysis report.
    """
    pass


# ============================================================================
# Exercise 11: Build a Dashboard Data Provider
# ============================================================================

def exercise_11_dashboard_data_provider(
    log_entries: list[dict[str, Any]],
    time_bucket_minutes: int = 60,
) -> dict[str, Any]:
    """
    Transform raw log entries into time-bucketed dashboard-ready data.

    Each log_entry contains:
        timestamp (datetime), model (str), latency_ms (float),
        prompt_tokens (int), completion_tokens (int), success (bool),
        cost_usd (float)

    Requirements:
    - "time_series": list of dicts, one per time bucket, sorted by bucket: {
          "bucket_start": datetime,
          "request_count": int,
          "error_count": int,
          "avg_latency_ms": float (rounded to 2),
          "total_tokens": int,
          "total_cost_usd": float (rounded to 4)
      }
      Buckets are aligned to time_bucket_minutes intervals starting from the
      earliest timestamp floored to the bucket boundary.
    - "model_breakdown": dict mapping model -> {
          "request_count": int,
          "avg_latency_ms": float (rounded to 2),
          "total_cost_usd": float (rounded to 4),
          "error_rate": float (rounded to 4)
      }
    - "summary": {
          "total_requests": int,
          "overall_error_rate": float (rounded to 4),
          "total_cost_usd": float (rounded to 4),
          "avg_latency_ms": float (rounded to 2)
      }

    Returns:
        Dashboard-ready data dictionary.
    """
    pass


# ============================================================================
# Exercise 12: Implement an Alert Rule Engine
# ============================================================================

@dataclass
class AlertRule:
    """Defines a threshold-based alert rule."""
    name: str
    metric: str           # key to look up in metrics dict
    operator: str         # "gt", "lt", "gte", "lte", "eq"
    threshold: float
    severity: AlertSeverity
    cooldown_minutes: int = 5   # minimum minutes between firings


def exercise_12_alert_rule_engine(
    rules: list[AlertRule],
    metrics_snapshots: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Evaluate alert rules against a time series of metrics snapshots.

    Each metrics_snapshot contains:
        timestamp (datetime), plus metric keys/values (e.g., "error_rate": 0.08)

    Requirements:
    - Evaluate each rule against each snapshot in chronological order
    - A rule fires when the comparison (metric <operator> threshold) is True
    - Respect cooldown: after a rule fires, it cannot fire again until
      cooldown_minutes have elapsed
    - Return list of fired alerts: {
          "rule_name": str,
          "severity": str (the AlertSeverity value),
          "timestamp": datetime,
          "metric_value": float,
          "threshold": float,
          "message": str (f"{rule_name}: {metric} is {metric_value} (threshold: {threshold})")
      }
    - Sort by timestamp, then by rule name

    Returns:
        List of fired alert records.
    """
    pass


# ============================================================================
# Exercise 13: Build a Log Retention Policy Enforcer
# ============================================================================

def exercise_13_log_retention_policy(
    log_entries: list[dict[str, Any]],
    retention_days: int = 30,
    archive_days: int = 90,
    reference_date: Optional[datetime] = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Classify log entries by retention policy tier.

    Each log_entry contains:
        timestamp (datetime), level (str), message (str), **extras

    Requirements:
    - reference_date defaults to datetime.utcnow() if not provided
    - "active": entries within retention_days of reference_date
    - "archive": entries older than retention_days but within archive_days
    - "delete": entries older than archive_days
    - Age is computed as (reference_date - entry timestamp).days
    - Each category list preserves original order
    - Return {"active": [...], "archive": [...], "delete": [...]}

    Returns:
        Dict with categorized log entries.
    """
    pass


# ============================================================================
# Exercise 14: Implement a Privacy-Aware Log Sanitizer
# ============================================================================

def exercise_14_privacy_sanitizer(
    log_entry: dict[str, Any],
    pii_fields: list[str] | None = None,
    hash_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Sanitize a log entry to remove or mask PII before storage.

    Requirements:
    - pii_fields defaults to: ["email", "phone", "ssn", "credit_card",
      "api_key", "password"]
    - hash_fields defaults to: ["customer_id", "user_id", "session_id"]
    - For keys matching pii_fields: replace value with "[REDACTED]"
    - For keys matching hash_fields: replace value with "hash_<first-8-chars-
      of-sha256-hex-digest>"  (use hashlib.sha256 on the str(value))
    - Recursively sanitize nested dicts
    - Do NOT mutate the original dict; return a new copy
    - For list values, recursively sanitize any dict elements in the list
    - Non-dict, non-list values at keys not in pii/hash fields are left as-is

    Returns:
        Sanitized copy of the log entry.
    """
    pass


# ============================================================================
# Exercise 15: Build an Observability Health Check
# ============================================================================

def exercise_15_observability_health_check(
    components: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Run a health check across all observability components and produce a
    unified status report.

    components is a dict mapping component_name -> component_info where
    component_info has:
        "status": str ("healthy", "degraded", "unhealthy"),
        "last_heartbeat": datetime,
        "error_count_last_hour": int,
        "details": str

    Requirements:
    - reference time: use the maximum last_heartbeat across all components
      as "now" (so the check is deterministic)
    - A component is "stale" if its last_heartbeat is > 5 minutes before
      the reference time. Override its status to "unhealthy" and append
      " (stale heartbeat)" to its details.
    - "overall_status":
        - "healthy" if ALL components are "healthy"
        - "degraded" if any component is "degraded" but none are "unhealthy"
        - "unhealthy" if any component is "unhealthy"
    - "components": dict mapping component_name -> {
          "status": str (potentially overridden),
          "last_heartbeat": datetime,
          "error_count_last_hour": int,
          "details": str,
          "is_stale": bool
      }
    - "total_errors_last_hour": sum of all error_count_last_hour
    - "unhealthy_components": sorted list of names with "unhealthy" status
    - "degraded_components": sorted list of names with "degraded" status

    Returns:
        Unified health check report.
    """
    pass


# ============================================================================
# Test Suite
# ============================================================================

if __name__ == "__main__":

    # -- Exercise 1 ----------------------------------------------------------
    entry = exercise_1_llm_log_entry(
        request_id="req-001",
        model="gpt-4o",
        provider="openai",
        prompt_tokens=500,
        completion_tokens=200,
        latency_ms=1234.5,
        status_code=200,
        customer_id="cust-42",
        timestamp=datetime(2025, 1, 15, 10, 30, 0),
    )
    assert entry["total_tokens"] == 700
    assert entry["success"] is True
    assert entry["error_message"] is None
    assert isinstance(entry["cost_usd"], float) and entry["cost_usd"] > 0
    assert entry["timestamp"] == "2025-01-15T10:30:00"
    print("Exercise 1 passed!")

    # -- Exercise 2 ----------------------------------------------------------
    raw_logs = [
        {"level": "DEBUG", "message": "verbose trace", "timestamp": "t1"},
        {"level": "INFO", "message": "request started", "timestamp": "t2"},
        {"level": "WARNING", "message": "slow query", "timestamp": "t3"},
        {"level": "ERROR", "message": "api failed", "timestamp": "t4"},
    ]
    filtered = exercise_2_structured_logger(raw_logs, LogLevel.WARNING)
    assert len(filtered) == 2
    assert all("log_id" in e for e in filtered)
    assert all(e["service"] == "llm-gateway" for e in filtered)
    assert filtered[0]["message"] == "slow query"
    print("Exercise 2 passed!")

    # -- Exercise 3 ----------------------------------------------------------
    reqs = [
        {"customer_id": "A", "model": "gpt-4o", "prompt_tokens": 100, "completion_tokens": 50},
        {"customer_id": "A", "model": "gpt-4o", "prompt_tokens": 200, "completion_tokens": 100},
        {"customer_id": "B", "model": "claude-3-5-sonnet", "prompt_tokens": 300, "completion_tokens": 150},
    ]
    usage = exercise_3_token_usage_tracker(reqs)
    assert usage["total_requests"] == 3
    assert usage["total_tokens"] == 900
    assert usage["per_customer"]["A"]["total_tokens"] == 450
    assert usage["per_model"]["gpt-4o"]["requests"] == 2
    print("Exercise 3 passed!")

    # -- Exercise 4 ----------------------------------------------------------
    daily = [
        {"date": "2025-01-06", "customer_id": "A", "total_tokens": 100, "total_cost_usd": 0.01, "request_count": 5},
        {"date": "2025-01-07", "customer_id": "A", "total_tokens": 200, "total_cost_usd": 0.02, "request_count": 10},
        {"date": "2025-01-13", "customer_id": "A", "total_tokens": 150, "total_cost_usd": 0.015, "request_count": 7},
    ]
    weekly = exercise_4_usage_aggregator(daily, "weekly")
    assert len(weekly) == 2  # Two distinct ISO weeks
    assert all("period" in w for w in weekly)
    print("Exercise 4 passed!")

    # -- Exercise 5 ----------------------------------------------------------
    feedbacks = [
        {"request_id": "r1", "model": "gpt-4o", "thumbs_up": True, "rating": 5, "comment": "Great"},
        {"request_id": "r2", "model": "gpt-4o", "thumbs_up": False, "rating": 2, "comment": None},
        {"request_id": "r3", "model": "claude-3-5-sonnet", "thumbs_up": True, "rating": None, "comment": None},
    ]
    quality = exercise_5_quality_score_calculator(feedbacks)
    assert abs(quality["overall_satisfaction"] - 2 / 3) < 0.01
    assert quality["average_rating"] == 3.5
    assert quality["negative_feedback_ids"] == ["r2"]
    print("Exercise 5 passed!")

    # -- Exercise 6 ----------------------------------------------------------
    lats = [120.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 800.0, 1200.0, 2000.0]
    pcts = exercise_6_latency_percentiles(lats)
    assert pcts["min"] == 120.0
    assert pcts["max"] == 2000.0
    assert pcts["p50"] is not None
    empty_pcts = exercise_6_latency_percentiles([])
    assert all(v is None for v in empty_pcts.values())
    print("Exercise 6 passed!")

    # -- Exercise 7 ----------------------------------------------------------
    costs = [
        {"date": "2025-01-01", "cost_usd": 10.0},
        {"date": "2025-01-02", "cost_usd": 12.0},
        {"date": "2025-01-03", "cost_usd": 11.0},
        {"date": "2025-01-04", "cost_usd": 50.0},  # spike
        {"date": "2025-01-05", "cost_usd": 10.5},
    ]
    anomalies = exercise_7_cost_anomaly_detector(costs, z_threshold=1.5)
    assert len(anomalies) >= 1
    assert anomalies[0]["date"] == "2025-01-04"
    assert anomalies[0]["direction"] == "spike"
    print("Exercise 7 passed!")

    # -- Exercise 8 ----------------------------------------------------------
    base_time = datetime(2025, 1, 15, 10, 0, 0)
    req_log = [
        {"timestamp": base_time + timedelta(seconds=i), "customer_id": "C1", "endpoint": "/chat"}
        for i in range(110)
    ]
    rate_result = exercise_8_rate_limit_monitor(req_log, window_seconds=60, max_requests_per_window=100)
    assert rate_result["summary"]["total_violations"] > 0
    assert "C1" in rate_result["summary"]["customers_with_violations"]
    print("Exercise 8 passed!")

    # -- Exercise 9 ----------------------------------------------------------
    t0 = datetime(2025, 1, 15, 10, 0, 0)
    spans = [
        SpanRecord("trace-1", "s1", None, "chain", t0, t0 + timedelta(milliseconds=500)),
        SpanRecord("trace-1", "s2", "s1", "llm_call", t0 + timedelta(milliseconds=10),
                   t0 + timedelta(milliseconds=300)),
        SpanRecord("trace-1", "s3", "s1", "retrieval", t0 + timedelta(milliseconds=5),
                   t0 + timedelta(milliseconds=200), status="error"),
        SpanRecord("trace-2", "s4", None, "simple_call", t0, t0 + timedelta(milliseconds=100)),
    ]
    trace_report = exercise_9_chain_tracer(spans)
    assert trace_report["total_traces"] == 2
    assert trace_report["error_traces"] == 1
    assert trace_report["traces"]["trace-1"]["has_error"] is True
    assert trace_report["traces"]["trace-1"]["root_operation"] == "chain"
    print("Exercise 9 passed!")

    # -- Exercise 10 ---------------------------------------------------------
    run1 = [
        RAGStep("query_embedding", 15.0, {"query": "test"}, {"embedding_dim": 1536}),
        RAGStep("retrieval", 120.0, {"top_k": 5}, {"num_docs": 5, "avg_score": 0.85}),
        RAGStep("reranking", 45.0, {"docs": 5}, {"docs": 3}),
        RAGStep("generation", 800.0, {"context_len": 2000}, {"tokens": 500}),
    ]
    run2 = [
        RAGStep("query_embedding", 18.0, {"query": "test2"}, {"embedding_dim": 1536}),
        RAGStep("retrieval", 130.0, {"top_k": 5}, {"num_docs": 4, "avg_score": 0.78}),
        RAGStep("reranking", 50.0, {"docs": 4}, {"docs": 2}),
        RAGStep("generation", 750.0, {"context_len": 1800}, {"tokens": 450}),
    ]
    rag_report = exercise_10_rag_pipeline_debugger([run1, run2])
    assert rag_report["total_runs"] == 2
    assert rag_report["bottleneck_step"] == "generation"
    assert "retrieval_analysis" in rag_report
    print("Exercise 10 passed!")

    # -- Exercise 11 ---------------------------------------------------------
    base = datetime(2025, 1, 15, 10, 0, 0)
    logs = [
        {"timestamp": base, "model": "gpt-4o", "latency_ms": 200.0,
         "prompt_tokens": 100, "completion_tokens": 50, "success": True, "cost_usd": 0.001},
        {"timestamp": base + timedelta(minutes=30), "model": "gpt-4o", "latency_ms": 300.0,
         "prompt_tokens": 200, "completion_tokens": 100, "success": False, "cost_usd": 0.002},
        {"timestamp": base + timedelta(minutes=90), "model": "claude-3-5-sonnet", "latency_ms": 150.0,
         "prompt_tokens": 150, "completion_tokens": 75, "success": True, "cost_usd": 0.0015},
    ]
    dashboard = exercise_11_dashboard_data_provider(logs, time_bucket_minutes=60)
    assert len(dashboard["time_series"]) == 2
    assert dashboard["summary"]["total_requests"] == 3
    assert "gpt-4o" in dashboard["model_breakdown"]
    print("Exercise 11 passed!")

    # -- Exercise 12 ---------------------------------------------------------
    rules = [
        AlertRule("HighErrorRate", "error_rate", "gt", 0.05, AlertSeverity.HIGH, cooldown_minutes=10),
        AlertRule("HighLatency", "p95_latency_ms", "gt", 1000.0, AlertSeverity.MEDIUM, cooldown_minutes=5),
    ]
    t0 = datetime(2025, 1, 15, 10, 0, 0)
    snapshots = [
        {"timestamp": t0, "error_rate": 0.08, "p95_latency_ms": 500.0},
        {"timestamp": t0 + timedelta(minutes=1), "error_rate": 0.03, "p95_latency_ms": 1500.0},
        {"timestamp": t0 + timedelta(minutes=2), "error_rate": 0.10, "p95_latency_ms": 800.0},
    ]
    alerts = exercise_12_alert_rule_engine(rules, snapshots)
    assert len(alerts) >= 2
    assert alerts[0]["rule_name"] == "HighErrorRate"
    print("Exercise 12 passed!")

    # -- Exercise 13 ---------------------------------------------------------
    ref = datetime(2025, 3, 1)
    entries = [
        {"timestamp": datetime(2025, 2, 20), "level": "INFO", "message": "recent"},
        {"timestamp": datetime(2025, 1, 15), "level": "ERROR", "message": "older"},
        {"timestamp": datetime(2024, 11, 1), "level": "WARNING", "message": "ancient"},
    ]
    result = exercise_13_log_retention_policy(entries, retention_days=30,
                                              archive_days=90, reference_date=ref)
    assert len(result["active"]) == 1
    assert len(result["archive"]) == 1
    assert len(result["delete"]) == 1
    print("Exercise 13 passed!")

    # -- Exercise 14 ---------------------------------------------------------
    raw = {
        "customer_id": "cust-123",
        "email": "user@example.com",
        "request": {
            "prompt": "Hello",
            "api_key": "sk-abc123",
            "user_id": "u-456",
        },
        "model": "gpt-4o",
    }
    sanitized = exercise_14_privacy_sanitizer(raw)
    assert sanitized["email"] == "[REDACTED]"
    assert sanitized["request"]["api_key"] == "[REDACTED]"
    assert sanitized["customer_id"].startswith("hash_")
    assert sanitized["request"]["user_id"].startswith("hash_")
    assert sanitized["model"] == "gpt-4o"
    assert raw["email"] == "user@example.com"  # original unchanged
    print("Exercise 14 passed!")

    # -- Exercise 15 ---------------------------------------------------------
    ref_time = datetime(2025, 1, 15, 10, 0, 0)
    comps = {
        "logging": {
            "status": "healthy",
            "last_heartbeat": ref_time,
            "error_count_last_hour": 0,
            "details": "All good",
        },
        "metrics": {
            "status": "degraded",
            "last_heartbeat": ref_time - timedelta(minutes=2),
            "error_count_last_hour": 3,
            "details": "Slow writes",
        },
        "tracing": {
            "status": "healthy",
            "last_heartbeat": ref_time - timedelta(minutes=10),
            "error_count_last_hour": 0,
            "details": "Running",
        },
    }
    health = exercise_15_observability_health_check(comps)
    assert health["overall_status"] == "unhealthy"
    assert health["components"]["tracing"]["is_stale"] is True
    assert "tracing" in health["unhealthy_components"]
    assert health["total_errors_last_hour"] == 3
    print("Exercise 15 passed!")

    print("\n" + "=" * 60)
    print("All 15 exercises passed!")
    print("=" * 60)
