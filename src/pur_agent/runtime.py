from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .strategy import RecoveryStrategy, V2Policy
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

_LAYER = {"layer": {"type": "string", "enum": ["nominal", "robust"]}}
AUDIT_TOOL_DEFINITIONS: list[dict[str, Any]] = [
    _fn("constraint_counterfactual", "Phase map of the winner versus the MDI-fraction floor: how far the frozen floor can move before the winner changes, and to whom.", _LAYER, ["layer"]),
    _fn("uncertainty_counterfactual", "Why L1 and L2 differ (worst-case objective vs admissibility gate), the uncertainty scale at which they cross, and the scale range over which the robust winner is stable.", {}),
    _fn("score_crossover", "Uncertainty scales at which two candidates' robust scores are equal, with their broad-window bottlenecks.", {"candidate_a": {"type": "string"}, "candidate_b": {"type": "string"}}, ["candidate_a", "candidate_b"]),
    _fn("weight_stability", "Fraction of random objective-weight vectors under which each candidate wins (frozen seed and sample count).", _LAYER, ["layer"]),
    _fn("pareto_alternatives", "Non-dominated robust-admissible candidates on |log distance| per response, uncertainty radius and domain ratio.", {}),
    _fn("objective_structure_audit", "Whether the frozen objective double-counts (eta80 = eta120 * ratio) and the induced principal weight ratio.", {}),
    _fn("consistency_report", "Internal consistency checks of the deterministic decision chain; lists contradictions.", {}),
]
AUDIT_TOOL_NAMES = tuple(d["name"] for d in AUDIT_TOOL_DEFINITIONS)

# ------------------------------------------------------------------- PUR-RECOVER V2 stage C
# Read-only counterfactual challenges. Each takes the Agent's own claims and returns a verdict
# on them; none of them returns the deterministic decision chain.
CHALLENGE_TOOL_DEFINITIONS: list[dict[str, Any]] = [
    _fn("challenge_constraint_relaxation",
        "Challenge 1: why does your claimed property-only winner stop winning once nominal constraints apply? Returns its canonical active constraint, the signed margin to the binding bound, and how far the MDI floor must move before the nominal winner changes.",
        {"claimed_property_winner": {"type": "string"}, "claimed_constrained_winner": {"type": "string"}},
        ["claimed_property_winner", "claimed_constrained_winner"]),
    _fn("challenge_uncertainty",
        "Challenge 2: why does your claimed constrained winner stop winning under the frozen robust rule? Returns the divergence mechanism, the uncertainty scale at which the two cross, and the scale range over which your claimed robust winner is stable.",
        {"claimed_constrained_winner": {"type": "string"}, "claimed_robust_winner": {"type": "string"}},
        ["claimed_constrained_winner", "claimed_robust_winner"]),
    _fn("challenge_boundary",
        "Challenge 3: is your claimed robust winner near a decision boundary or an objective crossover? Returns the objective margin to the nearest competitor, the MDI-floor margin and the uncertainty-scale stability interval.",
        {"claimed_robust_winner": {"type": "string"}}, ["claimed_robust_winner"]),
    _fn("challenge_consistency",
        "Challenge 4: do the decision fields you are about to submit contradict each other under the frozen definitions? Pass your own claims; returns per-check verdicts and the contradiction list.",
        {"claimed_property_winner": {"type": "string"},
         "claimed_constrained_winner": {"type": "string"},
         "claimed_robust_winner": {"type": "string"},
         "active_constraint_quantity": {"type": "string"},
         "continuous_threshold": {"type": "number"},
         "nearest_reachable_grid_value": {"type": "number"},
         "nearest_reachable_candidate_id": {"type": "string"}},
        ["claimed_property_winner", "claimed_constrained_winner", "claimed_robust_winner",
         "active_constraint_quantity", "continuous_threshold", "nearest_reachable_grid_value",
         "nearest_reachable_candidate_id"]),
]
CHALLENGE_TOOL_NAMES = tuple(d["name"] for d in CHALLENGE_TOOL_DEFINITIONS)
V2_TOOL_NAMES = ALL_TOOL_NAMES + CHALLENGE_TOOL_NAMES


@dataclass
class ToolboxExecutor:
    """Bridges LLM function calls to the deterministic toolbox and records the full trace."""

    toolbox: DecisionToolbox
    allowed_tools: tuple[str, ...] | None = None
    enforce_strategy: bool = True
    robust_required: bool = True
    strategy: RecoveryStrategy = field(default_factory=RecoveryStrategy)
    include_audit_tools: bool = False
    include_challenge_tools: bool = False
    v2_policy: V2Policy | None = None
    called_tools: list[str] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    gate_attempts: list[dict[str, Any]] = field(default_factory=list)

    def tool_definitions(self) -> list[dict[str, Any]]:
        defs = list(ALL_TOOL_DEFINITIONS)
        if self.include_audit_tools:
            defs += list(AUDIT_TOOL_DEFINITIONS)
        if self.include_challenge_tools:
            defs += list(CHALLENGE_TOOL_DEFINITIONS)
        if self.allowed_tools is None:
            return defs
        allowed = set(self.allowed_tools)
        return [d for d in defs if d["name"] in allowed]

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

    def strategy_check(self, final_text: str | None = None):
        if self.v2_policy is not None:
            return self.v2_policy.evaluate(called_tools=self.called_tools, available_tools=self.available_tool_names,
                                           trace=self.trace, final_text=final_text)
        return self.strategy.check_trace(self.called_tools, robust_required=self.robust_required, available_tools=self.available_tool_names)

    def finalization_guard(self, final_text: str | None = None) -> tuple[bool, str]:
        """Called when the model stops requesting tools.

        V2 also inspects the candidate final answer, so schema validity and canonical
        vocabulary are part of the gate rather than a post-hoc complaint. Every attempt is
        recorded, which is what makes "was the FIRST answer already schema-clean?" measurable
        instead of being hidden by the retry.
        """
        if self.v2_policy is not None:
            check = self.v2_policy.evaluate(called_tools=self.called_tools, available_tools=self.available_tool_names,
                                            trace=self.trace, final_text=final_text)
            gate = check.gate
            self.gate_attempts.append({
                "attempt": len(self.gate_attempts) + 1,
                "can_finalize": gate.get("can_finalize"),
                "reasons": gate.get("reasons", []),
                "schema_valid": gate.get("schema_valid"),
                "ontology_pass": (gate.get("ontology") or {}).get("pass"),
                "ontology_violations": (gate.get("ontology") or {}).get("violations", []),
                "evidence_satisfied": gate["evidence_coverage"].get("satisfied"),
                "evidence_required": gate["evidence_coverage"].get("required"),
                "challenge_completed": gate.get("challenge_completed"),
                "cross_path_status": (gate.get("cross_path") or {}).get("status"),
            })
            if not self.v2_policy.enforce:
                return True, ""
            return check.can_finalize, self.v2_policy.message(check)
        if not self.enforce_strategy:
            return True, ""
        check = self.strategy_check()
        return check.can_finalize, self.strategy.corrective_message(check)


# Backwards-compatible alias used by the cloud runner.
StrategyEnforcingExecutor = ToolboxExecutor
