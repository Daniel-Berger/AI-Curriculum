"""
Module 04: Functions and Closures - Exercises
============================================

15 exercises covering function definitions, closures, higher-order functions,
and functional programming patterns in Python.

Target audience: Swift/iOS developers learning Python.

Instructions:
    - Replace `pass` (or `...`) with your implementation.
    - Run this file to check your answers with the assert-based tests at the bottom.
    - Each function has a docstring explaining the expected behavior.
    - Type hints are provided in the signatures -- follow them.
"""

from typing import Callable, Any
from functools import reduce


# ---------------------------------------------------------------------------
# WARM-UP: Basic functions, default args, *args / **kwargs
# ---------------------------------------------------------------------------

def exercise_1_greeting(name: str, greeting: str = "Hello") -> str:
    """Return a greeting string in the format '{greeting}, {name}!'.

    If no greeting is provided, default to 'Hello'.

    Examples:
        exercise_1_greeting("Alice")          -> "Hello, Alice!"
        exercise_1_greeting("Bob", "Hey")     -> "Hey, Bob!"
    """
    pass


def exercise_2_sum_all(*args: float) -> float:
    """Return the sum of all positional arguments.

    If no arguments are provided, return 0.0.

    Examples:
        exercise_2_sum_all(1, 2, 3)       -> 6.0
        exercise_2_sum_all(1.5, 2.5)      -> 4.0
        exercise_2_sum_all()              -> 0.0
    """
    pass


def exercise_3_build_url(base: str, *path_parts: str, **query_params: str) -> str:
    """Build a URL from a base, path parts, and query parameters.

    - Join path parts with '/'
    - Append query parameters as '?key1=val1&key2=val2' (sorted by key)
    - If no query params, no '?' should appear

    Examples:
        exercise_3_build_url("https://api.com", "users", "42")
            -> "https://api.com/users/42"
        exercise_3_build_url("https://api.com", "search", q="python", page="1")
            -> "https://api.com/search?page=1&q=python"
    """
    pass


