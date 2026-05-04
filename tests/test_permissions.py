from agent_tools import ToolContext, ToolRegistry, tool


@tool(risk_level="high", requires_approval=True)
def delete_record(record_id: str) -> str:
    return f"deleted:{record_id}"


@tool(risk_level="medium")
def list_records() -> list[str]:
    return ["one", "two"]


def test_approval_required_tool_fails_without_approval() -> None:
    registry = ToolRegistry([delete_record])

    result = registry.run(
        "delete_record",
        context=ToolContext(),
        record_id="123",
    )

    assert result.ok is False
    assert result.error_type == "ToolExecutionError"
    assert result.error == "Tool 'delete_record' requires explicit approval."


def test_approval_required_tool_runs_when_approved() -> None:
    registry = ToolRegistry([delete_record])

    result = registry.run(
        "delete_record",
        context=ToolContext(approved_tools={"delete_record"}),
        record_id="123",
    )

    assert result.ok is True
    assert result.output == "deleted:123"


def test_context_can_require_approval_for_medium_risk_tools() -> None:
    registry = ToolRegistry([list_records])

    result = registry.run(
        "list_records",
        context=ToolContext(require_approval=True),
    )

    assert result.ok is False
    assert result.error_type == "ToolExecutionError"
    assert result.error == "Tool 'list_records' requires approval under the current execution context."


def test_context_allows_medium_risk_tool_when_approved() -> None:
    registry = ToolRegistry([list_records])

    result = registry.run(
        "list_records",
        context=ToolContext(require_approval=True, approved_tools={"list_records"}),
    )

    assert result.ok is True
    assert result.output == ["one", "two"]
