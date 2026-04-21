"""
Module 01: Syntax and Types - Solutions
========================================
Complete solutions for all exercises with Pythonic alternatives and notes.

Run this file to verify all solutions pass: `python solutions.py`
"""


# =============================================================================
# WARM-UP: Variable Assignment, Type Checking, f-Strings
# =============================================================================

# Exercise 1: Variable Swap
# Difficulty: Easy
def swap_values(a: int, b: int) -> tuple[int, int]:
    """Return a tuple with the values swapped."""
    # Pythonic: Python's tuple packing/unpacking makes this a one-liner
    return b, a
    # Note: In Python, `a, b = b, a` is idiomatic for in-place swaps.
    # The right side is fully evaluated before assignment, so no temp needed.


# Exercise 2: Type Inspector
# Difficulty: Easy
def type_inspector(value) -> str:
    """Return the name of the type as a string."""
    return type(value).__name__
    # Note: type() returns the class, __name__ gets its string name.
    # This handles ALL types, including custom classes.

    # Alternative (less Pythonic -- hardcoding types):
    # if isinstance(value, bool):    # Must check bool BEFORE int!
    #     return "bool"
    # elif isinstance(value, int):
    #     return "int"
    # ...


# Exercise 3: Greeting Formatter
# Difficulty: Easy
def format_greeting(name: str, age: int) -> str:
    """Return a greeting using f-string formatting."""
    return f"Hello, {name}! You are {age} years old."

    # Alternative: str.format() (older style)
    # return "Hello, {}! You are {} years old.".format(name, age)

    # Alternative: % formatting (oldest style, avoid in new code)
    # return "Hello, %s! You are %d years old." % (name, age)


# Exercise 4: Debug String
# Difficulty: Easy
def debug_format(x: int, y: int) -> str:
    """Return a debug string showing variable names and values."""
    return f"{x=}, {y=}"
    # The f-string = syntax was added in Python 3.8.
    # f"{x=}" produces "x=<value>" automatically.


# =============================================================================
# CORE: Type Conversions, String Manipulation, None Handling
# =============================================================================

