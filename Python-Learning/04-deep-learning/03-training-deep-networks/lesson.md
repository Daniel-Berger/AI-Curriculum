# Training Deep Networks

## Introduction

Training a neural network is an iterative process that involves computing predictions, measuring error, computing gradients, and updating weights. This chapter covers the core concepts, tools, and techniques that power modern deep learning training.

## 1. Training Loop Anatomy

### The Core Loop

A typical PyTorch training loop follows this pattern:

```python
import torch
import torch.nn as nn
from torch.optim import SGD, Adam

model = nn.Sequential(
    nn.Linear(10, 64),
    nn.ReLU(),
    nn.Linear(64, 2)
)
optimizer = Adam(model.parameters(), lr=0.001)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(num_epochs):
    for batch_x, batch_y in train_loader:
        # Forward pass: compute predictions
        logits = model(batch_x)

        # Compute loss
        loss = loss_fn(logits, batch_y)

        # Backward pass: compute gradients
        loss.backward()

        # Update weights
        optimizer.step()

        # Clear gradients for next iteration
        optimizer.zero_grad()
```

### Step-by-Step Breakdown

**1. Forward Pass:**
- Input data flows through the network
- Each layer applies a transformation
- Output represents model's predictions

```python
logits = model(batch_x)  # Raw outputs from final layer
predictions = logits.argmax(dim=1)  # Class with highest score
```

**2. Loss Computation:**
- Measures the difference between predictions and ground truth
- Guides optimization direction
- Must be differentiable for backpropagation

```python
loss = loss_fn(logits, batch_y)
print(loss.item())  # Extract scalar value
```

**3. Backward Pass (Backpropagation):**
- Computes gradients of loss w.r.t. all parameters
- Uses chain rule through all layers
- Gradients accumulated in `.grad` attributes

```python
loss.backward()  # Populates model.parameters().grad
```

**4. Optimizer Step:**
- Updates parameters using computed gradients
- Different optimizers use different update rules

```python
optimizer.step()  # Updates all parameters
```

**5. Gradient Zeroing:**
- PyTorch accumulates gradients by default
- Must zero before next backward pass

```python
optimizer.zero_grad()  # Clears all .grad attributes
```

## 2. Loss Functions

Loss functions measure how well the model's predictions match the ground truth.

### CrossEntropyLoss

For multi-class classification (combining log softmax + NLL):

```python
loss_fn = nn.CrossEntropyLoss()

# Expects:
# - Input: (batch_size, num_classes) raw logits
# - Target: (batch_size,) class indices

batch_size, num_classes = 32, 10
logits = torch.randn(batch_size, num_classes)
targets = torch.randint(0, num_classes, (batch_size,))

loss = loss_fn(logits, targets)

# Often with ignore_index for padding tokens
loss_fn = nn.CrossEntropyLoss(ignore_index=-100)

# Or with class weights to handle imbalance
class_weights = torch.tensor([1.0, 2.5, 1.8, 0.5])
loss_fn = nn.CrossEntropyLoss(weight=class_weights)
```

### MSELoss

For regression tasks:

```python
loss_fn = nn.MSELoss()

# Expects:
# - Input: (batch_size,) or any shape predictions
# - Target: same shape as input

predictions = torch.randn(32, 1)
targets = torch.randn(32, 1)
loss = loss_fn(predictions, targets)

# Variants
loss_fn = nn.MSELoss(reduction='mean')  # Default
loss_fn = nn.MSELoss(reduction='sum')
loss_fn = nn.MSELoss(reduction='none')  # Per-sample loss
```

### BCEWithLogitsLoss

For multi-label classification (combines sigmoid + BCE):

```python
loss_fn = nn.BCEWithLogitsLoss()

# Expects:
# - Input: (batch_size, num_labels) raw logits
# - Target: (batch_size, num_labels) binary labels [0, 1]

batch_size, num_labels = 32, 5
logits = torch.randn(batch_size, num_labels)
targets = torch.randint(0, 2, (batch_size, num_labels), dtype=torch.float)

loss = loss_fn(logits, targets)

# With pos_weight to handle label imbalance
pos_weights = torch.tensor([1.0, 2.0, 1.5, 3.0, 0.8])
loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weights)
```

### Other Common Loss Functions

```python
# L1Loss (Mean Absolute Error)
loss_fn = nn.L1Loss()

# SmoothL1Loss (Huber loss - robust to outliers)
loss_fn = nn.SmoothL1Loss()

# KLDivergence (for distribution matching)
loss_fn = nn.KLDivLoss()

# NLLLoss (with manually applied LogSoftmax)
loss_fn = nn.NLLLoss()
```

## 3. Optimizers

