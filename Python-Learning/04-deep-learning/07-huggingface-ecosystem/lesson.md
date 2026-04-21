# Hugging Face Ecosystem

## Introduction

Hugging Face provides state-of-the-art pre-trained models and tools for NLP, computer vision, and beyond. This chapter covers the transformers library, datasets, and the Hub.

## 1. Hugging Face Hub

The Hub is a repository of pre-trained models, datasets, and spaces.

### Exploring the Hub

```python
from huggingface_hub import hf_hub_download, list_models, model_info

# List available models
models = list_models(task="text-classification")
for model in models[:5]:
    print(model.id)

# Get model info
info = model_info("bert-base-uncased")
print(info.downloads)
print(info.likes)

# Download model files
model_path = hf_hub_download(
    repo_id="bert-base-uncased",
    filename="pytorch_model.bin"
)
```

### Authentication

```python
from huggingface_hub import login, notebook_login

# Login to Hugging Face
login(token="your_hf_token")

# Or in notebook
notebook_login()
```

## 2. Transformers Library

The main library for working with pre-trained models.

### AutoModel and AutoTokenizer

The `Auto` classes automatically load the correct model/tokenizer:

```python
from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Load model
model = AutoModel.from_pretrained("bert-base-uncased")

# For specific tasks
model = AutoModelForCausalLM.from_pretrained("gpt2")
```

### Tokenization

Converting text to tokens for the model:

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Basic tokenization
text = "Hello, how are you?"
tokens = tokenizer.tokenize(text)
print(tokens)  # ['hello', ',', 'how', 'are', 'you', '?']

# Full encoding
encoding = tokenizer(text, return_tensors="pt")
print(encoding.keys())  # dict_keys(['input_ids', 'token_type_ids', 'attention_mask'])
print(encoding['input_ids'])

# Batch encoding
texts = ["Hello world", "Good morning"]
batch = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

# Decode back to text
decoded = tokenizer.decode(encoding['input_ids'][0])
```

### Tokenizer Options

```python
# Padding and truncation
encoding = tokenizer(
    text,
    padding="max_length",  # Pad to max length
    truncation=True,       # Truncate if too long
    max_length=512,
    return_tensors="pt"
)

# Special token handling
encoding = tokenizer(
    text,
    add_special_tokens=True,  # Add [CLS], [SEP], etc.
    return_special_tokens_mask=True
)

# Get vocabulary size
vocab_size = len(tokenizer)

# Save and load custom tokenizer
tokenizer.save_pretrained("./my_tokenizer")
loaded = AutoTokenizer.from_pretrained("./my_tokenizer")
```

## 3. Pipeline API

High-level API for common tasks without loading models directly.

### Text Classification

```python
from transformers import pipeline

# Create pipeline
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# Classify text
result = classifier("This movie is amazing!")
print(result)  # [{'label': 'POSITIVE', 'score': 0.9998}]

# Batch classification
results = classifier([
    "This is great!",
    "This is terrible.",
    "Not sure about this."
])
```

### Sentiment Analysis

```python
sentiment = pipeline("sentiment-analysis")
result = sentiment("I love this product!")
print(result)  # [{'label': 'POSITIVE', 'score': 0.9999}]
```

### Text Generation

```python
generator = pipeline("text-generation", model="gpt2")
result = generator("Once upon a time", max_length=50, num_return_sequences=2)
for seq in result:
    print(seq['generated_text'])
```

### Summarization

```python
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

text = """
The quick brown fox jumps over the lazy dog. This is a common phrase used to test typewriters and computer keyboards.
It contains all the letters of the English alphabet, making it useful for checking if all keys work properly.
Many websites and applications use this phrase as a default test phrase.
"""

summary = summarizer(text, max_length=30, min_length=10)
print(summary[0]['summary_text'])
```

### Zero-Shot Classification

Classify without fine-tuning on specific classes:

```python
zero_shot_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

text = "I am extremely happy about the release of this product"
candidate_labels = ["positive", "negative", "neutral"]

result = zero_shot_classifier(text, candidate_labels)
print(result)
# {
#     'sequence': '...',
#     'labels': ['positive', 'neutral', 'negative'],
#     'scores': [0.97, 0.02, 0.01]
# }
```

### Question Answering

```python
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

context = "Python is a programming language. It was created by Guido van Rossum."
question = "Who created Python?"

result = qa_pipeline(question=question, context=context)
print(result)  # {'score': 0.95, 'start': 36, 'end': 53, 'answer': 'Guido van Rossum'}
```

### Named Entity Recognition

```python
ner = pipeline("ner", model="dslim/bert-base-NER")
result = ner("My name is Sarah and I live in London.")
print(result)
```

## 4. Training with the Trainer API

Easy fine-tuning with the Trainer class:

```python
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification
from datasets import load_dataset

