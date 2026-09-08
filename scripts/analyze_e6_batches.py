#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_bridge import AnchorMechanismModel, ExperimentAgent
from pur_bridge.experiment import load_e6_measurements, batch_means, summarize_primary_endpoint, andrade_by_batch, endpoint_to_dict


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="E6* measurement CSV following data/e6_measurement_template.csv")
    ap.add_argument("--outdir", default=str(ROOT / "results"))
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    df = load_e6_measurements(args.csv)
    model = AnchorMechanismModel(ROOT / "data" / "historical_anchor_truth.csv")
    endpoint = summarize_primary_endpoint(df, model)
    agent = ExperimentAgent(model)
    decision = agent.after_e6_summary(
        endpoint.geometric_mean_pa_s,
        endpoint.ci95_low_pa_s,
        endpoint.ci95_high_pa_s,
        endpoint.n_batches,
    )

    bm = batch_means(df)
    bm.to_csv(outdir / "e6_batch_means.csv", index=False)
    andrade = andrade_by_batch(df)
    andrade.to_csv(outdir / "e6_andrade_by_batch.csv", index=False)

    sigma_grid = [0.05, 0.08, 0.10, 0.12, 0.15]
    bf = {str(s): model.log_bayes_factor_strong_vs_weak(endpoint.geometric_mean_pa_s, s) for s in sigma_grid}
    report = {
        "primary_endpoint": endpoint_to_dict(endpoint),
        "log_bayes_factor_strong_vs_weak_by_sigma_log": bf,
        "agent_decision": decision.__dict__,
        "technical_cv_flag_count_gt_3pct": int((bm["technical_cv_pct"].fillna(0) > 3.0).sum()),
        "claim_note": "Historical patent values are frozen anchors; E6* is the only prospective wet-lab endpoint in this analysis.",
    }
    (outdir / "e6_analysis.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
