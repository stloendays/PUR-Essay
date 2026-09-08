from pathlib import Path
import json
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pur_bridge import AnchorMechanismModel, ExperimentAgent
from pur_bridge.acquisition import binary_gaussian_information_gain

model = AnchorMechanismModel(ROOT / "data" / "historical_anchor_truth.csv")
preds = model.predictions()
rows = []
for name, p in preds.items():
    rows.append({
        "hypothesis": name,
        "eta130_pa_s": p.eta_pa_s,
        "log_eta": p.log_eta,
        "transferred_log_effect": p.transfer_log_effect,
        "transferred_ratio": float(__import__("math").exp(p.transfer_log_effect)),
        "evidence_status": "preregistered_prediction_not_experiment",
    })
pd.DataFrame(rows).to_csv(ROOT / "results" / "e6_hypotheses.csv", index=False)

summary = {
    "evidence_basis": "US5932680A Examples 5-9 frozen as historical anchors; no E1-E5 remeasurement",
    "delta_balanced_log": model.delta_balanced,
    "balanced_ratio": model.eta("E2") / model.eta("E1"),
    "delta_D_rich_log": model.delta_D_rich,
    "D_rich_ratio": model.eta("E4") / model.eta("E3"),
    "H_strong_eta130_pa_s": preds["H_strong"].eta_pa_s,
    "H_weak_eta130_pa_s": preds["H_weak"].eta_pa_s,
    "equal_prior_geometric_boundary_pa_s": model.equal_prior_boundary_pa_s(),
    "hypothesis_separation_factor": preds["H_strong"].eta_pa_s / preds["H_weak"].eta_pa_s,
    "information_gain_nats_by_sigma": {},
}
for s in [0.05, 0.08, 0.10, 0.12, 0.15]:
    summary["information_gain_nats_by_sigma"][str(s)] = binary_gaussian_information_gain(
        preds["H_strong"].log_eta, preds["H_weak"].log_eta, s
    )
(ROOT / "results" / "anchor_model_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

agent = ExperimentAgent(model)
scenarios = {
    state: agent.round1(0.10, material_gate=state).__dict__
    for state in ["AUDIT_REQUIRED", "ANCHOR_COMPATIBLE", "SURROGATE_ONLY", "INCOMPATIBLE"]
}
(ROOT / "results" / "agent_round1_gate_scenarios.json").write_text(json.dumps(scenarios, indent=2), encoding="utf-8")
current = scenarios["AUDIT_REQUIRED"]
(ROOT / "results" / "agent_round1_decision.json").write_text(json.dumps(current, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
print(json.dumps({"current_agent_state": current, "gate_scenarios": scenarios}, indent=2))
