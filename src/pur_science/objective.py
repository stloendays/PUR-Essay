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
    """Geometric midpoint of a positive window (the frozen objective center)."""
    lo, hi = [float(x) for x in bounds]
    if lo <= 0 or hi <= 0 or hi < lo:
        raise ValueError(f"Invalid positive window {bounds!r}")
    return math.sqrt(lo * hi)


def mdi_fraction(mdi_parts: float, polyol_basis_parts: float = 100.0) -> float:
    """MDI mass fraction of polyol + MDI for a formulation on a fixed polyol basis."""
    if mdi_parts < 0 or polyol_basis_parts <= 0:
        raise ValueError("mdi_parts must be >= 0 and polyol basis > 0")
    return mdi_parts / (polyol_basis_parts + mdi_parts)


def objective_centers(config: dict[str, Any]) -> dict[str, float]:
    hc = config["hard_constraints"]
    return {k: window_center(hc[key]) for k, key in PREFERRED_KEYS.items()}


def objective_weights(config: dict[str, Any]) -> dict[str, float]:
    w = config.get("objective", {}).get("weights", {})
    return {ETA80: float(w.get("eta80", 1.0)), ETA120: float(w.get("eta120", 1.0)), RATIO: float(w.get("ratio", 1.0))}


def log_distance(frame: pd.DataFrame, centers: dict[str, float]) -> pd.DataFrame:
    """Signed log10 distance of each response from its center."""
    return pd.DataFrame({k: np.log10(frame[k] / centers[k]) for k in RESPONSES}, index=frame.index)


def property_score(frame: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    """Frozen nominal objective: weighted sum of squared log10 distances to the preferred centers.

    Identical to the ORACLE V2 `oracle_score` definition.
    """
    centers = objective_centers(config)
    weights = objective_weights(config)
    d = log_distance(frame, centers)
    return sum(weights[k] * d[k] ** 2 for k in RESPONSES)


def worst_case_property_score(frame: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    """FRONTIER V1 robust objective: worst case of the nominal objective over the frozen log10 interval.

    Each response is known only within log10(y) +/- r. The worst-case squared distance to the
    center is (|log10(y/c)| + r)^2. This is a deterministic, interval-based robust score; no
    distributional assumption is made.
    """
    if UNC_RADIUS not in frame.columns:
        raise KeyError("worst-case objective requires the uncertainty radius column")
    centers = objective_centers(config)
    weights = objective_weights(config)
    d = log_distance(frame, centers).abs()
    r = frame[UNC_RADIUS].astype(float)
    return sum(weights[k] * (d[k] + r) ** 2 for k in RESPONSES)


def _between(s: pd.Series, bounds: Iterable[float]) -> pd.Series:
    lo, hi = [float(x) for x in bounds]
    return s.ge(lo) & s.le(hi)


def _interval_inside(frame: pd.DataFrame, key: str, bounds: Iterable[float]) -> pd.Series:
    lo, hi = [float(x) for x in bounds]
    r = frame[UNC_RADIUS].astype(float)
    lg = np.log10(frame[key])
    return (lg - r).ge(math.log10(lo)) & (lg + r).le(math.log10(hi))


def nominal_checks(table: CanonicalTable, config: dict[str, Any]) -> pd.DataFrame:
    """Boolean pass/fail per nominal hard constraint (ORACLE V2 gate set, applied only where configured)."""
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
    """Additional FRONTIER V1 robust feasibility gates.

    - interval_inside_preferred: the whole log10 uncertainty interval of every response lies inside the preferred window.
    - domain_ratio_max: the domain-distance descriptor does not exceed the frozen maximum.
    """
    r = config.get("robustness") or {}
    if not r.get("enabled", False):
        raise RuntimeError("Robust ranking is not frozen in this config; refuse to invent a robust score.")
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
    """Human-readable bounds for each nominal check, for audits and Agent tools."""
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
