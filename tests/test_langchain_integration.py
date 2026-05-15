from __future__ import annotations

import builtins
from importlib.util import find_spec
from pathlib import Path

import pytest

from agent_tools import ToolContext, ToolRegistry, tool
from agent_tools.integrations import (
    registry_to_langchain_tools,
    to_langchain_tool,
    to_langchain_tools,
)
from agent_tools.tools import save_memory

langchain_available = find_spec("langchain_core") is not None
requires_langchain = pytest.mark.skipif(
    not langchain_available,
    reason="langchain-core optional dependency is not installed",
)


@tool(description="Add two integers.", tags=("math",), metadata={"unit": "count"})
def add(a: int, b: int) -> int:
    return a + b


@requires_langchain
def test_to_langchain_tool_exports_schema_and_metadata():
    exported = to_langchain_tool(add)

    assert exported.name == "add"
    assert exported.description == "Add two integers."
    assert exported.tags == ["math"]
    assert exported.metadata == {"unit": "count"}
    assert exported.args_schema is add.input_schema


@requires_langchain
def test_to_langchain_tools_preserves_order():
    @tool
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    exported = to_langchain_tools([add, greet])

    assert [tool_item.name for tool_item in exported] == ["add", "greet"]


@requires_langchain
def test_langchain_tool_invocation_returns_successful_output():
    exported = to_langchain_tool(add)

    assert exported.invoke({"a": 2, "b": 3}) == 5


@requires_langchain
def test_langchain_tool_routes_through_registry_run(monkeypatch: pytest.MonkeyPatch):
    registry = ToolRegistry([add])
    exported = registry_to_langchain_tools(registry)[0]

    calls: list[tuple[str, dict[str, object]]] = []

    def fake_run(name: str, *, context: ToolContext | None = None, **kwargs: object):
        calls.append((name, kwargs))
        return type(
            "Result",
            (),
            {"ok": True, "output": 99, "error": None, "error_type": None},
        )()

    monkeypatch.setattr(registry, "run", fake_run)

    assert exported.invoke({"a": 2, "b": 3}) == 99
    assert calls == [("add", {"a": 2, "b": 3})]


@requires_langchain
def test_langchain_tool_surfaces_validation_failure_cleanly():
    exported = to_langchain_tool(add)

    with pytest.raises(Exception) as exc_info:
        exported.invoke({"a": "x", "b": 3})

    message = str(exc_info.value)
    assert "validation error" in message.lower()
    assert "AddInput" in message


@requires_langchain
def test_langchain_tool_surfaces_missing_tool_cleanly():
    registry = ToolRegistry([add])
    exported = registry_to_langchain_tools(registry)[0]
    registry._tools.pop("add")

    with pytest.raises(Exception) as exc_info:
        exported.invoke({"a": 2, "b": 3})

    assert "ToolNotFoundError" in str(exc_info.value)


@requires_langchain
def test_langchain_tool_can_apply_context_factory(tmp_path: Path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    blocked = tmp_path / "blocked"
    blocked.mkdir()

    registry = ToolRegistry([save_memory])
    seen_metadata: list[dict[str, object] | None] = []

    def context_factory(
        tool_name: str,
        arguments: dict[str, object],
        metadata: dict[str, object] | None,
    ) -> ToolContext | None:
        assert tool_name == "save_memory"
        assert arguments["text"] == "blocked write"
        seen_metadata.append(metadata)
        return ToolContext(allowed_directories=(str(allowed),))

    exported = registry_to_langchain_tools(
        registry,
        context_factory=context_factory,
    )[0]

    with pytest.raises(Exception) as exc_info:
        exported.invoke(
            {
                "text": "blocked write",
                "memory_path": "memory.json",
                "base_dir": str(blocked),
            },
            config={"metadata": {"caller": "demo"}},
        )

    assert seen_metadata == [{"caller": "demo"}]
    message = str(exc_info.value)
    assert "ToolExecutionError" in message
    assert "allowed directories" in message.lower()


def test_langchain_adapter_missing_dependency_message(monkeypatch: pytest.MonkeyPatch):
    from agent_tools.integrations import langchain as langchain_integration

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("langchain_core"):
            raise ImportError("missing langchain_core")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ImportError, match=r'llm-tools-kit\[langchain\]'):
        langchain_integration._require_langchain()
