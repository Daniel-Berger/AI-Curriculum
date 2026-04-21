# Phase 1: Python Fundamentals -- Comprehensive Quiz

**30 questions** covering all 10 modules.
Difficulty distribution: 10 Easy, 12 Medium, 8 Hard.

For Swift/iOS developers: many questions include Swift comparisons to reinforce mental mapping between the two languages.

---

## Module 01: Syntax and Types (3 questions)

### Q1 (Easy) -- Multiple Choice

What is the Python equivalent of Swift's `let` (constant declaration)?

```python
# Which of these prevents reassignment?
A) const x = 10
B) let x = 10
C) final x = 10
D) None of the above -- Python has no built-in constant enforcement
```

---

### Q2 (Medium) -- Short Answer

Explain the difference between `is` and `==` in Python. How does this compare to Swift's `===` and `==`? Give an example where `==` returns `True` but `is` returns `False`.

---

### Q3 (Hard) -- Code Writing

Write a function `parse_value` with full type annotations that accepts a string and returns `int | float | str` depending on what the string contains. It should try to parse as `int` first, then `float`, and fall back to returning the original string. Include a docstring.

---

## Module 02: Control Flow (3 questions)

### Q4 (Easy) -- Multiple Choice

What Python keyword is equivalent to Swift's `default` in a switch statement?

```python
A) default:
B) case _:
C) else:
D) otherwise:
```

---

### Q5 (Medium) -- Code Writing

Rewrite the following Swift code in idiomatic Python using `match/case`:

```swift
enum Direction {
    case north, south, east, west
}

func describe(_ direction: Direction) -> String {
    switch direction {
    case .north: return "Going up"
    case .south: return "Going down"
    case .east, .west: return "Going sideways"
    }
}
```

---

### Q6 (Easy) -- Short Answer

Explain the difference between a `for` loop and a `while` loop in Python. In what situation would you prefer a `while` loop? How does Python's `for...else` construct work, and does Swift have an equivalent?

---

## Module 03: Data Structures (3 questions)

### Q7 (Easy) -- Multiple Choice

Which Python data structure is most similar to a Swift `Set<String>`?

```python
A) ["a", "b", "c"]
B) ("a", "b", "c")
C) {"a", "b", "c"}
D) {"a": 1, "b": 2, "c": 3}
```

---

### Q8 (Medium) -- Code Writing

Given a list of dictionaries representing employees:

```python
employees = [
    {"name": "Alice", "department": "Engineering", "salary": 120000},
    {"name": "Bob", "department": "Marketing", "salary": 80000},
    {"name": "Carol", "department": "Engineering", "salary": 140000},
    {"name": "David", "department": "Marketing", "salary": 90000},
    {"name": "Eva", "department": "Engineering", "salary": 100000},
]
```

Write a single dictionary comprehension that produces `{"Engineering": 120000.0, "Marketing": 85000.0}` -- the average salary per department. You may use helper variables but the final result must be a comprehension.

---

### Q9 (Medium) -- Short Answer

Explain the difference between a Python `list` and a `tuple`. Beyond mutability, discuss: hashability, performance characteristics, memory usage, and common use cases for each. When would you choose a `NamedTuple` over a `dataclass`?

---

## Module 04: Functions and Closures (3 questions)

### Q10 (Easy) -- Multiple Choice

What does the `*` in this function signature mean?

```python
def greet(name: str, *, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"
```

```
A) name can accept multiple values
B) greeting is a required positional argument
C) All parameters after * must be passed as keyword arguments
D) The function accepts any number of arguments
```

---

### Q11 (Medium) -- Code Writing

Write a decorator called `retry` that retries a function up to `max_attempts` times if it raises an exception. It should accept `max_attempts` as a parameter (default 3). Print the attempt number and exception on each failure. If all attempts fail, re-raise the last exception.

```python
@retry(max_attempts=3)
def flaky_api_call() -> str:
    ...
```

---

