"""
Module 10: Async and Concurrency - Exercises
=============================================

Complete each function so that the corresponding test passes.

To run all exercises:
    pytest exercises.py -v

Prerequisites:
    pip install pytest pytest-asyncio

NOTE: Exercises that use async require pytest-asyncio. The marker
`@pytest.mark.asyncio` is applied automatically via the config below.

Some exercises are synchronous (threading, multiprocessing concepts)
and use standard pytest.
"""

import asyncio
import time
import math
from typing import Any
from unittest.mock import MagicMock, AsyncMock
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import pytest

# Configure pytest-asyncio to auto-detect async tests
pytestmark = pytest.mark.asyncio


# ============================================================================
# WARM-UP EXERCISES (1-4): Basic async functions, await, asyncio.run
# ============================================================================

async def exercise_01_basic_coroutine(name: str) -> str:
    """
    Exercise 01: Basic Coroutine (Warm-up)

    Write an async function that:
    1. Awaits asyncio.sleep(0.01) to simulate a tiny delay
    2. Returns the string f"Hello, {name}!"

    Example:
        result = await exercise_01_basic_coroutine("Alice")
        assert result == "Hello, Alice!"
    """
    pass


async def exercise_02_sequential_await() -> list[int]:
    """
    Exercise 02: Sequential Await (Warm-up)

    Write an async function that:
    1. Calls await _async_double(1) and stores the result
    2. Calls await _async_double(2) and stores the result
    3. Calls await _async_double(3) and stores the result
    4. Returns all three results as a list [2, 4, 6]

    These calls should be sequential (one after another).
    """
    pass


async def exercise_03_concurrent_gather() -> list[int]:
    """
    Exercise 03: Concurrent with gather (Warm-up)

    Write an async function that:
    1. Uses asyncio.gather to run _async_double(1), _async_double(2),
       and _async_double(3) concurrently
    2. Returns the results as a list [2, 4, 6]

    This should be faster than sequential because all three run at the same time.
    """
    pass


async def exercise_04_create_task() -> list[str]:
    """
    Exercise 04: Creating Tasks (Warm-up)

    Write an async function that:
    1. Creates three tasks using asyncio.create_task():
       - _async_greet("Alice")
       - _async_greet("Bob")
       - _async_greet("Charlie")
    2. Awaits all three tasks
    3. Returns the results as a list:
       ["Hello, Alice!", "Hello, Bob!", "Hello, Charlie!"]
    """
    pass


# ============================================================================
# CORE EXERCISES (5-10): Fetch URLs concurrently, async generators, task groups
# ============================================================================

async def exercise_05_concurrent_fetch(urls: list[str]) -> list[dict]:
    """
    Exercise 05: Concurrent URL Fetching (Core)

    Given a list of URLs, fetch them all concurrently using asyncio.gather.
    Use the provided _mock_fetch(url) function to simulate fetching.

    Returns a list of results from _mock_fetch for each URL.

    Example:
        urls = ["https://api.example.com/1", "https://api.example.com/2"]
        results = await exercise_05_concurrent_fetch(urls)
        assert len(results) == 2
        assert results[0]["url"] == "https://api.example.com/1"
    """
    pass


async def exercise_06_async_generator(n: int):
    """
    Exercise 06: Async Generator (Core)

    Write an async generator that yields the squares of numbers from 0 to n-1.
    Include a tiny await asyncio.sleep(0) between yields to make it truly async.

    Example:
        results = []
        async for value in exercise_06_async_generator(4):
            results.append(value)
        assert results == [0, 1, 4, 9]
    """
    pass


async def exercise_07_timeout_handling(delay: float, timeout: float) -> str:
    """
    Exercise 07: Timeout Handling (Core)

    Write an async function that:
    1. Tries to run _slow_operation(delay) with asyncio.wait_for(timeout=timeout)
    2. If it completes in time, returns the result
    3. If it times out, returns "TIMEOUT"

    Example:
        result = await exercise_07_timeout_handling(0.1, 1.0)
        assert result == "completed"
        result = await exercise_07_timeout_handling(2.0, 0.1)
        assert result == "TIMEOUT"
    """
    pass


