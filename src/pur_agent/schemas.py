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
    if isinstance(ac_raw, dict) and ac_raw.get("name"):
        ac = ActiveConstraint(
            name=str(ac_raw["name"]),
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
