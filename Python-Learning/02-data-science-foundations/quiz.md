# Phase 2 Quiz: Data Science Foundations

Test your understanding of NumPy, Pandas, Polars, visualization, EDA, feature engineering, and math for ML.

---

## NumPy Fundamentals (Q1-Q4)

### Q1 [Easy] — Multiple Choice
What is the primary advantage of NumPy arrays over Python lists for numerical computation?

A) They can hold mixed types
B) Vectorized operations avoid Python loops, running in compiled C
C) They are always smaller in memory
D) They support string operations

### Q2 [Medium] — Short Answer
Explain NumPy broadcasting rules. Given arrays of shapes `(3, 1)` and `(1, 4)`, what is the resulting shape after an element-wise operation?

### Q3 [Medium] — Code Writing
Write a NumPy expression to normalize a 2D array `X` (shape `(n, m)`) so each column has mean 0 and standard deviation 1 — without using a loop.

### Q4 [Hard] — Short Answer
What is the difference between `np.dot(A, B)`, `A @ B`, and `np.matmul(A, B)` for 2D arrays? When would they differ?

---

## Pandas (Q5-Q10)

### Q5 [Easy] — Multiple Choice
Which method returns rows by integer position?

A) `.loc[]`
B) `.iloc[]`
C) `.at[]`
D) `.ix[]`

### Q6 [Easy] — Short Answer
What is the difference between `df.loc[0]` and `df.iloc[0]`?

### Q7 [Medium] — Code Writing
Given a DataFrame `df` with columns `['name', 'department', 'salary']`, write a single chained expression to:
1. Filter for salaries > 50000
2. Group by department
3. Calculate mean salary per department
4. Sort descending by mean salary

### Q8 [Medium] — Code Writing
Write code to handle missing values in a DataFrame: fill numeric columns with the median and categorical columns with the mode.

### Q9 [Hard] — Short Answer
Explain the difference between `df.apply()`, `df.map()`, and vectorized operations. When should you use each? What are the performance implications?

### Q10 [Hard] — Code Writing
Write a Pandas method chain using `.pipe()` and `.assign()` that:
1. Removes duplicates
2. Adds a `salary_rank` column (rank within each department)
3. Adds a `is_above_avg` boolean column (salary > department mean)

---

## Polars (Q11-Q13)

### Q11 [Easy] — Multiple Choice
What is the main architectural difference between Polars and Pandas?

A) Polars is written in Python, Pandas in C
B) Polars uses lazy evaluation and is written in Rust
C) Polars only works with CSV files
D) Polars doesn't support groupby operations

### Q12 [Medium] — Short Answer
Explain lazy evaluation in Polars. What are `scan_csv()`, `.collect()`, and `.explain()`?

### Q13 [Medium] — Code Writing
Translate this Pandas code to Polars:
```python
df.groupby("category")["value"].mean().sort_values(ascending=False)
```

---

## Data Visualization (Q14-Q16)

### Q14 [Easy] — Multiple Choice
Which Matplotlib function creates a figure with multiple subplots?

A) `plt.subplot()`
B) `plt.subplots()`
C) `plt.figure()`
D) `plt.axes()`

### Q15 [Medium] — Short Answer
When would you choose Seaborn over Matplotlib? When would you choose Plotly over both?

### Q16 [Medium] — Short Answer
What type of chart would you use to visualize: (a) distribution of a numeric variable, (b) relationship between two numeric variables, (c) comparison across categories, (d) correlation between all numeric variables?

---

## EDA Workflow (Q17-Q19)

### Q17 [Easy] — Short Answer
List the 5 main steps in a systematic EDA workflow.

### Q18 [Medium] — Short Answer
What is the difference between univariate, bivariate, and multivariate analysis? Give an example visualization for each.

### Q19 [Hard] — Short Answer
You discover that 30% of values in a critical feature are missing. Describe three different strategies to handle this and the tradeoffs of each.

---

## Feature Engineering (Q20-Q23)

### Q20 [Easy] — Multiple Choice
Which encoding method is best for a categorical variable with no ordinal relationship and 5 unique values?

A) Label encoding
B) One-hot encoding
C) Target encoding
D) Binary encoding

