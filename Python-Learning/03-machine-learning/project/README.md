# End-to-End ML Pipeline Project

This project demonstrates a complete machine learning pipeline from data loading through model evaluation, with experiment tracking via MLflow.

## Project Overview

This is a production-style machine learning project that implements:
- Data loading and preprocessing
- Feature engineering with ColumnTransformer
- Multiple model training (Logistic Regression, Random Forest, Gradient Boosting)
- Cross-validation and hyperparameter tuning
- MLflow experiment tracking
- Model evaluation and comparison
- Reproducibility and configuration management

## Project Structure

```
project/
├── README.md           # Project documentation
├── config.py           # Configuration and hyperparameters
├── pipeline.py         # Main ML pipeline implementation
├── test_pipeline.py    # Unit tests
└── requirements.txt    # Python dependencies
```

## Files

### config.py
Defines configuration parameters using dataclasses:
- Dataset parameters
- Feature names
- Model hyperparameters
- Training parameters
- MLflow configuration

### pipeline.py
Main pipeline implementation containing:
- Data loading functions
- Preprocessing with ColumnTransformer
- Model training with multiple algorithms
- Cross-validation
- Evaluation metrics
- MLflow logging

### test_pipeline.py
Comprehensive test suite covering:
- Data loading and validation
- Preprocessing correctness
- Model training
- Evaluation metrics
- MLflow logging
- Pipeline end-to-end functionality

## Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Requirements
- scikit-learn >= 1.0
- pandas >= 1.3
- numpy >= 1.21
- mlflow >= 2.0
- pytest >= 7.0 (for testing)

## Usage

### Run the Pipeline
```python
from config import Config
from pipeline import Pipeline

config = Config()
pipeline = Pipeline(config)

# Load and preprocess data
X_train, X_test, y_train, y_test = pipeline.load_and_preprocess_data()

# Train models
results = pipeline.train_and_evaluate()

# View results
for model_name, metrics in results.items():
    print(f"{model_name}: {metrics}")
```

### Run Tests
```bash
pytest test_pipeline.py -v
```

### View MLflow UI
```bash
mlflow ui
```
Then open http://localhost:5000 in your browser.

## Key Features

### 1. Configuration Management
- Centralized configuration in `config.py`
- Dataclass-based configuration for type safety
- Easy modification of hyperparameters

### 2. Data Processing
- Automatic feature type detection
- Separate pipelines for numeric and categorical features
- SimpleImputer for missing values
- StandardScaler for numeric features
- OneHotEncoder for categorical features

### 3. Model Training
- Multiple algorithms for comparison
- Cross-validation for robust evaluation
- Hyperparameter optimization
- Feature importance analysis

### 4. Experiment Tracking
- MLflow integration
- Automatic parameter logging
- Metric tracking
- Model artifact storage
- Run comparison

### 5. Testing
- Unit tests for each component
- Integration tests for pipeline
- Data validation tests
- Model evaluation tests

## Example Workflow

```python
# 1. Load configuration
from config import Config
config = Config()

# 2. Create pipeline
from pipeline import Pipeline
pipeline = Pipeline(config)

# 3. Load and preprocess data
X_train, X_test, y_train, y_test = pipeline.load_and_preprocess_data()

# 4. Train models with MLflow tracking
results = pipeline.train_and_evaluate()

# 5. Analyze results
best_model = max(results, key=lambda x: results[x]['accuracy'])
print(f"Best model: {best_model}")
print(f"Best accuracy: {results[best_model]['accuracy']:.4f}")

# 6. View experiments
# Open MLflow UI: mlflow ui
```

## Results

The pipeline trains and compares three models:
- **Logistic Regression**: Fast, interpretable baseline
- **Random Forest**: Robust ensemble method
- **Gradient Boosting**: Strong predictive power

Each model's performance is logged to MLflow with:
- Hyperparameters
- Accuracy, Precision, Recall, F1 metrics
- Cross-validation scores
- Trained model artifacts

## Best Practices Implemented

1. **Reproducibility**: Fixed random seeds, saved configuration
2. **Code Organization**: Separation of concerns (config, pipeline, tests)
3. **Type Hints**: Full type annotations for clarity
4. **Documentation**: Docstrings and comments throughout
5. **Testing**: Comprehensive test coverage
6. **Logging**: MLflow tracking for reproducible experiments
7. **Configuration**: Centralized, easy-to-modify parameters
8. **Error Handling**: Validation and error messages

## Extensibility

The pipeline is designed to be easily extended:

### Add a New Model
```python
# In config.py
@dataclass
class Config:
    # ... existing config ...
    xgb_params = {
        'n_estimators': 100,
        'max_depth': 5,
        'learning_rate': 0.1
    }

# In pipeline.py
def train_xgboost(self):
    # Add XGBoost training logic
    pass
```

### Add New Features
```python
# In config.py
self.numeric_features = ['feature1', 'feature2', 'new_feature']

# In pipeline.py
# Preprocessing automatically handles new features
X_train, X_test = self.preprocess_data(...)
```

### Add Custom Evaluation
```python
# In pipeline.py
def evaluate_model(self, y_true, y_pred):
    # Add custom metrics
    custom_metric = compute_metric(y_true, y_pred)
    return custom_metric
```

## Notes

- Data is generated synthetically using `make_classification`
- All random operations use fixed seeds for reproducibility
- Cross-validation uses 5 folds by default
- Features are standardized for fair comparison
- MLflow tracks all experiments locally in `mlruns/`

## Troubleshooting

### MLflow Not Found
```bash
pip install mlflow
```

### Sklearn Version Issues
Ensure sklearn >= 1.0:
```bash
pip install --upgrade scikit-learn
```

### Test Failures
Run tests with verbose output:
```bash
pytest test_pipeline.py -v -s
```

## License

MIT License

## Author

Created as part of Python Learning Module 3: Machine Learning
