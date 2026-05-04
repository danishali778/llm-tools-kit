from __future__ import annotations

from agent_tools.core.context import ToolContext
from agent_tools.core.errors import ToolExecutionError
from agent_tools.core.tool import Tool


def enforce_tool_permissions(tool: Tool, context: ToolContext | None) -> None:
    if context is None:
        return

    if tool.requires_approval and not context.is_tool_approved(tool.name):
        raise ToolExecutionError(f"Tool '{tool.name}' requires explicit approval.")

    if (
        context.require_approval
        and tool.risk_level in {"medium", "high"}
        and not context.is_tool_approved(tool.name)
    ):
        raise ToolExecutionError(
            f"Tool '{tool.name}' requires approval under the current execution context."
        )
