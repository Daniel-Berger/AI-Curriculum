"""
Coding Challenges for AI/ML Interviews

20 exercises across 4 categories:
- Data Manipulation (5): pandas, nested data, aggregation
- API Integration (5): clients, pagination, streaming
- Algorithms (5): classic + ML-relevant
- ML Coding (5): pipelines, metrics, validation
"""

from typing import Any, Dict, List, Tuple, Optional, Union
import json
from datetime import datetime


# ============================================================================
# CATEGORY 1: DATA MANIPULATION (5 exercises)
# ============================================================================

def exercise_1_parse_nested_json(data: Union[str, Dict]) -> List[Dict[str, Any]]:
    """
    Parse nested JSON and extract all user engagement metrics.

    Input: JSON string or dict with structure:
    {
        "success": true,
        "data": {
            "users": [
                {
                    "id": "user1",
                    "profile": {"name": "Alice"},
                    "metrics": {
                        "daily": [
                            {"date": "2024-01-01", "views": 100, "clicks": 10}
                        ],
                        "summary": {"total_views": 5000}
                    }
                }
            ]
        }
    }

    Return: List of dicts with {user_id, name, total_views, daily_metrics_count}

    Handle:
    - Missing 'data' key
    - Empty or missing 'users' array
    - Missing nested fields (profile, metrics, etc.)
    - Gracefully skip malformed entries
    """
    pass


def exercise_2_aggregate_time_series(
    data: List[Dict[str, Union[str, float]]],
    timestamp_col: str = "timestamp",
    value_col: str = "value"
) -> Dict[str, float]:
    """
    Aggregate hourly time series data to daily statistics.

    Input: List of dicts with timestamp and numeric value
    Example:
    [
        {"timestamp": "2024-01-01T10:00:00", "value": 100},
        {"timestamp": "2024-01-01T11:00:00", "value": 110},
        ...
    ]

    Return: Dict with date as key, dict of {mean, min, max, count} as value
    Example: {"2024-01-01": {"mean": 105.0, "min": 100, "max": 110, "count": 2}}

    Handle:
    - Missing or invalid timestamps
    - Non-numeric values
    - Gaps in time series (skip missing hours)
    - Multiple entries per day
    """
    pass


def exercise_3_pivot_table(
    data: List[Dict[str, Any]],
    index_col: str,
    column_col: str,
    value_col: str
) -> Dict[str, Dict[str, Any]]:
    """
    Convert long-format data to wide-format pivot table.

    Input: List of dicts (long format)
    Example:
    [
        {"product": "A", "region": "North", "sales": 100},
        {"product": "A", "region": "South", "sales": 150},
        {"product": "B", "region": "North", "sales": 200},
    ]

    Return: Dict (wide format)
    Example:
    {
        "A": {"North": 100, "South": 150},
        "B": {"North": 200}
    }

    Handle:
    - Duplicate entries (raise error or aggregate?)
    - Missing values (skip or None?)
    - Non-string index/column values
    """
    pass


def exercise_4_merge_datasets(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
    left_key: str,
    right_key: str,
    how: str = "inner"
) -> List[Dict[str, Any]]:
    """
    Merge two datasets on a key column (like SQL JOIN).

    Input:
    left = [{"user_id": 1, "name": "Alice"}, ...]
    right = [{"user_id": 1, "score": 95}, ...]

    Return: Merged list of dicts

    Support how in: "inner", "left", "right", "outer"
    - inner: only matching keys (default)
    - left: all left rows, matching right cols
    - right: all right rows, matching left cols
    - outer: all rows from both, NaN where no match

    Handle:
    - Duplicate keys in either dataset
    - Key type mismatches (int vs str)
    - Overlapping column names (prefix with left/right?)
    """
    pass


