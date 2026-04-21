# Python & Machine Learning Glossary

A comprehensive glossary of terms organized by category, covering Python fundamentals through production ML systems.

---

## 1. Python Core

**GIL (Global Interpreter Lock)** — A mutex in CPython that allows only one thread to execute Python bytecode at a time. This simplifies memory management but limits true parallelism for CPU-bound tasks. Use multiprocessing or alternative interpreters (e.g., the free-threaded build in Python 3.13+) to work around it.

**Decorator** — A function that wraps another function or class to modify its behavior without changing its source code. Decorators use the `@` syntax and are commonly used for logging, authentication, caching, and registering functions.

**Generator** — A function that uses `yield` to produce a sequence of values lazily, one at a time, rather than building an entire list in memory. Generators are iterable and are ideal for processing large datasets or infinite sequences.

**Comprehension** — A concise syntax for creating lists, dicts, or sets from iterables. List comprehensions (`[x**2 for x in range(10)]`) are the most common, but dict comprehensions (`{k: v for k, v in pairs}`) and set comprehensions (`{x for x in items}`) follow the same pattern.

**Dunder Method (Magic Method)** — Special methods surrounded by double underscores (e.g., `__init__`, `__repr__`, `__add__`) that define how objects behave with built-in operations and syntax. They let you customize object creation, string representation, arithmetic, comparison, and more.

**Context Manager** — An object that defines `__enter__` and `__exit__` methods, used with the `with` statement to manage resources like file handles or database connections. The `contextlib` module provides shortcuts like `@contextmanager` for creating them from generator functions.

**Metaclass** — A class whose instances are themselves classes. The default metaclass is `type`. Metaclasses control class creation and can be used to enforce coding standards, register classes, or modify class attributes automatically. Most Python developers rarely need to write custom metaclasses.

**Descriptor** — An object that defines `__get__`, `__set__`, or `__delete__` methods, allowing it to customize attribute access on other objects. Properties, class methods, and static methods are all implemented using descriptors under the hood.

**Coroutine** — A function defined with `async def` that can be paused and resumed using `await`. Coroutines are the foundation of Python's asyncio framework for writing concurrent, non-blocking I/O code.

**Walrus Operator (:=)** — The assignment expression operator, introduced in Python 3.8 (PEP 572). It assigns a value to a variable as part of an expression, which is useful in `while` loops and comprehensions to avoid redundant computation. Example: `if (n := len(data)) > 10:`.

**f-string (Formatted String Literal)** — A string prefixed with `f` that allows embedding Python expressions inside curly braces for inline evaluation. Introduced in Python 3.6, f-strings are faster and more readable than `.format()` or `%` formatting. Python 3.12 removed many prior limitations on expressions inside the braces.

**Type Hint (Type Annotation)** — Optional syntax for specifying the expected types of variables, function parameters, and return values. Type hints are not enforced at runtime but enable static analysis tools like mypy and pyright to catch bugs before execution.

**Dataclass** — A decorator (`@dataclasses.dataclass`) that automatically generates `__init__`, `__repr__`, `__eq__`, and other boilerplate methods based on class attributes with type annotations. Dataclasses reduce repetitive code for classes that primarily store data.

**Protocol** — A mechanism for structural subtyping (duck typing with static type checking), introduced in Python 3.8 via `typing.Protocol`. A class satisfies a Protocol if it implements the required methods, without needing explicit inheritance.

**ABC (Abstract Base Class)** — A class from the `abc` module that cannot be instantiated directly and may define abstract methods that subclasses must implement. ABCs enforce interface contracts at class instantiation time.

**PEP (Python Enhancement Proposal)** — A design document that describes a new feature, process, or informational guideline for Python. Notable PEPs include PEP 8 (style guide), PEP 20 (The Zen of Python), and PEP 484 (type hints).

**Virtual Environment** — An isolated Python environment with its own interpreter and installed packages, created with `venv` or third-party tools. Virtual environments prevent dependency conflicts between projects.

**pip** — Python's default package installer, used to install packages from PyPI (the Python Package Index). Common usage: `pip install package_name` or `pip install -r requirements.txt`.

**uv** — A fast Python package installer and project manager written in Rust, developed by Astral. It serves as a drop-in replacement for pip, pip-tools, virtualenv, and more, with dramatically faster dependency resolution and installation.

**pyproject.toml** — The modern standard configuration file for Python projects (PEP 518/621). It consolidates build system requirements, project metadata, and tool configuration (for tools like black, ruff, pytest) into a single file, replacing setup.py and setup.cfg.

**REPL (Read-Eval-Print Loop)** — An interactive shell that reads user input, evaluates it, and prints the result. Python's built-in REPL is launched by typing `python` in the terminal. Enhanced REPLs include IPython and the improved REPL introduced in Python 3.13.

**Unpacking** — The process of extracting values from iterables or mappings into individual variables. Tuple unpacking (`a, b = 1, 2`), starred unpacking (`first, *rest = items`), and dictionary unpacking (`{**d1, **d2}`) are all common forms.

