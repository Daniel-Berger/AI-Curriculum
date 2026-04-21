# Module 10: Async and Concurrency

## Introduction

Concurrency is one of the areas where Python and Swift diverge most dramatically. Swift was
designed with modern concurrency in mind (structured concurrency, actors, Sendable). Python's
concurrency story is older, more varied, and shaped by a unique constraint: the Global
Interpreter Lock (GIL).

This module covers all the major concurrency models in Python: `asyncio` for cooperative
multitasking, `threading` for I/O-bound parallelism, and `multiprocessing` for CPU-bound
parallelism. You will learn when to use each, how they interact, and how they compare to
Swift's concurrency features.

---

## Table of Contents

1. [The Concurrency Landscape](#1-the-concurrency-landscape)
2. [The GIL Explained](#2-the-gil-explained)
3. [async/await Fundamentals](#3-asyncawait-fundamentals)
4. [asyncio -- The Event Loop](#4-asyncio--the-event-loop)
5. [Coroutines vs Generators](#5-coroutines-vs-generators)
6. [Tasks and Concurrency with asyncio](#6-tasks-and-concurrency-with-asyncio)
7. [asyncio.gather, wait, and TaskGroups](#7-asynciogather-wait-and-taskgroups)
8. [Async Context Managers](#8-async-context-managers)
9. [Async Iterators and Generators](#9-async-iterators-and-generators)
10. [Async Comprehensions](#10-async-comprehensions)
11. [aiohttp -- Async HTTP Client](#11-aiohttp--async-http-client)
12. [asyncio.Queue -- Producer/Consumer](#12-asyncioqueue--producerconsumer)
13. [Threading Module](#13-threading-module)
14. [Multiprocessing Module](#14-multiprocessing-module)
15. [concurrent.futures -- High-Level Interface](#15-concurrentfutures--high-level-interface)
16. [CPU-Bound vs I/O-Bound -- Choosing the Right Tool](#16-cpu-bound-vs-io-bound--choosing-the-right-tool)
17. [asyncio.to_thread -- Bridging sync and async](#17-asyncioto_thread--bridging-sync-and-async)
18. [Practical Patterns and Best Practices](#18-practical-patterns-and-best-practices)

---

## 1. The Concurrency Landscape

Python offers three main concurrency models:

| Model               | Best For          | Parallelism?  | Module                  |
|----------------------|-------------------|---------------|-------------------------|
| **asyncio**          | I/O-bound work    | No (single thread) | `asyncio`          |
| **Threading**        | I/O-bound work    | No (GIL)       | `threading`            |
| **Multiprocessing**  | CPU-bound work    | Yes (separate processes) | `multiprocessing` |

### When to Use What

- **asyncio**: Network requests, file I/O, database queries, websockets -- anything where
  you spend most of the time *waiting* for external resources. Best for high-concurrency
  servers and clients.

- **Threading**: Legacy code, simple I/O concurrency, or when you need to integrate with
  libraries that do not support async. Simpler mental model than asyncio.

- **Multiprocessing**: Number crunching, image processing, data transformation -- anything
  that keeps the CPU busy. The only way to achieve true parallelism in CPython.

**Swift comparison**: Swift uses a single unified model (structured concurrency with
async/await, Task, TaskGroup, actors). Python requires you to choose the right tool.

---

## 2. The GIL Explained

### What Is the GIL?

The **Global Interpreter Lock** (GIL) is a mutex in CPython (the standard Python interpreter)
that allows only one thread to execute Python bytecode at a time. Even on a 16-core machine,
only one thread runs Python code at any given moment.

### Why Does the GIL Exist?

1. **Memory safety**: CPython uses reference counting for garbage collection. The GIL
   prevents race conditions on reference counts.
2. **Simplicity**: The GIL makes the interpreter simpler and C extensions easier to write.
3. **Historical**: When Python was created (1991), multi-core CPUs were rare.

### What the GIL Does and Does Not Block

```
GIL BLOCKS:
- Multiple threads running Python code simultaneously

GIL DOES NOT BLOCK:
- I/O operations (network, disk) -- the GIL is released during I/O
- C extensions that release the GIL (NumPy, etc.)
- Multiple processes (each process has its own GIL)
```

### Implications

```python
import threading
import time

def cpu_work():
    """CPU-bound: the GIL prevents true parallelism."""
    total = 0
    for i in range(10_000_000):
        total += i
    return total

# Single-threaded: ~1 second
start = time.time()
cpu_work()
cpu_work()
print(f"Sequential: {time.time() - start:.2f}s")

# Two threads: ALSO ~1 second (or slower due to GIL overhead!)
start = time.time()
t1 = threading.Thread(target=cpu_work)
t2 = threading.Thread(target=cpu_work)
t1.start()
t2.start()
t1.join()
t2.join()
print(f"Threaded: {time.time() - start:.2f}s")
```

For I/O-bound work, threads do help because the GIL is released during I/O:

```python
import threading
import time
import urllib.request

def fetch_url(url):
    """I/O-bound: GIL is released during network wait."""
    urllib.request.urlopen(url).read()

urls = ["https://example.com"] * 5

# Sequential: ~5 seconds
start = time.time()
for url in urls:
    fetch_url(url)
print(f"Sequential: {time.time() - start:.2f}s")

# Threaded: ~1 second (threads overlap during I/O waits)
start = time.time()
threads = [threading.Thread(target=fetch_url, args=(url,)) for url in urls]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"Threaded: {time.time() - start:.2f}s")
```

**Swift comparison**: Swift has no GIL. Multiple threads can execute Swift code in true
parallel on multiple CPU cores. This is why Swift has `Sendable`, actors, and
`@MainActor` -- it needs these safety mechanisms precisely because it allows real
parallelism. Python's GIL makes many of those concerns irrelevant (but at the cost
of true parallelism).

> **Note**: Python 3.13 introduced an experimental "free-threaded" mode that removes the GIL.
> It is opt-in and not yet the default.

---

## 3. async/await Fundamentals

### Defining an Async Function (Coroutine)

```python
import asyncio

async def greet(name: str) -> str:
    """An async function (coroutine function)."""
    return f"Hello, {name}!"

# Calling it returns a coroutine object, not the result:
coro = greet("Alice")  # <coroutine object greet at 0x...>

# You must await it to get the result:
async def main():
    result = await greet("Alice")
    print(result)  # "Hello, Alice!"

asyncio.run(main())
```

### asyncio.run() -- The Entry Point

`asyncio.run()` is how you enter the async world from synchronous code:

```python
import asyncio

async def main():
    print("Starting...")
    await asyncio.sleep(1)  # Non-blocking sleep
    print("Done!")

# This creates an event loop, runs the coroutine, and cleans up
asyncio.run(main())
```

**Swift comparison**: `asyncio.run(main())` is conceptually similar to how a Swift app's
`@main` entry point or a `Task { }` provides a context for async execution. The difference
is that Swift's runtime manages the async context implicitly, while Python requires you to
explicitly create one.

### await -- Yielding Control

`await` does two things:
1. Pauses the current coroutine
2. Gives control back to the event loop so it can run other tasks

```python
import asyncio

async def fetch_data() -> dict:
    print("Fetching data...")
    await asyncio.sleep(2)  # Simulate network delay
    print("Data received!")
    return {"key": "value"}

async def process_data() -> str:
    print("Processing...")
    await asyncio.sleep(1)  # Simulate processing
    print("Processing done!")
    return "processed"

async def main():
    # Sequential: takes 3 seconds
    data = await fetch_data()
    result = await process_data()
    print(data, result)

asyncio.run(main())
```

### Key Rule: You Can Only await Inside an async Function

```python
# This is a SyntaxError:
# result = await some_coroutine()

# Must be inside an async function:
async def main():
    result = await some_coroutine()  # OK
```

---

## 4. asyncio -- The Event Loop

The event loop is the core of asyncio. It manages and schedules coroutines.

### How the Event Loop Works

```
Event Loop Cycle:
1. Check for completed I/O operations
2. Run callbacks/coroutines that are ready
3. Schedule new I/O operations
4. Repeat
```

Think of it like iOS's RunLoop, but for async tasks instead of UI events.

### Getting and Using the Event Loop

```python
import asyncio

async def main():
    # Get the running event loop
    loop = asyncio.get_running_loop()
    print(f"Running on loop: {loop}")

asyncio.run(main())
```

### asyncio.sleep vs time.sleep

```python
import asyncio
import time

async def wrong_way():
    """DON'T DO THIS: time.sleep blocks the entire event loop."""
    time.sleep(5)  # Nothing else can run during this!

async def right_way():
    """DO THIS: asyncio.sleep yields control to the event loop."""
    await asyncio.sleep(5)  # Other tasks can run during this!
```

**Rule of thumb**: Never use blocking calls (`time.sleep`, `requests.get`,
`open().read()`) inside async functions. Use their async equivalents or run them
in a thread with `asyncio.to_thread()`.

---

## 5. Coroutines vs Generators

Coroutines and generators share syntax ancestry but serve different purposes.

### Generators (sync, yield values)

```python
def count_up(n: int):
    """A generator: yields values one at a time."""
    for i in range(n):
        yield i

for value in count_up(5):
    print(value)  # 0, 1, 2, 3, 4
```

### Coroutines (async, yield control)

```python
async def fetch_items():
    """A coroutine: awaits async operations."""
    for i in range(5):
        await asyncio.sleep(0.1)  # Yield control to event loop
        print(f"Fetched item {i}")
```

### Async Generators (both!)

```python
async def async_count_up(n: int):
    """An async generator: yields values AND yields control."""
    for i in range(n):
        await asyncio.sleep(0.1)  # Yield control
        yield i                    # Yield a value

async def main():
    async for value in async_count_up(5):
        print(value)  # 0, 1, 2, 3, 4 (with delays)
```

---

## 6. Tasks and Concurrency with asyncio

### Creating Tasks

A `Task` wraps a coroutine so it can run concurrently with other tasks:

```python
import asyncio

async def fetch_user(user_id: int) -> dict:
    print(f"Fetching user {user_id}...")
    await asyncio.sleep(1)  # Simulate network delay
    return {"id": user_id, "name": f"User {user_id}"}

async def main():
    # Sequential: takes 3 seconds
    user1 = await fetch_user(1)
    user2 = await fetch_user(2)
    user3 = await fetch_user(3)

    # Concurrent: takes ~1 second!
    task1 = asyncio.create_task(fetch_user(1))
    task2 = asyncio.create_task(fetch_user(2))
    task3 = asyncio.create_task(fetch_user(3))

    user1 = await task1
    user2 = await task2
    user3 = await task3

asyncio.run(main())
```

**Swift comparison**: `asyncio.create_task()` is analogous to Swift's `Task { }`.
Both schedule work for concurrent execution.

```swift
// Swift equivalent:
let task1 = Task { await fetchUser(1) }
let task2 = Task { await fetchUser(2) }
let task3 = Task { await fetchUser(3) }

let user1 = await task1.value
let user2 = await task2.value
let user3 = await task3.value
```

### Task Names (Python 3.12+)

```python
task = asyncio.create_task(fetch_user(1), name="fetch-user-1")
print(task.get_name())  # "fetch-user-1"
```

### Cancelling Tasks

```python
async def long_running():
    try:
        while True:
            await asyncio.sleep(1)
            print("Still running...")
    except asyncio.CancelledError:
        print("Task was cancelled!")
        # Clean up resources here
        raise  # Re-raise to confirm cancellation

async def main():
    task = asyncio.create_task(long_running())
    await asyncio.sleep(3)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("Confirmed: task cancelled")

asyncio.run(main())
```

**Swift comparison**: Swift's `Task.cancel()` is cooperative, just like Python's.
The task must check `Task.isCancelled` or handle `CancellationError`. In Python,
`asyncio.CancelledError` is raised at the `await` point.

---

## 7. asyncio.gather, wait, and TaskGroups

### asyncio.gather -- Run Coroutines Concurrently

```python
import asyncio

async def fetch_user(user_id: int) -> dict:
    await asyncio.sleep(1)
    return {"id": user_id, "name": f"User {user_id}"}

async def fetch_posts(user_id: int) -> list:
    await asyncio.sleep(1.5)
    return [{"id": 1, "title": "Post 1"}]

async def main():
    # Run both concurrently, get results as a list
    user, posts = await asyncio.gather(
        fetch_user(1),
        fetch_posts(1),
    )
    print(user)   # {"id": 1, "name": "User 1"}
    print(posts)  # [{"id": 1, "title": "Post 1"}]

asyncio.run(main())
```

**Swift comparison**: `asyncio.gather()` is similar to Swift's `async let` or
`withTaskGroup`:

```swift
// Swift async let:
async let user = fetchUser(1)
async let posts = fetchPosts(1)
let (u, p) = await (user, posts)
```

### gather With Error Handling

```python
async def might_fail():
    raise ValueError("Something went wrong")

async def main():
    # By default, if one fails, gather raises immediately
    try:
        results = await asyncio.gather(
            fetch_user(1),
            might_fail(),
        )
    except ValueError as e:
        print(f"Error: {e}")

    # With return_exceptions=True, errors are returned as results
    results = await asyncio.gather(
        fetch_user(1),
        might_fail(),
        return_exceptions=True,
    )
    # results = [{"id": 1, ...}, ValueError("Something went wrong")]
    for result in results:
        if isinstance(result, Exception):
            print(f"Error: {result}")
        else:
            print(f"Success: {result}")

asyncio.run(main())
```

### asyncio.wait -- More Control

```python
async def main():
    tasks = [
        asyncio.create_task(fetch_user(i), name=f"user-{i}")
        for i in range(5)
    ]

    # Wait for all to complete
    done, pending = await asyncio.wait(tasks)
    for task in done:
        print(task.result())

    # Wait for the first one to complete
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )
    first_result = done.pop().result()

    # Wait with a timeout
    done, pending = await asyncio.wait(tasks, timeout=2.0)
    for task in pending:
        task.cancel()  # Cancel tasks that did not finish in time
```

### TaskGroup (Python 3.11+)

TaskGroups provide structured concurrency -- similar to Swift's `TaskGroup`:

```python
import asyncio

async def fetch_user(user_id: int) -> dict:
    await asyncio.sleep(1)
    return {"id": user_id, "name": f"User {user_id}"}

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_user(1))
        task2 = tg.create_task(fetch_user(2))
        task3 = tg.create_task(fetch_user(3))

    # All tasks are guaranteed complete here
    print(task1.result())
    print(task2.result())
    print(task3.result())

asyncio.run(main())
```

**Swift comparison**: This maps directly to Swift's `withTaskGroup`:

```swift
await withTaskGroup(of: User.self) { group in
    for id in [1, 2, 3] {
        group.addTask { await fetchUser(id) }
    }
    for await user in group {
        print(user)
    }
}
```

### TaskGroup Error Handling

If any task in a TaskGroup raises an exception, all other tasks are cancelled:

```python
async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch_user(1))        # OK
            tg.create_task(might_fail())          # Raises!
            tg.create_task(fetch_user(3))         # Cancelled automatically
    except* ValueError as eg:
        # Python 3.11+ except* syntax for ExceptionGroups
        for exc in eg.exceptions:
            print(f"Error: {exc}")
```

---

## 8. Async Context Managers

### Writing an Async Context Manager

```python
class AsyncDatabaseConnection:
    def __init__(self, url: str):
        self.url = url
        self.connection = None

    async def __aenter__(self):
        """Called when entering the 'async with' block."""
        print(f"Connecting to {self.url}...")
        await asyncio.sleep(0.5)  # Simulate connection time
        self.connection = {"url": self.url, "status": "connected"}
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting the 'async with' block."""
        print("Disconnecting...")
        await asyncio.sleep(0.1)  # Simulate cleanup
        self.connection = None
        return False  # Don't suppress exceptions

async def main():
    async with AsyncDatabaseConnection("postgres://localhost/db") as db:
        print(f"Connected: {db.connection}")
        # Use the connection
    # Connection is automatically closed here
```

### Using contextlib for Simpler Syntax

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def database_connection(url: str):
    """Async context manager using decorator."""
    print(f"Connecting to {url}...")
    conn = await connect_to_db(url)
    try:
        yield conn
    finally:
        print("Disconnecting...")
        await conn.close()

async def main():
    async with database_connection("postgres://localhost/db") as conn:
        result = await conn.query("SELECT * FROM users")
```

**Swift comparison**: This is similar to how you might use a `withCheckedThrowingContinuation`
or a custom resource management pattern. Swift does not have direct equivalent syntax for
context managers, but `defer` and RAII patterns serve a similar purpose.

---

## 9. Async Iterators and Generators

### Async Iterator Protocol

```python
class AsyncRange:
    """An async iterator that yields numbers with delays."""

    def __init__(self, start: int, stop: int):
        self.current = start
        self.stop = stop

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        value = self.current
        self.current += 1
        await asyncio.sleep(0.1)  # Simulate async work
        return value

async def main():
    async for num in AsyncRange(0, 5):
        print(num)  # 0, 1, 2, 3, 4 (with delays)
```

### Async Generators (Simpler)

```python
async def async_range(start: int, stop: int):
    """Async generator -- much simpler than the class-based version."""
    for i in range(start, stop):
        await asyncio.sleep(0.1)
        yield i

async def read_lines_async(filename: str):
    """Async generator that reads lines from a file."""
    # In real code, use aiofiles
    import aiofiles
    async with aiofiles.open(filename) as f:
        async for line in f:
            yield line.strip()

async def main():
    async for num in async_range(0, 5):
        print(num)
```

### Async Generator with send() and close()

```python
async def accumulator():
    """Async generator that receives values via send()."""
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value

async def main():
    acc = accumulator()
    await acc.__anext__()       # Prime the generator
    print(await acc.asend(10))  # 10
    print(await acc.asend(20))  # 30
    print(await acc.asend(30))  # 60
    await acc.aclose()
```

---

## 10. Async Comprehensions

### Async For Comprehension

```python
async def get_user(user_id: int) -> dict:
    await asyncio.sleep(0.1)
    return {"id": user_id, "name": f"User {user_id}"}

async def main():
    # Async list comprehension
    users = [await get_user(i) for i in range(5)]
    print(users)

    # Async list comprehension with async for
    names = [name async for name in async_name_generator()]

    # Async set comprehension
    unique_ids = {user["id"] async for user in async_user_stream()}

    # Async dict comprehension
    user_map = {u["id"]: u async for u in async_user_stream()}
```

**Important**: `[await coro(i) for i in range(5)]` runs coroutines *sequentially*.
For concurrent execution, use `asyncio.gather`:

```python
async def main():
    # Sequential (slow):
    users = [await get_user(i) for i in range(5)]

    # Concurrent (fast):
    users = await asyncio.gather(*[get_user(i) for i in range(5)])
```

---

## 11. aiohttp -- Async HTTP Client

### Installation

```bash
pip install aiohttp
```

### Basic Usage

```python
import aiohttp
import asyncio

async def fetch_url(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def main():
    html = await fetch_url("https://example.com")
    print(html[:100])

asyncio.run(main())
```

### Reusing Sessions (Important for Performance)

```python
async def fetch_many_urls(urls: list[str]) -> list[str]:
    """Reuse a single session for multiple requests."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch_with_session(session, url))
        return await asyncio.gather(*tasks)

async def fetch_with_session(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/ip",
        "https://httpbin.org/headers",
    ]
    results = await fetch_many_urls(urls)
    print(f"Fetched {len(results)} URLs concurrently!")

asyncio.run(main())
```

### POST Requests and JSON

```python
async def create_user(name: str, email: str) -> dict:
    async with aiohttp.ClientSession() as session:
        payload = {"name": name, "email": email}
        async with session.post(
            "https://api.example.com/users",
            json=payload,
            headers={"Authorization": "Bearer token123"},
        ) as response:
            response.raise_for_status()  # Raise on HTTP errors
            return await response.json()
```

### Error Handling and Timeouts

```python
import aiohttp
import asyncio

async def fetch_with_retry(url: str, max_retries: int = 3) -> str:
    timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for attempt in range(max_retries):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise
                wait = 2 ** attempt  # Exponential backoff
                print(f"Retry {attempt + 1} after {wait}s: {e}")
                await asyncio.sleep(wait)
    return ""  # Unreachable, but satisfies type checker
```

**Swift comparison**: `aiohttp.ClientSession` is analogous to `URLSession`. Both
manage connection pooling and should be reused across requests.

```swift
// Swift equivalent concept:
let session = URLSession.shared
let (data, response) = try await session.data(from: url)
```

---

## 12. asyncio.Queue -- Producer/Consumer

### Basic Queue Usage

```python
import asyncio

async def producer(queue: asyncio.Queue, items: list):
    """Produce items and put them in the queue."""
    for item in items:
        await queue.put(item)
        print(f"Produced: {item}")
        await asyncio.sleep(0.1)  # Simulate work

    # Signal that we are done
    await queue.put(None)  # Sentinel value

async def consumer(queue: asyncio.Queue):
    """Consume items from the queue."""
    while True:
        item = await queue.get()
        if item is None:
            break  # Sentinel received
        print(f"Consumed: {item}")
        await asyncio.sleep(0.2)  # Simulate processing
        queue.task_done()

async def main():
    queue: asyncio.Queue = asyncio.Queue(maxsize=5)

    # Run producer and consumer concurrently
    await asyncio.gather(
        producer(queue, ["apple", "banana", "cherry"]),
        consumer(queue),
    )

asyncio.run(main())
```

### Multiple Producers and Consumers

```python
import asyncio
import random

async def producer(queue: asyncio.Queue, producer_id: int, num_items: int):
    for i in range(num_items):
        item = f"item-{producer_id}-{i}"
        await queue.put(item)
        print(f"Producer {producer_id}: produced {item}")
        await asyncio.sleep(random.uniform(0.05, 0.15))

async def consumer(queue: asyncio.Queue, consumer_id: int):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumer {consumer_id}: processing {item}")
        await asyncio.sleep(random.uniform(0.1, 0.3))
        queue.task_done()

async def main():
    queue: asyncio.Queue = asyncio.Queue(maxsize=10)
    num_producers = 3
    num_consumers = 2
    items_per_producer = 5

    producers = [
        asyncio.create_task(producer(queue, i, items_per_producer))
        for i in range(num_producers)
    ]

    consumers = [
        asyncio.create_task(consumer(queue, i))
        for i in range(num_consumers)
    ]

    # Wait for all producers to finish
    await asyncio.gather(*producers)

    # Send sentinel values to stop consumers
    for _ in range(num_consumers):
        await queue.put(None)

    # Wait for all consumers to finish
    await asyncio.gather(*consumers)
    print("All done!")

asyncio.run(main())
```

### Priority Queue

```python
async def main():
    pq: asyncio.PriorityQueue = asyncio.PriorityQueue()

    # Lower numbers = higher priority
    await pq.put((3, "low priority"))
    await pq.put((1, "high priority"))
    await pq.put((2, "medium priority"))

    while not pq.empty():
        priority, item = await pq.get()
        print(f"Priority {priority}: {item}")
    # Output:
    # Priority 1: high priority
    # Priority 2: medium priority
    # Priority 3: low priority
```

---

## 13. Threading Module

### Basic Threading

```python
import threading
import time

def download_file(url: str, filename: str) -> None:
    """Simulate downloading a file."""
    print(f"Downloading {filename}...")
    time.sleep(2)  # Simulate network delay
    print(f"Downloaded {filename}")

# Create and start threads
thread1 = threading.Thread(target=download_file, args=("url1", "file1.txt"))
thread2 = threading.Thread(target=download_file, args=("url2", "file2.txt"))

thread1.start()
thread2.start()

# Wait for both to complete
thread1.join()
thread2.join()
print("All downloads complete!")
```

### Thread With Return Values

Threads do not return values directly. Use shared data structures:

```python
import threading
from typing import Any

results: dict[str, Any] = {}
lock = threading.Lock()

def fetch_data(url: str, key: str) -> None:
    # Simulate work
    import time
    time.sleep(1)
    data = f"Data from {url}"

    with lock:  # Thread-safe access to shared dict
        results[key] = data

threads = []
for i in range(5):
    t = threading.Thread(
        target=fetch_data,
        args=(f"https://api.example.com/{i}", f"result_{i}"),
    )
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(results)
```

### Threading.Lock -- Preventing Race Conditions

```python
import threading

counter = 0
lock = threading.Lock()

def increment(n: int) -> None:
    global counter
    for _ in range(n):
        with lock:  # Only one thread can execute this block at a time
            counter += 1

threads = [
    threading.Thread(target=increment, args=(100_000,))
    for _ in range(10)
]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Counter: {counter}")  # Always 1,000,000 with lock
```

### Other Synchronization Primitives

```python
# RLock: Reentrant lock (same thread can acquire multiple times)
rlock = threading.RLock()

# Event: Signal between threads
event = threading.Event()
# Thread A: event.wait()  -- blocks until set
# Thread B: event.set()   -- unblocks thread A

# Semaphore: Allow N threads at once
semaphore = threading.Semaphore(3)  # At most 3 concurrent
with semaphore:
    # Only 3 threads can be here at once
    do_limited_work()

# Condition: Wait for a condition to be true
condition = threading.Condition()
with condition:
    condition.wait_for(lambda: data_ready)
    process(data)
```

### Daemon Threads

```python
def background_task():
    while True:
        time.sleep(1)
        print("Background work...")

# Daemon thread: killed when main thread exits
t = threading.Thread(target=background_task, daemon=True)
t.start()

# Main thread continues; daemon dies when main exits
time.sleep(3)
print("Main thread done")
```

**Swift comparison**: Python's `threading.Thread` is similar to creating a
`DispatchQueue` or `Thread` in Swift. Python's `Lock` is like `NSLock` or
`os_unfair_lock`. However, due to the GIL, Python threads do not achieve
true CPU parallelism.

---

## 14. Multiprocessing Module

### Why Multiprocessing?

Multiprocessing bypasses the GIL by creating separate Python processes, each with
its own interpreter and memory space. This is the only way to achieve true CPU
parallelism in CPython.

### Basic Multiprocessing

```python
import multiprocessing
import os

def cpu_intensive(n: int) -> int:
    """CPU-bound work: calculate sum of squares."""
    print(f"Process {os.getpid()} computing...")
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    # Create processes
    p1 = multiprocessing.Process(target=cpu_intensive, args=(10_000_000,))
    p2 = multiprocessing.Process(target=cpu_intensive, args=(10_000_000,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
```

### multiprocessing.Pool -- The Easy Way

```python
import multiprocessing

def square(n: int) -> int:
    return n * n

if __name__ == "__main__":
    with multiprocessing.Pool(processes=4) as pool:
        # map: apply function to each item
        results = pool.map(square, range(10))
        print(results)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

        # starmap: for functions with multiple arguments
        pairs = [(2, 3), (4, 5), (6, 7)]
        results = pool.starmap(pow, pairs)
        print(results)  # [8, 1024, 279936]

        # apply_async: non-blocking
        future = pool.apply_async(square, (42,))
        result = future.get(timeout=5)  # Wait for result
        print(result)  # 1764
```

### Sharing Data Between Processes

Processes have separate memory, so sharing data requires special mechanisms:

```python
import multiprocessing

def worker(shared_value, shared_array, lock):
    with lock:
        shared_value.value += 1
        for i in range(len(shared_array)):
            shared_array[i] += 1

if __name__ == "__main__":
    lock = multiprocessing.Lock()
    value = multiprocessing.Value("i", 0)       # Shared integer
    array = multiprocessing.Array("i", [0] * 5)  # Shared array

    processes = [
        multiprocessing.Process(target=worker, args=(value, array, lock))
        for _ in range(4)
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    print(f"Value: {value.value}")  # 4
    print(f"Array: {list(array)}")  # [4, 4, 4, 4, 4]
```

### When to Use multiprocessing

- Image/video processing
- Scientific computing
- Data transformation on large datasets
- Any task that keeps the CPU busy

**Swift comparison**: Python's multiprocessing is like using `DispatchQueue.global()`
or `ProcessInfo.processInfo.performExpiringActivity` but at the process level.
Swift does not need multiprocessing for CPU parallelism because it has no GIL --
regular threads achieve true parallelism.

---

## 15. concurrent.futures -- High-Level Interface

`concurrent.futures` provides a unified API for both threading and multiprocessing.

### ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch_url(url: str) -> str:
    time.sleep(1)  # Simulate network delay
    return f"Content from {url}"

# Using context manager
with ThreadPoolExecutor(max_workers=5) as executor:
    urls = [f"https://example.com/page/{i}" for i in range(10)]

    # submit: submit one task at a time
    future = executor.submit(fetch_url, urls[0])
    result = future.result()  # Blocks until complete

    # map: submit many tasks, get results in order
    results = list(executor.map(fetch_url, urls))
    print(f"Fetched {len(results)} pages")
```

### ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor
import math

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    numbers = range(100_000, 101_000)

    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(is_prime, numbers))
        primes = [n for n, is_p in zip(numbers, results) if is_p]
        print(f"Found {len(primes)} primes")
```

### Future Objects

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def slow_task(task_id: int) -> str:
    time.sleep(task_id)
    return f"Task {task_id} done"

with ThreadPoolExecutor() as executor:
    futures = {
        executor.submit(slow_task, i): i
        for i in range(5)
    }

    # as_completed: iterate results as they finish (not in order)
    for future in as_completed(futures):
        task_id = futures[future]
        try:
            result = future.result()
            print(f"Task {task_id}: {result}")
        except Exception as e:
            print(f"Task {task_id} failed: {e}")
```

### Comparison: ThreadPoolExecutor vs ProcessPoolExecutor

| Feature                  | ThreadPoolExecutor           | ProcessPoolExecutor          |
|--------------------------|------------------------------|------------------------------|
| Use case                 | I/O-bound tasks              | CPU-bound tasks              |
| GIL impact               | Limited by GIL for CPU work  | Bypasses GIL (separate processes) |
| Memory                   | Shared memory                | Separate memory per process  |
| Startup cost             | Low                          | High (process creation)      |
| Data sharing             | Easy (shared references)     | Requires serialization (pickle) |
| API                      | Identical                    | Identical                    |

---

## 16. CPU-Bound vs I/O-Bound -- Choosing the Right Tool

### Decision Tree

```
Is your task I/O-bound or CPU-bound?
    |
    |-- I/O-bound (network, disk, database):
    |       |
    |       |-- Need high concurrency (100s+ connections)?
    |       |       --> asyncio + aiohttp
    |       |
    |       |-- Simple concurrency (10s of connections)?
    |       |       --> ThreadPoolExecutor
    |       |
    |       |-- Need to integrate with sync libraries?
    |               --> ThreadPoolExecutor or asyncio.to_thread
    |
    |-- CPU-bound (math, image processing, data crunching):
            |
            |-- Can the work be split into independent chunks?
            |       --> ProcessPoolExecutor
            |
            |-- Need shared memory?
            |       --> multiprocessing with Value/Array
            |
            |-- Consider using NumPy/Pandas (release GIL internally)?
                    --> Threading might work
```

### Benchmark: I/O-Bound Task

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

async def async_fetch(url: str) -> str:
    await asyncio.sleep(0.5)  # Simulate network I/O
    return f"Data from {url}"

def sync_fetch(url: str) -> str:
    time.sleep(0.5)  # Simulate network I/O
    return f"Data from {url}"

async def benchmark():
    urls = [f"https://example.com/{i}" for i in range(20)]

    # asyncio approach
    start = time.time()
    results = await asyncio.gather(*[async_fetch(url) for url in urls])
    print(f"asyncio: {time.time() - start:.2f}s")

    # ThreadPool approach
    start = time.time()
    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(sync_fetch, urls))
    print(f"ThreadPool: {time.time() - start:.2f}s")

asyncio.run(benchmark())
# Both: ~0.5s (20 concurrent requests, each taking 0.5s)
```

### Benchmark: CPU-Bound Task

```python
import time
import math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_work(n: int) -> int:
    """Pure CPU computation."""
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    tasks = [5_000_000] * 4

    # Sequential
    start = time.time()
    results = [cpu_work(n) for n in tasks]
    print(f"Sequential: {time.time() - start:.2f}s")

    # ThreadPool (GIL limits parallelism)
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(cpu_work, tasks))
    print(f"ThreadPool: {time.time() - start:.2f}s")  # Similar to sequential!

    # ProcessPool (true parallelism)
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(cpu_work, tasks))
    print(f"ProcessPool: {time.time() - start:.2f}s")  # ~4x faster!
```

---

## 17. asyncio.to_thread -- Bridging sync and async

### The Problem

You are writing async code but need to call a synchronous, blocking function:

```python
import asyncio
import time

def blocking_io_operation() -> str:
    """A sync function that blocks (e.g., uses requests, reads files)."""
    time.sleep(2)
    return "result"

async def main():
    # DON'T DO THIS: blocks the event loop
    result = blocking_io_operation()

    # DO THIS: run in a thread so the event loop stays free
    result = await asyncio.to_thread(blocking_io_operation)
    print(result)

asyncio.run(main())
```

### Practical Example: Mixing Sync and Async

```python
import asyncio
import time

def sync_database_query(query: str) -> list[dict]:
    """Simulates a sync database query (e.g., using psycopg2)."""
    time.sleep(1)
    return [{"id": 1, "name": "Alice"}]

def sync_file_read(path: str) -> str:
    """Simulates reading a file synchronously."""
    time.sleep(0.5)
    return f"Contents of {path}"

async def async_api_call(url: str) -> dict:
    """An async API call."""
    await asyncio.sleep(0.5)
    return {"status": "ok", "url": url}

async def main():
    # Run sync and async operations concurrently
    db_result, file_content, api_result = await asyncio.gather(
        asyncio.to_thread(sync_database_query, "SELECT * FROM users"),
        asyncio.to_thread(sync_file_read, "/path/to/file"),
        async_api_call("https://api.example.com/data"),
    )

    print(f"DB: {db_result}")
    print(f"File: {file_content}")
    print(f"API: {api_result}")
    # Total time: ~1 second (not 2 seconds)

asyncio.run(main())
```

**Swift comparison**: `asyncio.to_thread()` is similar to:

```swift
// Swift: running blocking code off the main actor
let result = await Task.detached {
    return blockingOperation()
}.value
```

---

## 18. Practical Patterns and Best Practices

### Pattern 1: Rate-Limited Concurrent Requests

```python
import asyncio
import aiohttp

async def rate_limited_fetch(
    urls: list[str],
    max_concurrent: int = 10,
) -> list[str]:
    """Fetch URLs with a concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def fetch_one(session: aiohttp.ClientSession, url: str) -> str:
        async with semaphore:
            async with session.get(url) as response:
                return await response.text()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    return results
```

### Pattern 2: Timeout for Async Operations

```python
import asyncio

async def fetch_with_timeout(url: str, timeout: float = 5.0) -> str | None:
    try:
        result = await asyncio.wait_for(
            fetch_url(url),
            timeout=timeout,
        )
        return result
    except asyncio.TimeoutError:
        print(f"Timeout fetching {url}")
        return None
```

### Pattern 3: Retry with Exponential Backoff

```python
import asyncio
import random

async def retry_async(
    coro_func,
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
):
    """Retry an async function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await coro_func(*args)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
            await asyncio.sleep(delay)
```

### Pattern 4: Graceful Shutdown

```python
import asyncio
import signal

async def main():
    # Handle shutdown signals
    loop = asyncio.get_running_loop()
    shutdown_event = asyncio.Event()

    def signal_handler():
        print("Shutdown signal received")
        shutdown_event.set()

    loop.add_signal_handler(signal.SIGTERM, signal_handler)
    loop.add_signal_handler(signal.SIGINT, signal_handler)

    # Run until shutdown
    task = asyncio.create_task(worker())
    await shutdown_event.wait()

    # Clean up
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print("Clean shutdown complete")
```

### Best Practices Summary

1. **Never block the event loop**: Use `await` for I/O, `asyncio.to_thread()` for
   blocking sync code.

2. **Reuse sessions**: Create one `aiohttp.ClientSession` and share it across requests.

3. **Use TaskGroups** (Python 3.11+) for structured concurrency instead of bare
   `create_task()` calls.

4. **Limit concurrency**: Use `asyncio.Semaphore` to prevent overwhelming external
   services.

5. **Handle cancellation**: Always catch `asyncio.CancelledError` and clean up.

6. **Choose the right tool**:
   - asyncio for I/O-bound, high-concurrency work
   - threading for simple I/O parallelism or sync library integration
   - multiprocessing for CPU-bound work

7. **Use `if __name__ == "__main__":`** when using multiprocessing (required on macOS/Windows).

8. **Avoid mixing paradigms unnecessarily**: Stick to one concurrency model per component
   when possible.

---

## Summary

| Concept                     | Key API                                        |
|-----------------------------|------------------------------------------------|
| Async function              | `async def func():`                            |
| Await                       | `result = await coroutine()`                   |
| Run async code              | `asyncio.run(main())`                          |
| Create task                 | `asyncio.create_task(coro())`                  |
| Run concurrently            | `asyncio.gather(coro1(), coro2())`             |
| Task group                  | `async with asyncio.TaskGroup() as tg:`        |
| Async sleep                 | `await asyncio.sleep(seconds)`                 |
| Async queue                 | `asyncio.Queue(maxsize=N)`                     |
| Async HTTP                  | `aiohttp.ClientSession()`                      |
| Run sync in thread          | `await asyncio.to_thread(func, *args)`         |
| Thread pool                 | `ThreadPoolExecutor(max_workers=N)`            |
| Process pool                | `ProcessPoolExecutor(max_workers=N)`           |
| Threading lock              | `threading.Lock()` + `with lock:`              |

---

## Next Steps

- Work through the exercises in `exercises.py`
- Try building a simple web scraper with aiohttp
- Compare performance of threading vs multiprocessing on CPU-bound tasks
- Check out `swift_comparison.md` for Swift concurrency mappings
- Explore the [asyncio documentation](https://docs.python.org/3/library/asyncio.html)
