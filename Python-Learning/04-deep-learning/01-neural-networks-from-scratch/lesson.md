# Module 01: Neural Networks from Scratch

## Overview

In this module, you will build a complete neural network using **only NumPy** — no PyTorch,
no TensorFlow, no frameworks. This is analogous to how understanding UIKit internals makes
you a better SwiftUI developer: understanding what happens beneath the abstractions makes
you far more effective when debugging, tuning, and designing neural networks with frameworks.

By the end of this module you will have implemented forward propagation, backpropagation,
and a full training loop from first principles.

---

## 1. Biological Inspiration (Brief)

A biological neuron receives electrical signals through **dendrites**, processes them in
the **cell body**, and transmits an output through the **axon**. Artificial neurons are
a loose mathematical analogy:

```
Biological              Artificial
─────────────           ─────────────
Dendrites         →     Input features (x₁, x₂, ..., xₙ)
Synaptic weights  →     Learnable weights (w₁, w₂, ..., wₙ)
Cell body         →     Weighted sum + bias: z = Σ(wᵢxᵢ) + b
Axon firing       →     Activation function: a = f(z)
```

That is the extent of the biological analogy that is useful. Modern neural networks are
engineering constructs, not neuroscience simulations.

---

## 2. The Perceptron

The perceptron is the simplest neural network: a single neuron that performs binary
classification.

```python
import numpy as np

def perceptron(x, w, b):
    """Single perceptron: step activation."""
    z = np.dot(w, x) + b
    return 1 if z >= 0 else 0
```

### Perceptron Learning Rule

```python
def train_perceptron(X, y, learning_rate=0.1, epochs=100):
    """Train a perceptron on dataset X with labels y."""
    n_features = X.shape[1]
    w = np.zeros(n_features)
    b = 0.0

    for epoch in range(epochs):
        for i in range(len(X)):
            prediction = 1 if np.dot(w, X[i]) + b >= 0 else 0
            error = y[i] - prediction
            w += learning_rate * error * X[i]
            b += learning_rate * error

    return w, b

# AND gate
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 0, 0, 1])
w, b = train_perceptron(X, y)
print(f"Weights: {w}, Bias: {b}")
```

**Limitation**: A single perceptron can only learn linearly separable functions.
It cannot learn XOR. This is why we need **multi-layer** networks.

---

## 3. Multi-Layer Networks (MLPs)

A multi-layer perceptron (MLP) stacks layers of neurons:

```
Input Layer → Hidden Layer(s) → Output Layer

Architecture notation: [input_dim, hidden1, hidden2, ..., output_dim]
Example: [784, 128, 64, 10]  (for MNIST digit classification)
```

Each layer performs:
1. **Linear transformation**: Z = XW + b
2. **Non-linear activation**: A = f(Z)

The key insight: stacking linear transformations without non-linear activations would
just produce another linear transformation. Activation functions introduce the non-linearity
that lets networks learn complex patterns.

```
Think of it like Swift protocol composition:
- Each layer is a transform
- Without non-linearity, composing linear transforms = one linear transform
- Non-linearity is what gives depth its power
```

---

## 4. Forward Propagation

Forward propagation is a series of matrix multiplications and element-wise activations.

### Matrix Dimensions

For a network with layers [n₀, n₁, n₂, n₃]:

```
Layer 1: W₁ is (n₀, n₁), b₁ is (1, n₁)
Layer 2: W₂ is (n₁, n₂), b₂ is (1, n₂)
Layer 3: W₃ is (n₂, n₃), b₃ is (1, n₃)

Input X is (m, n₀) where m = batch size
```

### Step-by-Step Forward Pass

```python
def forward_pass(X, weights, biases, activations):
    """
    Forward propagation through a network.

    Parameters:
        X: input data, shape (m, n_features)
        weights: list of weight matrices
        biases: list of bias vectors
        activations: list of activation functions

    Returns:
        output: final layer output
        cache: intermediate values needed for backprop
    """
    cache = {'A0': X}
    A = X

    for l in range(len(weights)):
        Z = A @ weights[l] + biases[l]       # Linear: Z = AW + b
        A = activations[l](Z)                  # Activation: A = f(Z)
        cache[f'Z{l+1}'] = Z
        cache[f'A{l+1}'] = A

    return A, cache
```

### Concrete Example

