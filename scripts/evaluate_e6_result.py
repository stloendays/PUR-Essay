from pathlib import Path
import json, sys, argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from pur_bridge import AnchorMechanismModel, ExperimentAgent

ap=argparse.ArgumentParser()
ap.add_argument('eta130_pa_s',type=float)
args=ap.parse_args()
model=AnchorMechanismModel(ROOT/'data'/'historical_anchor_truth.csv')
agent=ExperimentAgent(model)
out={
  'eta130_pa_s':args.eta130_pa_s,
  'classification':model.classify(args.eta130_pa_s),
  'context_transfer_theta':model.context_transfer_theta(args.eta130_pa_s),
  'log_bayes_factor_sensitivity':{str(s):model.log_bayes_factor_strong_vs_weak(args.eta130_pa_s,s) for s in [0.05,0.08,0.10,0.12,0.15]},
  'agent_next_decision':agent.after_e6(args.eta130_pa_s).__dict__
}
print(json.dumps(out,indent=2))
