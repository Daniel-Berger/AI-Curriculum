# Module 01: Machine Learning Fundamentals

## Introduction for Swift Developers

If you've built iOS apps with Core ML, you've already used machine learning -- but Core ML
hides the details behind a clean drag-and-drop interface. In this module, we pull back the
curtain. You'll learn what machine learning actually *is*, the vocabulary every ML practitioner
uses daily, and the scikit-learn (sklearn) API that serves as the lingua franca of classical ML
in Python.

Coming from Swift, you'll appreciate sklearn's consistency: every model follows the same
`fit` / `predict` / `score` interface, much like how every SwiftUI view conforms to the `View`
protocol. The difference is that sklearn uses duck typing and conventions instead of protocol
conformance -- welcome to Python.

---

## 1. What Is Machine Learning?

### Formal Definition

Machine learning is the study of algorithms that improve their performance at some task through
experience (data). Tom Mitchell's classic definition:

> A computer program is said to **learn** from experience E with respect to some task T and
> performance measure P, if its performance at T, as measured by P, improves with experience E.

In practical terms: instead of writing explicit rules (`if temperature > 100: alert()`), you
give the algorithm examples and let it discover the rules itself.

### Traditional Programming vs ML

```
Traditional Programming:
    Rules + Data  -->  Program  -->  Output

Machine Learning:
    Data + Output -->  Program  -->  Rules (learned)
```

```python
# Traditional approach: hand-coded rules
def is_spam_rules(email: str) -> bool:
    spam_words = ["free", "winner", "click here", "act now"]
    return any(word in email.lower() for word in spam_words)

# ML approach: learn from labeled examples
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(emails)       # Data
model = MultinomialNB()
model.fit(X, labels)                        # Learn rules from data
predictions = model.predict(X_new)          # Apply learned rules
```

---

## 2. Types of Machine Learning

### Supervised Learning

The algorithm learns from **labeled** data -- inputs paired with correct outputs.

**Regression** -- predict a continuous value:
- House prices, temperature, stock prices
- Output: a number (e.g., $450,000)

**Classification** -- predict a discrete category:
- Spam/not spam, cat/dog/bird, disease/healthy
- Output: a class label (e.g., "spam")

```python
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier

# Regression: predict a continuous value
reg = LinearRegression()
reg.fit(X_train, y_train)         # y_train contains numbers
price = reg.predict(X_new)        # Returns: [450000.0]

# Classification: predict a category
clf = RandomForestClassifier()
clf.fit(X_train, y_train)         # y_train contains labels
label = clf.predict(X_new)        # Returns: ["spam"]
proba = clf.predict_proba(X_new)  # Returns: [[0.1, 0.9]]
```

### Unsupervised Learning

The algorithm finds structure in **unlabeled** data -- no correct answers provided.

**Clustering** -- group similar data points:
- Customer segmentation, document grouping
- Output: cluster assignments

**Dimensionality Reduction** -- compress features while preserving structure:
- PCA, t-SNE, UMAP
- Output: lower-dimensional representation

```python
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Clustering: discover groups
kmeans = KMeans(n_clusters=3)
kmeans.fit(X)                     # No y! Unsupervised
clusters = kmeans.predict(X_new)  # Returns: [0, 2, 1, ...]

# Dimensionality reduction
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X)  # 100 features -> 2 features
```

### Semi-Supervised Learning

Uses a small amount of labeled data plus a large amount of unlabeled data. Common in
real-world scenarios where labeling is expensive (e.g., medical imaging -- getting a doctor
to annotate thousands of X-rays is costly).

```python
# Typical semi-supervised workflow (conceptual):
# 1. Train a model on labeled data
# 2. Use that model to generate "pseudo-labels" for unlabeled data
# 3. Retrain on the combined dataset
# 4. Repeat

from sklearn.semi_supervised import LabelSpreading

# -1 indicates unlabeled samples
labels = [0, 1, -1, -1, -1, 0, -1, 1, -1, -1]
model = LabelSpreading()
model.fit(X, labels)
```

### Self-Supervised Learning