### Q12 (Hard) -- Code Writing

Implement a function `compose` that takes any number of single-argument functions and returns a new function that applies them right-to-left (mathematical function composition). Include type hints using `Callable`.

```python
# Usage:
add_one = lambda x: x + 1
double = lambda x: x * 2
square = lambda x: x ** 2

transform = compose(square, double, add_one)
print(transform(3))  # square(double(add_one(3))) = square(double(4)) = square(8) = 64
```

---

## Module 05: OOP and Protocols (3 questions)

### Q13 (Easy) -- Multiple Choice

Which Python feature is the closest equivalent to Swift's `protocol`?

```python
A) Abstract Base Class (ABC) only
B) typing.Protocol only
C) Both ABC and typing.Protocol, but typing.Protocol supports structural subtyping
D) Python does not have any protocol equivalent
```

---

### Q14 (Medium) -- Code Writing

Create a `Temperature` dataclass that stores a value in Celsius and provides:
- A `to_fahrenheit()` method
- A `from_fahrenheit` classmethod (alternative constructor)
- Proper `__str__` output (e.g., `"25.0 C"`)
- Comparison operators via `order=True`
- The class should be frozen (immutable)

---

### Q15 (Hard) -- Code Writing

Using `typing.Protocol`, define a `Drawable` protocol with a `draw(canvas: str) -> str` method. Then create two classes (`Circle` and `Rectangle`) that conform to this protocol WITHOUT inheriting from it. Write a function `render_all` that takes a list of `Drawable` objects and calls `draw` on each. This demonstrates structural subtyping -- explain in a comment how this differs from Swift's protocol conformance.

---

## Module 06: Advanced Python (3 questions)

### Q16 (Medium) -- Short Answer

Explain what a generator is in Python and how it differs from a regular function that returns a list. What is the `yield` keyword doing? What is the Swift equivalent (if any)? Describe a situation where a generator is significantly better than returning a list.

---

### Q17 (Hard) -- Code Writing

Write a context manager class called `Timer` that measures and prints the elapsed time of a code block. Implement it using both approaches:

1. A class with `__enter__` and `__exit__` methods
2. A function using `@contextmanager` from `contextlib`

```python
# Usage:
with Timer("data processing"):
    process_data()
# Output: "data processing: 1.234s"
```

---

### Q18 (Hard) -- Code Writing

Write a `cached_property` descriptor (do NOT use `functools.cached_property`) that caches the result of a method call on first access and returns the cached value on subsequent accesses. The descriptor should store the cached value on the instance, not on the descriptor itself.

```python
class DataLoader:
    @cached_property
    def data(self) -> list[int]:
        print("Loading data...")
        return [1, 2, 3]

loader = DataLoader()
print(loader.data)  # prints "Loading data..." then [1, 2, 3]
print(loader.data)  # prints [1, 2, 3] only (cached)
```

---

## Module 07: Error Handling and I/O (3 questions)

### Q19 (Easy) -- Multiple Choice

What is the Python equivalent of Swift's `defer { file.close() }` pattern?

```python
A) try/finally
B) with statement (context manager)
C) atexit.register()
D) Both A and B
```

---

### Q20 (Medium) -- Code Writing

Write a function `safe_read_json(path: Path) -> dict | None` that:
- Uses `pathlib.Path` for file operations
- Reads and parses a JSON file
- Returns `None` (not crashes) if the file does not exist
- Returns `None` if the JSON is malformed
- Logs a warning message for each error case using the `logging` module
- Uses type hints throughout

---

### Q21 (Easy) -- Short Answer

Explain the difference between Python's `pathlib.Path` and `os.path`. Why is `pathlib` generally preferred in modern Python? How does it compare to Swift's `FileManager` and `URL` for file operations? Give 3 examples of common file operations using `pathlib`.

---

## Module 08: Modules, Packages, and Tooling (3 questions)

### Q22 (Easy) -- Multiple Choice

