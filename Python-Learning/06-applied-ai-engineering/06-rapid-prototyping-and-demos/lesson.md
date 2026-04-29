# Module 06: Rapid Prototyping & Demos

## Introduction for Swift Developers

If you have ever presented an iOS app through TestFlight, demoed a prototype in Xcode
Previews, or run a live SwiftUI walkthrough for stakeholders, you already understand the
power of showing rather than telling. In AI engineering -- especially in solutions engineer
and applied AI engineer roles -- the demo is your most powerful sales tool, your proof of
technical feasibility, and often the deciding factor in whether a customer adopts your
platform.

This module covers the tools, techniques, and strategies for rapidly building AI-powered
prototypes and delivering compelling technical demonstrations. You will learn Streamlit and
Gradio -- the two dominant Python frameworks for interactive AI demos -- along with the
softer skills of audience analysis, failure handling, and customer handoff that separate
good engineers from great solutions engineers.

> **Swift Developer Note:** Think of Streamlit as the "SwiftUI Previews" of the Python AI
> world -- it lets you build interactive UIs with minimal boilerplate, but it runs as a
> full web application rather than an IDE preview. Gradio is more like a specialized demo
> framework, similar in spirit to what you might build with a quick Playground + UI layer.

---

## 1. The Art of the Technical Demo

### Why Demos Matter for Solutions Engineers

At companies like Anthropic, OpenAI, Google, and Cohere, solutions engineers sit at the
intersection of engineering and customer success. Your job is not just to build -- it is to
convince. A working demo accomplishes what slides and documentation cannot:

- **Credibility**: A live, working prototype proves that your claims are real
- **Specificity**: Customers see their use case, not a generic pitch
- **Discovery**: Live interaction reveals requirements that meetings never surface
- **Urgency**: A working demo compresses the sales cycle by removing uncertainty

### Demo vs POC vs Prototype

These terms are often used interchangeably, but they serve different purposes:

| Aspect | Demo | POC (Proof of Concept) | Prototype |
|--------|------|------------------------|-----------|
| **Purpose** | Show capabilities | Prove feasibility | Explore design |
| **Audience** | Customer/stakeholder | Technical team | Internal team |
| **Fidelity** | Polished UI, curated data | Functional, rough edges OK | Iterative, evolving |
| **Lifespan** | Single meeting/event | Days to weeks | Weeks to months |
| **Data** | Curated/synthetic | Customer's actual data | Mix of real and synthetic |
| **Code quality** | Good enough to show | Good enough to validate | Good enough to learn |
| **Outcome** | "We want this" | "This is possible" | "This is how it should work" |

### Audience Analysis

Before writing a single line of code, profile your audience:

```python
# Framework for audience analysis -- use this as a mental model
audience_profiles = {
    "technical_lead": {
        "cares_about": ["architecture", "scalability", "integration complexity"],
        "demo_focus": "Show the API calls, explain the pipeline, discuss tradeoffs",
        "risk": "Will ask about edge cases you haven't considered",
        "language": "Technical -- use correct terminology",
    },
    "product_manager": {
        "cares_about": ["user experience", "timeline", "feature completeness"],
        "demo_focus": "Show the end-to-end workflow, emphasize speed of delivery",
        "risk": "Will ask about features you haven't built yet",
        "language": "Feature-oriented -- benefits over implementation",
    },
    "executive": {
        "cares_about": ["ROI", "competitive advantage", "risk mitigation"],
        "demo_focus": "Show the business impact, keep it high-level",
        "risk": "Has 5 minutes of attention, not 30",
        "language": "Business outcomes -- revenue, cost, time savings",
    },
    "ml_engineer": {
        "cares_about": ["model quality", "eval metrics", "training pipeline"],
        "demo_focus": "Show evaluation results, discuss model selection rationale",
        "risk": "Will challenge your methodology",
        "language": "ML-specific -- precision, recall, latency percentiles",
    },
}
```

### Demo Preparation Checklist

```python
demo_checklist = {
    "before_building": [
        "Identify primary audience and their top 3 concerns",
        "Define the 'aha moment' -- the single thing they must see",
        "Set a time limit for the demo (aim for 10-15 minutes of live demo)",
        "Identify 3 scenarios to demonstrate (happy path, edge case, failure recovery)",
    ],
    "while_building": [
        "Build the happy path first, polish second",
        "Create pre-loaded fallback responses for network failures",
        "Add loading indicators -- silence during API calls kills momentum",
        "Test with realistic data, not lorem ipsum",
    ],
    "before_presenting": [
        "Run the full demo 3 times end-to-end",
        "Test on the exact machine/network you will present from",
        "Prepare offline fallback (screenshots, recorded video)",
        "Have a colleague try to break it",
    ],
    "during_demo": [
        "Narrate what you are doing and why",
        "Pause after the aha moment -- let it land",
        "Keep a mental list of questions to defer to follow-up",
        "End with clear next steps, not an awkward silence",
    ],
}
```

---

## 2. Streamlit for AI Prototypes

### What is Streamlit?

Streamlit is a Python framework that turns scripts into interactive web applications with
minimal code. It is the most popular tool for AI/ML demos because it requires zero frontend
knowledge and integrates seamlessly with the Python data science ecosystem.

### Installation

```bash
pip install streamlit

# Verify installation
streamlit hello  # Opens a sample app in your browser
```

### Your First Streamlit App

```python
# app.py
import streamlit as st

st.set_page_config(
    page_title="AI Demo",
    page_icon="🤖",
    layout="wide",
)

st.title("My First AI Demo")
st.write("This is a Streamlit app. Every time you interact with a widget, "
         "the entire script re-runs from top to bottom.")

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", ["claude-3-5-sonnet", "claude-3-opus", "gpt-4o"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.number_input("Max Tokens", 100, 4096, 1024, step=100)

# Main content
user_input = st.text_area("Enter your prompt:", height=100)

if st.button("Generate"):
    if user_input:
        with st.spinner("Generating response..."):
            # In a real app, this calls an LLM API
            st.success(f"Response generated using {model} at temperature {temperature}")
            st.write(f"You said: {user_input}")
    else:
        st.warning("Please enter a prompt first.")
```

```bash
# Run the app
streamlit run app.py
```

> **Swift Developer Note:** Streamlit's execution model is fundamentally different from
> SwiftUI. In SwiftUI, your `body` re-evaluates when `@State` changes. In Streamlit, the
> _entire script_ re-runs from top to bottom on every interaction. This feels strange at
> first but is actually simpler -- there is no state management framework to learn.

### Building a Chat Interface

Chat is the most common AI demo pattern. Streamlit has built-in chat components:

```python
# chat_demo.py
import streamlit as st
import anthropic

st.title("Chat with Claude")

# Initialize the Anthropic client
client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("What would you like to discuss?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system="You are a helpful AI assistant.",
                messages=st.session_state.messages,
            )
            assistant_message = response.content[0].text
            st.markdown(assistant_message)

    # Add assistant message to history
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_message}
    )
```

### Streaming Chat Responses

For a more polished demo, stream tokens as they arrive:

```python
# streaming_chat.py
import streamlit as st
import anthropic

st.title("Streaming Chat Demo")

client = anthropic.Anthropic()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Stream tokens into a placeholder
        response_placeholder = st.empty()
        full_response = ""

        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=st.session_state.messages,
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )
```

### File Upload and Document Processing

A common demo scenario: "Can your AI understand my documents?"

```python
# document_qa.py
import streamlit as st
import anthropic
from pathlib import Path

st.title("Document Q&A Demo")

client = anthropic.Anthropic()

# File upload
uploaded_file = st.file_uploader(
    "Upload a document",
    type=["txt", "md", "csv", "json", "py"],
    help="Upload a text file to ask questions about it",
)

if uploaded_file is not None:
    # Read and display the file
    content = uploaded_file.read().decode("utf-8")

    with st.expander("View Document Contents", expanded=False):
        st.code(content, language=Path(uploaded_file.name).suffix.lstrip("."))

    st.success(f"Loaded: {uploaded_file.name} ({len(content):,} characters)")

    # Store document in session state
    st.session_state["document"] = content
    st.session_state["document_name"] = uploaded_file.name

if "document" in st.session_state:
    question = st.text_input("Ask a question about the document:")

    if question:
        with st.spinner("Analyzing document..."):
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=(
                    "You are a document analysis assistant. Answer questions "
                    "based on the provided document. If the answer is not in the "
                    "document, say so clearly."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Document ({st.session_state['document_name']}):\n"
                            f"```\n{st.session_state['document']}\n```\n\n"
                            f"Question: {question}"
                        ),
                    }
                ],
            )
            st.markdown("### Answer")
            st.write(response.content[0].text)
```

### Session State Deep Dive

Streamlit's session state is essential for any non-trivial demo:

```python
# session_state_demo.py
import streamlit as st

# Initialize state -- only runs on first load
if "counter" not in st.session_state:
    st.session_state.counter = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "config" not in st.session_state:
    st.session_state.config = {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
    }

st.title("Session State Demo")

# Display current state
st.metric("Counter", st.session_state.counter)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Increment"):
        st.session_state.counter += 1
        st.session_state.history.append(f"Incremented to {st.session_state.counter}")

with col2:
    if st.button("Decrement"):
        st.session_state.counter -= 1
        st.session_state.history.append(f"Decremented to {st.session_state.counter}")

with col3:
    if st.button("Reset"):
        st.session_state.counter = 0
        st.session_state.history.append("Reset to 0")

# Show history
if st.session_state.history:
    st.subheader("Action History")
    for i, action in enumerate(reversed(st.session_state.history[-10:]), 1):
        st.text(f"{i}. {action}")


# Callbacks -- alternative to checking button clicks
def on_model_change():
    """Called when the model selector changes."""
    st.session_state.config["model"] = st.session_state.model_selector


st.selectbox(
    "Model",
    ["claude-sonnet-4-20250514", "claude-3-opus", "gpt-4o"],
    key="model_selector",
    on_change=on_model_change,
)
```

