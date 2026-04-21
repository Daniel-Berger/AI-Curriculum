"""
Module 01: LLM Architecture — Solutions
========================================

Complete solutions for all 12 exercises.
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
    """
    d_ff = d_ff_multiplier * d_model

    # Self-attention: Q, K, V, Output — each is d_model × d_model
    attention_per_layer = 4 * d_model * d_model

    # Feed-forward: two linear layers (d_model → d_ff and d_ff → d_model)
    ffn_per_layer = 2 * d_model * d_ff

    # Layer norms: two per layer, each with d_model scale parameters
    norm_per_layer = 2 * d_model

    # Token embeddings
    embedding = vocab_size * d_model

    # Final layer norm
    final_norm = d_model

    total_per_layer = attention_per_layer + ffn_per_layer + norm_per_layer
    total = n_layers * total_per_layer + embedding + final_norm

    return {
        'attention_per_layer': attention_per_layer,
        'ffn_per_layer': ffn_per_layer,
        'norm_per_layer': norm_per_layer,
        'embedding': embedding,
        'total_per_layer': total_per_layer,
        'total': total,
    }


# ---------------------------------------------------------------------------
# Exercise 2: Memory Requirements
# ---------------------------------------------------------------------------
def estimate_memory_gb(
    num_params: int,
    precision: str,
) -> float:
    """
    Estimate the memory required to load a model in different precisions.
    """
    bytes_per_param = {
        'fp32': 4,
        'fp16': 2,
        'bf16': 2,
        'int8': 1,
        'int4': 0.5,
    }

    total_bytes = num_params * bytes_per_param[precision]
    total_gb = total_bytes / (1024 ** 3)
    return round(total_gb, 2)


# ---------------------------------------------------------------------------
# Exercise 3: Compute Estimation (FLOPs)
# ---------------------------------------------------------------------------
def estimate_training_flops(
    num_params: int,
    num_tokens: int,
) -> float:
    """
    Estimate the total floating point operations for training.
    FLOPs ≈ 6 * N * D
    """
    return 6.0 * num_params * num_tokens


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
    """
    # Convert TFLOPS to FLOPS
    flops_per_gpu_per_second = gpu_tflops * 1e12

    # Effective FLOPS across all GPUs with utilization
    effective_flops_per_second = num_gpus * flops_per_gpu_per_second * utilization

    # Total seconds
    total_seconds = total_flops / effective_flops_per_second

    # Convert to days
    total_days = total_seconds / (60 * 60 * 24)

    return round(total_days, 1)


# ---------------------------------------------------------------------------
# Exercise 5: Chinchilla Optimal Tokens
# ---------------------------------------------------------------------------
def chinchilla_optimal(
    num_params: int,
) -> dict[str, float]:
    """
    Calculate the Chinchilla-optimal number of training tokens.
    """
    optimal_tokens = 20 * num_params
    optimal_flops = 6.0 * num_params * optimal_tokens

    return {
        'optimal_tokens': optimal_tokens,
        'optimal_flops': optimal_flops,
        'tokens_per_param': 20,
    }


# ---------------------------------------------------------------------------
# Exercise 6: Actual vs. Optimal Training Analysis
# ---------------------------------------------------------------------------
def analyze_training_efficiency(
    model_name: str,
    num_params: int,
    actual_tokens: int,
) -> dict[str, object]:
    """
    Analyze whether a model was over-trained or under-trained.
    """
    optimal_tokens = 20 * num_params
    tokens_per_param = round(actual_tokens / num_params, 1)
    ratio_to_optimal = round(actual_tokens / optimal_tokens, 2)

    if ratio_to_optimal < 0.8:
        status = 'under-trained'
    elif ratio_to_optimal <= 1.5:
        status = 'near-optimal'
    else:
        status = 'over-trained'

    return {
        'model_name': model_name,
        'num_params': num_params,
        'actual_tokens': actual_tokens,
        'optimal_tokens': optimal_tokens,
        'tokens_per_param': tokens_per_param,
        'ratio_to_optimal': ratio_to_optimal,
        'status': status,
    }


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
    """
    # 2 for Key + Value, then layers, seq positions, dimensions, batch, precision
    total_bytes = 2 * n_layers * seq_length * d_model * batch_size * precision_bytes
    total_mb = total_bytes / (1024 ** 2)
    return round(total_mb, 2)


