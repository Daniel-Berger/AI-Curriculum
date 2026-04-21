# ML Fundamentals Interview Questions

20 commonly asked machine learning interview questions with concise, structured answers.

---

## 1. Explain the bias-variance tradeoff

**Bias** is the error from overly simplistic assumptions in the model (underfitting). **Variance** is the error from sensitivity to small fluctuations in the training set (overfitting).

- **High bias**: Model misses relevant relations (e.g., linear model on nonlinear data)
- **High variance**: Model captures noise as if it were signal (e.g., deep tree on small data)
- **Tradeoff**: Increasing model complexity decreases bias but increases variance, and vice versa
- **Total Error** = Bias^2 + Variance + Irreducible Noise
- **Goal**: Find the sweet spot where total error is minimized (the "U" curve)

**Example**: A degree-1 polynomial on curved data has high bias. A degree-20 polynomial on 10 data points has high variance. A degree-3 polynomial might be just right.

---

## 2. Precision vs Recall vs F1

All three are classification metrics, especially important for imbalanced datasets.

| Metric | Formula | Answers the question |
|--------|---------|---------------------|
| **Precision** | TP / (TP + FP) | "Of all positive predictions, how many were correct?" |
| **Recall** | TP / (TP + FN) | "Of all actual positives, how many did we find?" |
| **F1** | 2 * (P * R) / (P + R) | "Harmonic mean of precision and recall" |

