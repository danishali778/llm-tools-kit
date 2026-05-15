from agent_tools import ToolRegistry, tool
from agent_tools.adapters import to_openai_tools


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


registry = ToolRegistry([add])
openai_tools = to_openai_tools(registry.tools)

print(openai_tools)
