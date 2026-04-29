"""PII detection and redaction pipeline.

Provides regex-based detectors for common PII types (email, phone, SSN,
credit card), configurable redaction strategies, a scan-and-redact pipeline,
and an audit log that records every redaction performed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple

from config import PII_PATTERNS


class RedactionStrategy(str, Enum):
    """How detected PII should be replaced in text."""

    MASK = "mask"       # Replace with asterisks:  j***@e***.com
    REPLACE = "replace" # Replace with a label:    [EMAIL_REDACTED]


@dataclass
class PIIMatch:
    """A single PII occurrence found in text."""

    pii_type: str
    original: str
    start: int
    end: int


@dataclass
class RedactionRecord:
    """Audit-log entry for one redaction event."""

    timestamp: str
    pii_type: str
    original_snippet: str  # first 4 chars + "..." for audit without storing full PII
    replacement: str
    position: Tuple[int, int]


@dataclass
class RedactionResult:
    """Outcome of running the redaction pipeline on a piece of text."""

    original_text: str
    redacted_text: str
    matches_found: int
    records: List[RedactionRecord] = field(default_factory=list)


class PIIRedactor:
    """Scan text for PII and redact it according to a chosen strategy."""

    def __init__(
        self,
        strategy: RedactionStrategy = RedactionStrategy.REPLACE,
        patterns: Optional[Dict[str, re.Pattern[str]]] = None,
    ) -> None:
        self.strategy = strategy
        self.patterns = patterns or PII_PATTERNS
        self.audit_log: List[RedactionRecord] = []

    # -- scanning --------------------------------------------------------------

    def scan(self, text: str) -> List[PIIMatch]:
        """Return all PII matches found in *text* without modifying it."""
        matches: List[PIIMatch] = []
        for pii_type, pattern in self.patterns.items():
            for m in pattern.finditer(text):
                matches.append(PIIMatch(
                    pii_type=pii_type,
                    original=m.group(),
                    start=m.start(),
                    end=m.end(),
                ))
        # Sort by position so we can replace right-to-left.
        matches.sort(key=lambda m: m.start)
        return matches

    # -- redaction helpers -----------------------------------------------------

    def _mask_value(self, value: str, pii_type: str) -> str:
        """Produce a masked version of the PII value."""
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]

    def _replace_label(self, pii_type: str) -> str:
        """Produce a bracketed label like [EMAIL_REDACTED]."""
        return f"[{pii_type.upper()}_REDACTED]"

    def _redact_value(self, value: str, pii_type: str) -> str:
        """Apply the configured redaction strategy to a single value."""
        if self.strategy == RedactionStrategy.MASK:
            return self._mask_value(value, pii_type)
        return self._replace_label(pii_type)

    # -- pipeline --------------------------------------------------------------

    def redact(self, text: str) -> RedactionResult:
        """Scan *text* for PII, redact all matches, and return results."""
        matches = self.scan(text)
        if not matches:
            return RedactionResult(
                original_text=text,
                redacted_text=text,
                matches_found=0,
            )

        records: List[RedactionRecord] = []
        redacted = text

        # Process matches in reverse order so indices stay valid.
        for match in reversed(matches):
            replacement = self._redact_value(match.original, match.pii_type)
            redacted = redacted[:match.start] + replacement + redacted[match.end:]

            snippet = match.original[:4] + "..." if len(match.original) > 4 else match.original
            record = RedactionRecord(
                timestamp=datetime.now(timezone.utc).isoformat(),
                pii_type=match.pii_type,
                original_snippet=snippet,
                replacement=replacement,
                position=(match.start, match.end),
            )
            records.append(record)
            self.audit_log.append(record)

        records.reverse()  # restore original order for the result
        return RedactionResult(
            original_text=text,
            redacted_text=redacted,
            matches_found=len(matches),
            records=records,
        )

    def get_audit_log(self) -> List[RedactionRecord]:
        """Return a copy of the accumulated audit log."""
        return list(self.audit_log)

    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        self.audit_log.clear()
