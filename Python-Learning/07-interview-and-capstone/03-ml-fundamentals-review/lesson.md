# ML Fundamentals Speed Review

**Read this the night before your interview.**

This is a comprehensive one-pass review of all ML concepts across the 7-phase curriculum, with quick formulas, decision trees, and Python syntax cheat sheet.

---

## Phase 1: Python Foundations

### Must-Know Built-ins

```python
# List operations
nums = [3, 1, 2]
nums.sort()  # in-place
sorted(nums)  # returns new list
nums.reverse()  # in-place
nums[::-1]  # returns reversed

# Dict operations
d = {"a": 1}
d.get("b", default=0)  # safe access
d.setdefault("c", 0)  # get or set
d.update({"d": 4})  # merge

# Comprehensions
[x**2 for x in range(5) if x % 2 == 0]  # list
{x: x**2 for x in range(3)}  # dict
{x**2 for x in range(5)}  # set

# Generators (memory efficient)
(x**2 for x in range(1000000))  # lazy evaluation

# File I/O
with open("file.txt") as f:
    lines = f.readlines()
```

### Key Patterns

**Iterators**: Implement `__iter__()` and `__next__()`
**Decorators**: `@decorator` wraps function
**Exceptions**: Try/except/finally for error handling
**Classes**: `__init__`, `self`, inheritance with `super()`

---

## Phase 2: NumPy & SciPy

### NumPy Essentials

```python
import numpy as np

# Creation
np.array([1, 2, 3])
np.zeros((3, 4))
np.ones((2, 2))
np.arange(0, 10, 2)
np.linspace(0, 1, 5)
np.random.randn(1000)  # normal distribution

# Indexing & slicing
arr[0]  # first element
arr[:3]  # first 3
arr[::2]  # every other
arr[arr > 5]  # boolean mask

# Operations (vectorized = fast)
arr + 1
arr * 2
np.dot(a, b)  # matrix multiplication
arr.T  # transpose

# Aggregations
arr.sum(), arr.mean(), arr.std()
arr.sum(axis=0)  # sum columns

# Shape manipulation
arr.reshape((-1, 1))  # flatten to column
np.concatenate([a, b], axis=0)
np.vstack([a, b])
np.hstack([a, b])
```

### SciPy Highlights

- `scipy.stats`: distributions, tests
- `scipy.optimize`: minimize/maximize functions
- `scipy.linalg`: linear algebra beyond NumPy
- `scipy.spatial.distance`: pairwise distances

---

## Phase 3: Data Processing (Pandas)

### Pandas 101

```python
import pandas as pd

# Creation
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
df = pd.read_csv("file.csv")
df = pd.read_json("file.json")

# Inspection
df.shape  # (rows, cols)
df.head(), df.tail()
df.info()  # dtypes, non-null counts
df.describe()  # statistics

# Selection
df["col"]  # Series
df[["col1", "col2"]]  # DataFrame
df.loc[0]  # by index label
df.iloc[0]  # by position
df[df["col"] > 5]  # boolean mask

# Manipulation
df["new_col"] = df["A"] + df["B"]
df.drop(columns=["col"])
df.rename(columns={"old": "new"})
df.fillna(0)
df.dropna()

# Groupby (critical!)
df.groupby("col")["value"].mean()
df.groupby(["col1", "col2"]).agg({"val": ["mean", "sum"]})

# Merging
pd.merge(df1, df2, on="key", how="inner")
df1.join(df2)

# Pivoting
df.pivot(index="col1", columns="col2", values="col3")
df.pivot_table(index="col1", columns="col2", aggfunc="mean")

# Time series
df["date"] = pd.to_datetime(df["date"])
df.set_index("date").resample("D").mean()

# Efficiency
df.loc[df["col"] > 5, "new_col"] = val  # faster than iterating
```

---

## Phase 4: ML Algorithms Cheat Sheet

### Supervised Learning

#### Regression

**Linear Regression**: Y = β₀ + β₁X₁ + ... + βₙXₙ
- Loss: MSE = (1/n) Σ(yᵢ - ŷᵢ)²
- When: continuous output, linear relationship
- Assumptions: linearity, independence, homoscedasticity