Optimizers update model parameters based on gradients.

### SGD (Stochastic Gradient Descent)

Basic optimizer with momentum support:

```python
optimizer = torch.optim.SGD(
    model.parameters(),
    lr=0.01,
    momentum=0.9,  # Accelerates convergence
    weight_decay=0.0001  # L2 regularization
)

# Update rule (without momentum):
# param = param - lr * param.grad

# Update rule (with momentum):
# velocity = momentum * velocity + grad
# param = param - lr * velocity
```

### Adam (Adaptive Moment Estimation)

Adaptive learning rates with momentum:

```python
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.001,  # Much smaller than SGD
    betas=(0.9, 0.999),  # Momentum and RMSprop betas
    eps=1e-8,  # Numerical stability
    weight_decay=0.0001  # Default: no L2 regularization
)

# Adapts individual learning rates per parameter
# Maintains exponential moving average of gradients and squared gradients
```

### AdamW (Adam with decoupled weight decay)

Improved version that decouples weight decay:

```python
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.001,
    weight_decay=0.01  # Better weight decay than standard Adam
)

# Recommended for modern deep learning
# Especially effective with learning rate schedulers
```

### Choosing an Optimizer

```python
# Transformers and vision models: AdamW
# CNNs for vision: SGD with momentum
# RNNs: Adam or Adam
# When in doubt: Start with AdamW

optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
```

## 4. Learning Rate Scheduling

Adjusting learning rate during training improves convergence.

### StepLR

Reduce LR by a factor every N epochs:

```python
scheduler = torch.optim.lr_scheduler.StepLR(
    optimizer,
    step_size=30,  # Every 30 epochs
    gamma=0.1  # Multiply by 0.1
)

for epoch in range(num_epochs):
    # Training code
    train_one_epoch()
    scheduler.step()  # Call after each epoch
```

### CosineAnnealingLR

Cosine decay from initial to minimum LR:

```python
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    optimizer,
    T_max=num_epochs,  # Total epochs
    eta_min=1e-5  # Minimum learning rate
)

for epoch in range(num_epochs):
    train_one_epoch()
    scheduler.step()
```

### OneCycleLR

Single cycle from low→high→low LR (excellent for training):

```python
scheduler = torch.optim.lr_scheduler.OneCycleLR(
    optimizer,
    max_lr=0.1,  # Peak learning rate
    total_steps=len(train_loader) * num_epochs,  # Total iterations
    pct_start=0.3  # 30% of training to reach peak
)

for epoch in range(num_epochs):
    for batch_x, batch_y in train_loader:
        # Training step
        logits = model(batch_x)
        loss = loss_fn(logits, batch_y)
        loss.backward()
        optimizer.step()
        scheduler.step()  # Call after each batch!
        optimizer.zero_grad()
```

### ExponentialLR

Exponential decay:

```python
scheduler = torch.optim.lr_scheduler.ExponentialLR(
    optimizer,
    gamma=0.95  # Multiply by 0.95 each epoch
)
```

### ReduceLROnPlateau

Reduce LR when metric stops improving:

```python
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode='min',  # 'min' for loss, 'max' for accuracy
    factor=0.1,  # Multiply LR by 0.1
    patience=5,  # Wait 5 epochs without improvement
    verbose=True
)

for epoch in range(num_epochs):
    train_loss = train_one_epoch()
    val_loss = validate()
    scheduler.step(val_loss)  # Pass metric value
```

## 5. DataLoader and Dataset

Loading data efficiently is crucial for training.

### Custom Dataset

```python
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    """Wraps data arrays into a dataset."""

    def __init__(self, features, labels, transforms=None):
        self.features = features
        self.labels = labels
        self.transforms = transforms

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        x = self.features[idx]
        y = self.labels[idx]

        if self.transforms:
            x = self.transforms(x)

        return x, y

# Create dataset
dataset = CustomDataset(X_train, y_train)

# Create dataloader
train_loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,  # Shuffle for training
    num_workers=4  # Parallel loading
)
```

### Image Dataset with Transforms

```python
from torchvision import transforms
from PIL import Image

class ImageDataset(Dataset):
    def __init__(self, image_paths, labels):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx])
        image = self.transform(image)
        label = self.labels[idx]
        return image, label
```

### DataLoader Features

```python
# Basic usage
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# Iteration
for batch_x, batch_y in loader:
    print(batch_x.shape, batch_y.shape)

# With pin_memory for GPU
loader = DataLoader(
    dataset,
    batch_size=32,
    num_workers=4,
    pin_memory=True  # Faster GPU transfer
)

# Drop last incomplete batch
loader = DataLoader(dataset, batch_size=32, drop_last=True)

# Custom batch sampler
from torch.utils.data import BatchSampler, SequentialSampler
sampler = BatchSampler(SequentialSampler(dataset), 32, drop_last=False)
loader = DataLoader(dataset, batch_sampler=sampler)
```

