"""
Module 02 Solutions: PyTorch Fundamentals
==========================================
Complete implementations with explanatory comments.
"""

import torch
import torch.nn as nn
import numpy as np

# ============================================================================
# EXERCISE 1: Tensor Creation
# ============================================================================

def create_tensors() -> dict:
    """Create various tensors demonstrating different constructors."""
    return {
        'zeros': torch.zeros(3, 4),                              # 3x4 of 0s
        'ones': torch.ones(2, 3),                                 # 2x3 of 1s
        'range': torch.arange(0, 10, 2),                          # [0, 2, 4, 6, 8]
        'random': torch.randn(4, 4),                              # Standard normal
        'identity': torch.eye(5),                                  # 5x5 identity
        'custom': torch.tensor([[1, 2, 3], [4, 5, 6]], dtype=torch.float32),
    }


# ============================================================================
# EXERCISE 2: Tensor Data Types and Casting
# ============================================================================

def dtype_operations() -> dict:
    """Demonstrate dtype creation and casting."""
    # Create float64 tensor
    float64 = torch.tensor([1.5, 2.7, 3.9], dtype=torch.float64)

    # Cast to int64 — truncates (floors toward zero)
    # 1.5 → 1, 2.7 → 2, 3.9 → 3
    int64 = float64.to(torch.int64)

    # Cast int64 to float32
    float32 = int64.to(torch.float32)

    # Boolean tensor
    bool_tensor = torch.tensor([True, False, True, False])

    return {
        'float64': float64,
        'int64': int64,
        'float32': float32,
        'bool': bool_tensor,
    }


# ============================================================================
# EXERCISE 3: Tensor Reshaping
# ============================================================================

def reshape_tensors() -> dict:
    """Demonstrate various reshape operations."""
    t = torch.arange(24)

    matrix = t.reshape(4, 6)           # (24,) → (4, 6)
    cube = t.reshape(2, 3, 4)          # (24,) → (2, 3, 4)

    # unsqueeze adds a dimension of size 1 at the specified position
    unsqueezed = matrix.unsqueeze(0)   # (4, 6) → (1, 4, 6)

    # flatten collapses all dimensions back to 1D
    flattened = cube.flatten()         # (2, 3, 4) → (24,)

    # .T transposes a 2D tensor (swaps rows and columns)
    transposed = matrix.T              # (4, 6) → (6, 4)

    return {
        'matrix': matrix,
        'cube': cube,
        'unsqueezed': unsqueezed,
        'flattened': flattened,
        'transposed': transposed,
    }


# ============================================================================
# EXERCISE 4: Tensor Arithmetic and Reductions
# ============================================================================

def tensor_math() -> dict:
    """Demonstrate arithmetic and reduction operations."""
    A = torch.tensor([[1.0, 2.0, 3.0],
                       [4.0, 5.0, 6.0]])

    return {
        # Sum along dim=1 (across columns within each row)
        # Row 0: 1+2+3=6, Row 1: 4+5+6=15
        'row_sum': A.sum(dim=1),

        # Mean along dim=0 (across rows within each column)
        # Col 0: (1+4)/2=2.5, Col 1: (2+5)/2=3.5, Col 2: (3+6)/2=4.5
        'col_mean': A.mean(dim=0),

        # Sum all elements: 1+2+3+4+5+6 = 21
        'total_sum': A.sum(),

        # Max per row — .max(dim=1) returns (values, indices) namedtuple
        # We want just the values
        'max_per_row': A.max(dim=1).values,

        # Element-wise square
        'element_square': A ** 2,
    }


# ============================================================================
# EXERCISE 5: Matrix Multiplication
# ============================================================================

def matrix_operations() -> dict:
    """Demonstrate matrix and vector operations."""
    A = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    B = torch.tensor([[5.0, 6.0], [7.0, 8.0]])

    # Matrix multiplication: C[i,j] = sum(A[i,k] * B[k,j])
    # [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]] = [[19, 22], [43, 50]]
    matmul = A @ B

    # Element-wise: each element multiplied independently
    # [[1*5, 2*6], [3*7, 4*8]] = [[5, 12], [21, 32]]
    element_mul = A * B

    # Dot product: sum of element-wise products
    v1 = torch.tensor([1.0, 2.0, 3.0])
    v2 = torch.tensor([4.0, 5.0, 6.0])
    dot = torch.dot(v1, v2)  # 1*4 + 2*5 + 3*6 = 32

    # Outer product: every element of v1 multiplied by every element of v2
    v3 = torch.tensor([1.0, 2.0])
    v4 = torch.tensor([3.0, 4.0, 5.0])
    outer = torch.outer(v3, v4)  # [[3, 4, 5], [6, 8, 10]]

    return {
        'matmul': matmul,
        'element_mul': element_mul,
        'dot': dot,
        'outer': outer,
    }


