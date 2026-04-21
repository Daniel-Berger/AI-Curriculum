"""
Module 05: Unsupervised Learning - Exercises
=============================================
Target audience: Swift developers learning Python.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- If no AssertionError is raised, your solution is correct.

Difficulty levels:
  Easy   - Direct application of sklearn API
  Medium - Requires understanding algorithm behavior
  Hard   - Combines multiple concepts or requires deeper reasoning
"""

import numpy as np
from sklearn.datasets import make_blobs, make_moons, load_iris
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


# =============================================================================
# CLUSTERING
# =============================================================================

# Exercise 1: Basic K-Means
# Difficulty: Easy
# Fit K-Means with 3 clusters on the given data and return the cluster labels.
def kmeans_basic(X: np.ndarray) -> np.ndarray:
    """Fit K-Means with 3 clusters and return labels.

    Args:
        X: Feature matrix of shape (n_samples, n_features).

    Returns:
        Array of cluster labels of shape (n_samples,).

    >>> X, _ = make_blobs(n_samples=100, centers=3, random_state=42)
    >>> labels = kmeans_basic(X)
    >>> len(set(labels)) == 3
    True
    """
    pass


# Exercise 2: Elbow Method
# Difficulty: Medium
# Compute inertia values for K=1 through K=max_k and return them as a list.
def compute_elbow_values(X: np.ndarray, max_k: int = 10) -> list[float]:
    """Compute K-Means inertia for K=1 to max_k (inclusive).

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        max_k: Maximum number of clusters to test.

    Returns:
        List of inertia values, one per K.

    >>> X, _ = make_blobs(n_samples=100, centers=3, random_state=42)
    >>> inertias = compute_elbow_values(X, max_k=5)
    >>> len(inertias) == 5
    True
    >>> all(inertias[i] >= inertias[i+1] for i in range(len(inertias)-1))
    True
    """
    pass


# Exercise 3: Silhouette Analysis
# Difficulty: Medium
# Find the best K (from 2 to max_k) using silhouette score.
def best_k_silhouette(X: np.ndarray, max_k: int = 8) -> int:
    """Find the K with the highest silhouette score.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        max_k: Maximum K to evaluate (inclusive). Minimum K is 2.

    Returns:
        The integer K that produces the highest silhouette score.

    >>> X, _ = make_blobs(n_samples=200, centers=4, random_state=42)
    >>> best_k_silhouette(X, max_k=8)
    4
    """
    pass


# Exercise 4: DBSCAN Clustering
# Difficulty: Easy
# Apply DBSCAN to moon-shaped data and return labels. Noise points should
# be labeled as -1.
def dbscan_moons(X: np.ndarray, eps: float = 0.2, min_samples: int = 5) -> np.ndarray:
    """Apply DBSCAN clustering and return labels (noise = -1).

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        eps: Maximum distance between two samples to be neighbors.
        min_samples: Minimum number of samples in a neighborhood.

    Returns:
        Array of cluster labels of shape (n_samples,).

    >>> X, _ = make_moons(n_samples=200, noise=0.05, random_state=42)
    >>> labels = dbscan_moons(X)
    >>> n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    >>> n_clusters == 2
    True
    """
    pass


# Exercise 5: Count DBSCAN Noise Points
# Difficulty: Easy
# Given DBSCAN labels, count the number of noise points (label == -1).
def count_noise_points(labels: np.ndarray) -> int:
    """Count noise points in DBSCAN output.

    Args:
        labels: DBSCAN cluster labels array.

    Returns:
        Number of noise points (labeled -1).

    >>> labels = np.array([0, 0, 1, -1, 1, -1, 0])
    >>> count_noise_points(labels)
    2
    """
    pass


# Exercise 6: Agglomerative Clustering
# Difficulty: Easy
# Perform agglomerative clustering with the given number of clusters and linkage.
def agglomerative_cluster(
    X: np.ndarray, n_clusters: int = 3, linkage: str = "ward"
) -> np.ndarray:
    """Perform agglomerative clustering and return labels.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        n_clusters: Number of clusters to produce.
        linkage: Linkage criterion ('ward', 'complete', 'average', 'single').

    Returns:
        Array of cluster labels of shape (n_samples,).

    >>> X, _ = make_blobs(n_samples=100, centers=3, random_state=42)
    >>> labels = agglomerative_cluster(X, n_clusters=3)
    >>> len(set(labels)) == 3
    True
    """
    pass


