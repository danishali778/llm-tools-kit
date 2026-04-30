from dataclasses import dataclass
from typing import Literal

from agent_tools import ToolRegistry, tool
from agent_tools.adapters import (
    execute_gemini_tool_call,
    to_gemini_function_declaration,
    to_gemini_function_declarations,
    to_gemini_tool,
)


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def test_converts_tool_to_gemini_function_declaration() -> None:
    declaration = to_gemini_function_declaration(add)

    assert declaration == {
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


def test_converts_multiple_tools_to_gemini_tool_config() -> None:
    declarations = to_gemini_function_declarations([add])
    tool_config = to_gemini_tool([add])

    assert declarations == [to_gemini_function_declaration(add)]
    assert tool_config == {"functionDeclarations": declarations}


def test_preserves_supported_schema_metadata() -> None:
    @tool
    def set_light(level: int, color: Literal["daylight", "warm"]) -> str:
        """Set a light."""
        return f"{color}:{level}"

    declaration = to_gemini_function_declaration(set_light)

    assert declaration["parameters"]["properties"]["color"] == {
        "enum": ["daylight", "warm"],
        "type": "string",
    }


def test_executes_gemini_tool_call_from_mapping() -> None:
    registry = ToolRegistry([add])

    result = execute_gemini_tool_call(
        {"name": "add", "args": {"a": 2, "b": 3}},
        registry,
    )

    assert result.ok is True
    assert result.output == 5


def test_executes_gemini_tool_call_from_object() -> None:
    @dataclass
    class FunctionCall:
        name: str
        args: dict[str, int]

    registry = ToolRegistry([add])

    result = execute_gemini_tool_call(FunctionCall("add", {"a": 2, "b": 3}), registry)

    assert result.ok is True
    assert result.output == 5


def test_returns_failure_for_invalid_tool_call_args() -> None:
    registry = ToolRegistry([add])

    result = execute_gemini_tool_call({"name": "add", "args": ["bad"]}, registry)

    assert result.ok is False
    assert result.error_type == "ToolValidationError"
