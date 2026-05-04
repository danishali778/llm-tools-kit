from agent_tools.safety import normalize_risk_level, risk_rank


def test_normalize_risk_level_accepts_known_values() -> None:
    assert normalize_risk_level("LOW") == "low"
    assert normalize_risk_level("medium") == "medium"
    assert normalize_risk_level("high") == "high"


def test_risk_rank_orders_levels() -> None:
    assert risk_rank("low") < risk_rank("medium") < risk_rank("high")