def exercise_5_clean_messy_data(
    data: List[Dict[str, Any]],
    schema: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Clean and standardize messy data using a schema.

    Input:
    data = [
        {"age": "25", "salary": "$100,000", "status": "ACTIVE", "email": "  alice@example.com  "},
        {"age": "N/A", "salary": "unknown", "status": "inactive", "email": "bob@example.com"},
    ]
    schema = {
        "age": "int",        # Convert to int, skip if invalid
        "salary": "float",   # Remove $ and commas, convert to float
        "status": "category", # Lowercase, map to standard values
        "email": "string"    # Lowercase, strip whitespace
    }

    Return: Cleaned list of dicts with invalid rows removed

    Handle:
    - Type conversions with fallback
    - String normalization (whitespace, case)
    - Currency parsing ($X,XXX format)
    - Category mapping (ACTIVE -> active)
    - Skip completely invalid rows
    """
    pass


# ============================================================================
# CATEGORY 2: API INTEGRATION (5 exercises)
# ============================================================================

def exercise_6_build_api_client(
    base_url: str,
    api_key: str,
    timeout: int = 30
) -> object:
    """
    Create a simple API client class with centralized request handling.

    The client should:
    - Store base_url, api_key, timeout as instance variables
    - Have a method: request(method: str, endpoint: str, **kwargs) -> dict
      - Constructs full URL: base_url + endpoint
      - Adds Authorization header with api_key
      - Adds timeout
      - Returns parsed JSON response
      - Raises custom exception on error (4xx, 5xx)
    - Have convenience methods: get(endpoint, **kwargs), post(endpoint, json, **kwargs)

    Return: Instance of APIClient

    Example usage:
    client = exercise_6_build_api_client("https://api.example.com", "my_key")
    response = client.get("users/123")
    """
    pass


def exercise_7_handle_pagination(
    fetch_func: callable,
    endpoint: str,
    total_limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Fetch all results from a paginated API.

    The fetch_func simulates an API with cursor-based pagination:
    - fetch_func(endpoint, params) returns:
      {
          "data": [item1, item2, ...],
          "next_cursor": "abc123" or None if last page
      }
    - Each page has max 100 items
    - Stop when next_cursor is None or total_limit reached

    Input:
    - fetch_func: callable that takes (endpoint, params) dict
    - endpoint: str like "/users"
    - total_limit: max items to fetch

    Return: List of all items from all pages

    Handle:
    - Stop condition (next_cursor is None)
    - Respect total_limit
    - Empty responses
    """
    pass


def exercise_8_retry_with_backoff(
    fetch_func: callable,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Any:
    """
    Retry a function with exponential backoff.

    Implementation:
    - Call fetch_func()
    - If it raises an exception (simulating HTTP error):
      - Retry up to max_retries times
      - Wait base_delay, 2*base_delay, 4*base_delay, ... seconds between attempts
      - Double delay each time
    - Return result on success
    - Raise exception if all retries fail

    The fetch_func may raise Exception or return None to simulate failures.

    Example: retry_with_backoff(lambda: requests.get(url), max_retries=3)
    """
    pass


def exercise_9_parse_streaming_response(
    response_text: str,
    format: str = "jsonl"
) -> List[Dict[str, Any]]:
    """
    Parse streaming response (JSONL or newline-delimited JSON).

    Input: String with multiple lines, each line is valid JSON
    Example:
    '{"id": 1, "text": "hello"}\n{"id": 2, "text": "world"}'

    format can be:
    - "jsonl": JSON Lines (one JSON object per line)
    - "sse": Server-Sent Events (lines prefixed with "data: ")

    Return: List of parsed JSON objects

    Handle:
    - Empty lines
    - Invalid JSON on a line (skip or error?)
    - SSE format with "data:" prefix
    """
    pass


def exercise_10_batch_api_calls(
    items: List[Any],
    batch_size: int = 100
) -> List[Dict[str, Any]]:
    """
    Process items in batches to simulate a batch API endpoint.

    Input:
    - items: List of items to process
    - batch_size: Max items per batch

    Simulate calling a batch API:
    - Divide items into chunks of batch_size
    - For each batch, simulate API call: batch_process(batch)
    - Combine results

    Mock batch_process function returns:
    {"results": [{"input": item, "processed": True}], "duration_ms": 50}

    Return: Combined list of all processed results
    """
    pass


# ============================================================================
# CATEGORY 3: ALGORITHMS (5 exercises)
# ============================================================================

def exercise_11_lru_cache(capacity: int) -> object:
    """
    Implement an LRU (Least Recently Used) Cache.

    The cache should:
    - Store up to `capacity` items
    - When capacity is exceeded, evict the least recently used item
    - Both get() and put() count as "using" an item

    Return: LRUCache instance with methods:
    - get(key: int) -> int: Return value or -1 if not found
    - put(key: int, value: int) -> None: Insert or update

    Example:
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.get(1)  # returns 1
    cache.put(3, 3)  # evicts key 2
    cache.get(2)  # returns -1

    Implement with dict + doubly linked list for O(1) operations.
    """
    pass


def exercise_12_cosine_similarity(
    vec_a: List[float],
    vec_b: List[float]
) -> float:
    """
    Calculate cosine similarity between two vectors.

    Formula: similarity = (A · B) / (||A|| * ||B||)

    Input:
    - vec_a, vec_b: Lists of floats, same length

    Return: Float between -1 and 1
    - 1.0: identical direction
    - 0.0: orthogonal
    - -1.0: opposite direction

    Handle:
    - Zero vectors (denominator = 0)
    - Empty vectors
    - Different lengths (error or pad with zeros?)
    """
    pass


def exercise_13_tfidf_vectorizer(
    documents: List[str]
) -> Tuple[List[str], List[List[float]]]:
    """
    Compute TF-IDF vectors for a list of documents (no library).

    Input: List of document strings

    Return: Tuple of (vocab, vectors)
    - vocab: Sorted list of unique words
    - vectors: List of TF-IDF vectors (one per document)
    Each vector is a list of floats matching vocab order.

    Algorithm:
    1. Tokenize: split by whitespace, lowercase, remove punctuation
    2. Build vocabulary from all documents
    3. For each document:
       - TF(word) = count(word) / total_words_in_doc
       - IDF(word) = log(num_docs / num_docs_with_word)
       - TF-IDF(word) = TF * IDF

    Handle:
    - Case insensitivity
    - Punctuation removal
    - Words appearing in all documents (low IDF)
    - Zero vectors
    """
    pass


def exercise_14_kmeans_clustering(
    points: List[List[float]],
    k: int,
    max_iterations: int = 100
) -> Tuple[List[List[float]], List[int]]:
    """
    K-Means clustering from scratch (no library).

    Input:
    - points: List of [x, y] coordinates
    - k: Number of clusters
    - max_iterations: Stop criterion

    Return: Tuple of (centroids, labels)
    - centroids: k center points
    - labels: Cluster assignment for each point (0 to k-1)

    Algorithm:
    1. Initialize k centroids randomly from points
    2. Repeat until convergence or max_iterations:
       a. Assign each point to nearest centroid
       b. Recompute centroids as mean of assigned points
       c. Check for convergence (no points changed clusters)

    Handle:
    - k > num_points (error)
    - Convergence detection
    - Deterministic initialization (use sorted points)
    """
    pass


def exercise_15_binary_search(
    sorted_array: List[int],
    target: int
) -> int:
    """
    Binary search for target in sorted array.

    Input:
    - sorted_array: Sorted list of integers (ascending)
    - target: Value to search for

    Return: Index of target if found, -1 if not found

    Requirements:
    - O(log n) time complexity
    - Handle edge cases: empty array, single element, duplicates
    - Don't use Python's built-in search

    Example:
    binary_search([1, 3, 5, 7, 9], 5) -> 2
    binary_search([1, 3, 5, 7, 9], 4) -> -1
    """
    pass


# ============================================================================
# CATEGORY 4: ML CODING (5 exercises)
# ============================================================================

def exercise_16_cross_validation(
    X: List[List[float]],
    y: List[int],
    model_class: type,
    k: int = 5
) -> Dict[str, float]:
    """
    Implement k-fold cross-validation for model evaluation.

    Input:
    - X: List of feature vectors (same length as y)
    - y: List of labels
    - model_class: Class with fit(X, y) and predict(X) methods
    - k: Number of folds

    Return: Dict with keys:
    - "train_scores": List of k training accuracies
    - "test_scores": List of k test accuracies
    - "mean_test_score": Average test accuracy
    - "std_test_score": Std dev of test accuracies

    Algorithm:
    1. Divide data into k folds
    2. For each fold i:
       - Test set = fold i
       - Train set = all other folds
       - Train model on train set
       - Evaluate on both train and test
    3. Return scores

    Handle:
    - k > len(X) (error)
    - k = 1 (no meaningful cross-validation)
    - Stratified split (optional: preserve class distribution)
    """
    pass


def exercise_17_simple_pipeline(
    X_train: List[List[float]],
    y_train: List[int],
    X_test: List[List[float]]
) -> List[int]:
    """
    Build and fit a simple preprocessing + model pipeline.

    Pipeline steps:
    1. Standardize features: (X - mean) / std
    2. Reduce dimensionality with PCA (keep top 2 components)
    3. Train logistic regression

    Input:
    - X_train, y_train: Training data
    - X_test: Test data

    Return: Predictions on X_test

    Handle:
    - Fit standardizer and PCA on train only
    - Apply same transformations to test
    - Prevent data leakage (fit on train, not test)

    Note: Implement standardization and PCA manually or use a simple approach.
    """
    pass


def exercise_18_feature_engineering(
    data: List[Dict[str, Any]]
) -> Tuple[List[List[float]], List[str]]:
    """
    Transform raw data into machine-learning features.

    Input: List of dicts
    [
        {"timestamp": "2024-01-01T10:30:00", "price": 100.5, "category": "A"},
        ...
    ]

    Return: Tuple of (feature_matrix, feature_names)
    - feature_matrix: List of feature vectors
    - feature_names: List of column names

    Required features:
    1. Hour extracted from timestamp (0-23)
    2. Day of week (0-6)
    3. Price (continuous)
    4. Category one-hot encoded (A -> [1, 0, 0], B -> [0, 1, 0], etc.)
    5. Interaction: price * hour

    Handle:
    - Missing values
    - Invalid timestamps
    - Unknown categories (map to 0 or new category?)
    """
    pass


def exercise_19_compute_metrics(
    y_true: List[int],
    y_pred: List[int]
) -> Dict[str, float]:
    """
    Compute classification metrics from scratch (no library).

    Input:
    - y_true: Ground truth labels (0 or 1)
    - y_pred: Predicted labels (0 or 1)

    Return: Dict with keys:
    - "accuracy": (TP + TN) / Total
    - "precision": TP / (TP + FP)
    - "recall": TP / (TP + FN)
    - "f1": 2 * (precision * recall) / (precision + recall)
    - "specificity": TN / (TN + FP)
    - "false_positive_rate": FP / (FP + TN)

    Where:
    - TP: True Positives (y_true=1, y_pred=1)
    - TN: True Negatives (y_true=0, y_pred=0)
    - FP: False Positives (y_true=0, y_pred=1)
    - FN: False Negatives (y_true=1, y_pred=0)

    Handle:
    - Division by zero (return 0 or NaN?)
    - Mismatched lengths
    - Invalid labels
    """
    pass


def exercise_20_confusion_matrix(
    y_true: List[int],
    y_pred: List[int],
    labels: Optional[List[int]] = None
) -> Dict[str, Dict[str, int]]:
    """
    Build confusion matrix and compute derived metrics.

    Input:
    - y_true: Ground truth labels
    - y_pred: Predicted labels
    - labels: List of unique labels (auto-detect if None)

    Return: Dict representation of confusion matrix
    Format:
    {
        "matrix": [[TN, FP], [FN, TP]],  # for binary classification
        "tp": int,
        "tn": int,
        "fp": int,
        "fn": int,
        "sensitivity": float,  # TP / (TP + FN)
        "specificity": float,  # TN / (TN + FP)
        "ppv": float,          # TP / (TP + FP) - Positive Predictive Value
        "npv": float           # TN / (TN + FN) - Negative Predictive Value
    }

    Support multi-class confusion matrix:
    - Row i, Col j = count where y_true=i, y_pred=j

    Handle:
    - Binary vs multi-class
    - Missing labels
    - Imbalanced classes
    """
    pass


# ============================================================================
# Tests
# ============================================================================

if __name__ == "__main__":
    print("All 20 coding challenge exercises defined.")
    print("\nImplement each exercise function and run comprehensive tests.")
    print("\nCategories:")
    print("  1. Data Manipulation (exercises 1-5)")
    print("  2. API Integration (exercises 6-10)")
    print("  3. Algorithms (exercises 11-15)")
    print("  4. ML Coding (exercises 16-20)")
