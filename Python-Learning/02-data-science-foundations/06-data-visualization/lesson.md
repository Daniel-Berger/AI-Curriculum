# Module 06: Data Visualization

## Introduction for Swift Developers

If you've worked with SwiftUI Charts or Core Plot, you know that data visualization on
Apple platforms is often tightly coupled to the UI framework. Python's visualization
ecosystem is different -- it is designed for exploration, publication, and interactivity,
with libraries ranging from static matplotlib to fully interactive Plotly dashboards.

This module covers the three most important visualization libraries: Matplotlib (the
foundation), Seaborn (statistical elegance), and Plotly (interactivity). You will learn
when to use each, how they relate, and how to produce publication-quality graphics.

---

## 1. Matplotlib -- The Foundation

Matplotlib is Python's original plotting library. Nearly every other visualization library
in the Python ecosystem either wraps it or was inspired by it.

### The Two Interfaces

Matplotlib has two APIs. Understanding both is critical:

```python
import matplotlib.pyplot as plt
import numpy as np

# ---- PYPLOT INTERFACE (quick and dirty) ----
# Similar to MATLAB. Uses implicit "current figure" state.
x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.title("Sine Wave")
plt.xlabel("x")
plt.ylabel("sin(x)")
plt.savefig("sine_wave.png")
plt.close()

# ---- OBJECT-ORIENTED INTERFACE (recommended) ----
# Explicit Figure and Axes objects. More control, more predictable.
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, np.sin(x), label="sin(x)", color="steelblue", linewidth=2)
ax.plot(x, np.cos(x), label="cos(x)", color="coral", linewidth=2)
ax.set_title("Trigonometric Functions", fontsize=16)
ax.set_xlabel("x", fontsize=12)
ax.set_ylabel("y", fontsize=12)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("trig_functions.png", dpi=150)
plt.close(fig)
```

**Swift analogy**: The pyplot interface is like using SwiftUI's implicit environment,
while the OO interface is like building UIKit views with explicit references. Always
prefer the OO interface for anything beyond a quick exploration.

### Figure and Axes Anatomy

```
Figure (the entire window/image)
 +-- Axes (a single plot area)
 |    +-- Title
 |    +-- X-axis (xlabel, ticks, limits)
 |    +-- Y-axis (ylabel, ticks, limits)
 |    +-- Plot elements (lines, bars, scatter points)
 |    +-- Legend
 |    +-- Grid
 +-- Axes (another plot in the same figure)
 +-- Suptitle (super title for the whole figure)
```

```python
# Creating a figure with specific dimensions
fig = plt.figure(figsize=(12, 8))  # width, height in inches

# Creating figure + axes together (most common)
fig, ax = plt.subplots()           # single plot
fig, axes = plt.subplots(2, 3)     # 2 rows, 3 columns of subplots
fig, (ax1, ax2) = plt.subplots(1, 2)  # 1 row, 2 columns with unpacking
```

### Core Plot Types

#### Line Plot

```python
fig, ax = plt.subplots(figsize=(10, 6))

x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), 'b-', linewidth=2, label='sin(x)')    # blue solid
ax.plot(x, np.cos(x), 'r--', linewidth=2, label='cos(x)')   # red dashed
ax.plot(x, np.sin(x) * np.exp(-x/5), 'g-.', linewidth=2,    # green dash-dot
        label='damped sin(x)')

# Format string: '[color][marker][line]'
# Colors: b=blue, r=red, g=green, k=black, etc.
# Markers: o=circle, s=square, ^=triangle, etc.
# Lines: -=solid, --=dashed, -.=dash-dot, :=dotted

ax.set_title("Line Plot Examples")
ax.legend()
ax.grid(True, alpha=0.3)
fig.savefig("line_plots.png", dpi=150, bbox_inches='tight')
plt.close(fig)
```

#### Bar Plot

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

categories = ['iOS', 'Android', 'Web', 'Backend', 'ML']
values = [85, 60, 72, 55, 90]
colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336']

# Vertical bar chart
ax1.bar(categories, values, color=colors, edgecolor='white', linewidth=1.5)
ax1.set_title("Skills by Platform")
ax1.set_ylabel("Proficiency (%)")

# Horizontal bar chart -- great for many categories
ax2.barh(categories, values, color=colors, edgecolor='white', linewidth=1.5)
ax2.set_title("Skills by Platform (Horizontal)")
ax2.set_xlabel("Proficiency (%)")

