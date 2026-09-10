"""PUR-AUDIT V1 secondary mode: tools delegate to pur_science.depth, gold is deterministic, mock recovers it."""
import json
from pathlib import Path

import pytest

from pur_agent.agent import run_once
from pur_agent.audit import score_audit
from pur_agent.blind_bundle import build_blind_bundle
from pur_agent.conditions import CONDITIONS
from pur_agent.config import load_benchmark_config
from pur_agent.data_access import BlindBundle
from pur_agent.evaluator import evaluate_run_record, load_gold
from pur_agent.llm_client import MockLLMClient
from pur_agent.strategy import AuditStrategy
from pur_science.dataio import materialize_pur_sim_v1

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def audit_bench(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("audit")
    table = materialize_pur_sim_v1(ROOT / "data" / "pur_sim_v1" / "candidates_full.csv")
    cfg = load_benchmark_config(ROOT / "configs" / "audit_v1.json", repo_root=ROOT)
    build_blind_bundle(table, cfg, tmp / "blind", tmp / "ev", seed=int(cfg["anonymization"]["seed"]))
    return tmp


def test_audit_gold_matches_frozen_depth(audit_bench):
    gold = json.loads((audit_bench / "ev" / "gold_audit.json").read_text())
    depth = json.loads((ROOT / "results" / "frontier_depth_v1" / "summary.json").read_text())
    assert gold["mode"] == "PUR_AUDIT_V1"
    assert gold["layer_divergence"] == {"l0_l1_reason": "mdi_fraction", "l1_l2_mechanism": "worst_case_objective", "uncertainty_bottleneck_response": "ratio"}
    assert gold["uncertainty_counterfactual"]["l1_l2_crossover_scale"] == pytest.approx(depth["uncertainty_scale"]["L1_L2_score_crossover_roots"][0])
    assert gold["constraint_counterfactual"]["winner_if_floor_raised"] is not None
    assert gold["objective_structure"]["principal_weight_ratio"] == pytest.approx(3.0)
    assert gold["stability"]["nominal_winner_weight_fraction"] == pytest.approx(depth["weight_stability"]["nominal_top"][0]["fraction"])
    assert gold["contradictions"] == []
    assert "WO_INV_0420" in gold["pareto_alternatives"]


def test_audit_strategy_requires_counterfactual_tools():
    base = ["dataset_summary", "rank_property", "rank_constrained", "rank_robust", "constraint_audit", "solve_backward_threshold", "check_reachability"]
    assert not AuditStrategy().check_trace(base).can_finalize
    full = base + ["constraint_counterfactual", "uncertainty_counterfactual", "objective_structure_audit", "pareto_alternatives", "weight_stability", "consistency_report"]
    assert AuditStrategy().check_trace(full).can_finalize


def test_mock_audit_run_recovers_audit_gold(audit_bench):
    bundle = BlindBundle.load(audit_bench / "blind")
    rec = run_once(bundle, CONDITIONS["pur_audit"], MockLLMClient(), seed=1)
    assert rec["decision_valid"] and rec["error"] is None and rec["mode"] == "audit"
    assert rec["strategy_check"]["can_finalize"]
    gold = load_gold(audit_bench / "ev" / "gold_decision.json", mode="audit")
    mapping = json.loads((audit_bench / "ev" / "gold_mapping.json").read_text())
    m = evaluate_run_record(rec, gold, mapping)
    assert m["audit_completeness"] is True, m
    assert m["audit_field_recovery"] == 1.0 and m["hypothesis_present"]
    assert rec["final_json"]["pareto_alternatives"][0].startswith("Candidate_")


def test_wrong_audit_is_not_complete(audit_bench):
    gold = json.loads((audit_bench / "ev" / "gold_audit.json").read_text())
    report = {"layer_divergence": {"l0_l1_reason": "nco_oh", "l1_l2_mechanism": "identical"}, "contradictions": ["made_up"], "abstain": False}
    m = score_audit(report, gold)
    assert not m["audit_completeness"] and m["false_contradictions"] == ["made_up"] and m["audit_field_recovery"] < 0.5