**Slicing** — A syntax for extracting subsequences from sequences using `[start:stop:step]`. Slicing works on strings, lists, tuples, and any object that implements `__getitem__` with a `slice` argument. Negative indices count from the end.

**Mutable / Immutable** — Mutable objects (lists, dicts, sets) can be changed in place after creation. Immutable objects (ints, strings, tuples, frozensets) cannot be modified once created. Understanding mutability is critical for avoiding bugs involving shared references and for using objects as dictionary keys.

**Pythonic** — Code that follows Python's idioms and conventions, emphasizing readability, simplicity, and the effective use of Python-specific features. "Pythonic" code leverages comprehensions, context managers, generators, and built-in functions rather than porting patterns from other languages.

---

## 2. Data Science & NumPy/Pandas

**DataFrame** — A two-dimensional, tabular data structure in pandas (and Polars) with labeled rows and columns. Each column can hold a different data type. DataFrames are the primary object for data manipulation and analysis in Python.

**Series** — A one-dimensional labeled array in pandas, essentially a single column of a DataFrame. A Series has an index and a data type, and supports vectorized operations and alignment by label.

**ndarray (N-dimensional Array)** — NumPy's core data structure: a fixed-size, homogeneous, multidimensional array of numbers. ndarrays support fast element-wise operations and linear algebra, and they form the foundation that pandas, scikit-learn, and other libraries build upon.

**Broadcasting** — A set of rules in NumPy that allow arithmetic operations on arrays with different shapes by automatically expanding the smaller array. For example, adding a scalar to an array or adding a 1D array to each row of a 2D array.

**Vectorization** — The practice of replacing explicit Python loops with array-level operations implemented in compiled C code (via NumPy or pandas). Vectorized code is typically 10-100x faster because it avoids Python's per-element overhead.

**dtype (Data Type)** — The data type of elements in a NumPy array or pandas Series (e.g., `float64`, `int32`, `object`, `category`). Choosing appropriate dtypes affects both memory usage and computation speed.

**Indexing (loc / iloc)** — Methods for selecting data in pandas. `loc` selects by label (row/column names), while `iloc` selects by integer position. Boolean indexing (`df[df['col'] > 5]`) filters rows by condition.

**groupby** — A pandas method that splits a DataFrame into groups based on one or more columns, applies a function to each group, and combines the results. It follows the split-apply-combine pattern and is used for aggregation, transformation, and filtering.

**merge / join** — Operations for combining two DataFrames based on shared columns or indices, analogous to SQL JOIN operations. `merge()` supports inner, outer, left, and right joins. `join()` is a convenience method that joins on indices by default.

**Pivot Table** — A reshaped summary table that aggregates data by grouping rows and columns, similar to pivot tables in spreadsheet software. Created with `df.pivot_table()`, it supports multiple aggregation functions and multi-level grouping.

**Missing Data / NaN** — Represents absent or undefined values in a dataset. pandas uses `NaN` (Not a Number) for float columns and `pd.NA` for nullable integer/boolean types. Handling missing data through dropping, filling, or imputation is a critical step in data preparation.

**Feature** — A measurable property or characteristic of a data point used as input to a model. In tabular data, each column (other than the target) is typically a feature. Also called a variable, predictor, or attribute.

**Observation** — A single data point or record in a dataset, corresponding to one row in a tabular dataset. Also called a sample, instance, or record.

**Correlation** — A statistical measure of the linear relationship between two variables, ranging from -1 (perfect negative) to +1 (perfect positive). Pearson correlation is the most common; Spearman and Kendall measure rank-based relationships.

**Distribution** — The pattern describing how values of a variable are spread or arranged. Common distributions include normal (Gaussian), uniform, binomial, and Poisson. Understanding distributions informs the choice of statistical methods and ML algorithms.

**Normalization** — Rescaling data to a fixed range, typically [0, 1], using min-max scaling. This is useful when features have different units or ranges and you want to give them equal weight. Sensitive to outliers.

**Standardization** — Transforming data to have a mean of 0 and a standard deviation of 1 (z-score scaling). Preferred over normalization when the data contains outliers or when algorithms assume normally distributed features (e.g., SVM, logistic regression).

**One-Hot Encoding** — Converting a categorical variable into a set of binary (0/1) columns, one per category. For example, a "color" column with values [red, blue, green] becomes three columns: `color_red`, `color_blue`, `color_green`. Avoids implying ordinal relationships.

**EDA (Exploratory Data Analysis)** — The process of visually and statistically summarizing a dataset to understand its structure, detect patterns, spot anomalies, and formulate hypotheses before formal modeling. Common tools include histograms, scatter plots, correlation matrices, and summary statistics.

**Data Wrangling** — The process of cleaning, transforming, and restructuring raw data into a format suitable for analysis or modeling. This includes handling missing values, merging datasets, parsing dates, reshaping tables, and correcting data types.

**Imputation** — The process of filling in missing values with estimated substitutes. Common strategies include mean/median imputation, forward/backward fill, and model-based imputation (e.g., KNN imputation). The choice of method can significantly affect model performance.

**Outlier** — A data point that lies significantly outside the expected range of values. Outliers can arise from measurement errors, rare events, or data entry mistakes. Detection methods include IQR (interquartile range), z-scores, and isolation forests.

