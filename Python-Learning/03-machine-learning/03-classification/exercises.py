"""
Module 03: Classification - Exercises
======================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- If no AssertionError is raised, your solution is correct.

Difficulty levels:
  Easy   - Direct use of a single classifier
  Medium - Requires preprocessing, metric selection, or comparing models
  Hard   - Requires custom code, visualization, or complex analysis
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
from sklearn.datasets import make_classification, load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
from sklearn.multiclass import OneVsRestClassifier


# =============================================================================
# LOGISTIC REGRESSION
# =============================================================================

# Exercise 1: Train a Logistic Regression Model
# Difficulty: Easy
def train_logistic_regression(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[LogisticRegression, float]:
    """Train a LogisticRegression classifier and return model and test accuracy.

    Steps:
        1. Standardize the features (StandardScaler).
        2. Create LogisticRegression(random_state=42, max_iter=1000).
        3. Fit on training data.
        4. Return the model and test accuracy.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Tuple of (trained_model, test_accuracy).

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> model, acc = train_logistic_regression(X_tr, X_te, y_tr, y_te)
    >>> isinstance(model, LogisticRegression)
    True
    >>> acc > 0.6
    True
    """
    pass


# Exercise 2: Get Probability Predictions
# Difficulty: Easy
def logistic_regression_probabilities(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray
) -> np.ndarray:
    """Train LogisticRegression and return probability predictions on test data.

    Use StandardScaler and LogisticRegression(random_state=42, max_iter=1000).
    Return predict_proba for X_test. Shape should be (n_samples, 2) for binary.

    Args:
        X_train, X_test: Feature matrices.
        y_train: Training target.

    Returns:
        Probability predictions array (n_samples, n_classes).

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, _ = train_test_split(X, y, random_state=42)
    >>> proba = logistic_regression_probabilities(X_tr, X_te, y_tr)
    >>> proba.shape[1] == 2  # binary classification
    True
    >>> np.all((proba >= 0) & (proba <= 1))
    True
    """
    pass


# Exercise 3: Logistic Regression with Different Regularization
# Difficulty: Medium
def compare_logistic_regularization(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """Train LogisticRegression with C values [0.1, 1.0, 10.0].

    Return dict with keys 'C_0.1', 'C_1.0', 'C_10.0' and test accuracies as values.

    Use StandardScaler and LogisticRegression(random_state=42, max_iter=1000).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Dict mapping C value strings to test accuracies.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> results = compare_logistic_regularization(X_tr, X_te, y_tr, y_te)
    >>> len(results) == 3
    True
    >>> all(k in results for k in ['C_0.1', 'C_1.0', 'C_10.0'])
    True
    """
    pass


# =============================================================================
# SUPPORT VECTOR MACHINES (SVM)
# =============================================================================

# Exercise 4: SVM with Different Kernels
# Difficulty: Medium
def svm_kernel_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """Train SVM with 'linear', 'rbf', 'poly' kernels and return test accuracies.

    Standardize features. Use SVC(C=1.0, random_state=42) for each kernel.
    For 'poly', use degree=3.

    Return dict with keys 'linear', 'rbf', 'poly' and accuracies as values.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Dict mapping kernel names to test accuracies.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> results = svm_kernel_comparison(X_tr, X_te, y_tr, y_te)
    >>> all(k in results for k in ['linear', 'rbf', 'poly'])
    True
    """
    pass


# Exercise 5: SVM with RBF Kernel - Gamma Effect
# Difficulty: Medium
def svm_gamma_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """Train RBF SVM with different gamma values [0.1, 1.0, 10.0].

    Standardize features. Use SVC(kernel='rbf', C=1.0, random_state=42).
    Return dict with keys 'gamma_0.1', 'gamma_1.0', 'gamma_10.0'.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Dict mapping gamma strings to test accuracies.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> results = svm_gamma_comparison(X_tr, X_te, y_tr, y_te)
    >>> len(results) == 3
    True
    """
    pass


# =============================================================================
# K-NEAREST NEIGHBORS
# =============================================================================

# Exercise 6: KNN with Different k Values
# Difficulty: Easy
def knn_k_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[int, float]:
    """Train KNN with k=[3, 5, 7, 9] and return test accuracies.

    Standardize features. Return dict with k as keys and accuracies as values.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Dict mapping k values to test accuracies.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> results = knn_k_comparison(X_tr, X_te, y_tr, y_te)
    >>> all(k in results for k in [3, 5, 7, 9])
    True
    """
    pass


# Exercise 7: KNN Probability Predictions
# Difficulty: Easy
def knn_probabilities(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray
) -> np.ndarray:
    """Train KNN (k=5) and return probability predictions on test data.

    Standardize features. Return predict_proba for X_test.

    Args:
        X_train, X_test: Feature matrices.
        y_train: Training target.

    Returns:
        Probability predictions array.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, _ = train_test_split(X, y, random_state=42)
    >>> proba = knn_probabilities(X_tr, X_te, y_tr)
    >>> proba.shape[1] == 2
    True
    >>> np.allclose(proba.sum(axis=1), 1.0)
    True
    """
    pass


# =============================================================================
# NAIVE BAYES
# =============================================================================

# Exercise 8: Gaussian Naive Bayes
# Difficulty: Easy
def train_gaussian_naive_bayes(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[GaussianNB, float]:
    """Train GaussianNB and return model and test accuracy.

    Note: Do NOT scale features for Naive Bayes.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Tuple of (trained_model, test_accuracy).

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> model, acc = train_gaussian_naive_bayes(X_tr, X_te, y_tr, y_te)
    >>> isinstance(model, GaussianNB)
    True
    >>> acc >= 0.5
    True
    """
    pass


# Exercise 9: Naive Bayes Learned Parameters
# Difficulty: Medium
def naive_bayes_parameters(
    X_train: np.ndarray, y_train: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Train GaussianNB and return class priors and feature means.

    Args:
        X_train: Feature matrix.
        y_train: Target array.

    Returns:
        Tuple of (class_priors, class_means) where:
            - class_priors: shape (n_classes,)
            - class_means: shape (n_classes, n_features)

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> priors, means = naive_bayes_parameters(X, y)
    >>> priors.shape == (2,)  # binary
    True
    >>> means.shape == (2, 5)
    True
    """
    pass


