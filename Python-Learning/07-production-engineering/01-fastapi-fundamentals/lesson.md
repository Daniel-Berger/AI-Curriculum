# Module 01: FastAPI Fundamentals

## Introduction for Swift Developers

If you've built REST APIs with Vapor (Swift's popular server-side framework), FastAPI will
feel both familiar and surprisingly productive. Both are type-safe, both generate API
documentation, and both leverage modern language features. But FastAPI's Python ecosystem
gives you access to the entire ML/AI stack -- meaning your model serving layer speaks the
same language as your training pipeline.

FastAPI is a modern, high-performance web framework for building APIs with Python 3.7+,
based on standard Python type hints. It's built on Starlette (for the web layer) and
Pydantic (for data validation), giving you automatic request validation, serialization,
and interactive API documentation -- for free.

---

## 1. What is FastAPI?

### Key Features

| Feature | FastAPI | Vapor (Swift) |
|---------|---------|---------------|
| Type checking | Runtime (Pydantic) | Compile-time |
| Auto-docs | Swagger UI + ReDoc | None built-in |
| Async support | Native (asyncio) | Native (SwiftNIO) |
| Performance | On par with Node.js/Go | Comparable |
| Data validation | Pydantic models | Codable + custom |
| Dependency injection | Built-in `Depends()` | Services pattern |

### Why FastAPI for ML/AI?

1. **Same language as your models** -- No context switching between training and serving
2. **Async-first** -- Handle concurrent inference requests efficiently
3. **Pydantic integration** -- Validate complex ML inputs/outputs with type safety
4. **Streaming support** -- Stream LLM token-by-token responses via SSE
5. **Battle-tested** -- Used by Microsoft, Uber, Netflix for ML serving

### Installation

```bash
# Install FastAPI with all dependencies
pip install "fastapi[standard]"

# This installs:
# - fastapi (the framework)
# - uvicorn (ASGI server)
# - pydantic (data validation)
# - starlette (underlying web framework)
# - httpx (async HTTP client for testing)
```

---

## 2. Your First FastAPI Application

### Hello World

```python
# main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint returning a greeting."""
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

Run it:
```bash
# Development server with auto-reload
uvicorn main:app --reload

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.
Visit `http://localhost:8000/redoc` for ReDoc documentation.

### Comparing to Vapor (Swift)

```swift
// Vapor equivalent
import Vapor

func routes(_ app: Application) throws {
    app.get { req in
        return ["message": "Hello, World!"]
    }

    app.get("health") { req in
        return ["status": "healthy"]
    }
}
```

The key difference: FastAPI auto-generates full API documentation from your type hints
and docstrings. Vapor requires additional packages (like vapor-openapi) for this.

---

## 3. Path Operations (HTTP Methods)

FastAPI uses decorators to define HTTP method handlers, similar to Vapor's route
registration but more concise.

### The Four Core Operations

```python
from fastapi import FastAPI

app = FastAPI()

# In-memory database for demonstration
items_db: dict[int, dict] = {}


@app.get("/items")
def list_items():
    """GET -- Retrieve all items."""
    return list(items_db.values())


@app.post("/items", status_code=201)
def create_item(item: dict):
    """POST -- Create a new item."""
    item_id = len(items_db) + 1
    items_db[item_id] = {**item, "id": item_id}
    return items_db[item_id]


@app.put("/items/{item_id}")
def update_item(item_id: int, item: dict):
    """PUT -- Update an existing item."""
    if item_id not in items_db:
        return {"error": "Item not found"}
    items_db[item_id].update(item)
    return items_db[item_id]


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """DELETE -- Remove an item."""
    if item_id not in items_db:
        return {"error": "Item not found"}
    deleted = items_db.pop(item_id)
    return {"deleted": deleted}
```

### Swift/Vapor Comparison

```swift
// Vapor uses similar method-based routing
app.get("items") { req -> [Item] in ... }
app.post("items") { req -> Item in ... }
app.put("items", ":itemId") { req -> Item in ... }
app.delete("items", ":itemId") { req -> HTTPStatus in ... }
```

---

