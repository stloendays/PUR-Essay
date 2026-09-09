from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

_BLEND_TOKEN = re.compile(r"^\s*([^:+]+?)\s*:\s*([0-9.]+)\s*$")

# Canonical internal column names used by every science function.
CID = "cid"
BLEND = "blend"
NCO = "nco_oh"
MDI_PARTS = "mdi_parts"
MDI_FRACTION = "mdi_fraction"
ETA80 = "eta80"
ETA120 = "eta120"
RATIO = "ratio"
DOMAIN_RATIO = "domain_ratio"
UNC_RADIUS = "unc_radius"
IN_DOMAIN = "in_domain"

REQUIRED = ("candidate_id", "blend", "nco_oh", "mdi_parts", "eta80", "eta120", "ratio")
OPTIONAL = ("domain_ratio", "uncertainty_radius", "chemistry_in_domain")

DEFAULT_COLUMN_CANDIDATES: dict[str, tuple[str, ...]] = {
    "candidate_id": ("source_candidate_id", "candidate_id", "formulation_id"),
    "blend": ("blend",),
    "nco_oh": ("nco_oh",),
    "mdi_parts": ("mdi_parts",),
    "eta80": ("simulated_eta_80c_pa_s", "eta80_pa_s", "eta80"),
    "eta120": ("simulated_eta_120c_pa_s", "eta120_pa_s", "eta120"),
    "ratio": ("simulated_ratio_80c_120c", "ratio_80_120", "ratio"),
    "domain_ratio": ("simulated_domain_ratio", "domain_ratio"),
    "uncertainty_radius": ("simulated_log10_interval_radius", "uncertainty_radius", "log10_interval_radius"),
    "chemistry_in_domain": ("simulated_chemistry_in_domain_flag", "chemistry_in_domain"),
}


def parse_blend(text: Any) -> dict[str, float]:
    """Parse 'PPG1000:50+PPG700:50' (or 'Material_B:50+Material_C:50') into {component: parts}."""
    out: dict[str, float] = {}
    for token in str(text).split("+"):
        m = _BLEND_TOKEN.match(token)
        if not m:
            raise ValueError(f"Cannot parse blend token {token!r} in {text!r}")
        out[m.group(1)] = float(m.group(2))
    if not out:
        raise ValueError(f"Empty blend string: {text!r}")
    return out


def resolve_columns(df_columns: list[str], configured: dict[str, str] | None) -> dict[str, str]:
    """Map logical names to the physical columns present in the table."""
    configured = configured or {}
    resolved: dict[str, str] = {}
    for logical in REQUIRED + OPTIONAL:
        name = configured.get(logical)
        if name:
            if name in df_columns:
                resolved[logical] = name
            elif logical in REQUIRED:
                raise KeyError(f"Configured column {logical}={name!r} is not in the candidate table")
            continue
        for cand in DEFAULT_COLUMN_CANDIDATES.get(logical, ()):
            if cand in df_columns:
                resolved[logical] = cand
                break
        else:
            if logical in REQUIRED:
                raise KeyError(f"No column found for required field {logical!r}; configure columns.{logical}")
    return resolved


@dataclass
class CanonicalTable:
    """Candidate table with canonical column names and derived descriptors."""

    frame: pd.DataFrame
    physical: dict[str, str]
    polyol_basis_parts: float = 100.0
    components: list[str] = field(default_factory=list)

    @property
    def has_uncertainty(self) -> bool:
        return UNC_RADIUS in self.frame.columns

    @property
    def has_domain_ratio(self) -> bool:
        return DOMAIN_RATIO in self.frame.columns

    @property
    def has_in_domain(self) -> bool:
        return IN_DOMAIN in self.frame.columns

    def row(self, cid: str) -> pd.Series:
        hit = self.frame[self.frame[CID] == str(cid)]
        if hit.empty:
            raise KeyError(f"Unknown candidate: {cid}")
        return hit.iloc[0]


def canonicalize(df: pd.DataFrame, config: dict[str, Any]) -> CanonicalTable:
    """Return a canonical copy of the candidate table.

    The source frame is never mutated. Derived columns:
    - mdi_fraction = mdi_parts / (polyol_basis + mdi_parts)
    - one '<component>' parts column per blend component parsed from the blend string
    """
    physical = resolve_columns(list(df.columns), config.get("columns"))
    basis = float(config.get("polyol_basis_parts", 100.0))
    out = pd.DataFrame(index=df.index)
    out[CID] = df[physical["candidate_id"]].astype(str)
    out[BLEND] = df[physical["blend"]].astype(str)
    for logical, canon in (("nco_oh", NCO), ("mdi_parts", MDI_PARTS), ("eta80", ETA80), ("eta120", ETA120), ("ratio", RATIO)):
        out[canon] = pd.to_numeric(df[physical[logical]], errors="raise").astype(float)
    if "domain_ratio" in physical:
        out[DOMAIN_RATIO] = pd.to_numeric(df[physical["domain_ratio"]], errors="raise").astype(float)
    if "uncertainty_radius" in physical:
        out[UNC_RADIUS] = pd.to_numeric(df[physical["uncertainty_radius"]], errors="raise").astype(float)
    if "chemistry_in_domain" in physical:
        raw = df[physical["chemistry_in_domain"]]
        if raw.dtype == object or str(raw.dtype).startswith("str"):
            out[IN_DOMAIN] = raw.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})
        else:
            out[IN_DOMAIN] = raw.astype(bool)
    if (out[[ETA80, ETA120, RATIO]] <= 0).any().any():
        raise ValueError("eta80, eta120 and ratio must be strictly positive for the log-space objective")
    out[MDI_FRACTION] = out[MDI_PARTS] / (basis + out[MDI_PARTS])

    parsed = out[BLEND].map(parse_blend)
    components = sorted({k for d in parsed for k in d})
    for comp in components:
        out[comp] = parsed.map(lambda d, c=comp: d.get(c, 0.0)).astype(float)
    if out[CID].duplicated().any():
        dup = out[CID][out[CID].duplicated()].iloc[0]
        raise ValueError(f"Duplicate candidate id {dup!r}")
    return CanonicalTable(out.reset_index(drop=True), physical, basis, components)
