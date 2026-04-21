# Swift vs Python: Functions and Closures

A side-by-side comparison for Swift/iOS developers learning Python.

---

## 1. Function Definition

| Feature | Swift | Python |
|---------|-------|--------|
| Keyword | `func` | `def` |
| Body delimiters | `{ }` | Indentation (colon `:` starts block) |
| Return type | `-> Int` | `-> int` (type hint, not enforced) |
| Argument labels | `func f(for name: String)` | No labels; keyword args by name |
| Omit label | `func f(_ name: String)` | Default behavior (no labels) |
| Void return | `-> Void` or omit | `-> None` or omit |

### Swift

```swift
func greet(name: String, with greeting: String = "Hello") -> String {
    return "\(greeting), \(name)!"
}

greet(name: "Alice", with: "Hey")
```

### Python

```python
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

greet("Alice", greeting="Hey")
```

---

## 2. Closures / Lambdas

| Feature | Swift | Python |
|---------|-------|--------|
| Anonymous function | `{ (params) -> Type in body }` | `lambda params: expression` |
| Multi-line body | Yes | No (single expression only) |
| Shorthand args | `$0`, `$1`, `$2` | Not available |
| Trailing closure syntax | `array.map { $0 * 2 }` | Not available |
| Type inference | Yes (often infers everything) | No type annotations on lambdas |
| Stored in variable | `let f: (Int) -> Int = { $0 * 2 }` | `f = lambda x: x * 2` |

### Swift Trailing Closures

```swift
// Swift's trailing closure syntax -- very common
let numbers = [1, 2, 3, 4, 5]

let doubled = numbers.map { $0 * 2 }
let evens = numbers.filter { $0 % 2 == 0 }
let sum = numbers.reduce(0) { $0 + $1 }
// or even: numbers.reduce(0, +)
```

### Python Equivalents

```python
numbers = [1, 2, 3, 4, 5]

# Functional style (less common in Python)
doubled = list(map(lambda x: x * 2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))
total = reduce(lambda acc, x: acc + x, numbers, 0)

# Pythonic style (preferred)
doubled = [x * 2 for x in numbers]
evens = [x for x in numbers if x % 2 == 0]
total = sum(numbers)
```

**Key insight:** Python lacks trailing closure syntax, so chained functional operations are
less elegant. List comprehensions fill this gap and are the idiomatic Python approach.

---

## 3. @escaping vs Python Closures

| Concept | Swift | Python |
|---------|-------|--------|
| Default capture | Non-escaping (for function params) | Always "escaping" |
| Escaping annotation | `@escaping` required | Not needed -- all closures escape by default |
| Stored closures | Must be `@escaping` | Always allowed |
| Completion handlers | `completion: @escaping (Result) -> Void` | Regular `Callable` parameter |

### Swift

```swift
class NetworkManager {
    var completionHandlers: [(String) -> Void] = []

    // Must mark as @escaping because closure outlives function scope
    func fetchData(completion: @escaping (String) -> Void) {
        completionHandlers.append(completion)
    }
}
```

### Python

```python
class NetworkManager:
    def __init__(self):
        self.completion_handlers: list[Callable[[str], None]] = []

    def fetch_data(self, completion: Callable[[str], None]) -> None:
        # No @escaping needed -- closures always outlive their scope
        self.completion_handlers.append(completion)
```

**Key insight:** Python has no concept of escaping vs non-escaping closures. All function
objects can be stored, passed around, and called later. There is no compiler check for this.

---

## 4. Capture Lists vs `nonlocal`

| Concept | Swift | Python |
|---------|-------|--------|
| Capture by reference | Default for reference types | Default for everything |
| Capture by value | `[x]` in capture list | `lambda x=x: ...` (default arg trick) |
| Weak capture | `[weak self]` | No equivalent (use `weakref` module) |
| Unowned capture | `[unowned self]` | No equivalent |
| Modify captured var | Automatic for reference types | Requires `nonlocal` keyword |

### Swift Capture Lists

```swift
func makeCounter() -> () -> Int {
    var count = 0
    // count is captured by reference automatically
    return {
        count += 1
        return count
    }
}

// With capture list (value capture)
var x = 10
let closure = { [x] in print(x) }  // Captures current value of x
x = 20
closure()  // Prints 10, not 20
```

### Python `nonlocal`

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count  # Required to modify count
        count += 1
        return count

    return increment

# Value capture workaround
x = 10
closure = lambda x=x: print(x)  # Captures current value via default arg
x = 20
closure()  # Prints 10, not 20
```

### The Loop Capture Problem

Both languages can encounter this, but Python makes it more common:

```swift
// Swift -- each closure captures a separate copy of i
var closures: [() -> Int] = []
for i in 0..<5 {
    closures.append { i }  // Value type, captured by value in the capture
}
closures.map { $0() }  // [0, 1, 2, 3, 4] -- correct!
```

```python
# Python -- all closures share the same variable i
closures = []
for i in range(5):
    closures.append(lambda: i)  # All see the final value of i

[fn() for fn in closures]  # [4, 4, 4, 4, 4] -- surprise!

# Fix with default parameter
closures = []
for i in range(5):
    closures.append(lambda i=i: i)