```python
# Network: 2 inputs → 3 hidden → 1 output
np.random.seed(42)

X = np.array([[1.0, 2.0],
              [3.0, 4.0]])  # (2, 2) — 2 samples, 2 features

W1 = np.random.randn(2, 3) * 0.01  # (2, 3)
b1 = np.zeros((1, 3))               # (1, 3)

W2 = np.random.randn(3, 1) * 0.01  # (3, 1)
b2 = np.zeros((1, 1))               # (1, 1)

# Forward pass
Z1 = X @ W1 + b1           # (2, 3)
A1 = np.maximum(0, Z1)     # ReLU activation, (2, 3)

Z2 = A1 @ W2 + b2          # (2, 1)
A2 = 1 / (1 + np.exp(-Z2)) # Sigmoid activation, (2, 1)

print(f"Z1 shape: {Z1.shape}")  # (2, 3)
print(f"A1 shape: {A1.shape}")  # (2, 3)
print(f"Z2 shape: {Z2.shape}")  # (2, 1)
print(f"Output: {A2}")          # (2, 1) — predictions
```

---

## 5. Activation Functions

Activation functions introduce non-linearity. Here is each one with its formula, derivative,
and when to use it.

### 5.1 Sigmoid

```
Formula:    σ(z) = 1 / (1 + e^(-z))
Derivative: σ'(z) = σ(z) * (1 - σ(z))
Range:      (0, 1)
Use:        Binary classification output layer
Problem:    Vanishing gradients for large |z|, outputs not zero-centered
```

```python
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def sigmoid_derivative(z):
    s = sigmoid(z)
    return s * (1 - s)

# Visualization data
z = np.linspace(-6, 6, 100)
print(f"sigmoid(0) = {sigmoid(0)}")       # 0.5
print(f"sigmoid(5) = {sigmoid(5):.4f}")   # 0.9933
print(f"sigmoid(-5) = {sigmoid(-5):.4f}") # 0.0067
```

### 5.2 Tanh

```
Formula:    tanh(z) = (e^z - e^(-z)) / (e^z + e^(-z))
Derivative: tanh'(z) = 1 - tanh²(z)
Range:      (-1, 1)
Use:        Hidden layers (zero-centered, stronger gradients than sigmoid)
Problem:    Still suffers from vanishing gradients at extremes
```

```python
def tanh(z):
    return np.tanh(z)

def tanh_derivative(z):
    return 1 - np.tanh(z) ** 2
```

### 5.3 ReLU (Rectified Linear Unit)

```
Formula:    ReLU(z) = max(0, z)
Derivative: ReLU'(z) = 1 if z > 0 else 0
Range:      [0, ∞)
Use:        Default for hidden layers in most networks
Advantage:  Fast, no vanishing gradient for positive values
Problem:    "Dying ReLU" — neurons can get stuck at 0
```

```python
def relu(z):
    return np.maximum(0, z)

def relu_derivative(z):
    return (z > 0).astype(float)
```

### 5.4 Leaky ReLU

```
Formula:    LeakyReLU(z) = z if z > 0 else αz  (α = 0.01 typically)
Derivative: LeakyReLU'(z) = 1 if z > 0 else α
Range:      (-∞, ∞)
Use:        When dying ReLU is a problem
```

```python
def leaky_relu(z, alpha=0.01):
    return np.where(z > 0, z, alpha * z)

def leaky_relu_derivative(z, alpha=0.01):
    return np.where(z > 0, 1.0, alpha)
```

### 5.5 Softmax

```
Formula:    softmax(zᵢ) = e^(zᵢ) / Σⱼ e^(zⱼ)
Range:      (0, 1), outputs sum to 1
Use:        Multi-class classification output layer
Note:       Applied across a vector, not element-wise like others
```

```python
def softmax(z):
    # Subtract max for numerical stability (prevents overflow)
    exp_z = np.exp(z - np.max(z, axis=-1, keepdims=True))
    return exp_z / np.sum(exp_z, axis=-1, keepdims=True)

# Example
logits = np.array([[2.0, 1.0, 0.1]])
probs = softmax(logits)
print(f"Softmax output: {probs}")       # [[0.659, 0.242, 0.099]]
print(f"Sum: {np.sum(probs)}")          # 1.0
```

### Activation Function Cheat Sheet