# ============================================================================
# EXERCISE 6: NumPy Interop
# ============================================================================

def numpy_interop() -> dict:
    """Demonstrate NumPy-PyTorch interoperability."""
    np_array = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    # from_numpy shares memory — modifying one changes the other
    from_numpy = torch.from_numpy(np_array)

    # .numpy() converts tensor to NumPy (CPU only, shares memory)
    torch_tensor = torch.tensor([10.0, 20.0, 30.0])
    to_numpy = torch_tensor.numpy()

    # torch.tensor() creates a COPY — no memory sharing
    # This is safer when you want independent data
    safe_copy = torch.tensor(np_array)

    return {
        'from_numpy': from_numpy,
        'to_numpy': to_numpy,
        'safe_copy': safe_copy,
    }


# ============================================================================
# EXERCISE 7: Autograd Basics
# ============================================================================

def autograd_basics() -> dict:
    """Compute gradients using autograd."""
    # requires_grad=True tells PyTorch to record operations on this tensor
    x = torch.tensor(3.0, requires_grad=True)

    # Forward: y = x^3 + 2x^2 - 5x + 1
    # At x=3: y = 27 + 18 - 15 + 1 = 31
    y = x ** 3 + 2 * x ** 2 - 5 * x + 1

    # Backward: compute dy/dx
    # dy/dx = 3x^2 + 4x - 5
    # At x=3: 27 + 12 - 5 = 34
    y.backward()

    return {
        'gradient': x.grad.item(),  # .item() extracts scalar value
        'y_value': y.item(),
    }


# ============================================================================
# EXERCISE 8: Autograd with Vectors
# ============================================================================

def autograd_vectors() -> dict:
    """Compute gradients for matrix operations."""
    torch.manual_seed(42)
    W = torch.randn(3, 2, requires_grad=True)

    x = torch.tensor([1.0, 2.0, 3.0])

    # y = W^T @ x: (2, 3) @ (3,) = (2,)
    y = W.T @ x

    # loss = sum(y) — need scalar for backward()
    loss = y.sum()

    # Backward computes dloss/dW
    # loss = sum(W^T @ x) = sum over j of (sum over i of W[i,j] * x[i])
    # dloss/dW[i,j] = x[i] for all j
    # So each column of W.grad should be x = [1, 2, 3]
    loss.backward()

    return {
        'W_grad': W.grad,
        'W_grad_shape': tuple(W.grad.shape),
    }


# ============================================================================
# EXERCISE 9: Simple nn.Module
# ============================================================================

