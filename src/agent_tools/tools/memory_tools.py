from __future__ import annotations

from typing import Any

from agent_tools.core.tool import tool
from agent_tools.memory.store import JsonMemoryStore


@tool(risk_level="medium")
def save_memory(
    text: str,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    memory_path: str = "memory.json",
    base_dir: str = ".",
) -> dict[str, object]:
    """Save a note to local memory."""
    return JsonMemoryStore(memory_path=memory_path, base_dir=base_dir).save_note(
        text=text,
        tags=tags,
        metadata=metadata,
    )


@tool(risk_level="low")
def get_memory(
    memory_id: str,
    memory_path: str = "memory.json",
    base_dir: str = ".",
) -> dict[str, object] | None:
    """Load a saved note from local memory."""
    return JsonMemoryStore(memory_path=memory_path, base_dir=base_dir).get_note(memory_id)


@tool(risk_level="low")
def search_memory(
    query: str,
    memory_path: str = "memory.json",
    base_dir: str = ".",
    limit: int = 10,
) -> list[dict[str, object]]:
    """Search saved notes by substring."""
    return JsonMemoryStore(memory_path=memory_path, base_dir=base_dir).search_notes(
        query=query,
        limit=limit,
    )
