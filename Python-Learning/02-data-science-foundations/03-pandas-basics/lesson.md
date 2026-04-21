# Module 03: Pandas Basics

## What is Pandas?

Pandas is Python's premier library for working with tabular (spreadsheet-like) data.
If NumPy is the `Accelerate` framework, Pandas is like a combination of `UITableView`
data sources, Core Data queries, and Excel -- but in code.

**Key concepts:**
- **Series**: A labeled 1D array (like a column in a spreadsheet)
- **DataFrame**: A 2D labeled table (like a spreadsheet or SQL table)
- Built on top of NumPy -- inherits its performance for numerical operations
- Handles mixed data types, missing values, dates, strings, categories

```python
import pandas as pd
import numpy as np

print(pd.__version__)
```

**Swift analogy:**
| Swift/iOS            | Pandas                    |
|---------------------|---------------------------|
| `[String: [Any]]`  | `DataFrame`               |
| `Array<T>`          | `Series`                  |
| Core Data fetch     | `df.query()` / `df.loc[]` |
| `Codable` decode    | `pd.read_csv()`           |
| `JSONSerialization` | `pd.read_json()`          |

---

## Series

A Series is a 1D labeled array. Think of it as a dictionary with integer or custom keys
that also supports vectorized operations.

### Creating a Series

```python
import pandas as pd
import numpy as np

# From a list
s = pd.Series([10, 20, 30, 40, 50])
print(s)
# 0    10
# 1    20
# 2    30
# 3    40
# 4    50
# dtype: int64

# With custom index
s = pd.Series([10, 20, 30], index=['a', 'b', 'c'])
print(s['a'])    # 10
print(s[0])      # 10 (positional also works)

# From a dictionary
d = {'apple': 3, 'banana': 5, 'cherry': 2}
s = pd.Series(d)
print(s)
# apple     3
# banana    5
# cherry    2

# From a NumPy array
arr = np.random.randn(5)
s = pd.Series(arr, name='random_values')
```

### Series Operations

```python
s = pd.Series([10, 20, 30, 40, 50], index=['a', 'b', 'c', 'd', 'e'])

# Vectorized operations (like NumPy)
print(s * 2)          # Element-wise multiply
print(s > 25)         # Boolean mask
print(s[s > 25])      # Filter: c=30, d=40, e=50

# Aggregation
print(s.sum())        # 150
print(s.mean())       # 30.0
print(s.std())        # 15.81...
print(s.describe())   # Summary statistics

# String index operations
print(s.index)        # Index(['a', 'b', 'c', 'd', 'e'], dtype='object')
print('a' in s)       # True (check if index label exists)

# Alignment: operations on Series with different indices auto-align
s1 = pd.Series([1, 2, 3], index=['a', 'b', 'c'])
s2 = pd.Series([10, 20, 30], index=['b', 'c', 'd'])
result = s1 + s2
print(result)
# a     NaN    (no 'a' in s2)
# b    12.0    (2 + 10)
# c    23.0    (3 + 20)
# d     NaN    (no 'd' in s1)
# This auto-alignment is unique to Pandas!
```

---

## DataFrame

A DataFrame is a 2D labeled data structure -- the workhorse of Pandas.

### Creating DataFrames

```python
import pandas as pd

# From a dictionary of lists (most common)
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'age': [30, 25, 35, 28],
    'city': ['NYC', 'LA', 'Chicago', 'NYC'],
    'salary': [70000, 65000, 80000, 72000],
})
print(df)
#       name  age     city  salary
# 0    Alice   30      NYC   70000
# 1      Bob   25       LA   65000
# 2  Charlie   35  Chicago   80000
# 3    Diana   28      NYC   72000

# From a list of dictionaries
records = [
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25},
]
df = pd.DataFrame(records)

# From a list of lists
data = [['Alice', 30], ['Bob', 25]]
df = pd.DataFrame(data, columns=['name', 'age'])

# From a NumPy array
arr = np.random.randn(5, 3)
df = pd.DataFrame(arr, columns=['feature_1', 'feature_2', 'feature_3'])

# With custom index
df = pd.DataFrame(
    {'val': [10, 20, 30]},
    index=['row_a', 'row_b', 'row_c']
)
```

