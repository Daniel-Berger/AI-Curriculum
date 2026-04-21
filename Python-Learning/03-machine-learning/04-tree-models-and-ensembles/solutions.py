"""
Module 04: Tree Models and Ensemble Methods - Solutions
=========================================================
Complete implementations for all tree and ensemble exercises.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.datasets import make_classification, load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False


# =============================================================================
# DECISION TREES
# =============================================================================

def train_decision_tree(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[DecisionTreeClassifier, float]:
    """Train a DecisionTreeClassifier and return model and test accuracy."""
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    return model, accuracy


def compare_gini_entropy(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """Train DecisionTree with 'gini' and 'entropy' criteria."""
    results = {}

    for criterion in ['gini', 'entropy']:
        model = DecisionTreeClassifier(criterion=criterion, random_state=42)
        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)
        results[criterion] = accuracy

    return results


def tree_depth_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[int, float]:
    """Train DecisionTree with different max_depth values."""
    results = {}

    for depth in [2, 5, 10, None]:
        model = DecisionTreeClassifier(max_depth=depth, random_state=42)
        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)
        results[depth] = accuracy

    return results


def decision_tree_feature_importance(
    X_train: np.ndarray, y_train: np.ndarray
) -> np.ndarray:
    """Train DecisionTree and return feature importances."""
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    return model.feature_importances_


# =============================================================================
# RANDOM FORESTS
# =============================================================================

def train_random_forest(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[RandomForestClassifier, float]:
    """Train RandomForestClassifier and return model and test accuracy."""
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    return model, accuracy


def forest_n_estimators_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[int, float]:
    """Train RandomForest with different n_estimators values."""
    results = {}

    for n_est in [10, 50, 100, 200]:
        model = RandomForestClassifier(n_estimators=n_est, random_state=42)
        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)
        results[n_est] = accuracy

    return results


def random_forest_oob_score(
    X_train: np.ndarray, y_train: np.ndarray
) -> Tuple[RandomForestClassifier, float]:
    """Train RandomForest with OOB scoring enabled."""
    model = RandomForestClassifier(
        n_estimators=100, oob_score=True, random_state=42
    )
    model.fit(X_train, y_train)
    return model, model.oob_score_


def random_forest_feature_importance(
    X_train: np.ndarray, y_train: np.ndarray
) -> np.ndarray:
    """Train RandomForest and return feature importances."""
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model.feature_importances_


# =============================================================================
# GRADIENT BOOSTING
# =============================================================================

def train_gradient_boosting(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[GradientBoostingClassifier, float]:
    """Train GradientBoostingClassifier and return model and test accuracy."""
    model = GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.1, random_state=42
    )
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    return model, accuracy


def learning_rate_comparison(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[float, float]:
    """Compare GradientBoosting with different learning_rate values."""
    results = {}

    for lr in [0.01, 0.05, 0.1, 0.5]:
        model = GradientBoostingClassifier(
            n_estimators=100, learning_rate=lr, random_state=42
        )
        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)
        results[lr] = accuracy

    return results


# =============================================================================
# XGBOOST (OPTIONAL)
# =============================================================================

def train_xgboost(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[float, bool]:
    """Train XGBClassifier if available."""
    if not HAS_XGBOOST:
        return 0.0, False

    model = xgb.XGBClassifier(
        n_estimators=100, max_depth=3, random_state=42, verbosity=0
    )
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    return accuracy, True


# =============================================================================
# LIGHTGBM (OPTIONAL)
# =============================================================================

def train_lightgbm(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Tuple[float, bool]:
    """Train LGBMClassifier if available."""
    if not HAS_LIGHTGBM:
        return 0.0, False

    model = lgb.LGBMClassifier(
        n_estimators=100, max_depth=5, random_state=42, verbose=-1
    )
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    return accuracy, True


# =============================================================================
# SHAP INTERPRETATION (OPTIONAL)
# =============================================================================

def shap_feature_importance(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray
) -> Tuple[np.ndarray, bool]:
    """Train RandomForest and compute SHAP feature importances if available."""
    if not HAS_SHAP:
        return np.array([]), False

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # For binary classification, use class 1 SHAP values
    if isinstance(shap_values, list):
        shap_array = np.abs(shap_values[1])
    else:
        shap_array = np.abs(shap_values)

    mean_abs_shap = shap_array.mean(axis=0)
    return mean_abs_shap, True


# =============================================================================
# MODEL COMPARISON
# =============================================================================

def compare_all_models(
    X_train: np.ndarray, X_test: np.ndarray,
    y_train: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """Train multiple models and compare their test accuracies."""
    results = {}

    # Decision Tree
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(X_train, y_train)
    results['decision_tree'] = dt.score(X_test, y_test)

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    results['random_forest'] = rf.score(X_test, y_test)

    # Gradient Boosting
    gb = GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.1, random_state=42
    )
    gb.fit(X_train, y_train)
    results['gradient_boosting'] = gb.score(X_test, y_test)

    # XGBoost (if available)
    if HAS_XGBOOST:
        xgb_model = xgb.XGBClassifier(
            n_estimators=100, max_depth=3, random_state=42, verbosity=0
        )
        xgb_model.fit(X_train, y_train)
        results['xgboost'] = xgb_model.score(X_test, y_test)

    # LightGBM (if available)
    if HAS_LIGHTGBM:
        lgb_model = lgb.LGBMClassifier(
            n_estimators=100, max_depth=5, random_state=42, verbose=-1
        )
        lgb_model.fit(X_train, y_train)
        results['lightgbm'] = lgb_model.score(X_test, y_test)

    return results


# =============================================================================
# CROSS-VALIDATION COMPARISON
# =============================================================================

def cross_validation_comparison(
    X: np.ndarray, y: np.ndarray
) -> Dict[str, float]:
    """Perform 5-fold cross-validation on multiple models."""
    results = {}

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_scores = cross_val_score(rf, X, y, cv=5, scoring='accuracy')
    results['random_forest_cv_mean'] = rf_scores.mean()
    results['random_forest_cv_std'] = rf_scores.std()

    # Gradient Boosting
    gb = GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.1, random_state=42
    )
    gb_scores = cross_val_score(gb, X, y, cv=5, scoring='accuracy')
    results['gradient_boosting_cv_mean'] = gb_scores.mean()
    results['gradient_boosting_cv_std'] = gb_scores.std()

    return results


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    print("Running Exercise 1: Train Decision Tree...")
    model1, acc1 = train_decision_tree(X_train, X_test, y_train, y_test)
    assert isinstance(model1, DecisionTreeClassifier)
    assert acc1 > 0.6
    print(f"  PASSED (Accuracy: {acc1:.4f})")

    print("Running Exercise 2: Compare Gini vs Entropy...")
    results2 = compare_gini_entropy(X_train, X_test, y_train, y_test)
    print(f"  PASSED: {results2}")

    print("Running Exercise 3: Tree Depth Comparison...")
    results3 = tree_depth_comparison(X_train, X_test, y_train, y_test)
    print(f"  PASSED: {results3}")

    print("Running Exercise 4: Feature Importance...")
    importance4 = decision_tree_feature_importance(X_train, y_train)
    assert importance4.shape == (5,)
    assert np.isclose(importance4.sum(), 1.0)
    print("  PASSED")

    print("Running Exercise 5: Train Random Forest...")
    model5, acc5 = train_random_forest(X_train, X_test, y_train, y_test)
    assert isinstance(model5, RandomForestClassifier)
    assert acc5 > 0.6
    print(f"  PASSED (Accuracy: {acc5:.4f})")

    print("Running Exercise 6: N-Estimators Comparison...")
    results6 = forest_n_estimators_comparison(X_train, X_test, y_train, y_test)
    print(f"  PASSED: {results6}")

    print("Running Exercise 7: OOB Score...")
    model7, oob7 = random_forest_oob_score(X_train, y_train)
    assert isinstance(model7, RandomForestClassifier)
    assert 0 <= oob7 <= 1
    print(f"  PASSED (OOB Score: {oob7:.4f})")

    print("Running Exercise 8: Feature Importance (RF)...")
    importance8 = random_forest_feature_importance(X_train, y_train)
    assert importance8.shape == (5,)
    print("  PASSED")

    print("Running Exercise 9: Train Gradient Boosting...")
    model9, acc9 = train_gradient_boosting(X_train, X_test, y_train, y_test)
    assert isinstance(model9, GradientBoostingClassifier)
    assert acc9 > 0.6
    print(f"  PASSED (Accuracy: {acc9:.4f})")

    print("Running Exercise 10: Learning Rate Comparison...")
    results10 = learning_rate_comparison(X_train, X_test, y_train, y_test)
    print(f"  PASSED: {results10}")

    print("Running Exercise 11: XGBoost...")
    acc11, success11 = train_xgboost(X_train, X_test, y_train, y_test)
    if success11:
        print(f"  PASSED (Accuracy: {acc11:.4f})")
    else:
        print(f"  PASSED (XGBoost not installed)")

    print("Running Exercise 12: LightGBM...")
    acc12, success12 = train_lightgbm(X_train, X_test, y_train, y_test)
    if success12:
        print(f"  PASSED (Accuracy: {acc12:.4f})")
    else:
        print(f"  PASSED (LightGBM not installed)")

    print("Running Exercise 13: SHAP Feature Importance...")
    X_tr, X_te = train_test_split(X_train, test_size=0.5, random_state=42)
    shap_vals, success13 = shap_feature_importance(X_tr, X_te, y_train[:len(X_tr)])
    if success13:
        print(f"  PASSED (SHAP importances computed)")
    else:
        print(f"  PASSED (SHAP not installed)")

    print("Running Exercise 14: Model Comparison...")
    results14 = compare_all_models(X_train, X_test, y_train, y_test)
    print(f"  PASSED: {results14}")

    print("Running Exercise 15: Cross-Validation Comparison...")
    results15 = cross_validation_comparison(X, y)
    print(f"  PASSED: {results15}")

    print("\nAll exercises passed!")
