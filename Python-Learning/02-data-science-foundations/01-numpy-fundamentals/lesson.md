# Module 01: NumPy Fundamentals

## What is NumPy and Why It Matters

If you're coming from Swift/iOS development, think of NumPy as the `Accelerate` framework
on steroids -- but for Python. Where Swift has `Array<Float>` and `vDSP` for vectorized math,
Python's native lists are slow for numerical work. NumPy fills this gap with `ndarray`, a
fixed-type, contiguous-memory array that enables C-speed operations from Python.

**Why NumPy is foundational:**
- Every major data science library (Pandas, scikit-learn, TensorFlow, PyTorch) is built on NumPy
- Vectorized operations run 10-100x faster than Python loops
- Memory-efficient: a NumPy array of 1 million float64 values uses ~8 MB; a Python list of floats uses ~28 MB
- The mental model (arrays, broadcasting, slicing) carries directly into PyTorch and TensorFlow

```python
import numpy as np

# Python list vs NumPy array -- the speed difference is dramatic
python_list = list(range(1_000_000))
numpy_array = np.arange(1_000_000)

# Squaring every element:
# Python list: [x**2 for x in python_list]    ~200ms
# NumPy array: numpy_array ** 2               ~2ms
```

**Swift analogy:**
| Swift                     | NumPy                          |
|---------------------------|--------------------------------|
| `[Double]`                | `np.ndarray` with `float64`    |
| `vDSP.add(_:_:)`         | `array1 + array2`              |
| `Accelerate` framework   | NumPy vectorized operations    |
| `simd_float4`             | `np.array([1,2,3,4])`         |

---

## Installing NumPy

```bash
pip install numpy
# or
pip install numpy pandas matplotlib  # common combo
```

```python
import numpy as np  # ALWAYS use this convention
print(np.__version__)
```

---

## ndarray Creation

### From Python sequences

```python
import numpy as np

# From a list
a = np.array([1, 2, 3, 4, 5])
print(a)          # [1 2 3 4 5]
print(type(a))    # <class 'numpy.ndarray'>

# From a list of lists (2D array / matrix)
matrix = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])
print(matrix)
# [[1 2 3]
#  [4 5 6]
#  [7 8 9]]

# Specifying dtype explicitly
floats = np.array([1, 2, 3], dtype=np.float64)
print(floats)     # [1. 2. 3.]
```

### Factory functions

```python
# Zeros -- like Array(repeating: 0.0, count: 5) in Swift
zeros_1d = np.zeros(5)                 # [0. 0. 0. 0. 0.]
zeros_2d = np.zeros((3, 4))            # 3 rows, 4 columns
zeros_int = np.zeros(5, dtype=np.int32)  # [0 0 0 0 0]

# Ones
ones = np.ones((2, 3))
# [[1. 1. 1.]
#  [1. 1. 1.]]

# Full -- fill with arbitrary value
fives = np.full((3, 3), 5.0)
# [[5. 5. 5.]
#  [5. 5. 5.]
#  [5. 5. 5.]]

# Identity matrix (square matrix with 1s on diagonal)
identity = np.eye(4)
# [[1. 0. 0. 0.]
#  [0. 1. 0. 0.]
#  [0. 0. 1. 0.]
#  [0. 0. 0. 1.]]

# Diagonal matrix from values
diag = np.diag([1, 2, 3, 4])
# [[1 0 0 0]
#  [0 2 0 0]
#  [0 0 3 0]
#  [0 0 0 4]]
```

### Ranges and sequences

```python
# arange -- like Swift's stride(from:to:by:)
a = np.arange(10)           # [0 1 2 3 4 5 6 7 8 9]
b = np.arange(2, 10)        # [2 3 4 5 6 7 8 9]
c = np.arange(0, 1, 0.1)    # [0.  0.1 0.2 ... 0.9]

# linspace -- evenly spaced numbers over an interval (INCLUDES endpoint)
d = np.linspace(0, 1, 5)    # [0.   0.25 0.5  0.75 1.  ]
e = np.linspace(0, 2*np.pi, 100)  # 100 points for a sine wave

# Key difference:
# arange(start, stop, step)  -- uses step size, excludes stop
# linspace(start, stop, num) -- uses number of points, includes stop
```