### DataFrame Attributes

```python
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [30, 25, 35],
    'salary': [70000, 65000, 80000],
})

print(df.shape)       # (3, 3) -- 3 rows, 3 columns
print(df.columns)     # Index(['name', 'age', 'salary'], dtype='object')
print(df.index)       # RangeIndex(start=0, stop=3, step=1)
print(df.dtypes)      # name: object, age: int64, salary: int64
print(df.info())      # Detailed info: columns, non-null counts, dtypes, memory
print(len(df))        # 3 (number of rows)
print(df.values)      # Underlying NumPy array (2D)
```

---

## Reading Data

### CSV files

```python
# Read CSV
df = pd.read_csv('data.csv')

# Common parameters
df = pd.read_csv(
    'data.csv',
    sep=',',                    # Delimiter (default comma)
    header=0,                   # Row number for column names (0 = first row)
    index_col='id',             # Use a column as the index
    usecols=['name', 'age'],    # Only read specific columns
    dtype={'age': int},         # Specify dtypes
    na_values=['N/A', 'null'],  # Additional strings to treat as NaN
    nrows=100,                  # Only read first 100 rows
    parse_dates=['date_col'],   # Parse date columns automatically
    encoding='utf-8',           # File encoding
)

# Read from URL
df = pd.read_csv('https://example.com/data.csv')

# Read TSV (tab-separated)
df = pd.read_csv('data.tsv', sep='\t')
```

### Other formats

```python
# JSON
df = pd.read_json('data.json')
df = pd.read_json('data.json', orient='records')  # List of dicts

# Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# Parquet (fast, columnar format -- increasingly popular)
df = pd.read_parquet('data.parquet')

# SQL (requires SQLAlchemy)
# from sqlalchemy import create_engine
# engine = create_engine('sqlite:///database.db')
# df = pd.read_sql('SELECT * FROM users', engine)

# From clipboard (handy for quick exploration)
# df = pd.read_clipboard()

# From a string (useful for testing)
from io import StringIO
csv_string = """name,age,city
Alice,30,NYC
Bob,25,LA"""
df = pd.read_csv(StringIO(csv_string))
```

---

## Indexing: loc, iloc, at, iat

This is one of the most important topics in Pandas. The difference between
`loc` and `iloc` trips up everyone at first.

### loc — Label-based indexing

```python
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'age': [30, 25, 35, 28],
    'salary': [70000, 65000, 80000, 72000],
}, index=['a', 'b', 'c', 'd'])

# Single element
print(df.loc['a', 'name'])        # 'Alice'

# Single row (returns Series)
print(df.loc['a'])
# name      Alice
# age          30
# salary    70000

# Multiple rows
print(df.loc[['a', 'c']])         # Rows 'a' and 'c'

# Slice (INCLUSIVE of both ends -- different from Python!)
print(df.loc['a':'c'])            # Rows 'a', 'b', AND 'c'

# Row and column selection
print(df.loc['a':'c', 'name':'age'])  # Rows a-c, columns name-age

# Boolean indexing with loc
print(df.loc[df['age'] > 28])     # Rows where age > 28
```

### iloc — Integer position-based indexing

```python
# Same DataFrame
# iloc uses integer positions (0-based), like Swift array subscripts

# Single element
print(df.iloc[0, 0])             # 'Alice' (row 0, col 0)

# Single row
print(df.iloc[0])                # First row

# Multiple rows
print(df.iloc[[0, 2]])           # Rows 0 and 2

# Slice (EXCLUSIVE of end -- normal Python slicing)
print(df.iloc[0:2])              # Rows 0 and 1 (NOT 2)

# Row and column slicing
print(df.iloc[0:2, 0:2])        # First 2 rows, first 2 columns

# Last row
print(df.iloc[-1])               # Diana's row
```

### at and iat — Fast scalar access

```python
# at: label-based, single value (faster than loc for scalars)
print(df.at['a', 'name'])       # 'Alice'

# iat: integer-based, single value (faster than iloc for scalars)
print(df.iat[0, 0])             # 'Alice'

# Use at/iat when you know you need exactly one value
# They are faster but raise errors for non-scalar results
```

### Key Difference Summary

