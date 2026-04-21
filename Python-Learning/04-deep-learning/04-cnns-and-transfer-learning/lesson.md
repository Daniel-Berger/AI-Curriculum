# CNNs and Transfer Learning

## Introduction

Convolutional Neural Networks (CNNs) are the backbone of computer vision. Transfer learning allows us to leverage pre-trained models to solve new problems efficiently. This chapter covers CNN fundamentals, architectures, and transfer learning strategies.

## 1. The Convolution Operation

### How Convolution Works

The convolution operation applies filters (kernels) to input images to extract features:

```python
import torch
import torch.nn as nn

# Simple convolution example
conv = nn.Conv2d(
    in_channels=3,      # RGB image
    out_channels=16,    # Number of filters
    kernel_size=3,      # 3x3 filter
    stride=1,           # Move filter by 1 pixel
    padding=1           # Add border of 0s
)

# Input: (batch_size, channels, height, width)
x = torch.randn(4, 3, 32, 32)
output = conv(x)
print(output.shape)  # (4, 16, 32, 32)
```

### Key Concepts

**Filters/Kernels**: Learnable weights that detect features

```python
# Visualize filter weights
conv = nn.Conv2d(3, 16, kernel_size=3)
# conv.weight has shape (16, 3, 3, 3)
# 16 output channels, 3 input channels, 3x3 spatial dimensions
```

**Stride**: How many pixels the filter moves

```python
# Stride=2 means filter moves 2 pixels at a time
conv_stride2 = nn.Conv2d(3, 16, kernel_size=3, stride=2)
x = torch.randn(4, 3, 32, 32)
output = conv_stride2(x)
print(output.shape)  # (4, 16, 16, 16) - height/width halved
```

**Padding**: Adding zeros around the image

```python
# Padding=0: no padding (shrinks spatial dimensions)
conv_no_pad = nn.Conv2d(3, 16, kernel_size=3, padding=0)
x = torch.randn(4, 3, 32, 32)
output = conv_no_pad(x)
print(output.shape)  # (4, 16, 30, 30)

# Padding=1: same padding (keeps dimensions with stride=1)
conv_same = nn.Conv2d(3, 16, kernel_size=3, padding=1)
output = conv_same(x)
print(output.shape)  # (4, 16, 32, 32) - same spatial size
```

### Output Size Calculation

```
output_size = (input_size + 2*padding - kernel_size) / stride + 1
```

## 2. Pooling Operations

Pooling reduces spatial dimensions and aggregates features:

```python
# Max pooling: take maximum value in each pool
maxpool = nn.MaxPool2d(kernel_size=2, stride=2)
x = torch.randn(4, 16, 32, 32)
output = maxpool(x)
print(output.shape)  # (4, 16, 16, 16) - spatial dims halved

# Average pooling: average values in each pool
avgpool = nn.AvgPool2d(kernel_size=2, stride=2)
output = avgpool(x)
print(output.shape)  # (4, 16, 16, 16)

# Adaptive pooling: automatically choose pool size
adaptive_pool = nn.AdaptiveAvgPool2d((1, 1))
output = adaptive_pool(x)
print(output.shape)  # (4, 16, 1, 1) - global average pooling
```

## 3. Classic CNN Architectures

### LeNet (1998)

One of the first CNNs, designed for digit recognition:

```python
class LeNet(nn.Module):
    def __init__(self, num_classes: int = 10):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(1, 6, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(6, 16, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.classifier = nn.Sequential(
            nn.Linear(16 * 5 * 5, 120),
            nn.ReLU(inplace=True),
            nn.Linear(120, 84),
            nn.ReLU(inplace=True),
            nn.Linear(84, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.flatten(1)
        x = self.classifier(x)
        return x
```

### AlexNet (2012)

Deeper network with ReLU and dropout:

```python
class AlexNet(nn.Module):
    def __init__(self, num_classes: int = 1000):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),

            nn.Conv2d(64, 192, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),

            nn.Conv2d(192, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(384, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
        )

        self.avgpool = nn.AdaptiveAvgPool2d((6, 6))

        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = x.flatten(1)
        x = self.classifier(x)
        return x
```

