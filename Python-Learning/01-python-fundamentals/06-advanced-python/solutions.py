"""
Module 06: Advanced Python - Solutions
======================================

Complete solutions for all 15 exercises. Where applicable, Pythonic
alternatives are noted in comments.
"""

from __future__ import annotations

import math
import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Any, TypeVar, Iterator, Generator


# ---------------------------------------------------------------------------
# WARM-UP
# ---------------------------------------------------------------------------

def exercise_1_call_counter(func: Callable) -> Callable:
    """Decorator that counts how many times a function is called."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.call_count += 1
        return func(*args, **kwargs)
    wrapper.call_count = 0
    return wrapper


def exercise_2_fibonacci_generator(n: int) -> Generator[int, None, None]:
    """Generator that yields the first n Fibonacci numbers."""
    if n <= 0:
        return
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


def exercise_3_chunks(iterable: list, size: int) -> Generator[list, None, None]:
    """Generator that yields successive chunks of the given size."""
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

    # Alternative using itertools:
    # from itertools import islice
    # it = iter(iterable)
    # while chunk := list(islice(it, size)):
    #     yield chunk


def exercise_4_timer_decorator(func: Callable) -> Callable:
    """Decorator that measures and records execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        wrapper.last_elapsed = elapsed
        wrapper.total_elapsed += elapsed
        return result
    wrapper.last_elapsed = 0.0
    wrapper.total_elapsed = 0.0
    return wrapper


# ---------------------------------------------------------------------------
# CORE
# ---------------------------------------------------------------------------

