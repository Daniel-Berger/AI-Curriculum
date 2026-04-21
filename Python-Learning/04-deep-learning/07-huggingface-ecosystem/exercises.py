"""
Exercises for Hugging Face Ecosystem.

Practice using transformers, tokenizers, pipelines, and the Trainer API.
"""

import torch
from typing import Dict, List, Tuple, Any, Optional
from datasets import Dataset


# Exercise 1: Basic tokenization
def tokenize_text(text: str, model_name: str = "bert-base-uncased") -> Dict[str, Any]:
    """
    Tokenize text using a pre-trained tokenizer.

    Args:
        text: Input text to tokenize
        model_name: Name of the model/tokenizer on Hugging Face Hub

    Returns:
        Dictionary with 'tokens' and 'input_ids' keys
    """
    pass


# Exercise 2: Batch tokenization
def tokenize_batch(
    texts: List[str],
    model_name: str = "bert-base-uncased",
    max_length: int = 512
) -> Dict[str, torch.Tensor]:
    """
    Tokenize a batch of texts with padding and truncation.

    Args:
        texts: List of input texts
        model_name: Model name on Hub
        max_length: Maximum sequence length

    Returns:
        Dictionary with 'input_ids' and 'attention_mask' tensors
    """
    pass


# Exercise 3: Text classification pipeline
def classify_texts(
    texts: List[str],
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
) -> List[Dict[str, Any]]:
    """
    Classify texts using a pre-trained classification model.

    Args:
        texts: List of texts to classify
        model_name: Pre-trained model on Hub

    Returns:
        List of classification results with 'label' and 'score'
    """
    pass


# Exercise 4: Extract embeddings
def get_embeddings(
    texts: List[str],
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> torch.Tensor:
    """
    Extract embeddings from texts using a pre-trained model.

    Args:
        texts: List of texts
        model_name: Model name (preferably sentence-transformers)

    Returns:
        Tensor of embeddings with shape (num_texts, embedding_dim)
    """
    pass


# Exercise 5: Text generation
def generate_text(
    prompt: str,
    model_name: str = "gpt2",
    max_length: int = 50,
    num_sequences: int = 1
) -> List[str]:
    """
    Generate text continuation using a pre-trained language model.

    Args:
        prompt: Starting text
        model_name: Model name on Hub
        max_length: Maximum generation length
        num_sequences: Number of sequences to generate

    Returns:
        List of generated text sequences
    """
    pass


# Exercise 6: Summarization
def summarize_text(
    text: str,
    model_name: str = "facebook/bart-large-cnn",
    max_length: int = 100,
    min_length: int = 30
) -> str:
    """
    Summarize a long text using a pre-trained summarization model.

    Args:
        text: Long text to summarize
        model_name: Model name on Hub
        max_length: Maximum summary length
        min_length: Minimum summary length

    Returns:
        Summary text
    """
    pass


# Exercise 7: Zero-shot classification
def zero_shot_classify(
    text: str,
    candidate_labels: List[str],
    model_name: str = "facebook/bart-large-mnli"
) -> Dict[str, Any]:
    """
    Classify text into arbitrary categories without fine-tuning.

    Args:
        text: Input text
        candidate_labels: List of possible categories
        model_name: Model name on Hub

    Returns:
        Dictionary with 'labels' and 'scores' (sorted by score)
    """
    pass


# Exercise 8: Question answering
def answer_question(
    question: str,
    context: str,
    model_name: str = "distilbert-base-cased-distilled-squad"
) -> Dict[str, Any]:
    """
    Answer a question given context using a pre-trained QA model.

    Args:
        question: Question to answer
        context: Context containing the answer
        model_name: Model name on Hub

    Returns:
        Dictionary with 'answer', 'score', 'start', 'end'
    """
    pass


# Exercise 9: Named entity recognition
def extract_entities(
    text: str,
    model_name: str = "dslim/bert-base-NER"
) -> List[Dict[str, Any]]:
    """
    Extract named entities from text.

    Args:
        text: Input text
        model_name: NER model on Hub

    Returns:
        List of entities with 'entity', 'word', 'start', 'end', 'score'
    """
    pass


# Exercise 10: Create a custom dataset
def create_custom_dataset(
    texts: List[str],
    labels: List[int]
) -> Dataset:
    """
    Create a Hugging Face Dataset from texts and labels.

    Args:
        texts: List of text samples
        labels: List of corresponding labels

    Returns:
        Hugging Face Dataset object
    """
    pass


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
    """
    Fine-tune a text classification model using the Trainer API.

    Args:
        train_texts: Training texts
        train_labels: Training labels (0 or 1 for binary classification)
        val_texts: Validation texts
        val_labels: Validation labels
        model_name: Model to fine-tune
        num_epochs: Number of training epochs
        batch_size: Batch size
        output_dir: Directory to save results

    Returns:
        Dictionary with training metrics and model path
    """
    pass


# Exercise 12: Model inference and post-processing
def predict_with_confidence(
    texts: List[str],
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english",
    confidence_threshold: float = 0.8
) -> List[Dict[str, Any]]:
    """
    Make predictions and filter by confidence threshold.

    Args:
        texts: List of texts to classify
        model_name: Pre-trained model
        confidence_threshold: Only return predictions above this threshold

    Returns:
        List of high-confidence predictions with text, label, and score
    """
    pass


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
