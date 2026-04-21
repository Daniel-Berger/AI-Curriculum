"""
Module 04: Functions and Closures - Solutions
=============================================

Complete solutions for all 15 exercises. Where applicable, Pythonic
alternatives are noted in comments.
"""

from typing import Callable, Any
from functools import reduce


# ---------------------------------------------------------------------------
# WARM-UP
# ---------------------------------------------------------------------------

def exercise_1_greeting(name: str, greeting: str = "Hello") -> str:
    """Return a greeting string in the format '{greeting}, {name}!'."""
    return f"{greeting}, {name}!"


def exercise_2_sum_all(*args: float) -> float:
    """Return the sum of all positional arguments."""
    return float(sum(args))

    # Alternative: manual accumulation
    # total = 0.0
    # for n in args:
    #     total += n
    # return total


def exercise_3_build_url(base: str, *path_parts: str, **query_params: str) -> str:
    """Build a URL from a base, path parts, and query parameters."""
    url = base
    if path_parts:
        url += "/" + "/".join(path_parts)
    if query_params:
        sorted_params = sorted(query_params.items())
        query_string = "&".join(f"{k}={v}" for k, v in sorted_params)
        url += "?" + query_string
    return url

    # Alternative using urllib.parse (more robust for production code):
    # from urllib.parse import urlencode, urljoin
    # path = "/".join(path_parts)
    # query = urlencode(sorted(query_params.items()))
    # return f"{base}/{path}{'?' + query if query else ''}"


def exercise_4_safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dictionaries using the provided keys."""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

    # Alternative: using try/except (EAFP style, more Pythonic)
    # current = data
    # try:
    #     for key in keys:
    #         current = current[key]
    #     return current
    # except (KeyError, TypeError):
    #     return default


# ---------------------------------------------------------------------------
# CORE
# ---------------------------------------------------------------------------

def exercise_5_transform_names(names: list[str]) -> list[str]:
    """Transform names: strip, title case, filter short names. Use map/filter."""
    stripped = map(lambda n: n.strip(), names)
    titled = map(lambda n: n.title(), stripped)
    filtered = filter(lambda n: len(n) >= 2, titled)
    return list(filtered)

    # Pythonic alternative (list comprehension):
    # return [n.strip().title() for n in names if len(n.strip()) >= 2]


def exercise_6_make_multiplier(factor: float) -> Callable[[float], float]:
    """Return a closure that multiplies its argument by `factor`."""
    def multiplier(x: float) -> float:
        return x * factor
    return multiplier

    # Alternative: using lambda
    # return lambda x: x * factor


def exercise_7_make_counter(start: int = 0) -> dict[str, Callable]:
    """Return a dict with increment, decrement, and get closures."""
    count = start

    def increment() -> int:
        nonlocal count
        count += 1
        return count

    def decrement() -> int:
        nonlocal count
        count -= 1
        return count

    def get() -> int:
        return count

    return {"increment": increment, "decrement": decrement, "get": get}


def exercise_8_apply_pipeline(
    value: Any,
    *functions: Callable[[Any], Any],
) -> Any:
    """Apply a series of functions to a value from left to right."""
    result = value
    for func in functions:
        result = func(result)
    return result

    # Alternative: using functools.reduce
    # return reduce(lambda v, f: f(v), functions, value)


def exercise_9_memoized_fibonacci() -> Callable[[int], int]:
    """Return a memoized Fibonacci function using a closure with a dict cache."""
    cache: dict[int, int] = {0: 0, 1: 1}

    def fib(n: int) -> int:
        if n not in cache:
            cache[n] = fib(n - 1) + fib(n - 2)
        return cache[n]

    return fib


def exercise_10_compose(*functions: Callable) -> Callable:
    """Compose multiple functions right to left using functools.reduce."""
    if not functions:
        return lambda x: x
    if len(functions) == 1:
        return functions[0]
    return reduce(lambda f, g: lambda x: f(g(x)), functions)

    # Alternative without reduce:
    # def composed(x):
    #     result = x
    #     for func in reversed(functions):
    #         result = func(result)
    #     return result
    # return composed


# ---------------------------------------------------------------------------
# CHALLENGE
# ---------------------------------------------------------------------------

def exercise_11_retry(
    func: Callable[[], Any],
    max_attempts: int = 3,
) -> Any:
    """Call func() up to max_attempts times until it succeeds."""
    last_exception: Exception | None = None
    for _ in range(max_attempts):
        try:
            return func()
        except Exception as e:
            last_exception = e
    raise last_exception  # type: ignore[misc]

    # Alternative: re-raise on the last attempt explicitly
    # for attempt in range(max_attempts):
    #     try:
    #         return func()
    #     except Exception:
    #         if attempt == max_attempts - 1:
    #             raise


def exercise_12_make_validator(
    *predicates: Callable[[Any], bool],
) -> Callable[[Any], bool]:
    """Return a function that validates a value against ALL predicates."""
    def validate(value: Any) -> bool:
        return all(pred(value) for pred in predicates)
    return validate

    # Alternative: using lambda
    # return lambda value: all(pred(value) for pred in predicates)


def exercise_13_once(func: Callable[..., Any]) -> Callable[..., Any]:
    """Return a wrapper that only calls func on the first invocation."""
    result: list = []  # Using a list to store result since we need mutability
    called = False

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal called
        if not called:
            result.append(func(*args, **kwargs))
            called = True
        return result[0]

    return wrapper

    # Alternative: using a mutable container without nonlocal
    # state = {"called": False, "result": None}
    # def wrapper(*args, **kwargs):
    #     if not state["called"]:
    #         state["result"] = func(*args, **kwargs)
    #         state["called"] = True
    #     return state["result"]
    # return wrapper


# ---------------------------------------------------------------------------
# SWIFT BRIDGE
# ---------------------------------------------------------------------------

def exercise_14_sorted_with_key(
    items: list[dict[str, Any]],
    key: str,
    reverse: bool = False,
) -> list[dict[str, Any]]:
    """Sort a list of dictionaries by a given key."""
    return sorted(items, key=lambda item: item[key], reverse=reverse)

    # Alternative: using operator.itemgetter (slightly faster)
    # from operator import itemgetter
    # return sorted(items, key=itemgetter(key), reverse=reverse)


def exercise_15_compact_map(
    items: list[Any],
    transform: Callable[[Any], Any | None],
) -> list[Any]:
    """Apply transform and filter out None results (like Swift's compactMap)."""
    return [result for item in items if (result := transform(item)) is not None]

    # Alternative without walrus operator (:=):
    # results = []
    # for item in items:
    #     result = transform(item)
    #     if result is not None:
    #         results.append(result)
    # return results

    # Alternative using filter + map:
    # mapped = map(transform, items)
    # return list(filter(lambda x: x is not None, mapped))


# ===========================================================================
# TESTS
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
    assert exercise_8_apply_pipeline(42) == 42
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
    assert exercise_12_make_validator()(42) is True
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
