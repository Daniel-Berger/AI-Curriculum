# Module 08: Feature Engineering

## Introduction for Swift Developers

In iOS development, you transform raw JSON into strongly-typed models. Feature
engineering is the data science equivalent -- transforming raw data into features
that machine learning models can actually use. The difference: there is no schema,
no compiler enforcing types, and the "right" transformation depends on the algorithm
you plan to use.

Feature engineering is widely considered the most impactful skill in applied ML. A
mediocre model with great features will almost always outperform a sophisticated
model with poor features.

This module covers the core techniques: encoding categorical variables, scaling
numeric features, creating new features, selecting the most useful ones, and
handling problematic data distributions.

---

## 1. Encoding Categorical Variables

Machine learning models work with numbers. Categorical data (strings, labels) must be
converted to numeric form. The encoding method matters significantly.

### One-Hot Encoding

Creates a binary column for each category. Safe for nominal data (no ordering).

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder

df = pd.DataFrame({
    'color': ['red', 'blue', 'green', 'red', 'blue'],
    'size': ['S', 'M', 'L', 'XL', 'M'],
    'price': [10, 20, 15, 12, 22],
})

# Method 1: pandas get_dummies (quick and easy)
dummies = pd.get_dummies(df, columns=['color'], prefix='color', dtype=int)
print(dummies)
#    size  price  color_blue  color_green  color_red
# 0    S     10           0            0          1
# 1    M     20           1            0          0
# ...

# Drop first to avoid multicollinearity (for linear models)
dummies = pd.get_dummies(df, columns=['color'], drop_first=True, dtype=int)

# Method 2: sklearn OneHotEncoder (recommended for ML pipelines)
encoder = OneHotEncoder(sparse_output=False, drop='first')
encoded = encoder.fit_transform(df[['color']])
feature_names = encoder.get_feature_names_out(['color'])
encoded_df = pd.DataFrame(encoded, columns=feature_names)
print(encoded_df)
```

**When to use**: Nominal categories with low cardinality (< 10-15 unique values).
**Watch out for**: High cardinality creates too many columns (curse of dimensionality).

### Label Encoding

Assigns an integer to each category. Simple but implies ordering.

```python
from sklearn.preprocessing import LabelEncoder

# Label encoding
le = LabelEncoder()
df['color_encoded'] = le.fit_transform(df['color'])
print(df[['color', 'color_encoded']])
# color  color_encoded
# red              2
# blue             0
# green            1

# Reverse transform
original = le.inverse_transform(df['color_encoded'])

# Map for custom ordering
custom_map = {'red': 0, 'blue': 1, 'green': 2}
df['color_manual'] = df['color'].map(custom_map)
```

**When to use**: Tree-based models (they split on thresholds, so ordering does not
matter). Also good for target variables.
**Watch out for**: Linear models will interpret the numbers as ordered, which is wrong
for nominal data.

### Ordinal Encoding

For categories with a natural order.

```python
from sklearn.preprocessing import OrdinalEncoder

# Ordinal encoding with explicit order
size_order = [['S', 'M', 'L', 'XL']]  # list of lists, one per feature
oe = OrdinalEncoder(categories=size_order)
df['size_encoded'] = oe.fit_transform(df[['size']])
print(df[['size', 'size_encoded']])
# size  size_encoded
#    S           0.0
#    M           1.0
#    L           2.0
#   XL           3.0

# Manual ordinal mapping (more common in practice)
education_order = {
    'high_school': 0,
    'some_college': 1,
    'bachelors': 2,
    'masters': 3,
    'phd': 4,
}
```

**When to use**: Categories with meaningful order (size, education level, rating).

### Target Encoding (Mean Encoding)

Replace each category with the mean of the target variable for that category.

```python
# Target encoding (manual implementation)
df = pd.DataFrame({
    'city': ['NYC', 'LA', 'NYC', 'Chicago', 'LA', 'Chicago', 'NYC', 'LA'],
    'price': [500, 300, 450, 200, 350, 180, 550, 280],
})

# Calculate mean price per city
city_means = df.groupby('city')['price'].mean()
df['city_encoded'] = df['city'].map(city_means)
print(df[['city', 'city_encoded']])
# city  city_encoded
# NYC        500.00
# LA         310.00
# Chicago    190.00