What file makes a directory a Python package (prior to namespace packages)?

```
A) package.json
B) __init__.py
C) setup.py
D) __main__.py
```

---

### Q23 (Medium) -- Short Answer

Explain the difference between `ruff check` and `ruff format`. What does each tool do? How do they compare to SwiftLint and swift-format? What is the purpose of the `[tool.ruff]` section in `pyproject.toml`, and what are 3 useful ruff rules you would enable?

---

### Q24 (Hard) -- Short Answer

Explain Python's module resolution order. When you write `import foo`, what sequence of locations does Python search? What is `sys.path`, how is it constructed, and how do virtual environments modify it? How does this compare to Swift's module system with SPM?

---

## Module 09: Testing with pytest (3 questions)

### Q25 (Easy) -- Multiple Choice

What does `@pytest.mark.parametrize` do?

```python
A) Runs the test in parallel across multiple cores
B) Runs the same test function with different input/output combinations
C) Marks the test as parameterized so it is skipped by default
D) Passes command-line parameters to the test function
```

---

### Q26 (Medium) -- Code Writing

Write a pytest test class `TestStack` that tests a simple `Stack` implementation. Include:
- A fixture that creates a pre-populated stack
- Tests for `push`, `pop`, `peek`, and `is_empty`
- A test using `pytest.raises` for popping from an empty stack
- A parametrized test for pushing multiple different value types

Assume this `Stack` interface:

```python
class Stack:
    def push(self, item: Any) -> None: ...
    def pop(self) -> Any: ...
    def peek(self) -> Any: ...
    def is_empty(self) -> bool: ...
```

---

### Q27 (Medium) -- Short Answer

Compare pytest fixtures with Swift's XCTest `setUp()` / `tearDown()` methods. What advantages do fixtures provide? Explain fixture scopes (`function`, `class`, `module`, `session`) with an example of when you would use each. What is `conftest.py` and why is it useful?

---

## Module 10: Async and Concurrency (3 questions)

### Q28 (Medium) -- Short Answer

Explain the difference between `asyncio.gather()` and `asyncio.TaskGroup()`. When would you use each? How does this compare to Swift's `async let` and `withTaskGroup`?

---

### Q29 (Hard) -- Code Writing

Write an async function `fetch_all_urls(urls: list[str]) -> list[str]` that:
- Uses `aiohttp` to fetch multiple URLs concurrently
- Returns the response text for each URL
- Handles individual request failures gracefully (returns an error message string for failed URLs instead of crashing)
- Uses `asyncio.TaskGroup` (Python 3.11+)
- Includes proper type hints

---

### Q30 (Hard) -- Short Answer

Explain the Global Interpreter Lock (GIL) in CPython. How does it affect multithreading vs. multiprocessing? When is `threading` still useful despite the GIL? How does `asyncio` relate to the GIL? Compare Python's concurrency model to Swift's actor-based concurrency model (Swift 5.5+ structured concurrency).

---

---

# Answer Key

---

## Q1 -- Answer: D

Python has no built-in constant enforcement. By convention, `UPPER_SNAKE_CASE` names signal "treat this as a constant," but nothing prevents reassignment. The `typing.Final` annotation adds type-checker enforcement but not runtime prevention. This is a notable difference from Swift's strict `let` vs. `var` distinction.

---

## Q2 -- Answer

`==` checks **value equality** (calls `__eq__`), while `is` checks **identity** (same object in memory).

- Swift comparison: `==` in Python is like `==` in Swift (Equatable). `is` in Python is like `===` in Swift (identity comparison for reference types).

Example:

```python
a = [1, 2, 3]
b = [1, 2, 3]

a == b   # True  -- same values
a is b   # False -- different objects in memory

c = a
a is c   # True  -- same object
```

---

## Q3 -- Answer

