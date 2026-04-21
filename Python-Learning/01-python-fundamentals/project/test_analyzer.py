"""pytest test suite for the data_analyzer module.

Demonstrates testing patterns from Module 09 (Testing with pytest):
    - Fixtures for setup/teardown
    - Parametrize for data-driven tests
    - Exception testing with pytest.raises
    - Temporary files for I/O testing
    - Descriptive test names and docstrings

Swift parallel: This is the Python equivalent of XCTestCase,
but with a more functional, fixture-based approach rather than
setUp()/tearDown() methods.

Run:
    pytest test_analyzer.py -v
    pytest test_analyzer.py --cov=data_analyzer -v
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from data_analyzer import (
    CSVReader,
    ComparisonOperator,
    DataAnalysisError,
    DataFilter,
    EmptyDataError,
    FileNotFoundError_,
    FilterCriteria,
    InvalidColumnError,
    InvalidFilterError,
    StatisticsCalculator,
    StatisticsResult,
)


# ---------------------------------------------------------------------------
# Fixtures  (Module 09 -- Fixtures)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create a temporary CSV file with sample data.

    Similar to Swift's setUpWithError() creating test fixtures,
    but scoped automatically by pytest.
    """
    csv_file = tmp_path / "test_data.csv"
    rows = [
        {"name": "Alice", "age": "30", "salary": "100000", "department": "Engineering"},
        {"name": "Bob", "age": "25", "salary": "80000", "department": "Marketing"},
        {"name": "Carol", "age": "35", "salary": "120000", "department": "Engineering"},
        {"name": "David", "age": "28", "salary": "90000", "department": "Design"},
        {"name": "Eva", "age": "32", "salary": "110000", "department": "Engineering"},
    ]
    headers = ["name", "age", "salary", "department"]
    with csv_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return csv_file


@pytest.fixture
def sample_rows() -> list[dict[str, str]]:
    """Provide in-memory sample rows (no file I/O needed)."""
    return [
        {"name": "Alice", "age": "30", "salary": "100000", "department": "Engineering"},
        {"name": "Bob", "age": "25", "salary": "80000", "department": "Marketing"},
        {"name": "Carol", "age": "35", "salary": "120000", "department": "Engineering"},
        {"name": "David", "age": "28", "salary": "90000", "department": "Design"},
        {"name": "Eva", "age": "32", "salary": "110000", "department": "Engineering"},
    ]


@pytest.fixture
def sample_headers() -> list[str]:
    """Column headers matching sample_rows."""
    return ["name", "age", "salary", "department"]


@pytest.fixture
def empty_csv(tmp_path: Path) -> Path:
    """Create a CSV file with only a header row (no data)."""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("name,age,salary\n", encoding="utf-8")
    return csv_file


@pytest.fixture
def csv_with_mixed_types(tmp_path: Path) -> Path:
    """Create a CSV file with some non-numeric values in numeric columns."""
    csv_file = tmp_path / "mixed.csv"
    content = (
        "name,age,score\n"
        "Alice,30,95.5\n"
        "Bob,N/A,87.0\n"
        "Carol,35,invalid\n"
        "David,28,92.0\n"
    )
    csv_file.write_text(content, encoding="utf-8")
    return csv_file


# ---------------------------------------------------------------------------
# CSVReader Tests
# ---------------------------------------------------------------------------

class TestCSVReader:
    """Tests for the CSVReader class."""

    def test_read_valid_csv(self, sample_csv: Path) -> None:
        """CSVReader should correctly read a valid CSV file."""
        reader = CSVReader(sample_csv)
        rows = reader.read()

        assert len(rows) == 5
        assert reader.headers == ["name", "age", "salary", "department"]
        assert rows[0]["name"] == "Alice"
        assert rows[0]["salary"] == "100000"

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        """CSVReader should raise FileNotFoundError_ for missing files."""
        reader = CSVReader(tmp_path / "does_not_exist.csv")

        with pytest.raises(FileNotFoundError_) as exc_info:
            reader.read()

        assert "does_not_exist.csv" in str(exc_info.value)

    def test_read_empty_csv(self, empty_csv: Path) -> None:
        """CSVReader should raise EmptyDataError when no data rows exist."""
        reader = CSVReader(empty_csv)

        with pytest.raises(EmptyDataError):
            reader.read()

    def test_row_count_property(self, sample_csv: Path) -> None:
        """The row_count property should reflect the number of data rows."""
        reader = CSVReader(sample_csv)
        assert reader.row_count == 5

    def test_iter_rows_generator(self, sample_csv: Path) -> None:
        """iter_rows should yield rows lazily as a generator."""
        reader = CSVReader(sample_csv)
        rows_list = list(reader.iter_rows())

        assert len(rows_list) == 5
        assert rows_list[0]["name"] == "Alice"


