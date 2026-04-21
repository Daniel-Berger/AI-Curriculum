# Machine Learning Phase 3 Quiz
## Comprehensive Assessment Across All 8 Modules

**Instructions:**
- 30 questions total (10 Easy, 12 Medium, 8 Hard)
- Mix of multiple choice, short answer, and code-writing questions
- Answer key provided at bottom
- Time limit: 2-3 hours for complete quiz

---

## EASY QUESTIONS (10 points each)

### 1. Classification Basics
What is the output of logistic regression for a binary classification problem?
a) A continuous value between 0 and 1 (probability)
b) A discrete class label (0 or 1)
c) Multiple class probabilities
d) A distance value

**Answer: a**

---

### 2. Decision Trees
Which splitting criterion is used by default in scikit-learn's DecisionTreeClassifier?
a) Entropy
b) Gini impurity
c) Information gain
d) Chi-square

**Answer: b**

---

### 3. Ensemble Methods
What is bagging in the context of ensemble methods?
a) Bootstrap AGGregating - training multiple models on bootstrap samples and averaging predictions
b) Stacking multiple models sequentially
c) Weighting samples by their importance
d) Removing outliers from data

**Answer: a**

---

### 4. Random Forest
Which statement about Random Forests is true?
a) They are strictly worse than single decision trees
b) They can reduce overfitting by averaging multiple trees
c) They require scaled features
d) They cannot handle categorical features

**Answer: b**

---

### 5. Gradient Boosting
In Gradient Boosting, what does each new tree attempt to do?
a) Predict the same target as the first tree
b) Predict the residual errors of previous trees
c) Reduce the number of features
d) Create the largest possible tree

**Answer: b**

---

### 6. SVM Kernel Trick
What is the main advantage of the kernel trick in SVM?
a) It reduces the number of support vectors
b) It allows non-linear decision boundaries without explicit transformation to high dimensions
c) It guarantees convexity
d) It speeds up training on very large datasets

**Answer: b**

---

### 7. KNN
What is the computational complexity of making a prediction with k-NN for a new point?
a) O(log n) where n is training set size
b) O(n) where n is training set size
c) O(k) where k is number of neighbors
d) O(1) constant time

**Answer: b**

---

### 8. Pipelines
What is the main benefit of using sklearn pipelines?
a) They make code shorter
b) They prevent data leakage during preprocessing and ensure consistent transformations
c) They automatically tune hyperparameters
d) They reduce memory usage

**Answer: b**

---

### 9. MLflow Basics
What is an MLflow experiment?
a) A single model training run
b) A collection of related runs for comparing models/hyperparameters
c) A hyperparameter search
d) A version of a trained model

**Answer: b**

---

### 10. Naive Bayes
What key assumption does Naive Bayes make about features?
a) All features are normally distributed
b) Features are conditionally independent given the class label
c) Features must be scaled
d) Features must be numeric

**Answer: b**

---

## MEDIUM QUESTIONS (15 points each)

### 11. Confusion Matrix and Metrics
For a medical test predicting disease (positive) vs no disease (negative), which metric is most important when false negatives (missing disease) are very costly?

a) Precision
b) Recall (Sensitivity)
c) Specificity
d) Accuracy

**Answer: b** - Recall is important because we want to catch all actual positive cases (minimize false negatives).

---

### 12. ROC Curves and AUC
A classifier has an AUC-ROC score of 0.5. What does this indicate?

a) The classifier is perfect
b) The classifier is random (no better than chance)
c) The classifier is terrible
d) We need more data

**Answer: b** - AUC of 0.5 indicates random guessing (1.0 is perfect, 0 is inverse perfect).

---

### 13. Feature Importance
What does feature importance in tree-based models measure?

a) How important the feature is to the domain expert
b) How much each feature contributes to reducing impurity in splits
c) The correlation between feature and target
d) The variance of the feature

**Answer: b** - Tree feature importance is based on how much impurity (Gini or entropy) is reduced by splits on that feature.

---

