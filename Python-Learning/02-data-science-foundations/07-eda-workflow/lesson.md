# Module 07: Exploratory Data Analysis (EDA) Workflow

## Introduction for Swift Developers

In iOS development, you work with well-defined data models -- structs, enums, Codable
protocols. The data is typed, validated, and predictable. In data science, your raw data
is almost never clean. EDA is the disciplined process of understanding what you actually
have before you try to build anything on top of it.

Think of EDA as the "code review" of your data. You would never ship code without
reviewing it. Similarly, you should never build models without thoroughly exploring
the data first.

This module teaches a systematic, repeatable EDA workflow that you can apply to any
dataset.

---

## 1. The Systematic EDA Process

A thorough EDA follows this sequence:

```
1. Understand Structure    --> shape, dtypes, columns, first/last rows
2. Check Data Quality      --> missing values, duplicates, invalid entries
3. Univariate Analysis     --> distribution of each variable independently
4. Bivariate Analysis      --> relationships between pairs of variables
5. Multivariate Analysis   --> interactions across multiple variables
6. Document Findings       --> summarize insights, flag issues, recommend next steps
```

Every step informs the next. Missing values discovered in step 2 affect how you
interpret distributions in step 3. Outliers found in step 3 affect correlations
in step 4.

---

## 2. Step 1: Understand Structure

The very first thing you do with any new dataset:

```python
import pandas as pd
import numpy as np

# Load your data
df = pd.read_csv("data.csv")

# --- Shape and Size ---
print(f"Shape: {df.shape}")           # (rows, columns)
print(f"Memory: {df.memory_usage(deep=True).sum() / 1e6:.2f} MB")

# --- First/Last Rows ---
print(df.head(10))                    # first 10 rows
print(df.tail(5))                     # last 5 rows
print(df.sample(5, random_state=42))  # 5 random rows

# --- Column Info ---
print(df.columns.tolist())            # column names as a list
print(df.dtypes)                      # data types of each column
print(df.info())                      # comprehensive summary

# --- Quick Counts ---
print(f"Numeric columns: {df.select_dtypes(include=[np.number]).columns.tolist()}")
print(f"Categorical columns: {df.select_dtypes(include=['object', 'category']).columns.tolist()}")
print(f"Datetime columns: {df.select_dtypes(include=['datetime']).columns.tolist()}")
```

### Structured Summary Function

```python
def structure_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create a structured summary of all columns."""
    summary = pd.DataFrame({
        'dtype': df.dtypes,
        'non_null': df.count(),
        'null_count': df.isnull().sum(),
        'null_pct': (df.isnull().sum() / len(df) * 100).round(2),
        'unique': df.nunique(),
        'sample_value': df.iloc[0] if len(df) > 0 else None,
    })
    return summary

print(structure_summary(df))
```

---

## 3. Step 2: Data Quality Assessment

### Missing Values

```python
# --- Missing Value Analysis ---
def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Generate a detailed missing value report."""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)

    report = pd.DataFrame({
        'missing_count': missing,
        'missing_pct': missing_pct,
        'dtype': df.dtypes,
    })
    report = report[report['missing_count'] > 0].sort_values(
        'missing_pct', ascending=False
    )
    return report

print(missing_value_report(df))

# --- Visualize Missing Patterns ---
import matplotlib.pyplot as plt
import seaborn as sns

def plot_missing_values(df: pd.DataFrame) -> plt.Figure:
    """Create a heatmap showing missing value patterns."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Bar chart of missing percentages
    missing_pct = (df.isnull().sum() / len(df) * 100)
    missing_pct = missing_pct[missing_pct > 0].sort_values(ascending=True)
    if len(missing_pct) > 0:
        missing_pct.plot(kind='barh', ax=axes[0], color='coral')
        axes[0].set_title('Missing Values (%)')
        axes[0].set_xlabel('Percentage')
    else:
        axes[0].text(0.5, 0.5, 'No missing values!',
                     ha='center', va='center', fontsize=14)
        axes[0].set_title('Missing Values (%)')

    # Heatmap of missing pattern (sample if large)
    sample = df.sample(min(200, len(df)), random_state=42) if len(df) > 200 else df
    sns.heatmap(sample.isnull(), cbar=True, yticklabels=False,
                cmap='YlOrRd', ax=axes[1])
    axes[1].set_title('Missing Value Pattern')

    fig.tight_layout()
    return fig
```