```python
def parse_value(text: str) -> int | float | str:
    """Parse a string into the most specific numeric type possible.

    Tries int first, then float, then returns the original string.

    Args:
        text: The string to parse.

    Returns:
        An int if the string represents a whole number, a float if it
        represents a decimal number, or the original string otherwise.
    """
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text
```

---

## Q4 -- Answer: B

In Python's `match/case` (structural pattern matching, added in 3.10), the wildcard pattern `case _:` serves as the default/catch-all case, equivalent to Swift's `default:` in a switch statement.

---

## Q5 -- Answer

```python
from enum import Enum

class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

def describe(direction: Direction) -> str:
    match direction:
        case Direction.NORTH:
            return "Going up"
        case Direction.SOUTH:
            return "Going down"
        case Direction.EAST | Direction.WEST:
            return "Going sideways"
```

---

## Q6 -- Answer

**`for` loop**: Iterates over an iterable (list, range, generator, etc.). Python's `for` is always a for-each loop (like Swift's `for item in collection`). There is no C-style `for(i=0; i<n; i++)`.

**`while` loop**: Repeats as long as a condition is true. Preferred when: (1) you do not know the number of iterations in advance, (2) you are waiting for a condition to change (e.g., reading until EOF), or (3) implementing retry logic.

**`for...else` / `while...else`**: The `else` block executes only if the loop completed normally (was NOT terminated by `break`). This is useful for search patterns:

```python
for item in collection:
    if item == target:
        print("Found!")
        break
else:
    print("Not found.")  # Only runs if break was never hit
```

Swift has no direct equivalent to `for...else`.

---

## Q7 -- Answer: C

`{"a", "b", "c"}` is a Python `set` literal -- unordered, unique elements, like Swift's `Set<String>`. Option A is a list (ordered, duplicates allowed), B is a tuple (ordered, immutable), and D is a dict.

---

## Q8 -- Answer

```python
departments = {emp["department"] for emp in employees}

avg_salaries = {
    dept: sum(e["salary"] for e in employees if e["department"] == dept)
    / sum(1 for e in employees if e["department"] == dept)
    for dept in departments
}
# Result: {"Engineering": 120000.0, "Marketing": 85000.0}
```

Alternative (more efficient with a helper):

```python
from collections import defaultdict

dept_salaries: dict[str, list[int]] = defaultdict(list)
for emp in employees:
    dept_salaries[emp["department"]].append(emp["salary"])

avg_salaries = {dept: sum(s) / len(s) for dept, s in dept_salaries.items()}
```

---

## Q9 -- Answer

**Mutability**: Lists are mutable (`append`, `remove`, `sort` in-place). Tuples are immutable (cannot be changed after creation).

**Hashability**: Tuples (containing only hashable elements) are hashable and can be used as dict keys or set members. Lists are never hashable.

**Performance**: Tuples are slightly faster to create and iterate. They use less memory because Python can optimize their storage (fixed size).

**Memory**: A tuple of N elements uses less memory than a list of N elements because lists over-allocate to support `append()`.

**Use cases**:
- **List**: Homogeneous collections that change (e.g., a list of scores).
- **Tuple**: Heterogeneous fixed records (e.g., `(name, age, city)`) or dictionary keys.

**NamedTuple vs. dataclass**: Use `NamedTuple` when you want immutability, hashability, tuple unpacking, and minimal overhead. Use `dataclass` when you want mutability, default values, `__post_init__`, inheritance, or more complex behavior. `NamedTuple` is a tuple subclass; `dataclass` is a regular class with generated methods.

---

## Q10 -- Answer: C

The bare `*` in the parameter list means "everything after this must be passed as a keyword argument." So `greet("Alice", greeting="Hi")` works, but `greet("Alice", "Hi")` raises a `TypeError`. This is similar to Swift's argument labels, which enforce named parameters at the call site.

---

## Q11 -- Answer

