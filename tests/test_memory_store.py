from datetime import datetime, timezone

from agent_tools.memory.models import MemoryNote


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
