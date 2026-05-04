# Creating Tools

This guide covers how to add a new tool to `llm-tools-kit`.

## Basic Pattern

Use `@tool` on a normal Python function:

```python
from agent_tools import tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

The decorator infers:

- `name` from the function name
- `description` from the first docstring line
- `input_schema` from the function signature and type hints

## Registering Tools

```python
from agent_tools import ToolRegistry

registry = ToolRegistry([add])
result = registry.run("add", a=2, b=3)
```

## Custom Metadata

You can override metadata at definition time:

```python
@tool(
    name="sum_numbers",
    description="Add a pair of numbers.",
    tags=["math"],
    risk_level="low",
)
def add(a: int, b: int) -> int:
    return a + b
```

Supported `risk_level` values:

- `low`
- `medium`
- `high`

If a tool should require approval explicitly:

```python
@tool(risk_level="high", requires_approval=True)
def delete_record(record_id: str) -> str:
    return record_id
```

## Tool Function Guidelines

Prefer tools that are:

- typed
- deterministic
- narrow in scope
- easy to test

Avoid tools that:

- rely on hidden global state
- silently mutate unrelated files
- mix multiple concerns in one callable

## Error Handling

Raise `ToolExecutionError` for expected runtime failures:

```python
from agent_tools import ToolExecutionError, tool


@tool
def chunk_text(text: str, max_chars: int = 4000) -> list[str]:
    if max_chars < 1:
        raise ToolExecutionError("max_chars must be greater than 0.")
    return [text]
```

This produces cleaner `ToolResult` failures when run through the registry.

## Context-Aware Tools

If a tool needs execution-time safety settings, read them from `ToolContext`.

File tools already do this using:

- `allowed_directories`
- `max_file_size_bytes`

New tools should only consult context when there is a real runtime safety requirement.

## Testing New Tools

New tools should generally have:

- direct-function tests
- registry execution tests
- failure-path tests

For tools with platform-sensitive behavior, keep assertions portable across Windows and Linux.
