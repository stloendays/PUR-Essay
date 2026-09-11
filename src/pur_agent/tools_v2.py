"""V2 toolbox: the V1 deterministic tools plus the challenge wrappers, speaking one ontology.

Only the *presentation* of a constraint changes. Every number still comes from `pur_science`
through `DecisionToolbox`; no objective, constraint, uncertainty rule or ranking is touched.

The V1 pilot's one strict-audit failure was caused here: `solve_backward_threshold` returns
`constraint: "mdi_fraction_min"` while the frozen gold names the same constraint
`mdi_fraction`, and a model that copied the tool's own wording was scored wrong for a
scientifically correct answer. The V2 wrappers emit the canonical object everywhere, so the
trap no longer exists for V2 conditions. The V1 tools and the frozen `pur_science` field
names are left exactly as they were, so the V1 pilot stays reproducible.
"""
from __future__ import annotations

from typing import Any

from .challenge_tools import ChallengeToolbox
from .ontology import CANONICAL_VERSION, canonical_constraint, canonical_from_active_constraint, constraint_bounds_for
from .tools import _clean

# Quantities whose canonical form is published to the Agent in dataset_summary.
_PUBLISHED_QUANTITIES = (
    "mdi_fraction", "nco_oh", "eta80_broad", "eta120_broad", "ratio_broad",
    "eta80_preferred", "eta120_preferred", "ratio_preferred",
)


class V2Toolbox(ChallengeToolbox):
    """Deterministic tools + challenge tools, with canonical constraint objects attached."""

    # -- ontology surface --------------------------------------------------------------------
    def canonical_constraints(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for quantity in _PUBLISHED_QUANTITIES:
            bounds = constraint_bounds_for(self.config, quantity)
            if not bounds:
                continue
            lo, hi = bounds
            out.append({"quantity": quantity, "operator": ">=", "threshold": lo})
            out.append({"quantity": quantity, "operator": "<=", "threshold": hi})
        if (self.config.get("hard_constraints") or {}).get("require_chemistry_in_domain"):
            out.append({"quantity": "chemistry_in_domain", "operator": "is_true", "threshold": None})
        dr = (self.config.get("robustness") or {}).get("domain_ratio_max")
        if dr is not None:
            out.append({"quantity": "domain_ratio", "operator": "<=", "threshold": float(dr)})
        return out

    def dataset_summary(self) -> dict[str, Any]:
        out = super().dataset_summary()
        out["ontology_version"] = CANONICAL_VERSION
        out["canonical_constraints"] = self.canonical_constraints()
        out["ontology_note"] = (
            "Refer to every constraint by its canonical {quantity, operator, threshold} object. "
            "`quantity` is the scientific quantity name; do not append 'min'/'max' to it."
        )
        return out

    def constraint_audit(self, candidate_id: str) -> dict[str, Any]:
        out = super().constraint_audit(candidate_id)
        active = out.get("active_constraint") or {}
        canonical = canonical_from_active_constraint(active, self.config)
        if canonical:
            active["canonical"] = canonical
            out["active_constraint"] = active
            out["active_constraint_canonical"] = canonical
        for name, item in (out.get("checks") or {}).items():
            try:
                item["canonical_quantity"] = canonical_constraint(name, bounds=item.get("bounds"))["quantity"]
            except Exception:  # unknown check names stay as-is; never fail an audit on vocabulary
                continue
        return _clean(out)

    def solve_backward_threshold(self, candidate_id: str) -> dict[str, Any]:
        out = super().solve_backward_threshold(candidate_id)
        canonical = canonical_constraint("mdi_fraction_min", threshold=out.get("threshold"))
        out["constraint"] = canonical["quantity"]          # canonical spelling replaces mdi_fraction_min
        out["constraint_canonical"] = canonical
        return _clean(out)

    def check_reachability(self, candidate_id: str) -> dict[str, Any]:
        out = super().check_reachability(candidate_id)
        out["constraint_canonical"] = canonical_constraint(
            "mdi_fraction_min",
            threshold=(constraint_bounds_for(self.config, "mdi_fraction") or [None])[0],
        )
        return _clean(out)

    def calculate_mdi_fraction(self, mdi_parts: float) -> dict[str, Any]:
        out = super().calculate_mdi_fraction(mdi_parts)
        bounds = constraint_bounds_for(self.config, "mdi_fraction")
        if bounds:
            out["constraint_canonical"] = canonical_constraint("mdi_fraction_min", threshold=bounds[0])
            out["satisfies_floor"] = bool(out["mdi_fraction"] >= bounds[0])
        return _clean(out)
