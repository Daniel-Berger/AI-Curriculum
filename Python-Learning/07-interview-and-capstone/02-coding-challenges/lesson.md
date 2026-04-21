# Coding Challenges for AI/ML Interviews

## Overview

Coding interviews for ML/AI roles test your ability to:
- **Manipulate data** efficiently (pandas, numpy, raw Python)
- **Integrate with APIs** and handle real-world complexities
- **Implement algorithms** from scratch (search, clustering, similarity)
- **Write ML-adjacent code** (cross-validation, pipelines, metrics)

This is NOT about memorizing LeetCode solutions. It's about demonstrating:
- Clean, readable code with proper error handling
- Understanding of complexity and optimization
- Ability to explain design choices
- Knowledge of standard libraries and when to use them

---

## Data Manipulation Patterns

### 1. Nested Data Processing

**Interview Question**: "Parse this JSON and extract user engagement metrics."

**Key Concept**: Use recursion, generators, or comprehensions to traverse nested structures without getting lost.

```python
# DON'T: Write fragile code that assumes structure
user_data = response['data']['users'][0]['metrics']['daily']

# DO: Use .get() and handle missing keys
metrics = response.get('data', {}).get('users', [{}])[0].get('metrics', {})
```

**Interview Tips**:
- Ask clarifying questions: Are there missing fields? Inconsistent nesting?
- Use `dict.get()` with defaults
- Consider using `jsonpath` for complex queries
- Test with edge cases (empty dicts, missing keys, None values)

### 2. Time Series Aggregation

**Pattern**: Group by time window, apply aggregation, handle gaps.

```python
# Group hourly data by day, compute daily mean
daily = df.set_index('timestamp').resample('D').agg({'value': 'mean'})
```

**Interview Tips**:
- Always sort by timestamp first
- Use pandas `resample()` for regular intervals
- Handle missing intervals (forward-fill, interpolation, or drop)
- Explain timezone handling if needed

### 3. Data Pivoting

**Pattern**: Reshape data from long to wide format or vice versa.

```python
# Wide to long: df.melt()
# Long to wide: df.pivot() or df.pivot_table()
```

**Interview Tips**:
- Pivot vs pivot_table: pivot fails on duplicates, pivot_table aggregates
- Always verify shape before/after
- Consider memory impact for large datasets

### 4. Dataset Merging

**Pattern**: Join two tables, handle duplicates and mismatches.

**Interview Tips**:
- Know the difference: inner, left, right, outer joins
- Always check for duplicate keys before joining
- Verify row count makes sense after join
- Use `validate` parameter: `merge(..., validate='one_to_one')`

### 5. Data Cleaning

**Dirty Data Reality**: 80% of data work is cleaning, 20% is modeling.

**Common Issues**:
- Missing values: NaN, None, empty strings, "N/A", -999
- Duplicates: exact and fuzzy
- Type mismatches: "123" vs 123
- Outliers: data entry errors or real extremes?
- Inconsistent formatting: whitespace, casing, units

**Interview Strategy**:
1. Understand the data semantics
2. Decide on strategy per column (drop, fill, transform)
3. Document assumptions
4. Validate results

---

## API Integration Patterns

### 1. Building an API Client

**Structure**:
```python
class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {api_key}'}

    def request(self, method, endpoint, **kwargs):
        # Central place for headers, error handling, retries
        url = f'{self.base_url}/{endpoint}'
        return requests.request(method, url, headers=self.headers, **kwargs)
```

**Why**: Centralize configuration, error handling, and logging.

### 2. Pagination

**Common Patterns**:
- **Offset-based**: `?offset=0&limit=100`
- **Cursor-based**: `?cursor=abc123` (preferred, handles real-time changes)
- **Page-based**: `?page=1&per_page=100`

**Implementation**:
```python
def fetch_all(endpoint):
    results = []
    cursor = None
    while True:
        params = {'limit': 100}
        if cursor:
            params['cursor'] = cursor
        resp = client.get(endpoint, params=params)
        results.extend(resp['data'])
        cursor = resp.get('next_cursor')
        if not cursor:
            break
    return results
```

