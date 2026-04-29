"""
Monitoring and Observability - Solutions

Complete implementations for all 10 exercises.
"""

import json
from typing import Dict, Any
from datetime import datetime


def solution_1_counter_metric() -> str:
    """
    Solution 1: Prometheus counter metrics for API monitoring.
    """
    return '''"""Counter metrics for API monitoring."""

from prometheus_client import Counter

# Define counters
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

api_errors_total = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type']
)

predictions_total = Counter(
    'predictions_total',
    'Total successful predictions',
    ['model', 'endpoint']
)

# Example usage
def handle_request(method: str, endpoint: str, status: int):
    """Track request."""
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()

def handle_error(endpoint: str, error_type: str):
    """Track error."""
    api_errors_total.labels(
        endpoint=endpoint,
        error_type=error_type
    ).inc()

def handle_prediction(model: str, endpoint: str):
    """Track prediction."""
    predictions_total.labels(
        model=model,
        endpoint=endpoint
    ).inc()
'''


def solution_2_gauge_metric() -> str:
    """
    Solution 2: Prometheus gauge metrics for model monitoring.
    """
    return '''"""Gauge metrics for model monitoring."""

from prometheus_client import Gauge

# Define gauges
model_accuracy_score = Gauge(
    'model_accuracy_score',
    'Current model accuracy',
    ['model_version']
)

model_inference_latency_ms = Gauge(
    'model_inference_latency_ms',
    'Average inference latency (milliseconds)',
    ['model_version']
)

cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Cache hit rate (0-1)',
    ['cache_name']
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

# Update functions
def update_model_metrics(accuracy: float, latency_ms: float, version: str):
    """Update model metrics."""
    model_accuracy_score.labels(model_version=version).set(accuracy)
    model_inference_latency_ms.labels(model_version=version).set(latency_ms)

def update_cache_metrics(hit_rate: float, cache_name: str):
    """Update cache metrics."""
    cache_hit_rate.labels(cache_name=cache_name).set(hit_rate)

def update_active_users(count: int):
    """Update active user count."""
    active_users.set(count)
'''


def solution_3_histogram_metric() -> str:
    """
    Solution 3: Prometheus histogram metrics for performance tracking.
    """
    return '''"""Histogram metrics for performance tracking."""

from prometheus_client import Histogram
import time
from contextlib import contextmanager

# Define histograms with custom buckets
api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration (seconds)',
    ['endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

model_inference_time = Histogram(
    'model_inference_time_seconds',
    'Model inference time (seconds)',
    ['model_name'],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0)
)

db_query_time = Histogram(
    'db_query_time_seconds',
    'Database query time (seconds)',
    ['query_type'],
    buckets=(0.001, 0.01, 0.05, 0.1, 0.5, 1.0)
)

# Context managers for timing
@contextmanager
def measure_request_time(endpoint: str):
    """Measure API request time."""
    with api_request_duration.labels(endpoint=endpoint).time():
        yield

@contextmanager
def measure_inference_time(model_name: str):
    """Measure model inference time."""
    with model_inference_time.labels(model_name=model_name).time():
        yield

@contextmanager
def measure_query_time(query_type: str):
    """Measure database query time."""
    with db_query_time.labels(query_type=query_type).time():
        yield

# Example usage
def get_user_data(user_id: int):
    """Get user data with timing."""
    with measure_query_time('select_user'):
        # Actual database query
        return {"user_id": user_id, "name": "John"}

def predict(features: list, model_name: str):
    """Run inference with timing."""
    with measure_inference_time(model_name):
        # Actual model inference
        return 0.95
'''


def solution_4_json_logging_setup() -> str:
    """
    Solution 4: Structured JSON logging setup for FastAPI.
    """
    return '''"""JSON logging setup for FastAPI."""

import logging
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime
import uuid

# Configure JSON logger
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s',
    timestamp=True
)
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

# Context manager for adding trace ID
class LogContext:
    def __init__(self, trace_id: str = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.service_name = "ml-api"
        self.version = "1.0.0"

    def log(self, level: str, message: str, **extra):
        """Log with context."""
        context = {
            "service_name": self.service_name,
            "version": self.version,
            "trace_id": self.trace_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        context.update(extra)

        log_func = getattr(logger, level)
        log_func(message, extra=context)

# Example usage
log_ctx = LogContext()
log_ctx.log("info", "API started", port=8000)
log_ctx.log("error", "Database connection failed", error="timeout")
'''


