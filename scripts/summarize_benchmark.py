#!/usr/bin/env python3
"""Aggregate every run record under results/recover_v1 into summary.csv / summary.json by condition x model."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from pur_agent.benchmark import summarize_tree, write_summary_csv

ROOT = _bootstrap.ROOT
KEY = ("condition", "provider", "model", "n_runs", "n_valid_output", "complete_decision_recovery_rate", "top1_recovery_rate", "top3_recovery_rate",
       "top5_recovery_rate", "oracle_rank_median", "objective_regret_mean", "hard_constraint_violation_rate_mean", "backward_threshold_error_mean",
       "reachability_recovery_rate", "explanation_fidelity_mean", "tool_call_count_mean", "input_tokens_mean", "output_tokens_mean", "api_calls_mean", "latency_s_mean")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=str(ROOT / "results" / "recover_v1"))
    args = ap.parse_args()
    rows = summarize_tree(args.root)
    if not rows:
        print("no run records found", file=sys.stderr)
        return 2
    write_summary_csv(Path(args.root) / "summary.csv", rows)
    (Path(args.root) / "summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps([{k: r.get(k) for k in KEY} for r in rows], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
