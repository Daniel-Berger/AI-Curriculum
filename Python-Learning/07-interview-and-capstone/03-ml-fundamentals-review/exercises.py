"""
Rapid-fire ML Fundamentals Review Exercises

15 questions covering ALL 7 phases of the curriculum.
These are conceptual and practical questions for quick review.
"""

from typing import List, Dict, Tuple, Any, Optional


# ============================================================================
# Phase 1-2: Python & NumPy (2 questions)
# ============================================================================

def exercise_1_python_gotchas() -> Dict[str, Any]:
    """
    Identify and fix 3 common Python mistakes:

    1. Mutable default arguments:
       def bad(x, items=[]):  # DON'T: shared across calls
           items.append(x)

       def good(x, items=None):  # DO: create new each time
           if items is None:
               items = []

    2. Late binding in closures:
       funcs = [lambda x: x+i for i in range(3)]  # all use same 'i'
       funcs[0](1)  # returns 3, not 1 (i=2 at closure time)

       Fix: funcs = [lambda x, j=i: x+j for i in range(3)]

    3. Integer division:
       1/2 = 0.5 (true division in Python 3)
       1//2 = 0 (floor division)
       -1//2 = -1 (floors toward negative infinity)

    Return: Dict with keys "mutable_defaults", "closures", "division"
    Each key has a brief explanation (string).
    """
    pass


def exercise_2_numpy_vectorization() -> float:
    """
    Why is NumPy vectorization fast?

    Given 1 million numbers, compute sum of squares.

    Slow (Python loop):
        result = 0
        for x in arr:
            result += x**2

    Fast (NumPy):
        result = np.sum(arr**2)

    Reason: NumPy uses C under the hood, operates on contiguous memory,
    no Python interpreter overhead per operation.

    Trade-off: NumPy can't JIT-compile closures or complex Python logic.

    Return: Speedup factor (estimate as float, e.g., 100.0 for 100x faster)
    """
    pass


# ============================================================================
# Phase 3: Pandas (2 questions)
# ============================================================================

def exercise_3_groupby_aggregation() -> Dict[str, Any]:
    """
    When would you use groupby vs pivot vs merge?

    groupby:
        - Aggregate by groups (mean, sum, custom function)
        - Returns Series or DataFrame
        - Can handle multiple aggregations per column

    pivot:
        - Reshape long→wide
        - One value per index/column combo
        - Fails on duplicates

    pivot_table:
        - Like pivot but with aggregation for duplicates
        - Specify how='mean' etc.

    merge:
        - Join on common key
        - inner/left/right/outer

    Scenario: You have sales data with [date, product, region, amount].
    What operation would you use for:

    A) Total sales by product → groupby product, sum amount
    B) Wide table with products as columns, regions as rows → pivot_table
    C) Combine with employee data on region → merge

    Return: Dict with keys "groupby_use", "pivot_use", "merge_use"
    Each value is string explanation.
    """
    pass


def exercise_4_handling_missing_data() -> Dict[str, str]:
    """
    Strategy for missing data depends on context.

    Options:
    1. Drop: df.dropna() - removes rows with any NaN
       Use: If few missing (<5%)

    2. Fill forward: df.fillna(method='ffill') - carry last value
       Use: Time series where continuity makes sense

    3. Fill with value: df.fillna(0) or df.fillna(df.mean())
       Use: Zero makes sense (e.g., no sales), or impute with column mean

    4. Interpolation: df.interpolate() - linear fit between known values
       Use: Time series, continuous data

    5. Advanced: KNN imputation, MICE, learned imputation
       Use: Complex missing pattern, high-impact column

    Given:
    - Time series with temperature readings, 2% missing
    - Categorical survey response, 30% missing
    - Income column, 5% missing

    Choose strategy for each.

    Return: Dict with keys: "time_series", "categorical", "income"
    Values: name of strategy (e.g., "interpolation")
    """
    pass


# ============================================================================
# Phase 4: ML Algorithms (4 questions)
# ============================================================================

def exercise_5_bias_variance_tradeoff() -> Dict[str, float]:
    """
    Understand bias-variance and overfitting/underfitting.

    Bias: Error from wrong assumptions
    - High bias: model too simple, misses patterns
    - Underfitting: high bias, high variance (unstable on small data)

    Variance: Error from high sensitivity to training data
    - High variance: model too complex, memorizes noise
    - Overfitting: low bias, high variance (great on train, poor on test)

    Total Error = Bias² + Variance + Irreducible Error

    Trade-off: Often can't reduce both. Increase complexity → lower bias,
    higher variance. Regularize (L1/L2, dropout) → lower variance, slightly higher bias.

    Given training/test accuracy:

    Model A: train=99.5%, test=50% → Overfitting (high variance)
    Model B: train=60%, test=60% → Underfitting (high bias)
    Model C: train=95%, test=92% → Good (balanced)

    Return: Dict with keys "bias", "variance" for Model A
    Values: "high" or "low"
    """
    pass


