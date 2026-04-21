"""
Solutions for Training Deep Networks exercises.
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, TensorDataset
from torch.optim.lr_scheduler import StepLR, CosineAnnealingLR, ExponentialLR
from torch.cuda.amp import autocast, GradScaler
from torchvision import transforms
from typing import Tuple, List, Optional, Dict, Any
import numpy as np
import os


# Exercise 1: Build a basic training loop
def basic_training_loop(
    model: nn.Module,
    train_loader: DataLoader,
    num_epochs: int,
    learning_rate: float,
    device: str = 'cpu'
) -> List[float]:
    """
    Implement a basic training loop with forward pass, loss computation,
    backward pass, and weight updates.
    """
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.CrossEntropyLoss()

    losses = []
    model.train()

    for epoch in range(num_epochs):
        epoch_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            # Forward pass
            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)

            # Backward pass
            loss.backward()

            # Update weights
            optimizer.step()
            optimizer.zero_grad()

            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(train_loader)
        losses.append(avg_loss)

    return losses


# Exercise 2: Implement custom Dataset class
class CustomDataset(Dataset):
    """Create a custom PyTorch Dataset that wraps numpy arrays."""

    def __init__(self, features: np.ndarray, labels: np.ndarray):
        """Initialize dataset."""
        self.features = torch.from_numpy(features).float()
        self.labels = torch.from_numpy(labels).long()

    def __len__(self) -> int:
        """Return the number of samples in the dataset."""
        return len(self.features)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Return a single sample as (feature, label) tensors."""
        return self.features[idx], self.labels[idx]


# Exercise 3: Loss function comparison
def compute_losses(
    logits: torch.Tensor,
    targets: torch.Tensor,
    task: str = 'multiclass'
) -> Dict[str, torch.Tensor]:
    """Compute different loss functions for the same predictions/targets."""
    losses = {}

    if task == 'multiclass':
        losses['CrossEntropyLoss'] = nn.CrossEntropyLoss()(logits, targets)

        # MSELoss requires same shape
        if len(logits.shape) > 1:
            one_hot = torch.nn.functional.one_hot(targets, num_classes=logits.shape[1]).float()
            losses['MSELoss'] = nn.MSELoss()(logits, one_hot)

    elif task == 'binary':
        # For binary classification
        losses['BCEWithLogitsLoss'] = nn.BCEWithLogitsLoss()(logits.squeeze(), targets.float())
        losses['CrossEntropyLoss'] = nn.CrossEntropyLoss()(logits, targets)

    elif task == 'regression':
        losses['MSELoss'] = nn.MSELoss()(logits, targets)
        losses['L1Loss'] = nn.L1Loss()(logits, targets)
        losses['SmoothL1Loss'] = nn.SmoothL1Loss()(logits, targets)

    return losses


# Exercise 4: Optimizer comparison
def create_optimizers(
    model: nn.Module,
    learning_rate: float
) -> Dict[str, torch.optim.Optimizer]:
    """Create different optimizer instances for the same model."""
    optimizers = {
        'SGD': torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9),
        'Adam': torch.optim.Adam(model.parameters(), lr=learning_rate),
        'AdamW': torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01),
        'RMSprop': torch.optim.RMSprop(model.parameters(), lr=learning_rate),
    }
    return optimizers


# Exercise 5: Gradient accumulation
def train_with_gradient_accumulation(
    model: nn.Module,
    train_loader: DataLoader,
    num_epochs: int,
    accumulation_steps: int = 4,
    device: str = 'cpu'
) -> List[float]:
    """Train with gradient accumulation to simulate larger batch sizes."""
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()

    losses = []
    model.train()

    for epoch in range(num_epochs):
        epoch_loss = 0.0
        num_batches = 0

        optimizer.zero_grad()

        for i, (batch_x, batch_y) in enumerate(train_loader):
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            # Forward pass
            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)

            # Scale loss by accumulation steps
            scaled_loss = loss / accumulation_steps
            scaled_loss.backward()

            epoch_loss += loss.item()
            num_batches += 1

            # Update weights every accumulation_steps
            if (i + 1) % accumulation_steps == 0:
                optimizer.step()
                optimizer.zero_grad()

        # Final update if not divisible
        if num_batches % accumulation_steps != 0:
            optimizer.step()
            optimizer.zero_grad()

        avg_loss = epoch_loss / num_batches
        losses.append(avg_loss)

    return losses


