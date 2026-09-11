from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable


class StrategyStage(str, Enum):
    AUDIT = "audit"
    PROPERTY_RANKING = "property_ranking"
    CONSTRAINED_RANKING = "constrained_ranking"
    ROBUST_RANKING = "robust_ranking"
    BACKWARD = "backward"
    LOCAL_TRENDS = "local_trends"
    EVIDENCE_RECONCILIATION = "evidence_reconciliation"
    SELF_CHECK = "self_check"
    FINAL = "final"
    ABSTAIN = "abstain"


REQUIRED_TOOL_FAMILIES = {
    StrategyStage.AUDIT: {"dataset_summary"},
    StrategyStage.PROPERTY_RANKING: {"rank_property"},
    StrategyStage.CONSTRAINED_RANKING: {"rank_constrained"},
    StrategyStage.ROBUST_RANKING: {"rank_robust"},
    StrategyStage.BACKWARD: {"constraint_audit", "solve_backward_threshold", "check_reachability"},
    StrategyStage.LOCAL_TRENDS: {"local_nco_sweep", "local_composition_sweep"},
}


@dataclass(frozen=True)
class StrategyCheck:
    complete: bool
    missing_stages: tuple[str, ...]
    missing_tool_families: tuple[str, ...]
    can_finalize: bool
    reason: str


class RecoveryStrategy:
    """Policy guardrail for complete-decision recovery.

    The LLM may choose tool order, but it may not finalize a scientific decision until the
    deterministic decision chain has been inspected. This prevents a lucky winner guess from
    being scored as a complete scientific recovery. Tools that are not available in the
    current condition (ablations) are not required, so an ablated Agent can still finalize;
    it is then scored on what it could not recover.
    """

    stages: tuple[StrategyStage, ...] = (
        StrategyStage.AUDIT,
        StrategyStage.PROPERTY_RANKING,
        StrategyStage.CONSTRAINED_RANKING,
        StrategyStage.ROBUST_RANKING,
        StrategyStage.BACKWARD,
        StrategyStage.LOCAL_TRENDS,
        StrategyStage.EVIDENCE_RECONCILIATION,
        StrategyStage.SELF_CHECK,
        StrategyStage.FINAL,
    )

    def check_trace(self, tool_names: Iterable[str], *, robust_required: bool = True, available_tools: Iterable[str] | None = None) -> StrategyCheck:
        called = set(tool_names)
        required = self.required_families()
        if not robust_required:
            required.pop(StrategyStage.ROBUST_RANKING, None)
        available = set(available_tools) if available_tools is not None else None

        missing_stages: list[str] = []
        missing_tools: list[str] = []
        for stage, family in required.items():
            fam = family if available is None else (family & available)
            if not fam:
                continue
            if not fam.issubset(called):
                missing_stages.append(stage.value)
                missing_tools.extend(sorted(fam - called))

        complete = not missing_stages
        reason = (
            "complete deterministic decision chain inspected"
            if complete
            else "missing required deterministic evidence before finalization"
        )
        return StrategyCheck(
            complete=complete,
            missing_stages=tuple(missing_stages),
            missing_tool_families=tuple(missing_tools),
            can_finalize=complete,
            reason=reason,
        )

    def required_families(self) -> dict[StrategyStage, set[str]]:
        return dict(REQUIRED_TOOL_FAMILIES)

    def corrective_message(self, check: StrategyCheck) -> str:
        if check.can_finalize:
            return "The decision trace is complete. Perform a final consistency check and return JSON only."
        missing = ", ".join(check.missing_tool_families)
        return (
            "You attempted to finalize before completing the blinded scientific decision chain. "
            f"Call the missing deterministic tools first: {missing}. Do not guess the final answer."
        )


