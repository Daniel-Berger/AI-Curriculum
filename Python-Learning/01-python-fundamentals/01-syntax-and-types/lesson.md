# Module 01: Syntax and Types

## Introduction for Swift Developers

If you're coming from Swift, you'll find Python both liberating and unsettling. There's
no `let` vs `var`, no semicolons, no braces for blocks, and no compiler catching type
errors before runtime. But Python's simplicity is intentional -- it optimizes for
readability, rapid iteration, and expressiveness.

This lesson covers the foundational building blocks: variables, types, strings, numbers,
and the conventions that replace what the Swift compiler enforces.

---

## 1. Variables and Assignment

### No `let` or `var` -- Just Names

In Swift, you explicitly choose between `let` (immutable) and `var` (mutable). Python
has no such distinction. Every variable is simply a name bound to an object.

```python
# Python -- just assign
name = "Daniel"
age = 30
age = 31  # Reassignment is always allowed

# Multiple assignment (Python specialty)
x, y, z = 1, 2, 3

# Swap without a temp variable
x, y = y, x

# Same value to multiple variables
a = b = c = 0
```

Compare with Swift:
```swift
// Swift
let name = "Daniel"    // immutable
var age = 30           // mutable
age = 31               // OK because var
// name = "Other"      // ERROR: cannot assign to let
```

### Variable Naming Conventions

Python uses `snake_case` by convention (PEP 8), not `camelCase`:

```python
# Python conventions
user_name = "daniel"          # snake_case for variables
MAX_CONNECTIONS = 100         # UPPER_SNAKE_CASE for constants
_private_var = "internal"     # leading underscore = "private by convention"
__name_mangled = "special"    # double underscore = name mangling (advanced)

# These work but violate convention:
userName = "daniel"           # Avoid -- this is Swift/Java style
```

### The Constants Convention

Python has no `let`. Instead, `UPPER_CASE` names signal "don't reassign this":

```python
# By convention, these are constants
MAX_RETRIES = 3
API_BASE_URL = "https://api.example.com"
PI = 3.14159265358979

# Nothing prevents reassignment -- it's purely a social contract
MAX_RETRIES = 5  # Python won't stop you, but linters will warn
```

For Swift developers, this feels dangerous. But in practice, Python's convention works
well. Linters like `pylint` and `ruff` will flag constant reassignment.

---

## 2. Dynamic Typing

### No Type Declarations Required

Python is dynamically typed. The type belongs to the *object*, not the *variable*:

```python
x = 42          # x refers to an int object
x = "hello"     # now x refers to a str object -- totally fine
x = [1, 2, 3]   # now x refers to a list object

# Check types at runtime
print(type(x))         # <class 'list'>
print(isinstance(x, list))  # True
```

### The `type()` and `isinstance()` Functions

```python
value = 42

# type() returns the exact type
print(type(value))              # <class 'int'>
print(type(value) == int)       # True

# isinstance() checks type hierarchy (preferred)
print(isinstance(value, int))   # True
print(isinstance(value, (int, float)))  # True -- checks multiple types

# isinstance respects inheritance
print(isinstance(True, int))    # True! bool is a subclass of int
print(type(True) == int)        # False -- type() is exact
```

**Rule of thumb**: Use `isinstance()` for type checking, not `type() ==`.

---

## 3. Type Hints (Type Annotations)

Python 3.5+ supports optional type hints. They don't enforce anything at runtime --
they're for documentation, IDE support, and static analysis tools like `mypy`.

```python
# Basic type hints
name: str = "Daniel"
age: int = 30
height: float = 5.11
is_active: bool = True

# Function type hints
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Without type hints (also valid)
def greet_untyped(name):
    return f"Hello, {name}!"
```

### Complex Type Hints

```python
from typing import Optional, Union

# Optional means "this type OR None"
middle_name: Optional[str] = None   # equivalent to str | None

# Python 3.10+ union syntax (preferred in modern Python)
middle_name: str | None = None

# Union of multiple types
value: int | float = 42

# Collection type hints
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
unique_ids: set[int] = {1, 2, 3}
coordinates: tuple[float, float] = (40.7, -74.0)
```

