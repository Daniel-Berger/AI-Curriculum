# Module 02: Tokenization — How Text Becomes Numbers

## Why Tokenization Matters

Neural networks operate on numbers, not text. Tokenization is the bridge between human language
and the numerical representations that models process. Every single interaction with an LLM --
every prompt, every response, every API call -- passes through a tokenizer. Understanding
tokenization is not optional; it directly affects:

- **Cost:** API pricing is per-token. Knowing how text tokenizes lets you estimate costs.
- **Context window:** Your 200K context window is measured in tokens, not characters or words.
- **Model behavior:** Tokenization artifacts affect how models handle numbers, code, and
  multilingual text.
- **Performance:** Some prompts are more token-efficient than others.

**Swift analogy:** Think of tokenization as analogous to `String.UTF8View` in Swift. Just as
Swift's `String` is a collection of `Character` values but is stored as UTF-8 bytes under the
hood, an LLM's "text" is really a sequence of token IDs under the hood. And just as
`.count` on a `String` gives characters while `.utf8.count` gives bytes (often different!),
word count and token count are different things.

---

## The Vocabulary Problem

### Why Not Characters?

The simplest approach: map each character to a number.

```python
text = "Hello, world!"
char_tokens = [ord(c) for c in text]
# [72, 101, 108, 108, 111, 44, 32, 119, 111, 114, 108, 100, 33]
# 13 tokens for 13 characters
```

**Problems with character-level tokenization:**
1. **Long sequences:** "Hello world" is 11 tokens. A document is tens of thousands.
   Self-attention is O(n^2), so longer sequences are exponentially more expensive.
2. **No semantic units:** The model must learn that 'c', 'a', 't' together mean something.
3. **Tiny vocabulary:** Only ~256 tokens (ASCII/UTF-8 bytes), so the embedding table is tiny
   but sequences are very long.

### Why Not Words?

Split on whitespace and punctuation, give each word a number.

```python
text = "Hello, world!"
word_tokens = ["Hello", ",", "world", "!"]
# 4 tokens — much shorter!
```

**Problems with word-level tokenization:**
1. **Huge vocabulary:** English has 170,000+ words. Add misspellings, names, technical terms,
   and you need millions of entries. The embedding matrix becomes enormous.
2. **Out-of-vocabulary (OOV):** What about "ChatGPT"? "iPhone15Pro"? "TensorFlow"?
   Any word not in the vocabulary becomes `<UNK>` (unknown).
3. **No morphological awareness:** "running", "runs", "runner" are three separate tokens with
   no shared representation, even though they share the root "run."
4. **Multilingual nightmare:** Chinese, Japanese, Arabic — word boundaries are not marked by
   spaces.

### The Subword Sweet Spot

Subword tokenization splits text into pieces that are between characters and words:

```python
text = "unhappiness"
subword_tokens = ["un", "happiness"]  # or ["un", "happi", "ness"]
```

**Benefits:**
- Moderate vocabulary size (32K-100K tokens)
- No OOV problem — any text can be encoded by falling back to smaller pieces
- Common words stay as single tokens ("the" = 1 token)
- Rare words are split into meaningful subwords ("tokenization" → "token" + "ization")
- Compact sequences (shorter than character-level)

---

## Byte Pair Encoding (BPE)

BPE is the most common subword tokenization algorithm. Used by GPT-2, GPT-3, GPT-4, Llama, and
(with modifications) most modern LLMs.

### The BPE Training Algorithm

BPE starts with a character-level vocabulary and iteratively merges the most frequent pair.

**Step-by-step example:**

