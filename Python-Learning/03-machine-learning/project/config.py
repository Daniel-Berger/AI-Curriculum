"""
Configuration Module for ML Pipeline Project
==============================================

Defines all configuration parameters for the pipeline using dataclasses.
This provides a single source of truth for all settings.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Config:
    """Configuration for the ML pipeline project.

    Attributes:
        dataset: Dataset generation parameters
        features: Feature configuration
        preprocessing: Preprocessing parameters
        models: Model hyperparameters
        training: Training parameters
        mlflow: MLflow configuration
    """

    # =========================================================================
    # DATASET PARAMETERS
    # =========================================================================

    # Dataset generation
    dataset_n_samples: int = 1000
    dataset_n_features: int = 20
    dataset_n_informative: int = 15
    dataset_n_redundant: int = 3
    dataset_n_classes: int = 3
    dataset_random_state: int = 42
    dataset_test_size: float = 0.2

    # =========================================================================
    # FEATURE CONFIGURATION
    # =========================================================================

    # Feature names (generated during pipeline)
    numeric_features: List[str] = None
    categorical_features: List[str] = None

    # =========================================================================
    # PREPROCESSING PARAMETERS
    # =========================================================================

    # Imputation strategy for numeric features
    numeric_impute_strategy: str = "mean"

    # Imputation strategy for categorical features
    categorical_impute_strategy: str = "most_frequent"

    # StandardScaler parameters
    scale_numeric: bool = True

    # OneHotEncoder parameters
    ohe_handle_unknown: str = "ignore"
    ohe_sparse_output: bool = False

    # =========================================================================
    # MODEL HYPERPARAMETERS
    # =========================================================================

    # Logistic Regression
    logistic_regression_params: Dict[str, Any] = None
    # Default values
    logistic_regression_C: float = 1.0
    logistic_regression_max_iter: int = 1000
    logistic_regression_random_state: int = 42

    # Random Forest
    random_forest_params: Dict[str, Any] = None
    # Default values
    random_forest_n_estimators: int = 100
    random_forest_max_depth: int = 10
    random_forest_min_samples_split: int = 5
    random_forest_min_samples_leaf: int = 2
    random_forest_random_state: int = 42

    # Gradient Boosting
    gradient_boosting_params: Dict[str, Any] = None
    # Default values
    gradient_boosting_n_estimators: int = 100
    gradient_boosting_learning_rate: float = 0.1
    gradient_boosting_max_depth: int = 3
    gradient_boosting_min_samples_split: int = 5
    gradient_boosting_min_samples_leaf: int = 2
    gradient_boosting_random_state: int = 42

    # =========================================================================
    # TRAINING PARAMETERS
    # =========================================================================

    # Cross-validation
    cv_folds: int = 5
    cv_shuffle: bool = True
    cv_random_state: int = 42

    # Evaluation
    scoring_metrics: List[str] = None

    # =========================================================================
    # MLFLOW CONFIGURATION
    # =========================================================================

    # Experiment name
    mlflow_experiment_name: str = "ML-Pipeline-Project"

    # Whether to enable autologging
    mlflow_autolog: bool = True

    # Which frameworks to autolog
    mlflow_autolog_sklearn: bool = True

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def __post_init__(self):
        """Initialize default values after dataclass instantiation."""
        # Set default model parameters if not provided
        if self.logistic_regression_params is None:
            self.logistic_regression_params = {
                'C': self.logistic_regression_C,
                'max_iter': self.logistic_regression_max_iter,
                'random_state': self.logistic_regression_random_state
            }

        if self.random_forest_params is None:
            self.random_forest_params = {
                'n_estimators': self.random_forest_n_estimators,
                'max_depth': self.random_forest_max_depth,
                'min_samples_split': self.random_forest_min_samples_split,
                'min_samples_leaf': self.random_forest_min_samples_leaf,
                'random_state': self.random_forest_random_state,
                'n_jobs': -1
            }

        if self.gradient_boosting_params is None:
            self.gradient_boosting_params = {
                'n_estimators': self.gradient_boosting_n_estimators,
                'learning_rate': self.gradient_boosting_learning_rate,
                'max_depth': self.gradient_boosting_max_depth,
                'min_samples_split': self.gradient_boosting_min_samples_split,
                'min_samples_leaf': self.gradient_boosting_min_samples_leaf,
                'random_state': self.gradient_boosting_random_state
            }

        if self.scoring_metrics is None:
            self.scoring_metrics = ['accuracy', 'precision', 'recall', 'f1']

        # Generate feature names if not provided
        if self.numeric_features is None:
            self.numeric_features = [f'numeric_{i}' for i in range(self.dataset_n_features)]
        if self.categorical_features is None:
            self.categorical_features = []

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Dictionary representation of configuration.
        """
        return {
            'dataset': {
                'n_samples': self.dataset_n_samples,
                'n_features': self.dataset_n_features,
                'n_classes': self.dataset_n_classes,
            },
            'models': {
                'logistic_regression': self.logistic_regression_params,
                'random_forest': self.random_forest_params,
                'gradient_boosting': self.gradient_boosting_params,
            },
            'training': {
                'cv_folds': self.cv_folds,
                'test_size': self.dataset_test_size,
            },
            'mlflow': {
                'experiment_name': self.mlflow_experiment_name,
                'autolog': self.mlflow_autolog,
            }
        }

    def __str__(self) -> str:
        """String representation of config."""
        return f"Config(samples={self.dataset_n_samples}, " \
               f"features={self.dataset_n_features}, " \
               f"classes={self.dataset_n_classes})"


# Create default configuration instance
DEFAULT_CONFIG = Config()
