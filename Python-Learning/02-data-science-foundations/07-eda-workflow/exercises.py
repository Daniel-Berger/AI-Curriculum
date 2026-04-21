"""
Module 07: EDA Workflow - Exercises
====================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- Most exercises use a sample employee dataset generated below.

Difficulty levels:
  Easy   - Direct application of a single EDA step
  Medium - Combining multiple techniques or interpreting results
  Hard   - Building reusable EDA utilities

Required packages: pandas, numpy, matplotlib, seaborn
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure


# =============================================================================
# SAMPLE DATASET GENERATOR
# =============================================================================

def create_sample_dataset(seed: int = 42) -> pd.DataFrame:
    """Generate a sample employee dataset for EDA exercises.

    Returns a DataFrame with intentional data quality issues:
    - Missing values in several columns
    - A few duplicate rows
    - Outliers in salary
    - Mixed data types
    """
    np.random.seed(seed)
    n = 300

    df = pd.DataFrame({
        'employee_id': range(1000, 1000 + n),
        'age': np.random.normal(38, 10, n).astype(int).clip(20, 65),
        'department': np.random.choice(
            ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance'],
            n, p=[0.30, 0.25, 0.20, 0.15, 0.10]
        ),
        'salary': np.random.lognormal(11.0, 0.4, n).round(2),
        'years_experience': np.random.exponential(8, n).round(1).clip(0, 40),
        'satisfaction_score': np.random.choice([1, 2, 3, 4, 5], n,
                                                p=[0.05, 0.10, 0.30, 0.35, 0.20]),
        'remote_pct': np.random.choice([0, 25, 50, 75, 100], n,
                                        p=[0.15, 0.10, 0.25, 0.25, 0.25]),
        'performance_rating': np.random.normal(3.5, 0.8, n).round(1).clip(1.0, 5.0),
    })

    # Inject missing values
    df.loc[np.random.choice(n, 20, replace=False), 'salary'] = np.nan
    df.loc[np.random.choice(n, 12, replace=False), 'age'] = np.nan
    df.loc[np.random.choice(n, 8, replace=False), 'performance_rating'] = np.nan

    # Inject outliers
    df.loc[5, 'salary'] = 950000.00
    df.loc[150, 'salary'] = 15000.00
    df.loc[200, 'years_experience'] = 45.0

    # Add duplicate rows
    dupes = df.iloc[:4].copy()
    df = pd.concat([df, dupes], ignore_index=True)

    return df


# =============================================================================
# STEP 1: UNDERSTAND STRUCTURE
# =============================================================================

# Exercise 1: Dataset Overview
# Difficulty: Easy
# Create a structured overview of the dataset.
def dataset_overview(df: pd.DataFrame) -> dict:
    """Return a dictionary with basic dataset information.

    Expected keys and value types:
        'n_rows': int -- number of rows
        'n_cols': int -- number of columns
        'column_names': list[str] -- list of column names
        'numeric_columns': list[str] -- columns with numeric dtype
        'categorical_columns': list[str] -- columns with object/category dtype
        'memory_mb': float -- memory usage in megabytes (rounded to 2 decimals)
        'dtypes': dict -- mapping of column name to dtype string

    >>> df = create_sample_dataset()
    >>> info = dataset_overview(df)
    >>> info['n_cols']
    8
    """
    pass


# Exercise 2: Column Type Classifier
# Difficulty: Easy
# Classify columns by their semantic type (not just dtype).
def classify_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    """Classify columns into semantic categories.

    Categories:
        'numeric_continuous': numeric columns with > 20 unique values
        'numeric_discrete': numeric columns with <= 20 unique values
        'categorical': object or category dtype columns
        'potential_id': columns where every value is unique

    >>> df = create_sample_dataset()
    >>> classes = classify_columns(df)
    >>> 'employee_id' in classes['potential_id']
    True
    """
    pass


# =============================================================================
# STEP 2: DATA QUALITY
# =============================================================================

# Exercise 3: Missing Value Report
# Difficulty: Easy
# Generate a missing value summary.
def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Create a DataFrame summarizing missing values.

    The returned DataFrame should have:
    - Index: column names (only columns WITH missing values)
    - Columns: 'missing_count', 'missing_pct', 'dtype'
    - Sorted by missing_pct descending
    - missing_pct should be rounded to 2 decimal places

    >>> df = create_sample_dataset()
    >>> report = missing_value_report(df)
    >>> len(report) > 0
    True
    >>> 'missing_count' in report.columns
    True
    """
    pass


# Exercise 4: Duplicate Detector
# Difficulty: Medium
# Detect and report duplicates with details.
def detect_duplicates(df: pd.DataFrame) -> dict:
    """Analyze duplicates in the dataset.

    Return a dictionary with:
        'n_exact_duplicates': int -- number of exactly duplicated rows
        'duplicate_pct': float -- percentage of rows that are duplicates (rounded to 2)
        'duplicate_rows': pd.DataFrame -- the actual duplicate rows (all copies)
        'n_after_dedup': int -- row count after removing duplicates

    >>> df = create_sample_dataset()
    >>> result = detect_duplicates(df)
    >>> result['n_exact_duplicates'] > 0
    True
    """
    pass


