"""Deterministic decision certificate (PUR-RECOVER V2, Stage F).

V1's only trust signal was a number the model wrote about itself (`confidence: 0.92`). V2
replaces it with a certificate computed by the harness from the recorded tool trace, the
frozen config and the blind candidate table. `confidence` survives for backward
compatibility but is no longer the trust anchor.

Two deliberately separate things live here:

`procedural_gate`  runs **during** the run and decides whether the Agent may finalise. It
    checks only process: evidence coverage, challenge completion, cross-path surfacing,
    canonical ontology. It must never tell the model that an answer is wrong, because the
    corrective message is fed back into the model context and would be a gold side-channel.

`build_certificate`  runs **after** the run and records the full diagnostic set, including
    self-consistency facts (is the claimed constrained winner actually nominally feasible?)
    and margins. These are computed on the blind table from information the Agent already
    had, never from the evaluator gold, and are never returned to the model.

The certificate does not ask "is this the right candidate?". Rank optimality is evaluator
territory; a certificate that encoded it would be a disguised oracle.
"""
from __future__ import annotations

from typing import Any, Iterable

from pur_science.canonical import CID

from .challenge_tools import REQUIRED_CHALLENGE_TOOLS, challenge_complete
from .crosspath import reported_matches_trace, verify_backward_threshold
from .evidence import EvidencePlanner, unnecessary_tool_calls
from .ontology import canonical_from_active_constraint, is_canonical_spelling, normalize_quantity, same_constraint

CERTIFICATE_VERSION = "PUR_CERTIFICATE_V2"


def ontology_check(decision: dict[str, Any] | None) -> dict[str, Any]:
    """Are the decision's constraint references spelled in the canonical vocabulary?

    A recognised alias (`mdi_fraction_min`) is scientifically right and schema-wrong; an
    unrecognised name is both.
    """
    violations: list[str] = []
    recognised = True
    if not isinstance(decision, dict):
        return {"pass": False, "violations": ["decision is not an object"], "recognised": False}
    ac = decision.get("active_constraint") or {}
    name = ac.get("quantity") or ac.get("name")
    if name is not None:
        quantity, _ = normalize_quantity(name)
        if quantity is None:
            recognised = False
            violations.append(f"active_constraint names an unregistered quantity {name!r}")
        elif not is_canonical_spelling(name):
            violations.append(f"active_constraint uses the non-canonical spelling {name!r}; canonical is {quantity!r}")
    if ac and "operator" not in ac:
        violations.append("active_constraint omits the canonical 'operator' field")
    bw = decision.get("backward_design") or {}
    bw_name = bw.get("quantity") or bw.get("active_constraint")
    if bw_name:
        quantity, _ = normalize_quantity(bw_name)
        if quantity is None:
            recognised = False
            violations.append(f"backward_design names an unregistered quantity {bw_name!r}")
        elif not is_canonical_spelling(bw_name):
            violations.append(f"backward_design uses the non-canonical spelling {bw_name!r}; canonical is {quantity!r}")
    if name is not None and bw_name and not same_constraint(name, bw_name):
        violations.append("active_constraint and backward_design refer to different quantities")
    return {"pass": not violations, "violations": violations, "recognised": recognised}


def procedural_gate(
    *,
    called_tools: Iterable[str],
    available_tools: Iterable[str] | None,
    trace: list[dict[str, Any]],
    config: dict[str, Any],
    require_evidence_plan: bool = True,
    require_challenge: bool = True,
    require_cross_path: bool = True,
    property_winner_hint: str | None = None,
    cross_path_tolerance: float | None = None,
) -> dict[str, Any]:
    """Process-only finalisation check. Never inspects whether an answer is correct."""
    called = list(called_tools)
    available = None if available_tools is None else set(available_tools)
    planner = EvidencePlanner()
    coverage = planner.coverage(called, available)

    reasons: list[str] = []
    if require_evidence_plan and not coverage.complete:
        missing = ", ".join(coverage.missing_tools())
        reasons.append(f"claims without sufficient evidence: {', '.join(coverage.missing_claims)}; call: {missing}")

    challenge_available = REQUIRED_CHALLENGE_TOOLS & (available or REQUIRED_CHALLENGE_TOOLS)
    challenge_done = challenge_complete(called, available)
    if require_challenge and not challenge_done:
        outstanding = sorted(challenge_available - set(called))
        reasons.append(f"scientific challenge incomplete; call: {', '.join(outstanding)}")

    cross = verify_backward_threshold(
        trace, config, property_winner=property_winner_hint,
        tolerance=cross_path_tolerance,
        required=require_cross_path and _both_paths_available(available),
    )
    if require_cross_path and _both_paths_available(available) and cross["status"] == "no_path":
        reasons.append("no backward-threshold derivation recorded; both admissible paths are available in this condition")

    return {
        "can_finalize": not reasons,
        "reasons": reasons,
        "evidence_coverage": coverage.to_dict(),
        # None, not True, when the condition has no challenge tools: the stage was not
        # required and did not happen, and the summary must not read as if it had.
        "challenge_completed": challenge_done if challenge_available else None,
        "challenge_applicable": bool(challenge_available),
        "challenge_tools_available": sorted(challenge_available),
        "cross_path": cross,
    }


