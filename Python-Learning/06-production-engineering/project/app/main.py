"""
Production ML API Service

FastAPI application with async endpoints, middleware, monitoring, and error handling.
"""

import logging
import time
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, make_wsgi_app
from starlette.middleware.wsgi import WSGIMiddleware
import uvicorn

from app.models import PredictionRequest, PredictionResponse, HealthResponse
from app.services import MLService, get_ml_service
from app.middleware import LoggingMiddleware, ErrorHandlerMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

prediction_count = Counter(
    'predictions_total',
    'Total predictions',
    ['status']
)

tokens_used = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['type']  # prompt, completion
)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("Starting ML API service")
    yield
    # Shutdown
    logger.info("Shutting down ML API service")


# Create FastAPI application
app = FastAPI(
    title="Production ML API",
    description="FastAPI-based LLM service for production",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Add Prometheus metrics endpoint
app.add_route("/metrics", make_wsgi_app()(make_wsgi_app=True), name="metrics")


@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
    """Middleware to collect request metrics."""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)

    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    response.headers["X-Process-Time"] = str(process_time)
    return response


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Liveness probe - basic health check."""
    return HealthResponse(
        status="alive",
        timestamp=datetime.utcnow().isoformat(),
        service="ml-api"
    )


@app.get("/ready", response_model=HealthResponse)
async def readiness_check(ml_service: MLService = Depends(get_ml_service)):
    """Readiness probe - check if service is ready for traffic."""
    try:
        # Check model is loaded
        if not ml_service.is_loaded():
            raise HTTPException(
                status_code=503,
                detail="Model not loaded"
            )

        return HealthResponse(
            status="ready",
            timestamp=datetime.utcnow().isoformat(),
            service="ml-api"
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service not ready"
        )


# ============================================================================
# Prediction Endpoints
# ============================================================================

@app.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    ml_service: MLService = Depends(get_ml_service)
) -> PredictionResponse:
    """
    Get prediction from LLM.

    Request body:
    {
        "prompt": "What is machine learning?",
        "max_tokens": 100
    }

    Response:
    {
        "prediction": "Machine learning is...",
        "tokens_used": 150,
        "model": "gpt-4",
        "timestamp": "2024-01-15T10:30:45.123Z"
    }
    """
    try:
        logger.info(f"Prediction request: {request.prompt[:50]}...")

        # Generate prediction
        response = await ml_service.predict(
            prompt=request.prompt,
            max_tokens=request.max_tokens
        )

        # Track metrics
        prediction_count.labels(status="success").inc()
        tokens_used.labels(type="total").inc(response.tokens_used)

        logger.info(f"Prediction successful: {response.tokens_used} tokens used")

        return response

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        prediction_count.labels(status="validation_error").inc()
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        prediction_count.labels(status="error").inc()
        raise HTTPException(status_code=500, detail="Prediction failed")


@app.post("/batch-predict")
async def batch_predict(
    requests: list[PredictionRequest],
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Batch prediction endpoint for multiple prompts.

    Request body:
    [
        {"prompt": "Question 1?", "max_tokens": 100},
        {"prompt": "Question 2?", "max_tokens": 100}
    ]

    Response:
    {
        "predictions": [
            {"prediction": "Answer 1", "tokens_used": 75},
            {"prediction": "Answer 2", "tokens_used": 82}
        ],
        "total_tokens": 157
    }
    """
    try:
        if len(requests) > 100:
            raise ValueError("Batch size cannot exceed 100")

        logger.info(f"Batch prediction request: {len(requests)} items")

        # Process all requests
        predictions = []
        total_tokens = 0

        for req in requests:
            response = await ml_service.predict(
                prompt=req.prompt,
                max_tokens=req.max_tokens
            )
            predictions.append({
                "prediction": response.prediction,
                "tokens_used": response.tokens_used
            })
            total_tokens += response.tokens_used

        prediction_count.labels(status="success").inc()

        return {
            "predictions": predictions,
            "total_tokens": total_tokens,
            "count": len(predictions)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Batch prediction failed")


# ============================================================================
# Validation Endpoints
# ============================================================================

@app.post("/validate")
async def validate_prompt(request: PredictionRequest):
    """
    Validate a prompt without generating prediction.

    Returns validation results and estimated token usage.
    """
    try:
        validation_result = {
            "valid": True,
            "prompt_length": len(request.prompt),
            "estimated_tokens": len(request.prompt) // 4,
            "max_tokens": request.max_tokens,
            "warnings": []
        }

        if len(request.prompt) < 5:
            validation_result["warnings"].append("Prompt is very short")

        if len(request.prompt) > 5000:
            validation_result["warnings"].append("Prompt is very long")

        if request.max_tokens > 2000:
            validation_result["warnings"].append("Max tokens is very high")

        return validation_result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Info Endpoints
# ============================================================================

@app.get("/info")
async def get_info(ml_service: MLService = Depends(get_ml_service)):
    """Get service information."""
    return {
        "service": "ML API",
        "version": "1.0.0",
        "model": ml_service.model_name,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": [
            "/health",
            "/ready",
            "/predict",
            "/batch-predict",
            "/validate",
            "/metrics",
            "/info"
        ]
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(
        f"HTTP error {exc.status_code}: {exc.detail}",
        extra={"endpoint": request.url.path}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected error: {str(exc)}",
        exc_info=True,
        extra={"endpoint": request.url.path}
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
