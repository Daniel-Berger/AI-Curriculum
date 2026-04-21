# Module 05: Structured Output with Pydantic

## Introduction for Swift Developers

If you've used `Codable` in Swift to decode JSON from network responses, you already
understand the core idea of structured output: forcing unstructured data into strongly
typed models. In the LLM world, structured output is even more critical because LLMs
generate free-form text by default. Without structure, you're left parsing fragile
strings with regex -- the software equivalent of building on sand.

Pydantic is Python's answer to Swift's `Codable`, but more powerful. It validates data
at runtime, coerces types, provides detailed error messages, and integrates seamlessly
with LLM APIs. This module teaches you to harness Pydantic to make LLM outputs
reliable, predictable, and production-ready.

---

## 1. Why Structured Output Matters

### The Problem with Raw LLM Output

LLMs generate text. When you ask Claude or GPT to "extract the person's name and age,"
you might get any of these:

```
"The person's name is Alice and she is 30 years old."
"Name: Alice\nAge: 30"
"{"name": "Alice", "age": 30}"
"Alice, 30"
```

Parsing these reliably is a nightmare. Structured output solves this by constraining
the LLM to produce a specific format -- typically JSON that matches a schema.

### Swift Analogy

Think of it like the difference between:

```swift
// Fragile: parsing a raw string
let response = "Alice, 30"
let parts = response.split(separator: ",")
// What if the format changes? What if there's no comma?

// Robust: using Codable
struct Person: Codable {
    let name: String
    let age: Int
}
let person = try JSONDecoder().decode(Person.self, from: data)
```

Pydantic gives you the same safety net in Python, plus validation, coercion, and
schema generation for LLM APIs.

---

## 2. Pydantic v2 Fundamentals

### BaseModel -- Your Codable Equivalent

```python
from pydantic import BaseModel, Field
from typing import Optional

class Person(BaseModel):
    """A person extracted from text."""
    name: str
    age: int
    email: Optional[str] = None
```

```swift
// Swift equivalent
struct Person: Codable {
    let name: String
    let age: Int
    let email: String?
}
```

### Creating Instances

```python
# From keyword arguments
person = Person(name="Alice", age=30)
print(person.name)   # "Alice"
print(person.age)    # 30
print(person.email)  # None

# From a dictionary
data = {"name": "Bob", "age": 25, "email": "bob@example.com"}
person = Person(**data)
# Or equivalently:
person = Person.model_validate(data)

# From JSON string
json_str = '{"name": "Charlie", "age": 35}'
person = Person.model_validate_json(json_str)
```

### Type Coercion

Pydantic v2 coerces types by default in "lax" mode:

```python
# String "30" is coerced to int 30
person = Person(name="Alice", age="30")
print(person.age)       # 30 (int, not str)
print(type(person.age)) # <class 'int'>
```

This is crucial for LLM output where numbers often arrive as strings.

### Strict Mode

