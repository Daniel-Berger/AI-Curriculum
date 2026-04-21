# Module 09: Math for ML

## Introduction

Machine Learning is built on mathematics. You don't need to be a mathematician to use ML,
but understanding the fundamentals makes you a much better practitioner.

**What We'll Cover:**
- Linear Algebra: Vectors, matrices, operations
- Calculus: Derivatives, gradients, optimization
- Probability: Bayes' theorem, conditional probability
- Statistics: Hypothesis testing, p-values, distributions

We'll focus on intuition and practical applications using NumPy.

---

## Part 1: Linear Algebra

Linear algebra is the language of machine learning. Every dataset is a matrix,
every prediction involves matrix operations.

### Vectors

A vector is a 1D array of numbers. In ML, it often represents a single data point
or a feature.

```python
import numpy as np

# Create a vector (1D array)
v = np.array([1, 2, 3, 4, 5])
print(v.shape)  # (5,)

# Vector operations
v1 = np.array([1, 2, 3])
v2 = np.array([4, 5, 6])

# Element-wise addition
result = v1 + v2  # [5, 7, 9]

# Element-wise multiplication
result = v1 * v2  # [4, 10, 18]

# Dot product (critical for ML)
dot_product = np.dot(v1, v2)  # 1*4 + 2*5 + 3*6 = 32
# Alternative: v1 @ v2
```

**Intuition:** Dot product measures similarity between vectors.
- High dot product = vectors point in similar directions
- Zero dot product = vectors are orthogonal (perpendicular)

### Magnitude (Norm)

```python
# L2 norm (Euclidean distance)
v = np.array([3, 4])
magnitude = np.linalg.norm(v)  # sqrt(3^2 + 4^2) = 5

# L1 norm (Manhattan distance)
magnitude_l1 = np.linalg.norm(v, ord=1)  # |3| + |4| = 7

# Normalization: divide by magnitude to get unit vector
unit_vector = v / np.linalg.norm(v)  # [0.6, 0.8]
```

### Matrices

A matrix is a 2D array. In ML, each row is a data point, each column is a feature.

```python
# Create a matrix
A = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])
print(A.shape)  # (3, 3)

# Matrix transposition
A_T = A.T
# or A_T = A.transpose()

# Matrix multiplication
B = np.array([
    [1, 2],
    [3, 4],
    [5, 6]
])

C = A @ B  # Matrix multiplication (3x3) @ (3x2) = (3x2)
# A[i, j] dot product with B[:, k] gives C[i, k]

# Element-wise multiplication (Hadamard product)
D = A * B  # Not possible: shape mismatch, but same shapes would work

# Matrix determinant (only for square matrices)
det = np.linalg.det(A)

# Matrix inverse (if determinant != 0)
A_inv = np.linalg.inv(A)
# Verify: A @ A_inv ≈ Identity
```

**Why matrix multiplication is critical:**
- In a neural network: y = X @ W (predictions)
- Linear regression: β = (X^T X)^(-1) X^T y
- Every transformation in ML involves matrix operations

### Eigenvalues and Eigenvectors

Eigenvalues and eigenvectors reveal the "principal directions" of a matrix.

```python
A = np.array([
    [4, 1],
    [1, 3]
])

eigenvalues, eigenvectors = np.linalg.eig(A)
print(eigenvalues)      # [4.56, 2.44] (or similar)
print(eigenvectors)     # Corresponding eigenvectors as columns

# Intuition: if v is an eigenvector with eigenvalue λ, then:
# A @ v = λ * v
# The matrix only scales v, doesn't change its direction
```

**Application:** Principal Component Analysis (PCA) uses eigenvectors to find
directions of maximum variance in data.

---

## Part 2: Calculus Essentials

Calculus is how we optimize machine learning models. We use derivatives to find
the best parameters.

### Derivatives

A derivative measures how fast a function changes. In ML, we use derivatives to
understand how loss changes with parameters.

```python
# Numerical differentiation (approximate)
def f(x):
    return x**2

def numerical_derivative(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)

x = 3
df_dx = numerical_derivative(f, x)
print(df_dx)  # ≈ 6 (exact: 2*x = 2*3 = 6)

# Analytical derivative of f(x) = x^2 is f'(x) = 2x
# At x=3, f'(3) = 6
```

**Rules of derivatives:**

