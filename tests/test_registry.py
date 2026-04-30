import pytest

from agent_tools import ToolNotFoundError, ToolRegistrationError, ToolRegistry, tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def test_registry_registers_and_gets_tool() -> None:
    registry = ToolRegistry()
    registry.register(add)

    assert len(registry) == 1
    assert "add" in registry
    assert registry.get("add") is add


def test_registry_rejects_duplicate_tool_names() -> None:
    registry = ToolRegistry([add])

    with pytest.raises(ToolRegistrationError):
        registry.register(add)


def test_registry_raises_for_missing_tool() -> None:
    registry = ToolRegistry()

    with pytest.raises(ToolNotFoundError):
        registry.get("missing")


def test_registry_run_executes_tool() -> None:
    registry = ToolRegistry([add])

    result = registry.run("add", a=2, b=3)

    assert result.ok is True
    assert result.output == 5

