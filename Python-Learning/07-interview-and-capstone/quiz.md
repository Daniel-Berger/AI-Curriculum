# Phase 7: Comprehensive Interview Quiz

20 questions covering all 7 phases. Test your knowledge before the interview.

---

## EASY (5 questions)

### Question 1
What does the lambda function do?

```python
func = lambda x, y: x + y * 2
result = func(3, 4)
```

What is `result`?

**A)** 14
**B)** 11
**C)** 7
**D)** 24

<details>
<summary>Answer</summary>

**A) 14**

`lambda x, y: x + y * 2` means `x + (y * 2)` due to operator precedence.
`func(3, 4)` = `3 + (4 * 2)` = `3 + 8` = `11`

Wait, let me recalculate: 3 + (4 * 2) = 3 + 8 = 11

Actually the answer is **B) 11**

</details>

---

### Question 2
What's the difference between `.reshape()` and `.flatten()` in NumPy?

**A)** They do the same thing
**B)** reshape changes shape but not order; flatten always creates 1D array
**C)** flatten changes shape; reshape always creates 1D array
**D)** reshape requires a tuple; flatten doesn't

<details>
<summary>Answer</summary>

**B) reshape changes shape but not order; flatten always creates 1D array**

- `reshape(shape)`: Rearrange elements into new shape, same total elements
- `flatten()`: Always returns 1D array, creates a copy
- Key difference: `reshape(-1, 1)` means "infer this dimension", whereas `flatten()` is specific

</details>

---

### Question 3
In pandas, what does `groupby('col').agg({'val': 'mean'})` do?

**A)** Returns mean of column 'val' for each unique value in 'col'
**B)** Returns total rows grouped by 'col'
**C)** Sorts by 'col' then calculates mean
**D)** Returns only rows where 'val' is the mean

<details>
<summary>Answer</summary>

**A) Returns mean of column 'val' for each unique value in 'col'**

`groupby` splits data by unique values in key column, then applies aggregation function to other columns.

</details>

---

### Question 4
What's the primary difference between regression and classification?

**A)** Regression is faster
**B)** Regression predicts continuous values; classification predicts categories
**C)** Classification is more accurate
**D)** They're the same, different names

<details>
<summary>Answer</summary>

**B) Regression predicts continuous values; classification predicts categories**

- Regression: Output is continuous (e.g., price $100-500)
- Classification: Output is discrete category (e.g., email is spam/not spam)

</details>

---

### Question 5
What does ReLU activation do?

**A)** Returns max(0, x)
**B)** Returns 1/(1+e^-x)
**C)** Returns x if x>0 else -x
**D)** Returns random value

<details>
<summary>Answer</summary>

**A) Returns max(0, x)**

ReLU (Rectified Linear Unit) = max(0, input). Simple, computationally efficient, reduces vanishing gradient.

</details>

---

## MEDIUM (8 questions)

### Question 6
You train a model that achieves 99% accuracy on training data but 75% on test data. What's happening?

**A)** Underfitting
**B)** Model is perfect
**C)** Overfitting
**D)** Data leakage

<details>
<summary>Answer</summary>

**C) Overfitting**

Large gap between train and test = overfitting (memorized training data, poor generalization).

Solutions: regularization (L1/L2), dropout, early stopping, more training data.

</details>

---

### Question 7
You apply StandardScaler to your data. What does it do?

```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
```

**A)** Converts to 0-1 range
**B)** Normalizes to mean=0, std=1
**C)** Sorts data
**D)** Removes outliers

<details>
<summary>Answer</summary>

**B) Normalizes to mean=0, std=1**

StandardScaler: `(x - mean) / std`

Result: features have mean 0 and standard deviation 1. Important for distance-based algorithms (KNN, SVM, neural networks).

</details>

---

### Question 8
What's the purpose of cross-validation?