```
Training corpus: "low low low low low lower lower newest newest newest widest"

Step 0: Initialize with character vocabulary
  Vocabulary: {l, o, w, e, r, n, s, t, i, d, ' '}
  Word frequencies: low(5), lower(2), newest(3), widest(1)
  Initial encoding: l·o·w, l·o·w·e·r, n·e·w·e·s·t, w·i·d·e·s·t

Step 1: Count all adjacent pairs
  (l, o): 7    ← most frequent
  (o, w): 7
  (w, e): 5
  (e, r): 2
  (e, s): 4
  (s, t): 4
  (n, e): 3
  ...

Step 2: Merge most frequent pair (l, o) → "lo"
  Vocabulary: {l, o, w, e, r, n, s, t, i, d, ' ', lo}
  Encoding: lo·w, lo·w·e·r, n·e·w·e·s·t, w·i·d·e·s·t

Step 3: Recount pairs, merge (lo, w) → "low"
  Vocabulary: {..., lo, low}
  Encoding: low, low·e·r, n·e·w·e·s·t, w·i·d·e·s·t

Step 4: Merge (e, s) → "es"
  Vocabulary: {..., low, es}
  Encoding: low, low·e·r, n·e·w·es·t, w·i·d·es·t

Step 5: Merge (es, t) → "est"
  Vocabulary: {..., low, es, est}
  Encoding: low, low·e·r, n·e·w·est, w·i·d·est

... continue until desired vocabulary size is reached
```

### BPE Encoding (Inference Time)

Once trained, encoding new text applies the learned merges in priority order:

```python
def bpe_encode(text, merges):
    """
    Apply BPE merges to encode text.

    1. Split text into individual characters (or bytes)
    2. Repeatedly apply the highest-priority merge that exists in the sequence
    3. Stop when no more merges can be applied
    """
    tokens = list(text)  # Start with characters

    for merge_pair in merges:  # merges are ordered by training frequency
        i = 0
        new_tokens = []
        while i < len(tokens):
            # Look for the merge pair at position i
            if i < len(tokens) - 1 and (tokens[i], tokens[i + 1]) == merge_pair:
                new_tokens.append(tokens[i] + tokens[i + 1])
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        tokens = new_tokens

    return tokens
```

### Byte-Level BPE

Modern BPE (as used in GPT-2+) operates on **bytes** rather than Unicode characters. This
ensures every possible input can be encoded (no OOV, ever) since any text is a sequence of bytes.

```python
text = "Hello"
bytes_representation = text.encode('utf-8')  # b'Hello'
byte_tokens = list(bytes_representation)  # [72, 101, 108, 108, 111]
```

GPT-2 added a clever trick: map each byte (0-255) to a printable Unicode character so the
vocabulary is human-readable. This is why you sometimes see `Ġ` (represents a space byte)
in GPT tokenizer outputs.

---

## SentencePiece

Developed by Google, SentencePiece is a language-agnostic tokenizer that operates directly on
raw text (no pre-tokenization needed). Used by Llama, T5, and many multilingual models.

### Key Differences from Standard BPE

| Feature            | Standard BPE (GPT)          | SentencePiece               |
|--------------------|-----------------------------|-----------------------------|
| Pre-tokenization   | Splits on spaces first      | Treats input as raw stream  |
| Space handling      | Space is a separator        | Space is a token (`▁`)     |
| Language support    | Needs pre-tokenization rules| Language-agnostic           |
| Training input      | Pre-tokenized words         | Raw text                    |

### The Unigram Model (SentencePiece's Default)

Unlike BPE which builds up from characters, the Unigram model starts with a large vocabulary
and prunes it down:

```
1. Start with a large initial vocabulary (all substrings up to a length limit)
2. Compute the loss (negative log-likelihood) of the training corpus
3. For each vocabulary item, compute how much the loss would increase if removed
4. Remove the items that increase loss the least (keeping a desired percentage)
5. Repeat steps 2-4 until desired vocabulary size is reached
```

**Key property:** The Unigram model assigns a probability to each token and finds the most
probable segmentation of the input using the Viterbi algorithm.

```python
# SentencePiece treats spaces as part of tokens
import sentencepiece as spm

# Training
spm.SentencePieceTrainer.train(
    input='corpus.txt',
    model_prefix='my_tokenizer',
    vocab_size=32000,
    model_type='unigram',  # or 'bpe'
)

# Encoding
sp = spm.SentencePieceProcessor()
sp.load('my_tokenizer.model')

tokens = sp.encode_as_pieces("Hello world")
# ['▁Hello', '▁world']  — note the ▁ (underscore) represents spaces

ids = sp.encode_as_ids("Hello world")
# [8774, 296]
```