```
Layer Type          Recommended Activation
─────────────       ─────────────────────
Hidden layers       ReLU (default), Leaky ReLU
Binary output       Sigmoid
Multi-class output  Softmax
Regression output   None (linear/identity)
```

---

## 6. Loss Functions

Loss functions measure how wrong the model's predictions are. They provide the signal
that drives learning.

### 6.1 Mean Squared Error (MSE)

```
Formula:  L = (1/m) Σᵢ (yᵢ - ŷᵢ)²
Use:      Regression problems
Gradient: dL/dŷ = (2/m)(ŷ - y)
```

```python
def mse_loss(y_true, y_pred):
    m = y_true.shape[0]
    return np.mean((y_true - y_pred) ** 2)

def mse_loss_gradient(y_true, y_pred):
    m = y_true.shape[0]
    return (2 / m) * (y_pred - y_true)

# Example
y_true = np.array([[3.0], [5.0], [7.0]])
y_pred = np.array([[2.8], [5.1], [6.5]])
print(f"MSE: {mse_loss(y_true, y_pred):.4f}")  # small
```

### 6.2 Binary Cross-Entropy

```
Formula:  L = -(1/m) Σᵢ [yᵢ log(ŷᵢ) + (1-yᵢ) log(1-ŷᵢ)]
Use:      Binary classification (with sigmoid output)
Gradient: dL/dŷ = -(y/ŷ) + (1-y)/(1-ŷ)

Intuition: Penalizes confident wrong predictions heavily.
           If y=1 and ŷ=0.01, loss = -log(0.01) = 4.6 (huge!)
           If y=1 and ŷ=0.99, loss = -log(0.99) = 0.01 (tiny)
```

```python
def binary_cross_entropy(y_true, y_pred):
    epsilon = 1e-15  # prevent log(0)
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(
        y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred)
    )

def binary_cross_entropy_gradient(y_true, y_pred):
    epsilon = 1e-15
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return (-(y_true / y_pred) + (1 - y_true) / (1 - y_pred)) / y_true.shape[0]
```

### 6.3 Categorical Cross-Entropy

```
Formula:  L = -(1/m) Σᵢ Σⱼ yᵢⱼ log(ŷᵢⱼ)
Use:      Multi-class classification (with softmax output)
Combined gradient (softmax + cross-entropy): dL/dz = ŷ - y
  — This simplification is why softmax + cross-entropy are always paired
```

```python
def categorical_cross_entropy(y_true_onehot, y_pred):
    epsilon = 1e-15
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(np.sum(y_true_onehot * np.log(y_pred), axis=1))
```

---

## 7. Backpropagation

Backpropagation is the algorithm that computes gradients of the loss with respect to
every weight in the network. It uses the **chain rule** of calculus to propagate error
signals backward through the network.

### 7.1 The Chain Rule

```
If y = f(g(x)), then dy/dx = f'(g(x)) * g'(x)

In a network:
  Z = XW + b       (linear)
  A = f(Z)         (activation)
  L = loss(A, y)   (loss)

We want dL/dW. By the chain rule:
  dL/dW = dL/dA * dA/dZ * dZ/dW
```

### 7.2 Computational Graph

Think of the network as a directed acyclic graph (like a SwiftUI view hierarchy):

```
X ──→ [Z1 = XW1+b1] ──→ [A1 = relu(Z1)] ──→ [Z2 = A1W2+b2] ──→ [A2 = sigmoid(Z2)] ──→ L
          ↑                                         ↑
          W1, b1                                    W2, b2

Forward:  left → right (compute activations)
Backward: right → left (compute gradients)
```

### 7.3 Gradient Flow — Worked Example

For a 2-layer network (one hidden layer):

**Forward pass:**
```
Z1 = X @ W1 + b1
A1 = relu(Z1)
Z2 = A1 @ W2 + b2
A2 = sigmoid(Z2)
L = binary_cross_entropy(y, A2)
```

**Backward pass (deriving each gradient):**

