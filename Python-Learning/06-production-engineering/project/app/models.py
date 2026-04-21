"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PredictionRequest(BaseModel):
    """Request model for prediction endpoint."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Input prompt for the model"
    )

    max_tokens: int = Field(
        default=100,
        ge=1,
        le=2000,
        description="Maximum tokens to generate"
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Controls randomness (0=deterministic, 2=maximum randomness)"
    )

    top_p: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What is machine learning?",
                "max_tokens": 100,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint."""

    prediction: str = Field(
        ...,
        description="Generated prediction from the model"
    )

    tokens_used: int = Field(
        ...,
        description="Total tokens used (prompt + completion)"
    )

    model: str = Field(
        default="gpt-4",
        description="Model name used for prediction"
    )

    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp of prediction"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prediction": "Machine learning is a subset of artificial intelligence...",
                "tokens_used": 150,
                "model": "gpt-4",
                "timestamp": "2024-01-15T10:30:45.123Z"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoints."""

    status: str = Field(
        ...,
        description="Health status (alive, ready, error)"
    )

    timestamp: str = Field(
        ...,
        description="Timestamp of health check"
    )

    service: str = Field(
        default="ml-api",
        description="Service name"
    )

    details: Optional[dict] = Field(
        default=None,
        description="Additional health details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ready",
                "timestamp": "2024-01-15T10:30:45.123Z",
                "service": "ml-api",
                "details": {
                    "database": "ok",
                    "model": "loaded",
                    "cache": "ok"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error endpoints."""

    error: str = Field(
        ...,
        description="Error message"
    )

    status_code: int = Field(
        ...,
        description="HTTP status code"
    )

    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp of error"
    )

    details: Optional[dict] = Field(
        default=None,
        description="Additional error details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation error",
                "status_code": 400,
                "timestamp": "2024-01-15T10:30:45.123Z",
                "details": {
                    "field": "prompt",
                    "reason": "Field is required"
                }
            }
        }


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""

    requests_total: int
    errors_total: int
    average_latency_ms: float
    model_accuracy: float
    tokens_used_total: int

    class Config:
        json_schema_extra = {
            "example": {
                "requests_total": 1000,
                "errors_total": 5,
                "average_latency_ms": 125.5,
                "model_accuracy": 0.95,
                "tokens_used_total": 150000
            }
        }


class InfoResponse(BaseModel):
    """Response model for info endpoint."""

    service: str
    version: str
    model: str
    timestamp: str
    endpoints: list[str]

    class Config:
        json_schema_extra = {
            "example": {
                "service": "ML API",
                "version": "1.0.0",
                "model": "gpt-4",
                "timestamp": "2024-01-15T10:30:45.123Z",
                "endpoints": [
                    "/health",
                    "/ready",
                    "/predict",
                    "/batch-predict",
                    "/metrics"
                ]
            }
        }
