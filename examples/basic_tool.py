from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_tools import ToolRegistry, tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def main() -> None:
    registry = ToolRegistry()
    registry.register(add)

    result = registry.run("add", a=2, b=3)
    print(result.model_dump())


if __name__ == "__main__":
    main()
