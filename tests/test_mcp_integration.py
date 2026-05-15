from __future__ import annotations

import asyncio
import builtins
from importlib.util import find_spec
from pathlib import Path

import pytest

from agent_tools import ToolContext, ToolRegistry, tool
from agent_tools.integrations import create_mcp_server
from agent_tools.tools import save_memory

mcp_available = find_spec("mcp") is not None
requires_mcp = pytest.mark.skipif(
    not mcp_available,
    reason="mcp optional dependency is not installed",
)


@tool(description="Add two integers.")
def add(a: int, b: int) -> int:
    return a + b


@requires_mcp
def test_create_mcp_server_exports_single_tool_schema():
    registry = ToolRegistry([add])

    server = create_mcp_server(registry, name="Demo", version="0.1.0")

    tools = asyncio.run(server.list_tools())

    assert len(tools) == 1
    exported = tools[0]
    assert exported.name == "add"
    assert exported.description == "Add two integers."
    assert exported.inputSchema["properties"]["a"]["type"] == "integer"
    assert exported.inputSchema["properties"]["b"]["type"] == "integer"


@requires_mcp
def test_create_mcp_server_exports_multiple_tools():
    @tool
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    registry = ToolRegistry([add, greet])
    server = create_mcp_server(registry)

    tools = asyncio.run(server.list_tools())

    assert [item.name for item in tools] == ["add", "greet"]


@requires_mcp
def test_mcp_call_routes_through_registry_successfully():
    registry = ToolRegistry([add])
    server = create_mcp_server(registry)

    content, structured = asyncio.run(server.call_tool("add", {"a": 2, "b": 3}))

    assert structured == {"result": 5}
    assert content[0].text == "5"


@requires_mcp
def test_mcp_call_translates_validation_failure_cleanly():
    registry = ToolRegistry([add])
    server = create_mcp_server(registry)

    with pytest.raises(Exception) as exc_info:
        asyncio.run(server.call_tool("add", {"a": "x", "b": 3}))

    message = str(exc_info.value)
    assert "Error executing tool add" in message
    assert "validation error" in message.lower()


@requires_mcp
def test_mcp_call_translates_missing_tool_cleanly():
    registry = ToolRegistry([add])
    server = create_mcp_server(registry)

    with pytest.raises(Exception) as exc_info:
        asyncio.run(server.call_tool("missing", {}))

    assert "Unknown tool: missing" in str(exc_info.value)


@requires_mcp
def test_mcp_call_can_apply_context_factory(tmp_path: Path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    blocked = tmp_path / "blocked"
    blocked.mkdir()

    registry = ToolRegistry([save_memory])

    def context_factory(
        tool_name: str,
        arguments: dict[str, object],
    ) -> ToolContext | None:
        assert tool_name == "save_memory"
        return ToolContext(allowed_directories=(str(allowed),))

    server = create_mcp_server(registry, context_factory=context_factory)

    with pytest.raises(Exception) as exc_info:
        asyncio.run(
            server.call_tool(
                "save_memory",
                {
                    "text": "blocked write",
                    "memory_path": "memory.json",
                    "base_dir": str(blocked),
                },
            )
        )

    message = str(exc_info.value)
    assert "ToolExecutionError" in message
    assert "allowed directories" in message.lower()


def test_mcp_adapter_missing_dependency_message(monkeypatch: pytest.MonkeyPatch):
    from agent_tools.integrations import mcp as mcp_integration

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("mcp"):
            raise ImportError("missing mcp")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ImportError, match=r'llm-tools-kit\[mcp\]'):
        mcp_integration._require_mcp()
