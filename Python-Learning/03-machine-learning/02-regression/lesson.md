# Module 02: Regression

## Introduction for Swift Developers

Regression is the ML task of predicting a continuous value -- a house price, a temperature,
a user engagement score. If you've ever used Core ML to predict a number from features, the
model behind it was almost certainly a regression model.

In this module, we start with the simplest and most interpretable model (linear regression),
build mathematical intuition, then explore regularization techniques (Ridge, Lasso, ElasticNet)
that prevent overfitting. You'll learn to evaluate regression models with proper metrics and
diagnose problems through residual analysis.

Coming from Swift, think of regularization like memory management: just as ARC prevents memory
leaks by adding constraints, regularization prevents overfitting by constraining model weights.

---

## 1. Linear Regression: Math Intuition

### The Core Idea

Linear regression fits a line (or hyperplane) through data to minimize prediction error.
For a single feature:

```
y = w0 + w1 * x

where:
  y  = predicted value (target)
  x  = feature (input)
  w0 = intercept (bias term)
  w1 = slope (weight/coefficient)
```

For multiple features:

```
y = w0 + w1*x1 + w2*x2 + ... + wn*xn

In vector notation:
y = X @ w + b

where:
  X = feature matrix (n_samples, n_features)
  w = weight vector (n_features,)
  b = bias/intercept (scalar)
```

### What "Fit" Means

"Fitting" linear regression means finding the weights `w` and intercept `b` that minimize
the sum of squared errors between predictions and actual values:

```
Loss = sum((y_actual - y_predicted)^2)
     = sum((y - (X @ w + b))^2)
```

This is called **Ordinary Least Squares (OLS)**.

### The Normal Equation (Closed-Form Solution)

For linear regression, there's an exact mathematical solution:

```
w = (X^T X)^(-1) X^T y
```

This directly computes the optimal weights without iteration. sklearn uses a more
numerically stable variant (based on SVD decomposition).

```python
import numpy as np

# Manual normal equation (for understanding only -- use sklearn in practice)
def normal_equation(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Compute linear regression weights using the normal equation."""
    # Add bias column (column of 1s)
    X_b = np.column_stack([np.ones(len(X)), X])
    # w = (X^T X)^(-1) X^T y
    w = np.linalg.inv(X_b.T @ X_b) @ X_b.T @ y
    return w  # w[0] is intercept, w[1:] are coefficients

# Example
X = np.array([[1], [2], [3], [4], [5]], dtype=float)
y = np.array([2.1, 4.0, 5.9, 8.1, 10.0])

w = normal_equation(X, y)
print(f"Intercept: {w[0]:.2f}, Slope: {w[1]:.2f}")
# Output: Intercept: 0.04, Slope: 1.99
```

### Gradient Descent (Iterative Approach)

For large datasets, the normal equation is expensive (matrix inversion is O(n^3)). Gradient
descent iteratively updates weights by moving in the direction that reduces the loss:

```
Repeat until convergence:
    gradient = -2/n * X^T @ (y - X @ w)
    w = w - learning_rate * gradient
```

```python
def gradient_descent(X: np.ndarray, y: np.ndarray,
                     lr: float = 0.01, n_iter: int = 1000) -> np.ndarray:
    """Compute linear regression weights using gradient descent."""
    X_b = np.column_stack([np.ones(len(X)), X])
    n = len(X)
    w = np.zeros(X_b.shape[1])

    for _ in range(n_iter):
        predictions = X_b @ w
        errors = predictions - y
        gradient = (2 / n) * X_b.T @ errors
        w -= lr * gradient

    return w
```

In practice, you'll never implement gradient descent by hand. sklearn and other libraries
handle this for you. But understanding the concept is essential for tuning learning rates
and understanding optimization in deep learning.

---

## 2. sklearn LinearRegression

```python
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
import numpy as np

# Generate data
X, y = make_regression(n_samples=200, n_features=3, noise=15, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit
model = LinearRegression()
model.fit(X_train, y_train)

# Inspect learned parameters
print(f"Intercept: {model.intercept_:.4f}")
print(f"Coefficients: {model.coef_}")
# Output: array of 3 weights, one per feature

# Predict
y_pred = model.predict(X_test)
print(f"First 5 predictions: {y_pred[:5]}")

# Score (R2)
r2 = model.score(X_test, y_test)
print(f"R2 Score: {r2:.4f}")
```