---

## WordPiece

Used by BERT and related encoder models. Similar to BPE but with a different merge criterion.

### BPE vs. WordPiece Merge Criterion

```
BPE:       Choose pair with highest COUNT
           merge("t", "h") if "th" appears most often

WordPiece: Choose pair that maximizes LIKELIHOOD
           score(a, b) = count(ab) / (count(a) * count(b))
           Prefers merges that create meaningful units
```

WordPiece uses the `##` prefix to indicate continuation tokens:

```python
# BERT tokenizer example
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
tokens = tokenizer.tokenize("unhappiness")
# ['un', '##happiness']  — ## means "continuation of previous token"
```

---

## tiktoken: OpenAI's Fast BPE Tokenizer

tiktoken is OpenAI's open-source tokenizer implementation. It's extremely fast (written in Rust
with Python bindings) and is the standard way to count tokens for OpenAI API calls.

### Installation and Basic Usage

```python
import tiktoken

# Get the tokenizer for a specific model
enc = tiktoken.encoding_for_model("gpt-4")
# Or by encoding name directly
enc = tiktoken.get_encoding("cl100k_base")  # GPT-4, GPT-3.5-turbo

# Encode text to token IDs
text = "Hello, how are you?"
token_ids = enc.encode(text)
print(token_ids)       # [9906, 11, 1268, 527, 499, 30]
print(len(token_ids))  # 6 tokens

# Decode back to text
decoded = enc.decode(token_ids)
print(decoded)         # "Hello, how are you?"

# Decode individual tokens to see what each one represents
for tid in token_ids:
    print(f"  {tid} → {enc.decode([tid])!r}")
# 9906 → 'Hello'
# 11   → ','
# 1268 → ' how'
# 527  → ' are'
# 499  → ' you'
# 30   → '?'
```

### OpenAI Encoding Names

| Encoding Name    | Models                        | Vocab Size |
|------------------|-------------------------------|------------|
| `cl100k_base`    | GPT-4, GPT-3.5-turbo         | ~100,000   |
| `o200k_base`     | GPT-4o, o1                    | ~200,000   |
| `p50k_base`      | text-davinci-002/003          | ~50,000    |
| `r50k_base`      | GPT-2, davinci (original)     | ~50,000    |

### Counting Tokens for API Calls

```python
import tiktoken


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens for a given model."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


def estimate_cost(
    prompt: str,
    completion: str,
    model: str = "gpt-4",
    input_cost_per_1k: float = 0.03,
    output_cost_per_1k: float = 0.06,
) -> dict:
    """Estimate API call cost."""
    enc = tiktoken.encoding_for_model(model)
    prompt_tokens = len(enc.encode(prompt))
    completion_tokens = len(enc.encode(completion))

    return {
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'total_tokens': prompt_tokens + completion_tokens,
        'estimated_cost': (
            prompt_tokens / 1000 * input_cost_per_1k +
            completion_tokens / 1000 * output_cost_per_1k
        ),
    }
```

---

## Comparing Tokenizers Across Models

Different models tokenize the same text differently, which affects token counts and costs.

```python
import tiktoken

text = "Tokenization is fascinating! Let's count: 1234567890"

# GPT-4 (cl100k_base)
enc_gpt4 = tiktoken.get_encoding("cl100k_base")
gpt4_tokens = enc_gpt4.encode(text)
print(f"GPT-4: {len(gpt4_tokens)} tokens")

# GPT-4o (o200k_base)
enc_gpt4o = tiktoken.get_encoding("o200k_base")
gpt4o_tokens = enc_gpt4o.encode(text)
print(f"GPT-4o: {len(gpt4o_tokens)} tokens")

# Examine individual tokens
print("\nGPT-4 token breakdown:")
for tid in gpt4_tokens:
    print(f"  {tid:6d} → {enc_gpt4.decode([tid])!r}")
```

