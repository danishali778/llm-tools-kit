from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any

from agent_tools.core.result import ToolResult

if TYPE_CHECKING:
    from agent_tools.core.context import ToolContext
    from agent_tools.core.registry import ToolRegistry

ContextFactory = Callable[[str, dict[str, Any]], "ToolContext | None"]


def create_mcp_server(
    registry: "ToolRegistry",
    *,
    name: str = "llm-tools-kit",
    version: str | None = None,
    instructions: str | None = None,
    context_factory: ContextFactory | None = None,
):
    """Create an MCP stdio server that exposes a ToolRegistry."""
    FastMCP, MCPToolError = _require_mcp()

    server = FastMCP(name=name, instructions=_merge_instructions(instructions, version))
    if version is not None:
        setattr(server, "agent_tools_version", version)

    for tool in registry.tools:
        wrapper = _make_mcp_tool_wrapper(
            registry,
            tool.name,
            tool.func,
            context_factory=context_factory,
            mcp_tool_error=MCPToolError,
        )
        server.add_tool(
            wrapper,
            name=tool.name,
            description=tool.description,
            meta=tool.metadata or None,
        )

    return server


def serve_mcp(
    registry: "ToolRegistry",
    *,
    name: str = "llm-tools-kit",
    version: str | None = None,
    instructions: str | None = None,
    context_factory: ContextFactory | None = None,
) -> None:
    """Create and run an MCP server over stdio."""
    server = create_mcp_server(
        registry,
        name=name,
        version=version,
        instructions=instructions,
        context_factory=context_factory,
    )
    server.run(transport="stdio")


def _make_mcp_tool_wrapper(
    registry: "ToolRegistry",
    tool_name: str,
    func: Callable[..., Any],
    *,
    context_factory: ContextFactory | None,
    mcp_tool_error: type[Exception],
) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if args:
            raise TypeError("MCP tool wrappers expect keyword arguments only.")

        context = context_factory(tool_name, kwargs) if context_factory is not None else None
        result = registry.run(tool_name, context=context, **kwargs)
        return _unwrap_tool_result(result, mcp_tool_error)

    return wrapper


def _unwrap_tool_result(result: ToolResult, mcp_tool_error: type[Exception]) -> Any:
    if result.ok:
        return result.output

    error_prefix = f"{result.error_type}: " if result.error_type else ""
    raise mcp_tool_error(f"{error_prefix}{result.error}")


def _merge_instructions(instructions: str | None, version: str | None) -> str | None:
    if version is None:
        return instructions
    if instructions:
        return f"{instructions}\n\nVersion: {version}"
    return f"Version: {version}"


def _require_mcp() -> tuple[type[Any], type[Exception]]:
    try:
        from mcp.server.fastmcp import FastMCP
        from mcp.server.fastmcp.exceptions import ToolError
    except ImportError as exc:
        raise ImportError(
            "MCP support is optional. Install it with 'pip install \"llm-tools-kit[mcp]\"'."
        ) from exc

    return FastMCP, ToolError
