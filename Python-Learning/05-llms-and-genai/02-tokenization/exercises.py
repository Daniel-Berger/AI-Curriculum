"""
Module 02: Tokenization — Exercises
====================================

12 exercises on tokenization, byte-pair encoding (BPE), tiktoken, and token counting.

Topics:
- Character and subword tokenization
- Byte-Pair Encoding (BPE) algorithm
- Vocabulary construction
- Token counting with tiktoken
- Edge cases (whitespace, special tokens, Unicode)

Run this file directly to check your solutions:
    python exercises.py
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Exercise 1: Basic Character Tokenization
# ---------------------------------------------------------------------------
def char_tokenize(text: str) -> list[int]:
    """
    Convert text to character-level tokens using Unicode code points.

    Each character becomes its Unicode code point integer.
    Return the list of integer token IDs.

    Args:
        text: Input string

    Returns:
        List of integers representing character tokens
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Character Tokenizer to String
# ---------------------------------------------------------------------------
def char_detokenize(tokens: list[int]) -> str:
    """
    Convert character-level tokens back to text.

    Inverse of char_tokenize: convert code points back to characters.

    Args:
        tokens: List of integer character tokens

    Returns:
        Original string
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Simple Word Tokenization
# ---------------------------------------------------------------------------
def word_tokenize(text: str) -> list[str]:
    """
    Split text into words using whitespace and punctuation.

    Use a simple regex to split on word boundaries.
    Regex pattern: r'\w+' matches sequences of word characters.

    Args:
        text: Input string

    Returns:
        List of word tokens (strings)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Build Vocabulary from Corpus
