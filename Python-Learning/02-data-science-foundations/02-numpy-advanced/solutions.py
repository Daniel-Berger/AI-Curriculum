"""
Module 02: NumPy Advanced - Solutions
======================================

Complete solutions for all 15 exercises.
Run this file to verify all solutions pass:
    python solutions.py
"""

import numpy as np


# ---------------------------------------------------------------------------
# Exercise 1: Broadcasting — Row Normalization
# ---------------------------------------------------------------------------
def subtract_row_mean(matrix: np.ndarray) -> np.ndarray:
    """Subtract the mean of each row from every element in that row."""
    row_means = matrix.mean(axis=1, keepdims=True)  # shape (n_rows, 1)
    return matrix - row_means  # Broadcasting: (n, m) - (n, 1)

    # Without keepdims you'd need:
    # row_means = matrix.mean(axis=1)[:, np.newaxis]  # (n,) -> (n, 1)
    # return matrix - row_means


# ---------------------------------------------------------------------------
# Exercise 2: Broadcasting — Outer Product
# ---------------------------------------------------------------------------
def multiplication_table(n: int) -> np.ndarray:
    """Create an n x n multiplication table using broadcasting."""
    row = np.arange(1, n + 1)                    # shape (n,)
    col = np.arange(1, n + 1)[:, np.newaxis]     # shape (n, 1)
    return col * row                              # Broadcasting: (n,1) * (n,) -> (n,n)

    # Alternative: np.outer(np.arange(1, n+1), np.arange(1, n+1))
    # Alternative: np.einsum('i,j->ij', np.arange(1,n+1), np.arange(1,n+1))


# ---------------------------------------------------------------------------
# Exercise 3: Broadcasting — Distance from Point
# ---------------------------------------------------------------------------
def distances_from_origin(points: np.ndarray) -> np.ndarray:
    """Compute Euclidean distance of each point from origin."""
    return np.sqrt(np.sum(points ** 2, axis=1))

    # Alternative: np.linalg.norm(points, axis=1)
    # Alternative: np.sqrt((points ** 2).sum(axis=1))
    # Alternative: np.einsum('ij,ij->i', points, points) ** 0.5


# ---------------------------------------------------------------------------
# Exercise 4: Vectorization — Sigmoid Function
# ---------------------------------------------------------------------------
def sigmoid(x: np.ndarray) -> np.ndarray:
    """Sigmoid activation function: 1 / (1 + exp(-x))."""
    return 1.0 / (1.0 + np.exp(-x))

    # For numerical stability with very large negative values:
    # return np.where(x >= 0,
    #                 1 / (1 + np.exp(-x)),
    #                 np.exp(x) / (1 + np.exp(x)))


# ---------------------------------------------------------------------------
# Exercise 5: Vectorization — Softmax
# ---------------------------------------------------------------------------
def softmax(x: np.ndarray) -> np.ndarray:
    """Numerically stable softmax for a 1D array."""
    shifted = x - np.max(x)        # Subtract max for numerical stability
    exp_vals = np.exp(shifted)
    return exp_vals / np.sum(exp_vals)

    # Without the max subtraction, exp(1000) would overflow to inf.
    # Subtracting max doesn't change the result because:
    # exp(x_i - c) / sum(exp(x_j - c)) = exp(x_i) / sum(exp(x_j))


