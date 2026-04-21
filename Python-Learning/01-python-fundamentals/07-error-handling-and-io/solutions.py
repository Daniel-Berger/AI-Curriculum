"""
Module 07 Solutions: Error Handling and I/O
==========================================

Complete solutions for all 15 exercises.
Each solution includes the Pythonic/idiomatic approach.
"""

import csv
import io
import json
import logging
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from pathlib import Path


# ============================================================================
# WARM-UP: Basic Exception Handling (Exercises 1-5)
# ============================================================================


def safe_divide(a: float, b: float) -> float | str:
    """Exercise 1: Safe division with error handling."""
    try:
        return a / b
    except ZeroDivisionError:
        return "Error: division by zero"
    except TypeError:
        return "Error: invalid input"

    # Pythonic alternative: you could also check types explicitly (LBYL),
    # but EAFP (try/except) is the Python convention.


def parse_int_list(raw_values: list[str]) -> list[int]:
    """Exercise 2: Parse a list of strings into integers, skipping invalid ones."""
    result = []
    for value in raw_values:
        try:
            result.append(int(value))
        except (ValueError, TypeError):
            continue  # Skip invalid entries
    return result

    # Pythonic alternative using a list comprehension with a helper:
    # def _try_int(s):
    #     try:
    #         return int(s)
    #     except (ValueError, TypeError):
    #         return None
    # return [x for x in (try_int(v) for v in raw_values) if x is not None]


class InsufficientFundsError(Exception):
    """Exercise 3: Custom exception for bank account operations."""

    def __init__(self, balance: float, amount: float) -> None:
        self.balance = balance
        self.amount = amount
        super().__init__(f"Cannot withdraw {amount}: only {balance} available")


class BankAccount:
    """Exercise 3 (continued): Bank account using the custom exception."""

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner
        self._balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise InsufficientFundsError(self._balance, amount)
        self._balance -= amount

    def get_balance(self) -> float:
        return self._balance


def read_file_safely(path: Path) -> str | None:
    """Exercise 4: Read a file with proper error handling."""
    try:
        return path.read_text()
    except (FileNotFoundError, PermissionError, OSError):
        return None

    # Note: catching OSError covers FileNotFoundError and PermissionError
    # since they're subclasses, but being explicit improves readability.


def nested_dict_lookup(data: dict, *keys: str) -> object | None:
    """Exercise 5: Safely look up nested dictionary keys using EAFP."""
    try:
        current = data
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError, IndexError):
        return None

    # The TypeError catch handles cases where current is not subscriptable
    # (e.g., trying to index into an int or string).


# ============================================================================
# CORE: JSON and CSV Processing (Exercises 6-10)
# ============================================================================


