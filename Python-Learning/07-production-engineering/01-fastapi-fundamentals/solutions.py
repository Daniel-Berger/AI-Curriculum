"""
Module 01: FastAPI Fundamentals - Solutions
=============================================
Complete solutions for all exercises with explanations.

Run this file to verify all solutions pass: `python solutions.py`
"""

from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from enum import Enum
from typing import Any
import time


# =============================================================================
# SECTION 1: Pydantic Models (Request/Response Bodies)
# =============================================================================

# Exercise 1: Basic Pydantic Model
class Book(BaseModel):
    """A book model with validation."""
    title: str = Field(..., min_length=1)
    author: str
    year: int = Field(..., ge=1000, le=2030)
    isbn: str | None = None
    # Note: Field(...) means required. The ... is Python's Ellipsis object,
    # used by Pydantic to indicate "no default value."
    # This is similar to Swift where non-optional properties must be initialized.


# Exercise 2: Nested Pydantic Models
class Message(BaseModel):
    """A chat message."""
    role: str  # In production, you'd use Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1)


class CompletionRequest(BaseModel):
    """A chat completion request."""
    messages: list[Message] = Field(..., min_length=1)
    model: str = "claude-3-sonnet"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    stream: bool = False
    # Note: Pydantic automatically validates nested models.
    # When JSON is posted, Message objects are created from dicts automatically.
    # Similar to Swift's nested Codable structs being decoded from JSON.


# Exercise 3: Response Model with Computed Fields
class CompletionResponse(BaseModel):
    """A chat completion response."""
    id: str
    model: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def total_tokens(self) -> int:
        """Computed property for total token count."""
        return self.prompt_tokens + self.completion_tokens
        # Note: @property in Python is like computed properties in Swift:
        #   var totalTokens: Int { promptTokens + completionTokens }

    def estimated_cost(self, cost_per_token: float = 0.00001) -> float:
        """Calculate estimated cost based on total tokens."""
        return self.total_tokens * cost_per_token

    # Alternative using Pydantic's computed_field (shown but not required):
    # @computed_field
    # @property
    # def total_tokens_v2(self) -> int:
    #     return self.prompt_tokens + self.completion_tokens
    # This would include total_tokens_v2 in serialization (model_dump/JSON).


# =============================================================================
# SECTION 2: Endpoint Logic Functions
# =============================================================================

# Exercise 4: Pagination Helper
def paginate(
    items: list[Any],
    skip: int = 0,
    limit: int = 10,
) -> dict[str, Any]:
    """Return a paginated response dict."""
    # Cap limit at 100 (prevent abuse)
    limit = min(limit, 100)

    # Slice the items
    paginated_items = items[skip : skip + limit]

    # Check if there are more items beyond this page
    has_more = (skip + limit) < len(items)

    return {
        "items": paginated_items,
        "total": len(items),
        "skip": skip,
        "limit": limit,
        "has_more": has_more,
    }
    # Note: Python's list slicing handles out-of-bounds gracefully.
    # items[100:200] on a 50-item list returns [] -- no crash.
    # Swift's Array subscript would crash on out-of-bounds access.


# Exercise 5: Search Filter
def filter_items(
    items: list[dict[str, Any]],
    query: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
) -> list[dict[str, Any]]:
    """Filter a list of item dicts based on various criteria."""
    results = items

    if query is not None:
        results = [
            item for item in results
            if query.lower() in item["name"].lower()
        ]

    if category is not None:
        results = [
            item for item in results
            if item["category"] == category
        ]

    if min_price is not None:
        results = [
            item for item in results
            if item["price"] >= min_price
        ]

    if max_price is not None:
        results = [
            item for item in results
            if item["price"] <= max_price
        ]

    return results
    # Note: Each filter step creates a new list via list comprehension.
    # For large datasets, you'd use a database query instead.
    # In Swift, you'd chain .filter() calls on an Array, which is similar.

    # Alternative: single-pass filtering
    # def matches(item):
    #     if query and query.lower() not in item["name"].lower():
    #         return False
    #     if category and item["category"] != category:
    #         return False
    #     if min_price is not None and item["price"] < min_price:
    #         return False
    #     if max_price is not None and item["price"] > max_price:
    #         return False
    #     return True
    # return [item for item in items if matches(item)]