**Polars** — A high-performance DataFrame library written in Rust, designed as a faster alternative to pandas. Polars uses lazy evaluation, multi-threaded execution, and Apache Arrow as its memory model, making it well-suited for large datasets that would be slow in pandas.

**Lazy Evaluation** — A computation strategy where expressions are not executed immediately but are recorded as a plan and only evaluated when the results are explicitly requested. In Polars, lazy evaluation enables query optimization such as predicate pushdown and projection pruning.

**Method Chaining** — A coding style where multiple method calls are linked together in a single expression (e.g., `df.dropna().groupby('col').mean().reset_index()`). Method chaining produces readable, pipeline-style transformations and avoids intermediate variables.

---

## 3. Machine Learning

**Supervised Learning** — A type of machine learning where the model learns from labeled data (input-output pairs). The goal is to learn a mapping from inputs to outputs so it can predict labels for unseen data. Regression and classification are the two main types.

**Unsupervised Learning** — A type of machine learning where the model learns from unlabeled data, discovering hidden patterns or structure. Common tasks include clustering, dimensionality reduction, and anomaly detection.

**Regression** — A supervised learning task where the target variable is continuous (e.g., predicting house prices, stock values, or temperatures). Common algorithms include linear regression, ridge regression, and gradient boosting regressors.

**Classification** — A supervised learning task where the target variable is categorical (e.g., spam/not-spam, digit recognition). The model assigns each input to one of a predefined set of classes. Common algorithms include logistic regression, random forest, and SVM.

**Clustering** — An unsupervised learning task that groups similar data points together without predefined labels. Popular algorithms include K-Means, DBSCAN, and hierarchical clustering. Clustering is used for customer segmentation, anomaly detection, and data exploration.

**Bias-Variance Tradeoff** — The fundamental tension between a model's ability to fit the training data (low bias) and its ability to generalize to new data (low variance). Simple models tend to have high bias (underfitting); complex models tend to have high variance (overfitting). The goal is to find the sweet spot.

**Overfitting** — When a model learns the training data too well, including its noise and outliers, resulting in poor performance on unseen data. Signs include a large gap between training and validation accuracy. Remedies include regularization, more data, simpler models, and dropout.

**Underfitting** — When a model is too simple to capture the underlying patterns in the data, resulting in poor performance on both training and test data. Remedies include using a more complex model, adding features, or reducing regularization.

**Cross-Validation** — A technique for evaluating model performance by splitting data into multiple folds, training on some folds and testing on the held-out fold, then rotating. K-fold cross-validation (commonly k=5 or 10) provides a more robust estimate of generalization performance than a single train-test split.

**Hyperparameter** — A configuration value set before training begins (e.g., learning rate, number of trees, regularization strength), as opposed to model parameters that are learned during training. Hyperparameters are tuned via grid search, random search, or Bayesian optimization.

**Feature Engineering** — The process of creating new features or transforming existing ones to improve model performance. Examples include creating interaction terms, extracting date components, computing rolling averages, or encoding domain-specific knowledge into the data.

**Feature Selection** — The process of choosing a subset of relevant features to use in model training, removing redundant or irrelevant ones. Methods include filter methods (correlation), wrapper methods (recursive feature elimination), and embedded methods (L1 regularization). Reduces overfitting and training time.

**Regularization (L1/L2)** — Techniques that add a penalty term to the loss function to prevent overfitting. L1 regularization (Lasso) adds the sum of absolute weights, encouraging sparsity. L2 regularization (Ridge) adds the sum of squared weights, encouraging smaller weights. Elastic Net combines both.

**Ensemble Methods** — Techniques that combine multiple models to produce a stronger predictor than any individual model. The main strategies are bagging (parallel, reduces variance), boosting (sequential, reduces bias), and stacking (meta-learning from model outputs).

**Bagging (Bootstrap Aggregating)** — An ensemble method that trains multiple models on random bootstrap samples of the training data and averages their predictions (or takes a majority vote). Bagging reduces variance and is the basis of random forests.

**Boosting** — An ensemble method that trains models sequentially, with each new model focusing on the errors made by the previous ones. Boosting reduces bias and can achieve very high accuracy. Examples include AdaBoost, Gradient Boosting, and XGBoost.

**Random Forest** — An ensemble of decision trees trained using bagging, with an additional randomization step: each tree considers only a random subset of features at each split. Random forests are robust, require minimal tuning, and provide feature importance scores.

**Gradient Boosting** — A boosting technique that builds trees sequentially, with each new tree fitting the negative gradient (residuals) of the loss function. Implementations include scikit-learn's GradientBoostingClassifier, XGBoost, LightGBM, and CatBoost.

**XGBoost (Extreme Gradient Boosting)** — A highly optimized, scalable implementation of gradient boosting that includes regularization, parallel processing, and built-in handling of missing values. XGBoost is one of the most successful algorithms in structured data competitions and industry applications.

**SVM (Support Vector Machine)** — A supervised learning algorithm that finds the hyperplane with the maximum margin separating classes. SVMs can handle non-linear boundaries using kernel functions (e.g., RBF, polynomial). They work well in high-dimensional spaces but can be slow on large datasets.