## 4. Path Parameters

Path parameters let you capture values from the URL path.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Path parameter with automatic type conversion.

    FastAPI converts the string from the URL to int automatically.
    If someone sends /users/abc, they get a 422 Validation Error.
    """
    return {"user_id": user_id}


@app.get("/models/{model_name}/versions/{version}")
def get_model_version(model_name: str, version: int):
    """Multiple path parameters."""
    return {
        "model_name": model_name,
        "version": version
    }


# Enum-based path parameters for fixed choices
from enum import Enum

class ModelType(str, Enum):
    GPT = "gpt"
    CLAUDE = "claude"
    LLAMA = "llama"


@app.get("/models/{model_type}/info")
def get_model_info(model_type: ModelType):
    """Path parameter constrained to enum values."""
    return {"model_type": model_type, "value": model_type.value}
```

### Order Matters

```python
# WRONG ORDER -- /users/me will match {user_id} first
@app.get("/users/{user_id}")
def get_user(user_id: int): ...

@app.get("/users/me")          # Never reached!
def get_current_user(): ...

# CORRECT ORDER -- specific routes before parameterized ones
@app.get("/users/me")          # Checked first
def get_current_user(): ...

@app.get("/users/{user_id}")   # Checked second
def get_user(user_id: int): ...
```

---

## 5. Query Parameters

Any function parameter that isn't a path parameter is automatically treated as a
query parameter.

```python
from fastapi import FastAPI, Query

app = FastAPI()

# Mock database
fake_items = [{"name": f"Item {i}", "price": i * 10.0} for i in range(100)]


@app.get("/items")
def list_items(skip: int = 0, limit: int = 10):
    """Basic query parameters with defaults.

    GET /items?skip=0&limit=10
    """
    return fake_items[skip : skip + limit]


@app.get("/search")
def search_items(
    q: str,                              # Required (no default)
    category: str | None = None,         # Optional
    min_price: float = 0.0,              # Default value
    max_price: float = 1000.0,           # Default value
    in_stock: bool = True,               # Boolean query param
):
    """Multiple query parameters with various types.

    GET /search?q=laptop&category=electronics&min_price=500
    """
    results = {"query": q, "filters": {}}
    if category:
        results["filters"]["category"] = category
    results["filters"]["price_range"] = [min_price, max_price]
    results["filters"]["in_stock"] = in_stock
    return results


@app.get("/models")
def list_models(
    q: str = Query(
        default=None,
        min_length=2,
        max_length=50,
        description="Search query for model names",
        examples=["gpt-4", "claude"],
    ),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
):
    """Query parameters with validation using Query()."""
    return {"query": q, "page": page, "size": size}
```

---

## 6. Request Body with Pydantic Models

This is where FastAPI really shines. Pydantic models provide automatic validation,
serialization, and documentation -- similar to Swift's `Codable` but with runtime
validation built in.

### Defining Models

```python
from pydantic import BaseModel, Field
from datetime import datetime


class ChatMessage(BaseModel):
    """A single chat message.

    Swift equivalent:
        struct ChatMessage: Codable {
            let role: String
            let content: String
            let timestamp: Date?
        }
    """
    role: str = Field(
        ...,  # ... means required (no default)
        description="The role of the message sender",
        examples=["user", "assistant", "system"],
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The message content",
    )
    timestamp: datetime | None = Field(
        default=None,
        description="When the message was sent",
    )


class ChatRequest(BaseModel):
    """Request body for chat completions."""
    model: str = Field(default="claude-3-sonnet", description="Model to use")
    messages: list[ChatMessage] = Field(
        ...,
        min_length=1,
        description="List of messages in the conversation",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )
    max_tokens: int = Field(
        default=1024,
        ge=1,
        le=4096,
        description="Maximum tokens to generate",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "model": "claude-3-sonnet",
                    "messages": [
                        {"role": "user", "content": "Hello!"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024,
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Response from chat completions."""
    id: str
    model: str
    content: str
    usage: dict[str, int]
    created_at: datetime
```

### Using Models in Endpoints

```python
from fastapi import FastAPI
import uuid

