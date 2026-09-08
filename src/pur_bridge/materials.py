from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd

_ALLOWED = {"MATCH", "FAMILY_MATCH", "UNKNOWN", "MISMATCH"}

@dataclass(frozen=True)
class MaterialGateResult:
    state: str
    reason: str


def evaluate_material_gate(path: str | Path) -> MaterialGateResult:
    df = pd.read_csv(path)
    required = {"material", "critical", "chemistry_status", "property_status"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing material audit columns: {sorted(missing)}")
    for col in ("chemistry_status", "property_status"):
        bad = set(df[col]).difference(_ALLOWED)
        if bad:
            raise ValueError(f"Invalid {col} states: {sorted(bad)}")
    critical = df[df["critical"].astype(bool)]
    if ((critical["chemistry_status"] == "MISMATCH") | (critical["property_status"] == "MISMATCH")).any():
        return MaterialGateResult("INCOMPATIBLE", "At least one critical material has a chemistry/property mismatch.")
    if ((critical["chemistry_status"] == "UNKNOWN") | (critical["property_status"] == "UNKNOWN")).any():
        return MaterialGateResult("AUDIT_REQUIRED", "Critical material evidence is incomplete; resolve before E6*.")
    all_exact = ((df["chemistry_status"] == "MATCH") & (df["property_status"] == "MATCH")).all()
    if all_exact:
        return MaterialGateResult("ANCHOR_COMPATIBLE", "All audited chemistry and disclosed property specifications match.")
    return MaterialGateResult("SURROGATE_ONLY", "No critical mismatch, but at least one material is only family/specification matched.")
