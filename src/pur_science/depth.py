"""Decision-geometry diagnostics on a frozen FRONTIER table (PUR-FRONTIER-DEPTH / PUR-AUDIT V1 tools).

Every function here is deterministic and config-driven. Nothing modifies the frozen
frontier, objective, constraints or gold; the functions only answer counterfactual
questions about the already-computed table:

- at which constraint value does the winner change (constraint phase map);
- at which uncertainty scale does the robust winner change (uncertainty phase map);
- how stable is the winner under objective-weight perturbation;
- which candidates are Pareto-alternatives;
- does the objective double-count (eta80 = eta120 * ratio);
- is the frozen decision chain internally consistent.

All outputs are algorithmic properties of the synthetic PUR_SIM_V1 space.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from .canonical import BLEND, CID, DOMAIN_RATIO, ETA120, ETA80, MDI_FRACTION, NCO, RATIO, UNC_RADIUS
from .objective import BROAD_KEYS, PREFERRED_KEYS, RESPONSES, objective_centers, objective_weights, uncertainty_radius_multipliers


# ----------------------------------------------------------------------------------------- helpers
def _bounds(config: dict[str, Any], keys: dict[str, str]) -> dict[str, tuple[float, float]]:
    hc = config["hard_constraints"]
    return {k: (float(hc[key][0]), float(hc[key][1])) for k, key in keys.items() if key in hc}


def _nominal_gate_columns(frontier: pd.DataFrame, exclude: str = "check_mdi_fraction") -> list[str]:
    return [c for c in frontier.columns if c.startswith("check_") and c != exclude]


def _robust_gate_columns(frontier: pd.DataFrame) -> list[str]:
    return [c for c in frontier.columns if c.startswith("robust_check_")]


def _abs_log_distance(frontier: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    centers = objective_centers(config)
    return pd.DataFrame({k: np.abs(np.log10(frontier[k] / centers[k])) for k in RESPONSES}, index=frontier.index)


# ------------------------------------------------------------------------------- constraint phase map
def mdi_floor_phase(frontier: pd.DataFrame, config: dict[str, Any], *, layer: str = "robust", lo: float = 0.30, hi: float = 0.40) -> list[dict[str, Any]]:
    """Winner as a function of the MDI-fraction lower bound, all other frozen gates unchanged.

    Returns contiguous segments [floor_lo, floor_hi] with the winner of that phase.
    """
    if layer not in ("nominal", "robust"):
        raise ValueError("layer must be 'nominal' or 'robust'")
    hc_hi = float(config["hard_constraints"]["mdi_fraction_of_polyol_plus_mdi"][1])
    base = frontier[_nominal_gate_columns(frontier)].all(axis=1) & frontier[MDI_FRACTION].le(hc_hi)
    score = "property_score"
    if layer == "robust":
        if "robust_score" not in frontier.columns:
            raise RuntimeError("robust layer not frozen in this frontier table")
        rcols = _robust_gate_columns(frontier)
        if rcols:
            base &= frontier[rcols].all(axis=1)
        score = "robust_score"
    segments: list[dict[str, Any]] = []
    cur = float(lo)
    while cur <= hi + 1e-12:
        cand = frontier[base & frontier[MDI_FRACTION].ge(cur)]
        if cand.empty:
            break
        win = cand.sort_values([score, CID], kind="mergesort").iloc[0]
        upper = min(float(win[MDI_FRACTION]), float(hi))
        segments.append({"floor_lo": cur, "floor_hi_inclusive": upper, "winner": str(win[CID]), "blend": str(win[BLEND]),
                         "nco_oh": float(win[NCO]), "mdi_fraction": float(win[MDI_FRACTION]), "score": float(win[score])})
        if upper >= hi - 1e-12:
            break
        cur = float(np.nextafter(upper, np.inf))
    return segments


def constraint_counterfactual(frontier: pd.DataFrame, config: dict[str, Any], *, layer: str = "robust") -> dict[str, Any]:
    """How far the frozen MDI floor can move before the current winner changes."""
    floor = float(config["hard_constraints"]["mdi_fraction_of_polyol_plus_mdi"][0])
    segs = mdi_floor_phase(frontier, config, layer=layer)
    current = next((s for s in segs if s["floor_lo"] - 1e-12 <= floor <= s["floor_hi_inclusive"] + 1e-12), None)
    idx = segs.index(current) if current else None
    return {
        "layer": layer,
        "frozen_floor": floor,
        "current_winner": current["winner"] if current else None,
        "winner_stable_for_floor_in": [current["floor_lo"], current["floor_hi_inclusive"]] if current else None,
        "floor_increase_to_change_winner": (current["floor_hi_inclusive"] - floor) if current else None,
        "floor_decrease_to_change_winner": (floor - current["floor_lo"]) if current else None,
        "winner_if_floor_raised": segs[idx + 1]["winner"] if current and idx + 1 < len(segs) else None,
        "winner_if_floor_lowered": segs[idx - 1]["winner"] if current and idx > 0 else None,
        "phase_map": segs,
    }


# ------------------------------------------------------------------------------ uncertainty phase map
def uncertainty_scale_table(frontier: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Per candidate: robust score as quadratic A + B s + C s^2 in the uncertainty scale s, and the
    largest s at which the propagated interval still fits the broad windows (smax_broad, bottleneck)."""
    r_cfg = config.get("robustness") or {}
    dmax = r_cfg.get("domain_ratio_max")
    mask = frontier["feasible_nominal"].astype(bool)
    if dmax is not None and DOMAIN_RATIO in frontier.columns:
        mask &= frontier[DOMAIN_RATIO].le(float(dmax))
    U = frontier[mask].copy()
    w = objective_weights(config)
    q = uncertainty_radius_multipliers(config)
    d = _abs_log_distance(U, config)
    r = U[UNC_RADIUS].astype(float)
    U["A"] = sum(w[k] * d[k] ** 2 for k in RESPONSES)
    U["B"] = sum(w[k] * 2 * d[k] * q[k] * r for k in RESPONSES)
    U["C"] = sum(w[k] * (q[k] * r) ** 2 for k in RESPONSES)
    broad = _bounds(config, BROAD_KEYS)
    smax, bott = [], []
    for _, row in U.iterrows():
        best = (math.inf, None)
        for k in RESPONSES:
            lo, hi = broad[k]
            y = float(row[k]); rr = float(row[UNC_RADIUS]) * q[k]
            s = min((math.log10(y) - math.log10(lo)) / rr, (math.log10(hi) - math.log10(y)) / rr) if rr > 0 else math.inf
            if s < best[0]:
                best = (s, k)
        smax.append(best[0]); bott.append(best[1])
    U["smax_broad"] = smax
    U["bottleneck_broad"] = bott
    return U


