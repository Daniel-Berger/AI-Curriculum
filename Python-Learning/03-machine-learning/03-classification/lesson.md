# Module 03: Classification
## Logistic Regression, SVM, KNN, Naive Bayes, and Classification Metrics

### Table of Contents
1. Classification Fundamentals
2. Logistic Regression
3. Support Vector Machines (SVM)
4. K-Nearest Neighbors (KNN)
5. Naive Bayes
6. Classification Metrics
7. Decision Boundaries
8. Multi-Class Strategies

---

## 1. Classification Fundamentals

Classification is a supervised learning task where we predict discrete categorical labels for inputs. Unlike regression (continuous output), classification outputs belong to a finite set of classes.

**Key Concepts:**
- **Binary Classification**: Two classes (e.g., spam/not spam, disease/no disease)
- **Multi-Class Classification**: More than two classes (e.g., digit recognition 0-9)
- **Class Imbalance**: When classes have very different frequencies
- **Decision Boundary**: The surface that separates different classes in feature space

### Example: Binary Classification Setup
```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import numpy as np

# Create synthetic binary classification dataset
X, y = make_classification(n_samples=200, n_features=2, n_informative=2,
                           n_redundant=0, random_state=42)

# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Dataset shape: {X.shape}")
print(f"Classes: {np.unique(y)}")
print(f"Class distribution: {np.bincount(y)}")
```

---

## 2. Logistic Regression

Despite its name, logistic regression is a **classification** algorithm. It models the probability that an instance belongs to a particular class using the logistic function.

### How It Works
- Uses the **sigmoid function** to convert linear output to probabilities: σ(z) = 1 / (1 + e^(-z))
- Minimizes the **binary cross-entropy loss** function
- Outputs probabilities between 0 and 1
- Naturally extends to multi-class via One-vs-Rest or Multinomial approaches

### Implementation
```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# Standardize features (important for logistic regression)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Create and train logistic regression model
log_reg = LogisticRegression(random_state=42, max_iter=1000)
log_reg.fit(X_train_scaled, y_train)

# Make predictions
y_pred = log_reg.predict(X_test_scaled)

# Get probabilities
y_proba = log_reg.predict_proba(X_test_scaled)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")
print(classification_report(y_test, y_pred))
```

### Key Parameters
- **C**: Inverse of regularization strength (default=1.0)
- **penalty**: Type of regularization ('l2' or 'l1')
- **solver**: Algorithm ('liblinear', 'lbfgs', 'saga', 'newton-cg')
- **max_iter**: Maximum iterations for solver convergence
- **multi_class**: Strategy for multi-class ('auto', 'ovr', 'multinomial')

---

## 3. Support Vector Machines (SVM)

SVM finds the optimal **hyperplane** that maximizes the margin between classes. It uses the **kernel trick** to handle non-linear boundaries efficiently.

### Key Concepts
- **Margin**: Distance between the separating hyperplane and nearest data points
- **Support Vectors**: Data points closest to the decision boundary
- **Kernel Trick**: Maps data to higher dimensions without explicit computation
- **C Parameter**: Trade-off between margin and misclassification

### Kernel Trick Explanation
The kernel trick allows SVM to work in high-dimensional spaces without explicitly computing the transformation. Instead of φ(x)·φ(y), we compute K(x,y) = φ(x)·φ(y) directly.

### Common Kernels
1. **Linear**: K(x,y) = x·y → Linear decision boundary
2. **RBF (Radial Basis Function)**: K(x,y) = exp(-γ||x-y||²) → Non-linear boundary
3. **Polynomial**: K(x,y) = (x·y + 1)^d → Polynomial boundary
4. **Sigmoid**: K(x,y) = tanh(αx·y + c) → Neural-network-like boundary

### Implementation
```python
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# Linear SVM
svm_linear = SVC(kernel='linear', C=1.0, random_state=42)
svm_linear.fit(X_train_scaled, y_train)
y_pred_linear = svm_linear.predict(X_test_scaled)
print(f"Linear SVM Accuracy: {accuracy_score(y_test, y_pred_linear):.4f}")

# RBF SVM (non-linear)
svm_rbf = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)
svm_rbf.fit(X_train_scaled, y_train)
y_pred_rbf = svm_rbf.predict(X_test_scaled)
print(f"RBF SVM Accuracy: {accuracy_score(y_test, y_pred_rbf):.4f}")

# Get decision function scores (not probabilities)
scores = svm_rbf.decision_function(X_test_scaled)
print(f"Decision function scores shape: {scores.shape}")

# For probability estimates (slower, requires probability=True)
svm_prob = SVC(kernel='rbf', probability=True, random_state=42)
svm_prob.fit(X_train_scaled, y_train)
y_proba = svm_prob.predict_proba(X_test_scaled)
```

