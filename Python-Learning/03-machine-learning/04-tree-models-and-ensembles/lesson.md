# Module 04: Tree Models and Ensemble Methods
## Decision Trees, Random Forests, Gradient Boosting, XGBoost, LightGBM, and SHAP

### Table of Contents
1. Decision Trees
2. Tree Splitting Criteria (Gini vs Entropy)
3. Tree Pruning
4. Ensemble Methods Overview
5. Random Forests (Bagging)
6. Gradient Boosting
7. XGBoost
8. LightGBM
9. SHAP Values for Model Interpretation

---

## 1. Decision Trees

Decision trees recursively partition the feature space by asking binary questions about features. They create a tree-like model of decisions and their consequences.

### How Decision Trees Work
1. Start with all data at the root node
2. Find the feature and threshold that best splits the data
3. Recursively split child nodes until stopping criteria are met
4. Make predictions based on the majority class (or mean value for regression) in leaf nodes

### Key Concepts
- **Root Node**: Contains all data
- **Internal Nodes**: Contain decision rules
- **Leaf Nodes**: Contain final predictions
- **Depth**: Number of levels in the tree
- **Split Quality**: Measured by Gini impurity or entropy

### Basic Implementation
```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, random_state=42
)

# Create and train decision tree
dt = DecisionTreeClassifier(random_state=42, max_depth=5)
dt.fit(X_train, y_train)

# Make predictions
y_pred = dt.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")

# Feature importance
feature_importance = dt.feature_importances_
print(f"Feature importances: {feature_importance}")
```

### Key Parameters
- **criterion**: 'gini' or 'entropy' (split criterion)
- **max_depth**: Maximum tree depth (prevents overfitting)
- **min_samples_split**: Minimum samples to split a node
- **min_samples_leaf**: Minimum samples in leaf nodes
- **max_features**: Number of features to consider at each split

---

## 2. Tree Splitting Criteria

### Gini Impurity
Measures the probability of incorrectly classifying a randomly chosen element.
- **Formula**: Gini = 1 - Σ(p_i²) where p_i is proportion of class i
- **Range**: 0 (pure) to 0.5 (binary, maximum impurity)
- **Advantage**: Computationally efficient
- **Disadvantage**: Slightly biased toward high-cardinality features

Example: A node with 3 of class A and 1 of class B:
Gini = 1 - (3/4)² - (1/4)² = 1 - 9/16 - 1/16 = 6/16 = 0.375

### Entropy (Information Gain)
Measures the amount of uncertainty in data.
- **Formula**: Entropy = -Σ(p_i × log₂(p_i))
- **Range**: 0 (pure) to log₂(n_classes)
- **Advantage**: More theoretically grounded
- **Disadvantage**: Slightly slower than Gini

Example: Same node:
Entropy = -(3/4 × log₂(3/4) + 1/4 × log₂(1/4)) ≈ 0.811

### Information Gain
The reduction in entropy from splitting:
Information Gain = Entropy(parent) - Σ(proportion × Entropy(child))

### Comparison
```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=200, n_features=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# Gini criterion
dt_gini = DecisionTreeClassifier(criterion='gini', random_state=42)
dt_gini.fit(X_train, y_train)
gini_acc = dt_gini.score(X_test, y_test)

# Entropy criterion
dt_entropy = DecisionTreeClassifier(criterion='entropy', random_state=42)
dt_entropy.fit(X_train, y_train)
entropy_acc = dt_entropy.score(X_test, y_test)

print(f"Gini Accuracy: {gini_acc:.4f}")
print(f"Entropy Accuracy: {entropy_acc:.4f}")
```

---

## 3. Tree Pruning

Pruning removes branches that provide little predictive power, reducing overfitting.

### Cost Complexity Pruning (Post-pruning)
Removes nodes based on a complexity parameter alpha.

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, random_state=42
)

# Grow full tree
dt = DecisionTreeClassifier(random_state=42)
dt.fit(X_train, y_train)

