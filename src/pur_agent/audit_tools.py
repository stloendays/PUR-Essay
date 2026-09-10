from __future__ import annotations

from typing import Any

from pur_science.depth import (
    consistency_report, constraint_counterfactual, objective_structure_audit, pareto_alternatives, score_crossover,
    uncertainty_counterfactual, weight_stability,
)
from pur_science.frontier import frontier_decision

from .tools import DecisionToolbox, _clean


class AuditToolbox(DecisionToolbox):
    """PUR-AUDIT V1 tools. Every method is a thin wrapper over `pur_science.depth`; nothing here can
    alter the objective, constraints, uncertainty rule or gold. The LLM only chooses what to ask."""

    def _chain(self) -> dict[str, Any]:
        d = frontier_decision(self.table, self.config)
        return {k: d[k] for k in ("property_winner", "constrained_winner", "robust_winner", "active_constraint", "backward_design", "robust_layer_frozen")}

    def constraint_counterfactual(self, layer: str = "robust") -> dict[str, Any]:
        return _clean(constraint_counterfactual(self.frontier, self.config, layer=layer))

    def uncertainty_counterfactual(self) -> dict[str, Any]:
        chain = self._chain()
        if not chain["robust_layer_frozen"]:
            raise RuntimeError("Robust layer is not frozen; no uncertainty counterfactual is defined")
        return _clean(uncertainty_counterfactual(self.frontier, self.config, chain["constrained_winner"], chain["robust_winner"]))

    def score_crossover(self, candidate_a: str, candidate_b: str) -> dict[str, Any]:
        return _clean(score_crossover(self.frontier, self.config, str(candidate_a), str(candidate_b)))

    def weight_stability(self, layer: str = "robust") -> dict[str, Any]:
        a = self.config.get("audit", {})
        return _clean(weight_stability(self.frontier, self.config, layer=layer, samples=int(a.get("weight_samples", 50000)), seed=int(a.get("weight_seed", 20260909))))

    def pareto_alternatives(self) -> dict[str, Any]:
        return _clean(pareto_alternatives(self.frontier, self.config))

    def objective_structure_audit(self) -> dict[str, Any]:
        return _clean(objective_structure_audit(self.config))

    def consistency_report(self) -> dict[str, Any]:
        chain = self._chain()
        return _clean({"decision_chain": chain, **consistency_report(self.frontier, self.config, chain)})