# ---------------------------------------------------------------------------
# Exercise 8: Model Architecture Identification
# ---------------------------------------------------------------------------
def identify_model_features() -> dict[str, list[str]]:
    """
    Return a dictionary mapping architectural features to model families.
    """
    return {
        'grouped_query_attention': ['Llama 3', 'Mistral 7B', 'Gemma'],
        'mixture_of_experts': ['GPT-4', 'Mixtral'],
        'sliding_window_attention': ['Mistral 7B'],
        'rotary_position_embeddings': ['Llama 3', 'Mistral 7B', 'Mixtral', 'Gemma'],
        'swiglu_activation': ['Llama 3', 'Mistral 7B', 'Mixtral', 'Gemma'],
        'constitutional_ai': ['Claude'],
    }


# ---------------------------------------------------------------------------
# Exercise 9: Training Pipeline Ordering
# ---------------------------------------------------------------------------
def order_training_pipeline() -> list[str]:
    """
    Return the correct chronological order of the LLM training pipeline.
    """
    return [
        'Data collection and curation',
        'Pretraining (causal LM)',
        'Supervised fine-tuning (SFT)',
        'RLHF/DPO alignment',
        'Evaluation and red-teaming',
        'Deployment and monitoring',
    ]


# ---------------------------------------------------------------------------
# Exercise 10: Alignment Method Comparison
# ---------------------------------------------------------------------------
def compare_alignment_methods() -> dict[str, dict[str, str]]:
    """
    Return a comparison of RLHF and DPO alignment methods.
    """
    return {
        'RLHF': {
            'num_models': '3',
            'requires_reward_model': 'yes',
            'training_algorithm': 'PPO',
            'stability': 'low',
            'data_required': 'preference_pairs',
        },
        'DPO': {
            'num_models': '2',
            'requires_reward_model': 'no',
            'training_algorithm': 'supervised',
            'stability': 'high',
            'data_required': 'preference_pairs',
        },
    }


