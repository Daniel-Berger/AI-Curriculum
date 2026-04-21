# Module 05: Polars - Modern DataFrames

## What is Polars?

Polars is a modern DataFrame library written in Rust with Python bindings. It's designed
to be faster, more efficient, and easier to use than pandas for many operations.

**Key Advantages:**
- Written in Rust: Much faster than pandas (which uses NumPy/C)
- Expression API: Composable, readable data transformations
- Lazy Evaluation: Optimize queries before executing
- Better Memory Usage: More efficient data structures
- Streaming: Handle datasets larger than RAM
- Type Safe: Strong typing catches errors early

**Swift Analogy:**
- Polars is like writing async/await code vs callback hell
- You describe the transformation, Polars optimizes and executes it
- Similar to SwiftUI's declarative approach vs UIKit's imperative

---

## Getting Started with Polars

```python
import polars as pl

# Check version
print(pl.__version__)

# Create a simple DataFrame
df = pl.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [30, 25, 35],
    'salary': [90000, 65000, 95000],
})

print(df)
# shape: (3, 3)
# ┌─────────┬─────┬────────┐
# │ name    ┆ age ┆ salary │
# │ ---     ┆ --- ┆ ---    │
# │ str     ┆ i64 ┆ i64    │
# ╞═════════╪═════╪════════╡
# │ Alice   ┆ 30  ┆ 90000  │
# │ Bob     ┆ 25  ┆ 65000  │
# │ Charlie ┆ 35  ┆ 95000  │
# └─────────┴─────┴────────┘
```

---

## The Expression API

The Polars Expression API is the core of its power. Expressions are lazy—they describe
transformations without executing them immediately.

### Basic Expressions

```python
import polars as pl

df = pl.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'department': ['Engineering', 'Sales', 'Engineering', 'Marketing'],
    'salary': [90000, 65000, 95000, 72000],
})

# Select columns using expressions
result = df.select(
    pl.col('name'),
    pl.col('salary') * 1.1  # 10% raise
)

# Multiple operations
result = df.select(
    pl.col('name'),
    (pl.col('salary') * 1.1).alias('new_salary'),
)
```

### Filtering with Expressions

```python
# Boolean expressions
result = df.filter(pl.col('salary') > 80000)

# Multiple conditions
result = df.filter(
    (pl.col('salary') > 70000) &
    (pl.col('department') == 'Engineering')
)

# Using between
result = df.filter(pl.col('salary').between(60000, 90000))

# Is null checks
result = df.filter(pl.col('salary').is_not_null())
```

### String and Numerical Operations

```python
# String methods
result = df.select(
    pl.col('name').str.to_uppercase(),
    pl.col('name').str.lengths(),
)

# Numerical operations
result = df.select(
    pl.col('salary'),
    pl.col('salary').log(),
    pl.col('salary').round(-3),  # Round to nearest 1000
)
```

---

## Lazy Evaluation

Lazy evaluation is Polars' secret weapon. Instead of executing immediately,
you build a query plan that Polars optimizes.

### Eager vs Lazy

```python
# EAGER: Executes immediately (traditional)
result = df.filter(pl.col('salary') > 80000).select(['name', 'salary'])

# LAZY: Builds execution plan, optimizes, then runs
lazy_df = df.lazy()
result = (lazy_df
    .filter(pl.col('salary') > 80000)
    .select(['name', 'salary'])
    .collect()  # Execute here
)

# With lazy, Polars can optimize the query before running
# For example, it will push the select (projection) earlier
```

### Building Complex Lazy Queries

```python
lazy_result = (df.lazy()
    .filter(pl.col('salary') > 60000)
    .groupby('department')
    .agg(
        pl.col('salary').mean().alias('avg_salary'),
        pl.col('salary').max().alias('max_salary'),
        pl.col('name').count().alias('count')
    )
    .sort('avg_salary', descending=True)
    .collect()
)
```

---

## GroupBy and Aggregations

GroupBy works similarly to pandas but with the expression API.

### Basic GroupBy

```python
result = df.groupby('department').agg(
    pl.col('salary').mean().alias('avg_salary'),
    pl.col('salary').max().alias('max_salary'),
    pl.col('name').count().alias('count'),
)

print(result)
```

### GroupBy with Multiple Columns

```python
df_sales = pl.DataFrame({
    'region': ['North', 'North', 'South', 'South'],
    'quarter': ['Q1', 'Q2', 'Q1', 'Q2'],
    'revenue': [100000, 120000, 90000, 95000],
})

result = df_sales.groupby(['region', 'quarter']).agg(
    pl.col('revenue').sum().alias('total_revenue')
)
```

### Advanced Aggregations

```python
result = df.groupby('department').agg(
    pl.col('salary').mean().alias('avg_salary'),
    pl.col('salary').median().alias('median_salary'),
    pl.col('salary').std().alias('std_salary'),
    pl.col('name').count().alias('employee_count'),
    # Multiple aggregations on same column
    pl.col('salary').min().alias('min_salary'),
    pl.col('salary').max().alias('max_salary'),
)
```

---

## Joins

Polars supports SQL-style joins with intuitive syntax.

### Types of Joins

