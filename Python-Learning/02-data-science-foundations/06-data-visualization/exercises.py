"""
Module 06: Data Visualization - Exercises
==========================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Each function should return a matplotlib Figure object (NOT call plt.show()).
- Run this file to check your work: `python exercises.py`
- Exercises that produce figures will save them to disk for visual inspection.

Difficulty levels:
  Easy   - Direct use of a single plot type
  Medium - Combining features or multiple plot elements
  Hard   - Custom layouts, styling, or multi-library integration

Required packages: matplotlib, seaborn, numpy, pandas
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving figures
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure


# =============================================================================
# MATPLOTLIB BASICS
# =============================================================================

# Exercise 1: Simple Line Plot
# Difficulty: Easy
# Create a line plot of sin(x) and cos(x) on the same axes.
def plot_trig_functions() -> Figure:
    """Create a figure with sin(x) and cos(x) plotted from 0 to 2*pi.

    Requirements:
    - x values: 100 points from 0 to 2*pi
    - sin(x) as a blue solid line with label 'sin(x)'
    - cos(x) as a red dashed line with label 'cos(x)'
    - Include a legend, grid, title ('Trigonometric Functions'),
      and axis labels ('x', 'y')
    - Return the Figure object
    """
    pass


# Exercise 2: Bar Chart with Labels
# Difficulty: Easy
# Create a horizontal bar chart showing programming language popularity.
def plot_language_popularity() -> Figure:
    """Create a horizontal bar chart of programming language popularity.

    Data:
        languages = ['Python', 'JavaScript', 'Java', 'C++', 'Swift', 'Rust']
        popularity = [92, 88, 75, 68, 45, 42]

    Requirements:
    - Horizontal bar chart (barh)
    - Each bar should have a different color (use any color scheme)
    - Add value labels at the end of each bar (the popularity number)
    - Title: 'Programming Language Popularity 2024'
    - x-label: 'Popularity Score'
    - Return the Figure object
    """
    pass


# Exercise 3: Scatter Plot with Color Encoding
# Difficulty: Easy
# Create a scatter plot with size and color encoding.
def plot_scatter_with_encoding() -> Figure:
    """Create a scatter plot using random data with visual encoding.

    Requirements:
    - Generate 150 random points: x ~ N(0,1), y = 1.5*x + N(0,0.5)
    - Use np.random.seed(42) for reproducibility
    - Color points by their y-value using the 'viridis' colormap
    - Size points proportional to abs(x) * 50 + 10
    - Add a colorbar
    - Title: 'Scatter Plot with Visual Encoding'
    - Return the Figure object
    """
    pass


# Exercise 4: Histogram Comparison
# Difficulty: Medium
# Create overlapping histograms comparing two distributions.
def plot_distribution_comparison() -> Figure:
    """Create overlapping histograms of two normal distributions.

    Requirements:
    - Use np.random.seed(42)
    - Distribution A: 1000 samples from N(0, 1) -- label 'Group A'
    - Distribution B: 1000 samples from N(2, 1.5) -- label 'Group B'
    - 30 bins, alpha=0.5 for transparency
    - Add vertical dashed lines at each group's mean
    - Include a legend
    - Title: 'Distribution Comparison'
    - Return the Figure object
    """
    pass


# Exercise 5: Subplots Grid
# Difficulty: Medium
# Create a 2x2 grid showing different views of the same data.
def plot_four_views(data: np.ndarray | None = None) -> Figure:
    """Create a 2x2 subplot grid showing four views of the same data.

    If data is None, generate 500 samples from N(0,1) with seed 42.

    Subplot layout:
    - Top-left: Histogram (30 bins, blue)
    - Top-right: Box plot (horizontal, green)
    - Bottom-left: KDE-style line plot (use np.histogram + smoothing,
                   or just plot a fine histogram with many bins as a line)
    - Bottom-right: QQ-like plot -- sorted data vs theoretical quantiles
                    (plot sorted(data) against np.linspace(min, max, len(data)))

    Requirements:
    - Figure size: (12, 10)
    - Super title: 'Four Views of the Data'
    - Use tight_layout()
    - Return the Figure object
    """
    pass


# =============================================================================
# SEABORN
# =============================================================================

# Exercise 6: Seaborn Box Plot
# Difficulty: Easy
# Create a grouped box plot using Seaborn with the tips dataset.
def plot_tips_boxplot() -> Figure:
    """Create a box plot of total_bill by day, colored by time.

    Requirements:
    - Load the 'tips' dataset from seaborn
    - x='day', y='total_bill', hue='time'
    - Use palette='Set2'
    - Title: 'Bill Distribution by Day and Time'
    - Return the Figure object
    """
    pass


# Exercise 7: Seaborn Heatmap
# Difficulty: Medium
# Create a correlation heatmap for a dataset.
def plot_correlation_heatmap() -> Figure:
    """Create a correlation heatmap using the penguins dataset.

    Requirements:
    - Load the 'penguins' dataset from seaborn
    - Compute correlation matrix of numeric columns only
    - Use sns.heatmap with annot=True, fmt='.2f'
    - Use cmap='coolwarm', center=0
    - Title: 'Penguin Measurements Correlation'
    - Return the Figure object
    """
    pass


# Exercise 8: Seaborn Pair Plot
# Difficulty: Medium
# Create a pair plot with custom diagonal.
def plot_iris_pairplot() -> sns.PairGrid:
    """Create a pair plot of the iris dataset.

    Requirements:
    - Load the 'iris' dataset from seaborn
    - Color by 'species'
    - Use kde on the diagonal (diag_kind='kde')
    - Use palette='husl'
    - Return the PairGrid object (which contains the figure)
    """
    pass


# Exercise 9: Combined Seaborn Visualization
# Difficulty: Hard
# Create a figure with multiple Seaborn plot types on the tips dataset.
def plot_tips_analysis() -> Figure:
    """Create a 2x2 analysis dashboard of the tips dataset.

    Requirements:
    - Load the 'tips' dataset from seaborn
    - Figure size: (14, 10)
    - Top-left: Scatter plot (total_bill vs tip, hue='smoker')
    - Top-right: Violin plot (day vs total_bill, hue='sex', split=True)
    - Bottom-left: Count plot (day, hue='time')
    - Bottom-right: Bar plot (day vs tip, hue='smoker')
    - Super title: 'Restaurant Tips Analysis'
    - Use tight_layout()
    - Return the Figure object
    """
    pass


# =============================================================================
# PLOTLY (return dicts or save files since we can't display interactively)
# =============================================================================

# Exercise 10: Plotly Express Scatter
# Difficulty: Easy
# Create an interactive scatter plot and save to HTML.
def create_plotly_scatter(output_path: str = "plotly_scatter_exercise.html") -> dict:
    """Create a Plotly Express scatter plot of the iris dataset.

    Requirements:
    - Use plotly.express with the iris dataset (px.data.iris())
    - x='sepal_width', y='sepal_length', color='species'
    - size='petal_length'
    - title: 'Iris Dataset: Sepal Dimensions'
    - Save to output_path as HTML
    - Return the figure as a dict (fig.to_dict())

    Note: If plotly is not installed, return an empty dict.
    """
    pass


# Exercise 11: Plotly Subplots
# Difficulty: Hard
# Create a multi-panel Plotly figure.
def create_plotly_dashboard(output_path: str = "plotly_dashboard.html") -> dict:
    """Create a 2x2 Plotly dashboard using graph_objects and subplots.

    Requirements:
    - Use make_subplots with 2 rows, 2 columns
    - Top-left: Line plot of sin(x) for x in [0, 4*pi] with 200 points
    - Top-right: Bar chart of 5 random values (seed=42)
    - Bottom-left: Scatter plot of 100 random (x, y) points (seed=42)
    - Bottom-right: Histogram of 500 random normal values (seed=42)
    - Set overall title: 'Plotly Dashboard'
    - Set height=600
    - Save to output_path
    - Return the figure as a dict (fig.to_dict())

    Note: If plotly is not installed, return an empty dict.
    """
    pass


# =============================================================================
# ADVANCED / STYLING
# =============================================================================

# Exercise 12: Publication-Quality Figure
# Difficulty: Hard
# Create a polished, publication-ready figure.
def plot_publication_figure() -> Figure:
    """Create a publication-quality figure demonstrating advanced styling.

    Requirements:
    - Use np.random.seed(42)
    - Generate data: x = linspace(0, 10, 200), y = sin(x) * exp(-x/5) + noise
      where noise is N(0, 0.05)
    - Figure size: (10, 6)
    - Plot the noisy data as small gray dots (alpha=0.4, s=10)
    - Plot a smooth curve (sin(x) * exp(-x/5)) as a thick blue line
    - Add a shaded region between the smooth curve +/- 0.15
      using ax.fill_between() with alpha=0.2
    - Remove top and right spines
    - Add an annotation pointing to the first peak with an arrow
    - Title: 'Damped Oscillation with Noise'
    - x-label: 'Time (s)', y-label: 'Amplitude'
    - Legend with entries: 'Observations', 'True Signal', 'Confidence Band'
    - Set DPI to 300 equivalent styling (line widths, font sizes)
    - Return the Figure object
    """
    pass


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
            # Save figures to files for inspection
            if isinstance(result, Figure):
                filename = f"exercise_{name.lower().replace(' ', '_')}.png"
                result.savefig(filename, dpi=100, bbox_inches='tight')
                plt.close(result)
                print(f"      Saved to {filename}")
            elif hasattr(result, 'savefig'):
                # PairGrid and similar objects
                filename = f"exercise_{name.lower().replace(' ', '_')}.png"
                result.savefig(filename, dpi=100, bbox_inches='tight')
                plt.close('all')
                print(f"      Saved to {filename}")
    except Exception as e:
        print(f"  [!] {name} -- error: {e}")


if __name__ == "__main__":
    print("Module 06: Data Visualization Exercises")
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
