from __future__ import annotations

import re
from typing import Any

from agent_tools.core.tool import tool

_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("openai", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("github", re.compile(r"\bghp_[A-Za-z0-9]{30,}\b")),
    ("gemini", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
)


@tool
def detect_secrets(text: str) -> list[dict[str, Any]]:
    """Detect likely secrets in text using common token patterns."""
    findings: list[dict[str, Any]] = []

    for secret_type, pattern in _SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                {
                    "type": secret_type,
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                }
            )

    findings.sort(key=lambda item: int(item["start"]))
    return findings


@tool
def redact_secrets(text: str) -> str:
    """Redact likely secrets in text using common token patterns."""
    redacted = text
    for secret_type, pattern in _SECRET_PATTERNS:
        redacted = pattern.sub(f"[REDACTED:{secret_type}]", redacted)
    return redacted
