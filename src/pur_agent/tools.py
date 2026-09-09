from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .config import candidate_id_column


def _window_center(bounds: Iterable[float]) -> float:
    lo, hi = [float(x) for x in bounds]
    if lo <= 0 or hi <= 0:
        raise ValueError("Log-space objective requires positive preferred-window bounds.")
    return math.sqrt(lo * hi)


def _between(s: pd.Series, bounds: Iterable[float]) -> pd.Series:
    lo, hi = [float(x) for x in bounds]
    return s.ge(lo) & s.le(hi)


@dataclass
class DecisionToolbox:
    """Deterministic tools exposed to the blind LLM.

    Input data should already be anonymized for the primary benchmark. The
    toolbox never reads evaluator gold files and never converts anonymous IDs
    back to source IDs.
    """

    candidates: pd.DataFrame
    config: dict[str, Any]

    def __post_init__(self) -> None:
        self.df = self.candidates.copy()
        cols = self.config.get("columns", {})
        self.id_col = candidate_id_column(list(self.df.columns), cols.get("candidate_id"))

    @property
    def columns(self) -> dict[str, str]:
        c = self.config.get("columns", {})
        required = {
            "eta80": "eta80_pa_s",
            "eta120": "eta120_pa_s",
            "ratio": "ratio_80_120",
            "nco_oh": "nco_oh",
            "mdi_parts": "mdi_parts",
        }
        out = {}
        for key, fallback in required.items():
            name = c.get(key, fallback)
            if name not in self.df.columns:
                raise KeyError(f"Configured column {key}={name!r} not present in candidate table")
            out[key] = name
        for key in ("domain_ratio", "uncertainty_radius", "chemistry_in_domain", "blend"):
            name = c.get(key)
            if name:
                if name not in self.df.columns:
                    raise KeyError(f"Configured column {key}={name!r} not present in candidate table")
                out[key] = name
        return out

    def _base(self) -> pd.DataFrame:
        d = self.df.copy()
        c = self.columns
        basis = float(self.config.get("polyol_basis_parts", 100.0))
        d["_mdi_fraction_total"] = d[c["mdi_parts"]] / (basis + d[c["mdi_parts"]])
        hc = self.config["hard_constraints"]
        centers = {
            "eta80": _window_center(hc["eta80_preferred_pa_s"]),
            "eta120": _window_center(hc["eta120_preferred_pa_s"]),
            "ratio": _window_center(hc["ratio_preferred"]),
        }
        weights = self.config.get("objective", {}).get(
            "weights", {"eta80": 1.0, "eta120": 1.0, "ratio": 1.0}
        )
        d["_property_score"] = (
            float(weights.get("eta80", 1.0)) * np.log10(d[c["eta80"]] / centers["eta80"]) ** 2
            + float(weights.get("eta120", 1.0)) * np.log10(d[c["eta120"]] / centers["eta120"]) ** 2
            + float(weights.get("ratio", 1.0)) * np.log10(d[c["ratio"]] / centers["ratio"]) ** 2
        )
        return d

    def dataset_summary(self) -> dict[str, Any]:
        d = self._base()
        return {
            "n_candidates": int(len(d)),
            "candidate_id_column": self.id_col,
            "columns": list(d.columns),
            "nco_oh_range": [float(d[self.columns["nco_oh"]].min()), float(d[self.columns["nco_oh"]].max())],
            "mdi_fraction_range": [float(d["_mdi_fraction_total"].min()), float(d["_mdi_fraction_total"].max())],
        }

    def _records(self, d: pd.DataFrame, top_k: int = 10) -> list[dict[str, Any]]:
        c = self.columns
        keep = [self.id_col]
        if "blend" in c:
            keep.append(c["blend"])
        keep += [c["nco_oh"], c["mdi_parts"], "_mdi_fraction_total", c["eta80"], c["eta120"], c["ratio"], "_property_score"]
        for extra in ("_robust_score", "_feasible"):
            if extra in d.columns:
                keep.append(extra)
        return d.loc[:, list(dict.fromkeys(keep))].head(top_k).to_dict(orient="records")

    def rank_property(self, top_k: int = 10) -> dict[str, Any]:
        d = self._base().sort_values(["_property_score", self.id_col], kind="mergesort")
        return {"ranking": self._records(d, top_k), "n_ranked": int(len(d))}

    def _feasibility(self, d: pd.DataFrame) -> pd.Series:
        c = self.columns
        hc = self.config["hard_constraints"]
        ok = (
            _between(d[c["nco_oh"]], hc["nco_oh"])
            & _between(d["_mdi_fraction_total"], hc["mdi_fraction_of_polyol_plus_mdi"])
            & _between(d[c["eta80"]], hc["eta80_preferred_pa_s"])
            & _between(d[c["eta120"]], hc["eta120_preferred_pa_s"])
            & _between(d[c["ratio"]], hc["ratio_preferred"])
        )
        if hc.get("require_chemistry_in_domain", False):
            col = c.get("chemistry_in_domain")
            if not col:
                raise KeyError("require_chemistry_in_domain=true but columns.chemistry_in_domain is not configured")
            ok &= d[col].astype(bool)
        return ok

    def rank_constrained(self, top_k: int = 10) -> dict[str, Any]:
        d = self._base()
        d["_feasible"] = self._feasibility(d)
        feasible = d[d["_feasible"]].sort_values(["_property_score", self.id_col], kind="mergesort")
        return {
            "ranking": self._records(feasible, top_k),
            "n_feasible": int(len(feasible)),
            "n_total": int(len(d)),
        }

    def rank_robust(self, top_k: int = 10) -> dict[str, Any]:
        d = self._base()
        d["_feasible"] = self._feasibility(d)
        r = self.config.get("robustness")
        if not r or not r.get("enabled", False):
            raise RuntimeError("Robust ranking is not frozen in this benchmark config; abstain rather than inventing a robust score.")
        c = self.columns
        domain_col = c.get("domain_ratio")
        unc_col = c.get("uncertainty_radius")
        if not domain_col or not unc_col:
            raise KeyError("Robust ranking requires columns.domain_ratio and columns.uncertainty_radius")
        wd = float(r.get("domain_weight", 1.0))
        wu = float(r.get("uncertainty_weight", 1.0))
        domain_ref = float(r.get("domain_reference", 1.0))
        d["_robust_score"] = (
            d["_property_score"]
            + wd * np.maximum(d[domain_col] - domain_ref, 0.0) ** 2
            + wu * d[unc_col].astype(float) ** 2
        )
        feasible = d[d["_feasible"]].sort_values(["_robust_score", "_property_score", self.id_col], kind="mergesort")
        return {
            "ranking": self._records(feasible, top_k),
            "n_feasible": int(len(feasible)),
            "robustness_definition": r,
        }

    def inspect_candidate(self, candidate_id: str) -> dict[str, Any]:
        d = self._base()
        hit = d[d[self.id_col].astype(str) == str(candidate_id)]
        if hit.empty:
            raise KeyError(f"Unknown candidate: {candidate_id}")
        row = hit.iloc[0].to_dict()
        row["_feasible"] = bool(self._feasibility(hit).iloc[0])
        return row

    def compare_candidates(self, candidate_ids: list[str]) -> dict[str, Any]:
        return {"candidates": [self.inspect_candidate(x) for x in candidate_ids]}

    def constraint_audit(self, candidate_id: str) -> dict[str, Any]:
        d = self._base()
        c = self.columns
        hc = self.config["hard_constraints"]
        hit = d[d[self.id_col].astype(str) == str(candidate_id)]
        if hit.empty:
            raise KeyError(f"Unknown candidate: {candidate_id}")
        row = hit.iloc[0]
        checks = {
            "nco_oh": {"value": float(row[c["nco_oh"]]), "bounds": hc["nco_oh"], "pass": bool(_between(hit[c["nco_oh"]], hc["nco_oh"]).iloc[0])},
            "mdi_fraction": {"value": float(row["_mdi_fraction_total"]), "bounds": hc["mdi_fraction_of_polyol_plus_mdi"], "pass": bool(_between(hit["_mdi_fraction_total"], hc["mdi_fraction_of_polyol_plus_mdi"]).iloc[0])},
            "eta80_preferred": {"value": float(row[c["eta80"]]), "bounds": hc["eta80_preferred_pa_s"], "pass": bool(_between(hit[c["eta80"]], hc["eta80_preferred_pa_s"]).iloc[0])},
            "eta120_preferred": {"value": float(row[c["eta120"]]), "bounds": hc["eta120_preferred_pa_s"], "pass": bool(_between(hit[c["eta120"]], hc["eta120_preferred_pa_s"]).iloc[0])},
            "ratio_preferred": {"value": float(row[c["ratio"]]), "bounds": hc["ratio_preferred"], "pass": bool(_between(hit[c["ratio"]], hc["ratio_preferred"]).iloc[0])},
        }
        if hc.get("require_chemistry_in_domain", False):
            col = c["chemistry_in_domain"]
            checks["chemistry_in_domain"] = {"value": bool(row[col]), "pass": bool(row[col])}
        failures = [name for name, item in checks.items() if not item["pass"]]
        return {"candidate_id": candidate_id, "checks": checks, "failures": failures, "feasible": not failures}

    def solve_backward_threshold(self, candidate_id: str, *, constraint: str = "mdi_fraction_min") -> dict[str, Any]:
        if constraint != "mdi_fraction_min":
            raise ValueError("Current backward solver supports mdi_fraction_min only")
        c = self.columns
        if "blend" not in c:
            raise KeyError("Backward threshold requires columns.blend")
        target = self.inspect_candidate(candidate_id)
        blend_value = target[c["blend"]]
        d = self._base()
        local = d[d[c["blend"]] == blend_value].copy().sort_values(c["nco_oh"])
        if len(local) < 2:
            raise RuntimeError("Need at least two NCO:OH grid points for the same blend")
        threshold = float(self.config["hard_constraints"]["mdi_fraction_of_polyol_plus_mdi"][0])
        y = local["_mdi_fraction_total"].to_numpy(dtype=float)
        x = local[c["nco_oh"]].to_numpy(dtype=float)
        if not (np.min(y) <= threshold <= np.max(y)):
            return {"constraint": constraint, "threshold": threshold, "continuous_threshold": None, "reachable": False, "reason": "threshold lies outside the local candidate manifold"}
        order = np.argsort(y)
        continuous = float(np.interp(threshold, y[order], x[order]))
        reachable_values = x[y >= threshold]
        nearest = float(np.min(reachable_values)) if len(reachable_values) else None
        return {
            "constraint": constraint,
            "threshold": threshold,
            "blend": blend_value,
            "continuous_threshold": continuous,
            "nearest_reachable_grid_value": nearest,
            "reachable": nearest is not None,
        }

    def check_reachability(self, candidate_id: str, *, constraint: str = "mdi_fraction_min") -> dict[str, Any]:
        solved = self.solve_backward_threshold(candidate_id, constraint=constraint)
        return {
            "candidate_id": candidate_id,
            "reachable": solved.get("reachable"),
            "continuous_threshold": solved.get("continuous_threshold"),
            "nearest_reachable_grid_value": solved.get("nearest_reachable_grid_value"),
        }

    def local_nco_sweep(self, candidate_id: str) -> dict[str, Any]:
        c = self.columns
        if "blend" not in c:
            raise KeyError("Local NCO sweep requires columns.blend")
        target = self.inspect_candidate(candidate_id)
        d = self._base()
        local = d[d[c["blend"]] == target[c["blend"]]].sort_values(c["nco_oh"])
        return {"blend": target[c["blend"]], "rows": self._records(local, len(local))}

    def local_composition_sweep(self, candidate_id: str) -> dict[str, Any]:
        c = self.columns
        target = self.inspect_candidate(candidate_id)
        nco = target[c["nco_oh"]]
        d = self._base()
        local = d[np.isclose(d[c["nco_oh"]].astype(float), float(nco))].sort_values("_property_score")
        return {"nco_oh": float(nco), "rows": self._records(local, min(len(local), 30))}