# ---------------------------------------------------------------------------
# DataFilter Tests
# ---------------------------------------------------------------------------

class TestDataFilterParsing:
    """Tests for DataFilter.parse_filter -- parsing filter expressions."""

    @pytest.mark.parametrize(
        ("expression", "expected_col", "expected_op", "expected_val"),
        [
            ("salary>80000", "salary", ComparisonOperator.GT, "80000"),
            ("age<=30", "age", ComparisonOperator.LE, "30"),
            ("department==Engineering", "department", ComparisonOperator.EQ, "Engineering"),
            ("salary!=100000", "salary", ComparisonOperator.NE, "100000"),
            ("age>=25", "age", ComparisonOperator.GE, "25"),
            ("salary<90000", "salary", ComparisonOperator.LT, "90000"),
        ],
        ids=[
            "greater_than",
            "less_than_or_equal",
            "equals",
            "not_equals",
            "greater_than_or_equal",
            "less_than",
        ],
    )
    def test_parse_comparison_operators(
        self,
        expression: str,
        expected_col: str,
        expected_op: ComparisonOperator,
        expected_val: str,
    ) -> None:
        """parse_filter should correctly identify column, operator, and value."""
        criteria = DataFilter.parse_filter(expression)

        assert criteria.column == expected_col
        assert criteria.operator == expected_op
        assert criteria.value == expected_val

    def test_parse_contains_operator(self) -> None:
        """parse_filter should handle the 'contains' keyword operator."""
        criteria = DataFilter.parse_filter("city contains San")

        assert criteria.column == "city"
        assert criteria.operator == ComparisonOperator.CONTAINS
        assert criteria.value == "San"

    def test_parse_invalid_expression(self) -> None:
        """parse_filter should raise InvalidFilterError for malformed input."""
        with pytest.raises(InvalidFilterError):
            DataFilter.parse_filter("this is not a valid filter")

    def test_parse_empty_expression(self) -> None:
        """parse_filter should raise InvalidFilterError for empty strings."""
        with pytest.raises(InvalidFilterError):
            DataFilter.parse_filter("")


class TestDataFilterApplication:
    """Tests for DataFilter.apply_filter -- filtering row data."""

    def test_filter_equals(
        self, sample_rows: list[dict[str, str]], sample_headers: list[str]
    ) -> None:
        """Equality filter should return only matching rows."""
        criteria = FilterCriteria(
            column="department",
            operator=ComparisonOperator.EQ,
            value="Engineering",
        )
        result = DataFilter.apply_filter(sample_rows, criteria, sample_headers)

        assert len(result) == 3
        assert all(r["department"] == "Engineering" for r in result)

    def test_filter_greater_than(
        self, sample_rows: list[dict[str, str]], sample_headers: list[str]
    ) -> None:
        """Greater-than filter should work with numeric comparisons."""
        criteria = FilterCriteria(
            column="salary",
            operator=ComparisonOperator.GT,
            value="95000",
        )
        result = DataFilter.apply_filter(sample_rows, criteria, sample_headers)

        assert len(result) == 3
        assert all(float(r["salary"]) > 95000 for r in result)

    def test_filter_invalid_column(
        self, sample_rows: list[dict[str, str]], sample_headers: list[str]
    ) -> None:
        """Filtering on a nonexistent column should raise InvalidColumnError."""
        criteria = FilterCriteria(
            column="nonexistent",
            operator=ComparisonOperator.EQ,
            value="anything",
        )
        with pytest.raises(InvalidColumnError) as exc_info:
            DataFilter.apply_filter(sample_rows, criteria, sample_headers)

        assert "nonexistent" in str(exc_info.value)


# ---------------------------------------------------------------------------
# StatisticsCalculator Tests
# ---------------------------------------------------------------------------

