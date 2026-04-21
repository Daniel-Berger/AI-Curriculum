# Module 02: NumPy Advanced

## Broadcasting Rules

Broadcasting is NumPy's mechanism for performing operations on arrays of different shapes.
Coming from Swift, where you would need explicit loops or `zip` to combine arrays of
different sizes, broadcasting feels almost magical.

### The Basic Idea

```python
import numpy as np

# Scalar broadcast: add 10 to every element
a = np.array([1, 2, 3])
result = a + 10          # [11, 12, 13]

# NumPy "broadcasts" the scalar 10 to match shape (3,)
# Conceptually: [1, 2, 3] + [10, 10, 10] = [11, 12, 13]
```

### Broadcasting Rules (Step by Step)

When operating on two arrays, NumPy compares shapes element-wise, starting from
the **trailing** (rightmost) dimensions:

1. **If dimensions are equal**: compatible
2. **If one dimension is 1**: it gets "stretched" to match the other
3. **If dimensions differ and neither is 1**: incompatible (error)

Arrays with fewer dimensions are padded with 1s on the **left** side.

### Visual Examples

```
Example 1: Vector + Scalar
Array A:  (3,)    -->  (3,)
Scalar:   ()      -->  (3,)   [broadcast scalar to match]
Result:   (3,)

Example 2: Matrix + Row Vector
Array A:  (3, 4)  -->  (3, 4)
Array B:  (4,)    -->  (1, 4)  [pad left with 1]
                  -->  (3, 4)  [stretch dim 0 from 1 to 3]
Result:   (3, 4)

Example 3: Column Vector + Row Vector (Outer Product Pattern)
Array A:  (3, 1)  -->  (3, 1)  -->  (3, 4)  [stretch dim 1 from 1 to 4]
Array B:  (1, 4)  -->  (1, 4)  -->  (3, 4)  [stretch dim 0 from 1 to 3]
Result:   (3, 4)

Example 4: INCOMPATIBLE
Array A:  (3, 4)
Array B:  (3,)    -->  (1, 3)  -->  (?, 3)  [can't stretch 3 to match 4]
ERROR: shapes (3,4) and (3,) not aligned
```

### Practical Broadcasting Examples

```python
import numpy as np

# 1. Add a row vector to every row of a matrix
matrix = np.array([[1, 2, 3],
                   [4, 5, 6],
                   [7, 8, 9]])
row = np.array([10, 20, 30])

result = matrix + row
# [[11 22 33]
#  [14 25 36]
#  [17 28 39]]

# 2. Add a column vector to every column of a matrix
col = np.array([[100], [200], [300]])  # shape (3, 1)
result = matrix + col
# [[101 102 103]
#  [204 205 206]
#  [307 308 309]]

# 3. Outer product via broadcasting
x = np.array([1, 2, 3])[:, np.newaxis]   # shape (3, 1)
y = np.array([10, 20, 30])[np.newaxis, :] # shape (1, 3)
outer = x * y
# [[ 10  20  30]
#  [ 20  40  60]
#  [ 30  60  90]]

# 4. Distance matrix (pairwise distances between points)
points = np.array([[0, 0], [1, 1], [2, 0]])  # 3 points in 2D
# Expand dims to enable broadcasting
diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]  # (3,3,2)
distances = np.sqrt(np.sum(diff**2, axis=2))                # (3,3)
# [[0.    1.414 2.   ]
#  [1.414 0.    1.414]
#  [2.    1.414 0.   ]]

# 5. Normalizing features (very common in ML)
data = np.array([[100, 0.5],
                 [200, 0.8],
                 [150, 0.6]])
means = data.mean(axis=0)    # [150.  0.633]  -- shape (2,)
stds = data.std(axis=0)      # shape (2,)
normalized = (data - means) / stds  # Broadcasting handles (3,2) - (2,)
```

### Common Broadcasting Patterns

```python
# Pattern: Convert 1D to column vector for broadcasting
v = np.array([1, 2, 3])

# Method 1: reshape
col = v.reshape(-1, 1)       # (3, 1)

# Method 2: np.newaxis (more idiomatic)
col = v[:, np.newaxis]       # (3, 1)

# Method 3: None is an alias for np.newaxis
col = v[:, None]             # (3, 1)
```

---

## Vectorization: Replacing Loops

Vectorization means expressing operations on entire arrays instead of looping
through elements. This is THE most important performance technique in NumPy.

### Why Loops Are Slow in Python

