# Module 04: Pandas Advanced

## Introduction

After mastering the basics, you're ready for the real power of pandas. This module covers
techniques that enable you to work efficiently with complex, real-world datasets.

**What You'll Learn:**
- GroupBy: Aggregate data across groups
- Merging and Joining: Combine DataFrames like SQL operations
- Reshaping: Pivot tables, melt, stack/unstack
- Missing Data: Handling NaN, dropna, fillna
- Method Chaining: Write readable, fluent code
- Apply/Map: Custom transformations
- Window Functions: Rolling averages, expanding operations
- MultiIndex: Multi-level row and column indices
- String Methods: Text operations on Series
- Datetime Methods: Time series manipulation
- Categorical Data: Memory-efficient category operations

---

## GroupBy Operations

GroupBy is one of pandas' most powerful features. It follows the "split-apply-combine" pattern.

### Basic GroupBy

```python
import pandas as pd
import numpy as np

# Sample data
df = pd.DataFrame({
    'department': ['Sales', 'Sales', 'Engineering', 'Engineering', 'HR', 'HR'],
    'employee': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank'],
    'salary': [70000, 65000, 95000, 92000, 55000, 58000],
    'bonus': [5000, 3000, 8000, 7000, 2000, 2500],
})

# Group by department and get mean salary
print(df.groupby('department')['salary'].mean())
# department
# Engineering    93500.0
# HR             56500.0
# Sales          67500.0
# Name: salary, dtype: float64

# Multiple aggregations
print(df.groupby('department').agg({
    'salary': ['mean', 'min', 'max', 'count'],
    'bonus': ['sum', 'mean']
}))
```

### Multiple GroupBy Keys

```python
# Group by multiple columns
df_sales = pd.DataFrame({
    'region': ['North', 'North', 'South', 'South', 'North', 'South'],
    'quarter': ['Q1', 'Q2', 'Q1', 'Q2', 'Q1', 'Q1'],
    'revenue': [100000, 120000, 90000, 95000, 110000, 85000],
})

# Group by region and quarter
grouped = df_sales.groupby(['region', 'quarter'])['revenue'].sum()
print(grouped)
# region  quarter
# North   Q1          210000
#         Q2          120000
# South   Q1           85000
#         Q2           95000
# Name: revenue, dtype: int64
```

### Custom Aggregation Functions

```python
def custom_agg(group):
    """Calculate percentage of max salary in group."""
    return (group / group.max() * 100).mean()

result = df.groupby('department')['salary'].apply(custom_agg)
print(result)
```

### GroupBy Transform

Transform allows you to return a Series with the same shape as the input.

```python
# Normalize salary within each department
df['salary_normalized'] = df.groupby('department')['salary'].transform(
    lambda x: (x - x.mean()) / x.std()
)

# Count employees per department
df['dept_size'] = df.groupby('department').transform('count')['employee']
```

---

## Merging and Joining DataFrames

SQL-style operations to combine DataFrames.

### merge (SQL-like joins)

```python
employees = pd.DataFrame({
    'emp_id': [1, 2, 3, 4],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'dept_id': [10, 20, 10, 20],
})

departments = pd.DataFrame({
    'dept_id': [10, 20, 30],
    'dept_name': ['Engineering', 'Sales', 'HR'],
})

# Inner join (default)
result = pd.merge(employees, departments, on='dept_id')
# Only rows with matching dept_ids

# Left join
result = pd.merge(employees, departments, on='dept_id', how='left')
# All rows from employees, matching data from departments

# Outer join
result = pd.merge(employees, departments, on='dept_id', how='outer')
# All rows from both DataFrames

# Join on different column names
result = pd.merge(employees, departments,
                  left_on='dept_id', right_on='dept_id')
```

### concat (Concatenation)

```python
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})

# Concatenate rows (axis=0 is default)
result = pd.concat([df1, df2], ignore_index=True)

# Concatenate columns (axis=1)
result = pd.concat([df1, df2], axis=1)
```

### join (Index-based join)

```python
df1 = pd.DataFrame({'A': [1, 2, 3]}, index=['a', 'b', 'c'])
df2 = pd.DataFrame({'B': [4, 5, 6]}, index=['a', 'b', 'c'])

# Join on index
result = df1.join(df2)
```

---

## Reshaping Data

Transform the shape and structure of DataFrames.

### pivot_table

```python
sales = pd.DataFrame({
    'date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02'],
    'region': ['East', 'West', 'East', 'West'],
    'revenue': [1000, 1500, 1200, 1300],
})

# Create pivot table
pivot = pd.pivot_table(sales, values='revenue', index='date',
                       columns='region', aggfunc='sum')
# region   East  West
# date
# 2024-01-01  1000  1500
# 2024-01-02  1200  1300
```