### Accessing Model Parameters

After fitting, sklearn models expose learned parameters as attributes ending with `_`:

```python
model.coef_       # Array of feature weights: shape (n_features,)
model.intercept_  # Bias term: scalar
model.n_features_in_  # Number of features the model was trained on
```

This naming convention (`trailing_underscore_`) is universal in sklearn: any attribute
that is learned from data gets an underscore suffix. It's like a Swift property that's
only available after initialization.

---

## 3. Polynomial Regression

Linear regression can model nonlinear relationships by adding polynomial features.
The model is still "linear" in its parameters -- it's just operating on transformed inputs.

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
import numpy as np

# Generate nonlinear data
np.random.seed(42)
X = np.sort(np.random.uniform(0, 5, 50)).reshape(-1, 1)
y = 2 * X.ravel()**2 - 3 * X.ravel() + 5 + np.random.normal(0, 3, 50)

# PolynomialFeatures transforms [x] into [1, x, x^2, x^3, ...]
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
print(f"Original feature: {X[0]}")       # [0.18]
print(f"Polynomial features: {X_poly[0]}")  # [0.18, 0.033]  (x and x^2)

# Fit linear regression on polynomial features
model = LinearRegression()
model.fit(X_poly, y)
print(f"Coefficients: {model.coef_}")  # Coefficients for x and x^2
print(f"Intercept: {model.intercept_:.4f}")

# Using make_pipeline for clean workflow
poly_model = make_pipeline(
    PolynomialFeatures(degree=2, include_bias=False),
    LinearRegression()
)
poly_model.fit(X, y)
predictions = poly_model.predict(X)
```

### Danger: High-Degree Polynomials

```python
# Degree 2: good fit
# Degree 5: starting to overfit
# Degree 15: extreme overfitting -- fits noise, not signal

for degree in [1, 2, 5, 15]:
    model = make_pipeline(
        PolynomialFeatures(degree=degree, include_bias=False),
        LinearRegression()
    )
    model.fit(X, y)
    train_r2 = model.score(X, y)
    print(f"Degree {degree:2d}: Train R2 = {train_r2:.4f}")
    # Train R2 keeps increasing, but test R2 would drop for high degrees
```

---

## 4. Regularization Motivation

Why do high-degree polynomials overfit? Because the model has too many parameters and too
much freedom. The coefficients become very large to fit every training point exactly.

**Regularization** adds a penalty for large coefficients, forcing the model to be simpler:

```
Loss = sum((y - y_pred)^2)  +  alpha * penalty(weights)
       |_________________|     |_____________________|
       Data fit term           Regularization term
```

- `alpha = 0`: no regularization (standard linear regression)
- `alpha = small`: slight regularization, small weights preferred
- `alpha = large`: strong regularization, weights pushed toward zero

Think of alpha as a "complexity budget": higher alpha means the model gets less freedom
to use large weights.

---

## 5. Ridge Regression (L2 Regularization)

Ridge regression adds the sum of squared weights as a penalty:

```
Loss = sum((y - y_pred)^2)  +  alpha * sum(w_i^2)
```

This shrinks all coefficients toward zero but never makes them exactly zero. All features
stay in the model, just with reduced influence.

```python
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_regression
import numpy as np

