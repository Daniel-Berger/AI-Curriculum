"""
Custom middleware for request/response processing.
"""

import time
import logging
import json
from datetime import datetime
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Extract request info
        request_id = request.headers.get("X-Request-ID", "unknown")
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {exc}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": int(process_time * 1000)
                },
                exc_info=True
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {response.status_code}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": int(process_time * 1000),
                "method": request.method,
                "path": request.url.path
            }
        )

        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle and format errors."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and catch errors."""
        try:
            response = await call_next(request)
            return response

        except Exception as exc:
            # Log error
            logger.error(
                f"Unhandled error: {str(exc)}",
                extra={
                    "path": request.url.path,
                    "method": request.method
                },
                exc_info=True
            )

            # Return error response
            error_response = {
                "error": "Internal server error",
                "status_code": 500,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }

            return Response(
                content=json.dumps(error_response),
                status_code=500,
                media_type="application/json"
            )


class CORSMiddleware(BaseHTTPMiddleware):
    """Middleware to handle CORS headers."""

    def __init__(self, app, allowed_origins=None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add CORS headers to response."""
        # Handle preflight requests
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": ",".join(self.allowed_origins),
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )

        response = await call_next(request)

        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = ",".join(
            self.allowed_origins
        )
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization"
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting."""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limits before processing request."""
        client_id = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean old entries (older than 1 minute)
        if client_id in self.client_requests:
            self.client_requests[client_id] = [
                req_time for req_time in self.client_requests[client_id]
                if current_time - req_time < 60
            ]

        # Check if rate limit exceeded
        if client_id in self.client_requests:
            if len(self.client_requests[client_id]) >= self.requests_per_minute:
                logger.warning(
                    f"Rate limit exceeded for client: {client_id}"
                )
                return Response(
                    content=json.dumps({"error": "Rate limit exceeded"}),
                    status_code=429,
                    media_type="application/json"
                )

        # Add request to tracking
        if client_id not in self.client_requests:
            self.client_requests[client_id] = []
        self.client_requests[client_id].append(current_time)

        response = await call_next(request)
        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate authentication."""

    def __init__(self, app, require_auth: bool = False):
        super().__init__(app)
        self.require_auth = require_auth

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check authentication if required."""
        # Skip auth check for health endpoints
        if request.url.path in ["/health", "/ready", "/metrics"]:
            return await call_next(request)

        if self.require_auth:
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return Response(
                    content=json.dumps({"error": "Missing authorization header"}),
                    status_code=401,
                    media_type="application/json"
                )

            # Simple token validation (in production, use proper JWT/OAuth)
            if not auth_header.startswith("Bearer "):
                return Response(
                    content=json.dumps({"error": "Invalid authorization header"}),
                    status_code=401,
                    media_type="application/json"
                )

        response = await call_next(request)
        return response