**Ridge/Lasso**: Add regularization to prevent overfitting
- Ridge: L2 penalty = λΣβᵢ² (shrink all)
- Lasso: L1 penalty = λΣ|βᵢ| (feature selection)

#### Classification

**Logistic Regression**: P(Y=1|X) = 1 / (1 + e^(-z))
- Loss: cross-entropy = -[y log ŷ + (1-y) log(1-ŷ)]
- Output: probability [0, 1]

**Decision Trees**:
- Split on feature that maximizes information gain
- Info gain = Entropy(parent) - Σ(|child|/|parent|) * Entropy(child)
- Entropy = -Σ pᵢ log₂(pᵢ)
- Pros: interpretable, nonlinear
- Cons: overfitting, unstable

**Random Forest**: Ensemble of trees
- Pros: reduces overfitting, parallelizable
- Cons: less interpretable, slower inference

**SVM**: Find max-margin hyperplane
- Kernel trick: nonlinear decision boundaries
- Works for binary and multi-class
- Sensitive to scaling

**Naive Bayes**: P(Y|X) ∝ P(X|Y) * P(Y)
- Assumes feature independence (naive)
- Fast, works well for text/spam
- Probabilistic interpretation

#### Unsupervised Learning

**K-Means**:
- Initialize k centroids randomly
- Assign points to nearest centroid
- Recompute centroids as means
- Repeat until convergence
- Complexity: O(n*k*d*iterations)
- Issues: sensitivity to init, non-spherical clusters

**Hierarchical Clustering**:
- Agglomerative (bottom-up): merge closest clusters
- Divisive (top-down): split clusters
- Linkage: single (min distance), complete (max), average, Ward (min variance)
- Dendrogram: tree visualization

**DBSCAN**:
- Density-based: points within ε of each other
- Parameters: ε (radius), min_pts (density threshold)
- Pros: finds arbitrary shapes, no k parameter
- Cons: sensitive to parameters

**Dimensionality Reduction**

**PCA**: Unsupervised, linear
- Maximize variance in orthogonal directions
- Explained variance ratio: tells how much info each PC captures
- Use for: compression, visualization, denoising

**t-SNE**: Nonlinear, for visualization
- Preserves local structure
- Expensive (O(n²))
- Use for: exploring high-dimensional data

**UMAP**: Nonlinear, faster than t-SNE
- Graph-based approach
- Preserves both local and global structure

---

## Phase 5: Deep Learning Essentials

### Neural Network Basics

**Architecture**: Layers of neurons
- Input layer: features
- Hidden layers: learned representations
- Output layer: predictions
- Activation: ReLU (hidden), softmax (classification), sigmoid (binary)

**Forward Pass**:
```
z = W*x + b
a = activation(z)
```

**Backward Pass** (Backpropagation):
```
dL/dW = (dL/da) * (da/dz) * (dz/dW)
```

**Optimization**:
- SGD: W -= lr * gradient
- Momentum: adds velocity, faster convergence
- Adam: adaptive learning rate per parameter (best default)

### CNN (Image Data)

**Convolution**: Slide filter over image, extract features
- Filters: detect edges, textures, shapes at different scales
- Pooling: downsample, reduce parameters

**Architecture**:
```
Input → Conv → ReLU → Pool → Conv → ReLU → Pool → Flatten → Dense → Output
```

- Advantages: parameter sharing, translation invariance
- Use: image classification, detection, segmentation

### RNN (Sequential Data)

**Recurrent**: Pass hidden state forward
- h_t = tanh(W_h * h_{t-1} + W_x * x_t + b)
- Issue: vanishing gradients (RNN forgets old info)

**LSTM** (Long Short-Term Memory):
- Cell state: long-term memory (C_t)
- Hidden state: short-term output (h_t)
- Gates: forget, input, output (learned what to remember/forget)
- Fixes: can learn long-range dependencies

**GRU** (Gated Recurrent Unit): Simpler LSTM
- 2 gates instead of 3
- Often comparable performance, fewer parameters

