"""
Solutions to Rapid-fire ML Fundamentals Review

Concise answers with explanations.
"""

from typing import Dict, List, Tuple, Any, Optional


def solution_1_python_gotchas() -> Dict[str, Any]:
    """
    Three common Python mistakes and fixes.
    """
    return {
        "mutable_defaults": (
            "Don't use mutable defaults (list, dict, set). "
            "They're shared across all function calls. "
            "Instead: use None and create new inside function."
        ),
        "closures": (
            "Closures capture variable name, not value. "
            "Late binding: functions reference the variable at call time. "
            "Fix: Use default argument closure=i to capture current value."
        ),
        "division": (
            "Python 3: / is true division (returns float), "
            "// is floor division (rounds down). "
            "-1//2 = -1 (floors toward negative infinity, not toward 0)."
        )
    }


def solution_2_numpy_vectorization() -> float:
    """
    NumPy is ~100-1000x faster than Python loops for large arrays.

    Reasons:
    - C-level implementation (no interpreter overhead)
    - Contiguous memory access (cache-friendly)
    - SIMD instructions (process multiple elements at once)
    - No type checking per element

    For 1M elements: Pure Python ~100ms, NumPy ~0.1-1ms = 100-1000x speedup
    """
    return 100.0  # Typical 100x speedup for vectorized operations


def solution_3_groupby_aggregation() -> Dict[str, Any]:
    """
    Different tools for different reshaping tasks.
    """
    return {
        "groupby_use": "Use groupby to aggregate: df.groupby('product')['amount'].sum()",
        "pivot_use": (
            "Use pivot_table to reshape long→wide: "
            "df.pivot_table(index='region', columns='product', values='amount', aggfunc='sum')"
        ),
        "merge_use": (
            "Use merge to join on key: "
            "pd.merge(sales, employees, on='region', how='left')"
        )
    }


def solution_4_handling_missing_data() -> Dict[str, str]:
    """
    Choose missing data strategy by context.
    """
    return {
        "time_series": "interpolation",  # Linear interpolation between timestamps
        "categorical": "drop",  # 30% missing = drop rows with NaN
        "income": "fillna(mean)"  # 5% missing = fill with column mean
    }


def solution_5_bias_variance_tradeoff() -> Dict[str, float]:
    """
    Model A has huge gap between train and test = overfitting = high variance, low bias
    """
    return {
        "bias": "low",      # Model fits train data well (low bias)
        "variance": "high"  # Poor generalization = high variance
    }


def solution_6_classification_metrics() -> str:
    """
    Fraud detection: fraud rate 0.1% (highly imbalanced)

    Accuracy: If model predicts "no fraud" for all → 99.9% accurate! Useless.

    Precision: Of fraud alerts, how many are real? (false alarm cost)
    Recall: Of real frauds, how many caught? (miss cost)

    In fraud: missing fraud is very expensive (financial loss).
    So optimize for Recall. Accept more false alarms to catch frauds.

    Practical: Use Recall but check Precision too.
    Better: ROC-AUC (threshold-independent) to compare models.
    """
    return "recall"  # Catch frauds > false alarms


def solution_7_regularization_techniques() -> Dict[str, str]:
    """
    Network overfits after 20 epochs: three techniques
    """
    return {
        "technique_1": "early_stopping",
        "why_1": "Stop training when validation loss plateaus, prevents memorizing noise",

        "technique_2": "dropout",
        "why_2": "Randomly zero activations, prevents co-adaptation of neurons",

        "technique_3": "l2_regularization",
        "why_3": "Add penalty term λ*Σw² to loss, shrink weights toward zero"
    }


def solution_8_unsupervised_clustering() -> Dict[str, str]:
    """
    Choose clustering algorithm by scenario.
    """
    return {
        "scenario_1": "kmeans",        # 5-7 clusters, expected count
        "scenario_2": "dbscan",        # Unknown k, outlier detection
        "scenario_3": "hierarchical"   # Taxonomy, want hierarchy
    }


def solution_9_neural_network_architecture() -> Dict[str, int]:
    """
    Rough MNIST architecture estimate.
    """
    return {
        "conv_filters_layer1": 32,      # Start with 32 filters
        "dense_neurons": 128,           # Hidden dense layer
        "total_params_millions": 1      # Small network ~1M params
    }


def solution_10_backpropagation_flow() -> str:
    """
    Issue and solution for ReLU networks.
    """
    return (
        "Dead ReLU: neurons with z<=0 have gradient 0, stop learning. "
        "Solution: Leaky ReLU (returns αx for x<0), layer normalization, or proper initialization."
    )


def solution_11_transformer_attention() -> Dict[str, str]:
    """
    Self-attention mechanics and complexity.
    """
    return {
        "complexity": "O(n²)",
        "strength": (
            "Attention learns long-range dependencies in one step. "
            "Unlike RNN that needs many steps → can parallelize training. "
            "Flexible weighting: different heads attend to different aspects."
        )
    }


def solution_12_token_economics() -> Dict[str, Any]:
    """
    Token accounting and cost-benefit analysis.
    """
    return {
        "tokens_per_word": 0.75,
        "cheaper_for_high_volume": "fine_tune"  # If many queries, fine-tune wins on cost
    }


