# Swift vs Python: Data Structures

## Collections Overview

| Feature | Swift | Python |
|---------|-------|--------|
| Ordered, mutable sequence | `Array<T>` / `[T]` | `list` |
| Immutable sequence | `let arr = [1,2,3]` | `tuple` — `(1, 2, 3)` |
| Key-value mapping | `Dictionary<K,V>` / `[K:V]` | `dict` — `{k: v}` |
| Unique unordered collection | `Set<T>` | `set` — `{1, 2, 3}` |
| Immutable set | `let s: Set = [1,2]` | `frozenset({1, 2})` |
| Named fields | Struct / tuple labels | `namedtuple` / `@dataclass` |
| Double-ended queue | No built-in (use array) | `collections.deque` |

## Array (Swift) vs List (Python)

| Operation | Swift | Python |
|-----------|-------|--------|
| Create | `var a = [1, 2, 3]` | `a = [1, 2, 3]` |
| Append | `a.append(4)` | `a.append(4)` |
| Insert | `a.insert(0, at: 0)` | `a.insert(0, 0)` |
| Remove at index | `a.remove(at: 1)` | `a.pop(1)` or `del a[1]` |
| Remove by value | `a.removeAll { $0 == 2 }` | `a.remove(2)` |
| Length | `a.count` | `len(a)` |
| Check contains | `a.contains(3)` | `3 in a` |
| Sort in place | `a.sort()` | `a.sort()` |
| Sorted copy | `a.sorted()` | `sorted(a)` |
| Reverse | `a.reverse()` | `a.reverse()` or `a[::-1]` |
| First / Last | `a.first` / `a.last` | `a[0]` / `a[-1]` |
| Slice | `Array(a[1...3])` | `a[1:4]` |

## Slicing

| Operation | Swift | Python |
|-----------|-------|--------|
| First N | `Array(a.prefix(3))` | `a[:3]` |
| Last N | `Array(a.suffix(3))` | `a[-3:]` |
| Range | `Array(a[1..<4])` | `a[1:4]` |
| Every 2nd | Manual loop | `a[::2]` |
| Reversed | `Array(a.reversed())` | `a[::-1]` |

**Key difference:** Python slicing is far more powerful with `[start:stop:step]` syntax. Swift uses range operators and methods like `prefix`/`suffix`.

## Dictionary (Swift) vs dict (Python)

| Operation | Swift | Python |
|-----------|-------|--------|
| Create | `var d = ["a": 1, "b": 2]` | `d = {"a": 1, "b": 2}` |
| Access | `d["a"]` → `Optional` | `d["a"]` → raises `KeyError` |
| Safe access | `d["a"] ?? 0` | `d.get("a", 0)` |
| Set value | `d["c"] = 3` | `d["c"] = 3` |
| Remove | `d.removeValue(forKey: "a")` | `del d["a"]` or `d.pop("a")` |
| Keys | `d.keys` | `d.keys()` |
| Values | `d.values` | `d.values()` |
| Iterate | `for (k, v) in d` | `for k, v in d.items()` |
| Merge | `d.merge(other) { ... }` | `d \| other` (3.9+) or `d.update(other)` |
| Check key | `d["a"] != nil` | `"a" in d` |

**Key difference:** Swift dict access returns `Optional<V>`, Python raises `KeyError`. Use `.get()` in Python for safe access.

## Set (Swift) vs set (Python)

| Operation | Swift | Python |
|-----------|-------|--------|
| Create | `var s: Set = [1, 2, 3]` | `s = {1, 2, 3}` |
| Empty set | `Set<Int>()` | `set()` (NOT `{}` — that's a dict!) |
| Add | `s.insert(4)` | `s.add(4)` |
| Remove | `s.remove(2)` | `s.remove(2)` or `s.discard(2)` |
| Union | `s.union(other)` | `s \| other` or `s.union(other)` |
| Intersection | `s.intersection(other)` | `s & other` |
| Difference | `s.subtracting(other)` | `s - other` |
| Symmetric diff | `s.symmetricDifference(other)` | `s ^ other` |
| Subset | `s.isSubset(of: other)` | `s <= other` or `s.issubset(other)` |

## Tuples

| Feature | Swift | Python |
|---------|-------|--------|
| Create | `let t = (1, "hello", true)` | `t = (1, "hello", True)` |
| Access by index | `t.0`, `t.1` | `t[0]`, `t[1]` |
| Named elements | `let t = (x: 1, y: 2)` | `from collections import namedtuple` |
| Destructure | `let (a, b, c) = t` | `a, b, c = t` |
| Ignore element | `let (a, _, c) = t` | `a, _, c = t` |
| Mutability | Depends on `let`/`var` | Always immutable |

## Value Types vs Reference Types

| Concept | Swift | Python |
|---------|-------|--------|
| Value semantics | `struct`, `enum`, `Array`, `Dict`, `Set` | Immutable types: `int`, `str`, `tuple`, `frozenset` |
| Reference semantics | `class` | `list`, `dict`, `set`, all custom classes |
| Copy behavior | Structs copy on assignment | Lists/dicts share reference; use `.copy()` or `copy.deepcopy()` |
| Identity check | `===` | `is` |
| Equality check | `==` (requires `Equatable`) | `==` (requires `__eq__`) |

## Python's collections Module (No Swift Equivalent)

```python
from collections import defaultdict, Counter, OrderedDict, deque, namedtuple

# defaultdict — auto-initializes missing keys
word_count = defaultdict(int)
word_count["hello"] += 1  # No KeyError!

# Counter — count occurrences
Counter(["a", "b", "a", "c", "a"])  # Counter({'a': 3, 'b': 1, 'c': 1})

# deque — efficient append/pop from both ends
d = deque([1, 2, 3])
d.appendleft(0)  # O(1) vs O(n) for list.insert(0, x)

# namedtuple — lightweight immutable class (like a Swift struct)
Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)
print(p.x)  # 1
```

## Unpacking (Python-Specific)

```python
# Starred unpacking — no Swift equivalent
first, *rest = [1, 2, 3, 4, 5]    # first=1, rest=[2,3,4,5]
first, *mid, last = [1, 2, 3, 4]  # first=1, mid=[2,3], last=4

# Dict unpacking
defaults = {"color": "blue", "size": 10}
custom = {**defaults, "size": 20}  # {"color": "blue", "size": 20}
```
