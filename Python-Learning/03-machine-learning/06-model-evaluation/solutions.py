"""
Module 06: Model Evaluation - Solutions
========================================
Complete solutions for all exercises.
"""

import numpy as np
import optuna
from sklearn.datasets import load_iris, make_classification, make_regression
from sklearn.model_selection import (
    train_test_split, cross_val_score, KFold, StratifiedKFold,
    TimeSeriesSplit, GridSearchCV, RandomizedSearchCV,
    learning_curve
)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, mean_squared_error,
    mean_absolute_error, r2_score, silhouette_score,
    classification_report, log_loss
)
from sklearn.preprocessing import StandardScaler

# Suppress Optuna logging for cleaner output
optuna.logging.set_verbosity(optuna.logging.WARNING)


# Exercise 1: Confusion Matrix Components
def confusion_matrix_components(
    y_true: np.ndarray, y_pred: np.ndarray
) -> tuple[int, int, int, int]:
    """Extract TN, FP, FN, TP from confusion matrix."""
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    return int(tn), int(fp), int(fn), int(tp)


# Exercise 2: Precision and Recall Manual
def precision_recall_manual(
    tn: int, fp: int, fn: int, tp: int
) -> tuple[float, float]:
    """Compute precision and recall from confusion matrix components."""
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return precision, recall


# Exercise 3: F1 Score Variants
def compute_f1_variants(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> dict[str, float]:
    """Train LogisticRegression and compute F1 with different averaging."""
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return {
        'macro': f1_score(y_test, y_pred, average='macro'),
        'micro': f1_score(y_test, y_pred, average='micro'),
        'weighted': f1_score(y_test, y_pred, average='weighted'),
    }


# Exercise 4: ROC AUC Score
def compute_roc_auc(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> float:
    """Train LogisticRegression and compute ROC AUC."""
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train, y_train)
    y_proba = model.predict_proba(X_test)[:, 1]
    return roc_auc_score(y_test, y_proba)


# Exercise 5: Log Loss
def compute_log_loss(
    y_true: np.ndarray, y_proba: np.ndarray
) -> float:
    """Compute log loss (cross-entropy)."""
    return log_loss(y_true, y_proba)


# Exercise 6: Regression Metrics Suite
def regression_metrics(
    y_true: np.ndarray, y_pred: np.ndarray
) -> dict[str, float]:
    """Compute common regression metrics."""
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
    }


# Exercise 7: Adjusted R-Squared
def adjusted_r_squared(r2: float, n_samples: int, n_features: int) -> float:
    """Compute adjusted R-squared."""
    return 1 - (1 - r2) * (n_samples - 1) / (n_samples - n_features - 1)


# Exercise 8: Stratified Cross-Validation
def stratified_cv_score(
    X: np.ndarray, y: np.ndarray
) -> tuple[float, float]:
    """Perform 5-fold stratified CV with LogisticRegression."""
    model = LogisticRegression(random_state=42, max_iter=1000)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy')
    return float(scores.mean()), float(scores.std())


# Exercise 9: Time Series Cross-Validation
def timeseries_cv_scores(
    X: np.ndarray, y: np.ndarray
) -> np.ndarray:
    """Perform TimeSeriesSplit CV with LinearRegression."""
    model = LinearRegression()
    tscv = TimeSeriesSplit(n_splits=5)
    scores = cross_val_score(model, X, y, cv=tscv, scoring='neg_mean_squared_error')
    return scores


# Exercise 10: Grid Search
def grid_search_rf(
    X: np.ndarray, y: np.ndarray
) -> dict:
    """Grid search over RandomForest hyperparameters."""
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [3, 5, None],
    }

    grid = GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid,
        cv=3,
        scoring='accuracy',
    )
    grid.fit(X, y)
    return grid.best_params_


