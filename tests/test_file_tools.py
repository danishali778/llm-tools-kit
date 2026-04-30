from pathlib import Path

import pytest

from agent_tools import ToolRegistry
from agent_tools.tools import list_files_safe, read_file_safe, search_files_safe


def test_read_file_safe_reads_text_file(tmp_path: Path) -> None:
    file_path = tmp_path / "note.txt"
    file_path.write_text("hello", encoding="utf-8")

    assert read_file_safe(str(file_path), base_dir=str(tmp_path)) == "hello"


def test_read_file_safe_rejects_path_escape(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")

    with pytest.raises(Exception, match="escapes the allowed base directory"):
        read_file_safe(str(outside), base_dir=str(tmp_path))


def test_list_files_safe_returns_relative_paths(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "b.txt").write_text("b", encoding="utf-8")

    files = list_files_safe(directory=".", base_dir=str(tmp_path), pattern="*.txt")

    expected = {
        "a.txt",
        "nested\\b.txt",
    }
    assert set(files) == expected


def test_search_files_safe_returns_matching_lines(tmp_path: Path) -> None:
    (tmp_path / "alpha.txt").write_text("one\ntwo match\nthree", encoding="utf-8")

    matches = search_files_safe(".", "match", base_dir=str(tmp_path), pattern="*.txt")

    assert len(matches) == 1
    assert matches[0].endswith(":2:two match")


def test_file_tools_run_through_registry(tmp_path: Path) -> None:
    file_path = tmp_path / "payload.txt"
    file_path.write_text("payload", encoding="utf-8")
    registry = ToolRegistry([read_file_safe])

    result = registry.run(
        "read_file_safe",
        path=str(file_path),
        base_dir=str(tmp_path),
    )

    assert result.ok is True
    assert result.output == "payload"