# Exercise 5: Safe Integer Conversion
# Difficulty: Medium
def safe_int(value: str, default: int = 0) -> int:
    """Convert a string to int, returning default if conversion fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
    # Note: "3.14" raises ValueError with int() because int() doesn't
    # parse floats. You'd need int(float("3.14")) if you wanted that.

    # Pythonic alternative using walrus operator (Python 3.8+):
    # This doesn't work as cleanly here since try/except is the idiomatic way.


# Exercise 6: Number Formatter
# Difficulty: Medium
def format_number(value: float, decimals: int = 2) -> str:
    """Format a number with commas and specified decimal places."""
    return f"{value:,.{decimals}f}"
    # The format spec `:,.2f` means:
    #   , = comma thousands separator
    #   .2 = 2 decimal places
    #   f = fixed-point notation

    # Alternative using format():
    # return format(value, f",.{decimals}f")


# Exercise 7: String Analyzer
# Difficulty: Medium
def analyze_string(s: str) -> dict:
    """Analyze a string and return a dict with various properties."""
    return {
        "length": len(s),
        "words": len(s.split()),
        "upper": sum(1 for c in s if c.isupper()),
        "lower": sum(1 for c in s if c.islower()),
        "digits": sum(1 for c in s if c.isdigit()),
        "is_title": s.istitle(),
    }
    # Note: Using generator expressions inside sum() is memory-efficient
    # (doesn't create an intermediate list).

    # Pythonic alternative for counting:
    # from collections import Counter
    # import unicodedata
    # But for these simple checks, the generator approach is clearest.


# Exercise 8: None-Safe Property Access
# Difficulty: Medium
def safe_get(data: dict | None, key: str, default=None):
    """Safely get a value from a dict, returning default if data is None or key missing."""
    if data is None:
        return default
    return data.get(key, default)
    # dict.get(key, default) is the Pythonic way to access dict values
    # with a fallback -- it never raises KeyError.

    # One-liner alternative:
    # return data.get(key, default) if data is not None else default


# Exercise 9: String Reversal and Palindrome Check
# Difficulty: Medium
def is_palindrome(s: str) -> bool:
    """Check if a string is a palindrome (case-insensitive, ignoring spaces)."""
    cleaned = s.lower().replace(" ", "")
    return cleaned == cleaned[::-1]
    # [::-1] is the Pythonic way to reverse a sequence.
    # Complexity: O(n) time and space.

    # Alternative (two-pointer approach, O(1) space):
    # cleaned = s.lower().replace(" ", "")
    # left, right = 0, len(cleaned) - 1
    # while left < right:
    #     if cleaned[left] != cleaned[right]:
    #         return False
    #     left += 1
    #     right -= 1
    # return True


# Exercise 10: Multi-Base Converter
# Difficulty: Medium
def multi_base(n: int) -> dict[str, str]:
    """Convert an integer to multiple base representations."""
    return {
        "bin": bin(n),
        "oct": oct(n),
        "hex": hex(n),
    }
    # bin(), oct(), hex() are built-in functions that include the prefix.
    # To remove prefix: bin(n)[2:], or format(n, 'b')


# =============================================================================
# CHALLENGE: Type Hints, Complex String Formatting
# =============================================================================

# Exercise 11: Table Formatter
# Difficulty: Hard
def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Format data as a simple text table with right-padded columns."""
    # Calculate column widths (max of header and all row values)
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Build header row (ljust pads with spaces to the right)
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))

    # Build separator row
    separator = "+".join("-" * (col_widths[i] + 1) for i in range(len(headers)))
    # Adjust: first column gets no leading space, use full width + 1 for first col dash
    separator = "+".join("-" * (w + (0 if i == 0 else 1))
                         for i, w in enumerate(col_widths))
    # Simpler approach: match the column widths with padding
    parts = []
    for i, w in enumerate(col_widths):
        if i == 0:
            parts.append("-" * (w + 1))  # +1 for trailing space before |
        else:
            parts.append("-" * (w + 1))  # +1 for leading space after |
    separator = "+".join(parts)

    # Build data rows
    data_lines = []
    for row in rows:
        line = " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
        data_lines.append(line.rstrip())

    # Combine (rstrip to remove trailing spaces)
    result = header_line.rstrip() + "\n" + separator + "\n" + "\n".join(data_lines)
    return result

    # Note: For production code, consider the `tabulate` library:
    # from tabulate import tabulate
    # print(tabulate(rows, headers=headers))


# Exercise 12: Type Coercion Chain
# Difficulty: Hard
def coercion_chain(value: str) -> dict:
    """Process a numeric string through a chain of type conversions."""
    as_float = float(value)
    as_int = int(as_float)
    as_bool = bool(as_int)
    as_bool_int = int(as_bool)
    as_str = str(as_bool_int)

    return {
        "float": as_float,
        "int": as_int,
        "bool": as_bool,
        "bool_as_int": as_bool_int,
        "final_str": as_str,
    }
    # Key insight: bool is a subclass of int in Python!
    # int(True) == 1, int(False) == 0
    # bool(0) == False, bool(anything_else) == True


# Exercise 13: Truthiness Tester
# Difficulty: Medium
def classify_truthiness(values: list) -> dict[str, list]:
    """Classify a list of values into truthy and falsy groups."""
    truthy = [v for v in values if v]
    falsy = [v for v in values if not v]
    return {"truthy": truthy, "falsy": falsy}

    # Pythonic alternative using itertools:
    # from itertools import filterfalse
    # truthy = list(filter(bool, values))
    # falsy = list(filterfalse(bool, values))

    # Note: Be careful with `0 in falsy` -- 0 == False in Python,
    # so you might get unexpected membership test results.


