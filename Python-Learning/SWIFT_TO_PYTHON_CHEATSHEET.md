# Swift to Python Syntax Cheatsheet

A practical, side-by-side reference for developers moving between Swift and Python.

---

## Table of Contents

1. [Variables & Constants](#1-variables--constants)
2. [Basic Types](#2-basic-types)
3. [String Operations](#3-string-operations)
4. [Collections](#4-collections)
5. [Control Flow](#5-control-flow)
6. [Functions](#6-functions)
7. [Closures](#7-closures)
8. [OOP](#8-oop)
9. [Error Handling](#9-error-handling)
10. [Optionals & None](#10-optionals--none)
11. [Properties](#11-properties)
12. [Generics](#12-generics)
13. [Protocol / Interface](#13-protocol--interface)
14. [Concurrency](#14-concurrency)
15. [Pattern Matching](#15-pattern-matching)
16. [Memory Management](#16-memory-management)
17. [Package Management](#17-package-management)
18. [Testing](#18-testing)
19. [Common Patterns](#19-common-patterns)

---

## 1. Variables & Constants

| Swift | Python |
|-------|--------|
| `let name = "Alice"` | `name = "Alice"` (all variables are reassignable) |
| `var count = 0` | `count = 0` |
| `let pi: Double = 3.14` | `pi: float = 3.14` (annotation only, not enforced) |
| `var items: [String] = []` | `items: list[str] = []` |

**Key difference:** Swift distinguishes between immutable (`let`) and mutable (`var`) bindings at the language level. Python has no true constant mechanism. By convention, `ALL_CAPS` names signal a constant.

```swift
// Swift
let MAX_RETRIES = 3        // immutable, compiler-enforced
var attempt = 0             // mutable
let name: String = "Alice"  // explicit type annotation
```

```python
# Python
MAX_RETRIES = 3             # convention only, nothing prevents reassignment
attempt = 0
name: str = "Alice"         # type hint, not enforced at runtime

# For true immutability, use Final (checked by mypy/pyright, not at runtime)
from typing import Final
MAX_RETRIES: Final = 3
```

---

## 2. Basic Types

| Concept | Swift | Python |
|---------|-------|--------|
| Integer | `Int` | `int` (arbitrary precision) |
| Float | `Double`, `Float` | `float` |
| Boolean | `Bool` (`true`/`false`) | `bool` (`True`/`False`) |
| String | `String` | `str` |
| Character | `Character` | `str` (single character) |
| Null/absent | `nil` | `None` |
| Optional | `String?` | `str \| None` or `Optional[str]` |
| Any type | `Any` | `Any` (from `typing`) |
| Void | `Void` / `()` | `None` (as return type) |
| Byte data | `Data` | `bytes` |
| Type alias | `typealias Name = String` | `Name = str` or `type Name = str` (3.12+) |

```swift
// Swift
let age: Int = 30
let price: Double = 9.99
let active: Bool = true
let label: String = "Hello"
let maybeValue: Int? = nil
```

```python
# Python
age: int = 30
price: float = 9.99
active: bool = True
label: str = "Hello"
maybe_value: int | None = None
```

---

## 3. String Operations

| Operation | Swift | Python |
|-----------|-------|--------|
| Interpolation | `"Hello, \(name)"` | `f"Hello, {name}"` |
| Concatenation | `"a" + "b"` | `"a" + "b"` |
| Multiline | `"""..."""` | `"""..."""` |
| Repeat | `String(repeating: "ab", count: 3)` | `"ab" * 3` |
| Length | `str.count` | `len(s)` |
| Contains | `str.contains("x")` | `"x" in s` |
| Uppercase | `str.uppercased()` | `s.upper()` |
| Lowercase | `str.lowercased()` | `s.lower()` |
| Trim whitespace | `str.trimmingCharacters(in: .whitespaces)` | `s.strip()` |
| Split | `str.split(separator: ",")` | `s.split(",")` |
| Join | `arr.joined(separator: ", ")` | `", ".join(lst)` |
| Starts with | `str.hasPrefix("He")` | `s.startswith("He")` |
| Ends with | `str.hasSuffix("lo")` | `s.endswith("lo")` |
| Replace | `str.replacingOccurrences(of: "a", with: "b")` | `s.replace("a", "b")` |
| Substring | `str.prefix(5)` | `s[:5]` |
| Index of | `str.firstIndex(of: "l")` | `s.index("l")` or `s.find("l")` |
| Is empty | `str.isEmpty` | `not s` or `len(s) == 0` |

```swift
// Swift
let name = "World"
let greeting = "Hello, \(name)!"
let lines = """
    Line 1
    Line 2
    """
let words = greeting.split(separator: " ")
let upper = greeting.uppercased()
```

```python
# Python
name = "World"
greeting = f"Hello, {name}!"
lines = """Line 1
Line 2"""
words = greeting.split(" ")
upper = greeting.upper()
```

---

## 4. Collections

### Array / List

| Operation | Swift | Python |
|-----------|-------|--------|
| Create | `let a = [1, 2, 3]` | `a = [1, 2, 3]` |
| Empty | `var a: [Int] = []` or `[Int]()` | `a: list[int] = []` |
| Append | `a.append(4)` | `a.append(4)` |
| Insert | `a.insert(0, at: 0)` | `a.insert(0, 0)` |
| Remove | `a.remove(at: 0)` | `a.pop(0)` or `del a[0]` |
| Access | `a[0]` | `a[0]` |
| Slice | `Array(a[1...3])` | `a[1:4]` |
| Count | `a.count` | `len(a)` |
| Sort | `a.sorted()` | `sorted(a)` |
| Sort in place | `a.sort()` | `a.sort()` |
| Reverse | `a.reversed()` | `reversed(a)` or `a[::-1]` |
| Contains | `a.contains(2)` | `2 in a` |
| First / Last | `a.first`, `a.last` | `a[0]`, `a[-1]` |
| Enumerate | `for (i, v) in a.enumerated()` | `for i, v in enumerate(a)` |
| Zip | `zip(a, b)` | `zip(a, b)` |
| Flatten | `a.flatMap { $0 }` | `[x for sub in a for x in sub]` |

```swift
// Swift
var fruits = ["apple", "banana"]
fruits.append("cherry")
fruits.insert("avocado", at: 0)
let first = fruits.first   // Optional<String>
let count = fruits.count
for (index, fruit) in fruits.enumerated() {
    print("\(index): \(fruit)")
}
```

```python
# Python
fruits = ["apple", "banana"]
fruits.append("cherry")
fruits.insert(0, "avocado")
first = fruits[0]           # raises IndexError if empty
count = len(fruits)
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```

### Dictionary / dict

| Operation | Swift | Python |
|-----------|-------|--------|
| Create | `let d = ["a": 1, "b": 2]` | `d = {"a": 1, "b": 2}` |
| Empty | `var d: [String: Int] = [:]` | `d: dict[str, int] = {}` |
| Access | `d["a"]` (returns `Int?`) | `d["a"]` (raises `KeyError`) |
| Safe access | `d["a"]` (already optional) | `d.get("a")` (returns `None`) |
| Default | `d["a", default: 0]` | `d.get("a", 0)` |
| Set | `d["c"] = 3` | `d["c"] = 3` |
| Remove | `d.removeValue(forKey: "a")` | `del d["a"]` or `d.pop("a")` |
| Keys | `d.keys` | `d.keys()` |
| Values | `d.values` | `d.values()` |
| Iterate | `for (k, v) in d` | `for k, v in d.items()` |
| Merge | `d.merge(other) { $1 }` | `d \| other` (3.9+) or `d.update(other)` |
| Count | `d.count` | `len(d)` |

```swift
// Swift
var scores: [String: Int] = ["Alice": 90, "Bob": 85]
let aliceScore = scores["Alice"]       // Optional(90)
scores["Charlie"] = 78
for (name, score) in scores {
    print("\(name): \(score)")
}
```

```python
# Python
scores: dict[str, int] = {"Alice": 90, "Bob": 85}
alice_score = scores.get("Alice")       # 90 (None if missing)
scores["Charlie"] = 78
for name, score in scores.items():
    print(f"{name}: {score}")
```

### Set

| Operation | Swift | Python |
|-----------|-------|--------|
| Create | `let s: Set = [1, 2, 3]` | `s = {1, 2, 3}` |
| Empty | `var s = Set<Int>()` | `s: set[int] = set()` |
| Add | `s.insert(4)` | `s.add(4)` |
| Remove | `s.remove(1)` | `s.discard(1)` or `s.remove(1)` |
| Contains | `s.contains(2)` | `2 in s` |
| Union | `s.union(other)` | `s \| other` or `s.union(other)` |
| Intersection | `s.intersection(other)` | `s & other` or `s.intersection(other)` |
| Difference | `s.subtracting(other)` | `s - other` or `s.difference(other)` |

### Tuple

| Operation | Swift | Python |
|-----------|-------|--------|
| Create | `let t = (1, "hello")` | `t = (1, "hello")` |
| Named | `let t = (x: 1, y: 2)` | Use `NamedTuple` (see below) |
| Access | `t.0`, `t.1` | `t[0]`, `t[1]` |
| Destructure | `let (a, b) = t` | `a, b = t` |

```swift
// Swift
let point = (x: 10, y: 20)
print(point.x)
let (x, y) = point
```

```python
# Python
from typing import NamedTuple

class Point(NamedTuple):
    x: int
    y: int

point = Point(x=10, y=20)
print(point.x)
x, y = point
```

---

## 5. Control Flow

### if / else

| Swift | Python |
|-------|--------|
| `if condition { }` | `if condition:` |
| `} else if other { }` | `elif other:` |
| `} else { }` | `else:` |
| Braces required, parens optional | Colon + indentation, no braces |

```swift
// Swift
let score = 85
if score >= 90 {
    print("A")
} else if score >= 80 {
    print("B")
} else {
    print("C")
}

// Ternary
let grade = score >= 90 ? "A" : "B"
```

```python
# Python
score = 85
if score >= 90:
    print("A")
elif score >= 80:
    print("B")
else:
    print("C")

# Ternary (conditional expression)
grade = "A" if score >= 90 else "B"
```

### switch / match

| Swift | Python (3.10+) |
|-------|----------------|
| `switch value { case ...: }` | `match value: case ...:` |
| Exhaustive (requires `default`) | No exhaustiveness check |
| Pattern matching with `where` | Pattern matching with guards (`if`) |
| Fallthrough is opt-in | No fallthrough concept |

```swift
// Swift
switch statusCode {
case 200:
    print("OK")
case 400...499:
    print("Client error")
case 500...599:
    print("Server error")
case let code where code > 0:
    print("Other: \(code)")
default:
    print("Unknown")
}
```

```python
# Python 3.10+
match status_code:
    case 200:
        print("OK")
    case code if 400 <= code <= 499:
        print("Client error")
    case code if 500 <= code <= 599:
        print("Server error")
    case code if code > 0:
        print(f"Other: {code}")
    case _:
        print("Unknown")
```

### for-in

| Swift | Python |
|-------|--------|
| `for i in 0..<10` | `for i in range(10)` |
| `for i in 0...10` | `for i in range(11)` |
| `for item in collection` | `for item in collection` |
| `for (i, v) in arr.enumerated()` | `for i, v in enumerate(arr)` |
| `for i in stride(from: 0, to: 10, by: 2)` | `for i in range(0, 10, 2)` |
| `for _ in 0..<5` | `for _ in range(5)` |

```swift
// Swift
for i in 0..<5 {
    print(i)    // 0, 1, 2, 3, 4
}

for (index, value) in ["a", "b", "c"].enumerated() {
    print("\(index): \(value)")
}
```

```python
# Python
for i in range(5):
    print(i)    # 0, 1, 2, 3, 4

for index, value in enumerate(["a", "b", "c"]):
    print(f"{index}: {value}")
```

### while

| Swift | Python |
|-------|--------|
| `while condition { }` | `while condition:` |
| `repeat { } while condition` | No direct equivalent (use `while True` + `break`) |

```swift
// Swift
var n = 0
while n < 5 {
    n += 1
}

repeat {
    n -= 1
} while n > 0
```

```python
# Python
n = 0
while n < 5:
    n += 1

# Emulating repeat...while
while True:
    n -= 1
    if n <= 0:
        break
```

### guard

| Swift | Python |
|-------|--------|
| `guard condition else { return }` | No `guard` keyword; use early return with `if not` |

```swift
// Swift
func process(value: Int?) {
    guard let value = value else {
        print("No value")
        return
    }
    guard value > 0 else {
        print("Must be positive")
        return
    }
    print("Processing \(value)")
}
```

```python
# Python
def process(value: int | None) -> None:
    if value is None:
        print("No value")
        return
    if value <= 0:
        print("Must be positive")
        return
    print(f"Processing {value}")
```

---

## 6. Functions

| Concept | Swift | Python |
|---------|-------|--------|
| Declare | `func name() -> ReturnType` | `def name() -> ReturnType:` |
| No return | `func name()` (implicitly `Void`) | `def name() -> None:` |
| Parameters | `func f(x: Int, y: Int)` | `def f(x: int, y: int):` |
| Argument labels | `func f(for name: String)` | No equivalent (keyword args only) |
| Default params | `func f(x: Int = 0)` | `def f(x: int = 0):` |
| Variadic | `func f(_ items: Int...)` | `def f(*items: int):` |
| Inout | `func f(_ x: inout Int)` | No equivalent (mutate container or return) |
| Return tuple | `func f() -> (Int, Int)` | `def f() -> tuple[int, int]:` |
| Keyword only | N/A (all are keyword by default) | `def f(*, x: int):` |
| Positional only | N/A | `def f(x: int, /):` (3.8+) |
| Docstring | `/// Description` | `"""Description"""` inside function |

```swift
// Swift
func greet(person name: String, from city: String = "NYC") -> String {
    return "Hello, \(name) from \(city)!"
}
let msg = greet(person: "Alice", from: "Boston")

func sum(_ numbers: Int...) -> Int {
    return numbers.reduce(0, +)
}
```

```python
# Python
def greet(name: str, city: str = "NYC") -> str:
    """Return a greeting string."""
    return f"Hello, {name} from {city}!"

msg = greet("Alice", city="Boston")

def sum_all(*numbers: int) -> int:
    return sum(numbers)
```

---

## 7. Closures

| Concept | Swift | Python |
|---------|-------|--------|
| Inline closure | `{ (x: Int) -> Int in x * 2 }` | `lambda x: x * 2` |
| Trailing closure | `arr.map { $0 * 2 }` | `list(map(lambda x: x * 2, arr))` |
| Shorthand args | `$0`, `$1` | No equivalent |
| Multi-line | Closures can be multi-line | Lambda is single expression; use `def` for multi-line |
| Capture list | `{ [weak self] in ... }` | Closures capture by reference automatically |
| Escaping | `@escaping () -> Void` | All functions/lambdas are "escaping" by default |
| Stored closure | `var action: (() -> Void)?` | `action: Callable[[], None] \| None` |

```swift
// Swift
let numbers = [1, 2, 3, 4, 5]

// Full closure syntax
let doubled = numbers.map({ (n: Int) -> Int in
    return n * 2
})

// Shorthand
let doubled2 = numbers.map { $0 * 2 }

// Trailing closure
let evens = numbers.filter { $0 % 2 == 0 }

// Closure as variable
let operation: (Int, Int) -> Int = { $0 + $1 }

// Capturing values
func makeCounter() -> () -> Int {
    var count = 0
    return {
        count += 1
        return count
    }
}
```

```python
# Python
numbers = [1, 2, 3, 4, 5]

# Lambda (single expression only)
doubled = list(map(lambda n: n * 2, numbers))

# List comprehension (more Pythonic)
doubled2 = [n * 2 for n in numbers]

# Filter
evens = [n for n in numbers if n % 2 == 0]

# Function as variable
from typing import Callable
operation: Callable[[int, int], int] = lambda a, b: a + b

# Closure capturing values
def make_counter() -> Callable[[], int]:
    count = 0
    def counter() -> int:
        nonlocal count
        count += 1
        return count
    return counter
```

---

## 8. OOP

### Class

| Concept | Swift | Python |
|---------|-------|--------|
| Define class | `class Dog { }` | `class Dog:` |
| Init | `init(name: String)` | `def __init__(self, name: str):` |
| Properties | `var name: String` | `self.name = name` |
| Methods | `func bark()` | `def bark(self):` |
| Inheritance | `class Puppy: Dog` | `class Puppy(Dog):` |
| Call super | `super.init()` | `super().__init__()` |
| Deinit | `deinit { }` | `def __del__(self):` |
| Access control | `private`, `fileprivate`, `internal`, `public`, `open` | `_private` convention, `__mangled` |
| Static method | `static func` | `@staticmethod` |
| Class method | `class func` | `@classmethod` |
| Computed prop | `var x: Int { get { } }` | `@property` |
| String repr | `description` (via `CustomStringConvertible`) | `__repr__` / `__str__` |

```swift
// Swift
class Animal {
    let name: String
    var sound: String

    init(name: String, sound: String) {
        self.name = name
        self.sound = sound
    }

    func speak() -> String {
        return "\(name) says \(sound)"
    }
}

class Dog: Animal {
    let breed: String

    init(name: String, breed: String) {
        self.breed = breed
        super.init(name: name, sound: "Woof")
    }

    override func speak() -> String {
        return "\(name) the \(breed) says \(sound)!"
    }
}
```

```python
# Python
class Animal:
    def __init__(self, name: str, sound: str) -> None:
        self.name = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name} says {self.sound}"

class Dog(Animal):
    def __init__(self, name: str, breed: str) -> None:
        self.breed = breed
        super().__init__(name, sound="Woof")

    def speak(self) -> str:
        return f"{self.name} the {self.breed} says {self.sound}!"
```

### Struct vs dataclass

| Swift | Python |
|-------|--------|
| `struct Point { var x: Int; var y: Int }` | `@dataclass` or `NamedTuple` |
| Value semantics (copied on assignment) | Reference semantics (use `copy.deepcopy` for copies) |
| Automatic memberwise init | `@dataclass` generates `__init__` |
| Mutating methods: `mutating func` | No concept; just modify attributes |

```swift
// Swift
struct Point {
    var x: Double
    var y: Double

    func distance(to other: Point) -> Double {
        let dx = x - other.x
        let dy = y - other.y
        return (dx * dx + dy * dy).squareRoot()
    }

    mutating func translate(dx: Double, dy: Double) {
        x += dx
        y += dy
    }
}

let p = Point(x: 1.0, y: 2.0)  // auto memberwise init
```

```python
# Python
from dataclasses import dataclass
import math

@dataclass
class Point:
    x: float
    y: float

    def distance(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def translate(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy

p = Point(x=1.0, y=2.0)  # auto-generated __init__

# For immutable (like Swift's let with struct):
@dataclass(frozen=True)
class FrozenPoint:
    x: float
    y: float
```

### Enum

| Swift | Python |
|-------|--------|
| `enum Direction { case north, south }` | `class Direction(Enum):` |
| Raw values: `enum Coin: Int { case penny = 1 }` | `class Coin(IntEnum):` |
| Associated values: `case success(Data)` | No direct equivalent; use classes or tagged unions |
| Methods on enums | Methods on Enum subclass |
| `CaseIterable` | `list(Direction)` iterates all cases |

```swift
// Swift
enum Direction: String, CaseIterable {
    case north, south, east, west
}

enum Result {
    case success(String)
    case failure(Error)
}

let dir = Direction.north
print(dir.rawValue)  // "north"
```

```python
# Python
from enum import Enum, auto

class Direction(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

dir = Direction.NORTH
print(dir.value)  # "north"

# For associated values, use a union of dataclasses
from dataclasses import dataclass

@dataclass
class Success:
    value: str

@dataclass
class Failure:
    error: Exception

Result = Success | Failure  # Python 3.10+ union type
```

---

## 9. Error Handling

| Concept | Swift | Python |
|---------|-------|--------|
| Throw | `throw MyError.notFound` | `raise NotFoundError()` |
| Catch | `do { try f() } catch { }` | `try: f() except: ` |
| Define error | `enum MyError: Error { }` | `class MyError(Exception):` |
| Typed catch | `catch MyError.notFound { }` | `except NotFoundError:` |
| Rethrow | `throws` in signature | Exceptions propagate automatically |
| Try optional | `try? f()` | Wrap in try/except returning None |
| Force try | `try! f()` | No equivalent; just call it |
| Defer | `defer { cleanup() }` | Context managers: `with` or `try/finally` |
| Result type | `Result<Success, Failure>` | Return value or raise exception |

```swift
// Swift
enum NetworkError: Error {
    case notFound
    case timeout
    case serverError(code: Int)
}

func fetchData(url: String) throws -> String {
    guard url.hasPrefix("https") else {
        throw NetworkError.notFound
    }
    return "data"
}

// Handling
do {
    let data = try fetchData(url: "https://api.example.com")
    print(data)
} catch NetworkError.notFound {
    print("Not found")
} catch NetworkError.serverError(let code) {
    print("Server error: \(code)")
} catch {
    print("Other error: \(error)")
}

// try? returns Optional
let maybeData = try? fetchData(url: "bad")  // nil

// defer
func processFile() {
    let file = openFile()
    defer { file.close() }
    // work with file...
}
```

```python
# Python
class NetworkError(Exception):
    pass

class NotFoundError(NetworkError):
    pass

class TimeoutError(NetworkError):
    pass

class ServerError(NetworkError):
    def __init__(self, code: int) -> None:
        self.code = code
        super().__init__(f"Server error: {code}")

def fetch_data(url: str) -> str:
    if not url.startswith("https"):
        raise NotFoundError()
    return "data"

# Handling
try:
    data = fetch_data("https://api.example.com")
    print(data)
except NotFoundError:
    print("Not found")
except ServerError as e:
    print(f"Server error: {e.code}")
except NetworkError as e:
    print(f"Other error: {e}")

# Equivalent of try? (returns None on failure)
def try_fetch(url: str) -> str | None:
    try:
        return fetch_data(url)
    except NetworkError:
        return None

# Context manager (equivalent of defer for resources)
with open("file.txt") as f:
    data = f.read()
    # file is automatically closed
```

---

## 10. Optionals & None

| Concept | Swift | Python |
|---------|-------|--------|
| Optional type | `String?` | `str \| None` or `Optional[str]` |
| Nil / None | `nil` | `None` |
| Check for nil | `if value != nil` | `if value is not None` |
| Optional binding | `if let v = optional { }` | `if (v := optional) is not None:` |
| Guard let | `guard let v = opt else { return }` | `if opt is None: return` then use `opt` |
| Force unwrap | `value!` | No equivalent; just access it (may raise) |
| Nil coalescing | `value ?? default` | `value if value is not None else default` or `value or default` |
| Optional chaining | `obj?.prop?.method()` | No built-in chaining; check each level |
| Map optional | `optional.map { $0 * 2 }` | `x * 2 if x is not None else None` |
| flatMap optional | `optional.flatMap { Int($0) }` | Nested None checks |
| Implicitly unwrapped | `String!` | No equivalent |

```swift
// Swift
var name: String? = "Alice"

// Optional binding
if let name = name {
    print("Hello, \(name)")
}

// Guard let
func greet(_ name: String?) -> String {
    guard let name = name else {
        return "Hello, stranger"
    }
    return "Hello, \(name)"
}

// Nil coalescing
let displayName = name ?? "Unknown"

// Optional chaining
let count = name?.count  // Int?

// Multiple optional binding
if let first = getFirst(), let second = getSecond() {
    print("\(first), \(second)")
}
```

```python
# Python
name: str | None = "Alice"

# Check and use
if name is not None:
    print(f"Hello, {name}")

# Walrus operator (Python 3.8+)
if (n := name) is not None:
    print(f"Hello, {n}")

# Early return (guard equivalent)
def greet(name: str | None) -> str:
    if name is None:
        return "Hello, stranger"
    return f"Hello, {name}"

# None coalescing (careful: `or` also catches empty string, 0, False)
display_name = name if name is not None else "Unknown"
# If falsy values are not a concern:
display_name = name or "Unknown"

# Optional chaining (no built-in syntax; manual checks)
count = len(name) if name is not None else None

# Multiple None checks
first = get_first()
second = get_second()
if first is not None and second is not None:
    print(f"{first}, {second}")
```

---

## 11. Properties

| Concept | Swift | Python |
|---------|-------|--------|
| Stored property | `var name: String` | `self.name: str` in `__init__` |
| Computed (get) | `var area: Double { width * height }` | `@property` |
| Computed (get/set) | `var x: Int { get { } set { } }` | `@property` + `@x.setter` |
| Property observer | `willSet { }` / `didSet { }` | No built-in; use `@property` setter or `__setattr__` |
| Lazy property | `lazy var data = loadData()` | `@cached_property` (3.8+) or manual |
| Static property | `static let shared = MyClass()` | Class variable or `@staticmethod` |
| Read-only | `let name: String` or `private(set)` | `@property` without setter |

```swift
// Swift
class Circle {
    var radius: Double

    // Computed property (read-only)
    var area: Double {
        return .pi * radius * radius
    }

    // Computed property (read-write)
    var diameter: Double {
        get { radius * 2 }
        set { radius = newValue / 2 }
    }

    // Property observer
    var color: String = "red" {
        willSet { print("Changing from \(color) to \(newValue)") }
        didSet { print("Changed from \(oldValue) to \(color)") }
    }

    // Lazy property
    lazy var description: String = {
        return "Circle with radius \(radius)"
    }()

    init(radius: Double) {
        self.radius = radius
    }
}
```

```python
# Python
import math
from functools import cached_property

class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius
        self._color = "red"

    # Computed property (read-only)
    @property
    def area(self) -> float:
        return math.pi * self._radius ** 2

    # Computed property (read-write)
    @property
    def diameter(self) -> float:
        return self._radius * 2

    @diameter.setter
    def diameter(self, value: float) -> None:
        self._radius = value / 2

    # Property with observer-like behavior
    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, new_value: str) -> None:
        print(f"Changing from {self._color} to {new_value}")
        old_value = self._color
        self._color = new_value
        print(f"Changed from {old_value} to {self._color}")

    # Lazy / cached property
    @cached_property
    def description(self) -> str:
        return f"Circle with radius {self._radius}"
```

---

## 12. Generics

| Concept | Swift | Python |
|---------|-------|--------|
| Generic function | `func swap<T>(_ a: inout T, _ b: inout T)` | `def swap(a: T, b: T) -> ...` with `TypeVar` |
| Generic class | `class Stack<Element> { }` | `class Stack(Generic[T]):` or `class Stack[T]:` (3.12+) |
| Type constraint | `func f<T: Comparable>(_ x: T)` | `T = TypeVar("T", bound=Comparable)` |
| Where clause | `where T: Equatable` | Bound on TypeVar |
| Associated type | `associatedtype Item` | Generic protocol with TypeVar |
| Multiple constraints | `<T: Protocol1 & Protocol2>` | Multiple bounds not directly supported; use `Protocol` intersection |

```swift
// Swift
func findIndex<T: Equatable>(of target: T, in array: [T]) -> Int? {
    for (index, element) in array.enumerated() {
        if element == target {
            return index
        }
    }
    return nil
}

class Stack<Element> {
    private var items: [Element] = []

    func push(_ item: Element) {
        items.append(item)
    }

    func pop() -> Element? {
        return items.popLast()
    }

    var isEmpty: Bool {
        return items.isEmpty
    }
}

let intStack = Stack<Int>()
intStack.push(42)
```

```python
# Python 3.12+ (new syntax)
def find_index[T](target: T, collection: list[T]) -> int | None:
    for index, element in enumerate(collection):
        if element == target:
            return index
    return None

class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T | None:
        return self._items.pop() if self._items else None

    @property
    def is_empty(self) -> bool:
        return len(self._items) == 0

int_stack = Stack[int]()
int_stack.push(42)

# Pre-3.12 syntax (still widely used):
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> Optional[T]:
        return self._items.pop() if self._items else None
```

---

## 13. Protocol / Interface

| Concept | Swift | Python |
|---------|-------|--------|
| Define protocol | `protocol Drawable { func draw() }` | `class Drawable(Protocol):` or `class Drawable(ABC):` |
| Conform/implement | `class Circle: Drawable { }` | Implicit with `Protocol`; explicit with `ABC` |
| Protocol extension | `extension Drawable { func defaultDraw() }` | Mixin class or default method in ABC |
| Protocol composition | `Drawable & Printable` | Multiple inheritance |
| Optional requirement | `@objc optional func x()` | Provide default implementation |
| Checking conformance | `value is Drawable` | `isinstance(value, Drawable)` |

```swift
// Swift
protocol Drawable {
    var color: String { get }
    func draw() -> String
}

protocol Resizable {
    func resize(factor: Double)
}

// Protocol extension with default implementation
extension Drawable {
    func description() -> String {
        return "A \(color) drawable"
    }
}

class Circle: Drawable, Resizable {
    var color: String
    var radius: Double

    init(color: String, radius: Double) {
        self.color = color
        self.radius = radius
    }

    func draw() -> String {
        return "Drawing circle with radius \(radius)"
    }

    func resize(factor: Double) {
        radius *= factor
    }
}
```

```python
# Python - Using typing.Protocol (structural subtyping / duck typing)
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    @property
    def color(self) -> str: ...

    def draw(self) -> str: ...

class Resizable(Protocol):
    def resize(self, factor: float) -> None: ...

# No need to explicitly declare conformance
class Circle:
    def __init__(self, color: str, radius: float) -> None:
        self._color = color
        self.radius = radius

    @property
    def color(self) -> str:
        return self._color

    def draw(self) -> str:
        return f"Drawing circle with radius {self.radius}"

    def resize(self, factor: float) -> None:
        self.radius *= factor

# Type checker recognizes Circle as Drawable and Resizable

# Python - Using ABC (nominal subtyping / explicit)
from abc import ABC, abstractmethod

class DrawableABC(ABC):
    @property
    @abstractmethod
    def color(self) -> str: ...

    @abstractmethod
    def draw(self) -> str: ...

    # Default implementation (like Swift protocol extension)
    def description(self) -> str:
        return f"A {self.color} drawable"

class Square(DrawableABC):
    def __init__(self, color: str, side: float) -> None:
        self._color = color
        self.side = side

    @property
    def color(self) -> str:
        return self._color

    def draw(self) -> str:
        return f"Drawing square with side {self.side}"
```

---

## 14. Concurrency

| Concept | Swift | Python |
|---------|-------|--------|
| Async function | `func f() async -> T` | `async def f() -> T:` |
| Await | `let result = await f()` | `result = await f()` |
| Async throws | `func f() async throws -> T` | `async def f() -> T:` (just raise) |
| Task | `Task { await f() }` | `asyncio.create_task(f())` |
| Task group | `withTaskGroup(of:) { }` | `asyncio.gather()` or `TaskGroup` (3.11+) |
| Actor | `actor Counter { }` | No built-in equivalent; use locks |
| Main actor | `@MainActor` | No equivalent |
| Sleep | `try await Task.sleep(nanoseconds:)` | `await asyncio.sleep(seconds)` |
| Run event loop | Automatic (structured concurrency) | `asyncio.run(main())` |
| Async sequence | `for await item in stream { }` | `async for item in stream:` |
| Sendable | `Sendable` protocol | No equivalent |

```swift
// Swift
func fetchUser(id: Int) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

func fetchAllUsers() async throws -> [User] {
    async let user1 = fetchUser(id: 1)
    async let user2 = fetchUser(id: 2)
    async let user3 = fetchUser(id: 3)
    return try await [user1, user2, user3]
}

// Task
Task {
    let users = try await fetchAllUsers()
    print(users)
}

// Actor
actor Counter {
    private var value = 0

    func increment() {
        value += 1
    }

    func getValue() -> Int {
        return value
    }
}
```

```python
# Python
import asyncio
import aiohttp

async def fetch_user(user_id: int) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/users/{user_id}") as resp:
            return await resp.json()

async def fetch_all_users() -> list[dict]:
    # Concurrent execution (like async let)
    return await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    )

# Run the event loop
async def main() -> None:
    users = await fetch_all_users()
    print(users)

asyncio.run(main())

# Task creation
async def background_work() -> None:
    task = asyncio.create_task(fetch_user(1))
    # do other work...
    user = await task

# TaskGroup (Python 3.11+)
async def fetch_with_group() -> list[dict]:
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fetch_user(1))
        t2 = tg.create_task(fetch_user(2))
        t3 = tg.create_task(fetch_user(3))
    return [t1.result(), t2.result(), t3.result()]

# Async iteration
async def read_stream(stream):
    async for chunk in stream:
        process(chunk)
```

---

## 15. Pattern Matching

| Concept | Swift | Python (3.10+) |
|---------|-------|----------------|
| Value match | `case 42:` | `case 42:` |
| Wildcard | `case _:` or `default:` | `case _:` |
| Binding | `case let x:` | `case x:` |
| Tuple match | `case (0, let y):` | `case (0, y):` |
| Enum match | `case .success(let v):` | `case Success(value=v):` |
| Guard/condition | `case let x where x > 0:` | `case x if x > 0:` |
| Multiple | `case 1, 2, 3:` | `case 1 \| 2 \| 3:` |
| Range | `case 0...9:` | Not directly; use guard |
| Type check | `case let s as String:` | `case str() as s:` |
| Nested patterns | Supported | Supported |

```swift
// Swift
enum Shape {
    case circle(radius: Double)
    case rectangle(width: Double, height: Double)
    case triangle(base: Double, height: Double)
}

func describe(_ shape: Shape) -> String {
    switch shape {
    case .circle(let r) where r > 10:
        return "Large circle"
    case .circle(let r):
        return "Circle with radius \(r)"
    case .rectangle(let w, let h) where w == h:
        return "Square with side \(w)"
    case .rectangle(let w, let h):
        return "Rectangle \(w)x\(h)"
    case .triangle(let b, let h):
        return "Triangle with area \(0.5 * b * h)"
    }
}

// Tuple matching
let point = (2, 0)
switch point {
case (0, 0):
    print("Origin")
case (let x, 0):
    print("On x-axis at \(x)")
case (0, let y):
    print("On y-axis at \(y)")
case (let x, let y):
    print("At (\(x), \(y))")
}
```

```python
# Python 3.10+
from dataclasses import dataclass

@dataclass
class Circle:
    radius: float

@dataclass
class Rectangle:
    width: float
    height: float

@dataclass
class Triangle:
    base: float
    height: float

Shape = Circle | Rectangle | Triangle

def describe(shape: Shape) -> str:
    match shape:
        case Circle(radius=r) if r > 10:
            return "Large circle"
        case Circle(radius=r):
            return f"Circle with radius {r}"
        case Rectangle(width=w, height=h) if w == h:
            return f"Square with side {w}"
        case Rectangle(width=w, height=h):
            return f"Rectangle {w}x{h}"
        case Triangle(base=b, height=h):
            return f"Triangle with area {0.5 * b * h}"

# Tuple matching
point = (2, 0)
match point:
    case (0, 0):
        print("Origin")
    case (x, 0):
        print(f"On x-axis at {x}")
    case (0, y):
        print(f"On y-axis at {y}")
    case (x, y):
        print(f"At ({x}, {y})")
```

---

## 16. Memory Management

| Concept | Swift | Python |
|---------|-------|--------|
| Model | ARC (Automatic Reference Counting) | Garbage Collection (reference counting + cycle detector) |
| Retain cycle risk | Yes (use `weak`/`unowned`) | Yes (GC handles most cycles) |
| Weak reference | `weak var delegate: MyProtocol?` | `weakref.ref(obj)` |
| Unowned reference | `unowned let parent: Parent` | No direct equivalent |
| Manual cleanup | `deinit { }` | `__del__` (not guaranteed to run) |
| Deterministic cleanup | Yes (ARC is deterministic) | No (GC timing is nondeterministic) |
| Resource cleanup | `defer { }` | `with` statement (context managers) |
| Value types | Structs, enums (stack allocated) | All objects are heap allocated |

```swift
// Swift - Avoiding retain cycles
class ViewController {
    var onComplete: (() -> Void)?

    func setup() {
        // Capture list prevents retain cycle
        onComplete = { [weak self] in
            guard let self = self else { return }
            self.dismiss()
        }
    }

    deinit {
        print("ViewController deallocated")
    }
}
```

```python
# Python - Weak references
import weakref

class Node:
    def __init__(self, value: int) -> None:
        self.value = value
        self._parent: weakref.ref["Node"] | None = None

    @property
    def parent(self) -> "Node | None":
        return self._parent() if self._parent else None

    @parent.setter
    def parent(self, node: "Node") -> None:
        self._parent = weakref.ref(node)

# Context manager for deterministic cleanup
class DatabaseConnection:
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False

with DatabaseConnection() as db:
    db.query("SELECT * FROM users")
# connection is closed here, guaranteed
```

---

## 17. Package Management

| Concept | Swift (SPM) | Python (uv / pip) |
|---------|-------------|---------------------|
| Package file | `Package.swift` | `pyproject.toml` or `requirements.txt` |
| Add dependency | Add to `Package.swift` dependencies | `uv add package` or `pip install package` |
| Install dependencies | `swift package resolve` | `uv sync` or `pip install -r requirements.txt` |
| Lock file | `Package.resolved` | `uv.lock` or `requirements.txt` (pinned) |
| Run | `swift run` | `uv run script.py` or `python script.py` |
| Build | `swift build` | N/A (interpreted) |
| Test | `swift test` | `uv run pytest` or `pytest` |
| Create project | `swift package init` | `uv init` |
| Virtual env | N/A | `uv venv` or `python -m venv .venv` |
| Registry | Swift Package Index | PyPI (pypi.org) |
| Script deps | N/A | Inline metadata (`# /// script`) with `uv run` |

```swift
// Swift - Package.swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyApp",
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
    ],
    targets: [
        .executableTarget(
            name: "MyApp",
            dependencies: ["Alamofire"]),
        .testTarget(
            name: "MyAppTests",
            dependencies: ["MyApp"]),
    ]
)
```

```toml
# Python - pyproject.toml
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

```bash
# Python - common commands
uv init myproject        # create new project
uv add httpx             # add a dependency
uv remove httpx          # remove a dependency
uv sync                  # install all dependencies
uv run python main.py    # run within the virtual environment
uv run pytest            # run tests
```

---

## 18. Testing

| Concept | Swift (XCTest) | Python (pytest) |
|---------|----------------|-----------------|
| Test file | `MyTests.swift` | `test_my.py` (prefix `test_`) |
| Test class | `class MyTests: XCTestCase` | `class TestMy:` (or just functions) |
| Test method | `func testSomething()` | `def test_something():` |
| Assert equal | `XCTAssertEqual(a, b)` | `assert a == b` |
| Assert true | `XCTAssertTrue(x)` | `assert x` |
| Assert nil | `XCTAssertNil(x)` | `assert x is None` |
| Assert throws | `XCTAssertThrowsError(try f())` | `with pytest.raises(Error):` |
| Setup | `override func setUp()` | `def setup_method(self):` or fixtures |
| Teardown | `override func tearDown()` | `def teardown_method(self):` or fixtures |
| Async test | `func testAsync() async throws` | `@pytest.mark.asyncio async def test_async():` |
| Skip | `throw XCTSkip("reason")` | `@pytest.mark.skip(reason="...")` |
| Parameterize | N/A (manual loop) | `@pytest.mark.parametrize(...)` |
| Run tests | `swift test` | `pytest` |
| Run specific | `swift test --filter testName` | `pytest test_file.py::test_name` |
| Mocking | Protocol-based / manual | `unittest.mock.patch` or `pytest-mock` |

```swift
// Swift - XCTest
import XCTest
@testable import MyApp

class CalculatorTests: XCTestCase {
    var calculator: Calculator!

    override func setUp() {
        super.setUp()
        calculator = Calculator()
    }

    override func tearDown() {
        calculator = nil
        super.tearDown()
    }

    func testAddition() {
        XCTAssertEqual(calculator.add(2, 3), 5)
    }

    func testDivisionByZero() {
        XCTAssertThrowsError(try calculator.divide(10, by: 0)) { error in
            XCTAssertEqual(error as? CalcError, .divisionByZero)
        }
    }

    func testAsyncFetch() async throws {
        let result = try await calculator.fetchRemoteValue()
        XCTAssertGreaterThan(result, 0)
    }
}
```

```python
# Python - pytest
import pytest
from myapp.calculator import Calculator, CalcError

@pytest.fixture
def calculator():
    """Fixture replaces setUp/tearDown."""
    calc = Calculator()
    yield calc
    # teardown code goes here if needed

def test_addition(calculator):
    assert calculator.add(2, 3) == 5

def test_division_by_zero(calculator):
    with pytest.raises(CalcError, match="division by zero"):
        calculator.divide(10, by=0)

@pytest.mark.asyncio
async def test_async_fetch(calculator):
    result = await calculator.fetch_remote_value()
    assert result > 0

# Parametrized tests (no Swift equivalent)
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add_parametrized(calculator, a, b, expected):
    assert calculator.add(a, b) == expected

# Mocking
from unittest.mock import patch

def test_with_mock(calculator):
    with patch.object(calculator, "fetch_remote_value", return_value=42):
        result = calculator.fetch_remote_value()
        assert result == 42
```

---

## 19. Common Patterns

### map / filter / reduce

| Operation | Swift | Python |
|-----------|-------|--------|
| Map | `arr.map { $0 * 2 }` | `[x * 2 for x in arr]` |
| Filter | `arr.filter { $0 > 3 }` | `[x for x in arr if x > 3]` |
| Reduce | `arr.reduce(0, +)` | `from functools import reduce; reduce(lambda a,b: a+b, arr, 0)` or `sum(arr)` |
| CompactMap | `arr.compactMap { Int($0) }` | `[int(x) for x in arr if x.isdigit()]` |
| FlatMap | `arr.flatMap { $0 }` | `[item for sub in arr for item in sub]` |
| Chained | `arr.filter{}.map{}.sorted()` | Comprehensions or `\|` with itertools |
| First match | `arr.first { $0 > 5 }` | `next((x for x in arr if x > 5), None)` |
| All satisfy | `arr.allSatisfy { $0 > 0 }` | `all(x > 0 for x in arr)` |
| Any satisfy | `arr.contains { $0 > 0 }` | `any(x > 0 for x in arr)` |
| Min / Max | `arr.min()`, `arr.max()` | `min(arr)`, `max(arr)` |
| Sort by key | `arr.sorted { $0.name < $1.name }` | `sorted(arr, key=lambda x: x.name)` |
| Group by | `Dictionary(grouping: arr, by: { $0.category })` | `itertools.groupby(sorted(arr, key=f), key=f)` |

```swift
// Swift
let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

let result = numbers
    .filter { $0 % 2 == 0 }    // [2, 4, 6, 8, 10]
    .map { $0 * $0 }            // [4, 16, 36, 64, 100]
    .reduce(0, +)               // 220

let strings = ["1", "two", "3", "four", "5"]
let validNumbers = strings.compactMap { Int($0) }  // [1, 3, 5]
```

```python
# Python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Pythonic: comprehensions
result = sum(x * x for x in numbers if x % 2 == 0)  # 220

# Step by step
evens = [x for x in numbers if x % 2 == 0]    # [2, 4, 6, 8, 10]
squared = [x * x for x in evens]                # [4, 16, 36, 64, 100]
total = sum(squared)                             # 220

# compactMap equivalent
strings = ["1", "two", "3", "four", "5"]
valid_numbers = [int(s) for s in strings if s.isdigit()]  # [1, 3, 5]
```

### Guard / Early Return

```swift
// Swift
func processOrder(_ order: Order?) throws -> Receipt {
    guard let order = order else {
        throw OrderError.missing
    }
    guard order.items.count > 0 else {
        throw OrderError.empty
    }
    guard let payment = order.payment else {
        throw OrderError.noPayment
    }
    guard payment.isValid else {
        throw OrderError.invalidPayment
    }
    return Receipt(order: order, payment: payment)
}
```

```python
# Python
def process_order(order: Order | None) -> Receipt:
    if order is None:
        raise OrderError("missing")
    if len(order.items) == 0:
        raise OrderError("empty")
    if order.payment is None:
        raise OrderError("no payment")
    if not order.payment.is_valid:
        raise OrderError("invalid payment")
    return Receipt(order=order, payment=order.payment)
```

### Codable vs Pydantic

```swift
// Swift - Codable
struct User: Codable {
    let id: Int
    let name: String
    let email: String
    let isActive: Bool

    enum CodingKeys: String, CodingKey {
        case id, name, email
        case isActive = "is_active"
    }
}

// Decode
let json = """
{"id": 1, "name": "Alice", "email": "alice@example.com", "is_active": true}
""".data(using: .utf8)!

let user = try JSONDecoder().decode(User.self, from: json)

// Encode
let data = try JSONEncoder().encode(user)
```

```python
# Python - Pydantic
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = Field(alias="isActive", default=True)

    model_config = {"populate_by_name": True}

# Decode
json_str = '{"id": 1, "name": "Alice", "email": "alice@example.com", "is_active": true}'
user = User.model_validate_json(json_str)

# Encode
json_output = user.model_dump_json()
dict_output = user.model_dump()

# Validation is automatic
try:
    bad_user = User(id="not_a_number", name="Bob", email="bob@example.com")
except ValueError as e:
    print(e)  # validation error
```

### Singleton

```swift
// Swift
class AppConfig {
    static let shared = AppConfig()
    private init() { }

    var apiKey: String = ""
}

AppConfig.shared.apiKey = "abc123"
```

```python
# Python - module-level (simplest, most Pythonic)
# config.py
api_key: str = ""

# Or class-based singleton
class AppConfig:
    _instance: "AppConfig | None" = None

    def __new__(cls) -> "AppConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.api_key = ""
        return cls._instance

config = AppConfig()
config.api_key = "abc123"
```

### Builder / Fluent API

```swift
// Swift
class RequestBuilder {
    private var url: String = ""
    private var method: String = "GET"
    private var headers: [String: String] = [:]

    func setURL(_ url: String) -> RequestBuilder {
        self.url = url
        return self
    }

    func setMethod(_ method: String) -> RequestBuilder {
        self.method = method
        return self
    }

    func addHeader(_ key: String, _ value: String) -> RequestBuilder {
        self.headers[key] = value
        return self
    }

    func build() -> URLRequest { ... }
}

let request = RequestBuilder()
    .setURL("https://api.example.com")
    .setMethod("POST")
    .addHeader("Authorization", "Bearer token")
    .build()
```

```python
# Python - using dataclass with builder methods
from dataclasses import dataclass, field
from typing import Self

@dataclass
class RequestBuilder:
    _url: str = ""
    _method: str = "GET"
    _headers: dict[str, str] = field(default_factory=dict)

    def set_url(self, url: str) -> Self:
        self._url = url
        return self

    def set_method(self, method: str) -> Self:
        self._method = method
        return self

    def add_header(self, key: str, value: str) -> Self:
        self._headers[key] = value
        return self

    def build(self) -> Request: ...

request = (
    RequestBuilder()
    .set_url("https://api.example.com")
    .set_method("POST")
    .add_header("Authorization", "Bearer token")
    .build()
)
```

---

## Quick Reference: Naming Conventions

| Context | Swift | Python |
|---------|-------|--------|
| Variables | `camelCase` | `snake_case` |
| Constants | `camelCase` | `UPPER_SNAKE_CASE` |
| Functions | `camelCase` | `snake_case` |
| Classes | `PascalCase` | `PascalCase` |
| Protocols/Interfaces | `PascalCase` (often `-able` suffix) | `PascalCase` |
| Enums | `PascalCase` | `PascalCase` |
| Enum cases | `camelCase` | `UPPER_SNAKE_CASE` |
| Files | `PascalCase.swift` | `snake_case.py` |
| Modules/Packages | `PascalCase` | `snake_case` |
| Private | `private` keyword | `_leading_underscore` convention |
| Boolean names | `isActive`, `hasValue` | `is_active`, `has_value` |

---

## Quick Reference: Operators

| Operator | Swift | Python |
|----------|-------|--------|
| Integer division | `a / b` (for Int) | `a // b` |
| Remainder | `a % b` | `a % b` |
| Power | `pow(a, b)` | `a ** b` |
| Nil coalescing | `a ?? b` | `a if a is not None else b` |
| Range (exclusive) | `0..<n` | `range(n)` |
| Range (inclusive) | `0...n` | `range(n + 1)` |
| Type check | `x is T` | `isinstance(x, T)` |
| Type cast | `x as? T` / `x as! T` | `cast(T, x)` (typing) or just use |
| Identity | `===` | `is` |
| Equality | `==` | `==` |
| Logical AND | `&&` | `and` |
| Logical OR | `\|\|` | `or` |
| Logical NOT | `!` | `not` |
| Bitwise AND | `&` | `&` |
| Bitwise OR | `\|` | `\|` |
| String in | `str.contains(s)` | `s in str` |
