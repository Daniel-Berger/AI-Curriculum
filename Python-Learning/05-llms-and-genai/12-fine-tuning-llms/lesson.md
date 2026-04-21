# Module 12: Fine-Tuning LLMs

## When to Fine-Tune

Fine-tuning makes sense when:
1. You have domain-specific tasks and labeled data (100s-1000s of examples)
2. Prompt engineering alone isn't sufficient
3. You need consistent output format
4. You want to reduce costs (smaller fine-tuned model vs. large model)
5. You need low latency

Fine-tuning doesn't make sense for:
- One-off tasks (use prompting)
- No labeled data available
- Task too complex to learn from examples

---

## Data Preparation

### Format

OpenAI/Anthropic fine-tuning expects JSONL (JSON Lines):

```jsonl
{"messages": [{"role": "user", "content": "Q1"}, {"role": "assistant", "content": "A1"}]}
{"messages": [{"role": "user", "content": "Q2"}, {"role": "assistant", "content": "A2"}]}
```

### Quality Checklist

- **Diversity**: Mix of different task types
- **Correctness**: All answers are factually correct
- **Consistency**: Same style and format throughout
- **Size**: At least 100 examples, ideally 500+
- **Balance**: Roughly equal distribution across categories
- **No duplicates**: Remove near-duplicate examples

---

## Parameter-Efficient Fine-Tuning (PEFT)

### LoRA (Low-Rank Adaptation)

Instead of updating all model weights, update small "adapter" matrices:

```
Original: W (large matrix)
LoRA: W + A @ B  (where A, B are small)

Total params = original + r × (input_dim + output_dim)
where r = rank (typically 8-64)
```

**Advantages**:
- 10-100x fewer parameters than full fine-tuning
- Faster training
- Can combine multiple LoRA adapters
- Cheaper

**When to use**: Small-to-medium adapters, cost-sensitive

### QLoRA (Quantized LoRA)

Quantize base model to 4-bit, only update LoRA:

```
Memory for 7B model:
- Full FP32: 28GB
- LoRA: 6GB
- QLoRA: 1.5GB
```

---

## Training Process

### 1. Data Preparation

```python
# Create JSONL training data
import jsonlines

training_data = [
    {
        "messages": [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}
        ]
    }
    for question, answer in examples
]

with jsonlines.open("training.jsonl", "w") as f:
    for example in training_data:
        f.write(example)
```

### 2. Upload and Fine-Tune (OpenAI)

```python
# Upload file
training_file = client.files.create(
    file=open("training.jsonl", "rb"),
    purpose="fine-tune"
)

# Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=training_file.id,
    model="gpt-3.5-turbo",
    hyperparameters={
        "n_epochs": 3,
        "learning_rate_multiplier": 1.0
    }
)

# Monitor progress
while True:
    job = client.fine_tuning.jobs.retrieve(job.id)
    if job.status == "succeeded":
        print(f"Fine-tuned model: {job.fine_tuned_model}")
        break
```

### 3. Hyperparameters

| Hyperparameter | Default | Notes |
|---|---|---|
| n_epochs | 3 | Number of training passes |
| learning_rate | 0.001 | Learning rate |
| batch_size | auto | Batch size |
| weight_decay | 0.01 | L2 regularization |

---

## Evaluation

### Validation Set

Always hold out 10-20% of data for validation:

```python
import random

all_examples = [...]
random.shuffle(all_examples)
split = int(0.8 * len(all_examples))

train = all_examples[:split]
val = all_examples[split:]
```

### Metrics

- **Exact Match**: Model answer == reference answer (strict)
- **F1 Score**: Token-level overlap
- **BLEU/ROUGE**: Sequence similarity
- **Task-Specific**: Accuracy, precision, recall for classification

### Comparing with Baseline

```python
def compare_models(examples):
    baseline_accuracy = evaluate(base_model, examples)
    finetuned_accuracy = evaluate(finetuned_model, examples)

    improvement = (finetuned_accuracy - baseline_accuracy) / baseline_accuracy * 100
    print(f"Improvement: {improvement}%")
```

---

## Common Pitfalls

1. **Too little data**: <50 examples → likely overfitting
2. **Poor data quality**: Errors in training data get amplified
3. **Wrong format**: Mismatched instruction/response format
4. **Overfitting**: Monitor validation accuracy
5. **Inconsistent style**: Mixed tones/formats confuse the model

---

## Production Deployment

### Testing Before Deployment

1. Evaluate on held-out test set
2. Compare against baseline
3. Do edge case testing
4. Monitor for data drift

### Deployment Options

- **OpenAI**: Use fine-tuned model ID in API calls
- **Local**: Export weights, run with vLLM or similar
- **Cost**: Fine-tuned models cost less per token than large models

---

## Summary

- **Fine-tuning**: Training on domain-specific data
- **Data prep**: JSONL format, 100-1000 high-quality examples
- **LoRA**: Parameter-efficient, combines adapters
- **QLoRA**: 4-bit quantization + LoRA, minimal memory
- **Hyperparameters**: Epochs (3-10), learning rate (1e-5 to 1e-3)
- **Evaluation**: Hold-out validation set, compare metrics
- **Production**: Monitor performance, watch for drift