fig.tight_layout()
fig.savefig("bar_plots.png", dpi=150)
plt.close(fig)
```

#### Grouped and Stacked Bars

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

languages = ['Python', 'Swift', 'JS', 'Rust']
year_2023 = [88, 75, 90, 45]
year_2024 = [92, 78, 85, 62]

x = np.arange(len(languages))
width = 0.35

# Grouped bar chart
ax1.bar(x - width/2, year_2023, width, label='2023', color='steelblue')
ax1.bar(x + width/2, year_2024, width, label='2024', color='coral')
ax1.set_xticks(x)
ax1.set_xticklabels(languages)
ax1.set_title("Grouped Bar Chart")
ax1.legend()

# Stacked bar chart
ax2.bar(languages, year_2023, label='2023', color='steelblue')
ax2.bar(languages, year_2024, bottom=year_2023, label='2024', color='coral')
ax2.set_title("Stacked Bar Chart")
ax2.legend()

fig.tight_layout()
fig.savefig("grouped_stacked_bars.png", dpi=150)
plt.close(fig)
```

#### Scatter Plot

```python
np.random.seed(42)
fig, ax = plt.subplots(figsize=(10, 8))

n = 200
x = np.random.randn(n)
y = 2 * x + np.random.randn(n) * 0.5
sizes = np.random.uniform(20, 200, n)
colors = np.random.randn(n)

scatter = ax.scatter(x, y, s=sizes, c=colors, cmap='viridis',
                     alpha=0.6, edgecolors='white', linewidth=0.5)

ax.set_title("Scatter Plot with Size and Color Encoding")
ax.set_xlabel("Feature X")
ax.set_ylabel("Feature Y")

# Add colorbar
cbar = fig.colorbar(scatter, ax=ax)
cbar.set_label("Color Value")

fig.savefig("scatter_plot.png", dpi=150, bbox_inches='tight')
plt.close(fig)
```

#### Histogram

```python
np.random.seed(42)
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

data = np.random.randn(1000)

# Basic histogram
axes[0].hist(data, bins=30, color='steelblue', edgecolor='white', alpha=0.7)
axes[0].set_title("Basic Histogram")

# Histogram with KDE overlay (using density=True to normalize)
axes[1].hist(data, bins=30, density=True, color='steelblue',
             edgecolor='white', alpha=0.7, label='Histogram')
x_kde = np.linspace(-4, 4, 100)
from scipy import stats
kde = stats.gaussian_kde(data)
axes[1].plot(x_kde, kde(x_kde), 'r-', linewidth=2, label='KDE')
axes[1].set_title("Histogram + KDE")
axes[1].legend()

# Multiple overlapping histograms
data2 = np.random.randn(1000) + 2
axes[2].hist(data, bins=30, alpha=0.5, label='Group A', color='steelblue')
axes[2].hist(data2, bins=30, alpha=0.5, label='Group B', color='coral')
axes[2].set_title("Overlapping Histograms")
axes[2].legend()

fig.tight_layout()
fig.savefig("histograms.png", dpi=150)
plt.close(fig)
```

#### Box Plot

```python
np.random.seed(42)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Basic box plot
data = [np.random.randn(100) * s + m
        for s, m in zip([1, 1.5, 0.8, 1.2], [0, 1, -0.5, 2])]

bp = ax1.boxplot(data, labels=['A', 'B', 'C', 'D'],
                 patch_artist=True, notch=True)
colors_box = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax1.set_title("Box Plot with Notches")
ax1.set_ylabel("Value")

# Violin plot -- shows distribution shape
parts = ax2.violinplot(data, positions=[1, 2, 3, 4], showmeans=True,
                       showmedians=True)
ax2.set_xticks([1, 2, 3, 4])
ax2.set_xticklabels(['A', 'B', 'C', 'D'])
ax2.set_title("Violin Plot")
ax2.set_ylabel("Value")

fig.tight_layout()
fig.savefig("box_violin_plots.png", dpi=150)
plt.close(fig)
```

#### Heatmap (with Matplotlib)