# Get cost complexity pruning path
path = dt.cost_complexity_pruning_path(X_train, y_train)
ccp_alphas = path.ccp_alphas
impurities = path.impurities

# Train models with different alpha values
trees = []
for ccp_alpha in ccp_alphas:
    tree = DecisionTreeClassifier(random_state=42, ccp_alpha=ccp_alpha)
    tree.fit(X_train, y_train)
    trees.append(tree)

# Find best tree using validation set
train_scores = [tree.score(X_train, y_train) for tree in trees]
test_scores = [tree.score(X_test, y_test) for tree in trees]

# Plot validation curves
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot(ccp_alphas, train_scores, marker='o', label='Train Accuracy')
plt.plot(ccp_alphas, test_scores, marker='o', label='Test Accuracy')
plt.xlabel('Alpha')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# Select tree with best test performance
best_idx = np.argmax(test_scores)
best_tree = trees[best_idx]
```

### Pre-pruning
Control tree growth using max_depth, min_samples_split, etc.

```python
dt = DecisionTreeClassifier(
    max_depth=5,
    min_samples_split=10,
    min_samples_leaf=4,
    random_state=42
)
dt.fit(X_train, y_train)
```

---

## 4. Ensemble Methods Overview

Ensemble methods combine multiple models to achieve better performance than any single model.

### Key Principles
- **Diversity**: Models should make different types of errors
- **Accuracy**: Each model should be better than random guessing
- **Independence**: Errors should be uncorrelated

### Types of Ensemble Methods
1. **Bagging**: Train models independently, average predictions
2. **Boosting**: Train models sequentially, each corrects previous errors
3. **Stacking**: Train meta-learner on outputs of base learners
4. **Voting**: Combine diverse models through voting

---

## 5. Random Forests (Bagging)

Random Forests use bagging (Bootstrap AGGregating) with decision trees.

### How Random Forests Work
1. Create multiple bootstrap samples from training data
2. Train a decision tree on each sample
3. For classification: average class probabilities (soft voting) or majority vote (hard voting)
4. For regression: average predictions

### Key Advantages
- Reduces overfitting compared to single tree
- Handles non-linear relationships
- Provides feature importance
- Fast predictions (parallel)
- Works with both categorical and continuous features

### Implementation
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, random_state=42
)

# Create Random Forest
rf = RandomForestClassifier(
    n_estimators=100,        # number of trees
    max_depth=10,            # max tree depth
    min_samples_split=5,     # min samples to split
    min_samples_leaf=2,      # min samples in leaf
    n_jobs=-1,               # use all CPUs
    random_state=42
)

rf.fit(X_train, y_train)
accuracy = rf.score(X_test, y_test)
print(f"Accuracy: {accuracy:.4f}")

# Feature importance
feature_importance = rf.feature_importances_
for name, importance in zip(iris.feature_names, feature_importance):
    print(f"{name}: {importance:.4f}")

# Out-of-bag (OOB) score - built-in validation
rf_oob = RandomForestClassifier(oob_score=True, random_state=42)
rf_oob.fit(X_train, y_train)
print(f"OOB Score: {rf_oob.oob_score_:.4f}")
```

### Parameters
- **n_estimators**: Number of trees (more is better but slower)
- **max_depth**: Maximum tree depth
- **min_samples_split**: Minimum samples required to split a node
- **min_samples_leaf**: Minimum samples required at a leaf node
- **max_features**: Number of features to consider ('sqrt', 'log2', or integer)
- **bootstrap**: Use bootstrap samples (True for bagging)
- **n_jobs**: Number of parallel jobs (-1 for all CPUs)
- **oob_score**: Calculate out-of-bag score

---

## 6. Gradient Boosting

Gradient Boosting builds models sequentially where each model corrects the residual errors of previous models.

### How Gradient Boosting Works
1. Train initial model (often simple)
2. Calculate residuals (actual - predicted)
3. Train next model to predict residuals
4. Add new model to ensemble (with learning rate)
5. Repeat until convergence or max iterations

