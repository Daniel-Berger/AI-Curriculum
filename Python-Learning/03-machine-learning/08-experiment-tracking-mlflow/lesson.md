# Module 08: Experiment Tracking with MLflow
## Experiments, Runs, Parameters, Metrics, Artifacts, and Model Registry

### Table of Contents
1. MLflow Overview
2. Experiments and Runs
3. Logging Parameters and Metrics
4. Artifacts and Model Artifacts
5. Autologging
6. MLflow UI
7. Model Registry
8. Best Practices

---

## 1. MLflow Overview

MLflow is an open-source platform for managing machine learning workflows. It provides tools for:
- **Experiment Tracking**: Log and compare experiments
- **Reproducibility**: Track code, data, and configuration
- **Model Management**: Package, version, and deploy models
- **Project Execution**: Define reproducible projects

### Installation
```bash
pip install mlflow
```

### Core Concepts
- **Experiment**: A collection of related runs
- **Run**: A single execution of model training with specific parameters and metrics
- **Artifact**: Any file associated with a run (model, plot, etc.)
- **Parameter**: Configuration value (immutable during run)
- **Metric**: Quantitative measurement (can change during run)

---

## 2. Experiments and Runs

### Setting Up Experiments
```python
import mlflow

# Get or create an experiment
experiment = mlflow.get_experiment_by_name("My First Experiment")
if experiment is None:
    exp_id = mlflow.create_experiment("My First Experiment")
else:
    exp_id = experiment.experiment_id

# Set active experiment
mlflow.set_experiment("My First Experiment")

# Get experiment info
experiment = mlflow.get_experiment(exp_id)
print(f"Experiment ID: {experiment.experiment_id}")
print(f"Experiment name: {experiment.name}")
print(f"Artifact location: {experiment.artifact_location}")
```

### Creating Runs
```python
import mlflow
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

mlflow.set_experiment("RandomForest Tuning")

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

# Start a new run
with mlflow.start_run():
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Get predictions and accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Log results
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", accuracy)

# Access run info
print(f"Run ID: {mlflow.active_run().info.run_id}")
```

### Run Context Management
```python
import mlflow

# Automatic cleanup with context manager
with mlflow.start_run() as run:
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("loss", 0.5)
    run_id = run.info.run_id

# Run is automatically ended

# Start run without context manager (must manually end)
mlflow.start_run()
try:
    mlflow.log_param("param", value)
    # Do work
finally:
    mlflow.end_run()

# Get current run info
run = mlflow.active_run()
print(f"Run ID: {run.info.run_id}")
print(f"Status: {run.info.status}")
```

---

## 3. Logging Parameters and Metrics

### Parameters
Parameters are configuration values logged once per run.

```python
import mlflow

with mlflow.start_run():
    # Log single parameter
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 5)

    # Log multiple parameters at once
    params = {
        "learning_rate": 0.01,
        "batch_size": 32,
        "epochs": 100
    }
    mlflow.log_params(params)
```

### Metrics
Metrics are quantitative measurements that can change during training.

```python
import mlflow
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

with mlflow.start_run():
    model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # Log single metric
    accuracy = accuracy_score(y_test, y_pred)
    mlflow.log_metric("accuracy", accuracy)

    # Log multiple metrics
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred)
    }
    mlflow.log_metrics(metrics)

    # Log metric step (for tracking evolution during training)
    for epoch in range(5):
        train_loss = 0.5 - (epoch * 0.1)  # Mock loss
        mlflow.log_metric("train_loss", train_loss, step=epoch)
```

### Tags
Tags are simple key-value pairs for organizing and searching experiments.

```python
import mlflow

with mlflow.start_run():
    mlflow.set_tag("model_type", "gradient_boosting")
    mlflow.set_tag("dataset", "iris")
    mlflow.set_tag("user", "alice")

    # Set multiple tags
    tags = {
        "version": "1.0",
        "release": "production"
    }
    mlflow.set_tags(tags)
```

---

## 4. Artifacts and Model Artifacts