The model generates its own labels from the data structure. This is how modern LLMs (GPT,
Claude) are trained -- predict the next token given previous tokens. The "label" is just the
next word in the text.

Examples:
- **Masked language modeling**: mask a word, predict it (BERT)
- **Next token prediction**: predict the next word (GPT)
- **Contrastive learning**: learn that augmented versions of the same image are similar (SimCLR)

### Reinforcement Learning

The agent learns by interacting with an environment, receiving rewards or penalties.

- **Agent**: the learner/decision-maker
- **Environment**: what the agent interacts with
- **Actions**: what the agent can do
- **Rewards**: feedback signal (positive or negative)
- **Policy**: the strategy the agent learns

Examples: game-playing AI (AlphaGo), robotics, recommendation systems.

```
Agent  --action-->  Environment
Agent  <--reward--  Environment
Agent  <--state---  Environment
```

We won't focus on RL in this curriculum, but it's important to know where it fits.

---

## 3. The ML Workflow

Every ML project follows roughly the same pipeline. Think of it like the iOS development
lifecycle (design -> code -> test -> ship), but for data.

```
1. Problem Definition    What are we predicting? Why?
       |
2. Data Collection       Databases, APIs, scraping, sensors
       |
3. Data Exploration      EDA: distributions, correlations, missing values
       |
4. Data Preprocessing    Clean, transform, encode, scale
       |
5. Feature Engineering   Create new features, select important ones
       |
6. Model Selection       Choose algorithm(s) to try
       |
7. Training              Fit model to training data
       |
8. Evaluation            Measure performance on held-out data
       |
9. Hyperparameter Tuning Optimize model settings
       |
10. Deployment           Serve predictions (API, Core ML, etc.)
       |
11. Monitoring           Track performance over time, retrain as needed
```

```python
# A complete mini-workflow in sklearn
import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score

# 1-2. Generate/collect data
X, y = make_regression(n_samples=1000, n_features=10, noise=20, random_state=42)

# 3. Quick exploration
print(f"Features shape: {X.shape}")   # (1000, 10)
print(f"Target range: [{y.min():.1f}, {y.max():.1f}]")

# 4. Preprocessing: split and scale
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Use same scaling!

# 5-6. Model selection
model = Ridge(alpha=1.0)

# 7. Training
model.fit(X_train_scaled, y_train)

# 8. Evaluation
y_pred = model.predict(X_test_scaled)
print(f"R2:   {r2_score(y_test, y_pred):.4f}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")
```

---

## 4. Bias-Variance Tradeoff

This is arguably the most important concept in ML. Every model's error can be decomposed into
three components:

```
Total Error = Bias^2 + Variance + Irreducible Noise
```

### Bias

**Bias** is the error from oversimplifying the model. A high-bias model makes strong
assumptions and misses patterns in the data.

- **Example**: fitting a straight line to clearly curved data
- **Symptom**: poor performance on *both* training and test data (underfitting)
- **Swift analogy**: like using a `UILabel` when you need a `UITextView` -- the tool is too simple for the job

### Variance

**Variance** is the error from the model being too sensitive to training data. A high-variance
model memorizes noise and doesn't generalize.

- **Example**: fitting a degree-20 polynomial to 10 data points
- **Symptom**: great performance on training data, poor on test data (overfitting)
- **Swift analogy**: like hardcoding pixel positions instead of using Auto Layout -- it works perfectly on one screen but breaks on every other

### The Tradeoff

```
High Bias, Low Variance (Underfitting)
  |
  |  Simple models (linear regression)
  |  Misses true patterns
  |  Consistent but consistently wrong
  |
  |         Sweet Spot
  |         Right complexity for the data
  |         Good generalization
  |
  |  Complex models (deep neural nets)
  |  Captures noise as if it were signal
  |  Great on training data, poor on new data
  |
High Variance, Low Bias (Overfitting)
```

### Visual Intuition

