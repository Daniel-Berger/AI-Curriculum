# Module 05: Sequence Models (RNNs, LSTMs, GRUs)

## Introduction for Swift Developers

If you've worked with Core ML's sequence models or Apple's Natural Language framework,
you've been using the end product of the architectures we'll build here from scratch.
In iOS, `NLLanguageRecognizer` and `NLTagger` use sequence models internally -- now
you'll understand exactly how they process text one token at a time.

Think of a sequence model like reading a Swift string character by character: at each
position you have the current character plus everything you remember from before. That
"memory" is the key concept in this module.

**Important context**: Transformers (Module 06) have largely replaced RNNs for most
NLP tasks. However, understanding RNNs/LSTMs is crucial for:
- Interview preparation (frequently tested)
- Time-series applications where they're still competitive
- Understanding the historical progression that motivated attention mechanisms
- Edge deployment on devices with limited memory (smaller than transformers)

---

## 1. Sequential Data: Why Order Matters

### The Problem with Feedforward Networks

In previous modules, we treated each input independently. But many real-world signals
have a **temporal or sequential structure** where order matters:

| Domain | Sequential Data | Why Order Matters |
|--------|----------------|-------------------|
| Text | "The cat sat on the mat" | "cat sat" vs "sat cat" = different meaning |
| Time series | Stock prices, sensor data | Tomorrow depends on today |
| Audio | Speech waveforms | Phonemes form words in sequence |
| Code | Token sequences | `if x > 0:` requires seeing tokens in order |
| iOS events | Touch sequences, gestures | Swipe direction = ordered touch points |

```python
import torch
import torch.nn as nn

# A feedforward network sees each input independently
# It has NO concept of "what came before"
feedforward = nn.Linear(10, 5)

# These two sequences would produce the same outputs for each element:
seq_a = torch.randn(5, 10)  # 5 time steps, 10 features
seq_b = seq_a.flip(0)       # Same elements, reversed order

# Feedforward treats each row independently -- order is lost
out_a = feedforward(seq_a)  # Same elements...
out_b = feedforward(seq_b)  # ...just in different order
# out_a[0] == out_b[4], out_a[1] == out_b[3], etc.
# The network can't distinguish "cat sat" from "sat cat"
```

### What We Need: Memory

We need a network that:
1. Processes inputs **one step at a time** (like iterating over a Swift `Sequence`)
2. Maintains a **hidden state** (memory) that carries information forward
3. Updates that state at each step based on the new input AND the previous state

```
Swift analogy:
    var state = initialState
    for element in sequence {
        state = process(element, state)  // state carries forward
    }
    return state  // contains information about the entire sequence
```

---

## 2. Recurrent Neural Networks (RNNs)

### The Core Idea

An RNN processes a sequence one element at a time, maintaining a hidden state that
acts as memory. At each time step t:

```
h_t = tanh(W_hh * h_{t-1} + W_xh * x_t + b)
```

Where:
- `h_t` = hidden state at time t (the "memory")
- `h_{t-1}` = hidden state from previous time step
- `x_t` = input at time t
- `W_hh` = weight matrix for hidden-to-hidden connections
- `W_xh` = weight matrix for input-to-hidden connections
- `b` = bias

### RNN from Scratch

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleRNN(nn.Module):
    """A basic RNN cell implemented from scratch.

    Swift analogy: Think of this as a class with a mutable 'state'
    property that updates as you feed in elements from a sequence.
    """

    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.hidden_size = hidden_size
        # Two weight matrices: one for input, one for previous hidden state
        self.W_xh = nn.Linear(input_size, hidden_size)    # input -> hidden
        self.W_hh = nn.Linear(hidden_size, hidden_size)   # hidden -> hidden

    def forward(self, x: torch.Tensor, h: torch.Tensor | None = None) -> tuple[torch.Tensor, torch.Tensor]:
        """Process a sequence step by step.

        Args:
            x: Input tensor of shape (batch, seq_len, input_size)
            h: Initial hidden state of shape (batch, hidden_size)

        Returns:
            outputs: All hidden states, shape (batch, seq_len, hidden_size)
            h: Final hidden state, shape (batch, hidden_size)
        """
        batch_size, seq_len, _ = x.shape

        if h is None:
            h = torch.zeros(batch_size, self.hidden_size, device=x.device)

        outputs = []
        for t in range(seq_len):
            # At each time step: combine input and previous hidden state
            h = torch.tanh(self.W_xh(x[:, t, :]) + self.W_hh(h))
            outputs.append(h)

        # Stack all hidden states: (batch, seq_len, hidden_size)
        outputs = torch.stack(outputs, dim=1)
        return outputs, h


