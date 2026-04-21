"""
Solutions for CNNs and Transfer Learning exercises.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, TensorDataset
from torchvision import models, transforms
from typing import Tuple, List, Dict, Optional, Any
import numpy as np


# Exercise 1: Implement basic convolution layer properties
def compute_conv_output_size(
    input_size: int,
    kernel_size: int,
    stride: int = 1,
    padding: int = 0
) -> int:
    """Calculate the output size of a convolution operation."""
    output_size = (input_size + 2 * padding - kernel_size) // stride + 1
    return output_size


# Exercise 2: Build a simple CNN
class SimpleCNN(nn.Module):
    """Create a simple CNN with 3 convolutional blocks."""

    def __init__(self, num_classes: int = 10):
        """Initialize SimpleCNN."""
        super().__init__()

        # Block 1: Conv -> ReLU -> Pool
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Block 2: Conv -> ReLU -> Pool
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)

        # Block 3: Conv -> ReLU -> Pool
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        # Fully connected layers
        # After 3 pooling operations: 32x32 -> 16x16 -> 8x8 -> 4x4
        self.fc1 = nn.Linear(128 * 4 * 4, 256)
        self.fc2 = nn.Linear(256, num_classes)

        self.dropout = nn.Dropout(0.5)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        # Block 1
        x = F.relu(self.conv1(x))  # (batch, 32, 32, 32)
        x = self.pool(x)            # (batch, 32, 16, 16)

        # Block 2
        x = F.relu(self.conv2(x))  # (batch, 64, 16, 16)
        x = self.pool(x)            # (batch, 64, 8, 8)

        # Block 3
        x = F.relu(self.conv3(x))  # (batch, 128, 8, 8)
        x = self.pool(x)            # (batch, 128, 4, 4)

        # Flatten and fully connected
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)

        return x


# Exercise 3: Implement residual block
class ResidualBlock(nn.Module):
    """Create a residual block with skip connections."""

    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        """Initialize residual block."""
        super().__init__()

        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)

        # Shortcut
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with skip connection."""
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        out = out + self.shortcut(residual)
        out = self.relu(out)

        return out


# Exercise 4: Transfer learning - feature extraction
def transfer_learning_feature_extraction(
    model: nn.Module,
    train_loader: DataLoader,
    num_epochs: int,
    device: str = 'cpu'
) -> List[float]:
    """Train a pre-trained model using feature extraction (frozen backbone)."""
    model = model.to(device)

    # Freeze all parameters
    for param in model.parameters():
        param.requires_grad = False

    # Only unfreeze final layer
    if hasattr(model, 'fc'):
        for param in model.fc.parameters():
            param.requires_grad = True
    elif hasattr(model, 'classifier'):
        for param in model.classifier.parameters():
            param.requires_grad = True

    # Optimizer only for final layer
    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=1e-3
    )

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
            optimizer.step()
            optimizer.zero_grad()

            epoch_loss += loss.item()

        losses.append(epoch_loss / len(train_loader))

    return losses


# Exercise 5: Transfer learning - fine-tuning
def transfer_learning_fine_tuning(
    model: nn.Module,
    train_loader: DataLoader,
    num_epochs: int,
    backbone_lr: float = 1e-5,
    head_lr: float = 1e-3,
    device: str = 'cpu'
) -> List[float]:
    """Fine-tune a pre-trained model with different learning rates."""
    model = model.to(device)

    # Get backbone and head parameters
    backbone_params = []
    head_params = []

    if hasattr(model, 'fc'):
        head_params = list(model.fc.parameters())
        backbone_params = [p for p in model.parameters() if p not in head_params]
    elif hasattr(model, 'classifier'):
        head_params = list(model.classifier.parameters())
        backbone_params = [p for p in model.parameters() if p not in head_params]

    # Different learning rates for backbone and head
    optimizer = torch.optim.AdamW([
        {'params': backbone_params, 'lr': backbone_lr},
        {'params': head_params, 'lr': head_lr}
    ])

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
            optimizer.step()
            optimizer.zero_grad()

            epoch_loss += loss.item()

        losses.append(epoch_loss / len(train_loader))

    return losses


# Exercise 6: Load pretrained model and adapt
def load_and_adapt_pretrained_model(
    model_name: str,
    num_classes: int,
    pretrained: bool = True
) -> nn.Module:
    """Load a pretrained model and adapt it for a new task."""
    if model_name == 'resnet18':
        model = models.resnet18(pretrained=pretrained)
    elif model_name == 'resnet50':
        model = models.resnet50(pretrained=pretrained)
    elif model_name == 'vgg16':
        model = models.vgg16(pretrained=pretrained)
    elif model_name == 'mobilenet_v2':
        model = models.mobilenet_v2(pretrained=pretrained)
    elif model_name == 'efficientnet_b0':
        model = models.efficientnet_b0(pretrained=pretrained)
    else:
        raise ValueError(f"Unknown model: {model_name}")

    # Adapt final layer for new task
    if hasattr(model, 'fc'):
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, num_classes)
    elif hasattr(model, 'classifier'):
        if isinstance(model.classifier, nn.Sequential):
            num_features = model.classifier[-1].in_features
            model.classifier[-1] = nn.Linear(num_features, num_classes)
        else:
            num_features = model.classifier.in_features
            model.classifier = nn.Linear(num_features, num_classes)

    return model