app = FastAPI()


@app.post("/chat/completions", response_model=ChatResponse)
def create_chat_completion(request: ChatRequest):
    """Create a chat completion.

    FastAPI automatically:
    1. Parses the JSON request body
    2. Validates against ChatRequest schema
    3. Returns 422 if validation fails
    4. Validates the response against ChatResponse
    5. Documents everything in Swagger UI
    """
    # Process the request
    last_message = request.messages[-1].content

    return ChatResponse(
        id=str(uuid.uuid4()),
        model=request.model,
        content=f"Echo: {last_message}",
        usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        created_at=datetime.now(),
    )
```

### Nested Models

```python
class ModelConfig(BaseModel):
    """Model configuration parameters."""
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class RAGRequest(BaseModel):
    """Request for RAG (Retrieval Augmented Generation)."""
    query: str
    config: ModelConfig = ModelConfig()  # Nested model with defaults
    filters: dict[str, str] | None = None
    top_k: int = Field(default=5, ge=1, le=20)
```

---

## 7. Response Models and Status Codes

### Response Models

Response models let you control exactly what gets returned to the client,
filtering out internal fields.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class UserInDB(BaseModel):
    """Internal user model with sensitive fields."""
    id: int
    username: str
    email: str
    hashed_password: str  # Should NEVER be returned!
    is_admin: bool


class UserResponse(BaseModel):
    """Public user model -- safe to return."""
    id: int
    username: str
    email: str


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """response_model=UserResponse filters out hashed_password.

    Even though we return a UserInDB, FastAPI strips fields
    not in UserResponse. Similar to Swift's CodingKeys for
    controlling serialization.
    """
    user = UserInDB(
        id=user_id,
        username="daniel",
        email="daniel@example.com",
        hashed_password="$2b$12$...",
        is_admin=True,
    )
    return user  # hashed_password is automatically excluded
```

### Status Codes

```python
from fastapi import FastAPI, status

app = FastAPI()


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(name: str):
    """Return 201 Created on success."""
    return {"name": name, "id": 1}


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    """Return 204 No Content on successful deletion."""
    pass  # No response body needed
```

---

## 8. Error Handling with HTTPException

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

models_db = {
    "claude-3-sonnet": {"name": "Claude 3 Sonnet", "provider": "Anthropic"},
    "gpt-4": {"name": "GPT-4", "provider": "OpenAI"},
}


@app.get("/models/{model_id}")
def get_model(model_id: str):
    """Raise HTTPException for error responses.

    Similar to Vapor's `throw Abort(.notFound)`.
    """
    if model_id not in models_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found",
            headers={"X-Error-Code": "MODEL_NOT_FOUND"},  # Optional headers
        )
    return models_db[model_id]


# Custom exception handler
from fastapi import Request
from fastapi.responses import JSONResponse


class ModelNotFoundError(Exception):
    """Custom exception for model not found."""
    def __init__(self, model_id: str):
        self.model_id = model_id


