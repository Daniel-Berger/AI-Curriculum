"""
Module 01: Machine Learning Fundamentals - Solutions
=====================================================
Complete solutions with notes on Pythonic patterns and ML best practices.

Prerequisites:
    pip install scikit-learn numpy
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
# Exercise 1: Basic Train/Test Split
# =============================================================================
# Note: train_test_split is the most common first step in any ML workflow.
# The random_state parameter ensures reproducibility -- like a fixed seed in Swift.

def basic_train_test_split(
    X: np.ndarray, y: np.ndarray, test_fraction: float, seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data into train and test sets."""
    return train_test_split(X, y, test_size=test_fraction, random_state=seed)


# =============================================================================
# Exercise 2: Stratified Train/Test Split
# =============================================================================
# Note: stratify=y preserves the class distribution in both train and test sets.
# This is critical for imbalanced datasets -- without stratification, the minority
# class might not appear in the test set at all.

def stratified_split(
    X: np.ndarray, y: np.ndarray, test_fraction: float, seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data with stratification to preserve class proportions."""
    return train_test_split(
        X, y, test_size=test_fraction, stratify=y, random_state=seed
    )


# =============================================================================
# Exercise 3: Three-Way Split
# =============================================================================
# Note: sklearn doesn't have a built-in three-way split, so we chain two splits.
# First split off 20% for test, then split the remaining 80% into 75% train / 25% val.
# 0.75 * 0.80 = 0.60 (train), 0.25 * 0.80 = 0.20 (val), 0.20 (test).

def three_way_split(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, np.ndarray]:
    """Split data into 60% train, 20% validation, 20% test sets."""
    # First split: 80% temp, 20% test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )
    # Second split: 75% of temp = 60% total for train, 25% of temp = 20% total for val
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.25, random_state=seed
    )
    return {
        'X_train': X_train, 'X_val': X_val, 'X_test': X_test,
        'y_train': y_train, 'y_val': y_val, 'y_test': y_test,
    }


# =============================================================================
# Exercise 4: Fit and Predict
# =============================================================================
# Note: This is the most fundamental sklearn pattern: instantiate -> fit -> predict.
# Every sklearn model follows this exact same interface, whether it's linear regression,
# random forest, or SVM.

def fit_and_predict(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
) -> np.ndarray:
    """Train a LinearRegression model and return predictions on the test set."""
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model.predict(X_test)


# =============================================================================
# Exercise 5: Model Score
# =============================================================================
# Note: The .score() method returns the default metric for the model type:
# - Regression: R2 score (proportion of variance explained)
# - Classification: accuracy
# R2 of 1.0 = perfect, 0.0 = no better than predicting the mean.

def compute_r2_score(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> float:
    """Train a LinearRegression model and return its R2 score on the test set."""
    model = LinearRegression()
    model.fit(X_train, y_train)
    return float(model.score(X_test, y_test))


# =============================================================================
# Exercise 6: K-Fold Cross-Validation
# =============================================================================
# Note: cross_val_score is the quickest way to do CV in sklearn. It handles
# splitting, training, and scoring in one call. The model is cloned for each
# fold, so the original model object is never modified.

def kfold_cv_scores(
    X: np.ndarray, y: np.ndarray, n_splits: int, seed: int
) -> dict[str, float]:
    """Perform K-Fold cross-validation with Ridge regression."""
    kfold = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    model = Ridge(alpha=1.0)
    scores = cross_val_score(model, X, y, cv=kfold, scoring='r2')
    return {'mean': float(scores.mean()), 'std': float(scores.std())}


# =============================================================================
# Exercise 7: Stratified K-Fold Cross-Validation
# =============================================================================
# Note: StratifiedKFold is essential for classification problems. It ensures
# each fold has approximately the same percentage of samples of each target class
# as the complete set.

def stratified_kfold_cv(
    X: np.ndarray, y: np.ndarray, n_splits: int, seed: int
) -> dict[str, float]:
    """Perform Stratified K-Fold CV with LogisticRegression."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    model = LogisticRegression(max_iter=1000, random_state=seed)
    scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy')
    return {'mean': float(scores.mean()), 'std': float(scores.std())}


# =============================================================================
# Exercise 8: Compare CV Strategies
# =============================================================================
# Note: More folds = more training data per fold = lower bias, but higher variance
# and more computation. 5-fold is the most common default in practice.

def compare_cv_strategies(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, float]:
    """Compare 3-fold, 5-fold, and 10-fold cross-validation."""
    model = Ridge(alpha=1.0)
    results = {}
    for k in [3, 5, 10]:
        kfold = KFold(n_splits=k, shuffle=True, random_state=seed)
        scores = cross_val_score(model, X, y, cv=kfold, scoring='r2')
        results[f'{k}-fold'] = float(scores.mean())
    return results


# =============================================================================
# Exercise 9: Detect Overfitting
# =============================================================================
# Note: The hallmark of overfitting is a large gap between train and test scores.
# A decision tree with no depth limit will perfectly memorize the training data
# (train R2 = 1.0) but generalize poorly. Limiting max_depth is regularization.

def detect_overfitting(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, dict[str, float]]:
    """Compare simple vs complex DecisionTree to detect overfitting."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    results = {}
    for name, depth in [('simple', 2), ('complex', None)]:
        model = DecisionTreeRegressor(max_depth=depth, random_state=seed)
        model.fit(X_train, y_train)
        results[name] = {
            'train_r2': float(model.score(X_train, y_train)),
            'test_r2': float(model.score(X_test, y_test)),
        }
    return results


# =============================================================================
# Exercise 10: Leakage vs No Leakage
# =============================================================================
# Note: Data leakage is one of the most common and insidious ML mistakes.
# When you fit_transform the scaler on ALL data before splitting, the test set's
# statistics influence the training data's scaling. In production, you won't have
# the test data at training time, so this gives a falsely optimistic estimate.

def scaling_with_leakage(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[str, float]:
    """Demonstrate data leakage with scaling."""
    # Approach 1: WITH leakage (scale all data, then split)
    scaler_leak = StandardScaler()
    X_scaled_all = scaler_leak.fit_transform(X)
    X_tr_leak, X_te_leak, y_tr, y_te = train_test_split(
        X_scaled_all, y, test_size=0.2, random_state=seed
    )
    model_leak = Ridge(alpha=1.0)
    model_leak.fit(X_tr_leak, y_tr)
    score_leak = float(model_leak.score(X_te_leak, y_te))

    # Approach 2: WITHOUT leakage (split first, then scale)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )
    scaler_clean = StandardScaler()
    X_tr_scaled = scaler_clean.fit_transform(X_tr)
    X_te_scaled = scaler_clean.transform(X_te)
    model_clean = Ridge(alpha=1.0)
    model_clean.fit(X_tr_scaled, y_tr)
    score_clean = float(model_clean.score(X_te_scaled, y_te))

    return {'with_leakage': score_leak, 'without_leakage': score_clean}


# =============================================================================
# Exercise 11: Scaling Order Matters
# =============================================================================
# Note: The key insight is fit_transform on train, transform (NOT fit_transform)
# on test. The scaler learns mean/std from training data and applies those same
# parameters to test data. This mirrors production: you save the scaler's parameters
# and apply them to new data at inference time.

def proper_scaling_pipeline(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> dict[str, np.ndarray]:
    """Properly scale train and test data WITHOUT data leakage."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return {
        'X_train_scaled': X_train_scaled,
        'X_test_scaled': X_test_scaled,
        'train_mean': scaler.mean_,
        'train_std': scaler.scale_,
    }