# With sklearn (newer versions)
from sklearn.preprocessing import TargetEncoder

te = TargetEncoder(smooth="auto")
df['city_target'] = te.fit_transform(df[['city']], df['price'])
```

**When to use**: High-cardinality categorical features (hundreds of unique values).
**Watch out for**: Data leakage. Always compute means on training data only, then
apply to validation/test.

### Encoding Summary Table

| Method | Ordered? | Cardinality | Best For |
|---|---|---|---|
| One-Hot | No | Low (< 15) | Linear models, neural nets |
| Label | No | Any | Tree-based models, target vars |
| Ordinal | Yes | Low-Med | Ordinal features |
| Target | No | High | Any model, high cardinality |

---

## 2. Scaling and Normalization

Different features have different scales. Many algorithms (linear regression, SVM,
k-NN, neural networks) are sensitive to feature scales. Tree-based models are not.

### StandardScaler (Z-score normalization)

Centers to mean=0, std=1. Most common choice.

```python
from sklearn.preprocessing import StandardScaler

data = pd.DataFrame({
    'salary': [50000, 60000, 80000, 120000, 45000],
    'age': [25, 30, 35, 55, 22],
    'experience': [2, 5, 10, 30, 1],
})

scaler = StandardScaler()
scaled = scaler.fit_transform(data)
scaled_df = pd.DataFrame(scaled, columns=data.columns)
print(scaled_df)
#      salary       age  experience
# 0 -0.592    -0.680    -0.646
# 1 -0.263    -0.170    -0.314
# ...

# Reverse transform
original = scaler.inverse_transform(scaled)

# Key properties
print(f"Means: {scaled_df.mean().round(4).tolist()}")   # ~[0, 0, 0]
print(f"Stds:  {scaled_df.std().round(4).tolist()}")    # ~[1, 1, 1]
```

**When to use**: Default choice. Good when you do not know the distribution.
**Properties**: Does not bound values to a range. Outliers affect the scaling.

### MinMaxScaler

Scales to a fixed range, typically [0, 1].

```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()  # default range [0, 1]
scaled = scaler.fit_transform(data)
scaled_df = pd.DataFrame(scaled, columns=data.columns)
print(scaled_df)
#    salary   age  experience
# 0  0.0667  0.091      0.034
# 1  0.2000  0.242      0.138
# ...

# Custom range
scaler_custom = MinMaxScaler(feature_range=(-1, 1))
scaled_custom = scaler_custom.fit_transform(data)
```

**When to use**: When you need bounded values. Neural networks, image data.
**Watch out for**: Very sensitive to outliers (one outlier compresses everything else).

### RobustScaler

Uses median and IQR instead of mean and std. Robust to outliers.

```python
from sklearn.preprocessing import RobustScaler

# RobustScaler: (x - median) / IQR
scaler = RobustScaler()
scaled = scaler.fit_transform(data)
scaled_df = pd.DataFrame(scaled, columns=data.columns)
print(scaled_df)

# Compare with StandardScaler on data with outliers
data_with_outlier = data.copy()
data_with_outlier.loc[5] = [1_000_000, 25, 2]  # salary outlier

# StandardScaler -- outlier dominates
std_scaled = StandardScaler().fit_transform(data_with_outlier)
# RobustScaler -- outlier has less effect
robust_scaled = RobustScaler().fit_transform(data_with_outlier)
```

**When to use**: When your data has significant outliers.

### Scaling Decision Guide

| Scaler | Use When | Outlier Resistant? |
|---|---|---|
| StandardScaler | Default choice, Gaussian-ish data | No |
| MinMaxScaler | Need bounded range, neural nets | No |
| RobustScaler | Outliers present | Yes |
| None | Tree-based models (RF, XGBoost) | N/A |

### Critical Rule: Fit on Train, Transform on Both

```python
from sklearn.model_selection import train_test_split

