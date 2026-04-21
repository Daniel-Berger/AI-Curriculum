# Module 02: PyTorch Fundamentals

## Overview

In Module 01, you built a neural network from scratch with NumPy. Now you will learn
**PyTorch**, the framework that automates everything you did manually — forward pass,
backpropagation, gradient descent — while giving you fine-grained control when you need it.

PyTorch is to NumPy neural networks what SwiftUI is to manually drawing UIKit views:
the same underlying operations, but with a declarative, composable API and automatic
differentiation.

---

## 1. Why PyTorch?

### Dynamic Computation Graphs

PyTorch builds its computation graph **on the fly** during execution (eager mode). This
means you can use standard Python control flow (if/else, loops) in your models. Compare:

```
TensorFlow 1.x (static graph):  Define graph → compile → run
PyTorch (dynamic graph):         Define and run simultaneously

This is like the difference between:
  Interface Builder (define first, run later)  ← static
  SwiftUI (declarative but evaluated eagerly)  ← dynamic
```

### Pythonic Design

PyTorch feels like Python. Models are Python classes. Training loops are Python for-loops.
Debugging uses standard Python tools (print, pdb, breakpoints).

### Core Strengths

- **Automatic differentiation** (autograd) — replaces your manual backprop
- **GPU acceleration** — seamless CPU/GPU/MPS switching
- **Rich ecosystem** — torchvision, torchaudio, torchtext, HuggingFace
- **Production path** — TorchScript, ONNX, and (relevant for you) CoreML export

---

## 2. Tensors

Tensors are PyTorch's fundamental data structure — multi-dimensional arrays, like NumPy's
`ndarray` but with GPU support and automatic differentiation.

### 2.1 Creating Tensors

```python
import torch

# ── From Python data ──────────────────────────────────────────────
t1 = torch.tensor([1, 2, 3])                    # 1D tensor (vector)
t2 = torch.tensor([[1, 2], [3, 4]])              # 2D tensor (matrix)
t3 = torch.tensor([[[1, 2], [3, 4]]])            # 3D tensor

# ── Common constructors ──────────────────────────────────────────
zeros = torch.zeros(3, 4)           # 3x4 matrix of zeros
ones = torch.ones(2, 3)             # 2x3 matrix of ones
rand = torch.rand(3, 4)             # Uniform [0, 1)
randn = torch.randn(3, 4)          # Normal(0, 1)
arange = torch.arange(0, 10, 2)    # [0, 2, 4, 6, 8]
linspace = torch.linspace(0, 1, 5) # [0.0, 0.25, 0.5, 0.75, 1.0]
eye = torch.eye(3)                  # 3x3 identity matrix
empty = torch.empty(2, 3)           # Uninitialized (fast, use carefully)

# ── Like-constructors (match shape/dtype/device of existing tensor) ──
x = torch.randn(3, 4)
zeros_like = torch.zeros_like(x)    # Same shape, dtype, device
ones_like = torch.ones_like(x)
rand_like = torch.rand_like(x)

# ── From a specific range of values ──
full = torch.full((2, 3), fill_value=7.0)  # 2x3 matrix, all 7.0
```

### 2.2 Data Types (dtypes)

```python
# Default float is float32 (unlike NumPy's float64)
t = torch.tensor([1.0, 2.0])
print(t.dtype)  # torch.float32

# Specify dtype
t_int = torch.tensor([1, 2, 3], dtype=torch.int64)
t_float64 = torch.tensor([1.0, 2.0], dtype=torch.float64)
t_bool = torch.tensor([True, False])

# Cast between types
t_float = t_int.float()     # int64 → float32
t_long = t_float.long()     # float32 → int64
t_half = t_float.half()     # float32 → float16

# Common dtypes:
# torch.float32 (torch.float)  — default for weights and data
# torch.float64 (torch.double) — rarely needed
# torch.float16 (torch.half)   — mixed precision training
# torch.int64 (torch.long)     — default for indices and labels
# torch.bool                   — masks and conditions
```

### 2.3 Device Management