```python
import numpy as np

# BAD: Python loop (slow)
def slow_square(arr):
    result = np.empty_like(arr)
    for i in range(len(arr)):
        result[i] = arr[i] ** 2
    return result

# GOOD: Vectorized (fast)
def fast_square(arr):
    return arr ** 2

# The vectorized version is typically 50-100x faster
```

### Common Vectorization Patterns

```python
import numpy as np

# Pattern 1: Replace if/else loops with np.where
# BAD
def slow_relu(arr):
    result = np.empty_like(arr)
    for i in range(len(arr)):
        result[i] = arr[i] if arr[i] > 0 else 0
    return result

# GOOD
def fast_relu(arr):
    return np.where(arr > 0, arr, 0)
    # Or even simpler: return np.maximum(arr, 0)

# Pattern 2: Replace accumulation loops with aggregation
# BAD
def slow_running_max(arr):
    result = np.empty_like(arr)
    current_max = arr[0]
    for i in range(len(arr)):
        current_max = max(current_max, arr[i])
        result[i] = current_max
    return result

# GOOD
def fast_running_max(arr):
    return np.maximum.accumulate(arr)

# Pattern 3: Replace nested loops with broadcasting
# BAD: Pairwise distances
def slow_distances(points):
    n = len(points)
    result = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            result[i, j] = np.sqrt(np.sum((points[i] - points[j])**2))
    return result

# GOOD: Vectorized with broadcasting
def fast_distances(points):
    diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
    return np.sqrt(np.sum(diff**2, axis=-1))

# Pattern 4: Replace conditional assignment with boolean masking
# BAD
def slow_clamp(arr, low, high):
    result = arr.copy()
    for i in range(len(result)):
        if result[i] < low:
            result[i] = low
        elif result[i] > high:
            result[i] = high
    return result

# GOOD
def fast_clamp(arr, low, high):
    return np.clip(arr, low, high)
```

---

## Performance Comparison

```python
import numpy as np
import time

def benchmark(func, *args, n_runs=100):
    """Simple benchmarking utility."""
    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        func(*args)
        times.append(time.perf_counter() - start)
    return np.mean(times)

# Example: element-wise squaring
arr = np.random.randn(100_000)

# Loop version
def loop_square(arr):
    result = np.empty_like(arr)
    for i in range(len(arr)):
        result[i] = arr[i] ** 2
    return result

# Vectorized version
def vec_square(arr):
    return arr ** 2

loop_time = benchmark(loop_square, arr, n_runs=10)
vec_time = benchmark(vec_square, arr, n_runs=10)

print(f"Loop: {loop_time*1000:.2f} ms")
print(f"Vectorized: {vec_time*1000:.4f} ms")
print(f"Speedup: {loop_time/vec_time:.0f}x")
# Typical output: Loop: 35ms, Vectorized: 0.08ms, Speedup: ~400x

# More realistic example: computing softmax
def loop_softmax(arr):
    result = np.empty_like(arr)
    total = 0
    max_val = max(arr)  # for numerical stability
    for i in range(len(arr)):
        result[i] = np.exp(arr[i] - max_val)
        total += result[i]
    return result / total

def vec_softmax(arr):
    shifted = arr - arr.max()  # numerical stability
    exp_vals = np.exp(shifted)
    return exp_vals / exp_vals.sum()
```

---

## Linear Algebra

NumPy's `linalg` module provides essential linear algebra operations.
These are critical for understanding ML algorithms.

### Dot Product and Matrix Multiplication

```python
import numpy as np

# Dot product of 1D vectors
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(np.dot(a, b))      # 32 (1*4 + 2*5 + 3*6)
print(a @ b)              # 32 (@ operator -- preferred syntax)

# Matrix multiplication
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print(A @ B)              # Matrix multiply (preferred)
# [[19 22]
#  [43 50]]

print(np.matmul(A, B))    # Equivalent
print(np.dot(A, B))       # Also works for 2D (but @ is clearer)

# IMPORTANT: * is element-wise, @ is matrix multiply
print(A * B)    # [[ 5 12] [21 32]]  -- Hadamard product
print(A @ B)    # [[19 22] [43 50]]  -- Matrix multiplication

# Matrix-vector multiplication
M = np.array([[1, 2], [3, 4], [5, 6]])  # (3, 2)
v = np.array([10, 20])                   # (2,)
print(M @ v)   # [50 110 170]            # (3,) result
```

### Matrix Operations