### Caching for Performance

API calls are expensive and slow. Cache aggressively in demos:

```python
# caching_demo.py
import streamlit as st
import anthropic
import time

client = anthropic.Anthropic()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_embedding(text: str) -> list[float]:
    """Cache embeddings to avoid redundant API calls.

    @st.cache_data serializes the return value and stores it.
    Same input = same output, no API call.
    """
    # Simulated embedding -- in production, use a real embedding API
    import hashlib
    hash_val = hashlib.sha256(text.encode()).hexdigest()
    return [int(hash_val[i:i+2], 16) / 255.0 for i in range(0, 64, 2)]


@st.cache_resource  # Cache the resource (like a database connection)
def get_anthropic_client():
    """Cache the client object -- created once, reused across reruns.

    @st.cache_resource is for objects that should NOT be serialized:
    database connections, ML models, API clients.
    """
    return anthropic.Anthropic()


@st.cache_data(ttl=300, show_spinner="Loading data...")
def load_demo_data(dataset_name: str) -> dict:
    """Load and cache demo datasets.

    The show_spinner parameter adds a loading message automatically.
    """
    time.sleep(2)  # Simulate loading time
    return {
        "customer_support": {
            "queries": ["How do I reset my password?", "Where is my order?"],
            "count": 1500,
        },
        "code_review": {
            "queries": ["Review this Python function", "Find bugs in this code"],
            "count": 800,
        },
    }.get(dataset_name, {"queries": [], "count": 0})


st.title("Caching Demo")

dataset = st.selectbox("Dataset", ["customer_support", "code_review"])
data = load_demo_data(dataset)  # Only loads once per dataset

st.write(f"Loaded {data['count']} records")
st.write("Sample queries:", data["queries"])
```

> **Swift Developer Note:** Streamlit's `@st.cache_data` is conceptually similar to
> `NSCache` in iOS development -- it stores computed results and returns the cached version
> on subsequent calls. The key difference is that Streamlit's cache is keyed by function
> arguments, not by an explicit key you provide.

### Multi-Page Streamlit Apps

For larger demos, split into multiple pages:

```
my_demo/
  app.py                    # Main entry point
  pages/
    1_Chat.py               # Page 1
    2_Document_Analysis.py  # Page 2
    3_Settings.py           # Page 3
  utils/
    __init__.py
    ai_client.py
    demo_data.py
```

```python
# app.py -- main entry point
import streamlit as st

st.set_page_config(
    page_title="AI Solutions Demo",
    page_icon="🧠",
    layout="wide",
)

st.title("AI Solutions Demo")
st.markdown("""
Welcome to our AI platform demo. Use the sidebar to navigate between features:

- **Chat**: Interactive conversation with our AI models
- **Document Analysis**: Upload and analyze documents
- **Settings**: Configure model parameters
""")

# Shared state initialization
if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = True
```

```python
# pages/1_Chat.py
import streamlit as st

st.title("Chat Interface")
st.write("This page provides the chat functionality.")
# ... chat implementation from above
```

### Deployment Options

```bash
# Option 1: Streamlit Community Cloud (free, easiest)
# Push to GitHub, connect at share.streamlit.io

# Option 2: Docker
# Dockerfile
cat << 'DOCKERFILE'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
DOCKERFILE

# Option 3: Cloud Run / Railway / Render
# Most PaaS providers support Streamlit apps natively
```

---

## 3. Gradio for ML Demos

### What is Gradio?

Gradio is a Python library for building ML demos and web interfaces. While Streamlit is a
general-purpose app framework, Gradio is specifically designed for ML model interaction --
it excels at input/output demos where you want to showcase a model's capabilities.

### Installation

```bash
pip install gradio
```

### Your First Gradio App

```python
# gradio_hello.py
import gradio as gr

def greet(name: str, intensity: int) -> str:
    return f"Hello, {name}! " * intensity

demo = gr.Interface(
    fn=greet,
    inputs=[
        gr.Textbox(label="Name", placeholder="Enter your name"),
        gr.Slider(1, 5, value=1, step=1, label="Intensity"),
    ],
    outputs=gr.Textbox(label="Greeting"),
    title="Greeting Generator",
    description="A simple demo showing Gradio's Interface API.",
)

demo.launch()
```

```bash
python gradio_hello.py
# Opens at http://localhost:7860
```

### Building an AI Chat with Gradio

```python
# gradio_chat.py
import gradio as gr
import anthropic

client = anthropic.Anthropic()


def chat(message: str, history: list[dict]) -> str:
    """Process a chat message and return the response.

    Gradio's ChatInterface passes the full conversation history
    automatically -- no manual session state management needed.
    """
    messages = []
    for entry in history:
        messages.append({"role": entry["role"], "content": entry["content"]})
    messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="You are a helpful AI assistant for technical demos.",
        messages=messages,
    )
    return response.content[0].text


demo = gr.ChatInterface(
    fn=chat,
    title="Chat with Claude",
    description="An interactive chat powered by Claude.",
    examples=[
        "Explain RAG in simple terms",
        "Write a Python function to calculate cosine similarity",
        "What are the key differences between fine-tuning and prompt engineering?",
    ],
    type="messages",
)

demo.launch()
```

### Streaming with Gradio

```python
# gradio_streaming.py
import gradio as gr
import anthropic

client = anthropic.Anthropic()


def stream_chat(message: str, history: list[dict]) -> str:
    """Stream responses token by token."""
    messages = []
    for entry in history:
        messages.append({"role": entry["role"], "content": entry["content"]})
    messages.append({"role": "user", "content": message})

    partial_response = ""
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            partial_response += text
            yield partial_response  # Gradio handles streaming via generators


demo = gr.ChatInterface(
    fn=stream_chat,
    title="Streaming Chat Demo",
    type="messages",
)

demo.launch()
```

### Gradio Blocks Layout

For complex demos, use `gr.Blocks` instead of `gr.Interface`:

```python
# gradio_blocks.py
import gradio as gr
import anthropic

client = anthropic.Anthropic()


def analyze_text(text: str, task: str, model: str) -> tuple[str, dict]:
    """Analyze text based on the selected task."""
    prompts = {
        "Summarize": "Summarize the following text concisely:",
        "Extract Key Points": "Extract the key points from this text as a bulleted list:",
        "Sentiment Analysis": (
            "Analyze the sentiment of this text. Return a JSON object with "
            "'sentiment' (positive/negative/neutral), 'confidence' (0-1), "
            "and 'explanation'."
        ),
        "Translate to Spanish": "Translate the following text to Spanish:",
    }

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"{prompts[task]}\n\n{text}"}
        ],
    )

    result = response.content[0].text
    metadata = {
        "model": model,
        "task": task,
        "input_length": len(text),
        "output_length": len(result),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

    return result, metadata


with gr.Blocks(title="Text Analysis Suite", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Text Analysis Suite")
    gr.Markdown("Analyze text using various AI-powered tasks.")

    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="Input Text",
                placeholder="Paste your text here...",
                lines=8,
            )
            with gr.Row():
                task_selector = gr.Dropdown(
                    choices=[
                        "Summarize",
                        "Extract Key Points",
                        "Sentiment Analysis",
                        "Translate to Spanish",
                    ],
                    value="Summarize",
                    label="Task",
                )
                model_selector = gr.Dropdown(
                    choices=[
                        "claude-sonnet-4-20250514",
                        "claude-3-haiku-20240307",
                    ],
                    value="claude-sonnet-4-20250514",
                    label="Model",
                )
            analyze_btn = gr.Button("Analyze", variant="primary")

        with gr.Column(scale=2):
            output_text = gr.Textbox(label="Result", lines=8)
            output_metadata = gr.JSON(label="Metadata")

    # Wire up the event
    analyze_btn.click(
        fn=analyze_text,
        inputs=[text_input, task_selector, model_selector],
        outputs=[output_text, output_metadata],
    )

    # Examples that auto-populate the input
    gr.Examples(
        examples=[
            [
                "Artificial intelligence is transforming how businesses operate. "
                "From automating customer service to predicting market trends, "
                "AI tools are becoming essential for competitive advantage.",
                "Summarize",
                "claude-sonnet-4-20250514",
            ],
            [
                "The product quality has declined significantly over the past year. "
                "Customer support is unresponsive and the pricing keeps increasing "
                "without any new features.",
                "Sentiment Analysis",
                "claude-sonnet-4-20250514",
            ],
        ],
        inputs=[text_input, task_selector, model_selector],
    )

demo.launch()
```

### Sharing Gradio Apps

One of Gradio's killer features is instant public sharing:

```python
# Share publicly via Gradio's tunneling service
demo.launch(share=True)
# Output: Running on public URL: https://xxxxx.gradio.live
# Link is valid for 72 hours -- perfect for demos

# Customize the server
demo.launch(
    server_name="0.0.0.0",   # Listen on all interfaces
    server_port=7860,
    share=False,              # No public tunnel
    auth=("admin", "demo123"),  # Basic auth for private demos
)
```

### Deploying to Hugging Face Spaces

```bash
# 1. Create a Hugging Face account and space
# 2. Create the following files:

# requirements.txt
# anthropic
# gradio

# app.py -- your Gradio app (same code as above)

# 3. Push to Hugging Face
pip install huggingface_hub
huggingface-cli login
```

```python
# upload_to_spaces.py
from huggingface_hub import HfApi

api = HfApi()
api.create_repo(
    repo_id="your-username/ai-text-analyzer",
    repo_type="space",
    space_sdk="gradio",
)
api.upload_folder(
    folder_path="./my_demo",
    repo_id="your-username/ai-text-analyzer",
    repo_type="space",
)
```

