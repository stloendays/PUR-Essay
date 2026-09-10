"""PUR-AUDIT V1: evaluator-side gold and scorer for the secondary audit mode.

The audit gold is computed by the same deterministic `pur_science.depth` functions the Agent
tools expose. The Agent is scored on whether it recovered each counterfactual quantity, not on
prose quality. The scientific-hypothesis field is only checked for presence and evidence
citations; its scientific merit is left to human review.
"""
from __future__ import annotations

import json
import math
from typing import Any

import pandas as pd

from pur_science.canonical import CanonicalTable
from pur_science.depth import (
    consistency_report, constraint_counterfactual, objective_structure_audit, pareto_alternatives,
    uncertainty_counterfactual, uncertainty_scale_table, weight_stability,
)
from pur_science.frontier import compute_frontier, frontier_decision

AUDIT_FIELDS = (
    "layer_divergence_l0_l1", "layer_divergence_l1_l2", "uncertainty_bottleneck", "constraint_counterfactual_up",
    "constraint_counterfactual_down", "uncertainty_crossover", "reachability", "objective_double_counting",
    "principal_weight_ratio", "pareto_alternatives", "stability_nominal", "stability_robust",
)


def audit_gold(table: CanonicalTable, config: dict[str, Any]) -> dict[str, Any]:
    f = compute_frontier(table, config)
    d = frontier_decision(table, config)
    a = config.get("audit", {})
    l1, l2 = d["constrained_winner"], d["robust_winner"]
    uc = uncertainty_counterfactual(f, config, l1, l2) if l2 else None
    cc = constraint_counterfactual(f, config, layer="robust" if l2 else "nominal")
    U = uncertainty_scale_table(f, config).set_index("cid")
    bottleneck = str(U.loc[l2, "bottleneck_broad"]) if l2 and l2 in U.index else None
    ws_n = weight_stability(f, config, layer="nominal", samples=int(a.get("weight_samples", 50000)), seed=int(a.get("weight_seed", 20260909)))
    ws_r = weight_stability(f, config, layer="robust", samples=int(a.get("weight_samples", 50000)), seed=int(a.get("weight_seed", 20260909))) if l2 else None
    frac = lambda ws, cid: next((x["fraction"] for x in ws["winner_fractions"] if x["winner"] == cid), 0.0) if ws else None
    par = pareto_alternatives(f, config) if l2 else {"pareto_ids": []}
    obj = objective_structure_audit(config)
    rep = consistency_report(f, config, d)
    return {
        "gold_status": "GOLD",
        "mode": "PUR_AUDIT_V1",
        "layer_divergence": {"l0_l1_reason": d["active_constraint"]["name"], "l1_l2_mechanism": uc["mechanism"] if uc else "not_frozen",
                             "uncertainty_bottleneck_response": bottleneck},
        "constraint_counterfactual": {k: cc[k] for k in ("frozen_floor", "winner_stable_for_floor_in", "floor_increase_to_change_winner",
                                                         "floor_decrease_to_change_winner", "winner_if_floor_raised", "winner_if_floor_lowered")},
        "uncertainty_counterfactual": {"l1_l2_crossover_scale": (uc["crossover"]["crossover_scales"][0] if uc and uc.get("crossover") and uc["crossover"]["crossover_scales"] else None),
                                       "robust_winner_stable_scale_range": uc["robust_winner_stable_for_scale_in"] if uc else None},
        "reachability": {"target_reachable": d["backward_design"]["reachable"], "nearest_reachable_grid_value": d["backward_design"]["nearest_reachable_grid_value"]},
        "objective_structure": {"double_counting": obj["double_counting"], "principal_weight_ratio": obj["principal_weight_ratio"]},
        "pareto_alternatives": par["pareto_ids"],
        "stability": {"nominal_winner_weight_fraction": frac(ws_n, l1), "robust_winner_weight_fraction": frac(ws_r, l2)},
        "contradictions": rep["contradictions"],
        "decision_chain": {k: d[k] for k in ("property_winner", "constrained_winner", "robust_winner")},
    }


def _num(x: Any) -> float | None:
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _within(a: Any, b: Any, tol: float) -> bool:
    a, b = _num(a), _num(b)
    return a is not None and b is not None and abs(a - b) <= tol