### Creating arrays like existing arrays

```python
original = np.array([[1, 2], [3, 4]])

# Same shape, filled with zeros
z = np.zeros_like(original)    # [[0 0] [0 0]]

# Same shape, filled with ones
o = np.ones_like(original)     # [[1 1] [1 1]]

# Same shape, uninitialized (faster but contains garbage)
e = np.empty_like(original)    # [[ ? ?] [ ? ?]]
```

---

## Data Types (dtypes)

NumPy arrays are homogeneous -- every element has the same type. This is similar to
Swift's `Array<Int>` or `Array<Double>`.

```python
# Common dtypes
np.int32      # 32-bit integer
np.int64      # 64-bit integer (default for integers on 64-bit systems)
np.float32    # 32-bit float (single precision) -- common in ML
np.float64    # 64-bit float (double precision) -- default for floats
np.bool_      # Boolean
np.complex128 # Complex number
np.str_       # String (fixed-length)

# Check dtype
a = np.array([1, 2, 3])
print(a.dtype)    # int64

b = np.array([1.0, 2.0, 3.0])
print(b.dtype)    # float64

# Explicit dtype
c = np.array([1, 2, 3], dtype=np.float32)
print(c.dtype)    # float32

# Type casting
d = a.astype(np.float64)  # Convert int to float
print(d)          # [1. 2. 3.]

# ML tip: float32 is standard in deep learning (saves memory, GPU-friendly)
model_weights = np.random.randn(1000, 1000).astype(np.float32)
```

**Swift comparison:**
| Swift Type   | NumPy dtype      |
|-------------|------------------|
| `Int`       | `np.int64`       |
| `Int32`     | `np.int32`       |
| `Float`     | `np.float32`     |
| `Double`    | `np.float64`     |
| `Bool`      | `np.bool_`       |

---

## Array Attributes

```python
matrix = np.array([
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12]
])

# Shape -- tuple of dimension sizes (like a 3x4 matrix)
print(matrix.shape)    # (3, 4) -- 3 rows, 4 columns

# Number of dimensions
print(matrix.ndim)     # 2

# Total number of elements
print(matrix.size)     # 12

# Data type
print(matrix.dtype)    # int64

# Bytes per element
print(matrix.itemsize) # 8 (bytes)

# Total bytes
print(matrix.nbytes)   # 96 (12 elements * 8 bytes)

# 3D example
cube = np.zeros((2, 3, 4))  # 2 "layers", 3 rows, 4 columns
print(cube.shape)      # (2, 3, 4)
print(cube.ndim)       # 3
print(cube.size)       # 24
```

---

## Indexing

### Basic indexing (like Swift subscripts)

```python
a = np.array([10, 20, 30, 40, 50])

# Single element
print(a[0])     # 10
print(a[-1])    # 50  (last element, just like Python lists)

# 2D array indexing
matrix = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])

print(matrix[0, 0])    # 1  (row 0, col 0)
print(matrix[1, 2])    # 6  (row 1, col 2)
print(matrix[-1, -1])  # 9  (last row, last col)

# This is different from Python lists where you'd do matrix[0][0]
# NumPy's matrix[0, 0] is more efficient (single lookup vs two)
```

### Boolean indexing (filtering)

This is extremely powerful and has no direct Swift equivalent without custom extensions.

