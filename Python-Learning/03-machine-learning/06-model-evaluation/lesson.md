# Module 06: Model Evaluation

## Table of Contents

1. [Why Evaluation Matters](#1-why-evaluation-matters)
2. [Classification Metrics Deep Dive](#2-classification-metrics-deep-dive)
3. [Regression Metrics](#3-regression-metrics)
4. [Cross-Validation Strategies](#4-cross-validation-strategies)
5. [Hyperparameter Tuning with GridSearchCV and RandomizedSearchCV](#5-hyperparameter-tuning-with-gridsearchcv-and-randomizedsearchcv)
6. [Hyperparameter Tuning with Optuna](#6-hyperparameter-tuning-with-optuna)
7. [Learning Curves and Validation Curves](#7-learning-curves-and-validation-curves)
8. [Handling Imbalanced Datasets](#8-handling-imbalanced-datasets)
9. [Statistical Significance of Results](#9-statistical-significance-of-results)
10. [Best Practices](#10-best-practices)

---

## 1. Why Evaluation Matters

A model that looks great on training data can be worthless in production. Proper evaluation
tells you how your model will perform on **unseen data** and helps you make informed decisions
about model selection, hyperparameter tuning, and deployment readiness.

### Swift Analogy

Think of model evaluation like unit testing in iOS development. You would never ship an app
with only manual testing on your device. You write XCTest cases that cover edge cases, run
them on CI, and measure code coverage. Model evaluation is the ML equivalent -- systematic,
repeatable measurement of how well your model generalizes.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Metric** | A numerical measure of model quality (accuracy, F1, RMSE, etc.) |
| **Cross-validation** | Repeated train/test splitting for robust estimates |
| **Hyperparameter tuning** | Systematic search for optimal model settings |
| **Overfitting detection** | Learning curves that show train vs. validation performance |

---

## 2. Classification Metrics Deep Dive

### The Accuracy Paradox

Accuracy (correct predictions / total predictions) is the most intuitive metric, but it can
be deeply misleading with imbalanced data.

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_curve, auc,
    precision_recall_curve, log_loss, roc_auc_score
)
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import numpy as np
import matplotlib.pyplot as plt

# Create imbalanced dataset: 95% class 0, 5% class 1
X, y = make_classification(n_samples=1000, n_features=20,
                           weights=[0.95, 0.05], random_state=42)

# A "model" that always predicts 0
dummy_preds = np.zeros_like(y)
print(f"Accuracy of always predicting 0: {accuracy_score(y, dummy_preds):.2%}")
# ~95% -- looks great, but catches ZERO positive cases!
```

### Confusion Matrix

```
                    Predicted
                 Negative  Positive
Actual Negative    TN         FP       <- FP = "False Alarm"
       Positive    FN         TP       <- FN = "Missed"
```

```python
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
model = LogisticRegression(random_state=42, max_iter=1000)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(cm)
# [[TN, FP],
#  [FN, TP]]
```

### Precision, Recall, and F1

| Metric | Formula | Interpretation | Optimize When |
|--------|---------|----------------|---------------|
| **Precision** | TP / (TP + FP) | "Of predictions positive, how many correct?" | False positives are costly (spam filter) |
| **Recall** | TP / (TP + FN) | "Of actual positives, how many found?" | False negatives are costly (disease detection) |
| **F1** | 2 * P * R / (P + R) | Harmonic mean of precision and recall | Balance both |

```python
print(f"Precision: {precision_score(y_test, y_pred):.3f}")
print(f"Recall:    {recall_score(y_test, y_pred):.3f}")
print(f"F1:        {f1_score(y_test, y_pred):.3f}")

# Full classification report
print(classification_report(y_test, y_pred))
```

### F1 Variants for Multi-Class

```python
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

iris = load_iris()
X_tr, X_te, y_tr, y_te = train_test_split(iris.data, iris.target, random_state=42)
rf = RandomForestClassifier(random_state=42)
rf.fit(X_tr, y_tr)
y_pred_mc = rf.predict(X_te)

# Different averaging strategies
print(f"F1 (macro):    {f1_score(y_te, y_pred_mc, average='macro'):.3f}")
print(f"F1 (micro):    {f1_score(y_te, y_pred_mc, average='micro'):.3f}")
print(f"F1 (weighted): {f1_score(y_te, y_pred_mc, average='weighted'):.3f}")
```

| Average | Description | Use When |
|---------|-------------|----------|
| `macro` | Unweighted mean across classes | All classes equally important |
| `micro` | Global TP, FP, FN | Aggregate performance |
| `weighted` | Weighted by class support | Imbalanced classes |

### ROC Curve and AUC

The ROC curve plots the **True Positive Rate** (recall) against the **False Positive Rate**
at different classification thresholds.

```python
# Get probability predictions
y_proba = model.predict_proba(X_test)[:, 1]

# ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_proba)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, 'b-', label=f'ROC (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], 'k--', label='Random (AUC = 0.5)')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Or use the shortcut
print(f"AUC: {roc_auc_score(y_test, y_proba):.3f}")
```

### Precision-Recall Curve

For imbalanced datasets, the precision-recall curve is often more informative than ROC.

```python
precision_vals, recall_vals, pr_thresholds = precision_recall_curve(y_test, y_proba)

plt.figure(figsize=(8, 6))
plt.plot(recall_vals, precision_vals, 'b-')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.grid(True, alpha=0.3)
plt.show()
```

### Log Loss (Cross-Entropy)

Log loss penalizes confident wrong predictions heavily. Lower is better.

```python
ll = log_loss(y_test, y_proba)
print(f"Log Loss: {ll:.4f}")
```

---

## 3. Regression Metrics

```python
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error,
    r2_score, mean_absolute_percentage_error
)
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression

# Generate regression data
X_reg, y_reg = make_regression(n_samples=200, n_features=5,
                                noise=10, random_state=42)
X_tr_r, X_te_r, y_tr_r, y_te_r = train_test_split(X_reg, y_reg, random_state=42)

lr = LinearRegression()
lr.fit(X_tr_r, y_tr_r)
y_pred_r = lr.predict(X_te_r)
```

### MSE, RMSE, and MAE

```python
mse = mean_squared_error(y_te_r, y_pred_r)
rmse = np.sqrt(mse)  # or mean_squared_error(y_te_r, y_pred_r, squared=False)
mae = mean_absolute_error(y_te_r, y_pred_r)

print(f"MSE:  {mse:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"MAE:  {mae:.2f}")
```

| Metric | Interpretation | Sensitive to Outliers? |
|--------|---------------|----------------------|
| **MSE** | Average squared error (same units squared) | Very (squared) |
| **RMSE** | Square root of MSE (same units as target) | Yes |
| **MAE** | Average absolute error (same units) | Less than MSE |

### R-squared and Adjusted R-squared

```python
r2 = r2_score(y_te_r, y_pred_r)
print(f"R-squared: {r2:.4f}")

# Adjusted R-squared (penalizes extra features)
n = len(y_te_r)
p = X_te_r.shape[1]
adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)
print(f"Adjusted R-squared: {adj_r2:.4f}")
```

### MAPE

```python
mape = mean_absolute_percentage_error(y_te_r, y_pred_r)
print(f"MAPE: {mape:.2%}")
```

> **Warning**: MAPE is undefined when actual values are zero and distorted by small values.

---

## 4. Cross-Validation Strategies

Cross-validation gives a more robust performance estimate than a single train/test split
by using multiple folds.

### KFold

```python
from sklearn.model_selection import (
    KFold, StratifiedKFold, TimeSeriesSplit, GroupKFold,
    cross_val_score, cross_validate
)

# Basic K-Fold
kfold = KFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_val_score(
    LogisticRegression(max_iter=1000),
    iris.data, iris.target,
    cv=kfold, scoring='accuracy'
)

print(f"Accuracy per fold: {scores}")
print(f"Mean: {scores.mean():.3f} +/- {scores.std():.3f}")
```

### StratifiedKFold

Maintains the class distribution in each fold -- **always use this for classification**.

```python
skfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores_strat = cross_val_score(
    LogisticRegression(max_iter=1000),
    X, y,  # imbalanced data
    cv=skfold, scoring='f1'
)
print(f"Stratified F1 scores: {scores_strat}")
print(f"Mean F1: {scores_strat.mean():.3f} +/- {scores_strat.std():.3f}")
```

### TimeSeriesSplit

For time series data, you cannot shuffle -- future data must never leak into training.

```python
tscv = TimeSeriesSplit(n_splits=5)

# Visualize the splits
for i, (train_idx, test_idx) in enumerate(tscv.split(X_reg)):
    print(f"Fold {i}: Train [{train_idx[0]}..{train_idx[-1]}], "
          f"Test [{test_idx[0]}..{test_idx[-1]}]")
```

### GroupKFold

When samples from the same group (e.g., same patient, same user) should not appear in both
train and test sets.

```python
# Suppose each sample belongs to a group (e.g., patient ID)
groups = np.array([i // 10 for i in range(len(iris.target))])  # 15 groups

gkfold = GroupKFold(n_splits=5)

scores_group = cross_val_score(
    LogisticRegression(max_iter=1000),
    iris.data, iris.target,
    cv=gkfold, groups=groups,
    scoring='accuracy'
)
print(f"GroupKFold scores: {scores_group}")
```

### cross_validate -- Multiple Metrics at Once

```python
results = cross_validate(
    LogisticRegression(max_iter=1000),
    iris.data, iris.target,
    cv=5,
    scoring=['accuracy', 'f1_macro'],
    return_train_score=True
)

print(f"Test accuracy:  {results['test_accuracy'].mean():.3f}")
print(f"Test F1 macro:  {results['test_f1_macro'].mean():.3f}")
print(f"Train accuracy: {results['train_accuracy'].mean():.3f}")
```

---

## 5. Hyperparameter Tuning with GridSearchCV and RandomizedSearchCV

### GridSearchCV -- Exhaustive Search

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 10, None],
    'min_samples_split': [2, 5, 10],
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,              # use all CPU cores
    verbose=1,
    return_train_score=True
)

grid_search.fit(iris.data, iris.target)

print(f"Best params: {grid_search.best_params_}")
print(f"Best score:  {grid_search.best_score_:.3f}")
print(f"Best model:  {grid_search.best_estimator_}")
```

### RandomizedSearchCV -- Faster Exploration

When the parameter space is large, random search is more efficient.

```python
from scipy.stats import randint, uniform

param_distributions = {
    'n_estimators': randint(50, 500),
    'max_depth': randint(3, 30),
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10),
    'max_features': uniform(0.1, 0.9),
}

random_search = RandomizedSearchCV(
    RandomForestClassifier(random_state=42),
    param_distributions,
    n_iter=50,              # number of random combinations to try
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    random_state=42,
    return_train_score=True
)

random_search.fit(iris.data, iris.target)

print(f"Best params: {random_search.best_params_}")
print(f"Best score:  {random_search.best_score_:.3f}")
```

### Grid vs. Random Search

| Feature | GridSearchCV | RandomizedSearchCV |
|---------|-------------|-------------------|
| Coverage | Exhaustive | Sampled |
| Speed | Slow (exponential) | Fast (linear in n_iter) |
| Best for | Small param spaces | Large param spaces |
| Guarantee | Finds global optimum | May miss it |

---

## 6. Hyperparameter Tuning with Optuna

Optuna is a modern hyperparameter optimization framework that uses **Bayesian optimization**
to intelligently explore the parameter space. It is far more efficient than grid or random
search.

### Installing Optuna

```bash
pip install optuna
```

### Basic Optuna Example

```python
import optuna
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

def objective(trial: optuna.Trial) -> float:
    """Optuna objective function -- returns the metric to optimize."""

    # Suggest hyperparameters
    n_estimators = trial.suggest_int('n_estimators', 50, 500)
    max_depth = trial.suggest_int('max_depth', 3, 30)
    min_samples_split = trial.suggest_int('min_samples_split', 2, 20)
    min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 10)
    max_features = trial.suggest_float('max_features', 0.1, 1.0)

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        random_state=42
    )

    # Cross-validate and return mean score
    scores = cross_val_score(model, iris.data, iris.target,
                             cv=5, scoring='accuracy')
    return scores.mean()

# Create study and optimize
study = optuna.create_study(direction='maximize')  # maximize accuracy
study.optimize(objective, n_trials=50, show_progress_bar=True)

print(f"Best trial:")
print(f"  Value (accuracy): {study.best_trial.value:.4f}")
print(f"  Params: {study.best_trial.params}")
```

### Optuna Suggest Methods

| Method | Description | Example |
|--------|-------------|---------|
| `suggest_int` | Integer parameter | `trial.suggest_int('depth', 1, 30)` |
| `suggest_float` | Float parameter | `trial.suggest_float('lr', 1e-5, 1e-1, log=True)` |
| `suggest_categorical` | Categorical choice | `trial.suggest_categorical('algo', ['rf', 'xgb'])` |

### Optuna Pruning

Pruning stops unpromising trials early, saving time.

```python
from sklearn.model_selection import StratifiedKFold

def objective_with_pruning(trial: optuna.Trial) -> float:
    n_estimators = trial.suggest_int('n_estimators', 50, 500)
    max_depth = trial.suggest_int('max_depth', 3, 30)

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42
    )

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    scores = []
    for step, (train_idx, val_idx) in enumerate(skf.split(iris.data, iris.target)):
        X_train_fold = iris.data[train_idx]
        X_val_fold = iris.data[val_idx]
        y_train_fold = iris.target[train_idx]
        y_val_fold = iris.target[val_idx]

        model.fit(X_train_fold, y_train_fold)
        score = model.score(X_val_fold, y_val_fold)
        scores.append(score)

        # Report intermediate value and prune if unpromising
        trial.report(np.mean(scores), step)
        if trial.should_prune():
            raise optuna.TrialPruned()

    return np.mean(scores)

pruned_study = optuna.create_study(
    direction='maximize',
    pruner=optuna.pruners.MedianPruner(n_startup_trials=5)
)
pruned_study.optimize(objective_with_pruning, n_trials=50)
```

### Optuna Visualization

```python
# These require plotly: pip install plotly
from optuna.visualization import (
    plot_optimization_history,
    plot_param_importances,
    plot_contour,
    plot_slice
)

# Optimization history
fig = plot_optimization_history(study)
fig.show()

# Parameter importance
fig = plot_param_importances(study)
fig.show()

# Contour plot of 2 parameters
fig = plot_contour(study, params=['n_estimators', 'max_depth'])
fig.show()
```

### Multi-Objective Optimization

```python
def multi_objective(trial: optuna.Trial) -> tuple[float, float]:
    """Optimize both accuracy and speed (model complexity)."""
    n_estimators = trial.suggest_int('n_estimators', 10, 500)
    max_depth = trial.suggest_int('max_depth', 2, 30)

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42
    )

    scores = cross_val_score(model, iris.data, iris.target, cv=5)
    accuracy = scores.mean()

    # Proxy for complexity / inference time
    complexity = n_estimators * max_depth

    return accuracy, -complexity  # maximize accuracy, minimize complexity

multi_study = optuna.create_study(
    directions=['maximize', 'maximize']
)
multi_study.optimize(multi_objective, n_trials=50)

# Pareto front
print("Pareto-optimal trials:")
for trial in multi_study.best_trials:
    print(f"  Accuracy={trial.values[0]:.3f}, "
          f"Complexity={-trial.values[1]}, "
          f"Params={trial.params}")
```

---

## 7. Learning Curves and Validation Curves

### Learning Curves -- Diagnosing Bias vs. Variance

Learning curves plot performance against training set size. They reveal:
- **High bias (underfitting)**: both train and validation scores are low.
- **High variance (overfitting)**: train score high, validation score low, big gap.

```python
from sklearn.model_selection import learning_curve, validation_curve

train_sizes, train_scores, val_scores = learning_curve(
    RandomForestClassifier(n_estimators=100, random_state=42),
    iris.data, iris.target,
    train_sizes=np.linspace(0.1, 1.0, 10),
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

# Plot
train_mean = train_scores.mean(axis=1)
train_std = train_scores.std(axis=1)
val_mean = val_scores.mean(axis=1)
val_std = val_scores.std(axis=1)

plt.figure(figsize=(8, 5))
plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1)
plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1)
plt.plot(train_sizes, train_mean, 'o-', label='Training Score')
plt.plot(train_sizes, val_mean, 'o-', label='Validation Score')
plt.xlabel('Training Set Size')
plt.ylabel('Accuracy')
plt.title('Learning Curve')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

### Validation Curves -- Tuning a Single Hyperparameter

```python
param_range = np.arange(1, 30)
train_scores_vc, val_scores_vc = validation_curve(
    RandomForestClassifier(n_estimators=100, random_state=42),
    iris.data, iris.target,
    param_name='max_depth',
    param_range=param_range,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

plt.figure(figsize=(8, 5))
plt.plot(param_range, train_scores_vc.mean(axis=1), 'o-', label='Training')
plt.plot(param_range, val_scores_vc.mean(axis=1), 'o-', label='Validation')
plt.xlabel('max_depth')
plt.ylabel('Accuracy')
plt.title('Validation Curve')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

---

## 8. Handling Imbalanced Datasets

### The Problem

With a 95/5 class split, a model can achieve 95% accuracy by always predicting the majority
class. This is useless in practice.

### Strategy 1: Class Weights

Most sklearn classifiers support `class_weight='balanced'`.

```python
from sklearn.linear_model import LogisticRegression

# Without class weights
model_plain = LogisticRegression(random_state=42, max_iter=1000)
model_plain.fit(X_train, y_train)
print(f"Plain recall: {recall_score(y_test, model_plain.predict(X_test)):.3f}")

# With balanced class weights
model_balanced = LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000)
model_balanced.fit(X_train, y_train)
print(f"Balanced recall: {recall_score(y_test, model_balanced.predict(X_test)):.3f}")
```

### Strategy 2: SMOTE (Synthetic Minority Over-sampling)

```python
# pip install imbalanced-learn
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

print(f"Before SMOTE: {np.bincount(y_train)}")
print(f"After SMOTE:  {np.bincount(y_resampled)}")

model_smote = LogisticRegression(random_state=42, max_iter=1000)
model_smote.fit(X_resampled, y_resampled)
print(f"SMOTE recall: {recall_score(y_test, model_smote.predict(X_test)):.3f}")
```

### Strategy 3: Threshold Moving

Instead of the default 0.5 threshold, choose a threshold that optimizes your target metric.

```python
y_proba_bal = model_balanced.predict_proba(X_test)[:, 1]

# Find the threshold that maximizes F1
thresholds = np.arange(0.1, 0.9, 0.01)
f1_scores = []

for t in thresholds:
    y_pred_t = (y_proba_bal >= t).astype(int)
    f1_scores.append(f1_score(y_test, y_pred_t, zero_division=0))

best_threshold = thresholds[np.argmax(f1_scores)]
print(f"Best threshold: {best_threshold:.2f}")
print(f"Best F1: {max(f1_scores):.3f}")
```

---

## 9. Statistical Significance of Results

### Is Model A Actually Better than Model B?

A difference of 0.5% in cross-validation accuracy might be noise. Use statistical tests
to determine if the difference is significant.

```python
from scipy import stats

# Compare two models with paired cross-validation
from sklearn.model_selection import cross_val_score

scores_lr = cross_val_score(
    LogisticRegression(max_iter=1000), iris.data, iris.target, cv=10
)
scores_rf = cross_val_score(
    RandomForestClassifier(n_estimators=100, random_state=42),
    iris.data, iris.target, cv=10
)

# Paired t-test (same folds)
t_stat, p_value = stats.ttest_rel(scores_lr, scores_rf)
print(f"LR mean: {scores_lr.mean():.3f}, RF mean: {scores_rf.mean():.3f}")
print(f"t-statistic: {t_stat:.3f}, p-value: {p_value:.4f}")

if p_value < 0.05:
    print("Statistically significant difference!")
else:
    print("No significant difference -- might be noise.")
```

### Confidence Intervals

```python
# 95% confidence interval for cross-validation score
mean = scores_rf.mean()
se = scores_rf.std() / np.sqrt(len(scores_rf))
ci_lower = mean - 1.96 * se
ci_upper = mean + 1.96 * se
print(f"RF Accuracy: {mean:.3f} [{ci_lower:.3f}, {ci_upper:.3f}]")
```

---

## 10. Best Practices

### Evaluation Checklist

1. **Choose metrics that match your business goal** -- do not default to accuracy.
2. **Always use stratified cross-validation** for classification.
3. **Report confidence intervals**, not just point estimates.
4. **Use learning curves** to diagnose overfitting/underfitting before tuning.
5. **Start with RandomizedSearchCV**, then refine with GridSearchCV or Optuna.
6. **Hold out a final test set** that is never used during tuning.
7. **For imbalanced data**, use precision-recall curves, F1, and class-weight/SMOTE.
8. **Log everything** -- use MLflow (Module 08) to track experiments systematically.

### Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Tuning on test set | Use a separate validation set or nested CV |
| Ignoring class imbalance | Use stratified CV, class weights, SMOTE |
| Single train/test split | Use cross-validation (5 or 10 folds) |
| Comparing models without significance test | Use paired t-test or Wilcoxon |
| Data leakage in preprocessing | Use sklearn Pipelines (Module 07) |

---

## Summary

| Concept | Key Takeaway |
|---------|-------------|
| Accuracy paradox | High accuracy can be meaningless on imbalanced data |
| Precision/Recall | Choose based on the cost of FP vs. FN |
| ROC & AUC | Threshold-independent classifier comparison |
| Cross-validation | StratifiedKFold for classification, TimeSeriesSplit for temporal data |
| GridSearchCV | Exhaustive but slow -- use for small parameter spaces |
| Optuna | Bayesian optimization -- smart, fast, prunable |
| Learning curves | Diagnose bias (underfitting) vs. variance (overfitting) |
| Imbalanced data | class_weight, SMOTE, threshold moving |
| Statistical tests | Paired t-test to compare models rigorously |