```python
import functools
from typing import Any, Callable, TypeVar
from collections.abc import Callable as CallableABC

F = TypeVar("F", bound=Callable[..., Any])

def retry(max_attempts: int = 3) -> Callable[[F], F]:
    """Decorator that retries a function up to max_attempts times."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    print(f"Attempt {attempt}/{max_attempts} failed: {exc}")
            raise last_exception  # type: ignore[misc]
        return wrapper  # type: ignore[return-value]
    return decorator
```

---

## Q12 -- Answer

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def compose(*functions: Callable[[T], T]) -> Callable[[T], T]:
    """Compose functions right-to-left (mathematical composition).

    compose(f, g, h)(x) == f(g(h(x)))
    """
    def composed(x: T) -> T:
        result = x
        for fn in reversed(functions):
            result = fn(result)
        return result
    return composed
```

---

## Q13 -- Answer: C

Both `ABC` and `typing.Protocol` serve as Python's answer to Swift protocols, but `typing.Protocol` is generally closer because it supports **structural subtyping** (duck typing with type-checker support). A class does not need to explicitly inherit from a `Protocol` to satisfy it -- it just needs to have the right methods. This is similar to how Swift protocols work with `@objc optional` methods, though Swift still requires explicit conformance declarations.

---

## Q14 -- Answer

```python
from dataclasses import dataclass

@dataclass(frozen=True, order=True)
class Temperature:
    celsius: float

    def to_fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32

    @classmethod
    def from_fahrenheit(cls, fahrenheit: float) -> "Temperature":
        return cls(celsius=(fahrenheit - 32) * 5 / 9)

    def __str__(self) -> str:
        return f"{self.celsius:.1f} C"
```

---

## Q15 -- Answer

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self, canvas: str) -> str: ...

class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def draw(self, canvas: str) -> str:
        return f"{canvas}: Circle(r={self.radius})"

class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def draw(self, canvas: str) -> str:
        return f"{canvas}: Rectangle({self.width}x{self.height})"

def render_all(drawables: list[Drawable], canvas: str) -> list[str]:
    return [d.draw(canvas) for d in drawables]

# Structural subtyping: Circle and Rectangle satisfy the Drawable protocol
# WITHOUT inheriting from it. Python's typing.Protocol checks for the
# presence of the required methods/attributes at type-check time.
#
# In Swift, you MUST explicitly declare conformance:
#     class Circle: Drawable { ... }
# In Python with Protocol, conformance is implicit -- if it has the
# right methods, it IS Drawable. This is "duck typing" with static
# type checker support.
```

---

## Q16 -- Answer

A **generator** is a function that uses `yield` to produce values one at a time, suspending its execution state between each yield. When called, it returns a generator iterator rather than computing all values at once.

**Difference from a list-returning function**:
- A list function computes ALL values, stores them in memory, then returns.
- A generator computes one value at a time, yielding it lazily. Memory usage is O(1) regardless of how many values are produced.

**`yield`** pauses the function, saves its local state, and produces a value. When `next()` is called again, execution resumes right after the `yield`.

**Swift equivalent**: Swift has `AsyncSequence` and `AsyncStream` for async lazy sequences, but no direct synchronous generator equivalent. The closest is a custom `Sequence`/`IteratorProtocol` implementation.

**When generators are significantly better**: Reading a 10GB log file line by line. A list approach would load all lines into memory (crash). A generator processes one line at a time:

```python
def read_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.strip()
```

---

## Q17 -- Answer

```python
import time
from contextlib import contextmanager

# Approach 1: Class-based
class Timer:
    def __init__(self, label: str = "elapsed") -> None:
        self.label = label
        self.elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.elapsed = time.perf_counter() - self.start
        print(f"{self.label}: {self.elapsed:.3f}s")

# Approach 2: Function with @contextmanager
@contextmanager
def timer(label: str = "elapsed"):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.3f}s")
```

---

## Q18 -- Answer

```python
from typing import Any, Callable

class cached_property:
    """Descriptor that caches the result of a method on the instance."""

    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        self.attr_name = func.__name__

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        # Store result directly on the instance's __dict__
        value = self.func(obj)
        obj.__dict__[self.attr_name] = value
        return value
```

