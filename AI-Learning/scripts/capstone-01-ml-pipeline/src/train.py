"""
Training Module
===============

Handles model training with support for multiple algorithms, hyperparameter
tuning, cross-validation, and MLflow experiment tracking.

Supported model families:
- Scikit-learn classifiers and regressors
- XGBoost gradient boosted trees
- Custom model wrappers implementing the sklearn estimator interface

All training runs are logged to MLflow with parameters, metrics, and artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd


class ModelType(Enum):
    """Supported model types."""

    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    LOGISTIC_REGRESSION = "logistic_regression"
    LINEAR_REGRESSION = "linear_regression"
    XGBOOST = "xgboost"
    SVM = "svm"


class TaskType(Enum):
    """ML task type."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"


@dataclass
class TrainingConfig:
    """Configuration for model training.

    Attributes
    ----------
    model_type : ModelType
        Which model algorithm to use.
    task_type : TaskType
        Whether this is classification or regression.
    hyperparams : dict
        Model-specific hyperparameters.
    cv_folds : int
        Number of cross-validation folds.
    enable_tuning : bool
        Whether to run hyperparameter search.
    tuning_n_iter : int
        Number of iterations for randomized search.
    mlflow_experiment : str
        MLflow experiment name for tracking.
    random_state : int
        Random seed for reproducibility.
    """

    model_type: ModelType = ModelType.RANDOM_FOREST
    task_type: TaskType = TaskType.CLASSIFICATION
    hyperparams: Dict[str, Any] = None
    cv_folds: int = 5
    enable_tuning: bool = False
    tuning_n_iter: int = 50
    mlflow_experiment: str = "ml-pipeline"
    random_state: int = 42

    def __post_init__(self) -> None:
        if self.hyperparams is None:
            self.hyperparams = {}


class Trainer:
    """Train and tune ML models with experiment tracking.

    Parameters
    ----------
    config : TrainingConfig
        Training configuration.
    """

    def __init__(self, config: Optional[TrainingConfig] = None) -> None:
        self.config = config or TrainingConfig()
        self.model: Optional[Any] = None
        self.best_params: Optional[Dict[str, Any]] = None
        self.cv_results: Optional[Dict[str, Any]] = None

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
    ) -> Any:
        """Train a model on the provided data.

        Parameters
        ----------
        X_train : pd.DataFrame
            Training feature matrix.
        y_train : pd.Series
            Training target values.

        Returns
        -------
        Any
            The fitted model object (sklearn-compatible estimator).
        """
        raise NotImplementedError

    def tune_hyperparameters(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        param_distributions: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run hyperparameter tuning via randomized search with cross-validation.

        Parameters
        ----------
        X_train : pd.DataFrame
            Training feature matrix.
        y_train : pd.Series
            Training target values.
        param_distributions : dict, optional
            Parameter distributions for search. Uses defaults if not provided.

        Returns
        -------
        dict
            Best parameters found during search.
        """
        raise NotImplementedError

    def cross_validate(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
    ) -> Dict[str, List[float]]:
        """Run cross-validation and return per-fold metrics.

        Parameters
        ----------
        X_train : pd.DataFrame
            Training features.
        y_train : pd.Series
            Training targets.

        Returns
        -------
        dict
            Per-fold scores for each metric.
        """
        raise NotImplementedError

    def save_model(self, path: Union[str, Path]) -> Path:
        """Persist the trained model to disk.

        Parameters
        ----------
        path : str or Path
            Directory to save the model artifacts.

        Returns
        -------
        Path
            Path to the saved model file.

        Raises
        ------
        RuntimeError
            If no model has been trained yet.
        """
        raise NotImplementedError

    def log_to_mlflow(self, metrics: Dict[str, float]) -> str:
        """Log training run to MLflow.

        Logs parameters, metrics, and the model artifact.

        Parameters
        ----------
        metrics : dict
            Evaluation metrics to log.

        Returns
        -------
        str
            The MLflow run ID.
        """
        raise NotImplementedError
