"""
Module 07: EDA Workflow - Solutions
====================================
Complete solutions for all exercises.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure


# =============================================================================
# SAMPLE DATASET GENERATOR (same as exercises.py)
# =============================================================================

def create_sample_dataset(seed: int = 42) -> pd.DataFrame:
    """Generate a sample employee dataset for EDA exercises."""
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

    df.loc[np.random.choice(n, 20, replace=False), 'salary'] = np.nan
    df.loc[np.random.choice(n, 12, replace=False), 'age'] = np.nan
    df.loc[np.random.choice(n, 8, replace=False), 'performance_rating'] = np.nan
    df.loc[5, 'salary'] = 950000.00
    df.loc[150, 'salary'] = 15000.00
    df.loc[200, 'years_experience'] = 45.0
    dupes = df.iloc[:4].copy()
    df = pd.concat([df, dupes], ignore_index=True)

    return df


# =============================================================================
# Exercise 1: Dataset Overview
# =============================================================================

def dataset_overview(df: pd.DataFrame) -> dict:
    """Return a dictionary with basic dataset information."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    memory_mb = round(df.memory_usage(deep=True).sum() / 1e6, 2)
    dtypes_dict = {col: str(dtype) for col, dtype in df.dtypes.items()}

    return {
        'n_rows': df.shape[0],
        'n_cols': df.shape[1],
        'column_names': df.columns.tolist(),
        'numeric_columns': numeric_cols,
        'categorical_columns': categorical_cols,
        'memory_mb': memory_mb,
        'dtypes': dtypes_dict,
    }


# =============================================================================
# Exercise 2: Column Type Classifier
# =============================================================================

def classify_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    """Classify columns into semantic categories."""
    result: dict[str, list[str]] = {
        'numeric_continuous': [],
        'numeric_discrete': [],
        'categorical': [],
        'potential_id': [],
    }

    for col in df.columns:
        # Check if potential ID (all unique values)
        if df[col].nunique() == len(df):
            result['potential_id'].append(col)

        if df[col].dtype in ['object', 'category']:
            result['categorical'].append(col)
        elif np.issubdtype(df[col].dtype, np.number):
            if df[col].nunique() > 20:
                result['numeric_continuous'].append(col)
            else:
                result['numeric_discrete'].append(col)

    return result


# =============================================================================
# Exercise 3: Missing Value Report
# =============================================================================

def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Create a DataFrame summarizing missing values."""
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)

    report = pd.DataFrame({
        'missing_count': missing_count,
        'missing_pct': missing_pct,
        'dtype': df.dtypes.astype(str),
    })

    # Only columns with missing values, sorted descending
    report = report[report['missing_count'] > 0].sort_values(
        'missing_pct', ascending=False
    )

    return report


# =============================================================================
# Exercise 4: Duplicate Detector
# =============================================================================

def detect_duplicates(df: pd.DataFrame) -> dict:
    """Analyze duplicates in the dataset."""
    n_exact = df.duplicated().sum()
    duplicate_rows = df[df.duplicated(keep=False)]
    n_after = len(df.drop_duplicates())

    return {
        'n_exact_duplicates': int(n_exact),
        'duplicate_pct': round(n_exact / len(df) * 100, 2),
        'duplicate_rows': duplicate_rows,
        'n_after_dedup': n_after,
    }


# =============================================================================
# Exercise 5: Outlier Detection
# =============================================================================

def detect_outliers_iqr(df: pd.DataFrame,
                        columns: list[str] | None = None) -> pd.DataFrame:
    """Detect outliers in numeric columns using the IQR method."""
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    results = []
    for col in columns:
        data = df[col].dropna()
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        n_outliers = int(((data < lower) | (data > upper)).sum())

        results.append({
            'column': col,
            'q1': round(q1, 2),
            'q3': round(q3, 2),
            'iqr': round(iqr, 2),
            'lower_bound': round(lower, 2),
            'upper_bound': round(upper, 2),
            'n_outliers': n_outliers,
            'outlier_pct': round(n_outliers / len(data) * 100, 2),
        })

    return pd.DataFrame(results)


# =============================================================================
# Exercise 6: Data Quality Score
# =============================================================================

def data_quality_score(df: pd.DataFrame) -> dict:
    """Compute a data quality score from 0 to 100."""
    # Completeness
    total_cells = df.shape[0] * df.shape[1]
    total_missing = df.isnull().sum().sum()
    completeness = round(100 * (1 - total_missing / total_cells), 1)

    # Uniqueness
    n_dupes = df.duplicated().sum()
    uniqueness = round(100 * (1 - n_dupes / len(df)), 1)

    # Consistency
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        reasonable = sum(1 for col in numeric_cols if abs(df[col].skew()) < 2)
        consistency = round(100 * reasonable / len(numeric_cols), 1)
    else:
        consistency = 100.0

    overall = round((completeness + uniqueness + consistency) / 3, 1)

    return {
        'completeness': completeness,
        'uniqueness': uniqueness,
        'consistency': consistency,
        'overall': overall,
    }


# =============================================================================
# Exercise 7: Enhanced Describe
# =============================================================================

def enhanced_describe(df: pd.DataFrame) -> pd.DataFrame:
    """Create an enhanced version of df.describe() for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    desc = df[numeric_cols].describe().T

    desc['skewness'] = df[numeric_cols].skew()
    desc['kurtosis'] = df[numeric_cols].kurtosis()
    desc['iqr'] = desc['75%'] - desc['25%']
    desc['cv'] = (desc['std'] / desc['mean'] * 100).round(2)
    desc['missing'] = df[numeric_cols].isnull().sum()

    return desc