# =============================================================================
# SWIFT BRIDGE: Rewrite Swift Snippets in Python
# =============================================================================

# Exercise 14: Swift Optional Handling
# Difficulty: Medium
def get_display_name(first_name: str | None, last_name: str | None) -> str:
    """Return a display name from optional first and last names."""
    # Python equivalent of Swift's ?? (nil coalescing) is `or` for strings,
    # but be careful: `or` uses truthiness, so "" would also trigger fallback.
    # For None specifically, use explicit check or ternary.
    first = first_name if first_name is not None else "Unknown"
    last = last_name if last_name is not None else ""

    if last:
        return f"{first} {last}"
    return first

    # Shorter alternative (works because we treat "" same as None for last):
    # first = first_name or "Unknown"
    # last = last_name or ""
    # return f"{first} {last}" if last else first
    #
    # But note: `first_name or "Unknown"` would also replace "" with "Unknown",
    # which might not match the Swift behavior. Use the explicit check when
    # you need to distinguish None from empty string.


# Exercise 15: Swift String Processing
# Difficulty: Hard
def process_csv_line(line: str) -> dict[str, str]:
    """Parse a CSV line into a dictionary."""
    parts = [part.strip() for part in line.split(",")]
    if len(parts) < 3:
        return {}
    return {"name": parts[0], "age": parts[1], "city": parts[2]}

    # Note: For real CSV parsing, use the csv module:
    # import csv
    # reader = csv.reader([line])
    # parts = next(reader)
    #
    # The csv module handles quoted fields, embedded commas, etc.

    # Pythonic note: The list comprehension `[p.strip() for p in line.split(",")]`
    # is the Python equivalent of Swift's `.map { $0.trimmingCharacters(in: .whitespaces) }`


# =============================================================================
# Self-Test Runner
# =============================================================================