```python
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Generate data with a quadratic relationship
np.random.seed(42)
X = np.sort(np.random.uniform(0, 10, 30)).reshape(-1, 1)
y = 2 * X.ravel() ** 2 - 5 * X.ravel() + 10 + np.random.normal(0, 10, 30)

# Underfitting: degree 1 (too simple)
model_1 = LinearRegression()
model_1.fit(X, y)
print(f"Degree 1 train R2: {model_1.score(X, y):.4f}")  # Low

# Good fit: degree 2 (just right)
poly_2 = PolynomialFeatures(degree=2)
X_poly_2 = poly_2.fit_transform(X)
model_2 = LinearRegression()
model_2.fit(X_poly_2, y)
print(f"Degree 2 train R2: {model_2.score(X_poly_2, y):.4f}")  # High

# Overfitting: degree 15 (too complex)
poly_15 = PolynomialFeatures(degree=15)
X_poly_15 = poly_15.fit_transform(X)
model_15 = LinearRegression()
model_15.fit(X_poly_15, y)
print(f"Degree 15 train R2: {model_15.score(X_poly_15, y):.4f}")  # Very high (suspicious!)
```

---

## 5. Underfitting vs Overfitting

### Underfitting (High Bias)

Signs:
- High training error
- High test error (similar to training error)
- Model is too simple for the data

Solutions:
- Use a more complex model
- Add more features / feature engineering
- Reduce regularization
- Train longer (for iterative algorithms)

### Overfitting (High Variance)

Signs:
- Low training error
- Much higher test error (big gap between train and test)
- Model memorizes training data, including noise

Solutions:
- Get more training data
- Use regularization (L1, L2)
- Simplify the model (fewer features, shallower trees)
- Use dropout (in neural networks)
- Use cross-validation to detect it early
- Early stopping

```python
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Overfitting tree: no depth limit
tree_overfit = DecisionTreeRegressor(max_depth=None)
tree_overfit.fit(X_train, y_train)
print(f"Overfit -- Train R2: {tree_overfit.score(X_train, y_train):.4f}")  # ~1.0
print(f"Overfit -- Test R2:  {tree_overfit.score(X_test, y_test):.4f}")    # Much lower

# Regularized tree: limited depth
tree_good = DecisionTreeRegressor(max_depth=3)
tree_good.fit(X_train, y_train)
print(f"Good -- Train R2: {tree_good.score(X_train, y_train):.4f}")
print(f"Good -- Test R2:  {tree_good.score(X_test, y_test):.4f}")  # Closer to train
```

### How to Diagnose

| Metric | Underfitting | Good Fit | Overfitting |
|--------|-------------|----------|-------------|
| Training error | High | Low | Very low |
| Test error | High | Low (close to train) | High (much > train) |
| Gap (test - train) | Small | Small | Large |

---

## 6. Train/Validation/Test Splits

### Why Split the Data?

If you evaluate a model on the same data it was trained on, you get a misleadingly optimistic
estimate. The model has already seen these examples -- of course it performs well on them!

This is like a student who memorizes the answer key: they'll ace *that* specific test but
fail on new questions.

### The Three Splits

```
Full Dataset
|
|-- Training Set (60-80%)    Model learns from this
|-- Validation Set (10-20%)  Tune hyperparameters against this
|-- Test Set (10-20%)        Final, unbiased evaluation (touch ONCE)
```

**Training set**: The model learns patterns from this data.
**Validation set**: Used to tune hyperparameters (like `alpha` in Ridge regression).
**Test set**: Touched only once, at the very end, to estimate real-world performance.

```python
from sklearn.model_selection import train_test_split

# Two-way split (common for simple experiments)
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,       # 20% for testing
    random_state=42,     # Reproducibility (like a fixed seed in Swift)
    shuffle=True         # Shuffle before splitting (default)
)

# Three-way split
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42  # 0.25 * 0.8 = 0.2
)

print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
```

### Stratified Splits for Classification

When your target has imbalanced classes (e.g., 95% non-fraud, 5% fraud), a random split
might put all fraud cases in the training set, leaving none in the test set. Stratified
splitting preserves class proportions.

```python
from sklearn.model_selection import train_test_split

# Stratified split: preserves class proportions in each split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,          # Ensure each split has same class proportions
    random_state=42
)
```

---

## 7. Cross-Validation

A single train/test split gives one estimate of performance. That estimate depends heavily on
which samples ended up in which set. Cross-validation gives a more robust estimate by
repeating the split multiple times.

