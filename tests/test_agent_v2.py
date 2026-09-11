"""PUR-RECOVER V2: evidence planning, challenge, dual-path verification, ontology, certificate.

The toy fixture from conftest.py is used throughout; it is not PUR_SIM_V1 and carries no
scientific meaning. What is tested here is the V2 contract, not the frozen science.
"""
import json

import pytest

from pur_agent.agent import run_once
from pur_agent.benchmark import run_benchmark
from pur_agent.blind_bundle import build_blind_bundle, verify_no_leakage
from pur_agent.certificate import build_certificate, ontology_check, procedural_gate
from pur_agent.challenge_tools import REQUIRED_CHALLENGE_TOOLS
from pur_agent.conditions import CONDITIONS, get_condition
from pur_agent.crosspath import verify_backward_threshold
from pur_agent.data_access import BlindBundle
from pur_agent.evaluator import evaluate_run_record, load_gold
from pur_agent.evidence import CLAIM_EVIDENCE_PATHS, REQUIRED_CLAIMS, EvidencePlanner
from pur_agent.llm_client import MockLLMClient
from pur_agent.metrics import score_decision, score_decision_v2
from pur_agent.ontology import (
    OntologyError, canonical_constraint, is_canonical_spelling, normalize_quantity, same_constraint,
)
from pur_agent.runtime import ALL_TOOL_NAMES, CHALLENGE_TOOL_NAMES, V2_TOOL_NAMES
from pur_agent.schemas import DecisionSchemaError, parse_decision, parse_decision_v2
from pur_agent.tools_v2 import V2Toolbox

V2_CONDITIONS = ("pur_agent_v2", "pur_agent_v2_no_evidence_planner", "pur_agent_v2_no_challenge",
                 "pur_agent_v2_no_cross_path", "pur_agent_v2_no_certificate")
V1_CONDITIONS = ("oracle", "direct_llm", "tool_llm", "pur_agent", "pur_agent_no_backward",
                 "pur_agent_no_constraint_checker", "pur_agent_no_provenance", "pur_agent_single_pass")


@pytest.fixture
def v2_config(toy_config):
    cfg = dict(toy_config)
    cfg["benchmark_id"] = "TEST_RECOVER_V2"
    cfg["evaluation"] = {**cfg["evaluation"], "cross_path_tolerance_nco_oh": 1e-6}
    return cfg


@pytest.fixture
def v2_bench(tmp_path, toy_csv, v2_config):
    blind, ev = tmp_path / "v2" / "blind", tmp_path / "v2" / "evaluator_only"
    build_blind_bundle(toy_csv, v2_config, blind, ev, seed=7)
    gold = load_gold(ev / "gold_decision.json")
    mapping = json.loads((ev / "gold_mapping.json").read_text())
    return BlindBundle.load(blind), gold, mapping, blind, ev


def _run(bench, condition, client=None):
    bundle, gold, mapping, _, _ = bench
    rec = run_once(bundle, CONDITIONS[condition], client or MockLLMClient(), seed=1)
    return rec, evaluate_run_record(rec, gold, mapping)


# ------------------------------------------------------------------- 1. evidence planner
def test_every_required_claim_has_at_least_one_evidence_path():
    assert set(REQUIRED_CLAIMS) == set(CLAIM_EVIDENCE_PATHS)
    assert len(REQUIRED_CLAIMS) == 9
    for claim, paths in CLAIM_EVIDENCE_PATHS.items():
        assert paths, claim
        for path in paths:
            assert set(path).issubset(set(ALL_TOOL_NAMES)), (claim, path)


def test_planner_scores_minimum_sufficient_evidence_not_a_tool_checklist():
    planner = EvidencePlanner()
    minimal = ["rank_property", "rank_constrained", "rank_robust", "constraint_audit",
               "solve_backward_threshold", "check_reachability", "local_nco_sweep", "local_composition_sweep"]
    cov = planner.coverage(minimal, ALL_TOOL_NAMES)
    assert cov.complete and cov.satisfied == cov.required == 9
    # dataset_summary is never called above, so a V1-style "call everything" checklist would fail
    assert "dataset_summary" not in cov.used_evidence_tools()

    partial = planner.coverage(["rank_property"], ALL_TOOL_NAMES)
    assert not partial.complete and "robust_winner" in partial.missing_claims
    assert "rank_robust" in partial.missing_tools()