**KNN (K-Nearest Neighbors)** — A simple algorithm that classifies a data point based on the majority class among its k nearest neighbors (or averages their values for regression). KNN is intuitive and non-parametric but can be slow for large datasets and sensitive to feature scaling.

**Decision Tree** — A model that makes predictions by learning a series of if/else rules that split the data at each node based on feature values. Decision trees are interpretable but prone to overfitting. They form the building blocks of random forests and gradient boosting.

**Precision** — The proportion of positive predictions that are actually correct: TP / (TP + FP). High precision means few false positives. Precision is critical when the cost of false positives is high (e.g., spam detection, fraud alerts).

**Recall (Sensitivity)** — The proportion of actual positives that are correctly identified: TP / (TP + FN). High recall means few false negatives. Recall is critical when missing a positive case is costly (e.g., disease screening, safety systems).

**F1 Score** — The harmonic mean of precision and recall: 2 * (precision * recall) / (precision + recall). F1 balances precision and recall into a single metric and is especially useful when classes are imbalanced and accuracy would be misleading.

**AUC-ROC (Area Under the Receiver Operating Characteristic Curve)** — A metric that measures a classifier's ability to distinguish between classes across all possible thresholds. AUC ranges from 0.5 (random guessing) to 1.0 (perfect separation). It is threshold-independent and useful for comparing models.

**Confusion Matrix** — A table that summarizes a classifier's predictions versus actual labels, showing true positives, false positives, true negatives, and false negatives. It provides a complete picture of classification performance beyond a single accuracy number.

**Pipeline** — In scikit-learn, a `Pipeline` chains together preprocessing steps and a model into a single object that can be fit and predict in one call. Pipelines prevent data leakage by ensuring transformations are fit only on training data and applied consistently.

**Grid Search** — An exhaustive hyperparameter tuning method that evaluates all possible combinations of specified hyperparameter values using cross-validation. `GridSearchCV` in scikit-learn automates this process. For large search spaces, random search or Bayesian optimization is more efficient.

**Optuna** — A Python framework for automatic hyperparameter optimization that uses Bayesian optimization (specifically Tree-structured Parzen Estimators). Optuna supports pruning of unpromising trials, distributed optimization, and integrates with most ML frameworks.

**SHAP (SHapley Additive exPlanations)** — A model interpretability framework based on Shapley values from game theory. SHAP assigns each feature an importance value for a particular prediction, providing both local (per-prediction) and global (overall) explanations of model behavior.

---

## 4. Deep Learning

**Neural Network** — A computational model inspired by the brain, composed of layers of interconnected nodes (neurons) that learn to map inputs to outputs by adjusting connection weights during training. Neural networks can approximate complex, non-linear functions.

**Neuron (Node / Unit)** — The fundamental computational element of a neural network. Each neuron receives inputs, computes a weighted sum plus a bias, applies an activation function, and passes the result to the next layer.

**Activation Function** — A non-linear function applied to a neuron's output to enable the network to learn complex patterns. Common choices include ReLU (most popular for hidden layers), sigmoid (output layer for binary classification), tanh, and softmax (multi-class output).

**Backpropagation** — The algorithm used to compute gradients of the loss function with respect to each weight in the network, by applying the chain rule of calculus layer by layer from output to input. These gradients drive weight updates during training.

**Gradient Descent** — An optimization algorithm that iteratively adjusts model parameters in the direction that reduces the loss function, proportional to the negative gradient. It is the core optimization method behind training neural networks.

**SGD (Stochastic Gradient Descent)** — A variant of gradient descent that updates weights using one sample (or a small mini-batch) at a time rather than the entire dataset. SGD is noisier but much faster and can escape local minima more easily than full-batch gradient descent.

**Adam (Adaptive Moment Estimation)** — An optimizer that combines the benefits of AdaGrad and RMSProp by maintaining per-parameter adaptive learning rates based on first and second moment estimates of the gradients. Adam is the most widely used optimizer in deep learning due to its robustness.

**Learning Rate** — A hyperparameter that controls the size of weight updates during gradient descent. Too high a learning rate causes instability; too low a learning rate causes slow convergence. Learning rate schedulers (e.g., cosine annealing, warm-up) adjust it dynamically during training.

**Epoch** — One complete pass through the entire training dataset. Training typically runs for many epochs (tens to hundreds), with the model's performance monitored on a validation set to decide when to stop (early stopping).

**Batch** — The entire training dataset when processed at once, or the subset of data used in one forward/backward pass. In practice, "batch" often refers to a mini-batch. The batch size affects training speed, memory usage, and generalization.

**Mini-batch** — A small, fixed-size subset of the training data used for each gradient update step. Mini-batch training (common sizes: 32, 64, 128, 256) balances the efficiency of full-batch gradient descent with the noise benefits of stochastic updates.

**Loss Function (Objective Function)** — A function that measures how far the model's predictions are from the true values. Common choices include cross-entropy (classification), mean squared error (regression), and contrastive loss (representation learning). Training minimizes this function.