```python
# Check available devices
print(torch.cuda.is_available())       # NVIDIA GPU
print(torch.backends.mps.is_available())  # Apple Silicon GPU

# Create on specific device
device = torch.device('mps' if torch.backends.mps.is_available()
                      else 'cuda' if torch.cuda.is_available()
                      else 'cpu')
print(f"Using device: {device}")

t_cpu = torch.randn(3, 4)                # CPU by default
t_device = torch.randn(3, 4, device=device)  # On target device

# Move between devices
t_gpu = t_cpu.to(device)          # CPU → GPU/MPS
t_back = t_gpu.to('cpu')         # GPU/MPS → CPU
t_gpu2 = t_cpu.to(device)       # Equivalent

# IMPORTANT: Tensors on different devices cannot interact
# t_cpu + t_gpu  ← This will ERROR
# Always ensure tensors are on the same device before operations

# Check tensor device
print(t_cpu.device)   # cpu
print(t_gpu.device)   # mps:0 or cuda:0
```

**iOS Developer Note**: The MPS (Metal Performance Shaders) backend uses Apple's Metal
framework — the same GPU acceleration you have used in iOS apps. PyTorch on Apple Silicon
uses the same hardware path as Core ML inference.

---

## 3. Tensor Operations

### 3.1 Arithmetic

```python
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([4.0, 5.0, 6.0])

# Element-wise operations
c = a + b            # tensor([5., 7., 9.])
c = a * b            # tensor([4., 10., 18.])
c = a / b            # tensor([0.25, 0.4, 0.5])
c = a ** 2           # tensor([1., 4., 9.])

# Equivalent method calls
c = torch.add(a, b)
c = torch.mul(a, b)

# In-place operations (modify tensor directly, end with _)
a.add_(1)            # a is now [2., 3., 4.]
a.mul_(2)            # a is now [4., 6., 8.]
# CAUTION: In-place ops can break autograd — avoid in training code
```

### 3.2 Matrix Operations

```python
A = torch.randn(3, 4)
B = torch.randn(4, 5)

# Matrix multiplication (3 equivalent ways)
C = A @ B                    # Preferred syntax
C = torch.matmul(A, B)      # Function form
C = torch.mm(A, B)          # Only for 2D matrices

# Batch matrix multiplication
batch_A = torch.randn(8, 3, 4)   # 8 matrices, each 3x4
batch_B = torch.randn(8, 4, 5)   # 8 matrices, each 4x5
batch_C = torch.bmm(batch_A, batch_B)  # 8 matrices, each 3x5

# Dot product
v1 = torch.tensor([1.0, 2.0, 3.0])
v2 = torch.tensor([4.0, 5.0, 6.0])
dot = torch.dot(v1, v2)     # 32.0

# Transpose
At = A.T               # Shorthand
At = A.t()             # Method
At = A.transpose(0, 1) # Explicit dims
```

### 3.3 Indexing and Slicing

```python
t = torch.arange(12).reshape(3, 4)
# tensor([[ 0,  1,  2,  3],
#          [ 4,  5,  6,  7],
#          [ 8,  9, 10, 11]])

# Basic indexing (same as NumPy)
t[0]         # First row: tensor([0, 1, 2, 3])
t[0, 2]      # Element at row 0, col 2: tensor(2)
t[:, 1]      # All rows, column 1: tensor([1, 5, 9])
t[1:, :2]    # Rows 1+, columns 0-1

# Boolean indexing
mask = t > 5
t[mask]      # tensor([6, 7, 8, 9, 10, 11])

# Fancy indexing
indices = torch.tensor([0, 2])
t[indices]   # Rows 0 and 2

# Gather — useful for selecting specific elements per row
# (common for selecting action values in reinforcement learning)
idx = torch.tensor([[1], [3], [2]])  # column to pick per row
selected = torch.gather(t, dim=1, index=idx)
# tensor([[1], [7], [10]])
```

### 3.4 Reshaping

