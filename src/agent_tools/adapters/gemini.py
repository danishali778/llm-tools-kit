from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from agent_tools.core.registry import ToolRegistry
from agent_tools.core.result import ToolResult
from agent_tools.core.tool import Tool

_GEMINI_SCHEMA_KEYS = {
    "type",
    "nullable",
    "required",
    "format",
    "description",
    "properties",
    "items",
    "enum",
}


def to_gemini_function_declaration(tool: Tool) -> dict[str, Any]:
    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": _to_gemini_schema(tool.input_schema.model_json_schema()),
    }


def to_gemini_function_declarations(tools: Iterable[Tool]) -> list[dict[str, Any]]:
    return [to_gemini_function_declaration(tool) for tool in tools]


def to_gemini_tool(tools: Iterable[Tool]) -> dict[str, Any]:
    return {"functionDeclarations": to_gemini_function_declarations(tools)}


def execute_gemini_tool_call(
    tool_call: Mapping[str, Any] | Any,
    registry: ToolRegistry,
) -> ToolResult:
    name = _read_attr_or_key(tool_call, "name")
    args = _read_attr_or_key(tool_call, "args", default={})

    if not isinstance(name, str):
        return ToolResult.failure(
            tool_name="",
            error="Gemini tool call is missing a string name.",
            error_type="ToolValidationError",
        )

    if args is None:
        args = {}

    if not isinstance(args, Mapping):
        return ToolResult.failure(
            tool_name=name,
            error="Gemini tool call args must be a mapping.",
            error_type="ToolValidationError",
        )

    return registry.run(name, **dict(args))


def _to_gemini_schema(schema: dict[str, Any]) -> dict[str, Any]:
    definitions = schema.get("$defs", {})
    return _clean_schema(schema, definitions)


def _clean_schema(value: Any, definitions: Mapping[str, Any]) -> Any:
    if isinstance(value, list):
        return [_clean_schema(item, definitions) for item in value]

    if not isinstance(value, dict):
        return value

    if "$ref" in value:
        ref_name = str(value["$ref"]).split("/")[-1]
        return _clean_schema(definitions.get(ref_name, {}), definitions)

    cleaned: dict[str, Any] = {}
    for key, item in value.items():
        if key not in _GEMINI_SCHEMA_KEYS:
            continue

        if key == "properties":
            cleaned[key] = {
                name: _clean_schema(property_schema, definitions)
                for name, property_schema in item.items()
            }
            continue

        cleaned[key] = _clean_schema(item, definitions)

    return cleaned


def _read_attr_or_key(value: Mapping[str, Any] | Any, key: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(key, default)

    return getattr(value, key, default)