# ---------------------------------------------------------------------------
# Exercise 6: Linear Algebra — Solve System
# ---------------------------------------------------------------------------
def solve_linear_system(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Solve Ax = b for x."""
    return np.linalg.solve(A, b)

    # Alternative (less efficient, less numerically stable):
    # return np.linalg.inv(A) @ b


# ---------------------------------------------------------------------------
# Exercise 7: Linear Algebra — Matrix Properties
# ---------------------------------------------------------------------------
def matrix_properties(M: np.ndarray) -> dict:
    """Compute determinant, trace, rank, invertibility, and eigenvalues."""
    eigenvalues = np.real(np.linalg.eigvals(M))
    det = np.linalg.det(M)

    return {
        'determinant': det,
        'trace': np.trace(M),
        'rank': np.linalg.matrix_rank(M),
        'is_invertible': not np.isclose(det, 0),
        'eigenvalues': np.sort(eigenvalues)[::-1],  # Descending order
    }

    # Note: np.linalg.eigvals returns eigenvalues only (faster than eig).
    # np.real() handles potential tiny imaginary parts from float arithmetic.


# ---------------------------------------------------------------------------
# Exercise 8: Linear Algebra — Projection Matrix
# ---------------------------------------------------------------------------
def project_onto_vector(points: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """Project each point onto the given direction vector."""
    # Scalar projection for each point: (point . direction) / (direction . direction)
    # Shape: (n,)
    scalars = (points @ direction) / (direction @ direction)

    # Outer product to get projected points: scalar * direction for each point
    # scalars[:, np.newaxis] has shape (n, 1), direction has shape (d,)
    # Broadcasting: (n, 1) * (d,) -> (n, d)
    return scalars[:, np.newaxis] * direction

    # Alternative using einsum:
    # coeffs = np.einsum('ij,j->i', points, direction) / np.einsum('i,i->', direction, direction)
    # return np.einsum('i,j->ij', coeffs, direction)


# ---------------------------------------------------------------------------
# Exercise 9: Random — Reproducible Dataset
# ---------------------------------------------------------------------------
def generate_clusters(
    n_samples: int,
    n_clusters: int,
    seed: int = 42
) -> tuple[np.ndarray, np.ndarray]:
    """Generate a synthetic 2D clustering dataset."""
    rng = np.random.default_rng(seed)
    samples_per_cluster = n_samples // n_clusters

    # Generate cluster centers
    centers = rng.uniform(-10, 10, size=(n_clusters, 2))

    # Generate points around each center
    X_parts = []
    label_parts = []
    for i in range(n_clusters):
        points = rng.normal(loc=centers[i], scale=1.0, size=(samples_per_cluster, 2))
        X_parts.append(points)
        label_parts.append(np.full(samples_per_cluster, i))

    X = np.vstack(X_parts)
    labels = np.concatenate(label_parts)

    return X, labels

    # Note: In real ML, you'd use sklearn.datasets.make_blobs.
    # This exercise is about understanding the mechanics.


# ---------------------------------------------------------------------------
# Exercise 10: Random — Bootstrap Sampling
# ---------------------------------------------------------------------------
def bootstrap_mean_ci(
    data: np.ndarray,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: int = 42
) -> tuple[float, float, float]:
    """Compute bootstrap confidence interval for the mean."""
    rng = np.random.default_rng(seed)
    n = len(data)

    # Draw bootstrap samples and compute means
    bootstrap_means = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        sample = rng.choice(data, size=n, replace=True)
        bootstrap_means[i] = sample.mean()

    # Compute percentiles
    alpha = (1 - confidence) / 2
    lower = np.percentile(bootstrap_means, alpha * 100)
    upper = np.percentile(bootstrap_means, (1 - alpha) * 100)

    return float(np.mean(data)), float(lower), float(upper)

    # Vectorized alternative (faster, avoids loop):
    # indices = rng.integers(0, n, size=(n_bootstrap, n))
    # samples = data[indices]  # fancy indexing: (n_bootstrap, n)
    # bootstrap_means = samples.mean(axis=1)


# ---------------------------------------------------------------------------
# Exercise 11: Stacking and Splitting
# ---------------------------------------------------------------------------
def train_test_split(
    X: np.ndarray,
    y: np.ndarray,
    test_ratio: float = 0.2,
    seed: int = 42
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data into training and test sets."""
    rng = np.random.default_rng(seed)
    n = len(y)
    indices = rng.permutation(n)

    test_size = int(n * test_ratio)
    test_idx = indices[:test_size]
    train_idx = indices[test_size:]

    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]

    # In real ML, use sklearn.model_selection.train_test_split
    # which also supports stratification.


# ---------------------------------------------------------------------------
# Exercise 12: np.where — Vectorized Conditional
# ---------------------------------------------------------------------------
def categorize_bmi(bmis: np.ndarray) -> np.ndarray:
    """Categorize BMI values into string labels."""
    conditions = [
        bmis < 18.5,
        (bmis >= 18.5) & (bmis < 25.0),
        (bmis >= 25.0) & (bmis < 30.0),
        bmis >= 30.0,
    ]
    choices = ['underweight', 'normal', 'overweight', 'obese']

    return np.select(conditions, choices, default='unknown')

    # Alternative with nested np.where (less readable):
    # return np.where(bmis < 18.5, 'underweight',
    #        np.where(bmis < 25.0, 'normal',
    #        np.where(bmis < 30.0, 'overweight', 'obese')))


