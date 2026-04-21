"""
Module 02 Exercises: PyTorch Fundamentals
==========================================
Learn tensors, autograd, and nn.Module by doing.

Run this file to check your work:
    python exercises.py
"""

import torch
import torch.nn as nn
import numpy as np

# ============================================================================
# EXERCISE 1: Tensor Creation
# ============================================================================

def create_tensors() -> dict:
    """
    Create the following tensors and return them in a dict:

    1. 'zeros': A 3x4 tensor of zeros (float32)
    2. 'ones': A 2x3 tensor of ones (float32)
    3. 'range': A 1D tensor containing [0, 2, 4, 6, 8] using torch.arange
    4. 'random': A 4x4 tensor from standard normal distribution
    5. 'identity': A 5x5 identity matrix
    6. 'custom': The tensor [[1, 2, 3], [4, 5, 6]] as float32

    Returns:
        Dict with keys: 'zeros', 'ones', 'range', 'random', 'identity', 'custom'
    """
    pass


# ============================================================================
# EXERCISE 2: Tensor Data Types and Casting
# ============================================================================

def dtype_operations() -> dict:
    """
    Perform the following dtype operations:

    1. Create a float64 tensor [1.5, 2.7, 3.9] named 'float64'
    2. Cast it to int64 (truncation expected) named 'int64'
    3. Cast the int64 tensor to float32 named 'float32'
    4. Create a boolean tensor [True, False, True, False] named 'bool'

    Returns:
        Dict with keys: 'float64', 'int64', 'float32', 'bool'
    """
    pass


# ============================================================================
# EXERCISE 3: Tensor Reshaping
# ============================================================================

def reshape_tensors() -> dict:
    """
    Given a 1D tensor of 24 elements (torch.arange(24)), create:

    1. 'matrix': Reshape to (4, 6)
    2. 'cube': Reshape to (2, 3, 4)
    3. 'unsqueezed': Take the matrix (4, 6) and add a batch dimension
       at position 0 to get shape (1, 4, 6)
    4. 'flattened': Take the cube (2, 3, 4) and flatten it back to 1D
    5. 'transposed': Transpose the matrix (4, 6) to get (6, 4)

    Returns:
        Dict with keys: 'matrix', 'cube', 'unsqueezed', 'flattened', 'transposed'
    """
    pass


# ============================================================================
# EXERCISE 4: Tensor Arithmetic and Reductions
# ============================================================================

def tensor_math() -> dict:
    """
    Given:
        A = torch.tensor([[1.0, 2.0, 3.0],
                           [4.0, 5.0, 6.0]])

    Compute:
    1. 'row_sum': Sum along rows (dim=1), shape should be (2,)
    2. 'col_mean': Mean along columns (dim=0), shape should be (3,)
    3. 'total_sum': Sum of all elements (scalar)
    4. 'max_per_row': Max value per row, shape should be (2,)
       (just the values, not indices)
    5. 'element_square': Element-wise square of A, shape (2, 3)

    Returns:
        Dict with keys: 'row_sum', 'col_mean', 'total_sum', 'max_per_row',
                         'element_square'
    """
    pass


# ============================================================================
# EXERCISE 5: Matrix Multiplication
# ============================================================================

def matrix_operations() -> dict:
    """
    Perform the following matrix operations:

    1. Create A = [[1, 2], [3, 4]] and B = [[5, 6], [7, 8]] as float tensors
    2. 'matmul': Compute A @ B
    3. 'element_mul': Compute element-wise A * B
    4. 'dot': Compute dot product of vectors [1, 2, 3] and [4, 5, 6]
    5. 'outer': Compute outer product of vectors [1, 2] and [3, 4, 5]
       Hint: Use .unsqueeze() and matrix multiply, or torch.outer

    Returns:
        Dict with keys: 'matmul', 'element_mul', 'dot', 'outer'
    """
    pass


