from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from typing import Any

from agent_tools.core.registry import ToolRegistry
from agent_tools.core.result import ToolResult
from agent_tools.core.tool import Tool

_OPENAI_SCHEMA_KEYS = {
    "type",
    "nullable",
    "required",
    "format",
    "description",
    "properties",
    "items",
    "enum",
}


def to_openai_tool(tool: Tool) -> dict[str, Any]:
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description,
        "parameters": _to_openai_schema(tool.input_schema.model_json_schema()),
    }


def to_openai_tools(tools: Iterable[Tool]) -> list[dict[str, Any]]:
    return [to_openai_tool(tool) for tool in tools]


def execute_openai_tool_call(
    tool_call: Mapping[str, Any] | Any,
    registry: ToolRegistry,
) -> ToolResult:
    name = _read_attr_or_key(tool_call, "name")
    arguments = _read_attr_or_key(tool_call, "arguments", default={})

    if not isinstance(name, str):
        return ToolResult.failure(
            tool_name="",
            error="OpenAI tool call is missing a string name.",
            error_type="ToolValidationError",
        )

    parsed_arguments = _parse_arguments(arguments, tool_name=name)
    if isinstance(parsed_arguments, ToolResult):
        return parsed_arguments

    return registry.run(name, **parsed_arguments)


def _parse_arguments(arguments: Any, *, tool_name: str) -> dict[str, Any] | ToolResult:
    if arguments is None:
        return {}

    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError as exc:
            return ToolResult.failure(
                tool_name=tool_name,
                error=f"OpenAI tool call arguments are not valid JSON: {exc.msg}",
                error_type="ToolValidationError",
            )

    if not isinstance(arguments, Mapping):
        return ToolResult.failure(
            tool_name=tool_name,
            error="OpenAI tool call arguments must be a JSON object.",
            error_type="ToolValidationError",
        )

    return dict(arguments)


def _to_openai_schema(schema: dict[str, Any]) -> dict[str, Any]:
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
        if key not in _OPENAI_SCHEMA_KEYS:
            continue

        if key == "properties":
            cleaned[key] = {
                name: _clean_schema(property_schema, definitions)
                for name, property_schema in item.items()
            }
            continue

        cleaned[key] = _clean_schema(item, definitions)

    return cleaned


def _read_attr_or_key(
    value: Mapping[str, Any] | Any,
    key: str,
    default: Any = None,
) -> Any:
    if isinstance(value, Mapping):
        return value.get(key, default)

    return getattr(value, key, default)
