"""
Module 01: NumPy Fundamentals - Exercises
==========================================

15 exercises covering ndarray creation, indexing, slicing, reshaping,
element-wise operations, and aggregation.

Run this file directly to check your solutions:
    python exercises.py

Each exercise has assert-based tests that verify correctness.
"""

import numpy as np


# ---------------------------------------------------------------------------
# Exercise 1: Array Creation Basics
# ---------------------------------------------------------------------------
def create_arrays() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create and return three arrays:
    1. A 1D array of integers from 1 to 10 (inclusive)
    2. A 2D array of zeros with shape (3, 5), dtype float64
    3. A 3x3 identity matrix

    Returns:
        Tuple of (sequential, zeros_matrix, identity)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Linspace and Arange
# ---------------------------------------------------------------------------
def create_sequences() -> tuple[np.ndarray, np.ndarray]:
    """
    Create and return two arrays:
    1. Using arange: even numbers from 0 to 20 (exclusive), i.e. [0, 2, 4, ..., 18]
    2. Using linspace: 5 evenly spaced values from 0 to 1 (inclusive)

    Returns:
        Tuple of (evens, spaced)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Array Attributes
# ---------------------------------------------------------------------------
def get_array_info(arr: np.ndarray) -> dict:
    """
    Given an arbitrary NumPy array, return a dictionary with:
    - 'shape': the array's shape (tuple)
    - 'ndim': number of dimensions (int)
    - 'size': total number of elements (int)
    - 'dtype': the data type (np.dtype)

    Args:
        arr: Any NumPy array

    Returns:
        Dictionary with keys 'shape', 'ndim', 'size', 'dtype'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Type Casting