# ============================================================================
# EXERCISE 6: NumPy Interop
# ============================================================================

def numpy_interop() -> dict:
    """
    Demonstrate NumPy-PyTorch interoperability:

    1. Create a NumPy array: np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    2. 'from_numpy': Convert to a PyTorch tensor using torch.from_numpy
    3. 'to_numpy': Create a new torch tensor [10.0, 20.0, 30.0] and
       convert to NumPy using .numpy()
    4. 'safe_copy': Create a torch tensor from the NumPy array that does NOT
       share memory (use torch.tensor, not torch.from_numpy)

    Returns:
        Dict with keys: 'from_numpy', 'to_numpy', 'safe_copy'
        'to_numpy' should be a NumPy array, others should be tensors
    """
    pass


# ============================================================================
# EXERCISE 7: Autograd Basics
# ============================================================================

def autograd_basics() -> dict:
    """
    Use autograd to compute gradients:

    1. Create x = torch.tensor(3.0, requires_grad=True)
    2. Compute y = x^3 + 2*x^2 - 5*x + 1
    3. Call y.backward()
    4. 'gradient': The gradient dy/dx at x=3
       (dy/dx = 3x^2 + 4x - 5; at x=3: 27 + 12 - 5 = 34)
    5. 'y_value': The value of y at x=3

    Returns:
        Dict with keys: 'gradient' (float), 'y_value' (float)
    """
    pass


# ============================================================================
# EXERCISE 8: Autograd with Vectors
# ============================================================================

def autograd_vectors() -> dict:
    """
    Compute gradients for vector operations:

    1. Create W = torch.randn(3, 2, requires_grad=True) with manual seed 42
       (set torch.manual_seed(42) before creating W)
    2. Create x = torch.tensor([1.0, 2.0, 3.0]) (no grad needed)
    3. Compute y = W.T @ x (matrix-vector multiply), shape should be (2,)
    4. Compute loss = y.sum()
    5. Call loss.backward()
    6. Return W.grad

    Returns:
        Dict with keys:
            'W_grad': The gradient tensor, shape (3, 2)
            'W_grad_shape': The shape as a tuple
    """
    pass


# ============================================================================
# EXERCISE 9: Simple nn.Module
# ============================================================================

class LinearRegression(nn.Module):
    """
    Implement a simple linear regression model: y = Wx + b

    The model should have:
    - One nn.Linear layer with input_dim features and 1 output

    Args:
        input_dim: Number of input features
    """

    def __init__(self, input_dim: int):
        super().__init__()
        # TODO: Define one linear layer
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass: just apply the linear layer.

        Args:
            x: Input tensor, shape (batch_size, input_dim)

        Returns:
            Predictions, shape (batch_size, 1)
        """
        pass


# ============================================================================
# EXERCISE 10: Multi-Layer nn.Module
# ============================================================================

class TwoLayerNet(nn.Module):
    """
    Implement a two-layer neural network for binary classification.

    Architecture:
        Linear(input_dim, hidden_dim) → ReLU → Linear(hidden_dim, 1) → Sigmoid

    Args:
        input_dim: Number of input features
        hidden_dim: Number of hidden neurons
    """

    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        # TODO: Define layers
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.

        Args:
            x: Input tensor, shape (batch_size, input_dim)

        Returns:
            Predictions (probabilities), shape (batch_size, 1)
        """
        pass


# ============================================================================
# EXERCISE 11: nn.Sequential Model
# ============================================================================

def build_sequential_model(input_dim: int, num_classes: int) -> nn.Sequential:
    """
    Build a classifier using nn.Sequential.

    Architecture:
        Linear(input_dim, 128) → ReLU → Dropout(0.3) →
        Linear(128, 64) → ReLU → Dropout(0.3) →
        Linear(64, num_classes)

    NOTE: No softmax at the end — PyTorch's CrossEntropyLoss includes it.

    Args:
        input_dim: Number of input features
        num_classes: Number of output classes

    Returns:
        nn.Sequential model
    """
    pass


