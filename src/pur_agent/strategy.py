from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class StrategyStage(str, Enum):
    AUDIT = "audit"
    PROPERTY_RANKING = "property_ranking"
    CONSTRAINED_RANKING = "constrained_ranking"
    ROBUST_RANKING = "robust_ranking"
    BACKWARD = "backward"
    LOCAL_TRENDS = "local_trends"
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

    The LLM may choose tool order, but it may not finalize a scientific decision
    until the deterministic decision chain has been inspected. This prevents a
    lucky winner guess from being scored as a complete scientific recovery.
    """

    stages: tuple[StrategyStage, ...] = (
        StrategyStage.AUDIT,
        StrategyStage.PROPERTY_RANKING,
        StrategyStage.CONSTRAINED_RANKING,
        StrategyStage.ROBUST_RANKING,
        StrategyStage.BACKWARD,
        StrategyStage.LOCAL_TRENDS,
        StrategyStage.SELF_CHECK,
        StrategyStage.FINAL,
    )

    def check_trace(self, tool_names: Iterable[str], *, robust_required: bool = True) -> StrategyCheck:
        called = set(tool_names)
        required = dict(REQUIRED_TOOL_FAMILIES)
        if not robust_required:
            required.pop(StrategyStage.ROBUST_RANKING, None)

        missing_stages: list[str] = []
        missing_tools: list[str] = []
        for stage, family in required.items():
            if not family.issubset(called):
                missing_stages.append(stage.value)
                missing_tools.extend(sorted(family - called))

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

    def corrective_message(self, check: StrategyCheck) -> str:
        if check.can_finalize:
            return "The decision trace is complete. Perform a final consistency check and return JSON only."
        missing = ", ".join(check.missing_tool_families)
        return (
            "You attempted to finalize before completing the blinded scientific decision chain. "
            f"Call the missing deterministic tools first: {missing}. Do not guess the final answer."
        )
