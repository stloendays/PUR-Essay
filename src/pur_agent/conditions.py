from __future__ import annotations

from dataclasses import dataclass

from .runtime import ALL_TOOL_NAMES


@dataclass(frozen=True)
class Condition:
    name: str
    description: str
    uses_llm: bool = True
    use_tools: bool = True
    tools: tuple[str, ...] | None = None          # None = every tool
    enforce_strategy: bool = True                  # finalization guard on incomplete trace
    system_prompt: str = "recover_v1_system.txt"
    include_provenance: bool = True
    inline_data: bool = False                      # embed the compressed table in the task text


_NO_BACKWARD = tuple(t for t in ALL_TOOL_NAMES if t not in ("solve_backward_threshold", "check_reachability"))
_NO_CONSTRAINT = tuple(t for t in ALL_TOOL_NAMES if t not in ("constraint_audit", "rank_constrained", "rank_robust"))

CONDITIONS: dict[str, Condition] = {
    "oracle": Condition("oracle", "Baseline 0: deterministic frontier, not an Agent; gold reference computed on the blind table.", uses_llm=False, use_tools=False, enforce_strategy=False),
    "direct_llm": Condition("direct_llm", "Baseline 1: compressed complete data in context, no deterministic tools.", use_tools=False, enforce_strategy=False, system_prompt="direct_llm_system.txt", inline_data=True),
    "tool_llm": Condition("tool_llm", "Baseline 2: deterministic tools available, no strategy enforcement, plain task prompt.", enforce_strategy=False, system_prompt="tool_llm_system.txt"),
    "pur_agent": Condition("pur_agent", "Baseline 3: full PUR-Agent — planning, inspection, constraint checking, calculation, backward analysis, self-check, gated finalization."),
    "pur_agent_no_backward": Condition("pur_agent_no_backward", "Ablation: PUR-Agent without the backward-threshold and reachability tools.", tools=_NO_BACKWARD),
    "pur_agent_no_constraint_checker": Condition("pur_agent_no_constraint_checker", "Ablation: PUR-Agent without constraint audit / constrained and robust ranking tools.", tools=_NO_CONSTRAINT),
    "pur_agent_no_provenance": Condition("pur_agent_no_provenance", "Ablation: PUR-Agent without the source/provenance block in the task.", include_provenance=False),
    "pur_agent_single_pass": Condition("pur_agent_single_pass", "Ablation: PUR-Agent prompt but the run is accepted on the first final answer (no finalization guard).", enforce_strategy=False),
}


def get_condition(name: str) -> Condition:
    try:
        return CONDITIONS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown condition {name!r}; choose from {sorted(CONDITIONS)}") from exc
