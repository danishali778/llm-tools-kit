from agent_tools import ToolRegistry
from agent_tools.tools import detect_secrets, redact_secrets


def test_detect_secrets_finds_supported_token_types() -> None:
    text = (
        "OpenAI sk-test_1234567890abcdefghijklmnop and "
        "GitHub ghp_1234567890abcdefghijklmnopqrstuvwx and "
        "Gemini AIzaSyD12345678901234567890123456789"
    )

    findings = detect_secrets(text)

    assert [item["type"] for item in findings] == ["openai", "github", "gemini"]


def test_redact_secrets_replaces_matches() -> None:
    text = "token sk-test_1234567890abcdefghijklmnop should be hidden"

    assert redact_secrets(text) == "token [REDACTED:openai] should be hidden"


def test_redaction_tools_run_through_registry() -> None:
    registry = ToolRegistry([redact_secrets])

    result = registry.run(
        "redact_secrets",
        text="ghp_1234567890abcdefghijklmnopqrstuvwx",
    )

    assert result.ok is True
    assert result.output == "[REDACTED:github]"