If you want to disable coercion (like Swift's strict typing):

```python
from pydantic import ConfigDict

class StrictPerson(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    age: int

# This raises ValidationError -- no coercion allowed
try:
    StrictPerson(name="Alice", age="30")
except Exception as e:
    print(e)  # Input should be a valid integer
```

---

## 3. Field Validators and Constraints

### Field with Constraints

```python
from pydantic import BaseModel, Field

class MovieReview(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    rating: float = Field(..., ge=0.0, le=10.0)
    summary: str = Field(..., min_length=10, max_length=1000)
    year: int = Field(..., ge=1888, le=2030)  # 1888 = first movie ever

# Valid
review = MovieReview(
    title="Inception",
    rating=8.8,
    summary="A mind-bending thriller about dreams within dreams.",
    year=2010
)

# Invalid -- rating > 10
try:
    MovieReview(title="Bad", rating=15.0, summary="Too high rating", year=2020)
except Exception as e:
    print(e)  # Input should be less than or equal to 10
```

### Field Descriptions for LLM Schema

The `description` parameter in `Field` is critical for LLMs -- it guides the model
on what to put in each field:

```python
class ExtractedEntity(BaseModel):
    name: str = Field(
        ...,
        description="The full name of the person or organization"
    )
    entity_type: str = Field(
        ...,
        description="Either 'person' or 'organization'"
    )
    confidence: float = Field(
        ...,
        ge=0.0, le=1.0,
        description="Confidence score from 0.0 to 1.0"
    )
```

### Custom Validators

```python
from pydantic import BaseModel, field_validator

class SentimentResult(BaseModel):
    text: str
    sentiment: str
    score: float

    @field_validator("sentiment")
    @classmethod
    def validate_sentiment(cls, v: str) -> str:
        allowed = {"positive", "negative", "neutral"}
        v_lower = v.lower().strip()
        if v_lower not in allowed:
            raise ValueError(f"Sentiment must be one of {allowed}, got '{v}'")
        return v_lower

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not -1.0 <= v <= 1.0:
            raise ValueError(f"Score must be between -1.0 and 1.0, got {v}")
        return round(v, 4)
```

### Model Validators (Cross-Field Validation)

```python
from pydantic import model_validator

class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode="after")
    def validate_date_order(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before end_date")
        return self
```

---

## 4. Nested Models for Complex Output

Real LLM tasks produce complex, nested structures. Pydantic handles this naturally.

### Example: Structured Article Analysis

```python
from pydantic import BaseModel, Field
from typing import Optional

class Author(BaseModel):
    name: str
    affiliation: Optional[str] = None

class KeyPoint(BaseModel):
    summary: str = Field(..., description="One-sentence summary of the key point")
    supporting_evidence: str = Field(..., description="Quote or data supporting this point")
    importance: str = Field(..., description="'high', 'medium', or 'low'")

class ArticleAnalysis(BaseModel):
    title: str
    authors: list[Author]
    publication_date: Optional[str] = None
    key_points: list[KeyPoint] = Field(
        ..., min_length=1, max_length=10,
        description="The main arguments or findings"
    )
    summary: str = Field(
        ..., min_length=50,
        description="A comprehensive summary in 2-3 sentences"
    )
    topics: list[str] = Field(
        ..., min_length=1,
        description="List of topic tags"
    )
```

### Generating JSON Schema for LLMs

```python
import json

schema = ArticleAnalysis.model_json_schema()
print(json.dumps(schema, indent=2))
```

This schema can be passed directly to LLM APIs to constrain output format.

---

## 5. JSON Mode with Claude

### Using Claude's API with Structured Output

```python
import anthropic
from pydantic import BaseModel, Field
import json

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var

class ExtractedContact(BaseModel):
    name: str = Field(..., description="Full name of the contact")
    phone: str | None = Field(None, description="Phone number if mentioned")
    email: str | None = Field(None, description="Email address if mentioned")
    company: str | None = Field(None, description="Company name if mentioned")

def extract_contact(text: str) -> ExtractedContact:
    """Extract contact information from unstructured text."""

    # Generate JSON schema from the Pydantic model
    schema = ExtractedContact.model_json_schema()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Extract contact information from this text.
Respond with ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Text: {text}"""
            }
        ]
    )

    # Parse the response into our Pydantic model
    response_text = message.content[0].text
    return ExtractedContact.model_validate_json(response_text)

# Usage
text = "Hi, I'm Sarah Chen from TechCorp. Reach me at sarah@techcorp.com or 555-0123."
contact = extract_contact(text)
print(contact.model_dump())
# {'name': 'Sarah Chen', 'phone': '555-0123', 'email': 'sarah@techcorp.com', 'company': 'TechCorp'}
```

### Claude's Tool Use for Guaranteed Structure

Claude's tool use feature provides more reliable structured output than JSON mode:

```python
import anthropic
import json
from pydantic import BaseModel, Field

class SentimentAnalysis(BaseModel):
    sentiment: str = Field(..., description="positive, negative, or neutral")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Brief explanation of the sentiment")

def analyze_sentiment(text: str) -> SentimentAnalysis:
    client = anthropic.Anthropic()

    # Convert Pydantic schema to Claude tool format
    tool = {
        "name": "record_sentiment",
        "description": "Record the sentiment analysis result",
        "input_schema": SentimentAnalysis.model_json_schema()
    }

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=[tool],
        tool_choice={"type": "tool", "name": "record_sentiment"},
        messages=[
            {
                "role": "user",
                "content": f"Analyze the sentiment of this text: {text}"
            }
        ]
    )

    # Extract tool use result
    tool_use = next(
        block for block in message.content
        if block.type == "tool_use"
    )

    return SentimentAnalysis.model_validate(tool_use.input)
```

---

## 6. JSON Mode with OpenAI

### Using response_format

```python
from openai import OpenAI
from pydantic import BaseModel
import json

client = OpenAI()  # uses OPENAI_API_KEY env var

class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    steps: list[str]
    prep_time_minutes: int
    difficulty: str

def generate_recipe(dish: str) -> Recipe:
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": f"Generate a recipe. Respond with JSON matching: "
                           f"{json.dumps(Recipe.model_json_schema())}"
            },
            {"role": "user", "content": f"Give me a recipe for {dish}"}
        ]
    )

    return Recipe.model_validate_json(response.choices[0].message.content)
```

### OpenAI Structured Outputs (Newer API)

OpenAI also supports schema-constrained generation natively:

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class MathSolution(BaseModel):
    steps: list[str]
    answer: float

response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Solve the math problem step by step."},
        {"role": "user", "content": "What is 25% of 340?"}
    ],
    response_format=MathSolution,
)

