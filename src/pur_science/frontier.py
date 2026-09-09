from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from .backward import solve_backward_threshold
from .canonical import (
    BLEND, CID, DOMAIN_RATIO, ETA80, MDI_FRACTION, MDI_PARTS, NCO, RATIO, ETA120, CanonicalTable,
)
from .objective import (
    BROAD_KEYS, RESPONSES, constraint_bounds, nominal_checks, property_score, robust_checks,
    worst_case_property_score,
)
from .reachability import check_reachability
from .rheology import two_point_activation_energy_kj_mol

# Priority used to name *the* active constraint when several nominal checks fail.
# Interval containment appears here only for backward compatibility with historical configs;
# FRONTIER V1's active config does not use it as a nominal gate.
ACTIVE_CONSTRAINT_PRIORITY = (
    "mdi_fraction", "nco_oh", "chemistry_in_domain", "interval_inside_broad",
    "eta80_broad", "eta120_broad", "ratio_broad", "eta80_preferred", "eta120_preferred", "ratio_preferred",
)


def broad_margin(frame: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    """ORACLE V2 tie-break descriptor: minimum natural-log distance to the nearest broad-window edge."""
    hc = config["hard_constraints"]
    margins = []
    for k, key in BROAD_KEYS.items():
        if key not in hc:
            continue
        lo, hi = [float(x) for x in hc[key]]
        margins.append(np.minimum(np.log(frame[k] / lo), np.log(hi / frame[k])))
    if not margins:
        return pd.Series(np.inf, index=frame.index)
    return pd.concat(margins, axis=1).min(axis=1)


def _ordered(frame: pd.DataFrame, score_col: str, config: dict[str, Any]) -> pd.DataFrame:
    """Deterministic ordering: score, then the frozen tie-break chain."""
    keys = [score_col]
    ascending = [True]
    for rule in config.get("objective", {}).get("tie_break", ["candidate_id_lexicographic"]):
        if rule == "higher_broad_margin":
            keys.append("broad_margin"); ascending.append(False)
        elif rule == "lower_domain_ratio" and DOMAIN_RATIO in frame.columns:
            keys.append(DOMAIN_RATIO); ascending.append(True)
        elif rule == "candidate_id_lexicographic":
            keys.append(CID); ascending.append(True)
    if CID not in keys:
        keys.append(CID); ascending.append(True)
    return frame.sort_values(keys, ascending=ascending, kind="mergesort")


def compute_frontier(table: CanonicalTable, config: dict[str, Any]) -> pd.DataFrame:
    """Score every candidate on the three frontier layers.

    Columns added: property_score, broad_margin, per-check booleans, feasible_nominal,
    property_rank (all candidates), nominal_rank (nominally feasible only) and, when the
    robust layer is enabled and the required columns exist, robust_score, feasible_robust,
    robust_rank.
    """
    f = table.frame.copy()
    f["property_score"] = property_score(f, config)
    f["broad_margin"] = broad_margin(f, config)
    f["ea_two_point_kj_mol"] = [
        two_point_activation_energy_kj_mol(a, b) for a, b in zip(f[ETA80], f[ETA120])
    ]
    checks = nominal_checks(table, config)
    for col in checks.columns:
        f[f"check_{col}"] = checks[col]
    f["feasible_nominal"] = checks.all(axis=1) if len(checks.columns) else True

    ordered = _ordered(f, "property_score", config)
    f.loc[ordered.index, "property_rank"] = np.arange(1, len(ordered) + 1)
    feas = _ordered(f[f["feasible_nominal"]], "property_score", config)
    f["nominal_rank"] = np.nan
    f.loc[feas.index, "nominal_rank"] = np.arange(1, len(feas) + 1)

    r = config.get("robustness") or {}
    if r.get("enabled", False):
        rchecks = robust_checks(table, config)
        for col in rchecks.columns:
            f[f"robust_check_{col}"] = rchecks[col]
        f["feasible_robust"] = f["feasible_nominal"] & (rchecks.all(axis=1) if len(rchecks.columns) else True)
        method = r.get("method", "worst_case_interval")
        if method not in {"worst_case_interval", "minimax_worst_case_interval"}:
            raise ValueError(
                f"Unknown robust method {method!r}; FRONTIER V1 supports only the deterministic worst-case interval objective"
            )
        f["robust_score"] = worst_case_property_score(f, config)
        rob = _ordered(f[f["feasible_robust"]], "robust_score", config)
        f["robust_rank"] = np.nan
        f.loc[rob.index, "robust_rank"] = np.arange(1, len(rob) + 1)
    return f


def _winner(frame: pd.DataFrame, rank_col: str) -> str | None:
    hit = frame[frame[rank_col] == 1]
    return None if hit.empty else str(hit.iloc[0][CID])


def _direction(values: np.ndarray, tol: float) -> str:
    d = np.diff(values)
    if len(d) == 0:
        return "unknown"
    rel = d / np.maximum(np.abs(values[:-1]), 1e-300)
    if np.all(np.abs(rel) <= tol):
        return "flat"
    if np.all(rel >= -tol):
        return "increase"
    if np.all(rel <= tol):
        return "decrease"
    return "mixed"


def local_nco_trend(table: CanonicalTable, candidate_id: str, *, response: str = ETA80, tol: float = 1e-9) -> dict[str, Any]:
    """Direction of `response` as NCO:OH increases along the candidate's blend."""
    row = table.row(candidate_id)
    local = table.frame[table.frame[BLEND] == row[BLEND]].sort_values(NCO)
    return {
        "variable": "nco_oh",
        "response": response,
        "blend": str(row[BLEND]),
        "n_points": int(len(local)),
        "direction": _direction(local[response].to_numpy(dtype=float), tol),
        "grid": [float(x) for x in local[NCO]],
        "values": [float(x) for x in local[response]],
    }


def composition_family(table: CanonicalTable, candidate_id: str) -> tuple[list[str], pd.DataFrame]:
    """All candidates at the candidate's NCO:OH whose components are a subset of its blend components."""
    row = table.row(candidate_id)
    comps = [c for c in table.components if float(row[c]) > 0]
    f = table.frame
    same_nco = f[np.isclose(f[NCO].astype(float), float(row[NCO]))]
    others = [c for c in table.components if c not in comps]
    mask = pd.Series(True, index=same_nco.index)
    for c in others:
        mask &= same_nco[c].eq(0.0)
    return comps, same_nco[mask]


def local_composition_trend(table: CanonicalTable, candidate_id: str, *, response: str = ETA80, tol: float = 1e-9) -> dict[str, Any]:
    """Direction of `response` as the parts of the higher-MDI-demand component increase at fixed NCO:OH.

    The axis component is defined from the data alone: within the two-component family, the
    component whose parts raise mdi_parts (higher hydroxyl demand) is the axis. This makes the
    definition identical in named and anonymized tables.
    """
    comps, fam = composition_family(table, candidate_id)
    if len(comps) != 2 or len(fam) < 2:
        return {"variable": "composition", "response": response, "axis_component": comps[0] if comps else None,
                "other_component": None, "direction": "unknown", "n_points": int(len(fam)), "reason": "no two-component family"}
    a, b = comps
    fam = fam.sort_values(a)
    slope = np.polyfit(fam[a].to_numpy(dtype=float), fam[MDI_PARTS].to_numpy(dtype=float), 1)[0]
    axis, other = (a, b) if slope >= 0 else (b, a)
    fam = fam.sort_values(axis)
    return {
        "variable": "composition",
        "response": response,
        "axis_component": axis,
        "other_component": other,
        "axis_definition": "component whose parts increase mdi_parts at fixed NCO:OH (higher hydroxyl demand)",
        "nco_oh": float(fam.iloc[0][NCO]),
        "n_points": int(len(fam)),
        "direction": _direction(fam[response].to_numpy(dtype=float), tol),
        "axis_parts": [float(x) for x in fam[axis]],
        "values": [float(x) for x in fam[response]],
        "candidate_ids": [str(x) for x in fam[CID]],
    }


def active_constraint_for(frame: pd.DataFrame, config: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    row = frame[frame[CID] == candidate_id].iloc[0]
    failures = [c for c in ACTIVE_CONSTRAINT_PRIORITY if f"check_{c}" in frame.columns and not bool(row[f"check_{c}"])]
    if not failures:
        return {"name": "none", "threshold": None, "candidate_value": None, "all_failures": []}
    name = failures[0]
    bounds = constraint_bounds(config)
    value_col = {"mdi_fraction": MDI_FRACTION, "nco_oh": NCO, "eta80_broad": ETA80, "eta80_preferred": ETA80,
                 "eta120_broad": ETA120, "eta120_preferred": ETA120, "ratio_broad": RATIO, "ratio_preferred": RATIO}.get(name)
    value = float(row[value_col]) if value_col else None
    threshold = None
    if name in bounds and value is not None:
        lo, hi = [float(x) for x in bounds[name]]
        threshold = lo if value < lo else hi
    return {"name": name, "threshold": threshold, "candidate_value": value, "all_failures": failures}


def frontier_decision(table: CanonicalTable, config: dict[str, Any], *, top_n: int = 10) -> dict[str, Any]:
    """Complete deterministic decision chain. This is the gold-producing function."""
    f = compute_frontier(table, config)
    bw_cfg = config.get("backward", {})
    threshold = float(config["hard_constraints"]["mdi_fraction_of_polyol_plus_mdi"][0])
    property_winner = _winner(f, "property_rank")
    constrained_winner = _winner(f, "nominal_rank")
    robust_enabled = "robust_rank" in f.columns
    robust_winner = _winner(f, "robust_rank") if robust_enabled else None

    active = active_constraint_for(f, config, property_winner)
    backward = solve_backward_threshold(table, property_winner, threshold=threshold, constraint=bw_cfg.get("constraint", "mdi_fraction_min"))
    reach = check_reachability(table, backward)

    decision_point = robust_winner or constrained_winner
    lt_cfg = config.get("local_trends", {})
    response = lt_cfg.get("response", ETA80)
    nco_trend = local_nco_trend(table, decision_point, response=response)
    comp_trend = local_composition_trend(table, decision_point, response=response)

    def top(rank_col: str) -> list[dict[str, Any]]:
        sub = f[f[rank_col].notna()].sort_values(rank_col).head(top_n)
        cols = [CID, BLEND, NCO, MDI_PARTS, MDI_FRACTION, ETA80, ETA120, RATIO, "property_score"]
        if "robust_score" in f.columns:
            cols.append("robust_score")
        return [{k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in r.items()} for r in sub[cols].to_dict(orient="records")]

    def full_order(rank_col: str) -> list[str]:
        sub = f[f[rank_col].notna()].sort_values(rank_col)
        return [str(x) for x in sub[CID]]

    score_cols = ["property_score", "feasible_nominal", "property_rank", "nominal_rank"]
    if robust_enabled:
        score_cols += ["robust_score", "feasible_robust", "robust_rank"]
    scores: dict[str, dict[str, Any]] = {}
    for rec in f[[CID] + score_cols].to_dict(orient="records"):
        cid = str(rec.pop(CID))
        scores[cid] = {k: (None if (isinstance(v, float) and math.isnan(v)) else (bool(v) if isinstance(v, (bool, np.bool_)) else float(v))) for k, v in rec.items()}

    out: dict[str, Any] = {
        "n_candidates": int(len(f)),
        "n_feasible_nominal": int(f["feasible_nominal"].sum()),
        "n_feasible_robust": int(f["feasible_robust"].sum()) if robust_enabled else None,
        "robust_layer_frozen": robust_enabled,
        "property_winner": property_winner,
        "constrained_winner": constrained_winner,
        "robust_winner": robust_winner,
        "decision_point": decision_point,
        "active_constraint": active,
        "backward_design": {
            **backward.to_dict(),
            "nearest_reachable_grid_value": reach.nearest_reachable_grid_value,
            "nearest_reachable_candidate_id": reach.nearest_reachable_candidate_id,
            "reachable": reach.reachable,
            "grid_values": list(reach.grid_values),
        },
        "local_trends": {
            "nco_direction": nco_trend["direction"],
            "composition_axis": comp_trend.get("axis_component"),
            "composition_other_component": comp_trend.get("other_component"),
            "composition_direction": comp_trend["direction"],
            "response": response,
            "nco_detail": nco_trend,
            "composition_detail": comp_trend,
        },
        "rankings": {
            "property_top": top("property_rank"),
            "nominal_top": top("nominal_rank"),
            "robust_top": top("robust_rank") if robust_enabled else [],
            "property_order": full_order("property_rank"),
            "nominal_order": full_order("nominal_rank"),
            "robust_order": full_order("robust_rank") if robust_enabled else [],
        },
        "scores": scores,
    }
    return out
