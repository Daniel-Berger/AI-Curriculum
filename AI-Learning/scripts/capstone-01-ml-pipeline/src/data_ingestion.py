"""
Data Ingestion Module
=====================

Handles loading data from multiple sources into a unified DataFrame format.
Supported sources include CSV files, Parquet files, SQL databases, and REST APIs.

Key responsibilities:
- Source validation and connection management
- Schema inference and validation
- Data loading with configurable chunking for large datasets
- Basic data quality checks on ingestion (null counts, duplicates, type mismatches)
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd


class DataSource(Enum):
    """Supported data source types."""

    CSV = "csv"
    PARQUET = "parquet"
    SQL = "sql"
    API = "api"


class DataIngester:
    """Load and validate data from various sources.

    Parameters
    ----------
    source_type : DataSource
        The type of data source to read from.
    connection_params : dict, optional
        Connection parameters (e.g., database URI, API base URL, file path).

    Examples
    --------
    >>> ingester = DataIngester(source_type=DataSource.CSV, connection_params={"path": "data.csv"})
    >>> df = ingester.load()
    """

    def __init__(
        self,
        source_type: DataSource,
        connection_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.source_type = source_type
        self.connection_params = connection_params or {}
        self._validated: bool = False

    def validate_source(self) -> bool:
        """Validate that the data source is accessible and well-formed.

        Returns
        -------
        bool
            True if the source is valid and accessible.

        Raises
        ------
        ConnectionError
            If the source cannot be reached.
        FileNotFoundError
            If a file-based source does not exist.
        """
        raise NotImplementedError

    def load(self, chunk_size: Optional[int] = None) -> pd.DataFrame:
        """Load data from the configured source.

        Parameters
        ----------
        chunk_size : int, optional
            If provided, load data in chunks of this size for memory efficiency.

        Returns
        -------
        pd.DataFrame
            The loaded dataset.
        """
        raise NotImplementedError

    def get_schema(self) -> Dict[str, str]:
        """Infer and return the schema of the data source.

        Returns
        -------
        dict
            Mapping of column names to dtype strings.
        """
        raise NotImplementedError

    def quality_check(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run basic quality checks on the ingested data.

        Checks include null counts per column, duplicate row count,
        and type consistency.

        Parameters
        ----------
        df : pd.DataFrame
            The ingested DataFrame to check.

        Returns
        -------
        dict
            Quality report with keys: 'null_counts', 'duplicate_rows', 'type_issues'.
        """
        raise NotImplementedError
