"""
Module 09: Testing with pytest - Exercises
==========================================

Complete each test function so that it passes when run with pytest.

To run all exercises:
    pytest exercises.py -v

To run a specific exercise:
    pytest exercises.py::test_exercise_01 -v

Prerequisites:
    pip install pytest

For mocking exercises, no additional installs needed (unittest.mock is in stdlib).

NOTE: Some exercises test code defined at the bottom of this file.
Scroll down to see the helper classes and functions being tested.
"""

import pytest
from unittest.mock import patch, MagicMock, call
from typing import Any
from pathlib import Path
import json
import sys


# ============================================================================
# WARM-UP EXERCISES (1-4): Basic test functions, assertions
# ============================================================================

def test_exercise_01_basic_assertions():
    """
    Exercise 01: Basic Assertions (Warm-up)

    Write assertions to verify all of the following:
    1. 2 + 2 equals 4
    2. "hello".upper() equals "HELLO"
    3. 3 is in the list [1, 2, 3, 4, 5]
    4. None is None (use identity check)
    5. isinstance(3.14, float) is True
    """
    pass


def test_exercise_02_list_operations():
    """
    Exercise 02: Testing List Operations (Warm-up)

    Create a list with elements [1, 2, 3].
    Append 4 to the list.
    Insert 0 at index 0.
    Assert:
    1. The list equals [0, 1, 2, 3, 4]
    2. The length is 5
    3. The sum is 10
    4. The max is 4
    """
    pass


def test_exercise_03_string_methods():
    """
    Exercise 03: Testing String Methods (Warm-up)

    Given the string "  Hello, World!  ":
    Assert:
    1. .strip() removes leading/trailing whitespace
    2. .lower() on the stripped version gives "hello, world!"
    3. .split(", ") on the stripped version gives ["Hello", "World!"]
    4. .replace("World", "Python") on stripped gives "Hello, Python!"
    """
    pass


def test_exercise_04_dictionary_operations():
    """
    Exercise 04: Testing Dictionary Operations (Warm-up)

    Create a dict: {"name": "Alice", "age": 30, "city": "NYC"}
    Assert:
    1. "name" is in the dict (key existence)
    2. dict["name"] equals "Alice"
    3. dict.get("country", "Unknown") equals "Unknown"
    4. len(dict) equals 3
    5. list(dict.keys()) contains "age"
    """
    pass


# ============================================================================
# CORE EXERCISES (5-10): Fixtures, parametrize, mocking
# ============================================================================

# --- Fixtures ---

@pytest.fixture
def calculator():
    """
    Exercise 05: Create a Fixture (Core)

    This fixture is provided for you. Use it in test_exercise_05.
    """
    return Calculator()


def test_exercise_05_using_fixtures(calculator):
    """
    Exercise 05: Using Fixtures (Core)

    Using the `calculator` fixture injected as a parameter:
    1. Assert calculator.add(10, 5) equals 15
    2. Assert calculator.subtract(10, 5) equals 5
    3. Assert calculator.multiply(3, 4) equals 12
    4. Assert calculator.divide(10, 2) equals 5.0
    """
    pass


@pytest.fixture
def sample_users():
    """
    Exercise 06: Write a Fixture and Use It (Core)

    Complete this fixture to return a list of user dictionaries.
    Return:
    [
        {"name": "Alice", "age": 30, "active": True},
        {"name": "Bob", "age": 25, "active": False},
        {"name": "Charlie", "age": 35, "active": True},
    ]
    """
    pass


def test_exercise_06_custom_fixture(sample_users):
    """
    Exercise 06: Write a Fixture and Use It (Core)

    Using the sample_users fixture:
    1. Assert there are 3 users
    2. Assert the first user's name is "Alice"
    3. Assert there are exactly 2 active users
       (Hint: use a list comprehension with len())
    4. Assert the average age is 30.0
    """
    pass


# --- Parametrize ---

@pytest.mark.parametrize("input_str, expected", [
    # Exercise 07: Add test cases here
    # Add at least 5 parametrized cases for str.title()
    # str.title() capitalizes the first letter of each word
    # Example: "hello world" -> "Hello World"
    #
    # Include cases for:
    # 1. Two lowercase words
    # 2. All uppercase input
    # 3. Mixed case input
    # 4. Single word
    # 5. Empty string
])
def test_exercise_07_parametrize(input_str: str, expected: str):
    """
    Exercise 07: Parametrized Tests (Core)

    Fill in the parametrize decorator above with test cases for str.title().
    Each test case should be a tuple of (input_string, expected_output).
    """
    assert input_str.title() == expected


