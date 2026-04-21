"""
Module 03: Classification - Solutions
======================================
Complete implementations for all classification exercises.
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

def train_logistic_regression(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[LogisticRegression, float]:
    """Train a LogisticRegression classifier and return model and test accuracy."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)

    accuracy = model.score(X_test_scaled, y_test)
    return model, accuracy


def logistic_regression_probabilities(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray
) -> np.ndarray:
    """Train LogisticRegression and return probability predictions on test data."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)

    return model.predict_proba(X_test_scaled)


def compare_logistic_regularization(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """Train LogisticRegression with different C values and compare."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}
    for c in [0.1, 1.0, 10.0]:
        model = LogisticRegression(C=c, random_state=42, max_iter=1000)
        model.fit(X_train_scaled, y_train)
        accuracy = model.score(X_test_scaled, y_test)
        results[f'C_{c}'] = accuracy

    return results


# =============================================================================
# SUPPORT VECTOR MACHINES (SVM)
# =============================================================================

def svm_kernel_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """Train SVM with different kernels and return test accuracies."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}
    for kernel in ['linear', 'rbf', 'poly']:
        if kernel == 'poly':
            model = SVC(kernel=kernel, degree=3, C=1.0, random_state=42)
        else:
            model = SVC(kernel=kernel, C=1.0, random_state=42)
        model.fit(X_train_scaled, y_train)
        accuracy = model.score(X_test_scaled, y_test)
        results[kernel] = accuracy

    return results


def svm_gamma_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """Train RBF SVM with different gamma values."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}
    for gamma in [0.1, 1.0, 10.0]:
        model = SVC(kernel='rbf', gamma=gamma, C=1.0, random_state=42)
        model.fit(X_train_scaled, y_train)
        accuracy = model.score(X_test_scaled, y_test)
        results[f'gamma_{gamma}'] = accuracy

    return results


# =============================================================================
# K-NEAREST NEIGHBORS
# =============================================================================

def knn_k_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[int, float]:
    """Train KNN with different k values and compare."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}
    for k in [3, 5, 7, 9]:
        model = KNeighborsClassifier(n_neighbors=k)
        model.fit(X_train_scaled, y_train)
        accuracy = model.score(X_test_scaled, y_test)
        results[k] = accuracy

    return results


def knn_probabilities(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray
) -> np.ndarray:
    """Train KNN (k=5) and return probability predictions on test data."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train_scaled, y_train)

    return model.predict_proba(X_test_scaled)


# =============================================================================
# NAIVE BAYES
# =============================================================================

