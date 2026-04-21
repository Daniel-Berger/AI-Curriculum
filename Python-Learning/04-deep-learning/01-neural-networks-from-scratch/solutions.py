"""
Module 01 Solutions: Neural Networks from Scratch
==================================================
Complete implementations using ONLY NumPy.
"""

import numpy as np

# ============================================================================
# EXERCISE 1: Implement Sigmoid Activation
# ============================================================================

def sigmoid(z: np.ndarray) -> np.ndarray:
    """
    Compute the sigmoid activation function element-wise.

    The np.clip prevents overflow in exp for very large negative values.
    """
    return 1 / (1 + np.exp(-np.clip(z, -500, 500)))


# ============================================================================
# EXERCISE 2: Implement ReLU Activation
# ============================================================================

def relu(z: np.ndarray) -> np.ndarray:
    """
    Compute the ReLU activation function element-wise.

    np.maximum broadcasts element-wise: keeps z where z > 0, else 0.
    """
    return np.maximum(0, z)


# ============================================================================
# EXERCISE 3: Implement Leaky ReLU Activation
# ============================================================================

def leaky_relu(z: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    """
    Compute the Leaky ReLU activation function element-wise.

    np.where acts like a ternary: condition ? true_val : false_val
    Similar to Swift's ternary operator.
    """
    return np.where(z > 0, z, alpha * z)


# ============================================================================
# EXERCISE 4: Implement Softmax
# ============================================================================

def softmax(z: np.ndarray) -> np.ndarray:
    """
    Compute the softmax function along the last axis.

    We subtract the max value before exponentiating to prevent numerical
    overflow. This does not change the result because:
        e^(z_i - c) / sum(e^(z_j - c)) = e^(z_i) * e^(-c) / (sum(e^(z_j)) * e^(-c))
                                        = e^(z_i) / sum(e^(z_j))
    """
    # Subtract max for numerical stability (per row for batched inputs)
    exp_z = np.exp(z - np.max(z, axis=-1, keepdims=True))
    return exp_z / np.sum(exp_z, axis=-1, keepdims=True)


# ============================================================================
# EXERCISE 5: Implement Sigmoid Derivative
# ============================================================================

def sigmoid_derivative(z: np.ndarray) -> np.ndarray:
    """
    Compute the derivative of sigmoid with respect to z.

    The derivative has a beautifully simple form:
        sigma'(z) = sigma(z) * (1 - sigma(z))

    This means the gradient is largest when sigma(z) = 0.5 (i.e., z = 0)
    and vanishes when sigma(z) is near 0 or 1 — the "vanishing gradient" problem.
    """
    s = sigmoid(z)
    return s * (1 - s)


# ============================================================================
# EXERCISE 6: Implement ReLU Derivative
# ============================================================================

def relu_derivative(z: np.ndarray) -> np.ndarray:
    """
    Compute the derivative of ReLU with respect to z.

    The derivative is a simple step function:
    - 1 where z > 0 (gradient passes through unchanged)
    - 0 where z <= 0 (gradient is blocked — this causes "dying ReLU")

    Note: The derivative is technically undefined at z = 0.
    By convention, we set it to 0.
    """
    return (z > 0).astype(float)


# ============================================================================
# EXERCISE 7: Implement He Weight Initialization
# ============================================================================

def he_init(n_in: int, n_out: int) -> np.ndarray:
    """
    Initialize a weight matrix using He initialization.

    He initialization accounts for the fact that ReLU zeros out ~half the
    values, so we need to scale up by sqrt(2) compared to Xavier.

    This keeps the variance of activations stable across layers,
    preventing them from exploding or vanishing.
    """
    return np.random.randn(n_in, n_out) * np.sqrt(2.0 / n_in)


# ============================================================================
# EXERCISE 8: Implement Xavier Weight Initialization
# ============================================================================

def xavier_init(n_in: int, n_out: int) -> np.ndarray:
    """
    Initialize a weight matrix using Xavier/Glorot initialization.

    Xavier considers both the fan-in and fan-out to keep both forward
    activations and backward gradients at similar scales. Best for
    symmetric activations like sigmoid and tanh.
    """
    return np.random.randn(n_in, n_out) * np.sqrt(2.0 / (n_in + n_out))


# ============================================================================
# EXERCISE 9: Implement MSE Loss
# ============================================================================

def mse_loss(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Compute Mean Squared Error loss.

    MSE penalizes large errors quadratically — an error of 2 costs 4x as
    much as an error of 1. This makes it sensitive to outliers.
    """
    return np.mean((y_true - y_pred) ** 2)


# ============================================================================
# EXERCISE 10: Implement Binary Cross-Entropy Loss
# ============================================================================

def binary_cross_entropy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Compute binary cross-entropy loss.

    Cross-entropy measures the "distance" between two probability distributions.
    It penalizes confident wrong predictions very heavily:
        - If y=1 and y_pred=0.01 → loss contribution = -log(0.01) = 4.6
        - If y=1 and y_pred=0.99 → loss contribution = -log(0.99) = 0.01

    The epsilon clipping prevents log(0) = -infinity.
    """
    epsilon = 1e-15
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(
        y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred)
    )


# ============================================================================
# EXERCISE 11: Implement a Single Dense Layer Forward Pass
# ============================================================================

def dense_forward(X: np.ndarray, W: np.ndarray, b: np.ndarray,
                  activation: str = 'relu') -> tuple:
    """
    Compute the forward pass for a single dense layer.

    This is the fundamental building block: linear transform + non-linearity.
    The Z values are cached because backprop needs them to compute
    activation derivatives.
    """
    # Step 1: Linear transformation
    Z = X @ W + b  # Matrix multiply + broadcast bias

    # Step 2: Apply activation
    if activation == 'relu':
        A = relu(Z)
    elif activation == 'sigmoid':
        A = sigmoid(Z)
    elif activation == 'tanh':
        A = np.tanh(Z)
    else:
        raise ValueError(f"Unknown activation: {activation}")

    return A, Z


# ============================================================================
# EXERCISE 12: Implement Full Forward Propagation
# ============================================================================

def forward_propagation(X: np.ndarray,
                        weights: list,
                        biases: list,
                        hidden_activation: str = 'relu',
                        output_activation: str = 'sigmoid') -> tuple:
    """
    Forward propagation through a multi-layer network.

    We cache every intermediate Z and A value because backprop needs them:
    - Z values: needed for activation derivatives
    - A values: needed for weight gradients (dW = A_prev.T @ dZ)
    """
    cache = {'A0': X}
    A = X
    num_layers = len(weights)

    for l in range(num_layers):
        # Linear transformation
        Z = A @ weights[l] + biases[l]
        cache[f'Z{l+1}'] = Z

        # Apply activation — output layer uses different activation
        if l == num_layers - 1:
            # Output layer
            if output_activation == 'sigmoid':
                A = sigmoid(Z)
            elif output_activation == 'softmax':
                A = softmax(Z)
            else:
                A = Z  # linear output for regression
        else:
            # Hidden layer
            if hidden_activation == 'relu':
                A = relu(Z)
            elif hidden_activation == 'sigmoid':
                A = sigmoid(Z)
            elif hidden_activation == 'tanh':
                A = np.tanh(Z)

        cache[f'A{l+1}'] = A

    return A, cache


# ============================================================================
# EXERCISE 13: Implement Backward Propagation for a 2-Layer Network
# ============================================================================

def backward_propagation_2layer(y: np.ndarray,
                                 cache: dict,
                                 W1: np.ndarray,
                                 W2: np.ndarray) -> dict:
    """
    Backward propagation for a 2-layer network (ReLU hidden, Sigmoid output).

    Key insight: When combining sigmoid activation with binary cross-entropy loss,
    the gradient simplifies beautifully to just (A2 - y). This is NOT a coincidence —
    it's why these two are always paired together.

    The chain rule gives us:
        dL/dZ2 = dL/dA2 * dA2/dZ2
               = [-(y/A2) + (1-y)/(1-A2)] * [A2*(1-A2)]
               = A2 - y  (after simplification)
    """
    m = y.shape[0]

    # Retrieve cached values
    A0 = cache['A0']  # Input
    Z1 = cache['Z1']  # Pre-activation, layer 1
    A1 = cache['A1']  # Post-activation (ReLU), layer 1
    A2 = cache['A2']  # Post-activation (Sigmoid), layer 2 = output

    # ── Output layer gradients ──
    # Combined sigmoid + BCE gradient (the beautiful simplification)
    dZ2 = A2 - y                                       # (m, 1)

    # Weight and bias gradients for layer 2
    dW2 = A1.T @ dZ2 / m                               # (n_hidden, 1)
    db2 = np.sum(dZ2, axis=0, keepdims=True) / m       # (1, 1)

    # ── Hidden layer gradients ──
    # Propagate gradient backward through W2
    dA1 = dZ2 @ W2.T                                   # (m, n_hidden)

    # Gradient through ReLU: pass gradient where Z1 > 0, block where Z1 <= 0
    dZ1 = dA1 * relu_derivative(Z1)                    # (m, n_hidden)

    # Weight and bias gradients for layer 1
    dW1 = A0.T @ dZ1 / m                               # (n_in, n_hidden)
    db1 = np.sum(dZ1, axis=0, keepdims=True) / m       # (1, n_hidden)

    return {'dW1': dW1, 'db1': db1, 'dW2': dW2, 'db2': db2}


# ============================================================================
# EXERCISE 14: Implement Parameter Update (Gradient Descent Step)
# ============================================================================

def update_parameters(weights: list,
                      biases: list,
                      grads: dict,
                      learning_rate: float) -> tuple:
    """
    Update weights and biases using vanilla gradient descent.

    This is the simplest optimizer: move each parameter in the direction
    opposite to its gradient, scaled by the learning rate.

    w_new = w_old - lr * dL/dw

    The learning rate controls step size:
    - Too large → overshooting, divergence
    - Too small → very slow convergence
    - Just right → smooth convergence to minimum
    """
    updated_weights = []
    updated_biases = []

    for l in range(len(weights)):
        # Subtract gradient (we're minimizing the loss)
        new_W = weights[l] - learning_rate * grads[f'dW{l+1}']
        new_b = biases[l] - learning_rate * grads[f'db{l+1}']
        updated_weights.append(new_W)
        updated_biases.append(new_b)

    return updated_weights, updated_biases


# ============================================================================
# EXERCISE 15: Full Training Loop
# ============================================================================

def train_neural_network(X: np.ndarray,
                         y: np.ndarray,
                         hidden_size: int = 16,
                         epochs: int = 100,
                         learning_rate: float = 0.1,
                         batch_size: int = 32) -> dict:
    """
    Train a 2-layer neural network for binary classification.

    This ties together everything from the module:
    1. He initialization (Exercise 7)
    2. Forward propagation (Exercise 12)
    3. Loss computation (Exercise 10)
    4. Backward propagation (Exercise 13)
    5. Parameter updates (Exercise 14)

    The training loop structure is identical to what PyTorch uses — in the
    next module you'll see the same pattern with torch abstractions.
    """
    m, n_features = X.shape

    # ── Initialize parameters with He initialization ──
    # He init because we use ReLU in the hidden layer
    W1 = np.random.randn(n_features, hidden_size) * np.sqrt(2.0 / n_features)
    b1 = np.zeros((1, hidden_size))
    W2 = np.random.randn(hidden_size, 1) * np.sqrt(2.0 / hidden_size)
    b2 = np.zeros((1, 1))

    weights = [W1, W2]
    biases = [b1, b2]
    loss_history = []

    for epoch in range(epochs):
        # ── Shuffle data (prevents learning order-dependent patterns) ──
        indices = np.random.permutation(m)
        X_shuffled = X[indices]
        y_shuffled = y[indices]

        epoch_loss = 0.0
        num_batches = 0

        # ── Mini-batch training ──
        for start in range(0, m, batch_size):
            end = min(start + batch_size, m)
            X_batch = X_shuffled[start:end]
            y_batch = y_shuffled[start:end]

            # Forward propagation
            output, cache = forward_propagation(
                X_batch, weights, biases,
                hidden_activation='relu',
                output_activation='sigmoid'
            )

            # Compute loss
            batch_loss = binary_cross_entropy(y_batch, output)
            epoch_loss += batch_loss
            num_batches += 1

            # Backward propagation
            grads = backward_propagation_2layer(y_batch, cache, weights[0], weights[1])

            # Update parameters
            weights, biases = update_parameters(weights, biases, grads, learning_rate)

        # Record average loss for the epoch
        loss_history.append(epoch_loss / num_batches)

    return {
        'W1': weights[0],
        'b1': biases[0],
        'W2': weights[1],
        'b2': biases[1],
        'loss_history': loss_history
    }


# ============================================================================
# VERIFICATION — Run the same tests as exercises.py
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Neural Networks from Scratch — Solutions Verification")
    print("=" * 60)

    # Exercise 1: Sigmoid
    print("\n--- Exercise 1: Sigmoid ---")
    result = sigmoid(np.array([0.0, 2.0, -2.0]))
    print(f"  sigmoid([0, 2, -2]) = {result}")
    assert abs(result[0] - 0.5) < 1e-6
    print("  PASSED")

    # Exercise 2: ReLU
    print("\n--- Exercise 2: ReLU ---")
    result = relu(np.array([-3.0, -1.0, 0.0, 1.0, 3.0]))
    print(f"  relu([-3,-1,0,1,3]) = {result}")
    np.testing.assert_array_almost_equal(result, [0, 0, 0, 1, 3])
    print("  PASSED")

    # Exercise 3: Leaky ReLU
    print("\n--- Exercise 3: Leaky ReLU ---")
    result = leaky_relu(np.array([-2.0, 0.0, 2.0]), alpha=0.1)
    print(f"  leaky_relu([-2,0,2], alpha=0.1) = {result}")
    np.testing.assert_array_almost_equal(result, [-0.2, 0.0, 2.0])
    print("  PASSED")

    # Exercise 4: Softmax
    print("\n--- Exercise 4: Softmax ---")
    result = softmax(np.array([[2.0, 1.0, 0.1]]))
    print(f"  softmax([2, 1, 0.1]) = {result}")
    assert abs(np.sum(result) - 1.0) < 1e-6
    print("  PASSED")

    # Exercise 5: Sigmoid Derivative
    print("\n--- Exercise 5: Sigmoid Derivative ---")
    result = sigmoid_derivative(np.array([0.0]))
    print(f"  sigmoid'(0) = {result[0]}")
    assert abs(result[0] - 0.25) < 1e-6
    print("  PASSED")

    # Exercise 6: ReLU Derivative
    print("\n--- Exercise 6: ReLU Derivative ---")
    result = relu_derivative(np.array([-1.0, 0.0, 1.0]))
    print(f"  relu'([-1,0,1]) = {result}")
    np.testing.assert_array_almost_equal(result, [0, 0, 1])
    print("  PASSED")

    # Exercise 7: He Initialization
    print("\n--- Exercise 7: He Initialization ---")
    np.random.seed(42)
    W = he_init(784, 128)
    print(f"  Shape: {W.shape}, Std: {np.std(W):.4f}, Expected: {np.sqrt(2/784):.4f}")
    assert W.shape == (784, 128)
    print("  PASSED")

    # Exercise 8: Xavier Initialization
    print("\n--- Exercise 8: Xavier Initialization ---")
    np.random.seed(42)
    W = xavier_init(784, 128)
    print(f"  Shape: {W.shape}, Std: {np.std(W):.4f}, Expected: {np.sqrt(2/912):.4f}")
    assert W.shape == (784, 128)
    print("  PASSED")

    # Exercise 9: MSE Loss
    print("\n--- Exercise 9: MSE Loss ---")
    loss = mse_loss(np.array([[1.0], [2.0], [3.0]]), np.array([[1.5], [2.5], [3.5]]))
    print(f"  MSE = {loss}")
    assert abs(loss - 0.25) < 1e-6
    print("  PASSED")

    # Exercise 10: Binary Cross-Entropy
    print("\n--- Exercise 10: Binary Cross-Entropy ---")
    loss = binary_cross_entropy(
        np.array([[1.0], [0.0], [1.0]]),
        np.array([[0.9], [0.1], [0.8]])
    )
    print(f"  BCE = {loss:.4f}")
    assert 0 < loss < 1
    print("  PASSED")

    # Exercise 11: Dense Forward
    print("\n--- Exercise 11: Dense Forward ---")
    np.random.seed(42)
    A, Z = dense_forward(np.random.randn(4, 3), np.random.randn(3, 5), np.zeros((1, 5)))
    print(f"  Output shape: {A.shape}, All non-negative (ReLU): {np.all(A >= 0)}")
    assert A.shape == (4, 5) and np.all(A >= 0)
    print("  PASSED")

    # Exercise 12: Forward Propagation
    print("\n--- Exercise 12: Forward Propagation ---")
    np.random.seed(42)
    X = np.random.randn(10, 4)
    output, cache = forward_propagation(
        X,
        [np.random.randn(4, 8) * 0.1, np.random.randn(8, 1) * 0.1],
        [np.zeros((1, 8)), np.zeros((1, 1))]
    )
    print(f"  Output shape: {output.shape}, Range: [{output.min():.4f}, {output.max():.4f}]")
    assert output.shape == (10, 1)
    print("  PASSED")

    # Exercise 13: Backward Propagation
    print("\n--- Exercise 13: Backward Propagation ---")
    np.random.seed(42)
    X = np.random.randn(10, 4)
    y = np.random.randint(0, 2, (10, 1)).astype(float)
    W1 = np.random.randn(4, 8) * 0.1
    W2 = np.random.randn(8, 1) * 0.1
    output, cache = forward_propagation(X, [W1, W2], [np.zeros((1, 8)), np.zeros((1, 1))])
    grads = backward_propagation_2layer(y, cache, W1, W2)
    print(f"  dW1 shape: {grads['dW1'].shape}, dW2 shape: {grads['dW2'].shape}")
    assert grads['dW1'].shape == (4, 8) and grads['dW2'].shape == (8, 1)
    print("  PASSED")

    # Exercise 14: Parameter Update
    print("\n--- Exercise 14: Parameter Update ---")
    W1 = np.ones((3, 4))
    b1 = np.zeros((1, 4))
    grads = {'dW1': np.ones((3, 4)) * 0.1, 'db1': np.ones((1, 4)) * 0.05}
    new_w, new_b = update_parameters([W1], [b1], grads, learning_rate=1.0)
    print(f"  W after update: all {new_w[0][0, 0]} (expected 0.9)")
    np.testing.assert_array_almost_equal(new_w[0], np.ones((3, 4)) * 0.9)
    print("  PASSED")

    # Exercise 15: Full Training Loop
    print("\n--- Exercise 15: Full Training Loop ---")
    np.random.seed(42)
    X_train = np.vstack([
        np.random.randn(50, 2) + np.array([2, 2]),
        np.random.randn(50, 2) + np.array([-2, -2])
    ])
    y_train = np.vstack([np.ones((50, 1)), np.zeros((50, 1))])
    result = train_neural_network(X_train, y_train, hidden_size=8,
                                   epochs=200, learning_rate=0.1, batch_size=32)
    print(f"  Initial loss: {result['loss_history'][0]:.4f}")
    print(f"  Final loss:   {result['loss_history'][-1]:.4f}")
    assert result['loss_history'][-1] < result['loss_history'][0]
    print("  PASSED")

    print("\n" + "=" * 60)
    print("All solutions verified!")
    print("=" * 60)