def uncertainty_scale_phase(frontier: pd.DataFrame, config: dict[str, Any], *, s_max: float = 2.2, step: float = 0.0025) -> list[dict[str, Any]]:
    """Robust winner as a function of a multiplier s on every frozen uncertainty radius."""
    U = uncertainty_scale_table(frontier, config)
    segs: list[dict[str, Any]] = []
    for s in np.arange(0.0, s_max + 1e-9, step):
        v = U[U["smax_broad"] >= s - 1e-12]
        if v.empty:
            winner, n = None, 0
        else:
            score = v["A"] + v["B"] * s + v["C"] * s * s
            winner, n = str(v.loc[score.idxmin(), CID]), int(len(v))
        if segs and segs[-1]["winner"] == winner:
            segs[-1]["s_hi"] = float(s); segs[-1]["n_admissible_at_hi"] = n
        else:
            segs.append({"s_lo": float(s), "s_hi": float(s), "winner": winner, "n_admissible_at_lo": n, "n_admissible_at_hi": n})
    return segs


def score_crossover(frontier: pd.DataFrame, config: dict[str, Any], candidate_a: str, candidate_b: str) -> dict[str, Any]:
    """Uncertainty scales at which the robust scores of two candidates are equal."""
    U = uncertainty_scale_table(frontier, config).set_index(CID)
    for c in (candidate_a, candidate_b):
        if c not in U.index:
            raise KeyError(f"{c} is not nominal-feasible/domain-admissible, so it has no robust score trajectory")
    a, b = U.loc[candidate_a], U.loc[candidate_b]
    coeffs = [float(a["C"] - b["C"]), float(a["B"] - b["B"]), float(a["A"] - b["A"])]
    roots = np.roots(coeffs) if abs(coeffs[0]) > 1e-18 or abs(coeffs[1]) > 1e-18 else np.array([])
    cross = sorted(float(x.real) for x in roots if abs(x.imag) < 1e-10 and x.real >= 0)
    return {
        "candidate_a": candidate_a, "candidate_b": candidate_b,
        "score_a_at_s1": float(a["A"] + a["B"] + a["C"]), "score_b_at_s1": float(b["A"] + b["B"] + b["C"]),
        "nominal_score_a": float(a["A"]), "nominal_score_b": float(b["A"]),
        "crossover_scales": cross,
        "leader_at_s0": candidate_a if a["A"] <= b["A"] else candidate_b,
        "leader_at_s1": candidate_a if (a["A"] + a["B"] + a["C"]) <= (b["A"] + b["B"] + b["C"]) else candidate_b,
        "smax_broad_a": float(a["smax_broad"]), "smax_broad_b": float(b["smax_broad"]),
        "bottleneck_a": str(a["bottleneck_broad"]), "bottleneck_b": str(b["bottleneck_broad"]),
    }


