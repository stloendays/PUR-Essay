from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Direction = Literal["increase", "decrease", "mixed", "flat", "unknown"]
DIRECTIONS = ("increase", "decrease", "mixed", "flat", "unknown")


@dataclass(frozen=True)
class ActiveConstraint:
    name: str
    threshold: float | None = None
    candidate_value: float | None = None
    evidence: str = ""


@dataclass(frozen=True)
class BackwardDesign:
    variable: str
    continuous_threshold: float | None
    nearest_reachable_grid_value: float | None
    reachable: bool | None
    active_constraint: str = ""


@dataclass(frozen=True)
class LocalTrends:
    nco_direction: Direction = "unknown"
    composition_axis: str | None = None
    composition_direction: Direction = "unknown"
    notes: str = ""


@dataclass(frozen=True)
class AgentDecision:
    """Final Agent output. Field meanings are fixed by docs/AGENT_STRATEGY_V1.md."""

    property_winner: str | None
    constrained_winner: str | None
    robust_winner: str | None
    active_constraint: ActiveConstraint | None
    backward_design: BackwardDesign | None
    local_trends: LocalTrends = field(default_factory=LocalTrends)
    evidence: tuple[str, ...] = ()
    final_reasoning_summary: str = ""
    confidence: float | None = None
    abstain: bool = False
    abstention_reason: str | None = None
    robust_abstention_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DecisionSchemaError(ValueError):
    pass


def _opt_float(value: Any, name: str) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise DecisionSchemaError(f"{name} must be a number or null, got {value!r}") from exc