def test_plan_is_machine_readable_and_marks_dual_path_claims():
    plan = EvidencePlanner().plan(ALL_TOOL_NAMES)
    claims = {c["claim"]: c for c in plan["claims"]}
    assert plan["n_admissible_claims"] == 9
    assert claims["backward_threshold"]["dual_path_checked"] is True
    assert claims["property_winner"]["dual_path_checked"] is False
    assert claims["backward_threshold"]["minimum_sufficient_tools"] == ["solve_backward_threshold"]


# --------------------------------------------------------------- 2. alternative evidence path
def test_backward_threshold_is_satisfiable_without_the_backward_tool():
    """The pilot's no_backward ablation recovered the threshold this way; it is not an accident."""
    planner = EvidencePlanner()
    available = [t for t in ALL_TOOL_NAMES if t not in ("solve_backward_threshold", "check_reachability")]
    called = ["rank_property", "rank_constrained", "rank_robust", "constraint_audit",
              "local_nco_sweep", "calculate_mdi_fraction", "local_composition_sweep"]
    cov = planner.coverage(called, available)
    backward = next(c for c in cov.claims if c.claim == "backward_threshold")
    assert backward.satisfied and backward.satisfied_path == ("local_nco_sweep", "calculate_mdi_fraction")
    assert cov.complete


def test_active_constraint_has_an_alternative_derivation():
    cov = EvidencePlanner().coverage(["inspect_candidate", "dataset_summary"], ALL_TOOL_NAMES)
    active = next(c for c in cov.claims if c.claim == "active_constraint")
    assert active.satisfied and active.satisfied_path == ("inspect_candidate", "dataset_summary")


def test_ablated_claims_are_unsatisfiable_not_merely_missing():
    available = [t for t in ALL_TOOL_NAMES if t not in ("local_composition_sweep",)]
    cov = EvidencePlanner().coverage(["rank_property"], available)
    assert "composition_direction" in cov.unsatisfiable
    assert "composition_direction" not in cov.missing_claims  # not counted against an ablation
    assert cov.required == 8


# ---------------------------------------------------------------- 3/4. cross-path verification
def test_cross_path_agrees_on_the_two_admissible_derivations(v2_bench):
    rec, _ = _run(v2_bench, "pur_agent_v2")
    cross = rec["decision_certificate"]["cross_path"]
    assert cross["status"] == "agree" and cross["cross_path_verified"] is True
    assert cross["value_a"] == pytest.approx(cross["value_b"], abs=1e-9)
    assert cross["path_b"]["derivation"] == "local_nco_sweep + calculate_mdi_fraction"


def test_forced_cross_path_disagreement_is_reported_as_a_conflict(v2_bench, v2_config):
    """Corrupt Path A in the trace; the deterministic comparison must refuse to pick a winner."""
    rec, _ = _run(v2_bench, "pur_agent_v2")
    trace = json.loads(json.dumps(rec["tool_trace"]))
    for entry in trace:
        if entry["tool"] == "solve_backward_threshold":
            entry["output"]["result"]["continuous_threshold"] = 2.5
    cross = verify_backward_threshold(trace, v2_config, tolerance=1e-6)
    assert cross["status"] == "disagree" and cross["conflict"] is True
    assert cross["cross_path_verified"] is False
    assert cross["absolute_difference"] > 0.5
    assert cross["value_a"] == 2.5 and cross["value_b"] != 2.5  # neither value was silently chosen


def test_single_path_condition_is_not_scored_as_a_disagreement(v2_config):
    trace = [{"tool": "solve_backward_threshold",
              "output": {"ok": True, "result": {"continuous_threshold": 1.8, "blend": "X:50+Y:50"}}}]
    cross = verify_backward_threshold(trace, v2_config, required=False)
    assert cross["status"] == "single_path_only" and cross["conflict"] is False