### 14. Hyperparameter Tuning
What is the main risk when using GridSearchCV on the same test set that was used during model development?

a) It will take too long
b) Data leakage / overfitting to the test set
c) The model will be underfitting
d) Memory requirements will be too high

**Answer: b** - Using the test set for hyperparameter tuning causes overfitting to that specific test set.

---

### 15. Cross-Validation
If a dataset has 100 samples and we use 5-fold cross-validation, how many samples are in the validation set of each fold?

a) 5 samples
b) 20 samples
c) 50 samples
d) 95 samples

**Answer: b** - Each fold contains 100/5 = 20 samples.

---

### 16. Preprocessing
What should you do to prevent data leakage when preprocessing?

a) Fit the scaler on the entire dataset then transform both train and test
b) Fit the scaler on training data, then transform both train and test using those parameters
c) Fit different scalers for train and test sets
d) Don't use preprocessing at all

**Answer: b** - Fit preprocessing on training data only, then apply the same transformation to test data.

---

### 17. ColumnTransformer
What is the main purpose of ColumnTransformer?

a) To select the most important columns
b) To apply different preprocessing pipelines to different column types (numeric vs categorical)
c) To rename columns
d) To aggregate columns

**Answer: b** - ColumnTransformer applies different preprocessing to different feature types.

---

### 18. Autologging
What does MLflow autologging do?

a) Automatically logs parameters, metrics, and models without explicit logging code
b) Automatically tunes hyperparameters
c) Automatically splits data
d) Automatically saves the code

**Answer: a** - Autologging captures model details automatically when enabled.

---

### 19. Model Registry
What is the purpose of the MLflow Model Registry?

a) To track code versions
b) To store and manage model versions with staging (dev/staging/production)
c) To log training metrics
d) To visualize data

**Answer: b** - Model Registry is for centralized model version management and lifecycle tracking.

---

### 20. Learning Rate in Boosting
What happens if the learning rate in gradient boosting is set too high?

a) The model trains slower
b) The model may overshoot and diverge or overfit
c) The model underfits
d) More trees are needed

**Answer: b** - High learning rate leads to instability or overfitting; lower values are more conservative.

---

### 21. One-vs-Rest Classification
For 5-class multi-class classification, how many binary classifiers does One-vs-Rest train?

a) 5
b) 10 (5 choose 2)
c) 1
d) 25

**Answer: a** - One-vs-Rest trains one binary classifier per class (5 in this case).

---

### 22. Model Evaluation with Imbalanced Data
For imbalanced classification (e.g., 95% negative, 5% positive), which metric is misleading?

a) Accuracy
b) F1 score
c) Precision and Recall
d) ROC-AUC

**Answer: a** - Accuracy is misleading because a model predicting all negatives would get 95% accuracy.

---

## HARD QUESTIONS (25 points each)

### 23. Tree Pruning - Code Writing
Write code to perform cost-complexity pruning on a decision tree. Find the optimal alpha value using cross-validation on a validation set.

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
import numpy as np

def find_optimal_alpha(X_train, X_val, y_train, y_val):
    """
    Find optimal complexity parameter alpha for pruning.

    Returns: (best_tree, best_alpha)
    """
    # Grow full tree
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(X_train, y_train)

    # Get cost-complexity pruning path
    path = dt.cost_complexity_pruning_path(X_train, y_train)
    ccp_alphas = path.ccp_alphas

    # Train trees with different alphas
    trees = []
    for alpha in ccp_alphas:
        tree = DecisionTreeClassifier(ccp_alpha=alpha, random_state=42)
        tree.fit(X_train, y_train)
        trees.append(tree)

    # Evaluate on validation set
    val_scores = [tree.score(X_val, y_val) for tree in trees]

    # Find best
    best_idx = np.argmax(val_scores)
    best_tree = trees[best_idx]
    best_alpha = ccp_alphas[best_idx]

    return best_tree, best_alpha