# Exercise 7: Gaussian Mixture Model
# Difficulty: Medium
# Fit a GMM and return both hard labels AND soft probability assignments.
def gmm_cluster(
    X: np.ndarray, n_components: int = 3
) -> tuple[np.ndarray, np.ndarray]:
    """Fit a Gaussian Mixture Model and return labels and probabilities.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        n_components: Number of Gaussian components.

    Returns:
        Tuple of (labels, probabilities) where:
            - labels has shape (n_samples,)
            - probabilities has shape (n_samples, n_components)

    >>> X, _ = make_blobs(n_samples=100, centers=3, random_state=42)
    >>> labels, probs = gmm_cluster(X, n_components=3)
    >>> probs.shape == (100, 3)
    True
    >>> np.allclose(probs.sum(axis=1), 1.0)
    True
    """
    pass


# Exercise 8: GMM Model Selection with BIC
# Difficulty: Hard
# Find the best number of components using BIC (lower is better).
def best_gmm_components(X: np.ndarray, max_components: int = 8) -> int:
    """Find optimal number of GMM components using BIC.

    Test n_components from 1 to max_components (inclusive).
    Return the number that gives the lowest BIC.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        max_components: Maximum number of components to test.

    Returns:
        Optimal number of components (int).

    >>> X, _ = make_blobs(n_samples=300, centers=4, random_state=42)
    >>> best_gmm_components(X, max_components=8)
    4
    """
    pass


# =============================================================================
# DIMENSIONALITY REDUCTION
# =============================================================================

# Exercise 9: PCA Basics
# Difficulty: Easy
# Apply PCA to reduce data to n_components dimensions. Scale the data first.
def pca_reduce(X: np.ndarray, n_components: int = 2) -> np.ndarray:
    """Scale data with StandardScaler, then apply PCA.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        n_components: Number of principal components to keep.

    Returns:
        Transformed data of shape (n_samples, n_components).

    >>> iris = load_iris()
    >>> X_reduced = pca_reduce(iris.data, n_components=2)
    >>> X_reduced.shape == (150, 2)
    True
    """
    pass


# Exercise 10: PCA Explained Variance
# Difficulty: Medium
# Compute the cumulative explained variance ratio for all components.
# Return the minimum number of components needed to explain at least
# the given threshold of variance.
def pca_min_components(X: np.ndarray, threshold: float = 0.95) -> int:
    """Find minimum components to explain threshold fraction of variance.

    Args:
        X: Feature matrix (will be scaled internally).
        threshold: Minimum cumulative explained variance ratio (e.g., 0.95).

    Returns:
        Minimum number of components needed.

    >>> iris = load_iris()
    >>> pca_min_components(iris.data, threshold=0.95)
    2
    """
    pass


# Exercise 11: t-SNE Visualization Data
# Difficulty: Medium
# Apply t-SNE to reduce data to 2D. Return the transformed coordinates.
# Note: Always scale the data first. Use random_state=42 for reproducibility.
def tsne_reduce(X: np.ndarray, perplexity: float = 30.0) -> np.ndarray:
    """Scale data and apply t-SNE to reduce to 2 dimensions.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        perplexity: t-SNE perplexity parameter.

    Returns:
        Transformed data of shape (n_samples, 2).

    >>> iris = load_iris()
    >>> X_tsne = tsne_reduce(iris.data)
    >>> X_tsne.shape == (150, 2)
    True
    """
    pass