### Duplicates

```python
# --- Duplicate Detection ---
def duplicate_report(df: pd.DataFrame) -> dict:
    """Analyze duplicates in the dataset."""
    n_exact_dupes = df.duplicated().sum()
    n_rows = len(df)

    report = {
        'total_rows': n_rows,
        'exact_duplicates': n_exact_dupes,
        'duplicate_pct': round(n_exact_dupes / n_rows * 100, 2),
        'unique_rows': n_rows - n_exact_dupes,
    }

    # Check for duplicates in potential ID columns
    for col in df.columns:
        if df[col].nunique() == n_rows:
            report[f'{col}_is_unique_id'] = True
        elif df[col].nunique() > n_rows * 0.9:
            report[f'{col}_near_unique'] = df[col].nunique()

    return report

print(duplicate_report(df))

# Show duplicate rows
dupes = df[df.duplicated(keep=False)]
if len(dupes) > 0:
    print(f"\nDuplicate rows ({len(dupes)}):")
    print(dupes.sort_values(df.columns.tolist()).head(10))
```

### Data Type Validation

```python
def validate_dtypes(df: pd.DataFrame) -> list[str]:
    """Check for potential dtype issues."""
    issues = []

    for col in df.columns:
        # Numeric columns stored as strings
        if df[col].dtype == 'object':
            try:
                pd.to_numeric(df[col].dropna())
                issues.append(f"'{col}' looks numeric but stored as string")
            except (ValueError, TypeError):
                pass

        # Date columns stored as strings
        if df[col].dtype == 'object':
            sample = df[col].dropna().head(20)
            try:
                pd.to_datetime(sample)
                issues.append(f"'{col}' looks like dates but stored as string")
            except (ValueError, TypeError):
                pass

        # High-cardinality object columns (might need encoding)
        if df[col].dtype == 'object' and df[col].nunique() > 50:
            issues.append(
                f"'{col}' has {df[col].nunique()} unique values -- high cardinality"
            )

    return issues

for issue in validate_dtypes(df):
    print(f"  WARNING: {issue}")
```

### Outlier Detection

```python
def detect_outliers_iqr(df: pd.DataFrame) -> pd.DataFrame:
    """Detect outliers in numeric columns using IQR method."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    results = []

    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower) | (df[col] > upper)]

        results.append({
            'column': col,
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'lower_bound': lower,
            'upper_bound': upper,
            'n_outliers': len(outliers),
            'pct_outliers': round(len(outliers) / len(df) * 100, 2),
        })

    return pd.DataFrame(results)

print(detect_outliers_iqr(df))
```

---

## 4. Step 3: Univariate Analysis

Examine each variable independently to understand its distribution.

### Numeric Variables

```python
def univariate_numeric(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
    """Analyze distributions of all numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    stats = df[numeric_cols].describe().T
    stats['skewness'] = df[numeric_cols].skew()
    stats['kurtosis'] = df[numeric_cols].kurtosis()

    # Create distribution plots
    n_cols = len(numeric_cols)
    n_rows = (n_cols + 2) // 3
    fig, axes = plt.subplots(n_rows, 3, figsize=(15, 4 * n_rows))
    axes = axes.flatten() if n_cols > 3 else [axes] if n_cols == 1 else axes.flatten()

    for i, col in enumerate(numeric_cols):
        if i < len(axes):
            ax = axes[i]
            sns.histplot(df[col].dropna(), kde=True, ax=ax, color='steelblue')
            ax.axvline(df[col].mean(), color='red', linestyle='--',
                       label=f'Mean: {df[col].mean():.2f}')
            ax.axvline(df[col].median(), color='green', linestyle='-.',
                       label=f'Median: {df[col].median():.2f}')
            ax.set_title(f'{col} Distribution')
            ax.legend(fontsize=8)

    # Hide unused subplots
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.tight_layout()
    return stats, fig

stats, fig = univariate_numeric(df)
print(stats)
fig.savefig("univariate_numeric.png", dpi=150)
plt.close(fig)
```

