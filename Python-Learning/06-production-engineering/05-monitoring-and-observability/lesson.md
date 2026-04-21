# Monitoring and Observability: Production Insights

## Overview

Observability is the ability to understand system state through external outputs. Monitoring collects metrics, logs, and traces to detect issues and optimize performance.

## 1. Three Pillars of Observability

### Metrics
Quantitative measurements of system behavior over time.

**Types:**
- Counter: Monotonically increasing (requests, errors)
- Gauge: Current value (CPU usage, memory)
- Histogram: Distribution of values (response times)
- Summary: Aggregated statistics (percentiles)

**Examples:**
```
http_requests_total{method="POST",endpoint="/predict"} 1024
model_inference_duration_seconds_bucket{le=0.1} 950
model_accuracy_score{model="v2.1"} 0.92
```

### Logs
Discrete events with detailed context.

**Structured Logging:**
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "error",
  "service": "ml-api",
  "user_id": "user123",
  "endpoint": "/predict",
  "error": "ModelInferenceError",
  "message": "Failed to load model weights",
  "trace_id": "abc123def456"
}
```

### Traces
Distributed request flows across services.

**Example Trace:**
```
Request: predict_user_model [0ms - 500ms]
├─ Load model [10ms - 50ms]
├─ Validate input [50ms - 80ms]
├─ ML inference [80ms - 450ms]
│  ├─ GPU forward pass [100ms - 400ms]
│  └─ Post-processing [400ms - 450ms]
└─ Write result to DB [450ms - 500ms]
```

## 2. Prometheus Metrics

Prometheus is a metrics collection and alerting system.

### Metric Types

**Counter:**
```python
from prometheus_client import Counter

request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint']
)

request_count.labels(method='POST', endpoint='/predict').inc()
```

**Gauge:**
```python
from prometheus_client import Gauge

model_load_time = Gauge(
    'model_load_time_seconds',
    'Time to load model'
)

model_load_time.set(2.345)
```

**Histogram:**
```python
from prometheus_client import Histogram

inference_time = Histogram(
    'inference_duration_seconds',
    'Model inference duration',
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
)

with inference_time.time():
    predictions = model.predict(data)
```

### Integration with FastAPI

```python
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, make_wsgi_app
from prometheus_client import REGISTRY

app = FastAPI()

request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

@app.middleware("http")
async def add_metrics(request, call_next):
    with request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).time():
        response = await call_next(request)
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        return response

@app.get("/metrics")
async def metrics():
    return make_wsgi_app()(request)
```

## 3. Structured Logging

Structured logs enable easy parsing and analysis.

### Python Logging

```python
import logging
import json
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Log with context
logger.info("model_prediction", extra={
    "user_id": "user123",
    "model_version": "v2.1",
    "inference_time_ms": 125,
    "confidence": 0.95
})
```

### Log Aggregation

Forward logs to centralized systems:
- Elasticsearch + Kibana
- Splunk
- CloudWatch
- Datadog

```python
from pythonjsonlogger import jsonlogger
import logging.handlers

handler = logging.handlers.SysLogHandler(
    address=('logs.example.com', 514)
)
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

## 4. LLM-Specific Monitoring

### Token Usage Tracking

```python
from prometheus_client import Counter, Histogram

tokens_used = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'type']  # type: prompt, completion
)

token_cost = Counter(
    'llm_cost_dollars',
    'LLM API cost',
    ['model']
)

# Track usage
tokens_used.labels(model='gpt-4', type='prompt').inc(150)
tokens_used.labels(model='gpt-4', type='completion').inc(200)
token_cost.labels(model='gpt-4').inc(0.0045)
```

### Response Quality Monitoring

```python
response_quality = Histogram(
    'llm_response_quality_score',
    'User-rated response quality (1-5)',
    buckets=[1, 2, 3, 4, 5]
)

response_latency = Histogram(
    'llm_response_latency_seconds',
    'LLM response generation latency',
    ['model']
)

# Track quality and latency
response_quality.observe(4.5)
with response_latency.labels(model='gpt-4').time():
    response = llm.generate(prompt)
```

## 5. Health Checks

Endpoints exposing system health for load balancers and orchestrators.

### Implementation

```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health_check():
    """Liveness probe: Is service running?"""
    return {"status": "alive", "timestamp": datetime.utcnow()}

@app.get("/ready")
async def readiness_check():
    """Readiness probe: Can service handle requests?"""
    # Check dependencies
    db_ok = await check_database()
    model_loaded = model is not None
    cache_ok = await check_redis()

    if not (db_ok and model_loaded and cache_ok):
        return {"status": "not_ready"}, 503

    return {"status": "ready"}

@app.get("/startup")
async def startup_check():
    """Startup probe: Has service initialized?"""
    return {"initialized": True}
```

### Kubernetes Probes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ml-api
spec:
  containers:
  - name: api
    image: ml-api:latest

    livenessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 30

    readinessProbe:
      httpGet:
        path: /ready
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 10
```

## 6. Alerting

Proactive notifications when thresholds are exceeded.

### Prometheus Alerting Rules

```yaml
groups:
  - name: ml_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(api_errors_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "Error rate above 5%"

      - alert: SlowInference
        expr: histogram_quantile(0.95, request_duration) > 1.0
        for: 10m
        annotations:
          summary: "P95 inference latency > 1s"

      - alert: LowModelAccuracy
        expr: model_accuracy_score < 0.85
        for: 1h
        annotations:
          summary: "Model accuracy dropped below 85%"

      - alert: HighTokenCost
        expr: increase(llm_cost_dollars[1h]) > 100
        annotations:
          summary: "Hourly LLM cost exceeding $100"
```

### Alert Routing

```yaml
global:
  resolve_timeout: 5m

route:
  receiver: 'critical'
  group_by: ['alertname']
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'
```

## 7. Distributed Tracing

Track requests across services.

### OpenTelemetry

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    jaeger_exporter
)
tracer = trace.get_tracer(__name__)

# Create spans
with tracer.start_as_current_span("predict"):
    with tracer.start_as_current_span("load_model"):
        model = load_model()

    with tracer.start_as_current_span("inference"):
        prediction = model.predict(input_data)
```

## 8. Dashboards

Visualize metrics and system state.

**Key Dashboards:**
- System Health: CPU, memory, disk, network
- Application Metrics: Request rate, latency, errors
- Model Performance: Accuracy, inference time, token usage
- Business Metrics: User activity, cost, ROI
- Alerts: Active and resolved alerts

## 9. Best Practices

1. **Instrument Early**
   - Add metrics from day one
   - Don't try to retrofit monitoring

2. **Use Context and Correlation IDs**
   - Trace requests across services
   - Debug distributed issues

3. **Alert on Symptoms, Not Causes**
   - Alert on user impact
   - Avoid alert fatigue

4. **Combine Signals**
   - Correlate metrics, logs, traces
   - Find root causes faster

5. **Test Alerts**
   - Verify alert conditions work
   - Test notification channels

6. **Privacy in Logs**
   - Don't log PII
   - Mask sensitive data
   - Follow data regulations

## 10. Observability Maturity

**Level 1**: Basic metrics on key endpoints
**Level 2**: Structured logging with context
**Level 3**: Distributed tracing across services
**Level 4**: Anomaly detection and predictive alerts
**Level 5**: Autonomous issue detection and resolution

## Summary

Effective observability enables:
- Rapid incident detection and response
- Performance optimization insights
- User experience improvements
- Cost optimization for LLM-powered systems
- Compliance and audit trails

Invest in observability infrastructure early to understand your system's behavior and maintain reliability at scale.