### K-Fold Cross-Validation

```
Fold 1: [Test] [Train] [Train] [Train] [Train]
Fold 2: [Train] [Test] [Train] [Train] [Train]
Fold 3: [Train] [Train] [Test] [Train] [Train]
Fold 4: [Train] [Train] [Train] [Test] [Train]
Fold 5: [Train] [Train] [Train] [Train] [Test]

Final score = average of 5 fold scores
```

```python
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import Ridge

model = Ridge(alpha=1.0)

# Quick cross-validation (5-fold by default)
scores = cross_val_score(model, X, y, cv=5, scoring='r2')
print(f"R2 scores: {scores}")
print(f"Mean R2: {scores.mean():.4f} (+/- {scores.std():.4f})")

# Explicit KFold control
kfold = KFold(n_splits=10, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=kfold, scoring='r2')
print(f"10-Fold Mean R2: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

### StratifiedKFold

For classification, use `StratifiedKFold` to preserve class proportions in each fold.

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=1000, n_classes=2, weights=[0.9, 0.1],
                           random_state=42)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
model = LogisticRegression()

scores = cross_val_score(model, X, y, cv=skf, scoring='f1')
print(f"Stratified 5-Fold F1: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

### Leave-One-Out Cross-Validation (LOOCV)

Each fold uses a single sample as the test set. Gives the most unbiased estimate but is
computationally expensive (n folds for n samples).

```python
from sklearn.model_selection import LeaveOneOut, cross_val_score

loo = LeaveOneOut()
scores = cross_val_score(model, X[:100], y[:100], cv=loo)
print(f"LOOCV Mean score: {scores.mean():.4f}")
# Note: LOOCV on 1000 samples = 1000 model fits!
```

### cross_validate for Multiple Metrics

```python
from sklearn.model_selection import cross_validate

results = cross_validate(
    model, X, y, cv=5,
    scoring=['r2', 'neg_mean_squared_error'],
    return_train_score=True
)

print(f"Test R2:   {results['test_r2'].mean():.4f}")
print(f"Train R2:  {results['train_r2'].mean():.4f}")
print(f"Test MSE:  {-results['test_neg_mean_squared_error'].mean():.4f}")
```

---

## 8. Data Leakage

Data leakage is when information from outside the training dataset leaks into the model
during training, giving unrealistically good performance that won't hold up in production.
It's the most common and dangerous mistake in ML.

### What Is It?

**Data leakage** occurs when the model has access to information during training that it
would not have at prediction time.

### Common Sources of Leakage

**1. Target leakage**: A feature is derived from the target variable.
```python
# BAD: "was_fraud_reported" is a consequence of the target "is_fraud"
# The model learns a trivial rule: if reported, then fraud
features = ["transaction_amount", "was_fraud_reported"]  # Leaks target!
```

**2. Train-test contamination**: Preprocessing uses information from the test set.
```python
# BAD: scaler sees test data statistics
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Fits on ALL data including test!
X_train, X_test = X_scaled[:800], X_scaled[800:]

# GOOD: fit scaler on training data only
X_train, X_test = X[:800], X[800:]
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # Fit on train only
X_test_scaled = scaler.transform(X_test)          # Transform test (no fit!)
```

**3. Temporal leakage**: Using future data to predict the past.
```python
# BAD: random split on time series data lets future data "leak" into training
# The model sees tomorrow's data when predicting today

# GOOD: split chronologically
train = data[data["date"] < "2024-01-01"]
test = data[data["date"] >= "2024-01-01"]
```

### How to Avoid Leakage

1. **Always split before preprocessing** -- fit scalers, encoders, etc. on training data only
2. **Use sklearn Pipelines** -- they handle this automatically (Module 07)
3. **Think about causality** -- would this feature be available at prediction time?
4. **Be suspicious of too-good results** -- if your model gets 99.9% accuracy, check for leakage
5. **Use time-based splits for time series** -- never let the future leak into the past

---

## 9. The No Free Lunch Theorem

The No Free Lunch (NFL) theorem states that **no single algorithm is best for all problems**.
Averaged over all possible problems, every algorithm performs equally well.

### What This Means in Practice

- You can't just always use XGBoost or neural networks
- Different data structures and patterns favor different algorithms
- You must try multiple approaches and evaluate on your specific data
- Domain knowledge helps you choose better starting points

```python
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=500, n_features=20, random_state=42)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "SVM": SVC(),
    "KNN": KNeighborsClassifier(),
}