def exercise_5_retry_decorator(
    max_attempts: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """Parameterized decorator that retries a function on failure."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
            raise last_exception  # type: ignore
        return wrapper
    return decorator

    # Alternative: re-raise on last attempt
    # def decorator(func):
    #     @wraps(func)
    #     def wrapper(*args, **kwargs):
    #         for attempt in range(max_attempts):
    #             try:
    #                 return func(*args, **kwargs)
    #             except exceptions:
    #                 if attempt == max_attempts - 1:
    #                     raise
    #     return wrapper
    # return decorator


def exercise_6_context_manager_class() -> type:
    """IndentedPrinter context manager class."""

    class IndentedPrinter:
        def __init__(self, indent: int = 4) -> None:
            self._indent_size = indent
            self._depth = 0
            self.output: list[str] = []

        def __enter__(self):
            self._depth += 1
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._depth -= 1
            return False

        def print(self, *args: Any) -> None:
            prefix = " " * (self._indent_size * self._depth)
            text = " ".join(str(a) for a in args)
            self.output.append(f"{prefix}{text}")

    return IndentedPrinter


def exercise_7_validated_config() -> type:
    """AppConfig Pydantic model with validation."""
    from pydantic import BaseModel, Field, field_validator

    class AppConfig(BaseModel):
        app_name: str = Field(min_length=1, max_length=50)
        debug: bool = False
        port: int = Field(ge=1, le=65535)
        database_url: str
        max_connections: int = Field(default=10, ge=1)
        allowed_origins: list[str] = Field(default_factory=list)

        @field_validator("database_url")
        @classmethod
        def validate_database_url(cls, v: str) -> str:
            if not (v.startswith("postgresql://") or v.startswith("sqlite://")):
                raise ValueError(
                    "database_url must start with 'postgresql://' or 'sqlite://'"
                )
            return v

    return AppConfig


def exercise_8_flatten_generator(nested: Any) -> Generator[Any, None, None]:
    """Generator that recursively flattens nested lists/tuples."""
    if isinstance(nested, str):
        yield nested
    elif isinstance(nested, (list, tuple)):
        for item in nested:
            yield from exercise_8_flatten_generator(item)
    else:
        yield nested


def exercise_9_cached_property_decorator(func: Callable) -> Any:
    """Descriptor that acts as a cached property."""

    class CachedProperty:
        def __init__(self, func: Callable) -> None:
            self.func = func
            self.attr_name = ""

        def __set_name__(self, owner: type, name: str) -> None:
            self.attr_name = f"_cached_{name}"

        def __get__(self, obj: Any, objtype: type | None = None) -> Any:
            if obj is None:
                return self
            if not hasattr(obj, self.attr_name):
                value = self.func(obj)
                setattr(obj, self.attr_name, value)
            return getattr(obj, self.attr_name)

    return CachedProperty(func)

    # Alternative: simpler approach using the instance __dict__
    # class CachedProperty:
    #     def __init__(self, func):
    #         self.func = func
    #         self.attr_name = ""
    #
    #     def __set_name__(self, owner, name):
    #         self.attr_name = name
    #
    #     def __get__(self, obj, objtype=None):
    #         if obj is None:
    #             return self
    #         value = self.func(obj)
    #         # Store directly on the instance, which shadows the descriptor
    #         setattr(obj, self.attr_name, value)
    #         return value


# ---------------------------------------------------------------------------
# CHALLENGE
# ---------------------------------------------------------------------------

def exercise_10_generic_decorator() -> Callable:
    """Return a memoize decorator with .cache and .cache_clear()."""

    def memoize(func: Callable) -> Callable:
        cache: dict = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                key = (args, frozenset(kwargs.items()))
                hash(key)  # Test hashability
            except TypeError:
                # Unhashable arguments -- skip caching
                return func(*args, **kwargs)

            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]

        wrapper.cache = cache

        def cache_clear():
            cache.clear()

        wrapper.cache_clear = cache_clear
        return wrapper

    return memoize


def exercise_11_range_iterator() -> type:
    """FloatRange iterable class."""

    class FloatRange:
        def __init__(self, start: float, stop: float, step: float) -> None:
            self.start = start
            self.stop = stop
            self.step = step
            # Pre-compute the values for consistency
            self._values: list[float] = []
            current = start
            while current < stop - 1e-12:
                self._values.append(round(current, 10))
                current += step

        def __iter__(self) -> Iterator[float]:
            return iter(self._values)

        def __reversed__(self) -> Iterator[float]:
            return iter(reversed(self._values))

        def __len__(self) -> int:
            return len(self._values)

        def __contains__(self, value: float) -> bool:
            return any(abs(v - value) < 1e-9 for v in self._values)

        def __repr__(self) -> str:
            return f"FloatRange({self.start}, {self.stop}, {self.step})"

    return FloatRange


def exercise_12_pydantic_api_models() -> tuple[type, type, type]:
    """Pydantic API models: CreateUserRequest, UserResponse, UserListResponse."""
    import re
    from pydantic import BaseModel, Field, field_validator

    class CreateUserRequest(BaseModel):
        username: str = Field(min_length=3, max_length=20)
        email: str
        password: str = Field(min_length=8)
        age: int = Field(ge=13)
        tags: list[str] = Field(default_factory=list, max_length=10)

        @field_validator("username")
        @classmethod
        def validate_username(cls, v: str) -> str:
            if not re.match(r"^[a-zA-Z0-9_]+$", v):
                raise ValueError("Username must be alphanumeric with underscores only")
            return v

        @field_validator("email")
        @classmethod
        def validate_email(cls, v: str) -> str:
            if "@" not in v:
                raise ValueError("Email must contain @")
            return v

    class UserResponse(BaseModel):
        id: int
        username: str
        email: str
        age: int
        tags: list[str] = Field(default_factory=list)
        created_at: str

    class UserListResponse(BaseModel):
        users: list[UserResponse]
        total: int
        page: int = Field(default=1, ge=1)
        per_page: int = Field(default=20, ge=1, le=100)

    return CreateUserRequest, UserResponse, UserListResponse


# ---------------------------------------------------------------------------
# SWIFT BRIDGE
# ---------------------------------------------------------------------------

def exercise_13_clamped_decorator(min_val: float, max_val: float) -> Callable:
    """Parameterized decorator that clamps the return value."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return max(min_val, min(max_val, result))
        return wrapper
    return decorator


def exercise_14_sequence_like_iterator() -> type:
    """RepeatSequence class mimicking Swift's Sequence protocol."""

    class RepeatSequence:
        def __init__(self, element: Any, count: int) -> None:
            self._element = element
            self._count = count

        def __iter__(self) -> Iterator:
            for _ in range(self._count):
                yield self._element

        def __len__(self) -> int:
            return self._count

        def __getitem__(self, index):
            if isinstance(index, slice):
                start, stop, step = index.indices(self._count)
                return [self._element for _ in range(start, stop, step or 1)]
            if index < 0:
                index = self._count + index
            if index < 0 or index >= self._count:
                raise IndexError("index out of range")
            return self._element

        def __contains__(self, value: Any) -> bool:
            return self._count > 0 and value == self._element

        def __repr__(self) -> str:
            return f"RepeatSequence({self._element}, {self._count})"

    return RepeatSequence


def exercise_15_contextmanager_generator():
    """Context manager that temporarily modifies dictionary values."""

    @contextmanager
    def temporary_values(d: dict, **kwargs):
        # Save original state
        saved = {}
        missing_keys = set()

        for key, value in kwargs.items():
            if key in d:
                saved[key] = d[key]
            else:
                missing_keys.add(key)
            d[key] = value

        try:
            yield d
        finally:
            # Restore original values
            for key, value in saved.items():
                d[key] = value
            # Remove keys that didn't exist before
            for key in missing_keys:
                d.pop(key, None)

    return temporary_values


# ===========================================================================
# TESTS
# ===========================================================================

if __name__ == "__main__":
    # --- Exercise 1: Call Counter ---
    @exercise_1_call_counter
    def greet(name):
        return f"Hello, {name}"

    assert greet("Alice") == "Hello, Alice"
    assert greet.call_count == 1
    greet("Bob")
    assert greet.call_count == 2
    assert greet.__name__ == "greet"
    print("Exercise 1 passed!")

    # --- Exercise 2: Fibonacci Generator ---
    assert list(exercise_2_fibonacci_generator(7)) == [0, 1, 1, 2, 3, 5, 8]
    assert list(exercise_2_fibonacci_generator(1)) == [0]
    assert list(exercise_2_fibonacci_generator(0)) == []
    assert list(exercise_2_fibonacci_generator(2)) == [0, 1]
    print("Exercise 2 passed!")

    # --- Exercise 3: Chunks ---
    assert list(exercise_3_chunks([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(exercise_3_chunks([1, 2, 3], 5)) == [[1, 2, 3]]
    assert list(exercise_3_chunks([], 3)) == []
    assert list(exercise_3_chunks([1], 1)) == [[1]]
    print("Exercise 3 passed!")

    # --- Exercise 4: Timer Decorator ---
    @exercise_4_timer_decorator
    def slow_add(a, b):
        time.sleep(0.01)
        return a + b

    result = slow_add(1, 2)
    assert result == 3
    assert slow_add.last_elapsed >= 0.005
    first_elapsed = slow_add.last_elapsed
    slow_add(3, 4)
    assert slow_add.total_elapsed >= first_elapsed
    assert slow_add.__name__ == "slow_add"
    print("Exercise 4 passed!")

    # --- Exercise 5: Retry Decorator ---
    attempt_count = {"n": 0}

    @exercise_5_retry_decorator(max_attempts=3, exceptions=(ValueError,))
    def flaky_func():
        attempt_count["n"] += 1
        if attempt_count["n"] < 3:
            raise ValueError("not yet")
        return "success"

    assert flaky_func() == "success"
    assert attempt_count["n"] == 3

    @exercise_5_retry_decorator(max_attempts=3, exceptions=(ValueError,))
    def type_error_func():
        raise TypeError("wrong type")

    try:
        type_error_func()
        assert False, "Should have raised TypeError"
    except TypeError:
        pass
    print("Exercise 5 passed!")

    # --- Exercise 6: IndentedPrinter ---
    IndentedPrinter = exercise_6_context_manager_class()
    p = IndentedPrinter(indent=2)
    with p:
        p.print("level 1")
        with p:
            p.print("level 2")
        p.print("back to 1")
    assert p.output == ["  level 1", "    level 2", "  back to 1"]
    print("Exercise 6 passed!")

    # --- Exercise 7: Validated Config (Pydantic) ---
    AppConfig = exercise_7_validated_config()
    config = AppConfig(
        app_name="MyApp",
        port=8080,
        database_url="postgresql://localhost/db",
    )
    assert config.debug is False
    assert config.max_connections == 10
    assert config.allowed_origins == []

    try:
        AppConfig(app_name="X", port=0, database_url="mysql://localhost")
        assert False, "Should fail validation"
    except Exception:
        pass

    try:
        AppConfig(app_name="X", port=8080, database_url="mysql://localhost")
        assert False, "Should fail on database_url"
    except Exception:
        pass
    print("Exercise 7 passed!")

    # --- Exercise 8: Flatten Generator ---
    assert list(exercise_8_flatten_generator([1, [2, [3, 4]], [5, 6]])) == [1, 2, 3, 4, 5, 6]
    assert list(exercise_8_flatten_generator([1, (2, 3), [[4]], "hello"])) == [1, 2, 3, 4, "hello"]
    assert list(exercise_8_flatten_generator([])) == []
    assert list(exercise_8_flatten_generator([1])) == [1]
    assert list(exercise_8_flatten_generator("hello")) == ["hello"]
    print("Exercise 8 passed!")

    # --- Exercise 9: Cached Property ---
    compute_count = {"n": 0}

    class MyClass:
        @exercise_9_cached_property_decorator
        def expensive(self):
            compute_count["n"] += 1
            return 42

    obj = MyClass()
    assert obj.expensive == 42
    assert compute_count["n"] == 1
    assert obj.expensive == 42
    assert compute_count["n"] == 1

    obj2 = MyClass()
    assert obj2.expensive == 42
    assert compute_count["n"] == 2
    print("Exercise 9 passed!")

    # --- Exercise 10: Memoize Decorator ---
    memoize = exercise_10_generic_decorator()
    compute_count_10 = {"n": 0}

    @memoize
    def expensive_add(a, b):
        compute_count_10["n"] += 1
        return a + b

    assert expensive_add(1, 2) == 3
    assert compute_count_10["n"] == 1
    assert expensive_add(1, 2) == 3
    assert compute_count_10["n"] == 1
    assert expensive_add(3, 4) == 7
    assert compute_count_10["n"] == 2
    assert len(expensive_add.cache) == 2
    expensive_add.cache_clear()
    assert len(expensive_add.cache) == 0
    assert expensive_add(1, 2) == 3
    assert compute_count_10["n"] == 3
    print("Exercise 10 passed!")

    # --- Exercise 11: FloatRange Iterator ---
    FloatRange = exercise_11_range_iterator()
    r = FloatRange(0.0, 1.0, 0.3)
    values = list(r)
    assert len(values) == 4
    assert abs(values[0] - 0.0) < 1e-9
    assert abs(values[1] - 0.3) < 1e-9
    assert abs(values[2] - 0.6) < 1e-9
    assert abs(values[3] - 0.9) < 1e-9
    assert len(r) == 4
    assert list(r) == values
    rev = list(reversed(r))
    assert abs(rev[0] - 0.9) < 1e-9
    assert abs(rev[-1] - 0.0) < 1e-9
    print("Exercise 11 passed!")

    # --- Exercise 12: Pydantic API Models ---
    CreateUserRequest, UserResponse, UserListResponse = exercise_12_pydantic_api_models()

    req = CreateUserRequest(
        username="alice_123",
        email="alice@test.com",
        password="securepass",
        age=25,
    )
    assert req.username == "alice_123"
    assert req.tags == []

    try:
        CreateUserRequest(
            username="a",
            email="invalid",
            password="short",
            age=10,
        )
        assert False, "Should fail validation"
    except Exception:
        pass

    resp = UserResponse(
        id=1,
        username="alice",
        email="a@b.com",
        age=25,
        tags=["admin"],
        created_at="2024-01-01T00:00:00",
    )
    assert resp.id == 1

    list_resp = UserListResponse(
        users=[resp],
        total=1,
    )
    assert list_resp.page == 1
    assert list_resp.per_page == 20
    print("Exercise 12 passed!")

    # --- Exercise 13: Clamped Decorator ---
    @exercise_13_clamped_decorator(0, 100)
    def calc_score(base, bonus):
        return base + bonus

    assert calc_score(80, 30) == 100
    assert calc_score(50, 10) == 60
    assert calc_score(-10, 5) == 0
    assert calc_score(0, 0) == 0
    print("Exercise 13 passed!")

    # --- Exercise 14: RepeatSequence ---
    RepeatSequence = exercise_14_sequence_like_iterator()
    s = RepeatSequence("Hello", 3)
    assert list(s) == ["Hello", "Hello", "Hello"]
    assert len(s) == 3
    assert s[0] == "Hello"
    assert s[-1] == "Hello"
    assert s[1:3] == ["Hello", "Hello"]
    assert "Hello" in s
    assert "World" not in s
    assert list(s) == ["Hello", "Hello", "Hello"]
    assert repr(s) == "RepeatSequence(Hello, 3)"
    print("Exercise 14 passed!")

    # --- Exercise 15: Temporary Values Context Manager ---
    temporary_values = exercise_15_contextmanager_generator()
    config = {"debug": False, "verbose": False}
    with temporary_values(config, debug=True, new_key="temp"):
        assert config["debug"] is True
        assert config["new_key"] == "temp"
        assert config["verbose"] is False
    assert config["debug"] is False
    assert "new_key" not in config
    assert config["verbose"] is False
    print("Exercise 15 passed!")

    print("\n All exercises passed!")
