"""
Module 08: Feature Engineering - Solutions
==========================================

Complete solutions for all 12 exercises.
Run this file to verify all solutions pass:
    python solutions.py
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    OneHotEncoder, LabelEncoder, OrdinalEncoder,
)
from sklearn.feature_selection import SelectKBest, f_classif


# ---------------------------------------------------------------------------
# Exercise 1: StandardScaler - Standardization
# ---------------------------------------------------------------------------
def standardize_features() -> tuple[np.ndarray, StandardScaler]:
    """
    Use StandardScaler to standardize numerical features.

    Data:
        values: [[10], [20], [30], [40], [50]]

    Fit the scaler and transform the data.
    Return tuple of (scaled_data, fitted_scaler).
    """
    X = np.array([[10], [20], [30], [40], [50]])

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(X)

    return scaled_data, scaler


# ---------------------------------------------------------------------------
# Exercise 2: MinMaxScaler - Normalization
# ---------------------------------------------------------------------------
def normalize_features() -> np.ndarray:
    """
    Use MinMaxScaler to normalize features to [0, 1].

    Data:
        values: [[5], [10], [15], [20], [25]]

    Return scaled numpy array.
    """
    X = np.array([[5], [10], [15], [20], [25]])

    scaler = MinMaxScaler()
    normalized = scaler.fit_transform(X)

    return normalized


# ---------------------------------------------------------------------------
# Exercise 3: RobustScaler - Handling Outliers
# ---------------------------------------------------------------------------
def robust_scale_features() -> np.ndarray:
    """
    Use RobustScaler to handle outliers in features.

    Data:
        values: [[1], [2], [3], [4], [100]]  # 100 is an outlier

    Return scaled numpy array.
    """
    X = np.array([[1], [2], [3], [4], [100]])

    scaler = RobustScaler()
    robust = scaler.fit_transform(X)

    return robust


# ---------------------------------------------------------------------------
# Exercise 4: LabelEncoder - Encoding Categorical Variables
# ---------------------------------------------------------------------------
def label_encode_categories() -> tuple[np.ndarray, LabelEncoder]:
    """
    Use LabelEncoder to encode categorical string values.

    Data:
        categories: ['red', 'blue', 'green', 'red', 'blue', 'green']

    Fit and transform the data.
    Return tuple of (encoded_values, fitted_encoder).
    """
    categories = ['red', 'blue', 'green', 'red', 'blue', 'green']

    encoder = LabelEncoder()
    encoded = encoder.fit_transform(categories)

    return encoded, encoder


# ---------------------------------------------------------------------------
# Exercise 5: OneHotEncoder - One-Hot Encoding
# ---------------------------------------------------------------------------
def one_hot_encode() -> tuple[np.ndarray, OneHotEncoder]:
    """
    Use OneHotEncoder to create binary features from categories.

    Data:
        categories: [['A'], ['B'], ['A'], ['C'], ['B']]  # Note: 2D array

    Fit and transform the data.
    Return tuple of (encoded_array, fitted_encoder).
    """
    categories = np.array([['A'], ['B'], ['A'], ['C'], ['B']])

    encoder = OneHotEncoder(sparse_output=False)
    encoded = encoder.fit_transform(categories)

    return encoded, encoder


# ---------------------------------------------------------------------------
# Exercise 6: OrdinalEncoder - Ordinal Encoding
# ---------------------------------------------------------------------------
def ordinal_encode_features() -> np.ndarray:
    """
    Use OrdinalEncoder for ordinal categorical features.

    Data (with categories having natural order):
        size: [['small'], ['large'], ['medium'], ['small'], ['large']]

    Use categories parameter to enforce order: ['small', 'medium', 'large']

    Return encoded array.
    """
    size = np.array([['small'], ['large'], ['medium'], ['small'], ['large']])

    encoder = OrdinalEncoder(
        categories=[['small', 'medium', 'large']]
    )
    ordinal = encoder.fit_transform(size)

    return ordinal


# ---------------------------------------------------------------------------
# Exercise 7: Feature Creation - Polynomial Features
# ---------------------------------------------------------------------------
def create_polynomial_features(X: np.ndarray) -> np.ndarray:
    """
    Create polynomial features manually (without PolynomialFeatures).

    Input: X shape (n_samples, 1) containing values [2, 3, 4]

    Create new features:
    - x^2: square of original feature
    - x^3: cube of original feature

    Return array with shape (3, 3) with [x, x^2, x^3].
    """
    x = X.flatten()

    result = np.column_stack([
        x,
        x ** 2,
        x ** 3,
    ])

    return result


# ---------------------------------------------------------------------------
# Exercise 8: Feature Creation - Interaction Terms
# ---------------------------------------------------------------------------
def create_interaction_features() -> tuple[np.ndarray, np.ndarray]:
    """
    Create interaction features from two features.

    Data:
        x1: [1, 2, 3, 4]
        x2: [2, 3, 4, 5]

    Create:
    1. interaction: x1 * x2 (element-wise product)
    2. combined: array with [x1, x2, interaction] columns

    Return tuple of (interaction, combined).
    """
    x1 = np.array([1, 2, 3, 4])
    x2 = np.array([2, 3, 4, 5])

    interaction = x1 * x2

    combined = np.column_stack([x1, x2, interaction])

    return interaction, combined


# ---------------------------------------------------------------------------
# Exercise 9: Feature Creation - Binning/Bucketing
# ---------------------------------------------------------------------------
def create_binned_features() -> pd.DataFrame:
    """
    Convert continuous values into categorical bins.

    Data:
        age: [5, 15, 25, 35, 45, 55, 65, 75]

    Create bins:
    - 'age_group': 'child' (0-18), 'adult' (18-50), 'senior' (50+)

    Return DataFrame with original age and age_group columns.
    """
    df = pd.DataFrame({
        'age': [5, 15, 25, 35, 45, 55, 65, 75],
    })

    def categorize_age(age):
        if age < 18:
            return 'child'
        elif age < 50:
            return 'adult'
        else:
            return 'senior'

    df['age_group'] = df['age'].apply(categorize_age)

    return df


# ---------------------------------------------------------------------------
# Exercise 10: Feature Creation - Date/Time Features
# ---------------------------------------------------------------------------
def create_datetime_features() -> pd.DataFrame:
    """
    Extract features from datetime data.

    Data (as strings):
        dates: ['2024-01-15', '2024-03-20', '2024-06-10', '2024-12-25']

    Create:
    - 'month': month number (1-12)
    - 'quarter': quarter number (1-4)
    - 'day_of_year': day number in year (1-365)
    - 'is_quarter_end': boolean if last month of quarter

    Return DataFrame with all features.
    """
    df = pd.DataFrame({
        'date': pd.to_datetime(['2024-01-15', '2024-03-20', '2024-06-10', '2024-12-25']),
    })

    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['day_of_year'] = df['date'].dt.dayofyear
    df['is_quarter_end'] = df['month'].isin([3, 6, 9, 12])

    return df


# ---------------------------------------------------------------------------
# Exercise 11: Feature Selection - SelectKBest with f_classif
# ---------------------------------------------------------------------------
def select_best_features_classification() -> np.ndarray:
    """
    Use SelectKBest to select the top k features for classification.

    Data:
        X: [[1, 10], [2, 20], [3, 30], [4, 40], [5, 50]]
        y: [0, 0, 1, 1, 1]  # Target for classification

    Select k=1 best feature using f_classif.
    Return the transformed array with only the best feature.
    """
    X = np.array([[1, 10], [2, 20], [3, 30], [4, 40], [5, 50]])
    y = np.array([0, 0, 1, 1, 1])

    selector = SelectKBest(score_func=f_classif, k=1)
    selected = selector.fit_transform(X, y)

    return selected


# ---------------------------------------------------------------------------
# Exercise 12: Feature Scaling - Fit on Train, Transform on Test
# ---------------------------------------------------------------------------
def scale_train_test_split() -> tuple[np.ndarray, np.ndarray, StandardScaler]:
    """
    Proper workflow: fit scaler on train set, apply to test set.

    Data:
        train: [[10], [20], [30]]
        test: [[25], [35]]

    Fit StandardScaler on train data, transform both train and test.

    Return tuple of (scaled_train, scaled_test, fitted_scaler).
    """
    X_train = np.array([[10], [20], [30]])
    X_test = np.array([[25], [35]])

    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(X_train)
    scaled_test = scaler.transform(X_test)

    return scaled_train, scaled_test, scaler


# ===========================================================================
# Tests
# ===========================================================================
if __name__ == "__main__":
    print("Running Feature Engineering solution tests...\n")

    # Test 1: StandardScaler
    scaled, scaler = standardize_features()
    assert scaled.shape == (5, 1)
    assert np.isclose(scaled.mean(), 0, atol=1e-10)
    assert np.isclose(scaled.std(), 1, atol=1e-10)
    print("  [PASS] Exercise 1: StandardScaler")

    # Test 2: MinMaxScaler
    normalized = normalize_features()
    assert normalized.shape == (5, 1)
    assert normalized.min() >= 0
    assert normalized.max() <= 1
    assert normalized[0, 0] == 0  # Minimum value
    assert normalized[-1, 0] == 1  # Maximum value
    print("  [PASS] Exercise 2: MinMaxScaler")

    # Test 3: RobustScaler
    robust = robust_scale_features()
    assert robust.shape == (5, 1)
    print("  [PASS] Exercise 3: RobustScaler")

    # Test 4: LabelEncoder
    encoded, encoder = label_encode_categories()
    assert len(encoded) == 6
    assert set(encoded) == {0, 1, 2}  # Three unique categories
    print("  [PASS] Exercise 4: LabelEncoder")

    # Test 5: OneHotEncoder
    onehot, encoder = one_hot_encode()
    assert onehot.shape[0] == 5  # 5 samples
    assert onehot.shape[1] == 3  # 3 categories
    print("  [PASS] Exercise 5: OneHotEncoder")

    # Test 6: OrdinalEncoder
    ordinal = ordinal_encode_features()
    assert ordinal.shape == (5, 1)
    print("  [PASS] Exercise 6: OrdinalEncoder")

    # Test 7: Polynomial features
    X = np.array([[2], [3], [4]])
    poly = create_polynomial_features(X)
    assert poly.shape == (3, 3)
    assert np.allclose(poly[:, 1], X.flatten()**2)
    assert np.allclose(poly[:, 2], X.flatten()**3)
    print("  [PASS] Exercise 7: Polynomial Features")

    # Test 8: Interaction features
    interaction, combined = create_interaction_features()
    assert len(interaction) == 4
    assert interaction[0] == 2  # 1*2
    assert interaction[1] == 6  # 2*3
    assert combined.shape == (4, 3)
    print("  [PASS] Exercise 8: Interaction Features")

    # Test 9: Binned features
    binned = create_binned_features()
    assert 'age' in binned.columns
    assert 'age_group' in binned.columns
    assert 'child' in binned['age_group'].values
    assert 'adult' in binned['age_group'].values
    assert 'senior' in binned['age_group'].values
    print("  [PASS] Exercise 9: Binned Features")

    # Test 10: DateTime features
    dt_features = create_datetime_features()
    assert 'month' in dt_features.columns
    assert 'quarter' in dt_features.columns
    assert 'day_of_year' in dt_features.columns
    assert 'is_quarter_end' in dt_features.columns
    assert dt_features.loc[0, 'month'] == 1
    assert dt_features.loc[3, 'month'] == 12
    print("  [PASS] Exercise 10: DateTime Features")

    # Test 11: Feature selection
    selected = select_best_features_classification()
    assert selected.shape == (5, 1)  # 1 feature selected
    print("  [PASS] Exercise 11: Feature Selection")

    # Test 12: Train/test scaling
    scaled_train, scaled_test, fitted_scaler = scale_train_test_split()
    assert scaled_train.shape == (3, 1)
    assert scaled_test.shape == (2, 1)
    assert np.isclose(scaled_train.mean(), 0, atol=1e-10)
    print("  [PASS] Exercise 12: Train/Test Scaling")

    print("\nAll 12 solutions passed!")