**A)** Make training faster
**B)** Get robust estimate of model performance on unseen data
**C)** Prevent overfitting (only)
**D)** Balance classes

<details>
<summary>Answer</summary>

**B) Get robust estimate of model performance on unseen data**

K-Fold CV: train k models on different splits, average performance. More reliable than single train/test split.

</details>

---

### Question 9
In a confusion matrix, what is "recall"?

Confusion Matrix:
```
         Predicted Pos  Predicted Neg
Actual Pos    TP=100         FN=20
Actual Neg    FP=10          TN=870
```

**A)** TP / (TP + FP) = 100/110 = 0.91
**B)** TP / (TP + FN) = 100/120 = 0.83
**C)** (TP + TN) / Total = 970/1000 = 0.97
**D)** FP / (FP + TN) = 10/880 = 0.01

<details>
<summary>Answer</summary>

**B) TP / (TP + FN) = 100/120 = 0.83**

Recall = "Of actual positives, how many did we catch?"
- High recall: miss few positives (good for fraud detection, disease screening)
- Formula: TP / (TP + FN)

(A) is Precision = "Of predicted positives, how many are correct?"

</details>

---

### Question 10
What's the main advantage of using a pre-trained BERT model vs training from scratch?

**A)** No hyperparameter tuning needed
**B)** Requires less data, faster training
**C)** Always more accurate
**D)** Works for all languages

<details>
<summary>Answer</summary>

**B) Requires less data, faster training**

Transfer learning: pre-trained on huge corpus, learned general language patterns. Fine-tuning on your task data is much faster and requires less labeled data.

Trade-off: might not be optimal for specialized domains.

</details>

---

### Question 11
What does an attention head in a transformer do?

**A)** Learns one fixed pattern (e.g., only next token)
**B)** Learns a different relevance weighting between tokens
**C)** Reduces model size
**D)** Ensures deterministic output

<details>
<summary>Answer</summary>

**B) Learns a different relevance weighting between tokens**

Each attention head learns a different way to weight all tokens. Multi-head = multiple patterns in parallel.

Head 1 might attend to next word, Head 2 to matching pronouns, etc.

</details>

---

### Question 12
You deploy a model that works great in testing but fails in production. What's likely?

**A)** Bug in deployment code
**B)** Data distribution changed (data drift)
**C)** Model is too complex
**D)** Users are using it wrong

<details>
<summary>Answer</summary>

**B) Data distribution changed (data drift)**

Common in production: real-world data differs from training data (seasonal changes, new patterns, data quality issues).

Solutions: monitor accuracy, retrain periodically, alert on drift, A/B test new versions.

</details>

---

### Question 13
What's RAG (Retrieval-Augmented Generation)?

**A)** Angry retrieval model
**B)** Retrieve relevant documents, use as context for LLM to generate answer
**C)** Retrain model after generating
**D)** Reduce and Group operation

<details>
<summary>Answer</summary>

**B) Retrieve relevant documents, use as context for LLM to generate answer**

RAG pipeline:
1. Index documents with embeddings
2. User query → retrieve relevant docs
3. Pass docs + query to LLM
4. LLM generates grounded answer

Benefits: factually accurate, updatable knowledge base, cheaper than fine-tuning.

</details>

---

## HARD (7 questions)

### Question 14
You're building a classifier for rare disease (0.1% prevalence). Accuracy alone is misleading. Why, and what should you optimize instead?

<details>
<summary>Answer</summary>

**Problem**: If model predicts "no disease" for everyone, accuracy = 99.9%! Useless.

**Why**: Class imbalance makes majority class dominate accuracy metric.

**Solution**: Optimize for recall (catch all diseases, even if false alarms) or F1 (balance precision/recall).

Better: Use ROC-AUC or PR-AUC (threshold-independent), stratified CV.

</details>

---

### Question 15
Explain data leakage in this scenario:

```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_all)  # ALL data, including test!
X_train, X_test = train_test_split(X_scaled, ...)
model.fit(X_train, y_train)
```

