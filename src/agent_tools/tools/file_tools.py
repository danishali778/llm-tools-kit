from __future__ import annotations

from pathlib import Path

from agent_tools.core.context import get_current_tool_context
from agent_tools.core.errors import ToolExecutionError
from agent_tools.core.tool import tool
from agent_tools.safety.path_safety import (
    ensure_within_allowed_directories,
    resolve_base_dir,
    resolve_within_base,
)


@tool(risk_level="medium")
def read_file_safe(path: str, base_dir: str = ".", max_chars: int = 1_000_000) -> str:
    """Read a text file within base_dir."""
    if max_chars < 1:
        raise ToolExecutionError("max_chars must be greater than 0.")

    base_path = resolve_base_dir(base_dir)
    target_path = resolve_within_base(base_path, path)
    _enforce_context_paths(base_path, target_path)

    if not target_path.is_file():
        raise ToolExecutionError(f"File not found: {path}")

    content = _read_text_file(target_path)
    if len(content) > max_chars:
        raise ToolExecutionError(f"File exceeds max_chars limit of {max_chars}.")
    _enforce_context_size_limit(content)

    return content


@tool(risk_level="medium")
def list_files_safe(
    directory: str = ".",
    base_dir: str = ".",
    pattern: str = "*",
    recursive: bool = True,
    max_results: int = 200,
) -> list[str]:
    """List files inside a directory within the current workspace."""
    if max_results < 1:
        raise ToolExecutionError("max_results must be greater than 0.")

    base_path = resolve_base_dir(base_dir)
    target_dir = resolve_within_base(base_path, directory)
    _enforce_context_paths(base_path, target_dir)

    if not target_dir.is_dir():
        raise ToolExecutionError(f"Directory not found: {directory}")

    iterator = target_dir.rglob(pattern) if recursive else target_dir.glob(pattern)
    files = [
        str(path.relative_to(base_path))
        for path in sorted(iterator)
        if path.is_file()
    ]
    return files[:max_results]


@tool(risk_level="medium")
def search_files_safe(
    directory: str,
    query: str,
    base_dir: str = ".",
    pattern: str = "*",
    case_sensitive: bool = False,
    max_results: int = 50,
) -> list[str]:
    """Search text files within a directory and return matching lines."""
    if not query:
        raise ToolExecutionError("query must not be empty.")
    if max_results < 1:
        raise ToolExecutionError("max_results must be greater than 0.")

    base_path = resolve_base_dir(base_dir)
    target_dir = resolve_within_base(base_path, directory)
    _enforce_context_paths(base_path, target_dir)

    if not target_dir.is_dir():
        raise ToolExecutionError(f"Directory not found: {directory}")

    needle = query if case_sensitive else query.casefold()
    matches: list[str] = []

    for path in sorted(target_dir.rglob(pattern)):
        if not path.is_file():
            continue

        try:
            content = _read_text_file(path)
        except ToolExecutionError:
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            haystack = line if case_sensitive else line.casefold()
            if needle in haystack:
                relative_path = path.relative_to(base_path)
                matches.append(f"{relative_path}:{line_number}:{line.strip()}")
                if len(matches) >= max_results:
                    return matches

    return matches


def _enforce_context_paths(*paths: Path) -> None:
    context = get_current_tool_context()
    if context is None:
        return

    allowed_directories = context.resolved_allowed_directories()
    if not allowed_directories:
        return

    for path in paths:
        ensure_within_allowed_directories(path, allowed_directories)


def _enforce_context_size_limit(content: str) -> None:
    context = get_current_tool_context()
    if context is None or context.max_file_size_bytes is None:
        return

    content_size = len(content.encode("utf-8"))
    if content_size > context.max_file_size_bytes:
        raise ToolExecutionError(
            f"File exceeds max_file_size_bytes limit of {context.max_file_size_bytes}."
        )


def _read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ToolExecutionError(f"File is not valid UTF-8 text: {path.name}") from exc
    except OSError as exc:
        raise ToolExecutionError(f"Unable to read file: {path}") from exc
