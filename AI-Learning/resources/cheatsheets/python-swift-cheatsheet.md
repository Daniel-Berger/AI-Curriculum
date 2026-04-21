# Python <-> Swift Cheatsheet

A side-by-side reference for developers working in both languages. Python 3.10+ and Swift 5.9+ syntax.

---

## Variables & Constants

| Concept | Python | Swift |
|---------|--------|-------|
| Variable | `x = 10` | `var x = 10` |
| Constant | `X = 10` (convention only) | `let x = 10` (enforced by compiler) |
| Type annotation | `x: int = 10` | `var x: Int = 10` |
| Multiple assignment | `a, b = 1, 2` | `let (a, b) = (1, 2)` |
| Type alias | `Vector = list[float]` | `typealias Vector = [Double]` |

```python
# Python
name = "Alice"          # mutable
PI = 3.14159            # constant by convention (ALL_CAPS)
count: int = 0          # type hint (not enforced at runtime)
```

```swift
// Swift
var name = "Alice"      // mutable
let pi = 3.14159        // immutable (compiler-enforced)
var count: Int = 0      // explicit type annotation
```

---

## Strings & String Interpolation

| Concept | Python | Swift |
|---------|--------|-------|
| String literal | `"hello"` or `'hello'` | `"hello"` |
| Multi-line | `"""..."""` | `"""..."""` |
| Interpolation | `f"Hello, {name}"` | `"Hello, \(name)"` |
| Concatenation | `"a" + "b"` | `"a" + "b"` |
| Length | `len(s)` | `s.count` |
| Contains | `"lo" in s` | `s.contains("lo")` |
| Split | `s.split(",")` | `s.split(separator: ",")` |
| Strip/Trim | `s.strip()` | `s.trimmingCharacters(in: .whitespaces)` |
| Uppercase | `s.upper()` | `s.uppercased()` |
| Replace | `s.replace("a", "b")` | `s.replacingOccurrences(of: "a", with: "b")` |
| Starts with | `s.startswith("He")` | `s.hasPrefix("He")` |
| Ends with | `s.endswith("lo")` | `s.hasSuffix("lo")` |
| Character at index | `s[0]` | `s[s.startIndex]` |
| Substring | `s[1:4]` | `s[s.index(after: s.startIndex)...]` |

```python
# Python
name = "World"
greeting = f"Hello, {name}! {2 + 2} is four."
multiline = """
Line 1
Line 2
"""
```

```swift
// Swift
let name = "World"
let greeting = "Hello, \(name)! \(2 + 2) is four."
let multiline = """
Line 1
Line 2
"""
```

---

## Arrays / Lists

| Concept | Python (list) | Swift (Array) |
|---------|--------------|---------------|
| Create | `nums = [1, 2, 3]` | `var nums = [1, 2, 3]` |
| Empty | `nums = []` or `list()` | `var nums: [Int] = []` or `[Int]()` |
| Type | `list[int]` (hint) | `[Int]` or `Array<Int>` |
| Access | `nums[0]` | `nums[0]` |
| Last | `nums[-1]` | `nums.last` (returns Optional) |
| Append | `nums.append(4)` | `nums.append(4)` |
| Insert | `nums.insert(0, 99)` | `nums.insert(99, at: 0)` |
| Remove | `nums.remove(3)` (by value) | `nums.remove(at: 0)` (by index) |
| Pop last | `nums.pop()` | `nums.removeLast()` |
| Length | `len(nums)` | `nums.count` |
| Slice | `nums[1:3]` | `Array(nums[1..<3])` |
| Contains | `3 in nums` | `nums.contains(3)` |
| Sort (in-place) | `nums.sort()` | `nums.sort()` |
| Sorted (copy) | `sorted(nums)` | `nums.sorted()` |
| Reverse | `nums.reverse()` | `nums.reverse()` |
| Concatenate | `a + b` | `a + b` |

```python
# Python
fruits = ["apple", "banana", "cherry"]
fruits.append("date")
first = fruits[0]           # "apple"
last = fruits[-1]           # "date"
sliced = fruits[1:3]        # ["banana", "cherry"]
```

```swift
// Swift
var fruits = ["apple", "banana", "cherry"]
fruits.append("date")
let first = fruits[0]       // "apple"
let last = fruits.last!     // "date" (force unwrap Optional)
let sliced = Array(fruits[1..<3])  // ["banana", "cherry"]
```

