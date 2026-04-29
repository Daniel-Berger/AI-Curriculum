"""
FastAPI Advanced - Solutions

Complete implementations for all 12 exercises.
"""

import asyncio
import time
from typing import Generator, AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException, WebSocket, Request, Response
from fastapi.testclient import TestClient
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
import json


class DataModel(BaseModel):
    """Model for exercise data."""
    id: int
    name: str
    value: float


# ============================================================================
# Solution 1: Async Endpoints and Concurrency
# ============================================================================

async def solution_1_slow_async_operation() -> AsyncGenerator[str, None]:
    """
    Solution 1: Async function simulating slow I/O operation.
    Takes 2 seconds and yields a status message.
    """
    await asyncio.sleep(2)
    yield "Operation completed successfully"


async def solution_2_concurrent_requests(request_ids: list[int]) -> dict:
    """
    Solution 2: Process multiple requests concurrently using asyncio.gather.
    """
    async def process_request(request_id: int) -> dict:
        await asyncio.sleep(1)
        return {"id": request_id, "status": "completed", "result": request_id * 2}

    results = await asyncio.gather(*[process_request(rid) for rid in request_ids])
    return {"total": len(results), "results": results}


# ============================================================================
# Solution 3-4: Server-Sent Events (SSE)
# ============================================================================

def solution_3_sse_generator() -> Generator[str, None, None]:
    """
    Solution 3: SSE generator yielding formatted messages.
    """
    for i in range(5):
        time.sleep(1)
        yield f"data: Message {i+1}\n\n"


async def solution_4_async_sse_generator() -> AsyncGenerator[str, None]:
    """
    Solution 4: Async SSE generator for real-time data.
    """
    for i in range(5):
        await asyncio.sleep(0.5)
        temperature = 20 + i * 0.5
        data = {"temperature": temperature, "timestamp": time.time()}
        yield f"data: {json.dumps(data)}\n\n"


# ============================================================================
# Solution 5-6: Middleware
# ============================================================================

async def solution_5_request_logging_middleware(request: Request, call_next):
    """
    Solution 5: Logging middleware with timing.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to ms
    response.headers["X-Request-Time"] = str(int(process_time))
    return response


class RequestCounterMiddleware(BaseHTTPMiddleware):
    """
    Solution 6: Middleware that counts requests.
    """

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self.request_count = 0

    async def dispatch(self, request: Request, call_next):
        self.request_count += 1
        response = await call_next(request)
        response.headers["X-Request-Count"] = str(self.request_count)
        return response


# ============================================================================
# Solution 7-8: Authentication and Authorization
# ============================================================================

def solution_7_api_key_dependency(api_key: str = None) -> str:
    """
    Solution 7: API key validation dependency.
    """
    if api_key != "secret-key-123":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


class BearerTokenDependency:
    """
    Solution 8: Bearer token validation dependency.
    """

    def __call__(self, authorization: str = None) -> str:
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing authorization header")

        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = parts[1]
        if token != "valid-token-xyz":
            raise HTTPException(status_code=401, detail="Invalid token")

        return token


# ============================================================================
# Solution 9-10: WebSocket Communication
# ============================================================================

async def solution_9_websocket_echo(websocket: WebSocket) -> None:
    """
    Solution 9: WebSocket echo endpoint.
    """
    await websocket.accept()
    try:
        for _ in range(3):
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    finally:
        await websocket.close()


async def solution_10_websocket_broadcast(websocket: WebSocket, room_id: str) -> None:
    """
    Solution 10: WebSocket with room-based messaging.
    """
    await websocket.accept()
    try:
        message = await websocket.receive_text()
        broadcast_message = f"{room_id}: {message}"
        # In production, would broadcast to all clients in room
        await websocket.send_text(f"Message queued: {broadcast_message}")
    finally:
        await websocket.close()


# ============================================================================
# Solution 11-12: Testing with TestClient
# ============================================================================

def solution_11_test_json_response() -> dict:
    """
    Solution 11: TestClient test for JSON response.
    """
    app = FastAPI()

    @app.get("/data")
    def get_data():
        return {"status": "ok", "data": [1, 2, 3], "timestamp": "2024-01-01"}

    client = TestClient(app)
    response = client.get("/data")

    return {
        "status_code": response.status_code,
        "expected_status": 200,
        "response_keys": list(response.json().keys()),
        "expected_keys": ["status", "data", "timestamp"],
        "passed": response.status_code == 200 and all(
            key in response.json() for key in ["status", "data", "timestamp"]
        ),
    }


def solution_12_test_error_handling() -> dict:
    """
    Solution 12: TestClient test for error handling.
    """
    app = FastAPI()

    @app.post("/validate")
    def validate_data(data: DataModel):
        if data.value < 0:
            raise HTTPException(status_code=400, detail="Value must be positive")
        return {"validated": True, "data": data}

    client = TestClient(app)

    # Test invalid input
    invalid_response = client.post("/validate", json={"name": "test"})
    invalid_passed = invalid_response.status_code == 422

    # Test valid input
    valid_response = client.post("/validate", json={"id": 1, "name": "test", "value": 42.0})
    valid_passed = valid_response.status_code == 200

    return {
        "invalid_input_status": invalid_response.status_code,
        "expected_invalid_status": 422,
        "invalid_test_passed": invalid_passed,
        "valid_input_status": valid_response.status_code,
        "expected_valid_status": 200,
        "valid_test_passed": valid_passed,
        "all_passed": invalid_passed and valid_passed,
    }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("Running solution tests...\n")

    print("Solution 2 - Concurrent Requests:")
    result = asyncio.run(solution_2_concurrent_requests([1, 2, 3]))
    print(f"  {result}\n")

    print("Solution 7 - API Key Validation:")
    try:
        solution_7_api_key_dependency("invalid-key")
    except HTTPException as e:
        print(f"  Caught expected error: {e.detail}\n")

    print("Solution 11 - Test JSON Response:")
    result = solution_11_test_json_response()
    print(f"  Passed: {result['passed']}\n")

    print("Solution 12 - Test Error Handling:")
    result = solution_12_test_error_handling()
    print(f"  Passed: {result['all_passed']}\n")
