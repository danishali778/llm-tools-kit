# llm-tools-kit

A Python toolkit for building safe, reusable tools for LLM agents.

This repository currently includes:

- The core tool system
- A Gemini adapter for function calling
- The first built-in utility tools for JSON extraction/repair and text chunking

## Quickstart

```python
from agent_tools import ToolRegistry, tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


registry = ToolRegistry()
registry.register(add)

result = registry.run("add", a=2, b=3)
print(result.output)
```

## Built-In Tools

```python
from agent_tools import ToolRegistry
from agent_tools.tools import chunk_text, extract_json

registry = ToolRegistry([extract_json, chunk_text])

payload = registry.run("extract_json", text='Result: {"ok": true}')
chunks = registry.run("chunk_text", text="alpha beta gamma delta", max_chars=10)
```

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

