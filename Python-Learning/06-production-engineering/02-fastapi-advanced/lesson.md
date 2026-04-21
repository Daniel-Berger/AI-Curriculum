# Module 02: FastAPI Advanced

## Introduction for Swift Developers

In Module 01, we covered FastAPI basics -- routes, Pydantic models, dependency injection.
Now we dive into the advanced features that make FastAPI the go-to framework for ML/AI
serving: async endpoints, streaming responses (essential for LLMs), WebSockets, authentication,
testing, and application organization.

If you've worked with SwiftNIO's `EventLoopFuture` or Swift's modern `async/await`, the
async patterns here will feel familiar. The streaming patterns are what you'd use to build
real-time token-by-token LLM responses -- the same experience users get with ChatGPT or
Claude's web interface.

---

## 1. Async Endpoints: `async def` vs `def`

### The Two Modes

FastAPI supports both synchronous and asynchronous endpoints:

```python
from fastapi import FastAPI
import asyncio
import httpx

app = FastAPI()


# Synchronous endpoint -- runs in a thread pool
@app.get("/sync")
def sync_endpoint():
    """This runs in a separate thread from the event loop.

    Use 'def' when:
    - Calling blocking I/O (database drivers without async support)
    - CPU-bound work (model inference with synchronous libraries)
    - Simple endpoints that don't need concurrency
    """
    import time
    time.sleep(1)  # Blocks the thread, NOT the event loop
    return {"mode": "sync"}


# Asynchronous endpoint -- runs on the event loop
@app.get("/async")
async def async_endpoint():
    """This runs on the main event loop.

    Use 'async def' when:
    - Making HTTP calls (httpx, aiohttp)
    - Using async database drivers (asyncpg, motor)
    - Calling other async functions
    - You need high concurrency
    """
    await asyncio.sleep(1)  # Non-blocking sleep
    return {"mode": "async"}
```

### When to Use Which

```python
# GOOD: async with async I/O
@app.get("/models")
async def list_models():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/models")
        return response.json()


# BAD: async with blocking I/O -- blocks the entire event loop!
@app.get("/models-bad")
async def list_models_bad():
    import requests  # Blocking library!
    response = requests.get("https://api.example.com/models")  # Blocks event loop!
    return response.json()


# GOOD: def with blocking I/O -- FastAPI runs it in a thread pool
@app.get("/models-sync")
def list_models_sync():
    import requests
    response = requests.get("https://api.example.com/models")
    return response.json()  # Runs in thread pool, doesn't block event loop
```

### Swift Comparison

```swift
// Swift async/await (very similar to Python)
func listModels() async throws -> [Model] {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode([Model].self, from: data)
}

// Python equivalent:
// async def list_models():
//     async with httpx.AsyncClient() as client:
//         response = await client.get(url)
//         return response.json()
```

---

## 2. Background Tasks

Background tasks run after the response is sent -- perfect for logging, sending emails,
or updating caches without making the user wait.

```python
from fastapi import FastAPI, BackgroundTasks
import logging

app = FastAPI()
logger = logging.getLogger(__name__)


def log_prediction(model: str, input_text: str, output: str):
    """Background task to log predictions (runs after response is sent)."""
    logger.info(f"Prediction: model={model}, input={input_text[:50]}, output={output[:50]}")
    # In production: save to database, send to analytics, etc.


def update_usage_stats(user_id: str, tokens_used: int):
    """Background task to update usage statistics."""
    logger.info(f"Usage: user={user_id}, tokens={tokens_used}")


@app.post("/predict")
async def predict(
    text: str,
    background_tasks: BackgroundTasks,
):
    """Run prediction and log it in the background.

    The response is sent immediately. Background tasks run after.
    Similar to Swift's Task { } for fire-and-forget work.
    """
    result = f"Prediction for: {text}"

    # Queue background tasks (run after response is sent)
    background_tasks.add_task(log_prediction, "model-v1", text, result)
    background_tasks.add_task(update_usage_stats, "user-123", 100)

    return {"result": result}
```

---

## 3. Streaming Responses

Streaming is essential for LLM applications -- it lets users see tokens as they're
generated, rather than waiting for the full response.

### Basic StreamingResponse

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()


async def generate_numbers():
    """Async generator that yields numbers one at a time."""
    for i in range(10):
        yield f"Number: {i}\n"
        await asyncio.sleep(0.5)  # Simulate slow generation


@app.get("/stream")
async def stream_numbers():
    """Stream numbers to the client.

    The client receives data as it's generated, not all at once.
    """
    return StreamingResponse(
        generate_numbers(),
        media_type="text/plain",
    )