### Key Parameters
- **kernel**: Type of kernel ('linear', 'rbf', 'poly', 'sigmoid')
- **C**: Regularization parameter (lower C → larger margin, more errors)
- **gamma**: Kernel coefficient for RBF (affects neighborhood size)
- **degree**: Degree of polynomial kernel
- **probability**: Whether to enable probability estimates

---

## 4. K-Nearest Neighbors (KNN)

KNN is an instance-based, non-parametric algorithm. For prediction, it finds the k nearest training examples and makes decisions based on them.

### How It Works
1. For a new point, compute distance to all training points
2. Find the k nearest neighbors
3. For classification: take majority class vote
4. For regression: take mean of neighbor values

### Distance Metrics
- **Euclidean**: √(Σ(x_i - y_i)²) → Default, assumes continuous features
- **Manhattan**: Σ|x_i - y_i| → Better for high-dimensional sparse data
- **Minkowski**: (Σ|x_i - y_i|^p)^(1/p) → Generalization of both
- **Cosine**: 1 - (x·y / ||x||·||y||) → For text/sparse data

### Implementation
```python
from sklearn.neighbors import KNeighborsClassifier

# Try different values of k
for k in [3, 5, 7]:
    knn = KNeighborsClassifier(n_neighbors=k, metric='euclidean')
    knn.fit(X_train_scaled, y_train)
    y_pred = knn.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"KNN (k={k}) Accuracy: {accuracy:.4f}")

# Get probability estimates
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)
y_proba = knn.predict_proba(X_test_scaled)
print(f"Class probabilities shape: {y_proba.shape}")

# Get distances to neighbors
distances, indices = knn.kneighbors(X_test_scaled[:5])
print(f"Distances to 5 nearest neighbors:\n{distances}")
```

### Key Parameters
- **n_neighbors**: Number of neighbors to use (default=5)
- **metric**: Distance metric to use
- **weights**: 'uniform' (equal weight) or 'distance' (inverse distance)
- **algorithm**: 'ball_tree', 'kd_tree', 'brute', or 'auto'

### Advantages and Disadvantages
- **Advantages**: Simple, no training phase, works with any metric
- **Disadvantages**: Slow at prediction time, sensitive to feature scaling, curse of dimensionality

---

## 5. Naive Bayes

Naive Bayes is a probabilistic classifier based on Bayes' theorem. It assumes conditional independence between features given the class (the "naive" assumption).

### Bayes' Theorem
P(Class|Features) = P(Features|Class) × P(Class) / P(Features)

### Implementation
```python
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.metrics import accuracy_score

# Gaussian Naive Bayes (for continuous features)
gnb = GaussianNB()
gnb.fit(X_train, y_train)
y_pred = gnb.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Gaussian NB Accuracy: {accuracy:.4f}")

# Get probabilities
y_proba = gnb.predict_proba(X_test)

# Access learned parameters
print(f"Class priors: {gnb.class_prior_}")
print(f"Class means: {gnb.theta_}")
print(f"Class variances: {gnb.var_}")

# Multinomial Naive Bayes (for count/frequency data like text)
X_counts = np.array([[0, 1, 2], [2, 1, 0], [1, 1, 1], [1, 0, 2]])
y_small = np.array([0, 1, 0, 1])
mnb = MultinomialNB()
mnb.fit(X_counts, y_small)
pred = mnb.predict(X_counts[:2])

# Bernoulli Naive Bayes (for binary features)
bnb = BernoulliNB()
X_binary = np.array([[1, 0, 1], [0, 1, 0], [1, 1, 1]])
bnb.fit(X_binary, y_small[:3])
```

### Types of Naive Bayes
1. **Gaussian NB**: Assumes features follow Gaussian distribution
2. **Multinomial NB**: For discrete count data (text classification)
3. **Bernoulli NB**: For binary/boolean features

### Key Parameters (Gaussian NB)
- **var_smoothing**: Variance smoothing parameter (default=1e-9)

---

## 6. Classification Metrics

Evaluating classification models requires different metrics than regression. We need to consider the specific problem's requirements.