### Implementation
```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, random_state=42
)

gb = GradientBoostingClassifier(
    n_estimators=100,        # number of boosting stages
    learning_rate=0.1,       # shrinkage parameter
    max_depth=3,             # depth of trees
    min_samples_split=5,
    min_samples_leaf=2,
    subsample=0.8,           # fraction of samples per iteration
    random_state=42
)

gb.fit(X_train, y_train)
accuracy = gb.score(X_test, y_test)
print(f"Accuracy: {accuracy:.4f}")

# Get feature importance
feature_importance = gb.feature_importances_
for name, importance in zip(iris.feature_names, feature_importance):
    print(f"{name}: {importance:.4f}")
```

### Key Parameters
- **n_estimators**: Number of boosting stages
- **learning_rate**: Shrinkage parameter (0 to 1, lower = more conservative)
- **max_depth**: Tree depth (usually 3-5 for boosting)
- **min_samples_split/leaf**: Minimum samples for splitting/leaves
- **subsample**: Fraction of samples for training each tree (< 1 enables stochastic boosting)
- **loss**: Loss function ('deviance' for classification, 'exponential' for AdaBoost)
- **validation_fraction**: Fraction of training set for early stopping

### Learning Rate Effect
- Higher learning_rate: Faster convergence but may overfit
- Lower learning_rate: Slower but more stable, requires more estimators

```python
from sklearn.ensemble import GradientBoostingClassifier

results = {}
for lr in [0.01, 0.05, 0.1, 0.5]:
    gb = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=lr,
        random_state=42
    )
    gb.fit(X_train, y_train)
    results[lr] = gb.score(X_test, y_test)

print(results)
```

---

## 7. XGBoost

XGBoost (eXtreme Gradient Boosting) is an optimized gradient boosting library with:
- Regularization to prevent overfitting
- Parallel processing
- Handling of missing values
- Built-in cross-validation
- Feature importance via multiple methods

### Installation
```bash
pip install xgboost
```

### Implementation
```python
import xgboost as xgb
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, random_state=42
)

# Create XGBoost classifier
xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,    # feature subsampling
    random_state=42,
    n_jobs=-1
)

xgb_model.fit(X_train, y_train)
accuracy = xgb_model.score(X_test, y_test)
print(f"Accuracy: {accuracy:.4f}")

# Feature importance (multiple methods)
importance_gain = xgb_model.get_booster().get_score(importance_type='gain')
importance_weight = xgb_model.get_booster().get_score(importance_type='weight')
importance_cover = xgb_model.get_booster().get_score(importance_type='cover')

# Predictions with different outputs
y_pred = xgb_model.predict(X_test)
y_proba = xgb_model.predict_proba(X_test)
```

### Key Parameters
- **n_estimators**: Number of boosting rounds
- **max_depth**: Maximum tree depth
- **learning_rate** (eta): Shrinkage parameter
- **subsample**: Row sampling ratio
- **colsample_bytree**: Column sampling ratio
- **lambda**: L2 regularization weight
- **alpha**: L1 regularization weight
- **gamma**: Minimum loss reduction to split
- **min_child_weight**: Minimum sum of weights in child node

### Cross-Validation
```python
import xgboost as xgb
from sklearn.model_selection import cross_val_score

xgb_model = xgb.XGBClassifier(random_state=42)
cv_scores = cross_val_score(xgb_model, X_train, y_train, cv=5, scoring='accuracy')
print(f"CV Scores: {cv_scores}")
print(f"Mean CV Score: {cv_scores.mean():.4f}")
```

---

## 8. LightGBM

LightGBM (Light Gradient Boosting Machine) is another optimized boosting library:
- Faster training
- Lower memory usage
- Better with large datasets
- Handles categorical features natively

### Installation
```bash
pip install lightgbm
```

### Implementation
```python
import lightgbm as lgb
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, random_state=42
)

# Create LightGBM classifier
lgb_model = lgb.LGBMClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    num_leaves=31,           # max leaves per tree
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbose=-1               # suppress output
)

lgb_model.fit(X_train, y_train)
accuracy = lgb_model.score(X_test, y_test)
print(f"Accuracy: {accuracy:.4f}")

# Feature importance
feature_importance = lgb_model.feature_importances_
for name, importance in zip(iris.feature_names, feature_importance):
    print(f"{name}: {importance:.4f}")
```