def exercise_6_classification_metrics() -> str:
    """
    Which metric matters for different problems?

    Accuracy: (TP+TN)/Total
    - Use ONLY if balanced classes
    - Misleading for imbalanced data

    Precision: TP/(TP+FP) - "of predicted positives, how many correct?"
    - Use: When false alarms are costly (spam filter, medical alert)
    - Optimize: Increase decision threshold

    Recall: TP/(TP+FN) - "of actual positives, how many caught?"
    - Use: When missing positive is costly (cancer detection, fraud)
    - Optimize: Lower decision threshold

    F1: 2*(P*R)/(P+R) - Harmonic mean of P and R
    - Use: When you care about both precision and recall equally

    ROC-AUC: Area under curve
    - Threshold-independent, good for comparing models
    - Use: When you don't know the decision threshold yet

    Scenario: Fraud detection (fraud rate 0.1%)
    What metric would you optimize and why?

    Return: String, one of ["precision", "recall", "f1", "roc_auc", "accuracy"]
    """
    pass


def exercise_7_regularization_techniques() -> Dict[str, str]:
    """
    How to prevent overfitting?

    Regularization adds penalty to loss to prevent overfitting.

    L1 (Lasso): λ * Σ|w|
    - Drives some weights to exactly 0
    - Feature selection
    - Use: High-dimensional, want to identify important features

    L2 (Ridge): λ * Σw²
    - Shrinks all weights, none to 0
    - More stable numerically
    - Use: Default choice, computational stability

    Early Stopping:
    - Stop training when validation loss plateaus
    - Use: Neural networks
    - Prevents learning noise

    Dropout:
    - Randomly zero activations during training
    - Use: Neural networks, prevents co-adaptation
    - Rate: typically 0.2-0.5

    Data Augmentation:
    - Create synthetic examples (rotate images, synonym replacement)
    - Use: When data is limited

    Cross-Validation:
    - Multiple train/test splits
    - Use: Tune hyperparameters, estimate performance

    Scenario: Your neural network overfits after 20 epochs.
    Three techniques would help. Which and why?

    Return: Dict with 2 keys: "technique_1" and "why_1" (and "_2", "_3")
    """
    pass


def exercise_8_unsupervised_clustering() -> Dict[str, str]:
    """
    When would you use K-Means vs DBSCAN vs Hierarchical?

    K-Means:
    - Assumes spherical, similar-sized clusters
    - Fast, O(n*k*d*i)
    - Need to specify k
    - Use: Quick exploratory, known k
    - Pros: simple, fast
    - Cons: sensitive to init, non-spherical clusters, k must be known

    DBSCAN:
    - Density-based, finds arbitrary shapes
    - No k needed, specify ε and min_pts
    - Robust to outliers (labels as noise)
    - Use: Unknown k, non-spherical, outlier detection
    - Pros: no k, outliers, any shape
    - Cons: sensitive to ε, slow for high-d

    Hierarchical:
    - Builds tree of clusters (dendrogram)
    - Choose cutoff level for clusters
    - Can use different linkage (single, complete, average, Ward)
    - Use: When hierarchy is meaningful, want to explore structure
    - Pros: interpretable, hierarchy
    - Cons: slow O(n²), can't reassign points

    Scenario 1: Cluster customer segments, expect 5-7 clusters
    Scenario 2: Detect outliers in sensor data, don't know cluster count
    Scenario 3: Understand taxonomy of species, want hierarchy

    Return: Dict with keys "scenario_1", "scenario_2", "scenario_3"
    Values: algorithm name
    """
    pass


# ============================================================================
# Phase 5: Deep Learning (3 questions)
# ============================================================================

def exercise_9_neural_network_architecture() -> Dict[str, int]:
    """
    Design a neural network for image classification (MNIST).

    Input: 28x28 grayscale images (784 features)
    Output: 10 classes (digits 0-9)

    Architecture considerations:

    Convolutional layers:
    - Extract spatial features
    - Filters: 32, 64, 128 (increasing depth)
    - Kernel: 3x3 typical

    Pooling:
    - Reduce spatial dimensions
    - Max pooling 2x2

    Dense layers:
    - Flatten after convolutions
    - Dense 128 → ReLU
    - Output 10 → softmax

    Regularization:
    - BatchNorm: after Conv or Dense
    - Dropout: 0.25-0.5 before Dense

    Training:
    - Optimizer: Adam (default)
    - Loss: categorical_crossentropy
    - Epochs: 10-20 typically

    Return: Dict with estimated counts
    Keys: "conv_filters_layer1", "dense_neurons", "total_params_millions"
    Values: integers (e.g., 32, 128, 2)
    """
    pass


