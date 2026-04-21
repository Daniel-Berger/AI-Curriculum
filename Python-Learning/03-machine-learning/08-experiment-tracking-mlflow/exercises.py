"""
Module 08: Experiment Tracking with MLflow - Exercises
========================================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- If no AssertionError is raised, your solution is correct.

Note: Requires MLflow installation: pip install mlflow

Difficulty levels:
  Easy   - Direct MLflow API usage
  Medium - Requires setup and parameter/metric logging
  Hard   - Requires artifact handling or advanced features
"""

import os
import tempfile
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
import mlflow
from sklearn.datasets import make_classification, load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score
import warnings
warnings.filterwarnings('ignore')


# =============================================================================
# EXPERIMENT SETUP
# =============================================================================

# Exercise 1: Create and Get Experiment
# Difficulty: Easy
def create_and_get_experiment(experiment_name: str) -> Tuple[str, bool]:
    """Create an experiment and return its ID and existence flag.

    If experiment already exists, get its ID.
    Return (experiment_id, experiment_exists).

    Args:
        experiment_name: Name of the experiment to create/get.

    Returns:
        Tuple of (experiment_id_string, experiment_exists_bool).

    >>> exp_id, exists = create_and_get_experiment("test_exp_123")
    >>> len(exp_id) > 0
    True
    >>> isinstance(exists, bool)
    True
    """
    pass


# Exercise 2: Start and End Run
# Difficulty: Easy
def start_and_end_run(experiment_name: str) -> str:
    """Create experiment, start run, and return run ID.

    Use mlflow.start_run() and mlflow.end_run().
    Return the run ID.

    Args:
        experiment_name: Name of the experiment.

    Returns:
        Run ID as string.

    >>> run_id = start_and_end_run("test_run_123")
    >>> len(run_id) > 0
    True
    """
    pass


# =============================================================================
# LOGGING PARAMETERS AND METRICS
# =============================================================================

# Exercise 3: Log Single Parameter and Metric
# Difficulty: Easy
def log_param_and_metric(
    experiment_name: str,
    param_name: str, param_value: Any,
    metric_name: str, metric_value: float
) -> str:
    """Log a single parameter and metric, return run ID.

    Args:
        experiment_name: Name of experiment.
        param_name, param_value: Parameter to log.
        metric_name, metric_value: Metric to log.

    Returns:
        Run ID as string.

    >>> run_id = log_param_and_metric("test", "lr", 0.01, "acc", 0.95)
    >>> len(run_id) > 0
    True
    """
    pass


# Exercise 4: Log Multiple Parameters and Metrics
# Difficulty: Medium
def log_multiple_params_metrics(
    experiment_name: str,
    params: Dict[str, Any],
    metrics: Dict[str, float]
) -> str:
    """Log multiple parameters and metrics at once.

    Use mlflow.log_params() and mlflow.log_metrics().
    Return run ID.

    Args:
        experiment_name: Name of experiment.
        params: Dict of parameters.
        metrics: Dict of metrics.

    Returns:
        Run ID as string.

    >>> params = {"lr": 0.01, "batch_size": 32}
    >>> metrics = {"train_acc": 0.9, "val_acc": 0.85}
    >>> run_id = log_multiple_params_metrics("test", params, metrics)
    >>> len(run_id) > 0
    True
    """
    pass


# Exercise 5: Log Tags
# Difficulty: Easy
def log_tags(
    experiment_name: str,
    tags: Dict[str, str]
) -> str:
    """Log tags for a run, return run ID.

    Use mlflow.set_tag() or mlflow.set_tags().

    Args:
        experiment_name: Name of experiment.
        tags: Dict of tags.

    Returns:
        Run ID as string.

    >>> tags = {"model": "rf", "version": "1.0"}
    >>> run_id = log_tags("test", tags)
    >>> len(run_id) > 0
    True
    """
    pass


# =============================================================================
# TRAINING AND LOGGING
# =============================================================================