**When to prioritize precision**: Spam filtering (don't lose important emails), content moderation
**When to prioritize recall**: Cancer screening (don't miss a positive case), fraud detection
**F1** is useful when you need a single metric and care about both equally.

**Note**: F1 uses harmonic mean (not arithmetic) because it penalizes imbalance. P=1.0, R=0.01 gives F1=0.02, not 0.505.

---

## 3. How do you prevent overfitting?

Overfitting occurs when a model learns training noise instead of the underlying pattern.

**Data-side approaches**:
- Get more training data
- Data augmentation (flips, crops, noise injection)
- Clean noisy labels

**Model-side approaches**:
- Reduce model complexity (fewer parameters, shallower trees)
- Regularization (L1/L2, dropout, weight decay)
- Early stopping (stop training when validation loss increases)
- Ensemble methods (bagging reduces variance)

**Training-side approaches**:
- Cross-validation for hyperparameter selection
- Proper train/validation/test split (no data leakage!)
- Batch normalization (acts as mild regularizer)

**Diagnosis**: Training loss keeps decreasing but validation loss starts increasing = overfitting.

---

## 4. Gradient descent variants

All variants minimize a loss function by iteratively moving in the direction of steepest descent.

| Variant | Batch Size | Pros | Cons |
|---------|-----------|------|------|
| **Batch GD** | Full dataset | Stable convergence, exact gradient | Slow on large datasets, memory-heavy |
| **Stochastic GD (SGD)** | 1 sample | Fast updates, can escape local minima | Noisy, unstable convergence |
| **Mini-batch GD** | 32-512 samples | Balance of speed and stability | Need to tune batch size |

**Modern optimizers**:
- **SGD + Momentum**: Accumulates velocity, dampens oscillations
- **RMSProp**: Adapts learning rate per-parameter using moving average of squared gradients
- **Adam**: Combines momentum + RMSProp. Default choice for most DL. Maintains first moment (mean) and second moment (variance) of gradients.
- **AdamW**: Adam with decoupled weight decay. Preferred for transformers.

---

## 5. Regularization: L1 vs L2

Both add a penalty term to the loss function to discourage large weights.

| | L1 (Lasso) | L2 (Ridge) |
|-|-----------|-----------|
| **Penalty** | lambda * sum(\|w\|) | lambda * sum(w^2) |
| **Effect on weights** | Drives some weights to exactly zero | Shrinks all weights toward zero |
| **Feature selection** | Yes (sparse solutions) | No (keeps all features) |
| **Geometry** | Diamond constraint region | Circular constraint region |
| **When to use** | When you suspect many irrelevant features | When all features are somewhat useful |

**Elastic Net** combines both: `alpha * L1 + (1-alpha) * L2`. Useful when features are correlated.

**Why L1 produces sparsity**: The diamond shape of the L1 constraint means the loss contour is more likely to intersect at a corner (where some weight = 0) rather than along an edge.

---

## 6. Cross-validation strategies

Cross-validation estimates model performance on unseen data and helps select hyperparameters.

| Strategy | Description | When to use |
|----------|-------------|-------------|
| **K-Fold** | Split data into K folds, train on K-1, validate on 1, rotate | Default choice (K=5 or 10) |
| **Stratified K-Fold** | K-Fold but preserves class distribution in each fold | Imbalanced classification |
| **Leave-One-Out (LOO)** | K-Fold where K=N (each sample is a fold) | Very small datasets |
| **Time Series Split** | Train on past, validate on future, expanding window | Temporal data (no future leakage!) |
| **Group K-Fold** | Ensures samples from same group stay in same fold | When samples are grouped (e.g., per-patient) |
| **Repeated K-Fold** | Run K-Fold multiple times with different splits | More reliable estimate, higher cost |

**Common mistake**: Using random K-Fold on time series data causes data leakage (training on future data).

---

## 7. Feature normalization

Scaling features to a common range improves convergence and prevents features with large magnitudes from dominating.

| Method | Formula | Range | When to use |
|--------|---------|-------|-------------|
| **Min-Max** | (x - min) / (max - min) | [0, 1] | Bounded data, neural networks |
| **Standard (Z-score)** | (x - mean) / std | ~[-3, 3] | Gaussian-like data, SVM, logistic regression |
| **Robust** | (x - median) / IQR | Variable | Data with outliers |
| **Log transform** | log(x) | Variable | Skewed distributions (incomes, counts) |

**Important rules**:
- Fit the scaler on training data only, then transform both train and test (no data leakage)
- Tree-based models (RF, XGBoost) generally don't need normalization
- Distance-based models (KNN, SVM, K-means) and gradient-based models (neural nets) benefit greatly

---

## 8. Ensemble methods

Combine multiple models to achieve better performance than any single model.

**Bagging (Bootstrap Aggregating)**:
- Train multiple models on random subsets (with replacement) of the data
- Aggregate by voting (classification) or averaging (regression)
- Reduces variance. Example: Random Forest
- Models trained independently (parallelizable)

**Boosting**:
- Train models sequentially, each focusing on previous errors
- Later models "boost" performance on hard examples
- Reduces bias. Examples: AdaBoost, Gradient Boosting, XGBoost, LightGBM
- Models are dependent (sequential)

**Stacking**:
- Train diverse base models, then train a meta-model on their predictions
- Can combine different model types (tree + SVM + neural net)
- Most flexible but most complex

**Key insight**: Bagging helps with high-variance models (deep trees). Boosting helps with high-bias models (shallow trees/stumps).

---

## 9. Decision tree vs Random Forest vs Gradient Boosting

| Aspect | Decision Tree | Random Forest | Gradient Boosting |
|--------|--------------|---------------|-------------------|
| **Type** | Single model | Bagging ensemble | Boosting ensemble |
| **Trees** | 1 deep tree | Many deep trees (parallel) | Many shallow trees (sequential) |
| **Bias** | Low | Low | Low (reduces with iterations) |
| **Variance** | High | Low (averaging) | Low (sequential correction) |
| **Overfitting** | Prone | Resistant | Can overfit if too many rounds |
| **Speed** | Fast | Medium (parallelizable) | Slower (sequential) |
| **Interpretability** | High | Low | Low |
| **Hyperparameters** | Few | Few | Many (learning rate, depth, etc.) |

**Practical guidance**:
- Start with Random Forest (robust, few hyperparameters)
- Use XGBoost/LightGBM for competitions and when you need maximum performance
- Use single decision tree only for interpretability requirements
- LightGBM is faster than XGBoost for large datasets (histogram-based splits)

---

## 10. PCA explained

**Principal Component Analysis** reduces dimensionality by projecting data onto directions of maximum variance.

**Steps**:
1. Standardize features (zero mean, unit variance)
2. Compute covariance matrix
3. Compute eigenvectors and eigenvalues of the covariance matrix
4. Sort eigenvectors by eigenvalue (descending)
5. Select top K eigenvectors as principal components
6. Project data onto these components

**Key concepts**:
- Each principal component is orthogonal to all others
- PC1 captures the most variance, PC2 the second most, and so on
- The eigenvalue tells you how much variance each component explains
- Choose K such that cumulative explained variance >= 95% (common threshold)

**When to use**: High-dimensional data, visualization (reduce to 2D/3D), remove multicollinearity, speed up downstream models.

**Limitations**: Linear only. Assumes variance = importance. Hard to interpret components. Use t-SNE/UMAP for nonlinear visualization.

---

## 11. K-means limitations

K-means partitions data into K clusters by minimizing within-cluster sum of squared distances.

**Limitations**:
1. **Must specify K in advance** - Use elbow method, silhouette score, or gap statistic to find optimal K
2. **Assumes spherical clusters** - Fails on elongated, ring-shaped, or irregular clusters
3. **Sensitive to initialization** - Use K-means++ initialization (default in scikit-learn) to mitigate
4. **Sensitive to outliers** - A single outlier can pull a centroid far from the true cluster center
5. **Assumes equal cluster sizes** - Tends to create equal-sized Voronoi cells even if true clusters vary in size
6. **Only finds convex clusters** - Cannot discover non-convex shapes (use DBSCAN or spectral clustering instead)
7. **Scale-dependent** - Features with larger ranges dominate distance; normalize first

**Alternatives**: DBSCAN (arbitrary shapes, auto-detects K), Gaussian Mixture Models (soft assignments, elliptical clusters), spectral clustering (non-convex clusters).

---

## 12. SVM kernel trick

**Support Vector Machines** find the maximum-margin hyperplane separating classes.

**The problem**: Many datasets are not linearly separable in their original feature space.

**The kernel trick**: Instead of explicitly mapping data to a higher-dimensional space (expensive), compute the dot product in that space directly using a kernel function.

| Kernel | Formula | Use case |
|--------|---------|----------|
| **Linear** | x^T * y | Linearly separable data, text classification |
| **RBF (Gaussian)** | exp(-gamma \|\|x-y\|\|^2) | Default choice, works well in most cases |
| **Polynomial** | (x^T * y + c)^d | Interaction features matter |

**Why it works**: SVM optimization only involves dot products between data points (not coordinates directly). We can replace dot products with kernel evaluations, implicitly working in a higher-dimensional space without ever computing the coordinates.

**Example**: Data on a circle (not linearly separable in 2D). RBF kernel implicitly maps to infinite-dimensional space where a hyperplane can separate them.

---

## 13. Naive Bayes assumptions

Naive Bayes is a probabilistic classifier based on Bayes' theorem with the "naive" assumption of feature independence.

**Core formula**: P(class|features) proportional to P(class) * product(P(feature_i|class))

**Assumptions**:
1. **Feature independence**: All features are conditionally independent given the class. This is almost never true in practice but the model works surprisingly well anyway.
2. **Feature distribution**: Gaussian NB assumes features follow normal distributions. Multinomial NB assumes count data. Bernoulli NB assumes binary features.
3. **Equal feature importance**: Each feature contributes equally (no feature weighting).

**Why it works despite violated assumptions**: Classification only requires ranking classes correctly, not calibrated probabilities. The independence assumption affects probability estimates but often preserves the correct ordering.

**Strengths**: Very fast training and inference, works well with high-dimensional sparse data (text classification), good baseline model, handles missing data naturally.

**Weaknesses**: Poor probability estimates, cannot learn feature interactions, performance degrades with correlated features.

---

## 14. ROC-AUC interpretation

**ROC Curve** plots True Positive Rate (recall) vs False Positive Rate at all classification thresholds.

- **X-axis**: FPR = FP / (FP + TN) - "How many negatives did we incorrectly flag?"
- **Y-axis**: TPR = TP / (TP + FN) - "How many positives did we correctly find?"
- Each point on the curve corresponds to a different decision threshold

**AUC (Area Under the ROC Curve)**:
- AUC = 1.0: Perfect classifier
- AUC = 0.5: Random classifier (diagonal line)
- AUC < 0.5: Worse than random (invert predictions)

**Interpretation**: AUC = probability that a randomly chosen positive example is scored higher than a randomly chosen negative example.

**When to use**: Binary classification, especially when you want a threshold-independent metric.

**When NOT to use**: Heavily imbalanced datasets (ROC can be misleadingly optimistic). Use Precision-Recall AUC instead when the positive class is rare (<5%).

---

## 15. Handling class imbalance

When one class vastly outnumbers the other (e.g., 99% negative, 1% positive).

**Data-level approaches**:
- **Oversampling minority class**: SMOTE (creates synthetic minority samples by interpolating between neighbors)
- **Undersampling majority class**: Random or Tomek links (remove majority samples close to decision boundary)
- **Combination**: SMOTE + Tomek links

**Algorithm-level approaches**:
- **Class weights**: Set `class_weight='balanced'` in scikit-learn. Increases loss for minority class errors.
- **Cost-sensitive learning**: Assign higher misclassification cost to minority class
- **Threshold tuning**: Instead of 0.5, choose threshold that maximizes F1 or business metric

**Ensemble approaches**:
- **Balanced Random Forest**: Undersample each bootstrap sample
- **EasyEnsemble**: Train multiple classifiers on different undersampled subsets

**Evaluation**: Never use accuracy for imbalanced data (99% accuracy by predicting all negative). Use F1, Precision-Recall AUC, or Matthews Correlation Coefficient.

---

## 16. Feature selection methods

Choosing the most relevant features to improve model performance and reduce complexity.

**Filter Methods** (independent of model):
- Correlation with target (Pearson, Spearman)
- Chi-squared test (categorical features)
- Mutual information
- Variance threshold (remove near-constant features)
- *Pros*: Fast, scalable. *Cons*: Ignores feature interactions.

**Wrapper Methods** (use model performance):
- Forward selection: Start empty, add best feature iteratively
- Backward elimination: Start with all, remove worst iteratively
- Recursive Feature Elimination (RFE): Train model, remove least important, repeat
- *Pros*: Considers feature interactions. *Cons*: Computationally expensive.

**Embedded Methods** (built into model training):
- L1 regularization (Lasso): Drives irrelevant feature weights to zero
- Tree feature importance: Based on information gain or impurity decrease
- *Pros*: Efficient, considers interactions. *Cons*: Model-specific.

**Practical approach**: Start with variance threshold and correlation analysis (filter), then use tree-based importance or L1 (embedded), then RFE for final selection if needed.

---

## 17. Curse of dimensionality

As the number of features (dimensions) increases, several problems emerge:

**Core problems**:
1. **Data sparsity**: In high dimensions, data points become equidistant from each other. A cube needs exponentially more points to maintain the same density (10 points per dimension = 10^d total).
2. **Distance concentration**: All pairwise distances converge to the same value, making distance-based methods (KNN, K-means, SVM) unreliable.
3. **Overfitting risk**: More features = more parameters to fit = easier to memorize training data.
4. **Computational cost**: Training time and memory grow with dimensionality.

**Rule of thumb**: You need at least 5-10 training samples per dimension for reliable statistical estimation (some say 10-20x).

**Solutions**:
- Feature selection (keep only relevant features)
- Dimensionality reduction (PCA, t-SNE, autoencoders)
- Regularization (penalize model complexity)
- Domain knowledge (engineer fewer, better features)

---

## 18. Batch normalization explained

Batch norm normalizes the inputs to each layer during training to stabilize and accelerate learning.

**How it works** (for each mini-batch):
1. Compute mean and variance of activations across the batch
2. Normalize: `x_hat = (x - mean) / sqrt(variance + epsilon)`
3. Scale and shift: `y = gamma * x_hat + beta` (learned parameters)

**Why it helps**:
- **Reduces internal covariate shift**: Each layer's input distribution stays stable even as earlier layers change
- **Allows higher learning rates**: Normalized inputs prevent gradients from exploding/vanishing
- **Acts as regularization**: Mini-batch statistics add noise, similar to dropout
- **Speeds up convergence**: Often 5-10x faster training

**During inference**: Uses running averages of mean and variance computed during training (not batch statistics).

**Placement debate**: Originally proposed after linear layer, before activation. Some practitioners prefer after activation. Both work; experiment.

**Alternatives**: Layer Norm (used in transformers, normalizes across features), Group Norm (useful for small batch sizes), Instance Norm (used in style transfer).

---

## 19. Dropout explained

Dropout is a regularization technique that randomly "drops" (zeroes out) neurons during training.

**How it works**:
- During **training**: Each neuron is set to zero with probability p (typically 0.1-0.5) at each forward pass. Remaining neurons are scaled by 1/(1-p) to maintain expected values.
- During **inference**: All neurons are active. No dropout applied. (Scaling during training with "inverted dropout" means no change needed at inference.)

**Why it works**:
- **Prevents co-adaptation**: Neurons cannot rely on specific other neurons being present, so each learns more robust features
- **Implicit ensemble**: Each training step uses a different sub-network. At inference, you're averaging predictions of ~2^n sub-networks
- **Reduces overfitting**: Equivalent to adding noise to the network, acts as regularization

**Practical tips**:
- Common rates: 0.2-0.5 for hidden layers, 0.1-0.2 for input layer
- Higher dropout = stronger regularization (but too high = underfitting)
- Often not used with batch normalization (both add noise; combining can hurt)
- Used less in convolutional layers (spatial dropout instead)

---

## 20. Learning rate scheduling

The learning rate controls the step size during gradient descent. Scheduling adjusts it during training for better convergence.

**Common schedules**:

| Schedule | Description | Use case |
|----------|-------------|----------|
| **Constant** | Fixed LR throughout | Simple baselines |
| **Step decay** | Reduce by factor every N epochs | Classic CNN training |
| **Exponential decay** | LR = LR0 * decay^epoch | Smooth continuous reduction |
| **Cosine annealing** | LR follows cosine curve from max to min | Transformers, modern DL |
| **Warmup + decay** | Linear increase for N steps, then decay | Transformer training (Adam is unstable early) |
| **ReduceLROnPlateau** | Reduce when validation metric stops improving | When you don't know the optimal schedule |
| **Cyclical LR** | Oscillate between min and max LR | Escaping local minima, super-convergence |
| **One-cycle** | Warmup to max, then anneal to near-zero | Fast convergence (Leslie Smith) |

**Practical guidance**:
- **Transformers**: Warmup (5-10% of steps) + cosine decay is standard
- **CNNs**: Step decay or cosine annealing
- **Finding initial LR**: Use learning rate finder (train for one epoch with exponentially increasing LR, plot loss, pick the LR where loss decreases fastest)
- **AdamW + cosine schedule** is a strong default for most deep learning tasks