### Categorical Variables

```python
def univariate_categorical(df: pd.DataFrame) -> plt.Figure:
    """Analyze distributions of all categorical columns."""
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    n_cols = len(cat_cols)

    if n_cols == 0:
        print("No categorical columns found.")
        return plt.figure()

    n_rows = (n_cols + 1) // 2
    fig, axes = plt.subplots(n_rows, 2, figsize=(14, 4 * n_rows))
    axes = np.array(axes).flatten()

    for i, col in enumerate(cat_cols):
        if i < len(axes):
            value_counts = df[col].value_counts().head(15)  # top 15
            value_counts.plot(kind='barh', ax=axes[i], color='steelblue')
            axes[i].set_title(f'{col} (top {min(15, len(value_counts))} values)')
            axes[i].set_xlabel('Count')

            # Show percentage on bars
            total = len(df)
            for bar in axes[i].patches:
                width = bar.get_width()
                axes[i].text(width + total * 0.01,
                           bar.get_y() + bar.get_height() / 2,
                           f'{width/total:.1%}',
                           va='center', fontsize=8)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.tight_layout()
    return fig
```

---

## 5. Step 4: Bivariate Analysis

Examine relationships between pairs of variables.

### Numeric vs Numeric

```python
def bivariate_numeric(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
    """Analyze correlations between numeric variables."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr = df[numeric_cols].corr()

    # Correlation heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))  # upper triangle mask
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
                cmap='coolwarm', center=0, square=True,
                linewidths=0.5, ax=ax)
    ax.set_title('Correlation Matrix (Lower Triangle)')
    fig.tight_layout()

    return corr, fig

# Find strong correlations
def find_strong_correlations(corr: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Extract pairs with strong correlations."""
    pairs = []
    cols = corr.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr.iloc[i, j]
            if abs(val) >= threshold:
                pairs.append({
                    'var1': cols[i],
                    'var2': cols[j],
                    'correlation': round(val, 3),
                    'strength': 'strong' if abs(val) >= 0.7 else 'moderate'
                })
    return pd.DataFrame(pairs).sort_values('correlation', key=abs, ascending=False)
```

### Numeric vs Categorical

```python
def bivariate_num_cat(df: pd.DataFrame, numeric_col: str,
                      categorical_col: str) -> plt.Figure:
    """Compare numeric distribution across categories."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Box plot
    sns.boxplot(data=df, x=categorical_col, y=numeric_col, ax=axes[0])
    axes[0].set_title(f'{numeric_col} by {categorical_col} (Box)')
    axes[0].tick_params(axis='x', rotation=45)

    # Violin plot
    sns.violinplot(data=df, x=categorical_col, y=numeric_col, ax=axes[1])
    axes[1].set_title(f'{numeric_col} by {categorical_col} (Violin)')
    axes[1].tick_params(axis='x', rotation=45)

    # Strip plot (individual points)
    sns.stripplot(data=df, x=categorical_col, y=numeric_col,
                  alpha=0.4, jitter=True, ax=axes[2])
    axes[2].set_title(f'{numeric_col} by {categorical_col} (Strip)')
    axes[2].tick_params(axis='x', rotation=45)

    fig.tight_layout()
    return fig
```

### Categorical vs Categorical

