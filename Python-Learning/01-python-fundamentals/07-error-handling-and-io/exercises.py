"""
Module 07 Exercises: Error Handling and I/O
==========================================

15 exercises covering exception handling, file I/O with pathlib,
JSON/CSV processing, logging, and environment variables.

For Swift developers: these exercises bridge do/try/catch -> try/except,
FileManager -> pathlib, Codable -> json module, and os_log -> logging.

Instructions:
- Replace `pass` (or `...`) with your implementation
- Run this file with `python exercises.py` to check your work
- All assert-based tests are at the bottom of the file
"""

import csv
import json
import logging
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


# ============================================================================
# WARM-UP: Basic Exception Handling (Exercises 1-5)
# ============================================================================


def safe_divide(a: float, b: float) -> float | str:
    """Exercise 1: Safe division with error handling.

    Return the result of a / b.
    If b is zero, return the string "Error: division by zero".
    If either argument is not a number (int or float), return "Error: invalid input".

    Swift equivalent: This is like a function returning Result<Double, Error>.

    Examples:
        safe_divide(10, 3)       -> 3.333...
        safe_divide(10, 0)       -> "Error: division by zero"
        safe_divide("10", 3)     -> "Error: invalid input"
    """
    pass


def parse_int_list(raw_values: list[str]) -> list[int]:
    """Exercise 2: Parse a list of strings into integers, skipping invalid ones.

    Given a list of strings, attempt to convert each to an integer.
    Skip any values that cannot be converted (don't raise an error).
    Return the list of successfully converted integers.

    Examples:
        parse_int_list(["1", "2", "three", "4"])  -> [1, 2, 4]
        parse_int_list(["hello", "world"])          -> []
        parse_int_list(["42"])                      -> [42]
    """
    pass


class InsufficientFundsError(Exception):
    """Exercise 3: Custom exception for bank account operations.

    Create a custom exception that stores:
    - balance: the current account balance (float)
    - amount: the attempted withdrawal amount (float)

    The error message should be:
    "Cannot withdraw {amount}: only {balance} available"

    Swift equivalent: This is like defining a custom Error enum case
    with associated values.
    """
    pass


class BankAccount:
    """Exercise 3 (continued): Bank account using the custom exception.

    Implement a simple bank account with:
    - __init__(self, owner: str, balance: float = 0.0)
    - deposit(self, amount: float) -> None -- raises ValueError if amount <= 0
    - withdraw(self, amount: float) -> None -- raises InsufficientFundsError
      if amount > balance, raises ValueError if amount <= 0
    - get_balance(self) -> float
    """

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        pass

    def deposit(self, amount: float) -> None:
        pass

    def withdraw(self, amount: float) -> None:
        pass

    def get_balance(self) -> float:
        pass


def read_file_safely(path: Path) -> str | None:
    """Exercise 4: Read a file with proper error handling.

    Attempt to read and return the text content of the file at `path`.
    - If the file does not exist, return None.
    - If the file cannot be read (permission error, etc.), return None.
    - Use pathlib (not open()) for reading.

    Swift equivalent: try? String(contentsOf: url)

    Examples:
        read_file_safely(Path("/nonexistent"))  -> None
        read_file_safely(existing_file_path)     -> "file contents..."
    """
    pass


def nested_dict_lookup(data: dict, *keys: str) -> object | None:
    """Exercise 5: Safely look up nested dictionary keys using EAFP.

    Given a dictionary and a series of keys, traverse the nested structure
    and return the value. Return None if any key is missing.

    Use EAFP (try/except), NOT LBYL (checking with `in` or `isinstance`).

    Swift equivalent: data["a"]?["b"]?["c"] optional chaining

    Examples:
        data = {"a": {"b": {"c": 42}}}
        nested_dict_lookup(data, "a", "b", "c")  -> 42
        nested_dict_lookup(data, "a", "x", "c")  -> None
        nested_dict_lookup(data, "a")             -> {"b": {"c": 42}}
    """
    pass


# ============================================================================
# CORE: JSON and CSV Processing (Exercises 6-10)
# ============================================================================