class StrategyStageV2(str, Enum):
    """PLAN -> SOLVE -> CHALLENGE -> CERTIFY -> EXPLAIN."""

    PLAN = "plan"
    SOLVE = "solve"
    CHALLENGE = "challenge"
    CERTIFY = "certify"
    EXPLAIN = "explain"
    CONFLICT = "conflict"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class V2Check:
    """Trace-state view with the same surface as `StrategyCheck`, plus the full V2 gate."""

    complete: bool
    missing_stages: tuple[str, ...]
    missing_tool_families: tuple[str, ...]
    can_finalize: bool
    reason: str
    gate: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class V2Policy:
    """Which parts of the V2 contract gate finalisation for this condition.

    `enforce=False` switches the machine gate off entirely: the run finalises on its first
    answer and the certificate is recorded post hoc only. That is the `no_certificate`
    ablation, in which the model's self-reported `confidence` is again the only trust signal.

    The gate is deliberately procedural. Its corrective message names missing evidence,
    unfinished stages, schema errors and non-canonical vocabulary — never which candidate is
    right — because that message is fed back into the model context and would otherwise be a
    gold side-channel.
    """

    config: dict[str, Any]
    enforce: bool = True
    require_evidence_plan: bool = True
    require_challenge: bool = True
    require_cross_path: bool = True
    cross_path_tolerance: float | None = None

    def evaluate(
        self,
        *,
        called_tools: Iterable[str],
        available_tools: Iterable[str] | None,
        trace: list[dict[str, Any]],
        final_text: str | None = None,
    ) -> V2Check:
        from .certificate import ontology_check, procedural_gate

        called = list(called_tools)
        gate = procedural_gate(
            called_tools=called, available_tools=available_tools, trace=trace, config=self.config,
            require_evidence_plan=self.require_evidence_plan, require_challenge=self.require_challenge,
            require_cross_path=self.require_cross_path, cross_path_tolerance=self.cross_path_tolerance,
        )
        reasons = list(gate["reasons"])
        gate["schema_valid"] = None
        if final_text is not None:
            decision, schema_error = parse_final_text(final_text)
            gate["schema_valid"] = schema_error is None
            if schema_error:
                reasons.append(f"The final JSON does not satisfy the V2 output schema: {schema_error}.")
            else:
                onto = ontology_check(decision)
                gate["ontology"] = onto
                if not onto["pass"]:
                    reasons.append("The canonical constraint ontology is violated: " + "; ".join(onto["violations"]) + ".")
        gate["reasons"] = reasons
        gate["can_finalize"] = not reasons
        missing = list(_missing_evidence_tools(gate))
        missing += [t for t in sorted(set(gate["challenge_tools_available"]) - set(called)) if t not in missing]
        return V2Check(
            complete=not reasons,
            missing_stages=tuple(gate["evidence_coverage"].get("missing_claims", ())),
            missing_tool_families=tuple(missing),
            can_finalize=(not reasons) if self.enforce else True,
            reason=("V2 evidence contract satisfied" if not reasons else " ".join(reasons)),
            gate=gate,
        )

    def message(self, check: V2Check) -> str:
        from .certificate import corrective_message

        return corrective_message(check.gate)


def _missing_evidence_tools(gate: dict[str, Any]) -> tuple[str, ...]:
    out: list[str] = []
    for claim in gate["evidence_coverage"].get("claims", []):
        if claim.get("admissible") and not claim.get("satisfied"):
            for tool in claim.get("missing_tools", []):
                if tool not in out:
                    out.append(tool)
    return tuple(out)


def parse_final_text(final_text: str) -> tuple[dict[str, Any] | None, str | None]:
    """Best-effort parse of the model's final answer, for the live V2 gate."""
    from .schemas import DecisionSchemaError, parse_decision_v2

    text = (final_text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    raw: Any
    try:
        raw = json.loads(text)
    except json.JSONDecodeError:
        a, b = text.find("{"), text.rfind("}")
        if a < 0 or b <= a:
            return None, "the output is not JSON"
        try:
            raw = json.loads(text[a:b + 1])
        except json.JSONDecodeError as exc:
            return None, str(exc)
    try:
        parse_decision_v2(raw)
    except DecisionSchemaError as exc:
        return (raw if isinstance(raw, dict) else None), str(exc)
    return raw, None


class AuditStage(str, Enum):
    COUNTERFACTUAL_CONSTRAINT = "counterfactual_constraint"
    COUNTERFACTUAL_UNCERTAINTY = "counterfactual_uncertainty"
    OBJECTIVE_STRUCTURE = "objective_structure"
    PARETO = "pareto"
    STABILITY = "stability"
    CONSISTENCY = "consistency"


AUDIT_TOOL_FAMILIES = {
    AuditStage.COUNTERFACTUAL_CONSTRAINT: {"constraint_counterfactual"},
    AuditStage.COUNTERFACTUAL_UNCERTAINTY: {"uncertainty_counterfactual"},
    AuditStage.OBJECTIVE_STRUCTURE: {"objective_structure_audit"},
    AuditStage.PARETO: {"pareto_alternatives"},
    AuditStage.STABILITY: {"weight_stability"},
    AuditStage.CONSISTENCY: {"consistency_report"},
}


class AuditStrategy(RecoveryStrategy):
    """PUR-AUDIT V1: the recovery chain plus every counterfactual family must be inspected
    before the auditor may finalize. Local sweeps are not required in audit mode."""

    def required_families(self) -> dict:
        base = {k: v for k, v in REQUIRED_TOOL_FAMILIES.items() if k is not StrategyStage.LOCAL_TRENDS}
        base.update(AUDIT_TOOL_FAMILIES)
        return base