def _opt_str(value: Any, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise DecisionSchemaError(f"{name} must be a non-empty string or null, got {value!r}")
    return value.strip()


def _direction(value: Any, name: str) -> Direction:
    if value is None:
        return "unknown"
    if value not in DIRECTIONS:
        raise DecisionSchemaError(f"{name} must be one of {DIRECTIONS}, got {value!r}")
    return value  # type: ignore[return-value]


def parse_decision(raw: dict[str, Any]) -> AgentDecision:
    """Validate a raw JSON object from the LLM into the typed schema.

    Unknown keys are ignored. Missing optional blocks become None so the evaluator scores
    them as not recovered instead of crashing.
    """
    if not isinstance(raw, dict):
        raise DecisionSchemaError("decision must be a JSON object")
    ac_raw = raw.get("active_constraint")
    ac = None
    # V2 answers name the constraint with the canonical `quantity`; V1 answers use `name`.
    # Either populates `name`, so one evaluator scores both versions.
    if isinstance(ac_raw, dict) and (ac_raw.get("name") or ac_raw.get("quantity")):
        ac = ActiveConstraint(
            name=str(ac_raw.get("name") or ac_raw.get("quantity")),
            threshold=_opt_float(ac_raw.get("threshold"), "active_constraint.threshold"),
            candidate_value=_opt_float(ac_raw.get("candidate_value"), "active_constraint.candidate_value"),
            evidence=str(ac_raw.get("evidence", "")),
        )
    bw_raw = raw.get("backward_design")
    bw = None
    if isinstance(bw_raw, dict):
        reachable = bw_raw.get("reachable")
        if reachable is not None and not isinstance(reachable, bool):
            raise DecisionSchemaError("backward_design.reachable must be boolean or null")
        bw = BackwardDesign(
            variable=str(bw_raw.get("variable", "nco_oh")),
            continuous_threshold=_opt_float(bw_raw.get("continuous_threshold"), "backward_design.continuous_threshold"),
            nearest_reachable_grid_value=_opt_float(bw_raw.get("nearest_reachable_grid_value"), "backward_design.nearest_reachable_grid_value"),
            reachable=reachable,
            active_constraint=str(bw_raw.get("active_constraint", "")),
        )
    lt_raw = raw.get("local_trends") or {}
    if not isinstance(lt_raw, dict):
        raise DecisionSchemaError("local_trends must be an object")
    lt = LocalTrends(
        nco_direction=_direction(lt_raw.get("nco_direction"), "local_trends.nco_direction"),
        composition_axis=_opt_str(lt_raw.get("composition_axis"), "local_trends.composition_axis"),
        composition_direction=_direction(lt_raw.get("composition_direction"), "local_trends.composition_direction"),
        notes=str(lt_raw.get("notes", "")),
    )
    evidence = raw.get("evidence") or []
    if not isinstance(evidence, list):
        raise DecisionSchemaError("evidence must be a list of strings")
    return AgentDecision(
        property_winner=_opt_str(raw.get("property_winner"), "property_winner"),
        constrained_winner=_opt_str(raw.get("constrained_winner"), "constrained_winner"),
        robust_winner=_opt_str(raw.get("robust_winner"), "robust_winner"),
        active_constraint=ac,
        backward_design=bw,
        local_trends=lt,
        evidence=tuple(str(x) for x in evidence),
        final_reasoning_summary=str(raw.get("final_reasoning_summary", "")),
        confidence=_opt_float(raw.get("confidence"), "confidence"),
        abstain=bool(raw.get("abstain", False)),
        abstention_reason=_opt_str(raw.get("abstention_reason"), "abstention_reason"),
        robust_abstention_reason=_opt_str(raw.get("robust_abstention_reason"), "robust_abstention_reason"),
    )


# ------------------------------------------------------------------ PUR-RECOVER V2 schema
DECISION_STATUSES = ("final", "conflict", "abstain")
CONFLICT_KINDS = ("cross_path_disagreement", "tool_contradiction", "insufficient_evidence", "other")


@dataclass(frozen=True)
class AgentDecisionV2:
    """V2 final output: the V1 decision plus the machine-checkable V2 blocks.

    Every V1 field keeps its V1 meaning, so the same evaluator and the same primary metric
    apply to both versions. `active_constraint` additionally carries the canonical ontology
    fields `quantity` and `operator`; a legacy `name` spelling is still parsed and is scored
    as a schema defect rather than a scientific one.
    """

    decision: AgentDecision
    decision_status: str = "final"
    evidence_plan: tuple[dict[str, Any], ...] = ()
    cross_path_verification: dict[str, Any] | None = None
    challenge: dict[str, Any] | None = None
    conflicts: tuple[dict[str, Any], ...] = ()
    certificate_claimed: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        out = self.decision.to_dict()
        out.update({
            "decision_status": self.decision_status,
            "evidence_plan": list(self.evidence_plan),
            "cross_path_verification": self.cross_path_verification,
            "challenge": self.challenge,
            "conflicts": list(self.conflicts),
            "certificate_claimed": self.certificate_claimed,
        })
        return out


def parse_decision_v2(raw: dict[str, Any]) -> AgentDecisionV2:
    """Validate a V2 answer. Superset of `parse_decision`; unknown keys are still ignored."""
    base = parse_decision(raw)
    status = raw.get("decision_status") or "final"
    if status not in DECISION_STATUSES:
        raise DecisionSchemaError(f"decision_status must be one of {DECISION_STATUSES}, got {status!r}")

    ac_raw = raw.get("active_constraint")
    if isinstance(ac_raw, dict) and (ac_raw.get("quantity") or ac_raw.get("name")):
        if not ac_raw.get("quantity"):
            raise DecisionSchemaError("active_constraint must carry the canonical 'quantity' field in V2")
        if not ac_raw.get("operator"):
            raise DecisionSchemaError("active_constraint must carry the canonical 'operator' field in V2")

    plan = raw.get("evidence_plan") or []
    if not isinstance(plan, list):
        raise DecisionSchemaError("evidence_plan must be a list of {claim, evidence} objects")
    for item in plan:
        if not isinstance(item, dict) or not item.get("claim"):
            raise DecisionSchemaError("each evidence_plan entry must be an object with a 'claim'")

    cpv = raw.get("cross_path_verification")
    if cpv is not None and not isinstance(cpv, dict):
        raise DecisionSchemaError("cross_path_verification must be an object or null")
    challenge = raw.get("challenge")
    if challenge is not None and not isinstance(challenge, dict):
        raise DecisionSchemaError("challenge must be an object or null")

    conflicts = raw.get("conflicts") or []
    if not isinstance(conflicts, list):
        raise DecisionSchemaError("conflicts must be a list")
    for c in conflicts:
        if not isinstance(c, dict) or not c.get("kind"):
            raise DecisionSchemaError("each conflict must be an object with a 'kind'")
        if c["kind"] not in CONFLICT_KINDS:
            raise DecisionSchemaError(f"unknown conflict kind {c['kind']!r}; use one of {CONFLICT_KINDS}")
    if status == "conflict" and not conflicts:
        raise DecisionSchemaError("decision_status 'conflict' requires at least one entry in conflicts")

    cert = raw.get("certificate_claimed")
    if cert is not None and not isinstance(cert, dict):
        raise DecisionSchemaError("certificate_claimed must be an object or null")

    return AgentDecisionV2(
        decision=base,
        decision_status=str(status),
        evidence_plan=tuple(plan),
        cross_path_verification=cpv,
        challenge=challenge,
        conflicts=tuple(conflicts),
        certificate_claimed=cert,
    )


AUDIT_REQUIRED_BLOCKS = ("layer_divergence", "constraint_counterfactual", "uncertainty_counterfactual", "reachability",
                         "objective_structure", "pareto_alternatives", "stability", "hypothesis_to_test", "contradictions")


def parse_audit_report(raw: dict[str, Any]) -> dict[str, Any]:
    """Structural validation of a PUR-AUDIT V1 report. Missing blocks are allowed (scored as not
    recovered) but present blocks must have the right container type."""
    if not isinstance(raw, dict):
        raise DecisionSchemaError("audit report must be a JSON object")
    for key in ("layer_divergence", "constraint_counterfactual", "uncertainty_counterfactual", "reachability", "objective_structure", "stability", "hypothesis_to_test"):
        if key in raw and raw[key] is not None and not isinstance(raw[key], dict):
            raise DecisionSchemaError(f"{key} must be an object")
    for key in ("pareto_alternatives", "contradictions", "evidence"):
        if key in raw and raw[key] is not None and not isinstance(raw[key], list):
            raise DecisionSchemaError(f"{key} must be a list")
    if "abstain" in raw and not isinstance(raw["abstain"], bool):
        raise DecisionSchemaError("abstain must be boolean")
    ld = raw.get("layer_divergence") or {}
    mech = ld.get("l1_l2_mechanism")
    if mech is not None and mech not in ("worst_case_objective", "robust_admissibility_gate", "identical", "not_frozen"):
        raise DecisionSchemaError(f"unknown l1_l2_mechanism {mech!r}")
    return raw
