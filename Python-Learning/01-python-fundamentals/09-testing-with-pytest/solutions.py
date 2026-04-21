"""
Module 09: Testing with pytest - Solutions
==========================================

These are the complete solutions for all exercises.
Run with: pytest solutions.py -v

All 15 tests should pass.
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
    """Exercise 01: Basic Assertions"""
    assert 2 + 2 == 4
    assert "hello".upper() == "HELLO"
    assert 3 in [1, 2, 3, 4, 5]
    assert None is None
    assert isinstance(3.14, float)


def test_exercise_02_list_operations():
    """Exercise 02: Testing List Operations"""
    items = [1, 2, 3]
    items.append(4)
    items.insert(0, 0)

    assert items == [0, 1, 2, 3, 4]
    assert len(items) == 5
    assert sum(items) == 10
    assert max(items) == 4


def test_exercise_03_string_methods():
    """Exercise 03: Testing String Methods"""
    original = "  Hello, World!  "

    assert original.strip() == "Hello, World!"
    assert original.strip().lower() == "hello, world!"
    assert original.strip().split(", ") == ["Hello", "World!"]
    assert original.strip().replace("World", "Python") == "Hello, Python!"


def test_exercise_04_dictionary_operations():
    """Exercise 04: Testing Dictionary Operations"""
    data = {"name": "Alice", "age": 30, "city": "NYC"}

    assert "name" in data
    assert data["name"] == "Alice"
    assert data.get("country", "Unknown") == "Unknown"
    assert len(data) == 3
    assert "age" in list(data.keys())


# ============================================================================
# CORE EXERCISES (5-10): Fixtures, parametrize, mocking
# ============================================================================

@pytest.fixture
def calculator():
    """Provide a Calculator instance."""
    return Calculator()


def test_exercise_05_using_fixtures(calculator):
    """Exercise 05: Using Fixtures"""
    assert calculator.add(10, 5) == 15
    assert calculator.subtract(10, 5) == 5
    assert calculator.multiply(3, 4) == 12
    assert calculator.divide(10, 2) == 5.0


@pytest.fixture
def sample_users():
    """Exercise 06: User fixture."""
    return [
        {"name": "Alice", "age": 30, "active": True},
        {"name": "Bob", "age": 25, "active": False},
        {"name": "Charlie", "age": 35, "active": True},
    ]


def test_exercise_06_custom_fixture(sample_users):
    """Exercise 06: Write a Fixture and Use It"""
    assert len(sample_users) == 3
    assert sample_users[0]["name"] == "Alice"
    assert len([u for u in sample_users if u["active"]]) == 2
    assert sum(u["age"] for u in sample_users) / len(sample_users) == 30.0


@pytest.mark.parametrize("input_str, expected", [
    ("hello world", "Hello World"),
    ("HELLO WORLD", "Hello World"),
    ("hElLo WoRlD", "Hello World"),
    ("python", "Python"),
    ("", ""),
])
def test_exercise_07_parametrize(input_str: str, expected: str):
    """Exercise 07: Parametrized Tests"""
    assert input_str.title() == expected


@pytest.mark.parametrize("a, b, operation, expected", [
    (2, 3, "add", 5),
    (-1, -1, "add", -2),
    (10, 3, "subtract", 7),
    (0, 5, "subtract", -5),
    (3, 4, "multiply", 12),
    (10, 2, "divide", 5.0),
])
def test_exercise_08_parametrize_calculator(a: float, b: float, operation: str, expected: float):
    """Exercise 08: Parametrized Calculator Tests"""
    calc = Calculator()
    method = getattr(calc, operation)
    assert method(a, b) == expected


def test_exercise_09_basic_mocking():
    """Exercise 09: Basic Mocking"""
    service = WeatherService()

    with patch.object(service, "_fetch_from_api") as mock_fetch:
        mock_fetch.return_value = {"temp": 72.5, "unit": "F"}

        result = service.get_temperature("NYC")

        assert result == 72.5
        mock_fetch.assert_called_once_with("NYC")


def test_exercise_10_mock_side_effect():
    """Exercise 10: Mock side_effect"""
    service = WeatherService()

    with patch.object(service, "_fetch_from_api") as mock_fetch:
        mock_fetch.side_effect = ConnectionError("API unavailable")

        with pytest.raises(ConnectionError, match="API unavailable"):
            service.get_temperature("NYC")


# ============================================================================
# CHALLENGE EXERCISES (11-13): Complex mocking, coverage, test design
# ============================================================================

def test_exercise_11_mock_class_dependency():
    """Exercise 11: Mock a Class Dependency"""
    mock_gateway = MagicMock()
    mock_gateway.charge.return_value = {
        "status": "success",
        "transaction_id": "tx_123",
    }

    service = OrderService(payment_gateway=mock_gateway)
    result = service.place_order("user_1", "item_42", 29.99)

    assert result["status"] == "confirmed"
    assert result["transaction_id"] == "tx_123"
    mock_gateway.charge.assert_called_once_with("user_1", 29.99)
    mock_gateway.send_receipt.assert_called_once()


def test_exercise_12_testing_with_tmp_path(tmp_path: Path):
    """Exercise 12: Testing with Temporary Files"""
    config_file = tmp_path / "config.json"
    config_data = {"database": "sqlite", "debug": True, "port": 8080}
    config_file.write_text(json.dumps(config_data))

    config = ConfigManager(config_file)

    assert config.get("database") == "sqlite"
    assert config.get("debug") is True
    assert config.get("missing", "default") == "default"

    config.set("database", "postgres")
    assert config.get("database") == "postgres"

    # Verify the file was updated on disk
    updated_data = json.loads(config_file.read_text())
    assert updated_data["database"] == "postgres"


def test_exercise_13_comprehensive_mock_test():
    """Exercise 13: Comprehensive Mocking"""
    mock_email = MagicMock()
    mock_push = MagicMock()

    mock_email.send.return_value = True
    mock_push.notify.return_value = True

    service = NotificationService(
        email_sender=mock_email,
        push_notifier=mock_push,
    )
    result = service.notify_signup("alice@example.com", "Alice")

    # Verify email
    mock_email.send.assert_called_once()
    email_call_kwargs = mock_email.send.call_args
    assert email_call_kwargs == call(
        to="alice@example.com",
        subject="Welcome, Alice!",
        body="Hello Alice, welcome to our platform!",
    )

    # Verify push notification
    mock_push.notify.assert_called_once()
    push_call_kwargs = mock_push.notify.call_args
    assert push_call_kwargs == call(
        user_email="alice@example.com",
        message="A warm welcome to Alice!",
    )

    # Verify result
    assert result["email_sent"] is True
    assert result["push_sent"] is True


# ============================================================================
# SWIFT BRIDGE EXERCISES (14-15): XCTest patterns translated to pytest
# ============================================================================

def test_exercise_14_xctest_setup_teardown_pattern():
    """Exercise 14: XCTest setUp/tearDown Translated to pytest"""
    # Setup (equivalent to Swift's setUp())
    db = MockDatabase()
    db.connect()
    assert db.is_connected is True

    # Test body (equivalent to the test method in Swift)
    db.insert("test_key", "test_value")
    assert db.get("test_key") == "test_value"

    # Teardown (equivalent to Swift's tearDown())
    db.disconnect()
    assert db.is_connected is False


def test_exercise_15_xctest_async_expectation_pattern():
    """Exercise 15: XCTest Expectations Translated to pytest"""
    callback = MagicMock()
    processor = DataProcessor()

    processor.process_with_callback(data=[1, 2, 3], callback=callback)

    callback.assert_called_once()
    result = callback.call_args[0][0]
    assert result["sum"] == 6
    assert result["count"] == 3


# ============================================================================
# HELPER CLASSES AND FUNCTIONS (same as in exercises.py)
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
        raise NotImplementedError("This should be mocked in tests")

    def get_temperature(self, city: str) -> float:
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
    def send(self, to: str, subject: str, body: str) -> bool:
        raise NotImplementedError("Use mock")


class PushNotifier:
    def notify(self, user_email: str, message: str) -> bool:
        raise NotImplementedError("Use mock")


class NotificationService:
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
    def process_with_callback(self, data: list, callback) -> None:
        result = {
            "sum": sum(data),
            "count": len(data),
            "average": sum(data) / len(data) if data else 0,
        }
        callback(result)
