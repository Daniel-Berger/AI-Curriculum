"""
Module 06: Data Visualization - Solutions
==========================================
Complete solutions for all exercises.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure


# =============================================================================
# Exercise 1: Simple Line Plot
# =============================================================================

def plot_trig_functions() -> Figure:
    """Create a figure with sin(x) and cos(x) plotted from 0 to 2*pi."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), 'b-', linewidth=2, label='sin(x)')
    ax.plot(x, np.cos(x), 'r--', linewidth=2, label='cos(x)')

    ax.set_title('Trigonometric Functions', fontsize=14)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    return fig


# =============================================================================
# Exercise 2: Bar Chart with Labels
# =============================================================================

def plot_language_popularity() -> Figure:
    """Create a horizontal bar chart of programming language popularity."""
    fig, ax = plt.subplots(figsize=(10, 6))

    languages = ['Python', 'JavaScript', 'Java', 'C++', 'Swift', 'Rust']
    popularity = [92, 88, 75, 68, 45, 42]
    colors = ['#3776AB', '#F7DF1E', '#ED8B00', '#00599C', '#FA7343', '#DEA584']

    bars = ax.barh(languages, popularity, color=colors, edgecolor='white',
                   linewidth=1.5)

    # Add value labels at the end of each bar
    for bar, val in zip(bars, popularity):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                str(val), ha='left', va='center', fontsize=11, fontweight='bold')

    ax.set_title('Programming Language Popularity 2024', fontsize=14)
    ax.set_xlabel('Popularity Score', fontsize=12)
    ax.set_xlim(0, 105)

    fig.tight_layout()
    return fig


# =============================================================================
# Exercise 3: Scatter Plot with Color Encoding
# =============================================================================

def plot_scatter_with_encoding() -> Figure:
    """Create a scatter plot using random data with visual encoding."""
    np.random.seed(42)
    fig, ax = plt.subplots(figsize=(10, 8))

    n = 150
    x = np.random.randn(n)
    y = 1.5 * x + np.random.randn(n) * 0.5
    sizes = np.abs(x) * 50 + 10
    colors = y

    scatter = ax.scatter(x, y, s=sizes, c=colors, cmap='viridis',
                         alpha=0.7, edgecolors='white', linewidth=0.5)

    fig.colorbar(scatter, ax=ax, label='y value')
    ax.set_title('Scatter Plot with Visual Encoding', fontsize=14)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    return fig


# =============================================================================
# Exercise 4: Histogram Comparison
# =============================================================================

def plot_distribution_comparison() -> Figure:
    """Create overlapping histograms of two normal distributions."""
    np.random.seed(42)
    fig, ax = plt.subplots(figsize=(10, 6))

    group_a = np.random.randn(1000)
    group_b = np.random.randn(1000) * 1.5 + 2

    ax.hist(group_a, bins=30, alpha=0.5, label='Group A', color='steelblue')
    ax.hist(group_b, bins=30, alpha=0.5, label='Group B', color='coral')

    # Mean lines
    ax.axvline(group_a.mean(), color='steelblue', linestyle='--', linewidth=2,
               label=f'Mean A ({group_a.mean():.2f})')
    ax.axvline(group_b.mean(), color='coral', linestyle='--', linewidth=2,
               label=f'Mean B ({group_b.mean():.2f})')

    ax.set_title('Distribution Comparison', fontsize=14)
    ax.set_xlabel('Value', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend(fontsize=10)

    fig.tight_layout()
    return fig


# =============================================================================
# Exercise 5: Subplots Grid
# =============================================================================

def plot_four_views(data: np.ndarray | None = None) -> Figure:
    """Create a 2x2 subplot grid showing four views of the same data."""
    if data is None:
        np.random.seed(42)
        data = np.random.randn(500)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Top-left: Histogram
    axes[0, 0].hist(data, bins=30, color='steelblue', edgecolor='white', alpha=0.7)
    axes[0, 0].set_title('Histogram')
    axes[0, 0].set_xlabel('Value')
    axes[0, 0].set_ylabel('Frequency')

    # Top-right: Box plot
    axes[0, 1].boxplot(data, vert=False, patch_artist=True,
                       boxprops=dict(facecolor='lightgreen', alpha=0.7))
    axes[0, 1].set_title('Box Plot')
    axes[0, 1].set_xlabel('Value')

    # Bottom-left: KDE-style line (fine histogram as line)
    counts, bin_edges = np.histogram(data, bins=80, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    axes[1, 0].plot(bin_centers, counts, color='steelblue', linewidth=2)
    axes[1, 0].fill_between(bin_centers, counts, alpha=0.3, color='steelblue')
    axes[1, 0].set_title('Density Estimate')
    axes[1, 0].set_xlabel('Value')
    axes[1, 0].set_ylabel('Density')

    # Bottom-right: Sorted data vs theoretical quantiles
    sorted_data = np.sort(data)
    theoretical = np.linspace(sorted_data.min(), sorted_data.max(), len(sorted_data))
    axes[1, 1].plot(theoretical, sorted_data, 'o', markersize=2,
                    color='steelblue', alpha=0.5)
    axes[1, 1].plot([theoretical.min(), theoretical.max()],
                    [theoretical.min(), theoretical.max()],
                    'r--', linewidth=2, label='y=x reference')
    axes[1, 1].set_title('QQ-style Plot')
    axes[1, 1].set_xlabel('Theoretical Quantiles')
    axes[1, 1].set_ylabel('Observed Values')
    axes[1, 1].legend()

    fig.suptitle('Four Views of the Data', fontsize=16)
    fig.tight_layout()
    return fig


# =============================================================================
# Exercise 6: Seaborn Box Plot
# =============================================================================

def plot_tips_boxplot() -> Figure:
    """Create a box plot of total_bill by day, colored by time."""
    tips = sns.load_dataset("tips")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=tips, x='day', y='total_bill', hue='time',
                palette='Set2', ax=ax)
    ax.set_title('Bill Distribution by Day and Time', fontsize=14)
    ax.set_xlabel('Day', fontsize=12)
    ax.set_ylabel('Total Bill ($)', fontsize=12)

    fig.tight_layout()
    return fig


# =============================================================================
# Exercise 7: Seaborn Heatmap
# =============================================================================

def plot_correlation_heatmap() -> Figure:
    """Create a correlation heatmap using the penguins dataset."""
    penguins = sns.load_dataset("penguins")

    fig, ax = plt.subplots(figsize=(10, 8))
    numeric_cols = penguins.select_dtypes(include=[np.number])
    corr = numeric_cols.corr()

    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, square=True, linewidths=1, ax=ax)
    ax.set_title('Penguin Measurements Correlation', fontsize=14)

    fig.tight_layout()
    return fig