X_train, X_test = train_test_split(data, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # fit AND transform
X_test_scaled = scaler.transform(X_test)          # transform ONLY

# WRONG: fitting on test data causes data leakage
# X_test_scaled = scaler.fit_transform(X_test)  # DON'T DO THIS
```

**Swift analogy**: This is like training a `NormalizationTransform` on your training
dataset in Create ML. You never recalculate statistics on validation data.

---

## 3. Feature Creation

### Polynomial Features

Create interactions and polynomial terms.

```python
from sklearn.preprocessing import PolynomialFeatures

X = pd.DataFrame({'x1': [1, 2, 3], 'x2': [4, 5, 6]})

# Degree 2: includes x1^2, x2^2, x1*x2
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
feature_names = poly.get_feature_names_out(['x1', 'x2'])
print(pd.DataFrame(X_poly, columns=feature_names))
#    x1   x2   x1^2  x1 x2  x2^2
# 0  1.0  4.0   1.0    4.0  16.0
# 1  2.0  5.0   4.0   10.0  25.0
# 2  3.0  6.0   9.0   18.0  36.0

# Interaction terms only (no x^2)
poly_interact = PolynomialFeatures(degree=2, interaction_only=True,
                                    include_bias=False)
X_interact = poly_interact.fit_transform(X)
```

### Date/Time Features

Extract rich features from datetime columns.

```python
df = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=365, freq='D'),
    'value': np.random.randn(365).cumsum(),
})

# Extract date features
df['year'] = df['timestamp'].dt.year
df['month'] = df['timestamp'].dt.month
df['day'] = df['timestamp'].dt.day
df['day_of_week'] = df['timestamp'].dt.dayofweek    # 0=Monday
df['day_of_year'] = df['timestamp'].dt.dayofyear
df['week_of_year'] = df['timestamp'].dt.isocalendar().week.astype(int)
df['quarter'] = df['timestamp'].dt.quarter
df['is_weekend'] = df['timestamp'].dt.dayofweek >= 5
df['is_month_start'] = df['timestamp'].dt.is_month_start
df['is_month_end'] = df['timestamp'].dt.is_month_end

# Cyclical encoding for periodic features (better for models)
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)

# Time since reference
df['days_since_start'] = (df['timestamp'] - df['timestamp'].min()).dt.days
```

### Text Features

Extract numeric features from text columns.

```python
df = pd.DataFrame({
    'review': [
        "Great product, love it!",
        "Terrible quality. Waste of money.",
        "OK, nothing special but works fine.",
        "AMAZING!!! Best purchase ever!!!",
    ]
})

# Basic text features
df['text_length'] = df['review'].str.len()
df['word_count'] = df['review'].str.split().str.len()
df['avg_word_length'] = df['review'].str.split().apply(
    lambda words: np.mean([len(w) for w in words])
)
df['exclamation_count'] = df['review'].str.count('!')
df['question_count'] = df['review'].str.count(r'\?')
df['uppercase_ratio'] = df['review'].apply(
    lambda x: sum(1 for c in x if c.isupper()) / len(x)
)
df['has_negative'] = df['review'].str.lower().str.contains(
    r'terrible|bad|waste|poor|awful', regex=True
).astype(int)

print(df[['review', 'word_count', 'exclamation_count', 'uppercase_ratio']])
```

### Aggregation Features

Create features from grouped aggregations.

```python
transactions = pd.DataFrame({
    'customer_id': [1, 1, 1, 2, 2, 3, 3, 3, 3],
    'amount': [100, 150, 200, 50, 75, 300, 25, 175, 250],
    'date': pd.date_range('2024-01-01', periods=9, freq='W'),
})

# Customer-level features
customer_features = transactions.groupby('customer_id').agg(
    total_spent=('amount', 'sum'),
    avg_transaction=('amount', 'mean'),
    max_transaction=('amount', 'max'),
    min_transaction=('amount', 'min'),
    n_transactions=('amount', 'count'),
    std_transaction=('amount', 'std'),
).reset_index()

# Ratio features
customer_features['max_to_avg_ratio'] = (
    customer_features['max_transaction'] / customer_features['avg_transaction']
)
customer_features['spending_range'] = (
    customer_features['max_transaction'] - customer_features['min_transaction']
)

print(customer_features)
```

---

## 4. Feature Selection

Not all features help. Some are redundant, noisy, or irrelevant. Feature selection
identifies the most useful subset.

### Correlation-Based Removal

Remove features that are highly correlated with each other.

```python
def remove_correlated_features(df: pd.DataFrame,
                                threshold: float = 0.90) -> list[str]:
    """Find features to drop based on high inter-correlation."""
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr().abs()

    # Upper triangle of correlation matrix
    upper = corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )

    # Find features with correlation > threshold
    to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
    return to_drop