```python
employees = pl.DataFrame({
    'emp_id': [1, 2, 3, 4],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'dept_id': [10, 20, 10, 30],
})

departments = pl.DataFrame({
    'dept_id': [10, 20, 40],
    'dept_name': ['Engineering', 'Sales', 'Marketing'],
})

# Inner join (default)
result = employees.join(departments, on='dept_id', how='inner')

# Left join
result = employees.join(departments, on='dept_id', how='left')

# Outer join
result = employees.join(departments, on='dept_id', how='outer')

# Right join
result = employees.join(departments, on='dept_id', how='right')

# Cross join (cartesian product)
result = employees.join(departments, how='cross')
```

### Multi-key Joins

```python
# Join on multiple columns
result = df1.join(df2, on=['year', 'month'])

# Join with different column names
result = df1.join(df2, left_on='dept_id', right_on='id')
```

---

## Common Transformations

### Select and With Columns

```python
# Select specific columns
result = df.select(['name', 'salary'])

# Select with expressions
result = df.select(
    'name',
    pl.col('salary').alias('annual_salary'),
)

# Add columns (keeps existing)
result = df.with_columns(
    (pl.col('salary') / 12).alias('monthly_salary'),
    (pl.col('salary') * 1.1).alias('new_salary'),
)

# Rename columns
result = df.rename({'old_name': 'new_name'})

# Drop columns
result = df.drop(['unwanted_col'])
```

### Sorting and Unique

```python
# Sort ascending
result = df.sort('salary')

# Sort descending
result = df.sort('salary', descending=True)

# Multi-column sort
result = df.sort(['department', 'salary'], descending=[False, True])

# Get unique rows
result = df.unique()

# Get unique values in a column
result = df.select(pl.col('department').unique())
```

### Filtering and Subsetting

```python
# Basic filter
result = df.filter(pl.col('salary') > 80000)

# Filter with multiple conditions
result = df.filter(
    (pl.col('salary') > 70000) |
    (pl.col('department') == 'Engineering')
)

# Get first/last n rows
result = df.head(10)
result = df.tail(5)

# Sample rows
result = df.sample(n=10)
```

---

## Pandas vs Polars Comparison

### Basic Operations

**Pandas:**
```python
import pandas as pd

df = pd.DataFrame({
    'department': ['Sales', 'Sales', 'Engineering', 'Engineering'],
    'salary': [65000, 70000, 90000, 95000],
})

result = df.groupby('department')['salary'].mean()
```

**Polars:**
```python
import polars as pl

df = pl.DataFrame({
    'department': ['Sales', 'Sales', 'Engineering', 'Engineering'],
    'salary': [65000, 70000, 90000, 95000],
})

result = df.groupby('department').agg(pl.col('salary').mean())
```

### Filtering

**Pandas:**
```python
result = df[(df['salary'] > 60000) & (df['department'] == 'Engineering')]
```

**Polars:**
```python
result = df.filter(
    (pl.col('salary') > 60000) &
    (pl.col('department') == 'Engineering')
)
```

### Adding Columns

**Pandas:**
```python
df['salary_k'] = df['salary'] / 1000
df['new_salary'] = df['salary'] * 1.1
```

**Polars:**
```python
df = df.with_columns(
    (pl.col('salary') / 1000).alias('salary_k'),
    (pl.col('salary') * 1.1).alias('new_salary'),
)
```

### Aggregations

**Pandas:**
```python
result = df.groupby('department').agg({
    'salary': ['mean', 'max', 'count']
})
```

**Polars:**
```python
result = df.groupby('department').agg(
    pl.col('salary').mean().alias('avg_salary'),
    pl.col('salary').max().alias('max_salary'),
    pl.col('salary').count().alias('count'),
)
```

### Joining

**Pandas:**
```python
result = pd.merge(employees, departments, on='dept_id', how='inner')
```

**Polars:**
```python
result = employees.join(departments, on='dept_id', how='inner')
```

---

## Performance Comparison

Polars is significantly faster for large datasets:

```python
import polars as pl
import pandas as pd
import time

# Create a large dataset
n = 1_000_000

data = {
    'group': ['A', 'B', 'C', 'D'] * (n // 4),
    'value': range(n),
}

# Polars
df_pl = pl.DataFrame(data)
start = time.time()
result_pl = df_pl.groupby('group').agg(pl.col('value').mean())
polars_time = time.time() - start

# Pandas
df_pd = pd.DataFrame(data)
start = time.time()
result_pd = df_pd.groupby('group')['value'].mean()
pandas_time = time.time() - start

print(f"Polars: {polars_time:.4f}s")
print(f"Pandas: {pandas_time:.4f}s")
# Polars is typically 5-10x faster
```

---

## When to Use Polars

**Use Polars when:**
- Working with large datasets (100MB+)
- Performance is critical
- You want readable, composable expressions
- You need lazy evaluation and query optimization
- You're doing complex transformations

**Use Pandas when:**
- Working with small-medium datasets
- You need extensive statistical methods
- You need .iloc-style positional indexing
- The ecosystem integration (matplotlib, scikit-learn) is crucial
- You're comfortable with the existing API

---

## Key Takeaways

1. **Expressions**: Use Polars' expression API for composable transformations
2. **Lazy Evaluation**: Let Polars optimize your queries
3. **Type Safety**: Polars catches type errors before execution
4. **Performance**: Rust implementation is much faster than pandas
5. **Modern Design**: Polars' API is cleaner and more intuitive than pandas