X, y = make_regression(n_samples=200, n_features=50, n_informative=10,
                       noise=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Always scale features before regularization!
# Regularization penalizes large weights -- if features are on different scales,
# the penalty affects them unevenly.
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# Compare different alpha values
for alpha in [0.01, 0.1, 1.0, 10.0, 100.0]:
    ridge = Ridge(alpha=alpha)
    ridge.fit(X_train_s, y_train)
    train_r2 = ridge.score(X_train_s, y_train)
    test_r2 = ridge.score(X_test_s, y_test)
    n_small = np.sum(np.abs(ridge.coef_) < 0.1)
    print(f"alpha={alpha:6.2f}  Train R2={train_r2:.4f}  Test R2={test_r2:.4f}  "
          f"Small coefficients: {n_small}/50")
```

### Why Scale Before Regularization?

If feature A is measured in meters (values 0-100) and feature B is measured in millimeters
(values 0-100000), the coefficient for B will naturally be much smaller. L2 penalty treats
all coefficients equally, so without scaling, it would penalize the large-value feature
less than it should.

---

## 6. Lasso Regression (L1 Regularization)

Lasso uses the sum of absolute values as a penalty:

```
Loss = sum((y - y_pred)^2)  +  alpha * sum(|w_i|)
```

The key difference from Ridge: **Lasso drives some coefficients to exactly zero**, effectively
performing feature selection. Features with zero coefficients are removed from the model.

```python
from sklearn.linear_model import Lasso

# Same data as Ridge example
lasso = Lasso(alpha=0.1)
lasso.fit(X_train_s, y_train)

print(f"Train R2: {lasso.score(X_train_s, y_train):.4f}")
print(f"Test R2:  {lasso.score(X_test_s, y_test):.4f}")

# Count zero coefficients (feature selection!)
n_zero = np.sum(lasso.coef_ == 0)
n_nonzero = np.sum(lasso.coef_ != 0)
print(f"Zero coefficients: {n_zero}/50")
print(f"Non-zero coefficients: {n_nonzero}/50")

# Compare with different alphas
for alpha in [0.01, 0.1, 1.0, 10.0]:
    lasso = Lasso(alpha=alpha, max_iter=10000)
    lasso.fit(X_train_s, y_train)
    n_zero = np.sum(lasso.coef_ == 0)
    print(f"alpha={alpha:5.2f}: {n_zero} zero coefficients, "
          f"Test R2={lasso.score(X_test_s, y_test):.4f}")
```

### Ridge vs Lasso: When to Use Which

| Aspect | Ridge (L2) | Lasso (L1) |
|--------|-----------|-----------|
| Penalty | sum(w^2) | sum(|w|) |
| Effect on coefficients | Shrinks toward zero | Drives some to exactly zero |
| Feature selection | No | Yes |
| When many relevant features | Better | Worse (may drop important ones) |
| When few relevant features | Decent | Better (finds the important ones) |
| Correlated features | Keeps all, shares weight | Arbitrarily picks one |

---

## 7. ElasticNet (L1 + L2)

ElasticNet combines both penalties, getting the best of both worlds:

```
Loss = sum((y - y_pred)^2)  +  alpha * (l1_ratio * sum(|w_i|) + (1-l1_ratio)/2 * sum(w_i^2))
```

- `l1_ratio=1.0`: pure Lasso
- `l1_ratio=0.0`: pure Ridge
- `l1_ratio=0.5`: equal mix (common starting point)

```python
from sklearn.linear_model import ElasticNet

# Try different l1_ratios
for l1_ratio in [0.1, 0.3, 0.5, 0.7, 0.9]:
    enet = ElasticNet(alpha=0.1, l1_ratio=l1_ratio, max_iter=10000)
    enet.fit(X_train_s, y_train)
    n_zero = np.sum(enet.coef_ == 0)
    test_r2 = enet.score(X_test_s, y_test)
    print(f"l1_ratio={l1_ratio:.1f}: {n_zero} zero coefs, Test R2={test_r2:.4f}")
```

### Choosing Between Ridge, Lasso, ElasticNet

```python
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV

# Use built-in CV variants that automatically find the best alpha!
ridge_cv = RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0, 100.0])
ridge_cv.fit(X_train_s, y_train)
print(f"Best Ridge alpha: {ridge_cv.alpha_}")
print(f"Ridge Test R2: {ridge_cv.score(X_test_s, y_test):.4f}")

lasso_cv = LassoCV(alphas=[0.001, 0.01, 0.1, 1.0], cv=5, max_iter=10000)
lasso_cv.fit(X_train_s, y_train)
print(f"Best Lasso alpha: {lasso_cv.alpha_}")
print(f"Lasso Test R2: {lasso_cv.score(X_test_s, y_test):.4f}")

