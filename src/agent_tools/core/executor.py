from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from agent_tools.core.errors import ToolError, ToolNotFoundError
from agent_tools.core.result import ToolResult

if TYPE_CHECKING:
    from agent_tools.core.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: "ToolRegistry") -> None:
        self.registry = registry

    def run(self, name: str, **kwargs: Any) -> ToolResult:
        try:
            tool = self.registry.get(name)
        except ToolNotFoundError as exc:
            return ToolResult.failure(
                tool_name=name,
                error=str(exc),
                error_type=exc.__class__.__name__,
            )

        try:
            output = tool.run(**kwargs)
        except ValidationError as exc:
            return ToolResult.failure(
                tool_name=name,
                error=str(exc),
                error_type="ToolValidationError",
            )
        except ToolError as exc:
            return ToolResult.failure(
                tool_name=name,
                error=str(exc),
                error_type=exc.__class__.__name__,
            )
        except Exception as exc:
            return ToolResult.failure(
                tool_name=name,
                error=str(exc),
                error_type=exc.__class__.__name__,
            )

        return ToolResult.success(tool_name=name, output=output)