### Type Hints Do NOT Enforce Types

This is the biggest difference from Swift. Type hints are *suggestions*:

```python
age: int = "thirty"  # No error! Python ignores the hint at runtime
print(age)           # "thirty" -- works fine

# To actually enforce types, use mypy (static analysis tool):
# $ mypy your_file.py
# error: Incompatible types in assignment (expression has type "str", variable has type "int")
```

---

## 4. Basic Types

### Integers (`int`)

Python integers have **arbitrary precision** -- no overflow, no `Int8`/`Int64` distinction:

```python
# Regular integers
x = 42
big = 10 ** 100  # 100-digit number -- no overflow!

# Underscores for readability (like Swift)
population = 7_900_000_000
hex_color = 0xFF_AA_00

# Different bases
binary = 0b1010      # 10
octal = 0o17         # 15
hexadecimal = 0xFF   # 255

# Integer operations
print(10 / 3)    # 3.3333... (float division -- DIFFERENT from Swift!)
print(10 // 3)   # 3 (integer/floor division)
print(10 % 3)    # 1 (modulo)
print(2 ** 10)   # 1024 (exponentiation -- Swift uses pow())
```

**Key difference from Swift**: The `/` operator *always* returns a float in Python,
even for integers. Use `//` for integer division.

### Floating Point (`float`)

```python
pi = 3.14159
negative = -2.5
scientific = 1.5e10   # 15000000000.0
tiny = 1.5e-10        # 0.00000000015

# Float precision (same IEEE 754 as Swift's Double)
print(0.1 + 0.2)  # 0.30000000000000004

# For precise decimals (like financial calculations)
from decimal import Decimal
price = Decimal("19.99")
tax = Decimal("0.08")
total = price * (1 + tax)  # Decimal('21.5892')

# Special float values
import math
print(math.inf)      # Infinity
print(-math.inf)     # -Infinity
print(math.nan)      # NaN
print(math.isnan(math.nan))  # True
```

### Booleans (`bool`)

```python
is_valid = True    # Note: capitalized (not `true` like JavaScript)
is_empty = False   # Not `false`

# bool is a subclass of int!
print(True + True)   # 2
print(False + 1)     # 1
print(True * 10)     # 10

# Truthy and Falsy values (important -- no Swift equivalent)
# These are ALL falsy:
bool(0)        # False
bool(0.0)      # False
bool("")       # False  (empty string)
bool([])       # False  (empty list)
bool({})       # False  (empty dict)
bool(set())    # False  (empty set)
bool(None)     # False
bool(False)    # False

# Everything else is truthy:
bool(1)        # True
bool(-1)       # True
bool("hello")  # True
bool([0])      # True  (non-empty list, even if it contains falsy values)

# This means you can write:
items = [1, 2, 3]
if items:        # Pythonic -- checks if list is non-empty
    print("has items")

# Instead of:
if len(items) > 0:  # Works but not Pythonic
    print("has items")
```

### Strings (`str`)

Strings in Python are immutable sequences of Unicode characters, similar to Swift:

```python
# String creation
single = 'hello'
double = "hello"
multi = """This is a
multi-line string"""

# Raw strings (no escape processing -- great for regex)
path = r"C:\Users\new\test"   # backslashes are literal
# In Swift, you'd use: #"C:\Users\new\test"#

# String is immutable (like Swift)
s = "hello"
# s[0] = 'H'  # TypeError! Can't modify in place
s = "H" + s[1:]  # Create a new string instead
```

### `None` vs Swift's `nil`

`None` is Python's equivalent of `nil`, but it works differently:

```python
# None is a singleton object
x = None

# Check for None with `is`, not `==`
if x is None:
    print("x is None")

if x is not None:
    print("x has a value")

# Why `is` instead of `==`?
# `is` checks identity (same object), `==` checks equality
# None is a singleton, so `is` is correct and faster

# None is falsy
if not x:
    print("x is falsy")  # True, but also true for 0, "", [], etc.

# Common pattern: default arguments
def connect(host: str, port: int | None = None) -> None:
    if port is None:
        port = 443  # default
    print(f"Connecting to {host}:{port}")
```