class TestStatisticsCalculator:
    """Tests for the StatisticsCalculator class."""

    def test_mean_basic(self) -> None:
        """Mean of [10, 20, 30] should be 20.0."""
        assert StatisticsCalculator.mean([10.0, 20.0, 30.0]) == 20.0

    def test_mean_empty(self) -> None:
        """Mean of an empty list should be 0.0."""
        assert StatisticsCalculator.mean([]) == 0.0

    @pytest.mark.parametrize(
        ("values", "expected"),
        [
            ([1.0, 2.0, 3.0], 2.0),              # odd count -- middle element
            ([1.0, 2.0, 3.0, 4.0], 2.5),          # even count -- average of middle two
            ([5.0], 5.0),                           # single element
            ([10.0, 20.0], 15.0),                   # two elements
        ],
        ids=["odd_count", "even_count", "single", "two_elements"],
    )
    def test_median(self, values: list[float], expected: float) -> None:
        """Median should handle both odd and even-length lists."""
        assert StatisticsCalculator.median(values) == expected

    def test_mode_with_repeats(self) -> None:
        """Mode should return the most frequent value."""
        values = [1.0, 2.0, 2.0, 3.0, 3.0, 3.0]
        assert StatisticsCalculator.mode(values) == 3.0

    def test_mode_all_unique(self) -> None:
        """Mode should return None when all values are unique."""
        values = [1.0, 2.0, 3.0, 4.0]
        assert StatisticsCalculator.mode(values) is None

    def test_std_dev(self) -> None:
        """Standard deviation of [2, 4, 4, 4, 5, 5, 7, 9] should be ~2.0."""
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        result = StatisticsCalculator.std_dev(values)
        assert abs(result - 2.0) < 0.01

    def test_compute_full_statistics(
        self, sample_rows: list[dict[str, str]], sample_headers: list[str]
    ) -> None:
        """compute() should return a complete StatisticsResult for a valid column."""
        result = StatisticsCalculator.compute(sample_rows, "salary", sample_headers)

        assert result.column_name == "salary"
        assert result.count == 5
        assert result.mean == 100000.0
        assert result.min_value == 80000.0
        assert result.max_value == 120000.0

    def test_compute_invalid_column(
        self, sample_rows: list[dict[str, str]], sample_headers: list[str]
    ) -> None:
        """compute() should raise InvalidColumnError for nonexistent columns."""
        with pytest.raises(InvalidColumnError):
            StatisticsCalculator.compute(sample_rows, "nonexistent", sample_headers)

    def test_compute_non_numeric_column(
        self, sample_rows: list[dict[str, str]], sample_headers: list[str]
    ) -> None:
        """compute() should raise DataAnalysisError for non-numeric columns."""
        with pytest.raises(DataAnalysisError, match="No numeric values"):
            StatisticsCalculator.compute(sample_rows, "name", sample_headers)

    def test_detect_numeric_columns(
        self, sample_rows: list[dict[str, str]], sample_headers: list[str]
    ) -> None:
        """detect_numeric_columns should identify age and salary as numeric."""
        numeric = StatisticsCalculator.detect_numeric_columns(
            sample_rows, sample_headers
        )
        assert "age" in numeric
        assert "salary" in numeric
        assert "name" not in numeric
        assert "department" not in numeric

    def test_extract_numeric_skips_invalid(
        self, csv_with_mixed_types: Path
    ) -> None:
        """extract_numeric_values should skip non-numeric entries gracefully."""
        reader = CSVReader(csv_with_mixed_types)
        rows = reader.read()

        age_values = StatisticsCalculator.extract_numeric_values(rows, "age")
        assert len(age_values) == 3  # "N/A" skipped
        assert 30.0 in age_values

        score_values = StatisticsCalculator.extract_numeric_values(rows, "score")
        assert len(score_values) == 3  # "invalid" skipped
        assert 95.5 in score_values


# ---------------------------------------------------------------------------
# StatisticsResult Tests
# ---------------------------------------------------------------------------

class TestStatisticsResult:
    """Tests for the StatisticsResult dataclass."""

    def test_str_representation(self) -> None:
        """__str__ should produce a formatted multi-line summary."""
        result = StatisticsResult(
            column_name="salary",
            count=5,
            mean=100000.0,
            median=100000.0,
            mode=None,
            std_dev=14142.14,
            min_value=80000.0,
            max_value=120000.0,
        )
        text = str(result)

        assert "salary" in text
        assert "100000.00" in text
        assert "N/A" in text  # mode is None

    def test_repr_representation(self) -> None:
        """__repr__ should produce a concise developer-friendly string."""
        result = StatisticsResult(
            column_name="age",
            count=3,
            mean=30.0,
            median=30.0,
            mode=30.0,
            std_dev=5.0,
            min_value=25.0,
            max_value=35.0,
        )
        text = repr(result)

        assert "StatisticsResult" in text
        assert "age" in text


# ---------------------------------------------------------------------------
# Integration Test
# ---------------------------------------------------------------------------

class TestIntegration:
    """End-to-end tests combining CSVReader + DataFilter + StatisticsCalculator."""

    def test_full_pipeline(self, sample_csv: Path) -> None:
        """Full pipeline: read -> filter -> compute should work end-to-end."""
        # Read
        reader = CSVReader(sample_csv)
        rows = reader.read()
        headers = reader.headers

        # Filter: Engineering department only
        criteria = DataFilter.parse_filter("department==Engineering")
        filtered = DataFilter.apply_filter(rows, criteria, headers)
        assert len(filtered) == 3

        # Compute statistics on salary
        result = StatisticsCalculator.compute(filtered, "salary", headers)
        assert result.count == 3
        assert result.min_value == 100000.0
        assert result.max_value == 120000.0