@app.exception_handler(ModelNotFoundError)
async def model_not_found_handler(request: Request, exc: ModelNotFoundError):
    """Custom exception handler -- catch domain exceptions and return JSON."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "model_not_found",
            "message": f"Model '{exc.model_id}' does not exist",
            "available_models": list(models_db.keys()),
        },
    )


@app.get("/v2/models/{model_id}")
def get_model_v2(model_id: str):
    """Using custom exception."""
    if model_id not in models_db:
        raise ModelNotFoundError(model_id)
    return models_db[model_id]
```

---

## 9. Dependency Injection with Depends

FastAPI's dependency injection is one of its most powerful features. It's similar
to Vapor's `Services` pattern but more flexible and composable.

### Basic Dependencies

```python
from fastapi import FastAPI, Depends, Header, HTTPException

app = FastAPI()


# Simple dependency -- a function that returns a value
def get_api_key(x_api_key: str = Header(...)):
    """Extract and validate API key from header.

    This function is called before the endpoint handler.
    Similar to Vapor middleware but more granular.
    """
    if x_api_key != "secret-key-123":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@app.get("/protected")
def protected_endpoint(api_key: str = Depends(get_api_key)):
    """This endpoint requires a valid API key.

    Depends(get_api_key) tells FastAPI:
    1. Call get_api_key() before this handler
    2. Pass the result as the api_key parameter
    3. If get_api_key raises, skip this handler
    """
    return {"message": "You have access!", "api_key": api_key}
```

### Composable Dependencies

```python
from dataclasses import dataclass


@dataclass
class PaginationParams:
    """Pagination parameters extracted from query string."""
    skip: int = 0
    limit: int = 20


def get_pagination(skip: int = 0, limit: int = 20) -> PaginationParams:
    """Dependency for pagination parameters."""
    if limit > 100:
        limit = 100  # Cap maximum page size
    return PaginationParams(skip=skip, limit=limit)


class DatabaseSession:
    """Simulated database session."""
    def __init__(self):
        self.connected = True

    def close(self):
        self.connected = False


def get_db():
    """Dependency with cleanup (like a context manager).

    yield-based dependencies allow setup/teardown.
    Similar to Swift's defer { } pattern.
    """
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()  # Always runs, even on error


@app.get("/items")
def list_items(
    pagination: PaginationParams = Depends(get_pagination),
    db: DatabaseSession = Depends(get_db),
):
    """Multiple dependencies composed together."""
    return {
        "items": [],
        "pagination": {"skip": pagination.skip, "limit": pagination.limit},
        "db_connected": db.connected,
    }
```

### Class-Based Dependencies

```python
class ModelService:
    """Dependency as a class -- useful for services with state."""

    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        self.loaded = True

    def predict(self, text: str) -> str:
        return f"[{self.model_name}] Prediction for: {text}"


def get_model_service() -> ModelService:
    """Factory function for model service."""
    return ModelService(model_name="claude-3-sonnet")


@app.post("/predict")
def predict(
    text: str,
    model_service: ModelService = Depends(get_model_service),
):
    """Use injected model service."""
    return {"prediction": model_service.predict(text)}
```

---

## 10. Middleware

Middleware runs code before and/or after every request, similar to Vapor's
`Middleware` protocol.

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()


# CORS Middleware -- essential for web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    """Add X-Process-Time header to every response.

    Similar to Vapor's:
        struct TimingMiddleware: Middleware {
            func respond(to request: Request, chainingTo next: Responder) -> EventLoopFuture<Response>
        }
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every incoming request."""
    print(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"Response: {response.status_code}")
    return response
```

---

## 11. CORS (Cross-Origin Resource Sharing)

When your FastAPI backend serves an iOS app or web frontend, you need CORS.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Development: allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allow all origins (dev only!)
    allow_credentials=True,
    allow_methods=["*"],           # Allow all HTTP methods
    allow_headers=["*"],           # Allow all headers
)

# Production: restrict to known origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://admin.myapp.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Request-Id"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

For an iOS app using `URLSession`, CORS doesn't apply (it's a browser-only concept).
But if your API also serves a web frontend, CORS is essential.

---

## 12. Static Files

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve files from a directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Now files in ./static/ are accessible at /static/filename.ext
# Example: ./static/logo.png -> http://localhost:8000/static/logo.png
```

---

## 13. Swagger UI and ReDoc

FastAPI generates interactive API documentation automatically from your type hints,
docstrings, and Pydantic models. No additional configuration needed.

```python
from fastapi import FastAPI

app = FastAPI(
    title="ML Model Serving API",
    description="""
    An API for serving machine learning models.

    ## Features
    - Chat completions
    - Embedding generation
    - RAG (Retrieval Augmented Generation)
    """,
    version="1.0.0",
    docs_url="/docs",          # Swagger UI (default: /docs)
    redoc_url="/redoc",        # ReDoc (default: /redoc)
    openapi_url="/openapi.json",  # OpenAPI schema
)


# Tag-based organization
@app.get("/models", tags=["Models"])
def list_models():
    """List all available models.

    Returns a list of model IDs with their metadata.
    """
    return []


@app.post("/chat", tags=["Chat"])
def create_chat():
    """Create a chat completion.

    Send messages and receive AI-generated responses.
    """
    return {}


@app.post("/embeddings", tags=["Embeddings"])
def create_embedding():
    """Generate text embeddings.

    Convert text into vector representations for semantic search.
    """
    return {}
```

When you visit `/docs`, you get a fully interactive Swagger UI where you can:
- See all endpoints organized by tags
- Read descriptions and see parameter types
- Try out endpoints directly from the browser
- See request/response schemas

This is a massive advantage over Vapor, which requires additional setup for OpenAPI.

---

## 14. Putting It All Together: A Mini ML API

Here's a complete example combining everything we've learned:

```python
"""A complete mini ML API demonstrating all FastAPI fundamentals."""
from datetime import datetime
from enum import Enum
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, Header, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# --- App Setup ---
app = FastAPI(
    title="Mini ML API",
    description="A demonstration API for serving ML models",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---
class ModelName(str, Enum):
    SMALL = "model-small"
    LARGE = "model-large"


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    model: ModelName = ModelName.SMALL
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class PredictResponse(BaseModel):
    id: str
    text: str
    model: str
    confidence: float
    created_at: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: str


# --- Dependencies ---
def verify_api_key(x_api_key: str = Header(...)):
    """Validate API key from request header."""
    valid_keys = {"key-1", "key-2", "key-3"}
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return x_api_key


# --- Endpoints ---
@app.get("/", tags=["Health"])
def root():
    """Root endpoint."""
    return {"service": "Mini ML API", "status": "running"}


@app.get("/health", tags=["Health"])
def health():
    """Health check."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    tags=["Predictions"],
    responses={401: {"model": ErrorResponse}},
)
def create_prediction(
    request: PredictRequest,
    api_key: str = Depends(verify_api_key),
):
    """Create a prediction using the specified model.

    Requires a valid API key in the X-Api-Key header.
    """
    return PredictResponse(
        id=str(uuid4()),
        text=f"Prediction for: {request.text[:50]}...",
        model=request.model.value,
        confidence=0.95,
        created_at=datetime.now(),
    )