# =============================================================================
# Exercise 8: Seaborn Pair Plot
# =============================================================================

def plot_iris_pairplot() -> sns.PairGrid:
    """Create a pair plot of the iris dataset."""
    iris = sns.load_dataset("iris")

    g = sns.pairplot(iris, hue='species', diag_kind='kde',
                     palette='husl', plot_kws={'alpha': 0.6, 's': 30})

    return g


# =============================================================================
# Exercise 9: Combined Seaborn Visualization
# =============================================================================

def plot_tips_analysis() -> Figure:
    """Create a 2x2 analysis dashboard of the tips dataset."""
    tips = sns.load_dataset("tips")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Top-left: Scatter plot
    sns.scatterplot(data=tips, x='total_bill', y='tip',
                    hue='smoker', ax=axes[0, 0], palette='Set1')
    axes[0, 0].set_title('Total Bill vs Tip')

    # Top-right: Violin plot
    sns.violinplot(data=tips, x='day', y='total_bill',
                   hue='sex', split=True, ax=axes[0, 1], palette='Set2')
    axes[0, 1].set_title('Bill Distribution by Day & Sex')

    # Bottom-left: Count plot
    sns.countplot(data=tips, x='day', hue='time',
                  ax=axes[1, 0], palette='pastel')
    axes[1, 0].set_title('Visit Counts by Day')

    # Bottom-right: Bar plot
    sns.barplot(data=tips, x='day', y='tip', hue='smoker',
                ax=axes[1, 1], palette='muted')
    axes[1, 1].set_title('Average Tip by Day')

    fig.suptitle('Restaurant Tips Analysis', fontsize=16)
    fig.tight_layout()
    return fig


# =============================================================================
# Exercise 10: Plotly Express Scatter
# =============================================================================

def create_plotly_scatter(output_path: str = "plotly_scatter_exercise.html") -> dict:
    """Create a Plotly Express scatter plot of the iris dataset."""
    try:
        import plotly.express as px
    except ImportError:
        return {}

    df = px.data.iris()
    fig = px.scatter(
        df,
        x='sepal_width',
        y='sepal_length',
        color='species',
        size='petal_length',
        title='Iris Dataset: Sepal Dimensions',
        labels={
            'sepal_width': 'Sepal Width (cm)',
            'sepal_length': 'Sepal Length (cm)',
        }
    )
    fig.update_layout(template='plotly_white')
    fig.write_html(output_path)
    return fig.to_dict()


# =============================================================================
# Exercise 11: Plotly Subplots
# =============================================================================