### Cross-Model Token Count Comparison

```python
def compare_tokenizers(text: str) -> dict[str, int]:
    """Compare token counts across different encodings."""
    encodings = {
        'GPT-4 (cl100k)': 'cl100k_base',
        'GPT-4o (o200k)': 'o200k_base',
    }

    results = {}
    for name, encoding_name in encodings.items():
        enc = tiktoken.get_encoding(encoding_name)
        tokens = enc.encode(text)
        results[name] = len(tokens)

    return results
```

### Using Hugging Face Tokenizers for Open Models

```python
from transformers import AutoTokenizer

# Load Llama tokenizer
llama_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
tokens = llama_tokenizer.encode("Hello, world!")
print(f"Llama 2: {len(tokens)} tokens")
print(f"Tokens: {llama_tokenizer.convert_ids_to_tokens(tokens)}")

# Load Mistral tokenizer
mistral_tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
tokens = mistral_tokenizer.encode("Hello, world!")
print(f"Mistral: {len(tokens)} tokens")
```

---

## Token Economics

Understanding tokenization is directly tied to cost management when using LLM APIs.

### Pricing Breakdown (Approximate, 2024-2025)

```
Model              Input (per 1M tokens)    Output (per 1M tokens)
GPT-4o             $2.50                    $10.00
GPT-4 Turbo        $10.00                   $30.00
Claude 3.5 Sonnet   $3.00                    $15.00
Claude 3 Opus      $15.00                   $75.00
Llama 3 (hosted)   $0.20-2.00               $0.20-2.00
```

### Token-to-Word Ratio

A rough rule of thumb: **1 token ≈ 0.75 words** (or **1 word ≈ 1.33 tokens**) for English.

```python
import tiktoken


def tokens_per_word(text: str, encoding_name: str = "cl100k_base") -> float:
    """Calculate the average tokens per word for a text."""
    enc = tiktoken.get_encoding(encoding_name)
    num_tokens = len(enc.encode(text))
    num_words = len(text.split())
    return round(num_tokens / num_words, 2)


# English text: typically 1.2-1.5 tokens per word
english = "The quick brown fox jumps over the lazy dog."
print(f"English: {tokens_per_word(english)} tokens/word")

# Code: often more tokens per "word"
code = "def calculate_fibonacci(n: int) -> list[int]:"
print(f"Code: {tokens_per_word(code)} tokens/word")

# Numbers: surprisingly token-heavy
numbers = "123456789 987654321 111222333"
print(f"Numbers: {tokens_per_word(numbers)} tokens/word")
```

### Context Window Usage

```python
import tiktoken


def context_usage_report(
    system_prompt: str,
    user_messages: list[str],
    max_context: int = 128000,
    encoding_name: str = "cl100k_base",
) -> dict:
    """Report on context window usage."""
    enc = tiktoken.get_encoding(encoding_name)

    system_tokens = len(enc.encode(system_prompt))
    message_tokens = sum(len(enc.encode(msg)) for msg in user_messages)
    total_used = system_tokens + message_tokens
    remaining = max_context - total_used

    return {
        'system_prompt_tokens': system_tokens,
        'message_tokens': message_tokens,
        'total_used': total_used,
        'remaining': remaining,
        'usage_percent': round(total_used / max_context * 100, 1),
    }
```

---

## Tokenization Artifacts

Tokenization can cause surprising behavior. Understanding these artifacts helps you write
better prompts and debug model behavior.

### Numbers Are Not Atomic

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# Numbers get split unpredictably
print(enc.encode("123"))     # might be 1 token
print(enc.encode("12345"))   # might be 1-2 tokens
print(enc.encode("123456"))  # might be 2-3 tokens

# This is why LLMs struggle with arithmetic!
# "123 + 456" → the model sees fragments, not whole numbers
for num in ["42", "1000", "123456", "3.14159"]:
    tokens = enc.encode(num)
    parts = [enc.decode([t]) for t in tokens]
    print(f"  '{num}' → {len(tokens)} tokens: {parts}")