### Q21 [Medium] — Short Answer
What is the difference between StandardScaler, MinMaxScaler, and RobustScaler? When would you use each?

### Q22 [Medium] — Code Writing
Write a sklearn pipeline that applies StandardScaler to numeric columns and OneHotEncoder to categorical columns using ColumnTransformer.

### Q23 [Hard] — Short Answer
What is target encoding and what is the risk of using it naively? How do you mitigate this risk?

---

## Math for ML (Q24-Q30)

### Q24 [Easy] — Short Answer
What is the dot product of vectors `[1, 2, 3]` and `[4, 5, 6]`? What does the dot product geometrically represent?

### Q25 [Easy] — Multiple Choice
What does the determinant of a matrix tell you?

A) The number of rows
B) Whether the matrix is invertible and the scaling factor of the linear transformation
C) The sum of all elements
D) The rank of the matrix

### Q26 [Medium] — Short Answer
Explain the chain rule in calculus and why it's essential for neural network training (backpropagation).

### Q27 [Medium] — Short Answer
What is Bayes' theorem? Give the formula and a practical example of how it's used in machine learning.

### Q28 [Medium] — Code Writing
Using NumPy, write code to compute the eigenvalues and eigenvectors of a 2x2 matrix. Verify that `A @ v = λ * v` for each eigenvalue-eigenvector pair.

### Q29 [Hard] — Short Answer
Explain the difference between a p-value and a confidence interval. A colleague says "the p-value is the probability that the null hypothesis is true." Is this correct? Why or why not?

### Q30 [Hard] — Short Answer
What is SVD (Singular Value Decomposition) and how is it used in machine learning? Name two specific applications.

---

# Answer Key

### Q1: **B** — NumPy arrays use vectorized operations implemented in C, avoiding slow Python loops.

### Q2: Broadcasting aligns dimensions from the right. `(3, 1)` and `(1, 4)` → each dimension is either 1 or matching. Result shape: **(3, 4)**. The `(3, 1)` array is "stretched" across 4 columns, and `(1, 4)` is stretched across 3 rows.

### Q3:
```python
X_normalized = (X - X.mean(axis=0)) / X.std(axis=0)
```

### Q4: For 2D arrays, all three are equivalent (matrix multiplication). They differ for higher-dimensional arrays: `np.dot` does a sum-product over the last axis of A and second-to-last of B, while `@`/`np.matmul` treats them as stacks of matrices and broadcasts. `np.dot` with a scalar multiplies element-wise; `@` doesn't allow scalars.

### Q5: **B** — `.iloc[]` uses integer position indexing.

### Q6: `.loc[0]` selects the row with **index label** 0 (which may not exist if the index was reset). `.iloc[0]` selects the **first row** by position regardless of the index labels.

### Q7:
```python
(df[df["salary"] > 50000]
 .groupby("department")["salary"]
 .mean()
 .sort_values(ascending=False))
```

### Q8:
```python
numeric_cols = df.select_dtypes(include="number").columns
cat_cols = df.select_dtypes(include="object").columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
df[cat_cols] = df[cat_cols].fillna(df[cat_cols].mode().iloc[0])
```

### Q9: **Vectorized operations** (e.g., `df["a"] + df["b"]`) are fastest — they run in C. **`.map()`** applies a function element-wise to a Series. **`.apply()`** applies a function row-wise or column-wise to a DataFrame. Performance: vectorized >> map > apply. Use vectorized when possible, `map` for element transformations, `apply` only when you need multiple columns per row.

### Q10:
```python
(df
 .drop_duplicates()
 .assign(
     salary_rank=lambda d: d.groupby("department")["salary"].rank(ascending=False),
     is_above_avg=lambda d: d["salary"] > d.groupby("department")["salary"].transform("mean"),
 ))
```

### Q11: **B** — Polars uses lazy evaluation and is written in Rust, enabling better performance and parallelism.

### Q12: Lazy evaluation means Polars builds a query plan without executing it. `scan_csv()` lazily reads a CSV (no data loaded yet). `.collect()` executes the query plan and returns a DataFrame. `.explain()` shows the optimized query plan. This allows Polars to optimize the entire pipeline (predicate pushdown, projection pushdown) before running.