# Usage
cols_to_drop = remove_correlated_features(df, threshold=0.90)
df_reduced = df.drop(columns=cols_to_drop)
```

### Variance Threshold

Remove features with very low variance (they carry little information).

```python
from sklearn.feature_selection import VarianceThreshold

# Remove features with zero variance
selector = VarianceThreshold(threshold=0.0)
X_selected = selector.fit_transform(X)
selected_features = X.columns[selector.get_support()].tolist()

# Remove features with variance below a threshold
# For binary features, var = p(1-p), so threshold=0.1 removes
# features where 95%+ of values are the same
selector = VarianceThreshold(threshold=0.1)
X_selected = selector.fit_transform(X)
```

### Mutual Information

Measures dependency between feature and target (works for non-linear relationships).

```python
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif

# For regression targets
mi_scores = mutual_info_regression(X, y, random_state=42)
mi_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
print(mi_series)

# For classification targets
mi_scores = mutual_info_classif(X, y, random_state=42)
mi_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
```

### SelectKBest

Select the K features with the highest scores according to a scoring function.

```python
from sklearn.feature_selection import SelectKBest, f_regression, f_classif

# Select top 5 features for regression
selector = SelectKBest(score_func=f_regression, k=5)
X_selected = selector.fit_transform(X, y)
selected_mask = selector.get_support()
selected_features = X.columns[selected_mask].tolist()

# See scores
scores = pd.DataFrame({
    'feature': X.columns,
    'score': selector.scores_,
    'p_value': selector.pvalues_,
    'selected': selector.get_support()
}).sort_values('score', ascending=False)
print(scores)
```

### Recursive Feature Elimination (RFE)

Iteratively removes the least important feature.

```python
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression

model = LinearRegression()
rfe = RFE(estimator=model, n_features_to_select=5, step=1)
rfe.fit(X, y)

# Results
selected = X.columns[rfe.support_].tolist()
ranking = pd.DataFrame({
    'feature': X.columns,
    'ranking': rfe.ranking_,
    'selected': rfe.support_,
}).sort_values('ranking')
print(ranking)
```

---

## 5. Handling Outliers

### Detection Methods

```python
def detect_outliers(series: pd.Series, method: str = 'iqr') -> pd.Series:
    """Detect outliers using IQR or z-score method."""
    if method == 'iqr':
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return (series < lower) | (series > upper)

    elif method == 'zscore':
        from scipy import stats
        z = np.abs(stats.zscore(series.dropna()))
        mask = pd.Series(False, index=series.index)
        mask.loc[series.dropna().index] = z > 3
        return mask

    else:
        raise ValueError(f"Unknown method: {method}")

