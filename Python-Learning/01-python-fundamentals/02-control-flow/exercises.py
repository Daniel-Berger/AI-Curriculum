"""
Module 02: Control Flow - Exercises
====================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` or `...` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- Focus on writing Pythonic code (comprehensions, walrus operator, etc.).

Difficulty levels:
  Easy   - Direct translation from Swift concepts
  Medium - Requires understanding Python-specific idioms
  Hard   - Combines multiple concepts or requires Pythonic thinking
"""


# =============================================================================
# WARM-UP: Conditionals and Basic Loops
# =============================================================================

# Exercise 1: FizzBuzz
# Difficulty: Easy
# The classic FizzBuzz problem using if/elif/else.
def fizzbuzz(n: int) -> list[str]:
    """Return a list of strings for numbers 1 to n.

    For multiples of 3: "Fizz"
    For multiples of 5: "Buzz"
    For multiples of both 3 and 5: "FizzBuzz"
    Otherwise: the number as a string

    >>> fizzbuzz(5)
    ['1', '2', 'Fizz', '4', 'Buzz']
    >>> fizzbuzz(15)[-1]
    'FizzBuzz'
    """
    pass


# Exercise 2: Ternary Classifier
# Difficulty: Easy
# Use Python's ternary expression (not if/elif/else blocks).
def classify_number(n: int) -> str:
    """Classify a number as 'positive', 'negative', or 'zero'.

    Must be implemented as a single return statement using ternary expressions.

    >>> classify_number(5)
    'positive'
    >>> classify_number(-3)
    'negative'
    >>> classify_number(0)
    'zero'
    """
    pass


# Exercise 3: Early Return Pattern
# Difficulty: Easy
# Implement the Python equivalent of Swift's guard statement.
def validate_password(password: str) -> tuple[bool, str]:
    """Validate a password and return (is_valid, message).

    Rules (check in this order, return on first failure):
    1. Must be at least 8 characters: "Too short"
    2. Must contain at least one digit: "No digit"
    3. Must contain at least one uppercase letter: "No uppercase"
    4. If all pass: return (True, "Valid")

    >>> validate_password("short")
    (False, 'Too short')
    >>> validate_password("longpassword")
    (False, 'No digit')
    >>> validate_password("longpassword1")
    (False, 'No uppercase')
    >>> validate_password("LongPassword1")
    (True, 'Valid')
    """
    pass


# =============================================================================
# CORE: Comprehensions
# =============================================================================

# Exercise 4: List Comprehension Basics
# Difficulty: Medium
# Create various lists using comprehensions (no loops allowed).
def comprehension_basics() -> dict[str, list]:
    """Return a dict with the following keys and their list values:

    'squares':     squares of 0-9 (i.e., [0, 1, 4, 9, ...])
    'even_squares': squares of even numbers 0-9
    'words_upper': ['HELLO', 'WORLD', 'PYTHON'] from ['hello', 'world', 'python']
    'lengths':     lengths of ['cat', 'elephant', 'dog', 'hippopotamus']

    All values MUST be created using list comprehensions.

    >>> result = comprehension_basics()
    >>> result['squares']
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    >>> result['even_squares']
    [0, 4, 16, 36, 64]
    >>> result['words_upper']
    ['HELLO', 'WORLD', 'PYTHON']
    """
    pass


# Exercise 5: Dict Comprehension
# Difficulty: Medium
# Transform data using dict comprehensions.
def invert_and_filter(d: dict[str, int], min_value: int = 0) -> dict[int, str]:
    """Invert a dict (swap keys/values), keeping only entries where
    the original value is >= min_value.

    >>> invert_and_filter({"a": 1, "b": 2, "c": 3}, min_value=2)
    {2: 'b', 3: 'c'}
    >>> invert_and_filter({"x": 10, "y": 20}, min_value=0)
    {10: 'x', 20: 'y'}
    """
    pass


# Exercise 6: Nested Comprehension -- Matrix Transpose
# Difficulty: Medium
# Transpose a matrix using nested comprehensions.
def transpose(matrix: list[list[int]]) -> list[list[int]]:
    """Transpose a matrix (rows become columns).

    Must use a list comprehension (not loops).

    >>> transpose([[1, 2, 3], [4, 5, 6]])
    [[1, 4], [2, 5], [3, 6]]
    >>> transpose([[1, 2], [3, 4], [5, 6]])
    [[1, 3, 5], [2, 4, 6]]
    """
    pass


# Exercise 7: Set Comprehension -- Unique Word Lengths
# Difficulty: Easy
# Find all unique word lengths in a sentence using a set comprehension.
def unique_word_lengths(sentence: str) -> set[int]:
    """Return the set of unique word lengths in the sentence.

    Words are split by whitespace. Use a set comprehension.

    >>> unique_word_lengths("the quick brown fox jumps")
    {3, 4, 5}
    >>> unique_word_lengths("I am a student")
    {1, 2, 7}
    """
    pass


