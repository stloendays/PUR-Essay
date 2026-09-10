#!/usr/bin/env python3
"""Run every baseline/ablation condition for the same model and number of runs.

  python scripts/run_baselines.py --runs 20
  python scripts/run_baselines.py --runs 2 --provider mock
  python scripts/run_baselines.py --conditions oracle direct_llm tool_llm pur_agent --runs 30
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from pur_agent.env import load_dotenv
load_dotenv()

from pur_agent.benchmark import run_benchmark, summarize_tree, write_summary_csv
from pur_agent.conditions import CONDITIONS

ROOT = _bootstrap.ROOT
DEFAULT_ORDER = ["oracle", "direct_llm", "tool_llm", "pur_agent", "pur_agent_no_backward", "pur_agent_no_constraint_checker", "pur_agent_no_provenance", "pur_agent_single_pass"]


def safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name or "none")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--conditions", nargs="+", default=DEFAULT_ORDER, choices=sorted(CONDITIONS))
    ap.add_argument("--provider", default=os.getenv("OPENAI_PROVIDER", "auto"))
    ap.add_argument("--model", default=os.getenv("OPENAI_MODEL"))
    ap.add_argument("--blind-dir", default=str(ROOT / "benchmark" / "recover_v1" / "blind"))
    ap.add_argument("--results-root", default=str(ROOT / "results" / "recover_v1"))
    ap.add_argument("--seed-base", type=int, default=None)
    ap.add_argument("--max-rounds", type=int, default=40)
    args = ap.parse_args()
    model = args.model or ("mock" if args.provider == "mock" else "")
    if not model and any(CONDITIONS[c].uses_llm for c in args.conditions):
        print("Set OPENAI_MODEL or pass --model (or use --provider mock)", file=sys.stderr)
        return 2
    summaries = []
    for name in args.conditions:
        cond = CONDITIONS[name]
        runs = 1 if not cond.uses_llm else args.runs
        out_dir = f"{args.results_root}/{cond.name}/{safe(model if cond.uses_llm else 'deterministic')}"
        summaries.append(run_benchmark(blind_dir=args.blind_dir, condition=name, provider=args.provider, model=model, runs=runs,
                                       out_dir=out_dir, seed_base=args.seed_base, max_rounds=args.max_rounds))
    tree = summarize_tree(args.results_root)
    write_summary_csv(f"{args.results_root}/summary.csv", tree)
    (Path(args.results_root) / "summary.json").write_text(json.dumps(tree, indent=2), encoding="utf-8")
    print(json.dumps([{k: s.get(k) for k in ("condition", "model", "n_runs", "complete_decision_recovery_rate", "top1_recovery_rate", "explanation_fidelity_mean", "tool_call_count_mean")} for s in summaries], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