# Exercise 12: PCA then t-SNE Pipeline
# Difficulty: Hard
# For large datasets, first reduce to 50 dimensions with PCA, then apply t-SNE.
# If the data already has <= 50 features, skip the PCA step.
def pca_then_tsne(X: np.ndarray, pca_components: int = 50) -> np.ndarray:
    """Scale data, optionally reduce with PCA, then apply t-SNE to 2D.

    If n_features <= pca_components, skip PCA.
    Always scale data first. Use random_state=42 for both PCA and t-SNE.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        pca_components: Number of PCA components for initial reduction.

    Returns:
        Transformed data of shape (n_samples, 2).

    >>> rng = np.random.RandomState(42)
    >>> X_high = rng.randn(100, 200)
    >>> result = pca_then_tsne(X_high, pca_components=50)
    >>> result.shape == (100, 2)
    True
    """
    pass


# =============================================================================
# ANOMALY DETECTION
# =============================================================================

# Exercise 13: Isolation Forest
# Difficulty: Medium
# Fit an Isolation Forest and return a boolean mask where True = anomaly.
def detect_anomalies_iforest(
    X: np.ndarray, contamination: float = 0.1
) -> np.ndarray:
    """Detect anomalies using Isolation Forest.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        contamination: Expected proportion of outliers (0 to 0.5).

    Returns:
        Boolean array of shape (n_samples,) where True indicates anomaly.

    >>> rng = np.random.RandomState(42)
    >>> X_normal = rng.randn(100, 2)
    >>> X_outliers = rng.uniform(-6, 6, size=(10, 2))
    >>> X_all = np.vstack([X_normal, X_outliers])
    >>> anomalies = detect_anomalies_iforest(X_all, contamination=0.1)
    >>> anomalies.dtype == np.dtype('bool')
    True
    >>> anomalies.sum() > 0
    True
    """
    pass


# Exercise 14: Local Outlier Factor
# Difficulty: Medium
# Fit LOF and return anomaly scores (negative_outlier_factor_).
# More negative = more anomalous.
def lof_scores(X: np.ndarray, n_neighbors: int = 20) -> np.ndarray:
    """Compute Local Outlier Factor scores.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        n_neighbors: Number of neighbors for LOF.

    Returns:
        Array of LOF scores of shape (n_samples,).
        More negative values indicate stronger outliers.

    >>> rng = np.random.RandomState(42)
    >>> X_normal = rng.randn(100, 2)
    >>> scores = lof_scores(X_normal, n_neighbors=20)
    >>> scores.shape == (100,)
    True
    >>> all(s <= 0 for s in scores)
    True
    """
    pass