### VGG

Simpler, uniform architecture with 3x3 convolutions:

```python
class VGG16(nn.Module):
    def __init__(self, num_classes: int = 1000):
        super().__init__()

        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # Block 2
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # ... more blocks ...
        )

        self.avgpool = nn.AdaptiveAvgPool2d((7, 7))
        self.classifier = nn.Sequential(
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(4096, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = x.flatten(1)
        x = self.classifier(x)
        return x
```

### ResNet (Residual Networks)

Skip connections prevent vanishing gradients:

```python
class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()

        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)

        # Shortcut connection (identity or projection)
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        # Add skip connection
        out = out + self.shortcut(residual)
        out = self.relu(out)

        return out
```

### EfficientNet

Scales depth, width, and resolution in a principled way:

```python
# EfficientNet is complex to implement from scratch
# Use torchvision pre-trained version instead
from torchvision.models import efficientnet_b0

model = efficientnet_b0(pretrained=True)
```

## 4. Building CNNs in PyTorch

### Complete CNN Example

```python
import torch.nn.functional as F

class SimpleCNN(nn.Module):
    def __init__(self, num_classes: int = 10):
        super().__init__()

        # Convolutional layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        # Pooling
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Fully connected layers
        self.fc1 = nn.Linear(128 * 4 * 4, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, num_classes)

        # Regularization
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        # Input: (batch_size, 3, 32, 32)

        # Block 1: Conv -> ReLU -> Pool
        x = F.relu(self.conv1(x))  # (batch_size, 32, 32, 32)
        x = self.pool(x)            # (batch_size, 32, 16, 16)

        # Block 2: Conv -> ReLU -> Pool
        x = F.relu(self.conv2(x))  # (batch_size, 64, 16, 16)
        x = self.pool(x)            # (batch_size, 64, 8, 8)

        # Block 3: Conv -> ReLU -> Pool
        x = F.relu(self.conv3(x))  # (batch_size, 128, 8, 8)
        x = self.pool(x)            # (batch_size, 128, 4, 4)

        # Flatten
        x = x.view(x.size(0), -1)  # (batch_size, 128*4*4)

        # Fully connected
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)

        return x

# Usage
model = SimpleCNN(num_classes=10)
x = torch.randn(4, 3, 32, 32)
output = model(x)
print(output.shape)  # (4, 10)
```

## 5. Transfer Learning

### Feature Extraction

Use pre-trained model as fixed feature extractor:

```python
import torchvision.models as models

# Load pre-trained ResNet50
resnet50 = models.resnet50(pretrained=True)

# Freeze all parameters
for param in resnet50.parameters():
    param.requires_grad = False

# Replace final layer for new task
num_classes = 10
resnet50.fc = nn.Linear(resnet50.fc.in_features, num_classes)

# Only final layer is trainable
# Training is fast, memory-efficient
for epoch in range(num_epochs):
    # Train with frozen backbone
    pass
```

### Fine-tuning

Train entire model with lower learning rate:

```python
# Load pre-trained model
resnet50 = models.resnet50(pretrained=True)

# Initially all parameters frozen
for param in resnet50.parameters():
    param.requires_grad = False

# Replace final layer
resnet50.fc = nn.Linear(resnet50.fc.in_features, num_classes)

# Make backbone trainable
for param in resnet50.parameters():
    param.requires_grad = True

# Use lower learning rate for pre-trained weights
backbone_params = list(resnet50.children())[:-1]  # All but last layer
head_params = list(resnet50.children())[-1:]      # Last layer

optimizer = torch.optim.Adam([
    {'params': nn.Sequential(*backbone_params).parameters(), 'lr': 1e-5},
    {'params': nn.Sequential(*head_params).parameters(), 'lr': 1e-3}
])
```

### Progressive Fine-tuning

Unfreeze layers gradually:

