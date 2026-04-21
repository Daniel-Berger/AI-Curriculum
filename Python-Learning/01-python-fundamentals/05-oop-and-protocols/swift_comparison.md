# Swift vs Python: OOP and Protocols

A side-by-side comparison for Swift/iOS developers learning Python.

---

## 1. Swift Protocol vs Python Protocol / ABC

| Feature | Swift Protocol | Python `typing.Protocol` | Python `ABC` |
|---------|---------------|-------------------------|-------------|
| Conformance | Explicit (`: MyProtocol`) | Implicit (structural) | Explicit (`(MyABC)`) |
| Type checking | Compile-time | Static (mypy) | Runtime |
| Default implementations | Via extensions | Possible but uncommon | Yes |
| Associated types | `associatedtype` | `TypeVar` | N/A |
| Requirements | Methods, properties, inits | Methods, properties | Methods, properties |
| Multiple conformance | Yes | Yes | Yes (multiple inheritance) |
| Self requirement | Yes | Yes | No |

### Swift Protocol

```swift
protocol Drawable {
    func draw() -> String
}

// Explicit conformance
struct Circle: Drawable {
    let radius: Double
    func draw() -> String { "Drawing circle with radius \(radius)" }
}

// Protocol extension (default implementation)
extension Drawable {
    func drawTwice() -> String { draw() + "\n" + draw() }
}
```

### Python typing.Protocol (Structural)

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

# NO explicit conformance -- structural typing
class Circle:
    def __init__(self, radius: float):
        self.radius = radius

    def draw(self) -> str:
        return f"Drawing circle with radius {self.radius}"

# Circle satisfies Drawable because it has a draw() method
def render(item: Drawable) -> None:
    print(item.draw())

render(Circle(5.0))  # Works! No inheritance needed
```

### Python ABC (Nominal)

```python
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self) -> str: ...

    # Default implementation (like Swift protocol extension)
    def draw_twice(self) -> str:
        return self.draw() + "\n" + self.draw()

# MUST explicitly inherit
class Circle(Drawable):
    def __init__(self, radius: float):
        self.radius = radius

    def draw(self) -> str:
        return f"Drawing circle with radius {self.radius}"
```

### When to Use Each

| Use Case | Recommended Approach |
|----------|---------------------|
| Third-party type conformance | `Protocol` (structural, no inheritance needed) |
| Enforcing implementation at instantiation | `ABC` (raises TypeError if abstract methods missing) |
| Type hints for duck typing | `Protocol` |
| Mixin with default behavior | `ABC` or mixin class |

---

## 2. Swift Struct vs Python Dataclass

| Feature | Swift `struct` | Python `@dataclass` | Python `@dataclass(frozen=True)` |
|---------|---------------|--------------------|---------------------------------|
| Value/Reference | Value type | Reference type | Reference type (immutable) |
| Auto `init` | Yes (memberwise) | Yes | Yes |
| Auto `Equatable` | Synthesized | Auto `__eq__` | Auto `__eq__` + `__hash__` |
| Auto `Hashable` | Synthesized | Only if `frozen=True` or `unsafe_hash=True` | Yes |
| Auto `description` | No (need CustomStringConvertible) | Auto `__repr__` | Auto `__repr__` |
| Mutability | `let` = immutable, `var` = mutable | Mutable by default | Immutable (`frozen`) |
| Copy behavior | Automatic (value type) | Manual (`.copy()` or `copy.deepcopy`) | Sharing is safe (immutable) |

### Swift Struct

```swift
struct Point: Equatable, Hashable, CustomStringConvertible {
    let x: Double
    let y: Double

    var description: String { "Point(x: \(x), y: \(y))" }

    func distanceTo(_ other: Point) -> Double {
        sqrt(pow(x - other.x, 2) + pow(y - other.y, 2))
    }
}

let p1 = Point(x: 0, y: 0)
let p2 = Point(x: 3, y: 4)
p1 == p2                    // false (Equatable)
p1.distanceTo(p2)          // 5.0
var set: Set<Point> = [p1]  // Hashable
```

### Python Dataclass

```python
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

p1 = Point(0, 0)
p2 = Point(3, 4)
p1 == p2                 # False (__eq__)
p1.distance_to(p2)      # 5.0
{p1, p2}                # Set works (frozen -> hashable)
print(p1)               # Point(x=0, y=0) (__repr__)
```

### Advanced Dataclass Features

```python
from dataclasses import dataclass, field

