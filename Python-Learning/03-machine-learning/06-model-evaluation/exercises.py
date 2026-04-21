"""
Module 06: Model Evaluation - Exercises
========================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- If no AssertionError is raised, your solution is correct.

Difficulty levels:
  Easy   - Direct application of sklearn metrics API
  Medium - Requires understanding metric behavior or CV strategies
  Hard   - Combines multiple concepts or uses Optuna
"""

import numpy as np
from sklearn.datasets import load_iris, make_classification, make_regression
from sklearn.model_selection import (
    train_test_split, cross_val_score, KFold, StratifiedKFold,
    TimeSeriesSplit, GridSearchCV, RandomizedSearchCV,
    learning_curve
)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, mean_squared_error,
    mean_absolute_error, r2_score, silhouette_score,
    classification_report, log_loss
)
from sklearn.preprocessing import StandardScaler


# =============================================================================
# CLASSIFICATION METRICS
# =============================================================================

# Exercise 1: Confusion Matrix Components
# Difficulty: Easy
# Given true labels and predicted labels, return TN, FP, FN, TP as a tuple.
def confusion_matrix_components(
    y_true: np.ndarray, y_pred: np.ndarray
) -> tuple[int, int, int, int]:
    """Extract TN, FP, FN, TP from confusion matrix.

    Args:
        y_true: True binary labels.
        y_pred: Predicted binary labels.

    Returns:
        Tuple of (TN, FP, FN, TP).

    >>> y_true = np.array([0, 0, 1, 1, 1, 0])
    >>> y_pred = np.array([0, 1, 1, 1, 0, 0])
    >>> confusion_matrix_components(y_true, y_pred)
    (2, 1, 1, 2)
    """
    pass


# Exercise 2: Precision and Recall
# Difficulty: Easy
# Compute precision and recall manually from TN, FP, FN, TP.
def precision_recall_manual(
    tn: int, fp: int, fn: int, tp: int
) -> tuple[float, float]:
    """Compute precision and recall from confusion matrix components.

    Args:
        tn, fp, fn, tp: Confusion matrix components.

    Returns:
        Tuple of (precision, recall) as floats.

    >>> precision_recall_manual(50, 10, 5, 35)
    (0.7777777777777778, 0.875)
    """
    pass


