"""
Module 05: OOP and Protocols - Solutions
========================================

Complete solutions for all 15 exercises. Where applicable, Pythonic
alternatives are noted in comments.
"""

from __future__ import annotations

import json
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, runtime_checkable, Iterator, Any


# ---------------------------------------------------------------------------
# WARM-UP
# ---------------------------------------------------------------------------

def exercise_1_bank_account() -> type:
    """BankAccount with deposit, withdraw, balance property."""

    class BankAccount:
        def __init__(self, owner: str, balance: float = 0.0) -> None:
            self.owner = owner
            self._balance = balance

        @property
        def balance(self) -> float:
            return self._balance

        def deposit(self, amount: float) -> None:
            if amount <= 0:
                raise ValueError("Deposit amount must be positive")
            self._balance += amount

        def withdraw(self, amount: float) -> None:
            if amount <= 0:
                raise ValueError("Withdrawal amount must be positive")
            if amount > self._balance:
                raise ValueError("Insufficient funds")
            self._balance -= amount

        def __repr__(self) -> str:
            return f"BankAccount(owner={self.owner!r}, balance={self._balance})"

    return BankAccount


def exercise_2_temperature() -> type:
    """Temperature with celsius and fahrenheit properties."""

    class Temperature:
        def __init__(self, celsius: float) -> None:
            self.celsius = celsius  # Uses the setter for validation

        @property
        def celsius(self) -> float:
            return self._celsius

        @celsius.setter
        def celsius(self, value: float) -> None:
            if value < -273.15:
                raise ValueError("Temperature cannot be below absolute zero")
            self._celsius = value

        @property
        def fahrenheit(self) -> float:
            return self._celsius * 9 / 5 + 32

        @fahrenheit.setter
        def fahrenheit(self, value: float) -> None:
            self.celsius = (value - 32) * 5 / 9

        def __repr__(self) -> str:
            return f"Temperature(celsius={self._celsius})"

    return Temperature


def exercise_3_color_dataclass() -> type:
    """Frozen Color dataclass with hex conversion."""

    @dataclass(frozen=True)
    class Color:
        red: int
        green: int
        blue: int
        alpha: float = 1.0

        def hex(self) -> str:
            return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"

        @classmethod
        def from_hex(cls, hex_str: str) -> Color:
            hex_str = hex_str.lstrip("#")
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return cls(r, g, b)

    return Color


# ---------------------------------------------------------------------------
# CORE
# ---------------------------------------------------------------------------

def exercise_4_money() -> type:
    """Money class with arithmetic and comparison dunder methods."""

    class Money:
        def __init__(self, amount: float, currency: str = "USD") -> None:
            self.amount = round(amount, 2)
            self.currency = currency

        def _check_currency(self, other: Money) -> None:
            if self.currency != other.currency:
                raise ValueError(
                    f"Cannot operate on {self.currency} and {other.currency}"
                )

        def __add__(self, other: Money) -> Money:
            self._check_currency(other)
            return Money(self.amount + other.amount, self.currency)

        def __sub__(self, other: Money) -> Money:
            self._check_currency(other)
            return Money(self.amount - other.amount, self.currency)

        def __mul__(self, factor: float) -> Money:
            return Money(self.amount * factor, self.currency)

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Money):
                return NotImplemented
            return self.amount == other.amount and self.currency == other.currency

        def __lt__(self, other: Money) -> bool:
            if not isinstance(other, Money):
                return NotImplemented
            self._check_currency(other)
            return self.amount < other.amount

        def __repr__(self) -> str:
            return f"Money({self.amount:.2f}, {self.currency!r})"

        def __str__(self) -> str:
            if self.currency == "USD":
                return f"${self.amount:.2f}"
            return f"{self.amount:.2f} {self.currency}"

    return Money


def exercise_5_linked_list() -> type:
    """LinkedList with full container dunder support."""

    class LinkedList:
        class _Node:
            def __init__(self, value: Any) -> None:
                self.value = value
                self.next: LinkedList._Node | None = None

        def __init__(self) -> None:
            self._head: LinkedList._Node | None = None
            self._length = 0

        def append(self, value: Any) -> None:
            new_node = LinkedList._Node(value)
            if self._head is None:
                self._head = new_node
            else:
                current = self._head
                while current.next is not None:
                    current = current.next
                current.next = new_node
            self._length += 1

        def __len__(self) -> int:
            return self._length

        def __getitem__(self, index: int) -> Any:
            if index < 0:
                index = self._length + index
            if index < 0 or index >= self._length:
                raise IndexError("LinkedList index out of range")
            current = self._head
            for _ in range(index):
                current = current.next  # type: ignore
            return current.value  # type: ignore

        def __contains__(self, value: Any) -> bool:
            current = self._head
            while current is not None:
                if current.value == value:
                    return True
                current = current.next
            return False

        def __iter__(self) -> Iterator:
            current = self._head
            while current is not None:
                yield current.value
                current = current.next

        def __repr__(self) -> str:
            return f"LinkedList({list(self)})"

    return LinkedList


