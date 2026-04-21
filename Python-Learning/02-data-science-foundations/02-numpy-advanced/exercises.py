"""
Module 02: NumPy Advanced - Exercises
======================================

15 exercises covering broadcasting, vectorization, linear algebra,
random numbers, stacking/splitting, np.where, and einsum.

Run this file directly to check your solutions:
    python exercises.py
"""

import numpy as np


# ---------------------------------------------------------------------------
# Exercise 1: Broadcasting — Row Normalization
# ---------------------------------------------------------------------------
def subtract_row_mean(matrix: np.ndarray) -> np.ndarray:
    """
    Subtract the mean of each row from every element in that row.
    Use broadcasting (no loops).

    Example:
        [[1, 2, 3],     row means: [2, 5]
         [4, 5, 6]]
        Result: [[-1, 0, 1],
                 [-1, 0, 1]]

    Args:
        matrix: 2D array of shape (n_rows, n_cols)

    Returns:
        Row-centered matrix (same shape)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Broadcasting — Outer Product
# ---------------------------------------------------------------------------
def multiplication_table(n: int) -> np.ndarray:
    """
    Create an n x n multiplication table using broadcasting.
    Element [i, j] should be (i+1) * (j+1).

    Example (n=4):
        [[ 1  2  3  4]
         [ 2  4  6  8]
         [ 3  6  9 12]
         [ 4  8 12 16]]

    Do NOT use loops. Use broadcasting with column and row vectors.

    Args:
        n: Size of the multiplication table

    Returns:
        n x n multiplication table
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Broadcasting — Distance from Point
# ---------------------------------------------------------------------------
def distances_from_origin(points: np.ndarray) -> np.ndarray:
    """
    Given an array of 2D points with shape (n, 2), compute the Euclidean
    distance of each point from the origin (0, 0).

    Use vectorized operations (no loops).

    Args:
        points: 2D array of shape (n, 2), each row is [x, y]

    Returns:
        1D array of distances, shape (n,)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Vectorization — Sigmoid Function
# ---------------------------------------------------------------------------
def sigmoid(x: np.ndarray) -> np.ndarray:
    """
    Implement the sigmoid function: sigma(x) = 1 / (1 + exp(-x))

    Must work for arrays of any shape (1D, 2D, etc.).
    Must be fully vectorized (no loops).

    Args:
        x: Input array of any shape

    Returns:
        Array of same shape with sigmoid applied element-wise
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Vectorization — Softmax
# ---------------------------------------------------------------------------
def softmax(x: np.ndarray) -> np.ndarray:
    """
    Implement the softmax function for a 1D array:
        softmax(x_i) = exp(x_i) / sum(exp(x_j))

    For numerical stability, subtract max(x) before exponentiation.

    The output should sum to 1.0.

    Args:
        x: 1D input array

    Returns:
        1D array of same shape, values sum to 1.0
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Linear Algebra — Solve System
# ---------------------------------------------------------------------------
def solve_linear_system(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Solve the linear system Ax = b for x.

    Args:
        A: Square coefficient matrix of shape (n, n)
        b: Right-hand side vector of shape (n,)

    Returns:
        Solution vector x of shape (n,)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Linear Algebra — Matrix Properties
# ---------------------------------------------------------------------------
def matrix_properties(M: np.ndarray) -> dict:
    """
    Compute properties of a square matrix M.

    Returns a dictionary with:
    - 'determinant': the determinant (float)
    - 'trace': the trace (sum of diagonal) (float)
    - 'rank': the matrix rank (int)
    - 'is_invertible': whether det != 0 (bool)
    - 'eigenvalues': sorted eigenvalues in descending order (1D array)

    Args:
        M: Square matrix

    Returns:
        Dictionary of properties
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Linear Algebra — Projection Matrix
# ---------------------------------------------------------------------------
def project_onto_vector(points: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """
    Project each point onto the given direction vector.
    Formula: proj = (point . direction / direction . direction) * direction

    This is a core operation in PCA and linear regression.

    Args:
        points: Array of shape (n, d) -- n points in d dimensions
        direction: 1D direction vector of shape (d,)

    Returns:
        Projected points, shape (n, d)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Random — Reproducible Dataset
# ---------------------------------------------------------------------------
def generate_clusters(
    n_samples: int,
    n_clusters: int,
    seed: int = 42
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a synthetic 2D clustering dataset with reproducible results.

    Steps:
    1. Create a Generator with the given seed
    2. Generate n_clusters random 2D center points from uniform[-10, 10]
    3. For each cluster, generate n_samples // n_clusters points
       from a normal distribution centered at that cluster center, std=1.0
    4. Create labels (0, 1, 2, ...) for each cluster

    Args:
        n_samples: Total number of points (divisible by n_clusters)
        n_clusters: Number of clusters
        seed: Random seed

    Returns:
        Tuple of (X, labels) where:
        - X has shape (n_samples, 2)
        - labels has shape (n_samples,) with values 0 to n_clusters-1
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Random — Bootstrap Sampling
# ---------------------------------------------------------------------------
def bootstrap_mean_ci(
    data: np.ndarray,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: int = 42
) -> tuple[float, float, float]:
    """
    Compute a bootstrap confidence interval for the mean.

    Steps:
    1. Create a Generator with the given seed
    2. Draw n_bootstrap samples (with replacement) of the same size as data
    3. Compute the mean of each bootstrap sample
    4. Return the mean, lower bound, and upper bound of the confidence interval

    The lower bound is the (1-confidence)/2 percentile of bootstrap means.
    The upper bound is the (1+confidence)/2 percentile of bootstrap means.

    For 95% confidence: lower = 2.5th percentile, upper = 97.5th percentile.

    Args:
        data: 1D array of observed values
        n_bootstrap: Number of bootstrap iterations
        confidence: Confidence level (e.g., 0.95 for 95%)
        seed: Random seed

    Returns:
        Tuple of (mean, lower_bound, upper_bound)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Stacking and Splitting
# ---------------------------------------------------------------------------
def train_test_split(
    X: np.ndarray,
    y: np.ndarray,
    test_ratio: float = 0.2,
    seed: int = 42
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split data into training and test sets.

    Steps:
    1. Create a Generator with the given seed
    2. Create a permutation of indices
    3. Split at the appropriate index based on test_ratio
    4. Return X_train, X_test, y_train, y_test

    Args:
        X: Feature matrix of shape (n_samples, n_features)
        y: Label vector of shape (n_samples,)
        test_ratio: Fraction of data for testing (e.g., 0.2 = 20%)
        seed: Random seed

    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: np.where — Vectorized Conditional
# ---------------------------------------------------------------------------
def categorize_bmi(bmis: np.ndarray) -> np.ndarray:
    """
    Categorize BMI values into string labels using vectorized operations.
    Do NOT use loops.

    Categories:
    - BMI < 18.5: 'underweight'
    - 18.5 <= BMI < 25.0: 'normal'
    - 25.0 <= BMI < 30.0: 'overweight'
    - BMI >= 30.0: 'obese'

    Hint: np.select works well for multiple conditions.

    Args:
        bmis: 1D array of BMI values (floats)

    Returns:
        1D array of string labels
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 13: np.where — Replace Conditionally
# ---------------------------------------------------------------------------
def winsorize(arr: np.ndarray, percentile: float = 5.0) -> np.ndarray:
    """
    Winsorize an array: replace values below the lower percentile with
    the lower percentile value, and values above the upper percentile
    with the upper percentile value.

    Example: if percentile=5, clip to [5th percentile, 95th percentile]

    Do NOT modify the original array.

    Args:
        arr: 1D array of values
        percentile: Lower percentile (upper = 100 - percentile)

    Returns:
        Winsorized array
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 14: Einsum — Multiple Operations
# ---------------------------------------------------------------------------
def einsum_operations(A: np.ndarray, B: np.ndarray) -> dict:
    """
    Given two 2D matrices A and B (of compatible shapes for multiplication),
    compute the following using ONLY np.einsum (no other NumPy functions):

    - 'trace_A': trace of A (A must be square for this, but compute sum of A[i,i])
    - 'col_sums_A': column sums of A
    - 'row_sums_B': row sums of B
    - 'matmul': A @ B
    - 'element_product_sum': sum of all elements of A * B^T
      (element-wise product of A and transpose of B, then sum everything)

    Note: For 'element_product_sum', A and B must have the same shape.
    If they don't have the same shape, this is A and B.T having the same shape.

    Args:
        A: 2D array of shape (m, n)
        B: 2D array of shape (n, p)

    Returns:
        Dictionary with keys above
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 15: Putting It All Together — Feature Engineering
# ---------------------------------------------------------------------------
def engineer_features(X: np.ndarray) -> np.ndarray:
    """
    Given a feature matrix X of shape (n_samples, n_features), create
    an expanded feature matrix that includes:

    1. Original features (n_features columns)
    2. Squared features (n_features columns): each feature squared
    3. Pairwise products (n_features * (n_features - 1) / 2 columns):
       for each pair (i, j) where i < j, compute X[:, i] * X[:, j]

    Use vectorized operations. Stack the results horizontally.

    Example: If X has 3 features [a, b, c], the output has columns:
    [a, b, c, a^2, b^2, c^2, a*b, a*c, b*c]

    Args:
        X: Feature matrix of shape (n_samples, n_features)

    Returns:
        Expanded feature matrix
    """
    pass


# ===========================================================================
# Tests
# ===========================================================================
if __name__ == "__main__":
    print("Running NumPy Advanced tests...\n")

    # Test 1: Subtract row mean
    m = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    result = subtract_row_mean(m)
    assert result.shape == m.shape
    assert np.allclose(result, [[-1, 0, 1], [-1, 0, 1]])
    assert np.allclose(result.mean(axis=1), [0, 0])
    print("  [PASS] Exercise 1: Subtract Row Mean")

    # Test 2: Multiplication table
    table = multiplication_table(5)
    assert table.shape == (5, 5)
    assert table[0, 0] == 1
    assert table[4, 4] == 25
    assert table[2, 3] == 12
    assert np.array_equal(table, table.T)  # symmetric
    print("  [PASS] Exercise 2: Multiplication Table")

    # Test 3: Distances from origin
    pts = np.array([[3.0, 4.0], [0.0, 0.0], [1.0, 0.0]])
    dists = distances_from_origin(pts)
    assert np.allclose(dists, [5.0, 0.0, 1.0])
    print("  [PASS] Exercise 3: Distances from Origin")

    # Test 4: Sigmoid
    x = np.array([-10, 0, 10])
    s = sigmoid(x)
    assert np.allclose(s[1], 0.5)
    assert s[0] < 0.001
    assert s[2] > 0.999
    # Test 2D
    x2d = np.array([[0, 1], [-1, 0]])
    s2d = sigmoid(x2d)
    assert s2d.shape == (2, 2)
    assert np.allclose(s2d[0, 0], 0.5)
    print("  [PASS] Exercise 4: Sigmoid")

    # Test 5: Softmax
    x = np.array([1.0, 2.0, 3.0])
    s = softmax(x)
    assert np.allclose(s.sum(), 1.0)
    assert s[2] > s[1] > s[0]
    # Test numerical stability with large values
    large = np.array([1000, 1001, 1002])
    s_large = softmax(large)
    assert np.allclose(s_large.sum(), 1.0)
    assert not np.any(np.isnan(s_large))
    print("  [PASS] Exercise 5: Softmax")

    # Test 6: Solve linear system
    A = np.array([[2.0, 1.0], [1.0, 3.0]])
    b = np.array([5.0, 10.0])
    x = solve_linear_system(A, b)
    assert np.allclose(A @ x, b)
    print("  [PASS] Exercise 6: Solve Linear System")

    # Test 7: Matrix properties
    M = np.array([[4.0, -2.0], [1.0, 1.0]])
    props = matrix_properties(M)
    assert np.isclose(props['determinant'], 6.0)
    assert np.isclose(props['trace'], 5.0)
    assert props['rank'] == 2
    assert props['is_invertible'] is True
    assert len(props['eigenvalues']) == 2
    assert props['eigenvalues'][0] >= props['eigenvalues'][1]  # descending
    print("  [PASS] Exercise 7: Matrix Properties")

    # Test 8: Projection
    pts = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    direction = np.array([1.0, 0.0])  # project onto x-axis
    proj = project_onto_vector(pts, direction)
    assert np.allclose(proj, [[1, 0], [0, 0], [1, 0]])
    print("  [PASS] Exercise 8: Projection")

    # Test 9: Generate clusters
    X, labels = generate_clusters(300, 3, seed=42)
    assert X.shape == (300, 2)
    assert labels.shape == (300,)
    assert set(labels) == {0, 1, 2}
    assert np.sum(labels == 0) == 100
    # Reproducibility test
    X2, labels2 = generate_clusters(300, 3, seed=42)
    assert np.array_equal(X, X2)
    print("  [PASS] Exercise 9: Generate Clusters")

    # Test 10: Bootstrap CI
    rng_test = np.random.default_rng(0)
    data = rng_test.normal(50, 10, size=100)
    mean_val, lower, upper = bootstrap_mean_ci(data, n_bootstrap=2000, seed=42)
    assert lower < mean_val < upper
    assert lower < 50 < upper  # true mean should be in CI (probably)
    print("  [PASS] Exercise 10: Bootstrap CI")

    # Test 11: Train/test split
    X = np.arange(50).reshape(10, 5)
    y = np.arange(10)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_ratio=0.3, seed=42)
    assert X_train.shape[0] == 7
    assert X_test.shape[0] == 3
    assert y_train.shape[0] == 7
    assert y_test.shape[0] == 3
    # All original indices accounted for
    all_y = np.sort(np.concatenate([y_train, y_test]))
    assert np.array_equal(all_y, np.arange(10))
    print("  [PASS] Exercise 11: Train/Test Split")

    # Test 12: BMI categorization
    bmis = np.array([16.0, 18.5, 22.0, 27.5, 35.0])
    cats = categorize_bmi(bmis)
    assert cats[0] == 'underweight'
    assert cats[1] == 'normal'
    assert cats[2] == 'normal'
    assert cats[3] == 'overweight'
    assert cats[4] == 'obese'
    print("  [PASS] Exercise 12: BMI Categorization")

    # Test 13: Winsorize
    arr = np.array([1.0, 2, 3, 4, 5, 6, 7, 8, 9, 100])
    original = arr.copy()
    w = winsorize(arr, percentile=10)
    assert np.array_equal(arr, original)  # original unchanged
    assert w.min() >= np.percentile(arr, 10)
    assert w.max() <= np.percentile(arr, 90)
    print("  [PASS] Exercise 13: Winsorize")

    # Test 14: Einsum
    A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    B = np.array([[9, 8, 7], [6, 5, 4], [3, 2, 1]])
    result = einsum_operations(A, B)
    assert np.isclose(result['trace_A'], 15)  # 1 + 5 + 9
    assert np.array_equal(result['col_sums_A'], [12, 15, 18])
    assert np.array_equal(result['row_sums_B'], [24, 15, 6])
    assert np.array_equal(result['matmul'], A @ B)
    # element_product_sum: sum of A * B.T element-wise
    expected_eps = np.sum(A * B.T)
    assert np.isclose(result['element_product_sum'], expected_eps)
    print("  [PASS] Exercise 14: Einsum Operations")

    # Test 15: Feature engineering
    X = np.array([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]])
    expanded = engineer_features(X)
    # Original (3) + Squared (3) + Pairwise (3) = 9 columns
    assert expanded.shape == (2, 9)
    # Check original features preserved
    assert np.array_equal(expanded[:, :3], X)
    # Check squared
    assert np.array_equal(expanded[:, 3:6], X ** 2)
    # Check pairwise: [a*b, a*c, b*c]
    assert np.allclose(expanded[0, 6], 2.0)   # 1*2
    assert np.allclose(expanded[0, 7], 3.0)   # 1*3
    assert np.allclose(expanded[0, 8], 6.0)   # 2*3
    print("  [PASS] Exercise 15: Feature Engineering")

    print("\nAll 15 exercises passed!")