```python
np.random.seed(42)
fig, ax = plt.subplots(figsize=(10, 8))

data = np.random.randn(8, 10)
im = ax.imshow(data, cmap='RdBu_r', aspect='auto')

ax.set_xticks(range(10))
ax.set_yticks(range(8))
ax.set_xticklabels([f'Col {i}' for i in range(10)])
ax.set_yticklabels([f'Row {i}' for i in range(8)])
ax.set_title("Heatmap with imshow")

# Add text annotations
for i in range(8):
    for j in range(10):
        ax.text(j, i, f'{data[i, j]:.1f}', ha='center', va='center',
                color='white' if abs(data[i, j]) > 1 else 'black', fontsize=8)

fig.colorbar(im, ax=ax, shrink=0.8)
fig.tight_layout()
fig.savefig("heatmap_matplotlib.png", dpi=150)
plt.close(fig)
```

### Subplots and Layouts

```python
# Method 1: plt.subplots -- most common
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
# axes is a 2D numpy array of Axes objects
for i, ax in enumerate(axes.flat):
    ax.set_title(f"Plot {i+1}")
fig.suptitle("2x3 Grid of Subplots", fontsize=16)
fig.tight_layout()
fig.savefig("subplots_grid.png", dpi=150)
plt.close(fig)

# Method 2: GridSpec -- for unequal subplot sizes
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(12, 8))
gs = GridSpec(3, 3, figure=fig)

ax_main = fig.add_subplot(gs[0:2, 0:2])   # top-left 2x2
ax_right = fig.add_subplot(gs[0:2, 2])     # right column
ax_bottom = fig.add_subplot(gs[2, :])      # entire bottom row

ax_main.set_title("Main Plot (2x2)")
ax_right.set_title("Right Panel")
ax_bottom.set_title("Bottom Panel (full width)")

fig.tight_layout()
fig.savefig("gridspec_layout.png", dpi=150)
plt.close(fig)
```

### Customization and Styling

```python
# Global style
plt.style.use('seaborn-v0_8-whitegrid')  # or 'ggplot', 'dark_background', etc.
print(plt.style.available)  # see all available styles

# Custom rcParams
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'sans-serif',
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 100,
})

# Per-plot customization
fig, ax = plt.subplots(figsize=(10, 6))
x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), color='#1a73e8', linewidth=2.5)

# Spine customization (the plot border)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_linewidth(1.5)

# Tick customization
ax.tick_params(axis='both', which='major', labelsize=11, length=6, width=1.5)

# Annotations
ax.annotate('Peak', xy=(np.pi/2, 1), xytext=(np.pi/2 + 1, 1.2),
            fontsize=12, arrowprops=dict(arrowstyle='->', color='red'),
            color='red')

fig.savefig("customized_plot.png", dpi=150, bbox_inches='tight')
plt.close(fig)
```

### Saving Figures

```python
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])

# PNG -- raster, good for web
fig.savefig("plot.png", dpi=300, bbox_inches='tight')

# PDF -- vector, good for papers
fig.savefig("plot.pdf", bbox_inches='tight')

# SVG -- vector, good for web with scaling
fig.savefig("plot.svg", bbox_inches='tight')

# JPEG -- raster, smaller but lossy
fig.savefig("plot.jpg", dpi=200, quality=95, bbox_inches='tight')

plt.close(fig)
```

---

## 2. Seaborn -- Statistical Visualization

Seaborn is built on top of Matplotlib but provides a higher-level API for statistical
graphics. It works beautifully with pandas DataFrames.

**Swift analogy**: If Matplotlib is UIKit, Seaborn is SwiftUI for plotting -- more
opinionated, more concise, and prettier by default.

### Setup and Data

```python
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Seaborn comes with built-in datasets
tips = sns.load_dataset("tips")
iris = sns.load_dataset("iris")
penguins = sns.load_dataset("penguins")

print(tips.head())
# total_bill   tip     sex smoker  day    time  size
# 16.99        1.01  Female     No  Sun  Dinner     2
# 10.34        1.66    Male     No  Sun  Dinner     3
# ...
```

### Seaborn Themes and Styling

```python
# Set the aesthetic style
sns.set_theme(style="whitegrid")  # white, dark, whitegrid, darkgrid, ticks

# Set the color palette
sns.set_palette("husl")  # deep, muted, pastel, bright, dark, colorblind

# Custom palette
custom_palette = sns.color_palette("coolwarm", n_colors=6)
sns.set_palette(custom_palette)

# Context controls scale (paper, notebook, talk, poster)
sns.set_context("notebook", font_scale=1.2)
```

### Relational Plots (relplot)

