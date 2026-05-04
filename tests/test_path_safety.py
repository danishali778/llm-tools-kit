from pathlib import Path

from agent_tools import ToolContext, ToolRegistry
from agent_tools.tools import list_files_safe, read_file_safe


def test_file_tools_respect_allowed_directories_context(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    blocked = tmp_path / "blocked"
    allowed.mkdir()
    blocked.mkdir()

    file_path = blocked / "secret.txt"
    file_path.write_text("secret", encoding="utf-8")
    registry = ToolRegistry([read_file_safe])

    result = registry.run(
        "read_file_safe",
        context=ToolContext(allowed_directories=[str(allowed)]),
        path=str(file_path),
        base_dir=str(tmp_path),
    )

    assert result.ok is False
    assert result.error_type == "ToolExecutionError"
    assert result.error == "Path is outside the allowed directories."


def test_file_tools_allow_paths_within_allowed_directories(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    file_path = allowed / "note.txt"
    file_path.write_text("hello", encoding="utf-8")
    registry = ToolRegistry([read_file_safe])

    result = registry.run(
        "read_file_safe",
        context=ToolContext(allowed_directories=[str(allowed)]),
        path="note.txt",
        base_dir=str(allowed),
    )

    assert result.ok is True
    assert result.output == "hello"


def test_file_tools_respect_context_file_size_limit(tmp_path: Path) -> None:
    file_path = tmp_path / "note.txt"
    file_path.write_text("hello world", encoding="utf-8")
    registry = ToolRegistry([read_file_safe])

    result = registry.run(
        "read_file_safe",
        context=ToolContext(max_file_size_bytes=5),
        path="note.txt",
        base_dir=str(tmp_path),
    )

    assert result.ok is False
    assert result.error_type == "ToolExecutionError"
    assert result.error == "File exceeds max_file_size_bytes limit of 5."


def test_list_files_safe_respects_allowed_directories_context(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    blocked = tmp_path / "blocked"
    allowed.mkdir()
    blocked.mkdir()
    (allowed / "a.txt").write_text("a", encoding="utf-8")
    (blocked / "b.txt").write_text("b", encoding="utf-8")
    registry = ToolRegistry([list_files_safe])

    result = registry.run(
        "list_files_safe",
        context=ToolContext(allowed_directories=[str(allowed)]),
        directory="blocked",
        base_dir=str(tmp_path),
        pattern="*.txt",
    )

    assert result.ok is False
    assert result.error_type == "ToolExecutionError"
    assert result.error == "Path is outside the allowed directories."