**Key difference**: Swift's `Optional` is a type wrapper (`String?`). Python's `None`
is just a regular value -- any variable can be `None` at any time unless you use
type hints + mypy.

---

## 5. Strings In Depth

### f-Strings (Formatted String Literals)

f-strings are Python's string interpolation, similar to Swift's `\()`:

```python
name = "Daniel"
age = 30

# Basic interpolation
greeting = f"Hello, {name}! You are {age} years old."

# Expressions inside braces
print(f"Next year you'll be {age + 1}")
print(f"Name uppercase: {name.upper()}")
print(f"Is adult: {age >= 18}")

# Multi-line f-strings
message = f"""
Dear {name},
Welcome to Python! You are {age} years old.
"""

# Format specifiers
pi = 3.14159265
print(f"Pi is approximately {pi:.2f}")       # "Pi is approximately 3.14"
print(f"Pi is approximately {pi:.4f}")       # "Pi is approximately 3.1416"
print(f"Large number: {1000000:,}")          # "Large number: 1,000,000"
print(f"Percentage: {0.856:.1%}")            # "Percentage: 85.6%"
print(f"Padded: {42:>10}")                   # "Padded:         42"
print(f"Padded: {42:<10}")                   # "Padded: 42        "
print(f"Padded: {42:^10}")                   # "Padded:     42    "
print(f"Zero-padded: {42:05d}")              # "Zero-padded: 00042"
print(f"Hex: {255:#x}")                      # "Hex: 0xff"
print(f"Binary: {10:#b}")                    # "Binary: 0b1010"

# Debugging with f-strings (Python 3.8+)
x = 42
print(f"{x=}")           # "x=42"
print(f"{x + 1=}")       # "x + 1=43"
print(f"{name=!r}")      # "name='Daniel'" (shows repr with quotes)
```

### String Methods

Python strings have a rich set of built-in methods:

```python
s = "Hello, World!"

# Case methods
s.upper()          # "HELLO, WORLD!"
s.lower()          # "hello, world!"
s.title()          # "Hello, World!"
s.capitalize()     # "Hello, world!"
s.swapcase()       # "hELLO, wORLD!"
s.casefold()       # "hello, world!" (aggressive lowercase for comparisons)

# Search methods
s.find("World")       # 7 (index of first occurrence, -1 if not found)
s.index("World")      # 7 (like find, but raises ValueError if not found)
s.rfind("l")          # 10 (search from right)
s.count("l")          # 3
s.startswith("Hello") # True
s.endswith("!")        # True
"World" in s           # True (containment check -- very Pythonic)

# Modification methods (return new strings)
s.replace("World", "Python")    # "Hello, Python!"
s.strip()           # Remove whitespace from both ends
s.lstrip()          # Remove whitespace from left
s.rstrip()          # Remove whitespace from right
"  hello  ".strip() # "hello"

# Split and Join
"a,b,c".split(",")          # ["a", "b", "c"]
"hello world".split()       # ["hello", "world"] (splits on whitespace)
", ".join(["a", "b", "c"])  # "a, b, c"
"\n".join(["line1", "line2"])  # "line1\nline2"

# Validation methods
"abc".isalpha()     # True
"123".isdigit()     # True
"abc123".isalnum()  # True
"   ".isspace()     # True
"Hello".istitle()   # True

# Padding
"hello".ljust(10)        # "hello     "
"hello".rjust(10)        # "     hello"
"hello".center(11)       # "   hello   "
"hello".center(11, "-")  # "---hello---"
"42".zfill(5)            # "00042"
```

### String Slicing

Slicing is one of Python's most powerful features:

