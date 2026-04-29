"""
Monitoring and Observability - Exercises

10 exercises covering:
- Prometheus metrics (counter, gauge, histogram)
- Structured logging
- Health checks
- Alerting rules
- Distributed tracing
- Dashboard design
"""

from typing import Dict, List, Any


# ============================================================================
# Exercise 1-3: Prometheus Metrics
# ============================================================================

def exercise_1_counter_metric() -> str:
    """
    Exercise 1: Create Prometheus counter metrics for API monitoring.

    Requirements:
    - Counter for total HTTP requests
    - Counter for API errors
    - Counter for successful predictions
    - Labels for method, endpoint, status
    - Return code that increments counters

    Returns:
        Complete Python code implementing counters
    """
    pass


def exercise_2_gauge_metric() -> str:
    """
    Exercise 2: Create Prometheus gauge metrics for model monitoring.

    Requirements:
    - Gauge for model accuracy score
    - Gauge for model inference latency (ms)
    - Gauge for cache hit rate (0-1)
    - Gauge for active users
    - Function to update gauges based on current values

    Returns:
        Complete Python code implementing gauges
    """
    pass


def exercise_3_histogram_metric() -> str:
    """
    Exercise 3: Create Prometheus histogram metrics for performance tracking.

    Requirements:
    - Histogram for API request duration
    - Histogram for model inference time
    - Histogram for database query time
    - Custom buckets for each (e.g., 0.01, 0.05, 0.1, 0.5, 1.0)
    - Context manager to measure timing
    - Return code with example usage

    Returns:
        Complete Python code implementing histograms
    """
    pass


# ============================================================================
# Exercise 4-5: Structured Logging
# ============================================================================

def exercise_4_json_logging_setup() -> str:
    """
    Exercise 4: Set up structured JSON logging for FastAPI application.

    Requirements:
    - Configure JSON logger with python-json-logger
    - Create custom formatter with timestamps
    - Log at multiple levels (debug, info, warning, error)
    - Include context fields: service_name, version, trace_id
    - Return complete logging configuration code

    Returns:
        Complete Python code for logging setup
    """
    pass


def exercise_5_llm_monitoring_logs() -> str:
    """
    Exercise 5: Create structured logs for LLM usage monitoring.

    Requirements:
    - Log LLM API calls with model name, tokens used
    - Log prompt and completion tokens separately
    - Log cost and timestamp
    - Include user ID and session ID
    - Log error cases with full error details
    - Return code that logs various LLM scenarios

    Returns:
        Complete Python code for LLM logging
    """
    pass


# ============================================================================
# Exercise 6-7: Health Checks
# ============================================================================

def exercise_6_health_check_endpoints() -> str:
    """
    Exercise 6: Create health check endpoints for FastAPI.

    Requirements:
    - /health (liveness): Always return 200
    - /ready (readiness): Check DB, model, cache dependencies
    - /startup (startup): Check initialization status
    - Return detailed status information
    - Use appropriate status codes

    Returns:
        Complete FastAPI endpoint code
    """
    pass


def exercise_7_health_check_with_dependencies() -> str:
    """
    Exercise 7: Implement health checks with database and external service checks.

    Requirements:
    - Check PostgreSQL database connectivity
    - Check Redis cache connectivity
    - Check model availability (weights loaded)
    - Check external LLM API availability
    - Return component-wise status
    - Set appropriate HTTP status codes based on component health

    Returns:
        Complete Python code for comprehensive health checks
    """
    pass


# ============================================================================
# Exercise 8: Alerting Rules
# ============================================================================

def exercise_8_prometheus_alert_rules() -> str:
    """
    Exercise 8: Create Prometheus alerting rules for ML service.

    Requirements:
    - Alert if error rate > 5% over 5 minutes
    - Alert if P95 latency > 1 second
    - Alert if model accuracy drops below 0.85
    - Alert if LLM API errors > 10% of requests
    - Alert if cache hit rate drops below 50%
    - Return YAML alerting rules

    Returns:
        Complete Prometheus alerting rules YAML
    """
    pass


# ============================================================================
# Exercise 9: Distributed Tracing
# ============================================================================

def exercise_9_opentelemetry_tracing() -> str:
    """
    Exercise 9: Set up OpenTelemetry distributed tracing.

    Requirements:
    - Configure Jaeger exporter
    - Create spans for API request lifecycle
    - Create child spans for: model loading, inference, DB query
    - Add attributes to spans (model_version, input_size, etc.)
    - Configure trace context propagation
    - Return complete setup and usage code

    Returns:
        Complete Python code for OpenTelemetry tracing
    """
    pass


# ============================================================================
# Exercise 10: Monitoring Dashboard Design
# ============================================================================

def exercise_10_dashboard_specification() -> Dict[str, Any]:
    """
    Exercise 10: Design a Grafana dashboard specification for ML API.

    Requirements:
    - Define 6-8 panels for key metrics
    - Include system health (CPU, memory, disk)
    - Include API metrics (requests, latency, errors)
    - Include model metrics (accuracy, inference time, token usage)
    - Include business metrics (active users, cost)
    - Return dashboard structure with panel definitions

    Returns:
        Dictionary with dashboard specification
    """
    pass
