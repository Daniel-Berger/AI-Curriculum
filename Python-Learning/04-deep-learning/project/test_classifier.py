"""
Unit tests for the image classifier.

Run with: pytest test_classifier.py -v
"""

import pytest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
import tempfile
from PIL import Image
import numpy as np

from classifier import ImageClassifier, CustomImageDataset


class TestImageClassifier:
    """Test suite for ImageClassifier class."""

    @pytest.fixture
    def classifier(self):
        """Create a classifier instance for testing."""
        return ImageClassifier(
            model_name="resnet18",
            num_classes=10,
            pretrained=False,
            device="cpu"
        )

    @pytest.fixture
    def sample_data(self):
        """Create sample image tensor."""
        return torch.randn(4, 3, 224, 224)

    @pytest.fixture
    def sample_labels(self):
        """Create sample labels."""
        return torch.randint(0, 10, (4,))

    def test_initialization(self, classifier):
        """Test classifier initialization."""
        assert classifier.model_name == "resnet18"
        assert classifier.num_classes == 10
        assert classifier.pretrained is False
        assert classifier.device == "cpu"

    def test_model_creation(self):
        """Test model creation for different architectures."""
        for model_name in ["resnet18", "resnet50", "vgg16", "mobilenet"]:
            classifier = ImageClassifier(
                model_name=model_name,
                num_classes=5,
                pretrained=False
            )
            assert classifier.model is not None
            assert classifier.model_name == model_name

    def test_invalid_model_name(self):
        """Test that invalid model name raises error."""
        with pytest.raises(ValueError):
            ImageClassifier(
                model_name="invalid_model",
                num_classes=10,
                pretrained=False
            )

    def test_freeze_backbone(self, classifier):
        """Test freezing backbone parameters."""
        classifier.freeze_backbone()

        # Check that backbone params are frozen
        frozen_count = 0
        trainable_count = 0

        for name, param in classifier.model.named_parameters():
            if 'fc' not in name:
                frozen_count += param.requires_grad == False
            else:
                trainable_count += param.requires_grad == True

        assert frozen_count > 0, "Backbone should have frozen parameters"
        assert trainable_count > 0, "Final layer should be trainable"

    def test_unfreeze_backbone(self, classifier):
        """Test unfreezing backbone parameters."""
        classifier.freeze_backbone()
        classifier.unfreeze_backbone()

        # All parameters should be trainable
        for param in classifier.model.parameters():
            assert param.requires_grad, "All parameters should be trainable"

    def test_forward_pass(self, classifier, sample_data):
        """Test forward pass through the model."""
        classifier.model.eval()
        with torch.no_grad():
            output = classifier.model(sample_data)

        assert output.shape == (4, 10), f"Expected (4, 10), got {output.shape}"

    def test_train_epoch(self, classifier, sample_data, sample_labels):
        """Test training for one epoch."""
        dataset = TensorDataset(sample_data, sample_labels)
        loader = DataLoader(dataset, batch_size=2)

        optimizer = classifier.get_optimizer(learning_rate=0.01, fine_tune=False)
        loss_fn = nn.CrossEntropyLoss()

        loss = classifier.train_epoch(loader, optimizer, loss_fn)

        assert isinstance(loss, float)
        assert loss >= 0, "Loss should be non-negative"

    def test_evaluate(self, classifier, sample_data, sample_labels):
        """Test evaluation."""
        dataset = TensorDataset(sample_data, sample_labels)
        loader = DataLoader(dataset, batch_size=2)

        loss_fn = nn.CrossEntropyLoss()

        loss, accuracy = classifier.evaluate(loader, loss_fn)

        assert isinstance(loss, float)
        assert isinstance(accuracy, float)
        assert 0 <= accuracy <= 1, "Accuracy should be between 0 and 1"

    def test_get_optimizer_feature_extraction(self, classifier):
        """Test optimizer creation for feature extraction."""
        classifier.freeze_backbone()
        optimizer = classifier.get_optimizer(learning_rate=0.001, fine_tune=False)

        assert optimizer is not None
        assert len(optimizer.param_groups) > 0

    def test_get_optimizer_fine_tuning(self, classifier):
        """Test optimizer creation for fine-tuning."""
        optimizer = classifier.get_optimizer(learning_rate=0.001, fine_tune=True)

        assert optimizer is not None
        # Should have 2 param groups (backbone and head with different LRs)
        assert len(optimizer.param_groups) == 2

    def test_predict_single_image(self, classifier):
        """Test single image prediction."""
        # Create a dummy image
        dummy_image = torch.randn(3, 224, 224)

        # Create temporary image file
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = Path(tmpdir) / "test.jpg"

            # Convert tensor to PIL Image and save
            img_array = ((dummy_image.numpy() * 0.5 + 0.5) * 255).astype(np.uint8)
            img_array = np.transpose(img_array, (1, 2, 0))
            Image.fromarray(img_array).save(img_path)

            # Predict
            prediction = classifier.predict(str(img_path))

            assert "class" in prediction
            assert "confidence" in prediction
            assert 0 <= prediction["class"] < 10
            assert 0 <= prediction["confidence"] <= 1

    def test_predict_batch(self, classifier):
        """Test batch image prediction."""
        batch_size = 3
        dummy_images = [torch.randn(3, 224, 224) for _ in range(batch_size)]

        with tempfile.TemporaryDirectory() as tmpdir:
            image_paths = []
            for i, img_tensor in enumerate(dummy_images):
                img_path = Path(tmpdir) / f"test_{i}.jpg"
                img_array = ((img_tensor.numpy() * 0.5 + 0.5) * 255).astype(np.uint8)
                img_array = np.transpose(img_array, (1, 2, 0))
                Image.fromarray(img_array).save(img_path)
                image_paths.append(str(img_path))

            predictions = classifier.predict_batch(image_paths)

            assert len(predictions) == batch_size
            for pred in predictions:
                assert "class" in pred
                assert "confidence" in pred

    def test_save_and_load_checkpoint(self, classifier):
        """Test saving and loading checkpoints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.pth"

            # Save checkpoint
            classifier.save_checkpoint(str(checkpoint_path))
            assert checkpoint_path.exists()

            # Create new classifier and load
            new_classifier = ImageClassifier(
                model_name="resnet18",
                num_classes=10,
                pretrained=False
            )
            new_classifier.load_checkpoint(str(checkpoint_path))

            # Models should have same weights
            for p1, p2 in zip(classifier.model.parameters(), new_classifier.model.parameters()):
                assert torch.allclose(p1, p2)

    def test_to_device(self, classifier):
        """Test moving model to device."""
        if torch.cuda.is_available():
            classifier.to_device("cuda")
            assert classifier.device == "cuda"
            assert next(classifier.model.parameters()).device.type == "cuda"

            classifier.to_device("cpu")
            assert classifier.device == "cpu"
            assert next(classifier.model.parameters()).device.type == "cpu"

    def test_transforms(self, classifier):
        """Test that transforms are properly configured."""
        assert classifier.train_transform is not None
        assert classifier.val_transform is not None

        # Create dummy image tensor
        dummy_img = torch.randn(3, 256, 256)
        dummy_pil = Image.fromarray(
            ((dummy_img.numpy() * 0.5 + 0.5) * 255).astype(np.uint8).transpose(1, 2, 0)
        )

        # Apply transforms
        train_output = classifier.train_transform(dummy_pil)
        val_output = classifier.val_transform(dummy_pil)

        assert train_output.shape == (3, 224, 224)
        assert val_output.shape == (3, 224, 224)


class TestCustomImageDataset:
    """Test suite for CustomImageDataset class."""

    @pytest.fixture
    def sample_dataset(self):
        """Create a sample dataset structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create class directories
            for class_name in ["class1", "class2"]:
                class_dir = root / class_name
                class_dir.mkdir()

                # Create dummy images
                for i in range(3):
                    img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
                    Image.fromarray(img_array).save(class_dir / f"img_{i}.jpg")

            yield root

    def test_dataset_initialization(self, sample_dataset):
        """Test dataset initialization."""
        dataset = CustomImageDataset(str(sample_dataset))

        assert len(dataset) > 0
        assert dataset.num_classes == 2
        assert len(dataset.classes) == 2

    def test_dataset_getitem(self, sample_dataset):
        """Test getting items from dataset."""
        dataset = CustomImageDataset(str(sample_dataset))

        for i in range(len(dataset)):
            img, label = dataset[i]

            assert isinstance(img, Image.Image)
            assert isinstance(label, int)
            assert 0 <= label < dataset.num_classes

    def test_dataset_with_transform(self, sample_dataset):
        """Test dataset with transforms."""
        from torchvision import transforms

        transform = transforms.Compose([
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor()
        ])

        dataset = CustomImageDataset(str(sample_dataset), transform=transform)

        img, label = dataset[0]

        assert isinstance(img, torch.Tensor)
        assert img.shape == (3, 224, 224)