Key insight: After the first call, the value is stored in `obj.__dict__` under the same name as the descriptor. On subsequent accesses, Python's attribute lookup finds the instance attribute first (in `__dict__`) and never calls `__get__` again. This works because data descriptors (with `__set__`) take priority over instance attributes, but non-data descriptors (only `__get__`) do NOT -- so the instance dict wins.

---

## Q19 -- Answer: D

Both `try/finally` and the `with` statement (context manager) serve the purpose of Swift's `defer`. The `with` statement is preferred in modern Python because it is more concise and less error-prone. `try/finally` is the more general mechanism. The `with` statement combines resource acquisition and guaranteed cleanup into a single construct.

---

## Q20 -- Answer

```python
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def safe_read_json(path: Path) -> dict | None:
    """Read and parse a JSON file, returning None on any error.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed dict if successful, None if the file is missing or malformed.
    """
    if not path.exists():
        logger.warning("File not found: %s", path)
        return None

    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        if not isinstance(data, dict):
            logger.warning("JSON root is not a dict in: %s", path)
            return None
        return data
    except json.JSONDecodeError as exc:
        logger.warning("Malformed JSON in %s: %s", path, exc)
        return None
```

---

## Q21 -- Answer

**`pathlib.Path`** is an object-oriented API (introduced in Python 3.4) where paths are objects with methods. **`os.path`** is a functional API where paths are plain strings passed to functions.

`pathlib` is preferred because:
1. Paths are objects, not strings -- operator `/` joins paths: `Path("data") / "file.csv"`
2. Methods are discoverable and chainable: `path.read_text()`, `path.stem`, `path.suffix`
3. Cross-platform by default, similar to how Swift's `URL` abstracts file paths

**Swift comparison**: `pathlib.Path` is most like Swift's `URL(fileURLWithPath:)` combined with `FileManager`. Swift uses `URL` for path representation and `FileManager` for operations. Python's `pathlib` combines both into one object.

**3 common operations**:

```python
from pathlib import Path

# 1. Read a file
content = Path("data.txt").read_text(encoding="utf-8")

# 2. List all CSV files in a directory
csv_files = list(Path("data_dir").glob("*.csv"))

# 3. Create a directory (including parents)
Path("output/reports").mkdir(parents=True, exist_ok=True)
```

---

## Q22 -- Answer: B

`__init__.py` makes a directory a Python package. It can be empty or contain package initialization code. This is similar to how Swift uses module maps or `Package.swift` to define module boundaries, though the mechanism is quite different. Note: PEP 420 introduced namespace packages (no `__init__.py` required), but explicit packages with `__init__.py` are still the standard practice.

---

## Q23 -- Answer

**`ruff check`**: A linter that detects code quality issues, potential bugs, style violations, and import ordering problems. Similar to SwiftLint. It does NOT modify code by default (use `--fix` to auto-fix).

**`ruff format`**: An opinionated code formatter (like `black`) that rewrites code to a consistent style. Similar to `swift-format`. It modifies files in place.

**Comparison to Swift tools**:
- `ruff check` ~ SwiftLint (detects issues, suggests fixes)
- `ruff format` ~ swift-format (reformats code to a standard style)
- Key difference: ruff handles both roles in one tool and is extremely fast (written in Rust)

**`[tool.ruff]` in `pyproject.toml`**: Configures ruff's behavior project-wide, including target Python version, line length, enabled/disabled rules, and per-file overrides.

**3 useful rules**:
1. `"I"` (isort) -- Sorts and organizes import statements automatically
2. `"UP"` (pyupgrade) -- Modernizes syntax to use newer Python features (e.g., `dict()` to `{}`)
3. `"B"` (flake8-bugbear) -- Catches common bugs and design problems like mutable default arguments

---

## Q24 -- Answer

