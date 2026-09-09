#!/usr/bin/env python3
"""Freeze PUR-FRONTIER V1 from the complete PUR_SIM_V1 table.

Outputs (results/frontier_v1/):
  frontier_table.csv        every candidate with scores, checks and ranks
  frontier_v1_decision.json named decision chain (L0/L1/L2, active constraint, backward, reachability, trends)
  expectation_check.json    agreement/disagreement with the values documented before the freeze
  manifest.json             input hashes, config hash, status

The script never edits input data. If the table is incomplete it refuses unless --allow-partial
is given, and then every output is stamped NOT_GOLD_PARTIAL_INPUT.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
import pandas as pd

from pur_agent.data_access import sha256_file
from pur_agent.logging_utils import sha256_json, utc_now
from pur_science import canonicalize, compute_frontier, frontier_decision
from pur_science.canonical import BLEND, CID, MDI_PARTS, NCO

ROOT = _bootstrap.ROOT


def check_against_design_space(df: pd.DataFrame, cfg: dict, design_csv: Path) -> dict:
    ds = pd.read_csv(design_csv)
    idc = cfg["columns"]["candidate_id"]
    m = ds.merge(df[[idc, cfg["columns"]["blend"], cfg["columns"]["nco_oh"], cfg["columns"]["mdi_parts"]]], left_on="source_candidate_id", right_on=idc, suffixes=("_design", ""))
    return {
        "design_rows": int(len(ds)),
        "table_rows": int(len(df)),
        "matched_ids": int(len(m)),
        "blend_mismatch": int((m["blend_design"] != m[cfg["columns"]["blend"]]).sum()) if len(m) else None,
        "nco_max_abs_diff": float((m["nco_oh_design"] - m[cfg["columns"]["nco_oh"]]).abs().max()) if len(m) else None,
        "mdi_parts_max_abs_diff": float((m["mdi_parts_design"] - m[cfg["columns"]["mdi_parts"]]).abs().max()) if len(m) else None,
    }


def expectation_check(decision: dict, expected: dict | None) -> dict:
    if not expected:
        return {"status": "no_expectation_recorded"}
    bw = decision["backward_design"]
    items = {
        "property_winner": (expected.get("property_winner"), decision["property_winner"]),
        "constrained_winner": (expected.get("constrained_winner"), decision["constrained_winner"]),
        "robust_winner": (expected.get("robust_winner"), decision["robust_winner"]),
        "active_constraint": (expected.get("active_constraint"), decision["active_constraint"]["name"]),
        "backward_continuous_threshold": (expected.get("backward_continuous_threshold"), bw["continuous_threshold"]),
        "nearest_reachable_grid_value": (expected.get("nearest_reachable_grid_value"), bw["nearest_reachable_grid_value"]),
    }
    out = {}
    all_ok = True
    for k, (exp, got) in items.items():
        if exp is None:
            ok = None
        elif isinstance(exp, (int, float)) and isinstance(got, (int, float)):
            ok = abs(float(exp) - float(got)) <= 5e-3
        else:
            ok = str(exp) == str(got)
        all_ok &= (ok is not False)
        out[k] = {"expected_from_docs": exp, "computed": got, "agrees": ok}
    out["all_agree"] = bool(all_ok)
    out["note"] = "Disagreements are reported, never patched. A disagreement means the documented value came from a different version/config/score definition."
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidates", default=str(ROOT / "data" / "pur_sim_v1" / "candidates_full.csv"))
    ap.add_argument("--config", default=str(ROOT / "configs" / "frontier_v1.json"))
    ap.add_argument("--design-space", default=str(ROOT / "data" / "pur_sim_v1" / "design_space_928.csv"))
    ap.add_argument("--out", default=str(ROOT / "results" / "frontier_v1"))
    ap.add_argument("--allow-partial", action="store_true", help="accept a table with fewer rows than design_space.n_candidates (outputs marked NOT_GOLD)")
    args = ap.parse_args()

    cand = Path(args.candidates)
    if not cand.is_file():
        print(f"ERROR: candidate table not found: {cand}\nSupply the complete PUR_SIM_V1 table (see data/pur_sim_v1/README.md).", file=sys.stderr)
        return 2
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    df = pd.read_csv(cand)
    expected_n = int(cfg.get("design_space", {}).get("n_candidates", len(df)))
    status = "GOLD"
    if len(df) != expected_n:
        if not args.allow_partial:
            print(f"ERROR: table has {len(df)} rows, frozen design space has {expected_n}. Refusing to freeze a partial frontier (use --allow-partial for a diagnostic, non-gold run).", file=sys.stderr)
            return 3
        status = "NOT_GOLD_PARTIAL_INPUT"

    table = canonicalize(df, cfg)
    frontier = compute_frontier(table, cfg)
    decision = frontier_decision(table, cfg)
    decision["gold_status"] = status

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    frontier.to_csv(out / "frontier_table.csv", index=False)
    (out / "frontier_v1_decision.json").write_text(json.dumps(decision, indent=2, default=str), encoding="utf-8")
    exp = expectation_check(decision, cfg.get("expected_from_docs"))
    (out / "expectation_check.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
    manifest = {
        "workflow_id": cfg.get("workflow_id"),
        "gold_status": status,
        "frozen_utc": utc_now(),
        "candidate_table": str(cand),
        "candidate_table_sha256": sha256_file(cand),
        "config_sha256": sha256_json(cfg),
        "n_candidates": int(len(df)),
        "design_space_check": check_against_design_space(df, cfg, Path(args.design_space)) if Path(args.design_space).is_file() else None,
        "decision_sha256": sha256_json(decision),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "property_winner": decision["property_winner"], "constrained_winner": decision["constrained_winner"],
                      "robust_winner": decision["robust_winner"], "active_constraint": decision["active_constraint"]["name"],
                      "backward": {k: decision["backward_design"][k] for k in ("continuous_threshold", "nearest_reachable_grid_value", "reachable")},
                      "local_trends": {k: decision["local_trends"][k] for k in ("nco_direction", "composition_axis", "composition_direction")},
                      "expectation_all_agree": exp.get("all_agree"), "out": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
