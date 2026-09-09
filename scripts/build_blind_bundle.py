#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

import pandas as pd

from pur_agent.blind_bundle import build_blind_bundle, verify_no_leakage
from pur_agent.config import load_json


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--config", default="configs/recover_v1.json")
    ap.add_argument("--blind-dir", default="benchmark/recover_v1/blind")
    ap.add_argument("--evaluator-dir", default="benchmark/recover_v1/evaluator_only")
    ap.add_argument("--seed", type=int, default=20260909)
    args = ap.parse_args()
    cfg = load_json(args.config)
    df = pd.read_csv(args.candidates)
    originals = [str(x) for x in df[cfg["columns"]["candidate_id"]].unique()]
    materials = cfg.get("anonymization", {}).get("component_columns", [])
    manifest = build_blind_bundle(args.candidates, cfg, args.blind_dir, args.evaluator_dir, seed=args.seed)
    violations = verify_no_leakage(args.blind_dir, originals, materials)
    if violations:
        raise SystemExit("Leakage check failed:\n" + "\n".join(violations[:20]))
    print(json.dumps({"manifest": manifest, "leakage_check": "PASS"}, indent=2))


if __name__ == "__main__":
    main()
