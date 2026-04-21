"""
Phase 2 Project: Complete EDA Pipeline
========================================
A systematic Exploratory Data Analysis pipeline for tabular data.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving plots

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================
@dataclass
class EDAConfig:
    """Configuration for the EDA pipeline."""
    data_path: Path = Path("sample_data.csv")
    output_dir: Path = Path("eda_output")
    outlier_threshold: float = 1.5  # IQR multiplier
    missing_threshold: float = 0.5  # Flag columns with >50% missing
    correlation_threshold: float = 0.7  # Flag high correlations
    figsize: tuple[int, int] = (10, 6)


# =============================================================================
# Data Quality Report
# =============================================================================
@dataclass
class DataQualityReport:
    """Results of data quality checks."""
    shape: tuple[int, int] = (0, 0)
    dtypes: dict[str, str] = field(default_factory=dict)
    missing_counts: dict[str, int] = field(default_factory=dict)
    missing_pcts: dict[str, float] = field(default_factory=dict)
    duplicate_rows: int = 0
    outlier_counts: dict[str, int] = field(default_factory=dict)
    high_missing_columns: list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Shape: {self.shape[0]} rows x {self.shape[1]} columns",
            f"Duplicate rows: {self.duplicate_rows}",
            f"Columns with missing data: {sum(1 for v in self.missing_counts.values() if v > 0)}",
            f"Total missing values: {sum(self.missing_counts.values())}",
        ]
        if self.outlier_counts:
            lines.append(f"Columns with outliers: {len(self.outlier_counts)}")
        if self.high_missing_columns:
            lines.append(f"High-missing columns (>{50}%): {self.high_missing_columns}")
        return "\n".join(lines)


# =============================================================================
# EDA Pipeline
# =============================================================================
class EDAPipeline:
    """A systematic EDA pipeline for tabular data."""

    def __init__(self, config: Optional[EDAConfig] = None) -> None:
        self.config = config or EDAConfig()
        self.df: Optional[pd.DataFrame] = None
        self.quality_report: Optional[DataQualityReport] = None

    def load_data(self, path: Optional[Path] = None) -> pd.DataFrame:
        """Load data from CSV file."""
        data_path = path or self.config.data_path
        logger.info(f"Loading data from {data_path}")

        self.df = pd.read_csv(data_path, parse_dates=["date"])
        logger.info(f"Loaded {self.df.shape[0]} rows, {self.df.shape[1]} columns")
        return self.df

    def check_quality(self) -> DataQualityReport:
        """Perform data quality checks."""
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")

        df = self.df
        report = DataQualityReport()

        # Basic info
        report.shape = df.shape
        report.dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}

        # Missing values
        missing = df.isnull().sum()
        report.missing_counts = missing.to_dict()
        report.missing_pcts = (missing / len(df) * 100).round(2).to_dict()
        report.high_missing_columns = [
            col for col, pct in report.missing_pcts.items()
            if pct > self.config.missing_threshold * 100
        ]

        # Duplicates
        report.duplicate_rows = int(df.duplicated().sum())

        # Outliers (IQR method for numeric columns)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - self.config.outlier_threshold * iqr
            upper = q3 + self.config.outlier_threshold * iqr
            n_outliers = int(((df[col] < lower) | (df[col] > upper)).sum())
            if n_outliers > 0:
                report.outlier_counts[col] = n_outliers

        self.quality_report = report
        logger.info("Data quality check complete")
        return report

    def statistical_summary(self) -> dict[str, pd.DataFrame]:
        """Generate statistical summaries."""
        if self.df is None:
            raise ValueError("No data loaded.")

        summaries = {}

        # Numeric summary
        numeric_df = self.df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            summaries["numeric"] = numeric_df.describe().round(2)

        # Categorical summary
        cat_df = self.df.select_dtypes(include=["object", "category"])
        if not cat_df.empty:
            cat_summary = pd.DataFrame({
                col: {
                    "count": cat_df[col].count(),
                    "unique": cat_df[col].nunique(),
                    "top": cat_df[col].mode().iloc[0] if not cat_df[col].mode().empty else None,
                    "freq": cat_df[col].value_counts().iloc[0] if cat_df[col].count() > 0 else 0,
                }
                for col in cat_df.columns
            })
            summaries["categorical"] = cat_summary

        logger.info("Statistical summaries generated")
        return summaries

    def correlation_analysis(self) -> pd.DataFrame:
        """Compute correlation matrix for numeric columns."""
        if self.df is None:
            raise ValueError("No data loaded.")

        numeric_df = self.df.select_dtypes(include=[np.number])
        corr = numeric_df.corr().round(3)

        # Flag high correlations
        high_corr = []
        for i in range(len(corr.columns)):
            for j in range(i + 1, len(corr.columns)):
                if abs(corr.iloc[i, j]) > self.config.correlation_threshold:
                    high_corr.append(
                        (corr.columns[i], corr.columns[j], corr.iloc[i, j])
                    )

        if high_corr:
            logger.info(f"High correlations found: {high_corr}")

        return corr

    def create_visualizations(self, output_dir: Optional[Path] = None) -> list[Path]:
        """Create and save visualizations."""
        if self.df is None:
            raise ValueError("No data loaded.")

        save_dir = output_dir or self.config.output_dir
        save_dir.mkdir(parents=True, exist_ok=True)
        saved_files: list[Path] = []

        sns.set_theme(style="whitegrid")

        # 1. Distribution of numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            fig, axes = plt.subplots(1, min(len(numeric_cols), 3),
                                     figsize=self.config.figsize)
            if len(numeric_cols) == 1:
                axes = [axes]
            for ax, col in zip(axes, numeric_cols[:3]):
                self.df[col].dropna().hist(ax=ax, bins=20, edgecolor="black")
                ax.set_title(f"Distribution of {col}")
                ax.set_xlabel(col)
            plt.tight_layout()
            path = save_dir / "distributions.png"
            fig.savefig(path, dpi=100)
            plt.close(fig)
            saved_files.append(path)

        # 2. Correlation heatmap
        if len(numeric_cols) > 1:
            corr = self.df[numeric_cols].corr()
            fig, ax = plt.subplots(figsize=self.config.figsize)
            sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, ax=ax, fmt=".2f")
            ax.set_title("Correlation Heatmap")
            plt.tight_layout()
            path = save_dir / "correlation_heatmap.png"
            fig.savefig(path, dpi=100)
            plt.close(fig)
            saved_files.append(path)

        # 3. Category counts
        cat_cols = self.df.select_dtypes(include=["object", "category"]).columns
        if len(cat_cols) > 0:
            fig, axes = plt.subplots(1, min(len(cat_cols), 3),
                                     figsize=self.config.figsize)
            if len(cat_cols) == 1:
                axes = [axes]
            for ax, col in zip(axes, cat_cols[:3]):
                self.df[col].value_counts().plot(kind="bar", ax=ax, edgecolor="black")
                ax.set_title(f"Counts: {col}")
                ax.set_xlabel(col)
            plt.tight_layout()
            path = save_dir / "category_counts.png"
            fig.savefig(path, dpi=100)
            plt.close(fig)
            saved_files.append(path)

        # 4. Box plots for outlier detection
        if len(numeric_cols) > 0:
            fig, ax = plt.subplots(figsize=self.config.figsize)
            self.df[numeric_cols].boxplot(ax=ax)
            ax.set_title("Box Plots — Outlier Detection")
            plt.xticks(rotation=45)
            plt.tight_layout()
            path = save_dir / "boxplots.png"
            fig.savefig(path, dpi=100)
            plt.close(fig)
            saved_files.append(path)

        logger.info(f"Saved {len(saved_files)} visualizations to {save_dir}")
        return saved_files

    def run(self) -> dict[str, object]:
        """Run the full EDA pipeline."""
        logger.info("=" * 50)
        logger.info("Starting EDA Pipeline")
        logger.info("=" * 50)

        # Step 1: Load
        self.load_data()

        # Step 2: Quality
        report = self.check_quality()
        print("\n--- Data Quality Report ---")
        print(report.summary())

        # Step 3: Statistics
        summaries = self.statistical_summary()
        print("\n--- Numeric Summary ---")
        if "numeric" in summaries:
            print(summaries["numeric"])

        # Step 4: Correlations
        corr = self.correlation_analysis()
        print("\n--- Correlation Matrix ---")
        print(corr)

        # Step 5: Visualizations
        plots = self.create_visualizations()
        print(f"\n--- Visualizations saved: {len(plots)} plots ---")

        logger.info("EDA Pipeline complete")
        return {
            "quality_report": report,
            "summaries": summaries,
            "correlations": corr,
            "plots": plots,
        }


if __name__ == "__main__":
    pipeline = EDAPipeline()
    pipeline.run()
