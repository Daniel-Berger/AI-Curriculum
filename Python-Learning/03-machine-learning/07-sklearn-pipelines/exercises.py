"""
Module 07: sklearn Pipelines - Exercises
=========================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- If no AssertionError is raised, your solution is correct.

Difficulty levels:
  Easy   - Direct pipeline construction
  Medium - Requires ColumnTransformer or custom logic
  Hard   - Custom transformers, serialization, or combining concepts
"""

import os
import tempfile
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, make_pipeline, FeatureUnion
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split
from sklearn.datasets import load_iris


# =============================================================================
# BASIC PIPELINES
# =============================================================================

# Exercise 1: Simple Pipeline
# Difficulty: Easy
# Create a pipeline with StandardScaler followed by LogisticRegression.
def create_basic_pipeline() -> Pipeline:
    """Create a pipeline: StandardScaler -> LogisticRegression.

    Use LogisticRegression(random_state=42, max_iter=1000).
    Use named steps: 'scaler' and 'classifier'.

    Returns:
        A sklearn Pipeline object (unfitted).

    >>> pipe = create_basic_pipeline()
    >>> list(pipe.named_steps.keys())
    ['scaler', 'classifier']
    """
    pass


# Exercise 2: make_pipeline Shortcut
# Difficulty: Easy
# Create the same pipeline using make_pipeline (auto-named steps).
def create_auto_pipeline() -> Pipeline:
    """Create a pipeline using make_pipeline: StandardScaler -> LogisticRegression.

    Use LogisticRegression(random_state=42, max_iter=1000).

    Returns:
        A sklearn Pipeline object with auto-generated step names.

    >>> pipe = create_auto_pipeline()
    >>> 'standardscaler' in pipe.named_steps
    True
    >>> 'logisticregression' in pipe.named_steps
    True
    """
    pass


