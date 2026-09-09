from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .strategy import RecoveryStrategy
from .tools import DecisionToolbox


@dataclass
class ToolboxExecutor:
    toolbox: DecisionToolbox

    def tool_definitions(self) -> list[dict[str, Any]]:
        def fn(name: str, description: str, properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
            return {
                "type": "function",
                "name": name,
                "description": description,
                "parameters": {"type": "object", "properties": properties, "required": required or [], "additionalProperties": False},
                "strict": True,
            }
        cid = {"candidate_id": {"type": "string"}}
        return [
            fn("dataset_summary", "Audit the blinded candidate table before making decisions.", {}),
            fn("rank_property", "Rank all candidates by the frozen property objective only.", {"top_k": {"type": "integer", "minimum": 1, "maximum": 30}}, ["top_k"]),
            fn("rank_constrained", "Apply frozen nominal hard constraints and rank feasible candidates.", {"top_k": {"type": "integer", "minimum": 1, "maximum": 30}}, ["top_k"]),
            fn("rank_robust", "Apply the frozen robustness definition; if it is not frozen, the deterministic tool will return an error and the Agent must abstain.", {"top_k": {"type": "integer", "minimum": 1, "maximum": 30}}, ["top_k"]),
            fn("inspect_candidate", "Inspect one anonymized candidate in detail.", cid, ["candidate_id"]),
            fn("compare_candidates", "Compare a short list of anonymized candidates.", {"candidate_ids": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 10}}, ["candidate_ids"]),
            fn("constraint_audit", "Return exact nominal hard-constraint checks and failures for one candidate.", cid, ["candidate_id"]),
            fn("solve_backward_threshold", "Solve the continuous NCO:OH threshold needed to cross the MDI-fraction lower bound for a candidate's blend.", cid, ["candidate_id"]),
            fn("check_reachability", "Project the continuous backward threshold onto the discrete candidate grid.", cid, ["candidate_id"]),
            fn("local_nco_sweep", "Inspect all NCO:OH grid points for the same blend as the candidate.", cid, ["candidate_id"]),
            fn("local_composition_sweep", "Inspect local composition alternatives at the candidate's NCO:OH.", cid, ["candidate_id"]),
        ]

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        func = getattr(self.toolbox, name, None)
        if func is None or name.startswith("_"):
            raise KeyError(f"Tool not allowed: {name}")
        return func(**arguments)


class StrategyEnforcingExecutor(ToolboxExecutor):
    def __post_init__(self) -> None:
        self.called_tools: list[str] = []

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        if not hasattr(self, "called_tools"):
            self.called_tools = []
        try:
            result = super().execute(name, arguments)
            payload = {"ok": True, "result": result}
        except Exception as exc:
            payload = {"ok": False, "error_type": type(exc).__name__, "error": str(exc)}
        self.called_tools.append(name)
        return payload

    def strategy_check(self):
        return RecoveryStrategy().check_trace(self.called_tools, robust_required=True)

    def finalization_guard(self) -> tuple[bool, str]:
        check = self.strategy_check()
        return check.can_finalize, RecoveryStrategy().corrective_message(check)