# =============================================================================
# CLASSIFICATION METRICS
# =============================================================================

# Exercise 10: Compute All Classification Metrics
# Difficulty: Medium
def compute_metrics(
    y_test: np.ndarray, y_pred: np.ndarray
) -> Dict[str, float]:
    """Compute accuracy, precision, recall, f1 for binary classification.

    Return dict with keys: 'accuracy', 'precision', 'recall', 'f1'.

    Args:
        y_test: True labels.
        y_pred: Predicted labels.

    Returns:
        Dict mapping metric names to values.

    >>> y_true = np.array([0, 1, 1, 0, 1])
    >>> y_pred = np.array([0, 1, 0, 0, 1])
    >>> metrics = compute_metrics(y_true, y_pred)
    >>> len(metrics) == 4
    True
    >>> all(k in metrics for k in ['accuracy', 'precision', 'recall', 'f1'])
    True
    """
    pass


# Exercise 11: Confusion Matrix Analysis
# Difficulty: Medium
def analyze_confusion_matrix(
    y_test: np.ndarray, y_pred: np.ndarray
) -> Dict[str, int]:
    """Compute confusion matrix and return TP, FP, TN, FN counts.

    For binary classification (classes 0 and 1), class 1 is positive.

    Args:
        y_test: True labels.
        y_pred: Predicted labels.

    Returns:
        Dict with keys 'TP', 'FP', 'TN', 'FN'.

    >>> y_true = np.array([0, 1, 1, 0, 1, 0])
    >>> y_pred = np.array([0, 1, 0, 0, 1, 1])
    >>> cm = analyze_confusion_matrix(y_true, y_pred)
    >>> all(k in cm for k in ['TP', 'FP', 'TN', 'FN'])
    True
    >>> cm['TP'] + cm['FP'] + cm['TN'] + cm['FN'] == len(y_true)
    True
    """
    pass


# Exercise 12: ROC-AUC Score
# Difficulty: Medium
def compute_roc_auc(
    y_test: np.ndarray, y_proba: np.ndarray
) -> float:
    """Compute ROC-AUC score from probability predictions.

    For binary classification, use probability of positive class (column 1).

    Args:
        y_test: True labels.
        y_proba: Probability predictions (n_samples, 2).

    Returns:
        ROC-AUC score (float between 0 and 1).

    >>> y_true = np.array([0, 1, 1, 0, 1])
    >>> y_proba = np.array([[0.9, 0.1], [0.2, 0.8], [0.3, 0.7],
    ...                     [0.8, 0.2], [0.1, 0.9]])
    >>> roc_auc = compute_roc_auc(y_true, y_proba)
    >>> 0 <= roc_auc <= 1
    True
    """
    pass


# =============================================================================
# MULTI-CLASS CLASSIFICATION
# =============================================================================

# Exercise 13: Multi-Class Classification with Iris
# Difficulty: Medium
def multi_class_classification() -> Dict[str, float]:
    """Load iris dataset and train classifiers on all 3 classes.

    Compare LogisticRegression (multinomial), GaussianNB, and KNN (k=5).
    Standardize features (except Naive Bayes).

    Return dict with keys 'logistic_regression', 'gaussian_nb', 'knn'
    and cross-validation scores (5-fold) as values.

    Returns:
        Dict mapping classifier names to mean CV accuracy scores.

    >>> results = multi_class_classification()
    >>> len(results) == 3
    True
    >>> all(k in results for k in ['logistic_regression', 'gaussian_nb', 'knn'])
    True
    """
    pass


# Exercise 14: One-vs-Rest SVM
# Difficulty: Hard
def one_vs_rest_svm() -> Tuple[OneVsRestClassifier, float]:
    """Load iris dataset and train OneVsRest SVM with RBF kernel.

    Use SVC(kernel='rbf', probability=True, random_state=42).
    Standardize features. Return model and test accuracy (80/20 split, random_state=42).

    Returns:
        Tuple of (trained_model, test_accuracy).

    >>> model, acc = one_vs_rest_svm()
    >>> isinstance(model, OneVsRestClassifier)
    True
    >>> acc > 0.8
    True
    """
    pass