### Streamlit vs Gradio -- When to Use Which

| Criterion | Streamlit | Gradio |
|-----------|-----------|--------|
| **Best for** | Full applications, dashboards | Model demos, input/output |
| **Learning curve** | Moderate | Very low |
| **Layout** | Top-to-bottom script | Blocks/Interface components |
| **State management** | Session state | Built-in for chat, limited otherwise |
| **Sharing** | Deploy to cloud | `share=True` -- instant public link |
| **Multi-page** | Native support | Tabs within Blocks |
| **Theming** | Configurable | Multiple themes + custom CSS |
| **HF Spaces** | Supported | First-class support |
| **Best demo scenario** | "Here is our full product" | "Try this model right now" |

---

## 4. POC Architecture

### Structuring a Proof-of-Concept

A well-structured POC demonstrates technical feasibility while remaining disposable. You
should be able to build it in days, not weeks.

```
customer-poc/
  README.md               # Setup, running, and context
  requirements.txt         # Pinned dependencies
  .env.example             # Required environment variables
  app.py                   # Main demo entry point
  config.py                # All tunable parameters in one place
  data/
    sample_data.json       # Curated demo data
    customer_sample.csv    # Anonymized customer data (if provided)
  src/
    __init__.py
    pipeline.py            # Core AI pipeline
    prompts.py             # All prompts in one file (easy to iterate)
    utils.py               # Shared utilities
  tests/
    test_pipeline.py       # Smoke tests for core functionality
  fallbacks/
    cached_responses.json  # Pre-computed responses for offline demos
  docs/
    architecture.png       # Simple architecture diagram
    demo_script.md         # Step-by-step demo walkthrough
```

### The Config-Driven POC

Make every tunable parameter configurable without code changes:

```python
# config.py
from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class POCConfig:
    """Central configuration for the POC.

    All parameters that might change between demo runs live here.
    This makes it easy to adapt the demo for different customers
    without touching the core pipeline code.
    """

    # Model settings
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 1024
    temperature: float = 0.3

    # Customer-specific
    customer_name: str = "Acme Corp"
    industry: str = "financial_services"
    use_case: str = "customer_support"

    # Data paths
    data_dir: Path = Path("data")
    fallback_dir: Path = Path("fallbacks")

    # Feature flags for progressive demos
    enable_streaming: bool = True
    enable_rag: bool = False
    enable_tool_use: bool = False
    enable_multimodal: bool = False

    # API configuration
    api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    base_url: str | None = None

    # Demo-specific
    max_demo_queries: int = 50  # Rate limit for demo environments
    demo_timeout_seconds: int = 30

    def validate(self) -> list[str]:
        """Return a list of configuration issues."""
        issues = []
        if not self.api_key:
            issues.append("ANTHROPIC_API_KEY not set")
        if not self.data_dir.exists():
            issues.append(f"Data directory not found: {self.data_dir}")
        return issues


# Usage
config = POCConfig()
errors = config.validate()
if errors:
    print(f"Configuration issues: {errors}")
```

### Prompts as First-Class Citizens

Never bury prompts inside pipeline code. Make them visible and editable:

```python
# prompts.py
"""All prompts for the POC, organized by use case.

Keeping prompts in one file makes it easy to:
1. Iterate on prompt quality without touching pipeline code
2. Show customers exactly what prompts are being used
3. A/B test different prompt variants
4. Hand off to the customer's team for customization
"""

SYSTEM_PROMPTS = {
    "customer_support": (
        "You are a customer support agent for {customer_name}. "
        "You help customers with their inquiries about {industry} products and services. "
        "Be professional, empathetic, and concise. "
        "If you don't know the answer, say so and offer to escalate."
    ),
    "code_review": (
        "You are a senior software engineer reviewing code. "
        "Provide constructive feedback focusing on: "
        "1) Correctness, 2) Performance, 3) Readability, 4) Security. "
        "Use specific line references when possible."
    ),
    "document_analysis": (
        "You are a document analysis assistant. "
        "Extract key information from the provided document. "
        "Structure your response with clear headings and bullet points."
    ),
}

TASK_PROMPTS = {
    "summarize": "Summarize the following content in 3-5 bullet points:\n\n{content}",
    "extract_entities": (
        "Extract all named entities (people, organizations, locations, dates) "
        "from the following text. Return as JSON.\n\n{content}"
    ),
    "classify": (
        "Classify the following text into one of these categories: "
        "{categories}. Return only the category name.\n\n{content}"
    ),
}


def get_system_prompt(use_case: str, **kwargs) -> str:
    """Get a system prompt with variables filled in."""
    template = SYSTEM_PROMPTS.get(use_case, SYSTEM_PROMPTS["customer_support"])
    return template.format(**kwargs)


def get_task_prompt(task: str, **kwargs) -> str:
    """Get a task prompt with variables filled in."""
    template = TASK_PROMPTS.get(task, "{content}")
    return template.format(**kwargs)
```

### What to Include vs Exclude in a POC

```python
poc_scope = {
    "include": [
        "Core AI pipeline (the thing you are proving works)",
        "Simple but functional UI (Streamlit or Gradio)",
        "Error handling for common failures (API timeout, bad input)",
        "2-3 pre-built scenarios demonstrating the value",
        "Basic logging and cost tracking",
        "README with setup instructions",
        "Configuration file for easy customization",
    ],
    "exclude": [
        "User authentication (use env vars or basic auth)",
        "Database persistence (use in-memory or file-based storage)",
        "Production error monitoring (simple try/except is fine)",
        "CI/CD pipeline (manual deployment is fine)",
        "Multi-tenancy (one customer at a time)",
        "Comprehensive test suite (smoke tests only)",
        "Performance optimization (correctness first)",
        "Custom CSS/styling (default themes are fine)",
    ],
}
```

> **Swift Developer Note:** This is analogous to building an iOS prototype with hardcoded
> data, no Core Data persistence, and a single storyboard. The goal is identical -- prove
> the concept works and get feedback -- but the Python ecosystem lets you go from zero to
> a shareable web demo in hours instead of the days it takes to get a TestFlight build out.

---

## 5. Demo Data and Scenarios

### Creating Compelling Demo Datasets

The data you use in a demo is as important as the code. Bad data makes even great AI
look broken. Good data makes your demo feel like the customer's own product.

```python
# demo_data.py
"""Generate and manage demo datasets for AI prototypes."""

import json
import random
from datetime import datetime, timedelta


def generate_support_tickets(
    n: int = 50,
    customer_name: str = "Acme Corp",
) -> list[dict]:
    """Generate realistic customer support tickets.

    These should cover the spectrum of complexity:
    - Easy wins (the AI handles perfectly)
    - Medium complexity (AI needs context)
    - Hard cases (AI acknowledges limitations)
    """
    categories = [
        "billing", "technical", "account", "feature_request", "complaint"
    ]
    urgencies = ["low", "medium", "high", "critical"]

    templates = {
        "billing": [
            "I was charged twice for my subscription this month. Order #{order_id}.",
            "Can I get a refund for the unused portion of my annual plan?",
            "My invoice shows a charge for a service I never signed up for.",
            "I need to update my payment method but the portal is not working.",
        ],
        "technical": [
            "The API is returning 500 errors when I send batch requests.",
            "My integration stopped working after your latest update.",
            "How do I configure SSO with our Azure AD instance?",
            "Getting rate limited even though I'm well under my quota.",
        ],
        "account": [
            "I need to add 5 new users to our enterprise account.",
            "Can I transfer my account data to a different region?",
            "My admin access was revoked and I don't know why.",
        ],
        "feature_request": [
            "We need webhook support for real-time event notifications.",
            "Can you add support for custom model fine-tuning?",
            "We'd like to see a dashboard for tracking API usage by team.",
        ],
        "complaint": [
            "Response times have been terrible this week. Is there an outage?",
            "Your documentation is outdated and caused us to deploy a broken integration.",
            "We were promised features in our contract that still aren't available.",
        ],
    }

    tickets = []
    for i in range(n):
        category = random.choice(categories)
        template_list = templates[category]
        ticket = {
            "id": f"TICKET-{1000 + i}",
            "customer": customer_name,
            "category": category,
            "urgency": random.choice(urgencies),
            "subject": random.choice(template_list).format(
                order_id=f"ORD-{random.randint(10000, 99999)}"
            ),
            "created_at": (
                datetime.now() - timedelta(hours=random.randint(1, 720))
            ).isoformat(),
            "status": random.choice(["open", "in_progress", "waiting"]),
        }
        tickets.append(ticket)

    return tickets


def generate_code_samples() -> list[dict]:
    """Generate code samples for code review demos."""
    return [
        {
            "id": "sample_1",
            "title": "User Authentication Handler",
            "language": "python",
            "difficulty": "easy",
            "code": '''
def authenticate(username, password):
    # TODO: This is obviously insecure -- good for demo
    users = {"admin": "password123", "user": "letmein"}
    if username in users and users[username] == password:
        return {"token": "fake-jwt-token", "user": username}
    return None
''',
            "expected_issues": [
                "Hardcoded credentials",
                "Plain text password comparison",
                "No password hashing",
                "No rate limiting",
            ],
        },
        {
            "id": "sample_2",
            "title": "Data Processing Pipeline",
            "language": "python",
            "difficulty": "medium",
            "code": '''
def process_data(items):
    results = []
    for item in items:
        try:
            processed = transform(item)
            results.append(processed)
        except:
            pass  # Silently ignore errors
    return results

def transform(item):
    return {"value": item["price"] * 1.1, "name": item["name"].upper()}
''',
            "expected_issues": [
                "Bare except clause",
                "Silent error swallowing",
                "Magic number (1.1)",
                "No input validation",
                "No type hints",
            ],
        },
    ]


# Save demo data to files
def save_demo_data(output_dir: str = "data"):
    """Generate and save all demo datasets."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    tickets = generate_support_tickets()
    with open(f"{output_dir}/support_tickets.json", "w") as f:
        json.dump(tickets, f, indent=2)

    code_samples = generate_code_samples()
    with open(f"{output_dir}/code_samples.json", "w") as f:
        json.dump(code_samples, f, indent=2)

    print(f"Generated {len(tickets)} support tickets")
    print(f"Generated {len(code_samples)} code samples")


if __name__ == "__main__":
    save_demo_data()
```

