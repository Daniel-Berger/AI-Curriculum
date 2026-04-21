# Module 02: Control Flow

## Introduction for Swift Developers

Python's control flow will feel familiar in concept but different in syntax. No braces,
no parentheses around conditions, and colons everywhere. But the real power is in
Python's unique features: comprehensions, the walrus operator, `else` on loops, and
pattern matching with `match/case`.

This module covers everything you need to write expressive, Pythonic control flow.

---

## 1. Conditional Statements: if / elif / else

### Basic Syntax

```python
# Python: colons and indentation, no braces
age = 25

if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teenager")
else:
    print("Child")
```

Compare with Swift:
```swift
// Swift
if age >= 18 {
    print("Adult")
} else if age >= 13 {
    print("Teenager")
} else {
    print("Child")
}
```

### Key Differences from Swift

1. **No parentheses** around the condition (they're optional but non-Pythonic)
2. **Colon** after each condition
3. **`elif`** not `else if`
4. **Indentation** defines the block (4 spaces by convention)
5. **No braces** -- indentation IS the syntax

```python
# Parentheses are allowed but not Pythonic
if (age >= 18):    # Works but avoid
    print("Adult")

if age >= 18:      # Pythonic
    print("Adult")

# Multi-line conditions: use parentheses for line continuation
if (age >= 18
        and has_id
        and not is_banned):
    print("Allowed entry")

# Or use backslash continuation (less preferred)
if age >= 18 \
        and has_id:
    print("Allowed entry")
```

### Truthiness in Conditions

This is where Python diverges most from Swift. You don't need explicit boolean
expressions:

```python
# Pythonic (using truthiness)
name = "Daniel"
items = [1, 2, 3]
count = 0
value = None

if name:           # True (non-empty string)
    print(name)

if items:          # True (non-empty list)
    print(items)

if not count:      # True (0 is falsy)
    print("no items")

if value is None:  # Explicit None check (preferred over `not value`)
    print("no value")
```

### Single-Line If (Ternary Expression)

```python
# Python ternary: value_if_true if condition else value_if_false
status = "adult" if age >= 18 else "minor"

# Swift equivalent: let status = age >= 18 ? "adult" : "minor"

# Can be chained (but gets unreadable fast)
category = "senior" if age >= 65 else "adult" if age >= 18 else "minor"

# Nested ternaries are a code smell -- use if/elif/else instead
```

### No `guard` Statement

Python doesn't have Swift's `guard`. Use early returns instead:

```python
# Swift guard equivalent: early return
def process_user(user: dict | None) -> str:
    if user is None:
        return "No user"

    if "name" not in user:
        return "No name"

    name = user["name"]
    if not name:
        return "Empty name"

    return f"Processing {name}"
```

---

## 2. For Loops

### Basic For Loop

Python's `for` loop always iterates over an *iterable* -- there's no C-style
`for (i = 0; i < n; i++)`:

```python
# Iterate over a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Iterate over a string
for char in "hello":
    print(char)

# Iterate over a dictionary
scores = {"Alice": 95, "Bob": 87, "Charlie": 92}
for name in scores:           # Iterates over KEYS by default
    print(name)

for name, score in scores.items():  # Key-value pairs
    print(f"{name}: {score}")

for score in scores.values():       # Values only
    print(score)
```

### The `range()` Function

`range()` generates a sequence of numbers. It's Python's answer to C-style loops:

```python
# range(stop) -- 0 to stop-1
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# range(start, stop) -- start to stop-1
for i in range(2, 5):
    print(i)  # 2, 3, 4

# range(start, stop, step)
for i in range(0, 10, 2):
    print(i)  # 0, 2, 4, 6, 8

# Counting down
for i in range(5, 0, -1):
    print(i)  # 5, 4, 3, 2, 1

# range is lazy -- doesn't create a list in memory
r = range(1_000_000_000)  # Instant, uses almost no memory
print(999_999 in r)        # True (O(1) lookup!)
```

Compare with Swift:
```swift
// Swift
for i in 0..<5 { print(i) }       // Python: range(5)
for i in 2..<5 { print(i) }       // Python: range(2, 5)
for i in stride(from: 0, to: 10, by: 2) { print(i) }  // Python: range(0, 10, 2)
for i in (1...5).reversed() { print(i) }  // Python: range(5, 0, -1)
```

### `enumerate()` -- Index + Value

```python
# Instead of tracking index manually:
fruits = ["apple", "banana", "cherry"]

# Pythonic way
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
# 0: apple
# 1: banana
# 2: cherry

# Start from a different index
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}: {fruit}")
# 1: apple
# 2: banana
# 3: cherry
```

Swift equivalent:
```swift
// Swift
for (i, fruit) in fruits.enumerated() {
    print("\(i): \(fruit)")
}
```

### `zip()` -- Parallel Iteration

```python
names = ["Alice", "Bob", "Charlie"]
scores = [95, 87, 92]
grades = ["A", "B+", "A-"]

# Iterate two sequences in parallel
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# Iterate three or more
for name, score, grade in zip(names, scores, grades):
    print(f"{name}: {score} ({grade})")

# zip stops at the shortest sequence
short = [1, 2]
long = [10, 20, 30]
list(zip(short, long))  # [(1, 10), (2, 20)]  -- 30 is dropped

# To keep going to the longest, use itertools.zip_longest
from itertools import zip_longest
list(zip_longest(short, long, fillvalue=0))
# [(1, 10), (2, 20), (0, 30)]

# Creating a dict from two lists
name_score = dict(zip(names, scores))
# {"Alice": 95, "Bob": 87, "Charlie": 92}
```

Swift equivalent:
```swift
// Swift
for (name, score) in zip(names, scores) {
    print("\(name): \(score)")
}
```

### Unpacking in Loops

```python
# List of tuples
points = [(1, 2), (3, 4), (5, 6)]
for x, y in points:
    print(f"({x}, {y})")

# List of dicts (common pattern with APIs)
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
]
for user in users:
    print(f"{user['name']} is {user['age']}")
```

---

## 3. While Loops

```python
# Basic while loop
count = 0
while count < 5:
    print(count)
    count += 1

# While with complex condition
import random
attempts = 0
while (guess := random.randint(1, 10)) != 7:
    attempts += 1
print(f"Found 7 after {attempts} attempts")

# Infinite loop with break
while True:
    line = input("Enter command (q to quit): ")
    if line == "q":
        break
    print(f"Processing: {line}")
```

**Note**: Python has no `repeat...while` (Swift's `do...while`). Use `while True` with
a `break` instead:

```python
# Python equivalent of Swift's repeat { } while condition
while True:
    data = get_data()
    process(data)
    if not should_continue(data):
        break
```

---

## 4. Break, Continue, and the `else` Clause on Loops

### `break` and `continue`

These work the same as Swift:

```python
# break exits the loop
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue skips to next iteration
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 1, 3, 5, 7, 9
```

### The `else` Clause on Loops (Python Unique!)

Python loops can have an `else` block that runs **only if the loop completed without
hitting `break`**. This is Python-unique and many developers find it confusing, but
it's useful for search patterns:

```python
# else runs when loop completes naturally (no break)
for item in items:
    if item == target:
        print(f"Found {target}")
        break
else:
    # This runs if we DIDN'T break (target not found)
    print(f"{target} not found")

# Real-world example: searching for a prime factor
n = 97
for i in range(2, int(n**0.5) + 1):
    if n % i == 0:
        print(f"{n} is divisible by {i}")
        break
else:
    print(f"{n} is prime")

# Same pattern with while loops
while condition:
    if found_something:
        break
else:
    print("Loop completed without finding anything")
```

Think of `else` as "no break" -- it runs when the loop finishes without `break`.

---

## 5. Comprehensions

Comprehensions are one of Python's most distinctive features. They create collections
in a single, readable expression.

### List Comprehensions

```python
# Basic: [expression for item in iterable]
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# With condition: [expression for item in iterable if condition]
even_squares = [x**2 for x in range(10) if x % 2 == 0]
# [0, 4, 16, 36, 64]

# Transform: apply function to each element
names = ["alice", "bob", "charlie"]
capitalized = [name.capitalize() for name in names]
# ["Alice", "Bob", "Charlie"]

# Flatten nested lists
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# With if/else (note: this goes BEFORE the for)
labels = ["even" if x % 2 == 0 else "odd" for x in range(5)]
# ["even", "odd", "even", "odd", "even"]

# Nested comprehension (2D grid)
grid = [(x, y) for x in range(3) for y in range(3)]
# [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)]
```

Swift equivalent:
```swift
// Swift
let squares = (0..<10).map { $0 * $0 }
let evenSquares = (0..<10).filter { $0 % 2 == 0 }.map { $0 * $0 }
let capitalized = names.map { $0.capitalized }
```

### Dict Comprehensions

```python
# {key_expr: value_expr for item in iterable}
squares_dict = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Swap keys and values
original = {"a": 1, "b": 2, "c": 3}
swapped = {v: k for k, v in original.items()}
# {1: "a", 2: "b", 3: "c"}

# Filter a dict
scores = {"Alice": 95, "Bob": 67, "Charlie": 82, "Diana": 91}
passing = {name: score for name, score in scores.items() if score >= 80}
# {"Alice": 95, "Charlie": 82, "Diana": 91}

# From two lists
keys = ["name", "age", "city"]
values = ["Alice", 30, "NYC"]
person = dict(zip(keys, values))
# or: {k: v for k, v in zip(keys, values)}
```

### Set Comprehensions

```python
# {expression for item in iterable}
unique_lengths = {len(word) for word in ["hello", "world", "hi", "hey"]}
# {2, 3, 5}

# Unique first letters
first_letters = {name[0].lower() for name in names}
```

### Generator Expressions

Generator expressions look like comprehensions but use `()` instead of `[]`. They
produce values lazily (one at a time), saving memory:

```python
# Generator expression (lazy -- values computed on demand)
gen = (x**2 for x in range(1_000_000))
print(next(gen))  # 0
print(next(gen))  # 1
print(next(gen))  # 4

# Great for passing to functions that consume iterables
total = sum(x**2 for x in range(1000))  # No brackets needed inside function call
any_negative = any(x < 0 for x in numbers)
all_positive = all(x > 0 for x in numbers)

# Memory comparison
list_comp = [x**2 for x in range(1_000_000)]  # Creates entire list in memory
gen_exp = (x**2 for x in range(1_000_000))     # Almost no memory

# Use generators when you only need to iterate once
# Use lists when you need random access or multiple iterations
```

### When to Use Comprehensions vs Loops

```python
# USE a comprehension when:
# - Transforming/filtering data into a new collection
# - The logic fits in one line
squares = [x**2 for x in range(10)]

# USE a loop when:
# - You have side effects (print, write to file, etc.)
# - Logic is complex (multiple conditions, early exit)
# - Comprehension would be longer than 80 characters
for item in items:
    if complex_condition(item):
        process(item)
        log(item)

# AVOID overly complex comprehensions
# Bad: hard to read
result = [transform(x) for x in items if condition1(x) and condition2(x) or special_case(x)]

# Better: use a loop or break it up
filtered = [x for x in items if is_valid(x)]
result = [transform(x) for x in filtered]
```

---

## 6. Match / Case (Python 3.10+)

Python 3.10 introduced structural pattern matching, similar to Swift's `switch`:

### Basic Pattern Matching

```python
# Basic match/case
command = "quit"

match command:
    case "quit":
        print("Quitting")
    case "save":
        print("Saving")
    case "load":
        print("Loading")
    case _:                    # Wildcard (like Swift's `default`)
        print(f"Unknown: {command}")
```

Swift equivalent:
```swift
switch command {
case "quit":
    print("Quitting")
case "save":
    print("Saving")
default:
    print("Unknown: \(command)")
}
```

### Key Differences from Swift's switch

1. **No exhaustiveness checking** -- `case _` is optional
2. **No fallthrough** -- Python never falls through (no `break` needed)
3. **No `where` clause** -- use guards (see below)

### Pattern Matching with Guards

```python
match value:
    case x if x > 0:
        print("Positive")
    case x if x < 0:
        print("Negative")
    case 0:
        print("Zero")
```

### Matching Sequences and Structures

```python
# Match on structure
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

# Match with | (OR patterns)
match command:
    case "quit" | "exit" | "q":
        print("Goodbye")
    case "help" | "h" | "?":
        print("Showing help")

# Match on type
match value:
    case int(x):
        print(f"Integer: {x}")
    case str(s):
        print(f"String: {s}")
    case list(items):
        print(f"List with {len(items)} items")

# Match on dict-like structures
match event:
    case {"type": "click", "x": x, "y": y}:
        print(f"Click at ({x}, {y})")
    case {"type": "keypress", "key": key}:
        print(f"Key pressed: {key}")
    case {"type": t}:
        print(f"Unknown event type: {t}")

# Match with star patterns
match items:
    case []:
        print("Empty list")
    case [single]:
        print(f"Single item: {single}")
    case [first, *rest]:
        print(f"First: {first}, remaining: {rest}")
```

---

## 7. The Walrus Operator `:=` (Python 3.8+)

The walrus operator assigns a value AND returns it in a single expression. It's
similar to what Swift does with `if let`, but more general:

```python
# Without walrus operator
line = input()
while line != "quit":
    process(line)
    line = input()

# With walrus operator -- assign and test in one step
while (line := input()) != "quit":
    process(line)

# In if statements (similar to Swift's if-let)
if (n := len(items)) > 10:
    print(f"Too many items: {n}")

# In list comprehensions
results = [y for x in data if (y := expensive_compute(x)) > threshold]

# Reading file lines
with open("file.txt") as f:
    while (line := f.readline()):
        process(line.strip())

# Finding a match in a list
if (match := next((x for x in items if x > 100), None)) is not None:
    print(f"Found: {match}")
```

Compare with Swift's `if let`:
```swift
// Swift
if let count = optionalCount, count > 10 {
    print("Too many: \(count)")
}
```

```python
# Python equivalent
if (count := get_count()) is not None and count > 10:
    print(f"Too many: {count}")
```

---

## 8. Logical Operators and Short-Circuit Evaluation

```python
# and, or, not (words, not symbols)
if age >= 18 and has_id:
    print("Allowed")

if is_admin or is_moderator:
    print("Has privileges")

if not is_banned:
    print("Welcome")
```

### Short-Circuit with `and` and `or`

Python's `and` and `or` return actual VALUES, not just True/False:

```python
# `or` returns the first truthy value, or the last value
"hello" or "default"    # "hello" (first truthy)
"" or "default"         # "default" (first is falsy)
None or "default"       # "default"
0 or "" or "fallback"   # "fallback" (first two are falsy)
0 or "" or []           # [] (all falsy, returns last)

# `and` returns the first falsy value, or the last value
"hello" and "world"     # "world" (both truthy, returns last)
"" and "world"          # "" (first is falsy)
None and "world"        # None

# Common patterns:
name = user_input or "Anonymous"       # Default value
result = condition and value           # Conditional value
items = data and data.get("items", []) # Safe access
```

---

## 9. Iteration Patterns and Idioms

### Iterating with Conditions

```python
# filter() function (functional style)
numbers = [1, -2, 3, -4, 5]
positives = list(filter(lambda x: x > 0, numbers))
# [1, 3, 5]

# Pythonic: comprehension (preferred over filter)
positives = [x for x in numbers if x > 0]

# map() function
squares = list(map(lambda x: x**2, numbers))
# [1, 4, 9, 16, 25]

# Pythonic: comprehension (preferred over map)
squares = [x**2 for x in numbers]
```

### `any()` and `all()` -- Short-Circuit Aggregation

```python
numbers = [2, 4, 6, 8, 10]

# all() -- True if ALL elements are truthy
all(x > 0 for x in numbers)     # True
all(x % 2 == 0 for x in numbers) # True

# any() -- True if ANY element is truthy
any(x > 5 for x in numbers)     # True
any(x > 100 for x in numbers)   # False

# Useful patterns
has_errors = any(result.failed for result in results)
all_valid = all(item.is_valid() for item in items)
```

### `sorted()`, `reversed()`, and Iteration Helpers

```python
# sorted() returns a new sorted list
numbers = [3, 1, 4, 1, 5, 9]
sorted(numbers)                    # [1, 1, 3, 4, 5, 9]
sorted(numbers, reverse=True)     # [9, 5, 4, 3, 1, 1]

# Sort by key function
words = ["banana", "apple", "cherry"]
sorted(words, key=len)            # ["apple", "banana", "cherry"]
sorted(words, key=str.lower)      # Case-insensitive sort

# reversed() returns an iterator
for x in reversed([1, 2, 3]):
    print(x)  # 3, 2, 1

# Chaining iteration tools
from itertools import chain, islice

# chain: iterate multiple iterables as one
for x in chain([1, 2], [3, 4], [5]):
    print(x)  # 1, 2, 3, 4, 5

# islice: slice an iterable (like list slicing but for any iterable)
from itertools import islice
first_three = list(islice(range(100), 3))  # [0, 1, 2]
```

---

## 10. Common Patterns

### Pattern: Accumulator

```python
# Building up a result
total = 0
for x in numbers:
    total += x

# Pythonic: use sum()
total = sum(numbers)

# Building a string
parts = []
for item in items:
    parts.append(str(item))
result = ", ".join(parts)

# Pythonic: one-liner
result = ", ".join(str(item) for item in items)
```

### Pattern: Find First Match

```python
# Loop approach
result = None
for item in items:
    if predicate(item):
        result = item
        break

# Pythonic: next() with generator
result = next((item for item in items if predicate(item)), None)
```

### Pattern: Group By

```python
# Building groups
groups = {}
for item in items:
    key = item.category
    if key not in groups:
        groups[key] = []
    groups[key].append(item)

# Pythonic: defaultdict
from collections import defaultdict
groups = defaultdict(list)
for item in items:
    groups[item.category].append(item)

# Even more Pythonic: itertools.groupby (requires sorted input)
from itertools import groupby
sorted_items = sorted(items, key=lambda x: x.category)
for key, group in groupby(sorted_items, key=lambda x: x.category):
    print(f"{key}: {list(group)}")
```

### Pattern: Flat Map

```python
# Swift: array.flatMap { ... }
nested = [[1, 2], [3, 4], [5, 6]]

# Python equivalent
flat = [item for sublist in nested for item in sublist]
# [1, 2, 3, 4, 5, 6]

# Or using itertools.chain
from itertools import chain
flat = list(chain.from_iterable(nested))
```

---

## 11. Exception-Based Control Flow

Python uses exceptions for control flow more liberally than Swift:

```python
# EAFP: Easier to Ask Forgiveness than Permission (Pythonic)
try:
    value = my_dict[key]
except KeyError:
    value = default

# LBYL: Look Before You Leap (Swift-like, less Pythonic)
if key in my_dict:
    value = my_dict[key]
else:
    value = default

# Best: use .get() for dicts specifically
value = my_dict.get(key, default)

# Iteration: StopIteration is used internally
iterator = iter([1, 2, 3])
next(iterator)  # 1
next(iterator)  # 2
next(iterator)  # 3
next(iterator)  # Raises StopIteration (caught by for loops automatically)
```

---

## 12. Pass, Ellipsis, and No-Op Statements

```python
# pass: explicit no-op (placeholder)
if condition:
    pass  # TODO: implement later

# Ellipsis (...): often used as placeholder in function bodies
def not_yet_implemented():
    ...

# Both are used in stub files and abstract methods
class Animal:
    def speak(self) -> str:
        ...   # Abstract -- subclass must implement
```

---

## Summary: Control Flow Quick Reference

| Feature | Swift | Python |
|---------|-------|--------|
| If/else | `if cond { } else { }` | `if cond: ... else: ...` |
| Else if | `else if` | `elif` |
| Ternary | `cond ? a : b` | `a if cond else b` |
| For range | `for i in 0..<5` | `for i in range(5)` |
| For each | `for x in array` | `for x in array` |
| Enumerated | `for (i,x) in arr.enumerated()` | `for i,x in enumerate(arr)` |
| While | `while cond { }` | `while cond:` |
| Switch/Match | `switch x { case .a: ... }` | `match x: case a: ...` |
| Guard | `guard cond else { return }` | `if not cond: return` |
| List comp | `arr.map { $0 * 2 }` | `[x*2 for x in arr]` |
| Filter | `arr.filter { $0 > 0 }` | `[x for x in arr if x > 0]` |
| Walrus | `if let x = expr` | `if (x := expr)` |
| For-else | N/A | `for x in y: ... else: ...` |

---

## Next Steps

In the next module, we'll dive into **Data Structures** -- lists, tuples, dicts, sets,
and Python's powerful `collections` module. Many of the patterns you learned here
(comprehensions, unpacking, iteration) will be applied to manipulate these structures.

Practice comprehensions until they feel natural -- they're one of the most common
Pythonic patterns you'll encounter in real codebases.
