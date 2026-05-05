from datetime import datetime, timezone
from pathlib import Path

from agent_tools.memory.models import MemoryNote
from agent_tools.memory.store import JsonMemoryStore


def test_memory_note_defaults():
    note = MemoryNote(
        id="note-1",
        text="remember this",
    )

    assert note.tags == []
    assert note.metadata == {}
    assert isinstance(note.created_at, datetime)
    assert isinstance(note.updated_at, datetime)
    assert note.created_at.tzinfo is timezone.utc
    assert note.updated_at.tzinfo is timezone.utc


def test_memory_note_supports_structured_metadata_and_datetime_fields():
    created_at = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    updated_at = datetime(2026, 1, 2, 4, 5, 6, tzinfo=timezone.utc)

    note = MemoryNote(
        id="note-2",
        text="remember nested metadata",
        metadata={
            "source": "chat",
            "attempts": 2,
            "flags": {"pinned": True},
            "related_ids": ["a", "b"],
        },
        created_at=created_at,
        updated_at=updated_at,
    )

    assert note.metadata == {
        "source": "chat",
        "attempts": 2,
        "flags": {"pinned": True},
        "related_ids": ["a", "b"],
    }
    assert note.created_at == created_at
    assert note.updated_at == updated_at


def test_store_creates_file_and_saves_note(tmp_path: Path):
    store = JsonMemoryStore(memory_path="memory.json", base_dir=tmp_path)
    note = store.save_note(text="hello world", tags=["demo"])

    assert note["text"] == "hello world"
    assert (tmp_path / "memory.json").exists()


def test_store_can_get_note_by_id(tmp_path: Path):
    store = JsonMemoryStore(memory_path="memory.json", base_dir=tmp_path)
    note = store.save_note(text="alpha")

    loaded = store.get_note(note["id"])

    assert loaded is not None
    assert loaded["id"] == note["id"]


def test_store_returns_none_for_missing_note(tmp_path: Path):
    store = JsonMemoryStore(memory_path="memory.json", base_dir=tmp_path)

    assert store.get_note("missing") is None


def test_store_searches_text_and_tags(tmp_path: Path):
    store = JsonMemoryStore(memory_path="memory.json", base_dir=tmp_path)
    store.save_note(text="remember the release plan", tags=["project"])
    store.save_note(text="buy milk", tags=["personal"])

    results = store.search_notes("release")

    assert len(results) == 1
    assert results[0]["text"] == "remember the release plan"