# Exercise 3: F1 Score Variants
# Difficulty: Medium
# Train a model on Iris data and compute F1 with macro, micro, and weighted averaging.
def compute_f1_variants(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> dict[str, float]:
    """Train LogisticRegression and compute F1 with different averaging.

    Use LogisticRegression(random_state=42, max_iter=1000).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Dict with keys 'macro', 'micro', 'weighted' and float values.

    >>> iris = load_iris()
    >>> X_tr, X_te, y_tr, y_te = train_test_split(
    ...     iris.data, iris.target, random_state=42)
    >>> result = compute_f1_variants(X_tr, X_te, y_tr, y_te)
    >>> all(0 <= v <= 1 for v in result.values())
    True
    """
    pass


# Exercise 4: ROC AUC Score
# Difficulty: Medium
# Train a LogisticRegression on binary classification data and return the
# ROC AUC score using predict_proba.
def compute_roc_auc(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> float:
    """Train LogisticRegression and compute ROC AUC.

    Use LogisticRegression(random_state=42, max_iter=1000).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Binary target arrays.

    Returns:
        ROC AUC score (float between 0.5 and 1.0 for a decent model).

    >>> X, y = make_classification(n_samples=500, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> auc = compute_roc_auc(X_tr, X_te, y_tr, y_te)
    >>> 0.5 <= auc <= 1.0
    True
    """
    pass


# Exercise 5: Log Loss
# Difficulty: Easy
# Compute log loss given true labels and predicted probabilities.
def compute_log_loss(
    y_true: np.ndarray, y_proba: np.ndarray
) -> float:
    """Compute log loss (cross-entropy).

    Args:
        y_true: True binary labels.
        y_proba: Predicted probabilities for class 1.

    Returns:
        Log loss value (float, lower is better).

    >>> y_true = np.array([0, 0, 1, 1])
    >>> y_proba = np.array([0.1, 0.4, 0.8, 0.9])
    >>> loss = compute_log_loss(y_true, y_proba)
    >>> 0 < loss < 1
    True
    """
    pass


# =============================================================================
# REGRESSION METRICS
# =============================================================================

# Exercise 6: Regression Metrics Suite
# Difficulty: Medium
# Compute MSE, RMSE, MAE, and R-squared from predictions.
def regression_metrics(
    y_true: np.ndarray, y_pred: np.ndarray
) -> dict[str, float]:
    """Compute common regression metrics.

    Args:
        y_true: True target values.
        y_pred: Predicted values.

    Returns:
        Dict with keys 'mse', 'rmse', 'mae', 'r2' and float values.

    >>> y_true = np.array([3.0, 5.0, 2.5, 7.0])
    >>> y_pred = np.array([2.8, 5.2, 2.3, 6.8])
    >>> metrics = regression_metrics(y_true, y_pred)
    >>> metrics['rmse'] < 1.0
    True
    """
    pass


# Exercise 7: Adjusted R-Squared
# Difficulty: Medium
# Compute adjusted R-squared given R-squared, number of samples, and number of features.
def adjusted_r_squared(r2: float, n_samples: int, n_features: int) -> float:
    """Compute adjusted R-squared.

    Formula: 1 - (1 - R^2) * (n - 1) / (n - p - 1)
    where n = n_samples, p = n_features.

    Args:
        r2: R-squared value.
        n_samples: Number of samples.
        n_features: Number of features.

    Returns:
        Adjusted R-squared value (float).

    >>> adjusted_r_squared(0.9, 100, 5)
    0.8946808510638298
    """
    pass


# =============================================================================
# CROSS-VALIDATION
# =============================================================================

# Exercise 8: Stratified Cross-Validation
# Difficulty: Easy
# Perform 5-fold stratified cross-validation and return mean and std of scores.
def stratified_cv_score(
    X: np.ndarray, y: np.ndarray
) -> tuple[float, float]:
    """Perform 5-fold stratified CV with LogisticRegression.

    Use LogisticRegression(random_state=42, max_iter=1000).
    Use StratifiedKFold with shuffle=True, random_state=42.
    Scoring: 'accuracy'.

    Args:
        X: Feature matrix.
        y: Target array.

    Returns:
        Tuple of (mean_score, std_score).

    >>> iris = load_iris()
    >>> mean_s, std_s = stratified_cv_score(iris.data, iris.target)
    >>> mean_s > 0.9
    True
    """
    pass


# Exercise 9: Time Series Cross-Validation
# Difficulty: Medium
# Perform time series cross-validation with 5 splits and return scores.
def timeseries_cv_scores(
    X: np.ndarray, y: np.ndarray
) -> np.ndarray:
    """Perform TimeSeriesSplit CV with LinearRegression.

    Use TimeSeriesSplit(n_splits=5).
    Scoring: 'neg_mean_squared_error'.

    Args:
        X: Feature matrix (assumed to be in temporal order).
        y: Target array.

    Returns:
        Array of scores (negative MSE) for each fold.

    >>> X, y = make_regression(n_samples=200, n_features=5, random_state=42)
    >>> scores = timeseries_cv_scores(X, y)
    >>> len(scores) == 5
    True
    """
    pass


# =============================================================================
# HYPERPARAMETER TUNING
# =============================================================================

# Exercise 10: Grid Search
# Difficulty: Medium
# Perform grid search over RandomForest hyperparameters and return best params.
def grid_search_rf(
    X: np.ndarray, y: np.ndarray
) -> dict:
    """Grid search over RandomForest hyperparameters.

    Parameter grid:
        'n_estimators': [50, 100],
        'max_depth': [3, 5, None]

    Use cv=3, scoring='accuracy', RandomForestClassifier(random_state=42).

    Args:
        X: Feature matrix.
        y: Target array.

    Returns:
        Dict of best parameters found.

    >>> iris = load_iris()
    >>> params = grid_search_rf(iris.data, iris.target)
    >>> 'n_estimators' in params and 'max_depth' in params
    True
    """
    pass


# Exercise 11: Optuna Basic Tuning
# Difficulty: Hard
# Use Optuna to tune a RandomForest on the given data.
# Return the best trial's parameters and score.
def optuna_tune_rf(
    X: np.ndarray, y: np.ndarray, n_trials: int = 30
) -> tuple[dict, float]:
    """Tune RandomForest with Optuna.

    Search space:
        n_estimators: int in [50, 300]
        max_depth: int in [3, 20]
        min_samples_split: int in [2, 10]

    Use cross_val_score with cv=3, scoring='accuracy'.
    Direction: maximize.

    Args:
        X: Feature matrix.
        y: Target array.
        n_trials: Number of Optuna trials.

    Returns:
        Tuple of (best_params dict, best_score float).

    >>> iris = load_iris()
    >>> params, score = optuna_tune_rf(iris.data, iris.target, n_trials=10)
    >>> score > 0.9
    True
    """
    pass


# Exercise 12: Optuna with Pruning
# Difficulty: Hard
# Use Optuna with MedianPruner to tune a model.
# Implement manual cross-validation with intermediate reporting.
def optuna_tune_with_pruning(
    X: np.ndarray, y: np.ndarray, n_trials: int = 30
) -> tuple[dict, float]:
    """Tune RandomForest with Optuna using MedianPruner.

    Search space:
        n_estimators: int in [50, 300]
        max_depth: int in [3, 20]

    Use StratifiedKFold(n_splits=5, shuffle=True, random_state=42).
    Report intermediate accuracy after each fold.
    Use MedianPruner with n_startup_trials=5.
    Direction: maximize.

    Args:
        X: Feature matrix.
        y: Target array.
        n_trials: Number of Optuna trials.

    Returns:
        Tuple of (best_params dict, best_score float).

    >>> iris = load_iris()
    >>> params, score = optuna_tune_with_pruning(iris.data, iris.target, n_trials=10)
    >>> score > 0.9
    True
    """
    pass


# =============================================================================
# LEARNING CURVES
# =============================================================================

# Exercise 13: Learning Curve Data
# Difficulty: Medium
# Generate learning curve data and return train/val means and sizes.
def compute_learning_curve(
    X: np.ndarray, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute learning curve data for RandomForestClassifier.

    Use RandomForestClassifier(n_estimators=50, random_state=42).
    Use train_sizes=np.linspace(0.1, 1.0, 5), cv=5, scoring='accuracy'.

    Args:
        X: Feature matrix.
        y: Target array.

    Returns:
        Tuple of (train_sizes_abs, train_mean_scores, val_mean_scores).
        Each is a 1D array with 5 elements.

    >>> iris = load_iris()
    >>> sizes, train_m, val_m = compute_learning_curve(iris.data, iris.target)
    >>> len(sizes) == 5
    True
    """
    pass


# =============================================================================
# IMBALANCED DATA
# =============================================================================

# Exercise 14: Class Weight Comparison
# Difficulty: Medium
# Train two LogisticRegression models (with and without class_weight='balanced')
# and compare their recall on the minority class (class 1).
def compare_class_weights(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> tuple[float, float]:
    """Compare recall with and without balanced class weights.

    Use LogisticRegression(random_state=42, max_iter=1000).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Binary target arrays (imbalanced).

    Returns:
        Tuple of (recall_plain, recall_balanced).

    >>> X, y = make_classification(n_samples=1000, weights=[0.9, 0.1],
    ...                            random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> plain, balanced = compare_class_weights(X_tr, X_te, y_tr, y_te)
    >>> balanced >= plain
    True
    """
    pass


# Exercise 15: Optimal Threshold
# Difficulty: Hard
# Find the classification threshold that maximizes F1 score.
def find_optimal_threshold(
    y_true: np.ndarray, y_proba: np.ndarray
) -> tuple[float, float]:
    """Find the threshold that maximizes F1 score.

    Test thresholds from 0.1 to 0.9 in steps of 0.01.

    Args:
        y_true: True binary labels.
        y_proba: Predicted probabilities for class 1.

    Returns:
        Tuple of (best_threshold, best_f1_score).

    >>> y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    >>> y_proba = np.array([0.1, 0.3, 0.4, 0.6, 0.5, 0.7, 0.8, 0.9])
    >>> threshold, f1 = find_optimal_threshold(y_true, y_proba)
    >>> 0.1 <= threshold <= 0.9
    True
    >>> f1 > 0.5
    True
    """
    pass


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    print("Running Exercise 1: Confusion Matrix Components...")
    y_true1 = np.array([0, 0, 1, 1, 1, 0])
    y_pred1 = np.array([0, 1, 1, 1, 0, 0])
    tn, fp, fn, tp = confusion_matrix_components(y_true1, y_pred1)
    assert (tn, fp, fn, tp) == (2, 1, 1, 2), f"Got ({tn}, {fp}, {fn}, {tp})"
    print("  PASSED")

    print("Running Exercise 2: Precision and Recall Manual...")
    p, r = precision_recall_manual(50, 10, 5, 35)
    assert abs(p - 0.7778) < 0.001, f"Precision={p}"
    assert abs(r - 0.875) < 0.001, f"Recall={r}"
    print("  PASSED")

    print("Running Exercise 3: F1 Variants...")
    iris = load_iris()
    X_tr3, X_te3, y_tr3, y_te3 = train_test_split(
        iris.data, iris.target, random_state=42)
    f1_result = compute_f1_variants(X_tr3, X_te3, y_tr3, y_te3)
    assert all(k in f1_result for k in ['macro', 'micro', 'weighted'])
    assert all(0 <= v <= 1 for v in f1_result.values())
    print("  PASSED")

    print("Running Exercise 4: ROC AUC...")
    X4, y4 = make_classification(n_samples=500, random_state=42)
    X_tr4, X_te4, y_tr4, y_te4 = train_test_split(X4, y4, random_state=42)
    auc_val = compute_roc_auc(X_tr4, X_te4, y_tr4, y_te4)
    assert 0.5 <= auc_val <= 1.0, f"AUC={auc_val}"
    print("  PASSED")

    print("Running Exercise 5: Log Loss...")
    y_true5 = np.array([0, 0, 1, 1])
    y_proba5 = np.array([0.1, 0.4, 0.8, 0.9])
    ll = compute_log_loss(y_true5, y_proba5)
    assert 0 < ll < 1, f"Log loss={ll}"
    print("  PASSED")

    print("Running Exercise 6: Regression Metrics...")
    y_true6 = np.array([3.0, 5.0, 2.5, 7.0])
    y_pred6 = np.array([2.8, 5.2, 2.3, 6.8])
    metrics6 = regression_metrics(y_true6, y_pred6)
    assert all(k in metrics6 for k in ['mse', 'rmse', 'mae', 'r2'])
    assert metrics6['rmse'] < 1.0
    print("  PASSED")

    print("Running Exercise 7: Adjusted R-Squared...")
    adj_r2 = adjusted_r_squared(0.9, 100, 5)
    assert abs(adj_r2 - 0.8947) < 0.001, f"Adj R2={adj_r2}"
    print("  PASSED")

    print("Running Exercise 8: Stratified CV...")
    mean_s, std_s = stratified_cv_score(iris.data, iris.target)
    assert mean_s > 0.9, f"Mean={mean_s}"
    assert std_s < 0.1, f"Std={std_s}"
    print("  PASSED")

    print("Running Exercise 9: Time Series CV...")
    X9, y9 = make_regression(n_samples=200, n_features=5, random_state=42)
    scores9 = timeseries_cv_scores(X9, y9)
    assert len(scores9) == 5
    print("  PASSED")

    print("Running Exercise 10: Grid Search...")
    params10 = grid_search_rf(iris.data, iris.target)
    assert 'n_estimators' in params10
    assert 'max_depth' in params10
    print("  PASSED")

    print("Running Exercise 11: Optuna Basic...")
    params11, score11 = optuna_tune_rf(iris.data, iris.target, n_trials=10)
    assert score11 > 0.9, f"Score={score11}"
    print("  PASSED")

    print("Running Exercise 12: Optuna with Pruning...")
    params12, score12 = optuna_tune_with_pruning(iris.data, iris.target, n_trials=10)
    assert score12 > 0.9, f"Score={score12}"
    print("  PASSED")

    print("Running Exercise 13: Learning Curve...")
    sizes13, train_m13, val_m13 = compute_learning_curve(iris.data, iris.target)
    assert len(sizes13) == 5
    assert len(train_m13) == 5
    assert len(val_m13) == 5
    print("  PASSED")

    print("Running Exercise 14: Class Weight Comparison...")
    X14, y14 = make_classification(n_samples=1000, weights=[0.9, 0.1],
                                    random_state=42)
    X_tr14, X_te14, y_tr14, y_te14 = train_test_split(X14, y14, random_state=42)
    plain14, balanced14 = compare_class_weights(X_tr14, X_te14, y_tr14, y_te14)
    assert balanced14 >= plain14, f"Balanced={balanced14}, Plain={plain14}"
    print("  PASSED")

    print("Running Exercise 15: Optimal Threshold...")
    y_true15 = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_proba15 = np.array([0.1, 0.3, 0.4, 0.6, 0.5, 0.7, 0.8, 0.9])
    thresh15, f1_15 = find_optimal_threshold(y_true15, y_proba15)
    assert 0.1 <= thresh15 <= 0.9
    assert f1_15 > 0.5
    print("  PASSED")

    print("\nAll exercises passed!")
