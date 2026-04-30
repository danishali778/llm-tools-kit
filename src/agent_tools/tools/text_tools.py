from __future__ import annotations

from agent_tools.core.errors import ToolExecutionError
from agent_tools.core.tool import tool


@tool
def chunk_text(text: str, max_chars: int = 4000) -> list[str]:
    """Split text into chunks that do not exceed max_chars."""
    if max_chars < 1:
        raise ToolExecutionError("max_chars must be greater than 0.")

    stripped = text.strip()
    if not stripped:
        return []

    if len(stripped) <= max_chars:
        return [stripped]

    chunks: list[str] = []
    start = 0

    while start < len(stripped):
        end = min(start + max_chars, len(stripped))
        if end == len(stripped):
            chunks.append(stripped[start:].strip())
            break

        split_at = stripped.rfind(" ", start, end + 1)
        if split_at <= start:
            split_at = end

        chunks.append(stripped[start:split_at].strip())
        start = split_at

        while start < len(stripped) and stripped[start].isspace():
            start += 1

    return chunks
