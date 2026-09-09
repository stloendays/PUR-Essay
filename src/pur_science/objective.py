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


def uncertainty_radius_multipliers(config: dict[str, Any]) -> dict[str, float]:
    """Return the frozen multiplier applied to the stored log10 uncertainty radius.

    PUR_SIM_V1 stores viscosity intervals as log10(eta) +/- r. Because the ratio is
    eta80/eta120, the conservative frozen interval used by FRONTIER V1 is
    log10(ratio) +/- 2r. Configs without an explicit uncertainty section retain the
    historical all-ones behavior for backwards-compatible tests and legacy artifacts.
    """
    raw = config.get("uncertainty", {}).get("log10_radius_multiplier", {})
    return {
        ETA80: float(raw.get("eta80", 1.0)),
        ETA120: float(raw.get("eta120", 1.0)),
        RATIO: float(raw.get("ratio", 1.0)),
    }


def log_distance(frame: pd.DataFrame, centers: dict[str, float]) -> pd.DataFrame:
    """Signed log10 distance of each response from its center."""
    return pd.DataFrame({k: np.log10(frame[k] / centers[k]) for k in RESPONSES}, index=frame.index)


def property_score(frame: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    """Frozen nominal objective: weighted sum of squared log10 distances to preferred centers."""
    centers = objective_centers(config)
    weights = objective_weights(config)
    d = log_distance(frame, centers)
    return sum(weights[k] * d[k] ** 2 for k in RESPONSES)


def worst_case_property_score(frame: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    """Worst case of the nominal objective over the frozen rectangular log10 interval.

    If a response k has nominal value y_k and uncertainty interval
    log10(y_k) +/- q_k*r, the maximum squared distance from the preferred center c_k
    is (abs(log10(y_k/c_k)) + q_k*r)^2. No probability distribution and no new
    uncertainty weight are introduced: FRONTIER V1 inherits the nominal objective
    weights unchanged.
    """
    if UNC_RADIUS not in frame.columns:
        raise KeyError("worst-case objective requires the uncertainty radius column")
    centers = objective_centers(config)
    weights = objective_weights(config)
    mult = uncertainty_radius_multipliers(config)
    d = log_distance(frame, centers).abs()
    r = frame[UNC_RADIUS].astype(float)
    return sum(weights[k] * (d[k] + mult[k] * r) ** 2 for k in RESPONSES)


def _between(s: pd.Series, bounds: Iterable[float]) -> pd.Series:
    lo, hi = [float(x) for x in bounds]
    return s.ge(lo) & s.le(hi)


def _interval_inside(frame: pd.DataFrame, key: str, bounds: Iterable[float], *, radius_multiplier: float = 1.0) -> pd.Series:
    lo, hi = [float(x) for x in bounds]
    r = frame[UNC_RADIUS].astype(float) * float(radius_multiplier)
    lg = np.log10(frame[key])
    return (lg - r).ge(math.log10(lo)) & (lg + r).le(math.log10(hi))


def nominal_checks(table: CanonicalTable, config: dict[str, Any]) -> pd.DataFrame:
    """Boolean pass/fail per nominal hard constraint.

    FRONTIER V1 intentionally keeps uncertainty out of L1. Historical configs may still
    request an interval-inside-broad gate; when they do, the configured uncertainty
    propagation multipliers are honored.
    """
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
        mult = uncertainty_radius_multipliers(config)
        inside = pd.Series(True, index=f.index)
        for k, key in BROAD_KEYS.items():
            inside &= _interval_inside(f, k, hc[key], radius_multiplier=mult[k])
        checks["interval_inside_broad"] = inside
    return pd.DataFrame(checks, index=f.index)


def robust_checks(table: CanonicalTable, config: dict[str, Any]) -> pd.DataFrame:
    """Additional FRONTIER robust-feasibility gates.

    FRONTIER V1 uses broad functional windows as the interval-certification envelope.
    Preferred windows remain the optimization target and are not required to contain the
    full uncertainty interval. The function also retains support for the earlier
    interval-inside-preferred option so historical toy fixtures remain reproducible.
    """
    r_cfg = config.get("robustness") or {}
    if not r_cfg.get("enabled", False):
        raise RuntimeError("Robust ranking is not frozen in this config; refuse to invent a robust score.")
    hc = config["hard_constraints"]
    f = table.frame
    checks: dict[str, pd.Series] = {}
    mult = uncertainty_radius_multipliers(config)

    if r_cfg.get("require_interval_inside_broad", False):
        if not table.has_uncertainty:
            raise KeyError("Robust broad-window gate needs the uncertainty radius column")
        inside = pd.Series(True, index=f.index)
        for k, key in BROAD_KEYS.items():
            inside &= _interval_inside(f, k, hc[key], radius_multiplier=mult[k])
        checks["interval_inside_broad"] = inside

    if r_cfg.get("require_interval_inside_preferred", False):
        if not table.has_uncertainty:
            raise KeyError("Robust preferred-window gate needs the uncertainty radius column")
        inside = pd.Series(True, index=f.index)
        for k, key in PREFERRED_KEYS.items():
            inside &= _interval_inside(f, k, hc[key], radius_multiplier=mult[k])
        checks["interval_inside_preferred"] = inside

    if r_cfg.get("domain_ratio_max") is not None:
        if not table.has_domain_ratio:
            raise KeyError("Robust gate needs the domain_ratio column")
        checks["domain_ratio_max"] = f[DOMAIN_RATIO].le(float(r_cfg["domain_ratio_max"]))
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