# Exercise 6: Learning rate scheduling
def train_with_scheduler(
    model: nn.Module,
    train_loader: DataLoader,
    num_epochs: int,
    scheduler_type: str = 'step'
) -> Tuple[List[float], List[float]]:
    """Train with learning rate scheduling."""
    model = model.to('cpu')
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    loss_fn = nn.CrossEntropyLoss()

    if scheduler_type == 'step':
        scheduler = StepLR(optimizer, step_size=2, gamma=0.1)
    elif scheduler_type == 'cosine':
        scheduler = CosineAnnealingLR(optimizer, T_max=num_epochs)
    elif scheduler_type == 'exponential':
        scheduler = ExponentialLR(optimizer, gamma=0.95)
    else:
        raise ValueError(f"Unknown scheduler type: {scheduler_type}")

    losses = []
    lrs = []
    model.train()

    for epoch in range(num_epochs):
        epoch_loss = 0.0

        for batch_x, batch_y in train_loader:
            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            epoch_loss += loss.item()

        scheduler.step()

        losses.append(epoch_loss / len(train_loader))
        lrs.append(optimizer.param_groups[0]['lr'])

    return losses, lrs


# Exercise 7: Gradient clipping
def train_with_gradient_clipping(
    model: nn.Module,
    train_loader: DataLoader,
    num_epochs: int,
    max_grad_norm: float = 1.0,
    device: str = 'cpu'
) -> List[float]:
    """Train with gradient clipping to prevent exploding gradients."""
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()

    losses = []
    model.train()

    for epoch in range(num_epochs):
        epoch_loss = 0.0

        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)

            loss.backward()

            # Clip gradients
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_grad_norm)

            optimizer.step()
            optimizer.zero_grad()

            epoch_loss += loss.item()

        losses.append(epoch_loss / len(train_loader))

    return losses


# Exercise 8: Early stopping implementation
class EarlyStoppingCallback:
    """Implement early stopping to prevent overfitting."""

    def __init__(self, patience: int = 3, delta: float = 0.0):
        """Initialize early stopping."""
        self.patience = patience
        self.delta = delta
        self.best_loss = None
        self.counter = 0
        self.best_model_state = None

    def __call__(self, val_loss: float, model: nn.Module) -> bool:
        """Check if training should stop."""
        if self.best_loss is None:
            self.best_loss = val_loss
            self.best_model_state = model.state_dict()
            return False

        if val_loss < self.best_loss - self.delta:
            self.best_loss = val_loss
            self.counter = 0
            self.best_model_state = model.state_dict()
            return False
        else:
            self.counter += 1
            if self.counter >= self.patience:
                return True  # Stop training

        return False

    def restore_best_weights(self, model: nn.Module) -> None:
        """Restore model to best state seen during training."""
        if self.best_model_state is not None:
            model.load_state_dict(self.best_model_state)


# Exercise 9: Mixed precision training setup
def setup_mixed_precision_training(
    model: nn.Module,
    learning_rate: float
) -> Tuple[nn.Module, torch.optim.Optimizer, Any]:
    """Setup mixed precision training with automatic casting and gradient scaling."""
    model = model.cuda() if torch.cuda.is_available() else model
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    scaler = GradScaler()

    return model, optimizer, scaler