for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f"{name:25s}: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

No single model consistently wins -- it depends on the data. This is NFL in action.

---

## 10. The sklearn API Design

sklearn's greatest strength is its consistent API. Once you learn the pattern, you can use
any of the 100+ algorithms without reading new documentation.

### The Three Core Interfaces

**1. Estimator** -- anything that learns from data:
```python
model.fit(X, y)           # Supervised
model.fit(X)              # Unsupervised
```

**2. Predictor** -- anything that makes predictions:
```python
model.predict(X)          # Predict labels/values
model.predict_proba(X)    # Predict probabilities (classification)
model.score(X, y)         # Evaluate performance
```

**3. Transformer** -- anything that transforms data:
```python
transformer.fit(X)                 # Learn parameters
transformer.transform(X)          # Apply transformation
transformer.fit_transform(X)      # Both in one step
```

### The Consistent Pattern

```python
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Every estimator follows the same pattern:

# Supervised regression
reg = LinearRegression()
reg.fit(X_train, y_train)
predictions = reg.predict(X_test)
score = reg.score(X_test, y_test)

# Supervised classification
clf = RandomForestClassifier()
clf.fit(X_train, y_train)
predictions = clf.predict(X_test)
probabilities = clf.predict_proba(X_test)
score = clf.score(X_test, y_test)

# Unsupervised clustering
km = KMeans(n_clusters=3)
km.fit(X)
labels = km.predict(X_new)

# Transformer
scaler = StandardScaler()
scaler.fit(X_train)
X_scaled = scaler.transform(X_test)
# Or combined:
X_scaled = scaler.fit_transform(X_train)
```

### For Swift Developers: The Protocol Analogy

Think of sklearn's API like Swift protocols:

```swift
// If sklearn were Swift:
protocol Estimator {
    mutating func fit(_ X: [[Double]], _ y: [Double]?)
}

protocol Predictor: Estimator {
    func predict(_ X: [[Double]]) -> [Double]
    func score(_ X: [[Double]], _ y: [Double]) -> Double
}

protocol Transformer: Estimator {
    func transform(_ X: [[Double]]) -> [[Double]]
    func fitTransform(_ X: [[Double]]) -> [[Double]]
}
```

But Python uses duck typing: there's no formal protocol declaration. If an object has a
`fit` method and a `predict` method, it's a predictor -- no explicit conformance needed.

---

## 11. Feature Matrix X and Target Vector y

sklearn has a universal convention for data shapes:

### X: The Feature Matrix

- Shape: `(n_samples, n_features)` -- a 2D array
- Each row is one sample (one observation, one data point)
- Each column is one feature (one attribute, one measurement)
- Always uppercase `X` by convention

### y: The Target Vector

- Shape: `(n_samples,)` -- a 1D array
- Each element is the target/label for the corresponding row in X
- Always lowercase `y` by convention

```python
import numpy as np
from sklearn.datasets import load_iris

# Load a classic dataset
iris = load_iris()
X = iris.data      # (150, 4) -- 150 samples, 4 features
y = iris.target    # (150,)   -- 150 labels

print(f"X shape: {X.shape}")   # (150, 4)
print(f"y shape: {y.shape}")   # (150,)

# Features: sepal length, sepal width, petal length, petal width
print(f"Feature names: {iris.feature_names}")
print(f"Target names:  {iris.target_names}")  # setosa, versicolor, virginica

# First sample
print(f"X[0]: {X[0]}")   # [5.1, 3.5, 1.4, 0.2]
print(f"y[0]: {y[0]}")   # 0 (setosa)
```

### Common sklearn Datasets