def uncertainty_counterfactual(frontier: pd.DataFrame, config: dict[str, Any], constrained_winner: str, robust_winner: str) -> dict[str, Any]:
    """Why L1 != L2 and how much uncertainty must shrink/grow to change that."""
    rob = frontier.set_index(CID)
    l1_robust_feasible = bool(rob.loc[constrained_winner, "feasible_robust"]) if "feasible_robust" in rob.columns else None
    out: dict[str, Any] = {
        "constrained_winner": constrained_winner, "robust_winner": robust_winner,
        "same_winner": constrained_winner == robust_winner,
        "l1_winner_robust_admissible": l1_robust_feasible,
        "mechanism": ("identical" if constrained_winner == robust_winner else
                      ("worst_case_objective" if l1_robust_feasible else "robust_admissibility_gate")),
    }
    if constrained_winner != robust_winner and l1_robust_feasible:
        out["crossover"] = score_crossover(frontier, config, constrained_winner, robust_winner)
    phase = uncertainty_scale_phase(frontier, config)
    cur = next((p for p in phase if p["s_lo"] - 1e-12 <= 1.0 <= p["s_hi"] + 1e-12), None)
    out["robust_winner_stable_for_scale_in"] = [cur["s_lo"], cur["s_hi"]] if cur else None
    out["phase_map"] = phase
    return out


# ---------------------------------------------------------------------------------- weight stability
def weight_stability(frontier: pd.DataFrame, config: dict[str, Any], *, layer: str = "robust", samples: int = 50000, seed: int = 20260909) -> dict[str, Any]:
    """Fraction of Dirichlet-random objective weights under which each candidate wins."""
    if layer == "robust":
        x = frontier[frontier["feasible_robust"]]
        q = uncertainty_radius_multipliers(config)
        d = _abs_log_distance(x, config)
        r = x[UNC_RADIUS].astype(float)
        D = np.column_stack([(d[k] + q[k] * r) ** 2 for k in RESPONSES])
    elif layer == "nominal":
        x = frontier[frontier["feasible_nominal"]]
        d = _abs_log_distance(x, config)
        D = np.column_stack([d[k] ** 2 for k in RESPONSES])
    else:
        raise ValueError("layer must be 'nominal' or 'robust'")
    rng = np.random.default_rng(seed)
    W = rng.dirichlet(np.ones(3), size=int(samples))
    ids = x[CID].to_numpy()
    winners: list[str] = []
    for i in range(0, len(W), 5000):
        winners.extend(ids[np.argmin(W[i:i + 5000] @ D.T, axis=1)])
    counts = pd.Series(winners).value_counts()
    return {"layer": layer, "samples": int(samples), "seed": int(seed), "weights_frozen": objective_weights(config),
            "winner_fractions": [{"winner": str(k), "fraction": float(v / len(W))} for k, v in counts.items()][:15]}