def parse_json_config(json_string: str) -> dict:
    """Exercise 6: Parse a JSON configuration string with error handling."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid configuration: {e}") from e


@dataclass
class Product:
    """Data class for exercises 7-8."""
    name: str
    price: float
    quantity: int

    def total_value(self) -> float:
        return self.price * self.quantity


def products_to_json(products: list[Product]) -> str:
    """Exercise 7: Serialize a list of Product dataclasses to JSON."""
    data = [
        {
            "name": p.name,
            "price": p.price,
            "quantity": p.quantity,
            "total_value": p.total_value(),
        }
        for p in products
    ]
    return json.dumps(data, indent=2)

    # Pythonic alternative: use dataclasses.asdict() and add computed fields:
    # from dataclasses import asdict
    # data = [asdict(p) | {"total_value": p.total_value()} for p in products]
    # return json.dumps(data, indent=2)


def json_to_products(json_string: str) -> list[Product]:
    """Exercise 8: Deserialize JSON string to a list of Products."""
    try:
        raw = json.loads(json_string)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON")

    products = []
    for entry in raw:
        try:
            products.append(Product(
                name=entry["name"],
                price=float(entry["price"]),
                quantity=int(entry["quantity"]),
            ))
        except (KeyError, ValueError, TypeError):
            continue  # Skip malformed entries
    return products


def process_csv_data(csv_content: str) -> list[dict[str, str | float]]:
    """Exercise 9: Process CSV content (as a string) into structured data."""
    result = []
    reader = csv.DictReader(io.StringIO(csv_content))
    for row in reader:
        try:
            salary = float(row["salary"])
        except (ValueError, TypeError):
            continue  # Skip rows with invalid salary
        result.append({
            "name": row["name"],
            "department": row["department"],
            "salary": salary,
        })
    return result


def csv_report_from_dicts(
    data: list[dict[str, object]],
    fieldnames: list[str],
) -> str:
    """Exercise 10: Generate a CSV string from a list of dictionaries."""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",  # Ignore keys not in fieldnames
    )
    writer.writeheader()
    for row in data:
        # Fill in missing keys with empty strings
        clean_row = {field: row.get(field, "") for field in fieldnames}
        writer.writerow(clean_row)
    return output.getvalue()


# ============================================================================
# CHALLENGE: Robust File Processing (Exercises 11-13)
# ============================================================================


class FileProcessor:
    """Exercise 11: A robust file processor with logging."""

    def __init__(self, log_level: int = logging.INFO) -> None:
        self.logger = logging.getLogger("FileProcessor")
        self.logger.setLevel(log_level)

        # Only add a handler if the logger doesn't already have one
        # (prevents duplicate log messages if multiple instances are created)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            )
            self.logger.addHandler(handler)

    def read_json(self, path: Path) -> dict | None:
        self.logger.info("Reading JSON from %s", path)
        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.logger.warning("File not found: %s", path)
            return None
        except OSError as e:
            self.logger.error("Cannot read file %s: %s", path, e)
            return None

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            self.logger.error("Invalid JSON in %s: %s", path, e)
            return None

    def write_json(self, path: Path, data: dict) -> bool:
        self.logger.info("Writing JSON to %s", path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(data, indent=2) + "\n",
                encoding="utf-8",
            )
            self.logger.info("Successfully wrote %s", path)
            return True
        except OSError as e:
            self.logger.error("Failed to write %s: %s", path, e)
            return False

    def process_directory(self, dir_path: Path, pattern: str = "*.json") -> list[dict]:
        self.logger.info("Processing directory %s with pattern %s", dir_path, pattern)
        results = []
        files = list(dir_path.glob(pattern))
        total = len(files)

        for file_path in files:
            data = self.read_json(file_path)
            if data is not None:
                results.append(data)

        self.logger.info(
            "Processed %d/%d files successfully", len(results), total
        )
        return results


def transform_file(
    input_path: Path,
    output_path: Path,
    transform_fn: callable,
) -> None:
    """Exercise 12: Safely transform a file using a temp file."""
    # Read input (raises FileNotFoundError if missing)
    content = input_path.read_text()

    # Create parent directory for output if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file, then atomically rename
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=output_path.parent,
        suffix=output_path.suffix,
        delete=False,
    ) as tmp:
        tmp_path = Path(tmp.name)
        try:
            transformed = transform_fn(content)
            tmp.write(transformed)
            tmp.flush()
            tmp_path.replace(output_path)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise


def load_config_from_env(
    required_keys: list[str],
    optional_keys: dict[str, str] | None = None,
) -> dict[str, str]:
    """Exercise 13: Load configuration from environment variables."""
    if optional_keys is None:
        optional_keys = {}

    config: dict[str, str] = {}

    # Check for ALL missing required keys before raising
    missing = [key for key in required_keys if key not in os.environ]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    # Load required keys
    for key in required_keys:
        config[key] = os.environ[key]

    # Load optional keys with defaults
    for key, default in optional_keys.items():
        config[key] = os.environ.get(key, default)

    return config


# ============================================================================
# SWIFT BRIDGE: Translating iOS Patterns (Exercises 14-15)
# ============================================================================


class AppError(Exception):
    """Exercise 14: Base application error."""
    pass


class NetworkError(AppError):
    """Network-related error with url_error attribute."""

    def __init__(self, url_error: str) -> None:
        self.url_error = url_error
        super().__init__(f"Network error: {url_error}")


class DecodingError(AppError):
    """Decoding error with detail attribute."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(f"Decoding error: {detail}")


class ValidationError(AppError):
    """Validation error with field and message attributes."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"Validation error on '{field}': {message}")


class NotFoundError(AppError):
    """Resource not found error with resource and id attributes."""

    def __init__(self, resource: str, id: str) -> None:
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} not found: {id}")


def handle_app_errors(func: callable) -> callable:
    """Exercise 15: Create a decorator that handles AppError exceptions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return ("success", result)
        except NetworkError as e:
            return ("network_error", str(e))
        except ValidationError as e:
            return ("validation_error", str(e))
        except NotFoundError as e:
            return ("not_found", str(e))
        except AppError as e:
            return ("app_error", str(e))
        # Non-AppError exceptions propagate normally

    return wrapper


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
        assert e.__cause__ is not None
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
        {"name": "Broken"},
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

        test_data = {"key": "value", "number": 42}
        assert processor.write_json(tmp / "test.json", test_data) is True

        loaded = processor.read_json(tmp / "test.json")
        assert loaded == test_data

        assert processor.read_json(tmp / "missing.json") is None

        nested = tmp / "a" / "b" / "c" / "data.json"
        assert processor.write_json(nested, {"nested": True}) is True
        assert processor.read_json(nested) == {"nested": True}

        processor.write_json(tmp / "a.json", {"file": "a"})
        processor.write_json(tmp / "b.json", {"file": "b"})
        (tmp / "bad.json").write_text("{invalid json}")
        results = processor.process_directory(tmp)
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

        def bad_transform(s: str) -> str:
            raise RuntimeError("Transform failed")

        try:
            transform_file(input_file, tmp / "bad_output.txt", bad_transform)
            assert False, "Should have raised RuntimeError"
        except RuntimeError:
            assert not (tmp / "bad_output.txt").exists()

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

    try:
        load_config_from_env(required_keys=["MISSING_VAR_1", "MISSING_VAR_2"])
        assert False, "Should have raised EnvironmentError"
    except EnvironmentError as e:
        assert "MISSING_VAR_1" in str(e)
        assert "MISSING_VAR_2" in str(e)

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
    assert status == "app_error"

    print("Exercise 15 passed: handle_app_errors decorator")

    print("\n" + "=" * 60)
    print("All 15 exercises passed!")
    print("=" * 60)