class LinearRegression(nn.Module):
    """Simple linear regression: y = Wx + b"""

    def __init__(self, input_dim: int):
        super().__init__()
        # nn.Linear creates W (weight) and b (bias) parameters automatically
        # It handles initialization and gradient tracking for you
        self.linear = nn.Linear(input_dim, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # nn.Linear computes x @ W.T + b internally
        # Note: PyTorch stores W transposed compared to our NumPy convention
        return self.linear(x)


# ============================================================================
# EXERCISE 10: Multi-Layer nn.Module
# ============================================================================

class TwoLayerNet(nn.Module):
    """Two-layer network for binary classification."""

    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        # Layer 1: Linear + ReLU
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()

        # Layer 2: Linear + Sigmoid
        self.fc2 = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # This is the PyTorch equivalent of your NumPy forward_propagation
        # from Module 01 — but autograd handles the backward pass for free
        x = self.fc1(x)       # Z1 = X @ W1 + b1
        x = self.relu(x)      # A1 = relu(Z1)
        x = self.fc2(x)       # Z2 = A1 @ W2 + b2
        x = self.sigmoid(x)   # A2 = sigmoid(Z2)
        return x


# ============================================================================
# EXERCISE 11: nn.Sequential Model
# ============================================================================

def build_sequential_model(input_dim: int, num_classes: int) -> nn.Sequential:
    """Build a classifier using nn.Sequential."""
    # nn.Sequential passes input through each layer in order
    # No need to write a forward() method — it's automatic
    return nn.Sequential(
        nn.Linear(input_dim, 128),
        nn.ReLU(),
        nn.Dropout(0.3),      # Randomly zero 30% of activations during training
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(64, num_classes),
        # No softmax! CrossEntropyLoss combines LogSoftmax + NLLLoss
        # This is more numerically stable than separate softmax + log
    )


# ============================================================================
# EXERCISE 12: Parameter Counting
# ============================================================================

def count_parameters(model: nn.Module) -> dict:
    """Count parameters in a model."""
    total = 0
    trainable = 0
    layer_params = {}

    for name, param in model.named_parameters():
        n = param.numel()  # Number of elements in this parameter tensor
        total += n
        if param.requires_grad:
            trainable += n
        layer_params[name] = n

    return {
        'total': total,
        'trainable': trainable,
        'non_trainable': total - trainable,
        'layer_params': layer_params,
    }


# ============================================================================
# EXERCISE 13: Model Device Management
# ============================================================================

def get_device() -> torch.device:
    """Return the best available device."""
    # Priority: MPS > CUDA > CPU
    # MPS = Metal Performance Shaders (Apple Silicon GPU)
    # CUDA = NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device('mps')
    elif torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')


def move_to_device(model: nn.Module, data: torch.Tensor,
                   device: torch.device) -> tuple:
    """Move model and data to device."""
    # model.to(device) moves ALL parameters and buffers to the device
    # This is an in-place operation for models (returns self)
    model = model.to(device)

    # For tensors, .to() returns a NEW tensor on the target device
    data = data.to(device)

    return model, data


# ============================================================================
# EXERCISE 14: Save and Load Model
# ============================================================================

def save_model(model: nn.Module, filepath: str) -> None:
    """Save model's state dict."""
    # state_dict() returns an OrderedDict of parameter name → tensor
    # This is the recommended save format because:
    # 1. It's portable across code changes
    # 2. It only saves learned values, not Python code
    # 3. It works with any serialization format
    torch.save(model.state_dict(), filepath)


def load_model(model: nn.Module, filepath: str) -> nn.Module:
    """Load state dict into model."""
    # Load the saved state dict
    # weights_only=True is a security best practice (avoids pickle exploits)
    state_dict = torch.load(filepath, weights_only=True)

    # Load parameters into the model
    # strict=True (default) ensures all keys match
    model.load_state_dict(state_dict)

    # Set to eval mode — disables dropout and uses running stats for batchnorm
    model.eval()

    return model


# ============================================================================
# EXERCISE 15: Putting It All Together — Train Linear Regression
# ============================================================================

def train_linear_regression(n_samples: int = 200,
                            n_features: int = 3,
                            epochs: int = 100,
                            lr: float = 0.01) -> dict:
    """Train linear regression with PyTorch — the standard training pattern."""

    # ── 1. Generate synthetic data ──
    # We know the true relationship so we can verify learning works
    torch.manual_seed(42)
    X = torch.randn(n_samples, n_features)
    true_weights = torch.tensor([[2.0], [-1.0], [0.5]])  # (3, 1)
    true_bias = 0.5
    noise = torch.randn(n_samples, 1) * 0.1
    y = X @ true_weights + true_bias + noise  # (n_samples, 1)

    # ── 2. Create model, loss, optimizer ──
    model = LinearRegression(n_features)
    criterion = nn.MSELoss()             # Mean Squared Error
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)

    # ── 3. Training loop ──
    # This is THE standard PyTorch training pattern.
    # You will use this exact structure in every project.
    loss_history = []

    for epoch in range(epochs):
        # Forward pass — compute predictions
        y_pred = model(X)

        # Compute loss
        loss = criterion(y_pred, y)

        # Backward pass — compute gradients
        # This replaces your entire backward_propagation function from Module 01!
        loss.backward()

        # Update parameters — gradient descent step
        # This replaces your update_parameters function!
        optimizer.step()

        # Zero gradients — MUST do this or gradients accumulate
        optimizer.zero_grad()

        # Record loss
        loss_history.append(loss.item())

    # ── 4. Extract learned parameters ──
    # .detach() removes from computation graph, .numpy() converts to NumPy
    learned_weight = model.linear.weight.detach().numpy()
    learned_bias = model.linear.bias.detach().numpy()

    return {
        'model': model,
        'loss_history': loss_history,
        'final_loss': loss_history[-1],
        'learned_weight': learned_weight,
        'learned_bias': learned_bias,
    }