# ------------------------------------------------------------------- 5. canonical ontology
@pytest.mark.parametrize("alias", ["mdi_fraction_min", "MDI_Fraction_Min", "min_mdi_fraction",
                                   "mdi_fraction_of_polyol_plus_mdi", "mdi fraction", "mdi-fraction"])
def test_known_aliases_normalize_to_one_quantity(alias):
    quantity, _ = normalize_quantity(alias)
    assert quantity == "mdi_fraction"
    assert same_constraint(alias, "mdi_fraction")


def test_only_the_canonical_spelling_counts_as_schema_correct():
    assert is_canonical_spelling("mdi_fraction")
    assert not is_canonical_spelling("mdi_fraction_min")
    assert normalize_quantity("not_a_constraint") == (None, None)


def test_canonical_constraint_object_shape_and_operator_inference():
    assert canonical_constraint("mdi_fraction_min", threshold=0.35) == {
        "quantity": "mdi_fraction", "operator": ">=", "threshold": 0.35}
    # operator inferred from the geometry: the candidate sits below the lower bound
    assert canonical_constraint("mdi_fraction", candidate_value=0.34, bounds=[0.35, 0.49]) == {
        "quantity": "mdi_fraction", "operator": ">=", "threshold": 0.35}
    assert canonical_constraint("mdi_fraction", candidate_value=0.50, bounds=[0.35, 0.49])["operator"] == "<="
    with pytest.raises(OntologyError):
        canonical_constraint("completely_unknown_quantity")


def test_v2_tools_stop_emitting_the_legacy_spelling(toy_table, v2_config):
    """The exact interface defect the pilot hit: the tool used to answer `mdi_fraction_min`."""
    tb = V2Toolbox(toy_table, v2_config)
    pw = tb.rank_property(1)["ranking"][0]["cid"]
    backward = tb.solve_backward_threshold(pw)
    assert backward["constraint"] == "mdi_fraction"
    assert backward["constraint_canonical"] == {"quantity": "mdi_fraction", "operator": ">=", "threshold": 0.35}
    audit = tb.constraint_audit(pw)
    assert audit["active_constraint_canonical"]["quantity"] == "mdi_fraction"
    assert {"quantity": "mdi_fraction", "operator": ">=", "threshold": 0.35} in tb.dataset_summary()["canonical_constraints"]


def test_ontology_check_separates_unknown_from_merely_non_canonical():
    legacy = {"active_constraint": {"name": "mdi_fraction_min", "operator": ">="}}
    result = ontology_check(legacy)
    assert not result["pass"] and result["recognised"] is True
    unknown = ontology_check({"active_constraint": {"quantity": "made_up_thing", "operator": ">="}})
    assert not unknown["pass"] and unknown["recognised"] is False
    clean = ontology_check({"active_constraint": {"quantity": "mdi_fraction", "operator": ">="},
                            "backward_design": {"quantity": "mdi_fraction"}})
    assert clean["pass"] and clean["violations"] == []


# ---------------------------------------------------------------- 6. decision certificate
def test_certificate_is_computed_from_the_trace_not_from_self_reported_confidence(v2_bench):
    rec, metrics = _run(v2_bench, "pur_agent_v2")
    cert = rec["decision_certificate"]
    assert cert["evidence_coverage"]["satisfied"] == cert["evidence_coverage"]["required"] == 9
    assert cert["cross_path_agreement"] and cert["challenge_completed"]
    assert cert["constraint_audit_pass"] and cert["robustness_audit_pass"]
    assert cert["schema_consistency_pass"] and cert["ontology_consistency_pass"]
    assert cert["tool_contradictions"] == 0 and cert["certificate_pass"] is True
    assert metrics["certificate_pass"] is True and metrics["evidence_coverage_ratio"] == 1.0


