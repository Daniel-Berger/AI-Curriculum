"""
API Middleware Module
====================

Configures and applies middleware for the FastAPI application:

- **CORS**: Cross-Origin Resource Sharing for frontend access
- **Authentication**: API key validation via headers
- **Rate Limiting**: Token bucket rate limiting per API key
- **Request Logging**: Structured logging of all requests with timing
- **Request ID**: Assigns a unique ID to each request for tracing

Middleware is applied in order, with the outermost middleware executing first.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Validate API keys from request headers.

    Checks for an 'X-API-Key' header and validates it against
    a configured set of allowed keys. Skips authentication for
    health check and documentation endpoints.

    Parameters
    ----------
    app : FastAPI
        The ASGI application.
    api_keys : dict
        Mapping of API key to metadata (owner, tier, etc.).
    exempt_paths : list of str
        Paths that don't require authentication.
    """

    def __init__(
        self,
        app: Any,
        api_keys: Optional[Dict[str, Dict[str, Any]]] = None,
        exempt_paths: Optional[list] = None,
    ) -> None:
        super().__init__(app)
        self.api_keys = api_keys or {}
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/redoc", "/openapi.json"]

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Validate the API key and pass the request through.

        Parameters
        ----------
        request : Request
            Incoming HTTP request.
        call_next : callable
            Next middleware or route handler.

        Returns
        -------
        Response
            HTTP response.
        """
        raise NotImplementedError


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token bucket rate limiting per API key.

    Parameters
    ----------
    app : FastAPI
        The ASGI application.
    requests_per_minute : int
        Default rate limit per API key.
    burst_size : int
        Maximum burst size (bucket capacity).
    """

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 60,
        burst_size: int = 10,
    ) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self._buckets: Dict[str, Dict[str, float]] = {}

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Check rate limit and pass through or reject.

        Parameters
        ----------
        request : Request
            Incoming request.
        call_next : callable
            Next handler.

        Returns
        -------
        Response
            HTTP response (429 if rate limited).
        """
        raise NotImplementedError


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing, status, and metadata.

    Emits structured log entries with:
    - Request ID, method, path, query parameters
    - Response status code and latency
    - API key (masked) and user-agent
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Log the request and response with timing.

        Parameters
        ----------
        request : Request
            Incoming request.
        call_next : callable
            Next handler.

        Returns
        -------
        Response
            HTTP response with added X-Request-ID header.
        """
        raise NotImplementedError


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assign a unique request ID to each incoming request.

    The ID is added to the request state and the response headers
    as 'X-Request-ID' for distributed tracing.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Add a request ID and pass through.

        Parameters
        ----------
        request : Request
            Incoming request.
        call_next : callable
            Next handler.

        Returns
        -------
        Response
            Response with X-Request-ID header.
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def setup_middleware(app: FastAPI) -> None:
    """Apply all middleware to the FastAPI application.

    Middleware is applied in reverse order (last added = outermost).

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.
    """
    # CORS -- outermost
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID -- early, so other middleware can use it
    app.add_middleware(RequestIDMiddleware)

    # Request logging
    app.add_middleware(RequestLoggingMiddleware)

    # Note: Auth and Rate Limiting are commented out until API keys are configured
    # app.add_middleware(AuthenticationMiddleware, api_keys={...})
    # app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
