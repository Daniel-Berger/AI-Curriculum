"""
Solution for Ticket #002 — Customer PII Found in API Logs
==========================================================
Root cause:  Two issues combine to create a PII exposure.

  1. main.py logs the raw user message at DEBUG level, which can
     contain SSNs, DOBs, credit-card numbers, and other PII.
  2. config.py logs the OpenAI API key in plaintext at INFO level
     every time the module is imported.

Fix:
  1. Build a PII redaction pipeline that scrubs sensitive patterns
     from text before it is logged or sent to the LLM.
  2. Never log API keys — mask them if they must appear at all.
  3. Set log level to INFO (or WARNING) in production so DEBUG
     messages with raw payloads are never emitted.
"""

import re
import logging
from typing import List, Tuple

logger = logging.getLogger("chat_service")

# ---------------------------------------------------------------------------
# PII patterns — each tuple is (human-readable name, compiled regex)
# ---------------------------------------------------------------------------
PII_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("CREDIT_CARD", re.compile(r"\b(?:\d[ -]*?){13,19}\b")),
    ("DOB", re.compile(
        r"\b(?:DOB|Date of Birth)[:\s]*\d{4}-\d{2}-\d{2}\b", re.IGNORECASE
    )),
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")),
    ("PHONE", re.compile(r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
]


def redact_pii(text: str) -> str:
    """Replace all recognized PII patterns with a redaction placeholder."""
    for label, pattern in PII_PATTERNS:
        text = pattern.sub(f"[REDACTED_{label}]", text)
    return text


def mask_secret(value: str, visible_chars: int = 4) -> str:
    """Show only the last `visible_chars` characters of a secret."""
    if len(value) <= visible_chars:
        return "****"
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]


# ---------------------------------------------------------------------------
# Secure logging helper
# ---------------------------------------------------------------------------

def log_request_safely(user_id: str, message: str) -> None:
    """Log an incoming request without exposing PII."""
    sanitized = redact_pii(message)
    # Log only a truncated preview, never the full message
    preview = sanitized[:80] + "..." if len(sanitized) > 80 else sanitized
    logger.info("Incoming request from user=%s message_preview=%s", user_id, preview)


# ---------------------------------------------------------------------------
# Secure config logging (replaces the line in config.py)
# ---------------------------------------------------------------------------

def log_config_safely(api_key: str, model_name: str) -> None:
    """Log configuration without exposing secrets."""
    logger.info(
        "Loaded configuration: API_KEY=%s MODEL=%s",
        mask_secret(api_key),
        model_name,
    )