# Exercise 11: Optuna Basic Tuning
def optuna_tune_rf(
    X: np.ndarray, y: np.ndarray, n_trials: int = 30
) -> tuple[dict, float]:
    """Tune RandomForest with Optuna."""

    def objective(trial: optuna.Trial) -> float:
        n_estimators = trial.suggest_int('n_estimators', 50, 300)
        max_depth = trial.suggest_int('max_depth', 3, 20)
        min_samples_split = trial.suggest_int('min_samples_split', 2, 10)

        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42,
        )

        scores = cross_val_score(model, X, y, cv=3, scoring='accuracy')
        return scores.mean()

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=n_trials)

    return study.best_trial.params, study.best_trial.value


# Exercise 12: Optuna with Pruning
def optuna_tune_with_pruning(
    X: np.ndarray, y: np.ndarray, n_trials: int = 30
) -> tuple[dict, float]:
    """Tune RandomForest with Optuna using MedianPruner."""

    def objective(trial: optuna.Trial) -> float:
        n_estimators = trial.suggest_int('n_estimators', 50, 300)
        max_depth = trial.suggest_int('max_depth', 3, 20)

        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
        )

        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = []

        for step, (train_idx, val_idx) in enumerate(skf.split(X, y)):
            X_train_fold = X[train_idx]
            X_val_fold = X[val_idx]
            y_train_fold = y[train_idx]
            y_val_fold = y[val_idx]

            model.fit(X_train_fold, y_train_fold)
            score = model.score(X_val_fold, y_val_fold)
            scores.append(score)

            trial.report(np.mean(scores), step)
            if trial.should_prune():
                raise optuna.TrialPruned()

        return np.mean(scores)

    study = optuna.create_study(
        direction='maximize',
        pruner=optuna.pruners.MedianPruner(n_startup_trials=5),
    )
    study.optimize(objective, n_trials=n_trials)

    return study.best_trial.params, study.best_trial.value