```python
# Step 1: Gradient of loss w.r.t. output
# dL/dA2 — depends on loss function
dA2 = binary_cross_entropy_gradient(y, A2)  # shape: (m, 1)

# Step 2: Gradient through sigmoid
# dL/dZ2 = dL/dA2 * dA2/dZ2 = dL/dA2 * sigmoid'(Z2)
dZ2 = dA2 * sigmoid_derivative(Z2)          # shape: (m, 1)

# Step 3: Gradients for W2 and b2
# dL/dW2 = A1^T @ dZ2  (from Z2 = A1 @ W2 + b2, so dZ2/dW2 = A1^T)
dW2 = A1.T @ dZ2 / m                        # shape: (n1, 1)
db2 = np.sum(dZ2, axis=0, keepdims=True) / m # shape: (1, 1)

# Step 4: Propagate gradient to previous layer
# dL/dA1 = dZ2 @ W2^T  (from Z2 = A1 @ W2 + b2, so dZ2/dA1 = W2^T)
dA1 = dZ2 @ W2.T                            # shape: (m, n1)

# Step 5: Gradient through ReLU
# dL/dZ1 = dL/dA1 * dA1/dZ1 = dL/dA1 * relu'(Z1)
dZ1 = dA1 * relu_derivative(Z1)             # shape: (m, n1)

# Step 6: Gradients for W1 and b1
dW1 = X.T @ dZ1 / m                         # shape: (n0, n1)
db1 = np.sum(dZ1, axis=0, keepdims=True) / m # shape: (1, n1)
```

### 7.4 The General Pattern

For any layer l:
```
dZ[l] = dA[l] * activation_derivative(Z[l])
dW[l] = A[l-1].T @ dZ[l] / m
db[l] = sum(dZ[l], axis=0) / m
dA[l-1] = dZ[l] @ W[l].T
```

This pattern repeats from the last layer to the first — that is backpropagation.

```python
def backward_pass(y, cache, weights, activation_derivatives):
    """
    Backward propagation through the network.

    Returns:
        grads: dict with dW and db for each layer
    """
    m = y.shape[0]
    L = len(weights)  # number of layers
    grads = {}

    # Start with output gradient
    dA = binary_cross_entropy_gradient(y, cache[f'A{L}'])

    for l in range(L, 0, -1):
        dZ = dA * activation_derivatives[l-1](cache[f'Z{l}'])
        grads[f'dW{l}'] = cache[f'A{l-1}'].T @ dZ / m
        grads[f'db{l}'] = np.sum(dZ, axis=0, keepdims=True) / m
        if l > 1:
            dA = dZ @ weights[l-1].T

    return grads
```

---

## 8. Gradient Descent Variants

### 8.1 Batch Gradient Descent

Uses the **entire dataset** for each update:

```python
def batch_gradient_descent(X, y, weights, biases, learning_rate, epochs):
    for epoch in range(epochs):
        # Forward pass on ALL data
        output, cache = forward_pass(X, weights, biases, activations)
        loss = compute_loss(y, output)

        # Backward pass
        grads = backward_pass(y, cache, weights, activation_derivatives)

        # Update ALL weights
        for l in range(len(weights)):
            weights[l] -= learning_rate * grads[f'dW{l+1}']
            biases[l] -= learning_rate * grads[f'db{l+1}']
```

**Pros**: Stable convergence, exact gradient.
**Cons**: Slow for large datasets, requires entire dataset in memory.

### 8.2 Stochastic Gradient Descent (SGD)

Uses **one sample** per update:

```python
def sgd(X, y, weights, biases, learning_rate, epochs):
    for epoch in range(epochs):
        indices = np.random.permutation(len(X))
        for i in indices:
            xi = X[i:i+1]  # keep 2D shape: (1, n_features)
            yi = y[i:i+1]
            output, cache = forward_pass(xi, weights, biases, activations)
            grads = backward_pass(yi, cache, weights, activation_derivatives)

            for l in range(len(weights)):
                weights[l] -= learning_rate * grads[f'dW{l+1}']
                biases[l] -= learning_rate * grads[f'db{l+1}']
```

**Pros**: Fast updates, can escape local minima, works with large datasets.
**Cons**: Noisy updates, may not converge smoothly.

### 8.3 Mini-Batch Gradient Descent (Most Common)

Uses **small batches** (typically 32, 64, 128):