@pytest.mark.parametrize("a, b, operation, expected", [
    # Exercise 08: Add test cases here
    # Test the Calculator class with different operations
    # Each case: (a, b, operation_name, expected_result)
    # Include at least 6 cases covering add, subtract, multiply, divide
    #
    # Example: (2, 3, "add", 5)
])
def test_exercise_08_parametrize_calculator(a: float, b: float, operation: str, expected: float):
    """
    Exercise 08: Parametrized Calculator Tests (Core)

    Fill in the parametrize decorator above, then complete the test body.
    Use getattr(calculator, operation) to call the method dynamically.
    Assert the result equals expected.
    """
    pass


# --- Mocking ---

def test_exercise_09_basic_mocking():
    """
    Exercise 09: Basic Mocking (Core)

    The WeatherService.get_temperature() method calls an external API.
    Mock the _fetch_from_api method to return {"temp": 72.5, "unit": "F"}.

    Steps:
    1. Create a WeatherService instance
    2. Use unittest.mock.patch.object to mock the _fetch_from_api method
    3. Assert get_temperature("NYC") returns 72.5
    4. Assert _fetch_from_api was called once with "NYC"
    """
    pass


def test_exercise_10_mock_side_effect():
    """
    Exercise 10: Mock side_effect (Core)

    Test WeatherService.get_temperature() error handling.

    Steps:
    1. Create a WeatherService instance
    2. Mock _fetch_from_api to raise ConnectionError("API unavailable")
    3. Use pytest.raises to verify get_temperature raises ConnectionError
    4. Verify the error message contains "API unavailable"
    """
    pass


# ============================================================================
# CHALLENGE EXERCISES (11-13): Complex mocking, coverage, test design
# ============================================================================

def test_exercise_11_mock_class_dependency():
    """
    Exercise 11: Mock a Class Dependency (Challenge)

    Test the OrderService class (defined below) with a mocked PaymentGateway.

    Steps:
    1. Create a MagicMock for the PaymentGateway
    2. Configure the mock: charge() returns {"status": "success", "transaction_id": "tx_123"}
    3. Create an OrderService with the mock payment gateway
    4. Call place_order("user_1", "item_42", 29.99)
    5. Assert the result has status "confirmed"
    6. Assert the result has the transaction_id "tx_123"
    7. Verify charge was called with "user_1" and 29.99
    8. Verify send_receipt was called once
    """
    pass


def test_exercise_12_testing_with_tmp_path(tmp_path: Path):
    """
    Exercise 12: Testing with Temporary Files (Challenge)

    Test the ConfigManager class (defined below) using tmp_path.

    Steps:
    1. Create a config file in tmp_path called "config.json"
    2. Write this JSON to it: {"database": "sqlite", "debug": true, "port": 8080}
    3. Create a ConfigManager with the path to the config file
    4. Assert config.get("database") equals "sqlite"
    5. Assert config.get("debug") is True
    6. Assert config.get("missing", "default") equals "default"
    7. Call config.set("database", "postgres")
    8. Assert config.get("database") now equals "postgres"
    9. Verify the file was updated by reading it and parsing the JSON
    """
    pass


def test_exercise_13_comprehensive_mock_test():
    """
    Exercise 13: Comprehensive Mocking (Challenge)

    Test the NotificationService class (defined below) end-to-end.

    Scenario: User signs up, gets a welcome email and a push notification.

    Steps:
    1. Create MagicMock instances for EmailSender and PushNotifier
    2. Create NotificationService with both mocks
    3. Call notify_signup("alice@example.com", "Alice")
    4. Verify email_sender.send was called with:
       - to="alice@example.com"
       - subject="Welcome, Alice!"
       - body containing "Alice" (use any_call or check call_args)
    5. Verify push_notifier.notify was called with:
       - user_email="alice@example.com"
       - message containing "welcome"
    6. Assert the result dict has "email_sent" as True and "push_sent" as True
    """
    pass


# ============================================================================
# SWIFT BRIDGE EXERCISES (14-15): XCTest patterns translated to pytest
# ============================================================================

def test_exercise_14_xctest_setup_teardown_pattern():
    """
    Exercise 14: XCTest setUp/tearDown Translated to pytest (Swift Bridge)

    In XCTest, you might write:
        class TestDatabase: XCTestCase {
            var db: Database!
            override func setUp() { db = Database(); db.connect() }
            override func tearDown() { db.disconnect() }
            func testInsert() { ... }
        }

    Translate this to a pytest fixture with yield.

    Steps:
    1. Create a MockDatabase instance (defined below)
    2. Call its connect() method (setup)
    3. Assert it is connected
    4. Yield the database (this is what the test receives)
    5. After yield, call disconnect() (teardown)

    NOTE: Implement this as the inner fixture function below,
    then write assertions in the test body.
    """
    # Implement the fixture inline using a context-manager-like pattern
    db = None  # Replace with actual setup

    # TODO: Create MockDatabase, connect, assert connected, yield

    # After the "yield" equivalent, disconnect
    # For this exercise, since we can't use yield in a test function,
    # simulate it: do setup, test, teardown in sequence.

    # Setup
    # ... your code here ...

    # Test (the "body" after yield)
    # assert db.is_connected is True
    # db.insert("test_key", "test_value")
    # assert db.get("test_key") == "test_value"

    # Teardown
    # ... your code here ...
    # assert db.is_connected is False
    pass


