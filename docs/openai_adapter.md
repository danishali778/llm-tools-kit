# OpenAI Adapter

`llm-tools-kit` includes an OpenAI adapter that converts registered tools into
OpenAI Responses API function tools.

The adapter lives in:

```txt
agent_tools.adapters.openai
```

## Available Helpers

- `to_openai_tool(tool)`
- `to_openai_tools(tools)`
- `execute_openai_tool_call(tool_call, registry)`

## Exporting Tool Schemas

Example:

```python
from agent_tools import ToolRegistry, tool
from agent_tools.adapters import to_openai_tools


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


registry = ToolRegistry([add])
tools = to_openai_tools(registry.tools)
```

Result shape:

```python
[
    {
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
]
```

## Executing Tool Calls

The adapter can execute Responses API function-call payloads through
`ToolRegistry`.

```python
from agent_tools.adapters import execute_openai_tool_call

result = execute_openai_tool_call(
    {
        "type": "function_call",
        "name": "add",
        "arguments": "{\"a\": 2, \"b\": 3}",
    },
    registry,
)
```

The helper also accepts SDK-like objects with `name` and `arguments` attributes.
Arguments may be a JSON string or a mapping.

## Intentional Scope

This adapter currently:

- exports OpenAI Responses API function tool schemas
- normalizes supported JSON schema fields
- executes Responses-style function calls against the registry

It does not currently:

- call the OpenAI API
- manage conversations, retries, or streaming
- add the OpenAI Python SDK as a package dependency
- target Chat Completions tool-call payloads

This is deliberate. The package keeps provider transport code separate from the
schema/export layer.