# Usage example
rnn = SimpleRNN(input_size=10, hidden_size=32)
x = torch.randn(4, 5, 10)   # batch=4, seq_len=5, features=10
outputs, final_h = rnn(x)
print(f"All hidden states: {outputs.shape}")   # (4, 5, 32)
print(f"Final hidden state: {final_h.shape}")  # (4, 32)
```

### PyTorch's Built-in RNN

```python
# PyTorch provides optimized implementations
rnn = nn.RNN(
    input_size=10,       # Size of each input element
    hidden_size=32,      # Size of hidden state
    num_layers=1,        # Number of stacked RNN layers
    batch_first=True,    # Input shape: (batch, seq, features)
    dropout=0.0,         # Dropout between layers (if num_layers > 1)
    bidirectional=False  # Process forward only
)

x = torch.randn(4, 5, 10)  # (batch, seq_len, input_size)
outputs, h_n = rnn(x)

print(f"outputs shape: {outputs.shape}")  # (4, 5, 32) -- all hidden states
print(f"h_n shape: {h_n.shape}")          # (1, 4, 32) -- final hidden state
# h_n has an extra dim for num_layers * num_directions
```

### The Vanishing Gradient Problem

Here's why vanilla RNNs fail on long sequences:

```python
# During backpropagation, gradients flow backward through time.
# At each step, they're multiplied by the weight matrix W_hh.

# If the largest eigenvalue of W_hh < 1: gradients SHRINK exponentially
# If the largest eigenvalue of W_hh > 1: gradients EXPLODE exponentially

# After T time steps, the gradient contribution from step 0 is roughly:
# gradient ~ (W_hh)^T * local_gradient

# Example: with a decay factor of 0.9 per step
import numpy as np
steps = [10, 50, 100, 200]
for t in steps:
    gradient_magnitude = 0.9 ** t
    print(f"After {t:3d} steps: gradient = {gradient_magnitude:.2e}")
# After  10 steps: gradient = 3.49e-01  -- still usable
# After  50 steps: gradient = 5.15e-03  -- very small
# After 100 steps: gradient = 2.66e-05  -- nearly zero
# After 200 steps: gradient = 7.07e-10  -- effectively zero

# This means the RNN "forgets" information from early in the sequence.
# It cannot learn long-range dependencies.
```

**The consequence**: A vanilla RNN processing the sentence "The cat, which had been
sitting on the mat for the entire afternoon while the dog slept nearby, suddenly
**jumped**" cannot connect "cat" to "jumped" -- they're too far apart.

---

## 3. Long Short-Term Memory (LSTM)

### Why LSTM Solves Vanishing Gradients

The LSTM introduces a **cell state** -- a highway that runs through the entire
sequence with minimal interference. Information can flow along this highway without
being multiplied by weight matrices at every step.

```
Swift analogy:
    // Vanilla RNN: like passing a message through a chain of people
    // Each person paraphrases it -- information degrades over time

    // LSTM: like having a shared document (cell state) that anyone
    // in the chain can read from and write to, but the document
    // itself travels unmodified unless explicitly changed