```python
a = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Create a boolean mask
mask = a > 5
print(mask)     # [False False False False False  True  True  True  True  True]

# Use the mask to filter
filtered = a[mask]
print(filtered)  # [ 6  7  8  9 10]

# One-liner (most common usage)
result = a[a > 5]
print(result)    # [ 6  7  8  9 10]

# Compound conditions -- use & (and), | (or), ~ (not)
# IMPORTANT: use parentheses around each condition!
result = a[(a > 3) & (a < 8)]
print(result)    # [4 5 6 7]

result = a[(a < 3) | (a > 8)]
print(result)    # [ 1  2  9 10]

result = a[~(a > 5)]
print(result)    # [1 2 3 4 5]

# Boolean indexing with 2D arrays
matrix = np.array([[1, 2], [3, 4], [5, 6]])
print(matrix[matrix > 3])  # [4 5 6]  -- flattened result!
```

### Fancy indexing (indexing with arrays)

```python
a = np.array([10, 20, 30, 40, 50])

# Index with a list of indices
indices = [0, 2, 4]
print(a[indices])    # [10 30 50]

# Index with a NumPy array
idx = np.array([1, 3])
print(a[idx])        # [20 40]

# 2D fancy indexing
matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Select specific rows
print(matrix[[0, 2]])     # [[1 2 3]
                           #  [7 8 9]]

# Select specific elements: (row0,col0), (row1,col1), (row2,col2)
rows = [0, 1, 2]
cols = [0, 1, 2]
print(matrix[rows, cols])  # [1 5 9]  -- diagonal elements
```

---

## Slicing

### 1D slicing

```python
a = np.arange(10)  # [0 1 2 3 4 5 6 7 8 9]

# Syntax: array[start:stop:step]
print(a[2:7])      # [2 3 4 5 6]
print(a[:5])       # [0 1 2 3 4]
print(a[5:])       # [5 6 7 8 9]
print(a[::2])      # [0 2 4 6 8]  -- every other element
print(a[::-1])     # [9 8 7 6 5 4 3 2 1 0]  -- reversed

# CRITICAL DIFFERENCE FROM SWIFT:
# NumPy slices return VIEWS, not copies!
b = a[2:5]
b[0] = 99
print(a)  # [ 0  1 99  3  4  5  6  7  8  9]  -- original is modified!
```

### 2D slicing

```python
matrix = np.array([
    [1,  2,  3,  4],
    [5,  6,  7,  8],
    [9,  10, 11, 12],
    [13, 14, 15, 16]
])

# Row slicing
print(matrix[0:2])       # First 2 rows
# [[ 1  2  3  4]
#  [ 5  6  7  8]]

# Column slicing
print(matrix[:, 1])      # All rows, column 1: [ 2  6 10 14]
print(matrix[:, 1:3])    # All rows, columns 1-2
# [[ 2  3]
#  [ 6  7]
#  [10 11]
#  [14 15]]

# Submatrix
print(matrix[1:3, 1:3])  # Rows 1-2, Columns 1-2
# [[ 6  7]
#  [10 11]]

# Every other row, every other column
print(matrix[::2, ::2])
# [[ 1  3]
#  [ 9 11]]
```

### 3D slicing

```python
# Think of 3D arrays as a stack of 2D matrices
cube = np.arange(24).reshape(2, 3, 4)
# cube[layer, row, column]

print(cube[0])           # First "layer" (3x4 matrix)
print(cube[:, 0, :])     # First row of every layer
print(cube[:, :, 0])     # First column of every layer
print(cube[0, 1, 2])     # Specific element: layer 0, row 1, col 2
```

---

## Reshaping