```

### Code Tokenization

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# Python code
code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""

tokens = enc.encode(code)
print(f"Code: {len(tokens)} tokens")

# Indentation uses tokens!
print(f"  4 spaces: {len(enc.encode('    '))} tokens")
print(f"  1 tab:    {len(enc.encode(chr(9)))} tokens")

# Variable names matter
print(f"  'x': {len(enc.encode('x'))} token")
print(f"  'calculate_fibonacci_sequence': "
      f"{len(enc.encode('calculate_fibonacci_sequence'))} tokens")
```

### Multilingual Tokenization

English-centric tokenizers are inefficient for other languages:

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

texts = {
    "English": "Hello, how are you?",
    "Spanish": "Hola, como estas?",
    "Chinese": "你好，你好吗？",
    "Japanese": "こんにちは、お元気ですか？",
    "Arabic": "مرحبا، كيف حالك؟",
    "Korean": "안녕하세요, 어떻게 지내세요?",
}

for lang, text in texts.items():
    tokens = enc.encode(text)
    ratio = len(tokens) / len(text)
    print(f"  {lang:10s}: {len(text):3d} chars → {len(tokens):3d} tokens "
          f"(ratio: {ratio:.2f})")
```

**Why this happens:** BPE training data is predominantly English, so English subwords get
single tokens while other scripts need multiple tokens per character.

### Leading Spaces

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# A space before a word changes tokenization!
print(enc.encode("hello"))    # different from...
print(enc.encode(" hello"))   # this (space is merged with 'hello')
```

---

## Special Tokens

Special tokens are reserved tokens with specific meaning to the model. They are NOT part of
the normal text vocabulary.

### Common Special Tokens

| Token              | Used By     | Purpose                                |
|--------------------|-------------|----------------------------------------|
| `<\|endoftext\|>`  | GPT models  | Marks end of a document/sequence       |
| `[CLS]`            | BERT        | Classification token (start of input)  |
| `[SEP]`            | BERT        | Separator between segments             |
| `[MASK]`           | BERT        | Masked position for prediction         |
| `<s>`, `</s>`      | Llama, T5   | Beginning/end of sequence              |
| `[INST]`, `[/INST]`| Llama 2     | Instruction delimiters                 |
| `<\|im_start\|>`   | ChatML      | Start of a message                     |
| `<\|im_end\|>`     | ChatML      | End of a message                       |

### How Special Tokens Work with tiktoken

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# Normal encoding does NOT include special tokens
text = "Hello world"
tokens = enc.encode(text)

# To include special tokens, use allowed_special
tokens_with_special = enc.encode(
    "<|endoftext|>Hello world",
    allowed_special={"<|endoftext|>"}
)
print(f"With special token: {tokens_with_special}")
# The special token gets its own ID, separate from normal tokens

# Trying to encode special tokens without allowing them raises an error
try:
    enc.encode("<|endoftext|>")
except Exception as e:
    print(f"Error: {e}")
```

### Chat Template Tokens

Modern chat models use special tokens to structure conversations:

```
# GPT-4 / ChatML format:
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
What is Python?<|im_end|>
<|im_start|>assistant
Python is a programming language...<|im_end|>

# Llama 2 format:
<s>[INST] <<SYS>>
You are a helpful assistant.
<</SYS>>
What is Python? [/INST]
Python is a programming language... </s>

