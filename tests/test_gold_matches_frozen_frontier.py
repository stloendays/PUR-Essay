"""The benchmark gold must be byte-for-byte the same decision as the frozen FRONTIER V1 freeze.

This guards against the class of bug found on 2026-09-10, where the benchmark config loader
dropped the `uncertainty` block and the blind bundle silently used a different L2 rule.
"""
import json
from pathlib import Path

import pandas as pd
import pytest

from pur_agent.blind_bundle import build_blind_bundle
from pur_agent.config import load_benchmark_config
from pur_science import canonicalize, frontier_decision
from pur_science.dataio import EXPECTED_CANDIDATE_SHA256, materialize_pur_sim_v1

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "results" / "frontier_v1" / "frontier_v1_decision.json"


@pytest.fixture(scope="module")
def full_table() -> Path:
    return materialize_pur_sim_v1(ROOT / "data" / "pur_sim_v1" / "candidates_full.csv")


def test_benchmark_config_carries_every_science_block():
    cfg = load_benchmark_config(ROOT / "configs" / "recover_v1.json", repo_root=ROOT)
    sci = json.loads((ROOT / "configs" / "frontier_v1.json").read_text(encoding="utf-8"))
    for key in sci:
        assert key in cfg, f"science key {key!r} missing from merged benchmark config"
        assert cfg[key] == sci[key]
    assert cfg["uncertainty"]["log10_radius_multiplier"]["ratio"] == 2.0


def test_benchmark_decision_equals_frozen_frontier(full_table):
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    assert frozen["gold_status"] == "GOLD"
    cfg = load_benchmark_config(ROOT / "configs" / "recover_v1.json", repo_root=ROOT)
    d = frontier_decision(canonicalize(pd.read_csv(full_table), cfg), cfg)
    for key in ("property_winner", "constrained_winner", "robust_winner", "n_feasible_nominal", "n_feasible_robust"):
        assert d[key] == frozen[key], key
    assert d["active_constraint"]["name"] == frozen["active_constraint"]["name"]
    assert d["backward_design"]["continuous_threshold"] == pytest.approx(frozen["backward_design"]["continuous_threshold"], abs=1e-12)
    assert d["backward_design"]["nearest_reachable_grid_value"] == frozen["backward_design"]["nearest_reachable_grid_value"]
    for key in ("nco_direction", "composition_axis", "composition_direction"):
        assert d["local_trends"][key] == frozen["local_trends"][key]
    for order in ("property_order", "nominal_order", "robust_order"):
        assert d["rankings"][order] == frozen["rankings"][order]


def test_built_gold_equals_frozen_frontier(tmp_path, full_table):
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    cfg = load_benchmark_config(ROOT / "configs" / "recover_v1.json", repo_root=ROOT)
    build_blind_bundle(full_table, cfg, tmp_path / "blind", tmp_path / "ev", seed=int(cfg["anonymization"]["seed"]))
    gold = json.loads((tmp_path / "ev" / "gold_decision.json").read_text(encoding="utf-8"))
    assert gold["source_table_sha256"] == EXPECTED_CANDIDATE_SHA256
    assert (gold["property_winner"], gold["constrained_winner"], gold["robust_winner"]) == ("WO_INV_0419", "WO_INV_0579", "WO_INV_0420")
    assert gold["n_feasible_robust"] == 117 and frozen["n_feasible_robust"] == 117
    assert gold["rankings"]["robust_order"] == frozen["rankings"]["robust_order"]
