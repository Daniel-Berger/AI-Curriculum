"""
Module 10: Async and Concurrency - Solutions
=============================================

Complete solutions for all exercises.
Run with: pytest solutions.py -v

Prerequisites:
    pip install pytest pytest-asyncio

All 15+ tests should pass.
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
# WARM-UP EXERCISES (1-4)
# ============================================================================

async def exercise_01_basic_coroutine(name: str) -> str:
    """
    Exercise 01: Basic Coroutine

    Note: The simplest possible async function. We await asyncio.sleep(0.01)
    to make it truly asynchronous, then return a greeting string.
    """
    await asyncio.sleep(0.01)
    return f"Hello, {name}!"


async def exercise_02_sequential_await() -> list[int]:
    """
    Exercise 02: Sequential Await

    Note: Each await completes before the next begins. Total time is the
    sum of all delays (~0.03s). This is the simplest but slowest approach.
    """
    r1 = await _async_double(1)
    r2 = await _async_double(2)
    r3 = await _async_double(3)
    return [r1, r2, r3]


async def exercise_03_concurrent_gather() -> list[int]:
    """
    Exercise 03: Concurrent with gather

    Note: asyncio.gather runs all three coroutines concurrently. Total time
    is the maximum delay (~0.01s), not the sum. gather returns results in
    the same order as the input coroutines.
    """
    results = await asyncio.gather(
        _async_double(1),
        _async_double(2),
        _async_double(3),
    )
    return list(results)


async def exercise_04_create_task() -> list[str]:
    """
    Exercise 04: Creating Tasks

    Note: create_task schedules the coroutine for execution. The task starts
    running immediately (at the next event loop iteration). We then await
    each task to get the result. This is equivalent to Swift's Task { }.
    """
    task1 = asyncio.create_task(_async_greet("Alice"))
    task2 = asyncio.create_task(_async_greet("Bob"))
    task3 = asyncio.create_task(_async_greet("Charlie"))

    r1 = await task1
    r2 = await task2
    r3 = await task3
    return [r1, r2, r3]


# ============================================================================
# CORE EXERCISES (5-10)
# ============================================================================

async def exercise_05_concurrent_fetch(urls: list[str]) -> list[dict]:
    """
    Exercise 05: Concurrent URL Fetching

    Note: We create a coroutine for each URL and gather them all. This is
    the most common asyncio pattern for concurrent I/O. The results preserve
    input order thanks to asyncio.gather's guarantee.
    """
    results = await asyncio.gather(*[_mock_fetch(url) for url in urls])
    return list(results)


async def exercise_06_async_generator(n: int):
    """
    Exercise 06: Async Generator

    Note: An async generator uses 'yield' just like a regular generator,
    but can also 'await' async operations. The caller uses 'async for'
    to iterate over values.
    """
    for i in range(n):
        await asyncio.sleep(0)
        yield i * i


async def exercise_07_timeout_handling(delay: float, timeout: float) -> str:
    """
    Exercise 07: Timeout Handling

    Note: asyncio.wait_for wraps a coroutine with a timeout. If the coroutine
    does not complete within the timeout, asyncio.TimeoutError is raised.
    This is similar to Swift's withTimeout or Task cancellation.
    """
    try:
        result = await asyncio.wait_for(_slow_operation(delay), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        return "TIMEOUT"


async def exercise_08_semaphore_limit(
    items: list[str],
    max_concurrent: int,
) -> list[str]:
    """
    Exercise 08: Semaphore for Concurrency Limiting

    Note: A Semaphore limits how many coroutines can enter a section
    simultaneously. This prevents overwhelming external services. We wrap
    each item's processing in a semaphore-guarded coroutine, then gather
    all of them. gather preserves order even though execution is concurrent.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_limit(item: str) -> str:
        async with semaphore:
            return await _process_item(item)

    results = await asyncio.gather(*[process_with_limit(item) for item in items])
    return list(results)


async def exercise_09_producer_consumer() -> list[str]:
    """
    Exercise 09: Producer-Consumer with asyncio.Queue

    Note: The producer and consumer run concurrently via gather. The queue
    provides backpressure (maxsize=5 means the producer blocks if the queue
    is full). The None sentinel signals the consumer to stop. task_done()
    is called for proper queue joining if needed.
    """
    queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=5)
    results: list[str] = []

    async def producer():
        for i in range(5):
            item = await _produce_item(i)
            await queue.put(item)
        await queue.put(None)  # Sentinel

    async def consumer():
        while True:
            item = await queue.get()
            if item is None:
                break
            results.append(item)
            queue.task_done()

    await asyncio.gather(producer(), consumer())
    return results