```python
def bivariate_cat_cat(df: pd.DataFrame, col1: str, col2: str) -> plt.Figure:
    """Analyze relationship between two categorical variables."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Crosstab heatmap
    ct = pd.crosstab(df[col1], df[col2], normalize='index')
    sns.heatmap(ct, annot=True, fmt='.2f', cmap='YlOrRd', ax=axes[0])
    axes[0].set_title(f'{col1} vs {col2} (Row-Normalized)')

    # Stacked bar chart
    ct_raw = pd.crosstab(df[col1], df[col2])
    ct_raw.plot(kind='bar', stacked=True, ax=axes[1], colormap='Set2')
    axes[1].set_title(f'{col1} vs {col2} (Stacked)')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].legend(title=col2)

    fig.tight_layout()
    return fig
```

---

## 6. Step 5: Multivariate Analysis

Look at interactions among three or more variables.

```python
# Pair plot with color
def multivariate_overview(df: pd.DataFrame,
                          hue_col: str | None = None) -> None:
    """Create a comprehensive multivariate overview."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns[:6]  # limit to 6
    subset = df[numeric_cols].copy()
    if hue_col and hue_col in df.columns:
        subset[hue_col] = df[hue_col]

    g = sns.pairplot(subset, hue=hue_col, diag_kind='kde',
                     plot_kws={'alpha': 0.5, 's': 20})
    g.savefig("multivariate_pairplot.png", dpi=150)
    plt.close('all')

# Parallel coordinates (great for high-dimensional data)
from pandas.plotting import parallel_coordinates

def plot_parallel_coordinates(df: pd.DataFrame, class_col: str) -> plt.Figure:
    """Create a parallel coordinates plot."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Normalize columns to [0, 1] for fair comparison
    plot_df = df[numeric_cols + [class_col]].copy()
    for col in numeric_cols:
        col_min = plot_df[col].min()
        col_max = plot_df[col].max()
        if col_max > col_min:
            plot_df[col] = (plot_df[col] - col_min) / (col_max - col_min)

    fig, ax = plt.subplots(figsize=(14, 6))
    parallel_coordinates(plot_df, class_col, ax=ax, alpha=0.3)
    ax.set_title('Parallel Coordinates Plot')
    ax.legend(loc='upper right')
    fig.tight_layout()
    return fig
```

---

## 7. Step 6: Document Findings

The most underrated step. Create a summary of what you learned.

```python
def generate_eda_report(df: pd.DataFrame) -> str:
    """Generate a text-based EDA summary report."""
    lines = []
    lines.append("=" * 60)
    lines.append("EXPLORATORY DATA ANALYSIS REPORT")
    lines.append("=" * 60)

    # Structure
    lines.append(f"\n1. DATASET STRUCTURE")
    lines.append(f"   Rows: {df.shape[0]:,}")
    lines.append(f"   Columns: {df.shape[1]}")
    lines.append(f"   Memory: {df.memory_usage(deep=True).sum() / 1e6:.2f} MB")

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    lines.append(f"   Numeric columns: {len(numeric_cols)}")
    lines.append(f"   Categorical columns: {len(cat_cols)}")

    # Data Quality
    lines.append(f"\n2. DATA QUALITY")
    total_missing = df.isnull().sum().sum()
    total_cells = df.shape[0] * df.shape[1]
    lines.append(f"   Total missing: {total_missing:,} / {total_cells:,} "
                 f"({total_missing/total_cells*100:.1f}%)")
    lines.append(f"   Duplicate rows: {df.duplicated().sum()}")

    cols_with_missing = df.columns[df.isnull().any()].tolist()
    if cols_with_missing:
        lines.append(f"   Columns with missing data: {cols_with_missing}")

    # Numeric summaries
    lines.append(f"\n3. NUMERIC COLUMN SUMMARIES")
    for col in numeric_cols:
        skew = df[col].skew()
        skew_label = "symmetric" if abs(skew) < 0.5 else \
                     "moderately skewed" if abs(skew) < 1 else "highly skewed"
        lines.append(f"   {col}:")
        lines.append(f"     Range: [{df[col].min():.2f}, {df[col].max():.2f}]")
        lines.append(f"     Mean: {df[col].mean():.2f}, Median: {df[col].median():.2f}")
        lines.append(f"     Skewness: {skew:.2f} ({skew_label})")

    # Categorical summaries
    lines.append(f"\n4. CATEGORICAL COLUMN SUMMARIES")
    for col in cat_cols:
        n_unique = df[col].nunique()
        top_val = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
        lines.append(f"   {col}: {n_unique} unique values, top='{top_val}'")

    # Correlations
    if len(numeric_cols) > 1:
        lines.append(f"\n5. NOTABLE CORRELATIONS (|r| > 0.5)")
        corr = df[numeric_cols].corr()
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                r = corr.iloc[i, j]
                if abs(r) > 0.5:
                    lines.append(
                        f"   {numeric_cols[i]} <-> {numeric_cols[j]}: r={r:.3f}"
                    )

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)
```