def parse_json_config(json_string: str) -> dict:
    """Exercise 6: Parse a JSON configuration string with error handling.

    Parse the JSON string and return the resulting dictionary.
    If the JSON is invalid, raise a ValueError with the message:
    "Invalid configuration: <original error message>"

    Use exception chaining (raise ... from ...).

    Examples:
        parse_json_config('{"debug": true}')  -> {"debug": True}
        parse_json_config('{bad json}')        -> raises ValueError
    """
    pass


@dataclass
class Product:
    """Data class for exercises 7-8."""
    name: str
    price: float
    quantity: int

    def total_value(self) -> float:
        return self.price * self.quantity


def products_to_json(products: list[Product]) -> str:
    """Exercise 7: Serialize a list of Product dataclasses to JSON.

    Convert the list of Products to a JSON string with:
    - 2-space indentation
    - Each product as a dict with keys: name, price, quantity, total_value
    - total_value should be computed from price * quantity

    Note: dataclasses are not JSON-serializable by default. You'll need
    to convert them to dicts manually.

    Swift equivalent: Encoding an array of Codable structs with JSONEncoder.
    """
    pass


def json_to_products(json_string: str) -> list[Product]:
    """Exercise 8: Deserialize JSON string to a list of Products.

    Parse the JSON string and return a list of Product objects.
    The JSON contains an array of objects with keys: name, price, quantity.
    (The total_value key, if present, should be ignored.)

    If a product entry is missing required fields, skip it and continue.
    If the JSON is invalid, raise ValueError with "Invalid JSON".

    Swift equivalent: Decoding with JSONDecoder into [Product].
    """
    pass


def process_csv_data(csv_content: str) -> list[dict[str, str | float]]:
    """Exercise 9: Process CSV content (as a string) into structured data.

    The CSV has columns: name, department, salary
    Parse it and return a list of dictionaries with:
    - name (str): the employee name
    - department (str): the department
    - salary (float): the salary converted to float

    Skip rows where salary is not a valid number.

    Example input:
        "name,department,salary\\nAlice,Engineering,95000\\nBob,Sales,invalid"

    Expected output:
        [{"name": "Alice", "department": "Engineering", "salary": 95000.0}]
    """
    pass


def csv_report_from_dicts(
    data: list[dict[str, object]],
    fieldnames: list[str],
) -> str:
    """Exercise 10: Generate a CSV string from a list of dictionaries.

    Given a list of dictionaries and a list of field names, produce a CSV
    string (including header row).

    Missing keys should be written as empty strings.

    Example:
        data = [{"name": "Alice", "age": 30}, {"name": "Bob"}]
        fieldnames = ["name", "age"]
        Returns: "name,age\\r\\nAlice,30\\r\\nBob,\\r\\n"
    """
    pass


# ============================================================================
# CHALLENGE: Robust File Processing (Exercises 11-13)
# ============================================================================


class FileProcessor:
    """Exercise 11: A robust file processor with logging.

    Implement a class that processes text files with built-in logging:

    - __init__(self, log_level: int = logging.INFO):
        Set up a logger named "FileProcessor" with a StreamHandler.
        Use format: "%(asctime)s [%(levelname)s] %(message)s"

    - read_json(self, path: Path) -> dict | None:
        Read and parse a JSON file. Log the action.
        Return None and log a warning if the file doesn't exist.
        Return None and log an error if the JSON is invalid.

    - write_json(self, path: Path, data: dict) -> bool:
        Write data as pretty JSON (indent=2) to the file.
        Create parent directories if needed.
        Log success. Return True on success, False on failure.
        Log any errors.

    - process_directory(self, dir_path: Path, pattern: str = "*.json") -> list[dict]:
        Find all files matching the pattern in the directory.
        Read each one, skip failures, return list of successfully parsed dicts.
        Log a summary: "Processed X/Y files successfully"
    """

    def __init__(self, log_level: int = logging.INFO) -> None:
        pass

    def read_json(self, path: Path) -> dict | None:
        pass

    def write_json(self, path: Path, data: dict) -> bool:
        pass

    def process_directory(self, dir_path: Path, pattern: str = "*.json") -> list[dict]:
        pass


