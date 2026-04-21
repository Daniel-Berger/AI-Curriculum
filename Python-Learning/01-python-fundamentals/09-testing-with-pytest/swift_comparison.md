# Swift Comparison: XCTest vs pytest

## Overview

Both XCTest and pytest serve the same purpose -- automated testing -- but they differ
significantly in philosophy. XCTest is class-based, tightly integrated with Xcode, and
relies on special assertion methods. pytest is function-based, convention-driven, and
uses plain `assert`.

---

## At a Glance

| Aspect                  | XCTest (Swift)                          | pytest (Python)                         |
|-------------------------|------------------------------------------|-----------------------------------------|
| Test framework          | Built into Xcode SDK                    | Third-party (`pip install pytest`)      |
| Test structure          | Class inheriting `XCTestCase`           | Functions named `test_*`                |
| Assertions              | `XCTAssert*` family of methods          | Plain `assert` keyword                  |
| Setup/Teardown          | `setUp()` / `tearDown()` overrides      | Fixtures with `@pytest.fixture`         |
| Test discovery          | Xcode test navigator + targets          | Convention-based filename scanning      |
| Parametrized tests      | Not built-in                            | `@pytest.mark.parametrize`              |
| Mocking                 | Third-party (or manual protocols)       | `unittest.mock` (stdlib)                |
| Code coverage           | Xcode scheme settings                   | `pytest-cov` plugin                     |
| Running tests           | Cmd+U in Xcode                          | `pytest` in terminal                    |

---

## Test Structure

### Swift (XCTest)

```swift
import XCTest
@testable import MyApp

class CalculatorTests: XCTestCase {
    var calculator: Calculator!

    override func setUp() {
        super.setUp()
        calculator = Calculator()
    }

    override func tearDown() {
        calculator = nil
        super.tearDown()
    }

    func testAdd() {
        XCTAssertEqual(calculator.add(2, 3), 5)
    }

    func testSubtract() {
        XCTAssertEqual(calculator.subtract(5, 3), 2)
    }
}
```

### Python (pytest)

```python
import pytest
from calculator import Calculator

@pytest.fixture
def calculator():
    return Calculator()

def test_add(calculator):
    assert calculator.add(2, 3) == 5

def test_subtract(calculator):
    assert calculator.subtract(5, 3) == 2
```

**Key differences:**
- No class inheritance required in pytest
- Fixtures replace setUp/tearDown (and are more flexible)
- Plain `assert` instead of `XCTAssertEqual`
- No `@testable import` -- Python modules are importable directly

---

## Assertion Methods

| XCTest                              | pytest                                | Notes                                    |
|-------------------------------------|---------------------------------------|------------------------------------------|
| `XCTAssertEqual(a, b)`             | `assert a == b`                      | Equality check                           |
| `XCTAssertNotEqual(a, b)`          | `assert a != b`                      | Inequality check                         |
| `XCTAssertTrue(x)`                 | `assert x`                           | Truthiness                               |
| `XCTAssertFalse(x)`                | `assert not x`                       | Falsiness                                |
| `XCTAssertNil(x)`                  | `assert x is None`                   | Nil/None check                           |
| `XCTAssertNotNil(x)`               | `assert x is not None`               | Not nil/None                             |
| `XCTAssertGreaterThan(a, b)`       | `assert a > b`                       | Greater than                             |
| `XCTAssertLessThan(a, b)`          | `assert a < b`                       | Less than                                |
| `XCTAssertIdentical(a, b)`         | `assert a is b`                      | Identity (same object)                   |
| `XCTAssertThrowsError(expr)`       | `pytest.raises(Exception)`           | Exception testing                        |
| `XCTAssertNoThrow(expr)`           | Just call the function                | No exception expected                    |
| `XCTAssertEqual(a, b, accuracy:)`  | `assert a == pytest.approx(b)`       | Floating-point comparison                |
| `XCTFail("message")`               | `pytest.fail("message")`             | Force a test failure                     |

### Custom Messages

```swift
// Swift
XCTAssertEqual(result, 42, "Result should be 42 after processing")
```

```python
# Python
assert result == 42, "Result should be 42 after processing"
```

---

## setUp / tearDown vs Fixtures

### Swift: Method Overrides

```swift
class DatabaseTests: XCTestCase {
    var db: Database!

    override func setUp() {
        super.setUp()
        db = Database()
        db.connect()
    }

    override func tearDown() {
        db.disconnect()
        db = nil
        super.tearDown()
    }

    func testInsert() {
        db.insert("key", value: "value")
        XCTAssertEqual(db.get("key"), "value")
    }
}
```

