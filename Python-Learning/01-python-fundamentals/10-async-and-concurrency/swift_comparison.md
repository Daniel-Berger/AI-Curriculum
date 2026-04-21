# Swift Comparison: Swift Concurrency vs Python Async/Concurrency

## Overview

Swift and Python both support async/await syntax, but the underlying models differ
significantly. Swift provides structured concurrency with compile-time safety (Sendable,
actors). Python provides multiple concurrency models (asyncio, threading, multiprocessing)
and relies on the GIL for thread safety of the interpreter itself.

---

## At a Glance

| Aspect                    | Swift                                | Python                                  |
|---------------------------|--------------------------------------|-----------------------------------------|
| async/await               | Language-level, compiler-enforced    | Language-level, runtime-enforced        |
| Concurrency model         | Structured concurrency               | Event loop (asyncio)                    |
| Thread safety             | Sendable, actors, compile-time       | GIL (runtime), manual locks             |
| True parallelism          | Yes (threads)                        | Only via multiprocessing                |
| Task creation             | `Task { }`                           | `asyncio.create_task()`                 |
| Task groups               | `withTaskGroup`                      | `asyncio.TaskGroup` (3.11+)            |
| Actor isolation           | `actor` keyword                      | No equivalent (GIL provides some safety)|
| Cancellation              | Cooperative (`Task.isCancelled`)     | Cooperative (`CancelledError`)          |
| Main thread               | `@MainActor`                         | Event loop (single-threaded)            |

---

## async/await Syntax

### Swift

```swift
func fetchUser(id: Int) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// Calling:
let user = try await fetchUser(id: 1)
```

### Python

```python
async def fetch_user(user_id: int) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/users/{user_id}") as resp:
            return await resp.json()

# Calling:
user = await fetch_user(1)
```

**Key differences:**
- Swift uses `throws` for error handling; Python uses regular exceptions
- Swift's async functions are part of the type system; Python's are runtime-checked
- Swift does not need a session object (URLSession.shared); Python needs aiohttp session

---

## Task Creation

### Swift

```swift
// Fire-and-forget task
Task {
    let user = await fetchUser(id: 1)
    print(user.name)
}

// Task with a result
let task = Task {
    return await fetchUser(id: 1)
}
let user = await task.value
```

### Python

```python
# Fire-and-forget task (must be inside an async function)
task = asyncio.create_task(fetch_user(1))

# Get the result later
user = await task

# Or use asyncio.run() as the entry point
asyncio.run(main())
```

| Swift                              | Python                                  |
|------------------------------------|-----------------------------------------|
| `Task { await work() }`           | `asyncio.create_task(work())`           |
| `await task.value`                 | `await task`                            |
| `task.cancel()`                    | `task.cancel()`                         |
| `Task.isCancelled`                 | `task.cancelled()`                      |
| `try Task.checkCancellation()`     | Check `asyncio.CancelledError`          |
| `Task.detached { }`               | No direct equivalent                    |

---

## Concurrent Execution

### Swift: async let

```swift
func fetchDashboard() async throws -> Dashboard {
    async let user = fetchUser(id: 1)
    async let posts = fetchPosts(userId: 1)
    async let notifications = fetchNotifications()

    return Dashboard(
        user: try await user,
        posts: try await posts,
        notifications: try await notifications
    )
}
```

### Python: asyncio.gather

```python
async def fetch_dashboard() -> dict:
    user, posts, notifications = await asyncio.gather(
        fetch_user(1),
        fetch_posts(user_id=1),
        fetch_notifications(),
    )
    return {
        "user": user,
        "posts": posts,
        "notifications": notifications,
    }
```

| Swift                              | Python                                  |
|------------------------------------|-----------------------------------------|
| `async let x = expr`              | No direct equivalent (use gather)       |
| Multiple `async let` + `await`    | `asyncio.gather(coro1, coro2, ...)`     |
| Automatic cancellation on error    | `gather` can cancel (default) or return errors |

---

## Task Groups

### Swift

```swift
func fetchAllUsers(ids: [Int]) async throws -> [User] {
    try await withThrowingTaskGroup(of: User.self) { group in
        for id in ids {
            group.addTask {
                try await fetchUser(id: id)
            }
        }

        var users: [User] = []
        for try await user in group {
            users.append(user)
        }
        return users
    }
}
```

### Python (3.11+)

