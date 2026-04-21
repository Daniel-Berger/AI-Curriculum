# Module 09: LangChain Fundamentals

## Introduction for Swift Developers

If you have built iOS apps, you know the value of frameworks like UIKit or SwiftUI -- they
provide structure, reusable components, and conventions that make complex apps manageable.
LangChain serves the same role for LLM-powered applications. Instead of manually gluing
together API calls, prompt formatting, and output parsing, LangChain gives you composable
building blocks that snap together.

Think of LangChain as the "UIKit of LLM apps" -- it defines patterns (chains, retrievers,
memory) that let you build sophisticated AI applications without reinventing the plumbing
every time.

This module covers LangChain's core abstractions, the expressive LCEL pipe syntax, memory
management, and how to build multi-step chains that solve real problems.

---

## 1. What is LangChain?

### The Orchestration Problem

When building LLM applications, you quickly encounter recurring patterns:

1. Format a prompt with dynamic variables
2. Send it to an LLM
3. Parse the structured output
4. Maybe feed it into another LLM call
5. Handle conversation history
6. Retrieve relevant documents

Without a framework, you end up writing boilerplate for each of these steps. LangChain
provides standardized interfaces for all of them.

### Core Architecture

```
┌─────────────────────────────────────────────────┐
│                   LangChain                      │
├──────────┬──────────┬──────────┬────────────────┤
│ Prompts  │  Models  │ Output   │  Chains        │
│          │          │ Parsers  │                 │
├──────────┼──────────┼──────────┼────────────────┤
│ Memory   │Retrievers│ Document │  Callbacks     │
│          │          │ Loaders  │                 │
└──────────┴──────────┴──────────┴────────────────┘
```

### Installation

```bash
pip install langchain langchain-anthropic langchain-openai langchain-community
pip install langchain-chroma  # For vector store examples
```

### Swift Analogy

| LangChain Concept    | Swift Equivalent                              |
|----------------------|-----------------------------------------------|
| Chain                | Pipeline of operations (like Combine chain)   |
| PromptTemplate       | String interpolation with structure            |
| OutputParser         | JSONDecoder / Codable                         |
| Memory               | @State / UserDefaults for conversation        |
| Retriever            | Core Data fetch request                       |
| LCEL pipe `\|`       | Combine's `.map { }.flatMap { }` chaining     |

---

## 2. Prompt Templates

### ChatPromptTemplate

Prompt templates are parameterized message sequences. They separate the prompt structure
from the dynamic values, just as SwiftUI separates layout from data.

```python
from langchain_core.prompts import ChatPromptTemplate

# Simple template with variables
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant specializing in {domain}."),
    ("human", "{question}")
])

# Invoke produces a ChatPromptValue with formatted messages
result = prompt.invoke({
    "domain": "iOS development",
    "question": "How do I use async/await in Swift?"
})

print(result.messages)
# [SystemMessage(content='You are a helpful assistant specializing in iOS development.'),
#  HumanMessage(content='How do I use async/await in Swift?')]
```

### From Template Strings

```python
from langchain_core.prompts import ChatPromptTemplate

# Shorthand for a single human message
prompt = ChatPromptTemplate.from_template(
    "Translate the following to {language}: {text}"
)

# Check what variables are expected
print(prompt.input_variables)  # ['language', 'text']
```

### Message Types

```python
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Full control over message types
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a code reviewer."),
    MessagesPlaceholder(variable_name="history"),  # For conversation history
    ("human", "{input}")
])

# Invoke with history
result = prompt.invoke({
    "history": [
        HumanMessage(content="Review my Python code"),
        AIMessage(content="Sure, paste it here.")
    ],
    "input": "def add(a, b): return a + b"
})
```

### Few-Shot Prompt Templates

```python
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

# Define examples
examples = [
    {"input": "happy", "output": "sad"},
    {"input": "tall", "output": "short"},
    {"input": "sunny", "output": "cloudy"},
]

# Example template
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

# Few-shot template
few_shot = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

# Final prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You give the opposite of the word."),
    few_shot,
    ("human", "{input}"),
])

result = prompt.invoke({"input": "big"})
```

