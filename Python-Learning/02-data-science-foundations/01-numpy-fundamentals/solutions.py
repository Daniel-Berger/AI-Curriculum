"""
Module 01: NumPy Fundamentals - Solutions
==========================================

Complete solutions for all 15 exercises.
Run this file to verify all solutions pass:
    python solutions.py
"""

import numpy as np


# ---------------------------------------------------------------------------
# Exercise 1: Array Creation Basics
# ---------------------------------------------------------------------------
def create_arrays() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create basic arrays: sequential 1-10, zeros (3,5), identity 3x3."""
    sequential = np.arange(1, 11)          # [1, 2, ..., 10]
    zeros_matrix = np.zeros((3, 5))        # 3 rows, 5 cols of float64 zeros
    identity = np.eye(3)                   # 3x3 identity matrix

    return sequential, zeros_matrix, identity

    # Alternative: sequential could also be np.array(range(1, 11))
    # or np.linspace(1, 10, 10, dtype=int)


# ---------------------------------------------------------------------------
# Exercise 2: Linspace and Arange
# ---------------------------------------------------------------------------
def create_sequences() -> tuple[np.ndarray, np.ndarray]:
    """Create even numbers 0-18 with arange, and 5 points 0-1 with linspace."""
    evens = np.arange(0, 20, 2)        # [0, 2, 4, ..., 18]
    spaced = np.linspace(0, 1, 5)      # [0.0, 0.25, 0.5, 0.75, 1.0]

    return evens, spaced


# ---------------------------------------------------------------------------
# Exercise 3: Array Attributes
# ---------------------------------------------------------------------------
def get_array_info(arr: np.ndarray) -> dict:
    """Extract shape, ndim, size, and dtype from an array."""
    return {
        'shape': arr.shape,
        'ndim': arr.ndim,
        'size': arr.size,
        'dtype': arr.dtype,
    }


# ---------------------------------------------------------------------------
# Exercise 4: Type Casting
# ---------------------------------------------------------------------------
def cast_array(arr: np.ndarray, target_dtype: np.dtype) -> np.ndarray:
    """Cast array to target dtype without modifying the original."""
    return arr.astype(target_dtype)

    # Note: astype() always returns a new array (even if dtype is the same,
    # unless you pass copy=False). So it's safe -- the original is untouched.


# ---------------------------------------------------------------------------
# Exercise 5: Boolean Indexing
# ---------------------------------------------------------------------------
def filter_positive_evens(arr: np.ndarray) -> np.ndarray:
    """Return elements that are both positive AND even."""
    mask = (arr > 0) & (arr % 2 == 0)
    return arr[mask]

    # Pythonic alternative (less readable but equivalent):
    # return arr[(arr > 0) & (arr % 2 == 0)]


# ---------------------------------------------------------------------------
# Exercise 6: Fancy Indexing
# ---------------------------------------------------------------------------
def select_elements(matrix: np.ndarray, row_indices: list, col_indices: list) -> np.ndarray:
    """Select elements at corresponding (row, col) index pairs."""
    return matrix[row_indices, col_indices]

    # This uses NumPy's fancy indexing: matrix[[0,1,2], [2,1,0]]
    # returns [matrix[0,2], matrix[1,1], matrix[2,0]]


# ---------------------------------------------------------------------------
# Exercise 7: Slicing Practice
# ---------------------------------------------------------------------------
def extract_submatrix(matrix: np.ndarray) -> np.ndarray:
    """Extract the center 2x2 block from the top-left 4x4 region."""
    return matrix[1:3, 1:3]

    # Rows 1 and 2, Columns 1 and 2 -- the center of the 4x4 block.
    # Note: this returns a VIEW. If you need a copy, add .copy()


# ---------------------------------------------------------------------------
# Exercise 8: Reshaping
# ---------------------------------------------------------------------------
def reshape_to_grid(arr: np.ndarray, rows: int) -> np.ndarray:
    """Reshape a 1D array into a 2D grid with given number of rows."""
    return arr.reshape(rows, -1)

    # The -1 tells NumPy to infer the number of columns automatically.
    # For arr of length 12 and rows=3, this gives shape (3, 4).


# ---------------------------------------------------------------------------
# Exercise 9: Flatten and Ravel
# ---------------------------------------------------------------------------
def safe_flatten(arr: np.ndarray) -> np.ndarray:
    """Return a guaranteed 1D copy of the array."""
    return arr.flatten()

    # flatten() ALWAYS returns a copy.
    # ravel() returns a view when possible, so it would NOT be safe here
    # if we need to guarantee the original is unmodified.


# ---------------------------------------------------------------------------
# Exercise 10: Element-wise Operations
# ---------------------------------------------------------------------------
def normalize_vector(v: np.ndarray) -> np.ndarray:
    """Normalize a vector to unit length (L2 norm = 1)."""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v.copy()  # Return a copy of the zero vector
    return v / norm

    # Alternative using manual computation:
    # norm = np.sqrt(np.sum(v ** 2))
    # return v / norm if norm != 0 else v.copy()


# ---------------------------------------------------------------------------
# Exercise 11: Comparison and Masking
# ---------------------------------------------------------------------------
def clip_outliers(arr: np.ndarray, lower: float, upper: float) -> np.ndarray:
    """Clip values to [lower, upper] using boolean indexing (not np.clip)."""
    result = arr.copy()           # Don't modify original
    result[result < lower] = lower
    result[result > upper] = upper
    return result

    # Alternative using np.where (also valid):
    # result = np.where(arr < lower, lower, arr)
    # result = np.where(result > upper, upper, result)
    # return result

    # Note: In practice, just use np.clip(arr, lower, upper)


# ---------------------------------------------------------------------------
# Exercise 12: Aggregation Basics
# ---------------------------------------------------------------------------
def compute_statistics(arr: np.ndarray) -> dict:
    """Compute mean, std, min, max, range, and median."""
    return {
        'mean': np.mean(arr),
        'std': np.std(arr),
        'min': np.min(arr),
        'max': np.max(arr),
        'range': np.max(arr) - np.min(arr),
        'median': np.median(arr),
    }

    # Alternative using method syntax:
    # 'mean': arr.mean(), 'std': arr.std(), etc.
    # np.ptp(arr) computes peak-to-peak (range) but is deprecated in newer NumPy.


# ---------------------------------------------------------------------------
# Exercise 13: Axis-based Aggregation
# ---------------------------------------------------------------------------
def column_normalize(matrix: np.ndarray) -> np.ndarray:
    """Z-score normalize each column (mean=0, std=1)."""
    means = matrix.mean(axis=0)  # shape: (n_features,)
    stds = matrix.std(axis=0)    # shape: (n_features,)
    return (matrix - means) / stds

    # The subtraction and division broadcast automatically:
    # matrix shape: (n_samples, n_features)
    # means shape:  (n_features,)
    # NumPy broadcasts means across all rows.

    # With keepdims for explicit clarity:
    # means = matrix.mean(axis=0, keepdims=True)  # (1, n_features)
    # stds = matrix.std(axis=0, keepdims=True)     # (1, n_features)
    # return (matrix - means) / stds


# ---------------------------------------------------------------------------
# Exercise 14: Combining Concepts
# ---------------------------------------------------------------------------
def top_k_indices(arr: np.ndarray, k: int) -> np.ndarray:
    """Return indices of the k largest values, sorted descending."""
    # argsort returns indices that would sort the array in ascending order
    sorted_indices = np.argsort(arr)

    # Take the last k indices (largest values) and reverse
    return sorted_indices[-k:][::-1]

    # Alternative: np.argpartition is faster for large arrays (O(n) vs O(n log n))
    # but doesn't guarantee full sort among the top k:
    # top_k_unsorted = np.argpartition(arr, -k)[-k:]
    # top_k_sorted = top_k_unsorted[np.argsort(arr[top_k_unsorted])[::-1]]
    # return top_k_sorted


# ---------------------------------------------------------------------------
# Exercise 15: Practical Application — Grade Analysis
# ---------------------------------------------------------------------------
def analyze_grades(grades: np.ndarray) -> dict:
    """Comprehensive grade analysis using axis-based aggregation."""
    student_averages = grades.mean(axis=1)       # Mean across columns (per row)
    assignment_averages = grades.mean(axis=0)     # Mean across rows (per column)

    return {
        'student_averages': student_averages,
        'assignment_averages': assignment_averages,
        'highest_student': np.argmax(student_averages),
        'hardest_assignment': np.argmin(assignment_averages),
        'passing_counts': np.sum(grades >= 60, axis=0),  # Count passing per column
    }

    # Note on passing_counts:
    # grades >= 60 creates a boolean matrix (True/False for each grade)
    # np.sum(..., axis=0) counts True values per column
    # True counts as 1, False as 0 in a sum


# ===========================================================================
# Tests — run with: python solutions.py
# ===========================================================================
if __name__ == "__main__":
    print("Running NumPy Fundamentals solution tests...\n")

    # Test 1
    seq, zeros_m, ident = create_arrays()
    assert np.array_equal(seq, np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    assert zeros_m.shape == (3, 5)
    assert zeros_m.dtype == np.float64
    assert np.all(zeros_m == 0)
    assert ident.shape == (3, 3)
    assert np.array_equal(ident, np.eye(3))
    print("  [PASS] Exercise 1: Array Creation")

    # Test 2
    evens, spaced = create_sequences()
    assert np.array_equal(evens, np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18]))
    assert len(spaced) == 5
    assert spaced[0] == 0.0
    assert spaced[-1] == 1.0
    print("  [PASS] Exercise 2: Sequences")

    # Test 3
    test_arr = np.zeros((2, 3, 4))
    info = get_array_info(test_arr)
    assert info['shape'] == (2, 3, 4)
    assert info['ndim'] == 3
    assert info['size'] == 24
    assert info['dtype'] == np.float64
    print("  [PASS] Exercise 3: Array Info")

    # Test 4
    int_arr = np.array([1, 2, 3])
    float_arr = cast_array(int_arr, np.float32)
    assert float_arr.dtype == np.float32
    assert int_arr.dtype == np.int64
    assert np.array_equal(float_arr, np.array([1.0, 2.0, 3.0], dtype=np.float32))
    print("  [PASS] Exercise 4: Type Casting")

    # Test 5
    test = np.array([-3, -2, -1, 0, 1, 2, 3, 4, 5, 6])
    result = filter_positive_evens(test)
    assert np.array_equal(result, np.array([2, 4, 6]))
    print("  [PASS] Exercise 5: Boolean Indexing")

    # Test 6
    mat = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    result = select_elements(mat, [0, 1, 2], [2, 1, 0])
    assert np.array_equal(result, np.array([3, 5, 7]))
    print("  [PASS] Exercise 6: Fancy Indexing")

    # Test 7
    mat = np.arange(25).reshape(5, 5)
    result = extract_submatrix(mat)
    assert result.shape == (2, 2)
    assert np.array_equal(result, np.array([[6, 7], [11, 12]]))
    print("  [PASS] Exercise 7: Slicing")

    # Test 8
    arr = np.arange(12)
    result = reshape_to_grid(arr, 3)
    assert result.shape == (3, 4)
    assert np.array_equal(result, np.arange(12).reshape(3, 4))
    print("  [PASS] Exercise 8: Reshaping")

    # Test 9
    mat = np.array([[1, 2], [3, 4]])
    flat = safe_flatten(mat)
    assert flat.shape == (4,)
    flat[0] = 99
    assert mat[0, 0] == 1
    print("  [PASS] Exercise 9: Flatten")

    # Test 10
    v = np.array([3.0, 4.0])
    nv = normalize_vector(v)
    assert np.allclose(np.linalg.norm(nv), 1.0)
    assert np.allclose(nv, [0.6, 0.8])
    zeros = np.zeros(3)
    assert np.array_equal(normalize_vector(zeros), zeros)
    print("  [PASS] Exercise 10: Normalize Vector")

    # Test 11
    arr = np.array([-10.0, -1.0, 0.0, 5.0, 100.0])
    original = arr.copy()
    clipped = clip_outliers(arr, 0.0, 10.0)
    assert np.array_equal(clipped, np.array([0.0, 0.0, 0.0, 5.0, 10.0]))
    assert np.array_equal(arr, original)
    print("  [PASS] Exercise 11: Clip Outliers")

    # Test 12
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    stats = compute_statistics(arr)
    assert stats['mean'] == 3.0
    assert np.isclose(stats['std'], np.std(arr))
    assert stats['min'] == 1.0
    assert stats['max'] == 5.0
    assert stats['range'] == 4.0
    assert stats['median'] == 3.0
    print("  [PASS] Exercise 12: Statistics")

    # Test 13
    mat = np.array([[1.0, 100.0], [2.0, 200.0], [3.0, 300.0]])
    norm = column_normalize(mat)
    assert norm.shape == mat.shape
    assert np.allclose(norm.mean(axis=0), [0.0, 0.0], atol=1e-10)
    assert np.allclose(norm.std(axis=0), [1.0, 1.0], atol=1e-10)
    print("  [PASS] Exercise 13: Column Normalize")

    # Test 14
    arr = np.array([10, 30, 20, 50, 40])
    result = top_k_indices(arr, 3)
    assert np.array_equal(result, np.array([3, 4, 1]))
    print("  [PASS] Exercise 14: Top K Indices")

    # Test 15
    grades = np.array([
        [90, 80, 70],
        [50, 60, 55],
        [85, 95, 90],
        [40, 30, 20]
    ], dtype=np.float64)
    analysis = analyze_grades(grades)
    assert np.allclose(analysis['student_averages'], [80.0, 55.0, 90.0, 30.0])
    assert np.allclose(analysis['assignment_averages'], [66.25, 66.25, 58.75])
    assert analysis['highest_student'] == 2
    assert analysis['hardest_assignment'] == 2
    assert np.array_equal(analysis['passing_counts'], np.array([2, 3, 2]))
    print("  [PASS] Exercise 15: Grade Analysis")

    print("\nAll 15 solutions verified!")