```

### The Four Gates

An LSTM cell has four components (three gates + one candidate):

```
1. Forget Gate (f_t):   "What should I erase from memory?"
2. Input Gate (i_t):    "What new information should I store?"
3. Candidate (g_t):     "What is the new information?"
4. Output Gate (o_t):   "What should I output from memory?"
```

The math:

```
f_t = sigmoid(W_f * [h_{t-1}, x_t] + b_f)     -- forget gate
i_t = sigmoid(W_i * [h_{t-1}, x_t] + b_i)     -- input gate
g_t = tanh(W_g * [h_{t-1}, x_t] + b_g)         -- candidate values
o_t = sigmoid(W_o * [h_{t-1}, x_t] + b_o)      -- output gate

c_t = f_t * c_{t-1} + i_t * g_t                 -- cell state update
h_t = o_t * tanh(c_t)                            -- hidden state output
```

### LSTM from Scratch

```python
class LSTMCell(nn.Module):
    """LSTM cell implemented from scratch.

    The key insight: the cell state c_t acts as a "conveyor belt."
    Information flows along it with only element-wise operations
    (multiply by forget gate, add from input gate), NOT matrix
    multiplications. This prevents gradient vanishing.
    """

    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.hidden_size = hidden_size

        # All four gates computed in one matrix multiply for efficiency
        # (then split the output into 4 chunks)
        self.gates = nn.Linear(input_size + hidden_size, 4 * hidden_size)

    def forward(
        self,
        x: torch.Tensor,
        state: tuple[torch.Tensor, torch.Tensor] | None = None,
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        """Process a full sequence.

        Args:
            x: (batch, seq_len, input_size)
            state: tuple of (h_0, c_0), each (batch, hidden_size)

        Returns:
            outputs: (batch, seq_len, hidden_size)
            (h_n, c_n): final hidden and cell states
        """
        batch_size, seq_len, _ = x.shape

        if state is None:
            h = torch.zeros(batch_size, self.hidden_size, device=x.device)
            c = torch.zeros(batch_size, self.hidden_size, device=x.device)
        else:
            h, c = state

        outputs = []
        for t in range(seq_len):
            # Concatenate input and previous hidden state
            combined = torch.cat([x[:, t, :], h], dim=1)

            # Compute all four gates at once
            gates = self.gates(combined)

            # Split into individual gates
            i, f, g, o = gates.chunk(4, dim=1)

            i = torch.sigmoid(i)  # Input gate
            f = torch.sigmoid(f)  # Forget gate
            g = torch.tanh(g)     # Candidate values
            o = torch.sigmoid(o)  # Output gate

            # Update cell state: forget old + add new
            c = f * c + i * g

            # Compute hidden state (output)
            h = o * torch.tanh(c)

            outputs.append(h)

        outputs = torch.stack(outputs, dim=1)
        return outputs, (h, c)


# Test it
lstm = LSTMCell(input_size=10, hidden_size=32)
x = torch.randn(4, 20, 10)  # batch=4, seq_len=20, features=10
outputs, (h_n, c_n) = lstm(x)
print(f"Outputs: {outputs.shape}")  # (4, 20, 32)
print(f"Final h: {h_n.shape}")      # (4, 32)
print(f"Final c: {c_n.shape}")      # (4, 32)
```

### PyTorch's Built-in LSTM

```python
lstm = nn.LSTM(
    input_size=10,
    hidden_size=32,
    num_layers=2,        # Stack 2 LSTM layers
    batch_first=True,
    dropout=0.3,         # Dropout between layers
    bidirectional=False,
)

x = torch.randn(4, 20, 10)
outputs, (h_n, c_n) = lstm(x)

print(f"outputs: {outputs.shape}")  # (4, 20, 32)
print(f"h_n: {h_n.shape}")         # (2, 4, 32)  -- one per layer
print(f"c_n: {c_n.shape}")         # (2, 4, 32)  -- one per layer

# Get the final hidden state of the last layer
last_layer_hidden = h_n[-1]  # (4, 32)
```

### Why LSTM Gradients Don't Vanish

```python
# The cell state update: c_t = f_t * c_{t-1} + i_t * g_t
# Gradient of c_t w.r.t. c_{t-1} = f_t (the forget gate)
# f_t is a sigmoid output in [0, 1]

# Unlike vanilla RNNs where gradients pass through tanh AND
# a weight matrix multiplication at each step, LSTM gradients
# only pass through an element-wise multiply by f_t.

# If the forget gate is close to 1.0 (remembering everything),
# the gradient flows almost unchanged -- like a "gradient highway."

# This is why LSTMs can learn dependencies over hundreds of steps
# where vanilla RNNs fail after ~20 steps.
```

---

## 4. Gated Recurrent Unit (GRU)

### A Simpler Alternative

The GRU combines the forget and input gates into a single **update gate** and
merges the cell state and hidden state. It has fewer parameters than LSTM but
often performs comparably.

```
z_t = sigmoid(W_z * [h_{t-1}, x_t])     -- update gate
r_t = sigmoid(W_r * [h_{t-1}, x_t])     -- reset gate
h_hat_t = tanh(W * [r_t * h_{t-1}, x_t]) -- candidate hidden state
h_t = (1 - z_t) * h_{t-1} + z_t * h_hat_t  -- final hidden state
```

The key differences from LSTM:
- **No separate cell state** -- just a hidden state
- **Two gates** instead of three (update + reset vs forget + input + output)
- **Fewer parameters** -- faster to train

```python
class GRUCell(nn.Module):
    """GRU cell from scratch.

    Think of it as a simplified LSTM:
    - Update gate z = "how much of the new state to use"
    - Reset gate r = "how much of the old state to consider"
    """

    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.hidden_size = hidden_size

        # Update gate
        self.W_z = nn.Linear(input_size + hidden_size, hidden_size)
        # Reset gate
        self.W_r = nn.Linear(input_size + hidden_size, hidden_size)
        # Candidate hidden state
        self.W_h = nn.Linear(input_size + hidden_size, hidden_size)

    def forward(
        self, x: torch.Tensor, h: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        batch_size, seq_len, _ = x.shape

        if h is None:
            h = torch.zeros(batch_size, self.hidden_size, device=x.device)

        outputs = []
        for t in range(seq_len):
            x_t = x[:, t, :]
            combined = torch.cat([x_t, h], dim=1)

            z = torch.sigmoid(self.W_z(combined))  # Update gate
            r = torch.sigmoid(self.W_r(combined))  # Reset gate

            # Reset gate controls how much of previous h to use
            combined_reset = torch.cat([x_t, r * h], dim=1)
            h_candidate = torch.tanh(self.W_h(combined_reset))

            # Update gate interpolates between old and new
            h = (1 - z) * h + z * h_candidate

            outputs.append(h)

        outputs = torch.stack(outputs, dim=1)
        return outputs, h
```

### PyTorch's Built-in GRU

```python
gru = nn.GRU(
    input_size=10,
    hidden_size=32,
    num_layers=2,
    batch_first=True,
    dropout=0.3,
)

x = torch.randn(4, 20, 10)
outputs, h_n = gru(x)

print(f"outputs: {outputs.shape}")  # (4, 20, 32)
print(f"h_n: {h_n.shape}")         # (2, 4, 32)
```

### When to Use What?

| Model | Parameters | Speed | Long Sequences | Use When |
|-------|-----------|-------|----------------|----------|
| RNN | Fewest | Fastest | Poor (vanishing gradient) | Short sequences, simple tasks |
| LSTM | Most | Slowest | Good | Default choice for sequence modeling |
| GRU | Medium | Medium | Good | Want LSTM-like perf with fewer params |
| Transformer | Varies | Varies | Best | Module 06 -- the current standard |

---

## 5. Bidirectional RNNs

### Processing Sequences in Both Directions

Sometimes context from the **future** matters too. For example, in "I went to the
bank to deposit money" vs "I went to the bank of the river," the word after "bank"
disambiguates its meaning.

```python
# Bidirectional LSTM processes the sequence forward AND backward
bilstm = nn.LSTM(
    input_size=10,
    hidden_size=32,
    num_layers=1,
    batch_first=True,
    bidirectional=True,  # <-- This is the key flag
)

x = torch.randn(4, 20, 10)
outputs, (h_n, c_n) = bilstm(x)

# Output size DOUBLES because we concatenate forward + backward
print(f"outputs: {outputs.shape}")  # (4, 20, 64)  -- 32*2
print(f"h_n: {h_n.shape}")         # (2, 4, 32)   -- 2 directions

# h_n[0] = final hidden state from forward pass
# h_n[1] = final hidden state from backward pass

# For classification, common to concatenate both:
h_forward = h_n[0]   # (4, 32)
h_backward = h_n[1]  # (4, 32)
h_combined = torch.cat([h_forward, h_backward], dim=1)  # (4, 64)
```

```
Visual:

Forward:   h1 -> h2 -> h3 -> h4 -> h5
                                       \
Input:     x1    x2    x3    x4    x5   --> concat at each step
                                       /
Backward:  h1 <- h2 <- h3 <- h4 <- h5

Each output[t] = [forward_h_t; backward_h_t]
```

---

## 6. Stacked (Deep) RNNs

### Adding Depth with Multiple Layers

Stacking RNN layers lets the network learn hierarchical representations:
- Layer 1 might learn character-level patterns
- Layer 2 might learn word-level patterns
- Layer 3 might learn phrase-level patterns

```python
# Stacked LSTM with 3 layers
stacked_lstm = nn.LSTM(
    input_size=10,
    hidden_size=64,
    num_layers=3,         # 3 stacked layers
    batch_first=True,
    dropout=0.3,          # Dropout between layers (not applied to last layer)
)

x = torch.randn(4, 20, 10)
outputs, (h_n, c_n) = stacked_lstm(x)

print(f"outputs: {outputs.shape}")  # (4, 20, 64) -- outputs from LAST layer only
print(f"h_n: {h_n.shape}")         # (3, 4, 64)  -- final h from each layer
print(f"c_n: {c_n.shape}")         # (3, 4, 64)  -- final c from each layer

# How it works internally:
# Layer 1 input: original x        -> produces hidden states h1
# Layer 2 input: h1 (+ dropout)    -> produces hidden states h2
# Layer 3 input: h2 (+ dropout)    -> produces hidden states h3 (= outputs)
```

---

## 7. Handling Variable-Length Sequences

### The Padding Problem

In real data, sequences have different lengths. We pad shorter sequences to match
the longest, but we don't want the model to process padding tokens.

```python
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

# Three sequences of different lengths
seq1 = torch.randn(5, 10)  # Length 5
seq2 = torch.randn(3, 10)  # Length 3
seq3 = torch.randn(7, 10)  # Length 7

# Pad to max length (7) -- pad with zeros
padded = torch.zeros(3, 7, 10)  # (batch=3, max_len=7, features=10)
padded[0, :5, :] = seq1
padded[1, :3, :] = seq2
padded[2, :7, :] = seq3

lengths = torch.tensor([5, 3, 7])

# Sort by length (descending) -- required by pack_padded_sequence
sorted_lengths, sorted_idx = lengths.sort(descending=True)
sorted_padded = padded[sorted_idx]

# Pack: tells the RNN to skip padding positions
packed = pack_padded_sequence(
    sorted_padded,
    sorted_lengths.cpu(),  # lengths must be on CPU
    batch_first=True,
)

# Process with LSTM -- it only computes on real (non-padded) positions
lstm = nn.LSTM(input_size=10, hidden_size=32, batch_first=True)
packed_output, (h_n, c_n) = lstm(packed)

# Unpack back to padded format
output, output_lengths = pad_packed_sequence(packed_output, batch_first=True)
print(f"output: {output.shape}")  # (3, 7, 32) -- padded positions are zeros

# Unsort to restore original order
_, unsort_idx = sorted_idx.sort()
output = output[unsort_idx]
```

### Modern Alternative: `enforce_sorted=False`

```python
# Since PyTorch 1.1, you can skip manual sorting
packed = pack_padded_sequence(
    padded,
    lengths.cpu(),
    batch_first=True,
    enforce_sorted=False,  # Handles sorting internally
)

packed_output, (h_n, c_n) = lstm(packed)
output, _ = pad_packed_sequence(packed_output, batch_first=True)
# output is already in the original order!
```

---

## 8. Sequence-to-Sequence (Seq2Seq) Basics

### Encoder-Decoder Architecture

Seq2seq uses two RNNs: an **encoder** that reads the input sequence and an
**decoder** that generates the output sequence.

```python
class Seq2Seq(nn.Module):
    """Basic sequence-to-sequence model.

    Applications:
    - Machine translation ("Hello" -> "Bonjour")
    - Text summarization
    - Chatbots

    Swift analogy: Think of this as two Codable objects --
    one encodes the input into a compressed representation,
    the other decodes it into the output.
    """

    def __init__(
        self,
        input_vocab_size: int,
        output_vocab_size: int,
        embed_size: int,
        hidden_size: int,
    ):
        super().__init__()
        # Encoder
        self.encoder_embed = nn.Embedding(input_vocab_size, embed_size)
        self.encoder = nn.LSTM(embed_size, hidden_size, batch_first=True)

        # Decoder
        self.decoder_embed = nn.Embedding(output_vocab_size, embed_size)
        self.decoder = nn.LSTM(embed_size, hidden_size, batch_first=True)
        self.output_proj = nn.Linear(hidden_size, output_vocab_size)

    def forward(
        self,
        src: torch.Tensor,       # (batch, src_len)
        tgt: torch.Tensor,       # (batch, tgt_len)
    ) -> torch.Tensor:
        # Encode: compress entire input into a context vector
        src_embedded = self.encoder_embed(src)
        _, (h, c) = self.encoder(src_embedded)
        # h and c now hold the "meaning" of the entire source sequence

        # Decode: generate output sequence from context
        tgt_embedded = self.decoder_embed(tgt)
        decoder_output, _ = self.decoder(tgt_embedded, (h, c))

        # Project to vocabulary
        logits = self.output_proj(decoder_output)
        return logits  # (batch, tgt_len, output_vocab_size)


model = Seq2Seq(
    input_vocab_size=1000,
    output_vocab_size=800,
    embed_size=64,
    hidden_size=128,
)

src = torch.randint(0, 1000, (4, 10))  # Source sentences
tgt = torch.randint(0, 800, (4, 15))   # Target sentences
logits = model(src, tgt)
print(f"logits: {logits.shape}")  # (4, 15, 800)
```

### Limitation of Basic Seq2Seq

The entire input sequence is compressed into a single fixed-size vector (h, c).
This is a **bottleneck** -- long inputs lose information. This is exactly what
**attention** (Module 06) was invented to solve.

---

## 9. Practical Tips

### Gradient Clipping

```python
# Prevent exploding gradients by capping their magnitude
model = nn.LSTM(input_size=10, hidden_size=64, batch_first=True)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# During training:
loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()

# max_norm=1.0 means: if the total gradient norm exceeds 1.0,
# scale all gradients down proportionally.
# This is ESSENTIAL for RNN training.
```

### Teacher Forcing

```python
# During seq2seq training, we have two options:
#
# 1. Free running: Feed the model's own predictions back as input
#    Problem: Early in training, predictions are garbage, so errors compound
#
# 2. Teacher forcing: Feed the GROUND TRUTH as input at each step
#    Problem: At inference time, we don't have ground truth
#
# Solution: Use teacher forcing with some probability during training

import random

def train_step(model, src, tgt, teacher_forcing_ratio=0.5):
    """Train with probabilistic teacher forcing."""
    encoder_output, (h, c) = model.encoder(model.encoder_embed(src))

    # Start with <SOS> token
    decoder_input = tgt[:, 0:1]  # First token
    outputs = []

    for t in range(1, tgt.shape[1]):
        output, (h, c) = model.decoder(
            model.decoder_embed(decoder_input), (h, c)
        )
        logits = model.output_proj(output)
        outputs.append(logits)

        # Teacher forcing: use ground truth or model prediction
        if random.random() < teacher_forcing_ratio:
            decoder_input = tgt[:, t:t+1]             # Ground truth
        else:
            decoder_input = logits.argmax(dim=-1)      # Model prediction

    return torch.cat(outputs, dim=1)
```

### Building a Complete Sequence Classifier

```python
class SentimentClassifier(nn.Module):
    """LSTM-based text classifier.

    This is the most common practical use of LSTMs:
    encode a sequence, then classify based on the final state.
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int,
        hidden_dim: int,
        num_classes: int,
        num_layers: int = 2,
        dropout: float = 0.3,
        bidirectional: bool = True,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=bidirectional,
        )
        self.dropout = nn.Dropout(dropout)

        # If bidirectional, hidden_dim is doubled
        fc_input = hidden_dim * 2 if bidirectional else hidden_dim
        self.fc = nn.Linear(fc_input, num_classes)

    def forward(self, x: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Token IDs, shape (batch, max_seq_len)
            lengths: Actual lengths, shape (batch,)
        """
        embedded = self.dropout(self.embedding(x))

        # Pack to handle variable lengths efficiently
        packed = pack_padded_sequence(
            embedded, lengths.cpu(),
            batch_first=True, enforce_sorted=False,
        )
        packed_output, (h_n, c_n) = self.lstm(packed)

        # Get final hidden states from both directions
        if self.lstm.bidirectional:
            # h_n shape: (num_layers * 2, batch, hidden)
            # Take last layer's forward and backward
            h_forward = h_n[-2]  # (batch, hidden)
            h_backward = h_n[-1]  # (batch, hidden)
            hidden = torch.cat([h_forward, h_backward], dim=1)
        else:
            hidden = h_n[-1]  # (batch, hidden)

        hidden = self.dropout(hidden)
        logits = self.fc(hidden)
        return logits  # (batch, num_classes)


# Usage
classifier = SentimentClassifier(
    vocab_size=10000,
    embed_dim=128,
    hidden_dim=256,
    num_classes=2,  # positive/negative
)

# Fake batch
tokens = torch.randint(1, 10000, (8, 50))  # 8 sentences, max 50 tokens
lengths = torch.randint(10, 50, (8,))        # actual lengths
logits = classifier(tokens, lengths)
print(f"Predictions: {logits.shape}")         # (8, 2)
```

---

## 10. Summary: The Evolution of Sequence Models

```
RNN (1986)
  |
  | Problem: vanishing gradients on long sequences
  v
LSTM (1997)
  |
  | Problem: slow training, complex architecture
  v
GRU (2014)
  |
  | Problem: still sequential (can't parallelize)
  v
Attention + Seq2Seq (2014-2015)
  |
  | Problem: still uses RNN backbone
  v
Transformer (2017) -- Module 06
  |
  | Completely removes recurrence
  v
Modern NLP (BERT, GPT, etc.) -- Module 07
```

### Key Takeaways

1. **RNNs** process sequences step-by-step with a hidden state, but suffer from vanishing gradients
2. **LSTMs** add a cell state "highway" with gates to control information flow, solving vanishing gradients
3. **GRUs** simplify LSTMs with fewer gates while maintaining similar performance
4. **Bidirectional** models process sequences in both directions for richer representations
5. **Packing padded sequences** is essential for efficient training with variable-length inputs
6. **Gradient clipping** is mandatory for stable RNN training
7. **Seq2seq** models use encoder-decoder architecture but have a bottleneck that attention solves

---

## Swift/iOS Connection

| Python/PyTorch | Swift/iOS Equivalent |
|---------------|---------------------|
| `nn.LSTM` | `MLModel` with recurrent layers |
| Sequence classifier | `NLTagger`, `NLModel` |
| Tokenization | `NLTokenizer` |
| `pack_padded_sequence` | Variable-length `MLMultiArray` |
| Sentiment analysis | `NLTagger(tagSchemes: [.sentimentScore])` |
| Bidirectional processing | Create ML's built-in text classifier |

After training in PyTorch, you can convert sequence models to Core ML using
`coremltools` for on-device inference in your iOS apps.
