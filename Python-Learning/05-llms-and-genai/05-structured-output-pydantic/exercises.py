"""
Module 05: Structured Output with Pydantic - Exercises
======================================================
Target audience: Swift developers learning Python + AI/ML.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- No API keys or external services required -- all exercises use mock data.

Difficulty levels:
  Easy   - Direct Pydantic model definition
  Medium - Requires validation, parsing, or error handling
  Hard   - Combines multiple concepts (nested models, retries, unions)
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from typing import Optional, Literal, Union
import json


# =============================================================================
# SECTION 1: Defining Pydantic Models
# =============================================================================

# Exercise 1: Basic Model Definition
# Difficulty: Easy
# Define a Pydantic model for a movie extracted by an LLM.
def create_movie_model():
    """Define and return a Pydantic model class called Movie with these fields:
    - title: str (required)
    - year: int (required)
    - genre: str (required)
    - rating: float (optional, default None)
    - director: str (optional, default None)

    The model should be created and returned by this function.

    >>> Movie = create_movie_model()
    >>> m = Movie(title="Inception", year=2010, genre="sci-fi")
    >>> m.title
    'Inception'
    >>> m.rating is None
    True
    """
    pass


# Exercise 2: Model with Field Constraints
# Difficulty: Easy
# Define a model with validation constraints using Field().
def create_review_model():
    """Define and return a Pydantic model class called Review with:
    - product_name: str (min_length=1, max_length=100)
    - rating: int (ge=1, le=5)
    - review_text: str (min_length=10)
    - reviewer_name: str (required)

    >>> Review = create_review_model()
    >>> r = Review(product_name="Widget", rating=5,
    ...            review_text="This is a great product!", reviewer_name="Alice")
    >>> r.rating
    5
    """
    pass


# Exercise 3: Model with Custom Validator
# Difficulty: Medium
# Define a model where a custom validator normalizes the sentiment field.
def create_sentiment_model():
    """Define and return a Pydantic model called SentimentResult with:
    - text: str (required)
    - sentiment: str (required) - must be "positive", "negative", or "neutral"
    - score: float (required, between -1.0 and 1.0)

    The sentiment field should have a field_validator that:
    1. Converts to lowercase
    2. Strips whitespace
    3. Raises ValueError if not one of the three allowed values

    >>> Sentiment = create_sentiment_model()
    >>> s = Sentiment(text="Great!", sentiment="  POSITIVE  ", score=0.9)
    >>> s.sentiment
    'positive'
    """
    pass


# Exercise 4: Nested Models
# Difficulty: Medium
# Define nested Pydantic models for a structured LLM extraction result.
def create_extraction_models():
    """Define and return a tuple of (Entity, ExtractionResult) model classes.

    Entity should have:
    - name: str (required)
    - entity_type: str (required) - "person", "place", or "organization"
    - confidence: float (ge=0.0, le=1.0)

    ExtractionResult should have:
    - text: str (required) - the original text
    - entities: list[Entity] (default empty list)
    - language: str (default "en")

    >>> Entity, ExtractionResult = create_extraction_models()
    >>> e = Entity(name="Apple", entity_type="organization", confidence=0.95)
    >>> result = ExtractionResult(text="Apple is great", entities=[e])
    >>> len(result.entities)
    1
    """
    pass


# =============================================================================
# SECTION 2: Parsing LLM Output
# =============================================================================

# Exercise 5: Parse JSON String into Model
# Difficulty: Easy
# Parse a JSON string (simulating LLM output) into a Pydantic model.
class TaskItem(BaseModel):
    title: str
    priority: str = Field(..., description="high, medium, or low")
    done: bool = False


def parse_task_json(json_string: str) -> TaskItem:
    """Parse a JSON string into a TaskItem model.

    >>> parse_task_json('{"title": "Buy milk", "priority": "high"}')
    TaskItem(title='Buy milk', priority='high', done=False)
    """
    pass


# Exercise 6: Extract JSON from LLM Prose
# Difficulty: Medium
# LLMs sometimes wrap JSON in markdown code blocks or explanatory text.
# Extract and parse the JSON.
class WeatherInfo(BaseModel):
    city: str
    temperature_f: float
    condition: str


def extract_and_parse_weather(llm_response: str) -> WeatherInfo:
    """Extract JSON from an LLM response that may contain markdown fences
    or surrounding prose, then parse it into a WeatherInfo model.

    Should handle these formats:
    1. Pure JSON: '{"city": "NYC", "temperature_f": 72.0, "condition": "sunny"}'
    2. Markdown-fenced:
       ```json
       {"city": "NYC", "temperature_f": 72.0, "condition": "sunny"}
       ```
    3. JSON embedded in prose:
       "Here is the weather: {"city": "NYC", ...} Hope that helps!"

    >>> response = '```json\\n{"city": "NYC", "temperature_f": 72.0, "condition": "sunny"}\\n```'
    >>> result = extract_and_parse_weather(response)
    >>> result.city
    'NYC'
    """
    pass


# Exercise 7: Handle Validation Errors
# Difficulty: Medium
# Gracefully handle cases where LLM output doesn't match the schema.
class ProductInfo(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    in_stock: bool


def safe_parse_product(json_string: str) -> dict:
    """Attempt to parse JSON into a ProductInfo model.

    Returns a dict with either:
    - {"success": True, "data": <ProductInfo instance>} on success
    - {"success": False, "errors": <list of error dicts from ValidationError>} on failure
    - {"success": False, "errors": [{"msg": "Invalid JSON"}]} if JSON is malformed

    >>> result = safe_parse_product('{"name": "Widget", "price": 9.99, "in_stock": true}')
    >>> result["success"]
    True
    >>> result["data"].name
    'Widget'

    >>> result = safe_parse_product('{"name": "", "price": -5, "in_stock": true}')
    >>> result["success"]
    False
    >>> len(result["errors"]) >= 1
    True
    """
    pass


# =============================================================================
# SECTION 3: Advanced Patterns
# =============================================================================

# Exercise 8: Discriminated Union
# Difficulty: Hard
# Parse LLM responses that could be one of several types.
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
    """Parse a JSON string into the appropriate response type using
    discriminated union based on the 'response_type' field.

    >>> r1 = parse_llm_response('{"response_type": "answer", "answer": "Paris", "confidence": 0.95}')
    >>> isinstance(r1, AnswerResponse)
    True

    >>> r2 = parse_llm_response('{"response_type": "clarification", "question": "Which Paris?", "options": ["France", "Texas"]}')
    >>> isinstance(r2, ClarifyResponse)
    True

    >>> r3 = parse_llm_response('{"response_type": "error", "error_message": "Cannot process"}')
    >>> isinstance(r3, ErrorLLMResponse)
    True
    """
    pass


# Exercise 9: Type Coercion Validator
# Difficulty: Medium
# Build a model that handles messy LLM output with pre-validators.
def create_robust_metrics_model():
    """Define and return a Pydantic model called RobustMetrics with:
    - accuracy: float (between 0.0 and 1.0)
    - count: int
    - tags: list[str]

    With these pre-validators (mode="before"):
    - accuracy: if the value is a string ending with '%', convert to decimal
      (e.g., "85%" -> 0.85)
    - tags: if the value is a comma-separated string, split into list
      (e.g., "ml, ai, nlp" -> ["ml", "ai", "nlp"])

    >>> Metrics = create_robust_metrics_model()
    >>> m = Metrics(accuracy="92%", count="10", tags="ml, ai, nlp")
    >>> m.accuracy
    0.92
    >>> m.tags
    ['ml', 'ai', 'nlp']
    >>> m.count
    10
    """
    pass


# Exercise 10: Serialization Control
# Difficulty: Easy
# Practice converting Pydantic models to dicts and JSON with various options.
class UserProfile(BaseModel):
    username: str
    email: str
    bio: Optional[str] = None
    age: Optional[int] = None
    is_verified: bool = False


def serialize_profile(profile: UserProfile) -> dict:
    """Return a dict with three serialization variants of the profile:

    - "full": model_dump() with all fields
    - "no_none": model_dump(exclude_none=True) - excludes fields that are None
    - "public": model_dump(include={"username", "bio", "is_verified"}) - only public fields

    >>> p = UserProfile(username="alice", email="a@b.com", is_verified=True)
    >>> result = serialize_profile(p)
    >>> result["full"]["email"]
    'a@b.com'
    >>> "email" not in result["public"]
    True
    >>> "bio" not in result["no_none"]
    True
    """
    pass


# Exercise 11: Schema Generation
# Difficulty: Medium
# Generate a JSON schema from a Pydantic model and verify its structure.
class RecipeSchema(BaseModel):
    name: str = Field(..., description="Name of the recipe")
    ingredients: list[str] = Field(..., description="List of ingredients")
    steps: list[str] = Field(..., description="Step-by-step instructions")
    prep_time_minutes: int = Field(..., ge=1, description="Prep time in minutes")
    difficulty: str = Field(..., description="easy, medium, or hard")


def get_schema_info(model_class: type[BaseModel]) -> dict:
    """Generate the JSON schema from the model and return a summary dict with:
    - "field_count": number of fields (top-level properties)
    - "required_fields": sorted list of required field names
    - "has_descriptions": True if ALL fields have descriptions
    - "schema_json": the full schema as a JSON string (indented)

    >>> info = get_schema_info(RecipeSchema)
    >>> info["field_count"]
    5
    >>> info["required_fields"]
    ['difficulty', 'ingredients', 'name', 'prep_time_minutes', 'steps']
    >>> info["has_descriptions"]
    True
    """
    pass


# Exercise 12: Complete Pipeline — Mock LLM Extraction
# Difficulty: Hard
# Simulate a full structured output pipeline: define schema, "call LLM",
# parse output, validate, and handle errors.
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
    """Process a list of text strings, attempting to extract contact info from each.

    For this exercise, simulate LLM output by looking for patterns in the text:
    - Name: first two capitalized words (or first capitalized word)
    - Email: word containing '@'
    - Phone: word matching pattern of digits/dashes (contains digit and has len >= 7)
    - Company: word(s) after "at" or "from" (if present)

    Return a dict with:
    - "successful": list of ContactInfo objects that parsed successfully
    - "failed": list of dicts with {"text": original_text, "error": error_message}
    - "total": total number of texts processed
    - "success_rate": float (successful / total)

    >>> texts = [
    ...     "John Smith works at TechCorp. Email: john@tech.com, Phone: 555-123-4567",
    ...     "Jane Doe from StartupXYZ jane@startup.io",
    ...     "",  # This should fail (no name found)
    ... ]
    >>> result = extract_contacts_pipeline(texts)
    >>> result["total"]
    3
    >>> len(result["successful"]) >= 2
    True
    >>> result["success_rate"] > 0
    True
    """
    pass


# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Module 05: Structured Output with Pydantic - Exercises")
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
        # Check that successful entries are ContactInfo instances
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
