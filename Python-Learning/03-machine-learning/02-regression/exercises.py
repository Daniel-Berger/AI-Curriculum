"""
Module 02: Regression - Exercises
==================================
Target audience: Swift developers learning Python ML.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.

Prerequisites:
    pip install scikit-learn numpy

Difficulty levels:
  Easy   - Direct application of sklearn regression API
  Medium - Requires understanding regularization or metrics
  Hard   - Combines multiple concepts or requires analysis
"""

import numpy as np
from sklearn.datasets import make_regression, load_diabetes
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
    ElasticNet,
    RidgeCV,
)
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.pipeline import make_pipeline


# =============================================================================
# WARM-UP: Linear Regression Basics
# =============================================================================

# Exercise 1: Simple Linear Regression
# Difficulty: Easy
def simple_linear_regression(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
) -> dict[str, float]:
    """Fit a LinearRegression model and return its performance metrics.

    Returns:
        Dict with keys: 'r2', 'mse', 'rmse', 'mae'
    """
    pass


# Exercise 2: Access Model Parameters
# Difficulty: Easy
def get_model_params(
    X: np.ndarray, y: np.ndarray
) -> dict[str, object]:
    """Fit a LinearRegression and return its learned parameters.

    Returns:
        Dict with keys:
        - 'intercept': float (the bias term)
        - 'coefficients': np.ndarray (the feature weights)
        - 'n_features': int (number of features the model was trained on)
    """
    pass


# Exercise 3: Predict New Values
# Difficulty: Easy
def predict_with_linear_model(
    X_train: np.ndarray, y_train: np.ndarray,
    X_new: np.ndarray
) -> np.ndarray:
    """Train a LinearRegression model and return predictions for X_new.

    Returns:
        Predictions array of shape (n_samples,)
    """
    pass


# =============================================================================
# CORE: Regularization
# =============================================================================

# Exercise 4: Ridge Regression
# Difficulty: Medium
def ridge_regression(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
    alpha: float
) -> dict[str, float]:
    """Fit a Ridge regression model with the given alpha.

    IMPORTANT: Scale the data first using StandardScaler.
    Fit the scaler on training data only.

    Returns:
        Dict with keys: 'train_r2', 'test_r2', 'n_nonzero_coefs'
        where n_nonzero_coefs counts coefficients with |coef| > 1e-6
    """
    pass


# Exercise 5: Lasso Regression with Feature Selection
# Difficulty: Medium
def lasso_feature_selection(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
    alpha: float
) -> dict[str, object]:
    """Fit a Lasso regression model and analyze which features were selected.

    Scale data first. Use max_iter=10000 for Lasso.

    Returns:
        Dict with keys:
        - 'test_r2': float
        - 'n_selected': int (number of non-zero coefficients)
        - 'n_dropped': int (number of zero coefficients)
        - 'selected_indices': list[int] (indices of non-zero coefficients)
    """
    pass


# Exercise 6: Compare Regularization Methods
# Difficulty: Medium
def compare_regularization(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
) -> list[dict[str, object]]:
    """Compare Linear, Ridge, Lasso, and ElasticNet regression.

    Scale data first. Use these settings:
    - LinearRegression()
    - Ridge(alpha=1.0)
    - Lasso(alpha=0.1, max_iter=10000)
    - ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10000)

    Returns:
        List of dicts sorted by test_r2 descending:
        [{'name': str, 'test_r2': float, 'n_nonzero': int}, ...]
    """
    pass


# Exercise 7: Regularization Strength Curve
# Difficulty: Medium
def regularization_curve(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
) -> dict[float, dict[str, float]]:
    """Compute Ridge train/test R2 for different alpha values.

    Scale data first.
    Test alphas: [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]

    Returns:
        {alpha: {'train_r2': float, 'test_r2': float}, ...}
    """
    pass


# =============================================================================
# INTERMEDIATE: Polynomial Regression and Metrics
# =============================================================================

# Exercise 8: Polynomial Regression
# Difficulty: Medium
def polynomial_regression(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
    degree: int
) -> dict[str, float]:
    """Fit a polynomial regression model of the given degree.

    Use PolynomialFeatures(degree=degree, include_bias=False) to transform features,
    then fit LinearRegression on the transformed data.

    Returns:
        Dict with keys: 'train_r2', 'test_r2', 'n_poly_features'
        where n_poly_features is the number of features after polynomial transformation.
    """
    pass


