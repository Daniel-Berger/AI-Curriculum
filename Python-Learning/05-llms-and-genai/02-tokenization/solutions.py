"""
Module 02: Tokenization — Solutions
====================================

Complete solutions for all 12 exercises on tokenization and BPE.
"""

import re
from typing import Optional
from collections import Counter, defaultdict


# ---------------------------------------------------------------------------
# Exercise 1: Basic Character Tokenization
# ---------------------------------------------------------------------------
def char_tokenize(text: str) -> list[int]:
    """
    Convert text to character-level tokens using Unicode code points.
    """
    return [ord(char) for char in text]


# ---------------------------------------------------------------------------
# Exercise 2: Character Tokenizer to String
# ---------------------------------------------------------------------------
def char_detokenize(tokens: list[int]) -> str:
    """
    Convert character-level tokens back to text.
    """
    return ''.join(chr(token) for token in tokens)


# ---------------------------------------------------------------------------
# Exercise 3: Simple Word Tokenization
# ---------------------------------------------------------------------------
def word_tokenize(text: str) -> list[str]:
    """
    Split text into words using whitespace and punctuation.
    """
    return re.findall(r'\w+', text.lower())


# ---------------------------------------------------------------------------
# Exercise 4: Build Vocabulary from Corpus
# ---------------------------------------------------------------------------
def build_vocab(texts: list[str], max_vocab_size: int = 1000) -> dict[str, int]:
    """
    Build a vocabulary from a list of texts.
    """
    # Tokenize all texts
    all_tokens = []
    for text in texts:
        all_tokens.extend(word_tokenize(text))

    # Count frequencies
    token_counts = Counter(all_tokens)

    # Sort by frequency (most frequent first)
    sorted_tokens = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)

    # Build vocab with special token
    vocab = {'<unk>': 0}
    token_id = 1

    for token, _ in sorted_tokens:
        if token_id >= max_vocab_size:
            break
        vocab[token] = token_id
        token_id += 1

    return vocab


# ---------------------------------------------------------------------------
# Exercise 5: BPE - Initial Byte Pair Frequencies
# ---------------------------------------------------------------------------
def get_byte_pair_freqs(tokens: list[int]) -> dict[tuple[int, int], int]:
    """
    Count the frequency of adjacent token pairs.
    """
    freqs = defaultdict(int)
    for i in range(len(tokens) - 1):
        pair = (tokens[i], tokens[i + 1])
        freqs[pair] += 1
    return dict(freqs)


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
    """
    result = []
    i = 0
    while i < len(tokens):
        if i < len(tokens) - 1 and (tokens[i], tokens[i + 1]) == pair:
            result.append(new_token_id)
            i += 2
        else:
            result.append(tokens[i])
            i += 1
    return result


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
    """
    # Start with character-level tokens
    tokens = char_tokenize(text)

    # Track merges: (token1, token2) -> new_token_id
    merges = {}
    next_token_id = vocab_size

    for _ in range(num_merges):
        # Find most frequent pair
        freqs = get_byte_pair_freqs(tokens)
        if not freqs:
            break

        most_frequent_pair = max(freqs.items(), key=lambda x: x[1])[0]

        # Merge the pair
        tokens = merge_pair(tokens, most_frequent_pair, next_token_id)
        merges[most_frequent_pair] = next_token_id
        next_token_id += 1

    # Build final vocabulary
    vocab = {}
    for i in range(vocab_size):
        vocab[chr(i)] = i

    for (pair, new_id) in merges.items():
        # Map the pair back to a subword representation
        left_repr = list(vocab.keys())[pair[0]] if pair[0] < len(vocab) else str(pair[0])
        right_repr = list(vocab.keys())[pair[1]] if pair[1] < len(vocab) else str(pair[1])
        vocab[left_repr + right_repr] = new_id

    return vocab


