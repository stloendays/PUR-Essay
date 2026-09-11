#!/usr/bin/env python3
"""Freeze a preregistration-style run manifest before a PUR-RECOVER pilot or formal matrix.

Captures everything needed to reproduce or audit a run set: git commit and worktree state,
prompt/config/data hashes, the recovered PUR_SIM_V1 snapshot hash, the anonymisation seed,
the model/provider identity, the seed schedule, the tool policy per condition, and the
retry/failure policy. No credential is read or recorded.

  python scripts/freeze_run_manifest.py --label pilot_v2_20260911 --runs 3 \
      --conditions direct_llm tool_llm pur_agent pur_agent_v2 --seed-base 1000

Writes results/<benchmark>/<label>/run_manifest.json and refuses to overwrite an existing one,
so a frozen manifest cannot be silently rewritten after seeing results.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from pur_agent.conditions import CONDITIONS
from pur_agent.data_access import sha256_file
from pur_agent.logging_utils import sha256_json, sha256_text, utc_now
from pur_agent.prompts import PROMPT_DIR

ROOT = _bootstrap.ROOT


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _hash_if_present(path: Path) -> str | None:
    return sha256_file(path) if path.is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True, help="run-set label, e.g. pilot_v2_20260911")
    ap.add_argument("--benchmark", default="recover_v2", choices=["recover_v1", "recover_v2"])
    ap.add_argument("--conditions", nargs="+", required=True, choices=sorted(CONDITIONS))
    ap.add_argument("--runs", type=int, required=True)
    ap.add_argument("--seed-base", type=int, required=True)
    ap.add_argument("--model", default=None, help="model identifier (defaults to $OPENAI_MODEL)")
    ap.add_argument("--provider", default=None, help="provider (defaults to $OPENAI_PROVIDER or auto)")
    ap.add_argument("--max-rounds", type=int, default=40)
    ap.add_argument("--results-root", default=None)
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    import os
    from pur_agent.env import load_dotenv
    load_dotenv()
    model = args.model or os.getenv("OPENAI_MODEL") or ""
    provider = args.provider or os.getenv("OPENAI_PROVIDER") or "auto"
    if not model:
        print("Set OPENAI_MODEL or pass --model; the manifest must record the exact model.", file=sys.stderr)
        return 2

    blind = ROOT / "benchmark" / args.benchmark / "blind"
    config_path = ROOT / "configs" / f"{args.benchmark}.json"
    if not blind.is_dir():
        print(f"Blind bundle not found: {blind}. Build it first.", file=sys.stderr)
        return 2

    prompts: dict[str, str | None] = {}
    for name in sorted({p for c in args.conditions for p in (CONDITIONS[c].system_prompt, CONDITIONS[c].task_prompt)}):
        prompts[name] = _hash_if_present(Path(PROMPT_DIR) / name)

    conditions = {}
    for name in args.conditions:
        cond = CONDITIONS[name]
        conditions[name] = {
            "schema_version": cond.schema_version,
            "mode": cond.mode,
            "uses_llm": cond.uses_llm,
            "use_tools": cond.use_tools,
            "tool_policy": sorted(cond.tools) if cond.tools else "all tools of the mode",
            "enforce_strategy": cond.enforce_strategy,
            "require_evidence_plan": cond.require_evidence_plan,
            "require_challenge": cond.require_challenge,
            "require_cross_path": cond.require_cross_path,
            "enforce_certificate": cond.enforce_certificate,
            "system_prompt": cond.system_prompt,
            "task_prompt": cond.task_prompt,
            "include_provenance": cond.include_provenance,
            "inline_data": cond.inline_data,
        }

    manifest = {
        "manifest_status": "FROZEN",
        "label": args.label,
        "benchmark": args.benchmark,
        "frozen_utc": utc_now(),
        "note": args.note,
        "git": {
            "commit": _git("rev-parse", "HEAD"),
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "worktree_clean": _git("status", "--porcelain") == "",
            "dirty_files": [ln for ln in (_git("status", "--porcelain") or "").splitlines() if ln],
        },
        "model": {"model": model, "provider": provider, "max_rounds": args.max_rounds},
        "seed_schedule": {
            "seed_base": args.seed_base,
            "runs_per_condition": args.runs,
            "seeds": [args.seed_base + i for i in range(1, args.runs + 1)],
            "policy": "identical run count and seed schedule across every comparable condition",
        },
        "hashes": {
            "config_file_sha256": _hash_if_present(config_path),
            "blind_candidates_sha256": _hash_if_present(blind / "candidates.csv"),
            "blind_config_sha256": _hash_if_present(blind / "benchmark_config.json"),
            "blind_task_sha256": _hash_if_present(blind / "task.json"),
            "pur_sim_v1_snapshot_sha256": _hash_if_present(ROOT / "data" / "pur_sim_v1" / "candidates_full.csv"),
            "frontier_config_sha256": _hash_if_present(ROOT / "configs" / "frontier_v1.json"),
            "gold_sha256": _hash_if_present(ROOT / "benchmark" / args.benchmark / "evaluator_only" / "gold_decision.json"),
            "prompts": prompts,
        },
        "anonymization_seed": json.loads((blind / "manifest.json").read_text(encoding="utf-8")).get("seed"),
        "conditions": conditions,
        "retry_failure_policy": {
            "transport_failures": "recorded in the run JSON with the error string; never retried silently, never deleted",
            "invalid_json_or_schema": "recorded as decision_valid=false and scored as invalid_output",
            "finalization_guard_retries": "at most 3 procedural corrective rounds per run (V1 strategy guard and V2 gate alike)",
            "failed_runs": "immutable evidence; negative and transport/schema failures are kept",
        },
        "evaluator": {
            "primary_metric": "complete_decision_recovery",
            "gold_is_evaluator_only": True,
            "tolerances_frozen_before_runs": True,
        },
    }
    manifest["manifest_sha256"] = sha256_json({k: v for k, v in manifest.items() if k != "frozen_utc"})

    out_dir = Path(args.results_root or (ROOT / "results" / args.benchmark)) / args.label
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "run_manifest.json"
    if target.exists():
        print(f"Refusing to overwrite an existing frozen manifest: {target}", file=sys.stderr)
        return 3
    target.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"written": str(target), "commit": manifest["git"]["commit"],
                      "worktree_clean": manifest["git"]["worktree_clean"],
                      "manifest_sha256": manifest["manifest_sha256"]}, indent=2))
    if not manifest["git"]["worktree_clean"]:
        print("WARNING: the worktree is dirty; commit before a formal matrix so the manifest pins real code.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
