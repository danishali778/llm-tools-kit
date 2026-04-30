import pytest

from agent_tools import ToolRegistry
from agent_tools.tools import extract_json, repair_json


def test_extract_json_from_plain_json_text() -> None:
    assert extract_json('{"name": "Ali", "age": 30}') == {"name": "Ali", "age": 30}


def test_extract_json_from_markdown_code_block() -> None:
    text = """
    Here is the payload:

    ```json
    {"status": "ok", "count": 2}
    ```
    """

    assert extract_json(text) == {"status": "ok", "count": 2}


def test_extract_json_raises_when_no_json_exists() -> None:
    with pytest.raises(Exception, match="No valid JSON object or array"):
        extract_json("No structured data here.")


def test_repair_json_removes_trailing_commas() -> None:
    assert repair_json('{"name": "Ali", "roles": ["admin",],}') == {
        "name": "Ali",
        "roles": ["admin"],
    }


def test_repair_json_accepts_python_style_literals() -> None:
    assert repair_json("{'name': 'Ali', 'active': True}") == {
        "name": "Ali",
        "active": True,
    }


def test_json_tools_run_through_registry() -> None:
    registry = ToolRegistry([extract_json, repair_json])

    result = registry.run("extract_json", text='{"ok": true}')

    assert result.ok is True
    assert result.output == {"ok": True}
