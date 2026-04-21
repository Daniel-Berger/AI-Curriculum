"""Core data analysis module.

Provides classes for reading CSV files, filtering rows, and computing
descriptive statistics. Designed to demonstrate Python fundamentals
for developers coming from Swift/iOS.

Swift parallels:
    - CSVReader  ~  a Codable-based JSON/CSV decoder
    - DataFilter ~  NSPredicate / Collection.filter { }
    - StatisticsCalculator ~  vDSP / Accelerate statistical functions
    - DataAnalysisError hierarchy ~  enum MyError: Error { }
"""

from __future__ import annotations

import csv
import logging
import math
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom Exceptions  (Module 07 -- Error Handling)
# ---------------------------------------------------------------------------

class DataAnalysisError(Exception):
    """Base exception for the data analysis module."""


class FileNotFoundError_(DataAnalysisError):
    """Raised when the specified CSV file does not exist."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"File not found: {path}")


class EmptyDataError(DataAnalysisError):
    """Raised when a CSV file contains no data rows."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"No data rows found in: {path}")


class InvalidColumnError(DataAnalysisError):
    """Raised when a requested column does not exist in the data."""

    def __init__(self, column: str, available: list[str]) -> None:
        self.column = column
        self.available = available
        super().__init__(
            f"Column '{column}' not found. Available columns: {available}"
        )


class InvalidFilterError(DataAnalysisError):
    """Raised when a filter expression cannot be parsed."""

    def __init__(self, expression: str, reason: str = "") -> None:
        self.expression = expression
        msg = f"Invalid filter expression: '{expression}'"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


# ---------------------------------------------------------------------------
# Enums and Protocols  (Module 05 -- OOP & Protocols)
# ---------------------------------------------------------------------------

class ComparisonOperator(Enum):
    """Supported comparison operators for filtering."""

    EQ = "=="
    NE = "!="
    GT = ">"
    LT = "<"
    GE = ">="
    LE = "<="
    CONTAINS = "contains"


class Analyzable(Protocol):
    """Protocol for objects that can provide numeric data for analysis.

    In Swift terms, this is similar to defining:
        protocol Analyzable {
            var values: [Double] { get }
        }
    """

    @property
    def values(self) -> list[float]: ...


# ---------------------------------------------------------------------------
# Data Classes  (Module 05, 01 -- Dataclasses, Type Hints)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FilterCriteria:
    """Represents a parsed filter expression.

    Attributes:
        column: The column name to filter on.
        operator: The comparison operator.
        value: The value to compare against.
    """

    column: str
    operator: ComparisonOperator
    value: str

    def __str__(self) -> str:
        return f"{self.column} {self.operator.value} {self.value}"


@dataclass
class StatisticsResult:
    """Container for computed statistics on a single column.

    Similar to a Swift struct with computed properties, but here
    all values are pre-computed and stored.
    """

    column_name: str
    count: int
    mean: float
    median: float
    mode: float | None
    std_dev: float
    min_value: float
    max_value: float

    def __str__(self) -> str:
        mode_str = f"{self.mode:.2f}" if self.mode is not None else "N/A"
        return (
            f"Statistics for '{self.column_name}':\n"
            f"  Count:    {self.count}\n"
            f"  Mean:     {self.mean:.2f}\n"
            f"  Median:   {self.median:.2f}\n"
            f"  Mode:     {mode_str}\n"
            f"  Std Dev:  {self.std_dev:.2f}\n"
            f"  Min:      {self.min_value:.2f}\n"
            f"  Max:      {self.max_value:.2f}"
        )

    def __repr__(self) -> str:
        return (
            f"StatisticsResult(column_name={self.column_name!r}, "
            f"count={self.count}, mean={self.mean:.2f})"
        )


# Type alias -- a row is a dict mapping column names to string values.
Row = dict[str, str]


# ---------------------------------------------------------------------------
# CSVReader  (Modules 03, 06, 07 -- Data Structures, Generators, I/O)
# ---------------------------------------------------------------------------

