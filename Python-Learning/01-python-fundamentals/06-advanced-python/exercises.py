"""
Module 06: Advanced Python - Exercises
======================================

15 exercises covering decorators, generators, context managers, iterators,
type hints, and Pydantic v2.

Target audience: Swift/iOS developers learning Python.

Instructions:
    - Replace `pass` (or `...`) with your implementation.
    - Run this file to check your answers with the assert-based tests at the bottom.
    - Type hints are provided in the signatures -- follow them.
"""

from __future__ import annotations

import time
from functools import wraps
from typing import Callable, Any, TypeVar, Iterator, Generator


# ---------------------------------------------------------------------------
# WARM-UP: Simple decorators, basic generators
# ---------------------------------------------------------------------------

def exercise_1_call_counter(func: Callable) -> Callable:
    """Create a decorator that counts how many times a function is called.

    The decorated function should have a `.call_count` attribute that
    tracks the number of calls.

    Use @functools.wraps to preserve function metadata.

    Examples:
        @exercise_1_call_counter
        def greet(name):
            return f"Hello, {name}"

        greet("Alice")    -> "Hello, Alice"
        greet.call_count  -> 1
        greet("Bob")
        greet.call_count  -> 2
    """
    pass


def exercise_2_fibonacci_generator(n: int) -> Generator[int, None, None]:
    """Create a generator that yields the first n Fibonacci numbers.

    fib(0)=0, fib(1)=1, fib(k)=fib(k-1)+fib(k-2) for k>=2.

    Examples:
        list(exercise_2_fibonacci_generator(7))  -> [0, 1, 1, 2, 3, 5, 8]
        list(exercise_2_fibonacci_generator(1))  -> [0]
        list(exercise_2_fibonacci_generator(0))  -> []
    """
    pass


def exercise_3_chunks(iterable: list, size: int) -> Generator[list, None, None]:
    """Create a generator that yields successive chunks of the given size.

    The last chunk may be smaller than `size` if the iterable doesn't
    divide evenly.

    Examples:
        list(exercise_3_chunks([1, 2, 3, 4, 5], 2))  -> [[1, 2], [3, 4], [5]]
        list(exercise_3_chunks([1, 2, 3], 5))         -> [[1, 2, 3]]
        list(exercise_3_chunks([], 3))                 -> []
    """
    pass


def exercise_4_timer_decorator(func: Callable) -> Callable:
    """Create a decorator that measures and records execution time.

    The decorated function should have:
    - .last_elapsed: float (seconds of the most recent call)
    - .total_elapsed: float (cumulative seconds across all calls)

    The decorated function should still return the original return value.

    Use time.perf_counter() for timing.
    Use @functools.wraps to preserve function metadata.

    Examples:
        @exercise_4_timer_decorator
        def slow():
            time.sleep(0.01)
            return 42

        result = slow()      -> 42
        slow.last_elapsed    -> ~0.01
        slow.total_elapsed   -> ~0.01
    """
    pass


# ---------------------------------------------------------------------------
# CORE: Parameterized decorators, context managers, Pydantic models
# ---------------------------------------------------------------------------