[fn() for fn in closures]  # [0, 1, 2, 3, 4] -- correct
```

---

## 5. map / filter / reduce Comparison

| Operation | Swift | Python (Functional) | Python (Idiomatic) |
|-----------|-------|--------------------|--------------------|
| Transform | `.map { $0 * 2 }` | `list(map(lambda x: x*2, lst))` | `[x*2 for x in lst]` |
| Filter | `.filter { $0 > 0 }` | `list(filter(lambda x: x>0, lst))` | `[x for x in lst if x>0]` |
| Reduce | `.reduce(0, +)` | `reduce(lambda a,x: a+x, lst, 0)` | `sum(lst)` |
| CompactMap | `.compactMap { Int($0) }` | N/A built-in | `[r for x in lst if (r:=f(x)) is not None]` |
| FlatMap | `.flatMap { $0.items }` | N/A built-in | `[y for x in lst for y in x.items]` |
| Chaining | `.filter{}.map{}.reduce{}` | Nested calls (ugly) | Generator expressions |
| Lazy | `.lazy.map{}.filter{}` | `map()` / `filter()` are lazy | Generator expressions |

### Chaining Example

```swift
// Swift -- elegant chaining
let result = numbers
    .filter { $0 % 2 == 0 }
    .map { $0 * $0 }
    .reduce(0, +)
```

```python
# Python -- functional style (less readable when chained)
result = reduce(
    lambda acc, x: acc + x,
    map(lambda x: x * x, filter(lambda x: x % 2 == 0, numbers)),
    0,
)

# Python -- Pythonic style (preferred)
result = sum(x * x for x in numbers if x % 2 == 0)
```

---

## 6. Higher-Order Function Patterns

| Pattern | Swift | Python |
|---------|-------|--------|
| Function as parameter | `func apply(_ f: (Int) -> Int, to x: Int)` | `def apply(f: Callable[[int], int], x: int)` |
| Return a function | `func makeAdder(_ n: Int) -> (Int) -> Int` | `def make_adder(n: int) -> Callable[[int], int]` |
| Partial application | Manual closure | `functools.partial(func, arg)` |
| Memoization | Manual dictionary | `@functools.lru_cache` decorator |
| Function composition | Manual or custom operator | `functools.reduce` or manual |

### Partial Application

```swift
// Swift -- manual partial application via closure
func power(_ base: Int, _ exponent: Int) -> Int {
    return Int(pow(Double(base), Double(exponent)))
}

let square = { (x: Int) in power(x, 2) }
let cube = { (x: Int) in power(x, 3) }
```

```python
from functools import partial

def power(base: int, exponent: int) -> int:
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)
```

---

## 7. Variadic Parameters

| Feature | Swift | Python |
|---------|-------|--------|
| Variadic positional | `values: Int...` | `*args` |
| Type inside function | `[Int]` (Array) | `tuple` |
| Variadic keyword | Not available | `**kwargs` (becomes `dict`) |
| Unpacking into call | Not available | `func(*list)`, `func(**dict)` |
| Multiple variadic | One per function | One `*args`, one `**kwargs` |

### Swift

```swift
func sum(_ values: Int...) -> Int {
    return values.reduce(0, +)  // values is [Int]
}

sum(1, 2, 3)  // 6
```

### Python

```python
def sum_all(*values: int) -> int:
    return sum(values)  # values is tuple[int, ...]

sum_all(1, 2, 3)  # 6

# Python also has **kwargs -- no Swift equivalent
def config(**options: str) -> dict[str, str]:
    return options

config(host="localhost", port="8080")
# {'host': 'localhost', 'port': '8080'}
```

---

## 8. Documentation

| Feature | Swift | Python |
|---------|-------|--------|
| Doc comment syntax | `/// Single line` or `/** Multi-line */` | `"""Triple-quoted docstring"""` |
| Param docs | `/// - Parameter name: description` | `Args:\n    name: description` (Google style) |
| Return docs | `/// - Returns: description` | `Returns:\n    description` |
| Throws docs | `/// - Throws: description` | `Raises:\n    ErrorType: description` |
| Runtime access | No (compile-time only) | Yes (`func.__doc__`) |
| Markup language | Markdown | reStructuredText or plain text |

---

## Summary: Mental Model Shifts

| Swift Concept | Python Equivalent | Key Difference |
|---------------|-------------------|----------------|
| Closure `{ }` | `lambda` or `def` | Lambdas are single-expression only |
| Trailing closure | List comprehension | Different syntax, same idea |
| `@escaping` | N/A | All Python closures escape |
| Capture list `[x]` | Default arg `x=x` | Python has no capture list syntax |
| `[weak self]` | `weakref.ref(self)` | Manual, not language-level |
| `.map { }` | `[... for ...]` | Comprehensions are preferred |
| Argument labels | Keyword arguments | Python uses parameter names directly |
| `Int...` variadic | `*args` | Python also has `**kwargs` |
| No equivalent | `nonlocal` | Required to mutate enclosed variables |
| No equivalent | `functools.partial` | Built-in partial application |
| No equivalent | `@lru_cache` | Built-in memoization decorator |