if __name__ == "__main__":
    print("Running Module 01 Solutions...\n")
    errors = 0

    # Exercise 1
    try:
        assert swap_values(1, 2) == (2, 1)
        assert swap_values(10, 20) == (20, 10)
        print("  Exercise  1 (swap_values):          PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  1 (swap_values):          FAIL - {e}")
        errors += 1

    # Exercise 2
    try:
        assert type_inspector(42) == "int"
        assert type_inspector("hello") == "str"
        assert type_inspector(3.14) == "float"
        assert type_inspector(True) == "bool"
        assert type_inspector(None) == "NoneType"
        assert type_inspector([1, 2]) == "list"
        print("  Exercise  2 (type_inspector):        PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  2 (type_inspector):        FAIL - {e}")
        errors += 1

    # Exercise 3
    try:
        assert format_greeting("Daniel", 30) == "Hello, Daniel! You are 30 years old."
        assert format_greeting("Alice", 25) == "Hello, Alice! You are 25 years old."
        print("  Exercise  3 (format_greeting):       PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  3 (format_greeting):       FAIL - {e}")
        errors += 1

    # Exercise 4
    try:
        assert debug_format(10, 20) == "x=10, y=20"
        assert debug_format(0, 0) == "x=0, y=0"
        print("  Exercise  4 (debug_format):          PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  4 (debug_format):          FAIL - {e}")
        errors += 1

    # Exercise 5
    try:
        assert safe_int("42") == 42
        assert safe_int("hello") == 0
        assert safe_int("", -1) == -1
        assert safe_int("3.14") == 0
        print("  Exercise  5 (safe_int):              PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  5 (safe_int):              FAIL - {e}")
        errors += 1

    # Exercise 6
    try:
        assert format_number(1234567.891) == "1,234,567.89"
        assert format_number(1234567.891, 0) == "1,234,568"
        assert format_number(42.5, 3) == "42.500"
        print("  Exercise  6 (format_number):         PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  6 (format_number):         FAIL - {e}")
        errors += 1

    # Exercise 7
    try:
        result = analyze_string("Hello World 123")
        assert result["length"] == 15
        assert result["words"] == 3
        assert result["upper"] == 2
        assert result["lower"] == 8
        assert result["digits"] == 3
        assert result["is_title"] is True
        print("  Exercise  7 (analyze_string):        PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  7 (analyze_string):        FAIL - {e}")
        errors += 1

    # Exercise 8
    try:
        assert safe_get({"name": "Daniel"}, "name") == "Daniel"
        assert safe_get({"name": "Daniel"}, "age") is None
        assert safe_get({"name": "Daniel"}, "age", 0) == 0
        assert safe_get(None, "name") is None
        assert safe_get(None, "name", "Unknown") == "Unknown"
        print("  Exercise  8 (safe_get):              PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  8 (safe_get):              FAIL - {e}")
        errors += 1

    # Exercise 9
    try:
        assert is_palindrome("racecar") is True
        assert is_palindrome("Race Car") is True
        assert is_palindrome("hello") is False
        assert is_palindrome("A man a plan a canal Panama") is True
        print("  Exercise  9 (is_palindrome):         PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  9 (is_palindrome):         FAIL - {e}")
        errors += 1

    # Exercise 10
    try:
        assert multi_base(255) == {"bin": "0b11111111", "oct": "0o377", "hex": "0xff"}
        assert multi_base(10) == {"bin": "0b1010", "oct": "0o12", "hex": "0xa"}
        print("  Exercise 10 (multi_base):            PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 10 (multi_base):            FAIL - {e}")
        errors += 1

    # Exercise 11
    try:
        expected = "Name  | Age\n------+----\nAlice | 30\nBob   | 25"
        result = format_table(["Name", "Age"], [["Alice", "30"], ["Bob", "25"]])
        assert result == expected, f"Got:\n{result}\n\nExpected:\n{expected}"
        print("  Exercise 11 (format_table):          PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 11 (format_table):          FAIL - {e}")
        errors += 1

    # Exercise 12
    try:
        assert coercion_chain("3.14") == {
            "float": 3.14, "int": 3, "bool": True, "bool_as_int": 1, "final_str": "1"
        }
        assert coercion_chain("0.0") == {
            "float": 0.0, "int": 0, "bool": False, "bool_as_int": 0, "final_str": "0"
        }
        print("  Exercise 12 (coercion_chain):        PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 12 (coercion_chain):        FAIL - {e}")
        errors += 1

    # Exercise 13
    try:
        result = classify_truthiness([0, 1, "", "hello", None, [], [0], {}, True, False])
        assert result["truthy"] == [1, "hello", [0], True]
        assert result["falsy"] == [0, "", None, [], {}, False]
        print("  Exercise 13 (classify_truthiness):   PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 13 (classify_truthiness):   FAIL - {e}")
        errors += 1

    # Exercise 14
    try:
        assert get_display_name("Daniel", "Berger") == "Daniel Berger"
        assert get_display_name(None, "Berger") == "Unknown Berger"
        assert get_display_name("Daniel", None) == "Daniel"
        assert get_display_name(None, None) == "Unknown"
        assert get_display_name("Daniel", "") == "Daniel"
        print("  Exercise 14 (get_display_name):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 14 (get_display_name):      FAIL - {e}")
        errors += 1

    # Exercise 15
    try:
        assert process_csv_line("Alice, 30, New York") == {
            "name": "Alice", "age": "30", "city": "New York"
        }
        assert process_csv_line("Bob,25,London") == {
            "name": "Bob", "age": "25", "city": "London"
        }
        assert process_csv_line("Only,Two") == {}
        assert process_csv_line("") == {}
        print("  Exercise 15 (process_csv_line):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 15 (process_csv_line):      FAIL - {e}")
        errors += 1

    print(f"\n{'='*50}")
    if errors == 0:
        print("All solutions passed!")
    else:
        print(f"{errors} solution(s) have issues.")
    print(f"{'='*50}")
