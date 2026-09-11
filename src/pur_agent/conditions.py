from __future__ import annotations

from dataclasses import dataclass

from .runtime import ALL_TOOL_NAMES, AUDIT_TOOL_NAMES, CHALLENGE_TOOL_NAMES, V2_TOOL_NAMES


@dataclass(frozen=True)
class Condition:
    name: str
    description: str
    uses_llm: bool = True
    use_tools: bool = True
    tools: tuple[str, ...] | None = None          # None = every tool of the mode
    enforce_strategy: bool = True                  # finalization guard on incomplete trace
    system_prompt: str = "recover_v1_system.txt"
    task_prompt: str = "recover_v1_task.txt"
    include_provenance: bool = True
    inline_data: bool = False                      # embed the compressed table in the task text
    mode: str = "recover"                          # "recover" (primary) or "audit" (secondary PUR-AUDIT V1)
    # ------------------------------------------------------------------ PUR-RECOVER V2 only
    schema_version: str = "v1"                     # "v2" enables the claim-evidence contract
    require_evidence_plan: bool = False            # gate on minimum-sufficient evidence per claim
    require_challenge: bool = False                # gate on the counterfactual challenge stage
    require_cross_path: bool = False               # gate on dual-path threshold verification
    enforce_certificate: bool = False              # certificate gates finalisation (else logged only)


_NO_BACKWARD = tuple(t for t in ALL_TOOL_NAMES if t not in ("solve_backward_threshold", "check_reachability"))
_NO_CONSTRAINT = tuple(t for t in ALL_TOOL_NAMES if t not in ("constraint_audit", "rank_constrained", "rank_robust"))
_V2_NO_CHALLENGE = tuple(t for t in V2_TOOL_NAMES if t not in CHALLENGE_TOOL_NAMES)


def _v2(name: str, description: str, **overrides: object) -> Condition:
    """A PUR-RECOVER V2 condition. Defaults are the full contract; each ablation drops one part."""
    base: dict[str, object] = dict(
        system_prompt="recover_v2_system.txt", task_prompt="recover_v2_task.txt", schema_version="v2",
        require_evidence_plan=True, require_challenge=True, require_cross_path=True, enforce_certificate=True,
    )
    base.update(overrides)
    return Condition(name, description, **base)  # type: ignore[arg-type]

CONDITIONS: dict[str, Condition] = {
    "oracle": Condition("oracle", "Baseline 0: deterministic frontier, not an Agent; gold reference computed on the blind table.", uses_llm=False, use_tools=False, enforce_strategy=False),
    "direct_llm": Condition("direct_llm", "Baseline 1: compressed complete data in context, no deterministic tools.", use_tools=False, enforce_strategy=False, system_prompt="direct_llm_system.txt", inline_data=True),
    "tool_llm": Condition("tool_llm", "Baseline 2: deterministic tools available, no strategy enforcement, plain task prompt.", enforce_strategy=False, system_prompt="tool_llm_system.txt"),
    "pur_agent": Condition("pur_agent", "Baseline 3: full PUR-Agent — planning, inspection, constraint checking, calculation, backward analysis, evidence reconciliation, self-check, gated finalization."),
    "pur_agent_no_backward": Condition("pur_agent_no_backward", "Ablation: PUR-Agent without the backward-threshold and reachability tools.", tools=_NO_BACKWARD),
    "pur_agent_no_constraint_checker": Condition("pur_agent_no_constraint_checker", "Ablation: PUR-Agent without constraint audit / constrained and robust ranking tools.", tools=_NO_CONSTRAINT),
    "pur_agent_no_provenance": Condition("pur_agent_no_provenance", "Ablation: PUR-Agent without the source/provenance block in the task.", include_provenance=False),
    "pur_agent_single_pass": Condition("pur_agent_single_pass", "Ablation: PUR-Agent prompt but the run is accepted on the first final answer (no finalization guard).", enforce_strategy=False),
    # --------------------------------------------------------------------- PUR-RECOVER V2
    # Separately versioned. The frozen science, gold and primary metric are identical to V1;
    # only the way the Agent reaches, challenges, certifies and explains the answer changes.
    "pur_agent_v2": _v2("pur_agent_v2",
                        "PUR-Agent V2: PLAN -> SOLVE -> CHALLENGE -> CERTIFY -> EXPLAIN. Claim-level minimum-sufficient evidence planning, deterministic solve, counterfactual challenge, dual-path threshold verification, canonical constraint ontology and a machine-computed decision certificate."),
    "pur_agent_v2_no_evidence_planner": _v2("pur_agent_v2_no_evidence_planner",
                                            "V2 ablation: no claim-evidence contract; challenge, cross-path and ontology gates remain.",
                                            require_evidence_plan=False),
    "pur_agent_v2_no_challenge": _v2("pur_agent_v2_no_challenge",
                                     "V2 ablation: counterfactual challenge tools removed and not required.",
                                     tools=_V2_NO_CHALLENGE, require_challenge=False),
    "pur_agent_v2_no_cross_path": _v2("pur_agent_v2_no_cross_path",
                                      "V2 ablation: dual-path threshold verification recorded but not required.",
                                      require_cross_path=False),
    "pur_agent_v2_no_certificate": _v2("pur_agent_v2_no_certificate",
                                       "V2 ablation: no machine gate at all; the certificate is computed post hoc and the model's own confidence is the only trust signal.",
                                       enforce_certificate=False, enforce_strategy=False),
    # Secondary mode. Same blind bundle, same frozen contract; different task and scorer.
    "pur_audit": Condition("pur_audit", "PUR-AUDIT V1: blinded decision audit — why layers differ, counterfactual constraint/uncertainty thresholds, reachability, objective double-counting, Pareto alternatives, stability, hypothesis, contradictions.",
                           system_prompt="audit_v1_system.txt", task_prompt="audit_v1_task.txt", mode="audit"),
}

AUDIT_TOOLS = ALL_TOOL_NAMES + AUDIT_TOOL_NAMES


def get_condition(name: str) -> Condition:
    try:
        return CONDITIONS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown condition {name!r}; choose from {sorted(CONDITIONS)}") from exc
