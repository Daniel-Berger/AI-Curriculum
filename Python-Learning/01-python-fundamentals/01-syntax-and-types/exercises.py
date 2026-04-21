"""
Module 01: Syntax and Types - Exercises
========================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` or `...` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- If no AssertionError is raised, your solution is correct.

Difficulty levels:
  Easy   - Direct translation from Swift concepts
  Medium - Requires understanding Python-specific behavior
  Hard   - Combines multiple concepts or requires Pythonic thinking
"""


# =============================================================================
# WARM-UP: Variable Assignment, Type Checking, f-Strings
# =============================================================================

# Exercise 1: Variable Swap
# Difficulty: Easy
# Swap the values of two variables without using a temporary variable.
def swap_values(a: int, b: int) -> tuple[int, int]:
    """Return a tuple with the values swapped.

    >>> swap_values(1, 2)
    (2, 1)
    """
    pass


# Exercise 2: Type Inspector
# Difficulty: Easy
# Return a string describing the type of the given value.
def type_inspector(value) -> str:
    """Return the name of the type as a string.

    >>> type_inspector(42)
    'int'
    >>> type_inspector("hello")
    'str'
    >>> type_inspector(3.14)
    'float'
    >>> type_inspector(True)
    'bool'
    >>> type_inspector(None)
    'NoneType'
    """
    pass


# Exercise 3: Greeting Formatter
# Difficulty: Easy
# Use an f-string to format a greeting message.
def format_greeting(name: str, age: int) -> str:
    """Return a greeting using f-string formatting.

    >>> format_greeting("Daniel", 30)
    'Hello, Daniel! You are 30 years old.'
    """
    pass


# Exercise 4: Debug String
# Difficulty: Easy
# Use f-string debugging syntax (f"{var=}") to create a debug output.
def debug_format(x: int, y: int) -> str:
    """Return a debug string showing variable names and values.

    >>> debug_format(10, 20)
    'x=10, y=20'

    Hint: Use f-string = syntax, e.g., f"{x=}"
    """
    pass


# =============================================================================
# CORE: Type Conversions, String Manipulation, None Handling
# =============================================================================

# Exercise 5: Safe Integer Conversion
# Difficulty: Medium
# Convert a string to an integer safely, returning a default on failure.
def safe_int(value: str, default: int = 0) -> int:
    """Convert a string to int, returning default if conversion fails.

    >>> safe_int("42")
    42
    >>> safe_int("hello")
    0
    >>> safe_int("", -1)
    -1
    >>> safe_int("3.14")
    0
    """
    pass


# Exercise 6: Number Formatter
# Difficulty: Medium
# Format a number with commas as thousands separators and specified decimal places.
def format_number(value: float, decimals: int = 2) -> str:
    """Format a number with commas and specified decimal places.

    >>> format_number(1234567.891)
    '1,234,567.89'
    >>> format_number(1234567.891, 0)
    '1,234,568'
    >>> format_number(42.5, 3)
    '42.500'
    """
    pass


# Exercise 7: String Analyzer
# Difficulty: Medium
# Analyze a string and return a dictionary of its properties.
def analyze_string(s: str) -> dict:
    """Analyze a string and return a dict with these keys:
    - 'length': number of characters
    - 'words': number of words (split by whitespace)
    - 'upper': number of uppercase letters
    - 'lower': number of lowercase letters
    - 'digits': number of digit characters
    - 'is_title': whether the string is title case

    >>> result = analyze_string("Hello World 123")
    >>> result['length']
    15
    >>> result['words']
    3
    >>> result['upper']
    2
    >>> result['lower']
    8
    >>> result['digits']
    3
    >>> result['is_title']
    True
    """
    pass


# Exercise 8: None-Safe Property Access
# Difficulty: Medium
# Implement a function that safely gets a nested value, returning a default if
# any part of the chain is None.
def safe_get(data: dict | None, key: str, default=None):
    """Safely get a value from a dict, returning default if data is None or key missing.

    >>> safe_get({"name": "Daniel"}, "name")
    'Daniel'
    >>> safe_get({"name": "Daniel"}, "age")
    >>> safe_get({"name": "Daniel"}, "age", 0)
    0
    >>> safe_get(None, "name")
    >>> safe_get(None, "name", "Unknown")
    'Unknown'
    """
    pass


# Exercise 9: String Reversal and Palindrome Check
# Difficulty: Medium
# Check if a string is a palindrome (reads the same forwards and backwards).
def is_palindrome(s: str) -> bool:
    """Check if a string is a palindrome (case-insensitive, ignoring spaces).

    >>> is_palindrome("racecar")
    True
    >>> is_palindrome("Race Car")
    True
    >>> is_palindrome("hello")
    False
    >>> is_palindrome("A man a plan a canal Panama")
    True
    """
    pass


