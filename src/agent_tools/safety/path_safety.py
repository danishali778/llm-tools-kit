from __future__ import annotations

from pathlib import Path

from agent_tools.core.errors import ToolExecutionError


def resolve_base_dir(base_dir: str) -> Path:
    path = Path(base_dir).resolve()
    if not path.is_dir():
        raise ToolExecutionError(f"Base directory not found: {base_dir}")
    return path


def resolve_within_base(base_path: Path, user_path: str) -> Path:
    target = (base_path / user_path).resolve()
    try:
        target.relative_to(base_path)
    except ValueError as exc:
        raise ToolExecutionError("Path escapes the allowed base directory.") from exc
    return target


def ensure_within_allowed_directories(path: Path, allowed_directories: tuple[Path, ...]) -> None:
    if not allowed_directories:
        return

    for allowed_path in allowed_directories:
        try:
            path.relative_to(allowed_path)
            return
        except ValueError:
            continue

    raise ToolExecutionError("Path is outside the allowed directories.")