def train_gaussian_naive_bayes(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[GaussianNB, float]:
    """Train GaussianNB and return model and test accuracy."""
    model = GaussianNB()
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    return model, accuracy


def naive_bayes_parameters(
    X_train: np.ndarray, y_train: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Train GaussianNB and return class priors and feature means."""
    model = GaussianNB()
    model.fit(X_train, y_train)

    return model.class_prior_, model.theta_


# =============================================================================
# CLASSIFICATION METRICS
# =============================================================================

def compute_metrics(
    y_test: np.ndarray, y_pred: np.ndarray
) -> Dict[str, float]:
    """Compute all classification metrics."""
    return {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred)
    }


def analyze_confusion_matrix(
    y_test: np.ndarray, y_pred: np.ndarray
) -> Dict[str, int]:
    """Compute confusion matrix and extract TP, FP, TN, FN."""
    cm = confusion_matrix(y_test, y_pred)

    # For binary classification where class 1 is positive:
    # cm[0, 0] = TN, cm[0, 1] = FP
    # cm[1, 0] = FN, cm[1, 1] = TP
    tn, fp = cm[0]
    fn, tp = cm[1]

    return {
        'TP': int(tp),
        'FP': int(fp),
        'TN': int(tn),
        'FN': int(fn)
    }


def compute_roc_auc(
    y_test: np.ndarray, y_proba: np.ndarray
) -> float:
    """Compute ROC-AUC score from probability predictions."""
    # Use probability of positive class (column 1)
    return roc_auc_score(y_test, y_proba[:, 1])


# =============================================================================
# MULTI-CLASS CLASSIFICATION
# =============================================================================

def multi_class_classification() -> Dict[str, float]:
    """Load iris dataset and train classifiers on all 3 classes."""
    iris = load_iris()
    X = iris.data
    y = iris.target

    results = {}

    # Logistic Regression
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model_lr = LogisticRegression(multi_class='multinomial', random_state=42, max_iter=1000)
    cv_scores_lr = cross_val_score(model_lr, X_scaled, y, cv=5, scoring='accuracy')
    results['logistic_regression'] = cv_scores_lr.mean()

    # Gaussian Naive Bayes
    model_nb = GaussianNB()
    cv_scores_nb = cross_val_score(model_nb, X, y, cv=5, scoring='accuracy')
    results['gaussian_nb'] = cv_scores_nb.mean()

    # KNN
    model_knn = KNeighborsClassifier(n_neighbors=5)
    X_scaled_knn = scaler.fit_transform(X)
    cv_scores_knn = cross_val_score(model_knn, X_scaled_knn, y, cv=5, scoring='accuracy')
    results['knn'] = cv_scores_knn.mean()

    return results


def one_vs_rest_svm() -> Tuple[OneVsRestClassifier, float]:
    """Load iris dataset and train OneVsRest SVM with RBF kernel."""
    iris = load_iris()
    X = iris.data
    y = iris.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = OneVsRestClassifier(SVC(kernel='rbf', probability=True, random_state=42))
    model.fit(X_train_scaled, y_train)

    accuracy = model.score(X_test_scaled, y_test)
    return model, accuracy


def classification_report_multiclass() -> str:
    """Load iris dataset, train LogisticRegression, and return classification report."""
    iris = load_iris()
    X = iris.data
    y = iris.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)

    report = classification_report(
        y_test, y_pred,
        target_names=iris.target_names
    )

    return report


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
    print(f"  PASSED (Accuracy: {acc1:.4f})")

    print("Running Exercise 2: Logistic Regression Probabilities...")
    proba2 = logistic_regression_probabilities(X_train, X_test, y_train)
    assert proba2.shape[1] == 2
    assert np.all((proba2 >= 0) & (proba2 <= 1))
    print("  PASSED")

    print("Running Exercise 3: Logistic Regularization Comparison...")
    results3 = compare_logistic_regularization(X_train, X_test, y_train, y_test)
    assert len(results3) == 3
    print(f"  PASSED: {results3}")

    print("Running Exercise 4: SVM Kernel Comparison...")
    results4 = svm_kernel_comparison(X_train, X_test, y_train, y_test)
    print(f"  PASSED: {results4}")

    print("Running Exercise 5: SVM Gamma Comparison...")
    results5 = svm_gamma_comparison(X_train, X_test, y_train, y_test)
    print(f"  PASSED: {results5}")

    print("Running Exercise 6: KNN k Comparison...")
    results6 = knn_k_comparison(X_train, X_test, y_train, y_test)
    print(f"  PASSED: {results6}")

    print("Running Exercise 7: KNN Probabilities...")
    proba7 = knn_probabilities(X_train, X_test, y_train)
    assert proba7.shape[1] == 2
    assert np.allclose(proba7.sum(axis=1), 1.0)
    print("  PASSED")

    print("Running Exercise 8: Gaussian Naive Bayes...")
    model8, acc8 = train_gaussian_naive_bayes(X_train, X_test, y_train, y_test)
    assert isinstance(model8, GaussianNB)
    assert acc8 >= 0.5
    print(f"  PASSED (Accuracy: {acc8:.4f})")

    print("Running Exercise 9: Naive Bayes Parameters...")
    priors9, means9 = naive_bayes_parameters(X_train, y_train)
    assert priors9.shape == (2,)
    assert means9.shape == (2, 5)
    print(f"  PASSED")

    print("Running Exercise 10: Classification Metrics...")
    y_pred10 = np.array([0, 1, 1, 0, 1])
    y_true10 = np.array([0, 1, 0, 0, 1])
    metrics10 = compute_metrics(y_true10, y_pred10)
    print(f"  PASSED: {metrics10}")

    print("Running Exercise 11: Confusion Matrix Analysis...")
    y_true11 = np.array([0, 1, 1, 0, 1, 0])
    y_pred11 = np.array([0, 1, 0, 0, 1, 1])
    cm11 = analyze_confusion_matrix(y_true11, y_pred11)
    print(f"  PASSED: {cm11}")

    print("Running Exercise 12: ROC-AUC...")
    y_true12 = np.array([0, 1, 1, 0, 1])
    y_proba12 = np.array([[0.9, 0.1], [0.2, 0.8], [0.3, 0.7],
                          [0.8, 0.2], [0.1, 0.9]])
    roc_auc12 = compute_roc_auc(y_true12, y_proba12)
    print(f"  PASSED: ROC-AUC={roc_auc12:.4f}")

    print("Running Exercise 13: Multi-Class Classification...")
    results13 = multi_class_classification()
    print(f"  PASSED: {results13}")

    print("Running Exercise 14: One-vs-Rest SVM...")
    model14, acc14 = one_vs_rest_svm()
    assert isinstance(model14, OneVsRestClassifier)
    assert acc14 > 0.8
    print(f"  PASSED (Accuracy: {acc14:.4f})")

    print("Running Exercise 15: Classification Report...")
    report15 = classification_report_multiclass()
    print(f"  PASSED")
    print("Report preview:")
    print(report15)

    print("\nAll exercises passed!")
