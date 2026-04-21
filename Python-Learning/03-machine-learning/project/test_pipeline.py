"""
Test Suite for ML Pipeline
===========================

Comprehensive tests for the machine learning pipeline including
data loading, preprocessing, model training, and evaluation.
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch

from config import Config
from pipeline import Pipeline


class TestConfig:
    """Test configuration module."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = Config()
        assert config.dataset_n_samples == 1000
        assert config.dataset_n_features == 20
        assert config.dataset_n_classes == 3
        assert config.cv_folds == 5

    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = Config(dataset_n_samples=500, dataset_n_features=10)
        assert config.dataset_n_samples == 500
        assert config.dataset_n_features == 10

    def test_config_to_dict(self):
        """Test configuration to_dict conversion."""
        config = Config()
        config_dict = config.to_dict()

        assert 'dataset' in config_dict
        assert 'models' in config_dict
        assert 'training' in config_dict
        assert 'mlflow' in config_dict

    def test_config_string_representation(self):
        """Test configuration string representation."""
        config = Config()
        config_str = str(config)

        assert 'Config' in config_str
        assert '1000' in config_str  # n_samples
        assert '20' in config_str    # n_features

    def test_config_post_init_sets_defaults(self):
        """Test that post_init sets default parameter dicts."""
        config = Config()

        assert config.logistic_regression_params is not None
        assert config.random_forest_params is not None
        assert config.gradient_boosting_params is not None
        assert config.scoring_metrics is not None

    def test_config_model_params_match_attributes(self):
        """Test that model params match individual attributes."""
        config = Config()

        assert config.logistic_regression_params['C'] == config.logistic_regression_C
        assert config.random_forest_params['n_estimators'] == config.random_forest_n_estimators
        assert config.gradient_boosting_params['learning_rate'] == config.gradient_boosting_learning_rate


class TestPipelineDataLoading:
    """Test data loading functionality."""

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        config = Config()
        pipeline = Pipeline(config)

        assert pipeline.config is config
        assert pipeline.X_train is None
        assert pipeline.X_test is None

    def test_load_data_returns_correct_shape(self):
        """Test that load_data returns correct dimensions."""
        config = Config(dataset_n_samples=100, dataset_n_features=10)
        pipeline = Pipeline(config)

        X, y = pipeline._load_data()

        assert X.shape == (100, 10)
        assert y.shape == (100,)
        assert len(np.unique(y)) == config.dataset_n_classes

    def test_load_data_deterministic(self):
        """Test that load_data is deterministic with same seed."""
        config1 = Config(dataset_random_state=42)
        config2 = Config(dataset_random_state=42)

        pipeline1 = Pipeline(config1)
        pipeline2 = Pipeline(config2)

        X1, y1 = pipeline1._load_data()
        X2, y2 = pipeline2._load_data()

        np.testing.assert_array_equal(X1, X2)
        np.testing.assert_array_equal(y1, y2)

    def test_load_data_different_seeds(self):
        """Test that different seeds produce different data."""
        config1 = Config(dataset_random_state=42)
        config2 = Config(dataset_random_state=43)

        pipeline1 = Pipeline(config1)
        pipeline2 = Pipeline(config2)

        X1, y1 = pipeline1._load_data()
        X2, y2 = pipeline2._load_data()

        assert not np.allclose(X1, X2)


class TestPipelinePreprocessing:
    """Test data preprocessing."""

    def test_create_preprocessor_returns_column_transformer(self):
        """Test that create_preprocessor returns ColumnTransformer."""
        config = Config()
        pipeline = Pipeline(config)

        preprocessor = pipeline._create_preprocessor()

        assert hasattr(preprocessor, 'fit_transform')
        assert hasattr(preprocessor, 'fit')
        assert hasattr(preprocessor, 'transform')

    def test_load_and_preprocess_data_returns_correct_shapes(self):
        """Test that load_and_preprocess_data returns correct shapes."""
        config = Config(dataset_n_samples=100, dataset_n_features=10)
        pipeline = Pipeline(config)

        X_train, X_test, y_train, y_test = pipeline.load_and_preprocess_data()

        # Check shapes
        assert X_train.shape[0] + X_test.shape[0] == 100
        assert X_train.shape[1] == 10
        assert X_test.shape[1] == 10
        assert len(y_train) + len(y_test) == 100

    def test_preprocessing_produces_finite_values(self):
        """Test that preprocessing produces finite values (no NaN/Inf)."""
        config = Config()
        pipeline = Pipeline(config)

        X_train, X_test, y_train, y_test = pipeline.load_and_preprocess_data()

        assert np.all(np.isfinite(X_train))
        assert np.all(np.isfinite(X_test))

    def test_train_test_split_is_consistent(self):
        """Test that train/test split is consistent with same seed."""
        config1 = Config(dataset_random_state=42, dataset_test_size=0.2)
        config2 = Config(dataset_random_state=42, dataset_test_size=0.2)

        pipeline1 = Pipeline(config1)
        pipeline2 = Pipeline(config2)

        X_tr1, X_te1, y_tr1, y_te1 = pipeline1.load_and_preprocess_data()
        X_tr2, X_te2, y_tr2, y_te2 = pipeline2.load_and_preprocess_data()

        np.testing.assert_array_equal(y_tr1, y_tr2)
        np.testing.assert_array_equal(y_te1, y_te2)


