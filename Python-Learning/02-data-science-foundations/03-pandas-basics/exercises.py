"""
Module 03: Pandas Basics - Exercises
=====================================

15 exercises covering Series, DataFrame creation, reading data, indexing,
filtering, column operations, sorting, and basic statistics.

All exercises use inline data (no external files needed).

Run this file directly to check your solutions:
    python exercises.py
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Helper: Sample data used across multiple exercises
# ---------------------------------------------------------------------------
def get_employees_df() -> pd.DataFrame:
    """Return a sample employees DataFrame for exercises."""
    return pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve',
                 'Frank', 'Grace', 'Hank', 'Ivy', 'Jack'],
        'department': ['Engineering', 'Marketing', 'Engineering', 'Marketing',
                       'Engineering', 'Sales', 'Engineering', 'Sales',
                       'Marketing', 'Engineering'],
        'age': [30, 25, 35, 28, 32, 45, 27, 38, 29, 33],
        'salary': [90000, 65000, 95000, 72000, 88000,
                   78000, 82000, 71000, 69000, 91000],
        'years_exp': [5, 2, 10, 3, 7, 20, 4, 12, 4, 8],
        'remote': [True, False, True, True, False,
                   False, True, False, True, True],
    })


# ---------------------------------------------------------------------------
# Exercise 1: Series Creation and Operations
# ---------------------------------------------------------------------------
def series_operations() -> tuple[float, pd.Series, int]:
    """
    Given the monthly sales data below, compute:

    1. total_sales: sum of all monthly sales (float)
    2. above_average: a Series containing only months where sales
       exceed the average (filtered Series)
    3. best_month_index: the integer position (0-based) of the month
       with the highest sales

    Monthly sales data:
        Jan: 12000, Feb: 15000, Mar: 18000, Apr: 14000,
        May: 22000, Jun: 19000, Jul: 25000, Aug: 21000,
        Sep: 17000, Oct: 16000, Nov: 23000, Dec: 30000

    Returns:
        Tuple of (total_sales, above_average, best_month_index)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: DataFrame Creation