# ============================================================================
# EXERCISE 12: Parameter Counting
# ============================================================================

def count_parameters(model: nn.Module) -> dict:
    """
    Count the parameters in a model.

    Returns:
        Dict with keys:
            'total': total number of parameters
            'trainable': number of trainable parameters (requires_grad=True)
            'non_trainable': number of non-trainable parameters
            'layer_params': dict mapping layer name to parameter count
                           e.g. {'fc1.weight': 1280, 'fc1.bias': 128, ...}
    """
    pass


# ============================================================================
# EXERCISE 13: Model Device Management
# ============================================================================

def get_device() -> torch.device:
    """
    Return the best available device for training.

    Priority: MPS (Apple Silicon) > CUDA (NVIDIA) > CPU

    Returns:
        torch.device object
    """
    pass


def move_to_device(model: nn.Module, data: torch.Tensor,
                   device: torch.device) -> tuple:
    """
    Move both model and data to the specified device.

    Args:
        model: An nn.Module
        data: A tensor
        device: Target device

    Returns:
        Tuple of (model_on_device, data_on_device)
    """
    pass


# ============================================================================
# EXERCISE 14: Save and Load Model
# ============================================================================

def save_model(model: nn.Module, filepath: str) -> None:
    """
    Save a model's state dict to disk.

    Args:
        model: Trained nn.Module
        filepath: Path to save the .pth file
    """
    pass


def load_model(model: nn.Module, filepath: str) -> nn.Module:
    """
    Load a state dict from disk into a model.

    Args:
        model: An nn.Module instance (same architecture as saved model)
        filepath: Path to the .pth file

    Returns:
        The model with loaded weights, in eval mode
    """
    pass


# ============================================================================
# EXERCISE 15: Putting It All Together — Train Linear Regression
# ============================================================================

def train_linear_regression(n_samples: int = 200,
                            n_features: int = 3,
                            epochs: int = 100,
                            lr: float = 0.01) -> dict:
    """
    Train a linear regression model using PyTorch.

    Steps:
    1. Generate synthetic data:
       - X = torch.randn(n_samples, n_features)
       - true_weights = torch.tensor([2.0, -1.0, 0.5])  (or appropriate size)
       - y = X @ true_weights + 0.5 (bias) + noise * 0.1
    2. Create a LinearRegression model (from Exercise 9)
    3. Use nn.MSELoss() as loss function
    4. Use torch.optim.SGD as optimizer
    5. Train for the specified number of epochs
    6. Record loss history

    Returns:
        Dict with keys:
            'model': trained LinearRegression model
            'loss_history': list of loss values per epoch
            'final_loss': last loss value
            'learned_weight': the learned weight matrix (as numpy array)
            'learned_bias': the learned bias (as numpy array)
    """
    pass