class TestPipelineMetrics:
    """Test metric computation."""

    def test_compute_metrics_returns_all_metrics(self):
        """Test that compute_metrics returns all expected metrics."""
        config = Config()
        pipeline = Pipeline(config)

        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 1, 1, 1, 0, 0])

        metrics = pipeline._compute_metrics(y_true, y_pred)

        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics

    def test_compute_metrics_perfect_predictions(self):
        """Test metrics with perfect predictions."""
        config = Config()
        pipeline = Pipeline(config)

        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1])

        metrics = pipeline._compute_metrics(y_true, y_pred)

        assert metrics['accuracy'] == 1.0

    def test_compute_metrics_zero_division_handling(self):
        """Test that metrics handle zero division gracefully."""
        config = Config()
        pipeline = Pipeline(config)

        y_true = np.array([0, 0, 0, 0])
        y_pred = np.array([0, 0, 0, 0])

        metrics = pipeline._compute_metrics(y_true, y_pred)

        # Should not raise exception
        assert np.all(np.isfinite(list(metrics.values())))


class TestPipelineTraining:
    """Test model training."""

    def test_train_logistic_regression_returns_model_and_metrics(self):
        """Test that train_logistic_regression returns model and metrics."""
        config = Config(dataset_n_samples=50, dataset_n_features=5)
        pipeline = Pipeline(config)

        X_train, X_test, y_train, y_test = pipeline.load_and_preprocess_data()

        model, metrics = pipeline.train_logistic_regression(X_train, X_test, y_train, y_test)

        assert model is not None
        assert isinstance(metrics, dict)
        assert len(metrics) == 4  # accuracy, precision, recall, f1

    def test_train_random_forest_returns_model_and_metrics(self):
        """Test that train_random_forest returns model and metrics."""
        config = Config(dataset_n_samples=50, dataset_n_features=5)
        pipeline = Pipeline(config)

        X_train, X_test, y_train, y_test = pipeline.load_and_preprocess_data()

        model, metrics = pipeline.train_random_forest(X_train, X_test, y_train, y_test)

        assert model is not None
        assert isinstance(metrics, dict)
        assert len(metrics) == 4

    def test_train_gradient_boosting_returns_model_and_metrics(self):
        """Test that train_gradient_boosting returns model and metrics."""
        config = Config(dataset_n_samples=50, dataset_n_features=5)
        pipeline = Pipeline(config)

        X_train, X_test, y_train, y_test = pipeline.load_and_preprocess_data()

        model, metrics = pipeline.train_gradient_boosting(X_train, X_test, y_train, y_test)

        assert model is not None
        assert isinstance(metrics, dict)
        assert len(metrics) == 4

    def test_trained_model_can_make_predictions(self):
        """Test that trained models can make predictions."""
        config = Config(dataset_n_samples=50, dataset_n_features=5)
        pipeline = Pipeline(config)

        X_train, X_test, y_train, y_test = pipeline.load_and_preprocess_data()

        model, _ = pipeline.train_logistic_regression(X_train, X_test, y_train, y_test)

        predictions = model.predict(X_test)

        assert len(predictions) == len(y_test)
        assert np.all(np.isin(predictions, np.unique(y_test)))


