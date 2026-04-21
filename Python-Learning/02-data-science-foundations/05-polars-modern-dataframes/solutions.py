"""
Module 05: Polars - Modern DataFrames - Solutions
================================================

Complete solutions for all 12 exercises.
Run this file to verify all solutions pass:
    python solutions.py
"""

import polars as pl


# ---------------------------------------------------------------------------
# Exercise 1: Creating DataFrames
# ---------------------------------------------------------------------------
def create_dataframe() -> pl.DataFrame:
    """
    Create a Polars DataFrame with employee data.

    Data:
        name: ['Alice', 'Bob', 'Charlie', 'Diana']
        department: ['Engineering', 'Sales', 'Engineering', 'Marketing']
        salary: [90000, 65000, 95000, 72000]
        years_exp: [5, 2, 10, 3]

    Return the DataFrame.
    """
    df = pl.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'department': ['Engineering', 'Sales', 'Engineering', 'Marketing'],
        'salary': [90000, 65000, 95000, 72000],
        'years_exp': [5, 2, 10, 3],
    })

    return df


# ---------------------------------------------------------------------------
# Exercise 2: Basic Select with Expressions
# ---------------------------------------------------------------------------
def select_with_expressions(df: pl.DataFrame) -> pl.DataFrame:
    """
    Use select and expressions to:
    1. Keep 'name' and 'salary' columns
    2. Add 'salary_k': salary divided by 1000
    3. Add 'monthly_salary': salary divided by 12

    Args:
        df: Employee DataFrame from exercise 1

    Return DataFrame with these columns.
    """
    result = df.select(
        'name',
        'salary',
        (pl.col('salary') / 1000).alias('salary_k'),
        (pl.col('salary') / 12).alias('monthly_salary'),
    )

    return result


# ---------------------------------------------------------------------------
# Exercise 3: Filtering with Expressions
# ---------------------------------------------------------------------------
def filter_with_expressions(df: pl.DataFrame) -> pl.DataFrame:
    """
    Filter to get:
    - salary > 70000 AND
    - department is 'Engineering'

    Args:
        df: Employee DataFrame from exercise 1

    Return filtered DataFrame.
    """
    result = df.filter(
        (pl.col('salary') > 70000) &
        (pl.col('department') == 'Engineering')
    )

    return result


# ---------------------------------------------------------------------------
# Exercise 4: With Columns (Add Computed Columns)
# ---------------------------------------------------------------------------
def with_columns_operation(df: pl.DataFrame) -> pl.DataFrame:
    """
    Add columns to the DataFrame:
    1. 'salary_per_year_exp': salary / years_exp
    2. 'senior': True if years_exp >= 5, False otherwise

    Args:
        df: Employee DataFrame from exercise 1

    Return DataFrame with new columns added.
    """
    result = df.with_columns(
        (pl.col('salary') / pl.col('years_exp')).alias('salary_per_year_exp'),
        (pl.col('years_exp') >= 5).alias('senior'),
    )

    return result