# Llama 3 format:
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a helpful assistant.<|eot_id|>
<|start_header_id|>user<|end_header_id|>
What is Python?<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
```

---

## Vocabulary Size Tradeoffs

### Small Vocabulary (e.g., 32K)

**Pros:**
- Smaller embedding matrix → less memory
- Simpler to train
- Works well for single-language models

**Cons:**
- Longer sequences (more tokens needed per text)
- Worse compression for diverse text

### Large Vocabulary (e.g., 200K)

**Pros:**
- Shorter sequences (better compression)
- Better multilingual support
- More "whole words" as single tokens

**Cons:**
- Larger embedding matrix
- Many rare tokens may be undertrained
- More memory for the embedding table

### Vocabulary Sizes by Model

| Model        | Vocab Size | Notes                                |
|--------------|------------|--------------------------------------|
| GPT-2        | 50,257     | Byte-level BPE                       |
| GPT-4        | ~100,000   | cl100k_base encoding                 |
| GPT-4o       | ~200,000   | o200k_base, better multilingual      |
| BERT         | 30,522     | WordPiece                            |
| Llama 2      | 32,000     | SentencePiece BPE                    |
| Llama 3      | 128,256    | Larger vocab, better multilingual    |
| Mistral      | 32,000     | SentencePiece BPE                    |

---

## Implementing BPE from Scratch

Here is a complete, minimal BPE implementation for understanding:

```python
from collections import Counter


def train_bpe(corpus: str, num_merges: int) -> tuple[dict, list]:
    """
    Train a simple BPE tokenizer.

    Args:
        corpus: Training text
        num_merges: Number of merge operations to learn

    Returns:
        Tuple of (vocabulary dict, list of merge rules)
    """
    # Step 1: Initialize with character-level tokens
    # Split corpus into words, represent each as characters with end-of-word marker
    words = corpus.split()
    word_freqs = Counter(words)

    # Represent each word as a tuple of characters
    splits = {}
    for word, freq in word_freqs.items():
        splits[word] = list(word)

    merges = []

    for i in range(num_merges):
        # Step 2: Count all adjacent pairs across the corpus
        pair_counts = Counter()
        for word, freq in word_freqs.items():
            chars = splits[word]
            for j in range(len(chars) - 1):
                pair = (chars[j], chars[j + 1])
                pair_counts[pair] += freq

        if not pair_counts:
            break

        # Step 3: Find the most frequent pair
        best_pair = pair_counts.most_common(1)[0][0]
        merges.append(best_pair)

        # Step 4: Merge that pair everywhere
        merged_token = best_pair[0] + best_pair[1]
        for word in splits:
            chars = splits[word]
            new_chars = []
            j = 0
            while j < len(chars):
                if (j < len(chars) - 1 and
                        chars[j] == best_pair[0] and
                        chars[j + 1] == best_pair[1]):
                    new_chars.append(merged_token)
                    j += 2
                else:
                    new_chars.append(chars[j])
                    j += 1
            splits[word] = new_chars

        print(f"Merge {i + 1}: {best_pair} → '{merged_token}'")

    # Build vocabulary
    vocab = set()
    for chars in splits.values():
        vocab.update(chars)

    return vocab, merges


def encode_bpe(text: str, merges: list[tuple[str, str]]) -> list[str]:
    """
    Encode text using learned BPE merges.
    """
    words = text.split()
    all_tokens = []

    for word in words:
        tokens = list(word)

        for pair in merges:
            new_tokens = []
            i = 0
            while i < len(tokens):
                if (i < len(tokens) - 1 and
                        tokens[i] == pair[0] and
                        tokens[i + 1] == pair[1]):
                    new_tokens.append(pair[0] + pair[1])
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            tokens = new_tokens

        all_tokens.extend(tokens)

    return all_tokens


# Example usage
corpus = "low low low low low lower lower newest newest newest widest"
vocab, merges = train_bpe(corpus, num_merges=10)
print(f"\nVocabulary: {sorted(vocab)}")
print(f"Merges: {merges}")

encoded = encode_bpe("low newest", merges)
print(f"\n'low newest' → {encoded}")
```

---

## Counting Tokens Programmatically

### For OpenAI Models (tiktoken)

```python
import tiktoken


