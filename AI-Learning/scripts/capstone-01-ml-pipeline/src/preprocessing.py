"""
Preprocessing Module
====================

Handles all data transformation steps between raw ingestion and model training.
Implements a configurable pipeline of preprocessing steps including missing value
imputation, feature encoding, scaling, feature selection, and train/test splitting.

Design:
- Each transformation is a method that can be called independently or chained
- Fitted transformers are stored for consistent application to new data
- Supports both numerical and categorical features
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class PreprocessingConfig:
    """Configuration for preprocessing steps.

    Attributes
    ----------
    numeric_strategy : str
        Imputation strategy for numeric columns ('mean', 'median', 'zero').
    categorical_strategy : str
        Encoding strategy for categorical columns ('onehot', 'label', 'target').
    scaling_method : str
        Feature scaling method ('standard', 'minmax', 'robust', 'none').
    test_size : float
        Fraction of data reserved for testing.
    random_state : int
        Random seed for reproducibility.
    feature_selection_k : int or None
        If set, select top-k features by importance.
    """

    numeric_strategy: str = "median"
    categorical_strategy: str = "onehot"
    scaling_method: str = "standard"
    test_size: float = 0.2
    random_state: int = 42
    feature_selection_k: Optional[int] = None


class Preprocessor:
    """Transform raw data into model-ready features.

    Parameters
    ----------
    config : PreprocessingConfig
        Configuration controlling each preprocessing step.
    """

    def __init__(self, config: Optional[PreprocessingConfig] = None) -> None:
        self.config = config or PreprocessingConfig()
        self._fitted: bool = False
        self._transformers: Dict[str, Any] = {}

    def fit(self, df: pd.DataFrame, target_column: str) -> "Preprocessor":
        """Fit all preprocessing transformers on the training data.

        Parameters
        ----------
        df : pd.DataFrame
            Training data including the target column.
        target_column : str
            Name of the target variable column.

        Returns
        -------
        Preprocessor
            Self, for method chaining.
        """
        raise NotImplementedError

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply fitted transformations to a DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            Data to transform (must have same schema as fit data).

        Returns
        -------
        pd.DataFrame
            Transformed feature matrix.

        Raises
        ------
        RuntimeError
            If called before fit().
        """
        raise NotImplementedError

    def fit_transform(
        self, df: pd.DataFrame, target_column: str
    ) -> pd.DataFrame:
        """Convenience method: fit and transform in one call.

        Parameters
        ----------
        df : pd.DataFrame
            Training data.
        target_column : str
            Target column name.

        Returns
        -------
        pd.DataFrame
            Transformed feature matrix.
        """
        return self.fit(df, target_column).transform(df)

    def split(
        self, df: pd.DataFrame, target_column: str
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Split data into train and test sets.

        Parameters
        ----------
        df : pd.DataFrame
            Full dataset.
        target_column : str
            Name of the target column.

        Returns
        -------
        tuple
            (X_train, X_test, y_train, y_test)
        """
        raise NotImplementedError

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values using the configured strategy.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame potentially containing missing values.

        Returns
        -------
        pd.DataFrame
            DataFrame with missing values imputed.
        """
        raise NotImplementedError

    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features using the configured strategy.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with categorical columns.

        Returns
        -------
        pd.DataFrame
            DataFrame with encoded categorical features.
        """
        raise NotImplementedError

    def scale_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features using the configured method.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with numerical features.

        Returns
        -------
        pd.DataFrame
            DataFrame with scaled features.
        """
        raise NotImplementedError