```python
resnet50 = models.resnet50(pretrained=True)

# Start with all layers frozen
for param in resnet50.parameters():
    param.requires_grad = False

# Replace final layer
resnet50.fc = nn.Linear(resnet50.fc.in_features, num_classes)

# Stage 1: Train only final layer
print("Stage 1: Training final layer")
for epoch in range(num_epochs):
    train()

# Stage 2: Unfreeze and train layer4
print("Stage 2: Fine-tuning layer4")
for param in resnet50.layer4.parameters():
    param.requires_grad = True

# Recreate optimizer with all trainable parameters
optimizer = torch.optim.AdamW(
    filter(lambda p: p.requires_grad, resnet50.parameters()),
    lr=1e-4
)

for epoch in range(num_epochs):
    train()

# Stage 3: Unfreeze and train layer3
print("Stage 3: Fine-tuning layer3")
for param in resnet50.layer3.parameters():
    param.requires_grad = True
# ... continue ...
```

## 6. Pretrained Models

### Torchvision Models

```python
from torchvision import models

# Classification models
resnet18 = models.resnet18(pretrained=True)
resnet50 = models.resnet50(pretrained=True)
vgg16 = models.vgg16(pretrained=True)
mobilenet = models.mobilenet_v2(pretrained=True)
efficientnet = models.efficientnet_b0(pretrained=True)

# Object detection
faster_rcnn = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)

# Segmentation
fcn = models.segmentation.fcn_resnet50(pretrained=True)

# List all available models
import torchvision.models as models
print(models.list_models())
```

### Model Adaptation

```python
# Load model and adapt to new task
model = models.resnet50(pretrained=True)

# Get input features to final layer
num_features = model.fc.in_features

# Replace final layer
num_classes = 10
model.fc = nn.Linear(num_features, num_classes)

# Modify for different input size
model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3)  # For grayscale

# For regression (instead of classification)
model.fc = nn.Linear(num_features, 1)  # Single output value
```

## 7. Data Augmentation for Images

Augmentation increases data diversity:

```python
from torchvision import transforms
from PIL import Image

# Training augmentation (strong)
train_transforms = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Validation augmentation (minimal)
val_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Use in dataset
from torch.utils.data import DataLoader

train_dataset = ImageDataset(image_paths, labels, transform=train_transforms)
val_dataset = ImageDataset(image_paths, labels, transform=val_transforms)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
```

## 8. Advanced Augmentation

```python
# AutoAugment: automatically choose augmentation policies
# RandAugment: random augmentation with fewer hyperparameters
# Mixup: blend two images
# CutMix: mix regions from two images

from torchvision.transforms import AutoAugment, AutoAugmentPolicy

transform = transforms.Compose([
    transforms.ToTensor(),
    AutoAugment(AutoAugmentPolicy.IMAGENET),
    transforms.Normalize((0.5,), (0.5,))
])

# CutMix implementation example
def cutmix(image, target, alpha=1.0):
    """Apply CutMix augmentation."""
    if np.random.rand() > 0.5:
        return image, target

    batch_size = image.shape[0]
    index = torch.randperm(batch_size)

    # Random location
    lam = np.random.beta(alpha, alpha)
    image_size = image.shape[-1]
    cut_ratio = np.sqrt(1.0 - lam)
    cut_size = int(image_size * cut_ratio)

    cx = np.random.randint(0, image_size)
    cy = np.random.randint(0, image_size)

    bbx1 = np.clip(cx - cut_size // 2, 0, image_size)
    bby1 = np.clip(cy - cut_size // 2, 0, image_size)
    bbx2 = np.clip(cx + cut_size // 2, 0, image_size)
    bby2 = np.clip(cy + cut_size // 2, 0, image_size)

    image[:, :, bbx1:bbx2, bby1:bby2] = image[index, :, bbx1:bbx2, bby1:bby2]
    lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (image_size * image_size))

    return image, target, lam
```

## Summary

- **Convolution**: Slides filters across image to extract features
- **Pooling**: Reduces spatial dimensions while preserving important features
- **CNN Architectures**: LeNet → VGG → ResNet → EfficientNet
- **Skip Connections**: ResNets enable training very deep networks
- **Transfer Learning**: Leverage pre-trained models for new tasks
- **Feature Extraction**: Freeze backbone, train final layers (fast)
- **Fine-tuning**: Train entire model with lower learning rate
- **Data Augmentation**: Increase training diversity to improve generalization