What's wrong?

<details>
<summary>Answer</summary>

**Data Leakage**: Scaler was fitted on ALL data, including test set.

Why it's wrong: Scaler learned mean/std from test data, then applied to test data. Artificially inflates performance.

**Fix**: Fit scaler ONLY on training data:
```python
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Apply same scaler
```

This way: scaler parameters only know about training distribution.

</details>

---

### Question 16
You have 100K documents and need to build a semantic search system. Walk through the architecture.

<details>
<summary>Answer</summary>

**Architecture**:

1. **Embedding** (offline, one-time):
   - Load all documents
   - Split into chunks (500 chars, 100 overlap)
   - Embed each chunk: SentenceTransformers or OpenAI API (100K chunks ≈ $10-50)
   - Store embeddings in vector DB: ChromaDB, Pinecone, Weaviate

2. **Search** (at runtime):
   - User query → embed (same model as documents)
   - Vector similarity search: cosine similarity to find top-k chunks
   - ChromaDB: ~50ms for 100K documents

3. **Results**:
   - Return top-k chunks with document metadata
   - Optional: Re-rank using cross-encoder for better quality

**Trade-offs**:
- Embedding model: small (fast, cheap) vs large (accurate, expensive)
- Chunk size: large (fewer chunks, less context) vs small (more chunks, more noise)
- Vector DB: local (free, slow) vs cloud (expensive, fast, managed)

</details>

---

### Question 17
Design an ML system to predict customer churn. Walk through phases.

<details>
<summary>Answer</summary>

**Phase 1: Problem Definition**
- Business goal: Reduce churn rate
- Metric: Recall (catch at-risk customers), F1 (balance false alarms)
- Data needed: customer features + churn label

**Phase 2: Data Collection & EDA**
- Gather: usage, engagement, support tickets, demographics
- Analyze: class imbalance (typical: 5-10% churn), feature distributions, missing data

**Phase 3: Feature Engineering**
- Temporal: days since last purchase, usage trend
- Behavioral: support ticket count, engagement score
- Interaction: usage × tenure (heavy user for long = low churn)

**Phase 4: Model Selection**
- Try: logistic regression (baseline), random forest (feature importance), gradient boosting (best performance)
- Cross-validate: stratified k-fold (preserve churn ratio)

**Phase 5: Evaluation**
- Not accuracy! Use: recall, precision, F1, ROC-AUC
- Confusion matrix: understand false positives (cost of offer) vs false negatives (lost customer)

**Phase 6: Deployment**
- Batch: daily scoring of all customers
- Return: top-100 at-risk customers + churn probability
- Action: send retention offer

**Phase 7: Monitoring**
- Track: model accuracy over time, demographic bias
- Retrain monthly: capture new patterns

</details>

---

### Question 18
You fine-tuned a BERT model on your task. It overfits: train accuracy 95%, test accuracy 70%. How do you fix?

<details>
<summary>Answer</summary>

**Root cause**: Fine-tuning on small dataset leads to overfitting.

**Solutions** (in order of try):

1. **More data**: Best solution, but expensive
   - Data augmentation: back-translation (NLP), mixup
   - Semi-supervised: pseudo-labeling

2. **Regularization**:
   - Dropout: add 0.2-0.3 dropout to fine-tune head
   - Early stopping: stop when validation loss plateaus
   - Weight decay: L2 penalty on weights