# ---------------------------------------------------------------------------
# Exercise 11: Emergent Abilities Analysis
# ---------------------------------------------------------------------------
def classify_capabilities_by_scale() -> dict[str, list[str]]:
    """
    Classify model capabilities by the approximate scale needed.
    """
    return {
        'small (< 3B)': [
            'basic text completion',
            'simple classification',
        ],
        'medium (3B-30B)': [
            'few-shot learning',
            'code generation',
            'multilingual translation',
        ],
        'large (30B+)': [
            'chain-of-thought reasoning',
            'multi-step math',
            'complex analogical reasoning',
        ],
    }


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
    """
    # Attention FLOPs per layer: 2 * seq_len^2 * d_model
    attention_flops_per_layer = 2 * context_length ** 2 * d_model

    # Total attention FLOPs across all layers
    total_attention_flops = attention_flops_per_layer * n_layers

    # KV cache in MB (FP16 = 2 bytes)
    kv_cache_bytes = 2 * n_layers * context_length * d_model * 2
    kv_cache_mb = round(kv_cache_bytes / (1024 ** 2), 2)

    # Practical limit assessment
    if context_length <= 4096:
        practical_limit = 'standard - fits easily on single GPU'
    elif context_length <= 32768:
        practical_limit = 'extended - requires optimization'
    elif context_length <= 131072:
        practical_limit = 'long - requires flash attention and careful memory management'
    else:
        practical_limit = 'ultra-long - requires specialized techniques (ring attention, etc.)'

    return {
        'attention_flops_per_layer': attention_flops_per_layer,
        'total_attention_flops': total_attention_flops,
        'kv_cache_mb': kv_cache_mb,
        'attention_complexity': 'quadratic',
        'practical_limit': practical_limit,
    }


# ---------------------------------------------------------------------------
# Run tests
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Test Exercise 1
    print("Testing Exercise 1: Transformer Parameter Counting...")
    result = count_transformer_params(512, 6, 32000)
    assert result['attention_per_layer'] == 4 * 512 * 512
    assert result['ffn_per_layer'] == 2 * 512 * 2048
    assert result['embedding'] == 32000 * 512
    result7b = count_transformer_params(4096, 32, 32000)
    print(f"  Llama 7B-like total params: {result7b['total']:,}")
    print("  Passed!")

    # Test Exercise 2
    print("\nTesting Exercise 2: Memory Requirements...")
    assert estimate_memory_gb(7_000_000_000, 'fp32') == 26.08
    assert estimate_memory_gb(7_000_000_000, 'fp16') == 13.04
    assert estimate_memory_gb(7_000_000_000, 'int8') == 6.52
    assert estimate_memory_gb(7_000_000_000, 'int4') == 3.26
    print("  Passed!")

    # Test Exercise 3
    print("\nTesting Exercise 3: Compute Estimation...")
    flops = estimate_training_flops(7_000_000_000, 2_000_000_000_000)
    assert flops == 6 * 7e9 * 2e12
    print(f"  {flops:.2e} FLOPs")
    print("  Passed!")

    # Test Exercise 4
    print("\nTesting Exercise 4: Training Time...")
    flops_7b = estimate_training_flops(7_000_000_000, 2_000_000_000_000)
    days = estimate_training_days(flops_7b, 1000, 312.0, 0.3)
    print(f"  {days} days on 1000 A100s")
    print("  Passed!")

    # Test Exercise 5
    print("\nTesting Exercise 5: Chinchilla Optimal...")
    result = chinchilla_optimal(7_000_000_000)
    assert result['optimal_tokens'] == 140_000_000_000
    assert result['tokens_per_param'] == 20
    print("  Passed!")

    # Test Exercise 6
    print("\nTesting Exercise 6: Training Efficiency...")
    gpt3 = analyze_training_efficiency("GPT-3", 175_000_000_000, 300_000_000_000)
    assert gpt3['status'] == 'under-trained'
    llama2 = analyze_training_efficiency("Llama 2 7B", 7_000_000_000, 2_000_000_000_000)
    assert llama2['status'] == 'over-trained'
    chinchilla = analyze_training_efficiency("Chinchilla", 70_000_000_000, 1_400_000_000_000)
    assert chinchilla['status'] == 'near-optimal'
    print("  Passed!")

    # Test Exercise 7
    print("\nTesting Exercise 7: KV Cache Size...")
    kv_mb = estimate_kv_cache_mb(32, 4096, 32, 4096)
    print(f"  KV cache at 4096 tokens: {kv_mb} MB")
    kv_mb_long = estimate_kv_cache_mb(32, 4096, 32, 8192)
    assert abs(kv_mb_long - 2 * kv_mb) < 0.01
    print("  Passed!")

    # Test Exercise 8
    print("\nTesting Exercise 8: Model Features...")
    features = identify_model_features()
    assert 'Llama 3' in features['grouped_query_attention']
    assert 'GPT-4' in features['mixture_of_experts']
    assert 'Claude' in features['constitutional_ai']
    print("  Passed!")

    # Test Exercise 9
    print("\nTesting Exercise 9: Training Pipeline...")
    pipeline = order_training_pipeline()
    assert pipeline[0] == 'Data collection and curation'
    assert pipeline[1] == 'Pretraining (causal LM)'
    assert pipeline[-1] == 'Deployment and monitoring'
    print("  Passed!")

    # Test Exercise 10
    print("\nTesting Exercise 10: Alignment Comparison...")
    methods = compare_alignment_methods()
    assert methods['RLHF']['num_models'] == '3'
    assert methods['DPO']['num_models'] == '2'
    assert methods['DPO']['stability'] == 'high'
    print("  Passed!")

    # Test Exercise 11
    print("\nTesting Exercise 11: Capabilities by Scale...")
    caps = classify_capabilities_by_scale()
    assert 'basic text completion' in caps['small (< 3B)']
    assert 'chain-of-thought reasoning' in caps['large (30B+)']
    print("  Passed!")

    # Test Exercise 12
    print("\nTesting Exercise 12: Context Tradeoffs...")
    result = analyze_context_tradeoffs(4096, 4096, 32, 32)
    assert result['attention_complexity'] == 'quadratic'
    assert result['practical_limit'] == 'standard - fits easily on single GPU'
    result_long = analyze_context_tradeoffs(131072, 4096, 32, 32)
    assert result_long['practical_limit'] == 'long - requires flash attention and careful memory management'
    print("  Passed!")

    print("\n" + "=" * 50)
    print("All solutions verified!")
    print("=" * 50)
