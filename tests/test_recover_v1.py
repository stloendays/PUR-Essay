"""Original PUR-RECOVER V1 strategy/tool tests, adapted to the pur_science-backed toolbox."""
import pytest

from pur_agent.strategy import RecoveryStrategy
from pur_agent.tools import DecisionToolbox


def test_complete_trace_gate():
    tools = ["dataset_summary", "rank_property", "rank_constrained", "rank_robust", "constraint_audit", "solve_backward_threshold",
             "check_reachability", "local_nco_sweep", "local_composition_sweep"]
    assert RecoveryStrategy().check_trace(tools).can_finalize


def test_incomplete_trace_blocked():
    check = RecoveryStrategy().check_trace(["rank_property"])
    assert not check.can_finalize and "rank_constrained" in check.missing_tool_families
    assert "rank_constrained" in RecoveryStrategy().corrective_message(check)


def test_unavailable_tools_are_not_required():
    called = ["dataset_summary", "rank_property", "rank_constrained", "rank_robust", "constraint_audit", "local_nco_sweep", "local_composition_sweep"]
    available = set(called)
    assert RecoveryStrategy().check_trace(called, available_tools=available).can_finalize
    assert not RecoveryStrategy().check_trace(called).can_finalize


def test_property_and_constraint_separate(toy_table, toy_config):
    tb = DecisionToolbox(toy_table, toy_config)
    prop = tb.rank_property(1)["ranking"][0]
    cons = tb.rank_constrained(10)
    assert prop["cid"] != cons["ranking"][0]["cid"]
    assert cons["n_feasible"] < cons["n_total"]
    assert all(r["feasible_nominal"] for r in cons["ranking"])


def test_constraint_audit_exposes_failure(toy_table, toy_config):
    tb = DecisionToolbox(toy_table, toy_config)
    pw = tb.rank_property(1)["ranking"][0]["cid"]
    audit = tb.constraint_audit(pw)
    assert "mdi_fraction" in audit["failures"] and audit["feasible"] is False
    assert audit["active_constraint"]["name"] == "mdi_fraction"
    assert audit["checks"]["mdi_fraction"]["bounds"] == [0.35, 0.49]


def test_backward_threshold_and_projection(toy_table, toy_config):
    tb = DecisionToolbox(toy_table, toy_config)
    pw = tb.rank_property(1)["ranking"][0]["cid"]
    out = tb.solve_backward_threshold(pw)
    reach = tb.check_reachability(pw)
    assert 1.7 < out["continuous_threshold"] < 1.8
    assert reach["reachable"] is True and reach["nearest_reachable_grid_value"] == 1.8


def test_robustness_requires_frozen_definition(toy_table, toy_config):
    toy_config["robustness"]["enabled"] = False
    with pytest.raises(RuntimeError):
        DecisionToolbox(toy_table, toy_config).rank_robust()


def test_sweeps_report_directions(toy_table, toy_config):
    tb = DecisionToolbox(toy_table, toy_config)
    rw = tb.rank_robust(1)["ranking"][0]["cid"]
    assert tb.local_nco_sweep(rw)["eta80_direction_with_increasing_nco"] == "decrease"
    comp = tb.local_composition_sweep(rw)
    assert comp["axis_component"] == "X" and comp["eta80_direction_with_increasing_axis_parts"] == "increase"
    assert tb.calculate_mdi_fraction(55.30525)["mdi_fraction"] == pytest.approx(0.3561067639)
