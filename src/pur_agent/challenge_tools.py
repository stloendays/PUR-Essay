"""Scientific challenge tools (PUR-RECOVER V2, Stage C).

V1 ended with a self-check: the Agent re-read its own notes. V2 requires it to actively try
to falsify the recommendation it is about to issue, using read-only deterministic
counterfactuals.

Every function here is a thin wrapper over `pur_science.depth` — the same primitives already
frozen for PUR-AUDIT V1 (`constraint_counterfactual`, `uncertainty_counterfactual`,
`score_crossover`, `uncertainty_scale_phase`, `consistency_report`). No science is
reimplemented and nothing here can change the objective, constraints, uncertainty rule,
frontier or gold.

The difference from the audit-mode wrappers in `audit_tools.py` is deliberate: these take
the Agent's **own asserted claims** as arguments and return a verdict on those claims. They
do not hand back the deterministic decision chain, so the challenge stage cannot be used as
a shortcut to the answer it is meant to interrogate.

Challenge questions covered, in the order the V2 spec requires them:
  1. why does the L0 winner stop winning once nominal constraints apply?
  2. why does the L1 winner stop winning under the frozen robust rule?
  3. is the claimed robust winner close to a boundary or an objective crossover?
  4. do any tool outputs contradict each other?
"""
from __future__ import annotations

from typing import Any

from pur_science.canonical import CID, MDI_FRACTION, NCO
from pur_science.depth import (
    consistency_report, constraint_counterfactual, score_crossover, uncertainty_counterfactual,
    uncertainty_scale_phase,
)
from pur_science.frontier import active_constraint_for

from .ontology import canonical_from_active_constraint, constraint_bounds_for
from .tools import DecisionToolbox, _clean

CHALLENGE_TOOL_NAMES = (
    "challenge_constraint_relaxation",
    "challenge_uncertainty",
    "challenge_boundary",
    "challenge_consistency",
)

# The challenge stage is complete once the Agent has interrogated all three scientific
# mechanisms and run the contradiction check.
REQUIRED_CHALLENGE_TOOLS = frozenset(CHALLENGE_TOOL_NAMES)