# =============================================================================
# Exercise 8: Distribution Plots
# =============================================================================

def plot_distributions(df: pd.DataFrame) -> Figure:
    """Create a grid of distribution plots for all numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    n = len(numeric_cols)
    n_cols_grid = 3
    n_rows = (n + n_cols_grid - 1) // n_cols_grid

    fig, axes = plt.subplots(n_rows, n_cols_grid, figsize=(15, 4 * n_rows))
    axes_flat = np.array(axes).flatten()

    for i, col in enumerate(numeric_cols):
        ax = axes_flat[i]
        data = df[col].dropna()
        sns.histplot(data, kde=True, ax=ax, color='steelblue', alpha=0.7)
        ax.axvline(data.mean(), color='red', linestyle='--', linewidth=1.5,
                   label=f'Mean: {data.mean():.1f}')
        ax.axvline(data.median(), color='green', linestyle='-.', linewidth=1.5,
                   label=f'Median: {data.median():.1f}')
        ax.set_title(col)
        ax.legend(fontsize=8)

    # Hide unused axes
    for j in range(n, len(axes_flat)):
        axes_flat[j].set_visible(False)

    fig.tight_layout()
    return fig


# =============================================================================
# Exercise 9: Correlation Finder
# =============================================================================

def find_correlations(df: pd.DataFrame,
                      threshold: float = 0.3) -> pd.DataFrame:
    """Find all pairwise correlations above the threshold."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr = df[numeric_cols].corr()

    pairs = []
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            r = corr.iloc[i, j]
            abs_r = abs(r)
            if abs_r >= threshold:
                pairs.append({
                    'var1': numeric_cols[i],
                    'var2': numeric_cols[j],
                    'pearson_r': round(r, 3),
                    'abs_r': round(abs_r, 3),
                    'direction': 'positive' if r > 0 else 'negative',
                })

    result = pd.DataFrame(pairs)
    if len(result) > 0:
        result = result.sort_values('abs_r', ascending=False).reset_index(drop=True)
    return result


# =============================================================================
# Exercise 10: Grouped Summary
# =============================================================================

def grouped_summary(df: pd.DataFrame, numeric_col: str,
                    group_col: str) -> pd.DataFrame:
    """Summarize a numeric column grouped by a categorical column."""
    summary = df.groupby(group_col)[numeric_col].agg(
        count='count',
        mean='mean',
        median='median',
        std='std',
        min='min',
        max='max',
    )

    summary['mean'] = summary['mean'].round(2)
    summary['median'] = summary['median'].round(2)
    summary['std'] = summary['std'].round(2)

    return summary.sort_values('mean', ascending=False)


