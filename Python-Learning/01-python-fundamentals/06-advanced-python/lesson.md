# Module 06: Advanced Python

## Table of Contents

1. [Decorators](#1-decorators)
2. [Generators](#2-generators)
3. [Context Managers](#3-context-managers)
4. [Iterators](#4-iterators)
5. [Type Hints Deep Dive](#5-type-hints-deep-dive)
6. [Pydantic v2](#6-pydantic-v2)

---

## 1. Decorators

Decorators are one of Python's most powerful features. A decorator is a function that takes
a function (or class) and returns a modified version. They use the `@` syntax, which is
syntactic sugar for wrapping.

### Basic Function Decorator

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Before calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"After calling {func.__name__}")
        return result
    return wrapper

@my_decorator
def say_hello(name: str) -> str:
    return f"Hello, {name}!"

# @my_decorator is equivalent to:
# say_hello = my_decorator(say_hello)

print(say_hello("Alice"))
# Before calling say_hello
# After calling say_hello
# Hello, Alice!
```

### Preserving Function Metadata with functools.wraps

Without `@wraps`, the decorated function loses its name, docstring, and other metadata.

```python
from functools import wraps

def timer(func):
    @wraps(func)  # Preserves func's __name__, __doc__, __module__, etc.
    def wrapper(*args, **kwargs):
        import time
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    """This function is intentionally slow."""
    import time
    time.sleep(0.1)
    return 42

print(slow_function.__name__)  # slow_function (not 'wrapper')
print(slow_function.__doc__)   # This function is intentionally slow.
```

### Practical Decorator: Retry

```python
from functools import wraps
import time

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator factory that retries a function on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt}/{max_attempts} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unreliable_api_call():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Server unavailable")
    return {"status": "ok"}
```

### Decorators with Arguments

When a decorator needs arguments, you need a three-level nesting pattern: the outer function
takes the arguments, the middle function takes the decorated function, and the inner function
replaces the decorated function.

```python
from functools import wraps

def log_calls(level: str = "INFO"):
    """Decorator factory -- takes arguments and returns a decorator."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[{level}] Calling {func.__name__}({args}, {kwargs})")
            result = func(*args, **kwargs)
            print(f"[{level}] {func.__name__} returned {result!r}")
            return result
        return wrapper
    return decorator

@log_calls(level="DEBUG")
def add(a: int, b: int) -> int:
    return a + b

add(3, 5)
# [DEBUG] Calling add((3, 5), {})
# [DEBUG] add returned 8
```

### Stacking Decorators

Decorators are applied bottom-up (the one closest to the function runs first).

```python
def bold(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

def italic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper

@bold
@italic
def greet(name: str) -> str:
    return f"Hello, {name}"

print(greet("Alice"))  # <b><i>Hello, Alice</i></b>
# Applied as: bold(italic(greet))
```

### Class Decorators

Decorators can also be applied to classes to modify or wrap them.

```python
def add_repr(cls):
    """Class decorator that adds a __repr__ method."""
    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items()
                         if not k.startswith("_"))
        return f"{cls.__name__}({attrs})"
    cls.__repr__ = __repr__
    return cls

@add_repr
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

print(User("Alice", 30))  # User(name='Alice', age=30)
```

### Class-Based Decorators

You can use a class as a decorator by implementing `__call__`:

```python
class CountCalls:
    """Decorator that counts how many times a function is called."""

    def __init__(self, func):
        self.func = func
        self.count = 0
        # Preserve function metadata
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} has been called {self.count} times")
        return self.func(*args, **kwargs)

@CountCalls
def say_hi():
    print("Hi!")

say_hi()  # say_hi has been called 1 times\nHi!
say_hi()  # say_hi has been called 2 times\nHi!
print(say_hi.count)  # 2
```

### Decorator with Optional Arguments

A flexible pattern that works both with and without parentheses:

```python
from functools import wraps

def validate_types(_func=None, *, strict: bool = False):
    """Works as @validate_types or @validate_types(strict=True)."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validation logic here
            return func(*args, **kwargs)
        return wrapper

    if _func is not None:
        # Called without parentheses: @validate_types
        return decorator(_func)
    # Called with parentheses: @validate_types(strict=True)
    return decorator

@validate_types
def f1(): pass

@validate_types(strict=True)
def f2(): pass
```

**Swift comparison:** Decorators are conceptually similar to Swift's **property wrappers**
(`@Published`, `@State`, `@Binding`), but more general -- they can wrap any function or class.

---

## 2. Generators

Generators are functions that produce a sequence of values lazily using `yield`. Instead of
computing and returning all values at once, they produce values one at a time, pausing between
each yield.

### Basic Generator

```python
def countdown(n: int):
    """Generator that counts down from n to 1."""
    while n > 0:
        yield n
        n -= 1

# Using the generator
for num in countdown(5):
    print(num)  # 5, 4, 3, 2, 1

# Generators are iterators -- they produce values lazily
gen = countdown(3)
print(next(gen))  # 3
print(next(gen))  # 2
print(next(gen))  # 1
# print(next(gen))  # StopIteration exception!
```

### How Generators Work

When you call a generator function, it does **not** execute the function body. Instead, it
returns a **generator object**. The body executes incrementally each time you call `next()`.

```python
def simple_gen():
    print("Step 1")
    yield "a"
    print("Step 2")
    yield "b"
    print("Step 3")
    yield "c"
    print("Done")

gen = simple_gen()
# Nothing printed yet!

print(next(gen))
# Step 1
# a

print(next(gen))
# Step 2
# b

print(next(gen))
# Step 3
# c

# next(gen) would print "Done" then raise StopIteration
```

### Practical: Reading Large Files

```python
def read_large_file(filepath: str, chunk_size: int = 1024):
    """Read a large file in chunks without loading it all into memory."""
    with open(filepath, "r") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

# Process a multi-gigabyte file with constant memory
# for chunk in read_large_file("huge_log.txt"):
#     process(chunk)
```

### Generator Expressions

Generator expressions are like list comprehensions but lazy -- they produce values on demand
without building the entire list in memory.

```python
# List comprehension -- creates entire list in memory
squares_list = [x ** 2 for x in range(1_000_000)]

# Generator expression -- creates values on demand
squares_gen = (x ** 2 for x in range(1_000_000))

# Sum of squares without storing all values
total = sum(x ** 2 for x in range(1_000_000))  # Parentheses optional in function call

# Memory comparison
import sys
print(sys.getsizeof(squares_list))  # ~8 MB
print(sys.getsizeof(squares_gen))   # ~200 bytes (constant!)
```

### yield from

`yield from` delegates to another generator, iterable, or sub-generator. It flattens nested
generators.

```python
def flatten(nested):
    """Flatten a nested list using yield from."""
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)  # Delegate to recursive call
        else:
            yield item

data = [1, [2, 3], [4, [5, 6]], 7]
print(list(flatten(data)))  # [1, 2, 3, 4, 5, 6, 7]


def chain(*iterables):
    """Like itertools.chain -- concatenate multiple iterables."""
    for iterable in iterables:
        yield from iterable

print(list(chain([1, 2], [3, 4], [5])))  # [1, 2, 3, 4, 5]
```

### itertools -- Generator Utilities

The `itertools` module provides a collection of fast, memory-efficient building blocks.

```python
import itertools

# count: infinite counter
for i in itertools.count(1):
    if i > 5: break
    print(i)  # 1, 2, 3, 4, 5

# cycle: infinite cycling through an iterable
colors = itertools.cycle(["red", "green", "blue"])
print([next(colors) for _ in range(7)])
# ['red', 'green', 'blue', 'red', 'green', 'blue', 'red']

# chain: concatenate iterables
print(list(itertools.chain([1, 2], [3, 4], [5])))  # [1, 2, 3, 4, 5]

# islice: slice an iterator (like list slicing but for any iterable)
print(list(itertools.islice(range(100), 5, 10)))  # [5, 6, 7, 8, 9]

# groupby: group consecutive elements
data = [("A", 1), ("A", 2), ("B", 3), ("B", 4), ("A", 5)]
for key, group in itertools.groupby(data, key=lambda x: x[0]):
    print(f"{key}: {list(group)}")
# A: [('A', 1), ('A', 2)]
# B: [('B', 3), ('B', 4)]
# A: [('A', 5)]

# product: cartesian product
print(list(itertools.product("AB", "12")))
# [('A', '1'), ('A', '2'), ('B', '1'), ('B', '2')]

# combinations and permutations
print(list(itertools.combinations([1, 2, 3], 2)))
# [(1, 2), (1, 3), (2, 3)]

print(list(itertools.permutations([1, 2, 3], 2)))
# [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]

# accumulate: running totals
print(list(itertools.accumulate([1, 2, 3, 4, 5])))
# [1, 3, 6, 10, 15]

# takewhile / dropwhile
print(list(itertools.takewhile(lambda x: x < 5, [1, 3, 5, 2, 1])))
# [1, 3]

print(list(itertools.dropwhile(lambda x: x < 5, [1, 3, 5, 2, 1])))
# [5, 2, 1]

# starmap: like map but unpacks arguments
print(list(itertools.starmap(pow, [(2, 3), (3, 2), (10, 3)])))
# [8, 9, 1000]

# batched (Python 3.12+)
# print(list(itertools.batched(range(10), 3)))
# [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
```

### Generator as Pipeline

Generators are perfect for data processing pipelines where each stage is lazy.

```python
def read_lines(filepath):
    with open(filepath) as f:
        for line in f:
            yield line.strip()

def filter_comments(lines):
    for line in lines:
        if not line.startswith("#"):
            yield line

def parse_csv(lines):
    for line in lines:
        yield line.split(",")

def extract_column(rows, col: int):
    for row in rows:
        if len(row) > col:
            yield row[col]

# Each stage is lazy -- processes one line at a time
# pipeline = extract_column(
#     parse_csv(
#         filter_comments(
#             read_lines("data.csv")
#         )
#     ),
#     col=2
# )
# for value in pipeline:
#     process(value)
```

---

## 3. Context Managers

Context managers ensure that resources are properly acquired and released using the
`with` statement. They guarantee cleanup even if exceptions occur.

### The with Statement

```python
# File handling -- the classic context manager
with open("example.txt", "w") as f:
    f.write("Hello, World!")
# f is automatically closed here, even if an exception occurred

# Without context manager (error-prone)
f = open("example.txt", "w")
try:
    f.write("Hello, World!")
finally:
    f.close()  # Must remember to close!
```

### Writing a Context Manager Class

Implement `__enter__` and `__exit__`:

```python
class DatabaseConnection:
    """Context manager for database connections."""

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string
        self.connection = None

    def __enter__(self):
        print(f"Connecting to {self.connection_string}")
        self.connection = {"status": "connected"}  # Simulated connection
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        self.connection = None
        # Return False (or None) to propagate exceptions
        # Return True to suppress exceptions
        return False


with DatabaseConnection("postgresql://localhost/mydb") as conn:
    print(f"Using connection: {conn}")
# Output:
# Connecting to postgresql://localhost/mydb
# Using connection: {'status': 'connected'}
# Closing connection
```

### The `__exit__` Method Parameters

```python
class SafeBlock:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Args:
            exc_type: Exception class (or None if no exception)
            exc_val: Exception instance (or None)
            exc_tb: Traceback (or None)

        Returns:
            True to suppress the exception, False to propagate it.
        """
        if exc_type is not None:
            print(f"Caught exception: {exc_type.__name__}: {exc_val}")
            return True  # Suppress the exception

with SafeBlock():
    raise ValueError("Something went wrong")

print("This still executes because the exception was suppressed")
```

### contextlib.contextmanager

A decorator that turns a generator function into a context manager. Much more concise
than writing a class.

```python
from contextlib import contextmanager

@contextmanager
def timer(label: str = "Block"):
    """Context manager that times a block of code."""
    import time
    start = time.perf_counter()
    try:
        yield  # The with-block runs here
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label} took {elapsed:.4f}s")

with timer("Computation"):
    total = sum(range(1_000_000))
# Computation took 0.0234s
```

```python
@contextmanager
def temporary_directory():
    """Create a temporary directory and clean it up afterward."""
    import tempfile
    import shutil

    tmpdir = tempfile.mkdtemp()
    try:
        yield tmpdir  # Provide the path to the with-block
    finally:
        shutil.rmtree(tmpdir)  # Clean up

with temporary_directory() as tmpdir:
    print(f"Working in {tmpdir}")
    # Create files, do work...
# Directory is automatically deleted
```

### Multiple Context Managers

```python
# Multiple context managers in one with statement
with open("input.txt") as fin, open("output.txt", "w") as fout:
    for line in fin:
        fout.write(line.upper())

# Python 3.10+ parenthesized syntax
with (
    open("input.txt") as fin,
    open("output.txt", "w") as fout,
):
    pass
```

### contextlib Utilities

```python
from contextlib import suppress, redirect_stdout, nullcontext
import io

# suppress: silently ignore specific exceptions
with suppress(FileNotFoundError):
    open("nonexistent.txt")  # No error raised

# redirect_stdout: capture print output
f = io.StringIO()
with redirect_stdout(f):
    print("captured!")
output = f.getvalue()  # "captured!\n"

# nullcontext: a no-op context manager (useful for conditional contexts)
def process(filepath=None):
    cm = open(filepath) if filepath else nullcontext("default data")
    with cm as data:
        print(data)
```

**Swift comparison:** Context managers are similar to Swift's `defer` statement for cleanup,
or the pattern of using `withCheckedContinuation` and similar scoped APIs. The key difference
is that Python context managers are reusable, composable objects.

---

## 4. Iterators

### The Iterator Protocol

An iterator is any object that implements:
- `__iter__()`: returns the iterator object itself
- `__next__()`: returns the next value, or raises `StopIteration` when exhausted

```python
class Countdown:
    """A custom iterator that counts down from n."""

    def __init__(self, n: int) -> None:
        self.n = n

    def __iter__(self):
        return self  # Iterator returns itself

    def __next__(self) -> int:
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

for num in Countdown(5):
    print(num)  # 5, 4, 3, 2, 1
```

### Iterable vs Iterator

An **iterable** is any object that can produce an iterator (has `__iter__`).
An **iterator** is an object that tracks state and produces values (has `__iter__` and `__next__`).

```python
# list is an iterable (not an iterator)
my_list = [1, 2, 3]

# iter() creates an iterator from an iterable
it = iter(my_list)
print(next(it))  # 1
print(next(it))  # 2
print(next(it))  # 3
```

### Custom Iterable (Separate Iterator)

```python
class NumberRange:
    """An iterable that produces a fresh iterator each time."""

    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end

    def __iter__(self):
        """Return a new iterator each time (allows multiple iterations)."""
        return NumberRangeIterator(self.start, self.end)


class NumberRangeIterator:
    """The iterator for NumberRange."""

    def __init__(self, current: int, end: int) -> None:
        self.current = current
        self.end = end

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.current >= self.end:
            raise StopIteration
        value = self.current
        self.current += 1
        return value


r = NumberRange(1, 5)

# Can iterate multiple times (creates new iterator each time)
print(list(r))  # [1, 2, 3, 4]
print(list(r))  # [1, 2, 3, 4] -- works again!

# Compare with a generator (which is exhausted after one pass)
gen = (x for x in range(1, 5))
print(list(gen))  # [1, 2, 3, 4]
print(list(gen))  # [] -- exhausted!
```

### Infinite Iterators

```python
class Fibonacci:
    """Infinite Fibonacci iterator."""

    def __init__(self) -> None:
        self.a = 0
        self.b = 1

    def __iter__(self):
        return self

    def __next__(self) -> int:
        value = self.a
        self.a, self.b = self.b, self.a + self.b
        return value

# Use with islice to limit
import itertools
fib = Fibonacci()
first_10 = list(itertools.islice(fib, 10))
print(first_10)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

**Swift comparison:** Python's iterator protocol (`__iter__` / `__next__`) maps directly to
Swift's `IteratorProtocol` (`makeIterator()` / `next()`). Python's iterables correspond to
Swift's `Sequence` protocol.

---

## 5. Type Hints Deep Dive

Python's type hint system has grown significantly. Here's a comprehensive tour of the
typing module.

### Basic Types (Review)

```python
# Built-in types (Python 3.9+)
x: int = 42
y: float = 3.14
z: str = "hello"
flag: bool = True
data: bytes = b"raw"
nothing: None = None
```

### Collection Types

```python
# Python 3.9+ built-in generics
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95}
coords: tuple[float, float] = (1.0, 2.0)
variable_tuple: tuple[int, ...] = (1, 2, 3, 4)  # Variable-length
ids: set[int] = {1, 2, 3}
frozen: frozenset[str] = frozenset({"a", "b"})
```

### Union and Optional

```python
from typing import Optional

# Union: either type (Python 3.10+ syntax)
value: int | str = 42
value = "hello"  # Also valid

# Optional: shorthand for X | None
name: str | None = None  # Modern syntax
name: Optional[str] = None  # Older syntax (equivalent)

def find(items: list[int], target: int) -> int | None:
    try:
        return items.index(target)
    except ValueError:
        return None
```

### TypeVar and Generic

```python
from typing import TypeVar, Generic

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    """Return first element or None -- type-safe."""
    return items[0] if items else None

# Constrained TypeVar
Number = TypeVar("Number", int, float)

def add(a: Number, b: Number) -> Number:
    return a + b

# Bound TypeVar
from typing import Comparable
S = TypeVar("S", bound=str)  # Must be str or subclass
```

### Generic Classes

```python
from typing import TypeVar, Generic, Iterator

T = TypeVar("T")

class Stack(Generic[T]):
    """A type-safe stack."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(reversed(self._items))


# Type checker knows these are int stacks
stack: Stack[int] = Stack()
stack.push(1)
stack.push(2)
value: int = stack.pop()  # Type checker knows this is int
```

### Literal

```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    """Only accepts specific string values."""
    print(f"Mode: {mode}")

set_mode("read")   # OK
# set_mode("delete")  # Type error (caught by mypy)

# Literal with other types
Direction = Literal["N", "S", "E", "W"]
HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]
```

### TypeAlias

```python
from typing import TypeAlias

# Simple type aliases
UserId: TypeAlias = int
Coordinates: TypeAlias = tuple[float, float]
Matrix: TypeAlias = list[list[float]]
Handler: TypeAlias = Callable[[str, int], bool]
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

def process_user(user_id: UserId) -> None:
    pass
```

### ParamSpec and Concatenate

These are used for preserving parameter types when writing decorators.

```python
from typing import ParamSpec, Concatenate, TypeVar, Callable

P = ParamSpec("P")
T = TypeVar("T")

def log_call(func: Callable[P, T]) -> Callable[P, T]:
    """Decorator that preserves the exact function signature."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_call
def greet(name: str, excited: bool = False) -> str:
    return f"Hello, {name}{'!' if excited else '.'}"

# Type checker knows the signature is preserved:
# greet(name: str, excited: bool = False) -> str
```

### @overload

Declare multiple signatures for a single function:

```python
from typing import overload

@overload
def process(value: int) -> str: ...
@overload
def process(value: str) -> int: ...
@overload
def process(value: list[int]) -> list[str]: ...

def process(value):
    """Implementation handles all cases."""
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, str):
        return len(value)
    elif isinstance(value, list):
        return [str(x) for x in value]
```

### TypeGuard and TypeIs

```python
from typing import TypeGuard  # Python 3.10+

def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    """Type guard: narrows the type if True is returned."""
    return all(isinstance(x, str) for x in val)

def process_items(items: list[object]) -> None:
    if is_string_list(items):
        # Type checker now knows items is list[str]
        print(", ".join(items))
```

---

## 6. Pydantic v2

Pydantic is the most popular data validation library in Python. It uses type hints to define
data schemas and automatically validates, serializes, and deserializes data. Think of it as
Swift's `Codable` + validation on steroids.

### Basic Model

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int
    is_active: bool = True

# Validation happens automatically
user = User(name="Alice", email="alice@example.com", age=30)
print(user)           # name='Alice' email='alice@example.com' age=30 is_active=True
print(user.name)      # Alice
print(user.model_dump())  # {'name': 'Alice', 'email': 'alice@example.com', 'age': 30, 'is_active': True}

# Type coercion
user2 = User(name="Bob", email="bob@example.com", age="25")  # "25" -> 25
print(user2.age)      # 25 (int, not str)
print(type(user2.age))  # <class 'int'>

# Validation error
try:
    User(name="Charlie", email="c@c.com", age="not_a_number")
except Exception as e:
    print(e)  # validation error for age
```

### Field Configuration

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, description="Price in USD")
    quantity: int = Field(ge=0, default=0)
    tags: list[str] = Field(default_factory=list)
    sku: str = Field(pattern=r"^[A-Z]{2}-\d{4}$")  # Regex validation

product = Product(
    name="Widget",
    price=9.99,
    quantity=100,
    sku="AB-1234",
)

# Validation failures
try:
    Product(name="", price=-1, sku="invalid")
except Exception as e:
    print(e)  # Multiple validation errors
```

### Custom Validators

```python
from pydantic import BaseModel, field_validator, model_validator

class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    password_confirm: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.lower()

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v.lower()

    @model_validator(mode="after")
    def passwords_match(self) -> "UserRegistration":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self

user = UserRegistration(
    username="Alice123",
    email="Alice@Example.com",
    password="secret",
    password_confirm="secret",
)
print(user.username)  # alice123 (lowercased by validator)
print(user.email)     # alice@example.com
```

### model_config

```python
from pydantic import BaseModel, ConfigDict

class APIResponse(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,    # Strip whitespace from strings
        frozen=True,                   # Immutable (like frozen dataclass)
        extra="forbid",                # Forbid extra fields
        populate_by_name=True,         # Allow field names AND aliases
    )

    status_code: int = Field(alias="statusCode")
    message: str
    data: dict | None = None
```

### Nested Models

```python
from pydantic import BaseModel
from datetime import datetime

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class Company(BaseModel):
    name: str
    address: Address
    founded: datetime

class Employee(BaseModel):
    name: str
    email: str
    company: Company
    skills: list[str] = []

# Nested data is automatically validated
employee = Employee(
    name="Alice",
    email="alice@acme.com",
    company={
        "name": "Acme Corp",
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
        },
        "founded": "2020-01-15",
    },
    skills=["Python", "ML"],
)

print(employee.company.address.city)  # Springfield
print(type(employee.company.founded))  # <class 'datetime.datetime'>
```

### Serialization

```python
from pydantic import BaseModel

class Config(BaseModel):
    name: str
    debug: bool = False
    max_retries: int = 3

config = Config(name="production")

# To dict
d = config.model_dump()
print(d)  # {'name': 'production', 'debug': False, 'max_retries': 3}

# To dict (exclude defaults)
d = config.model_dump(exclude_defaults=True)
print(d)  # {'name': 'production'}

# To JSON string
j = config.model_dump_json()
print(j)  # '{"name":"production","debug":false,"max_retries":3}'

# To JSON with indentation
j = config.model_dump_json(indent=2)

# From dict
config2 = Config.model_validate({"name": "staging", "debug": True})

# From JSON string
config3 = Config.model_validate_json('{"name": "dev"}')

# Exclude specific fields
d = config.model_dump(exclude={"max_retries"})
```

### Pydantic with Enums

```python
from enum import Enum
from pydantic import BaseModel

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class User(BaseModel):
    name: str
    status: Status = Status.PENDING

user = User(name="Alice", status="active")  # String coerced to enum
print(user.status)        # Status.ACTIVE
print(user.status.value)  # active

d = user.model_dump()
print(d)  # {'name': 'Alice', 'status': 'active'}  -- enum serialized to value
```

### Practical: API Request/Response Models

```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskCreate(BaseModel):
    """Model for creating a new task (request body)."""
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    priority: Priority = Priority.MEDIUM
    due_date: datetime | None = None

class TaskResponse(BaseModel):
    """Model for task API response."""
    id: int
    title: str
    description: str
    priority: Priority
    due_date: datetime | None
    created_at: datetime
    completed: bool = False

# Validate incoming request
request_data = {
    "title": "Write documentation",
    "priority": "high",
    "due_date": "2024-12-31T23:59:59",
}
task = TaskCreate.model_validate(request_data)
print(task.priority)  # Priority.HIGH
print(task.due_date)  # 2024-12-31 23:59:59
```

---

## Quick Reference: Advanced Python Cheat Sheet

| Concept | Syntax | Swift Equivalent |
|---------|--------|-----------------|
| Decorator | `@my_decorator` | Property wrapper (`@State`) |
| Decorator with args | `@retry(max=3)` | `@Clamped(range: 0...100)` |
| Generator function | `def gen(): yield x` | `AsyncSequence` / custom Sequence |
| Generator expression | `(x for x in items)` | `.lazy.map { }` |
| Context manager (class) | `__enter__` / `__exit__` | `defer { }` / scoped APIs |
| Context manager (func) | `@contextmanager` | N/A |
| Iterator | `__iter__` / `__next__` | `IteratorProtocol` |
| Type alias | `TypeAlias = ...` | `typealias X = Y` |
| Generic class | `class Foo(Generic[T])` | `struct Foo<T>` |
| Union type | `int \| str` | Protocol or enum |
| Optional | `str \| None` | `String?` |
| Overloaded function | `@overload` | No equivalent (use generics) |
| Pydantic model | `class M(BaseModel)` | `Codable` struct |

---

## Key Takeaways for Swift Developers

1. **Decorators are everywhere** -- they're Python's version of meta-programming. Learn the three-level nesting pattern for parameterized decorators.
2. **Generators are lazy sequences** -- they're Python's equivalent of `lazy` + custom `Sequence` in Swift. They use constant memory.
3. **Context managers = resource management** -- think `defer` but structured and reusable. The `with` statement guarantees cleanup.
4. **Python's type system is optional** -- unlike Swift's enforced type system, Python type hints are for tooling (mypy, IDEs) and documentation. They are not enforced at runtime.
5. **Pydantic is your Codable** -- but much more powerful with built-in validation, coercion, and serialization. It's the de facto standard for data validation in Python.
6. **itertools is your best friend** -- memorize the key functions (`chain`, `islice`, `groupby`, `product`, `combinations`). They appear constantly in real-world Python.
7. **ParamSpec preserves decorator signatures** -- use it when writing decorators that need to preserve type information.

---

## Next Steps

Module 07 covers Error Handling and I/O -- how Python's exception system, file handling, and
pathlib compare to Swift's do/try/catch, Result type, and FileManager. These build naturally
on the context managers and patterns covered here.
