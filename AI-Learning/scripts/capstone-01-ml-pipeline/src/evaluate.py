"""
Evaluation Module
=================

Comprehensive model evaluation with support for classification and regression
metrics, visualization generation, feature importance analysis, and model
comparison reports.

Produces:
- Standard metrics (accuracy, precision, recall, F1, AUC, RMSE, MAE, R2)
- Confusion matrices and ROC curves
- Feature importance plots
- Model comparison tables
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


@dataclass
class EvaluationReport:
    """Container for evaluation results.

    Attributes
    ----------
    metrics : dict
        Computed metric values.
    confusion_matrix : np.ndarray or None
        Confusion matrix for classification tasks.
    feature_importance : dict or None
        Feature name to importance score mapping.
    predictions : np.ndarray
        Model predictions on the evaluation set.
    """

    metrics: Dict[str, float]
    confusion_matrix: Optional[np.ndarray] = None
    feature_importance: Optional[Dict[str, float]] = None
    predictions: Optional[np.ndarray] = None


class Evaluator:
    """Evaluate trained models and generate reports.

    Parameters
    ----------
    task_type : str
        Either 'classification' or 'regression'.
    output_dir : str or Path, optional
        Directory for saving evaluation artifacts (plots, reports).
    """

    def __init__(
        self,
        task_type: str = "classification",
        output_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        self.task_type = task_type
        self.output_dir = Path(output_dir) if output_dir else Path("reports")

    def evaluate(
        self,
        model: Any,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> EvaluationReport:
        """Run full evaluation on the test set.

        Parameters
        ----------
        model : Any
            Trained sklearn-compatible estimator.
        X_test : pd.DataFrame
            Test feature matrix.
        y_test : pd.Series
            True test labels / values.

        Returns
        -------
        EvaluationReport
            Complete evaluation results.
        """
        raise NotImplementedError

    def compute_classification_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
    ) -> Dict[str, float]:
        """Compute classification-specific metrics.

        Returns accuracy, precision, recall, F1 (macro and weighted), and AUC
        if probability predictions are available.

        Parameters
        ----------
        y_true : np.ndarray
            Ground truth labels.
        y_pred : np.ndarray
            Predicted labels.
        y_proba : np.ndarray, optional
            Predicted probabilities for AUC computation.

        Returns
        -------
        dict
            Metric name to value mapping.
        """
        raise NotImplementedError

    def compute_regression_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict[str, float]:
        """Compute regression-specific metrics.

        Returns RMSE, MAE, R2, and explained variance.

        Parameters
        ----------
        y_true : np.ndarray
            True target values.
        y_pred : np.ndarray
            Predicted values.

        Returns
        -------
        dict
            Metric name to value mapping.
        """
        raise NotImplementedError

    def plot_confusion_matrix(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> Path:
        """Generate and save a confusion matrix plot.

        Parameters
        ----------
        y_true : np.ndarray
            Ground truth labels.
        y_pred : np.ndarray
            Predicted labels.

        Returns
        -------
        Path
            Path to the saved plot image.
        """
        raise NotImplementedError

    def plot_feature_importance(
        self, model: Any, feature_names: List[str], top_k: int = 20
    ) -> Path:
        """Generate and save a feature importance bar chart.

        Parameters
        ----------
        model : Any
            Trained model with feature_importances_ attribute.
        feature_names : list of str
            Feature names corresponding to the model's input.
        top_k : int
            Number of top features to display.

        Returns
        -------
        Path
            Path to the saved plot image.
        """
        raise NotImplementedError

    def compare_models(
        self, reports: Dict[str, EvaluationReport]
    ) -> pd.DataFrame:
        """Compare multiple model evaluation reports side by side.

        Parameters
        ----------
        reports : dict
            Mapping of model name to EvaluationReport.

        Returns
        -------
        pd.DataFrame
            Comparison table with models as rows, metrics as columns.
        """
        raise NotImplementedError
