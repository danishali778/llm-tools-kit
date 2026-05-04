# Gemini Adapter

`llm-tools-kit` includes a Gemini adapter that converts registered tools into Gemini `functionDeclarations`.

The adapter lives in:

```txt
agent_tools.adapters.gemini
```

## Available Helpers

- `to_gemini_function_declaration(tool)`
- `to_gemini_function_declarations(tools)`
- `to_gemini_tool(tools)`
- `execute_gemini_tool_call(tool_call, registry)`

## Exporting Tool Schemas

Example:

```python
from agent_tools import ToolRegistry, tool
from agent_tools.adapters import to_gemini_tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


registry = ToolRegistry([add])
tool_config = to_gemini_tool(registry.tools)
```

Result shape:

```python
{
    "functionDeclarations": [
        {
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
    ]
}
```

## Executing Tool Calls

The adapter can execute Gemini-style tool call payloads through `ToolRegistry`.

```python
from agent_tools.adapters import execute_gemini_tool_call

result = execute_gemini_tool_call(
    {"name": "add", "args": {"a": 2, "b": 3}},
    registry,
)
```

The helper also accepts objects with `name` and `args` attributes.

## Intentional Scope

This adapter currently:

- exports schemas
- normalizes supported JSON schema fields
- executes Gemini-style tool calls against the registry

It does not currently:

- call the Gemini API
- manage chat history
- handle streaming
- add a Gemini SDK dependency to the package

This is deliberate. The package keeps the provider-specific transport layer separate from the provider-specific schema/export layer.

## Credentials

`.env.example` documents:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`

These are for future live examples and integrations. The current adapter and tests do not require them.