def test_certificate_fails_when_the_claimed_winner_is_not_feasible(v2_bench, v2_config):
    """Self-consistency, not rank optimality: the certificate never checks 'is this the gold'."""
    bundle, _, _, _, _ = v2_bench
    toolbox = V2Toolbox(bundle.candidates, bundle.config)
    infeasible = toolbox.rank_property(1)["ranking"][0]["cid"]  # property winner fails a nominal gate
    decision = {"property_winner": infeasible, "constrained_winner": infeasible, "robust_winner": None,
                "active_constraint": {"quantity": "mdi_fraction", "operator": ">=", "threshold": 0.35}}
    cert = build_certificate(decision=decision, trace=[], called_tools=[], available_tools=V2_TOOL_NAMES,
                             config=bundle.config, toolbox=toolbox, schema_valid=True)
    assert cert["constraint_audit_pass"] is False and cert["certificate_pass"] is False


def test_certificate_is_recorded_even_when_it_does_not_gate(v2_bench):
    rec, metrics = _run(v2_bench, "pur_agent_v2_no_certificate")
    assert rec["decision_certificate"]["version"] == "PUR_CERTIFICATE_V2"
    assert metrics["certificate_pass"] is not None
    assert rec["strategy_check"]["can_finalize"] is True  # no machine gate in this ablation


# ------------------------------------------------------------------- 7. challenge-stage gate
def test_challenge_stage_blocks_finalization_until_it_has_run(v2_config):
    complete_evidence = ["rank_property", "rank_constrained", "rank_robust", "constraint_audit",
                         "solve_backward_threshold", "check_reachability", "local_nco_sweep",
                         "calculate_mdi_fraction", "local_composition_sweep"]
    gate = procedural_gate(called_tools=complete_evidence, available_tools=V2_TOOL_NAMES,
                           trace=[], config=v2_config)
    assert not gate["can_finalize"] and not gate["challenge_completed"]
    assert any("challenge" in r for r in gate["reasons"])

    gate2 = procedural_gate(called_tools=complete_evidence + list(CHALLENGE_TOOL_NAMES),
                            available_tools=V2_TOOL_NAMES, trace=[], config=v2_config)
    assert gate2["challenge_completed"]
    assert all("challenge" not in r for r in gate2["reasons"])


def test_challenge_is_not_required_when_its_tools_are_ablated(v2_config):
    """The stage is not required, and is reported as not-applicable rather than as completed."""
    available = [t for t in V2_TOOL_NAMES if t not in CHALLENGE_TOOL_NAMES]
    gate = procedural_gate(called_tools=list(ALL_TOOL_NAMES), available_tools=available, trace=[], config=v2_config)
    assert gate["challenge_tools_available"] == []
    assert gate["challenge_applicable"] is False
    assert gate["challenge_completed"] is None  # never True: the challenge did not happen
    assert all("challenge" not in r for r in gate["reasons"])


def test_full_v2_run_executes_every_challenge_tool(v2_bench):
    rec, _ = _run(v2_bench, "pur_agent_v2")
    called = {t["tool"] for t in rec["tool_trace"]}
    assert REQUIRED_CHALLENGE_TOOLS.issubset(called)
    assert rec["final_json"]["challenge"]["l1_to_l2"] in ("worst_case_objective", "robust_admissibility_gate", "identical")


def test_challenge_tools_verify_claims_and_do_not_hand_back_the_chain(toy_table, v2_config):
    tb = V2Toolbox(toy_table, v2_config)
    l0 = tb.rank_property(1)["ranking"][0]["cid"]
    l1 = tb.rank_constrained(1)["ranking"][0]["cid"]
    out = tb.challenge_constraint_relaxation(l0, l1)
    assert out["verdict"].startswith("consistent")
    assert "current_winner" not in out  # the frozen winner is never returned by a challenge tool
    wrong = tb.challenge_constraint_relaxation(l0, l0)
    assert wrong["verdict"].startswith("challenge")

    report = tb.challenge_consistency(l0, l1, active_constraint_quantity="mdi_fraction")
    assert report["claimed_chain"]["property_winner"] == l0
    assert "is " not in report["checks"]["l0_is_global_property_min"]["detail"]  # no answer leaked