# Exercise 6: Train and Log Model
# Difficulty: Medium
def train_and_log_logistic_regression(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray,
    experiment_name: str
) -> str:
    """Train LogisticRegression and log parameters, metrics, and model.

    Log C=1.0, max_iter=1000.
    Log accuracy and f1 metrics.
    Use mlflow.sklearn.log_model() to log the fitted model.
    Use StandardScaler for preprocessing.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.
        experiment_name: Name of experiment.

    Returns:
        Run ID as string.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> run_id = train_and_log_logistic_regression(X_tr, X_te, y_tr, y_te, "test")
    >>> len(run_id) > 0
    True
    """
    pass


# Exercise 7: Train Multiple Models and Compare
# Difficulty: Medium
def train_multiple_models_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray,
    experiment_name: str
) -> Dict[str, str]:
    """Train LogisticRegression, RandomForest, GradientBoosting.

    For each model, create a separate run with:
    - Model parameters logged
    - Test accuracy and f1 metrics logged
    - Model logged

    Return dict with keys 'logistic_regression', 'random_forest', 'gradient_boosting'
    mapping to run IDs.

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.
        experiment_name: Name of experiment.

    Returns:
        Dict mapping model names to run IDs.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> results = train_multiple_models_comparison(X_tr, X_te, y_tr, y_te, "test")
    >>> len(results) == 3
    True
    """
    pass


# =============================================================================
# ARTIFACTS
# =============================================================================

# Exercise 8: Log Text Artifact
# Difficulty: Medium
def log_text_artifact(
    experiment_name: str,
    text_content: str,
    filename: str
) -> str:
    """Log a text artifact.

    Create temporary file, write text_content, log as artifact.
    Return run ID.

    Args:
        experiment_name: Name of experiment.
        text_content: Text to save.
        filename: Name for the artifact file.

    Returns:
        Run ID as string.

    >>> content = "Model performance report"
    >>> run_id = log_text_artifact("test", content, "report.txt")
    >>> len(run_id) > 0
    True
    """
    pass


# Exercise 9: Log CSV Artifact
# Difficulty: Medium
def log_csv_artifact(
    experiment_name: str,
    data_dict: Dict[str, list],
    csv_filename: str
) -> str:
    """Log a CSV artifact from dictionary.

    Create DataFrame from dict, save to CSV, log as artifact.
    Return run ID.

    Args:
        experiment_name: Name of experiment.
        data_dict: Dict with column names as keys, lists as values.
        csv_filename: Name for the CSV file.

    Returns:
        Run ID as string.

    >>> data = {"epoch": [1, 2], "loss": [0.5, 0.3]}
    >>> run_id = log_csv_artifact("test", data, "metrics.csv")
    >>> len(run_id) > 0
    True
    """
    pass


# Exercise 10: Log Directory Artifacts
# Difficulty: Hard
def log_directory_artifacts(
    experiment_name: str,
    artifacts_dict: Dict[str, str]
) -> str:
    """Log multiple artifacts from a directory.

    Create temp directory, write files from artifacts_dict, log directory.
    Return run ID.

    artifacts_dict: {filename: content} pairs

    Args:
        experiment_name: Name of experiment.
        artifacts_dict: Dict mapping filenames to content.

    Returns:
        Run ID as string.

    >>> artifacts = {"file1.txt": "content1", "file2.txt": "content2"}
    >>> run_id = log_directory_artifacts("test", artifacts)
    >>> len(run_id) > 0
    True
    """
    pass


# =============================================================================
# AUTOLOGGING
# =============================================================================

# Exercise 11: Enable Autologging
# Difficulty: Easy
def train_with_autologging(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray,
    experiment_name: str
) -> str:
    """Enable sklearn autologging, train RandomForest, return run ID.

    Use mlflow.sklearn.autolog() before training.
    Train RandomForestClassifier(n_estimators=10, random_state=42).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.
        experiment_name: Name of experiment.

    Returns:
        Run ID as string.

    >>> X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    >>> X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)
    >>> run_id = train_with_autologging(X_tr, X_te, y_tr, y_te, "test")
    >>> len(run_id) > 0
    True
    """
    pass


