from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .metrics import score_decision


def _same(a: Any, b: Any) -> bool:
    return a is not None and b is not None and str(a) == str(b)


def _within(a: Any, b: Any, tol: float) -> bool:
    try:
        return math.isfinite(float(a)) and math.isfinite(float(b)) and abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def evaluate_decision(agent: dict[str, Any], gold: dict[str, Any], *, backward_tolerance: float = 0.03) -> dict[str, Any]:
    """Minimal component-wise recovery check (kept for the original RECOVER V1 tests).

    `score_decision` in metrics.py is the full benchmark scorer.
    """
    property_ok = _same(agent.get("property_winner"), gold.get("property_winner"))
    constrained_ok = _same(agent.get("constrained_winner"), gold.get("constrained_winner"))
    robust_ok = _same(agent.get("robust_winner"), gold.get("robust_winner"))
    ac_a = agent.get("active_constraint") or {}; ac_g = gold.get("active_constraint") or {}
    constraint_ok = _same(ac_a.get("name"), ac_g.get("name"))
    bw_a = agent.get("backward_design") or {}; bw_g = gold.get("backward_design") or {}
    threshold_ok = _within(bw_a.get("continuous_threshold"), bw_g.get("continuous_threshold"), backward_tolerance)
    grid_ok = _within(bw_a.get("nearest_reachable_grid_value"), bw_g.get("nearest_reachable_grid_value"), 1e-9)
    reachable_ok = bw_a.get("reachable") is bw_g.get("reachable")
    lt_a = agent.get("local_trends") or {}; lt_g = gold.get("local_trends") or {}
    nco_ok = _same(lt_a.get("nco_direction"), lt_g.get("nco_direction"))
    composition_ok = _same(lt_a.get("composition_direction"), lt_g.get("composition_direction"))
    complete = all([property_ok, constrained_ok, robust_ok, constraint_ok, threshold_ok, grid_ok, reachable_ok, nco_ok, composition_ok])
    return {
        "property_winner_recovery": property_ok,
        "constrained_winner_recovery": constrained_ok,
        "robust_winner_recovery": robust_ok,
        "active_constraint_recovery": constraint_ok,
        "backward_threshold_recovery": threshold_ok,
        "reachable_grid_recovery": grid_ok,
        "reachability_recovery": reachable_ok,
        "nco_direction_recovery": nco_ok,
        "composition_direction_recovery": composition_ok,
        "complete_decision_recovery": complete,
    }


def remap_decision(decision: dict[str, Any], mapping: dict[str, Any]) -> dict[str, Any]:
    """Evaluator-side: translate anonymous candidate IDs and material names back to source names."""
    out = json.loads(json.dumps(decision))
    cand = mapping.get("candidate_reverse", {})
    mat = mapping.get("material_reverse", {})
    for key in ("property_winner", "constrained_winner", "robust_winner"):
        if out.get(key) in cand:
            out[key] = cand[out[key]]
    lt = out.get("local_trends") or {}
    axis = lt.get("composition_axis")
    if isinstance(axis, str):
        for anon, src in sorted(mat.items(), key=lambda kv: -len(kv[0])):
            if axis == anon or axis.startswith(anon):
                lt["composition_axis"] = axis.replace(anon, src, 1)
                break
        out["local_trends"] = lt
    return out


def evaluate_run_record(record: dict[str, Any], gold: dict[str, Any], mapping: dict[str, Any] | None, *, backward_tolerance: float = 0.03, top_k: tuple[int, ...] = (1, 3, 5)) -> dict[str, Any]:
    """Score one run record in place and return the metrics. Audit-mode records need the audit gold."""
    final = record.get("final_json")
    if record.get("mode") == "audit":
        from .audit import remap_audit_report, score_audit
        if gold.get("mode") != "PUR_AUDIT_V1":
            raise ValueError("audit-mode run must be scored against gold_audit.json")
        if not record.get("decision_valid") or not isinstance(final, dict):
            metrics = score_audit({"abstain": True}, gold); metrics["invalid_output"] = True
        else:
            report = remap_audit_report(final, mapping) if mapping else final
            metrics = score_audit(report, gold); metrics["invalid_output"] = False
            record["final_json_named"] = report
        metrics["tool_call_count"] = record.get("tool_call_count", 0)
        usage = record.get("usage") or {}
        metrics["input_tokens"] = usage.get("input_tokens", usage.get("prompt_tokens"))
        metrics["output_tokens"] = usage.get("output_tokens", usage.get("completion_tokens"))
        metrics["api_calls"] = usage.get("calls")
        metrics["latency_s"] = record.get("latency_s")
        record["evaluation"] = metrics
        return metrics
    if not record.get("decision_valid") or not isinstance(final, dict):
        metrics = score_decision({"abstain": True}, gold, backward_tolerance=backward_tolerance, top_k=top_k)
        metrics["invalid_output"] = True
    else:
        decision = remap_decision(final, mapping) if mapping else final
        metrics = score_decision(decision, gold, backward_tolerance=backward_tolerance, top_k=top_k)
        metrics["invalid_output"] = False
        record["final_json_named"] = decision
    metrics["tool_call_count"] = record.get("tool_call_count", 0)
    usage = record.get("usage") or {}
    metrics["input_tokens"] = usage.get("input_tokens", usage.get("prompt_tokens"))
    metrics["output_tokens"] = usage.get("output_tokens", usage.get("completion_tokens"))
    metrics["api_calls"] = usage.get("calls")
    metrics["latency_s"] = record.get("latency_s")
    record["evaluation"] = metrics
    return metrics


def load_gold(gold_path: str | Path, *, mode: str = "recover") -> dict[str, Any]:
    """Load the evaluator gold for a mode. For audit mode, `gold_audit.json` next to the given file is used."""
    gold_path = Path(gold_path)
    if mode == "audit" and gold_path.name != "gold_audit.json":
        gold_path = gold_path.with_name("gold_audit.json")
    gold = json.loads(Path(gold_path).read_text(encoding="utf-8"))
    if gold.get("gold_status") not in (None, "GOLD"):
        raise RuntimeError(f"Refusing to evaluate against a non-gold decision file (gold_status={gold.get('gold_status')!r})")
    return gold
