#!/usr/bin/env python3
"""Repeated PUR-RECOVER V1 runs for one condition.

  python scripts/run_agent_benchmark.py --runs 20                       # pur_agent with env model
  python scripts/run_agent_benchmark.py --runs 3 --provider mock        # offline dry run
Writes results/recover_v1/<condition>/<model>/runs/run_XXXX.json plus summary.json / summary.csv.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import _bootstrap  # noqa: F401
from pur_agent.env import load_dotenv
load_dotenv()

from pur_agent.benchmark import run_benchmark
from pur_agent.conditions import CONDITIONS

ROOT = _bootstrap.ROOT


def safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name or "none")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--condition", default="pur_agent", choices=sorted(CONDITIONS))
    ap.add_argument("--provider", default=os.getenv("OPENAI_PROVIDER", "auto"))
    ap.add_argument("--model", default=os.getenv("OPENAI_MODEL"))
    ap.add_argument("--blind-dir", default=str(ROOT / "benchmark" / "recover_v1" / "blind"))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--gold", default=None)
    ap.add_argument("--mapping", default=None)
    ap.add_argument("--seed-base", type=int, default=None)
    ap.add_argument("--max-rounds", type=int, default=40)
    args = ap.parse_args()
    cond = CONDITIONS[args.condition]
    model = args.model or ("mock" if args.provider == "mock" else "")
    if cond.uses_llm and not model:
        print("Set OPENAI_MODEL or pass --model (or use --provider mock)", file=sys.stderr)
        return 2
    out_dir = args.out_dir or str(ROOT / "results" / "recover_v1" / cond.name / safe(model if cond.uses_llm else "deterministic"))
    summary = run_benchmark(blind_dir=args.blind_dir, condition=args.condition, provider=args.provider, model=model, runs=args.runs,
                            out_dir=out_dir, gold=args.gold, mapping=args.mapping, seed_base=args.seed_base, max_rounds=args.max_rounds)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