# Load dataset
dataset = load_dataset("imdb")

# Load model
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=100,
    evaluation_strategy="epoch",
)

# Create trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
)

# Train
trainer.train()

# Save model
trainer.save_model("./fine_tuned_model")
```

### Training Arguments

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./output",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=100,
    save_steps=1000,
    eval_steps=1000,
    evaluation_strategy="steps",  # or "epoch", "no"
    save_strategy="steps",         # or "epoch", "no"
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    learning_rate=2e-5,
    push_to_hub=True,  # Push to Hub after training
)
```

### Custom Datasets

```python
from datasets import Dataset
import pandas as pd

# From pandas DataFrame
df = pd.DataFrame({
    'text': ['Hello world', 'Good morning'],
    'label': [1, 0]
})
dataset = Dataset.from_pandas(df)

# From dictionary
data = {
    'text': ['Hello', 'World'],
    'label': [0, 1]
}
dataset = Dataset.from_dict(data)

# From list of dictionaries
examples = [
    {'text': 'Hello', 'label': 0},
    {'text': 'World', 'label': 1}
]
dataset = Dataset.from_dict({
    'text': [ex['text'] for ex in examples],
    'label': [ex['label'] for ex in examples]
})
```

## 5. Datasets Library

Load and process datasets from Hugging Face:

```python
from datasets import load_dataset, load_from_disk

# Load from Hub
dataset = load_dataset("imdb")
print(dataset)  # DatasetDict with train/test splits

# Access splits
train_data = dataset["train"]
test_data = dataset["test"]

# Inspect data
print(dataset["train"][0])
print(f"Number of samples: {len(dataset['train'])}")

# Map operations
def preprocess(example):
    example['text'] = example['text'].lower()
    return example

processed = dataset.map(preprocess)

# Filter
long_texts = dataset.filter(lambda x: len(x['text']) > 100)

# Save and load
dataset.save_to_disk("./my_dataset")
loaded = load_from_disk("./my_dataset")
```

## 6. Common Model Types

### Encoder Models (BERT)

```python
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

# Get last hidden state
inputs = tokenizer("Hello world", return_tensors="pt")
outputs = model(**inputs)
last_hidden_state = outputs.last_hidden_state
print(last_hidden_state.shape)  # (1, seq_len, 768)
```

### Decoder Models (GPT-2)

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")

# Generate text
input_ids = tokenizer("Once upon a time", return_tensors="pt")['input_ids']
output = model.generate(input_ids, max_length=50)
text = tokenizer.decode(output[0])
print(text)
```

### Encoder-Decoder Models (BART, T5)

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

# Summarization
input_ids = tokenizer("Long text here", return_tensors="pt")['input_ids']
summary_ids = model.generate(input_ids, max_length=50)
summary = tokenizer.decode(summary_ids[0])
```

## 7. Advanced Features

### LoRA Fine-tuning

Low-rank adaptation for efficient fine-tuning:

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("gpt2")

# Configure LoRA
lora_config = LoraConfig(
    r=8,                      # LoRA rank
    lora_alpha=32,             # LoRA alpha scaling
    target_modules=["c_attn"],  # Target layers
    lora_dropout=0.05,
    bias="none",
)

# Apply LoRA
model = get_peft_model(model, lora_config)
print(model.print_trainable_parameters())
# trainable params: 25,165,824 || all params: 124,439,808 || trainable%: 20.23
```

### Using GPU

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# Or automatically with fp16
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./output",
    fp16=True,  # Use mixed precision
    fp16_full_eval=True,
)
```

### Pushing to Hub

```python
# Push model after training
trainer.push_to_hub("my-awesome-model")

# Or manually
model.push_to_hub("my-awesome-model", use_auth_token=True)
tokenizer.push_to_hub("my-awesome-model", use_auth_token=True)
```

## Summary

- **Hub**: Central repository for models, datasets, and spaces
- **AutoModel/AutoTokenizer**: Automatically select correct model architecture
- **Pipelines**: High-level API for common NLP tasks
- **Trainer**: Easy fine-tuning with automatic mixed precision, distributed training
- **Datasets**: Efficient data loading and processing
- **Model Types**: Encoders (BERT), Decoders (GPT), Encoder-Decoders (T5, BART)
- **LoRA**: Efficient fine-tuning with low-rank adaptation
- **Hub Integration**: Push models and share with community