# Exercise 9: Compare Polynomial Degrees
# Difficulty: Medium
def compare_poly_degrees(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[int, dict[str, float]]:
    """Compare polynomial regression at degrees 1, 2, 3, 5, 7.

    Split data 80/20 with random_state=seed.
    For each degree, compute train_r2 and test_r2.

    Returns:
        {degree: {'train_r2': float, 'test_r2': float}, ...}

    You should observe overfitting at high degrees.
    """
    pass


# Exercise 10: Residual Analysis
# Difficulty: Medium
def compute_residual_stats(
    y_true: np.ndarray, y_pred: np.ndarray
) -> dict[str, float]:
    """Compute residual statistics.

    Returns:
        Dict with keys:
        - 'mean': mean of residuals (should be close to 0)
        - 'std': standard deviation of residuals
        - 'max_abs': maximum absolute residual
        - 'median_abs': median absolute residual
        - 'n_large': number of residuals > 2 standard deviations from mean
    """
    pass


# =============================================================================
# ADVANCED: Feature Importance and Model Selection
# =============================================================================

# Exercise 11: Feature Importance from Ridge
# Difficulty: Hard
def ridge_feature_importance(
    X: np.ndarray, y: np.ndarray,
    feature_names: list[str]
) -> list[tuple[str, float]]:
    """Compute feature importance from a Ridge regression model.

    Steps:
    1. Scale features with StandardScaler
    2. Fit Ridge(alpha=1.0)
    3. Feature importance = absolute value of coefficients

    Returns:
        List of (feature_name, importance) tuples sorted by importance descending.
    """
    pass


# Exercise 12: Best Alpha via Cross-Validation
# Difficulty: Hard
def find_best_alpha(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, object]:
    """Find the best Ridge alpha using RidgeCV.

    Scale data first using StandardScaler.
    Use RidgeCV with alphas=[0.001, 0.01, 0.1, 1.0, 10.0, 100.0].

    Returns:
        {
            'best_alpha': float,
            'cv_score': float (R2 on the full dataset after fit),
            'coefficients': np.ndarray
        }
    """
    pass


# Exercise 13: Complete Regression Pipeline
# Difficulty: Hard
def full_regression_pipeline(seed: int) -> dict[str, object]:
    """Run a complete regression pipeline on the diabetes dataset.

    Steps:
    1. Load diabetes dataset
    2. Split 80/20 (random_state=seed)
    3. Scale features
    4. Train LinearRegression, Ridge(1.0), Lasso(0.1, max_iter=10000)
    5. Find best model by test R2
    6. Get feature importances from the best model

    Returns:
        {
            'best_model': str (name of the best model),
            'best_r2': float (test R2 of the best model),
            'all_results': dict mapping model name to test R2,
            'top_3_features': list of top 3 feature names by importance (from best model)
        }
    """
    pass


# Exercise 14: Regression with Multicollinearity
# Difficulty: Hard
def handle_multicollinearity(seed: int) -> dict[str, object]:
    """Demonstrate how Ridge handles multicollinearity better than OLS.

    Steps:
    1. Create data with correlated features:
       X, y = make_regression(n_samples=100, n_features=10, n_informative=5,
                              noise=10, random_state=seed)
       Add a duplicate of column 0 as a new column (creates perfect collinearity).
    2. Split 80/20 (random_state=seed)
    3. Scale
    4. Fit LinearRegression and Ridge(alpha=1.0)
    5. Compare coefficient magnitudes

    Returns:
        {
            'ols_max_coef': float (max absolute coefficient of LinearRegression),
            'ridge_max_coef': float (max absolute coefficient of Ridge),
            'ols_test_r2': float,
            'ridge_test_r2': float,
        }

    Ridge should have smaller max coefficient (more stable).
    """
    pass


# Exercise 15: Polynomial + Regularization
# Difficulty: Hard
def poly_with_regularization(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, dict[str, float]]:
    """Compare polynomial regression with and without regularization.

    Data: single feature (X shape: (n, 1))
    Split 80/20 with random_state=seed.

    Create 4 models:
    - 'poly2_ols': PolynomialFeatures(2) + LinearRegression
    - 'poly5_ols': PolynomialFeatures(5) + LinearRegression
    - 'poly5_ridge': PolynomialFeatures(5) + Ridge(alpha=1.0)
    - 'poly10_ridge': PolynomialFeatures(10) + Ridge(alpha=1.0)

    For polynomial features use include_bias=False.

    Returns:
        {
            'poly2_ols': {'train_r2': float, 'test_r2': float},
            'poly5_ols': {'train_r2': float, 'test_r2': float},
            'poly5_ridge': {'train_r2': float, 'test_r2': float},
            'poly10_ridge': {'train_r2': float, 'test_r2': float},
        }

    poly5_ridge should generalize better than poly5_ols (less overfitting).
    """
    pass


# =============================================================================
# Self-Test Runner
# =============================================================================

if __name__ == "__main__":
    print("Running Module 02: Regression Exercises...\n")
    errors = 0

    # Setup shared data
    X_reg, y_reg = make_regression(
        n_samples=200, n_features=20, n_informative=10,
        noise=15, random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )

    # Exercise 1
    try:
        result = simple_linear_regression(X_train, y_train, X_test, y_test)
        assert all(k in result for k in ['r2', 'mse', 'rmse', 'mae'])
        assert result['rmse'] == np.sqrt(result['mse']), "RMSE should be sqrt(MSE)"
        assert 0 < result['r2'] <= 1.0
        print("  Exercise  1 (simple_linear_regression):   PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  1 (simple_linear_regression):   FAIL - {e}")
        errors += 1

    # Exercise 2
    try:
        result = get_model_params(X_reg, y_reg)
        assert 'intercept' in result and 'coefficients' in result and 'n_features' in result
        assert isinstance(result['intercept'], float)
        assert len(result['coefficients']) == 20
        assert result['n_features'] == 20
        print("  Exercise  2 (get_model_params):            PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  2 (get_model_params):            FAIL - {e}")
        errors += 1

    # Exercise 3
    try:
        X_new = np.random.RandomState(0).randn(5, 20)
        preds = predict_with_linear_model(X_train, y_train, X_new)
        assert preds.shape == (5,)
        print("  Exercise  3 (predict_with_linear_model):   PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  3 (predict_with_linear_model):   FAIL - {e}")
        errors += 1

    # Exercise 4
    try:
        result = ridge_regression(X_train, y_train, X_test, y_test, alpha=1.0)
        assert 'train_r2' in result and 'test_r2' in result and 'n_nonzero_coefs' in result
        assert 0 < result['test_r2'] <= 1.0
        print("  Exercise  4 (ridge_regression):            PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  4 (ridge_regression):            FAIL - {e}")
        errors += 1

    # Exercise 5
    try:
        result = lasso_feature_selection(X_train, y_train, X_test, y_test, alpha=0.5)
        assert 'test_r2' in result and 'n_selected' in result and 'n_dropped' in result
        assert result['n_selected'] + result['n_dropped'] == 20
        assert isinstance(result['selected_indices'], list)
        print("  Exercise  5 (lasso_feature_selection):     PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  5 (lasso_feature_selection):     FAIL - {e}")
        errors += 1

    # Exercise 6
    try:
        result = compare_regularization(X_train, y_train, X_test, y_test)
        assert len(result) == 4
        assert all('name' in r and 'test_r2' in r and 'n_nonzero' in r for r in result)
        assert result[0]['test_r2'] >= result[-1]['test_r2'], "Should be sorted descending"
        print("  Exercise  6 (compare_regularization):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  6 (compare_regularization):      FAIL - {e}")
        errors += 1

    # Exercise 7
    try:
        result = regularization_curve(X_train, y_train, X_test, y_test)
        assert len(result) == 7
        assert all(isinstance(v, dict) for v in result.values())
        assert 0.001 in result and 1000.0 in result
        print("  Exercise  7 (regularization_curve):        PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  7 (regularization_curve):        FAIL - {e}")
        errors += 1

    # Exercise 8
    try:
        # Single feature for polynomial regression
        X_1d = X_train[:, :1]
        X_1d_test = X_test[:, :1]
        result = polynomial_regression(X_1d, y_train, X_1d_test, y_test, degree=3)
        assert 'train_r2' in result and 'test_r2' in result and 'n_poly_features' in result
        assert result['n_poly_features'] == 3  # x, x^2, x^3
        print("  Exercise  8 (polynomial_regression):       PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  8 (polynomial_regression):       FAIL - {e}")
        errors += 1

    # Exercise 9
    try:
        np.random.seed(42)
        X_1d_all = np.sort(np.random.uniform(0, 5, 100)).reshape(-1, 1)
        y_1d = 2 * X_1d_all.ravel()**2 - 3 * X_1d_all.ravel() + np.random.normal(0, 3, 100)
        result = compare_poly_degrees(X_1d_all, y_1d, 42)
        assert all(d in result for d in [1, 2, 3, 5, 7])
        print("  Exercise  9 (compare_poly_degrees):        PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  9 (compare_poly_degrees):        FAIL - {e}")
        errors += 1

    # Exercise 10
    try:
        model = LinearRegression().fit(X_train, y_train)
        y_pred = model.predict(X_test)
        result = compute_residual_stats(y_test, y_pred)
        assert all(k in result for k in ['mean', 'std', 'max_abs', 'median_abs', 'n_large'])
        assert abs(result['mean']) < 10, "Mean residual should be close to 0"
        print("  Exercise 10 (compute_residual_stats):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 10 (compute_residual_stats):      FAIL - {e}")
        errors += 1

    # Exercise 11
    try:
        diabetes = load_diabetes()
        result = ridge_feature_importance(diabetes.data, diabetes.target, list(diabetes.feature_names))
        assert len(result) == 10
        assert all(isinstance(t, tuple) and len(t) == 2 for t in result)
        # Should be sorted descending by importance
        assert result[0][1] >= result[-1][1]
        print("  Exercise 11 (ridge_feature_importance):    PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 11 (ridge_feature_importance):    FAIL - {e}")
        errors += 1

    # Exercise 12
    try:
        result = find_best_alpha(X_reg, y_reg, 42)
        assert 'best_alpha' in result and 'cv_score' in result and 'coefficients' in result
        assert result['best_alpha'] in [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
        print("  Exercise 12 (find_best_alpha):             PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 12 (find_best_alpha):             FAIL - {e}")
        errors += 1

    # Exercise 13
    try:
        result = full_regression_pipeline(42)
        assert 'best_model' in result and 'best_r2' in result
        assert 'all_results' in result and 'top_3_features' in result
        assert len(result['all_results']) == 3
        assert len(result['top_3_features']) == 3
        print("  Exercise 13 (full_regression_pipeline):    PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 13 (full_regression_pipeline):    FAIL - {e}")
        errors += 1

    # Exercise 14
    try:
        result = handle_multicollinearity(42)
        assert all(k in result for k in ['ols_max_coef', 'ridge_max_coef',
                                          'ols_test_r2', 'ridge_test_r2'])
        assert result['ridge_max_coef'] < result['ols_max_coef'], \
            "Ridge should have smaller max coefficient"
        print("  Exercise 14 (handle_multicollinearity):    PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 14 (handle_multicollinearity):    FAIL - {e}")
        errors += 1

    # Exercise 15
    try:
        np.random.seed(42)
        X_poly = np.sort(np.random.uniform(0, 5, 100)).reshape(-1, 1)
        y_poly = 2 * X_poly.ravel()**2 - 3 * X_poly.ravel() + np.random.normal(0, 3, 100)
        result = poly_with_regularization(X_poly, y_poly, 42)
        assert all(k in result for k in ['poly2_ols', 'poly5_ols', 'poly5_ridge', 'poly10_ridge'])
        for key in result:
            assert 'train_r2' in result[key] and 'test_r2' in result[key]
        print("  Exercise 15 (poly_with_regularization):    PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 15 (poly_with_regularization):    FAIL - {e}")
        errors += 1

    print(f"\n{'='*55}")
    if errors == 0:
        print("All exercises passed!")
    else:
        print(f"{errors} exercise(s) need attention.")
    print(f"{'='*55}")