**Module resolution order** when you write `import foo`:

1. **`sys.modules` cache** -- If already imported, return the cached module
2. **Built-in modules** -- Modules compiled into the Python interpreter (e.g., `sys`, `builtins`)
3. **`sys.path` search** -- Searches directories/zip files in order:
   a. The directory of the script being run (or CWD for interactive)
   b. `PYTHONPATH` environment variable entries
   c. Installation-dependent defaults (site-packages, standard library)

**`sys.path` construction**:
1. Script directory (or `""` for interactive)
2. `PYTHONPATH` entries
3. Default paths from the Python installation

**Virtual environments** modify `sys.path` by:
- Replacing the system `site-packages` with the venv's `site-packages`
- Keeping the standard library paths intact
- Effectively isolating third-party packages per project

**Comparison to Swift/SPM**:
- Swift modules are compiled and linked; Python modules are found at runtime via file-system search
- SPM uses `Package.swift` to declare explicit dependencies; Python uses `pyproject.toml`/`requirements.txt` plus a package installer (pip/uv)
- Swift has no equivalent of `sys.path` -- module resolution is handled at compile time by the build system

---

## Q25 -- Answer: B

`@pytest.mark.parametrize` runs the same test function multiple times with different sets of arguments. Each parameter combination becomes a separate test case in the output. This is similar to Swift's approach of writing separate test methods, but more concise. It avoids code duplication when testing the same logic with different inputs.

---

## Q26 -- Answer

```python
from typing import Any

import pytest

# Assume Stack is imported from the module under test.

class TestStack:
    @pytest.fixture
    def empty_stack(self) -> Stack:
        return Stack()

    @pytest.fixture
    def populated_stack(self) -> Stack:
        s = Stack()
        s.push(1)
        s.push(2)
        s.push(3)
        return s

    def test_is_empty_on_new_stack(self, empty_stack: Stack) -> None:
        assert empty_stack.is_empty()

    def test_push_makes_non_empty(self, empty_stack: Stack) -> None:
        empty_stack.push(42)
        assert not empty_stack.is_empty()

    def test_pop_returns_last_pushed(self, populated_stack: Stack) -> None:
        assert populated_stack.pop() == 3

    def test_peek_does_not_remove(self, populated_stack: Stack) -> None:
        val = populated_stack.peek()
        assert val == 3
        assert populated_stack.peek() == 3  # still there

    def test_pop_empty_raises(self, empty_stack: Stack) -> None:
        with pytest.raises(IndexError):
            empty_stack.pop()

    @pytest.mark.parametrize(
        "value",
        [42, "hello", 3.14, None, [1, 2, 3]],
        ids=["int", "str", "float", "none", "list"],
    )
    def test_push_various_types(self, empty_stack: Stack, value: Any) -> None:
        empty_stack.push(value)
        assert empty_stack.peek() == value
```

---

## Q27 -- Answer

**XCTest `setUp()`/`tearDown()` vs. pytest fixtures**:

- XCTest runs `setUp()` before EVERY test and `tearDown()` after. All setup is in one method, even if only some tests need it.
- pytest fixtures are **composable** and **on-demand**: each test declares which fixtures it needs via function parameters. Only the required fixtures run.

**Advantages of fixtures**:
1. **Composability** -- Fixtures can depend on other fixtures, building a dependency graph
2. **Scope control** -- Choose how often setup/teardown occurs
3. **Explicit dependencies** -- Test signatures declare exactly what they need
4. **Reusability** -- Fixtures in `conftest.py` are shared across multiple test files

**Fixture scopes**:
- `function` (default) -- Fresh for every test. Example: a temporary database record.
- `class` -- Shared across all tests in a test class. Example: an expensive object that tests only read.
- `module` -- Shared across all tests in a file. Example: a database connection per test file.
- `session` -- Created once for the entire test run. Example: spinning up a Docker container.

