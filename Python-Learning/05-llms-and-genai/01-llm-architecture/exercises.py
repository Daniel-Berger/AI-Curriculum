"""
Module 01: LLM Architecture — Exercises
========================================

12 exercises covering LLM architecture concepts: parameter counting,
compute estimation, scaling laws, and conceptual understanding.

These exercises are conceptual — they test your understanding of how
LLMs are built and trained through calculations and knowledge questions.

Run this file directly to check your solutions:
    python exercises.py

Each exercise has assert-based tests that verify correctness.
"""

import math


# ---------------------------------------------------------------------------
# Exercise 1: Transformer Parameter Counting
# ---------------------------------------------------------------------------
def count_transformer_params(
    d_model: int,
    n_layers: int,
    vocab_size: int,
    d_ff_multiplier: int = 4,
) -> dict[str, int]:
    """
    Calculate the number of parameters in a decoder-only transformer.

    For each transformer layer:
    - Self-attention: 4 * d_model^2  (Q, K, V, Output projections, no bias)
    - Feed-forward: 2 * d_model * d_ff  where d_ff = d_ff_multiplier * d_model
    - Layer norms: 2 * d_model  (two layer norms per block, each with d_model params)

    Additionally:
    - Token embeddings: vocab_size * d_model
    - Final layer norm: d_model

    Assume NO bias terms and NO separate output projection (weight tying with
    embeddings, so the output projection shares weights with the embedding layer).

    Args:
        d_model: Model dimension (hidden size)
        n_layers: Number of transformer layers
        vocab_size: Vocabulary size
        d_ff_multiplier: FFN hidden dimension multiplier (default 4)

    Returns:
        Dictionary with keys:
        - 'attention_per_layer': params in self-attention per layer
        - 'ffn_per_layer': params in feed-forward per layer
        - 'norm_per_layer': params in layer norms per layer
        - 'embedding': params in token embedding
        - 'total_per_layer': total params per layer
        - 'total': total model parameters
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Memory Requirements
# ---------------------------------------------------------------------------
def estimate_memory_gb(
    num_params: int,
    precision: str,
) -> float:
    """
    Estimate the memory required to load a model in different precisions.

    Precision options:
    - 'fp32': 4 bytes per parameter
    - 'fp16' or 'bf16': 2 bytes per parameter
    - 'int8': 1 byte per parameter
    - 'int4': 0.5 bytes per parameter

    Args:
        num_params: Number of model parameters
        precision: One of 'fp32', 'fp16', 'bf16', 'int8', 'int4'

    Returns:
        Memory in gigabytes (float), rounded to 2 decimal places
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Compute Estimation (FLOPs)
# ---------------------------------------------------------------------------
def estimate_training_flops(
    num_params: int,
    num_tokens: int,
) -> float:
    """
    Estimate the total floating point operations for training using the
    approximation: FLOPs ≈ 6 * N * D

    Where N = number of parameters, D = number of training tokens.
    The factor of 6 accounts for forward pass (2 * N * D) and
    backward pass (4 * N * D).

    Args:
        num_params: Number of model parameters
        num_tokens: Number of training tokens

    Returns:
        Estimated FLOPs as a float
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Training Time Estimation
# ---------------------------------------------------------------------------
def estimate_training_days(
    total_flops: float,
    num_gpus: int,
    gpu_tflops: float,
    utilization: float = 0.3,
) -> float:
    """
    Estimate training time in days given compute requirements.

    GPU utilization (MFU — Model FLOPS Utilization) accounts for
    communication overhead, memory operations, etc. Typical values
    are 0.3-0.5 for large training runs.

    Args:
        total_flops: Total FLOPs required for training
        num_gpus: Number of GPUs
        gpu_tflops: Peak TFLOPS per GPU (e.g., 312 for A100)
        utilization: Model FLOPS Utilization factor (default 0.3)

    Returns:
        Estimated training time in days, rounded to 1 decimal place
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Chinchilla Optimal Tokens
# ---------------------------------------------------------------------------
def chinchilla_optimal(
    num_params: int,
) -> dict[str, float]:
    """
    Calculate the Chinchilla-optimal number of training tokens and the
    approximate compute budget.

    Chinchilla ratio: approximately 20 tokens per parameter.

    Args:
        num_params: Number of model parameters

    Returns:
        Dictionary with:
        - 'optimal_tokens': Chinchilla-optimal number of training tokens
        - 'optimal_flops': Estimated FLOPs (using 6 * N * D)
        - 'tokens_per_param': The ratio (should be 20)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Actual vs. Optimal Training Analysis
# ---------------------------------------------------------------------------
def analyze_training_efficiency(
    model_name: str,
    num_params: int,
    actual_tokens: int,
) -> dict[str, object]:
    """
    Analyze whether a model was over-trained or under-trained relative
    to Chinchilla-optimal.

    Args:
        model_name: Name of the model (for the report)
        num_params: Number of parameters
        actual_tokens: Number of tokens actually used for training

    Returns:
        Dictionary with:
        - 'model_name': the model name
        - 'num_params': number of parameters
        - 'actual_tokens': actual training tokens
        - 'optimal_tokens': Chinchilla-optimal tokens (20 * num_params)
        - 'tokens_per_param': actual_tokens / num_params (rounded to 1 decimal)
        - 'ratio_to_optimal': actual_tokens / optimal_tokens (rounded to 2 decimal)
        - 'status': 'under-trained' if ratio < 0.8,
                    'near-optimal' if 0.8 <= ratio <= 1.5,
                    'over-trained' if ratio > 1.5
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: KV Cache Size Estimation
# ---------------------------------------------------------------------------
def estimate_kv_cache_mb(
    n_layers: int,
    d_model: int,
    n_heads: int,
    seq_length: int,
    batch_size: int = 1,
    precision_bytes: int = 2,
) -> float:
    """
    Estimate the KV cache memory usage during inference.

    KV cache stores the key and value tensors for all previous tokens
    across all layers to avoid recomputation during autoregressive generation.

    Per layer, per sequence position:
    - Key:   d_model values (or d_head * n_kv_heads for GQA, but assume MHA here)
    - Value: d_model values

    Total KV cache = 2 * n_layers * seq_length * d_model * batch_size * precision_bytes

    Args:
        n_layers: Number of transformer layers
        d_model: Model dimension
        n_heads: Number of attention heads (for standard MHA, not used in calc
                 since we use d_model directly, but included for completeness)
        seq_length: Current sequence length (number of cached positions)
        batch_size: Number of sequences being generated in parallel
        precision_bytes: Bytes per value (2 for FP16, 1 for INT8)

    Returns:
        KV cache size in megabytes, rounded to 2 decimal places
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Model Architecture Identification
# ---------------------------------------------------------------------------
def identify_model_features() -> dict[str, list[str]]:
    """
    Return a dictionary mapping architectural features to the model
    families that use them.

    Features to categorize:
    - 'grouped_query_attention': Models using GQA
    - 'mixture_of_experts': Models using MoE architecture
    - 'sliding_window_attention': Models using sliding window attention
    - 'rotary_position_embeddings': Models using RoPE
    - 'swiglu_activation': Models using SwiGLU in FFN
    - 'constitutional_ai': Models using Constitutional AI alignment

    Choose from these model families:
    'GPT-4', 'Claude', 'Llama 3', 'Mistral 7B', 'Mixtral', 'Gemma'

    Returns:
        Dictionary mapping feature name to list of model family names
        (use the exact strings above)

    Hints:
    - GQA: Llama 3, Mistral 7B, Gemma
    - MoE: GPT-4, Mixtral
    - SWA: Mistral 7B
    - RoPE: Llama 3, Mistral 7B, Mixtral, Gemma
    - SwiGLU: Llama 3, Mistral 7B, Mixtral, Gemma
    - CAI: Claude
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Training Pipeline Ordering
# ---------------------------------------------------------------------------
def order_training_pipeline() -> list[str]:
    """
    Return the correct chronological order of the LLM training pipeline.

    Arrange these stages in order (return as a list of strings):
    - 'RLHF/DPO alignment'
    - 'Data collection and curation'
    - 'Supervised fine-tuning (SFT)'
    - 'Pretraining (causal LM)'
    - 'Deployment and monitoring'
    - 'Evaluation and red-teaming'

    Returns:
        List of 6 strings in the correct order
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Alignment Method Comparison
# ---------------------------------------------------------------------------
def compare_alignment_methods() -> dict[str, dict[str, str]]:
    """
    Return a comparison of RLHF and DPO alignment methods.

    For each method, provide:
    - 'num_models': How many models are needed during training
                    ('2' for DPO: policy + reference,
                     '3' for RLHF: policy + reference + reward model)
    - 'requires_reward_model': 'yes' or 'no'
    - 'training_algorithm': The core algorithm used
                            ('supervised' for DPO,
                             'PPO' for RLHF)
    - 'stability': 'high' or 'low'
                   (DPO is high, RLHF/PPO is low)
    - 'data_required': Type of data needed
                       ('preference_pairs' for both)

    Returns:
        Dictionary with keys 'RLHF' and 'DPO', each mapping to a dict
        with the keys described above.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Emergent Abilities Analysis
