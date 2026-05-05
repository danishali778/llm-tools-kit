from pathlib import Path

from agent_tools import ToolContext, ToolRegistry
from agent_tools.tools import get_memory, save_memory, search_memory


def test_save_memory_returns_note_payload(tmp_path: Path):
    result = save_memory(
        text="remember deployment checklist",
        tags=["release"],
        memory_path="memory.json",
        base_dir=str(tmp_path),
    )

    assert result["text"] == "remember deployment checklist"
    assert result["tags"] == ["release"]


def test_get_memory_returns_saved_note(tmp_path: Path):
    saved = save_memory(
        text="remember launch date",
        memory_path="memory.json",
        base_dir=str(tmp_path),
    )

    loaded = get_memory(
        memory_id=saved["id"],
        memory_path="memory.json",
        base_dir=str(tmp_path),
    )

    assert loaded is not None
    assert loaded["id"] == saved["id"]


def test_search_memory_returns_matching_notes(tmp_path: Path):
    save_memory(
        text="draft release notes",
        tags=["docs"],
        memory_path="memory.json",
        base_dir=str(tmp_path),
    )
    save_memory(
        text="buy groceries",
        tags=["home"],
        memory_path="memory.json",
        base_dir=str(tmp_path),
    )

    results = search_memory(
        query="release",
        memory_path="memory.json",
        base_dir=str(tmp_path),
        limit=5,
    )

    assert len(results) == 1
    assert results[0]["text"] == "draft release notes"


def test_save_memory_respects_allowed_directories(tmp_path: Path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    blocked = tmp_path / "blocked"
    blocked.mkdir()

    registry = ToolRegistry([save_memory])
    context = ToolContext(allowed_directories=(str(allowed),))

    result = registry.run(
        "save_memory",
        context=context,
        text="blocked write",
        memory_path="memory.json",
        base_dir=str(blocked),
    )

    assert result.ok is False
