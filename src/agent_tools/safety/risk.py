from __future__ import annotations

from agent_tools.core.errors import ToolRegistrationError

RISK_LEVELS = ("low", "medium", "high")


def normalize_risk_level(risk_level: str) -> str:
    normalized = risk_level.strip().lower()
    if normalized not in RISK_LEVELS:
        raise ToolRegistrationError(
            f"Unsupported risk level '{risk_level}'. Expected one of: {', '.join(RISK_LEVELS)}."
        )
    return normalized


def risk_rank(risk_level: str) -> int:
    return RISK_LEVELS.index(normalize_risk_level(risk_level))
