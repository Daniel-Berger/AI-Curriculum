"""
Module 02: Control Flow - Solutions
====================================
Complete solutions for all exercises with Pythonic alternatives and notes.

Run this file to verify all solutions pass: `python solutions.py`
"""


# =============================================================================
# WARM-UP: Conditionals and Basic Loops
# =============================================================================

# Exercise 1: FizzBuzz
# Difficulty: Easy
def fizzbuzz(n: int) -> list[str]:
    """Return a list of FizzBuzz strings for numbers 1 to n."""
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result

    # Pythonic alternative: list comprehension (concise but less readable)
    # return [
    #     "FizzBuzz" if i % 15 == 0
    #     else "Fizz" if i % 3 == 0
    #     else "Buzz" if i % 5 == 0
    #     else str(i)
    #     for i in range(1, n + 1)
    # ]

    # Clever alternative: string concatenation
    # return [
    #     (("Fizz" * (i % 3 == 0)) + ("Buzz" * (i % 5 == 0))) or str(i)
    #     for i in range(1, n + 1)
    # ]


# Exercise 2: Ternary Classifier
# Difficulty: Easy
def classify_number(n: int) -> str:
    """Classify a number using ternary expressions."""
    return "positive" if n > 0 else "negative" if n < 0 else "zero"
    # This chains two ternary expressions:
    # 1. "positive" if n > 0 else (rest)
    # 2. "negative" if n < 0 else "zero"


# Exercise 3: Early Return Pattern
# Difficulty: Easy
def validate_password(password: str) -> tuple[bool, str]:
    """Validate a password using early returns (Python's guard equivalent)."""
    if len(password) < 8:
        return (False, "Too short")

    if not any(c.isdigit() for c in password):
        return (False, "No digit")

    if not any(c.isupper() for c in password):
        return (False, "No uppercase")

    return (True, "Valid")

    # Note: `any(c.isdigit() for c in password)` is a generator expression
    # inside any(). It short-circuits: stops as soon as a digit is found.

    # Alternative using regex:
    # import re
    # if not re.search(r'\d', password):
    #     return (False, "No digit")
    # if not re.search(r'[A-Z]', password):
    #     return (False, "No uppercase")


# =============================================================================
# CORE: Comprehensions
# =============================================================================

# Exercise 4: List Comprehension Basics
# Difficulty: Medium
def comprehension_basics() -> dict[str, list]:
    """Create various lists using comprehensions."""
    return {
        "squares": [x**2 for x in range(10)],
        "even_squares": [x**2 for x in range(10) if x % 2 == 0],
        "words_upper": [w.upper() for w in ["hello", "world", "python"]],
        "lengths": [len(w) for w in ["cat", "elephant", "dog", "hippopotamus"]],
    }
    # Note: The comprehension [x**2 for x in range(10) if x % 2 == 0]
    # is equivalent to Swift: (0..<10).filter { $0 % 2 == 0 }.map { $0 * $0 }


# Exercise 5: Dict Comprehension
# Difficulty: Medium
def invert_and_filter(d: dict[str, int], min_value: int = 0) -> dict[int, str]:
    """Invert a dict, keeping only entries where original value >= min_value."""
    return {v: k for k, v in d.items() if v >= min_value}
    # Dict comprehension with filter condition.
    # d.items() yields (key, value) tuples; we swap them in the output.


# Exercise 6: Nested Comprehension -- Matrix Transpose
# Difficulty: Medium
def transpose(matrix: list[list[int]]) -> list[list[int]]:
    """Transpose a matrix using nested comprehension."""
    return [[row[i] for row in matrix] for i in range(len(matrix[0]))]
    # Outer comprehension: iterate over column indices
    # Inner comprehension: collect that column index from each row

    # Pythonic alternative using zip + unpacking:
    # return [list(col) for col in zip(*matrix)]
    # The * unpacks the matrix so each row is a separate argument to zip.
    # zip then groups the first elements, second elements, etc.