def exercise_6_shape_abc() -> tuple[type, type, type]:
    """Shape ABC with Circle and Rectangle implementations."""

    class Shape(ABC):
        @abstractmethod
        def area(self) -> float: ...

        @abstractmethod
        def perimeter(self) -> float: ...

        def describe(self) -> str:
            return (
                f"{self.__class__.__name__}: "
                f"area={self.area():.2f}, perimeter={self.perimeter():.2f}"
            )

    class Circle(Shape):
        def __init__(self, radius: float) -> None:
            self.radius = radius

        def area(self) -> float:
            return math.pi * self.radius ** 2

        def perimeter(self) -> float:
            return 2 * math.pi * self.radius

    class Rectangle(Shape):
        def __init__(self, width: float, height: float) -> None:
            self.width = width
            self.height = height

        def area(self) -> float:
            return self.width * self.height

        def perimeter(self) -> float:
            return 2 * (self.width + self.height)

    return Shape, Circle, Rectangle


def exercise_7_sortable_protocol() -> type:
    """Runtime-checkable Sortable Protocol."""

    @runtime_checkable
    class Sortable(Protocol):
        @property
        def sort_key(self) -> Any: ...

    return Sortable


def exercise_8_animal_hierarchy() -> tuple[type, type, type]:
    """Animal, Dog, Cat class hierarchy."""

    class Animal:
        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

        def speak(self) -> str:
            return f"{self.name} makes a sound"

        def __repr__(self) -> str:
            return f"{self.__class__.__name__}(name={self.name!r}, age={self.age})"

        @classmethod
        def from_dict(cls, data: dict) -> Animal:
            return cls(**data)

    class Dog(Animal):
        def __init__(self, name: str, age: int, breed: str) -> None:
            super().__init__(name, age)
            self.breed = breed

        def speak(self) -> str:
            return f"{self.name} says Woof!"

        def fetch(self, item: str) -> str:
            return f"{self.name} fetches the {item}"

    class Cat(Animal):
        def __init__(self, name: str, age: int, indoor: bool = True) -> None:
            super().__init__(name, age)
            self.indoor = indoor

        def speak(self) -> str:
            return f"{self.name} says Meow!"

        def purr(self) -> str:
            return f"{self.name} purrs..."

    return Animal, Dog, Cat


# ---------------------------------------------------------------------------
# CHALLENGE
# ---------------------------------------------------------------------------

def exercise_9_matrix() -> type:
    """Matrix with full dunder support."""

    class Matrix:
        def __init__(self, rows: list[list[float]]) -> None:
            self._rows = [row[:] for row in rows]  # Deep copy

        @property
        def shape(self) -> tuple[int, int]:
            if not self._rows:
                return (0, 0)
            return (len(self._rows), len(self._rows[0]))

        def __repr__(self) -> str:
            return f"Matrix({self._rows})"

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Matrix):
                return NotImplemented
            return self._rows == other._rows

        def __getitem__(self, pos: tuple[int, int]) -> float:
            row, col = pos
            return self._rows[row][col]

        def __setitem__(self, pos: tuple[int, int], value: float) -> None:
            row, col = pos
            self._rows[row][col] = value

        def __add__(self, other: Matrix) -> Matrix:
            if not isinstance(other, Matrix):
                return NotImplemented
            if self.shape != other.shape:
                raise ValueError(
                    f"Cannot add matrices of shape {self.shape} and {other.shape}"
                )
            rows = [
                [self._rows[i][j] + other._rows[i][j]
                 for j in range(self.shape[1])]
                for i in range(self.shape[0])
            ]
            return Matrix(rows)

        def __mul__(self, scalar: float) -> Matrix:
            rows = [
                [val * scalar for val in row]
                for row in self._rows
            ]
            return Matrix(rows)

        def __len__(self) -> int:
            r, c = self.shape
            return r * c

        def __contains__(self, value: float) -> bool:
            return any(value in row for row in self._rows)

        def transpose(self) -> Matrix:
            if not self._rows:
                return Matrix([])
            rows = list(map(list, zip(*self._rows)))
            return Matrix(rows)

    return Matrix


def exercise_10_task_status_enum() -> type:
    """TaskStatus enum with workflow methods."""

    class TaskStatus(Enum):
        TODO = auto()
        IN_PROGRESS = auto()
        REVIEW = auto()
        DONE = auto()
        CANCELLED = auto()

        def is_active(self) -> bool:
            return self in (TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.REVIEW)

        def next_status(self) -> TaskStatus:
            workflow = {
                TaskStatus.TODO: TaskStatus.IN_PROGRESS,
                TaskStatus.IN_PROGRESS: TaskStatus.REVIEW,
                TaskStatus.REVIEW: TaskStatus.DONE,
            }
            if self not in workflow:
                raise ValueError(f"No next status for {self.name}")
            return workflow[self]

        @classmethod
        def from_string(cls, s: str) -> TaskStatus:
            s_upper = s.upper()
            for member in cls:
                if member.name == s_upper:
                    return member
            raise ValueError(f"Unknown status: {s!r}")

    return TaskStatus