def test_exercise_15_xctest_async_expectation_pattern():
    """
    Exercise 15: XCTest Expectations Translated to pytest (Swift Bridge)

    In XCTest, you test callbacks with expectations:
        func testAsyncFetch() {
            let expectation = XCTestExpectation(description: "Data fetched")
            service.fetch { result in
                XCTAssertNotNil(result)
                expectation.fulfill()
            }
            wait(for: [expectation], timeout: 5.0)
        }

    In Python, callbacks are less common, but when they exist, you can test
    them with MagicMock.

    Steps:
    1. Create a MagicMock callback
    2. Create a DataProcessor instance (defined below)
    3. Call process_with_callback(data=[1, 2, 3], callback=your_mock)
    4. Assert the callback was called once
    5. Get the argument the callback was called with (use .call_args[0][0])
    6. Assert the result has "sum" equal to 6
    7. Assert the result has "count" equal to 3
    """
    pass


# ============================================================================
# HELPER CLASSES AND FUNCTIONS (used by exercises above)
# ============================================================================

class Calculator:
    """A simple calculator for testing exercises."""

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


class WeatherService:
    """Service that fetches weather data from an external API."""

    def _fetch_from_api(self, city: str) -> dict:
        """Simulate an API call. In real code, this would use requests."""
        raise NotImplementedError("This should be mocked in tests")

    def get_temperature(self, city: str) -> float:
        """Get temperature for a city."""
        data = self._fetch_from_api(city)
        return data["temp"]


class PaymentGateway:
    """External payment processing service."""

    def charge(self, user_id: str, amount: float) -> dict:
        raise NotImplementedError("Use mock")

    def send_receipt(self, user_id: str, transaction_id: str) -> None:
        raise NotImplementedError("Use mock")


class OrderService:
    """Service for placing orders, depends on PaymentGateway."""

    def __init__(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway

    def place_order(self, user_id: str, item_id: str, amount: float) -> dict:
        result = self.payment_gateway.charge(user_id, amount)
        if result["status"] == "success":
            self.payment_gateway.send_receipt(user_id, result["transaction_id"])
            return {
                "status": "confirmed",
                "item_id": item_id,
                "transaction_id": result["transaction_id"],
            }
        return {"status": "failed", "item_id": item_id}


class ConfigManager:
    """Manages JSON configuration files."""

    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        with open(self.config_path) as f:
            self._data = json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        with open(self.config_path, "w") as f:
            json.dump(self._data, f, indent=2)


class EmailSender:
    """Email sending service."""

    def send(self, to: str, subject: str, body: str) -> bool:
        raise NotImplementedError("Use mock")


class PushNotifier:
    """Push notification service."""

    def notify(self, user_email: str, message: str) -> bool:
        raise NotImplementedError("Use mock")


class NotificationService:
    """Service that sends notifications via multiple channels."""

    def __init__(self, email_sender: EmailSender, push_notifier: PushNotifier):
        self.email_sender = email_sender
        self.push_notifier = push_notifier

    def notify_signup(self, email: str, name: str) -> dict:
        email_sent = self.email_sender.send(
            to=email,
            subject=f"Welcome, {name}!",
            body=f"Hello {name}, welcome to our platform!",
        )
        push_sent = self.push_notifier.notify(
            user_email=email,
            message=f"A warm welcome to {name}!",
        )
        return {"email_sent": email_sent, "push_sent": push_sent}


class MockDatabase:
    """A mock database for the setUp/tearDown exercise."""

    def __init__(self):
        self.is_connected = False
        self._data: dict[str, str] = {}

    def connect(self) -> None:
        self.is_connected = True

    def disconnect(self) -> None:
        self.is_connected = False
        self._data.clear()

    def insert(self, key: str, value: str) -> None:
        if not self.is_connected:
            raise RuntimeError("Not connected")
        self._data[key] = value

    def get(self, key: str) -> str | None:
        if not self.is_connected:
            raise RuntimeError("Not connected")
        return self._data.get(key)


class DataProcessor:
    """Processes data and calls a callback with the result."""

    def process_with_callback(self, data: list, callback) -> None:
        result = {
            "sum": sum(data),
            "count": len(data),
            "average": sum(data) / len(data) if data else 0,
        }
        callback(result)