```python
# Power rule: d/dx(x^n) = n*x^(n-1)
# Product rule: d/dx(u*v) = u*v' + u'*v
# Chain rule: d/dx(f(g(x))) = f'(g(x)) * g'(x)

# Example: d/dx((2x^2 + 3)^3)
# Let u = 2x^2 + 3, then we want d/dx(u^3)
# By chain rule: 3*u^2 * du/dx = 3*(2x^2+3)^2 * 4x

def f_composite(x):
    return (2*x**2 + 3)**3

def df_composite(x):
    u = 2*x**2 + 3
    return 3 * u**2 * (4*x)

# Verify
x = 2
numerical = numerical_derivative(f_composite, x)
analytical = df_composite(x)
print(f"Numerical: {numerical}, Analytical: {analytical}")
```

### Partial Derivatives and Gradients

In ML, we have many parameters (dimensions). The gradient is a vector of partial
derivatives, one for each parameter.

```python
# Function of two variables
def f(x, y):
    return x**2 + 2*x*y + y**2

# Partial derivatives
def df_dx(x, y):
    """∂f/∂x = 2x + 2y"""
    return 2*x + 2*y

def df_dy(x, y):
    """∂f/∂y = 2x + 2y"""
    return 2*x + 2*y

# Gradient at point (x=1, y=2)
x, y = 1, 2
gradient = np.array([df_dx(x, y), df_dy(x, y)])
print(gradient)  # [6, 6]

# The gradient points in the direction of steepest ascent
# Negative gradient points toward minimum (gradient descent)
```

### Optimization with Gradient Descent

The core of training neural networks is gradient descent: repeatedly update
parameters by moving in the direction opposite to the gradient.

```python
# Example: minimize f(x) = x^2
def f(x):
    return x**2

def df_dx(x):
    return 2*x

# Gradient descent
x = 5.0  # Starting point
learning_rate = 0.1

for i in range(10):
    gradient = df_dx(x)
    x = x - learning_rate * gradient  # Update: x = x - lr * ∇f
    print(f"Iteration {i}: x={x:.4f}, f(x)={f(x):.4f}")

# x converges to 0 (the minimum of x^2)
```

**Key insight:** Learning rate controls step size.
- Too small: slow convergence
- Too large: might overshoot and diverge
- Adaptive learning rates (Adam, RMSprop) adjust this automatically

---

## Part 3: Probability

Probability is the foundation of statistical machine learning.

### Basic Probability

```python
# Probability: number of favorable outcomes / total outcomes
# P(rolling a 6 on a die) = 1/6 ≈ 0.167

# Joint probability: P(A and B)
# Example: P(rain and cold) = 0.1 (it's rare both happen)

# Conditional probability: P(A | B) = P(A and B) / P(B)
# Example: P(slippery | rain) = P(slippery and rain) / P(rain)
# If rain makes slippery: this is high
# If rain doesn't affect slipperiness: this equals P(slippery)

# Law of total probability
# P(A) = P(A|B) * P(B) + P(A|¬B) * P(¬B)
```

### Bayes' Theorem

The most important theorem in machine learning and statistics.

```python
# Bayes' Theorem: P(A|B) = P(B|A) * P(A) / P(B)

# Example: Medical test for disease
# P(disease) = 0.01 (1% of population has disease)
# P(positive | disease) = 0.99 (test correctly identifies 99% of sick)
# P(positive | no disease) = 0.05 (false positive rate is 5%)

# Question: if you test positive, what's probability you have the disease?

p_disease = 0.01
p_positive_given_disease = 0.99
p_positive_given_no_disease = 0.05

# P(positive) by law of total probability
p_positive = (p_positive_given_disease * p_disease +
              p_positive_given_no_disease * (1 - p_disease))

# P(disease | positive) by Bayes
p_disease_given_positive = (
    (p_positive_given_disease * p_disease) / p_positive
)

print(f"P(disease | positive) = {p_disease_given_positive:.3f}")
# Despite positive test, only ~16.6% chance you have disease!
# This is the base rate fallacy: ignore prior probability at your peril
```

**ML Applications:**
- Naive Bayes classifier: P(class | features) = P(features | class) * P(class) / P(features)
- Posterior = likelihood * prior / evidence

---

## Part 4: Statistics

Statistics helps us understand data and make decisions despite uncertainty.

### Distributions

