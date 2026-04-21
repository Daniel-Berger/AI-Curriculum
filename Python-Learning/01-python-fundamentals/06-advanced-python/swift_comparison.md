# Swift vs Python: Advanced Python Features

A side-by-side comparison for Swift/iOS developers learning Python.

---

## 1. Property Wrappers vs Decorators

| Feature | Swift Property Wrappers | Python Decorators |
|---------|------------------------|-------------------|
| Syntax | `@Published var x: Int` | `@my_decorator` above `def`/`class` |
| Scope | Properties only | Functions, methods, classes |
| Parameterized | `@Clamped(range: 0...100)` | `@retry(max_attempts=3)` |
| Stacking | Yes (multiple wrappers) | Yes (multiple decorators) |
| Access to wrapped value | `wrappedValue`, `projectedValue` | Via closure / `functools.wraps` |
| Built-in examples | `@State`, `@Binding`, `@Published` | `@property`, `@staticmethod`, `@lru_cache` |
| Implementation | Struct with `wrappedValue` | Function returning function |

### Swift Property Wrapper

```swift
@propertyWrapper
struct Clamped {
    let range: ClosedRange<Int>
    var wrappedValue: Int {
        didSet { wrappedValue = wrappedValue.clamped(to: range) }
    }

    init(wrappedValue: Int, range: ClosedRange<Int>) {
        self.range = range
        self.wrappedValue = wrappedValue.clamped(to: range)
    }
}

struct Settings {
    @Clamped(range: 0...100) var volume: Int = 50
}

var s = Settings()
s.volume = 150  // Clamped to 100
```

### Python Decorator (Function-Level)

```python
from functools import wraps

def clamped(min_val, max_val):
    """Decorator that clamps a function's return value."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return max(min_val, min(max_val, result))
        return wrapper
    return decorator

@clamped(0, 100)
def calculate_volume(base, adjustment):
    return base + adjustment

calculate_volume(80, 30)  # Returns 100 (clamped)
```

### Python Descriptor (Property-Level, Closer to Swift)

```python
class Clamped:
    """Descriptor that clamps values -- closer to Swift property wrapper."""

    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val

    def __set_name__(self, owner, name):
        self.attr_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.attr_name, self.min_val)

    def __set__(self, obj, value):
        clamped_value = max(self.min_val, min(self.max_val, value))
        setattr(obj, self.attr_name, clamped_value)

class Settings:
    volume = Clamped(0, 100)

s = Settings()
s.volume = 150  # Clamped to 100
print(s.volume)  # 100
```

### Common Built-in Decorators Comparison

| Swift | Python | Purpose |
|-------|--------|---------|
| `@State` | N/A (manual) | UI state management |
| `@Published` | N/A | Observable property |
| `@objc` | N/A | Objective-C bridge |
| `@available` | `@deprecated` (custom) | API availability |
| N/A | `@property` | Computed property |
| N/A | `@staticmethod` | Static method |
| N/A | `@classmethod` | Class method |
| N/A | `@lru_cache` | Memoization |
| N/A | `@dataclass` | Auto-generate boilerplate |
| N/A | `@contextmanager` | Resource management |
| N/A | `@abstractmethod` | Abstract methods |

---

## 2. Sequence / IteratorProtocol vs Python Iterators

| Feature | Swift | Python |
|---------|-------|--------|
| Iterator protocol | `IteratorProtocol` with `next() -> T?` | `__next__()` raises `StopIteration` |
| Sequence protocol | `Sequence` with `makeIterator()` | `__iter__()` returns iterator |
| Exhaustion signal | Returns `nil` | Raises `StopIteration` |
| Lazy evaluation | `.lazy` property | Generators are lazy by default |
| Infinite sequences | `AnySequence { ... }` | Generator function / `itertools.count` |
| For-in loop | `for x in sequence` | `for x in iterable` |
| Multiple passes | Depends on conformance | Iterable (yes), Iterator (no) |

### Swift Sequence

```swift
struct Countdown: Sequence {
    let start: Int

    func makeIterator() -> CountdownIterator {
        return CountdownIterator(current: start)
    }
}

struct CountdownIterator: IteratorProtocol {
    var current: Int

    mutating func next() -> Int? {
        guard current > 0 else { return nil }
        defer { current -= 1 }
        return current
    }
}

for n in Countdown(start: 5) {
    print(n)  // 5, 4, 3, 2, 1
}
```