```
loc['a':'c']    -> includes 'c'  (label-based, inclusive)
iloc[0:2]       -> excludes 2    (position-based, exclusive like Python)
at['a', 'name'] -> single value  (label-based, scalar only)
iat[0, 0]       -> single value  (position-based, scalar only)
```

---

## Boolean Filtering

```python
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'age': [30, 25, 35, 28, 32],
    'dept': ['Engineering', 'Marketing', 'Engineering', 'Marketing', 'Engineering'],
    'salary': [90000, 65000, 95000, 72000, 88000],
})

# Single condition
young = df[df['age'] < 30]
engineers = df[df['dept'] == 'Engineering']

# Multiple conditions (& = and, | = or, ~ = not)
# ALWAYS use parentheses around each condition!
senior_engineers = df[(df['dept'] == 'Engineering') & (df['age'] > 30)]

# isin -- like Swift's contains
target_depts = ['Engineering', 'Marketing']
filtered = df[df['dept'].isin(target_depts)]

# String methods (str accessor)
starts_with_a = df[df['name'].str.startswith('A')]
has_e = df[df['name'].str.contains('e', case=False)]

# between
mid_salary = df[df['salary'].between(70000, 90000)]

# query method (string-based, often cleaner)
result = df.query('age > 28 and dept == "Engineering"')
result = df.query('salary > @min_salary', local_dict={'min_salary': 80000})
# Or with a variable:
min_sal = 80000
result = df.query('salary > @min_sal')
```

---

## Column Operations

### Accessing columns

```python
df = pd.DataFrame({
    'name': ['Alice', 'Bob'],
    'age': [30, 25],
    'salary': [70000, 65000],
})

# Dot notation (convenient but limited)
print(df.name)         # Works, but can conflict with methods

# Bracket notation (always works -- preferred)
print(df['name'])      # Single column -> Series
print(df[['name', 'age']])  # Multiple columns -> DataFrame
```

### Adding columns

```python
# Direct assignment
df['bonus'] = df['salary'] * 0.1
df['is_senior'] = df['age'] >= 30

# From a conditional
df['level'] = np.where(df['age'] >= 30, 'Senior', 'Junior')

# Using assign (returns new DataFrame, doesn't modify original)
df2 = df.assign(
    tax=df['salary'] * 0.3,
    net_pay=lambda x: x['salary'] - x['salary'] * 0.3,
)
```

### Renaming columns

```python
# Rename specific columns
df = df.rename(columns={'name': 'employee_name', 'age': 'employee_age'})

# Rename all columns
df.columns = ['emp_name', 'emp_age', 'emp_salary', 'emp_bonus', 'emp_senior', 'emp_level']

# Rename with a function
df = df.rename(columns=str.upper)          # All caps
df = df.rename(columns=str.lower)          # All lower
df = df.rename(columns=lambda x: x.strip())  # Remove whitespace
```

### Dropping columns

```python
# Drop columns (returns new DataFrame by default)
df_slim = df.drop(columns=['bonus', 'is_senior'])

# Drop in place
df.drop(columns=['bonus'], inplace=True)  # Modifies df directly

# Drop by position
df_slim = df.iloc[:, :3]  # Keep first 3 columns
```

---

## Sorting

```python
df = pd.DataFrame({
    'name': ['Charlie', 'Alice', 'Bob', 'Diana'],
    'age': [35, 30, 25, 30],
    'salary': [80000, 70000, 65000, 72000],
})

# Sort by a column
df_sorted = df.sort_values('age')

# Sort descending
df_sorted = df.sort_values('salary', ascending=False)

# Sort by multiple columns
df_sorted = df.sort_values(['age', 'salary'], ascending=[True, False])
# First by age ascending, then by salary descending within same age

# Sort by index
df_sorted = df.sort_index()

# Get top/bottom N
top_3 = df.nlargest(3, 'salary')
bottom_2 = df.nsmallest(2, 'age')

# Rank
df['salary_rank'] = df['salary'].rank(ascending=False)
```

---

## Basic Statistics

