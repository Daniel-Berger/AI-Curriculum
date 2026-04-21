# Module 07: sklearn Pipelines

## Table of Contents

1. [Why Pipelines Matter](#1-why-pipelines-matter)
2. [The Pipeline Class](#2-the-pipeline-class)
3. [ColumnTransformer](#3-columntransformer)
4. [FeatureUnion](#4-featureunion)
5. [Custom Transformers](#5-custom-transformers)
6. [Combining Preprocessing and Models](#6-combining-preprocessing-and-models)
7. [Pipelines with Cross-Validation](#7-pipelines-with-cross-validation)
8. [Pipeline Serialization](#8-pipeline-serialization)
9. [Reusable Preprocessing Pipelines](#9-reusable-preprocessing-pipelines)
10. [Best Practices for Production](#10-best-practices-for-production)

---

## 1. Why Pipelines Matter

### The Data Leakage Problem

Without pipelines, it is dangerously easy to introduce **data leakage** -- information from
the test set leaking into training through preprocessing steps.

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris

# BAD -- data leakage!
iris = load_iris()
X, y = iris.data, iris.target

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)          # fit on ALL data (including test!)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, random_state=42)

# GOOD -- no leakage
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # fit only on train
X_test_scaled = scaler.transform(X_test)         # transform test with train stats
```

### Why Pipelines Are Better

Pipelines solve this automatically by ensuring:

1. **No data leakage**: `.fit()` only touches training data.
2. **Reproducibility**: the entire workflow is a single object.
3. **Cleaner code**: no manual intermediate variables.
4. **Easy serialization**: save the whole pipeline as one file.
5. **Grid search compatibility**: tune preprocessing + model together.

### Swift Analogy

Think of a pipeline like a `Combine` publisher chain in SwiftUI. Each operator transforms
the data and passes it downstream. The chain is defined once, reused many times, and the
order is guaranteed. A sklearn Pipeline is the same idea for ML workflows.

---

## 2. The Pipeline Class

### Basic Pipeline

```python
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Explicit Pipeline with named steps
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42, max_iter=1000))
])

# fit calls scaler.fit_transform() then classifier.fit()
pipe.fit(X_train, y_train)

# predict calls scaler.transform() then classifier.predict()
accuracy = pipe.score(X_test, y_test)
print(f"Pipeline accuracy: {accuracy:.3f}")
```

### make_pipeline -- Shortcut

`make_pipeline` auto-generates step names from class names.

```python
# Equivalent, but step names are auto-generated
pipe_auto = make_pipeline(
    StandardScaler(),
    LogisticRegression(random_state=42, max_iter=1000)
)

# Step names: 'standardscaler', 'logisticregression'
print(pipe_auto.named_steps)
```

### Accessing Pipeline Steps

```python
# Access by name
scaler_step = pipe.named_steps['scaler']
print(f"Scaler mean: {scaler_step.mean_}")

# Access by index
first_step = pipe[0]
last_step = pipe[-1]

# Get intermediate results
X_scaled = pipe[:-1].transform(X_test)  # everything except the last step
print(f"Scaled shape: {X_scaled.shape}")
```

---

## 3. ColumnTransformer

Real-world data has mixed column types: numeric features need scaling, categorical features
need encoding. `ColumnTransformer` applies different transformers to different columns.

### Basic ColumnTransformer

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Create sample mixed-type data
data = pd.DataFrame({
    'age': [25, 30, np.nan, 45, 35],
    'income': [50000, 60000, 75000, np.nan, 55000],
    'city': ['NYC', 'LA', 'NYC', 'SF', 'LA'],
    'education': ['BS', 'MS', 'PhD', 'BS', 'MS'],
})
y_sample = np.array([0, 1, 1, 0, 1])

numeric_features = ['age', 'income']
categorical_features = ['city', 'education']

# Define column-specific preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
        ]), numeric_features),
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
        ]), categorical_features),
    ]
)

# Transform
X_processed = preprocessor.fit_transform(data)
print(f"Output shape: {X_processed.shape}")
print(f"Output feature names: {preprocessor.get_feature_names_out()}")
```

### ColumnTransformer Options

```python
# remainder='passthrough' keeps untransformed columns
# remainder='drop' (default) drops them

preprocessor_pass = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
    ],
    remainder='passthrough'  # keep categorical columns as-is
)
```

### Full Pipeline with ColumnTransformer

```python
full_pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(random_state=42, max_iter=1000))
])

full_pipe.fit(data, y_sample)
predictions = full_pipe.predict(data)
print(f"Predictions: {predictions}")
```

---

## 4. FeatureUnion

`FeatureUnion` runs multiple transformers in parallel and concatenates their outputs
horizontally. This is useful when you want to create multiple feature representations
of the same data.

```python
from sklearn.pipeline import FeatureUnion
from sklearn.decomposition import PCA
from sklearn.preprocessing import PolynomialFeatures

# Create two different feature representations and combine them
feature_union = FeatureUnion([
    ('pca', PCA(n_components=2)),
    ('poly', PolynomialFeatures(degree=2, include_bias=False)),
])

# Pipeline with FeatureUnion
pipe_fu = Pipeline([
    ('scaler', StandardScaler()),
    ('features', feature_union),
    ('classifier', LogisticRegression(random_state=42, max_iter=1000)),
])

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, random_state=42
)

pipe_fu.fit(X_train, y_train)
print(f"FeatureUnion pipeline accuracy: {pipe_fu.score(X_test, y_test):.3f}")

# Check the combined feature count
X_combined = pipe_fu.named_steps['features'].transform(
    pipe_fu.named_steps['scaler'].transform(X_test)
)
print(f"Combined features: {X_combined.shape[1]}")
# 2 (PCA) + 14 (degree-2 polynomial of 4 features) = 16
```

---

## 5. Custom Transformers

Sometimes you need preprocessing steps that sklearn does not provide out of the box.
Custom transformers let you plug any Python logic into a pipeline.

### Using BaseEstimator and TransformerMixin

```python
from sklearn.base import BaseEstimator, TransformerMixin

class OutlierClipper(BaseEstimator, TransformerMixin):
    """Clip outliers to percentile bounds.

    This is a custom transformer that clips feature values to the
    specified lower and upper percentiles.
    """

    def __init__(self, lower_percentile: float = 1.0, upper_percentile: float = 99.0):
        self.lower_percentile = lower_percentile
        self.upper_percentile = upper_percentile

    def fit(self, X, y=None):
        """Compute percentile bounds from training data."""
        X_array = np.asarray(X)
        self.lower_bounds_ = np.percentile(X_array, self.lower_percentile, axis=0)
        self.upper_bounds_ = np.percentile(X_array, self.upper_percentile, axis=0)
        return self

    def transform(self, X):
        """Clip values to the learned bounds."""
        X_array = np.asarray(X).copy()
        X_clipped = np.clip(X_array, self.lower_bounds_, self.upper_bounds_)
        return X_clipped


# Use in a pipeline
pipe_custom = Pipeline([
    ('clipper', OutlierClipper(lower_percentile=5, upper_percentile=95)),
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42, max_iter=1000)),
])

pipe_custom.fit(X_train, y_train)
print(f"Custom pipeline accuracy: {pipe_custom.score(X_test, y_test):.3f}")
```

### Key Rules for Custom Transformers

1. **Inherit from `BaseEstimator` and `TransformerMixin`**.
2. **`__init__` parameters must match instance attributes** -- sklearn uses this for
   `get_params()` and `set_params()` (needed for grid search).
3. **`fit()` must return `self`** -- this enables method chaining.
4. **`transform()` must return an array-like** -- numpy array or sparse matrix.
5. **Do not store training data** -- only store learned statistics.

### FunctionTransformer for Simple Cases

```python
from sklearn.preprocessing import FunctionTransformer

# Quick-and-dirty custom transform
log_transformer = FunctionTransformer(
    func=np.log1p,          # transform
    inverse_func=np.expm1,  # inverse_transform
    validate=True
)

pipe_log = Pipeline([
    ('log', log_transformer),
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42, max_iter=1000)),
])
```

---

## 6. Combining Preprocessing and Models

### Complete Pipeline Example

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# Swap models easily -- preprocessing stays the same
models = {
    'logreg': LogisticRegression(random_state=42, max_iter=1000),
    'rf': RandomForestClassifier(random_state=42, n_estimators=100),
    'svm': SVC(random_state=42),
}

preprocessor_simple = Pipeline([
    ('clipper', OutlierClipper()),
    ('scaler', StandardScaler()),
])

for name, model in models.items():
    pipe = Pipeline([
        ('preprocessing', preprocessor_simple),
        ('model', model),
    ])
    pipe.fit(X_train, y_train)
    score = pipe.score(X_test, y_test)
    print(f"{name:10s}: accuracy = {score:.3f}")
```

---

## 7. Pipelines with Cross-Validation

Pipelines integrate seamlessly with cross-validation and grid search. The key benefit:
**preprocessing is correctly re-fit on each fold's training set**.

### Cross-Validation

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold

pipe_cv = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42, max_iter=1000)),
])

scores = cross_val_score(
    pipe_cv,
    iris.data, iris.target,
    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
    scoring='accuracy'
)
print(f"CV scores: {scores}")
print(f"Mean: {scores.mean():.3f} +/- {scores.std():.3f}")
```

### Grid Search with Pipeline Parameters

Access nested parameters using the `step_name__param_name` syntax:

```python
from sklearn.model_selection import GridSearchCV

pipe_gs = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(random_state=42)),
])

# Note the double underscore: step_name__param_name
param_grid = {
    'classifier__n_estimators': [50, 100, 200],
    'classifier__max_depth': [3, 5, 10, None],
}

grid = GridSearchCV(pipe_gs, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
grid.fit(iris.data, iris.target)

print(f"Best params: {grid.best_params_}")
print(f"Best score:  {grid.best_score_:.3f}")
```

### Tuning Preprocessing Hyperparameters Too

```python
param_grid_full = {
    'clipper__lower_percentile': [1, 5],
    'clipper__upper_percentile': [95, 99],
    'classifier__n_estimators': [50, 100],
    'classifier__max_depth': [5, 10],
}

pipe_full_gs = Pipeline([
    ('clipper', OutlierClipper()),
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(random_state=42)),
])

grid_full = GridSearchCV(pipe_full_gs, param_grid_full, cv=5, scoring='accuracy')
grid_full.fit(iris.data, iris.target)
print(f"Best params: {grid_full.best_params_}")
```

---

## 8. Pipeline Serialization

### Saving with joblib (Recommended)

```python
import joblib

# Save
joblib.dump(pipe_cv, 'model_pipeline.joblib')

# Load
loaded_pipe = joblib.load('model_pipeline.joblib')
predictions = loaded_pipe.predict(X_test)
print(f"Loaded pipeline accuracy: {loaded_pipe.score(X_test, y_test):.3f}")
```

### Saving with pickle

```python
import pickle

# Save
with open('model_pipeline.pkl', 'wb') as f:
    pickle.dump(pipe_cv, f)

# Load
with open('model_pipeline.pkl', 'rb') as f:
    loaded_pipe_pkl = pickle.load(f)
```

### joblib vs. pickle

| Feature | joblib | pickle |
|---------|--------|--------|
| Speed with numpy arrays | Faster (compressed) | Slower |
| File size | Smaller | Larger |
| Recommended for sklearn | Yes | No |
| Compatibility | sklearn objects | Any Python object |

### Security Warning

> **Never load a pipeline from an untrusted source.** Both joblib and pickle can execute
> arbitrary code during deserialization. This is similar to how you would never run an
> unsigned `.ipa` from an unknown source.

---

## 9. Reusable Preprocessing Pipelines

### Template Pattern

Create reusable preprocessing recipes that can be paired with different models:

```python
def create_preprocessing_pipeline(
    numeric_features: list[str],
    categorical_features: list[str],
    clip_outliers: bool = True
) -> ColumnTransformer:
    """Create a reusable preprocessing pipeline.

    Args:
        numeric_features: List of numeric column names.
        categorical_features: List of categorical column names.
        clip_outliers: Whether to clip outliers before scaling.

    Returns:
        A ColumnTransformer ready for use in a Pipeline.
    """
    numeric_steps = []
    if clip_outliers:
        numeric_steps.append(('clipper', OutlierClipper()))
    numeric_steps.extend([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])

    categorical_steps = [
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
    ]

    return ColumnTransformer(
        transformers=[
            ('num', Pipeline(numeric_steps), numeric_features),
            ('cat', Pipeline(categorical_steps), categorical_features),
        ]
    )


# Usage
preprocessor = create_preprocessing_pipeline(
    numeric_features=['age', 'income'],
    categorical_features=['city', 'education']
)

# Pair with any model
for model_name, model in models.items():
    pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model),
    ])
    # pipe.fit(X_train, y_train) ...
```

---

## 10. Best Practices for Production

### Checklist

1. **Always use pipelines** -- never scale/encode outside a pipeline.
2. **Name your steps** explicitly for clarity and grid search compatibility.
3. **Use `ColumnTransformer`** for mixed-type data -- it prevents you from accidentally
   one-hot encoding numeric features.
4. **Save the entire pipeline** -- not just the model. The preprocessing must match.
5. **Version your pipelines** -- include a version number or hash in the filename.
6. **Test with `clone()`** -- `sklearn.base.clone()` ensures your pipeline can be
   reinstantiated from parameters (needed for cross-validation).
7. **Use `set_output(transform='pandas')`** to preserve column names through the pipeline
   (sklearn 1.2+).

### Preserving Column Names (sklearn 1.2+)

```python
# Enable pandas output throughout the pipeline
pipe_pandas = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42, max_iter=1000)),
]).set_output(transform='pandas')

# Now intermediate transforms return DataFrames instead of numpy arrays
```

### Common Pipeline Anti-Patterns

| Anti-Pattern | Problem | Solution |
|-------------|---------|----------|
| Scaling before split | Data leakage | Put scaler in pipeline |
| Fitting imputer on full dataset | Data leakage | Put imputer in pipeline |
| Separate preprocessing file | Hard to keep in sync | Single pipeline object |
| Saving model without scaler | Inference fails | Save entire pipeline |
| Hardcoded column indices | Breaks when columns change | Use column names with ColumnTransformer |

---

## Summary

| Concept | Key Takeaway |
|---------|-------------|
| Pipeline | Chain preprocessing + model into a single object |
| make_pipeline | Shortcut that auto-names steps |
| ColumnTransformer | Different transforms for different column types |
| FeatureUnion | Parallel feature extraction, concatenated horizontally |
| Custom Transformers | Inherit BaseEstimator + TransformerMixin |
| Pipeline + GridSearch | Use `step__param` syntax; prevents data leakage |
| Serialization | Use joblib; save the whole pipeline |
| Production | Always pipeline, version, test with clone |