### Q13:
```python
df.group_by("category").agg(pl.col("value").mean()).sort("value", descending=True)
```

### Q14: **B** — `plt.subplots()` returns a figure and axes array.

### Q15: **Seaborn** for statistical visualizations with less code (distribution plots, regression plots, heatmaps) — it handles grouping/coloring automatically. **Plotly** for interactive plots (zoom, hover, tooltips) or dashboards, especially for presentations or web apps.

### Q16: (a) Histogram or KDE plot, (b) Scatter plot, (c) Bar chart or box plot, (d) Correlation heatmap.

### Q17: 1. Understand structure (shape, types, head/tail), 2. Check data quality (missing, duplicates, outliers), 3. Univariate analysis (distributions), 4. Bivariate/multivariate analysis (correlations, relationships), 5. Document findings and recommendations.

### Q18: **Univariate** — one variable (histogram, box plot). **Bivariate** — two variables (scatter plot, grouped bar chart). **Multivariate** — three+ variables (pair plot, heatmap, 3D scatter, colored scatter by category).

### Q19: 1. **Drop rows** — simple but loses data, biases sample if missing isn't random. 2. **Imputation** (mean/median/mode) — preserves sample size but may reduce variance and distort relationships. 3. **Model-based imputation** (KNN, iterative) — more accurate but computationally expensive and can introduce data leakage if not done within cross-validation. Choice depends on missingness mechanism (MCAR/MAR/MNAR) and feature importance.

### Q20: **B** — One-hot encoding. Label encoding implies ordinal relationship, which is incorrect here. 5 unique values is manageable for one-hot (low cardinality).

### Q21: **StandardScaler**: mean=0, std=1. Best for normally distributed features. **MinMaxScaler**: scales to [0,1]. Best when you need bounded values (e.g., neural networks). **RobustScaler**: uses median and IQR. Best when data has outliers (not affected by extreme values).

### Q22:
```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ]
)
```

### Q23: Target encoding replaces each category with the mean of the target variable for that category. **Risk**: data leakage — the encoding uses information from the target, leading to overfitting. **Mitigation**: use leave-one-out encoding, add smoothing/regularization, or compute encodings only within cross-validation folds.

### Q24: `1*4 + 2*5 + 3*6 = 4 + 10 + 18 = **32**`. Geometrically, the dot product measures how much two vectors point in the same direction: `a·b = |a||b|cos(θ)`.

### Q25: **B** — The determinant indicates if a matrix is invertible (det ≠ 0) and represents the scaling factor of the linear transformation. If det = 0, the transformation collapses a dimension.

### Q26: The chain rule states: `d/dx f(g(x)) = f'(g(x)) * g'(x)`. In backpropagation, the loss is a composition of many functions (layers). The chain rule lets us compute the gradient of the loss with respect to each weight by multiplying local gradients backwards through the network.

### Q27: `P(A|B) = P(B|A) * P(A) / P(B)`. Example: Naive Bayes classifier — given observed features (B), compute the probability of each class (A). The prior `P(A)` is updated with the likelihood `P(B|A)` to get the posterior `P(A|B)`.

### Q28:
```python
A = np.array([[4, 2], [1, 3]])
eigenvalues, eigenvectors = np.linalg.eig(A)
for i in range(len(eigenvalues)):
    v = eigenvectors[:, i]
    lam = eigenvalues[i]
    np.testing.assert_array_almost_equal(A @ v, lam * v)
```

### Q29: No, this is a common misconception. The p-value is the probability of observing data as extreme as (or more extreme than) what was observed, **assuming the null hypothesis is true**. It is NOT the probability that the null hypothesis is true. A confidence interval provides a range of plausible values for the parameter — a 95% CI means that 95% of such intervals (from repeated sampling) would contain the true parameter.

### Q30: SVD decomposes a matrix A into `U * Σ * Vᵀ` where U and V are orthogonal and Σ is diagonal (singular values). Applications: (1) **PCA** — dimensionality reduction by keeping top-k singular values; (2) **Recommender systems** — matrix factorization for collaborative filtering; also used in LSA (topic modeling) and image compression.