---

## 8. Automated EDA Tools

For quick first-pass analysis, several libraries automate EDA:

### ydata-profiling (formerly pandas-profiling)

```python
# pip install ydata-profiling
from ydata_profiling import ProfileReport

# Generate a comprehensive HTML report
profile = ProfileReport(
    df,
    title="My Dataset EDA Report",
    explorative=True,
    correlations={
        "pearson": {"calculate": True},
        "spearman": {"calculate": True},
    },
)

# Save to HTML
profile.to_file("eda_report.html")

# In Jupyter notebook
profile.to_notebook_iframe()
```

### sweetviz

```python
# pip install sweetviz
import sweetviz as sv

# Analyze a single dataset
report = sv.analyze(df, target_feat="target_column")
report.show_html("sweetviz_report.html")

# Compare two datasets (train vs test)
report = sv.compare(train_df, test_df)
report.show_html("comparison_report.html")
```

### dtale

```python
# pip install dtale
import dtale

# Launch interactive web-based EDA
d = dtale.show(df)
d.open_browser()  # opens in default browser
```

---

## 9. EDA Checklist Template

Use this checklist for every new dataset:

```markdown
## EDA Checklist

### 1. Structure
- [ ] Check shape (rows x columns)
- [ ] Review column names and data types
- [ ] Inspect first/last/random rows
- [ ] Calculate memory usage
- [ ] Identify numeric vs categorical vs datetime columns

### 2. Data Quality
- [ ] Count and visualize missing values per column
- [ ] Check for duplicate rows
- [ ] Validate data types (numbers as strings? dates as strings?)
- [ ] Detect outliers (IQR or z-score method)
- [ ] Check for invalid/impossible values (negative ages, future dates)
- [ ] Verify expected ranges and categories

### 3. Univariate Analysis
- [ ] Summary statistics for all numeric columns
- [ ] Distribution plots (histograms + KDE) for numeric columns
- [ ] Check skewness and kurtosis
- [ ] Value counts and bar charts for categorical columns
- [ ] Identify rare categories (< 1% frequency)

### 4. Bivariate Analysis
- [ ] Correlation matrix heatmap
- [ ] Scatter plots for strongly correlated numeric pairs
- [ ] Box/violin plots for numeric vs categorical
- [ ] Crosstabs for categorical vs categorical
- [ ] Statistical tests where appropriate

### 5. Multivariate Analysis
- [ ] Pair plots for key variables
- [ ] Grouped analysis (segment by key categories)
- [ ] Feature interaction plots

### 6. Documentation
- [ ] Summary of key findings
- [ ] List of data quality issues
- [ ] Recommendations for cleaning/engineering
- [ ] Questions for domain experts
```

---

## 10. Complete EDA Walkthrough

Let us walk through a complete EDA on a sample dataset:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- Generate Sample Data ---
np.random.seed(42)
n = 500

df = pd.DataFrame({
    'age': np.random.normal(35, 10, n).astype(int).clip(18, 70),
    'income': np.random.lognormal(10.5, 0.7, n).round(2),
    'education_years': np.random.choice([12, 14, 16, 18, 20], n,
                                         p=[0.2, 0.25, 0.3, 0.15, 0.1]),
    'department': np.random.choice(
        ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance'], n,
        p=[0.3, 0.25, 0.2, 0.15, 0.1]
    ),
    'satisfaction': np.random.choice([1, 2, 3, 4, 5], n,
                                      p=[0.05, 0.1, 0.3, 0.35, 0.2]),
    'tenure_months': np.random.exponential(36, n).astype(int),
})

