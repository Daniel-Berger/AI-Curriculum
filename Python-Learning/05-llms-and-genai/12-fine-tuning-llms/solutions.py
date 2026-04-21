"""
Module 12: Fine-Tuning LLMs — Solutions
========================================

Complete solutions for all 10 exercises.
"""

import random
from collections import Counter


# Exercise 1
def prepare_training_jsonl(examples: list[tuple[str, str]]) -> list[dict]:
    data = []
    for question, answer in examples:
        data.append({
            "messages": [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ]
        })
    return data


# Exercise 2
def split_train_val(data: list, train_ratio: float = 0.8, random_seed: int = 42) -> tuple[list, list]:
    random.seed(random_seed)
    shuffled = data.copy()
    random.shuffle(shuffled)

    split_idx = int(len(shuffled) * train_ratio)
    train = shuffled[:split_idx]
    val = shuffled[split_idx:]

    return train, val


# Exercise 3
def check_data_quality(examples: list[tuple[str, str]]) -> dict:
    if not examples:
        return {'num_examples': 0, 'duplicates': 0, 'avg_q_len': 0, 'avg_a_len': 0}

    # Check duplicates
    unique_examples = set(examples)
    num_duplicates = len(examples) - len(unique_examples)

    # Calculate lengths
    q_lens = [len(q) for q, _ in examples]
    a_lens = [len(a) for _, a in examples]

    return {
        'num_examples': len(examples),
        'duplicates': num_duplicates,
        'avg_q_len': round(sum(q_lens) / len(q_lens), 1) if q_lens else 0,
        'avg_a_len': round(sum(a_lens) / len(a_lens), 1) if a_lens else 0,
    }


# Exercise 4
def create_lora_config(
    rank: int = 8,
    alpha: int = 16,
    target_modules: list = None,
    lora_dropout: float = 0.05,
) -> dict:
    return {
        'rank': rank,
        'alpha': alpha,
        'target_modules': target_modules or ['q_proj', 'v_proj'],
        'lora_dropout': lora_dropout,
    }


# Exercise 5
def estimate_trainable_params(
    model_params: int,
    rank: int,
    num_layers: int,
    d_model: int,
) -> dict:
    # LoRA: rank * (d_model + d_model) * num_layers = 2 * rank * d_model * num_layers
    lora_params = 2 * rank * d_model * num_layers

    percentage = (lora_params / model_params) * 100

    return {
        'full_params': model_params,
        'lora_params': lora_params,
        'percentage': round(percentage, 2),
    }


# Exercise 6
def estimate_memory_for_training(
    model_params: int,
    bits: int = 4,
    with_lora: bool = True,
    rank: int = 8,
) -> dict:
    # Model size
    bytes_per_param = bits / 8
    model_gb = (model_params * bytes_per_param) / (1024 ** 3)

    # Training overhead: gradients (model size) + optimizer state (2x model for Adam)
    training_overhead = 3 * model_gb

    # LoRA adds ~20% to gradient overhead
    if with_lora:
        training_overhead *= 1.2

    total_gb = model_gb + training_overhead

    return {
        'model_gb': round(model_gb, 2),
        'training_gb': round(training_overhead, 2),
        'total_gb': round(total_gb, 2),
    }


# Exercise 7
def calculate_exact_match(predictions: list[str], references: list[str]) -> float:
    if not predictions:
        return 0.0

    matches = sum(1 for p, r in zip(predictions, references) if p.strip() == r.strip())
    return matches / len(predictions)


# Exercise 8
def calculate_f1(predictions: list[str], references: list[str]) -> float:
    if not predictions:
        return 0.0

    f1_scores = []
    for pred, ref in zip(predictions, references):
        pred_tokens = set(pred.lower().split())
        ref_tokens = set(ref.lower().split())

        if not pred_tokens and not ref_tokens:
            f1_scores.append(1.0)
            continue

        if not pred_tokens or not ref_tokens:
            f1_scores.append(0.0)
            continue

        tp = len(pred_tokens & ref_tokens)
        fp = len(pred_tokens - ref_tokens)
        fn = len(ref_tokens - pred_tokens)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0

        f1_scores.append(f1)

    return sum(f1_scores) / len(f1_scores)


# Exercise 9
def detect_overfitting(
    train_loss: list[float],
    val_loss: list[float],
    threshold: float = 0.1,
) -> dict:
    if not train_loss or not val_loss:
        return {'is_overfitting': False, 'divergence': 0, 'best_epoch': 0}

    # Find best (lowest) validation loss
    best_epoch = val_loss.index(min(val_loss))

    # Calculate divergence at last epoch
    if train_loss[-1] > 0:
        divergence = (val_loss[-1] - train_loss[-1]) / train_loss[-1]
    else:
        divergence = 0

    is_overfitting = divergence > threshold

    return {
        'is_overfitting': is_overfitting,
        'divergence': round(divergence, 3),
        'best_epoch': best_epoch,
    }


# Exercise 10
def create_comparison_report(
    baseline_accuracy: float,
    finetuned_accuracy: float,
    training_time_hours: float,
    cost_dollars: float,
) -> dict:
    improvement = finetuned_accuracy - baseline_accuracy
    improvement_pct = (improvement / baseline_accuracy) * 100 if baseline_accuracy > 0 else 0

    # Cost per 1% improvement
    cost_per_improvement = cost_dollars / improvement_pct if improvement_pct > 0 else float('inf')

    recommendation = "Recommended" if improvement_pct > 5 else "Consider baseline"

    return {
        'baseline_accuracy': round(baseline_accuracy, 3),
        'finetuned_accuracy': round(finetuned_accuracy, 3),
        'accuracy_gain': round(improvement, 3),
        'improvement_percent': round(improvement_pct, 2),
        'training_time_hours': round(training_time_hours, 2),
        'cost_dollars': round(cost_dollars, 2),
        'cost_per_improvement_pct': round(cost_per_improvement, 2),
        'recommendation': recommendation,
    }


# Test Suite
if __name__ == '__main__':
    examples = [("Q1", "A1"), ("Q2", "A2")]
    data = prepare_training_jsonl(examples)
    assert len(data) == 2
    assert data[0]['messages'][0]['role'] == 'user'

    train, val = split_train_val([1, 2, 3, 4, 5], train_ratio=0.8)
    assert len(train) == 4
    assert len(val) == 1

    quality = check_data_quality([("hello", "world"), ("hello", "world")])
    assert quality['num_examples'] == 2
    assert quality['duplicates'] == 0

    cfg = create_lora_config(rank=16)
    assert cfg['rank'] == 16

    params = estimate_trainable_params(7_000_000_000, 8, 32, 4096)
    assert params['lora_params'] > 0
    assert params['percentage'] < 1

    mem = estimate_memory_for_training(7_000_000_000, bits=4)
    assert mem['total_gb'] > 0

    em = calculate_exact_match(['answer'], ['answer'])
    assert em == 1.0

    f1 = calculate_f1(['hello world'], ['hello world'])
    assert f1 == 1.0

    overfitting = detect_overfitting([0.5, 0.4], [0.5, 0.6])
    assert isinstance(overfitting['is_overfitting'], bool)

    report = create_comparison_report(0.7, 0.85, 2.0, 50.0)
    assert 'improvement_percent' in report

    print('All tests passed!')
