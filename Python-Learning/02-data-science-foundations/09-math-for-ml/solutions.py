"""
Module 09: Math for ML - Solutions
==================================

Complete solutions for all 15 exercises.
Run this file to verify all solutions pass:
    python solutions.py
"""

import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# Exercise 1: Vector Operations - Dot Product
# ---------------------------------------------------------------------------
def vector_dot_product(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Compute dot product of two vectors.

    Args:
        v1: First vector (1D array)
        v2: Second vector (1D array)

    Returns:
        Scalar dot product
    """
    return float(np.dot(v1, v2))


# ---------------------------------------------------------------------------
# Exercise 2: Vector Operations - Magnitude (Norm)
# ---------------------------------------------------------------------------
def vector_magnitude(v: np.ndarray) -> float:
    """
    Compute L2 norm (Euclidean magnitude) of a vector.

    Args:
        v: Vector (1D array)

    Returns:
        Magnitude as float
    """
    return float(np.linalg.norm(v))


# ---------------------------------------------------------------------------
# Exercise 3: Vector Normalization
# ---------------------------------------------------------------------------
def normalize_vector(v: np.ndarray) -> np.ndarray:
    """
    Normalize vector to unit length (divide by magnitude).

    Args:
        v: Vector (1D array)

    Returns:
        Unit vector with magnitude 1
    """
    magnitude = np.linalg.norm(v)
    return v / magnitude


# ---------------------------------------------------------------------------
# Exercise 4: Matrix Multiplication
# ---------------------------------------------------------------------------
def matrix_multiply(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Perform matrix multiplication A @ B without using @ operator.
    Use np.dot or explicit loop.

    Args:
        A: First matrix (m x n)
        B: Second matrix (n x p)

    Returns:
        Result matrix (m x p)
    """
    return np.dot(A, B)


# ---------------------------------------------------------------------------
# Exercise 5: Matrix Transpose and Properties
# ---------------------------------------------------------------------------
def matrix_transpose_properties(A: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute A^T and verify (A^T)^T = A.

    Args:
        A: Matrix (2D array)

    Returns:
        Tuple of (A_transpose, A_retransposed)
    """
    A_transpose = A.T
    A_retransposed = A_transpose.T

    return A_transpose, A_retransposed


# ---------------------------------------------------------------------------
# Exercise 6: Matrix Determinant
# ---------------------------------------------------------------------------
def matrix_determinant(A: np.ndarray) -> float:
    """
    Compute determinant of a square matrix using np.linalg.det.

    Args:
        A: Square matrix (n x n)

    Returns:
        Determinant as float
    """
    return float(np.linalg.det(A))


# ---------------------------------------------------------------------------
# Exercise 7: Matrix Inverse
# ---------------------------------------------------------------------------
def matrix_inverse(A: np.ndarray) -> np.ndarray:
    """
    Compute inverse of a square matrix A^(-1).

    Args:
        A: Invertible square matrix (n x n)

    Returns:
        Inverse matrix
    """
    return np.linalg.inv(A)


# ---------------------------------------------------------------------------
# Exercise 8: Numerical Derivative
# ---------------------------------------------------------------------------
def numerical_derivative(f, x: float, h: float = 1e-5) -> float:
    """
    Compute numerical derivative of function f at point x.

    Use central difference formula: f'(x) ≈ (f(x+h) - f(x-h)) / (2h)

    Args:
        f: Function taking single float and returning float
        x: Point at which to compute derivative
        h: Step size for numerical differentiation

    Returns:
        Approximate derivative as float
    """
    return (f(x + h) - f(x - h)) / (2 * h)


# ---------------------------------------------------------------------------
# Exercise 9: Gradient of Scalar Function
# ---------------------------------------------------------------------------
def compute_gradient(f, x: np.ndarray, h: float = 1e-5) -> np.ndarray:
    """
    Compute gradient (vector of partial derivatives) of function f.

    Args:
        f: Function taking array and returning scalar
        x: Point at which to compute gradient (1D array)
        h: Step size for numerical differentiation

    Returns:
        Gradient vector (same shape as x)
    """
    gradient = np.zeros_like(x)

    for i in range(len(x)):
        x_plus = x.copy()
        x_plus[i] += h

        x_minus = x.copy()
        x_minus[i] -= h

        gradient[i] = (f(x_plus) - f(x_minus)) / (2 * h)

    return gradient


# ---------------------------------------------------------------------------
# Exercise 10: Gradient Descent Optimization
# ---------------------------------------------------------------------------
def gradient_descent(f, df, x0: float, learning_rate: float, iterations: int) -> float:
    """
    Perform gradient descent optimization to minimize f(x).

    Update rule: x = x - learning_rate * df(x)

    Args:
        f: Objective function (for reference, not used in update)
        df: Gradient function (derivative of f)
        x0: Initial point
        learning_rate: Step size for each update
        iterations: Number of iterations

    Returns:
        Optimized x value after all iterations
    """
    x = x0

    for _ in range(iterations):
        gradient = df(x)
        x = x - learning_rate * gradient

    return x


# ---------------------------------------------------------------------------
# Exercise 11: Bayes' Theorem
# ---------------------------------------------------------------------------
def bayes_theorem(p_b_given_a: float, p_a: float, p_b: float) -> float:
    """
    Compute P(A|B) using Bayes' theorem.

    Formula: P(A|B) = P(B|A) * P(A) / P(B)

    Args:
        p_b_given_a: P(B|A) - probability of B given A
        p_a: P(A) - prior probability of A
        p_b: P(B) - total probability of B

    Returns:
        P(A|B) - posterior probability of A given B
    """
    return (p_b_given_a * p_a) / p_b


# ---------------------------------------------------------------------------
# Exercise 12: Conditional Probability - Medical Test
# ---------------------------------------------------------------------------
def medical_test_posterior(sensitivity: float, specificity: float, prevalence: float) -> float:
    """
    Calculate probability of disease given positive test result.

    Args:
        sensitivity: P(positive | disease) - true positive rate
        specificity: P(negative | no disease) - true negative rate
        prevalence: P(disease) - base rate of disease

    Returns:
        P(disease | positive test) - posterior probability
    """
    # P(positive | disease) = sensitivity
    p_positive_given_disease = sensitivity

    # P(positive | no disease) = 1 - specificity
    p_positive_given_no_disease = 1 - specificity

    # P(positive) by law of total probability
    p_positive = (p_positive_given_disease * prevalence +
                  p_positive_given_no_disease * (1 - prevalence))

    # P(disease | positive) by Bayes' theorem
    p_disease_given_positive = (p_positive_given_disease * prevalence) / p_positive

    return p_disease_given_positive


# ---------------------------------------------------------------------------
# Exercise 13: Normal Distribution
# ---------------------------------------------------------------------------
def normal_distribution_probability(x: float, mean: float, std: float) -> float:
    """
    Compute probability density P(X=x) for normal distribution.

    Use scipy.stats.norm.pdf

    Args:
        x: Value at which to evaluate PDF
        mean: Mean of distribution
        std: Standard deviation

    Returns:
        Probability density at x
    """
    return float(stats.norm.pdf(x, loc=mean, scale=std))


# ---------------------------------------------------------------------------
# Exercise 14: Cumulative Probability
# ---------------------------------------------------------------------------
def cumulative_normal_probability(x: float, mean: float, std: float) -> float:
    """
    Compute cumulative probability P(X <= x) for normal distribution.

    Use scipy.stats.norm.cdf

    Args:
        x: Upper bound
        mean: Mean of distribution
        std: Standard deviation

    Returns:
        Cumulative probability P(X <= x)
    """
    return float(stats.norm.cdf(x, loc=mean, scale=std))


# ---------------------------------------------------------------------------
# Exercise 15: Linear Regression - Least Squares
# ---------------------------------------------------------------------------
def least_squares_regression(X: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """
    Compute least squares solution for linear regression: y = mx + b

    Using normal equations:
    - m = (n*Σ(xy) - Σx*Σy) / (n*Σ(x²) - (Σx)²)
    - b = (Σy - m*Σx) / n

    Args:
        X: Independent variable (1D array)
        y: Dependent variable (1D array)

    Returns:
        Tuple of (slope m, intercept b)
    """
    n = len(X)
    sum_x = np.sum(X)
    sum_y = np.sum(y)
    sum_xy = np.sum(X * y)
    sum_x2 = np.sum(X ** 2)

    # Calculate slope
    m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)

    # Calculate intercept
    b = (sum_y - m * sum_x) / n

    return float(m), float(b)


# ===========================================================================
# Tests
# ===========================================================================
if __name__ == "__main__":
    print("Running Math for ML solution tests...\n")

    # Test 1: Dot product
    v1 = np.array([1, 2, 3])
    v2 = np.array([4, 5, 6])
    dot = vector_dot_product(v1, v2)
    assert dot == 32  # 1*4 + 2*5 + 3*6
    print("  [PASS] Exercise 1: Vector Dot Product")

    # Test 2: Vector magnitude
    v = np.array([3, 4])
    mag = vector_magnitude(v)
    assert np.isclose(mag, 5.0)  # sqrt(9 + 16) = 5
    print("  [PASS] Exercise 2: Vector Magnitude")

    # Test 3: Vector normalization
    v = np.array([3, 4])
    normalized = normalize_vector(v)
    assert np.isclose(np.linalg.norm(normalized), 1.0)
    assert np.allclose(normalized, np.array([0.6, 0.8]))
    print("  [PASS] Exercise 3: Vector Normalization")

    # Test 4: Matrix multiplication
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])
    C = matrix_multiply(A, B)
    expected = np.array([[19, 22], [43, 50]])
    assert np.allclose(C, expected)
    print("  [PASS] Exercise 4: Matrix Multiplication")

    # Test 5: Transpose
    A = np.array([[1, 2, 3], [4, 5, 6]])
    A_T, A_TT = matrix_transpose_properties(A)
    assert A_T.shape == (3, 2)
    assert np.allclose(A_TT, A)
    print("  [PASS] Exercise 5: Matrix Transpose")

    # Test 6: Determinant
    A = np.array([[1, 2], [3, 4]])
    det = matrix_determinant(A)
    assert np.isclose(det, -2.0)
    print("  [PASS] Exercise 6: Matrix Determinant")

    # Test 7: Matrix inverse
    A = np.array([[1, 2], [3, 4]], dtype=float)
    A_inv = matrix_inverse(A)
    identity = A @ A_inv
    assert np.allclose(identity, np.eye(2))
    print("  [PASS] Exercise 7: Matrix Inverse")

    # Test 8: Numerical derivative
    def f(x):
        return x**2
    deriv = numerical_derivative(f, 3.0)
    assert np.isclose(deriv, 6.0, atol=1e-4)  # d/dx(x^2) at x=3 = 6
    print("  [PASS] Exercise 8: Numerical Derivative")

    # Test 9: Gradient
    def f_2d(x):
        return x[0]**2 + 2*x[1]**2
    grad = compute_gradient(f_2d, np.array([1.0, 2.0]))
    expected_grad = np.array([2.0, 8.0])  # [2*x[0], 4*x[1]]
    assert np.allclose(grad, expected_grad, atol=1e-4)
    print("  [PASS] Exercise 9: Gradient")

    # Test 10: Gradient descent
    def f_minimize(x):
        return x**2
    def df_minimize(x):
        return 2*x
    result = gradient_descent(f_minimize, df_minimize, x0=5.0,
                            learning_rate=0.1, iterations=100)
    assert np.isclose(result, 0.0, atol=0.1)
    print("  [PASS] Exercise 10: Gradient Descent")

    # Test 11: Bayes' theorem
    posterior = bayes_theorem(p_b_given_a=0.99, p_a=0.01, p_b=0.052)
    assert np.isclose(posterior, 0.19, atol=0.01)
    print("  [PASS] Exercise 11: Bayes' Theorem")

    # Test 12: Medical test
    post_prob = medical_test_posterior(sensitivity=0.99, specificity=0.95,
                                       prevalence=0.01)
    assert 0.15 < post_prob < 0.20
    print("  [PASS] Exercise 12: Medical Test Posterior")

    # Test 13: Normal distribution PDF
    pdf_val = normal_distribution_probability(x=0, mean=0, std=1)
    assert np.isclose(pdf_val, 1/np.sqrt(2*np.pi), atol=1e-5)
    print("  [PASS] Exercise 13: Normal Distribution PDF")

    # Test 14: Cumulative probability
    cdf_val = cumulative_normal_probability(x=0, mean=0, std=1)
    assert np.isclose(cdf_val, 0.5, atol=1e-5)
    print("  [PASS] Exercise 14: Cumulative Probability")

    # Test 15: Linear regression
    X = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 4, 6, 8, 10])  # y = 2x
    m, b = least_squares_regression(X, y)
    assert np.isclose(m, 2.0, atol=1e-10)
    assert np.isclose(b, 0.0, atol=1e-10)
    print("  [PASS] Exercise 15: Least Squares Regression")

    print("\nAll 15 solutions passed!")
