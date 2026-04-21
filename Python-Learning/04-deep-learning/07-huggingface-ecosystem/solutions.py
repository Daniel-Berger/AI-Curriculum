"""
Solutions for Hugging Face Ecosystem exercises.
"""

import torch
from transformers import (
    AutoTokenizer, AutoModel, pipeline,
    AutoModelForSequenceClassification, AutoModelForCausalLM,
    Trainer, TrainingArguments, DataCollatorWithPadding
)
from datasets import Dataset
from typing import Dict, List, Tuple, Any, Optional
import numpy as np


# Exercise 1: Basic tokenization
def tokenize_text(text: str, model_name: str = "bert-base-uncased") -> Dict[str, Any]:
    """Tokenize text using a pre-trained tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Tokenize
    tokens = tokenizer.tokenize(text)

    # Full encoding
    encoding = tokenizer(text, return_tensors="pt")

    return {
        'tokens': tokens,
        'input_ids': encoding['input_ids'].squeeze().tolist(),
        'attention_mask': encoding['attention_mask'].squeeze().tolist(),
    }


# Exercise 2: Batch tokenization
def tokenize_batch(
    texts: List[str],
    model_name: str = "bert-base-uncased",
    max_length: int = 512
) -> Dict[str, torch.Tensor]:
    """Tokenize a batch of texts with padding and truncation."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    encoding = tokenizer(
        texts,
        padding="max_length",
        truncation=True,
        max_length=max_length,
        return_tensors="pt"
    )

    return {
        'input_ids': encoding['input_ids'],
        'attention_mask': encoding['attention_mask'],
    }


# Exercise 3: Text classification pipeline
def classify_texts(
    texts: List[str],
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
) -> List[Dict[str, Any]]:
    """Classify texts using a pre-trained classification model."""
    classifier = pipeline("text-classification", model=model_name)
    results = classifier(texts)
    return results


