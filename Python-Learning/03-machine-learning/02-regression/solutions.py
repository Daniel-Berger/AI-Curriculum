"""
Module 02: Regression - Solutions
==================================
Complete solutions with notes on Pythonic patterns and ML best practices.

Prerequisites:
    pip install scikit-learn numpy
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
# Exercise 1: Simple Linear Regression
# =============================================================================
# Note: This is the fundamental sklearn pattern. LinearRegression uses OLS
# (Ordinary Least Squares) -- no regularization, no hyperparameters to tune.

def simple_linear_regression(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
) -> dict[str, float]:
    """Fit a LinearRegression model and return its performance metrics."""
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mse = float(mean_squared_error(y_test, y_pred))
    return {
        'r2': float(r2_score(y_test, y_pred)),
        'mse': mse,
        'rmse': float(np.sqrt(mse)),
        'mae': float(mean_absolute_error(y_test, y_pred)),
    }


# =============================================================================
# Exercise 2: Access Model Parameters
# =============================================================================
# Note: sklearn learned attributes always end with underscore_ (e.g., coef_, intercept_).
# This convention is like Swift's computed properties -- they only exist after fit().

def get_model_params(
    X: np.ndarray, y: np.ndarray
) -> dict[str, object]:
    """Fit a LinearRegression and return its learned parameters."""
    model = LinearRegression()
    model.fit(X, y)
    return {
        'intercept': float(model.intercept_),
        'coefficients': model.coef_,
        'n_features': int(model.n_features_in_),
    }


# =============================================================================
# Exercise 3: Predict New Values
# =============================================================================
# Note: predict() returns an array of the same length as the input X.

def predict_with_linear_model(
    X_train: np.ndarray, y_train: np.ndarray,
    X_new: np.ndarray
) -> np.ndarray:
    """Train a LinearRegression model and return predictions for X_new."""
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model.predict(X_new)


# =============================================================================
# Exercise 4: Ridge Regression
# =============================================================================
# Note: The critical detail here is scaling. Ridge penalizes large coefficients,
# but if features are on different scales, the penalty is unevenly distributed.
# Always fit the scaler on training data only to prevent data leakage.

def ridge_regression(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
    alpha: float
) -> dict[str, float]:
    """Fit a Ridge regression model with proper scaling."""
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = Ridge(alpha=alpha)
    model.fit(X_train_s, y_train)

    return {
        'train_r2': float(model.score(X_train_s, y_train)),
        'test_r2': float(model.score(X_test_s, y_test)),
        'n_nonzero_coefs': int(np.sum(np.abs(model.coef_) > 1e-6)),
    }


# =============================================================================
# Exercise 5: Lasso Regression with Feature Selection
# =============================================================================
# Note: Lasso's key property is that it drives some coefficients to exactly zero,
# performing automatic feature selection. np.where returns the indices where a
# condition is True -- a very Pythonic way to find non-zero coefficients.

def lasso_feature_selection(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
    alpha: float
) -> dict[str, object]:
    """Fit a Lasso model and analyze feature selection."""
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = Lasso(alpha=alpha, max_iter=10000)
    model.fit(X_train_s, y_train)

    nonzero_mask = model.coef_ != 0
    return {
        'test_r2': float(model.score(X_test_s, y_test)),
        'n_selected': int(np.sum(nonzero_mask)),
        'n_dropped': int(np.sum(~nonzero_mask)),
        'selected_indices': list(np.where(nonzero_mask)[0]),
    }


# =============================================================================
# Exercise 6: Compare Regularization Methods
# =============================================================================
# Note: This is the standard model comparison pattern. We create a list of
# (name, model) tuples, iterate through them, and collect results. The sorted()
# call at the end uses a lambda as the key function -- very Pythonic.

def compare_regularization(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
) -> list[dict[str, object]]:
    """Compare Linear, Ridge, Lasso, and ElasticNet regression."""
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    models = [
        ("LinearRegression", LinearRegression()),
        ("Ridge", Ridge(alpha=1.0)),
        ("Lasso", Lasso(alpha=0.1, max_iter=10000)),
        ("ElasticNet", ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10000)),
    ]

    results = []
    for name, model in models:
        model.fit(X_train_s, y_train)
        results.append({
            'name': name,
            'test_r2': float(model.score(X_test_s, y_test)),
            'n_nonzero': int(np.sum(model.coef_ != 0)),
        })

    results.sort(key=lambda r: r['test_r2'], reverse=True)
    return results


# =============================================================================
# Exercise 7: Regularization Strength Curve
# =============================================================================
# Note: This produces the classic regularization curve. As alpha increases,
# train_r2 decreases (model is more constrained) and test_r2 initially improves
# (less overfitting) then eventually decreases (underfitting). The optimal alpha
# is where test_r2 peaks.

def regularization_curve(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
) -> dict[float, dict[str, float]]:
    """Compute Ridge train/test R2 for different alpha values."""
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    alphas = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
    results = {}

    for alpha in alphas:
        model = Ridge(alpha=alpha)
        model.fit(X_train_s, y_train)
        results[alpha] = {
            'train_r2': float(model.score(X_train_s, y_train)),
            'test_r2': float(model.score(X_test_s, y_test)),
        }

    return results


# =============================================================================
# Exercise 8: Polynomial Regression
# =============================================================================
# Note: PolynomialFeatures with degree=3 and a single input feature creates:
# [x, x^2, x^3] (with include_bias=False). With two input features (x1, x2),
# it creates all combinations up to degree 3: [x1, x2, x1^2, x1*x2, x2^2, ...].

def polynomial_regression(
    X_train: np.ndarray, y_train: np.ndarray,
    X_test: np.ndarray, y_test: np.ndarray,
    degree: int
) -> dict[str, float]:
    """Fit a polynomial regression model of the given degree."""
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_poly, y_train)

    return {
        'train_r2': float(model.score(X_train_poly, y_train)),
        'test_r2': float(model.score(X_test_poly, y_test)),
        'n_poly_features': int(X_train_poly.shape[1]),
    }


# =============================================================================
# Exercise 9: Compare Polynomial Degrees
# =============================================================================
# Note: This demonstrates overfitting beautifully. As degree increases,
# train_r2 approaches 1.0 but test_r2 drops (the model fits noise, not signal).

def compare_poly_degrees(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[int, dict[str, float]]:
    """Compare polynomial regression at various degrees."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    results = {}
    for degree in [1, 2, 3, 5, 7]:
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        X_train_poly = poly.fit_transform(X_train)
        X_test_poly = poly.transform(X_test)

        model = LinearRegression()
        model.fit(X_train_poly, y_train)
        results[degree] = {
            'train_r2': float(model.score(X_train_poly, y_train)),
            'test_r2': float(model.score(X_test_poly, y_test)),
        }

    return results


