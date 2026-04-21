"""
Module 05: Unsupervised Learning - Solutions
=============================================
Complete solutions for all exercises.
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


# Exercise 1: Basic K-Means
def kmeans_basic(X: np.ndarray) -> np.ndarray:
    """Fit K-Means with 3 clusters and return labels."""
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    return kmeans.fit_predict(X)


# Exercise 2: Elbow Method
def compute_elbow_values(X: np.ndarray, max_k: int = 10) -> list[float]:
    """Compute K-Means inertia for K=1 to max_k (inclusive)."""
    inertias = []
    for k in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        inertias.append(kmeans.inertia_)
    return inertias


# Exercise 3: Silhouette Analysis
def best_k_silhouette(X: np.ndarray, max_k: int = 8) -> int:
    """Find the K with the highest silhouette score."""
    best_score = -1.0
    best_k = 2
    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        if score > best_score:
            best_score = score
            best_k = k
    return best_k


# Exercise 4: DBSCAN Moons
def dbscan_moons(X: np.ndarray, eps: float = 0.2, min_samples: int = 5) -> np.ndarray:
    """Apply DBSCAN clustering and return labels (noise = -1)."""
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    return dbscan.fit_predict(X)


# Exercise 5: Count DBSCAN Noise Points
def count_noise_points(labels: np.ndarray) -> int:
    """Count noise points in DBSCAN output."""
    return int(np.sum(labels == -1))


# Exercise 6: Agglomerative Clustering
def agglomerative_cluster(
    X: np.ndarray, n_clusters: int = 3, linkage: str = "ward"
) -> np.ndarray:
    """Perform agglomerative clustering and return labels."""
    agg = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
    return agg.fit_predict(X)


# Exercise 7: Gaussian Mixture Model
def gmm_cluster(
    X: np.ndarray, n_components: int = 3
) -> tuple[np.ndarray, np.ndarray]:
    """Fit a Gaussian Mixture Model and return labels and probabilities."""
    gmm = GaussianMixture(n_components=n_components, random_state=42)
    gmm.fit(X)
    labels = gmm.predict(X)
    probs = gmm.predict_proba(X)
    return labels, probs


# Exercise 8: GMM Model Selection with BIC
def best_gmm_components(X: np.ndarray, max_components: int = 8) -> int:
    """Find optimal number of GMM components using BIC."""
    best_bic = np.inf
    best_n = 1
    for n in range(1, max_components + 1):
        gmm = GaussianMixture(n_components=n, random_state=42)
        gmm.fit(X)
        bic = gmm.bic(X)
        if bic < best_bic:
            best_bic = bic
            best_n = n
    return best_n


# Exercise 9: PCA Basics
def pca_reduce(X: np.ndarray, n_components: int = 2) -> np.ndarray:
    """Scale data with StandardScaler, then apply PCA."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA(n_components=n_components, random_state=42)
    return pca.fit_transform(X_scaled)


# Exercise 10: PCA Explained Variance
def pca_min_components(X: np.ndarray, threshold: float = 0.95) -> int:
    """Find minimum components to explain threshold fraction of variance."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA(random_state=42)
    pca.fit(X_scaled)
    cumulative = np.cumsum(pca.explained_variance_ratio_)
    # Find first index where cumulative variance >= threshold
    n_components = int(np.argmax(cumulative >= threshold) + 1)
    return n_components


# Exercise 11: t-SNE Visualization Data
def tsne_reduce(X: np.ndarray, perplexity: float = 30.0) -> np.ndarray:
    """Scale data and apply t-SNE to reduce to 2 dimensions."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
    return tsne.fit_transform(X_scaled)


# Exercise 12: PCA then t-SNE Pipeline
def pca_then_tsne(X: np.ndarray, pca_components: int = 50) -> np.ndarray:
    """Scale data, optionally reduce with PCA, then apply t-SNE to 2D."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if X_scaled.shape[1] > pca_components:
        pca = PCA(n_components=pca_components, random_state=42)
        X_scaled = pca.fit_transform(X_scaled)

    tsne = TSNE(n_components=2, random_state=42)
    return tsne.fit_transform(X_scaled)


# Exercise 13: Isolation Forest
def detect_anomalies_iforest(
    X: np.ndarray, contamination: float = 0.1
) -> np.ndarray:
    """Detect anomalies using Isolation Forest."""
    iso = IsolationForest(contamination=contamination, random_state=42)
    predictions = iso.fit_predict(X)
    # Convert: 1 = inlier (False), -1 = outlier (True)
    return predictions == -1


# Exercise 14: Local Outlier Factor
def lof_scores(X: np.ndarray, n_neighbors: int = 20) -> np.ndarray:
    """Compute Local Outlier Factor scores."""
    lof = LocalOutlierFactor(n_neighbors=n_neighbors)
    lof.fit_predict(X)
    return lof.negative_outlier_factor_


# Exercise 15: Full Unsupervised Pipeline
def unsupervised_pipeline(
    X: np.ndarray, n_pca_components: int = 2, n_clusters: int = 3
) -> dict:
    """Full unsupervised pipeline: scale -> PCA -> K-Means."""
    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA
    pca = PCA(n_components=n_pca_components, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    # K-Means on PCA-reduced data
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_pca)

    # Map cluster centers back to original (scaled) space
    centers_pca = kmeans.cluster_centers_                 # shape (n_clusters, n_pca_components)
    centers_original = pca.inverse_transform(centers_pca)  # shape (n_clusters, n_features)

    # Cumulative explained variance
    explained_variance = float(np.sum(pca.explained_variance_ratio_))

    return {
        'labels': labels,
        'centers_original': centers_original,
        'explained_variance': explained_variance,
    }


# =============================================================================
# SELF-CHECK
# =============================================================================

if __name__ == "__main__":
    print("Running Exercise 1: Basic K-Means...")
    X1, _ = make_blobs(n_samples=100, centers=3, random_state=42)
    labels1 = kmeans_basic(X1)
    assert labels1.shape == (100,)
    assert len(set(labels1)) == 3
    print("  PASSED")

    print("Running Exercise 2: Elbow Method...")
    inertias = compute_elbow_values(X1, max_k=5)
    assert len(inertias) == 5
    assert all(inertias[i] >= inertias[i + 1] for i in range(len(inertias) - 1))
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
    assert n_clusters4 == 2
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