```python
# Scatter with semantic mappings
fig = plt.figure(figsize=(10, 7))
g = sns.relplot(data=tips, x="total_bill", y="tip",
                hue="smoker", style="time", size="size",
                sizes=(20, 200), alpha=0.7, palette="Set2")
g.set_axis_labels("Total Bill ($)", "Tip ($)")
g.fig.suptitle("Tips by Bill Amount", y=1.02)
g.savefig("seaborn_relplot.png", dpi=150, bbox_inches='tight')
plt.close('all')

# Line plot with confidence intervals
fig, ax = plt.subplots(figsize=(10, 6))
fmri = sns.load_dataset("fmri")
sns.lineplot(data=fmri, x="timepoint", y="signal",
             hue="event", style="region", ax=ax)
ax.set_title("fMRI Signal Over Time")
fig.savefig("seaborn_lineplot.png", dpi=150, bbox_inches='tight')
plt.close(fig)
```

### Categorical Plots (catplot)

```python
# Box plot
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=tips, x="day", y="total_bill", hue="smoker",
            palette="Set2", ax=ax)
ax.set_title("Bill Distribution by Day")
fig.savefig("seaborn_boxplot.png", dpi=150, bbox_inches='tight')
plt.close(fig)

# Violin plot -- shows full distribution shape
fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=tips, x="day", y="total_bill", hue="sex",
               split=True, palette="Set1", ax=ax)
ax.set_title("Bill Distribution by Day and Sex")
fig.savefig("seaborn_violin.png", dpi=150, bbox_inches='tight')
plt.close(fig)

# Swarm plot -- every point visible, no overlap
fig, ax = plt.subplots(figsize=(10, 6))
sns.swarmplot(data=tips, x="day", y="total_bill",
              hue="time", dodge=True, palette="Set2", ax=ax, size=4)
ax.set_title("Individual Bills by Day")
fig.savefig("seaborn_swarm.png", dpi=150, bbox_inches='tight')
plt.close(fig)

# Bar plot -- with confidence intervals automatically
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=tips, x="day", y="total_bill", hue="sex",
            palette="muted", ci=95, ax=ax)
ax.set_title("Average Bill by Day")
fig.savefig("seaborn_barplot.png", dpi=150, bbox_inches='tight')
plt.close(fig)

# Count plot -- bar chart of counts
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=tips, x="day", hue="time",
              palette="pastel", ax=ax)
ax.set_title("Visit Counts by Day")
fig.savefig("seaborn_countplot.png", dpi=150, bbox_inches='tight')
plt.close(fig)
```

### Distribution Plots (displot)

```python
# Histogram with KDE
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(data=tips, x="total_bill", hue="time",
             kde=True, bins=25, palette="Set2", ax=ax)
ax.set_title("Bill Distribution by Time")
fig.savefig("seaborn_histplot.png", dpi=150, bbox_inches='tight')
plt.close(fig)

# KDE plot -- smooth density estimate
fig, ax = plt.subplots(figsize=(10, 6))
sns.kdeplot(data=tips, x="total_bill", hue="day",
            fill=True, alpha=0.4, ax=ax)
ax.set_title("Bill Density by Day")
fig.savefig("seaborn_kdeplot.png", dpi=150, bbox_inches='tight')
plt.close(fig)

# ECDF plot -- empirical cumulative distribution
fig, ax = plt.subplots(figsize=(10, 6))
sns.ecdfplot(data=tips, x="total_bill", hue="time", ax=ax)
ax.set_title("Cumulative Distribution of Bills")
fig.savefig("seaborn_ecdf.png", dpi=150, bbox_inches='tight')
plt.close(fig)
```

### Heatmap and Correlation

```python
# Correlation heatmap -- one of seaborn's most useful features
fig, ax = plt.subplots(figsize=(10, 8))
numeric_tips = tips.select_dtypes(include=[np.number])
corr = numeric_tips.corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, square=True, linewidths=1, ax=ax)
ax.set_title("Correlation Heatmap")
fig.savefig("seaborn_heatmap.png", dpi=150, bbox_inches='tight')
plt.close(fig)
```

### Pair Plot

```python
# Pairplot -- scatter matrix of all numeric columns
g = sns.pairplot(iris, hue="species", palette="Set2",
                 diag_kind="kde", plot_kws={'alpha': 0.6, 's': 30})
g.fig.suptitle("Iris Dataset Pairplot", y=1.02)
g.savefig("seaborn_pairplot.png", dpi=150, bbox_inches='tight')
plt.close('all')
```