# Exercise 15: Full Unsupervised Pipeline
# Difficulty: Hard
# Combine scaling, PCA, and K-Means in a single function.
# Scale the data, reduce to n_pca_components with PCA, then cluster with K-Means.
# Return a dict with 'labels', 'centers_original' (cluster centers in original
# space via inverse_transform), and 'explained_variance' (cumulative).
def unsupervised_pipeline(
    X: np.ndarray, n_pca_components: int = 2, n_clusters: int = 3
) -> dict:
    """Full unsupervised pipeline: scale -> PCA -> K-Means.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        n_pca_components: Number of PCA components.
        n_clusters: Number of K-Means clusters.

    Returns:
        Dict with keys:
            'labels': cluster labels array of shape (n_samples,)
            'centers_original': cluster centers in original (scaled) space,
                shape (n_clusters, n_features)
            'explained_variance': cumulative explained variance ratio (float),
                the total variance explained by the chosen components.

    >>> iris = load_iris()
    >>> result = unsupervised_pipeline(iris.data, n_pca_components=2, n_clusters=3)
    >>> result['labels'].shape == (150,)
    True
    >>> result['centers_original'].shape == (3, 4)
    True
    >>> 0.0 < result['explained_variance'] <= 1.0
    True
    """
    pass


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    print("Running Exercise 1: Basic K-Means...")
    X1, _ = make_blobs(n_samples=100, centers=3, random_state=42)
    labels1 = kmeans_basic(X1)
    assert labels1.shape == (100,), f"Expected shape (100,), got {labels1.shape}"
    assert len(set(labels1)) == 3, f"Expected 3 clusters, got {len(set(labels1))}"
    print("  PASSED")

    print("Running Exercise 2: Elbow Method...")
    inertias = compute_elbow_values(X1, max_k=5)
    assert len(inertias) == 5, f"Expected 5 values, got {len(inertias)}"
    assert all(inertias[i] >= inertias[i + 1] for i in range(len(inertias) - 1)), \
        "Inertias should be non-increasing"
    print("  PASSED")

    print("Running Exercise 3: Best K Silhouette...")
    X3, _ = make_blobs(n_samples=200, centers=4, random_state=42)
    best_k = best_k_silhouette(X3, max_k=8)
    assert best_k == 4, f"Expected K=4, got K={best_k}"
    print("  PASSED")

    print("Running Exercise 4: DBSCAN Moons...")
    X4, _ = make_moons(n_samples=200, noise=0.05, random_state=42)
    labels4 = dbscan_moons(X4)
    n_clusters4 = len(set(labels4)) - (1 if -1 in labels4 else 0)
    assert n_clusters4 == 2, f"Expected 2 clusters, got {n_clusters4}"
    print("  PASSED")

    print("Running Exercise 5: Count Noise Points...")
    labels5 = np.array([0, 0, 1, -1, 1, -1, 0])
    assert count_noise_points(labels5) == 2
    print("  PASSED")

    print("Running Exercise 6: Agglomerative Clustering...")
    X6, _ = make_blobs(n_samples=100, centers=3, random_state=42)
    labels6 = agglomerative_cluster(X6, n_clusters=3)
    assert len(set(labels6)) == 3
    print("  PASSED")

    print("Running Exercise 7: GMM Cluster...")
    X7, _ = make_blobs(n_samples=100, centers=3, random_state=42)
    labels7, probs7 = gmm_cluster(X7, n_components=3)
    assert probs7.shape == (100, 3)
    assert np.allclose(probs7.sum(axis=1), 1.0)
    print("  PASSED")

    print("Running Exercise 8: Best GMM Components...")
    X8, _ = make_blobs(n_samples=300, centers=4, random_state=42)
    best_n = best_gmm_components(X8, max_components=8)
    assert best_n == 4, f"Expected 4, got {best_n}"
    print("  PASSED")

    print("Running Exercise 9: PCA Basics...")
    iris = load_iris()
    X_pca = pca_reduce(iris.data, n_components=2)
    assert X_pca.shape == (150, 2)
    print("  PASSED")

    print("Running Exercise 10: PCA Min Components...")
    min_comp = pca_min_components(iris.data, threshold=0.95)
    assert min_comp == 2, f"Expected 2, got {min_comp}"
    print("  PASSED")

    print("Running Exercise 11: t-SNE Reduce...")
    X_tsne = tsne_reduce(iris.data)
    assert X_tsne.shape == (150, 2)
    print("  PASSED")

    print("Running Exercise 12: PCA then t-SNE...")
    rng = np.random.RandomState(42)
    X_high = rng.randn(100, 200)
    X_pt = pca_then_tsne(X_high, pca_components=50)
    assert X_pt.shape == (100, 2)
    print("  PASSED")

    print("Running Exercise 13: Isolation Forest...")
    rng13 = np.random.RandomState(42)
    X_n = rng13.randn(100, 2)
    X_o = rng13.uniform(-6, 6, size=(10, 2))
    X_all13 = np.vstack([X_n, X_o])
    anom = detect_anomalies_iforest(X_all13, contamination=0.1)
    assert anom.dtype == np.dtype('bool')
    assert anom.sum() > 0
    print("  PASSED")

    print("Running Exercise 14: LOF Scores...")
    rng14 = np.random.RandomState(42)
    X14 = rng14.randn(100, 2)
    scores14 = lof_scores(X14, n_neighbors=20)
    assert scores14.shape == (100,)
    assert all(s <= 0 for s in scores14)
    print("  PASSED")

    print("Running Exercise 15: Full Pipeline...")
    result15 = unsupervised_pipeline(iris.data, n_pca_components=2, n_clusters=3)
    assert result15['labels'].shape == (150,)
    assert result15['centers_original'].shape == (3, 4)
    assert 0.0 < result15['explained_variance'] <= 1.0
    print("  PASSED")

    print("\nAll exercises passed!")
