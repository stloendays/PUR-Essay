"""pur_science.depth must reproduce the frozen FRONTIER-DEPTH V1 numbers from the frozen frontier table."""
import json
from pathlib import Path

import pandas as pd
import pytest

from pur_science.depth import (
    consistency_report, constraint_counterfactual, mdi_floor_phase, objective_structure_audit, pareto_alternatives,
    score_crossover, uncertainty_counterfactual, weight_stability,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def frontier():
    return pd.read_csv(ROOT / "results" / "frontier_v1" / "frontier_table.csv")


@pytest.fixture(scope="module")
def cfg():
    return json.loads((ROOT / "configs" / "frontier_v1.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def depth_summary():
    return json.loads((ROOT / "results" / "frontier_depth_v1" / "summary.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def decision():
    return json.loads((ROOT / "results" / "frontier_v1" / "frontier_v1_decision.json").read_text(encoding="utf-8"))


def test_mdi_floor_phase_reproduces_frozen(frontier, cfg):
    nom = pd.DataFrame(mdi_floor_phase(frontier, cfg, layer="nominal"))
    rob = pd.DataFrame(mdi_floor_phase(frontier, cfg, layer="robust"))
    frozen_nom = pd.read_csv(ROOT / "results" / "frontier_depth_v1" / "mdi_floor_phase_nominal.csv")
    frozen_rob = pd.read_csv(ROOT / "results" / "frontier_depth_v1" / "mdi_floor_phase_robust.csv")
    assert nom["winner"].tolist() == frozen_nom["winner"].tolist()
    assert rob["winner"].tolist() == frozen_rob["winner"].tolist()
    assert nom["floor_hi_inclusive"].to_numpy() == pytest.approx(frozen_nom["floor_hi_inclusive"].to_numpy(), abs=1e-9)
    cf = constraint_counterfactual(frontier, cfg, layer="robust")
    assert cf["current_winner"] == "WO_INV_0420"
    assert cf["winner_stable_for_floor_in"][0] == pytest.approx(0.345868, abs=1e-5)
    assert cf["winner_stable_for_floor_in"][1] == pytest.approx(0.353577, abs=1e-5)


def test_uncertainty_crossover_reproduces_frozen(frontier, cfg, depth_summary):
    x = score_crossover(frontier, cfg, "WO_INV_0579", "WO_INV_0420")
    assert x["crossover_scales"] == pytest.approx(depth_summary["uncertainty_scale"]["L1_L2_score_crossover_roots"], abs=1e-9)
    assert x["leader_at_s0"] == "WO_INV_0579" and x["leader_at_s1"] == "WO_INV_0420"
    uc = uncertainty_counterfactual(frontier, cfg, "WO_INV_0579", "WO_INV_0420")
    assert uc["mechanism"] == "worst_case_objective"
    assert uc["robust_winner_stable_for_scale_in"][0] <= 1.0 <= uc["robust_winner_stable_for_scale_in"][1]
    phase = pd.read_csv(ROOT / "results" / "frontier_depth_v1" / "uncertainty_scale_phase.csv")
    # the frozen CSV keeps one row per empty-admissible-set step; depth.py merges that tail into one segment
    assert [p["winner"] for p in uc["phase_map"] if p["winner"]] == [w for w in phase["winner"] if not pd.isna(w)]


def test_weight_stability_reproduces_frozen(frontier, cfg, depth_summary):
    ws = depth_summary["weight_stability"]
    nom = weight_stability(frontier, cfg, layer="nominal", samples=ws["samples"], seed=ws["seed"])
    rob = weight_stability(frontier, cfg, layer="robust", samples=ws["samples"], seed=ws["seed"])
    assert nom["winner_fractions"][0] == {"winner": ws["nominal_top"][0]["winner"], "fraction": pytest.approx(ws["nominal_top"][0]["fraction"])}
    assert rob["winner_fractions"][0] == {"winner": ws["robust_top"][0]["winner"], "fraction": pytest.approx(ws["robust_top"][0]["fraction"])}


def test_pareto_and_objective_structure(frontier, cfg, depth_summary):
    p = pareto_alternatives(frontier, cfg)
    assert p["n_non_dominated"] == depth_summary["pareto5"]["n_non_dominated"]
    frozen = pd.read_csv(ROOT / "results" / "frontier_depth_v1" / "pareto5_frontier.csv")
    assert set(p["pareto_ids"]) == set(frozen[frozen["pareto5"]]["cid"])
    assert "WO_INV_0420" in p["pareto_ids"]
    o = objective_structure_audit(cfg)
    assert o["double_counting"] is True and o["principal_weight_ratio"] == pytest.approx(3.0)
    assert o["center_inconsistency_delta_log10"] == pytest.approx(depth_summary["objective_geometry"]["center_inconsistency_delta_log10"])


def test_frozen_chain_is_consistent(frontier, cfg, decision):
    rep = consistency_report(frontier, cfg, decision)
    assert rep["n_contradictions"] == 0, rep["contradictions"]
    assert rep["checks"]["robust_winner_equals_reachable_candidate"]["observation"] is True