def test_challenge_consistency_flags_a_wrong_claimed_chain(toy_table, v2_config):
    tb = V2Toolbox(toy_table, v2_config)
    l0 = tb.rank_property(1)["ranking"][0]["cid"]
    l1 = tb.rank_constrained(1)["ranking"][0]["cid"]
    bad = tb.challenge_consistency(l1, l1, active_constraint_quantity="mdi_fraction")
    assert bad["n_contradictions"] > 0 and "l0_is_global_property_min" in bad["contradictions"]
    good = tb.challenge_consistency(l0, l1, active_constraint_quantity="mdi_fraction")
    assert "l0_is_global_property_min" not in good["contradictions"]


# --------------------------------------------------------- 8. structured conflict / abstention
def test_conflict_status_requires_a_recorded_conflict():
    base = {"property_winner": "Candidate_0001", "constrained_winner": "Candidate_0002",
            "robust_winner": "Candidate_0003",
            "active_constraint": {"quantity": "mdi_fraction", "operator": ">=", "threshold": 0.35},
            "decision_status": "conflict"}
    with pytest.raises(DecisionSchemaError):
        parse_decision_v2(base)
    base["conflicts"] = [{"kind": "cross_path_disagreement", "detail": "paths differ by 0.7"}]
    assert parse_decision_v2(base).decision_status == "conflict"
    base["conflicts"] = [{"kind": "not_a_real_kind"}]
    with pytest.raises(DecisionSchemaError):
        parse_decision_v2(base)


def test_abstention_is_a_valid_structured_outcome():
    parsed = parse_decision_v2({"property_winner": None, "constrained_winner": None, "robust_winner": None,
                                "decision_status": "abstain", "abstain": True,
                                "abstention_reason": "evidence for the robust layer is insufficient"})
    assert parsed.decision_status == "abstain" and parsed.decision.abstain


def test_unsurfaced_cross_path_conflict_fails_the_certificate(v2_bench, v2_config):
    rec, _ = _run(v2_bench, "pur_agent_v2")
    trace = json.loads(json.dumps(rec["tool_trace"]))
    for entry in trace:
        if entry["tool"] == "solve_backward_threshold":
            entry["output"]["result"]["continuous_threshold"] = 2.5
    silent = dict(rec["final_json"], decision_status="final", conflicts=[])
    cert = build_certificate(decision=silent, trace=trace, called_tools=[t["tool"] for t in trace],
                             available_tools=V2_TOOL_NAMES, config=v2_config, schema_valid=True)
    assert cert["unsurfaced_cross_path_conflict"] is True and cert["certificate_pass"] is False

    surfaced = dict(silent, decision_status="conflict",
                    conflicts=[{"kind": "cross_path_disagreement", "detail": "paths disagree"}])
    cert2 = build_certificate(decision=surfaced, trace=trace, called_tools=[t["tool"] for t in trace],
                              available_tools=V2_TOOL_NAMES, config=v2_config, schema_valid=True)
    assert cert2["unsurfaced_cross_path_conflict"] is False and cert2["conflict_surfaced"] is True


# ------------------------------------------------------------------------ 9. no gold leakage
def test_v2_prompts_and_bundle_contain_no_gold(v2_bench, toy_table):
    _, _, _, blind, ev = v2_bench
    gold_texts = [p.read_text(encoding="utf-8") for p in ev.glob("*.json")]
    assert verify_no_leakage(blind, toy_table["source_candidate_id"].tolist(), ["X", "Y"], gold_texts=gold_texts) == []
    from pur_agent.prompts import PROMPT_DIR
    for name in ("recover_v2_system.txt", "recover_v2_task.txt"):
        assert verify_no_leakage(PROMPT_DIR / name if (PROMPT_DIR / name).is_dir() else PROMPT_DIR,
                                 gold_texts=gold_texts) == []