```python
s = "Hello, World!"
#    0123456789...

# Basic slicing: s[start:stop:step]
s[0]      # "H"
s[-1]     # "!" (last character)
s[0:5]    # "Hello" (start inclusive, stop exclusive)
s[:5]     # "Hello" (omit start = from beginning)
s[7:]     # "World!" (omit stop = to end)
s[-6:]    # "orld!" (last 6 characters... wait)
s[-6:]    # "orld!" -- actually last 6 chars
s[::2]    # "Hlo ol!" (every 2nd character)
s[::-1]   # "!dlroW ,olleH" (reverse the string)

# Slicing never raises IndexError
s[0:1000]  # "Hello, World!" (no error, just goes to end)
s[1000:]   # "" (empty string, no error)
```

---

## 6. Numeric Operations

```python
# Arithmetic
10 + 3    # 13
10 - 3    # 7
10 * 3    # 30
10 / 3    # 3.3333333333333335 (always float!)
10 // 3   # 3 (floor division)
10 % 3    # 1 (modulo)
10 ** 3   # 1000 (exponentiation)

# Augmented assignment
x = 10
x += 5    # x = 15
x -= 3    # x = 12
x *= 2    # x = 24
x //= 5   # x = 4
x **= 3   # x = 64
# Note: no x++ or x-- in Python!

# Built-in numeric functions
abs(-42)           # 42
round(3.7)         # 4
round(3.14159, 2)  # 3.14
min(1, 2, 3)       # 1
max(1, 2, 3)       # 3
sum([1, 2, 3, 4])  # 10
divmod(17, 5)      # (3, 2) -- quotient and remainder

# Math module for advanced operations
import math

math.sqrt(16)      # 4.0
math.ceil(3.2)     # 4
math.floor(3.8)    # 3
math.log(100, 10)  # 2.0
math.log2(8)       # 3.0
math.sin(math.pi / 2)  # 1.0
math.factorial(5)  # 120
math.gcd(12, 8)    # 4
math.isclose(0.1 + 0.2, 0.3)  # True (handles floating point comparison)
```

---

## 7. Type Conversion

