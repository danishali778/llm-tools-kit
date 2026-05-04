from agent_tools.memory.models import MemoryNote


def test_memory_note_defaults():
    note = MemoryNote(
        id="note-1",
        text="remember this",
    )

    assert note.tags == []
    assert note.metadata == {}
    assert note.created_at
    assert note.updated_at
