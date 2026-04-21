"""
Module 04: Pandas Advanced - Exercises
======================================

15 exercises covering GroupBy, merging, reshaping, missing data,
method chaining, apply/map, window functions, MultiIndex, string/datetime methods,
and categorical data.

All exercises use inline data (no external files needed).

Run this file directly to check your solutions:
    python exercises.py
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Exercise 1: GroupBy Basic Aggregation
# ---------------------------------------------------------------------------
def groupby_aggregation() -> pd.DataFrame:
    """
    Given sales data, group by region and calculate:
    - 'total_sales': sum of sales
    - 'avg_sales': mean of sales
    - 'num_transactions': count of transactions
    - 'max_sale': maximum sale

    Data:
        region: ['North', 'South', 'North', 'South', 'North']
        sales: [1000, 1200, 950, 1100, 1050]

    Return DataFrame grouped by region with the aggregations above.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: GroupBy Multiple Columns
# ---------------------------------------------------------------------------
def groupby_multiple() -> pd.DataFrame:
    """
    Given employee data, group by department and role, then calculate:
    - 'employee_count': count of employees
    - 'avg_salary': mean salary
    - 'min_salary': minimum salary

    Data:
        department: ['Sales', 'Sales', 'Engineering', 'Engineering', 'Sales', 'Engineering']
        role: ['Manager', 'Rep', 'Senior', 'Junior', 'Rep', 'Senior']
        salary: [80000, 45000, 95000, 60000, 48000, 92000]

    Return DataFrame grouped by both columns.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: GroupBy Transform
# ---------------------------------------------------------------------------
def groupby_transform() -> tuple[pd.Series, pd.Series]:
    """
    Given sales data, use groupby transform to:
    1. salary_normalized: normalize salary within each department
       (subtract mean, divide by std within group)
    2. dept_count: count of employees per department for each row

    Data:
        department: ['Sales', 'Sales', 'Engineering', 'Engineering']
        employee: ['Alice', 'Bob', 'Charlie', 'Diana']
        salary: [60000, 65000, 90000, 85000]

    Return tuple of (salary_normalized, dept_count) as Series.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Merge (Inner Join)
# ---------------------------------------------------------------------------
def merge_inner_join() -> pd.DataFrame:
    """
    Perform an inner join of employees and departments on department_id.

    Employees:
        emp_id: [1, 2, 3, 4]
        name: ['Alice', 'Bob', 'Charlie', 'Diana']
        dept_id: [10, 20, 10, 30]

    Departments:
        dept_id: [10, 20, 40]
        dept_name: ['Engineering', 'Sales', 'Marketing']

    Return merged DataFrame with only matching department_ids.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Merge (Left Join)
# ---------------------------------------------------------------------------
def merge_left_join() -> pd.DataFrame:
    """
    Perform a left join: keep all employees, add department names where available.
    Use same data as Exercise 4.

    Return merged DataFrame with all employees (some dept_name will be NaN).
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Concat DataFrames
# ---------------------------------------------------------------------------
def concat_dataframes() -> pd.DataFrame:
    """
    Concatenate two DataFrames vertically (row-wise).

    DF1:
        Q: ['Q1', 'Q1']
        region: ['East', 'West']
        revenue: [100000, 110000]

    DF2:
        Q: ['Q2', 'Q2']
        region: ['East', 'West']
        revenue: [120000, 115000]

    Return concatenated DataFrame with reset index.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Pivot Table
# ---------------------------------------------------------------------------
def pivot_table_creation() -> pd.DataFrame:
    """
    Create a pivot table from sales data.

    Data:
        date: ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02']
        region: ['East', 'West', 'East', 'West']
        product: ['A', 'A', 'A', 'A']
        revenue: [1000, 1500, 1200, 1300]

    Pivot with:
        index='date'
        columns='region'
        values='revenue'
        aggfunc='sum'

    Return the pivot table.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Melt (Unpivot)