**CNN (Convolutional Neural Network)** — A neural network architecture that uses convolutional layers to automatically learn spatial hierarchies of features from grid-structured data like images. CNNs apply learnable filters that detect edges, textures, and progressively more complex patterns.

**RNN (Recurrent Neural Network)** — A neural network architecture designed for sequential data, where connections between nodes form directed cycles, allowing the network to maintain a hidden state that captures information from previous time steps. RNNs suffer from vanishing gradients on long sequences.

**LSTM (Long Short-Term Memory)** — A type of RNN that uses gating mechanisms (input, forget, and output gates) to selectively remember or forget information over long sequences. LSTMs largely solved the vanishing gradient problem of vanilla RNNs and were the dominant sequence model before transformers.

**GRU (Gated Recurrent Unit)** — A simplified variant of LSTM with fewer parameters, using only reset and update gates instead of three gates. GRUs achieve similar performance to LSTMs on many tasks while being faster to train.

**Dropout** — A regularization technique that randomly sets a fraction of neuron activations to zero during each training step. This prevents co-adaptation of neurons and reduces overfitting. Dropout is disabled during inference, and outputs are scaled accordingly.

**Batch Normalization** — A technique that normalizes the inputs to each layer by subtracting the batch mean and dividing by the batch standard deviation, then applying learned scale and shift parameters. Batch normalization stabilizes training, allows higher learning rates, and acts as a mild regularizer.

**Transfer Learning** — The practice of taking a model pretrained on a large dataset (e.g., ImageNet for vision, a large text corpus for NLP) and adapting it to a different but related task. Transfer learning dramatically reduces the data and compute needed for new tasks.

**Fine-tuning** — A form of transfer learning where some or all layers of a pretrained model are further trained on a new, typically smaller, task-specific dataset. Fine-tuning adjusts the pretrained weights to specialize them for the target domain.

**Autograd (Automatic Differentiation)** — A system (used in PyTorch, JAX, and other frameworks) that automatically computes gradients by recording operations on tensors and replaying them in reverse. Autograd enables flexible, dynamic computation graphs without manually deriving gradients.

**Tensor** — A multi-dimensional array of numbers, generalizing scalars (0D), vectors (1D), and matrices (2D) to arbitrary dimensions. Tensors are the fundamental data structure in deep learning frameworks like PyTorch and TensorFlow.

**ResNet (Residual Network)** — A deep CNN architecture that introduced skip (residual) connections, allowing gradients to flow directly through the network and enabling training of networks with hundreds of layers. ResNet won the 2015 ImageNet competition and remains a foundational architecture.

**Skip Connection (Residual Connection)** — A shortcut that adds a layer's input directly to its output, bypassing one or more intermediate layers. Skip connections ease gradient flow in deep networks and are a key component of ResNets, transformers, and many other modern architectures.

**Embedding** — A learned, dense vector representation of a discrete input (e.g., a word, token, or category) in a continuous vector space. Embeddings capture semantic relationships; for example, similar words have similar embedding vectors. Used in NLP, recommendation systems, and retrieval.

---

## 5. Transformers & Attention

**Attention Mechanism** — A technique that allows a model to dynamically focus on the most relevant parts of the input when producing each part of the output. Attention computes a weighted sum of value vectors, where the weights are determined by the compatibility between a query and the corresponding keys.

**Self-Attention** — A form of attention where the queries, keys, and values all come from the same sequence. Each position in the sequence attends to all other positions, enabling the model to capture dependencies regardless of distance. Self-attention is the core operation of transformers.

**Multi-Head Attention** — An extension of self-attention that runs multiple attention operations in parallel with different learned projections, then concatenates the results. Multiple heads allow the model to jointly attend to information from different representation subspaces at different positions.

**Transformer** — A neural network architecture introduced in "Attention Is All You Need" (Vaswani et al., 2017) that relies entirely on attention mechanisms, dispensing with recurrence and convolution. Transformers are the foundation of modern NLP (BERT, GPT) and increasingly used in vision and other domains.

**Encoder** — The component of a transformer that processes the input sequence and produces contextual representations. Encoder-only models (e.g., BERT) are well-suited for tasks like classification and named entity recognition. Encoders use bidirectional self-attention.

**Decoder** — The component of a transformer that generates the output sequence, attending to both the encoder's output (in encoder-decoder models) and previously generated tokens. Decoder-only models (e.g., GPT) use causal (masked) self-attention to generate text autoregressively.

**Positional Encoding** — A mechanism for injecting information about token position into the transformer, since self-attention is permutation-invariant and has no inherent notion of order. The original transformer used sinusoidal functions; modern models often use learned positional embeddings or rotary position embeddings (RoPE).

**Layer Normalization** — A normalization technique that normalizes across the feature dimension for each individual sample, rather than across the batch (as in batch normalization). Layer norm is standard in transformers because it works well with variable-length sequences and small batches.

**Feed-Forward Network (FFN)** — The position-wise fully connected network applied independently to each position after the attention sublayer in a transformer block. It typically consists of two linear transformations with a non-linear activation (ReLU or GELU) in between and expands then contracts the dimensionality.