---

## 3. Model Wrappers

### ChatAnthropic (Claude)

LangChain wraps LLM APIs in a standard interface so you can swap providers without
changing your chain logic.

```python
from langchain_anthropic import ChatAnthropic

# Initialize the model
model = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    temperature=0.7,
    max_tokens=1024,
    # api_key="..."  # Or set ANTHROPIC_API_KEY env var
)

# Direct invocation
from langchain_core.messages import HumanMessage
response = model.invoke([HumanMessage(content="Explain Swift optionals")])
print(response.content)
```

### ChatOpenAI

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=1024,
    # api_key="..."  # Or set OPENAI_API_KEY env var
)

response = model.invoke([HumanMessage(content="Explain Swift optionals")])
print(response.content)
```

### Streaming

```python
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4-20250514")

# Stream tokens as they arrive
for chunk in model.stream([HumanMessage(content="Write a haiku about Python")]):
    print(chunk.content, end="", flush=True)
```

### Batch Processing

```python
# Process multiple inputs at once
messages_batch = [
    [HumanMessage(content="Capital of France?")],
    [HumanMessage(content="Capital of Japan?")],
    [HumanMessage(content="Capital of Brazil?")],
]

responses = model.batch(messages_batch)
for r in responses:
    print(r.content)
```

---

## 4. Output Parsers

### StrOutputParser

The simplest parser -- extracts the string content from an AI message.

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()

# Typically used at the end of a chain
from langchain_core.messages import AIMessage
result = parser.invoke(AIMessage(content="Hello, world!"))
print(result)  # "Hello, world!"
print(type(result))  # <class 'str'>
```

### JsonOutputParser

Parses JSON from model output into a Python dict.

```python
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()

# The parser extracts JSON from the model's response
# It handles markdown code blocks (```json ... ```) automatically
from langchain_core.messages import AIMessage
result = parser.invoke(
    AIMessage(content='```json\n{"name": "Swift", "year": 2014}\n```')
)
print(result)  # {'name': 'Swift', 'year': 2014}
```

### PydanticOutputParser

The most powerful parser -- validates output against a Pydantic model, just like
using Codable in Swift to decode JSON.

```python
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class MovieReview(BaseModel):
    title: str = Field(description="The movie title")
    rating: float = Field(description="Rating from 1.0 to 5.0")
    summary: str = Field(description="Brief review summary")
    recommend: bool = Field(description="Whether you recommend it")

parser = PydanticOutputParser(pydantic_object=MovieReview)

# Get format instructions to include in prompt
print(parser.get_format_instructions())
# Prints a detailed JSON schema the LLM should follow

# Parse a response
from langchain_core.messages import AIMessage
result = parser.invoke(AIMessage(content='''{
    "title": "Inception",
    "rating": 4.5,
    "summary": "Mind-bending masterpiece",
    "recommend": true
}'''))
print(result)         # MovieReview object
print(result.title)   # "Inception"
print(result.rating)  # 4.5
```

### Combining Parser with Prompt

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class CodeReview(BaseModel):
    language: str = Field(description="Programming language")
    issues: list[str] = Field(description="List of issues found")
    score: int = Field(description="Code quality score 1-10")

parser = PydanticOutputParser(pydantic_object=CodeReview)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a code reviewer. {format_instructions}"),
    ("human", "Review this code:\n{code}")
])

# Partial the prompt with format instructions
prompt = prompt.partial(format_instructions=parser.get_format_instructions())
```

---

## 5. LCEL (LangChain Expression Language)

### The Pipe Operator

LCEL is LangChain's declarative way to compose chains. If you have used Combine in Swift,
the pipe operator `|` will feel familiar -- it chains operations where the output of one
step becomes the input of the next.

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
model = ChatAnthropic(model="claude-sonnet-4-20250514")
parser = StrOutputParser()

# LCEL chain: prompt | model | parser
chain = prompt | model | parser

# Invoke the chain
result = chain.invoke({"topic": "programming"})
print(result)  # A joke about programming (as a plain string)
```

