"""
Module 03: Data Structures - Exercises
=======================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` or `...` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- Focus on using the right data structure for each problem.

Difficulty levels:
  Easy   - Direct translation from Swift concepts
  Medium - Requires understanding Python-specific behavior
  Hard   - Combines multiple concepts or requires Pythonic thinking
"""
from collections import Counter, defaultdict, deque, namedtuple
from typing import NamedTuple


# =============================================================================
# WARM-UP: Lists, Tuples, Basic Operations
# =============================================================================

# Exercise 1: List Manipulation
# Difficulty: Easy
# Perform a sequence of list operations.
def list_operations(items: list[int]) -> dict[str, object]:
    """Perform various list operations and return results.

    Starting with a COPY of items (don't modify the original):
    1. Append 99 to the end
    2. Insert 0 at the beginning
    3. Sort in descending order
    4. Return a dict with:
       - 'result': the final list
       - 'length': length of the final list
       - 'first': first element
       - 'last': last element
       - 'sum': sum of all elements

    >>> list_operations([3, 1, 4, 1, 5])
    {'result': [99, 5, 4, 3, 1, 1, 0], 'length': 7, 'first': 99, 'last': 0, 'sum': 113}
    """
    pass


# Exercise 2: Slice Master
# Difficulty: Easy
# Use slicing to extract and transform data.
def slice_operations(items: list[int]) -> dict[str, list[int]]:
    """Perform various slice operations on the list.

    Return a dict with:
    - 'first_three': first 3 elements
    - 'last_three': last 3 elements
    - 'reversed': the list reversed (using slicing)
    - 'every_other': every other element starting from index 0
    - 'middle': everything except first and last element

    >>> slice_operations([1, 2, 3, 4, 5, 6, 7])
    {'first_three': [1, 2, 3], 'last_three': [5, 6, 7], 'reversed': [7, 6, 5, 4, 3, 2, 1], 'every_other': [1, 3, 5, 7], 'middle': [2, 3, 4, 5, 6]}
    """
    pass


# Exercise 3: Tuple Unpacking
# Difficulty: Easy
# Use tuple unpacking to extract data.
def unpack_coordinates(points: list[tuple[float, float]]) -> dict[str, float]:
    """Calculate statistics from a list of (x, y) coordinate tuples.

    Return a dict with:
    - 'min_x': minimum x coordinate
    - 'max_x': maximum x coordinate
    - 'min_y': minimum y coordinate
    - 'max_y': maximum y coordinate
    - 'avg_x': average x coordinate
    - 'avg_y': average y coordinate

    Use unpacking in your iteration.

    >>> unpack_coordinates([(1, 2), (3, 4), (5, 6)])
    {'min_x': 1, 'max_x': 5, 'min_y': 2, 'max_y': 6, 'avg_x': 3.0, 'avg_y': 4.0}
    """
    pass


# =============================================================================
# CORE: Dict, Set, and Collection Operations
# =============================================================================

# Exercise 4: Word Frequency Counter
# Difficulty: Medium
# Count word frequencies in a string.
def word_frequency(text: str) -> list[tuple[str, int]]:
    """Count word frequencies and return the top results.

    - Convert all words to lowercase
    - Split by whitespace
    - Return a list of (word, count) tuples sorted by count descending,
      then alphabetically for ties
    - Only include words that appear more than once

    >>> word_frequency("the cat sat on the mat the cat")
    [('the', 3), ('cat', 2)]
    >>> word_frequency("all unique words here")
    []
    """
    pass