def exercise_11_registry() -> type:
    """Registry class acting as a generic container."""

    class Registry:
        def __init__(self) -> None:
            self._data: dict[str, Any] = {}

        def register(self, key: str, value: Any) -> None:
            self._data[key] = value

        def get(self, key: str, default: Any = None) -> Any:
            return self._data.get(key, default)

        def __getitem__(self, key: str) -> Any:
            return self._data[key]  # Raises KeyError if missing

        def __setitem__(self, key: str, value: Any) -> None:
            self._data[key] = value

        def __delitem__(self, key: str) -> None:
            del self._data[key]  # Raises KeyError if missing

        def __contains__(self, key: str) -> bool:
            return key in self._data

        def __len__(self) -> int:
            return len(self._data)

        def __iter__(self) -> Iterator[str]:
            return iter(self._data)

        def __repr__(self) -> str:
            return f"Registry({self._data})"

    return Registry


# ---------------------------------------------------------------------------
# SWIFT BRIDGE
# ---------------------------------------------------------------------------

def exercise_12_equatable_hashable() -> type:
    """Card dataclass -- Equatable and Hashable."""

    @dataclass(frozen=True)
    class Card:
        rank: str
        suit: str

        _RANK_VALUES = {
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
            "8": 8, "9": 9, "10": 10,
            "Jack": 11, "Queen": 12, "King": 13, "Ace": 14,
        }

        @property
        def order_value(self) -> int:
            return self._RANK_VALUES.get(self.rank, 0)

        def __str__(self) -> str:
            return f"{self.rank} of {self.suit}"

    return Card


def exercise_13_codable_like() -> type:
    """User dataclass with Codable-like serialization."""

    @dataclass
    class User:
        name: str
        email: str
        age: int
        tags: list[str] = field(default_factory=list)

        def to_dict(self) -> dict:
            return {
                "name": self.name,
                "email": self.email,
                "age": self.age,
                "tags": self.tags[:],  # Copy the list
            }

        @classmethod
        def from_dict(cls, data: dict) -> User:
            return cls(
                name=data["name"],
                email=data["email"],
                age=data["age"],
                tags=data.get("tags", []),
            )

        def to_json(self) -> str:
            return json.dumps(self.to_dict())

        @classmethod
        def from_json(cls, json_str: str) -> User:
            return cls.from_dict(json.loads(json_str))

    return User

    # Alternative: use dataclasses.asdict for to_dict
    # from dataclasses import asdict
    # def to_dict(self): return asdict(self)


def exercise_14_protocol_extensions() -> tuple[type, type, type]:
    """Describable mixin with Product and Employee."""

    class Describable(ABC):
        @property
        @abstractmethod
        def description_fields(self) -> dict[str, Any]: ...

        def describe(self) -> str:
            fields = self.description_fields
            sorted_fields = sorted(fields.items())
            parts = ", ".join(f"{k}={v}" for k, v in sorted_fields)
            return f"{self.__class__.__name__}({parts})"

    class Product(Describable):
        def __init__(self, name: str, price: float) -> None:
            self.name = name
            self.price = price

        @property
        def description_fields(self) -> dict[str, Any]:
            return {"name": self.name, "price": self.price}

    class Employee(Describable):
        def __init__(self, name: str, department: str) -> None:
            self.name = name
            self.department = department

        @property
        def description_fields(self) -> dict[str, Any]:
            return {"name": self.name, "department": self.department}

    return Describable, Product, Employee


def exercise_15_builder_pattern() -> type:
    """QueryBuilder with method chaining."""

    class QueryBuilder:
        def __init__(self) -> None:
            self._columns: list[str] = []
            self._table: str = ""
            self._conditions: list[str] = []
            self._order_column: str | None = None
            self._order_asc: bool = True
            self._limit: int | None = None

        def select(self, *columns: str) -> QueryBuilder:
            self._columns.extend(columns)
            return self

        def from_table(self, table: str) -> QueryBuilder:
            self._table = table
            return self

        def where(self, condition: str) -> QueryBuilder:
            self._conditions.append(condition)
            return self

        def order_by(self, column: str, ascending: bool = True) -> QueryBuilder:
            self._order_column = column
            self._order_asc = ascending
            return self

        def limit(self, n: int) -> QueryBuilder:
            self._limit = n
            return self

        def build(self) -> str:
            parts = [f"SELECT {', '.join(self._columns)}"]
            parts.append(f"FROM {self._table}")

            if self._conditions:
                parts.append(f"WHERE {' AND '.join(self._conditions)}")

            if self._order_column:
                direction = "ASC" if self._order_asc else "DESC"
                parts.append(f"ORDER BY {self._order_column} {direction}")

            if self._limit is not None:
                parts.append(f"LIMIT {self._limit}")

            return " ".join(parts)

    return QueryBuilder


# ===========================================================================
# TESTS
# ===========================================================================

if __name__ == "__main__":
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
        Shape()
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
