"""
ML Pipeline Module
==================

Complete end-to-end machine learning pipeline with data loading,
preprocessing, model training, evaluation, and MLflow logging.
"""

from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
import mlflow
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline as SklearnPipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from config import Config


class Pipeline:
    """End-to-end ML pipeline for training and evaluating models.

    This class handles:
    - Data loading and generation
    - Data preprocessing with ColumnTransformer
    - Model training with multiple algorithms
    - Cross-validation
    - Evaluation and metric computation
    - MLflow experiment tracking

    Attributes:
        config: Configuration object with all parameters
        X_train, X_test: Training and test feature matrices
        y_train, y_test: Training and test target arrays
    """

    def __init__(self, config: Config = None):
        """Initialize the pipeline.

        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or Config()
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.preprocessor = None

        # Set up MLflow
        if self.config.mlflow_autolog and self.config.mlflow_autolog_sklearn:
            mlflow.sklearn.autolog()

    def load_and_preprocess_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Load data and apply preprocessing.

        Returns:
            Tuple of (X_train_processed, X_test_processed, y_train, y_test)
        """
        # Load data
        X, y = self._load_data()

        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y,
            test_size=self.config.dataset_test_size,
            random_state=self.config.dataset_random_state,
            stratify=y
        )

        # Create preprocessor
        self.preprocessor = self._create_preprocessor()

        # Apply preprocessing
        X_train_processed = self.preprocessor.fit_transform(self.X_train)
        X_test_processed = self.preprocessor.transform(self.X_test)

        return X_train_processed, X_test_processed, self.y_train, self.y_test

    def _load_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load synthetic dataset.

        Returns:
            Tuple of (features, target)
        """
        X, y = make_classification(
            n_samples=self.config.dataset_n_samples,
            n_features=self.config.dataset_n_features,
            n_informative=self.config.dataset_n_informative,
            n_redundant=self.config.dataset_n_redundant,
            n_classes=self.config.dataset_n_classes,
            random_state=self.config.dataset_random_state
        )
        return X, y

    def _create_preprocessor(self) -> ColumnTransformer:
        """Create preprocessing pipeline with ColumnTransformer.

        Returns:
            Fitted ColumnTransformer
        """
        # For synthetic data, all features are numeric
        numeric_transformer = SklearnPipeline([
            ('imputer', SimpleImputer(strategy=self.config.numeric_impute_strategy)),
            ('scaler', StandardScaler()) if self.config.scale_numeric else ('identity', 'passthrough')
        ])

        # Create ColumnTransformer
        # In this case, all features are numeric
        preprocessor = ColumnTransformer([
            ('num', numeric_transformer, self.config.numeric_features)
        ], remainder='passthrough')

        return preprocessor

    def train_logistic_regression(
        self,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray
    ) -> Tuple[LogisticRegression, Dict[str, float]]:
        """Train Logistic Regression model.

        Args:
            X_train, X_test: Processed feature matrices
            y_train, y_test: Target arrays

        Returns:
            Tuple of (trained_model, metrics_dict)
        """
        with mlflow.start_run(run_name='logistic_regression'):
            model = LogisticRegression(**self.config.logistic_regression_params)
            model.fit(X_train, y_train)

            # Get predictions
            y_pred = model.predict(X_test)

            # Compute metrics
            metrics = self._compute_metrics(y_test, y_pred)

            # Log metrics to MLflow
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)

            # Log model
            mlflow.sklearn.log_model(model, 'model')

            return model, metrics

    def train_random_forest(
        self,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray
    ) -> Tuple[RandomForestClassifier, Dict[str, float]]:
        """Train Random Forest model.

        Args:
            X_train, X_test: Processed feature matrices
            y_train, y_test: Target arrays

        Returns:
            Tuple of (trained_model, metrics_dict)
        """
        with mlflow.start_run(run_name='random_forest'):
            model = RandomForestClassifier(**self.config.random_forest_params)
            model.fit(X_train, y_train)

            # Get predictions
            y_pred = model.predict(X_test)

            # Compute metrics
            metrics = self._compute_metrics(y_test, y_pred)

            # Log metrics to MLflow
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)

            # Log model
            mlflow.sklearn.log_model(model, 'model')

            return model, metrics

    def train_gradient_boosting(
        self,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray
    ) -> Tuple[GradientBoostingClassifier, Dict[str, float]]:
        """Train Gradient Boosting model.

        Args:
            X_train, X_test: Processed feature matrices
            y_train, y_test: Target arrays

        Returns:
            Tuple of (trained_model, metrics_dict)
        """
        with mlflow.start_run(run_name='gradient_boosting'):
            model = GradientBoostingClassifier(**self.config.gradient_boosting_params)
            model.fit(X_train, y_train)

            # Get predictions
            y_pred = model.predict(X_test)

            # Compute metrics
            metrics = self._compute_metrics(y_test, y_pred)

            # Log metrics to MLflow
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)

            # Log model
            mlflow.sklearn.log_model(model, 'model')

            return model, metrics

    def _compute_metrics(
        self,
        y_test: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """Compute evaluation metrics.

        Args:
            y_test: True labels
            y_pred: Predicted labels

        Returns:
            Dictionary of metrics
        """
        # Determine if binary or multiclass
        n_classes = len(np.unique(y_test))
        average = 'binary' if n_classes == 2 else 'weighted'

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average=average, zero_division=0),
            'recall': recall_score(y_test, y_pred, average=average, zero_division=0),
            'f1': f1_score(y_test, y_pred, average=average, zero_division=0)
        }

        return metrics

    def train_and_evaluate(self) -> Dict[str, Dict[str, float]]:
        """Load data, train all models, and return results.

        Returns:
            Dictionary mapping model names to metrics dictionaries
        """
        mlflow.set_experiment(self.config.mlflow_experiment_name)

        # Load and preprocess data
        X_train, X_test, y_train, y_test = self.load_and_preprocess_data()

        results = {}

        # Train Logistic Regression
        print("Training Logistic Regression...")
        model_lr, metrics_lr = self.train_logistic_regression(X_train, X_test, y_train, y_test)
        results['logistic_regression'] = metrics_lr

        # Train Random Forest
        print("Training Random Forest...")
        model_rf, metrics_rf = self.train_random_forest(X_train, X_test, y_train, y_test)
        results['random_forest'] = metrics_rf

        # Train Gradient Boosting
        print("Training Gradient Boosting...")
        model_gb, metrics_gb = self.train_gradient_boosting(X_train, X_test, y_train, y_test)
        results['gradient_boosting'] = metrics_gb

        return results

    def cross_validate_model(
        self,
        model_class,
        model_params: Dict[str, Any],
        X: np.ndarray,
        y: np.ndarray
    ) -> Dict[str, float]:
        """Perform k-fold cross-validation.

        Args:
            model_class: Model class to instantiate
            model_params: Parameters for the model
            X: Feature matrix
            y: Target array

        Returns:
            Dictionary with CV mean and std for each metric
        """
        results = {}

        for metric in self.config.scoring_metrics:
            scores = cross_val_score(
                model_class(**model_params),
                X, y,
                cv=self.config.cv_folds,
                scoring=metric
            )
            results[f'{metric}_mean'] = scores.mean()
            results[f'{metric}_std'] = scores.std()

        return results

    def get_data_info(self) -> Dict[str, Any]:
        """Get information about the loaded data.

        Returns:
            Dictionary with data statistics
        """
        if self.X_train is None:
            return {}

        return {
            'n_train_samples': len(self.X_train),
            'n_test_samples': len(self.X_test),
            'n_features': self.X_train.shape[1],
            'n_classes': len(np.unique(self.y_train)),
            'class_distribution': dict(zip(*np.unique(self.y_train, return_counts=True)))
        }

    def summary(self) -> str:
        """Print pipeline summary.

        Returns:
            Summary string
        """
        summary = f"""
        ML Pipeline Summary
        ===================
        Dataset: {self.config.dataset_n_samples} samples, {self.config.dataset_n_features} features
        Classes: {self.config.dataset_n_classes}
        Test Size: {self.config.dataset_test_size:.2%}
        CV Folds: {self.config.cv_folds}

        Models:
        - Logistic Regression
        - Random Forest (n_estimators={self.config.random_forest_n_estimators})
        - Gradient Boosting (n_estimators={self.config.gradient_boosting_n_estimators})

        MLflow: {self.config.mlflow_experiment_name}
        """
        return summary


if __name__ == "__main__":
    # Example usage
    config = Config()
    pipeline = Pipeline(config)

    print(pipeline.summary())

    # Train and evaluate
    results = pipeline.train_and_evaluate()

    # Print results
    print("\nResults:")
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        for metric_name, value in metrics.items():
            print(f"  {metric_name}: {value:.4f}")