# Exercise 10: Data augmentation with transforms
def create_data_transforms() -> Tuple[Any, Any]:
    """Create image data transforms for training and validation."""
    train_transforms = transforms.Compose([
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    val_transforms = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    return train_transforms, val_transforms


# Exercise 11: Batch normalization and dropout
def create_model_with_regularization(input_size: int, num_classes: int) -> nn.Module:
    """Create a model with batch normalization and dropout for regularization."""
    return nn.Sequential(
        nn.Linear(input_size, 256),
        nn.BatchNorm1d(256),
        nn.ReLU(),
        nn.Dropout(0.3),

        nn.Linear(256, 128),
        nn.BatchNorm1d(128),
        nn.ReLU(),
        nn.Dropout(0.3),

        nn.Linear(128, 64),
        nn.BatchNorm1d(64),
        nn.ReLU(),
        nn.Dropout(0.2),

        nn.Linear(64, num_classes)
    )


# Exercise 12: Training loop with validation
def train_with_validation(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    num_epochs: int,
    device: str = 'cpu'
) -> Tuple[List[float], List[float]]:
    """Complete training loop with validation metrics."""
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()

    train_losses = []
    val_losses = []

    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            train_loss += loss.item()

        train_loss /= len(train_loader)
        train_losses.append(train_loss)

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)

                logits = model(batch_x)
                loss = loss_fn(logits, batch_y)
                val_loss += loss.item()

        val_loss /= len(val_loader)
        val_losses.append(val_loss)

    return train_losses, val_losses


# Exercise 13: Weight decay and L2 regularization
def compare_regularization(
    model: nn.Module,
    train_loader: DataLoader,
    num_epochs: int
) -> Dict[str, List[float]]:
    """Compare training with different weight decay settings."""
    weight_decays = [0.0, 0.0001, 0.001, 0.01]
    results = {}

    for wd in weight_decays:
        model_copy = nn.Sequential(
            nn.Linear(20, 64),
            nn.ReLU(),
            nn.Linear(64, 10)
        )

        optimizer = torch.optim.Adam(model_copy.parameters(), lr=0.001, weight_decay=wd)
        loss_fn = nn.CrossEntropyLoss()

        losses = []
        model_copy.train()

        for epoch in range(num_epochs):
            epoch_loss = 0.0
            for batch_x, batch_y in train_loader:
                logits = model_copy(batch_x)
                loss = loss_fn(logits, batch_y)

                loss.backward()
                optimizer.step()
                optimizer.zero_grad()

                epoch_loss += loss.item()

            losses.append(epoch_loss / len(train_loader))

        results[f'weight_decay_{wd}'] = losses

    return results


# Exercise 14: Learning rate finder
def find_optimal_learning_rate(
    model: nn.Module,
    train_loader: DataLoader,
    start_lr: float = 1e-4,
    end_lr: float = 10.0,
    num_iterations: int = 100
) -> Tuple[List[float], List[float]]:
    """Use learning rate finder to find optimal learning rate."""
    model.train()
    optimizer = torch.optim.SGD(model.parameters(), lr=start_lr)
    loss_fn = nn.CrossEntropyLoss()

    lrs = []
    losses = []

    # Compute learning rate multiplier
    lr_multiplier = (end_lr / start_lr) ** (1 / num_iterations)

    iteration = 0
    best_loss = float('inf')

    for batch_x, batch_y in train_loader:
        if iteration >= num_iterations:
            break

        logits = model(batch_x)
        loss = loss_fn(logits, batch_y)

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        # Update learning rate
        current_lr = start_lr * (lr_multiplier ** iteration)
        for param_group in optimizer.param_groups:
            param_group['lr'] = current_lr

        lrs.append(current_lr)
        losses.append(loss.item())

        # Stop if loss is too high
        if loss.item() > 4 * best_loss:
            break

        best_loss = min(best_loss, loss.item())
        iteration += 1

    return lrs, losses


# Exercise 15: Checkpointing and resuming training
def save_and_resume_training(
    model: nn.Module,
    train_loader: DataLoader,
    checkpoint_path: str,
    num_epochs: int = 10,
    resume_from_checkpoint: bool = False
) -> Dict[str, Any]:
    """Implement training with checkpointing to save and resume progress."""
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()

    start_epoch = 0
    all_losses = []

    # Resume from checkpoint if exists
    if resume_from_checkpoint and os.path.exists(checkpoint_path):
        checkpoint = torch.load(checkpoint_path)
        model.load_state_dict(checkpoint['model_state'])
        optimizer.load_state_dict(checkpoint['optimizer_state'])
        start_epoch = checkpoint['epoch']
        all_losses = checkpoint['losses']

    model.train()

    for epoch in range(start_epoch, num_epochs):
        epoch_loss = 0.0

        for batch_x, batch_y in train_loader:
            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            epoch_loss += loss.item()

        epoch_loss /= len(train_loader)
        all_losses.append(epoch_loss)

        # Save checkpoint
        checkpoint = {
            'epoch': epoch + 1,
            'model_state': model.state_dict(),
            'optimizer_state': optimizer.state_dict(),
            'losses': all_losses
        }
        torch.save(checkpoint, checkpoint_path)

    return {
        'losses': all_losses,
        'final_epoch': num_epochs,
        'checkpoint_path': checkpoint_path
    }


# Helper functions
def create_synthetic_classification_data(
    n_samples: int = 1000,
    input_size: int = 20,
    num_classes: int = 10
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Create synthetic classification dataset."""
    X = torch.randn(n_samples, input_size)
    y = torch.randint(0, num_classes, (n_samples,))
    return X, y


def create_synthetic_regression_data(
    n_samples: int = 1000,
    input_size: int = 20
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Create synthetic regression dataset."""
    X = torch.randn(n_samples, input_size)
    y = torch.randn(n_samples)
    return X, y


def create_simple_model(input_size: int = 20, num_classes: int = 10) -> nn.Module:
    """Create a simple fully connected model for testing."""
    return nn.Sequential(
        nn.Linear(input_size, 64),
        nn.ReLU(),
        nn.Linear(64, 32),
        nn.ReLU(),
        nn.Linear(32, num_classes)
    )
