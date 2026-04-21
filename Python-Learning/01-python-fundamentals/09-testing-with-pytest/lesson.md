# Module 09: Testing with pytest

## Introduction

If you come from Swift/iOS development, you are accustomed to XCTest -- Apple's built-in
testing framework that is tightly integrated with Xcode. Python's testing story is different:
while the standard library includes `unittest` (modeled after Java's JUnit), the community has
overwhelmingly adopted **pytest** as the go-to testing framework. pytest is simpler, more
powerful, and more Pythonic than unittest.

This module covers pytest from the ground up: writing tests, organizing them, using fixtures,
parametrizing, mocking, and integrating with coverage tools. By the end, you will be
comfortable writing thorough test suites for any Python project.

---

## Table of Contents

1. [Why pytest Over unittest](#1-why-pytest-over-unittest)
2. [Getting Started](#2-getting-started)
3. [Writing Your First Tests](#3-writing-your-first-tests)
4. [Assert Statements -- No Special Methods Needed](#4-assert-statements--no-special-methods-needed)
5. [Test Discovery](#5-test-discovery)
6. [Fixtures](#6-fixtures)
7. [Parametrize](#7-parametrize)
8. [Markers](#8-markers)
9. [Testing Exceptions](#9-testing-exceptions)
10. [Mocking](#10-mocking)
11. [Temporary Files and Directories](#11-temporary-files-and-directories)
12. [Capturing Output](#12-capturing-output)
13. [Test Organization Best Practices](#13-test-organization-best-practices)
14. [Coverage with pytest-cov](#14-coverage-with-pytest-cov)
15. [Test-Driven Development Workflow](#15-test-driven-development-workflow)
16. [Advanced Tips](#16-advanced-tips)

---

## 1. Why pytest Over unittest

### unittest: The Standard Library Option

Python ships with `unittest`, which requires you to:

```python
import unittest

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_add(self):
        self.assertEqual(self.calc.add(2, 3), 5)

    def test_subtract(self):
        self.assertEqual(self.calc.subtract(5, 3), 2)

if __name__ == "__main__":
    unittest.main()
```

This looks a lot like XCTest, and for good reason -- both are JUnit-inspired. But notice:
- You must subclass `unittest.TestCase`
- You use special assertion methods (`assertEqual`, `assertTrue`, `assertRaises`, etc.)
- Setup/teardown are method overrides on the class

### pytest: The Community Standard

The same tests in pytest:

```python
from calculator import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_subtract():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
```

Key differences:
- **No class required** -- tests are just functions
- **Plain `assert`** -- no special assertion methods to memorize
- **Better error messages** -- pytest rewrites `assert` to show detailed failure info
- **Powerful fixtures** -- replace setUp/tearDown with composable, reusable fixtures
- **Rich plugin ecosystem** -- hundreds of plugins available

### What pytest Shows You on Failure

When an assertion fails, pytest provides rich introspection:

```
    def test_add():
        calc = Calculator()
>       assert calc.add(2, 3) == 6
E       assert 5 == 6
E        +  where 5 = <bound method Calculator.add of ...>(2, 3)
```

Compare this to unittest's terse `AssertionError: 5 != 6`. pytest tells you exactly
what happened and what was called.

---

## 2. Getting Started

### Installation

```bash
pip install pytest
```

Verify the installation:

```bash
pytest --version
```

### Project Structure

A typical Python project with tests:

```
my_project/
    src/
        my_project/
            __init__.py
            calculator.py
            user_service.py
    tests/
        __init__.py
        test_calculator.py
        test_user_service.py
        conftest.py
    pyproject.toml
```

Or, for simpler projects:

```
my_project/
    my_project/
        __init__.py
        calculator.py
    tests/
        test_calculator.py
        conftest.py
    pyproject.toml
```

### Configuration in pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
addopts = "-v --tb=short"
```

### Running Tests

```bash
# Run all tests
pytest

# Run a specific file
pytest tests/test_calculator.py

# Run a specific test function
pytest tests/test_calculator.py::test_add

# Run tests matching a keyword expression
pytest -k "add or subtract"

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x

# Run last failed tests first
pytest --lf

# Show local variables in tracebacks
pytest -l

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

---

## 3. Writing Your First Tests

### The Basics

A test in pytest is simply a function whose name starts with `test_`:

```python
# test_basics.py

def test_integer_addition():
    assert 1 + 1 == 2

def test_string_concatenation():
    assert "hello" + " " + "world" == "hello world"

def test_list_append():
    items = [1, 2, 3]
    items.append(4)
    assert items == [1, 2, 3, 4]
    assert len(items) == 4
```

### Testing a Real Module

Suppose you have a `calculator.py`:

```python
# calculator.py

class Calculator:
    def add(self, a: float, b: float) -> float:
        return a + b

    def subtract(self, a: float, b: float) -> float:
        return a - b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
```

Your test file:

```python
# test_calculator.py
import pytest
from calculator import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_add_negative():
    calc = Calculator()
    assert calc.add(-1, -1) == -2

def test_subtract():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2

def test_multiply():
    calc = Calculator()
    assert calc.multiply(3, 4) == 12

def test_divide():
    calc = Calculator()
    assert calc.divide(10, 2) == 5.0

def test_divide_by_zero():
    calc = Calculator()
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(10, 0)
```

### Grouping Tests in Classes

You can optionally group tests in classes (no need to inherit from anything):

```python
class TestCalculatorArithmetic:
    def test_add(self):
        calc = Calculator()
        assert calc.add(2, 3) == 5

    def test_subtract(self):
        calc = Calculator()
        assert calc.subtract(5, 3) == 2

class TestCalculatorDivision:
    def test_divide(self):
        calc = Calculator()
        assert calc.divide(10, 2) == 5.0

    def test_divide_by_zero(self):
        calc = Calculator()
        with pytest.raises(ValueError):
            calc.divide(10, 0)
```

**Swift comparison**: This is like having separate `XCTestCase` subclasses, except these
classes do not need to inherit from anything.

---

## 4. Assert Statements -- No Special Methods Needed

### Plain Assert

In pytest, you use Python's built-in `assert` statement for everything:

```python
# Equality
assert result == expected

# Truthiness
assert user.is_active

# Containment
assert "hello" in greeting
assert 42 in numbers

# Identity
assert result is None
assert result is not None

# Type checking
assert isinstance(result, dict)

# Approximate equality (for floats)
assert result == pytest.approx(3.14, abs=0.01)
assert result == pytest.approx(3.14, rel=1e-3)
```

### Comparison With unittest Assertion Methods

| unittest                          | pytest                              |
|-----------------------------------|-------------------------------------|
| `assertEqual(a, b)`              | `assert a == b`                    |
| `assertNotEqual(a, b)`           | `assert a != b`                    |
| `assertTrue(x)`                  | `assert x`                         |
| `assertFalse(x)`                 | `assert not x`                     |
| `assertIs(a, b)`                 | `assert a is b`                    |
| `assertIsNone(x)`                | `assert x is None`                 |
| `assertIn(a, b)`                 | `assert a in b`                    |
| `assertIsInstance(a, b)`         | `assert isinstance(a, b)`         |
| `assertRaises(Exc)`             | `pytest.raises(Exc)`              |
| `assertAlmostEqual(a, b)`       | `assert a == pytest.approx(b)`    |

### Custom Failure Messages

You can add messages to assertions:

```python
assert result == expected, f"Expected {expected}, got {result}"

# Or more descriptive:
assert len(users) > 0, "User list should not be empty after registration"
```

### Comparing Collections

pytest excels at showing diffs for collections:

```python
def test_list_comparison():
    expected = [1, 2, 3, 4, 5]
    actual = [1, 2, 3, 4, 6]
    assert actual == expected
    # Output shows:
    # E       assert [1, 2, 3, 4, 6] == [1, 2, 3, 4, 5]
    # E         At index 4 diff: 6 != 5

def test_dict_comparison():
    expected = {"name": "Alice", "age": 30, "city": "NYC"}
    actual = {"name": "Alice", "age": 31, "city": "NYC"}
    assert actual == expected
    # Output shows exactly which keys differ
```

---

## 5. Test Discovery

pytest automatically discovers tests by following these conventions:

### Default Discovery Rules

1. **Directories**: Recurse into directories (unless excluded)
2. **Files**: Collect files matching `test_*.py` or `*_test.py`
3. **Classes**: Collect classes matching `Test*` (no `__init__` method)
4. **Functions**: Collect functions and methods matching `test_*`

### Customizing Discovery

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
# Where to look for tests
testpaths = ["tests", "integration_tests"]

# File patterns
python_files = ["test_*.py", "check_*.py"]

# Function patterns
python_functions = ["test_*", "check_*"]

# Class patterns
python_classes = ["Test*", "Check*"]
```

### Ignoring Directories

```toml
[tool.pytest.ini_options]
# Directories to ignore
norecursedirs = [".git", "node_modules", "venv", "__pycache__"]
```

**Swift comparison**: In Xcode, test targets are explicitly defined in the project file, and
test classes must subclass XCTestCase. pytest's convention-based discovery is more flexible --
just name things right and they are found automatically.

---

## 6. Fixtures

Fixtures are pytest's answer to setUp/tearDown, but far more powerful. They are
composable, reusable, and can have different scopes.

### Basic Fixture

```python
import pytest
from calculator import Calculator

@pytest.fixture
def calculator():
    """Provide a Calculator instance."""
    return Calculator()

def test_add(calculator):
    assert calculator.add(2, 3) == 5

def test_subtract(calculator):
    assert calculator.subtract(5, 3) == 2
```

How it works: pytest sees that `test_add` has a parameter named `calculator`, looks for a
fixture with that name, calls it, and injects the return value.

### Fixtures With Setup and Teardown

Use `yield` to split setup and teardown:

```python
import pytest
import sqlite3

@pytest.fixture
def db_connection():
    """Create a database connection and clean up after."""
    # Setup
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()

    yield conn  # This is what the test receives

    # Teardown (runs after the test, even if it fails)
    conn.close()

def test_insert_user(db_connection):
    db_connection.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
    db_connection.commit()
    cursor = db_connection.execute("SELECT name FROM users")
    assert cursor.fetchone()[0] == "Alice"
```

**Swift comparison**: This is like `setUp()` and `tearDown()` combined, but the fixture
is a standalone function that can be shared across test files.

### Fixture Scope

Fixtures can have different lifetimes:

```python
@pytest.fixture(scope="function")  # Default: new instance per test
def calculator():
    return Calculator()

@pytest.fixture(scope="class")  # One instance per test class
def shared_calculator():
    return Calculator()

@pytest.fixture(scope="module")  # One instance per test file
def db_connection():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

@pytest.fixture(scope="session")  # One instance for the entire test run
def api_client():
    client = APIClient()
    client.authenticate()
    yield client
    client.close()
```

Scope options:
- `"function"` (default) -- created and destroyed for each test
- `"class"` -- created once per test class
- `"module"` -- created once per test file
- `"package"` -- created once per test package
- `"session"` -- created once for the entire test run

### Fixtures That Use Other Fixtures

Fixtures can depend on other fixtures:

```python
@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

@pytest.fixture
def db_with_schema(db_connection):
    """Database connection with tables created."""
    db_connection.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
    )
    db_connection.commit()
    return db_connection

@pytest.fixture
def db_with_data(db_with_schema):
    """Database with test data pre-populated."""
    db_with_schema.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("Alice", "alice@example.com"),
    )
    db_with_schema.commit()
    return db_with_schema

def test_user_count(db_with_data):
    cursor = db_with_data.execute("SELECT COUNT(*) FROM users")
    assert cursor.fetchone()[0] == 1
```

### conftest.py -- Sharing Fixtures

Place fixtures in `conftest.py` to share them across test files. pytest discovers
`conftest.py` files automatically -- no imports needed.

```
tests/
    conftest.py          # Fixtures available to ALL tests
    test_users.py
    api/
        conftest.py      # Fixtures available to tests in api/
        test_endpoints.py
    db/
        conftest.py      # Fixtures available to tests in db/
        test_queries.py
```

```python
# tests/conftest.py

import pytest

@pytest.fixture
def sample_user():
    return {"name": "Alice", "email": "alice@example.com", "age": 30}

@pytest.fixture
def sample_users():
    return [
        {"name": "Alice", "email": "alice@example.com", "age": 30},
        {"name": "Bob", "email": "bob@example.com", "age": 25},
        {"name": "Charlie", "email": "charlie@example.com", "age": 35},
    ]
```

```python
# tests/test_users.py
# No import needed -- conftest.py fixtures are auto-discovered

def test_user_has_name(sample_user):
    assert "name" in sample_user

def test_users_count(sample_users):
    assert len(sample_users) == 3
```

### Autouse Fixtures

Fixtures that apply to every test automatically:

```python
@pytest.fixture(autouse=True)
def reset_database(db_connection):
    """Clean the database before every test."""
    yield
    db_connection.execute("DELETE FROM users")
    db_connection.commit()

@pytest.fixture(autouse=True)
def set_test_environment(monkeypatch):
    """Ensure tests run in test mode."""
    monkeypatch.setenv("ENVIRONMENT", "test")
```

**Swift comparison**: Autouse fixtures are like putting cleanup logic in
`override func setUp()` on a base test class that all your tests inherit from, but
without the inheritance.

### The request Fixture

The built-in `request` fixture gives you information about the test being run:

```python
@pytest.fixture
def resource(request):
    """Fixture that knows which test is using it."""
    print(f"Setting up resource for: {request.node.name}")
    resource = create_resource()
    yield resource
    print(f"Tearing down resource for: {request.node.name}")
    resource.cleanup()
```

---

## 7. Parametrize

`@pytest.mark.parametrize` lets you run a test with multiple sets of inputs, without
writing separate test functions.

### Basic Parametrize

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(calculator, a, b, expected):
    assert calculator.add(a, b) == expected
```

This generates four separate tests:
```
test_calculator.py::test_add[2-3-5]
test_calculator.py::test_add[0-0-0]
test_calculator.py::test_add[-1-1-0]
test_calculator.py::test_add[100-200-300]
```

### Parametrize With IDs

Give meaningful names to test cases:

```python
@pytest.mark.parametrize("input_str, expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("", ""),
    ("123", "123"),
], ids=["lowercase", "mixed_case", "empty_string", "digits_only"])
def test_upper(input_str, expected):
    assert input_str.upper() == expected
```

Output:
```
test_strings.py::test_upper[lowercase]
test_strings.py::test_upper[mixed_case]
test_strings.py::test_upper[empty_string]
test_strings.py::test_upper[digits_only]
```

### Multiple Parametrize Decorators

Stack decorators to create a cartesian product:

```python
@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", [10, 20])
def test_multiply(calculator, x, y):
    result = calculator.multiply(x, y)
    assert result == x * y
    # Generates: 1*10, 1*20, 2*10, 2*20, 3*10, 3*20
```

### Parametrize With pytest.param

Use `pytest.param` for more control:

```python
@pytest.mark.parametrize("a, b, expected", [
    pytest.param(2, 3, 5, id="positive"),
    pytest.param(-1, -1, -2, id="negative"),
    pytest.param(0, 0, 0, id="zeros"),
    pytest.param(
        1_000_000, 2_000_000, 3_000_000,
        id="large_numbers",
        marks=pytest.mark.slow,  # Apply a marker to this specific case
    ),
])
def test_add(calculator, a, b, expected):
    assert calculator.add(a, b) == expected
```

### Parametrize a Fixture

You can also parametrize fixtures themselves:

```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    """Provide different database backends for testing."""
    db_type = request.param
    if db_type == "sqlite":
        db = SQLiteDB(":memory:")
    elif db_type == "postgres":
        db = PostgresDB("test_db")
    elif db_type == "mysql":
        db = MySQLDB("test_db")
    yield db
    db.close()

def test_insert(database):
    # This test runs 3 times: once for each database backend
    database.insert({"key": "value"})
    assert database.get("key") == "value"
```

**Swift comparison**: XCTest does not have built-in parametrized tests. You typically
write separate test methods or use a loop inside a test. pytest's approach is far
more ergonomic.

---

## 8. Markers

Markers let you categorize tests and control which ones run.

### Built-in Markers

#### skip -- Always Skip

```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass
```

#### skipif -- Conditional Skip

```python
import sys

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Does not run on Windows",
)
def test_unix_specific():
    import pwd
    assert pwd.getpwuid(0).pw_name == "root"

@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="Requires Python 3.10+",
)
def test_match_statement():
    # Uses structural pattern matching
    pass
```

#### xfail -- Expected Failure

```python
@pytest.mark.xfail(reason="Known bug in library v2.1")
def test_known_bug():
    assert buggy_function() == expected_result

@pytest.mark.xfail(strict=True)
def test_must_fail():
    # strict=True means if this test PASSES, it is marked as a failure
    # Useful when you expect something to fail and want to know when it is fixed
    assert broken_function() == "works"
```

### Custom Markers

Define your own markers to categorize tests:

```python
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests that require external services",
    "smoke: marks tests for the smoke test suite",
]
```

```python
# test_api.py
import pytest

@pytest.mark.slow
def test_large_dataset_processing():
    # Takes a long time
    process_million_records()

@pytest.mark.integration
def test_api_connection():
    # Requires actual API access
    response = api.get("/health")
    assert response.status_code == 200

@pytest.mark.smoke
def test_app_starts():
    app = create_app()
    assert app is not None
```

Running with markers:

```bash
# Run only slow tests
pytest -m slow

# Run everything except slow tests
pytest -m "not slow"

# Run smoke and unit tests (but not integration)
pytest -m "smoke or not integration"

# Combine markers
pytest -m "slow and integration"
```

**Swift comparison**: In XCTest you might use `XCTSkipIf()` or
`XCTExpectFailure()`, but there is no built-in marker/tagging system.
Xcode test plans provide some test selection, but pytest markers are
more flexible.

---

## 9. Testing Exceptions

### pytest.raises as a Context Manager

```python
import pytest

def test_divide_by_zero():
    calc = Calculator()
    with pytest.raises(ValueError):
        calc.divide(10, 0)

def test_divide_by_zero_message():
    calc = Calculator()
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(10, 0)

def test_divide_by_zero_details():
    calc = Calculator()
    with pytest.raises(ValueError) as exc_info:
        calc.divide(10, 0)

    # Inspect the exception object
    assert str(exc_info.value) == "Cannot divide by zero"
    assert exc_info.type is ValueError
```

### Testing Multiple Exception Types

```python
def test_invalid_input():
    with pytest.raises((TypeError, ValueError)):
        parse_input(None)
```

### Testing That No Exception Is Raised

```python
def test_valid_input():
    # If this raises, the test fails automatically
    result = parse_input("valid data")
    assert result is not None
```

### Matching Exception Messages With Regex

```python
def test_error_message_format():
    with pytest.raises(ValueError, match=r"Invalid ID: \d+"):
        validate_id(-1)

    with pytest.raises(ValueError, match="must be positive"):
        validate_age(-5)
```

**Swift comparison**: In XCTest, you use `XCTAssertThrowsError` or
`XCTAssertNoThrow`. pytest's context manager syntax is more readable,
especially when you want to inspect the exception after it is raised.

---

## 10. Mocking

Mocking lets you replace parts of your system with fake objects during tests. Python's
`unittest.mock` module works seamlessly with pytest.

### Why Mock?

You mock when you want to:
- Isolate the unit under test from its dependencies
- Avoid hitting external services (APIs, databases) in unit tests
- Control the behavior of dependencies (force errors, specific return values)
- Verify that your code calls dependencies correctly

### Basic Mocking with patch

```python
from unittest.mock import patch, MagicMock

# The module under test
# weather_service.py
import requests

def get_temperature(city: str) -> float:
    response = requests.get(f"https://api.weather.com/temp?city={city}")
    data = response.json()
    return data["temperature"]
```

```python
# test_weather_service.py
from unittest.mock import patch
from weather_service import get_temperature

@patch("weather_service.requests.get")
def test_get_temperature(mock_get):
    # Configure the mock
    mock_response = MagicMock()
    mock_response.json.return_value = {"temperature": 72.5}
    mock_get.return_value = mock_response

    # Call the function under test
    result = get_temperature("NYC")

    # Verify
    assert result == 72.5
    mock_get.assert_called_once_with("https://api.weather.com/temp?city=NYC")
```

### patch as a Context Manager

```python
def test_get_temperature_context_manager():
    with patch("weather_service.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"temperature": 72.5}
        mock_get.return_value = mock_response

        result = get_temperature("NYC")
        assert result == 72.5
```

### patch as a pytest Fixture (Using monkeypatch)

pytest's `monkeypatch` fixture is often preferred for simpler cases:

```python
def test_get_temperature(monkeypatch):
    def mock_get(url):
        response = MagicMock()
        response.json.return_value = {"temperature": 72.5}
        return response

    monkeypatch.setattr("weather_service.requests.get", mock_get)

    result = get_temperature("NYC")
    assert result == 72.5
```

### MagicMock

`MagicMock` creates objects that record how they are used:

```python
from unittest.mock import MagicMock

def test_magic_mock():
    mock = MagicMock()

    # Call it like a function
    mock(1, 2, 3)
    mock.assert_called_once_with(1, 2, 3)

    # Access attributes -- they are auto-created as new MagicMocks
    mock.some_method.return_value = 42
    assert mock.some_method() == 42

    # Chained attributes work too
    mock.db.query.return_value = [{"id": 1}]
    assert mock.db.query() == [{"id": 1}]
```

### side_effect

`side_effect` lets you control what happens when the mock is called:

```python
from unittest.mock import MagicMock

def test_side_effect_exception():
    mock = MagicMock()
    mock.side_effect = ConnectionError("Network down")

    with pytest.raises(ConnectionError):
        mock()

def test_side_effect_function():
    mock = MagicMock()
    mock.side_effect = lambda x: x * 2

    assert mock(3) == 6
    assert mock(5) == 10

def test_side_effect_sequence():
    mock = MagicMock()
    mock.side_effect = [1, 2, 3, StopIteration]

    assert mock() == 1
    assert mock() == 2
    assert mock() == 3
    with pytest.raises(StopIteration):
        mock()
```

### Patching the Right Thing

A common gotcha: you must patch where the name is *looked up*, not where it is *defined*.

```python
# my_module.py
from os.path import exists   # <-- `exists` is now a name in my_module

def check_file(path: str) -> bool:
    return exists(path)
```

```python
# test_my_module.py

# WRONG: patching os.path.exists won't work because my_module already
# imported it under its own name
@patch("os.path.exists")
def test_check_file_wrong(mock_exists):
    mock_exists.return_value = True
    assert check_file("/some/path")  # This might not work!

# RIGHT: patch it where it is looked up
@patch("my_module.exists")
def test_check_file_right(mock_exists):
    mock_exists.return_value = True
    assert check_file("/some/path")  # This works!
```

### Mocking a Class

```python
# user_service.py
from email_client import EmailClient

class UserService:
    def __init__(self, email_client: EmailClient):
        self.email_client = email_client

    def register(self, email: str, name: str) -> dict:
        user = {"email": email, "name": name, "id": generate_id()}
        self.email_client.send_welcome(email, name)
        return user
```

```python
# test_user_service.py
from unittest.mock import MagicMock
from user_service import UserService

def test_register_sends_welcome_email():
    mock_email = MagicMock()
    service = UserService(email_client=mock_email)

    user = service.register("alice@example.com", "Alice")

    mock_email.send_welcome.assert_called_once_with("alice@example.com", "Alice")
    assert user["email"] == "alice@example.com"
```

### Asserting Mock Calls

```python
from unittest.mock import MagicMock, call

mock = MagicMock()
mock(1)
mock(2)
mock(3)

# Was it called?
assert mock.called
assert mock.call_count == 3

# What was it called with?
mock.assert_called_with(3)  # Last call
mock.assert_any_call(2)     # Any call

# Exact call sequence
assert mock.call_args_list == [call(1), call(2), call(3)]

# Was it NOT called with something?
# There is no assert_not_called_with, so use:
assert call(99) not in mock.call_args_list
```

### Async Mocking

For async functions, use `AsyncMock`:

```python
from unittest.mock import AsyncMock, patch

@patch("my_module.fetch_data", new_callable=AsyncMock)
async def test_async_function(mock_fetch):
    mock_fetch.return_value = {"data": "value"}
    result = await fetch_data("url")
    assert result == {"data": "value"}
```

---

## 11. Temporary Files and Directories

pytest provides the `tmp_path` fixture for creating temporary files and directories
that are automatically cleaned up.

### tmp_path

```python
def test_write_and_read_file(tmp_path):
    # tmp_path is a pathlib.Path object pointing to a temporary directory
    file = tmp_path / "test_data.txt"
    file.write_text("Hello, World!")

    assert file.read_text() == "Hello, World!"
    assert file.exists()

def test_create_nested_structure(tmp_path):
    sub_dir = tmp_path / "sub" / "nested"
    sub_dir.mkdir(parents=True)

    config = sub_dir / "config.json"
    config.write_text('{"key": "value"}')

    import json
    data = json.loads(config.read_text())
    assert data["key"] == "value"
```

### tmp_path_factory (Session-Scoped)

For fixtures with broader scope:

```python
@pytest.fixture(scope="session")
def shared_data_dir(tmp_path_factory):
    """Create a temporary directory shared across all tests in the session."""
    data_dir = tmp_path_factory.mktemp("shared_data")
    # Populate with test data
    (data_dir / "users.json").write_text('[{"name": "Alice"}]')
    return data_dir
```

**Swift comparison**: In XCTest, you would use `FileManager.default.temporaryDirectory`
and clean up manually in `tearDown()`. pytest handles cleanup automatically.

---

## 12. Capturing Output

The `capsys` fixture captures stdout and stderr.

### capsys

```python
def test_print_output(capsys):
    print("Hello, World!")
    print("Error!", file=sys.stderr)

    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n"
    assert captured.err == "Error!\n"

def test_greeting(capsys):
    greet("Alice")  # Assume this function prints a greeting

    captured = capsys.readouterr()
    assert "Alice" in captured.out
    assert "Hello" in captured.out
```

### capfd -- File Descriptor Level

For capturing output from C extensions or subprocesses:

```python
def test_low_level_output(capfd):
    os.system("echo 'from subprocess'")
    captured = capfd.readouterr()
    assert "from subprocess" in captured.out
```

### caplog -- Capturing Log Messages

```python
import logging

def test_logging(caplog):
    logger = logging.getLogger("my_app")

    with caplog.at_level(logging.WARNING):
        logger.warning("Something happened")
        logger.error("Something bad happened")

    assert "Something happened" in caplog.text
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[1].levelname == "ERROR"
```

---

## 13. Test Organization Best Practices

### Directory Structure

```
project/
    src/
        myapp/
            __init__.py
            models.py
            services.py
            utils.py
    tests/
        conftest.py              # Shared fixtures
        unit/
            conftest.py          # Unit test fixtures
            test_models.py
            test_utils.py
        integration/
            conftest.py          # Integration test fixtures
            test_services.py
            test_database.py
        e2e/
            test_api.py
        fixtures/
            sample_data.json     # Test data files
```

### Naming Conventions

```python
# Files: test_<module_name>.py
# test_calculator.py
# test_user_service.py

# Functions: test_<method>_<scenario>_<expected_result>
def test_add_positive_numbers_returns_sum():
    ...

def test_add_negative_numbers_returns_negative_sum():
    ...

def test_divide_by_zero_raises_value_error():
    ...

# Classes: Test<ClassName>
class TestCalculator:
    def test_add(self):
        ...

class TestCalculatorEdgeCases:
    def test_add_overflow(self):
        ...
```

### The Arrange-Act-Assert Pattern

```python
def test_user_registration():
    # Arrange -- set up the test data and dependencies
    service = UserService(email_client=MagicMock())
    email = "alice@example.com"
    name = "Alice"

    # Act -- perform the action being tested
    user = service.register(email, name)

    # Assert -- verify the result
    assert user["email"] == email
    assert user["name"] == name
    assert "id" in user
```

### Keeping Tests Independent

Each test should be independent -- never rely on another test's side effects:

```python
# BAD: Tests depend on each other
class TestUserDatabase:
    def test_create_user(self):
        create_user("Alice")  # Creates user in shared state

    def test_get_user(self):
        user = get_user("Alice")  # Assumes test_create_user ran first!
        assert user.name == "Alice"

# GOOD: Each test sets up its own state
class TestUserDatabase:
    def test_create_user(self, db):
        create_user("Alice")
        assert get_user("Alice").name == "Alice"

    def test_get_user(self, db, sample_user):
        # sample_user fixture creates the user
        user = get_user(sample_user.name)
        assert user.name == sample_user.name
```

---

## 14. Coverage with pytest-cov

### Installation

```bash
pip install pytest-cov
```

### Running With Coverage

```bash
# Basic coverage report
pytest --cov=myapp

# With line numbers of missing coverage
pytest --cov=myapp --cov-report=term-missing

# Generate HTML report
pytest --cov=myapp --cov-report=html
# Opens htmlcov/index.html in browser

# Fail if coverage is below threshold
pytest --cov=myapp --cov-fail-under=80
```

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src/myapp"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
fail_under = 80
show_missing = true
```

### What Coverage Tells You (and Does Not)

Coverage measures which lines of code were executed during tests. It does NOT tell you:
- Whether your tests assert the right things
- Whether edge cases are covered
- Whether the code is correct

100% coverage does not mean 100% tested. Aim for meaningful tests, not just line coverage.

**Swift comparison**: Xcode has built-in code coverage (enable in the Test Plan or scheme).
The coverage report appears inline in the editor. pytest-cov provides similar functionality
via terminal or HTML reports.

---

## 15. Test-Driven Development Workflow

TDD with pytest follows the Red-Green-Refactor cycle:

### Step 1: Red -- Write a Failing Test

```python
# test_password_validator.py

def test_valid_password():
    assert validate_password("Str0ng!Pass") is True

def test_too_short():
    assert validate_password("Ab1!") is False

def test_no_uppercase():
    assert validate_password("weakpassword1!") is False

def test_no_digit():
    assert validate_password("NoDigitHere!") is False
```

Run: `pytest` -- all tests fail because `validate_password` does not exist.

### Step 2: Green -- Write Minimal Code to Pass

```python
# password_validator.py

def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in "!@#$%^&*" for c in password):
        return False
    return True
```

Run: `pytest` -- all tests pass.

### Step 3: Refactor -- Improve the Code

```python
import re

def validate_password(password: str) -> bool:
    checks = [
        len(password) >= 8,
        bool(re.search(r"[A-Z]", password)),
        bool(re.search(r"\d", password)),
        bool(re.search(r"[!@#$%^&*]", password)),
    ]
    return all(checks)
```

Run: `pytest` -- all tests still pass. Refactoring is safe.

### TDD Benefits

- Forces you to think about the interface before implementation
- Tests serve as documentation of expected behavior
- Gives confidence when refactoring
- Catches regressions immediately

---

## 16. Advanced Tips

### Using pytest.ini or pyproject.toml Effectively

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
]
filterwarnings = [
    "error",
    "ignore::UserWarning",
]
```

### Useful Plugins

| Plugin            | Purpose                                    |
|-------------------|--------------------------------------------|
| `pytest-xdist`    | Run tests in parallel                      |
| `pytest-cov`      | Code coverage                              |
| `pytest-mock`     | Convenience wrapper around unittest.mock   |
| `pytest-asyncio`  | Test async code                            |
| `pytest-benchmark`| Benchmark performance                      |
| `pytest-freezegun`| Freeze time in tests                       |
| `pytest-randomly` | Randomize test order                       |
| `pytest-timeout`  | Fail tests that take too long              |
| `pytest-sugar`    | Better test output formatting              |
| `pytest-httpx`    | Mock httpx requests                        |

### Writing Reusable Test Helpers

```python
# tests/helpers.py

def assert_user_valid(user: dict) -> None:
    """Assert that a user dictionary has all required fields."""
    assert "id" in user, "User must have an id"
    assert "email" in user, "User must have an email"
    assert "@" in user["email"], "Email must contain @"
    assert "name" in user, "User must have a name"
    assert len(user["name"]) > 0, "Name must not be empty"
```

```python
# tests/test_users.py
from tests.helpers import assert_user_valid

def test_create_user():
    user = create_user("Alice", "alice@example.com")
    assert_user_valid(user)
```

### Freezing Time in Tests

```python
from unittest.mock import patch
from datetime import datetime

def test_created_at():
    fixed_time = datetime(2024, 1, 15, 12, 0, 0)
    with patch("my_module.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

        user = create_user("Alice")
        assert user.created_at == fixed_time
```

### Testing With Environment Variables

```python
def test_config_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("DEBUG", "true")

    config = load_config()
    assert config.database_url == "sqlite:///test.db"
    assert config.debug is True

def test_missing_env_var(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(EnvironmentError):
        load_config()
```

### Snapshot Testing (pytest-snapshot)

```python
def test_api_response(snapshot):
    response = api.get("/users/1")
    snapshot.assert_match(response.json(), "user_response.json")
    # First run: creates the snapshot file
    # Subsequent runs: compares against it
```

---

## Summary

| Concept                | What to Remember                                              |
|------------------------|---------------------------------------------------------------|
| Writing tests          | Functions starting with `test_`, plain `assert`               |
| Fixtures               | `@pytest.fixture`, `yield` for teardown, `conftest.py`        |
| Parametrize            | `@pytest.mark.parametrize` for multiple inputs                |
| Markers                | `@pytest.mark.skip`, `xfail`, custom markers                  |
| Exceptions             | `pytest.raises(ExcType, match="pattern")`                     |
| Mocking                | `unittest.mock.patch`, `MagicMock`, `monkeypatch`             |
| Temp files             | `tmp_path` fixture (pathlib.Path)                             |
| Output capture         | `capsys` for stdout/stderr, `caplog` for logging              |
| Coverage               | `pytest --cov=myapp --cov-report=term-missing`                |
| Discovery              | Name files `test_*.py`, functions `test_*`                    |

---

## Next Steps

- Work through the exercises in `exercises.py`
- Set up pytest in one of your own projects
- Explore the [pytest documentation](https://docs.pytest.org/)
- Try the TDD workflow on a small feature
- Check out `swift_comparison.md` for XCTest vs pytest mappings