3. **Training tweaks**:
   - Lower learning rate: 1e-5 to 2e-5 (smaller updates)
   - Shorter fine-tune: fewer epochs (don't overfit)
   - Freeze early layers: keep pre-trained knowledge, only fine-tune head

4. **Model tweaks**:
   - Ensemble: combine multiple fine-tuned models
   - Distillation: train smaller model on large model's output

**Best practice**: Freeze early layers + lower learning rate + early stopping

</details>

---

### Question 19
Compare K-Means, DBSCAN, and Hierarchical Clustering. When would you use each?

<details>
<summary>Answer</summary>

| Aspect | K-Means | DBSCAN | Hierarchical |
|--------|---------|--------|--------------|
| **k needed?** | Yes, must specify | No, data-driven | No, choose cutoff |
| **Shape** | Spherical, similar size | Any shape | Any shape |
| **Outliers** | Assigned to cluster | Labeled as noise (good!) | Forced into cluster |
| **Speed** | Fast: O(n*k*d*i) | Slow: O(n²) | Slow: O(n²) |
| **Interpretability** | Simple | Good for outliers | Dendrogram is beautiful |

**When to use**:

- **K-Means**: Quick exploration, known k, scalability needed (millions of points)
- **DBSCAN**: Unknown k, outlier detection, non-spherical clusters
- **Hierarchical**: Small data, want hierarchy, dendrogram visualization

**Example**:
- Customer segments (5-10 clusters) → K-Means
- Detecting anomalies → DBSCAN
- Understanding species taxonomy → Hierarchical

</details>

---

### Question 20
A company has 1M customers, 10K positive examples (1% churn). Cost: keeping customer costs $50/offer, losing customer costs $500. How would you set the classification threshold?

<details>
<summary>Answer</summary>

**Problem**: Standard 0.5 threshold isn't optimal. Different costs = different threshold.

**Analysis**:
- False Positive (offer to not-churner): cost = $50
- False Negative (miss churner): cost = $500
- Ratio: FN cost / FP cost = 500 / 50 = 10x

**Solution**: Use cost-aware threshold

1. Get predicted probabilities for all customers
2. Sweep threshold from 0 to 1, compute cost:
   ```
   Total Cost = FP*50 + FN*500
   ```
3. Find threshold that minimizes cost

**Example**:
- Threshold 0.5: Cost = $100K (many FN, few FP)
- Threshold 0.2: Cost = $80K (fewer FN, more FP, but FN is costlier)
- Threshold 0.1: Cost = $150K (too many FP)

Optimal threshold ≈ 0.2

**Why not 0.5?**: Default threshold assumes equal costs. Here, missing churn is 10x more expensive, so lower threshold (catch more positives even if more false alarms).

**Bonus**: ROC-AUC doesn't depend on threshold. Cost curve analysis does.

</details>

---

## Answer Key Summary

| Q | Answer | Key Concept |
|---|--------|-------------|
| 1 | B | Operator precedence |
| 2 | B | reshape vs flatten |
| 3 | A | groupby-agg |
| 4 | B | Regression vs classification |
| 5 | A | ReLU activation |
| 6 | C | Overfitting |
| 7 | B | StandardScaler |
| 8 | B | Cross-validation |
| 9 | B | Recall (sensitivity) |
| 10 | B | Transfer learning |
| 11 | B | Attention heads |
| 12 | B | Data drift |
| 13 | B | RAG explanation |
| 14 | - | Class imbalance metrics |
| 15 | - | Data leakage in scaling |
| 16 | - | Semantic search architecture |
| 17 | - | End-to-end ML system |
| 18 | - | Fine-tuning regularization |
| 19 | - | Clustering comparison |
| 20 | - | Cost-aware thresholds |

---

## Scoring Guide

- **15-20 correct**: Interview-ready. Deep understanding.
- **12-14 correct**: Solid. Review weak areas before interview.
- **9-11 correct**: Need more prep. Focus on fundamentals.
- **<9 correct**: Review curriculum. You're not ready yet.

---

## How to Use This Quiz

1. **Timed**: Give yourself 45 minutes. Interview is fast-paced.
2. **No notes**: Test yourself, don't cheat.
3. **Review answers**: Spend time understanding why, not just memorizing.
4. **Retake**: After reviewing, retake. Aim for 18+.

Good luck! You've got this.