# ---------------------------------------------------------------------------
def classify_capabilities_by_scale() -> dict[str, list[str]]:
    """
    Classify model capabilities by the approximate scale needed.

    Capabilities to classify:
    - 'basic text completion'
    - 'few-shot learning'
    - 'chain-of-thought reasoning'
    - 'multi-step math'
    - 'simple classification'
    - 'code generation'
    - 'complex analogical reasoning'
    - 'multilingual translation'

    Scale categories:
    - 'small (< 3B)': Capabilities that work reasonably at small scale
    - 'medium (3B-30B)': Capabilities that need medium scale
    - 'large (30B+)': Capabilities that typically require large scale

    Returns:
        Dictionary with the three scale category strings as keys,
        each mapping to a list of capability strings.

    Expected classification:
    - small: 'basic text completion', 'simple classification'
    - medium: 'few-shot learning', 'code generation', 'multilingual translation'
    - large: 'chain-of-thought reasoning', 'multi-step math',
             'complex analogical reasoning'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Context Window Trade-offs
# ---------------------------------------------------------------------------
def analyze_context_tradeoffs(
    context_length: int,
    d_model: int,
    n_layers: int,
    n_heads: int,
) -> dict[str, object]:
    """
    Analyze the computational and memory trade-offs of different context lengths.

    Compute the following metrics for the given context length:

    1. 'attention_flops_per_layer': Approximate FLOPs for self-attention
       in one layer = 2 * seq_len^2 * d_model (for Q@K^T and attn@V)

    2. 'total_attention_flops': attention_flops_per_layer * n_layers

    3. 'kv_cache_mb': KV cache in MB (assuming FP16 = 2 bytes)
       = 2 * n_layers * context_length * d_model * 2 / (1024^2)

    4. 'attention_complexity': 'quadratic' (always, for standard attention)

    5. 'practical_limit': A string assessment:
       - context_length <= 4096: 'standard - fits easily on single GPU'
       - context_length <= 32768: 'extended - requires optimization'
       - context_length <= 131072: 'long - requires flash attention and careful memory management'
       - context_length > 131072: 'ultra-long - requires specialized techniques (ring attention, etc.)'

    Args:
        context_length: Number of tokens in the context
        d_model: Model dimension
        n_layers: Number of layers
        n_heads: Number of attention heads

    Returns:
        Dictionary with the keys described above
    """
    pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Test Exercise 1: Transformer Parameter Counting
    print("Testing Exercise 1: Transformer Parameter Counting...")
    # Small model: d_model=512, 6 layers, vocab=32000
    result = count_transformer_params(512, 6, 32000)
    assert result['attention_per_layer'] == 4 * 512 * 512, \
        f"Expected attention_per_layer={4*512*512}, got {result['attention_per_layer']}"
    assert result['ffn_per_layer'] == 2 * 512 * 2048, \
        f"Expected ffn_per_layer={2*512*2048}, got {result['ffn_per_layer']}"
    assert result['embedding'] == 32000 * 512
    print("  Passed!")

    # Llama 2 7B-like: d_model=4096, 32 layers, vocab=32000
    result7b = count_transformer_params(4096, 32, 32000)
    assert result7b['attention_per_layer'] == 4 * 4096 * 4096
    assert result7b['total'] > 6_000_000_000  # Should be ~6.5B+
    print("  Llama 7B-like params:", f"{result7b['total']:,}")
    print("  Passed!")

    # Test Exercise 2: Memory Requirements
    print("\nTesting Exercise 2: Memory Requirements...")
    assert estimate_memory_gb(7_000_000_000, 'fp32') == 26.08
    assert estimate_memory_gb(7_000_000_000, 'fp16') == 13.04
    assert estimate_memory_gb(7_000_000_000, 'int8') == 6.52
    assert estimate_memory_gb(7_000_000_000, 'int4') == 3.26
    print("  Passed!")

    # Test Exercise 3: Compute Estimation
    print("\nTesting Exercise 3: Compute Estimation (FLOPs)...")
    flops = estimate_training_flops(7_000_000_000, 2_000_000_000_000)
    assert flops == 6 * 7e9 * 2e12, f"Expected {6*7e9*2e12}, got {flops}"
    print(f"  7B model, 2T tokens: {flops:.2e} FLOPs")
    print("  Passed!")

    # Test Exercise 4: Training Time
    print("\nTesting Exercise 4: Training Time Estimation...")
    flops_7b = estimate_training_flops(7_000_000_000, 2_000_000_000_000)
    days = estimate_training_days(flops_7b, 1000, 312.0, 0.3)
    assert days > 0
    print(f"  7B model on 1000 A100s: {days} days")
    print("  Passed!")

    # Test Exercise 5: Chinchilla Optimal
    print("\nTesting Exercise 5: Chinchilla Optimal Tokens...")
    result = chinchilla_optimal(7_000_000_000)
    assert result['optimal_tokens'] == 140_000_000_000
    assert result['tokens_per_param'] == 20
    print(f"  7B model optimal: {result['optimal_tokens']:,} tokens")
    print("  Passed!")

    # Test Exercise 6: Training Efficiency Analysis
    print("\nTesting Exercise 6: Training Efficiency Analysis...")
    gpt3 = analyze_training_efficiency("GPT-3", 175_000_000_000, 300_000_000_000)
    assert gpt3['status'] == 'under-trained', f"GPT-3 should be under-trained, got {gpt3['status']}"
    llama2 = analyze_training_efficiency("Llama 2 7B", 7_000_000_000, 2_000_000_000_000)
    assert llama2['status'] == 'over-trained', f"Llama 2 should be over-trained, got {llama2['status']}"
    chinchilla = analyze_training_efficiency("Chinchilla", 70_000_000_000, 1_400_000_000_000)
    assert chinchilla['status'] == 'near-optimal', f"Chinchilla should be near-optimal, got {chinchilla['status']}"
    print("  Passed!")

    # Test Exercise 7: KV Cache Size
    print("\nTesting Exercise 7: KV Cache Size Estimation...")
    # Llama 2 7B-like: 32 layers, d_model=4096, 32 heads, 4096 seq length
    kv_mb = estimate_kv_cache_mb(32, 4096, 32, 4096, batch_size=1, precision_bytes=2)
    assert kv_mb > 0
    print(f"  Llama 7B KV cache at 4096 tokens: {kv_mb} MB")
    # Double sequence length should double cache
    kv_mb_long = estimate_kv_cache_mb(32, 4096, 32, 8192, batch_size=1, precision_bytes=2)
    assert abs(kv_mb_long - 2 * kv_mb) < 0.01
    print("  Passed!")

    # Test Exercise 8: Model Features
    print("\nTesting Exercise 8: Model Architecture Identification...")
    features = identify_model_features()
    assert 'Llama 3' in features['grouped_query_attention']
    assert 'GPT-4' in features['mixture_of_experts']
    assert 'Mistral 7B' in features['sliding_window_attention']
    assert 'Claude' in features['constitutional_ai']
    print("  Passed!")

    # Test Exercise 9: Training Pipeline
    print("\nTesting Exercise 9: Training Pipeline Ordering...")
    pipeline = order_training_pipeline()
    assert len(pipeline) == 6
    assert pipeline[0] == 'Data collection and curation'
    assert pipeline[1] == 'Pretraining (causal LM)'
    assert pipeline[2] == 'Supervised fine-tuning (SFT)'
    assert pipeline[-1] == 'Deployment and monitoring'
    print("  Passed!")

    # Test Exercise 10: Alignment Comparison
    print("\nTesting Exercise 10: Alignment Method Comparison...")
    methods = compare_alignment_methods()
    assert methods['RLHF']['num_models'] == '3'
    assert methods['DPO']['num_models'] == '2'
    assert methods['RLHF']['requires_reward_model'] == 'yes'
    assert methods['DPO']['requires_reward_model'] == 'no'
    assert methods['DPO']['stability'] == 'high'
    print("  Passed!")

    # Test Exercise 11: Capabilities by Scale
    print("\nTesting Exercise 11: Emergent Abilities Analysis...")
    caps = classify_capabilities_by_scale()
    assert 'basic text completion' in caps['small (< 3B)']
    assert 'chain-of-thought reasoning' in caps['large (30B+)']
    assert 'few-shot learning' in caps['medium (3B-30B)']
    print("  Passed!")

    # Test Exercise 12: Context Tradeoffs
    print("\nTesting Exercise 12: Context Window Trade-offs...")
    result = analyze_context_tradeoffs(4096, 4096, 32, 32)
    assert result['attention_complexity'] == 'quadratic'
    assert result['practical_limit'] == 'standard - fits easily on single GPU'
    result_long = analyze_context_tradeoffs(131072, 4096, 32, 32)
    assert result_long['practical_limit'] == 'long - requires flash attention and careful memory management'
    # Attention FLOPs should scale quadratically
    assert result_long['attention_flops_per_layer'] > result['attention_flops_per_layer']
    ratio = result_long['attention_flops_per_layer'] / result['attention_flops_per_layer']
    expected_ratio = (131072 / 4096) ** 2
    assert abs(ratio - expected_ratio) < 1, f"Expected quadratic scaling, ratio={ratio}"
    print("  Passed!")

    print("\n" + "=" * 50)
    print("All exercises passed!")
    print("=" * 50)
