from __future__ import annotations

import math
from typing import Any

EXPLANATION_ITEMS = ("active_constraint", "backward_threshold", "reachable_grid", "reachability", "nco_direction", "composition_direction")


def _same(a: Any, b: Any) -> bool:
    return a is not None and b is not None and str(a) == str(b)


def _within(a: Any, b: Any, tol: float) -> bool:
    try:
        return math.isfinite(float(a)) and math.isfinite(float(b)) and abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


_OPPOSITE = {"increase": "decrease", "decrease": "increase", "flat": "flat", "mixed": "mixed", "unknown": "unknown"}


def composition_direction_matches(agent_lt: dict[str, Any], gold_lt: dict[str, Any]) -> bool:
    """Direction is scored relative to the axis the Agent names.

    If the Agent names the other component of the same two-component family, the direction is
    flipped before comparison. If the Agent names no axis, the gold axis is assumed.
    """
    g_dir = gold_lt.get("composition_direction")
    a_dir = agent_lt.get("composition_direction")
    if g_dir is None or a_dir is None:
        return False
    axis = agent_lt.get("composition_axis")
    g_axis = gold_lt.get("composition_axis")
    g_other = gold_lt.get("composition_other_component")
    if axis is None or _same(axis, g_axis) or (g_axis and str(axis).startswith(str(g_axis))):
        return _same(a_dir, g_dir)
    if g_other and (_same(axis, g_other) or str(axis).startswith(str(g_other))):
        return _same(_OPPOSITE.get(a_dir), g_dir)
    return False


def score_decision(agent: dict[str, Any], gold: dict[str, Any], *, backward_tolerance: float = 0.03, top_k: tuple[int, ...] = (1, 3, 5)) -> dict[str, Any]:
    """All benchmark metrics for one run. `agent` must already be in gold (source) ID space.

    Requires `gold["rankings"]` (ordered ID lists) and `gold["scores"]` (per-candidate scores and
    feasibility) as written by the FRONTIER V1 freeze.
    """
    rank = gold.get("rankings", {})
    scores = gold.get("scores", {})
    robust_frozen = bool(gold.get("robust_layer_frozen")) and bool(rank.get("robust_order"))
    decision_key = "robust_winner" if robust_frozen else "constrained_winner"
    order = rank.get("robust_order") if robust_frozen else rank.get("nominal_order", [])
    score_key = "robust_score" if robust_frozen else "property_score"
    feas_key = "feasible_robust" if robust_frozen else "feasible_nominal"

    agent_choice = agent.get(decision_key)
    gold_choice = gold.get(decision_key)
    oracle_rank = (order.index(agent_choice) + 1) if agent_choice in order else None
    topk = {f"top{k}_recovery": (oracle_rank is not None and oracle_rank <= k) for k in top_k}

    regret = None
    if agent_choice in scores and gold_choice in scores:
        a, g = scores[agent_choice].get(score_key), scores[gold_choice].get(score_key)
        if a is not None and g is not None:
            regret = float(a) - float(g)

    violations = 0
    checked = 0
    for key, fk in (("constrained_winner", "feasible_nominal"), ("robust_winner", feas_key)):
        cid = agent.get(key)
        if cid is None:
            continue
        checked += 1
        if cid not in scores or not scores[cid].get(fk, False):
            violations += 1
    violation_rate = (violations / checked) if checked else None

    ac_a = agent.get("active_constraint") or {}
    ac_g = gold.get("active_constraint") or {}
    bw_a = agent.get("backward_design") or {}
    bw_g = gold.get("backward_design") or {}
    lt_a = agent.get("local_trends") or {}
    lt_g = gold.get("local_trends") or {}

    # V1 answers name the active constraint in `name`, V2 answers in the canonical `quantity`.
    # This reads the same field under either key; it does NOT alias the gold's value, so a
    # legacy spelling such as `mdi_fraction_min` still fails this strict check.
    agent_constraint_name = ac_a.get("name") or ac_a.get("quantity")

    parts = {
        "property_winner_recovery": _same(agent.get("property_winner"), gold.get("property_winner")),
        "constrained_winner_recovery": _same(agent.get("constrained_winner"), gold.get("constrained_winner")),
        "robust_winner_recovery": (_same(agent.get("robust_winner"), gold.get("robust_winner")) if robust_frozen
                                    else agent.get("robust_winner") is None),
        "active_constraint_recovery": _same(agent_constraint_name, ac_g.get("name")),
        "backward_threshold_recovery": _within(bw_a.get("continuous_threshold"), bw_g.get("continuous_threshold"), backward_tolerance),
        "reachable_grid_recovery": _within(bw_a.get("nearest_reachable_grid_value"), bw_g.get("nearest_reachable_grid_value"), 1e-9),
        "reachability_recovery": bw_a.get("reachable") is not None and bw_a.get("reachable") is bw_g.get("reachable"),
        "nco_direction_recovery": _same(lt_a.get("nco_direction"), lt_g.get("nco_direction")),
        "composition_direction_recovery": composition_direction_matches(lt_a, lt_g),
    }
    backward_error = None
    try:
        backward_error = abs(float(bw_a.get("continuous_threshold")) - float(bw_g.get("continuous_threshold")))
    except (TypeError, ValueError):
        pass
    fidelity_items = [parts["active_constraint_recovery"], parts["backward_threshold_recovery"], parts["reachable_grid_recovery"],
                      parts["reachability_recovery"], parts["nco_direction_recovery"], parts["composition_direction_recovery"]]
    winner_ok = parts["property_winner_recovery"] and parts["constrained_winner_recovery"] and parts["robust_winner_recovery"]
    complete = bool(winner_ok and all(fidelity_items) and not agent.get("abstain", False))
    return {
        **parts,
        **topk,
        "oracle_rank": oracle_rank,
        "objective_regret": regret,
        "hard_constraint_violation_rate": violation_rate,
        "backward_threshold_error": backward_error,
        "explanation_fidelity": sum(bool(x) for x in fidelity_items) / len(fidelity_items),
        "abstained": bool(agent.get("abstain", False)),
        "complete_decision_recovery": complete,
        "decision_layer_scored": decision_key,
    }


