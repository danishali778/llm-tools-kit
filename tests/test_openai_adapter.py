from dataclasses import dataclass
from typing import Literal

from agent_tools import ToolRegistry, tool
from agent_tools.adapters import (
    execute_openai_tool_call,
    to_openai_tool,
    to_openai_tools,
)


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def test_converts_tool_to_openai_tool_schema() -> None:
    declaration = to_openai_tool(add)

    assert declaration == {
        "type": "function",
        "name": "add",
        "description": "Add two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
    }


def test_converts_multiple_tools_to_openai_tool_list() -> None:
    @tool
    def greet(name: str) -> str:
        """Greet a person."""
        return f"Hello, {name}!"

    tools = to_openai_tools([add, greet])

    assert tools == [to_openai_tool(add), to_openai_tool(greet)]


def test_preserves_supported_schema_metadata() -> None:
    @tool
    def set_light(level: int, color: Literal["daylight", "warm"]) -> str:
        """Set a light."""
        return f"{color}:{level}"

    declaration = to_openai_tool(set_light)

    assert declaration["parameters"]["properties"]["color"] == {
        "enum": ["daylight", "warm"],
        "type": "string",
    }


def test_executes_openai_tool_call_from_mapping() -> None:
    registry = ToolRegistry([add])

    result = execute_openai_tool_call(
        {"type": "function_call", "name": "add", "arguments": {"a": 2, "b": 3}},
        registry,
    )

    assert result.ok is True
    assert result.output == 5


def test_executes_openai_tool_call_from_object() -> None:
    @dataclass
    class FunctionCall:
        name: str
        arguments: dict[str, int]

    registry = ToolRegistry([add])

    result = execute_openai_tool_call(FunctionCall("add", {"a": 2, "b": 3}), registry)

    assert result.ok is True
    assert result.output == 5


def test_parses_json_string_arguments() -> None:
    registry = ToolRegistry([add])

    result = execute_openai_tool_call(
        {"name": "add", "arguments": '{"a": 2, "b": 3}'},
        registry,
    )

    assert result.ok is True
    assert result.output == 5


def test_returns_failure_for_invalid_json_arguments() -> None:
    registry = ToolRegistry([add])

    result = execute_openai_tool_call(
        {"name": "add", "arguments": '{"a": 2,'},
        registry,
    )

    assert result.ok is False
    assert result.tool_name == "add"
    assert result.error_type == "ToolValidationError"
    assert "not valid JSON" in str(result.error)


def test_returns_failure_for_non_object_arguments() -> None:
    registry = ToolRegistry([add])

    for arguments in (["bad"], "[]", '"bad"'):
        result = execute_openai_tool_call(
            {"name": "add", "arguments": arguments},
            registry,
        )

        assert result.ok is False
        assert result.tool_name == "add"
        assert result.error_type == "ToolValidationError"


def test_returns_failure_for_missing_or_non_string_name() -> None:
    registry = ToolRegistry([add])

    for tool_call in ({"arguments": {"a": 2, "b": 3}}, {"name": 123, "arguments": {}}):
        result = execute_openai_tool_call(tool_call, registry)

        assert result.ok is False
        assert result.tool_name == ""
        assert result.error_type == "ToolValidationError"