async def exercise_08_semaphore_limit(
    items: list[str],
    max_concurrent: int,
) -> list[str]:
    """
    Exercise 08: Semaphore for Concurrency Limiting (Core)

    Process a list of items concurrently, but limit the number of
    concurrent operations to max_concurrent using asyncio.Semaphore.

    For each item, call _process_item(item) which returns a processed string.

    Returns a list of processed results (order matches input).

    Example:
        items = ["a", "b", "c", "d", "e"]
        results = await exercise_08_semaphore_limit(items, max_concurrent=2)
        assert results == ["processed: a", "processed: b", ...]
    """
    pass


async def exercise_09_producer_consumer() -> list[str]:
    """
    Exercise 09: Producer-Consumer with asyncio.Queue (Core)

    Implement a producer-consumer pattern:
    1. Create an asyncio.Queue with maxsize=5
    2. The producer puts items "item_0" through "item_4" into the queue
       (use _produce_item(i) for each)
    3. The producer puts None as a sentinel to signal completion
    4. The consumer reads items from the queue until it gets None
    5. The consumer collects each item into a results list
    6. Run producer and consumer concurrently with asyncio.gather
    7. Return the results list

    Example:
        results = await exercise_09_producer_consumer()
        assert results == ["item_0", "item_1", "item_2", "item_3", "item_4"]
    """
    pass


async def exercise_10_error_handling_gather() -> dict[str, Any]:
    """
    Exercise 10: Error Handling with gather (Core)

    Use asyncio.gather with return_exceptions=True to run three tasks:
    1. _async_double(5)       -> should return 10
    2. _async_failing()       -> should raise ValueError("async failure")
    3. _async_double(10)      -> should return 20

    Return a dict with:
    - "successes": list of successful results (ints only)
    - "errors": list of error messages (str(exception) for each error)

    Example:
        result = await exercise_10_error_handling_gather()
        assert result == {"successes": [10, 20], "errors": ["async failure"]}
    """
    pass


# ============================================================================
# CHALLENGE EXERCISES (11-13): Task groups, threading vs multiprocessing
# ============================================================================

async def exercise_11_task_group(user_ids: list[int]) -> list[dict]:
    """
    Exercise 11: TaskGroup (Challenge)

    Use asyncio.TaskGroup (Python 3.11+) to fetch user data for multiple
    user IDs concurrently.

    For each user_id, call _fetch_user(user_id).

    Return a list of user dicts sorted by user ID.

    Example:
        users = await exercise_11_task_group([3, 1, 2])
        assert users == [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"},
            {"id": 3, "name": "User 3"},
        ]

    Note: TaskGroup requires Python 3.11+. If running an older version,
    fall back to asyncio.gather.
    """
    pass


def exercise_12_thread_pool(numbers: list[int]) -> list[bool]:
    """
    Exercise 12: ThreadPoolExecutor (Challenge)

    Use concurrent.futures.ThreadPoolExecutor to check if numbers are prime
    concurrently.

    For each number, call _is_prime(n) which returns True/False.
    Use executor.map to apply _is_prime to all numbers.

    Returns a list of booleans in the same order as the input.

    NOTE: This is a synchronous function (not async). It uses threads.

    Example:
        results = exercise_12_thread_pool([2, 3, 4, 5, 6])
        assert results == [True, True, False, True, False]
    """
    pass


def exercise_13_compare_sequential_vs_concurrent(n: int) -> dict[str, float]:
    """
    Exercise 13: Compare Sequential vs Concurrent (Challenge)

    Run _cpu_light_work(i) for i in range(n) both sequentially and with
    ThreadPoolExecutor, measuring the time for each.

    Return a dict with:
    - "sequential_time": time in seconds for sequential execution
    - "concurrent_time": time in seconds for ThreadPoolExecutor execution
    - "speedup": sequential_time / concurrent_time

    Use time.perf_counter() for timing.

    NOTE: This is a synchronous function. The concurrent version uses threads.

    Example:
        result = exercise_13_compare_sequential_vs_concurrent(10)
        assert "sequential_time" in result
        assert "concurrent_time" in result
        assert "speedup" in result
        assert result["speedup"] > 0
    """
    pass