```

### Server-Sent Events (SSE) for LLM Streaming

SSE is the standard protocol for streaming LLM responses (used by OpenAI, Anthropic, etc.).

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()


async def generate_chat_stream(prompt: str):
    """Simulate streaming LLM response token by token.

    SSE format: each event is:
        data: {json}\n\n

    The double newline separates events.
    """
    tokens = ["Hello", "!", " I'm", " an", " AI", " assistant", ".",
              " How", " can", " I", " help", " you", " today", "?"]

    for i, token in enumerate(tokens):
        event_data = {
            "id": f"msg-{i}",
            "type": "content_block_delta",
            "delta": {"text": token},
        }
        yield f"data: {json.dumps(event_data)}\n\n"
        await asyncio.sleep(0.1)  # Simulate generation time

    # Send final event
    yield f"data: {json.dumps({'type': 'message_stop'})}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/chat/stream")
async def stream_chat(prompt: str = "Hello"):
    """Stream a chat response using SSE.

    This is how ChatGPT and Claude stream their responses.
    The frontend uses EventSource or fetch() to consume the stream.
    """
    return StreamingResponse(
        generate_chat_stream(prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

### Using sse-starlette (Cleaner SSE)

```python
# pip install sse-starlette
from sse_starlette.sse import EventSourceResponse

@app.post("/chat/stream/v2")
async def stream_chat_v2(prompt: str = "Hello"):
    """Cleaner SSE using sse-starlette library."""

    async def event_generator():
        tokens = ["Hello", " world", "!"]
        for token in tokens:
            yield {
                "event": "token",
                "data": json.dumps({"text": token}),
            }
            await asyncio.sleep(0.1)
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
```

### iOS Client for SSE

For context, here's how you'd consume this from Swift:

```swift
// Swift URLSession for SSE consumption
func streamChat(prompt: String) async throws {
    let url = URL(string: "http://localhost:8000/chat/stream")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"

    let (bytes, _) = try await URLSession.shared.bytes(for: request)

    for try await line in bytes.lines {
        if line.hasPrefix("data: ") {
            let data = String(line.dropFirst(6))
            if data == "[DONE]" { break }
            // Parse JSON and update UI
            print(data)
        }
    }
}
```

---

## 4. WebSocket Support

WebSockets provide full-duplex communication -- both sides can send messages at any time.
Useful for real-time chat interfaces.

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Any

app = FastAPI()


class ConnectionManager:
    """Manage active WebSocket connections.

    Similar to managing multiple URLSessionWebSocketTask instances in iOS,
    but on the server side.
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat.

    The client connects once and can send/receive messages continuously.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            # Process and respond
            response = f"Echo: {data}"
            await manager.send_personal(response, websocket)

            # Optionally broadcast to all connected clients
            # await manager.broadcast(f"User said: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/chat/{room_id}")
async def websocket_chat_room(websocket: WebSocket, room_id: str):
    """WebSocket with path parameters -- chat rooms."""
    await manager.connect(websocket)
    try:
        await manager.broadcast(f"User joined room {room_id}")
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"[Room {room_id}] {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"User left room {room_id}")
```

---

## 5. Custom Middleware

### Timing Middleware

```python
from fastapi import FastAPI, Request
import time
import logging

app = FastAPI()
logger = logging.getLogger(__name__)


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """Measure and log request processing time."""
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    response.headers["X-Process-Time"] = f"{duration:.4f}"
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {duration:.4f}s "
        f"status={response.status_code}"
    )
    return response
```

### Request ID Middleware

```python
import uuid


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add a unique request ID to every request/response.

    Essential for tracing requests through distributed systems.
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response
```

### Logging Middleware with Starlette BaseHTTPMiddleware

```python
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Class-based middleware for more complex logic.

    Similar to Vapor's Middleware protocol:
        struct LoggingMiddleware: Middleware {
            func respond(to request: Request, chainingTo next: Responder)
                -> EventLoopFuture<Response>
        }
    """

    async def dispatch(self, request: Request, call_next):
        # Before request
        logger.info(f"Incoming: {request.method} {request.url.path}")
        body = await request.body()
        if body:
            logger.debug(f"Body size: {len(body)} bytes")

        # Process request
        response = await call_next(request)

        # After request
        logger.info(f"Outgoing: {response.status_code}")
        return response


# Add class-based middleware
app.add_middleware(LoggingMiddleware)
```

---

## 6. Authentication

### API Key Authentication

```python
from fastapi import FastAPI, Depends, HTTPException, Header, Security
from fastapi.security import APIKeyHeader

app = FastAPI()

# Define the API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key")


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Validate API key -- shown in Swagger UI as a security scheme."""
    valid_keys = {"sk-prod-key-1", "sk-prod-key-2"}
    if api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


@app.get("/protected", dependencies=[Depends(verify_api_key)])
async def protected_route():
    """This endpoint requires an API key.

    The Swagger UI will show a lock icon and let you enter the key.
    """
    return {"message": "Authenticated!"}
```

