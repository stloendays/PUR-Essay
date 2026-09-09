#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--model", default=os.getenv("OPENAI_MODEL"))
    ap.add_argument("--blind-dir", default="benchmark/recover_v1/blind")
    ap.add_argument("--out-dir", default="results/recover_v1")
    ap.add_argument("--gold", default=None)
    ap.add_argument("--mapping", default="benchmark/recover_v1/evaluator_only/anonymous_mapping.json")
    args = ap.parse_args()
    if not args.model:
        raise SystemExit("Set OPENAI_MODEL or pass --model")
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    metrics = []
    for i in range(1, args.runs + 1):
        run = out / f"run_{i:03d}.json"
        subprocess.run([sys.executable, "scripts/run_agent_once.py", "--blind-dir", args.blind_dir, "--model", args.model, "--out", str(run)], check=True)
        if args.gold:
            subprocess.run([sys.executable, "scripts/evaluate_agent_run.py", str(run), "--gold", args.gold, "--mapping", args.mapping], check=True)
            metrics.append(json.loads(run.read_text()).get("evaluation", {}))
    summary = {"model": args.model, "n_runs": args.runs}
    if metrics:
        keys = sorted({k for m in metrics for k, v in m.items() if isinstance(v, bool)})
        summary.update({f"{k}_rate": sum(bool(m.get(k)) for m in metrics) / len(metrics) for k in keys})
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
