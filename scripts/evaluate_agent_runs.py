#!/usr/bin/env python3
"""(Re-)evaluate every run record under a directory against the evaluator-only gold.

  python scripts/evaluate_agent_runs.py results/recover_v1
  python scripts/evaluate_agent_runs.py results/recover_v1/pur_agent --gold gold/recover_v1/gold_decision.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from pur_agent.benchmark import find_gold
from pur_agent.evaluator import evaluate_run_record, load_gold
from pur_agent.logging_utils import write_run_record

ROOT = _bootstrap.ROOT


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=str(ROOT / "results" / "recover_v1"))
    ap.add_argument("--blind-dir", default=str(ROOT / "benchmark" / "recover_v1" / "blind"))
    ap.add_argument("--gold", default=None)
    ap.add_argument("--mapping", default=None)
    ap.add_argument("--tolerance", type=float, default=0.03)
    args = ap.parse_args()
    gold_path, mapping_path = find_gold(args.blind_dir, args.gold, args.mapping)
    if not gold_path:
        print("No gold decision found; build the blind bundle first.", file=sys.stderr)
        return 2
    gold = load_gold(gold_path)
    mapping = json.loads(Path(mapping_path).read_text(encoding="utf-8")) if mapping_path else None
    n = 0
    for p in sorted(Path(args.root).rglob("run_*.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        evaluate_run_record(rec, gold, mapping, backward_tolerance=args.tolerance)
        write_run_record(p, rec)
        n += 1
    print(json.dumps({"evaluated": n, "gold": str(gold_path)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
