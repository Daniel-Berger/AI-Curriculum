"""
Module 08: Experiment Tracking with MLflow - Solutions
========================================================
Complete implementations for all MLflow exercises.
"""

import os
import tempfile
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
from sklearn.datasets import make_classification
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

def create_and_get_experiment(experiment_name: str) -> Tuple[str, bool]:
    """Create an experiment and return its ID and existence flag."""
    existing_exp = mlflow.get_experiment_by_name(experiment_name)

    if existing_exp is None:
        exp_id = mlflow.create_experiment(experiment_name)
        exists = False
    else:
        exp_id = existing_exp.experiment_id
        exists = True

    return exp_id, exists


def start_and_end_run(experiment_name: str) -> str:
    """Create experiment, start run, and return run ID."""
    mlflow.set_experiment(experiment_name)

    mlflow.start_run()
    run_id = mlflow.active_run().info.run_id
    mlflow.end_run()

    return run_id


# =============================================================================
# LOGGING PARAMETERS AND METRICS
# =============================================================================

def log_param_and_metric(
    experiment_name: str,
    param_name: str, param_value: Any,
    metric_name: str, metric_value: float
) -> str:
    """Log a single parameter and metric, return run ID."""
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():
        mlflow.log_param(param_name, param_value)
        mlflow.log_metric(metric_name, metric_value)
        run_id = mlflow.active_run().info.run_id

    return run_id


def log_multiple_params_metrics(
    experiment_name: str,
    params: Dict[str, Any],
    metrics: Dict[str, float]
) -> str:
    """Log multiple parameters and metrics at once."""
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        run_id = mlflow.active_run().info.run_id

    return run_id


def log_tags(
    experiment_name: str,
    tags: Dict[str, str]
) -> str:
    """Log tags for a run, return run ID."""
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():
        mlflow.set_tags(tags)
        run_id = mlflow.active_run().info.run_id

    return run_id


# =============================================================================
# TRAINING AND LOGGING
# =============================================================================

def train_and_log_logistic_regression(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray,
    experiment_name: str
) -> str:
    """Train LogisticRegression and log parameters, metrics, and model."""
    mlflow.set_experiment(experiment_name)

    # Preprocess data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    with mlflow.start_run():
        # Train model
        model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        model.fit(X_train_scaled, y_train)

        # Log parameters
        mlflow.log_param("C", 1.0)
        mlflow.log_param("max_iter", 1000)

        # Get predictions and compute metrics
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='binary' if len(np.unique(y_test)) == 2 else 'weighted')

        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1", f1)

        # Log model
        mlflow.sklearn.log_model(model, "model")

        run_id = mlflow.active_run().info.run_id

    return run_id


def train_multiple_models_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray,
    experiment_name: str
) -> Dict[str, str]:
    """Train multiple models and return run IDs."""
    mlflow.set_experiment(experiment_name)

    # Preprocess data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}

    # Logistic Regression
    with mlflow.start_run(run_name="logistic_regression"):
        model_lr = LogisticRegression(random_state=42, max_iter=1000)
        model_lr.fit(X_train_scaled, y_train)

        y_pred = model_lr.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='binary' if len(np.unique(y_test)) == 2 else 'weighted')

        mlflow.log_param("model", "logistic_regression")
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1", f1)
        mlflow.sklearn.log_model(model_lr, "model")

        results['logistic_regression'] = mlflow.active_run().info.run_id

    # Random Forest
    with mlflow.start_run(run_name="random_forest"):
        model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
        model_rf.fit(X_train_scaled, y_train)

        y_pred = model_rf.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='binary' if len(np.unique(y_test)) == 2 else 'weighted')

        mlflow.log_param("model", "random_forest")
        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1", f1)
        mlflow.sklearn.log_model(model_rf, "model")

        results['random_forest'] = mlflow.active_run().info.run_id

    # Gradient Boosting
    with mlflow.start_run(run_name="gradient_boosting"):
        model_gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
        model_gb.fit(X_train_scaled, y_train)

        y_pred = model_gb.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='binary' if len(np.unique(y_test)) == 2 else 'weighted')

        mlflow.log_param("model", "gradient_boosting")
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("learning_rate", 0.1)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1", f1)
        mlflow.sklearn.log_model(model_gb, "model")

        results['gradient_boosting'] = mlflow.active_run().info.run_id

    return results


# =============================================================================
# ARTIFACTS
# =============================================================================

def log_text_artifact(
    experiment_name: str,
    text_content: str,
    filename: str
) -> str:
    """Log a text artifact."""
    mlflow.set_experiment(experiment_name)

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, filename)

        with open(filepath, 'w') as f:
            f.write(text_content)

        with mlflow.start_run():
            mlflow.log_artifact(filepath)
            run_id = mlflow.active_run().info.run_id

    return run_id


def log_csv_artifact(
    experiment_name: str,
    data_dict: Dict[str, list],
    csv_filename: str
) -> str:
    """Log a CSV artifact from dictionary."""
    mlflow.set_experiment(experiment_name)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create DataFrame and save to CSV
        df = pd.DataFrame(data_dict)
        csv_path = os.path.join(tmpdir, csv_filename)
        df.to_csv(csv_path, index=False)

        with mlflow.start_run():
            mlflow.log_artifact(csv_path)
            run_id = mlflow.active_run().info.run_id

    return run_id