# ---------------------------------------------------------------------------
def create_product_df() -> pd.DataFrame:
    """
    Create a DataFrame with the following product data:

    | product     | category    | price  | stock |
    |-------------|-------------|--------|-------|
    | Laptop      | Electronics | 999.99 | 50    |
    | Headphones  | Electronics | 149.99 | 200   |
    | Desk Chair  | Furniture   | 299.99 | 75    |
    | Monitor     | Electronics | 449.99 | 100   |
    | Bookshelf   | Furniture   | 199.99 | 30    |

    The price column should be float64 and stock should be int64.

    Returns:
        DataFrame with columns: product, category, price, stock
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: DataFrame Attributes
# ---------------------------------------------------------------------------
def df_info(df: pd.DataFrame) -> dict:
    """
    Given any DataFrame, return a dictionary with:
    - 'n_rows': number of rows (int)
    - 'n_cols': number of columns (int)
    - 'column_names': list of column names (list of str)
    - 'numeric_columns': list of numeric column names (list of str)
    - 'has_missing': whether the DataFrame has any missing values (bool)

    Args:
        df: Any pandas DataFrame

    Returns:
        Dictionary with the keys described above
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: loc vs iloc
# ---------------------------------------------------------------------------
def indexing_practice(df: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame, str]:
    """
    Given the employees DataFrame (from get_employees_df()):

    1. first_row: Get the first row using iloc (as a Series)
    2. eng_subset: Using loc, select rows 0 through 4 (inclusive)
       and only the columns 'name' and 'salary' (as a DataFrame)
    3. last_name: Get the name of the last employee using iloc (as a string)

    Args:
        df: The employees DataFrame

    Returns:
        Tuple of (first_row, eng_subset, last_name)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Boolean Filtering
# ---------------------------------------------------------------------------
def filter_employees(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Given the employees DataFrame, create three filtered DataFrames:

    1. senior_engineers: Engineering department AND age >= 30
    2. high_earners: salary > 85000
    3. remote_marketing: remote is True AND department is 'Marketing'

    Args:
        df: The employees DataFrame

    Returns:
        Tuple of (senior_engineers, high_earners, remote_marketing)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Adding and Modifying Columns
# ---------------------------------------------------------------------------
def add_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given the employees DataFrame, add the following columns
    (return a NEW DataFrame, don't modify the original):

    1. 'salary_k': salary divided by 1000 (e.g., 90000 -> 90.0)
    2. 'experience_level': 'Junior' if years_exp < 5,
                           'Mid' if 5 <= years_exp < 10,
                           'Senior' if years_exp >= 10
    3. 'salary_per_year_exp': salary / years_exp (rounded to 2 decimals)

    Args:
        df: The employees DataFrame

    Returns:
        New DataFrame with the 3 additional columns
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Sorting
# ---------------------------------------------------------------------------
def sort_employees(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Given the employees DataFrame:

    1. by_salary_desc: Sort by salary descending
    2. by_dept_then_age: Sort by department ascending, then by age descending
       within each department

    Args:
        df: The employees DataFrame

    Returns:
        Tuple of (by_salary_desc, by_dept_then_age)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Basic Statistics
# ---------------------------------------------------------------------------
def salary_statistics(df: pd.DataFrame) -> dict:
    """
    Given the employees DataFrame, compute:

    - 'mean_salary': mean salary across all employees
    - 'median_salary': median salary
    - 'std_salary': standard deviation of salary
    - 'salary_range': max salary minus min salary
    - 'dept_counts': value counts of department (as a Series)
    - 'n_unique_depts': number of unique departments

    Args:
        df: The employees DataFrame

    Returns:
        Dictionary with the keys above
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Column Renaming and Dropping
# ---------------------------------------------------------------------------
def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given the employees DataFrame:
    1. Rename 'years_exp' to 'experience'
    2. Rename 'remote' to 'is_remote'
    3. Drop the 'age' column

    Return a new DataFrame (don't modify the original).

    Args:
        df: The employees DataFrame

    Returns:
        Cleaned DataFrame
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Type Conversion
# ---------------------------------------------------------------------------
def convert_types() -> pd.DataFrame:
    """
    Create a DataFrame from this raw data and convert the types appropriately:

    Raw data (as strings):
        id: ['001', '002', '003', '004']
        score: ['85.5', '92.3', 'N/A', '78.1']
        date: ['2024-01-15', '2024-02-20', '2024-03-10', '2024-04-05']
        passed: ['1', '1', '0', '1']

    Convert:
    - score to float (N/A should become NaN)
    - date to datetime
    - passed to boolean (1=True, 0=False)
    - id should remain as string

    Returns:
        DataFrame with properly typed columns
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: value_counts and describe
# ---------------------------------------------------------------------------
def analyze_categories(df: pd.DataFrame) -> tuple[str, float, int]:
    """
    Given the employees DataFrame:

    1. most_common_dept: name of the most common department (str)
    2. engineering_avg_salary: average salary in Engineering dept (float)
    3. n_remote: number of employees who work remotely (int)

    Args:
        df: The employees DataFrame

    Returns:
        Tuple of (most_common_dept, engineering_avg_salary, n_remote)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Creating DataFrames from Different Sources
# ---------------------------------------------------------------------------
def create_from_records() -> pd.DataFrame:
    """
    Create a DataFrame from a list of dictionaries (records):

    Records:
        {'city': 'New York', 'pop_millions': 8.3, 'country': 'US'}
        {'city': 'London', 'pop_millions': 8.9, 'country': 'UK'}
        {'city': 'Tokyo', 'pop_millions': 13.9, 'country': 'Japan'}
        {'city': 'Paris', 'pop_millions': 2.1, 'country': 'France'}
        {'city': 'Sydney', 'pop_millions': 5.3, 'country': 'Australia'}

    Set the 'city' column as the DataFrame index.

    Returns:
        DataFrame with city as index
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 13: isin and between
# ---------------------------------------------------------------------------
def advanced_filtering(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Given the employees DataFrame:

    1. target_depts: employees in either 'Engineering' or 'Sales' departments
       (use isin)
    2. mid_salary: employees with salary between 70000 and 90000 (inclusive)
       (use between)

    Args:
        df: The employees DataFrame

    Returns:
        Tuple of (target_depts, mid_salary)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 14: nlargest, nsmallest, and rank
# ---------------------------------------------------------------------------
def ranking_operations(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """
    Given the employees DataFrame:

    1. top_3_salary: the 3 employees with the highest salary (DataFrame)
    2. youngest_2: the 2 youngest employees (DataFrame)
    3. salary_rank: rank of each employee by salary (1 = highest),
       as a Series with the same index as df

    Args:
        df: The employees DataFrame

    Returns:
        Tuple of (top_3_salary, youngest_2, salary_rank)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 15: Comprehensive Analysis
# ---------------------------------------------------------------------------
def department_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given the employees DataFrame, create a summary report DataFrame
    with one row per department and these columns:

    - 'employee_count': number of employees in the department
    - 'avg_salary': average salary (rounded to 0 decimals)
    - 'avg_age': average age (rounded to 1 decimal)
    - 'avg_experience': average years_exp (rounded to 1 decimal)
    - 'remote_pct': percentage of remote workers (0-100, rounded to 1 decimal)

    The department name should be the index.
    Sort by employee_count descending.

    Args:
        df: The employees DataFrame

    Returns:
        Summary DataFrame
    """
    pass


# ===========================================================================
# Tests
# ===========================================================================
if __name__ == "__main__":
    print("Running Pandas Basics tests...\n")
    emp_df = get_employees_df()

    # Test 1: Series operations
    total, above_avg, best_idx = series_operations()
    assert total == 232000
    assert len(above_avg) > 0
    assert all(v > 232000 / 12 for v in above_avg.values)
    assert best_idx == 11  # December
    print("  [PASS] Exercise 1: Series Operations")

    # Test 2: Product DataFrame
    products = create_product_df()
    assert products.shape == (5, 4)
    assert list(products.columns) == ['product', 'category', 'price', 'stock']
    assert products['price'].dtype == np.float64
    assert products['stock'].dtype == np.int64
    assert products.loc[0, 'product'] == 'Laptop'
    print("  [PASS] Exercise 2: Create Product DataFrame")

    # Test 3: DataFrame info
    info = df_info(emp_df)
    assert info['n_rows'] == 10
    assert info['n_cols'] == 6
    assert 'name' in info['column_names']
    assert 'salary' in info['numeric_columns']
    assert 'name' not in info['numeric_columns']
    assert info['has_missing'] is False
    print("  [PASS] Exercise 3: DataFrame Info")

    # Test 4: Indexing
    first, subset, last = indexing_practice(emp_df)
    assert first['name'] == 'Alice'
    assert subset.shape == (5, 2)
    assert list(subset.columns) == ['name', 'salary']
    assert last == 'Jack'
    print("  [PASS] Exercise 4: loc vs iloc")

    # Test 5: Filtering
    se, he, rm = filter_employees(emp_df)
    assert len(se) == 3  # Alice(30), Charlie(35), Jack(33)
    assert all(se['department'] == 'Engineering')
    assert all(se['age'] >= 30)
    assert len(he) == 3  # Alice, Charlie, Jack
    assert all(he['salary'] > 85000)
    assert len(rm) == 2  # Diana, Ivy
    print("  [PASS] Exercise 5: Boolean Filtering")

    # Test 6: Adding columns
    with_cols = add_columns(emp_df)
    assert 'salary_k' in with_cols.columns
    assert with_cols.loc[0, 'salary_k'] == 90.0
    assert 'experience_level' in with_cols.columns
    assert with_cols.loc[0, 'experience_level'] == 'Mid'  # 5 years
    assert with_cols.loc[2, 'experience_level'] == 'Senior'  # 10 years
    assert with_cols.loc[1, 'experience_level'] == 'Junior'  # 2 years
    assert 'salary_per_year_exp' in with_cols.columns
    # Original should be unchanged
    assert 'salary_k' not in emp_df.columns
    print("  [PASS] Exercise 6: Adding Columns")

    # Test 7: Sorting
    by_sal, by_dept_age = sort_employees(emp_df)
    assert by_sal.iloc[0]['name'] == 'Charlie'  # highest salary
    assert by_sal.iloc[-1]['name'] == 'Bob'  # lowest salary
    # Check department sorting
    depts = by_dept_age['department'].tolist()
    assert depts == sorted(depts, key=lambda x: x)  # This just checks grouping
    print("  [PASS] Exercise 7: Sorting")

    # Test 8: Statistics
    stats = salary_statistics(emp_df)
    assert np.isclose(stats['mean_salary'], 80100.0)
    assert isinstance(stats['dept_counts'], pd.Series)
    assert stats['n_unique_depts'] == 3
    print("  [PASS] Exercise 8: Salary Statistics")

    # Test 9: Clean columns
    cleaned = clean_columns(emp_df)
    assert 'experience' in cleaned.columns
    assert 'years_exp' not in cleaned.columns
    assert 'is_remote' in cleaned.columns
    assert 'remote' not in cleaned.columns
    assert 'age' not in cleaned.columns
    assert 'years_exp' in emp_df.columns  # original unchanged
    print("  [PASS] Exercise 9: Clean Columns")

    # Test 10: Type conversion
    typed = convert_types()
    assert typed['score'].dtype == np.float64
    assert pd.isna(typed.loc[2, 'score'])
    assert pd.api.types.is_datetime64_any_dtype(typed['date'])
    assert typed['passed'].dtype == bool
    print("  [PASS] Exercise 10: Type Conversion")

    # Test 11: Category analysis
    dept, avg_sal, n_remote = analyze_categories(emp_df)
    assert dept == 'Engineering'
    assert np.isclose(avg_sal, (90000 + 95000 + 88000 + 82000 + 91000) / 5)
    assert n_remote == 6
    print("  [PASS] Exercise 11: Category Analysis")

    # Test 12: From records
    cities = create_from_records()
    assert cities.index.name == 'city'
    assert 'Tokyo' in cities.index
    assert cities.loc['Tokyo', 'pop_millions'] == 13.9
    assert cities.shape == (5, 2)  # city is index, so 2 remaining columns
    print("  [PASS] Exercise 12: Create from Records")

    # Test 13: Advanced filtering
    td, ms = advanced_filtering(emp_df)
    assert set(td['department'].unique()) == {'Engineering', 'Sales'}
    assert len(td) == 7  # 5 Engineering + 2 Sales
    assert all(ms['salary'].between(70000, 90000))
    print("  [PASS] Exercise 13: Advanced Filtering")

    # Test 14: Ranking
    top3, young2, ranks = ranking_operations(emp_df)
    assert len(top3) == 3
    assert top3.iloc[0]['name'] == 'Charlie'  # 95000
    assert len(young2) == 2
    assert young2.iloc[0]['name'] == 'Bob'  # 25
    assert ranks.iloc[0] == ranks[emp_df['name'] == 'Alice'].values[0]
    print("  [PASS] Exercise 14: Ranking Operations")

    # Test 15: Department report
    report = department_report(emp_df)
    assert report.index.name == 'department'
    assert 'employee_count' in report.columns
    assert report.loc['Engineering', 'employee_count'] == 5
    assert report.loc['Marketing', 'employee_count'] == 3
    assert report.loc['Sales', 'employee_count'] == 2
    assert np.isclose(report.loc['Engineering', 'avg_salary'], 89200.0)
    print("  [PASS] Exercise 15: Department Report")

    print("\nAll 15 exercises passed!")