```python
t = torch.arange(12)

# Reshape (returns view when possible)
t2d = t.reshape(3, 4)      # 3x4 matrix
t3d = t.reshape(2, 2, 3)   # 2x2x3 tensor

# View (always returns view, fails if not contiguous)
t2d = t.view(3, 4)

# -1 means "infer this dimension"
t2d = t.reshape(-1, 4)     # (3, 4) — inferred 12/4 = 3
t2d = t.reshape(3, -1)     # (3, 4) — inferred 12/3 = 4

# Squeeze and unsqueeze
t = torch.randn(1, 3, 1, 4)
t.squeeze()        # Remove all size-1 dims → shape (3, 4)
t.squeeze(0)       # Remove dim 0 if size 1 → shape (3, 1, 4)

t = torch.randn(3, 4)
t.unsqueeze(0)     # Add dim at position 0 → shape (1, 3, 4)
t.unsqueeze(-1)    # Add dim at last position → shape (3, 4, 1)

# Flatten
t = torch.randn(2, 3, 4)
t.flatten()          # shape (24,) — all dims
t.flatten(1)         # shape (2, 12) — flatten from dim 1 onward

# Permute (reorder dimensions)
t = torch.randn(2, 3, 4)  # (batch, height, width)
t.permute(0, 2, 1)        # (batch, width, height) → shape (2, 4, 3)
```

### 3.5 Broadcasting

Broadcasting follows the same rules as NumPy:

```python
# Rule: Dimensions are compared from right to left.
# Two dimensions are compatible when:
#   1. They are equal, OR
#   2. One of them is 1

A = torch.randn(3, 4)    # (3, 4)
b = torch.randn(1, 4)    # (1, 4) — broadcasts across rows
c = A + b                 # (3, 4) — b repeated 3 times

v = torch.randn(3, 1)    # (3, 1) — broadcasts across columns
d = A + v                 # (3, 4) — v repeated 4 times

# Common pattern: adding bias to batch
batch = torch.randn(32, 10)   # 32 samples, 10 features
bias = torch.randn(10)        # broadcast to (32, 10)
result = batch + bias
```

### 3.6 Reduction Operations

```python
t = torch.tensor([[1.0, 2.0, 3.0],
                   [4.0, 5.0, 6.0]])

t.sum()              # 21.0 — sum all elements
t.sum(dim=0)         # tensor([5., 7., 9.]) — sum across rows
t.sum(dim=1)         # tensor([6., 15.]) — sum across columns

t.mean()             # 3.5
t.mean(dim=0)        # tensor([2.5, 3.5, 4.5])

t.max()              # tensor(6.)
t.max(dim=1)         # values=tensor([3., 6.]), indices=tensor([2, 2])
t.argmax(dim=1)      # tensor([2, 2]) — indices of max per row

t.min(), t.std(), t.var()  # other reductions
```

---

## 4. NumPy Interoperability

PyTorch and NumPy share memory when on CPU — changes to one affect the other.

```python
import numpy as np
import torch

# ── NumPy → Tensor ──
np_array = np.array([1.0, 2.0, 3.0])
tensor = torch.from_numpy(np_array)     # Shares memory!
np_array[0] = 999
print(tensor)  # tensor([999., 2., 3.]) — tensor changed too!

# Safe copy (no memory sharing)
tensor = torch.tensor(np_array)         # Creates a copy

# ── Tensor → NumPy ──
tensor = torch.randn(3, 4)
np_array = tensor.numpy()               # Shares memory (CPU only)

# If tensor requires grad or is on GPU, need extra steps:
tensor_grad = torch.randn(3, 4, requires_grad=True)
np_array = tensor_grad.detach().numpy()  # detach from computation graph

tensor_gpu = torch.randn(3, 4, device='mps')
np_array = tensor_gpu.cpu().numpy()      # move to CPU first
```

---

## 5. Autograd: Automatic Differentiation

Autograd is PyTorch's automatic differentiation engine. It replaces the manual
backpropagation you implemented in Module 01.

### 5.1 Basic Autograd

```python
# requires_grad=True tells PyTorch to track operations for differentiation
x = torch.tensor([2.0, 3.0], requires_grad=True)

# Forward: PyTorch records operations in a computation graph
y = x ** 2 + 3 * x + 1  # y = x^2 + 3x + 1

# Compute sum to get scalar (backward needs scalar output)
loss = y.sum()

# Backward: compute dy/dx for all tensors with requires_grad=True
loss.backward()

# Access gradients
print(x.grad)  # tensor([7., 9.])
# dy/dx = 2x + 3
# At x=2: 2(2) + 3 = 7
# At x=3: 2(3) + 3 = 9
```