### OAuth2 with JWT Tokens

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt  # pip install PyJWT

app = FastAPI()

SECRET_KEY = "your-secret-key"  # In production, use environment variable!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str
    is_active: bool = True


# Fake user database
fake_users = {
    "daniel": {
        "username": "daniel",
        "email": "daniel@example.com",
        "hashed_password": "fakehashed_password123",
        "is_active": True,
    }
}


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Decode JWT token and return the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user_data = fake_users.get(username)
    if user_data is None:
        raise credentials_exception

    return User(**user_data)


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 login endpoint -- returns JWT token."""
    user = fake_users.get(form_data.username)
    if not user or f"fakehashed_{form_data.password}" != user["hashed_password"]:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user -- requires valid JWT token."""
    return current_user
```

---

## 7. Rate Limiting

```python
from fastapi import FastAPI, Request, HTTPException
from collections import defaultdict
import time

app = FastAPI()

# Simple in-memory rate limiter
request_counts: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 60  # requests
RATE_WINDOW = 60  # seconds


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limit by client IP address."""
    client_ip = request.client.host
    now = time.time()

    # Clean old entries
    request_counts[client_ip] = [
        ts for ts in request_counts[client_ip]
        if now - ts < RATE_WINDOW
    ]

    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(RATE_WINDOW)},
        )

    request_counts[client_ip].append(now)
    response = await call_next(request)

    # Add rate limit headers
    remaining = RATE_LIMIT - len(request_counts[client_ip])
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response
```

---

## 8. File Upload and Download

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
from pathlib import Path

app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file.

    UploadFile provides:
    - filename: original filename
    - content_type: MIME type
    - file: SpooledTemporaryFile (file-like object)
    """
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file_path.stat().st_size,
    }


@app.post("/upload/multiple")
async def upload_multiple(files: list[UploadFile] = File(...)):
    """Upload multiple files at once."""
    results = []
    for file in files:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        results.append({"filename": file.filename, "size": file_path.stat().st_size})
    return results


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a file."""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)
```

---

## 9. Testing FastAPI Applications

### Using TestClient (Synchronous)

```python
# test_app.py
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

# App to test
app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


items_db: dict[int, Item] = {}


@app.post("/items", status_code=201)
def create_item(item: Item):
    item_id = len(items_db) + 1
    items_db[item_id] = item
    return {"id": item_id, **item.model_dump()}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404)
    return items_db[item_id]


# Tests
client = TestClient(app)


def test_create_item():
    """Test creating an item."""
    response = client.post("/items", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Widget"
    assert data["price"] == 9.99
    assert "id" in data


def test_get_item_not_found():
    """Test 404 for missing item."""
    response = client.get("/items/9999")
    assert response.status_code == 404


def test_create_item_invalid():
    """Test validation error for invalid data."""
    response = client.post("/items", json={"name": "Widget"})  # Missing price
    assert response.status_code == 422  # Validation error
```

### Async Testing with httpx

```python
# test_async.py
import pytest
import httpx
from fastapi import FastAPI

app = FastAPI()


@app.get("/async-endpoint")
async def async_endpoint():
    return {"status": "ok"}


@pytest.mark.anyio
async def test_async_endpoint():
    """Test async endpoint using httpx.AsyncClient."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/async-endpoint")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
```

### Testing with Dependency Overrides

```python
from fastapi import FastAPI, Depends

app = FastAPI()


def get_db():
    """Production database dependency."""
    return {"type": "production_db"}


@app.get("/data")
def get_data(db=Depends(get_db)):
    return {"db_type": db["type"]}


# In tests, override the dependency
def get_test_db():
    """Test database dependency."""
    return {"type": "test_db"}


def test_with_dependency_override():
    """Override dependencies for testing.

    Similar to Swift dependency injection with test doubles.
    """
    app.dependency_overrides[get_db] = get_test_db

    client = TestClient(app)
    response = client.get("/data")
    assert response.json()["db_type"] == "test_db"

    # Clean up
    app.dependency_overrides.clear()
```

---

## 10. Lifespan Events (Startup/Shutdown)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI


# Modern approach (FastAPI 0.93+): lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Setup and teardown for the application.

    Everything before 'yield' runs on startup.
    Everything after 'yield' runs on shutdown.

    Similar to Swift's application(_:didFinishLaunchingWithOptions:)
    and applicationWillTerminate(_:).
    """
    # Startup
    print("Loading ML model...")
    app.state.model = {"name": "loaded_model", "ready": True}
    print("Model loaded!")

    yield  # Application runs here

    # Shutdown
    print("Cleaning up...")
    app.state.model = None
    print("Cleanup complete!")


app = FastAPI(lifespan=lifespan)


@app.get("/model/status")
async def model_status():
    """Check if the model is loaded."""
    model = app.state.model
    return {"model": model["name"], "ready": model["ready"]}
```

