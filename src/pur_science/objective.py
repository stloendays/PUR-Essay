from __future__ import annotations

import math
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .canonical import (
    DOMAIN_RATIO, ETA120, ETA80, IN_DOMAIN, MDI_FRACTION, NCO, RATIO, UNC_RADIUS, CanonicalTable,
)

RESPONSES = (ETA80, ETA120, RATIO)
PREFERRED_KEYS = {ETA80: "eta80_preferred_pa_s", ETA120: "eta120_preferred_pa_s", RATIO: "ratio_preferred"}
BROAD_KEYS = {ETA80: "eta80_broad_pa_s", ETA120: "eta120_broad_pa_s", RATIO: "ratio_broad"}


def window_center(bounds: Iterable[float]) -> float:
    """Geometric midpoint of a positive window."""
    lo, hi = [float(x) for x in bounds]
    if lo <= 0 or hi <= 0 or hi < lo:
        raise ValueError(f"Invalid positive window {bounds!r}")
    return math.sqrt(lo * hi)


def mdi_fraction(mdi_parts: float, polyol_basis_parts: float = 100.0) -> float:
    if mdi_parts < 0 or polyol_basis_parts <= 0:
        raise ValueError("mdi_parts must be >= 0 and polyol basis > 0")
    return mdi_parts / (polyol_basis_parts + mdi_parts)


def objective_coordinates(config: dict[str, Any]) -> tuple[str, ...]:
    """Return the response coordinates used by the frozen objective.

    Historical ORACLE V2 used eta80, eta120 and eta80/eta120. The database-synchronised
    rheology-state objective uses the two algebraically independent coordinates eta120 and
    eta80/eta120 while retaining eta80 as a hard processing-window constraint.
    """
    coords = config.get("objective", {}).get("coordinates")
    if coords is None:
        return RESPONSES
    mapping = {"eta80": ETA80, "eta120": ETA120, "ratio": RATIO}
    out = tuple(mapping.get(str(k), str(k)) for k in coords)
    bad = [k for k in out if k not in RESPONSES]
    if bad:
        raise ValueError(f"Unsupported objective coordinates: {bad}")
    return out


def objective_centers(config: dict[str, Any]) -> dict[str, float]:
    obj = config.get("objective", {})
    configured = obj.get("centers") or {}
    hc = config["hard_constraints"]
    out: dict[str, float] = {}
    for k in objective_coordinates(config):
        if k in configured:
            out[k] = float(configured[k])
        else:
            out[k] = window_center(hc[PREFERRED_KEYS[k]])
    return out


def objective_weights(config: dict[str, Any]) -> dict[str, float]:
    w = config.get("objective", {}).get("weights", {})
    return {k: float(w.get(k, 1.0)) for k in objective_coordinates(config)}


def objective_halfwidths(config: dict[str, Any]) -> dict[str, float] | None:
    raw = config.get("objective", {}).get("halfwidth_log10")
    if raw is None:
        return None
    out = {k: float(raw[k]) for k in objective_coordinates(config)}
    if any(v <= 0 for v in out.values()):
        raise ValueError("objective halfwidth_log10 values must be positive")
    return out