### Python: Fixtures With yield

```python
@pytest.fixture
def db():
    database = Database()
    database.connect()
    yield database          # Test runs here
    database.disconnect()   # Teardown after test

def test_insert(db):
    db.insert("key", "value")
    assert db.get("key") == "value"
```

### Advantages of pytest Fixtures Over setUp/tearDown

| Feature                          | XCTest setUp/tearDown         | pytest Fixtures                        |
|----------------------------------|-------------------------------|----------------------------------------|
| Reuse across test classes        | Base class inheritance        | `conftest.py` (no inheritance needed)  |
| Composability                    | Limited                       | Fixtures can depend on other fixtures  |
| Scope control                    | Per-test only                 | function, class, module, session       |
| Selective use                    | Applies to all tests in class | Only tests that request the fixture    |
| Parametrization                  | Not supported                 | `@pytest.fixture(params=[...])`        |
| Automatic application            | Always runs for class         | `autouse=True` when needed             |

### Fixture Scope -- No XCTest Equivalent

```python
@pytest.fixture(scope="session")
def expensive_resource():
    """Created once for the entire test suite."""
    resource = create_expensive_resource()
    yield resource
    resource.cleanup()

@pytest.fixture(scope="module")
def module_db():
    """Created once per test file."""
    db = Database()
    yield db
    db.close()
```

In XCTest, you might use `override class func setUp()` for class-level setup, but there
is no direct equivalent to module or session scope.

---

## conftest.py -- No XCTest Equivalent

pytest's `conftest.py` lets you share fixtures across files without imports:

```
tests/
    conftest.py          # Fixtures available everywhere
    test_users.py        # Just use the fixture name as a parameter
    test_orders.py
    api/
        conftest.py      # Additional fixtures for API tests
        test_endpoints.py
```

In XCTest, you would create a base test class and inherit from it, or use helper methods.

---

## Parametrized Tests

### Swift: No Built-In Support

```swift
// You have to write separate test methods or loop manually
func testAddPositive() {
    XCTAssertEqual(calculator.add(2, 3), 5)
}

func testAddNegative() {
    XCTAssertEqual(calculator.add(-1, -1), -2)
}

func testAddZero() {
    XCTAssertEqual(calculator.add(0, 0), 0)
}
```

### Python: Built-In Parametrize

```python
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, -1, -2),
    (0, 0, 0),
])
def test_add(calculator, a, b, expected):
    assert calculator.add(a, b) == expected
```

This generates three separate tests from one function. XCTest has no equivalent feature.

---

## Exception Testing

### Swift

```swift
func testDivideByZero() {
    XCTAssertThrowsError(try calculator.divide(10, by: 0)) { error in
        XCTAssertEqual(error as? CalculatorError, .divisionByZero)
    }
}
```

### Python

```python
def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculator.divide(10, 0)
```

```python
# Or with more inspection:
def test_divide_by_zero_details():
    with pytest.raises(ValueError) as exc_info:
        calculator.divide(10, 0)
    assert "Cannot divide by zero" in str(exc_info.value)
```

---

## Async Testing

### Swift (XCTest Expectations)

```swift
func testAsyncFetch() {
    let expectation = XCTestExpectation(description: "Data fetched")

    service.fetchData { result in
        XCTAssertNotNil(result)
        expectation.fulfill()
    }

    wait(for: [expectation], timeout: 5.0)
}

// Swift 5.5+ with async/await:
func testAsyncFetch() async throws {
    let result = try await service.fetchData()
    XCTAssertNotNil(result)
}
```

### Python (pytest-asyncio)

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await service.fetch_data()
    assert result is not None
```

| Swift async testing                       | Python async testing                      |
|-------------------------------------------|-------------------------------------------|
| `XCTestExpectation` + `wait(for:)`        | `@pytest.mark.asyncio` + `await`          |
| `func test...() async throws`            | `async def test_...():`                   |
| Built into XCTest (Swift 5.5+)            | Requires `pytest-asyncio` plugin          |

---

## Mocking

### Swift: Protocol-Based (Manual)

Swift typically uses protocol-based dependency injection for testability:

```swift
protocol EmailSending {
    func send(to: String, subject: String, body: String) -> Bool
}