**Interview Tips**:
- Ask about pagination strategy upfront
- Stop condition: next_cursor is None, page has < limit items, or explicit flag
- Consider rate limiting in your loop
- Test with small datasets first

### 3. Retry Logic

**Real World**: APIs are unreliable. Network hiccups, transient errors (5xx), rate limits (429).

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_data():
    return requests.get(url)
```

**When to Retry**:
- 5xx errors: transient server issues
- 429 (Too Many Requests): wait and retry
- Network timeouts: maybe

**Don't Retry**:
- 4xx errors (except 429): client fault, won't be fixed by retrying
- 401, 403: auth issues

### 4. Streaming Responses

**Pattern**: For large responses, don't load all in memory.

```python
resp = requests.get(url, stream=True)
for line in resp.iter_lines():
    data = json.loads(line)
    process(data)  # Process incrementally
```

**Use Cases**:
- Large CSV/JSON files
- Server-Sent Events (SSE)
- WebSocket alternatives

### 5. Batch API Calls

**Pattern**: Multiple operations in one request.

```python
# DON'T: Individual calls in a loop
for user_id in user_ids:
    user = api.get_user(user_id)

# DO: Batch endpoint
users = api.get_users(user_ids)  # Single request
```

**Interview Tips**:
- Ask if a batch endpoint exists
- If not, implement concurrent calls with rate limiting
- Consider memory vs time tradeoff

---

## Algorithm Patterns

### 1. LRU Cache

**Why**: Common in systems design (memoization, caching, eviction).

**Core Idea**: Fixed-size cache, evict least-recently-used item when full.

**Data Structure**: HashMap + Doubly Linked List.

**Operations**:
- Get: O(1) lookup, move to front
- Put: O(1) insert/update, move to front, evict if full

### 2. Similarity Metrics

**Cosine Similarity**: Measures angle between vectors, ignores magnitude.
```
similarity = (A · B) / (||A|| * ||B||)
```

**When to use**: Text (TF-IDF vectors), recommendations, semantic search.

**Properties**: -1 to 1, where 1 = identical direction, 0 = orthogonal, -1 = opposite.

### 3. TF-IDF from Scratch

**Intuition**: Common words (the, a, is) are less informative. Rare words are more informative.

**Formula**:
```
TF(term, doc) = count(term, doc) / count(all terms, doc)
IDF(term, corpus) = log(total docs / docs containing term)
TF-IDF = TF * IDF
```

**Interview Tips**:
- Explain why logarithm in IDF (handles scale)
- Discuss smoothing for unseen terms
- Common variant: log-normalized TF

### 4. K-Means from Scratch

**Algorithm**:
1. Initialize K random centroids
2. Assign each point to nearest centroid
3. Recompute centroids as mean of assigned points
4. Repeat until convergence

**Interview Tips**:
- Explain convergence criterion
- Discuss initialization (K-means++ is better)
- Complexity: O(n*k*d*i) where i = iterations
- Limitations: sensitive to initial centroids, doesn't handle non-spherical clusters

### 5. Binary Search

**Variants**:
- **Exact match**: Standard binary search
- **First/Last occurrence**: With duplicates
- **Search in rotated array**: With rotation point
- **Find insertion position**: For sorted insert

**Interview Tips**:
- Always verify array is sorted
- Off-by-one errors are common: test with 1-2 element arrays
- Use `mid = left + (right - left) // 2` to avoid overflow
- Clearly define invariants (what's in left vs right half)

---

## ML Coding Patterns

### 1. Cross-Validation

**Why**: Single train/test split is unreliable. CV gives robust estimate.

**Strategies**:
- **K-Fold**: Divide into K folds, train K times (leave one out)
- **Stratified K-Fold**: Preserve class distribution (for imbalanced data)
- **Time Series Split**: Respect temporal order

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)
print(f'Mean: {scores.mean():.3f}, Std: {scores.std():.3f}')
```

### 2. ML Pipeline

**Pattern**: Chain transformations and model in reproducible way.

```python
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=10)),
    ('model', LogisticRegression())
])
pipeline.fit(X_train, y_train)
```

**Benefits**: Prevents data leakage, easier hyperparameter tuning, reproducible preprocessing.

### 3. Feature Engineering

**Common Techniques**:
- **Scaling**: StandardScaler, MinMaxScaler, RobustScaler
- **Encoding**: OneHotEncoder, LabelEncoder
- **Binning**: Discretize continuous features
- **Interactions**: Create feature products
- **Domain features**: Leverage domain knowledge (e.g., time-based features from timestamp)

### 4. Evaluation Metrics from Scratch

**Classification**:
- **Accuracy**: (TP + TN) / Total (misleading on imbalanced data)
- **Precision**: TP / (TP + FP) (false alarm rate)
- **Recall**: TP / (TP + FN) (miss rate)
- **F1**: 2 * (Precision * Recall) / (Precision + Recall)

**Regression**:
- **MAE**: Mean absolute error
- **RMSE**: Root mean squared error (penalizes large errors)
- **R²**: Coefficient of determination (proportion of variance explained)

### 5. Confusion Matrix

**Structure**:
```
         Predicted Positive  Predicted Negative
