# llm-tools-kit

A Python toolkit for building safe, reusable tools for LLM agents.

This repository is currently in Phase 1: the core tool system.

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

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