def log_directory_artifacts(
    experiment_name: str,
    artifacts_dict: Dict[str, str]
) -> str:
    """Log multiple artifacts from a directory."""
    mlflow.set_experiment(experiment_name)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write all files to temp directory
        for filename, content in artifacts_dict.items():
            filepath = os.path.join(tmpdir, filename)
            with open(filepath, 'w') as f:
                f.write(content)

        with mlflow.start_run():
            mlflow.log_artifacts(tmpdir)
            run_id = mlflow.active_run().info.run_id

    return run_id


# =============================================================================
# AUTOLOGGING
# =============================================================================

def train_with_autologging(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray,
    experiment_name: str
) -> str:
    """Enable sklearn autologging, train RandomForest, return run ID."""
    # Enable autologging
    mlflow.sklearn.autolog()

    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)

        # Autologging captures parameters, metrics, and model automatically
        run_id = mlflow.active_run().info.run_id

    return run_id


# =============================================================================
# TRACKING CLIENT AND QUERYING
# =============================================================================

def get_best_run_by_metric(
    experiment_name: str,
    metric_name: str,
    direction: str = "max"
) -> Tuple[str, float]:
    """Get the best run in experiment by a metric."""
    client = MlflowClient()

    # Get experiment ID
    exp = mlflow.get_experiment_by_name(experiment_name)
    if exp is None:
        return "", 0.0

    exp_id = exp.experiment_id

    # Search runs
    try:
        runs = client.search_runs(
            experiment_ids=[exp_id],
            order_by=[f"metrics.{metric_name} {'DESC' if direction == 'max' else 'ASC'}"]
        )
    except Exception:
        return "", 0.0

    if not runs:
        return "", 0.0

    best_run = runs[0]
    run_id = best_run.info.run_id
    metric_value = best_run.data.metrics.get(metric_name, 0.0)

    return run_id, metric_value


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    print("Running Exercise 1: Create and Get Experiment...")
    exp_id1, exists1 = create_and_get_experiment("sol_ex1_test_exp")
    assert len(exp_id1) > 0
    assert isinstance(exists1, bool)
    print("  PASSED")

    print("Running Exercise 2: Start and End Run...")
    run_id2 = start_and_end_run("sol_ex2_test_exp")
    assert len(run_id2) > 0
    print("  PASSED")

    print("Running Exercise 3: Log Single Parameter and Metric...")
    run_id3 = log_param_and_metric("sol_ex3_test_exp", "learning_rate", 0.01, "accuracy", 0.95)
    assert len(run_id3) > 0
    print("  PASSED")

    print("Running Exercise 4: Log Multiple Parameters and Metrics...")
    params4 = {"lr": 0.01, "batch_size": 32}
    metrics4 = {"train_acc": 0.9, "val_acc": 0.85}
    run_id4 = log_multiple_params_metrics("sol_ex4_test_exp", params4, metrics4)
    assert len(run_id4) > 0
    print("  PASSED")

    print("Running Exercise 5: Log Tags...")
    tags5 = {"model": "rf", "version": "1.0"}
    run_id5 = log_tags("sol_ex5_test_exp", tags5)
    assert len(run_id5) > 0
    print("  PASSED")

    print("Running Exercise 6: Train and Log Model...")
    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    run_id6 = train_and_log_logistic_regression(X_train, X_test, y_train, y_test, "sol_ex6_test_exp")
    assert len(run_id6) > 0
    print("  PASSED")

    print("Running Exercise 7: Train Multiple Models...")
    results7 = train_multiple_models_comparison(X_train, X_test, y_train, y_test, "sol_ex7_test_exp")
    assert len(results7) == 3
    print("  PASSED")

    print("Running Exercise 8: Log Text Artifact...")
    run_id8 = log_text_artifact("sol_ex8_test_exp", "Model report content", "report.txt")
    assert len(run_id8) > 0
    print("  PASSED")

    print("Running Exercise 9: Log CSV Artifact...")
    data9 = {"epoch": [1, 2, 3], "loss": [0.5, 0.3, 0.2]}
    run_id9 = log_csv_artifact("sol_ex9_test_exp", data9, "metrics.csv")
    assert len(run_id9) > 0
    print("  PASSED")

    print("Running Exercise 10: Log Directory Artifacts...")
    artifacts10 = {"file1.txt": "content1", "file2.txt": "content2"}
    run_id10 = log_directory_artifacts("sol_ex10_test_exp", artifacts10)
    assert len(run_id10) > 0
    print("  PASSED")

    print("Running Exercise 11: Train with Autologging...")
    run_id11 = train_with_autologging(X_train, X_test, y_train, y_test, "sol_ex11_test_exp")
    assert len(run_id11) > 0
    print("  PASSED")

    print("Running Exercise 12: Get Best Run by Metric...")
    run_id12, value12 = get_best_run_by_metric("sol_ex6_test_exp", "accuracy", "max")
    print(f"  PASSED (Best run: {run_id12}, value: {value12})")

    print("\nAll exercises passed!")
