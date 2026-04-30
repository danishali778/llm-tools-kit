from agent_tools import ToolRegistry, tool


@tool
def divide(a: int, b: int) -> float:
    """Divide two numbers."""
    return a / b


def test_executor_returns_validation_failure_result() -> None:
    registry = ToolRegistry([divide])

    result = registry.run("divide", a="wrong", b=2)

    assert result.ok is False
    assert result.output is None
    assert result.error_type == "ToolValidationError"


def test_executor_returns_missing_tool_failure_result() -> None:
    registry = ToolRegistry()

    result = registry.run("missing", value=1)

    assert result.ok is False
    assert result.error_type == "ToolNotFoundError"


def test_executor_returns_runtime_failure_result() -> None:
    registry = ToolRegistry([divide])

    result = registry.run("divide", a=1, b=0)

    assert result.ok is False
    assert result.error_type == "ZeroDivisionError"