# =============================================================================
# TRACKING CLIENT AND QUERYING
# =============================================================================

# Exercise 12: Query Runs from Experiment
# Difficulty: Hard
def get_best_run_by_metric(
    experiment_name: str,
    metric_name: str,
    direction: str = "max"
) -> Tuple[str, float]:
    """Get the best run in experiment by a metric.

    Use MlflowClient to search runs.
    direction: "max" for higher is better, "min" for lower is better.
    Return (run_id, metric_value).

    If no runs found, return ("", 0.0).

    Args:
        experiment_name: Name of experiment to search.
        metric_name: Metric to optimize.
        direction: "max" or "min".

    Returns:
        Tuple of (run_id, metric_value).

    >>> # This requires runs to have been logged first
    >>> run_id, value = get_best_run_by_metric("nonexistent", "accuracy")
    >>> run_id == "" or len(run_id) > 0
    True
    """
    pass


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    print("Running Exercise 1: Create and Get Experiment...")
    exp_id1, exists1 = create_and_get_experiment("ex1_test_exp")
    assert len(exp_id1) > 0
    assert isinstance(exists1, bool)
    print("  PASSED")

    print("Running Exercise 2: Start and End Run...")
    run_id2 = start_and_end_run("ex2_test_exp")
    assert len(run_id2) > 0
    print("  PASSED")

    print("Running Exercise 3: Log Single Parameter and Metric...")
    run_id3 = log_param_and_metric("ex3_test_exp", "learning_rate", 0.01, "accuracy", 0.95)
    assert len(run_id3) > 0
    print("  PASSED")

    print("Running Exercise 4: Log Multiple Parameters and Metrics...")
    params4 = {"lr": 0.01, "batch_size": 32}
    metrics4 = {"train_acc": 0.9, "val_acc": 0.85}
    run_id4 = log_multiple_params_metrics("ex4_test_exp", params4, metrics4)
    assert len(run_id4) > 0
    print("  PASSED")

    print("Running Exercise 5: Log Tags...")
    tags5 = {"model": "rf", "version": "1.0"}
    run_id5 = log_tags("ex5_test_exp", tags5)
    assert len(run_id5) > 0
    print("  PASSED")

    print("Running Exercise 6: Train and Log Model...")
    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    run_id6 = train_and_log_logistic_regression(X_train, X_test, y_train, y_test, "ex6_test_exp")
    assert len(run_id6) > 0
    print("  PASSED")

    print("Running Exercise 7: Train Multiple Models...")
    results7 = train_multiple_models_comparison(X_train, X_test, y_train, y_test, "ex7_test_exp")
    assert len(results7) == 3
    assert all(k in results7 for k in ['logistic_regression', 'random_forest', 'gradient_boosting'])
    print("  PASSED")

    print("Running Exercise 8: Log Text Artifact...")
    run_id8 = log_text_artifact("ex8_test_exp", "Model report content", "report.txt")
    assert len(run_id8) > 0
    print("  PASSED")

    print("Running Exercise 9: Log CSV Artifact...")
    data9 = {"epoch": [1, 2, 3], "loss": [0.5, 0.3, 0.2]}
    run_id9 = log_csv_artifact("ex9_test_exp", data9, "metrics.csv")
    assert len(run_id9) > 0
    print("  PASSED")

    print("Running Exercise 10: Log Directory Artifacts...")
    artifacts10 = {"file1.txt": "content1", "file2.txt": "content2"}
    run_id10 = log_directory_artifacts("ex10_test_exp", artifacts10)
    assert len(run_id10) > 0
    print("  PASSED")

    print("Running Exercise 11: Train with Autologging...")
    run_id11 = train_with_autologging(X_train, X_test, y_train, y_test, "ex11_test_exp")
    assert len(run_id11) > 0
    print("  PASSED")

    print("Running Exercise 12: Get Best Run by Metric...")
    run_id12, value12 = get_best_run_by_metric("ex6_test_exp", "accuracy", "max")
    print(f"  PASSED (Best run: {run_id12}, value: {value12})")

    print("\nAll exercises passed!")