```python
def mini_batch_gd(X, y, weights, biases, learning_rate, epochs, batch_size=32):
    m = X.shape[0]

    for epoch in range(epochs):
        indices = np.random.permutation(m)
        X_shuffled = X[indices]
        y_shuffled = y[indices]

        for start in range(0, m, batch_size):
            end = min(start + batch_size, m)
            X_batch = X_shuffled[start:end]
            y_batch = y_shuffled[start:end]

            output, cache = forward_pass(X_batch, weights, biases, activations)
            grads = backward_pass(y_batch, cache, weights, activation_derivatives)

            for l in range(len(weights)):
                weights[l] -= learning_rate * grads[f'dW{l+1}']
                biases[l] -= learning_rate * grads[f'db{l+1}']
```

**Best of both worlds**: Vectorized computation + frequent updates + some noise for
regularization.

---

## 9. Weight Initialization

Bad initialization can kill training. Two key strategies:

### 9.1 Xavier/Glorot Initialization

For **sigmoid** and **tanh** activations:

```
W ~ N(0, sqrt(2 / (n_in + n_out)))

Intuition: Keep variance of activations roughly equal across layers.
```

```python
def xavier_init(n_in, n_out):
    return np.random.randn(n_in, n_out) * np.sqrt(2.0 / (n_in + n_out))
```

### 9.2 He Initialization

For **ReLU** activations (recommended default):

```
W ~ N(0, sqrt(2 / n_in))

Intuition: ReLU zeros out half the values, so we need larger initial
weights to compensate.
```

```python
def he_init(n_in, n_out):
    return np.random.randn(n_in, n_out) * np.sqrt(2.0 / n_in)
```

### Why Initialization Matters

```python
# BAD: zeros — all neurons learn the same thing (symmetry problem)
W = np.zeros((784, 128))

# BAD: too large — activations saturate, gradients vanish
W = np.random.randn(784, 128) * 10

# BAD: too small — activations shrink to zero layer by layer
W = np.random.randn(784, 128) * 0.0001

# GOOD: He initialization for ReLU
W = np.random.randn(784, 128) * np.sqrt(2.0 / 784)
```

---

## 10. Building a Complete Neural Network from Scratch

Here is a full implementation of a neural network class using only NumPy. This implements
everything we have covered: forward propagation, backpropagation, and mini-batch training.