```python
# Transpose
A = np.array([[1, 2, 3], [4, 5, 6]])
print(A.T)
# [[1 4]
#  [2 5]
#  [3 6]]

# Inverse (square matrices only)
A = np.array([[1, 2], [3, 4]])
A_inv = np.linalg.inv(A)
print(A @ A_inv)  # ~identity matrix (with floating point noise)

# Determinant
det = np.linalg.det(A)
print(det)  # -2.0

# Trace (sum of diagonal)
print(np.trace(A))  # 5 (1 + 4)

# Rank
print(np.linalg.matrix_rank(A))  # 2
```

### Eigenvalues and Eigenvectors

```python
# Eigendecomposition (important for PCA, spectral methods)
A = np.array([[4, -2], [1, 1]])
eigenvalues, eigenvectors = np.linalg.eig(A)
print(f"Eigenvalues: {eigenvalues}")     # [3. 2.]
print(f"Eigenvectors:\n{eigenvectors}")  # columns are eigenvectors

# For symmetric matrices (common in ML), use eigh (faster, more stable)
S = np.array([[2, 1], [1, 3]])
eigenvalues, eigenvectors = np.linalg.eigh(S)
```

### Solving Linear Systems

```python
# Solve Ax = b
A = np.array([[2, 1], [1, 3]])
b = np.array([5, 10])

x = np.linalg.solve(A, b)
print(x)               # [1. 3.]
print(A @ x)           # [5. 10.] -- verify

# Least squares solution (for overdetermined systems)
# Minimize ||Ax - b||^2
A = np.array([[1, 1], [2, 1], [3, 1]])  # More equations than unknowns
b = np.array([2, 3, 5])
result = np.linalg.lstsq(A, b, rcond=None)
x = result[0]
print(f"Best fit: y = {x[0]:.2f}x + {x[1]:.2f}")

# Norms
v = np.array([3, 4])
print(np.linalg.norm(v))        # 5.0 (L2 norm, Euclidean)
print(np.linalg.norm(v, ord=1)) # 7.0 (L1 norm, Manhattan)
print(np.linalg.norm(v, ord=np.inf))  # 4.0 (infinity norm)
```

### Singular Value Decomposition (SVD)

```python
# SVD: A = U @ diag(S) @ V^T
# Used in dimensionality reduction, recommendation systems
A = np.array([[1, 2], [3, 4], [5, 6]])
U, S, Vt = np.linalg.svd(A, full_matrices=False)
print(f"U shape: {U.shape}")    # (3, 2)
print(f"S: {S}")                 # singular values
print(f"Vt shape: {Vt.shape}")  # (2, 2)

# Reconstruct
A_reconstructed = U @ np.diag(S) @ Vt
print(np.allclose(A, A_reconstructed))  # True
```

---

## Random Module

NumPy's random module is essential for ML: generating synthetic data,
initializing weights, splitting datasets, bootstrapping, etc.

### Modern API (Recommended): Generator

```python
import numpy as np

# Create a Generator with a seed for reproducibility
rng = np.random.default_rng(seed=42)

# Uniform distribution [0, 1)
print(rng.random(5))              # 5 random floats
print(rng.random((3, 4)))         # 3x4 matrix of random floats

# Uniform integers
print(rng.integers(0, 10, size=5))        # 5 random ints in [0, 10)
print(rng.integers(1, 7, size=(3, 3)))    # 3x3 dice rolls

# Normal (Gaussian) distribution
print(rng.normal(loc=0, scale=1, size=5))  # mean=0, std=1
print(rng.standard_normal(5))              # equivalent

# Other distributions
print(rng.uniform(low=2, high=8, size=5))   # Uniform [2, 8)
print(rng.exponential(scale=2.0, size=5))   # Exponential
print(rng.poisson(lam=5, size=5))           # Poisson
print(rng.binomial(n=10, p=0.5, size=5))   # Binomial
print(rng.choice([1, 2, 3, 4, 5], size=3)) # Random selection

# Permutations
arr = np.arange(10)
rng.shuffle(arr)                     # In-place shuffle
permuted = rng.permutation(arr)      # Returns shuffled copy
```

### Seeds and Reproducibility

```python
# Same seed = same sequence of random numbers
rng1 = np.random.default_rng(42)
rng2 = np.random.default_rng(42)

print(rng1.random(3))   # [0.773... 0.438... 0.858...]
print(rng2.random(3))   # [0.773... 0.438... 0.858...]  -- identical!

# Different seeds = different sequences
rng3 = np.random.default_rng(123)
print(rng3.random(3))   # Different values

# Best practice: create one rng and pass it around
def generate_data(n_samples, n_features, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    X = rng.normal(0, 1, (n_samples, n_features))
    y = rng.integers(0, 2, n_samples)
    return X, y

rng = np.random.default_rng(42)
X, y = generate_data(100, 5, rng=rng)
```