def transform_file(
    input_path: Path,
    output_path: Path,
    transform_fn: callable,
) -> None:
    """Exercise 12: Safely transform a file using a temp file.

    1. Read the input file
    2. Apply transform_fn to the content (transform_fn takes str, returns str)
    3. Write the result to output_path using a temporary file for safety
       - Write to a NamedTemporaryFile in the same directory as output_path
       - Only move it to the final location if writing succeeds
       - Clean up the temp file if anything goes wrong

    Raise FileNotFoundError if input_path doesn't exist.
    Raise any exception from transform_fn as-is.

    Swift equivalent: Similar to writing atomically with
    Data.WritingOptions.atomic in Swift.
    """
    pass


def load_config_from_env(
    required_keys: list[str],
    optional_keys: dict[str, str] | None = None,
) -> dict[str, str]:
    """Exercise 13: Load configuration from environment variables.

    Load required and optional environment variables into a config dict.

    - required_keys: list of env var names that MUST be set.
      Raise EnvironmentError with message "Missing required environment
      variables: VAR1, VAR2" listing ALL missing keys (not just the first).

    - optional_keys: dict mapping env var names to default values.
      Use the env var value if set, otherwise use the default.

    Return a dict mapping variable names to their values.

    Example:
        os.environ["API_KEY"] = "abc123"
        os.environ["DEBUG"] = "true"
        result = load_config_from_env(
            required_keys=["API_KEY"],
            optional_keys={"DEBUG": "false", "PORT": "8000"},
        )
        # result == {"API_KEY": "abc123", "DEBUG": "true", "PORT": "8000"}
    """
    pass


# ============================================================================
# SWIFT BRIDGE: Translating iOS Patterns (Exercises 14-15)
# ============================================================================


class AppError(Exception):
    """Exercise 14: Build a Swift-style error hierarchy in Python.

    Create an exception hierarchy that mirrors this Swift pattern:

        enum AppError: Error {
            case networkError(URLError)
            case decodingError(String)
            case validationError(field: String, message: String)
            case notFound(resource: String, id: String)
        }

    Implement as Python exception classes:
    - AppError (base) -- already defined
    - NetworkError(AppError) -- stores `url_error: str`
    - DecodingError(AppError) -- stores `detail: str`
    - ValidationError(AppError) -- stores `field: str` and `message: str`
    - NotFoundError(AppError) -- stores `resource: str` and `id: str`

    Each should have a descriptive __str__ (the message passed to super().__init__).
    """
    pass


class NetworkError(AppError):
    """Network-related error with url_error attribute."""
    pass


class DecodingError(AppError):
    """Decoding error with detail attribute."""
    pass


class ValidationError(AppError):
    """Validation error with field and message attributes."""
    pass


class NotFoundError(AppError):
    """Resource not found error with resource and id attributes."""
    pass


def handle_app_errors(func: callable) -> callable:
    """Exercise 15: Create a decorator that handles AppError exceptions.

    Return a wrapper function that:
    1. Calls the original function with all arguments
    2. If it succeeds, returns ("success", result)
    3. If it raises NetworkError, returns ("network_error", str(error))
    4. If it raises ValidationError, returns ("validation_error", str(error))
    5. If it raises NotFoundError, returns ("not_found", str(error))
    6. If it raises any other AppError, returns ("app_error", str(error))
    7. Any non-AppError exception should propagate normally (not caught)

    Swift equivalent: This is like a Result<T, AppError> return type with
    a switch over the error cases.
    """
    pass


# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    # ── Exercise 1: safe_divide ──
    assert safe_divide(10, 3) == 10 / 3
    assert safe_divide(10, 0) == "Error: division by zero"
    assert safe_divide("10", 3) == "Error: invalid input"
    assert safe_divide(10, "3") == "Error: invalid input"
    assert safe_divide(0, 5) == 0.0
    print("Exercise 1 passed: safe_divide")

    # ── Exercise 2: parse_int_list ──
    assert parse_int_list(["1", "2", "three", "4"]) == [1, 2, 4]
    assert parse_int_list(["hello", "world"]) == []
    assert parse_int_list(["42"]) == [42]
    assert parse_int_list([]) == []
    assert parse_int_list(["1", "2", "3"]) == [1, 2, 3]
    print("Exercise 2 passed: parse_int_list")

    # ── Exercise 3: BankAccount with InsufficientFundsError ──
    account = BankAccount("Alice", 100.0)
    assert account.get_balance() == 100.0
    account.deposit(50.0)
    assert account.get_balance() == 150.0
    account.withdraw(30.0)
    assert account.get_balance() == 120.0

    try:
        account.withdraw(200.0)
        assert False, "Should have raised InsufficientFundsError"
    except InsufficientFundsError as e:
        assert e.balance == 120.0
        assert e.amount == 200.0

    try:
        account.deposit(-10)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        account.withdraw(-10)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("Exercise 3 passed: BankAccount + InsufficientFundsError")

    # ── Exercise 4: read_file_safely ──
    assert read_file_safely(Path("/nonexistent/file.txt")) is None

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        tmp_path = Path(f.name)
    assert read_file_safely(tmp_path) == "hello world"
    tmp_path.unlink()
    print("Exercise 4 passed: read_file_safely")

    # ── Exercise 5: nested_dict_lookup ──
    test_data = {"a": {"b": {"c": 42}}, "x": [1, 2, 3]}
    assert nested_dict_lookup(test_data, "a", "b", "c") == 42
    assert nested_dict_lookup(test_data, "a", "b") == {"c": 42}
    assert nested_dict_lookup(test_data, "a", "z", "c") is None
    assert nested_dict_lookup(test_data, "missing") is None
    assert nested_dict_lookup(test_data, "x") == [1, 2, 3]
    print("Exercise 5 passed: nested_dict_lookup")

    # ── Exercise 6: parse_json_config ──
    assert parse_json_config('{"debug": true}') == {"debug": True}
    assert parse_json_config('{"port": 8080}') == {"port": 8080}
    try:
        parse_json_config("{bad json}")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid configuration" in str(e)
        assert e.__cause__ is not None  # Exception chaining
    print("Exercise 6 passed: parse_json_config")

    # ── Exercise 7: products_to_json ──
    products = [
        Product("Widget", 9.99, 100),
        Product("Gadget", 24.99, 50),
    ]
    json_output = products_to_json(products)
    parsed_output = json.loads(json_output)
    assert len(parsed_output) == 2
    assert parsed_output[0]["name"] == "Widget"
    assert parsed_output[0]["total_value"] == 999.0
    assert parsed_output[1]["price"] == 24.99
    print("Exercise 7 passed: products_to_json")

    # ── Exercise 8: json_to_products ──
    json_input = json.dumps([
        {"name": "Widget", "price": 9.99, "quantity": 100},
        {"name": "Gadget", "price": 24.99, "quantity": 50},
        {"name": "Broken"},  # Missing fields -- should be skipped
    ])
    result = json_to_products(json_input)
    assert len(result) == 2
    assert result[0].name == "Widget"
    assert result[1].quantity == 50
    try:
        json_to_products("{bad json}")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid JSON" in str(e)
    print("Exercise 8 passed: json_to_products")

    # ── Exercise 9: process_csv_data ──
    csv_input = "name,department,salary\nAlice,Engineering,95000\nBob,Sales,invalid\nCharlie,HR,75000"
    csv_result = process_csv_data(csv_input)
    assert len(csv_result) == 2
    assert csv_result[0]["name"] == "Alice"
    assert csv_result[0]["salary"] == 95000.0
    assert csv_result[1]["name"] == "Charlie"
    print("Exercise 9 passed: process_csv_data")

    # ── Exercise 10: csv_report_from_dicts ──
    report_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob"},
    ]
    csv_output = csv_report_from_dicts(report_data, ["name", "age"])
    lines = csv_output.strip().split("\r\n")
    assert lines[0] == "name,age"
    assert lines[1] == "Alice,30"
    assert lines[2] == "Bob,"
    print("Exercise 10 passed: csv_report_from_dicts")

    # ── Exercise 11: FileProcessor ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        processor = FileProcessor()

        # write_json
        test_data = {"key": "value", "number": 42}
        assert processor.write_json(tmp / "test.json", test_data) is True

        # read_json
        loaded = processor.read_json(tmp / "test.json")
        assert loaded == test_data

        # read_json with missing file
        assert processor.read_json(tmp / "missing.json") is None

        # write invalid path parent creation
        nested = tmp / "a" / "b" / "c" / "data.json"
        assert processor.write_json(nested, {"nested": True}) is True
        assert processor.read_json(nested) == {"nested": True}

        # process_directory
        processor.write_json(tmp / "a.json", {"file": "a"})
        processor.write_json(tmp / "b.json", {"file": "b"})
        (tmp / "bad.json").write_text("{invalid json}")
        results = processor.process_directory(tmp)
        # Should get test.json, a.json, b.json (3 valid, 1 invalid skipped)
        assert len(results) == 3

    print("Exercise 11 passed: FileProcessor")

    # ── Exercise 12: transform_file ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        input_file = tmp / "input.txt"
        output_file = tmp / "output.txt"
        input_file.write_text("hello world")

        transform_file(input_file, output_file, str.upper)
        assert output_file.read_text() == "HELLO WORLD"

        # Test with failing transform
        def bad_transform(s: str) -> str:
            raise RuntimeError("Transform failed")

        try:
            transform_file(input_file, tmp / "bad_output.txt", bad_transform)
            assert False, "Should have raised RuntimeError"
        except RuntimeError:
            assert not (tmp / "bad_output.txt").exists()

        # Test with missing input
        try:
            transform_file(tmp / "missing.txt", output_file, str.upper)
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass

    print("Exercise 12 passed: transform_file")

    # ── Exercise 13: load_config_from_env ──
    os.environ["TEST_API_KEY"] = "secret123"
    os.environ["TEST_DEBUG"] = "true"
    config = load_config_from_env(
        required_keys=["TEST_API_KEY"],
        optional_keys={"TEST_DEBUG": "false", "TEST_PORT": "8000"},
    )
    assert config["TEST_API_KEY"] == "secret123"
    assert config["TEST_DEBUG"] == "true"
    assert config["TEST_PORT"] == "8000"

    # Test missing required keys
    try:
        load_config_from_env(required_keys=["MISSING_VAR_1", "MISSING_VAR_2"])
        assert False, "Should have raised EnvironmentError"
    except EnvironmentError as e:
        assert "MISSING_VAR_1" in str(e)
        assert "MISSING_VAR_2" in str(e)

    # Cleanup
    del os.environ["TEST_API_KEY"]
    del os.environ["TEST_DEBUG"]
    print("Exercise 13 passed: load_config_from_env")

    # ── Exercise 14: AppError hierarchy ──
    net_err = NetworkError("Connection refused")
    assert isinstance(net_err, AppError)
    assert net_err.url_error == "Connection refused"

    dec_err = DecodingError("Unexpected token at position 5")
    assert isinstance(dec_err, AppError)
    assert dec_err.detail == "Unexpected token at position 5"

    val_err = ValidationError("email", "Invalid email format")
    assert isinstance(val_err, AppError)
    assert val_err.field == "email"
    assert val_err.message == "Invalid email format"

    nf_err = NotFoundError("User", "42")
    assert isinstance(nf_err, AppError)
    assert nf_err.resource == "User"
    assert nf_err.id == "42"
    print("Exercise 14 passed: AppError hierarchy")

    # ── Exercise 15: handle_app_errors decorator ──
    @handle_app_errors
    def fetch_user(user_id: int) -> dict:
        if user_id < 0:
            raise NetworkError("timeout")
        if user_id == 0:
            raise ValidationError("user_id", "must be positive")
        if user_id == 999:
            raise NotFoundError("User", str(user_id))
        if user_id == 1000:
            raise DecodingError("bad response body")
        return {"id": user_id, "name": "Alice"}

    status, result = fetch_user(1)
    assert status == "success"
    assert result == {"id": 1, "name": "Alice"}

    status, result = fetch_user(-1)
    assert status == "network_error"

    status, result = fetch_user(0)
    assert status == "validation_error"

    status, result = fetch_user(999)
    assert status == "not_found"

    status, result = fetch_user(1000)
    assert status == "app_error"  # DecodingError -> falls to generic AppError

    print("Exercise 15 passed: handle_app_errors decorator")

    print("\n" + "=" * 60)
    print("All 15 exercises passed!")
    print("=" * 60)