# =============================================================================
# CORE: Iteration Patterns
# =============================================================================

# Exercise 8: Enumerate and Zip
# Difficulty: Medium
# Use enumerate and zip to merge and annotate data.
def merge_with_index(names: list[str], scores: list[int]) -> list[str]:
    """Merge names and scores into indexed strings.

    Use zip and enumerate together. Format: "{index}. {name}: {score}"
    Index starts at 1.

    If lists have different lengths, only include entries where both exist.

    >>> merge_with_index(["Alice", "Bob"], [95, 87])
    ['1. Alice: 95', '2. Bob: 87']
    >>> merge_with_index(["Alice", "Bob", "Charlie"], [95, 87])
    ['1. Alice: 95', '2. Bob: 87']
    """
    pass


# Exercise 9: For-Else Pattern
# Difficulty: Medium
# Use Python's for-else to search for a value.
def find_first_negative(numbers: list[int]) -> str:
    """Find the first negative number in the list.

    Use a for-else loop (not any(), not a flag variable).
    If found: return "Found {number} at index {index}"
    If not found: return "All positive"

    >>> find_first_negative([1, 2, -3, 4])
    'Found -3 at index 2'
    >>> find_first_negative([1, 2, 3, 4])
    'All positive'
    >>> find_first_negative([-1, 2, 3])
    'Found -1 at index 0'
    """
    pass


# Exercise 10: Generator Expression
# Difficulty: Medium
# Use generator expressions with sum(), any(), all().
def analyze_numbers(numbers: list[int]) -> dict[str, object]:
    """Analyze a list of numbers using generator expressions.

    Return a dict with:
    - 'sum_of_squares': sum of each number squared
    - 'has_negative': True if any number is negative
    - 'all_even': True if all numbers are even
    - 'count_positive': count of positive numbers

    Use generator expressions (not list comprehensions) for each.

    >>> analyze_numbers([1, -2, 3, -4])
    {'sum_of_squares': 30, 'has_negative': True, 'all_even': False, 'count_positive': 2}
    >>> analyze_numbers([2, 4, 6])
    {'sum_of_squares': 56, 'has_negative': False, 'all_even': True, 'count_positive': 3}
    """
    pass


# =============================================================================
# CHALLENGE: Match/Case, Walrus Operator, Advanced Patterns
# =============================================================================

# Exercise 11: Match/Case with Patterns
# Difficulty: Hard
# Use match/case for structural pattern matching (Python 3.10+).
def describe_shape(shape: tuple) -> str:
    """Describe a shape based on its tuple structure using match/case.

    Pattern matching rules:
    - () -> "empty"
    - (r,) where r > 0 -> "circle with radius {r}"
    - (w, h) where w == h and w > 0 -> "square with side {w}"
    - (w, h) where w > 0 and h > 0 -> "rectangle {w}x{h}"
    - (a, b, c) where all > 0 -> "triangle with sides {a}, {b}, {c}"
    - anything else -> "unknown shape"

    >>> describe_shape((5,))
    'circle with radius 5'
    >>> describe_shape((3, 3))
    'square with side 3'
    >>> describe_shape((4, 6))
    'rectangle 4x6'
    >>> describe_shape((3, 4, 5))
    'triangle with sides 3, 4, 5'
    >>> describe_shape(())
    'empty'
    >>> describe_shape((0, 5))
    'unknown shape'
    """
    pass


# Exercise 12: Match/Case with Dict Patterns
# Difficulty: Hard
# Use match/case to process event dictionaries.
def process_event(event: dict) -> str:
    """Process an event dict using match/case.

    Expected patterns:
    - {"type": "click", "x": x, "y": y} -> "Click at ({x}, {y})"
    - {"type": "keypress", "key": key, "modifiers": [mod, *_]} ->
        "Key '{key}' with modifier '{mod}'"
    - {"type": "keypress", "key": key} -> "Key '{key}'"
    - {"type": "scroll", "direction": "up" | "down" as d} ->
        "Scroll {d}"
    - {"type": t} -> "Unknown event: {t}"
    - anything else -> "Invalid event"

    >>> process_event({"type": "click", "x": 100, "y": 200})
    'Click at (100, 200)'
    >>> process_event({"type": "keypress", "key": "a"})
    "Key 'a'"
    >>> process_event({"type": "keypress", "key": "a", "modifiers": ["ctrl", "shift"]})
    "Key 'a' with modifier 'ctrl'"
    >>> process_event({"type": "scroll", "direction": "up"})
    'Scroll up'
    >>> process_event({"type": "resize"})
    'Unknown event: resize'
    >>> process_event("not a dict")
    'Invalid event'
    """
    pass