### Confusion Matrix
A confusion matrix shows true positives (TP), false positives (FP), true negatives (TN), and false negatives (FN).

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# Generate confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"Confusion Matrix:\n{cm}")

# Visualize
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Negative', 'Positive'])
disp.plot()
plt.show()
```

### Accuracy
Proportion of correct predictions. Works well for balanced datasets.
- **Formula**: (TP + TN) / (TP + TN + FP + FN)
- **Use when**: All classes are equally important

```python
from sklearn.metrics import accuracy_score

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")
```

### Precision and Recall
- **Precision**: Of positive predictions, how many are correct? TP / (TP + FP)
- **Recall (Sensitivity, True Positive Rate)**: Of actual positives, how many were found? TP / (TP + FN)

```python
from sklearn.metrics import precision_score, recall_score

precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
```

### F1 Score
Harmonic mean of precision and recall. Balances both metrics.
- **Formula**: 2 × (Precision × Recall) / (Precision + Recall)
- **Use when**: Need to balance precision and recall

```python
from sklearn.metrics import f1_score

f1 = f1_score(y_test, y_pred)
print(f"F1 Score: {f1:.4f}")
```

### Specificity and False Positive Rate
- **Specificity (True Negative Rate)**: TN / (TN + FP)
- **False Positive Rate**: FP / (TN + FP)

### ROC-AUC Score
Receiver Operating Characteristic - Area Under Curve measures classifier performance across all thresholds.
- **Range**: 0.5 (random) to 1.0 (perfect)

```python
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt

# Get prediction probabilities
y_proba = log_reg.predict_proba(X_test_scaled)[:, 1]

# Calculate ROC-AUC
roc_auc = roc_auc_score(y_test, y_proba)
print(f"ROC-AUC: {roc_auc:.4f}")

# Plot ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_proba)
plt.plot(fpr, tpr, label=f'ROC Curve (AUC={roc_auc:.3f})')
plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.show()
```

### Classification Report
Comprehensive summary of metrics for each class and overall.

```python
from sklearn.metrics import classification_report

print(classification_report(y_test, y_pred,
                          target_names=['Negative', 'Positive']))
```

### Multi-Class Metrics
For multi-class problems, use averaging strategies:
- **micro**: Calculate metrics globally (useful for imbalanced data)
- **macro**: Calculate metrics for each class and average (unweighted)
- **weighted**: Calculate metrics for each class and average (weighted by support)

```python
from sklearn.metrics import precision_recall_fscore_support

# Multi-class with iris dataset
from sklearn.datasets import load_iris

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

