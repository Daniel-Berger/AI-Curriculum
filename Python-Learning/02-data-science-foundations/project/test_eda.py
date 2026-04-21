"""Tests for the EDA Pipeline."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from eda_pipeline import DataQualityReport, EDAConfig, EDAPipeline


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create a sample CSV for testing."""
    data = {
        "id": range(1, 21),
        "date": pd.date_range("2024-01-01", periods=20).strftime("%Y-%m-%d"),
        "category": ["A", "B", "C", "A", "B"] * 4,
        "value1": [100, 200, None, 400, 500, 150, 250, 350, 450, 550,
                   120, 220, 320, 420, 520, 160, 260, 360, 460, 560],
        "value2": [10.5, 20.3, 30.1, None, 50.7, 15.2, 25.4, 35.6, 45.8, 55.0,
                   12.1, 22.3, 32.5, 42.7, 52.9, 16.3, 26.5, 36.7, 46.9, 57.1],
        "region": ["North", "South", "East", "West", "North"] * 4,
        "status": ["completed"] * 15 + ["pending"] * 3 + ["cancelled"] * 2,
    }
    csv_path = tmp_path / "test_data.csv"
    pd.DataFrame(data).to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def pipeline(sample_csv: Path) -> EDAPipeline:
    """Create a pipeline with test data loaded."""
    config = EDAConfig(data_path=sample_csv, output_dir=sample_csv.parent / "output")
    p = EDAPipeline(config)
    p.load_data()
    return p


# =============================================================================
# Tests: Data Loading
# =============================================================================
class TestDataLoading:
    def test_load_data_returns_dataframe(self, sample_csv: Path) -> None:
        config = EDAConfig(data_path=sample_csv)
        p = EDAPipeline(config)
        df = p.load_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 20

    def test_load_data_sets_df_attribute(self, pipeline: EDAPipeline) -> None:
        assert pipeline.df is not None
        assert isinstance(pipeline.df, pd.DataFrame)

    def test_load_nonexistent_file_raises(self, tmp_path: Path) -> None:
        config = EDAConfig(data_path=tmp_path / "nonexistent.csv")
        p = EDAPipeline(config)
        with pytest.raises(FileNotFoundError):
            p.load_data()


# =============================================================================
# Tests: Data Quality
# =============================================================================
class TestDataQuality:
    def test_quality_report_shape(self, pipeline: EDAPipeline) -> None:
        report = pipeline.check_quality()
        assert report.shape == (20, 7)

    def test_detects_missing_values(self, pipeline: EDAPipeline) -> None:
        report = pipeline.check_quality()
        assert report.missing_counts["value1"] == 1
        assert report.missing_counts["value2"] == 1

    def test_no_duplicates(self, pipeline: EDAPipeline) -> None:
        report = pipeline.check_quality()
        assert report.duplicate_rows == 0

    def test_quality_report_has_dtypes(self, pipeline: EDAPipeline) -> None:
        report = pipeline.check_quality()
        assert len(report.dtypes) == 7
        assert "float64" in report.dtypes["value1"]

    def test_quality_without_data_raises(self) -> None:
        p = EDAPipeline()
        with pytest.raises(ValueError, match="No data loaded"):
            p.check_quality()


# =============================================================================
# Tests: Statistical Summary
# =============================================================================
class TestStatisticalSummary:
    def test_returns_numeric_summary(self, pipeline: EDAPipeline) -> None:
        summaries = pipeline.statistical_summary()
        assert "numeric" in summaries
        assert "count" in summaries["numeric"].index

    def test_returns_categorical_summary(self, pipeline: EDAPipeline) -> None:
        summaries = pipeline.statistical_summary()
        assert "categorical" in summaries


# =============================================================================
# Tests: Correlation
# =============================================================================
class TestCorrelation:
    def test_correlation_returns_dataframe(self, pipeline: EDAPipeline) -> None:
        corr = pipeline.correlation_analysis()
        assert isinstance(corr, pd.DataFrame)

    def test_correlation_is_symmetric(self, pipeline: EDAPipeline) -> None:
        corr = pipeline.correlation_analysis()
        np.testing.assert_array_almost_equal(corr.values, corr.T.values)

    def test_diagonal_is_one(self, pipeline: EDAPipeline) -> None:
        corr = pipeline.correlation_analysis()
        np.testing.assert_array_almost_equal(np.diag(corr.values), 1.0)


# =============================================================================
# Tests: Visualizations
# =============================================================================
class TestVisualizations:
    def test_creates_output_dir(self, pipeline: EDAPipeline) -> None:
        output_dir = pipeline.config.output_dir
        pipeline.create_visualizations()
        assert output_dir.exists()

    def test_creates_plot_files(self, pipeline: EDAPipeline) -> None:
        plots = pipeline.create_visualizations()
        assert len(plots) > 0
        for plot_path in plots:
            assert plot_path.exists()
            assert plot_path.suffix == ".png"


# =============================================================================
# Tests: Full Pipeline
# =============================================================================
class TestFullPipeline:
    def test_run_returns_results(self, sample_csv: Path) -> None:
        config = EDAConfig(
            data_path=sample_csv,
            output_dir=sample_csv.parent / "output",
        )
        p = EDAPipeline(config)
        results = p.run()
        assert "quality_report" in results
        assert "summaries" in results
        assert "correlations" in results
        assert "plots" in results