### Handling "Bring Your Own Data" Requests

Customers often want to see the AI work on their actual data. This is a make-or-break
moment:

```python
# byod_handler.py
"""Handle customer-provided data safely and effectively."""

import json
import csv
import io
from pathlib import Path


class BYODHandler:
    """Bring Your Own Data handler for customer demos.

    Validates, sanitizes, and adapts customer data for the demo pipeline.
    """

    SUPPORTED_FORMATS = {".csv", ".json", ".txt", ".jsonl"}
    MAX_FILE_SIZE_MB = 10
    MAX_RECORDS = 1000

    def __init__(self):
        self.validation_errors: list[str] = []
        self.warnings: list[str] = []

    def validate_file(self, file_path: Path) -> bool:
        """Validate a customer-provided file before processing."""
        self.validation_errors = []
        self.warnings = []

        # Check file exists and is readable
        if not file_path.exists():
            self.validation_errors.append(f"File not found: {file_path}")
            return False

        # Check file size
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            self.validation_errors.append(
                f"File too large: {size_mb:.1f}MB (max {self.MAX_FILE_SIZE_MB}MB)"
            )
            return False

        # Check format
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            self.validation_errors.append(
                f"Unsupported format: {file_path.suffix}. "
                f"Supported: {self.SUPPORTED_FORMATS}"
            )
            return False

        return True

    def load_and_preview(
        self,
        file_path: Path,
        max_preview: int = 5,
    ) -> dict:
        """Load customer data and return a preview for confirmation.

        Always preview data before running the full demo -- this catches
        format issues and lets you adapt your prompts.
        """
        if not self.validate_file(file_path):
            return {"error": self.validation_errors}

        suffix = file_path.suffix.lower()

        if suffix == ".json":
            with open(file_path) as f:
                data = json.load(f)
            if isinstance(data, list):
                records = data[:max_preview]
                total = len(data)
            else:
                records = [data]
                total = 1

        elif suffix == ".csv":
            records = []
            total = 0
            with open(file_path) as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i < max_preview:
                        records.append(dict(row))
                    total = i + 1

        elif suffix in (".txt", ".jsonl"):
            records = []
            total = 0
            with open(file_path) as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if line:
                        if i < max_preview:
                            if suffix == ".jsonl":
                                records.append(json.loads(line))
                            else:
                                records.append({"text": line})
                        total += 1

        else:
            return {"error": [f"Unsupported format: {suffix}"]}

        if total > self.MAX_RECORDS:
            self.warnings.append(
                f"File contains {total} records. "
                f"Only first {self.MAX_RECORDS} will be processed."
            )

        return {
            "preview": records,
            "total_records": total,
            "columns": list(records[0].keys()) if records else [],
            "warnings": self.warnings,
        }

    def detect_text_column(self, records: list[dict]) -> str | None:
        """Auto-detect which column contains the primary text content.

        Heuristic: find the column with the longest average string length.
        """
        if not records:
            return None

        avg_lengths = {}
        for key in records[0].keys():
            lengths = [
                len(str(r.get(key, "")))
                for r in records
                if isinstance(r.get(key), str)
            ]
            if lengths:
                avg_lengths[key] = sum(lengths) / len(lengths)

        if avg_lengths:
            return max(avg_lengths, key=avg_lengths.get)
        return None
```

### Synthetic Data Generation with LLMs

When you need realistic data but cannot use real customer data:

```python
# synthetic_data.py
import anthropic
import json


def generate_synthetic_data(
    description: str,
    schema: dict,
    n: int = 10,
    industry: str = "technology",
) -> list[dict]:
    """Use an LLM to generate realistic synthetic data.

    This is invaluable for demos where you need data that looks
    like it came from the customer's domain but contains no real PII.
    """
    client = anthropic.Anthropic()

    prompt = f"""Generate exactly {n} realistic synthetic data records for the following use case:

Description: {description}
Industry: {industry}

Each record must follow this JSON schema:
{json.dumps(schema, indent=2)}

Requirements:
- Data should be realistic and varied (not repetitive)
- Use plausible names, dates, and values
- Include some edge cases (very short text, special characters, etc.)
- Do NOT include any real PII

Return ONLY a JSON array of {n} objects. No other text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    # Parse the JSON from the response
    text = response.content[0].text
    # Handle markdown code blocks if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    return json.loads(text.strip())


# Example usage
if __name__ == "__main__":
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Unique ticket ID"},
            "subject": {"type": "string", "description": "Support ticket subject"},
            "body": {"type": "string", "description": "Detailed description of the issue"},
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"],
            },
            "customer_type": {
                "type": "string",
                "enum": ["free", "pro", "enterprise"],
            },
        },
    }

    data = generate_synthetic_data(
        description="Customer support tickets for an AI API platform",
        schema=schema,
        n=5,
        industry="technology",
    )

    for record in data:
        print(json.dumps(record, indent=2))
```

---

## 6. Live Demo Techniques

### The Golden Rule: Never Let Silence Kill Your Demo

The most common demo failure is not a crash -- it is an awkward silence while waiting for
an API response. Every second of silence erodes confidence.

```python
# resilient_demo.py
"""A demo app built with resilience as a first-class concern."""

import streamlit as st
import anthropic
import json
import time
from pathlib import Path


# Load fallback responses
@st.cache_data
def load_fallbacks() -> dict:
    """Pre-computed responses for when the API is unavailable."""
    fallback_path = Path("fallbacks/cached_responses.json")
    if fallback_path.exists():
        with open(fallback_path) as f:
            return json.load(f)
    return {}


def call_ai_with_fallback(
    prompt: str,
    fallback_key: str | None = None,
    timeout: float = 15.0,
) -> tuple[str, bool]:
    """Call the AI API with automatic fallback on failure.

    Returns (response_text, used_fallback).
    """
    fallbacks = load_fallbacks()

    try:
        client = anthropic.Anthropic(timeout=timeout)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text, False

    except anthropic.APITimeoutError:
        st.warning("API response is taking longer than usual. Using cached response.")
        if fallback_key and fallback_key in fallbacks:
            return fallbacks[fallback_key], True
        return "Response is taking longer than expected. Let me try a simpler approach...", True

    except anthropic.APIConnectionError:
        st.error("Network connectivity issue detected.")
        if fallback_key and fallback_key in fallbacks:
            st.info("Showing a pre-computed example response.")
            return fallbacks[fallback_key], True
        return "Network issue -- let me show you a pre-recorded example.", True

    except anthropic.RateLimitError:
        st.warning("Rate limit reached. Showing cached response.")
        if fallback_key and fallback_key in fallbacks:
            return fallbacks[fallback_key], True
        return "We've hit the rate limit. This is a demo constraint, not a production one.", True

    except Exception as e:
        st.error(f"Unexpected error: {type(e).__name__}")
        if fallback_key and fallback_key in fallbacks:
            return fallbacks[fallback_key], True
        return f"Something unexpected happened. Let me walk you through what would happen here.", True


# Generate fallback cache before the demo
def pre_generate_fallbacks(scenarios: dict[str, str], output_path: str = "fallbacks"):
    """Run all demo scenarios and cache the responses.

    Run this the night before your demo to ensure you have fresh fallbacks.
    """
    Path(output_path).mkdir(exist_ok=True)
    client = anthropic.Anthropic()
    cached = {}

    for key, prompt in scenarios.items():
        print(f"Generating fallback for: {key}")
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        cached[key] = response.content[0].text

    with open(f"{output_path}/cached_responses.json", "w") as f:
        json.dump(cached, f, indent=2)

    print(f"Cached {len(cached)} fallback responses.")
```

### Progressive Complexity Pattern

Start simple, build complexity as the audience's interest grows:

```python
# progressive_demo.py
"""Demo structured with progressive complexity levels."""

import streamlit as st

st.title("AI Customer Support Assistant")

# Level selector in sidebar
with st.sidebar:
    st.header("Demo Level")
    level = st.radio(
        "Select demo complexity:",
        [
            "Level 1: Basic Q&A",
            "Level 2: Context-Aware Responses",
            "Level 3: Multi-Turn with Memory",
            "Level 4: Tool Use & Actions",
            "Level 5: Full Pipeline with RAG",
        ],
        index=0,
    )

    st.divider()
    st.markdown("""
    **Demo Progression:**
    - Start with Level 1 to show basic capabilities
    - Progress through levels based on audience interest
    - Each level builds on the previous one
    - Skip to any level if the audience asks about specific features
    """)

# Level 1: Simple question answering
if level.startswith("Level 1"):
    st.subheader("Basic Q&A")
    st.write("The AI answers questions using only its training data.")

    query = st.text_input("Ask a question:")
    if query:
        # Simple API call
        st.info("This is Level 1 -- direct question answering, no context window.")
        # ... API call here

# Level 2: Add context
elif level.startswith("Level 2"):
    st.subheader("Context-Aware Responses")
    st.write("Now the AI uses your company's knowledge base.")

    # Show the knowledge base
    with st.expander("View Knowledge Base"):
        st.json({
            "company": "Acme Corp",
            "products": ["Widget Pro", "Widget Enterprise"],
            "policies": {
                "refund_window": "30 days",
                "support_hours": "24/7 for Enterprise",
            },
        })

    query = st.text_input("Ask about Acme Corp:")
    if query:
        st.info("Level 2 -- the AI now has company-specific context in its system prompt.")
        # ... API call with system prompt containing knowledge base

# Level 3: Multi-turn conversation
elif level.startswith("Level 3"):
    st.subheader("Multi-Turn Conversation")
    st.write("The AI remembers previous messages in the conversation.")
    # ... Full chat interface with session state

# Level 4: Tool use
elif level.startswith("Level 4"):
    st.subheader("Tool Use & Actions")
    st.write("The AI can take actions: check order status, create tickets, etc.")
    # ... Chat interface with tool use

# Level 5: Full RAG pipeline
elif level.startswith("Level 5"):
    st.subheader("Full RAG Pipeline")
    st.write("The AI searches your document database for relevant information.")
    # ... Full RAG implementation
```