# Exercise 5: Set Operations
# Difficulty: Medium
# Use set operations to analyze student enrollment.
def analyze_enrollment(
    math_students: set[str],
    science_students: set[str],
    english_students: set[str],
) -> dict[str, set[str]]:
    """Analyze student enrollment across three classes.

    Return a dict with:
    - 'all_students': everyone enrolled in at least one class
    - 'all_three': students in all three classes
    - 'math_only': students ONLY in math (not in science or english)
    - 'math_and_science': students in both math and science (regardless of english)
    - 'exactly_two': students in exactly two classes (not one, not three)

    >>> math = {"Alice", "Bob", "Charlie", "Diana"}
    >>> science = {"Bob", "Charlie", "Eve"}
    >>> english = {"Charlie", "Diana", "Eve", "Frank"}
    >>> result = analyze_enrollment(math, science, english)
    >>> result['all_three']
    {'Charlie'}
    >>> result['math_only']
    {'Alice'}
    """
    pass


# Exercise 6: Dict Merge and Transform
# Difficulty: Medium
# Merge and transform multiple dictionaries.
def merge_configs(*configs: dict[str, object]) -> dict[str, object]:
    """Merge multiple config dicts with later dicts taking priority.

    Rules:
    - Later dicts override earlier ones for the same key
    - If both values are dicts, merge them recursively
    - If both values are lists, concatenate them
    - Otherwise, later value wins

    >>> merge_configs({"a": 1}, {"b": 2}, {"a": 3})
    {'a': 3, 'b': 2}
    >>> merge_configs({"a": [1]}, {"a": [2, 3]})
    {'a': [1, 2, 3]}
    >>> merge_configs({"a": {"x": 1}}, {"a": {"y": 2}})
    {'a': {'x': 1, 'y': 2}}
    >>> merge_configs({"a": {"x": 1}}, {"a": 5})
    {'a': 5}
    """
    pass


# Exercise 7: Grouping with defaultdict
# Difficulty: Medium
# Group items by a computed key using defaultdict.
def group_by_length(words: list[str]) -> dict[int, list[str]]:
    """Group words by their length, sorted alphabetically within each group.

    Return a regular dict (not defaultdict) with integer keys (lengths)
    and sorted list values.

    >>> group_by_length(["cat", "dog", "elephant", "ant", "bee", "ox"])
    {3: ['ant', 'bee', 'cat', 'dog'], 8: ['elephant'], 2: ['ox']}
    """
    pass


# Exercise 8: Counter Arithmetic
# Difficulty: Medium
# Use Counter for inventory management.
def inventory_check(
    stock: dict[str, int],
    orders: list[dict[str, int]],
) -> dict[str, object]:
    """Check inventory against orders using Counter.

    - stock: current inventory as {item: quantity}
    - orders: list of order dicts, each {item: quantity}

    Return a dict with:
    - 'total_ordered': Counter of total items ordered across all orders
    - 'remaining': dict of remaining stock (items with 0 or negative should show 0)
    - 'can_fulfill': True if stock can fulfill ALL orders combined
    - 'shortage': dict of items with shortages and how many are short (only items short)

    >>> stock = {"apple": 10, "banana": 5, "cherry": 3}
    >>> orders = [{"apple": 3, "banana": 2}, {"apple": 5, "cherry": 4}]
    >>> result = inventory_check(stock, orders)
    >>> result['total_ordered']
    Counter({'apple': 8, 'cherry': 4, 'banana': 2})
    >>> result['can_fulfill']
    False
    >>> result['shortage']
    {'cherry': 1}
    """
    pass


# =============================================================================
# CHALLENGE: Advanced Patterns
# =============================================================================

# Exercise 9: Named Tuple Records
# Difficulty: Medium
# Use NamedTuple to create structured records.
class Student(NamedTuple):
    """A student record."""
    name: str
    grade: int
    gpa: float