---

## Dictionaries

| Concept | Python (dict) | Swift (Dictionary) |
|---------|--------------|-------------------|
| Create | `d = {"a": 1, "b": 2}` | `var d = ["a": 1, "b": 2]` |
| Empty | `d = {}` | `var d: [String: Int] = [:]` |
| Access | `d["a"]` (KeyError if missing) | `d["a"]` (returns Optional) |
| Default | `d.get("c", 0)` | `d["c", default: 0]` |
| Set | `d["c"] = 3` | `d["c"] = 3` |
| Delete | `del d["a"]` | `d["a"] = nil` or `d.removeValue(forKey: "a")` |
| Keys | `d.keys()` | `d.keys` |
| Values | `d.values()` | `d.values` |
| Items/Pairs | `d.items()` | `d` (iterate directly) |
| Length | `len(d)` | `d.count` |
| Contains key | `"a" in d` | `d["a"] != nil` or `d.keys.contains("a")` |
| Merge | `d.update(other)` or `d \| other` | `d.merge(other) { _, new in new }` |

```python
# Python
scores = {"alice": 95, "bob": 87}
alice_score = scores.get("alice", 0)  # 95
scores["charlie"] = 91
for name, score in scores.items():
    print(f"{name}: {score}")
```

```swift
// Swift
var scores = ["alice": 95, "bob": 87]
let aliceScore = scores["alice", default: 0]  // 95
scores["charlie"] = 91
for (name, score) in scores {
    print("\(name): \(score)")
}
```

---

## Sets

| Concept | Python | Swift |
|---------|--------|-------|
| Create | `s = {1, 2, 3}` | `var s: Set = [1, 2, 3]` |
| Empty | `s = set()` | `var s: Set<Int> = []` |
| Add | `s.add(4)` | `s.insert(4)` |
| Remove | `s.remove(1)` | `s.remove(1)` |
| Contains | `1 in s` | `s.contains(1)` |
| Union | `a \| b` or `a.union(b)` | `a.union(b)` |
| Intersection | `a & b` or `a.intersection(b)` | `a.intersection(b)` |
| Difference | `a - b` or `a.difference(b)` | `a.subtracting(b)` |
| Symmetric diff | `a ^ b` | `a.symmetricDifference(b)` |
| Subset | `a <= b` or `a.issubset(b)` | `a.isSubset(of: b)` |

---

## Optionals / None Handling

| Concept | Python | Swift |
|---------|--------|-------|
| Null value | `None` | `nil` |
| Nullable type | `Optional[str]` or `str \| None` | `String?` (Optional<String>) |
| Check null | `if x is None` | `if x == nil` |
| Check not null | `if x is not None` | `if let x = x { ... }` |
| Default value | `x or default` | `x ?? default` |
| Force access | N/A (no concept) | `x!` (crashes if nil) |
| Safe chaining | `x and x.method()` | `x?.method()` |

```python
# Python
from typing import Optional

def find_user(id: int) -> Optional[str]:
    users = {1: "Alice", 2: "Bob"}
    return users.get(id)  # Returns None if not found

name = find_user(1)
if name is not None:
    print(f"Found: {name}")
display_name = name or "Unknown"
```

```swift
// Swift
func findUser(id: Int) -> String? {
    let users = [1: "Alice", 2: "Bob"]
    return users[id]  // Returns nil if not found
}

let name = findUser(id: 1)
if let name = name {         // Optional binding
    print("Found: \(name)")
}
let displayName = name ?? "Unknown"   // Nil coalescing
```

---

## Control Flow

### If/Else

```python
# Python
if x > 10:
    print("big")
elif x > 5:
    print("medium")
else:
    print("small")

# Ternary
result = "even" if x % 2 == 0 else "odd"
```

```swift
// Swift
if x > 10 {
    print("big")
} else if x > 5 {
    print("medium")
} else {
    print("small")
}

// Ternary
let result = x % 2 == 0 ? "even" : "odd"
```

### Loops

```python
# Python
for i in range(5):           # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 10, 2):   # 1, 3, 5, 7, 9
    print(i)

for item in items:
    print(item)

while count > 0:
    count -= 1

# List comprehension
squares = [x**2 for x in range(10)]
```