def count_message_tokens(
    messages: list[dict],
    model: str = "gpt-4",
) -> int:
    """
    Count tokens for a list of chat messages.

    OpenAI's chat format adds overhead tokens for role names and formatting.
    This function accounts for that overhead.
    """
    enc = tiktoken.encoding_for_model(model)

    # Every message adds formatting tokens
    tokens_per_message = 3  # <|im_start|>{role}\n ... <|im_end|>\n
    tokens_per_name = 1     # if 'name' field is present

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(enc.encode(value))
            if key == "name":
                num_tokens += tokens_per_name

    num_tokens += 3  # every reply is primed with <|im_start|>assistant<|im_sep|>
    return num_tokens


# Example
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"},
]
print(f"Message tokens: {count_message_tokens(messages)}")
```

### For Anthropic Models

Anthropic does not publish a public tokenizer, but you can estimate:

```python
def estimate_claude_tokens(text: str) -> int:
    """
    Estimate token count for Claude models.

    Claude uses a proprietary tokenizer, but for English text,
    the ratio is roughly similar to tiktoken's cl100k_base.
    For precise counts, use the API's usage response.
    """
    # Rough estimate: ~4 characters per token for English
    return len(text) // 4


# After an API call, get actual usage:
# response.usage.input_tokens
# response.usage.output_tokens
```

---

## Tokenization Best Practices for LLM Development

### 1. Always Count Tokens Before API Calls

```python
import tiktoken


def check_fits_context(
    text: str,
    max_tokens: int = 128000,
    model: str = "gpt-4",
) -> tuple[bool, int]:
    """Check if text fits in the context window."""
    enc = tiktoken.encoding_for_model(model)
    token_count = len(enc.encode(text))
    return token_count <= max_tokens, token_count
```

### 2. Optimize Prompts for Token Efficiency

```python
# Verbose (more tokens, more cost):
prompt_verbose = """
Please take the following text and provide a comprehensive summary
of the main points discussed in the text. The summary should be
concise but cover all the important topics mentioned.
"""

# Concise (fewer tokens, same result):
prompt_concise = "Summarize the key points of this text:"

# Both work, but the concise version saves tokens (and money)
```

### 3. Be Aware of Tokenization When Working with Structured Data

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# JSON is relatively token-efficient
json_data = '{"name": "Alice", "age": 30}'
print(f"JSON: {len(enc.encode(json_data))} tokens")

# XML is token-heavy
xml_data = '<person><name>Alice</name><age>30</age></person>'
print(f"XML:  {len(enc.encode(xml_data))} tokens")

# Markdown tables are moderate
md_data = "| Name | Age |\n|------|-----|\n| Alice | 30 |"
print(f"MD:   {len(enc.encode(md_data))} tokens")
```

---

## Swift Developer's Perspective

| Tokenization Concept      | Swift Analogy                                    |
|---------------------------|--------------------------------------------------|
| Token                     | A `Character` in `String` (but not 1:1)         |
| Token ID                  | `Unicode.Scalar.value`                           |
| Vocabulary                | `CharacterSet` (but much larger)                 |
| Encoding                  | `String.utf8` / `String.utf16` conversion        |
| Special tokens            | Control characters (`\n`, `\0`, etc.)            |
| Subword tokenization      | Splitting a `String` at `CharacterSet` boundaries|
| Vocabulary size tradeoff  | UTF-8 (compact) vs UTF-32 (fixed-width)          |

---

## Summary

| Topic                     | Key Takeaway                                      |
|---------------------------|---------------------------------------------------|
| Why subwords              | Balance between vocabulary size and sequence length|
| BPE                       | Iteratively merge most frequent pairs             |
| SentencePiece             | Language-agnostic, raw text input, Unigram model  |
| WordPiece                 | BERT-style, uses likelihood-based merging         |
| tiktoken                  | Fast, use for counting OpenAI tokens              |
| Token economics           | ~1 token ≈ 0.75 words, pricing is per-token       |
| Artifacts                 | Numbers split oddly, multilingual is expensive    |
| Special tokens            | Reserved tokens for model control and formatting  |
| Vocab size                | 32K-200K; larger = shorter sequences, more memory |

Next module: **API Mastery** — putting tokenization knowledge to work with real API calls.