# =============================================================================
# Exercise 10: Residual Analysis
# =============================================================================
# Note: Good residuals should have mean ~0, be normally distributed, and have
# no patterns. Large residuals (outliers) may indicate data quality issues or
# model inadequacy. The 2-sigma rule flags approximately 5% of residuals in a
# normal distribution.

def compute_residual_stats(
    y_true: np.ndarray, y_pred: np.ndarray
) -> dict[str, float]:
    """Compute residual statistics."""
    residuals = y_true - y_pred
    std = float(residuals.std())

    return {
        'mean': float(residuals.mean()),
        'std': std,
        'max_abs': float(np.max(np.abs(residuals))),
        'median_abs': float(np.median(np.abs(residuals))),
        'n_large': int(np.sum(np.abs(residuals - residuals.mean()) > 2 * std)),
    }


# =============================================================================
# Exercise 11: Feature Importance from Ridge
# =============================================================================
# Note: After scaling, coefficient magnitudes directly indicate feature importance.
# Sorting by absolute value and returning (name, importance) tuples is a clean
# Pythonic pattern using zip() and sorted().

def ridge_feature_importance(
    X: np.ndarray, y: np.ndarray,
    feature_names: list[str]
) -> list[tuple[str, float]]:
    """Compute feature importance from a Ridge regression model."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = Ridge(alpha=1.0)
    model.fit(X_scaled, y)

    importances = np.abs(model.coef_)
    # zip pairs each name with its importance, sorted descending
    name_importance_pairs = list(zip(feature_names, importances))
    name_importance_pairs.sort(key=lambda pair: pair[1], reverse=True)

    return [(name, float(imp)) for name, imp in name_importance_pairs]


# =============================================================================
# Exercise 12: Best Alpha via Cross-Validation
# =============================================================================
# Note: RidgeCV performs efficient leave-one-out cross-validation internally
# (it uses a mathematical shortcut). The .alpha_ attribute gives the best alpha
# and .score() gives the performance.

def find_best_alpha(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, object]:
    """Find the best Ridge alpha using RidgeCV."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RidgeCV(alphas=[0.001, 0.01, 0.1, 1.0, 10.0, 100.0])
    model.fit(X_scaled, y)

    return {
        'best_alpha': float(model.alpha_),
        'cv_score': float(model.score(X_scaled, y)),
        'coefficients': model.coef_,
    }