```swift
// Swift
for i in 0..<5 {             // 0, 1, 2, 3, 4
    print(i)
}

for i in stride(from: 1, to: 10, by: 2) {  // 1, 3, 5, 7, 9
    print(i)
}

for item in items {
    print(item)
}

while count > 0 {
    count -= 1
}

// Map equivalent of list comprehension
let squares = (0..<10).map { $0 * $0 }
```

### Guard (Swift-specific)

```swift
// Swift - guard for early exit
func process(name: String?) {
    guard let name = name else {
        print("No name provided")
        return
    }
    // name is now unwrapped and available
    print("Hello, \(name)")
}
```

```python
# Python equivalent pattern
def process(name: str | None) -> None:
    if name is None:
        print("No name provided")
        return
    # name is known to be str here (by type narrowing)
    print(f"Hello, {name}")
```

---

## Functions & Closures

### Functions

```python
# Python
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

result = greet("Alice")
result = greet("Alice", greeting="Hi")  # keyword argument

# *args and **kwargs
def flexible(*args, **kwargs):
    print(args, kwargs)
```

```swift
// Swift
func greet(name: String, greeting: String = "Hello") -> String {
    return "\(greeting), \(name)!"
}

let result = greet(name: "Alice")
let result2 = greet(name: "Alice", greeting: "Hi")

// Variadic parameters
func flexible(_ items: Int...) {
    print(items)  // items is [Int]
}

// External/internal parameter names
func move(from start: Int, to end: Int) { }
move(from: 0, to: 10)
```

### Closures / Lambdas

```python
# Python
square = lambda x: x ** 2

# Multi-line: use regular function
def transform(items, func):
    return [func(x) for x in items]

result = transform([1, 2, 3], lambda x: x * 2)
```

```swift
// Swift
let square = { (x: Int) -> Int in return x * x }

// Trailing closure syntax
let result = [1, 2, 3].map { $0 * 2 }

// Multi-line closure
let result2 = [1, 2, 3].map { number -> Int in
    let doubled = number * 2
    return doubled + 1
}

// Closure as function parameter
func transform(_ items: [Int], using func: (Int) -> Int) -> [Int] {
    items.map(func)
}
```

---

## Classes & Structs / Dataclasses

### Classes

```python
# Python
class Animal:
    def __init__(self, name: str, sound: str):
        self.name = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name} says {self.sound}"

    def __str__(self) -> str:
        return f"Animal({self.name})"

class Dog(Animal):
    def __init__(self, name: str):
        super().__init__(name, "Woof")

    def fetch(self) -> str:
        return f"{self.name} fetches the ball"
```

```swift
// Swift
class Animal {
    let name: String
    let sound: String

    init(name: String, sound: String) {
        self.name = name
        self.sound = sound
    }

    func speak() -> String {
        "\(name) says \(sound)"
    }

    var description: String {
        "Animal(\(name))"
    }
}

class Dog: Animal {
    init(name: String) {
        super.init(name: name, sound: "Woof")
    }

    func fetch() -> String {
        "\(name) fetches the ball"
    }
}
```

### Structs / Dataclasses

```python
# Python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

    def distance_to_origin(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

@dataclass(frozen=True)  # immutable
class Color:
    r: int
    g: int
    b: int

p = Point(3.0, 4.0)
print(p)                    # Point(x=3.0, y=4.0) (auto __repr__)
print(p == Point(3.0, 4.0)) # True (auto __eq__)
```

```swift
// Swift
struct Point {
    var x: Double
    var y: Double

    func distanceToOrigin() -> Double {
        (x * x + y * y).squareRoot()
    }
}

struct Color {  // structs are value types by default
    let r: Int  // use 'let' for immutable properties
    let g: Int
    let b: Int
}

var p = Point(x: 3.0, y: 4.0)  // auto-generated memberwise init
print(p)                         // Point(x: 3.0, y: 4.0)
print(p == Point(x: 3.0, y: 4.0)) // requires Equatable conformance
```

**Key difference**: Swift structs are value types (copied on assignment). Python dataclasses are reference types. Swift classes are reference types.

---

## Error Handling

```python
# Python
class InsufficientFundsError(Exception):
    def __init__(self, balance: float, amount: float):
        self.balance = balance
        self.amount = amount
        super().__init__(f"Cannot withdraw {amount}, balance is {balance}")

def withdraw(balance: float, amount: float) -> float:
    if amount > balance:
        raise InsufficientFundsError(balance, amount)
    return balance - amount

try:
    new_balance = withdraw(100, 200)
except InsufficientFundsError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected: {e}")
else:
    print(f"New balance: {new_balance}")
finally:
    print("Done")
```