class CSVReader:
    """Reads and parses CSV files into a list of row dictionaries.

    Usage:
        reader = CSVReader(Path("data.csv"))
        rows = reader.read()          # eager -- all rows in memory
        for row in reader.iter_rows(): # lazy -- generator-based

    Swift parallel: Think of this as a custom Decoder that reads CSV
    instead of JSON, returning [Dictionary<String, String>].
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self._headers: list[str] = []
        self._rows: list[Row] = []
        self._is_loaded = False

    @property
    def headers(self) -> list[str]:
        """Column headers from the CSV file."""
        if not self._is_loaded:
            self.read()
        return list(self._headers)

    @property
    def row_count(self) -> int:
        """Number of data rows (excluding header)."""
        if not self._is_loaded:
            self.read()
        return len(self._rows)

    def read(self) -> list[Row]:
        """Read the entire CSV file into memory.

        Returns:
            A list of dictionaries, one per row.

        Raises:
            FileNotFoundError_: If the file does not exist.
            EmptyDataError: If the file has headers but no data rows.
        """
        if not self.file_path.exists():
            raise FileNotFoundError_(self.file_path)

        logger.info("Reading CSV file: %s", self.file_path)

        with self.file_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is None:
                raise EmptyDataError(self.file_path)

            self._headers = list(reader.fieldnames)
            self._rows = list(reader)

        if not self._rows:
            raise EmptyDataError(self.file_path)

        self._is_loaded = True
        logger.info(
            "Loaded %d rows with columns: %s", len(self._rows), self._headers
        )
        return list(self._rows)

    def iter_rows(self):
        """Lazily yield rows from the CSV file (generator).

        This avoids loading the entire file into memory -- useful for
        large datasets. In Swift terms, this is like a LazySequence.

        Yields:
            One Row dictionary per CSV line.
        """
        if not self.file_path.exists():
            raise FileNotFoundError_(self.file_path)

        with self.file_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is None:
                raise EmptyDataError(self.file_path)

            self._headers = list(reader.fieldnames)
            for row in reader:
                yield row

    def __repr__(self) -> str:
        status = "loaded" if self._is_loaded else "not loaded"
        return f"CSVReader(file_path={self.file_path!r}, status={status})"


# ---------------------------------------------------------------------------
# DataFilter  (Modules 02, 04 -- Control Flow, Functions & Closures)
# ---------------------------------------------------------------------------

class DataFilter:
    """Filters rows based on column values and comparison operators.

    Swift parallel: Similar to using NSPredicate or
    collection.filter { $0.salary > 100_000 }.
    """

    # Operators ordered so that two-char operators are checked first.
    _OPERATORS_BY_LENGTH: list[tuple[str, ComparisonOperator]] = [
        (">=", ComparisonOperator.GE),
        ("<=", ComparisonOperator.LE),
        ("!=", ComparisonOperator.NE),
        ("==", ComparisonOperator.EQ),
        (">", ComparisonOperator.GT),
        ("<", ComparisonOperator.LT),
    ]

    @staticmethod
    def parse_filter(expression: str) -> FilterCriteria:
        """Parse a filter string like ``"salary>80000"`` or ``"city contains San"``.

        Returns:
            A FilterCriteria dataclass instance.

        Raises:
            InvalidFilterError: If the expression cannot be parsed.
        """
        expression = expression.strip()
        if not expression:
            raise InvalidFilterError(expression, "empty expression")

        # Check for 'contains' first (word-based operator).
        if " contains " in expression:
            parts = expression.split(" contains ", maxsplit=1)
            if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
                raise InvalidFilterError(expression, "invalid 'contains' syntax")
            return FilterCriteria(
                column=parts[0].strip(),
                operator=ComparisonOperator.CONTAINS,
                value=parts[1].strip(),
            )

        # Try symbol-based operators.
        for symbol, op in DataFilter._OPERATORS_BY_LENGTH:
            if symbol in expression:
                parts = expression.split(symbol, maxsplit=1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    return FilterCriteria(
                        column=parts[0].strip(),
                        operator=op,
                        value=parts[1].strip(),
                    )

        raise InvalidFilterError(
            expression,
            "must be in the form 'column==value', 'column>value', "
            "or 'column contains value'",
        )

    @staticmethod
    def apply_filter(
        rows: list[Row],
        criteria: FilterCriteria,
        available_columns: list[str],
    ) -> list[Row]:
        """Filter rows based on the given criteria.

        Args:
            rows: The data rows to filter.
            criteria: The parsed filter criteria.
            available_columns: Valid column names (for validation).

        Returns:
            A new list containing only the rows that match.

        Raises:
            InvalidColumnError: If the filter column is not in the data.
        """
        if criteria.column not in available_columns:
            raise InvalidColumnError(criteria.column, available_columns)

        logger.info("Applying filter: %s", criteria)

        # Build a predicate function -- closures in action (Module 04).
        predicate = DataFilter._build_predicate(criteria)

        # Use list comprehension with the predicate (Module 03).
        filtered = [row for row in rows if predicate(row)]
        logger.info(
            "Filter matched %d of %d rows", len(filtered), len(rows)
        )
        return filtered

    @staticmethod
    def _build_predicate(criteria: FilterCriteria):
        """Build and return a predicate function (closure) for the criteria.

        This demonstrates higher-order functions and closures, which are
        the Python equivalent of Swift's trailing closure syntax:
            array.filter { $0.age > 30 }
        """
        col = criteria.column
        op = criteria.operator
        raw_value = criteria.value

        match op:
            case ComparisonOperator.CONTAINS:
                return lambda row: raw_value.lower() in row.get(col, "").lower()
            case ComparisonOperator.EQ:
                return lambda row: _compare_values(row.get(col, ""), raw_value) == 0
            case ComparisonOperator.NE:
                return lambda row: _compare_values(row.get(col, ""), raw_value) != 0
            case ComparisonOperator.GT:
                return lambda row: _compare_values(row.get(col, ""), raw_value) > 0
            case ComparisonOperator.LT:
                return lambda row: _compare_values(row.get(col, ""), raw_value) < 0
            case ComparisonOperator.GE:
                return lambda row: _compare_values(row.get(col, ""), raw_value) >= 0
            case ComparisonOperator.LE:
                return lambda row: _compare_values(row.get(col, ""), raw_value) <= 0


def _compare_values(cell_value: str, filter_value: str) -> int:
    """Compare two values, attempting numeric comparison first.

    Returns:
        Negative if cell < filter, 0 if equal, positive if cell > filter.
    """
    try:
        cell_num = float(cell_value)
        filter_num = float(filter_value)
        if cell_num < filter_num:
            return -1
        if cell_num > filter_num:
            return 1
        return 0
    except ValueError:
        # Fall back to case-insensitive string comparison.
        cell_lower = cell_value.lower()
        filter_lower = filter_value.lower()
        if cell_lower < filter_lower:
            return -1
        if cell_lower > filter_lower:
            return 1
        return 0


# ---------------------------------------------------------------------------
# StatisticsCalculator  (Modules 03, 04 -- Data Structures, Functions)
# ---------------------------------------------------------------------------

class StatisticsCalculator:
    """Computes descriptive statistics for numeric data columns.

    Swift parallel: Similar to using vDSP/Accelerate functions
    or writing extension methods on Array<Double>.
    """

    @staticmethod
    def extract_numeric_values(
        rows: list[Row], column: str
    ) -> list[float]:
        """Extract numeric values from a column, skipping non-numeric entries.

        Args:
            rows: The data rows.
            column: The column name to extract.

        Returns:
            A list of float values from that column.
        """
        values: list[float] = []
        skipped = 0
        for row in rows:
            raw = row.get(column, "").strip()
            if not raw:
                skipped += 1
                continue
            try:
                values.append(float(raw))
            except ValueError:
                skipped += 1
                logger.debug(
                    "Skipping non-numeric value in column '%s': %r",
                    column,
                    raw,
                )
        if skipped:
            logger.info(
                "Skipped %d non-numeric values in column '%s'",
                skipped,
                column,
            )
        return values

    @staticmethod
    def compute(
        rows: list[Row],
        column: str,
        available_columns: list[str],
    ) -> StatisticsResult:
        """Compute descriptive statistics for a single column.

        Args:
            rows: The data rows.
            column: The column to analyze.
            available_columns: Valid column names (for validation).

        Returns:
            A StatisticsResult dataclass with all computed metrics.

        Raises:
            InvalidColumnError: If the column is not in the data.
            DataAnalysisError: If no numeric values are found.
        """
        if column not in available_columns:
            raise InvalidColumnError(column, available_columns)

        values = StatisticsCalculator.extract_numeric_values(rows, column)
        if not values:
            raise DataAnalysisError(
                f"No numeric values found in column '{column}'"
            )

        return StatisticsResult(
            column_name=column,
            count=len(values),
            mean=StatisticsCalculator.mean(values),
            median=StatisticsCalculator.median(values),
            mode=StatisticsCalculator.mode(values),
            std_dev=StatisticsCalculator.std_dev(values),
            min_value=min(values),
            max_value=max(values),
        )

    # -- Individual statistic methods (all pure functions) -----------------

    @staticmethod
    def mean(values: list[float]) -> float:
        """Arithmetic mean."""
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def median(values: list[float]) -> float:
        """Median value (middle element of the sorted list)."""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
        return sorted_vals[mid]

    @staticmethod
    def mode(values: list[float]) -> float | None:
        """Mode (most frequently occurring value).

        Returns None if all values are unique (no meaningful mode).
        """
        if not values:
            return None
        counter = Counter(values)
        most_common = counter.most_common()
        # If all values appear exactly once, there is no meaningful mode.
        if most_common[0][1] == 1:
            return None
        return most_common[0][0]

    @staticmethod
    def std_dev(values: list[float]) -> float:
        """Population standard deviation."""
        if len(values) < 2:
            return 0.0
        avg = StatisticsCalculator.mean(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    @staticmethod
    def detect_numeric_columns(rows: list[Row], headers: list[str]) -> list[str]:
        """Detect which columns contain numeric data.

        A column is considered numeric if at least 50% of its non-empty
        values can be parsed as floats.
        """
        numeric_cols: list[str] = []
        for header in headers:
            total = 0
            numeric_count = 0
            for row in rows:
                val = row.get(header, "").strip()
                if not val:
                    continue
                total += 1
                try:
                    float(val)
                    numeric_count += 1
                except ValueError:
                    pass
            if total > 0 and (numeric_count / total) >= 0.5:
                numeric_cols.append(header)
        return numeric_cols