### Legacy API (You Will See This in Older Code)

```python
# Legacy -- avoid in new code, but know how to read it
np.random.seed(42)                  # Global seed (not recommended)
np.random.rand(3, 4)               # Uniform [0, 1)
np.random.randn(3, 4)              # Standard normal
np.random.randint(0, 10, size=5)   # Random integers
np.random.choice([1, 2, 3])        # Random selection
np.random.shuffle(arr)             # In-place shuffle

# Modern equivalents:
rng = np.random.default_rng(42)    # Use this instead
rng.random((3, 4))                 # Instead of np.random.rand
rng.standard_normal((3, 4))        # Instead of np.random.randn
rng.integers(0, 10, size=5)        # Instead of np.random.randint
```

---

## Structured Arrays

Structured arrays let you define arrays with named fields -- similar to
an array of Swift structs.

```python
import numpy as np

# Define a structured dtype
dt = np.dtype([
    ('name', 'U20'),        # Unicode string, max 20 chars
    ('age', 'i4'),           # 32-bit integer
    ('weight', 'f8'),        # 64-bit float
])

# Create structured array
people = np.array([
    ('Alice', 30, 65.5),
    ('Bob', 25, 80.0),
    ('Charlie', 35, 72.3),
], dtype=dt)

# Access by field name
print(people['name'])      # ['Alice' 'Bob' 'Charlie']
print(people['age'])       # [30 25 35]
print(people[0])           # ('Alice', 30, 65.5)
print(people[0]['name'])   # Alice

# Filter
young = people[people['age'] < 30]
print(young['name'])       # ['Bob']

# Sort by field
sorted_people = np.sort(people, order='age')
print(sorted_people['name'])  # ['Bob' 'Alice' 'Charlie']

# Note: For most tabular data work, Pandas DataFrames are preferable.
# Structured arrays are useful for low-level, memory-mapped data.
```

---

## Memory Layout: C vs Fortran Order

Understanding memory layout helps optimize performance for large arrays.

```python
import numpy as np

matrix = np.array([[1, 2, 3],
                   [4, 5, 6]])

# C order (row-major): default in NumPy
# Memory: [1, 2, 3, 4, 5, 6]  -- rows are contiguous
c_arr = np.array(matrix, order='C')

# Fortran order (column-major): used in MATLAB, some BLAS routines
# Memory: [1, 4, 2, 5, 3, 6]  -- columns are contiguous
f_arr = np.array(matrix, order='F')

# Check order
print(c_arr.flags['C_CONTIGUOUS'])  # True
print(c_arr.flags['F_CONTIGUOUS'])  # False
print(f_arr.flags['C_CONTIGUOUS'])  # False
print(f_arr.flags['F_CONTIGUOUS'])  # True

# Why it matters: iterating over contiguous memory is faster (cache-friendly)
# If you iterate over rows frequently -> C order (default)
# If you iterate over columns frequently -> Fortran order

# Make contiguous copy
c_copy = np.ascontiguousarray(f_arr)   # Convert to C order
f_copy = np.asfortranarray(c_arr)       # Convert to Fortran order

# ravel order
print(matrix.ravel('C'))   # [1 2 3 4 5 6]  -- row by row
print(matrix.ravel('F'))   # [1 4 2 5 3 6]  -- column by column
```

---

## Stacking and Splitting Arrays

### Stacking (combining arrays)

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Vertical stack (add rows)
print(np.vstack([a, b]))
# [[1 2 3]
#  [4 5 6]]

# Horizontal stack (add columns -- for 1D, just concatenates)
print(np.hstack([a, b]))    # [1 2 3 4 5 6]

# For 2D arrays:
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print(np.vstack([A, B]))     # Stack vertically: shape (4, 2)
# [[1 2]
#  [3 4]
#  [5 6]
#  [7 8]]

print(np.hstack([A, B]))     # Stack horizontally: shape (2, 4)
# [[1 2 5 6]
#  [3 4 7 8]]

# Concatenate (general version)
print(np.concatenate([A, B], axis=0))   # Same as vstack
print(np.concatenate([A, B], axis=1))   # Same as hstack

