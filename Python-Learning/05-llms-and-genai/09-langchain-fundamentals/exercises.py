"""
Module 09: LangChain Fundamentals - Exercises
==============================================
Target audience: Swift developers learning Python and LangChain.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Some exercises require langchain packages: pip install langchain langchain-anthropic langchain-core
- Exercises are designed to work with mock objects where possible.
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.

Difficulty levels:
  Easy   - Direct application of a single LangChain concept
  Medium - Combines multiple concepts or requires chain composition
  Hard   - Builds complex multi-step chains or requires creative LCEL usage
"""

from typing import Any


# =============================================================================
# SETUP: Mock classes for exercises that don't need real API calls
# =============================================================================

class MockChatModel:
    """Simulates a chat model for testing chains without API keys."""

    def __init__(self, responses: list[str] | None = None):
        self._responses = responses or ["Mock response"]
        self._call_count = 0

    def invoke(self, messages, **kwargs) -> "MockAIMessage":
        response = self._responses[self._call_count % len(self._responses)]
        self._call_count += 1
        return MockAIMessage(content=response)

    def __or__(self, other):
        """Support pipe operator for LCEL."""
        from langchain_core.runnables import RunnableSequence
        return RunnableSequence(first=self, last=other)


class MockAIMessage:
    """Simulates an AIMessage."""

    def __init__(self, content: str):
        self.content = content


# =============================================================================
# EXERCISE 1: Create a Chat Prompt Template
# Difficulty: Easy
# =============================================================================

def create_translation_prompt() -> Any:
    """Create a ChatPromptTemplate for translating text.

    The template should:
    - Have a system message: "You are a translator. Translate text to {language}."
    - Have a human message: "{text}"
    - Accept two variables: 'language' and 'text'

    Returns:
        A ChatPromptTemplate instance.

    >>> prompt = create_translation_prompt()
    >>> result = prompt.invoke({"language": "Spanish", "text": "Hello"})
    >>> len(result.messages) == 2
    True
    >>> "Spanish" in result.messages[0].content
    True
    >>> result.messages[1].content == "Hello"
    True
    """
    pass


# =============================================================================
# EXERCISE 2: Build a Few-Shot Prompt
# Difficulty: Medium
# =============================================================================

def create_sentiment_prompt() -> Any:
    """Create a few-shot ChatPromptTemplate for sentiment analysis.

    The template should:
    - Have a system message: "Classify the sentiment as positive, negative, or neutral."
    - Include these examples:
        - input: "I love this product!" -> output: "positive"
        - input: "This is terrible." -> output: "negative"
        - input: "The meeting is at 3pm." -> output: "neutral"
    - Have a final human message: "{input}"

    Returns:
        A ChatPromptTemplate instance.

    >>> prompt = create_sentiment_prompt()
    >>> result = prompt.invoke({"input": "Great weather today!"})
    >>> len(result.messages) >= 8  # system + 3 pairs + human
    True
    """
    pass


# =============================================================================
# EXERCISE 3: Use StrOutputParser in a Chain
# Difficulty: Easy
# =============================================================================

def build_simple_chain(model: Any) -> Any:
    """Build a simple LCEL chain: prompt | model | parser.

    The chain should:
    - Use a prompt template: "Explain {concept} in one sentence."
    - Pipe through the provided model
    - Parse the output to a plain string using StrOutputParser

    Args:
        model: A chat model (or MockChatModel for testing).

    Returns:
        An LCEL chain (RunnableSequence) that accepts {"concept": str}
        and returns a string.

    >>> mock = MockChatModel(responses=["Variables store data."])
    >>> chain = build_simple_chain(mock)
    >>> # chain.invoke({"concept": "variables"}) would return "Variables store data."
    """
    pass


# =============================================================================
# EXERCISE 4: PydanticOutputParser
# Difficulty: Medium
# =============================================================================

def create_book_parser() -> tuple[Any, str]:
    """Create a PydanticOutputParser for book information.

    Define a Pydantic model called BookInfo with:
    - title: str (description: "The book title")
    - author: str (description: "The author's name")
    - year: int (description: "Publication year")
    - genres: list[str] (description: "List of genres")

    Returns:
        A tuple of (parser, format_instructions_string).

    >>> parser, instructions = create_book_parser()
    >>> "title" in instructions
    True
    >>> from langchain_core.messages import AIMessage
    >>> result = parser.invoke(AIMessage(content='{"title": "Dune", "author": "Frank Herbert", "year": 1965, "genres": ["sci-fi"]}'))
    >>> result.title
    'Dune'
    >>> result.year
    1965
    """
    pass


