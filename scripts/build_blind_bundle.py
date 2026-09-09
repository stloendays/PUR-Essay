#!/usr/bin/env python3
"""Build the PUR-RECOVER V1 blind bundle (Agent-readable) and the evaluator-only gold files.

  benchmark/recover_v1/blind/            candidates.csv, benchmark_config.json, task.json, manifest.json, provenance.json
  benchmark/recover_v1/evaluator_only/   gold_mapping.json, gold_decision.json, gold_decision_blind.json
  gold/recover_v1/                       copies of the evaluator-only files

Runs the leakage scan afterwards and exits non-zero if it fails.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
import pandas as pd

from pur_agent.blind_bundle import build_blind_bundle, verify_no_leakage
from pur_agent.config import load_benchmark_config

ROOT = _bootstrap.ROOT


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidates", default=str(ROOT / "data" / "pur_sim_v1" / "candidates_full.csv"))
    ap.add_argument("--config", default=str(ROOT / "configs" / "recover_v1.json"))
    ap.add_argument("--blind-dir", default=str(ROOT / "benchmark" / "recover_v1" / "blind"))
    ap.add_argument("--evaluator-dir", default=str(ROOT / "benchmark" / "recover_v1" / "evaluator_only"))
    ap.add_argument("--gold-dir", default=str(ROOT / "gold" / "recover_v1"))
    ap.add_argument("--seed", type=int, default=None, help="anonymization seed (default: config anonymization.seed)")
    ap.add_argument("--no-anonymize", action="store_true", help="secondary named-chemistry benchmark: keep source IDs and material names")
    args = ap.parse_args()

    cand = Path(args.candidates)
    if not cand.is_file():
        print(f"ERROR: candidate table not found: {cand} (see data/pur_sim_v1/README.md)", file=sys.stderr)
        return 2
    cfg = load_benchmark_config(args.config, repo_root=ROOT)
    seed = args.seed if args.seed is not None else int(cfg.get("anonymization", {}).get("seed", 20260909))
    if args.no_anonymize:
        cfg["benchmark_id"] = cfg.get("benchmark_id", "PUR_RECOVER_V1") + "_NAMED"
        cfg["anonymization"] = {"component_columns": [], "material_prefix": "", "seed": seed}
    df = pd.read_csv(cand)
    originals = [str(x) for x in df[cfg["columns"]["candidate_id"]].unique()]
    materials = list(cfg.get("anonymization", {}).get("component_columns", []))

    manifest = build_blind_bundle(cand, cfg, args.blind_dir, args.evaluator_dir, seed=seed)
    gold_dir = Path(args.gold_dir); gold_dir.mkdir(parents=True, exist_ok=True)
    for name in ("gold_mapping.json", "gold_decision.json", "gold_decision_blind.json"):
        src = Path(args.evaluator_dir) / name
        if src.is_file():
            shutil.copyfile(src, gold_dir / name)

    if args.no_anonymize:
        print(json.dumps({"manifest": manifest, "leakage_check": "SKIPPED (named benchmark keeps identities by design)"}, indent=2))
        return 0
    gold_texts = [p.read_text(encoding="utf-8") for p in Path(args.evaluator_dir).glob("*.json")]
    violations = verify_no_leakage(args.blind_dir, originals, materials, gold_texts=gold_texts)
    if violations:
        print("Leakage check FAILED:\n" + "\n".join(violations[:30]), file=sys.stderr)
        return 1
    print(json.dumps({"manifest": manifest, "leakage_check": "PASS"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