# =============================================================================
# Exercise 11: Bivariate Visualization
# =============================================================================

def plot_bivariate_analysis(df: pd.DataFrame, x_col: str,
                            y_col: str, hue_col: str) -> Figure:
    """Create a 2x2 figure analyzing the relationship between two numeric vars."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # Top-left: Scatter plot with hue
    sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col,
                    alpha=0.6, ax=axes[0, 0])
    axes[0, 0].set_title(f'{x_col} vs {y_col} (by {hue_col})')

    # Top-right: Scatter with regression line per group
    for group_name, group_data in df.groupby(hue_col):
        group_clean = group_data[[x_col, y_col]].dropna()
        if len(group_clean) > 2:
            sns.regplot(data=group_clean, x=x_col, y=y_col,
                        scatter=True, ax=axes[0, 1],
                        label=str(group_name), scatter_kws={'alpha': 0.3, 's': 15})
    axes[0, 1].set_title(f'{x_col} vs {y_col} (Regression)')
    axes[0, 1].legend(fontsize=8)

    # Bottom-left: KDE contour plot
    clean = df[[x_col, y_col]].dropna()
    sns.kdeplot(data=clean, x=x_col, y=y_col, fill=True,
                cmap='Blues', ax=axes[1, 0])
    axes[1, 0].set_title(f'{x_col} vs {y_col} (KDE)')

    # Bottom-right: Box plot of y by hue
    sns.boxplot(data=df, x=hue_col, y=y_col, ax=axes[1, 1], palette='Set2')
    axes[1, 1].set_title(f'{y_col} by {hue_col}')
    axes[1, 1].tick_params(axis='x', rotation=45)

    fig.suptitle(f'{x_col} vs {y_col} Analysis', fontsize=16)
    fig.tight_layout()
    return fig


# =============================================================================
# Exercise 12: EDA Report Generator
# =============================================================================

def generate_eda_report(df: pd.DataFrame) -> str:
    """Generate a comprehensive text-based EDA summary."""
    lines = []

    # Section 1: Dataset Overview
    lines.append("=" * 60)
    lines.append("1. DATASET OVERVIEW")
    lines.append("=" * 60)
    lines.append(f"   Rows: {df.shape[0]:,}")
    lines.append(f"   Columns: {df.shape[1]}")
    lines.append(f"   Memory: {df.memory_usage(deep=True).sum() / 1e6:.2f} MB")

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    lines.append(f"   Numeric columns ({len(numeric_cols)}): {numeric_cols.tolist()}")
    lines.append(f"   Categorical columns ({len(cat_cols)}): {cat_cols.tolist()}")

    # Section 2: Data Quality
    lines.append("")
    lines.append("=" * 60)
    lines.append("2. DATA QUALITY")
    lines.append("=" * 60)

    total_cells = df.shape[0] * df.shape[1]
    total_missing = df.isnull().sum().sum()
    lines.append(f"   Total missing values: {total_missing:,} / {total_cells:,} "
                 f"({total_missing / total_cells * 100:.1f}%)")
    lines.append(f"   Duplicate rows: {df.duplicated().sum()}")

    missing_cols = df.columns[df.isnull().any()].tolist()
    if missing_cols:
        lines.append("   Columns with missing data:")
        for col in missing_cols:
            n_miss = df[col].isnull().sum()
            pct = n_miss / len(df) * 100
            lines.append(f"     - {col}: {n_miss} ({pct:.1f}%)")

    # Section 3: Numeric Summaries
    lines.append("")
    lines.append("=" * 60)
    lines.append("3. NUMERIC SUMMARIES")
    lines.append("=" * 60)

    for col in numeric_cols:
        data = df[col].dropna()
        skew = data.skew()
        lines.append(f"   {col}:")
        lines.append(f"     Mean: {data.mean():.2f}, Median: {data.median():.2f}")
        lines.append(f"     Std: {data.std():.2f}")
        lines.append(f"     Range: [{data.min():.2f}, {data.max():.2f}]")
        lines.append(f"     Skewness: {skew:.2f}")

    # Section 4: Categorical Summaries
    lines.append("")
    lines.append("=" * 60)
    lines.append("4. CATEGORICAL SUMMARIES")
    lines.append("=" * 60)

    for col in cat_cols:
        n_unique = df[col].nunique()
        if len(df[col].dropna()) > 0:
            top_val = df[col].value_counts().index[0]
            top_freq = df[col].value_counts().iloc[0]
            top_pct = top_freq / len(df) * 100
            lines.append(f"   {col}: {n_unique} unique values")
            lines.append(f"     Top: '{top_val}' ({top_freq}, {top_pct:.1f}%)")
        else:
            lines.append(f"   {col}: {n_unique} unique values (all missing)")

    # Section 5: Correlations
    lines.append("")
    lines.append("=" * 60)
    lines.append("5. CORRELATIONS (|r| > 0.3)")
    lines.append("=" * 60)

    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        found_any = False
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                r = corr.iloc[i, j]
                if abs(r) > 0.3:
                    found_any = True
                    direction = "positive" if r > 0 else "negative"
                    lines.append(
                        f"   {numeric_cols[i]} <-> {numeric_cols[j]}: "
                        f"r={r:.3f} ({direction})"
                    )
        if not found_any:
            lines.append("   No correlations above threshold found.")
    else:
        lines.append("   Not enough numeric columns for correlation analysis.")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


# =============================================================================
# SELF-CHECK / RUNNER
# =============================================================================

if __name__ == "__main__":
    print("Module 07: EDA Workflow Solutions")
    print("=" * 50)

    df = create_sample_dataset()
    print(f"\nSample dataset created: {df.shape[0]} rows x {df.shape[1]} columns\n")

    # Run each solution
    print("01 Dataset Overview:")
    overview = dataset_overview(df)
    print(f"   {overview['n_rows']} rows, {overview['n_cols']} cols, "
          f"{overview['memory_mb']} MB")

    print("\n02 Column Classifier:")
    classes = classify_columns(df)
    for k, v in classes.items():
        print(f"   {k}: {v}")

    print("\n03 Missing Value Report:")
    mvr = missing_value_report(df)
    print(mvr.to_string(index=True))

    print("\n04 Duplicate Detector:")
    dupes = detect_duplicates(df)
    print(f"   Exact duplicates: {dupes['n_exact_duplicates']}")
    print(f"   Rows after dedup: {dupes['n_after_dedup']}")

    print("\n05 Outlier Detection:")
    outliers = detect_outliers_iqr(df)
    print(outliers[['column', 'n_outliers', 'outlier_pct']].to_string(index=False))

    print("\n06 Data Quality Score:")
    scores = data_quality_score(df)
    for k, v in scores.items():
        print(f"   {k}: {v}")

    print("\n07 Enhanced Describe:")
    desc = enhanced_describe(df)
    print(desc[['mean', 'skewness', 'kurtosis', 'cv', 'missing']].to_string())

    print("\n08 Distribution Plots:")
    fig = plot_distributions(df)
    fig.savefig("solution_distributions.png", dpi=100, bbox_inches='tight')
    plt.close(fig)
    print("   Saved to solution_distributions.png")

    print("\n09 Correlation Finder:")
    corrs = find_correlations(df, threshold=0.1)
    if len(corrs) > 0:
        print(corrs.to_string(index=False))
    else:
        print("   No correlations found above threshold")

    print("\n10 Grouped Summary:")
    gs = grouped_summary(df, 'salary', 'department')
    print(gs.to_string())

    print("\n11 Bivariate Analysis:")
    fig = plot_bivariate_analysis(df, 'age', 'salary', 'department')
    fig.savefig("solution_bivariate.png", dpi=100, bbox_inches='tight')
    plt.close(fig)
    print("   Saved to solution_bivariate.png")

    print("\n12 EDA Report:")
    report = generate_eda_report(df)
    print(report)

    print("\nAll solutions completed!")
