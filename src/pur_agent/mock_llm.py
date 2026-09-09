from __future__ import annotations

import json
from typing import Any


def _ok(payload: Any) -> Any:
    """Unwrap the executor envelope {'ok': bool, 'result'|'error'}."""
    if isinstance(payload, dict) and "ok" in payload:
        return payload.get("result") if payload["ok"] else None
    return payload


def scripted_mock_run(executor: Any | None) -> tuple[str, int]:
    """Deterministic tool follower used by MockLLMClient.

    Returns (final_text, n_rounds). Only tools present in executor.tool_definitions() are
    used, so ablation conditions naturally lose the corresponding fields.
    """
    if executor is None:
        return json.dumps({
            "property_winner": None, "constrained_winner": None, "robust_winner": None,
            "active_constraint": None, "backward_design": None,
            "local_trends": {"nco_direction": "unknown", "composition_axis": None, "composition_direction": "unknown"},
            "evidence": [], "final_reasoning_summary": "mock client without tools cannot reason; abstaining",
            "confidence": 0.0, "abstain": True, "abstention_reason": "mock client has no reasoning capability",
        }), 1

    available = {d["name"] for d in executor.tool_definitions()}
    rounds = 0

    def call(name: str, **args: Any) -> Any:
        nonlocal rounds
        if name not in available:
            return None
        rounds += 1
        return _ok(executor.execute(name, args))

    call("dataset_summary")
    prop = call("rank_property", top_k=5)
    cons = call("rank_constrained", top_k=5)
    rob = call("rank_robust", top_k=5)

    def first_id(r: Any) -> str | None:
        try:
            return str(r["ranking"][0]["cid"])
        except (TypeError, KeyError, IndexError):
            return None

    property_winner = first_id(prop)
    constrained_winner = first_id(cons)
    robust_winner = first_id(rob)
    robust_reason = None if rob is not None else "rank_robust unavailable or robustness not frozen"
    decision_point = robust_winner or constrained_winner

    audit = call("constraint_audit", candidate_id=property_winner) if property_winner else None
    backward = call("solve_backward_threshold", candidate_id=property_winner) if property_winner else None
    reach = call("check_reachability", candidate_id=property_winner) if property_winner else None
    nco = call("local_nco_sweep", candidate_id=decision_point) if decision_point else None
    comp = call("local_composition_sweep", candidate_id=decision_point) if decision_point else None

    active = None
    if audit and audit.get("active_constraint"):
        ac = audit["active_constraint"]
        active = {"name": ac.get("name"), "threshold": ac.get("threshold"), "candidate_value": ac.get("candidate_value"),
                  "evidence": f"constraint_audit failures={audit.get('failures')}"}
    bw = None
    if backward:
        bw = {"variable": backward.get("variable", "nco_oh"), "continuous_threshold": backward.get("continuous_threshold"),
              "nearest_reachable_grid_value": reach.get("nearest_reachable_grid_value") if reach else None,
              "reachable": reach.get("reachable") if reach else None, "active_constraint": backward.get("constraint", "")}
    trends = {
        "nco_direction": (nco or {}).get("eta80_direction_with_increasing_nco", "unknown"),
        "composition_axis": (comp or {}).get("axis_component"),
        "composition_direction": (comp or {}).get("eta80_direction_with_increasing_axis_parts", "unknown"),
        "notes": "mock: directions copied from deterministic sweeps",
    }
    final = {
        "property_winner": property_winner,
        "constrained_winner": constrained_winner,
        "robust_winner": robust_winner,
        "robust_abstention_reason": robust_reason,
        "active_constraint": active,
        "backward_design": bw,
        "local_trends": trends,
        "evidence": [f"tools used: {sorted(available)}"],
        "final_reasoning_summary": "mock scripted run: final fields assembled from deterministic tool outputs only",
        "confidence": 1.0 if all([property_winner, constrained_winner, active, bw]) else 0.5,
        "abstain": False,
        "abstention_reason": None,
    }
    return json.dumps(final), rounds + 1