result = response.choices[0].message.parsed
print(result.steps)   # ['25% of 340 = 0.25 * 340', '0.25 * 340 = 85']
print(result.answer)  # 85.0
```

---

## 7. The Instructor Library

The `instructor` library wraps LLM clients to add automatic structured output,
validation, and retry logic. It's the most production-ready approach.

### Basic Usage

```python
import instructor
from anthropic import Anthropic
from pydantic import BaseModel, Field

# Patch the client
client = instructor.from_anthropic(Anthropic())

class UserInfo(BaseModel):
    name: str
    age: int = Field(..., ge=0, le=150)
    occupation: str

# Now you get Pydantic models directly
user = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    response_model=UserInfo,
    messages=[
        {
            "role": "user",
            "content": "Extract: John is a 28-year-old software engineer."
        }
    ]
)

print(user)  # name='John' age=28 occupation='software engineer'
```

### With OpenAI

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel

client = instructor.from_openai(OpenAI())

class Extraction(BaseModel):
    names: list[str]
    locations: list[str]
    dates: list[str]

result = client.chat.completions.create(
    model="gpt-4o",
    response_model=Extraction,
    messages=[
        {
            "role": "user",
            "content": "Alice went to Paris on January 5th. Bob visited Tokyo in March."
        }
    ]
)

print(result.names)      # ['Alice', 'Bob']
print(result.locations)  # ['Paris', 'Tokyo']
print(result.dates)      # ['January 5th', 'March']
```

### Retry Logic with Instructor

Instructor can automatically retry when validation fails:

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel, field_validator

client = instructor.from_openai(OpenAI())

class ValidatedAnswer(BaseModel):
    answer: str
    confidence: float

    @field_validator("confidence")
    @classmethod
    def check_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v

