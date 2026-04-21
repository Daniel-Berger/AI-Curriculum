"""
Module 05: Structured Output with Pydantic - Solutions
======================================================
Complete solutions for all exercises with explanations.

Run this file to verify all solutions pass: `python solutions.py`
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from pydantic import TypeAdapter
from typing import Optional, Literal, Union
import json
import re


# =============================================================================
# SECTION 1: Defining Pydantic Models
# =============================================================================

# Exercise 1: Basic Model Definition
def create_movie_model():
    """Define and return a Pydantic model class called Movie."""

    class Movie(BaseModel):
        title: str
        year: int
        genre: str
        rating: Optional[float] = None
        director: Optional[str] = None

    return Movie
    # Note: This is similar to defining a Swift struct with Codable.
    # Optional fields default to None, like Swift's optional properties.


# Exercise 2: Model with Field Constraints
def create_review_model():
    """Define and return a Pydantic model with Field constraints."""

    class Review(BaseModel):
        product_name: str = Field(..., min_length=1, max_length=100)
        rating: int = Field(..., ge=1, le=5)
        review_text: str = Field(..., min_length=10)
        reviewer_name: str

    return Review
    # Note: Field(...) means the field is required (no default).
    # ge = greater or equal, le = less or equal.
    # Swift equivalent would be custom Codable init with validation logic.


# Exercise 3: Model with Custom Validator
def create_sentiment_model():
    """Define a model with a custom validator for sentiment normalization."""

    class SentimentResult(BaseModel):
        text: str
        sentiment: str
        score: float = Field(..., ge=-1.0, le=1.0)

        @field_validator("sentiment")
        @classmethod
        def normalize_sentiment(cls, v: str) -> str:
            v_clean = v.lower().strip()
            allowed = {"positive", "negative", "neutral"}
            if v_clean not in allowed:
                raise ValueError(f"Sentiment must be one of {allowed}, got '{v}'")
            return v_clean

    return SentimentResult
    # Note: field_validator runs automatically during model creation.
    # The @classmethod decorator is required in Pydantic v2.
    # This pattern is essential for LLM output -- models often return
    # "Positive" or "POSITIVE" instead of "positive".


# Exercise 4: Nested Models
def create_extraction_models():
    """Define nested Pydantic models for entity extraction."""

    class Entity(BaseModel):
        name: str
        entity_type: str
        confidence: float = Field(..., ge=0.0, le=1.0)

    class ExtractionResult(BaseModel):
        text: str
        entities: list[Entity] = Field(default_factory=list)
        language: str = "en"

    return Entity, ExtractionResult
    # Note: Nested models are like nested Codable structs in Swift.
    # default_factory=list creates a new empty list for each instance
    # (avoids the mutable default argument pitfall).


# =============================================================================
# SECTION 2: Parsing LLM Output
# =============================================================================

# Exercise 5: Parse JSON String into Model
class TaskItem(BaseModel):
    title: str
    priority: str = Field(..., description="high, medium, or low")
    done: bool = False


def parse_task_json(json_string: str) -> TaskItem:
    """Parse a JSON string into a TaskItem model."""
    return TaskItem.model_validate_json(json_string)
    # Note: model_validate_json is preferred over json.loads() + model_validate()
    # because it's faster (single pass) and handles encoding better.
    # Swift equivalent: JSONDecoder().decode(TaskItem.self, from: data)


# Exercise 6: Extract JSON from LLM Prose
class WeatherInfo(BaseModel):
    city: str
    temperature_f: float
    condition: str


def extract_and_parse_weather(llm_response: str) -> WeatherInfo:
    """Extract JSON from an LLM response and parse it."""
    text = llm_response.strip()

    # Try 1: Look for ```json ... ``` code blocks
    json_block = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if json_block:
        json_str = json_block.group(1).strip()
        return WeatherInfo.model_validate_json(json_str)

    # Try 2: Look for a JSON object { ... }
    json_obj = re.search(r'\{[\s\S]*\}', text)
    if json_obj:
        json_str = json_obj.group(0)
        return WeatherInfo.model_validate_json(json_str)

    # Try 3: Assume the whole response is JSON
    return WeatherInfo.model_validate_json(text)
    # Note: This cascading approach is essential in production.
    # LLMs are unpredictable -- sometimes they add explanatory text around JSON.
    # Always try the most structured format first (code blocks), then fall back.


# Exercise 7: Handle Validation Errors
class ProductInfo(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    in_stock: bool


def safe_parse_product(json_string: str) -> dict:
    """Attempt to parse JSON into ProductInfo with error handling."""
    try:
        data = ProductInfo.model_validate_json(json_string)
        return {"success": True, "data": data}
    except ValidationError as e:
        return {"success": False, "errors": e.errors()}
    except json.JSONDecodeError:
        return {"success": False, "errors": [{"msg": "Invalid JSON"}]}
    # Note: Always catch BOTH ValidationError and JSONDecodeError.
    # ValidationError = valid JSON but wrong structure/values.
    # JSONDecodeError = not even valid JSON.
    # In Swift, this is like catching DecodingError vs. generic Error.


# =============================================================================
# SECTION 3: Advanced Patterns
# =============================================================================

# Exercise 8: Discriminated Union
class AnswerResponse(BaseModel):
    response_type: Literal["answer"] = "answer"
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class ClarifyResponse(BaseModel):
    response_type: Literal["clarification"] = "clarification"
    question: str
    options: list[str]


class ErrorLLMResponse(BaseModel):
    response_type: Literal["error"] = "error"
    error_message: str


LLMResponse = Union[AnswerResponse, ClarifyResponse, ErrorLLMResponse]


def parse_llm_response(json_string: str) -> LLMResponse:
    """Parse JSON into the appropriate response type using discriminated union."""
    adapter = TypeAdapter(LLMResponse)
    return adapter.validate_json(json_string)
    # Note: TypeAdapter is the Pydantic v2 way to work with Union types.
    # It uses the Literal field (response_type) as a discriminator to pick
    # the correct model class. This is similar to Swift's enum with
    # associated values + CodingKeys for discriminated decoding.


# Exercise 9: Type Coercion Validator
def create_robust_metrics_model():
    """Define a model that handles messy LLM output with pre-validators."""

    class RobustMetrics(BaseModel):
        accuracy: float = Field(..., ge=0.0, le=1.0)
        count: int
        tags: list[str]

        @field_validator("accuracy", mode="before")
        @classmethod
        def parse_percentage(cls, v):
            """Convert '85%' to 0.85."""
            if isinstance(v, str) and v.strip().endswith("%"):
                return float(v.strip()[:-1]) / 100
            return v

        @field_validator("tags", mode="before")
        @classmethod
        def parse_csv_tags(cls, v):
            """Convert comma-separated string to list."""
            if isinstance(v, str):
                return [tag.strip() for tag in v.split(",")]
            return v

    return RobustMetrics
    # Note: mode="before" validators run BEFORE Pydantic's type coercion.
    # This is crucial for LLM output where numbers come as "85%" strings
    # or lists come as "a, b, c" strings. In Swift, you'd handle this in
    # init(from decoder:) with custom decoding logic.


# Exercise 10: Serialization Control
class UserProfile(BaseModel):
    username: str
    email: str
    bio: Optional[str] = None
    age: Optional[int] = None
    is_verified: bool = False


def serialize_profile(profile: UserProfile) -> dict:
    """Serialize a profile in three different ways."""
    return {
        "full": profile.model_dump(),
        "no_none": profile.model_dump(exclude_none=True),
        "public": profile.model_dump(include={"username", "bio", "is_verified"}),
    }
    # Note: model_dump() is the Pydantic v2 replacement for .dict().
    # exclude_none=True is perfect for API responses where you don't want nulls.
    # include={...} acts like a field-level allowlist.
    # Swift equivalent: custom CodingKeys or encode(to:) with conditional encoding.


# Exercise 11: Schema Generation
class RecipeSchema(BaseModel):
    name: str = Field(..., description="Name of the recipe")
    ingredients: list[str] = Field(..., description="List of ingredients")
    steps: list[str] = Field(..., description="Step-by-step instructions")
    prep_time_minutes: int = Field(..., ge=1, description="Prep time in minutes")
    difficulty: str = Field(..., description="easy, medium, or hard")


def get_schema_info(model_class: type[BaseModel]) -> dict:
    """Generate and analyze a JSON schema from a Pydantic model."""
    schema = model_class.model_json_schema()

    properties = schema.get("properties", {})
    required = sorted(schema.get("required", []))

    # Check if all fields have descriptions
    has_descriptions = all(
        "description" in prop_info
        for prop_info in properties.values()
    )

    return {
        "field_count": len(properties),
        "required_fields": required,
        "has_descriptions": has_descriptions,
        "schema_json": json.dumps(schema, indent=2),
    }
    # Note: model_json_schema() generates a JSON Schema (Draft 2020-12)
    # that can be passed directly to LLM APIs. This is how you tell
    # Claude or GPT exactly what structure to output. Always add descriptions
    # to fields -- they serve as mini-prompts for the LLM.


# Exercise 12: Complete Pipeline — Mock LLM Extraction
class ContactInfo(BaseModel):
    name: str = Field(..., min_length=1, description="Full name")
    email: Optional[str] = Field(None, description="Email if found")
    phone: Optional[str] = Field(None, description="Phone number if found")
    company: Optional[str] = Field(None, description="Company if mentioned")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and "@" not in v:
            raise ValueError("Email must contain @")
        return v


def extract_contacts_pipeline(texts: list[str]) -> dict:
    """Process texts and extract contact info using pattern matching."""
    successful = []
    failed = []

    for text in texts:
        try:
            if not text.strip():
                raise ValueError("Empty text, no contact info to extract")

            words = text.split()

            # Extract name: first two capitalized words
            cap_words = [w.strip(".,!?:;") for w in words if w[0:1].isupper()]
            name = " ".join(cap_words[:2]) if cap_words else ""

            if not name:
                raise ValueError("No name found in text")

            # Extract email: word containing '@'
            email = None
            for w in words:
                clean_w = w.strip(".,!?:;")
                if "@" in clean_w:
                    email = clean_w
                    break

            # Extract phone: word with digits and length >= 7
            phone = None
            for w in words:
                clean_w = w.strip(".,!?:;")
                if any(c.isdigit() for c in clean_w) and len(clean_w) >= 7:
                    phone = clean_w
                    break

            # Extract company: word(s) after "at" or "from"
            company = None
            words_lower = [w.lower().strip(".,!?:;") for w in words]
            for keyword in ["at", "from"]:
                if keyword in words_lower:
                    idx = words_lower.index(keyword)
                    if idx + 1 < len(words):
                        company = words[idx + 1].strip(".,!?:;")
                        break

            # Build and validate the ContactInfo
            contact = ContactInfo(
                name=name,
                email=email,
                phone=phone,
                company=company,
            )
            successful.append(contact)

        except (ValidationError, ValueError, IndexError) as e:
            failed.append({"text": text, "error": str(e)})

    total = len(texts)
    return {
        "successful": successful,
        "failed": failed,
        "total": total,
        "success_rate": len(successful) / total if total > 0 else 0.0,
    }
    # Note: In production, the "pattern matching" part would be replaced
    # by an actual LLM call (e.g., Claude with tool use or instructor).
    # The pipeline structure (iterate, parse, validate, collect errors)
    # remains the same. This pattern is extremely common in LLM apps.


# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Module 05: Structured Output with Pydantic - Solutions")
    print("=" * 60)
    errors = 0

    # Exercise 1
    try:
        Movie = create_movie_model()
        m = Movie(title="Inception", year=2010, genre="sci-fi")
        assert m.title == "Inception"
        assert m.year == 2010
        assert m.genre == "sci-fi"
        assert m.rating is None
        assert m.director is None
        m2 = Movie(title="Dune", year=2021, genre="sci-fi", rating=8.0, director="Denis Villeneuve")
        assert m2.rating == 8.0
        assert m2.director == "Denis Villeneuve"
        print("  Exercise 01 (create_movie_model):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 01 (create_movie_model):      FAIL - {e}")
        errors += 1

    # Exercise 2
    try:
        Review = create_review_model()
        r = Review(product_name="Widget", rating=5, review_text="This is a great product indeed!", reviewer_name="Alice")
        assert r.rating == 5
        try:
            Review(product_name="", rating=5, review_text="This is a great product!", reviewer_name="Bob")
            assert False, "Should have raised ValidationError for empty product_name"
        except ValidationError:
            pass
        try:
            Review(product_name="Widget", rating=6, review_text="This is a great product!", reviewer_name="Bob")
            assert False, "Should have raised ValidationError for rating > 5"
        except ValidationError:
            pass
        print("  Exercise 02 (create_review_model):     PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 02 (create_review_model):     FAIL - {e}")
        errors += 1

    # Exercise 3
    try:
        Sentiment = create_sentiment_model()
        s = Sentiment(text="Great!", sentiment="  POSITIVE  ", score=0.9)
        assert s.sentiment == "positive"
        s2 = Sentiment(text="Bad", sentiment="NEGATIVE", score=-0.8)
        assert s2.sentiment == "negative"
        try:
            Sentiment(text="Hmm", sentiment="UNKNOWN", score=0.5)
            assert False, "Should have raised ValidationError"
        except ValidationError:
            pass
        print("  Exercise 03 (create_sentiment_model):  PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 03 (create_sentiment_model):  FAIL - {e}")
        errors += 1

    # Exercise 4
    try:
        Entity, ExtractionResult = create_extraction_models()
        e = Entity(name="Apple", entity_type="organization", confidence=0.95)
        assert e.name == "Apple"
        result = ExtractionResult(text="Apple is great", entities=[e])
        assert len(result.entities) == 1
        assert result.language == "en"
        empty = ExtractionResult(text="Nothing here")
        assert len(empty.entities) == 0
        print("  Exercise 04 (create_extraction_models): PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 04 (create_extraction_models): FAIL - {e}")
        errors += 1

    # Exercise 5
    try:
        t = parse_task_json('{"title": "Buy milk", "priority": "high"}')
        assert isinstance(t, TaskItem)
        assert t.title == "Buy milk"
        assert t.priority == "high"
        assert t.done is False
        t2 = parse_task_json('{"title": "Deploy", "priority": "low", "done": true}')
        assert t2.done is True
        print("  Exercise 05 (parse_task_json):         PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 05 (parse_task_json):         FAIL - {e}")
        errors += 1

    # Exercise 6
    try:
        r1 = extract_and_parse_weather('{"city": "NYC", "temperature_f": 72.0, "condition": "sunny"}')
        assert r1.city == "NYC"
        r2 = extract_and_parse_weather('```json\n{"city": "LA", "temperature_f": 85.0, "condition": "clear"}\n```')
        assert r2.city == "LA"
        r3 = extract_and_parse_weather('Here is the weather: {"city": "Chicago", "temperature_f": 60.0, "condition": "cloudy"} Hope this helps!')
        assert r3.city == "Chicago"
        print("  Exercise 06 (extract_and_parse):       PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 06 (extract_and_parse):       FAIL - {e}")
        errors += 1

    # Exercise 7
    try:
        good = safe_parse_product('{"name": "Widget", "price": 9.99, "in_stock": true}')
        assert good["success"] is True
        assert good["data"].name == "Widget"
        bad = safe_parse_product('{"name": "", "price": -5, "in_stock": true}')
        assert bad["success"] is False
        assert len(bad["errors"]) >= 1
        malformed = safe_parse_product('not json at all')
        assert malformed["success"] is False
        assert malformed["errors"][0]["msg"] == "Invalid JSON"
        print("  Exercise 07 (safe_parse_product):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 07 (safe_parse_product):      FAIL - {e}")
        errors += 1

    # Exercise 8
    try:
        r1 = parse_llm_response('{"response_type": "answer", "answer": "Paris", "confidence": 0.95}')
        assert isinstance(r1, AnswerResponse)
        assert r1.answer == "Paris"
        r2 = parse_llm_response('{"response_type": "clarification", "question": "Which?", "options": ["A", "B"]}')
        assert isinstance(r2, ClarifyResponse)
        r3 = parse_llm_response('{"response_type": "error", "error_message": "Fail"}')
        assert isinstance(r3, ErrorLLMResponse)
        print("  Exercise 08 (parse_llm_response):      PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 08 (parse_llm_response):      FAIL - {e}")
        errors += 1

    # Exercise 9
    try:
        Metrics = create_robust_metrics_model()
        m = Metrics(accuracy="85%", count="10", tags="ml, ai, nlp")
        assert m.accuracy == 0.85
        assert m.count == 10
        assert m.tags == ["ml", "ai", "nlp"]
        m2 = Metrics(accuracy=0.92, count=5, tags=["a", "b"])
        assert m2.accuracy == 0.92
        assert m2.tags == ["a", "b"]
        print("  Exercise 09 (create_robust_metrics):   PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 09 (create_robust_metrics):   FAIL - {e}")
        errors += 1

    # Exercise 10
    try:
        p = UserProfile(username="alice", email="a@b.com", is_verified=True)
        result = serialize_profile(p)
        assert result["full"]["email"] == "a@b.com"
        assert result["full"]["bio"] is None
        assert "bio" not in result["no_none"]
        assert "email" not in result["public"]
        assert result["public"]["username"] == "alice"
        print("  Exercise 10 (serialize_profile):       PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 10 (serialize_profile):       FAIL - {e}")
        errors += 1

    # Exercise 11
    try:
        info = get_schema_info(RecipeSchema)
        assert info["field_count"] == 5
        assert info["required_fields"] == ["difficulty", "ingredients", "name", "prep_time_minutes", "steps"]
        assert info["has_descriptions"] is True
        assert isinstance(info["schema_json"], str)
        assert "name" in info["schema_json"]
        print("  Exercise 11 (get_schema_info):         PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 11 (get_schema_info):         FAIL - {e}")
        errors += 1

    # Exercise 12
    try:
        texts = [
            "John Smith works at TechCorp. Email: john@tech.com, Phone: 555-123-4567",
            "Jane Doe from StartupXYZ jane@startup.io",
            "",
        ]
        result = extract_contacts_pipeline(texts)
        assert result["total"] == 3
        assert len(result["successful"]) >= 2
        assert len(result["failed"]) >= 1
        assert 0 < result["success_rate"] <= 1.0
        for contact in result["successful"]:
            assert isinstance(contact, ContactInfo)
        print("  Exercise 12 (extract_contacts):        PASS")
    except (AssertionError, Exception) as e:
        print(f"  Exercise 12 (extract_contacts):        FAIL - {e}")
        errors += 1

    print(f"\n{'='*60}")
    if errors == 0:
        print("All exercises passed!")
    else:
        print(f"{errors} exercise(s) need attention.")
    print(f"{'='*60}")