# Exercise 7: Set Comprehension -- Unique Word Lengths
# Difficulty: Easy
def unique_word_lengths(sentence: str) -> set[int]:
    """Return the set of unique word lengths."""
    return {len(word) for word in sentence.split()}
    # Set comprehension uses {} like dict, but without key:value pairs.
    # Duplicates are automatically eliminated.


# =============================================================================
# CORE: Iteration Patterns
# =============================================================================

# Exercise 8: Enumerate and Zip
# Difficulty: Medium
def merge_with_index(names: list[str], scores: list[int]) -> list[str]:
    """Merge names and scores into indexed strings."""
    return [
        f"{i}. {name}: {score}"
        for i, (name, score) in enumerate(zip(names, scores), start=1)
    ]
    # enumerate(zip(...), start=1) gives us:
    # (1, ("Alice", 95)), (2, ("Bob", 87)), ...
    # We unpack (name, score) from the zip tuple.

    # Alternative without comprehension:
    # result = []
    # for i, (name, score) in enumerate(zip(names, scores), start=1):
    #     result.append(f"{i}. {name}: {score}")
    # return result


# Exercise 9: For-Else Pattern
# Difficulty: Medium
def find_first_negative(numbers: list[int]) -> str:
    """Find the first negative number using for-else."""
    for i, num in enumerate(numbers):
        if num < 0:
            return f"Found {num} at index {i}"
    else:
        return "All positive"
    # The else clause runs only if the loop completes without break/return.
    # Since we return inside the loop, the else handles the "not found" case.

    # Note: In this case, the else is technically unnecessary since the
    # return inside the loop already exits. But the for-else pattern is
    # most useful when you use break instead of return:
    #
    # for i, num in enumerate(numbers):
    #     if num < 0:
    #         result = f"Found {num} at index {i}"
    #         break
    # else:
    #     result = "All positive"
    # return result


# Exercise 10: Generator Expression
# Difficulty: Medium
def analyze_numbers(numbers: list[int]) -> dict[str, object]:
    """Analyze numbers using generator expressions."""
    return {
        "sum_of_squares": sum(x**2 for x in numbers),
        "has_negative": any(x < 0 for x in numbers),
        "all_even": all(x % 2 == 0 for x in numbers),
        "count_positive": sum(1 for x in numbers if x > 0),
    }
    # Generator expressions are used inside sum(), any(), all().
    # They don't create intermediate lists -- values are computed lazily.
    #
    # sum(1 for x in numbers if x > 0) is a common idiom for counting
    # items that match a condition. It's equivalent to:
    # len([x for x in numbers if x > 0])
    # but more memory-efficient.


# =============================================================================
# CHALLENGE: Match/Case, Walrus Operator, Advanced Patterns
# =============================================================================

# Exercise 11: Match/Case with Patterns
# Difficulty: Hard
def describe_shape(shape: tuple) -> str:
    """Describe a shape using match/case."""
    match shape:
        case ():
            return "empty"
        case (r,) if r > 0:
            return f"circle with radius {r}"
        case (w, h) if w == h and w > 0:
            return f"square with side {w}"
        case (w, h) if w > 0 and h > 0:
            return f"rectangle {w}x{h}"
        case (a, b, c) if a > 0 and b > 0 and c > 0:
            return f"triangle with sides {a}, {b}, {c}"
        case _:
            return "unknown shape"
    # Note: Order matters! Square must be checked before rectangle
    # because a square also matches the (w, h) pattern.
    # Guards (if conditions) are checked after the pattern matches.