def score_audit(report: dict[str, Any], gold: dict[str, Any], *, floor_tol: float = 0.002, scale_tol: float = 0.02, frac_tol: float = 0.05, pareto_min_jaccard: float = 0.6) -> dict[str, Any]:
    """Component recovery of the audit report (IDs must already be in gold ID space)."""
    ld, gld = report.get("layer_divergence") or {}, gold["layer_divergence"]
    cc, gcc = report.get("constraint_counterfactual") or {}, gold["constraint_counterfactual"]
    uc, guc = report.get("uncertainty_counterfactual") or {}, gold["uncertainty_counterfactual"]
    rc, grc = report.get("reachability") or {}, gold["reachability"]
    ob, gob = report.get("objective_structure") or {}, gold["objective_structure"]
    st, gst = report.get("stability") or {}, gold["stability"]
    par = set(str(x) for x in (report.get("pareto_alternatives") or []))
    gpar = set(gold["pareto_alternatives"])
    jacc = (len(par & gpar) / len(par | gpar)) if (par | gpar) else 1.0
    hyp = report.get("hypothesis_to_test") or {}
    contradictions = report.get("contradictions") or []
    m = {
        "layer_divergence_l0_l1": str(ld.get("l0_l1_reason")) == str(gld["l0_l1_reason"]),
        "layer_divergence_l1_l2": str(ld.get("l1_l2_mechanism")) == str(gld["l1_l2_mechanism"]),
        "uncertainty_bottleneck": str(ld.get("uncertainty_bottleneck_response")) == str(gld["uncertainty_bottleneck_response"]),
        "constraint_counterfactual_up": _within(cc.get("floor_increase_to_change_winner"), gcc["floor_increase_to_change_winner"], floor_tol)
                                         and str(cc.get("winner_if_floor_raised")) == str(gcc["winner_if_floor_raised"]),
        "constraint_counterfactual_down": _within(cc.get("floor_decrease_to_change_winner"), gcc["floor_decrease_to_change_winner"], floor_tol),
        "uncertainty_crossover": _within(uc.get("l1_l2_crossover_scale"), guc["l1_l2_crossover_scale"], scale_tol),
        "reachability": rc.get("target_reachable") is grc["target_reachable"] and _within(rc.get("nearest_reachable_grid_value"), grc["nearest_reachable_grid_value"], 1e-9),
        "objective_double_counting": ob.get("double_counting") is gob["double_counting"],
        "principal_weight_ratio": _within(ob.get("principal_weight_ratio"), gob["principal_weight_ratio"], 0.1),
        "pareto_alternatives": jacc >= pareto_min_jaccard and gold["decision_chain"]["robust_winner"] in par,
        "stability_nominal": _within(st.get("nominal_winner_weight_fraction"), gst["nominal_winner_weight_fraction"], frac_tol),
        "stability_robust": _within(st.get("robust_winner_weight_fraction"), gst["robust_winner_weight_fraction"], frac_tol),
    }
    m["pareto_jaccard"] = jacc
    m["hypothesis_present"] = bool(str(hyp.get("statement", "")).strip()) and bool(hyp.get("evidence_sources"))
    m["false_contradictions"] = [c for c in contradictions if c not in gold["contradictions"]]
    m["missed_contradictions"] = [c for c in gold["contradictions"] if c not in contradictions]
    m["abstained"] = bool(report.get("abstain", False))
    m["audit_completeness"] = bool(all(m[k] for k in AUDIT_FIELDS) and not m["false_contradictions"] and not m["missed_contradictions"] and not m["abstained"])
    m["audit_field_recovery"] = sum(bool(m[k]) for k in AUDIT_FIELDS) / len(AUDIT_FIELDS)
    return m


def remap_audit_report(report: dict[str, Any], mapping: dict[str, Any]) -> dict[str, Any]:
    out = json.loads(json.dumps(report))
    rev = mapping.get("candidate_reverse", {})
    cc = out.get("constraint_counterfactual") or {}
    for k in ("winner_if_floor_raised", "winner_if_floor_lowered"):
        if cc.get(k) in rev:
            cc[k] = rev[cc[k]]
    out["pareto_alternatives"] = [rev.get(str(x), str(x)) for x in (out.get("pareto_alternatives") or [])]
    return out