### Handling Failures Gracefully During Live Demos

```python
# graceful_failures.py
"""Patterns for handling failures during live demos."""

import streamlit as st
import time


class DemoGuard:
    """Wrap demo operations with graceful failure handling."""

    def __init__(self):
        self.error_count = 0
        self.max_errors = 3

    def safe_api_call(self, fn, *args, **kwargs):
        """Execute a function with demo-friendly error handling.

        In a live demo, the worst thing is a stack trace on screen.
        This wrapper ensures the audience sees helpful messages, not errors.
        """
        try:
            result = fn(*args, **kwargs)
            self.error_count = 0  # Reset on success
            return result

        except Exception as e:
            self.error_count += 1
            error_type = type(e).__name__

            if self.error_count >= self.max_errors:
                st.error(
                    "We're experiencing connectivity issues. "
                    "Let me switch to our pre-recorded walkthrough."
                )
                return self._switch_to_recording()

            # User-friendly error messages
            friendly_messages = {
                "APITimeoutError": (
                    "The model is taking a moment to think -- this occasionally "
                    "happens with complex queries. Let me try again with a simpler prompt."
                ),
                "RateLimitError": (
                    "We've hit the demo rate limit. In production, you'd have "
                    "dedicated capacity. Let me show you a cached example."
                ),
                "APIConnectionError": (
                    "Looks like the WiFi hiccup we all love at conferences. "
                    "I have an offline version ready."
                ),
            }

            message = friendly_messages.get(
                error_type,
                f"Hit a small bump -- {error_type}. Let me work around this."
            )
            st.warning(message)
            return None

    def _switch_to_recording(self):
        """Switch to a pre-recorded demo flow."""
        st.info("Switching to pre-recorded demonstration...")
        return {"mode": "recording", "available": True}


# Usage in a demo
guard = DemoGuard()

def demo_with_guard():
    st.title("Resilient Demo")

    query = st.text_input("Enter your query:")
    if query:
        with st.spinner("Processing..."):
            result = guard.safe_api_call(
                lambda q: f"AI response to: {q}",  # Replace with real API call
                query,
            )
            if result:
                st.success("Response received!")
                st.write(result)
```

### Timing and Pacing

```python
# demo_timer.py
"""Utilities for managing demo timing."""

import time
from contextlib import contextmanager
import streamlit as st


@contextmanager
def timed_section(name: str, expected_seconds: float = 5.0):
    """Track and display timing for demo sections.

    Shows the audience that your solution is fast -- or gives you
    an excuse to fill time if it is slow.
    """
    start = time.time()
    yield
    elapsed = time.time() - start

    if elapsed < expected_seconds:
        st.caption(f"{name} completed in {elapsed:.1f}s")
    else:
        st.caption(
            f"{name} took {elapsed:.1f}s "
            f"(demo environment -- production is typically {expected_seconds:.0f}x faster)"
        )


# Usage
def demo_with_timing():
    query = "Analyze this customer feedback"

    with timed_section("AI Analysis", expected_seconds=3.0):
        # API call here
        time.sleep(2)  # Simulated
        st.write("Analysis complete.")

    with timed_section("RAG Retrieval", expected_seconds=1.0):
        # Vector search here
        time.sleep(0.5)  # Simulated
        st.write("Retrieved 5 relevant documents.")
```

> **Swift Developer Note:** In iOS development, you might use `os_signpost` or
> Instruments to measure performance. The demo timing pattern above serves a similar
> purpose but is audience-facing -- it builds confidence in your solution's performance
> rather than being a debugging tool.

---

## 7. Customer Handoff

### Transitioning from Demo to Production

The demo worked. The customer is excited. Now what? The handoff phase is where many deals
stall because the gap between "impressive demo" and "production deployment" feels too
large. Your job as a solutions engineer is to make that gap feel manageable.

### Documentation Requirements

Every POC handoff needs these documents:

```python
# handoff_generator.py
"""Generate handoff documentation for customer POCs."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class HandoffPackage:
    """Everything needed for a clean customer handoff."""

    customer_name: str
    poc_name: str
    se_name: str
    date: str = ""

    def __post_init__(self):
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d")

    def generate_architecture_doc(self) -> str:
        return f"""# {self.poc_name} -- Architecture Overview

## For: {self.customer_name}
## Date: {self.date}
## Solutions Engineer: {self.se_name}

---

## System Architecture

### Components
1. **Frontend**: Streamlit web application
2. **AI Layer**: Claude API (Anthropic)
3. **Data Layer**: [Describe data storage approach]
4. **Integration Points**: [List external systems]

### Data Flow
1. User submits query via web interface
2. Application constructs prompt with relevant context
3. Prompt sent to Claude API
4. Response parsed and displayed to user
5. Conversation history maintained in session state

### API Usage
- **Model**: claude-sonnet-4-20250514
- **Estimated tokens per request**: ~2,000 input, ~500 output
- **Expected daily volume**: [Based on customer estimates]
- **Estimated monthly cost**: [Calculate based on volume]

---

## Moving to Production

### What Changes from POC to Production
| POC | Production |
|-----|------------|
| Streamlit UI | Customer's existing frontend |
| Session state (in-memory) | Database persistence |
| Single-user | Multi-user with auth |
| env var API key | Secret manager (AWS/GCP/Azure) |
| No monitoring | Full observability stack |
| Demo data | Customer's actual data pipeline |

### Recommended Next Steps
1. **Week 1-2**: API integration into existing backend
2. **Week 3-4**: Data pipeline setup and prompt tuning
3. **Week 5-6**: Testing, evaluation, and iteration
4. **Week 7-8**: Monitoring, scaling, and launch
"""

    def generate_prompt_catalog(self) -> str:
        return f"""# {self.poc_name} -- Prompt Catalog

## For: {self.customer_name}

This document catalogs all prompts used in the POC.
Each prompt has been tested and tuned during the demo phase.

---

### Prompt 1: [Use Case Name]

**Purpose**: [What this prompt does]

**System Prompt**:
```
[The actual system prompt text]
```

**User Prompt Template**:
```
[Template with {{variable}} placeholders]
```

**Tuning Notes**:
- [Why specific phrasing was chosen]
- [Edge cases that required prompt adjustments]
- [Performance characteristics]

**Evaluation Results**:
- Accuracy: [X]%
- Average latency: [X]ms
- Token usage: ~[X] input, ~[X] output
"""

    def generate_runbook(self) -> str:
        return f"""# {self.poc_name} -- Runbook

## Setup

### Prerequisites
- Python 3.11+
- Anthropic API key
- [Other dependencies]

### Installation
```bash
git clone [repo-url]
cd {self.poc_name.lower().replace(' ', '-')}
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
```

### Running
```bash
streamlit run app.py
```

### Configuration
All tunable parameters are in `config.py`.
See inline comments for guidance on each setting.

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| 500 errors | API key invalid | Check .env file |
| Slow responses | Model overloaded | Reduce max_tokens or switch to Haiku |
| Incorrect outputs | Prompt needs tuning | Edit prompts.py |
| Rate limiting | Too many requests | Add request queuing |
"""


# Usage
handoff = HandoffPackage(
    customer_name="Acme Corp",
    poc_name="AI Support Assistant",
    se_name="Daniel",
)

print(handoff.generate_architecture_doc())
```

### Code Handoff Best Practices

```python
# Code handoff checklist
handoff_checklist = {
    "code_quality": [
        "Remove all hardcoded secrets and API keys",
        "Replace print() with proper logging",
        "Add docstrings to all public functions",
        "Include type hints on function signatures",
        "Remove dead code and commented-out experiments",
    ],
    "repository": [
        "Clean git history (squash WIP commits)",
        "Comprehensive .gitignore (include .env, __pycache__, .streamlit/)",
        "requirements.txt with pinned versions",
        "README with setup, running, and architecture overview",
        ".env.example with all required variables (no values)",
    ],
    "documentation": [
        "Architecture diagram (even a simple ASCII one)",
        "Prompt catalog with rationale for each prompt",
        "Known limitations and edge cases",
        "Cost estimates based on expected usage",
        "Recommended next steps for production",
    ],
    "demo_artifacts": [
        "Recording of the final demo (for internal reference)",
        "Demo script document (step-by-step walkthrough)",
        "Customer questions and answers log",
        "Follow-up action items with owners and dates",
    ],
}
```

### Follow-Up Planning