def solution_5_llm_monitoring_logs() -> str:
    """
    Solution 5: Structured logs for LLM usage monitoring.
    """
    return '''"""LLM usage monitoring logs."""

import logging
import json
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LLMMonitor:
    """Monitor and log LLM usage."""

    @staticmethod
    def log_api_call(
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cost: float,
        user_id: str,
        session_id: str,
        timestamp: str = None
    ) -> None:
        """Log LLM API call."""
        timestamp = timestamp or datetime.utcnow().isoformat()

        logger.info(
            "LLM API call",
            extra={
                "event_type": "llm_api_call",
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost_usd": cost,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": timestamp,
            }
        )

    @staticmethod
    def log_api_error(
        model: str,
        error_type: str,
        error_message: str,
        user_id: str,
        session_id: str,
        traceback: str = None
    ) -> None:
        """Log LLM API error."""

        logger.error(
            "LLM API error",
            extra={
                "event_type": "llm_api_error",
                "model": model,
                "error_type": error_type,
                "error_message": error_message,
                "user_id": user_id,
                "session_id": session_id,
                "traceback": traceback,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @staticmethod
    def log_token_usage_daily(
        model: str,
        total_tokens: int,
        cost: float,
        date: str
    ) -> None:
        """Log daily token usage summary."""

        logger.info(
            "Daily token usage",
            extra={
                "event_type": "daily_token_summary",
                "model": model,
                "total_tokens": total_tokens,
                "total_cost_usd": cost,
                "date": date,
            }
        )

# Example usage
monitor = LLMMonitor()
monitor.log_api_call(
    model="gpt-4",
    prompt_tokens=150,
    completion_tokens=200,
    total_tokens=350,
    cost=0.0105,
    user_id="user123",
    session_id="sess456"
)
'''


def solution_6_health_check_endpoints() -> str:
    """
    Solution 6: Health check endpoints for FastAPI.
    """
    return '''"""Health check endpoints for FastAPI."""

from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health_check():
    """Liveness probe: Is service running?"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ml-api"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe: Can service handle requests?"""
    status = {
        "status": "ready",
        "components": {
            "database": "unknown",
            "model": "unknown",
            "cache": "unknown"
        }
    }

    # Check database
    try:
        # await db.execute("SELECT 1")
        status["components"]["database"] = "ok"
    except Exception:
        status["components"]["database"] = "error"
        status["status"] = "not_ready"

    # Check model
    try:
        # model is not None
        status["components"]["model"] = "ok"
    except Exception:
        status["components"]["model"] = "error"
        status["status"] = "not_ready"

    # Check cache
    try:
        # await redis.ping()
        status["components"]["cache"] = "ok"
    except Exception:
        status["components"]["cache"] = "error"
        status["status"] = "not_ready"

    http_status = 200 if status["status"] == "ready" else 503
    return status, http_status

@app.get("/startup")
async def startup_check():
    """Startup probe: Has service initialized?"""
    return {
        "initialized": True,
        "timestamp": datetime.utcnow().isoformat()
    }
'''


def solution_7_health_check_with_dependencies() -> str:
    """
    Solution 7: Health checks with database and external service checks.
    """
    return '''"""Comprehensive health checks with dependency checks."""

import asyncio
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

class HealthChecker:
    """Check various service dependencies."""

    @staticmethod
    async def check_database() -> tuple[bool, str]:
        """Check database connectivity."""
        try:
            # await db.execute("SELECT 1")
            return True, "ok"
        except Exception as e:
            return False, str(e)

    @staticmethod
    async def check_cache() -> tuple[bool, str]:
        """Check Redis cache connectivity."""
        try:
            # await redis.ping()
            return True, "ok"
        except Exception as e:
            return False, str(e)

    @staticmethod
    async def check_model() -> tuple[bool, str]:
        """Check model availability."""
        try:
            # if model is not None and model.weights_loaded()
            return True, "ok"
        except Exception as e:
            return False, str(e)

    @staticmethod
    async def check_llm_api() -> tuple[bool, str]:
        """Check external LLM API."""
        try:
            # response = await llm_client.health_check()
            return True, "ok"
        except Exception as e:
            return False, str(e)

@app.get("/ready")
async def readiness():
    """Comprehensive readiness check."""
    checker = HealthChecker()

    results = await asyncio.gather(
        checker.check_database(),
        checker.check_cache(),
        checker.check_model(),
        checker.check_llm_api()
    )

    db_ok, db_msg = results[0]
    cache_ok, cache_msg = results[1]
    model_ok, model_msg = results[2]
    llm_ok, llm_msg = results[3]

    all_ok = all([db_ok, cache_ok, model_ok, llm_ok])

    response = {
        "status": "ready" if all_ok else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": {"status": "ok" if db_ok else "error", "message": db_msg},
            "cache": {"status": "ok" if cache_ok else "error", "message": cache_msg},
            "model": {"status": "ok" if model_ok else "error", "message": model_msg},
            "llm_api": {"status": "ok" if llm_ok else "error", "message": llm_msg}
        }
    }

    http_status = 200 if all_ok else 503
    return response, http_status
'''