```python
import numpy as np


class NeuralNetwork:
    """
    A fully-connected neural network built from scratch with NumPy.

    Think of this like building UIKit components from scratch
    before using SwiftUI — you understand what the framework does for you.
    """

    def __init__(self, layer_dims, activation='relu', output_activation='sigmoid'):
        """
        Initialize the network.

        Args:
            layer_dims: list of layer sizes, e.g. [784, 128, 64, 10]
            activation: hidden layer activation ('relu', 'tanh', 'sigmoid')
            output_activation: output layer activation ('sigmoid', 'softmax')
        """
        self.layer_dims = layer_dims
        self.num_layers = len(layer_dims) - 1
        self.activation_name = activation
        self.output_activation_name = output_activation

        # Initialize weights and biases
        self.weights = []
        self.biases = []
        for l in range(self.num_layers):
            n_in = layer_dims[l]
            n_out = layer_dims[l + 1]

            # He initialization for ReLU, Xavier for others
            if activation == 'relu':
                W = np.random.randn(n_in, n_out) * np.sqrt(2.0 / n_in)
            else:
                W = np.random.randn(n_in, n_out) * np.sqrt(2.0 / (n_in + n_out))

            b = np.zeros((1, n_out))
            self.weights.append(W)
            self.biases.append(b)

        # Track training history
        self.loss_history = []

    # ── Activation Functions ──────────────────────────────────────────

    def _sigmoid(self, z):
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))

    def _sigmoid_deriv(self, z):
        s = self._sigmoid(z)
        return s * (1 - s)

    def _tanh(self, z):
        return np.tanh(z)

    def _tanh_deriv(self, z):
        return 1 - np.tanh(z) ** 2

    def _relu(self, z):
        return np.maximum(0, z)

    def _relu_deriv(self, z):
        return (z > 0).astype(float)

    def _softmax(self, z):
        exp_z = np.exp(z - np.max(z, axis=-1, keepdims=True))
        return exp_z / np.sum(exp_z, axis=-1, keepdims=True)

    def _get_activation(self, name):
        return {'sigmoid': self._sigmoid, 'tanh': self._tanh,
                'relu': self._relu, 'softmax': self._softmax}[name]

    def _get_activation_deriv(self, name):
        return {'sigmoid': self._sigmoid_deriv, 'tanh': self._tanh_deriv,
                'relu': self._relu_deriv}[name]

    # ── Forward Pass ──────────────────────────────────────────────────

    def forward(self, X):
        """
        Forward propagation through all layers.

        Returns:
            output: predictions
            cache: intermediate values for backprop
        """
        cache = {'A0': X}
        A = X
        hidden_act = self._get_activation(self.activation_name)
        output_act = self._get_activation(self.output_activation_name)

        for l in range(self.num_layers):
            Z = A @ self.weights[l] + self.biases[l]
            cache[f'Z{l+1}'] = Z

            if l == self.num_layers - 1:
                A = output_act(Z)
            else:
                A = hidden_act(Z)

            cache[f'A{l+1}'] = A

        return A, cache

    # ── Loss Functions ────────────────────────────────────────────────

    def _binary_cross_entropy(self, y_true, y_pred):
        eps = 1e-15
        y_pred = np.clip(y_pred, eps, 1 - eps)
        return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))

    def _categorical_cross_entropy(self, y_true, y_pred):
        eps = 1e-15
        y_pred = np.clip(y_pred, eps, 1 - eps)
        return -np.mean(np.sum(y_true * np.log(y_pred), axis=1))

    def _mse(self, y_true, y_pred):
        return np.mean((y_true - y_pred) ** 2)

    # ── Backward Pass ─────────────────────────────────────────────────

    def backward(self, y, cache):
        """
        Backward propagation — computes gradients for all weights and biases.
        """
        m = y.shape[0]
        grads = {}
        L = self.num_layers

        # Output layer gradient
        A_out = cache[f'A{L}']

        if self.output_activation_name == 'softmax':
            # Softmax + cross-entropy combined gradient
            dZ = A_out - y
        elif self.output_activation_name == 'sigmoid':
            # Sigmoid + binary cross-entropy combined gradient
            eps = 1e-15
            A_out_clipped = np.clip(A_out, eps, 1 - eps)
            dZ = A_out_clipped - y
        else:
            # MSE gradient for linear output
            dZ = 2 * (A_out - y) / y.shape[1]

        # Gradient for last layer
        grads[f'dW{L}'] = cache[f'A{L-1}'].T @ dZ / m
        grads[f'db{L}'] = np.sum(dZ, axis=0, keepdims=True) / m

        # Propagate backward through hidden layers
        hidden_deriv = self._get_activation_deriv(self.activation_name)

        for l in range(L - 1, 0, -1):
            dA = dZ @ self.weights[l].T
            dZ = dA * hidden_deriv(cache[f'Z{l}'])
            grads[f'dW{l}'] = cache[f'A{l-1}'].T @ dZ / m
            grads[f'db{l}'] = np.sum(dZ, axis=0, keepdims=True) / m

        return grads

    # ── Training ──────────────────────────────────────────────────────

    def fit(self, X, y, epochs=100, learning_rate=0.01, batch_size=32, verbose=True):
        """
        Train the network with mini-batch gradient descent.
        """
        m = X.shape[0]
        self.loss_history = []

        for epoch in range(epochs):
            # Shuffle data
            indices = np.random.permutation(m)
            X_shuffled = X[indices]
            y_shuffled = y[indices]

            epoch_loss = 0
            num_batches = 0

            for start in range(0, m, batch_size):
                end = min(start + batch_size, m)
                X_batch = X_shuffled[start:end]
                y_batch = y_shuffled[start:end]

                # Forward
                output, cache = self.forward(X_batch)

                # Compute loss
                if self.output_activation_name == 'softmax':
                    batch_loss = self._categorical_cross_entropy(y_batch, output)
                elif self.output_activation_name == 'sigmoid':
                    batch_loss = self._binary_cross_entropy(y_batch, output)
                else:
                    batch_loss = self._mse(y_batch, output)

                epoch_loss += batch_loss
                num_batches += 1

                # Backward
                grads = self.backward(y_batch, cache)

                # Update weights
                for l in range(self.num_layers):
                    self.weights[l] -= learning_rate * grads[f'dW{l+1}']
                    self.biases[l] -= learning_rate * grads[f'db{l+1}']

            avg_loss = epoch_loss / num_batches
            self.loss_history.append(avg_loss)

            if verbose and (epoch + 1) % max(1, epochs // 10) == 0:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")

    # ── Prediction ────────────────────────────────────────────────────

    def predict(self, X):
        """Forward pass without caching (inference only)."""
        output, _ = self.forward(X)
        return output

    def predict_classes(self, X):
        """Return predicted class labels."""
        probs = self.predict(X)
        if self.output_activation_name == 'softmax':
            return np.argmax(probs, axis=1)
        else:
            return (probs >= 0.5).astype(int).flatten()

    def accuracy(self, X, y):
        """Compute classification accuracy."""
        predictions = self.predict_classes(X)
        if self.output_activation_name == 'softmax':
            true_labels = np.argmax(y, axis=1)
        else:
            true_labels = y.flatten()
        return np.mean(predictions == true_labels)
```