def test_gate_feedback_carries_no_correctness_information(v2_bench):
    """What the gate records (and therefore could say back to the model) is process only."""
    rec, _ = _run(v2_bench, "pur_agent_v2")
    assert rec["gate_attempts"], "the mock must submit its answer to the guard"
    recorded = json.dumps(rec["gate_attempts"])
    for banned in ("certificate_pass", "objective_margin", "active_constraint_margin",
                   "constraint_audit_pass", "robustness_audit_pass", "WO_INV_", "Candidate_"):
        assert banned not in recorded, banned
    assert rec["gate_attempts"][0]["can_finalize"] is True


def test_v2_gate_message_never_names_a_candidate(v2_config):
    from pur_agent.certificate import corrective_message
    gate = procedural_gate(called_tools=["rank_property"], available_tools=V2_TOOL_NAMES, trace=[], config=v2_config)
    message = corrective_message(gate)
    assert "Candidate_" not in message and "WO_INV" not in message
    assert "rank_robust" in message  # it names missing evidence, not answers


# ------------------------------------------------------------- 10. V1 backward compatibility
def test_v1_conditions_are_untouched_and_still_v1():
    for name in V1_CONDITIONS:
        cond = get_condition(name)
        assert cond.schema_version == "v1"
        assert cond.system_prompt in ("recover_v1_system.txt", "direct_llm_system.txt", "tool_llm_system.txt")
        assert not any([cond.require_evidence_plan, cond.require_challenge, cond.require_cross_path,
                        cond.enforce_certificate])


def test_v1_mock_run_still_produces_a_v1_record(v2_bench):
    rec, metrics = _run(v2_bench, "pur_agent")
    assert "decision_certificate" not in rec and "schema_version" not in rec
    assert metrics["complete_decision_recovery"] is True
    assert "scientific_correctness" not in metrics  # V2 diagnostics do not leak into V1 records
    assert rec["strategy_check"]["can_finalize"] is True


def test_v1_answers_still_parse_and_score_unchanged():
    v1_answer = {"property_winner": "A", "constrained_winner": "B", "robust_winner": "C",
                 "active_constraint": {"name": "mdi_fraction", "threshold": 0.35, "candidate_value": 0.34}}
    assert parse_decision(v1_answer).active_constraint.name == "mdi_fraction"
    gold = {"property_winner": "A", "constrained_winner": "B", "robust_winner": "C",
            "active_constraint": {"name": "mdi_fraction"}, "robust_layer_frozen": True,
            "rankings": {"robust_order": ["C"]}, "scores": {"C": {"robust_score": 1.0, "feasible_robust": True}},
            "backward_design": {}, "local_trends": {}}
    assert score_decision(v1_answer, gold)["active_constraint_recovery"] is True


# --------------------------------------------------------------- 11. V2 condition registration
@pytest.mark.parametrize("name", V2_CONDITIONS)
def test_v2_conditions_are_registered_with_the_right_contract(name):
    cond = get_condition(name)
    assert cond.schema_version == "v2"
    assert cond.system_prompt == "recover_v2_system.txt" and cond.task_prompt == "recover_v2_task.txt"
    assert cond.mode == "recover"


def test_each_v2_ablation_removes_exactly_one_part():
    full = get_condition("pur_agent_v2")
    assert all([full.require_evidence_plan, full.require_challenge, full.require_cross_path, full.enforce_certificate])
    assert get_condition("pur_agent_v2_no_evidence_planner").require_evidence_plan is False
    assert get_condition("pur_agent_v2_no_challenge").require_challenge is False
    assert set(get_condition("pur_agent_v2_no_challenge").tools or ()).isdisjoint(CHALLENGE_TOOL_NAMES)
    assert get_condition("pur_agent_v2_no_cross_path").require_cross_path is False
    assert get_condition("pur_agent_v2_no_certificate").enforce_certificate is False


@pytest.mark.parametrize("name", V2_CONDITIONS)
def test_every_v2_condition_runs_end_to_end_on_the_mock(v2_bench, name):
    rec, metrics = _run(v2_bench, name)
    assert rec["decision_valid"] and rec["error"] is None, rec.get("error")
    assert rec["schema_version"] == "v2"
    assert rec["evidence_plan"]["version"] == "PUR_EVIDENCE_V2"
    assert metrics["complete_decision_recovery"] is True, metrics


