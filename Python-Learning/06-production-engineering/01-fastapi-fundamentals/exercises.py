"""
Module 01: FastAPI Fundamentals - Exercises
=============================================
Target audience: Swift developers learning Python API development.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- These exercises build FastAPI components that can be tested independently.
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.

Difficulty levels:
  Easy   - Direct translation from Swift/Vapor concepts
  Medium - Requires understanding FastAPI-specific patterns
  Hard   - Combines multiple concepts or requires creative design
"""

from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Any


# =============================================================================
# SECTION 1: Pydantic Models (Request/Response Bodies)
# =============================================================================

# Exercise 1: Basic Pydantic Model
# Difficulty: Easy
# Create a Pydantic model for a book with title, author, year, and optional ISBN.
class Book(BaseModel):
    """A book model with validation.

    Fields:
    - title: str (required, min length 1)
    - author: str (required)
    - year: int (required, must be >= 1000 and <= 2030)
    - isbn: str or None (optional, default None)

    Think of this like a Swift Codable struct:
        struct Book: Codable {
            let title: String
            let author: String
            let year: Int
            let isbn: String?
        }
    """
    pass


# Exercise 2: Nested Pydantic Models
# Difficulty: Easy
# Create models for a chat completion request.
class Message(BaseModel):
    """A chat message.

    Fields:
    - role: str (required, one of "user", "assistant", "system")
    - content: str (required, min length 1)
    """
    pass


class CompletionRequest(BaseModel):
    """A chat completion request.

    Fields:
    - messages: list of Message (required, min length 1)
    - model: str (default "claude-3-sonnet")
    - temperature: float (default 0.7, between 0.0 and 2.0)
    - max_tokens: int (default 1024, between 1 and 4096)
    - stream: bool (default False)
    """
    pass


# Exercise 3: Response Model with Computed Fields
# Difficulty: Medium
class CompletionResponse(BaseModel):
    """A chat completion response.

    Fields:
    - id: str (required)
    - model: str (required)
    - content: str (required)
    - prompt_tokens: int (required)
    - completion_tokens: int (required)
    - created_at: datetime (default to now)

    Properties/Methods:
    - total_tokens property: returns prompt_tokens + completion_tokens
    - estimated_cost method: returns total_tokens * cost_per_token (default 0.00001)
    """
    pass


# =============================================================================
# SECTION 2: Endpoint Logic Functions
# =============================================================================

# Exercise 4: Pagination Helper
# Difficulty: Easy
# Create a function that computes pagination metadata.
def paginate(
    items: list[Any],
    skip: int = 0,
    limit: int = 10,
) -> dict[str, Any]:
    """Return a paginated response dict.

    Args:
        items: The full list of items
        skip: Number of items to skip
        limit: Maximum items to return (cap at 100)

    Returns:
        dict with keys: "items" (the sliced list), "total" (total count),
        "skip", "limit", "has_more" (bool: are there more items?)

    >>> paginate([1,2,3,4,5], skip=0, limit=3)
    {'items': [1, 2, 3], 'total': 5, 'skip': 0, 'limit': 3, 'has_more': True}
    >>> paginate([1,2,3], skip=2, limit=10)
    {'items': [3], 'total': 3, 'skip': 2, 'limit': 10, 'has_more': False}
    """
    pass


# Exercise 5: Search Filter
# Difficulty: Medium
# Create a function that filters items based on query parameters.
def filter_items(
    items: list[dict[str, Any]],
    query: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
) -> list[dict[str, Any]]:
    """Filter a list of item dicts based on various criteria.

    Each item dict has keys: "name" (str), "category" (str), "price" (float)

    Filtering rules:
    - query: case-insensitive substring match on "name"
    - category: exact match on "category"
    - min_price: item price >= min_price
    - max_price: item price <= max_price
    - None means "don't filter by this criterion"

    >>> items = [
    ...     {"name": "Laptop", "category": "electronics", "price": 999.99},
    ...     {"name": "Book", "category": "education", "price": 29.99},
    ...     {"name": "Keyboard", "category": "electronics", "price": 79.99},
    ... ]
    >>> filter_items(items, query="key")
    [{'name': 'Keyboard', 'category': 'electronics', 'price': 79.99}]
    >>> filter_items(items, category="electronics", max_price=100)
    [{'name': 'Keyboard', 'category': 'electronics', 'price': 79.99}]
    """
    pass