def exercise_4_safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dictionaries using the provided keys.

    Navigate through nested dicts following each key in sequence.
    If any key is missing, return the default value.

    Examples:
        d = {"a": {"b": {"c": 42}}}
        exercise_4_safe_get(d, "a", "b", "c")           -> 42
        exercise_4_safe_get(d, "a", "x", default=-1)    -> -1
        exercise_4_safe_get(d, "a", "b")                 -> {"c": 42}
    """
    pass


# ---------------------------------------------------------------------------
# CORE: Lambda with map/filter, closures, higher-order functions, lru_cache
# ---------------------------------------------------------------------------

def exercise_5_transform_names(names: list[str]) -> list[str]:
    """Transform a list of names: strip whitespace, convert to title case,
    and filter out any names shorter than 2 characters (after stripping).

    Use map() and filter() with lambda functions (not list comprehensions).

    Examples:
        exercise_5_transform_names(["  alice ", "BOB", " a ", "charlie"])
            -> ["Alice", "Bob", "Charlie"]
    """
    pass


def exercise_6_make_multiplier(factor: float) -> Callable[[float], float]:
    """Return a closure that multiplies its argument by `factor`.

    Examples:
        double = exercise_6_make_multiplier(2)
        double(5)    -> 10.0
        double(3.5)  -> 7.0

        triple = exercise_6_make_multiplier(3)
        triple(4)    -> 12.0
    """
    pass


def exercise_7_make_counter(start: int = 0) -> dict[str, Callable]:
    """Return a dictionary with three closure functions that share state:
        - "increment": increments the counter by 1 and returns the new value
        - "decrement": decrements the counter by 1 and returns the new value
        - "get": returns the current counter value

    Examples:
        c = exercise_7_make_counter(10)
        c["increment"]()  -> 11
        c["increment"]()  -> 12
        c["decrement"]()  -> 11
        c["get"]()        -> 11
    """
    pass


def exercise_8_apply_pipeline(
    value: Any,
    *functions: Callable[[Any], Any],
) -> Any:
    """Apply a series of functions to a value from left to right (pipeline).

    Examples:
        exercise_8_apply_pipeline(
            "  hello world  ",
            str.strip,
            str.upper,
            lambda s: s.replace(" ", "_"),
        )
        -> "HELLO_WORLD"

        exercise_8_apply_pipeline(5, lambda x: x + 1, lambda x: x * 2)
        -> 12
    """
    pass


def exercise_9_memoized_fibonacci() -> Callable[[int], int]:
    """Return a memoized Fibonacci function using a closure (manual memoization).

    Do NOT use functools.lru_cache for this exercise -- build the cache yourself
    using a dictionary inside the closure.

    The returned function should compute fib(0)=0, fib(1)=1,
    fib(n)=fib(n-1)+fib(n-2) for n>=2.

    Examples:
        fib = exercise_9_memoized_fibonacci()
        fib(0)   -> 0
        fib(1)   -> 1
        fib(10)  -> 55
        fib(50)  -> 12586269025
    """
    pass


def exercise_10_compose(
    *functions: Callable,
) -> Callable:
    """Compose multiple functions right to left.

    compose(f, g, h)(x) should equal f(g(h(x))).
    If no functions are provided, return the identity function.
    If one function is provided, return it directly.

    Use functools.reduce to implement this.

    Examples:
        inc = lambda x: x + 1
        dbl = lambda x: x * 2
        sqr = lambda x: x ** 2

        compose(inc, dbl)(3)       -> 7   # inc(dbl(3)) = inc(6) = 7
        compose(dbl, inc)(3)       -> 8   # dbl(inc(3)) = dbl(4) = 8
        compose(inc, dbl, sqr)(3)  -> 19  # inc(dbl(sqr(3))) = inc(dbl(9)) = inc(18) = 19
    """
    pass


# ---------------------------------------------------------------------------
# CHALLENGE: Decorator-like patterns, function composition
# ---------------------------------------------------------------------------

def exercise_11_retry(
    func: Callable[[], Any],
    max_attempts: int = 3,
) -> Any:
    """Call func() up to max_attempts times until it succeeds (returns without
    raising an exception). Return the result of the first successful call.

    If all attempts fail, raise the last exception.

    Examples:
        counter = {"n": 0}
        def flaky():
            counter["n"] += 1
            if counter["n"] < 3:
                raise ValueError("not yet")
            return "success"

        exercise_11_retry(flaky, max_attempts=5)  -> "success"
    """
    pass


def exercise_12_make_validator(
    *predicates: Callable[[Any], bool],
) -> Callable[[Any], bool]:
    """Return a function that validates a value against ALL predicates.

    The returned function should return True only if every predicate
    returns True for the given value.

    Examples:
        is_positive = lambda x: x > 0
        is_even = lambda x: x % 2 == 0
        is_small = lambda x: x < 100

        check = exercise_12_make_validator(is_positive, is_even, is_small)
        check(4)    -> True
        check(-2)   -> False  (not positive)
        check(3)    -> False  (not even)
        check(200)  -> False  (not small)
    """
    pass


def exercise_13_once(func: Callable[..., Any]) -> Callable[..., Any]:
    """Return a wrapper that only calls func on the first invocation.

    Subsequent calls should return the result of the first call without
    re-executing func.

    Examples:
        call_count = 0
        def expensive():
            nonlocal call_count
            call_count += 1
            return 42

        wrapped = exercise_13_once(expensive)
        wrapped()  -> 42  (call_count is now 1)
        wrapped()  -> 42  (call_count is still 1)
        wrapped()  -> 42  (call_count is still 1)
    """
    pass


# ---------------------------------------------------------------------------
# SWIFT BRIDGE: Convert Swift closure / higher-order function patterns
# ---------------------------------------------------------------------------

def exercise_14_sorted_with_key(
    items: list[dict[str, Any]],
    key: str,
    reverse: bool = False,
) -> list[dict[str, Any]]:
    """Sort a list of dictionaries by a given key.

    This mirrors Swift's .sorted(by:) with a key path.

    In Swift you might write:
        users.sorted(by: { $0.age < $1.age })

    In Python, use sorted() with a key function.

    Examples:
        users = [
            {"name": "Charlie", "age": 35},
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        exercise_14_sorted_with_key(users, "age")
            -> [{"name": "Bob", ...}, {"name": "Alice", ...}, {"name": "Charlie", ...}]
        exercise_14_sorted_with_key(users, "name", reverse=True)
            -> [{"name": "Charlie", ...}, {"name": "Bob", ...}, {"name": "Alice", ...}]
    """
    pass


def exercise_15_compact_map(
    items: list[Any],
    transform: Callable[[Any], Any | None],
) -> list[Any]:
    """Apply a transform to each item and filter out None results.

    This mirrors Swift's compactMap(_:).

    In Swift:
        let numbers = ["1", "two", "3", "four", "5"]
        let parsed = numbers.compactMap { Int($0) }  // [1, 3, 5]

    Examples:
        def try_int(s: str) -> int | None:
            try:
                return int(s)
            except ValueError:
                return None

        exercise_15_compact_map(["1", "two", "3"], try_int)  -> [1, 3]
    """
    pass


# ===========================================================================
# TESTS -- Run this file to verify your solutions
# ===========================================================================

if __name__ == "__main__":
    # --- Exercise 1 ---
    assert exercise_1_greeting("Alice") == "Hello, Alice!"
    assert exercise_1_greeting("Bob", "Hey") == "Hey, Bob!"
    assert exercise_1_greeting("World", greeting="Greetings") == "Greetings, World!"
    print("Exercise 1 passed!")

    # --- Exercise 2 ---
    assert exercise_2_sum_all(1, 2, 3) == 6.0
    assert exercise_2_sum_all(1.5, 2.5) == 4.0
    assert exercise_2_sum_all() == 0.0
    assert exercise_2_sum_all(10) == 10.0
    print("Exercise 2 passed!")

    # --- Exercise 3 ---
    assert exercise_3_build_url("https://api.com", "users", "42") == "https://api.com/users/42"
    assert exercise_3_build_url("https://api.com", "search", q="python", page="1") == \
        "https://api.com/search?page=1&q=python"
    assert exercise_3_build_url("https://api.com") == "https://api.com"
    print("Exercise 3 passed!")

    # --- Exercise 4 ---
    nested = {"a": {"b": {"c": 42}}}
    assert exercise_4_safe_get(nested, "a", "b", "c") == 42
    assert exercise_4_safe_get(nested, "a", "x", default=-1) == -1
    assert exercise_4_safe_get(nested, "a", "b") == {"c": 42}
    assert exercise_4_safe_get(nested, "z") is None
    print("Exercise 4 passed!")

    # --- Exercise 5 ---
    assert exercise_5_transform_names(["  alice ", "BOB", " a ", "charlie"]) == \
        ["Alice", "Bob", "Charlie"]
    assert exercise_5_transform_names([]) == []
    assert exercise_5_transform_names(["  X  "]) == []
    print("Exercise 5 passed!")

    # --- Exercise 6 ---
    double = exercise_6_make_multiplier(2)
    assert double(5) == 10.0
    assert double(3.5) == 7.0
    triple = exercise_6_make_multiplier(3)
    assert triple(4) == 12.0
    print("Exercise 6 passed!")

    # --- Exercise 7 ---
    c = exercise_7_make_counter(10)
    assert c["increment"]() == 11
    assert c["increment"]() == 12
    assert c["decrement"]() == 11
    assert c["get"]() == 11
    print("Exercise 7 passed!")

    # --- Exercise 8 ---
    assert exercise_8_apply_pipeline(
        "  hello world  ",
        str.strip,
        str.upper,
        lambda s: s.replace(" ", "_"),
    ) == "HELLO_WORLD"
    assert exercise_8_apply_pipeline(5, lambda x: x + 1, lambda x: x * 2) == 12
    assert exercise_8_apply_pipeline(42) == 42  # no functions = identity
    print("Exercise 8 passed!")

    # --- Exercise 9 ---
    fib = exercise_9_memoized_fibonacci()
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(10) == 55
    assert fib(50) == 12586269025
    print("Exercise 9 passed!")

    # --- Exercise 10 ---
    inc = lambda x: x + 1
    dbl = lambda x: x * 2
    sqr = lambda x: x ** 2
    assert exercise_10_compose(inc, dbl)(3) == 7
    assert exercise_10_compose(dbl, inc)(3) == 8
    assert exercise_10_compose(inc, dbl, sqr)(3) == 19
    identity = exercise_10_compose()
    assert identity(99) == 99
    print("Exercise 10 passed!")

    # --- Exercise 11 ---
    attempt_counter = {"n": 0}
    def flaky():
        attempt_counter["n"] += 1
        if attempt_counter["n"] < 3:
            raise ValueError("not yet")
        return "success"

    assert exercise_11_retry(flaky, max_attempts=5) == "success"
    assert attempt_counter["n"] == 3

    attempt_counter2 = {"n": 0}
    def always_fails():
        attempt_counter2["n"] += 1
        raise RuntimeError("boom")

    try:
        exercise_11_retry(always_fails, max_attempts=3)
        assert False, "Should have raised"
    except RuntimeError as e:
        assert str(e) == "boom"
        assert attempt_counter2["n"] == 3
    print("Exercise 11 passed!")

    # --- Exercise 12 ---
    is_positive = lambda x: x > 0
    is_even = lambda x: x % 2 == 0
    is_small = lambda x: x < 100
    check = exercise_12_make_validator(is_positive, is_even, is_small)
    assert check(4) is True
    assert check(-2) is False
    assert check(3) is False
    assert check(200) is False
    assert exercise_12_make_validator()(42) is True  # no predicates = always True
    print("Exercise 12 passed!")

    # --- Exercise 13 ---
    call_count_13 = {"n": 0}
    def expensive():
        call_count_13["n"] += 1
        return 42

    wrapped = exercise_13_once(expensive)
    assert wrapped() == 42
    assert call_count_13["n"] == 1
    assert wrapped() == 42
    assert call_count_13["n"] == 1
    assert wrapped() == 42
    assert call_count_13["n"] == 1
    print("Exercise 13 passed!")

    # --- Exercise 14 ---
    users = [
        {"name": "Charlie", "age": 35},
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]
    sorted_by_age = exercise_14_sorted_with_key(users, "age")
    assert [u["name"] for u in sorted_by_age] == ["Bob", "Alice", "Charlie"]
    sorted_by_name_desc = exercise_14_sorted_with_key(users, "name", reverse=True)
    assert [u["name"] for u in sorted_by_name_desc] == ["Charlie", "Bob", "Alice"]
    print("Exercise 14 passed!")

    # --- Exercise 15 ---
    def try_int(s: str) -> int | None:
        try:
            return int(s)
        except ValueError:
            return None

    assert exercise_15_compact_map(["1", "two", "3", "four", "5"], try_int) == [1, 3, 5]
    assert exercise_15_compact_map([], try_int) == []
    assert exercise_15_compact_map(["a", "b"], try_int) == []
    print("Exercise 15 passed!")

    print("\n All exercises passed!")
