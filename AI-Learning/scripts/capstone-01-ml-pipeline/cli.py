"""
CLI Entry Point
================

Click-based command-line interface for the ML pipeline. Provides commands
to run the full pipeline or individual stages (ingest, preprocess, train,
evaluate) with configurable options.

Usage:
    python cli.py run --config config.yaml
    python cli.py ingest --source data/raw/dataset.csv
    python cli.py train --data data/processed --model random_forest
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """ML Pipeline CLI - End-to-end machine learning pipeline management."""
    pass


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    required=True,
    help="Path to YAML configuration file.",
)
def run(config: str) -> None:
    """Run the full ML pipeline end-to-end."""
    click.echo(f"Running full pipeline with config: {config}")
    raise NotImplementedError("Full pipeline execution not yet implemented.")


@cli.command()
@click.option(
    "--source",
    type=click.Path(),
    required=True,
    help="Path or URI of the data source.",
)
@click.option(
    "--source-type",
    type=click.Choice(["csv", "parquet", "sql", "api"]),
    default="csv",
    help="Type of data source.",
)
@click.option(
    "--output",
    type=click.Path(),
    default="data/raw",
    help="Output directory for ingested data.",
)
def ingest(source: str, source_type: str, output: str) -> None:
    """Ingest data from a source into the pipeline."""
    click.echo(f"Ingesting {source_type} data from: {source}")
    click.echo(f"Output directory: {output}")
    raise NotImplementedError("Data ingestion CLI not yet implemented.")


@cli.command()
@click.option(
    "--input",
    "input_dir",
    type=click.Path(exists=True),
    required=True,
    help="Input data directory.",
)
@click.option(
    "--output",
    type=click.Path(),
    default="data/processed",
    help="Output directory for processed data.",
)
@click.option(
    "--target",
    type=str,
    default="target",
    help="Name of the target column.",
)
def preprocess(input_dir: str, output: str, target: str) -> None:
    """Preprocess raw data for model training."""
    click.echo(f"Preprocessing data from: {input_dir}")
    click.echo(f"Target column: {target}")
    raise NotImplementedError("Preprocessing CLI not yet implemented.")


@cli.command()
@click.option(
    "--data",
    type=click.Path(exists=True),
    required=True,
    help="Path to preprocessed data.",
)
@click.option(
    "--model",
    type=click.Choice(
        ["random_forest", "gradient_boosting", "logistic_regression", "xgboost"]
    ),
    default="random_forest",
    help="Model type to train.",
)
@click.option("--tune/--no-tune", default=False, help="Enable hyperparameter tuning.")
@click.option(
    "--output",
    type=click.Path(),
    default="models",
    help="Output directory for trained model.",
)
def train(data: str, model: str, tune: bool, output: str) -> None:
    """Train a model on preprocessed data."""
    click.echo(f"Training {model} on data: {data}")
    click.echo(f"Hyperparameter tuning: {'enabled' if tune else 'disabled'}")
    raise NotImplementedError("Training CLI not yet implemented.")


@cli.command()
@click.option(
    "--model",
    "model_path",
    type=click.Path(exists=True),
    required=True,
    help="Path to trained model.",
)
@click.option(
    "--data",
    type=click.Path(exists=True),
    required=True,
    help="Path to test data.",
)
@click.option(
    "--output",
    type=click.Path(),
    default="reports",
    help="Output directory for evaluation reports.",
)
def evaluate(model_path: str, data: str, output: str) -> None:
    """Evaluate a trained model on test data."""
    click.echo(f"Evaluating model: {model_path}")
    click.echo(f"Test data: {data}")
    raise NotImplementedError("Evaluation CLI not yet implemented.")


if __name__ == "__main__":
    cli()
