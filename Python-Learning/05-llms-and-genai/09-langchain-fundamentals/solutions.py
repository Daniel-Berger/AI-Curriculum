"""
Module 09: LangChain Fundamentals - Solutions
==============================================
Complete solutions for all exercises with explanations.

Run this file to verify all solutions pass: `python solutions.py`
"""

from typing import Any


# =============================================================================
# SETUP: Mock classes (same as exercises.py)
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
    """Create a ChatPromptTemplate for translating text."""
    from langchain_core.prompts import ChatPromptTemplate

    # ChatPromptTemplate.from_messages takes a list of (role, template) tuples.
    # Variables are denoted with {curly_braces} -- similar to Swift's \() interpolation
    # but the values are supplied later via .invoke().
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a translator. Translate text to {language}."),
        ("human", "{text}")
    ])
    return prompt

    # Swift analogy: This is like creating a parameterized LocalizedStringKey
    # where you define the structure first and fill in values at call time.


# =============================================================================
# EXERCISE 2: Build a Few-Shot Prompt
# Difficulty: Medium
# =============================================================================

def create_sentiment_prompt() -> Any:
    """Create a few-shot ChatPromptTemplate for sentiment analysis."""
    from langchain_core.prompts import (
        ChatPromptTemplate,
        FewShotChatMessagePromptTemplate,
    )

    # Define the examples
    examples = [
        {"input": "I love this product!", "output": "positive"},
        {"input": "This is terrible.", "output": "negative"},
        {"input": "The meeting is at 3pm.", "output": "neutral"},
    ]

    # Template for each example pair
    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("ai", "{output}"),
    ])

    # Wrap in FewShotChatMessagePromptTemplate
    few_shot = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    # Final template: system + examples + user input
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Classify the sentiment as positive, negative, or neutral."),
        few_shot,
        ("human", "{input}"),
    ])

    return prompt

    # Note: Few-shot prompting is one of the most effective techniques for
    # guiding LLM behavior. The examples act as implicit instructions.


# =============================================================================
# EXERCISE 3: Use StrOutputParser in a Chain
# Difficulty: Easy
# =============================================================================