# ---------------------------------------------------------------------------
def melt_dataframe() -> pd.DataFrame:
    """
    Melt (unpivot) data from wide to long format.

    Data (wide format):
        product: ['A', 'B', 'C']
        Q1: [100, 200, 300]
        Q2: [150, 250, 350]
        Q3: [180, 290, 400]

    Melt with:
        id_vars=['product']
        var_name='quarter'
        value_name='revenue'

    Return melted DataFrame in long format.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Handling Missing Data - Dropping
# ---------------------------------------------------------------------------
def handle_missing_drop() -> tuple[pd.DataFrame, int]:
    """
    Given a DataFrame with missing values:
    1. dropped: DataFrame after dropping rows with ANY missing values
    2. n_dropped: number of rows dropped

    Data:
        A: [1, 2, np.nan, 4, 5]
        B: [5, np.nan, np.nan, 8, 9]
        C: [10, 11, 12, 13, 14]

    Return tuple of (dropped_df, num_rows_dropped).
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Handling Missing Data - Filling
# ---------------------------------------------------------------------------
def handle_missing_fill() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Given a DataFrame with missing values, create three versions:
    1. filled_zero: fill missing with 0
    2. filled_forward: forward fill (ffill)
    3. filled_interpolate: interpolate (for numeric data)

    Data:
        value: [1.0, 2.0, np.nan, 4.0, np.nan, 6.0]

    Return tuple of (filled_zero, filled_forward, filled_interpolate).
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Method Chaining
# ---------------------------------------------------------------------------
def method_chaining() -> float:
    """
    Use method chaining to:
    1. Filter for salary > 60000
    2. Group by department
    3. Calculate mean salary per department
    4. Get the maximum average salary across departments
    5. Round to 2 decimals

    Data:
        department: ['Sales', 'Sales', 'Engineering', 'Engineering', 'Engineering']
        salary: [60000, 70000, 85000, 90000, 95000]

    Return the final result as a float.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Apply on Series
# ---------------------------------------------------------------------------
def apply_series() -> tuple[pd.Series, pd.Series]:
    """
    Apply custom functions to a Series.

    Data:
        values: [1, 2, 3, 4, 5]

    Create:
    1. squared: square each value using apply
    2. doubled: double each value using apply

    Return tuple of (squared, doubled) as Series.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 13: Map Categorical Values
