"""
Pipeline Tests
==============

Unit tests for the ML pipeline components. Uses pytest fixtures to provide
test data and configurations. Tests cover individual stages as well as the
full pipeline orchestration.
"""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.data_ingestion import DataIngester, DataSource
from src.evaluate import Evaluator, EvaluationReport
from src.pipeline import MLPipeline, PipelineConfig
from src.preprocessing import Preprocessor, PreprocessingConfig
from src.train import ModelType, Trainer, TrainingConfig


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a small sample DataFrame for testing."""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "feature_a": np.random.randn(100),
            "feature_b": np.random.choice(["cat", "dog", "bird"], 100),
            "feature_c": np.random.randint(0, 100, 100),
            "target": np.random.choice([0, 1], 100),
        }
    )


@pytest.fixture
def pipeline_config() -> PipelineConfig:
    """Create a default pipeline configuration for testing."""
    return PipelineConfig(
        name="test-pipeline",
        data_source=DataSource.CSV,
        data_path="tests/fixtures/test_data.csv",
        target_column="target",
        model_type=ModelType.RANDOM_FOREST,
    )


# ---------------------------------------------------------------------------
# Data Ingestion Tests
# ---------------------------------------------------------------------------


class TestDataIngester:
    """Tests for the DataIngester class."""

    def test_init_sets_source_type(self) -> None:
        """DataIngester should store the configured source type."""
        ingester = DataIngester(source_type=DataSource.CSV)
        assert ingester.source_type == DataSource.CSV

    def test_validate_source_raises_not_implemented(self) -> None:
        """validate_source should raise NotImplementedError until implemented."""
        ingester = DataIngester(source_type=DataSource.CSV)
        with pytest.raises(NotImplementedError):
            ingester.validate_source()

    def test_load_raises_not_implemented(self) -> None:
        """load should raise NotImplementedError until implemented."""
        ingester = DataIngester(source_type=DataSource.CSV)
        with pytest.raises(NotImplementedError):
            ingester.load()


# ---------------------------------------------------------------------------
# Preprocessing Tests
# ---------------------------------------------------------------------------


class TestPreprocessor:
    """Tests for the Preprocessor class."""

    def test_init_with_default_config(self) -> None:
        """Preprocessor should initialize with default config when none provided."""
        preprocessor = Preprocessor()
        assert preprocessor.config.test_size == 0.2
        assert preprocessor.config.scaling_method == "standard"

    def test_fit_raises_not_implemented(self, sample_dataframe: pd.DataFrame) -> None:
        """fit should raise NotImplementedError until implemented."""
        preprocessor = Preprocessor()
        with pytest.raises(NotImplementedError):
            preprocessor.fit(sample_dataframe, target_column="target")

    def test_transform_before_fit_raises(self, sample_dataframe: pd.DataFrame) -> None:
        """transform should raise NotImplementedError (or RuntimeError once implemented)."""
        preprocessor = Preprocessor()
        with pytest.raises((NotImplementedError, RuntimeError)):
            preprocessor.transform(sample_dataframe)


# ---------------------------------------------------------------------------
# Trainer Tests
# ---------------------------------------------------------------------------


class TestTrainer:
    """Tests for the Trainer class."""

    def test_init_with_default_config(self) -> None:
        """Trainer should initialize with sensible defaults."""
        trainer = Trainer()
        assert trainer.config.model_type == ModelType.RANDOM_FOREST
        assert trainer.model is None

    def test_train_raises_not_implemented(self, sample_dataframe: pd.DataFrame) -> None:
        """train should raise NotImplementedError until implemented."""
        trainer = Trainer()
        X = sample_dataframe.drop(columns=["target"])
        y = sample_dataframe["target"]
        with pytest.raises(NotImplementedError):
            trainer.train(X, y)


# ---------------------------------------------------------------------------
# Evaluator Tests
# ---------------------------------------------------------------------------


class TestEvaluator:
    """Tests for the Evaluator class."""

    def test_init_sets_task_type(self) -> None:
        """Evaluator should store the task type."""
        evaluator = Evaluator(task_type="classification")
        assert evaluator.task_type == "classification"

    def test_evaluate_raises_not_implemented(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """evaluate should raise NotImplementedError until implemented."""
        evaluator = Evaluator()
        mock_model = MagicMock()
        X = sample_dataframe.drop(columns=["target"])
        y = sample_dataframe["target"]
        with pytest.raises(NotImplementedError):
            evaluator.evaluate(mock_model, X, y)


# ---------------------------------------------------------------------------
# Pipeline Integration Tests
# ---------------------------------------------------------------------------


class TestMLPipeline:
    """Tests for the MLPipeline orchestrator."""

    def test_init_with_config(self, pipeline_config: PipelineConfig) -> None:
        """Pipeline should store the provided configuration."""
        pipeline = MLPipeline(config=pipeline_config)
        assert pipeline.config.name == "test-pipeline"

    def test_from_yaml_raises_not_implemented(self) -> None:
        """from_yaml should raise NotImplementedError until implemented."""
        with pytest.raises(NotImplementedError):
            MLPipeline.from_yaml("config.yaml")

    def test_run_raises_not_implemented(
        self, pipeline_config: PipelineConfig
    ) -> None:
        """run should raise NotImplementedError until implemented."""
        pipeline = MLPipeline(config=pipeline_config)
        with pytest.raises(NotImplementedError):
            pipeline.run()

    def test_get_artifact_raises_key_error(
        self, pipeline_config: PipelineConfig
    ) -> None:
        """get_artifact should raise KeyError for missing artifacts."""
        pipeline = MLPipeline(config=pipeline_config)
        with pytest.raises((NotImplementedError, KeyError)):
            pipeline.get_artifact("nonexistent")