def log_distance(frame: pd.DataFrame, centers: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame({k: np.log10(frame[k] / centers[k]) for k in centers}, index=frame.index)


def property_score(frame: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    """Frozen nominal objective.

    If `objective.halfwidth_log10` is present, each independent coordinate is normalised by
    the corresponding preferred-window half-width in log10 space. Otherwise this reduces to
    the historical ORACLE V2 weighted squared-log objective.
    """
    centers = objective_centers(config)
    weights = objective_weights(config)
    half = objective_halfwidths(config)
    d = log_distance(frame, centers)
    if half is None:
        return sum(weights[k] * d[k] ** 2 for k in centers)
    return sum(weights[k] * (d[k] / half[k]) ** 2 for k in centers)


def worst_case_property_score(frame: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    """Worst case over a common symmetric log10 response radius.

    This remains available for historical/test configurations. The database-synchronised
    strict robustness definition requires actual per-response lower/upper intervals and is
    intentionally refused here rather than approximated by a common radius.
    """
    robust = config.get("robustness") or {}
    if robust.get("require_actual_response_intervals", False):
        raise RuntimeError(
            "This FRONTIER definition requires actual per-response lower/upper intervals; "
            "a single common uncertainty radius is not an admissible substitute."
        )
    if UNC_RADIUS not in frame.columns:
        raise KeyError("worst-case objective requires the uncertainty radius column")
    centers = objective_centers(config)
    weights = objective_weights(config)
    half = objective_halfwidths(config)
    d = log_distance(frame, centers).abs()
    r = frame[UNC_RADIUS].astype(float)
    if half is None:
        return sum(weights[k] * (d[k] + r) ** 2 for k in centers)
    return sum(weights[k] * ((d[k] + r) / half[k]) ** 2 for k in centers)


def _between(s: pd.Series, bounds: Iterable[float]) -> pd.Series:
    lo, hi = [float(x) for x in bounds]
    return s.ge(lo) & s.le(hi)


def _interval_inside(frame: pd.DataFrame, key: str, bounds: Iterable[float]) -> pd.Series:
    lo, hi = [float(x) for x in bounds]
    r = frame[UNC_RADIUS].astype(float)
    lg = np.log10(frame[key])
    return (lg - r).ge(math.log10(lo)) & (lg + r).le(math.log10(hi))


def nominal_checks(table: CanonicalTable, config: dict[str, Any]) -> pd.DataFrame:
    hc = config["hard_constraints"]
    f = table.frame
    checks: dict[str, pd.Series] = {}
    if "nco_oh" in hc:
        checks["nco_oh"] = _between(f[NCO], hc["nco_oh"])
    if "mdi_fraction_of_polyol_plus_mdi" in hc:
        checks["mdi_fraction"] = _between(f[MDI_FRACTION], hc["mdi_fraction_of_polyol_plus_mdi"])
    for k, key in BROAD_KEYS.items():
        if key in hc:
            checks[f"{k}_broad"] = _between(f[k], hc[key])
    for k, key in PREFERRED_KEYS.items():
        if key in hc:
            checks[f"{k}_preferred"] = _between(f[k], hc[key])
    if hc.get("require_chemistry_in_domain", False):
        if not table.has_in_domain:
            raise KeyError("require_chemistry_in_domain=true but no chemistry_in_domain column is available")
        checks["chemistry_in_domain"] = f[IN_DOMAIN].astype(bool)
    if hc.get("require_full_oracle_interval_inside_broad_window", False):
        if not table.has_uncertainty:
            raise KeyError("require_full_oracle_interval_inside_broad_window=true but no uncertainty radius column is available")
        inside = pd.Series(True, index=f.index)
        for k, key in BROAD_KEYS.items():
            inside &= _interval_inside(f, k, hc[key])
        checks["interval_inside_broad"] = inside
    return pd.DataFrame(checks, index=f.index)


def robust_checks(table: CanonicalTable, config: dict[str, Any]) -> pd.DataFrame:
    """Additional FRONTIER robust feasibility gates for common-radius configurations.

    The latest database audit uses actual lower/upper intervals, including a compounded
    eta80/eta120 interval. Those bounds are not present in the current PUR-Essay candidate
    schema, so this function refuses to reconstruct them from a common radius.
    """
    r = config.get("robustness") or {}
    if not r.get("enabled", False):
        raise RuntimeError("Robust ranking is not frozen in this config; refuse to invent a robust score.")
    if r.get("require_actual_response_intervals", False):
        raise RuntimeError(
            "Strict robustness requires the original per-response lower/upper interval columns. "
            "Restore them with the full PUR_SIM_V1 response table before freezing L2."
        )
    hc = config["hard_constraints"]
    f = table.frame
    checks: dict[str, pd.Series] = {}
    if r.get("require_interval_inside_preferred", True):
        if not table.has_uncertainty:
            raise KeyError("Robust gate needs the uncertainty radius column")
        inside = pd.Series(True, index=f.index)
        for k, key in PREFERRED_KEYS.items():
            inside &= _interval_inside(f, k, hc[key])
        checks["interval_inside_preferred"] = inside
    if r.get("domain_ratio_max") is not None:
        if not table.has_domain_ratio:
            raise KeyError("Robust gate needs the domain_ratio column")
        checks["domain_ratio_max"] = f[DOMAIN_RATIO].le(float(r["domain_ratio_max"]))
    return pd.DataFrame(checks, index=f.index)


def constraint_bounds(config: dict[str, Any]) -> dict[str, Any]:
    hc = config["hard_constraints"]
    out: dict[str, Any] = {}
    if "nco_oh" in hc:
        out["nco_oh"] = hc["nco_oh"]
    if "mdi_fraction_of_polyol_plus_mdi" in hc:
        out["mdi_fraction"] = hc["mdi_fraction_of_polyol_plus_mdi"]
    for k, key in BROAD_KEYS.items():
        if key in hc:
            out[f"{k}_broad"] = hc[key]
    for k, key in PREFERRED_KEYS.items():
        if key in hc:
            out[f"{k}_preferred"] = hc[key]
    return out