```

**Sample Answer (accept similar variations):**
The key elements are:
- Using `cost_complexity_pruning_path()` to get alpha values
- Training multiple trees with different alphas
- Evaluating on validation set (not training set)
- Returning the tree with best validation score

---

### 24. SHAP Interpretation - Code Writing
Write code to compute and visualize SHAP feature importance for a trained model.

```python
import shap
import matplotlib.pyplot as plt

def explain_model_with_shap(model, X_test, feature_names):
    """
    Compute SHAP values and plot feature importance.
    """
    # Create SHAP explainer (for tree models)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # For binary classification, use shap_values[1] (positive class)
    if isinstance(shap_values, list):
        shap_values_to_plot = shap_values[1]
    else:
        shap_values_to_plot = shap_values

    # Plot summary (bar plot)
    shap.summary_plot(shap_values_to_plot, X_test,
                      feature_names=feature_names, plot_type='bar')
    plt.show()

    # Get mean absolute SHAP values for feature importance
    feature_importance = np.abs(shap_values_to_plot).mean(axis=0)
    return feature_importance
```

**Sample Answer (accept similar variations):**
Key elements:
- Using `shap.TreeExplainer` for tree-based models
- Handling list vs array output from explainer
- Using `summary_plot` for visualization
- Computing mean absolute SHAP for importance

---

### 25. Custom Transformer - Code Writing
Write a custom sklearn transformer that applies log transformation to numeric features.

```python
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

class LogTransformer(BaseEstimator, TransformerMixin):
    """Apply log1p transformation to features."""

    def __init__(self, columns=None):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_copy = X.copy() if isinstance(X, np.ndarray) else X.copy()
        if self.columns is None:
            return np.log1p(X_copy)
        else:
            for col in self.columns:
                X_copy[col] = np.log1p(X_copy[col])
        return X_copy
```

**Sample Answer (accept similar variations):**
Must include:
- Inheritance from `BaseEstimator` and `TransformerMixin`
- `fit()` method returning `self`
- `transform()` method doing actual transformation
- Proper handling of data (copy to avoid modifying original)

---

### 26. Gradient Boosting vs XGBoost
Compare and contrast Gradient Boosting, XGBoost, and LightGBM. When would you choose each?

**Expected Answer (key points):**
- **Gradient Boosting (sklearn):** Basic implementation, good for learning/understanding, slower on large datasets
- **XGBoost:** Optimized version with regularization, faster than sklearn, handles missing values, more hyperparameters
- **LightGBM:** Fastest for large datasets, lowest memory, uses leaf-wise tree growth, categorical feature support

**Choice criteria:**
- Small to medium dataset → Gradient Boosting or XGBoost
- Large dataset → LightGBM
- Need interpretability → Gradient Boosting
- Competition/production → XGBoost or LightGBM

---

### 27. Pipeline with GridSearch - Code Writing
Write code to perform grid search over pipeline hyperparameters (both preprocessing and model).

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

def grid_search_pipeline(X, y):
    """Grid search over pipeline and model hyperparameters."""

    # Create pipeline
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('rf', RandomForestClassifier(random_state=42))
    ])

    # Parameter grid
    param_grid = {
        'rf__n_estimators': [50, 100],
        'rf__max_depth': [5, 10, None],
        'rf__min_samples_split': [2, 5]
    }

    # Grid search
    gs = GridSearchCV(pipe, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
    gs.fit(X, y)

    print(f"Best params: {gs.best_params_}")
    print(f"Best score: {gs.best_score_:.4f}")

    return gs.best_estimator_
```

**Sample Answer (accept similar variations):**
Key elements:
- Pipeline with preprocessing + model
- Parameter grid with `__` notation for pipeline steps
- GridSearchCV with appropriate cv and scoring
- Returning best estimator

---

### 28. MLflow Experiment Tracking - Code Writing
Write code to track a hyperparameter tuning experiment with MLflow, logging results for each configuration.