def test_v2_benchmark_loop_writes_records_and_summary(v2_bench, tmp_path):
    _, _, _, blind, _ = v2_bench
    out = tmp_path / "results" / "pur_agent_v2"
    summary = run_benchmark(blind_dir=blind, condition="pur_agent_v2", provider="mock", model="mock",
                            runs=2, out_dir=out, seed_base=10, progress=False)
    assert summary["n_runs"] == 2 and summary["complete_decision_recovery_rate"] == 1.0
    assert summary["certificate_pass_rate"] == 1.0 and summary["evidence_coverage_ratio_mean"] == 1.0
    assert summary["scientific_correctness_rate"] == 1.0 and summary["schema_correctness_rate"] == 1.0
    assert summary["first_answer_gate_clean_rate"] == 1.0


# ------------------------------------- 12. scientific correctness vs schema correctness split
def _gold_for_split():
    return {"property_winner": "A", "constrained_winner": "B", "robust_winner": "C",
            "active_constraint": {"name": "mdi_fraction"},
            "backward_design": {"continuous_threshold": 1.77, "nearest_reachable_grid_value": 1.8, "reachable": True},
            "local_trends": {"nco_direction": "decrease", "composition_axis": "X", "composition_direction": "increase"},
            "robust_layer_frozen": True, "rankings": {"robust_order": ["C"]},
            "scores": {"C": {"robust_score": 1.0, "feasible_robust": True}, "B": {"feasible_nominal": True}}}


def _answer(constraint_field: dict):
    return {"property_winner": "A", "constrained_winner": "B", "robust_winner": "C",
            "active_constraint": constraint_field,
            "backward_design": {"continuous_threshold": 1.77, "nearest_reachable_grid_value": 1.8, "reachable": True},
            "local_trends": {"nco_direction": "decrease", "composition_axis": "X", "composition_direction": "increase"},
            "decision_status": "final"}


def test_legacy_spelling_is_scientifically_right_and_schema_wrong():
    """This is exactly the pilot's pur_agent_no_constraint_checker outcome, now measured as two things."""
    cert = {"ontology_consistency_pass": False, "schema_consistency_pass": True}
    m = score_decision_v2(_answer({"name": "mdi_fraction_min", "threshold": 0.35}), _gold_for_split(), certificate=cert)
    assert m["active_constraint_science"] is True
    assert m["active_constraint_schema"] is False
    assert m["scientific_correctness"] is True
    assert m["schema_correctness"] is False
    assert m["ontology_alias_used"] is True
    # the strict primary metric is NOT relaxed by the alias
    assert m["active_constraint_recovery"] is False and m["complete_decision_recovery"] is False


def test_canonical_spelling_is_right_on_both_axes():
    cert = {"ontology_consistency_pass": True, "schema_consistency_pass": True}
    m = score_decision_v2(_answer({"quantity": "mdi_fraction", "operator": ">=", "threshold": 0.35}),
                          _gold_for_split(), certificate=cert)
    assert m["scientific_correctness"] and m["schema_correctness"]
    assert m["complete_decision_recovery"] is True and m["ontology_alias_used"] is False


def test_wrong_constraint_fails_both_axes():
    cert = {"ontology_consistency_pass": True, "schema_consistency_pass": True}
    m = score_decision_v2(_answer({"quantity": "nco_oh", "operator": ">=", "threshold": 1.3}),
                          _gold_for_split(), certificate=cert)
    assert m["active_constraint_science"] is False and m["scientific_correctness"] is False


def test_cost_is_none_without_declared_pricing():
    from pur_agent.metrics import estimate_cost
    assert estimate_cost({"input_tokens": 1000, "output_tokens": 500}, None) is None
    assert estimate_cost({"input_tokens": 1000, "output_tokens": 500},
                         {"input": 0.002, "output": 0.008}) == pytest.approx(0.006)