def solution_13_prompting_strategies() -> Dict[str, str]:
    """
    Choose prompting strategy by use case.
    """
    return {
        "scenario_1": "few_shot",       # Consistency, clear examples
        "scenario_2": "rag",            # Domain-specific knowledge
        "scenario_3": "fine_tune",      # Consistent style/format
        "scenario_4": "chain_of_thought"  # Complex reasoning
    }


def solution_14_experiment_tracking() -> Dict[str, str]:
    """
    Debug performance drop: systematic approach.
    """
    return {
        "check_1": "data_drift",
        "why_1": "Input distribution may have changed. Check data statistics, outliers.",

        "check_2": "model_version",
        "why_2": "Confirm you're running the right model. Look at commit hash, experiment logs.",

        "check_3": "preprocessing",
        "why_3": "Features may have changed (scaling, encoding). Verify preprocessing matches training.",

        "prevention": (
            "Track all experiments (MLflow, W&B): log hyperparams, metrics, data version, code commit. "
            "Monitor in production: log predictions, actuals, metrics. Alert on drift. "
            "Canary deploy: new models to 1% traffic first."
        )
    }


def solution_15_model_deployment_considerations() -> Dict[str, str]:
    """
    Deploy new recommendation model (5% more accurate, 2x slower).
    """
    return {
        "serve_model_to": "vip_users_only",
        "why": "New model 5% better but 2x slower. Trade accuracy for latency. VIPs get better experience.",

        "optimization": "latency_and_accuracy_balance",
        "how": (
            "Serve new model to 10-20% VIP traffic (canary). "
            "Monitor latency: if acceptable, expand. If not, optimize (quantization, distillation) or revert."
        ),

        "rollback_plan": (
            "Keep old model running in parallel. "
            "If new model latency exceeds SLA or accuracy degrades in production, "
            "switch traffic back within 5 minutes. Log all metrics for post-mortem."
        )
    }


# ============================================================================
# Quick Reference Formulas
# ============================================================================

QUICK_FORMULAS = {
    "Linear Regression Loss": "MSE = (1/n) * Σ(y_i - ŷ_i)²",

    "Logistic Regression": "P(Y=1|X) = 1 / (1 + e^(-wx))",

    "Cross Entropy": "-[y*log(ŷ) + (1-y)*log(1-ŷ)]",

    "Information Gain": "IG = H(parent) - Σ(|child|/|parent|)*H(child)",

    "Entropy": "H = -Σ p_i * log2(p_i)",

    "Precision": "TP / (TP + FP)",

    "Recall": "TP / (TP + FN)",

    "F1": "2 * (P*R) / (P+R)",

    "ROC-AUC": "Area under curve(TPR vs FPR)",

    "Cosine Similarity": "(A·B) / (||A||*||B||)",

    "KL Divergence": "Σ p_i * log(p_i / q_i)",

    "Softmax": "e^(z_i) / Σ e^(z_j)",

    "Attention": "softmax(Q*K^T / sqrt(d_k)) * V",

    "RMSE": "sqrt((1/n) * Σ(y_i - ŷ_i)²)",

    "R²": "1 - (SS_res / SS_tot)",

    "Gini": "1 - Σ p_i²",
}


# ============================================================================
# Algorithm Decision Tree
# ============================================================================

ALGORITHM_GUIDE = """
QUICK ALGORITHM GUIDE:

Regression (continuous Y):
├─ Linear? → Linear Regression (MSE)
├─ Need interpretability? → Decision Tree
└─ Nonlinear, complex? → Gradient Boosting (XGBoost)

Classification (categorical Y):
├─ Binary, probability? → Logistic Regression
├─ Fast, interpretable? → Decision Tree
├─ High-dim (text/features)? → Linear SVM or Naive Bayes
├─ Mixed features, nonlinear? → Random Forest
└─ Complex patterns? → Neural Network

Unsupervised Clustering:
├─ k known, spherical? → K-Means
├─ k unknown, any shape? → DBSCAN
├─ Hierarchy needed? → Hierarchical
└─ Soft assignments? → Gaussian Mixture Model

Dimensionality Reduction:
├─ Linear, interpretable? → PCA
├─ Visualization? → t-SNE or UMAP
└─ Nonlinear, complex? → Autoencoder

Sequence/Time Series:
├─ Recent history important? → LSTM/GRU
├─ Long-range dependencies? → Transformer
└─ Simple trend? → ARIMA or exponential smoothing

Text/NLP:
├─ Classification? → TF-IDF + SVM or Neural Network
├─ Generate text? → RNN/LSTM or Transformer (LLM)
├─ Understand text? → BERT or other encoder
└─ Question answering? → Transformer + RAG

Recommendation:
├─ Collaborative filtering? → Matrix Factorization
├─ Content-based? → Similarity matching
└─ Cold start, complex? → Neural Collaborative Filtering
"""


if __name__ == "__main__":
    print("ML Fundamentals Review Solutions")
    print("\n" + "="*60)
    print("QUICK FORMULAS")
    print("="*60)
    for name, formula in QUICK_FORMULAS.items():
        print(f"{name:.<40} {formula}")

    print("\n" + "="*60)
    print(ALGORITHM_GUIDE)
    print("="*60)

    print("\nAll 15 solutions and quick references ready!")