```swift
// Swift
enum BankError: Error {
    case insufficientFunds(balance: Double, amount: Double)
}

func withdraw(balance: Double, amount: Double) throws -> Double {
    guard amount <= balance else {
        throw BankError.insufficientFunds(balance: balance, amount: amount)
    }
    return balance - amount
}

do {
    let newBalance = try withdraw(balance: 100, amount: 200)
    print("New balance: \(newBalance)")
} catch BankError.insufficientFunds(let balance, let amount) {
    print("Cannot withdraw \(amount), balance is \(balance)")
} catch {
    print("Unexpected: \(error)")
}

// try? returns Optional (nil on error)
let result = try? withdraw(balance: 100, amount: 200)

// try! crashes on error (like force unwrap)
let result2 = try! withdraw(balance: 100, amount: 50)
```

---

## Pattern Matching

```python
# Python (3.10+ match statement)
def describe(value):
    match value:
        case 0:
            return "zero"
        case int(x) if x > 0:
            return f"positive: {x}"
        case int(x):
            return f"negative: {x}"
        case str(s):
            return f"string: {s}"
        case [first, *rest]:
            return f"list starting with {first}"
        case {"name": name, "age": age}:
            return f"{name} is {age}"
        case _:
            return "unknown"
```

```swift
// Swift (switch statement - must be exhaustive)
func describe(_ value: Any) -> String {
    switch value {
    case 0:
        return "zero"
    case let x as Int where x > 0:
        return "positive: \(x)"
    case let x as Int:
        return "negative: \(x)"
    case let s as String:
        return "string: \(s)"
    default:
        return "unknown"
    }
}

// Swift enum pattern matching (more common and powerful)
enum Shape {
    case circle(radius: Double)
    case rectangle(width: Double, height: Double)
    case triangle(base: Double, height: Double)
}

func area(_ shape: Shape) -> Double {
    switch shape {
    case .circle(let r):
        return .pi * r * r
    case .rectangle(let w, let h):
        return w * h
    case .triangle(let b, let h):
        return 0.5 * b * h
    }
}
```

---

## Protocols / ABCs

```python
# Python (Abstract Base Classes)
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self) -> str:
        pass

    def description(self) -> str:  # default implementation
        return f"Drawable: {self.draw()}"

class Circle(Drawable):
    def __init__(self, radius: float):
        self.radius = radius

    def draw(self) -> str:
        return f"Circle with radius {self.radius}"

# Protocol (Python 3.8+ - structural typing)
from typing import Protocol

class Printable(Protocol):
    def to_string(self) -> str: ...

def print_item(item: Printable) -> None:
    print(item.to_string())
```

```swift
// Swift (Protocols)
protocol Drawable {
    func draw() -> String
}

extension Drawable {  // default implementation
    func description() -> String {
        "Drawable: \(draw())"
    }
}

struct Circle: Drawable {
    let radius: Double

    func draw() -> String {
        "Circle with radius \(radius)"
    }
}

// Protocol with associated type (like generic ABC)
protocol Container {
    associatedtype Item
    var count: Int { get }
    mutating func append(_ item: Item)
    subscript(i: Int) -> Item { get }
}
```

---

## Generics

```python
# Python
from typing import TypeVar, Generic

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self):
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0

# Python 3.12+ simplified syntax
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None

# Constrained generic
from typing import Comparable
def max_item[T: Comparable](a: T, b: T) -> T:
    return a if a > b else b
```

```swift
// Swift
struct Stack<Element> {
    private var items: [Element] = []

    mutating func push(_ item: Element) {
        items.append(item)
    }

    mutating func pop() -> Element {
        items.removeLast()
    }

    var isEmpty: Bool {
        items.isEmpty
    }
}

func first<T>(_ items: [T]) -> T? {
    items.first
}

// Constrained generic
func maxItem<T: Comparable>(_ a: T, _ b: T) -> T {
    a > b ? a : b
}

// Multiple constraints
func process<T: Hashable & Codable>(_ item: T) { }

// Where clause
func allMatch<C: Collection>(_ collection: C, _ predicate: (C.Element) -> Bool) -> Bool
    where C.Element: Equatable {
    collection.allSatisfy(predicate)
}
```