### Joint Plot

```python
g = sns.jointplot(data=tips, x="total_bill", y="tip",
                  hue="smoker", kind="scatter", palette="Set1")
g.fig.suptitle("Bill vs Tip with Marginal Distributions", y=1.02)
g.savefig("seaborn_jointplot.png", dpi=150, bbox_inches='tight')
plt.close('all')
```

---

## 3. Plotly -- Interactive Visualization

Plotly creates interactive, web-based visualizations. You can zoom, pan, hover, and
export. It has two APIs: Plotly Express (concise) and Graph Objects (full control).

### Plotly Express -- The Quick Way

```python
import plotly.express as px
import pandas as pd

# Plotly Express works like Seaborn but produces interactive charts
df = px.data.gapminder()

# Interactive scatter
fig = px.scatter(
    df.query("year == 2007"),
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    hover_name="country",
    log_x=True,
    size_max=60,
    title="GDP vs Life Expectancy (2007)"
)
fig.write_html("plotly_scatter.html")  # interactive HTML file
fig.write_image("plotly_scatter.png")  # static image (requires kaleido)

# Interactive line chart
fig = px.line(
    df.query("country in ['United States', 'Japan', 'Germany']"),
    x="year",
    y="gdpPercap",
    color="country",
    title="GDP Per Capita Over Time",
    labels={"gdpPercap": "GDP Per Capita ($)", "year": "Year"}
)
fig.write_html("plotly_line.html")

# Interactive bar chart
fig = px.bar(
    df.query("year == 2007 & continent == 'Europe'")
      .nlargest(10, "gdpPercap"),
    x="country",
    y="gdpPercap",
    color="country",
    title="Top 10 European Countries by GDP (2007)"
)
fig.update_layout(showlegend=False, xaxis_tickangle=-45)
fig.write_html("plotly_bar.html")

# Interactive histogram
fig = px.histogram(
    df.query("year == 2007"),
    x="lifeExp",
    nbins=30,
    color="continent",
    title="Life Expectancy Distribution (2007)"
)
fig.write_html("plotly_histogram.html")

# Choropleth map
fig = px.choropleth(
    df.query("year == 2007"),
    locations="iso_alpha",
    color="lifeExp",
    hover_name="country",
    color_continuous_scale="Viridis",
    title="Life Expectancy by Country (2007)"
)
fig.write_html("plotly_choropleth.html")
```

### Graph Objects -- Full Control

```python
import plotly.graph_objects as go

# Build plots piece by piece
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[1, 4, 9, 16, 25],
    mode='lines+markers',
    name='Squares',
    line=dict(color='steelblue', width=3),
    marker=dict(size=10, symbol='circle')
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[1, 8, 27, 64, 125],
    mode='lines+markers',
    name='Cubes',
    line=dict(color='coral', width=3, dash='dash'),
    marker=dict(size=10, symbol='diamond')
))

fig.update_layout(
    title="Squares vs Cubes",
    xaxis_title="x",
    yaxis_title="y",
    template="plotly_white",
    font=dict(size=14),
    legend=dict(x=0.02, y=0.98)
)

fig.write_html("plotly_go_scatter.html")
```

### 3D Plots

```python
import plotly.graph_objects as go
import numpy as np

# 3D Surface
x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Viridis')])
fig.update_layout(
    title="3D Surface Plot",
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    )
)
fig.write_html("plotly_3d_surface.html")

# 3D Scatter
np.random.seed(42)
n = 300
fig = go.Figure(data=[go.Scatter3d(
    x=np.random.randn(n),
    y=np.random.randn(n),
    z=np.random.randn(n),
    mode='markers',
    marker=dict(size=4, color=np.random.randn(n),
                colorscale='Viridis', opacity=0.8)
)])
fig.update_layout(title="3D Scatter Plot")
fig.write_html("plotly_3d_scatter.html")
```

### Subplots in Plotly

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Scatter", "Bar", "Line", "Histogram")
)

fig.add_trace(
    go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode='markers'),
    row=1, col=1
)
fig.add_trace(
    go.Bar(x=['A', 'B', 'C'], y=[3, 1, 2]),
    row=1, col=2
)
fig.add_trace(
    go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13], mode='lines'),
    row=2, col=1
)
fig.add_trace(
    go.Histogram(x=np.random.randn(500)),
    row=2, col=2
)