clf = LogisticRegression(max_iter=1000, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

# Get metrics for each class
precision, recall, f1, support = precision_recall_fscore_support(
    y_test, y_pred, average='weighted'
)
print(f"Weighted Precision: {precision:.4f}")
print(f"Weighted Recall: {recall:.4f}")
print(f"Weighted F1: {f1:.4f}")
```

### Choosing the Right Metric

| Scenario | Metric |
|----------|--------|
| Balanced classes, all errors equal | Accuracy |
| False positives costly (spam filter) | Precision |
| False negatives costly (disease detection) | Recall |
| Balance precision/recall | F1 Score |
| Probability ranking important | ROC-AUC |
| Imbalanced classes | Macro F1, Weighted F1 |

---

## 7. Decision Boundaries

Decision boundaries visualize how classifiers partition the feature space. They help understand model behavior and identify overfitting.

### Visualizing Decision Boundaries
```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification

# Create 2D dataset for visualization
X, y = make_classification(n_samples=200, n_features=2, n_informative=2,
                           n_redundant=0, random_state=42)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Create mesh for decision boundary
h = 0.02
x_min, x_max = X_scaled[:, 0].min() - 1, X_scaled[:, 0].max() + 1
y_min, y_max = X_scaled[:, 1].min() - 1, X_scaled[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

# Train classifiers and plot boundaries
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Logistic Regression
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(random_state=42, max_iter=1000)
clf.fit(X_scaled, y)
Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
axes[0, 0].contourf(xx, yy, Z, levels=20, cmap='RdBu')
axes[0, 0].scatter(X_scaled[y==0, 0], X_scaled[y==0, 1], c='blue', edgecolors='k')
axes[0, 0].scatter(X_scaled[y==1, 0], X_scaled[y==1, 1], c='red', edgecolors='k')
axes[0, 0].set_title('Logistic Regression')

# SVM with RBF kernel
from sklearn.svm import SVC
clf = SVC(kernel='rbf', C=1, gamma='scale')
clf.fit(X_scaled, y)
Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
axes[0, 1].contourf(xx, yy, Z, levels=20, cmap='RdBu')
axes[0, 1].scatter(X_scaled[y==0, 0], X_scaled[y==0, 1], c='blue', edgecolors='k')
axes[0, 1].scatter(X_scaled[y==1, 0], X_scaled[y==1, 1], c='red', edgecolors='k')
axes[0, 1].set_title('SVM (RBF Kernel)')

# KNN
from sklearn.neighbors import KNeighborsClassifier
clf = KNeighborsClassifier(n_neighbors=5)
clf.fit(X_scaled, y)
Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
axes[1, 0].contourf(xx, yy, Z, levels=20, cmap='RdBu')
axes[1, 0].scatter(X_scaled[y==0, 0], X_scaled[y==0, 1], c='blue', edgecolors='k')
axes[1, 0].scatter(X_scaled[y==1, 0], X_scaled[y==1, 1], c='red', edgecolors='k')
axes[1, 0].set_title('KNN (k=5)')

# Gaussian Naive Bayes
from sklearn.naive_bayes import GaussianNB
clf = GaussianNB()
clf.fit(X_scaled, y)
Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
axes[1, 1].contourf(xx, yy, Z, levels=20, cmap='RdBu')
axes[1, 1].scatter(X_scaled[y==0, 0], X_scaled[y==0, 1], c='blue', edgecolors='k')
axes[1, 1].scatter(X_scaled[y==1, 0], X_scaled[y==1, 1], c='red', edgecolors='k')
axes[1, 1].set_title('Gaussian Naive Bayes')

plt.tight_layout()
plt.show()
```

### Insights from Decision Boundaries
- **Linear boundaries** (Logistic Regression): Simple, fast, good for linearly separable data
- **Curved boundaries** (SVM RBF, KNN): Flexible, can capture complex patterns
- **Overfitting**: Very jagged boundaries with many regions indicate overfitting
- **Underfitting**: Too-simple boundaries may miss important patterns

---

## 8. Multi-Class Strategies

When a problem has more than two classes, we need strategies to extend binary classifiers to multi-class.

### One-vs-Rest (OvR)
For k classes, train k binary classifiers. Classifier i distinguishes class i from all others.

```python
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

# SVM doesn't natively support multi-class in the way we want,
# so we use OneVsRestClassifier
ovr = OneVsRestClassifier(SVC(kernel='rbf', probability=True, random_state=42))
ovr.fit(X_train, y_train)
y_pred = ovr.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"OneVsRest Accuracy: {accuracy:.4f}")
```

### One-vs-One (OvO)
For k classes, train k(k-1)/2 binary classifiers. Each classifier distinguishes between two classes.

```python
from sklearn.multiclass import OneVsOneClassifier

ovo = OneVsOneClassifier(SVC(kernel='rbf', probability=True, random_state=42))
ovo.fit(X_train, y_train)
y_pred = ovo.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"OneVsOne Accuracy: {accuracy:.4f}")
```

### Multinomial Strategy
Some classifiers (Logistic Regression, Naive Bayes) natively handle multi-class.

```python
# Logistic Regression with multinomial strategy
clf = LogisticRegression(multi_class='multinomial', max_iter=1000, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Logistic Regression (Multinomial) Accuracy: {accuracy:.4f}")

# View class probabilities for each sample
y_proba = clf.predict_proba(X_test[:5])
print(f"Probabilities for first 5 samples:\n{y_proba}")
```

### Comparison
- **OvR**: Trains fewer classifiers, faster, works for most algorithms
- **OvO**: More classifiers, slower, can be more accurate with SVM
- **Multinomial**: Only for algorithms supporting it natively, usually fastest

---

## Summary

Classification is a fundamental ML task with diverse algorithms and evaluation metrics:

1. **Logistic Regression**: Fast, interpretable, good baseline
2. **SVM**: Powerful with kernel trick, handles non-linear data
3. **KNN**: Simple, intuitive, works with any distance metric
4. **Naive Bayes**: Fast, probabilistic, effective for text
5. **Metrics**: Choose based on problem requirements (FP/FN costs, class imbalance)
6. **Decision Boundaries**: Visualize to understand model behavior
7. **Multi-Class**: Use OvR, OvO, or native strategies as needed

The choice of algorithm depends on dataset size, feature types, interpretability needs, and computational constraints.