# ---------------------------------------------------------------------------
# Exercise 5: Sorting
# ---------------------------------------------------------------------------
def sort_dataframe(df: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """
    Create two sorted versions:
    1. by_salary_desc: sorted by salary descending
    2. by_dept_then_exp: sorted by department ascending,
       then years_exp descending within each department

    Args:
        df: Employee DataFrame from exercise 1

    Return tuple of (by_salary_desc, by_dept_then_exp).
    """
    by_salary_desc = df.sort('salary', descending=True)
    by_dept_then_exp = df.sort(['department', 'years_exp'],
                               descending=[False, True])

    return by_salary_desc, by_dept_then_exp


# ---------------------------------------------------------------------------
# Exercise 6: GroupBy Basic Aggregation
# ---------------------------------------------------------------------------
def groupby_aggregation(df: pl.DataFrame) -> pl.DataFrame:
    """
    Group by department and calculate:
    - 'employee_count': count of employees
    - 'avg_salary': mean salary
    - 'max_salary': maximum salary

    Args:
        df: Employee DataFrame from exercise 1

    Return aggregated DataFrame.
    """
    result = df.groupby('department').agg(
        pl.col('name').count().alias('employee_count'),
        pl.col('salary').mean().alias('avg_salary'),
        pl.col('salary').max().alias('max_salary'),
    )

    return result


# ---------------------------------------------------------------------------
# Exercise 7: GroupBy Multiple Aggregations
# ---------------------------------------------------------------------------
def groupby_multiple_agg() -> pl.DataFrame:
    """
    Create sales data and group by region:

    Data:
        region: ['North', 'North', 'South', 'South', 'East', 'East']
        quarter: ['Q1', 'Q2', 'Q1', 'Q2', 'Q1', 'Q2']
        revenue: [100000, 120000, 90000, 95000, 110000, 125000]

    Group by region and calculate:
    - 'total_revenue': sum of revenue
    - 'avg_revenue': mean revenue
    - 'num_quarters': count of quarters
    - 'max_revenue': maximum revenue

    Return grouped DataFrame.
    """
    df = pl.DataFrame({
        'region': ['North', 'North', 'South', 'South', 'East', 'East'],
        'quarter': ['Q1', 'Q2', 'Q1', 'Q2', 'Q1', 'Q2'],
        'revenue': [100000, 120000, 90000, 95000, 110000, 125000],
    })

    result = df.groupby('region').agg(
        pl.col('revenue').sum().alias('total_revenue'),
        pl.col('revenue').mean().alias('avg_revenue'),
        pl.col('quarter').count().alias('num_quarters'),
        pl.col('revenue').max().alias('max_revenue'),
    )

    return result


# ---------------------------------------------------------------------------
# Exercise 8: Inner Join
# ---------------------------------------------------------------------------
def join_dataframes() -> pl.DataFrame:
    """
    Perform an inner join of employees and departments.

    Employees:
        emp_id: [1, 2, 3, 4]
        name: ['Alice', 'Bob', 'Charlie', 'Diana']
        dept_id: [10, 20, 10, 30]

    Departments:
        dept_id: [10, 20, 40]
        dept_name: ['Engineering', 'Sales', 'Marketing']

    Join on dept_id (inner join).
    Return the joined DataFrame.
    """
    employees = pl.DataFrame({
        'emp_id': [1, 2, 3, 4],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'dept_id': [10, 20, 10, 30],
    })

    departments = pl.DataFrame({
        'dept_id': [10, 20, 40],
        'dept_name': ['Engineering', 'Sales', 'Marketing'],
    })

    result = employees.join(departments, on='dept_id', how='inner')

    return result


# ---------------------------------------------------------------------------
# Exercise 9: Left Join
# ---------------------------------------------------------------------------
def left_join_dataframes() -> pl.DataFrame:
    """
    Perform a left join: keep all employees, add department names where available.
    Use same data as Exercise 8.

    Return the left-joined DataFrame.
    """
    employees = pl.DataFrame({
        'emp_id': [1, 2, 3, 4],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'dept_id': [10, 20, 10, 30],
    })

    departments = pl.DataFrame({
        'dept_id': [10, 20, 40],
        'dept_name': ['Engineering', 'Sales', 'Marketing'],
    })

    result = employees.join(departments, on='dept_id', how='left')

    return result


# ---------------------------------------------------------------------------
# Exercise 10: Lazy Evaluation
# ---------------------------------------------------------------------------
def lazy_evaluation() -> pl.DataFrame:
    """
    Build a lazy query that:
    1. Filters for salary > 80000
    2. Groups by department
    3. Calculates mean salary per department
    4. Sorts by department ascending
    5. Collects the result

    Data:
        name: ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
        department: ['Sales', 'Sales', 'Engineering', 'Engineering', 'Engineering']
        salary: [70000, 75000, 85000, 90000, 95000]

    Return the collected result.
    """
    df = pl.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'department': ['Sales', 'Sales', 'Engineering', 'Engineering', 'Engineering'],
        'salary': [70000, 75000, 85000, 90000, 95000],
    })

    result = (df.lazy()
        .filter(pl.col('salary') > 80000)
        .groupby('department')
        .agg(pl.col('salary').mean().alias('avg_salary'))
        .sort('department')
        .collect()
    )

    return result


# ---------------------------------------------------------------------------
# Exercise 11: String Operations
# ---------------------------------------------------------------------------
def string_operations() -> tuple[pl.DataFrame, pl.Series]:
    """
    Perform string operations on text data.

    Data:
        name: ['alice', 'bob', 'charlie', 'diana']
        email: ['alice@example.com', 'bob@example.com',
                'charlie@example.com', 'diana@example.com']

    Create:
    1. df_uppercase: DataFrame with 'name' converted to uppercase
    2. email_lengths: Series with length of each email

    Return tuple of (df_uppercase, email_lengths).
    """
    df = pl.DataFrame({
        'name': ['alice', 'bob', 'charlie', 'diana'],
        'email': ['alice@example.com', 'bob@example.com',
                  'charlie@example.com', 'diana@example.com'],
    })

    df_uppercase = df.with_columns(
        pl.col('name').str.to_uppercase()
    )

    email_lengths = df['email'].str.lengths()

    return df_uppercase, email_lengths


