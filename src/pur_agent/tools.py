from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from pur_science.backward import solve_backward_threshold
from pur_science.canonical import BLEND, CID, ETA120, ETA80, MDI_FRACTION, MDI_PARTS, NCO, RATIO, CanonicalTable, canonicalize
from pur_science.frontier import (
    active_constraint_for, composition_family, compute_frontier, local_composition_trend, local_nco_trend,
)
from pur_science.objective import constraint_bounds, nominal_checks, robust_checks
from pur_science.reachability import check_reachability

_RECORD_COLS = [CID, BLEND, NCO, MDI_PARTS, MDI_FRACTION, ETA80, ETA120, RATIO, "property_score", "feasible_nominal"]


def _clean(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return None if np.isnan(obj) else float(obj)
    if isinstance(obj, float) and np.isnan(obj):
        return None
    return obj


@dataclass
class DecisionToolbox:
    """Deterministic tools exposed to the blind LLM.

    Every number returned here is computed by `pur_science`; nothing is re-implemented. The
    toolbox only ever sees the (anonymized) candidate table and the public benchmark config.
    """

    candidates: pd.DataFrame
    config: dict[str, Any]
    table: CanonicalTable = field(init=False)
    frontier: pd.DataFrame = field(init=False)

    def __post_init__(self) -> None:
        self.table = canonicalize(self.candidates, self.config)
        self.frontier = compute_frontier(self.table, self.config)

    # -- helpers -----------------------------------------------------------------------------
    def _records(self, d: pd.DataFrame, top_k: int) -> list[dict[str, Any]]:
        cols = [c for c in _RECORD_COLS if c in d.columns]
        for extra in ("robust_score", "feasible_robust", "property_rank", "nominal_rank", "robust_rank", "ea_two_point_kj_mol"):
            if extra in d.columns:
                cols.append(extra)
        return _clean(d.loc[:, cols].head(int(top_k)).to_dict(orient="records"))

    def _row(self, candidate_id: str) -> pd.Series:
        hit = self.frontier[self.frontier[CID] == str(candidate_id)]
        if hit.empty:
            raise KeyError(f"Unknown candidate: {candidate_id}")
        return hit.iloc[0]

    @property
    def robust_frozen(self) -> bool:
        return "robust_rank" in self.frontier.columns

    # -- tools ---------------------------------------------------------------------------------
    def dataset_summary(self) -> dict[str, Any]:
        f = self.frontier
        return _clean({
            "n_candidates": int(len(f)),
            "candidate_id_column": self.table.physical["candidate_id"],
            "components": self.table.components,
            "n_blends": int(f[BLEND].nunique()),
            "nco_oh_grid": sorted(float(x) for x in f[NCO].unique()),
            "mdi_fraction_range": [float(f[MDI_FRACTION].min()), float(f[MDI_FRACTION].max())],
            "response_columns": {"eta80": self.table.physical["eta80"], "eta120": self.table.physical["eta120"], "ratio": self.table.physical["ratio"]},
            "uncertainty_column_present": self.table.has_uncertainty,
            "domain_ratio_column_present": self.table.has_domain_ratio,
            "hard_constraints": constraint_bounds(self.config),
            "objective": self.config.get("objective"),
            "robust_layer_frozen": self.robust_frozen,
            "robustness_definition": self.config.get("robustness"),
            "n_feasible_nominal": int(f["feasible_nominal"].sum()),
            "n_feasible_robust": int(f["feasible_robust"].sum()) if self.robust_frozen else None,
        })

    def rank_property(self, top_k: int = 10) -> dict[str, Any]:
        d = self.frontier.sort_values("property_rank")
        return {"ranking": self._records(d, top_k), "n_ranked": int(len(d)), "definition": "weighted squared log10 distance to preferred-window centers; no constraints"}

    def rank_constrained(self, top_k: int = 10) -> dict[str, Any]:
        d = self.frontier[self.frontier["feasible_nominal"]].sort_values("nominal_rank")
        return {"ranking": self._records(d, top_k), "n_feasible": int(len(d)), "n_total": int(len(self.frontier)), "definition": "property objective restricted to candidates passing every nominal hard constraint"}

    def rank_robust(self, top_k: int = 10) -> dict[str, Any]:
        if not self.robust_frozen:
            raise RuntimeError("Robust ranking is not frozen in this benchmark config; abstain rather than inventing a robust score.")
        d = self.frontier[self.frontier["feasible_robust"]].sort_values("robust_rank")
        return {"ranking": self._records(d, top_k), "n_feasible_robust": int(len(d)), "robustness_definition": self.config.get("robustness")}

    def inspect_candidate(self, candidate_id: str) -> dict[str, Any]:
        row = self._row(candidate_id).to_dict()
        return _clean(row)

    def compare_candidates(self, candidate_ids: list[str]) -> dict[str, Any]:
        return {"candidates": [self.inspect_candidate(x) for x in candidate_ids]}

    def constraint_audit(self, candidate_id: str) -> dict[str, Any]:
        row = self._row(candidate_id)
        bounds = constraint_bounds(self.config)
        value_col = {"mdi_fraction": MDI_FRACTION, "nco_oh": NCO, "eta80_broad": ETA80, "eta80_preferred": ETA80,
                     "eta120_broad": ETA120, "eta120_preferred": ETA120, "ratio_broad": RATIO, "ratio_preferred": RATIO}
        checks = {}
        for col in self.frontier.columns:
            if col.startswith("check_"):
                name = col[len("check_"):]
                item: dict[str, Any] = {"pass": bool(row[col])}
                if name in value_col:
                    item["value"] = float(row[value_col[name]])
                if name in bounds:
                    item["bounds"] = bounds[name]
                checks[name] = item
        failures = [n for n, it in checks.items() if not it["pass"]]
        out = {"candidate_id": str(candidate_id), "checks": checks, "failures": failures, "feasible": not failures,
               "active_constraint": active_constraint_for(self.frontier, self.config, str(candidate_id))}
        if self.robust_frozen:
            rchecks = {c[len("robust_check_"):]: bool(row[c]) for c in self.frontier.columns if c.startswith("robust_check_")}
            out["robust_checks"] = rchecks
            out["feasible_robust"] = bool(row["feasible_robust"])
        return _clean(out)

    def calculate_mdi_fraction(self, mdi_parts: float) -> dict[str, Any]:
        basis = self.table.polyol_basis_parts
        return {"mdi_parts": float(mdi_parts), "polyol_basis_parts": basis, "mdi_fraction": float(mdi_parts) / (basis + float(mdi_parts))}

    def calculate_objective(self, candidate_id: str) -> dict[str, Any]:
        row = self._row(candidate_id)
        out = {"candidate_id": str(candidate_id), "property_score": float(row["property_score"]), "property_rank": int(row["property_rank"])}
        if self.robust_frozen:
            out["robust_score"] = float(row["robust_score"])
            out["robust_rank"] = None if np.isnan(row["robust_rank"]) else int(row["robust_rank"])
        return out

    def solve_backward_threshold(self, candidate_id: str) -> dict[str, Any]:
        threshold = float(self.config["hard_constraints"]["mdi_fraction_of_polyol_plus_mdi"][0])
        sol = solve_backward_threshold(self.table, str(candidate_id), threshold=threshold)
        return _clean(sol.to_dict())

    def check_reachability(self, candidate_id: str) -> dict[str, Any]:
        threshold = float(self.config["hard_constraints"]["mdi_fraction_of_polyol_plus_mdi"][0])
        sol = solve_backward_threshold(self.table, str(candidate_id), threshold=threshold)
        return _clean(check_reachability(self.table, sol).to_dict())

    def local_nco_sweep(self, candidate_id: str) -> dict[str, Any]:
        row = self._row(candidate_id)
        local = self.frontier[self.frontier[BLEND] == row[BLEND]].sort_values(NCO)
        trend = local_nco_trend(self.table, str(candidate_id))
        return _clean({"blend": str(row[BLEND]), "rows": self._records(local, len(local)), "eta80_direction_with_increasing_nco": trend["direction"]})

    def local_composition_sweep(self, candidate_id: str) -> dict[str, Any]:
        comps, fam = composition_family(self.table, str(candidate_id))
        fam_f = self.frontier[self.frontier[CID].isin(fam[CID])]
        trend = local_composition_trend(self.table, str(candidate_id))
        axis = trend.get("axis_component")
        if axis and axis in fam_f.columns:
            fam_f = fam_f.sort_values(axis)
        return _clean({
            "components": comps,
            "nco_oh": float(self._row(candidate_id)[NCO]),
            "axis_component": axis,
            "axis_definition": trend.get("axis_definition"),
            "other_component": trend.get("other_component"),
            "eta80_direction_with_increasing_axis_parts": trend["direction"],
            "rows": self._records(fam_f, len(fam_f)),
        })