def process_students(data: list[tuple[str, int, float]]) -> dict[str, object]:
    """Convert raw tuples to Student NamedTuples and analyze.

    Return a dict with:
    - 'students': list of Student NamedTuples (sorted by GPA descending)
    - 'honor_roll': list of names with GPA >= 3.5 (sorted by GPA descending)
    - 'by_grade': dict mapping grade (int) to list of names (sorted alpha)
    - 'top_student': name of student with highest GPA

    >>> data = [("Alice", 10, 3.8), ("Bob", 10, 3.2), ("Charlie", 11, 3.9), ("Diana", 11, 3.5)]
    >>> result = process_students(data)
    >>> result['top_student']
    'Charlie'
    >>> result['honor_roll']
    ['Charlie', 'Alice', 'Diana']
    >>> result['by_grade']
    {10: ['Alice', 'Bob'], 11: ['Charlie', 'Diana']}
    """
    pass


# Exercise 10: Deque as Sliding Window
# Difficulty: Hard
# Use deque to implement a sliding window maximum.
def sliding_window_max(numbers: list[int], window_size: int) -> list[int]:
    """Find the maximum value in each sliding window of the given size.

    Use collections.deque to implement this efficiently.

    >>> sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)
    [3, 3, 5, 5, 6, 7]
    >>> sliding_window_max([1, 2, 3, 4, 5], 2)
    [2, 3, 4, 5]
    >>> sliding_window_max([5, 4, 3, 2, 1], 3)
    [5, 4, 3]
    """
    pass


# Exercise 11: Deep Flatten
# Difficulty: Hard
# Flatten a deeply nested list structure.
def deep_flatten(nested: list) -> list:
    """Recursively flatten a nested list of arbitrary depth.

    >>> deep_flatten([1, [2, [3, [4]], 5], 6])
    [1, 2, 3, 4, 5, 6]
    >>> deep_flatten([[1, 2], [3, [4, [5, [6]]]]])
    [1, 2, 3, 4, 5, 6]
    >>> deep_flatten([1, 2, 3])
    [1, 2, 3]
    >>> deep_flatten([])
    []
    """
    pass


# Exercise 12: Matrix Operations with Lists
# Difficulty: Hard
# Perform matrix operations using nested lists.
def matrix_ops(matrix: list[list[int]]) -> dict[str, object]:
    """Perform various operations on a matrix (list of lists).

    Return a dict with:
    - 'transposed': the transposed matrix
    - 'flattened': the matrix flattened to a single list
    - 'row_sums': list of sums for each row
    - 'col_sums': list of sums for each column
    - 'diagonal': list of diagonal elements (top-left to bottom-right)
                  (only for square matrices; empty list if not square)

    >>> matrix_ops([[1, 2, 3], [4, 5, 6]])
    {'transposed': [[1, 4], [2, 5], [3, 6]], 'flattened': [1, 2, 3, 4, 5, 6], 'row_sums': [6, 15], 'col_sums': [5, 7, 9], 'diagonal': []}
    >>> matrix_ops([[1, 2], [3, 4]])['diagonal']
    [1, 4]
    """
    pass


# =============================================================================
# SWIFT BRIDGE: Data Structure Translation
# =============================================================================

# Exercise 13: Swift-Style Stack
# Difficulty: Medium
# Implement a stack with Python list, mimicking Swift's Array-based stack.
class Stack:
    """A stack data structure using a Python list.

    Swift equivalent:
        struct Stack<Element> {
            private var items = [Element]()
            mutating func push(_ item: Element) { items.append(item) }
            mutating func pop() -> Element? { items.popLast() }
            var peek: Element? { items.last }
            var isEmpty: Bool { items.isEmpty }
            var count: Int { items.count }
        }

    >>> s = Stack()
    >>> s.push(1)
    >>> s.push(2)
    >>> s.push(3)
    >>> s.peek
    3
    >>> s.pop()
    3
    >>> len(s)
    2
    >>> bool(s)
    True
    >>> s.pop()
    2
    >>> s.pop()
    1
    >>> s.pop() is None
    True
    >>> bool(s)
    False
    """

    def __init__(self) -> None:
        """Initialize an empty stack."""
        ...

    def push(self, item: object) -> None:
        """Push an item onto the stack."""
        ...

    def pop(self) -> object | None:
        """Pop and return the top item, or None if empty."""
        ...

    @property
    def peek(self) -> object | None:
        """Return the top item without removing it, or None if empty."""
        ...

    def __len__(self) -> int:
        """Return the number of items in the stack."""
        ...

    def __bool__(self) -> bool:
        """Return True if the stack is non-empty."""
        ...