```python
a = np.arange(12)  # [ 0  1  2  3  4  5  6  7  8  9 10 11]

# reshape -- returns a view (usually)
matrix = a.reshape(3, 4)
print(matrix)
# [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]

# Use -1 to let NumPy figure out one dimension
auto = a.reshape(3, -1)   # Same as reshape(3, 4)
auto = a.reshape(-1, 6)   # Becomes (2, 6)

# Flatten (always returns a copy)
flat = matrix.flatten()
print(flat)  # [ 0  1  2  3  4  5  6  7  8  9 10 11]

# Ravel (returns a view when possible -- more memory efficient)
rav = matrix.ravel()  # Same result, but may be a view

# Transpose
print(matrix.T)        # Shorthand for transpose
# [[ 0  4  8]
#  [ 1  5  9]
#  [ 2  6 10]
#  [ 3  7 11]]

print(matrix.transpose())  # Equivalent

# Adding dimensions (useful for broadcasting)
row_vector = np.array([1, 2, 3])          # shape: (3,)
col_vector = row_vector.reshape(-1, 1)     # shape: (3, 1)
col_vector2 = row_vector[:, np.newaxis]    # Equivalent, more idiomatic

# Squeezing (removing dimensions of size 1)
x = np.array([[[1, 2, 3]]])  # shape: (1, 1, 3)
print(np.squeeze(x).shape)    # shape: (3,)
```

---

## Copies vs Views

This is a critical concept that trips up many newcomers. In Swift, arrays have
value semantics (copy-on-write). In NumPy, many operations return **views**
that share memory with the original array.

```python
# VIEWS (share memory -- changes propagate)
a = np.array([1, 2, 3, 4, 5])

# Slicing creates a view
b = a[1:4]
b[0] = 99
print(a)  # [ 1 99  3  4  5]  -- a is modified!

# reshape usually creates a view
c = a.reshape(5, 1)
c[0, 0] = 42
print(a)  # [42 99  3  4  5]  -- a is modified!

# COPIES (independent memory)
a = np.array([1, 2, 3, 4, 5])

# Explicit copy
b = a.copy()
b[0] = 99
print(a)  # [1 2 3 4 5]  -- a is unchanged

# flatten() always returns a copy
c = a.reshape(5, 1).flatten()
c[0] = 99
print(a)  # [1 2 3 4 5]  -- a is unchanged

# Fancy indexing returns a copy
d = a[[0, 1, 2]]
d[0] = 99
print(a)  # [1 2 3 4 5]  -- a is unchanged

# Check if arrays share memory
print(np.shares_memory(a, a[1:4]))  # True (view)
print(np.shares_memory(a, a.copy()))  # False (copy)
```

**Rule of thumb:**
- Basic slicing = **view**
- Fancy indexing (with list/array of indices) = **copy**
- Boolean indexing = **copy**
- `.copy()` = explicit **copy**
- `.flatten()` = **copy**, `.ravel()` = **view** (when possible)

---

## Universal Functions (ufuncs)

Ufuncs are vectorized wrappers around C functions. They operate element-wise
on arrays, eliminating the need for Python loops.

```python
a = np.array([1, 4, 9, 16, 25])

# Math ufuncs
print(np.sqrt(a))       # [1. 2. 3. 4. 5.]
print(np.square(a))     # [  1  16  81 256 625]
print(np.exp(a))        # exponential
print(np.log(a))        # natural log
print(np.log10(a))      # log base 10
print(np.abs(np.array([-1, -2, 3])))  # [1 2 3]

# Trigonometric
angles = np.array([0, np.pi/4, np.pi/2, np.pi])
print(np.sin(angles))   # [0.000 0.707 1.000 0.000]
print(np.cos(angles))   # [1.000 0.707 0.000 -1.000]

# Rounding
b = np.array([1.23, 2.78, 3.14, 4.99])
print(np.floor(b))      # [1. 2. 3. 4.]
print(np.ceil(b))       # [2. 3. 4. 5.]
print(np.round(b, 1))   # [1.2 2.8 3.1 5.0]

# Clip values to a range
c = np.array([1, 5, 10, 15, 20])
print(np.clip(c, 3, 12))  # [ 3  5 10 12 12]
```

---

## Element-wise Operations