---

## 11. Router Organization

For larger applications, organize endpoints into separate routers (like Vapor's
RouteCollection).

```python
# routers/chat.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def list_chats():
    return []


@router.post("/completions")
async def create_completion():
    return {"response": "Hello!"}


# routers/models.py
from fastapi import APIRouter

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("/")
async def list_models():
    return [{"id": "model-1", "name": "GPT-4"}]


@router.get("/{model_id}")
async def get_model(model_id: str):
    return {"id": model_id}


# main.py
from fastapi import FastAPI
# from routers import chat, models  # In real app

app = FastAPI(title="ML Platform API")

# Include routers
# app.include_router(chat.router)
# app.include_router(models.router)

# With prefix override:
# app.include_router(chat.router, prefix="/v2/chat")
```

---

## 12. Settings Management with pydantic-settings

```python
# settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    pydantic-settings automatically reads from:
    1. Environment variables
    2. .env file
    3. Default values

    Similar to Swift's Info.plist or ProcessInfo.processInfo.environment.
    """
    app_name: str = "ML API"
    debug: bool = False
    api_key: str = ""
    database_url: str = "sqlite:///./app.db"
    model_path: str = "./models/default"
    max_tokens: int = 4096
    rate_limit: int = 100

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings -- loaded once, reused everywhere.

    @lru_cache ensures Settings() is only called once.
    Similar to a Swift singleton pattern.
    """
    return Settings()


# Usage in FastAPI
from fastapi import FastAPI, Depends

app = FastAPI()


@app.get("/settings")
async def show_settings(settings: Settings = Depends(get_settings)):
    """Settings injected via Depends -- testable and configurable."""
    return {
        "app_name": settings.app_name,
        "debug": settings.debug,
        "max_tokens": settings.max_tokens,
    }
```

---

## 13. Putting It All Together: Structured LLM API

```python
"""A structured LLM API combining all advanced features."""
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import uuid4
import asyncio
import json
import time

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field


# --- Settings ---
class AppConfig:
    MODEL_NAME = "demo-model-v1"
    MAX_TOKENS = 2048
    VALID_API_KEYS = {"sk-key-1", "sk-key-2"}


# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model_loaded = True
    app.state.request_count = 0
    yield
    app.state.model_loaded = False


# --- App ---
app = FastAPI(
    title="LLM Serving API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Middleware ---
@app.middleware("http")
async def count_requests(request: Request, call_next):
    app.state.request_count += 1
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}"
    response.headers["X-Request-Count"] = str(app.state.request_count)
    return response


# --- Auth ---
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_key(api_key: str = Depends(api_key_header)):
    if api_key not in AppConfig.VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


# --- Models ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    stream: bool = False
    max_tokens: int = Field(default=1024, le=AppConfig.MAX_TOKENS)

class ChatResponse(BaseModel):
    id: str
    content: str
    model: str
    tokens_used: int
    created_at: datetime


# --- Streaming ---
async def generate_stream(messages: list[ChatMessage]):
    """Generate SSE stream simulating LLM output."""
    tokens = ["I", " understand", " your", " question", ".",
              " Let", " me", " help", " you", " with", " that", "."]
    for token in tokens:
        data = json.dumps({"delta": {"text": token}})
        yield f"data: {data}\n\n"
        await asyncio.sleep(0.05)
    yield "data: [DONE]\n\n"


# --- Endpoints ---
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": app.state.model_loaded,
        "requests_served": app.state.request_count,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_key),
):
    """Non-streaming chat completion."""
    if request.stream:
        return StreamingResponse(
            generate_stream(request.messages),
            media_type="text/event-stream",
        )

    return ChatResponse(
        id=str(uuid4()),
        content="This is a demo response.",
        model=AppConfig.MODEL_NAME,
        tokens_used=42,
        created_at=datetime.now(),
    )
```

---

## Summary

Advanced FastAPI features for ML/AI serving:

| Feature | Use Case | Swift Equivalent |
|---------|----------|-----------------|
| `async def` | Non-blocking I/O | `async` functions |
| Background tasks | Post-response work | `Task { }` |
| StreamingResponse | LLM token streaming | `URLSession.bytes` |
| SSE | Real-time updates | EventSource |
| WebSockets | Bidirectional chat | `URLSessionWebSocketTask` |
| Custom middleware | Cross-cutting concerns | `Middleware` protocol |
| JWT auth | User authentication | `Codable` + `CryptoKit` |
| TestClient | Endpoint testing | `XCTVapor` |
| Lifespan | Startup/shutdown | `AppDelegate` lifecycle |
| APIRouter | Code organization | `RouteCollection` |
| pydantic-settings | Configuration | `Info.plist` / env vars |

These features are the building blocks for production ML APIs. In the next modules,
we'll containerize these applications with Docker and set up CI/CD pipelines.