### Logging Files
```python
import mlflow
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

with mlflow.start_run():
    # Log model parameters
    mlflow.log_param("n_estimators", 100)

    # Train model and generate outputs
    # ... (model training code)

    # Log a CSV file
    metrics_df = pd.DataFrame({
        "epoch": [1, 2, 3],
        "train_loss": [0.5, 0.3, 0.2],
        "val_loss": [0.6, 0.4, 0.3]
    })
    metrics_df.to_csv("metrics.csv", index=False)
    mlflow.log_artifact("metrics.csv")

    # Log a plot
    plt.figure(figsize=(8, 6))
    plt.plot([1, 2, 3], [0.5, 0.3, 0.2])
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.savefig("loss_curve.png")
    plt.close()
    mlflow.log_artifact("loss_curve.png")

    # Log confusion matrix
    y_test = np.array([0, 1, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 0, 1])
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(cm)
    disp.plot()
    plt.savefig("confusion_matrix.png")
    plt.close()
    mlflow.log_artifact("confusion_matrix.png")
```

### Logging Models
```python
import mlflow
from sklearn.ensemble import RandomForestClassifier

with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", model.score(X_test, y_test))

    # Log sklearn model
    mlflow.sklearn.log_model(model, "model")

    # Log TensorFlow model
    # mlflow.tensorflow.log_model(tf_model, "keras_model")

    # Log PyTorch model
    # mlflow.pytorch.log_model(torch_model, "pytorch_model")

    # Log Keras model
    # mlflow.keras.log_model(keras_model, "keras_model")
```

### Logging Directories
```python
import mlflow
import os

with mlflow.start_run():
    # Create a directory with multiple files
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/results.txt", "w") as f:
        f.write("Results summary")
    with open("outputs/report.csv", "w") as f:
        f.write("metric,value\naccuracy,0.95")

    # Log entire directory
    mlflow.log_artifacts("outputs")
```

---

## 5. Autologging

Autologging automatically captures parameters, metrics, and models without explicit logging calls.

### Framework Support
```python
import mlflow

# Enable autologging for specific frameworks
mlflow.sklearn.autolog()           # scikit-learn
mlflow.tensorflow.autolog()        # TensorFlow
mlflow.pytorch.autolog()           # PyTorch
mlflow.xgboost.autolog()           # XGBoost
mlflow.lightgbm.autolog()          # LightGBM
```

### Sklearn Autologging Example
```python
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Enable autologging
mlflow.sklearn.autolog()

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, random_state=42
)

with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    # Autologging captures:
    # - Parameters: n_estimators, max_depth, etc.
    # - Metrics: accuracy, f1, precision, recall, etc.
    # - Model artifacts: model.pkl
    # - Feature importance plot

# Access logged data
client = mlflow.tracking.MlflowClient()
run = mlflow.active_run()
print(f"Logged params: {run.data.params}")
print(f"Logged metrics: {run.data.metrics}")
```

### Custom Autologging Configuration
```python
import mlflow

# Configure what gets logged
mlflow.sklearn.autolog(
    log_input_examples=True,      # Log sample inputs
    log_model_signatures=True,    # Log input/output schema
    log_models=True,              # Log trained models
    log_datasets=True,            # Log training dataset metadata
    disable=False                 # Disable autologging
)
```

---

## 6. MLflow UI

The MLflow UI provides a web interface for exploring experiments and runs.

### Starting the UI
```bash
mlflow ui
```

The UI is available at `http://localhost:5000`

### UI Features
- **Experiment View**: Compare metrics, parameters across runs
- **Run View**: Detailed information about a single run
- **Comparison**: Side-by-side comparison of runs
- **Charts**: Visualize metrics evolution
- **Artifacts**: Browse and download logged artifacts

### Programmatic Access
```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Get all experiments
experiments = client.search_experiments()
for exp in experiments:
    print(f"Experiment: {exp.name}")

# Search runs
runs = client.search_runs(
    experiment_ids=[exp_id],
    filter_string="metrics.accuracy > 0.9",
    order_by=["metrics.accuracy DESC"]
)

for run in runs:
    print(f"Run ID: {run.info.run_id}")
    print(f"Parameters: {run.data.params}")
    print(f"Metrics: {run.data.metrics}")
    print(f"Tags: {run.data.tags}")
```

---

## 7. Model Registry

The MLflow Model Registry provides centralized model storage, versioning, and deployment.