# ============================================================================
# VERIFICATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PyTorch Fundamentals — Exercise Verification")
    print("=" * 60)

    # ── Exercise 1: Tensor Creation ──
    print("\n--- Exercise 1: Tensor Creation ---")
    try:
        result = create_tensors()
        assert result is not None, "Returned None"
        assert result['zeros'].shape == (3, 4), f"zeros wrong shape: {result['zeros'].shape}"
        assert result['ones'].shape == (2, 3), f"ones wrong shape"
        assert torch.equal(result['range'], torch.arange(0, 10, 2)), "range incorrect"
        assert result['random'].shape == (4, 4), f"random wrong shape"
        assert result['identity'].shape == (5, 5), f"identity wrong shape"
        assert result['custom'].shape == (2, 3), f"custom wrong shape"
        assert result['custom'].dtype == torch.float32, f"custom wrong dtype"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 2: Dtype Operations ──
    print("\n--- Exercise 2: Dtype Operations ---")
    try:
        result = dtype_operations()
        assert result is not None, "Returned None"
        assert result['float64'].dtype == torch.float64
        assert result['int64'].dtype == torch.int64
        assert result['float32'].dtype == torch.float32
        assert result['bool'].dtype == torch.bool
        assert torch.equal(result['int64'], torch.tensor([1, 2, 3], dtype=torch.int64))
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 3: Reshape Tensors ──
    print("\n--- Exercise 3: Reshape Tensors ---")
    try:
        result = reshape_tensors()
        assert result is not None, "Returned None"
        assert result['matrix'].shape == (4, 6), f"matrix: {result['matrix'].shape}"
        assert result['cube'].shape == (2, 3, 4), f"cube: {result['cube'].shape}"
        assert result['unsqueezed'].shape == (1, 4, 6), f"unsqueezed: {result['unsqueezed'].shape}"
        assert result['flattened'].shape == (24,), f"flattened: {result['flattened'].shape}"
        assert result['transposed'].shape == (6, 4), f"transposed: {result['transposed'].shape}"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 4: Tensor Math ──
    print("\n--- Exercise 4: Tensor Math ---")
    try:
        result = tensor_math()
        assert result is not None, "Returned None"
        assert torch.allclose(result['row_sum'], torch.tensor([6.0, 15.0]))
        assert torch.allclose(result['col_mean'], torch.tensor([2.5, 3.5, 4.5]))
        assert result['total_sum'].item() == 21.0
        assert torch.allclose(result['max_per_row'], torch.tensor([3.0, 6.0]))
        expected_sq = torch.tensor([[1, 4, 9], [16, 25, 36]], dtype=torch.float32)
        assert torch.allclose(result['element_square'], expected_sq)
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 5: Matrix Operations ──
    print("\n--- Exercise 5: Matrix Operations ---")
    try:
        result = matrix_operations()
        assert result is not None, "Returned None"
        expected_mm = torch.tensor([[19.0, 22.0], [43.0, 50.0]])
        assert torch.allclose(result['matmul'], expected_mm), f"matmul: {result['matmul']}"
        expected_em = torch.tensor([[5.0, 12.0], [21.0, 32.0]])
        assert torch.allclose(result['element_mul'], expected_em)
        assert result['dot'].item() == 32.0, f"dot: {result['dot']}"
        expected_outer = torch.tensor([[3.0, 4.0, 5.0], [6.0, 8.0, 10.0]])
        assert torch.allclose(result['outer'], expected_outer)
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 6: NumPy Interop ──
    print("\n--- Exercise 6: NumPy Interop ---")
    try:
        result = numpy_interop()
        assert result is not None, "Returned None"
        assert isinstance(result['from_numpy'], torch.Tensor)
        assert isinstance(result['to_numpy'], np.ndarray)
        assert isinstance(result['safe_copy'], torch.Tensor)
        assert len(result['from_numpy']) == 5
        np.testing.assert_array_almost_equal(result['to_numpy'], [10.0, 20.0, 30.0])
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 7: Autograd Basics ──
    print("\n--- Exercise 7: Autograd Basics ---")
    try:
        result = autograd_basics()
        assert result is not None, "Returned None"
        assert abs(result['gradient'] - 34.0) < 1e-4, f"gradient: {result['gradient']}"
        expected_y = 27 + 18 - 15 + 1  # 31
        assert abs(result['y_value'] - 31.0) < 1e-4, f"y_value: {result['y_value']}"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 8: Autograd Vectors ──
    print("\n--- Exercise 8: Autograd Vectors ---")
    try:
        result = autograd_vectors()
        assert result is not None, "Returned None"
        assert result['W_grad_shape'] == (3, 2), f"Shape: {result['W_grad_shape']}"
        # Each column of W.grad should be x = [1, 2, 3]
        expected_col = torch.tensor([1.0, 2.0, 3.0])
        assert torch.allclose(result['W_grad'][:, 0], expected_col)
        assert torch.allclose(result['W_grad'][:, 1], expected_col)
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 9: Linear Regression Module ──
    print("\n--- Exercise 9: LinearRegression ---")
    try:
        model = LinearRegression(5)
        assert model is not None, "Model is None"
        x = torch.randn(10, 5)
        output = model(x)
        assert output.shape == (10, 1), f"Wrong shape: {output.shape}"
        params = list(model.parameters())
        assert len(params) == 2, f"Should have 2 params (W, b), got {len(params)}"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 10: TwoLayerNet ──
    print("\n--- Exercise 10: TwoLayerNet ---")
    try:
        model = TwoLayerNet(10, 32)
        assert model is not None, "Model is None"
        x = torch.randn(8, 10)
        output = model(x)
        assert output.shape == (8, 1), f"Wrong shape: {output.shape}"
        assert torch.all(output >= 0) and torch.all(output <= 1), \
            "Output should be in [0, 1] (sigmoid)"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 11: Sequential Model ──
    print("\n--- Exercise 11: Sequential Model ---")
    try:
        model = build_sequential_model(20, 5)
        assert model is not None, "Model is None"
        assert isinstance(model, nn.Sequential), "Should return nn.Sequential"
        x = torch.randn(8, 20)
        output = model(x)
        assert output.shape == (8, 5), f"Wrong shape: {output.shape}"
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 12: Parameter Counting ──
    print("\n--- Exercise 12: Parameter Counting ---")
    try:
        model = nn.Sequential(
            nn.Linear(10, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        result = count_parameters(model)
        assert result is not None, "Returned None"
        # 10*32 + 32 + 32*1 + 1 = 320 + 32 + 32 + 1 = 385
        assert result['total'] == 385, f"Total: {result['total']}"
        assert result['trainable'] == 385, f"Trainable: {result['trainable']}"
        assert result['non_trainable'] == 0
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 13: Device Management ──
    print("\n--- Exercise 13: Device Management ---")
    try:
        device = get_device()
        assert device is not None, "Returned None"
        assert isinstance(device, torch.device)
        print(f"  Device: {device}")

        model = nn.Linear(5, 1)
        data = torch.randn(3, 5)
        m, d = move_to_device(model, data, torch.device('cpu'))
        assert next(m.parameters()).device.type == 'cpu'
        assert d.device.type == 'cpu'
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 14: Save/Load Model ──
    print("\n--- Exercise 14: Save/Load ---")
    try:
        import tempfile, os
        model = nn.Linear(5, 1)
        with tempfile.NamedTemporaryFile(suffix='.pth', delete=False) as f:
            filepath = f.name
        save_model(model, filepath)
        assert os.path.exists(filepath), "File not saved"

        model2 = nn.Linear(5, 1)
        loaded = load_model(model2, filepath)
        assert loaded is not None, "Returned None"
        assert not loaded.training, "Should be in eval mode"
        # Check weights match
        for p1, p2 in zip(model.parameters(), loaded.parameters()):
            assert torch.equal(p1, p2), "Weights don't match"
        os.unlink(filepath)
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    # ── Exercise 15: Train Linear Regression ──
    print("\n--- Exercise 15: Train Linear Regression ---")
    try:
        torch.manual_seed(42)
        result = train_linear_regression(n_samples=200, n_features=3,
                                          epochs=500, lr=0.05)
        assert result is not None, "Returned None"
        assert 'loss_history' in result, "Missing loss_history"
        assert len(result['loss_history']) == 500, "Should have 500 epochs"
        assert result['final_loss'] < 0.1, f"Loss too high: {result['final_loss']:.4f}"
        print(f"  Final loss: {result['final_loss']:.6f}")
        print(f"  Learned weights: {result['learned_weight'].flatten()}")
        print(f"  Learned bias: {result['learned_bias'].flatten()}")
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

    print("\n" + "=" * 60)
    print("Verification complete!")
    print("=" * 60)