```python
async def fetch_all_users(ids: list[int]) -> list[dict]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_user(uid)) for uid in ids]

    return [task.result() for task in tasks]
```

| Swift TaskGroup                    | Python TaskGroup                        |
|------------------------------------|-----------------------------------------|
| `withTaskGroup(of:) { group in }`  | `async with asyncio.TaskGroup() as tg:` |
| `group.addTask { }`               | `tg.create_task(coro())`               |
| `for await result in group`       | Access `task.result()` after group exits|
| `withThrowingTaskGroup`           | TaskGroup raises `ExceptionGroup`       |
| Cancels all tasks on error         | Cancels all tasks on error              |

---

## Actors and Thread Safety

### Swift: Actors

```swift
actor BankAccount {
    private var balance: Decimal

    init(balance: Decimal) {
        self.balance = balance
    }

    func deposit(_ amount: Decimal) {
        balance += amount
    }

    func withdraw(_ amount: Decimal) throws {
        guard balance >= amount else {
            throw BankError.insufficientFunds
        }
        balance -= amount
    }

    func getBalance() -> Decimal {
        return balance
    }
}

// Usage:
let account = BankAccount(balance: 1000)
await account.deposit(500)
let balance = await account.getBalance()
```

### Python: No Direct Equivalent

Python has no actor model. The GIL provides some safety for simple operations,
but for complex shared state you use locks:

```python
import threading

class BankAccount:
    def __init__(self, balance: float):
        self._balance = balance
        self._lock = threading.Lock()

    def deposit(self, amount: float) -> None:
        with self._lock:
            self._balance += amount

    def withdraw(self, amount: float) -> None:
        with self._lock:
            if self._balance < amount:
                raise ValueError("Insufficient funds")
            self._balance -= amount

    def get_balance(self) -> float:
        with self._lock:
            return self._balance
```

| Swift actor feature               | Python equivalent                       |
|------------------------------------|-----------------------------------------|
| `actor MyActor { }`              | Class with `threading.Lock`             |
| Automatic isolation                | Manual lock management                  |
| `@MainActor`                      | Event loop (for asyncio)                |
| `nonisolated`                     | No concept needed                       |
| Compile-time safety                | Runtime only                            |

---

## Sendable and Data Races

### Swift

```swift
// Sendable: safe to share across concurrency domains
struct UserData: Sendable {
    let name: String
    let age: Int
}

// Non-Sendable: compiler warns if shared unsafely
class MutableState {
    var count = 0  // NOT safe to share
}
```

### Python

Python has **no Sendable equivalent**. The GIL prevents true data races on Python
objects (reference counting is protected), but logical races can still occur:

```python
# This is "safe" from crashes due to the GIL, but logically incorrect
# without a lock in multi-threaded code:
counter = 0

def increment():
    global counter
    temp = counter    # Read
    temp += 1         # Modify
    counter = temp    # Write -- another thread could have changed counter!
```

For multiprocessing, data must be explicitly serializable (picklable), which is
conceptually similar to Sendable.

---

## The GIL vs Swift's Threading Model

| Aspect                    | Python (with GIL)                     | Swift                                  |
|---------------------------|---------------------------------------|----------------------------------------|
| True parallelism          | Only via multiprocessing              | Native with threads                    |
| Thread safety             | GIL protects interpreter internals    | Developer responsibility (actors help) |
| Data race prevention      | GIL prevents crashes, not logic bugs  | Sendable + actors prevent both         |
| CPU-bound scaling         | Must use multiprocessing              | Use DispatchQueue / threads            |
| I/O-bound scaling         | asyncio or threading                  | async/await with tasks                 |

---

## HTTP Networking

### Swift

```swift
func fetchData(from url: URL) async throws -> Data {
    let (data, response) = try await URLSession.shared.data(from: url)
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.badResponse
    }
    return data
}
```

### Python

```python
async def fetch_data(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError(f"Bad response: {response.status}")
            return await response.read()
```

| Swift URLSession                   | Python aiohttp                          |
|------------------------------------|-----------------------------------------|
| `URLSession.shared`               | `aiohttp.ClientSession()`              |
| `session.data(from: url)`         | `session.get(url)`                      |
| Automatic session management       | Must use `async with` for cleanup       |
| Built into Foundation              | Third-party (`pip install aiohttp`)     |
| `URLRequest` for configuration     | Parameters on session/request methods   |
| `URLSessionConfiguration`         | `aiohttp.ClientTimeout`, etc.          |