# =============================================================================
# EXERCISE 5: RunnablePassthrough.assign
# Difficulty: Medium
# =============================================================================

def build_enrichment_chain() -> Any:
    """Build a chain that enriches input data using RunnablePassthrough.assign.

    The chain should take a dict with key "text" and add:
    - "word_count": number of words in the text
    - "char_count": number of characters in the text
    - "upper": the text in uppercase

    Returns:
        A Runnable that accepts {"text": str} and returns a dict with all four keys.

    >>> chain = build_enrichment_chain()
    >>> result = chain.invoke({"text": "hello world"})
    >>> result["text"]
    'hello world'
    >>> result["word_count"]
    2
    >>> result["char_count"]
    11
    >>> result["upper"]
    'HELLO WORLD'
    """
    pass


# =============================================================================
# EXERCISE 6: RunnableParallel
# Difficulty: Medium
# =============================================================================

def build_parallel_analysis() -> Any:
    """Build a RunnableParallel that performs multiple analyses simultaneously.

    The chain should accept a dict with key "text" and produce:
    - "word_count": number of words
    - "sentence_count": number of sentences (split on '. ', '! ', '? ', or end of string
      with '.', '!', '?')
    - "avg_word_length": average word length (float, rounded to 2 decimals)

    Use RunnableLambda for each computation.

    Returns:
        A RunnableParallel instance.

    >>> chain = build_parallel_analysis()
    >>> result = chain.invoke({"text": "Hello world. How are you?"})
    >>> result["word_count"]
    5
    >>> result["sentence_count"]
    2
    >>> isinstance(result["avg_word_length"], float)
    True
    """
    pass


# =============================================================================
# EXERCISE 7: RunnableBranch (Conditional Routing)
# Difficulty: Medium
# =============================================================================

def build_language_router() -> Any:
    """Build a RunnableBranch that routes based on detected programming language.

    The chain should accept a dict with key "code" and:
    - If the code contains "def " or "import ", return "Detected: Python"
    - If the code contains "func " or "let " or "var ", return "Detected: Swift"
    - If the code contains "function " or "const ", return "Detected: JavaScript"
    - Otherwise, return "Detected: Unknown"

    Use RunnableBranch with RunnableLambda for each branch.

    Returns:
        A RunnableBranch instance.

    >>> router = build_language_router()
    >>> router.invoke({"code": "def hello(): pass"})
    'Detected: Python'
    >>> router.invoke({"code": "let x = 5"})
    'Detected: Swift'
    >>> router.invoke({"code": "const y = 10"})
    'Detected: JavaScript'
    >>> router.invoke({"code": "PRINT HELLO"})
    'Detected: Unknown'
    """
    pass


# =============================================================================
# EXERCISE 8: Sequential Chain with Data Flow
# Difficulty: Hard
# =============================================================================

def build_data_pipeline() -> Any:
    """Build a multi-step data transformation pipeline using LCEL.

    The pipeline should:
    1. Accept a dict with "raw_data" (a comma-separated string of numbers)
    2. Step 1: Parse the string into a list of floats -> store as "numbers"
    3. Step 2: Calculate statistics -> add "mean", "min_val", "max_val"
    4. Step 3: Generate a summary string -> add "summary"

    The summary should be: "Stats: mean={mean:.1f}, min={min_val}, max={max_val}, count={count}"

    Returns:
        A Runnable chain.

    >>> pipeline = build_data_pipeline()
    >>> result = pipeline.invoke({"raw_data": "1,2,3,4,5"})
    >>> result["numbers"]
    [1.0, 2.0, 3.0, 4.0, 5.0]
    >>> result["mean"]
    3.0
    >>> result["min_val"]
    1.0
    >>> result["max_val"]
    5.0
    >>> "mean=3.0" in result["summary"]
    True
    """
    pass


# =============================================================================
# EXERCISE 9: Conversation Memory Setup
# Difficulty: Easy
# =============================================================================