# Exercise 3: Fit and Score Pipeline
# Difficulty: Easy
# Fit a pipeline on training data and return the test accuracy.
def fit_and_score_pipeline(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> float:
    """Create, fit, and score a StandardScaler + LogisticRegression pipeline.

    Use LogisticRegression(random_state=42, max_iter=1000).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Test accuracy as a float.

    >>> iris = load_iris()
    >>> X_tr, X_te, y_tr, y_te = train_test_split(
    ...     iris.data, iris.target, random_state=42)
    >>> score = fit_and_score_pipeline(X_tr, X_te, y_tr, y_te)
    >>> score > 0.9
    True
    """
    pass


# =============================================================================
# COLUMN TRANSFORMER
# =============================================================================

# Exercise 4: Numeric Preprocessing Pipeline
# Difficulty: Medium
# Create a pipeline for numeric features: impute missing values (median)
# then scale with StandardScaler.
def create_numeric_pipeline() -> Pipeline:
    """Create numeric preprocessing: SimpleImputer(median) -> StandardScaler.

    Named steps: 'imputer' and 'scaler'.

    Returns:
        A Pipeline for numeric feature preprocessing.

    >>> pipe = create_numeric_pipeline()
    >>> X = np.array([[1, 2], [np.nan, 4], [5, np.nan]])
    >>> result = pipe.fit_transform(X)
    >>> np.isnan(result).any()
    False
    """
    pass


# Exercise 5: Categorical Preprocessing Pipeline
# Difficulty: Medium
# Create a pipeline for categorical features: impute missing (most_frequent)
# then one-hot encode.
def create_categorical_pipeline() -> Pipeline:
    """Create categorical preprocessing: SimpleImputer -> OneHotEncoder.

    Use SimpleImputer(strategy='most_frequent').
    Use OneHotEncoder(handle_unknown='ignore', sparse_output=False).
    Named steps: 'imputer' and 'encoder'.

    Returns:
        A Pipeline for categorical feature preprocessing.

    >>> pipe = create_categorical_pipeline()
    >>> X = np.array([['A'], ['B'], ['A'], [None]])
    >>> result = pipe.fit_transform(X)
    >>> result.shape[1] == 2  # two unique categories
    True
    """
    pass


# Exercise 6: Full ColumnTransformer
# Difficulty: Medium
# Create a ColumnTransformer that applies numeric preprocessing to numeric
# columns and categorical preprocessing to categorical columns.
def create_column_transformer(
    numeric_features: list[str],
    categorical_features: list[str]
) -> ColumnTransformer:
    """Create a ColumnTransformer with separate pipelines per type.

    Numeric: SimpleImputer(median) -> StandardScaler
    Categorical: SimpleImputer(most_frequent) -> OneHotEncoder(handle_unknown='ignore', sparse_output=False)

    Args:
        numeric_features: List of numeric column names.
        categorical_features: List of categorical column names.

    Returns:
        A ColumnTransformer object.

    >>> ct = create_column_transformer(['age', 'income'], ['city'])
    >>> data = pd.DataFrame({'age': [25, 30], 'income': [50000, 60000], 'city': ['A', 'B']})
    >>> result = ct.fit_transform(data)
    >>> result.shape == (2, 4)  # 2 numeric + 2 one-hot
    True
    """
    pass


# Exercise 7: End-to-End Pipeline with ColumnTransformer
# Difficulty: Medium
# Combine a ColumnTransformer with a classifier into a complete pipeline.
def create_full_pipeline(
    numeric_features: list[str],
    categorical_features: list[str]
) -> Pipeline:
    """Create a full pipeline: ColumnTransformer -> LogisticRegression.

    Use the same preprocessing as Exercise 6.
    Use LogisticRegression(random_state=42, max_iter=1000).
    Named steps: 'preprocessor' and 'classifier'.

    Args:
        numeric_features: List of numeric column names.
        categorical_features: List of categorical column names.

    Returns:
        A complete Pipeline object.

    >>> pipe = create_full_pipeline(['age', 'income'], ['city'])
    >>> 'preprocessor' in pipe.named_steps
    True
    >>> 'classifier' in pipe.named_steps
    True
    """
    pass


# =============================================================================
# CUSTOM TRANSFORMERS
# =============================================================================

# Exercise 8: Custom Log Transformer
# Difficulty: Hard
# Create a custom transformer that applies log1p to all features.
# Must inherit from BaseEstimator and TransformerMixin.
class LogTransformer(BaseEstimator, TransformerMixin):
    """Apply np.log1p to all features.

    This transformer applies the natural log(1 + x) transformation,
    which is useful for right-skewed features. Handles zero values safely.

    >>> lt = LogTransformer()
    >>> X = np.array([[1, 10], [100, 1000]])
    >>> result = lt.fit_transform(X)
    >>> result.shape == (2, 2)
    True
    >>> np.allclose(result[0, 0], np.log1p(1))
    True
    """

    def fit(self, X, y=None):
        pass

    def transform(self, X):
        pass


# Exercise 9: Custom Feature Selector
# Difficulty: Hard
# Create a custom transformer that selects the top k features by variance.
class VarianceSelector(BaseEstimator, TransformerMixin):
    """Select top k features by variance (computed on training data).

    Args:
        k: Number of top-variance features to keep.

    >>> vs = VarianceSelector(k=2)
    >>> X = np.array([[1, 100, 10], [2, 200, 20], [3, 300, 30], [4, 400, 40]])
    >>> result = vs.fit_transform(X)
    >>> result.shape == (4, 2)
    True
    """

    def __init__(self, k: int = 2):
        pass

    def fit(self, X, y=None):
        pass

    def transform(self, X):
        pass


# =============================================================================
# FEATURE UNION
# =============================================================================

# Exercise 10: FeatureUnion Pipeline
# Difficulty: Medium
# Create a pipeline that uses FeatureUnion to combine PCA features with
# scaled features, then feeds into a classifier.
def create_feature_union_pipeline() -> Pipeline:
    """Create a pipeline with FeatureUnion: PCA(2) + StandardScaler -> LogisticRegression.

    Named steps:
        'features' for the FeatureUnion (containing 'pca' and 'scaler')
        'classifier' for LogisticRegression(random_state=42, max_iter=1000)

    Returns:
        A Pipeline object.

    >>> pipe = create_feature_union_pipeline()
    >>> iris = load_iris()
    >>> X_tr, X_te, y_tr, y_te = train_test_split(
    ...     iris.data, iris.target, random_state=42)
    >>> pipe.fit(X_tr, y_tr)
    >>> pipe.score(X_te, y_te) > 0.8
    True
    """
    pass


# =============================================================================
# GRID SEARCH WITH PIPELINES
# =============================================================================

# Exercise 11: Pipeline Grid Search
# Difficulty: Hard
# Perform grid search over both pipeline preprocessing and model hyperparameters.
def pipeline_grid_search(
    X: np.ndarray, y: np.ndarray
) -> dict:
    """Grid search over pipeline with StandardScaler -> RandomForest.

    Pipeline steps: 'scaler' (StandardScaler), 'classifier' (RandomForestClassifier).

    Parameter grid:
        'classifier__n_estimators': [50, 100]
        'classifier__max_depth': [3, 5, None]

    Use cv=3, scoring='accuracy', RandomForestClassifier(random_state=42).

    Args:
        X: Feature matrix.
        y: Target array.

    Returns:
        Dict of best parameters found.

    >>> iris = load_iris()
    >>> params = pipeline_grid_search(iris.data, iris.target)
    >>> 'classifier__n_estimators' in params
    True
    """
    pass


# =============================================================================
# SERIALIZATION
# =============================================================================

# Exercise 12: Save and Load Pipeline
# Difficulty: Hard
# Save a fitted pipeline to disk with joblib, load it back, and verify
# predictions match. Use a temporary file.
def save_and_load_pipeline(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> tuple[float, bool]:
    """Save a fitted pipeline, load it, and verify predictions match.

    Steps:
        1. Create and fit a StandardScaler -> LogisticRegression pipeline.
        2. Get predictions on X_test.
        3. Save pipeline to a temp file with joblib.
        4. Load pipeline from the temp file.
        5. Get predictions from loaded pipeline.
        6. Verify predictions match.

    Use LogisticRegression(random_state=42, max_iter=1000).

    Args:
        X_train, X_test: Feature matrices.
        y_train, y_test: Target arrays.

    Returns:
        Tuple of (accuracy, predictions_match) where:
            accuracy: float score on X_test from loaded pipeline
            predictions_match: bool True if original and loaded predictions are identical

    >>> iris = load_iris()
    >>> X_tr, X_te, y_tr, y_te = train_test_split(
    ...     iris.data, iris.target, random_state=42)
    >>> acc, match = save_and_load_pipeline(X_tr, X_te, y_tr, y_te)
    >>> acc > 0.9
    True
    >>> match
    True
    """
    pass


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, random_state=42
    )

    print("Running Exercise 1: Simple Pipeline...")
    pipe1 = create_basic_pipeline()
    assert list(pipe1.named_steps.keys()) == ['scaler', 'classifier']
    print("  PASSED")

    print("Running Exercise 2: make_pipeline...")
    pipe2 = create_auto_pipeline()
    assert 'standardscaler' in pipe2.named_steps
    assert 'logisticregression' in pipe2.named_steps
    print("  PASSED")

    print("Running Exercise 3: Fit and Score...")
    score3 = fit_and_score_pipeline(X_train, X_test, y_train, y_test)
    assert score3 > 0.9, f"Score={score3}"
    print("  PASSED")

    print("Running Exercise 4: Numeric Pipeline...")
    pipe4 = create_numeric_pipeline()
    X4 = np.array([[1.0, 2.0], [np.nan, 4.0], [5.0, np.nan]])
    result4 = pipe4.fit_transform(X4)
    assert not np.isnan(result4).any()
    print("  PASSED")

    print("Running Exercise 5: Categorical Pipeline...")
    pipe5 = create_categorical_pipeline()
    X5 = np.array([['A'], ['B'], ['A'], [None]])
    result5 = pipe5.fit_transform(X5)
    assert result5.shape[1] == 2
    print("  PASSED")

    print("Running Exercise 6: ColumnTransformer...")
    ct6 = create_column_transformer(['age', 'income'], ['city'])
    data6 = pd.DataFrame({
        'age': [25, 30], 'income': [50000, 60000], 'city': ['A', 'B']
    })
    result6 = ct6.fit_transform(data6)
    assert result6.shape == (2, 4), f"Shape={result6.shape}"
    print("  PASSED")

    print("Running Exercise 7: Full Pipeline with ColumnTransformer...")
    pipe7 = create_full_pipeline(['age', 'income'], ['city'])
    assert 'preprocessor' in pipe7.named_steps
    assert 'classifier' in pipe7.named_steps
    print("  PASSED")

    print("Running Exercise 8: LogTransformer...")
    lt8 = LogTransformer()
    X8 = np.array([[1, 10], [100, 1000]])
    result8 = lt8.fit_transform(X8)
    assert result8.shape == (2, 2)
    assert np.allclose(result8[0, 0], np.log1p(1))
    print("  PASSED")

    print("Running Exercise 9: VarianceSelector...")
    vs9 = VarianceSelector(k=2)
    X9 = np.array([[1, 100, 10], [2, 200, 20], [3, 300, 30], [4, 400, 40]])
    result9 = vs9.fit_transform(X9)
    assert result9.shape == (4, 2), f"Shape={result9.shape}"
    print("  PASSED")

    print("Running Exercise 10: FeatureUnion Pipeline...")
    pipe10 = create_feature_union_pipeline()
    pipe10.fit(X_train, y_train)
    assert pipe10.score(X_test, y_test) > 0.8
    print("  PASSED")

    print("Running Exercise 11: Pipeline Grid Search...")
    params11 = pipeline_grid_search(iris.data, iris.target)
    assert 'classifier__n_estimators' in params11
    assert 'classifier__max_depth' in params11
    print("  PASSED")

    print("Running Exercise 12: Save and Load Pipeline...")
    acc12, match12 = save_and_load_pipeline(X_train, X_test, y_train, y_test)
    assert acc12 > 0.9
    assert match12 is True
    print("  PASSED")

    print("\nAll exercises passed!")