enet_cv = ElasticNetCV(l1_ratio=[0.1, 0.5, 0.7, 0.9, 0.95], cv=5, max_iter=10000)
enet_cv.fit(X_train_s, y_train)
print(f"Best ElasticNet alpha: {enet_cv.alpha_:.4f}, l1_ratio: {enet_cv.l1_ratio_}")
print(f"ElasticNet Test R2: {enet_cv.score(X_test_s, y_test):.4f}")
```

---

## 8. Hyperparameter Tuning for Regularization

The `alpha` parameter is a **hyperparameter** -- it's not learned from data but set by you.
Beyond the `*CV` variants above, you can use GridSearchCV for more control:

```python
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Ridge

param_grid = {
    'alpha': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
}

grid_search = GridSearchCV(
    Ridge(),
    param_grid,
    cv=5,
    scoring='r2',
    return_train_score=True
)
grid_search.fit(X_train_s, y_train)

print(f"Best alpha: {grid_search.best_params_['alpha']}")
print(f"Best CV R2: {grid_search.best_score_:.4f}")
print(f"Test R2: {grid_search.score(X_test_s, y_test):.4f}")

# All results
import pandas as pd
results = pd.DataFrame(grid_search.cv_results_)
print(results[['param_alpha', 'mean_test_score', 'mean_train_score']].to_string())
```

---

## 9. Assumptions of Linear Regression

Linear regression works best when these assumptions hold:

### 1. Linearity
The relationship between features and target is approximately linear.

### 2. Independence
Observations are independent of each other (no autocorrelation).

### 3. Homoscedasticity
The variance of errors is constant across all levels of the independent variables.

### 4. Normality of Residuals
Residuals (errors) are approximately normally distributed.

### 5. No Multicollinearity
Features should not be highly correlated with each other.

When these assumptions are violated, the model may still work but its coefficients and
p-values become unreliable.

---

## 10. Residual Analysis

Residuals are the differences between actual and predicted values. Analyzing them helps
diagnose model problems.

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

X, y = make_regression(n_samples=200, n_features=5, noise=20, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Compute residuals
residuals = y_test - y_pred

# Residual statistics
print(f"Mean residual: {residuals.mean():.4f}")     # Should be ~0
print(f"Std residual:  {residuals.std():.4f}")
print(f"Min residual:  {residuals.min():.4f}")
print(f"Max residual:  {residuals.max():.4f}")

# Check normality (residuals should be approximately normal)
from scipy import stats
_, p_value = stats.shapiro(residuals)
print(f"Shapiro-Wilk p-value: {p_value:.4f}")
# p > 0.05 suggests normality is not rejected
```

### What to Look For in Residuals

**Good residuals:**
- Centered around zero (mean ~ 0)
- Constant spread (homoscedasticity)
- Normally distributed (bell curve)
- No patterns when plotted against predictions

**Bad residuals (signs of problems):**
- Curved pattern: nonlinear relationship (try polynomial features)
- Fan/funnel shape: heteroscedasticity (try log-transforming the target)
- Clusters: possible subgroups in data (consider separate models)
- Outliers: extreme residuals (investigate those data points)

```python
# Programmatic residual checks
def residual_diagnostics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute residual diagnostics."""
    residuals = y_true - y_pred

    return {
        'mean': float(residuals.mean()),
        'std': float(residuals.std()),
        'skewness': float(stats.skew(residuals)),
        'kurtosis': float(stats.kurtosis(residuals)),
        'shapiro_p': float(stats.shapiro(residuals)[1]),
        'n_outliers': int(np.sum(np.abs(residuals) > 3 * residuals.std())),
    }

diag = residual_diagnostics(y_test, y_pred)
for key, value in diag.items():
    print(f"  {key}: {value}")
```

---

## 11. Regression Metrics

### R-squared (R2)

The proportion of variance in the target that's explained by the model.

```
R2 = 1 - sum((y - y_pred)^2) / sum((y - y_mean)^2)
```