# max_retries tells instructor to re-prompt if validation fails
result = client.chat.completions.create(
    model="gpt-4o",
    response_model=ValidatedAnswer,
    max_retries=3,  # Will retry up to 3 times on validation failure
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
```

---

## 8. Handling Parsing Errors Gracefully

LLM output parsing can fail. You need robust error handling.

### Catching Validation Errors

```python
from pydantic import BaseModel, ValidationError
import json

class TaskResult(BaseModel):
    task: str
    status: str
    priority: int

def safe_parse(raw_json: str) -> TaskResult | dict:
    """Attempt to parse LLM output, with fallback."""
    try:
        return TaskResult.model_validate_json(raw_json)
    except ValidationError as e:
        print(f"Validation failed: {e.error_count()} errors")
        for error in e.errors():
            print(f"  - {error['loc']}: {error['msg']}")
        return {"raw": raw_json, "error": str(e)}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return {"raw": raw_json, "error": f"JSON decode error: {e}"}

# Test with invalid data
result = safe_parse('{"task": "deploy", "status": "done", "priority": "high"}')
# Validation failed: 1 errors
#   - ('priority',): Input should be a valid integer
```

### Extracting JSON from LLM Prose

Sometimes the LLM wraps JSON in explanation text or markdown:

```python
import re
import json
from pydantic import BaseModel

def extract_json_from_response(response: str) -> str:
    """Extract JSON from an LLM response that may contain markdown or prose."""

    # Try 1: Look for ```json code blocks
    json_block = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
    if json_block:
        return json_block.group(1).strip()

    # Try 2: Look for JSON object pattern
    json_obj = re.search(r'\{[\s\S]*\}', response)
    if json_obj:
        return json_obj.group(0)

    # Try 3: Look for JSON array pattern
    json_arr = re.search(r'\[[\s\S]*\]', response)
    if json_arr:
        return json_arr.group(0)

    # Fallback: return as-is and let the parser handle it
    return response

def robust_parse(response: str, model_class: type[BaseModel]):
    """Parse LLM response into a Pydantic model with JSON extraction."""
    json_str = extract_json_from_response(response)
    return model_class.model_validate_json(json_str)

# Example: LLM wrapped JSON in markdown
llm_response = """
Here's the analysis:

```json
{"sentiment": "positive", "score": 0.85}
```

Hope that helps!
"""

class Sentiment(BaseModel):
    sentiment: str
    score: float

result = robust_parse(llm_response, Sentiment)
print(result)  # sentiment='positive' score=0.85
```

---

## 9. Serialization

### model_dump and model_dump_json

```python
from pydantic import BaseModel
from typing import Optional

class APIResponse(BaseModel):
    query: str
    results: list[str]
    total: int
    next_page: Optional[str] = None

response = APIResponse(
    query="python tutorials",
    results=["intro", "advanced", "async"],
    total=3
)

# To dictionary
d = response.model_dump()
print(d)
# {'query': 'python tutorials', 'results': ['intro', 'advanced', 'async'],
#  'total': 3, 'next_page': None}

# Exclude None values (common for API responses)
d_clean = response.model_dump(exclude_none=True)
print(d_clean)
# {'query': 'python tutorials', 'results': ['intro', 'advanced', 'async'], 'total': 3}

# To JSON string
json_str = response.model_dump_json(indent=2)
print(json_str)

# Include/exclude specific fields
d_partial = response.model_dump(include={"query", "total"})
print(d_partial)  # {'query': 'python tutorials', 'total': 3}
```

### Comparison with Swift

```swift
// Swift Codable serialization
let encoder = JSONEncoder()
encoder.outputFormatting = .prettyPrinted
let data = try encoder.encode(response)
let jsonString = String(data: data, encoding: .utf8)!
```

In Python with Pydantic, it's just `response.model_dump_json(indent=2)` -- no encoder
configuration needed.

---

## 10. Discriminated Unions for Varied Outputs

When an LLM might return different types of responses, use discriminated unions:

```python
from pydantic import BaseModel, Field
from typing import Literal, Union

class SuccessResponse(BaseModel):
    status: Literal["success"] = "success"
    data: str
    confidence: float

class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    error_message: str
    error_code: int

class ClarificationResponse(BaseModel):
    status: Literal["clarification_needed"] = "clarification_needed"
    question: str
    options: list[str]

# Discriminated union -- Pydantic uses the 'status' field to pick the right model
LLMResponse = Union[SuccessResponse, ErrorResponse, ClarificationResponse]

from pydantic import TypeAdapter

adapter = TypeAdapter(LLMResponse)

# Parse different response types
success = adapter.validate_json('{"status": "success", "data": "Paris", "confidence": 0.95}')
print(type(success))  # <class 'SuccessResponse'>

error = adapter.validate_json('{"status": "error", "error_message": "Unknown", "error_code": 404}')
print(type(error))  # <class 'ErrorResponse'>

clarify = adapter.validate_json(
    '{"status": "clarification_needed", "question": "Which Paris?", "options": ["France", "Texas"]}'
)
print(type(clarify))  # <class 'ClarificationResponse'>
```

### Swift Comparison

This is similar to Swift enums with associated values:

```swift
enum LLMResponse: Codable {
    case success(data: String, confidence: Double)
    case error(message: String, code: Int)
    case clarificationNeeded(question: String, options: [String])
}
```

---

## 11. Practical Example: Entity Extraction Pipeline

Here's a complete, production-style example:

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import json

# --- Models ---

class Entity(BaseModel):
    text: str = Field(..., description="The entity text as it appears in the source")
    entity_type: str = Field(..., description="Type: person, organization, location, date, money")
    normalized: Optional[str] = Field(None, description="Normalized form, e.g., full name or ISO date")
    confidence: float = Field(..., ge=0.0, le=1.0)

    @field_validator("entity_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {"person", "organization", "location", "date", "money"}
        v_lower = v.lower()
        if v_lower not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v_lower

class ExtractionResult(BaseModel):
    entities: list[Entity] = Field(default_factory=list)
    raw_text: str
    entity_count: int = 0

    @property
    def persons(self) -> list[Entity]:
        return [e for e in self.entities if e.entity_type == "person"]

    @property
    def organizations(self) -> list[Entity]:
        return [e for e in self.entities if e.entity_type == "organization"]

# --- Mock extraction (no API key needed) ---

def mock_extract_entities(text: str) -> ExtractionResult:
    """Simulate LLM entity extraction for demonstration."""
    # In production, this would call Claude/OpenAI with the schema
    mock_response = {
        "entities": [
            {"text": "Apple", "entity_type": "organization", "normalized": "Apple Inc.", "confidence": 0.95},
            {"text": "Tim Cook", "entity_type": "person", "normalized": "Timothy Donald Cook", "confidence": 0.98},
            {"text": "$3 trillion", "entity_type": "money", "normalized": "3000000000000", "confidence": 0.90}
        ],
        "raw_text": text,
        "entity_count": 3
    }
    return ExtractionResult.model_validate(mock_response)

# Usage
result = mock_extract_entities("Apple CEO Tim Cook announced the company reached $3 trillion.")
print(f"Found {result.entity_count} entities")
for entity in result.entities:
    print(f"  {entity.entity_type}: {entity.text} (confidence: {entity.confidence})")
print(f"Persons: {[e.text for e in result.persons]}")
```

---

## 12. Validation and Retry Pattern

A production pattern for parsing LLM output with retries:

```python
from pydantic import BaseModel, ValidationError
import json
import time

class ParsedOutput(BaseModel):
    answer: str
    reasoning: str
    confidence: float

def parse_with_retry(
    llm_call_fn,  # Function that calls the LLM and returns raw text
    model_class: type[BaseModel],
    max_retries: int = 3,
    delay: float = 1.0
) -> BaseModel | None:
    """Parse LLM output with validation and retry."""
    errors = []

    for attempt in range(max_retries):
        try:
            raw = llm_call_fn()

            # Try to extract JSON from the response
            json_str = raw.strip()
            if json_str.startswith("```"):
                # Strip markdown code fences
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                json_str = json_str.strip()

            result = model_class.model_validate_json(json_str)
            return result

        except (ValidationError, json.JSONDecodeError) as e:
            errors.append(f"Attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)

    print(f"All {max_retries} attempts failed:")
    for err in errors:
        print(f"  {err}")
    return None
```

---

## 13. Type Coercion for LLM Output

LLMs often return data in unexpected formats. Pydantic's coercion helps:

```python
from pydantic import BaseModel, field_validator

class LLMMetrics(BaseModel):
    accuracy: float
    count: int
    label: str
    tags: list[str]

    @field_validator("tags", mode="before")
    @classmethod
    def ensure_list(cls, v):
        """LLMs sometimes return a single string instead of a list."""
        if isinstance(v, str):
            # Try comma-separated parsing
            return [tag.strip() for tag in v.split(",")]
        return v

    @field_validator("accuracy", mode="before")
    @classmethod
    def parse_percentage(cls, v):
        """Handle '85%' format that LLMs sometimes produce."""
        if isinstance(v, str) and v.endswith("%"):
            return float(v[:-1]) / 100
        return v

# These all work despite messy LLM output
m1 = LLMMetrics(accuracy="85%", count="42", label="test", tags="ml, ai, python")
print(m1.accuracy)  # 0.85
print(m1.count)     # 42
print(m1.tags)      # ['ml', 'ai', 'python']

m2 = LLMMetrics(accuracy=0.85, count=42, label="test", tags=["ml", "ai"])
print(m2.accuracy)  # 0.85
```

---

## 14. Complete Workflow: Structured Q&A System

Putting it all together:

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import json

# --- Schema Definition ---

class Source(BaseModel):
    title: str
    url: Optional[str] = None
    relevance_score: float = Field(..., ge=0.0, le=1.0)

class QAResponse(BaseModel):
    question: str
    answer: str = Field(..., min_length=10)
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: list[Source] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(
        default_factory=list, max_length=3,
        description="Suggested follow-up questions"
    )

    @field_validator("confidence")
    @classmethod
    def bucket_confidence(cls, v: float) -> float:
        """Round confidence to 2 decimal places."""
        return round(v, 2)

# --- Building the prompt with schema ---

def build_qa_prompt(question: str) -> str:
    schema = QAResponse.model_json_schema()
    return f"""Answer the following question. Respond with JSON matching this schema:

{json.dumps(schema, indent=2)}

Question: {question}

Respond with ONLY the JSON, no additional text."""

# --- Mock usage ---

prompt = build_qa_prompt("What is retrieval-augmented generation?")
print(prompt[:200] + "...")

# Simulated LLM response
mock_json = json.dumps({
    "question": "What is retrieval-augmented generation?",
    "answer": "RAG is a technique that enhances LLM responses by retrieving relevant "
              "documents from a knowledge base and including them in the prompt context.",
    "confidence": 0.92,
    "sources": [
        {"title": "RAG Paper (Lewis et al.)", "url": "https://arxiv.org/abs/2005.11401",
         "relevance_score": 0.95}
    ],
    "follow_up_questions": [
        "How does RAG compare to fine-tuning?",
        "What vector databases work best for RAG?"
    ]
})

response = QAResponse.model_validate_json(mock_json)
print(f"\nAnswer: {response.answer[:80]}...")
print(f"Confidence: {response.confidence}")
print(f"Sources: {len(response.sources)}")
print(f"Follow-ups: {response.follow_up_questions}")
```

---

## 15. Best Practices and Common Patterns

### Schema Design for LLMs

1. **Use descriptive field names** -- LLMs use field names as hints
2. **Add descriptions to every field** -- Guides the LLM on expected format
3. **Set reasonable constraints** -- `min_length`, `max_length`, `ge`, `le`
4. **Use Optional for fields the LLM might not fill** -- Don't force hallucination
5. **Prefer enums/Literal for constrained choices** -- Reduces invalid output

### Error Handling Checklist

```python
# 1. Always catch ValidationError AND JSONDecodeError
# 2. Log the raw response for debugging
# 3. Have a fallback strategy (retry, default, or graceful degradation)
# 4. Use field_validator with mode="before" for type coercion
# 5. Consider partial parsing for long responses
```

### Performance Tips

```python
# 1. Reuse TypeAdapter instances (they cache validation logic)
from pydantic import TypeAdapter
adapter = TypeAdapter(MyModel)  # Create once
result = adapter.validate_json(data)  # Use many times

# 2. Use model_validate_json instead of json.loads + model_validate
#    (it's faster because it skips the intermediate dict)

# 3. Use exclude_none=True when serializing to reduce token count
output = model.model_dump(exclude_none=True)
```

---

## Key Takeaways

1. **Pydantic is your Codable for Python** -- with runtime validation and coercion
2. **Always define schemas as Pydantic models** -- not raw dicts
3. **Use `model_json_schema()` to generate schemas for LLM APIs**
4. **Handle parsing errors gracefully** -- LLMs are not deterministic
5. **The instructor library is the easiest path** to structured LLM output
6. **Field descriptions guide LLM output** -- treat them as mini-prompts
7. **Validation + retry is a core production pattern** -- plan for failure

---

## Further Reading

- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Instructor Library](https://python.useinstructor.com/)
- [Anthropic Tool Use Guide](https://docs.anthropic.com/en/docs/tool-use)
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