**Transformer** (Modern):
- Self-attention: each token attends to all others
- Parallel processing (unlike RNN)
- BERT, GPT are transformers
- Use: text, sequence-to-sequence, multimodal

### Training Tips

**Batch Normalization**: Normalize layer inputs
- Reduces internal covariate shift
- Allows higher learning rates
- Acts as regularization

**Dropout**: Randomly zero activations during training
- Prevents co-adaptation
- Effective regularization
- Use ~20-50% dropout rate

**Early Stopping**: Stop when validation loss plateaus
- Prevents overfitting
- Set patience (e.g., stop if no improvement for 10 epochs)

**Learning Rate**:
- Too high: diverges
- Too low: slow, may stuck in local minima
- Learning rate schedule: decay over time

---

## Phase 6: LLMs & Transformers

### Key Concepts

**Tokenization**: Text → tokens → IDs
- BPE (Byte-Pair Encoding): subword tokenization
- Vocab size: 50k-100k tokens typical

**Embedding**: Token ID → vector
- Learned during training
- Capture semantic meaning
- Position embeddings: encode token position

**Attention**: Query-Key-Value mechanism
```
Attention(Q, K, V) = softmax(Q*K^T / sqrt(d_k)) * V
```
- Q: what am I looking for?
- K: what can you offer?
- V: what information do you have?
- Multi-head: multiple attention patterns in parallel

**Self-Attention**: Query, Key, Value all from same sequence
- Each token attends to all other tokens (and itself)
- Learns dependencies regardless of distance
- Parallel processing (unlike RNN)

### Transformer Architecture

**Encoder**: Bidirectional context (BERT)
- Processes entire sequence at once
- Use: understanding, classification, NER

**Decoder**: Causal (left-to-right) (GPT)
- Predicts next token from previous
- Use: generation, language modeling

**Encoder-Decoder** (T5, translation):
- Encoder: process input
- Decoder: generate output autoregressively

### Prompting & Fine-Tuning

**Prompting** (zero-shot, few-shot):
- Few examples set the task
- Chain-of-thought: ask model to explain reasoning

**Fine-tuning**:
- Supervised: labeled examples, task-specific loss
- Parameter-efficient: LoRA, prefix tuning (small updates)

**RAG** (Retrieval-Augmented Generation):
1. Retrieve relevant documents
2. Pass as context to LLM
3. Generate answer grounded in context

---

## Phase 7: Advanced Topics

### Evaluation Metrics

**Classification**:
- Accuracy: (TP + TN) / Total
- Precision: TP / (TP + FP) - false alarm rate
- Recall: TP / (TP + FN) - miss rate
- F1: 2 * (P * R) / (P + R) - harmonic mean
- ROC-AUC: area under curve, threshold-independent

**Imbalanced Data**:
- Accuracy is misleading
- Use precision-recall, F1, AUC-ROC
- SMOTE: oversample minority class
- Class weights: penalize minority errors more

**Regression**:
- MAE: mean absolute error (|predictions|)
- MSE: mean squared error (penalizes outliers)
- RMSE: sqrt(MSE), interpretable
- R²: proportion of variance explained (0-1 scale)

**NLP**:
- BLEU: n-gram overlap (translation)
- ROUGE: recall-oriented (summarization)
- Perplexity: measure of language model (lower = better)

### Feature Engineering

**Numerical**:
- Scaling: StandardScaler (mean 0, std 1), MinMaxScaler (0-1)
- Binning: discretize continuous to categorical
- Polynomial: x → x, x², x³ (captures nonlinearity)
- Log: x → log(x) (for skewed distributions)

**Categorical**:
- One-hot: categories → binary columns
- Ordinal: ranked categories → integers
- Target encoding: category → mean target value
- Embedding: learn dense representation

**Temporal**:
- Extract: year, month, day, hour, day-of-week
- Lag features: previous time step values
- Rolling: moving average, window statistics

**Domain**:
- Interaction: combine features
- Ratios: feature1 / feature2
- Domain knowledge: business context

### Cross-Validation