- R2 = 1.0: perfect predictions
- R2 = 0.0: model predicts the mean (no better than guessing the average)
- R2 < 0.0: model is worse than predicting the mean (something is very wrong)

```python
from sklearn.metrics import r2_score

r2 = r2_score(y_test, y_pred)
print(f"R2: {r2:.4f}")
```

### Mean Squared Error (MSE)

Average of squared errors. Penalizes large errors more heavily.

```python
from sklearn.metrics import mean_squared_error

mse = mean_squared_error(y_test, y_pred)
print(f"MSE: {mse:.4f}")
```

### Root Mean Squared Error (RMSE)

Square root of MSE -- same units as the target variable, making it more interpretable.

```python
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
# Or in newer sklearn:
rmse = mean_squared_error(y_test, y_pred, squared=False)
print(f"RMSE: {rmse:.4f}")
```

### Mean Absolute Error (MAE)

Average of absolute errors. Less sensitive to outliers than MSE/RMSE.

```python
from sklearn.metrics import mean_absolute_error

mae = mean_absolute_error(y_test, y_pred)
print(f"MAE: {mae:.4f}")
```

### Comparing Metrics

```python
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

def regression_report(y_true, y_pred):
    """Print a comprehensive regression evaluation report."""
    print("Regression Metrics:")
    print(f"  R2:   {r2_score(y_true, y_pred):.4f}")
    print(f"  MSE:  {mean_squared_error(y_true, y_pred):.4f}")
    print(f"  RMSE: {np.sqrt(mean_squared_error(y_true, y_pred)):.4f}")
    print(f"  MAE:  {mean_absolute_error(y_true, y_pred):.4f}")

regression_report(y_test, y_pred)
```

| Metric | Formula | Range | Interpretation |
|--------|---------|-------|----------------|
| R2 | 1 - SS_res/SS_tot | (-inf, 1] | Variance explained |
| MSE | mean((y-y_pred)^2) | [0, inf) | Average squared error |
| RMSE | sqrt(MSE) | [0, inf) | Error in target units |
| MAE | mean(abs(y-y_pred)) | [0, inf) | Average absolute error |

---

## 12. Feature Importance in Linear Models

In linear models, the coefficients directly tell you feature importance -- **after scaling**.

```python
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_diabetes
import numpy as np

# Load a real dataset
diabetes = load_diabetes()
X, y = diabetes.data, diabetes.target

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = Ridge(alpha=1.0)
model.fit(X_scaled, y)

# Feature importance = absolute value of coefficients (after scaling)
importance = np.abs(model.coef_)
feature_names = diabetes.feature_names

# Sort by importance
sorted_idx = np.argsort(importance)[::-1]
for i in sorted_idx:
    print(f"  {feature_names[i]:10s}: {model.coef_[i]:+.4f} (|{importance[i]:.4f}|)")
```

### Important Caveat

Coefficient magnitude only indicates importance when features are on the same scale.
Always standardize (zero mean, unit variance) before interpreting coefficients. Without
scaling, a feature measured in kilometers would have a coefficient 1000x smaller than the
same feature measured in meters -- but they're equally important.

---

## 13. Multicollinearity and VIF

**Multicollinearity** occurs when features are highly correlated with each other. This
makes coefficients unstable -- small changes in data cause large swings in coefficients.

### Variance Inflation Factor (VIF)

VIF measures how much the variance of a coefficient is inflated due to collinearity.

```python
import numpy as np
from sklearn.linear_model import LinearRegression

def compute_vif(X: np.ndarray, feature_names: list[str] = None) -> list[dict]:
    """Compute Variance Inflation Factor for each feature.

    VIF = 1 / (1 - R2) where R2 is from regressing one feature on all others.

    VIF interpretation:
      1.0: no collinearity
      1-5: low collinearity
      5-10: moderate collinearity
      >10: high collinearity (consider dropping or combining features)
    """
    if feature_names is None:
        feature_names = [f"X{i}" for i in range(X.shape[1])]

    results = []
    for i in range(X.shape[1]):
        # Regress feature i on all other features
        X_other = np.delete(X, i, axis=1)
        model = LinearRegression()
        model.fit(X_other, X[:, i])
        r2 = model.score(X_other, X[:, i])

        vif = 1.0 / (1.0 - r2) if r2 < 1.0 else float('inf')
        results.append({'feature': feature_names[i], 'VIF': vif})

    return sorted(results, key=lambda x: x['VIF'], reverse=True)

# Example with the diabetes dataset
from sklearn.datasets import load_diabetes
diabetes = load_diabetes()
vif_results = compute_vif(diabetes.data, list(diabetes.feature_names))
for r in vif_results:
    flag = " *** HIGH" if r['VIF'] > 5 else ""
    print(f"  {r['feature']:10s}: VIF = {r['VIF']:.2f}{flag}")
```