### Registering Models
```python
import mlflow
from sklearn.ensemble import RandomForestClassifier

with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    mlflow.sklearn.log_model(model, "model")
    mlflow.log_metric("accuracy", model.score(X_test, y_test))

    # Register model to Model Registry
    model_uri = "runs:/{}/model".format(mlflow.active_run().info.run_id)
    mv = mlflow.register_model(model_uri, "RandomForest-Classifier")
    print(f"Model version: {mv.version}")
```

### Managing Model Versions
```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Get model information
model = client.get_registered_model("RandomForest-Classifier")
print(f"Model: {model.name}")
print(f"Versions: {[v.version for v in model.latest_versions]}")

# Transition model version
client.transition_model_version_stage(
    name="RandomForest-Classifier",
    version=1,
    stage="Production"
)

# Get latest production version
latest_prod = client.get_latest_model_version(
    name="RandomForest-Classifier",
    stages=["Production"]
)
print(f"Latest production version: {latest_prod.version}")

# Load model from registry
model_uri = "models:/RandomForest-Classifier/Production"
model = mlflow.pyfunc.load_model(model_uri)
predictions = model.predict(X_test)
```

### Model Stages
- **None**: Development/experimental
- **Staging**: Ready for testing
- **Production**: In production use
- **Archived**: No longer in use

---

## 8. Best Practices

### 1. Organize Experiments
```python
import mlflow

# Use descriptive experiment names
mlflow.set_experiment("ImageClassification/ResNet50/V1")

# Use tags for organization
with mlflow.start_run():
    mlflow.set_tag("team", "computer_vision")
    mlflow.set_tag("dataset", "cifar10")
    mlflow.set_tag("framework", "pytorch")
```

### 2. Log Meaningful Metrics
```python
import mlflow
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

with mlflow.start_run():
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted'),
        "recall": recall_score(y_test, y_pred, average='weighted'),
        "f1": f1_score(y_test, y_pred, average='weighted')
    }
    mlflow.log_metrics(metrics)
```

### 3. Use Runs for Hyperparameter Tuning
```python
import mlflow
from sklearn.model_selection import GridSearchCV

mlflow.set_experiment("Hyperparameter Tuning")

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15]
}

gs = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3)

for params in param_grid_iterator:  # Simplified
    with mlflow.start_run():
        model = RandomForestClassifier(**params, random_state=42)
        model.fit(X_train, y_train)
        mlflow.log_params(params)
        mlflow.log_metric("accuracy", model.score(X_test, y_test))
```

### 4. Log Artifacts for Reproducibility
```python
import mlflow

with mlflow.start_run():
    # Log training configuration
    config = {"data_version": "1.0", "preprocessing": "standard_scaling"}
    mlflow.log_params(config)

    # Log data statistics
    data_stats = {"train_size": len(X_train), "test_size": len(X_test)}
    mlflow.log_metrics(data_stats)

    # Log important plots
    plot_feature_importance(model, "feature_importance.png")
    mlflow.log_artifact("feature_importance.png")
```

### 5. Version Models in Registry
```python
import mlflow

# Always register production models
with mlflow.start_run():
    model = train_model()
    mlflow.sklearn.log_model(model, "model")

    if evaluate_model_quality(model) > threshold:
        model_uri = "runs:/{}/model".format(mlflow.active_run().info.run_id)
        mlflow.register_model(model_uri, "ProductionModel")
```

### 6. Use Experiment-Level Context
```python
import mlflow

def train_and_log_model(params):
    with mlflow.start_run():
        model = train_model(**params)
        mlflow.log_params(params)
        mlflow.log_metric("accuracy", evaluate(model))
        mlflow.sklearn.log_model(model, "model")

mlflow.set_experiment("Production Models")

# Run multiple experiments
for params in param_configs:
    train_and_log_model(params)
```

---

## Summary

MLflow provides comprehensive experiment tracking and model management:

1. **Experiments**: Organize related runs logically
2. **Runs**: Individual training executions with parameters and metrics
3. **Artifacts**: Store models, plots, and data alongside runs
4. **Autologging**: Automatic capture of metrics and models
5. **UI**: Web interface for exploring experiments
6. **Model Registry**: Centralized model management and versioning
7. **Best Practices**: Organization, reproducibility, and systematic tracking

Effective use of MLflow enables:
- Easy comparison of experiments
- Reproducible research
- Model version control
- Simplified deployment workflows
