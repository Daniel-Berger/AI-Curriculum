"""
Module 05: OOP and Protocols - Exercises
========================================

15 exercises covering classes, properties, dataclasses, dunder methods,
ABC, Protocol, inheritance, and enums in Python.

Target audience: Swift/iOS developers learning Python.

Instructions:
    - Replace `pass` (or `...`) with your implementation.
    - Run this file to check your answers with the assert-based tests at the bottom.
    - Type hints are provided in the signatures -- follow them.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, Iterator, Any


# ---------------------------------------------------------------------------
# WARM-UP: Basic classes, properties, dataclasses
# ---------------------------------------------------------------------------

def exercise_1_bank_account() -> type:
    """Create and return a BankAccount class with:

    - __init__(self, owner: str, balance: float = 0.0)
    - deposit(self, amount: float) -> None  (raise ValueError if amount <= 0)
    - withdraw(self, amount: float) -> None (raise ValueError if amount <= 0
        or if amount > balance)
    - A read-only property `balance` (use @property, store as _balance)
    - __repr__ returning "BankAccount(owner='...', balance=...)"

    Examples:
        acct = BankAccount("Alice", 100.0)
        acct.deposit(50.0)
        acct.balance       -> 150.0
        acct.withdraw(30)
        acct.balance       -> 120.0
    """
    pass


def exercise_2_temperature() -> type:
    """Create and return a Temperature class with:

    - __init__(self, celsius: float)
    - @property celsius (getter/setter)
    - @property fahrenheit (computed, read-write):
        - getter: celsius * 9/5 + 32
        - setter: converts from Fahrenheit to Celsius
    - __repr__ returning "Temperature(celsius=...)"
    - Setter validation: raise ValueError if celsius < -273.15

    Examples:
        t = Temperature(100)
        t.fahrenheit     -> 212.0
        t.fahrenheit = 32
        t.celsius        -> 0.0
    """
    pass


def exercise_3_color_dataclass() -> type:
    """Create and return a frozen dataclass called Color with:

    - Fields: red (int), green (int), blue (int), alpha (float = 1.0)
    - A method `hex(self) -> str` that returns the color as '#RRGGBB'
        (ignore alpha for hex, use uppercase hex digits, 2 digits per channel)
    - A classmethod `from_hex(cls, hex_str: str) -> Color` that parses '#RRGGBB'

    Use @dataclass(frozen=True).

    Examples:
        c = Color(255, 128, 0)
        c.hex()                 -> "#FF8000"
        Color.from_hex("#FF8000") -> Color(red=255, green=128, blue=0, alpha=1.0)
    """
    pass


# ---------------------------------------------------------------------------
# CORE: Implementing dunder methods, ABC and Protocol, inheritance
# ---------------------------------------------------------------------------

def exercise_4_money() -> type:
    """Create and return a Money class with:

    - __init__(self, amount: float, currency: str = "USD")
    - __add__: only add Money of the same currency, raise ValueError otherwise
    - __sub__: only subtract Money of the same currency, raise ValueError otherwise
    - __mul__(self, factor: float) -> Money: multiply amount by a scalar
    - __eq__: True if same amount AND same currency
    - __lt__: compare amounts (only same currency, raise ValueError otherwise)
    - __repr__: "Money(100.00, 'USD')"
    - __str__: "$100.00" for USD, "100.00 EUR" for others

    Examples:
        m1 = Money(100, "USD")
        m2 = Money(50, "USD")
        m1 + m2  -> Money(150.00, 'USD')
        m1 * 2   -> Money(200.00, 'USD')
    """
    pass


def exercise_5_linked_list() -> type:
    """Create and return a LinkedList class that supports:

    - __init__(self): create an empty list
    - append(self, value: Any) -> None: add to the end
    - __len__(self) -> int
    - __getitem__(self, index: int) -> Any (support negative indexing)
    - __contains__(self, value: Any) -> bool
    - __iter__(self) -> Iterator: iterate over values
    - __repr__(self) -> str: "LinkedList([1, 2, 3])"

    Use a simple inner Node class with `value` and `next` attributes.

    Examples:
        ll = LinkedList()
        ll.append(1); ll.append(2); ll.append(3)
        len(ll)       -> 3
        ll[0]         -> 1
        ll[-1]        -> 3
        2 in ll       -> True
        list(ll)      -> [1, 2, 3]
    """
    pass


def exercise_6_shape_abc() -> tuple[type, type, type]:
    """Create and return a tuple of (Shape, Circle, Rectangle) where:

    Shape is an ABC with:
        - abstract method: area(self) -> float
        - abstract method: perimeter(self) -> float
        - concrete method: describe(self) -> str returning
            "{ClassName}: area={area:.2f}, perimeter={perimeter:.2f}"

    Circle(radius: float) implements Shape.

    Rectangle(width: float, height: float) implements Shape.

    Use math.pi for circle calculations.
    """
    pass


def exercise_7_sortable_protocol() -> type:
    """Create and return a Protocol class called Sortable that requires:

    - A property `sort_key` of type Any (use @property in protocol)

    Then the exercise test will verify that objects with a `sort_key` property
    satisfy the protocol (structural subtyping).

    Make it @runtime_checkable.

    Example:
        class Student:
            def __init__(self, name, gpa):
                self.name = name
                self._gpa = gpa

            @property
            def sort_key(self):
                return self._gpa

        isinstance(Student("A", 3.5), Sortable)  -> True
    """
    pass


def exercise_8_animal_hierarchy() -> tuple[type, type, type]:
    """Create and return (Animal, Dog, Cat) class hierarchy:

    Animal:
        - __init__(self, name: str, age: int)
        - speak(self) -> str: returns "{name} makes a sound"
        - __repr__: "{ClassName}(name='{name}', age={age})"
        - @classmethod from_dict(cls, data: dict) -> Animal

    Dog(Animal):
        - __init__(self, name: str, age: int, breed: str)
        - speak(self) -> str: returns "{name} says Woof!"
        - fetch(self, item: str) -> str: "{name} fetches the {item}"

    Cat(Animal):
        - __init__(self, name: str, age: int, indoor: bool = True)
        - speak(self) -> str: returns "{name} says Meow!"
        - purr(self) -> str: returns "{name} purrs..."
    """
    pass


# ---------------------------------------------------------------------------
# CHALLENGE: Custom container, Enum patterns
# ---------------------------------------------------------------------------

def exercise_9_matrix() -> type:
    """Create and return a Matrix class with full dunder support:

    - __init__(self, rows: list[list[float]]): store a copy of the rows
    - __repr__: "Matrix([[1, 2], [3, 4]])"
    - __eq__: element-wise comparison
    - __getitem__(self, pos: tuple[int, int]) -> float: matrix[row, col]
    - __setitem__(self, pos: tuple[int, int], value: float): matrix[row, col] = val
    - __add__: element-wise addition (same dimensions, raise ValueError otherwise)
    - __mul__(self, scalar: float): scalar multiplication
    - __len__: returns total number of elements (rows * cols)
    - __contains__(self, value: float): check if value exists in matrix
    - @property shape -> tuple[int, int]: (rows, cols)
    - transpose(self) -> Matrix: return transposed matrix

    Examples:
        m = Matrix([[1, 2], [3, 4]])
        m[0, 1]        -> 2
        m.shape        -> (2, 2)
        m.transpose()  -> Matrix([[1, 3], [2, 4]])
    """
    pass


def exercise_10_task_status_enum() -> type:
    """Create and return a TaskStatus enum with:

    Members:
        TODO, IN_PROGRESS, REVIEW, DONE, CANCELLED

    Methods:
        - is_active(self) -> bool: True for TODO, IN_PROGRESS, REVIEW
        - next_status(self) -> TaskStatus: returns the next status in the workflow
            TODO -> IN_PROGRESS -> REVIEW -> DONE
            Raise ValueError for DONE and CANCELLED
        - @classmethod from_string(cls, s: str) -> TaskStatus:
            Parse case-insensitive strings like "todo", "in_progress", etc.
            Raise ValueError for unknown strings.

    Examples:
        TaskStatus.TODO.is_active()      -> True
        TaskStatus.DONE.is_active()      -> False
        TaskStatus.TODO.next_status()    -> TaskStatus.IN_PROGRESS
    """
    pass


def exercise_11_registry() -> type:
    """Create and return a Registry class that acts as a generic container:

    - __init__(self): create empty registry
    - register(self, key: str, value: Any) -> None: add item
    - get(self, key: str, default: Any = None) -> Any: get item or default
    - __getitem__(self, key: str) -> Any: raise KeyError if missing
    - __setitem__(self, key: str, value: Any) -> None
    - __delitem__(self, key: str) -> None: raise KeyError if missing
    - __contains__(self, key: str) -> bool
    - __len__(self) -> int
    - __iter__(self) -> Iterator[str]: iterate over keys
    - __repr__(self) -> str: "Registry({...})" showing the internal dict

    Examples:
        r = Registry()
        r.register("a", 1)
        r["b"] = 2
        "a" in r       -> True
        len(r)          -> 2
        list(r)         -> ["a", "b"]
    """
    pass


# ---------------------------------------------------------------------------
# SWIFT BRIDGE: Convert Swift protocol/struct/class patterns to Python
# ---------------------------------------------------------------------------

def exercise_12_equatable_hashable() -> type:
    """Create and return a Card dataclass that is Equatable and Hashable
    (like conforming to Equatable & Hashable in Swift).

    Fields: rank (str), suit (str)

    Use @dataclass(frozen=True) so __eq__ and __hash__ are auto-generated.

    Add a __str__ method: "{rank} of {suit}" (e.g., "Ace of Spades").

    Add an `order_value` property that returns a numeric value for sorting:
        2-10 -> int value, Jack=11, Queen=12, King=13, Ace=14

    Examples:
        c1 = Card("Ace", "Spades")
        c2 = Card("Ace", "Spades")
        c1 == c2        -> True
        hash(c1) == hash(c2)  -> True
        str(c1)         -> "Ace of Spades"
        c1.order_value  -> 14
        {c1, c2}        -> one element (hashable, deduplicated)
    """
    pass


def exercise_13_codable_like() -> type:
    """Create and return a User dataclass with Codable-like behavior:

    Fields: name (str), email (str), age (int), tags (list[str]) with default []

    Methods:
        - to_dict(self) -> dict: serialize to dictionary
        - @classmethod from_dict(cls, data: dict) -> User: deserialize from dict
        - to_json(self) -> str: serialize to JSON string
        - @classmethod from_json(cls, json_str: str) -> User: deserialize from JSON

    Examples:
        u = User("Alice", "alice@test.com", 30, ["admin"])
        d = u.to_dict()   -> {"name": "Alice", "email": "alice@test.com", "age": 30, "tags": ["admin"]}
        User.from_dict(d) == u  -> True
    """
    pass


def exercise_14_protocol_extensions() -> tuple[type, type, type]:
    """Simulate Swift protocol extensions using a mixin.

    Create and return (Describable, Product, Employee):

    Describable (mixin class):
        - abstract property: description_fields -> dict[str, Any]
        - concrete method: describe() -> str
            Format: "ClassName(field1=val1, field2=val2)"
            (Sorted by key name)

    Product:
        - __init__(self, name: str, price: float)
        - description_fields returns {"name": self.name, "price": self.price}

    Employee:
        - __init__(self, name: str, department: str)
        - description_fields returns {"name": self.name, "department": self.department}

    Both Product and Employee should inherit from Describable.

    Examples:
        p = Product("Widget", 9.99)
        p.describe()  -> "Product(name=Widget, price=9.99)"
    """
    pass


def exercise_15_builder_pattern() -> type:
    """Create and return a QueryBuilder class that implements the builder
    pattern (similar to Swift method chaining).

    Methods (all return self for chaining):
        - select(self, *columns: str) -> QueryBuilder
        - from_table(self, table: str) -> QueryBuilder
        - where(self, condition: str) -> QueryBuilder (can be called multiple times)
        - order_by(self, column: str, ascending: bool = True) -> QueryBuilder
        - limit(self, n: int) -> QueryBuilder

    Build method:
        - build(self) -> str: returns the SQL query string

    Examples:
        q = (QueryBuilder()
             .select("name", "age")
             .from_table("users")
             .where("age > 18")
             .where("active = true")
             .order_by("name")
             .limit(10)
             .build())
        -> "SELECT name, age FROM users WHERE age > 18 AND active = true ORDER BY name ASC LIMIT 10"
    """
    pass


# ===========================================================================
# TESTS -- Run this file to verify your solutions
# ===========================================================================

if __name__ == "__main__":
    import math

    # --- Exercise 1: BankAccount ---
    BankAccount = exercise_1_bank_account()
    acct = BankAccount("Alice", 100.0)
    acct.deposit(50.0)
    assert acct.balance == 150.0
    acct.withdraw(30.0)
    assert acct.balance == 120.0
    try:
        acct.deposit(-10)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    try:
        acct.withdraw(9999)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    assert repr(acct) == "BankAccount(owner='Alice', balance=120.0)"
    print("Exercise 1 passed!")

    # --- Exercise 2: Temperature ---
    Temperature = exercise_2_temperature()
    t = Temperature(100)
    assert t.fahrenheit == 212.0
    t.fahrenheit = 32
    assert abs(t.celsius - 0.0) < 0.001
    assert repr(t) == "Temperature(celsius=0.0)"
    try:
        t.celsius = -300
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    print("Exercise 2 passed!")

    # --- Exercise 3: Color dataclass ---
    Color = exercise_3_color_dataclass()
    c = Color(255, 128, 0)
    assert c.hex() == "#FF8000"
    c2 = Color.from_hex("#FF8000")
    assert c2 == Color(255, 128, 0, 1.0)
    assert c.alpha == 1.0
    try:
        c.red = 0  # Should fail -- frozen
        assert False, "Should raise"
    except (AttributeError, FrozenInstanceError):
        pass
    except Exception:
        pass  # FrozenInstanceError is a subclass of AttributeError
    print("Exercise 3 passed!")

    # --- Exercise 4: Money ---
    Money = exercise_4_money()
    m1 = Money(100, "USD")
    m2 = Money(50, "USD")
    m3 = m1 + m2
    assert repr(m3) == "Money(150.00, 'USD')"
    assert str(m1) == "$100.00"
    assert str(Money(50, "EUR")) == "50.00 EUR"
    assert m1 * 2 == Money(200, "USD")
    assert m2 < m1
    try:
        m1 + Money(10, "EUR")
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    print("Exercise 4 passed!")

    # --- Exercise 5: LinkedList ---
    LinkedList = exercise_5_linked_list()
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    assert len(ll) == 3
    assert ll[0] == 1
    assert ll[2] == 3
    assert ll[-1] == 3
    assert ll[-2] == 2
    assert 2 in ll
    assert 99 not in ll
    assert list(ll) == [1, 2, 3]
    assert repr(ll) == "LinkedList([1, 2, 3])"
    print("Exercise 5 passed!")

    # --- Exercise 6: Shape ABC ---
    Shape, Circle, Rectangle = exercise_6_shape_abc()
    circ = Circle(5)
    assert abs(circ.area() - math.pi * 25) < 0.001
    assert abs(circ.perimeter() - 2 * math.pi * 5) < 0.001
    rect = Rectangle(3, 4)
    assert rect.area() == 12.0
    assert rect.perimeter() == 14.0
    assert "Circle" in circ.describe()
    try:
        Shape()  # Should not be instantiable
        assert False, "Should raise TypeError"
    except TypeError:
        pass
    print("Exercise 6 passed!")

    # --- Exercise 7: Sortable Protocol ---
    Sortable = exercise_7_sortable_protocol()

    class Student:
        def __init__(self, name: str, gpa: float):
            self.name = name
            self._gpa = gpa

        @property
        def sort_key(self):
            return self._gpa

    assert isinstance(Student("A", 3.5), Sortable)
    assert not isinstance(42, Sortable)
    print("Exercise 7 passed!")

    # --- Exercise 8: Animal hierarchy ---
    Animal, Dog, Cat = exercise_8_animal_hierarchy()
    dog = Dog("Rex", 3, "Labrador")
    cat = Cat("Whiskers", 5)
    assert dog.speak() == "Rex says Woof!"
    assert cat.speak() == "Whiskers says Meow!"
    assert dog.fetch("ball") == "Rex fetches the ball"
    assert cat.purr() == "Whiskers purrs..."
    assert repr(dog) == "Dog(name='Rex', age=3)"
    d = {"name": "Buddy", "age": 2}
    a = Animal.from_dict(d)
    assert a.name == "Buddy" and a.age == 2
    print("Exercise 8 passed!")

    # --- Exercise 9: Matrix ---
    Matrix = exercise_9_matrix()
    m = Matrix([[1, 2], [3, 4]])
    assert m[0, 1] == 2
    assert m[1, 0] == 3
    assert m.shape == (2, 2)
    assert len(m) == 4
    assert 3 in m
    assert 99 not in m
    m[0, 0] = 10
    assert m[0, 0] == 10
    m2 = Matrix([[5, 6], [7, 8]])
    m3 = Matrix([[10, 6], [7, 8]]) + m2
    assert m3[0, 0] == 15
    mt = Matrix([[1, 2, 3], [4, 5, 6]]).transpose()
    assert mt.shape == (3, 2)
    assert mt[0, 0] == 1
    assert mt[2, 1] == 6
    print("Exercise 9 passed!")

    # --- Exercise 10: TaskStatus Enum ---
    TaskStatus = exercise_10_task_status_enum()
    assert TaskStatus.TODO.is_active() is True
    assert TaskStatus.DONE.is_active() is False
    assert TaskStatus.CANCELLED.is_active() is False
    assert TaskStatus.TODO.next_status() == TaskStatus.IN_PROGRESS
    assert TaskStatus.IN_PROGRESS.next_status() == TaskStatus.REVIEW
    assert TaskStatus.REVIEW.next_status() == TaskStatus.DONE
    try:
        TaskStatus.DONE.next_status()
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    assert TaskStatus.from_string("todo") == TaskStatus.TODO
    assert TaskStatus.from_string("IN_PROGRESS") == TaskStatus.IN_PROGRESS
    try:
        TaskStatus.from_string("unknown")
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    print("Exercise 10 passed!")

    # --- Exercise 11: Registry ---
    Registry = exercise_11_registry()
    r = Registry()
    r.register("a", 1)
    r["b"] = 2
    assert "a" in r
    assert "c" not in r
    assert len(r) == 2
    assert r["a"] == 1
    assert r.get("c", 99) == 99
    del r["a"]
    assert len(r) == 1
    assert list(r) == ["b"]
    try:
        _ = r["nonexistent"]
        assert False, "Should raise KeyError"
    except KeyError:
        pass
    print("Exercise 11 passed!")

    # --- Exercise 12: Card ---
    Card = exercise_12_equatable_hashable()
    c1 = Card("Ace", "Spades")
    c2 = Card("Ace", "Spades")
    c3 = Card("King", "Hearts")
    assert c1 == c2
    assert c1 != c3
    assert hash(c1) == hash(c2)
    assert str(c1) == "Ace of Spades"
    assert c1.order_value == 14
    assert c3.order_value == 13
    assert Card("5", "Diamonds").order_value == 5
    assert len({c1, c2, c3}) == 2
    print("Exercise 12 passed!")

    # --- Exercise 13: User (Codable-like) ---
    import json
    User = exercise_13_codable_like()
    u = User("Alice", "alice@test.com", 30, ["admin"])
    d = u.to_dict()
    assert d == {"name": "Alice", "email": "alice@test.com", "age": 30, "tags": ["admin"]}
    u2 = User.from_dict(d)
    assert u2.name == "Alice" and u2.tags == ["admin"]
    j = u.to_json()
    u3 = User.from_json(j)
    assert u3.name == "Alice" and u3.age == 30
    print("Exercise 13 passed!")

    # --- Exercise 14: Protocol Extensions (Mixin) ---
    Describable, Product, Employee = exercise_14_protocol_extensions()
    p = Product("Widget", 9.99)
    assert p.describe() == "Product(name=Widget, price=9.99)"
    e = Employee("Alice", "Engineering")
    assert e.describe() == "Employee(department=Engineering, name=Alice)"
    print("Exercise 14 passed!")

    # --- Exercise 15: QueryBuilder ---
    QueryBuilder = exercise_15_builder_pattern()
    q = (QueryBuilder()
         .select("name", "age")
         .from_table("users")
         .where("age > 18")
         .where("active = true")
         .order_by("name")
         .limit(10)
         .build())
    assert q == "SELECT name, age FROM users WHERE age > 18 AND active = true ORDER BY name ASC LIMIT 10"

    q2 = (QueryBuilder()
          .select("*")
          .from_table("products")
          .order_by("price", ascending=False)
          .build())
    assert q2 == "SELECT * FROM products ORDER BY price DESC"
    print("Exercise 15 passed!")

    print("\n All exercises passed!")