def _both_paths_available(available: set[str] | None) -> bool:
    if available is None:
        return True
    from .crosspath import PATH_A_TOOLS, PATH_B_TOOLS
    return set(PATH_A_TOOLS).issubset(available) and set(PATH_B_TOOLS).issubset(available)


def corrective_message(gate: dict[str, Any]) -> str:
    """Feedback given to the model when the gate refuses finalisation.

    Deliberately procedural: it names missing evidence and unfinished stages only. It never
    states or implies which candidate is correct.
    """
    if gate.get("can_finalize"):
        return ("Evidence coverage, scientific challenge and cross-path verification are complete. "
                "Issue the final JSON only.")
    return (
        "You attempted to finalise before the V2 evidence contract was satisfied. "
        + " ".join(gate.get("reasons", []))
        + " Do not guess and do not restate an answer; obtain the missing deterministic evidence first."
    )


def build_certificate(
    *,
    decision: dict[str, Any] | None,
    trace: list[dict[str, Any]],
    called_tools: Iterable[str],
    available_tools: Iterable[str] | None,
    config: dict[str, Any],
    toolbox: Any | None = None,
    schema_valid: bool = True,
    require_evidence_plan: bool = True,
    require_challenge: bool = True,
    require_cross_path: bool = True,
    cross_path_tolerance: float | None = None,
) -> dict[str, Any]:
    """Full post-hoc certificate. Computed from the trace and the blind table; never from gold."""
    called = list(called_tools)
    decision = decision if isinstance(decision, dict) else None
    l0 = (decision or {}).get("property_winner")
    l1 = (decision or {}).get("constrained_winner")
    l2 = (decision or {}).get("robust_winner")

    gate = procedural_gate(
        called_tools=called, available_tools=available_tools, trace=trace, config=config,
        require_evidence_plan=require_evidence_plan, require_challenge=require_challenge,
        require_cross_path=require_cross_path, property_winner_hint=l0,
        cross_path_tolerance=cross_path_tolerance,
    )
    coverage = EvidencePlanner().coverage(called, available_tools)
    cross = gate["cross_path"]
    onto = ontology_check(decision)

    constraint_audit_pass: bool | None = None
    robustness_audit_pass: bool | None = None
    active_constraint_margin: float | None = None
    objective_margin: float | None = None
    if toolbox is not None and decision is not None:
        constraint_audit_pass, active_constraint_margin = _self_consistency_nominal(toolbox, decision, l0, l1, config)
        robustness_audit_pass = _self_consistency_robust(toolbox, l2)
        objective_margin = _objective_margin(toolbox, l2 or l1)

    contradictions = _trace_contradictions(trace)
    reported_conflicts = (decision or {}).get("conflicts") or []
    status = str((decision or {}).get("decision_status") or ("abstain" if (decision or {}).get("abstain") else "final"))
    conflict_surfaced = bool(reported_conflicts) or status in ("conflict", "abstain")
    cross_conflict = bool(cross.get("conflict"))
    unsurfaced_conflict = cross_conflict and not conflict_surfaced

    usage = unnecessary_tool_calls(trace or called, coverage)
    # Headline "wasted work" figure: calls that serve neither an admissible evidence path of a
    # satisfied claim nor the required challenge stage. This is the number that is comparable
    # between tool_llm and V2, because it does not punish V2 for the cross-check its contract
    # obliges it to perform.
    purposeful = set(coverage.purposeful_tools()) | set(REQUIRED_CHALLENGE_TOOLS)
    usage["challenge_calls"] = sum(1 for t in called if t in REQUIRED_CHALLENGE_TOOLS)
    usage["off_plan_calls"] = sum(1 for t in called if t not in purposeful)
    usage["unnecessary_calls_excluding_challenge"] = usage["off_plan_calls"] + usage["redundant_repeat_calls"]

    cert_pass = bool(
        gate["can_finalize"]
        and schema_valid
        and onto["pass"]
        and (cross.get("cross_path_verified") or conflict_surfaced or not require_cross_path)
        and not unsurfaced_conflict
        and (constraint_audit_pass is not False)
        and (robustness_audit_pass is not False)
        and contradictions == 0
    )
    return {
        "version": CERTIFICATE_VERSION,
        "evidence_coverage": {
            "satisfied": coverage.satisfied,
            "required": coverage.required,
            "complete": coverage.complete,
            "missing_claims": list(coverage.missing_claims),
            "unsatisfiable_claims": list(coverage.unsatisfiable),
            "claims": [c.to_dict() for c in coverage.claims],
        },
        "cross_path_agreement": bool(cross.get("cross_path_verified")),
        "cross_path": cross,
        "cross_path_reported_matches_trace": reported_matches_trace(decision, cross, tolerance=cross_path_tolerance),
        "challenge_completed": gate["challenge_completed"],
        "challenge_applicable": gate["challenge_applicable"],
        "challenge_tools_used": sorted(set(called) & REQUIRED_CHALLENGE_TOOLS),
        "constraint_audit_pass": constraint_audit_pass,
        "robustness_audit_pass": robustness_audit_pass,
        "schema_consistency_pass": bool(schema_valid),
        "ontology_consistency_pass": bool(onto["pass"]),
        "ontology_violations": onto["violations"],
        "ontology_recognised": onto["recognised"],
        "tool_contradictions": contradictions,
        "conflict_surfaced": conflict_surfaced,
        "unsurfaced_cross_path_conflict": unsurfaced_conflict,
        "decision_status": status,
        "active_constraint_margin": active_constraint_margin,
        "objective_margin": objective_margin,
        "tool_usage": usage,
        "procedural_gate_pass": bool(gate["can_finalize"]),
        "procedural_gate_reasons": gate["reasons"],
        "certificate_pass": cert_pass,
        "note": "Computed from the recorded trace and the blind candidate table. Contains no evaluator gold and is never returned to the model under test.",
    }


