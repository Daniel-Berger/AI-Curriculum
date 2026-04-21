# Swift vs Python: Control Flow

A side-by-side comparison for Swift developers learning Python.

---

## Conditional Statements

| Feature | Swift | Python |
|---------|-------|--------|
| If statement | `if condition { }` | `if condition:` |
| Else if | `else if condition { }` | `elif condition:` |
| Else | `else { }` | `else:` |
| Parentheses | Optional around condition | Optional (avoid for style) |
| Braces | Required `{ }` | None -- uses indentation |
| Ternary | `cond ? a : b` | `a if cond else b` |
| Guard | `guard cond else { return }` | `if not cond: return` |

### Conditionals Side by Side

```swift
// Swift
let score = 85
let grade: String

if score >= 90 {
    grade = "A"
} else if score >= 80 {
    grade = "B"
} else if score >= 70 {
    grade = "C"
} else {
    grade = "F"
}
```

```python
# Python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"
```

### Ternary Expression

```swift
// Swift
let status = age >= 18 ? "adult" : "minor"

// Nested ternary
let label = score >= 90 ? "A" : score >= 80 ? "B" : "C"
```

```python
# Python (note: reversed order from Swift)
status = "adult" if age >= 18 else "minor"

# Nested ternary (avoid -- hard to read)
label = "A" if score >= 90 else "B" if score >= 80 else "C"
```

### Guard vs Early Return

```swift
// Swift
func process(_ value: String?) -> String {
    guard let value = value else {
        return "No value"
    }
    guard !value.isEmpty else {
        return "Empty"
    }
    return "Processing: \(value)"
}
```

```python
# Python (no guard -- use early returns)
def process(value: str | None) -> str:
    if value is None:
        return "No value"
    if not value:
        return "Empty"
    return f"Processing: {value}"
```

---

## Switch / Match-Case

| Feature | Swift | Python |
|---------|-------|--------|
| Keyword | `switch` | `match` (3.10+) |
| Cases | `case value:` | `case value:` |
| Default | `default:` | `case _:` |
| Exhaustiveness | Required by compiler | Not required |
| Fallthrough | Never (explicit `fallthrough`) | Never (no fallthrough keyword) |
| Multiple values | `case "a", "b":` | `case "a" \| "b":` |
| Where clause | `case let x where x > 0:` | `case x if x > 0:` |
| Value binding | `case let (x, y):` | `case (x, y):` |
| Enum matching | `case .success(let val):` | N/A (different enum system) |

### Basic Switch vs Match

```swift
// Swift
switch command {
case "quit", "exit":
    print("Goodbye")
case "help":
    print("Help text")
default:
    print("Unknown command")
}
```

```python
# Python 3.10+
match command:
    case "quit" | "exit":
        print("Goodbye")
    case "help":
        print("Help text")
    case _:
        print("Unknown command")
```

### Pattern Matching with Tuples

```swift
// Swift
let point = (3, 4)
switch point {
case (0, 0):
    print("Origin")
case (let x, 0):
    print("On x-axis at \(x)")
case (0, let y):
    print("On y-axis at \(y)")
case (let x, let y):
    print("Point at (\(x), \(y))")
}
```

```python
# Python
point = (3, 4)
match point:
    case (0, 0):
        print("Origin")
    case (x, 0):
        print(f"On x-axis at {x}")
    case (0, y):
        print(f"On y-axis at {y}")
    case (x, y):
        print(f"Point at ({x}, {y})")
```

### Where Clause vs Guard

```swift
// Swift
switch value {
case let x where x > 0:
    print("Positive: \(x)")
case let x where x < 0:
    print("Negative: \(x)")
case 0:
    print("Zero")
default:
    break
}
```

```python
# Python
match value:
    case x if x > 0:
        print(f"Positive: {x}")
    case x if x < 0:
        print(f"Negative: {x}")
    case 0:
        print("Zero")
```

### Enum Matching

```swift
// Swift
enum Result {
    case success(String)
    case failure(Error)
}

switch result {
case .success(let message):
    print("Success: \(message)")
case .failure(let error):
    print("Error: \(error)")
}
```

```python
# Python -- no direct equivalent, but can match on type
match result:
    case str(message):
        print(f"Success: {message}")
    case Exception() as error:
        print(f"Error: {error}")

# Or with dataclasses (more similar to Swift enums with associated values)
from dataclasses import dataclass

@dataclass
class Success:
    message: str

@dataclass
class Failure:
    error: str

match result:
    case Success(message=msg):
        print(f"Success: {msg}")
    case Failure(error=err):
        print(f"Error: {err}")
```

---

## For Loops

| Feature | Swift | Python |
|---------|-------|--------|
| Range (exclusive) | `for i in 0..<5` | `for i in range(5)` |
| Range (inclusive) | `for i in 1...5` | `for i in range(1, 6)` |
| Stride | `stride(from:to:by:)` | `range(start, stop, step)` |
| For-each | `for item in array` | `for item in array` |
| Enumerated | `for (i, x) in arr.enumerated()` | `for i, x in enumerate(arr)` |
| Zip | `for (a, b) in zip(x, y)` | `for a, b in zip(x, y)` |
| Reversed | `for i in (0..<5).reversed()` | `for i in reversed(range(5))` |
| Where clause | `for x in arr where x > 0` | No direct equivalent |

### Range Comparison

```swift
// Swift
for i in 0..<5 { print(i) }           // 0, 1, 2, 3, 4
for i in 1...5 { print(i) }           // 1, 2, 3, 4, 5
for i in stride(from: 0, to: 10, by: 2) { print(i) }  // 0, 2, 4, 6, 8
for i in (1...5).reversed() { print(i) }  // 5, 4, 3, 2, 1
```

