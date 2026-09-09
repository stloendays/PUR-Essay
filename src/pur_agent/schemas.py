from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Direction = Literal["increase", "decrease", "mixed", "flat", "unknown"]


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
    composition_direction: Direction = "unknown"
    notes: str = ""


@dataclass(frozen=True)
class AgentDecision:
    property_winner: str | None
    constrained_winner: str | None
    robust_winner: str | None
    active_constraint: ActiveConstraint | None
    backward_design: BackwardDesign | None
    local_trends: LocalTrends = field(default_factory=LocalTrends)
    evidence: tuple[str, ...] = ()
    confidence: float | None = None
    abstain: bool = False
    abstention_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