## 6. TensorBoard Visualization

Monitor training with TensorBoard:

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter(log_dir='./runs/experiment1')

for epoch in range(num_epochs):
    for i, (batch_x, batch_y) in enumerate(train_loader):
        logits = model(batch_x)
        loss = loss_fn(logits, batch_y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        # Log loss every 10 batches
        if i % 10 == 0:
            writer.add_scalar('Loss/train', loss.item(), epoch * len(train_loader) + i)

    # Log learning rate
    writer.add_scalar('Learning_rate', optimizer.param_groups[0]['lr'], epoch)

    # Validate and log
    val_loss = validate()
    writer.add_scalar('Loss/val', val_loss, epoch)

    # Log histograms of weights (expensive!)
    for name, param in model.named_parameters():
        writer.add_histogram(name, param.data, epoch)

writer.close()

# View with: tensorboard --logdir=./runs
```

## 7. Early Stopping

Prevent overfitting by stopping when validation performance stops improving:

```python
class EarlyStopping:
    def __init__(self, patience=3, delta=0):
        self.patience = patience
        self.delta = delta
        self.best_loss = None
        self.counter = 0
        self.best_model_state = None

    def __call__(self, val_loss, model):
        if self.best_loss is None:
            self.best_loss = val_loss
            self.best_model_state = model.state_dict()
        elif val_loss < self.best_loss - self.delta:
            self.best_loss = val_loss
            self.counter = 0
            self.best_model_state = model.state_dict()
        else:
            self.counter += 1
            if self.counter >= self.patience:
                print(f"Early stopping triggered. Best loss: {self.best_loss}")
                return True  # Stop training
        return False

# Usage
early_stop = EarlyStopping(patience=3, delta=1e-4)

for epoch in range(num_epochs):
    train()
    val_loss = validate()

    if early_stop(val_loss, model):
        break

# Restore best weights
model.load_state_dict(early_stop.best_model_state)
```

## 8. Gradient Clipping

Prevent exploding gradients (common in RNNs):

```python
import torch.nn as nn

for epoch in range(num_epochs):
    for batch_x, batch_y in train_loader:
        logits = model(batch_x)
        loss = loss_fn(logits, batch_y)
        loss.backward()

        # Gradient clipping (clip by norm)
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()
        optimizer.zero_grad()

# Or clip by value
nn.utils.clip_grad_value_(model.parameters(), clip_value=0.5)
```

## 9. Mixed Precision Training

Use lower precision to train faster and use less memory:

```python
from torch.cuda.amp import autocast, GradScaler

model = model.cuda()
optimizer = torch.optim.Adam(model.parameters())
scaler = GradScaler()
loss_fn = nn.CrossEntropyLoss()

for epoch in range(num_epochs):
    for batch_x, batch_y in train_loader:
        batch_x, batch_y = batch_x.cuda(), batch_y.cuda()

        # Forward pass with automatic mixed precision
        with autocast():
            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)

        # Backward with scaling
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()
```

## 10. Complete Training Example

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from torch.optim import AdamW
from torch.optim.lr_scheduler import OneCycleLR
import numpy as np

# Setup
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Create synthetic dataset
X_train = torch.randn(1000, 20)
y_train = torch.randint(0, 10, (1000,))
dataset = TensorDataset(X_train, y_train)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# Model
model = nn.Sequential(
    nn.Linear(20, 128),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(64, 10)
).to(device)

# Optimizer and scheduler
optimizer = AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
scheduler = OneCycleLR(optimizer, max_lr=0.1, total_steps=len(loader) * 10)
loss_fn = nn.CrossEntropyLoss()

# Training
model.train()
for epoch in range(10):
    total_loss = 0
    for batch_x, batch_y in loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)

        logits = model(batch_x)
        loss = loss_fn(logits, batch_y)

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/10 - Loss: {total_loss/len(loader):.4f}")

print("Training complete!")
```

## Summary

- **Training Loop**: Forward → Loss → Backward → Step → Zero Grad
- **Loss Functions**: Choose based on task (CrossEntropyLoss for classification, MSELoss for regression)
- **Optimizers**: AdamW is a good default, SGD+momentum for vision models
- **Learning Rate Scheduling**: Use OneCycleLR for single training run
- **Data Loading**: Custom Dataset classes for flexibility
- **Monitoring**: TensorBoard for visualization, early stopping to prevent overfitting
- **Stability**: Gradient clipping and mixed precision for stability