**How it works:**
1. `prompt.invoke({"topic": "programming"})` produces formatted messages
2. Those messages flow into `model.invoke(messages)` which returns an AIMessage
3. The AIMessage flows into `parser.invoke(ai_message)` which extracts the string

This is analogous to Combine:
```swift
// Swift Combine analogy
URLSession.shared.dataTaskPublisher(for: url)
    .map(\.data)
    .decode(type: Response.self, decoder: JSONDecoder())
    .sink { ... }
```

### RunnablePassthrough

Passes input through unchanged -- useful for forwarding values in parallel chains.

```python
from langchain_core.runnables import RunnablePassthrough

# RunnablePassthrough just forwards its input
chain = RunnablePassthrough() | (lambda x: x.upper())
result = chain.invoke("hello")
print(result)  # "HELLO"

# With assign -- adds new keys to the dict while keeping existing ones
from langchain_core.runnables import RunnablePassthrough

chain = RunnablePassthrough.assign(
    upper=lambda x: x["text"].upper(),
    length=lambda x: len(x["text"])
)

result = chain.invoke({"text": "hello"})
print(result)  # {"text": "hello", "upper": "HELLO", "length": 5}
```

### RunnableParallel

Runs multiple chains in parallel and combines their outputs -- like a
`DispatchGroup` or `TaskGroup` in Swift.

```python
from langchain_core.runnables import RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4-20250514")
parser = StrOutputParser()

# Two prompts that process the same input differently
joke_chain = (
    ChatPromptTemplate.from_template("Tell a joke about {topic}")
    | model
    | parser
)

poem_chain = (
    ChatPromptTemplate.from_template("Write a haiku about {topic}")
    | model
    | parser
)

# Run both in parallel
parallel_chain = RunnableParallel(joke=joke_chain, poem=poem_chain)

result = parallel_chain.invoke({"topic": "Python"})
print(result["joke"])  # A joke about Python
print(result["poem"])  # A haiku about Python
```

### RunnableLambda

Wraps any Python function as a runnable -- the escape hatch for custom logic.

```python
from langchain_core.runnables import RunnableLambda

# Wrap a function
def word_count(text: str) -> dict:
    words = text.split()
    return {"text": text, "word_count": len(words)}

counter = RunnableLambda(word_count)
result = counter.invoke("Hello world from LangChain")
print(result)  # {"text": "Hello world from LangChain", "word_count": 4}

# Use in a chain
chain = prompt | model | parser | RunnableLambda(word_count)
```

### RunnableBranch (Conditional Routing)

```python
from langchain_core.runnables import RunnableBranch

# Route based on input
branch = RunnableBranch(
    # (condition, runnable) pairs
    (lambda x: "python" in x["topic"].lower(), python_chain),
    (lambda x: "swift" in x["topic"].lower(), swift_chain),
    # Default fallback (no condition)
    general_chain,
)

result = branch.invoke({"topic": "Python decorators"})
```

---

## 6. Building Chains

### Sequential Chains

The most common pattern -- steps execute one after another.

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

model = ChatAnthropic(model="claude-sonnet-4-20250514")
parser = StrOutputParser()

# Step 1: Generate a story outline
outline_prompt = ChatPromptTemplate.from_template(
    "Create a brief story outline about {topic}. Return just the outline."
)

# Step 2: Expand the outline into a story
story_prompt = ChatPromptTemplate.from_template(
    "Expand this outline into a short story:\n{outline}"
)

# Step 3: Create a title
title_prompt = ChatPromptTemplate.from_template(
    "Give this story a creative title:\n{story}\nReturn just the title."
)

# Chain them together
chain = (
    {"outline": outline_prompt | model | parser}
    | {"story": story_prompt | model | parser, "outline": lambda x: x["outline"]}
    | {"title": title_prompt | model | parser, "story": lambda x: x["story"]}
)

