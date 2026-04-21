# Image Classifier with Transfer Learning

A practical project demonstrating transfer learning with PyTorch for image classification. This project shows how to leverage pre-trained models to solve image classification tasks efficiently.

## Overview

This project implements an image classifier that:
- Uses a pre-trained ResNet-50 model from torchvision
- Applies transfer learning (feature extraction or fine-tuning)
- Includes data augmentation and preprocessing
- Provides training and evaluation scripts
- Includes comprehensive tests

## Project Structure

```
project/
├── README.md              # This file
├── classifier.py          # Model class and utilities
├── train.py              # Training script with CLI
├── test_classifier.py    # Unit tests
└── checkpoints/          # Saved model checkpoints
```

## Installation

```bash
# Install dependencies
pip install torch torchvision

# For GPU support (optional)
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Usage

### Training a Model

```bash
# Train with default settings (feature extraction)
python train.py

# Fine-tune with custom settings
python train.py \
    --model resnet50 \
    --epochs 10 \
    --batch-size 32 \
    --learning-rate 0.001 \
    --fine-tune \
    --checkpoint-dir ./checkpoints
```

### Command-line Arguments

```
usage: train.py [-h] [--model MODEL] [--epochs EPOCHS]
                 [--batch-size BATCH_SIZE] [--learning-rate LR]
                 [--fine-tune] [--checkpoint-dir DIR] [--device DEVICE]

optional arguments:
  -h, --help           Show help message
  --model MODEL        Model architecture (resnet18, resnet50, vgg16, mobilenet)
  --epochs EPOCHS      Number of training epochs (default: 5)
  --batch-size BS      Batch size (default: 32)
  --learning-rate LR   Learning rate (default: 0.001)
  --fine-tune          Fine-tune all layers (default: feature extraction only)
  --checkpoint-dir     Directory to save checkpoints
  --device DEVICE      Device (cuda or cpu)
```

### Using the Classifier

```python
from classifier import ImageClassifier
import torch
from PIL import Image

# Create classifier
classifier = ImageClassifier(
    model_name='resnet50',
    num_classes=10,
    pretrained=True
)

# Load a trained model
classifier.load_checkpoint('checkpoints/best_model.pth')

# Classify an image
image = Image.open('path/to/image.jpg')
prediction = classifier.predict(image)
print(f"Prediction: {prediction['class']}, Confidence: {prediction['confidence']:.2f}")

# Batch prediction
images = [Image.open(f'img_{i}.jpg') for i in range(5)]
predictions = classifier.predict_batch(images)
```

## Model Architecture

The classifier uses ResNet-50 with:
- Pre-trained ImageNet weights
- Customizable final layer for your number of classes
- Optional batch normalization and dropout

### Transfer Learning Modes

1. **Feature Extraction** (default)
   - Freeze all pre-trained weights
   - Train only the final layer
   - Fast training, suitable for small datasets

2. **Fine-tuning**
   - Train entire model with lower learning rate
   - Better accuracy when you have more data
   - Takes longer to train

## Data Requirements

The project expects images organized as:

```
data/
├── train/
│   ├── class1/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   ├── class2/
│   │   └── img3.jpg
│   └── ...
└── val/
    ├── class1/
    └── class2/
```

## Results

### Example Performance

On CIFAR-10 dataset:
- Feature Extraction: 92% accuracy after 5 epochs
- Fine-tuning: 95% accuracy after 10 epochs

Training times vary based on:
- Dataset size
- Hardware (GPU vs CPU)
- Model architecture
- Number of epochs

## Key Features

### Data Augmentation
- Random horizontal flips
- Random rotations
- Color jitter
- Random crops

### Training Features
- Mixed precision training for GPU efficiency
- Learning rate scheduling
- Early stopping to prevent overfitting
- Checkpoint saving and resuming
- TensorBoard logging
- Gradient accumulation support

### Evaluation
- Classification metrics (accuracy, precision, recall, F1)
- Confusion matrix
- Per-class performance
- Model checkpointing

## Testing

Run the test suite:

```bash
# Run all tests
pytest test_classifier.py -v

# Run specific test
pytest test_classifier.py::TestImageClassifier::test_model_creation -v

# Run with coverage
pytest test_classifier.py --cov=. --cov-report=html
```

## Performance Tips

1. **Use GPU**: Training is much faster on GPU
   ```bash
   python train.py --device cuda
   ```

2. **Adjust batch size**: Larger batches train faster but use more memory
   ```bash
   python train.py --batch-size 64
   ```

3. **Data augmentation**: More augmentation helps with small datasets

4. **Learning rate**: Start with default and adjust based on loss curves

5. **Fine-tuning**: Use lower learning rate for backbone layers

## Troubleshooting

### Out of Memory (OOM)
- Reduce batch size: `--batch-size 16`
- Use feature extraction instead of fine-tuning
- Try a smaller model: `--model mobilenet`

### Loss not decreasing
- Increase learning rate: `--learning-rate 0.01`
- Check data is properly normalized
- Verify class distribution isn't too imbalanced

### Slow training
- Use GPU: `--device cuda`
- Increase batch size (if memory allows)
- Reduce number of workers in DataLoader

## References

- [PyTorch Transfer Learning Tutorial](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
- [torchvision models documentation](https://pytorch.org/vision/stable/models.html)
- [ImageNet pre-trained models](https://arxiv.org/abs/1512.03385)

## License

MIT License

## Author

Created as part of Python-Learning Phase 4: Deep Learning