# Exercise 6: API Key Validator
def validate_api_key(api_key: str) -> dict[str, Any]:
    """Validate an API key and return the associated user info."""
    valid_keys = {
        "sk-test-key-1": {"user_id": 1, "name": "Alice", "tier": "free"},
        "sk-test-key-2": {"user_id": 2, "name": "Bob", "tier": "pro"},
        "sk-test-key-3": {"user_id": 3, "name": "Charlie", "tier": "enterprise"},
    }

    if api_key not in valid_keys:
        raise ValueError("Invalid API key")

    return valid_keys[api_key]
    # Note: In a real FastAPI app, you'd use this as a dependency:
    # def get_current_user(x_api_key: str = Header(...)):
    #     try:
    #         return validate_api_key(x_api_key)
    #     except ValueError:
    #         raise HTTPException(status_code=401, detail="Invalid API key")


# Exercise 7: Rate Limiter
class RateLimiter:
    """A simple in-memory rate limiter."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}
        # Each key maps to a list of timestamps when requests were made.
        # This is a "sliding window" approach.

    def _cleanup(self, key: str) -> None:
        """Remove expired timestamps for a key."""
        if key not in self._requests:
            return
        now = time.time()
        cutoff = now - self.window_seconds
        self._requests[key] = [
            ts for ts in self._requests[key]
            if ts > cutoff
        ]

    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed for the given key."""
        self._cleanup(key)

        if key not in self._requests:
            self._requests[key] = []

        if len(self._requests[key]) < self.max_requests:
            self._requests[key].append(time.time())
            return True

        return False
        # Note: This in-memory approach works for single-process servers.
        # For multi-process (uvicorn --workers 4), you'd use Redis instead.
        # Similar to iOS rate limiting for network requests, but server-side.

    def get_remaining(self, key: str) -> int:
        """Return the number of remaining requests for a key."""
        self._cleanup(key)
        current = len(self._requests.get(key, []))
        return max(0, self.max_requests - current)


# =============================================================================
# SECTION 3: Dependency Injection Patterns
# =============================================================================

# Exercise 8: Service Layer Pattern
class ModelRegistry:
    """Registry of available ML models."""

    def __init__(self):
        self._models: dict[str, dict[str, Any]] = {}

    def register(self, model_id: str, name: str, version: str, model_type: str) -> None:
        """Register a new model."""
        self._models[model_id] = {
            "name": name,
            "version": version,
            "type": model_type,
            "registered_at": datetime.now(),
        }
        # Note: In a real system, this would persist to a database.
        # The registry pattern is common in dependency injection --
        # similar to Swift's service locator or DI container patterns.

    def get(self, model_id: str) -> dict[str, Any]:
        """Get model info by ID."""
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' not found")
        return self._models[model_id]

    def list_models(self, model_type: str | None = None) -> list[dict[str, Any]]:
        """List all models, optionally filtered by type."""
        result = []
        for model_id, info in self._models.items():
            if model_type is None or info["type"] == model_type:
                result.append({"id": model_id, **info})
        return result
        # Note: The {**info} syntax unpacks the dict, similar to
        # Swift's merging dictionaries. "id" is prepended to each entry.