# Exercise 5: Outlier Detection
# Difficulty: Medium
# Detect outliers using the IQR method.
def detect_outliers_iqr(df: pd.DataFrame,
                        columns: list[str] | None = None) -> pd.DataFrame:
    """Detect outliers in numeric columns using the IQR method.

    Parameters:
        df: Input DataFrame
        columns: Specific columns to check. If None, check all numeric columns.

    Returns a DataFrame with columns:
        'column': column name
        'q1': 25th percentile
        'q3': 75th percentile
        'iqr': interquartile range
        'lower_bound': q1 - 1.5 * iqr
        'upper_bound': q3 + 1.5 * iqr
        'n_outliers': count of values outside bounds
        'outlier_pct': percentage of outliers (rounded to 2)

    >>> df = create_sample_dataset()
    >>> outliers = detect_outliers_iqr(df)
    >>> 'salary' in outliers['column'].values
    True
    """
    pass


# Exercise 6: Data Quality Score
# Difficulty: Hard
# Create a composite data quality score.
def data_quality_score(df: pd.DataFrame) -> dict:
    """Compute a data quality score from 0 to 100.

    Scoring criteria (each on a 0-100 scale, then averaged):
        'completeness': 100 * (1 - total_missing_cells / total_cells)
        'uniqueness': 100 * (1 - n_duplicate_rows / n_rows)
        'consistency': 100 * (numeric columns with |skew| < 2) / n_numeric_cols
                       (measures how many columns have reasonable distributions)

    Return:
        'completeness': float (0-100, rounded to 1)
        'uniqueness': float (0-100, rounded to 1)
        'consistency': float (0-100, rounded to 1)
        'overall': float (average of above three, rounded to 1)

    >>> df = create_sample_dataset()
    >>> scores = data_quality_score(df)
    >>> 0 <= scores['overall'] <= 100
    True
    """
    pass


# =============================================================================
# STEP 3: UNIVARIATE ANALYSIS
# =============================================================================

# Exercise 7: Statistical Summary
# Difficulty: Easy
# Generate an enhanced statistical summary.
def enhanced_describe(df: pd.DataFrame) -> pd.DataFrame:
    """Create an enhanced version of df.describe() for numeric columns.

    Include all standard describe() stats PLUS:
        'skewness': skewness of the column
        'kurtosis': kurtosis of the column
        'iqr': interquartile range (75th - 25th)
        'cv': coefficient of variation (std / mean * 100), rounded to 2
        'missing': count of missing values

    Return a DataFrame where rows are the numeric column names
    and columns include the above statistics.

    >>> df = create_sample_dataset()
    >>> desc = enhanced_describe(df)
    >>> 'skewness' in desc.columns
    True
    """
    pass


# Exercise 8: Distribution Plots
# Difficulty: Medium
# Create distribution plots for all numeric columns.
def plot_distributions(df: pd.DataFrame) -> Figure:
    """Create a grid of distribution plots for all numeric columns.

    Requirements:
    - One subplot per numeric column
    - Each subplot: histogram with KDE overlay (using seaborn's histplot)
    - Add vertical lines for mean (red dashed) and median (green dash-dot)
    - Subplot titles: column name
    - Grid arrangement: up to 3 columns, as many rows as needed
    - Figure size: (15, 4 * n_rows)
    - Use tight_layout()
    - Return the Figure object

    >>> df = create_sample_dataset()
    >>> fig = plot_distributions(df)
    >>> fig is not None
    True
    """
    pass


# =============================================================================
# STEP 4: BIVARIATE ANALYSIS
# =============================================================================

# Exercise 9: Correlation Finder
# Difficulty: Medium
# Find and rank correlations between numeric variables.
def find_correlations(df: pd.DataFrame,
                      threshold: float = 0.3) -> pd.DataFrame:
    """Find all pairwise correlations above the threshold.

    Returns a DataFrame with columns:
        'var1': first variable name
        'var2': second variable name
        'pearson_r': Pearson correlation coefficient (rounded to 3)
        'abs_r': absolute value of pearson_r
        'direction': 'positive' or 'negative'

    Only include each pair once (not both (A,B) and (B,A)).
    Sort by abs_r descending.
    Only include pairs where abs_r >= threshold.

    >>> df = create_sample_dataset()
    >>> corrs = find_correlations(df, threshold=0.1)
    >>> 'pearson_r' in corrs.columns
    True
    """
    pass