# Exercise 12: Match/Case with Dict Patterns
# Difficulty: Hard
def process_event(event: dict) -> str:
    """Process an event dict using match/case."""
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"Click at ({x}, {y})"
        case {"type": "keypress", "key": key, "modifiers": [mod, *_]}:
            return f"Key '{key}' with modifier '{mod}'"
        case {"type": "keypress", "key": key}:
            return f"Key '{key}'"
        case {"type": "scroll", "direction": ("up" | "down") as d}:
            return f"Scroll {d}"
        case {"type": t}:
            return f"Unknown event: {t}"
        case _:
            return "Invalid event"
    # Dict patterns match if the dict CONTAINS the specified keys.
    # Extra keys are allowed (partial matching).
    #
    # [mod, *_] matches a list with at least one element, capturing the first.
    # ("up" | "down") as d matches either value and binds it to d.
    #
    # Order matters: keypress with modifiers must come before keypress without,
    # because the simpler pattern would match both.


# Exercise 13: Walrus Operator
# Difficulty: Hard
def filter_long_words(text: str, min_length: int = 5) -> list[tuple[str, int]]:
    """Find words meeting minimum length using walrus operator."""
    result = [
        (word.lower(), length)
        for word in text.split()
        if (length := len(word)) >= min_length
    ]
    return sorted(result, key=lambda x: (-x[1], x[0]))
    # The walrus operator `:=` assigns len(word) to `length` AND returns it
    # for the condition check. Then `length` is available in the expression
    # part of the comprehension, avoiding computing len(word) twice.
    #
    # sorted() with key=lambda x: (-x[1], x[0]) sorts by:
    #   1. Length descending (negative for reverse)
    #   2. Alphabetically ascending (tiebreaker)

    # Without walrus operator (computes len twice):
    # result = [
    #     (word.lower(), len(word))
    #     for word in text.split()
    #     if len(word) >= min_length
    # ]


# Exercise 14: Comprehension Pipeline
# Difficulty: Hard
def process_student_scores(
    students: list[dict[str, object]],
) -> dict[str, str]:
    """Process student records and return grade assignments."""
    def get_grade(avg: float) -> str:
        if avg >= 90:
            return "A"
        elif avg >= 80:
            return "B"
        elif avg >= 70:
            return "C"
        elif avg >= 60:
            return "D"
        else:
            return "F"

    return {
        s["name"]: get_grade(sum(s["scores"]) / len(s["scores"]))
        for s in students
        if s["scores"]  # Filter out students with empty scores (truthiness!)
    }
    # The dict comprehension:
    # 1. Filters students with non-empty scores using truthiness of the list
    # 2. Calculates average inline
    # 3. Maps name -> grade using the helper function
    #
    # Alternative with walrus operator:
    # return {
    #     s["name"]: get_grade(avg)
    #     for s in students
    #     if s["scores"] and (avg := sum(s["scores"]) / len(s["scores"])) is not None
    # }


# =============================================================================
# SWIFT BRIDGE: Rewrite Swift Control Flow in Python
# =============================================================================

# Exercise 15: Swift-Style Higher-Order Functions
# Difficulty: Medium
def sum_of_even_squares(numbers: list[int]) -> int:
    """Filter even numbers, square them, and sum the result."""
    return sum(x**2 for x in numbers if x % 2 == 0)
    # This single generator expression replaces Swift's chain:
    #   .filter { $0 % 2 == 0 }
    #   .map { $0 * $0 }
    #   .reduce(0, +)
    #
    # The generator expression combines filter and map in one pass.

    # Alternative using reduce (from functools):
    # from functools import reduce
    # return reduce(lambda acc, x: acc + x**2,
    #               filter(lambda x: x % 2 == 0, numbers), 0)
    # This is more "functional" but less Pythonic than the comprehension.

    # Alternative with explicit steps:
    # evens = [x for x in numbers if x % 2 == 0]
    # squares = [x**2 for x in evens]
    # return sum(squares)


# =============================================================================
# Self-Test Runner
# =============================================================================

if __name__ == "__main__":
    print("Running Module 02 Solutions...\n")
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
        print("All solutions passed!")
    else:
        print(f"{errors} solution(s) have issues.")
    print(f"{'='*50}")
