from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from pur_bridge import AnchorMechanismModel

m=AnchorMechanismModel(ROOT/'data'/'historical_anchor_truth.csv')
p=m.predictions()
assert abs(p['H_strong'].eta_pa_s - 44.65384615384615) < 1e-9
assert abs(p['H_weak'].eta_pa_s - 29.454545454545453) < 1e-9
assert m.classify(45)=='strong_consistent'
assert m.classify(30)=='weak_consistent'
assert m.classify(36)=='indeterminate'
assert abs(m.context_transfer_theta(p['H_strong'].eta_pa_s)-1)<1e-9
assert abs(m.context_transfer_theta(p['H_weak'].eta_pa_s))<1e-9
print('ok')