# Or more simply with RunnablePassthrough.assign
chain = (
    RunnablePassthrough.assign(
        outline=outline_prompt | model | parser
    )
    | RunnablePassthrough.assign(
        story=story_prompt | model | parser
    )
    | RunnablePassthrough.assign(
        title=title_prompt | model | parser
    )
)
```

### Multi-Step Analysis Chain

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

model = ChatAnthropic(model="claude-sonnet-4-20250514")

# Analyze code, then suggest improvements, then rate
analyze_prompt = ChatPromptTemplate.from_template(
    "Analyze this code for issues:\n```\n{code}\n```\nList the issues."
)

fix_prompt = ChatPromptTemplate.from_template(
    "Given these issues:\n{analysis}\n\nRewrite the code to fix them:\n```\n{code}\n```"
)

chain = (
    RunnablePassthrough.assign(
        analysis=analyze_prompt | model | StrOutputParser()
    )
    | RunnablePassthrough.assign(
        fixed_code=fix_prompt | model | StrOutputParser()
    )
)

result = chain.invoke({"code": "def add(a,b): return a+b"})
print(result["analysis"])
print(result["fixed_code"])
```

---

## 7. Memory

### Why Memory Matters

LLMs are stateless -- each API call is independent. Memory gives your chatbot the
illusion of a continuous conversation, like maintaining `@State` across SwiftUI view
updates.

### ConversationBufferMemory

Stores the full conversation history. Simple but grows unbounded.

```python
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

memory = ConversationBufferMemory(return_messages=True)

# Save conversation turns
memory.save_context(
    {"input": "My name is Daniel"},
    {"output": "Hello Daniel! Nice to meet you."}
)
memory.save_context(
    {"input": "I'm an iOS developer"},
    {"output": "That's great! Swift is a wonderful language."}
)

# Load conversation history
history = memory.load_memory_variables({})
print(history["history"])
# [HumanMessage(content="My name is Daniel"),
#  AIMessage(content="Hello Daniel! Nice to meet you."),
#  HumanMessage(content="I'm an iOS developer"),
#  AIMessage(content="That's great! Swift is a wonderful language.")]
```

### ConversationWindowMemory

Keeps only the last K conversation turns -- bounded memory.

```python
from langchain.memory import ConversationWindowMemory

memory = ConversationWindowMemory(k=2, return_messages=True)

# After many turns, only the last 2 are kept
memory.save_context({"input": "Message 1"}, {"output": "Response 1"})
memory.save_context({"input": "Message 2"}, {"output": "Response 2"})
memory.save_context({"input": "Message 3"}, {"output": "Response 3"})

history = memory.load_memory_variables({})
# Only contains messages 2 and 3 (last k=2 turns)
```

### ConversationSummaryMemory

Summarizes older conversation turns -- maintains context without unlimited growth.

```python
from langchain.memory import ConversationSummaryMemory
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4-20250514")

memory = ConversationSummaryMemory(
    llm=model,
    return_messages=True
)

# As conversation grows, older messages are summarized
memory.save_context(
    {"input": "I work at Apple on the SwiftUI team"},
    {"output": "That's amazing! SwiftUI has transformed iOS development."}
)
memory.save_context(
    {"input": "We're working on new declarative animations"},
    {"output": "Declarative animations are a great addition to SwiftUI."}
)

# Memory contains a summary instead of raw messages
history = memory.load_memory_variables({})
print(history)
```

### Using Memory in LCEL Chains

The modern approach uses `RunnableWithMessageHistory` from `langchain_core`:

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser

# In-memory store for sessions
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

model = ChatAnthropic(model="claude-sonnet-4-20250514")

chain = prompt | model | StrOutputParser()

# Wrap with message history
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# Each invocation uses a session ID
config = {"configurable": {"session_id": "user_123"}}

response1 = chain_with_history.invoke(
    {"input": "My name is Daniel"},
    config=config
)
print(response1)  # "Hello Daniel! ..."

response2 = chain_with_history.invoke(
    {"input": "What's my name?"},
    config=config
)
print(response2)  # "Your name is Daniel ..."
```

---

## 8. Document Loaders

### Loading Different File Types

Document loaders bring external data into LangChain's `Document` format, similar to
how you might load data from different sources into Core Data.

```python
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    WebBaseLoader,
    CSVLoader,
)

