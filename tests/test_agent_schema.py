import pytest

from pur_agent.schemas import DecisionSchemaError, parse_decision


def _valid():
    return {
        "property_winner": "Candidate_0001", "constrained_winner": "Candidate_0002", "robust_winner": None,
        "robust_abstention_reason": "not frozen",
        "active_constraint": {"name": "mdi_fraction", "threshold": 0.35, "candidate_value": 0.34, "evidence": "audit"},
        "backward_design": {"variable": "nco_oh", "continuous_threshold": 1.77, "nearest_reachable_grid_value": 1.8, "reachable": True, "active_constraint": "mdi_fraction_min"},
        "local_trends": {"nco_direction": "decrease", "composition_axis": "Polyol_B_parts", "composition_direction": "increase", "notes": ""},
        "evidence": ["a", "b"], "final_reasoning_summary": "ok", "confidence": 0.9, "abstain": False, "abstention_reason": None,
    }


def test_valid_decision_parses():
    d = parse_decision(_valid())
    assert d.robust_winner is None and d.backward_design.reachable is True
    assert d.local_trends.composition_axis == "Polyol_B_parts"
    assert d.to_dict()["active_constraint"]["name"] == "mdi_fraction"


def test_invalid_direction_rejected():
    raw = _valid(); raw["local_trends"]["nco_direction"] = "down"
    with pytest.raises(DecisionSchemaError):
        parse_decision(raw)


def test_invalid_reachable_rejected():
    raw = _valid(); raw["backward_design"]["reachable"] = "yes"
    with pytest.raises(DecisionSchemaError):
        parse_decision(raw)


def test_missing_blocks_become_none():
    d = parse_decision({"property_winner": "Candidate_0001"})
    assert d.constrained_winner is None and d.active_constraint is None and d.backward_design is None
    assert d.local_trends.nco_direction == "unknown"


def test_non_object_rejected():
    with pytest.raises(DecisionSchemaError):
        parse_decision(["not", "an", "object"])  # type: ignore[arg-type]
