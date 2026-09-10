#!/usr/bin/env python3
"""Run one PUR-RECOVER V1 Agent (or baseline) run and write a complete run record.

Examples
  python scripts/run_agent_once.py --provider mock --condition pur_agent
  python scripts/run_agent_once.py --condition pur_agent            # uses OPENAI_MODEL / OPENAI_API_KEY / OPENAI_BASE_URL
  python scripts/run_agent_once.py --condition direct_llm --provider chat
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from pur_agent.env import load_dotenv
load_dotenv()

from pur_agent.agent import run_once
from pur_agent.benchmark import find_gold
from pur_agent.conditions import CONDITIONS, get_condition
from pur_agent.data_access import BlindBundle
from pur_agent.evaluator import evaluate_run_record, load_gold
from pur_agent.llm_client import make_client
from pur_agent.logging_utils import new_run_id, write_run_record

ROOT = _bootstrap.ROOT


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blind-dir", default=str(ROOT / "benchmark" / "recover_v1" / "blind"))
    ap.add_argument("--condition", default="pur_agent", choices=sorted(CONDITIONS))
    ap.add_argument("--provider", default=os.getenv("OPENAI_PROVIDER", "auto"), help="mock | auto | responses | chat")
    ap.add_argument("--model", default=os.getenv("OPENAI_MODEL"))
    ap.add_argument("--seed", type=int, default=None, help="LLM seed if the provider supports it (recorded either way)")
    ap.add_argument("--max-rounds", type=int, default=40)
    ap.add_argument("--gold", default=None, help="evaluator-only gold decision (default: auto-detect next to the blind dir)")
    ap.add_argument("--mapping", default=None)
    ap.add_argument("--no-eval", action="store_true")
    ap.add_argument("--out", default=None, help="run record path (default results/recover_v1/<condition>/runs/<run_id>.json)")
    args = ap.parse_args()

    bundle = BlindBundle.load(args.blind_dir)
    cond = get_condition(args.condition)
    client = make_client(args.provider, args.model or "", max_rounds=args.max_rounds) if cond.uses_llm else None
    run_id = new_run_id()
    rec = run_once(bundle, cond, client, run_id=run_id, seed=args.seed)
    if not args.no_eval:
        gold_path, mapping_path = find_gold(args.blind_dir, args.gold, args.mapping)
        if gold_path:
            gold = load_gold(gold_path, mode=cond.mode)
            mapping = json.loads(Path(mapping_path).read_text(encoding="utf-8")) if mapping_path else None
            evaluate_run_record(rec, gold, mapping)
        else:
            rec["evaluation"] = None
            rec["evaluation_note"] = "no evaluator gold found; run recorded unevaluated"
    out = Path(args.out) if args.out else ROOT / "results" / "recover_v1" / cond.name / "runs" / f"{run_id}.json"
    write_run_record(out, rec)
    shown = {k: rec.get(k) for k in ("run_id", "condition", "provider", "model", "decision_valid", "tool_call_count", "usage", "latency_s", "error")}
    shown["final_json"] = rec.get("final_json")
    shown["evaluation"] = rec.get("evaluation")
    shown["record"] = str(out)
    print(json.dumps(shown, indent=2, default=str))
    return 0 if rec.get("decision_valid") else 1


if __name__ == "__main__":
    sys.exit(main())
