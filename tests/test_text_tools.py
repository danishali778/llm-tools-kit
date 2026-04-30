import pytest

from agent_tools import ToolRegistry
from agent_tools.tools import chunk_text


def test_chunk_text_returns_single_chunk_for_short_text() -> None:
    assert chunk_text("short text", max_chars=20) == ["short text"]


def test_chunk_text_splits_text_without_exceeding_limit() -> None:
    chunks = chunk_text("alpha beta gamma delta", max_chars=10)

    assert chunks == ["alpha beta", "gamma", "delta"]
    assert all(len(chunk) <= 10 for chunk in chunks)


def test_chunk_text_hard_splits_long_tokens() -> None:
    assert chunk_text("abcdefghij", max_chars=4) == ["abcd", "efgh", "ij"]


def test_chunk_text_rejects_invalid_max_chars() -> None:
    with pytest.raises(Exception, match="greater than 0"):
        chunk_text("text", max_chars=0)


def test_chunk_text_runs_through_registry() -> None:
    registry = ToolRegistry([chunk_text])

    result = registry.run("chunk_text", text="alpha beta gamma", max_chars=7)

    assert result.ok is True
    assert result.output == ["alpha", "beta", "gamma"]