# Exercise 14: Frequency Analysis Pipeline
# Difficulty: Hard
# Combine multiple data structures for text analysis.
def frequency_analysis(text: str) -> dict[str, object]:
    """Perform comprehensive frequency analysis on text.

    Return a dict with:
    - 'char_freq': Counter of character frequencies (lowercase, letters only)
    - 'word_freq': Counter of word frequencies (lowercase)
    - 'unique_words': set of unique words (lowercase)
    - 'most_common_char': the most common letter (lowercase)
    - 'most_common_word': the most common word (lowercase)
    - 'char_to_words': defaultdict mapping each letter to the set of words
                       containing that letter (all lowercase)

    >>> result = frequency_analysis("The cat sat on the mat")
    >>> result['most_common_word']
    'the'
    >>> result['most_common_char']
    't'
    >>> result['unique_words']
    {'the', 'cat', 'sat', 'on', 'mat'}
    >>> 'cat' in result['char_to_words']['c']
    True
    """
    pass


# Exercise 15: Data Pipeline with Unpacking
# Difficulty: Hard
# Process structured data using unpacking and multiple data structures.
def process_transactions(
    transactions: list[tuple[str, str, float]],
) -> dict[str, object]:
    """Process a list of (date, category, amount) transaction tuples.

    Return a dict with:
    - 'total': total of all amounts (rounded to 2 decimal places)
    - 'by_category': dict mapping category -> total amount (rounded to 2 dp)
    - 'by_date': dict mapping date -> list of (category, amount) tuples
    - 'largest': the single largest transaction as a dict with keys
                 'date', 'category', 'amount'
    - 'categories': sorted list of unique categories
    - 'daily_totals': dict mapping date -> total amount (rounded to 2 dp),
                      sorted by date

    >>> txns = [
    ...     ("2024-01-01", "food", 25.50),
    ...     ("2024-01-01", "transport", 12.00),
    ...     ("2024-01-02", "food", 30.00),
    ...     ("2024-01-02", "entertainment", 45.00),
    ... ]
    >>> result = process_transactions(txns)
    >>> result['total']
    112.5
    >>> result['by_category']
    {'food': 55.5, 'transport': 12.0, 'entertainment': 45.0}
    >>> result['largest']
    {'date': '2024-01-02', 'category': 'entertainment', 'amount': 45.0}
    >>> result['categories']
    ['entertainment', 'food', 'transport']
    """
    pass


# =============================================================================
# Self-Test Runner
# =============================================================================