class ChallengeToolbox(DecisionToolbox):
    """Recover-mode challenge wrappers. Read-only; claim-driven; frozen science untouched."""

    def _require(self, candidate_id: str) -> str:
        cid = str(candidate_id)
        if cid not in set(self.frontier[CID].astype(str)):
            raise KeyError(f"Unknown candidate: {candidate_id}")
        return cid

    # -- 1. why L0 loses under nominal constraints -------------------------------------------
    def challenge_constraint_relaxation(self, claimed_property_winner: str, claimed_constrained_winner: str) -> dict[str, Any]:
        l0 = self._require(claimed_property_winner)
        l1 = self._require(claimed_constrained_winner)
        row = self._row(l0)
        active = active_constraint_for(self.frontier, self.config, l0)
        canonical = canonical_from_active_constraint(active, self.config)
        quantity = (canonical or {}).get("quantity")
        bounds = constraint_bounds_for(self.config, quantity) if quantity else None
        margin = None
        if active.get("threshold") is not None and active.get("candidate_value") is not None:
            margin = float(active["candidate_value"]) - float(active["threshold"])
        cc = constraint_counterfactual(self.frontier, self.config, layer="nominal")
        return _clean({
            "question": "why does the claimed property-only winner stop winning once nominal constraints apply?",
            "claimed_property_winner": l0,
            "claimed_constrained_winner": l1,
            "property_winner_nominally_feasible": bool(row["feasible_nominal"]),
            "active_constraint": canonical,
            "active_constraint_bounds": bounds,
            "candidate_value": active.get("candidate_value"),
            "signed_margin_to_binding_bound": margin,
            "all_failed_checks": active.get("all_failures", []),
            "claimed_constrained_winner_is_winner_at_frozen_floor": bool(cc.get("current_winner") == l1),
            "claimed_constrained_winner_nominally_feasible": bool(self._row(l1)["feasible_nominal"]),
            "mdi_floor_stability_interval": cc.get("winner_stable_for_floor_in"),
            "floor_increase_to_change_winner": cc.get("floor_increase_to_change_winner"),
            "floor_decrease_to_change_winner": cc.get("floor_decrease_to_change_winner"),
            "winner_if_floor_raised": cc.get("winner_if_floor_raised"),
            "winner_if_floor_lowered": cc.get("winner_if_floor_lowered"),
            "verdict": (
                "consistent: the claimed property winner is nominally infeasible and the claimed constrained winner wins at the frozen floor"
                if (not bool(row["feasible_nominal"])) and cc.get("current_winner") == l1
                else "challenge: the claimed layer separation is not reproduced by the frozen constraint counterfactual"
            ),
        })

    # -- 2. why L1 loses under the robust rule -----------------------------------------------
    def challenge_uncertainty(self, claimed_constrained_winner: str, claimed_robust_winner: str) -> dict[str, Any]:
        if not self.robust_frozen:
            raise RuntimeError("Robust layer is not frozen in this config; no uncertainty challenge is defined")
        l1 = self._require(claimed_constrained_winner)
        l2 = self._require(claimed_robust_winner)
        uc = uncertainty_counterfactual(self.frontier, self.config, l1, l2)
        crossover = (uc.get("crossover") or {}).get("crossover_scales") or []
        return _clean({
            "question": "why does the claimed constrained winner stop winning under the frozen robust rule?",
            "claimed_constrained_winner": l1,
            "claimed_robust_winner": l2,
            "same_winner": uc.get("same_winner"),
            "mechanism": uc.get("mechanism"),
            "l1_winner_robust_admissible": uc.get("l1_winner_robust_admissible"),
            "l1_l2_crossover_uncertainty_scale": crossover[0] if crossover else None,
            "bottleneck_response": (uc.get("crossover") or {}).get("bottleneck_b"),
            "robust_winner_stable_for_scale_in": uc.get("robust_winner_stable_for_scale_in"),
            "claimed_robust_winner_robust_feasible": bool(self._row(l2)["feasible_robust"]),
        })

    # -- 3. boundary / crossover proximity ---------------------------------------------------
    def challenge_boundary(self, claimed_robust_winner: str) -> dict[str, Any]:
        l2 = self._require(claimed_robust_winner)
        row = self._row(l2)
        score_col = "robust_score" if self.robust_frozen else "property_score"
        feas_col = "feasible_robust" if self.robust_frozen else "feasible_nominal"
        pool = self.frontier[self.frontier[feas_col] & (self.frontier[CID].astype(str) != l2)]
        competitor = None
        objective_margin = None
        crossover = None
        if not pool.empty:
            best = pool.sort_values(score_col).iloc[0]
            competitor = str(best[CID])
            objective_margin = float(row[score_col]) - float(best[score_col])
            if self.robust_frozen:
                try:
                    crossover = score_crossover(self.frontier, self.config, l2, competitor)
                except Exception:  # diagnostic only; never fails the challenge
                    crossover = None
        floor_bounds = constraint_bounds_for(self.config, "mdi_fraction")
        floor_margin = (float(row[MDI_FRACTION]) - float(floor_bounds[0])) if floor_bounds else None
        scale_interval = None
        if self.robust_frozen:
            phase = uncertainty_scale_phase(self.frontier, self.config)
            cur = next((p for p in phase if p["s_lo"] - 1e-12 <= 1.0 <= p["s_hi"] + 1e-12), None)
            scale_interval = [cur["s_lo"], cur["s_hi"]] if cur else None
        near = bool(objective_margin is not None and abs(objective_margin) < 0.05 * max(abs(float(row[score_col])), 1e-12))
        return _clean({
            "question": "is the claimed robust winner close to a decision boundary or an objective crossover?",
            "claimed_robust_winner": l2,
            "scored_layer": score_col,
            "claimed_score": float(row[score_col]),
            "nearest_competitor": competitor,
            "objective_margin": objective_margin,
            "objective_margin_note": "claimed score minus the best score among the other admissible candidates; negative means the claim is ahead",
            "nco_oh": float(row[NCO]),
            "mdi_fraction": float(row[MDI_FRACTION]),
            "mdi_floor_margin": floor_margin,
            "uncertainty_scale_stability_interval": scale_interval,
            "crossover": crossover,
            "near_objective_crossover": near,
        })

    # -- 4. mutual consistency of the claimed chain ------------------------------------------
    def challenge_consistency(
        self,
        claimed_property_winner: str,
        claimed_constrained_winner: str,
        claimed_robust_winner: str | None = None,
        active_constraint_quantity: str | None = None,
        continuous_threshold: float | None = None,
        nearest_reachable_grid_value: float | None = None,
        nearest_reachable_candidate_id: str | None = None,
    ) -> dict[str, Any]:
        """Run the frozen consistency checks against the chain the Agent is about to submit."""
        from .ontology import normalize_quantity

        quantity, _ = normalize_quantity(active_constraint_quantity)
        decision = {
            "property_winner": self._require(claimed_property_winner),
            "constrained_winner": self._require(claimed_constrained_winner),
            "robust_winner": self._require(claimed_robust_winner) if claimed_robust_winner else None,
            "active_constraint": {"name": quantity or active_constraint_quantity},
            "backward_design": {
                "continuous_threshold": continuous_threshold,
                "nearest_reachable_grid_value": nearest_reachable_grid_value,
                "nearest_reachable_candidate_id": nearest_reachable_candidate_id,
            },
        }
        report = consistency_report(self.frontier, self.config, decision)
        return _clean({
            "question": "do the claimed decision fields contradict each other under the frozen definitions?",
            "claimed_chain": {k: decision[k] for k in ("property_winner", "constrained_winner", "robust_winner")},
            "checks": _redact_reveals(report["checks"]),
            "contradictions": report["contradictions"],
            "n_contradictions": report["n_contradictions"],
        })


def _redact_reveals(checks: dict[str, Any]) -> dict[str, Any]:
    """Keep the verdicts, drop detail strings that would name the frozen answer.

    `consistency_report` writes the true global property minimiser into its detail string. A
    challenge tool must report that the claim fails, not supply the replacement; the Agent has
    `rank_property` for that. The boolean verdict is untouched.
    """
    out = dict(checks)
    key = "l0_is_global_property_min"
    if key in out and isinstance(out[key], dict):
        item = dict(out[key])
        item["detail"] = "claimed property winner compared against the frozen property ranking"
        out[key] = item
    return out


def challenge_tools_called(called: list[str] | tuple[str, ...]) -> set[str]:
    return {name for name in called if name in REQUIRED_CHALLENGE_TOOLS}


def challenge_complete(called: list[str] | tuple[str, ...], available: set[str] | None = None) -> bool:
    """Complete when every challenge tool available in this condition has been used."""
    required = REQUIRED_CHALLENGE_TOOLS if available is None else (REQUIRED_CHALLENGE_TOOLS & set(available))
    if not required:
        return True
    return required.issubset(set(called))