### melt (Unpivot)

```python
wide_df = pd.DataFrame({
    'product': ['A', 'B', 'C'],
    'Q1': [100, 200, 300],
    'Q2': [150, 250, 350],
})

# Unpivot: convert columns to rows
long_df = pd.melt(wide_df, id_vars=['product'],
                  var_name='quarter', value_name='revenue')
# product quarter  revenue
# A         Q1       100
# A         Q2       150
# B         Q1       200
```

### stack and unstack

```python
# Stack: pivot longer (convert columns to rows)
stacked = df.stack()

# Unstack: pivot wider (convert rows to columns)
unstacked = stacked.unstack()
```

---

## Missing Data Handling

Real data always has missing values. Pandas provides tools to handle them.

### Detecting Missing Data

```python
df = pd.DataFrame({
    'A': [1, 2, np.nan, 4],
    'B': [5, np.nan, np.nan, 8],
})

# Check for NaN values
print(df.isnull())          # Boolean DataFrame
print(df.isnull().sum())    # Count per column
print(df.isnull().any())    # Any missing per column

# Check for non-NaN values
print(df.notnull())
```

### Removing Missing Data

```python
# Drop rows with any NaN
df_clean = df.dropna()

# Drop rows where all values are NaN
df_clean = df.dropna(how='all')

# Drop columns with missing values
df_clean = df.dropna(axis=1)

# Drop rows where specific column is NaN
df_clean = df.dropna(subset=['A'])

# Drop rows with fewer than 2 non-NaN values
df_clean = df.dropna(thresh=2)
```

### Filling Missing Data

```python
# Fill with a constant value
df_filled = df.fillna(0)

# Forward fill (propagate last valid value)
df_filled = df.fillna(method='ffill')

# Backward fill (propagate next valid value)
df_filled = df.fillna(method='bfill')

# Fill with column-specific values
df_filled = df.fillna({'A': 0, 'B': -1})

# Fill with interpolation (useful for time series)
df_filled = df.interpolate()
```

---

## Method Chaining

Write readable, fluent code by chaining methods together.

```python
result = (df
    .query('salary > 60000')
    .groupby('department')['salary']
    .mean()
    .round(2)
    .sort_values(ascending=False)
)

# Complex example
result = (df
    .drop('unwanted_column', axis=1)
    .dropna()
    .groupby('department')
    .agg({'salary': 'mean', 'years_exp': 'max'})
    .rename(columns={'salary': 'avg_salary', 'years_exp': 'max_experience'})
    .sort_values('avg_salary', ascending=False)
)
```

---

## Apply and Map

Apply custom functions to Series and DataFrames.

### apply on Series

```python
s = pd.Series([1, 2, 3, 4, 5])

# Apply function to each element
result = s.apply(lambda x: x ** 2)

# Apply built-in function
result = s.apply(abs)

# Apply function returning Series (expands result)
result = s.apply(lambda x: pd.Series({'square': x**2, 'cube': x**3}))
```

### apply on DataFrame

```python
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
})

# Apply function to each row (axis=1)
result = df.apply(lambda row: row['A'] + row['B'], axis=1)

# Apply function to each column (axis=0, default)
result = df.apply(lambda col: col.mean())
```

### map on Series

```python
df = pd.DataFrame({
    'grade': ['A', 'B', 'C', 'D', 'F'],
})

# Map categorical values
grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
df['gpa'] = df['grade'].map(grade_points)
```

---

## Window Functions

Compute rolling statistics and expanding operations.

### Rolling Windows

```python
df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=10),
    'value': [10, 12, 11, 13, 15, 14, 16, 18, 17, 19],
})

# 3-day rolling mean
df['rolling_mean'] = df['value'].rolling(window=3).mean()

# 3-day rolling sum
df['rolling_sum'] = df['value'].rolling(window=3).sum()

# Min and max in rolling window
df['rolling_min'] = df['value'].rolling(window=3).min()
df['rolling_max'] = df['value'].rolling(window=3).max()

# Standard deviation of rolling window
df['rolling_std'] = df['value'].rolling(window=3).std()
```

### Expanding Windows

```python
# Expanding mean (grows from 1 to n)
df['expanding_mean'] = df['value'].expanding().mean()

# Expanding max
df['expanding_max'] = df['value'].expanding().max()
```

---

## MultiIndex

Work with multi-level indices for more complex data structures.

### Creating MultiIndex