# ---------------------------------------------------------------------------
# Exercise 13: np.where — Replace Conditionally
# ---------------------------------------------------------------------------
def winsorize(arr: np.ndarray, percentile: float = 5.0) -> np.ndarray:
    """Winsorize by clipping to percentile bounds."""
    lower = np.percentile(arr, percentile)
    upper = np.percentile(arr, 100 - percentile)
    return np.clip(arr, lower, upper)

    # Alternative without np.clip:
    # result = arr.copy()
    # result = np.where(result < lower, lower, result)
    # result = np.where(result > upper, upper, result)
    # return result


# ---------------------------------------------------------------------------
# Exercise 14: Einsum — Multiple Operations
# ---------------------------------------------------------------------------
def einsum_operations(A: np.ndarray, B: np.ndarray) -> dict:
    """Compute various operations using only np.einsum."""
    return {
        'trace_A': np.einsum('ii->', A),           # Sum of diagonal
        'col_sums_A': np.einsum('ij->j', A),       # Sum along axis 0
        'row_sums_B': np.einsum('ij->i', B),       # Sum along axis 1
        'matmul': np.einsum('ij,jk->ik', A, B),    # Matrix multiplication
        'element_product_sum': np.einsum('ij,ji->', A, B),
        # 'ij,ji->' means: multiply A[i,j] * B[j,i] then sum all
        # This is equivalent to np.sum(A * B.T)
    }


# ---------------------------------------------------------------------------
# Exercise 15: Putting It All Together — Feature Engineering
# ---------------------------------------------------------------------------
def engineer_features(X: np.ndarray) -> np.ndarray:
    """Expand features with squares and pairwise products."""
    n_samples, n_features = X.shape

    # Original features
    original = X

    # Squared features
    squared = X ** 2

    # Pairwise products: for each pair (i, j) where i < j
    pairwise_cols = []
    for i in range(n_features):
        for j in range(i + 1, n_features):
            pairwise_cols.append(X[:, i] * X[:, j])

    # Stack all parts horizontally
    if pairwise_cols:
        pairwise = np.column_stack(pairwise_cols)
        return np.hstack([original, squared, pairwise])
    else:
        return np.hstack([original, squared])

    # Note: sklearn.preprocessing.PolynomialFeatures does this automatically.
    # The loop here is over features (usually small), not samples,
    # so performance is fine.