# =============================================================================
# Exercise 12: Compare Multiple Models
# =============================================================================
# Note: This pattern -- trying multiple models with CV and comparing -- is the
# standard approach for model selection. The sorted output makes it easy to pick
# the winner. In practice, you'd also consider training time, interpretability,
# and deployment constraints.

def compare_classifiers(
    X: np.ndarray, y: np.ndarray, seed: int
) -> list[dict[str, object]]:
    """Compare multiple classifiers using stratified cross-validation."""
    models = [
        ("LogisticRegression", LogisticRegression(max_iter=1000, random_state=seed)),
        ("DecisionTree", DecisionTreeClassifier(max_depth=5, random_state=seed)),
        ("KNN", KNeighborsClassifier(n_neighbors=5)),
    ]

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    results = []

    for name, model in models:
        scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy')
        results.append({
            'name': name,
            'mean_score': float(scores.mean()),
            'std_score': float(scores.std()),
        })

    # Sort by mean_score descending -- Pythonic use of sorted with key
    results.sort(key=lambda r: r['mean_score'], reverse=True)
    return results


# =============================================================================
# Exercise 13: Full ML Workflow
# =============================================================================
# Note: This exercise ties together every concept: loading data, splitting,
# scaling, training, predicting, and evaluating. This is the workflow you'll
# repeat hundreds of times. Notice how the scaler is fit only on training data.