### Dealing with Multicollinearity

1. **Remove one of the correlated features** -- keep the more interpretable one
2. **Combine correlated features** -- e.g., create a ratio or average
3. **Use PCA** -- reduces features to uncorrelated components
4. **Use Ridge regression** -- L2 regularization handles collinearity gracefully
5. **Use Lasso** -- L1 regularization will select one and drop the other

---

## 14. Putting It All Together: Complete Regression Pipeline

```python
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# ---- Load and split ----
diabetes = load_diabetes()
X, y = diabetes.data, diabetes.target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---- Scale ----
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# ---- Compare models ----
models = {
    "Linear Regression": LinearRegression(),
    "Ridge (alpha=1)": Ridge(alpha=1.0),
    "Ridge (alpha=10)": Ridge(alpha=10.0),
    "Lasso (alpha=0.1)": Lasso(alpha=0.1, max_iter=10000),
    "Lasso (alpha=1.0)": Lasso(alpha=1.0, max_iter=10000),
    "ElasticNet (0.5)": ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10000),
}

print(f"{'Model':<25s} {'CV R2':>8s} {'Test R2':>8s} {'RMSE':>8s} {'Non-zero':>10s}")
print("-" * 65)

for name, model in models.items():
    # Cross-validation on training data
    cv_scores = cross_val_score(model, X_train_s, y_train, cv=5, scoring='r2')

    # Fit and evaluate on test data
    model.fit(X_train_s, y_train)
    y_pred = model.predict(X_test_s)
    test_r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Count non-zero coefficients
    n_nonzero = np.sum(model.coef_ != 0)

    print(f"{name:<25s} {cv_scores.mean():>8.4f} {test_r2:>8.4f} {rmse:>8.2f} "
          f"{n_nonzero:>5d}/{X.shape[1]}")
```

---

## Summary: Regression Quick Reference

| Model | Penalty | Feature Selection | When to Use |
|-------|---------|-------------------|-------------|
| LinearRegression | None | No | Baseline, interpretable |
| Ridge | L2 (sum w^2) | No | Many features, multicollinearity |
| Lasso | L1 (sum |w|) | Yes | Feature selection needed |
| ElasticNet | L1 + L2 | Yes | Correlated features + selection |

| Metric | Best For | Sensitive to Outliers |
|--------|----------|----------------------|
| R2 | Overall model quality | Somewhat |
| MSE | Penalizing large errors | Very |
| RMSE | Interpretable error scale | Very |
| MAE | Robust error estimate | Less |

---

## Key Takeaways

1. **Linear regression** finds the best-fit line by minimizing squared errors.
2. **Polynomial features** let linear models capture nonlinear relationships -- but watch for overfitting.
3. **Ridge (L2)** shrinks coefficients, Lasso (L1) drives some to zero, ElasticNet does both.
4. **Always scale features** before applying regularization.
5. **Residual analysis** reveals whether your model's assumptions are met.
6. **VIF** helps detect multicollinearity that makes coefficients unreliable.
7. **RMSE** is the most interpretable metric (same units as the target).
8. **Use cross-validation** to choose the best alpha, not the test set.

---

## Next Steps

Module 03 covers **Classification** -- logistic regression, SVMs, KNN, and Naive Bayes.
Many concepts carry over: regularization, scaling, and cross-validation work the same way,
but we'll learn new metrics (accuracy, precision, recall, F1) that replace R2/RMSE.