# --------------------------------------------------------------------------------------- Pareto set
def pareto_alternatives(frontier: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    """Non-dominated robust-admissible candidates on (|d80|, |d120|, |dratio|, uncertainty radius, domain ratio)."""
    P = frontier[frontier["feasible_robust"]].copy()
    d = _abs_log_distance(P, config)
    cols = [d[ETA80].to_numpy(), d[ETA120].to_numpy(), d[RATIO].to_numpy(), P[UNC_RADIUS].to_numpy(dtype=float)]
    names = ["abs_log10_d_eta80", "abs_log10_d_eta120", "abs_log10_d_ratio", "uncertainty_radius"]
    if DOMAIN_RATIO in P.columns:
        cols.append(P[DOMAIN_RATIO].to_numpy(dtype=float)); names.append("domain_ratio")
    V = np.column_stack(cols)
    nd = np.ones(len(P), dtype=bool)
    for i in range(len(P)):
        dom = np.all(V <= V[i] + 1e-15, axis=1) & np.any(V < V[i] - 1e-15, axis=1)
        dom[i] = False
        if dom.any():
            nd[i] = False
    P["pareto"] = nd
    front = P[nd].sort_values("robust_score")
    return {"criteria": names, "n_robust_admissible": int(len(P)), "n_non_dominated": int(nd.sum()),
            "pareto_ids": [str(x) for x in front[CID]],
            "pareto_rows": front[[CID, BLEND, NCO, MDI_FRACTION, "property_score", "robust_score"]].to_dict(orient="records")}


# --------------------------------------------------------------------------- objective structure audit
def objective_structure_audit(config: dict[str, Any]) -> dict[str, Any]:
    """Does the frozen three-term objective double-count? eta80 = eta120 * ratio, so the three log
    distances live on two degrees of freedom; equal weights induce the metric [[2,1],[1,2]] on
    (log eta120, log ratio) with eigenvalues 3 and 1."""
    c = objective_centers(config)
    w = objective_weights(config)
    pref = _bounds(config, PREFERRED_KEYS)
    delta = math.log10(c[ETA120] * c[RATIO] / c[ETA80])
    # J = w80 (u+v)^2 + w120 u^2 + wr v^2 with u = d120, v = dratio, d80 = u + v (+ delta)
    metric = [[w[ETA80] + w[ETA120], w[ETA80]], [w[ETA80], w[ETA80] + w[RATIO]]]
    eig = sorted(np.linalg.eigvalsh(np.array(metric)).tolist(), reverse=True)
    return {
        "identity": "eta80 = eta120 * ratio  =>  log10 d80 = log10 d120 + log10 dratio + delta",
        "center_inconsistency_delta_log10": delta,
        "independent_degrees_of_freedom": 2, "objective_terms": 3,
        "double_counting": True,
        "induced_metric_on_(log_eta120, log_ratio)": metric,
        "metric_eigenvalues": eig,
        "principal_weight_ratio": (eig[0] / eig[1]) if eig[1] > 0 else None,
        "principal_direction": "eta120 and ratio moving together (i.e. eta80 moving) is penalised 3x more than moving apart",
        "preferred_halfwidths_log10": {k: 0.5 * math.log10(hi / lo) for k, (lo, hi) in pref.items()},
        "note": "This is a property of the frozen objective definition. It is reported, not corrected; correcting it would be a new benchmark version.",
    }


# ------------------------------------------------------------------------------ consistency report
def consistency_report(frontier: pd.DataFrame, config: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    """Internal consistency of a frozen decision chain. Each check is True when consistent."""
    f = frontier.set_index(CID)
    checks: dict[str, dict[str, Any]] = {}

    def add(name: str, ok: bool, detail: str) -> None:
        checks[name] = {"consistent": bool(ok), "detail": detail}

    l0, l1, l2 = decision.get("property_winner"), decision.get("constrained_winner"), decision.get("robust_winner")
    ac = (decision.get("active_constraint") or {}).get("name")
    bw = decision.get("backward_design") or {}
    add("l0_is_global_property_min", f["property_rank"].idxmin() == l0, f"property_rank==1 is {f['property_rank'].idxmin()}")
    add("l1_nominal_feasible", bool(f.loc[l1, "feasible_nominal"]) if l1 in f.index else False, f"{l1} feasible_nominal")
    if l2 is not None and "feasible_robust" in f.columns:
        add("l2_robust_feasible", bool(f.loc[l2, "feasible_robust"]), f"{l2} feasible_robust")
    l0_feasible = bool(f.loc[l0, "feasible_nominal"]) if l0 in f.index else False
    add("active_constraint_matches_l0_feasibility", (ac == "none") == l0_feasible, f"L0 feasible={l0_feasible}, active_constraint={ac}")
    if ac and ac != "none" and l0 in f.index:
        add("active_constraint_is_a_real_failure", not bool(f.loc[l0, f"check_{ac}"]) if f"check_{ac}" in f.columns else False, f"check_{ac} for {l0}")
    t, g, reach_id = bw.get("continuous_threshold"), bw.get("nearest_reachable_grid_value"), bw.get("nearest_reachable_candidate_id")
    if t is not None and g is not None and l0 in f.index:
        add("backward_threshold_below_reachable_grid", float(f.loc[l0, NCO]) < t <= g + 1e-12, f"n_L0={float(f.loc[l0, NCO])}, n*={t}, grid={g}")
    if reach_id in f.index:
        add("reachable_candidate_passes_mdi_floor", bool(f.loc[reach_id, "check_mdi_fraction"]), f"{reach_id} check_mdi_fraction")
        add("reachable_candidate_same_blend_as_l0", f.loc[reach_id, BLEND] == f.loc[l0, BLEND], "blend equality")
    if l2 is not None and reach_id is not None:
        checks["robust_winner_equals_reachable_candidate"] = {"consistent": None, "observation": l2 == reach_id,
                                                              "detail": "observation only: the frozen chain does not require L2 to coincide with the backward-reachable point"}
    contradictions = [k for k, v in checks.items() if v.get("consistent") is False]
    return {"checks": checks, "contradictions": contradictions, "n_contradictions": len(contradictions)}