**BERT (Bidirectional Encoder Representations from Transformers)** — A pretrained language model from Google (2018) that uses a masked language model objective and bidirectional self-attention. BERT is fine-tuned for downstream tasks like question answering, sentiment analysis, and named entity recognition.

**GPT (Generative Pre-trained Transformer)** — A family of decoder-only language models from OpenAI that are pretrained on large text corpora using a causal language modeling objective (predicting the next token). GPT models generate text autoregressively and are the basis of ChatGPT and many commercial LLM applications.

**Sequence-to-Sequence (Seq2Seq)** — A model architecture that maps an input sequence to an output sequence, typically using an encoder-decoder structure. Seq2seq models are used for machine translation, summarization, and text generation. The original used RNNs; modern versions use transformers (e.g., T5, BART).

**Masked Language Model (MLM)** — A pretraining objective where random tokens in the input are replaced with a [MASK] token, and the model learns to predict the original tokens from context. MLM is used by BERT and similar encoder models to learn bidirectional representations.

**Causal Language Model (CLM)** — A pretraining objective where the model predicts the next token given all preceding tokens. The model can only attend to tokens to the left (past), enforced by causal masking. CLM is the training objective for GPT and other decoder-only models.

**Tokenizer** — A component that converts raw text into a sequence of tokens (integers) that can be fed into a model. Tokenizers handle splitting text into subwords, mapping tokens to IDs via a vocabulary, and adding special tokens. Common implementations include Hugging Face's `tokenizers` library.

**Vocabulary** — The complete set of tokens that a model knows, each mapped to a unique integer ID. Vocabulary size affects model capacity and memory. Modern LLMs typically have vocabularies of 32,000 to 150,000+ tokens, built using subword tokenization algorithms.

**Subword Tokenization** — A tokenization strategy that splits words into smaller units (subwords) rather than treating whole words or individual characters as tokens. This balances vocabulary size with the ability to represent any text, including rare or unseen words, by composing them from known subwords.

**BPE (Byte Pair Encoding)** — A subword tokenization algorithm that iteratively merges the most frequent pair of adjacent tokens in the training corpus until a target vocabulary size is reached. BPE is used by GPT models and many others. Variants include byte-level BPE, which operates on raw bytes.

**SentencePiece** — A language-independent tokenization library from Google that implements BPE and unigram language model tokenization. Unlike many tokenizers, SentencePiece treats the input as a raw byte stream and does not require pre-tokenization or whitespace splitting, making it truly language-agnostic.

---

## 6. LLMs & Generative AI

**Large Language Model (LLM)** — A neural network (typically a transformer) with billions of parameters, pretrained on vast amounts of text data. LLMs can generate text, answer questions, write code, reason, and perform a wide range of language tasks. Examples include GPT-4, Claude, Llama, and Gemini.

**Pretraining** — The initial phase of training a language model on a large, general-purpose text corpus using a self-supervised objective (e.g., next-token prediction). Pretraining builds broad language understanding and world knowledge before task-specific fine-tuning.

**Instruction Tuning** — A fine-tuning process that trains a pretrained LLM on a dataset of (instruction, response) pairs, teaching the model to follow human instructions rather than simply completing text. Instruction-tuned models (e.g., ChatGPT, Claude) are more useful in conversational settings.

**RLHF (Reinforcement Learning from Human Feedback)** — A training technique where a reward model is trained on human preference data (rankings of model outputs), and the LLM is then fine-tuned using reinforcement learning (typically PPO) to maximize the reward. RLHF aligns model outputs with human values and preferences.

**DPO (Direct Preference Optimization)** — An alternative to RLHF that directly optimizes the language model on preference data without training a separate reward model. DPO is simpler to implement and more stable, achieving results comparable to RLHF with less computational overhead.

**Prompt Engineering** — The practice of designing and refining input prompts to elicit desired behavior from an LLM. Techniques include providing clear instructions, examples, structured formatting, role assignments, and specifying output constraints. Prompt engineering is often the fastest way to improve LLM performance.

**Few-Shot Learning** — A prompting technique where a small number of input-output examples (shots) are included in the prompt to demonstrate the desired task format and behavior. Few-shot learning leverages the model's in-context learning ability without any gradient updates.

**Zero-Shot** — A prompting approach where the model performs a task without any examples, relying only on the instruction and its pretrained knowledge. Zero-shot performance is a key measure of an LLM's general capability and instruction-following ability.

**Chain-of-Thought (CoT)** — A prompting technique that encourages the model to show its reasoning step by step before providing a final answer. Chain-of-thought prompting significantly improves performance on arithmetic, logic, and multi-step reasoning tasks.

**System Prompt** — A special message (typically hidden from the end user) that sets the LLM's behavior, persona, constraints, and instructions for a conversation. System prompts define the context in which the model operates, such as "You are a helpful coding assistant."

**Temperature** — A parameter that controls the randomness of token sampling during text generation. A temperature of 0 produces deterministic (greedy) output; higher temperatures (e.g., 0.7-1.0) increase diversity and creativity; very high temperatures produce incoherent output.