# Exercise 4: Extract embeddings
def get_embeddings(
    texts: List[str],
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> torch.Tensor:
    """Extract embeddings from texts using a pre-trained model."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Tokenize
    encoded = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

    # Get embeddings
    with torch.no_grad():
        outputs = model(**encoded)
        embeddings = outputs.last_hidden_state

    # Mean pooling
    attention_mask = encoded['attention_mask']
    mask_expanded = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
    sum_embeddings = (embeddings * mask_expanded).sum(1)
    sum_mask = mask_expanded.sum(1)
    embeddings = sum_embeddings / sum_mask

    return embeddings


# Exercise 5: Text generation
def generate_text(
    prompt: str,
    model_name: str = "gpt2",
    max_length: int = 50,
    num_sequences: int = 1
) -> List[str]:
    """Generate text continuation using a pre-trained language model."""
    generator = pipeline("text-generation", model=model_name)

    results = generator(
        prompt,
        max_length=max_length,
        num_return_sequences=num_sequences,
        do_sample=True,
        top_p=0.95,
        temperature=0.7
    )

    return [result['generated_text'] for result in results]


# Exercise 6: Summarization
def summarize_text(
    text: str,
    model_name: str = "facebook/bart-large-cnn",
    max_length: int = 100,
    min_length: int = 30
) -> str:
    """Summarize a long text using a pre-trained summarization model."""
    summarizer = pipeline("summarization", model=model_name)

    # Split long text into chunks if needed
    max_chunk_length = 1024
    if len(text) > max_chunk_length:
        text = text[:max_chunk_length]

    result = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return result[0]['summary_text']


# Exercise 7: Zero-shot classification
def zero_shot_classify(
    text: str,
    candidate_labels: List[str],
    model_name: str = "facebook/bart-large-mnli"
) -> Dict[str, Any]:
    """Classify text into arbitrary categories without fine-tuning."""
    classifier = pipeline("zero-shot-classification", model=model_name)

    result = classifier(text, candidate_labels)

    return {
        'labels': result['labels'],
        'scores': result['scores'],
        'sequence': result['sequence']
    }


# Exercise 8: Question answering
def answer_question(
    question: str,
    context: str,
    model_name: str = "distilbert-base-cased-distilled-squad"
) -> Dict[str, Any]:
    """Answer a question given context using a pre-trained QA model."""
    qa_pipeline = pipeline("question-answering", model=model_name)

    result = qa_pipeline(question=question, context=context)

    return {
        'answer': result['answer'],
        'score': result['score'],
        'start': result['start'],
        'end': result['end']
    }


# Exercise 9: Named entity recognition
def extract_entities(
    text: str,
    model_name: str = "dslim/bert-base-NER"
) -> List[Dict[str, Any]]:
    """Extract named entities from text."""
    ner = pipeline("ner", model=model_name)
    entities = ner(text)
    return entities


# Exercise 10: Create a custom dataset
def create_custom_dataset(
    texts: List[str],
    labels: List[int]
) -> Dataset:
    """Create a Hugging Face Dataset from texts and labels."""
    data = {
        'text': texts,
        'label': labels
    }
    dataset = Dataset.from_dict(data)
    return dataset


# Exercise 11: Fine-tune with Trainer
def fine_tune_classifier(
    train_texts: List[str],
    train_labels: List[int],
    val_texts: List[str],
    val_labels: List[int],
    model_name: str = "distilbert-base-uncased",
    num_epochs: int = 3,
    batch_size: int = 8,
    output_dir: str = "./results"
) -> Dict[str, Any]:
    """Fine-tune a text classification model using the Trainer API."""
    # Create datasets
    train_dataset = create_custom_dataset(train_texts, train_labels)
    val_dataset = create_custom_dataset(val_texts, val_labels)

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2
    )

    # Tokenize datasets
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512
        )

    train_dataset = train_dataset.map(tokenize_function, batched=True)
    val_dataset = val_dataset.map(tokenize_function, batched=True)

    # Set format
    train_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])
    val_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        warmup_steps=100,
        weight_decay=0.01,
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    # Data collator
    data_collator = DataCollatorWithPadding(tokenizer)

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )

    # Train
    trainer.train()

    # Save model
    trainer.save_model(f"{output_dir}/final_model")

    # Get metrics
    metrics = trainer.evaluate()

    return {
        'model_path': f"{output_dir}/final_model",
        'metrics': metrics
    }


# Exercise 12: Model inference and post-processing
def predict_with_confidence(
    texts: List[str],
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english",
    confidence_threshold: float = 0.8
) -> List[Dict[str, Any]]:
    """Make predictions and filter by confidence threshold."""
    classifier = pipeline("text-classification", model=model_name)
    results = classifier(texts)

    filtered_results = []
    for text, result in zip(texts, results):
        confidence = result['score']
        if confidence >= confidence_threshold:
            filtered_results.append({
                'text': text,
                'label': result['label'],
                'score': confidence
            })

    return filtered_results


# Helper functions for testing
def create_sample_texts() -> Tuple[List[str], List[int]]:
    """Create sample texts and labels for testing."""
    texts = [
        "This movie is absolutely fantastic!",
        "I really hated this film.",
        "It was okay, nothing special.",
        "Best movie I've ever seen!",
        "Terrible waste of time.",
    ]
    labels = [1, 0, 0, 1, 0]
    return texts, labels


def create_sample_qa_data() -> Tuple[str, str, str]:
    """Create sample QA data for testing."""
    context = """
    Machine learning is a type of artificial intelligence that enables
    computers to learn from data without being explicitly programmed.
    Deep learning is a subset of machine learning that uses neural networks
    with multiple layers. Transformers are a type of neural network architecture
    introduced in the "Attention is All You Need" paper.
    """
    questions = [
        "What is machine learning?",
        "What are transformers?",
        "Who invented transformers?"
    ]
    return context, questions[0], questions[1]