### 5.2 Gradient Accumulation and Zeroing

```python
# IMPORTANT: Gradients ACCUMULATE by default!
x = torch.tensor([1.0], requires_grad=True)

for i in range(3):
    y = x * 2
    y.backward()
    print(f"Step {i}: grad = {x.grad}")
    # Step 0: grad = tensor([2.])
    # Step 1: grad = tensor([4.])  ← accumulated!
    # Step 2: grad = tensor([6.])  ← accumulated!

# You MUST zero gradients before each backward pass in training
x.grad.zero_()  # or optimizer.zero_grad() in training loops
```

### 5.3 Disabling Gradient Tracking

```python
x = torch.randn(3, requires_grad=True)

# Method 1: torch.no_grad() context manager
# Use during evaluation/inference for speed and memory savings
with torch.no_grad():
    y = x * 2
    print(y.requires_grad)  # False

# Method 2: .detach() — returns new tensor detached from graph
y = x.detach()
print(y.requires_grad)  # False

# Method 3: Decorating functions
@torch.no_grad()
def inference(model, x):
    return model(x)
```

### 5.4 Gradient Computation for Neural Networks

```python
# Manual linear regression with autograd
# (Compare this to what you did manually in Module 01!)

X = torch.randn(100, 1)
y_true = 3 * X + 2 + torch.randn(100, 1) * 0.1

# Parameters (requires_grad=True because we want to learn these)
w = torch.randn(1, requires_grad=True)
b = torch.zeros(1, requires_grad=True)

learning_rate = 0.1

for epoch in range(100):
    # Forward pass — autograd records this
    y_pred = X * w + b
    loss = ((y_pred - y_true) ** 2).mean()

    # Backward pass — autograd computes all gradients
    loss.backward()

    # Update parameters (disable grad tracking for the update step)
    with torch.no_grad():
        w -= learning_rate * w.grad
        b -= learning_rate * b.grad

    # Zero gradients for next iteration
    w.grad.zero_()
    b.grad.zero_()

print(f"Learned: w={w.item():.2f}, b={b.item():.2f}")
# Should be close to w=3, b=2
```

---

## 6. nn.Module: Building Models

`nn.Module` is PyTorch's base class for all neural network modules. Think of it like
a `UIViewController` or `View` protocol — the standard building block you subclass to
create your models.

### 6.1 Defining a Model

```python
import torch.nn as nn

class SimpleClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        # Define layers — these are registered as parameters
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        """Define the forward pass. Called when you do model(x)."""
        x = self.fc1(x)      # Linear: x @ W1 + b1
        x = self.relu(x)     # Activation
        x = self.fc2(x)      # Linear: x @ W2 + b2
        x = self.sigmoid(x)  # Output activation
        return x

# Create model
model = SimpleClassifier(input_dim=10, hidden_dim=32, output_dim=1)

# Use model (calls forward() automatically)
x = torch.randn(5, 10)  # 5 samples, 10 features
output = model(x)        # shape: (5, 1)
print(output.shape)

# Inspect parameters
for name, param in model.named_parameters():
    print(f"{name}: shape={param.shape}, requires_grad={param.requires_grad}")
# fc1.weight: shape=torch.Size([32, 10]), requires_grad=True
# fc1.bias: shape=torch.Size([32]), requires_grad=True
# fc2.weight: shape=torch.Size([1, 32]), requires_grad=True
# fc2.bias: shape=torch.Size([1]), requires_grad=True

# Count parameters
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params}")
```

### 6.2 nn.Sequential

For simple feed-forward models, use `nn.Sequential` — no subclassing needed:

```python
model = nn.Sequential(
    nn.Linear(10, 64),
    nn.ReLU(),
    nn.Linear(64, 32),
    nn.ReLU(),
    nn.Linear(32, 1),
    nn.Sigmoid()
)

output = model(torch.randn(5, 10))
print(output.shape)  # (5, 1)

# Named version for readability
model = nn.Sequential(
    ('hidden1', nn.Linear(10, 64)),
    ('relu1', nn.ReLU()),
    ('hidden2', nn.Linear(64, 32)),
    ('relu2', nn.ReLU()),
    ('output', nn.Linear(32, 1)),
    ('sigmoid', nn.Sigmoid())
)
# Access: model.hidden1, model.relu1, etc.
```

