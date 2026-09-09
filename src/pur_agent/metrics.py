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

    parts = {
        "property_winner_recovery": _same(agent.get("property_winner"), gold.get("property_winner")),
        "constrained_winner_recovery": _same(agent.get("constrained_winner"), gold.get("constrained_winner")),
        "robust_winner_recovery": (_same(agent.get("robust_winner"), gold.get("robust_winner")) if robust_frozen
                                    else agent.get("robust_winner") is None),
        "active_constraint_recovery": _same(ac_a.get("name"), ac_g.get("name")),
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