# Depth stack (3D)
print(np.dstack([A, B]).shape)  # (2, 2, 2)

# Stack along new axis
print(np.stack([a, b], axis=0))   # [[1 2 3] [4 5 6]]  shape (2, 3)
print(np.stack([a, b], axis=1))   # [[1 4] [2 5] [3 6]] shape (3, 2)
```

### Splitting (dividing arrays)

```python
arr = np.arange(12).reshape(3, 4)
# [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]

# Split into equal parts along axis
top, bottom = np.vsplit(arr, [2])    # Split after row 2
# top:    [[ 0  1  2  3] [ 4  5  6  7]]
# bottom: [[ 8  9 10 11]]

left, right = np.hsplit(arr, [2])    # Split after column 2
# left:  [[ 0  1] [ 4  5] [ 8  9]]
# right: [[ 2  3] [ 6  7] [10 11]]

# Split into N equal parts
parts = np.split(np.arange(9), 3)   # [array([0,1,2]), array([3,4,5]), array([6,7,8])]

# Split at specific indices
parts = np.split(np.arange(10), [3, 7])
# [array([0,1,2]), array([3,4,5,6]), array([7,8,9])]
```

---

## np.where and np.select

### np.where: Vectorized if/else

```python
import numpy as np

arr = np.array([1, -2, 3, -4, 5])

# np.where(condition, value_if_true, value_if_false)
result = np.where(arr > 0, arr, 0)        # ReLU function
print(result)   # [1 0 3 0 5]

# Can use different arrays for true/false
a = np.array([10, 20, 30])
b = np.array([1, 2, 3])
mask = np.array([True, False, True])
result = np.where(mask, a, b)
print(result)   # [10  2 30]

# Common ML use: binary labels
scores = np.array([0.3, 0.7, 0.5, 0.9, 0.1])
labels = np.where(scores >= 0.5, 1, 0)
print(labels)   # [0 1 1 1 0]

# np.where with only condition (returns indices)
indices = np.where(arr > 0)
print(indices)  # (array([0, 2, 4]),)  -- tuple of index arrays
```

### np.select: Multiple conditions

```python
arr = np.array([15, 25, 35, 45, 55, 65, 75, 85, 95])

conditions = [
    arr < 30,
    (arr >= 30) & (arr < 60),
    (arr >= 60) & (arr < 80),
    arr >= 80,
]
choices = ['F', 'D', 'C', 'B']

# Default is used when no condition matches (shouldn't happen here)
grades = np.select(conditions, choices, default='A')
print(grades)   # ['F' 'F' 'D' 'D' 'D' 'C' 'C' 'B' 'B']
```

---

## Einsum Basics

`np.einsum` (Einstein summation) is a powerful, concise notation for expressing
many array operations. It uses subscript labels to describe the operation.

### Core Idea

```python
import numpy as np

# The subscript notation: 'input_labels -> output_labels'
# Each letter represents an axis. Repeated letters imply summation.

# Example: Matrix multiplication
A = np.array([[1, 2], [3, 4]])  # (2, 2) labeled 'ij'
B = np.array([[5, 6], [7, 8]])  # (2, 2) labeled 'jk'

# 'ij,jk->ik' means: sum over j (shared axis), keep i and k
result = np.einsum('ij,jk->ik', A, B)
print(result)
# [[19 22]
#  [43 50]]
# Same as A @ B
```

### Common Einsum Patterns

```python
A = np.array([[1, 2, 3], [4, 5, 6]])   # (2, 3)
B = np.array([[1, 2], [3, 4], [5, 6]])  # (3, 2)

# Trace (sum of diagonal)
S = np.array([[1, 2], [3, 4]])
print(np.einsum('ii->', S))       # 5 (1 + 4)
# Same as np.trace(S)

# Diagonal elements
print(np.einsum('ii->i', S))      # [1 4]
# Same as np.diag(S)

# Transpose
print(np.einsum('ij->ji', A))     # Same as A.T

# Sum all elements
print(np.einsum('ij->', A))       # 21
# Same as np.sum(A)

# Column sums
print(np.einsum('ij->j', A))      # [5 7 9]
# Same as np.sum(A, axis=0)

# Row sums
print(np.einsum('ij->i', A))      # [6 15]
# Same as np.sum(A, axis=1)

# Matrix multiply
print(np.einsum('ij,jk->ik', A, B))
# Same as A @ B

# Dot product
v1 = np.array([1, 2, 3])
v2 = np.array([4, 5, 6])
print(np.einsum('i,i->', v1, v2))  # 32
# Same as np.dot(v1, v2)

