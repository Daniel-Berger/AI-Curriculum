# Swift vs Python: Syntax and Types

A side-by-side comparison for Swift developers learning Python.

---

## Variables and Constants

| Concept | Swift | Python |
|---------|-------|--------|
| Immutable binding | `let name = "Daniel"` | No equivalent; use `NAME = "Daniel"` (UPPER_CASE convention) |
| Mutable binding | `var count = 0` | `count = 0` (all variables are reassignable) |
| Type annotation | `let age: Int = 30` | `age: int = 30` (hint only, not enforced) |
| Type inference | `let x = 42` (compiler infers `Int`) | `x = 42` (dynamic, type belongs to value) |
| Multiple assignment | `let (x, y) = (1, 2)` | `x, y = 1, 2` |
| Swap | `swap(&a, &b)` or `(a, b) = (b, a)` | `a, b = b, a` |
| Constant enforcement | Compiler error on reassign `let` | Nothing -- purely convention + linter |

### Key Differences

- **Swift enforces immutability at compile time**; Python relies on naming conventions (`UPPER_CASE = "constant"`).
- **Swift's type annotations are binding**; Python's type hints are ignored at runtime.
- Python allows rebinding any name to any type at any time -- there is no `let`.

---

## Basic Types

| Type | Swift | Python | Notes |
|------|-------|--------|-------|
| Integer | `Int` (64-bit) | `int` (arbitrary precision) | Python ints never overflow |
| Float | `Double` (64-bit) | `float` (64-bit) | Same underlying IEEE 754 |
| Boolean | `Bool` (`true`/`false`) | `bool` (`True`/`False`) | Python `bool` is subclass of `int` |
| String | `String` | `str` | Both immutable, both Unicode |
| Character | `Character` | `str` (length 1) | Python has no separate char type |
| Nil/None | `nil` | `None` | Very different semantics (see below) |
| Any | `Any` | No keyword needed | Python variables can hold any type by default |
| Void | `Void` / `()` | `None` (return type) | Functions return `None` implicitly |

### Integer Comparison

```swift
// Swift: Fixed-width integers
let small: Int8 = 127
let big: Int64 = 9_223_372_036_854_775_807
// let overflow: Int8 = 128  // Compile error!
```

```python
# Python: Arbitrary precision
small = 127
big = 9_223_372_036_854_775_807
enormous = 10 ** 1000  # No overflow, ever
```

---

## String Interpolation

| Feature | Swift | Python |
|---------|-------|--------|
| Basic interpolation | `"Hello \(name)"` | `f"Hello {name}"` |
| Expression in string | `"Sum: \(a + b)"` | `f"Sum: {a + b}"` |
| Format specifier | N/A (use String(format:)) | `f"{pi:.2f}"` |
| Multi-line | `"""..."""` | `"""..."""` or `f"""..."""` |
| Raw string | `#"no \n escape"#` | `r"no \n escape"` |
| Repeat | `String(repeating: "a", count: 3)` | `"a" * 3` |
| Debug printing | `"\(variable)"` with `debugDescription` | `f"{variable=}"` (Python 3.8+) |

### Examples Side by Side

```swift
// Swift
let name = "Daniel"
let age = 30
let msg = "Hello, \(name)! You are \(age) years old."
let formatted = String(format: "%.2f", 3.14159)  // "3.14"
```

```python
# Python
name = "Daniel"
age = 30
msg = f"Hello, {name}! You are {age} years old."
formatted = f"{3.14159:.2f}"  # "3.14"
```

---

## Optional / None

| Concept | Swift | Python |
|---------|-------|--------|
| Null value | `nil` | `None` |
| Optional type | `String?` (explicit wrapper) | `str \| None` (type hint only) |
| Nil check | `if x != nil` | `if x is not None` |
| Force unwrap | `x!` | N/A (no wrapping) |
| Optional binding | `if let x = optionalX { }` | `if x is not None:` or walrus `:=` |
| Nil coalescing | `x ?? defaultValue` | `x if x is not None else default` or `x or default` |
| Optional chaining | `x?.method()` | No direct equivalent; use `x.method() if x else None` |
| Implicitly unwrapped | `String!` | N/A |

### Key Differences

```swift
// Swift: Optional is a type wrapper
var name: String? = nil      // Type is Optional<String>
name = "Daniel"              // Type is still Optional<String>
let greeting = "Hi \(name!)" // Must unwrap to use
// let len = name.count      // Error: must unwrap first
let len = name?.count ?? 0   // Safe access
```

