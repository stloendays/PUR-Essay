#!/usr/bin/env python3
"""Machine-readable project state audit. Read-only.

Reports git state, frozen versions, presence/schema of the PUR_SIM_V1 table, hashes of frozen
configs/results, and whether the blind bundle and gold exist. Writes results/project_state_audit.json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from pur_agent.data_access import sha256_file
from pur_science.canonical import resolve_columns

ROOT = _bootstrap.ROOT
FROZEN = ["configs/oracle_v2.json", "results/oracle_v2/oracle_best.json", "data/oracle_top30_compact.csv", "configs/pur_bridge_v1.json",
          "legacy/v07_frozen_summary.json", "results/rheology_v1/rheology_science_summary.json", "configs/frontier_v1.json", "configs/recover_v1.json",
          "data/pur_sim_v1/design_space_928.csv"]
REQUIRED_RESPONSE_COLS = ("simulated_eta_80c_pa_s", "simulated_eta_120c_pa_s", "simulated_ratio_80c_120c", "simulated_domain_ratio",
                          "simulated_log10_interval_radius", "simulated_chemistry_in_domain_flag")


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception as exc:  # pragma: no cover
        return f"unavailable: {exc}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results" / "project_state_audit.json"))
    args = ap.parse_args()
    full = ROOT / "data" / "pur_sim_v1" / "candidates_full.csv"
    table_state: dict = {"path": str(full), "present": full.is_file()}
    if full.is_file():
        import pandas as pd
        df = pd.read_csv(full)
        cfg = json.loads((ROOT / "configs" / "frontier_v1.json").read_text(encoding="utf-8"))
        try:
            resolve_columns(list(df.columns), cfg["columns"])
            schema_ok = True; schema_err = None
        except KeyError as exc:
            schema_ok = False; schema_err = str(exc)
        table_state.update({"rows": int(len(df)), "sha256": sha256_file(full), "schema_ok": schema_ok, "schema_error": schema_err,
                            "missing_response_columns": [c for c in REQUIRED_RESPONSE_COLS if c not in df.columns]})
    report = {
        "git_head": git("rev-parse", "--short", "HEAD"),
        "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty_files": [l for l in git("status", "--porcelain").splitlines() if l.strip()],
        "frozen_file_hashes": {p: (sha256_file(ROOT / p) if (ROOT / p).is_file() else None) for p in FROZEN},
        "pur_sim_v1_table": table_state,
        "frontier_v1_frozen": (ROOT / "results" / "frontier_v1" / "frontier_v1_decision.json").is_file(),
        "blind_bundle_present": (ROOT / "benchmark" / "recover_v1" / "blind" / "candidates.csv").is_file(),
        "gold_present": (ROOT / "benchmark" / "recover_v1" / "evaluator_only" / "gold_decision.json").is_file(),
        "prospective_validation_agent_access": json.loads((ROOT / "data" / "prospective_validation" / "access_policy.json").read_text())["agent_access"],
        "versions": {"PUR-ORACLE V2": "frozen L1 benchmark", "PUR-FRONTIER V1": "active decision-frontier definition",
                     "PUR-RECOVER V1": "active blind Agent benchmark", "PUR-Bridge v1.1 / v0.7": "legacy, frozen"},
        "next_step": None if full.is_file() else "supply data/pur_sim_v1/candidates_full.csv, then run scripts/freeze_frontier_v1.py and scripts/build_blind_bundle.py",
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