# Integration tests
class TestIntegration:
    """Integration tests for the classifier."""

    def test_full_training_loop(self):
        """Test a complete training loop."""
        # Create dummy data
        X = torch.randn(20, 3, 224, 224)
        y = torch.randint(0, 3, (20,))

        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=4)

        # Create classifier
        classifier = ImageClassifier(
            model_name="resnet18",
            num_classes=3,
            pretrained=False,
            device="cpu"
        )

        # Freeze backbone
        classifier.freeze_backbone()

        # Get optimizer and loss
        optimizer = classifier.get_optimizer(learning_rate=0.01, fine_tune=False)
        loss_fn = nn.CrossEntropyLoss()

        # Train for 2 epochs
        for epoch in range(2):
            train_loss = classifier.train_epoch(loader, optimizer, loss_fn)
            val_loss, val_acc = classifier.evaluate(loader, loss_fn)

            assert train_loss >= 0
            assert val_loss >= 0
            assert 0 <= val_acc <= 1

    def test_checkpoint_recovery(self):
        """Test that training can be recovered from checkpoint."""
        X = torch.randn(20, 3, 224, 224)
        y = torch.randint(0, 3, (20,))

        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.pth"

            # First training session
            classifier1 = ImageClassifier(
                model_name="resnet18",
                num_classes=3,
                pretrained=False
            )

            optimizer = classifier1.get_optimizer(0.01, fine_tune=False)
            loss_fn = nn.CrossEntropyLoss()

            classifier1.train_epoch(loader, optimizer, loss_fn)
            classifier1.save_checkpoint(str(checkpoint_path))

            # Load and continue training
            classifier2 = ImageClassifier(
                model_name="resnet18",
                num_classes=3,
                pretrained=False
            )
            classifier2.load_checkpoint(str(checkpoint_path))

            # Models should be identical
            for p1, p2 in zip(classifier1.model.parameters(), classifier2.model.parameters()):
                assert torch.allclose(p1, p2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