### Python Iterator

```python
class Countdown:
    """Iterable (creates fresh iterator each time)."""

    def __init__(self, start: int):
        self.start = start

    def __iter__(self):
        return CountdownIterator(self.start)


class CountdownIterator:
    """Iterator (tracks state, single-pass)."""

    def __init__(self, current: int):
        self.current = current

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


for n in Countdown(5):
    print(n)  # 5, 4, 3, 2, 1
```

### Python Generator (Simpler)

```python
def countdown(start: int):
    """Generator -- equivalent to the iterator above but much simpler."""
    while start > 0:
        yield start
        start -= 1

for n in countdown(5):
    print(n)  # 5, 4, 3, 2, 1
```

### Lazy Evaluation Comparison

```swift
// Swift lazy sequence
let result = (1...1_000_000)
    .lazy
    .map { $0 * $0 }
    .filter { $0 % 2 == 0 }
    .prefix(10)
Array(result)  // First 10 even squares
```

```python
# Python generator expressions (lazy by default)
import itertools

gen = (x * x for x in range(1, 1_000_001))
even_squares = (x for x in gen if x % 2 == 0)
result = list(itertools.islice(even_squares, 10))
# First 10 even squares
```

---

## 3. Codable vs Pydantic

| Feature | Swift `Codable` | Python `Pydantic v2` |
|---------|----------------|---------------------|
| Definition | `struct User: Codable { }` | `class User(BaseModel): ...` |
| JSON encode | `JSONEncoder().encode(obj)` | `model.model_dump_json()` |
| JSON decode | `JSONDecoder().decode(T.self, from:)` | `Model.model_validate_json(s)` |
| Validation | Type checking only | Rich validation (ranges, regex, custom) |
| Key mapping | `CodingKeys` enum | `Field(alias="...")` |
| Default values | Explicit in property | `Field(default=...)` |
| Nested models | Automatic | Automatic |
| Custom encoding | `encode(to encoder:)` | `@model_serializer` |
| Custom decoding | `init(from decoder:)` | `@model_validator` |
| Type coercion | No (strict) | Yes (configurable) |
| Error messages | `DecodingError` | `ValidationError` (detailed) |
| Schema generation | No | `model.model_json_schema()` |

### Swift Codable

```swift
struct User: Codable {
    let name: String
    let email: String
    let age: Int
    var isActive: Bool = true

    enum CodingKeys: String, CodingKey {
        case name, email, age
        case isActive = "is_active"  // Key mapping
    }
}

// Encode
let user = User(name: "Alice", email: "a@b.com", age: 30)
let data = try JSONEncoder().encode(user)
let json = String(data: data, encoding: .utf8)!

// Decode
let decoded = try JSONDecoder().decode(User.self, from: data)
```

### Python Pydantic v2

```python
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    name: str
    email: str
    age: int = Field(ge=0, le=150)
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email")
        return v.lower()

# Encode
user = User(name="Alice", email="a@b.com", age=30)
json_str = user.model_dump_json()
# '{"name":"Alice","email":"a@b.com","age":30,"is_active":true}'

# Decode with validation
decoded = User.model_validate_json(json_str)

# Dict conversion
d = user.model_dump()
user2 = User.model_validate(d)

# Schema generation (no Swift equivalent)
print(User.model_json_schema())
```

### Validation Comparison

```swift
// Swift -- manual validation in init
struct UserRegistration: Codable {
    let username: String
    let password: String

    init(username: String, password: String) throws {
        guard username.count >= 3 else {
            throw ValidationError.tooShort("username")
        }
        guard password.count >= 8 else {
            throw ValidationError.tooShort("password")
        }
        self.username = username
        self.password = password
    }
}
```

```python
# Python Pydantic -- declarative validation
from pydantic import BaseModel, Field, field_validator

class UserRegistration(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("Must be alphanumeric")
        return v

# Validation is automatic on instantiation
try:
    UserRegistration(username="a", password="123")
except ValidationError as e:
    print(e)
    # 2 validation errors:
    #   username: String should have at least 3 characters
    #   password: String should have at least 8 characters
```

---

## 4. Result Builders vs Generators

