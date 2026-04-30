from __future__ import annotations

import ast
import json
import re
from collections.abc import Iterator
from typing import Any

from agent_tools.core.errors import ToolExecutionError
from agent_tools.core.tool import tool

_CODE_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
_TRAILING_COMMA_PATTERN = re.compile(r",\s*([}\]])")


@tool
def extract_json(text: str) -> Any:
    """Extract the first JSON object or array from text."""
    for candidate in _json_candidates(text):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    raise ToolExecutionError("No valid JSON object or array was found in the input text.")


@tool
def repair_json(text: str) -> Any:
    """Repair common JSON formatting issues and return parsed data."""
    for candidate in _json_candidates(text):
        repaired = _repair_candidate(candidate)

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

        parsed = _parse_python_literal(repaired)
        if parsed is not None:
            return parsed

    raise ToolExecutionError("Unable to repair the input into valid JSON data.")


def _json_candidates(text: str) -> Iterator[str]:
    seen: set[str] = set()

    for candidate in [text.strip(), *_CODE_BLOCK_PATTERN.findall(text), *_balanced_segments(text)]:
        cleaned = candidate.strip()
        if not cleaned or cleaned in seen:
            continue

        seen.add(cleaned)
        yield cleaned


def _balanced_segments(text: str) -> Iterator[str]:
    for start, char in enumerate(text):
        if char not in "{[":
            continue

        segment = _extract_balanced_segment(text, start)
        if segment is not None:
            yield segment


def _extract_balanced_segment(text: str, start: int) -> str | None:
    stack: list[str] = []
    in_string = False
    escape = False
    quote_char = ""

    pairs = {"{": "}", "[": "]"}
    closing = set(pairs.values())

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote_char:
                in_string = False
            continue

        if char in "\"'":
            in_string = True
            quote_char = char
            continue

        if char in pairs:
            stack.append(pairs[char])
            continue

        if char in closing:
            if not stack or char != stack.pop():
                return None

            if not stack:
                return text[start : index + 1]

    return None


def _repair_candidate(candidate: str) -> str:
    repaired = candidate.strip().rstrip(";")
    repaired = _TRAILING_COMMA_PATTERN.sub(r"\1", repaired)
    return repaired


def _parse_python_literal(candidate: str) -> Any | None:
    try:
        parsed = ast.literal_eval(candidate)
    except (SyntaxError, ValueError):
        return None

    return _to_json_compatible(parsed)


def _to_json_compatible(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _to_json_compatible(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [_to_json_compatible(item) for item in value]

    return value