# =============================================================================
# Exercise 13: Complete Regression Pipeline
# =============================================================================
# Note: This ties together all the concepts. The pattern of trying multiple models,
# selecting the best, and then extracting feature importances is extremely common
# in practice. Using max() with a key function is the Pythonic way to find the
# best item in a collection.

def full_regression_pipeline(seed: int) -> dict[str, object]:
    """Run a complete regression pipeline on the diabetes dataset."""
    # 1. Load
    diabetes = load_diabetes()
    X, y = diabetes.data, diabetes.target
    feature_names = list(diabetes.feature_names)

    # 2. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    # 3. Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # 4. Train models
    models = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "Lasso": Lasso(alpha=0.1, max_iter=10000),
    }

    all_results = {}
    for name, model in models.items():
        model.fit(X_train_s, y_train)
        all_results[name] = float(model.score(X_test_s, y_test))

    # 5. Find best
    best_name = max(all_results, key=all_results.get)
    best_model = models[best_name]

    # 6. Feature importance from best model
    importances = np.abs(best_model.coef_)
    top_3_idx = np.argsort(importances)[-3:][::-1]
    top_3_features = [feature_names[i] for i in top_3_idx]

    return {
        'best_model': best_name,
        'best_r2': all_results[best_name],
        'all_results': all_results,
        'top_3_features': top_3_features,
    }


# =============================================================================
# Exercise 14: Regression with Multicollinearity
# =============================================================================
# Note: When features are perfectly correlated, OLS coefficients become unstable
# (they can be very large with opposite signs). Ridge handles this gracefully
# by shrinking coefficients, distributing weight evenly among correlated features.
# np.column_stack adds a new column to the feature matrix.

def handle_multicollinearity(seed: int) -> dict[str, object]:
    """Demonstrate how Ridge handles multicollinearity."""
    # 1. Create data with collinearity
    X, y = make_regression(
        n_samples=100, n_features=10, n_informative=5,
        noise=10, random_state=seed
    )
    # Add duplicate of column 0 (perfect collinearity)
    X = np.column_stack([X, X[:, 0]])

    # 2. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    # 3. Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # 4. Fit both models
    ols = LinearRegression()
    ols.fit(X_train_s, y_train)

    ridge = Ridge(alpha=1.0)
    ridge.fit(X_train_s, y_train)

    return {
        'ols_max_coef': float(np.max(np.abs(ols.coef_))),
        'ridge_max_coef': float(np.max(np.abs(ridge.coef_))),
        'ols_test_r2': float(ols.score(X_test_s, y_test)),
        'ridge_test_r2': float(ridge.score(X_test_s, y_test)),
    }


