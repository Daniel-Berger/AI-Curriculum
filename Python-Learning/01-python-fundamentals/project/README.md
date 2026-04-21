# Phase 1 Project: CLI Data Analysis Tool

A command-line data analysis tool that reads CSV files, filters data, computes descriptive statistics, and outputs results in formatted tables. This project integrates concepts from all 10 modules of Phase 1.

---

## Learning Objectives

This project reinforces the following Phase 1 concepts:

| Module | Concept Applied |
|--------|----------------|
| 01 - Syntax & Types | Type hints, f-strings, variable annotations |
| 02 - Control Flow | Conditional logic for filtering, match/case |
| 03 - Data Structures | Dicts, lists, comprehensions for data manipulation |
| 04 - Functions & Closures | Higher-order functions, lambda filters, `*args`/`**kwargs` |
| 05 - OOP & Protocols | Classes with `__repr__`, `__str__`, dataclasses, protocols |
| 06 - Advanced Python | Generators for lazy CSV reading, decorators, context managers |
| 07 - Error Handling & I/O | Custom exceptions, file I/O with pathlib, logging |
| 08 - Modules & Tooling | Project structure, imports, `__init__.py`, ruff |
| 09 - Testing with pytest | Fixtures, parametrize, mocking, test organization |
| 10 - Async & Concurrency | (Bonus) Async file reading, concurrent analysis |

---

## Features

- **CSV Reading**: Parse CSV files with automatic type inference (numeric detection)
- **Filtering**: Filter rows by column value with comparison operators (`==`, `!=`, `>`, `<`, `>=`, `<=`, `contains`)
- **Statistics**: Compute mean, median, mode, standard deviation, min, max, and count for numeric columns
- **Formatted Output**: Display results in rich, color-coded terminal tables
- **Logging**: Configurable logging with `--verbose` flag
- **Error Handling**: Graceful handling of missing files, malformed data, and invalid columns

---

## Requirements

- Python 3.11+
- Dependencies (installed via the base `pyproject.toml`):
  - `typer` -- CLI framework (similar to Swift's `ArgumentParser`)
  - `rich` -- Terminal formatting and tables

---

## Usage

```bash
# Show help
python main.py --help

# Analyze all numeric columns in a CSV
python main.py sample_data.csv

# Analyze a specific column
python main.py sample_data.csv --column salary

# Filter rows before analysis
python main.py sample_data.csv --filter "department==Engineering"

# Filter with comparison operators
python main.py sample_data.csv --filter "salary>80000" --column salary

# Use contains for partial string matching
python main.py sample_data.csv --filter "city contains San"

# Enable verbose logging
python main.py sample_data.csv --verbose

# Export results to a file
python main.py sample_data.csv --output results.txt
```

---

## Project Structure

```
project/
├── README.md              # This file
├── main.py                # CLI entry point (typer app)
├── data_analyzer.py       # Core analysis module (classes & functions)
├── test_analyzer.py       # pytest test suite (15+ tests)
└── sample_data.csv        # Sample dataset for testing
```

---

## Running Tests

```bash
# Run all tests
pytest test_analyzer.py -v

# Run with coverage
pytest test_analyzer.py --cov=data_analyzer -v

# Run a specific test
pytest test_analyzer.py::test_statistics_mean -v
```

---

## Swift/iOS Developer Notes

If you are coming from Swift, here are some key parallels in this project:

| Swift Pattern | Python Equivalent Used Here |
|---------------|----------------------------|
| `Codable` struct for CSV rows | `@dataclass` with type hints |
| `Result<Success, Failure>` | Exceptions + `try/except` |
| `CustomStringConvertible` | `__str__` and `__repr__` |
| Guard statements | Early returns with `if not` checks |
| `FileManager` | `pathlib.Path` |
| `XCTest` / `XCTestCase` | `pytest` with fixtures and parametrize |
| Protocol-oriented design | ABC / `typing.Protocol` |
| Closures as filter predicates | Lambda functions and `filter()` |