@dataclass(order=True, frozen=True)  # Auto <, <=, >, >= from fields
class Version:
    major: int
    minor: int
    patch: int

@dataclass
class Config:
    name: str
    tags: list[str] = field(default_factory=list)  # Mutable default
    _id: int = field(init=False, repr=False)        # Excluded from init and repr

    def __post_init__(self):
        self._id = hash(self.name)
```

---

## 3. Enum Comparison

| Feature | Swift `enum` | Python `Enum` |
|---------|-------------|---------------|
| Raw values | `case red = 1` | `RED = 1` |
| Auto values | N/A | `auto()` |
| Associated values | `case point(x: Int, y: Int)` | Not supported (use dataclass) |
| Methods | Yes | Yes |
| Computed properties | Yes | Yes (`@property`) |
| Pattern matching | `switch/case` with binding | `match/case` (3.10+) |
| String enum | `String` raw value | `StrEnum` (3.11+) |
| Iteration | `CaseIterable` | Built-in (`for x in MyEnum`) |
| From raw value | `Color(rawValue: 1)` | `Color(1)` |
| From name | N/A | `Color["RED"]` |

### Swift Enum

```swift
enum Direction: String, CaseIterable {
    case north, south, east, west

    var opposite: Direction {
        switch self {
        case .north: return .south
        case .south: return .north
        case .east: return .west
        case .west: return .east
        }
    }
}

// Associated values (not possible in Python Enum)
enum Result<T> {
    case success(T)
    case failure(Error)
}
```

### Python Enum

```python
from enum import Enum, StrEnum, auto

class Direction(StrEnum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    @property
    def opposite(self) -> "Direction":
        opposites = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }
        return opposites[self]

# For associated-value-like patterns, use dataclasses or unions:
from dataclasses import dataclass

@dataclass
class Success:
    value: object

@dataclass
class Failure:
    error: Exception

Result = Success | Failure  # Union type (Python 3.10+)
```

---

## 4. Equatable / Hashable vs `__eq__` / `__hash__`

| Concept | Swift | Python |
|---------|-------|--------|
| Equality | `Equatable` protocol, `==` operator | `__eq__` dunder method |
| Hashing | `Hashable` protocol, `hash(into:)` | `__hash__` dunder method |
| Auto-synthesis | Structs, enums with Equatable | `@dataclass` auto-generates |
| Set/Dict key | Requires Hashable | Requires `__hash__` + `__eq__` |
| Default behavior | No default (must conform) | `__eq__` checks identity by default |

### Swift

```swift
struct Card: Equatable, Hashable {
    let rank: String
    let suit: String

    // Equatable auto-synthesized for simple structs
    // Hashable auto-synthesized for simple structs
}

let c1 = Card(rank: "Ace", suit: "Spades")
let c2 = Card(rank: "Ace", suit: "Spades")
c1 == c2        // true
Set([c1, c2])   // 1 element
```

### Python

```python
@dataclass(frozen=True)
class Card:
    rank: str
    suit: str
    # __eq__ and __hash__ auto-generated by @dataclass(frozen=True)

c1 = Card("Ace", "Spades")
c2 = Card("Ace", "Spades")
c1 == c2         # True
{c1, c2}         # 1 element

# Manual implementation:
class Card:
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))
```

---

## 5. Codable vs Dataclass Serialization

| Feature | Swift `Codable` | Python `dataclass` | Python `Pydantic` |
|---------|----------------|-------------------|--------------------|
| JSON encode | `JSONEncoder().encode(obj)` | Manual or `dataclasses.asdict` + `json` | `model.model_dump_json()` |
| JSON decode | `JSONDecoder().decode(T.self, from:)` | Manual `from_dict` classmethod | `Model.model_validate_json()` |
| Key mapping | `CodingKeys` enum | Manual | `Field(alias=...)` |
| Validation | Type-checked at decode time | No built-in validation | Rich validators |
| Nested models | Automatic | Manual | Automatic |
| Custom encoding | `encode(to:)` | Manual | `model_serializer` |

### Swift Codable

```swift
struct User: Codable {
    let name: String
    let email: String
    let age: Int
}

// Encode
let user = User(name: "Alice", email: "a@b.com", age: 30)
let data = try JSONEncoder().encode(user)

// Decode
let decoded = try JSONDecoder().decode(User.self, from: data)
```

### Python Dataclass (Manual)

```python
from dataclasses import dataclass, asdict
import json

@dataclass
class User:
    name: str
    email: str
    age: int

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "User":
        return cls(**json.loads(json_str))