# ---------------------------------------------------------------------------
def map_categorical() -> pd.Series:
    """
    Map grade letters to GPA points.

    Data:
        grades: ['A', 'B', 'C', 'A', 'D', 'B']

    Mapping:
        'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0

    Return Series with GPA values.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 14: Rolling Window Functions
# ---------------------------------------------------------------------------
def rolling_windows() -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Create rolling window statistics.

    Data:
        values: [10, 12, 11, 13, 15, 14, 16, 18, 17, 19]

    Calculate with window=3:
    1. rolling_mean: rolling mean
    2. rolling_min: rolling minimum
    3. rolling_max: rolling maximum

    Return tuple of (rolling_mean, rolling_min, rolling_max).
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 15: String and DateTime Operations
# ---------------------------------------------------------------------------
def string_datetime_ops() -> tuple[pd.Series, pd.Series, int]:
    """
    Perform string and datetime operations.

    Data:
        text: ['apple', 'banana', 'cherry', 'apricot']
        dates: ['2024-01-15', '2024-02-20', '2024-03-10', '2024-04-05']

    Create:
    1. contains_a: Series of booleans indicating if 'a' is in text
    2. extracted_month: extracted month from dates (integers)
    3. count_january: count of dates in January (integer)

    Return tuple of (contains_a, extracted_month, count_january).
    """
    pass


# ===========================================================================
# Tests
# ===========================================================================
if __name__ == "__main__":
    print("Running Pandas Advanced tests...\n")

    # Test 1: GroupBy aggregation
    result = groupby_aggregation()
    assert len(result) == 2
    assert 'total_sales' in result.columns
    assert 'avg_sales' in result.columns
    assert 'num_transactions' in result.columns
    assert 'max_sale' in result.columns
    assert result.loc['North', 'total_sales'] == 3000
    print("  [PASS] Exercise 1: GroupBy Aggregation")

    # Test 2: GroupBy multiple columns
    result = groupby_multiple()
    assert len(result) == 4
    assert 'employee_count' in result.columns
    assert 'avg_salary' in result.columns
    print("  [PASS] Exercise 2: GroupBy Multiple Columns")

    # Test 3: GroupBy transform
    norm_sal, dept_cnt = groupby_transform()
    assert isinstance(norm_sal, pd.Series)
    assert isinstance(dept_cnt, pd.Series)
    assert len(norm_sal) == 4
    assert len(dept_cnt) == 4
    assert dept_cnt.iloc[0] == 2  # Two employees in Sales
    print("  [PASS] Exercise 3: GroupBy Transform")

    # Test 4: Inner join
    merged = merge_inner_join()
    assert len(merged) == 2  # Only emp_ids 1 and 3 have matching depts
    assert 'dept_name' in merged.columns
    print("  [PASS] Exercise 4: Merge Inner Join")

    # Test 5: Left join
    merged = merge_left_join()
    assert len(merged) == 4  # All employees
    assert 'dept_name' in merged.columns
    assert pd.isna(merged.loc[merged['emp_id'] == 4, 'dept_name'].iloc[0])
    print("  [PASS] Exercise 5: Merge Left Join")

    # Test 6: Concat
    concatenated = concat_dataframes()
    assert len(concatenated) == 4
    assert 'Q' in concatenated.columns
    assert concatenated.iloc[0]['Q'] == 'Q1'
    assert concatenated.iloc[2]['Q'] == 'Q2'
    print("  [PASS] Exercise 6: Concat DataFrames")

    # Test 7: Pivot table
    pivot = pivot_table_creation()
    assert pivot.shape == (2, 2)
    assert 'East' in pivot.columns
    assert 'West' in pivot.columns
    assert pivot.loc['2024-01-01', 'East'] == 1000
    print("  [PASS] Exercise 7: Pivot Table Creation")

    # Test 8: Melt
    melted = melt_dataframe()
    assert len(melted) == 9  # 3 products * 3 quarters
    assert 'quarter' in melted.columns
    assert 'revenue' in melted.columns
    assert melted.iloc[0]['product'] == 'A'
    assert melted.iloc[0]['quarter'] == 'Q1'
    print("  [PASS] Exercise 8: Melt DataFrame")

    # Test 9: Handle missing - drop
    dropped, n_dropped = handle_missing_drop()
    assert n_dropped == 2  # Rows with any NaN
    assert len(dropped) == 3
    assert not dropped.isnull().any().any()
    print("  [PASS] Exercise 9: Handle Missing - Drop")

    # Test 10: Handle missing - fill
    filled_zero, filled_ffill, filled_interp = handle_missing_fill()
    assert pd.isna(filled_zero).sum() == 0
    assert pd.isna(filled_ffill).sum() == 0
    assert pd.isna(filled_interp).sum() == 0
    print("  [PASS] Exercise 10: Handle Missing - Fill")

    # Test 11: Method chaining
    result = method_chaining()
    assert isinstance(result, (float, np.floating))
    assert result == 90000.0
    print("  [PASS] Exercise 11: Method Chaining")

    # Test 12: Apply on Series
    squared, doubled = apply_series()
    assert squared.iloc[0] == 1
    assert squared.iloc[4] == 25
    assert doubled.iloc[0] == 2
    assert doubled.iloc[4] == 10
    print("  [PASS] Exercise 12: Apply on Series")

    # Test 13: Map categorical
    gpa = map_categorical()
    assert gpa.iloc[0] == 4.0  # A
    assert gpa.iloc[1] == 3.0  # B
    assert gpa.iloc[2] == 2.0  # C
    print("  [PASS] Exercise 13: Map Categorical")

    # Test 14: Rolling windows
    rolling_mean, rolling_min, rolling_max = rolling_windows()
    assert len(rolling_mean) == 10
    assert pd.isna(rolling_mean.iloc[0])  # First value is NaN
    assert rolling_mean.iloc[2] == 11.0  # (10+12+11)/3
    print("  [PASS] Exercise 14: Rolling Windows")

    # Test 15: String and datetime ops
    contains_a, extracted_month, count_jan = string_datetime_ops()
    assert len(contains_a) == 4
    assert contains_a.iloc[0] == True  # 'apple' contains 'a'
    assert contains_a.iloc[1] == True  # 'banana' contains 'a'
    assert contains_a.iloc[2] == False  # 'cherry' does not contain 'a'
    assert len(extracted_month) == 4
    assert extracted_month.iloc[0] == 1  # January
    assert extracted_month.iloc[1] == 2  # February
    assert count_jan == 1
    print("  [PASS] Exercise 15: String and DateTime Operations")

    print("\nAll 15 exercises passed!")