### Using the Network

```python
# ── Binary Classification: XOR ────────────────────────────────────

X_xor = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y_xor = np.array([[0], [1], [1], [0]])

nn_xor = NeuralNetwork([2, 8, 1], activation='relu', output_activation='sigmoid')
nn_xor.fit(X_xor, y_xor, epochs=1000, learning_rate=0.1, batch_size=4, verbose=True)

predictions = nn_xor.predict(X_xor)
print("\nXOR Predictions:")
for i in range(len(X_xor)):
    print(f"  {X_xor[i]} → {predictions[i][0]:.4f} (expected {y_xor[i][0]})")

print(f"Accuracy: {nn_xor.accuracy(X_xor, y_xor) * 100:.1f}%")


# ── Multi-Class Classification: Simple Spiral ─────────────────────

def create_spiral_data(n_points=100, n_classes=3):
    """Generate spiral dataset for multi-class classification."""
    X = np.zeros((n_points * n_classes, 2))
    y = np.zeros(n_points * n_classes, dtype=int)

    for c in range(n_classes):
        idx = range(n_points * c, n_points * (c + 1))
        r = np.linspace(0.0, 1, n_points)
        t = np.linspace(c * 4, (c + 1) * 4, n_points) + np.random.randn(n_points) * 0.2
        X[idx] = np.c_[r * np.sin(t), r * np.cos(t)]
        y[idx] = c

    return X, y

X_spiral, y_spiral = create_spiral_data(100, 3)

# One-hot encode labels
y_onehot = np.zeros((len(y_spiral), 3))
y_onehot[np.arange(len(y_spiral)), y_spiral] = 1

nn_spiral = NeuralNetwork([2, 64, 32, 3], activation='relu', output_activation='softmax')
nn_spiral.fit(X_spiral, y_onehot, epochs=500, learning_rate=0.1, batch_size=32)

print(f"\nSpiral Accuracy: {nn_spiral.accuracy(X_spiral, y_onehot) * 100:.1f}%")
```

---

## 11. Connecting to iOS Development

If you have used **Create ML** or **Core ML** on iOS, you have been using neural networks
already — just through high-level APIs. Here is the mapping:

```
NumPy NN (this module)          iOS / CoreML
────────────────────            ─────────────
NeuralNetwork class       →    MLModel / Create ML model
forward()                 →    model.prediction(from:)
fit()                     →    MLImageClassifier.train()
weights, biases           →    .mlmodel file (compiled weights)
activation functions      →    Built into CoreML layers
loss + backprop           →    Handled by Create ML training
predict_classes()         →    VNClassificationObservation
```

Understanding what happens inside the `.mlmodel` file — the weight matrices, the
activations, the layer operations — is exactly what you have built in this module.

---

## 12. Key Takeaways

1. **Forward propagation** is just repeated matrix multiplication + activation
2. **Backpropagation** is the chain rule applied systematically from output to input
3. **Activation functions** introduce non-linearity — without them, deep = shallow
4. **Loss functions** quantify error and their gradients tell us how to improve
5. **Weight initialization** matters — use He for ReLU, Xavier for sigmoid/tanh
6. **Mini-batch gradient descent** is the practical default
7. Every framework (PyTorch, TensorFlow, CoreML) does exactly these operations — just faster and with automatic differentiation

---

## Next Steps

In Module 02, you will learn PyTorch, which automates everything you built here:
- `torch.nn.Linear` replaces your manual weight matrices
- `torch.autograd` replaces your manual backpropagation
- `torch.optim.SGD` replaces your manual gradient descent loop

But now you **understand** what those abstractions are doing.