**K-Fold**: Divide into k, train k times
- Standard: k=5 or 10
- Stratified: preserve class distribution
- Time series: respect temporal order (don't shuffle)

**Leave-One-Out (LOO)**: k=n, expensive but unbiased

**Validation Curve**: Plot train/test vs hyperparameter
- Underfitting: both high error
- Overfitting: gap between train and test
- Sweet spot: balanced

---

## ML Algorithm Decision Tree

```
PROBLEM TYPE?
├─ REGRESSION (continuous)
│  ├─ Linear relationship? → Linear Regression
│  ├─ Need interpretability? → Decision Tree
│  └─ Nonlinear? → Random Forest, Gradient Boosting
│
├─ CLASSIFICATION (categorical)
│  ├─ Binary, need probability? → Logistic Regression
│  ├─ Need interpretability? → Decision Tree
│  ├─ High-dimensional? → Linear SVM
│  ├─ Mixed features? → Random Forest
│  └─ Nonlinear? → SVM with RBF kernel, Neural Network
│
└─ UNSUPERVISED (no labels)
   ├─ Clustering?
   │  ├─ k known? → K-Means
   │  ├─ k unknown? → DBSCAN, Hierarchical
   │  └─ Elliptical clusters? → Gaussian Mixture
   │
   └─ Dimensionality reduction?
      ├─ Linear? → PCA
      ├─ Visualization? → t-SNE, UMAP
      └─ Nonlinear? → Autoencoders
```

---

## DL Quick Reference

### When to Use

- **Neural Networks**: >1000s samples, complex patterns
- **CNN**: Images, spatial data
- **RNN/LSTM**: Sequential: time series, text, speech
- **Transformer**: Text, sequence-to-sequence, all modern NLP

### Common Issues & Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| Loss not decreasing | LR too low, bad init | Increase LR, check data |
| Loss NaN | LR too high, exploding gradients | Lower LR, gradient clipping |
| Overfitting | Too complex, too much training | Regularize, early stop, more data |
| Underfitting | Too simple, too little training | Increase model size, train longer |
| Slow convergence | Momentum, learning rate | Use Adam, batch norm |

---

## LLM Quick Reference

### Tokens & Context

- 1 token ≈ 4 characters
- 100k tokens: ~75k words
- GPT-4: 128k tokens context
- Attention is O(n²) in context length

### Common Models

- **BERT**: Encoder, understanding, classification
- **GPT-3.5/4**: Decoder, generation, reasoning
- **Claude**: Decoder, long context, nuanced
- **LLaMA**: Open-source, efficient
- **Mistral**: Small, fast, good performance

### Costs

- Per-token billing: input tokens (cheaper) vs output tokens
- Context window affects cost (longer = more expensive)
- Batching amortizes cost

---

## Python ML Stack Cheat Sheet

```python
# Data
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# ML Models
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.svm import SVC, SVR
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA

# Feature Engineering
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Evaluation
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve

# Text
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk import word_tokenize, pos_tag
import nltk

# Deep Learning
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
import torch
import torch.nn as nn

# NLP
from transformers import AutoTokenizer, AutoModel, pipeline
from langchain import LLMChain, PromptTemplate

# Utils
from typing import List, Dict, Tuple, Optional
import json
import pickle
```

---

## Interview Red Flags to Avoid

1. **Data Leakage**: Using future information or test data stats during training
2. **Not scaling**: Features must be comparable scale
3. **Ignoring class imbalance**: Use stratified CV, evaluate on imbalanced metrics
4. **Overfitting**: High train accuracy, low test accuracy → regularize
5. **Wrong metric**: Accuracy on imbalanced data is meaningless
6. **No baseline**: Can't judge model without comparison
7. **Statistically insignificant**: A/B test before deploying

---

## Last-Minute Tips

- **Know the math**: Linear regression loss, softmax, cross-entropy, backprop
- **Know the tradeoffs**: Bias vs variance, precision vs recall
- **Know the tools**: pandas groupby, sklearn pipeline, numpy broadcasting
- **Know when to use what**: Which algorithm for which problem
- **Know the gotchas**: Scaling, leakage, overfitting, metrics
- **Explain clearly**: No jargon salad, explain to a 5-year-old

---

Good luck! You've got all the tools. Now go ace that interview.
