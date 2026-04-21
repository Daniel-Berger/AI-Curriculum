"""
ML Pipeline Orchestrator
========================

Chains together all pipeline stages (ingestion, preprocessing, training,
evaluation) into a configurable end-to-end workflow. Supports running the
full pipeline or individual stages, with configuration via YAML files.

The pipeline manages:
- Stage sequencing and dependency resolution
- Configuration loading and validation
- Artifact passing between stages
- Error handling and graceful degradation
- MLflow experiment lifecycle
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from .data_ingestion import DataIngester, DataSource
from .evaluate import Evaluator, EvaluationReport
from .preprocessing import Preprocessor, PreprocessingConfig
from .train import ModelType, Trainer, TrainingConfig


@dataclass
class PipelineConfig:
    """Top-level configuration for the ML pipeline.

    Attributes
    ----------
    name : str
        Pipeline run name / identifier.
    data_source : DataSource
        Type of data source.
    data_path : str
        Path or URI to the data.
    target_column : str
        Name of the target variable.
    model_type : ModelType
        Model algorithm to use.
    output_dir : str
        Directory for all pipeline outputs.
    preprocessing : PreprocessingConfig
        Preprocessing stage configuration.
    training : TrainingConfig
        Training stage configuration.
    """

    name: str = "default-pipeline"
    data_source: DataSource = DataSource.CSV
    data_path: str = ""
    target_column: str = "target"
    model_type: ModelType = ModelType.RANDOM_FOREST
    output_dir: str = "outputs"
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)


class MLPipeline:
    """Orchestrate the full ML pipeline from data to evaluation.

    Parameters
    ----------
    config : PipelineConfig
        Full pipeline configuration.
    """

    def __init__(self, config: Optional[PipelineConfig] = None) -> None:
        self.config = config or PipelineConfig()
        self._ingester: Optional[DataIngester] = None
        self._preprocessor: Optional[Preprocessor] = None
        self._trainer: Optional[Trainer] = None
        self._evaluator: Optional[Evaluator] = None
        self._artifacts: Dict[str, Any] = {}

    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> "MLPipeline":
        """Create a pipeline from a YAML configuration file.

        Parameters
        ----------
        config_path : str or Path
            Path to the YAML config file.

        Returns
        -------
        MLPipeline
            Configured pipeline instance.
        """
        raise NotImplementedError

    def run(self) -> EvaluationReport:
        """Execute the full pipeline end-to-end.

        Runs: ingest -> preprocess -> train -> evaluate.

        Returns
        -------
        EvaluationReport
            Final evaluation results.
        """
        raise NotImplementedError

    def ingest(self) -> pd.DataFrame:
        """Run the data ingestion stage.

        Returns
        -------
        pd.DataFrame
            Raw ingested data.
        """
        raise NotImplementedError

    def preprocess(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run the preprocessing stage.

        Parameters
        ----------
        df : pd.DataFrame
            Raw data from ingestion.

        Returns
        -------
        dict
            Contains 'X_train', 'X_test', 'y_train', 'y_test' DataFrames/Series.
        """
        raise NotImplementedError

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        """Run the training stage.

        Parameters
        ----------
        X_train : pd.DataFrame
            Training features.
        y_train : pd.Series
            Training targets.

        Returns
        -------
        Any
            Trained model object.
        """
        raise NotImplementedError

    def evaluate(
        self, model: Any, X_test: pd.DataFrame, y_test: pd.Series
    ) -> EvaluationReport:
        """Run the evaluation stage.

        Parameters
        ----------
        model : Any
            Trained model.
        X_test : pd.DataFrame
            Test features.
        y_test : pd.Series
            Test targets.

        Returns
        -------
        EvaluationReport
            Evaluation results.
        """
        raise NotImplementedError

    def get_artifact(self, name: str) -> Any:
        """Retrieve an artifact produced by a pipeline stage.

        Parameters
        ----------
        name : str
            Artifact name (e.g., 'raw_data', 'model', 'report').

        Returns
        -------
        Any
            The requested artifact.

        Raises
        ------
        KeyError
            If the artifact has not been produced yet.
        """
        raise NotImplementedError
