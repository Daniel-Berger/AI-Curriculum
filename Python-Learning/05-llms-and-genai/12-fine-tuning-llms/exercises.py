"""
Module 12: Fine-Tuning LLMs — Exercises
========================================

10 exercises on data prep, LoRA, QLoRA, quantization, and evaluation.

Run this file directly to check your solutions:
    python exercises.py
"""


# ---------------------------------------------------------------------------
# Exercise 1: Prepare Training Data
# ---------------------------------------------------------------------------
def prepare_training_jsonl(
    examples: list[tuple[str, str]],
) -> list[dict]:
    """
    Prepare training data in JSONL format.

    Args:
        examples: List of (question, answer) tuples

    Returns:
        List of dicts with 'messages' key
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Train/Val Split
# ---------------------------------------------------------------------------
def split_train_val(
    data: list,
    train_ratio: float = 0.8,
    random_seed: int = 42,
) -> tuple[list, list]:
    """
    Split data into training and validation sets.

    Args:
        data: Full dataset
        train_ratio: Fraction for training
        random_seed: Random seed

    Returns:
        Tuple of (train_data, val_data)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Data Quality Check
# ---------------------------------------------------------------------------
def check_data_quality(
    examples: list[tuple[str, str]],
) -> dict:
    """
    Check data quality: duplicates, lengths, format.

    Args:
        examples: List of (question, answer) tuples

    Returns:
        Dict with 'num_examples', 'duplicates', 'avg_q_len', 'avg_a_len'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: LoRA Config
# ---------------------------------------------------------------------------
def create_lora_config(
    rank: int = 8,
    alpha: int = 16,
    target_modules: list = None,
    lora_dropout: float = 0.05,
) -> dict:
    """
    Create LoRA configuration for fine-tuning.

    Args:
        rank: LoRA rank
        alpha: LoRA alpha (scaling)
        target_modules: Modules to apply LoRA to
        lora_dropout: Dropout rate

    Returns:
        LoRA config dict
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Parameter Efficiency Estimate
# ---------------------------------------------------------------------------
def estimate_trainable_params(
    model_params: int,
    rank: int,
    num_layers: int,
    d_model: int,
) -> dict:
    """
    Estimate trainable parameters for LoRA.

    LoRA params = rank * (d_model + d_model) * num_layers

    Args:
        model_params: Total model parameters
        rank: LoRA rank
        num_layers: Number of layers
        d_model: Model dimension

    Returns:
        Dict with 'full_params', 'lora_params', 'percentage'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: QLoRA Memory Estimate
# ---------------------------------------------------------------------------
def estimate_memory_for_training(
    model_params: int,
    bits: int = 4,
    with_lora: bool = True,
    rank: int = 8,
) -> dict:
    """
    Estimate GPU memory needed for QLoRA training.

    Model: bits * model_params / 8 GB
    LoRA overhead: ~20% extra
    Gradients/optimizer: ~2-3x model size

    Args:
        model_params: Number of model parameters
        bits: Quantization bits (4 or 8)
        with_lora: Whether using LoRA
        rank: LoRA rank

    Returns:
        Dict with 'model_gb', 'training_gb', 'total_gb'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Evaluate Exact Match
# ---------------------------------------------------------------------------
def calculate_exact_match(
    predictions: list[str],
    references: list[str],
) -> float:
    """
    Calculate exact match accuracy.

    Args:
        predictions: Model predictions
        references: Reference answers

    Returns:
        Exact match score (0-1)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Calculate F1 Score
# ---------------------------------------------------------------------------
def calculate_f1(
    predictions: list[str],
    references: list[str],
) -> float:
    """
    Calculate token-level F1 score.

    Args:
        predictions: Model predictions
        references: Reference answers

    Returns:
        F1 score (0-1)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Detect Overfitting
# ---------------------------------------------------------------------------
def detect_overfitting(
    train_loss: list[float],
    val_loss: list[float],
    threshold: float = 0.1,
) -> dict:
    """
    Detect if model is overfitting.

    Overfitting if: (val_loss - train_loss) / train_loss > threshold

    Args:
        train_loss: Training loss per epoch
        val_loss: Validation loss per epoch
        threshold: Divergence threshold

    Returns:
        Dict with 'is_overfitting', 'divergence', 'best_epoch'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Comparison Report
# ---------------------------------------------------------------------------
def create_comparison_report(
    baseline_accuracy: float,
    finetuned_accuracy: float,
    training_time_hours: float,
    cost_dollars: float,
) -> dict:
    """
    Create a report comparing baseline vs fine-tuned model.

    Args:
        baseline_accuracy: Baseline model accuracy
        finetuned_accuracy: Fine-tuned model accuracy
        training_time_hours: Time to fine-tune
        cost_dollars: Cost to fine-tune

    Returns:
        Report dict with metrics and recommendation
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    examples = [("Q1", "A1"), ("Q2", "A2")]
    data = prepare_training_jsonl(examples)
    assert len(data) == 2 and 'messages' in data[0]

    # Test Exercise 2
    train, val = split_train_val([1, 2, 3, 4, 5], train_ratio=0.8)
    assert len(train) + len(val) == 5

    # Test Exercise 3
    quality = check_data_quality([("hello", "world")])
    assert 'num_examples' in quality

    # Test Exercise 4
    cfg = create_lora_config()
    assert 'rank' in cfg

    # Test Exercise 5
    params = estimate_trainable_params(7_000_000_000, 8, 32, 4096)
    assert 'lora_params' in params

    # Test Exercise 6
    mem = estimate_memory_for_training(7_000_000_000)
    assert 'total_gb' in mem

    # Test Exercise 7
    em = calculate_exact_match(['A'], ['A'])
    assert em == 1.0

    # Test Exercise 8
    f1 = calculate_f1(['hello world'], ['hello world'])
    assert f1 > 0

    # Test Exercise 9
    overfitting = detect_overfitting([0.5, 0.4], [0.5, 0.6])
    assert 'is_overfitting' in overfitting

    # Test Exercise 10
    report = create_comparison_report(0.7, 0.85, 2.0, 50.0)
    assert 'improvement' in report or 'accuracy_gain' in report

    print('All tests passed!')
