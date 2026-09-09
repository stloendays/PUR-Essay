from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .strategy import RecoveryStrategy
from .tools import DecisionToolbox


def _fn(name: str, description: str, properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "function",
        "name": name,
        "description": description,
        "parameters": {"type": "object", "properties": properties, "required": required or [], "additionalProperties": False},
        "strict": True,
    }


_CID = {"candidate_id": {"type": "string", "description": "Candidate ID exactly as it appears in the table"}}
_TOPK = {"top_k": {"type": "integer", "minimum": 1, "maximum": 30}}

ALL_TOOL_DEFINITIONS: list[dict[str, Any]] = [
    _fn("dataset_summary", "Audit the candidate table, constraints, objective and which decision layers are frozen. Call first.", {}),
    _fn("rank_property", "Rank all candidates by the frozen property objective only (no constraints).", _TOPK, ["top_k"]),
    _fn("rank_constrained", "Apply every frozen nominal hard constraint and rank feasible candidates by the property objective.", _TOPK, ["top_k"]),
    _fn("rank_robust", "Rank candidates by the frozen robust (worst-case interval) objective among robust-feasible candidates. Errors if robustness is not frozen; then abstain.", _TOPK, ["top_k"]),
    _fn("inspect_candidate", "Return every descriptor, response and score of one candidate.", _CID, ["candidate_id"]),
    _fn("compare_candidates", "Side-by-side descriptors of 2-10 candidates.", {"candidate_ids": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 10}}, ["candidate_ids"]),
    _fn("constraint_audit", "Exact pass/fail of every hard constraint for one candidate, with the active (binding) constraint.", _CID, ["candidate_id"]),
    _fn("calculate_mdi_fraction", "MDI mass fraction of polyol+MDI for a given MDI parts value on the 100-part polyol basis.", {"mdi_parts": {"type": "number"}}, ["mdi_parts"]),
    _fn("calculate_objective", "Property score (and robust score if frozen) plus ranks for one candidate.", _CID, ["candidate_id"]),
    _fn("solve_backward_threshold", "Continuous minimum NCO:OH at which this candidate's blend reaches the MDI-fraction lower bound.", _CID, ["candidate_id"]),
    _fn("check_reachability", "Project the continuous backward threshold onto the discrete NCO:OH grid of the same blend.", _CID, ["candidate_id"]),
    _fn("local_nco_sweep", "All NCO:OH grid points of the same blend with responses and the eta80 direction.", _CID, ["candidate_id"]),
    _fn("local_composition_sweep", "All blends of the same two-component family at the same NCO:OH, sorted along the data-defined composition axis.", _CID, ["candidate_id"]),
]
ALL_TOOL_NAMES = tuple(d["name"] for d in ALL_TOOL_DEFINITIONS)


@dataclass
class ToolboxExecutor:
    """Bridges LLM function calls to the deterministic toolbox and records the full trace."""

    toolbox: DecisionToolbox
    allowed_tools: tuple[str, ...] | None = None
    enforce_strategy: bool = True
    robust_required: bool = True
    called_tools: list[str] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)

    def tool_definitions(self) -> list[dict[str, Any]]:
        if self.allowed_tools is None:
            return list(ALL_TOOL_DEFINITIONS)
        allowed = set(self.allowed_tools)
        return [d for d in ALL_TOOL_DEFINITIONS if d["name"] in allowed]

    @property
    def available_tool_names(self) -> set[str]:
        return {d["name"] for d in self.tool_definitions()}

    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in self.available_tool_names:
            payload = {"ok": False, "error_type": "ToolNotAllowed", "error": f"Tool not available in this condition: {name}"}
        else:
            try:
                result = getattr(self.toolbox, name)(**arguments)
                payload = {"ok": True, "result": result}
            except Exception as exc:  # deterministic tool errors are data for the LLM, not crashes
                payload = {"ok": False, "error_type": type(exc).__name__, "error": str(exc)}
        self.called_tools.append(name)
        self.trace.append({"tool": name, "arguments": arguments, "output": payload})
        return payload

    def strategy_check(self):
        return RecoveryStrategy().check_trace(self.called_tools, robust_required=self.robust_required, available_tools=self.available_tool_names)

    def finalization_guard(self) -> tuple[bool, str]:
        if not self.enforce_strategy:
            return True, ""
        check = self.strategy_check()
        return check.can_finalize, RecoveryStrategy().corrective_message(check)


# Backwards-compatible alias used by the cloud runner.
StrategyEnforcingExecutor = ToolboxExecutor