# ============================================================================
# SWIFT BRIDGE EXERCISES (14-15)
# ============================================================================

async def exercise_14_swift_task_equivalent() -> dict[str, Any]:
    """
    Exercise 14: Swift Task Equivalent (Swift Bridge)

    In Swift, you might write:
        Task {
            let user = await fetchUser(1)
            let posts = await fetchPosts(1)
            return (user, posts)
        }

    Or for concurrent execution:
        async let user = fetchUser(1)
        async let posts = fetchPosts(1)
        return await (user, posts)

    Translate the CONCURRENT version to Python:
    1. Use asyncio.create_task or asyncio.gather to run
       _fetch_user(1) and _fetch_posts(1) concurrently
    2. Return a dict: {"user": user_result, "posts": posts_result}

    Example:
        result = await exercise_14_swift_task_equivalent()
        assert result["user"] == {"id": 1, "name": "User 1"}
        assert result["posts"] == [{"user_id": 1, "title": "Post by User 1"}]
    """
    pass


async def exercise_15_async_context_manager():
    """
    Exercise 15: Async Context Manager (Swift Bridge)

    In Swift, resource management often uses defer:
        func withConnection() async throws -> Data {
            let conn = try await connect()
            defer { conn.close() }
            return try await conn.fetch()
        }

    In Python, we use async context managers.

    Use the provided AsyncResource class (defined below) as an async
    context manager:
    1. Enter the context with `async with AsyncResource("test-resource") as resource:`
    2. Call await resource.do_work() and store the result
    3. The context manager handles cleanup automatically
    4. Return the result from do_work()

    Example:
        result = await exercise_15_async_context_manager()
        assert result == "work done with test-resource"
    """
    pass


# ============================================================================
# HELPER FUNCTIONS AND CLASSES (used by exercises above)
# ============================================================================

async def _async_double(n: int) -> int:
    """Async function that doubles a number after a tiny delay."""
    await asyncio.sleep(0.01)
    return n * 2


async def _async_greet(name: str) -> str:
    """Async function that returns a greeting after a tiny delay."""
    await asyncio.sleep(0.01)
    return f"Hello, {name}!"


async def _mock_fetch(url: str) -> dict:
    """Simulate fetching a URL. Returns a dict with url and status."""
    await asyncio.sleep(0.01)
    return {"url": url, "status": 200, "data": f"Response from {url}"}


async def _slow_operation(delay: float) -> str:
    """An operation that takes `delay` seconds."""
    await asyncio.sleep(delay)
    return "completed"


async def _process_item(item: str) -> str:
    """Process an item with a small delay."""
    await asyncio.sleep(0.01)
    return f"processed: {item}"


async def _produce_item(index: int) -> str:
    """Produce an item with a small delay."""
    await asyncio.sleep(0.01)
    return f"item_{index}"


async def _async_failing() -> int:
    """An async function that always fails."""
    await asyncio.sleep(0.01)
    raise ValueError("async failure")


async def _fetch_user(user_id: int) -> dict:
    """Fetch a user by ID (simulated)."""
    await asyncio.sleep(0.01)
    return {"id": user_id, "name": f"User {user_id}"}


async def _fetch_posts(user_id: int) -> list[dict]:
    """Fetch posts for a user (simulated)."""
    await asyncio.sleep(0.01)
    return [{"user_id": user_id, "title": f"Post by User {user_id}"}]