# Exercise 13: Walrus Operator
# Difficulty: Hard
# Use the walrus operator (:=) in practical scenarios.
def filter_long_words(text: str, min_length: int = 5) -> list[tuple[str, int]]:
    """Find words meeting minimum length, returning word and its length.

    Use the walrus operator to compute len() once per word.
    Return list of (word_lowercase, length) tuples, sorted by length descending.

    >>> filter_long_words("The quick brown fox jumps over the lazy dog", 4)
    [('quick', 5), ('brown', 5), ('jumps', 5), ('over', 4), ('lazy', 4)]
    >>> filter_long_words("Hi there", 3)
    [('there', 5)]
    """
    pass


# Exercise 14: Comprehension Pipeline
# Difficulty: Hard
# Chain multiple comprehension operations to process data.
def process_student_scores(
    students: list[dict[str, object]],
) -> dict[str, str]:
    """Process student records and return grade assignments.

    Each student dict has keys: 'name' (str) and 'scores' (list[int]).

    Steps:
    1. Calculate average score for each student
    2. Assign grade: A (>=90), B (>=80), C (>=70), D (>=60), F (<60)
    3. Return dict mapping name -> grade
    4. Only include students with non-empty scores lists

    Use comprehensions where possible.

    >>> students = [
    ...     {"name": "Alice", "scores": [95, 87, 92]},
    ...     {"name": "Bob", "scores": [65, 70, 55]},
    ...     {"name": "Charlie", "scores": [88, 82, 90]},
    ...     {"name": "Diana", "scores": []},
    ... ]
    >>> process_student_scores(students)
    {'Alice': 'A', 'Bob': 'D', 'Charlie': 'B'}
    """
    pass


# =============================================================================
# SWIFT BRIDGE: Rewrite Swift Control Flow in Python
# =============================================================================

# Exercise 15: Swift-Style Higher-Order Functions
# Difficulty: Medium
# Rewrite Swift's map/filter/reduce chain using Python idioms.
#
# Swift code:
#     let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#     let result = numbers
#         .filter { $0 % 2 == 0 }         // even numbers
#         .map { $0 * $0 }                 // square them
#         .reduce(0, +)                    // sum them
def sum_of_even_squares(numbers: list[int]) -> int:
    """Filter even numbers, square them, and sum the result.

    Use Pythonic constructs (comprehensions and/or built-in functions).

    >>> sum_of_even_squares([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    220
    >>> sum_of_even_squares([1, 3, 5])
    0
    >>> sum_of_even_squares([2, 4])
    20
    """
    pass


# =============================================================================
# Self-Test Runner
# =============================================================================