def exercise_10_backpropagation_flow() -> str:
    """
    Explain how gradients flow backward through a simple network.

    Forward pass:
        x → [Linear] → z1 → [ReLU] → a1 → [Linear] → z2 → [Softmax] → ŷ
        Loss L computed at output

    Backward pass (chain rule):
        dL/dw2 = (dL/dz2) * (dz2/dw2)
        dL/dz2 = (dL/dŷ) * (dŷ/dz2)  # softmax derivative
        dL/dz1 = (dL/da1) * (da1/dz1) * (dz1/dw1)  # ReLU passes gradient
        dL/dw1 = (dL/dz1) * (dz1/dw1)

    Key points:
    - Gradients flow backward through loss → output → hidden → input
    - Each layer's derivative is multiplied
    - ReLU: gradient = 1 if z > 0, else 0
    - Vanishing gradient: gradients → 0 through many layers
    - Exploding gradient: gradients → ∞, cause NaN

    Problem: What happens if all layers have ReLU?
    - Gradient stays 1 or 0 → stable (good!)
    - But 0 gradient kills learning in inactive neurons (dead ReLU)

    Solution: Use different activations, leaky ReLU, layer norm, gradient clipping

    Return: String explanation of the issue and solution (100-200 chars)
    """
    pass


def exercise_11_transformer_attention() -> Dict[str, str]:
    """
    How does self-attention work in transformers?

    Self-Attention mechanism:

    Input: Sequence of embeddings X (n tokens × d dimensions)

    Project to Q, K, V:
        Q = X * W_Q  (n × d_k)
        K = X * W_K  (n × d_k)
        V = X * d_v  (n × d_v)

    Compute attention scores:
        scores = Q * K^T / sqrt(d_k)  (n × n)
        weights = softmax(scores)  (n × n)

    Weighted sum of values:
        output = weights * V  (n × d_v)

    Intuition:
    - Query: "What am I looking for?"
    - Key: "What can I offer?" (from other tokens)
    - Value: "What info do I have?"
    - Attention: matches query to keys, retrieves values

    Multi-head: Apply this multiple times with different W_Q, W_K, W_V
    - Enables attending to different aspects in parallel
    - Final: concatenate and project

    Complexity: O(n²) in sequence length (can be bottleneck)

    Scenario: Processing "The cat sat on the mat"
    When processing "cat", what does it attend to?
    - High attention to "sat" (verb, predicate)
    - Some to "mat" (object location)
    - Less to "the" (article, less info)

    Return: Dict with keys:
    "complexity": "O(n²)" or "O(n)" or "O(n log n)"
    "strength": brief string why attention is powerful
    """
    pass


# ============================================================================
# Phase 6: LLMs (2 questions)
# ============================================================================

def exercise_12_token_economics() -> Dict[str, Any]:
    """
    Understand token accounting in LLMs.

    1 token ≈ 4 characters or 0.75 words

    Token counts:
    - "Hello, world!" → ~3 tokens
    - 1 page of text (~400 words) → ~550 tokens
    - 1 million tokens → ~750,000 words → ~4 books

    Pricing (OpenAI GPT-4 example):
    - Input: $0.03 per 1K tokens
    - Output: $0.06 per 1K tokens

    Context window:
    - GPT-3.5: 4K or 16K tokens
    - GPT-4: 8K or 128K tokens
    - Claude: up to 200K tokens

    Cost implications:
    - Longer context window = higher token count = higher cost
    - Output more expensive (2x input in GPT-4)
    - Few-shot examples (prompt) count as input tokens

    Scenario: You want to answer questions about a 100-page document.

    Option A: RAG - retrieve relevant pages, pass 5 pages per query
    - Query: 500 tokens, context: 5 pages (~2750 tokens), output: ~200 tokens
    - Cost per query: (500 + 2750) * $0.03/1K + 200 * $0.06/1K = ~$0.12

    Option B: Fine-tune on full document (offline)
    - One-time cost: ~$5-50 depending on size
    - Query: Just question (50 tokens) + output (200 tokens)
    - Cost per query: 50 * $0.03/1K + 200 * $0.06/1K = ~$0.015

    Which is better? Depends on query volume.

    Return: Dict with keys:
    "tokens_per_word": float (e.g., 0.75)
    "cheaper_for_high_volume": str ("fine_tune" or "rag")
    """
    pass