def solution_8_prometheus_alert_rules() -> str:
    """
    Solution 8: Prometheus alerting rules for ML service.
    """
    return """groups:
  - name: ml_service_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(api_errors_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} over 5m"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 1.0
        for: 10m
        annotations:
          summary: "High API latency"
          description: "P95 latency is {{ $value | humanizeDuration }}"

      - alert: LowModelAccuracy
        expr: model_accuracy_score < 0.85
        for: 1h
        annotations:
          summary: "Model accuracy dropped"
          description: "Accuracy is {{ $value | humanizePercentage }}"

      - alert: HighLLMErrorRate
        expr: rate(llm_api_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High LLM API error rate"
          description: "LLM error rate is {{ $value | humanizePercentage }}"

      - alert: LowCacheHitRate
        expr: cache_hit_rate < 0.5
        for: 15m
        annotations:
          summary: "Cache hit rate too low"
          description: "Cache hit rate is {{ $value | humanizePercentage }}"

      - alert: ServiceDown
        expr: up{job="ml-api"} == 0
        for: 1m
        annotations:
          summary: "Service is down"
"""


def solution_9_opentelemetry_tracing() -> str:
    """
    Solution 9: OpenTelemetry distributed tracing setup.
    """
    return '''"""OpenTelemetry distributed tracing setup."""

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from fastapi import FastAPI

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# Set up tracer provider
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(
    SimpleSpanProcessor(jaeger_exporter)
)
trace.set_tracer_provider(tracer_provider)

# Get tracer
tracer = trace.get_tracer(__name__)

# Instrument FastAPI
app = FastAPI()
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Manual span creation
async def predict(features: list):
    """Run prediction with spans."""
    with tracer.start_as_current_span("predict") as span:
        span.set_attribute("features.size", len(features))

        with tracer.start_as_current_span("load_model") as model_span:
            model_span.set_attribute("model.version", "1.0")
            model = load_model()

        with tracer.start_as_current_span("inference") as infer_span:
            infer_span.set_attribute("batch.size", 1)
            prediction = model.predict(features)

        with tracer.start_as_current_span("save_result"):
            save_to_db(prediction)

        return prediction
'''


def solution_10_dashboard_specification() -> Dict[str, Any]:
    """
    Solution 10: Grafana dashboard specification for ML API.
    """
    return {
        "dashboard": {
            "title": "ML API Monitoring",
            "timezone": "UTC",
            "tags": ["ml", "api", "production"],
            "panels": [
                {
                    "title": "Request Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(http_requests_total[5m])'
                        }
                    ]
                },
                {
                    "title": "Error Rate",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": 'rate(api_errors_total[5m])'
                        }
                    ]
                },
                {
                    "title": "P95 Latency",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))'
                        }
                    ]
                },
                {
                    "title": "Model Accuracy",
                    "type": "gauge",
                    "targets": [
                        {
                            "expr": 'model_accuracy_score'
                        }
                    ]
                },
                {
                    "title": "Inference Time",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(model_inference_time_seconds_bucket[5m])'
                        }
                    ]
                },
                {
                    "title": "Active Users",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": 'active_users'
                        }
                    ]
                },
                {
                    "title": "Cache Hit Rate",
                    "type": "gauge",
                    "targets": [
                        {
                            "expr": 'cache_hit_rate'
                        }
                    ]
                },
                {
                    "title": "LLM Token Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(llm_tokens_total[1h])'
                        }
                    ]
                }
            ]
        }
    }


if __name__ == "__main__":
    print("Monitoring Solutions:")
    print("=" * 60)
    print("\nSolution 1: Counter Metrics")
    print(solution_1_counter_metric()[:200] + "...")
    print("\nSolution 10: Dashboard Spec")
    import json
    spec = solution_10_dashboard_specification()
    print(json.dumps(spec, indent=2)[:200] + "...")
