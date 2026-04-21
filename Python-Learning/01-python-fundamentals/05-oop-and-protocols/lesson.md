# Module 05: Object-Oriented Programming and Protocols

## Table of Contents

1. [Class Basics](#1-class-basics)
2. [self vs Swift's self](#2-self-vs-swifts-self)
3. [Instance, Class, and Static Methods](#3-instance-class-and-static-methods)
4. [Properties with @property](#4-properties-with-property)
5. [Inheritance and super()](#5-inheritance-and-super)
6. [Multiple Inheritance and MRO](#6-multiple-inheritance-and-mro)
7. [Abstract Base Classes (ABC)](#7-abstract-base-classes-abc)
8. [typing.Protocol -- Structural Subtyping](#8-typingprotocol----structural-subtyping)
9. [Dataclasses](#9-dataclasses)
10. [Dunder / Magic Methods](#10-dunder--magic-methods)
11. [Enum and IntEnum](#11-enum-and-intenum)
12. [Slots](#12-slots)
13. [Class Variables vs Instance Variables](#13-class-variables-vs-instance-variables)

---

## 1. Class Basics

### Defining a Class

Python classes use the `class` keyword, followed by the class name and a colon. The body is
indented, just like functions.

```python
class Dog:
    """A simple Dog class."""

    def __init__(self, name: str, breed: str, age: int = 0) -> None:
        """Initialize a Dog instance.

        Args:
            name: The dog's name.
            breed: The dog's breed.
            age: The dog's age in years.
        """
        self.name = name
        self.breed = breed
        self.age = age

    def bark(self) -> str:
        return f"{self.name} says: Woof!"

    def description(self) -> str:
        return f"{self.name} is a {self.age}-year-old {self.breed}"


# Creating instances
buddy = Dog("Buddy", "Golden Retriever", 3)
print(buddy.bark())         # Buddy says: Woof!
print(buddy.description())  # Buddy is a 3-year-old Golden Retriever
```

### Swift Comparison

```swift
// Swift class
class Dog {
    let name: String
    let breed: String
    var age: Int

    init(name: String, breed: String, age: Int = 0) {
        self.name = name
        self.breed = breed
        self.age = age
    }

    func bark() -> String {
        return "\(name) says: Woof!"
    }
}
```

### Key Differences

| Feature | Swift | Python |
|---------|-------|--------|
| Initializer | `init(...)` | `__init__(self, ...)` |
| Property declaration | `let name: String` (explicit) | `self.name = name` in `__init__` |
| Self reference | `self` (implicit in most cases) | `self` (always explicit as first param) |
| Access control | `public`, `private`, `internal` | Convention: `_private`, `__name_mangled` |
| Struct vs Class | Value types vs Reference types | Only classes (all reference types) |

---

## 2. self vs Swift's self

In Python, `self` must be the **first parameter** of every instance method. It is **not**
a keyword -- it's a convention (you could call it `this` or `s`, but don't).

```python
class Counter:
    def __init__(self) -> None:
        self.count = 0

    def increment(self) -> None:
        self.count += 1    # Must use self.count, not just count

    def get_count(self) -> int:
        return self.count

c = Counter()
c.increment()
c.increment()
print(c.get_count())  # 2
```

In Swift, `self` is implicit -- you can write `count` instead of `self.count` (unless there's
ambiguity). In Python, `self` is **always required** to access instance attributes and methods.

```python
class Person:
    def __init__(self, name: str) -> None:
        self.name = name

    def greet(self) -> str:
        # Must say self.name, not just name
        return f"Hi, I'm {self.name}"

    def introduce_to(self, other: "Person") -> str:
        # Must use self.greet(), not just greet()
        return f"{self.greet()} and I'm meeting {other.name}"
```

**Important:** When calling methods, you don't pass `self` -- Python passes it automatically:
```python
p = Person("Alice")
p.greet()  # Python automatically passes p as self
```

---

## 3. Instance, Class, and Static Methods

Python has three types of methods, distinguished by decorators.

### Instance Methods (default)

Regular methods that receive `self` as the first argument.

```python
class MyClass:
    def instance_method(self) -> str:
        return f"Called on {self}"
```

### Class Methods (@classmethod)

Receive the class itself (`cls`) as the first argument. Used for alternative constructors
and class-level operations.

```python
class Date:
    def __init__(self, year: int, month: int, day: int) -> None:
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_str: str) -> "Date":
        """Alternative constructor from 'YYYY-MM-DD' string."""
        year, month, day = map(int, date_str.split("-"))
        return cls(year, month, day)

    @classmethod
    def today(cls) -> "Date":
        """Alternative constructor for today's date."""
        import datetime
        d = datetime.date.today()
        return cls(d.year, d.month, d.day)

    def __repr__(self) -> str:
        return f"Date({self.year}, {self.month}, {self.day})"


d1 = Date(2024, 1, 15)
d2 = Date.from_string("2024-06-15")  # Alternative constructor
d3 = Date.today()                     # Another alternative constructor
```

**Swift comparison:** `@classmethod` is similar to Swift's `static func` or `class func` on
classes (the latter allows overriding). The `cls` parameter is like `Self` in Swift.

### Static Methods (@staticmethod)

Don't receive `self` or `cls`. They're just regular functions that live inside a class for
organizational purposes.

```python
class MathUtils:
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Clamp a value between min and max."""
        return max(min_val, min(value, max_val))

    @staticmethod
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

print(MathUtils.clamp(15, 0, 10))  # 10
print(MathUtils.is_prime(17))       # True
```

**Swift comparison:** `@staticmethod` is exactly like Swift's `static func`.

### Summary Table

| Method Type | First Argument | Decorator | Can Access Instance? | Can Access Class? |
|-------------|---------------|-----------|---------------------|-------------------|
| Instance | `self` | None | Yes | Yes (via `self.__class__`) |
| Class | `cls` | `@classmethod` | No | Yes |
| Static | None | `@staticmethod` | No | No |

---

## 4. Properties with @property

Python's `@property` decorator provides computed properties similar to Swift's computed
properties, with explicit getter, setter, and deleter.

### Basic Computed Property

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius  # Convention: _ prefix for "private"

    @property
    def radius(self) -> float:
        """The radius of the circle."""
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self) -> float:
        """Computed property: area of the circle (read-only)."""
        import math
        return math.pi * self._radius ** 2

    @property
    def diameter(self) -> float:
        return self._radius * 2

    @diameter.setter
    def diameter(self, value: float) -> None:
        self._radius = value / 2


c = Circle(5)
print(c.radius)    # 5       -- uses getter
print(c.area)      # 78.54   -- computed, read-only
print(c.diameter)  # 10      -- computed with setter

c.diameter = 20
print(c.radius)    # 10      -- setter updated _radius

# c.area = 100  # AttributeError: can't set 'area' (no setter defined)
```

### Swift Comparison

```swift
// Swift computed properties
class Circle {
    var radius: Double {
        didSet {
            if radius < 0 { radius = oldValue }
        }
    }

    var area: Double {          // read-only computed
        return .pi * radius * radius
    }

    var diameter: Double {      // read-write computed
        get { radius * 2 }
        set { radius = newValue / 2 }
    }

    init(radius: Double) {
        self.radius = radius
    }
}
```

### Property with Deleter

```python
class CachedResult:
    def __init__(self) -> None:
        self._value: int | None = None

    @property
    def value(self) -> int | None:
        return self._value

    @value.setter
    def value(self, new_value: int) -> None:
        self._value = new_value

    @value.deleter
    def value(self) -> None:
        """Clear the cached value."""
        self._value = None


obj = CachedResult()
obj.value = 42
print(obj.value)  # 42
del obj.value     # Calls the deleter
print(obj.value)  # None
```

---

## 5. Inheritance and super()

### Basic Inheritance

```python
class Animal:
    def __init__(self, name: str, sound: str) -> None:
        self.name = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name} says {self.sound}!"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class Dog(Animal):
    def __init__(self, name: str, breed: str) -> None:
        super().__init__(name, "Woof")  # Call parent's __init__
        self.breed = breed

    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}!"


class Cat(Animal):
    def __init__(self, name: str, indoor: bool = True) -> None:
        super().__init__(name, "Meow")
        self.indoor = indoor

    def speak(self) -> str:
        """Override parent method."""
        base = super().speak()
        return f"{base} {'(from inside)' if self.indoor else '(from outside)'}"


dog = Dog("Rex", "German Shepherd")
cat = Cat("Whiskers", indoor=True)

print(dog.speak())       # Rex says Woof!
print(dog.fetch("ball")) # Rex fetches the ball!
print(cat.speak())       # Whiskers says Meow! (from inside)
```

### Swift Comparison

```swift
// Swift inheritance
class Animal {
    let name: String
    let sound: String

    init(name: String, sound: String) {
        self.name = name
        self.sound = sound
    }

    func speak() -> String {
        return "\(name) says \(sound)!"
    }
}

class Dog: Animal {
    let breed: String

    init(name: String, breed: String) {
        self.breed = breed
        super.init(name: name, sound: "Woof")  // super.init at the end
    }
}
```

**Key difference:** In Swift, you initialize your own properties *before* calling `super.init`.
In Python, you typically call `super().__init__()` *first*, then set your own attributes.

### isinstance and issubclass

```python
print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True
print(isinstance(dog, Cat))     # False

print(issubclass(Dog, Animal))  # True
print(issubclass(Cat, Dog))     # False
```

---

## 6. Multiple Inheritance and MRO

Unlike Swift (which only supports single inheritance for classes), Python supports
**multiple inheritance**.

### Basic Multiple Inheritance

```python
class Flyable:
    def fly(self) -> str:
        return f"{self.__class__.__name__} is flying!"

class Swimmable:
    def swim(self) -> str:
        return f"{self.__class__.__name__} is swimming!"

class Duck(Flyable, Swimmable):
    def __init__(self, name: str) -> None:
        self.name = name

    def quack(self) -> str:
        return f"{self.name}: Quack!"


donald = Duck("Donald")
print(donald.fly())   # Duck is flying!
print(donald.swim())  # Duck is swimming!
print(donald.quack()) # Donald: Quack!
```

### Method Resolution Order (MRO)

When multiple parent classes define the same method, Python uses the C3 linearization
algorithm to determine the order in which classes are searched. You can inspect it:

```python
class A:
    def method(self) -> str:
        return "A"

class B(A):
    def method(self) -> str:
        return "B"

class C(A):
    def method(self) -> str:
        return "C"

class D(B, C):
    pass

d = D()
print(d.method())  # "B" -- B comes before C in MRO

# Inspect the MRO
print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)

# Or use the method
print(D.mro())
```

### Mixins

A common pattern is using small, focused classes (called mixins) to add specific behaviors.

```python
class JSONMixin:
    """Mixin that adds JSON serialization."""
    def to_json(self) -> str:
        import json
        return json.dumps(self.__dict__)

class LoggableMixin:
    """Mixin that adds logging."""
    def log(self, message: str) -> None:
        print(f"[{self.__class__.__name__}] {message}")

class User(JSONMixin, LoggableMixin):
    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email


user = User("Alice", "alice@example.com")
print(user.to_json())           # {"name": "Alice", "email": "alice@example.com"}
user.log("User created")        # [User] User created
```

**Swift comparison:** Swift achieves mixin-like behavior through **protocol extensions** and
**protocol composition**. Python uses multiple inheritance.

---

## 7. Abstract Base Classes (ABC)

ABCs let you define interfaces that subclasses **must** implement. This is similar to
Swift protocols with required methods.

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    """Abstract base class for shapes."""

    @abstractmethod
    def area(self) -> float:
        """Calculate the area of the shape."""
        ...

    @abstractmethod
    def perimeter(self) -> float:
        """Calculate the perimeter of the shape."""
        ...

    def describe(self) -> str:
        """Concrete method -- subclasses inherit this."""
        return f"{self.__class__.__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius


# Cannot instantiate abstract class
# shape = Shape()  # TypeError: Can't instantiate abstract class Shape

rect = Rectangle(3, 4)
print(rect.describe())  # Rectangle: area=12.00, perimeter=14.00
```

### Abstract Properties

```python
from abc import ABC, abstractmethod


class Vehicle(ABC):
    @property
    @abstractmethod
    def max_speed(self) -> float:
        """Maximum speed in km/h."""
        ...

    @property
    @abstractmethod
    def fuel_type(self) -> str:
        ...


class Car(Vehicle):
    @property
    def max_speed(self) -> float:
        return 200.0

    @property
    def fuel_type(self) -> str:
        return "gasoline"
```

---

## 8. typing.Protocol -- Structural Subtyping

`typing.Protocol` (Python 3.8+) enables **structural subtyping** (duck typing with type
checking). This is the closest Python equivalent to Swift protocols.

**Key insight:** Unlike ABC (which requires explicit inheritance), Protocol checks if an
object has the right methods/attributes -- regardless of its class hierarchy. This is
**structural** (shape-based) rather than **nominal** (name-based).

```python
from typing import Protocol, runtime_checkable


class Drawable(Protocol):
    """Any object with a draw() method satisfies this protocol."""
    def draw(self) -> str: ...


class Square:
    """Square doesn't inherit from Drawable, but has a draw() method."""
    def __init__(self, size: float) -> None:
        self.size = size

    def draw(self) -> str:
        return f"Drawing a {self.size}x{self.size} square"


class TextLabel:
    """TextLabel also has a draw() method."""
    def __init__(self, text: str) -> None:
        self.text = text

    def draw(self) -> str:
        return f"Drawing text: {self.text}"


def render(item: Drawable) -> None:
    """Accepts any object with a draw() method."""
    print(item.draw())


# Both work -- neither inherits from Drawable!
render(Square(5))            # Drawing a 5x5 square
render(TextLabel("Hello"))   # Drawing text: Hello
```

### Runtime Checkable Protocols

```python
@runtime_checkable
class Sized(Protocol):
    def __len__(self) -> int: ...

print(isinstance([1, 2, 3], Sized))  # True -- list has __len__
print(isinstance(42, Sized))          # False -- int doesn't have __len__
```

### Protocol vs ABC Comparison

| Feature | ABC | Protocol |
|---------|-----|----------|
| Requires inheritance | Yes (`class Foo(MyABC)`) | No |
| Checking mechanism | Nominal (explicit) | Structural (duck typing) |
| Runtime `isinstance` | Yes (automatic) | Only with `@runtime_checkable` |
| Default implementations | Yes | Yes (but less common) |
| Swift equivalent | Class inheritance | Protocol conformance |

---

## 9. Dataclasses

Dataclasses (Python 3.7+) automatically generate `__init__`, `__repr__`, `__eq__`, and
other boilerplate. They are Python's closest equivalent to Swift structs.

### Basic Dataclass

```python
from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


p1 = Point(0, 0)
p2 = Point(3, 4)

print(p1)                    # Point(x=0, y=4)
print(p1 == Point(0, 0))    # True -- auto-generated __eq__
print(p1.distance_to(p2))   # 5.0
```

### Dataclass Options

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)  # Immutable -- like a Swift struct with let properties
class Color:
    red: int
    green: int
    blue: int

c = Color(255, 128, 0)
# c.red = 0  # FrozenInstanceError!


@dataclass(order=True)  # Auto-generates <, <=, >, >= based on fields
class Version:
    major: int
    minor: int
    patch: int

v1 = Version(1, 2, 3)
v2 = Version(1, 3, 0)
print(v1 < v2)   # True
print(v1 >= v2)  # False


@dataclass(slots=True)  # Python 3.10+: uses __slots__ for memory efficiency
class Compact:
    x: int
    y: int
```

### Field Options

```python
from dataclasses import dataclass, field


@dataclass
class Config:
    name: str
    debug: bool = False
    tags: list[str] = field(default_factory=list)  # Mutable default!
    _internal: int = field(default=0, repr=False)   # Excluded from repr
    id: int = field(init=False)                      # Not in __init__

    def __post_init__(self) -> None:
        """Called after __init__. Good for derived fields."""
        self.id = hash(self.name) % 10000


c = Config("my-app", tags=["web", "api"])
print(c)  # Config(name='my-app', debug=False, tags=['web', 'api'])
```

### Dataclass vs Swift Struct

```swift
// Swift struct
struct Point: Equatable {
    let x: Double
    let y: Double

    func distanceTo(_ other: Point) -> Double {
        return sqrt(pow(x - other.x, 2) + pow(y - other.y, 2))
    }
}
// Equatable conformance is auto-synthesized
```

```python
# Python dataclass
@dataclass(frozen=True)  # frozen=True for immutability like Swift struct
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
# __eq__ is auto-generated
```

---

## 10. Dunder / Magic Methods

"Dunder" stands for "double underscore" (e.g., `__init__`). These special methods let you
customize how your objects behave with Python operators and built-in functions.

### String Representation

```python
class Product:
    def __init__(self, name: str, price: float) -> None:
        self.name = name
        self.price = price

    def __str__(self) -> str:
        """Human-readable string (used by print(), str())."""
        return f"{self.name}: ${self.price:.2f}"

    def __repr__(self) -> str:
        """Developer-readable string (used in REPL, debugging).
        Should ideally be valid Python to recreate the object."""
        return f"Product({self.name!r}, {self.price!r})"


p = Product("Widget", 9.99)
print(str(p))    # Widget: $9.99
print(repr(p))   # Product('Widget', 9.99)
print(p)         # Widget: $9.99 (print uses __str__)
print([p])       # [Product('Widget', 9.99)] (containers use __repr__)
```

### Comparison Methods

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius == other.celsius

    def __lt__(self, other: "Temperature") -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius < other.celsius

    def __le__(self, other: "Temperature") -> bool:
        return self == other or self < other

    def __hash__(self) -> int:
        return hash(self.celsius)

    def __repr__(self) -> str:
        return f"Temperature({self.celsius})"


t1 = Temperature(20)
t2 = Temperature(30)
t3 = Temperature(20)

print(t1 == t3)  # True
print(t1 < t2)   # True
print({t1, t2, t3})  # {Temperature(20), Temperature(30)} -- hashable!
```

**Tip:** Use `@functools.total_ordering` to auto-generate all comparison methods from
just `__eq__` and `__lt__`:

```python
from functools import total_ordering

@total_ordering
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius == other.celsius

    def __lt__(self, other: "Temperature") -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius < other.celsius
```

### Container Methods

```python
class Playlist:
    def __init__(self, name: str, songs: list[str] | None = None) -> None:
        self.name = name
        self._songs = songs or []

    def __len__(self) -> int:
        """len(playlist)"""
        return len(self._songs)

    def __getitem__(self, index: int) -> str:
        """playlist[0], enables iteration and slicing."""
        return self._songs[index]

    def __setitem__(self, index: int, value: str) -> None:
        """playlist[0] = 'new song'"""
        self._songs[index] = value

    def __contains__(self, song: str) -> bool:
        """'song' in playlist"""
        return song in self._songs

    def __iter__(self):
        """for song in playlist: ..."""
        return iter(self._songs)

    def __add__(self, other: "Playlist") -> "Playlist":
        """playlist1 + playlist2"""
        return Playlist(
            f"{self.name} + {other.name}",
            self._songs + other._songs,
        )

    def __repr__(self) -> str:
        return f"Playlist({self.name!r}, {len(self._songs)} songs)"


pl = Playlist("Rock", ["Stairway to Heaven", "Bohemian Rhapsody"])
print(len(pl))                          # 2
print(pl[0])                            # Stairway to Heaven
print("Bohemian Rhapsody" in pl)        # True
for song in pl:
    print(f"  - {song}")
```

### Arithmetic Methods

```python
class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector":
        """Handles scalar * vector (reversed operand)."""
        return self.__mul__(scalar)

    def __abs__(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"


v1 = Vector(1, 2)
v2 = Vector(3, 4)

print(v1 + v2)      # Vector(4, 6)
print(v1 * 3)       # Vector(3, 6)
print(3 * v1)       # Vector(3, 6) -- thanks to __rmul__
print(abs(v2))       # 5.0
```

### Context Manager Methods

```python
class Timer:
    """Context manager that times a block of code."""

    def __enter__(self):
        import time
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.time() - self.start
        print(f"Elapsed: {self.elapsed:.4f}s")
        return False  # Don't suppress exceptions


with Timer() as t:
    total = sum(range(1_000_000))

print(f"Result: {total}, Time: {t.elapsed:.4f}s")
```

### Complete Dunder Method Reference

| Method | Triggered By | Swift Equivalent |
|--------|-------------|-----------------|
| `__init__` | `MyClass()` | `init()` |
| `__str__` | `str(obj)`, `print(obj)` | `description` (CustomStringConvertible) |
| `__repr__` | `repr(obj)`, REPL display | `debugDescription` (CustomDebugStringConvertible) |
| `__eq__` | `==` | `==` (Equatable) |
| `__lt__` | `<` | `<` (Comparable) |
| `__hash__` | `hash(obj)`, set/dict key | `hash(into:)` (Hashable) |
| `__len__` | `len(obj)` | `count` property |
| `__getitem__` | `obj[key]` | `subscript` |
| `__setitem__` | `obj[key] = val` | `subscript` setter |
| `__contains__` | `x in obj` | `contains(_:)` |
| `__iter__` | `for x in obj` | `makeIterator()` |
| `__next__` | `next(obj)` | `next()` on Iterator |
| `__add__` | `obj + other` | `+` operator |
| `__enter__`/`__exit__` | `with obj:` | No direct equivalent |
| `__call__` | `obj()` | `callAsFunction()` |

---

## 11. Enum and IntEnum

Python enums are defined using the `enum` module.

### Basic Enum

```python
from enum import Enum, auto


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


# Usage
c = Color.RED
print(c)          # Color.RED
print(c.name)     # RED
print(c.value)    # 1
print(c == Color.RED)  # True

# Iteration
for color in Color:
    print(f"{color.name} = {color.value}")

# From value
print(Color(2))        # Color.GREEN

# From name
print(Color["BLUE"])   # Color.BLUE
```

### Using auto()

```python
class Direction(Enum):
    NORTH = auto()  # 1
    SOUTH = auto()  # 2
    EAST = auto()   # 3
    WEST = auto()   # 4
```

### String Enum

```python
from enum import StrEnum  # Python 3.11+

class Status(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"

print(Status.ACTIVE)           # Status.ACTIVE
print(Status.ACTIVE.value)     # active
print(Status.ACTIVE == "active")  # True -- StrEnum allows string comparison
```

### IntEnum

```python
from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

# IntEnum values can be used as integers
print(Priority.HIGH > Priority.LOW)  # True
print(Priority.MEDIUM + 1)           # 3
```

### Enum with Methods

```python
class Planet(Enum):
    MERCURY = (3.303e23, 2.4397e6)
    VENUS = (4.869e24, 6.0518e6)
    EARTH = (5.976e24, 6.37814e6)

    def __init__(self, mass: float, radius: float) -> None:
        self.mass = mass
        self.radius = radius

    @property
    def surface_gravity(self) -> float:
        G = 6.67300e-11
        return G * self.mass / (self.radius ** 2)

print(Planet.EARTH.surface_gravity)  # 9.802...
```

### Swift Enum Comparison

```swift
// Swift enum with associated values and methods
enum Planet {
    case mercury, venus, earth

    var surfaceGravity: Double {
        switch self {
        case .mercury: return 3.7
        case .venus: return 8.87
        case .earth: return 9.8
        }
    }
}
```

**Key difference:** Swift enums support **associated values** (each case can carry different
data). Python enums don't have this feature -- you'd use a dataclass or regular class for
associated-value patterns.

---

## 12. Slots

By default, Python objects store their attributes in a `__dict__` dictionary. Using `__slots__`
tells Python to use a fixed set of attributes, saving memory and slightly improving speed.

```python
class PointWithDict:
    """Normal class -- uses __dict__ for attributes."""
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class PointWithSlots:
    """Slotted class -- no __dict__, fixed attributes."""
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


p1 = PointWithDict(1, 2)
p1.z = 3  # Works -- can add arbitrary attributes

p2 = PointWithSlots(1, 2)
# p2.z = 3  # AttributeError: 'PointWithSlots' has no attribute 'z'
```

### When to Use Slots

- **Many instances** -- slots save ~40% memory per instance
- **Performance-critical** code -- attribute access is slightly faster
- **Dataclasses** -- use `@dataclass(slots=True)` for the best of both worlds

```python
import sys

p1 = PointWithDict(1, 2)
p2 = PointWithSlots(1, 2)

print(sys.getsizeof(p1.__dict__))  # ~104 bytes (the dict overhead)
# p2 has no __dict__ -- slots attributes are stored more efficiently
```

---

## 13. Class Variables vs Instance Variables

```python
class Dog:
    # Class variable -- shared across ALL instances
    species = "Canis familiaris"
    count = 0

    def __init__(self, name: str) -> None:
        # Instance variable -- unique to each instance
        self.name = name
        Dog.count += 1  # Modify the class variable

    @classmethod
    def get_count(cls) -> int:
        return cls.count


d1 = Dog("Rex")
d2 = Dog("Buddy")

print(d1.species)      # Canis familiaris (reads class var through instance)
print(d2.species)      # Canis familiaris (same class var)
print(Dog.species)     # Canis familiaris (access through class)

print(d1.name)         # Rex (instance var)
print(d2.name)         # Buddy (instance var)

print(Dog.get_count()) # 2
```

### The Shadowing Trap

```python
class Config:
    debug = False  # Class variable

c1 = Config()
c2 = Config()

print(c1.debug)  # False (reads class var)
print(c2.debug)  # False (reads class var)

c1.debug = True  # Creates an INSTANCE variable on c1, shadowing the class var!

print(c1.debug)       # True (instance var)
print(c2.debug)       # False (still reading class var)
print(Config.debug)   # False (class var unchanged)
```

### Swift Comparison

```swift
// Swift
class Dog {
    static var species = "Canis familiaris"  // Type property (class variable)
    static var count = 0                      // Type property

    let name: String                          // Instance property

    init(name: String) {
        self.name = name
        Dog.count += 1
    }
}
```

---

## Quick Reference: OOP Cheat Sheet

| Concept | Python | Swift |
|---------|--------|-------|
| Class definition | `class Foo:` | `class Foo { }` |
| Initializer | `def __init__(self):` | `init() { }` |
| Self reference | `self` (explicit param) | `self` (implicit) |
| Inheritance | `class Child(Parent):` | `class Child: Parent { }` |
| Call parent | `super().__init__()` | `super.init()` |
| Abstract class | `class Foo(ABC):` | `protocol Foo { }` |
| Protocol | `class Foo(Protocol):` | `protocol Foo { }` |
| Struct equivalent | `@dataclass(frozen=True)` | `struct Foo { }` |
| Property | `@property` | `var x: T { get set }` |
| Class method | `@classmethod` | `class func` / `static func` |
| Static method | `@staticmethod` | `static func` |
| Access control | `_private` convention | `private`, `internal`, `public` |
| Enum | `class Color(Enum):` | `enum Color { }` |
| Multiple inheritance | Yes | No (use protocol composition) |

---

## Key Takeaways for Swift Developers

1. **Everything is a reference type** -- Python has no value types like Swift structs. Use `@dataclass(frozen=True)` for immutable data.
2. **`self` is explicit** -- you must always include `self` as the first parameter and use it to access instance members.
3. **No access control** -- Python relies on naming conventions (`_private`, `__mangled`) rather than keywords.
4. **`typing.Protocol` is your friend** -- it provides Swift-like structural protocol conformance without requiring inheritance.
5. **Dataclasses replace struct boilerplate** -- they auto-generate `__init__`, `__repr__`, `__eq__`, and more.
6. **Dunder methods are everywhere** -- they are how you make your objects work with Python's operators and built-in functions.
7. **Multiple inheritance exists** -- use it carefully via mixins; prefer composition when possible.
8. **Enums are simpler** -- Python enums don't support associated values. Use dataclasses for that pattern.

---

## Next Steps

In Module 06, we'll explore advanced Python features: decorators, generators, context managers,
type hints, and Pydantic. These build directly on the OOP foundations covered here.
