#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pur_agent.evaluator import evaluate_decision


def remap_ids(decision: dict, reverse: dict[str, str]) -> dict:
    out = json.loads(json.dumps(decision))
    for key in ("property_winner", "constrained_winner", "robust_winner"):
        if out.get(key) in reverse:
            out[key] = reverse[out[key]]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_json")
    ap.add_argument("--gold", required=True, help="Evaluator-only frozen gold decision JSON")
    ap.add_argument("--mapping", default="benchmark/recover_v1/evaluator_only/anonymous_mapping.json")
    ap.add_argument("--tolerance", type=float, default=.03)
    args = ap.parse_args()
    run = json.loads(Path(args.run_json).read_text())
    gold = json.loads(Path(args.gold).read_text())
    mapping = json.loads(Path(args.mapping).read_text())
    decision = remap_ids(run["decision"], mapping["candidate_reverse"])
    metrics = evaluate_decision(decision, gold, backward_tolerance=args.tolerance)
    run["evaluation"] = metrics
    Path(args.run_json).write_text(json.dumps(run, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
