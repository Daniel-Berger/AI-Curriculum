"""
Training script for image classifier with transfer learning.

Usage:
    python train.py --model resnet50 --epochs 10 --fine-tune
"""

import argparse
import logging
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from pathlib import Path
from typing import Tuple
import sys

from classifier import ImageClassifier, CustomImageDataset

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train an image classifier with transfer learning"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="resnet50",
        choices=["resnet18", "resnet50", "vgg16", "mobilenet"],
        help="Model architecture to use"
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        default="./data/train",
        help="Directory containing training images organized by class"
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
        help="Number of training epochs"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for training"
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.001,
        help="Learning rate"
    )

    parser.add_argument(
        "--fine-tune",
        action="store_true",
        help="Fine-tune all layers (default: feature extraction only)"
    )

    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default="./checkpoints",
        help="Directory to save model checkpoints"
    )

    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        choices=["cuda", "cpu"],
        help="Device to use for training"
    )

    parser.add_argument(
        "--val-split",
        type=float,
        default=0.2,
        help="Validation split ratio"
    )

    return parser.parse_args()


def create_dataloaders(
    data_dir: str,
    batch_size: int,
    val_split: float = 0.2
) -> Tuple[DataLoader, DataLoader, int]:
    """
    Create training and validation dataloaders.

    Args:
        data_dir: Directory with images organized by class
        batch_size: Batch size
        val_split: Validation split ratio

    Returns:
        Tuple of (train_loader, val_loader, num_classes)
    """
    data_path = Path(data_dir)

    if not data_path.exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)

    logger.info(f"Loading dataset from {data_dir}")

    # Create dataset with train transforms
    classifier = ImageClassifier(num_classes=10)
    dataset = CustomImageDataset(data_dir, transform=classifier.train_transform)

    logger.info(f"Found {len(dataset)} images in {dataset.num_classes} classes")

    # Split into train and validation
    num_train = int(len(dataset) * (1 - val_split))
    num_val = len(dataset) - num_train

    train_dataset, val_dataset = random_split(
        dataset,
        [num_train, num_val],
        generator=torch.Generator().manual_seed(42)
    )

    # Apply different transforms to validation set
    val_dataset.transform = classifier.val_transform

    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True if torch.cuda.is_available() else False
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True if torch.cuda.is_available() else False
    )

    logger.info(f"Train set: {len(train_dataset)}, Validation set: {len(val_dataset)}")

    return train_loader, val_loader, dataset.num_classes


def train(
    classifier: ImageClassifier,
    train_loader: DataLoader,
    val_loader: DataLoader,
    num_epochs: int,
    learning_rate: float,
    fine_tune: bool,
    checkpoint_dir: str
) -> None:
    """
    Train the classifier.

    Args:
        classifier: ImageClassifier instance
        train_loader: Training dataloader
        val_loader: Validation dataloader
        num_epochs: Number of epochs to train
        learning_rate: Learning rate
        fine_tune: Whether to fine-tune all layers
        checkpoint_dir: Directory to save checkpoints
    """
    checkpoint_path = Path(checkpoint_dir)
    checkpoint_path.mkdir(parents=True, exist_ok=True)

    # Prepare model for training
    if fine_tune:
        logger.info("Fine-tuning all layers")
        classifier.unfreeze_backbone()
    else:
        logger.info("Feature extraction mode (backbone frozen)")
        classifier.freeze_backbone()

    # Get optimizer and loss function
    optimizer = classifier.get_optimizer(learning_rate, fine_tune)
    loss_fn = nn.CrossEntropyLoss()

    # Training loop
    best_val_loss = float('inf')
    best_checkpoint_path = checkpoint_path / "best_model.pth"

    logger.info("Starting training...")
    logger.info(f"Model: {classifier.model_name}, Device: {classifier.device}")

    for epoch in range(num_epochs):
        # Train
        train_loss = classifier.train_epoch(train_loader, optimizer, loss_fn)

        # Validate
        val_loss, val_accuracy = classifier.evaluate(val_loader, loss_fn)

        logger.info(
            f"Epoch {epoch + 1}/{num_epochs} - "
            f"Train Loss: {train_loss:.4f}, "
            f"Val Loss: {val_loss:.4f}, "
            f"Val Accuracy: {val_accuracy:.4f}"
        )

        # Save best checkpoint
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            classifier.save_checkpoint(str(best_checkpoint_path))
            logger.info(f"Best model saved with val loss: {val_loss:.4f}")

        # Save periodic checkpoint
        if (epoch + 1) % 5 == 0:
            periodic_checkpoint = checkpoint_path / f"checkpoint_epoch_{epoch + 1}.pth"
            classifier.save_checkpoint(str(periodic_checkpoint))

    # Load and save final model
    classifier.load_checkpoint(str(best_checkpoint_path))
    final_checkpoint = checkpoint_path / "final_model.pth"
    classifier.save_checkpoint(str(final_checkpoint))

    logger.info("Training complete!")
    logger.info(f"Best model saved to {best_checkpoint_path}")
    logger.info(f"Final model saved to {final_checkpoint}")


def main():
    """Main training function."""
    args = parse_arguments()

    logger.info("="*60)
    logger.info("Image Classifier Training")
    logger.info("="*60)

    # Create classifier
    logger.info(f"Creating classifier with {args.model}")

    try:
        train_loader, val_loader, num_classes = create_dataloaders(
            args.data_dir,
            args.batch_size,
            args.val_split
        )
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        logger.info("Creating synthetic data for demonstration...")

        # Create synthetic data for demonstration
        from torch.utils.data import TensorDataset
        X_train = torch.randn(100, 3, 224, 224)
        y_train = torch.randint(0, 10, (100,))
        X_val = torch.randn(20, 3, 224, 224)
        y_val = torch.randint(0, 10, (20,))

        train_dataset = TensorDataset(X_train, y_train)
        val_dataset = TensorDataset(X_val, y_val)

        train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
        num_classes = 10

    classifier = ImageClassifier(
        model_name=args.model,
        num_classes=num_classes,
        pretrained=True,
        device=args.device
    )

    # Log configuration
    logger.info(f"Configuration:")
    logger.info(f"  Model: {args.model}")
    logger.info(f"  Epochs: {args.epochs}")
    logger.info(f"  Batch Size: {args.batch_size}")
    logger.info(f"  Learning Rate: {args.learning_rate}")
    logger.info(f"  Fine-tune: {args.fine_tune}")
    logger.info(f"  Device: {args.device}")

    # Train
    train(
        classifier,
        train_loader,
        val_loader,
        args.epochs,
        args.learning_rate,
        args.fine_tune,
        args.checkpoint_dir
    )


if __name__ == "__main__":
    main()
