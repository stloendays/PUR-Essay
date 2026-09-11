"""Dual-path verification of critical quantities (PUR-RECOVER V2, Stage D).

The backward NCO:OH threshold has two admissible deterministic derivations on the frozen
design manifold:

    Path A  solve_backward_threshold                      (dedicated primitive)
    Path B  local_nco_sweep + calculate_mdi_fraction      (reconstruction from the blend grid)

In the 2026-09-10 pilot the `pur_agent_no_backward` ablation recovered 1.77198 through Path B
alone. V2 promotes that from an accident to a contract: when both paths are available, both
are computed and compared against a predeclared tolerance.

Both values are reconstructed **here, from the recorded tool trace**, not read out of the
model's prose. The model is separately asked to report its own two values, so that agreement
between the deterministic reconstruction and the model's narrative is measurable as an
independent explanation-fidelity signal.

This is independent scientific reconstruction, not voting between language-model samples: no
answer is selected by majority, and a disagreement is surfaced as a structured conflict.
"""
from __future__ import annotations

import math
from typing import Any, Iterable

DEFAULT_CROSS_PATH_TOLERANCE = 1e-6
CROSS_PATH_VERSION = "PUR_CROSSPATH_V2"

PATH_A_TOOLS = ("solve_backward_threshold",)
PATH_B_TOOLS = ("local_nco_sweep", "calculate_mdi_fraction")


def _ok(entry: dict[str, Any]) -> dict[str, Any] | None:
    out = entry.get("output")
    if isinstance(out, dict) and out.get("ok"):
        result = out.get("result")
        return result if isinstance(result, dict) else None
    return None


def _entries(trace: Iterable[dict[str, Any]], tool: str) -> list[dict[str, Any]]:
    return [r for r in (_ok(e) for e in trace if e.get("tool") == tool) if r]


def _mdi_floor(config: dict[str, Any]) -> float | None:
    bounds = (config.get("hard_constraints") or {}).get("mdi_fraction_of_polyol_plus_mdi")
    return float(bounds[0]) if bounds else None


def _pick_sweep(sweeps: list[dict[str, Any]], *, blend: str | None, property_winner: str | None) -> dict[str, Any] | None:
    """The sweep that describes the property winner's own blend manifold."""
    if not sweeps:
        return None
    if property_winner:
        for s in sweeps:
            if any(str(r.get("cid")) == str(property_winner) for r in (s.get("rows") or [])):
                return s
    if blend:
        for s in sweeps:
            if str(s.get("blend")) == str(blend):
                return s
    return sweeps[0] if len(sweeps) == 1 else sweeps[0]