# Exercise 10: Multi-Base Converter
# Difficulty: Medium
# Convert an integer to binary, octal, and hexadecimal string representations.
def multi_base(n: int) -> dict[str, str]:
    """Convert an integer to multiple base representations.

    Returns a dict with keys 'bin', 'oct', 'hex', each containing the
    string representation WITH the prefix (0b, 0o, 0x).

    >>> multi_base(255)
    {'bin': '0b11111111', 'oct': '0o377', 'hex': '0xff'}
    >>> multi_base(10)
    {'bin': '0b1010', 'oct': '0o12', 'hex': '0xa'}
    """
    pass


# =============================================================================
# CHALLENGE: Type Hints, Complex String Formatting
# =============================================================================

# Exercise 11: Table Formatter
# Difficulty: Hard
# Create a formatted text table from data.
def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Format data as a simple text table with right-padded columns.

    Each column should be as wide as the widest item in that column
    (considering both headers and data). Columns separated by " | ".
    Include a separator row of dashes after the header.

    >>> print(format_table(["Name", "Age"], [["Alice", "30"], ["Bob", "25"]]))
    Name  | Age
    ------+----
    Alice | 30
    Bob   | 25

    Note: No trailing spaces on any line. No trailing newline.
    """
    pass


# Exercise 12: Type Coercion Chain
# Difficulty: Hard
# Apply a chain of type conversions and return the final result.
def coercion_chain(value: str) -> dict:
    """Process a numeric string through a chain of type conversions.

    Starting with a string representation of a float:
    1. Convert to float
    2. Convert to int (truncation)
    3. Convert to bool
    4. Convert back to int (from bool)
    5. Convert to string

    Return a dict with keys 'float', 'int', 'bool', 'bool_as_int', 'final_str'
    showing each stage.

    >>> coercion_chain("3.14")
    {'float': 3.14, 'int': 3, 'bool': True, 'bool_as_int': 1, 'final_str': '1'}
    >>> coercion_chain("0.0")
    {'float': 0.0, 'int': 0, 'bool': False, 'bool_as_int': 0, 'final_str': '0'}
    """
    pass


# Exercise 13: Truthiness Tester
# Difficulty: Medium
# Classify a value as truthy or falsy using Python's truthiness rules.
def classify_truthiness(values: list) -> dict[str, list]:
    """Classify a list of values into truthy and falsy groups.

    Returns a dict with 'truthy' and 'falsy' keys, each containing a list
    of values from the input.

    >>> result = classify_truthiness([0, 1, "", "hello", None, [], [0], {}, True, False])
    >>> result['truthy']
    [1, 'hello', [0], True]
    >>> result['falsy']
    [0, '', None, [], {}, False]
    """
    pass


# =============================================================================
# SWIFT BRIDGE: Rewrite Swift Snippets in Python
# =============================================================================

# Exercise 14: Swift Optional Handling
# Difficulty: Medium
# Swift code to rewrite:
#     func getDisplayName(firstName: String?, lastName: String?) -> String {
#         let first = firstName ?? "Unknown"
#         let last = lastName ?? ""
#         return last.isEmpty ? first : "\(first) \(last)"
#     }
def get_display_name(first_name: str | None, last_name: str | None) -> str:
    """Return a display name from optional first and last names.

    If first_name is None, use "Unknown".
    If last_name is None or empty, return just the first name.
    Otherwise, return "first last".

    >>> get_display_name("Daniel", "Berger")
    'Daniel Berger'
    >>> get_display_name(None, "Berger")
    'Unknown Berger'
    >>> get_display_name("Daniel", None)
    'Daniel'
    >>> get_display_name(None, None)
    'Unknown'
    >>> get_display_name("Daniel", "")
    'Daniel'
    """
    pass


# Exercise 15: Swift String Processing
# Difficulty: Hard
# Swift code to rewrite:
#     func processCSVLine(_ line: String) -> [String: String] {
#         let parts = line.split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }
#         guard parts.count >= 3 else { return [:] }
#         return ["name": parts[0], "age": parts[1], "city": parts[2]]
#     }
def process_csv_line(line: str) -> dict[str, str]:
    """Parse a CSV line into a dictionary.

    Split by comma, trim whitespace from each part.
    If fewer than 3 parts, return an empty dict.
    Otherwise return dict with keys 'name', 'age', 'city' mapped to the
    first three parts.

    >>> process_csv_line("Alice, 30, New York")
    {'name': 'Alice', 'age': '30', 'city': 'New York'}
    >>> process_csv_line("Bob,25,London")
    {'name': 'Bob', 'age': '25', 'city': 'London'}
    >>> process_csv_line("Only,Two")
    {}
    >>> process_csv_line("")
    {}
    """
    pass


# =============================================================================
# Self-Test Runner
# =============================================================================

if __name__ == "__main__":
    print("Running Module 01 Exercises...\n")
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
        print("All exercises passed!")
    else:
        print(f"{errors} exercise(s) need attention.")
    print(f"{'='*50}")