```python
# follow_up.py
"""Structure for post-demo follow-up."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class FollowUpPlan:
    """Structured follow-up after a customer demo."""

    customer: str
    demo_date: datetime
    attendees: list[str]
    key_questions: list[str] = field(default_factory=list)
    action_items: list[dict] = field(default_factory=list)
    next_meeting: datetime | None = None

    def add_action_item(self, description: str, owner: str, days_to_complete: int = 7):
        self.action_items.append({
            "description": description,
            "owner": owner,
            "due_date": (self.demo_date + timedelta(days=days_to_complete)).isoformat(),
            "status": "open",
        })

    def generate_follow_up_email(self) -> str:
        items_text = "\n".join(
            f"  - {item['description']} (Owner: {item['owner']}, "
            f"Due: {item['due_date']})"
            for item in self.action_items
        )

        return f"""Subject: Follow-up: AI Demo for {self.customer}

Hi team,

Thank you for your time during our demo on {self.demo_date.strftime('%B %d, %Y')}.

Key Takeaways:
{chr(10).join(f'  - {q}' for q in self.key_questions)}

Action Items:
{items_text}

Next Steps:
{'  - Next meeting: ' + self.next_meeting.strftime('%B %d, %Y') if self.next_meeting else '  - To be scheduled'}

Please don't hesitate to reach out with any questions.

Best regards"""


# Example usage
plan = FollowUpPlan(
    customer="Acme Corp",
    demo_date=datetime.now(),
    attendees=["CTO", "VP Engineering", "ML Lead"],
    key_questions=[
        "How does the system handle PII in customer data?",
        "What's the latency for real-time classification?",
        "Can we fine-tune the model on our historical data?",
    ],
)

plan.add_action_item("Share API documentation and rate limits", "SE Team", days_to_complete=2)
plan.add_action_item("Provide cost estimate for 10K requests/day", "SE Team", days_to_complete=5)
plan.add_action_item("Send sanitized dataset for POC testing", "Customer", days_to_complete=7)
plan.next_meeting = datetime.now() + timedelta(days=14)

print(plan.generate_follow_up_email())
```

---

## 8. Rapid Iteration Patterns

### Quick Feedback Loops

The key to effective demos is tight iteration. Build, show, get feedback, adjust -- all in
the same meeting if possible.

```python
# feature_flags.py
"""Feature flags for demo variants."""

from dataclasses import dataclass, field


@dataclass
class DemoFeatureFlags:
    """Toggle features on/off during a demo without code changes.

    This lets you adapt in real-time based on audience reactions:
    - Customer asks about RAG? Enable it live.
    - Customer doesn't care about streaming? Disable it.
    - Customer wants to see error handling? Toggle force_errors.
    """

    # Core features
    enable_streaming: bool = True
    enable_rag: bool = False
    enable_tool_use: bool = False
    enable_multimodal: bool = False

    # Model selection
    use_fast_model: bool = False  # Haiku for speed demos, Sonnet for quality

    # Demo modes
    show_prompt_debug: bool = False  # Show the actual prompts being sent
    show_token_usage: bool = True   # Display token counts and costs
    show_latency: bool = True       # Display response times
    force_errors: bool = False      # Intentionally trigger errors for recovery demo

    # Data
    use_customer_data: bool = False
    use_synthetic_data: bool = True

    def model_name(self) -> str:
        if self.use_fast_model:
            return "claude-3-haiku-20240307"
        return "claude-sonnet-4-20250514"

    def active_features(self) -> list[str]:
        """Return list of currently active feature names."""
        return [
            name for name, value in self.__dict__.items()
            if isinstance(value, bool) and value
        ]
```

### Integrating Feature Flags with Streamlit

```python
# flagged_demo.py
import streamlit as st
from dataclasses import fields

# Initialize feature flags in session state
if "flags" not in st.session_state:
    st.session_state.flags = DemoFeatureFlags()

flags = st.session_state.flags

# Sidebar: feature flag toggles
with st.sidebar:
    st.header("Demo Features")
    st.caption("Toggle features on/off during the demo")

    flags.enable_streaming = st.toggle("Streaming", value=flags.enable_streaming)
    flags.enable_rag = st.toggle("RAG", value=flags.enable_rag)
    flags.enable_tool_use = st.toggle("Tool Use", value=flags.enable_tool_use)
    flags.use_fast_model = st.toggle("Fast Model (Haiku)", value=flags.use_fast_model)

    st.divider()
    st.header("Debug")
    flags.show_prompt_debug = st.toggle("Show Prompts", value=flags.show_prompt_debug)
    flags.show_token_usage = st.toggle("Show Token Usage", value=flags.show_token_usage)

# Main demo area
st.title("Adaptive AI Demo")
st.caption(f"Using model: {flags.model_name()}")

query = st.text_input("Enter your query:")

if query:
    # Show debug info if enabled
    if flags.show_prompt_debug:
        with st.expander("Debug: Prompt Sent to API"):
            st.code(f"System: You are a helpful assistant\nUser: {query}")

    # Use appropriate model
    model = flags.model_name()

    # Conditionally apply RAG
    context = ""
    if flags.enable_rag:
        st.info("RAG is enabled -- retrieving relevant documents...")
        context = "[Retrieved context would appear here]"

    # Generate response (streaming or not)
    if flags.enable_streaming:
        st.write("Streaming response...")
        # ... streaming implementation
    else:
        st.write("Generating response...")
        # ... standard implementation

    # Show token usage if enabled
    if flags.show_token_usage:
        col1, col2, col3 = st.columns(3)
        col1.metric("Input Tokens", "256")
        col2.metric("Output Tokens", "128")
        col3.metric("Est. Cost", "$0.002")
```

### A/B Demo Variants

```python
# ab_variants.py
"""Run multiple variants of a demo side by side."""

import streamlit as st
import anthropic
import time

st.title("A/B Prompt Comparison")
st.write("Compare different approaches side by side to find the best one.")

client = anthropic.Anthropic()

# Define variants
variants = {
    "Variant A: Direct": {
        "system": "You are a helpful assistant.",
        "description": "Simple, direct system prompt",
    },
    "Variant B: Detailed": {
        "system": (
            "You are a senior customer support agent for a SaaS platform. "
            "You are empathetic, concise, and solution-oriented. "
            "Always acknowledge the customer's frustration before offering solutions. "
            "If you don't know the answer, say so and offer to escalate."
        ),
        "description": "Detailed system prompt with persona and instructions",
    },
    "Variant C: Few-Shot": {
        "system": (
            "You are a customer support agent. Here are examples of good responses:\n\n"
            "Customer: My payment failed.\n"
            "Agent: I'm sorry about the payment issue. Let me look into this. "
            "Could you tell me which payment method you used? In the meantime, "
            "I'll check our payment processor for any known issues.\n\n"
            "Follow this style in your responses."
        ),
        "description": "System prompt with few-shot examples",
    },
}

query = st.text_input(
    "Enter a customer query to test:",
    value="I've been waiting 3 weeks for my refund and nobody is responding to my emails.",
)

if st.button("Compare All Variants") and query:
    cols = st.columns(len(variants))

    for col, (name, config) in zip(cols, variants.items()):
        with col:
            st.subheader(name)
            st.caption(config["description"])

            start = time.time()
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                system=config["system"],
                messages=[{"role": "user", "content": query}],
            )
            elapsed = time.time() - start

            st.write(response.content[0].text)
            st.caption(
                f"Latency: {elapsed:.1f}s | "
                f"Tokens: {response.usage.input_tokens}+{response.usage.output_tokens}"
            )
```

### Collecting Feedback Systematically

```python
# feedback_collector.py
"""Collect and store demo feedback for iteration."""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path


class FeedbackCollector:
    """Collect structured feedback during and after demos."""

    def __init__(self, storage_path: str = "feedback"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

    def render_inline_feedback(self, response_id: str, response_text: str):
        """Render feedback buttons next to an AI response.

        Use this during demos to quickly capture quality signals.
        """
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

        with col1:
            if st.button("Good", key=f"good_{response_id}"):
                self._save_feedback(response_id, "good", response_text)
                st.success("Noted!")

        with col2:
            if st.button("OK", key=f"ok_{response_id}"):
                self._save_feedback(response_id, "ok", response_text)
                st.info("Noted!")

        with col3:
            if st.button("Bad", key=f"bad_{response_id}"):
                self._save_feedback(response_id, "bad", response_text)
                st.warning("Noted -- will improve!")

    def render_session_summary(self):
        """Render an end-of-session feedback form."""
        st.subheader("Demo Feedback")

        overall = st.slider(
            "Overall demo quality (1-10):",
            min_value=1, max_value=10, value=7,
        )

        highlights = st.text_area(
            "What was most impressive?",
            placeholder="e.g., The speed of responses, the accuracy on our data...",
        )

        concerns = st.text_area(
            "What concerns do you have?",
            placeholder="e.g., How does it handle PII? What about hallucinations?",
        )

        missing = st.text_area(
            "What features are missing?",
            placeholder="e.g., Integration with our CRM, multi-language support...",
        )

        if st.button("Submit Feedback"):
            feedback = {
                "timestamp": datetime.now().isoformat(),
                "overall_score": overall,
                "highlights": highlights,
                "concerns": concerns,
                "missing_features": missing,
            }
            self._save_session_feedback(feedback)
            st.success("Thank you for your feedback!")

    def _save_feedback(self, response_id: str, rating: str, response_text: str):
        feedback = {
            "response_id": response_id,
            "rating": rating,
            "response_text": response_text[:500],  # Truncate for storage
            "timestamp": datetime.now().isoformat(),
        }
        file_path = self.storage_path / "inline_feedback.jsonl"
        with open(file_path, "a") as f:
            f.write(json.dumps(feedback) + "\n")

    def _save_session_feedback(self, feedback: dict):
        file_path = self.storage_path / "session_feedback.jsonl"
        with open(file_path, "a") as f:
            f.write(json.dumps(feedback) + "\n")
```

---

## 9. Complete Demo Application

### Putting It All Together

Here is a complete, production-quality demo application that incorporates all the patterns
from this module. This is the kind of application you would build for a real customer POC:

```python
# full_demo_app.py
"""
Complete AI Solutions Demo Application.

This app demonstrates a customer support AI assistant with:
- Streaming chat responses
- Document upload and Q&A
- Prompt debugging
- Response feedback collection
- Configurable model settings

Run: streamlit run full_demo_app.py
"""

import streamlit as st
import anthropic
import json
import time
from datetime import datetime
from pathlib import Path

# --- Configuration ---

st.set_page_config(
    page_title="AI Solutions Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODELS = {
    "Claude Sonnet (Balanced)": "claude-sonnet-4-20250514",
    "Claude Haiku (Fast)": "claude-3-haiku-20240307",
}

# --- Session State Initialization ---

if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = {"input": 0, "output": 0}
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = "chat"
if "document_context" not in st.session_state:
    st.session_state.document_context = None

# --- Sidebar Configuration ---

with st.sidebar:
    st.title("Demo Controls")

    # Model selection
    model_display = st.selectbox("Model", list(MODELS.keys()))
    model = MODELS[model_display]

    # Parameters
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max Tokens", 256, 4096, 1024, 256)

    st.divider()

    # Demo mode
    st.session_state.demo_mode = st.radio(
        "Demo Mode",
        ["chat", "document_qa", "comparison"],
    )

    st.divider()

    # Debug options
    show_debug = st.toggle("Show Debug Info", value=False)
    show_metrics = st.toggle("Show Metrics", value=True)

    st.divider()

    # Session stats
    if show_metrics:
        st.subheader("Session Metrics")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Input Tokens", f"{st.session_state.total_tokens['input']:,}")
        st.metric("Output Tokens", f"{st.session_state.total_tokens['output']:,}")

        total_cost = (
            st.session_state.total_tokens["input"] * 0.003 / 1000
            + st.session_state.total_tokens["output"] * 0.015 / 1000
        )
        st.metric("Est. Cost", f"${total_cost:.4f}")

    # Reset button
    if st.button("Reset Session"):
        st.session_state.messages = []
        st.session_state.total_tokens = {"input": 0, "output": 0}
        st.session_state.document_context = None
        st.rerun()


# --- Helper Functions ---

def get_client() -> anthropic.Anthropic:
    """Get or create the Anthropic client."""
    return anthropic.Anthropic()


def build_system_prompt() -> str:
    """Build the system prompt based on current demo configuration."""
    base = (
        "You are a helpful AI assistant demonstrating capabilities "
        "for enterprise customers. Be professional, accurate, and concise."
    )

    if st.session_state.document_context:
        base += (
            f"\n\nYou have access to the following document for reference:\n"
            f"---\n{st.session_state.document_context}\n---\n"
            f"Use this document to answer questions when relevant."
        )

    return base


# --- Main Content ---

st.title("AI Solutions Demo")

# Chat Mode
if st.session_state.demo_mode == "chat":
    st.caption(f"Using {model_display} | Temperature: {temperature}")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Show debug info
        if show_debug:
            with st.expander("Debug: API Request"):
                st.json({
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "system": build_system_prompt()[:200] + "...",
                    "messages_count": len(st.session_state.messages),
                })

        # Generate response with streaming
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                client = get_client()
                start_time = time.time()

                with client.messages.stream(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=build_system_prompt(),
                    messages=st.session_state.messages,
                ) as stream:
                    for text in stream.text_stream:
                        full_response += text
                        response_placeholder.markdown(full_response + "▌")

                elapsed = time.time() - start_time
                response_placeholder.markdown(full_response)

                # Update metrics
                final_message = stream.get_final_message()
                st.session_state.total_tokens["input"] += final_message.usage.input_tokens
                st.session_state.total_tokens["output"] += final_message.usage.output_tokens

                if show_debug:
                    st.caption(
                        f"Latency: {elapsed:.1f}s | "
                        f"Tokens: {final_message.usage.input_tokens}+"
                        f"{final_message.usage.output_tokens}"
                    )

            except Exception as e:
                full_response = (
                    f"I encountered an issue: {type(e).__name__}. "
                    f"In production, this would be handled by retry logic and fallbacks."
                )
                response_placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

# Document Q&A Mode
elif st.session_state.demo_mode == "document_qa":
    st.subheader("Document Q&A")

    uploaded = st.file_uploader("Upload a document", type=["txt", "md", "csv", "json"])

    if uploaded:
        content = uploaded.read().decode("utf-8")
        st.session_state.document_context = content

        with st.expander(f"Document: {uploaded.name}", expanded=False):
            st.code(content[:2000])
            if len(content) > 2000:
                st.caption(f"... and {len(content) - 2000:,} more characters")

        st.success(f"Document loaded: {len(content):,} characters")

    if st.session_state.document_context:
        question = st.text_input("Ask a question about the document:")

        if question:
            with st.spinner("Analyzing..."):
                client = get_client()
                response = client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=build_system_prompt(),
                    messages=[{"role": "user", "content": question}],
                )
                st.markdown(response.content[0].text)

# Comparison Mode
elif st.session_state.demo_mode == "comparison":
    st.subheader("Model Comparison")
    st.write("Compare responses from different models side by side.")

    comparison_query = st.text_input("Enter a query to compare:")

    if st.button("Compare") and comparison_query:
        col1, col2 = st.columns(2)

        for col, (name, model_id) in zip([col1, col2], MODELS.items()):
            with col:
                st.markdown(f"**{name}**")
                with st.spinner(f"Generating with {name}..."):
                    try:
                        client = get_client()
                        start = time.time()
                        response = client.messages.create(
                            model=model_id,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            messages=[
                                {"role": "user", "content": comparison_query}
                            ],
                        )
                        elapsed = time.time() - start
                        st.write(response.content[0].text)
                        st.caption(
                            f"Time: {elapsed:.1f}s | "
                            f"Tokens: {response.usage.output_tokens}"
                        )
                    except Exception as e:
                        st.error(f"Error: {type(e).__name__}")
```

---

## 10. Swift Comparison

### SwiftUI Previews vs Streamlit

| Concept | SwiftUI Previews | Streamlit |
|---------|-----------------|-----------|
| **Purpose** | Preview UI during development | Build interactive web demos |
| **Audience** | Developer (you) | Customer, stakeholder |
| **Update model** | Live reload in Xcode | Full script re-run on interaction |
| **State** | `@State`, `@Binding`, `@Observable` | `st.session_state` |
| **Layout** | `VStack`, `HStack`, `ZStack` | `st.columns()`, `st.sidebar` |
| **Deployment** | TestFlight / App Store | Streamlit Cloud / Docker |
| **Sharing** | TestFlight invite (hours to set up) | `share=True` in Gradio (instant) |

### Xcode Playgrounds vs Jupyter + Streamlit

```python
# In Swift Playgrounds, you might write:
#
# import PlaygroundSupport
# import SwiftUI
#
# struct ContentView: View {
#     @State private var text = ""
#     var body: some View {
#         VStack {
#             TextField("Enter text", text: $text)
#             Text("You typed: \(text)")
#         }
#     }
# }
#
# PlaygroundPage.current.setLiveView(ContentView())

# The Python equivalent with Streamlit:
import streamlit as st

text = st.text_input("Enter text")
st.write(f"You typed: {text}")

# That is it. Two lines vs ~15 lines, and it is a shareable web app.
```

> **Swift Developer Note:** The biggest mindset shift is that Python prototyping tools
> produce _shareable web applications_, not IDE previews. A Streamlit app runs in a
> browser, can be shared via URL, and requires no app installation. This is why Python
> dominates the demo/prototyping space in AI -- the time from idea to shareable link is
> measured in minutes, not days. TestFlight requires provisioning profiles, build
> processing, and invitation management. Gradio's `share=True` gives you a public URL
> in seconds.

### TestFlight vs Streamlit Cloud / Hugging Face Spaces

```python
# TestFlight deployment workflow:
testflight_steps = [
    "1. Archive build in Xcode",
    "2. Upload to App Store Connect",
    "3. Wait for processing (10-30 minutes)",
    "4. Add beta testers by email",
    "5. Testers install TestFlight app",
    "6. Testers download your build",
    "7. Total time: 30-60 minutes minimum",
]

# Streamlit Cloud deployment workflow:
streamlit_cloud_steps = [
    "1. Push code to GitHub",
    "2. Connect repo at share.streamlit.io",
    "3. App is live (2-3 minutes)",
    "4. Share URL -- no installation needed",
    "5. Total time: 5 minutes",
]

# Gradio sharing:
gradio_steps = [
    "1. Add share=True to demo.launch()",
    "2. Run the script",
    "3. Copy the public URL from terminal output",
    "4. Total time: 10 seconds",
]
```

### UIKit/SwiftUI Patterns in Streamlit

Several patterns translate directly from iOS development:

```python
# iOS: Navigation Controller pattern
# SwiftUI: NavigationStack with NavigationLink
# Streamlit: Multi-page apps with st.navigation

# iOS: TabBarController pattern
# SwiftUI: TabView
# Streamlit: st.tabs
import streamlit as st

tab1, tab2, tab3 = st.tabs(["Chat", "Documents", "Settings"])

with tab1:
    st.write("Chat interface here")
with tab2:
    st.write("Document upload here")
with tab3:
    st.write("Settings panel here")


# iOS: Alert / UIAlertController
# SwiftUI: .alert()
# Streamlit: st.warning(), st.error(), st.success(), st.info()
st.success("Operation completed successfully")  # Green
st.warning("This action cannot be undone")        # Yellow
st.error("Failed to connect to API")              # Red
st.info("Tip: You can also upload PDF files")     # Blue


# iOS: ActivityIndicator / ProgressView
# SwiftUI: ProgressView()
# Streamlit: st.spinner(), st.progress()
with st.spinner("Loading..."):
    import time
    time.sleep(2)
st.success("Done!")

progress = st.progress(0)
for i in range(100):
    progress.progress(i + 1)


# iOS: UserDefaults
# SwiftUI: @AppStorage
# Streamlit: st.session_state (per-session, not persistent)
if "user_preference" not in st.session_state:
    st.session_state.user_preference = "default"
```

---

## 11. Interview Focus

### Demo-Related SE Interview Questions

