"""Deterministic tool follower for PUR-RECOVER V2 (mock provider).

Offline stand-in used by CI and dry runs. It walks PLAN -> SOLVE -> CHALLENGE -> CERTIFY ->
EXPLAIN and copies every number out of tool output; it has no reasoning of its own, so an
ablation that removes a tool naturally loses the corresponding field instead of inventing it.
Both admissible derivations of the backward threshold are computed whenever both are
available, which is what makes the dual-path check testable without an API.
"""
from __future__ import annotations

import json
from typing import Any


def _ok(payload: Any) -> Any:
    if isinstance(payload, dict) and "ok" in payload:
        return payload.get("result") if payload["ok"] else None
    return payload


def scripted_v2_run(executor: Any, available: set[str]) -> tuple[str, int]:
    rounds = 0

    def call(name: str, **args: Any) -> Any:
        nonlocal rounds
        if name not in available:
            return None
        rounds += 1
        return _ok(executor.execute(name, args))

    def first_id(result: Any) -> str | None:
        try:
            return str(result["ranking"][0]["cid"])
        except (TypeError, KeyError, IndexError):
            return None

    # -- SOLVE -------------------------------------------------------------------------------
    summary = call("dataset_summary")
    prop = call("rank_property", top_k=5)
    cons = call("rank_constrained", top_k=5)
    rob = call("rank_robust", top_k=5)
    property_winner = first_id(prop)
    constrained_winner = first_id(cons)
    robust_winner = first_id(rob)
    robust_reason = None if rob is not None else "rank_robust unavailable or robustness not frozen"
    decision_point = robust_winner or constrained_winner

    audit = call("constraint_audit", candidate_id=property_winner) if property_winner else None
    backward = call("solve_backward_threshold", candidate_id=property_winner) if property_winner else None
    reach = call("check_reachability", candidate_id=property_winner) if property_winner else None
    nco = call("local_nco_sweep", candidate_id=property_winner) if property_winner else None

    floor = None
    for item in (summary or {}).get("canonical_constraints", []):
        if item.get("quantity") == "mdi_fraction" and item.get("operator") == ">=":
            floor = float(item["threshold"])
            break
    basis = float((summary or {}).get("polyol_basis_parts") or 100.0)
    parts_at_floor = (floor * basis / (1.0 - floor)) if floor is not None else None
    calc = call("calculate_mdi_fraction", mdi_parts=parts_at_floor) if parts_at_floor is not None else None

    nco_dp = nco if (decision_point == property_winner) else (
        call("local_nco_sweep", candidate_id=decision_point) if decision_point else None
    )
    comp = call("local_composition_sweep", candidate_id=decision_point) if decision_point else None

    # -- CERTIFY: two independent derivations of the same frozen quantity --------------------
    value_a = (backward or {}).get("continuous_threshold")
    value_b = None
    if nco and calc:
        rows = [r for r in (nco.get("rows") or []) if r.get("nco_oh")]
        if rows:
            slope = float(rows[0]["mdi_parts"]) / float(rows[0]["nco_oh"])
            value_b = float(calc["mdi_parts"]) / slope

    grid_value = (reach or {}).get("nearest_reachable_grid_value")
    reachable = (reach or {}).get("reachable")
    if grid_value is None and nco and floor is not None:
        usable = sorted(
            (r for r in (nco.get("rows") or [])
             if (r.get("mdi_fraction") or 0.0) >= floor and (value_b is None or float(r["nco_oh"]) >= value_b - 1e-9)),
            key=lambda r: float(r["nco_oh"]),
        )
        if usable:
            grid_value = float(usable[0]["nco_oh"])
            reachable = True

    canonical = None
    if audit:
        canonical = audit.get("active_constraint_canonical") or (audit.get("active_constraint") or {}).get("canonical")
    active = None
    if audit and audit.get("active_constraint"):
        ac = audit["active_constraint"]
        active = {
            "quantity": (canonical or {}).get("quantity") or ac.get("name"),
            "operator": (canonical or {}).get("operator") or ">=",
            "threshold": ac.get("threshold"),
            "candidate_value": ac.get("candidate_value"),
            "evidence": f"constraint_audit failures={audit.get('failures')}",
        }

    # -- CHALLENGE ---------------------------------------------------------------------------
    relax = call("challenge_constraint_relaxation", claimed_property_winner=property_winner,
                 claimed_constrained_winner=constrained_winner) if (property_winner and constrained_winner) else None
    uncertainty = call("challenge_uncertainty", claimed_constrained_winner=constrained_winner,
                       claimed_robust_winner=robust_winner) if (constrained_winner and robust_winner) else None
    boundary = call("challenge_boundary", claimed_robust_winner=decision_point) if decision_point else None
    consistency = None
    if property_winner and constrained_winner:
        consistency = call(
            "challenge_consistency",
            claimed_property_winner=property_winner,
            claimed_constrained_winner=constrained_winner,
            claimed_robust_winner=robust_winner or "",
            active_constraint_quantity=(active or {}).get("quantity") or "mdi_fraction",
            continuous_threshold=(value_a if value_a is not None else (value_b if value_b is not None else 0.0)),
            nearest_reachable_grid_value=(grid_value if grid_value is not None else 0.0),
            nearest_reachable_candidate_id=(reach or {}).get("nearest_reachable_candidate_id") or "",
        )

    policy_config = getattr(getattr(executor, "v2_policy", None), "config", {}) or {}
    tolerance = float((policy_config.get("evaluation") or {}).get("cross_path_tolerance_nco_oh") or 1e-6)
    difference = abs(value_a - value_b) if (value_a is not None and value_b is not None) else None
    verified = bool(difference is not None and difference <= tolerance)

    conflicts: list[dict[str, Any]] = []
    status = "final"
    if difference is not None and difference > tolerance:
        status = "conflict"
        conflicts.append({
            "kind": "cross_path_disagreement",
            "detail": "the dedicated backward primitive and the blend-grid reconstruction disagree beyond the declared tolerance",
            "values": {"value_a": value_a, "value_b": value_b, "absolute_difference": difference, "tolerance": tolerance},
        })
    contradictions = (consistency or {}).get("contradictions", [])
    if contradictions:
        status = "conflict"
        conflicts.append({"kind": "tool_contradiction", "detail": "; ".join(str(c) for c in contradictions)})

    chosen = value_a if value_a is not None else value_b
    final = {
        "property_winner": property_winner,
        "constrained_winner": constrained_winner,
        "robust_winner": robust_winner,
        "robust_abstention_reason": robust_reason,
        "active_constraint": active,
        "backward_design": {
            "variable": "nco_oh",
            "quantity": (active or {}).get("quantity") or "mdi_fraction",
            "operator": ">=",
            "continuous_threshold": chosen,
            "nearest_reachable_grid_value": grid_value,
            "reachable": reachable,
        },
        "local_trends": {
            "nco_direction": (nco_dp or {}).get("eta80_direction_with_increasing_nco", "unknown"),
            "composition_axis": (comp or {}).get("axis_component"),
            "composition_direction": (comp or {}).get("eta80_direction_with_increasing_axis_parts", "unknown"),
            "notes": "mock: directions copied from deterministic sweeps",
        },
        "evidence_plan": [
            {"claim": "property_winner", "evidence": ["rank_property"]},
            {"claim": "constrained_winner", "evidence": ["rank_constrained"]},
            {"claim": "robust_winner", "evidence": ["rank_robust"]},
            {"claim": "active_constraint", "evidence": ["constraint_audit"]},
            {"claim": "backward_threshold", "evidence": ["solve_backward_threshold", "local_nco_sweep", "calculate_mdi_fraction"]},
            {"claim": "reachable_grid", "evidence": ["check_reachability", "local_nco_sweep"]},
            {"claim": "reachability", "evidence": ["check_reachability", "local_nco_sweep"]},
            {"claim": "nco_direction", "evidence": ["local_nco_sweep"]},
            {"claim": "composition_direction", "evidence": ["local_composition_sweep"]},
        ],
        "cross_path_verification": {
            "quantity": "backward_continuous_threshold_nco_oh",
            "value_a": value_a,
            "value_b": value_b,
            "absolute_difference": difference,
            "tolerance": tolerance,
            "cross_path_verified": verified,
            "path_a": "solve_backward_threshold",
            "path_b": "local_nco_sweep + calculate_mdi_fraction",
        },
        "challenge": {
            "l0_to_l1": (relax or {}).get("verdict"),
            "l1_to_l2": (uncertainty or {}).get("mechanism"),
            "boundary": (boundary or {}).get("near_objective_crossover"),
            "contradictions_found": list(contradictions),
        },
        "conflicts": conflicts,
        "certificate_claimed": {
            "evidence_coverage": {"satisfied": None, "required": None},
            "cross_path_agreement": verified,
            "tool_contradictions": len(contradictions),
        },
        "decision_status": status,
        "evidence": [f"tools used: {sorted(available)}"],
        "final_reasoning_summary": (
            "mock scripted V2 run: every field copied from deterministic tool outputs; "
            "both admissible threshold derivations computed independently"
        ),
        "confidence": 1.0 if all([property_winner, constrained_winner, active, chosen is not None]) else 0.5,
        "abstain": False,
        "abstention_reason": None,
    }
    return json.dumps(final), rounds + 1
