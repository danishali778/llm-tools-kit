from agent_tools import ToolRegistry, tool
from agent_tools.adapters import to_gemini_tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


registry = ToolRegistry([add])
gemini_tool = to_gemini_tool(registry.tools)

print(gemini_tool)
