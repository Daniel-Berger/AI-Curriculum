"""
Module 09: Observability for LLM Apps -- Solutions
=====================================================

Complete implementations for all 15 exercises with detailed comments.

Run this file directly to verify all solutions:
    python solutions.py
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
# Shared Data Models (duplicated from exercises for standalone execution)
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


# Numeric ordering for log levels -- used in Exercise 2
_LOG_LEVEL_ORDER = {
    LogLevel.DEBUG: 0,
    LogLevel.INFO: 1,
    LogLevel.WARNING: 2,
    LogLevel.ERROR: 3,
    LogLevel.CRITICAL: 4,
}


# ============================================================================
# Solution 1: Build an LLM Request Log Entry Model
# ============================================================================

def solution_1_llm_log_entry(
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
    Build a structured log entry for an LLM API request.

    This is the foundational data model that every downstream observability
    tool -- dashboards, alerting, billing -- depends on.  Consistency here
    saves hours of debugging later.
    """
    # Pricing table: (input_price_per_1M, output_price_per_1M)
    pricing: dict[str, tuple[float, float]] = {
        "claude-3-5-sonnet": (3.0, 15.0),
        "claude-3-opus":     (15.0, 75.0),
        "gpt-4o":            (5.0, 15.0),
        "gpt-4o-mini":       (0.15, 0.60),
    }

    input_rate, output_rate = pricing.get(model, (10.0, 30.0))

    # Cost = tokens / 1_000_000 * rate
    cost_usd = (prompt_tokens / 1_000_000 * input_rate
                + completion_tokens / 1_000_000 * output_rate)

    return {
        "request_id": request_id,
        "model": model,
        "provider": provider,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "latency_ms": latency_ms,
        "status_code": status_code,
        "customer_id": customer_id,
        "timestamp": timestamp.isoformat(),
        "success": 200 <= status_code < 300,
        "cost_usd": cost_usd,
        "error_message": error_message,
    }


# ============================================================================
# Solution 2: Implement a Structured Logger for LLM Calls
# ============================================================================

def solution_2_structured_logger(
    log_entries: list[dict[str, Any]],
    min_level: LogLevel = LogLevel.INFO,
) -> list[dict[str, Any]]:
    """
    Filter by severity and enrich every surviving entry with traceability
    fields that downstream log aggregators (Datadog, Elasticsearch) expect.
    """
    min_order = _LOG_LEVEL_ORDER[min_level]

    result: list[dict[str, Any]] = []
    for entry in log_entries:
        # Parse the level string into our enum for comparison
        entry_level = LogLevel(entry["level"])
        if _LOG_LEVEL_ORDER[entry_level] < min_order:
            continue

        # Shallow-copy so we don't mutate the caller's data
        enriched = dict(entry)
        enriched["log_id"] = uuid.uuid4().hex
        enriched["service"] = "llm-gateway"
        enriched["environment"] = "production"
        result.append(enriched)

    return result


# ============================================================================
# Solution 3: Build a Token Usage Tracker
# ============================================================================

