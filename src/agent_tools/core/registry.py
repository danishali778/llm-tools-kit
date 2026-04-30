from __future__ import annotations

from collections.abc import Iterable

from agent_tools.core.errors import ToolNotFoundError, ToolRegistrationError
from agent_tools.core.executor import ToolExecutor
from agent_tools.core.result import ToolResult
from agent_tools.core.tool import Tool


class ToolRegistry:
    def __init__(self, tools: Iterable[Tool] | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        self._executor = ToolExecutor(self)

        for tool_item in tools or ():
            self.register(tool_item)

    def register(self, tool: Tool) -> Tool:
        if not isinstance(tool, Tool):
            raise ToolRegistrationError("Only Tool instances can be registered.")

        if tool.name in self._tools:
            raise ToolRegistrationError(f"Tool '{tool.name}' is already registered.")

        self._tools[tool.name] = tool
        return tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(f"Tool '{name}' is not registered.") from exc

    def list(self) -> list[Tool]:
        return list(self._tools.values())

    @property
    def tools(self) -> list[Tool]:
        return self.list()

    def run(self, name: str, **kwargs: object) -> ToolResult:
        return self._executor.run(name, **kwargs)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)