# ---------------------------------------------------------------------------
def cast_array(arr: np.ndarray, target_dtype: np.dtype) -> np.ndarray:
    """
    Cast the given array to the specified dtype.
    The original array must NOT be modified.

    Args:
        arr: Input array
        target_dtype: Target data type (e.g., np.float32)

    Returns:
        New array with the specified dtype
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Boolean Indexing
# ---------------------------------------------------------------------------
def filter_positive_evens(arr: np.ndarray) -> np.ndarray:
    """
    Given an array of integers, return only the elements that are
    BOTH positive AND even. Maintain original order.

    Example: [−3, −2, −1, 0, 1, 2, 3, 4] -> [2, 4]

    Args:
        arr: 1D array of integers

    Returns:
        Filtered array containing only positive even integers
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Fancy Indexing
# ---------------------------------------------------------------------------
def select_elements(matrix: np.ndarray, row_indices: list, col_indices: list) -> np.ndarray:
    """
    Given a 2D matrix and lists of row/column indices, return the elements
    at positions (row_indices[0], col_indices[0]), (row_indices[1], col_indices[1]), etc.

    Example:
        matrix = [[1,2,3],[4,5,6],[7,8,9]]
        row_indices = [0, 1, 2]
        col_indices = [2, 1, 0]
        result = [3, 5, 7]

    Args:
        matrix: 2D NumPy array
        row_indices: List of row indices
        col_indices: List of column indices

    Returns:
        1D array of selected elements
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Slicing Practice
# ---------------------------------------------------------------------------
def extract_submatrix(matrix: np.ndarray) -> np.ndarray:
    """
    Given a matrix of shape (N, M) where N >= 4 and M >= 4,
    extract the 2x2 submatrix from the CENTER of the first 4 rows
    and first 4 columns.

    For a matrix with top-left 4x4 block:
        [[ a  b  c  d]
         [ e  f  g  h]
         [ i  j  k  l]
         [ m  n  o  p]]
    Return:
        [[ f  g]
         [ j  k]]

    Args:
        matrix: 2D array with shape >= (4, 4)

    Returns:
        2x2 submatrix from the center of the top-left 4x4 block
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Reshaping
# ---------------------------------------------------------------------------
def reshape_to_grid(arr: np.ndarray, rows: int) -> np.ndarray:
    """
    Reshape a 1D array into a 2D grid with the specified number of rows.
    The number of columns should be inferred automatically.

    Args:
        arr: 1D array whose length is divisible by rows
        rows: Number of rows in the output

    Returns:
        2D array with shape (rows, len(arr) // rows)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Flatten and Ravel
# ---------------------------------------------------------------------------
def safe_flatten(arr: np.ndarray) -> np.ndarray:
    """
    Return a 1D copy of the input array (regardless of its shape).
    Modifying the returned array must NOT affect the original.

    Use the appropriate method (flatten vs ravel) to guarantee a copy.

    Args:
        arr: NumPy array of any shape

    Returns:
        1D copy of the array
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Element-wise Operations
# ---------------------------------------------------------------------------
def normalize_vector(v: np.ndarray) -> np.ndarray:
    """
    Normalize a vector to have unit length (L2 norm = 1).
    Formula: v_normalized = v / ||v||

    Where ||v|| is the L2 norm: sqrt(sum(v_i^2))

    If the vector is all zeros, return it unchanged.

    Args:
        v: 1D array of floats

    Returns:
        Normalized vector with L2 norm of 1 (or zeros if input is all zeros)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Comparison and Masking
# ---------------------------------------------------------------------------
def clip_outliers(arr: np.ndarray, lower: float, upper: float) -> np.ndarray:
    """
    Replace values below `lower` with `lower` and values above `upper` with `upper`.
    Do NOT modify the original array — return a new array.

    Implement this WITHOUT using np.clip (use boolean indexing instead).

    Args:
        arr: Input array
        lower: Minimum allowed value
        upper: Maximum allowed value

    Returns:
        New array with values clipped to [lower, upper]
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Aggregation Basics
# ---------------------------------------------------------------------------
def compute_statistics(arr: np.ndarray) -> dict:
    """
    Compute basic statistics for a 1D array.

    Returns a dictionary with keys:
    - 'mean': arithmetic mean
    - 'std': standard deviation
    - 'min': minimum value
    - 'max': maximum value
    - 'range': max - min
    - 'median': median value

    Args:
        arr: 1D array of numbers

    Returns:
        Dictionary of statistics
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 13: Axis-based Aggregation
# ---------------------------------------------------------------------------
def column_normalize(matrix: np.ndarray) -> np.ndarray:
    """
    Normalize each column of a 2D matrix to have mean=0 and std=1 (Z-score).
    Formula: (x - column_mean) / column_std

    Args:
        matrix: 2D array of shape (n_samples, n_features)

    Returns:
        Normalized matrix with same shape
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 14: Combining Concepts
# ---------------------------------------------------------------------------
def top_k_indices(arr: np.ndarray, k: int) -> np.ndarray:
    """
    Return the indices of the k largest values in a 1D array,
    sorted from largest to smallest.

    Example: arr = [10, 30, 20, 50, 40], k = 3
             result = [3, 4, 1]  (indices of 50, 40, 30)

    Hint: Look up np.argsort.

    Args:
        arr: 1D array
        k: Number of top indices to return

    Returns:
        1D array of k indices, sorted by descending value
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 15: Practical Application — Grade Analysis
# ---------------------------------------------------------------------------
def analyze_grades(grades: np.ndarray) -> dict:
    """
    Given a 2D array where rows are students and columns are assignments,
    compute:
    - 'student_averages': mean grade per student (1D array, one per row)
    - 'assignment_averages': mean grade per assignment (1D array, one per column)
    - 'highest_student': index of student with highest overall average
    - 'hardest_assignment': index of assignment with lowest average
    - 'passing_counts': number of students passing each assignment (grade >= 60)
                        (1D array, one per column)

    Args:
        grades: 2D array of shape (n_students, n_assignments)

    Returns:
        Dictionary with the keys described above
    """
    pass


# ===========================================================================
# Tests — run with: python exercises.py
# ===========================================================================
if __name__ == "__main__":
    print("Running NumPy Fundamentals tests...\n")

    # Test 1: Array Creation
    seq, zeros_m, ident = create_arrays()
    assert np.array_equal(seq, np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    assert zeros_m.shape == (3, 5)
    assert zeros_m.dtype == np.float64
    assert np.all(zeros_m == 0)
    assert ident.shape == (3, 3)
    assert np.array_equal(ident, np.eye(3))
    print("  [PASS] Exercise 1: Array Creation")

    # Test 2: Sequences
    evens, spaced = create_sequences()
    assert np.array_equal(evens, np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18]))
    assert len(spaced) == 5
    assert spaced[0] == 0.0
    assert spaced[-1] == 1.0
    print("  [PASS] Exercise 2: Sequences")

    # Test 3: Array Info
    test_arr = np.zeros((2, 3, 4))
    info = get_array_info(test_arr)
    assert info['shape'] == (2, 3, 4)
    assert info['ndim'] == 3
    assert info['size'] == 24
    assert info['dtype'] == np.float64
    print("  [PASS] Exercise 3: Array Info")

    # Test 4: Type Casting
    int_arr = np.array([1, 2, 3])
    float_arr = cast_array(int_arr, np.float32)
    assert float_arr.dtype == np.float32
    assert int_arr.dtype == np.int64  # original unchanged
    assert np.array_equal(float_arr, np.array([1.0, 2.0, 3.0], dtype=np.float32))
    print("  [PASS] Exercise 4: Type Casting")

    # Test 5: Boolean Indexing
    test = np.array([-3, -2, -1, 0, 1, 2, 3, 4, 5, 6])
    result = filter_positive_evens(test)
    assert np.array_equal(result, np.array([2, 4, 6]))
    print("  [PASS] Exercise 5: Boolean Indexing")

    # Test 6: Fancy Indexing
    mat = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    result = select_elements(mat, [0, 1, 2], [2, 1, 0])
    assert np.array_equal(result, np.array([3, 5, 7]))
    print("  [PASS] Exercise 6: Fancy Indexing")

    # Test 7: Slicing
    mat = np.arange(25).reshape(5, 5)
    result = extract_submatrix(mat)
    assert result.shape == (2, 2)
    assert np.array_equal(result, np.array([[6, 7], [11, 12]]))
    print("  [PASS] Exercise 7: Slicing")

    # Test 8: Reshaping
    arr = np.arange(12)
    result = reshape_to_grid(arr, 3)
    assert result.shape == (3, 4)
    assert np.array_equal(result, np.arange(12).reshape(3, 4))
    print("  [PASS] Exercise 8: Reshaping")

    # Test 9: Flatten
    mat = np.array([[1, 2], [3, 4]])
    flat = safe_flatten(mat)
    assert flat.shape == (4,)
    flat[0] = 99
    assert mat[0, 0] == 1  # original unchanged
    print("  [PASS] Exercise 9: Flatten")

    # Test 10: Normalize
    v = np.array([3.0, 4.0])
    nv = normalize_vector(v)
    assert np.allclose(np.linalg.norm(nv), 1.0)
    assert np.allclose(nv, [0.6, 0.8])
    zeros = np.zeros(3)
    assert np.array_equal(normalize_vector(zeros), zeros)
    print("  [PASS] Exercise 10: Normalize Vector")

    # Test 11: Clip Outliers
    arr = np.array([-10.0, -1.0, 0.0, 5.0, 100.0])
    original = arr.copy()
    clipped = clip_outliers(arr, 0.0, 10.0)
    assert np.array_equal(clipped, np.array([0.0, 0.0, 0.0, 5.0, 10.0]))
    assert np.array_equal(arr, original)  # original unchanged
    print("  [PASS] Exercise 11: Clip Outliers")

    # Test 12: Statistics
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    stats = compute_statistics(arr)
    assert stats['mean'] == 3.0
    assert np.isclose(stats['std'], np.std(arr))
    assert stats['min'] == 1.0
    assert stats['max'] == 5.0
    assert stats['range'] == 4.0
    assert stats['median'] == 3.0
    print("  [PASS] Exercise 12: Statistics")

    # Test 13: Column Normalize
    mat = np.array([[1.0, 100.0], [2.0, 200.0], [3.0, 300.0]])
    norm = column_normalize(mat)
    assert norm.shape == mat.shape
    assert np.allclose(norm.mean(axis=0), [0.0, 0.0], atol=1e-10)
    assert np.allclose(norm.std(axis=0), [1.0, 1.0], atol=1e-10)
    print("  [PASS] Exercise 13: Column Normalize")

    # Test 14: Top K
    arr = np.array([10, 30, 20, 50, 40])
    result = top_k_indices(arr, 3)
    assert np.array_equal(result, np.array([3, 4, 1]))
    print("  [PASS] Exercise 14: Top K Indices")

    # Test 15: Grade Analysis
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

    print("\nAll 15 exercises passed!")