class MockEmailSender: EmailSending {
    var sendCalled = false
    var lastRecipient: String?

    func send(to: String, subject: String, body: String) -> Bool {
        sendCalled = true
        lastRecipient = to
        return true
    }
}

func testRegistration() {
    let mockEmail = MockEmailSender()
    let service = UserService(emailSender: mockEmail)

    service.register(email: "alice@example.com", name: "Alice")

    XCTAssertTrue(mockEmail.sendCalled)
    XCTAssertEqual(mockEmail.lastRecipient, "alice@example.com")
}
```

### Python: unittest.mock

```python
from unittest.mock import MagicMock

def test_registration():
    mock_email = MagicMock()
    mock_email.send.return_value = True
    service = UserService(email_sender=mock_email)

    service.register("alice@example.com", "Alice")

    mock_email.send.assert_called_once()
    assert mock_email.send.call_args.kwargs["to"] == "alice@example.com"
```

| Mocking aspect            | Swift                                  | Python                                  |
|---------------------------|----------------------------------------|-----------------------------------------|
| Approach                  | Protocol + manual mock class           | `MagicMock` auto-creates everything     |
| Setup effort              | Write a full mock class                | One line: `MagicMock()`                 |
| Verification              | Manual properties (e.g., `sendCalled`) | Built-in: `.assert_called_once()`       |
| Patching existing code    | Difficult without protocols            | `@patch("module.function")`             |
| Type safety               | Full compile-time checking             | Runtime only                            |

---

## Test Organization

### Swift: Xcode Test Targets

```
MyApp/
    MyApp/
        Sources/
            Calculator.swift
    MyAppTests/               # Test target in Xcode project
        CalculatorTests.swift
    MyAppUITests/             # UI test target
        AppUITests.swift
```

- Tests are organized in separate **test targets**
- Discovered via Xcode's **Test Navigator** (diamond icons)
- Run via **Cmd+U** or clicking test diamonds

### Python: Convention-Based

```
my_project/
    src/
        my_project/
            calculator.py
    tests/
        test_calculator.py
        conftest.py
```

- Tests are discovered by **filename pattern** (`test_*.py`)
- Run via `pytest` command in terminal
- No IDE-specific project configuration needed

| Organization aspect       | XCTest / Xcode                         | pytest                                  |
|---------------------------|----------------------------------------|-----------------------------------------|
| Test location             | Separate test target                   | `tests/` directory (convention)         |
| Discovery mechanism       | Xcode project file                     | Filename pattern matching               |
| Running tests             | Cmd+U or Test Navigator                | `pytest` CLI                            |
| Selecting tests           | Test Plan or clicking diamonds         | `-k`, `-m`, or file path               |
| CI/CD                     | `xcodebuild test`                      | `pytest`                                |
| Test filtering            | Xcode Test Plans                       | Markers (`-m "not slow"`)              |
| Parallel execution        | Xcode parallel testing                 | `pytest-xdist` plugin (`-n auto`)      |

---

## Test-Driven Development

The TDD cycle is the same in both languages:

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve the code with tests as a safety net

The difference is tooling speed:
- **Xcode**: Compilation step before tests run (can be slow for large projects)
- **pytest**: No compilation, tests run immediately (Python is interpreted)

---

## Quick Reference: Translating Your XCTest Habits

| What you do in XCTest                        | What to do in pytest                          |
|----------------------------------------------|-----------------------------------------------|
| Create a new XCTestCase subclass             | Create a `test_*.py` file with test functions |
| Override `setUp()`                           | Write a `@pytest.fixture`                     |
| Override `tearDown()`                        | Use `yield` in the fixture                    |
| `XCTAssertEqual(a, b)`                      | `assert a == b`                               |
| `XCTAssertThrowsError { try expr }`         | `with pytest.raises(ErrorType):`              |
| `addTeardownBlock { ... }`                   | Code after `yield` in fixture                 |
| Test Plan for selecting tests                | Markers and `-m` flag                         |
| `@testable import Module`                    | Regular `import` (or `from module import`)    |
| `XCTSkipIf(condition)`                       | `@pytest.mark.skipif(condition)`              |
| `XCTExpectFailure("reason")`                 | `@pytest.mark.xfail(reason="...")`            |
| `measure { ... }` for performance            | `pytest-benchmark` plugin                     |
| Cmd+U to run all tests                       | `pytest` in terminal                          |
| Click diamond to run single test             | `pytest path/to/file.py::test_name`           |