if __name__ == "__main__":
    print("Running Module 03 Exercises...\n")
    errors = 0

    # Exercise 1
    try:
        result = list_operations([3, 1, 4, 1, 5])
        assert result == {
            "result": [99, 5, 4, 3, 1, 1, 0],
            "length": 7,
            "first": 99,
            "last": 0,
            "sum": 113,
        }
        # Verify original is not modified
        original = [1, 2, 3]
        list_operations(original)
        assert original == [1, 2, 3], "Original list was modified!"
        print("  Exercise  1 (list_operations):       PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  1 (list_operations):       FAIL - {e}")
        errors += 1

    # Exercise 2
    try:
        result = slice_operations([1, 2, 3, 4, 5, 6, 7])
        assert result["first_three"] == [1, 2, 3]
        assert result["last_three"] == [5, 6, 7]
        assert result["reversed"] == [7, 6, 5, 4, 3, 2, 1]
        assert result["every_other"] == [1, 3, 5, 7]
        assert result["middle"] == [2, 3, 4, 5, 6]
        print("  Exercise  2 (slice_operations):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  2 (slice_operations):      FAIL - {e}")
        errors += 1

    # Exercise 3
    try:
        result = unpack_coordinates([(1, 2), (3, 4), (5, 6)])
        assert result == {
            "min_x": 1, "max_x": 5,
            "min_y": 2, "max_y": 6,
            "avg_x": 3.0, "avg_y": 4.0,
        }
        print("  Exercise  3 (unpack_coordinates):    PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  3 (unpack_coordinates):    FAIL - {e}")
        errors += 1

    # Exercise 4
    try:
        assert word_frequency("the cat sat on the mat the cat") == [("the", 3), ("cat", 2)]
        assert word_frequency("all unique words here") == []
        assert word_frequency("a a b b c") == [("a", 2), ("b", 2)]
        print("  Exercise  4 (word_frequency):        PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  4 (word_frequency):        FAIL - {e}")
        errors += 1

    # Exercise 5
    try:
        math = {"Alice", "Bob", "Charlie", "Diana"}
        science = {"Bob", "Charlie", "Eve"}
        english = {"Charlie", "Diana", "Eve", "Frank"}
        result = analyze_enrollment(math, science, english)
        assert result["all_students"] == {"Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"}
        assert result["all_three"] == {"Charlie"}
        assert result["math_only"] == {"Alice"}
        assert result["math_and_science"] == {"Bob", "Charlie"}
        assert result["exactly_two"] == {"Bob", "Diana", "Eve"}
        print("  Exercise  5 (analyze_enrollment):    PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  5 (analyze_enrollment):    FAIL - {e}")
        errors += 1

    # Exercise 6
    try:
        assert merge_configs({"a": 1}, {"b": 2}, {"a": 3}) == {"a": 3, "b": 2}
        assert merge_configs({"a": [1]}, {"a": [2, 3]}) == {"a": [1, 2, 3]}
        assert merge_configs({"a": {"x": 1}}, {"a": {"y": 2}}) == {"a": {"x": 1, "y": 2}}
        assert merge_configs({"a": {"x": 1}}, {"a": 5}) == {"a": 5}
        print("  Exercise  6 (merge_configs):         PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  6 (merge_configs):         FAIL - {e}")
        errors += 1

    # Exercise 7
    try:
        result = group_by_length(["cat", "dog", "elephant", "ant", "bee", "ox"])
        assert result == {3: ["ant", "bee", "cat", "dog"], 8: ["elephant"], 2: ["ox"]}
        print("  Exercise  7 (group_by_length):       PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  7 (group_by_length):       FAIL - {e}")
        errors += 1

    # Exercise 8
    try:
        stock = {"apple": 10, "banana": 5, "cherry": 3}
        orders = [{"apple": 3, "banana": 2}, {"apple": 5, "cherry": 4}]
        result = inventory_check(stock, orders)
        assert result["total_ordered"] == Counter({"apple": 8, "cherry": 4, "banana": 2})
        assert result["can_fulfill"] is False
        assert result["shortage"] == {"cherry": 1}
        assert result["remaining"] == {"apple": 2, "banana": 3, "cherry": 0}
        print("  Exercise  8 (inventory_check):       PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  8 (inventory_check):       FAIL - {e}")
        errors += 1

    # Exercise 9
    try:
        data = [("Alice", 10, 3.8), ("Bob", 10, 3.2), ("Charlie", 11, 3.9), ("Diana", 11, 3.5)]
        result = process_students(data)
        assert result["top_student"] == "Charlie"
        assert result["honor_roll"] == ["Charlie", "Alice", "Diana"]
        assert result["by_grade"] == {10: ["Alice", "Bob"], 11: ["Charlie", "Diana"]}
        assert all(isinstance(s, Student) for s in result["students"])
        print("  Exercise  9 (process_students):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  9 (process_students):      FAIL - {e}")
        errors += 1

    # Exercise 10
    try:
        assert sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
        assert sliding_window_max([1, 2, 3, 4, 5], 2) == [2, 3, 4, 5]
        assert sliding_window_max([5, 4, 3, 2, 1], 3) == [5, 4, 3]
        assert sliding_window_max([1], 1) == [1]
        print("  Exercise 10 (sliding_window_max):    PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 10 (sliding_window_max):    FAIL - {e}")
        errors += 1

    # Exercise 11
    try:
        assert deep_flatten([1, [2, [3, [4]], 5], 6]) == [1, 2, 3, 4, 5, 6]
        assert deep_flatten([[1, 2], [3, [4, [5, [6]]]]]) == [1, 2, 3, 4, 5, 6]
        assert deep_flatten([1, 2, 3]) == [1, 2, 3]
        assert deep_flatten([]) == []
        assert deep_flatten([[], [[]], [[], []]]) == []
        print("  Exercise 11 (deep_flatten):          PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 11 (deep_flatten):          FAIL - {e}")
        errors += 1

    # Exercise 12
    try:
        result = matrix_ops([[1, 2, 3], [4, 5, 6]])
        assert result["transposed"] == [[1, 4], [2, 5], [3, 6]]
        assert result["flattened"] == [1, 2, 3, 4, 5, 6]
        assert result["row_sums"] == [6, 15]
        assert result["col_sums"] == [5, 7, 9]
        assert result["diagonal"] == []

        result2 = matrix_ops([[1, 2], [3, 4]])
        assert result2["diagonal"] == [1, 4]
        print("  Exercise 12 (matrix_ops):            PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 12 (matrix_ops):            FAIL - {e}")
        errors += 1

    # Exercise 13
    try:
        s = Stack()
        assert len(s) == 0
        assert not s
        s.push(1)
        s.push(2)
        s.push(3)
        assert s.peek == 3
        assert len(s) == 3
        assert bool(s)
        assert s.pop() == 3
        assert s.pop() == 2
        assert s.pop() == 1
        assert s.pop() is None
        assert not s
        print("  Exercise 13 (Stack):                 PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 13 (Stack):                 FAIL - {e}")
        errors += 1

    # Exercise 14
    try:
        result = frequency_analysis("The cat sat on the mat")
        assert result["most_common_word"] == "the"
        assert result["most_common_char"] == "t"
        assert result["unique_words"] == {"the", "cat", "sat", "on", "mat"}
        assert "cat" in result["char_to_words"]["c"]
        assert "cat" in result["char_to_words"]["a"]
        assert isinstance(result["char_freq"], Counter)
        print("  Exercise 14 (frequency_analysis):    PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 14 (frequency_analysis):    FAIL - {e}")
        errors += 1

    # Exercise 15
    try:
        txns = [
            ("2024-01-01", "food", 25.50),
            ("2024-01-01", "transport", 12.00),
            ("2024-01-02", "food", 30.00),
            ("2024-01-02", "entertainment", 45.00),
        ]
        result = process_transactions(txns)
        assert result["total"] == 112.5
        assert result["by_category"] == {
            "food": 55.5, "transport": 12.0, "entertainment": 45.0
        }
        assert result["largest"] == {
            "date": "2024-01-02", "category": "entertainment", "amount": 45.0
        }
        assert result["categories"] == ["entertainment", "food", "transport"]
        assert result["daily_totals"] == {"2024-01-01": 37.5, "2024-01-02": 75.0}
        assert result["by_date"]["2024-01-01"] == [("food", 25.50), ("transport", 12.00)]
        print("  Exercise 15 (process_transactions):  PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 15 (process_transactions):  FAIL - {e}")
        errors += 1

    print(f"\n{'='*50}")
    if errors == 0:
        print("All exercises passed!")
    else:
        print(f"{errors} exercise(s) need attention.")
    print(f"{'='*50}")