```python
# Python
for i in range(5): print(i)           # 0, 1, 2, 3, 4
for i in range(1, 6): print(i)        # 1, 2, 3, 4, 5
for i in range(0, 10, 2): print(i)    # 0, 2, 4, 6, 8
for i in range(5, 0, -1): print(i)    # 5, 4, 3, 2, 1
```

### Where Clause Equivalent

```swift
// Swift: for-where
for item in items where item.isValid {
    process(item)
}
```

```python
# Python: no for-where, use if inside loop or comprehension
for item in items:
    if item.is_valid:
        process(item)

# Or filter first
valid_items = [item for item in items if item.is_valid]
for item in valid_items:
    process(item)
```

---

## If-Let / Optional Binding vs Walrus Operator

| Concept | Swift | Python |
|---------|-------|--------|
| Optional binding | `if let x = optional { }` | `if (x := expr) is not None:` |
| Guard let | `guard let x = optional else { return }` | `if (x := expr) is None: return` |
| While let | `while let x = iter.next() { }` | `while (x := next(iter, None)) is not None:` |
| Assign + test | Not separate | `if (n := len(x)) > 10:` |

### Side-by-Side Examples

```swift
// Swift: if-let
if let name = optionalName {
    print("Hello, \(name)")
}

// Swift: guard-let
guard let data = fetchData() else {
    return nil
}
process(data)

// Swift: while-let
while let line = readLine() {
    process(line)
}
```

```python
# Python: walrus operator (:=)
if (name := get_name()) is not None:
    print(f"Hello, {name}")

# Python: early return (guard-let equivalent)
if (data := fetch_data()) is None:
    return None
process(data)

# Python: while with walrus
while (line := input_stream.readline()):
    process(line)

# Python: walrus in comprehension (unique to Python)
results = [
    processed
    for item in items
    if (processed := expensive_compute(item)) is not None
]
```

### Important Difference

Swift's `if let` specifically unwraps optionals. Python's walrus operator is more
general -- it assigns any value and returns it. You often need to add an explicit
`is not None` check:

```python
# This catches None AND all falsy values (0, "", [], etc.)
if (x := get_value()):
    print(x)

# This catches only None
if (x := get_value()) is not None:
    print(x)
```

---

## Comprehensions vs Higher-Order Functions

| Operation | Swift | Python |
|-----------|-------|--------|
| Map | `arr.map { $0 * 2 }` | `[x * 2 for x in arr]` |
| Filter | `arr.filter { $0 > 0 }` | `[x for x in arr if x > 0]` |
| Map + Filter | `arr.filter { }.map { }` | `[expr for x in arr if cond]` |
| FlatMap | `arr.flatMap { $0 }` | `[y for x in arr for y in x]` |
| CompactMap | `arr.compactMap { Int($0) }` | `[int(x) for x in arr if x.isdigit()]` |
| Reduce | `arr.reduce(0, +)` | `sum(arr)` or `functools.reduce` |
| Contains | `arr.contains { $0 > 5 }` | `any(x > 5 for x in arr)` |
| All satisfy | `arr.allSatisfy { $0 > 0 }` | `all(x > 0 for x in arr)` |

### Chaining Comparison

```swift
// Swift: method chaining
let result = numbers
    .filter { $0 % 2 == 0 }
    .map { $0 * $0 }
    .reduce(0, +)
```

```python
# Python: single comprehension (preferred)
result = sum(x * x for x in numbers if x % 2 == 0)

# Python: step by step (for complex logic)
evens = [x for x in numbers if x % 2 == 0]
squares = [x * x for x in evens]
result = sum(squares)

# Python: functional style (less Pythonic)
from functools import reduce
result = reduce(
    lambda acc, x: acc + x,
    map(lambda x: x * x, filter(lambda x: x % 2 == 0, numbers)),
    0
)
```

---

## Loop Features Unique to Each Language

### Python-Only Features

| Feature | Python | Description |
|---------|--------|-------------|
| For-else | `for x in y: ... else: ...` | Else runs if no `break` |
| While-else | `while cond: ... else: ...` | Else runs if no `break` |
| Walrus in loops | `while (x := f()):` | Assign + test |
| Comprehensions | `[x for x in y if z]` | Create collections inline |
| Generator expressions | `(x for x in y)` | Lazy comprehension |

### Swift-Only Features

| Feature | Swift | Description |
|---------|-------|-------------|
| For-where | `for x in arr where cond` | Inline filter in loop |
| Labeled statements | `outer: for ... { break outer }` | Named loop control |
| repeat-while | `repeat { } while cond` | Do-while loop |
| Fallthrough | `fallthrough` | Explicit case fallthrough |
| #available | `if #available(iOS 15, *)` | OS version checking |

---

## Quick Mental Model

> **Swift's control flow** is about safety: exhaustive switches, forced unwrapping,
> compiler-checked conditions.
>
> **Python's control flow** is about expressiveness: comprehensions, truthiness,
> generators, and the walrus operator let you say more in fewer lines.

The biggest adjustments:
1. **Ternary is reversed**: `a if cond else b` (Python) vs `cond ? a : b` (Swift)
2. **No switch exhaustiveness**: Python won't warn if you miss a case
3. **Comprehensions replace map/filter**: Learn to think in `[expr for x in y if cond]`
4. **Truthiness replaces explicit checks**: `if items:` instead of `if !items.isEmpty`
5. **For-else is unique**: "else" means "no break occurred" -- useful for search patterns