def _self_consistency_nominal(toolbox: Any, decision: dict[str, Any], l0: Any, l1: Any, config: dict[str, Any]) -> tuple[bool | None, float | None]:
    """Is the claimed constrained winner feasible, and is the claimed active constraint a real failure of L0?"""
    frame = getattr(toolbox, "frontier", None)
    if frame is None:
        return None, None
    ids = set(frame[CID].astype(str))
    ok = True
    margin = None
    if l1 is not None:
        if str(l1) not in ids:
            return False, None
        ok &= bool(frame.loc[frame[CID].astype(str) == str(l1), "feasible_nominal"].iloc[0])
    if l0 is not None and str(l0) in ids:
        ac = decision.get("active_constraint") or {}
        canonical = canonical_from_active_constraint(ac, config)
        quantity = (canonical or {}).get("quantity")
        col = f"check_{quantity}" if quantity else None
        if col and col in frame.columns:
            ok &= not bool(frame.loc[frame[CID].astype(str) == str(l0), col].iloc[0])
        elif quantity not in (None, "none"):
            ok = False
        thr, val = ac.get("threshold"), ac.get("candidate_value")
        try:
            margin = float(val) - float(thr)
        except (TypeError, ValueError):
            margin = None
    return bool(ok), margin


def _self_consistency_robust(toolbox: Any, l2: Any) -> bool | None:
    frame = getattr(toolbox, "frontier", None)
    if frame is None or l2 is None or "feasible_robust" not in frame.columns:
        return None
    hit = frame[frame[CID].astype(str) == str(l2)]
    if hit.empty:
        return False
    return bool(hit.iloc[0]["feasible_robust"])


def _objective_margin(toolbox: Any, cid: Any) -> float | None:
    frame = getattr(toolbox, "frontier", None)
    if frame is None or cid is None:
        return None
    robust = "robust_score" in frame.columns
    score_col = "robust_score" if robust else "property_score"
    feas_col = "feasible_robust" if robust else "feasible_nominal"
    hit = frame[frame[CID].astype(str) == str(cid)]
    if hit.empty:
        return None
    others = frame[frame[feas_col] & (frame[CID].astype(str) != str(cid))]
    if others.empty:
        return None
    return float(hit.iloc[0][score_col]) - float(others[score_col].min())


def _trace_contradictions(trace: list[dict[str, Any]]) -> int:
    """Contradictions reported by the deterministic consistency challenge, if it was run."""
    total = 0
    for entry in trace:
        if entry.get("tool") != "challenge_consistency":
            continue
        out = entry.get("output") or {}
        if out.get("ok") and isinstance(out.get("result"), dict):
            total = int(out["result"].get("n_contradictions", 0) or 0)
    return total
