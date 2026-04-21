"""
Image Classifier with Transfer Learning.

Provides the ImageClassifier class for building and training
image classification models with pre-trained backbones.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from torchvision.models import ResNet50_Weights, ResNet18_Weights, VGG16_Weights, MobileNet_V2_Weights
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import logging

logger = logging.getLogger(__name__)


class ImageClassifier:
    """
    Image classifier using transfer learning with pre-trained models.

    Supports multiple architectures (ResNet, VGG, MobileNet) and both
    feature extraction and fine-tuning modes.
    """

    def __init__(
        self,
        model_name: str = "resnet50",
        num_classes: int = 10,
        pretrained: bool = True,
        device: Optional[str] = None
    ):
        """
        Initialize the classifier.

        Args:
            model_name: Architecture name ('resnet18', 'resnet50', 'vgg16', 'mobilenet')
            num_classes: Number of output classes
            pretrained: Whether to use pre-trained ImageNet weights
            device: Device to use ('cuda' or 'cpu'), auto-detected if None
        """
        self.model_name = model_name
        self.num_classes = num_classes
        self.pretrained = pretrained
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.model = self._build_model()
        self.model.to(self.device)

        # Data transforms
        self.train_transform = self._get_train_transforms()
        self.val_transform = self._get_val_transforms()

    def _build_model(self) -> nn.Module:
        """Build the model with appropriate architecture."""
        # Load pre-trained model
        if self.model_name == "resnet18":
            weights = ResNet18_Weights.IMAGENET1K_V1 if self.pretrained else None
            model = models.resnet18(weights=weights)
            num_features = model.fc.in_features
            model.fc = nn.Linear(num_features, self.num_classes)

        elif self.model_name == "resnet50":
            weights = ResNet50_Weights.IMAGENET1K_V2 if self.pretrained else None
            model = models.resnet50(weights=weights)
            num_features = model.fc.in_features
            model.fc = nn.Linear(num_features, self.num_classes)

        elif self.model_name == "vgg16":
            weights = VGG16_Weights.IMAGENET1K_V1 if self.pretrained else None
            model = models.vgg16(weights=weights)
            num_features = model.classifier[6].in_features
            model.classifier[6] = nn.Linear(num_features, self.num_classes)

        elif self.model_name == "mobilenet":
            weights = MobileNet_V2_Weights.IMAGENET1K_V2 if self.pretrained else None
            model = models.mobilenet_v2(weights=weights)
            num_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(num_features, self.num_classes)

        else:
            raise ValueError(f"Unknown model: {self.model_name}")

        return model

    def _get_train_transforms(self) -> transforms.Compose:
        """Get data augmentation transforms for training."""
        return transforms.Compose([
            transforms.Resize(256),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _get_val_transforms(self) -> transforms.Compose:
        """Get transforms for validation (no augmentation)."""
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def freeze_backbone(self) -> None:
        """Freeze all parameters except the final layer."""
        for param in self.model.parameters():
            param.requires_grad = False

        # Unfreeze final layer
        if hasattr(self.model, 'fc'):
            for param in self.model.fc.parameters():
                param.requires_grad = True
        elif hasattr(self.model, 'classifier'):
            for param in self.model.classifier.parameters():
                param.requires_grad = True

    def unfreeze_backbone(self) -> None:
        """Unfreeze all parameters for fine-tuning."""
        for param in self.model.parameters():
            param.requires_grad = True

    def get_optimizer(
        self,
        learning_rate: float = 0.001,
        fine_tune: bool = False
    ) -> torch.optim.Optimizer:
        """
        Get optimizer with appropriate learning rates.

        Args:
            learning_rate: Base learning rate
            fine_tune: If True, use different LR for backbone vs head

        Returns:
            Optimizer instance
        """
        if fine_tune:
            # Different learning rates for backbone and head
            backbone_params = []
            head_params = []

            if hasattr(self.model, 'fc'):
                head_params = list(self.model.fc.parameters())
                backbone_params = [p for p in self.model.parameters() if p not in head_params]
            elif hasattr(self.model, 'classifier'):
                head_params = list(self.model.classifier.parameters())
                backbone_params = [p for p in self.model.parameters() if p not in head_params]

            optimizer = torch.optim.AdamW([
                {'params': backbone_params, 'lr': learning_rate * 0.1},
                {'params': head_params, 'lr': learning_rate}
            ])
        else:
            optimizer = torch.optim.AdamW(
                filter(lambda p: p.requires_grad, self.model.parameters()),
                lr=learning_rate
            )

        return optimizer

    def train_epoch(
        self,
        train_loader: DataLoader,
        optimizer: torch.optim.Optimizer,
        loss_fn: nn.Module
    ) -> float:
        """
        Train for one epoch.

        Args:
            train_loader: Training data loader
            optimizer: Optimizer
            loss_fn: Loss function

        Returns:
            Average loss for the epoch
        """
        self.model.train()
        total_loss = 0.0

        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)

            # Forward pass
            logits = self.model(batch_x)
            loss = loss_fn(logits, batch_y)

            # Backward pass
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            total_loss += loss.item()

        return total_loss / len(train_loader)

    def evaluate(
        self,
        val_loader: DataLoader,
        loss_fn: nn.Module
    ) -> Tuple[float, float]:
        """
        Evaluate model on validation set.

        Args:
            val_loader: Validation data loader
            loss_fn: Loss function

        Returns:
            Tuple of (average_loss, accuracy)
        """
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)

                logits = self.model(batch_x)
                loss = loss_fn(logits, batch_y)
                total_loss += loss.item()

                predictions = logits.argmax(dim=1)
                correct += (predictions == batch_y).sum().item()
                total += batch_y.shape[0]

        avg_loss = total_loss / len(val_loader)
        accuracy = correct / total if total > 0 else 0.0

        return avg_loss, accuracy

    def predict(self, image: Union[Image.Image, str]) -> Dict[str, Any]:
        """
        Predict class for a single image.

        Args:
            image: PIL Image or path to image

        Returns:
            Dictionary with 'class' and 'confidence' keys
        """
        if isinstance(image, str):
            image = Image.open(image)

        image_tensor = self.val_transform(image).unsqueeze(0).to(self.device)

        self.model.eval()
        with torch.no_grad():
            logits = self.model(image_tensor)
            probs = torch.softmax(logits, dim=1)
            confidence, class_idx = probs.max(dim=1)

        return {
            'class': class_idx.item(),
            'confidence': confidence.item()
        }

    def predict_batch(
        self,
        images: List[Union[Image.Image, str]]
    ) -> List[Dict[str, Any]]:
        """
        Predict classes for multiple images.

        Args:
            images: List of PIL Images or image paths

        Returns:
            List of prediction dictionaries
        """
        image_tensors = []

        for image in images:
            if isinstance(image, str):
                image = Image.open(image)
            tensor = self.val_transform(image)
            image_tensors.append(tensor)

        batch = torch.stack(image_tensors).to(self.device)

        self.model.eval()
        with torch.no_grad():
            logits = self.model(batch)
            probs = torch.softmax(logits, dim=1)
            confidences, class_indices = probs.max(dim=1)

        predictions = [
            {'class': idx.item(), 'confidence': conf.item()}
            for idx, conf in zip(class_indices, confidences)
        ]

        return predictions

    def save_checkpoint(self, path: str) -> None:
        """
        Save model checkpoint.

        Args:
            path: Path to save checkpoint
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        checkpoint = {
            'model_state': self.model.state_dict(),
            'model_name': self.model_name,
            'num_classes': self.num_classes,
            'pretrained': self.pretrained
        }

        torch.save(checkpoint, path)
        logger.info(f"Checkpoint saved to {path}")

    def load_checkpoint(self, path: str) -> None:
        """
        Load model checkpoint.

        Args:
            path: Path to checkpoint
        """
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state'])
        logger.info(f"Checkpoint loaded from {path}")

    def to_device(self, device: str) -> None:
        """Move model to device."""
        self.device = device
        self.model.to(device)


class CustomImageDataset(Dataset):
    """
    Custom dataset for loading images from directory structure.

    Expected structure:
    root/
    ├── class1/
    │   ├── img1.jpg
    │   └── img2.jpg
    ├── class2/
    │   └── img3.jpg
    """

    def __init__(
        self,
        root_dir: str,
        transform: Optional[transforms.Compose] = None
    ):
        """
        Initialize dataset.

        Args:
            root_dir: Root directory containing class subdirectories
            transform: Optional data transforms
        """
        self.root_dir = Path(root_dir)
        self.transform = transform

        # Find all classes
        self.classes = sorted([d.name for d in self.root_dir.iterdir() if d.is_dir()])
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}

        # Find all images
        self.images = []
        for class_name in self.classes:
            class_dir = self.root_dir / class_name
            for img_path in class_dir.glob("*"):
                if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    self.images.append((img_path, self.class_to_idx[class_name]))

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        image_path, label = self.images[idx]
        image = Image.open(image_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        return image, label

    @property
    def num_classes(self) -> int:
        """Return number of classes."""
        return len(self.classes)