# Exercise 10: Grouped Summary
# Difficulty: Medium
# Summarize a numeric variable across groups.
def grouped_summary(df: pd.DataFrame, numeric_col: str,
                    group_col: str) -> pd.DataFrame:
    """Summarize a numeric column grouped by a categorical column.

    Returns a DataFrame with the group_col values as index and columns:
        'count': number of non-null values
        'mean': mean value (rounded to 2)
        'median': median value (rounded to 2)
        'std': standard deviation (rounded to 2)
        'min': minimum
        'max': maximum

    Sort by mean descending.

    >>> df = create_sample_dataset()
    >>> summary = grouped_summary(df, 'salary', 'department')
    >>> 'mean' in summary.columns
    True
    """
    pass


# Exercise 11: Bivariate Visualization
# Difficulty: Hard
# Create a comprehensive bivariate analysis plot.
def plot_bivariate_analysis(df: pd.DataFrame, x_col: str,
                            y_col: str, hue_col: str) -> Figure:
    """Create a 2x2 figure analyzing the relationship between two numeric vars.

    Layout:
    - Top-left: Scatter plot with hue coloring
    - Top-right: Scatter plot with regression line per hue group
                 (use sns.regplot or sns.lmplot logic drawn on the axes)
    - Bottom-left: Joint KDE contour plot (no hue, just x_col vs y_col)
    - Bottom-right: Box plot of y_col grouped by hue_col

    Requirements:
    - Figure size: (14, 12)
    - Super title: f'{x_col} vs {y_col} Analysis'
    - Return the Figure object

    >>> df = create_sample_dataset()
    >>> fig = plot_bivariate_analysis(df, 'age', 'salary', 'department')
    >>> fig is not None
    True
    """
    pass


# =============================================================================
# STEP 5-6: MULTIVARIATE & DOCUMENTATION
# =============================================================================

# Exercise 12: EDA Report Generator
# Difficulty: Hard
# Generate a comprehensive text-based EDA report.
def generate_eda_report(df: pd.DataFrame) -> str:
    """Generate a comprehensive text-based EDA summary.

    The report should include these sections:
    1. DATASET OVERVIEW: shape, memory, column counts by type
    2. DATA QUALITY: missing values summary, duplicate count
    3. NUMERIC SUMMARIES: for each numeric column -- mean, median, skewness
    4. CATEGORICAL SUMMARIES: for each categorical column --
       unique count, top value, top value frequency
    5. CORRELATIONS: pairs with |r| > 0.3

    Format each section clearly with headers and indentation.
    Return the complete report as a string.

    >>> df = create_sample_dataset()
    >>> report = generate_eda_report(df)
    >>> 'DATASET OVERVIEW' in report
    True
    >>> 'DATA QUALITY' in report
    True
    """
    pass


# =============================================================================
# SELF-CHECK / RUNNER
# =============================================================================

if __name__ == "__main__":
    print("Module 07: EDA Workflow Exercises")
    print("=" * 50)

    df = create_sample_dataset()
    print(f"\nSample dataset created: {df.shape[0]} rows x {df.shape[1]} columns\n")

    exercises = [
        ("01 Dataset Overview", lambda: dataset_overview(df)),
        ("02 Column Classifier", lambda: classify_columns(df)),
        ("03 Missing Value Report", lambda: missing_value_report(df)),
        ("04 Duplicate Detector", lambda: detect_duplicates(df)),
        ("05 Outlier Detection", lambda: detect_outliers_iqr(df)),
        ("06 Data Quality Score", lambda: data_quality_score(df)),
        ("07 Enhanced Describe", lambda: enhanced_describe(df)),
        ("08 Distribution Plots", lambda: plot_distributions(df)),
        ("09 Correlation Finder", lambda: find_correlations(df, threshold=0.1)),
        ("10 Grouped Summary", lambda: grouped_summary(df, 'salary', 'department')),
        ("11 Bivariate Analysis", lambda: plot_bivariate_analysis(
            df, 'age', 'salary', 'department')),
        ("12 EDA Report", lambda: generate_eda_report(df)),
    ]

    for name, exercise_fn in exercises:
        try:
            result = exercise_fn()
            if result is None:
                print(f"  [ ] {name} -- returned None (not implemented yet)")
            else:
                print(f"  [x] {name} -- completed successfully")
                if isinstance(result, Figure):
                    filename = f"exercise_{name.lower().replace(' ', '_')}.png"
                    result.savefig(filename, dpi=100, bbox_inches='tight')
                    plt.close(result)
                    print(f"      Saved to {filename}")
                elif isinstance(result, pd.DataFrame):
                    print(f"      Shape: {result.shape}")
                elif isinstance(result, dict):
                    print(f"      Keys: {list(result.keys())[:5]}")
                elif isinstance(result, str):
                    lines = result.strip().split('\n')
                    print(f"      Report: {len(lines)} lines")
        except Exception as e:
            print(f"  [!] {name} -- error: {e}")

    print("\nDone!")