# Load a text file
loader = TextLoader("notes.txt")
docs = loader.load()
print(docs[0].page_content)   # The text content
print(docs[0].metadata)       # {"source": "notes.txt"}

# Load a PDF (one Document per page)
loader = PyPDFLoader("paper.pdf")
pages = loader.load()
print(f"Loaded {len(pages)} pages")
print(pages[0].page_content)  # Text from page 1

# Load from the web
loader = WebBaseLoader("https://docs.python.org/3/tutorial/")
docs = loader.load()

# Load CSV
loader = CSVLoader("data.csv")
rows = loader.load()  # One Document per row
```

### The Document Object

```python
from langchain_core.documents import Document

# Documents are simple: content + metadata
doc = Document(
    page_content="Swift is a general-purpose programming language...",
    metadata={
        "source": "wikipedia",
        "topic": "Swift",
        "year": 2014
    }
)

print(doc.page_content)  # The text
print(doc.metadata)      # The metadata dict
```

---

## 9. Text Splitters

### Why Split Text?

LLMs have context windows. Long documents must be split into chunks that fit. Text
splitters break documents intelligently -- preserving meaning while respecting size limits.

```python
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)

# RecursiveCharacterTextSplitter -- the default and usually best choice
# Tries to split on: \n\n, \n, " ", "" (in that order)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # Max characters per chunk
    chunk_overlap=50,     # Overlap between chunks for context continuity
    length_function=len,  # How to measure length
)

long_text = "..." # Some long document text
chunks = splitter.split_text(long_text)
print(f"Split into {len(chunks)} chunks")

# Split documents (preserves metadata)
from langchain_core.documents import Document
doc = Document(page_content=long_text, metadata={"source": "article.txt"})
split_docs = splitter.split_documents([doc])
# Each chunk Document inherits the parent's metadata
```

### Code-Aware Splitting

```python
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

# Language-aware splitting (knows about Python syntax)
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=500,
    chunk_overlap=50,
)

swift_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.SWIFT,
    chunk_size=500,
    chunk_overlap=50,
)

python_code = """
def hello():
    print("Hello, world!")

class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
"""

chunks = python_splitter.split_text(python_code)
# Splits at class/function boundaries when possible
```

---

## 10. Retrievers

### VectorStoreRetriever

Retrievers fetch relevant documents based on a query. The most common type wraps a
vector store, performing similarity search under the hood.

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Create some documents
docs = [
    Document(page_content="SwiftUI uses declarative syntax for building UIs"),
    Document(page_content="UIKit uses imperative, event-driven programming"),
    Document(page_content="Core Data manages persistent object graphs"),
    Document(page_content="Combine handles asynchronous event streams"),
]

# Create a vector store from documents
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
)

# Create a retriever from the vector store
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2}  # Return top 2 results
)

# Use the retriever
results = retriever.invoke("How do I build a UI in iOS?")
for doc in results:
    print(doc.page_content)
# "SwiftUI uses declarative syntax for building UIs"
# "UIKit uses imperative, event-driven programming"
```

### Using Retrievers in Chains (RAG Pattern)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4-20250514")

# RAG prompt
prompt = ChatPromptTemplate.from_template("""
Answer the question based on the following context:

Context: {context}

Question: {question}

Answer:""")

# Format documents into a single string
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# RAG chain
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | model
    | StrOutputParser()
)