def build_simple_chain(model: Any) -> Any:
    """Build a simple LCEL chain: prompt | model | parser."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    prompt = ChatPromptTemplate.from_template("Explain {concept} in one sentence.")
    parser = StrOutputParser()

    # The pipe operator creates a RunnableSequence.
    # Data flows: dict -> prompt -> messages -> model -> AIMessage -> parser -> str
    chain = prompt | model | parser

    return chain

    # Swift analogy: This is like Combine's publisher chain:
    # publisher.map { }.flatMap { }.sink { }
    # Each | is a transformation step.


# =============================================================================
# EXERCISE 4: PydanticOutputParser
# Difficulty: Medium
# =============================================================================

def create_book_parser() -> tuple[Any, str]:
    """Create a PydanticOutputParser for book information."""
    from langchain_core.output_parsers import PydanticOutputParser
    from pydantic import BaseModel, Field

    class BookInfo(BaseModel):
        title: str = Field(description="The book title")
        author: str = Field(description="The author's name")
        year: int = Field(description="Publication year")
        genres: list[str] = Field(description="List of genres")

    parser = PydanticOutputParser(pydantic_object=BookInfo)
    format_instructions = parser.get_format_instructions()

    return parser, format_instructions

    # This is directly analogous to Swift's Codable:
    # struct BookInfo: Codable {
    #     let title: String
    #     let author: String
    #     let year: Int
    #     let genres: [String]
    # }
    # let book = try JSONDecoder().decode(BookInfo.self, from: data)


# =============================================================================
# EXERCISE 5: RunnablePassthrough.assign
# Difficulty: Medium
# =============================================================================

def build_enrichment_chain() -> Any:
    """Build a chain that enriches input data using RunnablePassthrough.assign."""
    from langchain_core.runnables import RunnablePassthrough

    # RunnablePassthrough.assign adds new keys while preserving existing ones.
    # Each lambda receives the full input dict.
    chain = RunnablePassthrough.assign(
        word_count=lambda x: len(x["text"].split()),
        char_count=lambda x: len(x["text"]),
        upper=lambda x: x["text"].upper(),
    )

    return chain

    # Note: assign() is incredibly useful for building up context step-by-step.
    # Each step can add computed fields that later steps can use.


# =============================================================================
# EXERCISE 6: RunnableParallel
# Difficulty: Medium
# =============================================================================

def build_parallel_analysis() -> Any:
    """Build a RunnableParallel that performs multiple analyses simultaneously."""
    from langchain_core.runnables import RunnableParallel, RunnableLambda
    import re

    def count_words(data: dict) -> int:
        return len(data["text"].split())

    def count_sentences(data: dict) -> int:
        text = data["text"].strip()
        if not text:
            return 0
        # Split on sentence-ending punctuation followed by space or end of string
        sentences = re.split(r'[.!?]+\s*', text)
        # Filter out empty strings from the split
        sentences = [s for s in sentences if s.strip()]
        return len(sentences)

    def avg_word_length(data: dict) -> float:
        words = data["text"].split()
        if not words:
            return 0.0
        avg = sum(len(w.strip(".,!?;:")) for w in words) / len(words)
        return round(avg, 2)

    # RunnableParallel runs all branches concurrently and merges results.
    # Similar to Swift's async let or TaskGroup.
    chain = RunnableParallel(
        word_count=RunnableLambda(count_words),
        sentence_count=RunnableLambda(count_sentences),
        avg_word_length=RunnableLambda(avg_word_length),
    )

    return chain


# =============================================================================
# EXERCISE 7: RunnableBranch (Conditional Routing)
# Difficulty: Medium
# =============================================================================

def build_language_router() -> Any:
    """Build a RunnableBranch that routes based on detected programming language."""
    from langchain_core.runnables import RunnableBranch, RunnableLambda

    def is_python(data: dict) -> bool:
        code = data["code"]
        return "def " in code or "import " in code

    def is_swift(data: dict) -> bool:
        code = data["code"]
        return "func " in code or "let " in code or "var " in code

    def is_javascript(data: dict) -> bool:
        code = data["code"]
        return "function " in code or "const " in code

    # RunnableBranch checks conditions in order, returns the first match.
    # The last argument (no condition) is the default fallback.
    # Similar to a Swift switch statement with a default case.
    branch = RunnableBranch(
        (is_python, RunnableLambda(lambda x: "Detected: Python")),
        (is_swift, RunnableLambda(lambda x: "Detected: Swift")),
        (is_javascript, RunnableLambda(lambda x: "Detected: JavaScript")),
        RunnableLambda(lambda x: "Detected: Unknown"),  # default
    )

    return branch


# =============================================================================
# EXERCISE 8: Sequential Chain with Data Flow
# Difficulty: Hard
# =============================================================================

def build_data_pipeline() -> Any:
    """Build a multi-step data transformation pipeline using LCEL."""
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda

    def parse_numbers(data: dict) -> dict:
        """Step 1: Parse comma-separated string into list of floats."""
        numbers = [float(x.strip()) for x in data["raw_data"].split(",")]
        return {**data, "numbers": numbers}

    def calculate_stats(data: dict) -> dict:
        """Step 2: Calculate statistics."""
        numbers = data["numbers"]
        return {
            **data,
            "mean": sum(numbers) / len(numbers),
            "min_val": min(numbers),
            "max_val": max(numbers),
        }

    def generate_summary(data: dict) -> dict:
        """Step 3: Generate summary string."""
        summary = (
            f"Stats: mean={data['mean']:.1f}, "
            f"min={data['min_val']}, "
            f"max={data['max_val']}, "
            f"count={len(data['numbers'])}"
        )
        return {**data, "summary": summary}

    # Chain the steps sequentially. Each step receives the output of the previous.
    pipeline = (
        RunnableLambda(parse_numbers)
        | RunnableLambda(calculate_stats)
        | RunnableLambda(generate_summary)
    )

    return pipeline

    # Alternative approach using RunnablePassthrough.assign:
    # pipeline = (
    #     RunnablePassthrough.assign(
    #         numbers=lambda x: [float(n.strip()) for n in x["raw_data"].split(",")]
    #     )
    #     | RunnablePassthrough.assign(
    #         mean=lambda x: sum(x["numbers"]) / len(x["numbers"]),
    #         min_val=lambda x: min(x["numbers"]),
    #         max_val=lambda x: max(x["numbers"]),
    #     )
    #     | RunnablePassthrough.assign(
    #         summary=lambda x: f"Stats: mean={x['mean']:.1f}, ..."
    #     )
    # )


# =============================================================================
# EXERCISE 9: Conversation Memory Setup
# Difficulty: Easy
# =============================================================================

def simulate_conversation() -> list[str]:
    """Simulate a 3-turn conversation using ChatMessageHistory."""
    from langchain_community.chat_message_histories import ChatMessageHistory
    from langchain_core.messages import HumanMessage, AIMessage

    history = ChatMessageHistory()

    # Add messages in order -- each turn has a human message and AI response
    history.add_message(HumanMessage(content="My name is Daniel"))
    history.add_message(AIMessage(content="Hello Daniel!"))
    history.add_message(HumanMessage(content="I love Swift"))
    history.add_message(AIMessage(content="Swift is a great language!"))
    history.add_message(HumanMessage(content="What's my name?"))
    history.add_message(AIMessage(content="Your name is Daniel!"))

    # Extract just the content strings
    return [msg.content for msg in history.messages]

    # Note: ChatMessageHistory is the simplest memory backend.
    # For production, you'd use Redis, PostgreSQL, or another persistent store.


# =============================================================================
# EXERCISE 10: Document Splitting
# Difficulty: Easy
# =============================================================================

def split_document(text: str, chunk_size: int = 100, chunk_overlap: int = 20) -> list[str]:
    """Split a text into chunks using RecursiveCharacterTextSplitter."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        # Default separators: ["\n\n", "\n", " ", ""]
        # It tries each in order, splitting on the first that produces
        # chunks within the size limit.
    )

    chunks = splitter.split_text(text)
    return chunks

    # RecursiveCharacterTextSplitter is almost always the right choice.
    # It preserves semantic boundaries (paragraphs > lines > words).