# Exercise 9: Error Response Builder
def build_error_response(
    status_code: int,
    error_type: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a standardized error response dict."""
    response: dict[str, Any] = {
        "error": {
            "type": error_type,
            "message": message,
        },
        "status_code": status_code,
    }

    if details is not None:
        response["details"] = details

    return response
    # Note: Standardized error responses make API consumers' lives easier.
    # In FastAPI, you'd typically raise HTTPException with this structure
    # or use a custom exception handler.


# Exercise 10: Request Validator
def validate_chat_request(request_data: dict[str, Any]) -> list[str]:
    """Validate a chat request dict and return a list of error messages."""
    errors: list[str] = []

    # Check messages exist
    if "messages" not in request_data:
        errors.append("messages is required")
        return errors  # Can't validate further without messages

    messages = request_data["messages"]
    if not isinstance(messages, list) or len(messages) == 0:
        errors.append("messages must be a non-empty list")
        return errors

    # Validate each message
    valid_roles = {"user", "assistant", "system"}
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            errors.append(f"messages[{i}] must be a dict")
            continue
        if "role" not in msg:
            errors.append(f"messages[{i}] missing 'role'")
        elif msg["role"] not in valid_roles:
            errors.append(f"messages[{i}] role must be one of {valid_roles}")
        if "content" not in msg:
            errors.append(f"messages[{i}] missing 'content'")
        elif not isinstance(msg["content"], str) or len(msg["content"]) == 0:
            errors.append(f"messages[{i}] content must be a non-empty string")

    # Validate temperature
    if "temperature" in request_data:
        temp = request_data["temperature"]
        if not isinstance(temp, (int, float)) or temp < 0.0 or temp > 2.0:
            errors.append("temperature must be between 0.0 and 2.0")

    # Validate max_tokens
    if "max_tokens" in request_data:
        mt = request_data["max_tokens"]
        if not isinstance(mt, int) or mt < 1 or mt > 4096:
            errors.append("max_tokens must be an integer between 1 and 4096")

    return errors
    # Note: In real FastAPI code, Pydantic handles this validation automatically.
    # This exercise helps you understand what's happening under the hood.


# =============================================================================
# SECTION 4: Full Endpoint Simulation
# =============================================================================

# Exercise 11: CRUD Operations
class CRUDStore:
    """In-memory CRUD store for any entity type."""

    def __init__(self):
        self._data: dict[int, dict[str, Any]] = {}
        self._next_id: int = 1

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new entity."""
        entity = {
            **data,
            "id": self._next_id,
            "created_at": datetime.now(),
        }
        self._data[self._next_id] = entity
        self._next_id += 1
        return entity
        # Note: ** unpacks the data dict, then we add id and created_at.
        # Similar to Swift's struct init with computed properties.

    def read(self, entity_id: int) -> dict[str, Any]:
        """Read an entity by ID."""
        if entity_id not in self._data:
            raise KeyError(f"Entity {entity_id} not found")
        return self._data[entity_id]

    def update(self, entity_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Update an entity."""
        if entity_id not in self._data:
            raise KeyError(f"Entity {entity_id} not found")

        # Preserve id and created_at, update everything else
        entity = self._data[entity_id]
        for key, value in data.items():
            if key not in ("id", "created_at"):
                entity[key] = value
        entity["updated_at"] = datetime.now()

        return entity

    def delete(self, entity_id: int) -> dict[str, Any]:
        """Delete an entity."""
        if entity_id not in self._data:
            raise KeyError(f"Entity {entity_id} not found")
        return self._data.pop(entity_id)
        # dict.pop() removes and returns the value -- one-liner!
        # In Swift: let removed = dict.removeValue(forKey: key)

    def list_all(self, skip: int = 0, limit: int = 10) -> list[dict[str, Any]]:
        """List entities with pagination."""
        all_items = list(self._data.values())
        return all_items[skip : skip + limit]
        # Note: dict.values() returns a view, so we convert to list first
        # for slicing. In Python 3, dict preserves insertion order.


# Exercise 12: Full API Simulation
def simulate_api_request(
    method: str,
    path: str,
    headers: dict[str, str],
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Simulate processing an API request through the full pipeline."""

    # Step 1: Check for API key header
    if "X-API-Key" not in headers:
        return {"status": 401, "error": "Missing API key"}

    # Step 2: Validate API key
    try:
        user_info = validate_api_key(headers["X-API-Key"])
    except ValueError:
        return {"status": 401, "error": "Invalid API key"}

    # Step 3: Route the request
    if path == "/health":
        if method == "GET":
            return {"status": 200, "body": {"status": "healthy"}}
        else:
            return {"status": 405, "error": "Method not allowed"}

    elif path == "/chat":
        if method == "POST":
            # Validate request body
            if body is None:
                return {"status": 422, "body": {"errors": ["Request body is required"]}}

            errors = validate_chat_request(body)
            if errors:
                return {"status": 422, "body": {"errors": errors}}

            return {"status": 200, "body": {"response": "OK", "user": user_info}}
        else:
            return {"status": 405, "error": "Method not allowed"}

    else:
        return {"status": 404, "error": "Not found"}

    # Note: This simulates the request lifecycle that FastAPI handles:
    # 1. Middleware (auth check)
    # 2. Dependency injection (API key -> user info)
    # 3. Route matching (path + method)
    # 4. Request validation (Pydantic)
    # 5. Handler execution
    # 6. Response serialization
    #
    # In real FastAPI, all of this is declarative via decorators and type hints.


# =============================================================================
# SELF-CHECK TESTS
# =============================================================================

if __name__ == "__main__":
    print("Running self-checks...\n")

    # Test Exercise 1: Book model
    try:
        book = Book(title="Python Crash Course", author="Eric Matthes", year=2019)
        assert book.title == "Python Crash Course"
        assert book.isbn is None
        book2 = Book(title="Fluent Python", author="Luciano", year=2022, isbn="978-1")
        assert book2.isbn == "978-1"
        try:
            Book(title="", author="Test", year=2020)
            assert False, "Should reject empty title"
        except Exception:
            pass
        print("Exercise 1 (Book model): PASSED")
    except Exception as e:
        print(f"Exercise 1 (Book model): FAILED - {e}")

    # Test Exercise 2: Chat models
    try:
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        req = CompletionRequest(messages=[msg])
        assert req.model == "claude-3-sonnet"
        assert req.temperature == 0.7
        assert req.stream is False
        print("Exercise 2 (Chat models): PASSED")
    except Exception as e:
        print(f"Exercise 2 (Chat models): FAILED - {e}")

    # Test Exercise 3: CompletionResponse
    try:
        resp = CompletionResponse(
            id="test-1", model="claude", content="Hi",
            prompt_tokens=10, completion_tokens=5,
        )
        assert resp.total_tokens == 15
        assert resp.estimated_cost() == 15 * 0.00001
        assert resp.estimated_cost(0.001) == 15 * 0.001
        print("Exercise 3 (CompletionResponse): PASSED")
    except Exception as e:
        print(f"Exercise 3 (CompletionResponse): FAILED - {e}")

    # Test Exercise 4: Pagination
    try:
        result = paginate([1, 2, 3, 4, 5], skip=0, limit=3)
        assert result["items"] == [1, 2, 3]
        assert result["total"] == 5
        assert result["has_more"] is True
        result2 = paginate([1, 2, 3], skip=2, limit=10)
        assert result2["items"] == [3]
        assert result2["has_more"] is False
        result3 = paginate(list(range(200)), skip=0, limit=150)
        assert result3["limit"] == 100
        print("Exercise 4 (Pagination): PASSED")
    except Exception as e:
        print(f"Exercise 4 (Pagination): FAILED - {e}")

    # Test Exercise 5: Filter Items
    try:
        items = [
            {"name": "Laptop", "category": "electronics", "price": 999.99},
            {"name": "Book", "category": "education", "price": 29.99},
            {"name": "Keyboard", "category": "electronics", "price": 79.99},
        ]
        assert len(filter_items(items, query="key")) == 1
        assert filter_items(items, query="key")[0]["name"] == "Keyboard"
        assert len(filter_items(items, category="electronics")) == 2
        assert len(filter_items(items, min_price=50, max_price=100)) == 1
        assert len(filter_items(items)) == 3
        print("Exercise 5 (Filter Items): PASSED")
    except Exception as e:
        print(f"Exercise 5 (Filter Items): FAILED - {e}")

    # Test Exercise 6: API Key Validator
    try:
        user = validate_api_key("sk-test-key-1")
        assert user["name"] == "Alice"
        assert user["tier"] == "free"
        try:
            validate_api_key("invalid-key")
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "Invalid API key" in str(e)
        print("Exercise 6 (API Key Validator): PASSED")
    except Exception as e:
        print(f"Exercise 6 (API Key Validator): FAILED - {e}")

    # Test Exercise 7: Rate Limiter
    try:
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is False
        assert limiter.get_remaining("user1") == 0
        assert limiter.is_allowed("user2") is True
        assert limiter.get_remaining("user2") == 2
        print("Exercise 7 (Rate Limiter): PASSED")
    except Exception as e:
        print(f"Exercise 7 (Rate Limiter): FAILED - {e}")

    # Test Exercise 8: Model Registry
    try:
        registry = ModelRegistry()
        registry.register("gpt-4", "GPT-4", "1.0", "chat")
        registry.register("embed-1", "Embedder", "1.0", "embedding")
        assert registry.get("gpt-4")["name"] == "GPT-4"
        assert len(registry.list_models()) == 2
        assert len(registry.list_models(model_type="chat")) == 1
        try:
            registry.get("nonexistent")
            assert False, "Should raise KeyError"
        except KeyError:
            pass
        print("Exercise 8 (Model Registry): PASSED")
    except Exception as e:
        print(f"Exercise 8 (Model Registry): FAILED - {e}")

    # Test Exercise 9: Error Response Builder
    try:
        resp = build_error_response(404, "not_found", "Model not found")
        assert resp["status_code"] == 404
        assert resp["error"]["type"] == "not_found"
        assert "details" not in resp
        resp2 = build_error_response(422, "validation", "Bad", {"field": "x"})
        assert resp2["details"] == {"field": "x"}
        print("Exercise 9 (Error Response Builder): PASSED")
    except Exception as e:
        print(f"Exercise 9 (Error Response Builder): FAILED - {e}")

    # Test Exercise 10: Request Validator
    try:
        assert validate_chat_request({"messages": [{"role": "user", "content": "Hi"}]}) == []
        errors = validate_chat_request({})
        assert "messages is required" in errors
        errors2 = validate_chat_request({"messages": [{"role": "invalid", "content": "Hi"}]})
        assert any("role" in e for e in errors2)
        errors3 = validate_chat_request({"messages": [{"role": "user", "content": "Hi"}], "temperature": 3.0})
        assert any("temperature" in e for e in errors3)
        print("Exercise 10 (Request Validator): PASSED")
    except Exception as e:
        print(f"Exercise 10 (Request Validator): FAILED - {e}")

    # Test Exercise 11: CRUD Store
    try:
        store = CRUDStore()
        item = store.create({"name": "Test"})
        assert item["id"] == 1
        assert item["name"] == "Test"
        assert store.read(1)["name"] == "Test"
        updated = store.update(1, {"name": "Updated"})
        assert updated["name"] == "Updated"
        assert "updated_at" in updated
        deleted = store.delete(1)
        assert deleted["name"] == "Updated"
        try:
            store.read(1)
            assert False, "Should raise KeyError"
        except KeyError:
            pass
        print("Exercise 11 (CRUD Store): PASSED")
    except Exception as e:
        print(f"Exercise 11 (CRUD Store): FAILED - {e}")

    # Test Exercise 12: API Simulation
    try:
        result = simulate_api_request("GET", "/health", {"X-API-Key": "sk-test-key-1"})
        assert result["status"] == 200
        assert result["body"]["status"] == "healthy"
        result2 = simulate_api_request("GET", "/health", {})
        assert result2["status"] == 401
        result3 = simulate_api_request("POST", "/chat", {"X-API-Key": "sk-test-key-1"},
                                       {"messages": [{"role": "user", "content": "Hi"}]})
        assert result3["status"] == 200
        result4 = simulate_api_request("GET", "/unknown", {"X-API-Key": "sk-test-key-1"})
        assert result4["status"] == 404
        print("Exercise 12 (API Simulation): PASSED")
    except Exception as e:
        print(f"Exercise 12 (API Simulation): FAILED - {e}")

    print("\nAll self-checks complete!")