def solution_3_token_usage_tracker(
    requests: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Aggregate token usage both globally and per-customer / per-model.

    In production this feeds the billing pipeline and helps set per-customer
    quotas and rate limits.
    """
    total_prompt = 0
    total_completion = 0

    per_customer: dict[str, dict[str, int]] = defaultdict(
        lambda: {"requests": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    )
    per_model: dict[str, dict[str, int]] = defaultdict(
        lambda: {"requests": 0, "total_tokens": 0}
    )

    for req in requests:
        pt = req["prompt_tokens"]
        ct = req["completion_tokens"]
        tt = pt + ct
        cid = req["customer_id"]
        mdl = req["model"]

        total_prompt += pt
        total_completion += ct

        per_customer[cid]["requests"] += 1
        per_customer[cid]["prompt_tokens"] += pt
        per_customer[cid]["completion_tokens"] += ct
        per_customer[cid]["total_tokens"] += tt

        per_model[mdl]["requests"] += 1
        per_model[mdl]["total_tokens"] += tt

    return {
        "total_requests": len(requests),
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_tokens": total_prompt + total_completion,
        "per_customer": dict(per_customer),
        "per_model": dict(per_model),
    }


# ============================================================================
# Solution 4: Implement a Usage Aggregator (Daily/Weekly/Monthly)
# ============================================================================

def solution_4_usage_aggregator(
    daily_records: list[dict[str, Any]],
    period: str = "weekly",
) -> list[dict[str, Any]]:
    """
    Roll up daily usage into coarser time buckets for trend analysis.

    Weekly rollups are ideal for spotting usage growth; monthly rollups
    align with billing cycles.
    """
    buckets: dict[tuple[str, str], dict[str, Any]] = {}

    for rec in daily_records:
        dt = datetime.strptime(rec["date"], "%Y-%m-%d")
        cid = rec["customer_id"]

        if period == "weekly":
            iso = dt.isocalendar()
            period_key = f"{iso[0]}-W{iso[1]:02d}"
        else:  # monthly
            period_key = dt.strftime("%Y-%m")

        key = (period_key, cid)
        if key not in buckets:
            buckets[key] = {
                "period": period_key,
                "customer_id": cid,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "request_count": 0,
            }

        buckets[key]["total_tokens"] += rec["total_tokens"]
        buckets[key]["total_cost_usd"] += rec["total_cost_usd"]
        buckets[key]["request_count"] += rec["request_count"]

    # Round costs and sort
    result = list(buckets.values())
    for r in result:
        r["total_cost_usd"] = round(r["total_cost_usd"], 4)
    result.sort(key=lambda x: (x["period"], x["customer_id"]))

    return result


# ============================================================================
# Solution 5: Build a Quality Score Calculator from User Feedback
# ============================================================================

def solution_5_quality_score_calculator(
    feedbacks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Translate raw user signals into actionable quality metrics.

    Thumbs-up ratio is the simplest quality signal; per-model breakdowns
    tell you which provider is underperforming.
    """
    if not feedbacks:
        return {
            "overall_satisfaction": 0.0,
            "average_rating": None,
            "total_feedback_count": 0,
            "per_model": {},
            "negative_feedback_ids": [],
        }

    thumbs_up_count = sum(1 for f in feedbacks if f["thumbs_up"])
    ratings = [f["rating"] for f in feedbacks if f.get("rating") is not None]
    negative_ids = sorted(f["request_id"] for f in feedbacks if not f["thumbs_up"])

    # Per-model breakdown
    model_groups: dict[str, list[dict]] = defaultdict(list)
    for f in feedbacks:
        model_groups[f["model"]].append(f)

    per_model: dict[str, dict[str, Any]] = {}
    for model, group in model_groups.items():
        m_thumbs = sum(1 for f in group if f["thumbs_up"])
        m_ratings = [f["rating"] for f in group if f.get("rating") is not None]
        per_model[model] = {
            "satisfaction": m_thumbs / len(group),
            "average_rating": (statistics.mean(m_ratings) if m_ratings else None),
            "count": len(group),
        }

    return {
        "overall_satisfaction": thumbs_up_count / len(feedbacks),
        "average_rating": (statistics.mean(ratings) if ratings else None),
        "total_feedback_count": len(feedbacks),
        "per_model": per_model,
        "negative_feedback_ids": negative_ids,
    }


# ============================================================================
# Solution 6: Implement a Latency Percentile Calculator
# ============================================================================

def solution_6_latency_percentiles(
    latencies_ms: list[float],
) -> dict[str, float | None]:
    """
    Compute standard latency percentiles used in SLO definitions.

    p50 tells you the typical experience; p95/p99 expose tail latency that
    affects your worst-off users.
    """
    if not latencies_ms:
        return {"p50": None, "p90": None, "p95": None, "p99": None,
                "mean": None, "min": None, "max": None}

    sorted_lats = sorted(latencies_ms)

    def percentile(data: list[float], pct: float) -> float:
        """Linear interpolation percentile (matches numpy default)."""
        n = len(data)
        # Index position for the percentile
        k = (n - 1) * (pct / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return data[int(k)]
        return data[f] * (c - k) + data[c] * (k - f)

    return {
        "p50": round(percentile(sorted_lats, 50), 2),
        "p90": round(percentile(sorted_lats, 90), 2),
        "p95": round(percentile(sorted_lats, 95), 2),
        "p99": round(percentile(sorted_lats, 99), 2),
        "mean": round(statistics.mean(latencies_ms), 2),
        "min": round(min(latencies_ms), 2),
        "max": round(max(latencies_ms), 2),
    }


# ============================================================================
# Solution 7: Build an Anomaly Detector for Cost Spikes
# ============================================================================

def solution_7_cost_anomaly_detector(
    daily_costs: list[dict[str, Any]],
    z_threshold: float = 2.0,
) -> list[dict[str, Any]]:
    """
    Flag days where spending deviates significantly from the norm.

    Z-score anomaly detection is simple but effective for catching billing
    surprises before they hit the invoice.
    """
    if len(daily_costs) < 2:
        return []

    costs = [d["cost_usd"] for d in daily_costs]
    mean_cost = statistics.mean(costs)
    std_dev = statistics.stdev(costs)

    # If all values are the same, no anomalies
    if std_dev == 0:
        return []

    anomalies: list[dict[str, Any]] = []
    for d in daily_costs:
        z = (d["cost_usd"] - mean_cost) / std_dev
        if abs(z) > z_threshold:
            anomalies.append({
                "date": d["date"],
                "cost_usd": d["cost_usd"],
                "mean_cost": round(mean_cost, 2),
                "std_dev": round(std_dev, 2),
                "z_score": round(z, 2),
                "direction": "spike" if d["cost_usd"] > mean_cost else "drop",
            })

    anomalies.sort(key=lambda x: x["date"])
    return anomalies


# ============================================================================
# Solution 8: Implement a Rate Limit Monitor
# ============================================================================

def solution_8_rate_limit_monitor(
    request_log: list[dict[str, Any]],
    window_seconds: int = 60,
    max_requests_per_window: int = 100,
) -> dict[str, Any]:
    """
    Detect rate-limit violations and near-misses per customer.

    Near-miss detection is crucial: a customer at 85% of their limit is one
    retry storm away from getting throttled.
    """
    # Group requests by customer, sorted by timestamp
    by_customer: dict[str, list[datetime]] = defaultdict(list)
    for entry in request_log:
        by_customer[entry["customer_id"]].append(entry["timestamp"])

    violations: list[dict[str, Any]] = []
    near_misses: list[dict[str, Any]] = []
    near_miss_threshold = max_requests_per_window * 0.8

    # Track windows we have already reported to avoid duplicates
    for cid, timestamps in by_customer.items():
        sorted_ts = sorted(timestamps)

        for i, window_start in enumerate(sorted_ts):
            window_end = window_start + timedelta(seconds=window_seconds)
            # Count requests in [window_start, window_end)
            count = 0
            for ts in sorted_ts[i:]:
                if ts < window_end:
                    count += 1
                else:
                    break

            record = {
                "customer_id": cid,
                "window_start": window_start,
                "request_count": count,
            }

            if count > max_requests_per_window:
                violations.append(record)
            elif count >= near_miss_threshold:
                near_misses.append(record)

    customers_with_violations = sorted(
        set(v["customer_id"] for v in violations)
    )

    return {
        "violations": violations,
        "near_misses": near_misses,
        "summary": {
            "total_violations": len(violations),
            "total_near_misses": len(near_misses),
            "customers_with_violations": customers_with_violations,
        },
    }


# ============================================================================
# Solution 9: Build a Multi-Step Chain Tracer
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
    status: str = "ok"


def solution_9_chain_tracer(
    spans: list[SpanRecord],
) -> dict[str, Any]:
    """
    Reconstruct trace trees and compute performance characteristics.

    The critical path calculation identifies the bottleneck chain of
    operations -- the sequence you must optimize to reduce end-to-end latency.
    """
    # Group spans by trace_id
    traces: dict[str, list[SpanRecord]] = defaultdict(list)
    for span in spans:
        traces[span.trace_id].append(span)

    trace_analyses: dict[str, dict[str, Any]] = {}
    error_count = 0
    total_duration = 0.0

    for trace_id, trace_spans in traces.items():
        # Total duration: latest end - earliest start
        earliest = min(s.start_time for s in trace_spans)
        latest = max(s.end_time for s in trace_spans)
        duration_ms = (latest - earliest).total_seconds() * 1000

        has_error = any(s.status == "error" for s in trace_spans)
        if has_error:
            error_count += 1

        # Find root span (parent_span_id is None)
        root_spans = [s for s in trace_spans if s.parent_span_id is None]
        root_operation = root_spans[0].operation if root_spans else "unknown"

        # Build a children lookup for critical path calculation
        children_map: dict[str, list[SpanRecord]] = defaultdict(list)
        span_lookup: dict[str, SpanRecord] = {}
        for s in trace_spans:
            span_lookup[s.span_id] = s
            if s.parent_span_id is not None:
                children_map[s.parent_span_id].append(s)

        # Critical path: longest path from root to any leaf
        # using each span's own duration
        def _longest_path(span_id: str) -> float:
            span = span_lookup[span_id]
            own_duration = (span.end_time - span.start_time).total_seconds() * 1000
            child_spans = children_map.get(span_id, [])
            if not child_spans:
                return own_duration
            max_child = max(_longest_path(c.span_id) for c in child_spans)
            return own_duration + max_child

        critical_path_ms = 0.0
        if root_spans:
            critical_path_ms = _longest_path(root_spans[0].span_id)

        trace_analyses[trace_id] = {
            "total_duration_ms": duration_ms,
            "span_count": len(trace_spans),
            "has_error": has_error,
            "root_operation": root_operation,
            "critical_path_ms": critical_path_ms,
        }

        total_duration += duration_ms

    num_traces = len(trace_analyses)
    avg_duration = round(total_duration / num_traces, 2) if num_traces else 0.0

    return {
        "traces": trace_analyses,
        "total_traces": num_traces,
        "error_traces": error_count,
        "avg_duration_ms": avg_duration,
    }


# ============================================================================
# Solution 10: Implement a RAG Pipeline Debugger
# ============================================================================

@dataclass
class RAGStep:
    """Represents one step in a RAG pipeline execution."""
    step_name: str
    duration_ms: float
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


def solution_10_rag_pipeline_debugger(
    pipeline_runs: list[list[RAGStep]],
) -> dict[str, Any]:
    """
    Profile RAG pipelines to find the step that dominates latency.

    In practice, "generation" is almost always the bottleneck, but retrieval
    quality (avg_score) is what determines output quality.
    """
    if not pipeline_runs:
        return {
            "total_runs": 0,
            "avg_total_duration_ms": 0.0,
            "step_analysis": {},
            "bottleneck_step": None,
        }

    # Collect per-step durations across all runs
    step_durations: dict[str, list[float]] = defaultdict(list)
    total_durations: list[float] = []

    # For retrieval analysis
    retrieval_docs: list[float] = []
    retrieval_scores: list[float] = []

    for run in pipeline_runs:
        run_total = sum(step.duration_ms for step in run)
        total_durations.append(run_total)

        for step in run:
            step_durations[step.step_name].append(step.duration_ms)

            # Gather retrieval-specific metrics
            if step.step_name == "retrieval":
                if "num_docs" in step.output_data:
                    retrieval_docs.append(step.output_data["num_docs"])
                if "avg_score" in step.output_data:
                    retrieval_scores.append(step.output_data["avg_score"])

    avg_total = round(statistics.mean(total_durations), 2)

    # Per-step analysis
    step_analysis: dict[str, dict[str, Any]] = {}
    for step_name, durations in step_durations.items():
        avg_dur = round(statistics.mean(durations), 2)
        step_analysis[step_name] = {
            "avg_duration_ms": avg_dur,
            "max_duration_ms": max(durations),
            "min_duration_ms": min(durations),
            "pct_of_total": round(avg_dur / avg_total * 100, 1) if avg_total > 0 else 0.0,
        }

    # Identify bottleneck
    bottleneck = max(step_analysis, key=lambda s: step_analysis[s]["avg_duration_ms"])

    result: dict[str, Any] = {
        "total_runs": len(pipeline_runs),
        "avg_total_duration_ms": avg_total,
        "step_analysis": step_analysis,
        "bottleneck_step": bottleneck,
    }

    # Optional retrieval analysis
    if retrieval_docs or retrieval_scores:
        result["retrieval_analysis"] = {}
        if retrieval_docs:
            result["retrieval_analysis"]["avg_docs_retrieved"] = round(
                statistics.mean(retrieval_docs), 2
            )
        if retrieval_scores:
            result["retrieval_analysis"]["avg_relevance_score"] = round(
                statistics.mean(retrieval_scores), 2
            )

    return result


# ============================================================================
# Solution 11: Build a Dashboard Data Provider
# ============================================================================

def solution_11_dashboard_data_provider(
    log_entries: list[dict[str, Any]],
    time_bucket_minutes: int = 60,
) -> dict[str, Any]:
    """
    Aggregate raw logs into dashboard-ready time-series and breakdowns.

    This is the backend for a Grafana-style dashboard: pre-aggregate so the
    frontend never has to scan raw logs.
    """
    if not log_entries:
        return {
            "time_series": [],
            "model_breakdown": {},
            "summary": {
                "total_requests": 0,
                "overall_error_rate": 0.0,
                "total_cost_usd": 0.0,
                "avg_latency_ms": 0.0,
            },
        }

    bucket_delta = timedelta(minutes=time_bucket_minutes)

    # Find the earliest timestamp, floored to the bucket boundary
    earliest = min(e["timestamp"] for e in log_entries)
    # Floor to the nearest bucket boundary
    epoch = datetime(earliest.year, earliest.month, earliest.day)
    minutes_since_midnight = (earliest - epoch).total_seconds() / 60
    bucket_start_offset = int(minutes_since_midnight // time_bucket_minutes) * time_bucket_minutes
    floor_time = epoch + timedelta(minutes=bucket_start_offset)

    # Assign each entry to a bucket
    buckets: dict[datetime, list[dict]] = defaultdict(list)
    for entry in log_entries:
        offset = (entry["timestamp"] - floor_time).total_seconds() / 60
        bucket_index = int(offset // time_bucket_minutes)
        bucket_key = floor_time + timedelta(minutes=bucket_index * time_bucket_minutes)
        buckets[bucket_key].append(entry)

    # Build time series
    time_series: list[dict[str, Any]] = []
    for bucket_start in sorted(buckets):
        entries = buckets[bucket_start]
        error_count = sum(1 for e in entries if not e["success"])
        latencies = [e["latency_ms"] for e in entries]
        total_tokens = sum(e["prompt_tokens"] + e["completion_tokens"] for e in entries)
        total_cost = sum(e["cost_usd"] for e in entries)

        time_series.append({
            "bucket_start": bucket_start,
            "request_count": len(entries),
            "error_count": error_count,
            "avg_latency_ms": round(statistics.mean(latencies), 2),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
        })

    # Model breakdown
    model_groups: dict[str, list[dict]] = defaultdict(list)
    for entry in log_entries:
        model_groups[entry["model"]].append(entry)

    model_breakdown: dict[str, dict[str, Any]] = {}
    for model, entries in model_groups.items():
        errors = sum(1 for e in entries if not e["success"])
        latencies = [e["latency_ms"] for e in entries]
        total_cost = sum(e["cost_usd"] for e in entries)
        model_breakdown[model] = {
            "request_count": len(entries),
            "avg_latency_ms": round(statistics.mean(latencies), 2),
            "total_cost_usd": round(total_cost, 4),
            "error_rate": round(errors / len(entries), 4),
        }

    # Summary
    total_errors = sum(1 for e in log_entries if not e["success"])
    all_latencies = [e["latency_ms"] for e in log_entries]

    return {
        "time_series": time_series,
        "model_breakdown": model_breakdown,
        "summary": {
            "total_requests": len(log_entries),
            "overall_error_rate": round(total_errors / len(log_entries), 4),
            "total_cost_usd": round(sum(e["cost_usd"] for e in log_entries), 4),
            "avg_latency_ms": round(statistics.mean(all_latencies), 2),
        },
    }


# ============================================================================
# Solution 12: Implement an Alert Rule Engine
# ============================================================================

@dataclass
class AlertRule:
    """Defines a threshold-based alert rule."""
    name: str
    metric: str
    operator: str         # "gt", "lt", "gte", "lte", "eq"
    threshold: float
    severity: AlertSeverity
    cooldown_minutes: int = 5


def solution_12_alert_rule_engine(
    rules: list[AlertRule],
    metrics_snapshots: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Evaluate threshold-based alert rules with cooldown support.

    Cooldown prevents alert fatigue: once an alert fires, it stays quiet
    for cooldown_minutes even if the condition persists.
    """
    # Comparator functions
    ops = {
        "gt":  lambda v, t: v > t,
        "lt":  lambda v, t: v < t,
        "gte": lambda v, t: v >= t,
        "lte": lambda v, t: v <= t,
        "eq":  lambda v, t: v == t,
    }

    # Sort snapshots chronologically
    sorted_snapshots = sorted(metrics_snapshots, key=lambda s: s["timestamp"])

    # Track last fire time per rule
    last_fired: dict[str, datetime] = {}
    fired_alerts: list[dict[str, Any]] = []

    for snapshot in sorted_snapshots:
        ts = snapshot["timestamp"]

        for rule in rules:
            metric_value = snapshot.get(rule.metric)
            if metric_value is None:
                continue

            # Check comparison
            compare = ops.get(rule.operator)
            if compare is None or not compare(metric_value, rule.threshold):
                continue

            # Check cooldown
            if rule.name in last_fired:
                elapsed = (ts - last_fired[rule.name]).total_seconds() / 60
                if elapsed < rule.cooldown_minutes:
                    continue

            # Fire the alert
            last_fired[rule.name] = ts
            fired_alerts.append({
                "rule_name": rule.name,
                "severity": rule.severity.value,
                "timestamp": ts,
                "metric_value": metric_value,
                "threshold": rule.threshold,
                "message": (
                    f"{rule.name}: {rule.metric} is {metric_value} "
                    f"(threshold: {rule.threshold})"
                ),
            })

    # Sort by timestamp then rule name
    fired_alerts.sort(key=lambda a: (a["timestamp"], a["rule_name"]))
    return fired_alerts


# ============================================================================
# Solution 13: Build a Log Retention Policy Enforcer
# ============================================================================

def solution_13_log_retention_policy(
    log_entries: list[dict[str, Any]],
    retention_days: int = 30,
    archive_days: int = 90,
    reference_date: Optional[datetime] = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Classify logs into active / archive / delete tiers.

    Retention policies are essential for cost control (storage is not free)
    and compliance (GDPR right-to-erasure, data minimization).
    """
    ref = reference_date or datetime.utcnow()

    active: list[dict[str, Any]] = []
    archive: list[dict[str, Any]] = []
    delete: list[dict[str, Any]] = []

    for entry in log_entries:
        age_days = (ref - entry["timestamp"]).days

        if age_days <= retention_days:
            active.append(entry)
        elif age_days <= archive_days:
            archive.append(entry)
        else:
            delete.append(entry)

    return {"active": active, "archive": archive, "delete": delete}


# ============================================================================
# Solution 14: Implement a Privacy-Aware Log Sanitizer
# ============================================================================

def solution_14_privacy_sanitizer(
    log_entry: dict[str, Any],
    pii_fields: list[str] | None = None,
    hash_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Sanitize logs for PII before persisting to long-term storage.

    Hashing (rather than redacting) ID fields preserves the ability to
    correlate logs across a session without storing raw identifiers.
    """
    if pii_fields is None:
        pii_fields = ["email", "phone", "ssn", "credit_card", "api_key", "password"]
    if hash_fields is None:
        hash_fields = ["customer_id", "user_id", "session_id"]

    pii_set = set(pii_fields)
    hash_set = set(hash_fields)

    def _sanitize(obj: Any) -> Any:
        """Recursively sanitize a value."""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if key in pii_set:
                    result[key] = "[REDACTED]"
                elif key in hash_set:
                    digest = hashlib.sha256(str(value).encode()).hexdigest()[:8]
                    result[key] = f"hash_{digest}"
                else:
                    result[key] = _sanitize(value)
            return result
        elif isinstance(obj, list):
            return [_sanitize(item) for item in obj]
        else:
            return obj

    return _sanitize(log_entry)


# ============================================================================
# Solution 15: Build an Observability Health Check
# ============================================================================

def solution_15_observability_health_check(
    components: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Unified health check for observability infrastructure itself.

    If your logging, metrics, or tracing pipeline is down, you are flying
    blind.  This meta-health-check catches that.
    """
    if not components:
        return {
            "overall_status": "healthy",
            "components": {},
            "total_errors_last_hour": 0,
            "unhealthy_components": [],
            "degraded_components": [],
        }

    # Use the latest heartbeat as the reference time
    reference_time = max(c["last_heartbeat"] for c in components.values())
    stale_threshold = timedelta(minutes=5)

    processed: dict[str, dict[str, Any]] = {}
    total_errors = 0

    for name, info in components.items():
        is_stale = (reference_time - info["last_heartbeat"]) > stale_threshold
        status = info["status"]
        details = info["details"]

        if is_stale:
            status = "unhealthy"
            details = details + " (stale heartbeat)"

        processed[name] = {
            "status": status,
            "last_heartbeat": info["last_heartbeat"],
            "error_count_last_hour": info["error_count_last_hour"],
            "details": details,
            "is_stale": is_stale,
        }

        total_errors += info["error_count_last_hour"]

    # Determine overall status
    statuses = [c["status"] for c in processed.values()]
    if any(s == "unhealthy" for s in statuses):
        overall = "unhealthy"
    elif any(s == "degraded" for s in statuses):
        overall = "degraded"
    else:
        overall = "healthy"

    unhealthy = sorted(n for n, c in processed.items() if c["status"] == "unhealthy")
    degraded = sorted(n for n, c in processed.items() if c["status"] == "degraded")

    return {
        "overall_status": overall,
        "components": processed,
        "total_errors_last_hour": total_errors,
        "unhealthy_components": unhealthy,
        "degraded_components": degraded,
    }


# ============================================================================
# Test Suite
# ============================================================================

if __name__ == "__main__":

    # -- Solution 1 ----------------------------------------------------------
    entry = solution_1_llm_log_entry(
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
    # Verify cost calculation: 500/1M * 5 + 200/1M * 15 = 0.0025 + 0.003 = 0.0055
    assert abs(entry["cost_usd"] - 0.0055) < 0.0001
    print("Solution 1 passed!")

    # -- Solution 2 ----------------------------------------------------------
    raw_logs = [
        {"level": "DEBUG", "message": "verbose trace", "timestamp": "t1"},
        {"level": "INFO", "message": "request started", "timestamp": "t2"},
        {"level": "WARNING", "message": "slow query", "timestamp": "t3"},
        {"level": "ERROR", "message": "api failed", "timestamp": "t4"},
    ]
    filtered = solution_2_structured_logger(raw_logs, LogLevel.WARNING)
    assert len(filtered) == 2
    assert all("log_id" in e for e in filtered)
    assert all(e["service"] == "llm-gateway" for e in filtered)
    assert all(e["environment"] == "production" for e in filtered)
    assert filtered[0]["message"] == "slow query"
    assert filtered[1]["message"] == "api failed"
    print("Solution 2 passed!")

    # -- Solution 3 ----------------------------------------------------------
    reqs = [
        {"customer_id": "A", "model": "gpt-4o", "prompt_tokens": 100, "completion_tokens": 50},
        {"customer_id": "A", "model": "gpt-4o", "prompt_tokens": 200, "completion_tokens": 100},
        {"customer_id": "B", "model": "claude-3-5-sonnet", "prompt_tokens": 300, "completion_tokens": 150},
    ]
    usage = solution_3_token_usage_tracker(reqs)
    assert usage["total_requests"] == 3
    assert usage["total_prompt_tokens"] == 600
    assert usage["total_completion_tokens"] == 300
    assert usage["total_tokens"] == 900
    assert usage["per_customer"]["A"]["total_tokens"] == 450
    assert usage["per_customer"]["B"]["requests"] == 1
    assert usage["per_model"]["gpt-4o"]["requests"] == 2
    assert usage["per_model"]["gpt-4o"]["total_tokens"] == 450
    print("Solution 3 passed!")

    # -- Solution 4 ----------------------------------------------------------
    daily = [
        {"date": "2025-01-06", "customer_id": "A", "total_tokens": 100, "total_cost_usd": 0.01, "request_count": 5},
        {"date": "2025-01-07", "customer_id": "A", "total_tokens": 200, "total_cost_usd": 0.02, "request_count": 10},
        {"date": "2025-01-13", "customer_id": "A", "total_tokens": 150, "total_cost_usd": 0.015, "request_count": 7},
    ]
    weekly = solution_4_usage_aggregator(daily, "weekly")
    assert len(weekly) == 2
    assert all("period" in w for w in weekly)
    # First week should have combined tokens from Jan 6+7
    assert weekly[0]["total_tokens"] == 300
    assert weekly[0]["request_count"] == 15
    # Monthly rollup
    monthly = solution_4_usage_aggregator(daily, "monthly")
    assert len(monthly) == 1
    assert monthly[0]["total_tokens"] == 450
    print("Solution 4 passed!")

    # -- Solution 5 ----------------------------------------------------------
    feedbacks = [
        {"request_id": "r1", "model": "gpt-4o", "thumbs_up": True, "rating": 5, "comment": "Great"},
        {"request_id": "r2", "model": "gpt-4o", "thumbs_up": False, "rating": 2, "comment": None},
        {"request_id": "r3", "model": "claude-3-5-sonnet", "thumbs_up": True, "rating": None, "comment": None},
    ]
    quality = solution_5_quality_score_calculator(feedbacks)
    assert abs(quality["overall_satisfaction"] - 2 / 3) < 0.01
    assert quality["average_rating"] == 3.5
    assert quality["total_feedback_count"] == 3
    assert quality["negative_feedback_ids"] == ["r2"]
    assert quality["per_model"]["gpt-4o"]["count"] == 2
    assert quality["per_model"]["claude-3-5-sonnet"]["satisfaction"] == 1.0
    print("Solution 5 passed!")

    # -- Solution 6 ----------------------------------------------------------
    lats = [120.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 800.0, 1200.0, 2000.0]
    pcts = solution_6_latency_percentiles(lats)
    assert pcts["min"] == 120.0
    assert pcts["max"] == 2000.0
    assert pcts["p50"] is not None
    assert pcts["mean"] is not None
    # Empty case
    empty_pcts = solution_6_latency_percentiles([])
    assert all(v is None for v in empty_pcts.values())
    print("Solution 6 passed!")

    # -- Solution 7 ----------------------------------------------------------
    costs = [
        {"date": "2025-01-01", "cost_usd": 10.0},
        {"date": "2025-01-02", "cost_usd": 12.0},
        {"date": "2025-01-03", "cost_usd": 11.0},
        {"date": "2025-01-04", "cost_usd": 50.0},
        {"date": "2025-01-05", "cost_usd": 10.5},
    ]
    anomalies = solution_7_cost_anomaly_detector(costs, z_threshold=1.5)
    assert len(anomalies) >= 1
    assert anomalies[0]["date"] == "2025-01-04"
    assert anomalies[0]["direction"] == "spike"
    assert anomalies[0]["z_score"] > 1.5
    # All-same case
    same_costs = [{"date": f"2025-01-0{i}", "cost_usd": 5.0} for i in range(1, 6)]
    assert solution_7_cost_anomaly_detector(same_costs) == []
    print("Solution 7 passed!")

    # -- Solution 8 ----------------------------------------------------------
    base_time = datetime(2025, 1, 15, 10, 0, 0)
    req_log = [
        {"timestamp": base_time + timedelta(milliseconds=i * 100), "customer_id": "C1", "endpoint": "/chat"}
        for i in range(110)
    ]
    rate_result = solution_8_rate_limit_monitor(req_log, window_seconds=60, max_requests_per_window=100)
    assert rate_result["summary"]["total_violations"] > 0
    assert "C1" in rate_result["summary"]["customers_with_violations"]
    print("Solution 8 passed!")

    # -- Solution 9 ----------------------------------------------------------
    t0 = datetime(2025, 1, 15, 10, 0, 0)
    spans = [
        SpanRecord("trace-1", "s1", None, "chain", t0, t0 + timedelta(milliseconds=500)),
        SpanRecord("trace-1", "s2", "s1", "llm_call", t0 + timedelta(milliseconds=10),
                   t0 + timedelta(milliseconds=300)),
        SpanRecord("trace-1", "s3", "s1", "retrieval", t0 + timedelta(milliseconds=5),
                   t0 + timedelta(milliseconds=200), status="error"),
        SpanRecord("trace-2", "s4", None, "simple_call", t0, t0 + timedelta(milliseconds=100)),
    ]
    trace_report = solution_9_chain_tracer(spans)
    assert trace_report["total_traces"] == 2
    assert trace_report["error_traces"] == 1
    assert trace_report["traces"]["trace-1"]["has_error"] is True
    assert trace_report["traces"]["trace-1"]["root_operation"] == "chain"
    assert trace_report["traces"]["trace-1"]["span_count"] == 3
    assert trace_report["traces"]["trace-2"]["total_duration_ms"] == 100.0
    print("Solution 9 passed!")

    # -- Solution 10 ---------------------------------------------------------
    run1 = [
        RAGStep("query_embedding", 15.0, {"query": "test"}, {"embedding_dim": 1536}),
        RAGStep("retrieval", 120.0, {"top_k": 5}, {"num_docs": 5, "avg_score": 0.86}),
        RAGStep("reranking", 45.0, {"docs": 5}, {"docs": 3}),
        RAGStep("generation", 800.0, {"context_len": 2000}, {"tokens": 500}),
    ]
    run2 = [
        RAGStep("query_embedding", 18.0, {"query": "test2"}, {"embedding_dim": 1536}),
        RAGStep("retrieval", 130.0, {"top_k": 5}, {"num_docs": 4, "avg_score": 0.78}),
        RAGStep("reranking", 50.0, {"docs": 4}, {"docs": 2}),
        RAGStep("generation", 750.0, {"context_len": 1800}, {"tokens": 450}),
    ]
    rag_report = solution_10_rag_pipeline_debugger([run1, run2])
    assert rag_report["total_runs"] == 2
    assert rag_report["bottleneck_step"] == "generation"
    assert rag_report["retrieval_analysis"]["avg_docs_retrieved"] == 4.5
    assert rag_report["retrieval_analysis"]["avg_relevance_score"] == 0.82
    # Verify percentages sum to ~100
    pct_sum = sum(s["pct_of_total"] for s in rag_report["step_analysis"].values())
    assert 99.0 < pct_sum < 101.0
    print("Solution 10 passed!")

    # -- Solution 11 ---------------------------------------------------------
    base = datetime(2025, 1, 15, 10, 0, 0)
    logs = [
        {"timestamp": base, "model": "gpt-4o", "latency_ms": 200.0,
         "prompt_tokens": 100, "completion_tokens": 50, "success": True, "cost_usd": 0.001},
        {"timestamp": base + timedelta(minutes=30), "model": "gpt-4o", "latency_ms": 300.0,
         "prompt_tokens": 200, "completion_tokens": 100, "success": False, "cost_usd": 0.002},
        {"timestamp": base + timedelta(minutes=90), "model": "claude-3-5-sonnet", "latency_ms": 150.0,
         "prompt_tokens": 150, "completion_tokens": 75, "success": True, "cost_usd": 0.0015},
    ]
    dashboard = solution_11_dashboard_data_provider(logs, time_bucket_minutes=60)
    assert len(dashboard["time_series"]) == 2
    # First bucket: 2 requests (both within first hour)
    assert dashboard["time_series"][0]["request_count"] == 2
    assert dashboard["time_series"][0]["error_count"] == 1
    assert dashboard["summary"]["total_requests"] == 3
    assert "gpt-4o" in dashboard["model_breakdown"]
    assert dashboard["model_breakdown"]["gpt-4o"]["error_rate"] == 0.5
    print("Solution 11 passed!")

    # -- Solution 12 ---------------------------------------------------------
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
    alerts = solution_12_alert_rule_engine(rules, snapshots)
    # Should fire: HighErrorRate at t0, HighLatency at t0+1min
    # HighErrorRate at t0+2min should be suppressed (cooldown=10min)
    assert len(alerts) == 2
    assert alerts[0]["rule_name"] == "HighErrorRate"
    assert alerts[0]["metric_value"] == 0.08
    assert alerts[1]["rule_name"] == "HighLatency"
    assert alerts[1]["metric_value"] == 1500.0
    print("Solution 12 passed!")

    # -- Solution 13 ---------------------------------------------------------
    ref = datetime(2025, 3, 1)
    entries = [
        {"timestamp": datetime(2025, 2, 20), "level": "INFO", "message": "recent"},
        {"timestamp": datetime(2025, 1, 15), "level": "ERROR", "message": "older"},
        {"timestamp": datetime(2024, 11, 1), "level": "WARNING", "message": "ancient"},
    ]
    result = solution_13_log_retention_policy(entries, retention_days=30,
                                              archive_days=90, reference_date=ref)
    assert len(result["active"]) == 1
    assert result["active"][0]["message"] == "recent"
    assert len(result["archive"]) == 1
    assert result["archive"][0]["message"] == "older"
    assert len(result["delete"]) == 1
    assert result["delete"][0]["message"] == "ancient"
    print("Solution 13 passed!")

    # -- Solution 14 ---------------------------------------------------------
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
    sanitized = solution_14_privacy_sanitizer(raw)
    assert sanitized["email"] == "[REDACTED]"
    assert sanitized["request"]["api_key"] == "[REDACTED]"
    assert sanitized["customer_id"].startswith("hash_")
    assert sanitized["request"]["user_id"].startswith("hash_")
    assert sanitized["model"] == "gpt-4o"
    assert sanitized["request"]["prompt"] == "Hello"
    # Original must be untouched
    assert raw["email"] == "user@example.com"
    assert raw["request"]["api_key"] == "sk-abc123"
    print("Solution 14 passed!")

    # -- Solution 15 ---------------------------------------------------------
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
    health = solution_15_observability_health_check(comps)
    assert health["overall_status"] == "unhealthy"
    assert health["components"]["logging"]["is_stale"] is False
    assert health["components"]["metrics"]["is_stale"] is False
    assert health["components"]["tracing"]["is_stale"] is True
    assert health["components"]["tracing"]["status"] == "unhealthy"
    assert "stale heartbeat" in health["components"]["tracing"]["details"]
    assert "tracing" in health["unhealthy_components"]
    assert "metrics" in health["degraded_components"]
    assert health["total_errors_last_hour"] == 3
    print("Solution 15 passed!")

    print("\n" + "=" * 60)
    print("All 15 solutions passed!")
    print("=" * 60)