| Feature | Swift Result Builders | Python Generators |
|---------|----------------------|-------------------|
| Purpose | DSL construction | Lazy value production |
| Syntax | `@resultBuilder` | `yield` / `yield from` |
| Use case | SwiftUI views, HTML builders | Data pipelines, lazy sequences |
| Composability | `buildBlock`, `buildOptional` | `yield from`, chaining |
| Evaluation | Eager (builds result) | Lazy (produces on demand) |

### Swift Result Builder

```swift
@resultBuilder
struct ArrayBuilder {
    static func buildBlock(_ components: Int...) -> [Int] {
        return components
    }

    static func buildOptional(_ component: [Int]?) -> [Int] {
        return component ?? []
    }
}

@ArrayBuilder
func makeNumbers(includeExtra: Bool) -> [Int] {
    1
    2
    3
    if includeExtra {
        4
        5
    }
}

makeNumbers(includeExtra: true)  // [1, 2, 3, 4, 5]
```

### Python Generator

```python
def make_numbers(include_extra: bool):
    yield 1
    yield 2
    yield 3
    if include_extra:
        yield 4
        yield 5

list(make_numbers(True))   # [1, 2, 3, 4, 5]
list(make_numbers(False))  # [1, 2, 3]
```

**Key insight:** Swift result builders construct a complete value (eager). Python generators
produce values on demand (lazy). They solve different problems but share the concept of
declarative value production.

---

## 5. withCheckedContinuation vs Context Managers

| Feature | Swift Scoped APIs | Python Context Manager |
|---------|------------------|----------------------|
| Resource management | Manual / `defer` | `with` statement |
| Cleanup guarantee | `defer { }` | `__exit__` / `finally` |
| Reusability | Per-call `defer` | Reusable objects |
| Syntax | `defer { resource.close() }` | `with open(...) as f:` |
| Async variant | `withCheckedContinuation` | `async with` |
| Error handling | Propagated | `__exit__` can suppress |

### Swift defer

```swift
func processFile() throws {
    let file = try openFile("data.txt")
    defer { file.close() }  // Guaranteed cleanup

    let data = try file.read()
    process(data)
}  // file.close() called here
```

### Python Context Manager

```python
# Using with statement
def process_file():
    with open("data.txt") as f:  # Guaranteed cleanup
        data = f.read()
        process(data)
    # f.close() called here automatically

# Custom context manager
from contextlib import contextmanager

@contextmanager
def managed_resource(name):
    resource = acquire(name)
    try:
        yield resource
    finally:
        resource.release()  # Guaranteed cleanup

with managed_resource("db") as db:
    db.query("SELECT ...")
```

### Swift withCheckedContinuation

```swift
func fetchData() async -> Data {
    await withCheckedContinuation { continuation in
        legacyFetch { data in
            continuation.resume(returning: data)
        }
    }
}
```

### Python Async Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_connection(url):
    conn = await connect(url)
    try:
        yield conn
    finally:
        await conn.close()

async with managed_connection("postgres://...") as conn:
    await conn.execute("SELECT ...")
```

---

## Summary: Mental Model Shifts

| Swift Concept | Python Equivalent | Key Difference |
|---------------|-------------------|----------------|
| `@propertyWrapper` | Decorator or Descriptor | Decorators are more general (functions + classes) |
| `Sequence` protocol | `__iter__` method | Python iterables return iterator objects |
| `IteratorProtocol` | `__iter__` + `__next__` | Python raises `StopIteration` instead of `nil` |
| `.lazy.map { }` | Generator expression `(x for x in ...)` | Python generators are lazy by default |
| `Codable` | `Pydantic BaseModel` | Pydantic adds validation, coercion, schema gen |
| `CodingKeys` | `Field(alias=...)` | Pydantic is more flexible |
| `@resultBuilder` | Generator with `yield` | Result builders are eager, generators are lazy |
| `defer { }` | `with` statement / `finally` | Context managers are reusable objects |
| `withCheckedContinuation` | `async with` | Both provide scoped async resource management |
| No equivalent | `@functools.wraps` | Preserves decorator metadata |
| No equivalent | `itertools` module | Rich library of lazy iteration utilities |
| No equivalent | `yield from` | Delegation to sub-generators |
| No equivalent | `@contextmanager` | Generator-based context manager creation |
