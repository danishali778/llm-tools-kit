from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Iterator

from pydantic import BaseModel, ConfigDict, field_validator


class ToolContext(BaseModel):
    allowed_directories: tuple[str, ...] = ()
    approved_tools: frozenset[str] = frozenset()
    require_approval: bool = False
    max_file_size_bytes: int | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("allowed_directories", mode="before")
    @classmethod
    def _coerce_allowed_directories(cls, value: object) -> tuple[str, ...]:
        if value is None:
            return ()
        return tuple(str(item) for item in value)

    @field_validator("approved_tools", mode="before")
    @classmethod
    def _coerce_approved_tools(cls, value: object) -> frozenset[str]:
        if value is None:
            return frozenset()
        return frozenset(str(item) for item in value)

    @field_validator("max_file_size_bytes")
    @classmethod
    def _validate_max_file_size_bytes(cls, value: int | None) -> int | None:
        if value is not None and value < 1:
            raise ValueError("max_file_size_bytes must be greater than 0.")
        return value

    def resolved_allowed_directories(self) -> tuple[Path, ...]:
        return tuple(Path(path).resolve() for path in self.allowed_directories)

    def is_tool_approved(self, tool_name: str) -> bool:
        return tool_name in self.approved_tools


_CURRENT_TOOL_CONTEXT: ContextVar[ToolContext | None] = ContextVar(
    "agent_tools_current_context",
    default=None,
)


def get_current_tool_context() -> ToolContext | None:
    return _CURRENT_TOOL_CONTEXT.get()


@contextmanager
def use_tool_context(context: ToolContext | None) -> Iterator[None]:
    token = _CURRENT_TOOL_CONTEXT.set(context)
    try:
        yield
    finally:
        _CURRENT_TOOL_CONTEXT.reset(token)