Solutions engineer interviews at AI companies frequently test your ability to build and
present demos. Here are common questions and how to approach them:

### Question 1: "Build a demo in 30 minutes"

Many SE interviews include a live coding exercise where you build a working demo.

```python
# Strategy: Have a template ready that you can adapt
# This template covers 90% of demo scenarios

import streamlit as st
import anthropic

st.title("Interview Demo")

client = anthropic.Anthropic()

# Step 1: Configuration (2 minutes)
with st.sidebar:
    model = st.selectbox("Model", ["claude-sonnet-4-20250514"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.5)

# Step 2: Input handling (3 minutes)
user_input = st.text_area("Input:", height=150)

# Step 3: Processing (5 minutes)
if st.button("Process") and user_input:
    with st.spinner("Processing..."):
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            temperature=temperature,
            messages=[{"role": "user", "content": user_input}],
        )
        st.write(response.content[0].text)

# Step 4: Polish (remaining time)
# Add error handling, loading states, example inputs
```

### Question 2: "How would you demo X to a non-technical audience?"

**Framework for answering:**

```python
demo_presentation_framework = {
    "step_1_context": (
        "Start with the problem, not the technology. "
        "'Your support team handles 10,000 tickets/day. "
        "What if AI could handle 60% of them instantly?'"
    ),
    "step_2_simple_demo": (
        "Show the simplest possible example. "
        "One input, one output, zero configuration. "
        "'I'll type a real customer question and show you the AI response.'"
    ),
    "step_3_their_data": (
        "Use their domain. "
        "'Here's what it looks like with a question about YOUR product.'"
    ),
    "step_4_scale": (
        "Show volume handling. "
        "'Now imagine this running on all 10,000 daily tickets. "
        "Here's what the dashboard looks like.'"
    ),
    "step_5_next_steps": (
        "End with concrete next steps. "
        "'We can have a POC running on your data within two weeks.'"
    ),
}
```

### Question 3: "Your demo breaks during a customer presentation. What do you do?"

```python
demo_recovery_strategies = {
    "stay_calm": (
        "Never apologize excessively. Say 'Let me show you an alternative approach' "
        "or 'This is actually a great opportunity to show our error handling.'"
    ),
    "have_fallbacks": (
        "Always have pre-recorded responses, screenshots, or a video backup. "
        "Switch smoothly: 'Let me show you a recording of this workflow "
        "while we troubleshoot.'"
    ),
    "turn_it_into_a_strength": (
        "If the error is network-related: 'This is exactly why our SDK has "
        "built-in retry logic and fallback handling.' "
        "If the error is API-related: 'In production, you'd have dedicated "
        "capacity and rate limits set for your volume.'"
    ),
    "know_your_offline_story": (
        "Be ready to whiteboard the architecture and walk through the flow "
        "verbally. A confident technical explanation can be more convincing "
        "than a working demo."
    ),
}
```

### Question 4: "Design a POC for [specific use case]"

```python
# Framework for POC design questions
def design_poc(use_case: str) -> dict:
    """Framework for answering POC design questions in interviews."""
    return {
        "clarifying_questions": [
            "Who is the end user? (internal team vs. customers)",
            "What is the current workflow? (what are we replacing/augmenting)",
            "What data is available? (structured, unstructured, volume)",
            "What does success look like? (metrics, qualitative)",
            "What is the timeline? (days, weeks, months)",
        ],
        "proposed_architecture": {
            "frontend": "Streamlit (fastest to build, sufficient for POC)",
            "ai_layer": "Claude API with structured prompts",
            "data": "Customer-provided sample + synthetic fallback",
            "evaluation": "Side-by-side comparison with current process",
        },
        "timeline": {
            "day_1": "Set up repo, build basic pipeline, test with sample data",
            "day_2": "Build Streamlit UI, integrate pipeline, add error handling",
            "day_3": "Polish, add fallbacks, rehearse demo, generate documentation",
        },
        "success_metrics": [
            "Qualitative: Customer says 'this solves our problem'",
            "Quantitative: AI response quality >= human baseline on sample data",
            "Technical: < 5s response time, handles edge cases gracefully",
        ],
        "risks_and_mitigations": [
            ("API latency", "Pre-cache common queries, show streaming"),
            ("Data quality", "Validate input, show error messages clearly"),
            ("Hallucination", "Add grounding with RAG, show confidence signals"),
            ("Scope creep", "Document what is in/out of scope upfront"),
        ],
    }
```

### Question 5: "Walk us through a demo you've built"

**Structure your answer using the STAR-D method (Situation, Task, Action, Result, Demo):**

```python
star_d_framework = {
    "situation": (
        "Describe the customer and their problem. "
        "'A financial services company was spending 200 engineer-hours/month "
        "on manual code review for compliance.'"
    ),
    "task": (
        "What were you asked to build? "
        "'I was asked to build a POC showing how AI could automate "
        "80% of their compliance checks.'"
    ),
    "action": (
        "How did you build it? Be specific about tools and decisions. "
        "'I built a Streamlit app with Claude that analyzed code diffs, "
        "checked against their compliance rules, and flagged violations. "
        "I used RAG to ground the model in their compliance documentation.'"
    ),
    "result": (
        "What happened? Use numbers. "
        "'The POC correctly identified 92% of known violations in their "
        "test suite, and the customer signed a contract within 3 weeks.'"
    ),
    "demo": (
        "Offer to show it. "
        "'I can walk you through the architecture on a whiteboard, "
        "or I have a sanitized version I can show you live.'"
    ),
}
```

### Technical Skills to Demonstrate in Interviews

```python
interview_skills_checklist = {
    "must_have": [
        "Build a Streamlit or Gradio app from scratch in < 30 minutes",
        "Integrate with at least one LLM API (Claude, OpenAI)",
        "Handle errors gracefully -- no stack traces visible to users",
        "Explain your design decisions clearly while coding",
        "Show awareness of production concerns (cost, latency, security)",
    ],
    "differentiators": [
        "Stream responses in real-time",
        "Add evaluation/comparison features (A/B prompts)",
        "Show cost tracking and token usage",
        "Implement RAG in the demo",
        "Handle file uploads and multi-modal inputs",
        "Create a polished, professional-looking interface",
    ],
    "red_flags_to_avoid": [
        "Hardcoding API keys in source code",
        "Ignoring error handling entirely",
        "Over-engineering (don't build auth for a 30-minute demo)",
        "Not narrating your thought process",
        "Getting stuck on styling instead of functionality",
    ],
}
```

---

## 12. Exercises

### Exercise 1: Build a Customer Support Demo (Beginner)

Build a Streamlit app that:
- Takes a customer support query as input
- Uses Claude to generate a response
- Shows the response with token usage metrics
- Includes 3 pre-built example queries

**Time target**: 20 minutes.

### Exercise 2: Build a Document Q&A System (Intermediate)

Build a Gradio app that:
- Accepts file uploads (TXT, CSV, JSON)
- Lets users ask questions about uploaded documents
- Displays answers with source context highlighted
- Supports multiple file uploads in a single session

**Time target**: 45 minutes.

### Exercise 3: Build a Full POC (Advanced)

Build a complete POC for a fictional customer "DataFlow Inc." that needs:
- AI-powered data classification (categorize incoming records)
- A comparison view showing AI vs rule-based classification
- Feature flags to toggle between models and approaches
- Pre-generated fallback responses for offline demos
- A feedback collection mechanism

Structure it with the POC architecture from Section 4. Include a README, config file,
and prompt catalog.

**Time target**: 2-3 hours.

### Exercise 4: Demo Presentation (Practice)

Record yourself giving a 10-minute demo of Exercise 3. Review the recording for:
- Dead air (silence > 3 seconds during API calls)
- Technical jargon that a product manager would not understand
- Missing narration of what you are doing and why
- Unclear next steps at the end

### Exercise 5: Failure Recovery (Advanced)

Modify your demo from Exercise 3 to:
- Intentionally trigger an API timeout (set timeout to 0.1 seconds)
- Gracefully recover with a cached response
- Show the recovery to the audience with a helpful message
- Switch to an offline mode if 3 consecutive failures occur

---

## Summary

Rapid prototyping is arguably the most important skill for a solutions engineer. The
ability to take a customer's problem, build a working demo in hours, and present it
compellingly is what separates successful SE teams from those that rely on slide decks.

**Key Takeaways:**

1. **Demos are sales tools**: Treat them with the same care you would give a customer-facing
   product, but build them with the speed of a hackathon project.

2. **Streamlit for full apps, Gradio for model demos**: Use Streamlit when you need multi-page
   navigation, session state, and dashboard-like layouts. Use Gradio when you need quick
   input/output demos with instant sharing.

3. **Architecture matters even in prototypes**: A well-structured POC with separate config,
   prompts, and pipeline files is easier to iterate on, hand off, and extend.

4. **Data makes or breaks your demo**: Invest time in realistic demo data. Synthetic data
   generation with LLMs is your secret weapon.

5. **Plan for failure**: Pre-cached fallbacks, graceful error messages, and offline
   alternatives are not paranoia -- they are professionalism.

6. **The handoff is part of the demo**: A demo without documentation, follow-up, and clear
   next steps is just entertainment. Make it actionable.

7. **Practice**: Run your demo three times before presenting. Test on the actual network
   and machine. Have a colleague try to break it.

---

## Further Reading

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Gradio Documentation](https://www.gradio.app/docs)
- [Hugging Face Spaces](https://huggingface.co/spaces)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Streamlit Gallery](https://streamlit.io/gallery) -- inspiration for demo designs
- [Gradio Demos](https://www.gradio.app/demos) -- example ML demo applications

---

*Next module: [07 - Technical Communication](../07-technical-communication/lesson.md)* -- Learn to write technical documentation, create architecture diagrams, and present technical concepts to diverse audiences.
