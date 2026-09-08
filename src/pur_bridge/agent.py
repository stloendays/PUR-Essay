from __future__ import annotations
from dataclasses import dataclass
from .anchors import AnchorMechanismModel
from .acquisition import binary_gaussian_information_gain

@dataclass(frozen=True)
class AgentDecision:
    action: str
    candidate_id: str | None
    reason: str
    information_gain_nats: float | None = None

class ExperimentAgent:
    """Auditable decision layer. An LLM may narrate decisions but may not alter them."""
    def __init__(self, model: AnchorMechanismModel):
        self.model = model

    def round1(self, sigma_log: float = 0.10, material_gate: str = "ANCHOR_COMPATIBLE") -> AgentDecision:
        aliases = {"PASS": "ANCHOR_COMPATIBLE", "PARTIAL": "SURROGATE_ONLY", "FAIL": "INCOMPATIBLE"}
        gate = aliases.get(material_gate.upper(), material_gate.upper())
        if gate == "INCOMPATIBLE":
            return AgentDecision(
                action="abstain_and_redesign_modern_system",
                candidate_id=None,
                reason="Material-equivalence gate is incompatible; absolute comparison with historical anchors is not defensible.",
            )
        if gate == "AUDIT_REQUIRED":
            return AgentDecision(
                action="audit_material_equivalence",
                candidate_id=None,
                reason="Critical material evidence is incomplete; resolve identity/specification evidence before spending the prospective experiment.",
            )
        if gate not in {"ANCHOR_COMPATIBLE", "SURROGATE_ONLY"}:
            return AgentDecision(
                action="audit_material_equivalence",
                candidate_id=None,
                reason=f"Unrecognized material-gate state: {gate}.",
            )
        p = self.model.predictions()
        ig = binary_gaussian_information_gain(p["H_strong"].log_eta, p["H_weak"].log_eta, sigma_log)
        qualifier = (
            "patent-anchored prospective counterfactual"
            if gate == "ANCHOR_COMPATIBLE"
            else "specification-matched surrogate transfer test"
        )
        return AgentDecision(
            action="run_experiment",
            candidate_id="E6_star",
            information_gain_nats=ig,
            reason=f"Material gate={gate}. E6_star is the unique missing C-rich/high-A counterfactual; interpret as {qualifier}.",
        )

    def after_e6(self, eta_e6_pa_s: float) -> AgentDecision:
        return self.after_e6_summary(eta_e6_pa_s, None, None, n_batches=3)

    def after_e6_summary(
        self,
        eta_e6_pa_s: float,
        ci95_low_pa_s: float | None,
        ci95_high_pa_s: float | None,
        n_batches: int,
    ) -> AgentDecision:
        theta = self.model.context_transfer_theta(eta_e6_pa_s)
        if n_batches < 3:
            return AgentDecision(
                action="replicate_E6_star",
                candidate_id="E6_star",
                reason=f"Only {n_batches} independent E6* batch(es); preregistered minimum is 3. theta={theta:.3f}",
            )
        cls = self.model.classify(eta_e6_pa_s)
        if cls == "indeterminate":
            return AgentDecision(
                action="replicate_E6_star",
                candidate_id="E6_star",
                reason=f"E6* mean is in the preregistered no-decision zone; reduce experimental uncertainty before expanding chemistry. theta={theta:.3f}",
            )
        if ci95_low_pa_s is not None and ci95_high_pa_s is not None:
            if cls == "strong_consistent" and ci95_low_pa_s < 40.0:
                return AgentDecision(
                    action="replicate_E6_star",
                    candidate_id="E6_star",
                    reason=f"Point estimate is strong-consistent but the 95% batch CI crosses 40 Pa.s; replicate before transfer. theta={theta:.3f}",
                )
            if cls == "weak_consistent" and ci95_high_pa_s > 33.0:
                return AgentDecision(
                    action="replicate_E6_star",
                    candidate_id="E6_star",
                    reason=f"Point estimate is weak-consistent but the 95% batch CI crosses 33 Pa.s; replicate before transfer. theta={theta:.3f}",
                )
        return AgentDecision(
            action="evaluate_transfer_pool",
            candidate_id=None,
            reason=f"E6* is {cls} with adequate independent-batch precision; freeze mechanism state (theta={theta:.3f}) and rank transfer candidates with hard support gates. Abstain if none passes.",
        )
