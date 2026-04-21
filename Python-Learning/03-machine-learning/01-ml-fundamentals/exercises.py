"""
Module 01: Machine Learning Fundamentals - Exercises
=====================================================
Target audience: Swift developers learning Python ML.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- If no AssertionError is raised, your solution is correct.

Prerequisites:
    pip install scikit-learn numpy

Difficulty levels:
  Easy   - Direct application of sklearn API
  Medium - Requires understanding ML concepts
  Hard   - Combines multiple concepts or requires careful thinking
"""

import numpy as np
from sklearn.datasets import (
    make_classification,
    make_regression,
    load_iris,
    load_wine,
)
from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    KFold,
    StratifiedKFold,
    LeaveOneOut,
)
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, mean_squared_error


# =============================================================================
# WARM-UP: Data Splitting and sklearn Basics
# =============================================================================

# Exercise 1: Basic Train/Test Split
# Difficulty: Easy
def basic_train_test_split(
    X: np.ndarray, y: np.ndarray, test_fraction: float, seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data into train and test sets.

    Use sklearn's train_test_split with the given test_fraction and random_state=seed.

    Returns:
        (X_train, X_test, y_train, y_test)

    >>> X, y = make_regression(n_samples=100, n_features=5, random_state=0)
    >>> X_tr, X_te, y_tr, y_te = basic_train_test_split(X, y, 0.2, 42)
    >>> X_tr.shape[0]
    80
    >>> X_te.shape[0]
    20
    """
    pass


# Exercise 2: Stratified Train/Test Split
# Difficulty: Easy
def stratified_split(
    X: np.ndarray, y: np.ndarray, test_fraction: float, seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data with stratification to preserve class proportions.

    Use train_test_split with stratify=y.

    Returns:
        (X_train, X_test, y_train, y_test)

    >>> X, y = make_classification(n_samples=100, weights=[0.8, 0.2], random_state=0)
    >>> _, _, _, y_te = stratified_split(X, y, 0.3, 42)
    >>> # Class proportions should be roughly preserved
    """
    pass


# Exercise 3: Three-Way Split
# Difficulty: Medium
def three_way_split(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, np.ndarray]:
    """Split data into 60% train, 20% validation, 20% test sets.

    Perform two sequential splits to achieve the 60/20/20 ratio.
    Use random_state=seed for both splits.

    Returns:
        A dict with keys: 'X_train', 'X_val', 'X_test', 'y_train', 'y_val', 'y_test'

    >>> X, y = make_regression(n_samples=100, n_features=5, random_state=0)
    >>> splits = three_way_split(X, y, 42)
    >>> splits['X_train'].shape[0]
    60
    >>> splits['X_val'].shape[0]
    20
    >>> splits['X_test'].shape[0]
    20
    """
    pass


# Exercise 4: Fit and Predict
# Difficulty: Easy
def fit_and_predict(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
) -> np.ndarray:
    """Train a LinearRegression model and return predictions on the test set.

    Returns:
        Predictions array of shape (n_test_samples,)
    """
    pass


# Exercise 5: Model Score
# Difficulty: Easy
def compute_r2_score(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> float:
    """Train a LinearRegression model and return its R2 score on the test set.

    Use the model's .score() method.

    Returns:
        R2 score as a float
    """
    pass


# =============================================================================
# CORE: Cross-Validation
# =============================================================================

# Exercise 6: K-Fold Cross-Validation
# Difficulty: Medium
def kfold_cv_scores(
    X: np.ndarray, y: np.ndarray, n_splits: int, seed: int
) -> dict[str, float]:
    """Perform K-Fold cross-validation with a Ridge regression model (alpha=1.0).

    Use KFold with shuffle=True and random_state=seed.
    Use scoring='r2'.

    Returns:
        Dict with 'mean' and 'std' of the cross-validation scores.
    """
    pass


# Exercise 7: Stratified K-Fold Cross-Validation
# Difficulty: Medium
def stratified_kfold_cv(
    X: np.ndarray, y: np.ndarray, n_splits: int, seed: int
) -> dict[str, float]:
    """Perform Stratified K-Fold CV with LogisticRegression.

    Use StratifiedKFold with shuffle=True and random_state=seed.
    Use LogisticRegression(max_iter=1000, random_state=seed).
    Use scoring='accuracy'.

    Returns:
        Dict with 'mean' and 'std' of the cross-validation scores.
    """
    pass


# Exercise 8: Compare CV Strategies
# Difficulty: Medium
def compare_cv_strategies(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, float]:
    """Compare 3-fold, 5-fold, and 10-fold cross-validation on Ridge(alpha=1.0).

    Use KFold with shuffle=True and random_state=seed for each.
    Use scoring='r2'.

    Returns:
        Dict with keys '3-fold', '5-fold', '10-fold', each mapping to the mean CV score.
    """
    pass


# =============================================================================
# INTERMEDIATE: Detecting Overfitting and Data Leakage
# =============================================================================

# Exercise 9: Detect Overfitting
# Difficulty: Medium
def detect_overfitting(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, dict[str, float]]:
    """Train two DecisionTreeRegressor models and compare train vs test performance.

    Model 1: max_depth=2 (simple)
    Model 2: max_depth=None (complex, likely overfits)

    Split data 80/20 with random_state=seed.

    Returns:
        {
            'simple': {'train_r2': ..., 'test_r2': ...},
            'complex': {'train_r2': ..., 'test_r2': ...}
        }

    The 'complex' model should have a much larger gap between train and test R2.
    """
    pass


# Exercise 10: Leakage vs No Leakage
# Difficulty: Hard
def scaling_with_leakage(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, float]:
    """Demonstrate data leakage by comparing two scaling approaches.

    Approach 1 (WITH leakage):
        - Fit StandardScaler on ALL data, then transform all data
        - Split into train/test (80/20, random_state=seed)
        - Train Ridge(alpha=1.0) on scaled train, score on scaled test

    Approach 2 (WITHOUT leakage):
        - Split into train/test first (80/20, random_state=seed)
        - Fit StandardScaler on train only, transform both
        - Train Ridge(alpha=1.0) on scaled train, score on scaled test

    Returns:
        {'with_leakage': R2_score, 'without_leakage': R2_score}

    Note: With small datasets and this simple setup, the difference may be
    small, but the principle is critical in real-world scenarios.
    """
    pass


# Exercise 11: Scaling Order Matters
# Difficulty: Medium
def proper_scaling_pipeline(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> dict[str, np.ndarray]:
    """Properly scale train and test data WITHOUT data leakage.

    Fit StandardScaler on X_train only, then transform both X_train and X_test.

    Returns:
        {'X_train_scaled': ..., 'X_test_scaled': ...,
         'train_mean': ..., 'train_std': ...}

    Where train_mean and train_std are the scaler's learned parameters
    (scaler.mean_ and scaler.scale_).
    """
    pass


# =============================================================================
# ADVANCED: Model Comparison and Workflow
# =============================================================================

# Exercise 12: Compare Multiple Models
# Difficulty: Hard
def compare_classifiers(
    X: np.ndarray, y: np.ndarray, seed: int
) -> list[dict[str, object]]:
    """Compare multiple classifiers using 5-fold stratified cross-validation.

    Models to compare:
        - LogisticRegression(max_iter=1000, random_state=seed)
        - DecisionTreeClassifier(max_depth=5, random_state=seed)
        - KNeighborsClassifier(n_neighbors=5)

    Use StratifiedKFold(n_splits=5, shuffle=True, random_state=seed).
    Use scoring='accuracy'.

    Returns:
        A list of dicts sorted by mean_score descending:
        [
            {'name': 'ModelName', 'mean_score': float, 'std_score': float},
            ...
        ]
    """
    pass


# Exercise 13: Full ML Workflow
# Difficulty: Hard
def full_workflow(seed: int) -> dict[str, object]:
    """Execute a complete ML workflow on the Iris dataset.

    Steps:
    1. Load iris dataset
    2. Split 80/20 stratified (random_state=seed)
    3. Scale features (fit on train only)
    4. Train LogisticRegression(max_iter=1000, random_state=seed) on scaled train
    5. Predict on scaled test
    6. Compute accuracy

    Returns:
        {
            'n_train': int,
            'n_test': int,
            'n_features': int,
            'n_classes': int,
            'accuracy': float,
            'predictions': np.ndarray
        }
    """
    pass


# Exercise 14: Custom K-Fold Implementation
# Difficulty: Hard
def manual_kfold(
    X: np.ndarray, y: np.ndarray, n_splits: int
) -> list[float]:
    """Implement K-Fold cross-validation manually WITHOUT using sklearn's KFold.

    Steps for each fold:
    1. Divide data indices into n_splits consecutive groups
    2. Use each group as test, the rest as train
    3. Train LinearRegression, compute R2 on the test fold

    Do NOT shuffle the data.

    Returns:
        List of R2 scores, one per fold.

    Hint: Use np.array_split to divide indices into groups.
    """
    pass


# Exercise 15: Overfitting Curve
# Difficulty: Hard
def overfitting_curve(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[int, dict[str, float]]:
    """Compute train and test R2 for DecisionTreeRegressor at various max_depth values.

    Split data 80/20 with random_state=seed.
    Test max_depth values: 1, 2, 3, 5, 10, 20, None (None means unlimited).

    Returns:
        {
            1: {'train_r2': ..., 'test_r2': ...},
            2: {'train_r2': ..., 'test_r2': ...},
            ...
            None: {'train_r2': ..., 'test_r2': ...}
        }

    You should observe that train_r2 increases with depth while test_r2
    initially increases then decreases (overfitting).
    """
    pass


# =============================================================================
# Self-Test Runner
# =============================================================================

if __name__ == "__main__":
    print("Running Module 01: ML Fundamentals Exercises...\n")
    errors = 0

    # Setup shared data
    X_reg, y_reg = make_regression(n_samples=200, n_features=10, noise=10, random_state=42)
    X_cls, y_cls = make_classification(n_samples=200, n_features=10, n_classes=2, random_state=42)

    # Exercise 1
    try:
        X_tr, X_te, y_tr, y_te = basic_train_test_split(X_reg, y_reg, 0.2, 42)
        assert X_tr.shape[0] == 160, f"Expected 160 train samples, got {X_tr.shape[0]}"
        assert X_te.shape[0] == 40, f"Expected 40 test samples, got {X_te.shape[0]}"
        assert X_tr.shape[1] == 10
        assert y_tr.shape[0] == 160
        print("  Exercise  1 (basic_train_test_split):    PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  1 (basic_train_test_split):    FAIL - {e}")
        errors += 1

    # Exercise 2
    try:
        X_tr, X_te, y_tr, y_te = stratified_split(X_cls, y_cls, 0.3, 42)
        assert X_tr.shape[0] == 140
        assert X_te.shape[0] == 60
        # Check stratification: proportions should be similar
        train_ratio = y_tr.mean()
        test_ratio = y_te.mean()
        assert abs(train_ratio - test_ratio) < 0.1, "Stratification not preserved"
        print("  Exercise  2 (stratified_split):           PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  2 (stratified_split):           FAIL - {e}")
        errors += 1

    # Exercise 3
    try:
        splits = three_way_split(X_reg, y_reg, 42)
        assert splits['X_train'].shape[0] == 120, f"Expected 120, got {splits['X_train'].shape[0]}"
        assert splits['X_val'].shape[0] == 40, f"Expected 40, got {splits['X_val'].shape[0]}"
        assert splits['X_test'].shape[0] == 40, f"Expected 40, got {splits['X_test'].shape[0]}"
        assert 'y_train' in splits and 'y_val' in splits and 'y_test' in splits
        print("  Exercise  3 (three_way_split):            PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  3 (three_way_split):            FAIL - {e}")
        errors += 1

    # Exercise 4
    try:
        X_tr, X_te, y_tr, y_te = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
        preds = fit_and_predict(X_tr, y_tr, X_te)
        assert preds.shape == y_te.shape, f"Shape mismatch: {preds.shape} vs {y_te.shape}"
        assert isinstance(preds, np.ndarray)
        print("  Exercise  4 (fit_and_predict):            PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  4 (fit_and_predict):            FAIL - {e}")
        errors += 1

    # Exercise 5
    try:
        X_tr, X_te, y_tr, y_te = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
        r2 = compute_r2_score(X_tr, y_tr, X_te, y_te)
        assert isinstance(r2, float), f"Expected float, got {type(r2)}"
        assert 0.0 < r2 <= 1.0, f"R2 should be between 0 and 1 for this data, got {r2}"
        print("  Exercise  5 (compute_r2_score):           PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  5 (compute_r2_score):           FAIL - {e}")
        errors += 1

    # Exercise 6
    try:
        result = kfold_cv_scores(X_reg, y_reg, 5, 42)
        assert 'mean' in result and 'std' in result
        assert isinstance(result['mean'], float)
        assert isinstance(result['std'], float)
        assert result['mean'] > 0, "Mean R2 should be positive for this data"
        print("  Exercise  6 (kfold_cv_scores):            PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  6 (kfold_cv_scores):            FAIL - {e}")
        errors += 1

    # Exercise 7
    try:
        result = stratified_kfold_cv(X_cls, y_cls, 5, 42)
        assert 'mean' in result and 'std' in result
        assert 0.5 < result['mean'] <= 1.0, f"Accuracy should be > 0.5, got {result['mean']}"
        print("  Exercise  7 (stratified_kfold_cv):        PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  7 (stratified_kfold_cv):        FAIL - {e}")
        errors += 1

    # Exercise 8
    try:
        result = compare_cv_strategies(X_reg, y_reg, 42)
        assert '3-fold' in result and '5-fold' in result and '10-fold' in result
        for key in result:
            assert isinstance(result[key], float), f"{key} should be float"
        print("  Exercise  8 (compare_cv_strategies):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  8 (compare_cv_strategies):      FAIL - {e}")
        errors += 1

    # Exercise 9
    try:
        result = detect_overfitting(X_reg, y_reg, 42)
        assert 'simple' in result and 'complex' in result
        assert 'train_r2' in result['simple'] and 'test_r2' in result['simple']
        # Complex model should have higher train R2
        assert result['complex']['train_r2'] > result['simple']['train_r2'], \
            "Complex model should have higher train R2"
        # Complex model should have bigger gap between train and test
        simple_gap = abs(result['simple']['train_r2'] - result['simple']['test_r2'])
        complex_gap = abs(result['complex']['train_r2'] - result['complex']['test_r2'])
        assert complex_gap > simple_gap, "Complex model should show more overfitting"
        print("  Exercise  9 (detect_overfitting):         PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise  9 (detect_overfitting):         FAIL - {e}")
        errors += 1

    # Exercise 10
    try:
        result = scaling_with_leakage(X_reg, y_reg, 42)
        assert 'with_leakage' in result and 'without_leakage' in result
        assert isinstance(result['with_leakage'], float)
        assert isinstance(result['without_leakage'], float)
        print("  Exercise 10 (scaling_with_leakage):       PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 10 (scaling_with_leakage):       FAIL - {e}")
        errors += 1

    # Exercise 11
    try:
        X_tr, X_te, y_tr, y_te = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
        result = proper_scaling_pipeline(X_tr, X_te, y_tr, y_te)
        assert 'X_train_scaled' in result and 'X_test_scaled' in result
        # Train scaled should have mean ~0
        train_mean = result['X_train_scaled'].mean(axis=0)
        assert np.allclose(train_mean, 0, atol=1e-10), "Scaled train should have mean ~0"
        # Test scaled should NOT necessarily have mean 0 (different data, same scaler)
        assert result['train_mean'].shape[0] == X_tr.shape[1]
        print("  Exercise 11 (proper_scaling_pipeline):    PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 11 (proper_scaling_pipeline):    FAIL - {e}")
        errors += 1

    # Exercise 12
    try:
        result = compare_classifiers(X_cls, y_cls, 42)
        assert len(result) == 3, f"Expected 3 models, got {len(result)}"
        assert all('name' in r and 'mean_score' in r and 'std_score' in r for r in result)
        # Should be sorted descending
        assert result[0]['mean_score'] >= result[1]['mean_score'] >= result[2]['mean_score']
        print("  Exercise 12 (compare_classifiers):        PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 12 (compare_classifiers):        FAIL - {e}")
        errors += 1

    # Exercise 13
    try:
        result = full_workflow(42)
        assert result['n_train'] == 120
        assert result['n_test'] == 30
        assert result['n_features'] == 4
        assert result['n_classes'] == 3
        assert 0.8 <= result['accuracy'] <= 1.0, f"Expected high accuracy, got {result['accuracy']}"
        assert len(result['predictions']) == 30
        print("  Exercise 13 (full_workflow):              PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 13 (full_workflow):              FAIL - {e}")
        errors += 1

    # Exercise 14
    try:
        scores = manual_kfold(X_reg, y_reg, 5)
        assert len(scores) == 5, f"Expected 5 scores, got {len(scores)}"
        assert all(isinstance(s, float) for s in scores)
        print("  Exercise 14 (manual_kfold):               PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 14 (manual_kfold):               FAIL - {e}")
        errors += 1

    # Exercise 15
    try:
        result = overfitting_curve(X_reg, y_reg, 42)
        depths = [1, 2, 3, 5, 10, 20, None]
        for d in depths:
            assert d in result, f"Missing depth {d}"
            assert 'train_r2' in result[d] and 'test_r2' in result[d]
        # Train R2 at max_depth=None should be very high (close to 1.0)
        assert result[None]['train_r2'] > 0.95, "Unlimited depth should nearly memorize train data"
        print("  Exercise 15 (overfitting_curve):          PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 15 (overfitting_curve):          FAIL - {e}")
        errors += 1

    print(f"\n{'='*55}")
    if errors == 0:
        print("All exercises passed!")
    else:
        print(f"{errors} exercise(s) need attention.")
    print(f"{'='*55}")