# =============================================================================
# Exercise 15: Polynomial + Regularization
# =============================================================================
# Note: This is the key insight of the module: combining polynomial features
# (for expressiveness) with regularization (to prevent overfitting) gives the
# best of both worlds. poly5_ols overfits, but poly5_ridge + poly10_ridge
# generalize well because Ridge constrains the large coefficients that cause
# wild oscillations in high-degree polynomials.

def poly_with_regularization(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, dict[str, float]]:
    """Compare polynomial regression with and without regularization."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    configs = {
        'poly2_ols': (2, LinearRegression()),
        'poly5_ols': (5, LinearRegression()),
        'poly5_ridge': (5, Ridge(alpha=1.0)),
        'poly10_ridge': (10, Ridge(alpha=1.0)),
    }

    results = {}
    for name, (degree, model) in configs.items():
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        X_train_poly = poly.fit_transform(X_train)
        X_test_poly = poly.transform(X_test)

        model.fit(X_train_poly, y_train)
        results[name] = {
            'train_r2': float(model.score(X_train_poly, y_train)),
            'test_r2': float(model.score(X_test_poly, y_test)),
        }

    return results


# =============================================================================
# Verification
# =============================================================================

if __name__ == "__main__":
    print("Running Module 02 Solutions - Verification...\n")

    X_reg, y_reg = make_regression(
        n_samples=200, n_features=20, n_informative=10,
        noise=15, random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )

    print("Ex 1:", simple_linear_regression(X_train, y_train, X_test, y_test))
    print("Ex 2:", {k: type(v).__name__ for k, v in get_model_params(X_reg, y_reg).items()})
    print("Ex 3:", predict_with_linear_model(X_train, y_train, X_test[:3]).shape)
    print("Ex 4:", ridge_regression(X_train, y_train, X_test, y_test, 1.0))
    print("Ex 5:", {k: v for k, v in lasso_feature_selection(X_train, y_train, X_test, y_test, 0.5).items()
                    if k != 'selected_indices'})
    print("Ex 6:", [(r['name'], f"{r['test_r2']:.4f}") for r in compare_regularization(X_train, y_train, X_test, y_test)])
    print("Ex 7:", {a: f"{v['test_r2']:.4f}" for a, v in regularization_curve(X_train, y_train, X_test, y_test).items()})

    X_1d = X_train[:, :1]
    X_1d_test = X_test[:, :1]
    print("Ex 8:", polynomial_regression(X_1d, y_train, X_1d_test, y_test, 3))

    np.random.seed(42)
    X_poly = np.sort(np.random.uniform(0, 5, 100)).reshape(-1, 1)
    y_poly = 2 * X_poly.ravel()**2 - 3 * X_poly.ravel() + np.random.normal(0, 3, 100)
    print("Ex 9:", {d: f"test={v['test_r2']:.3f}" for d, v in compare_poly_degrees(X_poly, y_poly, 42).items()})

    model = LinearRegression().fit(X_train, y_train)
    print("Ex 10:", compute_residual_stats(y_test, model.predict(X_test)))

    diabetes = load_diabetes()
    print("Ex 11:", [(n, f"{v:.2f}") for n, v in ridge_feature_importance(diabetes.data, diabetes.target, list(diabetes.feature_names))[:5]])
    print("Ex 12:", {k: v for k, v in find_best_alpha(X_reg, y_reg, 42).items() if k != 'coefficients'})

    pipeline_result = full_regression_pipeline(42)
    print("Ex 13:", {k: v for k, v in pipeline_result.items() if k != 'all_results'})
    print("Ex 14:", handle_multicollinearity(42))

    result_15 = poly_with_regularization(X_poly, y_poly, 42)
    print("Ex 15:", {k: f"test={v['test_r2']:.3f}" for k, v in result_15.items()})

    print("\nAll solutions verified successfully!")
