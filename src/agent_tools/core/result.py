from typing import Any

from pydantic import BaseModel


class ToolResult(BaseModel):
    tool_name: str
    ok: bool
    output: Any = None
    error: str | None = None
    error_type: str | None = None

    @classmethod
    def success(cls, tool_name: str, output: Any) -> "ToolResult":
        return cls(tool_name=tool_name, ok=True, output=output)

    @classmethod
    def failure(
        cls,
        tool_name: str,
        error: str,
        error_type: str | None = None,
    ) -> "ToolResult":
        return cls(
            tool_name=tool_name,
            ok=False,
            output=None,
            error=error,
            error_type=error_type,
        )