```python
from sklearn.datasets import (
    load_iris,              # Classification: 150 samples, 4 features, 3 classes
    load_wine,              # Classification: 178 samples, 13 features, 3 classes
    load_breast_cancer,     # Classification: 569 samples, 30 features, 2 classes
    load_digits,            # Classification: 1797 samples, 64 features, 10 classes
    load_diabetes,          # Regression: 442 samples, 10 features
    load_linnerud,          # Regression: 20 samples, 3 features, 3 targets
    make_classification,    # Generate synthetic classification data
    make_regression,        # Generate synthetic regression data
    make_blobs,             # Generate synthetic clusters
    make_moons,             # Generate two interleaving half circles
    make_circles,           # Generate a large circle containing a small circle
)
```

### Creating Synthetic Data

```python
from sklearn.datasets import make_classification, make_regression

# Classification data
X, y = make_classification(
    n_samples=1000,
    n_features=20,
    n_informative=10,     # 10 features actually carry signal
    n_redundant=5,        # 5 features are linear combos of informative ones
    n_classes=2,
    random_state=42
)

# Regression data
X, y = make_regression(
    n_samples=1000,
    n_features=10,
    n_informative=5,
    noise=10.0,           # Gaussian noise added to output
    random_state=42
)
```

---

## 12. Putting It All Together: A Complete Example

Here's a full workflow that demonstrates every concept from this module.

```python
import numpy as np
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report

# ---- 1. Load data ----
data = load_wine()
X, y = data.data, data.target
print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(data.target_names)} classes")
print(f"Classes: {list(data.target_names)}")

# ---- 2. Split: train + test (stratified) ----
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

# ---- 3. Preprocess (fit on train only!) ----
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ---- 4. Compare models with cross-validation (on training data) ----
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "KNN (k=5)": KNeighborsClassifier(n_neighbors=5),
}

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("\nCross-validation results (on training data):")
best_name, best_score = None, 0
for name, model in models.items():
    scores = cross_val_score(model, X_train_scaled, y_train, cv=skf, scoring='accuracy')
    mean = scores.mean()
    print(f"  {name:25s}: {mean:.4f} (+/- {scores.std():.4f})")
    if mean > best_score:
        best_name, best_score = name, mean

# ---- 5. Final evaluation on test set (only once!) ----
print(f"\nBest model: {best_name}")
best_model = models[best_name]
best_model.fit(X_train_scaled, y_train)
y_pred = best_model.predict(X_test_scaled)

print(f"Test accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"\n{classification_report(y_test, y_pred, target_names=data.target_names)}")
```

---

## Summary: Swift to ML Quick Reference

| ML Concept | Swift/iOS Analogy |
|------------|-------------------|
| Training data | Unit test fixtures |
| Test data | QA/beta testing |
| Overfitting | Hardcoded magic numbers |
| Underfitting | Missing feature implementation |
| Cross-validation | Running tests on multiple devices/OS versions |
| Data leakage | Peeking at test answers during dev |
| Feature matrix X | `[[Double]]` -- array of feature arrays |
| Target vector y | `[Int]` or `[Double]` -- labels/values |
| `model.fit()` | `init(configuration:)` -- learning from data |
| `model.predict()` | `func prediction(from:)` -- Core ML inference |
| `model.score()` | Performance benchmarks |
| sklearn estimator | Swift protocol conformance |
| Bias-variance | Over-engineering vs under-engineering |

---

## Key Takeaways

1. **ML learns rules from data** instead of you writing them by hand.
2. **Supervised learning** (regression + classification) is where you'll spend 80% of your time.
3. **The bias-variance tradeoff** governs model complexity -- too simple = underfitting, too complex = overfitting.
4. **Always split before preprocessing** to avoid data leakage.
5. **Cross-validation** gives more reliable performance estimates than a single train/test split.
6. **sklearn's consistent API** (`fit`/`predict`/`transform`) means learning one model teaches you them all.
7. **No Free Lunch** -- always try multiple models; there's no universally best algorithm.

---

## Next Steps

In Module 02, we'll dive into **Regression** -- starting with linear regression's math
intuition, then exploring regularization with Ridge, Lasso, and ElasticNet. You'll see
the bias-variance tradeoff in action as we tune regularization strength.