@app.get("/models", tags=["Models"])
def list_models(
    api_key: str = Depends(verify_api_key),
):
    """List available models."""
    return [
        {"id": m.value, "name": m.name}
        for m in ModelName
    ]


@app.get("/predictions", tags=["Predictions"])
def list_predictions(
    api_key: str = Depends(verify_api_key),
    model: ModelName | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    """List previous predictions with filtering and pagination."""
    return {
        "predictions": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
        "model_filter": model,
    }
```

---

## 15. Key Differences: FastAPI vs Vapor (Swift)

| Concept | FastAPI (Python) | Vapor (Swift) |
|---------|-----------------|---------------|
| Route definition | `@app.get("/path")` | `app.get("path") { req in }` |
| Request body | Pydantic `BaseModel` | `Content` protocol / `Codable` |
| Validation | Pydantic `Field(ge=0)` | Custom validators |
| Dependency injection | `Depends(function)` | `req.application.services` |
| Middleware | `@app.middleware("http")` | `struct M: Middleware` |
| Async | `async def` / `def` | `EventLoopFuture` / `async` |
| Error handling | `raise HTTPException` | `throw Abort(.status)` |
| Auto documentation | Built-in (Swagger/ReDoc) | Requires packages |
| Type safety | Runtime (Pydantic) | Compile-time (Swift) |
| Testing | `TestClient` | `XCTVapor` |

---

## Summary

FastAPI gives you a production-ready API framework with:
- **Type validation** through Pydantic (runtime, but thorough)
- **Auto-documentation** via Swagger UI and ReDoc
- **Dependency injection** for clean, testable code
- **Async support** for high-concurrency ML serving
- **Middleware** for cross-cutting concerns (auth, logging, CORS)

For ML/AI work, FastAPI is the de facto standard because it speaks the same language
as your models (Python) and handles the complex request/response patterns that ML
serving demands (streaming, large payloads, async inference).

In the next module, we'll explore advanced FastAPI features: async patterns, streaming
responses for LLMs, WebSockets, authentication, and testing.