```python
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'dept': ['Eng', 'Mkt', 'Eng', 'Mkt', 'Eng'],
    'age': [30, 25, 35, 28, 32],
    'salary': [90000, 65000, 95000, 72000, 88000],
})

# describe() -- summary stats for numerical columns
print(df.describe())
#              age        salary
# count   5.000000      5.000000
# mean   30.000000  82000.000000
# std     3.807887  13038.404811
# min    25.000000  65000.000000
# 25%    28.000000  72000.000000
# 50%    30.000000  88000.000000
# 75%    32.000000  90000.000000
# max    35.000000  95000.000000

# For non-numeric columns
print(df['dept'].describe())
# count     5
# unique    2
# top       Eng
# freq      3

# Value counts (like a histogram for categorical data)
print(df['dept'].value_counts())
# Eng    3
# Mkt    2

# Unique values
print(df['dept'].unique())      # ['Eng' 'Mkt']
print(df['dept'].nunique())     # 2

# Correlations
print(df[['age', 'salary']].corr())

# Individual stats
print(df['salary'].mean())       # 82000.0
print(df['salary'].median())     # 88000.0
print(df['salary'].std())        # 13038.4...
print(df['salary'].min())        # 65000
print(df['salary'].max())        # 95000
print(df['salary'].sum())        # 410000
print(df['salary'].quantile(0.75))  # 90000.0
```

---

## Data Types and Conversion

### Checking types

```python
df = pd.DataFrame({
    'id': ['001', '002', '003'],
    'value': ['10.5', '20.3', '30.1'],
    'date': ['2024-01-01', '2024-02-15', '2024-03-20'],
    'active': [1, 0, 1],
})

print(df.dtypes)
# id        object     (string stored as object)
# value     object     (string, not float!)
# date      object     (string, not datetime!)
# active    int64
```

### Converting types

```python
# astype -- explicit casting
df['active'] = df['active'].astype(bool)     # int -> bool

# pd.to_numeric -- for numeric conversion with error handling
df['value'] = pd.to_numeric(df['value'])             # string -> float
# With error handling:
df['value'] = pd.to_numeric(df['value'], errors='coerce')  # Invalid -> NaN

# pd.to_datetime -- for date parsing
df['date'] = pd.to_datetime(df['date'])
print(df['date'].dtype)   # datetime64[ns]

# Now you can use datetime operations:
print(df['date'].dt.year)    # [2024, 2024, 2024]
print(df['date'].dt.month)   # [1, 2, 3]
print(df['date'].dt.day_name())  # ['Monday', 'Thursday', 'Wednesday']

# String type (modern Pandas uses StringDtype)
df['id'] = df['id'].astype('string')  # More memory-efficient than object
```

### Type optimization for large datasets

```python
# Downcast numeric types to save memory
df['value'] = pd.to_numeric(df['value'], downcast='float')  # float64 -> float32
df['count'] = pd.to_numeric(df['count'], downcast='integer')  # int64 -> int8/16/32

# Category type for low-cardinality strings
df['dept'] = df['dept'].astype('category')
# Saves memory: stores integers internally + lookup table
# Before: 5 strings * ~50 bytes = ~250 bytes
# After: 5 int8s + 2 unique strings = ~108 bytes
```

---

## Display Options

```python
# Common display settings
pd.set_option('display.max_rows', 100)        # Show more rows
pd.set_option('display.max_columns', 20)      # Show more columns
pd.set_option('display.width', 120)           # Wider output
pd.set_option('display.max_colwidth', 50)     # Wider column content
pd.set_option('display.float_format', '{:.2f}'.format)  # 2 decimal places

# Reset all options
pd.reset_option('all')

# Temporary option context
with pd.option_context('display.max_rows', 10):
    print(df)

# Quick look at data
print(df.head())        # First 5 rows
print(df.tail(3))       # Last 3 rows
print(df.sample(5))     # Random 5 rows
print(df.info())        # Column info, dtypes, memory usage
print(df.shape)         # (rows, cols)
```

---

## Saving Data