def _is_prime(n: int) -> bool:
    """Check if a number is prime (CPU-bound, for threading exercise)."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def _cpu_light_work(n: int) -> int:
    """Light CPU work with a small sleep to simulate I/O."""
    time.sleep(0.05)  # Simulate I/O delay
    return n * n


class AsyncResource:
    """An async context manager for resource management exercises."""

    def __init__(self, name: str):
        self.name = name
        self.is_open = False

    async def __aenter__(self):
        await asyncio.sleep(0.01)
        self.is_open = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(0.01)
        self.is_open = False
        return False

    async def do_work(self) -> str:
        if not self.is_open:
            raise RuntimeError("Resource is not open")
        await asyncio.sleep(0.01)
        return f"work done with {self.name}"


# ============================================================================
# TESTS (verify your implementations)
# ============================================================================

class TestWarmUp:
    """Tests for warm-up exercises."""

    async def test_exercise_01(self):
        result = await exercise_01_basic_coroutine("Alice")
        assert result == "Hello, Alice!"
        result2 = await exercise_01_basic_coroutine("World")
        assert result2 == "Hello, World!"

    async def test_exercise_02(self):
        result = await exercise_02_sequential_await()
        assert result == [2, 4, 6]

    async def test_exercise_03(self):
        start = time.perf_counter()
        result = await exercise_03_concurrent_gather()
        elapsed = time.perf_counter() - start
        assert result == [2, 4, 6]
        # Should be close to 0.01s (concurrent), not 0.03s (sequential)
        # Use generous bound for CI
        assert elapsed < 0.5

    async def test_exercise_04(self):
        result = await exercise_04_create_task()
        assert result == ["Hello, Alice!", "Hello, Bob!", "Hello, Charlie!"]


class TestCore:
    """Tests for core exercises."""

    async def test_exercise_05(self):
        urls = [
            "https://api.example.com/1",
            "https://api.example.com/2",
            "https://api.example.com/3",
        ]
        results = await exercise_05_concurrent_fetch(urls)
        assert len(results) == 3
        assert all(r["status"] == 200 for r in results)
        assert results[0]["url"] == "https://api.example.com/1"

    async def test_exercise_06(self):
        results = []
        async for value in exercise_06_async_generator(5):
            results.append(value)
        assert results == [0, 1, 4, 9, 16]

    async def test_exercise_07_success(self):
        result = await exercise_07_timeout_handling(0.01, 1.0)
        assert result == "completed"

    async def test_exercise_07_timeout(self):
        result = await exercise_07_timeout_handling(2.0, 0.05)
        assert result == "TIMEOUT"

    async def test_exercise_08(self):
        items = ["a", "b", "c", "d", "e"]
        results = await exercise_08_semaphore_limit(items, max_concurrent=2)
        assert results == [
            "processed: a",
            "processed: b",
            "processed: c",
            "processed: d",
            "processed: e",
        ]

    async def test_exercise_09(self):
        results = await exercise_09_producer_consumer()
        assert results == ["item_0", "item_1", "item_2", "item_3", "item_4"]

    async def test_exercise_10(self):
        result = await exercise_10_error_handling_gather()
        assert sorted(result["successes"]) == [10, 20]
        assert result["errors"] == ["async failure"]


class TestChallenge:
    """Tests for challenge exercises."""

    async def test_exercise_11(self):
        users = await exercise_11_task_group([3, 1, 2])
        assert users == [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"},
            {"id": 3, "name": "User 3"},
        ]

    def test_exercise_12(self):
        results = exercise_12_thread_pool([2, 3, 4, 5, 6, 7, 8, 9, 10])
        assert results == [True, True, False, True, False, True, False, False, False]

    def test_exercise_13(self):
        result = exercise_13_compare_sequential_vs_concurrent(8)
        assert "sequential_time" in result
        assert "concurrent_time" in result
        assert "speedup" in result
        assert result["sequential_time"] > 0
        assert result["concurrent_time"] > 0
        assert result["speedup"] > 0


class TestSwiftBridge:
    """Tests for Swift bridge exercises."""

    async def test_exercise_14(self):
        result = await exercise_14_swift_task_equivalent()
        assert result["user"] == {"id": 1, "name": "User 1"}
        assert result["posts"] == [{"user_id": 1, "title": "Post by User 1"}]

    async def test_exercise_15(self):
        result = await exercise_15_async_context_manager()
        assert result == "work done with test-resource"
