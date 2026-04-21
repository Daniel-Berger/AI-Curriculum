"""
Module 07: sklearn Pipelines - Solutions
===========================================
Complete implementations for all pipeline exercises.
"""

import os
import tempfile
import joblib
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

def create_basic_pipeline() -> Pipeline:
    """Create a pipeline: StandardScaler -> LogisticRegression."""
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000))
    ])
    return pipe


def create_auto_pipeline() -> Pipeline:
    """Create a pipeline using make_pipeline (auto-named steps)."""
    pipe = make_pipeline(
        StandardScaler(),
        LogisticRegression(random_state=42, max_iter=1000)
    )
    return pipe


def fit_and_score_pipeline(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> float:
    """Create, fit, and score a StandardScaler + LogisticRegression pipeline."""
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000))
    ])
    pipe.fit(X_train, y_train)
    return pipe.score(X_test, y_test)


# =============================================================================
# COLUMN TRANSFORMER
# =============================================================================

def create_numeric_pipeline() -> Pipeline:
    """Create numeric preprocessing: SimpleImputer(median) -> StandardScaler."""
    pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    return pipe


def create_categorical_pipeline() -> Pipeline:
    """Create categorical preprocessing: SimpleImputer -> OneHotEncoder."""
    pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    return pipe


def create_column_transformer(
    numeric_features: list[str],
    categorical_features: list[str]
) -> ColumnTransformer:
    """Create a ColumnTransformer with separate pipelines per type."""
    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    ct = ColumnTransformer([
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

    return ct


def create_full_pipeline(
    numeric_features: list[str],
    categorical_features: list[str]
) -> Pipeline:
    """Create a full pipeline: ColumnTransformer -> LogisticRegression."""
    ct = create_column_transformer(numeric_features, categorical_features)

    pipe = Pipeline([
        ('preprocessor', ct),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000))
    ])

    return pipe


# =============================================================================
# CUSTOM TRANSFORMERS
# =============================================================================

class LogTransformer(BaseEstimator, TransformerMixin):
    """Apply np.log1p to all features."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return np.log1p(X)


class VarianceSelector(BaseEstimator, TransformerMixin):
    """Select top k features by variance (computed on training data)."""

    def __init__(self, k: int = 2):
        self.k = k
        self.variances_ = None
        self.selected_indices_ = None

    def fit(self, X, y=None):
        # Compute variance for each feature
        self.variances_ = np.var(X, axis=0)
        # Get indices of top k features
        self.selected_indices_ = np.argsort(self.variances_)[-self.k:]
        return self

    def transform(self, X):
        return X[:, self.selected_indices_]


# =============================================================================
# FEATURE UNION
# =============================================================================

def create_feature_union_pipeline() -> Pipeline:
    """Create a pipeline with FeatureUnion: PCA(2) + StandardScaler -> LogisticRegression."""
    feature_union = FeatureUnion([
        ('pca', PCA(n_components=2)),
        ('scaler', StandardScaler())
    ])

    pipe = Pipeline([
        ('features', feature_union),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000))
    ])

    return pipe


# =============================================================================
# GRID SEARCH WITH PIPELINES
# =============================================================================

def pipeline_grid_search(
    X: np.ndarray, y: np.ndarray
) -> dict:
    """Grid search over pipeline with StandardScaler -> RandomForest."""
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(random_state=42))
    ])

    param_grid = {
        'classifier__n_estimators': [50, 100],
        'classifier__max_depth': [3, 5, None]
    }

    gs = GridSearchCV(pipe, param_grid, cv=3, scoring='accuracy')
    gs.fit(X, y)

    return gs.best_params_


# =============================================================================
# SERIALIZATION
# =============================================================================

def save_and_load_pipeline(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> tuple[float, bool]:
    """Save a fitted pipeline, load it, and verify predictions match."""
    # Create and fit pipeline
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000))
    ])
    pipe.fit(X_train, y_train)

    # Get predictions from original pipeline
    y_pred_original = pipe.predict(X_test)

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
        temp_path = f.name
        joblib.dump(pipe, temp_path)

    try:
        # Load pipeline
        pipe_loaded = joblib.load(temp_path)

        # Get predictions from loaded pipeline
        y_pred_loaded = pipe_loaded.predict(X_test)

        # Check predictions match
        predictions_match = np.array_equal(y_pred_original, y_pred_loaded)

        # Get accuracy from loaded pipeline
        accuracy = pipe_loaded.score(X_test, y_test)

        return accuracy, predictions_match

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


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
    print(f"  PASSED (Score: {score3:.4f})")

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
    print(f"  PASSED: {params11}")

    print("Running Exercise 12: Save and Load Pipeline...")
    acc12, match12 = save_and_load_pipeline(X_train, X_test, y_train, y_test)
    assert acc12 > 0.9
    assert match12 is True
    print(f"  PASSED (Accuracy: {acc12:.4f}, Match: {match12})")

    print("\nAll exercises passed!")