---

## 7. Common Layers

### 7.1 nn.Linear

Fully-connected layer. Replaces your manual `Z = X @ W + b`.

```python
# nn.Linear(in_features, out_features, bias=True)
fc = nn.Linear(784, 128)
print(fc.weight.shape)  # (128, 784) — NOTE: transposed from our convention
print(fc.bias.shape)    # (128,)

x = torch.randn(32, 784)
output = fc(x)          # (32, 128)
```

### 7.2 nn.Conv2d

2D convolution for image data. We will cover this in depth in Module 04.

```python
# nn.Conv2d(in_channels, out_channels, kernel_size, stride=1, padding=0)
conv = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)
# Input: (batch, channels, height, width)
x = torch.randn(8, 3, 32, 32)   # 8 RGB images, 32x32
output = conv(x)                  # (8, 16, 32, 32) — 16 feature maps
```

### 7.3 nn.BatchNorm1d / nn.BatchNorm2d

Normalizes activations to stabilize and accelerate training:

```python
# For fully-connected layers
bn1d = nn.BatchNorm1d(128)
x = torch.randn(32, 128)
output = bn1d(x)  # normalized, shape (32, 128)

# For conv layers
bn2d = nn.BatchNorm2d(16)  # 16 channels
x = torch.randn(8, 16, 32, 32)
output = bn2d(x)  # normalized per channel
```

### 7.4 nn.Dropout

Randomly zeros elements during training for regularization:

```python
dropout = nn.Dropout(p=0.5)  # 50% dropout

# During training
model.train()
x = torch.ones(1, 10)
output = dropout(x)  # ~half the values are 0, rest scaled by 2

# During evaluation — dropout is disabled
model.eval()
output = dropout(x)  # all values pass through unchanged
```

### 7.5 Activation Layers

```python
relu = nn.ReLU()
leaky_relu = nn.LeakyReLU(negative_slope=0.01)
sigmoid = nn.Sigmoid()
tanh = nn.Tanh()
softmax = nn.Softmax(dim=1)   # specify dimension

# Functional API alternative (used in forward())
import torch.nn.functional as F
x = torch.randn(3, 4)
F.relu(x)
F.sigmoid(x)
F.softmax(x, dim=1)
```

---

## 8. Building a Complete Model

Here is a complete example tying everything together — a multi-layer classifier:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class MLPClassifier(nn.Module):
    """Multi-layer perceptron for classification.

    Think of this as the PyTorch equivalent of the NeuralNetwork class
    you built in Module 01 — but with autograd handling backprop.
    """

    def __init__(self, input_dim: int, hidden_dims: list, num_classes: int,
                 dropout_rate: float = 0.3):
        super().__init__()

        # Build layers dynamically
        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
            ])
            prev_dim = hidden_dim

        # Output layer — no activation (handled by loss function)
        layers.append(nn.Linear(prev_dim, num_classes))

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


# ── Create and test the model ──
model = MLPClassifier(
    input_dim=784,
    hidden_dims=[256, 128, 64],
    num_classes=10,
    dropout_rate=0.3
)

# Test forward pass
x = torch.randn(32, 784)
logits = model(x)
print(f"Output shape: {logits.shape}")  # (32, 10)

# Get probabilities
probs = F.softmax(logits, dim=1)
predictions = torch.argmax(probs, dim=1)
print(f"Predictions: {predictions.shape}")  # (32,)

# Model summary
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters: {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")
```

---

## 9. Saving and Loading Models

### 9.1 Saving/Loading State Dict (Recommended)

```python
# Save only the learned parameters (not the model code)
torch.save(model.state_dict(), 'model_weights.pth')

# Load parameters into a model instance
model = MLPClassifier(784, [256, 128, 64], 10)
model.load_state_dict(torch.load('model_weights.pth'))
model.eval()  # Set to evaluation mode
```

### 9.2 Saving/Loading Entire Model

```python
# Save everything (model + weights) — uses pickle
torch.save(model, 'full_model.pth')

# Load — requires the class definition to be available
model = torch.load('full_model.pth')
model.eval()

# WARNING: This uses pickle, which is fragile across code changes.
# state_dict is more portable and recommended.
```

### 9.3 Checkpoint for Resuming Training

```python
# Save checkpoint with optimizer state
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}
torch.save(checkpoint, 'checkpoint.pth')