# Exercise 6: API Key Validator
# Difficulty: Easy
# Create a function that validates an API key and returns user info.
def validate_api_key(api_key: str) -> dict[str, Any]:
    """Validate an API key and return the associated user info.

    Valid API keys (hardcoded for exercise):
    - "sk-test-key-1" -> {"user_id": 1, "name": "Alice", "tier": "free"}
    - "sk-test-key-2" -> {"user_id": 2, "name": "Bob", "tier": "pro"}
    - "sk-test-key-3" -> {"user_id": 3, "name": "Charlie", "tier": "enterprise"}

    If the key is not valid, raise a ValueError with message "Invalid API key".

    >>> validate_api_key("sk-test-key-1")
    {'user_id': 1, 'name': 'Alice', 'tier': 'free'}
    >>> validate_api_key("bad-key")
    Traceback (most recent call last):
        ...
    ValueError: Invalid API key
    """
    pass


# Exercise 7: Rate Limiter
# Difficulty: Medium
# Create a simple in-memory rate limiter.
class RateLimiter:
    """A simple in-memory rate limiter.

    Tracks request counts per key within a time window.

    Similar to iOS's approach of throttling network requests,
    but on the server side.

    Args:
        max_requests: Maximum requests allowed per window
        window_seconds: Time window in seconds
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """Initialize the rate limiter.

        Store max_requests, window_seconds, and create an empty dict
        to track requests. Each key maps to a list of timestamps.
        """
        pass

    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed for the given key.

        Steps:
        1. Get current timestamp
        2. Remove any timestamps older than window_seconds for this key
        3. If count < max_requests, add current timestamp and return True
        4. Otherwise return False

        >>> limiter = RateLimiter(max_requests=2, window_seconds=60)
        >>> limiter.is_allowed("user1")
        True
        >>> limiter.is_allowed("user1")
        True
        >>> limiter.is_allowed("user1")
        False
        """
        pass

    def get_remaining(self, key: str) -> int:
        """Return the number of remaining requests for a key.

        >>> limiter = RateLimiter(max_requests=5, window_seconds=60)
        >>> limiter.get_remaining("user1")
        5
        >>> limiter.is_allowed("user1")
        True
        >>> limiter.get_remaining("user1")
        4
        """
        pass


# =============================================================================
# SECTION 3: Dependency Injection Patterns
# =============================================================================

# Exercise 8: Service Layer Pattern
# Difficulty: Medium
# Create a service class that would be injected via Depends().
class ModelRegistry:
    """Registry of available ML models.

    This simulates a service that would be injected into endpoint handlers.
    In FastAPI, you'd use Depends(get_model_registry) to inject it.
    """

    def __init__(self):
        """Initialize with a dict of model_id -> model_info."""
        self._models: dict[str, dict[str, Any]] = {}

    def register(self, model_id: str, name: str, version: str, model_type: str) -> None:
        """Register a new model.

        Store model info as a dict with keys: name, version, type, registered_at (datetime.now())

        >>> registry = ModelRegistry()
        >>> registry.register("gpt-4", "GPT-4", "1.0", "chat")
        >>> "gpt-4" in registry._models
        True
        """
        pass

    def get(self, model_id: str) -> dict[str, Any]:
        """Get model info by ID. Raise KeyError if not found.

        >>> registry = ModelRegistry()
        >>> registry.register("gpt-4", "GPT-4", "1.0", "chat")
        >>> info = registry.get("gpt-4")
        >>> info["name"]
        'GPT-4'
        """
        pass

    def list_models(self, model_type: str | None = None) -> list[dict[str, Any]]:
        """List all models, optionally filtered by type.

        Returns list of dicts, each with "id" added to the model info.

        >>> registry = ModelRegistry()
        >>> registry.register("gpt-4", "GPT-4", "1.0", "chat")
        >>> registry.register("embed-1", "Embedder", "1.0", "embedding")
        >>> len(registry.list_models())
        2
        >>> len(registry.list_models(model_type="chat"))
        1
        """
        pass


