import pytest

from agent_tools import Tool, ToolRegistrationError, tool


def test_tool_decorator_creates_tool_from_function() -> None:
    @tool
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    assert isinstance(add, Tool)
    assert add.name == "add"
    assert add.description == "Add two numbers."
    assert add.run(a=2, b=3) == 5


def test_tool_decorator_supports_custom_metadata() -> None:
    @tool(name="sum_numbers", description="Sum numbers.", tags=["math"])
    def add(a: int, b: int) -> int:
        return a + b

    assert add.name == "sum_numbers"
    assert add.description == "Sum numbers."
    assert add.tags == ("math",)


def test_tool_uses_defaults() -> None:
    @tool
    def greet(name: str, punctuation: str = "!") -> str:
        return f"Hello {name}{punctuation}"

    assert greet.run(name="Ali") == "Hello Ali!"


def test_tool_rejects_varargs() -> None:
    with pytest.raises(ToolRegistrationError):

        @tool
        def broken(*args: str) -> str:
            return ",".join(args)