```python
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

def track_hyperparameter_tuning(X_train, X_test, y_train, y_test):
    """Track multiple model configurations in MLflow."""

    mlflow.set_experiment("RandomForest Tuning")

    param_grids = [
        {'n_estimators': 50, 'max_depth': 5},
        {'n_estimators': 100, 'max_depth': 10},
        {'n_estimators': 200, 'max_depth': 15},
    ]

    for params in param_grids:
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(params)

            # Train model
            model = RandomForestClassifier(**params, random_state=42)
            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')

            # Log metrics
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("f1", f1)

            # Log model
            mlflow.sklearn.log_model(model, "model")

    # Print best run
    client = mlflow.tracking.MlflowClient()
    runs = client.search_runs(experiment_names=["RandomForest Tuning"])
    best_run = max(runs, key=lambda r: r.data.metrics['accuracy'])
    print(f"Best accuracy: {best_run.data.metrics['accuracy']:.4f}")
```

**Sample Answer (accept similar variations):**
Key elements:
- `mlflow.set_experiment()` for organization
- Loop through parameters
- `mlflow.start_run()` context manager
- `mlflow.log_params()` and `mlflow.log_metrics()`
- `mlflow.sklearn.log_model()`
- Optional: searching/analyzing runs

---

### 29. Multi-Class Classification Strategy
For a 10-class classification problem, explain when you would use:
a) One-vs-Rest (OvR)
b) One-vs-One (OvO)
c) Native multinomial

Discuss computational complexity and practical considerations.

**Expected Answer:**
- **OvR:** Trains 10 binary classifiers. Faster. Good for most algorithms. Can be problematic with very imbalanced classes.
- **OvO:** Trains 45 (10 choose 2) classifiers. Slower but often more accurate. Mainly used with SVM.
- **Native Multinomial:** Direct multi-class (Logistic Regression, Naive Bayes). Fastest and preferred when available.

**Recommendation:** Use native multinomial when available, otherwise OvR for speed or OvO for accuracy if computational budget allows.

---

### 30. End-to-End Pipeline Design
Design a complete ML pipeline for predicting customer churn. Include:
1. Data preprocessing steps
2. Feature engineering considerations
3. Model selection and comparison
4. Evaluation strategy
5. Deployment considerations

**Expected Answer (key components):**

1. **Preprocessing:**
   - Handle missing values (imputation strategy)
   - Encode categorical features (one-hot encoding)
   - Scale numeric features (StandardScaler)
   - Handle class imbalance (oversampling/undersampling)

2. **Feature Engineering:**
   - Create interaction features
   - Derive time-based features if applicable
   - Remove low-variance features
   - Select relevant features using feature importance

3. **Model Selection:**
   - Compare: Logistic Regression (baseline), Random Forest, Gradient Boosting
   - Use cross-validation for robust evaluation
   - Tune hyperparameters with GridSearchCV

4. **Evaluation:**
   - Use appropriate metrics (Recall important for churn - don't miss churners)
   - Check precision/recall tradeoff
   - ROC-AUC for threshold selection
   - Business metrics (cost of false positives vs false negatives)

5. **Deployment:**
   - Save model with MLflow Model Registry
   - Version preprocessing pipeline
   - Monitor model performance on new data
   - Plan retraining schedule
   - Set up prediction service

---

# ANSWER KEY SUMMARY

## Easy (1-10)
1. a | 2. b | 3. a | 4. b | 5. b | 6. b | 7. b | 8. b | 9. b | 10. b

## Medium (11-22)
11. b | 12. b | 13. b | 14. b | 15. b | 16. b | 17. b | 18. a | 19. b | 20. b | 21. a | 22. a

## Hard (23-30)
23-30: See model answers above. Accept reasonable variations that demonstrate understanding.

---

## Scoring Guide

- **Easy (1-10):** 10 points each = 100 points
- **Medium (11-22):** 15 points each = 180 points
- **Hard (23-30):** 25 points each = 200 points
- **Total:** 480 points

### Grading Scale
- 432-480: A (90-100%)
- 384-431: B (80-89%)
- 336-383: C (70-79%)
- 288-335: D (60-69%)
- Below 288: F (below 60%)