class TestPipelineIntegration:
    """Integration tests for complete pipeline."""

    def test_train_and_evaluate_returns_all_models(self):
        """Test that train_and_evaluate returns results for all models."""
        config = Config(dataset_n_samples=50, dataset_n_features=5)
        pipeline = Pipeline(config)

        results = pipeline.train_and_evaluate()

        assert 'logistic_regression' in results
        assert 'random_forest' in results
        assert 'gradient_boosting' in results

    def test_train_and_evaluate_all_metrics_present(self):
        """Test that all metrics are computed for each model."""
        config = Config(dataset_n_samples=50, dataset_n_features=5)
        pipeline = Pipeline(config)

        results = pipeline.train_and_evaluate()

        for model_name, metrics in results.items():
            assert 'accuracy' in metrics
            assert 'precision' in metrics
            assert 'recall' in metrics
            assert 'f1' in metrics

    def test_train_and_evaluate_metrics_are_numeric(self):
        """Test that all metrics are numeric values."""
        config = Config(dataset_n_samples=50, dataset_n_features=5)
        pipeline = Pipeline(config)

        results = pipeline.train_and_evaluate()

        for model_name, metrics in results.items():
            for metric_name, value in metrics.items():
                assert isinstance(value, (int, float, np.number))
                assert np.isfinite(value)

    def test_pipeline_reproducibility(self):
        """Test that pipeline produces reproducible results."""
        config1 = Config(dataset_n_samples=50, dataset_n_features=5, dataset_random_state=42)
        config2 = Config(dataset_n_samples=50, dataset_n_features=5, dataset_random_state=42)

        pipeline1 = Pipeline(config1)
        pipeline2 = Pipeline(config2)

        # Both pipelines should have same data after loading
        X1, _, y1, _ = pipeline1.load_and_preprocess_data()
        X2, _, y2, _ = pipeline2.load_and_preprocess_data()

        np.testing.assert_array_equal(y1, y2)


class TestPipelineUtilities:
    """Test utility methods."""

    def test_get_data_info_returns_dict(self):
        """Test that get_data_info returns dictionary."""
        config = Config(dataset_n_samples=100, dataset_n_features=10)
        pipeline = Pipeline(config)

        pipeline.load_and_preprocess_data()
        info = pipeline.get_data_info()

        assert isinstance(info, dict)
        assert 'n_train_samples' in info
        assert 'n_test_samples' in info
        assert 'n_features' in info
        assert 'n_classes' in info

    def test_get_data_info_before_loading(self):
        """Test that get_data_info returns empty dict before loading."""
        config = Config()
        pipeline = Pipeline(config)

        info = pipeline.get_data_info()

        assert info == {}

    def test_summary_returns_string(self):
        """Test that summary method returns string."""
        config = Config()
        pipeline = Pipeline(config)

        summary = pipeline.summary()

        assert isinstance(summary, str)
        assert 'ML Pipeline Summary' in summary

    def test_cross_validate_model_returns_cv_scores(self):
        """Test that cross_validate_model returns CV scores."""
        config = Config(dataset_n_samples=50, dataset_n_features=5, cv_folds=3)
        pipeline = Pipeline(config)

        X, y = pipeline._load_data()

        from sklearn.linear_model import LogisticRegression
        results = pipeline.cross_validate_model(
            LogisticRegression,
            config.logistic_regression_params,
            X, y
        )

        # Should have mean and std for each metric
        assert len(results) == len(config.scoring_metrics) * 2


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_pipeline_with_small_dataset(self):
        """Test pipeline with very small dataset."""
        config = Config(dataset_n_samples=20, dataset_n_features=3)
        pipeline = Pipeline(config)

        results = pipeline.train_and_evaluate()

        assert len(results) == 3

    def test_pipeline_with_single_feature(self):
        """Test pipeline with single feature."""
        config = Config(dataset_n_samples=50, dataset_n_features=1)
        pipeline = Pipeline(config)

        results = pipeline.train_and_evaluate()

        assert len(results) == 3

    def test_pipeline_with_binary_classification(self):
        """Test pipeline with binary classification."""
        config = Config(dataset_n_samples=50, dataset_n_classes=2)
        pipeline = Pipeline(config)

        results = pipeline.train_and_evaluate()

        assert len(results) == 3

    def test_preprocessing_stability(self):
        """Test that preprocessing is stable across calls."""
        config = Config(dataset_n_samples=50, dataset_n_features=5)
        pipeline = Pipeline(config)

        X_train, X_test, _, _ = pipeline.load_and_preprocess_data()

        # Apply preprocessor again to same data
        X_test_again = pipeline.preprocessor.transform(X_test)

        np.testing.assert_array_almost_equal(X_test, X_test_again)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