### Key Parameters
- **n_estimators**: Number of boosting rounds
- **max_depth**: Maximum tree depth
- **num_leaves**: Maximum number of leaves per tree
- **learning_rate**: Learning rate
- **subsample**: Row sampling
- **colsample_bytree**: Column sampling
- **lambda_l1**: L1 regularization
- **lambda_l2**: L2 regularization
- **min_child_samples**: Minimum samples in leaf

### Comparison: XGBoost vs LightGBM
| Aspect | XGBoost | LightGBM |
|--------|---------|----------|
| Speed | Slower | Faster |
| Memory | Higher | Lower |
| Categorical | One-hot | Native |
| Small Data | Better | May overfit |
| Large Data | Slower | Better |
| Regularization | Good | Good |

---

## 9. SHAP Values for Model Interpretation

SHAP (SHapley Additive exPlanations) provides theoretically sound model interpretation by computing each feature's contribution to predictions.

### Installation
```bash
pip install shap
```

### Basic Concepts
- **SHAP Value**: Average contribution of a feature to model prediction
- **Base Value**: Average model output
- **Feature Contribution**: How much feature changes prediction from base value
- **Force Plot**: Visualizes feature forces pushing prediction up/down
- **Dependence Plot**: Shows relationship between feature and SHAP value

### Implementation
```python
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Create SHAP explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Summary plot (mean absolute SHAP values)
shap.summary_plot(shap_values[0], X_test, feature_names=iris.feature_names)

# Bar plot (mean absolute SHAP values)
shap.summary_plot(shap_values[0], X_test, feature_names=iris.feature_names, plot_type='bar')

# Force plot for single prediction
shap.force_plot(explainer.expected_value[0], shap_values[0][0], X_test[0],
                feature_names=iris.feature_names)

# Dependence plot
shap.dependence_plot(0, shap_values[0], X_test, feature_names=iris.feature_names)

# Global feature importance
feature_importance = np.abs(shap_values[0]).mean(axis=0)
```

### SHAP Explainers
1. **TreeExplainer**: For tree-based models (fastest)
2. **KernelExplainer**: Model-agnostic, slower but works with any model
3. **DeepExplainer**: For deep learning models
4. **GradientExplainer**: For neural networks

### Interpretation
- **Positive SHAP**: Feature pushes prediction toward higher value
- **Negative SHAP**: Feature pushes prediction toward lower value
- **Magnitude**: How much the feature impacts the prediction
- **Color**: Feature value (red = high, blue = low)

### Example: Feature Interaction
```python
# Dependence plot shows interaction with other features
shap.dependence_plot('sepal length', shap_values[0], X_test,
                     feature_names=iris.feature_names)

# Waterfall plot for single prediction
shap.plots._waterfall.waterfall_legacy(
    explainer.expected_value[0],
    shap_values[0][0],
    X_test[0],
    feature_names=iris.feature_names
)
```

---

## Summary

Tree models and ensemble methods are powerful tools for machine learning:

1. **Decision Trees**: Interpretable but prone to overfitting
2. **Tree Pruning**: Control complexity via post-pruning or pre-pruning parameters
3. **Random Forests**: Robust ensemble with low bias, handles non-linearity
4. **Gradient Boosting**: Sequential training for strong predictive power
5. **XGBoost**: Optimized boosting with regularization and fast training
6. **LightGBM**: Memory-efficient boosting, excellent for large datasets
7. **SHAP**: Provide model-agnostic interpretability for any model

The choice depends on:
- **Dataset Size**: LightGBM for large data, XGBoost for balanced
- **Speed Requirements**: LightGBM fastest, Random Forest good baseline
- **Interpretability**: SHAP works with all models, tree feature importance simpler
- **Regularization Needs**: XGBoost/LightGBM have built-in regularization