def exercise_13_prompting_strategies() -> Dict[str, str]:
    """
    When to use different prompting techniques?

    Zero-shot:
    - "Classify: I love this movie!" → Sentiment?
    - Use: Well-understood task, general capability
    - Pros: No examples needed
    - Cons: Can be inconsistent

    Few-shot:
    - Example 1: "Great film!" → Positive
    - Example 2: "Boring." → Negative
    - Query: "Mediocre" → ?
    - Use: Improve consistency, define format/style
    - Pros: Few examples set task definition
    - Cons: Takes tokens, may overfit to examples

    Chain-of-Thought (CoT):
    - "Let's think step by step. First..."
    - Use: Complex reasoning, multi-step problems
    - Pros: Better accuracy on reasoning tasks
    - Cons: Longer response, more tokens

    Retrieval-Augmented Generation (RAG):
    - Query → Retrieve docs → Pass as context → Generate
    - Use: Domain-specific knowledge, current facts
    - Pros: Grounds in real data, updatable
    - Cons: Retrieval quality crucial, more complex

    Fine-tuning:
    - Train on task examples
    - Use: Consistent outputs, specific format, cost reduction
    - Pros: Reliable, cheaper per token
    - Cons: Requires labeled data, one-time cost

    Scenario 1: Classify news articles by topic (1000 per day, varied topics)
    Scenario 2: Answer questions about a specific company's internal docs
    Scenario 3: Write creative poetry in a specific style
    Scenario 4: Solve complex math word problems

    Return: Dict with scenario keys, values are technique names
    """
    pass


# ============================================================================
# Phase 7: Production & Advanced (2 questions)
# ============================================================================

def exercise_14_experiment_tracking() -> Dict[str, str]:
    """
    Why track experiments and how?

    Experiment: Train model variant and evaluate
    - Different architecture, hyperparams, dataset, preprocessing

    Tracking captures:
    - Model architecture
    - Hyperparameters
    - Training data version
    - Metrics (train/val loss, accuracy)
    - Training time, RAM usage
    - Model artifact (weights file)

    Tools:
    - MLflow: log params, metrics, models, artifacts
    - Weights & Biases: cloud-native, visualizations
    - Neptune: experiment management
    - Custom: database + artifact storage

    Why:
    - Reproducibility: which params led to best model?
    - Comparison: A/B test models
    - Debugging: what changed when performance dropped?
    - Deployment: know exact version of code/data/model
    - Compliance: audit trail for regulated industries

    Minimal tracking:
    ```python
    import mlflow
    mlflow.set_experiment("my_experiment")
    with mlflow.start_run():
        mlflow.log_param("learning_rate", 0.001)
        mlflow.log_metric("accuracy", 0.95)
        mlflow.log_model(model, "model")
    ```

    Scenario: Your model accuracy drops from 95% to 90% in production.
    How would you debug?

    Return: Dict with keys:
    "check_1": what to check first
    "check_2": what to check second
    "prevention": how to prevent in future
    """
    pass


def exercise_15_model_deployment_considerations() -> Dict[str, str]:
    """
    What matters when deploying models to production?

    Latency:
    - API response time must be acceptable
    - Model inference time + preprocessing + network
    - Trade-off: accuracy vs speed (simpler model may be faster)

    Throughput:
    - Queries per second the system handles
    - Batch processing faster but higher latency
    - Load balancing, autoscaling

    Monitoring:
    - Accuracy drift: does model still perform?
    - Data drift: input distribution changed?
    - System: latency, error rate, resource usage
    - Set alerts for degradation

    Serving options:
    - REST API (Flask, FastAPI): flexible, easy to update
    - Model server (TensorFlow Serving, MLflow): optimized
    - Batch: scheduled jobs, offline predictions
    - Edge: model runs on device (mobile), lower latency

    Testing:
    - Unit tests: preprocessing, postprocessing
    - Integration tests: API endpoints
    - Canary: serve new model to 1% traffic first
    - Shadow: run new model in parallel, log but don't serve

    Versioning:
    - Model versioning: v1, v2, v3
    - Ability to rollback to old model if new is bad
    - Store in artifact registry with metadata

    Scenario: Deploy new recommendation model
    - Current model handles 10K req/sec
    - New model 5% more accurate but 2x slower
    - High-value users (VIP) should get best accuracy

    Strategy?

    Return: Dict with keys:
    "serve_model_to": percentage or "all_users"
    "optimization": what to optimize for
    "rollback_plan": what to do if new model fails
    """
    pass


# ============================================================================
# Test
# ============================================================================

if __name__ == "__main__":
    print("15 Rapid-fire ML review exercises")
    print("\nCategories:")
    print("  1-2: Python & NumPy")
    print("  3-4: Pandas")
    print("  5-8: ML Algorithms")
    print("  9-11: Deep Learning")
    print("  12-13: LLMs")
    print("  14-15: Production & Advanced")
    print("\nImplement each exercise and test understanding!")