answer = rag_chain.invoke("What framework should I use for UI?")
print(answer)
```

---

## 11. Putting It All Together: A Complete Example

### Multi-Step Code Analysis Agent

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from pydantic import BaseModel, Field

model = ChatAnthropic(model="claude-sonnet-4-20250514")
parser = StrOutputParser()

# Step 1: Analyze code quality
quality_prompt = ChatPromptTemplate.from_template(
    "Rate the code quality (1-10) and explain:\n```{language}\n{code}\n```"
)

# Step 2: Suggest improvements
improve_prompt = ChatPromptTemplate.from_template(
    "Suggest specific improvements for this {language} code:\n```\n{code}\n```"
)

# Step 3: Convert to another language
convert_prompt = ChatPromptTemplate.from_template(
    "Convert this {language} code to {target_language}:\n```\n{code}\n```"
)

# Run quality check and improvements in parallel, then convert
analysis_chain = RunnableParallel(
    quality=quality_prompt | model | parser,
    improvements=improve_prompt | model | parser,
) | RunnablePassthrough.assign(
    converted=(
        lambda x: {"language": "python", "code": x.get("quality", ""), "target_language": "swift"}
    ) | convert_prompt | model | parser
)

# This would be invoked with:
# result = analysis_chain.invoke({
#     "language": "python",
#     "code": "def add(a,b): return a+b",
#     "target_language": "swift"
# })
```

### Chatbot with Memory and Context

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Session store
sessions = {}

def get_history(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = ChatMessageHistory()
    return sessions[session_id]

# Build the chain
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert iOS developer assistant.
You help with Swift, SwiftUI, UIKit, and Apple frameworks.
Be concise and provide code examples when helpful."""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

model = ChatAnthropic(model="claude-sonnet-4-20250514")

chain = prompt | model | StrOutputParser()

chatbot = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",
    history_messages_key="history",
)

# Usage
config = {"configurable": {"session_id": "dev_session_1"}}

# Turn 1
print(chatbot.invoke(
    {"input": "How do I create a list in SwiftUI?"},
    config=config
))

# Turn 2 -- chatbot remembers the context
print(chatbot.invoke(
    {"input": "How do I add swipe-to-delete to it?"},
    config=config
))
```

---

## 12. Debugging and Best Practices

### Tracing with LangSmith

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# All chain invocations are now traced in LangSmith
# You can see each step's input/output, latency, and token usage
```

### Error Handling

```python
from langchain_core.runnables import RunnableLambda

def safe_parse(text: str) -> dict:
    """Parse with fallback."""
    try:
        import json
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse", "raw": text}

# Use in chain
chain = prompt | model | StrOutputParser() | RunnableLambda(safe_parse)
```

### Fallback Chains

```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

# Primary model with fallback
model = ChatAnthropic(model="claude-sonnet-4-20250514").with_fallbacks(
    [ChatOpenAI(model="gpt-4o")]
)

# If Claude fails (rate limit, error), automatically tries OpenAI
```

### Best Practices

1. **Start simple** -- use `prompt | model | parser` before adding complexity
2. **Use LCEL** -- it provides streaming, batching, and tracing for free
3. **Type your outputs** -- PydanticOutputParser catches errors early
4. **Manage memory wisely** -- ConversationWindowMemory for most chatbots
5. **Test each step** -- invoke individual components before chaining
6. **Use fallbacks** -- production apps should handle provider failures
7. **Enable tracing** -- LangSmith makes debugging chains dramatically easier

---

## 13. Key Takeaways

| Concept           | What It Does                                      |
|--------------------|-------------------------------------------------|
| ChatPromptTemplate | Parameterized message templates                  |
| ChatAnthropic/OpenAI | Standard interface to LLM providers           |
| StrOutputParser    | Extracts string from AI response                 |
| PydanticOutputParser | Validates and structures output                |
| LCEL `\|` operator | Composes components into chains                  |
| RunnablePassthrough | Forwards input, optionally adding fields       |
| RunnableParallel   | Runs multiple chains concurrently                |
| RunnableLambda     | Wraps custom Python functions as runnables       |
| Memory             | Maintains conversation state across turns        |
| Document Loaders   | Bring external data into LangChain               |
| Text Splitters     | Break documents into LLM-friendly chunks         |
| Retrievers         | Fetch relevant documents by query                |

---

## Next Module

In Module 10, we will explore **LangGraph and Agents** -- building stateful, multi-step
agent workflows with cycles, conditional routing, and human-in-the-loop capabilities
that go beyond what simple chains can handle.