# ---------------------------------------------------------------------------
# Exercise 8: Token Count Estimation
# ---------------------------------------------------------------------------
def estimate_token_count(
    text: str,
    avg_chars_per_token: float = 4.0,
) -> int:
    """
    Estimate the number of tokens in text using a rough heuristic.
    """
    return max(1, int(len(text) / avg_chars_per_token))


# ---------------------------------------------------------------------------
# Exercise 9: Special Token Handling
# ---------------------------------------------------------------------------
def add_special_tokens(
    vocab: dict[str, int],
    special_tokens: list[str],
) -> dict[str, int]:
    """
    Add special tokens to vocabulary.
    """
    extended_vocab = vocab.copy()
    next_id = max(vocab.values()) + 1

    for token in special_tokens:
        extended_vocab[token] = next_id
        next_id += 1

    return extended_vocab


# ---------------------------------------------------------------------------
# Exercise 10: Token Rate Across Languages
# ---------------------------------------------------------------------------
def compare_token_rates() -> dict[str, float]:
    """
    Return estimated tokens-per-word ratios for different languages.
    """
    return {
        'English': 1.3,
        'French': 1.4,
        'Spanish': 1.35,
        'German': 1.5,
        'Japanese': 1.0,
        'Chinese': 1.1,
        'Korean': 1.2,
    }


# ---------------------------------------------------------------------------
# Exercise 11: Whitespace Handling in Tokenization
# ---------------------------------------------------------------------------
def tokenize_with_spaces(text: str) -> list[str]:
    """
    Tokenize text while preserving space information.
    """
    # Split on whitespace but keep track of spaces
    tokens = []
    current_token = ''

    for char in text:
        if char == ' ':
            if current_token:
                tokens.append(current_token)
                current_token = ''
            # Next word gets space prefix
        else:
            if not current_token and tokens and not tokens[-1].startswith(' '):
                current_token = ' '
            current_token += char

    if current_token:
        tokens.append(current_token)

    return tokens if tokens else ['']


# ---------------------------------------------------------------------------
# Exercise 12: Token Efficiency Ranking
# ---------------------------------------------------------------------------
def rank_models_by_efficiency(
    model_token_counts: dict[str, int],
    text: str,
) -> list[tuple[str, int]]:
    """
    Rank models from most efficient (fewest tokens) to least.
    """
    return sorted(model_token_counts.items(), key=lambda x: x[1])


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    tokens = char_tokenize('hello')
    assert tokens == [104, 101, 108, 108, 111]

    # Test Exercise 2
    assert char_detokenize([104, 101, 108, 108, 111]) == 'hello'

    # Test Exercise 3
    words = word_tokenize('hello world test')
    assert words == ['hello', 'world', 'test']

    # Test Exercise 4
    vocab = build_vocab(['hello world', 'world test'], max_vocab_size=10)
    assert '<unk>' in vocab
    assert 'world' in vocab

    # Test Exercise 5
    freqs = get_byte_pair_freqs([1, 2, 2, 3, 2])
    assert (2, 2) in freqs
    assert freqs[(2, 2)] == 1

    # Test Exercise 6
    merged = merge_pair([1, 2, 2, 3], (2, 2), 4)
    assert merged == [1, 4, 3]

    # Test Exercise 8
    count = estimate_token_count('hello world test')
    assert count > 0

    # Test Exercise 9
    vocab = {'hello': 1, 'world': 2}
    extended = add_special_tokens(vocab, ['<pad>', '<eos>'])
    assert '<pad>' in extended
    assert '<eos>' in extended

    # Test Exercise 10
    rates = compare_token_rates()
    assert 'English' in rates
    assert rates['English'] == 1.3

    # Test Exercise 11
    tokens = tokenize_with_spaces('hello world')
    assert isinstance(tokens, list)

    # Test Exercise 12
    model_counts = {'GPT-3': 100, 'Claude': 95, 'Llama': 110}
    ranked = rank_models_by_efficiency(model_counts, 'test text')
    assert ranked == [('Claude', 95), ('GPT-3', 100), ('Llama', 110)]

    print('All tests passed!')