```python
# From tuples
arrays = [
    ['A', 'A', 'B', 'B'],
    ['x', 'y', 'x', 'y'],
]
index = pd.MultiIndex.from_arrays(arrays, names=['letter', 'position'])
df = pd.DataFrame({'value': [1, 2, 3, 4]}, index=index)

# From product (cartesian product)
index = pd.MultiIndex.from_product([['A', 'B'], ['x', 'y']],
                                   names=['letter', 'position'])

# Using groupby
df = pd.DataFrame({
    'A': ['foo', 'foo', 'bar', 'bar'],
    'B': ['one', 'two', 'one', 'two'],
    'C': [1, 2, 3, 4],
})
multi_df = df.set_index(['A', 'B'])
```

### Accessing MultiIndex

```python
# Access by outer level
result = multi_df.loc['foo']

# Access by multiple levels
result = multi_df.loc[('foo', 'one')]

# Stack and unstack with MultiIndex
stacked = multi_df.stack()
unstacked = stacked.unstack()
```

---

## String Methods

Pandas provides string methods on Series with dtype 'object'.

### String Operations

```python
s = pd.Series(['apple', 'banana', 'cherry'])

# Convert to uppercase/lowercase
print(s.str.upper())
print(s.str.lower())

# String length
print(s.str.len())

# Substring
print(s.str[0:3])  # First 3 characters

# Contains (returns boolean)
print(s.str.contains('an'))  # True for 'banana'

# Replace
print(s.str.replace('a', 'o'))

# Split
print(s.str.split('a'))  # Split on 'a'

# Extract (using regex groups)
s2 = pd.Series(['2024-01-15', '2024-02-20', '2024-03-10'])
print(s2.str.extract(r'(\d{4})-(\d{2})-(\d{2})'))
```

---

## Datetime Methods

Work with time series data efficiently.

### Creating DateTime

```python
# From strings
dates = pd.to_datetime(['2024-01-15', '2024-02-20', '2024-03-10'])

# Using date_range
dates = pd.date_range('2024-01-01', periods=10, freq='D')  # Daily

# Frequency options: 'D', 'W', 'M', 'Q', 'Y', 'H', 'T' (minute), 'S' (second)
```

### Datetime Attributes and Methods

```python
dates = pd.to_datetime(['2024-01-15', '2024-02-20', '2024-03-10'])
s = pd.Series(dates)

# Extract components
print(s.dt.year)
print(s.dt.month)
print(s.dt.day)
print(s.dt.weekday)  # 0=Monday, 6=Sunday
print(s.dt.quarter)

# Time calculations
print(s.dt.days_in_month)

# Resample time series
ts = pd.Series(range(100), index=pd.date_range('2024-01-01', periods=100))
monthly = ts.resample('M').mean()  # Monthly average
```

---

## Categorical Data

Use categories for memory efficiency and meaningful orderings.

### Creating Categoricals

```python
# From list
s = pd.Categorical(['a', 'b', 'c', 'a', 'b', 'c'])
s_series = pd.Series(s)

# Specify categories explicitly
s = pd.Categorical(['a', 'b', 'c', 'a'],
                   categories=['a', 'b', 'c', 'd'],
                   ordered=False)

# From Series
s = pd.Series(['small', 'medium', 'large', 'small'])
s = s.astype('category')

# Ordered categories (for ordinal data)
size_order = pd.CategoricalDtype(categories=['small', 'medium', 'large'],
                                 ordered=True)
s = pd.Series(['small', 'medium', 'large']).astype(size_order)
s.cat.ordered  # True
```

### Categorical Methods

```python
s = pd.Series(pd.Categorical(['a', 'b', 'c', 'a']))

# Get categories
print(s.cat.categories)

# Add category
s = s.cat.add_categories(['d'])

# Remove unused categories
s = s.cat.remove_unused_categories()

# Rename categories
s = s.cat.rename_categories(['x', 'y', 'z'])
```

---

## Practical Example: Complete Analysis

```python
# Load employee data
df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=100),
    'department': np.random.choice(['Sales', 'Engineering', 'HR'], 100),
    'employee_id': np.random.randint(1, 20, 100),
    'revenue': np.random.randint(1000, 5000, 100),
    'hours': np.random.uniform(6, 10, 100),
})

# Method chaining analysis
result = (df
    .groupby(['date', 'department'])['revenue']
    .sum()
    .reset_index()
    .pivot_table(values='revenue', index='date', columns='department', fill_value=0)
    .rolling(window=7)
    .mean()
)

print(result)
```

This example demonstrates:
1. GroupBy aggregation
2. Resetting the index
3. Pivoting data
4. Rolling window calculations
5. Method chaining for readable code