**Top-p (Nucleus Sampling)** — A sampling strategy that selects from the smallest set of tokens whose cumulative probability exceeds a threshold p (e.g., 0.9). Top-p dynamically adjusts the number of candidate tokens, producing more diverse output than top-k when probability distributions vary.

**Top-k** — A sampling strategy that restricts token selection to the k most probable tokens at each generation step. Top-k is simpler than top-p but can be suboptimal when the probability distribution is very peaked or very flat.

**Token** — The basic unit of text that an LLM processes, typically a subword fragment (e.g., "un", "break", "able"). A single word may be one or multiple tokens. Token counts determine input length, output length, and API costs. One token is roughly 3/4 of a word in English.

**Context Window** — The maximum number of tokens an LLM can process in a single input (prompt + generation). Context windows range from 4K to 1M+ tokens in modern models. Longer context windows enable processing larger documents but increase memory and compute requirements.

**RAG (Retrieval-Augmented Generation)** — A technique that enhances LLM responses by retrieving relevant documents from an external knowledge base and including them in the prompt. RAG reduces hallucinations, provides up-to-date information, and allows models to reference specific sources.

**Embedding (in the LLM context)** — A dense vector representation of text (word, sentence, or document) produced by a model, used for semantic similarity, search, and clustering. Embedding models (e.g., OpenAI's text-embedding-3, Sentence-BERT) encode meaning into fixed-size vectors.

**Vector Database** — A specialized database optimized for storing, indexing, and querying high-dimensional embedding vectors by similarity (typically cosine similarity or dot product). Examples include Pinecone, Weaviate, Chroma, Qdrant, and pgvector. Vector databases are a core component of RAG systems.

**Chunking** — The process of splitting long documents into smaller, overlapping pieces (chunks) for embedding and retrieval in RAG systems. Chunk size and overlap strategy significantly affect retrieval quality. Common approaches include fixed-size chunking, sentence-based splitting, and semantic chunking.

**Retrieval** — The process of finding relevant documents or passages from a knowledge base given a query. In RAG, retrieval typically involves encoding the query as an embedding and performing a nearest-neighbor search in a vector database. Hybrid retrieval combines vector search with keyword search (e.g., BM25).

**Hallucination** — When an LLM generates plausible-sounding but factually incorrect or fabricated information. Hallucinations are a fundamental challenge of current LLMs. Mitigation strategies include RAG, grounding, fact-checking, and training-time interventions.

**Grounding** — The practice of connecting LLM outputs to verifiable sources of truth, such as retrieved documents, databases, or API responses. Grounding reduces hallucinations and enables the model to provide citations for its claims.

**Guardrails** — Safety mechanisms that constrain LLM behavior, preventing harmful, biased, or off-topic outputs. Guardrails can be implemented through system prompts, content filters, output validators, or dedicated guardrail frameworks (e.g., NeMo Guardrails, Guardrails AI).

**Red-Teaming** — The practice of systematically probing an AI system for vulnerabilities, biases, and failure modes by having testers attempt to elicit harmful or unintended behaviors. Red-teaming is a critical step in AI safety evaluation before deployment.

**LoRA (Low-Rank Adaptation)** — A parameter-efficient fine-tuning technique that freezes the pretrained model weights and injects trainable low-rank decomposition matrices into each layer. LoRA reduces the number of trainable parameters by 10,000x or more while achieving results comparable to full fine-tuning.

**QLoRA (Quantized LoRA)** — An extension of LoRA that quantizes the base model to 4-bit precision and applies LoRA adapters on top. QLoRA enables fine-tuning of large models (e.g., 65B parameters) on a single consumer GPU with minimal performance degradation.

**PEFT (Parameter-Efficient Fine-Tuning)** — A family of techniques (including LoRA, prefix tuning, adapters, and prompt tuning) that fine-tune only a small subset of model parameters while keeping the majority frozen. PEFT reduces memory, compute, and storage costs relative to full fine-tuning. The Hugging Face `peft` library provides unified implementations.

**Quantization** — The process of reducing the numerical precision of model weights (e.g., from 16-bit float to 4-bit integer) to decrease model size and increase inference speed. Quantization trades a small amount of accuracy for significant memory and compute savings, enabling large models to run on consumer hardware.

**GGUF (GPT-Generated Unified Format)** — A file format for storing quantized language models, used by llama.cpp and compatible tools (e.g., Ollama). GGUF replaced the older GGML format and supports various quantization levels (Q4, Q5, Q8, etc.), metadata, and efficient loading.

**Inference** — The process of using a trained model to generate predictions or outputs on new input data. In the LLM context, inference refers to text generation. Inference optimization (batching, KV caching, speculative decoding) is critical for production deployment.

**Agent** — An AI system that uses an LLM as its reasoning core and can take autonomous actions by calling tools, querying APIs, and making decisions in a loop to accomplish complex tasks. Agents typically follow an observe-think-act cycle and can handle multi-step problems that a single LLM call cannot.

**Tool Use (Function Calling)** — The ability of an LLM to generate structured requests to invoke external functions or APIs rather than answering purely from its training data. Tool use enables LLMs to perform calculations, query databases, search the web, execute code, and interact with external systems.

**Function Calling** — A specific API feature where the LLM is provided with function schemas and can return structured JSON arguments to invoke those functions. The application executes the function and passes the result back to the LLM. Function calling is a key enabler of tool use and agents.

**MCP (Model Context Protocol)** — An open protocol developed by Anthropic that standardizes how AI applications connect to external data sources and tools. MCP provides a universal interface (using a client-server architecture) for LLMs to access files, databases, APIs, and other resources, replacing fragmented custom integrations.

---

## 7. Production & MLOps

**API (Application Programming Interface)** — A set of rules and protocols that allows software components to communicate with each other. In ML, APIs typically expose model predictions as HTTP endpoints that client applications can call with input data and receive predictions in return.

**REST (Representational State Transfer)** — An architectural style for web APIs that uses standard HTTP methods (GET, POST, PUT, DELETE) and stateless communication. RESTful APIs are the most common way to serve ML model predictions over the network.

**FastAPI** — A modern, high-performance Python web framework for building APIs, based on standard type hints. FastAPI automatically generates OpenAPI documentation, validates request/response data with Pydantic, and supports async operations. It is widely used for serving ML models.

**Endpoint** — A specific URL path in an API that handles a particular type of request. For example, `/predict` might accept input data and return model predictions. Each endpoint is associated with a function that processes the request.

**Middleware** — Software that sits between the client request and the application logic, performing cross-cutting operations like authentication, logging, CORS handling, or rate limiting. In FastAPI and other frameworks, middleware intercepts every request and response.

**Docker** — A platform for building, shipping, and running applications in lightweight, portable containers. Docker packages an application and all its dependencies (OS libraries, Python version, packages) into a reproducible image, ensuring consistency across development, testing, and production.

**Container** — A lightweight, isolated runtime environment created from a Docker image. Containers share the host OS kernel but have their own filesystem, network, and process space. They start in seconds and use far fewer resources than virtual machines.

**CI/CD (Continuous Integration / Continuous Deployment)** — Automated practices where code changes are continuously built, tested, and optionally deployed. CI ensures new code does not break existing functionality (via automated tests); CD automates deployment to staging or production environments. Tools include GitHub Actions, GitLab CI, and Jenkins.

**MLflow** — An open-source platform for managing the ML lifecycle, including experiment tracking (logging parameters, metrics, and artifacts), model packaging, model registry, and deployment. MLflow provides a centralized place to compare experiments and reproduce results.

**Model Registry** — A centralized repository for storing, versioning, and managing trained ML models along with their metadata (metrics, parameters, training data lineage). Model registries (e.g., MLflow Model Registry, Weights & Biases) enable governance, approval workflows, and rollback.

**Model Serving** — The process of deploying a trained model to an environment where it can receive input data and return predictions in real time or batch mode. Serving frameworks include TorchServe, TensorFlow Serving, Triton Inference Server, and simple REST APIs with FastAPI.

**Latency** — The time elapsed between sending a request to a model and receiving a response. Low latency is critical for real-time applications like chatbots and recommendation systems. Techniques to reduce latency include model optimization, caching, quantization, and edge deployment.

**Throughput** — The number of requests or predictions a system can handle per unit of time (e.g., requests per second). High throughput is important for serving models at scale. Batching, horizontal scaling, and GPU optimization improve throughput.

**Monitoring** — The continuous observation of a deployed ML system's performance, data quality, and operational health. Monitoring detects issues like model degradation, data drift, and system failures. Tools include Prometheus, Grafana, WhyLabs, and Evidently.

**Drift Detection** — The process of identifying changes in the statistical properties of input data (data drift) or the relationship between inputs and outputs (concept drift) after a model is deployed. Drift detection signals that a model may need retraining. Methods include statistical tests (KS test, PSI) and monitoring dashboards.

**A/B Testing** — A method for comparing two versions of a model (or any system component) by randomly routing a portion of traffic to each version and measuring performance differences. A/B testing provides statistical evidence for whether a new model version improves key metrics.

**Canary Deployment** — A deployment strategy where a new model version is gradually rolled out to a small percentage of traffic before full deployment. If the canary version performs well, traffic is progressively shifted; if issues arise, traffic is routed back to the stable version. This minimizes the blast radius of bad deployments.

**SageMaker** — Amazon Web Services' fully managed platform for building, training, and deploying ML models. SageMaker provides built-in algorithms, notebook instances, distributed training, hyperparameter tuning, model hosting, and MLOps pipelines, all integrated with the AWS ecosystem.

**Vertex AI** — Google Cloud's unified ML platform for building, deploying, and managing ML models. Vertex AI provides AutoML, custom training, model registry, feature store, pipelines, and prediction serving. It integrates with BigQuery, TensorFlow, and the broader Google Cloud ecosystem.

**Serverless** — A cloud computing model where the cloud provider manages the infrastructure and automatically scales resources based on demand. In ML, serverless deployments (e.g., AWS Lambda, Google Cloud Functions, or serverless GPU inference) eliminate the need to manage servers and scale to zero when idle, reducing costs for intermittent workloads.

---

*Last updated: 2026-04-20*