Python uses constructor-style casting (similar to Swift's initializers):

```python
# String to number
int("42")        # 42
float("3.14")    # 3.14
int("0xFF", 16)  # 255 (specify base)
int("1010", 2)   # 10 (binary)

# Number to string
str(42)          # "42"
str(3.14)        # "3.14"

# Float/Int conversions
int(3.7)         # 3 (truncates, doesn't round!)
int(3.2)         # 3
float(42)        # 42.0

# To boolean
bool(0)          # False
bool(42)         # True
bool("")         # False
bool("hello")    # True

# Number to different bases (returns string)
bin(10)          # "0b1010"
oct(10)          # "0o12"
hex(255)         # "0xff"

# To character / from character
ord("A")         # 65 (Unicode code point)
chr(65)          # "A"

# Failed conversions raise exceptions
# int("hello")   # ValueError: invalid literal for int()
# float("abc")   # ValueError: could not convert string to float

# Safe conversion pattern
def safe_int(value: str, default: int = 0) -> int:
    """Convert string to int, returning default if conversion fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

safe_int("42")      # 42
safe_int("hello")   # 0
safe_int("hello", -1)  # -1
```

---

## 8. Multiple Assignment and Unpacking

Python's multiple assignment is more powerful than Swift's:

```python
# Multiple assignment
x, y, z = 1, 2, 3

# Swap
a, b = b, a  # No temp variable needed!

# Unpacking from a list/tuple
coordinates = (40.7128, -74.0060)
lat, lng = coordinates

# Star unpacking (captures remaining items)
first, *rest = [1, 2, 3, 4, 5]
# first = 1, rest = [2, 3, 4, 5]

first, *middle, last = [1, 2, 3, 4, 5]
# first = 1, middle = [2, 3, 4], last = 5

# Underscore for ignored values (convention)
_, y, _ = (1, 2, 3)  # Only care about y

# Nested unpacking
(a, b), (c, d) = (1, 2), (3, 4)

# In loops
points = [(1, 2), (3, 4), (5, 6)]
for x, y in points:
    print(f"x={x}, y={y}")
```

---

## 9. Identity and Equality

```python
# == checks equality (value comparison)
# is checks identity (same object in memory)

a = [1, 2, 3]
b = [1, 2, 3]
c = a

a == b    # True (same values)
a is b    # False (different objects!)
a is c    # True (same object)

# Always use `is` for None, True, False
x = None
x is None       # Correct
x == None       # Works but not Pythonic (can be overridden)

# Small integer caching (CPython implementation detail)
a = 256
b = 256
a is b   # True (Python caches integers -5 to 256)

a = 257
b = 257
a is b   # May be False! (implementation-dependent)
# Takeaway: always use == for value comparison, `is` only for None/True/False
```

---

## 10. The `dir()` and `help()` Functions

These are your best friends when exploring Python interactively:

```python
# dir() lists all attributes and methods
dir(str)  # Shows all string methods
dir(42)   # Shows all int methods

# Filter to non-dunder methods
[m for m in dir(str) if not m.startswith('_')]
# ['capitalize', 'casefold', 'center', 'count', 'encode', ...]

# help() shows documentation
help(str.split)
# Help on method_descriptor:
# split(self, /, sep=None, maxsplit=-1)
#     Return a list of the substrings in the string...

# In IPython/Jupyter, use ? instead:
# str.split?
```

---

## 11. Common Gotchas for Swift Developers

### 1. Division Always Returns Float

```python
10 / 2    # 5.0, not 5!
10 // 2   # 5 (use // for integer division)
```

### 2. No Switch Exhaustiveness

```python
# Python's match/case doesn't require exhaustiveness
# (covered in Module 02: Control Flow)
```

### 3. Truthiness Is Everywhere

```python
# Python checks truthiness in conditions, not just booleans
name = ""
if name:  # This is False because empty string is falsy
    print(name)
else:
    print("No name provided")
```

### 4. Mutable Default Arguments

```python
# DANGER: mutable defaults are shared across calls!
def bad_append(item, items=[]):  # DON'T DO THIS
    items.append(item)
    return items

bad_append(1)  # [1]
bad_append(2)  # [1, 2] -- NOT [2]!

# Correct pattern:
def good_append(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 5. Strings Are Immutable

```python
# Like Swift, Python strings are immutable
s = "hello"
# s[0] = "H"  # TypeError!
s = s.replace("h", "H")  # Creates a new string
```

---

## 12. Python's Philosophy

Run this in the Python REPL to see Python's guiding principles:

```python
import this
```

Key principles for Swift developers:
- **"Explicit is better than implicit"** -- but less explicit than Swift
- **"There should be one-- and preferably only one --obvious way to do it"** -- the "Pythonic" way
- **"Readability counts"** -- whitespace matters, clarity over cleverness
- **"Errors should never pass silently"** -- exceptions over error codes

---

## Summary: Swift to Python Quick Reference

| Concept | Swift | Python |
|---------|-------|--------|
| Immutable variable | `let x = 5` | `X = 5` (UPPER_CASE convention) |
| Mutable variable | `var x = 5` | `x = 5` |
| Type annotation | `let x: Int = 5` | `x: int = 5` (hint only) |
| String interpolation | `"Hello \(name)"` | `f"Hello {name}"` |
| Nil/None | `nil` | `None` |
| Nil check | `if x != nil` | `if x is not None` |
| Integer division | `10 / 3` (= 3) | `10 // 3` (= 3) |
| Float division | `Double(10) / 3.0` | `10 / 3` (= 3.333...) |
| Exponentiation | `pow(2, 10)` | `2 ** 10` |
| Type check | `x is Int` | `isinstance(x, int)` |
| Print | `print("hello")` | `print("hello")` |
| Multi-line string | `"""..."""` | `"""..."""` |
| Raw string | `#"raw \n"#` | `r"raw \n"` |

---

## Next Steps

In the next module, we'll cover **Control Flow** -- where Python's elegance really
starts to shine with comprehensions, the walrus operator, and match/case.

Practice the exercises to build muscle memory for Python's syntax. Pay special
attention to f-strings and truthiness -- you'll use them constantly.