```python
a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

# Arithmetic (element-wise, NOT matrix multiplication)
print(a + b)    # [11 22 33 44]
print(a - b)    # [ -9 -18 -27 -36]
print(a * b)    # [ 10  40  90 160]   -- Hadamard product
print(a / b)    # [0.1 0.1 0.1 0.1]
print(a ** 2)   # [ 1  4  9 16]
print(a % 2)    # [1 0 1 0]
print(a // 3)   # [0 0 1 1]   -- floor division

# Scalar operations broadcast automatically
print(a + 10)   # [11 12 13 14]
print(a * 3)    # [ 3  6  9 12]

# In-place operations (modify array directly, no new allocation)
a += 10
print(a)        # [11 12 13 14]

# Swift comparison:
# Swift:  zip(a, b).map(+)  or  vDSP.add(a, b)
# NumPy:  a + b  -- much cleaner!
```

---

## Comparison Operators

```python
a = np.array([1, 2, 3, 4, 5])

# Element-wise comparisons return boolean arrays
print(a > 3)      # [False False False  True  True]
print(a == 3)     # [False False  True False False]
print(a != 3)     # [ True  True False  True  True]
print(a >= 3)     # [False False  True  True  True]

# Array vs array comparison
b = np.array([5, 4, 3, 2, 1])
print(a > b)      # [False False False  True  True]
print(a == b)     # [False False  True False False]

# np.allclose -- for floating point comparison (handles precision)
x = np.array([0.1 + 0.2])
y = np.array([0.3])
print(x == y)                    # [False]  -- floating point issue!
print(np.allclose(x, y))         # True     -- correct comparison

# Any / All
print(np.any(a > 3))    # True  -- at least one element > 3
print(np.all(a > 0))    # True  -- all elements > 0
print(np.all(a > 3))    # False
```

---

## Aggregation Functions

```python
a = np.array([1, 2, 3, 4, 5])

# Basic aggregations
print(np.sum(a))       # 15     (or a.sum())
print(np.mean(a))      # 3.0    (or a.mean())
print(np.median(a))    # 3.0
print(np.min(a))       # 1      (or a.min())
print(np.max(a))       # 5      (or a.max())
print(np.std(a))       # 1.414... (standard deviation)
print(np.var(a))       # 2.0    (variance)
print(np.prod(a))      # 120    (product of all elements)

# Index of min/max
print(np.argmin(a))    # 0  (index of minimum)
print(np.argmax(a))    # 4  (index of maximum)

# Cumulative operations
print(np.cumsum(a))    # [ 1  3  6 10 15]
print(np.cumprod(a))   # [  1   2   6  24 120]
```

### Aggregation along axes

This is where things get interesting with multi-dimensional arrays.

```python
matrix = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])

# No axis: aggregate everything
print(np.sum(matrix))           # 45

# axis=0: collapse rows (aggregate DOWN each column)
print(np.sum(matrix, axis=0))   # [12 15 18]
# Explanation: 1+4+7=12, 2+5+8=15, 3+6+9=18

# axis=1: collapse columns (aggregate ACROSS each row)
print(np.sum(matrix, axis=1))   # [ 6 15 24]
# Explanation: 1+2+3=6, 4+5+6=15, 7+8+9=24

# Mean along axes
print(np.mean(matrix, axis=0))  # [4. 5. 6.]  -- column means
print(np.mean(matrix, axis=1))  # [2. 5. 8.]  -- row means

# Keep dimensions (useful for broadcasting)
col_sums = np.sum(matrix, axis=0, keepdims=True)
print(col_sums.shape)  # (1, 3) instead of (3,)
```

**How to remember axis:**
- `axis=0` collapses the first dimension (rows disappear, columns remain)
- `axis=1` collapses the second dimension (columns disappear, rows remain)
- Think: "aggregate along axis N" means "that dimension goes away"

```
axis=0: aggregate vertically (down)
    [1, 2, 3]
    [4, 5, 6]   -->  [12, 15, 18]
    [7, 8, 9]

axis=1: aggregate horizontally (across)
    [1, 2, 3]  -->  [ 6]
    [4, 5, 6]  -->  [15]
    [7, 8, 9]  -->  [24]
```