fig.update_layout(height=600, title_text="Plotly Subplots", showlegend=False)
fig.write_html("plotly_subplots.html")
```

### Updating Layouts

```python
import plotly.express as px

fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length",
                 color="species")

# Update layout after creation
fig.update_layout(
    title=dict(text="Iris Measurements", font=dict(size=24)),
    xaxis=dict(title="Sepal Width (cm)", gridcolor='lightgray'),
    yaxis=dict(title="Sepal Length (cm)", gridcolor='lightgray'),
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Arial", size=14),
    legend=dict(title="Species", bordercolor="gray", borderwidth=1),
    margin=dict(l=60, r=30, t=60, b=60),
    width=800,
    height=500
)

# Update all traces at once
fig.update_traces(marker=dict(size=10, line=dict(width=1, color='white')))

fig.write_html("plotly_styled.html")
```

---

## 4. Choosing the Right Chart Type

| Data Relationship | Best Chart Types |
|---|---|
| Distribution of one variable | Histogram, KDE, Box plot, Violin |
| Comparison across categories | Bar chart (vertical or horizontal) |
| Relationship between two numeric variables | Scatter plot |
| Trend over time | Line chart |
| Part-of-whole | Pie chart (sparingly), stacked bar |
| Correlation matrix | Heatmap |
| Distribution by group | Grouped box/violin, faceted histograms |
| High-dimensional overview | Pair plot, parallel coordinates |
| Geographic data | Choropleth, scatter on map |

### Best Practices

1. **Start simple**. A clean scatter or bar chart beats a complex 3D visualization.
2. **Label everything**. Title, axes, units, legend -- the chart should be readable standalone.
3. **Choose colors purposefully**. Use colorblind-friendly palettes (`colorblind`, `viridis`).
4. **Avoid chart junk**. No unnecessary gridlines, borders, or 3D effects on 2D data.
5. **Match chart to audience**. Exploratory analysis can be rough; presentations need polish.
6. **Use consistent scales** when comparing across subplots or panels.
7. **Show the data** when possible -- box plots hide individual points.

### Library Decision Guide

| Need | Use |
|---|---|
| Quick exploration | Matplotlib or Seaborn |
| Statistical visualization | Seaborn |
| Publication-quality static figures | Matplotlib + Seaborn |
| Interactive dashboards | Plotly |
| Sharing with non-technical audience | Plotly (HTML export) |
| Jupyter notebook exploration | Any -- Plotly shines here |
| Scripted batch generation | Matplotlib |

---

## 5. Matplotlib + Seaborn Integration

Seaborn creates Matplotlib objects, so you can freely mix them:

```python
import seaborn as sns
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

# Create a Seaborn plot, then customize with Matplotlib
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=tips, x="total_bill", y="tip",
                hue="smoker", style="time", ax=ax)

# Now use Matplotlib to add custom elements
ax.axhline(y=tips['tip'].mean(), color='red', linestyle='--',
           alpha=0.5, label='Mean Tip')
ax.axvline(x=tips['total_bill'].mean(), color='blue', linestyle='--',
           alpha=0.5, label='Mean Bill')
ax.set_title("Tips Analysis with Reference Lines", fontsize=14)
ax.legend(loc='upper left')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

fig.savefig("seaborn_matplotlib_combo.png", dpi=150, bbox_inches='tight')
plt.close(fig)
```

---

## Summary

| Library | Strengths | When to Use |
|---|---|---|
| Matplotlib | Full control, any plot type, scriptable | Publication figures, custom layouts |
| Seaborn | Statistical plots, beautiful defaults, DataFrame-native | EDA, statistical analysis |
| Plotly | Interactive, web-ready, 3D support | Dashboards, presentations, exploration |

**Key takeaway for Swift developers**: Python's visualization ecosystem is far richer than
anything available natively on Apple platforms. Matplotlib is your UIKit (powerful, verbose),
Seaborn is your SwiftUI (concise, opinionated), and Plotly is your web export layer.
Master Matplotlib first, then use Seaborn and Plotly to move faster.

---

## Next Steps

- Practice creating each plot type from memory
- Experiment with different Seaborn themes and palettes
- Build a small interactive dashboard with Plotly
- Move on to Module 07: EDA Workflow to apply these visualization skills systematically