# Usage
is_outlier = detect_outliers(df['salary'], method='iqr')
print(f"Outliers: {is_outlier.sum()} ({is_outlier.mean()*100:.1f}%)")
```

### Treatment Methods

```python
def treat_outliers(series: pd.Series, method: str = 'clip') -> pd.Series:
    """Treat outliers using various methods."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    if method == 'clip':
        # Cap values at boundaries (winsorizing)
        return series.clip(lower=lower, upper=upper)

    elif method == 'remove':
        # Set outliers to NaN (to be handled later)
        result = series.copy()
        result[(series < lower) | (series > upper)] = np.nan
        return result

    elif method == 'log':
        # Log transform (only for positive values)
        return np.log1p(series.clip(lower=0))

    else:
        raise ValueError(f"Unknown method: {method}")

# Usage
df['salary_clipped'] = treat_outliers(df['salary'], method='clip')
df['salary_log'] = treat_outliers(df['salary'], method='log')
```

---

## 6. Handling Skewed Data

### Log Transform

The most common technique for right-skewed data.

```python
# Check skewness
print(f"Original skewness: {df['salary'].skew():.3f}")

# Log transform (for positive values)
df['salary_log'] = np.log1p(df['salary'])  # log(1+x), handles zeros
print(f"Log skewness: {df['salary_log'].skew():.3f}")

# Reverse transform
original = np.expm1(df['salary_log'])  # exp(x) - 1
```

### Box-Cox Transform

Automatically finds the best power transform.

```python
from scipy import stats

# Box-Cox requires strictly positive values
salary_positive = df['salary'].dropna()
salary_positive = salary_positive[salary_positive > 0]
transformed, lambda_param = stats.boxcox(salary_positive)
print(f"Optimal lambda: {lambda_param:.3f}")

# sklearn version (handles zero/negative via Yeo-Johnson)
from sklearn.preprocessing import PowerTransformer

pt = PowerTransformer(method='yeo-johnson')  # handles negative values
df['salary_transformed'] = pt.fit_transform(df[['salary']])
print(f"Transformed skewness: {df['salary_transformed'].skew():.3f}")
```

### Binning

Convert continuous variables into discrete bins.

```python
# Equal-width binning
df['age_bins'] = pd.cut(df['age'], bins=5, labels=['young', 'early-career',
                                                     'mid-career', 'senior',
                                                     'veteran'])

# Equal-frequency binning (quantile)
df['salary_quartile'] = pd.qcut(df['salary'], q=4,
                                  labels=['Q1', 'Q2', 'Q3', 'Q4'])

# Custom bins
age_bins = [0, 25, 35, 45, 55, 100]
age_labels = ['<25', '25-34', '35-44', '45-54', '55+']
df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)
```

---

## 7. sklearn Preprocessing Pipeline

Combine multiple preprocessing steps into a clean pipeline.

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Define column groups
numeric_features = ['age', 'salary', 'experience']
categorical_features = ['department', 'education']

# Create transformers for each type
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('encoder', OneHotEncoder(drop='first', sparse_output=False,
                               handle_unknown='ignore')),
])

# Combine into a ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features),
    ],
    remainder='drop'  # or 'passthrough' to keep other columns
)

# Use in a full pipeline with a model
from sklearn.linear_model import LinearRegression

full_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', LinearRegression()),
])

# Fit and predict
# full_pipeline.fit(X_train, y_train)
# predictions = full_pipeline.predict(X_test)

# Get feature names after transformation
preprocessor.fit(X_train)
feature_names = preprocessor.get_feature_names_out()
print(feature_names)
```

**Swift analogy**: This is like a Combine pipeline -- you chain transformations, and
data flows through each step. The fit/transform pattern is like a Combine Publisher
that needs a Subscriber to activate.

---

## 8. Feature Engineering Best Practices

1. **Start simple**. Basic features often outperform clever ones.
2. **Use domain knowledge**. The best features come from understanding the problem.
3. **Avoid data leakage**. Never use information from the future or the test set.
4. **Scale after splitting**. Always fit scalers on training data only.
5. **Check feature importance** after training. Drop useless features.
6. **Document everything**. Future you (or your team) needs to know why each feature exists.
7. **Think about interactions**. `area = length * width` is better than two separate features.
8. **Handle missing values intentionally**. "Missing" can itself be a feature.

---

## Summary

| Technique | When to Use | Key Class/Function |
|---|---|---|
| One-Hot Encoding | Nominal categories, low cardinality | `OneHotEncoder`, `get_dummies` |
| Label Encoding | Tree models, target variable | `LabelEncoder` |
| Ordinal Encoding | Ordered categories | `OrdinalEncoder` |
| Target Encoding | High cardinality categories | `TargetEncoder` |
| StandardScaler | Default scaling | `StandardScaler` |
| MinMaxScaler | Need bounded range | `MinMaxScaler` |
| RobustScaler | Data with outliers | `RobustScaler` |
| Polynomial Features | Interaction terms | `PolynomialFeatures` |
| Log Transform | Right-skewed data | `np.log1p` |
| SelectKBest | Quick feature selection | `SelectKBest` |
| RFE | Iterative feature selection | `RFE` |

**Key takeaway for Swift developers**: Feature engineering is where the art of data
science lives. Unlike Swift's type system which enforces correctness, feature
engineering requires judgment -- there is no "correct" encoding, only better or
worse choices for a specific model and dataset.

---

## Next Steps

- Practice encoding and scaling on a real dataset
- Build a full sklearn Pipeline for end-to-end preprocessing
- Try automated feature engineering libraries (featuretools, autofeat)
- Move on to Module 09: Math for ML to understand why these transforms work