# =============================================================================
# EXERCISE 11: Build a Prompt with Memory Placeholder
# Difficulty: Medium
# =============================================================================

def create_memory_prompt() -> Any:
    """Create a prompt template that includes a MessagesPlaceholder for history."""
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a coding tutor for {language} developers."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])

    return prompt

    # MessagesPlaceholder is the key to memory in LCEL chains.
    # It accepts a list of Message objects and inserts them into the prompt.
    # This is how conversation history gets injected between the system
    # message and the current user message.


# =============================================================================
# EXERCISE 12: Complete Chain Assembly
# Difficulty: Hard
# =============================================================================

def build_code_review_chain(model: Any) -> Any:
    """Build a complete code review chain using LCEL."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableParallel, RunnablePassthrough

    parser = StrOutputParser()

    # Step 1: Define prompts
    style_prompt = ChatPromptTemplate.from_template(
        "Review the code style of this {language} code: {code}"
    )
    bug_prompt = ChatPromptTemplate.from_template(
        "Check for bugs in this {language} code: {code}"
    )
    summary_prompt = ChatPromptTemplate.from_template(
        "Summarize this code review:\nStyle: {style_review}\nBugs: {bug_check}"
    )

    # Step 2: Run style review and bug check in parallel
    # RunnableParallel passes the same input to both branches
    parallel_step = RunnableParallel(
        style_review=style_prompt | model | parser,
        bug_check=bug_prompt | model | parser,
    )

    # Step 3: Chain parallel results into summary
    # The parallel step outputs {"style_review": ..., "bug_check": ...}
    # which feeds directly into the summary prompt
    chain = parallel_step | RunnablePassthrough.assign(
        summary=summary_prompt | model | parser,
    )

    return chain

    # Architecture note: This is a fan-out-then-merge pattern.
    # The parallel step fans out the input to multiple chains,
    # then the results are merged and fed into a summary chain.
    # This pattern is extremely common in LLM applications.


# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Module 09: LangChain Fundamentals - Solution Tests")
    print("=" * 70)

    passed = 0
    failed = 0
    errors = []

    # Test Exercise 1
    try:
        prompt = create_translation_prompt()
        result = prompt.invoke({"language": "Spanish", "text": "Hello"})
        assert len(result.messages) == 2
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
        assert len(result.messages) >= 8
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
        assert chain is not None
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
        assert all(len(c) <= 50 for c in chunks)
        assert len(chunks) > 1
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
        assert len(result.messages) == 5
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
        assert chain is not None
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
