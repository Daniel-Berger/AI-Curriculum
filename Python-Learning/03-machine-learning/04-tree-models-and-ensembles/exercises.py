"""
Module 04: Tree Models and Ensemble Methods - Exercises
=========================================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- If no AssertionError is raised, your solution is correct.

Difficulty levels:
  Easy   - Direct use of a single model
  Medium - Requires comparison or parameter tuning
  Hard   - Requires complex analysis or custom implementation
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.datasets import load_iris, make_classification
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False


# =============================================================================
# DECISION TREES
# =============================================================================

# Exercise 1: Train Basic Decision Tree
# Difficulty: Easy
def train_decision_tree(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[DecisionTreeClassifier, float]:
    """Train a DecisionTreeClassifier and return model and test accuracy.

    Use DecisionTreeClassifier(random_state=42).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Tuple of (trained_model, test_accuracy).

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> model, acc = train_decision_tree(X_tr, X_te, y_tr, y_te)
    >>> isinstance(model, DecisionTreeClassifier)
    True
    >>> acc > 0.6
    True
    """
    pass


# Exercise 2: Compare Gini vs Entropy
# Difficulty: Medium
def compare_gini_entropy(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """Train DecisionTree with 'gini' and 'entropy' criteria.

    Return dict with keys 'gini' and 'entropy' and test accuracies as values.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Dict with 'gini' and 'entropy' keys mapping to accuracies.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> results = compare_gini_entropy(X_tr, X_te, y_tr, y_te)
    >>> all(k in results for k in ['gini', 'entropy'])
    True
    """
    pass


# Exercise 3: Tree Depth Effect
# Difficulty: Medium
def tree_depth_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[int, float]:
    """Train DecisionTree with max_depth=[2, 5, 10, None].

    Return dict with depth as keys and test accuracies as values.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Dict mapping max_depth to test accuracies.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> results = tree_depth_comparison(X_tr, X_te, y_tr, y_te)
    >>> len(results) == 4
    True
    """
    pass


# Exercise 4: Feature Importance
# Difficulty: Easy
def decision_tree_feature_importance(
    X_train: np.ndarray, y_train: np.ndarray
) -> np.ndarray:
    """Train DecisionTree and return feature importances.

    Use DecisionTreeClassifier(random_state=42).

    Args:
        X_train: Feature matrix.
        y_train: Target array.

    Returns:
        Array of feature importances (sum to 1.0).

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> importance = decision_tree_feature_importance(X, y)
    >>> importance.shape == (5,)
    True
    >>> np.isclose(importance.sum(), 1.0)
    True
    """
    pass


# =============================================================================
# RANDOM FORESTS
# =============================================================================

# Exercise 5: Train Random Forest
# Difficulty: Easy
def train_random_forest(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[RandomForestClassifier, float]:
    """Train RandomForestClassifier and return model and test accuracy.

    Use RandomForestClassifier(n_estimators=100, random_state=42).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Tuple of (trained_model, test_accuracy).

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> model, acc = train_random_forest(X_tr, X_te, y_tr, y_te)
    >>> isinstance(model, RandomForestClassifier)
    True
    >>> acc > 0.6
    True
    """
    pass


# Exercise 6: N-Estimators Effect
# Difficulty: Medium
def forest_n_estimators_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[int, float]:
    """Train RandomForest with n_estimators=[10, 50, 100, 200].

    Return dict with n_estimators as keys and test accuracies as values.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Dict mapping n_estimators to accuracies.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> results = forest_n_estimators_comparison(X_tr, X_te, y_tr, y_te)
    >>> all(k in results for k in [10, 50, 100, 200])
    True
    """
    pass


# Exercise 7: Out-of-Bag Score
# Difficulty: Medium
def random_forest_oob_score(
    X_train: np.ndarray, y_train: np.ndarray
) -> Tuple[RandomForestClassifier, float]:
    """Train RandomForest with OOB scoring enabled.

    Use RandomForestClassifier(n_estimators=100, oob_score=True, random_state=42).
    Return model and OOB score.

    Args:
        X_train: Training features.
        y_train: Training target.

    Returns:
        Tuple of (trained_model, oob_score).

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> model, oob = random_forest_oob_score(X, y)
    >>> isinstance(model, RandomForestClassifier)
    True
    >>> 0 <= oob <= 1
    True
    """
    pass


# Exercise 8: Random Forest Feature Importance
# Difficulty: Easy
def random_forest_feature_importance(
    X_train: np.ndarray, y_train: np.ndarray
) -> np.ndarray:
    """Train RandomForest and return feature importances.

    Use RandomForestClassifier(n_estimators=100, random_state=42).

    Args:
        X_train: Feature matrix.
        y_train: Target array.

    Returns:
        Array of feature importances.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> importance = random_forest_feature_importance(X, y)
    >>> importance.shape == (5,)
    True
    """
    pass


# =============================================================================
# GRADIENT BOOSTING
# =============================================================================

# Exercise 9: Train Gradient Boosting
# Difficulty: Easy
def train_gradient_boosting(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[GradientBoostingClassifier, float]:
    """Train GradientBoostingClassifier and return model and test accuracy.

    Use GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Tuple of (trained_model, test_accuracy).

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> model, acc = train_gradient_boosting(X_tr, X_te, y_tr, y_te)
    >>> isinstance(model, GradientBoostingClassifier)
    True
    >>> acc > 0.6
    True
    """
    pass


# Exercise 10: Learning Rate Effect
# Difficulty: Medium
def learning_rate_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[float, float]:
    """Compare GradientBoosting with learning_rate=[0.01, 0.05, 0.1, 0.5].

    Use n_estimators=100, random_state=42.
    Return dict with learning_rate as keys and test accuracies as values.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Dict mapping learning_rate to accuracies.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> results = learning_rate_comparison(X_tr, X_te, y_tr, y_te)
    >>> len(results) == 4
    True
    """
    pass


# =============================================================================
# XGBOOST (OPTIONAL)
# =============================================================================

# Exercise 11: Train XGBoost (if available)
# Difficulty: Medium
def train_xgboost(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[float, bool]:
    """Train XGBClassifier if available, return test accuracy and success flag.

    Use xgb.XGBClassifier(n_estimators=100, max_depth=3, random_state=42).
    If XGBoost not available, return (0.0, False).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Tuple of (test_accuracy, success_bool).

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> acc, success = train_xgboost(X_tr, X_te, y_tr, y_te)
    >>> success is False or (0.6 <= acc <= 1.0)
    True
    """
    pass


# Exercise 12: LightGBM Training (if available)
# Difficulty: Medium
def train_lightgbm(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[float, bool]:
    """Train LGBMClassifier if available, return test accuracy and success flag.

    Use lgb.LGBMClassifier(n_estimators=100, max_depth=5, random_state=42, verbose=-1).
    If LightGBM not available, return (0.0, False).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Tuple of (test_accuracy, success_bool).

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> acc, success = train_lightgbm(X_tr, X_te, y_tr, y_te)
    >>> success is False or (0.6 <= acc <= 1.0)
    True
    """
    pass


# =============================================================================
# SHAP INTERPRETATION (OPTIONAL)
# =============================================================================

# Exercise 13: SHAP Feature Importance (if available)
# Difficulty: Hard
def shap_feature_importance(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray
) -> Tuple[np.ndarray, bool]:
    """Train RandomForest and compute SHAP feature importances if available.

    Use RandomForestClassifier(n_estimators=100, random_state=42).
    Return array of mean absolute SHAP values and success flag.
    If SHAP not available, return (np.array([]), False).

    Args:
        X_train, X_test: Feature matrices.
        y_train: Training target.

    Returns:
        Tuple of (shap_importances_array, success_bool).

    >>> X, y = make_classification(n_samples=50, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr = train_test_split(X, y, test_size=0.2, random_state=42)[0:3]
    >>> shap_vals, success = shap_feature_importance(X_tr, X_te, y_tr)
    >>> success is False or shap_vals.shape == (5,)
    True
    """
    pass


# Exercise 14: Model Comparison
# Difficulty: Hard
def compare_all_models(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """Train DecisionTree, RandomForest, GradientBoosting, and optionally XGBoost/LightGBM.

    Return dict mapping model names to test accuracies.
    Always include: 'decision_tree', 'random_forest', 'gradient_boosting'.
    Optional: 'xgboost', 'lightgbm' if available.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Dict mapping model names to test accuracies.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> results = compare_all_models(X_tr, X_te, y_tr, y_te)
    >>> all(k in results for k in ['decision_tree', 'random_forest', 'gradient_boosting'])
    True
    """
    pass


# Exercise 15: Cross-Validation Comparison
# Difficulty: Hard
def cross_validation_comparison(
    X: np.ndarray, y: np.ndarray
) -> Dict[str, float]:
    """Perform 5-fold cross-validation on RandomForest and GradientBoosting.

    Return dict with keys 'random_forest_cv_mean', 'random_forest_cv_std',
    'gradient_boosting_cv_mean', 'gradient_boosting_cv_std'.

    Use n_estimators=100, random_state=42 for both, cv=5.

    Args:
        X: Feature matrix.
        y: Target array.

    Returns:
        Dict with mean and std of CV scores for each model.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> results = cross_validation_comparison(X, y)
    >>> len(results) == 4
    True
    """
    pass


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    print("Running Exercise 1: Train Decision Tree...")
    model1, acc1 = train_decision_tree(X_train, X_test, y_train, y_test)
    assert isinstance(model1, DecisionTreeClassifier)
    assert acc1 > 0.6
    print("  PASSED")

    print("Running Exercise 2: Compare Gini vs Entropy...")
    results2 = compare_gini_entropy(X_train, X_test, y_train, y_test)
    assert all(k in results2 for k in ['gini', 'entropy'])
    print("  PASSED")

    print("Running Exercise 3: Tree Depth Comparison...")
    results3 = tree_depth_comparison(X_train, X_test, y_train, y_test)
    assert len(results3) == 4
    print("  PASSED")

    print("Running Exercise 4: Feature Importance...")
    importance4 = decision_tree_feature_importance(X_train, y_train)
    assert importance4.shape == (5,)
    assert np.isclose(importance4.sum(), 1.0)
    print("  PASSED")

    print("Running Exercise 5: Train Random Forest...")
    model5, acc5 = train_random_forest(X_train, X_test, y_train, y_test)
    assert isinstance(model5, RandomForestClassifier)
    assert acc5 > 0.6
    print("  PASSED")

    print("Running Exercise 6: N-Estimators Comparison...")
    results6 = forest_n_estimators_comparison(X_train, X_test, y_train, y_test)
    assert all(k in results6 for k in [10, 50, 100, 200])
    print("  PASSED")

    print("Running Exercise 7: OOB Score...")
    model7, oob7 = random_forest_oob_score(X_train, y_train)
    assert isinstance(model7, RandomForestClassifier)
    assert 0 <= oob7 <= 1
    print("  PASSED")

    print("Running Exercise 8: Feature Importance (RF)...")
    importance8 = random_forest_feature_importance(X_train, y_train)
    assert importance8.shape == (5,)
    print("  PASSED")

    print("Running Exercise 9: Train Gradient Boosting...")
    model9, acc9 = train_gradient_boosting(X_train, X_test, y_train, y_test)
    assert isinstance(model9, GradientBoostingClassifier)
    assert acc9 > 0.6
    print("  PASSED")

    print("Running Exercise 10: Learning Rate Comparison...")
    results10 = learning_rate_comparison(X_train, X_test, y_train, y_test)
    assert len(results10) == 4
    print("  PASSED")

    print("Running Exercise 11: XGBoost...")
    acc11, success11 = train_xgboost(X_train, X_test, y_train, y_test)
    print(f"  PASSED (Available: {success11})")

    print("Running Exercise 12: LightGBM...")
    acc12, success12 = train_lightgbm(X_train, X_test, y_train, y_test)
    print(f"  PASSED (Available: {success12})")

    print("Running Exercise 13: SHAP Feature Importance...")
    X_tr, X_te = train_test_split(X_train, test_size=0.5, random_state=42)
    shap_vals, success13 = shap_feature_importance(X_tr, X_te, y_train[:len(X_tr)])
    print(f"  PASSED (Available: {success13})")

    print("Running Exercise 14: Model Comparison...")
    results14 = compare_all_models(X_train, X_test, y_train, y_test)
    assert all(k in results14 for k in ['decision_tree', 'random_forest', 'gradient_boosting'])
    print("  PASSED")

    print("Running Exercise 15: Cross-Validation Comparison...")
    results15 = cross_validation_comparison(X, y)
    assert len(results15) == 4
    print("  PASSED")

    print("\nAll exercises passed!")