# ---------------------------------------------------------------------------
# Exercise 12: Unique and Filtering
# ---------------------------------------------------------------------------
def unique_and_filter() -> tuple[pl.Series, pl.DataFrame]:
    """
    Work with categorical data.

    Data:
        product: ['A', 'B', 'A', 'C', 'B', 'A']
        region: ['North', 'South', 'North', 'East', 'South', 'East']
        sales: [1000, 1200, 950, 1100, 1050, 1300]

    Create:
    1. unique_products: unique product values (as Series)
    2. filtered: rows where product is 'A'

    Return tuple of (unique_products, filtered).
    """
    df = pl.DataFrame({
        'product': ['A', 'B', 'A', 'C', 'B', 'A'],
        'region': ['North', 'South', 'North', 'East', 'South', 'East'],
        'sales': [1000, 1200, 950, 1100, 1050, 1300],
    })

    unique_products = df['product'].unique().sort()
    filtered = df.filter(pl.col('product') == 'A')

    return unique_products, filtered


# ===========================================================================
# Tests
# ===========================================================================
if __name__ == "__main__":
    print("Running Polars solution tests...\n")

    # Test 1: Create DataFrame
    df = create_dataframe()
    assert df.shape == (4, 4)
    assert df.columns == ['name', 'department', 'salary', 'years_exp']
    assert df['salary'].to_list() == [90000, 65000, 95000, 72000]
    print("  [PASS] Exercise 1: Create DataFrame")

    # Test 2: Select with expressions
    result = select_with_expressions(df)
    assert len(result.columns) == 4
    assert 'salary_k' in result.columns
    assert 'monthly_salary' in result.columns
    assert result['salary_k'][0] == 90.0
    print("  [PASS] Exercise 2: Select with Expressions")

    # Test 3: Filtering
    filtered = filter_with_expressions(df)
    assert len(filtered) == 2  # Alice and Charlie
    assert filtered['department'].unique().to_list() == ['Engineering']
    print("  [PASS] Exercise 3: Filter with Expressions")

    # Test 4: With columns
    with_cols = with_columns_operation(df)
    assert 'salary_per_year_exp' in with_cols.columns
    assert 'senior' in with_cols.columns
    assert with_cols['senior'][0] == True  # Alice, 5 years
    assert with_cols['senior'][1] == False  # Bob, 2 years
    print("  [PASS] Exercise 4: With Columns Operation")

    # Test 5: Sorting
    by_sal, by_dept = sort_dataframe(df)
    assert by_sal['name'][0] == 'Charlie'  # Highest salary
    assert by_sal['name'][-1] == 'Bob'  # Lowest salary
    print("  [PASS] Exercise 5: Sort DataFrame")

    # Test 6: GroupBy aggregation
    grouped = groupby_aggregation(df)
    assert len(grouped) == 3  # 3 departments
    assert 'employee_count' in grouped.columns
    assert 'avg_salary' in grouped.columns
    assert 'max_salary' in grouped.columns
    print("  [PASS] Exercise 6: GroupBy Aggregation")

    # Test 7: GroupBy multiple agg
    grouped_multi = groupby_multiple_agg()
    assert 'total_revenue' in grouped_multi.columns
    assert 'avg_revenue' in grouped_multi.columns
    assert 'num_quarters' in grouped_multi.columns
    print("  [PASS] Exercise 7: GroupBy Multiple Aggregations")

    # Test 8: Inner join
    joined = join_dataframes()
    assert len(joined) == 2  # Only emp_ids 1 and 3
    assert 'dept_name' in joined.columns
    print("  [PASS] Exercise 8: Inner Join")

    # Test 9: Left join
    left_joined = left_join_dataframes()
    assert len(left_joined) == 4  # All employees
    print("  [PASS] Exercise 9: Left Join")

    # Test 10: Lazy evaluation
    lazy_result = lazy_evaluation()
    assert 'department' in lazy_result.columns
    assert len(lazy_result) > 0
    print("  [PASS] Exercise 10: Lazy Evaluation")

    # Test 11: String operations
    df_upper, email_lens = string_operations()
    assert 'name' in df_upper.columns
    assert df_upper['name'][0] == 'ALICE'
    assert len(email_lens) == 4
    assert email_lens[0] == 20  # 'alice@example.com'
    print("  [PASS] Exercise 11: String Operations")

    # Test 12: Unique and filter
    unique_prods, filtered = unique_and_filter()
    assert len(unique_prods) == 3  # A, B, C
    assert len(filtered) == 3  # 3 rows with product A
    print("  [PASS] Exercise 12: Unique and Filter")

    print("\nAll 12 solutions passed!")
