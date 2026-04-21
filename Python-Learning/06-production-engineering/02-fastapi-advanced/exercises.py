"""
FastAPI Advanced - Exercises

12 exercises covering:
- Async endpoints and concurrency
- Server-Sent Events (SSE) streaming
- Middleware and request/response handling
- Authentication and authorization
- WebSocket communication
- Testing with TestClient
"""

from typing import Generator, AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException, WebSocket, Request, Response
from pydantic import BaseModel
import asyncio


# ============================================================================
# Exercise 1: Async Endpoints and Concurrency
# ============================================================================

app = FastAPI()


class DataModel(BaseModel):
    """Model for exercise data."""
    id: int
    name: str
    value: float


def exercise_1_slow_async_operation() -> AsyncGenerator[str, None]:
    """
    Exercise 1: Implement an async function that simulates a slow I/O operation.
    Should take 2 seconds to complete and return a status message.

    Returns:
        AsyncGenerator that yields a completion message.
    """
    pass


async def exercise_2_concurrent_requests(request_ids: list[int]) -> dict:
    """
    Exercise 2: Create a function that processes multiple requests concurrently.
    Each request should take 1 second. Process all concurrently and return results.

    Args:
        request_ids: List of request IDs to process

    Returns:
        Dictionary with processed results
    """
    pass


# ============================================================================
# Exercise 3: Server-Sent Events (SSE)
# ============================================================================

def exercise_3_sse_generator() -> Generator[str, None, None]:
    """
    Exercise 3: Create a SSE generator that yields formatted SSE messages.
    Yield 5 messages with 1-second delays between them.
    Format: "data: {message}\n\n"

    Yields:
        Formatted SSE event strings
    """
    pass


async def exercise_4_async_sse_generator() -> AsyncGenerator[str, None]:
    """
    Exercise 4: Create an async SSE generator for real-time data streaming.
    Yield temperature readings every 500ms for 5 iterations.

    Yields:
        JSON-formatted SSE messages with temperature data
    """
    pass


# ============================================================================
# Exercise 5-6: Middleware
# ============================================================================

def exercise_5_request_logging_middleware(request: Request, call_next) -> Response:
    """
    Exercise 5: Implement middleware that logs request method, path, and response status.
    Should add a custom response header "X-Request-Time" with processing time in ms.

    Args:
        request: The incoming request
        call_next: The next middleware/handler

    Returns:
        Response with added headers
    """
    pass


class RequestCounterMiddleware:
    """
    Exercise 6: Implement middleware class that counts total requests.
    Should maintain a counter and add it to response headers as "X-Request-Count".
    """

    def __init__(self, app: FastAPI) -> None:
        """Initialize the middleware."""
        pass

    async def __call__(self, request: Request, call_next) -> Response:
        """Process request and track count."""
        pass


# ============================================================================
# Exercise 7-8: Authentication and Authorization
# ============================================================================

def exercise_7_api_key_dependency(api_key: str = None) -> str:
    """
    Exercise 7: Create a dependency that validates an API key.
    Check if api_key is exactly "secret-key-123".
    Raise HTTPException with status 403 if invalid.

    Args:
        api_key: The API key to validate

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is invalid
    """
    pass


class BearerTokenDependency:
    """
    Exercise 8: Create a dependency class for Bearer token authentication.
    Extract token from Authorization header (format: "Bearer {token}").
    Validate that token matches "valid-token-xyz".
    """

    def __call__(self, authorization: str = None) -> str:
        """
        Validate Bearer token and return it.

        Args:
            authorization: Authorization header value

        Returns:
            The validated token

        Raises:
            HTTPException: If token is missing or invalid
        """
        pass


# ============================================================================
# Exercise 9-10: WebSocket Communication
# ============================================================================

async def exercise_9_websocket_echo(websocket: WebSocket) -> None:
    """
    Exercise 9: Implement a WebSocket endpoint that echoes messages.
    Accept connection, receive 3 messages, echo each back, close connection.

    Args:
        websocket: The WebSocket connection
    """
    pass


async def exercise_10_websocket_broadcast(websocket: WebSocket, room_id: str) -> None:
    """
    Exercise 10: Implement WebSocket with broadcast functionality.
    When a message is received, format it as "{room_id}: {message}"
    and prepare for broadcasting to other clients in same room.

    Args:
        websocket: The WebSocket connection
        room_id: The room identifier for message scoping
    """
    pass


# ============================================================================
# Exercise 11-12: Testing with TestClient
# ============================================================================

def exercise_11_test_json_response() -> dict:
    """
    Exercise 11: Write test code (as dict) for TestClient.
    Test a GET /data endpoint that should return status 200 and JSON data.
    The response should contain keys: "status", "data", "timestamp".

    Returns:
        Dictionary describing the test assertions
    """
    pass


def exercise_12_test_error_handling() -> dict:
    """
    Exercise 12: Write test code for error handling.
    Test a POST /validate endpoint that should return 422 if input is invalid.
    Should also test recovery with valid input (status 200).

    Returns:
        Dictionary describing test assertions and error cases
    """
    pass