```python
# Python: None is just a value, not a type wrapper
name = None          # name holds None
name = "Daniel"      # name holds a string (any variable can be None)
greeting = f"Hi {name}"  # No unwrapping needed
length = len(name) if name is not None else 0  # Manual safety check

# With type hints + mypy, you get some compile-time safety:
name: str | None = None
# mypy will warn if you use name.upper() without a None check
```

### Nil Coalescing Comparison

```swift
// Swift
let displayName = username ?? "Anonymous"
let port = config?.port ?? 8080
```

```python
# Python -- explicit (safest, distinguishes None from falsy)
display_name = username if username is not None else "Anonymous"

# Python -- using `or` (simpler but treats ALL falsy values as None)
display_name = username or "Anonymous"
# WARNING: This also replaces "" with "Anonymous"!

port = config.port if config is not None else 8080
```

---

## Type Checking and Conversion

| Operation | Swift | Python |
|-----------|-------|--------|
| Type check | `x is Int` | `isinstance(x, int)` |
| Exact type | `type(of: x) == Int.self` | `type(x) == int` |
| Cast (safe) | `x as? Int` | Not needed (dynamic typing) |
| Cast (forced) | `x as! Int` | `int(x)` (may raise exception) |
| Type name | `String(describing: type(of: x))` | `type(x).__name__` |
| Convert Int to String | `String(42)` | `str(42)` |
| Convert String to Int | `Int("42")` (returns Optional) | `int("42")` (raises on failure) |

### Type Conversion Examples

```swift
// Swift -- conversion returns Optional
let num: Int? = Int("42")     // Optional(42)
let bad: Int? = Int("hello")  // nil

// Safe usage
if let n = Int(input) {
    print("Got number: \(n)")
} else {
    print("Not a number")
}
```

```python
# Python -- conversion raises exception on failure
num = int("42")     # 42
# bad = int("hello")  # ValueError!

# Safe usage (try/except pattern)
try:
    n = int(input_str)
    print(f"Got number: {n}")
except ValueError:
    print("Not a number")
```

---

## Boolean and Truthiness

| Concept | Swift | Python |
|---------|-------|--------|
| True/False | `true` / `false` | `True` / `False` |
| Logical AND | `&&` | `and` |
| Logical OR | `\|\|` | `or` |
| Logical NOT | `!` | `not` |
| Empty check | `array.isEmpty` | `not array` or `len(array) == 0` |
| Truthiness | Only `Bool` in conditions | ANY value has truthiness |

### Truthiness -- The Biggest Difference

```swift
// Swift -- only Bool expressions in conditions
let items = [1, 2, 3]
if !items.isEmpty {  // Must explicitly check
    print("has items")
}
// if items { }  // ERROR: not a Bool expression
```

```python
# Python -- any value can be used as a condition
items = [1, 2, 3]
if items:  # Non-empty list is truthy
    print("has items")

# Falsy values: 0, 0.0, "", [], {}, set(), None, False
# Everything else is truthy
```

---

## Naming Conventions

| Element | Swift | Python |
|---------|-------|--------|
| Variables | `camelCase` | `snake_case` |
| Constants | `camelCase` with `let` | `UPPER_SNAKE_CASE` |
| Functions | `camelCase` | `snake_case` |
| Classes | `PascalCase` | `PascalCase` |
| Protocols/ABCs | `PascalCase` | `PascalCase` |
| Modules | `PascalCase` | `snake_case` |
| Private | `private` keyword | `_leading_underscore` (convention) |
| File-private | `fileprivate` keyword | `_leading_underscore` |

---

## Operators

| Operation | Swift | Python |
|-----------|-------|--------|
| Integer division | `10 / 3` (= `3`) | `10 // 3` (= `3`) |
| Float division | `10.0 / 3.0` | `10 / 3` (= `3.333...`) |
| Exponentiation | `pow(2, 10)` | `2 ** 10` |
| Modulo | `10 % 3` | `10 % 3` |
| String repeat | `String(repeating: "a", count: 3)` | `"a" * 3` |
| In/contains | `array.contains(x)` | `x in array` |
| Identity check | `===` (reference types) | `is` |
| Equality | `==` | `==` |
| Ternary | `x > 0 ? "pos" : "neg"` | `"pos" if x > 0 else "neg"` |

---

## Quick Mental Model

> **Swift** is like a strict teacher who checks your homework before you submit it.
> **Python** is like a mentor who trusts you to do the right thing but gives you
> tools (mypy, linters, tests) to check yourself.

The biggest adjustment for Swift developers:
1. **No compiler safety net** -- you need tests and type checkers instead.
2. **Truthiness everywhere** -- empty containers, zero, and None are all falsy.
3. **Everything is an object** -- even `int` and `bool` have methods.
4. **Convention over enforcement** -- `UPPER_CASE` for constants, `_prefix` for private.
