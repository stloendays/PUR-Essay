from __future__ import annotations

import math
from typing import Any


def _same(a: Any, b: Any) -> bool:
    return a is not None and b is not None and str(a) == str(b)


def _within(a: Any, b: Any, tol: float) -> bool:
    try:
        return math.isfinite(float(a)) and math.isfinite(float(b)) and abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def evaluate_decision(agent: dict[str, Any], gold: dict[str, Any], *, backward_tolerance: float = 0.03) -> dict[str, Any]:
    property_ok = _same(agent.get("property_winner"), gold.get("property_winner"))
    constrained_ok = _same(agent.get("constrained_winner"), gold.get("constrained_winner"))
    robust_ok = _same(agent.get("robust_winner"), gold.get("robust_winner"))
    ac_a = agent.get("active_constraint") or {}; ac_g = gold.get("active_constraint") or {}
    constraint_ok = _same(ac_a.get("name"), ac_g.get("name"))
    bw_a = agent.get("backward_design") or {}; bw_g = gold.get("backward_design") or {}
    threshold_ok = _within(bw_a.get("continuous_threshold"), bw_g.get("continuous_threshold"), backward_tolerance)
    grid_ok = _same(bw_a.get("nearest_reachable_grid_value"), bw_g.get("nearest_reachable_grid_value"))
    reachable_ok = bw_a.get("reachable") is bw_g.get("reachable")
    lt_a = agent.get("local_trends") or {}; lt_g = gold.get("local_trends") or {}
    nco_ok = _same(lt_a.get("nco_direction"), lt_g.get("nco_direction"))
    composition_ok = _same(lt_a.get("composition_direction"), lt_g.get("composition_direction"))
    complete = all([property_ok, constrained_ok, robust_ok, constraint_ok, threshold_ok, grid_ok, reachable_ok, nco_ok, composition_ok])
    return {
        "property_winner_recovery": property_ok,
        "constrained_winner_recovery": constrained_ok,
        "robust_winner_recovery": robust_ok,
        "active_constraint_recovery": constraint_ok,
        "backward_threshold_recovery": threshold_ok,
        "reachable_grid_recovery": grid_ok,
        "reachability_recovery": reachable_ok,
        "nco_direction_recovery": nco_ok,
        "composition_direction_recovery": composition_ok,
        "complete_decision_recovery": complete,
    }