def create_plotly_dashboard(output_path: str = "plotly_dashboard.html") -> dict:
    """Create a 2x2 Plotly dashboard using graph_objects and subplots."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        return {}

    np.random.seed(42)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Sin Wave", "Bar Chart", "Scatter", "Histogram")
    )

    # Top-left: Line plot
    x = np.linspace(0, 4 * np.pi, 200)
    fig.add_trace(
        go.Scatter(x=x, y=np.sin(x), mode='lines',
                   line=dict(color='steelblue', width=2), name='sin(x)'),
        row=1, col=1
    )

    # Top-right: Bar chart
    bar_values = np.random.randint(10, 100, 5)
    fig.add_trace(
        go.Bar(x=['A', 'B', 'C', 'D', 'E'], y=bar_values,
               marker_color=['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336'],
               name='Values'),
        row=1, col=2
    )

    # Bottom-left: Scatter
    scatter_x = np.random.randn(100)
    scatter_y = np.random.randn(100)
    fig.add_trace(
        go.Scatter(x=scatter_x, y=scatter_y, mode='markers',
                   marker=dict(color='coral', size=6), name='Points'),
        row=2, col=1
    )

    # Bottom-right: Histogram
    hist_data = np.random.randn(500)
    fig.add_trace(
        go.Histogram(x=hist_data, nbinsx=30,
                     marker_color='steelblue', name='Distribution'),
        row=2, col=2
    )

    fig.update_layout(
        height=600,
        title_text='Plotly Dashboard',
        showlegend=False,
        template='plotly_white'
    )
    fig.write_html(output_path)
    return fig.to_dict()


# =============================================================================
# Exercise 12: Publication-Quality Figure
# =============================================================================

def plot_publication_figure() -> Figure:
    """Create a publication-quality figure demonstrating advanced styling."""
    np.random.seed(42)

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.linspace(0, 10, 200)
    y_true = np.sin(x) * np.exp(-x / 5)
    noise = np.random.randn(200) * 0.05
    y_noisy = y_true + noise

    # Noisy data as small gray dots
    ax.scatter(x, y_noisy, s=10, color='gray', alpha=0.4, label='Observations',
               zorder=2)

    # Smooth curve
    ax.plot(x, y_true, color='#1a73e8', linewidth=2.5, label='True Signal',
            zorder=3)

    # Confidence band
    ax.fill_between(x, y_true - 0.15, y_true + 0.15, color='#1a73e8',
                    alpha=0.2, label='Confidence Band', zorder=1)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)

    # Find the first peak (at x ~ pi/2)
    peak_idx = np.argmax(y_true[:50])  # first peak in first quarter
    peak_x = x[peak_idx]
    peak_y = y_true[peak_idx]

    # Annotation with arrow
    ax.annotate(
        f'First Peak\n({peak_x:.1f}, {peak_y:.2f})',
        xy=(peak_x, peak_y),
        xytext=(peak_x + 2, peak_y + 0.3),
        fontsize=11,
        arrowprops=dict(arrowstyle='->', color='#d93025', lw=2),
        color='#d93025',
        fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                  edgecolor='#d93025', alpha=0.8)
    )

    ax.set_title('Damped Oscillation with Noise', fontsize=16, fontweight='bold')
    ax.set_xlabel('Time (s)', fontsize=13)
    ax.set_ylabel('Amplitude', fontsize=13)
    ax.legend(fontsize=11, frameon=True, fancybox=True, shadow=True)
    ax.tick_params(axis='both', which='major', labelsize=11, length=6, width=1.5)
    ax.grid(True, alpha=0.2)

    fig.tight_layout()
    return fig


# =============================================================================
# SELF-CHECK / RUNNER
# =============================================================================

def run_exercise(name: str, func, *args, **kwargs):
    """Run an exercise and report results."""
    try:
        result = func(*args, **kwargs)
        if result is None:
            print(f"  [ ] {name} -- returned None (not implemented yet)")
        else:
            print(f"  [x] {name} -- completed successfully")
            if isinstance(result, Figure):
                filename = f"solution_{name.lower().replace(' ', '_')}.png"
                result.savefig(filename, dpi=100, bbox_inches='tight')
                plt.close(result)
                print(f"      Saved to {filename}")
            elif hasattr(result, 'savefig'):
                filename = f"solution_{name.lower().replace(' ', '_')}.png"
                result.savefig(filename, dpi=100, bbox_inches='tight')
                plt.close('all')
                print(f"      Saved to {filename}")
    except Exception as e:
        print(f"  [!] {name} -- error: {e}")


if __name__ == "__main__":
    print("Module 06: Data Visualization Solutions")
    print("=" * 50)
    print("\nMatplotlib Basics:")
    run_exercise("01 Trig Functions", plot_trig_functions)
    run_exercise("02 Language Popularity", plot_language_popularity)
    run_exercise("03 Scatter Encoding", plot_scatter_with_encoding)
    run_exercise("04 Distribution Comparison", plot_distribution_comparison)
    run_exercise("05 Four Views", plot_four_views)

    print("\nSeaborn:")
    run_exercise("06 Tips Boxplot", plot_tips_boxplot)
    run_exercise("07 Correlation Heatmap", plot_correlation_heatmap)
    run_exercise("08 Iris Pairplot", plot_iris_pairplot)
    run_exercise("09 Tips Analysis", plot_tips_analysis)

    print("\nPlotly:")
    run_exercise("10 Plotly Scatter", create_plotly_scatter)
    run_exercise("11 Plotly Dashboard", create_plotly_dashboard)

    print("\nAdvanced:")
    run_exercise("12 Publication Figure", plot_publication_figure)

    print("\nDone! Check generated image files for visual verification.")
