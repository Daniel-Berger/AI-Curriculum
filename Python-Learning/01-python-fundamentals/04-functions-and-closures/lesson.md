# Module 04: Functions and Closures

## Table of Contents

1. [Function Basics](#1-function-basics)
2. [Return Values](#2-return-values)
3. [Default Parameters](#3-default-parameters)
4. [*args and **kwargs](#4-args-and-kwargs)
5. [Keyword-Only and Positional-Only Arguments](#5-keyword-only-and-positional-only-arguments)
6. [Lambda Functions](#6-lambda-functions)
7. [map, filter, and reduce](#7-map-filter-and-reduce)
8. [functools: partial, lru_cache, and More](#8-functools-partial-lru_cache-and-more)
9. [Closures and nonlocal](#9-closures-and-nonlocal)
10. [Higher-Order Functions and First-Class Functions](#10-higher-order-functions-and-first-class-functions)
11. [Type Hints for Functions](#11-type-hints-for-functions)
12. [Docstrings Conventions](#12-docstrings-conventions)

---

## 1. Function Basics

### The `def` Keyword

In Python, functions are defined with the `def` keyword. Unlike Swift's `func`, Python uses
indentation (not braces) to delimit the function body.

```python
# Python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

```swift
// Swift equivalent
func greet(name: String) -> String {
    return "Hello, \(name)!"
}
```

### Key Differences from Swift

- **No braces** -- the function body is defined by indentation (typically 4 spaces).
- **No argument labels** by default -- Python does not have Swift's external/internal parameter name distinction.
- **No `func` keyword** -- Python uses `def` (short for "define").
- **Colon after the signature** -- the `:` starts the indented block.

### Basic Function Examples

```python
# Simple function with no parameters
def say_hello() -> None:
    print("Hello, World!")

# Function with parameters
def add(a: int, b: int) -> int:
    return a + b

# Function with no return value (implicitly returns None)
def log_message(message: str) -> None:
    print(f"[LOG] {message}")

# Calling functions
say_hello()                 # Hello, World!
result = add(3, 5)          # 8
log_message("Started")      # [LOG] Started
```

### Functions Are Objects

In Python, everything is an object -- including functions. This means you can assign functions
to variables, pass them as arguments, and return them from other functions.

```python
def multiply(a: int, b: int) -> int:
    return a * b

# Assign function to a variable
op = multiply
print(op(3, 4))  # 12

# Check the type
print(type(multiply))  # <class 'function'>
```

---

## 2. Return Values

### Single Return Values

```python
def square(x: int) -> int:
    return x * x

result = square(5)  # 25
```

### Multiple Return Values (Tuples)

Python functions can return multiple values by returning a tuple. This is similar to Swift's
tuple returns, but Python makes it even more natural with automatic packing/unpacking.

```python
def divide_and_remainder(a: int, b: int) -> tuple[int, int]:
    return a // b, a % b

# Tuple unpacking (like Swift's tuple destructuring)
quotient, remainder = divide_and_remainder(17, 5)
print(quotient)    # 3
print(remainder)   # 2

# You can also capture as a single tuple
result = divide_and_remainder(17, 5)
print(result)      # (3, 2)
```

### Returning None

If a function has no `return` statement, or uses `return` without a value, it returns `None`
(Python's equivalent of Swift's `Void` or `nil` for "no meaningful value").

```python
def greet_silently(name: str) -> None:
    # No return statement -- returns None implicitly
    _ = f"Hello, {name}"

result = greet_silently("Alice")
print(result)  # None
```

### Early Returns

```python
def find_first_negative(numbers: list[int]) -> int | None:
    for n in numbers:
        if n < 0:
            return n
    return None

print(find_first_negative([1, 2, -3, 4]))  # -3
print(find_first_negative([1, 2, 3]))       # None
```

---

## 3. Default Parameters

Python supports default parameter values, similar to Swift.

```python
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

print(greet("Alice"))                # Hello, Alice!
print(greet("Bob", "Hey"))           # Hey, Bob!
print(greet("Carol", greeting="Hi")) # Hi, Carol!
```

### The Mutable Default Argument Trap

**This is one of Python's most famous gotchas.** Default arguments are evaluated **once** when
the function is defined, not each time it is called. This means mutable defaults (like lists
or dicts) are shared across all calls.

```python
# BAD -- the list is shared across calls!
def append_to(item: int, target: list[int] = []) -> list[int]:
    target.append(item)
    return target

print(append_to(1))  # [1]
print(append_to(2))  # [1, 2]  -- Surprise! Not [2]!
print(append_to(3))  # [1, 2, 3]

# GOOD -- use None as sentinel and create a new list each time
def append_to_safe(item: int, target: list[int] | None = None) -> list[int]:
    if target is None:
        target = []
    target.append(item)
    return target

print(append_to_safe(1))  # [1]
print(append_to_safe(2))  # [2]  -- Correct!
```

**Swift comparison:** Swift doesn't have this problem because default expressions are evaluated
each time the function is called. This is a critical difference to internalize.

---

## 4. *args and **kwargs

Python provides two special syntaxes for accepting variable numbers of arguments:
- `*args` collects extra **positional** arguments into a tuple
- `**kwargs` collects extra **keyword** arguments into a dict

### *args (Variadic Positional Arguments)

```python
def sum_all(*args: int) -> int:
    """Sum any number of integers."""
    return sum(args)

print(sum_all(1, 2, 3))       # 6
print(sum_all(1, 2, 3, 4, 5)) # 15
print(sum_all())               # 0

# args is a tuple inside the function
def show_args(*args: str) -> None:
    print(type(args))  # <class 'tuple'>
    for i, arg in enumerate(args):
        print(f"  arg[{i}] = {arg}")

show_args("a", "b", "c")
```

**Swift comparison:** This is similar to Swift's variadic parameters (`func sum(_ values: Int...)`),
except `args` is a tuple, not an Array.

### **kwargs (Variadic Keyword Arguments)

```python
def build_profile(**kwargs: str) -> dict[str, str]:
    """Build a user profile from keyword arguments."""
    return kwargs

profile = build_profile(name="Alice", role="Engineer", city="NYC")
print(profile)  # {'name': 'Alice', 'role': 'Engineer', 'city': 'NYC'}

# kwargs is a dict inside the function
def show_kwargs(**kwargs: str) -> None:
    print(type(kwargs))  # <class 'dict'>
    for key, value in kwargs.items():
        print(f"  {key} = {value}")

show_kwargs(x="1", y="2")
```

**Swift has no direct equivalent** of `**kwargs`. The closest pattern would be passing a
`[String: Any]` dictionary.

### Combining Regular, *args, and **kwargs

```python
def make_request(url: str, *path_segments: str, **params: str) -> str:
    path = "/".join(path_segments)
    query = "&".join(f"{k}={v}" for k, v in params.items())
    full_url = f"{url}/{path}"
    if query:
        full_url += f"?{query}"
    return full_url

result = make_request(
    "https://api.example.com",
    "users", "42", "posts",           # *args
    page="1", limit="10"               # **kwargs
)
print(result)  # https://api.example.com/users/42/posts?page=1&limit=10
```

### Unpacking with * and **

You can also use `*` and `**` to **unpack** sequences and dicts when calling functions.

```python
def add(a: int, b: int, c: int) -> int:
    return a + b + c

numbers = [1, 2, 3]
print(add(*numbers))  # 6  -- unpacks list into positional args

config = {"a": 10, "b": 20, "c": 30}
print(add(**config))  # 60  -- unpacks dict into keyword args
```

---

## 5. Keyword-Only and Positional-Only Arguments

Python 3 introduced fine-grained control over how arguments can be passed.

### Keyword-Only Arguments (after `*`)

Parameters after a bare `*` **must** be passed as keyword arguments.

```python
def fetch(url: str, *, timeout: int = 30, retries: int = 3) -> str:
    """The * forces timeout and retries to be keyword-only."""
    return f"Fetching {url} (timeout={timeout}, retries={retries})"

# These work:
fetch("https://example.com")
fetch("https://example.com", timeout=10)
fetch("https://example.com", timeout=10, retries=5)

# This FAILS:
# fetch("https://example.com", 10, 5)  # TypeError!
```

This is extremely useful for API design -- it forces callers to be explicit about what they're
passing, making code more readable.

### Positional-Only Arguments (before `/`)

Parameters before a `/` **must** be passed positionally (Python 3.8+).

```python
def pow(base: float, exp: float, /) -> float:
    """base and exp must be passed positionally."""
    return base ** exp

# This works:
pow(2, 10)  # 1024

# This FAILS:
# pow(base=2, exp=10)  # TypeError!
```

### Combining Both

```python
def create_user(
    name: str,          # positional-only (before /)
    /,
    age: int,           # normal (positional or keyword)
    *,
    email: str,         # keyword-only (after *)
    admin: bool = False # keyword-only with default
) -> dict:
    return {"name": name, "age": age, "email": email, "admin": admin}

# Valid calls:
create_user("Alice", 30, email="alice@example.com")
create_user("Bob", age=25, email="bob@example.com")

# Invalid:
# create_user(name="Alice", age=30, email="alice@example.com")  # name is positional-only
# create_user("Alice", 30, "alice@example.com")                  # email is keyword-only
```

**Swift comparison:** Swift achieves similar clarity through argument labels and `_` to suppress
labels. Python's approach is more explicit about the calling convention.

---

## 6. Lambda Functions

Lambda functions are Python's anonymous functions. They are limited to a **single expression**
(no statements, no multi-line logic).

```python
# Named function
def square(x: int) -> int:
    return x * x

# Equivalent lambda
square_lambda = lambda x: x * x

print(square(5))         # 25
print(square_lambda(5))  # 25
```

### Lambda Syntax

```python
lambda arguments: expression
```

- No `return` keyword -- the expression's value is automatically returned.
- No type annotations (a limitation of lambdas).
- No statements (no `if/else` blocks, no loops, no assignments).

### Common Lambda Patterns

```python
# Sorting with a key function
names = ["Charlie", "Alice", "Bob"]
sorted_names = sorted(names, key=lambda name: len(name))
print(sorted_names)  # ['Bob', 'Alice', 'Charlie']

# Sorting complex objects
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35},
]
by_age = sorted(users, key=lambda u: u["age"])
print(by_age)  # [{'name': 'Bob', ...}, {'name': 'Alice', ...}, {'name': 'Charlie', ...}]

# Conditional expression in lambda (ternary)
classify = lambda x: "positive" if x > 0 else "non-positive"
print(classify(5))   # positive
print(classify(-3))  # non-positive
```

### Lambda vs Swift Closures

```swift
// Swift closure (much more powerful than Python lambdas)
let square = { (x: Int) -> Int in
    return x * x
}

// Swift trailing closure with map
let doubled = [1, 2, 3].map { $0 * 2 }
```

```python
# Python lambda (single expression only)
square = lambda x: x * x

# Python lambda with map
doubled = list(map(lambda x: x * 2, [1, 2, 3]))

# But Pythonic way is usually a list comprehension
doubled = [x * 2 for x in [1, 2, 3]]
```

**Key difference:** Swift closures can contain multiple statements, loops, and complex logic.
Python lambdas are restricted to a single expression. For anything more complex, use `def`.

---

## 7. map, filter, and reduce

### map()

Applies a function to every item in an iterable.

```python
numbers = [1, 2, 3, 4, 5]

# Using map with a named function
def square(x: int) -> int:
    return x * x

squared = list(map(square, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# Using map with a lambda
squared = list(map(lambda x: x ** 2, numbers))

# Pythonic alternative: list comprehension (generally preferred)
squared = [x ** 2 for x in numbers]
```

### filter()

Filters items based on a predicate function.

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Using filter
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4, 6, 8, 10]

# Pythonic alternative: list comprehension with condition
evens = [x for x in numbers if x % 2 == 0]
```

### reduce()

Reduces an iterable to a single value by applying a function cumulatively. Unlike `map` and
`filter`, `reduce` must be imported from `functools`.

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# Sum using reduce
total = reduce(lambda acc, x: acc + x, numbers)
print(total)  # 15

# With initial value
total = reduce(lambda acc, x: acc + x, numbers, 100)
print(total)  # 115

# Building a string
words = ["Hello", "World", "from", "Python"]
sentence = reduce(lambda acc, w: f"{acc} {w}", words)
print(sentence)  # Hello World from Python
```

### map/filter/reduce: Python vs Swift

```swift
// Swift
let numbers = [1, 2, 3, 4, 5]
let squared = numbers.map { $0 * $0 }           // [1, 4, 9, 16, 25]
let evens = numbers.filter { $0 % 2 == 0 }      // [2, 4]
let sum = numbers.reduce(0, +)                   // 15
```

```python
# Python -- functional style
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x * x, numbers))      # [1, 4, 9, 16, 25]
evens = list(filter(lambda x: x % 2 == 0, numbers)) # [2, 4]
total = reduce(lambda acc, x: acc + x, numbers)     # 15

# Python -- idiomatic/Pythonic style (preferred)
squared = [x * x for x in numbers]
evens = [x for x in numbers if x % 2 == 0]
total = sum(numbers)
```

**Note:** In Python, list comprehensions are generally preferred over `map`/`filter` for
readability. `reduce` is used sparingly -- often a simple loop or built-in like `sum()` is
clearer.

---

## 8. functools: partial, lru_cache, and More

The `functools` module provides higher-order functions and utilities for working with functions.

### functools.partial

Creates a new function with some arguments pre-filled. Similar to currying in functional
programming.

```python
from functools import partial

def power(base: int, exponent: int) -> int:
    return base ** exponent

# Create specialized versions
square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(3))    # 27

# Practical example: configuring a logger
def log(level: str, message: str) -> str:
    return f"[{level}] {message}"

info = partial(log, "INFO")
error = partial(log, "ERROR")

print(info("Server started"))   # [INFO] Server started
print(error("Disk full"))       # [ERROR] Disk full
```

### functools.lru_cache

Memoization decorator that caches function results. Extremely useful for expensive computations
or recursive algorithms.

```python
from functools import lru_cache
import time

# Without cache -- slow for large n
def fibonacci_slow(n: int) -> int:
    if n < 2:
        return n
    return fibonacci_slow(n - 1) + fibonacci_slow(n - 2)

# With cache -- fast even for large n
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

start = time.time()
print(fibonacci(100))  # 354224848179261915075
print(f"Time: {time.time() - start:.4f}s")  # Nearly instant

# Cache info
print(fibonacci.cache_info())
# CacheInfo(hits=98, misses=101, maxsize=128, currsize=101)

# Clear the cache
fibonacci.cache_clear()
```

### functools.cache (Python 3.9+)

Simpler version of `lru_cache` with no size limit.

```python
from functools import cache

@cache
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(10))  # 3628800
```

### functools.wraps

Preserves the original function's metadata when writing decorators. We'll cover this in detail
in Module 06, but here's a preview:

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # Preserves func's __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def say_hello():
    """Says hello to the world."""
    print("Hello!")

print(say_hello.__name__)  # say_hello (not 'wrapper')
print(say_hello.__doc__)   # Says hello to the world.
```

### functools.reduce (covered above)

Already discussed in section 7.

---

## 9. Closures and nonlocal

### What Is a Closure?

A closure is a function that "remembers" variables from its enclosing scope, even after
that scope has finished executing. Python closures work similarly to Swift closures, but
with some important differences.

```python
def make_multiplier(factor: int):
    """Returns a closure that multiplies by factor."""
    def multiplier(x: int) -> int:
        return x * factor  # 'factor' is captured from the enclosing scope
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))   # 10
print(triple(5))   # 15
print(double(10))  # 20
```

### How Closures Capture Variables

Python closures capture variables **by reference** (not by value). This means they see the
latest value of the variable at the time they are called.

```python
def make_counters():
    counters = []
    for i in range(5):
        counters.append(lambda: i)  # All lambdas share the same 'i'
    return counters

# Surprise! They all return 4 (the final value of i)
fns = make_counters()
print([fn() for fn in fns])  # [4, 4, 4, 4, 4]

# Fix: capture the current value with a default parameter
def make_counters_fixed():
    counters = []
    for i in range(5):
        counters.append(lambda i=i: i)  # Default captures current value
    return counters

fns = make_counters_fixed()
print([fn() for fn in fns])  # [0, 1, 2, 3, 4]
```

**Swift comparison:** Swift closures also capture by reference, but Swift has **capture lists**
(`[weak self]`, `[i]`) that let you explicitly control capture semantics. Python has no
capture lists -- the default-parameter trick is the standard workaround.

### The `nonlocal` Keyword

To **modify** a variable in an enclosing scope (not global), use `nonlocal`. Without it,
assigning to a variable creates a new local variable.

```python
def make_counter(start: int = 0):
    count = start

    def increment() -> int:
        nonlocal count  # Without this, 'count = count + 1' would fail
        count += 1
        return count

    def get() -> int:
        return count  # Reading doesn't require nonlocal

    return increment, get

inc, get = make_counter(0)
print(inc())   # 1
print(inc())   # 2
print(inc())   # 3
print(get())   # 3
```

### `nonlocal` vs `global`

```python
# global: refers to module-level variable
x = 10

def modify_global():
    global x
    x = 20

# nonlocal: refers to enclosing function's variable
def outer():
    x = 10
    def inner():
        nonlocal x
        x = 20
    inner()
    print(x)  # 20

outer()
```

### Closure as a State Machine

```python
def make_toggle(initial: bool = False):
    """Creates a toggle that alternates between True and False."""
    state = initial

    def toggle() -> bool:
        nonlocal state
        state = not state
        return state

    return toggle

flip = make_toggle()
print(flip())  # True
print(flip())  # False
print(flip())  # True
```

---

## 10. Higher-Order Functions and First-Class Functions

### First-Class Functions

In Python, functions are first-class objects. You can:
- Assign them to variables
- Store them in data structures
- Pass them as arguments
- Return them from functions

```python
# Store functions in a list
def add(a: int, b: int) -> int: return a + b
def sub(a: int, b: int) -> int: return a - b
def mul(a: int, b: int) -> int: return a * b

operations: list = [add, sub, mul]

for op in operations:
    print(f"{op.__name__}(10, 3) = {op(10, 3)}")
# add(10, 3) = 13
# sub(10, 3) = 7
# mul(10, 3) = 30

# Store functions in a dict (dispatch table)
dispatch: dict[str, callable] = {
    "+": add,
    "-": sub,
    "*": mul,
}

print(dispatch["+"](10, 3))  # 13
print(dispatch["*"](10, 3))  # 30
```

### Higher-Order Functions

Functions that take functions as arguments or return functions.

```python
from typing import Callable

def apply_twice(func: Callable[[int], int], value: int) -> int:
    """Apply a function twice to a value."""
    return func(func(value))

def increment(x: int) -> int:
    return x + 1

print(apply_twice(increment, 5))     # 7
print(apply_twice(lambda x: x * 2, 3))  # 12

# Function that returns a function
def make_adder(n: int) -> Callable[[int], int]:
    def adder(x: int) -> int:
        return x + n
    return adder

add5 = make_adder(5)
print(add5(10))   # 15
print(add5(100))  # 105
```

### Function Composition

```python
from typing import Callable, TypeVar

T = TypeVar("T")

def compose(f: Callable[[T], T], g: Callable[[T], T]) -> Callable[[T], T]:
    """Compose two functions: compose(f, g)(x) == f(g(x))"""
    def composed(x: T) -> T:
        return f(g(x))
    return composed

def double(x: int) -> int:
    return x * 2

def add_one(x: int) -> int:
    return x + 1

double_then_add = compose(add_one, double)
add_then_double = compose(double, add_one)

print(double_then_add(5))  # 11  (5*2 + 1)
print(add_then_double(5))  # 12  ((5+1) * 2)
```

### Practical: Pipeline Pattern

```python
def pipeline(*funcs: Callable) -> Callable:
    """Create a pipeline of functions applied left to right."""
    def apply(value):
        result = value
        for func in funcs:
            result = func(result)
        return result
    return apply

# Data processing pipeline
process = pipeline(
    str.strip,
    str.lower,
    lambda s: s.replace(" ", "_"),
    lambda s: s[:20],
)

print(process("  Hello World  "))  # hello_world
```

---

## 11. Type Hints for Functions

### The `Callable` Type

```python
from typing import Callable

# Function that takes two ints and returns an int
def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

# Callable with no args returning a string
def run(factory: Callable[[], str]) -> str:
    return factory()

# Callable with any args (use ... for unknown signatures)
def wrap(func: Callable[..., str]) -> str:
    return func()
```

### Complex Function Type Hints

```python
from typing import Callable, TypeVar, ParamSpec

T = TypeVar("T")
P = ParamSpec("P")

# Generic higher-order function
def retry(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Call func, retrying up to 3 times on failure."""
    for attempt in range(3):
        try:
            return func(*args, **kwargs)
        except Exception:
            if attempt == 2:
                raise
    raise RuntimeError("Unreachable")

# Type alias for function types
Predicate = Callable[[int], bool]
Transform = Callable[[str], str]

def find_first(items: list[int], predicate: Predicate) -> int | None:
    for item in items:
        if predicate(item):
            return item
    return None
```

### Overloaded Functions

```python
from typing import overload

@overload
def process(value: int) -> str: ...
@overload
def process(value: str) -> int: ...

def process(value: int | str) -> str | int:
    if isinstance(value, int):
        return str(value)
    return len(value)
```

---

## 12. Docstrings Conventions

Python uses docstrings (triple-quoted strings right after the function definition) for
documentation. Unlike Swift's `///` doc comments, Python docstrings are accessible at runtime
via `func.__doc__`.

### Google Style (Recommended)

```python
def fetch_user(user_id: int, include_posts: bool = False) -> dict:
    """Fetch a user by their ID from the database.

    Retrieves user information and optionally includes their posts.
    This function makes a network call to the user service.

    Args:
        user_id: The unique identifier of the user.
        include_posts: Whether to include the user's posts.
            Defaults to False.

    Returns:
        A dictionary containing user data with keys 'id', 'name',
        'email', and optionally 'posts'.

    Raises:
        ValueError: If user_id is negative.
        ConnectionError: If the database is unavailable.

    Example:
        >>> fetch_user(42)
        {'id': 42, 'name': 'Alice', 'email': 'alice@example.com'}
        >>> fetch_user(42, include_posts=True)
        {'id': 42, 'name': 'Alice', 'email': 'alice@example.com', 'posts': [...]}
    """
    if user_id < 0:
        raise ValueError(f"user_id must be non-negative, got {user_id}")
    ...
```

### NumPy/SciPy Style

```python
def compute_distance(point_a: tuple[float, float],
                     point_b: tuple[float, float]) -> float:
    """
    Compute the Euclidean distance between two 2D points.

    Parameters
    ----------
    point_a : tuple[float, float]
        The first point as (x, y).
    point_b : tuple[float, float]
        The second point as (x, y).

    Returns
    -------
    float
        The Euclidean distance between the two points.

    Examples
    --------
    >>> compute_distance((0, 0), (3, 4))
    5.0
    """
    return ((point_a[0] - point_b[0]) ** 2 +
            (point_a[1] - point_b[1]) ** 2) ** 0.5
```

### Accessing Docstrings at Runtime

```python
def my_function():
    """This is my function's docstring."""
    pass

print(my_function.__doc__)  # This is my function's docstring.
help(my_function)            # Pretty-prints the docstring
```

---

## Quick Reference: Functions Cheat Sheet

| Concept | Python | Swift |
|---------|--------|-------|
| Define function | `def func():` | `func func() {}` |
| Return type | `-> int` | `-> Int` |
| Default param | `def f(x=10):` | `func f(x: Int = 10)` |
| Variadic args | `*args` | `values: Int...` |
| Keyword variadic | `**kwargs` | N/A |
| Lambda | `lambda x: x + 1` | `{ (x: Int) in x + 1 }` or `{ $0 + 1 }` |
| Keyword-only | After `*` | N/A (use argument labels) |
| Positional-only | Before `/` | Use `_` for no label |
| Closure capture | By reference (always) | By reference (can use capture lists) |
| Modify captured var | `nonlocal x` | Automatic (reference types) |
| Memoize | `@lru_cache` | Manual dictionary cache |
| Partial application | `functools.partial` | Manual closure |
| Docstring | `"""..."""` | `/// ...` |

---

## Key Takeaways for Swift Developers

1. **Python functions are simpler** -- no argument labels, no `func` keyword, just `def`.
2. **Lambdas are limited** -- unlike Swift closures, they can only contain a single expression.
3. **The mutable default trap** is real -- always use `None` as the default for mutable parameters.
4. **`nonlocal` is your friend** -- it's required to modify enclosed variables (Swift does this automatically).
5. **List comprehensions > map/filter** -- Python developers generally prefer comprehensions over functional-style `map`/`filter`.
6. **`*args`/`**kwargs` are powerful** -- they enable very flexible function signatures that have no Swift equivalent.
7. **`lru_cache` is magic** -- use it liberally for expensive pure functions (similar to memoization you'd build manually in Swift).
8. **First-class functions** -- both languages treat functions as first-class citizens, but Python makes it feel more natural with less ceremony.

---

## Next Steps

In Module 05, we'll dive into Object-Oriented Programming and see how Python's class system
compares to Swift's protocols, structs, and classes. Many patterns from this module (closures,
higher-order functions) will continue to appear throughout the curriculum.
