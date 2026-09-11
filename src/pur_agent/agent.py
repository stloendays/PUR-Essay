from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from pur_science import canonicalize, frontier_decision

from .certificate import build_certificate
from .conditions import Condition, get_condition
from .data_access import BlindBundle
from .evidence import EvidencePlanner
from .llm_client import LLMClient, LLMResult
from .logging_utils import build_run_record, new_run_id, sha256_json, sha256_text
from .prompts import build_task_text, load_prompt
from .audit_tools import AuditToolbox
from .runtime import ToolboxExecutor
from .schemas import DecisionSchemaError, parse_audit_report, parse_decision, parse_decision_v2
from .strategy import AuditStrategy, V2Policy
from .tools import DecisionToolbox
from .tools_v2 import V2Toolbox


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        a, b = text.find("{"), text.rfind("}")
        if a < 0 or b <= a:
            raise
        return json.loads(text[a:b + 1])


def oracle_decision_on_bundle(bundle: BlindBundle) -> dict[str, Any]:
    """Baseline 0: run the deterministic frontier on the blind table itself (anonymous IDs)."""
    table = canonicalize(bundle.candidates, bundle.config)
    d = frontier_decision(table, bundle.config)
    lt = d["local_trends"]
    return {
        "property_winner": d["property_winner"],
        "constrained_winner": d["constrained_winner"],
        "robust_winner": d["robust_winner"],
        "robust_abstention_reason": None if d["robust_layer_frozen"] else "robust layer not frozen",
        "active_constraint": {k: d["active_constraint"].get(k) for k in ("name", "threshold", "candidate_value")},
        "backward_design": {
            "variable": d["backward_design"]["variable"],
            "continuous_threshold": d["backward_design"]["continuous_threshold"],
            "nearest_reachable_grid_value": d["backward_design"]["nearest_reachable_grid_value"],
            "reachable": d["backward_design"]["reachable"],
            "active_constraint": d["backward_design"]["constraint"],
        },
        "local_trends": {"nco_direction": lt["nco_direction"], "composition_axis": lt["composition_axis"], "composition_direction": lt["composition_direction"]},
        "evidence": ["deterministic frontier on the blind table"],
        "final_reasoning_summary": "Baseline 0: deterministic oracle, not an Agent.",
        "confidence": 1.0,
        "abstain": False,
        "abstention_reason": None,
    }