def exercise_5_retry_decorator(
    max_attempts: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """Create a parameterized decorator that retries a function on failure.

    - Retry up to `max_attempts` times total.
    - Only catch exceptions in the `exceptions` tuple.
    - If all attempts fail, raise the last exception.

    Examples:
        @exercise_5_retry_decorator(max_attempts=3, exceptions=(ValueError,))
        def flaky():
            ...
    """
    pass


def exercise_6_context_manager_class() -> type:
    """Create and return an IndentedPrinter context manager class.

    The class should:
    - __init__(self, indent: int = 4): set the indent level (spaces)
    - __enter__: return self
    - __exit__: no special cleanup needed (return False)
    - print(self, *args): print with the current indentation prefix

    Support nesting: when used in nested with-blocks, increase indentation.
    Use a class-level counter to track the current nesting depth.

    Examples:
        IndentedPrinter = exercise_6_context_manager_class()
        printer output should be captured via a custom method, not actual print

        p = IndentedPrinter(indent=2)
        with p:
            p.print("level 1")    -> stores "  level 1"
            with p:
                p.print("level 2")  -> stores "    level 2"
            p.print("back to 1")  -> stores "  back to 1"

        p.output should be ["  level 1", "    level 2", "  back to 1"]
    """
    pass


def exercise_7_validated_config() -> type:
    """Create and return a Pydantic BaseModel called AppConfig with:

    Fields:
        - app_name: str (min_length=1, max_length=50)
        - debug: bool (default False)
        - port: int (between 1 and 65535)
        - database_url: str (must start with "postgresql://" or "sqlite://")
        - max_connections: int (default 10, must be >= 1)
        - allowed_origins: list[str] (default empty list)

    Custom validator:
        - database_url must start with "postgresql://" or "sqlite://"
          (use @field_validator)

    Examples:
        config = AppConfig(
            app_name="MyApp",
            port=8080,
            database_url="postgresql://localhost/db"
        )
        config.debug  -> False
        config.max_connections  -> 10
    """
    pass


def exercise_8_flatten_generator(nested: Any) -> Generator[Any, None, None]:
    """Create a generator that recursively flattens nested lists/tuples.

    Non-list/tuple elements are yielded as-is.
    Strings should NOT be recursively flattened (treat them as atoms).

    Examples:
        list(exercise_8_flatten_generator([1, [2, [3, 4]], [5, 6]]))
            -> [1, 2, 3, 4, 5, 6]
        list(exercise_8_flatten_generator([1, (2, 3), [[4]], "hello"]))
            -> [1, 2, 3, 4, "hello"]
        list(exercise_8_flatten_generator([]))
            -> []
    """
    pass


def exercise_9_cached_property_decorator(func: Callable) -> Any:
    """Create a descriptor that acts as a cached property.

    On first access, compute the value and cache it on the instance.
    On subsequent accesses, return the cached value without recomputing.

    This mimics Swift's lazy var or functools.cached_property.

    Hint: Implement __set_name__ and __get__ methods (descriptor protocol).

    Examples:
        class MyClass:
            @exercise_9_cached_property_decorator
            def expensive(self):
                print("Computing...")
                return 42

        obj = MyClass()
        obj.expensive  -> prints "Computing...", returns 42
        obj.expensive  -> returns 42 (no print, cached)
    """
    pass


# ---------------------------------------------------------------------------
# CHALLENGE: Generic decorator, custom iterator, complex Pydantic validation
# ---------------------------------------------------------------------------

def exercise_10_generic_decorator() -> Callable:
    """Create and return a 'memoize' decorator that:

    1. Caches results based on all positional and keyword arguments
    2. Has a .cache attribute (dict) showing cached values
    3. Has a .cache_clear() method to reset the cache
    4. Uses @functools.wraps to preserve metadata

    Must handle unhashable arguments gracefully (skip caching if args
    contain unhashable types like lists).

    Examples:
        @memoize
        def add(a, b):
            return a + b

        add(1, 2)       -> 3
        add(1, 2)       -> 3 (cached)
        add.cache       -> {((1, 2), frozenset()): 3}
        add.cache_clear()
        add.cache       -> {}
    """
    pass


def exercise_11_range_iterator() -> type:
    """Create and return a FloatRange class that is an iterable (not iterator).

    FloatRange(start, stop, step) produces float values from start up to
    (but not including) stop, incrementing by step.

    Must support:
    - Multiple iterations (return fresh iterator each time)
    - __len__: number of elements
    - __contains__: check if a value is in the range (with float tolerance)
    - __repr__: "FloatRange(start, stop, step)"
    - __reversed__: iterate in reverse order

    Examples:
        r = FloatRange(0.0, 1.0, 0.3)
        list(r)        -> [0.0, 0.3, 0.6, 0.9]
        len(r)         -> 4
        0.3 in r       -> True
        list(r)        -> [0.0, 0.3, 0.6, 0.9]  (reusable!)
        list(reversed(r)) -> [0.9, 0.6, 0.3, 0.0]
    """
    pass


def exercise_12_pydantic_api_models() -> tuple[type, type, type]:
    """Create and return (CreateUserRequest, UserResponse, UserListResponse)
    Pydantic models.

    CreateUserRequest:
        - username: str (3-20 chars, alphanumeric + underscore only)
        - email: str (must contain @)
        - password: str (min 8 chars)
        - age: int (must be >= 13)
        - tags: list[str] (default empty, max 10 items)

    UserResponse:
        - id: int
        - username: str
        - email: str
        - age: int
        - tags: list[str]
        - created_at: str  (ISO format datetime string)

    UserListResponse:
        - users: list[UserResponse]
        - total: int
        - page: int (default 1, >= 1)
        - per_page: int (default 20, 1-100)

    Add validator to CreateUserRequest.username to ensure it matches
    ^[a-zA-Z0-9_]+$ pattern.

    Examples:
        req = CreateUserRequest(
            username="alice_123",
            email="alice@test.com",
            password="securepass",
            age=25,
        )
    """
    pass


# ---------------------------------------------------------------------------
# SWIFT BRIDGE: Property wrappers vs decorators, Sequence vs iterators,
#               Codable vs Pydantic
# ---------------------------------------------------------------------------

def exercise_13_clamped_decorator(min_val: float, max_val: float) -> Callable:
    """Create a parameterized decorator that clamps the return value of a
    function to the range [min_val, max_val].

    This mimics Swift's @Clamped property wrapper concept but applied
    as a function decorator.

    Examples:
        @exercise_13_clamped_decorator(0, 100)
        def calculate_score(base, bonus):
            return base + bonus

        calculate_score(80, 30)   -> 100  (clamped to max)
        calculate_score(50, 10)   -> 60   (within range)
        calculate_score(-10, 5)   -> 0    (clamped to min)
    """
    pass


def exercise_14_sequence_like_iterator() -> type:
    """Create and return a RepeatSequence class mimicking Swift's
    Sequence protocol with custom iteration.

    RepeatSequence(element, count) produces `element` repeated `count` times.

    Must support:
    - Iteration (for x in seq)
    - len()
    - Indexing (seq[0], seq[-1])
    - Slicing (seq[1:3])
    - __contains__
    - __repr__: "RepeatSequence(element, count)"
    - Multiple iteration passes

    Similar to Swift:
        let seq = repeatElement("Hello", count: 3)

    Examples:
        s = RepeatSequence("Hello", 3)
        list(s)     -> ["Hello", "Hello", "Hello"]
        len(s)      -> 3
        s[0]        -> "Hello"
        s[1:3]      -> ["Hello", "Hello"]
    """
    pass


def exercise_15_contextmanager_generator():
    """Create a context manager using @contextlib.contextmanager that
    temporarily modifies a dictionary's values and restores them on exit.

    The context manager function should be called `temporary_values` and
    accept a dict and **kwargs of temporary key-value pairs.

    Return the function (not call it).

    On __enter__:
        - Save the current values (or note missing keys)
        - Set the temporary values

    On __exit__:
        - Restore original values
        - Remove keys that didn't exist before

    Examples:
        config = {"debug": False, "verbose": False}
        with temporary_values(config, debug=True, new_key="temp"):
            config["debug"]     -> True
            config["new_key"]   -> "temp"
        config["debug"]         -> False
        "new_key" in config     -> False
    """
    pass


# ===========================================================================
# TESTS -- Run this file to verify your solutions
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

    # Should NOT catch TypeError
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
    assert compute_count["n"] == 1  # Not recomputed!

    obj2 = MyClass()
    assert obj2.expensive == 42
    assert compute_count["n"] == 2  # Different instance, computed again
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
    assert compute_count_10["n"] == 1  # Cached!
    assert expensive_add(3, 4) == 7
    assert compute_count_10["n"] == 2
    assert len(expensive_add.cache) == 2
    expensive_add.cache_clear()
    assert len(expensive_add.cache) == 0
    assert expensive_add(1, 2) == 3
    assert compute_count_10["n"] == 3  # Recomputed after cache clear
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
    assert list(r) == values  # Reusable!
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
            username="a",  # Too short
            email="invalid",
            password="short",
            age=10,  # Under 13
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
    assert list(s) == ["Hello", "Hello", "Hello"]  # Reusable
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
