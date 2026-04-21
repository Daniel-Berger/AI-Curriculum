"""
Module 01 Exercises: Neural Networks from Scratch
==================================================
Build neural network components using ONLY NumPy.
No PyTorch, no TensorFlow — just math.

All exercises use NumPy arrays. Run this file to check your work:
    python exercises.py
"""

import numpy as np

# ============================================================================
# EXERCISE 1: Implement Sigmoid Activation
# ============================================================================

def sigmoid(z: np.ndarray) -> np.ndarray:
    """
    Compute the sigmoid activation function element-wise.

    Formula: sigma(z) = 1 / (1 + e^(-z))

    Args:
        z: Input array of any shape

    Returns:
        Array of same shape with values in (0, 1)
    """
    pass


# ============================================================================
# EXERCISE 2: Implement ReLU Activation
# ============================================================================

def relu(z: np.ndarray) -> np.ndarray:
    """
    Compute the ReLU activation function element-wise.

    Formula: relu(z) = max(0, z)

    Args:
        z: Input array of any shape

    Returns:
        Array of same shape with negative values replaced by 0
    """
    pass


# ============================================================================
# EXERCISE 3: Implement Leaky ReLU Activation
# ============================================================================

def leaky_relu(z: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    """
    Compute the Leaky ReLU activation function element-wise.

    Formula: leaky_relu(z) = z if z > 0 else alpha * z

    Args:
        z: Input array of any shape
        alpha: Slope for negative values (default 0.01)

    Returns:
        Array of same shape
    """
    pass


# ============================================================================
# EXERCISE 4: Implement Softmax
# ============================================================================

def softmax(z: np.ndarray) -> np.ndarray:
    """
    Compute the softmax function along the last axis.

    Formula: softmax(z_i) = e^(z_i) / sum(e^(z_j))

    IMPORTANT: Subtract the max for numerical stability before exponentiating.

    Args:
        z: Input array, shape (m, n_classes) or (n_classes,)

    Returns:
        Array of same shape with values in (0, 1) that sum to 1 along last axis
    """
    pass


# ============================================================================
# EXERCISE 5: Implement Sigmoid Derivative
# ============================================================================

def sigmoid_derivative(z: np.ndarray) -> np.ndarray:
    """
    Compute the derivative of sigmoid with respect to z.

    Formula: sigma'(z) = sigma(z) * (1 - sigma(z))

    Hint: Use your sigmoid function from Exercise 1.

    Args:
        z: Input array (pre-activation values)

    Returns:
        Array of same shape containing the derivatives
    """
    pass


# ============================================================================
# EXERCISE 6: Implement ReLU Derivative
# ============================================================================

def relu_derivative(z: np.ndarray) -> np.ndarray:
    """
    Compute the derivative of ReLU with respect to z.

    Formula: relu'(z) = 1 if z > 0 else 0

    Args:
        z: Input array (pre-activation values)

    Returns:
        Array of same shape containing 0s and 1s
    """
    pass


# ============================================================================
# EXERCISE 7: Implement He Weight Initialization
# ============================================================================

def he_init(n_in: int, n_out: int) -> np.ndarray:
    """
    Initialize a weight matrix using He initialization.

    Formula: W ~ N(0, sqrt(2 / n_in))

    This is the recommended initialization for ReLU networks.

    Args:
        n_in: Number of input neurons (fan-in)
        n_out: Number of output neurons (fan-out)

    Returns:
        Weight matrix of shape (n_in, n_out)
    """
    pass


# ============================================================================
# EXERCISE 8: Implement Xavier Weight Initialization
# ============================================================================

def xavier_init(n_in: int, n_out: int) -> np.ndarray:
    """
    Initialize a weight matrix using Xavier/Glorot initialization.

    Formula: W ~ N(0, sqrt(2 / (n_in + n_out)))

    This is recommended for sigmoid/tanh activations.

    Args:
        n_in: Number of input neurons (fan-in)
        n_out: Number of output neurons (fan-out)

    Returns:
        Weight matrix of shape (n_in, n_out)
    """
    pass


# ============================================================================
# EXERCISE 9: Implement MSE Loss
# ============================================================================

def mse_loss(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Compute Mean Squared Error loss.

    Formula: L = (1/m) * sum((y_true - y_pred)^2)

    Args:
        y_true: Ground truth values, shape (m, n) or (m,)
        y_pred: Predicted values, same shape as y_true

    Returns:
        Scalar loss value
    """
    pass


# ============================================================================
# EXERCISE 10: Implement Binary Cross-Entropy Loss
# ============================================================================

def binary_cross_entropy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Compute binary cross-entropy loss.

    Formula: L = -(1/m) * sum(y * log(y_pred) + (1-y) * log(1-y_pred))

    IMPORTANT: Clip y_pred to [epsilon, 1-epsilon] to avoid log(0).
    Use epsilon = 1e-15.

    Args:
        y_true: Ground truth labels (0 or 1), shape (m, 1) or (m,)
        y_pred: Predicted probabilities, same shape as y_true

    Returns:
        Scalar loss value
    """
    pass


# ============================================================================
# EXERCISE 11: Implement a Single Dense Layer Forward Pass
# ============================================================================

def dense_forward(X: np.ndarray, W: np.ndarray, b: np.ndarray,
                  activation: str = 'relu') -> tuple:
    """
    Compute the forward pass for a single dense (fully-connected) layer.

    Steps:
        1. Compute linear transformation: Z = X @ W + b
        2. Apply activation function to Z

    Args:
        X: Input data, shape (m, n_in)
        W: Weight matrix, shape (n_in, n_out)
        b: Bias vector, shape (1, n_out)
        activation: 'relu', 'sigmoid', or 'tanh'

    Returns:
        Tuple of (A, Z) where:
            A: activated output, shape (m, n_out)
            Z: pre-activation values, shape (m, n_out) (needed for backprop)
    """
    pass


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

    For each hidden layer: Z = A_prev @ W + b, then A = hidden_activation(Z)
    For the output layer: Z = A_prev @ W + b, then A = output_activation(Z)

    Args:
        X: Input data, shape (m, n_features)
        weights: List of weight matrices [W1, W2, ..., WL]
        biases: List of bias vectors [b1, b2, ..., bL]
        hidden_activation: Activation for hidden layers ('relu', 'sigmoid', 'tanh')
        output_activation: Activation for output layer ('sigmoid', 'softmax')

    Returns:
        Tuple of (output, cache) where:
            output: final layer activations, shape (m, n_output)
            cache: dict with keys 'A0', 'Z1', 'A1', 'Z2', 'A2', etc.
    """
    pass


# ============================================================================
# EXERCISE 13: Implement Backward Propagation for a 2-Layer Network
# ============================================================================

def backward_propagation_2layer(y: np.ndarray,
                                 cache: dict,
                                 W1: np.ndarray,
                                 W2: np.ndarray) -> dict:
    """
    Backward propagation for a specific 2-layer network:
        Input → [Linear + ReLU] → [Linear + Sigmoid] → Output

    Uses binary cross-entropy loss. The combined sigmoid + BCE gradient
    simplifies to: dZ2 = A2 - y

    Args:
        y: True labels, shape (m, 1)
        cache: Dict from forward pass containing A0, Z1, A1, Z2, A2
        W1: Weight matrix for layer 1, shape (n_in, n_hidden)
        W2: Weight matrix for layer 2, shape (n_hidden, 1)

    Returns:
        Dict with keys: 'dW1', 'db1', 'dW2', 'db2'
        Each gradient has the same shape as its corresponding parameter.
    """
    pass


# ============================================================================
# EXERCISE 14: Implement Parameter Update (Gradient Descent Step)
# ============================================================================

def update_parameters(weights: list,
                      biases: list,
                      grads: dict,
                      learning_rate: float) -> tuple:
    """
    Update weights and biases using vanilla gradient descent.

    For each layer l:
        W[l] = W[l] - learning_rate * dW[l+1]
        b[l] = b[l] - learning_rate * db[l+1]

    Note: grads uses 1-indexed keys (dW1, dW2, ...) while the lists
    are 0-indexed.

    Args:
        weights: List of weight matrices [W1, W2, ...]
        biases: List of bias vectors [b1, b2, ...]
        grads: Dict with gradient keys 'dW1', 'db1', 'dW2', 'db2', ...
        learning_rate: Step size for gradient descent

    Returns:
        Tuple of (updated_weights, updated_biases)
    """
    pass


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
    Train a 2-layer neural network (1 hidden layer) for binary classification.

    Architecture: Input → [Linear + ReLU] → [Linear + Sigmoid] → Output

    Steps for each epoch:
        1. Shuffle the data
        2. For each mini-batch:
            a. Forward propagation
            b. Compute loss (binary cross-entropy)
            c. Backward propagation
            d. Update parameters
        3. Record average loss for the epoch

    Args:
        X: Training data, shape (m, n_features)
        y: Labels, shape (m, 1) with values 0 or 1
        hidden_size: Number of neurons in hidden layer
        epochs: Number of training epochs
        learning_rate: Step size for gradient descent
        batch_size: Mini-batch size

    Returns:
        Dict with keys:
            'W1': trained weight matrix 1
            'b1': trained bias vector 1
            'W2': trained weight matrix 2
            'b2': trained bias vector 2
            'loss_history': list of average loss per epoch
    """
    pass


# ============================================================================
# VERIFICATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Neural Networks from Scratch — Exercise Verification")
    print("=" * 60)

    # ── Exercise 1: Sigmoid ──
    print("\n--- Exercise 1: Sigmoid ---")
    try:
        result = sigmoid(np.array([0.0, 2.0, -2.0]))
        assert result is not None, "sigmoid returned None"
        assert result.shape == (3,), f"Wrong shape: {result.shape}"
        assert abs(result[0] - 0.5) < 1e-6, f"sigmoid(0) should be 0.5, got {result[0]}"
        assert result[1] > 0.8, f"sigmoid(2) should be > 0.8, got {result[1]}"
        assert result[2] < 0.2, f"sigmoid(-2) should be < 0.2, got {result[2]}"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 2: ReLU ──
    print("\n--- Exercise 2: ReLU ---")
    try:
        result = relu(np.array([-3.0, -1.0, 0.0, 1.0, 3.0]))
        assert result is not None, "relu returned None"
        np.testing.assert_array_almost_equal(result, [0, 0, 0, 1, 3])
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 3: Leaky ReLU ──
    print("\n--- Exercise 3: Leaky ReLU ---")
    try:
        result = leaky_relu(np.array([-2.0, 0.0, 2.0]), alpha=0.1)
        assert result is not None, "leaky_relu returned None"
        np.testing.assert_array_almost_equal(result, [-0.2, 0.0, 2.0])
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 4: Softmax ──
    print("\n--- Exercise 4: Softmax ---")
    try:
        result = softmax(np.array([[2.0, 1.0, 0.1]]))
        assert result is not None, "softmax returned None"
        assert abs(np.sum(result) - 1.0) < 1e-6, f"Softmax should sum to 1, got {np.sum(result)}"
        assert result[0, 0] > result[0, 1] > result[0, 2], "Ordering should be preserved"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 5: Sigmoid Derivative ──
    print("\n--- Exercise 5: Sigmoid Derivative ---")
    try:
        result = sigmoid_derivative(np.array([0.0]))
        assert result is not None, "sigmoid_derivative returned None"
        assert abs(result[0] - 0.25) < 1e-6, f"sigmoid'(0) should be 0.25, got {result[0]}"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 6: ReLU Derivative ──
    print("\n--- Exercise 6: ReLU Derivative ---")
    try:
        result = relu_derivative(np.array([-1.0, 0.0, 1.0]))
        assert result is not None, "relu_derivative returned None"
        np.testing.assert_array_almost_equal(result, [0, 0, 1])
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 7: He Initialization ──
    print("\n--- Exercise 7: He Initialization ---")
    try:
        np.random.seed(42)
        W = he_init(784, 128)
        assert W is not None, "he_init returned None"
        assert W.shape == (784, 128), f"Wrong shape: {W.shape}"
        expected_std = np.sqrt(2.0 / 784)
        actual_std = np.std(W)
        assert abs(actual_std - expected_std) < 0.01, \
            f"Std should be ~{expected_std:.4f}, got {actual_std:.4f}"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 8: Xavier Initialization ──
    print("\n--- Exercise 8: Xavier Initialization ---")
    try:
        np.random.seed(42)
        W = xavier_init(784, 128)
        assert W is not None, "xavier_init returned None"
        assert W.shape == (784, 128), f"Wrong shape: {W.shape}"
        expected_std = np.sqrt(2.0 / (784 + 128))
        actual_std = np.std(W)
        assert abs(actual_std - expected_std) < 0.01, \
            f"Std should be ~{expected_std:.4f}, got {actual_std:.4f}"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 9: MSE Loss ──
    print("\n--- Exercise 9: MSE Loss ---")
    try:
        y_true = np.array([[1.0], [2.0], [3.0]])
        y_pred = np.array([[1.0], [2.0], [3.0]])
        assert mse_loss(y_true, y_pred) == 0.0, "Perfect prediction should give 0 loss"
        y_pred2 = np.array([[1.5], [2.5], [3.5]])
        loss = mse_loss(y_true, y_pred2)
        assert abs(loss - 0.25) < 1e-6, f"Expected 0.25, got {loss}"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 10: Binary Cross-Entropy ──
    print("\n--- Exercise 10: Binary Cross-Entropy ---")
    try:
        y_true = np.array([[1.0], [0.0], [1.0]])
        y_pred = np.array([[0.9], [0.1], [0.8]])
        loss = binary_cross_entropy(y_true, y_pred)
        assert loss is not None, "binary_cross_entropy returned None"
        assert loss > 0, "Loss should be positive"
        assert loss < 1, "Loss should be < 1 for these predictions"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 11: Dense Forward ──
    print("\n--- Exercise 11: Dense Forward ---")
    try:
        np.random.seed(42)
        X = np.random.randn(4, 3)
        W = np.random.randn(3, 5)
        b = np.zeros((1, 5))
        A, Z = dense_forward(X, W, b, activation='relu')
        assert A is not None and Z is not None, "dense_forward returned None"
        assert A.shape == (4, 5), f"Wrong output shape: {A.shape}"
        assert Z.shape == (4, 5), f"Wrong Z shape: {Z.shape}"
        assert np.all(A >= 0), "ReLU output should be non-negative"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 12: Forward Propagation ──
    print("\n--- Exercise 12: Forward Propagation ---")
    try:
        np.random.seed(42)
        X = np.random.randn(10, 4)
        W1 = np.random.randn(4, 8) * 0.1
        b1 = np.zeros((1, 8))
        W2 = np.random.randn(8, 1) * 0.1
        b2 = np.zeros((1, 1))
        output, cache = forward_propagation(X, [W1, W2], [b1, b2])
        assert output is not None, "forward_propagation returned None"
        assert output.shape == (10, 1), f"Wrong output shape: {output.shape}"
        assert np.all(output > 0) and np.all(output < 1), "Sigmoid output should be in (0,1)"
        assert 'A0' in cache and 'Z1' in cache and 'A1' in cache, "Cache missing keys"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 13: Backward Propagation ──
    print("\n--- Exercise 13: Backward Propagation ---")
    try:
        np.random.seed(42)
        X = np.random.randn(10, 4)
        y = np.random.randint(0, 2, (10, 1)).astype(float)
        W1 = np.random.randn(4, 8) * 0.1
        b1 = np.zeros((1, 8))
        W2 = np.random.randn(8, 1) * 0.1
        b2 = np.zeros((1, 1))
        output, cache = forward_propagation(X, [W1, W2], [b1, b2])
        grads = backward_propagation_2layer(y, cache, W1, W2)
        assert grads is not None, "backward_propagation returned None"
        assert grads['dW1'].shape == W1.shape, f"dW1 wrong shape: {grads['dW1'].shape}"
        assert grads['dW2'].shape == W2.shape, f"dW2 wrong shape: {grads['dW2'].shape}"
        assert grads['db1'].shape == b1.shape, f"db1 wrong shape: {grads['db1'].shape}"
        assert grads['db2'].shape == b2.shape, f"db2 wrong shape: {grads['db2'].shape}"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 14: Parameter Update ──
    print("\n--- Exercise 14: Parameter Update ---")
    try:
        W1 = np.ones((3, 4))
        b1 = np.zeros((1, 4))
        grads = {'dW1': np.ones((3, 4)) * 0.1, 'db1': np.ones((1, 4)) * 0.05}
        new_w, new_b = update_parameters([W1], [b1], grads, learning_rate=1.0)
        assert new_w is not None, "update_parameters returned None"
        np.testing.assert_array_almost_equal(new_w[0], np.ones((3, 4)) * 0.9)
        np.testing.assert_array_almost_equal(new_b[0], np.ones((1, 4)) * -0.05)
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 15: Full Training Loop ──
    print("\n--- Exercise 15: Full Training Loop ---")
    try:
        np.random.seed(42)
        # Simple linearly separable data
        X_train = np.vstack([
            np.random.randn(50, 2) + np.array([2, 2]),
            np.random.randn(50, 2) + np.array([-2, -2])
        ])
        y_train = np.vstack([np.ones((50, 1)), np.zeros((50, 1))])
        result = train_neural_network(X_train, y_train, hidden_size=8,
                                       epochs=200, learning_rate=0.1, batch_size=32)
        assert result is not None, "train_neural_network returned None"
        assert 'W1' in result and 'W2' in result, "Missing weight keys"
        assert 'loss_history' in result, "Missing loss_history"
        assert len(result['loss_history']) == 200, "Should have 200 loss values"
        assert result['loss_history'][-1] < result['loss_history'][0], \
            "Loss should decrease during training"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    print("\n" + "=" * 60)
    print("Verification complete!")
    print("=" * 60)
