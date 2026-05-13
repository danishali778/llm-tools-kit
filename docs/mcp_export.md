# MCP Export

`llm-tools-kit` can expose a `ToolRegistry` as an MCP server over stdio.

## Installation

Install the optional MCP extra:

```bash
python -m pip install -e ".[mcp,dev]"
```

## Minimal usage

```python
from agent_tools import ToolRegistry
from agent_tools.integrations import serve_mcp
from agent_tools.tools import chunk_text, extract_json


registry = ToolRegistry([chunk_text, extract_json])
serve_mcp(registry, name="llm-tools-kit", version="0.1.0")
```

## Behavior

- existing `ToolRegistry` metadata becomes MCP tool metadata
- MCP-routed tool calls execute through `ToolRegistry.run(...)`
- tool failures are translated into MCP-facing tool errors
- transport is stdio only in this first slice

## Scope limits

This slice does not add:

- HTTP transport
- auth or session management
- LangChain integration helpers beyond the separate `docs/langchain_adapter.md` slice
- external-service requirements in normal tests