def full_workflow(seed: int) -> dict[str, object]:
    """Execute a complete ML workflow on the Iris dataset."""
    # 1. Load data
    iris = load_iris()
    X, y = iris.data, iris.target

    # 2. Split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=seed
    )

    # 3. Scale (fit on train only!)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. Train
    model = LogisticRegression(max_iter=1000, random_state=seed)
    model.fit(X_train_scaled, y_train)

    # 5. Predict
    predictions = model.predict(X_test_scaled)

    # 6. Evaluate
    accuracy = float(accuracy_score(y_test, predictions))

    return {
        'n_train': len(X_train),
        'n_test': len(X_test),
        'n_features': X.shape[1],
        'n_classes': len(iris.target_names),
        'accuracy': accuracy,
        'predictions': predictions,
    }


# =============================================================================
# Exercise 14: Custom K-Fold Implementation
# =============================================================================
# Note: Understanding how cross-validation works internally is important.
# np.array_split divides indices into n roughly equal groups. We iterate over
# each group, using it as the test set and the rest as training. This is exactly
# what sklearn's KFold does under the hood.

def manual_kfold(
    X: np.ndarray, y: np.ndarray, n_splits: int
) -> list[float]:
    """Implement K-Fold cross-validation manually."""
    indices = np.arange(len(X))
    folds = np.array_split(indices, n_splits)

    scores = []
    for i in range(n_splits):
        # Test indices: current fold
        test_idx = folds[i]
        # Train indices: all other folds concatenated
        train_idx = np.concatenate([folds[j] for j in range(n_splits) if j != i])

        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        model = LinearRegression()
        model.fit(X_train, y_train)
        scores.append(float(model.score(X_test, y_test)))

    return scores


# =============================================================================
# Exercise 15: Overfitting Curve
# =============================================================================
# Note: This exercise produces the classic "validation curve" data. As model
# complexity (max_depth) increases, training error decreases (the model memorizes
# more), while test error first decreases then increases (overfitting). The optimal
# depth is where test error is minimized -- the sweet spot of the bias-variance
# tradeoff.

def overfitting_curve(
    X: np.ndarray, y: np.ndarray, seed: int
) -> dict[int, dict[str, float]]:
    """Compute train and test R2 at various max_depth values."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    depths = [1, 2, 3, 5, 10, 20, None]
    results = {}

    for depth in depths:
        model = DecisionTreeRegressor(max_depth=depth, random_state=seed)
        model.fit(X_train, y_train)
        results[depth] = {
            'train_r2': float(model.score(X_train, y_train)),
            'test_r2': float(model.score(X_test, y_test)),
        }

    return results


# =============================================================================
# Verification
# =============================================================================

if __name__ == "__main__":
    print("Running Module 01 Solutions - Verification...\n")

    X_reg, y_reg = make_regression(n_samples=200, n_features=10, noise=10, random_state=42)
    X_cls, y_cls = make_classification(n_samples=200, n_features=10, n_classes=2, random_state=42)

    # Quick verification of each solution
    print("Ex 1:", basic_train_test_split(X_reg, y_reg, 0.2, 42)[0].shape)
    print("Ex 2:", stratified_split(X_cls, y_cls, 0.3, 42)[0].shape)
    print("Ex 3:", {k: v.shape for k, v in three_way_split(X_reg, y_reg, 42).items()})

    X_tr, X_te, y_tr, y_te = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
    print("Ex 4:", fit_and_predict(X_tr, y_tr, X_te).shape)
    print("Ex 5:", f"R2 = {compute_r2_score(X_tr, y_tr, X_te, y_te):.4f}")
    print("Ex 6:", kfold_cv_scores(X_reg, y_reg, 5, 42))
    print("Ex 7:", stratified_kfold_cv(X_cls, y_cls, 5, 42))
    print("Ex 8:", compare_cv_strategies(X_reg, y_reg, 42))
    print("Ex 9:", detect_overfitting(X_reg, y_reg, 42))
    print("Ex 10:", scaling_with_leakage(X_reg, y_reg, 42))
    print("Ex 11:", {k: v.shape if hasattr(v, 'shape') else v
                     for k, v in proper_scaling_pipeline(X_tr, X_te, y_tr, y_te).items()})
    print("Ex 12:", [(r['name'], f"{r['mean_score']:.4f}") for r in compare_classifiers(X_cls, y_cls, 42)])
    wf = full_workflow(42)
    print("Ex 13:", f"accuracy={wf['accuracy']:.4f}, n_train={wf['n_train']}, n_test={wf['n_test']}")
    print("Ex 14:", [f"{s:.4f}" for s in manual_kfold(X_reg, y_reg, 5)])
    oc = overfitting_curve(X_reg, y_reg, 42)
    print("Ex 15:", {d: f"train={v['train_r2']:.3f}, test={v['test_r2']:.3f}" for d, v in oc.items()})

    print("\nAll solutions verified successfully!")