# Resume training
checkpoint = torch.load('checkpoint.pth')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
start_epoch = checkpoint['epoch'] + 1
```

---

## 10. Device Management Patterns

### 10.1 Device-Agnostic Code

```python
# At the top of your script
device = torch.device(
    'mps' if torch.backends.mps.is_available()
    else 'cuda' if torch.cuda.is_available()
    else 'cpu'
)
print(f"Using: {device}")

# Move model to device
model = MLPClassifier(784, [256, 128, 64], 10).to(device)

# Move data to device in training loop
for X_batch, y_batch in dataloader:
    X_batch = X_batch.to(device)
    y_batch = y_batch.to(device)
    output = model(X_batch)
    # ...
```

### 10.2 Apple Silicon (MPS) Notes

```python
# MPS is Apple's Metal Performance Shaders backend
# It uses the same GPU hardware as CoreML inference on iOS/macOS

if torch.backends.mps.is_available():
    device = torch.device('mps')
    x = torch.randn(3, 4, device=device)
    print(x.device)  # mps:0

    # Some operations may not be supported on MPS yet
    # In that case, fall back to CPU:
    try:
        result = some_operation(x)
    except RuntimeError:
        result = some_operation(x.cpu()).to(device)
```

---

## 11. CoreML Comparison for iOS Developers

Here is how PyTorch concepts map to what you already know from iOS:

```
PyTorch                          iOS / CoreML
──────────────                   ──────────────
torch.Tensor                  →  MLMultiArray
model = MyNet()               →  let model = try MyModel(configuration: ...)
model(input)                  →  model.prediction(from: input)
model.to(device)              →  MLModelConfiguration().computeUnits = .all
model.eval()                  →  (always inference mode in CoreML)
torch.save(state_dict)        →  .mlmodel / .mlpackage file
model.train() / model.eval()  →  CoreML is always eval (inference only)
torch.no_grad()               →  (CoreML does not compute gradients)
DataLoader(batch_size=32)     →  VNImageRequestHandler (single image)

Key difference: CoreML is inference-only. PyTorch handles both
training AND inference.

Export path:
  PyTorch model → coremltools.convert() → .mlmodel → Xcode project
```

### Converting PyTorch to CoreML

```python
import coremltools as ct

# Trace the model (captures computation graph)
example_input = torch.randn(1, 784)
traced_model = torch.jit.trace(model.cpu().eval(), example_input)

# Convert to CoreML
mlmodel = ct.convert(
    traced_model,
    inputs=[ct.TensorType(name="input", shape=(1, 784))],
    outputs=[ct.TensorType(name="output")],
)

# Save for Xcode
mlmodel.save("MyClassifier.mlpackage")
```

---

## 12. Key Differences from NumPy

```
Feature                NumPy              PyTorch
──────────────         ──────────         ──────────
Default float          float64            float32
GPU support            No                 Yes (CUDA, MPS)
Auto-diff              No                 Yes (autograd)
In-place suffix        N/A                _ (e.g., add_)
Random                 np.random.randn    torch.randn
Axis keyword           axis=              dim=
Reshape                .reshape()         .reshape() or .view()
Concatenate            np.concatenate     torch.cat
Stack                  np.stack           torch.stack
Where                  np.where           torch.where
```

---

## 13. Key Takeaways

1. **Tensors** are GPU-enabled, autograd-tracking ndarrays
2. **Autograd** automatically computes gradients — no manual backprop
3. **nn.Module** is the base class for all models — subclass it and define `forward()`
4. **nn.Sequential** works for simple architectures without branching
5. **Device management** — always write device-agnostic code
6. **State dict** is the recommended way to save/load models
7. **MPS backend** gives you GPU acceleration on Apple Silicon
8. PyTorch models can be exported to **CoreML** for iOS deployment

---

## Next Steps

In Module 03, you will learn the complete training workflow:
- Training loops with loss functions and optimizers
- Learning rate scheduling
- DataLoader and custom datasets
- Debugging and monitoring training