---

## Common Operations: map, filter, reduce, sort, enumerate

### Map

```python
# Python
nums = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, nums))
doubled = [x * 2 for x in nums]              # preferred
```

```swift
// Swift
let nums = [1, 2, 3, 4, 5]
let doubled = nums.map { $0 * 2 }
```

### Filter

```python
# Python
evens = list(filter(lambda x: x % 2 == 0, nums))
evens = [x for x in nums if x % 2 == 0]      # preferred
```

```swift
// Swift
let evens = nums.filter { $0 % 2 == 0 }
```

### Reduce

```python
# Python
from functools import reduce
total = reduce(lambda acc, x: acc + x, nums, 0)
total = sum(nums)                               # preferred for sum
```

```swift
// Swift
let total = nums.reduce(0) { $0 + $1 }
let total2 = nums.reduce(0, +)                 // shorthand
```

### Sort

```python
# Python
names = ["Charlie", "Alice", "Bob"]
names.sort()                          # in-place, ascending
sorted_names = sorted(names)          # returns new list
sorted_desc = sorted(names, reverse=True)
sorted_by_len = sorted(names, key=len)
```

```swift
// Swift
var names = ["Charlie", "Alice", "Bob"]
names.sort()                          // in-place, ascending
let sortedNames = names.sorted()      // returns new array
let sortedDesc = names.sorted(by: >)
let sortedByLen = names.sorted { $0.count < $1.count }
```

### Enumerate

```python
# Python
for i, name in enumerate(names):
    print(f"{i}: {name}")

for i, name in enumerate(names, start=1):
    print(f"{i}: {name}")
```

```swift
// Swift
for (i, name) in names.enumerated() {
    print("\(i): \(name)")
}

// Starting from a different index
for (i, name) in names.enumerated() {
    print("\(i + 1): \(name)")
}
```

### Chaining Operations

```python
# Python
result = [
    name.upper()
    for name in names
    if len(name) > 3
]
# or
result = list(map(str.upper, filter(lambda n: len(n) > 3, names)))
```

```swift
// Swift
let result = names
    .filter { $0.count > 3 }
    .map { $0.uppercased() }
```

### FlatMap / CompactMap

```python
# Python
nested = [[1, 2], [3, 4], [5]]
flat = [x for sublist in nested for x in sublist]  # [1, 2, 3, 4, 5]

# Filter None values
items = [1, None, 3, None, 5]
valid = [x for x in items if x is not None]        # [1, 3, 5]
```

```swift
// Swift
let nested = [[1, 2], [3, 4], [5]]
let flat = nested.flatMap { $0 }                    // [1, 2, 3, 4, 5]

// Filter nil values (compactMap)
let items: [Int?] = [1, nil, 3, nil, 5]
let valid = items.compactMap { $0 }                 // [1, 3, 5]
```

### Zip

```python
# Python
names = ["Alice", "Bob"]
scores = [95, 87]
pairs = list(zip(names, scores))      # [("Alice", 95), ("Bob", 87)]
name_dict = dict(zip(names, scores))  # {"Alice": 95, "Bob": 87}
```

```swift
// Swift
let names = ["Alice", "Bob"]
let scores = [95, 87]
let pairs = Array(zip(names, scores)) // [("Alice", 95), ("Bob", 87)]
let nameDict = Dictionary(uniqueKeysWithValues: zip(names, scores))
```

---

## Quick Reference: Key Differences

| Concept | Python | Swift |
|---------|--------|-------|
| Null | `None` | `nil` |
| Boolean | `True` / `False` | `true` / `false` |
| Print | `print()` | `print()` |
| String format | `f"..."` | `"\(...)"` |
| Type check | `isinstance(x, int)` | `x is Int` |
| Type cast | `int(x)` | `x as? Int` |
| Range | `range(0, 5)` | `0..<5` |
| Inclusive range | `range(0, 6)` | `0...5` |
| Identity check | `a is b` | `a === b` (reference types) |
| Equality | `a == b` | `a == b` |
| Not | `not x` | `!x` |
| And / Or | `and` / `or` | `&&` / `\|\|` |
| Entry point | `if __name__ == "__main__":` | `@main` attribute |
| Package manager | `pip` / `poetry` | Swift Package Manager |
| REPL | `python` | `swift` |