# Exercise 9: Error Response Builder
# Difficulty: Easy
# Create a function that builds standardized error responses.
def build_error_response(
    status_code: int,
    error_type: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a standardized error response dict.

    Returns a dict with keys:
    - "error": {"type": error_type, "message": message}
    - "status_code": status_code
    - "details": details (only if not None)

    >>> build_error_response(404, "not_found", "Model not found")
    {'error': {'type': 'not_found', 'message': 'Model not found'}, 'status_code': 404}
    >>> resp = build_error_response(422, "validation", "Bad input", {"field": "name"})
    >>> resp["details"]
    {'field': 'name'}
    """
    pass


# Exercise 10: Request Validator
# Difficulty: Medium
# Create a function that validates a chat request and returns errors.
def validate_chat_request(request_data: dict[str, Any]) -> list[str]:
    """Validate a chat request dict and return a list of error messages.

    Validation rules:
    1. "messages" key must exist and be a non-empty list
    2. Each message must have "role" (str) and "content" (str) keys
    3. "role" must be one of: "user", "assistant", "system"
    4. "content" must be non-empty string
    5. "temperature" (if present) must be a float/int between 0.0 and 2.0
    6. "max_tokens" (if present) must be an int between 1 and 4096

    Returns empty list if valid, list of error strings if invalid.

    >>> validate_chat_request({"messages": [{"role": "user", "content": "Hi"}]})
    []
    >>> errors = validate_chat_request({})
    >>> "messages is required" in errors
    True
    """
    pass


# =============================================================================
# SECTION 4: Full Endpoint Simulation
# =============================================================================

# Exercise 11: CRUD Operations
# Difficulty: Medium
# Implement a simple in-memory CRUD store.
class CRUDStore:
    """In-memory CRUD store for any entity type.

    Simulates what you'd build for FastAPI endpoints.
    """

    def __init__(self):
        """Initialize with empty dict and counter starting at 1."""
        pass

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new entity. Add 'id' and 'created_at' fields.

        Returns the created entity with id and created_at added.

        >>> store = CRUDStore()
        >>> item = store.create({"name": "Test"})
        >>> item["id"]
        1
        >>> item["name"]
        'Test'
        >>> "created_at" in item
        True
        """
        pass

    def read(self, entity_id: int) -> dict[str, Any]:
        """Read an entity by ID. Raise KeyError if not found.

        >>> store = CRUDStore()
        >>> store.create({"name": "Test"})['id']
        1
        >>> store.read(1)["name"]
        'Test'
        """
        pass

    def update(self, entity_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Update an entity. Raise KeyError if not found.

        Merge data into existing entity (don't replace id or created_at).
        Add 'updated_at' field with current datetime.

        >>> store = CRUDStore()
        >>> store.create({"name": "Test"})['id']
        1
        >>> updated = store.update(1, {"name": "Updated"})
        >>> updated["name"]
        'Updated'
        >>> "updated_at" in updated
        True
        """
        pass

    def delete(self, entity_id: int) -> dict[str, Any]:
        """Delete an entity. Raise KeyError if not found. Returns deleted entity.

        >>> store = CRUDStore()
        >>> store.create({"name": "Test"})['id']
        1
        >>> deleted = store.delete(1)
        >>> deleted["name"]
        'Test'
        """
        pass

    def list_all(self, skip: int = 0, limit: int = 10) -> list[dict[str, Any]]:
        """List entities with pagination.

        >>> store = CRUDStore()
        >>> for i in range(5):
        ...     _ = store.create({"name": f"Item {i}"})
        >>> len(store.list_all(skip=0, limit=3))
        3
        >>> len(store.list_all(skip=3, limit=10))
        2
        """
        pass


# Exercise 12: Full API Simulation
# Difficulty: Hard
# Simulate a complete API flow: auth -> validate -> process -> respond.
def simulate_api_request(
    method: str,
    path: str,
    headers: dict[str, str],
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Simulate processing an API request through the full pipeline.

    Steps:
    1. Check "X-API-Key" header exists, if not return {"status": 401, "error": "Missing API key"}
    2. Validate API key using validate_api_key(). If ValueError, return {"status": 401, "error": "Invalid API key"}
    3. Route the request:
       - GET /health -> {"status": 200, "body": {"status": "healthy"}}
       - POST /chat -> Validate body using validate_chat_request().
         If errors: return {"status": 422, "body": {"errors": [...]}}
         If valid: return {"status": 200, "body": {"response": "OK", "user": <user_info>}}
       - Any other path -> {"status": 404, "error": "Not found"}
    4. Any other method for known paths -> {"status": 405, "error": "Method not allowed"}

    >>> simulate_api_request("GET", "/health", {"X-API-Key": "sk-test-key-1"})
    {'status': 200, 'body': {'status': 'healthy'}}
    >>> simulate_api_request("GET", "/health", {})
    {'status': 401, 'error': 'Missing API key'}
    """
    pass


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
        # Test limit capping
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
        assert len(filter_items(items)) == 3  # No filters
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
        assert limiter.is_allowed("user1") is False  # Exceeded
        assert limiter.get_remaining("user1") == 0
        assert limiter.is_allowed("user2") is True  # Different user OK
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