# Outer product
print(np.einsum('i,j->ij', v1, v2))
# Same as np.outer(v1, v2)

# Element-wise multiplication (Hadamard)
print(np.einsum('ij,ij->ij', A[:, :2], B[:2, :]))
# Same as A[:, :2] * B[:2, :]

# Batch matrix multiply (useful in deep learning)
batch_A = np.random.randn(10, 3, 4)  # 10 matrices of 3x4
batch_B = np.random.randn(10, 4, 5)  # 10 matrices of 4x5
batch_result = np.einsum('bij,bjk->bik', batch_A, batch_B)  # (10, 3, 5)
# Same as: np.array([a @ b for a, b in zip(batch_A, batch_B)])
```

### When to Use Einsum

- When you need to express complex tensor operations concisely
- When combining multiple operations (einsum can fuse them)
- When working with deep learning tensors (PyTorch and TensorFlow also support einsum)
- When the explicit notation makes the intent clearer

---

## Putting It All Together: PCA from Scratch

Here is a practical example combining many advanced concepts.

```python
import numpy as np

def pca(X, n_components=2):
    """
    Principal Component Analysis from scratch.

    Args:
        X: Data matrix of shape (n_samples, n_features)
        n_components: Number of principal components to keep

    Returns:
        X_transformed: Projected data (n_samples, n_components)
        components: Principal components (n_components, n_features)
        explained_variance_ratio: Fraction of variance explained
    """
    # 1. Center the data (subtract mean of each feature)
    X_centered = X - X.mean(axis=0)  # Broadcasting: (n, f) - (f,)

    # 2. Compute covariance matrix
    cov_matrix = (X_centered.T @ X_centered) / (X.shape[0] - 1)
    # Or: np.cov(X_centered.T)

    # 3. Eigendecomposition (use eigh for symmetric matrices)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

    # 4. Sort by eigenvalue (descending)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # 5. Select top n_components
    components = eigenvectors[:, :n_components].T  # (n_components, n_features)

    # 6. Project data
    X_transformed = X_centered @ components.T  # (n_samples, n_components)

    # 7. Explained variance ratio
    explained_variance_ratio = eigenvalues[:n_components] / eigenvalues.sum()

    return X_transformed, components, explained_variance_ratio

# Demo
rng = np.random.default_rng(42)
# Create correlated 3D data
X = rng.normal(0, 1, (200, 3))
X[:, 1] = X[:, 0] * 2 + rng.normal(0, 0.1, 200)  # feature 1 ~ 2 * feature 0
X[:, 2] = X[:, 0] * -0.5 + rng.normal(0, 0.5, 200)

X_pca, components, variance_ratio = pca(X, n_components=2)
print(f"Original shape: {X.shape}")            # (200, 3)
print(f"Transformed shape: {X_pca.shape}")     # (200, 2)
print(f"Variance explained: {variance_ratio}") # ~[0.86, 0.12]
print(f"Total variance: {variance_ratio.sum():.2%}")
```

---

## Quick Reference: Advanced Operations

| Operation                 | Code                                          |
|---------------------------|-----------------------------------------------|
| Broadcast add col vec     | `matrix + col[:, np.newaxis]`                 |
| Vectorized conditional    | `np.where(cond, true_val, false_val)`         |
| Matrix multiply           | `A @ B` or `np.matmul(A, B)`                 |
| Inverse                   | `np.linalg.inv(A)`                            |
| Eigenvalues               | `np.linalg.eig(A)` or `eigh(A)`              |
| Solve Ax=b                | `np.linalg.solve(A, b)`                       |
| SVD                       | `np.linalg.svd(A)`                            |
| Random generator          | `rng = np.random.default_rng(42)`             |
| Normal distribution       | `rng.normal(mean, std, size)`                 |
| Vertical stack            | `np.vstack([A, B])`                           |
| Horizontal stack          | `np.hstack([A, B])`                           |
| Split array               | `np.split(arr, indices_or_sections)`          |
| Einsum dot product        | `np.einsum('i,i->', a, b)`                    |
| Einsum matrix multiply    | `np.einsum('ij,jk->ik', A, B)`               |

---

## Next Steps

Module 03 covers **Pandas Basics** -- the standard library for tabular data
manipulation. While NumPy handles raw numerical arrays, Pandas adds labeled
axes, mixed data types, and SQL-like operations that make real-world data
analysis much more convenient.