def run_once(
    bundle: BlindBundle,
    condition: Condition | str,
    client: LLMClient | None,
    *,
    run_id: str | None = None,
    seed: int | None = None,
    prompt_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Execute one benchmark run and return the complete run record (no evaluation yet)."""
    cond = get_condition(condition) if isinstance(condition, str) else condition
    run_id = run_id or new_run_id()
    cfg = bundle.config
    config_hash = sha256_json(cfg)
    t0 = time.perf_counter()

    if not cond.uses_llm:
        final = oracle_decision_on_bundle(bundle)
        rec = build_run_record(
            run_id=run_id, benchmark_id=cfg.get("benchmark_id", ""), condition=cond.name, provider="deterministic", model="frontier_v1",
            prompt_hash="", data_hashes=bundle.hashes, config_hash=config_hash, anonymization_seed=bundle.manifest.get("seed"),
            llm_seed=None, tool_trace=[], final_json=final, raw_final_text=json.dumps(final), usage=None, response_ids=[],
            latency_s=time.perf_counter() - t0, strategy_check=None, extra={"condition_description": cond.description},
        )
        rec["decision_valid"] = True
        return rec

    if client is None:
        raise ValueError(f"Condition {cond.name} requires an LLM client")
    instructions = load_prompt(cond.system_prompt, prompt_dir)
    task = build_task_text(bundle, cond, prompt_dir=prompt_dir)
    prompt_hash = sha256_text(instructions + "\n---\n" + task)
    executor: ToolboxExecutor | None = None
    robust_required = bool((cfg.get("robustness") or {}).get("enabled", False))
    is_v2 = cond.schema_version == "v2"
    v2_toolbox = cond.uses_v2_toolbox
    cross_tol = (cfg.get("evaluation") or {}).get("cross_path_tolerance_nco_oh")
    if cond.use_tools and cond.mode == "audit":
        executor = ToolboxExecutor(AuditToolbox(bundle.candidates, cfg), allowed_tools=cond.tools, enforce_strategy=cond.enforce_strategy,
                                   robust_required=robust_required, strategy=AuditStrategy(), include_audit_tools=True)
    elif cond.use_tools and v2_toolbox:
        # The V2 gate only exists for V2-schema conditions; a V2-toolbox baseline gets the
        # canonical vocabulary and nothing else, which is what makes it an isolating control.
        policy = V2Policy(
            config=cfg, enforce=bool(cond.enforce_certificate and cond.enforce_strategy),
            require_evidence_plan=cond.require_evidence_plan, require_challenge=cond.require_challenge,
            require_cross_path=cond.require_cross_path, cross_path_tolerance=cross_tol,
        ) if is_v2 else None
        executor = ToolboxExecutor(V2Toolbox(bundle.candidates, cfg), allowed_tools=cond.tools, enforce_strategy=cond.enforce_strategy,
                                   robust_required=robust_required, include_challenge_tools=cond.include_challenge_tools,
                                   v2_policy=policy)
    elif cond.use_tools:
        executor = ToolboxExecutor(DecisionToolbox(bundle.candidates, cfg), allowed_tools=cond.tools, enforce_strategy=cond.enforce_strategy,
                                   robust_required=robust_required)
    error = None
    result: LLMResult | None = None
    final: dict[str, Any] | None = None
    valid = False
    try:
        result = client.run(instructions=instructions, task=task, executor=executor, seed=seed)
        final = extract_json(result.text)
        if cond.mode == "audit":
            parse_audit_report(final)
        elif is_v2:
            parse_decision_v2(final)
        else:
            parse_decision(final)
        valid = True
    except (json.JSONDecodeError, DecisionSchemaError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # API/transport failure: record it, never crash a benchmark loop
        error = f"{type(exc).__name__}: {exc}"
    latency = time.perf_counter() - t0
    # The certificate is harness-side, so it is computed for any V2-toolbox condition, including
    # the V1-schema isolating baseline. `metrics_version` is what selects the V2 scorer.
    v2_blocks: dict[str, Any] = {}
    if v2_toolbox and executor is not None:
        planner = EvidencePlanner()
        v2_blocks = {
            "schema_version": cond.schema_version,
            "toolbox_version": "v2",
            "metrics_version": "v2",
            "evidence_plan": planner.plan(executor.available_tool_names),
            "decision_certificate": build_certificate(
                decision=final, trace=executor.trace, called_tools=executor.called_tools,
                available_tools=executor.available_tool_names, config=cfg, toolbox=executor.toolbox,
                schema_valid=valid, require_evidence_plan=cond.require_evidence_plan,
                require_challenge=cond.require_challenge, require_cross_path=cond.require_cross_path,
                cross_path_tolerance=cross_tol, require_operator=is_v2,
            ),
            "gate_attempts": executor.gate_attempts,
        }
    rec = build_run_record(
        run_id=run_id, benchmark_id=cfg.get("benchmark_id", ""), condition=cond.name,
        provider=(result.provider if result else getattr(client, "provider", "unknown")), model=getattr(client, "model", ""),
        prompt_hash=prompt_hash, data_hashes=bundle.hashes, config_hash=config_hash, anonymization_seed=bundle.manifest.get("seed"),
        llm_seed=seed, tool_trace=executor.trace if executor else [], final_json=final, raw_final_text=(result.text if result else ""),
        usage=(result.usage if result else None), response_ids=(result.response_ids if result else []), latency_s=latency,
        strategy_check=(executor.strategy_check().__dict__ if executor else None), error=error,
        extra={"condition_description": cond.description, "mode": cond.mode, "fallback_transport_used": bool(result.fallback_used) if result else None,
               "llm_rounds": result.rounds if result else 0, "tools_available": sorted(executor.available_tool_names) if executor else [],
               **v2_blocks},
    )
    rec["decision_valid"] = valid
    return rec
