# Module 05: Unsupervised Learning

## Table of Contents

1. [Introduction to Unsupervised Learning](#1-introduction-to-unsupervised-learning)
2. [K-Means Clustering](#2-k-means-clustering)
3. [DBSCAN](#3-dbscan)
4. [Hierarchical Clustering](#4-hierarchical-clustering)
5. [Gaussian Mixture Models](#5-gaussian-mixture-models)
6. [PCA -- Principal Component Analysis](#6-pca----principal-component-analysis)
7. [t-SNE](#7-t-sne)
8. [UMAP](#8-umap)
9. [Anomaly Detection](#9-anomaly-detection)
10. [Choosing the Right Algorithm](#10-choosing-the-right-algorithm)

---

## 1. Introduction to Unsupervised Learning

In supervised learning (the previous modules), every training example had a label -- the "right
answer." Unsupervised learning works with **unlabeled data**. The goal is to discover hidden
structure: groups, patterns, compressed representations, or outliers.

### Swift Analogy

Think of supervised learning like Core ML with a labeled image dataset -- each photo is tagged
"cat" or "dog." Unsupervised learning is more like the Photos app's automatic "People" album:
it groups faces together without anyone telling it which face belongs to whom.

### Three Major Tasks

| Task | Goal | Example |
|------|------|---------|
| **Clustering** | Group similar data points | Customer segmentation |
| **Dimensionality Reduction** | Compress features while preserving information | Visualizing high-dimensional embeddings |
| **Anomaly Detection** | Find unusual data points | Fraud detection |

```python
# Quick imports we'll use throughout this module
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs, make_moons, load_iris

# Generate sample clustered data
X, y_true = make_blobs(n_samples=300, centers=4, cluster_std=0.8, random_state=42)

plt.scatter(X[:, 0], X[:, 1], s=30, alpha=0.7)
plt.title("Unlabeled Data -- Can You See the Clusters?")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.show()
```

---

## 2. K-Means Clustering

K-Means is the most widely used clustering algorithm. It partitions data into **K** clusters by
iteratively assigning points to the nearest centroid and then updating centroids.

### The Algorithm

1. **Initialize** K centroids (randomly or with k-means++).
2. **Assign** each data point to its nearest centroid.
3. **Update** each centroid to the mean of its assigned points.
4. **Repeat** steps 2--3 until centroids stabilize (convergence).

```python
from sklearn.cluster import KMeans

# Fit K-Means with 4 clusters
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
labels = kmeans.fit_predict(X)

# Inspect results
print(f"Cluster centers shape: {kmeans.cluster_centers_.shape}")  # (4, 2)
print(f"Inertia (within-cluster sum of squares): {kmeans.inertia_:.2f}")
print(f"Unique labels: {np.unique(labels)}")  # [0, 1, 2, 3]

# Visualize
plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', s=30, alpha=0.7)
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1],
            c='red', marker='X', s=200, edgecolors='black', linewidths=1.5)
plt.title("K-Means Clustering (K=4)")
plt.show()
```

### The Elbow Method -- Choosing K

The elbow method plots the **inertia** (within-cluster sum of squares) against different values
of K. The "elbow" -- where the curve bends sharply -- suggests a good K.

```python
inertias = []
K_range = range(1, 11)

for k in K_range:
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    model.fit(X)
    inertias.append(model.inertia_)

plt.figure(figsize=(8, 4))
plt.plot(K_range, inertias, 'bo-')
plt.xlabel("Number of Clusters (K)")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.xticks(K_range)
plt.grid(True, alpha=0.3)
plt.show()
```

### Silhouette Score -- Quantifying Cluster Quality

The silhouette score measures how similar a point is to its own cluster compared to other
clusters. Values range from -1 (wrong cluster) to +1 (well-clustered).

```python
from sklearn.metrics import silhouette_score, silhouette_samples

# Compute silhouette score for different K
for k in range(2, 8):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels_k = km.fit_predict(X)
    score = silhouette_score(X, labels_k)
    print(f"K={k}: Silhouette Score = {score:.3f}")

# Per-sample silhouette values (useful for visualization)
sample_scores = silhouette_samples(X, labels)
print(f"Mean silhouette: {sample_scores.mean():.3f}")
```

### K-Means Limitations

- Assumes **spherical, equal-sized clusters** -- fails on elongated or irregular shapes.
- You must **choose K** in advance.
- Sensitive to **initialization** -- use `n_init=10` (the default) or `init='k-means++'`.
- Sensitive to **outliers** -- a single outlier can drag a centroid.

---

## 3. DBSCAN

DBSCAN (Density-Based Spatial Clustering of Applications with Noise) finds clusters based on
**density** rather than distance to centroids. It naturally discovers the number of clusters
and handles noise.

### Key Parameters

| Parameter | Description | Rule of Thumb |
|-----------|-------------|---------------|
| `eps` | Maximum distance between two points to be neighbors | Plot k-distance graph |
| `min_samples` | Minimum points to form a dense region | Usually `2 * n_features` |

### Point Classifications

- **Core point**: has at least `min_samples` neighbors within `eps`.
- **Border point**: within `eps` of a core point but not itself a core point.
- **Noise point**: neither core nor border -- labeled as `-1`.

```python
from sklearn.cluster import DBSCAN

# Generate non-spherical data (moons)
X_moons, y_moons = make_moons(n_samples=300, noise=0.05, random_state=42)

# DBSCAN -- no need to specify number of clusters!
dbscan = DBSCAN(eps=0.2, min_samples=5)
labels_db = dbscan.fit_predict(X_moons)

# Check results
n_clusters = len(set(labels_db)) - (1 if -1 in labels_db else 0)
n_noise = list(labels_db).count(-1)
print(f"Clusters found: {n_clusters}")
print(f"Noise points: {n_noise}")

# Visualize -- noise points shown in black
plt.scatter(X_moons[:, 0], X_moons[:, 1], c=labels_db, cmap='viridis', s=30)
plt.title(f"DBSCAN: {n_clusters} clusters, {n_noise} noise points")
plt.show()
```

### Choosing eps with the k-Distance Graph

```python
from sklearn.neighbors import NearestNeighbors

# Compute distance to k-th nearest neighbor
k = 5  # same as min_samples
nn = NearestNeighbors(n_neighbors=k)
nn.fit(X_moons)
distances, _ = nn.kneighbors(X_moons)

# Sort distances to k-th neighbor
k_distances = np.sort(distances[:, k - 1])

plt.plot(k_distances)
plt.xlabel("Points (sorted)")
plt.ylabel(f"Distance to {k}-th nearest neighbor")
plt.title("k-Distance Graph (look for the 'elbow')")
plt.grid(True, alpha=0.3)
plt.show()
```

### DBSCAN vs. K-Means

| Feature | K-Means | DBSCAN |
|---------|---------|--------|
| Cluster shape | Spherical | Arbitrary |
| Number of clusters | Must specify K | Auto-detected |
| Handles noise | No | Yes (labels noise as -1) |
| Cluster sizes | Roughly equal | Variable |
| Scalability | Fast (O(n)) | Slower (O(n log n) with tree) |

---

## 4. Hierarchical Clustering

Hierarchical clustering builds a tree-like structure (dendrogram) showing nested groupings.
Two approaches:

- **Agglomerative** (bottom-up): start with each point as its own cluster, merge the closest pairs.
- **Divisive** (top-down): start with one cluster, recursively split.

### Agglomerative Clustering with sklearn

```python
from sklearn.cluster import AgglomerativeClustering

agg = AgglomerativeClustering(n_clusters=4, linkage='ward')
labels_agg = agg.fit_predict(X)

plt.scatter(X[:, 0], X[:, 1], c=labels_agg, cmap='viridis', s=30)
plt.title("Agglomerative Clustering (Ward linkage)")
plt.show()
```

### Dendrograms with scipy

```python
from scipy.cluster.hierarchy import dendrogram, linkage

# Compute linkage matrix (use a subset for readability)
X_subset = X[:50]
Z = linkage(X_subset, method='ward')

plt.figure(figsize=(12, 5))
dendrogram(Z, truncate_mode='level', p=5)
plt.title("Dendrogram (Ward Linkage)")
plt.xlabel("Sample index or (cluster size)")
plt.ylabel("Distance")
plt.show()
```

### Linkage Methods

| Method | Description | Best For |
|--------|-------------|----------|
| `ward` | Minimizes variance increase | Compact, equal-sized clusters |
| `complete` | Maximum distance between clusters | Well-separated clusters |
| `average` | Mean distance between clusters | General purpose |
| `single` | Minimum distance between clusters | Elongated clusters (but noisy) |

---

## 5. Gaussian Mixture Models

GMMs model data as a mixture of K Gaussian distributions. Unlike K-Means, which makes hard
assignments, GMMs provide **soft assignments** -- a probability that each point belongs to
each cluster.

### Swift Analogy

K-Means is like assigning each photo to exactly one album. GMM is like tagging each photo
with a probability distribution: "70% landscape, 25% architecture, 5% portrait."

```python
from sklearn.mixture import GaussianMixture

# Fit a GMM with 4 components
gmm = GaussianMixture(n_components=4, random_state=42)
gmm.fit(X)

# Hard labels
labels_gmm = gmm.predict(X)

# Soft probabilities
probs = gmm.predict_proba(X)
print(f"Probability shape: {probs.shape}")       # (300, 4)
print(f"First point probs: {probs[0].round(3)}")  # e.g., [0.001, 0.998, 0.001, 0.000]

# Model selection with BIC/AIC
n_components_range = range(1, 10)
bics = []
aics = []
for n in n_components_range:
    gm = GaussianMixture(n_components=n, random_state=42)
    gm.fit(X)
    bics.append(gm.bic(X))
    aics.append(gm.aic(X))

plt.plot(n_components_range, bics, 'bo-', label='BIC')
plt.plot(n_components_range, aics, 'rs-', label='AIC')
plt.xlabel("Number of Components")
plt.ylabel("Score")
plt.title("GMM Model Selection")
plt.legend()
plt.show()
```

### GMM vs. K-Means

| Feature | K-Means | GMM |
|---------|---------|-----|
| Assignment | Hard (0 or 1) | Soft (probabilities) |
| Cluster shape | Spherical | Elliptical |
| Model selection | Elbow/silhouette | BIC/AIC |
| Speed | Faster | Slower |

---

## 6. PCA -- Principal Component Analysis

PCA is the most common dimensionality reduction technique. It finds new axes (principal
components) that capture the maximum variance in the data. Each component is a linear
combination of the original features.

### Why Reduce Dimensions?

- **Visualization**: project high-dimensional data to 2D or 3D.
- **Noise reduction**: discard low-variance components.
- **Speed**: fewer features = faster model training.
- **Curse of dimensionality**: many algorithms degrade with too many features.

### PCA in Action

```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris

# Load Iris (4 features -> reduce to 2)
iris = load_iris()
X_iris = StandardScaler().fit_transform(iris.data)  # Always scale before PCA!

# Fit PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_iris)

print(f"Original shape: {iris.data.shape}")    # (150, 4)
print(f"Reduced shape:  {X_pca.shape}")         # (150, 2)
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
# e.g., [0.7296, 0.2285] -- first 2 PCs capture ~96% of variance

# Visualize
for label in np.unique(iris.target):
    mask = iris.target == label
    plt.scatter(X_pca[mask, 0], X_pca[mask, 1],
                label=iris.target_names[label], s=30, alpha=0.7)
plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
plt.title("PCA of Iris Dataset")
plt.legend()
plt.show()
```

### Scree Plot and Choosing Components

```python
# Fit PCA with all components to see the full picture
pca_full = PCA()
pca_full.fit(X_iris)

# Scree plot
explained_var = pca_full.explained_variance_ratio_
cumulative_var = np.cumsum(explained_var)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

ax1.bar(range(1, len(explained_var) + 1), explained_var)
ax1.set_xlabel("Principal Component")
ax1.set_ylabel("Explained Variance Ratio")
ax1.set_title("Scree Plot")

ax2.plot(range(1, len(cumulative_var) + 1), cumulative_var, 'bo-')
ax2.axhline(y=0.95, color='r', linestyle='--', label='95% threshold')
ax2.set_xlabel("Number of Components")
ax2.set_ylabel("Cumulative Explained Variance")
ax2.set_title("Cumulative Variance")
ax2.legend()

plt.tight_layout()
plt.show()
```

### Automatic Component Selection

```python
# Let PCA choose components that explain 95% of variance
pca_auto = PCA(n_components=0.95)
X_auto = pca_auto.fit_transform(X_iris)
print(f"Components needed for 95%: {pca_auto.n_components_}")
```

### Inspecting Component Loadings

```python
# Each component is a linear combination of original features
loadings = pd.DataFrame(
    pca.components_.T,
    columns=['PC1', 'PC2'],
    index=iris.feature_names
)
print(loadings)
# Shows which original features contribute most to each PC
```

---

## 7. t-SNE

t-Distributed Stochastic Neighbor Embedding (t-SNE) is a **nonlinear** dimensionality
reduction technique specifically designed for **visualization** of high-dimensional data.

### Key Differences from PCA

| Feature | PCA | t-SNE |
|---------|-----|-------|
| Type | Linear | Nonlinear |
| Preserves | Global variance | Local neighborhoods |
| Use case | Preprocessing, compression | Visualization only |
| Deterministic | Yes | No (stochastic) |
| Inverse transform | Yes | No |
| Speed | Fast | Slow on large data |

### Using t-SNE

```python
from sklearn.manifold import TSNE

# t-SNE on Iris data
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
X_tsne = tsne.fit_transform(X_iris)

for label in np.unique(iris.target):
    mask = iris.target == label
    plt.scatter(X_tsne[mask, 0], X_tsne[mask, 1],
                label=iris.target_names[label], s=30, alpha=0.7)
plt.title("t-SNE of Iris Dataset")
plt.legend()
plt.show()
```

### Perplexity -- The Key Hyperparameter

Perplexity controls the balance between local and global structure. It roughly corresponds
to the number of nearest neighbors considered.

```python
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for ax, perp in zip(axes, [5, 30, 100]):
    tsne_p = TSNE(n_components=2, perplexity=perp, random_state=42)
    X_t = tsne_p.fit_transform(X_iris)
    ax.scatter(X_t[:, 0], X_t[:, 1], c=iris.target, cmap='viridis', s=20)
    ax.set_title(f"Perplexity = {perp}")

plt.suptitle("Effect of Perplexity on t-SNE")
plt.tight_layout()
plt.show()
```

### t-SNE Gotchas

1. **Do not interpret distances between clusters** -- only within-cluster structure is meaningful.
2. **Do not compare across runs** -- different random seeds give different layouts.
3. **Cannot transform new data** -- there is no `.transform()` method; use PCA first to reduce
   dimensions before t-SNE for large datasets.
4. **Slow on large data** -- use PCA to reduce to 50 dimensions first, then apply t-SNE.

---

## 8. UMAP

UMAP (Uniform Manifold Approximation and Projection) is a newer alternative to t-SNE that
is faster and better at preserving global structure.

```python
# pip install umap-learn
import umap

# UMAP on Iris data
reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=42)
X_umap = reducer.fit_transform(X_iris)

for label in np.unique(iris.target):
    mask = iris.target == label
    plt.scatter(X_umap[mask, 0], X_umap[mask, 1],
                label=iris.target_names[label], s=30, alpha=0.7)
plt.title("UMAP of Iris Dataset")
plt.legend()
plt.show()
```

### Key UMAP Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_neighbors` | 15 | Controls local vs. global structure (like perplexity) |
| `min_dist` | 0.1 | Minimum distance between points in output (0 = tighter clusters) |
| `metric` | 'euclidean' | Distance metric (supports many) |

### UMAP vs. t-SNE

| Feature | t-SNE | UMAP |
|---------|-------|------|
| Speed | Slow | Fast (10-100x faster) |
| Global structure | Poor | Better preserved |
| Transform new data | No | Yes (`.transform()`) |
| Scalability | ~10K points | Millions of points |
| Deterministic | No | Yes (with `random_state`) |

---

## 9. Anomaly Detection

Anomaly detection identifies data points that differ significantly from the majority. This
is crucial in fraud detection, network security, manufacturing quality control, and health
monitoring.

### Isolation Forest

Isolation Forest isolates anomalies by randomly selecting features and split values. Anomalies
are isolated quickly (fewer splits), while normal points require many splits.

```python
from sklearn.ensemble import IsolationForest

# Generate data with outliers
rng = np.random.RandomState(42)
X_normal = 0.3 * rng.randn(200, 2)
X_outliers = rng.uniform(low=-4, high=4, size=(20, 2))
X_all = np.vstack([X_normal, X_outliers])

# Fit Isolation Forest
iso_forest = IsolationForest(contamination=0.1, random_state=42)
predictions = iso_forest.fit_predict(X_all)

# predictions: 1 = inlier, -1 = outlier
print(f"Inliers: {(predictions == 1).sum()}")
print(f"Outliers: {(predictions == -1).sum()}")

# Anomaly scores (lower = more anomalous)
scores = iso_forest.decision_function(X_all)
print(f"Score range: [{scores.min():.3f}, {scores.max():.3f}]")

# Visualize
colors = ['blue' if p == 1 else 'red' for p in predictions]
plt.scatter(X_all[:, 0], X_all[:, 1], c=colors, s=30, alpha=0.7)
plt.title("Isolation Forest: Blue=Normal, Red=Anomaly")
plt.show()
```

### Local Outlier Factor (LOF)

LOF measures the local density deviation of a point with respect to its neighbors. Points
in low-density regions compared to their neighbors are considered outliers.

```python
from sklearn.neighbors import LocalOutlierFactor

# LOF is primarily designed for novelty detection (predict on training data)
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
predictions_lof = lof.fit_predict(X_all)

# Negative outlier factor -- more negative = more anomalous
scores_lof = lof.negative_outlier_factor_
print(f"LOF score range: [{scores_lof.min():.3f}, {scores_lof.max():.3f}]")

# Visualize
colors_lof = ['blue' if p == 1 else 'red' for p in predictions_lof]
plt.scatter(X_all[:, 0], X_all[:, 1], c=colors_lof, s=30, alpha=0.7)
plt.title("Local Outlier Factor: Blue=Normal, Red=Anomaly")
plt.show()
```

### Isolation Forest vs. LOF

| Feature | Isolation Forest | LOF |
|---------|-----------------|-----|
| Approach | Random partitioning | Local density |
| Speed | Fast | Moderate |
| New data | Can predict on new data | Primarily fit_predict only |
| Best for | Global outliers | Local outliers (varying density) |

---

## 10. Choosing the Right Algorithm

### Clustering Decision Guide

```
Is the number of clusters known?
├── Yes
│   ├── Spherical clusters? → K-Means
│   └── Elliptical clusters? → GMM
└── No
    ├── Noisy data? → DBSCAN
    └── Need hierarchy? → Agglomerative
```

### Dimensionality Reduction Decision Guide

```
What is your goal?
├── Preprocessing / speed improvement → PCA
├── Visualization only
│   ├── Small dataset (<10K) → t-SNE
│   └── Large dataset → UMAP
└── Need to transform new data?
    ├── Yes → PCA or UMAP
    └── No → t-SNE is fine
```

### Quick Reference Table

| Algorithm | Type | Key Strength | Key Weakness |
|-----------|------|-------------|--------------|
| K-Means | Clustering | Fast, simple | Assumes spherical clusters |
| DBSCAN | Clustering | Finds arbitrary shapes, handles noise | Sensitive to eps/min_samples |
| Agglomerative | Clustering | Dendrogram visualization | Slow on large data |
| GMM | Clustering | Soft assignments, elliptical clusters | Needs component count |
| PCA | Dim. reduction | Fast, invertible, interpretable | Linear only |
| t-SNE | Dim. reduction | Excellent local structure | Slow, no transform |
| UMAP | Dim. reduction | Fast, preserves global structure | Requires extra install |
| Isolation Forest | Anomaly | Fast, scalable | Contamination parameter |
| LOF | Anomaly | Local density awareness | Primarily fit_predict only |

### General Tips

1. **Always scale your data** before clustering or PCA (use `StandardScaler`).
2. **Visualize first** -- plot your data before choosing an algorithm.
3. **Try multiple algorithms** -- no single method works best for all data.
4. **Use silhouette score** or **BIC/AIC** to compare cluster quality.
5. **PCA before t-SNE** -- reduce to 50 dimensions with PCA, then apply t-SNE for speed.

---

## Summary

| Concept | Key Takeaway |
|---------|-------------|
| K-Means | Fast, spherical clusters; use elbow method and silhouette score |
| DBSCAN | Density-based; auto-detects clusters and noise |
| Hierarchical | Dendrograms show cluster hierarchy; Ward linkage is a good default |
| GMM | Soft assignments with probabilities; use BIC for model selection |
| PCA | Linear reduction; explained variance guides component choice |
| t-SNE | Nonlinear visualization; do not over-interpret distances |
| UMAP | Faster t-SNE alternative; preserves more global structure |
| Isolation Forest | Anomaly detection via random partitioning |
| LOF | Anomaly detection via local density comparison |
