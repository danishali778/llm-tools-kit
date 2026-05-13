from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import wraps
from typing import TYPE_CHECKING, Any

from agent_tools.core.result import ToolResult

if TYPE_CHECKING:
    from agent_tools.core.context import ToolContext
    from agent_tools.core.registry import ToolRegistry
    from agent_tools.core.tool import Tool

ContextFactory = Callable[[str, dict[str, Any], dict[str, Any] | None], "ToolContext | None"]


def to_langchain_tool(
    tool: "Tool",
    *,
    context_factory: ContextFactory | None = None,
    return_direct: bool = False,
):
    """Export a single local Tool as a LangChain StructuredTool."""
    from agent_tools.core.registry import ToolRegistry

    registry = ToolRegistry([tool])
    return _build_langchain_tool(
        registry,
        tool,
        context_factory=context_factory,
        return_direct=return_direct,
    )


def to_langchain_tools(
    tools: Iterable["Tool"],
    *,
    context_factory: ContextFactory | None = None,
    return_direct: bool = False,
) -> list[Any]:
    """Export an iterable of local tools as LangChain StructuredTools."""
    from agent_tools.core.registry import ToolRegistry

    tool_list = list(tools)
    registry = ToolRegistry(tool_list)
    return [
        _build_langchain_tool(
            registry,
            tool,
            context_factory=context_factory,
            return_direct=return_direct,
        )
        for tool in tool_list
    ]


def registry_to_langchain_tools(
    registry: "ToolRegistry",
    *,
    context_factory: ContextFactory | None = None,
    return_direct: bool = False,
) -> list[Any]:
    """Export all tools in a registry as LangChain StructuredTools."""
    return [
        _build_langchain_tool(
            registry,
            tool,
            context_factory=context_factory,
            return_direct=return_direct,
        )
        for tool in registry.tools
    ]


def _build_langchain_tool(
    registry: "ToolRegistry",
    tool: "Tool",
    *,
    context_factory: ContextFactory | None,
    return_direct: bool,
):
    StructuredTool, _, _ = _require_langchain()

    wrapper = _make_langchain_tool_wrapper(
        registry,
        tool.name,
        tool.func,
        context_factory=context_factory,
    )
    return StructuredTool.from_function(
        wrapper,
        name=tool.name,
        description=tool.description,
        return_direct=return_direct,
        args_schema=tool.input_schema,
        infer_schema=False,
        tags=list(tool.tags) or None,
        metadata=tool.metadata or None,
    )


def _make_langchain_tool_wrapper(
    registry: "ToolRegistry",
    tool_name: str,
    func: Callable[..., Any],
    *,
    context_factory: ContextFactory | None,
) -> Callable[..., Any]:
    _, ToolException, ensure_config = _require_langchain()

    @wraps(func)
    def wrapper(**kwargs: Any) -> Any:
        config = ensure_config()
        metadata = dict(config.get("metadata") or {}) or None
        context = (
            context_factory(tool_name, kwargs, metadata) if context_factory is not None else None
        )
        result = registry.run(tool_name, context=context, **kwargs)
        return _unwrap_tool_result(result, ToolException)

    return wrapper


def _unwrap_tool_result(result: ToolResult, tool_exception: type[Exception]) -> Any:
    if result.ok:
        return result.output

    error_prefix = f"{result.error_type}: " if result.error_type else ""
    raise tool_exception(f"{error_prefix}{result.error}")


def _require_langchain() -> tuple[type[Any], type[Exception], Callable[..., dict[str, Any]]]:
    try:
        from langchain_core.runnables.config import ensure_config
        from langchain_core.tools import StructuredTool, ToolException
    except ImportError as exc:
        raise ImportError(
            "LangChain support is optional. Install it with "
            "'pip install \"llm-tools-kit[langchain]\"'."
        ) from exc

    return StructuredTool, ToolException, ensure_config
