# Module 03: Data Structures

## Introduction for Swift Developers

Python's data structures are simpler than Swift's in some ways (no value type vs
reference type distinction) and richer in others (slicing, the `collections` module,
structural pattern matching). This lesson covers the four core built-in types --
`list`, `tuple`, `dict`, `set` -- plus the essential tools from `collections`.

Coming from Swift, the biggest mental shifts will be:
- Lists are always mutable (no `let` arrays)
- Tuples are always immutable (but not just for function returns)
- Dicts are ordered by insertion (since Python 3.7)
- Everything is a reference (no value types)

---

## 1. Lists

Python's `list` is equivalent to Swift's `Array`. It's ordered, mutable, and can hold
mixed types (though you usually shouldn't).

### Creating Lists

```python
# Empty list
empty = []
empty = list()

# With values
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True, None]  # Valid but avoid

# From other iterables
from_range = list(range(5))         # [0, 1, 2, 3, 4]
from_string = list("hello")        # ["h", "e", "l", "l", "o"]
from_tuple = list((1, 2, 3))       # [1, 2, 3]

# List repetition
zeros = [0] * 5                    # [0, 0, 0, 0, 0]
grid = [[0] * 3 for _ in range(3)] # [[0,0,0], [0,0,0], [0,0,0]]

# DANGER: Don't do this for 2D lists!
bad_grid = [[0] * 3] * 3  # All 3 rows are the SAME list object!
bad_grid[0][0] = 1         # Changes ALL rows: [[1,0,0], [1,0,0], [1,0,0]]
```

### List Methods

```python
fruits = ["apple", "banana", "cherry"]

# Adding elements
fruits.append("date")          # Add to end: ["apple", "banana", "cherry", "date"]
fruits.insert(1, "avocado")   # Insert at index: ["apple", "avocado", "banana", ...]
fruits.extend(["fig", "grape"])  # Add multiple: ...

# Removing elements
fruits.remove("banana")       # Remove first occurrence (ValueError if not found)
popped = fruits.pop()         # Remove and return last item
popped = fruits.pop(0)        # Remove and return item at index
fruits.clear()                # Remove all items

# Searching
fruits = ["apple", "banana", "cherry", "banana"]
fruits.index("banana")        # 1 (first occurrence, ValueError if not found)
fruits.count("banana")        # 2
"banana" in fruits             # True (containment check)

# Sorting
numbers = [3, 1, 4, 1, 5, 9]
numbers.sort()                 # In-place sort: [1, 1, 3, 4, 5, 9]
numbers.sort(reverse=True)     # Descending: [9, 5, 4, 3, 1, 1]
numbers.sort(key=abs)          # Sort by absolute value

# sorted() returns a NEW list (doesn't modify original)
original = [3, 1, 4, 1, 5]
sorted_copy = sorted(original)  # original is unchanged

# Reversing
numbers.reverse()              # In-place reverse
reversed_copy = list(reversed(numbers))  # New reversed list
reversed_copy = numbers[::-1]  # Slice-based reverse (creates new list)

# Copying
shallow = fruits.copy()        # Shallow copy (same as fruits[:])
shallow = list(fruits)         # Also a shallow copy

import copy
deep = copy.deepcopy(fruits)   # Deep copy (for nested structures)
```

### List Slicing

Slicing is one of Python's superpowers. The syntax is `list[start:stop:step]`:

```python
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Basic slicing (start inclusive, stop exclusive)
nums[2:5]     # [2, 3, 4]
nums[:3]      # [0, 1, 2] (from beginning)
nums[7:]      # [7, 8, 9] (to end)
nums[:]       # [0, 1, 2, ..., 9] (shallow copy)

# Negative indexing
nums[-1]      # 9 (last element)
nums[-3:]     # [7, 8, 9] (last 3)
nums[:-2]     # [0, 1, 2, 3, 4, 5, 6, 7] (all but last 2)

# Step
nums[::2]     # [0, 2, 4, 6, 8] (every 2nd)
nums[1::2]    # [1, 3, 5, 7, 9] (every 2nd, starting at 1)
nums[::-1]    # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] (reversed)
nums[::-2]    # [9, 7, 5, 3, 1] (reversed, every 2nd)

# Slice assignment (modify in place)
nums[2:5] = [20, 30, 40]    # Replace elements
nums[2:5] = [20, 30]        # Replace with fewer (list shrinks)
nums[2:2] = [99, 98]        # Insert without removing
nums[2:5] = []              # Delete elements

# Slice objects (reusable slices)
first_three = slice(0, 3)
nums[first_three]            # Same as nums[0:3]
```

### List as Stack and Queue

```python
# Stack (LIFO): use append/pop
stack = []
stack.append(1)    # push
stack.append(2)
stack.append(3)
stack.pop()        # 3 (pop from end -- O(1))

# Queue (FIFO): DON'T use list -- use collections.deque instead
from collections import deque
queue = deque()
queue.append(1)     # enqueue (right end)
queue.append(2)
queue.popleft()     # 1 (dequeue from left end -- O(1))
# list.pop(0) is O(n) -- deque.popleft() is O(1)
```

---

## 2. Tuples

Tuples are immutable, ordered sequences. Think of them as read-only lists or
lightweight structs.

### Creating Tuples

```python
# With parentheses
point = (3, 4)
rgb = (255, 128, 0)

# Without parentheses (tuple packing)
point = 3, 4  # Still a tuple!

# Single-element tuple (needs trailing comma!)
single = (42,)    # Tuple
not_tuple = (42)  # Just an int! The parentheses are just grouping.

# Empty tuple
empty = ()
empty = tuple()

# From iterable
from_list = tuple([1, 2, 3])
from_string = tuple("abc")  # ("a", "b", "c")
```

### Tuple Operations

```python
point = (3, 4, 5)

# Indexing and slicing (same as list)
point[0]       # 3
point[-1]      # 5
point[1:]      # (4, 5)

# Immutability
# point[0] = 10  # TypeError: 'tuple' object does not support item assignment

# But mutable contents CAN be modified!
mixed = ([1, 2], [3, 4])
mixed[0].append(3)  # ([1, 2, 3], [3, 4]) -- the list inside is mutable

# Concatenation and repetition
(1, 2) + (3, 4)    # (1, 2, 3, 4)
(1, 2) * 3          # (1, 2, 1, 2, 1, 2)

# Methods (only two!)
point.count(3)      # 1
point.index(4)      # 1

# Comparison (lexicographic)
(1, 2) < (1, 3)    # True
(1, 2) < (2, 0)    # True (compares first elements first)
```

### Tuple Unpacking

```python
# Basic unpacking
x, y = (3, 4)

# In function returns
def get_bounds():
    return 0, 100  # Returns a tuple

low, high = get_bounds()

# Star unpacking
first, *rest = (1, 2, 3, 4, 5)
# first = 1, rest = [2, 3, 4, 5]  (rest is a LIST, not tuple)

first, *middle, last = (1, 2, 3, 4, 5)
# first = 1, middle = [2, 3, 4], last = 5

# Ignore values with _
_, y, _ = (1, 2, 3)
```

### Named Tuples

Named tuples give tuple elements names -- like a lightweight struct:

```python
from collections import namedtuple

# Define a named tuple type
Point = namedtuple("Point", ["x", "y"])

# Create instances
p = Point(3, 4)
p = Point(x=3, y=4)  # Keyword arguments

# Access by name or index
p.x      # 3
p[0]     # 3
x, y = p  # Unpacking still works

# Named tuples are immutable
# p.x = 5  # AttributeError

# Replace (creates a new tuple)
p2 = p._replace(x=10)  # Point(x=10, y=4)

# Convert to dict
p._asdict()  # {'x': 3, 'y': 4}

# Modern alternative: typing.NamedTuple (with type hints)
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float
    label: str = "origin"  # Default value

p = Point(3, 4)           # Point(x=3, y=4, label='origin')
p = Point(3, 4, "A")      # Point(x=3, y=4, label='A')
```

### When to Use Tuples vs Lists

```python
# Use TUPLES for:
# - Fixed structures (coordinates, RGB, date parts)
# - Dict keys (tuples are hashable, lists are not)
# - Function return values
# - Data that shouldn't change

point = (3, 4)
grid = {(0, 0): "start", (5, 5): "end"}  # Tuples as dict keys

# Use LISTS for:
# - Collections that grow/shrink
# - Data you'll sort or modify
# - Homogeneous collections

todos = ["buy milk", "write code", "learn Python"]
```

---

## 3. Dictionaries

Python's `dict` is equivalent to Swift's `Dictionary`. Keys must be hashable
(immutable). Since Python 3.7, dicts maintain insertion order.

### Creating Dicts

```python
# Literal syntax
person = {"name": "Daniel", "age": 30, "city": "NYC"}

# dict() constructor
person = dict(name="Daniel", age=30, city="NYC")

# From list of tuples
pairs = [("name", "Daniel"), ("age", 30)]
person = dict(pairs)

# Dict comprehension
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# From keys with default value
keys = ["a", "b", "c"]
defaults = dict.fromkeys(keys, 0)  # {"a": 0, "b": 0, "c": 0}

# Merge dicts (Python 3.9+)
a = {"x": 1, "y": 2}
b = {"y": 3, "z": 4}
merged = a | b   # {"x": 1, "y": 3, "z": 4}  (b wins on conflicts)
a |= b           # In-place merge
```

### Dict Operations

```python
person = {"name": "Daniel", "age": 30, "city": "NYC"}

# Access
person["name"]           # "Daniel"
# person["email"]        # KeyError!

# Safe access with .get()
person.get("name")       # "Daniel"
person.get("email")      # None (no error)
person.get("email", "")  # "" (custom default)

# Set/update
person["email"] = "d@example.com"   # Add or update
person.update({"age": 31, "phone": "555"})  # Update multiple

# setdefault: get value, setting it if missing
person.setdefault("country", "US")  # Sets and returns "US"
person.setdefault("name", "Other")  # Returns "Daniel" (already exists)

# Remove
del person["phone"]                  # Remove key (KeyError if missing)
email = person.pop("email")         # Remove and return (KeyError if missing)
email = person.pop("email", None)   # Remove and return, default if missing
last = person.popitem()             # Remove and return last (key, value) pair

# Iteration
for key in person:                   # Keys
    print(key)

for key, value in person.items():    # Key-value pairs
    print(f"{key}: {value}")

for value in person.values():        # Values only
    print(value)

# Membership
"name" in person      # True (checks keys only)
"Daniel" in person.values()  # True (checks values -- slower)

# Size
len(person)            # Number of key-value pairs
```

### Dict Views

```python
person = {"name": "Daniel", "age": 30}

# .keys(), .values(), .items() return VIEW objects (live references)
keys = person.keys()
print(keys)          # dict_keys(['name', 'age'])

person["city"] = "NYC"
print(keys)          # dict_keys(['name', 'age', 'city'])  -- updated!

# Views support set operations
a = {"x": 1, "y": 2, "z": 3}
b = {"y": 2, "z": 4, "w": 5}

a.keys() & b.keys()   # {'y', 'z'} (common keys)
a.keys() - b.keys()   # {'x'} (keys in a but not b)
a.keys() | b.keys()   # {'x', 'y', 'z', 'w'} (all keys)
a.items() & b.items()  # {('y', 2)} (common key-value pairs)
```

### defaultdict

```python
from collections import defaultdict

# defaultdict provides a default value for missing keys
word_counts = defaultdict(int)      # Default: 0
for word in "the cat sat on the mat".split():
    word_counts[word] += 1
# {'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1}

# Group items
groups = defaultdict(list)          # Default: empty list
for name, dept in [("Alice", "Eng"), ("Bob", "Sales"), ("Charlie", "Eng")]:
    groups[dept].append(name)
# {'Eng': ['Alice', 'Charlie'], 'Sales': ['Bob']}

# Nested defaultdict
nested = defaultdict(lambda: defaultdict(int))
nested["row1"]["col1"] = 42
```

### Counter

```python
from collections import Counter

# Count occurrences
colors = ["red", "blue", "red", "green", "blue", "red"]
count = Counter(colors)
# Counter({'red': 3, 'blue': 2, 'green': 1})

count["red"]           # 3
count["purple"]        # 0 (missing keys return 0, not KeyError)
count.most_common(2)   # [('red', 3), ('blue', 2)]

# Count characters in a string
letter_count = Counter("mississippi")
# Counter({'s': 4, 'i': 4, 'p': 2, 'm': 1})

# Arithmetic with Counters
a = Counter(["a", "b", "b", "c"])
b = Counter(["b", "c", "c", "d"])
a + b    # Counter({'b': 3, 'c': 3, 'a': 1, 'd': 1})
a - b    # Counter({'a': 1, 'b': 1})  (only positive counts)
a & b    # Counter({'b': 1, 'c': 1})  (min of each)
a | b    # Counter({'b': 2, 'c': 2, 'a': 1, 'd': 1})  (max of each)

# Total count (Python 3.10+)
count.total()          # 6

# Most common elements
count.most_common()    # All elements, most common first
```

### OrderedDict (Less Needed Since Python 3.7)

```python
from collections import OrderedDict

# Regular dicts are ordered since Python 3.7
# OrderedDict is still useful for:
# 1. move_to_end()
# 2. Equality considers order (regular dicts don't)
# 3. Explicitly communicating "order matters" in your code

od = OrderedDict(a=1, b=2, c=3)
od.move_to_end("a")          # Move 'a' to end
od.move_to_end("c", last=False)  # Move 'c' to beginning

# Order-sensitive equality
OrderedDict(a=1, b=2) == OrderedDict(b=2, a=1)  # False!
{"a": 1, "b": 2} == {"b": 2, "a": 1}            # True (regular dict)
```

---

## 4. Sets

Sets are unordered collections of unique, hashable elements. Equivalent to Swift's `Set`.

### Creating Sets

```python
# Literal syntax
colors = {"red", "green", "blue"}

# CAUTION: {} creates an EMPTY DICT, not an empty set!
empty_dict = {}        # This is a dict!
empty_set = set()      # Use set() for empty sets

# From iterable (deduplicates)
unique = set([1, 2, 2, 3, 3, 3])  # {1, 2, 3}
letters = set("hello")             # {'h', 'e', 'l', 'o'}

# Set comprehension
evens = {x for x in range(20) if x % 2 == 0}
```

### Set Operations

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# Set operations (return new sets)
a | b    # {1, 2, 3, 4, 5, 6}  (union)
a & b    # {3, 4}               (intersection)
a - b    # {1, 2}               (difference)
a ^ b    # {1, 2, 5, 6}         (symmetric difference)

# Method equivalents
a.union(b)
a.intersection(b)
a.difference(b)
a.symmetric_difference(b)

# In-place operations
a |= b   # a.update(b)
a &= b   # a.intersection_update(b)
a -= b   # a.difference_update(b)
a ^= b   # a.symmetric_difference_update(b)

# Subset/superset
{1, 2} <= {1, 2, 3}    # True (subset)
{1, 2, 3} >= {1, 2}    # True (superset)
{1, 2} < {1, 2, 3}     # True (proper subset)

# Membership (O(1) average)
3 in a     # True
10 in a    # False

# Adding/removing
a.add(5)           # Add single element
a.discard(5)       # Remove if present (no error if missing)
a.remove(5)        # Remove (KeyError if missing!)
popped = a.pop()   # Remove and return arbitrary element
a.clear()          # Remove all
```

### frozenset (Immutable Set)

```python
# frozenset is immutable -- can be used as dict key or set element
fs = frozenset([1, 2, 3])
# fs.add(4)  # AttributeError

# Use frozenset when you need a set as a dict key
cache = {}
key = frozenset(["a", "b", "c"])
cache[key] = "result"

# frozenset supports all non-mutating set operations
fs1 = frozenset([1, 2, 3])
fs2 = frozenset([2, 3, 4])
fs1 & fs2    # frozenset({2, 3})
```

---

## 5. The Collections Module

### deque (Double-Ended Queue)

```python
from collections import deque

# O(1) append/pop from both ends (list is O(n) for left operations)
d = deque([1, 2, 3])

d.append(4)         # Add to right: deque([1, 2, 3, 4])
d.appendleft(0)     # Add to left: deque([0, 1, 2, 3, 4])
d.pop()             # Remove from right: 4
d.popleft()         # Remove from left: 0
d.extend([4, 5])    # Extend right
d.extendleft([0])   # Extend left (reversed order)
d.rotate(1)         # Rotate right by 1
d.rotate(-1)        # Rotate left by 1

# Fixed-size deque (acts as circular buffer)
recent = deque(maxlen=3)
recent.append(1)    # deque([1])
recent.append(2)    # deque([1, 2])
recent.append(3)    # deque([1, 2, 3])
recent.append(4)    # deque([2, 3, 4]) -- 1 is dropped!

# Use cases:
# - BFS (breadth-first search)
# - Sliding window algorithms
# - Undo/redo stacks
# - Recent items buffer
```

### ChainMap

```python
from collections import ChainMap

# Combine multiple dicts into one logical view
defaults = {"color": "red", "size": "medium", "font": "Arial"}
user_prefs = {"color": "blue", "font": "Helvetica"}
cli_args = {"color": "green"}

# First dict in chain has highest priority
config = ChainMap(cli_args, user_prefs, defaults)
config["color"]   # "green" (from cli_args)
config["size"]    # "medium" (from defaults)
config["font"]    # "Helvetica" (from user_prefs)
```

---

## 6. Advanced Slicing

### Slice Objects

```python
# Named slices for readability
FIRST_NAME = slice(0, 20)
LAST_NAME = slice(20, 40)
AGE = slice(40, 45)

record = "Daniel              Berger              30   "
record[FIRST_NAME].strip()  # "Daniel"
record[LAST_NAME].strip()   # "Berger"
record[AGE].strip()          # "30"
```

### Multi-Dimensional Slicing (NumPy Preview)

```python
# Python lists don't support multi-dimensional slicing natively
# But this is a preview of NumPy syntax:

# Simulating with nested lists
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

# Get a column (no slice syntax -- use comprehension)
column_1 = [row[1] for row in matrix]  # [2, 5, 8]

# Get a submatrix (use nested slicing)
submatrix = [row[0:2] for row in matrix[0:2]]
# [[1, 2], [4, 5]]
```

---

## 7. Unpacking In Depth

### Star Unpacking (*args Style)

```python
# Unpack iterables with *
first, *rest = [1, 2, 3, 4, 5]
# first = 1, rest = [2, 3, 4, 5]

*head, last = [1, 2, 3, 4, 5]
# head = [1, 2, 3, 4], last = 5

first, *middle, last = [1, 2, 3, 4, 5]
# first = 1, middle = [2, 3, 4], last = 5

# In function calls
def add(a, b, c):
    return a + b + c

args = [1, 2, 3]
add(*args)          # Same as add(1, 2, 3)

# Unpack dict as keyword arguments
kwargs = {"a": 1, "b": 2, "c": 3}
add(**kwargs)       # Same as add(a=1, b=2, c=3)

# Merge lists/tuples with *
a = [1, 2]
b = [3, 4]
combined = [*a, *b, 5]  # [1, 2, 3, 4, 5]

# Merge dicts with **
a = {"x": 1}
b = {"y": 2}
combined = {**a, **b, "z": 3}  # {"x": 1, "y": 2, "z": 3}
```

### Nested Unpacking

```python
# Unpack nested structures
(a, b), (c, d) = [1, 2], [3, 4]

# In loops
data = [("Alice", (95, 87, 92)), ("Bob", (65, 70, 55))]
for name, (s1, s2, s3) in data:
    avg = (s1 + s2 + s3) / 3
    print(f"{name}: {avg:.1f}")

# Ignoring values
_, (_, important, _) = ("ignored", (1, 2, 3))
# important = 2
```

---

## 8. Structural Pattern Matching with Data Structures

Python 3.10+'s `match/case` is particularly powerful with data structures:

```python
# Match on list structure
def process_command(command: list[str]) -> str:
    match command:
        case []:
            return "No command"
        case ["quit"]:
            return "Goodbye"
        case ["greet", name]:
            return f"Hello, {name}!"
        case ["move", direction, distance]:
            return f"Moving {direction} by {distance}"
        case ["add", *items]:
            return f"Adding: {', '.join(items)}"
        case _:
            return "Unknown command"

process_command(["greet", "Daniel"])    # "Hello, Daniel!"
process_command(["add", "a", "b", "c"]) # "Adding: a, b, c"

# Match on dict structure
def process_record(record: dict) -> str:
    match record:
        case {"type": "user", "name": name, "role": "admin"}:
            return f"Admin user: {name}"
        case {"type": "user", "name": name}:
            return f"Regular user: {name}"
        case {"type": "log", "level": "error", "message": msg}:
            return f"ERROR: {msg}"
        case {"type": t}:
            return f"Unknown record type: {t}"

# Match with nested structures
def analyze_data(data):
    match data:
        case {"users": [{"name": first_name}, *rest]}:
            return f"First user: {first_name}, {len(rest)} more"
        case {"users": []}:
            return "No users"
        case {"error": {"code": code, "message": msg}}:
            return f"Error {code}: {msg}"
```

---

## 9. Copying: Shallow vs Deep

This is crucial for Python developers coming from Swift's value-type system:

```python
import copy

# Assignment is NOT copying -- it's creating another reference
a = [1, [2, 3], 4]
b = a           # b points to the SAME list as a
b.append(5)     # Modifies both a and b!
print(a)        # [1, [2, 3], 4, 5]

# Shallow copy: copies outer container, but inner objects are shared
a = [1, [2, 3], 4]
b = a.copy()    # or: b = a[:] or b = list(a)
b.append(5)     # Only modifies b
b[1].append(99) # Modifies BOTH a and b's inner list!
print(a)        # [1, [2, 3, 99], 4]
print(b)        # [1, [2, 3, 99], 4, 5]

# Deep copy: recursively copies everything
a = [1, [2, 3], 4]
b = copy.deepcopy(a)
b[1].append(99)  # Only modifies b
print(a)         # [1, [2, 3], 4]
print(b)         # [1, [2, 3, 99], 4]

# For dicts
original = {"a": [1, 2], "b": [3, 4]}
shallow = original.copy()        # or: dict(original)
deep = copy.deepcopy(original)
```

**Critical difference from Swift**: In Swift, `Array`, `Dictionary`, and `Set` are
value types -- assigning creates a copy automatically (copy-on-write). In Python,
assignment NEVER copies. You must explicitly copy.

---

## 10. Performance Characteristics

| Operation | list | tuple | dict | set |
|-----------|------|-------|------|-----|
| Index/Key access | O(1) | O(1) | O(1) avg | N/A |
| Search (`in`) | O(n) | O(n) | O(1) avg | O(1) avg |
| Append/Add | O(1) amortized | N/A | O(1) avg | O(1) avg |
| Insert (beginning) | O(n) | N/A | N/A | N/A |
| Delete | O(n) | N/A | O(1) avg | O(1) avg |
| Sort | O(n log n) | N/A | N/A | N/A |
| Memory | Low | Lowest | High | Medium |

**Key takeaways**:
- Use `set` or `dict` when you need fast membership testing (`in`)
- Use `deque` when you need fast append/pop from both ends
- Lists are best for ordered, indexed access
- Tuples use less memory than lists (consider for large read-only collections)

---

## 11. Choosing the Right Data Structure

```
Need ordered access by index?
  -> list (mutable) or tuple (immutable)

Need key-value mapping?
  -> dict (or defaultdict/Counter for specialized use)

Need unique elements and fast membership testing?
  -> set (mutable) or frozenset (immutable)

Need FIFO queue?
  -> collections.deque

Need to count occurrences?
  -> collections.Counter

Need a lightweight immutable record?
  -> tuple or NamedTuple

Need default values for missing keys?
  -> collections.defaultdict
```

---

## Summary: Quick Reference

| Feature | Swift | Python |
|---------|-------|--------|
| Ordered mutable | `[Int]` / `Array<Int>` | `list[int]` |
| Ordered immutable | `let arr: [Int]` | `tuple[int, ...]` |
| Key-value | `[String: Int]` / `Dictionary` | `dict[str, int]` |
| Unique unordered | `Set<Int>` | `set[int]` |
| Named fields | `struct` | `NamedTuple` or `dataclass` |
| Value semantics | Default (copy-on-write) | Never (use `copy.deepcopy`) |

---

## Next Steps

In the next module, we'll cover **Functions and Closures** -- Python's `def`, `lambda`,
decorators, `*args/**kwargs`, and how they compare to Swift's closures and function types.

Practice the exercises with a focus on:
- Slicing (you'll use it everywhere)
- Comprehensions with data structures
- Understanding shallow vs deep copy
- Using `defaultdict` and `Counter` for common patterns