user = User("Alice", "a@b.com", 30)
j = user.to_json()
decoded = User.from_json(j)
```

### Python Pydantic (Recommended for Production)

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int

user = User(name="Alice", email="a@b.com", age=30)
j = user.model_dump_json()              # Encode
decoded = User.model_validate_json(j)   # Decode with validation
```

---

## 6. Computed Properties vs @property

| Feature | Swift | Python |
|---------|-------|--------|
| Read-only computed | `var x: T { return ... }` | `@property` |
| Read-write computed | `var x: T { get { } set { } }` | `@property` + `@x.setter` |
| Stored property observers | `willSet`, `didSet` | `@x.setter` (manual) |
| Lazy properties | `lazy var` | `@functools.cached_property` |
| Delete property | N/A | `@x.deleter` |

### Swift

```swift
class Circle {
    var radius: Double {
        didSet {
            print("Radius changed to \(radius)")
        }
    }

    var area: Double {
        return .pi * radius * radius
    }

    var diameter: Double {
        get { radius * 2 }
        set { radius = newValue / 2 }
    }

    lazy var expensiveComputation: Double = {
        // Computed once on first access
        return (0..<1000000).reduce(0, +)
    }()
}
```

### Python

```python
from functools import cached_property

class Circle:
    def __init__(self, radius: float):
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        print(f"Radius changed to {value}")
        self._radius = value

    @property
    def area(self) -> float:
        return math.pi * self._radius ** 2

    @property
    def diameter(self) -> float:
        return self._radius * 2

    @diameter.setter
    def diameter(self, value: float) -> None:
        self._radius = value / 2

    @cached_property
    def expensive_computation(self) -> float:
        return sum(range(1_000_000))
```

---

## 7. Extensions vs Mixins

| Feature | Swift Extension | Python Mixin |
|---------|----------------|-------------|
| Add methods to existing type | Yes | No (must subclass) |
| Protocol conformance | Yes (retroactive) | Via multiple inheritance |
| Add stored properties | No | Yes (mixins are classes) |
| Apply to built-in types | Yes | No (generally) |
| Syntax | `extension Type { }` | `class My(Mixin, Base):` |

### Swift Extension

```swift
// Add functionality to an existing type
extension String {
    var isPalindrome: Bool {
        self == String(self.reversed())
    }
}

"racecar".isPalindrome  // true

// Retroactive protocol conformance
extension Int: MyProtocol {
    func myMethod() -> String { "\(self)" }
}
```

### Python Mixin

```python
class JSONMixin:
    """Mixin that adds JSON serialization."""
    def to_json(self) -> str:
        import json
        return json.dumps(vars(self))

class PrintableMixin:
    """Mixin that adds pretty printing."""
    def pretty_print(self) -> None:
        for key, value in vars(self).items():
            print(f"  {key}: {value}")

class User(JSONMixin, PrintableMixin):
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

user = User("Alice", 30)
print(user.to_json())     # {"name": "Alice", "age": 30}
user.pretty_print()       #   name: Alice\n  age: 30
```

**Note:** Python cannot add methods to built-in types after the fact (no monkey-patching of
`str`, `int` in practice). Use standalone functions or wrapper classes instead.

---

## Summary: Mental Model Shifts

| Swift Concept | Python Equivalent | Key Difference |
|---------------|-------------------|----------------|
| `struct` | `@dataclass(frozen=True)` | Python has no true value types |
| `protocol` | `typing.Protocol` | Structural (no explicit conformance) |
| `protocol` with defaults | `ABC` + mixin | Use ABC for enforced implementation |
| `Equatable` | `__eq__` | Auto-generated by `@dataclass` |
| `Hashable` | `__hash__` | Auto-generated by `@dataclass(frozen=True)` |
| `Codable` | Pydantic `BaseModel` | Pydantic adds validation too |
| `CustomStringConvertible` | `__str__` | Auto-generated by `@dataclass` as `__repr__` |
| `extension` | Mixin class | Cannot extend existing types retroactively |
| `enum` with associated values | `dataclass` + union | Python enums are simpler |
| `let` (immutable) | `frozen=True` | No per-property immutability |
| Access control keywords | Naming conventions (`_`, `__`) | Not enforced by language |
| Value semantics | N/A | Everything is reference in Python |
| `subscript` | `__getitem__` / `__setitem__` | Same concept, different syntax |
| `Sequence` / `Collection` | `__iter__` / `__len__` / `__getitem__` | Implement dunder methods |