# ------------------------------------------------------------------ PUR-RECOVER V2 metrics
# The primary metric above is unchanged and is applied identically to V1 and V2 runs. What
# follows is additive. `scientific_correctness` and `schema_correctness` split what the V1
# pilot conflated: a run that named the active constraint `mdi_fraction_min` was
# scientifically right and schema-wrong, and the two are counted separately here rather than
# the frozen gold being aliased after the fact.

SCIENTIFIC_ITEMS = ("property_winner_recovery", "constrained_winner_recovery", "robust_winner_recovery",
                    "active_constraint_science", "backward_threshold_recovery", "reachable_grid_recovery",
                    "reachability_recovery", "nco_direction_recovery", "composition_direction_recovery")


def score_decision_v2(
    agent: dict[str, Any],
    gold: dict[str, Any],
    *,
    certificate: dict[str, Any] | None = None,
    backward_tolerance: float = 0.03,
    top_k: tuple[int, ...] = (1, 3, 5),
    pricing: dict[str, Any] | None = None,
    usage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """V1 metrics plus the V2 diagnostics. `agent` must already be in gold (source) ID space."""
    from .ontology import is_canonical_spelling, same_constraint

    m = score_decision(agent, gold, backward_tolerance=backward_tolerance, top_k=top_k)
    ac_a = agent.get("active_constraint") or {}
    ac_g = gold.get("active_constraint") or {}
    agent_name = ac_a.get("quantity") or ac_a.get("name")

    # Same constraint by meaning (a registered alias counts) vs. same constraint by spelling.
    m["active_constraint_science"] = bool(same_constraint(agent_name, ac_g.get("name")))
    m["active_constraint_schema"] = bool(agent_name is not None and is_canonical_spelling(agent_name))
    m["scientific_correctness"] = bool(all(m[k] for k in SCIENTIFIC_ITEMS) and not agent.get("abstain", False))
    m["ontology_alias_used"] = bool(m["active_constraint_science"] and not m["active_constraint_schema"])

    cert = certificate or {}
    cov = cert.get("evidence_coverage") or {}
    required, satisfied = cov.get("required"), cov.get("satisfied")
    m["evidence_coverage_satisfied"] = satisfied
    m["evidence_coverage_required"] = required
    m["evidence_coverage_ratio"] = (satisfied / required) if (required and satisfied is not None) else None
    m["evidence_coverage_complete"] = bool(cov.get("complete")) if cov else None

    cross = cert.get("cross_path") or {}
    m["cross_path_status"] = cross.get("status")
    m["cross_path_agreement"] = bool(cert.get("cross_path_agreement")) if cert else None
    m["cross_path_failure"] = bool(cross.get("conflict")) if cross else None
    m["cross_path_absolute_difference"] = cross.get("absolute_difference")
    m["cross_path_reported_matches_trace"] = cert.get("cross_path_reported_matches_trace")

    m["challenge_completed"] = cert.get("challenge_completed")
    m["tool_contradictions"] = cert.get("tool_contradictions")
    m["certificate_pass"] = cert.get("certificate_pass")
    m["constraint_audit_pass"] = cert.get("constraint_audit_pass")
    m["robustness_audit_pass"] = cert.get("robustness_audit_pass")
    m["ontology_consistency_pass"] = cert.get("ontology_consistency_pass")
    m["active_constraint_margin"] = cert.get("active_constraint_margin")
    m["objective_margin"] = cert.get("objective_margin")

    status = str(agent.get("decision_status") or ("abstain" if agent.get("abstain") else "final"))
    m["decision_status"] = status
    m["abstention_or_conflict"] = status in ("abstain", "conflict")
    m["conflict_surfaced"] = cert.get("conflict_surfaced")
    m["unsurfaced_cross_path_conflict"] = cert.get("unsurfaced_cross_path_conflict")
    m["contradiction_detection"] = _contradiction_detection(agent, cert)

    usage_stats = cert.get("tool_usage") or {}
    m["unnecessary_tool_calls"] = usage_stats.get("unnecessary_calls_excluding_challenge", usage_stats.get("unnecessary_calls"))
    m["redundant_repeat_calls"] = usage_stats.get("redundant_repeat_calls")
    m["evidence_bearing_calls"] = usage_stats.get("evidence_bearing_calls")

    m["schema_correctness"] = bool(
        m["active_constraint_schema"]
        and bool(cert.get("ontology_consistency_pass", False))
        and bool(cert.get("schema_consistency_pass", False))
    )
    m["cost_usd"] = estimate_cost(usage, pricing)
    return m


def _contradiction_detection(agent: dict[str, Any], certificate: dict[str, Any]) -> bool | None:
    """Did the Agent report contradictions if and only if the deterministic check found them?

    None when the challenge tool that produces the deterministic count was never run.
    """
    if not certificate or certificate.get("challenge_completed") is None:
        return None
    actual = certificate.get("tool_contradictions")
    if actual is None:
        return None
    challenge = agent.get("challenge") or {}
    reported = list(agent.get("conflicts") or []) + list(challenge.get("contradictions_found") or [])
    return bool(bool(reported) == bool(actual))


def estimate_cost(usage: dict[str, Any] | None, pricing: dict[str, Any] | None) -> float | None:
    """USD cost when the benchmark config declares per-1k-token prices; None otherwise."""
    if not usage or not pricing:
        return None
    try:
        price_in = float(pricing["input"])
        price_out = float(pricing["output"])
    except (KeyError, TypeError, ValueError):
        return None
    tokens_in = usage.get("input_tokens", usage.get("prompt_tokens")) or 0
    tokens_out = usage.get("output_tokens", usage.get("completion_tokens")) or 0
    return (float(tokens_in) / 1000.0) * price_in + (float(tokens_out) / 1000.0) * price_out
