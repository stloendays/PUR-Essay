import pandas as pd
import pytest

from pur_agent.anonymization import anonymize_candidate_table
from pur_agent.evaluator import evaluate_decision
from pur_agent.strategy import RecoveryStrategy
from pur_agent.tools import DecisionToolbox


def cfg(robust=True):
    return {
        "polyol_basis_parts": 100,
        "columns": {
            "candidate_id":"source_candidate_id", "blend":"blend", "nco_oh":"nco_oh", "mdi_parts":"mdi_parts",
            "eta80":"eta80", "eta120":"eta120", "ratio":"ratio", "domain_ratio":"domain",
            "uncertainty_radius":"unc", "chemistry_in_domain":"in_domain"
        },
        "hard_constraints": {
            "eta80_preferred_pa_s":[2.2,5.5], "eta120_preferred_pa_s":[0.3,0.6], "ratio_preferred":[7,9.5],
            "nco_oh":[1.3,3.0], "mdi_fraction_of_polyol_plus_mdi":[0.35,0.49], "require_chemistry_in_domain":True
        },
        "objective":{"weights":{"eta80":1,"eta120":1,"ratio":1}},
        "robustness":{"enabled":robust,"domain_reference":1,"domain_weight":0.01,"uncertainty_weight":0.01},
    }


def table():
    return pd.DataFrame([
        ["A","X",1.6,50.0,3.48,.424,8.15,1.0,.05,True],
        ["B","X",1.7,54.0,3.45,.415,8.31,1.1,.06,True],
        ["C","X",1.8,58.0,3.20,.390,8.20,1.0,.04,True],
        ["D","Y",1.7,55.0,4.60,.520,8.85,2.5,.40,True],
    ], columns=["source_candidate_id","blend","nco_oh","mdi_parts","eta80","eta120","ratio","domain","unc","in_domain"])


def test_complete_trace_gate():
    tools=["dataset_summary","rank_property","rank_constrained","rank_robust","constraint_audit","solve_backward_threshold","check_reachability","local_nco_sweep","local_composition_sweep"]
    assert RecoveryStrategy().check_trace(tools).can_finalize


def test_incomplete_trace_blocked():
    assert not RecoveryStrategy().check_trace(["rank_property"]).can_finalize


def test_property_and_constraint_separate():
    tb=DecisionToolbox(table(),cfg())
    assert tb.rank_property(1)["ranking"][0]["source_candidate_id"] == "A"
    constrained=tb.rank_constrained(10)
    assert constrained["n_feasible"] == 3
    assert constrained["ranking"][0]["source_candidate_id"] == "B"


def test_constraint_audit_exposes_failure():
    audit=DecisionToolbox(table(),cfg()).constraint_audit("A")
    assert "mdi_fraction" in audit["failures"]
    assert audit["feasible"] is False


def test_backward_threshold_and_projection():
    out=DecisionToolbox(table(),cfg()).solve_backward_threshold("A")
    assert out["reachable"] is True
    assert 1.6 < out["continuous_threshold"] < 1.7
    assert out["nearest_reachable_grid_value"] == 1.7


def test_robustness_requires_frozen_definition():
    with pytest.raises(RuntimeError):
        DecisionToolbox(table(),cfg(False)).rank_robust()


def test_anonymization_is_deterministic_and_hides_names():
    df=pd.DataFrame({"candidate_id":["WO_1","WO_2"],"blend":["PPG700:50+PPG1000:50"]*2,"PPG700":[50,40],"PPG1000":[50,60],"oracle_rank":[1,2]})
    config={"columns":{"candidate_id":"candidate_id","blend":"blend"},"anonymization":{"component_columns":["PPG700","PPG1000"]},"blind":{"drop_columns":["oracle_rank"]}}
    a=anonymize_candidate_table(df,config,seed=7); b=anonymize_candidate_table(df,config,seed=7)
    assert a.blind_table.equals(b.blind_table)
    text=a.blind_table.to_csv(index=False)
    assert "WO_1" not in text and "PPG700" not in text and "oracle_rank" not in text


def test_complete_decision_recovery_metric():
    gold={
        "property_winner":"A","constrained_winner":"B","robust_winner":"C",
        "active_constraint":{"name":"mdi_fraction_min"},
        "backward_design":{"continuous_threshold":1.772,"nearest_reachable_grid_value":1.8,"reachable":True},
        "local_trends":{"nco_direction":"decrease","composition_direction":"increase"},
    }
    agent={**gold,"backward_design":{"continuous_threshold":1.78,"nearest_reachable_grid_value":1.8,"reachable":True}}
    assert evaluate_decision(agent,gold,backward_tolerance=.03)["complete_decision_recovery"] is True