# ---------------------------------------------------------------------------
def build_vocab(texts: list[str], max_vocab_size: int = 1000) -> dict[str, int]:
    """
    Build a vocabulary (token -> token_id mapping) from a list of texts.

    Tokenize using word_tokenize, count frequencies, and create a mapping.
    Assign token IDs in order of frequency (most frequent = lowest ID).
    Include a special token for unknown words at ID 0.

    Args:
        texts: List of text strings
        max_vocab_size: Maximum vocabulary size (including special token)

    Returns:
        Dictionary mapping token strings to integer IDs
        Special token '<unk>' should be at ID 0
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: BPE - Initial Byte Pair Frequencies
# ---------------------------------------------------------------------------
def get_byte_pair_freqs(tokens: list[int]) -> dict[tuple[int, int], int]:
    """
    Count the frequency of adjacent token pairs in a token sequence.

    For example, if tokens = [1, 2, 2, 3, 2]:
    Adjacent pairs: (1, 2), (2, 2), (2, 3), (3, 2)

    Args:
        tokens: List of token IDs

    Returns:
        Dictionary mapping (token1, token2) tuples to their frequency
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: BPE - Merge Most Frequent Pair
# ---------------------------------------------------------------------------
def merge_pair(
    tokens: list[int],
    pair: tuple[int, int],
    new_token_id: int,
) -> list[int]:
    """
    Merge all occurrences of a token pair into a new token.

    Replace all instances of (pair[0], pair[1]) with new_token_id.

    Args:
        tokens: List of token IDs
        pair: Tuple of two token IDs to merge
        new_token_id: The new token ID to replace the pair

    Returns:
        New token list with the pair merged
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Full BPE Encoding (Simplified)
# ---------------------------------------------------------------------------
def bpe_encode(
    text: str,
    vocab_size: int = 256,
    num_merges: int = 100,
) -> dict[str, int]:
    """
    Perform simplified BPE encoding on text.

    1. Start with character-level tokens (token ID = character code point)
    2. Repeatedly merge the most frequent adjacent pair
    3. Continue for num_merges iterations
    4. Return the final vocabulary (byte/subword -> token ID)

    Args:
        text: Input text
        vocab_size: Starting vocabulary size (typically 256 for bytes)
        num_merges: Number of merge operations to perform

    Returns:
        Dictionary mapping subword strings to token IDs
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Token Count Estimation
# ---------------------------------------------------------------------------
def estimate_token_count(
    text: str,
    avg_chars_per_token: float = 4.0,
) -> int:
    """
    Estimate the number of tokens in text using a rough heuristic.

    Rule of thumb: 1 token ≈ 4 characters on average for English.
    (More precise: OpenAI's GPT models use ~1.3 tokens per word, or ~4 chars/token)

    Args:
        text: Input text
        avg_chars_per_token: Average characters per token (default 4.0)

    Returns:
        Estimated number of tokens (as integer)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Special Token Handling
# ---------------------------------------------------------------------------
def add_special_tokens(
    vocab: dict[str, int],
    special_tokens: list[str],
) -> dict[str, int]:
    """
    Add special tokens to vocabulary (e.g., <pad>, <eos>, <bos>).

    Assign them IDs after the existing vocabulary.

    Args:
        vocab: Existing vocabulary dictionary
        special_tokens: List of special token strings (e.g., ['<pad>', '<eos>'])

    Returns:
        Extended vocabulary with special tokens at the end
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Token Rate Across Languages
# ---------------------------------------------------------------------------
def compare_token_rates() -> dict[str, float]:
    """
    Return estimated tokens-per-word ratios for different languages.

    Use these approximate values:
    - 'English': 1.3 (most efficient)
    - 'French': 1.4
    - 'Spanish': 1.35
    - 'German': 1.5 (longer words)
    - 'Japanese': 1.0 (uses subword units naturally)
    - 'Chinese': 1.1 (character-based, maps well to subword units)
    - 'Korean': 1.2 (uses Hangul syllables)

    Returns:
        Dictionary mapping language name to tokens-per-word ratio
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Whitespace Handling in Tokenization
# ---------------------------------------------------------------------------
def tokenize_with_spaces(text: str) -> list[str]:
    """
    Tokenize text while preserving information about spaces.

    Use a pattern that captures both words and spaces.
    Return list of tokens where spaces might be explicit.

    Example:
        "hello world" -> ['hello', ' world']  (space as prefix to second token)

    Args:
        text: Input string

    Returns:
        List of word tokens with space handling
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Token Efficiency Ranking
# ---------------------------------------------------------------------------
def rank_models_by_efficiency(
    model_token_counts: dict[str, int],
    text: str,
) -> list[tuple[str, int]]:
    """
    Given actual token counts from different models on the same text,
    rank them from most efficient (fewest tokens) to least.

    Args:
        model_token_counts: Dictionary mapping model name to token count
        text: The text that was tokenized

    Returns:
        List of (model_name, token_count) tuples, sorted by token count (ascending)
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1: char_tokenize
    tokens = char_tokenize('hello')
    assert isinstance(tokens, list) and len(tokens) > 0

    # Test Exercise 2: char_detokenize
    original = char_detokenize(char_tokenize('world'))
    assert original == 'world'

    # Test Exercise 3: word_tokenize
    words = word_tokenize('hello world test')
    assert 'hello' in words

    # Test Exercise 4: build_vocab
    vocab = build_vocab(['hello world', 'world test'], max_vocab_size=10)
    assert isinstance(vocab, dict)
    assert '<unk>' in vocab

    # Test Exercise 5: get_byte_pair_freqs
    freqs = get_byte_pair_freqs([1, 2, 2, 3, 2])
    assert isinstance(freqs, dict)

    # Test Exercise 6: merge_pair
    merged = merge_pair([1, 2, 2, 3], (2, 2), 4)
    assert 4 in merged

    # Test Exercise 8: estimate_token_count
    count = estimate_token_count('hello world test')
    assert count > 0

    # Test Exercise 9: add_special_tokens
    vocab = {'hello': 1, 'world': 2}
    extended = add_special_tokens(vocab, ['<pad>', '<eos>'])
    assert '<pad>' in extended

    # Test Exercise 10: compare_token_rates
    rates = compare_token_rates()
    assert 'English' in rates and isinstance(rates['English'], float)

    # Test Exercise 11: tokenize_with_spaces
    tokens = tokenize_with_spaces('hello world')
    assert isinstance(tokens, list) and len(tokens) > 0

    # Test Exercise 12: rank_models_by_efficiency
    model_counts = {'GPT-3': 100, 'Claude': 95, 'Llama': 110}
    ranked = rank_models_by_efficiency(model_counts, 'test text')
    assert ranked[0][1] <= ranked[-1][1]

    print('All tests passed!')