# Exercise 7: Data augmentation transforms
def create_augmentation_transforms() -> Tuple[Any, Any]:
    """Create training and validation image transforms."""
    train_transforms = transforms.Compose([
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
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


# Exercise 8: Custom CNN with batch normalization
class CNNWithBatchNorm(nn.Module):
    """Build CNN with batch normalization for stable training."""

    def __init__(self, num_classes: int = 10):
        """Initialize CNN with batch normalization."""
        super().__init__()

        # Block 1
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)

        # Block 2
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)

        # Block 3
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Fully connected
        self.fc1 = nn.Linear(128 * 4 * 4, 256)
        self.fc2 = nn.Linear(256, num_classes)

        self.dropout = nn.Dropout(0.5)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        # Block 1
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool(x)

        # Block 2
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool(x)

        # Block 3
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.pool(x)

        # Fully connected
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)

        return x


# Exercise 9: Implement conv output calculation
def calculate_receptive_field(
    layer_configs: List[Dict[str, int]]
) -> int:
    """Calculate receptive field size given a sequence of layers."""
    receptive_field = 1
    cumulative_stride = 1

    for config in layer_configs:
        kernel_size = config.get('kernel_size', 3)
        stride = config.get('stride', 1)
        padding = config.get('padding', 0)

        # RF = RF + (kernel_size - 1) * cumulative_stride
        receptive_field += (kernel_size - 1) * cumulative_stride
        cumulative_stride *= stride

    return receptive_field


# Exercise 10: Multi-scale feature extraction
class MultiScaleCNN(nn.Module):
    """Build CNN that extracts features at multiple scales."""

    def __init__(self, num_classes: int = 10):
        """Initialize multi-scale CNN."""
        super().__init__()

        # Main path
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))

        # Multi-scale pathways
        self.scale2_pool = nn.MaxPool2d(kernel_size=4, stride=4)
        self.scale3_pool = nn.MaxPool2d(kernel_size=8, stride=8)

        # Feature aggregation
        self.fc1 = nn.Linear(128 * 3, 256)  # 128 channels from 3 scales
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with multi-scale feature extraction."""
        # Main path
        x = F.relu(self.conv1(x))
        x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = F.relu(self.conv3(x))

        # Multi-scale outputs
        scale1 = self.global_pool(x)  # (batch, 128, 1, 1)
        scale2 = self.global_pool(self.scale2_pool(x))
        scale3 = self.global_pool(self.scale3_pool(x))

        # Concatenate scales
        x = torch.cat([scale1, scale2, scale3], dim=1)
        x = x.view(x.size(0), -1)

        x = F.relu(self.fc1(x))
        x = self.fc2(x)

        return x


# Exercise 11: Model comparison and benchmarking
def compare_model_architectures(
    train_loader: DataLoader,
    val_loader: DataLoader,
    num_epochs: int = 3,
    device: str = 'cpu'
) -> Dict[str, Dict[str, Any]]:
    """Train and compare different CNN architectures."""
    architectures = {
        'SimpleCNN': SimpleCNN(num_classes=10),
        'ResNet18': models.resnet18(pretrained=False),
        'MobileNetV2': models.mobilenet_v2(pretrained=False),
    }

    results = {}
    loss_fn = nn.CrossEntropyLoss()

    for arch_name, model in architectures.items():
        model = model.to(device)

        # Count parameters
        num_params = sum(p.numel() for p in model.parameters())

        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

        best_val_loss = float('inf')
        final_train_loss = 0

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

            final_train_loss = train_loss / len(train_loader)

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
            best_val_loss = min(best_val_loss, val_loss)

        results[arch_name] = {
            'num_parameters': num_params,
            'final_train_loss': final_train_loss,
            'best_val_loss': best_val_loss,
        }

    return results


# Exercise 12: Progressive fine-tuning
def progressive_fine_tuning(
    model: nn.Module,
    train_loader: DataLoader,
    num_stages: int = 3,
    epochs_per_stage: int = 5,
    device: str = 'cpu'
) -> Dict[str, Any]:
    """Fine-tune model in stages, progressively unfreezing layers."""
    model = model.to(device)

    # Initially freeze all
    for param in model.parameters():
        param.requires_grad = False

    loss_fn = nn.CrossEntropyLoss()
    history = {}

    # Get layer groups (for ResNet-like models)
    if hasattr(model, 'layer4'):
        layer_groups = [model.layer4, model.layer3, model.layer2, model.layer1]
    else:
        layer_groups = [model]

    for stage in range(num_stages):
        # Unfreeze layers for this stage
        if stage < len(layer_groups):
            for param in layer_groups[stage].parameters():
                param.requires_grad = True

        # Also unfreeze final layer
        if hasattr(model, 'fc'):
            for param in model.fc.parameters():
                param.requires_grad = True

        # Create optimizer for trainable parameters
        optimizer = torch.optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=1e-4
        )

        stage_losses = []
        model.train()

        for epoch in range(epochs_per_stage):
            epoch_loss = 0.0

            for batch_x, batch_y in train_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)

                logits = model(batch_x)
                loss = loss_fn(logits, batch_y)

                loss.backward()
                optimizer.step()
                optimizer.zero_grad()

                epoch_loss += loss.item()

            stage_losses.append(epoch_loss / len(train_loader))

        history[f'stage_{stage}'] = stage_losses

    return history


# Helper functions
def create_synthetic_image_data(
    num_samples: int = 100,
    num_classes: int = 10,
    image_size: int = 32
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Create synthetic image dataset."""
    images = torch.randn(num_samples, 3, image_size, image_size)
    labels = torch.randint(0, num_classes, (num_samples,))
    return images, labels


class SimpleImageDataset(Dataset):
    """Simple image dataset wrapper."""

    def __init__(self, images: torch.Tensor, labels: torch.Tensor, transform: Optional[Any] = None):
        self.images = images
        self.labels = labels
        self.transform = transform

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        image = self.images[idx]
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, label