def path_a_threshold(trace: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    for r in _entries(trace, "solve_backward_threshold"):
        if r.get("continuous_threshold") is not None:
            return {
                "value": float(r["continuous_threshold"]),
                "blend": r.get("blend"),
                "derivation": "solve_backward_threshold",
                "reason": r.get("reason"),
            }
    return None


def path_b_threshold(
    trace: Iterable[dict[str, Any]],
    config: dict[str, Any],
    *,
    blend: str | None = None,
    property_winner: str | None = None,
) -> dict[str, Any] | None:
    """Reconstruct the continuous threshold from the blend's own NCO:OH grid.

    On the frozen manifold mdi_parts = k * nco_oh for a fixed blend, so with the polyol basis
    B and floor f the threshold is n* = f*B / (k*(1-f)). If the observed grid is not exactly
    linear, monotone interpolation on (mdi_fraction, nco_oh) is used, matching
    `pur_science.backward.solve_backward_threshold`.
    """
    floor = _mdi_floor(config)
    if floor is None:
        return None
    sweeps = _entries(trace, "local_nco_sweep")
    sweep = _pick_sweep(sweeps, blend=blend, property_winner=property_winner)
    if not sweep:
        return None
    rows = [r for r in (sweep.get("rows") or []) if r.get("nco_oh") and r.get("mdi_parts") is not None]
    if len(rows) < 2:
        return None

    basis = None
    for r in _entries(trace, "calculate_mdi_fraction"):
        if r.get("polyol_basis_parts") is not None:
            basis = float(r["polyol_basis_parts"])
            break
    if basis is None:
        return None  # Path B requires the mass-fraction primitive; the graph declares it

    n = [float(r["nco_oh"]) for r in rows]
    m = [float(r["mdi_parts"]) for r in rows]
    k = [mi / ni for mi, ni in zip(m, n)]
    linear = all(math.isclose(ki, k[0], rel_tol=1e-6, abs_tol=0.0) for ki in k)
    if linear:
        value = floor * basis / (k[0] * (1.0 - floor))
        reason = "linear MDI-demand manifold reconstructed from the blend grid"
    else:
        frac = [float(r.get("mdi_fraction")) if r.get("mdi_fraction") is not None else mi / (basis + mi) for r, mi in zip(rows, m)]
        pairs = sorted(zip(frac, n))
        fs = [p[0] for p in pairs]
        ns = [p[1] for p in pairs]
        if not (fs[0] <= floor <= fs[-1]):
            return None
        value = _interp(floor, fs, ns)
        reason = "monotone interpolation on the observed blend grid (manifold not exactly linear)"
    return {
        "value": float(value),
        "blend": sweep.get("blend"),
        "derivation": "local_nco_sweep + calculate_mdi_fraction",
        "reason": reason,
        "polyol_basis_parts": basis,
        "mdi_floor": floor,
    }


def _interp(x: float, xs: list[float], ys: list[float]) -> float:
    for i in range(1, len(xs)):
        if xs[i - 1] <= x <= xs[i]:
            if xs[i] == xs[i - 1]:
                return ys[i]
            t = (x - xs[i - 1]) / (xs[i] - xs[i - 1])
            return ys[i - 1] + t * (ys[i] - ys[i - 1])
    return ys[-1]


def verify_backward_threshold(
    trace: Iterable[dict[str, Any]],
    config: dict[str, Any],
    *,
    property_winner: str | None = None,
    tolerance: float | None = None,
    required: bool = True,
) -> dict[str, Any]:
    """Compare the two admissible derivations recorded in the trace.

    status:
      agree              both paths present and within tolerance
      disagree           both paths present and outside tolerance -> structured conflict
      single_path_only   only one derivation was available or executed
      no_path            neither derivation is present
    """
    trace = list(trace)
    tol = float(tolerance if tolerance is not None else DEFAULT_CROSS_PATH_TOLERANCE)
    a = path_a_threshold(trace)
    b = path_b_threshold(trace, config, blend=(a or {}).get("blend"), property_winner=property_winner)
    out: dict[str, Any] = {
        "version": CROSS_PATH_VERSION,
        "quantity": "backward_continuous_threshold_nco_oh",
        "tolerance": tol,
        "required": bool(required),
        "path_a": a,
        "path_b": b,
        "value_a": (a or {}).get("value"),
        "value_b": (b or {}).get("value"),
        "absolute_difference": None,
        "cross_path_verified": False,
        "status": "no_path",
        "conflict": False,
    }
    if a and b:
        diff = abs(a["value"] - b["value"])
        out["absolute_difference"] = diff
        out["cross_path_verified"] = diff <= tol
        out["status"] = "agree" if diff <= tol else "disagree"
        out["conflict"] = diff > tol
    elif a or b:
        out["status"] = "single_path_only"
        out["cross_path_verified"] = not required
    return out


def reported_cross_path(decision: dict[str, Any] | None) -> dict[str, Any] | None:
    """The model's own account of its two derivations, if it supplied one."""
    if not isinstance(decision, dict):
        return None
    block = decision.get("cross_path_verification")
    return block if isinstance(block, dict) else None


def reported_matches_trace(decision: dict[str, Any] | None, verification: dict[str, Any], *, tolerance: float | None = None) -> bool | None:
    """Whether the model's reported path values match the deterministic reconstruction."""
    block = reported_cross_path(decision)
    if not block:
        return None
    tol = float(tolerance if tolerance is not None else DEFAULT_CROSS_PATH_TOLERANCE)
    ok = True
    for key in ("value_a", "value_b"):
        claimed, actual = block.get(key), verification.get(key)
        if actual is None:
            continue
        try:
            ok &= abs(float(claimed) - float(actual)) <= tol
        except (TypeError, ValueError):
            return False
    return bool(ok)