---

## Putting It All Together: A Practical Example

Here is a complete example that uses many concepts from this lesson -- normalizing
features in a dataset, a common ML preprocessing step.

```python
import numpy as np

# Simulate a dataset: 1000 samples, 4 features
rng = np.random.default_rng(42)
data = rng.normal(loc=[100, 50, 0.5, 1000], scale=[20, 10, 0.1, 200], size=(1000, 4))

print(f"Shape: {data.shape}")           # (1000, 4)
print(f"Means: {data.mean(axis=0)}")    # ~[100, 50, 0.5, 1000]
print(f"Stds:  {data.std(axis=0)}")     # ~[20, 10, 0.1, 200]

# Z-score normalization: (x - mean) / std
# This makes each feature have mean=0 and std=1
means = data.mean(axis=0, keepdims=True)  # shape: (1, 4)
stds = data.std(axis=0, keepdims=True)    # shape: (1, 4)
normalized = (data - means) / stds        # Broadcasting handles the shapes

print(f"\nAfter normalization:")
print(f"Means: {normalized.mean(axis=0).round(4)}")  # ~[0, 0, 0, 0]
print(f"Stds:  {normalized.std(axis=0).round(4)}")    # ~[1, 1, 1, 1]

# Find outliers (values > 3 standard deviations)
outlier_mask = np.abs(normalized) > 3
outlier_counts = outlier_mask.sum(axis=0)
print(f"\nOutliers per feature: {outlier_counts}")

# Clip outliers
clipped = np.clip(normalized, -3, 3)
print(f"Max after clipping: {clipped.max()}")   # 3.0
print(f"Min after clipping: {clipped.min()}")   # -3.0
```

---

## Common Pitfalls for Swift Developers

1. **Mutability**: NumPy slices are views. Modifying a slice modifies the original.
   In Swift, `let slice = array[1...3]` creates an independent value.

2. **Integer division**: `np.array([1, 2, 3]) / 2` gives `[0.5, 1.0, 1.5]` (float result).
   Use `//` for integer division.

3. **Boolean operators**: Use `&`, `|`, `~` for element-wise boolean ops on arrays,
   NOT `and`, `or`, `not`. And always use parentheses: `(a > 3) & (a < 8)`.

4. **Shape mismatches**: Operations between arrays of incompatible shapes will raise
   errors. Understanding broadcasting (covered in Module 02) is essential.

5. **0-indexed axes**: `axis=0` is rows, `axis=1` is columns. This is the opposite
   of what some people expect.

---

## Quick Reference

| Operation             | NumPy                           | Swift Equivalent              |
|-----------------------|---------------------------------|-------------------------------|
| Create array          | `np.array([1,2,3])`            | `[1, 2, 3]`                  |
| Zeros                 | `np.zeros(5)`                  | `Array(repeating: 0, count: 5)` |
| Range                 | `np.arange(0, 10, 2)`         | `stride(from: 0, to: 10, by: 2)` |
| Shape                 | `a.shape`                      | `(a.count,)` (1D only)       |
| Element access        | `a[i, j]`                      | `a[i][j]`                    |
| Slice                 | `a[1:4]`                       | `a[1..<4]`                   |
| Filter                | `a[a > 5]`                     | `a.filter { $0 > 5 }`        |
| Sum                   | `np.sum(a)` or `a.sum()`      | `a.reduce(0, +)`             |
| Element-wise add      | `a + b`                        | `zip(a, b).map(+)`           |
| Reshape               | `a.reshape(3, 4)`             | No direct equivalent          |
| Transpose             | `a.T`                          | No direct equivalent          |

---

## Next Steps

In Module 02, we will cover:
- **Broadcasting**: How NumPy automatically handles operations between arrays of different shapes
- **Vectorization**: Replacing Python loops with array operations for massive speedups
- **Linear algebra**: Matrix operations essential for ML
- **Random number generation**: For simulations and data generation