async def exercise_10_error_handling_gather() -> dict[str, Any]:
    """
    Exercise 10: Error Handling with gather

    Note: return_exceptions=True causes gather to return exceptions as
    values instead of raising them. We then separate successes from errors
    by checking isinstance. This pattern is common when you want to process
    as many results as possible even if some fail.
    """
    results = await asyncio.gather(
        _async_double(5),
        _async_failing(),
        _async_double(10),
        return_exceptions=True,
    )

    successes = []
    errors = []
    for result in results:
        if isinstance(result, Exception):
            errors.append(str(result))
        else:
            successes.append(result)

    return {"successes": successes, "errors": errors}


# ============================================================================
# CHALLENGE EXERCISES (11-13)
# ============================================================================

async def exercise_11_task_group(user_ids: list[int]) -> list[dict]:
    """
    Exercise 11: TaskGroup

    Note: TaskGroup (Python 3.11+) provides structured concurrency. All tasks
    within the group are guaranteed to complete (or be cancelled) before the
    async with block exits. We collect results from each task after the group
    completes and sort by user ID.
    """
    tasks: list[asyncio.Task] = []

    async with asyncio.TaskGroup() as tg:
        for uid in user_ids:
            task = tg.create_task(_fetch_user(uid))
            tasks.append(task)

    # Note: All tasks are complete here
    users = [task.result() for task in tasks]
    users.sort(key=lambda u: u["id"])
    return users


def exercise_12_thread_pool(numbers: list[int]) -> list[bool]:
    """
    Exercise 12: ThreadPoolExecutor

    Note: ThreadPoolExecutor.map applies a function to each item using
    a pool of threads. For I/O-bound or GIL-releasing work, this provides
    real speedup. For pure Python CPU-bound work, the GIL limits benefit.
    executor.map returns results in input order.
    """
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(_is_prime, numbers))
    return results


def exercise_13_compare_sequential_vs_concurrent(n: int) -> dict[str, float]:
    """
    Exercise 13: Compare Sequential vs Concurrent

    Note: Since _cpu_light_work includes a sleep (simulating I/O), threads
    can overlap the waits. The speedup demonstrates that threading helps
    with I/O-bound tasks despite the GIL. For pure CPU-bound work without
    sleep, the speedup would be negligible or even negative.
    """
    # Sequential
    start = time.perf_counter()
    for i in range(n):
        _cpu_light_work(i)
    sequential_time = time.perf_counter() - start

    # Concurrent with threads
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n) as executor:
        list(executor.map(_cpu_light_work, range(n)))
    concurrent_time = time.perf_counter() - start

    return {
        "sequential_time": sequential_time,
        "concurrent_time": concurrent_time,
        "speedup": sequential_time / concurrent_time if concurrent_time > 0 else 0,
    }


# ============================================================================
# SWIFT BRIDGE EXERCISES (14-15)
# ============================================================================

async def exercise_14_swift_task_equivalent() -> dict[str, Any]:
    """
    Exercise 14: Swift Task Equivalent

    Note: Python's asyncio.gather is the closest equivalent to Swift's
    async let for concurrent execution. Both start the work immediately
    and await the results together. The key difference is that Swift's
    async let is a language feature while Python uses a library function.
    """
    user, posts = await asyncio.gather(
        _fetch_user(1),
        _fetch_posts(1),
    )
    return {"user": user, "posts": posts}


async def exercise_15_async_context_manager():
    """
    Exercise 15: Async Context Manager

    Note: Python's 'async with' is the equivalent of Swift's defer pattern
    for async resource management. The __aenter__ method runs setup, and
    __aexit__ runs cleanup (even if an exception occurs). This ensures
    resources are always properly released.
    """
    async with AsyncResource("test-resource") as resource:
        result = await resource.do_work()
    return result


# ============================================================================
# HELPER FUNCTIONS AND CLASSES (same as in exercises.py)
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
    time.sleep(0.05)
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
# TESTS (verify solutions)
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