```python
# Normal distribution (bell curve)
import numpy as np
from scipy.stats import norm

# P(X) for normal distribution with mean=0, std=1
x = 0
probability_density = norm.pdf(x, loc=0, scale=1)

# Cumulative probability P(X <= x)
cumulative = norm.cdf(x, loc=0, scale=1)  # 0.5 (half the area)

# Generate random samples from normal distribution
samples = np.random.normal(loc=0, scale=1, size=1000)

# Binomial distribution (coin flips)
from scipy.stats import binom
# P(k successes in n trials) with probability p
p_k_heads = binom.pmf(k=3, n=5, p=0.5)  # P(3 heads in 5 flips)
```

### Hypothesis Testing

We use hypothesis testing to answer: "Is this result due to chance or real?"

```python
# Example: Does a coin flip p = 0.5 (fair) or p > 0.5 (biased)?
# We flip 100 times and get 60 heads

# Null hypothesis H0: p = 0.5 (fair coin)
# Alternative hypothesis H1: p > 0.5 (biased)

from scipy.stats import binom_test

# Test: if coin is fair, how likely to see >= 60 heads?
p_value = binom_test(x=60, n=100, p=0.5, alternative='greater')
print(f"p-value: {p_value:.6f}")

# If p-value < 0.05: reject null hypothesis (coin seems biased)
# If p-value >= 0.05: fail to reject null hypothesis (could be fair)
```

### P-values and Significance

```python
# P-value: probability of observing data this extreme if null hypothesis is true

# Significance level α (usually 0.05)
# If p-value < α: result is "statistically significant" (reject H0)
# If p-value >= α: result is not significant (don't reject H0)

# Important: p-value is NOT:
# - probability that null hypothesis is true
# - probability that alternative is true
# - "strength" of effect

# It's: probability of this data (or more extreme) under null hypothesis
```

### Confidence Intervals

```python
# 95% confidence interval for a mean
# "If we repeated experiment 100 times, 95 intervals would contain true mean"

data = np.array([2.1, 2.5, 2.8, 3.0, 3.2])
mean = data.mean()
std_error = data.std() / np.sqrt(len(data))

# For normal distribution, 95% CI is ±1.96 standard errors
ci_lower = mean - 1.96 * std_error
ci_upper = mean + 1.96 * std_error

print(f"95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
```

---

## Part 5: Practical Examples

### Linear Regression from Scratch

```python
# y = mx + b (find best m and b)
# Using gradient descent on mean squared error

def mse_gradient(X, y, m, b):
    """Gradient of MSE with respect to m and b"""
    n = len(X)
    y_pred = m * X + b
    residuals = y_pred - y

    dm = (2/n) * np.dot(residuals, X)    # ∂MSE/∂m
    db = (2/n) * np.sum(residuals)       # ∂MSE/∂b

    return dm, db

# Data
X = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 6, 8, 10])  # y = 2x (plus noise)

# Initialize parameters
m, b = 0.0, 0.0
learning_rate = 0.01

# Training loop
for epoch in range(100):
    dm, db = mse_gradient(X, y, m, b)
    m = m - learning_rate * dm
    b = b - learning_rate * db

print(f"Learned: y = {m:.4f}*x + {b:.4f}")
# Should get close to: y = 2*x + 0
```

### Logistic Regression (Classification)

```python
# Probability of class 1: P(y=1|x) = 1 / (1 + e^(-z))
# where z = mx + b

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# Cross-entropy loss: -y*log(ŷ) - (1-y)*log(1-ŷ)
# Gradient descent updates parameters similarly to linear regression

# In practice: use sklearn, TensorFlow, PyTorch
# They handle these calculations automatically and efficiently
```

---

## Key Takeaways

1. **Vectors & Matrices**: Think in terms of transformations, not individual numbers
2. **Derivatives**: Optimization finds parameters by following negative gradients
3. **Probability**: Bayes' theorem connects observations to beliefs
4. **Statistics**: Hypothesis testing and confidence intervals quantify uncertainty
5. **Intuition over calculation**: Understand the concepts, use libraries for computation

---

## Further Resources

- Essence of Linear Algebra (3Blue1Brown): Visualize linear algebra concepts
- Essence of Calculus (3Blue1Brown): Beautiful visual explanation of calculus
- Intuitive Probability (various sources): Focus on intuition, not formulas
- StatQuest (Josh Starmer): Clear explanations of statistics and ML math