**`conftest.py`**: A special file that pytest discovers automatically. Fixtures defined in `conftest.py` are available to all tests in the same directory and subdirectories WITHOUT importing them. It acts as a shared fixture registry, similar to how Swift test targets can share test utilities, but with automatic discovery.

---

## Q28 -- Answer

**`asyncio.gather()`**: Runs multiple coroutines concurrently and collects results. If one fails, the others may or may not be cancelled depending on `return_exceptions`. It is a flat API -- you pass all tasks at once.

**`asyncio.TaskGroup`** (Python 3.11+): A structured concurrency primitive. Tasks are created inside an `async with` block, and if ANY task raises an exception, all other tasks in the group are cancelled. It guarantees that all tasks have finished (or been cancelled) when the block exits.

**Comparison**:
- `gather` ~ loosely structured, results collected in order
- `TaskGroup` ~ strictly structured, guaranteed cleanup, exception propagation

**Swift equivalents**:
- `asyncio.gather()` ~ `async let` bindings (concurrent but independent)
- `asyncio.TaskGroup` ~ `withTaskGroup` / `withThrowingTaskGroup` (structured, managed lifecycle)

Swift's `withTaskGroup` is the closest to `TaskGroup` -- both enforce structured concurrency where child tasks cannot outlive their parent scope.

---

## Q29 -- Answer

```python
import asyncio

import aiohttp

async def fetch_all_urls(urls: list[str]) -> list[str]:
    """Fetch multiple URLs concurrently, returning response text or error messages."""
    results: dict[int, str] = {}

    async with aiohttp.ClientSession() as session:
        async with asyncio.TaskGroup() as tg:
            for i, url in enumerate(urls):
                tg.create_task(_fetch_one(session, url, i, results))

    # Return results in original order.
    return [results[i] for i in range(len(urls))]


async def _fetch_one(
    session: aiohttp.ClientSession,
    url: str,
    index: int,
    results: dict[int, str],
) -> None:
    """Fetch a single URL and store the result or error message."""
    try:
        async with session.get(url) as response:
            results[index] = await response.text()
    except Exception as exc:
        results[index] = f"Error fetching {url}: {exc}"
```

Note: Because `TaskGroup` cancels all tasks on any unhandled exception, individual exceptions must be caught inside each task (as shown above) to prevent one failure from cancelling the others.

---

## Q30 -- Answer

**The GIL (Global Interpreter Lock)**: A mutex in CPython that ensures only one thread executes Python bytecode at a time. It simplifies memory management (reference counting is not thread-safe) but limits true parallelism for CPU-bound work.

**Multithreading vs. multiprocessing**:
- **Threading**: Multiple threads share memory but the GIL means only one runs Python code at a time. CPU-bound tasks see NO speedup.
- **Multiprocessing**: Spawns separate processes, each with its own GIL. True parallelism for CPU-bound work, but with higher memory overhead and IPC costs.

**When threading is still useful**: I/O-bound tasks (network requests, file reads, database queries). While one thread waits for I/O, another can run Python code. The GIL is released during I/O operations.

**asyncio and the GIL**: `asyncio` is single-threaded and cooperative. It does NOT fight the GIL -- it works within it. Coroutines yield control voluntarily at `await` points. This is highly efficient for I/O-bound workloads because there is zero thread-switching overhead.

**Comparison to Swift's concurrency model**:
- Swift uses **actors** for safe mutable state (no shared mutable state by default). Python relies on the GIL or explicit locks.
- Swift's `async/await` uses a cooperative thread pool (multiple threads). Python's `asyncio` runs on a single thread.
- Swift actors isolate state at the language level. Python has no equivalent -- you use locks, queues, or multiprocessing for safety.
- Swift's model is fundamentally designed to avoid data races at compile time. Python's model relies on runtime conventions and the GIL as a safety net.
- PEP 703 (accepted) proposes removing the GIL from CPython in the future, which will make Python's concurrency model more similar to other languages but will require explicit synchronization.