# Inject some realistic issues
df.loc[np.random.choice(n, 25, replace=False), 'income'] = np.nan
df.loc[np.random.choice(n, 15, replace=False), 'age'] = np.nan
df.loc[10, 'income'] = 5_000_000  # extreme outlier
df = pd.concat([df, df.iloc[:5]])  # add a few duplicates

# --- Step 1: Structure ---
print("STEP 1: STRUCTURE")
print(f"Shape: {df.shape}")
print(f"\nDtypes:\n{df.dtypes}")
print(f"\nHead:\n{df.head()}")

# --- Step 2: Data Quality ---
print("\n\nSTEP 2: DATA QUALITY")
print(f"Missing values:\n{df.isnull().sum()}")
print(f"\nDuplicates: {df.duplicated().sum()}")

# Remove duplicates
df = df.drop_duplicates().reset_index(drop=True)

# --- Step 3: Univariate Analysis ---
print("\n\nSTEP 3: UNIVARIATE ANALYSIS")
print(df.describe())
print(f"\nSkewness:\n{df.select_dtypes(include=[np.number]).skew()}")

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
for i, col in enumerate(df.select_dtypes(include=[np.number]).columns):
    ax = axes.flatten()[i]
    sns.histplot(df[col].dropna(), kde=True, ax=ax, color='steelblue')
    ax.set_title(f'{col} distribution')
fig.tight_layout()
fig.savefig("eda_univariate.png", dpi=150)
plt.close(fig)

# --- Step 4: Bivariate Analysis ---
print("\n\nSTEP 4: BIVARIATE ANALYSIS")
numeric_cols = df.select_dtypes(include=[np.number]).columns
corr = df[numeric_cols].corr()
print(f"Correlation matrix:\n{corr}")

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax)
ax.set_title('Correlation Heatmap')
fig.tight_layout()
fig.savefig("eda_correlation.png", dpi=150)
plt.close(fig)

# --- Step 5: Multivariate ---
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=df, x='age', y='income', hue='department',
                style='department', alpha=0.6, ax=ax)
ax.set_title('Age vs Income by Department')
fig.savefig("eda_multivariate.png", dpi=150)
plt.close(fig)

# --- Step 6: Document ---
print("\n\nSTEP 6: KEY FINDINGS")
print("1. Income is right-skewed (log-normal distribution)")
print("2. One extreme income outlier ($5M) needs investigation")
print("3. 25 missing income values, 15 missing age values")
print("4. 5 duplicate rows removed")
print("5. Age distribution is approximately normal, centered around 35")
```

---

## Summary

| EDA Step | Key Questions | Tools |
|---|---|---|
| Structure | How big? What columns? What types? | `.shape`, `.dtypes`, `.info()` |
| Quality | Missing data? Duplicates? Invalid? | `.isnull()`, `.duplicated()`, IQR |
| Univariate | What does each variable look like? | Histograms, box plots, value_counts |
| Bivariate | How do variables relate? | Correlation, scatter, grouped box |
| Multivariate | Complex interactions? | Pair plots, faceted plots |
| Document | What did we learn? | Text summary, annotated notebooks |

**Key takeaway for Swift developers**: EDA is not something you do once and move on.
It is an iterative process. As you clean data, you re-examine distributions. As you
engineer features, you check correlations again. Build the habit of systematic
exploration, and your models will be far more reliable.

---

## Next Steps

- Practice the full EDA workflow on a Kaggle dataset
- Set up your own EDA template that you reuse for every project
- Try the automated tools (ydata-profiling, sweetviz) for quick overviews
- Move on to Module 08: Feature Engineering to learn what to do with your EDA findings
