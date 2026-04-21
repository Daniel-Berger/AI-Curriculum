"""
Exercises for CNNs and Transfer Learning.

Practice building CNN architectures, implementing convolution operations,
and using transfer learning strategies.
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
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
    """
    Calculate the output size of a convolution operation.

    Args:
        input_size: Input spatial dimension (height or width)
        kernel_size: Kernel/filter size
        stride: How far the kernel moves
        padding: Padding added to input

    Returns:
        Output spatial dimension
    """
    pass


# Exercise 2: Build a simple CNN
class SimpleCNN(nn.Module):
    """
    Create a simple CNN with 3 convolutional blocks.

    Each block: Conv2d -> ReLU -> MaxPool2d
    Followed by fully connected layers for classification.
    """

    def __init__(self, num_classes: int = 10):
        """
        Initialize SimpleCNN.

        Args:
            num_classes: Number of output classes
        """
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor of shape (batch_size, 3, 32, 32)

        Returns:
            Logits of shape (batch_size, num_classes)
        """
        pass


# Exercise 3: Implement residual block
class ResidualBlock(nn.Module):
    """
    Create a residual block with skip connections.

    Structure: Conv2d -> BatchNorm2d -> ReLU -> Conv2d -> BatchNorm2d
    Then add skip connection and apply ReLU.
    """

    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        """
        Initialize residual block.

        Args:
            in_channels: Number of input channels
            out_channels: Number of output channels
            stride: Stride for convolution
        """
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with skip connection.

        Args:
            x: Input tensor

        Returns:
            Output with skip connection applied
        """
        pass


# Exercise 4: Transfer learning - feature extraction
def transfer_learning_feature_extraction(
    model: nn.Module,
    train_loader: DataLoader,
    num_epochs: int,
    device: str = 'cpu'
) -> List[float]:
    """
    Train a pre-trained model using feature extraction (frozen backbone).

    Only the final layer should be trainable.

    Args:
        model: Pre-trained model with modified final layer
        train_loader: Training data loader
        num_epochs: Number of training epochs
        device: Device to train on

    Returns:
        List of training losses per epoch
    """
    pass


# Exercise 5: Transfer learning - fine-tuning
def transfer_learning_fine_tuning(
    model: nn.Module,
    train_loader: DataLoader,
    num_epochs: int,
    backbone_lr: float = 1e-5,
    head_lr: float = 1e-3,
    device: str = 'cpu'
) -> List[float]:
    """
    Fine-tune a pre-trained model with different learning rates.

    Backbone gets lower learning rate, final layer gets higher learning rate.

    Args:
        model: Pre-trained model
        train_loader: Training data loader
        num_epochs: Number of epochs
        backbone_lr: Learning rate for pre-trained weights
        head_lr: Learning rate for final layer
        device: Device to train on

    Returns:
        List of training losses
    """
    pass


# Exercise 6: Load pretrained model and adapt
def load_and_adapt_pretrained_model(
    model_name: str,
    num_classes: int,
    pretrained: bool = True
) -> nn.Module:
    """
    Load a pretrained model and adapt it for a new task.

    Modify the final layer to output num_classes instead of 1000.

    Args:
        model_name: Name of model ('resnet18', 'resnet50', 'vgg16', etc.)
        num_classes: Number of classes for new task
        pretrained: Whether to load pretrained weights

    Returns:
        Adapted model ready for fine-tuning
    """
    pass


# Exercise 7: Data augmentation transforms
def create_augmentation_transforms() -> Tuple[Any, Any]:
    """
    Create training and validation image transforms.

    Training should include augmentation, validation minimal preprocessing.

    Returns:
        Tuple of (train_transforms, val_transforms)
    """
    pass


# Exercise 8: Custom CNN with batch normalization
class CNNWithBatchNorm(nn.Module):
    """
    Build CNN with batch normalization for stable training.

    Include batch normalization after each convolution layer.
    """

    def __init__(self, num_classes: int = 10):
        """
        Initialize CNN with batch normalization.

        Args:
            num_classes: Number of output classes
        """
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        pass


# Exercise 9: Implement conv output calculation
def calculate_receptive_field(
    layer_configs: List[Dict[str, int]]
) -> int:
    """
    Calculate receptive field size given a sequence of layers.

    Each layer config: {'kernel_size': int, 'stride': int, 'padding': int}

    Args:
        layer_configs: List of layer configuration dicts

    Returns:
        Total receptive field size
    """
    pass


# Exercise 10: Multi-scale feature extraction
class MultiScaleCNN(nn.Module):
    """
    Build CNN that extracts features at multiple scales.

    Use different pooling rates to capture features at different resolutions.
    """

    def __init__(self, num_classes: int = 10):
        """Initialize multi-scale CNN."""
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with multi-scale feature extraction."""
        pass


# Exercise 11: Model comparison and benchmarking
def compare_model_architectures(
    train_loader: DataLoader,
    val_loader: DataLoader,
    num_epochs: int = 3,
    device: str = 'cpu'
) -> Dict[str, Dict[str, Any]]:
    """
    Train and compare different CNN architectures.

    Return metrics for each model: final_loss, best_val_loss, parameters_count, etc.

    Args:
        train_loader: Training data loader
        val_loader: Validation data loader
        num_epochs: Number of epochs to train
        device: Device to train on

    Returns:
        Dictionary with comparison metrics for each architecture
    """
    pass


# Exercise 12: Progressive fine-tuning
def progressive_fine_tuning(
    model: nn.Module,
    train_loader: DataLoader,
    num_stages: int = 3,
    epochs_per_stage: int = 5,
    device: str = 'cpu'
) -> Dict[str, Any]:
    """
    Fine-tune model in stages, progressively unfreezing layers.

    Start with frozen backbone, gradually unfreeze layers from top to bottom.

    Args:
        model: Pre-trained model
        train_loader: Training data loader
        num_stages: Number of fine-tuning stages
        epochs_per_stage: Epochs per stage
        device: Device to train on

    Returns:
        Dictionary with training history for each stage
    """
    pass


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