def simulate_conversation() -> list[str]:
    """Simulate a 3-turn conversation using ChatMessageHistory.

    Steps:
    1. Create a ChatMessageHistory instance.
    2. Add these messages in order:
       - HumanMessage: "My name is Daniel"
       - AIMessage: "Hello Daniel!"
       - HumanMessage: "I love Swift"
       - AIMessage: "Swift is a great language!"
       - HumanMessage: "What's my name?"
       - AIMessage: "Your name is Daniel!"
    3. Return a list of all message contents (strings).

    Returns:
        List of 6 message content strings.

    >>> messages = simulate_conversation()
    >>> len(messages)
    6
    >>> messages[0]
    'My name is Daniel'
    >>> messages[5]
    'Your name is Daniel!'
    """
    pass


# =============================================================================
# EXERCISE 10: Document Splitting
# Difficulty: Easy
# =============================================================================

def split_document(text: str, chunk_size: int = 100, chunk_overlap: int = 20) -> list[str]:
    """Split a text into chunks using RecursiveCharacterTextSplitter.

    Args:
        text: The text to split.
        chunk_size: Maximum size of each chunk.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.

    >>> chunks = split_document("word " * 100, chunk_size=50, chunk_overlap=10)
    >>> all(len(c) <= 50 for c in chunks)
    True
    >>> len(chunks) > 1
    True
    """
    pass


# =============================================================================
# EXERCISE 11: Build a Prompt with Memory Placeholder
# Difficulty: Medium
# =============================================================================

def create_memory_prompt() -> Any:
    """Create a prompt template that includes a MessagesPlaceholder for history.

    The template should have:
    - System message: "You are a coding tutor for {language} developers."
    - MessagesPlaceholder with variable_name="chat_history"
    - Human message: "{question}"

    Returns:
        A ChatPromptTemplate.

    >>> prompt = create_memory_prompt()
    >>> from langchain_core.messages import HumanMessage, AIMessage
    >>> result = prompt.invoke({
    ...     "language": "Swift",
    ...     "chat_history": [
    ...         HumanMessage(content="What is a closure?"),
    ...         AIMessage(content="A closure captures variables from its scope.")
    ...     ],
    ...     "question": "Give me an example"
    ... })
    >>> len(result.messages) == 5  # system + 2 history + human
    True
    """
    pass


# =============================================================================
# EXERCISE 12: Complete Chain Assembly
# Difficulty: Hard
# =============================================================================

def build_code_review_chain(model: Any) -> Any:
    """Build a complete code review chain using LCEL.

    The chain should:
    1. Accept {"code": str, "language": str}
    2. Step 1 (parallel):
       - "style_review": Use prompt "Review the code style of this {language} code: {code}"
       - "bug_check": Use prompt "Check for bugs in this {language} code: {code}"
    3. Step 2: Combine results into a summary using prompt:
       "Summarize this code review:\nStyle: {style_review}\nBugs: {bug_check}"

    All prompts go through model | StrOutputParser().

    Args:
        model: A chat model (or MockChatModel for testing).

    Returns:
        A Runnable chain that accepts {"code": str, "language": str}
        and returns a dict with "style_review", "bug_check", and "summary" keys.

    >>> mock = MockChatModel(responses=["Good style", "No bugs found", "All clear"])
    >>> chain = build_code_review_chain(mock)
    >>> # result = chain.invoke({"code": "print('hello')", "language": "Python"})
    >>> # result should have keys: style_review, bug_check, summary
    """
    pass


# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Module 09: LangChain Fundamentals - Exercise Tests")
    print("=" * 70)

    passed = 0
    failed = 0
    errors = []

    # Test Exercise 1
    try:
        prompt = create_translation_prompt()
        result = prompt.invoke({"language": "Spanish", "text": "Hello"})
        assert len(result.messages) == 2, f"Expected 2 messages, got {len(result.messages)}"
        assert "Spanish" in result.messages[0].content
        assert result.messages[1].content == "Hello"
        print("  Exercise 1 (Translation Prompt): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 1 (Translation Prompt): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 1", str(e)))

    # Test Exercise 2
    try:
        prompt = create_sentiment_prompt()
        result = prompt.invoke({"input": "Great weather today!"})
        assert len(result.messages) >= 8, f"Expected >= 8 messages, got {len(result.messages)}"
        print("  Exercise 2 (Sentiment Prompt): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 2 (Sentiment Prompt): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 2", str(e)))

    # Test Exercise 3
    try:
        mock = MockChatModel(responses=["Variables store data."])
        chain = build_simple_chain(mock)
        assert chain is not None, "Chain should not be None"
        print("  Exercise 3 (Simple Chain): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 3 (Simple Chain): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 3", str(e)))

    # Test Exercise 4
    try:
        parser, instructions = create_book_parser()
        assert "title" in instructions
        assert "author" in instructions
        from langchain_core.messages import AIMessage
        result = parser.invoke(AIMessage(content='{"title": "Dune", "author": "Frank Herbert", "year": 1965, "genres": ["sci-fi"]}'))
        assert result.title == "Dune"
        assert result.year == 1965
        assert result.genres == ["sci-fi"]
        print("  Exercise 4 (Book Parser): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 4 (Book Parser): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 4", str(e)))

    # Test Exercise 5
    try:
        chain = build_enrichment_chain()
        result = chain.invoke({"text": "hello world"})
        assert result["text"] == "hello world"
        assert result["word_count"] == 2
        assert result["char_count"] == 11
        assert result["upper"] == "HELLO WORLD"
        print("  Exercise 5 (Enrichment Chain): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 5 (Enrichment Chain): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 5", str(e)))

    # Test Exercise 6
    try:
        chain = build_parallel_analysis()
        result = chain.invoke({"text": "Hello world. How are you?"})
        assert result["word_count"] == 5
        assert result["sentence_count"] == 2
        assert isinstance(result["avg_word_length"], float)
        print("  Exercise 6 (Parallel Analysis): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 6 (Parallel Analysis): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 6", str(e)))

    # Test Exercise 7
    try:
        router = build_language_router()
        assert router.invoke({"code": "def hello(): pass"}) == "Detected: Python"
        assert router.invoke({"code": "let x = 5"}) == "Detected: Swift"
        assert router.invoke({"code": "const y = 10"}) == "Detected: JavaScript"
        assert router.invoke({"code": "PRINT HELLO"}) == "Detected: Unknown"
        print("  Exercise 7 (Language Router): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 7 (Language Router): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 7", str(e)))

    # Test Exercise 8
    try:
        pipeline = build_data_pipeline()
        result = pipeline.invoke({"raw_data": "1,2,3,4,5"})
        assert result["numbers"] == [1.0, 2.0, 3.0, 4.0, 5.0]
        assert result["mean"] == 3.0
        assert result["min_val"] == 1.0
        assert result["max_val"] == 5.0
        assert "mean=3.0" in result["summary"]
        print("  Exercise 8 (Data Pipeline): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 8 (Data Pipeline): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 8", str(e)))

    # Test Exercise 9
    try:
        messages = simulate_conversation()
        assert len(messages) == 6
        assert messages[0] == "My name is Daniel"
        assert messages[5] == "Your name is Daniel!"
        print("  Exercise 9 (Conversation Memory): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 9 (Conversation Memory): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 9", str(e)))

    # Test Exercise 10
    try:
        chunks = split_document("word " * 100, chunk_size=50, chunk_overlap=10)
        assert all(len(c) <= 50 for c in chunks), "Some chunks exceed max size"
        assert len(chunks) > 1, "Should produce multiple chunks"
        print("  Exercise 10 (Document Splitting): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 10 (Document Splitting): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 10", str(e)))

    # Test Exercise 11
    try:
        prompt = create_memory_prompt()
        from langchain_core.messages import HumanMessage, AIMessage
        result = prompt.invoke({
            "language": "Swift",
            "chat_history": [
                HumanMessage(content="What is a closure?"),
                AIMessage(content="A closure captures variables from its scope.")
            ],
            "question": "Give me an example"
        })
        assert len(result.messages) == 5, f"Expected 5 messages, got {len(result.messages)}"
        print("  Exercise 11 (Memory Prompt): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 11 (Memory Prompt): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 11", str(e)))

    # Test Exercise 12
    try:
        mock = MockChatModel(responses=["Good style", "No bugs found", "All clear"])
        chain = build_code_review_chain(mock)
        assert chain is not None, "Chain should not be None"
        print("  Exercise 12 (Code Review Chain): PASSED")
        passed += 1
    except Exception as e:
        print(f"  Exercise 12 (Code Review Chain): FAILED - {e}")
        failed += 1
        errors.append(("Exercise 12", str(e)))

    # Summary
    print()
    print(f"Results: {passed}/{passed + failed} exercises passed")
    if errors:
        print("\nFailed exercises:")
        for name, error in errors:
            print(f"  {name}: {error}")
