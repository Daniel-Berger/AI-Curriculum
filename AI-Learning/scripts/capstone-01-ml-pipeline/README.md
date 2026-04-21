# Capstone 1: End-to-End ML Pipeline

## Overview

A production-grade machine learning pipeline that handles the full lifecycle from data
ingestion through model evaluation, with experiment tracking, a CLI interface, and
containerized deployment.

## Architecture

```
Data Source --> DataIngester --> Preprocessor --> Trainer --> Evaluator
                                                    |
                                                MLflow Tracking
```

## Components

| Module | Description |
|---|---|
| `src/data_ingestion.py` | Load data from CSV, databases, or APIs |
| `src/preprocessing.py` | Feature engineering, scaling, encoding, train/test split |
| `src/train.py` | Model training with hyperparameter tuning |
| `src/evaluate.py` | Model evaluation with metrics and visualizations |
| `src/pipeline.py` | Orchestrator that chains all stages together |
| `cli.py` | Click-based CLI entry point |

## Features

- **Data Ingestion**: CSV, Parquet, SQL, and API data sources
- **Preprocessing**: Automated feature engineering, missing value handling, encoding
- **Training**: Scikit-learn and XGBoost models with hyperparameter search
- **Evaluation**: Classification/regression metrics, confusion matrices, feature importance
- **Experiment Tracking**: MLflow integration for parameters, metrics, and artifacts
- **CLI Interface**: Click-based CLI for running pipeline stages independently
- **Testing**: Unit tests with pytest and fixtures
- **Containerization**: Multi-stage Dockerfile for lean production images

## Usage

```bash
# Run the full pipeline
python cli.py run --config config.yaml

# Run individual stages
python cli.py ingest --source data/raw/dataset.csv
python cli.py preprocess --input data/raw --output data/processed
python cli.py train --data data/processed --model random_forest
python cli.py evaluate --model models/latest --data data/test

# Docker
docker build -t ml-pipeline .
docker run ml-pipeline run --config config.yaml
```

## Project Structure

```
capstone-01-ml-pipeline/
  README.md
  cli.py
  Dockerfile
  src/
    __init__.py
    data_ingestion.py
    preprocessing.py
    train.py
    evaluate.py
    pipeline.py
  tests/
    __init__.py
    test_pipeline.py
```

## Dependencies

- scikit-learn
- pandas
- numpy
- mlflow
- click
- xgboost
- pytest
