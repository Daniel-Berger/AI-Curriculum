#!/usr/bin/env python3
"""CLI Data Analysis Tool -- Phase 1 Capstone Project.

A command-line application that reads CSV files, filters rows, computes
descriptive statistics, and displays results in formatted terminal tables.

Usage:
    python main.py sample_data.csv
    python main.py sample_data.csv --column salary
    python main.py sample_data.csv --filter "department==Engineering"
    python main.py sample_data.csv --filter "salary>100000" --column salary
    python main.py sample_data.csv --verbose

Swift parallel: This is like building a CLI tool with Swift's
ArgumentParser, but using Python's typer (built on click).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from data_analyzer import (
    CSVReader,
    DataAnalysisError,
    DataFilter,
    StatisticsCalculator,
    StatisticsResult,
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = typer.Typer(
    name="data-analyzer",
    help="CLI tool for CSV data analysis -- reads, filters, and computes statistics.",
    add_completion=False,
)

console = Console()
error_console = Console(stderr=True)

logger = logging.getLogger("data_analyzer")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def display_statistics_table(results: list[StatisticsResult]) -> Table:
    """Build a rich Table from a list of StatisticsResult objects."""
    table = Table(
        title="Statistical Summary",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )

    table.add_column("Column", style="bold")
    table.add_column("Count", justify="right")
    table.add_column("Mean", justify="right")
    table.add_column("Median", justify="right")
    table.add_column("Mode", justify="right")
    table.add_column("Std Dev", justify="right")
    table.add_column("Min", justify="right")
    table.add_column("Max", justify="right")

    for result in results:
        mode_str = f"{result.mode:.2f}" if result.mode is not None else "N/A"
        table.add_row(
            result.column_name,
            str(result.count),
            f"{result.mean:.2f}",
            f"{result.median:.2f}",
            mode_str,
            f"{result.std_dev:.2f}",
            f"{result.min_value:.2f}",
            f"{result.max_value:.2f}",
        )

    return table


def display_data_preview(rows: list[dict[str, str]], headers: list[str]) -> Table:
    """Build a rich Table showing a preview of the raw data."""
    preview_rows = rows[:5]
    table = Table(
        title=f"Data Preview (first {len(preview_rows)} of {len(rows)} rows)",
        show_header=True,
        header_style="bold green",
        border_style="dim",
    )
    for header in headers:
        table.add_column(header)
    for row in preview_rows:
        table.add_row(*(row.get(h, "") for h in headers))
    return table


def configure_logging(verbose: bool) -> None:
    """Set up logging with rich handler."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=error_console, rich_tracebacks=True)],
        force=True,
    )


# ---------------------------------------------------------------------------
# Main CLI command
# ---------------------------------------------------------------------------

@app.command()
def analyze(
    csv_file: Annotated[
        Path,
        typer.Argument(
            help="Path to the CSV file to analyze.",
            exists=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    column: Annotated[
        Optional[str],
        typer.Option(
            "--column", "-c",
            help="Specific column to analyze. If omitted, all numeric columns are analyzed.",
        ),
    ] = None,
    filter_expr: Annotated[
        Optional[str],
        typer.Option(
            "--filter", "-f",
            help=(
                "Filter expression, e.g. 'salary>80000', 'department==Engineering', "
                "'city contains San'."
            ),
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o",
            help="Write results to a text file instead of stdout.",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v",
            help="Enable verbose/debug logging.",
        ),
    ] = False,
) -> None:
    """Analyze a CSV file: compute statistics, optionally filter rows."""
    configure_logging(verbose)

    try:
        _run_analysis(csv_file, column, filter_expr, output)
    except DataAnalysisError as exc:
        error_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        error_console.print(f"[bold red]Unexpected error:[/bold red] {exc}")
        logger.exception("Unexpected error during analysis")
        raise typer.Exit(code=2) from exc


def _run_analysis(
    csv_file: Path,
    column: str | None,
    filter_expr: str | None,
    output: Path | None,
) -> None:
    """Core analysis logic, separated from the CLI wiring for testability."""
    # 1. Read CSV
    reader = CSVReader(csv_file)
    rows = reader.read()
    headers = reader.headers

    console.print(f"\n[bold]Loaded:[/bold] {reader.row_count} rows from {csv_file.name}")

    # 2. Show data preview
    console.print(display_data_preview(rows, headers))
    console.print()

    # 3. Apply filter (if provided)
    if filter_expr:
        criteria = DataFilter.parse_filter(filter_expr)
        rows = DataFilter.apply_filter(rows, criteria, headers)
        console.print(
            f"[bold]Filter:[/bold] {criteria}  -->  {len(rows)} rows matched\n"
        )
        if not rows:
            console.print("[yellow]No rows match the filter. Nothing to analyze.[/yellow]")
            return

    # 4. Determine columns to analyze
    if column:
        columns_to_analyze = [column]
    else:
        columns_to_analyze = StatisticsCalculator.detect_numeric_columns(rows, headers)
        if not columns_to_analyze:
            console.print("[yellow]No numeric columns detected.[/yellow]")
            return
        logger.info("Auto-detected numeric columns: %s", columns_to_analyze)

    # 5. Compute statistics
    results: list[StatisticsResult] = []
    for col in columns_to_analyze:
        try:
            result = StatisticsCalculator.compute(rows, col, headers)
            results.append(result)
        except DataAnalysisError as exc:
            error_console.print(f"[yellow]Warning:[/yellow] {exc}")

    if not results:
        console.print("[yellow]No statistics could be computed.[/yellow]")
        return

    # 6. Display results
    stats_table = display_statistics_table(results)
    console.print(stats_table)
    console.print()

    # 7. Write to file if requested
    if output:
        _write_output(output, results)


def _write_output(output_path: Path, results: list[StatisticsResult]) -> None:
    """Write statistics results to a plain-text file."""
    with output_path.open("w", encoding="utf-8") as f:
        f.write("Statistical Summary\n")
        f.write("=" * 60 + "\n\n")
        for result in results:
            f.write(str(result))
            f.write("\n\n")
    console.print(f"[green]Results written to {output_path}[/green]")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app()
