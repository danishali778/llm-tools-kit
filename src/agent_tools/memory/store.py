from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from agent_tools.core.context import get_current_tool_context
from agent_tools.memory.models import MemoryNote
from agent_tools.safety.path_safety import (
    ensure_within_allowed_directories,
    resolve_base_dir,
    resolve_within_base,
)


class JsonMemoryStore:
    def __init__(self, memory_path: str = "memory.json", base_dir: str | Path = "."):
        self._base_dir = resolve_base_dir(str(base_dir))
        self._path = resolve_within_base(self._base_dir, memory_path)
        self._enforce_context_paths()

    def _enforce_context_paths(self) -> None:
        context = get_current_tool_context()
        if context is None:
            return

        allowed_directories = context.resolved_allowed_directories()
        if not allowed_directories:
            return

        ensure_within_allowed_directories(self._base_dir, allowed_directories)
        ensure_within_allowed_directories(self._path, allowed_directories)

    def _load_notes(self) -> list[MemoryNote]:
        if not self._path.exists():
            return []

        payload = json.loads(self._path.read_text(encoding="utf-8"))
        return [MemoryNote.model_validate(item) for item in payload]

    def _save_notes(self, notes: list[MemoryNote]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(
                [note.model_dump(mode="json") for note in notes],
                indent=2,
            ),
            encoding="utf-8",
        )

    def save_note(
        self,
        text: str,
        tags: list[str] | None = None,
        metadata: dict[str, object] | None = None,
    ) -> dict[str, object]:
        note = MemoryNote(
            id=str(uuid4()),
            text=text,
            tags=tags or [],
            metadata=metadata or {},
        )

        notes = self._load_notes()
        notes.append(note)
        self._save_notes(notes)
        return note.model_dump(mode="json")

    def get_note(self, memory_id: str) -> dict[str, object] | None:
        for note in self._load_notes():
            if note.id == memory_id:
                return note.model_dump(mode="json")
        return None

    def search_notes(self, query: str, limit: int = 10) -> list[dict[str, object]]:
        needle = query.casefold()
        matches: list[dict[str, object]] = []

        for note in self._load_notes():
            haystacks = [note.text.casefold(), *[tag.casefold() for tag in note.tags]]
            if any(needle in value for value in haystacks):
                matches.append(note.model_dump(mode="json"))
            if len(matches) >= limit:
                break

        return matches