# Exercise 15: Classification Report for Multi-Class
# Difficulty: Hard
def classification_report_multiclass() -> str:
    """Load iris dataset, train LogisticRegression, and return classification report.

    Use random_state=42 for both LogisticRegression and train_test_split (80/20).
    Standardize features.
    Return the classification_report as a string (use target_names from iris).

    Returns:
        Classification report string for all 3 iris classes.

    >>> report = classification_report_multiclass()
    >>> isinstance(report, str)
    True
    >>> 'precision' in report
    True
    >>> 'recall' in report
    True
    """
    pass


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    print("Running Exercise 1: Train Logistic Regression...")
    model1, acc1 = train_logistic_regression(X_train, X_test, y_train, y_test)
    assert isinstance(model1, LogisticRegression)
    assert acc1 > 0.6
    print("  PASSED")

    print("Running Exercise 2: Logistic Regression Probabilities...")
    proba2 = logistic_regression_probabilities(X_train, X_test, y_train)
    assert proba2.shape[1] == 2
    assert np.all((proba2 >= 0) & (proba2 <= 1))
    print("  PASSED")

    print("Running Exercise 3: Logistic Regularization Comparison...")
    results3 = compare_logistic_regularization(X_train, X_test, y_train, y_test)
    assert len(results3) == 3
    assert all(k in results3 for k in ['C_0.1', 'C_1.0', 'C_10.0'])
    print("  PASSED")

    print("Running Exercise 4: SVM Kernel Comparison...")
    results4 = svm_kernel_comparison(X_train, X_test, y_train, y_test)
    assert all(k in results4 for k in ['linear', 'rbf', 'poly'])
    print("  PASSED")

    print("Running Exercise 5: SVM Gamma Comparison...")
    results5 = svm_gamma_comparison(X_train, X_test, y_train, y_test)
    assert len(results5) == 3
    print("  PASSED")

    print("Running Exercise 6: KNN k Comparison...")
    results6 = knn_k_comparison(X_train, X_test, y_train, y_test)
    assert all(k in results6 for k in [3, 5, 7, 9])
    print("  PASSED")

    print("Running Exercise 7: KNN Probabilities...")
    proba7 = knn_probabilities(X_train, X_test, y_train)
    assert proba7.shape[1] == 2
    assert np.allclose(proba7.sum(axis=1), 1.0)
    print("  PASSED")

    print("Running Exercise 8: Gaussian Naive Bayes...")
    model8, acc8 = train_gaussian_naive_bayes(X_train, X_test, y_train, y_test)
    assert isinstance(model8, GaussianNB)
    assert acc8 >= 0.5
    print("  PASSED")

    print("Running Exercise 9: Naive Bayes Parameters...")
    priors9, means9 = naive_bayes_parameters(X_train, y_train)
    assert priors9.shape == (2,)
    assert means9.shape == (2, 5)
    print("  PASSED")

    print("Running Exercise 10: Classification Metrics...")
    y_pred10 = np.array([0, 1, 1, 0, 1])
    y_true10 = np.array([0, 1, 0, 0, 1])
    metrics10 = compute_metrics(y_true10, y_pred10)
    assert len(metrics10) == 4
    assert all(k in metrics10 for k in ['accuracy', 'precision', 'recall', 'f1'])
    print("  PASSED")

    print("Running Exercise 11: Confusion Matrix Analysis...")
    y_true11 = np.array([0, 1, 1, 0, 1, 0])
    y_pred11 = np.array([0, 1, 0, 0, 1, 1])
    cm11 = analyze_confusion_matrix(y_true11, y_pred11)
    assert all(k in cm11 for k in ['TP', 'FP', 'TN', 'FN'])
    assert cm11['TP'] + cm11['FP'] + cm11['TN'] + cm11['FN'] == 6
    print("  PASSED")

    print("Running Exercise 12: ROC-AUC...")
    y_true12 = np.array([0, 1, 1, 0, 1])
    y_proba12 = np.array([[0.9, 0.1], [0.2, 0.8], [0.3, 0.7],
                          [0.8, 0.2], [0.1, 0.9]])
    roc_auc12 = compute_roc_auc(y_true12, y_proba12)
    assert 0 <= roc_auc12 <= 1
    print("  PASSED")

    print("Running Exercise 13: Multi-Class Classification...")
    results13 = multi_class_classification()
    assert len(results13) == 3
    assert all(k in results13 for k in ['logistic_regression', 'gaussian_nb', 'knn'])
    print("  PASSED")

    print("Running Exercise 14: One-vs-Rest SVM...")
    model14, acc14 = one_vs_rest_svm()
    assert isinstance(model14, OneVsRestClassifier)
    assert acc14 > 0.8
    print("  PASSED")

    print("Running Exercise 15: Classification Report...")
    report15 = classification_report_multiclass()
    assert isinstance(report15, str)
    assert 'precision' in report15
    assert 'recall' in report15
    print("  PASSED")

    print("\nAll exercises passed!")