```python
# CSV
df.to_csv('output.csv', index=False)           # Don't save index as column
df.to_csv('output.csv', columns=['name', 'age'])  # Specific columns
df.to_csv('output.csv', sep='\t')               # Tab-separated

# Parquet (recommended for large data)
df.to_parquet('output.parquet')
df.to_parquet('output.parquet', compression='snappy')  # Compressed

# JSON
df.to_json('output.json', orient='records')     # List of dicts
df.to_json('output.json', orient='columns')     # Dict of lists

# Excel
df.to_excel('output.xlsx', sheet_name='Data', index=False)

# Pickle (Python-specific binary format)
df.to_pickle('output.pkl')
df = pd.read_pickle('output.pkl')

# To clipboard (for pasting into spreadsheets)
# df.to_clipboard()
```

---

## Putting It All Together: Exploratory Data Analysis (EDA) Template

```python
import pandas as pd
import numpy as np

def quick_eda(df: pd.DataFrame) -> None:
    """Quick exploratory data analysis on any DataFrame."""

    print("=" * 60)
    print("SHAPE")
    print(f"  Rows: {df.shape[0]:,}")
    print(f"  Columns: {df.shape[1]}")

    print("\n" + "=" * 60)
    print("DTYPES")
    for dtype, count in df.dtypes.value_counts().items():
        print(f"  {dtype}: {count} columns")

    print("\n" + "=" * 60)
    print("MISSING VALUES")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        for col, count in missing[missing > 0].items():
            pct = count / len(df) * 100
            print(f"  {col}: {count} ({pct:.1f}%)")
    else:
        print("  None!")

    print("\n" + "=" * 60)
    print("NUMERIC SUMMARY")
    print(df.describe().round(2))

    print("\n" + "=" * 60)
    print("CATEGORICAL SUMMARY")
    for col in df.select_dtypes(include=['object', 'category']).columns:
        n_unique = df[col].nunique()
        print(f"\n  {col}: {n_unique} unique values")
        if n_unique <= 10:
            print(df[col].value_counts().to_string(header=False))

    print("\n" + "=" * 60)
    print("SAMPLE (first 3 rows)")
    print(df.head(3))


# Usage
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'dept': ['Eng', 'Mkt', 'Eng', 'Mkt', 'Eng'],
    'age': [30, 25, 35, 28, 32],
    'salary': [90000, 65000, 95000, 72000, 88000],
})
quick_eda(df)
```

---

## Common Pitfalls for Swift Developers

1. **SettingWithCopyWarning**: Chained indexing like `df[df['age'] > 30]['salary'] = 0`
   may not modify `df`. Use `df.loc[df['age'] > 30, 'salary'] = 0` instead.

2. **`inplace` parameter**: Many Pandas methods return new DataFrames. If you want
   to modify in place, pass `inplace=True`, but the modern style is to reassign:
   `df = df.sort_values('age')` rather than `df.sort_values('age', inplace=True)`.

3. **Object dtype for strings**: Pandas stores strings as Python objects by default,
   which is slower and uses more memory. Use `.astype('string')` for better performance.

4. **Index confusion**: `loc` uses labels (inclusive slicing), `iloc` uses positions
   (exclusive slicing). This is the #1 source of bugs for Pandas beginners.

5. **NaN propagation**: Most operations skip NaN by default, but arithmetic propagates
   it: `1 + NaN = NaN`. Use `.fillna()` before operations if needed.

---

## Quick Reference

| Operation               | Pandas                                | Swift Equivalent               |
|-------------------------|---------------------------------------|--------------------------------|
| Create table            | `pd.DataFrame(dict)`                 | `[[String: Any]]`             |
| Read CSV                | `pd.read_csv(path)`                  | Custom CSV parser              |
| Access column           | `df['col']`                          | `array.map { $0.col }`        |
| Filter rows             | `df[df['age'] > 30]`                | `array.filter { $0.age > 30 }`|
| Sort                    | `df.sort_values('col')`             | `array.sorted(by: \.col)`     |
| Group + aggregate       | `df.groupby('col').mean()`          | `Dictionary(grouping:)`       |
| Column stats            | `df['col'].describe()`              | Manual computation             |
| Add column              | `df['new'] = values`                | No direct equivalent           |
| Select by label         | `df.loc[label]`                     | `dict[key]`                   |
| Select by position      | `df.iloc[pos]`                      | `array[index]`                |

---

## Next Steps

Module 04 covers **Pandas Advanced** -- GroupBy, merging/joining tables,
reshaping, handling missing data, method chaining, window functions, and
performance optimization.
