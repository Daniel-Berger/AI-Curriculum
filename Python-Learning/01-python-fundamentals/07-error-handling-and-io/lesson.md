# Module 07: Error Handling and I/O

## Overview

This module covers Python's exception system, file I/O with `pathlib`, data serialization
with `json` and `csv`, and operational tooling like `logging`, environment variables, and
temporary files. As a Swift developer, you will find many familiar concepts here --
`try/except` maps to `do/try/catch`, `pathlib` replaces `FileManager`, and the `json`
module stands in for `Codable`. The differences, however, are significant, and mastering
them is essential for writing robust Python code.

---

## Table of Contents

1. [Exception Hierarchy](#1-exception-hierarchy)
2. [try / except / else / finally](#2-try--except--else--finally)
3. [Raising Exceptions](#3-raising-exceptions)
4. [Custom Exceptions](#4-custom-exceptions)
5. [Exception Chaining](#5-exception-chaining)
6. [EAFP vs LBYL](#6-eafp-vs-lbyl)
7. [pathlib -- Modern File Paths](#7-pathlib----modern-file-paths)
8. [json Module](#8-json-module)
9. [csv Module](#9-csv-module)
10. [logging Module](#10-logging-module)
11. [Environment Variables](#11-environment-variables)
12. [tempfile and shutil](#12-tempfile-and-shutil)
13. [Putting It All Together](#13-putting-it-all-together)

---

## 1. Exception Hierarchy

Python's exception hierarchy is a single-rooted class tree. Every exception inherits from
`BaseException`, but the ones you will catch and raise in normal code all inherit from
`Exception`.

```
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── StopIteration
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   ├── OverflowError
    │   └── FloatingPointError
    ├── AttributeError
    ├── EOFError
    ├── ImportError
    │   └── ModuleNotFoundError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── NameError
    │   └── UnboundLocalError
    ├── OSError
    │   ├── FileNotFoundError
    │   ├── FileExistsError
    │   ├── PermissionError
    │   ├── IsADirectoryError
    │   └── NotADirectoryError
    ├── RuntimeError
    │   ├── NotImplementedError
    │   └── RecursionError
    ├── TypeError
    ├── ValueError
    │   └── UnicodeError
    └── Warning
        ├── DeprecationWarning
        ├── FutureWarning
        └── UserWarning
```

### Key Exceptions You Will Use Constantly

```python
# ValueError -- wrong value for correct type
int("hello")  # ValueError: invalid literal for int()

# TypeError -- wrong type entirely
len(42)  # TypeError: object of type 'int' has no len()

# KeyError -- missing dictionary key
d = {"a": 1}
d["b"]  # KeyError: 'b'

# IndexError -- out of range
[1, 2, 3][10]  # IndexError: list index out of range

# AttributeError -- missing attribute/method
"hello".nonexistent()  # AttributeError

# FileNotFoundError -- file does not exist
open("/nonexistent/file.txt")  # FileNotFoundError

# ImportError -- module cannot be imported
from nonexistent_module import something  # ModuleNotFoundError
```

### Swift Comparison

In Swift, errors conform to the `Error` protocol (often via enums). In Python, exceptions
are classes that inherit from `Exception`. There is no equivalent to Swift's typed throws --
any function can raise any exception at any time, and nothing in the signature tells you
what to expect.

```swift
// Swift: explicit error types
enum NetworkError: Error {
    case timeout
    case badResponse(statusCode: Int)
}
```

```python
# Python: class-based exception hierarchy
class NetworkError(Exception):
    """Base exception for network operations."""

class TimeoutError(NetworkError):
    """Raised when a network request times out."""

class BadResponseError(NetworkError):
    """Raised when the server returns an unexpected status."""
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"Bad response: {status_code}")
```

---

## 2. try / except / else / finally

Python's `try` statement has four clauses. Swift developers will recognize `try/catch` but
the `else` clause is uniquely Pythonic.

### Basic try/except

```python
try:
    result = int(user_input)
except ValueError:
    print("That's not a valid integer")
```

### Catching Multiple Exception Types

```python
try:
    value = data[key]
    result = int(value)
except KeyError:
    print(f"Key '{key}' not found")
except ValueError:
    print(f"Value '{value}' is not an integer")
except (TypeError, AttributeError) as e:
    # Catch multiple types in one clause
    print(f"Unexpected error: {e}")
```

### The else Clause

The `else` block runs **only if no exception was raised** in the `try` block. This is
important: it separates "code that might fail" from "code that should run on success."

```python
try:
    value = int(user_input)
except ValueError:
    print("Invalid input")
else:
    # Only runs if int() succeeded -- exceptions here are NOT caught above
    print(f"You entered: {value}")
    process(value)
```

**Why use `else`?** Without it, you would put `process(value)` inside the `try` block, but
then any exception from `process()` would also be caught by the `except` clause, masking
bugs.

### The finally Clause

`finally` always runs, whether an exception occurred or not. It is used for cleanup.

```python
file = open("data.txt")
try:
    data = file.read()
    process(data)
except IOError as e:
    print(f"Read error: {e}")
finally:
    file.close()  # Always runs, even if an exception propagated
```

### The Full Pattern

```python
try:
    # Code that might raise exceptions
    connection = connect_to_database(url)
    data = connection.execute(query)
except ConnectionError as e:
    # Handle specific exception
    logger.error(f"Database connection failed: {e}")
    data = load_fallback_data()
except TimeoutError:
    # Handle another specific exception
    logger.warning("Query timed out, retrying...")
    data = retry_query(connection, query)
except Exception as e:
    # Catch-all for unexpected exceptions (use sparingly)
    logger.exception(f"Unexpected error: {e}")
    raise  # Re-raise after logging
else:
    # Runs only if no exception -- the success path
    logger.info(f"Query returned {len(data)} rows")
finally:
    # Cleanup -- always runs
    if 'connection' in locals():
        connection.close()
```

### Bare except and Exception

```python
# BAD: bare except catches EVERYTHING including KeyboardInterrupt and SystemExit
try:
    do_something()
except:  # Never do this
    pass

# BAD: catching Exception and silencing it
try:
    do_something()
except Exception:
    pass  # Swallowing errors hides bugs

# ACCEPTABLE: catching Exception when you log and re-raise
try:
    do_something()
except Exception:
    logger.exception("Unexpected error")
    raise
```

### The `as` Keyword

Use `as` to bind the exception to a variable:

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error type: {type(e).__name__}")  # ZeroDivisionError
    print(f"Error message: {e}")               # division by zero
    print(f"Error args: {e.args}")             # ('division by zero',)
```

---

## 3. Raising Exceptions

### Basic raise

```python
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Divisor cannot be zero")
    return a / b
```

### Re-raising

```python
try:
    risky_operation()
except ValueError:
    logger.error("Operation failed")
    raise  # Re-raises the SAME exception with original traceback
```

### Conditional Re-raising

```python
try:
    result = parse_config(path)
except FileNotFoundError:
    if path.suffix == ".json":
        result = {}  # Default config for JSON
    else:
        raise  # Re-raise for non-JSON files
```

### raise from (Exception Chaining)

See the next section for details.

---

## 4. Custom Exceptions

### Basic Custom Exception

```python
class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the account balance."""

    def __init__(self, balance: float, amount: float) -> None:
        self.balance = balance
        self.amount = amount
        self.deficit = amount - balance
        super().__init__(
            f"Cannot withdraw ${amount:.2f}: "
            f"balance is ${balance:.2f} "
            f"(${self.deficit:.2f} short)"
        )
```

### Exception Hierarchy for a Library

```python
class AppError(Exception):
    """Base exception for our application."""

class ValidationError(AppError):
    """Raised when input validation fails."""

class DatabaseError(AppError):
    """Raised when a database operation fails."""

class NotFoundError(DatabaseError):
    """Raised when a requested record is not found."""

class DuplicateError(DatabaseError):
    """Raised when attempting to create a duplicate record."""
```

This lets callers choose their level of granularity:

```python
try:
    user = db.get_user(user_id)
except NotFoundError:
    # Handle missing user specifically
    return create_default_user()
except DatabaseError:
    # Handle any database issue
    return fallback_response()
except AppError:
    # Handle any application error
    log_and_alert()
```

### Comparison with Swift Error Enums

Swift uses enums for error types, which gives you exhaustive pattern matching. Python uses
class hierarchies instead, which gives you inheritance-based matching.

```swift
// Swift
enum APIError: Error {
    case unauthorized
    case notFound(resource: String)
    case serverError(code: Int, message: String)
}

do {
    try fetchUser(id: 42)
} catch APIError.notFound(let resource) {
    print("Not found: \(resource)")
} catch APIError.unauthorized {
    refreshToken()
}
```

```python
# Python
class APIError(Exception):
    """Base API exception."""

class UnauthorizedError(APIError):
    """401 Unauthorized."""

class NotFoundError(APIError):
    """404 Not Found."""
    def __init__(self, resource: str) -> None:
        self.resource = resource
        super().__init__(f"Not found: {resource}")

class ServerError(APIError):
    """5xx Server Error."""
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"Server error {code}: {message}")

try:
    fetch_user(42)
except NotFoundError as e:
    print(f"Not found: {e.resource}")
except UnauthorizedError:
    refresh_token()
```

---

## 5. Exception Chaining

Python supports explicit exception chaining with `raise ... from ...`. This preserves the
original exception as the `__cause__` of the new one.

### Explicit Chaining (raise from)

```python
class ConfigError(Exception):
    """Raised when configuration cannot be loaded."""

def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config: {path}") from e
```

When this raises, the traceback shows both exceptions:

```
FileNotFoundError: [Errno 2] No such file or directory: 'config.json'

The above exception was the direct cause of the following exception:

ConfigError: Config file not found: config.json
```

### Suppressing the Chain

Use `from None` to suppress the original exception from the traceback:

```python
try:
    value = int(user_input)
except ValueError:
    raise ValidationError(f"Expected integer, got: {user_input!r}") from None
```

### Implicit Chaining

If you raise an exception inside an `except` block without `from`, Python still records
the original exception as `__context__` (implicit chain):

```python
try:
    result = process(data)
except ProcessingError:
    # This implicitly chains -- the ProcessingError becomes __context__
    raise ReportError("Failed to generate report")
```

---

## 6. EAFP vs LBYL

Python strongly favors **EAFP** (Easier to Ask Forgiveness than Permission) over **LBYL**
(Look Before You Leap). This is the opposite of what you are used to in Swift.

### LBYL (Swift-style)

```python
# LBYL -- checking conditions before acting
if key in dictionary:
    value = dictionary[key]
else:
    value = default

if hasattr(obj, "method"):
    obj.method()

if os.path.exists(filepath):
    with open(filepath) as f:
        data = f.read()
```

### EAFP (Pythonic style)

```python
# EAFP -- just try it, handle failure if it occurs
try:
    value = dictionary[key]
except KeyError:
    value = default

# Even simpler with .get()
value = dictionary.get(key, default)

try:
    obj.method()
except AttributeError:
    pass  # or handle appropriately

try:
    with open(filepath) as f:
        data = f.read()
except FileNotFoundError:
    data = ""
```

### Why Python Prefers EAFP

1. **Race conditions**: Between the check and the action, the state can change (file deleted,
   key removed). EAFP is atomic.
2. **Performance**: In the common case (no error), EAFP avoids the overhead of the check.
   Exceptions are only expensive when actually raised.
3. **Duck typing**: Instead of checking "does this object have method X?", just call it
   and handle the `AttributeError`. This is the foundation of duck typing.

### Swift Comparison

Swift leans toward LBYL with optionals and `guard`:

```swift
// Swift: LBYL with guard
guard let value = dictionary["key"] else {
    return defaultValue
}
process(value)
```

```python
# Python: EAFP
try:
    value = dictionary["key"]
except KeyError:
    value = default_value
process(value)
```

---

## 7. pathlib -- Modern File Paths

`pathlib` is Python's modern, object-oriented file path library. It replaces the older
`os.path` module and is analogous to Swift's `FileManager` + URL path operations.

### Creating Paths

```python
from pathlib import Path

# Current directory
cwd = Path.cwd()
print(cwd)  # /Users/daniel/projects/myapp

# Home directory
home = Path.home()
print(home)  # /Users/daniel

# From string
config_path = Path("/etc/myapp/config.json")

# Building paths with / operator (Python magic!)
data_dir = Path.home() / "Documents" / "data"
report = data_dir / "report.csv"
print(report)  # /Users/daniel/Documents/data/report.csv

# From components
project = Path("src", "models", "user.py")
print(project)  # src/models/user.py
```

### Path Properties

```python
path = Path("/Users/daniel/projects/myapp/data/report.csv")

path.name       # "report.csv"      -- filename with extension
path.stem       # "report"          -- filename without extension
path.suffix     # ".csv"            -- file extension
path.suffixes   # [".csv"]          -- all extensions (e.g., [".tar", ".gz"])
path.parent     # Path("/Users/daniel/projects/myapp/data")
path.parents    # sequence of parent directories
path.parts      # ('/', 'Users', 'daniel', 'projects', 'myapp', 'data', 'report.csv')
path.anchor     # "/"               -- drive + root
path.is_absolute()  # True
```

### Checking Path State

```python
path = Path("some/file.txt")

path.exists()       # Does it exist?
path.is_file()      # Is it a regular file?
path.is_dir()       # Is it a directory?
path.is_symlink()   # Is it a symbolic link?
path.stat()         # os.stat_result (size, timestamps, permissions)
path.stat().st_size # File size in bytes
```

### Reading and Writing Files

```python
from pathlib import Path

# Reading text
content = Path("data.txt").read_text(encoding="utf-8")

# Writing text
Path("output.txt").write_text("Hello, World!\n", encoding="utf-8")

# Reading bytes
raw = Path("image.png").read_bytes()

# Writing bytes
Path("copy.png").write_bytes(raw)

# Line-by-line reading (memory efficient for large files)
with Path("large_file.txt").open(encoding="utf-8") as f:
    for line in f:
        process(line.strip())
```

### Directory Operations

```python
from pathlib import Path

# Create directory (and parents)
Path("output/reports/2024").mkdir(parents=True, exist_ok=True)

# List directory contents
for item in Path(".").iterdir():
    print(f"{'DIR ' if item.is_dir() else 'FILE'}: {item.name}")

# Glob -- find files matching a pattern
for py_file in Path("src").glob("*.py"):
    print(py_file)

# Recursive glob
for py_file in Path("src").rglob("*.py"):
    print(py_file)  # Searches all subdirectories

# Common glob patterns
Path(".").glob("*.txt")           # All .txt files in current dir
Path(".").rglob("*.py")           # All .py files recursively
Path(".").glob("data_*.csv")      # All CSV files starting with "data_"
Path(".").glob("**/*.json")       # Same as rglob("*.json")
```

### Path Manipulation

```python
path = Path("data/report.csv")

# Change extension
new_path = path.with_suffix(".json")   # data/report.json

# Change filename
new_path = path.with_name("summary.csv")  # data/summary.csv

# Change stem (keep extension)
new_path = path.with_stem("backup")  # data/backup.csv (Python 3.9+)

# Resolve to absolute path
abs_path = path.resolve()  # /Users/daniel/projects/myapp/data/report.csv

# Relative path
rel = Path("/Users/daniel/projects/myapp/data").relative_to(
    Path("/Users/daniel/projects")
)
print(rel)  # myapp/data
```

### Renaming and Deleting

```python
from pathlib import Path

# Rename / move
Path("old_name.txt").rename("new_name.txt")

# Replace (overwrite if exists)
Path("source.txt").replace("destination.txt")

# Delete a file
Path("temp.txt").unlink()
Path("temp.txt").unlink(missing_ok=True)  # No error if missing

# Delete an empty directory
Path("empty_dir").rmdir()

# For non-empty directories, use shutil (see Section 12)
```

### Comparison with Swift FileManager

```swift
// Swift: FileManager
let fm = FileManager.default
let home = fm.homeDirectoryForCurrentUser
let docURL = home.appendingPathComponent("Documents")
let exists = fm.fileExists(atPath: docURL.path)
let contents = try String(contentsOf: docURL.appendingPathComponent("data.txt"))
```

```python
# Python: pathlib
home = Path.home()
doc_path = home / "Documents"
exists = doc_path.exists()
contents = (doc_path / "data.txt").read_text()
```

---

## 8. json Module

Python's `json` module handles JSON serialization/deserialization. It is Python's analog to
Swift's `JSONDecoder`/`JSONEncoder` + `Codable`.

### Basic Usage

```python
import json

# Python object -> JSON string (serialization)
data = {"name": "Alice", "age": 30, "scores": [95, 87, 92]}
json_string = json.dumps(data)
print(json_string)  # {"name": "Alice", "age": 30, "scores": [95, 87, 92]}

# Pretty printing
pretty = json.dumps(data, indent=2)
print(pretty)
# {
#   "name": "Alice",
#   "age": 30,
#   "scores": [95, 87, 92]
# }

# JSON string -> Python object (deserialization)
parsed = json.loads(json_string)
print(parsed["name"])  # Alice
print(type(parsed))    # <class 'dict'>
```

### File I/O

```python
import json
from pathlib import Path

# Write JSON to file
data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
Path("data.json").write_text(json.dumps(data, indent=2))

# Or use json.dump() with a file object
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

# Read JSON from file
with open("data.json") as f:
    loaded = json.load(f)

# Or with pathlib
loaded = json.loads(Path("data.json").read_text())
```

### JSON Type Mapping

| JSON Type | Python Type |
|-----------|-------------|
| object    | `dict`      |
| array     | `list`      |
| string    | `str`       |
| number (int) | `int`    |
| number (float) | `float` |
| true/false | `bool`     |
| null      | `None`      |

### Custom Serialization

Not all Python objects are JSON-serializable. You need a custom encoder for dates,
dataclasses, sets, and other types.

```python
import json
from datetime import datetime, date
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class User:
    name: str
    email: str
    created_at: datetime


class CustomEncoder(json.JSONEncoder):
    """Handles types that json.dumps cannot serialize by default."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, set):
            return sorted(list(obj))
        if isinstance(obj, Path):
            return str(obj)
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


# Usage
user = User("Alice", "alice@example.com", datetime(2024, 1, 15, 10, 30))
json_str = json.dumps(user, cls=CustomEncoder, indent=2)
print(json_str)
# {
#   "name": "Alice",
#   "email": "alice@example.com",
#   "created_at": "2024-01-15T10:30:00"
# }
```

### Custom Deserialization with object_hook

```python
import json
from datetime import datetime


def custom_decoder(dct: dict) -> dict:
    """Convert ISO format strings back to datetime objects."""
    for key, value in dct.items():
        if isinstance(value, str):
            try:
                dct[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return dct


json_str = '{"name": "Alice", "created_at": "2024-01-15T10:30:00"}'
data = json.loads(json_str, object_hook=custom_decoder)
print(type(data["created_at"]))  # <class 'datetime.datetime'>
```

### Error Handling with JSON

```python
import json

def safe_parse_json(text: str) -> dict | None:
    """Parse JSON with proper error handling."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}")
        return None

# Examples
safe_parse_json('{"valid": true}')     # {'valid': True}
safe_parse_json('{invalid json}')      # Error message, returns None
safe_parse_json('')                     # Error message, returns None
```

---

## 9. csv Module

The `csv` module reads and writes CSV (Comma-Separated Values) files. There is no direct
Swift equivalent -- in iOS you typically use a third-party library or parse manually.

### Reading CSV

```python
import csv
from pathlib import Path

# Basic reader -- returns rows as lists
with open("data.csv", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)  # First row is usually the header
    for row in reader:
        print(row)  # ['Alice', '30', '95']

# DictReader -- returns rows as dictionaries (usually what you want)
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)  # {'name': 'Alice', 'age': '30', 'score': '95'}
        print(row["name"])  # Alice
```

### Writing CSV

```python
import csv

# Basic writer
with open("output.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age", "score"])  # Header
    writer.writerow(["Alice", 30, 95])
    writer.writerow(["Bob", 25, 87])

# Write multiple rows at once
rows = [
    ["name", "age", "score"],
    ["Alice", 30, 95],
    ["Bob", 25, 87],
]
with open("output.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

# DictWriter -- write from dictionaries
users = [
    {"name": "Alice", "age": 30, "score": 95},
    {"name": "Bob", "age": 25, "score": 87},
]
with open("output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age", "score"])
    writer.writeheader()
    writer.writerows(users)
```

### CSV with Different Delimiters

```python
import csv

# Tab-separated values
with open("data.tsv", newline="") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        print(row)

# Semicolon-separated (common in European locales)
with open("data.csv", newline="") as f:
    reader = csv.reader(f, delimiter=";")
    for row in reader:
        print(row)
```

### CSV Processing Example

```python
import csv
from pathlib import Path


def process_sales_data(input_path: Path, output_path: Path) -> None:
    """Read sales CSV, compute totals, write summary."""
    summaries: dict[str, float] = {}

    with input_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = row["product"]
            revenue = float(row["quantity"]) * float(row["price"])
            summaries[product] = summaries.get(product, 0.0) + revenue

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["product", "total_revenue"])
        writer.writeheader()
        for product, total in sorted(summaries.items()):
            writer.writerow({"product": product, "total_revenue": f"{total:.2f}"})
```

> **Note on `newline=""`**: Always pass `newline=""` when opening CSV files. The `csv`
> module handles newline translation internally, and without this parameter you may get
> extra blank rows on Windows.

---

## 10. logging Module

Python's `logging` module is a professional-grade logging framework. It replaces
`print()` debugging and is analogous to Apple's `os_log` / `Logger` system.

### Why Not print()?

```python
# Bad: print debugging
print(f"DEBUG: processing user {user_id}")
print(f"WARNING: rate limit approaching")
print(f"ERROR: database connection failed")

# Problems:
# - No log levels (can't filter)
# - No timestamps
# - All goes to stdout (can't redirect errors separately)
# - Must remove before production
# - No structured output
```

### Basic Logging

```python
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Get a logger for this module
logger = logging.getLogger(__name__)

# Log at different levels
logger.debug("Detailed diagnostic info")      # Level 10
logger.info("General operational info")        # Level 20
logger.warning("Something unexpected")         # Level 30
logger.error("Something failed")               # Level 40
logger.critical("System is unusable")          # Level 50
```

### Log Levels

| Level    | Value | When to Use |
|----------|:-----:|-------------|
| DEBUG    | 10    | Detailed diagnostic information during development |
| INFO     | 20    | Confirmation that things are working as expected |
| WARNING  | 30    | Something unexpected happened, or may cause a problem soon |
| ERROR    | 40    | An operation failed, but the program can continue |
| CRITICAL | 50    | The program is about to crash or is unusable |

### Formatters

```python
import logging

# Simple format
fmt = "%(levelname)s: %(message)s"

# Detailed format
fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Include file and line number
fmt = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"

# Date format
logging.basicConfig(
    format=fmt,
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
```

### Handlers

Handlers determine **where** log messages go.

```python
import logging
from pathlib import Path

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

# Console handler (INFO and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_fmt = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_fmt)

# File handler (DEBUG and above -- captures everything)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)
file_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_fmt)

# Error file handler (ERROR and above)
error_handler = logging.FileHandler("errors.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(file_fmt)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(error_handler)

# Now:
# - DEBUG messages go to app.log only
# - INFO/WARNING messages go to console AND app.log
# - ERROR/CRITICAL messages go to console, app.log, AND errors.log
```

### Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

# Use lazy formatting (don't format the string if the level is disabled)
logger.debug("Processing user %s with %d items", user_id, item_count)  # Good
logger.debug(f"Processing user {user_id} with {item_count} items")     # Bad (always formats)

# Log exceptions with traceback
try:
    result = risky_operation()
except Exception:
    logger.exception("Operation failed")  # Automatically includes traceback

# Use extra data
logger.info("Order processed", extra={"order_id": order_id, "total": total})

# Structured logging with dictionaries
logger.info("Request completed", extra={
    "method": "POST",
    "path": "/api/users",
    "status": 201,
    "duration_ms": 45,
})
```

### Production Logging Setup

```python
import logging
import logging.handlers
import sys


def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
    """Configure logging for the application."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    ))
    root_logger.addHandler(console)

    # Optional rotating file handler
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
        ))
        root_logger.addHandler(file_handler)


# Usage
setup_logging(level="DEBUG", log_file="app.log")
logger = logging.getLogger(__name__)
logger.info("Application started")
```

---

## 11. Environment Variables

Environment variables are used for configuration that changes between deployments (API keys,
database URLs, debug flags). This is analogous to Xcode's scheme environment variables or
`.xcconfig` files.

### Reading Environment Variables

```python
import os

# Get with default
debug = os.environ.get("DEBUG", "false")
port = int(os.environ.get("PORT", "8000"))

# Get required (raises KeyError if missing)
api_key = os.environ["API_KEY"]  # KeyError if not set

# Check existence
if "DATABASE_URL" in os.environ:
    db_url = os.environ["DATABASE_URL"]

# Get all environment variables (it's a dict-like mapping)
for key, value in os.environ.items():
    if key.startswith("MY_APP_"):
        print(f"{key}={value}")
```

### Setting Environment Variables

```python
import os

# Set for current process and children
os.environ["MY_VAR"] = "my_value"

# Delete
del os.environ["MY_VAR"]

# Or use pop with a default
os.environ.pop("MY_VAR", None)
```

### python-dotenv

The `python-dotenv` package loads variables from a `.env` file into `os.environ`. This is
the Python equivalent of using `.xcconfig` files.

```
# .env file
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=sk-abc123
DEBUG=true
SECRET_KEY=supersecretkey
```

```python
from dotenv import load_dotenv
import os

# Load .env file into os.environ
load_dotenv()  # Looks for .env in current directory and parents

# Now access them normally
db_url = os.environ.get("DATABASE_URL")
api_key = os.environ.get("API_KEY")
debug = os.environ.get("DEBUG", "false").lower() == "true"
```

### Configuration Pattern

```python
import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """Application configuration loaded from environment variables."""
    database_url: str
    api_key: str
    debug: bool = False
    port: int = 8000
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        load_dotenv()
        return cls(
            database_url=os.environ["DATABASE_URL"],
            api_key=os.environ["API_KEY"],
            debug=os.environ.get("DEBUG", "false").lower() == "true",
            port=int(os.environ.get("PORT", "8000")),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )


# Usage
config = Config.from_env()
print(f"Running on port {config.port}, debug={config.debug}")
```

> **Security Note**: Never commit `.env` files to version control. Add `.env` to your
> `.gitignore` file. Provide a `.env.example` with placeholder values instead.

---

## 12. tempfile and shutil

### tempfile -- Temporary Files and Directories

```python
import tempfile
from pathlib import Path

# Create a temporary file (auto-deleted when closed)
with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=True) as f:
    f.write('{"key": "value"}')
    f.flush()
    print(f.name)  # e.g., /tmp/tmpxy3k2q.json
    # File is still accessible here
# File is deleted after the with block

# Create a temporary file that persists
with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
    f.write("name,age\nAlice,30\n")
    temp_path = Path(f.name)
print(f"Temp file at: {temp_path}")
# Remember to clean up: temp_path.unlink()

# Create a temporary directory (auto-deleted when context exits)
with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)
    (tmp_path / "data.txt").write_text("temporary data")
    print(f"Temp dir: {tmpdir}")
    # Use the directory for processing...
# Directory and contents deleted here

# Get the system temp directory
print(tempfile.gettempdir())  # e.g., /tmp
```

### shutil -- High-Level File Operations

```python
import shutil
from pathlib import Path

# Copy a file (preserving metadata)
shutil.copy2("source.txt", "destination.txt")

# Copy a file (without metadata)
shutil.copy("source.txt", "destination.txt")

# Copy an entire directory tree
shutil.copytree("source_dir", "destination_dir")

# Copy directory tree, ignoring patterns
shutil.copytree(
    "source_dir",
    "destination_dir",
    ignore=shutil.ignore_patterns("*.pyc", "__pycache__", ".git"),
)

# Move a file or directory
shutil.move("old_location", "new_location")

# Delete a directory tree (be careful!)
shutil.rmtree("directory_to_delete")

# Delete directory tree, ignoring errors
shutil.rmtree("directory_to_delete", ignore_errors=True)

# Disk usage
usage = shutil.disk_usage("/")
print(f"Total: {usage.total / (1024**3):.1f} GB")
print(f"Used:  {usage.used / (1024**3):.1f} GB")
print(f"Free:  {usage.free / (1024**3):.1f} GB")

# Create archive
shutil.make_archive("backup", "zip", "project_dir")  # Creates backup.zip

# Extract archive
shutil.unpack_archive("backup.zip", "extracted_dir")
```

### Practical Example: Safe File Processing

```python
import shutil
import tempfile
from pathlib import Path


def safe_process_file(input_path: Path, output_path: Path) -> None:
    """Process a file safely using a temp file to avoid corruption.

    If processing fails, the original output (if any) is untouched.
    """
    # Write to a temporary file in the same directory as the output
    # (ensures atomic rename within the same filesystem)
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=output_path.parent,
        suffix=output_path.suffix,
        delete=False,
    ) as tmp:
        tmp_path = Path(tmp.name)
        try:
            # Read input
            data = input_path.read_text()

            # Process
            processed = data.upper()  # Example transformation

            # Write to temp file
            tmp.write(processed)
            tmp.flush()

            # Atomic rename to final destination
            tmp_path.replace(output_path)
        except Exception:
            # Clean up temp file on failure
            tmp_path.unlink(missing_ok=True)
            raise
```

---

## 13. Putting It All Together

Here is a real-world example that combines error handling, file I/O, JSON, CSV, logging,
and environment variables:

```python
"""Process user data from JSON, generate CSV reports, with full error handling."""

import csv
import json
import logging
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# ── Setup ──────────────────────────────────────────────────────────────────────

load_dotenv()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Exceptions ─────────────────────────────────────────────────────────────────

class DataPipelineError(Exception):
    """Base exception for data pipeline operations."""

class DataLoadError(DataPipelineError):
    """Raised when data cannot be loaded."""

class DataValidationError(DataPipelineError):
    """Raised when data fails validation."""


# ── Data Model ─────────────────────────────────────────────────────────────────

@dataclass
class UserRecord:
    name: str
    email: str
    age: int
    score: float

    @classmethod
    def from_dict(cls, data: dict) -> "UserRecord":
        """Create a UserRecord from a dictionary, with validation."""
        try:
            return cls(
                name=str(data["name"]),
                email=str(data["email"]),
                age=int(data["age"]),
                score=float(data["score"]),
            )
        except (KeyError, ValueError, TypeError) as e:
            raise DataValidationError(f"Invalid user data: {data}") from e


# ── Pipeline ───────────────────────────────────────────────────────────────────

def load_users(path: Path) -> list[UserRecord]:
    """Load user records from a JSON file."""
    logger.info("Loading users from %s", path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise DataLoadError(f"File not found: {path}")
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON in {path}: {e}") from e

    users = []
    for i, entry in enumerate(raw):
        try:
            users.append(UserRecord.from_dict(entry))
        except DataValidationError:
            logger.warning("Skipping invalid record at index %d: %s", i, entry)

    logger.info("Loaded %d valid users from %d records", len(users), len(raw))
    return users


def generate_report(users: list[UserRecord], output_path: Path) -> None:
    """Generate a CSV report from user records, safely."""
    logger.info("Generating report: %s", output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file, then atomically move
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=output_path.parent,
        suffix=".csv",
        delete=False,
        newline="",
    ) as tmp:
        tmp_path = Path(tmp.name)
        try:
            writer = csv.DictWriter(
                tmp,
                fieldnames=["name", "email", "age", "score", "grade"],
            )
            writer.writeheader()
            for user in sorted(users, key=lambda u: u.score, reverse=True):
                writer.writerow({
                    "name": user.name,
                    "email": user.email,
                    "age": user.age,
                    "score": user.score,
                    "grade": "A" if user.score >= 90 else "B" if user.score >= 80 else "C",
                })
            tmp.flush()
            tmp_path.replace(output_path)
            logger.info("Report written: %s (%d users)", output_path, len(users))
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise


def main() -> None:
    """Run the data pipeline."""
    data_dir = Path(os.environ.get("DATA_DIR", "data"))
    output_dir = Path(os.environ.get("OUTPUT_DIR", "output"))

    try:
        users = load_users(data_dir / "users.json")
        if not users:
            logger.warning("No valid users found, skipping report")
            return
        generate_report(users, output_dir / "report.csv")
    except DataPipelineError as e:
        logger.error("Pipeline failed: %s", e)
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
```

---

## Key Takeaways

1. **Catch specific exceptions** -- never use bare `except:` or silently swallow errors.
2. **Use `else` in try/except** -- to separate error-prone code from success-path code.
3. **EAFP over LBYL** -- try the operation and handle the exception rather than checking first.
4. **Use `pathlib.Path`** -- not `os.path`. It is the modern, Pythonic way.
5. **Use `logging`** -- not `print()`. Configure it once, use it everywhere.
6. **Use `python-dotenv`** -- for environment-specific configuration.
7. **Use `tempfile`** -- for safe file operations that survive crashes.
8. **Chain exceptions with `from`** -- to preserve the original error context.
9. **Create exception hierarchies** -- for libraries and applications, mirroring your domain.
10. **Always specify `encoding="utf-8"`** -- when reading/writing text files.
