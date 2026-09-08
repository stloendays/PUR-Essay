from pathlib import Path
from pur_bridge import AnchorMechanismModel, ExperimentAgent

ROOT = Path(__file__).resolve().parents[1]
MODEL = AnchorMechanismModel(ROOT / "data" / "historical_anchor_truth.csv")
AGENT = ExperimentAgent(MODEL)


def test_material_gate_invariants():
    assert AGENT.round1(material_gate="INCOMPATIBLE").action.startswith("abstain")
    assert AGENT.round1(material_gate="AUDIT_REQUIRED").action == "audit_material_equivalence"
    assert AGENT.round1(material_gate="ANCHOR_COMPATIBLE").candidate_id == "E6_star"


def test_e6_requires_independent_batches():
    assert AGENT.after_e6_summary(45.0, 43.0, 47.0, n_batches=2).action == "replicate_E6_star"


def test_e6_requires_ci_clearance():
    assert AGENT.after_e6_summary(45.0, 38.0, 52.0, n_batches=3).action == "replicate_E6_star"
    assert AGENT.after_e6_summary(30.0, 28.0, 35.0, n_batches=3).action == "replicate_E6_star"


def test_decisive_e6_advances():
    assert AGENT.after_e6_summary(45.0, 42.0, 48.0, n_batches=3).action == "evaluate_transfer_pool"
    assert AGENT.after_e6_summary(30.0, 28.0, 32.0, n_batches=3).action == "evaluate_transfer_pool"