---

## Event Loop vs Swift Runtime

### Swift

Swift's concurrency runtime is managed by the system:
- The runtime manages a thread pool internally
- You never interact with the event loop directly
- `@MainActor` ensures UI work happens on the main thread
- The system decides how to schedule tasks

### Python

Python's asyncio event loop is explicit:
- You create and run the event loop with `asyncio.run()`
- Only one event loop per thread
- The event loop is single-threaded (cooperative multitasking)
- You must avoid blocking the event loop

```python
# Python: explicit event loop management
async def main():
    # Everything in here runs on the event loop
    pass

asyncio.run(main())  # Creates loop, runs main, closes loop
```

| Concept                    | Swift                                | Python                                 |
|---------------------------|--------------------------------------|----------------------------------------|
| Runtime management        | Implicit (system-managed)            | Explicit (`asyncio.run()`)             |
| Thread pool               | System-managed                       | Single-threaded event loop             |
| Main thread               | `@MainActor`                         | Event loop thread                      |
| Background work           | `Task.detached { }` / DispatchQueue  | `asyncio.to_thread()` / ThreadPool     |
| Blocking operations       | Run on background thread             | Must use `to_thread()` or be async     |

---

## Structured Concurrency Comparison

| Feature                     | Swift                                | Python                                 |
|-----------------------------|--------------------------------------|----------------------------------------|
| Scope-bound tasks           | `withTaskGroup` / `async let`        | `asyncio.TaskGroup` (3.11+)           |
| Automatic cancellation      | Yes, when scope exits                | Yes, in TaskGroup                      |
| Unstructured tasks          | `Task { }`, `Task.detached { }`      | `asyncio.create_task()`               |
| Cancellation propagation    | Automatic in structured              | Automatic in TaskGroup                 |
| Error propagation           | Throws from group                    | ExceptionGroup from TaskGroup          |

---

## Quick Reference: Swift to Python Translation

| Swift Pattern                              | Python Equivalent                           |
|--------------------------------------------|---------------------------------------------|
| `async func foo() -> T`                   | `async def foo() -> T:`                     |
| `try await foo()`                          | `await foo()`                               |
| `Task { await foo() }`                    | `asyncio.create_task(foo())`                |
| `async let x = foo()`                     | `task_x = asyncio.create_task(foo())`       |
| `await x`                                 | `x = await task_x`                          |
| `withTaskGroup { group in ... }`           | `async with asyncio.TaskGroup() as tg: ...` |
| `group.addTask { await foo() }`            | `tg.create_task(foo())`                     |
| `for await result in group`               | `[t.result() for t in tasks]` after group   |
| `task.cancel()`                            | `task.cancel()`                             |
| `Task.sleep(nanoseconds:)`                | `await asyncio.sleep(seconds)`              |
| `actor MyActor { }`                       | Class + `threading.Lock`                    |
| `@MainActor`                              | Run on event loop thread                    |
| `URLSession.shared.data(from:)`           | `aiohttp.ClientSession().get()`             |
| `DispatchQueue.global().async { }`         | `asyncio.to_thread(sync_func)`              |
| `DispatchGroup`                            | `asyncio.gather()` or `asyncio.wait()`      |

---

## Common Pitfalls for Swift Developers

1. **No implicit concurrency**: In Swift, `async let` starts concurrent execution
   automatically. In Python, you must explicitly use `create_task` or `gather`.
   Simply calling `await coro1(); await coro2()` runs them sequentially.

2. **No compile-time safety**: Python will not warn you about data races, missing
   awaits on tasks, or Sendable violations. You must be disciplined.

3. **Blocking the event loop**: Python's event loop is single-threaded. Calling
   `time.sleep()` or `requests.get()` inside an async function blocks everything.
   Always use async equivalents or `asyncio.to_thread()`.

4. **Multiple concurrency models**: Unlike Swift's unified model, Python has asyncio,
   threading, and multiprocessing. You need to choose the right tool.

5. **The GIL misconception**: The GIL does not make your code thread-safe. It prevents
   crashes from concurrent access to Python internals, but logical races are still
   possible.

6. **No actor equivalent**: You cannot simply declare a class as an `actor` in Python.
   You need manual locking or must design your async code to avoid shared mutable state.