# ===========================================================================
# Tests
# ===========================================================================
if __name__ == "__main__":
    print("Running NumPy Advanced solution tests...\n")

    # Test 1
    m = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    result = subtract_row_mean(m)
    assert result.shape == m.shape
    assert np.allclose(result, [[-1, 0, 1], [-1, 0, 1]])
    assert np.allclose(result.mean(axis=1), [0, 0])
    print("  [PASS] Exercise 1: Subtract Row Mean")

    # Test 2
    table = multiplication_table(5)
    assert table.shape == (5, 5)
    assert table[0, 0] == 1
    assert table[4, 4] == 25
    assert table[2, 3] == 12
    assert np.array_equal(table, table.T)
    print("  [PASS] Exercise 2: Multiplication Table")

    # Test 3
    pts = np.array([[3.0, 4.0], [0.0, 0.0], [1.0, 0.0]])
    dists = distances_from_origin(pts)
    assert np.allclose(dists, [5.0, 0.0, 1.0])
    print("  [PASS] Exercise 3: Distances from Origin")

    # Test 4
    x = np.array([-10, 0, 10])
    s = sigmoid(x)
    assert np.allclose(s[1], 0.5)
    assert s[0] < 0.001
    assert s[2] > 0.999
    x2d = np.array([[0, 1], [-1, 0]])
    s2d = sigmoid(x2d)
    assert s2d.shape == (2, 2)
    assert np.allclose(s2d[0, 0], 0.5)
    print("  [PASS] Exercise 4: Sigmoid")

    # Test 5
    x = np.array([1.0, 2.0, 3.0])
    s = softmax(x)
    assert np.allclose(s.sum(), 1.0)
    assert s[2] > s[1] > s[0]
    large = np.array([1000, 1001, 1002])
    s_large = softmax(large)
    assert np.allclose(s_large.sum(), 1.0)
    assert not np.any(np.isnan(s_large))
    print("  [PASS] Exercise 5: Softmax")

    # Test 6
    A = np.array([[2.0, 1.0], [1.0, 3.0]])
    b = np.array([5.0, 10.0])
    x = solve_linear_system(A, b)
    assert np.allclose(A @ x, b)
    print("  [PASS] Exercise 6: Solve Linear System")

    # Test 7
    M = np.array([[4.0, -2.0], [1.0, 1.0]])
    props = matrix_properties(M)
    assert np.isclose(props['determinant'], 6.0)
    assert np.isclose(props['trace'], 5.0)
    assert props['rank'] == 2
    assert props['is_invertible'] is True
    assert len(props['eigenvalues']) == 2
    assert props['eigenvalues'][0] >= props['eigenvalues'][1]
    print("  [PASS] Exercise 7: Matrix Properties")

    # Test 8
    pts = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    direction = np.array([1.0, 0.0])
    proj = project_onto_vector(pts, direction)
    assert np.allclose(proj, [[1, 0], [0, 0], [1, 0]])
    print("  [PASS] Exercise 8: Projection")

    # Test 9
    X, labels = generate_clusters(300, 3, seed=42)
    assert X.shape == (300, 2)
    assert labels.shape == (300,)
    assert set(labels) == {0, 1, 2}
    assert np.sum(labels == 0) == 100
    X2, labels2 = generate_clusters(300, 3, seed=42)
    assert np.array_equal(X, X2)
    print("  [PASS] Exercise 9: Generate Clusters")

    # Test 10
    rng_test = np.random.default_rng(0)
    data = rng_test.normal(50, 10, size=100)
    mean_val, lower, upper = bootstrap_mean_ci(data, n_bootstrap=2000, seed=42)
    assert lower < mean_val < upper
    assert lower < 50 < upper
    print("  [PASS] Exercise 10: Bootstrap CI")

    # Test 11
    X = np.arange(50).reshape(10, 5)
    y = np.arange(10)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_ratio=0.3, seed=42)
    assert X_train.shape[0] == 7
    assert X_test.shape[0] == 3
    assert y_train.shape[0] == 7
    assert y_test.shape[0] == 3
    all_y = np.sort(np.concatenate([y_train, y_test]))
    assert np.array_equal(all_y, np.arange(10))
    print("  [PASS] Exercise 11: Train/Test Split")

    # Test 12
    bmis = np.array([16.0, 18.5, 22.0, 27.5, 35.0])
    cats = categorize_bmi(bmis)
    assert cats[0] == 'underweight'
    assert cats[1] == 'normal'
    assert cats[2] == 'normal'
    assert cats[3] == 'overweight'
    assert cats[4] == 'obese'
    print("  [PASS] Exercise 12: BMI Categorization")

    # Test 13
    arr = np.array([1.0, 2, 3, 4, 5, 6, 7, 8, 9, 100])
    original = arr.copy()
    w = winsorize(arr, percentile=10)
    assert np.array_equal(arr, original)
    assert w.min() >= np.percentile(arr, 10)
    assert w.max() <= np.percentile(arr, 90)
    print("  [PASS] Exercise 13: Winsorize")

    # Test 14
    A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    B = np.array([[9, 8, 7], [6, 5, 4], [3, 2, 1]])
    result = einsum_operations(A, B)
    assert np.isclose(result['trace_A'], 15)
    assert np.array_equal(result['col_sums_A'], [12, 15, 18])
    assert np.array_equal(result['row_sums_B'], [24, 15, 6])
    assert np.array_equal(result['matmul'], A @ B)
    expected_eps = np.sum(A * B.T)
    assert np.isclose(result['element_product_sum'], expected_eps)
    print("  [PASS] Exercise 14: Einsum Operations")

    # Test 15
    X = np.array([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]])
    expanded = engineer_features(X)
    assert expanded.shape == (2, 9)
    assert np.array_equal(expanded[:, :3], X)
    assert np.array_equal(expanded[:, 3:6], X ** 2)
    assert np.allclose(expanded[0, 6], 2.0)
    assert np.allclose(expanded[0, 7], 3.0)
    assert np.allclose(expanded[0, 8], 6.0)
    print("  [PASS] Exercise 15: Feature Engineering")

    print("\nAll 15 solutions verified!")