Actual Positive    TP                 FN
Actual Negative    FP                 TN
```

**Derived Metrics**:
- Sensitivity (Recall): TP / (TP + FN)
- Specificity: TN / (TN + FP)
- False Positive Rate: FP / (FP + TN)
- False Negative Rate: FN / (TP + FN)

---

## Interview Strategy

### Before You Code

1. **Understand the problem**: Ask clarifying questions
   - Input/output format and size
   - Edge cases (empty, None, duplicates)
   - Performance requirements
   - Library constraints (can I use pandas? numpy? sklearn?)

2. **Design before implementing**:
   - Describe the approach in plain English
   - Discuss complexity
   - Walk through an example

### While Coding

1. **Start simple**: Get a working solution, then optimize
2. **Test as you go**: Small unit tests, not full suite
3. **Handle edge cases**: Empty inputs, None values, type mismatches
4. **Add type hints**: Shows you write production code

### After Coding

1. **Walk through your code**: Narrate what you're doing
2. **Discuss complexity**: Time and space
3. **Mention improvements**: What would you do with more time?
4. **Be honest about unknowns**: "I'd look up the exact API" is better than guessing

---

## Common Mistakes to Avoid

| Mistake | Fix |
|---------|-----|
| No error handling | Add try/except, validate inputs |
| Hardcoded values | Use parameters, config |
| No tests | Write assertions, test edge cases |
| Ignoring complexity | Discuss O(n) vs O(n²) |
| No type hints | Add them: helps reader and catches bugs |
| Magic numbers | Use named constants |
| Forgetting docstrings | One-liner minimum |

---

## Complexity Cheat Sheet

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| List append | O(1) amortized | O(1) | |
| List insert(0) | O(n) | O(1) | avoid! |
| Dict/set lookup | O(1) average | O(n) | |
| Sorting | O(n log n) | O(n) | merge/quick |
| Binary search | O(log n) | O(1) | requires sorted |
| DF groupby | O(n) | O(n) | with aggregation |
| Matrix mult | O(n³) | O(n²) | numpy optimized |

---

## Resources

- **Pandas**: Official docs, focus on `groupby`, `merge`, `resample`
- **NumPy**: Broadcasting, vectorization, avoid loops
- **Requests**: Session for connection pooling, timeouts always
- **Algorithm visualization**: https://visualgo.net/
- **Complexity reference**: Keep a cheat sheet handy

---

## Practice Strategy

1. **Weekly focus**: Pick one pattern per week
2. **Read others' solutions**: Learn different approaches
3. **Time yourself**: Simulate interview pressure
4. **Explain out loud**: Practice verbal communication
5. **Refactor before moving on**: Make it production-ready

Good luck! You've got this.
