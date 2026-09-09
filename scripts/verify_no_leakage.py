#!/usr/bin/env python3
"""Gold-isolation check for PUR-RECOVER V1. Exit 0 = PASS, 1 = FAIL.

Scans every file the Agent runtime can read (blind bundle + prompts) for gold fields, source
candidate IDs, original material names and byte-identical copies of evaluator files, and
self-tests the runtime filesystem guard against evaluator-only paths.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from pur_agent.blind_bundle import verify_no_leakage
from pur_agent.config import load_benchmark_config
from pur_agent.data_access import AccessDenied, BundleReader

ROOT = _bootstrap.ROOT
GUARD_PROBES = (
    "../evaluator_only/gold_decision.json", "../evaluator_only/gold_mapping.json", "../../../gold/recover_v1/gold_decision.json",
    "../../../results/oracle_v2/oracle_best.json", "../../../data/oracle_top30_compact.csv",
    "../../../data/prospective_validation/access_policy.json", "gold_decision.json", "mapping.json",
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blind-dir", default=str(ROOT / "benchmark" / "recover_v1" / "blind"))
    ap.add_argument("--evaluator-dir", default=str(ROOT / "benchmark" / "recover_v1" / "evaluator_only"))
    ap.add_argument("--prompts-dir", default=str(ROOT / "prompts"))
    ap.add_argument("--config", default=str(ROOT / "configs" / "recover_v1.json"))
    args = ap.parse_args()

    blind = Path(args.blind_dir)
    if not blind.is_dir():
        print(f"FAIL: blind bundle not found at {blind}", file=sys.stderr)
        return 1
    cfg = load_benchmark_config(args.config, repo_root=ROOT)
    materials = list(cfg.get("anonymization", {}).get("component_columns", []))
    ev = Path(args.evaluator_dir)
    gold_texts, gold_ids = [], []
    if ev.is_dir():
        for p in ev.glob("*.json"):
            gold_texts.append(p.read_text(encoding="utf-8"))
        mp = ev / "gold_mapping.json"
        if mp.is_file():
            gold_ids = list(json.loads(mp.read_text(encoding="utf-8")).get("candidate_reverse", {}).values())
    violations = verify_no_leakage(blind, gold_ids, materials, gold_texts=gold_texts)
    violations += [f"prompts: {v}" for v in verify_no_leakage(args.prompts_dir, gold_ids, materials, gold_texts=gold_texts)]

    # runtime guard self-test
    reader = BundleReader(blind)
    for probe in GUARD_PROBES:
        try:
            reader.resolve(probe)
            violations.append(f"runtime guard allowed evaluator-only path {probe!r}")
        except (AccessDenied, FileNotFoundError):
            pass
    for name in ("candidates.csv", "benchmark_config.json", "task.json"):
        try:
            reader.resolve(name)
        except Exception as exc:  # pragma: no cover
            violations.append(f"runtime guard refused an admissible file {name}: {exc}")

    if violations:
        print("LEAKAGE CHECK: FAIL\n" + "\n".join(violations[:50]))
        return 1
    print(json.dumps({"leakage_check": "PASS", "blind_dir": str(blind), "files_scanned": sorted(p.name for p in blind.rglob("*") if p.is_file()),
                      "guard_probes_refused": len(GUARD_PROBES)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