# ============================================================================
# VERIFICATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PyTorch Fundamentals — Solutions Verification")
    print("=" * 60)

    # Exercise 1
    print("\n--- Exercise 1: Tensor Creation ---")
    result = create_tensors()
    assert result['zeros'].shape == (3, 4)
    assert result['custom'].dtype == torch.float32
    print("  PASSED")

    # Exercise 2
    print("\n--- Exercise 2: Dtype Operations ---")
    result = dtype_operations()
    assert result['float64'].dtype == torch.float64
    assert torch.equal(result['int64'], torch.tensor([1, 2, 3], dtype=torch.int64))
    print("  PASSED")

    # Exercise 3
    print("\n--- Exercise 3: Reshape Tensors ---")
    result = reshape_tensors()
    assert result['unsqueezed'].shape == (1, 4, 6)
    print("  PASSED")

    # Exercise 4
    print("\n--- Exercise 4: Tensor Math ---")
    result = tensor_math()
    assert torch.allclose(result['row_sum'], torch.tensor([6.0, 15.0]))
    print("  PASSED")

    # Exercise 5
    print("\n--- Exercise 5: Matrix Operations ---")
    result = matrix_operations()
    assert result['dot'].item() == 32.0
    print("  PASSED")

    # Exercise 6
    print("\n--- Exercise 6: NumPy Interop ---")
    result = numpy_interop()
    assert isinstance(result['to_numpy'], np.ndarray)
    print("  PASSED")

    # Exercise 7
    print("\n--- Exercise 7: Autograd Basics ---")
    result = autograd_basics()
    assert abs(result['gradient'] - 34.0) < 1e-4
    print(f"  dy/dx at x=3: {result['gradient']}")
    print("  PASSED")

    # Exercise 8
    print("\n--- Exercise 8: Autograd Vectors ---")
    result = autograd_vectors()
    assert result['W_grad_shape'] == (3, 2)
    print("  PASSED")

    # Exercise 9
    print("\n--- Exercise 9: LinearRegression ---")
    model = LinearRegression(5)
    assert model(torch.randn(3, 5)).shape == (3, 1)
    print("  PASSED")

    # Exercise 10
    print("\n--- Exercise 10: TwoLayerNet ---")
    model = TwoLayerNet(10, 32)
    output = model(torch.randn(4, 10))
    assert output.shape == (4, 1)
    assert torch.all(output >= 0) and torch.all(output <= 1)
    print("  PASSED")

    # Exercise 11
    print("\n--- Exercise 11: Sequential Model ---")
    model = build_sequential_model(20, 5)
    assert model(torch.randn(4, 20)).shape == (4, 5)
    print("  PASSED")

    # Exercise 12
    print("\n--- Exercise 12: Parameter Counting ---")
    model = nn.Sequential(nn.Linear(10, 32), nn.ReLU(), nn.Linear(32, 1))
    result = count_parameters(model)
    assert result['total'] == 385
    print(f"  Total params: {result['total']}")
    print(f"  Layer breakdown: {result['layer_params']}")
    print("  PASSED")

    # Exercise 13
    print("\n--- Exercise 13: Device Management ---")
    device = get_device()
    print(f"  Best device: {device}")
    model = nn.Linear(5, 1)
    data = torch.randn(3, 5)
    m, d = move_to_device(model, data, torch.device('cpu'))
    assert next(m.parameters()).device.type == 'cpu'
    print("  PASSED")

    # Exercise 14
    print("\n--- Exercise 14: Save/Load ---")
    import tempfile, os
    model = nn.Linear(5, 1)
    with tempfile.NamedTemporaryFile(suffix='.pth', delete=False) as f:
        filepath = f.name
    save_model(model, filepath)
    model2 = nn.Linear(5, 1)
    loaded = load_model(model2, filepath)
    for p1, p2 in zip(model.parameters(), loaded.parameters()):
        assert torch.equal(p1, p2)
    os.unlink(filepath)
    print("  PASSED")

    # Exercise 15
    print("\n--- Exercise 15: Train Linear Regression ---")
    torch.manual_seed(42)
    result = train_linear_regression(n_samples=200, n_features=3, epochs=500, lr=0.05)
    print(f"  Final loss: {result['final_loss']:.6f}")
    print(f"  Learned weights: {result['learned_weight'].flatten()}")
    print(f"  True weights:    [2.0, -1.0, 0.5]")
    print(f"  Learned bias:    {result['learned_bias'].flatten()}")
    print(f"  True bias:       0.5")
    assert result['final_loss'] < 0.1
    print("  PASSED")

    print("\n" + "=" * 60)
    print("All solutions verified!")
    print("=" * 60)