if __name__ == "__main__":
    print("Running Module 02 Exercises...\n")
    errors = 0

    # Exercise 1
    try:
        assert fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]
        assert fizzbuzz(15)[-1] == "FizzBuzz"
        assert fizzbuzz(3) == ["1", "2", "Fizz"]
        assert len(fizzbuzz(15)) == 15
        print("  Exercise  1 (fizzbuzz):              PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  1 (fizzbuzz):              FAIL - {e}")
        errors += 1

    # Exercise 2
    try:
        assert classify_number(5) == "positive"
        assert classify_number(-3) == "negative"
        assert classify_number(0) == "zero"
        print("  Exercise  2 (classify_number):       PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  2 (classify_number):       FAIL - {e}")
        errors += 1

    # Exercise 3
    try:
        assert validate_password("short") == (False, "Too short")
        assert validate_password("longpassword") == (False, "No digit")
        assert validate_password("longpassword1") == (False, "No uppercase")
        assert validate_password("LongPassword1") == (True, "Valid")
        print("  Exercise  3 (validate_password):     PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  3 (validate_password):     FAIL - {e}")
        errors += 1

    # Exercise 4
    try:
        result = comprehension_basics()
        assert result["squares"] == [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
        assert result["even_squares"] == [0, 4, 16, 36, 64]
        assert result["words_upper"] == ["HELLO", "WORLD", "PYTHON"]
        assert result["lengths"] == [3, 8, 3, 12]
        print("  Exercise  4 (comprehension_basics):  PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  4 (comprehension_basics):  FAIL - {e}")
        errors += 1

    # Exercise 5
    try:
        assert invert_and_filter({"a": 1, "b": 2, "c": 3}, min_value=2) == {2: "b", 3: "c"}
        assert invert_and_filter({"x": 10, "y": 20}, min_value=0) == {10: "x", 20: "y"}
        assert invert_and_filter({"a": 1}, min_value=5) == {}
        print("  Exercise  5 (invert_and_filter):     PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  5 (invert_and_filter):     FAIL - {e}")
        errors += 1

    # Exercise 6
    try:
        assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
        assert transpose([[1, 2], [3, 4], [5, 6]]) == [[1, 3, 5], [2, 4, 6]]
        assert transpose([[1]]) == [[1]]
        print("  Exercise  6 (transpose):             PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  6 (transpose):             FAIL - {e}")
        errors += 1

    # Exercise 7
    try:
        assert unique_word_lengths("the quick brown fox jumps") == {3, 4, 5}
        assert unique_word_lengths("I am a student") == {1, 2, 7}
        print("  Exercise  7 (unique_word_lengths):   PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  7 (unique_word_lengths):   FAIL - {e}")
        errors += 1

    # Exercise 8
    try:
        assert merge_with_index(["Alice", "Bob"], [95, 87]) == [
            "1. Alice: 95", "2. Bob: 87"
        ]
        assert merge_with_index(["Alice", "Bob", "Charlie"], [95, 87]) == [
            "1. Alice: 95", "2. Bob: 87"
        ]
        print("  Exercise  8 (merge_with_index):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  8 (merge_with_index):      FAIL - {e}")
        errors += 1

    # Exercise 9
    try:
        assert find_first_negative([1, 2, -3, 4]) == "Found -3 at index 2"
        assert find_first_negative([1, 2, 3, 4]) == "All positive"
        assert find_first_negative([-1, 2, 3]) == "Found -1 at index 0"
        print("  Exercise  9 (find_first_negative):   PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  9 (find_first_negative):   FAIL - {e}")
        errors += 1

    # Exercise 10
    try:
        result = analyze_numbers([1, -2, 3, -4])
        assert result["sum_of_squares"] == 30
        assert result["has_negative"] is True
        assert result["all_even"] is False
        assert result["count_positive"] == 2

        result2 = analyze_numbers([2, 4, 6])
        assert result2["sum_of_squares"] == 56
        assert result2["has_negative"] is False
        assert result2["all_even"] is True
        assert result2["count_positive"] == 3
        print("  Exercise 10 (analyze_numbers):       PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 10 (analyze_numbers):       FAIL - {e}")
        errors += 1

    # Exercise 11
    try:
        assert describe_shape((5,)) == "circle with radius 5"
        assert describe_shape((3, 3)) == "square with side 3"
        assert describe_shape((4, 6)) == "rectangle 4x6"
        assert describe_shape((3, 4, 5)) == "triangle with sides 3, 4, 5"
        assert describe_shape(()) == "empty"
        assert describe_shape((0, 5)) == "unknown shape"
        assert describe_shape((-1,)) == "unknown shape"
        print("  Exercise 11 (describe_shape):        PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 11 (describe_shape):        FAIL - {e}")
        errors += 1

    # Exercise 12
    try:
        assert process_event({"type": "click", "x": 100, "y": 200}) == "Click at (100, 200)"
        assert process_event({"type": "keypress", "key": "a"}) == "Key 'a'"
        assert process_event({"type": "keypress", "key": "a", "modifiers": ["ctrl", "shift"]}) == "Key 'a' with modifier 'ctrl'"
        assert process_event({"type": "scroll", "direction": "up"}) == "Scroll up"
        assert process_event({"type": "resize"}) == "Unknown event: resize"
        assert process_event("not a dict") == "Invalid event"
        print("  Exercise 12 (process_event):         PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 12 (process_event):         FAIL - {e}")
        errors += 1

    # Exercise 13
    try:
        result = filter_long_words("The quick brown fox jumps over the lazy dog", 4)
        assert result == [("quick", 5), ("brown", 5), ("jumps", 5), ("over", 4), ("lazy", 4)]
        assert filter_long_words("Hi there", 3) == [("there", 5)]
        print("  Exercise 13 (filter_long_words):     PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 13 (filter_long_words):     FAIL - {e}")
        errors += 1

    # Exercise 14
    try:
        students = [
            {"name": "Alice", "scores": [95, 87, 92]},
            {"name": "Bob", "scores": [65, 70, 55]},
            {"name": "Charlie", "scores": [88, 82, 90]},
            {"name": "Diana", "scores": []},
        ]
        result = process_student_scores(students)
        assert result == {"Alice": "A", "Bob": "D", "Charlie": "B"}
        print("  Exercise 14 (process_student_scores): PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 14 (process_student_scores): FAIL - {e}")
        errors += 1

    # Exercise 15
    try:
        assert sum_of_even_squares([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 220
        assert sum_of_even_squares([1, 3, 5]) == 0
        assert sum_of_even_squares([2, 4]) == 20
        print("  Exercise 15 (sum_of_even_squares):   PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 15 (sum_of_even_squares):   FAIL - {e}")
        errors += 1

    print(f"\n{'='*50}")
    if errors == 0:
        print("All exercises passed!")
    else:
        print(f"{errors} exercise(s) need attention.")
    print(f"{'='*50}")
