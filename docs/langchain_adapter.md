# LangChain Adapter

`llm-tools-kit` can export local tools and registries as LangChain `StructuredTool` objects using `langchain-core`.

## Installation

Install the optional LangChain extra:

```bash
python -m pip install -e ".[langchain,dev]"
```

## Minimal usage

```python
from agent_tools import ToolRegistry, tool
from agent_tools.integrations import registry_to_langchain_tools


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


registry = ToolRegistry([add])
langchain_tools = registry_to_langchain_tools(registry)

result = langchain_tools[0].invoke({"a": 2, "b": 3})
```

## Available helpers

- `to_langchain_tool(tool, *, context_factory=None, return_direct=False)`
- `to_langchain_tools(tools, *, context_factory=None, return_direct=False)`
- `registry_to_langchain_tools(registry, *, context_factory=None, return_direct=False)`

## Behavior

- local tool name, description, schema, tags, and metadata are preserved
- LangChain invocation routes through `ToolRegistry.run(...)`
- successful `ToolResult` objects are unwrapped into plain tool output
- failed `ToolResult` objects are converted into LangChain-facing tool errors
- context-aware execution is supported through an explicit `context_factory`

## Context bridge

If a tool needs `ToolContext`, provide a `context_factory`:

```python
from agent_tools import ToolContext


def context_factory(tool_name: str, arguments: dict[str, object], metadata: dict[str, object] | None):
    if tool_name == "save_memory" and metadata is not None:
        return ToolContext(allowed_directories=(str(metadata["allowed_directory"]),))
    return None
```

LangChain `invoke(..., config={"metadata": {...}})` metadata is passed through to this function unchanged.

## Scope limits

This slice does not add:

- reverse conversion from LangChain tools into `ToolRegistry`
- agent wrappers or chain helpers
- full `langchain` package dependency
- provider-specific LangChain integrations
