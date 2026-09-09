import copy
import json

from pur_agent.evaluator import evaluate_decision, remap_decision
from pur_agent.metrics import score_decision


def _gold():
    return {
        "robust_layer_frozen": True,
        "property_winner": "A", "constrained_winner": "B", "robust_winner": "C",
        "active_constraint": {"name": "mdi_fraction", "threshold": 0.35, "candidate_value": 0.34},
        "backward_design": {"continuous_threshold": 1.772, "nearest_reachable_grid_value": 1.8, "reachable": True},
        "local_trends": {"nco_direction": "decrease", "composition_axis": "PPG700", "composition_other_component": "PPG1000", "composition_direction": "increase"},
        "rankings": {"robust_order": ["C", "D", "B", "E"], "nominal_order": ["B", "C", "D", "E"]},
        "scores": {"A": {"property_score": 0.0, "feasible_nominal": False, "robust_score": 0.1, "feasible_robust": False},
                   "B": {"property_score": 0.001, "feasible_nominal": True, "robust_score": 0.05, "feasible_robust": True},
                   "C": {"property_score": 0.002, "feasible_nominal": True, "robust_score": 0.01, "feasible_robust": True},
                   "D": {"property_score": 0.003, "feasible_nominal": True, "robust_score": 0.02, "feasible_robust": True},
                   "E": {"property_score": 0.004, "feasible_nominal": True, "robust_score": 0.09, "feasible_robust": True}},
    }


def _agent():
    return {
        "property_winner": "A", "constrained_winner": "B", "robust_winner": "C",
        "active_constraint": {"name": "mdi_fraction"},
        "backward_design": {"continuous_threshold": 1.78, "nearest_reachable_grid_value": 1.8, "reachable": True},
        "local_trends": {"nco_direction": "decrease", "composition_axis": "PPG700", "composition_direction": "increase"},
        "abstain": False,
    }


def test_perfect_run_is_complete():
    m = score_decision(_agent(), _gold())
    assert m["complete_decision_recovery"] and m["top1_recovery"] and m["oracle_rank"] == 1
    assert m["objective_regret"] == 0.0 and m["hard_constraint_violation_rate"] == 0.0
    assert m["explanation_fidelity"] == 1.0 and abs(m["backward_threshold_error"] - 0.008) < 1e-9


def test_lucky_winner_is_not_complete():
    a = _agent(); a["active_constraint"] = {"name": "nco_oh"}; a["backward_design"]["continuous_threshold"] = 1.9
    m = score_decision(a, _gold())
    assert m["top1_recovery"] and m["robust_winner_recovery"]
    assert not m["complete_decision_recovery"]
    assert abs(m["explanation_fidelity"] - 4 / 6) < 1e-9


def test_rank_regret_and_violation():
    a = _agent(); a["robust_winner"] = "D"
    m = score_decision(a, _gold())
    assert m["oracle_rank"] == 2 and m["top1_recovery"] is False and m["top3_recovery"] is True
    assert abs(m["objective_regret"] - 0.01) < 1e-12
    a["constrained_winner"] = "A"  # infeasible pick
    m = score_decision(a, _gold())
    assert m["hard_constraint_violation_rate"] == 0.5


def test_opposite_axis_flips_direction():
    a = _agent(); a["local_trends"] = {"nco_direction": "decrease", "composition_axis": "PPG1000", "composition_direction": "decrease"}
    assert score_decision(a, _gold())["composition_direction_recovery"] is True
    a["local_trends"]["composition_direction"] = "increase"
    assert score_decision(a, _gold())["composition_direction_recovery"] is False


def test_abstention_never_counts_as_complete():
    a = _agent(); a["abstain"] = True
    m = score_decision(a, _gold())
    assert m["abstained"] and not m["complete_decision_recovery"]


def test_robust_not_frozen_requires_null_robust_winner():
    g = _gold(); g["robust_layer_frozen"] = False; g["robust_winner"] = None; g["rankings"]["robust_order"] = []
    a = _agent(); a["robust_winner"] = None
    m = score_decision(a, g)
    assert m["robust_winner_recovery"] and m["decision_layer_scored"] == "constrained_winner" and m["oracle_rank"] == 1
    a["robust_winner"] = "C"
    assert not score_decision(a, g)["robust_winner_recovery"]


def test_remap_ids_and_axis():
    mapping = {"candidate_reverse": {"Candidate_0007": "C", "Candidate_0001": "A"}, "material_reverse": {"Polyol_B": "PPG700"}}
    d = {"property_winner": "Candidate_0001", "constrained_winner": "X", "robust_winner": "Candidate_0007",
         "local_trends": {"composition_axis": "Polyol_B_parts", "composition_direction": "increase"}}
    out = remap_decision(d, mapping)
    assert out["property_winner"] == "A" and out["robust_winner"] == "C" and out["constrained_winner"] == "X"
    assert out["local_trends"]["composition_axis"] == "PPG700_parts"


def test_legacy_component_evaluator_still_works():
    g = _gold(); a = _agent()
    assert evaluate_decision(a, g)["complete_decision_recovery"] is True