# Exercise 13: Learning Curve Data
def compute_learning_curve(
    X: np.ndarray, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute learning curve data for RandomForestClassifier."""
    model = RandomForestClassifier(n_estimators=50, random_state=42)

    train_sizes_abs, train_scores, val_scores = learning_curve(
        model, X, y,
        train_sizes=np.linspace(0.1, 1.0, 5),
        cv=5,
        scoring='accuracy',
    )

    train_mean = train_scores.mean(axis=1)
    val_mean = val_scores.mean(axis=1)

    return train_sizes_abs, train_mean, val_mean


# Exercise 14: Class Weight Comparison
def compare_class_weights(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> tuple[float, float]:
    """Compare recall with and without balanced class weights."""
    # Without class weights
    model_plain = LogisticRegression(random_state=42, max_iter=1000)
    model_plain.fit(X_train, y_train)
    recall_plain = recall_score(y_test, model_plain.predict(X_test))

    # With balanced class weights
    model_balanced = LogisticRegression(
        class_weight='balanced', random_state=42, max_iter=1000
    )
    model_balanced.fit(X_train, y_train)
    recall_balanced = recall_score(y_test, model_balanced.predict(X_test))

    return recall_plain, recall_balanced


# Exercise 15: Optimal Threshold
def find_optimal_threshold(
    y_true: np.ndarray, y_proba: np.ndarray
) -> tuple[float, float]:
    """Find the threshold that maximizes F1 score."""
    thresholds = np.arange(0.1, 0.9, 0.01)
    best_threshold = 0.5
    best_f1 = 0.0

    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = t

    return float(best_threshold), float(best_f1)


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    print("Running Exercise 1: Confusion Matrix Components...")
    y_true1 = np.array([0, 0, 1, 1, 1, 0])
    y_pred1 = np.array([0, 1, 1, 1, 0, 0])
    tn, fp, fn, tp = confusion_matrix_components(y_true1, y_pred1)
    assert (tn, fp, fn, tp) == (2, 1, 1, 2)
    print("  PASSED")

    print("Running Exercise 2: Precision and Recall Manual...")
    p, r = precision_recall_manual(50, 10, 5, 35)
    assert abs(p - 0.7778) < 0.001
    assert abs(r - 0.875) < 0.001
    print("  PASSED")

    print("Running Exercise 3: F1 Variants...")
    iris = load_iris()
    X_tr3, X_te3, y_tr3, y_te3 = train_test_split(
        iris.data, iris.target, random_state=42)
    f1_result = compute_f1_variants(X_tr3, X_te3, y_tr3, y_te3)
    assert all(k in f1_result for k in ['macro', 'micro', 'weighted'])
    assert all(0 <= v <= 1 for v in f1_result.values())
    print("  PASSED")

    print("Running Exercise 4: ROC AUC...")
    X4, y4 = make_classification(n_samples=500, random_state=42)
    X_tr4, X_te4, y_tr4, y_te4 = train_test_split(X4, y4, random_state=42)
    auc_val = compute_roc_auc(X_tr4, X_te4, y_tr4, y_te4)
    assert 0.5 <= auc_val <= 1.0
    print("  PASSED")

    print("Running Exercise 5: Log Loss...")
    y_true5 = np.array([0, 0, 1, 1])
    y_proba5 = np.array([0.1, 0.4, 0.8, 0.9])
    ll = compute_log_loss(y_true5, y_proba5)
    assert 0 < ll < 1
    print("  PASSED")

    print("Running Exercise 6: Regression Metrics...")
    y_true6 = np.array([3.0, 5.0, 2.5, 7.0])
    y_pred6 = np.array([2.8, 5.2, 2.3, 6.8])
    metrics6 = regression_metrics(y_true6, y_pred6)
    assert metrics6['rmse'] < 1.0
    print("  PASSED")

    print("Running Exercise 7: Adjusted R-Squared...")
    adj_r2 = adjusted_r_squared(0.9, 100, 5)
    assert abs(adj_r2 - 0.8947) < 0.001
    print("  PASSED")

    print("Running Exercise 8: Stratified CV...")
    mean_s, std_s = stratified_cv_score(iris.data, iris.target)
    assert mean_s > 0.9
    assert std_s < 0.1
    print("  PASSED")

    print("Running Exercise 9: Time Series CV...")
    X9, y9 = make_regression(n_samples=200, n_features=5, random_state=42)
    scores9 = timeseries_cv_scores(X9, y9)
    assert len(scores9) == 5
    print("  PASSED")

    print("Running Exercise 10: Grid Search...")
    params10 = grid_search_rf(iris.data, iris.target)
    assert 'n_estimators' in params10
    assert 'max_depth' in params10
    print("  PASSED")

    print("Running Exercise 11: Optuna Basic...")
    params11, score11 = optuna_tune_rf(iris.data, iris.target, n_trials=10)
    assert score11 > 0.9
    print("  PASSED")

    print("Running Exercise 12: Optuna with Pruning...")
    params12, score12 = optuna_tune_with_pruning(iris.data, iris.target, n_trials=10)
    assert score12 > 0.9
    print("  PASSED")

    print("Running Exercise 13: Learning Curve...")
    sizes13, train_m13, val_m13 = compute_learning_curve(iris.data, iris.target)
    assert len(sizes13) == 5
    assert len(train_m13) == 5
    assert len(val_m13) == 5
    print("  PASSED")

    print("Running Exercise 14: Class Weight Comparison...")
    X14, y14 = make_classification(n_samples=1000, weights=[0.9, 0.1],
                                    random_state=42)
    X_tr14, X_te14, y_tr14, y_te14 = train_test_split(X14, y14, random_state=42)
    plain14, balanced14 = compare_class_weights(X_tr14, X_te14, y_tr14, y_te14)
    assert balanced14 >= plain14
    print("  PASSED")

    print("Running Exercise 15: Optimal Threshold...")
    y_true15 = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_proba15 = np.array([0.1, 0.3, 0.4, 0.6, 0.5, 0.7, 0.8, 0.9])
    thresh15, f1_15 = find_optimal_threshold(y_true15, y_proba15)
    assert 0.1 <= thresh15 <= 0.9
    assert f1_15 > 0.5
    print("  PASSED")

    print("\nAll exercises passed!")
